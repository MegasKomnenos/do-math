# -*- coding: utf-8 -*-
"""외부 피드백(2026-11-16) 3.1-3.3의 재현: rig_ray4 의 E1p·E1pp 급수 계수, w=1/1000 에서의 포함 실패, A00 중점에서 hatZ_derivs 의 포함.
사용:  python -I 검토_외부피드백_1116_ZV1_재현.py [모듈파일이름=rig_ray4]      (rig_ray4_v1_bug 를 주면 고치기 전 코드를 검사)
모든 비교는 정확 유리수(Fraction) 또는 mpmath 60자리 참값 대 구간 끝점의 정확 이진값이다."""
import sys, os, importlib
from fractions import Fraction as Fr
HERE = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\critical_window_rerun"
sys.path.insert(0, HERE)
modname = sys.argv[1] if len(sys.argv) > 1 else 'rig_ray4'
import mpmath
from rig_common import iv, I, cI
R4 = importlib.import_module(modname)
from boxes import all_boxes
print('module:', modname, '->', R4.__file__)

def mpf_to_fr(x):
    """mpmath.mpf (point) or zero-width ivmpf -> exact Fraction"""
    if hasattr(x, '_mpi_'):
        a, b = x._mpi_
        assert a == b, 'interval not a point'
        t = a
    else:
        t = mpmath.mpf(x)._mpf_
    sign, man, exp, bc = t
    v = Fr(man) * (Fr(2) ** exp)
    return -v if sign else v

def fact(n):
    r = 1
    for i in range(2, n + 1): r *= i
    return r

# ---------- 3.1 계수: 코드의 계수(루프를 그대로 유리수로 흉내) 대 참 계수
print('\n[3.1] E1p coefficient of w^{m-1}: code vs exact m/(m+1)!')
src = open(R4.__file__, encoding='utf-8').read()
old_pattern = 't = t * w / (m - 1)' in src and 's = s + m * t / iv.factorial(m + 1)' in src
print('  code has the record pattern  t=t*w/(m-1); s+=m*t/(m+1)! :', old_pattern)
for m in range(1, 7):
    exact = Fr(m, fact(m + 1))
    code = Fr(m, fact(m - 1) * fact(m + 1)) if old_pattern else exact
    print(f'  m={m}: code {code}  exact {exact}  {"OK" if code == exact else "DIFF"}')
print('[3.1] E1pp coefficient of w^{m-2}: code vs exact m(m-1)/(m+1)!')
for m in range(2, 7):
    exact = Fr(m * (m - 1), fact(m + 1))
    code = Fr(m * (m - 1), fact(m - 2) * fact(m + 1)) if old_pattern else exact
    print(f'  m={m}: code {code}  exact {exact}  {"OK" if code == exact else "DIFF"}')

# ---------- 3.2 w = 1/1000 : 반환 구간의 정확 이진 상단 대 참값의 유리수 하계(처음 세 항; 모든 항이 양수)
print('\n[3.2] w = 1/1000 (real):')
w = iv.mpf(1) / 1000
e1p = R4.E1p(w); e1pp = R4.E1pp(w)
lb_p = Fr(1, 2) + Fr(1, 3000) + Fr(1, 8 * 10**6)      # = 12008003/24000000
lb_pp = Fr(1, 3) + Fr(1, 4000) + Fr(1, 10 * 10**6)    # = 10007503/30000000
print('  exact lower bounds:', lb_p, '=', float(lb_p), ';', lb_pp, '=', float(lb_pp))
hi_p = mpf_to_fr(e1p.real.b); lo_p = mpf_to_fr(e1p.real.a)
hi_pp = mpf_to_fr(e1pp.real.b); lo_pp = mpf_to_fr(e1pp.real.a)
print(f'  E1p(1/1000)  returned [{float(lo_p):.18f}, {float(hi_p):.18f}]  ->  true lower bound > upper end: {lb_p > hi_p}')
print(f'  E1pp(1/1000) returned [{float(lo_pp):.18f}, {float(hi_pp):.18f}]  ->  true lower bound > upper end: {lb_pp > hi_pp}')
# 60자리 참값(급수 200항); 상자 끝점은 생산 코드와 같이 기본 정밀도(mp.dps=15, 53비트)에서 만든다
BOXES = all_boxes()
mpmath.mp.dps = 60
def E1p_true(wv, N=200):
    return mpmath.fsum(m * wv ** (m - 1) / mpmath.factorial(m + 1) for m in range(1, N))
def E1pp_true(wv, N=200):
    return mpmath.fsum(m * (m - 1) * wv ** (m - 2) / mpmath.factorial(m + 1) for m in range(2, N))
tp = E1p_true(mpmath.mpf(1) / 1000); tpp = E1pp_true(mpmath.mpf(1) / 1000)
print('  60-digit true values:', mpmath.nstr(tp, 20), mpmath.nstr(tpp, 20))
print('  contained (true in returned interval)?  E1p:', lo_p <= mpf_to_fr(tp) <= hi_p, ' E1pp:', lo_pp <= mpf_to_fr(tpp) <= hi_pp)

