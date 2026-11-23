---
weight: step
short: the composition weights depend on the profile at the cut points only
---
## Description

Two cut profiles that agree at the points $1, \dots, m-1$ give the same weights $V_q(m;\cdot)$ of the compositions of $m$.

## Statement

Let $f, g : \mathbb{N} \to \mathbb{R}$ and let $m$ be a natural number such that $f(s) = g(s)$ for every $s$ with $0 < s < m$. Then $V_q(m;f) = V_q(m;g)$ for every natural number $q$, where $V_q(m;f)$ is defined in `Parking.Vc`.

## Explanation

A cut of a composition of $m$ lies at one of the interior points $1, \dots, m-1$, so the values of the profile elsewhere do not enter the weight. In Lean a profile is a function on all natural numbers, and the statement is what allows a profile to be changed away from the cut points. It is used in the proof of `Parking.Vc_ratio_le`, and its consequence for the totals is `Parking.Lam_congr`.

## Proof

By induction on $q$, for all $m$ at once. For $q = 0$ both sides are $0$, and for $q = 1$ both sides are $a_m$ by `Parking.Vc_one`. For $q + 2$ parts, `Parking.Vc_succ_succ` writes both sides as sums over $0 < s < m$. In the term of index $s$ the factors $f(s)$ and $g(s)$ agree by hypothesis, and $V_{q+1}(s;f) = V_{q+1}(s;g)$ by the induction hypothesis, since the profiles agree on the cut points below $s$.
