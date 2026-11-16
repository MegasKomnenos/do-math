import sys, pymupdf as fitz
# usage: crop.py pdf page x0 y0 x1 y1 out dpi   (coords in fraction of page 0..1)
pdf, pno, x0, y0, x1, y1, out, dpi = sys.argv[1], int(sys.argv[2]), *map(float, sys.argv[3:7]), sys.argv[7], int(sys.argv[8])
doc = fitz.open(pdf); p = doc[pno-1]; r = p.rect
clip = fitz.Rect(r.width*x0, r.height*y0, r.width*x1, r.height*y1)
p.get_pixmap(dpi=dpi, clip=clip).save(out)
