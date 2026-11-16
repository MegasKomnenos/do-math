# -*- coding: utf-8 -*-
"""두 증명(9:old-7-46, 10:old-8-37)의 전체 추이적 폐포를 구해 11.3 표의 공유/고유 구분을 검사한다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
blocks = {}; after = {}
for f in sorted(glob.glob(os.path.join(BASE,'장*.md'))):
    lines = open(f,encoding='utf-8').read().split('\n')
    cur=None
    for ln in lines:
        h = HEAD.match(ln)
        if h: cur = h.group(2); blocks.setdefault(cur, [])
        elif re.match(r'#{2,4}\s', ln): cur=None
        if cur: blocks[cur].append(ln)
    cur=None
    for ln in lines:
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}의 증명', ln)
        if m: cur=m.group(2)
        elif HEAD.match(ln) or re.match(r'#{2,4}\s', ln): cur=None
        if cur: blocks.setdefault(cur,[]).append(ln)
def direct(lab):
    txt='\n'.join(blocks.get(lab,[]))
    j = txt.rfind('∎')
    core = txt[:j] if j>0 else txt
    return set(re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', core)) - {lab}
def closure(lab):
    seen=set(); st=[lab]; parent={}
    while st:
        x=st.pop()
        for y in direct(x):
            if y not in seen and not y.startswith('D:'):
                seen.add(y); parent[y]=x; st.append(y)
    return seen, parent
C9, P9 = closure('9:old-7-46'); C10, P10 = closure('10:old-8-37')
print("첫째 증명 폐포 크기:", len(C9), " 둘째 증명 폐포 크기:", len(C10))
ch11 = open(os.path.join(BASE,'장11.md'),encoding='utf-8').read()
i0 = ch11.index('**공유 입력.**'); i1 = ch11.index('**첫째 증명의 고유 입력.**'); i2 = ch11.index('**둘째 증명의 고유 입력.**'); i3 = ch11.index('### 11.4')
def labs(s): return re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', s)
def rows(seg):
    out=[]
    for ln in seg.split('\n'):
        if ln.startswith('| ') and not ln.startswith('| 입력') and not ln.startswith('|---'):
            c=[x.strip() for x in ln.strip().strip('|').split(' | ')]; out.append(c)
    return out
shared = rows(ch11[i0:i1]); uniq1 = rows(ch11[i1:i2]); uniq2 = rows(ch11[i2:i3])
def chain(lab, P):
    s=[lab]
    while s[-1] in P: s.append(P[s[-1]])
    return ' <- '.join(s)
print("\n=== 공유 입력 행의 입력 라벨이 두 폐포에 모두 드는가 ===")
for c in shared:
    for l in labs(c[0]):
        a, b = l in C9, l in C10
        if not (a and b): print(f"  {l}: 첫째 {a}, 둘째 {b}   [{c[0][:40]}]")
print("\n=== 첫째 고유 입력이 둘째 폐포에 드는가(들면 문제) ===")
for c in uniq1:
    for l in labs(c[0]):
        if l in C10: print(f"  ** {l} 둘째 폐포에 있음: {chain(l,P10)}")
        if l not in C9: print(f"  (첫째 폐포에 없음) {l}")
print("\n=== 둘째 고유 입력이 첫째 폐포에 드는가(들면 문제) ===")
for c in uniq2:
    for l in labs(c[0]):
        if l in C9: print(f"  ** {l} 첫째 폐포에 있음: {chain(l,P9)}")
        if l not in C10: print(f"  (둘째 폐포에 없음) {l}")
# 계산 진술 검사
heads = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체10_P11_heads.json",encoding='utf-8'))['heads']
calc = {l for l,h in heads.items() if '계산' in h['rest']}
listed_calc = set(labs(' '.join(c[1] for c in shared+uniq1+uniq2)))
print("\n=== 폐포 안의 계산 진술 가운데 세 표의 계산 열에 없는 것 ===")
for l in sorted((C9|C10)&calc):
    if l not in listed_calc: print("  **", l, "첫째" if l in C9 else "", "둘째" if l in C10 else "", chain(l, P9 if l in C9 else P10))
print("\n=== 계산 열에 적혔으나 어느 폐포에도 없는 것 ===")
for l in sorted(listed_calc):
    if l in calc and l not in C9 and l not in C10: print("  **", l)
print("\n=== 계산 열의 공유/고유 배치 검사 ===")
for c in shared:
    for l in labs(c[1]):
        if l in calc and not (l in C9 and l in C10): print(f"  공유 표 계산 열 {l}: 첫째 {l in C9}, 둘째 {l in C10}")
for c in uniq1:
    for l in labs(c[1]):
        if l in calc and l in C10: print(f"  ** 첫째 고유 표 계산 열 {l}이 둘째 폐포에 있음: {chain(l,P10)}")
for c in uniq2:
    for l in labs(c[1]):
        if l in calc and l in C9: print(f"  ** 둘째 고유 표 계산 열 {l}이 첫째 폐포에 있음: {chain(l,P9)}")
json.dump(dict(C9=sorted(C9),C10=sorted(C10),P9=P9,P10=P10), open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체10_P11_closure.json",'w',encoding='utf-8'), ensure_ascii=False, indent=1)
