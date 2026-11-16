# 검토전체6 L2: 중앙 상쇄 항등식 int F0 = 0, int F1 = 46 sqrt2 - 12, J 선도 적분 3 sqrt(2pi) 수치 확인
import mpmath as mp
mp.mp.dps=20
ninf=2/mp.sqrt(mp.pi)
def Daw(b): # e^{-b^2/2} int_0^b e^{v^2/2} dv
    return mp.e**(-b*b/2)*mp.sqrt(mp.pi/2)*mp.erfi(b/mp.sqrt(2))
def BldR(b): return mp.e**(b*b/2)*(2-2*b*Daw(b))
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z):
    inner=mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z,r)*BldR(r*z)/mp.sqrt(2*mp.pi),[0,1])
    return -ninf*z**4*mp.e**(-z*z)*inner
def F1(z):
    inner=mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z,r)*(mp.mpf(4)/3*r*r*z*z-mp.mpf(2)/3*r*z**4),[0,1])
    return -ninf*z**4*mp.e**(-z*z)*inner
I0=mp.quad(F0,[-10,-3,0,3,10]); I1=mp.quad(F1,[-10,-3,0,3,10])
print("int F0 =",I0); print("int F1 =",I1," 46sqrt2-12 =",46*mp.sqrt(2)-12)
cJ=mp.quad(lambda z: z**3*mp.e**(-z*z/2)*mp.quad(lambda r: r*((2-r**3)/3*z**3-r*z),[0,1]),[-12,0,12])
print("J 선도 적분 =",cJ," 3sqrt(2pi)=",3*mp.sqrt(2*mp.pi))
