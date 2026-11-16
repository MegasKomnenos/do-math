# 심사 A6 — P5 검산: 갱신 창 꼬리 상계(보조정리 7:transfer-F)의 1/(1-rho/x) 인자.
# 주장: K_j>=0, omega_j = K_j rho^j / K(rho), x>rho  ==>  sum_{j>X} omega_j <= (K(x)/K(rho)) (rho/x)^{X+1}   (분모 없이).
# 확인: 작은 k에서 K_j를 7.3절의 재귀 j K_j = sum_{m=1}^{k-1} (k-m) a°_{m-1} K_{j-m} + [j=k+1] 로 만들고,
#       rho_k(수치 근)와 x = rho_k e^{1/k}에서 세 양(실제 꼬리, 새 상계, 옛 상계)을 비교한다. 옛/새 비 = 1/(1-e^{-1/k}) ∈ (k,k+1).
import math, io
from pathlib import Path
ROOT = Path(r"C:\math\임시\주차함수_증명")
def acirc(m):  # a°_m = (m+1)^{m-1}/m!
    return (m + 1) ** (m - 1) / math.factorial(m)
def a_seq(k, N):
    # (m+1) a_m = sum_{z'=0}^{m} a_{m-z'} n(z'),  n(0)=1, n(z)=min(z,k) a_{z-1}  (7A level-chain 증명의 식)
    a = [1.0]
    for m in range(1, N + 1):
        s = a[m - 1] * 1.0  # z'=0 term: a_{m}... careful: (m+1)a_m = sum_{z'=0}^m a_{m-z'} n(z') includes z'=0 -> a_m*1 ; solve: m a_m = sum_{z'=1}^m a_{m-z'} min(z',k) a_{z'-1}
        s = sum(a[m - z] * min(z, k) * a[z - 1] for z in range(1, m + 1))
        a.append(s / m)
    return a
def rho_k(k, N=400):
    a = a_seq(k, N)
    # C_k(x) = 1 - 1/A(x); find x with A(x)->inf : use ratio a_{N}/a_{N-1} -> 1/rho
    return a[N - 1] / a[N]
def K_coeffs(k, J):
    K = [0.0] * (J + 1)
    for j in range(k + 1, J + 1):
        s = 1.0 if j == k + 1 else 0.0
        for m in range(1, k):
            if j - m >= 0:
                s += (k - m) * acirc(m - 1) * K[j - m]
        K[j] = s / j
    return K
out = []
for k in [3, 4, 6, 8]:
    rho = rho_k(k)
    x = rho * math.exp(1.0 / k)
    J = 60 * k
    K = K_coeffs(k, J)
    Krho = sum(K[j] * rho ** j for j in range(J + 1))
    Kx = sum(K[j] * x ** j for j in range(J + 1))
    for X in [k, 2 * k, 4 * k]:
        tail = sum(K[j] * rho ** j for j in range(X + 1, J + 1)) / Krho
        new = (Kx / Krho) * (rho / x) ** (X + 1)
        old = new / (1 - rho / x)
        out.append(f"k={k} rho={rho:.6f} X={X}: tail={tail:.4e}  new_bound={new:.4e}  old_bound={old:.4e}  tail<=new: {tail <= new}  old/new={old/new:.3f} (1/(1-e^-1/k)={1/(1-math.exp(-1/k)):.3f})")
txt = "\n".join(out)
print(txt)
io.open(ROOT / "scripts" / "구조압축" / "심사_A6_P5_tail_out.txt", "w", encoding="utf-8").write(txt + "\n")
