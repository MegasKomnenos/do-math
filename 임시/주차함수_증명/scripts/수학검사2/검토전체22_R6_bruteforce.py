# 장7A의 진술을 작은 크기에서 정확 유리수로 다시 센다.
import itertools, math, io, sys
from fractions import Fraction as Fr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def caps(s):
    n = len(s); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and s[j] < s[i]:
            j -= 1
        h.append(i - j)   # i-j with j=-1 -> i+1 (1-based: i - 0)
    return h

NMAX = 8
perms = {n: [caps(s) for s in itertools.permutations(range(n))] for n in range(0, NMAX + 1)}

def A(n, l):  # A_{n,l}
    if l < 0: return 0
    return sum(math.prod(min(h, l + 1) for h in hs) for hs in perms[n])

p = lambda n: (n + 1) ** (n - 1) if n >= 1 else 1
for n in range(1, NMAX + 1):
    assert A(n, n - 1) == p(n)

# 1. 정리 old-6-2, 보조정리 old-6-3, 따름정리 old-6-4, 정리 old-6-6(Psi=1{M<=k-1}), 명제 old-6-7, 정리 old-6-8
def tk(k):
    j = 0
    while (k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) < 2 * k ** (2 * j + 1):
        j += 1
    return j
bad = 0
for n in range(1, NMAX + 1):
    for k in range(2, n + 2):
        Ak1 = A(n, k - 1)
        EZ = Fr(0); EH = Fr(0); ET = Fr(0); mu = Fr(0)
        for hs in perms[n]:
            w = math.prod(min(h, k) for h in hs)
            Z = sum(1 for h in hs if h > k); H = sum(1 for h in hs if h == k)
            EZ += w * Z; EH += w * H; ET += w * (Z * (Z - 1) - k * H)
            v = Fr(k + 1, k) ** Z + Fr(k - 1, k) ** (Z + H) - 2
            assert v >= Fr(Z * (Z - 1) - k * H, k * k)
            mu += w * v
        EZ /= Ak1; EH /= Ak1; ET /= Ak1; mu /= Ak1
        d = A(n, k) - 2 * A(n, k - 1) + A(n, k - 2)
        assert mu == Fr(d, Ak1)
        assert Fr(d) >= ET * Ak1 / (k * k)
        if not EZ >= Fr(n - k, k + 1): bad += 1; print('old-6-6 FAIL', n, k)
        # 명제 old-6-7: R_flat > x_flat * R_sharp^(-o_k)  (부동소수로 확인)
        Rs = A(n, k) / Ak1; Rf = A(n, k - 2) / Ak1
        o = -2 * math.log(1 - 1 / k) / math.log(1 + 1 / k)
        if not Rf > (1 - 1 / k) * Rs ** (-o) * (1 + 1e-12): 
            if not (n < k): print('old-6-7 margin small', n, k, Rf, (1 - 1 / k) * Rs ** (-o))
        if n >= k + (k + 1) * tk(k):
            assert d > 0, ('old-6-8', n, k)
print('1 ok, old-6-6 fails:', bad)

# 정리 old-6-6: 다른 대칭 가중치(변위 다중집합의 함수)로도 확인 — 전수 열거 n<=6
def pf_enum(n):
    for a in itertools.product(range(1, n + 1), repeat=n):
        occ = [0] * (n + 2); disp = []; ok = True; pos = [0] * n
        for c, x in enumerate(a):
            y = x
            while y <= n and occ[y]: y += 1
            if y > n: ok = False; break
            occ[y] = 1; disp.append(y - x); pos[y - 1] = c
        if ok: yield a, disp, pos
import random
random.seed(1)
for n in range(1, 7):
    data = []
    for a, disp, sig in pf_enum(n):
        data.append((tuple(sorted(disp)), caps(sig)))
    assert len(data) == p(n)
    keys = sorted(set(d for d, _ in data))
    for trial in range(30):
        wt = {key: random.choice([0, 0, 1, 2, 5]) for key in keys}
        tot = sum(wt[d] for d, _ in data)
        if tot == 0: continue
        for y in range(0, n + 1):
            E = Fr(sum(wt[d] * sum(1 for h in hs if h > y) for d, hs in data), tot)
            assert E >= Fr(n - y, y + 1), (n, y, wt)
print('old-6-6 대칭 가중 무작위 확인 ok')

# 2. b_{n,1} >= (n-1) n!/2
for n in range(4, NMAX + 1):
    assert A(n, 1) - A(n, 0) >= (n - 1) * math.factorial(n) // 2 > math.factorial(n)
