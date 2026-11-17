import re, sys, json, io
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = [o for o in json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8')) if not o['proof']]
H = {o['label']: o for o in heads}
KINDS = ["따름정리","보조정리","정의","정리","명제"]
which = sys.argv[1]
f = {"대응표":"대조v2/라벨_번호_대응표_1114.md","장부":"장부_v2.md","구조표":"구조표_v2.md","지도":"의존지도_v2.md"}[which]
L = open(W+f, encoding='utf-8').read().split('\n')
lo = int(sys.argv[2]) if len(sys.argv)>2 else 1
hi = int(sys.argv[3]) if len(sys.argv)>3 else len(L)
pat = re.compile(r'(따름정리|보조정리|정의|정리|명제)?\s?`?(\{\{|\()?(\d+):([A-Za-z][A-Za-z0-9\-′\']*)(\}\}|\))?`?')
dead = Counter(); kindbad = []
for ln in range(lo, hi+1):
    line = L[ln-1]
    for m in pat.finditer(line):
        kind, op, ch, lab, cl = m.groups()
        key = f"{ch}:{lab}"
        if key not in H:
            dead[(key, op or '')] += 1
            if op == '{{': print('DEAD-IN-BRACES', ln, key)
        elif kind and H[key]['kind'] != kind:
            # '정리' may be suffix of 보조정리/따름정리 - regex alternation order handles
            kindbad.append((ln, kind, key, H[key]['kind']))
print('kind mismatches:')
for k in kindbad: print('  ', k)
if len(sys.argv)>4:
    print('dead refs:', len(dead))
    for k,v in sorted(dead.items()): print('  ', k, v)
