"""Cover image: G3 estimates on its 6x6 snake grid -> blog/figures/00_cover.png"""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = {json.loads(l)["q"]: json.loads(l)["value"] for l in open(f"{ROOT}/results/G3__gpu_1e-5_2e-5_3e-5_5e-5_1e-4_tl3.jsonl")}
BG, INK, MUTED = "#0f1420", "#f0efec", "#9a9a95"
plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
fig = plt.figure(figsize=(16, 8.4), facecolor=BG)
ax = fig.add_axes([0.58, 0.1, 0.38, 0.8]); ax.set_facecolor(BG); ax.set_axis_off()
cmap = LinearSegmentedColormap.from_list("d", ["#eb6834", "#3a3f4d", "#3987e5"])
pos = {}
for r in range(6):
    for c in range(6):
        q = r * 6 + (c if r % 2 == 0 else 5 - c); pos[q] = (c, 5 - r)
for q in range(35):
    (x0, y0), (x1, y1) = pos[q], pos[q + 1]
    ax.plot([x0, x1], [y0, y1], color="#2a3142", lw=3, zorder=1)
for r in range(5):
    for c in range(6):
        a, b = r * 6 + (c if r % 2 == 0 else 5 - c), (r + 1) * 6 + (c if (r + 1) % 2 == 0 else 5 - c)
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color="#2a3142", lw=1.5, ls=(0, (2, 3)), zorder=1)
for q, (x, y) in pos.items():
    val = v[q]; s = 300 + 4200 * abs(val) ** 0.6
    ax.scatter(x, y, s=s * 2.2, color=cmap((np.clip(val, -1, 1) + 1) / 2), alpha=0.18, zorder=2, linewidths=0)
    ax.scatter(x, y, s=s, color=cmap((np.clip(val, -1, 1) + 1) / 2), zorder=3, edgecolor=BG, linewidth=2)
bx, by = pos[15]
ax.scatter(bx, by, s=2400, facecolor="none", edgecolor="#eda100", lw=2.5, zorder=4)
ax.text(bx, by - 0.62, "butterfly", color="#eda100", ha="center", va="top", fontsize=13)
ax.set_xlim(-0.7, 5.7); ax.set_ylim(-0.8, 5.7)
fig.text(0.05, 0.70, "Simulating quantum chaos", color=INK, fontsize=38, fontweight="bold")
fig.text(0.05, 0.615, "without a quantum computer", color=INK, fontsize=38, fontweight="bold")
fig.text(0.05, 0.47, "Out-of-time-order correlators on 30–38 qubits,\nestimated with classical simulators", color=MUTED, fontsize=21, linespacing=1.5)
fig.text(0.05, 0.24, "2560 / 3000", color="#3987e5", fontsize=54, fontweight="bold")
fig.text(0.05, 0.18, "BlueQubit Midwest Quantum Hackathon", color=MUTED, fontsize=18)
fig.text(0.95, 0.035, "G3 estimates ⟨Z_q⟩ on its 6×6 grid · blue > 0, orange < 0, size = magnitude", color="#6b6e78", fontsize=11, ha="right")
fig.savefig(f"{ROOT}/blog/figures/00_cover.png", dpi=125, facecolor=BG); print("ok")
