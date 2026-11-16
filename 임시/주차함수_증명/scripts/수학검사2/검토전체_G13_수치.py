# -*- coding: utf-8 -*-
"""G13 수치 검산: 부록 D 7A/7B/9 항목의 셈 몇 가지. 읽기 전용. python -I 로 실행."""
from fractions import Fraction as F
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("== n_M(k)/k^{3/2}: 841, 2000")
for k, nM in [(841,20507),(2000,73032)]:
    r = nM / k**1.5
    print(k, nM, f"{r:.6f}", "k^1.5=", k**1.5)

print("== 10^21*400^10 vs 17^21*123^10")
L = 10**21*400**10; R = 17**21*123**10
print(f"L={L:.6e} R={R:.6e} L>R: {L>R}")

print("== column-certification-k500 비교 수")
def cnt(k1,k2):
    dd=0; bd=0
    for k in range(k1,k2+1):
        B = -(-k*k//4)
        dd += 2*B-(2*k+1)+1
        bd += 2*B-B+1
    return dd,bd
print("121-160:", cnt(121,160), " 161-500:", cnt(161,500))

print("== m1-column-reading 쌍 수")
tot=0; tot2=0
for k in range(3132,19404):
    lo = k + int(math.floor(0.75*k**(2/3)))
    lo2 = k + int(math.floor(k**(2/3)))
    hi = min(2*k-1,20000)
    tot += max(0,hi-lo+1); tot2 += max(0,hi-lo2+1)
print("0.75:", tot, " 1.0:", tot2)
# 전체 위치 수: 행 5..20000, 위치 ceil((n-1)/2) .. n-3
pos = sum(max(0,(n-3) - (-(-(n-1)//2)) + 1) for n in range(5,20001))
print("positions:", pos)
# (3288-3136)/3136^(2/3)
print("(3288-3136)/3136^(2/3) =", (3288-3136)/3136**(2/3))

print("== pair-check-10000 경우 수 q+q'+j<=50, q,q'>=1, j>=0")
c=sum(1 for q in range(1,51) for qp in range(1,51) for j in range(0,51) if q+qp+j<=50)
c19=sum(1 for q in range(1,20) for qp in range(1,20) for j in range(0,20) if q+qp+j<=19)
print(c, c19)

print("== seed: 검사 구간")
for k,kk,dd in [(2,8,13),(8,24,43),(34,68,189),(120,240,709)]:
    print(k, kk, dd+k+1-1)

print("== four-families eps0")
for k0 in [6668,8065,9551,9705]:
    print(k0, math.floor(2**(2/3)*(k0+1)**(2/3)))

print("== self-consistent j*(varsigma)")
def jstar(s):
    m=0
    while (1+1/(m+2))**(m+1) < s: m+=1
    return m  # max m with e^{g(m+1)}<s, e^{g(m+1)} = a_{m+1}/a_m = (1+1/(m+1))^m
# careful: e^{g(m+1)} = a°_{m+1}/a°_m = ((m+2)^m/(m+1)!)/((m+1)^{m-1}/m!) = (m+2)^m/(m+1)^m
def jstar2(s):
    m=0; best=-1
    while True:
        v=((m+2)/(m+1))**m
        if v<s: best=m
        else: break
        m+=1
    return best
for s in [F(267,100),F(27,10),F(271,100)]:
    js=jstar2(float(s))
    # k_R
    from math import factorial
    a = F((js+2)**js, factorial(js+1))  # a°_{js+1} = (js+2)^{js}/(js+1)!
    kR = max(2*js+2, math.ceil(s**(js+2)/a))
    print(float(s), js, kR)

print("== AR: J3,J4 at 6668")
k=6668
print((k/(2*k+1))**2.5*(1-3/k**0.5), (k/(2*k+1))**2.5*(1-3/(k-1)**0.5))
d=6.62/math.sqrt(6668); print("band req", (1+d/2)/(1-d/2), "bulk req", 1+1.676*d/(2-d)+0.676*(0.8825/k**0.5+0.72/k+41.2*(2/(0.48*k-102))**1.5))

print("== band-LP k=48966 Upsilon")
k=48966
u=3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print((k-1)*u/(2*k+1), 0.05*(1-1/k)**103)
k=6668; print("0.1113k=",0.1113*k)

print("== stored-table j_inf")
for x in [2,2.1]:
    print(x, math.exp(-4/3*(2*math.pi)**-0.5*x**1.5))

print("== M-natural constants")
print(3*math.sqrt(2)*0.16696, 2.5-math.log(2)-math.log(0.485917))
j1=0.7998716895841891; j2=2.717199867930190
print("decrease cond", j1+j2*(0.5*math.log(6667)-1))

print("== polar: table rows sum, and V sqrt k")
print(5+90+74+103+51+48+56+61)
print("n_X(501)=", math.ceil(501**(4/3)), " n_X(2002)=", math.ceil(2002**(4/3)))
print("2e^{-5.3146*0.6996}=", 2*math.exp(-5.3146*0.6996), " 0.0821 e^{-3/25233}=", 0.0821*math.exp(-3/25233))
print("0.3^{1.5}/2=", 0.3**1.5/2)
