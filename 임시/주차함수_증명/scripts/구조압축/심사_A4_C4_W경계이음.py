# 심사 A4 — 「W 경계 이음」 변형: t0^W(y) = 1 + min{m>=y+1 : m-y >= 𝔪(m)+1}  (IH(n,y)가 글자 그대로 W(m)이 되는 가장 좁은 이음)
#  폭 wid^W = t0^W-1-y 를 y^{2/3}+2 및 F4 폭과 비교하고, 𝔪(m) < m^{2/3} - 4.5 m^{1/3} (m>=20001) 를 정수로 확인한다.
def frak_m(m):
    mp = int(m**(2/3))+2
    while not (mp**3 <= (m-9*mp)**2 and m-9*mp > 0): mp -= 1
    while (mp+1)**3 <= (m-9*(mp+1))**2 and m-9*(mp+1) > 0: mp += 1
    return mp if mp >= 171 else 170
def t0W_minus1(y):
    m = y+1
    while not (m - y >= frak_m(m)+1): m += 1
    return m
viol=0; worst=(0,None); viol2=0
for y in list(range(25000, 40001, 7)) + [60000, 10**5, 10**6, 10**7]:
    w = t0W_minus1(y)-1-y
    if w > y**(2/3)+2: viol += 1
    rat = (w-2)/y**(2/3)
    if rat > worst[0]: worst = (rat, y)
    if w > 1.03*y**(2/3)+1: viol2 += 1
print(f"wid^W <= y^(2/3)+2 위반: {viol};  (wid^W-2)/y^(2/3) 최댓값 {worst[0]:.4f} at y={worst[1]};  F4 폭 상계 초과: {viol2}")
print(f"y=25000: wid^W={t0W_minus1(25000)-1-25000}, 현행 651, F4 874;  y=10^6: wid^W={t0W_minus1(10**6)-1-10**6}, y^(2/3)={10**6**(2/3) if False else (10**6)**(2/3):.0f}")
# 𝔪(m) < m^{2/3} - 4.5 m^{1/3}  ⇔ (𝔪 + 4.5 m^{1/3})^3 < m^2 ... 실수 비교로 확인(여유가 커서 배정밀도로 충분)
bad = sum(1 for m in range(20001, 200001) if not (frak_m(m) < m**(2/3) - 4.5*m**(1/3)))
print(f"𝔪(m) < m^(2/3)-4.5m^(1/3) 위반 (m=20001..200000): {bad};  m=20001: 𝔪={frak_m(20001)}, m^(2/3)-4.5m^(1/3)={20001**(2/3)-4.5*20001**(1/3):.1f}")
