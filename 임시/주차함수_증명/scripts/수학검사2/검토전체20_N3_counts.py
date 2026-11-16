import math
# 둘째 조각: 10001<=n<=20000, 비교 b_{n,1}<=...<=b_{n,k_n}: k_n-1 개
kn=lambda n:(n+1)//2
c2=sum(kn(n)-1 for n in range(10001,20001))
# 넷째 조각: 5<=n<=20000, ceil((n-1)/2)<=l<=n-3
cnt=lambda n: max(0,n-3-math.ceil((n-1)/2)+1)
c4=sum(cnt(n) for n in range(5,20001))
c5=sum(cnt(n) for n in range(20001,50001))
print("둘째조각",c2,"넷째조각",c4,"50000",c5, 94192042+5777960)
# old-5-2 (나) m_max for n=20001, 50000
for n in (20001,50000):
    m=max(m for m in range(171,2000) if m**1.5+9*m<=n); print(n,m)
