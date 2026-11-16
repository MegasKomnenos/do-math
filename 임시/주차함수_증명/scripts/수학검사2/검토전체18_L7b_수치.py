# L7b: 7.6-7.7절 상수 검산
from mpmath import mp, mpf, sqrt, log, exp, e, pi, binomial, floor, ceil
mp.dps = 30
out=[]
def P(s): out.append(s)
# theorem-W (가)
P(f"1-0.8/sqrt(301) = {1-mpf('0.8')/sqrt(301)}")
P(f"0.9538/0.398943 = {mpf('0.9538')/mpf('0.398943')}")
P(f"(2pi)^-1/2 = {1/sqrt(2*pi)}")
P(f"0.14*2.38*0.9999 = {mpf('0.14')*mpf('2.38')*mpf('0.9999')}; 0.14*301={mpf('0.14')*301}")
k=mpf(3131)
P(f"n>=6263: sg_n bound = {1/(2*6264)+1/(6*6263*6264)}, e^-sg >= {exp(-(1/(2*6264)+1/(6*6263*6264)))}")
P(f"D_k(2) at 3131 = {mpf('0.08329')*sqrt(k)-2-mpf('42.14')/k}; 0.33316/4={mpf('0.33316')/4}")
u=k**(mpf(1)/6)
P(f"k^(1/6)={u}; (1+1/k)^(4/3)={(1+1/k)**(mpf(4)/3)}; 1+2/k={1+2/k}; 1.001+42.14/k={mpf('1.001')+mpf('42.14')/k}")
R=mpf('0.33316')*(sqrt(k)-2*u+1/u)-mpf('1.0005')*k**(mpf(1)/3)-mpf('1.0145')
P(f"right end bound at 3131 = {R}")
dR=mpf('0.33316')*(3*k**(mpf(1)/3)-2-k**(-mpf(1)/3))-mpf('2.001')*u
P(f"derivative wrt u at 3131 = {dR}")
# exact n_PD check
nPD=ceil((k+1)**(mpf(4)/3))+k+1
P(f"n_PD(3131)={nPD}, n_PD/k={nPD/k}, k^(1/3)(1+1/k)^(4/3)+1+2/k={k**(mpf(1)/3)*(1+1/k)**(mpf(4)/3)+1+2/k}")
# direct check of G_k(n)>1 at some sample points for k=3131
def G(k,n):
    k=mpf(k); n=mpf(n); sg=n*log(n/(n+1))+1
    return mpf('0.14')/n*(mpf('2.38')*k**mpf('1.5')*(n-k+1)**2/(exp(sg)*n*(n+1))-301)
for kk in [3131, 6667, 20000]:
    kk=mpf(kk); npd=ceil((kk+1)**(mpf(4)/3))+kk+1
    vals=[G(kk,nn) for nn in [2*kk+1, 3*kk, npd-1]]
    P(f"k={kk}: G(2k+1)={vals[0]}, G(3k)={vals[1]}, G(nPD-1)={vals[2]}")
# threshold-unit-ratio
k=mpf(6667)
j0=floor(mpf('0.3')*k)
P(f"j0={j0}; (1+1/k)^j0={ (1+1/k)**j0 }; e^0.3={exp(mpf('0.3'))}")
val=(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1))
P(f"(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 = {val}")
exact=sum(mpf(i)/(k+1+i) for i in range(1,int(j0)+1))
P(f"exact sum i/(k+1+i) = {exact}; j0(j0+1)/(2(k+1+j0))={j0*(j0+1)/(2*(k+1+j0))}")
rhs=1+mpf(3)/2*log(k)-val
P(f"1+1.5 log k - val = {rhs}")
P(f"e^(3/(2k)) at 6667 = {exp(3/(2*k))}; 1.00023*1.34986={mpf('1.00023')*mpf('1.34986')}")
P(f"2*0.7654-1.3502={2*mpf('0.7654')-mpf('1.3502')}")
# binom(2k,k) >= 4^k/(2 sqrt k) sample
for kk in [2,3,10,100]:
    P(f"k={kk}: binom(2k,k)={binomial(2*kk,kk)}, 4^k/(2sqrt k)={mpf(4)**kk/(2*sqrt(kk))}")
# LRP2 remainder
P(f"3*3333-1={3*3333-1}; 3*3334-1={3*3334-1}; 3*6666-1={3*6666-1}; 3*6667-1={3*6667-1}; 3*6668-1={3*6668-1}")
# v_k bound: x_k n > 368
P(f"e^-1*1003={1003/e}; (501/502)^500={(mpf(501)/502)**500}")
# sg_m bound check for m=1..5 and large
for m in [1,2,5,100]:
    m=mpf(m); sg=m*log(m/(m+1))+1
    P(f"m={m}: sg={sg}, bound={1/(2*(m+1))+1/(6*m*(m+1))}")
open("scripts/수학검사2/검토전체18_L7b_수치.out","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
