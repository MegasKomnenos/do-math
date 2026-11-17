# R12 검산: D.column-certification-k500의 비교 수와 2n_* < 10000인 열
def cnt(a, b):
    d = bd = 0
    for k in range(a, b + 1):
        N = -(-k * k // 4)
        d += 2 * N - 2 * k
        bd += N + 1
    return d, bd
print(cnt(121, 160), cnt(161, 500))
print(max(k for k in range(121, 501) if 2 * (-(-k * k // 4)) < 10000))
L = 10**21 * 400**10; R = 17**21 * 123**10
print(L > R, L, R)
