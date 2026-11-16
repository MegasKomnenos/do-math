# 검토전체8 N7a: 보조정리 hermite-nu의 기호 검산
# (가) nm 식, q<2/9 항등식; (나) H_0, H_1, H_2; (다) off 이차식, 1-4q; (라) U_r, V_r (r=2,4); (마) M_2/M_0 일반식과 k 계수 20
import sympy as sp

w, nu, th, d, y, n, N = sp.symbols('w nu theta d y n N')
k = 1 / w

def section(t):
    print("\n==== " + t)

section("(가) q<2/9, nm")
Nk = 3 + (nu + 1 - th) * w            # N/k
# 2N^2 - 9(2k+nu)(k-theta) 를 k^2으로 나눈 것
lhs = sp.expand(2 * Nk**2 - 9 * (2 + nu * w) * (1 - th * w))
rhs = sp.expand((3 * nu + 12 + 6 * th) * w + 2 * (nu + 1 - th)**2 * w**2 + 9 * nu * th * w**2)
print("2N^2-9n y identity:", sp.simplify(lhs - rhs) == 0)
xn = (2 + (nu - 1) * w) * (1 - th * w) / Nk**2
nm = sp.expand(sp.simplify((1 - 4 * xn) * Nk**2))
nm_claim = 1 + (2 * nu + 10 + 2 * th) * w + ((nu + 1)**2 + 2 * (nu - 3) * th + th**2) * w**2
print("nm identity:", sp.simplify(nm - nm_claim) == 0)

section("(나) H_j")
x = w * (1 - th * w) / Nk**2
g = sp.sqrt(nm) / Nk            # sqrt(1-4 x_n)
C1 = (1 - g) / (2 * g**2)
C2 = -(1 - g) * (5 + g) / (4 * g**5)
C3 = 5 * (1 - g) * (6 + g - g**2) / (4 * g**8)
ups = (1 + g) / 2 + x * C1 + x**2 * C2 + x**3 * C3
H = (Nk * ups - 2 - nu * w) / w
ser = sp.series(H, w, 0, 3).removeO()
ser = sp.expand(ser)
for j in range(3):
    print(f"H_{j} =", sp.factor(sp.expand(ser.coeff(w, j))))
print("claim H_1 = -(26+4nu)-8theta; H_2 = 506+97nu+5nu^2+(168+16nu)theta+12theta^2")
print("H_1 ok:", sp.simplify(ser.coeff(w, 1) - (-(26 + 4 * nu) - 8 * th)) == 0)
print("H_2 ok:", sp.simplify(ser.coeff(w, 2) - (506 + 97 * nu + 5 * nu**2 + (168 + 16 * nu) * th + 12 * th**2)) == 0)

section("(다) off, 1-4q")
kk = sp.symbols('k', positive=True)
nn = 2 * kk + nu
NN = 3 * kk + nu + 1
off = sp.symbols('off')
U = nn + off
print("U^2-N U+n k = ", sp.factor(sp.expand(U**2 - NN * U + nn * kk)))
print("claim off^2+(k+nu-1)off-(2k+nu)")
print("W=2U-N:", sp.expand(2 * U - NN))
print("N^2-4nk =", sp.factor(sp.expand(NN**2 - 4 * nn * kk)), " claim (k+nu+3)^2-4(nu+2):", sp.expand((kk + nu + 3)**2 - 4 * (nu + 2) - (NN**2 - 4 * nn * kk)) == 0)
eps = (3 + nu) / kk
val = sp.expand((2 - eps)**2 + (kk + nu - 1) * (2 - eps) - (2 * kk + nu))
print("quadratic at off=2-(3+nu)/k:", sp.simplify(val - (-1 - (nu + 3)**2 / kk + (nu + 3)**2 / kk**2)) == 0)

section("(라) U_r, V_r via Hermite backward recurrence")
# He_{j-1} = (N He_j - He_{j+1})/(y j); express He_{n-i} in He_n, He_{n-1}
Hn, Hn1 = sp.symbols('He_n He_nm1')
def He_list(r):
    # returns dict i -> expr for He_{n-i}, i=0..r+1 in terms of Hn, Hn1
    H = {0: Hn, 1: Hn1}
    for i in range(2, r + 2):
        # He_{n-i} = (N He_{n-i+1} - He_{n-i+2}) / (y (n-i+1))
        H[i] = sp.simplify((N * H[i - 1] - H[i - 2]) / (y * (n - i + 1)))
    return H
