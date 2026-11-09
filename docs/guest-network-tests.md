# Guest network procedure (v101 foundation)

This is an owner-run procedure using existing guest tools or browsers. The bundle
does not start the listener, boot guests, change Windows networking or generate a
Delphi probe. Keep raw addresses, names and results under `assets/logs/guest-network/`;
public summaries contain counts, results and repo-relative evidence paths only.

## Prepare and record

Record the bundle version, engine versions, date and each guest's two adapter
settings. Follow the bundle's `docs/guest-lan.md` before adopting the local second
adapter. Both guests must retain their MAC/model/PCI identity and static IP/WINS
without new hardware or re-entry. Start at NT 128 MB and Windows 2000 256 MB. Keep
heavy models/databases stopped and let the owner launch each guest explicitly.

The second local link uses NT 192.168.50.10 and Windows 2000 192.168.50.20, mask
255.255.255.0, no gateway, WINS 192.168.50.10. Its host UDP endpoints are separate
from those guest addresses. Check local ping both ways and the existing HADAMIN
domain behavior, then first-adapter internet. Stop and restore the old configs
if Windows detects new hardware or loses its adapter settings.

Select the peer laptop, its Tailscale IPv4, short/full names and an external plain
HTTP target before testing. The peer must use normal tun-mode Tailscale. HTTP to
another laptop uses the existing user-mode adapter, not a remote second-NIC link.
Do not add ChromeOS port forwarding. Win31 networking is outside this procedure.

## Controlled HTTP marker

First check that TCP 8765 is free. This listener serves only a fixed marker and
returns 404 for other paths. The following is an explicit owner command for the
Linux host; it is not run by setup, dev-test, dev-demo or a launcher:

```bash
python3 - 127.0.0.1 <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

class Marker(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/', '/marker'):
            self.send_error(404)
            return
        body = b'dev-bundle-v101-network-marker\n'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *args):
        pass

class BoundedServer(HTTPServer):
    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address

server = BoundedServer((sys.argv[1], 8765), Marker)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
PY
```

Stop it with Ctrl+C after each binding's checks and confirm the port is free.
For peer tests, the owner starts the same command on the chosen peer, replacing
127.0.0.1 with that peer's specific Tailscale IPv4. A wildcard bind requires an
explicit reachability decision; it is not the default or a persistent service.

## Manual matrix

Record DNS, TCP connect and HTTP observations separately. A marker body and status
200 establish controlled HTTP success. A browser screenshot is browser evidence,
not a result from the deferred HTTPGET executable. Record NOT RUN, unsupported or
FAIL honestly; no template row is pre-filled with success.

| Origin | Target | Path and observation |
|---|---|---|
| Wine | `http://127.0.0.1:8765/marker` | Same-host loopback marker |
| win95 / NT / 2000 first user NIC | `http://10.0.2.2:8765/marker` | Host alias; verify installed DOSBox-X slirp alias rather than assuming it |
| All four | Peer Tailscale IPv4, port 8765 | Controlled peer marker via first/user adapter |
| All four | Peer short and full tailnet names | Record name resolution separately from IPv4 reachability; guest DNS need not inherit MagicDNS |
| All four | Owner-selected plain HTTP internet target | Record status/redirect; an HTTPS redirect is not a plain-HTTP transport failure |
| Period browsers | HTTP versus HTTPS | Marker HTTP is controlled; report actual legacy TLS errors without promising modern TLS support |
| NT second NIC → 2000 / reverse | 192.168.50.20 / .10 | Ping both ways, existing domain relationship, unchanged IP/WINS and first-NIC internet |

Use the advanced-demo `results-template.tsv` as a starting point. Its columns are
date, bundle/engine versions, origin, transport, target category, target, IP/name
form, DNS/connect/HTTP outcomes, elapsed milliseconds, status and evidence path.
Copy it to an explicitly chosen file under assets before recording observations;
the launcher's `results` action only explains this. Guest disks already account
for their growth; no application ISO or database content is added by this scaffold.

## Deferred Delphi HTTPGET and application work

The staged follow-up specifies one Delphi 3 Winsock HTTPGET executable: accept one
plain-HTTP URL, bound DNS/connect/read, send a Host header with HTTP/1.0 and connection
close, display status/body, and return nonzero for failures. Record its version and
checksum and deploy the identical binary to Wine/win95/NT/2000. No source, compiler
invocation, executable, TLS shim or browser installer belongs to v101.

Follow-up F0–F6 in `docs/plans/v101-dcom-demo.md` covers prerequisites, DCOM go/no-go,
the Delphi 7 slice, database swap, back-ports, transports/packaging and cross-laptop
work. NT SP6a and licensed media remain owner-supplied and owner-installed. Remote
F6 must measure the Tailscale 1280 MTU against encapsulated Ethernet frames and
larger transfers; small local pings do not establish remote DCOM or MTU readiness.
