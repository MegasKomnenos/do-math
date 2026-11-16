# -*- coding: utf-8 -*-
"""5B 수학검사2 검산 2: 5.6절 — C_I 정의 직접 적분 vs 부록 닫힌 꼴 vs 기록 코드, arc-leading 항등식,
Dawson 상수, 보조정리 5.40의 꼬리/호 정규화(Ttilde, Otilde, arctilde) vs 본문 정의의 직접 적분."""
import sys, io, contextlib, math
import mpmath as mp
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records\r5f5cf7334317436bab893b06bcd6d0b3\evidence\producer\code"
sys.path.insert(0, REC)
with contextlib.redirect_stdout(io.StringIO()):
    import certify2 as C
import sympy as sp
from mpmath import iv
mp.mp.dps = 20
S2PI = mp.sqrt(2*mp.pi)

import numpy as _np
_X,_W = _np.polynomial.legendre.leggauss(96)
def gl(f, a, b):
    a=mp.mpf(a); b=mp.mpf(b); h=(b-a)/2; c=(a+b)/2
    return h*mp.fsum(mp.mpf(float(w))*f(c+h*mp.mpf(float(x))) for x,w in zip(_X,_W))
def D(b):  # Dawson-type D(b) = e^{-b^2/2} int_0^b e^{u^2/2} du
    return mp.sqrt(2)*mp.sqrt(mp.pi)/2*mp.exp(-b*b/2)*mp.erfi(b/mp.sqrt(2))

print("== Dawson facts ==")
sup_bD = max(b*D(b) for b in mp.linspace(0.01, 12, 2400)); print("sup rho D (grid) =", mp.nstr(sup_bD,6), " bound 1.514")
dI = max(mp.mpf(2)/3*b*D(b)+2*abs(1-b*D(b)) for b in mp.linspace(0.01, 12, 2400)); print("sup d_I (grid) =", mp.nstr(dI,6), " bound 2.04")
worst = max(abs(1-b*D(b))*b*b for b in mp.linspace(0.05, 30, 3000)); print("sup rho^2|1-rho D| (grid) =", mp.nstr(worst,6), " bound 8")
# (다) j_m identity
eta = mp.mpf('0.342')
F = lambda s: mp.sqrt(mp.pi/2)*mp.sqrt(s)/(s+1)
for m in (0,1,2):
    jm_num = mp.quad(lambda b: b**(2*m)*(1-b*D(b))*mp.exp(-eta*b*b/2), [0, mp.inf])
    jm_cl = (-2)**m*mp.diff(F, eta, m)
    print(f"j_{m}: direct={mp.nstr(jm_num,12)} closed={mp.nstr(jm_cl,12)}")

print("== arc-leading (나),(다) ==")
def BorR(b): return 2*mp.exp(b*b/2)*(1-b*D(b))
def BorR_def(b): return 2 - mp.quad(lambda s: s**-1.5*(mp.exp(s*b*b/2)-1), [0,1])
print("Bor_R^ld(1.3): identity", mp.nstr(BorR(mp.mpf('1.3')),12), "definition", mp.nstr(BorR_def(mp.mpf('1.3')),12))
def inner_D(u):
    return gl(lambda r: r*r*mp.exp((1-r*r)*u*u/2)*((1-r*r)*u*u+(1-r*r)**2*u**4/4)*BorR(r*u), 0,1)
lhs = -(1/(2*mp.pi))*(1+eta)**1.5*2*mp.quad(lambda u: u**4*mp.exp(-(1+eta)*u*u/2)*inner_D(u), [mp.mpf('1e-6'), 2, 6, 12])
YD = 4/S2PI*(1-eta)*mp.sqrt(1+eta)*eta**-3.5
print("(나) lhs =", mp.nstr(lhs,10), " Y_D =", mp.nstr(YD,10))
lhsJ = (1/(2*mp.pi))*(1+eta)**1.5*2*mp.quad(lambda u: u**3*mp.exp(-eta*u*u/2)*gl(lambda r: r*(((1+eta)-r**3)*u**3/3-r*u),0,1), [mp.mpf('1e-6'), 5, 40])
YJ = 3/(2*S2PI)*(1+eta)**2.5*eta**-3.5
print("(다) lhs =", mp.nstr(lhsJ,10), " Y_J =", mp.nstr(YJ,10))
# P(sigma) antiderivative check
sg, l = sp.symbols('sigma l', positive=True)
P = 2*sg**sp.Rational(-1,2)*(1-(1-2*sg/l)*(1-sg/l)**sp.Rational(-1,2))
print("P'(sigma) - sigma^{-3/2}((1-sigma/l)^{-3/2}-1) simplifies to:", sp.simplify(sp.diff(P,sg) - sg**sp.Rational(-3,2)*((1-sg/l)**sp.Rational(-3,2)-1)))

