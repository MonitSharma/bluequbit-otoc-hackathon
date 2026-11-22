"""Exact <Z_q> for data/<NAME>/*.qasm via Aer statevector -> data/exact_<NAME>.csv"""
import sys, os, csv
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1]; d = f"{ROOT}/data/{name}"
nq = len([f for f in os.listdir(d) if f.endswith(".qasm")])
est = EstimatorV2(options={"backend_options": {"method": "statevector", "max_parallel_threads": 12}})
rows = []
for q in range(nq):
    qc = QuantumCircuit.from_qasm_file(f"{d}/MQW_{name}_{q}.qasm"); n = qc.num_qubits
    v = float(est.run([(qc, SparsePauliOp("I" * (n - 1 - q) + "Z" + "I" * q))]).result()[0].data.evs)
    rows.append((f"MQW_{name}_{q}", v)); print(q, round(v, 4), flush=True)
csv.writer(open(f"{ROOT}/data/exact_{name}.csv", "w", newline="")).writerows(rows)
