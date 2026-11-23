---
weight: unit
short: preference sequence of a function
---
## Description

The preferences of a function $\alpha$ from $\{0,\dots,n-1\}$ to itself, written as the sequence $(\alpha(0),\dots,\alpha(n-1))$ of natural numbers.

## Statement

Let $n$ be a natural number and let $\alpha$ be a function from $\{0,\dots,n-1\}$ to $\{0,\dots,n-1\}$. Its preference sequence is the sequence $(\alpha(0),\alpha(1),\dots,\alpha(n-1))$ of length $n$, read as a sequence of natural numbers.

## Explanation

In the library a preference sequence of length $n$ is a function `α : Fin n → Fin n`: the argument is a car and the value is the spot that this car prefers, both numbered $0,\dots,n-1$. The root proposition writes the same object as $(a_1,\dots,a_n)\in\{1,\dots,n\}^n$, with cars and spots numbered from $1$; the correspondence is $a_i=\alpha(i-1)+1$.

`Parking.prefList α` is `List.ofFn fun i => (α i : ℕ)`, the list of the values of $\alpha$ in the order of the cars, each value converted from `Fin n` to a natural number. It is the form in which $\alpha$ is given to the parking process `Parking.parkFrom`, which works with lists of natural numbers. Different functions have different preference sequences, and the preference sequences are exactly the sequences of length $n$ with entries smaller than $n$, so counting functions $\alpha$ and counting such sequences is the same; the proof of `Parking.A_succ` passes between the two.

The functions are taken on the finite type `Fin n` so that the set of all preference sequences of length $n$ is a finite set that Lean can count (`Finset.univ`), which is how `Parking.b` and `Parking.A` are defined.
