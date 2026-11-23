---
weight: unit
short: unimodality by maximum displacement, as posed
---
## Description

The root proposition: for every integer $n\ge1$ the sequence $(b_{n,0},b_{n,1},\dots,b_{n,n-1})$ is unimodal, where $b_{n,\ell}$ is the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

## Statement

**Definitions.** Let $n\ge1$ be an integer. A *preference sequence* of length $n$ is $\alpha=(a_1,\dots,a_n)\in\{1,\dots,n\}^n$. Spots $1,\dots,n$ lie in a row and are all empty at the start. Cars $1,2,\dots,n$ arrive in this order, and car $i$ looks from spot $a_i$ onward, in the direction of increasing spot numbers, and parks in the first empty spot it meets. If the spots $a_i,a_i+1,\dots,n$ are all occupied, car $i$ cannot park. If every car parks, $\alpha$ is called a *parking function*, and the set of all parking functions of length $n$ is written $\mathrm{PF}_n$.

For $\alpha\in\mathrm{PF}_n$, let $\mathrm{pos}_i(\alpha)$ be the spot in which car $i$ parks. The *displacement* of car $i$ is $d_i(\alpha)=\mathrm{pos}_i(\alpha)-a_i\ge0$, and the *maximum displacement* of $\alpha$ is $M(\alpha)=\max_{1\le i\le n}d_i(\alpha)\in\{0,1,\dots,n-1\}$. For $0\le\ell\le n-1$ put
$$b_{n,\ell}=\#\{\alpha\in\mathrm{PF}_n:\ M(\alpha)=\ell\}.$$

A finite sequence $(c_0,\dots,c_m)$ is *unimodal* if there is some $j^*\in\{0,\dots,m\}$ such that $c_{j-1}\le c_j$ holds for $1\le j\le j^*$ and $c_j\ge c_{j+1}$ holds for $j^*\le j\le m-1$. Equality is allowed.

**Proposition.** For every integer $n\ge1$ the sequence $(b_{n,0},b_{n,1},\dots,b_{n,n-1})$ is unimodal. That is, for every $n\ge1$ there is some $\ell^*\in\{0,\dots,n-1\}$ such that $b_{n,\ell-1}\le b_{n,\ell}$ for $1\le\ell\le\ell^*$ and $b_{n,\ell}\ge b_{n,\ell+1}$ for $\ell^*\le\ell\le n-2$.

## Explanation

**What this record is.** This is the proposition as it was posed, in the conventions in which it was posed: spots and cars are numbered from $1$. The record carries no proof. In the packaged library `Parking.root_unimodal` is this statement with its proof left open, and the proved theorem is carried under the name `Parking.root_unimodal_proof`, with the identical Lean statement; the record of that name contains the proof and an account of the whole argument. In the source tree of the library, before packaging, the proved theorem of the module `Parking.Unimodal` is itself named `root_unimodal`, and no declaration `root_unimodal_proof` exists there.

**The Lean statement, read against the proposition.** The Lean statement is

`theorem root_unimodal (n : ℕ) (hn : 1 ≤ n) : ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧ (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ)`.

- `(n : ℕ) (hn : 1 ≤ n)` is "for every integer $n\ge1$".
- `∃ p, p ≤ n - 1` is "there is some $\ell^*\in\{0,\dots,n-1\}$"; the index `p` stands for $\ell^*$. Here `n - 1` is the subtraction of natural numbers, which is the ordinary $n-1$ because $n\ge1$.
- `∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ` is "$b_{n,\ell-1}\le b_{n,\ell}$ for $1\le\ell\le\ell^*$"; `ℓ - 1` is exact because $\ell\ge1$.
- `∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ` is "$b_{n,\ell}\ge b_{n,\ell+1}$ for $\ell^*\le\ell\le n-2$". The range is written $\ell+1\le n-1$ and not $\ell\le n-2$, because for $n=1$ the natural-number subtraction would make $n-2$ equal to $0$ and admit $\ell=0$; with $\ell+1\le n-1$ the range is empty for $n=1$, as it is in the proposition.
- `b n ℓ` is $b_{n,\ell}$ (`Parking.b`): the number of functions `α : Fin n → Fin n` with `maxDisp α = some ℓ`.

**The objects behind `b n ℓ`.** A function `α : Fin n → Fin n` is a preference sequence with cars and spots numbered $0,\dots,n-1$; it corresponds to $(a_1,\dots,a_n)$ by $a_i=\alpha(i-1)+1$ (`Parking.prefList`). The process is `Parking.parkFrom` on the empty street, built from `Parking.firstFree`: a car with preference $a$ takes the least spot $s\ge a$ on the street that is still free, which is "the first empty spot it meets from $a_i$ onward"; the value `none` stands for "car $i$ cannot park", which happens exactly when all the spots from its preference to the end of the street are occupied. `Parking.positions α` is the list of the spots $\mathrm{pos}_i(\alpha)$, shifted by one, or `none` if some car cannot park. The displacements $\mathrm{pos}_i-a_i$ are differences of two numbers that are both shifted by one, so they are the same in the two numberings (`Parking.dispList`). `Parking.maxDisp α` is `some` $M(\alpha)$ for a parking function and `none` otherwise, so `maxDisp α = some ℓ` says "$\alpha\in\mathrm{PF}_n$ and $M(\alpha)=\ell$", and `b n ℓ` counts exactly the set in the definition of $b_{n,\ell}$.

**What is not part of the proposition.** The proposition speaks only of the numbers $b_{n,\ell}$ with $0\le\ell\le n-1$. The facts that accompany it where it is posed, namely $|\mathrm{PF}_n|=(n+1)^{n-1}$, $b_{n,\ell}\ge1$, $\sum_\ell b_{n,\ell}=(n+1)^{n-1}$, $b_{n,0}=n!$ and $b_{n,n-1}=n^{n-2}$, are not asserted by the Lean statement, and the unimodality does not depend on them. The range $M(\alpha)\in\{0,\dots,n-1\}$ is likewise a remark: in Lean `b n ℓ` is defined for every natural number $\ell$ and the statement uses it only for $\ell\le n-1$.
