# -*- coding: utf-8 -*-
# 쓰임: python -I 보기.py <파일> <행|행-행|all> <고정 문자열> [너비]
# 파일의 그 행(들)에서 고정 문자열이 나오는 자리마다 앞뒤 [너비]자를 찍는다. 문자열이 '-'이면 행 전체(너비로 자름).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
f, rng, needle = sys.argv[1], sys.argv[2], sys.argv[3]
w = int(sys.argv[4]) if len(sys.argv)>4 else 120
L = io.open(f, encoding='utf-8').read().split('\n')
if rng=='all': a,b=1,len(L)
elif '-' in rng: a,b=[int(x) for x in rng.split('-')]
else: a=b=int(rng)
n=0
for i in range(a,b+1):
    s=L[i-1]
    if needle=='-':
        print('%d: %s'%(i,s[:w])); continue
    j=s.find(needle)
    while j>=0:
        n+=1
        print('%d: …%s…'%(i, s[max(0,j-w):j+len(needle)+w]))
        j=s.find(needle,j+len(needle))
if needle!='-': print('# %d건'%n)
