"""Figures for the write-up -> blog/figures/*.png"""
import os, sys, json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
sys.path.insert(0, os.path.dirname(__file__))
from compare import load, exact

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/blog/figures"; os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, AQUA, YELLOW, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6", "#e34948"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#ffffff"
plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 11,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "axes.titlecolor": INK, "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 12,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "legend.frameon": False, "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.25,
})


def note(fig, text, y=-0.02):
    fig.text(0.0, y, text, ha="left", va="top", color=MUTED, fontsize=9)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png"); plt.close(fig); print("wrote", name)


def jl(path):
    return [json.loads(l) for l in open(f"{ROOT}/results/{path}")]


# 1. Circuit structure -------------------------------------------------------
def fig_circuit():
    fig, ax = plt.subplots(figsize=(10, 2.9)); ax.set_axis_off(); ax.set_xlim(0, 10.6); ax.set_ylim(-0.4, 2.6)
    for y in (0.4, 1.2, 2.0):
        ax.plot([0.2, 10.2], [y, y], color=MUTED, lw=1.2, zorder=0)
    ax.text(0.05, 2.0, "q", ha="right", va="center", color=INK2); ax.text(0.05, 1.2, "⋮", ha="right", va="center", color=INK2)
    ax.text(0.05, 0.4, "b", ha="right", va="center", color=INK2)
    blocks = [(0.5, "U", BLUE, 0.1, 2.3), (1.9, "X", ORANGE, 0.1, 0.7), (2.9, "U†", BLUE, 0.1, 2.3), (4.3, "Z", AQUA, 1.7, 2.3),
              (5.3, "U", BLUE, 0.1, 2.3), (6.7, "X", ORANGE, 0.1, 0.7), (7.7, "U†", BLUE, 0.1, 2.3)]
    for x, lab, col, y0, y1 in blocks:
        w = 1.1 if lab.startswith("U") else 0.7
        ax.add_patch(FancyBboxPatch((x, y0), w, y1 - y0, boxstyle="round,pad=0.02,rounding_size=0.08", fc=col, ec="white", lw=2, alpha=0.92))
        ax.text(x + w / 2, (y0 + y1) / 2, lab, ha="center", va="center", color="white", fontsize=15, fontweight="bold")
    ax.add_patch(FancyBboxPatch((9.2, 1.7), 0.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white", ec=INK, lw=1.4))
    ax.text(9.6, 2.0, "⟨Z⟩", ha="center", va="center", color=INK, fontsize=12)
    for x0, x1, t in [(0.5, 4.0, "B = U† X_b U  (butterfly)"), (5.3, 8.8, "B again")]:
        ax.annotate("", xy=(x1, -0.2), xytext=(x0, -0.2), arrowprops=dict(arrowstyle="-", color=INK2, lw=1))
        ax.text((x0 + x1) / 2, -0.35, t, ha="center", va="top", color=INK2, fontsize=10)
    ax.set_title("Each challenge circuit: a double echo that measures OTOC(2) = ⟨(Z_q B)⁴⟩", pad=4)
    save(fig, "01_circuit")


# 2. Score journey -----------------------------------------------------------
SUBS = [("S1", 100, "exact statevector"), ("S2", 100, ""), ("S3", 100, ""), ("G1", 300, "exact, 30 qubits"),
        ("G3", 240, "Pauli-path CPU 1e-4"), ("G2", 540, "MPS χ=128"), ("G4", 400, "partial (17/36)"),
        ("G4", 500, "Pauli-path GPU 1e-4"), ("G3", 400, "GPU, tight thresholds"), ("G4", 500, "GPU, tight thresholds"),
        ("G3", 720, "transpilation level 3"), ("G4", 700, "transpilation level 3"), ("G4", 700, "tighter δ on 7 circuits")]
MAXP = {"S1": 100, "S2": 100, "S3": 100, "G1": 300, "G2": 600, "G3": 800, "G4": 1000}


def fig_scores():
    best, totals = {}, []
    for p, s, _ in SUBS:
        best[p] = max(best.get(p, 0), s); totals.append(sum(best.values()))
    x = np.arange(1, len(SUBS) + 1)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.step(np.r_[0, x], np.r_[0, totals], where="post", color=BLUE, lw=2.2)
    ax.scatter(x, totals, s=46, color=BLUE, zorder=3, edgecolor="white", linewidth=2)
    ax.axhline(3000, color=MUTED, lw=1, ls=(0, (4, 3))); ax.text(0.2, 3030, "maximum 3000", color=MUTED, fontsize=9, va="bottom")
    for i in (3, 4, 5, 7, 10, 11):
        p, s, lab = SUBS[i]
        ax.annotate(f"{p}: {s}  ·  {lab}", (x[i], totals[i]), xytext=(-8, 12 if i not in (4,) else 12), textcoords="offset points",
                    ha="right", fontsize=9, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels([p for p, _, _ in SUBS], fontsize=9)
    ax.set_xlim(0, len(SUBS) + 0.5); ax.set_ylim(0, 3200)
    ax.set_xlabel("submission (in order)"); ax.set_ylabel("total points (best per problem)")
    ax.set_title("Score over the hackathon: 0 → 2560 of 3000")
    note(fig, "Score per problem = max(corr², 0.1) × points, best of up to 10 submissions.")
    save(fig, "02_score_journey")

    fig, ax = plt.subplots(figsize=(10, 3.8))
    probs = ["S1", "S2", "S3", "G1", "G2", "G3", "G4"]; y = np.arange(len(probs))[::-1]
    ax.barh(y, [MAXP[p] for p in probs], color=GRID, height=0.62)
    ax.barh(y, [best[p] for p in probs], color=BLUE, height=0.62)
    for yi, p in zip(y, probs):
        ax.text(MAXP[p] + 12, yi, f"{best[p]} / {MAXP[p]}   (corr² ≈ {best[p]/MAXP[p]:.1f})", va="center", fontsize=10, color=INK)
    ax.set_yticks(y); ax.set_yticklabels(probs); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 1350); ax.set_xlabel("points")
    ax.set_title("Final score by problem")
    save(fig, "03_final_scores")


# 3. Method calibration on look-alike circuits ---------------------------------
def corr2(c, tag, qs=None):
    d, e = load(c, tag), exact(c); qs = qs or sorted(d)
    return np.corrcoef([d[q] for q in qs], [e[q] for q in qs])[0, 1] ** 2, len(qs)


def fig_calibration():
    rows = [
        ("S3 sample (25q, near-Clifford)", "Pauli-path CPU, threshold 1e-3", *corr2("S3", "pauli-path_threshold0.001"), MUTED),
        ("S3 sample (25q, near-Clifford)", "Pauli-path CPU, threshold 1e-4", *corr2("S3", "pauli-path_threshold0.0001"), BLUE),
        ("Y4 look-alike (25q fSim, 8 cycles)", "Pauli-path CPU, threshold 1e-4", *corr2("Y4", "pauli-path_threshold0.0001"), MUTED),
        ("Y4 look-alike (25q fSim, 8 cycles)", "Pauli-path GPU, tightest accepted", *corr2("Y4", "gpu_1e-5_2e-5_3e-5"), BLUE),
        ("P3 look-alike (30q Clifford+rz)", "MPS, bond dim 128", *corr2("P3", "mps.cpu_dimension128"), ORANGE),
        ("P3 look-alike (30q Clifford+rz)", "Pauli-path GPU, tightest accepted", *corr2("P3", "gpu_1e-5_2e-5_3e-5_5e-5_1e-4"), BLUE),
        ("P4 look-alike (30q fSim, 10 cycles)", "Pauli-path GPU, tightest accepted", *corr2("P4", "gpu_1e-5_2e-5_3e-5_5e-5_1e-4"), BLUE),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.8)); y = np.arange(len(rows))[::-1]
    for yi, (circ, meth, r, n, col) in zip(y, rows):
        ax.plot([0, r], [yi, yi], color=col, lw=2, alpha=0.5)
        ax.scatter([r], [yi], s=80, color=col, edgecolor="white", linewidth=2, zorder=3)
        ax.text(r + 0.015, yi, f"{r:.2f}  (n={n})", va="center", fontsize=9.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([f"{m}\n{c}" for c, m, *_ in rows], fontsize=9)
    ax.set_xlim(0, 1.13); ax.set_xlabel("corr² against exact values"); ax.grid(axis="y", visible=False)
    ax.set_title("Testing methods on circuits with known answers")
    note(fig, "Exact references: Qiskit Aer statevector (≤25 qubits) or BlueQubit's free exact 'cpu' device (30 qubits). "
              "MPS on P3 measured on its first 6 qubits only.")
    save(fig, "04_calibration")


def fig_parity():
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.4))
    panels = [("Y4", [("pauli-path_threshold0.0001", "PP threshold 1e-4", MUTED), ("gpu_1e-5_2e-5_3e-5", "PP tightest accepted", BLUE)],
               "(a) Y4: tighter threshold fixes the shrinkage"),
              ("P3", [("mps.cpu_dimension128", "MPS χ=128", ORANGE), ("gpu_1e-5_2e-5_3e-5_5e-5_1e-4", "PP tightest accepted", BLUE)],
               "(b) P3: MPS misses the big value"),
              ("P4", [("gpu_1e-5_2e-5_3e-5_5e-5_1e-4", "PP tightest accepted", BLUE)],
               "(c) P4: G4-like, still shrunk")]
    for ax, (c, series, title) in zip(axs, panels):
        e = exact(c); lo, hi = 0, 0
        for tag, lab, col in series:
            d = load(c, tag); qs = sorted(d); ex = np.array([e[q] for q in qs]); v = np.array([d[q] for q in qs])
            ax.scatter(ex, v, s=34, color=col, edgecolor="white", linewidth=1.2, label=lab, zorder=3)
            lo, hi = min(lo, ex.min(), v.min()), max(hi, ex.max(), v.max())
        pad = 0.08 * (hi - lo); lim = (lo - pad, hi + pad)
        ax.plot(lim, lim, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1); ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_aspect("equal"); ax.set_title(title, fontsize=11); ax.set_xlabel("exact ⟨Z_q⟩")
        ax.legend(loc="lower right" if c == "P3" else "upper left", fontsize=8.5, handletextpad=0.3)
    axs[0].set_ylabel("estimate")
    fig.suptitle("Estimate vs exact, one dot per circuit (dashed = perfect)", x=0.0, ha="left", fontweight="bold", fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, "05_parity")


