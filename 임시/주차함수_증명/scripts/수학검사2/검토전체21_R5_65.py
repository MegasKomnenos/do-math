from mpmath import mp, mpf, sqrt, pi, log, exp
mp.dps=20
k=mpf(2001)
print("1/2(e^{3/2k}+1)=", (exp(mpf(3)/(2*k))+1)/2)
print("Acrit const:", (1+1/k)*(1+2/k)/(1-mpf(3)/(4*k))*mpf('1.3752'))
def DDL(k):
    k=mpf(k); return 14*(log(3*k)-1)/(5*sqrt(pi*k))+mpf('37.6')/(5*sqrt(pi)*k)
for kk in [2001,6668,8065,9551,9705]:
    print(kk, DDL(kk))
# derivative sign: d/dk of (log 3k -1)/sqrt(k) = [1/k*sqrt(k) - (log3k-1)/(2sqrt k)]/k = [1 - (log3k-1)/2]/k^{3/2} -> negative when log3k>3, k>e^3/3=6.7
print("e^3/3", exp(3)/3)
