# -*- coding: utf-8 -*-
"""F6 재실행이 끝난 뒤(cert/ 44개 + *_recert_first.json 5개, summary_out.txt, verify_exact_cover_out.txt) 부록 D.critical-window-rig 의
「결과」·「독립 재계산」, 5A 정리 old-5-13 증명 끝 문장, 재실행표 생성기(_gen_재실행표.py expect/time)와 _재실행표_여유.json 에 적을 새 값을
새 인증서에서 직접 세어 출력한다.  --apply 를 주면 부록D_장5A.md·_gen_재실행표.py·_재실행표_여유.json 의 해당 수치를 바꾼다(장5A.md 는 손대지 않음).
python -I 로 실행."""
import os, sys, json, glob, re, math, datetime
from fractions import Fraction as Fr
ROOT = r"C:\math\임시\주차함수_증명"
HERE = os.path.join(ROOT, '원고_자료', '세션_재계산', 'critical_window_rerun')
REC = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/ra4c01fca85d24f5cb35be1ec80d8e1c8/evidence/certificates'
sys.path.insert(0, HERE)
from boxes import all_boxes, RECERT
APPLY = '--apply' in sys.argv


def ex(s):
    neg = s.startswith('-'); s = s.lstrip('-'); man, e = s.split('*2^'); v = Fr(int(man)) * Fr(2) ** int(e); return -v if neg else v


def used_cells(D, R):
    out = []
    for r in D['records']:
        if r['margin'] > 0: out.append(r)
        elif R is not None: out += [q for q in R['records'] if q['xa'] >= r['xa'] - 1e-9 and q['xb'] <= r['xb'] + 1e-9]
    return out


names = [n for n, _, _ in all_boxes()]
certs = {}
for n in names:
    p = os.path.join(HERE, 'cert', n + '.json')
    if not os.path.exists(p):
        print('missing', p); sys.exit(1)
    certs[n] = json.load(open(p))
    assert 'error' not in certs[n], n
rec = {}
for n in RECERT:
    p = os.path.join(HERE, 'cert', n + '_recert_first.json')
    rec[n] = json.load(open(p)) if os.path.exists(p) else None
ncell = sum(len(D['records']) for D in certs.values())
# 최소 여유(정확 이진값)와 셀
worst = min(((ex(r['margin_exact']), n, r) for n, D in certs.items() for r in D['records']), key=lambda t: t[0])
permin = {n: min(D['records'], key=lambda r: r['margin']) for n, D in certs.items()}
allworst_cell = all(permin[n]['k'] == 42 for n in names)
lo_box = min(names, key=lambda n: permin[n]['margin']); hi_box = max(names, key=lambda n: permin[n]['margin'])
first = {n: certs[n]['records'][0]['margin'] for n in names}
small_first = sorted(first.items(), key=lambda t: t[1])
# 기록 인증서와의 차(summarize.py 와 같은 셈: 실제로 쓰인 셀들의 최소)
diffs = {}
for n in names:
    k = int(n[1:]); sub = 'cert2' if n[0] == 'A' else 'cert3'
    Do = json.load(open(os.path.join(REC, sub, 'ubox_%02d.json' % k)))
    rpo = os.path.join(REC, sub, 'ubox_%02d_recert_first.json' % k)
    Ro = json.load(open(rpo)) if os.path.exists(rpo) else None
    mn = min(used_cells(certs[n], rec.get(n)), key=lambda r: r['margin'])['margin']
    mno = min(used_cells(Do, Ro), key=lambda r: r['margin'])['margin']
    diffs[n] = mn - mno
neg = [n for n in names if diffs[n] < 0]; pos = [n for n in names if diffs[n] >= 0]
# 시간
secs = [certs[n]['secs'] + (certs[n].get('build_secs') or 0) * 0 for n in names]     # 'secs' already includes the build in rerun_boxes (t0 before build)
tot = sum(certs[n]['secs'] for n in names); rsecs = sum(R['secs'] for R in rec.values() if R)
t_first = min(certs[n]['t_start'] for n in names); t_last = max([certs[n]['t_end'] for n in names] + [R['t_end'] for R in rec.values() if R])
workers = sorted(set(certs[n].get('worker') for n in names))
wall = t_last - t_first
A00 = certs['A00']['records'][42]


def g(x, d=3):
    return ('%.' + str(d) + 'g') % x


def fmt_range(vals):
    vals = sorted(vals)
    def sci(v):
        e = int(math.floor(math.log10(abs(v)))); m = v / 10 ** e
        return m, e
    (m1, e1), (m2, e2) = sci(vals[0]), sci(vals[-1])
    if e1 == e2:
        return '$%.1f$–$%.1f\\times10^{%d}$' % (m1, m2, e1)
    return '$%.1f\\times10^{%d}$–$%.1f\\times10^{%d}$' % (m1, e1, m2, e2)


def boxlist(ns):
    # 연속 번호 묶기: A21, A23–A28, G09–G12 꼴
    out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1][0] == ns[i][0] and int(ns[j + 1][1:]) == int(ns[j][1:]) + 1: j += 1
        out.append(ns[i] if j == i else '%s–%s' % (ns[i], ns[j])); i = j + 1
    return ', '.join(out)


