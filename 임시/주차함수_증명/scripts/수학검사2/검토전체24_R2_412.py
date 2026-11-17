# R2 검산(수치): (4.12) 를 k=10000, 40000 의 몇 beta 에서 직접 합으로 대조
import mpmath as mp
mp.mp.dps = 50
def check(k):
    eps = 1/mp.sqrt(k); c = 1/mp.sqrt(2*mp.pi)
    # log Bor(j) 미리
    lb = [None] + [(-j + (j-1)*mp.log(j) - mp.loggamma(j+1)) for j in range(1, k+1)]
    out = []
    for beta in (mp.mpf('0.3'), mp.mpf(1), mp.mpf(2), mp.mpf(4), mp.mpf(7), mp.mpf(12)):
        Z = mp.mpc(1, beta*eps)
        lw = mp.log(Z) + 1 - Z
        s = mp.mpc(0)
        for j in range(1, k+1):
            s += mp.exp(lb[j] + j*lw)
        tail = 1 - s/Z
        val = mp.sqrt(k)*tail
        D = mp.e**(-beta**2/2)*mp.quad(lambda v: mp.e**(v*v/2), [0, beta])
        BldR = (2 - 2*beta*D)*mp.e**(beta**2/2)
        TR = mp.mpf(3)/5 + mp.mpf(12)/5*beta**2 + mp.mpf(8)/5*beta**4 + beta**6/25
        TI = mp.mpf(1)/100 + mp.mpf(201)/100*beta + mp.mpf(3)/4*beta**3 + beta**4/250 + beta**5/10**4 + beta**7/10**5
        eR = abs(val.real - c*BldR - mp.mpf(4)/3*beta**2*eps); bR = c*eps**2*mp.e**(beta**2/2)*TR
        eI = abs(val.imag - beta); bI = c*eps*mp.e**(beta**2/2)*TI
        out.append((mp.nstr(beta, 3), mp.nstr(eR/bR, 4), mp.nstr(eI/bI, 4)))
    return out
for k in (10000, 40000):
    print(k, check(k))
