# -*- coding: utf-8 -*-
"""보충 수리 E7의 세션 몫 반영: 장부 393·395·1204행, 구조표 85행, README 575행, 부록D_장7A D.self-consistent-constants 「확인하는 진술」(2). 2026-11-16."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"{rel}: {n}건 — {a[:80]}")
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel, len(pairs))


sub(r"장부_v2.md", [
    (r"7.3 진술 $\psi_V$와 7장 안에서 겹쳐", r"7.3 진술 $\psi_G$(2차 $\psi_V$)와 7장 안에서 겹쳐"),
    (r"$\mathfrak P^{\mathrm V}_k=\Gamma\mathfrak P^{\mathrm U}_k(1+2\times10^{-5})$(1차 $\mathcal E^{\mathrm V}_k$;",
     r"$\mathfrak P^{\mathrm M}_k=\Gamma\mathfrak P^{\mathrm U}_k(1+2\times10^{-5})$(2차 $\mathfrak P^{\mathrm V}_k$ — 첨자 V가 7.3의 옛 매개변수 $V$를 가리켜 E7이 바꿈; 1차 $\mathcal E^{\mathrm V}_k$;"),
    (r"라틴 대문자: $D$, $G$, $I$, $K$, $R$, $U$.", r"라틴 대문자: $D$, $I$, $K$, $R$, $U$."),
])
sub(r"구조표_v2.md", [
    (r"$\mathfrak P_k(n)\le\Gamma\,\mathfrak P_k(\infty)\le V$", r"$\mathfrak P_k(n)\le\Gamma\,\mathfrak P_k(\infty)\le G$"),
])
sub(r"원고_자료\README.md", [
    (r"결정 여유 $\eta$와 $V\sqrt k$는", r"결정 여유 $\eta$와 $G\sqrt k$는"),
])
sub(r"장v2\부록D_장7A.md", [
    (r"범위 1에서 $3.250\times10^{-4}$, 범위 2에서 $7.808\times10^{-5}$, 범위 3에서 $2.275\times10^{-4}$이며, 꼭짓점 조건",
     r"범위 1에서 $3.24\times10^{-4}$, 범위 2에서 $7.80\times10^{-5}$, 범위 3에서 $2.27\times10^{-4}$보다 크며, 꼭짓점 조건"),
])
