# -*- coding: utf-8 -*-
"""ZV5 (외부 피드백 1116 묶음 B, 9.2 F6) 검산.
(a) 옛 급수 Q1, Q2 와 참 급수 E1', E1'' 의 계수 차와, |w|<=R 에서의 |E1'-Q1|/|w|^2, |E1''-Q2|/|w|^2 의 상계(피드백의 0.066, 0.053 과 비교).
(b) critical_window_rerun/ 의 새 인증서(F6 뒤)와 v2_E1deriv/cert/ (F6 전)의 셀별 여유(정확 이진값)의 차 — 끝난 상자 전부.
python -I 로 실행. 읽기만 한다(계산 폴더에 쓰지 않는다)."""
import os, json, glob
from fractions import Fraction as Fr
from mpmath import mp, mpf, factorial

ROOT = r"C:\math\임시\주차함수_증명"
RERUN = os.path.join(ROOT, "원고_자료", "세션_재계산", "critical_window_rerun")
OLD = os.path.join(RERUN, "v2_E1deriv", "cert")

mp.dps = 30
print("=== (a) 계수 차 ===")
# 참: E1'(w) = sum_{m>=1} m w^{m-1}/(m+1)!,  옛: m/((m-1)!(m+1)!) ;  E1'' 참: m(m-1) w^{m-2}/(m+1)!, 옛: m(m-1)/((m-2)!(m+1)!)
import math
# 계수(참-옛): E1' 의 w^{m-1}, E1'' 의 w^{m-2}
d1 ={m: Fr(m, math.factorial(m + 1)) - Fr(m, math.factorial(m - 1) * math.factorial(m + 1)) for m in range(1, 21)}
d2 = {m: Fr(m * (m - 1), math.factorial(m + 1)) - Fr(m * (m - 1), math.factorial(m - 2) * math.factorial(m + 1)) for m in range(2, 21)}
for m in range(1, 8):
    print(f"m={m}: E1' 차(w^{m-1}) = {d1[m]} = {float(d1[m]):.6g}", (f"; E1'' 차(w^{m-2}) = {d2[m]} = {float(d2[m]):.6g}" if m >= 2 else ""))
for R in (0.05, 0.1, 0.2):
    s1 = sum(float(abs(d1[m])) * R ** (m - 3) for m in range(3, 21))      # |E1'-Q1| <= |w|^2 * s1  (차는 m>=3 부터; 모든 차가 >= 0)
    s2 = sum(float(abs(d2[m])) * R ** (m - 4) for m in range(4, 21))      # |E1''-Q2| <= |w|^2 * s2
    print(f"|w|<={R}: |E1'-Q1| <= {s1:.5f}|w|^2 (피드백 0.066), |E1''-Q2| <= {s2:.5f}|w|^2 (피드백 0.053)")

print("\n=== (b) 끝난 상자의 셀별 여유: 새(F6 뒤) - 옛(F6 전), 정확 이진값 ===")


def ex(s):
    neg = s.startswith('-'); s = s.lstrip('-'); man, e = s.split('*2^'); v = Fr(int(man)) * Fr(2) ** int(e); return -v if neg else v


news = sorted(glob.glob(os.path.join(RERUN, "cert", "[AG]??.json")))
tot_cells = 0; gmin = None; gmax = None
for p in news:
    b = os.path.basename(p)[:-5]
    new = json.load(open(p)); old = json.load(open(os.path.join(OLD, b + ".json")))
    if 'error' in new:
        print(b, 'error'); continue
    assert 'F6' in new['code'] and 'F6' not in old['code']
    assert len(new['records']) == len(old['records'])
    ds = []
    for rn, ro in zip(new['records'], old['records']):
        assert rn['xa_exact'] == ro['xa_exact'] and rn['xb_exact'] == ro['xb_exact']
        ds.append((ex(rn['margin_exact']) - ex(ro['margin_exact']), rn['k']))
    mn = min(ds); mx = max(ds); tot_cells += len(ds)
    gmin = mn if gmin is None or mn < gmin else gmin; gmax = mx if gmax is None or mx > gmax else gmax
    wn = float(min((ex(r['margin_exact']) for r in new['records']))); wo = float(min((ex(r['margin_exact']) for r in old['records'])))
    nneg = sum(1 for d in ds if d[0] < 0)
    print(f"{b}: 셀 {len(ds)}개; 최소 여유 새 {wn:.9f} 옛 {wo:.9f}; 차 범위 [{float(mn[0]):.3e} (셀 {mn[1]}), {float(mx[0]):.3e} (셀 {mx[1]})]; 음의 차 {nneg}개")
print(f"상자 {len(news)}개, 셀 {tot_cells}개; 전체 차 범위 [{float(gmin[0]):.3e}, {float(gmax[0]):.3e}]")
