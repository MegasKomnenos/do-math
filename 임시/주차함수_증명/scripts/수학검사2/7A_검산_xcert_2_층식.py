"""(2)(3)(4)의 식 검산: Omega의 나무 함수 표현과 R 상계, eta_j 상계, Stirling Bor 괄호, f_i 원시함수·볼록성, A-int F_i 상계식(글)의 유효성, 창 재귀."""
from mpmath import mp, mpf, exp, log, sqrt, pi, e, lambertw, quad, factorial, findroot
mp.dps = 30
c = 1/sqrt(2*pi); c0 = c/e
def Bor(m): return exp(-m)*mpf(m)**(m-1)/factorial(m)
def pr0(n): return mpf(n-1)**(n-1)*exp(-n)/factorial(n)
# 1. Omega tree identity at k=1000, sigma=-5 and -0.5
def T(z): return -lambertw(-z)
for k, s in ((1000, mpf(-5)), (1000, mpf('-0.5')), (600, mpf(-30))):
    Om = sum((k-m)*Bor(m)*(exp(s*m/k)-1)/m for m in range(1, k))
    t = 1 - T(exp(-1+s/k))
    R = sum(Bor(m)*(1-exp(s*m/k))*(1-mpf(k)/m) for m in range(k, 40*k))
    print("k=%d s=%s: Omega=%.12f ; -k t^2/2 + t - R = %.12f ; t+log(1-t)-s/k=%.2e ; R=%.6e ; bound c(4/3 k^-1/2+0.19k^-3/2)=%.6e ; R<=bound: %s"
          % (k, s, Om, -k*t*t/2+t-R, t+log(1-t)-s/k, R, c*(mpf(4)/3/sqrt(k)+mpf('0.19')/k**mpf(1.5)), R <= c*(mpf(4)/3/sqrt(k)+mpf('0.19')/k**mpf(1.5))))
# R bound in the worst case sigma -> -inf (1 - e^{sigma m/k} -> 1): sum_{m>=k} Bor(m)(1-k/m)
for k in (501, 1000, 5000, 20000):
    R = sum(Bor(m)*(1-mpf(k)/m) for m in range(k, 60*k)) + 2*c/sqrt(60*k)  # tail crude add
    print("k=%d: sup_sigma R <= %.6e  vs bound %.6e  ok=%s" % (k, R, c*(mpf(4)/3/sqrt(k)+mpf('0.19')/k**mpf(1.5)), R <= c*(mpf(4)/3/sqrt(k)+mpf('0.19')/k**mpf(1.5))))
# 2. eta_j bound: 0 < eps''_j <= eta_j
worst = -1
for j in list(range(2, 3001)) + [5000, 10000, 100000, 10**6]:
    lg = (j-1)*log(mpf(j-1)) - j - mp.loggamma(j+1) if j > 1 else 0
    eps2 = lg - (log(c0) - mpf(1.5)*log(j))
    eta = mpf(5)/(12*j) + mpf(1)/(6*j*(j-1))
    if eps2 <= 0 or eps2 > eta: print("eta violation at j=", j, eps2, eta)
    worst = max(worst, eps2/eta)
print("eta_j: max eps''_j/eta_j over j<=3000 & samples = %.6f (<=1 ok)" % worst)
# 3. Stirling Bor brackets
bad = 0
for m in list(range(1, 3001)) + [10**4, 10**5]:
    lb = log(c) - mpf(1.5)*log(m) - mpf(1)/(12*m); ub = log(c) - mpf(1.5)*log(m) - mpf(1)/(12*m+1)
    lB = -m + (m-1)*log(mpf(m)) - mp.loggamma(m+1)
    if not (lb <= lB <= ub): bad += 1
print("Bor Stirling brackets violations:", bad)
# pr0 lower bracket c0 n^{-3/2} <= pr0_n
bad = 0
for n in range(2, 3001):
    if log(pr0(n)) < log(c0) - mpf(1.5)*log(n): bad += 1
