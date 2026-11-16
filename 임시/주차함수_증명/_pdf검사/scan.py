import sys, json, pymupdf as fitz
pdf = sys.argv[1]; outdir = sys.argv[2]
doc = fitz.open(pdf)
print("pages", doc.page_count)
fonts = {}
report = []
mm = 72/25.4
for pno in range(doc.page_count):
    p = doc[pno]
    r = p.rect
    for f in p.get_fonts(full=True):
        fonts[f[3]] = fonts.get(f[3], 0) + 1
    # content box: margins 24mm sides, 22mm top, 24mm bottom
    left, right, top, bottom = 24*mm, r.width-24*mm, 22*mm, r.height-24*mm
    issues = []
    d = p.get_text("dict")
    for b in d["blocks"]:
        if b["type"] != 0: continue
        bb = fitz.Rect(b["bbox"])
        if bb.x1 > right + 2 or bb.x0 < left - 2:
            txt = "".join(s["text"] for l in b["lines"] for s in l["spans"])[:60]
            issues.append(("hoverflow", round(bb.x0,1), round(bb.x1,1), txt))
        if bb.y1 > bottom + 2:
            txt = "".join(s["text"] for l in b["lines"] for s in l["spans"])[:60]
            issues.append(("voverflow", round(bb.y1,1), txt))
    # drawings outside
    for dr in p.get_drawings():
        rr = dr["rect"]
        if rr.x1 > right + 2 or rr.x0 < left - 2:
            issues.append(("draw_hoverflow", round(rr.x0,1), round(rr.x1,1)))
            break
    text = p.get_text()
    if "�" in text: issues.append(("U+FFFD", text.count("�")))
    if len(text.strip()) < 40: issues.append(("sparse", len(text.strip())))
    if issues: report.append((pno+1, issues))
    pix = p.get_pixmap(dpi=100)
    pix.save(f"{outdir}/p{pno+1:03d}.png")
print("fonts:"); 
for k,v in sorted(fonts.items(), key=lambda x:-x[1]): print(" ", v, k)
print("issues:")
for pno, iss in report:
    print(pno, iss)
