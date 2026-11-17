# -*- coding: utf-8 -*-
# 장7A의 수치: 지표 t_k, 반감 경계 n^sharp_k, 열 인증 (가)의 정수 부등식과 도함수 하계 (검토 25차 R6).
import sys, io
from fractions import Fraction as Fr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def tk(k):
    j = 0
    while (k+1)**j * k**(j+1) + (k-1)**(2*j+1) < 2*k**(2*j+1): j += 1
    return j
mx = 0; last_le_20000 = None
for k in range(2, 501):
    t = tk(k); assert 1 <= t <= k
    ns = k + (k+1)*t
    assert ns <= k*k+2*k
    if k <= 140: mx = max(mx, ns)
    if ns <= 20000: last_le_20000 = k
    if k in (2, 3, 10, 41, 120, 121, 140, 141, 200, 222, 223, 224, 225, 500): print('k=%d t_k=%d n^sharp_k=%d  k^2+2k=%d' % (k, t, ns, k*k+2*k))
print('max_{k<=140} n^sharp_k =', mx, ' ; 140^2+280 =', 140*140+280)
print('n^sharp_k<=20000 인 마지막 k(연속 여부는 따로):', last_le_20000)
L = 10**21 * 400**10; R = 17**21 * 123**10
print('10^21*400^10 =', L); print('17^21*123^10 =', R); print(L > R, float(L), float(R))
print('17^4 =', 17**4, ' 123^2 =', 123**2, ' 8.36^5 =', 8.36**5, ' 1.513^5 =', 1.513**5, ' 17*40836 =', 17*40836, ' 6.95*7.93 =', 6.95*7.93)
print('1-(21/10)(10/17)^3 =', float(1-Fr(21, 10)*Fr(10, 17)**3))
print('2(k+1)/(k-1) at 41 =', Fr(2*42, 40))
