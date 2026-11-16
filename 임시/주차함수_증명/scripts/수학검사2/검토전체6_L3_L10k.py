# 검토전체6 L3: 보조정리 lemma-L (나)의 상수와 L(10^4) >= 0.845204, tm_d(1) <= sqrt(pi d/2) 를 수치로 확인한다.
from mpmath import mp, quad, exp, sqrt, pi, inf, findroot, mpf
mp.dps = 30
f = lambda q: (lambda y: y**q*exp(-y-y*y/2))
M = [quad(f(q), [0, inf]) for q in range(6)]
M26 = quad(f(2), [0, 6])
def Mstar(q):
    # max of y^q e^{-y-y^2/2}: derivative q/y - 1 - y = 0 -> y = (-1+sqrt(1+4q))/2
    y = (-1+sqrt(1+4*q))/2
    return f(q)(y)
Ms = {q: Mstar(q) for q in range(2, 6)}
C1 = 2*Ms[2] + M[3]/2 + M[5]/3
C2 = Ms[3]/2 + Ms[5]/3 + M[4]/2
C3 = Ms[4]/2 + M[3]/6
C4 = Ms[3]/6
print("M0..M5 =", [mp.nstr(m, 6) for m in M], " M2^(6) =", mp.nstr(M26, 6))
print("C1..C4 =", mp.nstr(C1, 6), mp.nstr(C2, 6), mp.nstr(C3, 6), mp.nstr(C4, 6))
def L(r):
    s = sqrt(mpf(r)); st = 1/s
    num = M26 - st*C1 - st**2*C2 - st**3*C3 - st**4*C4
    den = M[1] + st*(M[0] + exp(-mpf(1)/2)) + st**2
    return num/den
print("L(10^4) =", mp.nstr(L(10**4), 8), " L(2e4) =", mp.nstr(L(2*10**4), 6), " L(1e5) =", mp.nstr(L(10**5), 6))
# tm_d(1) = sum_{j>=1} prod_{i<=j}(1-i/(d+1)) vs sqrt(pi d/2)
for d in [1, 2, 3, 5, 10, 50, 200]:
    tm = mpf(0); pr = mpf(1)
    for j in range(1, d+1):
        pr *= (1 - mpf(j)/(d+1)); tm += pr
    print("d=", d, "tm_d(1)=", mp.nstr(tm, 6), " sqrt(pi d/2)=", mp.nstr(sqrt(pi*d/2), 6), tm <= sqrt(pi*d/2))
# cut-rep (가): k^{k-1}/k! = (1/pi) int_0^pi phi * ct(phi)^{-k-1} ct'(phi) dphi
from mpmath import cot, sin, diff, factorial
ct = lambda ph: ph/sin(ph)*exp(-ph*cot(ph))
for k in [1, 2, 3, 5]:
    val = quad(lambda ph: ph*ct(ph)**(-k-1)*diff(ct, ph), [mpf('1e-12'), pi - mpf('1e-9')])/pi
    print("k=", k, "integral=", mp.nstr(val, 10), " k^(k-1)/k! =", mp.nstr(mpf(k)**(k-1)/factorial(k), 10))
# log et(1/2)
print("log et(1/2) =", mp.nstr(mp.log(mp.e*ct(mpf('0.5'))), 8))
