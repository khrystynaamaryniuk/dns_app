import socket, os

HOST = "0.0.0.0"
PORT = 53533
DB_PATH = "/app/records.txt"

os.makedirs("/app", exist_ok=True)
if not os.path.exists(DB_PATH):
    open(DB_PATH, "w").close()

def parse(msg: str) -> dict:
    lines = [l.strip() for l in msg.splitlines() if l.strip()]
    d = {}
    for line in lines:
        tokens = line.split()
        for t in tokens:
            if "=" in t:
                k,v = t.split("=",1)
                d[k.upper()] = v
            elif t.upper().startswith("TYPE"):
                d["TYPE"] = t.split("=")[-1]
    return d

def load_records():
    recs = {}
    with open(DB_PATH, "r") as f:
        for line in f:
            if not line.strip(): continue
            parts = dict(p.split("=",1) for p in line.split())
            recs[parts["NAME"]] = parts
    return recs

def save_record(name, value, ttl):
    recs = load_records()
    recs[name] = {"NAME": name, "VALUE": value, "TTL": str(ttl)}
    with open(DB_PATH, "w") as f:
        for r in recs.values():
            f.write(f'NAME={r["NAME"]} VALUE={r["VALUE"]} TTL={r["TTL"]}\n')

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[AS] listening on {HOST}:{PORT}")
    while True:
        data, addr = sock.recvfrom(2048)
        msg = data.decode("utf-8", errors="ignore")
        d = parse(msg)

        # Registration
        if d.get("TYPE","").upper() == "A" and "NAME" in d and "VALUE" in d:
            ttl = int(d.get("TTL","10"))
            save_record(d["NAME"], d["VALUE"], ttl)
            sock.sendto(b"SUCCESS\n", addr)
            continue

        # Query
        if d.get("TYPE","").upper() == "A" and "NAME" in d and "VALUE" not in d:
            recs = load_records()
            r = recs.get(d["NAME"])
            if r:
                resp = f'TYPE=A\nNAME={r["NAME"]} VALUE={r["VALUE"]} TTL={r["TTL"]}\n'
                sock.sendto(resp.encode(), addr)
            else:
                sock.sendto(b"NOTFOUND\n", addr)
            continue

        sock.sendto(b"BADREQUEST\n", addr)

if __name__ == "__main__":
    serve()
