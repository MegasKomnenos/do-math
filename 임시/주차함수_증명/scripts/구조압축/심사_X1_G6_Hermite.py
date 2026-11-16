# -*- coding: utf-8 -*-
"""X1 G6 검산: Gauss형 계수 비 M_i/M_0 (i=2,4)를 Hermite 수의 점화식으로 d=He_n/He_{n-1}-n의 일차 분수식으로 적고,
7.50(라)의 U_i, V_i (ν 기호)와 4.9의 (4.9)·M_4/M_0 두 경우(ν=-1,0)가 같은 식임을 기호로 확인."""
import sympy as sp
n,y,d,k,nu,N=sp.symbols('n y d k nu N')
out=[]
def log(s): out.append(s); print(s)
# exp(N Y - y Y^2/2)=sum He_j Y^j/j!  →  He_{j+1} = N He_j - y j He_{j-1}
# M_i ∝ sum_{m=0}^{i+1} (-1)^m C(i+1,m) He_{n-m}/(n-m)!  (계수 [Y^n](1-Y)^{i+1} B(Y), 공통 인자 n!/p_n e^{-y/2})
# He_{n-m}을 He_n, He_{n-1}로: 역방향 He_{j-1} = (N He_j - He_{j+1})/(y j)
He_n, He_nm1 = sp.symbols('He_n He_nm1')
He={0:He_n,1:He_nm1}   # He[m] := He_{n-m}
for m in range(2,6):
    j=n-m+1  # He_{j-1}=(N He_j - He_{j+1})/(y j)
    He[m]=sp.simplify((N*He[m-1]-He[m-2])/(y*(n-m+1)))
def Mratio(i):
    num=sum((-1)**m*sp.binomial(i+1,m)*He[m]*sp.rf(n-m+1,m) for m in range(i+2))  # /(n-m)! → 곱 n!/(n-m)! = (n-m+1)_m
    den=sum((-1)**m*sp.binomial(1,m)*He[m]*sp.rf(n-m+1,m) for m in range(2))
    r=sp.simplify((num/den).subs({He_n:(n+d)*He_nm1}).subs(N,n+y+1))
    return sp.simplify(r)
r2=Mratio(2); r4=Mratio(4)
# 4.9의 (4.9)
eq49=1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d)
log(f"[4.9 (4.9)] M2/M0 == 1-2n/y+n(n+1)/y^2-n(n+1)/(y^2 d): {sp.simplify(r2-eq49)==0}")
# 7.50(라): y=k, n=2k+ν
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
sub={y:k,n:2*k+nu}
log(f"[7.50(라)] M2/M0 == U2 - V2/d (ν 기호): {sp.simplify(r2.subs(sub)-(U2-V2/d))==0}")
log(f"[7.50(라)] M4/M0 == U4 - V4/d (ν 기호): {sp.simplify(r4.subs(sub)-(U4-V4/d))==0}")
# 4.9의 M4/M0 두 경우
c0=1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/d
cm1=1+12/k-6/k**2-(4+26/k-14/k**2)/d
log(f"[4.9 M4/M0 ν=0] == 7.50(라) at ν=0: {sp.simplify((U4-V4/d).subs(nu,0)-c0)==0}; ν=-1: {sp.simplify((U4-V4/d).subs(nu,-1)-cm1)==0}")
# 4.9 둘째 단계의 k-계수 주장: P=d[(n-y)^2+n]-n(n+1), d 중심값 4-(26+4ν+8θ)/k+(506+97ν+5ν^2+(168+16ν)θ+12θ^2)/k^2, y=k-θ
th=sp.symbols('theta')
dc=4-(26+4*nu+8*th)/k+(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)/k**2
P=sp.expand((dc*((2*k+nu-(k-th))**2+2*k+nu)-(2*k+nu)*(2*k+nu+1)))
Pk=sp.Poly(sp.expand(P*k**2),k)
log(f"[4.9/7.50(마)] P·k^2 의 k^4,k^3 계수: {Pk.coeff_monomial(k**4)}, {sp.factor(Pk.coeff_monomial(k**3))} (주장: k^2 계수 0, k 계수 -20, ν·θ 무관)")
# 7.50(가): N/k>=3 조건 N=3k+ν+1-θ: ν=-1, θ∈(0,1]에서 N<3k → x<=1/(9k) 주장은 ν>=0 또는 θ=0에서만 바로 성립
log("[7.50(가) ν 범위] N/k = 3+(ν+1-θ)/k ≥ 3 ⇔ θ ≤ ν+1 : ν=-1에서는 θ=0(y=k)에서만 성립 — 4.8의 조건 x≤1.12e-5는 4.9 쪽에서 따로 확인됨(4.8(라))")
open("심사_X1_G6_Hermite_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
