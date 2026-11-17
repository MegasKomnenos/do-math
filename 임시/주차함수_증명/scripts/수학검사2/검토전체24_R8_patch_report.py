# R8 (review 24): fix line-number slips in my own report file (exact string replacement, LF kept).
import io, sys
path = sys.argv[1]
s = io.open(path, encoding="utf-8", newline="").read()
reps = [
    (r"진술 23개(보조정리 15, 정리 7, 명제 1)", r"진술 22개(보조정리 15, 정리 6, 명제 1)"),
    (r"(250–252, 302, 372–378)", r"(250–252, 302, 375–378)"),
    (r"「정리 {{2:tree-expansion}}(나)를 $k+1$에서 읽는다」(41행)", r"「정리 {{2:tree-expansion}}(나)를 $k+1$에서 읽는다」(42행)"),
    (r"「그 재귀를 주는 표시 나무 전개」(9행)", r"「그 재귀를 주는 표시 나무 전개」(7행)"),
    (r"2.10절(`장2.md` 868행)", r"2.10절(`장2.md` 866행)"),
    (r"빠듯한 것만 적으면 $(\text{나})$의 둘째 항", r"빠듯한 것만 적으면 정리 {{8:pieces-k-monotone}}(나)의 둘째 항"),
    (r"본문의 $\partial_\xi\mathrm{Flow}^-$ 식(397–399행)", r"본문의 $\partial_\xi\mathrm{Flow}^-$ 식(395–399행)"),
    (r"표본 334점에서 성립하고", r"표본 333점에서 성립하고"),
    (r"진술 23개의 머리를 1.5절의 규칙과", r"진술 22개의 머리를 1.5절의 규칙과"),
    (r"「(8.10)의 $\Lambda$」(271·287행)", r"「(8.10)의 $\Lambda$」(281·289행)"),
    (r"(2.6절)」(453행)", r"(2.6절)」(451행)"),
    (r"2.6절(`장2.md` 374–378행)", r"2.6절(`장2.md` 375–378행)"),
]
for a, b in reps:
    n = s.count(a)
    print(n, a[:40])
    assert n == 1, a
    s = s.replace(a, b)
assert "\r" not in s
io.open(path, "w", encoding="utf-8", newline="").write(s)
