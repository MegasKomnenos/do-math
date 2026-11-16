# pair-reach-table 검산(배정밀도 근사): (7.12) 꼬리 삼중 확인, 각 K_1 열의 nu_P 재계산, n_X(2002)
import math, numpy as np
def Bor(j): return math.exp(-j+ (j-1)*math.log(j) - math.lgamma(j+1))
def kebar(K1,M): 
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def check712(K1,M,tf):
    E=math.exp(kebar(K1,M)); B=[Bor(s+1) for s in range(M)]
    worst=None
    for q in range(2,M+1):
        F=tf*q**1.5-E*sum(B[s]*((q-1-s)+tf*(q-1-s)**1.5) for s in range(q-1))
        worst=F if worst is None else min(worst,F)
    return worst
for t in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    print("triple",t,"min F =",check712(*t), "tf*M^1.5=",t[2]*t[1]**1.5)
def nuP(K1,M,tf):
    k=K1
    q=np.arange(1,M+1,dtype=float)
    nh=np.where(q>=2, tf*q**1.5/k, 0.0)
    ex=q+(k+q)*nh/(1-nh)
    nu=1
    while True:
        ok=True
        # all q,q'>=1 with q+q'<=nu, j=nu-q-q' (lb decreasing in j), need q,q'<=M
        for qa in range(1,nu):
            qb_max=nu-qa
            if qb_max<1: break
            if qa>M: ok=False; break
            qb=np.arange(1,min(qb_max,M)+1)
            if qb_max>M: ok=False; break
            j=nu-qa-qb
            lb=1-(j/k)*(ex[qa-1]+ex[qb-1])-(ex[qa-1]*(qb-1)+ex[qb-1]*(qa-1))/(2*k)
            if (lb<=0).any(): ok=False; break
        if not ok: return nu-1
        nu+=1
        if nu>M+1: return nu-1
table={12000:(120,0.54),13000:(120,0.54),14000:(120,0.54),15000:(120,0.54),20000:(120,0.54),30000:(250,0.593),50000:(250,0.593),10**5:(300,0.522),2*10**5:(450,0.548),5*10**5:(450,0.548),10**6:(700,0.519)}
for K1,(M,tf) in table.items():
    print(K1, "nu_P =", nuP(K1,M,tf))
print("n_X(2002) =", math.ceil(2002**(4/3)), 2002**(4/3))
print("n_M ratios:", 20507/841**1.5, 73032/2000**1.5)
