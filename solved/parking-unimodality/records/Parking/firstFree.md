---
weight: unit
short: first free spot at or after a preference
---
## Description

The spot taken by a car with preference $a$ on a street with the spots $0,\dots,n-1$ when the spots of a set $U$ are occupied: the least spot $s\ge a$ of the street that is not in $U$, and no spot at all if there is none.

## Statement

Let $n$ and $a$ be natural numbers and let $U$ be a finite set of natural numbers. The street of length $n$ consists of the spots $0,1,\dots,n-1$. If there is a spot $s$ with $a\le s<n$ and $s\notin U$, then $\operatorname{first}_n(U,a)$ is the least such $s$. If there is none, that is, if every one of the spots $a,a+1,\dots,n-1$ belongs to $U$ (which includes the case $a\ge n$, where there is no such spot at all), then $\operatorname{first}_n(U,a)$ is undefined.

Spots are numbered from $0$ here; this is the convention of the Lean definition and is kept because the definition is a function of natural numbers.

## Explanation

**What it models.** The spots of a street lie in a row, and those in $U$ are occupied. A car that prefers the spot $a$ drives to $a$ and from there in the direction of increasing spot numbers, and it parks in the first empty spot it meets. If the spots $a,\dots,n-1$ are all occupied, the car leaves the street without parking. $\operatorname{first}_n(U,a)$ is the spot in which the car parks, and it is undefined exactly when the car cannot park. This is one step of the parking process `Parking.parkFrom`, which lets the cars arrive one after another.

**Numbering.** The root proposition numbers the spots $1,\dots,n$. The Lean definitions number them $0,\dots,n-1$, and a spot $s$ here is the spot $s+1$ there. A preference is shifted in the same way, so the difference between the spot taken and the preference, the displacement, is the same in both numberings.

**The Lean form.** `Parking.firstFree n occ a` has the type `Option ℕ`: it is `some s` when the car parks in $s$ and `none` when it cannot park. It is defined as `(List.range n).find? fun s => decide (a ≤ s ∧ s ∉ occ)`, which goes through $0,1,\dots,n-1$ in this order and returns the first number $s$ with $a\le s$ and $s\notin U$. So `firstFree n occ a = some s` holds exactly when $a\le s<n$, $s\notin U$, and every $j$ with $a\le j<s$ belongs to $U$; the proof of the last-car recursion `Parking.A_succ` uses the definition only in this form.

**Why the arguments are arbitrary natural numbers.** Neither $a<n$ nor $U\subseteq\{0,\dots,n-1\}$ is required: a preference $a\ge n$ gives `none`, and elements of $U$ outside the street have no effect. The definition is made on natural numbers, and not on the type `Fin n` of the spots of one street. This serves the proof of `Parking.A_succ`, which compares streets of different lengths and blocks of spots that are translated along the street: with natural numbers a spot keeps its name when the street is lengthened.
