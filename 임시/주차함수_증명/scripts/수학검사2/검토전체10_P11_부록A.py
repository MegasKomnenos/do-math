# -*- coding: utf-8 -*-
"""부록 A의 기호마다 본문에서 처음 나타나는 절을 찾아 「처음 정의된 절」과 견준다(어림 검사; 결과는 손으로 다시 본다)."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
order = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']
docs=[]
for f in order:
    sec=None
    for i,ln in enumerate(open(os.path.join(BASE,f),encoding='utf-8').read().split('\n'),1):
        m = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)\s', ln)
        if m: sec=m.group(1)
        docs.append((f,sec,i,ln))
A = open(os.path.join(BASE,'부록A.md'),encoding='utf-8').read()
rows=[]
for ln in A.split('\n'):
    if ln.startswith('| $') or ln.startswith('| 기호'): 
        if ln.startswith('| 기호'): continue
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]
        rows.append(c)
print("부록 A 기호 행 수:", len(rows))
def keys_of(sym):
    # 첫 기호만, $...$ 안의 핵심 문자열
    s = sym.split(',')[0].strip().strip('$')
    s = re.sub(r':=.*$','',s).strip()
    # 첨자/인수 제거한 핵심
    core = re.sub(r'\(.*\)$','',s)
    core = re.sub(r'\^\{?\?[a-zA-Z0-9]*\}?$','',core) if len(core)>4 else core
    return s, core
for c in rows:
    sym, meaning, sec, rec = c[0], c[1], c[2], c[3] if len(c)>3 else ''
    s, core = keys_of(sym)
    cand = [s, core]
    found=None
    for k in cand:
        if len(k)<2: continue
        for f,se,i,ln in docs:
            if k in ln:
                found=(f,se,i,k); break
        if found: break
    secs_tab = re.findall(r'\d+(?:\.\d+)?', sec)
    first_tab = secs_tab[0] if secs_tab else sec
    if not found:
        print(f"?? 못 찾음: {sym[:40]} | 표 {sec}")
    else:
        f,se,i,k = found
        se2 = '.'.join((se or '?').split('.')[:2])
        flag = '' if se2==first_tab or (se and se.startswith(first_tab)) else '  <<< 다름'
        if flag: print(f"{sym[:45]:45} 표 {sec:12} 첫 출현 {f}:{i} §{se} (키 『{k}』){flag}")
