"""sup_sigma R(sigma) = sum_{m>=k} Bor(m)(1-k/m) 의 정밀 상계(numpy, lgamma)와 글의 R_max = c(4/3 k^{-1/2}+0.19 k^{-3/2}) 대조.
꼬리 m>M 은 적분 상계 int_M^inf c x^{-3/2}(1-k/x)dx (그 구간에서 합산항이 감소하고 Bor(m) <= c m^{-3/2})."""
import numpy as np
from math import lgamma, sqrt, pi
c = 1/sqrt(2*pi)
lg = np.vectorize(lgamma)
for k in (501, 1000, 5000, 100000):
    M = 100*k
    m = np.arange(k+1, M+1, dtype=float)
    logB = -m + (m-1)*np.log(m) - lg(m+1)
    S = float(np.sum(np.exp(logB)*(1-k/m)))
    tail = c*(2/sqrt(M) - 2*k/(3*M**1.5))
    bound = c*(4/3/sqrt(k) + 0.19/k**1.5)
    print("k=%7d: sup R <= %.9e  R_max(text) = %.9e  ratio %.6f  ok=%s" % (k, S+tail, bound, (S+tail)/bound, S+tail <= bound))
