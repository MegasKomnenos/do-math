# 검토전체24 R9: 네 가족의 첫 열·대표 위치에서 FLQ의 참값(배정밀도 사슬 재귀)과 9.4-9.6절 상·하계의 대조.
# 엄밀 계산이 아니라, 환원에 쓰인 부등식의 방향과 상수가 참값과 어긋나지 않는지 보는 검산이다.
import math, sys
import numpy as np
sys.path.insert(0, '.')

def logBor_arr(nmax):
    m = np.arange(1, nmax+1, dtype=np.float64)
    lg = np.array([math.lgamma(x+1) for x in m])
    return np.concatenate(([0.0], -m+(m-1)*np.log(m)-lg))   # index m

def surv(y, dmax, lb):
    # s[d] = frak s_d(y) = s_{y+d-1}(y), 1<=d<=dmax (dmax<=y+3), (6.21)과 d=y+3 보정
    s = np.zeros(dmax+1); s[1] = 1.0
    q = np.arange(1, dmax+1)
    fac = y/(y+q.astype(np.float64))
    for d in range(2, dmax+1):
        qq = q[:d-1]
        pr = np.exp(lb[d-qq]+lb[y+qq]-lb[y+d])
        val = 1.0-pr.sum()+np.dot(pr, fac[:d-1]*s[1:d])
        if d == y+3:
            val += math.exp(-1+2*lb[y+1]-lb[2*y+3])/2/(y+1)**2
        s[d] = val
    return s

def position(k, nu, lb):
    N = k+nu
    sk1 = surv(k+1, k+2, lb)   # s_m(k+1) = sk1[m-k], m<=2k+1
    sk = surv(k, k+2, lb)      # s_m(k) = sk[m-k+1], m<=2k+1
    skm = surv(k-1, k+2, lb)   # s_m(k-1) = skm[m-k+2], m<=2k
    S1 = lambda m: 1.0 if m <= k+1 else sk1[m-k]
    S0 = lambda m: 1.0 if m <= k else sk[m-k+1]
    Sm = lambda m: 1.0 if m <= k-1 else skm[m-k+2]
    c_k = lambda m: S1(m)-S0(m)        # c_m(k)
    c_km = lambda m: S0(m)-Sm(m)       # c_m(k-1)
    sig_k = lambda m: S1(m+1)-S0(m)    # varsigma_m(k)
    sig_km = lambda m: S0(m+1)-Sm(m)   # varsigma_m(k-1)
    n = 2*k+nu
    def f(m):
        if m <= N: return 2*((k+1)*c_k(m)-(k-1)*c_km(m))
        return (k+n-m+1)*c_k(m)-(k+n-m-1)*c_km(m)
    T = {2*k+1: 0.0}
    for m in range(2*k, k-1, -1): T[m] = T[m+1]+f(m)
    Stays = 2*sig_k(N+1)+sum((2-(m-N)/k)*(sig_k(m)+sig_km(m-1)) for m in range(N+2, 2*k+1))
    Bd = -(k+nu)*(sig_k(2*k)+c_km(2*k))-S(Sm, 2*k)
    DD = lambda m: (k+1)*S1(m+1)-2*k*S0(m)+(k-1)*Sm(m-1)
    om = lambda m: 2.0 if m <= N+1 else 2-(m-N)/k
    DDsum = sum(om(m)*DD(m) for m in range(k+1, 2*k+1))
    Tk_stay = 4-2*S1(N+1)-S1(N+2)+Bd+DDsum-Stays
    g = lambda x: (x-1)*math.log(1+1/x)
    u_over_wk = math.exp(g(N)-g(k))*S1(N)/S0(N-1)
    wk1_over_wk = math.exp(g(k+1)-g(N-1))*S0(N-2)/S0(N-1)
    theta = (2*(1+1/k)*S0(N)/S1(N)-1) if nu <= 0.48*k else -1.0
    lhs_na = T[k]+theta*u_over_wk/wk1_over_wk
    minT = min((T[m], m) for m in range(k+2, 2*k+1))
    vis = 2*(nu+1)/(k+1)*c_k(N+2)+sum((2-(m-N)/k)*((m-k)/(k+1)*c_k(m+1)+(m-k)/k*c_km(m)) for m in range(N+2, 2*k+1))
    return dict(Tk=T[k], Tk_stay=Tk_stay, Stays=Stays, Stays_vis=vis, BdS=Bd, DDsum=DDsum, negDD=sum(om(m)*min(DD(m), 0.0) for m in range(k+1, 2*k+1)),
                theta=theta, u_wk=u_over_wk, wk1_wk=wk1_over_wk, na=lhs_na, minT=minT, sN1=S1(N+1), sN=S1(N), c2k_km=k*c_km(2*k), c2k_k=(k-1)*c_k(2*k))
def S(fn, m): return fn(m)

def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def DDL(k): return 14*(math.log(3*k)-1)/(5*math.sqrt(math.pi*k))+37.6/(5*math.sqrt(math.pi)*k)
def BdT(k, nu): return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
def sW(k, nu, lb):
    j = np.arange(1, nu)
    return 1-float(np.dot(np.exp(lb[j]), (nu-j)/(k+nu+1-j)))
def sup(d, y): return min(1.0, 1.15*(y+d)/d**1.5)

for (k, nus) in ((6668, (6665, 6667, 5000)), (8065, (3871,)), (9551, (899,)), (9705, (591,))):
    lb = logBor_arr(2*k+8)
    for nu in nus:
        r = position(k, nu, lb)
        N = k+nu
        print(f"k={k} nu={nu}: T_k={r['Tk']:.6f} (머묾 꼴 {r['Tk_stay']:.6f}) Stays={r['Stays']:.5f} vis={r['Stays_vis']:.5f} Bd^S={r['BdS']:.5f} (-Bd^T={-BdT(k,nu):.5f}) "
              f"DD가중합={r['DDsum']:.5f} 음의부분합={r['negDD']:.5f} (-DDL={-DDL(k):.5f}) theta={r['theta']:.5f} u/w_k={r['u_wk']:.5f} w_k+1/w_k={r['wk1_wk']:.6f} "
              f"(나) 좌변/w_k+1={r['na']:.5f} min T_m={r['minT'][0]:.5f}@m-k={r['minT'][1]-k} s_N+1(k+1)={r['sN1']:.5f} sW={sW(k,nu,lb):.5f} sup={sup(nu+1,k+1):.5f} "
              f"k c_2k(k-1)={r['c2k_km']:.5f} (k-1)c_2k(k)={r['c2k_k']:.5f} u(k)={u(k):.5f}")
