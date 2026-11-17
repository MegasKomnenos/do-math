# 부록 C 둘째 표의 「기록 [r…]의 <이름>」 가운데 ASCII 이름(주장 id 꼴)이 그 기록의 record.json·exposition.md에 실제로 있는지 본다.
import re, io, sys, os, glob, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
C = open(base+'부록C.md', encoding='utf-8').read().split('\n')
a = next(i for i,l in enumerate(C) if l.startswith('### 기록이 결과에'))
b = next(i for i,l in enumerate(C) if l.startswith('### 기록의 글자와'))
cache = {}
def rec(rid):
    if rid not in cache:
        d = glob.glob(R + rid + '*')[0]
        cache[rid] = open(d+'/record.json', encoding='utf-8').read() + '\n' + open(d+'/exposition.md', encoding='utf-8').read()
    return cache[rid]
nchk = 0; bad = 0
for i in range(a, b):
    l = C[i]
    if not l.startswith('| 기록 ['): continue
    cell = l.strip().strip('|').split(' | ')[0].strip()
    # 「기록 [rid]의 … , 기록 [rid2]의 …」로 가른다
    parts = re.split(r'(?=기록 \[r[0-9a-f]{7}\])', cell)
    for p in parts:
        m = re.match(r'기록 \[(r[0-9a-f]{7})\]\s*(?:의)?\s*(.*)', p)
        if not m: continue
        rid, names = m.groups()
        txt = rec(rid)
        for nm in re.findall(r'[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+', names):
            nchk += 1
            if nm not in txt:
                bad += 1; print(f'[C {i+1}] {rid}: 「{nm}」 기록에 없음')
print('확인한 ASCII 이름', nchk, '없음', bad)
