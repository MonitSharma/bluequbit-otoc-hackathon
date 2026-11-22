"""Synthetic look-alikes of the hidden circuits, for testing methods locally.

echo(U, n, bfly, q) builds  U, X_b, U^dag, Z_q, U, X_b, U^dag  (same structure as the MQW QASMs).
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_unitary
from qiskit.circuit.library import UnitaryGate, XXPlusYYGate, CPhaseGate


def haar_chain(n, layers, seed, weak=(), weak_eps=0.15):
    rng = np.random.default_rng(seed)
    U = QuantumCircuit(n)
    for l in range(layers):
        for i in range(l % 2, n - 1, 2):
            if i in weak:
                # near-identity gate: exp(-i eps H) with random Hermitian H
                A = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
                H = (A + A.conj().T) / 2
                w, v = np.linalg.eigh(H)
                g = v @ np.diag(np.exp(-1j * weak_eps * w)) @ v.conj().T
                U.append(UnitaryGate(g), [i, i + 1])
            else:
                U.append(UnitaryGate(random_unitary(4, seed=int(rng.integers(1 << 31)))), [i, i + 1])
    return U


def snake_index(r, c, cols):
    return r * cols + (c if r % 2 == 0 else cols - 1 - c)


def fsim_grid(rows, cols, cycles, seed, theta=np.pi / 2, phi=np.pi / 6, extra=()):
    """Google-style: random sqrt(X/Y/W) per qubit then fSim on one of 4 coupler patterns (ABCD...)."""
    rng = np.random.default_rng(seed)
    n = rows * cols + len(extra)
    edges = {k: [] for k in "ABCD"}
    for r in range(rows):
        for c in range(cols):
            a = snake_index(r, c, cols)
            if c + 1 < cols:
                edges["A" if (c % 2 == 0) else "B"].append((a, snake_index(r, c + 1, cols)))
            if r + 1 < rows:
                edges["C" if (r % 2 == 0) else "D"].append((a, snake_index(r + 1, c, cols)))
    for (a, b, k) in extra:
        edges[k].append((a, b))
    order = "ACBDCADB"
    U = QuantumCircuit(n)
    last = [None] * n
    for t in range(cycles):
        for qb in range(n):
            choices = [g for g in ("sx", "sy", "sw") if g != last[qb]]
            g = choices[rng.integers(len(choices))]
            last[qb] = g
            if g == "sx":
                U.rx(np.pi / 2, qb)
            elif g == "sy":
                U.ry(np.pi / 2, qb)
            else:
                U.rz(-np.pi / 4, qb); U.rx(np.pi / 2, qb); U.rz(np.pi / 4, qb)
        for (a, b) in edges[order[t % len(order)]]:
            # fSim(theta, phi) = iSWAP-like XX+YY rotation then controlled phase
            U.append(XXPlusYYGate(2 * theta, 0), [a, b])
            U.append(CPhaseGate(-phi), [a, b])
    return U


def echo(U, bflys, q):
    n = U.num_qubits
    qc = QuantumCircuit(n)
    qc.compose(U, inplace=True)
    for b in bflys:
        qc.x(b)
    qc.compose(U.inverse(), inplace=True)
    qc.z(q)
    qc.compose(U, inplace=True)
    for b in bflys:
        qc.x(b)
    qc.compose(U.inverse(), inplace=True)
    return qc
