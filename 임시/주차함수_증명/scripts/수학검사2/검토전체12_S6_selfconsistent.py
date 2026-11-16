# 검토전체12 S6: 정리 self-consistent-S (다) 표와 따름정리 cor-S-prime 세 값의 재계산
from mpmath import mp, mpf, e as E, ceil, log, exp, factorial
mp.dps = 60
def a0(m):  # 𝔞°_m = (m+1)^{m-1}/m!
    return mpf(m+1)**(m-1)/factorial(m)
def free_ratio(m):  # e^{g(m+1)} = (1+1/(m+1))^m = a0(m+1)/a0(m)
    return (1+mpf(1)/(m+1))**m
def jstar(L):
    m=0
    while free_ratio(m)<L: m+=1
    return m-1
def xk(k): return (mpf(k)/(k+1))**(k-1)
ranges=[(mpf(267)/100,25,501,mpf(13)/100),(mpf(27)/10,70,1855,mpf(2)/25),(mpf(271)/100,100,6098,mpf(11)/200)]
for L,J,k0,yy in ranges:
    js=jstar(L)
    kR=max(2*js+2, int(ceil(L**(js+2)/a0(js+1))))
    EJ=sum(a0(J+i)/a0(J)*exp(-i) for i in range(1,k0-js+1))
    Einf=(L/E)*(1-(L/E)**k0)/(1-L/E)
    R=max(1/(1+EJ),1/(1+Einf))
    def xbar(kap): return a0(kap)*L**(-(kap+1))
    def qlow(kap): return max(mpf(0),1-sum(a0(j)*L**(-(j+1)) for j in range(kap)))
    Xi=sum(max(mpf(0),xbar(kap)-R*qlow(kap)) for kap in range(J))
    Xik=sum(max(mpf(0),a0(kap)*xk(k0)*L**(-kap)-R*qlow(kap)) for kap in range(J))
    A0=xk(k0)+Xik/(L*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    xi=mpf(1)/k0
    val=(yy-xi)*(yy-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*yy)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R={mp.nstr(R,10)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik,8)} A0={mp.nstr(A0,8)} B0={mp.nstr(B0,8)} 1/(1+EJ)={mp.nstr(1/(1+EJ),8)} 1/(1+Einf)={mp.nstr(1/(1+Einf),8)}")
    print(f"   cor-S-prime value at k0 = {mp.nstr(val,6)}, vertex/k^2 = {mp.nstr(vert,6)} <= y={yy}")
# 𝗍_k, n♯_k 점검 및 𝔬_k 범위
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in [2,3,10,41,100,501,2000]:
    t=tk(k); print(f"k={k}: t_k={t}, n#_k={k+(k+1)*t}, o_k={mp.nstr(-2*log(1-mpf(1)/k)/log(1+mpf(1)/k),8)}")
# 열 인증 (가)의 정수 부등식
print("10^21*400^10 > 17^21*123^10 :", 10**21*400**10 > 17**21*123**10, 10**21*400**10, 17**21*123**10)
print("hf(17/10)+2 lower:", mp.nstr(mpf(17)/10+mpf(40)/41*(mpf(10)/17)**(mpf(21)/10),8))
print("hf' lower at k=41:", mp.nstr(1-mpf(21)/10*(mpf(10)/17)**3,6))
# polar-N 수치
k=2001
print("2k^1.5+1 at 2001:", mp.nstr(2*mpf(k)**1.5+1,10), " 0.3476k^2:", mp.nstr(mpf('0.3476')*k*k,10))
print("2/sqrt(2001)=",mp.nstr(2/mp.sqrt(2001),6)," e^{-1+2/2002}=",mp.nstr(exp(-1+mpf(2)/2002),6), " e^-0.0448=",mp.nstr(exp(mpf('-0.0448')),6))
print("y^2/(12(1-y^2)) at y=.0448:", mp.nstr(mpf('0.0448')**2/(12*(1-mpf('0.0448')**2)),6))
# riccati 반례 (k,z,n)=(3,1,2): 좌변 4, 우변 5
from mpmath import taylor
