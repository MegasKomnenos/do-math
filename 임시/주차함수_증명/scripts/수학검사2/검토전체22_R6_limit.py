# 정리 7:old-6-11 (나)의 극한 공식과 보조정리 supermultiplicative (나), pole-frame의 극한을 k=2..6에서 수치로 확인(다중정밀도).
import io, sys
from mpmath import mp, mpf, log, exp, findroot, quad, factorial
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mp.dps = 40
def run(k, N=400):
    a = [mpf(1)]
    for n in range(1, N + 1):
        a.append(sum(min(j, k) * a[j - 1] * a[n - j] for j in range(1, n + 1)) / n)
    ao = [mpf((m + 1) ** (m - 1)) / factorial(m) if m >= 1 else mpf(1) for m in range(N + 2)]
    Q = lambda x: sum((k - t) * mpf(t ** (t - 2) if t >= 2 else 1) * x ** t / factorial(t) for t in range(1, k))  # p_{t-1}=t^{t-2}
    # C_k(x) = 1 - e^{Q}(1 - k int_0^x e^{-Q})
    C = lambda x: 1 - exp(Q(x)) * (1 - k * quad(lambda f: exp(-Q(f)), [0, x]))
    rho = findroot(lambda x: C(x) - 1, mpf('0.6'))
    Kf = lambda x: exp(Q(x)) * quad(lambda f: f ** k * exp(-Q(f)), [0, x])
    Pinf = k * a[k - 1] * Kf(rho) / rho
    Kc = [mpf(0)] * (N + 2)
    for j in range(1, N + 2):
        s = sum((k - m) * ao[m - 1] * Kc[j - m] for m in range(1, k) if j - m >= 0)
        Kc[j] = (s + (1 if j == k + 1 else 0)) / j
    n = N
    EH = (n + 1) * a[k - 1] * sum(Kc[j] * a[n + 1 - j] for j in range(k + 1, n + 2)) / a[n]
    Pn = k * EH / n
    arho = [a[m] * rho ** m for m in range(N + 1)]
    print('k=%d rho=%s  1/e<rho<=1:%s  P(inf)=%s  P(%d)=%s  max a^rho=%s  a^rho_N*k*rho=%s' % (
        k, mp.nstr(rho, 12), mpf(1) / mp.e < rho <= 1, mp.nstr(Pinf, 10), n, mp.nstr(Pn, 10), mp.nstr(max(arho), 8), mp.nstr(arho[N] * k * rho, 12)))
for k in range(2, 7):
    run(k)
print('log 2 =', mp.nstr(log(2), 12))
