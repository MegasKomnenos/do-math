# -*- coding: utf-8 -*-
"""A12 검산: P3(G' 문턱·모멘트 위치 수), E5(증인 위치 상계로 m1 판독 대체), E6(DDL 1/4 산술),
S5(Jensen 지수 손실), S11(위험률 1/(2k) 하계·theorem-W 재조립), P9(쌍별 손실 상계 수치), C3(착지 질량 7/10),
C3 여파(band-check·right-part 상수 재조립), 자료 규모(원고_자료 파일에서 직접 셈)."""
import json, os, sys, io, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
R = os.path.join(ROOT, '원고_자료', '세션_재계산')

print("=== P3: G' 열별 인증서의 문턱 T_k=max(n0^bis, n^psi)와 모멘트 인증 위치 수 ===")
rows = {}
for f in ['res_p0.jsonl', 'res_p1.jsonl', 'res_ext_p0.jsonl', 'res_ext_p1.jsonl']:
    for ln in open(os.path.join(R, 'column_cert_iv', f), encoding='utf-8'):
        if not ln.strip():
            continue
        d = json.loads(ln)
        rows[d['k']] = d
ks = sorted(rows)
print('열 수', len(ks), '범위', ks[0], ks[-1], '누락', [k for k in range(501, 2001) if k not in rows], '모두 ok', all(rows[k]['ok'] for k in ks))
T = {k: max(rows[k]['n0'], rows[k]['nV']) for k in ks}
kmax = max((k for k in ks if k <= 840), key=lambda k: T[k])
print('501-840 max T_k =', max(T[k] for k in ks if k <= 840), '(k=%d)' % kmax)
print('T_841 =', T[841], ' T_2000 =', T[2000], ' nV_exact 전부:', all(rows[k].get('nV_exact', False) for k in ks))
print('T_k가 k에 단조증가:', all(T[ks[i]] <= T[ks[i + 1]] for i in range(len(ks) - 1)))
nM = {int(k): v for k, v in json.load(open(os.path.join(R, 'moment_cert_iv', 'nM.json'), encoding='utf-8')).items()}
diff = [nM[k] - T[k] for k in range(841, 2001)]
print('841-2000: n_M(k) - T_k 범위 [%d, %d]; n_M > T_k 전부: %s' % (min(diff), max(diff), all(d > 0 for d in diff)))
old1 = sum((13 * k * k) // 100 - (2 * k + 1) + 1 for k in range(501, 841))
old2 = sum(nM[k] - 1 - 10001 + 1 for k in range(841, 2001))
new2 = sum(max(0, T[k] - 1 - 20001 + 1) for k in range(841, 2001))
new2b = sum(max(0, T[k] - 1 - 10001 + 1) for k in range(841, 2001))
print('현행 모멘트 인증 위치 수: 첫째 범위 %d, 둘째 범위 %d, 합 %d' % (old1, old2, old1 + old2))
print('P3 뒤: 첫째 범위 0, 둘째 범위(20001..T_k-1) %d; (10001..T_k-1로 두면) %d; 줄어드는 수 %d' % (new2, new2b, old1 + old2 - new2))
print('T_k <= ceil(0.836 k^{3/2}) 전부:', all(T[k] <= math.ceil(0.836 * k ** 1.5) for k in ks))
print('n0(=n_bis0) 가운데 nV(=n_psi)보다 큰 열 수:', sum(1 for k in ks if rows[k]['n0'] > rows[k]['nV']))

print()
print('=== E5: 명제 5.3(증인 위치 상계)로 D:m1-column-reading을 대체할 수 있는가 ===')
def B(x):
    return 1.99 + 0.59963 * x ** (2 / 3) + 1.24847 * x ** (1 / 3)
worst = None
for k in range(3132, 19404):
    q0 = int(math.floor(0.75 * k ** (2 / 3)))
    m = k + q0
    if m > min(2 * k - 1, 20000):
        continue
    margin = (q0 + 1) - B(m + 1)
    if worst is None or margin < worst[0]:
        worst = (margin, k, q0, m)
print('0.75k^{2/3} 판: 최소 여유 (q0+1)-B(m+1) = %.3f at k=%d, q0=%d, m=%d' % worst)
x = 3000.0
print('q-증가 확인(도함수 at x=3000): %.4f' % (1 - 0.59963 * (2 / 3) * x ** (-1 / 3) - 1.24847 / 3 * x ** (-2 / 3)))
worst2 = None
for k in range(3132, 19404):
    q0 = int(math.floor(k ** (2 / 3)))
    m = k + q0
    if m > min(2 * k - 1, 20000):
        continue
    margin = (q0 + 1) - B(m + 1)
    if worst2 is None or margin < worst2[0]:
        worst2 = (margin, k, q0, m)
print('k^{2/3} 판(m<=20000 행만): 최소 여유 %.3f at k=%d,q0=%d,m=%d' % worst2)

print()
print('=== E6: DDL_2 <= 14(1+log 3k)/(5sqrt(pi k)) + 42/(5sqrt(3pi) k) < 1/4 (k>=6667) ===')
for k in [6667, 6668, 8065, 9551, 9705, 10 ** 5]:
    v = 14 * (1 + math.log(3 * k)) / (5 * math.sqrt(math.pi * k)) + 42 / (5 * math.sqrt(3 * math.pi) * k)
    print(' k=%d: %.5f' % (k, v))
print(' 네 가족 (나) 여유 재조립 (부록 D 구간의 차 - (1/4 - DDL(k0))):')
fam = {'벌크': (0.5893564, 0.13237), '2': (0.5045530, 0.12234), '1b': (0.4673235, 0.11404), '1a': (0.2047101, 0.11329)}
for name, (gap, ddl) in fam.items():
    print('  %s: %.4f  (F4: 벌크 .4717, 2 .3769, 1b .3314, 1a .0680)' % (name, gap - (0.25 - ddl)))
print(' (가)(a) q0=2 여유 재조립: 벌크 %.4f, 2 %.4f, 1b %.4f, 1a %.4f' % (2.681725 - (0.25 - 0.13237), 1.363140 - (0.25 - 0.12234), 0.7267559 - (0.25 - 0.11404), 0.2354722 - (0.25 - 0.11329)))
print(" (가)(b) 가장자리 R#': 1b %.4f, 1a %.4f" % (0.3372578 - (0.25 - 0.11404), 0.3947510 - (0.25 - 0.11329)))

print()
print('=== S5: Jensen 하계의 지수 손실 (d/(1-d))(mu2-mu1)/mu1, mu1>=Psi(d), mu2-mu1 <= d(1-d)^(-3/2) e^(1/(12(m+1))) ===')
def Bor(j):
    return math.exp((j - 1) * math.log(j) - j - math.lgamma(j + 1))
Ps = {}
acc = 0.0
for d in range(1, 120000):
    acc += d * Bor(d)
    Ps[d] = acc
best = (0, None)
for m in list(range(2001, 20001, 7)) + [10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8]:
    dmax = int(m ** (2 / 3) / 2)
    for d in range(14, dmax + 1):
        delta = d / m
        loss = delta / (1 - delta) * d * (1 - delta) ** (-1.5) * math.exp(1 / (12 * (m + 1))) / Ps[d]
        if loss > best[0]:
            best = (loss, (m, d))
print(' 표본 최대 지수 손실 %.6f at (m,d)=%s ; log2=%.6f ; F3 주장 .663774' % (best[0], best[1], math.log(2)))
print(' 소비처 확인: 6.48(나)는 6.49(다)에서만 쓰이고 그 자리는 하계, 14<=d<=m^{2/3}/2, m=k+d>=3145 (장6.md 1035·1061행)')

print()
print('=== S11: hz_k(N) >= 1-e^{-eps_N}, eps_N=g(N+1)-g(k) >= 3/(4k)-17/(24k^2) (N+1>=2k) ===')
def g(x):
    return (x - 1) * math.log(1 + 1 / x)
for k in [2001, 3131, 10 ** 4, 10 ** 6]:
    eps = g(2 * k) - g(k)
    lb = 3 / (4 * k) - 17 / (24 * k * k)
    hz = 1 - math.exp(-eps)
    claim = (0.75 - 11 / (6 * k)) / k
    print(' k=%d: eps(2k)=%.3e >= %.3e : %s ; 1-e^-eps=%.3e >= (3/4-11/(6k))/k=%.3e : %s ; >=1/(2k): %s' % (k, eps, lb, eps >= lb, hz, claim, hz >= claim, hz >= 1 / (2 * k)))
for k in [2001, 3131, 10 ** 4]:
    for n in [2 * k + 301, 3 * k + 1, 10 * k, 10 ** 9]:
        val = (1 / (2 * k)) * (2.38 * k ** 1.5 * (n - k + 1) ** 2 / (n * (n + 1)) - 301) - 1
        print('  k=%d n=%d: theorem-W 대괄호(hz>=1/(2k) 판) 하계 %.2f (>0 필요)' % (k, n, val))
print(' 현행 .14/n 판 D_k(n/k=3)/… at k=3131: %.3f' % (0.33316 * math.sqrt(3131) * 4 / 9 - 3 - 42.14 / 3131))

print()
print('=== P9: 쌍별 손실 상계 L^2/3 + (8C/25)sqrt(2/5) L^{5/2} (C=21/40) 대 K ===')
for K, L in [(10000, 50), (12000, 58), (13000, 79), (14000, 99), (15000, 102)]:
    C = 21 / 40
    v = L * L / 3 + (8 * C / 25) * math.sqrt(2 / 5) * L ** 2.5
    print(' (K,L)=(%d,%d): 상계 %.1f < K: %s' % (K, L, v, v < K))
for K, L in [(10000, 50), (15000, 102)]:
    C = 21 / 40
    e = lambda q: q + C * q ** 1.5
    best = 0
    for p in range(1, L):
        for q in range(1, L - p + 1):
            j = L - p - q
            v = j * (e(q) + e(p)) + (e(q) * (p - 1) + e(p) * (q - 1)) / 2
            best = max(best, v)
    print(' 브루트 최대(L=%d, p+q+j=L): %.1f' % (L, best))
k = 10000
q = 50
pi = q * (q - 1) / (2 * (k + 1))
print(' 현행 (7.11) ex_50(k=1e4)=%.1f ; 새 e_50=%.1f' % (q + (k + q) * pi / (1 - pi), q + 0.525 * q ** 1.5))

print()
print('=== C3: Lambda(Y) >= 1-2/Y-3Y/Q^{3/2}-3^{5/3}Y^{-1/3}+9/sqrt(Q)+3/Q^{3/2} > 7/10 (Y>=25000) ===')
for Y in [25000, 30000, 10 ** 5, 10 ** 6]:
    Q = int(6 * Y ** (2 / 3))
    v = 1 - 2 / Y - 3 * Y / Q ** 1.5 - 3 ** (5 / 3) * Y ** (-1 / 3) + 9 / math.sqrt(Q) + 3 / Q ** 1.5
    print(' Y=%d Q=%d: %.5f' % (Y, Q, v))
c = 0.8427 * 0.7 * 0.9936 * 1.9366 - 0.3678
print(' C3 여파 - w0 0.71216->0.7: right-part 계수 %.4f (현행 0.7869); Psi_R(lambda=2/3) >= %.4f' % (c, c * 2 / 3 - 1 / 3 - 2.5e-5))
print(' band-check 최소 비 재조립(곱 인자 선형): %.4f' % ((1.355874 + 0.0168736) * (0.7 / 0.71216) - 0.0168736))

print()
print('=== 자료 규모(원고_자료에서 직접 셈) ===')
def count_lines(p):
    return sum(1 for _ in open(p, encoding='utf-8', errors='ignore'))
qf = 0
for f in ['qfin_iv_result_p0.jsonl', 'qfin_iv_result_p1.jsonl']:
    qf += count_lines(os.path.join(R, 'Q_fin_1130', f))
print(' Q_fin_1130 결과 줄(열) 수:', qf)
for sub, f in [('r89eb039_polar_iv', 'out/NEW_blocks_merged.jsonl'), ('r89eb039_polar_iv', 'out/achain_iv.jsonl')]:
    p = os.path.join(R, sub, f)
    print(' ', sub, f, count_lines(p) if os.path.exists(p) else '없음')
for f in ['resB_p0.jsonl', 'resB_p1.jsonl', 'resAint_p0.jsonl', 'resAint_p1.jsonl', 'resAint_p3.jsonl', 'resA1_p0.jsonl', 'resA1_p1.jsonl', 'resA1_p3.jsonl', 'resA2.jsonl']:
    p = os.path.join(R, 'xcert_iv', f)
    print('  xcert', f, count_lines(p) if os.path.exists(p) else '없음')
bc = os.path.join(R, 'band_check', 'band_cells_CE0.tsv')
print(' band_cells_CE0.tsv 줄 수:', count_lines(bc))
nw = open(os.path.join(R, 'newton_r61_169', 'newton_cert_out.txt'), encoding='utf-8', errors='ignore').read()
print(' newton_cert_out.txt 머리:', nw[:300].replace('\n', ' | '))
for f in ['cert_Cb_iv_result_1_2280.json', 'cert_Cb_iv_result_2280_3000.json', 'cert_interval_iv_result.json']:
    try:
        d = json.load(open(os.path.join(R, 'window_mass_env', f), encoding='utf-8'))
        print('  window_mass_env', f, type(d).__name__, (len(d) if hasattr(d, '__len__') else ''), (list(d.keys())[:8] if isinstance(d, dict) else ''))
    except Exception as ex:
        print('  ', f, '읽기 실패', ex)
for sub, f in [('bprime_boxes', 'bprime_result.txt'), ('band_boxes', 'band_result.txt'), ('four_families', 'families_iv_out.txt'), ('M_natural', 'j_integrals_iv_out.txt'), ('theorem_D_base', 'thmD_base_iv_out.txt'), ('prop_W_thirteen', 'iv13_out.txt'), ('m1_column_reading', 'm1_read_out.txt'), ('H_star_plus', 'hplus_interval_out.txt'), ('AR_integrals', 'ar_integrals_iv_out.txt'), ('pair_one_variable', 'pair_iv_out.txt'), ('xcert_iv', 'summary.txt'), ('r89eb039_polar_iv', 'out/summary.txt'), ('Q_fin_1130', 'summarize_out.txt'), ('moment_cert_iv', 'summary.txt'), ('column_cert_iv', 'summary_all_out.txt')]:
    p = os.path.join(R, sub, f)
    if os.path.exists(p):
        t = open(p, encoding='utf-8', errors='ignore').read()
        print('  [%s/%s] %d바이트: %s' % (sub, f, len(t), t[:500].replace('\n', ' | ')))

print()
print('=== C1/C2: 기울인 생일 법칙의 정확 항등식, 모멘트 상계, 평균 하계, Pc 양성 ===')
from fractions import Fraction as Fr
def law(r, k):
    rho = Fr(k, k + r)
    bw = [Fr(1)]
    for j in range(r - 1):
        bw.append(bw[-1] * rho * Fr(j + 2, j + 1) * Fr(r - 1 - j, r))
    Z = sum(bw)
    mu = sum(j * bw[j] for j in range(r)) / Z
    m2 = sum(j * j * bw[j] for j in range(r)) / Z
    return mu, m2
for r, k in [(5, 20), (10, 100), (64, 1024), (170, 2217), (200, 4429)]:
    mu, m2 = law(r, k)
    ident = m2 + (3 + Fr(r * r, k)) * mu + 2
    print(' r=%d k=%d: E[J^2]+(3+r^2/k)mu+2 = %s (2r=%d) ; E[J(J-1)] <= 1.5mu^2: %s ; mu=%.4f, (6/7)sqrt r=%.4f' % (r, k, float(ident), 2 * r, (m2 - mu) <= Fr(3, 2) * mu * mu, float(mu), 6 / 7 * math.sqrt(r)))
import mpmath as mp
mp.mp.dps = 30
def mu_float(r, k):
    rho = mp.mpf(k) / (k + r)
    bw = mp.mpf(1); S = bw; M = mp.mpf(0)
    for j in range(r - 1):
        bw = bw * rho * mp.mpf(j + 2) / (j + 1) * mp.mpf(r - 1 - j) / r
        S += bw; M += (j + 1) * bw
    return M / S
worst = None
for r in list(range(64, 400)) + list(range(400, 3001, 50)) + [5000, 9999, 20000]:
    k = math.ceil(r ** 1.5 + 8 * r)
    mu = mu_float(r, k)
    ratio = mu / (mp.mpf(6) / 7 * mp.sqrt(r))
    if worst is None or ratio < worst[0]:
        worst = (ratio, r, k, mu)
print(' min_r mu/((6/7)sqrt r) over r in 64..20000 (k=ceil(r^1.5+8r)): %.5f at r=%d (mu=%.4f)' % (float(worst[0]), worst[1], float(worst[3])))
def Pc(k, r, eb):
    return k * (1 / (2 * r) - 1 / (3 * r * r)) - 2.5 + 2 * eb * (1 - 1 / k) - k / (k - 1) * (1 + math.sqrt(3 * math.pi * (r - 1) / 2))
w = None
for r in range(64, 20001):
    k = math.ceil(r ** 1.5 + 8 * r)
    v = Pc(k, r, 6 / 7 * math.sqrt(r)) - (math.sqrt(r) / 70 + 7 / 20)
    if w is None or v < w[0]:
        w = (v, r)
print(' C1: Pc(k_r, r, eb=(6/7)sqrt r) - (sqrt r/70 + 7/20) 최소 %.4f at r=%d (양이면 F4 주장 성립)' % w)
w2 = None
for r in range(2, 171):
    v = Pc(49831, r, 0)
    if w2 is None or v < w2[0]:
        w2 = (v, r)
print(' C2: Pc(49831, r, eb=0) 최소 %.3f at r=%d (F4: >57/2=28.5)' % w2)
print(' C2 보강: k=49831은 n=k+r>=50001, r<=170의 최소 k; Pc는 k에 증가(계수 1/(2r)-1/(3r^2)>0)이고 r에 감소')

print()
print('=== E5(둘째 부분): H*+의 G/L 비가 xi에 단조인지(격자 관찰; 증명 아님) ===')
def GL(xi, ups):
    one_l = 1 / (1 - ups ** 3)      # 1+1/ell
    c1 = (1 + xi * ups * one_l) ** 1.5 * math.exp(one_l * ups ** 3 / 12)
    uq = one_l ** 2 * (xi * ups + ups ** 3) ** 2 / 2
    Phi = one_l * c1 * math.exp(uq) * (0.11399 * xi ** 3.5 + 0.15958 * xi ** 2.5 * ups ** 2 + 0.85108 * xi ** 3 * ups)
    den = 0.7978 * math.sqrt(xi) - 0.8848 * ups
    E = c1 * one_l * (0.5320 * xi ** 1.5 * ups + 0.7979 * math.sqrt(xi) * ups ** 3 + c1 * (0.625 * xi ** 2 + xi * ups ** 2)) / den
    L = den * math.exp(-E) / (1 + (xi * ups + ups ** 3) * one_l)
    G = Phi + ups * (0.5320 * c1 * xi ** 1.5 + 0.2)
    return G / L
u1 = 3132 ** (-1 / 3); u2 = 19404 ** (-1 / 3)
for name, ups, lo, hi in [('A', u1, 2 * u1 * u1, 0.75), ('B', u2, 0.75, 1.0)]:
    N = 4000
    vals = [GL(lo + (hi - lo) * i / N, ups) for i in range(N + 1)]
    inc = sum(1 for i in range(N) if vals[i + 1] > vals[i]); dec = N - inc
    imax = max(range(N + 1), key=lambda i: vals[i])
    print(' 영역 %s: max G/L=%.4f at xi=%.4f (끝점 값 %.4f, %.4f); 증가 구간 %d, 감소 구간 %d' % (name, vals[imax], lo + (hi - lo) * imax / N, vals[0], vals[-1], inc, dec))
