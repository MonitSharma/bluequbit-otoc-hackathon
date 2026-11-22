import sys, glob, os, time, csv
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = sys.argv[1]; chis = [int(c) for c in sys.argv[2].split(',')]
exact = dict((r[0], float(r[1])) for r in csv.reader(open(f"{root}/data/exact_{s}.csv")))
files = sorted(glob.glob(f"{root}/data/{s}/MQW_{s}_*.qasm"), key=lambda x: int(x.split('_')[-1].split('.')[0]))
for chi in chis:
    est = EstimatorV2(options={"backend_options": {"method": "matrix_product_state", "matrix_product_state_max_bond_dimension": chi, "max_parallel_threads": 12}})
    vals = []; t = time.time()
    for f in files:
        q = int(f.split('_')[-1].split('.')[0]); qc = QuantumCircuit.from_qasm_file(f); n = qc.num_qubits
        vals.append(float(est.run([(qc, SparsePauliOp("I"*(n-1-q)+"Z"+"I"*q))]).result()[0].data.evs))
    ex = np.array([exact[f"MQW_{s}_{i}"] for i in range(len(vals))])
    c = np.corrcoef(vals, ex)[0, 1]
    print(f"{s} chi={chi} corr2={c**2:.4f} t={time.time()-t:.1f}s vals={np.round(vals,3).tolist()}", flush=True)
