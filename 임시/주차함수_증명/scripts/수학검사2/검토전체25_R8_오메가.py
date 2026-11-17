# 검토전체25 R8: 시험 함수 Omega의 본문 수치(Omega(0), max|Omega'|, sup s|Omega''(s)|, 감소)를 본문 정의대로 다시 계산 (배정밀도)
import numpy as np
W = "원고_자료/세션_재계산/r030ffae_window/work/"
wK = np.load(W + "wKrig.npy")
hK = 1e5 ** (-2.0 / 3.0); xK = np.arange(len(wK)) * hK
ramp = lambda s: np.where(s <= -0.1, 0.0, np.where(s < 0.1, (s + 0.1) ** 2 / 0.4, s))
nodes = (1 - np.minimum(1.0, 0.04 + 0.12 * ramp(xK - 1.0))) * wK
print("nodes", len(nodes), "last node x", xK[-1], "누적 최솟값이 바꾸는 항 수", int(np.sum(np.minimum.accumulate(nodes) != nodes)))
sec = np.diff(nodes) / hK
sl = np.empty_like(nodes); sl[1:-1] = 2 * sec[:-1] * sec[1:] / (sec[:-1] + sec[1:])
e0 = 1.5 * sec[0] - 0.5 * sec[1]; e1 = 1.5 * sec[-1] - 0.5 * sec[-2]
sl[0] = min(e0, 0.0); sl[-1] = min(e1, 0.0)
# 조각 [x_i,x_{i+1}]: p(t)=h00 y0+h10 h m0+h01 y1+h11 h m1 ; p''(t)/h^2 = (6(2t-1)(y0-y1) + h((6t-4)m0+(6t-2)m1))/h^2
y0 = nodes[:-1]; y1 = nodes[1:]; m0 = sl[:-1]; m1 = sl[1:]
d2a = (-6 * (y0 - y1) + hK * (-4 * m0 - 2 * m1)) / hK ** 2      # t=0
d2b = (6 * (y0 - y1) + hK * (2 * m0 + 4 * m1)) / hK ** 2        # t=1
sup = max(np.max(xK[1:] * np.maximum(np.abs(d2a), np.abs(d2b))), 0)
print("Omega(0) =", nodes[0], " max|slope at nodes| =", np.max(np.abs(sl)))
# 조각 안 |Omega'|의 최댓값: p'(t)/sec = alpha(1-t)(1-3t)+beta t(3t-2)+6t(1-t)
al = m0 / sec; be = m1 / sec
print("alpha,beta 범위", al.min(), al.max(), be.min(), be.max())
ts = np.linspace(0, 1, 41)[:, None]
dp = (al * (1 - ts) * (1 - 3 * ts) + be * ts * (3 * ts - 2) + 6 * ts * (1 - ts)) * sec
print("max|Omega'| (조각 안 표본) =", np.max(np.abs(dp)), " 감소(모든 표본에서 Omega'<=0):", bool(np.all(dp <= 1e-15)))
print("sup s|Omega''(s)| (조각 끝값, 오른끝 s) ~", sup)
