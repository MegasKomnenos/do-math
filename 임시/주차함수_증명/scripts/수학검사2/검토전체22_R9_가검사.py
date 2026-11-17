# 검토 22차 R9: 9.6절 명제 check-ga 표의 독립 재계산.
# 생존 확률 s_d(y)는 6.3절의 첫 층 사슬 재귀 (6.21)로 부동소수(mpmath 30자리) 계산한다(구간 산술 아님 — 표의 값 대조용).
from mpmath import mp, mpf, sqrt, log, exp, pi, loggamma, floor
import importlib.util, os, sys
mp.dps = 30
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fam", os.path.join(here, "검토전체22_R9_가족검사.py"))
import io, contextlib
fam = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(fam)
mp.dps = 30

def logBor(n):
    n = mpf(n)
    return -n + (n-1)*log(n) - loggamma(n+1)
BorC = {}
def Bor(n):
    if n not in BorC: BorC[n] = exp(logBor(n))
    return BorC[n]
def Ren(j): return j*Bor(j)

def surv_table(y, dmax):
    # s[d] = frak s_d(y), 1<=d<=dmax (<= y+2)
    s = [None, mpf(1)]
    for d in range(2, dmax+1):
        By = Bor(y+d)
        tot = mpf(1)
        for q in range(1, d):
            p = Bor(d-q)*Bor(y+q)/By
            tot -= p*(1 - mpf(y)/(y+q)*s[q])
        s.append(tot)
    return s

f1 = 4/(3*sqrt(2*pi))
cR = sqrt(2*pi)/2*exp(mpf(1)/12)
def slow(d, y):
    d = mpf(d); y = mpf(y)
    return exp(-f1*((y+d-1)/y)**mpf('1.5')*d**mpf('1.5')/y)
def Q(y, xi):
    y = mpf(y); k = y-1; q0 = xi*y**(mpf(2)/3)
    pref = k/(k+1)*(1-q0/(2*k))*2*(2*pi)**mpf('-0.5')*exp(-mpf(1)/12)*y/(cR*q0)
    b1 = exp(-cR*q0/y)-exp(-cR*q0*sqrt(q0/2)/y)
    b2 = exp(-cR*q0*sqrt(q0/2+1)/y)-exp(-cR*q0**mpf('1.5')/y)
    return pref*(exp(-q0/y)*slow(q0, y)*b1 + exp(-q0/(2*y))*slow(q0/2, y)*b2)

def RenStar(j): return (2*pi)**mpf('-0.5')*mpf(j)**mpf('-0.5')*exp(-mpf(1)/(12*j))
def Aup(q0, q): return sqrt(2*pi)/4*exp(mpf(1)/(12*(q0-q)))*(q0+q)*sqrt(mpf(q0-q))

fams = [("벌크", 6668, None), ("2", 8065, mpf('0.48')), ("1b", 9551, 2), ("1a", 9705, mpf('1.3'))]
for name, k0, par in fams:
    kk = mpf(k0); c = kk**(mpf(2)/3)
    eps0 = int(floor(2**(mpf(2)/3)*(kk+1)**(mpf(2)/3)))
    D = fam.DDLn(k0)
    if name == "벌크":
        Rs = fam.abar(k0)+fam.bbar(k0)+D+fam.dbar(k0); Rp = None
    elif name == "2":
        nb = mpf('0.48')*kk
        Rs = 3*fam.sup(2*c+1, kk+1)+fam.BdT(k0, nb)+D+fam.StaysUp(k0, nb); Rp = None
    elif name == "1b":
        nb = 2*c
        Rs = 3*fam.sup(mpf('1.3')*c+1, kk+1)+fam.BdT(k0, nb)+D+fam.StaysUp(k0, nb)
        Rp = fam.BdT(k0, nb)+D+fam.StaysUp(k0, nb)
    else:
        nb = mpf('1.3')*c
        Rs = 3+fam.BdT(k0, nb)+D+fam.StaysUp(k0, nb)
        Rp = fam.BdT(k0, nb)+D+fam.StaysUp(k0, nb)
    mp.dps = 30
    y = k0+1
    sy = surv_table(y, eps0+1)      # frak s_q(k0+1)
    sk = surv_table(k0, eps0+2)     # frak s_d(k0)
    # Borel tail
    cum = mpf(0); tail = {}
    for j in range(1, eps0+1):
        tail[j] = 1-cum   # Bor_>(j-1) = sum_{i>=j} Bor(i)
        cum += Bor(j)
    best = None; bestp = None
    for q0 in range(2, eps0+1):
        zR = mpf(0)
        for q in range(1, q0):
            zR += RenStar(q0-q)*exp(-(q+Aup(q0, q))/y)*sy[q]
        eR = kk/(kk+1)*(1-q0/(2*kk))*(max(zR, sy[q0]-tail[q0])+Bor(q0))
        el = 4*sk[q0+1]+2*eR
        if best is None or el-Rs < best[0]: best = (el-Rs, q0)
        if Rp is not None and q0 >= 104:
            v = eR+sk[q0+1]-Rp
            if bestp is None or v < bestp[0]: bestp = (v, q0)
    print(f"[{name}] k0={k0} eps0={eps0} R#={mp.nstr(Rs,8)}  (a) min={mp.nstr(best[0],6)} at q0={best[1]}", end="")
    if Rp is not None: print(f"  R#'={mp.nstr(Rp,8)} (a') min={mp.nstr(bestp[0],6)} at q0={bestp[1]}", end="")
    print()
    caps = [2**(mpf(2)/3)] if name != "1a" else [mpf('1.3'), 2**(mpf(2)/3)]
    for xc in caps:
        d = xc*(kk+1)**(mpf(2)/3)+1
        v = 4*slow(d, k0)+2*Q(k0+1, xc)
        print(f"    (b) xi_cap={mp.nstr(xc,6)}: 4s_low+2Q={mp.nstr(v,8)}  -R# = {mp.nstr(v-Rs,6)}", end="")
        if Rp is not None:
            w = Q(k0+1, xc)+slow(d, k0)
            print(f"   Q+s_low={mp.nstr(w,8)} -R#' = {mp.nstr(w-Rp,6)}", end="")
        print()
