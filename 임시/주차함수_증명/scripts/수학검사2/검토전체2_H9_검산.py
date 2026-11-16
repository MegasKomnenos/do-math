# -*- coding: utf-8 -*-
"""검토전체2 H9: 장9의 라벨 정의 확인과 9.1·9.3·9.4·9.5절 수치 주장의 독립 재계산.
python -I 로 돌린다. 파일은 읽기만 한다."""
import re, glob, os, sys
from mpmath import mp, mpf, sqrt, exp, log, quad, floor, ceil, e as E, pi as PI

mp.dps = 30
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
CH = os.path.join(ROOT, '장v2')

# 1. 라벨 정의 확인 ---------------------------------------------------------
src = open(os.path.join(CH, '장9.md'), encoding='utf-8').read()
used = set(re.findall(r'\{\{([0-9A-Za-z]+):([A-Za-z0-9\-]+)\}\}', src))
defined = set()
for f in glob.glob(os.path.join(CH, '*.md')):
    for ln in open(f, encoding='utf-8'):
        m = re.match(r'\*\*[가-힣 ]+ \{\{([0-9A-Za-z]+):([A-Za-z0-9\-]+)\}\}', ln)
        if m: defined.add((m.group(1), m.group(2)))
        m = re.match(r'### D\.\{\{(D):([A-Za-z0-9\-]+)\}\}', ln)
        if m: defined.add((m.group(1), m.group(2)))
missing = sorted(used - defined)
print('[1] 장9가 참조하는 라벨', len(used), '개; 정의 없는 것:', missing if missing else '없음')

# 2. 6장 상수 ----------------------------------------------------------------
def u(k):  # 6.4절 u(k)
    k = mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def Ups(k):  # hat Upsilon_k
    k = mpf(k); return (k-1)*u(k)/(2*k+1)
def v(k):  # 6.5절 v(k): k>=3999 branch
    k = mpf(k)
    tail = min(1, 3*(k+1)*k**(-mpf(3)/2))
    return 2-2*tail-2*u(k)-mpf('50.62')/sqrt(k-1)
print('[2] u(6668)=', u(6668), ' hatUps(6668)=', Ups(6668), ' v(6668)=', v(6668), ' v(6667)=', v(6667))

# 3. 보조정리 old-7-26 -------------------------------------------------------
def rhoH(k, nu):
    k = mpf(k); nu = mpf(nu); return ((1-3/(2*k))*mpf('0.307')*k/(k+nu-1)-mpf(47)/(24*k))/k
def rhoL(k, nu):
    k = mpf(k); nu = mpf(nu); return mpf(3)/2*nu/(k*(k+nu))*(1-mpf('1.2')/k)
def mu(k):
    k = mpf(k); return Ups(k)/(mpf(3)/2*(1-mpf('1.2')/k)*(v(k)+Ups(k)*(k+1)/k))
k = mpf(6668)
print('[3] (i) k*rhoL(0.112k)=', k*rhoL(k, mpf('0.112')*k), ' k*rhoH(0.112k)>=', k*rhoH(k, mpf('0.112')*k))
m_ = mu(k)
print('    (ii) k mu/(1-mu)=', k*m_/(1-m_), ' 0.1113k=', mpf('0.1113')*k, ' k^{1/3} mu/(1-mu)=', k**(mpf(1)/3)*m_/(1-m_))
rH = rhoH(k, k+1)
print('    (iii) k*rhoH(3k+1)=', k*rH, ' Y_k(3k+1)=', k*rH*v(k)-Ups(k)*(1-(k+1)*rH))
# 단조성 격자
grid = [6668, 7000, 8000, 10000, 20000, 50000, 10**5, 10**6, 10**7, 10**8]
mus = [mu(kk) for kk in grid]
g2 = [(1/mu(kk)-1)/mpf(kk)**(mpf(1)/3) for kk in grid]
g3 = [Ups(kk)*mpf(kk)**(mpf(1)/3) for kk in grid]
g4 = [mpf(kk)*rhoH(kk, kk+1)*v(kk)-Ups(kk)*(1-(kk+1)*rhoH(kk, kk+1)) for kk in grid]
print('    mu 감소?', all(mus[i] > mus[i+1] for i in range(len(grid)-1)),
      ' (1/mu-1)/k^{1/3} 증가?', all(g2[i] < g2[i+1] for i in range(len(grid)-1)),
      ' Ups k^{1/3} 감소?', all(g3[i] > g3[i+1] for i in range(len(grid)-1)),
      ' Y_k(3k+1) 증가?', all(g4[i] < g4[i+1] for i in range(len(grid)-1)))
