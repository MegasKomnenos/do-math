# 검토전체22 R7a: 7.4절·7.5절의 수치 다시 세기 (python -I)
from math import sqrt, pi
from fractions import Fraction as F

print("== tail-half (7.7) 상수 ==")
c = (1 + 100/10001)**1.5
print("(1+100/10001)^1.5 =", c, "< 1.0151:", c < 1.0151)
print("1.0151*(2pi)^-1/2 =", 1.0151/sqrt(2*pi), "< 0.405:", 1.0151/sqrt(2*pi) < 0.405)
def h(q): return 0.04*q**1.5 - 0.405*(q + sqrt(q) - 2/3 - 2/(3*sqrt(q)))
print("h(2) =", h(2), " h(101) =", h(101))
print("max h on integers 2..101 =", max(h(q) for q in range(2,102)))
# 직접: 0.405*[4/3 (q-1)^1.5 + sqrt(q-1) - q + 2/3] <= q^1.5/2 ?
worst = max(0.405*(4/3*(q-1)**1.5 + sqrt(q-1) - q + 2/3) - q**1.5/2 for q in range(2,102))
print("direct worst (should be <0):", worst)

print("== C_{K,L} ==")
for K,L in [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]:
    C = (1+(L-1)/K)/(2*(1-(L-1)**1.5/(2*K)))
    br = L*L/3 + 8/25*sqrt(2/5)*21/40*L**2.5
    print(K, L, "C=%.6f" % C, "bracket=%.3f" % br, br < K)

print("== pair-loss-bound (7.9) brute force ==")
def lhs(q,qp,j,C):
    return j*(q+qp+C*(q**1.5+qp**1.5)) + ((q+C*q**1.5)*(qp-1)+(qp+C*qp**1.5)*(q-1))/2
for C in [0, 0.1, 21/40, 1.0, 5.0]:
    for L in [2,3,5,10,50,58,79,99,102]:
        m = -1; arg=None
        for q in range(1,L):
            for qp in range(1,L-q+1):
                j = L-q-qp
                if j < 0: continue
                v = lhs(q,qp,j,C)
                if v > m: m=v; arg=(q,qp,j)
        rhs = L*L/3 + 8*C/25*sqrt(2/5)*L**2.5
        assert m <= rhs + 1e-9, (C,L,m,rhs)
        if C == 21/40: print("C=21/40 L=%d max lhs=%.2f at %s rhs=%.2f" % (L,m,arg,rhs))
print("ok")

print("== integer-strips 위치 수 ==")
ga = sum(max(0, 2*k+40 - max(20001,2*k+1) + 1) for k in range(9981,11100))
na = sum(max(0, 2*k+102 - max(2*k+41,20001) + 1) for k in range(9950,12000))
da = 1000*(102-59+1) + 1000*(102-80+1) + 1000*(102-96+1)
print("(가)", ga, "(나)", na, "(다)", da, "(나)+(다)", na+da)
# k<9981 에서 nu<=40 위치가 있는가
print("k in 9950..9980 with 2k+40>=20001:", [k for k in range(9950,9981) if 2*k+40>=20001])
# 정리 범위 전체 덮개: k>=9950, max(2k+1,20001)<=n<=2k+102
def covered(k,nu):
    n = 2*k+nu
    # 해석+쌍별
    def pair(k,nu):
        return any(k>=K and nu<=L for K,L in [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)])
    def ana(k,nu):
        if k>=10000 and 1<=nu<=19: return True
        if k>=11100 and 20<=nu<=40: return True
        for K1,nm in [(12000,58),(13000,79),(14000,99),(15000,102)]:
            if k>=K1 and 41<=nu<=nm: return True
        return False
    def strips(k,nu):
        n=2*k+nu
        if 9981<=k<=11099 and max(20001,2*k+1)<=n<=2*k+40: return True
        if 9950<=k<=11999 and max(2*k+41,20001)<=n<=2*k+102: return True
        if 12000<=k<=12999 and 59<=nu<=102: return True
        if 13000<=k<=13999 and 80<=nu<=102: return True
        if 14000<=k<=14999 and 96<=nu<=102: return True
        return False
    return (pair(k,nu) and ana(k,nu)) or strips(k,nu)
bad = [(k,nu) for k in range(9950,16001) for nu in range(1,103) if 2*k+nu>=20001 and not covered(k,nu)]
print("덮이지 않은 위치:", len(bad), bad[:5])