print("pr0 >= c0 n^-3/2 violations:", bad)
# 4. antiderivative of f_i and the three monotone regions / convexity
def f(t, k, i): return (k-t)*t**mpf(-1.5)*(k+i-t)**mpf(-1.5)
def F(t, k, i): return -2/mpf(k+i)*sqrt((k+i-t)/t) - 2*i*(2*t-k-i)/((k+i)**2*sqrt(t*(k+i-t)))
k, i = 5000, 300
num = quad(lambda t: f(t, k, i), [i, 1000, 3000, k])
print("antiderivative check: quad=%.12e  F(k)-F(i)=%.12e  closed 2(k-i)^2/(sqrt(ki)(k+i)^2)=%.12e" % (num, F(k,k,i)-F(i,k,i), 2*(k-i)**2/(sqrt(mpf(k)*i)*(k+i)**2)))
def logd(t, k, i): return -1/(k-t) - mpf(1.5)/t + mpf(1.5)/(k+i-t)
def d2(t, k, i): return mp.diff(lambda x: f(x, k, i), t, 2)
for (k, i) in ((5000, 30), (5000, 300), (5000, 900), (100000, 24)):
    signs = []
    prev = None
    for t in [i + (k-1-i)*q/400 for q in range(401)]:
        sgn = 1 if logd(t, k, i) > 0 else -1
        if sgn != prev: signs.append((float(t), sgn)); prev = sgn
    tc = min(k-4*i, 0.7*k)
    conv_ok = all(d2(t, k, i) >= 0 for t in [i + (tc-i)*q/50 for q in range(51)] if t < tc)
    print("k=%d i=%d: sign changes of f' at %s ; convex on [i, min(k-4i,0.7k)=%g): %s" % (k, i, signs, tc, conv_ok))
# 5. A-int upper bound formula of the text vs exact sum for large i (k=5000)
k = 5000
viol = []
for i in list(range(21, 1000, 37)) + list(range(1000, 5000, 97)) + [4990, 4998, 4999]:
    S = sum(f(mpf(t), k, i) for t in range(i, k))
    text_bound = F(k, k, i) - F(i - mpf(0.5), k, i) + mpf('0.4')/(k**mpf(1.5)*sqrt(i))
    code_hs2 = 2*(k-i)**2/(sqrt(mpf(k)*i)*(k+i)**2) + f(mpf(i), k, i) + mpf('0.4')/(k**mpf(1.5)*sqrt(i))
    lo_bound = 2*(k-i)**2/(sqrt(mpf(k)*i)*(k+i)**2) - mpf('0.4')/(k**mpf(1.5)*sqrt(i))
    cond = min(k-4*i-1, (7*k)//10) > i+1
    if S > text_bound or S > code_hs2 or S < lo_bound:
        viol.append((i, float(S), float(text_bound), float(code_hs2), float(lo_bound), cond))
print("k=5000: violations (i, sum, text_hs1, code_hs2, lower, cond_hs1):")
for v in viol: print("   ", v)
print("  (count %d)" % len(viol))
# 6. t lower bound  t >= sqrt(2eps/(1+4/3 sqrt(2eps))) for eps in (0,1/8]
worst = 1e9
for eps in [mpf(j)/800 for j in range(1, 101)]:
    t = findroot(lambda x: -x-log(1-x)-eps, sqrt(2*eps))
    worst = min(worst, t - sqrt(2*eps/(1+mpf(4)/3*sqrt(2*eps))))
print("min over eps<=1/8 of [t - sqrt(2eps/(1+4/3 sqrt(2eps)))] = %.3e (>=0 ok)" % worst)
# Omega(s') >= s' + 0.438|s'|^{3/2} k^{-1/2} - Rmax for eps<=1/8, check on -k t^2/2+t part
worst = 1e9
for k in (10**5, 10**6):
    for eps in [mpf(j)/800 for j in range(1, 101)]:
        t = findroot(lambda x: -x-log(1-x)-eps, sqrt(2*eps))
        sp = -eps*k
        worst = min(worst, (-k*t*t/2 + t) - (sp + mpf('0.438')*(-sp)**mpf(1.5)/sqrt(k)))
print("min [(-k t^2/2 + t) - (s' + 0.438|s'|^{3/2}k^{-1/2})] = %.3e (>=0 ok)" % worst)
# 7. window recursion: ghat_j = kappa_j rho^{j-k-1}; check with k=6 small: kappa from K' = Q' K + x^k
k = 6
rho = findroot(lambda x: sum(mpf(n-1)**(n-1)*x**n/factorial(n) for n in range(1, 60)) - 1, 0.5) if False else None
# just verify the coefficient identity a_circ_{m-1} rho^m = Bor(m) e^{sigma m/k} with sigma = k log(e rho) for arbitrary rho
rho = mpf('0.45'); sig = k*log(e*rho)
print("a^circ_{m-1} rho^m vs Bor(m) e^{sig m/k} (m=1..5):", [float(mpf(m)**(m-2)/factorial(m-1)*rho**m - Bor(m)*exp(sig*m/k)) for m in range(1, 6)])
