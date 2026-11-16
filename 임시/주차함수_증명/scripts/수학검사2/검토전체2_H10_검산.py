# 검토전체2 H10: 장10.md의 몇몇 손 계산 상수와 표 값을 독립으로 다시 계산한다(mpmath 배정밀도 이상; 보고용 검산).
from mpmath import mp, mpf, quad, sqrt, log, exp, pi, e, floor, ceil
mp.dps = 30
out=[]
def rep(n,v,c): out.append(f"{n}: 계산 {v} / 본문 {c}")
# 10.3 표와 가족 첫 열
for k,lab in [(8064,'k<8065 벌크뿐'),(8065,'띠 시작'),(9948,'nu_min=105'),(9949,'nu_min=103'),(9705,'1a'),(9704,'1a 전'),(9551,'1b'),(9550,'1b 전')]:
    rep(f"k={k} 20001-2k, 0.48k, 1.3k^(2/3), 2k^(2/3)", (20001-2*k, mpf('0.48')*k, mpf('1.3')*mpf(k)**(mpf(2)/3), 2*mpf(k)**(mpf(2)/3)), lab)
# 명제 10:old-8-23: j1, j2, DDL^natural
q = lambda r: 1+mpf('0.7501')*r/(1+r)
f2 = lambda r: sqrt((1+r)/r)*mpf('0.70836')*q(r)**3
f1 = lambda r: f2(r)*(mpf('2.528571')-log(q(r))+mpf('1.5')*log(r))
j2 = quad(f2,[0,mpf('1e-6'),mpf('0.01'),1]); j1 = quad(f1,[0,mpf('1e-6'),mpf('0.01'),1])
rep("j2", j2, "2.7171998..."); rep("j1", j1, "0.7998716...")
def DDLn(k):
    k=mpf(k); d=2*k**(mpf(2)/3)
    eps=-log(1-sqrt(k+1)/(mpf('0.485917')*k)); epsp=mpf('2.26')/k+mpf('0.47')/(d-1)
    gam=mpf('2.6047')*(mpf('2.53')+log(k)/2+eps+mpf('1.5')/k)/k
    return mpf('0.457143')/sqrt(2*pi)*q(d/k)*sqrt(1+d/k)*(d+1)**mpf('3.5')/k**3 + 2/sqrt(2*pi)/sqrt(k)*(1+epsp)*(j1+(log(k)/2+eps)*j2+gam) + mpf('3.9')/sqrt(2*pi)/k
