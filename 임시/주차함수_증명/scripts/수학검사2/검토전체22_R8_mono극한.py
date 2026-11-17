# 검토 22차 R8: 437행 「생존 인자를 지우는 조립의 하계는 k→∞에서도 띠의 끝까지 못 간다」의 확인.
# (8.24)의 LB^mono(k, nu)를 저장된 Omega 절점값과 봉투 표로 배정밀도 평가한다(인증 계산 아님; 사실 확인용).
import sys, math
import numpy as np
base = sys.argv[1]
w = np.load(base + '/wKrig.npy'); xK = np.load(base + '/xKrig.npy')
tv = np.load(base + '/qenv_fix_v.npy'); tx = np.load(base + '/qenv_fix_x.npy')
print("w", w.shape, "xK", xK[:3], xK[-1], "table", tv.shape, tx[:3], tx[-1])
def ramp(s):
    return np.where(s <= -0.1, 0.0, np.where(s < 0.1, (s+0.1)**2/0.4, s))
g = np.minimum(1.0, 0.04 + 0.12*ramp(xK-1.0))
node = (1-g)*w
node = np.minimum.accumulate(node)
def Omega(x): return np.interp(x, xK, node)          # 절점 사이는 선형(적분 확인에는 충분)
def That(x): return np.interp(x, np.arange(len(tv))*0.0005, tv)
xs = np.linspace(0, 6, 600001)
integ = np.trapezoid(Omega(xs)*np.sqrt(2*xs/math.pi), xs)
print("Omega(0,0.5,1,2,3,4,6) =", [round(float(Omega(v)), 3) for v in (0, 0.5, 1, 2, 3, 4, 6)])
print("int_0^6 Omega sqrt(2x/pi) dx =", integ)
c = 1/math.sqrt(2*math.pi)
def Psi_arr(Q):
    j = np.arange(1, Q+1, dtype=float)
    ren = np.exp(j*np.log(j) - j - np.array([math.lgamma(v+1) for v in j]))
    return np.concatenate(([0.0], np.cumsum(ren)))
def Rlow(k, nu, qw, Psi):
    q = np.arange(1, qw+1, dtype=float)
    xi = (q-1)/k**(2/3)
    return float(np.sum((1-q*nu/(k*(k+nu)))**1.5*(k/(k+q))*(That(xi)+Psi[:qw]*Omega(xi)))/k)
def BorLe(m):
    # 1 - 꼬리; 큰 m에서 꼬리 ~ sqrt(2/pi) m^-1/2
    return 1-math.sqrt(2/math.pi)/math.sqrt(m+0.5)
def LBmono(k, theta):
    nu = int(theta*k); n = 2*k+nu; N = k+nu
    qmax = int(6*k**(2/3)); qfb = (3*(k-1)-4*qmax-12)//32
    Psi = Psi_arr(qmax)
    c0 = max((1-1/k)**(N-k+1), 1-math.exp(7/6)*N**1.5/(4*c*k*(2*k-1-N)))
    def fb(lam): return sum((lam*BorLe(qfb))**i for i in range(8))
    k1 = k-1
    R0 = Rlow(k, nu, qmax, Psi); R1 = Rlow(k1, nu+2, qmax, Psi)
    val = BorLe(nu-1)*math.exp(-1/(12*(n+1)))*(k/n)*(math.exp(-5/(12*k))*R0*fb(k/n) + c0*math.exp(-5/(12*k1))*R1*fb(k1/n))
    return val, R0, c0
for k in (6668, 10**5, 10**6, 10**7, 10**8, 10**9):
    out = []
    for th in (0.30, 0.40, 0.48):
        v, R0, c0 = LBmono(k, th); out.append((th, round(v, 4)))
    print("k=%d  LB^mono:" % k, out, " R^low_k(0.48)=%.4f c0=%.4f" % (R0, c0))
for th in (0.30, 0.35, 0.40, 0.48, 0.487, 0.49):
    lam = 1/(2+th)
    print("극한 theta=%.3f: 2*I*(1-lam^8)/(1+theta) = %.5f" % (th, 2*integ*(1-lam**8)/(1+th)))
