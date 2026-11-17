# -*- coding: utf-8 -*-
# 전체 독립 검토 22차 수리 Z5(장v2/장6.md) 검산. 실행: python -I 수리_전체22_Z5_검산.py
# 6.6절 보조정리 6:lemma-Hprime의 상수를 2.218에서 1.6781(2.9절 보조정리 2:power-sum-renewal(ㄴ)의 c_Psi 상계)로
# 바꾼 뒤의 수치를 다시 센다.
#  (1) 마지막 차 재귀(정리 2:old-2-6)로 정확히 센 A_{n,l}에서 (k+1)c_m(k) >= Low(k,rho)를 k<=44, 1<=d<=(m+1)/2 전부에서 확인.
#  (2) 방향 반올림 구간(mpmath iv, 30자리)으로 Low(10001,1.4), Low(2001,3/4), B=1.6781*2001^(-1/3), R(1/2)을 평가.
#  (3) 보조정리 6:lemma-M의 두 단조성을 격자에서 견줌(증명이 아니라 견줌).
#  (4) 명제 6:old-8-23 1단계 괄호의 1.3778^2(1+2/2001)^2/6 (R5-6).
from mpmath import mp, mpf, iv, sqrt, exp, pi
from fractions import Fraction
from math import comb
mp.dps=30
# --- exact A_{n,l}: number of parking functions of length n with max displacement <= l
def Atable(l,N):
    A=[1]
    for n in range(N):
        s=0
        for i in range(n+1):
            s+=comb(n,i)*min(i+1,l+1)*A[i]*A[n-i]
        A.append(s)
    return A
N=90
tabs={}
def A(n,l):
    if l<0: return 1 if n==0 else 0
    if l not in tabs: tabs[l]=Atable(l,N)
    return tabs[l][n]
def p(n): return (n+1)**(n-1) if n>=1 else 1
# sanity: A(n,n-1)=p(n)
assert all(A(n,n)==p(n) and A(n,max(n-1,0))==p(n) for n in range(1,12))
def Low(k,rho,c=mpf('1.6781')):
    eps=mpf(k)**(-mpf(1)/3); C2=(2*pi)**(-mpf(1)/2); br=2*sqrt(rho)-c*eps
    return C2*mpf(k)**(mpf(1)/3)*br/(1+rho*eps)*exp(-mpf(1)/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf(1.5)*exp(mpf(1)/(4*(k+1)))/(C2*br))
worst=None;cnt=0
for k in range(1,45):
    for d in range(1,k+2):
        m=k+d
        if 2*d>m+1 or m>N: continue
        cm=Fraction(A(m,k)-A(m,k-1),p(m))
        lhs=mpf((k+1)*cm.numerator)/cm.denominator
        rho=mpf(d)/mpf(k)**(mpf(2)/3)
        low=Low(k,rho)
        cnt+=1
        r=lhs/low
        if worst is None or r<worst[0]: worst=(r,k,d,lhs,low)
        assert lhs>=low,(k,d,lhs,low)
print('lemma-Hprime(new const) exact check: cases',cnt,'min ratio lhs/Low',worst)
# d=1 cases specifically
for k in (1,2,3,10,40):
    m=k+1; cm=Fraction(A(m,k)-A(m,k-1),p(m)); print(' d=1 k',k,float((k+1)*cm), float(Low(k,mpf(1)/mpf(k)**(mpf(2)/3))))
# --- interval evaluation of the constants
iv.dps=30
def Low_iv(k,rho,c):
    k=iv.mpf(k); rho=iv.mpf(rho); c=iv.mpf(c)
    eps=k**(-iv.mpf(1)/3); C2=(2*iv.pi)**(-iv.mpf(1)/2); br=2*iv.sqrt(rho)-c*eps
    return C2*k**(iv.mpf(1)/3)*br/(1+rho*eps)*iv.exp(-1/(12*(k+1)))*iv.exp(-rho**2*(1+rho*eps)**iv.mpf('1.5')*iv.exp(1/(4*(k+1)))/(C2*br))
print('Low(10001,1.4) in',Low_iv(10001,'1.4','1.6781'))
print('Low(2001,0.75) in',Low_iv(2001,'0.75','1.6781'))
eps=iv.mpf(2001)**(-iv.mpf(1)/3); B=iv.mpf('1.6781')*eps; C2=(2*iv.pi)**(-iv.mpf(1)/2)
print('B in',B)
print('R(1/2) in', 3*iv.mpf('0.25')-2*B*iv.mpf('0.5')**iv.mpf('1.5')-2*C2*iv.sqrt(iv.mpf('0.5'))+C2*B)
print('0.18581-0.30817*0.1332 =', mpf('0.18581')-mpf('0.30817')*mpf('0.1332'))
print('3*0.1332=',3*mpf('0.1332'),' C2/sqrt(.5) in', C2/iv.sqrt(iv.mpf('0.5')))
print('1.6781*4^(-1/3) in', iv.mpf('1.6781')*iv.mpf(4)**(-iv.mpf(1)/3), ' sqrt2', iv.sqrt(2))
# monotonicity spot checks of Low: (가) k increasing for rho>=1/2, (나) rho decreasing for k>=2001
import itertools
ok=True
for rho in ('0.5','0.75','1','1.4','3','10','50'):
    prev=None
    for k in (4,5,10,100,2001,10001,10**6):
        v=Low(k,mpf(rho)); 
        if prev is not None and v<prev: ok=False; print('viol (ga)',rho,k)
        prev=v
for k in (2001,5000,10001,10**6,10**9):
    prev=None
    for i in range(0,2000):
        rho=mpf('0.5')+mpf(i)/100
        v=Low(k,rho)
        if prev is not None and v>prev: ok=False; print('viol (na)',k,rho); break
        prev=v
print('monotonicity spot checks ok:',ok)
print('1.3778^2(1+2/2001)^2/6 in', iv.mpf('1.3778')**2*(1+iv.mpf(2)/2001)**2/6)
