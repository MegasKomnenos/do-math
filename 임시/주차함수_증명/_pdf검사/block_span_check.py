"""진술 블록(왼쪽 세로선)이 쪽 사이에서 갈라진 곳을 센다: 세로선이 아래 여백 선까지 닿는 쪽(이어짐)을 찾는다."""
import sys, pymupdf as fitz
doc = fitz.open(sys.argv[1]); mm = 72/25.4
hits = []
for pno in range(doc.page_count):
    page = doc[pno]; r = page.rect; top = 22*mm; bottom = r.height - 24*mm
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] != "re": continue
            rect = it[1]
            if rect.width < 3 and rect.height > 20 and rect.x0 < 80:   # 블록 왼쪽 세로선
                if rect.y1 > bottom - 3: hits.append((pno+1, "아래로 이어짐", round(rect.y0), round(rect.y1)))
print("쪽 아래까지 닿은 진술 블록 세로선:", len(hits))
for h in hits[:40]: print("  ", h)
