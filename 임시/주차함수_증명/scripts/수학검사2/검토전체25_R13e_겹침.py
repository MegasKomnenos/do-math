# -*- coding: utf-8 -*-
# 7절에서 같은 기록(둘째 칸)이 든 두 행의 셋째 칸(기록의 글자)에 같은 머리 토큰(= 앞까지)이 나오는 자리를 모은다.
# 같은 기록 글자가 두 행에서 다른 「이 글의 글자」로 맞세워졌는지 사람이 읽어 가릴 후보다.
import sys, io, re, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
def heads(cell):
    out=[]
    for tok in re.findall(r'\$([^$]+)\$', cell):
        depth=0; cur=''; parts=[]
        for ch in tok:
            if ch in '({[': depth+=1
            if ch in ')}]': depth-=1
            if ch==',' and depth==0: parts.append(cur); cur=''
            else: cur+=ch
        parts.append(cur)
        for p in parts:
            p=p.strip()
            h=re.split(r'(?<![<>=!])=(?!=)|:=', p)[0].strip()
            h=re.sub(r'\s+','',h)
            if h: out.append(h)
    return out
idx=collections.defaultdict(lambda: collections.defaultdict(list))
rows=t12.table(1243,1441)
for ln,c in rows:
    rr=set(re.findall(r'\[(r[0-9a-f]{7})\]', c[1]))
    for h in set(heads(c[2])):
        for r in rr: idx[r][h].append(ln)
full={ln:c for ln,c in rows}
seen=set()
for r in sorted(idx):
    for h,lns in sorted(idx[r].items()):
        if len(set(lns))>1:
            key=(h,tuple(sorted(set(lns))))
            if key in seen: continue
            seen.add(key)
            print('기록 글자 $%s$ — 기록 [%s] 등이 든 행 %s'%(h, r, sorted(set(lns))))
            for ln in sorted(set(lns)): print('      %d: %s'%(ln, full[ln][0][:150]))
