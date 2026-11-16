# -*- coding: utf-8 -*-
# 심사 X7 — E6 검산: F4 §6의 닫힌 꼴 DDL_2(k) <= 14(1+log 3k)/(5 sqrt(pi k)) + 42/(5 sqrt(3 pi) k) < 1/4 (k>=6667)
#  (1) 10:old-8-23 1단계의 (d,q) 항 상계에서 F4의 앞인자 21/(5 sqrt(pi) k)와 둘째 캡 1/(3 q sqrt j)가 더 큰지 확인
#  (2) 이중합 S(k) = sum_{j=1}^{k} sum_{q=1}^{k+1-j} min{ q sqrt j / k^2 , 1/(3 q sqrt j) } 를 직접 더해
#      F4의 적분 비교 상계 (1+log 3k) sqrt k /3 + 1/sqrt3 과 비교
#  (3) 네 가족 (나) 여유의 재산출: 새 여유 = 옛 여유 - (1/4 - DDL^natural(k0))  (D:four-families의 구간값으로)
import math, sys
import numpy as np

out = []
# (1) 앞인자와 둘째 캡
qd_max = 1 + 0.7501/2                      # frak q_d <= 1.3751 (d<=k+1)
pref_ms = 3*(2*math.pi)**-0.5*qd_max*math.sqrt(2)   # 3 (2pi)^{-1/2} q_d sqrt(k-1+d) / k^{3/2} <= this / k
pref_F4 = 21/(5*math.sqrt(math.pi))
cap2_ms = 0.16696*qd_max**2
cap2_F4 = 1/3
out.append(f"(1) 앞인자: 원고 {pref_ms:.5f}/k <= F4 {pref_F4:.5f}/k : {pref_ms<=pref_F4};  둘째 캡: 원고 {cap2_ms:.5f} <= F4 {cap2_F4:.5f} : {cap2_ms<=cap2_F4}")

# (2) 이중합 직접 계산
def S_direct(k):
    tot = 0.0
    for j in range(1, k+1):
        q = np.arange(1, k+2-j, dtype=np.float64)
        sj = math.sqrt(j)
        tot += np.minimum(q*sj/k**2, 1.0/(3*q*sj)).sum()
    return tot
def S_F4(k):
    return (1+math.log(3*k))*math.sqrt(k)/3 + 1/math.sqrt(3)
def DDL_F4(k):
    return 14*(1+math.log(3*k))/(5*math.sqrt(math.pi*k)) + 42/(5*math.sqrt(3*math.pi)*k)
for k in (500, 2000, 6667, 6668, 9705, 20000):
    sd = S_direct(k); sf = S_F4(k)
    out.append(f"(2) k={k}: S_direct={sd:.4f}  S_F4={sf:.4f}  ratio={sd/sf:.4f}  OK={sd<=sf};  2*pref_F4*S_direct/k={2*pref_F4*sd/k:.5f}  DDL_F4={DDL_F4(k):.5f}")
# 1/4 문턱과 감소
k0 = 6667
out.append(f"(2') DDL_F4(6667)={DDL_F4(6667):.5f} < 0.25 : {DDL_F4(6667)<0.25};  DDL_F4 감소: " +
           str(all(DDL_F4(k) > DDL_F4(k+1) for k in range(6667, 200000, 7))))
# (3) 가족 여유 재산출 (D:four-families 구간값, D:M-natural-integrals 구간값)
old = {'벌크': (0.5893564, 0.132365937), '2': (0.5045530, 0.122330013), '1b': (0.4673235, 0.114039112), '1a': (0.2047101, 0.113284142)}
F4 = {'벌크': 0.4717223898, '2': 0.3768830931, '1b': 0.3313626540, '1a': 0.06799429334}
for fam, (marg, ddl) in old.items():
    new = marg - (0.25 - ddl)
    out.append(f"(3) 가족 {fam}: 옛 여유 {marg:.7f} - (1/4 - {ddl:.6f}) = {new:.7f};  F4 보고값 {F4[fam]:.7f};  차 {new-F4[fam]:+.2e}")
# (가) 검사의 여유도 같은 양만큼 준다 (1a q0=2: 0.2354722; 1a m0>N (b): 0.394; 1b (b): 0.337)
for name, marg, ddl in (("1a (가)(a) q0=2", 0.2354722, 0.113284142), ("1a (가)(b) m0>N", 0.394, 0.113284142), ("1b (가)(b) m0>N", 0.337, 0.114039112)):
    out.append(f"(3') {name}: {marg:.4f} - (1/4 - DDL) = {marg-(0.25-ddl):.4f}")
with open(sys.argv[1] if len(sys.argv) > 1 else 'scripts/구조압축/심사_X7_E6_DDL_out.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out)+'\n')
print('\n'.join(out))
