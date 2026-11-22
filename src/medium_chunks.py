"""Split blog/otoc_hackathon.md into Medium-friendly chunks -> blog/medium_chunks.json"""
import re, json, os, markdown
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md = open(f"{ROOT}/blog/otoc_hackathon.md").read()
lines = md.split("\n")
title = lines[0].lstrip("# ").strip(); body = "\n".join(lines[1:]).strip()

def table_to_list(m):
    rows = [r.strip().strip("|").split("|") for r in m.group(0).strip().split("\n")]
    head, data = [c.strip() for c in rows[0]], rows[2:]
    out = []
    for r in data:
        c = [x.strip() for x in r]
        rest = "; ".join(f"{h.lower()}: {v}" for h, v in zip(head[1:], c[1:]) if v)
        out.append(f"- **{c[0]}**: {rest}")
    return "\n".join(out) + "\n"
body = re.sub(r"(?:^\|.*\|\n)+", table_to_list, body + "\n", flags=re.M)
body = body.replace("\n---\n", "\n")
chunks, buf = [], []
for ln in body.split("\n"):
    m = re.match(r"!\[(.*)\]\((.*)\)", ln.strip())
    if m:
        if "\n".join(buf).strip(): chunks.append({"type": "html", "html": markdown.markdown("\n".join(buf))})
        chunks.append({"type": "img", "src": m.group(2), "alt": m.group(1)}); buf = []
    else:
        buf.append(ln)
if "\n".join(buf).strip(): chunks.append({"type": "html", "html": markdown.markdown("\n".join(buf))})
for c in chunks:
    if c["type"] == "html":
        c["html"] = c["html"].replace("<h2>", "<h3>").replace("</h2>", "</h3>").replace("<h3>", "<h3>")
json.dump({"title": title, "chunks": chunks}, open(f"{ROOT}/blog/medium_chunks.json", "w"))
print(title, len(chunks), [c["type"][0] for c in chunks])
