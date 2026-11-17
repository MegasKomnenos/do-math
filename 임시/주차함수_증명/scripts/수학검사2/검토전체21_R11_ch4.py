# R11 검산: 부록 D.central-gap-rational-audit의 몇 주장 재계산
import sympy as sp
from mpmath import mp, mpf, quad, sqrt, exp, pi, gamma, inf
# (ㄴ) 잔차 R(iota)의 x^0..x^4 계수 (gamma 변수), gamma=1/3에서 x^4 계수
g, x = sp.symbols('gamma x', positive=True)
iota = (1 - g**2)/4            # gamma = sqrt(1-4 iota)
def ups(gm): return (1+gm)/2
def C1(gm): return (1-ups(gm))/gm**2
def C2(gm): return -(1-ups(gm))*(2+ups(gm))/gm**5
def C3(gm): return 5*(1-ups(gm))*(6+gm-gm**2)/(2*gm**8)
def uhat(gm): return ups(gm) + x*C1(gm) + x**2*C2(gm) + x**3*C3(gm)
gshift = sp.sqrt(1 - 4*(iota - x))   # gamma at iota - x
R = (uhat(g) - 1)*uhat(gshift) + iota
ser = sp.series(R, x, 0, 5).removeO()
for j in range(5):
    c = sp.simplify(sp.expand(ser.coeff(x, j)))
    print(f"x^{j} coeff:", c if j < 4 else sp.factor(c))
    if j == 4: print("  at gamma=1/3:", c.subs(g, sp.Rational(1,3)))
# (ㄱ) a0, a1
mp.dps = 30
a0 = gamma(mpf(1)/3)/mpf(3)**(mpf(2)/3); a1 = gamma(mpf(2)/3)/mpf(3)**(mpf(1)/3)
print("a0 =", a0, " a1 =", a1)
# (ㅁ) int F0 = 0, int F1 = 46 sqrt2 - 12  (n_inf = 2/sqrt(pi))
mp.dps = 15
ninf = 2/sqrt(pi)
def Dw(b): return exp(-b*b/2)*quad(lambda v: exp(v*v/2), [0, b])
def BldR(b): return exp(b*b/2)*(2 - 2*b*Dw(b))
def F0(z):
    return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*((1-r*r)*z*z+(1-r*r)**2*z**4/4)*BldR(r*z)/sqrt(2*pi), [0,1])
def F1(z):
    return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*((1-r*r)*z*z+(1-r*r)**2*z**4/4)*(mpf(4)/3*r*r*z*z - mpf(2)/3*r*z**4), [0,1])
I0 = 2*quad(F0, [0, 2, 4, 8]); I1 = 2*quad(F1, [0, 2, 4, 8])
print("int F0 =", I0, "  int F1 =", I1, " 46sqrt2-12 =", 46*sqrt(2)-12)
# (ㅅ) 조립 산술, 정리 old-4-7 하계 (omega=6.98, k=10000)
k = mpf(10000); w = mpf('6.98')
lb = w - mpf(7)/2 - (4*w+mpf(1)/2)*mpf('1.2879')*k**(-mpf(1)/3) - mpf(13)*w/2*mpf('0.939')*k**(-mpf(2)/3) - 12*w/k
print("kR/Bor lower bound:", lb)
print("5.642*1.6809*0.39893-0.0163-3.554 =", mpf('5.642')*mpf('1.6809')*mpf('0.39893')-mpf('0.0163')-mpf('3.554'))
print("(2pi)^-1/2 (1-1/120000) =", (1-mpf(1)/120000)/sqrt(2*pi), " M0 lower 4sqrt2(1-23.75/k)=", 4*sqrt(2)*(1-mpf('23.75')/k))
print("Bn bound sqrt2/pi e^(1/k) =", sqrt(2)/pi*exp(1/k), " J: 0.4503*3*2.50663+1675.2/k =", mpf('0.4503')*3*mpf('2.50663')+mpf('1675.2')/k)
print("D bracket: 46sqrt2-12-54.6828 =", 46*sqrt(2)-12-mpf('54.6828'), " *e^(1/k) =", (46*sqrt(2)-12-mpf('54.6828'))*exp(1/k))
# 9400/k^3 vs 2e7*3.07*k^5/(3k-1)^8 at k=1e4
print("2e7*3.07*k^5/(3k-1)^8 * k^3 =", mpf(2e7)*mpf('3.07')*k**5/(3*k-1)**8*k**3)
# g_k = 2 - k M2/M0 with theta bounds (nu=0, -1), k=1e4
for nu in (0,-1):
    H1 = -(26+4*nu); H2 = 506+97*nu+5*nu*nu
    for d in (-3,3):
        th = 4 + H1/k + (H2+d)/k**2
        U2 = 1+(2*nu+2)/k+nu*(nu+1)/k**2; V2 = 4+(4*nu+2)/k+nu*(nu+1)/k**2
        print(f"nu={nu} d={d}: k*M2/M0 =", k*(U2-V2/th))
