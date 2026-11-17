# -*- coding: utf-8 -*-
# 뺌 행 주석이 가리키는 진술의 부분 (가)(나)…·(ㄱ)(ㄴ)…·(i)(ii)가 그 진술에 있는지 본다(자리 찾기 전용).
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
heads = json.load(io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_heads.json'), encoding='utf-8'))
txt = {}
cache = {}
for idx, h in enumerate(heads):
    f = h['file']
    if f not in cache:
        cache[f] = io.open(os.path.join(base, '장v2', f + '.md'), encoding='utf-8').read().split('\n')
    L = cache[f]
    end = len(L)
    for h2 in heads[idx + 1:]:
        if h2['file'] == f:
            end = h2['line'] - 1
            break
    txt[h['ch'] + ':' + h['lab']] = '\n'.join(L[h['line'] - 1:end])
src = sys.argv[1]
lo, hi = int(sys.argv[2]), int(sys.argv[3])
S = io.open(os.path.join(base, src), encoding='utf-8').read().split('\n')
pat = re.compile(r'`\{?\{?([0-9]+:[A-Za-z0-9\-]+)\}?\}?`((?:\((?:[가-힣]|[ㄱ-ㅎ]|[ivx]+|[a-z])\))+)')
seen = set()
for i in range(lo - 1, hi):
    for m in pat.finditer(S[i]):
        k = m.group(1)
        parts = re.findall(r'\(([^)]+)\)', m.group(2))
        if k not in txt:
            continue
        for p in parts:
            key = (k, p)
            if key in seen: continue
            seen.add(key)
            if ('(' + p + ')') not in txt[k]:
                print('MISSING part', i + 1, k, '(' + p + ')')
print('checked', len(seen))
