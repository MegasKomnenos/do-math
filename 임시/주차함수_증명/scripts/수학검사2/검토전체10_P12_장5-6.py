# -*- coding: utf-8 -*-
"""P12 검산 2: 부록 D 장5A·5B·6 항목의 셀 수·상수, 11.2절 표와의 문자열 대조, 자료 경로의 존재. python -I 로 돌린다."""
import sys, re, os, glob
from fractions import Fraction as Fr
from math import comb, factorial, ceil, floor
from mpmath import mp, mpf, exp, sqrt, pi, e as E

BASE = r'C:\math\임시\주차함수_증명'
REC = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
out = []
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)

# ---------- 1. 위치·쌍의 수 ----------
def qr_positions(n):  # (n-1)/2 <= l <= n-3
    lo = ceil(Fr(n - 1, 2)); return max(0, n - 3 - lo + 1)
def pairs(n):  # ceil((n-1)/2) <= l <= n-2
    lo = ceil(Fr(n - 1, 2)); return max(0, n - 2 - lo + 1)
log('[1] Q_R positions 5..20000:', sum(qr_positions(n) for n in range(5, 20001)), '(D: 99,970,002)')
log('[1] pairs 5..20000:', sum(pairs(n) for n in range(5, 20001)), '(D: 99,989,998)')
log('[1] Q_R positions 20001..50000:', sum(qr_positions(n) for n in range(20001, 50001)), '(D: 524,955,000)')
log('[1] pairs 20001..50000:', sum(pairs(n) for n in range(20001, 50001)), '(D: 524,985,000)')
log('[1] Q_R positions 5..2000:', sum(qr_positions(n) for n in range(5, 2001)), '(D: 997,002)')
log('[1] (L) comparisons 10001..20000, 1<=l<=k_n-1:', sum((n + 1) // 2 - 1 for n in range(10001, 20001)), '(D: 74,995,000)')
log('[1] row cert 501..4999:', sum(10000 - 2 * k for k in range(501, 5000)), '(D: 20,245,500)')
log('[1] left columns total:', 4 * 9989 + sum(10000 - 2 * k for k in range(6, 121)), '(D: 1,175,466)')
log('[1] newton polys:', sum(r - 1 for r in range(2, 171)), sum(r - 1 for r in range(2, 41)), '(D: 14,365 ; 780)')
log('[1] band-A cells: (A) 21*235=', 21 * 235, ' 82*235=', 82 * 235, ' A+ 70*150=', 70 * 150, ' 86*150=', 86 * 150, ' 40*150=', 40 * 150)
log('[1] 1/sqrt(598)=', float(1 / sqrt(598)), ' 1/sqrt(833)=', float(1 / sqrt(833)), ' 1/sqrt(966)=', float(1 / sqrt(966)), ' 1/sqrt(2164)=', float(1 / sqrt(2164)))
log('[1] critical window: 10001^(-1/3)=', float(mpf(10001) ** (-mpf(1) / 3)), ' 0.0015/1.25^12=', 0.0015 / 1.25 ** 12, ' (1.0307e-4)^-3=', 1.0307e-4 ** -3)
log('[1] 44*43 =', 44 * 43)
mp.dps = 30
et_half = E * mpf('0.5') * exp(-mpf('0.5') / mp.tan(mpf('0.5'))) / mp.sin(mpf('0.5'))
log('[1] log et(1/2) =', mp.nstr(mp.log(et_half), 10), ' (D: 0.126775...)')
log('[1] 166 k^(-1/6) e^(-0.1267k) at k=10001: exponent =', mp.nstr(mp.log(166) - mp.log(10001) / 6 - mpf('0.1267') * 10001, 8), ' (D: <= -1263)')
log('[1] pi/0.019 =', float(pi / mpf('0.019')))

# ---------- 2. tilt-sum ----------
def bor_q_sum(k):
    s = Fr(0)
    x = Fr(k, k + 1) ** (k - 1)
    for n in range(2, k + 2):
        s += Fr(n ** (n - 1), factorial(n)) * x ** n
    return s
vals = {k: bor_q_sum(k) for k in range(2, 61)}
log('[2] tilt-sum max over 2..60:', max(float(v) for v in vals.values()), ' at k=', max(vals, key=vals.get), ' k=2 value =', vals[2])
for k in (3, 10, 20, 42, 43):
    log('[2] k=%d sum=%.6f' % (k, float(vals[k])))
log('[2] all <1 for 2..60:', all(v < 1 for v in vals.values()))
def B2(k):
    k = mpf(k)
    return (1 - 1 / E) + (exp(mpf(3) / 2 + 1 / k) - 1) * 2 * (sqrt(k + 1) - 1) / (sqrt(2 * pi) * (k + 1))
log('[2] B_2(42)=', mp.nstr(B2(42), 7), ' B_2(43)=', mp.nstr(B2(43), 7), ' (D: 1.00229, 0.998553)')

# ---------- 3. prop-W thirteen ----------
mp.dps = 40
def eRen(m):  # e*Ren(m) = m^(m-1)/(e^(m-1) (m-1)!)  with m=r+1: (r+1)^r/(e^r r!)
    return mpf(m) ** (m - 1) / (E ** (m - 1) * factorial(m - 1))
def L(d): return 3130 * (eRen(d + 1) - mpf(60) * (d + 1) / (3131 + d))
def R(d): return 2 * (1 + sum(eRen(r + 1) + mpf(60) * (r + 1) / (3131 + d) for r in range(1, d)))
for d in range(1, 15):
    log('[3] d=%2d L=%s R=%s L>R=%s' % (d, mp.nstr(L(d), 7), mp.nstr(R(d), 5), L(d) > R(d)))

# ---------- 4. theorem-D base, m<=150 via last-car table ----------
N = 150
P = [1] + [(n + 1) ** (n - 1) for n in range(1, N + 1)]
C = [[comb(m, j) for j in range(m + 1)] for m in range(N)]
A = [[0] * (N + 1) for _ in range(N + 1)]
for l in range(N + 1):
    A[0][l] = 1
    for n in range(1, N + 1):
        A[n][l] = sum(C[n - 1][j] * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l] for j in range(n))
def b(n, l): return A[n][l] - (A[n][l - 1] if l >= 1 else 0)
log('[4] row n=4:', [b(4, l) for l in range(4)])
mp.dps = 30
def Psi(d): return sum(mpf(j) ** j * exp(-j) / factorial(j) for j in range(1, d + 1))
qs = {}
for m in range(3, N + 1):
    for d in range(1, floor(mpf(m) ** (mpf(2) / 3) / 2) + 1):
        if 8 * d ** 3 <= m * m:
            qs[(m, d)] = mpf(m) * b(m, m - d) / (P[m] * Psi(d))
log('[4] q(4,1)=', mp.nstr(qs[(4, 1)], 12), ' q(3,1)=', mp.nstr(qs[(3, 1)], 12))
q4 = {k: v for k, v in qs.items() if k[0] >= 4}
log('[4] m in 4..150: min q=', mp.nstr(min(q4.values()), 8), 'at', min(q4, key=q4.get), ' max q=', mp.nstr(max(q4.values()), 8), 'at', max(q4, key=q4.get),
    ' all in [0.856,1.392]:', all(mpf('0.856') <= v <= mpf('1.392') for v in q4.values()))

# ---------- 5. 11.2 표 vs 부록 D 「독립 재계산」 문자열 대조 ----------
files = ['부록D_장2.md', '부록D_장3.md', '부록D_장4.md', '부록D_장5A.md', '부록D_장5B.md', '부록D_장6.md']
items = {}
for f in files:
    txt = open(os.path.join(BASE, '장v2', f), encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([a-zA-Z0-9-]+)\}\}(.*?)(?=^### D\.|\Z)', txt, re.S | re.M):
        name, body = m.group(1), m.group(2)
        mm = re.search(r'\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n\n', body, re.S)
        grade = re.search(r'\*\*산술 등급\.\*\*\s*(.*?)\n', body)
        stmt = re.search(r'\*\*확인하는 진술\.\*\*\s*(.*?)\n', body)
        items[name] = dict(file=f, bracket=mm.group(1) if mm else None, text=mm.group(2).strip() if mm else None,
                           grade=grade.group(1).strip() if grade else None, body=body)
ch11 = open(os.path.join(BASE, '장v2', '장11.md'), encoding='utf-8').read()
rows = {}
for line in ch11.splitlines():
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        name = re.match(r'부록 D\.\{\{D:([a-zA-Z0-9-]+)\}\}', cells[0]).group(1)
        rows[name] = cells
log('[5] D items parsed:', len(items), ' table rows:', len(rows))
for name, it in items.items():
    if name not in rows:
        log('[5] NO TABLE ROW for', name); continue
    cells = rows[name]
    if len(cells) < 6:
        log('[5] row has', len(cells), 'cells for', name, cells); continue
    br_tbl, txt_tbl, grade_tbl = cells[4], cells[5], cells[2]
    if it['bracket'] != br_tbl:
        log('[5] BRACKET DIFF', name, '\n   D :', it['bracket'], '\n   11:', br_tbl)
    t_d = it['text']; t_t = txt_tbl
    if t_d != t_t:
        # locate first difference
        i = 0
        while i < min(len(t_d), len(t_t)) and t_d[i] == t_t[i]: i += 1
        log('[5] TEXT DIFF', name, 'at char', i, '\n   D :', t_d[max(0, i - 60):i + 80], '\n   11:', t_t[max(0, i - 60):i + 80])
    # 산술 등급: 표의 등급은 D 등급 줄의 첫 등급(들)
    g = it['grade']
    log('[5] grade', name, '| D:', g[:90], '| 11.2:', grade_tbl)

# ---------- 6. 자료 경로 존재 ----------
def resolve_record(prefix):
    m = re.match(r'records/(r[0-9a-f]{7})', prefix)
    if not m: return None
    cands = glob.glob(os.path.join(REC, m.group(1) + '*'))
    return cands[0] if cands else None
missing = []; checked = 0
for name, it in items.items():
    mat = re.search(r'\*\*자료\.\*\*\s*(.*?)\n\n', it['body'], re.S)
    if not mat: log('[6] no 자료 line', name); continue
    line = mat.group(1)
    paths = re.findall(r'`([^`]+)`', line)
    curdir = None
    for p in paths:
        p0 = p.split('(')[0].strip()
        if p0.startswith('records/'):
            rec = resolve_record(p0)
            rest = re.sub(r'^records/r[0-9a-f]{7}[^/]*/', '', p0)
            if rec is None: missing.append((name, p, 'record dir not found')); continue
            full = os.path.join(rec, rest.replace('/', os.sep))
            curdir = os.path.dirname(full)
        elif p0.startswith('원고_자료/'):
            full = os.path.join(BASE, p0.replace('/', os.sep)); curdir = os.path.dirname(full)
        elif '/' not in p0 and curdir and re.match(r'^[\w.\-*]+$', p0):
            full = os.path.join(curdir, p0)
        elif p0.startswith('code/') or p0.startswith('indep/') or p0.startswith('logs/') or p0.startswith('runs/') or p0.startswith('cert/') or p0.startswith('outputs/'):
            # relative to last 원고_자료 or record folder root
            base_dir = curdir
            # walk up to the 세션_재계산/<name> folder or record root
            while base_dir and not (os.path.basename(os.path.dirname(base_dir)) == '세션_재계산' or os.path.basename(base_dir) in ('evidence', 'review') or os.path.basename(os.path.dirname(base_dir)) == 'records'):
                nb = os.path.dirname(base_dir)
                if nb == base_dir: break
                base_dir = nb
            full = os.path.join(base_dir, p0.replace('/', os.sep))
        else:
            continue  # variable names etc.
        checked += 1
        if '*' in full:
            if not glob.glob(full): missing.append((name, p, full))
        elif not os.path.exists(full):
            # try the whole path as relative to curdir's parent chain
            alt = None
            d = curdir
            for _ in range(5):
                if d is None: break
                cand = os.path.join(d, p0.replace('/', os.sep))
                if os.path.exists(cand): alt = cand; break
                d = os.path.dirname(d)
            if alt is None: missing.append((name, p, full))
log('[6] paths checked:', checked, ' missing:', len(missing))
for m in missing: log('[6] MISSING', m[0], '|', m[1], '|', m[2])

open(sys.argv[1] if len(sys.argv) > 1 else 'P12_장5-6_out.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
