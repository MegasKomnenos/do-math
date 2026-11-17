# 검토전체24 R7a: 장7B 1-241행에서 수식 바로 뒤 조사를 뽑아 눈으로 볼 목록을 만든다 (자리를 찾는 용도)
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = io.open('장v2/장7B.md', encoding='utf-8').read().split('\n')[:241]
pat = re.compile(r'[$]([^$]{1,80})[$](이|가|은|는|을|를|와|과|으로|로|이다|다|이고|고|이며|며|이면|면|이라|라)(?=[\s,.)」])')
seen = {}
for i, l in enumerate(L, 1):
    if l.strip().startswith('$$'):
        continue
    for m in pat.finditer(l):
        body = m.group(1)
        tail = body[-14:]
        key = (tail, m.group(2))
        seen.setdefault(key, []).append(i)
for (tail, josa), lines in sorted(seen.items(), key=lambda kv: kv[0][0][::-1]):
    print(repr(tail), josa, lines[:6], len(lines))
