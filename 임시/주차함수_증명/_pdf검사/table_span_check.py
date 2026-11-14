"""tables.json(표 높이·머리·첫·끝 칸)과 PDF로, 한 쪽에 들어가는 표가 두 쪽에 걸쳤는지 검사한다."""
import json, sys, pymupdf as fitz
doc = fitz.open(sys.argv[1]); tables = json.load(open(sys.argv[2], encoding="utf-8")); ch = float(sys.argv[3])
def pages_with(txt):
    txt = txt.replace("\u200b", "").strip()
    if len(txt) < 2: return set()
    return {pno+1 for pno in range(doc.page_count) if doc[pno].search_for(txt[:25])}
bad = 0
for t in tables:
    frac = t["h"] / ch
    if frac > 0.95: continue
    ph = pages_with(t["head"]); pl = pages_with(t["last"])
    # 머리와 끝 행이 같은 쪽에 함께 있는 쪽이 하나라도 있으면 통과
    if ph and pl and not (ph & pl):
        bad += 1; print(f"걸침: 머리 {sorted(ph)[:4]} 끝 {sorted(pl)[:4]} 높이 {frac:.2f} {t['head'][:12]!r} / {t['last'][:20]!r}")
    elif not ph or not pl:
        print(f"판정 불가(글자 못 찾음): {t['head'][:12]!r} / {t['last'][:20]!r}")
print("한 쪽짜리 표 가운데 걸친 것:", bad)
