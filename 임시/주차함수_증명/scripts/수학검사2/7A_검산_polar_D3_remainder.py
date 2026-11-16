"""(8)(ㄴ) Xi 급수 나머지 R_J의 계수 1/((J+1/2)(J+3/2)) vs 필요한 pw^U_{J+1}=1/((J-1/2)(J+1/2))+c/k (기록 감사 D3) 정량화."""
import mpmath as mp
from mpmath import mpf, exp, factorial
mp.mp.dps = 30
J = 70
for k in (2001, 2*10**5, 10**7):
    k = mpf(k)
    d = J + 1 - mpf(5)/2
    pwU = 1/((d+1)*(d+2)) + d**d/((d+1)**(d+1)*k)        # pw^U_{J+1}
    code = 1/((J+mpf(1)/2)*(J+mpf(3)/2)) + 1/k           # coefficient used in R_J
    for u in (mpf('0.01'), mpf('0.03'), mpf('0.1'), mpf('1')):
        # true tail <= sum_{j>J} u^j/j! pw^U_j <= pw^U_{J+1} * sum_{j>J} u^j/j!  (pw^U decreasing in j); compare with R_J
        tail = sum(u**j/factorial(j)*(1/((j-mpf(3)/2)*(j-mpf(1)/2)) + (j-mpf(5)/2)**(j-mpf(5)/2)/((j-mpf(3)/2)**(j-mpf(3)/2)*k)) for j in range(J+1, J+40))
        RJ = u**(J+1)/factorial(J+1)*exp(u)*code
        print('k=%g u=%s: pw^U_{71}=%s code coef=%s ratio=%.4f ; R_J / (sum_{j>J} u^j/j! pw^U_j) = %.4f' % (k, mp.nstr(u, 3), mp.nstr(pwU, 8), mp.nstr(code, 8), code/pwU, RJ/tail))
