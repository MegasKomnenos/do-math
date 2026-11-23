---
weight: step
short: the series of e^{-n} c_n has sum e
---
## Description

The series $\sum_{n \ge 0} e^{-n} c_n$, with $c_n = (n+1)^{n-1}/n!$, converges and has the sum $e$.

## Statement

The series of positive real numbers

$$\sum_{n \ge 0} e^{-n}\, c_n$$

converges, and its sum is $e$. Here $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

This is the sum of the Borel weights, `Parking.hasSum_borel`, written in the shifted indexing $c_n = a_{n+1}$ of the Cayley coefficients $a_j = j^{j-1}/j!$. In terms of the series $P = \sum_n c_n X^n$ it is the value $P(e^{-1}) = e$, in agreement with the classical relation $P = e^{T}$ and the value $T(e^{-1}) = 1$ of the tree function. Its one use is as the input "the renewal sequence has a finite sum" in the proof of `Parking.hasSum_eps`.

In Lean the statement is `HasSum (fun n : ℕ => Real.exp (-n) * cc n) (Real.exp 1)`.

## Proof

By `Parking.hasSum_borel`, $\sum_{j \ge 0} e^{-j} a_j = 1$, and the term $j = 0$ is zero because $a_0 = 0$. Hence $\sum_{n \ge 0} e^{-(n+1)} a_{n+1} = 1$. Since $c_n = a_{n+1}$ and $e^{-n} = e \cdot e^{-(n+1)}$, each term of the series in question is $e$ times the corresponding term of this one, so its sum is $e$.
