# DOTYCAT TUNNEL

## Default Ports

| Service  | Transport |   TLS       |   NTLS      |
|----------|-----------|-------------|-------------|
| VLESS    | gRPC      | 443         | -           |
| VLESS    | WebSocket | 443         | 80          |
| VMESS    | gRPC      | 443         | -           |
| VMESS    | WebSocket | 443         | 80          |
| Trojan   | gRPC      | 443         | -           |
| Trojan   | WebSocket | 443         | 80          |
| SOCKS    | gRPC      | 443         | -           |
| SOCKS    | WebSocket | 443         | 80          |
| SSH      | WebSocket | 443         | 80          |
| SQUID    | -         | 3128, 8080  | -           |
| OpenVPN  | TCP/UDP   | 1194        | 2200        |
| OHP      | TCP       | -           | 8000        |
| ZIVPN    | UDP       | 5667        | 5667        |
| SLDNS    | -         | ALL PORT    | ALL PORT    |


## Custom path or NO path info 
- Allow configuration of custom paths or no path only for the following ports:
  
| Protocol | Type | Port |     Custom Path    |   Multi-Path Support   |
| -------- | ---- | ---- | ------------------ | -----------------------|
| VMESS    | TLS  | 2083 | / or `/<anytext>`  |  ✅ Yes `/<any>/<any>`   |
| VMESS    | NTLS | 2082 | / or `/<anytext>`  |  ✅ Yes `/<any>/<any>`   |
| VLESS    | TLS  | 2087 | / or `/<anytext>`  |  ✅ Yes `/<any>/<any>`   |
| VLESS    | NTLS | 2086 | / or `/<anytext>`  |  ✅ Yes `/<any>/<any>`   |

## Protocols & Multi-Path Support (WebSocket TLS & Non-TLS)

| Protocol       | Example Path       | Port TLS/NTLS  |   Multi-Path Support    |
|----------------|--------------------|----------------|-------------------------|
| **VMess (WS)** |      `/vmess`      |   443/80       | ⚠️ Partial (some port) |
| **VLESS (WS)** |      `/vless`      |   443/80       | ⚠️ Partial (some port) |
| **Trojan (WS)**|      `/trws`       |   443/80       | ⚠️ Partial (some port) |
| **Socks (WS)** |      `/ssws`       |   443/80       | ⚠️ Partial (some port) |
| **SSH (WS)**   |      `/<anypath>`  |   443/80       | ✅ Yes                 |



## Info:  
- ✅ All working: The tunnel works fully without issues.  
- ⚠️ Partial: Some features (e.g., SSH over WebSocket) may not work properly.  

## Ubuntu:
- 20 ✅ All working
- 22 ✅ All working
- 24 ⚠️ Partial (⚠️ SSH not working)

## Debian:
- 10 ✅ All working
- 11 ✅ All working
- 12 ⚠️ Partial (⚠️ SSH not working)

## Installation
 
<pre>
<code>wget -O /root/doty.sh https://raw.githubusercontent.com/dotywrt/doty/main/doty.sh && chmod +x /root/doty.sh && /root/doty.sh</code>
</pre>

### Known Bugs (will fix later, too lazy now 😅)
- Active user count for Xray (VLESS, VMess, Trojan, SOCKS) not displayed correctly
- Automatic deletion of expired accounts not working
 
## Changelog

### 📅 [2025-09-03]
- Initial script release
  
### 📅 [2025-09-04]
- Added support for custom multipath
- Fixed gRPC connection issues
- Updated Nginx configuration (single file)
- Fixed issue where user data could not be saved to JSON file

### 📅 [2025-09-06]  
- Added automatic blocking of torrent sites (BitTorrent traffic, trackers, etc.)  
- Added automatic blocking of adult (pornographic) sites  
- Added ad-blocking functionality (ads, popups, tracking scripts)

### 📅 [2025-09-10]  
- Add new ports for VMESS & VLESS.
- Support custom paths or no path for a specific port.
- Remove NetGuard, Use Default host blocker
- Remove Xray multi-path on ports 443 and 80

### 📅 2025-09-11
- Added OpenVPN support (TCP / UDP / SSL)
- Added Squid Proxy (3128 / 8080)
- Added OHP (Open HTTP Puncher) over TCP

### 📅 2025-09-12
- Added support for ZIVPN panel
- Added support for SlowDNS
