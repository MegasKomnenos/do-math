# 심사 A6 — P7 검산: 계승 모멘트 하계의 일반 Jensen 꼴.
# 주장: 비음 정수값 X, E X >= a >= r-1  ==>  E (X)_r >= (a)_r.
# 확인: (1) 연장 f(x) = (x)_r (x >= r-1), 0 (x < r-1) 이 [0,∞)에서 비감소·볼록 (이산 격자 위 둘째 차분과 도함수 점프);
#       (2) 무작위 분포에서 부등식 성립; (3) r=2는 Var >= 0 한 줄과 같음.
import random, io
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(r"C:\math\임시\주차함수_증명")
def ff(x, r):
    p = F(1)
    for i in range(r):
        p *= (x - i)
    return p
def f(x, r):
    return ff(x, r) if x >= r - 1 else F(0)
out = []
# (1) convexity on a fine rational grid, incl. the junction x=r-1 (derivative jumps from 0 to (r-1)!)
bad = 0
for r in range(1, 7):
    h = F(1, 8)
    xs = [F(i, 8) for i in range(0, 20 * 8)]
    for i in range(1, len(xs) - 1):
        d2 = f(xs[i + 1], r) - 2 * f(xs[i], r) + f(xs[i - 1], r)
        d1 = f(xs[i + 1], r) - f(xs[i], r)
        if d2 < 0 or d1 < 0:
            bad += 1
out.append(f"(1) extended f nondecreasing & convex on grid for r=1..6: violations = {bad}")
# (2) random integer distributions
random.seed(7)
viol = 0; tests = 0
for _ in range(4000):
    r = random.randint(1, 5)
    support = range(0, random.randint(r, 15))
    w = [random.randint(0, 9) for _ in support]
    if sum(w) == 0:
        continue
    tot = sum(w)
    EX = sum(F(wi, tot) * x for x, wi in zip(support, w))
    if EX < r - 1:
        continue
    # pick a in [r-1, EX]
    a = r - 1 + (EX - (r - 1)) * F(random.randint(0, 10), 10)
    Efr = sum(F(wi, tot) * ff(x, r) for x, wi in zip(support, w))
    tests += 1
    if Efr < ff(a, r):
        viol += 1
out.append(f"(2) random tests: {tests} cases, violations = {viol}")
# (3) r=2 identity: E[X(X-1)] = Var X + EX(EX-1)
viol3 = 0
for _ in range(500):
    support = range(0, random.randint(2, 12))
    w = [random.randint(0, 9) for _ in support]
    if sum(w) == 0:
        continue
    tot = sum(w)
    EX = sum(F(wi, tot) * x for x, wi in zip(support, w))
    EX2 = sum(F(wi, tot) * x * x for x, wi in zip(support, w))
    if EX2 - EX != (EX2 - EX * EX) + EX * (EX - 1):
        viol3 += 1
out.append(f"(3) E[X(X-1)] == Var X + EX(EX-1) exactly: violations = {viol3}")
txt = "\n".join(out)
print(txt)
io.open(ROOT / "scripts" / "구조압축" / "심사_A6_P7_jensen_out.txt", "w", encoding="utf-8").write(txt + "\n")
