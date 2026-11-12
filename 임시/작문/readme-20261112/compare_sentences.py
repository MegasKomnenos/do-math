import re, sys, os
old_path = sys.argv[1]; new_path = sys.argv[2]
def load(p):
    return open(p, encoding="utf-8").read()
def strip_code(t):
    return re.sub(r"```.*?```", "", t, flags=re.S)
def sentences(t):
    t = strip_code(t)
    out = []
    for line in t.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            out.extend(c for c in cells if c)
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`*\[(\d\"'])", s)
        out.extend(p.strip() for p in parts if p.strip())
    return out
def norm(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
old = load(old_path); new = load(new_path)
old_s = [norm(s) for s in sentences(old)]
new_s = [norm(s) for s in sentences(new)]
new_text = norm(strip_code(new))
old_text = norm(strip_code(old))
missing = [s for s in old_s if s not in new_text and s not in new_s]
added = [s for s in new_s if s not in old_text and s not in old_s]
print("OLD sentences:", len(old_s), " NEW sentences:", len(new_s))
print("\n=== OLD sentences not found in NEW (%d) ===" % len(missing))
for s in missing: print("-", s)
print("\n=== NEW sentences not found in OLD (%d) ===" % len(added))
for s in added: print("+", s)
# paragraph statistics for NEW
paras = [p.strip() for p in re.split(r"\n\s*\n", strip_code(new)) if p.strip()]
prose = [p for p in paras if not p.startswith("#") and not p.startswith("|") and not p.startswith("- ") and not p.startswith("```") and not p.startswith("$")]
wc = [len(p.split()) for p in prose]
sc = [len(re.findall(r"[.!?](\s|$)", p)) for p in prose]
print("\n=== NEW paragraph stats ===")
print("prose paragraphs:", len(prose), " avg words: %.0f" % (sum(wc)/len(wc)), " avg sentences: %.1f" % (sum(sc)/len(sc)))
print("paragraphs >150 words:", sum(1 for w in wc if w > 150), " >120:", sum(1 for w in wc if w > 120))
for p, w, s in sorted(zip(prose, wc, sc), key=lambda x: -x[1])[:12]:
    print(f"  {w:4d} w {s:2d} s  {p[:70]}...")
heads = re.findall(r"^(#{2,3}) (.+)$", new, flags=re.M)
print("\n=== headings ===")
for h, t in heads: print(" "*(len(h)-2)*2 + h + " " + t)
print("\n=== relative links ===")
root = os.path.dirname(os.path.abspath(old_path))
for m in re.finditer(r"\]\(([^)]+)\)", new):
    link = m.group(1)
    if link.startswith("http"): continue
    print(("OK   " if os.path.exists(os.path.join(root, link)) else "MISS ") + link)