print("== C_I(eta): 본문 정의 직접 적분 / 부록 닫힌 꼴 / 코드 C1_closed ==")
def CI_direct(eta):
    f = lambda u: u**4*mp.exp(-eta*u*u/2)*gl(lambda r: r*r*((1-r*r)*u*u+(1-r*r)**2*u**4/4)*mp.exp(-(r*u)**2/2)*(mp.mpf(4)/3*r*r*u*u-(1+eta)*r*u**4/3), 0,1)
    return 2*mp.quad(f, [mp.mpf('1e-6'), 3, 10, 40])
def CI_app(eta):
    I = lambda i,u: gl(lambda w: w*(1-w)**i*mp.exp(-u*u*w/2), 0,1)
    t2 = 2*(1+eta)/3*mp.quad(lambda u: mp.mpf(1)/2*(u**10*I(1,u)+u**12/4*I(2,u))*mp.exp(-eta*u*u/2), [mp.mpf('1e-6'),3,10,40])
    return 8*S2PI*eta**-3*(1+eta)**-1.5 - t2
def CI_app_wrong(eta):
    I = lambda i,u: gl(lambda w: w*(1-w)**i*mp.exp(-u*u*w/2), 0,1)
    t2 = 2*(1+eta)/3*mp.quad(lambda u: mp.mpf(1)/2*(u**5*I(1,u)+u**6/4*I(2,u))*mp.exp(-eta*u*u/2), [mp.mpf('1e-6'),3,10,40])
    return 8*S2PI*eta**-3*(1+eta)**-1.5 - t2
C1 = C.C1_closed()
for e in (mp.mpf('0.342'), mp.mpf('0.09')):
    code = sp.N(C1.subs(C.s, sp.sqrt(sp.Rational(str(e)))), 15)
    print(f"eta={e}: direct={mp.nstr(CI_direct(e),10)} appendix={mp.nstr(CI_app(e),10)} code={code}  (old wrong exponents: {mp.nstr(CI_app_wrong(e),8)})")

print("== Main_D closed form vs -(2pi)^-1/2 Y_0 ==")
Y0 = 2*mp.quad(lambda u: u**4*mp.exp(-eta*u*u/2)*gl(lambda r: r*r*((1-r*r)*u*u+(1-r*r)**2*u**4/4)*2*(1-r*u*D(r*u)),0,1), [mp.mpf('1e-6'),3,10,40])
print("-(2pi)^-1/2 Y_0 =", mp.nstr(-Y0/S2PI,10), " 4(1-eta)/(1+eta) eta^-7/2 =", mp.nstr(4*(1-eta)/(1+eta)*eta**-3.5,10))
print("Y_j = 4 sum gamma_q j_{q+1}: code D_j(0) =", sp.N(C.D_j(0).subs(C.s, sp.sqrt(sp.Rational('0.342'))),12), " direct Y_0 =", mp.nstr(Y0,12))

print("== 보조정리 5.40 꼬리·호의 정규화: 코드 vs 본문 정의 직접 계산 (점 상자) ==")
s_, phi_ = mp.mpf('0.5848'), mp.mpf('1.0')
k = 1000/(s_*phi_)**6; eta = s_*s_; N1 = (1+eta)*k; Q = eta*k
print("k=", mp.nstr(k,8), "eta=", eta, "Q=", mp.nstr(Q,8))
ustar = (6/N1)**(mp.mpf(1)/3); U2 = mp.sqrt(Q/N1); u2 = mp.sqrt(Q/(2*N1))
def G(m2, sig):
    m=m2//2; return mp.fac2(2*m-1)*S2PI*sig**(-m-mp.mpf(1)/2) if m>0 else S2PI*sig**(-mp.mpf(1)/2)  # gauss-moments closed form (checked separately)