# ---------- 3.3 A00 중점, sigma' = 1 : hatZ_derivs 대 닫힌식 Z(u) = (exp(1 + i s u - e^{i s u}) - 1)/u^2 의 도함수
print('\n[3.3] A00 midpoint, sigma\' = 1:')
name, ua, ub_ = BOXES[0]
assert name == 'A00'
U = iv.mpf([ua, ub_])
um = (U.a + U.b) / 2
Um = iv.mpf([um, um])
um_fr = mpf_to_fr(um)
print('  u_m =', um_fr, '=', mpmath.nstr(mpmath.mpf(um), 25), '  (feedback: 1645231281648331/36028797018963968 ->', um_fr == Fr(1645231281648331, 36028797018963968), ')')
import json
A00 = json.load(open(os.path.join(HERE, 'cert', 'A00.json'))) if os.path.exists(os.path.join(HERE, 'cert', 'A00.json')) else None
def ex(s):
    neg = s.startswith('-'); s = s.lstrip('-'); man, exp = s.split('*2^'); v = Fr(int(man)) * Fr(2) ** int(exp); return -v if neg else v
if A00:
    print('  cert/A00.json u endpoints equal boxes.py endpoints:', (mpf_to_fr(ua), mpf_to_fr(ub_)) == tuple(ex(t) for t in A00['u_exact']))
print('  u_m is a point interval:', Um.a == Um.b, ' (width', mpmath.nstr(mpmath.mpf(Um.delta.a) if hasattr(Um.delta,'a') else Um.delta, 5), ')')
def Z_true(sig, u):
    g = 1 + 1j * sig * u - mpmath.exp(1j * sig * u)
    gp = 1j * sig * (1 - mpmath.exp(1j * sig * u))
    gpp = sig * sig * mpmath.exp(1j * sig * u)
    eg = mpmath.exp(g)
    Z = (eg - 1) / u ** 2
    Zu = eg * gp / u ** 2 - 2 * (eg - 1) / u ** 3
    Zuu = eg * (gp * gp + gpp) / u ** 2 - 4 * eg * gp / u ** 3 + 6 * (eg - 1) / u ** 4
    return Z, Zu, Zuu
def contains(civ, z):
    return (mpf_to_fr(civ.real.a) <= mpf_to_fr(z.real) <= mpf_to_fr(civ.real.b)) and (mpf_to_fr(civ.imag.a) <= mpf_to_fr(z.imag) <= mpf_to_fr(civ.imag.b))
def gap(civ, z):
    """signed distance of z outside the interval (0 if inside), per part"""
    def g1(a, b, x):
        a, b, x = mpf_to_fr(a), mpf_to_fr(b), mpf_to_fr(x)
        return float(x - b) if x > b else (float(a - x) if x < a else 0.0)
    return g1(civ.real.a, civ.real.b, z.real), g1(civ.imag.a, civ.imag.b, z.imag)
umm = mpmath.mpf(um)
for sig in (1, 2, 3, 6):
    Zt, Zut, Zuut = Z_true(mpmath.mpf(sig), umm)
    # numerical cross-check of the derivatives
    Zn = mpmath.diff(lambda x: Z_true(mpmath.mpf(sig), x)[0], umm)
    Z, Zu, Zuu = R4.hatZ_derivs(iv.mpf(sig), Um)
    print(f"  sigma'={sig}: |Zu analytic - numeric| = {mpmath.nstr(abs(Zut - Zn), 3)}")
    print(f"     Z   contained {contains(Z, Zt)}   gap {gap(Z, Zt)}")
    print(f"     Z_u contained {contains(Zu, Zut)}   gap (re, im) {gap(Zu, Zut)}   width (re) {float(mpmath.mpf(Zu.real.delta.a)):.3e}")
    print(f"     Z_uu contained {contains(Zuu, Zuut)}   gap (re, im) {gap(Zuu, Zuut)}")
    Zb, Zub, Zuub = R4.hatZ_derivs(iv.mpf(sig), U)
    print(f"     whole-box enclosure contains the midpoint truth: Z {contains(Zb, Zt)} Z_u {contains(Zub, Zut)} Z_uu {contains(Zuub, Zuut)}")
# 전 격자: sigma' = i/80 (i = 1..480) 에서 중점 포위의 포함 여부
nfail_u = nfail_uu = 0; worst = (0.0, None)
for i in range(1, 481):
    s = mpmath.mpf(i) / 80
    Zt, Zut, Zuut = Z_true(s, umm)
    Z, Zu, Zuu = R4.hatZ_derivs(iv.mpf(i) / 80, Um)
    assert contains(Z, Zt)
    if not contains(Zu, Zut): nfail_u += 1
    if not contains(Zuu, Zuut): nfail_uu += 1
    g = max(gap(Zu, Zut)); 
    if g > worst[0]: worst = (g, i)
print(f"  grid sigma'=i/80, i=1..480 at u_m: Z_u not contained at {nfail_u}/480 points, Z_uu not contained at {nfail_uu}/480; largest Z_u gap {worst[0]:.3e} at i={worst[1]}")

# ---------- 고친 뒤의 검사: 무작위 복소 w 에서 E1p·E1pp 가 60자리 참값을 담는가
print('\n[check] E1p/E1pp containment at 200 random complex w with |w| <= 0.06 (the production range is |w| <~ 0.04):')
import random
random.seed(20261116)
nf = 0; maxrelw = 0.0
for _ in range(200):
    r = random.random() * 0.06; th = random.random() * 2 * mpmath.pi
    wv = mpmath.mpc(r * mpmath.cos(th), r * mpmath.sin(th))
    wi = iv.mpc(iv.mpf(wv.real), iv.mpf(wv.imag))
    wv_exact = mpmath.mpc(mpmath.mpf(wi.real.a), mpmath.mpf(wi.imag.a))
    tp, tpp = E1p_true(wv_exact), E1pp_true(wv_exact)
    ok = contains(R4.E1p(wi), tp) and contains(R4.E1pp(wi), tpp)
    nf += (not ok)
print('  failures:', nf, '/ 200')
