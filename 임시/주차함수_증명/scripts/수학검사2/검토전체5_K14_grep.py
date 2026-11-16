# -*- coding: utf-8 -*-
"""K14: 몇 가지 글자의 실제 꼴을 장 파일에서 찾는다(grep의 ^ 처리 문제를 피해 파이썬으로)."""
import re, io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r'C:\math\임시\주차함수_증명\장v2')
BS = chr(92)
def show(files, pat, width=90, maxn=6, label=None):
    print('==', label or pat)
    n = 0
    for f in files:
        for i, ln in enumerate(open(f, encoding='utf-8'), 1):
            for m in re.finditer(pat, ln):
                print(f'  {f}:{i}: …{ln[max(0,m.start()-width):m.end()+width]}…')
                n += 1
                if n >= maxn: return
    if n == 0: print('  (없음)')
show(['장6.md','장8.md','장9.md','장11.md'], BS*2 + r'mathrm\{Bor\}_\{?' + BS*2 + r'le', label='Bor_le forms')
show(['장6.md'], r'Bor\}_', label='Bor}_ in 장6', maxn=10)
show(['장6.md'], r'\(ㄷ\)', label='(ㄷ) in 장6', maxn=6, width=120)
show(sorted(glob.glob('*.md')), BS*2 + r'mathfrak a\^\{?' + BS*2 + r'circ', label='frak a circ anywhere')
show(['장7A.md'], r'자유 비', width=160, label='자유 비 7A')
show(['장5B.md'], r'mathrm\{top\}_' + BS*2 + r'pi:=', width=10, label='top_pi def')
show(['장6.md'], BS*2 + r'mathsf v\^' + BS*2 + r'prime_k:=', width=60, label='v prime def')
show(['장3.md'], BS*2 + r'ell_n', width=80, label='ell_n in 장3', maxn=4)
show(['부록A.md','부록C.md'], BS*2 + r'ell_n', width=60, label='ell_n in 부록')
show(['장7A.md'], r'n\^' + BS*2 + r'circ_k', width=60, label='n circ k 7A', maxn=3)
