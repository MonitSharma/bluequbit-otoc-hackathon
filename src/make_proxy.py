"""Write QASMs (no exact) for 30-qubit look-alikes.
python src/make_proxy.py NAME cliff ROWS COLS LAYERS P_ROT BFLY [SEED]   # random 2q Cliffords on grid + random-angle rz w.p. P_ROT
python src/make_proxy.py NAME grid ROWS COLS CYCLES BFLY [SEED]          # fSim grid
"""
import sys, os
import numpy as np
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.quantum_info import random_clifford
sys.path.insert(0, os.path.dirname(__file__))
from synth import fsim_grid, echo, snake_index
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cliff_grid(R, C, L, p, seed):
    rng = np.random.default_rng(seed); n = R * C
    edges = {k: [] for k in "ABCD"}
    for r in range(R):
        for c in range(C):
            a = snake_index(r, c, C)
            if c + 1 < C: edges["A" if c % 2 == 0 else "B"].append((a, snake_index(r, c + 1, C)))
            if r + 1 < R: edges["C" if r % 2 == 0 else "D"].append((a, snake_index(r + 1, c, C)))
    U = QuantumCircuit(n)
    for l in range(L):
        for (a, b) in edges["ACBD"[l % 4]]:
            U.compose(random_clifford(2, seed=int(rng.integers(1 << 31))).to_circuit(), [a, b], inplace=True)
        for q in range(n):
            if rng.random() < p:
                U.rz(rng.uniform(-np.pi, np.pi), q)
    return U

name, kind = sys.argv[1], sys.argv[2]
if kind == "cliff":
    R, C, L = map(int, sys.argv[3:6]); p = float(sys.argv[6]); b = int(sys.argv[7]); seed = int(sys.argv[8]) if len(sys.argv) > 8 else 1
    U = cliff_grid(R, C, L, p, seed)
else:
    R, C, cyc, b = map(int, sys.argv[3:7]); seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    U = fsim_grid(R, C, cyc, seed=seed)
U = transpile(U, basis_gates=["u3", "cz"], optimization_level=1)
os.makedirs(f"{ROOT}/data/{name}", exist_ok=True)
for q in range(U.num_qubits):
    qasm2.dump(echo(U, [b], q), f"{ROOT}/data/{name}/MQW_{name}_{q}.qasm")
print(name, U.num_qubits, dict(U.count_ops()))
