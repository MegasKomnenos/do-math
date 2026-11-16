# H12 검산 6: 부록 D 5A 항목의 셈·작은 n 대조
import math, time
from fractions import Fraction as Fr
import mpmath as mp
t0=time.time()
def p(n): return (n+1)**(n-1) if n>=1 else 1
def ceil_half(x): return -(-x//2)
# counts
c1=4*9989+sum(10000-2*k for k in range(6,121)); print("(ㄱ) 직접 비교 k<=120:",c1,"== 1175466:",c1==1175466)
def B(k): return -(-k*k//4)
d_col=sum(2*B(k)-2*k for k in range(161,501)); r_col=sum(B(k)+1 for k in range(161,501))
d_col2=sum(2*B(k)-2*k for k in range(121,161)); r_col2=sum(B(k)+1 for k in range(121,161))
print("열 인증 161-500 직접:",d_col,"(19982310) 비:",r_col,"(10103865); 121-160 직접:",d_col2,"(386260) 비:",r_col2,"(198790)")
print("행 인증 501-4999:",sum(10000-2*k for k in range(501,5000)),"(20245500)")
print("(ㄴ):",sum(ceil_half(n)-1 for n in range(10001,20001)),"(74995000)")
def qr_positions(n): 
    lo=ceil_half(n-1); return max(0,(n-3)-lo+1)
print("(ㄹ) 5..20000 위치:",sum(qr_positions(n) for n in range(5,20001)),"(99970002); 인접쌍:",sum(qr_positions(n)+1 for n in range(5,20001)),"(99989998)")
print("c50 20001..50000 위치:",sum(qr_positions(n) for n in range(20001,50001)),"(524955000); 인접쌍:",sum(qr_positions(n)+1 for n in range(20001,50001)),"(524985000)")
print("(ㅂ) 행 수 50..20000:",20000-50+1,"(19951); 50..900:",900-50+1,"(851); 901..20000:",20000-901+1,"(19100)")
print("Newton: sum_{r=2}^{170}(r-1)=",sum(r-1 for r in range(2,171)),"(14365); r<=40:",sum(r-1 for r in range(2,41)),"(780); coeffs r<=40 (deg r+d+3):",sum(r+d+4 for r in range(2,41) for d in range(1,r)),"(35100)")
print("tail T1: 171..9999 count",9999-171+1,"(9829)")
print("band A: 21*235=",21*235,"82*235=",82*235," crit cells 44*43=",44*43," 10001^(-1/3)=",10001**(-1/3)," A28 lower=",0.04641-29*0.0015," G: 0.0015/1.25^12=",0.0015/1.25**12)
print("166 k^-1/6 e^-0.1267k, k=10001: log10 =", math.log10(166)-math.log10(10001)/6-0.1267*10001/math.log(10), " e^-1263 log10=",-1263/math.log(10))
mp.mp.dps=30
M0=mp.quad(lambda y: mp.e**(-y-y*y/2),[0,mp.inf]); M=[M0,1-M0]
for i in range(1,5): M.append(i*M[i-1]-M[i])
print("M0..M5:",[mp.nstr(m,6) for m in M])
L=mp.mpf('0.845204'); s=mp.mpf(100)
lhs=s*(mp.mpf(1)/2+2*L-mp.sqrt(3*mp.pi/2))+mp.mpf(1)/2-(1/(3*s)+8/(3*s**2)+mp.mpf('2.507')/s**2+(1+mp.mpf('2.1709')*s)/s**3)
print("(B) at s=100: lhs=",lhs," rhs=",mp.mpf('0.0196')*s+mp.mpf('0.496'), " 1/2+2L-sqrt(3pi/2)=",mp.mpf(1)/2+2*L-mp.sqrt(3*mp.pi/2))
# exact rows n<=300 via columns 0..152 (as before)
N=300
cols={}
for l in range(0,153):
    col=[1]
    for n in range(1,N+1):
        s_=0
        for j in range(n):
            s_+=math.comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j]
        col.append(s_)
    cols[l]=col
def A_(n,l):
    if l<0: return 0
    if l>=n-1: return p(n)
    return cols[l][n]
def b(n,l): return A_(n,l)-A_(n,l-1)
print("rows done",round(time.time()-t0,1))
# (ㅁ) left chain strict for n<=300: b_{n,0}<...<b_{n,k_n-1}
bad=[n for n in range(2,N+1) if not all(b(n,l)<b(n,l+1) for l in range(0,ceil_half(n)-1))]
print("(ㅁ) left strict chain broken at n in", bad, " (expect 5,7,9,11)")
# (ㄱ) strict b_{n,1}<...<b_{n,k_n-1} for 12<=n<=300 implied above. (ㄹ) Q_R structure for 5<=n<=300
okR=True; prem_excl=0; lc=0
for n in range(5,154):
    lo=ceil_half(n-1); first_dec=None; last_nondec=None
    for l in range(lo,n-2):
        if b(n,l)<=b(n,l+1): last_nondec=l; prem_excl+=1
        else:
            lc+=1
            if first_dec is None: first_dec=l
            if not (b(n,l+1)**2>b(n,l)*b(n,l+2) and b(n,l)+b(n,l+2)<2*b(n,l+1)): okR=False; print("  QR fail",n,l)
    if first_dec is not None and last_nondec is not None and last_nondec>first_dec: okR=False; print("  order fail",n)
print("(ㄹ) n<=153: all ok:",okR," premise-excluded:",prem_excl," strict-LC:",lc)
# (ㅂ) witness offset for 50<=n<=300
mp.mp.dps=30
vals=[]
for n in range(50,154):
    row=[b(n,l) for l in range(n)]
    lstar=row.index(max(row))
    v=n+1-lstar-mp.mpf('0.59963')*mp.mpf(n+1)**(mp.mpf(2)/3)-mp.mpf('1.24847')*mp.mpf(n+1)**(mp.mpf(1)/3)
    vals.append((v,n))
print("(ㅂ) 50..153: min",mp.nstr(min(vals)[0],10),"at n=",min(vals)[1]," max",mp.nstr(max(vals)[0],10),"at n=",max(vals)[1], " in [0.889,1.987]:", min(vals)[0]>=0.889 and max(vals)[0]<=1.987)
# Y/Z recurrence check (D.c50 식) vs exact b, small n
mp.mp.dps=40
def Bor(j): return mp.mpf(j)**(j-1)*mp.e**(-j)/mp.factorial(j)
def hB(x): return mp.e*Bor(x)
def YZ(k,Nmax):
    Y={m:hB(m+1) for m in range(0,k+1)}
    for m in range(k+1,Nmax+1):
        Y[m]=hB(m+1)-mp.fsum(Bor(m+1-s_)*hB(s_) for s_ in range(k+1,m+1))+k*mp.fsum(Bor(m+1-s_)*Y[s_-1]/s_ for s_ in range(k+1,m+1))
    return Y
maxerr=0
for k in (2,3,5,8,12):
    Nmax=2*k+1
    Yk=YZ(k,Nmax); Yk1=YZ(k+1,Nmax)
    Z={k:mp.mpf(0)}
    for n in range(k+1,Nmax+1):
        Z[n]=mp.fsum(Bor(n+1-s_)*(Yk1[s_-1]+k*Z[s_-1])/s_ for s_ in range(k+1,n+1))
    for n in range(k+1,Nmax+1):
        ex=mp.mpf(b(n,k))*mp.e**(-n)/mp.factorial(n); exY=mp.mpf(A_(n,k-1))*mp.e**(-n)/mp.factorial(n)
        maxerr=max(maxerr,abs(Z[n]/ex-1),abs(Yk[n]/exY-1))
print("Y/Z recurrence vs exact (k<=12, n<=2k+1): max rel err",mp.nstr(maxerr,5))
# pi_n(s) identity
n,s_=37,25
lhs=Fr(math.comb(n,s_)*s_**(s_-1)*p(n-s_),p(n)); rhs=Bor(n+1-s_)*hB(s_)/hB(n+1)
print("pi_n(s) identity rel diff:",mp.nstr(abs(mp.mpf(lhs.numerator)/lhs.denominator/rhs-1),5))
# m(n) check: max{m>=171: m^{3/2}+9m<=n} vs integer m^3<=(n-9m)^2
for n_ in (20001,30000,50000):
    m1=max(m for m in range(171,n_) if m**1.5+9*m<=n_); m2=max(m for m in range(171,n_//9) if m**3<=(n_-9*m)**2)
    print("m(n)",n_,m1,m2)
print("time",round(time.time()-t0,1))
