# -*- coding: utf-8 -*-
"""두 증명(정리 9:old-7-46, 정리 10:old-8-37)에서 라벨 인용을 따라 거슬러 올라간 폐포를 구해
11.3의 공유/고유 분류와 맞세운다. 블록 = 머리 줄부터 다음 머리/절 머리 직전(증명+뒤 준비 문단 포함; 과포함 가능).
식 번호 인용과 준비 문단을 거친 인용은 잡지 못하므로 결과는 사람이 읽고 판단한다."""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'
LAB = re.compile(r'\{\{(\d+[AB]?:[^}]+)\}\}')
blocks = {}
for f in sorted(glob.glob(ROOT + r'\장*.md')):
    cur = None
    for ln in open(f, encoding='utf-8').read().split('\n'):
        if re.match(r'#{2,4}\s+\d', ln): cur = None
        mh = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}', ln)
        if mh: cur = mh.group(2); blocks.setdefault(cur, '')
        if cur: blocks[cur] += ln + '\n'
edges = {k: set(LAB.findall(v)) - {k} for k, v in blocks.items()}
edges = {k: {x for x in v if x in blocks} for k, v in edges.items()}

def closure(start, extra_text=''):
    seen = set(); stack = list(LAB.findall(extra_text)) + [start]
    while stack:
        x = stack.pop()
        if x in seen or x not in blocks: continue
        seen.add(x); stack.extend(edges[x])
    return seen

ch10 = open(ROOT + r'\장10.md', encoding='utf-8').read()
sec107 = ch10[ch10.index('### 10.7'):]
c1 = closure('9:old-7-46')
c2 = closure('10:old-8-37', sec107)
print('closure1', len(c1), 'closure2', len(c2))
shared = c1 & c2; only1 = c1 - c2; only2 = c2 - c1
# 11.3 표 읽기
ch11 = open(ROOT + r'\장11.md', encoding='utf-8').read()
s = ch11.index('**공유 입력.**'); m1 = ch11.index('**첫째 증명의 고유 입력.**'); m2 = ch11.index('**둘째 증명의 고유 입력.**'); e = ch11.index('### 11.4')
def firstcol(seg):
    out = set()
    for ln in seg.split('\n'):
        if ln.startswith('| ') and not ln.startswith('| 입력'):
            out |= set(LAB.findall(ln.split(' | ')[0]))
    return out
T_sh = firstcol(ch11[s:m1]); T_1 = firstcol(ch11[m1:m2]); T_2 = firstcol(ch11[m2:e])
print('\n11.3 공유 입력 가운데 폐포상 공유가 아닌 것:')
for x in sorted(T_sh):
    tag = 'shared' if x in shared else ('only1' if x in only1 else ('only2' if x in only2 else 'NEITHER'))
    if tag != 'shared': print('  ', x, tag)
print('\n11.3 첫째 고유 가운데 폐포상 첫째 고유가 아닌 것:')
for x in sorted(T_1):
    tag = 'shared' if x in shared else ('only1' if x in only1 else ('only2' if x in only2 else 'NEITHER'))
    if tag != 'only1': print('  ', x, tag)
print('\n11.3 둘째 고유 가운데 폐포상 둘째 고유가 아닌 것:')
for x in sorted(T_2):
    tag = 'shared' if x in shared else ('only1' if x in only1 else ('only2' if x in only2 else 'NEITHER'))
    if tag != 'only2': print('  ', x, tag)
# 폐포에 있으나 표 어디에도 없는 진술(앞 장 것만; 9·10장 중간 진술은 설계상 제외)
alltab = T_sh | T_1 | T_2
def chap(x): return x.split(':')[0]
print('\n폐포 공유이나 표에 없는 앞 장(2–8장) 진술:')
print('  ', sorted(x for x in shared - alltab if chap(x) not in ('9', '10')))
print('\n폐포 첫째 고유이나 표에 없는 앞 장 진술:')
print('  ', sorted(x for x in only1 - alltab if chap(x) not in ('9', '10')))
print('\n폐포 둘째 고유이나 표에 없는 앞 장 진술:')
print('  ', sorted(x for x in only2 - alltab if chap(x) not in ('9', '10')))
# 왜 공유인가: 첫째 고유 표 항목이 둘째 폐포에 든 경로
def path_to(target, start, extra=''):
    from collections import deque
    prev = {}; q = deque(LAB.findall(extra) + [start])
    for x in list(q): prev.setdefault(x, None)
    while q:
        x = q.popleft()
        if x == target: break
        for y in edges.get(x, ()):
            if y not in prev: prev[y] = x; q.append(y)
    if target not in prev: return None
    p = [target]
    while prev[p[-1]] is not None: p.append(prev[p[-1]])
    return list(reversed(p))
for x in sorted(T_1):
    if x in c2: print('\n경로(둘째→', x, '):', path_to(x, '10:old-8-37', sec107))
for x in sorted(T_2):
    if x in c1: print('\n경로(첫째→', x, '):', path_to(x, '9:old-7-46'))

# ---- 거짓 간선(준비 문단의 언급)을 빼고 다시 센다 ----
print('\n==== 거짓 간선 제거 후 ====')
edges['7:column-lemma'].discard('9:old-7-45')
edges['2:old-2-44'].discard('2:old-2-39')
c1 = closure('9:old-7-46'); c2 = closure('10:old-8-37', sec107)
shared = c1 & c2; only1 = c1 - c2; only2 = c2 - c1
for x in sorted(T_1):
    if x in c2: print('첫째 고유가 둘째 폐포에:', x, path_to(x, '10:old-8-37', sec107))
for x in sorted(T_2):
    if x in c1: print('둘째 고유가 첫째 폐포에:', x, path_to(x, '9:old-7-46'))
for x in sorted(T_sh):
    if x not in shared: print('공유 표 항목이 폐포상 공유 아님:', x, 'in1' if x in c1 else '', 'in2' if x in c2 else '')
print('폐포 첫째 고유이나 표에 없는 앞 장 진술:', sorted(x for x in only1 - alltab if chap(x) not in ('9','10')))
print('폐포 둘째 고유이나 표에 없는 앞 장 진술:', sorted(x for x in only2 - alltab if chap(x) not in ('9','10')))
