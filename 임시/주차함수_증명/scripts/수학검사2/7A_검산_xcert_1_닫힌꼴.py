"""D.xcert-partAB (5)의 닫힌 꼴 상계·하계(upsilon>60, tl_J, tb1/tb3/tbh/tw1/Shat, 계수 1.5/4.4/0.66)와 (6)의 수치 상수를 mpmath로 대조."""
from mpmath import mp, mpf, quad, exp, sqrt, e, pi, inf, gamma, log, cos, sin
mp.dps = 30
def tb1(u): return quad(lambda y: y**mpf(-1.5)*(exp(u*y)-1), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def tb3(u): return quad(lambda y: (1-y)*y**mpf(-1.5)*(exp(u*y)-1), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def tbh(u): return quad(lambda y: y**mpf(-0.5)*exp(u*y), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def tw1(u): return quad(lambda y: (1-y)*y**mpf(-0.5)*exp(u*y), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def tpj(j,u): return quad(lambda y: y**(j-mpf(1.5))*exp(u*y), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def twv(v,u): return quad(lambda y: (1-y)*y**(v-mpf(1.5))*exp(u*y), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def Sh(u): return quad(lambda y: y**mpf(-0.5)*(1-y)**2*(1+y)**-2*exp(u*y), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.5, 1])
def tlJ_true(u): return exp(-u)*quad(lambda y: y**mpf(-1.5)*(exp(u*y)-1), [0, 1e-10, 1e-6, 1e-3, 0.1, 0.25, 0.5])
def tlJ_text(u): return 2*e*sqrt(u)*exp(-u) + mpf('2.83')*exp(-u/2)/u + 2*sqrt(u)*exp(-mpf(3)*u/4)
def tlJ_code(u): return 2*e*sqrt(u)*exp(-u) + exp(-u/2)*(2*sqrt(2)/u + 6*sqrt(2)/u**2 + 480/u**3) + 2*sqrt(u)*exp(-mpf(3)*u/4)
print("== tl_J: 참값 / 글(2.83e^{-u/2}/u) / 코드(2sqrt2/u+6sqrt2/u^2+480/u^3) ==")
for u in (6, 10, 20, 26, 30, 40, 60, 61, 80, 100, 150):
    t = tlJ_true(u); a = tlJ_text(u); b = tlJ_code(u)
    print("u=%4d true=%.6e text=%.6e (text/true=%.4f) code=%.6e (code/true=%.4f)" % (u, t, a, a/t, b, b/t))
print("== 닫힌 꼴 상계 (u>60), 비 = 상계/참값 (>=1 이어야) ==")
for u in (60, 61, 70, 100, 200):
    u = mpf(u)
    r1t = (1/u+mpf('1.5')/u**2+mpf('8.8')/u**3+tlJ_text(u))/(exp(-u)*tb1(u))
    r1c = (1/u+mpf('1.5')/u**2+mpf('8.8')/u**3+tlJ_code(u))/(exp(-u)*tb1(u))
    r3t = (1/u**2+3/u**3+mpf('26.4')/u**4+tlJ_text(u))/(exp(-u)*tb3(u))
    r3c = (1/u**2+3/u**3+mpf('26.4')/u**4+tlJ_code(u))/(exp(-u)*tb3(u))
    rh = (1/u+mpf('0.5')/u**2+mpf('1.32')/u**3+sqrt(2)*exp(-u/2))/(exp(-u)*tbh(u))
    rw1t = (1/u**2+1/u**3+4/u**4+tlJ_text(u))/(exp(-u)*tw1(u))
    rw1c = (1/u**2+1/u**3+4/u**4+tlJ_code(u))/(exp(-u)*tw1(u))
    rS = (mpf(1)/4*(2/u**3+9/u**4+mpf('55.2')/u**5+168/u**6+525/u**7)+sqrt(2)*exp(-u/2))/(exp(-u)*Sh(u))
    rp = min((1/u)/(exp(-u)*tpj(j,u)) for j in range(2,10))
    rw = min((1/u**2)/(exp(-u)*twv(v,u)) for v in range(2,9))
    print("u=%3d tb1:text %.6f code %.6f | tb3:text %.6f code %.6f | tbh %.6f | tw1:text %.6f code %.6f | Shat %.6f | min tp_j(j>=2) %.4f | min tw_v(v>=2) %.4f"
          % (u, r1t, r1c, r3t, r3c, rh, rw1t, rw1c, rS, rp, rw))
print("== 하계 e^{-u}tb1 >= 1/u+1.5/u^2-3e^{-u} (u>=6), 비 = 참/하계 (>=1) ==")
for u in (6, 8, 10, 20, 60, 100):
    u = mpf(u); print("u=%3d ratio %.6f" % (u, exp(-u)*tb1(u)/(1/u+mpf('1.5')/u**2-3*exp(-u))))
print("== 계수 검사: (1-t)^{-3/2} <= 1+1.5t+4.4t^2, (1-t)^{-1/2} <= 1+t/2+0.66t^2 on [0,1/2] ==")
import numpy as np
ts = np.linspace(0, 0.5, 5001)
print("max (1-t)^-1.5 - (1+1.5t+4.4t^2):", max((1-t)**-1.5-(1+1.5*t+4.4*t*t) for t in ts))
print("max (1-t)^-0.5 - (1+t/2+0.66t^2):", max((1-t)**-0.5-(1+t/2+0.66*t*t) for t in ts))
print("== (6) 상수 ==")
c0 = 1/sqrt(2*pi)/e
S0 = sum(mpf(n-1)**(n-1)*exp(-n)/mp.factorial(n) for n in range(1, 257))
S1 = sum(n*mpf(n-1)**(n-1)*exp(-n)/mp.factorial(n) for n in range(1, 257))
Xc = 1 - S0 - 2*c0/sqrt(257) + c0*mpf(257)**mpf(-1.5)
print("S^(0)=%.12f  S^(1)=%.10f  Xc=%.9f" % (S0, S1, Xc))
s1 = mpf('39.08599253547307')
print("Xc/(1+1.5/s1)=%.6f ; Xc(1+1e-13)/(1+1.5/s1-3 s1 e^-s1)=%.6f ; limit s->inf %.6f" % (Xc/(1+mpf('1.5')/s1), Xc*(1+mpf('1e-13'))/(1+mpf('1.5')/s1-3*s1*exp(-s1)), Xc))
print("Im_min at phi=0.5: %.6f ; at 1.5: %.6f" % (exp(-1)*0.5-0.125*mpf('0.4982')/6, exp(-1)*1.5-3.375*mpf('0.4982')/6))
print("zone B 0.1853 check: e^-1-0.01627-c0 e^eta257 pi sqrt(pi)/20^1.5 - 2pi/40 = %.6f" % (exp(-1)-mpf('0.01627')-c0*exp(mpf(5)/(12*257)+mpf(1)/(6*257*256))*pi*sqrt(pi)/mpf(20)**mpf(1.5)-2*pi/40))
print("2^{3/2}/3 = %.6f (글 0.943) ; 2^{3/2}/(3 (5/3)^{3/2}) = %.5f (글 0.438)" % (2*sqrt(2)/3, 2*sqrt(2)/3/(mpf(5)/3)**mpf(1.5)))
print("t at eps=1/8: ", mp.findroot(lambda t: -t-log(1-t)-mpf(1)/8, 0.42), " ; sqrt(2eps/(1+4/3 sqrt(2eps))) at eps=1/8:", sqrt(mpf(0.25)/(1+mpf(4)/3*mpf(0.5))))
t=mpf('0.387'); print("eps - t^2/2 at t=0.387 (>=0.0194?):", -t-log(1-t)-t*t/2)
print("n_X(501)=ceil(501^{4/3}) :", mpf(501)**(mpf(4)/3))
# 0.12 term: sum_{n<=N} n pr0_n vs 2 c0 e^{eta_257} sqrt(N) (+0.12)
eta257 = mpf(5)/(12*257)+mpf(1)/(6*257*256)
worst = -1; 
acc = mpf(0)
for n in range(1, 20001):
    acc += n*mpf(n-1)**(n-1)*exp(-n)/mp.factorial(n) if n <= 2000 else n*c0*mpf(n)**mpf(-1.5)*exp(mpf(5)/(12*n)+mpf(1)/(6*n*(n-1)))
    if n >= 256:
        d = acc - 2*c0*exp(eta257)*sqrt(n)
        if d > worst: worst, nw = d, n
print("max_N [sum_{n<=N} n pr0_n - 2 c0 e^{eta257} sqrt N] = %.5f at N=%d  (0.12 항의 필요성; >0 이면 필요)" % (worst, nw))
