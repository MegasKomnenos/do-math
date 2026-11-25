---
weight: unit
short: maximum displacement
---
## Description

The maximum displacement $M(\alpha)$ of a parking function $\alpha$: the largest difference between the spot a car takes and the spot it prefers. It is undefined when $\alpha$ is not a parking function.

## Statement

Let $n$ be a natural number and let $\alpha$ be a function from $\{0,\dots,n-1\}$ to itself. If $\alpha$ is a parking function, with the spots $\operatorname{pos}(\alpha)=(p_0,\dots,p_{n-1})$ taken by the cars (`Parking.positions`), then
$$M(\alpha)=\max\bigl(0,\ p_0-\alpha(0),\ \dots,\ p_{n-1}-\alpha(n-1)\bigr).$$
If $\alpha$ is not a parking function, $M(\alpha)$ is undefined.

For $n\ge1$ this is the maximum of the $n$ displacements $p_i-\alpha(i)\ge0$. For $n=0$ the only function is the empty one, it is a parking function, and $M=0$.

## Explanation

**The object.** This is the statistic of the root proposition, $M(\alpha)=\max_i d_i(\alpha)$ with $d_i(\alpha)=\mathrm{pos}_i(\alpha)-a_i$. The displacements do not depend on whether spots are numbered from $0$ or from $1$ (`Parking.dispList`), so $M$ is the same number in both conventions. For a parking function of length $n\ge1$ one has $0\le M(\alpha)\le n-1$, since a car that prefers the spot $a$ takes a spot between $a$ and $n-1$; the library does not need this bound as a statement and does not prove it. $M(\alpha)=0$ means that every car parks in the spot it prefers, that is, that $\alpha$ is a permutation.

**The Lean form.** `Parking.maxDisp α` has the type `Option ℕ` and is
`(positions α).map fun ps => (dispList (prefList α) ps).foldr max 0`:
when `positions α` is `some ps` it is `some` of the maximum of the list of displacements, and when `positions α` is `none` it is `none`. The maximum is computed by `foldr max 0`, which starts from $0$; this is why the empty list has maximum $0$ and why the statement writes $0$ among the numbers of which the maximum is taken.

**Why `none` and not a number.** Giving $M$ the value `none` on the sequences that are not parking functions makes one equation carry two conditions: `maxDisp α = some ℓ` says that $\alpha$ is a parking function and that its maximum displacement is $\ell$. The counts `Parking.b` and `Parking.A` are defined by this equation, over all functions $\alpha$, and so need no separate type or set of parking functions. A convention that assigned a number, say $0$, to the sequences that do not park would have made these sequences count as parking functions with maximum displacement $0$.
