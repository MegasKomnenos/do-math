# 부록 B의 기록마다 record.json 주장의 by 값(작성자 구분)과 provenance.json의 구성을 모아 「기록마다 쓴 이는 둘」을 확인한다.
import re, io, sys, os, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
B = open(r'C:/math/임시/주차함수_증명/장v2/부록B.md', encoding='utf-8').read()
folders = re.findall(r'(?m)^[|] (r[0-9a-f]{7}) [|].*[|] `([0-9a-z]+)` [|]$', B)
agg = collections.Counter(); odd = []
keys = collections.Counter()
for rid, fo in folders:
    d = json.load(open(R+fo+'/record.json', encoding='utf-8'))
    bys = collections.Counter(c.get('by') for c in d.get('claims', []))
    agg[tuple(sorted(str(k) for k in bys))] += 1
    if set(bys) != {'producer', 'peer'}: odd.append((rid, dict(bys)))
    pv = R+fo+'/provenance.json'
    if os.path.exists(pv):
        p = json.load(open(pv, encoding='utf-8'))
        for k in (p.keys() if isinstance(p, dict) else []): keys[k] += 1
    rv = R+fo+'/review'
    if not os.path.isdir(rv) or not os.listdir(rv): odd.append((rid, 'review 비어 있음'))
print(agg)
for o in odd: print('  ', o)
print('provenance keys', dict(keys))
rid, fo = folders[0]
p = json.load(open(R+fo+'/provenance.json', encoding='utf-8'))
print(json.dumps(p, ensure_ascii=False)[:900])
