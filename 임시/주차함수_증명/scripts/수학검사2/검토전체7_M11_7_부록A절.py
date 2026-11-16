# -*- coding: utf-8 -*-
"""M11: 부록 A 각 행의 기호(쉼표로 나뉜 각각)가 장 파일에서 처음 나오는 절을 찾아 '처음 정의된 절' 열과 견준다.
거친 검사(중괄호·공백을 지운 문자열 일치); 결과는 손으로 판정."""
import re, os
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10"]
docs = []
for c in CH:
    sec = ""
    for i, ln in enumerate(rd(os.path.join(ROOT, c + ".md")).splitlines(), 1):
        ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
        if ms: sec = ms.group(2)
        docs.append((c, i, sec, ln))
def norm(s): return re.sub(r"[\s{}]", "", s)
ndocs = [(c, i, sec, norm(t)) for c, i, sec, t in docs]
tA = rd(os.path.join(ROOT, "부록A.md"))
rows = [ln for ln in tA.splitlines() if ln.startswith("| $")]
print("행 수", len(rows))
for ln in rows:
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    symcell, sec_claim = cells[0], cells[2]
    syms = re.findall(r"\$([^$]+)\$", symcell)
    parts = []
    for s in syms:
        for p in re.split(r",\s*", s): parts.append(p.strip())
    claimed = re.findall(r"\d+\.\d+", sec_claim)
    for p in parts:
        key = norm(p.split(":=")[0])
        if len(key) <= 2: continue   # 한 글자 변수는 건너뜀
        hit = None
        for c, i, sec, t in ndocs:
            if key in t: hit = (c, i, sec); break
        if not hit:
            print(f"[못 찾음] {p[:40]:40s} 표:{sec_claim}")
            continue
        c, i, sec = hit
        sec2 = ".".join(sec.split(".")[:2])
        if sec2 not in claimed and not any(sec.startswith(cl) for cl in claimed):
            print(f"[차이] {p[:40]:40s} 표:{sec_claim:12s} 첫 출현:{c}:{i} 절 {sec}")
