# A9 R8 검산: (1) 9.8 하계 Psi(d)>=0.7978 sqrt d - 0.8848 와 9.43 하계 0.3989(2 sqrt d - 1.678) 는 8.6(라)의 Psi^low_(d) 이하인가(8.6(라)가 함의하는가),
# 각 하계가 참값에 얼마나 못 미치는가; (2) 9.7의 g에 든 e^{1/(12(m-d+1))}: Bor(m-i)/Bor(m+1) <= ((m+1)/(m-i))^{3/2} 가 지수 인자 없이 성립하는가(rb 감소).
from math import sqrt, log, exp, lgamma, pi
z12=-1.46036; z32=2.61238
cPsi=-z12+z32/12
def Ren(j): return exp(j*log(j)-j-lgamma(j+1))
def psi_low_86(r): return (2*pi)**-0.5*(2*sqrt(r)-cPsi+1/(2*sqrt(r))-r**-1.5/24)
def lo98(d): return 0.7978*sqrt(d)-0.8848
def lo943(d): return 0.3989*(2*sqrt(d)-1.678)
P=0.0; bad98=bad943=0; gap=[]
for d in range(1,10**6+1):
    P+=Ren(d); l86=psi_low_86(d)
    if lo98(d)>l86+1e-15: bad98+=1
    if lo943(d)>l86+1e-15: bad943+=1
    if l86>P+1e-13: print("8.6(라) 위반",d)
    if d in (1,2,5,10,100,1000,10**4,10**5,10**6): gap.append((d,round(P,5),round(l86,5),round(lo943(d),5),round(lo98(d),5)))
print("(1) d<=1e6: 9.8 하계 > 8.6(라) 인 d 수 =",bad98,"; 9.43 하계 > 8.6(라) 인 d 수 =",bad943)
print("    (d, Psi, 8.6(라), 9.43, 9.8):",gap)
def rb(m): return lgamma(m+1)-(m+0.5)*log(m)+m-0.5*log(2*pi)
mono=all(rb(m)>rb(m+1) for m in range(1,20000))
print("(2) rb_m 감소(m<20000):",mono," -> 9.7의 g와 상계의 e^{1/(12·)} 인자는 불필요(두 인자 모두 1로 둘 수 있음)")
