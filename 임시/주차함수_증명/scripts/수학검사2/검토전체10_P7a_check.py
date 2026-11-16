# P7a 검산: 7.4절 수치 몇 가지
from fractions import Fraction as F
import math

# (a) pair-check-10000: 경우의 수와 최솟값
k=10000
def exbar(q):
    ps=F(q*(q-1),2*(k+1))
    return q+(k+q)*ps/(1-ps)
cnt=0; best=None
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,q,qp,j)
print("pair-check cases",cnt,"min",float(best[0]),best[1:])

# (b) integer-strips 비교 수
c1=sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100) if 2*k+40>=max(20001,2*k+1))
c2=sum(2*k+102-max(2*k+41,20001)+1 for k in range(9950,12000))
c3=sum(102-59+1 for k in range(12000,13000))+sum(102-80+1 for k in range(13000,14000))+sum(102-96+1 for k in range(14000,15000))
print("integer-strips (가)",c1,"(나)+(다)",c2+c3,"(나)",c2,"(다)",c3)

# (c) hermite-nu (라): U_r, V_r 검사 (정확 유리수, y=k)
def check(k,nu,d):
    n=2*k+nu; y=F(k); N=n+y+1
    # He_n, He_{n-1} symbolic via d: He_n=(n+d)*He_{n-1}; set He_{n-1}=1
    He={n-1:F(1), n:n+d}
    for j in range(n-1,n-6,-1):  # He_{j-1}=(N He_j - He_{j+1})/(y j)
        He[j-1]=(N*He[j]-He[j+1])/(y*j)
    def M(r):
        s=F(0)
        for i in range(r+2):
            s+=F(math.comb(r+1,i))*(-1)**i*F(math.perm(n,i))*He[n-i]
        return s
    M0=M(0)
    U2=1+F(2*nu+2,k)+F(nu*(nu+1),k*k); V2=4+F(4*nu+2,k)+F(nu*(nu+1),k*k)
    U4=1+F(4*nu+16,k)+F(6*nu*nu+30*nu+18,k**2)+F(4*nu**3+17*nu**2+15*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    V4=4+F(12*nu+38,k)+F(13*nu*nu+49*nu+22,k**2)+F(6*nu**3+21*nu**2+17*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    return (M(2)/M0==U2-V2/d, M(4)/M0==U4-V4/d)
for (kk,nu,d) in [(50,3,F(7,3)),(37,1,F(4)),(60,-1,F(11,3)),(60,0,F(5,2)),(100,600,F(39,10))]:
    print("UV check",kk,nu,d,check(kk,nu,d))

# (f) 꼬리 삼중 (10^4,120,0.54): F_tf(q)>=0 ? (부동소수점 점검)
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
def Fcheck(K1,M,tf):
    ke=3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    mn=min(tf*q**1.5-math.exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(q-1)) for q in range(2,M+1))
    return mn
for t in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    print("triple",t,"min F",Fcheck(*t), "tf M^1.5",t[2]*t[1]**1.5)

# (g) lb_{K1} 껍질 검사 (부동소수점)
def lbmin(K1,M,tf,nu):
    k=K1
    def exh(q):
        if q==1: return 1.0
        nh=tf*q**1.5/k; return q+(k+q)*nh/(1-nh)
    mn=1e9
    for q in range(1,nu):
        for qp in range(1,nu-q+1):
            j=nu-q-qp
            if q>M or qp>M: return None
            v=1-j/k*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
            mn=min(mn,v)
    return mn
for (K1,M,tf,nuP) in [(12000,120,0.54,93),(15000,120,0.54,102),(20000,120,0.54,115),(10**5,300,0.522,228),(10**6,700,0.519,590)]:
    print("lb",K1,nuP,lbmin(K1,M,tf,nuP),lbmin(K1,M,tf,nuP+1))

# (h) n_M 비
print("nM ratios",20507/841**1.5,73032/2000**1.5, 0.8165*841**1.5)
# polar-PD 수치
print("polarPD",2*math.exp(-5.3146*0.6996),0.3**1.5/2,0.7*2001/2002,math.ceil(2002**(4/3)),0.0821*math.exp(-3/25233), math.log(2/0.0820)/0.6996)