# 3. 초승법성
for k in range(1, 6):
    for m in range(0, NMAX + 1):
        for m2 in range(0, NMAX + 1 - m):
            assert A(m + m2, k - 1) >= math.comb(m + m2, m) * A(m, k - 1) * A(m2, k - 1)
print('2,3 ok')

# 4. 소인 분해: C_{n,k} 를 1 - 1/A_{k-1} 의 계수로 구하고 전수 열거와 대조, C_{n,n}=(n-1)^(n-1), C' = k - Q'(1-C)
def series_inv(a, N):
    b = [Fr(0)] * (N + 1); b[0] = 1 / a[0]
    for n in range(1, N + 1):
        b[n] = -sum(a[j] * b[n - j] for j in range(1, n + 1)) / a[0]
    return b
N = NMAX
for k in range(1, 6):
    a = [Fr(A(n, k - 1), math.factorial(n)) for n in range(N + 1)]
    inv = series_inv(a, N)
    C = [-x for x in inv]; C[0] = Fr(0)
    Cn = [C[n] * math.factorial(n) for n in range(N + 1)]
    # 전수 열거로 소인 주차함수 수 (n<=6)
    for n in range(1, 7):
        cnt = 0
        for aa, disp, sig in pf_enum(n):
            if max(disp) <= k - 1 and all(sum(1 for x in aa if x <= b) != b for b in range(1, n)):
                cnt += 1
        assert cnt == Cn[n], (k, n, cnt, Cn[n])
    for n in range(1, min(k, N) + 1):
        assert Cn[n] == (n - 1) ** (n - 1) if n > 1 else Cn[n] == 1
    # C' = k - Q'_{k-1}(1-C)
    Qp = [Fr((k - t) * p(t - 1), math.factorial(t - 1)) for t in range(1, k)]  # 계수 of x^{t-1}
    oneC = [1 - C[0]] + [-c for c in C[1:]]
    for m in range(0, N):
        lhs = (m + 1) * C[m + 1]
        rhs = (k if m == 0 else 0) - sum(Qp[i] * oneC[m - i] for i in range(0, min(len(Qp), m + 1)))
        assert lhs == rhs, (k, m)
print('4 ok')

# 5. 정리 old-6-11 (가): E[H_k] = (n+1) a_{k-1} sum_{j=k+1}^{n+1} K_j a_{n+1-j} / a_n
for k in range(2, 6):
    a = [Fr(A(n, k - 1), math.factorial(n)) for n in range(N + 1)]
    ao = [Fr(p(n), math.factorial(n)) for n in range(N + 2)]
    assert all(a[m] == ao[m] for m in range(0, min(k, N) + 1))
    K = [Fr(0)] * (N + 2)
    for j in range(1, N + 2):
        s = sum((k - m) * ao[m - 1] * K[j - m] for m in range(1, k) if j - m >= 0)
        K[j] = (s + (1 if j == k + 1 else 0)) / j
    assert all(K[j] == 0 for j in range(0, k + 1)) and K[k + 1] == Fr(1, k + 1)
    for n in range(1, N + 1):
        EH = Fr(sum(math.prod(min(h, k) for h in hs) * sum(1 for h in hs if h == k) for hs in perms[n]), A(n, k - 1))
        rhs = (n + 1) * a[k - 1] * sum(K[j] * a[n + 1 - j] for j in range(k + 1, n + 2)) / a[n]
        assert EH == rhs, (k, n, EH, rhs)
print('5 ok')

# 6. 보조정리 column-lemma (가)의 수
L = 10 ** 21 * 400 ** 10; R = 17 ** 21 * 123 ** 10
print('L=%.6e R=%.6e' % (L, R), L > R)
print('17^4', 17 ** 4, '8.36^5', 8.36 ** 5, '17^21 = %.5e' % 17 ** 21, '123^10 = %.5e' % 123 ** 10, '1.513^5', 1.513 ** 5)
print('1-2.1*(10/17)^3 =', 1 - 2.1 * (10 / 17) ** 3)
print('2(k+1)/(k-1) at 41:', Fr(2 * 42, 40))
# 7. t_k, n^sharp_k
print('max n^sharp_k for 2<=k<=140:', max(k + (k + 1) * tk(k) for k in range(2, 141)), ' k^2+2k at 140:', 140 * 142)
print('n^sharp_k: k=140', 140 + 141 * tk(140), 'k=141', 141 + 142 * tk(141), 'k=203', 203 + 204 * tk(203), 'k=204', 204 + 205 * tk(204), 'k=500', 500 + 501 * tk(500))
print('first k with n^sharp_k > 20000:', next(k for k in range(2, 600) if k + (k + 1) * tk(k) > 20000))
