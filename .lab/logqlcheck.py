#!/usr/bin/env python3
import json, os, re, sys, urllib.parse, urllib.request, urllib.error
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
LOKI = "http://127.0.0.1:3199"
passed = failed = 0

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing:  python3 -m pip install pyyaml")

W = json.load(open(".lab/.window.json"))
REF = {
    "l01": ('sum by (service) (count_over_time({app="beanie"} | json | level="error" [2h]))', ["service"]),
    "l02": ('sum by (level) (count_over_time({service="orders"} | json [2h]))', ["level"]),
    "l03": ('quantile_over_time(0.95, {service="payments"} | json | unwrap duration_ms [2h]) by (service)', "single"),
    "l04": ('topk(1, sum by (customer) (count_over_time({service="orders"} | json | level="error" [2h])))', ["customer"]),
    "l05": ('sum(count_over_time({app="beanie"} |= "card_declined" [2h]))', "single"),
    "l06": ('max_over_time({service="payments"} | json | unwrap duration_ms [2h]) by (service)', "single"),
    "l07": ('sum by (country) (count_over_time({service="notifications"} | pattern "sms sent country=<country> order=<_>" [2h]))', ["country"]),
    "l08": ('sum(count_over_time({service="orders"} | json | level="error" [2h])) / sum(count_over_time({service="orders"} [2h]))', "single"),
    "l09": ('count(sum by (trace_id) (count_over_time({app="beanie"} | json | level="error" [2h])))', "single"),
    "l10": ('avg_over_time({service="orders"} | json | unwrap duration_ms [5m]) by (service)', "single"),
}


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""))


def at(t):
    return W["end"] + 1 if t == "end" else W["start"] + int(re.fullmatch(r"start\+(\d+)m", t).group(1)) * 60


def query(expr, t):
    u = LOKI + "/loki/api/v1/query?" + urllib.parse.urlencode({"query": expr, "time": t, "limit": 5000})
    try:
        d = json.load(urllib.request.urlopen(u, timeout=60))
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:200]
    r = d["data"]
    if r["resultType"] == "vector":
        return [(m["metric"], float(m["value"][1])) for m in r["result"]], ""
    if r["resultType"] == "scalar":
        return [({}, float(r["result"][1]))], ""
    return None, "a %s: use an instant query that returns numbers (count_over_time, rate, quantile_over_time ...)" % r["resultType"]


doc = yaml.safe_load(open("queries.yaml"))
qs = {q["id"]: q for q in doc["questions"]}
for qid in sorted(REF):
    q = qs.get(qid)
    expr = str((q or {}).get("expr", "")).strip()
    label = "%s: %s" % (qid, (q["question"][:78] + "...") if q else "?")
    if not expr or expr == "TODO":
        check(label, False, "write the expression in queries.yaml"); continue
    if re.fullmatch(r"[\d.eE+\-*/() ]+", expr) or "{" not in expr:
        check(label, False, "ask the logs: a query needs a stream selector like {service=\"orders\"}"); continue
    ref, mode = REF[qid]
    t = at(q["time"])
    exp, _ = query(ref, t)
    got, err = query(expr, t)
    if got is None:
        check(label, False, "Loki says: %s" % err[:160]); continue
    if mode == "single":
        ok = len(got) == 1 and abs(got[0][1] - exp[0][1]) <= max(1e-6, abs(exp[0][1]) * 0.01)
        hint = "expected one value, about %s; your query returns %d series: %s" % (round(exp[0][1], 4), len(got), [round(v, 4) for _, v in got][:3])
    else:
        e = {tuple(m.get(k) for k in mode): v for m, v in exp}
        g = {tuple(m.get(k) for k in mode): v for m, v in got}
        ok = set(e) == set(g) and len(got) == len(exp) and all(abs(g[k] - e[k]) <= max(1e-6, abs(e[k]) * 0.01) for k in e)
        hint = "expected series with %s: %s; you return %s" % (mode, {k: round(v, 3) for k, v in e.items()}, {k: round(v, 3) for k, v in g.items()})
    check(label, ok, hint)
r = open("REPORT.md").read()
check("REPORT.md is written (no TODO) and gives times, a service and a size", "TODO" not in r and len(r.split()) >= 90 and re.search(r"\d", r) is not None and "payments" in r.lower())
print()
print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
sys.exit(1 if failed else 0)
