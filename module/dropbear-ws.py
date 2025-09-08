#!/usr/bin/env python3
import socket, threading, selectors, sys, time, getopt, ssl, base64, hashlib

# Default config
LISTENING_ADDR = "0.0.0.0"
LISTENING_PORT = 7000
DEFAULT_HOST = "127.0.0.1:109"   # Dropbear or other backend
BUFLEN = 4096 * 4
TIMEOUT = 300
PASS = ""   # optional password
USE_TLS = False
CERT_FILE = "/etc/ssl/certs/server.crt"
KEY_FILE  = "/etc/ssl/private/server.key"

# ---------------- WebSocket Handshake ----------------
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def make_handshake(key: str) -> bytes:
    accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n"
        "Server: nginx\r\n"
        "Keep-Alive: timeout=60\r\n"
        "\r\n"
    )
    return response.encode()

# ---------------- Server Class ----------------
class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.threads = []
        self.running = False
        self.sel = selectors.DefaultSelector()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if USE_TLS:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
            sock = context.wrap_socket(sock, server_side=True)

        sock.bind((self.host, self.port))
        sock.listen(100)
        sock.settimeout(2)
        self.running = True
        print(f"[+] Listening on {self.host}:{self.port} (TLS={USE_TLS})")

        while self.running:
            try:
                client, addr = sock.accept()
                client.setblocking(True)
                conn = ConnectionHandler(client, self, addr)
                conn.start()
                self.threads.append(conn)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[!] Accept error: {e}")

    def stop(self):
        self.running = False
        for c in self.threads:
            c.close()

# ---------------- Connection Handler ----------------
class ConnectionHandler(threading.Thread):
    def __init__(self, client, server, addr):
        super().__init__(daemon=True)
        self.client = client
        self.server = server
        self.addr = addr
        self.clientClosed = False
        self.targetClosed = True

    def close(self):
        for s in [self.client, getattr(self, "target", None)]:
            if s:
                try: s.close()
                except: pass

    def get_header(self, data: bytes, header: str) -> str:
        marker = (header + ": ").encode()
        idx = data.find(marker)
        if idx == -1:
            return ""
        start = idx + len(marker)
        end = data.find(b"\r\n", start)
        return data[start:end].decode() if end != -1 else ""

    def run(self):
        try:
            data = self.client.recv(BUFLEN)

            # Basic header validation
            if b"Upgrade: websocket" not in data:
                self.client.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                return

            ws_key = self.get_header(data, "Sec-WebSocket-Key")
            passwd = self.get_header(data, "X-Pass")
            hostPort = self.get_header(data, "X-Real-Host") or DEFAULT_HOST

            # Password check
            if PASS and passwd != PASS:
                self.client.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                return

            # Connect to backend
            self.target = self.connect_target(hostPort)
            self.client.sendall(make_handshake(ws_key))
            print(f"[+] WS CONNECT {self.addr} -> {hostPort}")

            self.forward_loop()

        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            self.close()

    def connect_target(self, hostPort: str):
        if ":" in hostPort:
            host, port = hostPort.split(":")
            port = int(port)
        else:
            host, port = hostPort, 443
        sock = socket.create_connection((host, port))
        self.targetClosed = False
        return sock

    def forward_loop(self):
        sel = selectors.DefaultSelector()
        sel.register(self.client, selectors.EVENT_READ, self.target)
        sel.register(self.target, selectors.EVENT_READ, self.client)

        idle = 0
        while idle < TIMEOUT:
            events = sel.select(timeout=3)
            if not events:
                idle += 1
                continue
            for key, _ in events:
                try:
                    data = key.fileobj.recv(BUFLEN)
                    if not data:
                        return
                    key.data.sendall(data)
                    idle = 0
                except:
                    return

# ---------------- CLI ----------------
def usage():
    print("Usage: ws-dropbear.py -p <port> [-b <bindAddr>] [--tls]")

def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT, USE_TLS
    try:
        opts, args = getopt.getopt(argv, "hb:p:", ["bind=", "port=", "tls"])
    except getopt.GetoptError:
        usage(); sys.exit(2)
    for opt, arg in opts:
        if opt in ("-b", "--bind"): LISTENING_ADDR = arg
        elif opt in ("-p", "--port"): LISTENING_PORT = int(arg)
        elif opt == "--tls": USE_TLS = True

def main():
    parse_args(sys.argv[1:])
    srv = Server(LISTENING_ADDR, LISTENING_PORT)
    srv.start()
    try:
        while True: time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping...")
        srv.stop()

if __name__ == "__main__":
    main()
