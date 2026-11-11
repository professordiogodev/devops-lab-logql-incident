#!/usr/bin/env python3
"""PROVIDED. Pushes about 100 minutes of Beanie logs into Loki. The content is the same every run; only the clock moves.

usage: python3 gen_logs.py http://127.0.0.1:3199        (writes .lab/.window.json with the exact start and end)
"""
import json, os, random, sys, time, urllib.request

LOKI = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3199"
rnd = random.Random(20260101)
MIN = 60
N = 100                                   # minutes of logs
end = int(time.time()) - 5 * MIN          # the last log line is five minutes old
start = end - N * MIN
CUSTOMERS = ["Ana", "Bruno", "Chloe", "Dmitri", "Eva", "Farid", "Gita", "Hugo"]
COUNTRIES = ["PT", "PT", "PT", "ES", "ES", "FR", "DE"]
streams = {}


def rid():
    return "req_%08x" % rnd.getrandbits(32)


def tid():
    return "%032x" % rnd.getrandbits(128)


def add(ts, service, obj=None, text=None):
    key = service
    line = json.dumps(obj) if obj is not None else text
    streams.setdefault(key, []).append((int(ts * 1e9) + rnd.randint(0, 999), line))


def log(ts, service, level, msg, **kw):
    o = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)), "level": level, "service": service, "msg": msg}
    o.update(kw)
    add(ts, service, o)


for m in range(N):
    base = start + m * MIN
    incident = 40 <= m < 60                      # payments is in trouble between minute 40 and 60
    menu_cache = 70 <= m < 78                    # a cache miss storm in menu
    per_min = 18
    for i in range(per_min):
        ts = base + i * (MIN / per_min) + rnd.random()
        r, t, cust = rid(), tid(), rnd.choice(CUSTOMERS)
        # access noise: health checks every few seconds
        for svc in ("gateway", "menu", "orders", "payments"):
            if i % 6 == 0:
                log(ts, svc, "info", "request", route="/healthz", status=200, duration_ms=rnd.randint(1, 4), request_id=rid())
        pay_ms = rnd.randint(1500, 4800) if incident else rnd.randint(40, 180)
        failed = incident and rnd.random() < 0.55
        log(ts, "gateway", "info", "request", route="/api/orders", status=504 if failed else 201, duration_ms=pay_ms + rnd.randint(10, 40), request_id=r, trace_id=t)
        log(ts + 0.01, "menu", "warn" if menu_cache and rnd.random() < 0.5 else "info", "cache miss" if menu_cache else "menu served", request_id=r, trace_id=t, duration_ms=rnd.randint(5, 30) if not menu_cache else rnd.randint(200, 600))
        if failed:
            log(ts + 0.05, "payments", "error", "charge timed out", request_id=r, trace_id=t, duration_ms=pay_ms, customer=cust)
            log(ts + 0.06, "orders", "error", "payment failed", order_id="ord_%06x" % rnd.getrandbits(24), customer=cust, request_id=r, trace_id=t, duration_ms=pay_ms + 20)
        else:
            declined = (not incident) and rnd.random() < 0.06
            if declined:
                log(ts + 0.05, "payments", "warn", "card_declined", request_id=r, trace_id=t, duration_ms=pay_ms, customer=cust)
                log(ts + 0.06, "orders", "warn", "order not paid: card_declined", customer=cust, request_id=r, trace_id=t, duration_ms=pay_ms + 20)
            else:
                log(ts + 0.05, "payments", "info", "charge approved", request_id=r, trace_id=t, duration_ms=pay_ms, customer=cust)
                log(ts + 0.06, "orders", "info", "order created", order_id="ord_%06x" % rnd.getrandbits(24), customer=cust, request_id=r, trace_id=t, duration_ms=pay_ms + 20)
                add(ts + 0.08, "notifications", text="sms sent country=%s order=%s" % (rnd.choice(COUNTRIES), "ord_%06x" % rnd.getrandbits(24)))

# push, one stream per service, oldest first
payload = {"streams": []}
for svc, rows in streams.items():
    rows.sort()
    for i in range(0, len(rows), 1000):
        chunk = rows[i:i + 1000]
        body = {"streams": [{"stream": {"app": "beanie", "service": svc}, "values": [[str(ts), line] for ts, line in chunk]}]}
        req = urllib.request.Request(LOKI + "/loki/api/v1/push", json.dumps(body).encode(), {"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=30).read()
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".lab"), exist_ok=True)
json.dump({"start": start, "end": end, "lines": {k: len(v) for k, v in streams.items()}}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".lab", ".window.json"), "w"))
print("pushed %d lines for %s" % (sum(len(v) for v in streams.values()), ", ".join(sorted(streams))))
