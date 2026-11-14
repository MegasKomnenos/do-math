"""한 쪽을 지정 dpi로 다시 그린다. 사용: python render_one.py <쪽번호> <dpi> [x0 y0 x1 y1 (쪽 비율 0~1)]
출력: pages_1557/zoom/p<쪽>_<dpi>[_crop].png"""
import sys, os, pymupdf as fitz
here = os.path.dirname(os.path.abspath(__file__))
pno, dpi = int(sys.argv[1]), int(sys.argv[2])
doc = fitz.open(os.path.join(here, "..", "원고.pdf"))
page = doc[pno - 1]
clip = None; suffix = ""
if len(sys.argv) >= 7:
    r = page.rect; x0, y0, x1, y1 = map(float, sys.argv[3:7])
    clip = fitz.Rect(r.width * x0, r.height * y0, r.width * x1, r.height * y1); suffix = "_crop"
out = os.path.join(here, "pages_1557", "zoom", f"p{pno:03d}_{dpi}{suffix}.png")
page.get_pixmap(dpi=dpi, clip=clip).save(out)
print(out)
