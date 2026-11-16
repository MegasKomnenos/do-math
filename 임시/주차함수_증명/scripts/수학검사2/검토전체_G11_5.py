# -*- coding: utf-8 -*-
"""G11: 부록 A의 기호가 '처음 정의된 절'에 실제로 처음 나타나는지 대조(공백 제거 문자열 검색)."""
import re, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md"]
sec_re = re.compile(r"^###\s+(\d+(?:\.\d+)*)\s")
body = []  # (file, line, sec, normalized text)
for fn in files:
    cur = None
    for i, ln in enumerate(open(os.path.join(CH, fn), encoding='utf-8').read().split('\n'), 1):
        m = sec_re.match(ln)
        if m: cur = m.group(1)
        body.append((fn, i, cur, re.sub(r"\s+", "", ln)))
A = open(os.path.join(CH, "부록A.md"), encoding='utf-8').read().split('\n')
def variants(sym):
    s = re.sub(r"\s+", "", sym)
    out = {s}
    bs = chr(92)
    for cmd in ("mathrm", "mathsf", "mathfrak", "mathcal"):
        out.add(re.sub(bs + bs + cmd + r"([A-Za-z])", lambda m: bs + cmd + "{" + m.group(1) + "}", s))
        out.add(re.sub(bs + bs + cmd + r"\{([A-Za-z])\}", lambda m: bs + cmd + m.group(1), s))
    out.add(s.replace("^" + bs + "prime", "'").replace("^{" + bs + "prime}", "'"))
    out.add(s.replace("'", "^" + bs + "prime"))
    return {v for v in out if v}
cnt = 0
for i, ln in enumerate(A, 1):
    if not ln.startswith('| $'): continue
    cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
    if len(cells) < 3: continue
    syms = re.findall(r"\$([^$]+)\$", cells[0])
    secs = re.findall(r"\d+\.\d+", cells[2])
    if not syms or not secs: continue
    # 첫 기호(쉼표로 나뉘면 각각)
    sym0 = syms[0]
    parts = [p for p in re.split(r",\s*", sym0) if p.strip()]
    for part in parts[:1]:
        # 정의식 ':=' 앞만
        part = part.split(':=')[0]
        vs = variants(part)
        hits = [(fn, l, sec) for fn, l, sec, t in body if any(v in t for v in vs)]
        if not hits:
            print(f"[A L{i}] {part!r}: 본문에서 못 찾음 (표: {cells[2]})"); cnt += 1; continue
        first = hits[0]
        ok = any(first[2] == s or (first[2] or '').startswith(s + '.') for s in secs)
        if not ok:
            # 표의 절 안에도 나타나는지
            in_sec = [h for h in hits if any(h[2] == s or (h[2] or '').startswith(s + '.') for s in secs)]
            print(f"[A L{i}] {part!r}: 첫 출현 {first[0]} L{first[1]} 절 {first[2]} ≠ 표 {cells[2]}" + ("" if in_sec else " (표의 절에는 아예 없음)")); cnt += 1
print("불일치/미발견", cnt)
