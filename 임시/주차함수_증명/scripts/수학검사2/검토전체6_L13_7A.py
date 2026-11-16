# L13: 부록D_장7A 수치 검산
from fractions import Fraction as F
import math
# 1. 열 인증 비교 수
def B(k): return -(-k*k//4)
d1=sum(2*B(k)-2*k for k in range(121,161)); d2=sum(2*B(k)-2*k for k in range(161,501))
b1=sum(B(k)+1 for k in range(121,161)); b2=sum(B(k)+1 for k in range(161,501))
print("직접차분", d1, d2, "띠", b1, b2)
# 2. 정수 부등식
L=10**21*400**10; R=17**21*123**10
print("L",L, "%.6e"%L, "R", R, "%.6e"%R, L>R)
print("40/41*(10/17)^2.1 =", 40/41*(10/17)**2.1, ">0.3?")
# 3. c = 0.34+0.65 ln k
for k in (121,125.5,160,495.5,500): print(k, 0.34+0.65*math.log(k))
# 4. cor-S-prime 세 값 (표의 올림값)
for k0,y,A0,B0 in ((501,F(13,100),F('1.4708'),F('0.098505')),(1855,F(2,25),F('2.5335'),F('0.060259')),(6098,F(11,200),F('2.7354'),F('0.0422'))):
    xi=F(1,k0); v=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    vtx=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print(k0, float(v), "꼭짓점", float(vtx), "<=", float(y), "y k^2-2k-1=", float(y*k0*k0-2*k0-1))
# 5. k_R: max(2j*+2, ceil(L^{j*+2}/a°_{j*+1}))
def ao(m): return F((m+1)**(m-1), math.factorial(m))
for L_,j in ((F(267,100),82),(F(27,10),220),(F(271,100),490)):
    # j* = max{m: e^{g(m+1)} < L}, e^{g(m+1)} = a°_{m+1}/a°_m
    m=0
    while ao(m+2)/ao(m+1) < L_: m+=1
    jstar=m
    kR=max(2*jstar+2, math.ceil(L_**(jstar+2)/ao(jstar+1)))
    print("L",L_,"j*",jstar,"k_R",kR)
# 6. x_k = (k/(k+1))^{k-1}
for k in (501,1855,6098): print("x_k", k, (k/(k+1))**(k-1))
# 7. psi_1 at k=1e7
k=1e7; print("psi1", 1-(2/3)*math.sqrt(2)*k**(-1/6)-k**(-1/3)/(1-math.sqrt(2)*k**(-1/6)))
# 8. Gamma(5/3)
print("Gamma(5/3)", math.gamma(5/3))
# 9. 6*0.95^2/e
print(6*0.95**2/math.e)
# 10. A''-3 numbers
print("ln 1e30", math.log(1e30), "2*39.0859", 2*39.0859)
# 11. 2-2/(n_X+1) for k=23462, 6e5
for k in (501,23462,359561,600000,1.7316e6): nX=math.ceil(k**(4/3)); print(k, nX, 2-2/(nX+1))
# 12. D.xcert: Xc
pc=(2*math.pi)**-0.5/math.e
S0=sum((n-1)**(n-1)*math.exp(-n)/math.factorial(n) if n>1 else math.exp(-1) for n in range(1,257))
print("S0",S0,"Xc",1-S0-2*pc/math.sqrt(257)+pc*257**-1.5)
# 13. seed cert: seed interval counts
for k,kk,d in ((2,8,13),(8,24,43),(34,68,189),(120,240,709)): print(k, kk, d+k+1-1, "count", d+k+1-kk)
