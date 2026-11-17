# R2 검산: (4.12)의 두 상계를 k=10000, 40000에서 수치로 시험
import mpmath as mp
mp.mp.dps = 60
c = 1/mp.sqrt(2*mp.pi)
def run(k, betas):
    eps = 1/mp.sqrt(k)
    lb = [-(j) + (j-1)*mp.log(j) - mp.loggamma(j+1) for j in range(1, k+1)]
    worstR = worstI = 0
    for beta in betas:
        Z = mp.mpc(1, beta*eps)
        L = mp.log(Z) + 1 - Z
        s = mp.mpc(0)
        for j in range(1, k+1):
            s += mp.exp(lb[j-1] + j*L)
        tail = 1 - s/Z
        val = mp.sqrt(k)*tail
        D = mp.exp(-beta**2/2)*mp.quad(lambda v: mp.exp(v*v/2), [0, beta])
        BldR = (2 - 2*beta*D)*mp.exp(beta**2/2)
        TR = mp.mpf(3)/5 + mp.mpf(12)/5*beta**2 + mp.mpf(8)/5*beta**4 + beta**6/25
        TI = mp.mpf(1)/100 + mp.mpf(201)/100*beta + mp.mpf(3)/4*beta**3 + beta**4/250 + beta**5/10**4 + beta**7/10**5
        eR = abs(val.real - c*BldR - mp.mpf(4)/3*beta**2*eps)/(c*eps**2*mp.exp(beta**2/2)*TR)
        eI = abs(val.imag - beta)/(c*eps*mp.exp(beta**2/2)*TI)
        worstR = max(worstR, eR); worstI = max(worstI, eI)
        print(k, float(beta), 'ratioR', mp.nstr(eR, 5), 'ratioI', mp.nstr(eI, 5))
    print('k', k, 'max ratios', mp.nstr(worstR, 6), mp.nstr(worstI, 6))
run(10000, [mp.mpf(x) for x in (0, 0.05, 0.2, 0.5, 1, 1.5, 2, 3, 4, 6, 9, 12.5)])
