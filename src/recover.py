"""Recover results of jobs submitted by a killed runner: python src/recover.py LOG JSONL"""
import sys, json, re, time
sys.path.insert(0, 'src')
from runner import init
log, out = sys.argv[1], sys.argv[2]
done = set()
try:
    for l in open(out):
        r = json.loads(l)
        if r.get("value") is not None: done.add(r["q"])
except FileNotFoundError: pass
subs = {int(q): j for q, j in re.findall(r"submitted q=(\d+) job=(\w+)", open(log).read())}
todo = {q: j for q, j in subs.items() if q not in done}
bq = init()
while todo:
    for q, jid in list(todo.items()):
        j = bq.get(jid)
        if j.run_status in ("RUNNING", "PENDING", "QUEUED"): continue
        val = j.expectation_value if j.run_status == "COMPLETED" else None
        with open(out, "a") as fh:
            fh.write(json.dumps({"q": q, "id": None, "value": val, "status": j.run_status, "job_id": jid, "run_time_ms": j.run_time_ms}) + "\n")
        print(q, j.run_status, val, flush=True); todo.pop(q)
    if todo: time.sleep(20)
print("ALL DONE")
