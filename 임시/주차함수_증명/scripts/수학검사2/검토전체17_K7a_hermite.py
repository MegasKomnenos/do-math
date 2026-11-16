# K7a: 보조정리 hermite-nu (라)·(마) 닫힌 꼴의 정확 유리수 검산 (작은 k, nu)
from fractions import Fraction as F
from math import comb
def He_list(N, y, n):
    He=[F(1), F(N)]
    for j in range(2, n+1): He.append(N*He[j-1]-(j-1)*y*He[j-2])
    return He
def M_ratio(i, y, n):
    N=n+y+1; He=He_list(N,y,n)
    def coef(p):  # [Y^n](1-Y)^p B
        return sum(comb(p,r)*(-1)**r*He[n-r]/F(1) / __import__('math').factorial(n-r) for r in range(0,p+1))
    return coef(i+1)/coef(1), He
for k,nu in [(50,3),(40,7),(60,-1),(60,0)]:
    n=2*k+nu; y=F(k)
    r2,He=M_ratio(2,y,n); r4,_=M_ratio(4,y,n)
    d=He[n]/He[n-1]-n
    U2=1+F(2*nu+2,k)+F(nu*(nu+1),k**2); V2=4+F(4*nu+2,k)+F(nu*(nu+1),k**2)
    U4=1+F(4*nu+16,k)+F(6*nu**2+30*nu+18,k**2)+F(4*nu**3+17*nu**2+15*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    V4=4+F(12*nu+38,k)+F(13*nu**2+49*nu+22,k**2)+F(6*nu**3+21*nu**2+17*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    print(k,nu,"M2/M0 ok:", r2==U2-V2/d, " M4/M0 ok:", r4==U4-V4/d, " d=",float(d))
# (마) 일반 y
k,nu=50,5; n=2*k+nu; y=F(k)-F(1,2)
r2,He=M_ratio(2,y,n); d=He[n]/He[n-1]-n
print("general y:", r2==1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))
