# -*- coding: utf-8 -*-
"""X1 C6 검산(한정: 전달행렬이 G1 틀에 드는지의 사실 확인용): nf 합성 법칙, W_n(γ,γ') 분해식,
ℓ_r(d)의 상하계 2d^r/r ≤ ℓ_r ≤ 5d^r/(2r), 전달행렬 0·1·2차 계수 b_j,a_j,c_j."""
from fractions import Fraction as Fr
import sympy as sp
from math import factorial
out=[]
def log(s): out.append(s); print(s)
def nf(n,d):
    # e^d n!/(n-d)! (n-d)^{n-d-2}/n^{n-2} — e^d는 기호로 분리: nf = e^d * r(n,d)
    return Fr(factorial(n),factorial(n-d))*Fr((n-d)**(n-d-2) if n-d-2>=0 else 1, (n-d)**(2-(n-d)) if n-d-2<0 else 1)/Fr(n**(n-2))
def r_nf(n,d):
    return sp.Rational(factorial(n),factorial(n-d))*sp.Integer(n-d)**(n-d-2)/sp.Integer(n)**(n-2)
ok=True
for n in range(4,14):
    for a in range(0,n):
        for b in range(0,n-a):
            if sp.simplify(r_nf(n,a+b)-r_nf(n,a)*r_nf(n-a,b))!=0: ok=False
log(f"[C6 nf 합성] nf(n,a+b)=nf(n,a)nf(n-a,b) (e^d 인자 분리 뒤 유리수부, n<=13): {ok}")
# W_n(γ) = nf(n, d_j -1) ∏_{i<j} n/(n+1-d_i); 첫 간격 분리 식
def W(n,gam):
    d=0; prod=sp.Integer(1); ds=[]
    for g in gam: d+=g; ds.append(d)
    val=sp.exp(ds[-1]-1)*r_nf(n,ds[-1]-1)
    for di in ds[:-1]: val*=sp.Rational(n,n+1-di)
    return val
ok=True
for n in (12,15,20):
    for gam in ((2,3),(1,4,2),(3,1,1,2),(2,2,2)):
        j=len(gam); g=gam[0]; rest=gam[1:]
        lhs=W(n,gam); rhs=sp.exp(g)*r_nf(n,g)*sp.Rational(n,n-g+1)*sp.Rational(n,n-g)**(j-2)*W(n-g,rest)
        if sp.simplify(lhs-rhs)!=0: ok=False; log(f"  불일치 n={n} γ={gam}")
log(f"[C6 W 분해] W_n(γ,γ')=nf(n,γ)·n/(n-γ+1)·(n/(n-γ))^{{j-2}}·W_{{n-γ}}(γ'): {ok}")
# ℓ_r(d) 상하계
ok=True
for r in range(1,9):
    for d in range(0,61):
        l=Fr(1,r)*(Fr(d**(r+1),r+1)+2*d**r-sum(u**r for u in range(d)))
        if not (Fr(2*d**r,r)<=l<=Fr(5*d**r,2*r)): ok=False
log(f"[C6 ℓ_r 상하계] 2d^r/r ≤ ℓ_r(d) ≤ 5d^r/(2r), r<=8, d<=60: {ok}  (원고 5.27(가)의 하계는 0; 강화된 하계가 (1-d/n)^-2 ≤ nf를 준다)")
# 전달행렬: K_{j,γ}(ε)=nf(1/ε,γ)(1-(γ-1)ε)^{-1}(1-γε)^{-(j-2)} 의 ε-전개; M_{j,sr}=[ε^{s-r}]K(1-γε)^{-r}
eps,gam,jj=sp.symbols('epsilon gamma j')
def lognf_series(gam,order):
    # log nf(1/ε,γ) = Σ ℓ_r(γ) ε^r
    return sum(sp.Rational(1,r)*(sp.Rational(1,r+1)*gam**(r+1)+2*gam**r-sum(sp.Integer(u)**r for u in range(0,100)) )*eps**r for r in range(1,order+1)) if False else None
def ell(r,g): return sp.Rational(1,r)*(sp.Rational(g**(r+1),r+1)+2*g**r-sum(u**r for u in range(g)))
ok=True
for g in range(1,5):
    for j in range(2,6):
        K=sp.exp(sum(ell(r,g)*eps**r for r in range(1,4)))*(1-(g-1)*eps)**-1*(1-g*eps)**(-(j-2))
        Ks=sp.series(K,eps,0,3).removeO()
        M10=sp.expand(Ks).coeff(eps,1)           # M_{j,10}=[ε^1]K
        M20=sp.expand(Ks).coeff(eps,2)           # M_{j,20}=[ε^2]K
        M21=sp.expand(sp.series(K*(1-g*eps)**-1,eps,0,3).removeO()).coeff(eps,1)  # [ε^{1}]K(1-γε)^{-1}
        b=(j+sp.Rational(3,2))*g-1; a=(j+sp.Rational(5,2))*g-1; c=sp.Rational(1,2)*(j+sp.Rational(3,2))*(j+sp.Rational(5,2))*g**2-(j+sp.Rational(31,12))*g+1
        if not (sp.simplify(M10-b)==0 and sp.simplify(M21-a)==0 and sp.simplify(M20-c)==0): ok=False; log(f"  불일치 γ={g} j={j}: {M10},{M21},{M20} vs {b},{a},{c}")
log(f"[C6 전달행렬 0·1·2차] b_j=(j+3/2)γ-1, a_j=(j+5/2)γ-1, c_j=½(j+3/2)(j+5/2)γ²-(j+31/12)γ+1 (γ<=4, j<=5): {ok}  — 5.17(나)·5.28(가)의 계수와 같다")
log("[판단] 전달행렬은 간격 수열(지정 사슬)의 1/n 전개에 관한 정리이고 G1(용량 가중 순열·숲의 분배함수)의 특수화가 아니다 — X5(R·사슬 공식)·A3·X4의 몫.")
open("심사_X1_C6_nf_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