for k in (6668,8065,9551,9705): rep(f"DDL^natural({k})", DDLn(k), "0.1324/0.1223/0.1140/0.1133")
rep("j1+j2(log(6667)/2-1)", j1+j2*(log(6667)/2-1), "10.04")
# 5단계 부호 보조정리 상수
rho0=floor(2*mpf(6667)**(mpf(2)/3))/6667; rep("rho0(6667)", rho0, "<=0.10635")
iota0 = mpf('2.528571')-log(q(rho0))+log(floor(2*mpf(6667)**(mpf(2)/3))**mpf('1.5')/6667); rep("iota0", iota0, ">=3.4964 (본문 3.4964)")
s0=exp(-mpf('3.4964')/mpf('1.5')); rep("sigma0", s0, "0.0972")
rr=rho0*s0; rep("d^nat q^3 at rho0*sigma0 * sqrt(rho)", sqrt(1+rr)*q(rr)**3, "<=1.0288")
rep("sign integral bracket", (2*mpf('3.4964')-6+6*sqrt(s0))-mpf('1.0288')*6*sqrt(s0), "0.938")
# 1단계: k_d(q) 둘째 항 상수 2.2503 vs (9/4)(1+e^{3/(2k)})/2
rep("(9/4)(1+e^{3/(2*6667)})/2", mpf(9)/4*(1+exp(mpf(3)/(2*6667)))/2, "<=3*0.7501=2.2503")
# 10:old-8-35 벌크 상수
rep("(2pi)^-1/2 e^-1 2^1.5", 2**mpf('1.5')/sqrt(2*pi)/e, ">=0.41508 (감쇠 인자 전)")
rep("1/0.41508", 1/mpf('0.41508'), "2.40918")
k=mpf(6668); m=ceil(sqrt(5*k*log(k))); xi=(sqrt(5*k*log(k))+2)/k
ebar=exp(mpf(3)/(2*k))*(exp(sqrt(5*log(k)/k)+1/k)+mpf('2.40918')*k**(mpf('1.5')-mpf('2.5')/(1+xi)))
rep("ebar(6668)", ebar, "1.0870"); rep("m_hit/k (6667)", ceil(sqrt(5*6667*log(6667)))/mpf(6667), "<=0.09")
# 10:bulk-majorants
u=lambda k: mpf(3)/mpf('0.35')*(mpf('1.35')+1/mpf(k))*(mpf('0.65')-1/mpf(k))**mpf('-1.5')/sqrt(mpf(k))
k=mpf(6668)
rep("abar(6668)", 3*mpf('1.15')*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**mpf('1.5'), "0.1880")
rep("bbar(6668)", 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**mpf('-1.5'), "1.1190")
rep("dbar(6668)", mpf('72.217')/sqrt(k), "0.8844")
r=mpf('0.48'); rep("bracket at 0.48", r**mpf('-0.5')-1+(1-sqrt(r))/3, "0.54577"); rep("132.32*0.54577", mpf('132.32')*mpf('0.54577'), "72.217")
# 10:check-na 가족 2 o_F 조각
k=mpf(8065); d=2*k**(mpf(2)/3)+1
rep("3 s^up_{2k^(2/3)+1}(k+1), k=8065", 3*mpf('1.15')*(k+1+d)/d**mpf('1.5'), "1.3392")
rep("theta0", (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')), "0.1470")
BdT=lambda k,nu: (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**mpf('-1.5')
rep("Bd^T(8065,0.48k)", BdT(k,mpf('0.48')*k), "0.7615")
k=mpf(9551); xs=2*k**(mpf(2)/3)/(k-1); d=mpf('1.3')*k**(mpf(2)/3)+1
rep("1b: 3s^up", 3*mpf('1.15')*(k+1+d)/d**mpf('1.5'), "2.4644"); rep("1b: theta part", (2*exp(-xs)-1)*exp(-xs), "0.7463"); rep("1b: Bd^T(k,2k^(2/3))", BdT(k,2*k**(mpf(2)/3)), "0.5254")
k=mpf(9705); nu=mpf('1.3')*k**(mpf(2)/3)
rep("1a: e^c", 3*nu**2/((k-1)*k)+mpf('4.8')*sqrt(nu)/k+nu**2/(2*(k-1)**2), "0.0250"); rep("1a: Bd^T", BdT(k,nu), "0.5062")
# 10:old-8-32(iii) 상수
cR=sqrt(2*pi)/2*exp(mpf(1)/12); rep("c_R", cR, "1.3622")
ge=lambda t: exp(-t)*(1+mpf('1.5')*t)
rep("beta0 min", cR*mpf('1.04')**mpf('1.5')/sqrt(2), "1.0216"); rep("g^e(1.0216)", ge(mpf('1.0216')), "0.912")
rep("iota q0 max", cR*2**(mpf(2)/3)*mpf(6669)**(-mpf(1)/3), "<=0.115")
rep("|g^e'| at 1.02, 2.73", (abs(exp(-mpf('1.02'))*(mpf('0.5')-mpf('1.53'))), abs(exp(-mpf('2.73'))*(mpf('0.5')-mpf('4.095')))), ">=0.234")
# 10:old-8-34
rep("0.7999 check: 2(2pi)^-1/2 (1-1/206)^-1/2", 2/sqrt(2*pi)*(1-mpf(1)/206)**mpf('-0.5'), "<=0.7999")
# 10:old-8-25 7단계
E=lambda up,q: 2/sqrt(2*pi)*(mpf('0.25')*(1-1/(2*mpf(q)))**mpf('-1.5')+(1+up+up*up)*(1-up)**mpf('-0.5')*(1+up)**mpf('-1.5'))
rep("E coef up=.9", E(mpf('0.9'),113), "<=2.82"); rep("E coef up=.99", E(mpf('0.99'),113), "<=9.3"); rep("E coef up=.9999", E(mpf('0.9999'),113), "<=85")
rep("(1.15*6666)^(2/3)", (mpf('1.15')*6666)**(mpf(2)/3), "<389"); rep("(1200)^(2/3)", mpf(1200)**(mpf(2)/3), "<113")
# 10:old-8-33(ii)
cAb=lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
rep("2cAb(0.6)-4/sqrt(0.6)", 2*cAb(mpf('0.6'))-4/sqrt(mpf('0.6')), "10.836")
rep("Sub max", quad(lambda r:(1+r)/sqrt(r)/(1-r)**2,[0,mpf('0.6')]), "3.873")
print("\n".join(out))
