# J10: 명제 old-8-33의 Stays^up(k; nubar) 를 세 가족의 첫 열에서 배정밀도로 재계산해 명제 check-na 표와 비교
import math
mS=1.15
def simpson(f,a,b,n=20000):
    if b<=a: return 0.0
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n): s+=(4 if i%2 else 2)*f(a+i*h)
    return s*h/3
def cAb(r): return 2*math.sqrt(r)/(1-r)+2*math.log((1+math.sqrt(r))/(1-math.sqrt(r)))
def Flat(y):
    ab=(mS*(y+2*y**(2/3)))**(2/3); return 2*(ab-1)/(y+2-ab)
def Sub(k,nb):
    xi=(nb+4)/(k-1)
    if xi>=0.6: return 0.0
    return (k-1)/k*simpson(lambda r:(r-xi)*(1+r)*r**-1.5*(1-r)**-2, xi, 0.6)
def Ab(y,k,nb):
    z=0.6+1/y
    return mS*(1+1/y)*(4*((mS*y)**(2/3)-1)**-0.5 + y**-0.5*(2*cAb(z)-4*z**-0.5-Sub(k,nb)))
def Top(k,nb):
    return simpson(lambda r: min(2,2+(nb+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1)
def StaysUp(k,nb):
    return sum(Flat(y)+Ab(y,k,nb) for y in (k-1,k)) + 2*16.54*k**-0.5*Top(k,nb)
for k,nb,ref in ((8065,0.48*8065,1.4194),(9551,2*9551**(2/3),1.1752),(9705,1.3*9705**(2/3),1.1507)):
    print(k, round(nb,2), "Stays^up=%.4f"%StaysUp(k,nb), "ref",ref, " pieces: Flat(k)=%.4f Ab(k)=%.4f Top=%.4f Sub=%.4f"%(Flat(k),Ab(k,k,nb),Top(k,nb),Sub(k,nb)))
# 감소 확인(표본)
for nbf in (lambda k:1.3*k**(2/3), lambda k:2*k**(2/3), lambda k:0.48*k):
    vals=[StaysUp(k,nbf(k)) for k in (6667,8000,10000,20000,50000)]
    print(["%.4f"%v for v in vals], "monotone dec:", all(vals[i]>vals[i+1] for i in range(len(vals)-1)))
print("2cAb(0.6)-4/sqrt(0.6)=",2*cAb(0.6)-4/math.sqrt(0.6))
