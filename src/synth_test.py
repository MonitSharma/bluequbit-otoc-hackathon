"""Exact vs local MPS on a synthetic circuit family.
python src/synth_test.py grid ROWS COLS CYCLES BFLY CHIS
python src/synth_test.py chain N LAYERS BFLYS(comma) WEAK(comma) CHIS
"""
import sys, time, json, os
import numpy as np
from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2
sys.path.insert(0, os.path.dirname(__file__))
from synth import haar_chain, fsim_grid, echo

kind = sys.argv[1]
if kind == "grid":
    R, C, cyc, b = map(int, sys.argv[2:6]); chis = sys.argv[6]
    U = fsim_grid(R, C, cyc, seed=1); bfl = [b]
else:
    n_, L = int(sys.argv[2]), int(sys.argv[3])
    bfl = [int(x) for x in sys.argv[4].split(",")]
    weak = [int(x) for x in sys.argv[5].split(",") if x]
    chis = sys.argv[6]
    U = haar_chain(n_, L, seed=1, weak=weak)
n = U.num_qubits
U = transpile(U, basis_gates=["u3", "cz"], optimization_level=1)
circs = [echo(U, bfl, q) for q in range(n)]
ops = [SparsePauliOp("I" * (n - 1 - q) + "Z" + "I" * q) for q in range(n)]

def run(method, **kw):
    est = EstimatorV2(options={"backend_options": {"method": method, "max_parallel_threads": 12, **kw}})
    return np.array([float(est.run([(c, o)]).result()[0].data.evs) for c, o in zip(circs, ops)])

t = time.time(); ex = run("statevector"); print("exact", np.round(ex, 3).tolist(), f"{time.time()-t:.0f}s", flush=True)
for chi in [int(c) for c in chis.split(",")]:
    t = time.time(); v = run("matrix_product_state", matrix_product_state_max_bond_dimension=chi)
    print(f"chi={chi} corr2={np.corrcoef(v, ex)[0,1]**2:.3f} {time.time()-t:.0f}s", np.round(v, 3).tolist(), flush=True)
