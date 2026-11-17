# -*- coding: utf-8 -*-
"""결정 K6 — 배타 영역의 셈(행·바이트·진술·십진 상수·라벨 행)."""
import re, sys
from pathlib import Path
ROOT=Path(r"C:/math/임시/주차함수_증명"); V=ROOT/"장v2"
def rb(p): return (V/p).read_bytes()
def lines(p): return rb(p).decode('utf-8').split('\n')
def seg(p,a,b):
    L=lines(p)[a-1:b]; s='\n'.join(L)+'\n'; return len(L), len(s.encode('utf-8'))
HEAD=re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([0-9A-Za-z]+:[^}]+)\}\}')
def stmts(p,a=1,b=None):
    L=lines(p); b=b or len(L); out=[]
    for i in range(a-1,b):
        m=HEAD.match(L[i]); 
        if m and not L[i].startswith('**'+m.group(1)+' {{'+m.group(2)+'}}의 증명'): out.append(m.group(2))
    return out
def file_stats(p):
    b=rb(p); L=b.decode('utf-8').split('\n'); n=len(L)-(1 if L and L[-1]=='' else 0)
    return n,len(b),b.count(b'\r')
DEC=re.compile(r'(?<![\w.])\d+\.\d+(?![\w.])')
def decimals(p,a=1,b=None):
    L=lines(p); b=b or len(L); txt='\n'.join(L[a-1:b])
    # 라벨·절 번호(예: 9.4절, 10.1절, (9.2) 식 번호)는 뺀다
    txt=re.sub(r'\d+\.\d+절','',txt); txt=re.sub(r'\(\d+\.\d+\)','',txt); txt=re.sub(r'D\.\{\{[^}]+\}\}','',txt)
    vals=DEC.findall(txt); return len(vals), len(set(vals))
print("## 장 파일")
for p in ['장9.md','장10.md','부록D_장9.md','부록D_장10.md']:
    n,b,cr=file_stats(p); print(f"{p}: 행 {n}, 바이트 {b}, CR {cr}, 진술 {len(stmts(p))}, 십진 상수(출현/서로 다른) {decimals(p)}")
print("  장9 진술:",stmts('장9.md')); print("  장10 진술:",stmts('장10.md'))
print("\n## 배타 영역(앞 장) — 9장과 함께 지울 수 있는 것")
for p,a,b,name in [('장2.md',815,850,'2:old-2-38(머리 합 정의 문단 제외)'),('장2.md',845,850,'머리 합 P_t(k) 정의 문단(남겨야 함; 6:cor-L이 씀)'),('장2.md',851,882,'2:old-2-39'),('장2.md',942,953,'2:old-2-41'),('장6.md',247,264,'6:increment-bounds'),('장6.md',711,728,'6:D-bound(+뒤 문단)'),('장6.md',697,710,'6:cor-L(공유; 참고)'),('장7B.md',399,411,'7:old-6-22'),('장7B.md',413,419,'7.8절 남은 것(재서술)')]:
    n,by=seg(p,a,b); print(f"  {name}: {p} {a}-{b}, 행 {n}, 바이트 {by}, 십진 {decimals(p,a,b)}")
print("\n## 배타 영역(앞 장) — 10장과 함께 지울 수 있는 것")
for p,a,b,name in [('장2.md',1004,1017,'2:old-2-46'),('장6.md',265,421,'6.3절 전체(6:old-8-13·chain-recursion·same-kernel·stay-margin-identity·lemma-omega·lemma-phi)'),('장6.md',657,682,'6:old-8-12(+뒤 문단)'),('장7B.md',246,248,'7:qstar-implies-wlflat')]:
    n,by=seg(p,a,b); print(f"  {name}: {p} {a}-{b}, 행 {n}, 바이트 {by}, 십진 {decimals(p,a,b)}, 진술 {stmts(p,a,b)}")
print("\n## 표지 셈")
for p in ['장9.md','장10.md']:
    t='\n'.join(lines(p))
    print(f"{p}: 작성자 판단 {t.count('작성자 판단')}, 칼표 † {t.count('†')}, 계산 보조 {t.count('계산 보조')}, 문헌 인용 {t.count('문헌 인용')}, 귀납 {t.count('귀납')}")
print("\n## 부록·장부 행")
import collections
for p in ['부록A.md','부록C.md','부록B.md']:
    t=lines(p); c9=sum(1 for l in t if '{{9:' in l); c10=sum(1 for l in t if '{{10:' in l)
    d9=sum(1 for l in t if re.search(r'\|\s*9\.\d\s*\|',l)); d10=sum(1 for l in t if re.search(r'\|\s*10\.\d\s*\|',l))
    print(f"{p}: {{9: 행 {c9}, {{10: 행 {c10}, 정의절 9.x 행 {d9}, 정의절 10.x 행 {d10}")
t=(ROOT/'장부_v2.md').read_text(encoding='utf-8').split('\n')
print(f"장부_v2.md: {{9: 행 {sum(1 for l in t if '{{9:' in l)}, {{10: 행 {sum(1 for l in t if '{{10:' in l)}, 정의절 9.x {sum(1 for l in t if re.search(r'\|\s*9\.\d\s*\|',l))}, 정의절 10.x {sum(1 for l in t if re.search(r'\|\s*10\.\d\s*\|',l))}")
for p in ['장1.md','장11.md','장3.md','장6.md','장7A.md','장7B.md','장8.md','장2.md','장5A.md']:
    t=lines(p); print(f"{p}: '9장' {sum(l.count('9장') for l in t)}, '10장' {sum(l.count('10장') for l in t)}, '첫째 증명' {sum(l.count('첫째 증명') for l in t)}, '둘째 증명' {sum(l.count('둘째 증명') for l in t)}, '두 증명' {sum(l.count('두 증명') for l in t)}, LRP {sum(l.count('LRP') for l in t)}, FLQ {sum(l.count('FLQ') for l in t)}, Qstar2 {sum(l.count('Q^' + chr(92) + 'star_2') for l in t)}")
