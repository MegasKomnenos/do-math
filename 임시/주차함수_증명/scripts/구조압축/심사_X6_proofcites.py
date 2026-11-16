# -*- coding: utf-8 -*-
"""심사 X6 — 「…의 증명에서 보았듯」류, 곧 다른 진술의 증명 안 사실을 근거로 끌어 쓰는 인용을 모은다.
출력: 심사_X6_proofcites.txt (자리마다 파일:행, 숙주 진술, 인용된 진술, 발췌)
패턴:
  A  {{라벨}}(가)?의 증명(에서|과 같|이|에 쓰|에서처럼|으로|의|에 있|안|을 거쳐|에 따라|처럼)
  B  (그|같은|위|앞) 정리|보조정리|명제|따름정리의 증명 / 그 증명에서 / 같은 증명
  C  N.M절의 증명 등 절 단위
장11은 표라서 따로 센다.
"""
import re, json, os
from collections import defaultdict
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, '장v2')
g = json.load(open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_graph.json'), encoding='utf-8'))
stmts = g['statements']
num = {}; cnt = {}
for s in stmts:
    ch = s['label'].split(':')[0]
    if ch == 'D': continue
    cnt[ch] = cnt.get(ch, 0) + 1
    num[s['label']] = f"{ch}.{cnt[ch]}"
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
def host_of(f, n):
    for t in stmts:
        if t['file'] == f and t['line'] <= n <= t['body_end']:
            return t['label'], ('머리' if n == t['line'] else '본문')
        for d in t['deferred']:
            if d[0] == f and d[1] <= n <= d[2]:
                return t['label'], '미룬 증명'
    return None, '산문'
PA = re.compile(r'\{\{([^}]+)\}\}((?:\([가-힣ivx′]+\))*)의 증명(?!됨)')
PB = re.compile(r'(그|같은|위의|앞의|이|두|세|각) (?:정리|보조정리|명제|따름정리)?의? ?증명(에서|과 같|이 |에 쓰|안|의 )')
PC = re.compile(r'(\d+\.\d+(?:\.\d+)?절)의 증명')
PD = re.compile(r'(?<!의 )증명에서 보았듯|증명 안에서|증명이 보인|증명이 세운|증명에서 세운|증명에서 적은|증명에서 둔|증명에서 본|증명이 준|증명에서 얻은|증명에서 쓴|증명에 나오는|증명에 있는')
rows = []
for f in FILES:
    lines = open(os.path.join(CH, f), encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines):
        h, kind = host_of(f, i+1)
        for m in PA.finditer(l):
            a = max(0, m.start()-80); b = min(len(l), m.end()+90)
            rows.append(dict(f=f, n=i+1, kind=kind, host=h, cited=m.group(1), part=m.group(2), pat='A', snip=l[a:b]))
        for m in PB.finditer(l):
            a = max(0, m.start()-120); b = min(len(l), m.end()+90)
            rows.append(dict(f=f, n=i+1, kind=kind, host=h, cited='(대명사)', part='', pat='B', snip=l[a:b]))
        for m in PC.finditer(l):
            a = max(0, m.start()-80); b = min(len(l), m.end()+90)
            rows.append(dict(f=f, n=i+1, kind=kind, host=h, cited=m.group(1), part='', pat='C', snip=l[a:b]))
        for m in PD.finditer(l):
            # A와 겹치면 건너뜀
            if any(r['f']==f and r['n']==i+1 and r['pat']=='A' and abs(r['snip'].find('증명')-0)>=0 for r in rows if r['pat']=='A' and r['n']==i+1 and r['f']==f) and '{{' in l[max(0,m.start()-40):m.start()]:
                continue
            a = max(0, m.start()-120); b = min(len(l), m.end()+90)
            rows.append(dict(f=f, n=i+1, kind=kind, host=h, cited='(무명)', part='', pat='D', snip=l[a:b]))
out = []
byf = defaultdict(int); hosts = set(); hostsA = set()
for r in rows:
    if r['f'] == '장11.md': continue
    byf[(r['f'], r['pat'])] += 1
    if r['host']: hosts.add(r['host'])
    if r['pat'] == 'A' and r['host']: hostsA.add(r['host'])
out.append('# 패턴별·장별 건수(장11 제외)')
for k in sorted(byf): out.append(f'{k[0]}\t{k[1]}\t{byf[k]}')
A = [r for r in rows if r['pat']=='A' and r['f']!='장11.md']
out.append(f'# A형(라벨 명시) 총 {len(A)}건, 숙주 진술 {len(hostsA)}개(산문 제외); 전체 패턴 숙주 {len(hosts)}개')
out.append(f'# 장11의 A형: {sum(1 for r in rows if r["pat"]=="A" and r["f"]=="장11.md")}건')
out.append('')
for pat in 'ABCD':
    out.append(f'===== 패턴 {pat}')
    k = 0
    for r in rows:
        if r['pat'] != pat: continue
        k += 1
        hn = (num.get(r['host'], '') + ' ' + r['host']) if r['host'] else '-'
        cn = (num.get(r['cited'], '') + ' ' + r['cited']) if r['cited'] in num else r['cited']
        out.append(f"{pat}{k:03d} {r['f']}:{r['n']} [{r['kind']}; 숙주 {hn}] → {cn}{r['part']} | {r['snip']}")
open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_proofcites.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:40]))
