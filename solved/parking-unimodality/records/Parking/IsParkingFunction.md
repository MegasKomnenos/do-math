---
weight: unit
short: parking function
---
## Description

A preference sequence $\alpha$ of length $n$ is a parking function if every one of the $n$ cars finds a spot when they arrive in order at the empty street.

## Statement

Let $n$ be a natural number and let $\alpha$ be a function from $\{0,\dots,n-1\}$ to itself. $\alpha$ is a *parking function* (of length $n$) if the sequence $\operatorname{pos}(\alpha)$ of the spots taken by the cars (`Parking.positions`) is defined, that is, if each car $i=0,\dots,n-1$ in turn finds a spot $s$ with $\alpha(i)\le s<n$ that no earlier car has taken.

## Explanation

This is the definition of the root proposition: a preference sequence is a parking function when every car parks. Numbered from $1$ as there, the sequence is $(a_1,\dots,a_n)$ with $a_i=\alpha(i-1)+1$. The number of parking functions of length $n$ is $(n+1)^{n-1}$. The library proves this formula for the count $A(n,k)$ of `Parking.A` with $n\le k+1$ (`Parking.A_eq_pow`), by the last-car recursion; that $A(n,k)$ is then the number of all parking functions of length $n$ rests on the remark that no displacement exceeds $n-1$, which the library does not state.

In Lean, `Parking.IsParkingFunction α` is `(Parking.positions α).isSome`. The library states this property for the reader and does not use it afterwards: the counts `Parking.b` and `Parking.A` are defined through the maximum displacement `Parking.maxDisp`, which is defined exactly for the parking functions, so the condition "is a parking function" is contained in the condition "the maximum displacement is $\ell$". No theorem of the library mentions `IsParkingFunction`.
