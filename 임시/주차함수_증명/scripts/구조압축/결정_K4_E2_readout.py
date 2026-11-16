# -*- coding: utf-8 -*-
"""결정 K4 검산 4: E2 — D:band-boxes 의 저장된 상자별 하계(이 글의 구간 재계산, 점별 충실판 FH; band_iv.py 가 저장한
box_FH_*.npy 의 (k_-, k_+, nu_-, nu_+, 하계))를 읽어, 띠 앞부분 103<=nu<=3.6k^{2/3} 과 만나는 모든 상자에서의 최솟값을 읽는다.
상자의 값은 그 상자 안 모든 정수점에서 (8.30)의 LB^low 의 하계이므로, 앞 띠와 만나는 상자들의 최솟값은 앞 띠 전체에서
LB^low 의 인증된 하계다. 새 계산이 아니라 저장값의 판독이다(읽기만; 자료 폴더에 쓰지 않는다).
또 k>=k_last 의 꼬리(nu/k 상자)는 tail_H_*.txt 에서 첫 상자(nu/k<1/200; 3.6k^{-1/3}<1/200 이 k>=k_last 에서 성립)의 값을 읽는다.
"""
import os, re
import numpy as np

D = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\band_boxes"
rows = []
for p in ("p0", "p1"):
    a = np.load(os.path.join(D, "box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_%s.npy" % p), allow_pickle=False)
    rows.append(a)
A = np.concatenate(rows)
ka, kb, nua, nub, val = A.T
print("상자 수:", len(A), "; 전체 최솟값(=D:band-boxes 결과 1.0097628...):", val.min(), "at", A[val.argmin()][:4])

def front_mask(c):
    # 앞 띠 nu <= c k^{2/3} 과 만나는 상자: nu_- <= c * k_+^{2/3}
    return nua <= np.floor(c * kb ** (2.0 / 3.0))

for c in (3.6, 4.0, 4.5):
    m = front_mask(c)
    i = np.argmin(np.where(m, val, np.inf))
    print("nu <= %.1f k^{2/3} 과 만나는 상자 %d개: 최솟값 %.6f at (k in [%d,%d], nu in [%d,%d]); 1.05 이상: %s" % (
        c, m.sum(), val[i], ka[i], kb[i], nua[i], nub[i], bool(val[m].min() >= 1.05)))
# 앞 띠 상자 가운데 k 가 가장 작은 띠(첫 k-상자)의 값 분포
m = front_mask(3.6) & (ka == 6668)
print("첫 k-상자 [6668,6935]의 앞 띠 상자 %d개: 최솟값 %.6f, 최댓값 %.6f" % (m.sum(), val[m].min(), val[m].max()))
# 1.05 를 넘는 최대 nu 범위: 모든 상자 가운데 값 >= 1.05 인 상자들로 덮이는 nu/k^{2/3} 의 한계(참고)
bad = val < 1.05
if bad.any():
    r = nua[bad] / kb[bad] ** (2.0 / 3.0)
    print("값 < 1.05 인 상자의 nu_-/k_+^{2/3} 최솟값(참고; 1.05 가 보장되는 창 좌표 상한): %.3f  (nu_-/k_- 최솟값 %.4f)" % (r.min(), (nua[bad] / ka[bad]).min()))
# 꼬리
t = open(os.path.join(D, "tail_H_T12-25_k6668.txt"), encoding="utf-8").read().splitlines()
print("꼬리 파일 처음 6줄:")
print("\n".join(t[:6]))
print("꼬리 파일 마지막 2줄:")
print("\n".join(t[-2:]))
