# K12: D.newton-m170 식의 Nw_{r,d}를 r<=14에서 정확 정수로 만들어 전진 차분 비음성·차수·영 차분 확인; inverse-renewal 정규화 재귀와의 일치
from fractions import Fraction as F
from math import comb, factorial
from functools import lru_cache
def p(m): return (m+1)**(m-1) if m>=1 else 1
@lru_cache(None)
def Gam(d,y,n):
    if d==0: return F(1)
    return comb(n,d)*p(d)+y*sum(comb(n-d+j,j)*p(j)*Gam(d-1-j,y,n) for j in range(d))
def sd(d,y,n):
    hg=lambda yy: yy*Gam(d,yy,n)
    return hg(y+1)-2*hg(y)+hg(y-1)
e15=sum(F(1,factorial(j)) for j in range(16))
def Nw(r,d,nv):
    k=r+1+nv; n=k+r
    return factorial(15)*(2*e15*k*k*(k+1)*Gam(r-1,k+2,n)*sd(d,k,n)-(2*k*k+5*k+4)*Gam(r,k-1,n)*sd(d,k+1,n))
allok=True; maxdeg={}
for r in range(2,15):
    for d in range(1,r):
        vals=[Nw(r,d,nv) for nv in range(0,2*r+3+4)]
        assert all(v.denominator==1 for v in vals)
        diffs=[]; cur=vals[:]
        for i in range(len(vals)):
            diffs.append(cur[0]); cur=[cur[j+1]-cur[j] for j in range(len(cur)-1)]
        if not (vals[0]>0 and all(x>=0 for x in diffs[:2*r+3])): allok=False; print("FAIL",r,d)
        nz=max(i for i,x in enumerate(diffs) if x!=0)
        maxdeg[(r,d)]=nz
        if nz>r+d+1: print("degree exceeds r+d+1:",r,d,nz)
print("all Newton checks r<=14 pass:",allok, " max over (r,d) of deg-(r+d+1):",max(maxdeg[k]-(k[0]+k[1]+1) for k in maxdeg))
# inverse-renewal normalized recursion
def tw(j): return F(1) if j==1 else F((j-1)**(j-1),factorial(j))
def gn_seq(D,y,n):
    g=[F(1)]
    for d in range(1,D+1):
        g.append((1+F(y,n-d+1))*g[d-1]+sum(tw(j)*g[d-j] for j in range(2,d+1)))
    return g
ok=True
for (y,n) in ((3,10),(7,12),(F(5,2),9)):
    g=gn_seq(6,y,n)
    for d in range(0,7):
        ff=F(1)
        for i in range(d): ff*=(n-i)
        if g[d]*ff!=Gam(d,y,n): ok=False
print("inverse-renewal recursion gives Gamma_d/(n)_d:",ok)
