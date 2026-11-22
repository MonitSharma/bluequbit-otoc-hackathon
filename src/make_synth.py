"""Write a synthetic family to data/<name>/MQW_<name>_q.qasm (u3+cz) and exact values to data/exact_<name>.csv.
python src/make_synth.py NAME grid ROWS COLS CYCLES BFLY [SEED]
python src/make_synth.py NAME chain N LAYERS BFLYS WEAK [SEED]
"""
import sys, os, csv, time
import numpy as np
from qiskit import transpile, qasm2
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2
sys.path.insert(0, os.path.dirname(__file__))
from synth import haar_chain, fsim_grid, echo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, kind = sys.argv[1], sys.argv[2]
if kind == "grid":
    R, C, cyc, b = map(int, sys.argv[3:7]); seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    U = fsim_grid(R, C, cyc, seed=seed); bfl = [b]
else:
    n_, L = int(sys.argv[3]), int(sys.argv[4])
    bfl = [int(x) for x in sys.argv[5].split(",")]
    weak = [int(x) for x in sys.argv[6].split(",") if x]
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    U = haar_chain(n_, L, seed=seed, weak=weak)
U = transpile(U, basis_gates=["u3", "cz"], optimization_level=1)
n = U.num_qubits
os.makedirs(f"{ROOT}/data/{name}", exist_ok=True)
est = EstimatorV2(options={"backend_options": {"method": "statevector", "max_parallel_threads": 12}})
rows = []
for q in range(n):
    qc = echo(U, bfl, q)
    qasm2.dump(qc, f"{ROOT}/data/{name}/MQW_{name}_{q}.qasm")
    t = time.time()
    v = float(est.run([(qc, SparsePauliOp("I" * (n - 1 - q) + "Z" + "I" * q))]).result()[0].data.evs)
    rows.append((f"MQW_{name}_{q}", v)); print(q, round(v, 4), f"{time.time()-t:.0f}s", flush=True)
with open(f"{ROOT}/data/exact_{name}.csv", "w", newline="") as fh:
    csv.writer(fh).writerows(rows)
