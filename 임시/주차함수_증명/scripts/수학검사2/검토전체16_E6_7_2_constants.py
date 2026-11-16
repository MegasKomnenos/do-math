# E6: 7.2절 수치 검산 — 열 인증 (가)의 부등식, 정리 self-consistent-S (다)의 표, 따름정리 cor-S-prime의 세 값, t_k 몇 개
from fractions import Fraction as Fr
from math import factorial, log
import mpmath as mp
mp.mp.dps = 60

# 1. 열 인증 (가): 10^21*400^10 > 17^21*123^10 ; (40/41)(10/17)^(2.1) > 0.3
L = 10**21 * 400**10; R = 17**21 * 123**10
print("column (가):", L > R, L, R, float(L)/float(R))
print("  (40/41)(10/17)^2.1 =", mp.mpf(40)/41*(mp.mpf(10)/17)**(mp.mpf(21)/10))
print("  o_k bound 2(k+1)/(k-1) at k=41:", Fr(2*42,40))
print("  hf'(1.7) lower:", 1-2.1*(10/17)**3)

# 2. t_k
def t_k(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in (2,3,5,10,100,501): print("t_k",k,t_k(k), "n#_k", k+(k+1)*t_k(k))

# 3. 정리 S (다) 표
def a0(m): return Fr((m+1)**(m-1), factorial(m)) if m>=1 else Fr(1)
def free_ratio(m): return a0(m+1)/a0(m)   # e^{g(m+1)}
def jstar(L):
    m=0
    while free_ratio(m) < L: m+=1
    return m-1
def table(Lfr, J, k0, xk_k):
    js = jstar(Lfr)
    kR = max(2*js+2, -(-(Lfr**(js+2)/a0(js+1)).numerator // (Lfr**(js+2)/a0(js+1)).denominator))
    # E_under, E_inf with mp
    Lm = mp.mpf(Lfr.numerator)/Lfr.denominator
    Eu = mp.fsum(mp.mpf((a0(J+i)/a0(J)).numerator)/(a0(J+i)/a0(J)).denominator*mp.e**(-i) for i in range(1,k0-js+1))
    Einf = (Lm/mp.e)*(1-(Lm/mp.e)**k0)/(1-Lm/mp.e)
    RJ = max(1/(1+Eu), 1/(1+Einf))
    xk = Fr(xk_k**(xk_k-1), (xk_k+1)**(xk_k-1))
    RJm = RJ
    def q_under(kap): return max(mp.mpf(0), 1-mp.fsum(mp.mpf(a0(j).numerator)/a0(j).denominator*Lm**(-(j+1)) for j in range(kap)))
    Xi = mp.fsum(max(mp.mpf(0), mp.mpf(a0(kap).numerator)/a0(kap).denominator*Lm**(-(kap+1)) - RJm*q_under(kap)) for kap in range(J))
    xkm = mp.mpf(xk.numerator)/xk.denominator
    Xik = mp.fsum(max(mp.mpf(0), mp.mpf(a0(kap).numerator)/a0(kap).denominator*xkm*Lm**(-kap) - RJm*q_under(kap)) for kap in range(J))
    A0 = xkm + Xik/(Lm*(1-Xi)); B0 = RJm*(1+Xik/(1-Xi))
    print(f"L={Lfr} J={J} k0={k0}: j*={js} kR={kR} RJ={mp.nstr(RJ,10)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik,8)} A0={mp.nstr(A0,8)} B0={mp.nstr(B0,8)}  (Eu={mp.nstr(Eu,8)} Einf={mp.nstr(Einf,8)})")
    return A0,B0
res=[]
res.append(table(Fr(267,100),25,501,501))
res.append(table(Fr(27,10),70,1855,1855))
res.append(table(Fr(271,100),100,6098,6098))

# 4. cor-S-prime: g_S(y k^2)/k^4 at k0 with table-rounded A0,B0 and with computed ones
for (y,k0,A0t,B0t),(A0c,B0c) in zip([(Fr(13,100),501,Fr(14708,10000),Fr(98505,10**6)),(Fr(2,25),1855,Fr(25335,10000),Fr(60259,10**6)),(Fr(11,200),6098,Fr(27354,10000),Fr(422,10**4))],res):
    xi=Fr(1,k0)
    def gval(A0,B0):
        return (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    ym=mp.mpf(y.numerator)/y.denominator; xim=mp.mpf(1)/k0
    comp=(ym-xim)*(ym-2*xim-xim**2)-(1+xim)**2*(A0c*xim+B0c*ym)
    print("cor-S' k0",k0,"table-rounded:", float(gval(A0t,B0t)), " computed:", mp.nstr(comp,8))
    nv = (Fr(3*k0+1)+Fr((k0+1)**2)*B0t)/2
    print("   n_v/k^2 =", float(nv/k0**2), " y k^2 > 2k+1:", y*k0**2 > 2*k0+1)
