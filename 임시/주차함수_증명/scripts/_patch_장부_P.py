# -*- coding: utf-8 -*-
"""대조 보고 P의 장부 제안(W₀′/W₀″, Ψ^low(b), 허용 나무 수, Ren(0))을 장부_기호용어이름.md에 반영한다."""
import io

p = "임시/주차함수_증명/장부_기호용어이름.md"
s = io.open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)


rep(r"| $W_0'(N)$ | 생존 없는 핵 질량 상계의 양 $\sum_{g\ge k+2}\pi_N(g)k/g$ | 7.4 | [rae1f209] §1 | 정리 W와 구별 문장 |",
    r"| $W_0'(N)$, $W_0''(N)$ | 생존 없는 핵 질량 상계의 양 $W_0'(N)=\sum_{g=k+2}^N\pi_N(g)k/g$(7.2 명제 R의 입력, [r77e234e]/p-theta-circ-kernel-bound)와 잘린 판 $W_0''(N)=\sum_{g=k+104}^N\pi_N(g)k/g$(7.4 정리 P◇′) | 7.2, 7.4 | [rae1f209] §1·§5.1 | 기록 [r5909c9e] §3.4는 잘린 판을 $W_0'$로 적음(대조 보고 P 1.3(가)). 정리 W·$W_L$과 구별 문장 |")

rep(r"| $\xi$, $\Psi^{low}(\xi)$, $F^{low}(k,\theta')$, 50칸, $a$ | 창 좌표 $b/k^{2/3}$, 칸 하계, 한 변수 함수, 격자 | 7.4 | [r5909c9e] §3 ($y$) |",
    r"| $\xi$, $\Psi^{low}(b)$, $F^{low}(k,\theta')$, 50칸, $a$ | 창 좌표 $b/k^{2/3}$, 칸 하계 $\Psi^{low}(d)=0.3989(2\sqrt d-1.678)$(정수 $b$ 또는 $d$의 함수; $\xi$의 함수가 아님), 한 변수 함수, 격자 | 7.4 | [r5909c9e] §3 ($y$) |")

rep(r"| 상수 $4/(3\sqrt{2\pi})=0.53192$ | — | $I_1$ ([re71a735]) | $\mathcal I_1$ | 4.3의 $I$와 구별 |",
    r"| 상수 $4/(3\sqrt{2\pi})=0.53192$ | — | $I_1$ ([re71a735]) | $\mathcal I_1$ | 4.3의 $I$와 구별 |" + "\n" +
    r"| 크기 $s$의 허용 나무 수 $\min(s,\ell+1)A_{s-1,\ell}$ | 없음(2.4의 허용 나무 생성함수 $T_\ell(z)$의 계수로만 있음) | $c_N(\kappa)=\min(N,\kappa)A_{N-1,\kappa-1}$ ([r4868e30] §1), $T_\ell(s)$ ([r5909c9e] §1) | $\mathcal N_\ell(s)$ | 2.4에서 정의. 수준 질량 $c_m(Y)$와 충돌 회피. $c_N(\kappa)=\mathcal N_{\kappa-1}(N)$ |" + "\n" +
    r"| 갱신 방문 핵의 0번째 값 | — | $c_0:=1$ ([r4868e30]) | $\mathrm{Ren}(0):=1$ | 2.9에서 규약으로 둠 |")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("장부 patched")
