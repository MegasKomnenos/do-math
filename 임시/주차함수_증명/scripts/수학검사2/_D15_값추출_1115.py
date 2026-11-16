# -*- coding: utf-8 -*-
"""D.15(critical-window-rig) 자리표시자 값을 cert/*.json·summary_out.txt·rerun_launches.txt에서 뽑아 보여 준다(읽기 전용)."""
import glob, io, json, math, os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '원고_자료', '세션_재계산', 'critical_window_rerun')
R = os.path.abspath(R)
def fl(x, d):  # 내림
    f = 10 ** d
    return math.floor(x * f) / f
boxes = {}
for p in sorted(glob.glob(os.path.join(R, 'cert', '*.json'))):
    name = os.path.basename(p)[:-5]
    if name.endswith('_recert_first'):
        continue
    D = json.load(io.open(p, encoding='utf-8'))
    recs = D['records']
    mins = min(recs, key=lambda r: r['margin'])
    first = [r for r in recs if abs(r['xa'] - 1.4) < 1e-9]
    boxes[name] = dict(min=mins['margin'], cell=(mins['xa'], mins['xb']), E0=mins.get('E0'), B0=mins.get('B0'),
                       first=first[0]['margin'] if first else None, secs=D.get('secs'), build=D.get('build_secs'),
                       worker=D.get('worker'), ncell=len(recs), keys=list(mins.keys())[:12])
print('boxes', len(boxes), 'cells', sum(b['ncell'] for b in boxes.values()))
m = min(boxes.items(), key=lambda kv: kv[1]['min'])
M = max(boxes.items(), key=lambda kv: kv[1]['min'])
print('overall min', m[0], m[1]['min'], m[1]['cell'], 'E0', m[1]['E0'], 'B0', m[1]['B0'])
print('per-box min range', m[0], fl(m[1]['min'], 5), '..', M[0], fl(M[1]['min'], 5))
print('worst cells', sorted(set(b['cell'] for b in boxes.values())))
firsts = sorted((b['first'], n) for n, b in boxes.items() if b['first'] is not None)
print('first-cell margins smallest 3', firsts[:3], 'third smallest floor', fl(firsts[2][0], 2))
print('five first cells', {n: (boxes[n]['first'], fl(boxes[n]['first'], 3)) for n in ['A29', 'G06', 'G07', 'G08', 'G13']})
secs = [b['secs'] for b in boxes.values()]
print('secs sum', sum(secs), 'h', sum(secs) / 3600, 'per box min/max min', min(secs) / 60, max(secs) / 60)
print('workers', sorted(set(str(b['worker']) for b in boxes.values())))
print('sample keys', m[1]['keys'])
# 기록 대비: summary_table.md
st = io.open(os.path.join(R, 'summary_out.txt'), encoding='utf-8').read().splitlines()
neg, pos = [], []
for ln in st:
    cells = [c.strip() for c in ln.split('|')]
    if len(cells) > 6 and re.match(r'^[AG]\d\d$', cells[1]):
        d = cells[5].replace('+', '')
        try:
            v = float(d)
        except ValueError:
            continue
        (neg if v < 0 else pos).append((v, cells[1]))
print('neg', len(neg), sorted(neg)[:1], sorted(neg)[-1:], [n for _, n in sorted(neg, key=lambda t: t[1])])
print('pos', len(pos), sorted(pos)[:1], sorted(pos)[-1:])
lp = os.path.join(R, 'rerun_launches.txt')
if os.path.exists(lp):
    print('--- rerun_launches.txt ---')
    print(io.open(lp, encoding='utf-8').read()[-1500:])