# 4. Runtime ------------------------------------------------------------------
def fig_runtime():
    q4cpu = [r for r in jl("G3__pauli-path_threshold3e-05.jsonl") if r["q"] == 4][0]
    q4gpu = jl("G3__pauli-path.gpu_threshold3e-05.jsonl")[0]
    fig, ax = plt.subplots(figsize=(8.5, 2.4))
    vals = [(f"CPU pauli-path", q4cpu["run_time_ms"] / 1000, MUTED), ("GPU pauli-path.gpu", q4gpu["run_time_ms"] / 1000, BLUE)]
    for i, (lab, t, col) in enumerate(vals[::-1]):
        ax.barh(i, t, color=col, height=0.55); ax.text(t * 1.15, i, f"{t:,.0f} s", va="center", fontsize=10, color=INK)
    ax.set_yticks([0, 1]); ax.set_yticklabels([v[0] for v in vals[::-1]]); ax.set_xscale("log"); ax.set_xlim(3, 2e4)
    ax.grid(axis="y", visible=False); ax.set_xlabel("server run time (log scale)")
    ax.set_title(f"Same circuit (G3, qubit 4, threshold 3e-5), same answer: {q4cpu['run_time_ms']/q4gpu['run_time_ms']:.0f}× faster on GPU")
    note(fig, f"Both returned ⟨Z⟩ = {q4cpu['value']:.4f}.", y=-0.16)
    save(fig, "06_cpu_vs_gpu")


