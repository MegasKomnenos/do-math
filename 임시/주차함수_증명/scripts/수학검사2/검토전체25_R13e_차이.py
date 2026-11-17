# -*- coding: utf-8 -*-
# 두 결과 파일(여유대장 출력)의 차이를 찍는다: 새로 생긴 줄과 건수가 바뀐 줄.
import io,re,sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def key(l): return l.split(': ')[0]
a={key(l):l for l in io.open(sys.argv[1],encoding='utf-8')}
b={key(l):l for l in io.open(sys.argv[2],encoding='utf-8')}
for k in b:
    if k not in a: print('NEW '+b[k][:330].rstrip())
    else:
        na=int(re.search(r': (\d+)건',a[k]).group(1)); nb=int(re.search(r': (\d+)건',b[k]).group(1))
        if nb!=na: print('CHG %d→%d %s'%(na,nb,b[k][:300].rstrip()))
