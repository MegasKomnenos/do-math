# -*- coding: utf-8 -*-
"""A12: 의존 지도(metadata.json)에서 부록 D 항목의 진술 노드가 두 증명(9.51, 10.36)과 주 정리(1.5)에
닿는지, 직접 소비 노드는 무엇인지 센다. 라벨→번호는 대조v2/라벨_번호_대응표_1114.md."""
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
lab2num = {}
for ln in open(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8'):
    m = re.match(r'^\|\s*`\{\{([^}]+)\}\}`\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|', ln)
    if m:
        lab2num[m.group(1)] = (m.group(4).strip(), m.group(2).strip(), m.group(3).strip())
meta = json.load(open(os.path.join(ROOT, 'dependency_map', '작업', '빌드', 'ko', 'metadata.json'), encoding='utf-8'))
cards = meta['cards']; edges = meta['edges']
nodes = set(cards.keys())
succ = {n: set() for n in nodes}; pred = {n: set() for n in nodes}
etypes = {}
for e in edges:
    s, t = e['source'], e['target']
    if s in nodes and t in nodes:
        succ[s].add(t); pred[t].add(s)
        etypes[(s, t)] = e.get('type')
def reach(start, goal):
    seen = {start}; st = [start]
    while st:
        x = st.pop()
        if x == goal: return True
        for y in succ[x]:
            if y not in seen: seen.add(y); st.append(y)
    return False
def ancestors(goal):
    seen = {goal}; st = [goal]
    while st:
        x = st.pop()
        for y in pred[x]:
            if y not in seen: seen.add(y); st.append(y)
    return seen
A1 = ancestors('9.51'); A2 = ancestors('10.36'); A0 = ancestors('1.5')
print('노드 수', len(nodes), '선 수', len(edges))
print('9.51 조상', len(A1), '10.36 조상', len(A2), '1.5 조상', len(A0))
items = json.load(open(os.path.join(ROOT, 'scripts', '구조압축', '심사_A12_장부.json'), encoding='utf-8'))
head = {}
for n, c in cards.items():
    head[n] = ' '.join(c['rows'][0]['lines'])[:70] if c.get('rows') else ''
for it in items:
    print('=' * 90); print(it['label'])
    for lab in it['head_refs']:
        num = lab2num.get(lab, ('?', '?', '?'))[0]
        if num not in nodes:
            print(f'  {lab} = {num}  (지도에 없음/접힘)'); continue
        tag = ('첫째' if num in A1 else '-') + '/' + ('둘째' if num in A2 else '-') + '/' + ('주정리' if num in A0 else '-')
        outs = sorted(succ[num], key=lambda s: [float(x) if x.replace('.','').isdigit() else x for x in s.split('.')[:1]] + [s])
        print(f'  {lab} = {num} [{tag}] -> 직접 소비 노드: ' + ', '.join(f'{o}({etypes.get((num,o))})' for o in outs))
# 숫자→라벨 역표 저장
json.dump(lab2num, open(os.path.join(ROOT, 'scripts', '구조압축', '심사_A12_lab2num.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
