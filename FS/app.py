from flask import Flask, request, jsonify, Response
import socket

app = Flask(__name__)

def send_udp(as_ip, as_port, name, ip_value, ttl=10):
    msg = f"TYPE=A\nNAME={name} VALUE={ip_value} TTL={ttl}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (as_ip, 53533))
    sock.settimeout(2.0)
    data, _ = sock.recvfrom(1024)
    return data.decode().strip()

def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

@app.put("/register")
def register():
    body = request.get_json(silent=True)
    if not body: return Response("Bad Request", status=400)
    for k in ("hostname","ip","as_ip","as_port"):
        if k not in body: return Response("Bad Request", status=400)

    try:
        resp = send_udp(body["as_ip"], body["as_port"], body["hostname"], body["ip"])
        if resp.startswith("SUCCESS"):
            return Response(status=201)
        return Response("Registration Failed", status=500)
    except Exception as e:
        return Response(f"Registration Error: {e}", status=500)

@app.get("/fibonacci")
def fibonacci():
    num = request.args.get("number")
    if num is None or not num.isdigit():
        return Response("Bad Request", status=400)
    return jsonify({"fibonacci": fib(int(num))}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
