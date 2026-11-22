"""Compare result files against exact values: python src/compare.py S3 [tags...]"""
import sys, os, json, csv, glob
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(circ, tag):
    d = {}
    for l in open(os.path.join(ROOT, "results", f"{circ}__{tag}.jsonl")):
        r = json.loads(l)
        if r.get("value") is not None:
            d[r["q"]] = r["value"]
    return d


def exact(circ):
    p = os.path.join(ROOT, "data", f"exact_{circ}.csv")
    if os.path.exists(p):
        return {int(r[0].split("_")[-1]): float(r[1]) for r in csv.reader(open(p))}
    try:
        return load(circ, "cpu")
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    c = sys.argv[1]
    tags = sys.argv[2:] or [os.path.basename(p).split("__")[1][:-6] for p in sorted(glob.glob(f"{ROOT}/results/{c}__*.jsonl"))]
    ex = exact(c)
    for t in tags:
        d = load(c, t)
        qs = sorted(d)
        v = np.array([d[q] for q in qs])
        line = f"{t:40s} n={len(qs):2d}"
        if ex and all(q in ex for q in qs) and len(qs) > 2:
            e = np.array([ex[q] for q in qs])
            line += f" corr2={np.corrcoef(v, e)[0,1]**2:.4f}"
        print(line, np.round(v, 3).tolist())
    if ex:
        print(f"{'exact':40s}", np.round([ex[q] for q in sorted(ex)], 3).tolist())
