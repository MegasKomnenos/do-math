# O1: 명제 2.20의 유한 n 상계값 네 개를 닫힌 꼴로 다시 센다 (mpmath 50자리).
import mpmath as mp
mp.mp.dps=50
def logfact(n): return mp.loggamma(n+1)
def term(n,c,bb,restricted):
    kappa=n-c-bb+1
    if kappa<0: return mp.mpf(0)
    base=mp.mpf(2) if restricted else mp.mpf(bb)
    shift=3 if restricted else 1   # (n-c-b+3) vs (n-c+1)=(n-c-b+1)+b
    x=mp.mpf(n-c-bb+3) if restricted else mp.mpf(n-c+1)
    # (x)^(kappa-1): kappa=0 -> x^{-1} ; formula has (.)^{n-c-b} = kappa-1
    lg=logfact(n)-logfact(c)+(c-1)*mp.log(c)+mp.log(base)+(kappa-1)*mp.log(x)-logfact(kappa)-(n-1)*mp.log(n+1)
    return mp.e**lg
def vneg(k,i):  # k^i v_k(i-1,1) <0 ?  (k+1)^{i-1} k + (k-1)^i - 2k^i < 0
    return (k+1)**(i-1)*k+(k-1)**i-2*k**i<0
def bound(n,bb):
    tot1=mp.mpf(0); tot2=mp.mpf(0)
    for c in range(n//2+1,n+1):
        tot1+=term(n,c,bb,False); tot2+=term(n,c,bb,True)
    return 1-tot1+tot2
for n in (17,100,1000,10000):
    best=None
    for bb in range(3,n//2+2):
        ok=all(vneg(k,i) for i in range(3,bb+1) for k in range(n//2+1,n+1))
        if not ok: break
        v=bound(n,bb)
        if best is None or v<best[0]: best=(v,bb)
    print(n, "best b=",best[1], "bound=",mp.nstr(best[0],10))
