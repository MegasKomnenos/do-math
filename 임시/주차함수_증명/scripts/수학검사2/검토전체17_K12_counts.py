# K12: D.exact-n20000 범위 줄의 개수들과 D.tail-T1 (B) 상수, tm 검산
import mpmath as mp
mp.mp.dps=30
ceil=lambda a,b: -(-a//b)
# (ㄹ) positions 5<=n<=20000, (n-1)/2<=l<=n-3
pos=sum(max(0,(n-3)-ceil(n-1,2)+1) for n in range(5,20001)); print("(ㄹ) positions",pos)
pos50=sum(max(0,(n-3)-ceil(n-1,2)+1) for n in range(20001,50001)); print("c50 positions",pos50)
# column cert 121..500
def col(klo,khi):
    d=r=0
    for k in range(klo,khi+1):
        B=ceil(k*k,4)
        d+=max(0,2*B-(2*k+1)+1); r+=B+1  # B<=n<=2B
    return d,r
print("col 161-500 direct,ratio:",col(161,500)); print("col 121-160:",col(121,160))
# theorem-D-base pair count
cnt=sum(int(mp.floor(mp.mpf(m)**(mp.mpf(2)/3)/2)) for m in range(4,701)); print("thmD pairs",cnt, "d at 700:",int(mp.floor(mp.mpf(700)**(mp.mpf(2)/3)/2)))
cnt2=sum(1 for m in range(4,701) for d in range(1,60) if 8*d**3<=m*m); print("8d^3<=m^2 pairs",cnt2)
# (B) constants
M0=mp.quad(lambda y: mp.e**(-y-y*y/2),[0,mp.inf]); M=[M0,1-M0]
for i in range(1,5): M.append(i*M[i-1]-M[i])
print("M0..M5:",[mp.nstr(x,6) for x in M])
L=mp.mpf('0.845204'); s=mp.mpf(100)
lhs=s*(mp.mpf(1)/2+2*L-mp.sqrt(3*mp.pi/2))+mp.mpf(1)/2-(1/(3*s)+8/(3*s*s)+mp.mpf('2.507')/s**2+(1+mp.mpf('2.1709')*s)/s**3)
print("(B) s=100 lhs",mp.nstr(lhs,8)," rhs",mp.nstr(mp.mpf('0.0196')*s+mp.mpf('0.496'),8), " 1/2+2L-sqrt(3pi/2)=",mp.nstr(mp.mpf(1)/2+2*L-mp.sqrt(3*mp.pi/2),8))
# tm_{r-1}(rho) with bw weights, rho=e^{-1/sqrt r}
def tm(r,rho):
    bw=mp.mpf(1); num=mp.mpf(0); den=mp.mpf(1); j=0
    while j<r-1:
        bw=bw*rho*mp.mpf(j+2)/(j+1)*mp.mpf(r-1-j)/r; j+=1
        num+=j*bw; den+=bw
    return num/den
for r in (10**4,2*10**4):
    print("r",r," tm/sqrt r =",mp.nstr(tm(r,mp.e**(-1/mp.sqrt(r)))/mp.sqrt(r),5))
# rho_r for (A): k_r=ceil(r^{3/2}+8r), rho=k/(k+r); tm_{r-1}(rho_r) for r=171 and 9999 (values only)
for r in (171,9999):
    k=int(mp.ceil(mp.mpf(r)**1.5+8*r)); rho=mp.mpf(k)/(k+r); print("r",r,"k_r",k,"tm_{r-1}(rho_r)=",mp.nstr(tm(r,rho),8))
