from flask import Flask, request, Response
import socket, requests

app = Flask(__name__)

def dns_query(as_ip, name):
    msg = f"TYPE=A\nNAME={name}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    sock.sendto(msg.encode(), (as_ip, 53533))
    data, _ = sock.recvfrom(1024)
    text = data.decode()
    if text.startswith("TYPE=A"):
        for line in text.splitlines():
            if "VALUE=" in line:
                parts = dict(p.split("=",1) for p in line.split())
                return parts["VALUE"]
    return None

@app.get("/fibonacci")
def proxy_fib():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number  = request.args.get("number")
    as_ip   = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return Response("Bad Request", status=400)

    ip = dns_query(as_ip, hostname)
    if not ip:
        return Response("DNS Not Found", status=404)

    url = f"http://{ip}:{fs_port}/fibonacci"
    try:
        r = requests.get(url, params={"number": number}, timeout=2.5)
    except Exception as e:
        return Response(f"Upstream Error: {e}", status=502)

    return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type","application/json")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
