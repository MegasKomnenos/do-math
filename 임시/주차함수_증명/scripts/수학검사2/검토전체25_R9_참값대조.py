# 검토전체25 R9: 몇 위치 (k,nu)에서 첫 층 생존의 참값(사슬 재귀, binary64)으로 9.2-9.6절의 부등식을 끝에서 끝까지 대조
import math, sys
import numpy as np

def logBor_arr(n):
    m = np.arange(1, n+1, dtype=np.float64)
    lg = np.array([math.lgamma(i+1) for i in range(1, n+1)])
    return np.concatenate(([0.0], -m+(m-1)*np.log(m)-lg))   # index m

def surv(y, dmax, lb):
    # s[d] = \mathfrak s_d(y), d=1..dmax (dmax <= y+2)
    s = np.zeros(dmax+1); s[1] = 1.0
    fac = y/(y+np.arange(0, dmax+1, dtype=np.float64))
    for q in range(2, dmax+1):
        q1 = np.arange(1, q)
        pr = np.exp(lb[q-q1]+lb[y+q1]-lb[y+q])
        s[q] = 1.0-pr.sum()+np.dot(pr, fac[1:q]*s[1:q])
    return s

def run(k, nu):
    n = 2*k+nu; N = k+nu
    lb = logBor_arr(2*k+6)
    S = {y: surv(y, k+3 if y != k+1 else k+2, lb) for y in (k-1, k, k+1)}
    def s(m, y):          # s_m(y) = \mathfrak s_{m+1-y}(y), m>=y-1
        d = m+1-y
        return 1.0 if d <= 1 else S[y][d]
    c = lambda m, l: s(m, l+1)-s(m, l)
    sig = lambda m, l: s(m+1, l+1)-s(m, l)
    f = lambda m: 2*((k+1)*c(m, k)-(k-1)*c(m, k-1)) if m <= N else (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
    T = np.zeros(2*k+2)
    for m in range(2*k, k-1, -1): T[m] = T[m+1]+f(m)
    Stays = 2*sig(N+1, k)+sum((2-(m-N)/k)*(sig(m, k)+sig(m-1, k-1)) for m in range(N+2, 2*k+1))
    BdS = -(k+nu)*(sig(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
    DD = lambda m: (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
    om = lambda m: 2.0 if m <= N+1 else 2-(m-N)/k
    DDsum = sum(om(m)*DD(m) for m in range(k+1, 2*k+1))
    DDneg = sum(max(-DD(m), 0.0) for m in range(k+1, 2*k+1))
    Tk_form = 4-2*s(N+1, k+1)-s(N+2, k+1)+BdS+DDsum-Stays
    g = lambda x: (x-1)*math.log(1+1/x)
    u_over_wk = math.exp(g(N)-g(k))*s(N, k+1)/s(N-1, k)
    wk1_over_wk = math.exp(g(k+1)-g(N-1))*s(N-2, k)/s(N-1, k)
    theta = 2*(1+1/k)*s(N, k)/s(N, k+1)-1 if nu <= 0.48*k else -1.0
    lhs = T[k]+theta*u_over_wk/wk1_over_wk
    # 명시 조각
    uu = 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
    BdT = (k+nu)*uu*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
    DDLn = 14*(math.log(3*k)-1)/(5*math.sqrt(math.pi*k))+37.6/(5*math.sqrt(math.pi)*k)
    Bor = lambda m: math.exp(lb[m])
    sW = 1-sum(Bor(j)*(nu-j)/(k+nu+1-j) for j in range(1, nu))
    sup = lambda d, y: min(1.0, 1.15*(y+d)/d**1.5)
    if nu <= 0.48*k:
        thT = (2*(1+1/k)**(1-nu)-1)*(1+1/(k-1))**(-(nu-1))
    else:
        pitwo = Bor(k)*Bor(nu-1)/(math.e*Bor(N))
        best = (1+1/k)**(nu-1); Pi = 1.0
        for j0 in range(0, nu-1):
            Pi *= (k+1)/(k+j0+1)           # Pi^up_{j0+1}
            best = min(best, (1+1/k)**j0+Pi/pitwo)
        thT = -math.exp(1.5/k)*best
    adm = 4-3*min(sW, sup(nu+1, k+1))-BdT-DDLn+thT
    vis = 2*(nu+1)/(k+1)*c(N+2, k)+sum((2-(m-N)/k)*((m-k)/(k+1)*c(m+1, k)+(m-k)/k*c(m, k-1)) for m in range(N+2, 2*k+1))
    Tmin = min((T[m], m) for m in range(k+2, 2*k+1))
    # 미결 범위 안의 (가) 하계와 참값
    worst = None
    for q0 in range(2, int((2*k)**(2/3))+1):
        m0 = k+q0
        lead = 4*s(m0, k)+2*k*c(m0, k) if m0 <= N else k*c(m0, k)+s(m0, k)
        if worst is None or T[m0]-0 < worst[0]: worst = (T[m0], q0, lead)
    print("k=%d nu=%d: T_k=%.5f (머묾 꼴로 %.5f)  Stays=%.5f  Stays^vis=%.5f  Bd^S=%.5f(>= -Bd^T=%.5f)  sum omega DD=%.5f, 2*sum(DD)_-=%.5f(<= DDL♮=%.5f)" % (k, nu, T[k], Tk_form, Stays, vis, BdS, -BdT, DDsum, 2*DDneg, DDLn))
    print("   (나): [w_{k+1}T_k+theta u]/w_{k+1}=%.5f >= Stays^adm-Stays=%.5f (Stays^adm=%.5f, theta=%.5f, u/w_k=%.5f, w_{k+1}/w_k=%.6f, theta^T=%.5f)" % (lhs, adm-Stays, adm, theta, u_over_wk, wk1_over_wk, thT))
    print("   (가): min_{m>=k+2} T_m=%.5f (m-k=%d);  미결 범위(q0<=(2k)^(2/3)) 안의 최소 T=%.5f (q0=%d)" % (Tmin[0], Tmin[1]-k, worst[0], worst[1]))
    return Stays

for (k, nu) in [(9705, 591), (9551, 899), (8065, 3871), (6668, 6665), (6668, 3334), (12000, 103)]:
    run(k, nu)
