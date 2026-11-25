---
weight: step
short: cross-ratio form of log-convexity
---
## Description

In a positive log-convex sequence $G$, $\ G_{a+c}\,G_b\le G_a\,G_{b+c}$ whenever $a\le b$.

## Statement

Let $(G_n)_{n\ge0}$ be a sequence of real numbers with $G_n>0$ for every $n$ and $G_{n+1}^2\le G_nG_{n+2}$ for every $n$. Then for all natural numbers $a\le b$ and $c$,
$$G_{a+c}\,G_b\ \le\ G_a\,G_{b+c}.$$

## Explanation

Log-convexity says that the ratios $G_{n+1}/G_n$ do not decrease. The statement is the consequence for ratios over a distance $c$: $G_{a+c}/G_a\le G_{b+c}/G_b$ for $a\le b$. It is written without division, as all statements of this kind in the library are.

It is applied to the kernel $\varepsilon_m=(m-1)^{m-1}/m!$ with the index shifted by one (`Parking.eps_cross`) and to the renewal sequence of a log-convex kernel in the proof of the extreme-column bound (`Parking.extreme_column_le`).

## Proof

First, for $i\le k$: $G_{i+1}G_k\le G_iG_{k+1}$. This is proved by induction on $k\ge i$. For $k=i$ it is an equality. If it holds for $k$, then
$$G_k\cdot G_{i+1}G_{k+1}=(G_{i+1}G_k)\,G_{k+1}\le G_iG_{k+1}^2\le G_i\,G_kG_{k+2}=G_k\cdot G_iG_{k+2},$$
by the induction hypothesis and by log-convexity at $k$; dividing by $G_k>0$ gives the inequality for $k+1$.

The statement follows by induction on $c$. For $c=0$ it is an equality. If $G_{a+c}G_b\le G_aG_{b+c}$, then with the first step applied to $i=a+c\le k=b+c$,
$$G_{b+c}\cdot G_{a+c+1}G_b=(G_{a+c+1}G_{b+c})\,G_b\le G_{a+c}G_{b+c+1}\,G_b=(G_{a+c}G_b)\,G_{b+c+1}\le G_aG_{b+c}\,G_{b+c+1},$$
and dividing by $G_{b+c}>0$ gives $G_{a+c+1}G_b\le G_aG_{b+c+1}$.
