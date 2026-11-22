# OTOC estimation — BlueQubit Midwest Quantum Hackathon

Classical estimation of out-of-time-order correlators (OTOC(2)) on 4–38 qubit echo circuits
(`U · X_b · U† · Z_q · U · X_b · U†`, then ⟨Z_q⟩). Final score: **2560 / 3000**.
No quantum hardware was used.

| Problem | Method | Score |
|---|---|---|
| S1–S3 | exact statevector (Qiskit Aer) | 300 / 300 |
| G1 | exact, BlueQubit `cpu` | 300 / 300 |
| G2 | MPS, bond dimension 128 | 540 / 600 |
| G3 | Pauli-path GPU, transpilation level 3, tightest accepted threshold | 720 / 800 |
| G4 | Pauli-path GPU, transpilation level 3, threshold 5e-5 (2e-5 on top circuits) | 700 / 1000 |

The full write-up is in [`blog/otoc_hackathon.md`](blog/otoc_hackathon.md); figures are in `blog/figures/`.

## Layout

- `src/runner.py` — resumable BlueQubit job runner (one result per line in `results/<C>__<tag>.jsonl`)
- `src/adaptive.py` — sequential GPU Pauli-path runner that uses the tightest threshold the server accepts per circuit
- `src/synth.py`, `src/make_synth.py`, `src/make_proxy.py` — look-alike circuit generators (Haar chains, fSim grids, Clifford+Rz grids)
- `src/exact_samples.py`, `src/exact_local.py` — exact reference values with Qiskit Aer
- `src/compare.py`, `src/subcmp.py` — corr² against exact values
- `src/blog_plots.py`, `src/cover.py` — figures for the write-up
- `data/` — sample QASMs, look-alike circuits and exact values
- `results/` — raw job results and logs
- `submissions/` — submitted CSVs

## Setup

```bash
uv venv .venv && uv pip install --python .venv/bin/python bluequbit qiskit qiskit-aer numpy matplotlib
```

Put your BlueQubit API token in `.bq_token` (git-ignored), then for example:

```bash
.venv/bin/python src/adaptive.py "G3:1e-5,2e-5,3e-5,5e-5,1e-4:tl=3"
```
