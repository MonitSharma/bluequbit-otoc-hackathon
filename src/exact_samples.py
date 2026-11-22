import sys, glob, os, time, csv
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
est = EstimatorV2(options={"backend_options": {"method": "statevector", "max_parallel_threads": 12}})
for s in sys.argv[1:]:
    files = glob.glob(f"{root}/data/{s}/MQW_{s}_*.qasm")
    rows = []
    t = time.time()
    for f in sorted(files, key=lambda x: int(x.split('_')[-1].split('.')[0])):
        q = int(f.split('_')[-1].split('.')[0])
        qc = QuantumCircuit.from_qasm_file(f)
        n = qc.num_qubits
        op = SparsePauliOp("I" * (n - 1 - q) + "Z" + "I" * q)
        v = float(est.run([(qc, op)]).result()[0].data.evs)
        rows.append((f"MQW_{s}_{q}", v))
        print(s, q, round(v, 5), f"{time.time()-t:.1f}s", flush=True)
    with open(f"{root}/data/exact_{s}.csv", "w", newline="") as fh:
        csv.writer(fh).writerows(rows)
