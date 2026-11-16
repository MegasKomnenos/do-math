# -*- coding: utf-8 -*-
"""부록 A의 「기록의 글자」 열과 부록 C 글자 표의 기록 목록을 견준다(이 글의 글자 문자열이 같은 행끼리)."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
A = open(os.path.join(BASE,'부록A.md'),encoding='utf-8').read()
C = open(os.path.join(BASE,'부록C.md'),encoding='utf-8').read()
def norm(s): return re.sub(r'\s+','',s.replace('\,','').replace('\prime',"'"))
Arows={}
for ln in A.split('\n'):
    if ln.startswith('| $'):
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]
        for sym in re.findall(r'\$([^$]+)\$', c[0]):
            Arows.setdefault(norm(sym), []).append((c[0], c[3] if len(c)>3 else ''))
i0 = C.index('### 기록의 글자와 이 글의 글자')
Crows=[]
for ln in C[i0:].split('\n'):
    if ln.startswith('| $'):
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]
        Crows.append(c)
print("부록 C 글자 표 행 수:", len(Crows))
for c in Crows:
    syms = re.findall(r'\$([^$]+)\$', c[0])
    recs_C = set(re.findall(r'\[r[0-9a-f]{7}\]', c[1]))
    for sym in syms:
        key=norm(sym)
        if key in Arows:
            for (asym, arec) in Arows[key]:
                recs_A = set(re.findall(r'\[r[0-9a-f]{7}\]', arec))
                if arec.strip()=='—' and recs_C:
                    print(f"A 『{asym[:40]}』 기록의 글자 '—'  /  C 행 『{c[0][:50]}』 기록 {sorted(recs_C)} 글자 『{c[2][:70]}』")
                else:
                    missing = recs_C - recs_A
                    if missing and recs_A:
                        print(f"A 『{asym[:40]}』 기록 {sorted(recs_A)}  /  C 행 『{c[0][:50]}』에만 있는 기록 {sorted(missing)}")
