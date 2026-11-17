# R11 검산: D.logconcavity-failure-n80 의 세 정수·비·분리자, 본문 대조
import re, json, glob, io
from math import comb
txt = io.open('장v2/부록D_장3.md', encoding='utf-8').read()
ints = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r'b_\{80,(\d+)\}=(\d{50,})', txt)}
print(sorted(ints))
N = 80
A = [[1]*N]
for n in range(1, N+1):
    row = []
    for l in range(N):
        row.append(sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n)))
    A.append(row)
viol = []
for n in range(1, N+1):
    b = [A[n][l]-(A[n][l-1] if l else 0) for l in range(n)]
    assert sum(b) == (n+1)**(n-1)
    for l in range(1, n-1):
        if b[l]*b[l] < b[l-1]*b[l+1]:
            viol.append((n, l))
print("violations n<=80:", viol)
b = [A[80][l]-(A[80][l-1] if l else 0) for l in range(80)]
print("text ints equal:", all(ints[l] == b[l] for l in (39, 40, 41)))
print("b39<b40<b41:", b[39] < b[40] < b[41])
print("sep:", 25000*b[40] < 25928*b[39], 25928*b[40] < 25000*b[41])
from fractions import Fraction
print(float(Fraction(b[40], b[39])), float(Fraction(b[41], b[40])))
pc = json.load(open(glob.glob('원고_자료/r81e7051/peer-checks.json')[0]))
print("peer-checks equal:", pc['first_log_concavity_failure']['counts'] == [b[39], b[40], b[41]])
w = json.load(open('원고_자료/r15524fd/logconcavity-witness.json'))
print("r15524fd witness equal:", [w['b_previous'], w['b_center'], w['b_next']] == [b[39], b[40], b[41]])
cs = json.load(open('원고_자료/r81e7051/computation-summary.json'))
print("record bad_log_concavity count:", len(cs['bad_log_concavity']), cs['bad_log_concavity'][:6], "N", cs['N'], "bad_unimodal", cs['bad_unimodal'])
