# R2 검산(수치): 보조정리 4:borel-tail-arc 셋째 조각의 전변동 주장
#   TV_{[0,1]} of G(w)=w^{-3/2}(e^{-phi w}-1+phi w) = phi^2 w^{1/2} h(phi w)  <=  |phi|^2 e^{-Re phi}
#   (Re phi<=0, |phi|<=2(-Re phi)).  h(u)=(e^{-u}-1+u)/u^2 는 작은 |u| 에서 급수로 계산(상쇄 회피).
#   (첫 판은 w->0 에서 e^{-phi w}-1+phi w 를 직접 빼서 자리 상쇄로 무의미한 값이 나왔다 — 이 판이 고친 것.)
import mpmath as mp, random
mp.mp.dps = 20
random.seed(11)
def h(u):
    if abs(u) < 0.5:
        return mp.fsum((-u)**m/mp.factorial(m+2) for m in range(30))
    return (mp.e**(-u) - 1 + u)/u**2
def hp(u):
    if abs(u) < 0.5:
        return mp.fsum(-m*(-u)**(m-1)/mp.factorial(m+2) for m in range(1, 30))
    return (2 - u - (u+2)*mp.e**(-u))/u**3
def TV(phi):
    # |G'| = |phi|^2 | (1/2) w^{-1/2} h + w^{1/2} phi h' | ; w=s^2 로 치환해 끝점 특이성 제거
    f = lambda s: abs(0.5*h(phi*s*s) + s*s*phi*hp(phi*s*s))*2
    return abs(phi)**2*mp.quad(f, mp.linspace(0, 1, 9))
worst = 0; wp = None
pts = [mp.mpc(-1e-4, 0), mp.mpc(-1e-4, 1.7e-4), mp.mpc(-40, 69), mp.mpc(-3, 5.19), mp.mpc(-1, 1.73), mp.mpc(-10, 0), mp.mpc(-1, 0), mp.mpc(-0.3, 0.5)]
for t in range(120):
    a = 10**random.uniform(-3, 1.6)
    pts.append(mp.mpc(-a, random.uniform(-1, 1)*a*mp.sqrt(3)))
for phi in pts:
    r = TV(phi)/(abs(phi)**2*mp.e**(-phi.real))
    if r > worst: worst = r; wp = phi
print("max TV/(|phi|^2 e^{-Re phi}) =", mp.nstr(worst, 6), "at", mp.nstr(wp, 6))
