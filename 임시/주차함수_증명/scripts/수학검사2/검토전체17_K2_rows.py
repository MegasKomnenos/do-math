# K2 검산 1: 마지막 차 재귀로 n<=80의 행을 정확 정수로 만들고 3장·4장의 유한 주장들을 다시 센다.
from fractions import Fraction
from math import comb, isqrt

NMAX = 80
A = [[0] * (NMAX + 2) for _ in range(NMAX + 1)]
for l in range(NMAX + 2):
    A[0][l] = 1
for n in range(1, NMAX + 1):
    for l in range(NMAX + 1):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l]
        A[n][l] = s
p = [(n + 1) ** (n - 1) if n >= 1 else 1 for n in range(NMAX + 1)]
b = {}
for n in range(1, NMAX + 1):
    row = [A[n][0]] + [A[n][l] - A[n][l - 1] for l in range(1, n)]
    assert sum(row) == p[n] and A[n][n - 1] == p[n]
    b[n] = row

out = []
# 1.3절 표 n<=10
out.append("n=10 row: " + ", ".join(map(str, b[10])))
out.append("n=7 row: " + ", ".join(map(str, b[7])))

def witnesses(row):
    m = max(row)
    return [i for i, v in enumerate(row) if v == m]

def unimodal(row):
    ws = witnesses(row)
    w = ws[0]
    return all(row[i] <= row[i + 1] for i in range(w)) and all(row[i] >= row[i + 1] for i in range(w, len(row) - 1))

smallest = [witnesses(b[n])[0] for n in range(1, 16)]
out.append("smallest witness n=1..15: " + str(smallest))
out.append("all rows n<=80 unimodal: " + str(all(unimodal(b[n]) for n in b)))
out.append("rows with plateau (multiple witnesses) n<=80: " + str([n for n in b if len(witnesses(b[n])) > 1]))
ties = [n for n in b if any(b[n][i] == b[n][i + 1] for i in range(n - 1))]
out.append("rows with adjacent equal terms n<=80: " + str(ties))
out.append("n<=10: all witnesses < ceil(n/2): " + str(all(max(witnesses(b[n])) < -(-n // 2) for n in range(1, 11))))

# 정리 4.5: d_{n,k_n} 부호, 2<=n<=15 오른쪽 절반 비증가
kn = lambda n: -(-n // 2)
neg = [n for n in range(2, NMAX + 1) if b[n][kn(n)] - b[n][kn(n) - 1] < 0]
out.append("n with d_{n,k_n}<0 (2<=n<=80): " + str(neg))
rh = all(all(b[n][j] >= b[n][j + 1] for j in range(kn(n), n - 1)) for n in range(2, 16))
out.append("2<=n<=15 right half (k_n<=j<=n-2) nonincreasing: " + str(rh))

# D.crossing-small-n: b_{n,k_n} < b_{n,k_n+1}
cross_true = [n for n in range(5, NMAX + 1) if b[n][kn(n)] < b[n][kn(n) + 1]]
out.append("b_{n,k_n}<b_{n,k_n+1} holds for n in 5..80: first true n = %s; false set = %s" % (cross_true[0], [n for n in range(5, NMAX + 1) if n not in cross_true]))

# Q_L(n) 3<=n<=15
def QL(n):
    for l in range(0, n - 2):
        if 2 * l <= n - 2 and b[n][l] > b[n][l + 1]:
            if b[n][l + 1] ** 2 < b[n][l] * b[n][l + 2]:
                return False
    return True
out.append("Q_L(n) for 3<=n<=15: " + str(all(QL(n) for n in range(3, 16))))
# Q(n,l) 전체 (감소 뒤 로그오목) n<=80
def Qall(n):
    return all(not (b[n][l] > b[n][l + 1]) or b[n][l + 1] ** 2 >= b[n][l] * b[n][l + 2] for l in range(0, n - 2))
out.append("Q(n) all l for 3<=n<=80: " + str(all(Qall(n) for n in range(3, 81))))

# 정리 3.4: 로그오목 첫 실패
fails = [(n, l) for n in range(1, NMAX + 1) for l in range(1, n - 1) if b[n][l] ** 2 < b[n][l - 1] * b[n][l + 1]]
out.append("log-concavity failures n<=80: " + str(fails))
b39, b40, b41 = b[80][39], b[80][40], b[80][41]
out.append("b80,39 < b80,40 < b80,41: %s ; b39*b41-b40^2 > 0: %s" % (b39 < b40 < b41, b39 * b41 - b40 ** 2 > 0))
out.append("separator 25928/25000: %s" % (b40 * 25000 < 25928 * b39 and 25928 * b40 < 25000 * b41))
out.append("ratios: %.11f %.11f" % (b40 / b39, b41 / b40))
out.append("b80,39 matches appendix: %s" % (b39 == 84023389540434452566263924886618364534909977983982121246715289307110432842993124383028872316744611198639623256560041269276054594442852268387046143312))
# 누적 로그오목 n<=80
Afail = [(n, l) for n in range(1, NMAX + 1) for l in range(1, n - 1) if A[n][l] ** 2 < A[n][l - 1] * A[n][l + 1]]
out.append("cumulative log-concavity failures n<=80: " + str(Afail))

# 정리 3.6 증명: E_n omega_n (n=1..5), 유리수 상계
def Eomega(n):
    return sum(Fraction(comb(n, j) * j ** j * p[n - j], p[n]) for j in range(1, n // 2 + 1))
out.append("E omega_n n=1..5: " + str([str(Eomega(n)) for n in range(1, 6)]))
out.append("E omega_n <= sqrt(n) for n=1..40: " + str(all(Eomega(n) ** 2 <= n for n in range(1, 41))))
lam = Fraction(751, 1000)
val = lam ** 8 + Fraction(1, 31) * sum(i * lam ** (i - 1) for i in range(1, 9)) + Fraction(1, 1000) * sum((i - 1) * lam ** (i - 1) for i in range(1, 9))
out.append("Thm 3.6 rational: %s ; equals text: %s ; float %.6f ; < 0.4716: %s" % (val, val == Fraction(7309649993107890414228499, 15500000000000000000000000), float(val), val < Fraction(4716, 10000)))
out.append("9n^2-48n-32 at n=6: %d" % (9 * 36 - 48 * 6 - 32))
out.append("lambda bound: ceil(3n/4)/n <= 751/1000 for n in 1000..5000: " + str(all(Fraction(-(-3 * n // 4), n) <= lam for n in range(1000, 5001))))
# 첫 층 둘째 문장: k=ceil(3n/4) <= n-1 for n>=4
out.append("ceil(3n/4)<=n-1 for 4<=n<=200: " + str(all(-(-3 * n // 4) <= n - 1 for n in range(4, 201))))
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체17_K2_rows_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