print('=== 새 값 (%s) ===' % datetime.datetime.now().isoformat(timespec='seconds'))
print('셀 수', ncell, '; 최소 여유 %.7f (%s, cell %d [%.1f,%.1f]) ; 모든 상자 최악 셀이 [9.8,10]:' % (float(worst[0]), worst[1], worst[2]['k'], worst[2]['xa'], worst[2]['xb']), allworst_cell)
print('상자별 최소 여유 범위: %.5f (%s) – %.5f (%s)' % (permin[lo_box]['margin'], lo_box, permin[hi_box]['margin'], hi_box))
print('A00 [9.8,10] 셀: E0=[%.4f,%.4f] B0=[%.4f,%.4f]' % (A00['E0'][0], A00['E0'][1], A00['B0'][0], A00['B0'][1]))
print('첫 셀 여유: 가장 작은 셋', small_first[:3], '; 나머지 최소 %.3f' % small_first[3][1])
print('기록 대비: 작은 상자 %d개 (%s): %s ; 큰 상자 %d개: %s' % (len(neg), boxlist(neg), fmt_range([-diffs[n] for n in neg]) if neg else '-', len(pos), fmt_range([diffs[n] for n in pos])))
print('시간: 작업자 %s ; 상자별 합 %.1f시간 ; 상자당 %d–%d분 ; 벽시계 %d시간 %d분 (재인증 포함) ; 재인증 합 %.1f시간' % (workers, tot / 3600, min(certs[n]['secs'] for n in names) // 60, -(-max(certs[n]['secs'] for n in names) // 60), wall // 3600, (wall % 3600) // 60, rsecs / 3600))
print('재인증(첫 셀, cw=0.2 통과 여유 / h=0.1 재인증 최소 여유):', {n: (round(first[n], 3), round(rec[n]['worst_margin'], 3) if rec[n] else None) for n in RECERT})
vo = open(os.path.join(HERE, 'verify_exact_cover_out.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(HERE, 'verify_exact_cover_out.txt')) else ''
print('verify_exact_cover: ALL CHECKS PASSED' if 'ALL CHECKS PASSED' in vo else 'verify_exact_cover: NOT PASSED / not run')

m6 = '%.6f' % float(worst[0])          # 아래로 자른 여섯 자리가 아니라 반올림; 부록 D 는 0.001827 꼴(여섯째 자리까지)
m6 = ('%.6f' % (math.floor(float(worst[0]) * 1e6) / 1e6))
print('\n--- 부록 D 「결과」 문장 ---')
res = ('**결과.** 모든 상자·셀($%s$개)의 여유가 양수다. 최소 여유는 $%s$(%s, $\\hat x\\in[9.8,10]$)이다. 여유는 $\\hat x$와 함께 줄어 최악 셀은 모든 상자에서 $\\hat x\\in[9.8,10]$이고, '
       '상자별 최소 여유는 $%.5f$(%s)에서 $%.5f$(%s) 사이다(예: A00의 그 셀에서 $\\Upsilon_{e,0}\\in[%.4f,%.4f]$, $\\Upsilon_{B,0}\\in[%.4f,%.4f]$). '
       '첫 셀 $[1.4,1.6]$의 여유는 가장 작은 %s에서 $%.3f$, %s에서 $%.3f$, 나머지 상자에서 $%.2f$ 이상이다.') % (
    '{:,}'.format(ncell).replace(',', '{,}'), m6, worst[1], math.floor(permin[lo_box]['margin'] * 1e5) / 1e5, lo_box, math.floor(permin[hi_box]['margin'] * 1e5) / 1e5, hi_box,
    math.floor(A00['E0'][0] * 1e4) / 1e4, math.ceil(A00['E0'][1] * 1e4) / 1e4, math.floor(A00['B0'][0] * 1e4) / 1e4, math.ceil(A00['B0'][1] * 1e4) / 1e4,
    small_first[0][0], math.floor(small_first[0][1] * 1e3) / 1e3, small_first[1][0], math.floor(small_first[1][1] * 1e3) / 1e3, math.floor(small_first[2][1] * 1e2) / 1e2)
print(res)
print('\n--- 부록 D 「독립 재계산」의 재실행 문장(교체 범위: 「이 글을 쓰며 …」부터 「… 크다.」까지, 그리고 재인증 괄호) ---')
rerun = ('이 글을 쓰며 위의 알고리즘을 그대로 구현한 하나의 코드로 $44$개 상자를 모두 다시 돌렸다(작업자 $%d$개; 상자별 소요 시간의 합 $%.1f$시간, 상자당 $%d$–$%d$분, 벽시계 $%d$시간 $%d$분). '
         '모든 셀의 여유가 양수이고 최솟값은 $%s$(%s, $\\hat x\\in[9.8,10]$)이다. 상자별 최소 여유는 기록의 인증서가 저장한 값보다 $%d$개 상자(%s)에서 %s 작고 나머지 $%d$개 상자에서 %s 크다.') % (
    len(workers), tot / 3600, min(certs[n]['secs'] for n in names) // 60, -(-max(certs[n]['secs'] for n in names) // 60), (t_last - t_first) // 3600, ((t_last - t_first) % 3600) // 60,
    m6, worst[1], len(neg), boxlist(neg), fmt_range([-diffs[n] for n in neg]) if neg else '', len(pos), fmt_range([diffs[n] for n in pos]))
print(rerun)
rc = '상자 A29, G06, G07, G08, G13의 첫 셀은 $\\mathrm{cw}=0.2$에서 통과한 것(여유 %s)에 더해, ' % ', '.join('$%.3f$' % (math.floor(first[n] * 1e3) / 1e3) for n in ('A29', 'G06', 'G07', 'G08', 'G13'))
rc2 = '최소 여유 각각 %s; 다섯 번 합쳐 $%.1f$시간' % (', '.join(('$%.3f$' % (math.floor(rec[n]['worst_margin'] * 1e3) / 1e3)) if rec[n] else '?' for n in ('A29', 'G06', 'G07', 'G08', 'G13')), rsecs / 3600)
print(rc); print(rc2)
print('\n--- 5A 정리 old-5-13 증명 끝 문장(Z3 몫) ---')
_v = float(str(m6).replace('$', ''))
print('장5A 844행은 「최소 여유도 $0.0018$보다 크다」로 적혀 있어 손대지 않는다(E2, 2026-11-16). 확인: 최솟값 %s > 0.0018 -> %s' % (m6, _v > 0.0018))
assert _v > 0.0018, '재인증 최솟값이 0.0018 이하 — 장5A 844행을 다시 본다'
print('\n--- _gen_재실행표.py expect / time ---')
expect = '모든 셀 여유 양수; 최소 여유 $%s$(%s, $\\hat x\\in[9.8,10]$); verify_exact_cover: ALL CHECKS PASSED' % (m6, worst[1])
tm = '상자별 소요 시간의 합 $%.1f$시간, 상자당 $%d$–$%d$분, 벽시계 $%d$시간 $%d$분(작업자 둘)' % (tot / 3600, min(certs[n]['secs'] for n in names) // 60, -(-max(certs[n]['secs'] for n in names) // 60), (t_last - t_first) // 3600, ((t_last - t_first) % 3600) // 60)
print(expect); print(tm)
print('\n--- _재실행표_여유.json ---')
yj = '최소 여유 $%s$(%s, $\\hat x\\in[9.8,10]$; 기준은 양수)' % (m6, worst[1])
print(yj)

if APPLY:
    pD = os.path.join(ROOT, '장v2', '부록D_장5A.md')
    s = open(pD, encoding='utf-8').read()
    s2 = re.sub(r'\*\*결과\.\*\* 모든 상자·셀\(\$1\{,\}892\$개\)의 여유가 양수다\..*?나머지 상자에서 \$[0-9.]+\$ 이상이다\.', lambda m: res, s, count=1, flags=re.S)
    s2 = re.sub(r'이 글을 쓰며 위의 알고리즘을 그대로 구현한 하나의 코드로 \$44\$개 상자를 모두 다시 돌렸다\(.*?크다\.', lambda m: rerun, s2, count=1, flags=re.S)
    s2 = re.sub(r'상자 A29, G06, G07, G08, G13의 첫 셀은 \$\\mathrm\{cw\}=0\.2\$에서 통과한 것\(여유 [^)]*\)에 더해, ', lambda m: rc, s2, count=1)
    s2 = re.sub(r'최소 여유 각각 \$[0-9.]+\$, \$[0-9.]+\$, \$[0-9.]+\$, \$[0-9.]+\$, \$[0-9.]+\$; 다섯 번 합쳐 \$[0-9.]+\$시간', lambda m: rc2, s2, count=1)
    assert s2 != s, 'no change applied to 부록D_장5A.md'
    open(pD, 'w', encoding='utf-8').write(s2); print('applied: 부록D_장5A.md')
    pg = os.path.join(ROOT, 'scripts', '_gen_재실행표.py')
    s = open(pg, encoding='utf-8').read()
    s2 = re.sub(r'(    "critical-window-rig": dict\(.*?expect=)"[^"]*"', lambda m: m.group(1) + '"' + expect.replace('\\', '\\\\') + '"', s, count=1, flags=re.S)
    s2 = re.sub(r'(    "critical-window-rig": dict\(.*?time=)"[^"]*"', lambda m: m.group(1) + '"' + tm.replace('\\', '\\\\') + '"', s2, count=1, flags=re.S)
    assert s2 != s; open(pg, 'w', encoding='utf-8').write(s2); print('applied: _gen_재실행표.py')
    pj = os.path.join(ROOT, 'scripts', '_재실행표_여유.json')
    J = json.load(open(pj, encoding='utf-8')); J['critical-window-rig'] = yj
    open(pj, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2) + '\n'); print('applied: _재실행표_여유.json')
