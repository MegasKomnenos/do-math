---
weight: unit
short: total mass of the Borel law
---
## Description

The series $\sum_{j \ge 1} e^{-j} a_j$, with the Cayley coefficients $a_j = j^{j-1}/j!$, converges and has the sum $1$: the Borel law with parameter $1$ is a probability law, or, in other words, the tree function takes the value $1$ at its singularity $e^{-1}$.

## Statement

The series of nonnegative real numbers

$$\sum_{j \ge 0} e^{-j}\, a_j$$

converges, and its sum is $1$. Here $a_0 = 0$ and $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`), so the term $j = 0$ is zero.

## Explanation

The numbers $e^{-j} j^{j-1}/j!$, $j \ge 1$, are the weights of the Borel distribution with parameter $1$, the law of the total progeny of a critical branching process with Poisson offspring. The statement is the classical fact that these weights add up to $1$. In terms of the tree function $T(x) = \sum_j a_j x^j$ it says $T(e^{-1}) = 1$.

The point $e^{-1}$ is the radius of convergence of the tree function, and the terms of the series decay only like $j^{-3/2}$, so the value is not obtained by substituting into an identity that holds inside the disc of convergence. The usual derivations use the analytic function $T$ and a limit at the boundary. The library avoids analytic functions altogether and argues with two sequences. Put

$$f_j = e^{-j} a_j, \qquad g_n = e^{-n}\,\frac{n^n}{n!}.$$

The finite identity `Parking.ren_conv` says that $g$ is the renewal sequence of $f$: $g_0 = 1$ and $g_n = \sum_{m \le n} f_m\, g_{n-m}$ for $n \ge 1$. In the language of renewal theory, $f$ is a distribution of waiting times, possibly of total mass less than $1$, and $g_n$ is the probability of a renewal at time $n$; the expected number of renewals $\sum_n g_n$ is infinite exactly when the total mass of $f$ is $1$. Here the $g_n$ are the Poisson masses (`Parking.poissonMass`), which by Stirling's formula are of order $n^{-1/2}$, so their sum diverges. The proof below carries this out with partial sums and inequalities only. Its analytic input is the pair of Stirling bounds `Parking.poissonMass_le` and `Parking.poissonMass_ge`.

Within the library the statement is used twice. It gives $\sum_n e^{-n} c_n = e$ (`Parking.hasSum_cc`), from which $\sum_m e^{-m} \varepsilon_m = 1 - e^{-1}$ follows (`Parking.hasSum_eps`). And in the proof of `Parking.kap_diag_le` it bounds every partial sum $\sum_{1 \le j < N} e^{-j} a_j$ by $1$.

In Lean the statement is `HasSum (fun j : ℕ => Real.exp (-j) * cay j) 1`: the family indexed by all natural numbers is summable with sum $1$. For a family of nonnegative real numbers this is the same as convergence of the partial sums to $1$.

## Proof

Let $f_j = e^{-j} a_j$ and $g_n = e^{-n} n^n/n!$ for $j, n \ge 0$, and write $F_M = \sum_{m=0}^{M} f_m$ and $G_M = \sum_{n=0}^{M} g_n$ for the partial sums.

*The properties used.* We have $f_j \ge 0$ (`Parking.cay_nonneg`), $g_n > 0$ (`Parking.poissonMass_pos`), $f_0 = 0$, $g_0 = 1$ (`Parking.poissonMass_zero`), and the renewal equation

$$g_n = \sum_{m=0}^{n} f_m\, g_{n-m} \qquad (n \ge 1). \tag{R}$$

The last is `Parking.ren_conv`, $\sum_{m=0}^{n} a_m \operatorname{ren}(n-m) = \operatorname{ren}(n)$ with $\operatorname{ren}(n) = n^n/n!$, multiplied by $e^{-n} = e^{-m}\,e^{-(n-m)}$. Steps 1 and 2 use only these properties of two sequences $f$ and $g$.

*Step 1: the summed renewal equation.* For every $M \ge 0$,

$$\sum_{m=0}^{M} f_m\, G_{M-m} = G_M - 1.$$

This is proved by induction on $M$. For $M = 0$ the left-hand side is $f_0 G_0 = 0$ and the right-hand side is $g_0 - 1 = 0$. For the step, $G_{M+1-m} = G_{M-m} + g_{M+1-m}$ for $m \le M$, and $G_0 = g_0$, so

$$\sum_{m=0}^{M+1} f_m\, G_{M+1-m} = \sum_{m=0}^{M} f_m\, G_{M-m} + \sum_{m=0}^{M+1} f_m\, g_{M+1-m} = (G_M - 1) + g_{M+1} = G_{M+1} - 1,$$

where the second sum was evaluated by (R) at $n = M+1$.

*Step 2: two inequalities between partial sums.* Since $g \ge 0$, the sequence $G$ is nondecreasing, and $G_M \ge G_0 = 1$. In the summed equation, bound $G_{M-m} \le G_M$:

$$G_M - 1 \le F_M\, G_M, \qquad\text{hence}\qquad 1 - \frac{1}{G_M} \le F_M. \tag{L}$$

Next, apply the summed equation at $M + k$, discard the nonnegative terms with $m > M$, and bound $G_{M+k-m} \ge G_k$ for $m \le M$:

$$F_M\, G_k \le G_{M+k} - 1 \qquad (M, k \ge 0). \tag{U}$$

*Step 3: the Poisson masses are at most $1$, and their sum diverges.* We have $g_0 = 1$, and for $n \ge 1$, by `Parking.poissonMass_le`, $g_n \le 1/\sqrt{2\pi n} \le 1$, because $2\pi n \ge 1$. For the divergence, let $1 \le k \le n$. By `Parking.poissonMass_ge`,

$$g_k \ge \Bigl(1 - \frac{1}{12k}\Bigr)\frac{1}{\sqrt{2\pi k}} \ge \frac{11}{12} \cdot \frac{1}{\sqrt{2\pi n}}.$$

Summing over $k = 1, \dots, n$ gives $G_n \ge \frac{11}{12}\, n/\sqrt{2\pi n} = \frac{11}{12}\sqrt{n}/\sqrt{2\pi}$, so $G_n \to \infty$.

*Step 4: $F_M \le 1$ for every $M$.* Suppose $F_M > 1$ for some $M$. Since $g_n \le 1$, the $M$ additional terms in $G_{M+k}$ add at most $M$: $G_{M+k} \le G_k + M$. With (U), $F_M\, G_k \le G_k + M - 1$, that is, $(F_M - 1)\, G_k \le M - 1$ for every $k$. This contradicts $G_k \to \infty$: for $k$ with $G_k \ge M/(F_M - 1)$ the left-hand side is at least $M$. This is the step at which the divergence is turned into the upper bound, and it is where the hypothesis $g \le 1$ is needed.

*Step 5: conclusion.* By (L) and Step 4, $1 - 1/G_M \le F_M \le 1$ for every $M$, and $1/G_M \to 0$ by Step 3. Hence $F_M \to 1$. The terms $f_j$ are nonnegative, so the convergence of the partial sums is the convergence of the series, and $\sum_j f_j = 1$.
