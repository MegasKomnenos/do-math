# -*- coding: utf-8 -*-
"""M11: 11.4 문헌 표 대조 자료 — 장 파일에서 저자명·결과명이 나오는 자리를 진술 라벨/절로 적는다."""
import re, glob, os
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()
HEAD0 = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}")
terms = ["Konheim", "Foata", "Pollak", "Celano", "Aguilar", "Stanley", "Knuth", "Flajolet", "Robbins", "Petersson", "Janson", "Ibragimov", "Ahlfors",
         "Graham", "Fortuin", "FKG", "Jensen", "Wallis", "Corless", "Tanner", "Grimmett", "Harris", "Comtet", "Apostol", "Titchmarsh", "Faà",
         "Euler–Maclaurin", "Euler 합", "Lagrange 역변환", "Cayley 공식", "지수 공식", "편각 원리", "Cauchy 적분", "Cauchy의 적분", "Cauchy 부등식", "부분분수", "Lambert", "나무 함수의 임계", "Borel–Tanner", "갈고리", "표준"]
hits = {t: [] for t in terms}
for f in sorted(glob.glob(os.path.join(ROOT, "장*.md"))) + sorted(glob.glob(os.path.join(ROOT, "부록D_*.md"))):
    fn = os.path.basename(f)
    if fn == "장11.md": continue
    sec = ""; cur = "(진술 밖)"
    for i, ln in enumerate(rd(f).splitlines(), 1):
        ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
        if ms: sec = ms.group(2); cur = "(진술 밖)"; continue
        md = re.match(r"^### D\.\{\{D:([^}]+)\}\}", ln)
        if md: cur = "D:" + md.group(1); continue
        m = HEAD0.match(ln)
        if m: cur = f"{m.group(1)} {m.group(2)}:{m.group(3)}"
        elif ln.startswith("**증명") or ln.startswith("**증명."):
            pass
        for t in terms:
            if t in ln:
                # 문장 일부
                j = ln.find(t); frag = ln[max(0, j-60):j+80].replace("|", "/")
                hits[t].append(f"{fn}:{i} [{sec}] {cur} :: {frag}")
for t in terms:
    print(f"\n===== {t} ({len(hits[t])})")
    for h in hits[t]: print("  ", h)
