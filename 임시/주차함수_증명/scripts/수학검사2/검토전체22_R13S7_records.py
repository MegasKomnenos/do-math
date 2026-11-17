# 7절 표의 기록 식별자와 부록 B 목록의 대조(자리 찾기용)
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
rows = [(i+1, L[i]) for i in range(1236, 1431) if L[i].startswith('|')]
rows = rows[0:]
print('rows', len(rows), rows[0][0], rows[-1][0])
B = open('장v2/부록B.md', encoding='utf-8').read().split('\n')
bids = [m.group(1) for l in B for m in [re.match(r'\| (r[0-9a-f]{7}) \|', l)] if m]
print('부록B 식별자', len(bids), len(set(bids)))
col2 = {}
anyc = {}
for n, l in rows:
    cells = l.split(' | ')
    for r in re.findall(r'\[(r[0-9a-f]{7})\]', cells[1]):
        col2.setdefault(r, []).append(n)
    for r in re.findall(r'\[(r[0-9a-f]{7})\]', l):
        anyc.setdefault(r, []).append(n)
print('7절 둘째 열의 기록 수', len(col2), '; 어느 열이든', len(anyc))
print('부록B에 없는데 7절 둘째 열에 있음:', sorted(set(col2) - set(bids)))
print('부록B에 없는데 7절 어느 열에 있음:', sorted(set(anyc) - set(bids)))
print('부록B에 있는데 7절 둘째 열에 없음:', sorted(set(bids) - set(col2)))
for r in bids:
    print(r, len(col2.get(r, [])), col2.get(r, [])[:12])
