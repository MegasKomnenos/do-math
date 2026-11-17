# 검토전체23 R5: (6.28)·(6.29)의 수치 미분 대조와 정리 6:pointwise의 최솟값 표본
import math, itertools
from math import log, factorial
def cg(g): return g**(g-1)/factorial(g)
def partitions(d, j):
    # interior points subsets of {d-j+1..d-1}
    pts = list(range(d-j+1, d))
    for r in range(len(pts)+1):
        for Q in itertools.combinations(pts, r):
            yield Q
def Gs(xi, y): return sum((1-1/y)**i for i in range(xi+1))
def Wc(Q, d, j, y):
    ends = [d-j]+list(Q)+[d]
    w = 1.0
    for a, b in zip(ends, ends[1:]): w *= cg(b-a)
    w *= Gs(len(Q), y)
    for q in Q: w *= y/(y+q)
    return w
def Gt(d, j, y):
    K = 1.0
    for r in range(d-j+1, d): K *= (y+r)
    K *= sum(Wc(Q, d, j, y) for Q in partitions(d, j))
    return math.exp(log(y-1)+log(y)+(y+d-j-2)*log(y+d-j)+log(K)-(y+d-1)*log(y+d))
def tie(xi, y):
    num = sum(i*(1-1/y)**(i-1) for i in range(xi+1))
    return num/Gs(xi, y)
def ftil(z, y): return y*y*z/(y+z)**2
def Lsharp(d, j, y):
    return y*y*(log(1+j/(y+d-j))-sum(1/(y+d-j+r) for r in range(1, j+1))) - y/(y-1) - 2*(d-j)*y/(y+d-j)
def Mfun(Q, d, j, y):
    xi = len(Q)
    ends = [d-j]+list(Q)+[d]
    eta = Gs(xi+1, y)/Gs(xi, y)
    tot = 0.0
    for a, b in zip(ends, ends[1:]):
        g = b-a
        for z in range(a+1, b):
            tot += cg(z-a)*cg(b-z)/cg(g)*ftil(z, y)
    return tie(xi, y) + eta*tot
maxerr = 0; minval = 1e9; arg = None
for d in range(1, 9):
    for j in range(1, d+1):
        for y in [max(d, 1.2), d+0.5, 1.5*d+1, 3*d+2, 10*d+5, 100*d]:
            if y <= 1: continue
            h = 1e-5*y
            num = y*y*(log(Gt(d, j, y+h))-log(Gt(d, j, y-h)))/(2*h)
            ws = [(Wc(Q, d, j, y), Q) for Q in partitions(d, j)]
            tw = sum(w for w, _ in ws)
            EM = sum(w*Mfun(Q, d, j, y) for w, Q in ws)/tw
            # (6.28) direct
            E28 = sum(w*(tie(len(Q), y)+sum(q*y/(y+q) for q in Q)) for w, Q in ws)/tw
            f28 = -Lsharp(d, j, y) + E28
            f29 = EM - Lsharp(d, j, y)
            maxerr = max(maxerr, abs(num-f28), abs(num-f29))
            for w, Q in ws:
                v = Mfun(Q, d, j, y) - Lsharp(d, j, y)
                if v < minval: minval = v; arg = (d, j, y, Q)
print("max |numeric - formula| for (6.28),(6.29):", maxerr)
print("min M(C)-L# over sample:", minval, arg)