# 촘촘한 격자에서 (1/mu-1)/k^{1/3} 증가
fine = [6668 + 7*i for i in range(0, 20000)]
vals = [(1/mu(kk)-1)/mpf(kk)**(mpf(1)/3) for kk in fine[::50]]
print('    촘촘한 격자(6668..~146000, 350 간격)에서 (1/mu-1)/k^{1/3} 증가?', all(vals[i] < vals[i+1] for i in range(len(vals)-1)))

# 4. 정리 old-7-28 (2)·(3) ---------------------------------------------------
print('[4] dY/dnu 하계 1.5(1-1.2/k)k v/(1.2366k^2) * k =', mpf(3)/2*(1-mpf('1.2')/k)*v(k)/mpf('1.2366'),
      '; 1/(20(k-1))*k=', k/(20*(k-1)))
for kk in (48965, 48966):
    kk = mpf(kk); print('    k=', int(kk), ' hatUps=', Ups(kk), ' (1/20)(1-1/k)^103=', (1-1/kk)**103/20)

# 5. 정리 old-7-16 -----------------------------------------------------------
def J1(k):
    k = mpf(k); c = 3/sqrt(k); t0 = 1/k + c**(mpf(2)/3)
    f = lambda t: (1+t+2/k)**(-mpf(7)/2)*max(0, 1-c*(t-1/k)**(-mpf(3)/2))
    return mpf(5)/2*quad(f, [t0, (t0+1)/2, 1])
def J2(k):
    k = mpf(k); c = 3*(k-1)*k**(-mpf(3)/2); t0 = 1/k + c**(mpf(2)/3)
    f = lambda t: (1+t+1/k)**(-mpf(7)/2)*max(0, 1-c*(t-1/k)**(-mpf(3)/2))
    return mpf(5)/2*quad(f, [t0, (t0+(k-1)/k)/2, (k-1)/k])
def J3(k): k = mpf(k); return (k/(2*k+1))**(mpf(5)/2)*(1-3/sqrt(k))
def J4(k): k = mpf(k); return (k/(2*k+1))**(mpf(5)/2)*(1-3/sqrt(k-1))
L = J1(6668)+J2(6668)+J3(6668)+J4(6668)
print('[5] L*(6668)=', L, ' (J1,J2,J3,J4)=', J1(6668), J2(6668), J3(6668), J4(6668))
dbar = mpf('6.62')/sqrt(k)
band = (1+dbar/2)/(1-dbar/2)
pi0 = mpf('0.8825')/sqrt(k)+mpf('0.72')/k
cover = mpf('41.2')*(2/(mpf('0.48')*k-102))**(mpf(3)/2)
bulk = 1+(1+1/mpf('1.48'))*dbar/(2-dbar)+(1/mpf('1.48'))*(pi0+cover)
print('    띠 요구값=', band, ' 벌크 요구값=', bulk)
# (2) 상계 함수의 최댓값
best = (0, 0)
for q in range(1, 6668, 1):
    N = 6668+q; num = min(1, 3*k*mpf(q)**(-mpf(3)/2))
    den = k*(mpf('0.734')*(mpf(q+1)**(-mpf(1)/2)-mpf(ceil(mpf(N)/2)+1)**(-mpf(1)/2))+mpf('0.98')/(N+1))
    r = num/den*sqrt(k)
    if r > best[0]: best = (r, q)
