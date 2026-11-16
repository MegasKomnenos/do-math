# H8 2차 검토: 장8 8.2절 수치 상수 독립 재계산
from mpmath import mp, mpf, sqrt, exp, log, pi, quad
mp.dps = 30
z12 = mpf('-1.4603545088095868'); zm12 = mpf('-0.2078862249773545'); z32 = mpf('2.6123753486854883')
cPsi = -z12 + z32/12
c = 1/sqrt(2*pi)
def s(q): return mpf(4)/15*q**mpf(2.5) + mpf('0.385')*q**mpf(1.5)
def Cr(q,k): return mpf(3)/2*c*s(q)*(k+q)**mpf(1.5)*(k+1)**mpf(-3.5)
def Lam(q):
    p=q-1
    return q*(2*sqrt(p)+z12+1/(2*sqrt(p))) - (mpf(2)/3*p**mpf(1.5)+sqrt(p)/2+zm12)
def Bp(q,k): return c*Lam(q)/(k+1)
def jinf(xi): return mpf(4)/3*c*xi**mpf(1.5)
k0=mpf(6600); e0=k0**(-mpf(1)/3)
print('192행: q_min',0.2*k0**(mpf(2)/3),' sqrt p_min',sqrt(0.2*k0**(mpf(2)/3)-1),' mu',1/(0.2*k0**(mpf(2)/3)),' xi eps',6.001*e0,' eps0',e0,' k^-2/3',k0**(-mpf(2)/3))
mu=1/(0.2*k0**(mpf(2)/3)); print('  (1-mu)^-1/2',(1-mu)**mpf(-0.5),' (1-mu)^-3/2',(1-mu)**mpf(-1.5))
# 295행 R2
p_min=0.2*k0**(mpf(2)/3)-1
print('295행: second term',(1+1/(4*p_min))/(1-mu),' third',-(mpf(7)/2)*k0/(k0+1),' sum',2.5+(1+1/(4*p_min))/(1-mu)-(mpf(7)/2)*k0/(k0+1)-mpf(2)/3)
# 297행 D3
print('297행: cPsi',cPsi,' 1-cPsi/(2sqrt p)',1-cPsi/(2*sqrt(p_min)),' total',6.001*e0/3+1/(3*(1-mu)*(1-cPsi/(2*sqrt(p_min))))-mpf(2)/3)
# 330행
print('330행:',mpf('0.2')-k0**(-mpf(2)/3)-3*c*sqrt(mpf('0.2'))*e0)
# 346행
xi=mpf('0.2'); k=k0
th1=(1.5*sqrt(xi)-0.5/sqrt(xi)*k**(-mpf(2)/3))/(2*c)
th3=0.75*k**(-mpf(1)/3)*(1+(1-1/(xi*k**(mpf(2)/3)))**mpf(-0.5))
ups=(k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**mpf(-1.5)/(xi**2*k**(mpf(2)/3))
print('346행:',th1,th3,ups,th1-th3-ups)
# 356행
print('356행:',(1+xi*e0)/(12*xi**2*k**(mpf(1)/3)), 3/(8*sqrt(xi)*k**(mpf(1)/3)))
# 392행
qmin=0.2*k0**(mpf(2)/3)
print('392행: jinf(0.2)',jinf(mpf('0.2')),' Cr(qmin,6600)',Cr(qmin,k0),' exp',exp(-(jinf(mpf('0.2'))+Cr(qmin,k0))))
E=2*c*xi**mpf(-0.5)*(1+xi*e0); print('394행: E<=',E,' denom',mpf('0.168623')+2*c*xi**mpf(-0.5),' ratio',E/(mpf('0.168623')+2*c*xi**mpf(-0.5)))
# 416-418행
print('418행: first',2*c*sqrt(mpf('0.0005'))*mpf('0.0005'),' Ks',(2/mpf('0.0055'))**mpf(1.5),' s(2)',s(2),' Cr(2,6934.2)',Cr(mpf(2),mpf('6934.2')))
# 420행
print('420행: Cr(2e4,6.6e9)',Cr(mpf(20000),mpf('6.6e9')),' worst: xi just below 2/6600^(2/3), K=6.6e9*1.02 -> q',(2/k0**(mpf(2)/3))*(mpf('6.6e9')*mpf('1.02'))**(mpf(2)/3),' Cr',Cr((2/k0**(mpf(2)/3))*(mpf('6.6e9')*mpf('1.02'))**(mpf(2)/3),mpf('6.6e9')*mpf('1.02')))
# 431행
print('431행: phi>=',exp(-1/(12*qmin)),' rho1<=',1.5*6.001*e0)
xi=mpf('6.001'); q=xi*k0**(mpf(2)/3)
rho2=mpf(5)/8*(1+3/(4*p_min))*(1+xi*e0)**mpf(2.5)*xi**2*k0**(-mpf(2)/3)
print('  rho2<=',rho2,' V>=',exp(-1/(12*qmin))-1.5*6.001*e0-rho2,' th1<=',xi**mpf(1.5)/(2*c),' ups<=',(k0+1)/k0*(1-mu)**mpf(-0.5),' U<=',xi**mpf(1.5)/(2*c)+(k0+1)/k0*(1-mu)**mpf(-0.5),' quot',(exp(-1/(12*qmin))-1.5*6.001*e0-rho2)/(xi**mpf(1.5)/(2*c)+(k0+1)/k0*(1-mu)**mpf(-0.5)))
# 437행
for xi in [mpf('0.1'),mpf('2.1')]:
    br=(mpf('0.4')*xi**mpf(1.5)+mpf('0.5775')*sqrt(xi)*k0**(-mpf(2)/3))*(1+xi*e0)**mpf(1.5)
    print('437행 xi',xi,' bracket',br)
q1=mpf('0.1')*k0**(mpf(2)/3); print('  q at 0.1',q1,' |z-1/2|/q',-zm12/q1,' p^-3/2/(12q)',(q1-1)**mpf(-1.5)/(12*q1))
# 441행
qq=2*k0**(mpf(2)/3); muq=1/qq
print('441행: q>=',qq,' bracket',sqrt(1-muq)-(1+(qq-1)**mpf(-0.5))*e0/sqrt(2),' half',(sqrt(1-muq)-(1+(qq-1)**mpf(-0.5))*e0/sqrt(2))/2)
print('443행:',e0/sqrt(2)/(3*c),' ',0.5*(1+1/(4*(qq-1))))
print('445행: bracket',0.5-1.5*muq-0.75*e0/sqrt(2))
xi=mpf(2); print('  U at xi=2,k=6600',(xi**mpf(1.5)-sqrt(xi)*k0**(-mpf(2)/3))/(2*c)+1-1.5*xi*e0)
print('447행:',mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# 449행
print('449행: e^-jinf(2)',exp(-jinf(mpf(2))),' e^-jinf(2.1)',exp(-jinf(mpf('2.1'))))
# 457행
print('457행: rG',mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2,' 2.75+z12',2.75+z12,' 0.85sqrt2',0.85*sqrt(2),' 0.85 c k/(k+1)',0.85*c*k0/(k0+1))
print('465행:',mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')),' ',mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.000499')))
print('467행:',mpf('7.429e-4')*mpf('0.0004999'))
# 404행
print('404행: (6600/6599)^(2/3)',(k0/(k0-1))**(mpf(2)/3))
# 529행
print('529행: 12927/1e5^(2/3)',12927/mpf(10)**(mpf(10)/3))
# 8.4절용: 추후
# ---- 8.4절 ----
from mpmath import floor, ceil
def qmax(k): return floor(6*k**(mpf(2)/3))
def qfb(k): return floor((3*(k-1)/4-qmax(k)-3)/8)
for k in [6668, 6667]:
    k=mpf(k); print('k',k,' qmax',qmax(k),' qfb',qfb(k),' k-2699-qmax',k-2699-qmax(k),' (3/4)k-2398-qmax',0.75*k-2398-qmax(k),' m_fb',ceil(5*k/4)+qmax(k),' 2k+1-8qfb',2*k+1-8*qfb(k),' (qfb+2)/k',(qfb(k)+2)/k,' 3/32-0.75k^-1/3+0.53/k',mpf(3)/32-0.75*k**(-mpf(1)/3)+0.53/k)
def G(z): return 1.5*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+mpf('0.5')
print('G(0.0537)',G(mpf('0.0537')),' G(0.571)',G(mpf('0.571')),' 3/2-0.307(1-3/(2k)) at 6667',1.5-0.307*(1-1.5/6667),' 47/24+1.1935',mpf(47)/24+mpf('1.1935'),' 3.2/6667',3.2/6667)
# 8.3 (다) 상수와 띠 끝에서의 c0
k=mpf(6668); nu=mpf('0.48')*k; N=k+nu
c0a=(1-1/k)**(N-k+1); c0d=1-exp(mpf(7)/6)*N**mpf(1.5)/(4*c*k*(2*k-1-N))
print('c0 (가)',c0a,' (다)',c0d,' 4c e^-7/6',4*c*exp(-mpf(7)/6))
# (8.11) 괄호가 nu=103에서 양인지
nu=mpf(103); S12=2*sqrt(nu)+z12+1/(2*sqrt(nu))-nu**mpf(-1.5)/24; Sm12=mpf(2)/3*nu**mpf(1.5)+sqrt(nu)/2+zm12+1/(24*sqrt(nu))
print('br(103)',(nu+1)*S12-Sm12-((nu+1)*z32-S12)/12)