def Mr_coeff(r):
    H = He_list(r)
    # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i C(r+1,i)(-1)^i n(n-1)...(n-i+1) He_{n-i}
    s = 0
    for i in range(r + 2):
        ff = 1
        for t in range(i):
            ff *= (n - t)
        s += sp.binomial(r + 1, i) * (-1)**i * ff * H[i]
    return sp.expand(s)
M0 = Mr_coeff(0)
M0d = sp.simplify(M0.subs(Hn, (n + d) * Hn1))
print("M0 ∝", sp.factor(M0d), " (claim He_{n-1} d)")
for r in (2, 4):
    Mr = Mr_coeff(r)
    ratio = sp.simplify(Mr.subs(Hn, (n + d) * Hn1) / M0d)
    ratio = sp.simplify(ratio.subs({N: n + y + 1}))
    # at y=k, n=2k+nu
    rk = sp.simplify(ratio.subs({y: kk, n: 2 * kk + nu}))
    rk = sp.apart(sp.together(rk), d)
    print(f"M_{r}/M_0 (y=k) =", rk)
    # Extract U_r = part independent of d, V_r = - d*(rest)
    Ur = sp.limit(rk, d, sp.oo)
    Vr = sp.simplify(-(rk - Ur) * d)
    print(f"  U_{r} =", sp.expand(Ur.subs(kk, 1 / w)), "\n  V_{r} =", sp.expand(Vr.subs(kk, 1 / w)))
    if r == 2:
        print("  claim U2 = 1+(2nu+2)w+nu(nu+1)w^2 ok:", sp.simplify(Ur.subs(kk, 1 / w) - (1 + (2 * nu + 2) * w + nu * (nu + 1) * w**2)) == 0)
        print("  claim V2 = 4+(4nu+2)w+nu(nu+1)w^2 ok:", sp.simplify(Vr.subs(kk, 1 / w) - (4 + (4 * nu + 2) * w + nu * (nu + 1) * w**2)) == 0)
    if r == 4:
        U4c = 1 + (4 * nu + 16) * w + (6 * nu**2 + 30 * nu + 18) * w**2 + (4 * nu**3 + 17 * nu**2 + 15 * nu + 2) * w**3 + nu * (nu + 1)**3 * w**4
        V4c = 4 + (12 * nu + 38) * w + (13 * nu**2 + 49 * nu + 22) * w**2 + (6 * nu**3 + 21 * nu**2 + 17 * nu + 2) * w**3 + nu * (nu + 1)**3 * w**4
        print("  claim U4 ok:", sp.simplify(Ur.subs(kk, 1 / w) - U4c) == 0)
        print("  claim V4 ok:", sp.simplify(Vr.subs(kk, 1 / w) - V4c) == 0)
    if r == 2:
        # (마) general y: 1-2n/y+n(n+1)/y^2 - n(n+1)/(y^2 d)
        gen = sp.simplify(ratio - (1 - 2 * n / y + n * (n + 1) / y**2 - n * (n + 1) / (y**2 * d)))
        print("  (마) general formula ok:", gen == 0)
    # 4.3절 nu in {-1,0} 값 대조는 생략(장4 수치 미인용)

section("(마) k 계수 20")
yy = kk - th
nn2 = 2 * kk + nu
dy = 4 + (-(26 + 4 * nu) - 8 * th) / kk   # d_y 의 1차 근사(H_0 + H_1/k)
diff = sp.expand(nn2 * (nn2 + 1) - dy * ((nn2 - yy)**2 + nn2))
print("diff =", sp.collect(diff, kk))
print("k^2 coeff:", sp.simplify(diff.coeff(kk, 2)), " k coeff:", sp.simplify(diff.coeff(kk, 1)))

section("hermite-nu (나) 소전개 확인")
print("sqrt(nm) series:", sp.series(sp.sqrt(nm_claim), w, 0, 2))
print("(N/k) ups^o series:", sp.expand(sp.series(Nk * (1 + sp.sqrt(nm_claim) / Nk) / 2, w, 0, 3).removeO()))
print("sqrt(1-4x_n) series:", sp.series(sp.sqrt(nm_claim) / Nk, w, 0, 2))
print("C1 series:", sp.series(C1, w, 0, 2))
print("x series:", sp.series(x, w, 0, 3))
print("(N/k) x C1 series:", sp.series(Nk * x * C1, w, 0, 3))
print("(N/k) x^2 C2 series:", sp.series(Nk * x**2 * C2, w, 0, 3))
