# 검토전체24 R9: 9.3-9.6절 수치의 재계산 (mpmath 30자리 + 배정밀도 재귀; 엄밀 구간 아님, 표의 수와 대조용)
import math
from mpmath import mp, mpf, sqrt, log, exp, pi, quad, floor, ceil
mp.dps = 30

print("== 9.3 표의 문턱")
for k in (8064, 8065):
    print(k, 20001-2*k, 0.48*k, 20001-2*k > 0.48*k)
for k in (9948, 9949):
    print(k, 20001-2*k, max(103, 20001-2*k))

print("== 가족 첫 열")
def first(up):
    k = 6668
    while not (max(103, 20001-2*k) <= up(k)): k += 1
    return k
for name, up in (("1a", lambda k: 1.3*k**(2/3)), ("1b", lambda k: 2*k**(2/3)), ("2", lambda k: 0.48*k), ("bulk", lambda k: k-1)):
    k = first(up); print(name, k, 20001-2*k, up(k), "| k-1:", 20001-2*(k-1), up(k-1))

print("== 상수")
f1 = 4/(3*sqrt(2*pi)); cR = sqrt(2*pi)/2*exp(mpf(1)/12)
print("f1", f1, "cR", cR, "theta0", (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')))
print("beta0 min", cR*mpf('1.04')**1.5/sqrt(2), "iota q0 max", cR*2**(mpf(2)/3)/mpf(6669)**(mpf(1)/3))
print("1.04*6669^(2/3)", 1.04*6669**(2/3), "2^(2/3)*6669^(2/3)", 2**(2/3)*6669**(2/3))

mS = mpf('1.15')
def u(k): k = mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**mpf('-1.5')*k**mpf('-0.5')
def DDL(k): k = mpf(k); return 14*(log(3*k)-1)/(5*sqrt(pi*k))+mpf('37.6')/(5*sqrt(pi)*k)
def BdT(k, nu): k = mpf(k); return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**mpf('-1.5')
def sup(d, y): return min(mpf(1), mS*(y+d)/mpf(d)**mpf('1.5'))
def ec(k, nu): k = mpf(k); return 3*nu**2/((k-1)*k)+mpf('4.8')*sqrt(nu)/k+nu**2/(2*(k-1)**2)
def ebar(k):
    k = mpf(k); xi = (sqrt(5*k*log(k))+2)/k
    return exp(3/(2*k))*(exp(sqrt(5*log(k)/k)+1/k)+mpf('2.40918')*k**(mpf('1.5')-mpf('2.5')/(1+xi)))
def cAb(r): return 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
def Sub(k, nb):
    k = mpf(k); xi = (nb+4)/(k-1)
    if xi >= mpf('0.6'): return mpf(0)
    return (k-1)/k*quad(lambda r: (r-xi)*(1+r)*r**mpf('-1.5')*(1-r)**-2, [xi, mpf('0.6')])
def Top(k, nb):
    k = mpf(k); a = mpf('0.6')-mpf('2.6')/k; kn = (nb+1)/k
    pts = [a, 1] if not (a < kn < 1) else [a, kn, 1]
    return quad(lambda r: min(mpf(2), 2+kn-r)*(1+r/3)*r**mpf('-1.5'), pts)
def Flat(y): y = mpf(y); a = (mS*(y+2*y**(mpf(2)/3)))**(mpf(2)/3); return 2*(a-1)/(y+2-a)
def Ab(y, k, nb):
    y = mpf(y); z = mpf('0.6')+1/y
    return mS*(1+1/y)*(4*((mS*y)**(mpf(2)/3)-1)**mpf('-0.5')+y**mpf('-0.5')*(2*cAb(z)-4*z**mpf('-0.5')-Sub(k, nb)))
def Stup(k, nb): return sum(Flat(y)+Ab(y, k, nb) for y in (k-1, k))+2*mpf('16.54')*mpf(k)**mpf('-0.5')*Top(k, nb)

print("== 9:check-na 표")
k = 6668
abar = 3*mS*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**mpf('1.5'); bbar = 2*u(k)*(2*k-1)/mpf(k-1)+3*(k+1)*mpf(k-1)**mpf('-1.5'); dbar = mpf('72.217')/sqrt(k)
print("bulk: 4-ebar", 4-ebar(k), "abar", abar, "bbar", bbar, "DDL", DDL(k), "dbar", dbar, "sum", abar+bbar+DDL(k)+dbar, "margin", 4-ebar(k)-(abar+bbar+DDL(k)+dbar), "sum+ebar", abar+bbar+DDL(k)+dbar+ebar(k))
Rs = {"bulk": abar+bbar+DDL(k)+dbar}
k = 8065; k23 = mpf(k)**(mpf(2)/3)
t = [3*sup(2*k23+1, k+1), (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')), BdT(k, mpf('0.48')*k), DDL(k)]
o2 = 4-t[0]+t[1]-t[2]-t[3]; S2 = Stup(k, mpf('0.48')*k)
print("2:", [str(x)[:9] for x in t], "o", o2, "Stup", S2, "margin", o2-S2)
Rs["2"] = t[0]+t[2]+t[3]+S2
k = 9551; k23 = mpf(k)**(mpf(2)/3); xi2 = 2*k23/(k-1)
t = [3*sup(mpf('1.3')*k23+1, k+1), (2*exp(-xi2)-1)*exp(-xi2), BdT(k, 2*k23), DDL(k)]
o1b = 4-t[0]+t[1]-t[2]-t[3]; S1b = Stup(k, 2*k23)
print("1b:", [str(x)[:9] for x in t], "o", o1b, "Stup", S1b, "margin", o1b-S1b)
Rs["1b"] = t[0]+t[2]+t[3]+S1b; Rsp = {"1b": t[2]+t[3]+S1b}
k = 9705; k23 = mpf(k)**(mpf(2)/3)
t = [ec(k, mpf('1.3')*k23), BdT(k, mpf('1.3')*k23), DDL(k)]
o1a = 2-t[0]-t[1]-t[2]; S1a = Stup(k, mpf('1.3')*k23)
print("1a:", [str(x)[:9] for x in t], "o", o1a, "Stup", S1a, "margin", o1a-S1a)
Rs["1a"] = 3+t[1]+t[2]+S1a; Rsp["1a"] = t[1]+t[2]+S1a
print("DDL nat", [str(DDL(x))[:9] for x in (6668, 8065, 9551, 9705)])
print("R#", {a: str(b)[:8] for a, b in Rs.items()}, "R#'", {a: str(b)[:8] for a, b in Rsp.items()})

print("== 9:check-ga (b) 가장자리")
def slow(d, y): d = mpf(d); y = mpf(y); return exp(-f1*((y+d-1)/y)**mpf('1.5')*d**mpf('1.5')/y)
def Q(y, xi):
    y = mpf(y); k = y-1; q0 = xi*y**(mpf(2)/3)
    pre = k/(k+1)*(1-q0/(2*k))*2*(2*pi)**mpf('-0.5')*exp(-mpf(1)/12)*y/(cR*q0)
    A_ = exp(-q0/y)*slow(q0, y)*(exp(-cR*q0/y)-exp(-cR*q0*sqrt(q0/2)/y))
    B_ = exp(-q0/(2*y))*slow(q0/2, y)*(exp(-cR*q0*sqrt(q0/2+1)/y)-exp(-cR*q0**mpf('1.5')/y))
    return pre*(A_+B_)
cap = 2**(mpf(2)/3)
for name, k0 in (("bulk", 6668), ("2", 8065), ("1b", 9551), ("1a", 9705)):
    xc = mpf('1.3') if name == "1a" else cap
    e1 = 4*slow(xc*mpf(k0+1)**(mpf(2)/3)+1, k0)+2*Q(k0+1, xc)-Rs[name]
    line = f"{name} k0={k0} eps0={int(floor(cap*mpf(k0+1)**(mpf(2)/3)))} (b) m0<=N margin {str(e1)[:7]}"
    if name in Rsp:
        e2 = Q(k0+1, cap)+slow(cap*mpf(k0+1)**(mpf(2)/3)+1, k0)-Rsp[name]
        line += f" | (b) m0>N margin {str(e2)[:7]}"
    print(line)

print("== 9:check-ga (a) 배정밀도 사슬 재귀")
def logBor(m): return -m+(m-1)*math.log(m)-math.lgamma(m+1)
def surv(y, dmax):
    # s[d] = frak s_d(y), d=1..dmax, (6.21)
    s = [0.0, 1.0]
    for d in range(2, dmax+1):
        lb = logBor(y+d); tot = 0.0; acc = 0.0
        for q in range(1, d):
            pq = math.exp(logBor(d-q)+logBor(y+q)-lb)
            tot += pq; acc += pq*(y/(y+q))*s[q]
        s.append(1.0-tot+acc)
    return s
for name, k0 in (("bulk", 6668), ("2", 8065), ("1b", 9551), ("1a", 9705)):
    eps0 = int(math.floor(2**(2/3)*(k0+1)**(2/3))); y = k0+1
    sy = surv(y, eps0+1); sk = surv(k0, eps0+2)
    Bor = [0.0]+[math.exp(logBor(j)) for j in range(1, eps0+2)]
    cum = [0.0]
    for j in range(1, eps0+2): cum.append(cum[-1]+Bor[j])
    best = None; best2 = None
    c_R = float(cR)
    for q0 in range(2, eps0+1):
        zR = 0.0
        for q in range(1, q0):
            l = q0-q
            ren = (2*math.pi)**-0.5*l**-0.5*math.exp(-1/(12*l))
            Aup = math.sqrt(2*math.pi)/4*math.exp(1/(12*l))*(q0+q)*math.sqrt(l)
            zR += ren*math.exp(-(q+Aup)/y)*sy[q]
        tail = 1.0-cum[q0-1]
        eR = k0/(k0+1)*(1-q0/(2*k0))*(max(zR, sy[q0]-tail)+Bor[q0])
        v = 4*sk[q0+1]+2*eR-float(Rs[name])
        if best is None or v < best[0]: best = (v, q0)
        if name in Rsp and q0 >= 104:
            v2 = eR+sk[q0+1]-float(Rsp[name])
            if best2 is None or v2 < best2[0]: best2 = (v2, q0)
    print(name, k0, "eps0", eps0, "(a) min", best, "(a) m0>N min", best2)
