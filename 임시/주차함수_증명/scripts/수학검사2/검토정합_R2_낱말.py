# -*- coding: utf-8 -*-
"""R2 (ㄴ): 장부 3절 낱말 사전의 낱말 열을 쉼표로 갈라, 각 낱말이 장 파일에 있는지와 처음 나오는 절을 구해 「첫 정의 절」과 견준다(읽기 전용; 휴리스틱)."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
ORDER = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
IDX = []
for ch in ORDER:
    sec = None
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n"), 1):
        m = re.match(r"^### (\d+\.\d+)", ln)
        if m: sec = m.group(1)
        m2 = re.match(r"^## (\d+)\.", ln)
        if m2 and sec is None: sec = m2.group(1) + "(도입)"
        IDX.append((ch, i, sec, ln))
def hits(word):
    out = []
    for ch, i, sec, ln in IDX:
        if word in ln: out.append((ch, i, sec))
    return out
L = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read().split("\n")
out = io.StringIO()
for n in range(502, 706):
    ln = L[n]
    if not ln.startswith("|") or ln.startswith("|---"): continue
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    if len(cells) < 4 or cells[0] == "낱말": continue
    words = [w.strip() for w in re.split(r",\s*", cells[0]) if w.strip()]
    decl = cells[2]
    decl_secs = re.findall(r"\d+\.\d+", decl)
    for w in words:
        wq = re.sub(r"\$[^$]*\$", "", w).strip()
        wq = re.sub(r"\(.*?\)", "", wq).strip()
        if not wq or len(wq) < 2: 
            out.write(f"[{n+1}] (건너뜀: {w})\n"); continue
        h = hits(wq)
        if not h:
            out.write(f"[{n+1}] 본문 없음: 「{wq}」 (선언 절 {decl})\n"); continue
        first = h[0]
        secs = [s for _, _, s in h]
        # 선언 절 가운데 하나가 본문 출현 절에 있는가; 첫 출현이 선언보다 앞서는가
        in_decl = any(s in decl_secs for s in secs) if decl_secs else True
        first_ok = (first[2] in decl_secs) if decl_secs else True
        flag = ""
        if not in_decl: flag = "선언 절에 출현 없음"
        elif not first_ok: flag = "첫 출현이 선언 절과 다름"
        if flag:
            out.write(f"[{n+1}] {flag}: 「{wq}」 선언 {decl} | 첫 출현 {first[0]}:{first[1]} ({first[2]}) | 출현 {len(h)}회\n")
sys.stdout.buffer.write(out.getvalue().encode("utf-8"))
