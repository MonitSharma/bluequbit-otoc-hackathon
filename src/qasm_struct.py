import sys, re, collections
f = sys.argv[1]
lines = open(f).read().splitlines()
cz = []; spec = []
for i, l in enumerate(lines):
    m = re.match(r'cz q\[(\d+)\],q\[(\d+)\];', l)
    if m: cz.append((i, int(m[1]), int(m[2])))
    m = re.match(r'(x|z) q\[(\d+)\];', l)
    if m: spec.append((i, m[1], int(m[2])))
print("n_cz", len(cz), "special", spec)
# split at special ops
bounds = [0] + [s[0] for s in spec] + [len(lines)]
for a, b in zip(bounds[:-1], bounds[1:]):
    seg = [c for c in cz if a <= c[0] < b]
    pairs = collections.Counter((min(p,q),max(p,q)) for _,p,q in seg)
    print("segment", a, b, "cz", len(seg), "pairs", len(pairs), sorted(pairs.items())[:40])
