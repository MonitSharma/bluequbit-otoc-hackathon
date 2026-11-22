"""Compare tags on their common qubit subset: python src/subcmp.py P4 tagA tagB ..."""
import sys, os, glob, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from compare import load, exact
c = sys.argv[1]; tags = sys.argv[2:]
ex = exact(c); ds = {t: load(c, t) for t in tags}
qs = sorted(set.intersection(*[set(d) for d in ds.values()]))
e = np.array([ex[q] for q in qs]); print("n", len(qs), qs)
for t, d in ds.items():
    v = np.array([d[q] for q in qs]); print(f"{t:45s} corr2={np.corrcoef(v, e)[0,1]**2:.3f}", np.round(v, 4).tolist())
print(f"{'exact':45s}", np.round(e, 4).tolist())
