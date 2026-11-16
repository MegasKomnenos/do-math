# D.band-LP (가)(나)의 닫힌 꼴 값을 9.4절·6장의 정의로 다시 계산한다(mpmath 30자리 점 평가; 대조용).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import mpmath as mp
mp.mp.dps = 30
def u(k): k=mp.mpf(k); return 3/mp.mpf('0.35')*(mp.mpf('1.35')+1/k)*(mp.mpf('0.65')-1/k)**(-1.5)/mp.sqrt(k)
def Ups(k): k=mp.mpf(k); return (k-1)*u(k)/(2*k+1)
def v(k):
    kk=mp.mpf(k); vp = max(k+1,4000); io_ = 2*k+1-vp
    return 2-2*min(1, 3*vp*mp.mpf(io_)**(-1.5)) - 2*u(k) - mp.mpf('50.62')/mp.sqrt(kk-1)
def rhoH(k,nu): k=mp.mpf(k); return ((1-3/(2*k))*mp.mpf('0.307')*k/(k+nu-1) - mp.mpf(47)/(24*k))/k
def rhoL(k,nu): k=mp.mpf(k); return mp.mpf(3)/2*nu/(k*(k+nu))*(1-mp.mpf('1.2')/k)
def rhomin(k,nu):
    if nu>k: return max(0, rhoH(k,nu))
    return max(0, min(rhoH(k,nu), rhoL(k,nu)))
def Y(k,nu): r=rhomin(k,nu); return k*r*v(k) - Ups(k)*(1-(k+1)*r)
k=6668
mu = Ups(k)/(mp.mpf(3)/2*(1-mp.mpf('1.2')/k)*(v(k)+Ups(k)*(k+1)/k))
print("v(6668)", v(6668), "Ups", Ups(6668))
print("(가) k mu/(1-mu)", k*mu/(1-mu), "<= 0.1113k =", mp.mpf('0.1113')*k, "; k^(1/3) mu/(1-mu)", mp.mpf(k)**(mp.mpf(1)/3)*mu/(1-mu), "; Y(3k+1)", Y(k,k+1))
def Fk(k,nu): return Y(k,nu) + (1-mp.mpf(1)/k)**nu/20
for kk in (38886,38887,38888): print("(나) F_k(103) k=%d"%kk, Fk(kk,103))
print("Ups(48966)", Ups(48966), (1-mp.mpf(1)/48966)**103/20)
# nu_0 check at k=6668: ceil(k mu/(1-mu)) vs 3.6 k^(2/3)
print("3.6k^(2/3)", mp.mpf('3.6')*mp.mpf(k)**(mp.mpf(2)/3))
