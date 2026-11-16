# F13: D.column-certification-k500 의 수치 검산
import math
L = 10**21 * 400**10
R = 17**21 * 123**10
print("L", L, "%.6e" % L)
print("R", R, "%.6e" % R)
print("L>R", L > R)
def cnt(ks):
    dd = rr = 0
    for k in ks:
        B = -(-k*k//4)
        dd += 2*B - 2*k   # n in [2k+1, 2B]
        rr += B + 1       # n in [B, 2B]
    return dd, rr
print("first 121..160", cnt(range(121,161)))
print("second 161..500", cnt(range(161,501)))
