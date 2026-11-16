# 명제 2-20의 유한 n 상계(n=17,100,1000,10^4)를 증명의 닫힌 꼴로 다시 센다(배정밀도 로그 산술; 세 유효숫자 확인용).
import math
def v(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
def lp(n): return (n-1)*math.log(n+1)  # log p_n
def term(n,c,b,coef_base,coef_mult):
    kap=n-c-b+1
    if kap<0: return 0.0
    # n!/c! * c^{c-1} * coef_mult*(coef_base+kap)^{kap-1}/kap! / (n+1)^{n-1}
    lg=math.lgamma(n+1)-math.lgamma(c+1)+(c-1)*math.log(c)+math.log(coef_mult)+(kap-1)*math.log(coef_base+kap)-math.lgamma(kap+1)-lp(n)
    return math.exp(lg)
for n in (17,100,1000,10000):
    best=None
    for b in range(3,60):
        ok=all(v(k,i-1,1)<0 for i in range(3,b+1) for k in range(n//2+1,n+1))
        if not ok: continue
        P1=sum(term(n,c,b,b,b) for c in range(n//2+1,n+1))
        P2=sum(term(n,c,b,2,2) for c in range(n//2+1,n+1))
        val=1-P1+P2
        if best is None or val<best[0]: best=(val,b,P1,P2)
    print(n,"best bound %.6f at b=%d (P(S_b>n/2)=%.6f, P(o=0)=%.6f)"%best)