# 5. Threshold map -------------------------------------------------------------
def fig_thresholds():
    thr_levels = [1e-5, 2e-5, 3e-5, 5e-5, 1e-4]
    rows = [("G3, level 2", "G3__gpu_1e-5_2e-5_3e-5_5e-5_1e-4.jsonl"), ("G3, level 3", "G3__gpu_1e-5_2e-5_3e-5_5e-5_1e-4_tl3.jsonl"),
            ("G4, level 2", "G4__gpu_1e-5_2e-5_3e-5_5e-5_1e-4.jsonl"), ("G4, level 3", "G4__gpu_5e-5_1e-4_tl3.jsonl")]
    M = np.full((len(rows), 36), np.nan)
    for i, (_, f) in enumerate(rows):
        for r in jl(f):
            M[i, r["q"]] = thr_levels.index(r["thr"])
    seq = ["#cfe3f7", "#8fbdee", "#4f97e0", "#2a78d6", "#174e94"]
    from matplotlib.colors import ListedColormap
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.imshow(M, cmap=ListedColormap(seq), vmin=-0.5, vmax=4.5, aspect="auto")
    ax.set_xticks(range(0, 36, 5)); ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xticks(np.arange(-0.5, 36, 1), minor=True); ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", lw=2); ax.grid(which="major", visible=False); ax.tick_params(which="minor", length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xlabel("circuit index q")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in seq]
    ax.legend(handles, ["1e-5", "2e-5", "3e-5", "5e-5", "1e-4"], title="threshold used", ncol=5, loc="upper left",
              bbox_to_anchor=(0, -0.32), fontsize=9, title_fontsize=9, handlelength=1.2)
    ax.set_title("Truncation threshold used per circuit (darker = looser)")
    note(fig, "Rows 1–3: tightest threshold the server accepted. G4 level 3 was run at a fixed 5e-5 to fit the remaining credit and time.", y=-0.42); save(fig, "07_threshold_map")


