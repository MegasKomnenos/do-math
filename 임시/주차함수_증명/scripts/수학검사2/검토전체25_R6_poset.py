# -*- coding: utf-8 -*-
# 정리 7:old-6-6 증명의 부분순서 비교(아래 닫힌 집합의 원소가 상위 F개 값에 드는 수는 초기하보다 확률적으로 작다)를
# 무작위 작은 부분순서에서 전수로 확인한다(검토 25차 R6).
import itertools, random, sys, io
from fractions import Fraction as Fr
from math import comb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
random.seed(7)
def hyp_ge(n, y, F, f):
    return Fr(sum(comb(y, j)*comb(n-y, F-j) for j in range(f, min(y, F)+1) if F-j <= n-y), comb(n, F))
cnt = 0
for n in range(2, 8):
    for trial in range(60):
        rel = [(j, i) for i in range(n) for j in range(i) if random.random() < 0.35]   # j<i 만: 접두는 아래 닫힘
        exts = [s for s in itertools.permutations(range(n)) if all(s[j] < s[i] for (j, i) in rel)]
        for y in range(0, n+1):
            for F in range(1, n+1):
                for f in range(1, min(y, F)+1):
                    pr = Fr(sum(1 for s in exts if sum(1 for pos in range(y) if s[pos] >= n-F) >= f), len(exts))
                    assert pr <= hyp_ge(n, y, F, f), (n, rel, y, F, f)
                    cnt += 1
print('부분순서 비교: 위반 0건, 비교', cnt, '개')
