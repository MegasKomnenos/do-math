---
weight: unit
short: property K of the diagonal triples of tilted masses in the first layer
---
## Description

For $k\ge 7$ and $0\le\rho\le k-2$, at the critical tilt $x_k$, the tilted masses $u^{(k-1)}_{k-1+\rho}$, $u^{(k)}_{k+\rho}$, $u^{(k+1)}_{k+1+\rho}$ of the thresholds $k-1$, $k$, $k+1$ at the sizes that exceed the threshold by $\rho$ form a triple with property K at $k$.

## Statement

Let $k\ge 7$ and $\rho$ be natural numbers with $\rho+2\le k$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and, for a threshold $y\ge 1$, $u^{(y)}_N=z^{(y)}_N\,x_k^{\,N}$, where $z^{(y)}_N=A(N,y-1)/N!$ and $A(N,y-1)$ is the number of parking functions of length $N$ all of whose displacements are smaller than $y$ (`Parking.zrT y (xcrit k) N`). Then the triple
$$\big(u^{(k-1)}_{k-1+\rho},\ u^{(k)}_{k+\rho},\ u^{(k+1)}_{k+1+\rho}\big)$$
has property K at $k$ (`Parking.FirstLayer.TK`): for every real $\mu\ge 0$,
$$2\,e^{\mu/k}\,u^{(k)}_{k+\rho}\;\le\;e^{\mu}\,u^{(k+1)}_{k+1+\rho}+e^{-\mu}\,u^{(k-1)}_{k-1+\rho}.$$

## Explanation

**The object.** The three masses lie on a diagonal of the array indexed by threshold and size: raising the threshold by one and the size by one keeps the excess $\rho$ of the size over the threshold. All three are tilted with the same number $x_k$, the critical tilt of the middle threshold. The range $0\le\rho\le k-2$ means that the middle size $N=k+\rho$ runs through $k,\dots,2k-2$; these are sizes in the first layer of each of the three thresholds, where the last-car recursion has the simple form of `Parking.FirstLayer.zrT_split`.

**What is obtained from it.** At $\mu=0$ the statement is the convexity of the tilted masses along the diagonal (`Parking.FirstLayer.zrT_diag_convex`), and after multiplication by the factor $z\mapsto z+\beta$ it is the weighted form `Parking.FirstLayer.zrT_weak_requirement`. These two inequalities are everything the rest of the library takes from the first layer.

**Why the statement is about property K.** The convexity at $\mu=0$ is what is wanted, but it cannot be proved by itself. The recursion expresses the triple of the excess $\rho$ through the triples of the excesses $1,\dots,\rho-1$, each multiplied by a factor $(c+i+1)/(c+\rho)$ that increases with the threshold $c$, and convexity of a triple is destroyed by such a factor. Property K is the strengthening that survives it (`Parking.FirstLayer.TK`, `Parking.FirstLayer.TK.mul_ratio`), so the induction is run for the whole family of tilts $\mu\ge 0$.

**The structure of the proof.** For $\rho=0$ the three masses are free and the triple is $(\omega_{k-1},\omega_k,\omega_{k+1})$ with $\omega_n=c_nx_k^{\,n}$ (`Parking.FirstLayer.TK_ccT_top`). For $\rho\ge 1$ the recursion splits each mass into a chain part, handled by the induction hypothesis and the closure of property K under sums, nonnegative multiples and the factors above, and the direct term $S_\rho(c)$ of `Parking.FirstLayer.Sdir`, whose property K is `Parking.FirstLayer.Sdir_TK`. The hypothesis $k\ge 7$ comes from that last statement and from nowhere else.

## Proof

Write $\omega_n=c_nx_k^{\,n}$ (`Parking.ccT`).

**The recursion divided by the size.** For a threshold $c$ and an excess $\rho$ with $1\le\rho\le c-1$,
$$u^{(c)}_{c+\rho}=\sum_{i=0}^{\rho-2}x_k\,\omega_i\,\frac{c+i+1}{c+\rho}\,u^{(c)}_{c+\rho-1-i}\;+\;S_\rho(c).\tag{1}$$
Indeed, `Parking.FirstLayer.zrT_split` with $P=\rho-1$ gives $(c+\rho)\,u^{(c)}_{c+\rho}=x_k\big(\sum_{i<\rho-1}(c+i+1)\,\omega_i\,u^{(c)}_{c+\rho-1-i}+D(c,\rho-1)\big)$, and by `Parking.FirstLayer.direct_generic` (applicable since $(\rho-1)+2\le c$) the direct part is $D(c,\rho-1)=(c+\rho)\,\omega_{\rho-1}\omega_c+\frac{c+\rho+1}{2}Q_\rho(c-\rho-1)$. Dividing by $c+\rho$ and comparing with the definition of $S_\rho(c)$ (`Parking.FirstLayer.Sdir`) gives (1).

**Induction.** The claim is proved by strong induction on $\rho$, for $\rho\le k-2$.

*$\rho=0$.* The sizes $k-1$, $k$, $k+1$ do not exceed the thresholds $k-1$, $k$, $k+1$, so by `Parking.zrT_eq_ccT` the triple is $(\omega_{k-1},\omega_k,\omega_{k+1})$, which has property K at $k$ by `Parking.FirstLayer.TK_ccT_top`.

*$1\le\rho\le k-2$.* Formula (1) holds for each of $c=k-1,k,k+1$, because $\rho\le k-2=(k-1)-1$. The range of $i$ and the constants $x_k\omega_i$ are the same for the three thresholds, so the triple of the statement is the sum of the following triples.

- For each $i=0,\dots,\rho-2$: the triple with the components $x_k\omega_i\,\frac{c+i+1}{c+\rho}\,u^{(c)}_{c+\rho'}$, $c=k-1,k,k+1$, where $\rho'=\rho-1-i$ satisfies $1\le\rho'\le\rho-1$. By the induction hypothesis $\big(u^{(k-1)}_{k-1+\rho'},u^{(k)}_{k+\rho'},u^{(k+1)}_{k+1+\rho'}\big)$ has property K at $k$. Its middle value is nonnegative (`Parking.zrT_nonneg`), so `Parking.FirstLayer.TK.mul_ratio` with $\alpha=i+1\le\beta=\rho$ shows that it keeps the property after multiplication by the values of $(z+i+1)/(z+\rho)$ at $z=k-1,k,k+1$, and `Parking.FirstLayer.TK.smul` that it keeps it after multiplication by $x_k\omega_i\ge 0$.
- The triple $\big(S_\rho(k-1),S_\rho(k),S_\rho(k+1)\big)$, which has property K at $k$ by `Parking.FirstLayer.Sdir_TK`.

By `Parking.FirstLayer.TK.sum` and `Parking.FirstLayer.TK.add` the sum has property K at $k$.
