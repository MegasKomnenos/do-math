---
weight: unit
short: normalised parking numbers c_n
---
## Description

The numbers $c_n = (n+1)^{n-1}/n!$ for $n \ge 0$: the number of parking functions of length $n$ divided by $n!$. They are the Cayley coefficients shifted by one, $c_n = a_{n+1}$.

## Statement

For a natural number $n$,

$$c_n = a_{n+1} = \frac{(n+1)^{n-1}}{n!},$$

where $a_j = j^{j-1}/j!$ is the Cayley coefficient (`Parking.cay`). In particular $c_0 = 1$.

## Explanation

There are $(n+1)^{n-1}$ parking functions of length $n$, so $c_n$ is that number divided by $n!$. Inside the library this is the statement `Parking.A_eq_pow`, and in normalised form `Parking.zr_eq_cc`: a count of parking functions of length $n$ with a bound on the displacement that is too large to exclude anything, divided by $n!$, equals $c_n$. The sequence $c$ is therefore the reference against which the counts with an effective displacement bound are measured throughout the library.

The sequence is determined by $c_0 = 1$ and the recursion $(n+1)\,c_{n+1} = \sum_{j \le n} (j+1)\,c_j\,c_{n-j}$ (`Parking.cc_rec`), which is the last-car recursion of parking functions without a displacement bound, divided by $n!$. Its generating series is $P = \sum_n c_n X^n$ (`Parking.TreeSeries.Pser`).

The definition in Lean is `cc n = cay (n + 1)`. Unfolded, this is $(n+1)^n/(n+1)!$ (`Parking.cc_eq`), which equals $(n+1)^{n-1}/n!$ after cancelling a factor $n+1$. At $n = 0$ the second form reads $1^{-1}/0! = 1$.
