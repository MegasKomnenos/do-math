# -*- coding: utf-8 -*-
import re, sys, io, json, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
heads = json.load(io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_heads.json'), encoding='utf-8'))
hl = {h['ch'] + ':' + h['lab']: h for h in heads}
alltext = {}
for p in glob.glob(os.path.join(base, '장v2', '*.md')):
    alltext[os.path.basename(p)] = io.open(p, encoding='utf-8').read()
live, dead = [], []
for line in io.open(os.path.join(base, '대조v2/라벨_번호_대응표_1114.md'), encoding='utf-8'):
    if line.startswith('| `{{'):
        live.append([c.strip() for c in line.strip().strip('|').split(' | ')])
    elif line.startswith('| `('):
        dead.append([c.strip() for c in line.strip().strip('|').split(' | ')])
print(len(live), len(dead))
# (a) removed labels absent
for r in dead:
    lab = r[0].strip('`()')
    for fn, t in alltext.items():
        if '{{' + lab + '}}' in t:
            print('DEAD LABEL PRESENT', lab, fn, t.count('{{' + lab + '}}'))
    # (b) referenced labels
    for ref in re.findall(r'`(\(?[0-9A-Za-z]+:[^`]+?\)?)`', r[2] + ' ' + r[3]):
        if ref.startswith('('):
            continue
        ref2 = ref.strip('{}')
        if ref2 not in hl:
            print('REF MISSING', lab, '->', ref)
    m = re.match(r'옮김 → `\{\{([^}]+)\}\}` (\S+)', r[3])
    if m:
        tgt, num = m.groups()
        if tgt not in hl: print('MOVE TARGET MISSING', lab, tgt)
        elif hl[tgt]['num'] != num: print('MOVE NUM', lab, tgt, num, hl[tgt]['num'])
        # live row back-reference
        lr = [x for x in live if x[0] == '`{{' + tgt + '}}`'][0]
        if lab not in lr[4] or r[4] not in lr[4]:
            print('MOVE BACKREF', lab, lr[4], r[4])
        if lr[1] != r[1] or lr[2] != r[2]: print('MOVE kind/name differ', lab, '|', r[1], r[2], '|', lr[1], lr[2])
# live rows with 옛
for lr in live:
    if '옛' in lr[4]:
        m = re.search(r'옛 `\(([^)]+)\)` (\S+)', lr[4])
        if not m: print('ODD', lr); continue
        d = [x for x in dead if x[0] == '`(' + m.group(1) + ')`']
        if not d: print('NO DEAD ROW for', lr[0], lr[4])
# (c) 15:52 numbering completeness
nums = {}
for r in live + dead:
    c = r[4]
    m = re.search(r'(\d+)\.(\d+)$', c)
    if c == '사본에 없음': continue
    if not m: print('ODD 1552', r[0], c); continue
    if '옛' in c and r in live: continue  # counted via dead row
    nums.setdefault(int(m.group(1)), []).append((int(m.group(2)), r[0]))
for ch in sorted(nums):
    s = sorted(nums[ch])
    ns = [x[0] for x in s]
    miss = [i for i in range(1, max(ns) + 1) if i not in ns]
    dup = sorted(set(i for i in ns if ns.count(i) > 1))
    print(ch, 'max', max(ns), 'count', len(ns), 'missing', miss, 'dup', dup)
# order of 15:52 numbers among live rows per chapter-of-origin monotone?
print('사본에 없음 rows:', sum(1 for r in live if r[4] == '사본에 없음'))
print('dead kinds: 옮김', sum(1 for r in dead if r[3].startswith('옮김')), '뺌', sum(1 for r in dead if r[3].startswith('뺌')))