print('    (2) 상계 함수 최댓값 *sqrt k =', best[0], ' at q=', best[1], ' (6.62 이하?)', best[0] <= mpf('6.62'))
jstar = int(ceil((3*k)**(mpf(2)/3)))
print('    (2) 첫째 구간 조건 4.85[sqrt k ((3k)^{2/3}+2)^{-1/2} - sqrt2]=', mpf('4.85')*(sqrt(k)*((3*k)**(mpf(2)/3)+2)**(-mpf(1)/2)-sqrt(2)))
print('    (2) 셋째 구간 끝점: iota=0.05k ->', mpf('16.35')*((k+1)/(k-mpf('0.05')*k))**(mpf(3)/2)/(mpf('0.05')*k)*k, '/k ;',
      ' iota=k-j*-1 -> *sqrt k =', mpf('16.35')*((k+1)/(jstar+1))**(mpf(3)/2)/(k-jstar-1)*sqrt(k))

# 6. 정리 H-star-plus t=k+1 ----------------------------------------------------
kk = mpf(3132)
print('[6] k P_{k+1}(k) at k=3132:', -1-(kk-1)/(kk+1)*(kk/(kk+1))**(kk-1), ' (<= -1.22?)')

# 7. 보조정리 old-7-38, psi-low, 7-39 상수 --------------------------------------
print('[7] a 하계 0.48k-1-8k^{2/3} at 6668 =', mpf('0.48')*k-1-8*k**(mpf(2)/3), '; e^{-1/(12*366)}=', exp(-1/mpf(12*366)))
print('    (2pi)^{-1/2} e^{-1/12}=', (2*PI)**(-mpf(1)/2)*exp(-mpf(1)/12), ' (2pi)^{-1/2}(1.46036+2.61238/12)=', (2*PI)**(-mpf(1)/2)*(mpf('1.46036')+mpf('2.61238')/12))
Ren = lambda j: mpf(j)**j*exp(-j)/mp.factorial(j)
bad = []; bad2 = []; P = mpf(0)
for d in range(1, 3000):
    P += Ren(d)
    if P < mpf('0.3989')*(2*sqrt(d)-mpf('1.678')): bad.append(d)
    if not (mpf('0.7978')*sqrt(d)-mpf('0.8848') <= P <= mpf('0.7979')*sqrt(d)): bad2.append(d)
    if d == 1: P1 = P
print('    psi-low 위반 d (1..2999):', bad if bad else '없음', '; Psi(1)=', P1)
print('    psi-two-sided 위반 d (1..2999):', bad2 if bad2 else '없음')

# 8. 9.3 (1) 보조: omega 차분 MVT, 9.1 head-sum-1 6단계 --------------------------
ups0 = mpf(3132)**(-mpf(1)/3); l0 = mpf(3131); opl = 1+1/l0
c1 = (1+ups0*opl)**(mpf(3)/2)*exp(1/(12*l0)); uq = opl**2*(ups0+ups0**3)**2/2
Phi = opl*c1*exp(uq)*(mpf('0.11399')+mpf('0.15958')*ups0**2+mpf('0.85108')*ups0)
c5 = mpf('0.7979')*sqrt(mpf('0.03'))*ups0**3/(mpf('0.7978')*sqrt(mpf('0.03'))-mpf('0.8848')*ups0)
Ebar = c1*opl*((mpf('0.5320')*ups0+c1*(mpf('0.625')+ups0**2))/(mpf('0.7978')-mpf('0.8848')*ups0)+c5)
Lbar = (mpf('0.7978')-mpf('0.8848')*ups0)*exp(-Ebar)/(1+(ups0+ups0**3)*opl)
print('[8] ups0=', ups0, ' c1=', c1, ' uq=', uq, ' Phi=', Phi, ' c5=', c5, ' Ebar=', Ebar, ' Lbar=', Lbar, ' R(1)=', Phi/Lbar)
