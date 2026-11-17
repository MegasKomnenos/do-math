# R12 검산: D.band-boxes의 격자 (k-상자 수, 마지막 격자점, 유한 상자 수, 꼬리 상자 수)를
# 「알고리즘」 줄의 규칙만으로 다시 센다 (정수 산술).
import math

k = 6668
ks = [k]
while ks[-1] < 10 ** 12:
    # ceil(1.04 k) 를 정수로: ceil(26 k / 25)
    ks.append(-(-26 * ks[-1] // 25))
print("k grid points", len(ks), "k boxes", len(ks) - 1, "last", ks[-1])
total = 0
for a, b in zip(ks[:-1], ks[1:]):
    kp = b - 1  # 상자 [k_-, k_+] = [a, b-1]
    top = 48 * kp // 100  # floor(0.48 k_+)
    v = 103
    n = 0
    while v <= top:
        vp = max(v + 3, 103 * v // 100)  # max(nu_- + 3, floor(1.03 nu_-))
        n += 1
        v = vp + 1
    total += n
print("finite boxes (k box = [k_i, k_{i+1}-1])", total)
total2 = 0
for a, b in zip(ks[:-1], ks[1:]):
    top = 48 * b // 100
    v = 103
    n = 0
    while v <= top:
        vp = max(v + 3, 103 * v // 100)
        n += 1
        v = vp + 1
    total2 += n
print("finite boxes (k box = [k_i, k_{i+1}])", total2)
print("first k box", ks[0], ks[1], " tail boxes", 48 * 200 // 100)
