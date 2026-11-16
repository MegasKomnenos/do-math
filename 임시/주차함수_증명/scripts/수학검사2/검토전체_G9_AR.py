# G9 독립 검산: 9.3절 정리 old-7-16의 (1) L_*(6668), (2) d_k 상계 함수, (3) 요구값; 9.1절 head-sum-1의 끝점 수치
from mpmath import mp, mpf, quad, sqrt, exp, log, ceil, floor, e, pi
mp.dps = 30
k = mpf(6668)
def J1(k):
    f = lambda t: (1+t+2/k)**(-mpf(7)/2) * max(0, 1-3*k**(-mpf(1)/2)*(t-1/k)**(-mpf(3)/2))
    t0 = 1/k + (3*k**(-mpf(1)/2))**(mpf(2)/3)
    return mpf(5)/2*quad(f, [t0, (t0+1)/2, 1])
def J2(k):
    c = 3*(k-1)*k**(-mpf(3)/2)
    f = lambda t: (1+t+1/k)**(-mpf(7)/2) * max(0, 1-c*(t-1/k)**(-mpf(3)/2))
    t0 = 1/k + c**(mpf(2)/3)
    return mpf(5)/2*quad(f, [t0, (t0+(k-1)/k)/2, (k-1)/k])
J3 = (k/(2*k+1))**(mpf(5)/2)*(1-3/sqrt(k))
J4 = (k/(2*k+1))**(mpf(5)/2)*(1-3/sqrt(k-1))
print("J1,J2,J3,J4 =", J1(k), J2(k), J3, J4)
print("L_*(6668) =", J1(k)+J2(k)+J3+J4)
# (2) d_k bound function
best = 0; bq = None
for q in range(1, int(k)):
    N = k+q
    num = min(1, 3*k*q**(-mpf(3)/2))
    den = k*(mpf('0.734')*max(0,(q+1)**(-mpf(1)/2)-(ceil(N/2)+1)**(-mpf(1)/2)) + mpf('0.98')/(N+1))
    v = num/den*sqrt(k)
    if v > best: best, bq = v, q
print("max sqrt(k)*ratio =", best, "at q=", bq)
# (3) requirement values
db = mpf('6.62')/sqrt(k)
band = (1+db/2)/(1-db/2)
bulk = 1 + (1+1/mpf('1.48'))*db/(2-db) + (1/mpf('1.48'))*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**(mpf(3)/2))
print("band need =", band, "bulk need =", bulk)
# first-interval condition at k=6668
jstar = ceil((3*k)**(mpf(2)/3))
print("4.85*[sqrt(k)((3k)^{2/3}+2)^{-1/2}-sqrt2] =", mpf('4.85')*(sqrt(k)*((3*k)**(mpf(2)/3)+2)**(-mpf(1)/2)-sqrt(2)))
print("third interval endpoints:", mpf('16.35')*((k+1)/(mpf('0.95')*k))**(mpf(3)/2)/(mpf('0.05')*k)*k, mpf('5.45')*(1+1/k)**(mpf(3)/2)*k/(k-jstar-1))
# head-sum-1 endpoint
u0 = mpf(3132)**(-mpf(1)/3); xi = mpf(1); l0 = mpf(3131)
inv = 1+1/l0
c1 = (1+xi*u0*inv)**(mpf(3)/2)*exp(inv*u0**3/12)
uq = inv**2*(xi*u0+u0**3)**2/2
Phi = inv*c1*exp(uq)*(mpf('0.11399')*xi**(mpf(7)/2)+mpf('0.15958')*xi**(mpf(5)/2)*u0**2+mpf('0.85108')*xi**3*u0)
den = mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u0
Ebar = c1*inv*((mpf('0.5320')*xi**(mpf(3)/2)*u0+c1*(mpf('0.625')*xi**2+xi*u0**2))/den + mpf('5.68e-4'))
Lbar = den*exp(-Ebar)/(1+(xi*u0+u0**3)*inv)
print("u0,c1,uq,Phi,Ebar,Lbar,R =", u0, c1, uq, Phi, Ebar, Lbar, Phi/Lbar)
# c5 check
xi=mpf('0.03'); print("c5 =", mpf('0.7979')*sqrt(xi)*u0**3/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u0))
# old-7-26 (i)
print("k rho^L(0.112k) <=", mpf('1.5')*mpf('0.112')/mpf('1.112'), " k rho^H >=", (1-mpf(1.5)/k)*mpf('0.307')/mpf('1.112')-mpf(47)/(24*k))
