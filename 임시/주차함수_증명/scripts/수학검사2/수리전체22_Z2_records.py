# 수리 전체22 Z2 — 기록의 감사 출력과 본문 식의 대조(읽기 전용; python -I)
# (1) 보조정리 4:hermite-nu(나)의 H_0..H_3 식이 기록 [r475ada3]·[r6b37c7e]의 감사 출력 g_coeffs와 같은가
# (2) 명제 4:analytic-transfer(다)의 표의 각 (K_1, 41<=nu<=nu_max)에서 감사가 쓴 omega의 범위와 최소 여유
import json, glob, os, re
from fractions import Fraction as Q
REC = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records'
os.chdir(REC)

def walk(o, path):
    if isinstance(o, dict):
        if 'g_coeffs' in o:
            yield path, o
        for k, v in o.items():
            yield from walk(v, path + [k])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + [i])

def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p

seen = {}; bad = 0; n = 0
for f in glob.glob('r475ada3*/evidence/peer/repro/work/audit/*.json') + glob.glob('r6b37c7e*/evidence/**/*.json', recursive=True):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    for path, o in walk(d, []):
        g = [[Q(c) for c in p] for p in o['g_coeffs']]
        nu = int((-g[1][0] - 26) / 4)
        n += 1
        e2 = [506 + 97*nu + 5*nu*nu, 168 + 16*nu, 12]
        e3 = [-(11016 + 3187*nu + 239*nu**2 + 6*nu**3), -(5362 + 762*nu + 26*nu*nu), -(594 + 36*nu), -16]
        ok = trim(g[0]) == [4] and trim(g[1]) == [-(26 + 4*nu), -8] and trim(g[2]) == e2 and trim(g[3]) == e3
        seen.setdefault(nu, []).append(ok)
        bad += (not ok)
print('g_coeffs records:', n, 'mismatch:', bad, 'nu from', min(seen), 'to', max(seen), 'distinct', len(seen))

vmax = {12000: 58, 13000: 79, 14000: 99, 15000: 102, 20000: 115, 30000: 132, 50000: 164, 100000: 228, 200000: 298, 500000: 435, 1000000: 590}
res = {}
for f in glob.glob('r6b37c7e*/evidence/peer/audit_rerun/rerun_audit_K*.txt') + glob.glob('r6b37c7e*/evidence/peer/out/rerun_audit_K14000_nu97_100.txt'):
    K = int(re.search('_K([0-9]+)', os.path.basename(f)).group(1))
    for m in re.finditer('nu=[+]([0-9]+): lam=([0-9.]+).*?margin=(-?[0-9.]+)', open(f, encoding='utf-8', errors='replace').read()):
        nu = int(m.group(1))
        if nu <= vmax[K]:
            res.setdefault(K, {})[nu] = (float(m.group(2)), float(m.group(3)))
for K in sorted(res):
    d = res[K]
    missing = [nu for nu in range(41, vmax[K] + 1) if nu not in d]
    print(K, 'pairs', len(d), 'missing', missing, 'omega', min(v[0] for v in d.values()), max(v[0] for v in d.values()), 'min margin', min(v[1] for v in d.values()))
