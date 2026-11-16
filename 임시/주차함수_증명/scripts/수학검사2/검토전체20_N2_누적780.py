# N2 검산: n=780 누적 개수 A_{780,l} 창(l0..l1)에서 로그오목 실패 위치와 상대 크기; n=779도 같은 창
import sys
from math import comb
from fractions import Fraction
n=780; l0=int(sys.argv[1]); l1=int(sys.argv[2])
p=[ (m+1)**(m-1) if m>=1 else 1 for m in range(n+1)]
def Arow(l):
    row=[0]*(n+1)
    for m in range(n+1):
        if m<=l+1: row[m]=p[m]
        else:
            s=0
            for t in range(1,m+1):
                s+=comb(m-1,t-1)*min(t,l+1)*row[t-1]*row[m-t]
            row[m]=s
    return row
rows={l:Arow(l) for l in range(l0-1,l1+2)}
out=[]
for nn in (779,780):
    for l in range(l0,l1+1):
        a=rows[l][nn]; am=rows[l-1][nn]; ap=rows[l+1][nn]
        diff=a*a-am*ap
        if diff<0:
            rel=Fraction(diff,a*a)
            out.append("n=%d l=%d FAIL rel=%.3e"%(nn,l,float(rel)))
    out.append("n=%d window [%d,%d] checked"%(nn,l0,l1))
open(sys.argv[3],"w").write("\n".join(out)+"\n")
