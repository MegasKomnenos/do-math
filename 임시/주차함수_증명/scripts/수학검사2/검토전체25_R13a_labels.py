# -*- coding: utf-8 -*-
# R13a: labels cited in ledger 1.2 (lines 43-288) vs live heads / appendix D labels
import io, json, re, glob, os
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
heads = json.load(io.open(os.path.join(base, 'scripts', '수학검사2', '검토전체25_R13_heads.json'), encoding='utf-8'))
live = {}
for h in heads:
    live[(h['ch'], h['lab'])] = h
lines = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
# D labels: definitions in 부록D files
dlabs = {}
for f in sorted(glob.glob(os.path.join(base, '장v2', '부록D_장*.md'))):
    for i, l in enumerate(io.open(f, encoding='utf-8').read().split('\n'), 1):
        for m in re.finditer(r'\{\{D:([^}]+)\}\}', l):
            if l.lstrip().startswith('#') or l.lstrip().startswith('**D.'):
                dlabs.setdefault(m.group(1), []).append((os.path.basename(f), i))
print('D labels defined (heading/bold):', len(dlabs))
bad = 0
for n in range(43, 289):
    l = lines[n-1]
    for m in re.finditer(r'\{\{([0-9A-Za-z]+):([^}]+)\}\}', l):
        ch, lab = m.group(1), m.group(2)
        if ch == 'D':
            if lab not in dlabs:
                print('L%d D-label not found as heading: %s' % (n, lab)); bad += 1
        else:
            if (ch, lab) not in live:
                print('L%d dead label: {{%s:%s}}' % (n, ch, lab)); bad += 1
            else:
                h = live[(ch, lab)]
                # print kind preceding the label in ledger
                pre = l[max(0, m.start()-12):m.start()]
                k = re.search(r'(정리|보조정리|명제|따름정리|정의|관찰|주의|예)\s*`?$', pre)
                if k and k.group(1) != h['kind']:
                    print('L%d kind mismatch: ledger "%s" vs head "%s" for {{%s:%s}} (sec %s)' % (n, k.group(1), h['kind'], ch, lab, h['sec'])); bad += 1
print('issues', bad)
