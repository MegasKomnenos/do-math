from fractions import Fraction as F
from math import comb, factorial, ceil, exp, log, sqrt
# (1) pair-check-10000 count and minimum of (7.11) RHS
k=10000
def pis(q): return F(q*(q-1),2*(k+1))
def exbar(q):
    p=pis(q); return q+(k+q)*p/(1-p)
cnt=0; best=None
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,(q,qp,j))
print("count",cnt,"min",float(best[0]),best[1])
# (2) tail triples tf*M^{3/2}
for K1,M,tf in [(10**4,120,.54),(2*10**4,250,.593),(10**5,300,.522),(10**5,450,.548),(10**6,700,.519)]:
    print(K1,M,tf, tf*M**1.5, tf*M**1.5<K1)
# (3) n_X(2002), n_M ratios
print("nX(2002)",ceil(2002**(4/3)), "nX(3131)",ceil(3131**(4/3)))
print(20507/841**1.5, 73032/2000**1.5)
# (4) polar-PD numbers
print(0.7*2001/2002, 0.3**1.5/2, 2*exp(-5.3146*0.6996), 0.0821*exp(-3/25233), log(2/0.0820)/0.6996)
# (5) vertical-nu (마)
print((1.5+1/20000)**1.5*exp(1/240000), 1.84*2/sqrt(3.141592653589793), 2.08/sqrt(2*3.141592653589793))
# (6) hermite: 1.12e-5 vs 1/(9e4); 9400/k^3 bound
print(1/(9*10**4), 2e7*3.07/9**4)
# (7) x_k for k: P_k(k)=k*k^{k-2}/(k+1)^{k-1}
k=5; print(F(k*k**(k-2),(k+1)**(k-1)), F(k**(k-1),(k+1)**(k-1)))
# (8) analytic-transfer (가) differences
vals=[0.2048,0.1938,0.1827,0.1717,0.1607,0.1496,0.1386,0.1275,0.1165,0.1054,0.0944,0.0833,0.0723,0.0613,0.0502,0.0392,0.0281,0.0170,0.0060]
print([round(vals[i]-vals[i+1],4) for i in range(18)])
# (9) integer-strips counts
cA=sum(1 for k in range(9981,11100) for n in range(max(20001,2*k+1),2*k+41))
cB=sum(1 for k in range(9950,12000) for n in range(max(2*k+41,20001),2*k+103))
cC=sum(1 for k in range(12000,13000) for nu in range(59,103))+sum(1 for k in range(13000,14000) for nu in range(80,103))+sum(1 for k in range(14000,15000) for nu in range(96,103))
print("strips",cA,cB,cC,cB+cC)
# (10) old-6-13: k lower bound
print((20001-102)/2, (20001-40)/2)
# (11) theorem-C-moment: 0.8165*841^1.5 vs 2*841+1
print(0.8165*841**1.5, 2*841+1)
