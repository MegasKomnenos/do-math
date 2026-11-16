# D.window-mass-env 결과 줄의 "∫_0^6 Ω(ς)√(2ς/π) dς ≈ 0.729" 재계산.
import sys, os, json, math, numpy as np
WD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "원고_자료", "세션_재계산", "r030ffae_window")
sys.path.insert(0, os.path.join(WD, "work"))
import cert_lib_fixed as CL
d = json.load(open(os.path.join(WD, "work", "design.json")))
x = np.load(os.path.join(WD, "work", "xKrig.npy")); w = np.load(os.path.join(WD, "work", "wKrig.npy"))
W = CL.make_W_pchip(x, w, d["eta0"], d["eta1"], d["x1"]); Wf = W[0] if isinstance(W, (tuple, list)) else W
xs = np.linspace(0, 6, 6001); vals = np.array([float(Wf(t)) for t in xs])
print("integral of Omega(s) sqrt(2s/pi) over [0,6] (record's make_W_pchip):", np.trapezoid(vals * np.sqrt(2 * xs / math.pi), xs))
# 절점값에 안전 인자(이 글의 식)를 곱한 표로 다시
def e(s): return 0.0 if s <= -0.1 else ((s + 0.1) ** 2 / 0.4 if abs(s) < 0.1 else s)
g = np.array([min(1.0, 0.04 + 0.12 * e(xi - 1)) for xi in x]); om = np.minimum.accumulate(w * (1 - g)); m = x <= 6.0
print("same with knots and this text's safety factor:", np.trapezoid(om[m] * np.sqrt(2 * x[m] / math.pi), x[m]))
