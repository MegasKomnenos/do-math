# -*- coding: utf-8 -*-
"""부록 A 각 행의 첫 기호가 본문(장1–장10)에서 처음 나오는 절을 찾아 「처음 정의된 절」과 맞세운다.
공백을 지운 문자열 일치로 찾으므로 과·소검출이 있다. 판단은 출력을 읽고 사람이 한다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'
order = ['장1.md', '장2.md', '장3.md', '장4.md', '장5A.md', '장5B.md', '장6.md', '장7A.md', '장7B.md', '장8.md', '장9.md', '장10.md']
norm = lambda s: re.sub(r'\s+', '', s)
texts = []
for c in order:
    sec = None
    for ln in open(ROOT + '\\' + c, encoding='utf-8').read().split('\n'):
        ms = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)', ln)
        if ms: sec = ms.group(1)
        texts.append((c, sec, norm(ln)))
A = open(ROOT + r'\부록A.md', encoding='utf-8').read()
for ln in A.split('\n'):
    if not ln.startswith('| $'): continue
    cells = [x.strip() for x in ln.strip().strip('|').split(' | ')]
    if len(cells) < 3: continue
    sym, decl = cells[0], cells[2]
    first = sym.split(', ')[0].strip().strip('$')
    first = re.sub(r':=.*$', '', first).strip()
    core = norm(first)
    hits = [(c, s) for (c, s, t) in texts if core and core in t]
    if not hits:
        print(f'  없음   {sym[:70]}   (A: {decl})'); continue
    fn, hs = hits[0]; hs = hs or ''
    declsecs = re.findall(r'\d+(?:\.\d+)?', decl)
    ok = any(hs == d or hs.startswith(d + '.') or (d.count('.') == 0 and hs.split('.')[0] == d) for d in declsecs)
    if not ok:
        # 선언 절 안에 출현이 있는지도 본다
        indecl = any((s or '').startswith(d) for (c, s) in hits for d in declsecs)
        print(f'  {sym[:70]}   A={decl}   첫 출현 {fn} §{hs}' + ('' if indecl else '   (선언 절 안 출현 없음)'))
