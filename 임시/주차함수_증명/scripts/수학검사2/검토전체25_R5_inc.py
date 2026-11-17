# 검토전체25 R5: 6.5절 문장 "두 계수의 차 inc^- - inc^+ 는 ... 각 계수보다 작다"의 범위 확인
import math
def g(x): return (x - 1) * math.log(1 + 1 / x)
bad = 0; worst = (0, None)
for y0 in range(2, 400):
    for d in range(2, y0 + 2):
        for q in range(1, d):
            ip = g(y0 + d) - g(y0 + q)
            im = g(y0 - 1 + d) - g(y0 - 1 + q)
            r = (im - ip) / ip
            if r > worst[0]: worst = (r, (y0, d, q))
            if im - ip >= ip: bad += 1
print('violations of (inc- - inc+) < inc+ :', bad, ' worst ratio', worst)
