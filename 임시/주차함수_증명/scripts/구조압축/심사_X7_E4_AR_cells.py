# -*- coding: utf-8 -*-
# 심사 X7 — E4 검산: 해석적 행 정리(9:old-7-16) (1)단계의 착지 비 하계를 적분(D:AR-integrals) 대신
# 몇 개의 셀로 나눈 Abel 합으로 세울 수 있는지. 셀 하계:
#   sum_{E=Y+1}^{2k} omega(E+1)[s_{E-1}(Y)-s_E(Y)] >= omega_1 - omega_r s̄_r - sum_{i<r} (omega_i-omega_{i+1}) s̄_i,
#   omega_i = omega(E_i+1) = (k/(E_i+1))^{5/2}, E_0=Y, s_{E_0}(Y)=1, s̄_i는 s_{E_i}(Y)의 상계.
# 생존 상계 두 가지: (A) 6:old-7-13  s_{y+q}(y) <= min(1, 3 y q^{-3/2}) (y>=4000)
#                    (B) 10:old-8-25  s_{y+d-1}(y) <= min(1, 1.15 (y+d)/d^{3/2}) (y>=6666, d<=y+2)
import math, sys

def s_upper_A(y, q):   # s_{y+q}(y)
    return 1.0 if q <= 0 else min(1.0, 3*y*q**-1.5)
def s_upper_B(y, q):   # s_{y+q}(y) = frak s_{q+1}(y)
    d = q+1
    if d > y+2: d = y+2   # (SM): s_{y+q} <= s_{y+(y+1)} for larger q
    return min(1.0, 1.15*(y+d)/d**1.5)

def cell_bound(k, Y, cuts, s_upper):
    # cuts: list of q (offsets E=Y+q... careful: E ranges over sizes, offsets relative to Y)
    E = [Y] + [Y+q for q in cuts] + [2*k]
    om = [(k/(e+1))**2.5 for e in E[1:]]             # omega_i, i=1..r
    sbar = [s_upper(Y, e-Y) for e in E[1:]]           # s̄_i
    r = len(om)
    val = om[0] - om[-1]*sbar[-1] - sum((om[i]-om[i+1])*sbar[i] for i in range(r-1))
    return val

def total(k, cuts_scale, s_upper):
    c = k**(2/3)
    cuts = [int(a*c) for a in cuts_scale]
    vk  = cell_bound(k, k,   cuts, s_upper)
    vk1 = cell_bound(k, k-1, [q+1 for q in cuts], s_upper)   # same sizes E, offsets shift by one
    return vk, vk1, vk+vk1

out = []
for k in (6668, 10000, 20000, 100000, 1000000):
    for name, cuts in (("3셀 [2.08,4,6]", [2.0801, 4, 6]), ("4셀 [2,4,6]+끝", [2, 4, 6]), ("6셀 [1.5,2,3,4,6]", [1.5, 2, 3, 4, 6]), ("8셀", [1.3, 1.6, 2, 2.5, 3, 4, 6])):
        a = total(k, cuts, s_upper_A); b = total(k, cuts, s_upper_B)
        out.append(f"k={k:>7} {name:>18}: (A 6:old-7-13) land>= {a[2]:.4f} [{a[0]:.4f}+{a[1]:.4f}] ; (B 10:old-8-25) land>= {b[2]:.4f} [{b[0]:.4f}+{b[1]:.4f}]")
out.append("요구값: 띠 1.0845, 벌크 1.0787 (k=6668); 원고의 적분값 L_*(6668)=1.206")
# 많은 셀로 극한 확인(적분 1.206에 수렴하는지): (A)로 200셀
k = 6668
fine = [1.0 + 0.05*i for i in range(0, 101)]  # 1.0 .. 6.0 step 0.05 (in k^{2/3} units) ; 아래 2.08 전에는 (A)가 1이라 무의미
a = total(k, fine, s_upper_A); b = total(k, fine, s_upper_B)
out.append(f"k=6668 101셀(1.0..6.0): (A) {a[2]:.4f}  (B) {b[2]:.4f}")
with open(sys.argv[1] if len(sys.argv) > 1 else 'scripts/구조압축/심사_X7_E4_AR_cells_out.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out)+'\n')
print('\n'.join(out))
