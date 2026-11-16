# 검토전체6 L5: 6.6절 수치 재계산
from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, findroot
mp.dps = 30
def Bor(n): return exp(-n)*mpf(n)**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
def Psi(d): return sum(Ren(j) for j in range(1, d+1))
print("Psi(14) =", Psi(14), " Psi(14)/(2e) =", Psi(14)/(2*e))
k = mpf(3131)
f1 = sqrt(2*pi)*(k+15)**1.5*Bor(3146); f2 = (k/(k+15))**1.5; f3 = (k+1)/(k+14)
print("세 인자 곱 k=3131:", f1*f2*f3, " (본문 0.98872)", " 전체:", f1*f2*f3*Psi(14)/(2*e), "(>=0.4345)")
ups = mpf(0.5)+5/(2*k)+1/(4*k*k); gW = 2*exp(mpf(0.0031))/e
print("gamma_W =", gW, " ups*gW(3131) =", ups*gW, " (<=0.3697)")
def u(k):
    k=mpf(k); return 3/mpf(0.35)*(mpf(1.35)+1/k)*(mpf(0.65)-1/k)**(-mpf(1.5))/sqrt(k)
for kk in (3131, 10001):
    kk=mpf(kk); up=mpf(0.5)+5/(2*kk)+1/(4*kk*kk)
    print("d(%d) =" % int(kk), gW*up + u(kk)/(e*2**mpf(1.5)), " parts:", gW*up, u(kk)/(e*2**mpf(1.5)))
# h(D) max
import mpmath
h = lambda D: (1-D)*(1+(e-2)*D)/(2-D)
Ds = [mpf(i)/10000 for i in range(0,10001)]
print("max h(D) =", max(h(D) for D in Ds), " (<=0.509)")
print("(1+7/3131)*0.509 =", (1+mpf(7)/3131)*mpf(0.509))
print("(e+3/4)/3131 =", (e+mpf(0.75))/3131, " 6.03/3131=", mpf(6.03)/3131, " 3.51/3131=", mpf(3.51)/3131)
print("log2+0.00113+0.00193 - log2 =", 0.00113+0.00193)
# Ren(d+1)/Psi(d) >= 1/(5d) for d>=14 check
print("min Ren(d+1)/Psi(d)*5d, d=14..200:", min(Ren(d+1)/Psi(d)*5*d for d in range(14,201)))
