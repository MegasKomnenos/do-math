# F8: closed-form-envelope (다)(라) 수치 — q_{6600,6600}(xi), e^{-j_inf}, 상수들
import math
c=(2*math.pi)**-0.5
z12=-1.46036; zm12=-0.20789; z32=2.61238   # 구간 끝 (보수적 선택은 아래에서 따로)
cpsi=-z12+z32/12
def Psilow(r):
    if r<1: return 0.0
    return c*(2*math.sqrt(r)-cpsi+1/(2*math.sqrt(r))-r**-1.5/24)
def pieces(xi,k):
    q=xi*k**(2/3); p=q-1; n=k+q; kk=k+1; eps=k**(-1/3)
    H=2/3*p**1.5+0.5*p**0.5+zm12+p**-0.5/24
    E=2*c*math.exp(-1/(12*q))*xi**-0.5*(1+xi*eps)
    R1=1.5*c*(2*math.sqrt(p)-1)*k**(-2/3)
    R2=15/8*c*n**2.5*H/(kk**3.5*k**(2/3))
    D1=p/k**(2/3)
    D2=kk*math.sqrt(2/math.pi)*p**-0.5*k**(-2/3)
    D3=1.5*kk*Psilow(p)/((n+1)*k**(2/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
def jinf(xi): return 4/3*c*xi**1.5
for xi in (2.0,2.1):
    print("xi=",xi,"q6600=",qkk(xi,6600),"e^-jinf=",math.exp(-jinf(xi)))
print("k->: q(2,k) for k in 6600,7000,1e4,1e6:",[qkk(2.0,k) for k in (6600,7000,1e4,1e6)])
print("q(0.2,6600)=",qkk(0.2,6600))
# (다) 상수
k=6600.; eps=k**(-1/3); q=2*k**(2/3); p=q-1; mu=1/q
print("0.480085:",0.5*(math.sqrt(1-mu)-(1+p**-0.5)*eps/math.sqrt(2)))
print("0.0314973:",(eps/math.sqrt(2))/(3*c))
print("0.5001779:",0.5*(1+1/(4*p)))
print("0.46959:",0.5-1.5*mu-0.75*eps/math.sqrt(2))
print("4.37993:",1+(2**1.5-2**0.5*k**(-2/3))/(2*c)-1.5*2*eps)
print("0.02536:",0.146751-0.5316752/4.37993)
print("rG:",0.38951*0.7202/19.4319**2)
print("Lambda'(1)-0.85sqrt2:",2.75+z12-0.85*math.sqrt(2))
print("0.339049:",0.85*c*6600/6601)
print("case2 coeffs:",0.020044*0.169524*math.sqrt(0.2),0.953386*0.169524*math.sqrt(0.0005))
print("(4c)^(2/3):",(4*c)**(2/3))
