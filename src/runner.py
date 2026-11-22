"""Resumable BlueQubit runner for MQW OTOC circuits.

Usage: python src/runner.py CIRCUIT DEVICE [--opt key=value ...] [--qubits 0,1,2] [--par N] [--tag NAME]
Results are appended to results/<CIRCUIT>__<TAG>.jsonl (one line per finished ID);
already-finished IDs are skipped on re-run.
"""
import argparse, json, os, sys, time
import bluequbit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = {"S1": 4, "S2": 16, "S3": 25, "G1": 30, "G2": 36, "G3": 36, "G4": 36}


def init():
    tok = open(os.path.join(ROOT, ".bq_token")).read().strip()
    return bluequbit.init(tok)


def parse_val(v):
    for f in (int, float):
        try:
            return f(v)
        except ValueError:
            pass
    return None if v == "None" else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("circuit"); ap.add_argument("device")
    ap.add_argument("--opt", action="append", default=[])
    ap.add_argument("--qubits", default=None)
    ap.add_argument("--par", type=int, default=5)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    opts = {k: parse_val(v) for k, v in (o.split("=", 1) for o in a.opt)}
    tag = a.tag or (a.device + "".join(f"_{k.split('_')[-1]}{v}" for k, v in opts.items()))
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    out = os.path.join(ROOT, "results", f"{a.circuit}__{tag}.jsonl")
    done = set()
    if os.path.exists(out):
        for l in open(out):
            r = json.loads(l)
            if r.get("value") is not None:
                done.add(r["q"])
    qs = [int(x) for x in a.qubits.split(",")] if a.qubits else list(range(IDS.get(a.circuit, 0)))
    qs = [q for q in qs if q not in done]
    bq = init()
    local = a.circuit not in IDS
    if local:
        from qiskit import QuantumCircuit
        qdir = os.path.join(ROOT, "data", a.circuit)
        nfiles = len([f for f in os.listdir(qdir) if f.endswith(".qasm")])
        if not a.qubits:
            qs = [q for q in range(nfiles) if q not in done]
        n = QuantumCircuit.from_qasm_file(os.path.join(qdir, f"MQW_{a.circuit}_0.qasm")).num_qubits
    else:
        n = bq.get_circuit_info(f"MQW_{a.circuit}_0").num_qubits
    pending = {}  # job_id -> (q, t0)
    print(f"{a.circuit} {a.device} {opts} -> {out}; todo {qs}", flush=True)
    while qs or pending:
        while qs and len(pending) < a.par:
            q = qs.pop(0)
            z = "I" * (n - 1 - q) + "Z" + "I" * q
            try:
                circ = (QuantumCircuit.from_qasm_file(os.path.join(qdir, f"MQW_{a.circuit}_{q}.qasm"))
                        if local else f"MQW_{a.circuit}_{q}")
                j = bq.run(circ, device=a.device, pauli_sum=[(z, 1.0)],
                           options=opts or None, asynchronous=True,
                           job_name=f"{a.circuit}_{q}_{tag}"[:190],
                           **({"force_run": True} if a.force else {}))
                pending[j.job_id] = (q, time.time())
                print(f"submitted q={q} job={j.job_id}", flush=True)
            except Exception as e:
                msg = str(e)
                print(f"submit failed q={q}: {msg[:300]}", flush=True)
                if "PARALLEL" in msg or "COOLDOWN" in msg or "LIMIT" in msg:
                    qs.insert(0, q); time.sleep(30); break
                with open(out, "a") as fh:
                    fh.write(json.dumps({"q": q, "value": None, "status": "SUBMIT_ERROR", "error": msg[:500]}) + "\n")
        time.sleep(10)
        for jid in list(pending):
            try:
                j = bq.get(jid)
            except Exception as e:
                print("get failed", jid, e, flush=True); continue
            if j.run_status in ("COMPLETED",) or j.run_status in bluequbit.job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES or j.run_status == "FAILED":
                q, t0 = pending.pop(jid)
                val = j.expectation_value if j.run_status == "COMPLETED" else None
                rec = {"q": q, "id": f"MQW_{a.circuit}_{q}", "value": val, "status": j.run_status,
                       "job_id": jid, "wall": round(time.time() - t0, 1),
                       "run_time_ms": getattr(j, "run_time_ms", None), "cost": getattr(j, "cost", None),
                       "error": getattr(j, "error_message", None)}
                with open(out, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                print(json.dumps(rec), flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
