"""Sequential GPU pauli-path runner; per qubit, tightest threshold that passes validation.
python src/adaptive.py C1:t1,t2,... C2:t1,...   -> results/<C>__gpu_<t1..>.jsonl
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from runner import init, IDS, ROOT
import bluequbit
from qiskit import QuantumCircuit

bq = init()
for spec in sys.argv[1:]:
    parts = spec.split(":"); C, ts = parts[0], parts[1]; thrs = [float(t) for t in ts.split(",")]
    extra = {}
    if len(parts) > 2 and parts[2]:
        for kv in parts[2].split(","):
            k, v = kv.split("="); extra[{"tl": "pauli_path_circuit_transpilation_level", "w": "pauli_path_weight_cutoff"}[k]] = int(v)
    only = [int(x) for x in parts[3].split(",")] if len(parts) > 3 else None
    out = f"{ROOT}/results/{C}__gpu_{ts.replace(',', '_')}" + "".join(f"_{k}{v}" for k, v in (kv.split("=") for kv in (parts[2].split(",") if len(parts) > 2 and parts[2] else []))) + ".jsonl"
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["q"] for l in open(out) if json.loads(l).get("value") is not None}
    local = C not in IDS
    if local:
        qdir = f"{ROOT}/data/{C}"; nq = len([f for f in os.listdir(qdir) if f.endswith(".qasm")])
        n = QuantumCircuit.from_qasm_file(f"{qdir}/MQW_{C}_0.qasm").num_qubits
    else:
        nq = IDS[C]; n = bq.get_circuit_info(f"MQW_{C}_0").num_qubits
    print(C, thrs, out, flush=True)
    for q in range(nq):
        if q in done or (only and q not in only): continue
        z = "I" * (n - 1 - q) + "Z" + "I" * q
        circ = QuantumCircuit.from_qasm_file(f"{qdir}/MQW_{C}_{q}.qasm") if local else f"MQW_{C}_{q}"
        i = 0
        if os.environ.get("START_FROM"):
            prev = {json.loads(l)["q"]: json.loads(l)["thr"] for l in open(os.environ["START_FROM"])}
            if q in prev and prev[q] in thrs: i = thrs.index(prev[q])
        while i < len(thrs):
            t0 = time.time()
            try:
                j = bq.run(circ, device="pauli-path.gpu", pauli_sum=[(z, 1.0)],
                           options={"pauli_path_truncation_threshold": thrs[i], **extra}, job_name=f"{C}_{q}_gpu{thrs[i]}")
            except Exception as e:
                m = str(e)
                if "FUNDS" in m:
                    print("OUT OF FUNDS, stopping", flush=True); print("ALL DONE", flush=True); sys.exit(0)
                if "PARALLEL" in m or "LIMIT" in m or "COOLDOWN" in m:
                    time.sleep(10); continue
                print(f"q={q} t={thrs[i]} fail: {m[:120]}", flush=True); i += 1; continue
            rec = {"q": q, "value": j.expectation_value if j.run_status == "COMPLETED" else None,
                   "thr": thrs[i], "status": j.run_status, "wall": round(time.time() - t0, 1),
                   "cost": getattr(j, "cost", None), "job_id": j.job_id}
            print(json.dumps(rec), flush=True)
            if rec["value"] is not None:
                open(out, "a").write(json.dumps(rec) + "\n"); break
            i += 1
print("ALL DONE", flush=True)
