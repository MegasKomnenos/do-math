# -*- coding: utf-8 -*-
# 5절 셋째 열(장이 처음 정의하는 낱말)을 3절 표의 「첫 정의 절」과 견준다. 어긋난 후보만 찍는다(원문은 따로 연다).
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
rows3 = [(ln,c) for ln,c in t12.table(452,688) if len(c)>=3]
print('3절 행 수', len(rows3), '열 수 분포', sorted(set(len(c) for _,c in rows3)))
exp = {}
for ln,c in rows3:
    word, sec = c[0], c[2]
    chs = [int(x) for x in re.findall(r'(?<![\d.])(\d+)\.\d', sec)]
    ch = min(chs) if chs else None
    exp.setdefault(ch, []).append((ln, word, sec))
sec5 = {int(c[0]): [w.strip() for w in c[2].split(';')] for ln,c in t12.table(1191,1200)}
for ch in range(1,11):
    e = [w for _,w,_ in exp.get(ch,[])]
    a = sec5[ch]
    print('장',ch,'5절',len(a),'3절',len(e))
    for w in a:
        if w not in e: print('   5절에만:', w, [ (ln,s[:60]) for ln,ww,s in rows3_flat if ww==w] if False else '')
    for ln,w,s in exp.get(ch,[]):
        if w not in a: print('   3절에만: %d행 [%s] 첫 정의 절 [%s]'%(ln,w,s[:80]))
print('장을 못 정한 3절 행:')
for ln,w,s in exp.get(None,[]): print('   %d행 [%s] [%s]'%(ln,w,s[:60]))
