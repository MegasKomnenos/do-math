# -*- coding: utf-8 -*-
"""H11: 부록 B의 「기록의 시각」·순서·판 번호를 지식 저장소 events/<id>.json의 at·sequence와 대조한다(KST)."""
import re, os, sys, io, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
ev = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\events'
KST = datetime.timezone(datetime.timedelta(hours=9))
rows = []
for line in open(os.path.join(root, '부록B.md'), encoding='utf-8'):
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) == 4 and re.fullmatch(r'r[0-9a-f]{7}', cells[0]):
        rows.append((cells[0], cells[1], cells[3].strip('`')))
bad = 0; prev = None; seqs = []
for rid, when, folder in rows:
    p = os.path.join(ev, folder + '.json')
    if not os.path.exists(p):
        print('no event', rid); bad += 1; continue
    d = json.load(open(p, encoding='utf-8'))
    t = datetime.datetime.fromtimestamp(d['at'], KST).strftime('%m-%d %H:%M')
    seqs.append((rid, d.get('sequence')))
    if t != when:
        print('TIME', rid, 'B:', when, 'event:', t); bad += 1
    if prev and d['at'] < prev:
        print('ORDER', rid); bad += 1
    prev = d['at']
print('rows', len(rows), 'mismatches', bad)
print('max sequence among cited:', max(s for _, s in seqs), 'rfc69320 seq:', dict(seqs)['rfc69320'])
