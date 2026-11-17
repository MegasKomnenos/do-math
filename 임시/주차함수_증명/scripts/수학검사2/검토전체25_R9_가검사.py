# 검토전체25 R9: 명제 check-ga 표의 (a)(b) 재계산 (binary64; 여유가 0.19 이상이라 배정밀도로 충분)
import math
PI2 = math.sqrt(2*math.pi)
def logBor(m): return -m+(m-1)*math.log(m)-math.lgamma(m+1)
def Bor(m): return math.exp(logBor(m))
def Ren(j): return j*Bor(j)

def surv_table(y, qmax):
    # s[q] = \mathfrak s_q(y) = s_{y+q-1}(y), q=1..qmax (사슬의 첫 걸음 분해)
    lb = [None]+[logBor(j) for j in range(1, qmax+1)]
    lby = [None]+[logBor(y+q) for q in range(1, qmax+1)]
    s = [None, 1.0]
    for q in range(2, qmax+1):
        tot = 0.0; stop = 1.0
        for q1 in range(1, q):
            pr = math.exp(lb[q-q1]+lby[q1]-lby[q])
            stop -= pr
            tot += pr*y/(y+q1)*s[q1]
        s.append(stop+tot)
    return s

def slow(d, y): return math.exp(-4/(3*PI2)*((y+d-1)/y)**1.5*d**1.5/y)
cR = PI2/2*math.exp(1/12)
def Q(y, xi):
    k = y-1; q0 = xi*y**(2/3)
    pre = k/(k+1)*(1-q0/(2*k))*2/PI2*math.exp(-1/12)*y/(cR*q0)
    b1 = math.exp(-cR*q0/y)-math.exp(-cR*q0*math.sqrt(q0/2)/y)
    b2 = math.exp(-cR*q0*math.sqrt(q0/2+1)/y)-math.exp(-cR*q0**1.5/y)
    return pre*(math.exp(-q0/y)*slow(q0, y)*b1+math.exp(-q0/(2*y))*slow(q0/2, y)*b2)

# 손실 상계는 검토전체25_R9_가족표.py가 낸 값(여섯째 자리에서 올림)을 넣는다
fam = [("벌크", 6668, 2.364207, None, 2**(2/3)), ("2", 8065, 3.680613, None, 2**(2/3)),
       ("1b", 9551, 4.315101, 1.850741, 2**(2/3)), ("1a", 9705, 4.806207, 1.806207, 1.3)]
for name, k0, R, Rp, xicap in fam:
    y = k0+1
    eps0 = math.floor(2**(2/3)*(k0+1)**(2/3))
    sy = surv_table(y, eps0+1)        # 용량 k0+1
    sk = surv_table(k0, eps0+2)       # 용량 k0
    BorT = [None]+[Bor(j) for j in range(1, eps0+2)]
    cum = [0.0]
    for j in range(1, eps0+2): cum.append(cum[-1]+BorT[j])
    best = None; bestp = None
    for q0 in range(2, eps0+1):
        z = 0.0
        for q in range(1, q0):
            l = q0-q
            RenS = l**-0.5/PI2*math.exp(-1/(12*l))
            Aup = PI2/4*math.exp(1/(12*l))*(q0+q)*math.sqrt(l)
            z += RenS*math.exp(-(q+Aup)/y)*sy[q]
        tail = 1-cum[q0-1]                       # Bor_>(q0-1)
        eR = k0/(k0+1)*(1-q0/(2*k0))*(max(z, sy[q0]-tail)+BorT[q0])
        e = 4*sk[q0+1]+2*eR
        if best is None or e-R < best[0]: best = (e-R, q0)
        if Rp is not None and q0 >= 104:
            v = eR+sk[q0+1]-Rp
            if bestp is None or v < bestp[0]: bestp = (v, q0)
    edge = 4*slow(xicap*(k0+1)**(2/3)+1, k0)+2*Q(k0+1, xicap)-R
    out = "가족 %s k0=%d eps0=%d (a) min=%.5f(q0=%d) (b) %.5f(xi=%.4f)" % (name, k0, eps0, best[0], best[1], edge, xicap)
    if Rp is not None:
        x = 2**(2/3)
        edgep = Q(k0+1, x)+slow(x*(k0+1)**(2/3)+1, k0)-Rp
        out += " | m0>N (a) min=%.5f(q0=%d) (b) %.5f" % (bestp[0], bestp[1], edgep)
        if name == "1a":
            out += " | 참고: xi=2^(2/3)로 잰 (b) m0<=N: %.4f" % (4*slow(x*(k0+1)**(2/3)+1, k0)+2*Q(k0+1, x)-R)
    print(out)
