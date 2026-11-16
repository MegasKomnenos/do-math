# -*- coding: utf-8 -*-
"""L11 검토 보조 5: 부록 A의 「처음 정의된 절」을 이름 있는 기호의 첫 출현 절과 견준다(참고용; 단일 글자 기호는 건너뛴다)."""
import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
CH = r"C:\math\임시\주차함수_증명\장v2"
order = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']
texts = []
for fn in order:
    cur = None
    for i, line in enumerate(open(os.path.join(CH, fn), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^###+ (\d+(?:\.\d+)*)', line)
        if m: cur = m.group(1)
        texts.append((fn, cur, i, line))
def first(tok):
    for fn, sec, i, line in texts:
        if tok in line: return (sec, fn, i)
    return None
pat1 = re.compile(r'\\(?:mathrm|mathsf|mathfrak|mathcal|operatorname)\s*\{[A-Za-z]+\}(?:[_^]\{[^}]*\})?|\\(?:mathfrak|mathcal|mathsf)\s[A-Za-z](?:[_^]\{[^}]*\}|[_^][A-Za-z0-9])?')
pat2 = re.compile(r'\\(?:Upsilon|Theta|Omega|Psi|Pi|Xi|Gamma|Phi|Lambda|varsigma|varkappa|vartheta|varrho|zeta|xi|kappa|epsilon|chi|omega|tau|rho|mu|nu|lambda)(?:[_^]\{[^}]*\}|[_^][A-Za-z0-9])?')
A = open(os.path.join(CH, '부록A.md'), encoding='utf-8').read().split('\n')
for l in A:
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    if len(cells) != 4: continue
    sym, sec = cells[0], cells[2]
    toks = pat1.findall(sym) or pat2.findall(sym)
    if not toks: continue
    t = toks[0]
    f = first(t)
    listed = re.findall(r'\d+(?:\.\d+)*', sec)
    f_sec = f[0] if f else None
    ok = f_sec is not None and any(f_sec == s or f_sec.startswith(s + '.') for s in listed)
    if not ok:
        print(f"{sym[:55]:55s} | A절={sec:14s} | 첫 출현={f} | tok={t}")