def Gr(m2, x, sig): return 2*mp.quad(lambda u: u**m2*mp.exp(-sig*u*u/2), [x, mp.inf])
S = iv.mpf([float(s_), float(s_)]); PHI = iv.mpf([float(phi_), float(phi_)])
# re-create the pieces of evaluate_box locally by calling it and reading XH; easier: replicate formulas
res = C.evaluate_box(float(s_), float(s_), float(phi_), float(phi_))
# Ttilde / Otilde / arctilde are inner functions; recompute via a tiny shim: copy code lines
import types
src = open(REC + r"\certify2.py", encoding='utf-8').read()
# extract inner definitions by executing evaluate_box body up to arct via exec of a modified copy
start = src.index("def evaluate_box"); body = src[start:src.index("    It_lo = {rr:")]
body = body.replace("def evaluate_box(s_lo, s_hi, phi_lo, phi_hi):", "def _inner(s_lo, s_hi, phi_lo, phi_hi):") + "    return Ttilde, Otilde, arctilde, XH\n"
ns = dict(vars(C)); exec(body, ns); Tt, Ot, At, XH = ns['_inner'](float(s_), float(s_), float(phi_), float(phi_))
print("ex_H code =", XH, " direct Q ustar^2/2 =", mp.nstr(Q*ustar**2/2,10))
for j in (0,1,2):
    rr = 2*j
    norm = N1/3*G(rr+4, Q)
    Tdirect = Gr(rr+4, ustar, Q)/G(rr+4, Q)
    O = (Gr(rr+1, ustar, 2*(Q/2-N1*ustar**2)) + Gr(rr+1, 2*ustar, 2*3*Q/8) + Gr(rr+1, u2, 2*Q/4))  # Gr uses e^{-sig u^2/2}: sig=2a
    Odirect = O/norm
    rad = mp.sqrt(1+U2**2)
    arc_direct = 2*mp.pi*rad*(1+rad)**(rr+1)*mp.exp(-Q*Q/(4*N1)) / (N1/3*G(rr+4,Q)) * 1  # |arc|/(n_n/2pi * norm) with n_n cancels: n_n*rad(1+rad)^{..}e^{..} / (n_n/(2pi) * norm)
    print(f"j={j}: Ttilde code={Tt(rr)} direct={mp.nstr(Tdirect,8)} | Otilde code={Ot(rr)} direct={mp.nstr(Odirect,8)} | arctilde code={At(rr)} direct={mp.nstr(arc_direct,8)}")
# Itilde lo/hi poly direct: I^lo/((N/3)G_{2j+4}) polynomial part
for j in (0,1,2):
    rr=2*j
    lo_direct = 1 - (N1/5*G(rr+6,Q) + N1**3/162*G(rr+10,Q))/(N1/3*G(rr+4,Q))
    gm_check = 2*mp.quad(lambda u: u**(rr+4)*mp.exp(-Q*u*u/2), [0, 0.02, 0.1, 1]) if j==0 else None
    cH = N1*ustar**4/4
    hi_direct = 1 + mp.exp(cH)*(N1/4)*G(rr+8,Q)/G(rr+4,Q)   # I^hi/((N/3)G_{2j+4}) = 1 + e^{c_H}(N/4)G_{2j+8}/G_{2j+4}
    E = C.IVEval({C.s: S, C.phi: PHI})
    print("   G_4 closed vs quad:", mp.nstr(G(4,Q),10), mp.nstr(gm_check,10)) if gm_check else None
    print(f"j={j}: Itilde_lo poly code={E(C.Itilde_lo_poly(rr))} direct={mp.nstr(lo_direct,10)} | hi code={E(C.Itilde_hi_poly(rr))} direct={mp.nstr(hi_direct,10)}")
print("c_H code =", sp.N(C.KAPPA_H.subs(C.s, sp.Rational('0.5848')).subs(C.phi, 1), 10), " direct =", mp.nstr(N1*ustar**4/4, 10))
print("Main_D normalised at this point: code MAIND_N/s^7 =", sp.N((C.MAIND_N/C.S7).subs({C.s: sp.Rational('0.5848'), C.phi: 1}),10), " 4(1-eta)/(1+eta) eta^-7/2 =", mp.nstr(4*(1-eta)/(1+eta)*eta**-3.5,10))
