# -*- coding: utf-8 -*-
"""장9 산문 퇴고 5묶음: 부록 D 조각(부록D_장9.md)의 산문."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""**알고리즘.** A와 B에서는 $\xi$ 구간을 기하 격자로 나누고(A는 $20000$ 구간, B는 $4000$ 구간), 구간 $[\xi_a,\xi_b]$마다 $\xi$에 증가하는 몫은 $\xi_b$에서, $\mathcal L$의 분자 $0.7978\sqrt\xi-0.8848\upsilon$은 $\xi_a$에서 막아 $\mathcal G/\mathcal L$의 구간별 상계를 구한다.""",
 r"""**알고리즘.** A와 B에서는 $\xi$ 구간을 기하 격자로 나누고(A는 $20000$ 구간, B는 $4000$ 구간), 구간 $[\xi_a,\xi_b]$마다 단조성으로 한쪽 끝의 값을 쓴다. 곧 $\xi$에 증가하는 몫은 $\xi_b$에서, $\mathcal L$의 분자 $0.7978\sqrt\xi-0.8848\upsilon$은 $\xi_a$에서 막아 $\mathcal G/\mathcal L$의 구간별 상계를 구한다."""),

(r"""**알고리즘.** 두 적분은 $k=6668$에서 피적분함수가 처음 양이 되는 점 $\mathfrak t_0=\frac1k+c^{2/3}$($c$는 $(\mathfrak t-\frac1k)^{-3/2}$의 계수) 바로 아래의 점 $T$부터 적분의 위 끝까지를 같은 길이의 칸 $80000$개로 나누고, 칸마다 피적분함수를 칸 전체 위에서 구간 산술로 포위한 값에 칸 길이를 곱해 더한다.""",
 r"""**알고리즘.** 두 적분은 다음과 같이 포위한다. $k=6668$에서 피적분함수가 처음 양이 되는 점 $\mathfrak t_0=\frac1k+c^{2/3}$($c$는 $(\mathfrak t-\frac1k)^{-3/2}$의 계수) 바로 아래의 점 $T$부터 적분의 위 끝까지를 같은 길이의 칸 $80000$개로 나누고, 칸마다 피적분함수를 칸 전체 위에서 구간 산술로 포위한 값에 칸 길이를 곱해 더한다."""),

(r"""이고 $\mathsf L_\ast(6668)\in[1.20601,1.20607]$, 곧 $\mathsf L_\ast(6668)\approx1.206$이고 증명에 쓰이는 하계 $\mathsf L_\ast(6668)\ge1.206$이 나오며, 아래 끝이 $1.0845$보다 $0.1215$ 크다(적분으로 내리기 전의 이산합 $\mathcal H_k+\mathcal H'_k$는 기록의 배정밀도 값 $1.2066$).""",
 r"""이고 $\mathsf L_\ast(6668)\in[1.20601,1.20607]$이다. 곧 $\mathsf L_\ast(6668)\approx1.206$이고, 증명에 쓰이는 하계 $\mathsf L_\ast(6668)\ge1.206$이 나오며, 아래 끝은 $1.0845$보다 $0.1215$ 크다(적분으로 내리기 전의 이산합 $\mathcal H_k+\mathcal H'_k$는 기록의 배정밀도 값 $1.2066$)."""),

(r"""(다)·(라)에서 덮을 $\nu$의 범위는 이렇게 정한다. 배정밀도로 찾은 $\nu_1(k)$의 후보 $M$에서 $\mathcal F_k(M)\ge0$을 구간으로 확인하면 $\nu_1(k)\le M$이므로 $103\le\nu\le M-1$을 덮으면 된다. (다) $\nu$의 구간 $[\nu_a,\nu_b]$에서 $P^{\theta\dagger}$는 $\nu_a$에서(합을 $t'=k+\nu_a+1$부터), $\varrho^\dagger$와 $\varrho^{\mathrm H}$는 $\nu_b$에서 평가한 한쪽 경계""",
 r"""(다)·(라)에서 덮을 $\nu$의 범위는 이렇게 정한다. 배정밀도로 찾은 $\nu_1(k)$의 후보 $M$에서 $\mathcal F_k(M)\ge0$을 구간으로 확인하면 $\nu_1(k)\le M$이므로, $103\le\nu\le M-1$을 덮으면 된다. (다) $\nu$의 구간 $[\nu_a,\nu_b]$에서는 한쪽 경계 하나를 평가한다. $P^{\theta\dagger}$는 $\nu_a$에서(합을 $t'=k+\nu_a+1$부터), $\varrho^\dagger$와 $\varrho^{\mathrm H}$는 $\nu_b$에서 평가한 경계"""),

(r"""선형 최소화의 값은 쌍대 가능해로 아래에서 막는다. 다면체의 모든 점 $z$와 모든 $\lambda\ge0$에서""",
 r"""선형 최소화의 값은 쌍대 가능해로 아래에서 막는다. 그 까닭은 이렇다. 다면체의 모든 점 $z$와 모든 $\lambda\ge0$에서"""),

(r"""이고, 오른쪽이 블록의 모든 $\nu$에서 $\mathrm{LP}_k(2k+\nu)$의 하계다.""",
 r"""이고, 오른쪽이 구간의 모든 $\nu$에서 $\mathrm{LP}_k(2k+\nu)$의 하계다."""),

(r"""**알고리즘.** $[0.48,1]$을 $5200$개 구간 $[\vartheta_a,\vartheta_b]$로 나누고, 구간마다 $\vartheta$에 감소하는 인자 $((N+1)/(\nu+1))^{3/2}$는 $\vartheta_b$에서, 감소하는 $A^\diamond_{\mathrm{dec}}$는 $\vartheta_a$에서, 증가하는 $\mathfrak e$ 몫은 $\vartheta_b$에서 평가해 $\mathfrak F(6668,\vartheta)$의 구간 하계를 구하고 최솟값을 읽는다.""",
 r"""**알고리즘.** $[0.48,1]$을 $5200$개 구간 $[\vartheta_a,\vartheta_b]$로 나누고, 구간마다 단조성으로 한쪽 끝의 값을 쓴다. 곧 $\vartheta$에 감소하는 인자 $((N+1)/(\nu+1))^{3/2}$는 $\vartheta_b$에서, 감소하는 $A^\diamond_{\mathrm{dec}}$는 $\vartheta_a$에서, 증가하는 $\mathfrak e$ 몫은 $\vartheta_b$에서 평가해 $\mathfrak F(6668,\vartheta)$의 구간 하계를 구하고 최솟값을 읽는다."""),
]

if __name__ == "__main__":
    apply("장v2/부록D_장9.md", PAIRS, dry="--dry" in sys.argv)
