# Q2: 4장 수치 검산 — 중앙 상쇄 항등식 int F0 = 0, int F1 = 46 sqrt2 - 12, J 선도 적분, 상수 -2/3, Robbins 질량 부등식
import mpmath as mp
mp.mp.dps = 15
def Bld(b):  # Bor^ld_R(beta) = e^{b^2/2}(2 - 2 b D(b)),  D(b) = e^{-b^2/2} int_0^b e^{v^2/2} dv = e^{-b^2/2} sqrt(pi/2) erfi(b/sqrt2)
    I = mp.sqrt(mp.pi/2)*mp.erfi(b/mp.sqrt(2))
    return 2*mp.e**(b*b/2) - 2*b*I
def Bld_def(b): return 2+mp.quad(lambda w: w**(-1.5)*(1-mp.e**(b*b*w/2)), [0,1])
print("Bld check:", Bld(mp.mpf('0.7')), Bld_def(mp.mpf('0.7')), flush=True)
ninf = 2/mp.sqrt(mp.pi)
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z,r)*Bld(r*z)/mp.sqrt(2*mp.pi), [0,1])
def F1(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z,r)*(mp.mpf(4)/3*r*r*z*z-mp.mpf(2)/3*r*z**4), [0,1])
print("int F0 =", 2*mp.quad(F0,[0,1,2,3,4,6,9]), flush=True)
print("int F1 =", 2*mp.quad(F1,[0,1,2,3,4,6,9]), " 46sqrt2-12 =", 46*mp.sqrt(2)-12, flush=True)
print("3sqrt(2pi) =", 3*mp.sqrt(2*mp.pi), mp.quad(lambda z: z**3*mp.e**(-z*z/2)*(mp.mpf(4)/15*z**3-z/3), [-mp.inf, mp.inf]), flush=True)
s = mp.nsum(lambda j: mp.e**(j*mp.log(j)-j-mp.loggamma(j+1)) - j**(-0.5)/mp.sqrt(2*mp.pi), [1, mp.inf])  # j*Bor(j) = j^j e^-j / j!
print("sum(jBor(j)-(2pi)^-1/2 j^-1/2) =", s, " target -2/3-(2pi)^-1/2 zeta(1/2) =", -mp.mpf(2)/3 - mp.zeta(0.5)/mp.sqrt(2*mp.pi), flush=True)
for j in (1,2,5,10,100):
    b = mp.e**((j-1)*mp.log(j)-j-mp.loggamma(j+1)); m=(2*mp.pi)**-0.5*mp.mpf(j)**-1.5
    print(j, "Bor<=main:", m-b >= 0, " gap<=main/(12j):", (m-b) <= m/(12*j), flush=True)
