# -*- coding: utf-8 -*-
"""N14: 특정 장에서 맨 글자(글꼴 없는 이탤릭)가 나오는 수식 조각을 보여 준다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
FONT = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb|mathscr|mathbf|operatorname|text|textrm|mathit)\s*(\{[^{}]*\}|[A-Za-z])')
MATH = re.compile(r'\$\$(.*?)\$\$|\$(.*?)\$', re.S)
def ctx(files, letter, maxn=12):
    n = 0
    for f in files:
        lines = open(os.path.join(ROOT, "장v2", f + ".md"), encoding='utf-8').read().split('\n')
        for i, ln in enumerate(lines, 1):
            for m in MATH.finditer(ln):
                seg = m.group(1) if m.group(1) is not None else m.group(2)
                s = FONT.sub(' ', seg); s = re.sub(r'\\[A-Za-z]+', ' ', s); s = re.sub(r'\\.', ' ', s)
                if re.search(r'(?<![A-Za-z])' + letter + r'(?![A-Za-z])', s):
                    print(f"{f}:{i}: {seg[:90]}"); n += 1
                    if n >= maxn: return
pairs = [(["장11"], "N"), (["장6"], "r"), (["장10"], "r"), (["장4"], "q"), (["장1"], "X"), (["장4"], "X"),
         (["장5A", "장5B"], "X"), (["장7A", "장7B"], "X"), (["장9"], "X"), (["장10"], "X"), (["장6"], "W"), (["장3"], "d")]
if len(sys.argv) > 2:
    pairs = [(sys.argv[1].split(','), sys.argv[2])]
for files, L in pairs:
    print("=====", files, L); ctx(files, L, 8)
