import sys, pymupdf as fitz
pdf, outdir, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3])
doc = fitz.open(pdf)
for pno in range(doc.page_count):
    doc[pno].get_pixmap(dpi=dpi).save(f"{outdir}/p{pno+1:03d}.png")
print("done", doc.page_count)
