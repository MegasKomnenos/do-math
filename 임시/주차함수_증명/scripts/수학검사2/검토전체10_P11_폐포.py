# -*- coding: utf-8 -*-
"""한 진술의 블록(머리+진술+증명)이 인용하는 라벨의 추이적 폐포(지정 장 범위)를 구한다."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
blocks = {}
for f in sorted(glob.glob(os.path.join(BASE,'장*.md'))):
    lines = open(f,encoding='utf-8').read().split('\n')
    cur=None
    for ln in lines:
        h = HEAD.match(ln)
        if h: cur = h.group(2); blocks.setdefault(cur, []); 
        if re.match(r'#{2,4}\s', ln): cur=None
        if cur: blocks[cur].append(ln)
    # 별도 "X의 증명" 블록도 그 라벨에 붙임
    cur=None
    for ln in lines:
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}의 증명', ln)
        if m: cur=m.group(2)
        elif HEAD.match(ln) or re.match(r'#{2,4}\s', ln): cur=None
        if cur: blocks.setdefault(cur,[]).append(ln)
def direct(lab):
    txt='\n'.join(blocks.get(lab,[]))
    # 증명 끝(∎) 이후 뒤 문단은 제외: 마지막 ∎까지만
    j = txt.rfind('∎')
    if j>0: txt = txt[:j]
    return set(re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', txt)) - {lab}
def closure(lab, pref):
    seen=set(); st=[lab]
    while st:
        x=st.pop()
        for y in direct(x):
            if y.startswith(pref) and y not in seen:
                seen.add(y); st.append(y)
    return seen
for lab in sys.argv[1:]:
    pref = sys.argv[1].split(':')[0]+':' if False else ''
    print(f"\n[{lab}] 직접:", sorted(direct(lab)))
    print(f"[{lab}] 6장 안 폐포:", sorted(closure(lab,'6:')))
