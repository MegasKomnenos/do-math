# O6: 7장A 수치 재검산
from fractions import Fraction as F
from math import log, exp, e, factorial, sqrt, cosh, ceil
import mpmath as mp
mp.mp.dps = 50

# 1) 열 인증 정수 부등식
L = 10**21 * 400**10; R = 17**21 * 123**10
print("정수부등식", L > R, float(L), float(R))
print("17^21", 17**21, "123^10", 123**10)
# phi#(17/10) bound
print("(40/41)(10/17)^2.1 =", (40/41)*(10/17)**2.1)
# o_k at k=41
k=41
ok = -2*log(1-1/k)/log(1+1/k); print("o_41", ok, "2(k+1)/(k-1)", 2*(k+1)/(k-1))
print("phi' lower", 1-2.1*(10/17)**3)

# 2) t_k 정의 확인, n#_k 샘플
def t_k(k):
    j=0
    while not ((k+1)**j * k**(j+1) + (k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in [2,3,5,10,100,501]:
    print("t_k",k,t_k(k), "n#", k+(k+1)*t_k(k))

# 3) 자기일관 상계 표
def a0(m): return F((m+1)**(m-1), factorial(m)) if m>=1 else F(1)
def g_exp(m): # e^{g(m)} = a0(m)/a0(m-1)
    return a0(m)/a0(m-1)
def jstar(L):
    m=0
    while g_exp(m+1) < L: m+=1
    return m-1
def table(L, J, k0, xk_k):
    js = jstar(L)
    kR = max(2*js+2, ceil(L**(js+2)/a0(js+1)))
    E_under = sum(a0(J+i)/a0(J)*mp.e**(-i) for i in range(1, k0-js+1))
    Le = mp.mpf(L.numerator)/L.denominator/mp.e
    E_inf = Le*(1-Le**k0)/(1-Le)
    RJ = max(1/(1+E_under), 1/(1+E_inf))
    xbar = [a0(x)*L**(-(x+1)) for x in range(J)]
    qund = [max(F(0), 1-sum(a0(j)*L**(-(j+1)) for j in range(x))) for x in range(J)]
    Xi = sum(max(mp.mpf(0), mp.mpf(xb.numerator)/xb.denominator - RJ*mp.mpf(q.numerator)/q.denominator) for xb,q in zip(xbar,qund))
    xk = mp.mpf(xk_k)/(xk_k+1); xk = xk**(xk_k-1)
    Xik = sum(max(mp.mpf(0), mp.mpf(a0(x).numerator)/a0(x).denominator*xk*mp.mpf(L.numerator)/L.denominator**1*(mp.mpf(L.denominator)/L.numerator)**x/ (mp.mpf(L.numerator)/L.denominator) *1 - RJ*mp.mpf(qund[x].numerator)/qund[x].denominator) for x in range(J))
    # simpler recompute Xik
    Lm = mp.mpf(L.numerator)/L.denominator
    Xik = sum(max(mp.mpf(0), mp.mpf(a0(x).numerator)/a0(x).denominator*xk*Lm**(-x) - RJ*mp.mpf(qund[x].numerator)/qund[x].denominator) for x in range(J))
    A0 = xk + Xik/(Lm*(1-Xi)); B0 = RJ*(1+Xik/(1-Xi))
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} RJ={mp.nstr(RJ,10)} Xi={mp.nstr(Xi,8)} Xik={mp.nstr(Xik,8)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)}")
    return A0,B0
res=[]
for L,J,k0,y in [(F(267,100),25,501,F(13,100)),(F(27,10),70,1855,F(2,25)),(F(271,100),100,6098,F(11,200))]:
    A0,B0 = table(L,J,k0,k0)
    xi = mp.mpf(1)/k0; ym = mp.mpf(y.numerator)/y.denominator
    val = (ym-xi)*(ym-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*ym)
    vert = (3*xi+xi**2)/2+(1+xi)**2*B0/2
    print("  cor-S' value", mp.nstr(val,6), "vertex/k^2", mp.nstr(vert,6), "<= y", vert<=ym)
# with table rounded values
for k0,y,A0,B0 in [(501,0.13,1.4708,0.098505),(1855,0.08,2.5335,0.060259),(6098,0.055,2.7354,0.0422)]:
    xi=1/k0; print("  rounded", (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y))

# 4) polar-N 수치
k=2001; n=2*k**1.5+1
print("2k^1.5+1 at 2001:", n, "0.3476k^2:", 0.3476*k*k, "2/sqrt k", 2/sqrt(k))
xk = (k/(k+1))**(k-1); print("x_2001", xk, "e^{-1+2/(k+1)}", exp(-1+2/(k+1)))
print("0.955*0.991*0.3678", 0.955*0.991*0.3678, "e^-0.0448", exp(-0.0448))
y=0.0448; print("cosh rem ratio", (2*(cosh(y)-1)-y*y)/(y*y))
# 5) polar-W hand inequality
k=10**7; print("(1+0.91/sqrt k)^3*8", 8*(1+0.91/sqrt(k))**3, "8.344/sqrt k", 8.344/sqrt(k))
print("(k+2sqrt k)/(k+1)", (k+2*sqrt(k))/(k+1))
# 6) rho_2 = log 2 check: C_2 = e^x -1
print("rho2", log(2))
# 7) Ren decreasing, 1/(1-T) coefficients m^m/m!
# 8) riccati counterexample (k,z,n)=(3,1,2)
print("LHS 4 RHS 5 claim: direct: perms of 2: (1,2): h=(1,2), H1=1, w=2 ; (2,1): h=(1,1), H1=2, w=1 ->", 2*1+1*2)
