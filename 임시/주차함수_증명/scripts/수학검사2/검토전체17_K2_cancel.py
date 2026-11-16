# K2 검산 4: 중앙 상쇄 항등식 int F_0 = 0, int F_1 = 46 sqrt2 - 12, J 선도 적분 3 sqrt(2 pi) (수치 구적)
# Dawson 함수는 erfi로 적는다: D(b) = e^{-b^2/2} int_0^b e^{v^2/2} dv = e^{-b^2/2} sqrt(pi/2) erfi(b/sqrt2)
import mpmath as mp
mp.mp.dps = 15
ninf = 2 / mp.sqrt(mp.pi)
def Daw(b):
    return mp.exp(-b ** 2 / 2) * mp.sqrt(mp.pi / 2) * mp.erfi(b / mp.sqrt(2))
def F0(z):
    def inner(r):
        mu = 1 - r ** 2
        Pq = mu * z ** 2 + mu ** 2 * z ** 4 / 4
        b = r * z
        return r ** 2 * Pq * (2 - 2 * b * Daw(b))   # e^{mu z^2/2} e^{b^2/2} = e^{z^2/2}
    return -ninf * z ** 4 * mp.exp(-z ** 2 / 2) * (2 * mp.pi) ** -0.5 * mp.quad(inner, [0, 1])
def F1(z):
    def inner(r):
        mu = 1 - r ** 2
        Pq = mu * z ** 2 + mu ** 2 * z ** 4 / 4
        return r ** 2 * mp.exp(mu * z ** 2 / 2) * Pq * (mp.mpf(4) / 3 * r ** 2 * z ** 2 - mp.mpf(2) / 3 * r * z ** 4)
    return -ninf * z ** 4 * mp.exp(-z ** 2) * mp.quad(inner, [0, 1])
I0 = 2 * mp.quad(F0, [0, 2, 4, 7, 10])     # 짝함수
I1 = 2 * mp.quad(F1, [0, 2, 4, 7, 10])
IJ = 2 * mp.quad(lambda z: z ** 3 * mp.exp(-z ** 2 / 2) * (mp.mpf(4) / 15 * z ** 3 - z / 3), [0, 3, 6, 10])
out = ["int F0 = %s (expected 0)" % mp.nstr(I0, 8), "int F1 = %s ; 46sqrt2-12 = %s" % (mp.nstr(I1, 10), mp.nstr(46 * mp.sqrt(2) - 12, 10)), "J leading = %s ; 3sqrt(2pi) = %s" % (mp.nstr(IJ, 10), mp.nstr(3 * mp.sqrt(2 * mp.pi), 10))]
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체17_K2_cancel_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
