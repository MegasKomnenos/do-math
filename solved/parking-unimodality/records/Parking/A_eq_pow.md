---
weight: step
short: the count in the free range
---
## Description

$A(n,k)=(n+1)^{n-1}$ whenever $n\le k+1$, where $A(n,k)$ is the number of parking functions of length $n$ with maximum displacement at most $k$.

## Statement

For all natural numbers $n$ and $k$ with $n\le k+1$, $A(n,k)=(n+1)^{n-1}$, where $A(n,k)$ (`Parking.A`) is the number of parking functions of length $n$ with maximum displacement at most $k$. For $n=0$ the right-hand side is $1$.

## Explanation

This is `Parking.zr_eq_cc` for the threshold $y=k+1$, multiplied by $n!$ and stated for natural numbers. In a parking function of length $n$ no displacement exceeds $n-1$, so for $n\le k+1$ the bound $k$ is no restriction, and the statement is the classical formula $(n+1)^{n-1}$ for the number of parking functions of length $n$. The library does not argue in this way: as explained in `Parking.zr_eq_cc`, it derives the formula from the last-car recursion `Parking.A_succ` and from the fact that the numbers $(n+1)^{n-1}/n!$ satisfy the recursion without a bound (`Parking.cc_rec`, a form of Abel's binomial identity). The table of two signs (`Parking.Tab.two_signs`) uses the statement for the numbers $P_n=(n+1)^{n-1}$ of its recursion.

In Lean the exponent is `n - 1` with the subtraction of natural numbers; for $n=0$ it is $0$, and $(0+1)^0=1$ agrees with the ordinary reading $1^{-1}=1$.

## Proof

By `Parking.zr_eq_cc` with $y=k+1\ge1$ and $n\le y$, $A(n,k)/n!=z^{(k+1)}_n=c_n$. By `Parking.cc_eq`, $c_n=(n+1)^n/(n+1)!$, and $(n+1)^n/(n+1)!=(n+1)^{n-1}/n!$ (for $n=0$ both are $1$). Hence $A(n,k)/n!=(n+1)^{n-1}/n!$ as real numbers, and multiplying by $n!$ gives the identity of natural numbers.
