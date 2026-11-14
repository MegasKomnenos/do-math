"""렌더된 PDF의 자동 검사: 쪽 수, 글자 크기(축소 여부), 여백 밖 글자, 폴백 글꼴, 쪽 이미지 렌더."""
import sys, collections, statistics, pymupdf as fitz
pdf, outdir = sys.argv[1], sys.argv[2]
doc = fitz.open(pdf); mm = 72/25.4
print("pages", doc.page_count, "toc entries", len(doc.get_toc()))
sizes = collections.Counter(); fonts = collections.defaultdict(collections.Counter); fpages = collections.defaultdict(set)
issues = []
for pno in range(doc.page_count):
    p = doc[pno]; r = p.rect
    left, right, top, bottom = 24*mm, r.width-24*mm, 22*mm, r.height-24*mm
    d = p.get_text("rawdict")
    for b in d["blocks"]:
        if b["type"] != 0: continue
        bb = fitz.Rect(b["bbox"])
        txt = "".join(c["c"] for l in b["lines"] for s in l["spans"] for c in s["chars"])
        if bb.x1 > right + 2 or bb.x0 < left - 2:
            issues.append((pno+1, "H", round(bb.x0,1), round(bb.x1,1), txt[:50]))
        if bb.y1 > bottom + 1.5 and bb.y0 < 800:
            issues.append((pno+1, "V", round(bb.y1,1), txt[:50]))
        for l in b["lines"]:
            for s in l["spans"]:
                if "Type3" in s["font"] and bb.y0 < 800: sizes[round(s["size"],1)] += len(s["chars"])
                if "KaTeX" not in s["font"] and "Type3" not in s["font"]:
                    for c in s["chars"]: fonts[s["font"]][c["c"]] += 1
                    fpages[s["font"]].add(pno+1)
    if outdir != "-":
        p.get_pixmap(dpi=100).save(f"{outdir}/p{pno+1:03d}.png")
print("body (Type3) font sizes:", sizes.most_common(4))
print("fallback fonts:")
for f, c in fonts.items(): print("  ", f, "pages", len(fpages[f]), "chars", "".join(sorted(c))[:60], sum(c.values()))
print("margin issues:", len(issues))
for i in issues[:60]: print("  ", i)
