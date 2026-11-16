# 검토전체8 N11: 11.4절 문헌 표의 "쓰인 자리"를 본문 검색으로 대조한다.
import re, json, os, glob
blocks = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks.json", encoding="utf-8"))
root = r"C:\math\임시\주차함수_증명\장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
sec_re = re.compile(r"^(#{2,4})\s+(\d+(?:\.\d+)*)\.?\s")
head_re = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}\s*([\(\[].*?|\.)\*\*")
# 줄마다 (파일, 절, 현재 진술 라벨)
lines = []
for ch in order:
    cur_sec=None; cur=None
    for i, ln in enumerate(open(os.path.join(root, ch+".md"), encoding="utf-8").read().split("\n"), 1):
        ms = sec_re.match(ln)
        if ms: cur_sec = ms.group(2); cur=None
        mh = head_re.match(ln)
        if mh: cur = mh.group(2)
        lines.append((ch, i, cur_sec, cur, ln))
        if cur and ln.strip().endswith("∎"): cur=None
dfiles = {os.path.basename(f): open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(root, "부록D_*.md"))}
keys = {
 "Konheim": r"Konheim", "Foata": r"Foata|Pollak", "Celano": r"Celano", "Aguilar": r"Aguilar", "Stanley 지수": r"지수 공식", "Cayley": r"Cayley 공식|Cayley의 공식", "Lagrange": r"Lagrange 역변환",
 "Knuth 갈고리": r"Knuth|갈고리", "Flajolet": r"Flajolet", "Tanner": r"Tanner", "Robbins": r"Robbins", "Petersson": r"Petersson", "Janson": r"Janson", "Ibragimov": r"Ibragimov",
 "Ahlfors": r"Ahlfors|편각 원리|Cauchy 적분 공식|Cauchy의 적분 공식|부분분수", "Graham": r"Euler–Maclaurin|Euler-Maclaurin|Graham", "FKG": r"FKG|Fortuin", "Jensen": r"Jensen", "Wallis": r"Wallis", "Corless": r"Corless|Lambert", "Grimmett": r"Grimmett", "Harris": r"Harris", "Comtet": r"Comtet|Faà di Bruno|Faa di Bruno", "Apostol": r"Apostol|Euler 합 공식", "Titchmarsh": r"Titchmarsh",
}
for name, pat in keys.items():
    rx = re.compile(pat)
    hits = {}
    for ch, i, sec, lab, ln in lines:
        if rx.search(ln):
            hits.setdefault((ch, sec, lab), 0); hits[(ch, sec, lab)] += 1
    dh = [k for k, t in dfiles.items() if rx.search(t)]
    print(f"--- {name}: " + "; ".join(f"{ch} {sec} {lab or '(산문)'}" for (ch, sec, lab) in sorted(hits, key=lambda x: (order.index(x[0]), x[1] or ''))) + (f" | D: {dh}" if dh else ""))
