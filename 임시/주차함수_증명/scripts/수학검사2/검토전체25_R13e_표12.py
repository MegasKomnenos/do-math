# -*- coding: utf-8 -*-
# 장부 표의 행을 열로 쪼개 글자·정의 절·쓰이는 장을 뽑는다(검산용; 지적 전에 원문 행을 다시 연다).
import sys, io
BS = chr(92)
P = '장부_v2.md'
L = io.open(P, encoding='utf-8').read().split('\n')
def split_row(s):
    # 파이프 분리(수식 $...$ 안과 `...` 안의 | 는 보존)
    cells=[]; cur=''; inm=False; i=0
    while i < len(s):
        ch=s[i]
        if ch==BS and i+1<len(s):
            cur+=s[i:i+2]; i+=2; continue
        if ch=='$': inm = not inm
        if ch=='`':
            j=s.find('`',i+1)
            if j>0:
                cur+=s[i:j+1]; i=j+1; continue
        if ch=='|' and not inm:
            cells.append(cur); cur=''
        else: cur+=ch
        i+=1
    cells.append(cur)
    return [c.strip() for c in cells[1:-1]]
def table(a,b):
    rows=[]
    for ln in range(a, b+1):
        s=L[ln-1]
        if not s.startswith('|'): continue
        rows.append((ln,split_row(s)))
    return rows
if __name__=='__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
    mode = sys.argv[1] if len(sys.argv)>1 else 'brief'
    for ln,c in table(48,288):
        if mode=='brief':
            print(ln, len(c), '|', c[0], '|', c[1], '|', c[3][:70], '|', c[4][:90])
        elif mode=='full':
            print(ln, len(c), '|', ' | '.join(c))