# 6. Per-circuit estimates: level 2 vs level 3 -----------------------------------
def fig_levels():
    fig, axs = plt.subplots(2, 1, figsize=(11, 6.4), sharex=True)
    for ax, c, f2, f3, sc, sc2 in [(axs[0], "G3", "G3__gpu_1e-5_2e-5_3e-5_5e-5_1e-4.jsonl", "G3__gpu_1e-5_2e-5_3e-5_5e-5_1e-4_tl3.jsonl", "720/800", "400/800"),
                              (axs[1], "G4", "G4__gpu_1e-5_2e-5_3e-5_5e-5_1e-4.jsonl", "G4__gpu_5e-5_1e-4_tl3.jsonl", "700/1000", "500/1000")]:
        a = {r["q"]: r["value"] for r in jl(f2)}; b = {r["q"]: r["value"] for r in jl(f3)}
        if c == "G3":
            a[12] = a.get(12, 0.0)
        q = np.arange(36)
        for qi in q:
            ax.plot([qi, qi], [a.get(qi, 0), b[qi]], color=GRID, lw=2, zorder=1)
        ax.scatter(q - 0.0, [a.get(i, 0) for i in q], s=30, color=MUTED, label="transpilation level 2 (default)", zorder=2)
        ax.scatter(q, [b[i] for i in q], s=36, color=BLUE, edgecolor="white", linewidth=1.2, label="transpilation level 3", zorder=3)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_ylabel(f"{c}  ⟨Z_q⟩ estimate"); ax.set_title(f"{c}: level 2 scored {sc2}, level 3 scored {sc}", fontsize=11, fontweight="normal", color=INK2)
    axs[1].set_xlabel("circuit index q"); axs[1].set_xticks(range(0, 36, 5))
    h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.07, 0.955), ncol=2, fontsize=9.5)
    fig.suptitle("Transpilation level 3 changed the answers, and the score", x=0.07, ha="left", fontweight="bold", fontsize=13, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    note(fig, "Same simulator, similar thresholds; only the server-side gate pre-processing differs.", y=-0.01)
    save(fig, "08_level2_vs_level3")


# 7. G1 / G2 profiles --------------------------------------------------------------
def fig_profiles():
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, c, tag, title, bfly in [(axs[0], "G1", "cpu", "G1 · 30-qubit Haar chain, exact", [28]),
                                    (axs[1], "G2", "mps.cpu_dimension128", "G2 · 36-qubit chain with hidden weak bonds, MPS χ=128", [2, 31])]:
        d = load(c, tag); q = np.array(sorted(d)); v = np.array([d[i] for i in q])
        ax.vlines(q, 0, v, color=BLUE, lw=2); ax.scatter(q, v, s=26, color=BLUE, zorder=3, edgecolor="white", linewidth=1)
        for b in bfly:
            ax.axvline(b, color=ORANGE, lw=1.2, ls=(0, (3, 3))); ax.text(b, 1.02, "butterfly", color=ORANGE, fontsize=8.5, ha="center", va="bottom")
        ax.axhline(0, color=MUTED, lw=0.8); ax.set_title(title, fontsize=11); ax.set_xlabel("measured qubit q")
        ax.set_ylim(-0.2, 1.12)
    axs[0].set_ylabel("⟨Z_q⟩")
    axs[1].annotate("region shielded from both\nbutterflies by weak bonds", xy=(12.3, 0.45), xytext=(3.2, 0.72), fontsize=8.5,
                    color=INK2, arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    save(fig, "09_g1_g2_profiles")


# 8. Resources ----------------------------------------------------------------------
def fig_resources():
    cats = [("G4 production runs", 115, BLUE), ("G3 production runs", 75, BLUE), ("calibration on look-alikes", 89, AQUA)]
    fig, ax = plt.subplots(figsize=(9, 2.6)); y = np.arange(len(cats))[::-1]
    for yi, (lab, n, col) in zip(y, cats):
        ax.barh(yi, n, color=col, height=0.55); ax.text(n + 2, yi, f"{n} jobs", va="center", fontsize=10, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([c[0] for c in cats]); ax.grid(axis="y", visible=False); ax.set_xlim(0, 135)
    ax.set_xlabel("completed GPU jobs (pauli-path.gpu, ~$0.20 each)")
    ax.set_title(r"Where the coupon credit went: \$56.60 of \$57.80 (\$30 hackathon + \$27.80 opening credit)")
    note(fig, "283 billed jobs, 1 h 59 min on an NVIDIA A100 80GB. 190 submissions rejected by the memory check were not billed. All CPU work ran in the free tier.", y=-0.2)
    save(fig, "10_resources")


if __name__ == "__main__":
    for f in [fig_circuit, fig_scores, fig_calibration, fig_parity, fig_runtime, fig_thresholds, fig_levels, fig_profiles, fig_resources]:
        f()
