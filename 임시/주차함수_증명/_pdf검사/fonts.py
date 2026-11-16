import sys, collections, pymupdf as fitz
doc = fitz.open(sys.argv[1])
byfont = collections.defaultdict(collections.Counter)
pagesby = collections.defaultdict(set)
samples = collections.defaultdict(list)
mm=72/25.4
extra = []
for pno in range(doc.page_count):
    p = doc[pno]
    r = p.rect
    left, right, top, bottom = 24*mm, r.width-24*mm, 22*mm, r.height-24*mm
    d = p.get_text("rawdict")
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                f = s["font"]
                for ch in s["chars"]:
                    byfont[f][ch["c"]] += 1
                    pagesby[f].add(pno+1)
                if len(samples[f])<6:
                    samples[f].append((pno+1, "".join(c["c"] for c in s["chars"])[:40]))
        bb = fitz.Rect(b["bbox"])
        if bb.y1 > bottom + 2 and bb.y1 < 800:
            extra.append((pno+1, round(bb.y1,1), "".join(c["c"] for l in b["lines"] for s in l["spans"] for c in s["chars"])[:50]))
        if bb.x1 > right + 2 or bb.x0 < left - 2:
            extra.append((pno+1, "H", round(bb.x0,1), round(bb.x1,1), "".join(c["c"] for l in b["lines"] for s in l["spans"] for c in s["chars"])[:50]))
for f, cnt in sorted(byfont.items(), key=lambda x: -sum(x[1].values())):
    if "KaTeX" in f: continue
    tot = sum(cnt.values())
    print(f"== {f!r} total {tot} pages {len(pagesby[f])}")
    print("   chars:", "".join(sorted(cnt))[:300])
    print("   top:", cnt.most_common(25))
    print("   samples:", samples[f][:4])
print("extra:", extra)
