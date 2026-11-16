# Q12: D.tail-T1-partAB (A)의 tm_{r-1}(rho_r)와 Pc(k_r)/sqrt r 를 배정밀도로 따라 셈 (정리 suff-cond(마)의 Pc, 보조정리 lemma-L의 꼴)
from math import sqrt, pi, ceil, exp, log
def tm(r,rho):
    # weights (j+1) rho^j bt_j, bt_j=prod_{i<=j}(1-i/r)
    w=1.0; num=0.0; den=0.0; j=0
    while True:
        num+=j*w; den+=w
        if j>=r-1: break
        w*= rho*(j+2)/(j+1)*(r-1-j)/r
        j+=1
        if w<1e-300: break
    return num/den
def Pc(r,eb):
    k=ceil(r**1.5+8*r)
    return k*(1/(2*r)-1/(3*r*r))-2.5+2*eb*(1-1/k)-k/(k-1)*(1+sqrt(3*pi*(r-1)/2))
mn=None
for r in range(171,10000):
    k=ceil(r**1.5+8*r); rho=k/(k+r)
    v=Pc(r,tm(r,rho))/sqrt(r)
    if mn is None or v<mn[0]: mn=(v,r)
    if r in (171,172,500,1000,5000,9999): print("r",r,"tm/sqrt r",tm(r,rho)/sqrt(r),"Pc/sqrt r",v)
print("min Pc/sqrt r over 171..9999:",mn)
for r in (10**4,2*10**4,10**5):
    print("r",r,"tm_{r-1}(e^{-1/sqrt r})/sqrt r =",tm(r,exp(-1/sqrt(r)))/sqrt(r))
