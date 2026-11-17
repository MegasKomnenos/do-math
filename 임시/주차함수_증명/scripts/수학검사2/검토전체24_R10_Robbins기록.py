# 부록 B의 기록 전부에서 Robbins 나머지를 적은 글자(ε_m 꼴)와 낱말(「Robbins 오차」 등)을 찾는다(부록 C 낱말 표의 Robbins 나머지 행 확인용).
import re, io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
B = open(r'C:/math/임시/주차함수_증명/장v2/부록B.md', encoding='utf-8').read()
folders = re.findall(r'(?m)^[|] (r[0-9a-f]{7}) [|].*[|] `([0-9a-z]+)` [|]$', B)
bs = chr(92)
pat_eps = re.compile('[εϵ]_[{]?m[}]?|' + bs + bs + '(?:var)?epsilon_[{]?m[}]?')
tot = 0
for rid, fo in folders:
    hits = []
    for f in glob.glob(R+fo+'/**/*.md', recursive=True):
        try: t = open(f, encoding='utf-8').read()
        except Exception: continue
        for m in pat_eps.finditer(t):
            ctx = t[max(0, m.start()-80):m.end()+80].replace('\n', ' ')
            hits.append((os.path.relpath(f, R+fo), ctx))
    if hits:
        tot += 1
        print('==', rid, len(hits))
        for h in hits[:2]: print('   ', h[0], '|', h[1])
print('ε_m 꼴이 든 기록 수', tot)
for rid, fo in folders:
    for f in glob.glob(R+fo+'/**/*.md', recursive=True):
        try: t = open(f, encoding='utf-8').read()
        except Exception: continue
        for w in ['Robbins 오차', 'Robbins 나머지', 'Robbins 보정', 'Robbins remainder', 'Stirling 보정', 'Stirling 나머지', 'Stirling 오차']:
            if w in t: print('낱말', w, rid, os.path.relpath(f, R+fo))
