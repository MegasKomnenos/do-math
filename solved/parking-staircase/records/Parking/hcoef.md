---
weight: step
short: coefficients of the series X^j P^(j+1)
---
## Description

The number $h_{j,s}$ is the coefficient of $X^s$ in the power series $X^j P^{j+1}$, where $P = \sum_n c_n X^n$ and $c_n = (n+1)^{n-1}/n!$.

## Statement

For natural numbers $j$ and $s$,

$$h_{j,s} = [X^s]\; X^j\,P(X)^{j+1},$$

where $P = \sum_{n\ge0} c_nX^n$ is the power series of `Parking.TreeSeries.Pser` with the coefficients $c_n = (n+1)^{n-1}/n!$ of `Parking.cc`. In Lean: `hcoef j s`.

## Explanation

These coefficients exist only to define the sequence $H_s = \sum_{j\le s}2^{-j}h_{j,s}$ of `Parking.Hres` and through it the resolvent sequence $G$ of `Parking.Gres`; the record of `Parking.Hres` says why the series $X^jP^{j+1}$ appear.

Three facts about $h_{j,s}$ are used, all inside the proofs of `Parking.Gres_isRenewal` and `Parking.Gres_lower`, where their arguments are given. First, $h_{j,s} = 0$ for $s < j$, because $X^j$ divides the series, and $h_{0,s} = c_s$. Second, there is a closed form: for $j \le s$,

$$h_{j,s} = \frac{w_{s-j}(j+1)}{(s-j)!}, \qquad w_0(x) = 1,\quad w_n(x) = x\,(x+n)^{n-1}\ (n\ge1),$$

with the Abel weights $w_n$ of `Parking.abelW`; explicitly $h_{j,s} = (j+1)(s+1)^{s-j-1}/(s-j)!$ for $j < s$ and $h_{s,s} = 1$. Third, consecutive coefficients are related by $h_{j+1,s}\,(j+1)(s+1) = h_{j,s}\,(j+2)(s-j)$ for $j + 1 \le s$.
