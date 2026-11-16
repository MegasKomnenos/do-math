# -*- coding: utf-8 -*-
"""5B 수학검사2 수정 스크립트(멱등). 앵커가 파일 안에서 정확히 한 번일 때만 치환한다."""
import io, sys
EDITS = [
    ("장v2/장5B.md",
     r"$(1+\varrho_0/y)^{3/2}\le1.0375$, $e^{1/(12y)}\le e^{1/400008}$",
     r"$(1+\varrho_0/y)^{3/2}\le1.0376$, $e^{1/(12y)}\le e^{1/400008}$"),
    ("장v2/장5B.md",
     r"\cdot0.7171\cdot1.5\cdot1.0871\cdot1.0375\cdot e^{0.1305+1/400008}\le0.3677$",
     r"\cdot0.7171\cdot1.5\cdot1.0871\cdot1.0376\cdot e^{0.1305+1/400008}\le0.3677$"),
    ("장v2/장5B.md",
     r"\le\frac{2/12}{1-1/32}\le0.172$이므로",
     r"\le\frac{2/12}{1-1/32}\le0.173$이므로"),
    ("장v2/장5B.md",
     r"$\mathcal Y_j=4\sum_m\gamma_m(\eta)\mathfrak j_m(\eta)$가 된다",
     r"$\mathcal Y_j=4\sum_m\gamma_m(\eta)\mathfrak j_{m+1}(\eta)$가 된다"),
    ("장v2/부록D_장5B.md",
     r"실패 $0$, 최솟값 $0.00283$.",
     r"실패 $0$, 최솟값 $0.00282$."),
    ("장v2/부록D_장5B.md",
     r"사다리꼴 보정 없이 위 식 항목에서 정의한 부분합에 두 적분 경계",
     r"사다리꼴 보정 없이 부분합 $\sum_{j\le N}j^{-3/2}$에 두 적분 경계"),
]
n_done = 0
for path, old, new in EDITS:
    s = io.open(path, encoding="utf-8").read()
    c_old, c_new = s.count(old), s.count(new)
    if c_old == 0 and c_new == 1:
        print(f"[skip] already applied: {path}: {new[:50]}"); continue
    if c_old != 1:
        print(f"[ERROR] anchor count {c_old} != 1 in {path}: {old[:60]}"); sys.exit(1)
    s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    n_done += 1
    print(f"[ok] {path}: {old[:60]} -> {new[:60]}")
print("치환", n_done)
