---
weight: unit
short: positive step on the curve
---
## Description

For natural numbers $r\ge41$ and $k$ with $(r-1)^3\le k^2\le r^3$, the step of the column $k$ in the row $k+r$ is positive: $b(k+r,k-1)<b(k+r,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ and $r$ be natural numbers with
$$r\ge41\qquad\text{and}\qquad(r-1)^3\le k^2\le r^3 .$$
Then
$$b(k+r,\,k-1)<b(k+r,\,k).$$
In the notation $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$, the conclusion is $d_{k+r,k}>0$.

## Explanation

**What the statement says.** Call $n-k$ the deficit of a position $(n,k)$, and call the set of positions with $k^2=(n-k)^3$ the curve. A position with deficit $r$ is behind the curve when $r^3\le k^2$. The hypothesis $(r-1)^3\le k^2\le r^3$ says that the position $(k+r,k)$ is on the curve or beyond it, and that the position one row higher in the same column, $(k+r-1,k)$, is on the curve or behind it. So $(k+r,k)$ is the first position of its column that is not strictly behind the curve, or the one after it when $k^2$ is a cube. The statement says that the step at such a position is positive.

The hypotheses force $k\ge253$, because $k^2\ge40^3=64000>252^2$. Conversely every column $k\ge253$ has such a position: the least $r$ with $k^2<r^3$ satisfies $(r-1)^3\le k^2\le r^3$, and $r\ge41$ because $k^2\ge253^2=64009>40^3$. `Parking.curve_crossing` is this remark for $k\ge265$.

**Where the position lies relative to the crossing.** The statement does not locate the row in which a column first has a positive step; it certifies a positive step in a row that is explicit in $k$. An exact computation with integers from the last-car recursion, which is not part of the proof, shows the distance: in the column $265$ the step is negative in the rows $265+r$ for $1\le r\le35$ and positive for $36\le r\le45$, and the position of the statement is $r=42$; in the column $253$ the first positive step is at $r=35$, and the position of the statement is $r=41$.

**How it is proved.** The record of `Parking.curve_crossing` tells the whole argument from the top. Here is the shape of the last step, which is the proof below. Put $R=r+1$, $N=k+R$ and $s=\sqrt R$; the position is $(N-1,k)$. The pair–impulse criterion `Parking.dq_pos_of_pair` reduces the claim to the inequality
$$k\,a_k\,\Lambda_R(k+1;N)\ <\ 2\,\mathcal{P}(k,R)$$
between a boundary term, the chain sum $\Lambda_R(k+1;N)$, and the pair sum $\mathcal{P}(k,R)$; the symbols are defined at the beginning of the proof. After division by $k\,a_k\,e^R$ both sides are bounded by closed forms in $s$, and one function of $s$ separates them: with $W_0(s)=\frac{s^2}{2}-1.06385\,s+0.7184$,
$$e^{-R}\,\Lambda_R(k+1;N)\ <\ \frac{2\cdot0.38385\;W_0(s)\,\bigl(1+\frac{1}{10s}\bigr)}{s^3}\ \le\ \frac{2\,\mathcal{P}(k,R)}{k\,a_k\,e^R}.$$
The right inequality is the pair side and rests on `Parking.pairSum_ge` and the three bounds `Parking.Wsum_ge`, `Parking.Gsum_le`, `Parking.Asum_le`. The left inequality is the impulse side and rests on `Parking.impulse_le`. The hypothesis on $k$ enters the pair side as $k\le s^3\le1.07593\,k$ and the impulse side as $k\le(R-1)^{3/2}$.

**How much room the comparison has.** The two sides are of the same order: each is a constant times $c_0/s$, where $c_0=1/\sqrt{2\pi}$. So the comparison is decided by constants, and at the lower end of the range it is close. The following numbers are floating-point evaluations of the two closed forms that `Parking.impulse_numeric` compares, the upper bound of the impulse side and the lower bound of the pair side, both divided by $c_0/s$; they are not part of the proof.

| $R$ | impulse side | pair side | relative room |
|---|---|---|---|
| 42 | 0.6826 | 0.6897 | 1.0 % |
| 43 | 0.6816 | 0.6925 | 1.6 % |
| 50 | 0.6755 | 0.7102 | 4.9 % |
| 100 | 0.6522 | 0.7790 | 16 % |

As $R$ grows the two numbers tend to about $0.59$ and $0.96$. At $R=40$ the same two expressions, evaluated as formulas, are $0.6846$ and $0.6837$, in the wrong order. The range of the statement, $R\ge42$, that is $r\ge41$, thus begins close to the point where the comparison stops holding, and this is why the numerical constants of the statements it uses are given to five or six digits. The staircase uses the statement for $r\ge42$ only, through `Parking.curve_crossing`.

**Two choices in the proof.** The upper bound `Parking.impulse_le` holds at every threshold $K\ge\max(k,R)$ and for every tangent parameter $c'\ge-1$. The proof takes $K=(R-1)(2R-1)/(2s)$, which depends on $R$ alone, is at least $(R-1)^{3/2}\ge k$, and is a rational function of $s$; and it takes $c'=0.35$. The lower bound `Parking.pairSum_ge` has two free parameters as well, and `Parking.pair_numeric` chooses them.

**The Lean form.** The statement is `b (k + r) (k - 1) < b (k + r) k` under `41 ≤ r`, `(r - 1) ^ 3 ≤ k ^ 2`, `k ^ 2 ≤ r ^ 3`. The subtractions $r-1$ and $k-1$ of natural numbers are the ordinary ones, since $r\ge41$ and $k\ge253$. The proof works with the normalised step $\delta^{(k)}_n=d_{n,k}/n!$ (`Parking.dq`), a real number, and passes to the comparison of natural numbers by `Parking.dq_pos_iff`. In the library the argument is a private lemma in the variable $R=r+1$: for $R\ge42$ and $(R-2)^3\le k^2\le(R-1)^3$, $\delta^{(k)}_{k+R-1}>0$. The public statement is this lemma with $r=R-1$.

## Proof

**Notation.** $a_k=k^{k-1}/k!$ (`Parking.cay`). $P(m)=e^{-m}m^m/m!$ is the Poisson mass (`Parking.poissonMass`), and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions (`Parking.kc2`, `Parking.kc3`). $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the cut profile $t\mapsto y/(N-t)$ (`Parking.Lam`, `Parking.thr`). $\mathcal{P}(k,R)$ is the pair sum (`Parking.pairSum`). $W_\Sigma(R)$, $G(k,R)$, $\mathcal A(k,R)$ are the three sums `Parking.Wsum`, `Parking.Gsum`, `Parking.Asum`. $c_0=1/\sqrt{2\pi}$ (`Parking.c0`). $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`).

**Organisation.** Step 0 passes to the variable $R=r+1$ and to the normalised step. Step 1 places the position. Step 2 bounds the pair sum from below and Step 3 bounds the boundary term from above, both by the same function of $s=\sqrt R$. Step 4 applies the criterion.

**Step 0: reduction.** Put $R=r+1$, so that $R\ge42$, the hypotheses read $(R-2)^3\le k^2\le(R-1)^3$, and the row is $k+r=k+R-1$. By `Parking.dq_pos_iff` the claim $b(k+r,k-1)<b(k+r,k)$ is equivalent to $\delta^{(k)}_{k+R-1}>0$, and this is what is proved.

**Step 1: the position.** Let $s=\sqrt R$. Then $R=s^2$, and $s\ge6.48$ by `Parking.sqrt_ge_648`, so that $s>0$. The statement `Parking.k_window` says: for real numbers with $s>0$, $R=s^2\ge42$, $k\ge0$ and $(R-2)^3\le k^2\le(R-1)^3$,
$$k\ \le\ s^3\ \le\ 1.07593\,k .$$
From this, $R+2\le k$: since $s^3=R\,s\ge6.48\,R$, one has $1.07593\,k\ge6.48\,R$, and for $R\ge42$ this gives $k\ge R+2$. Hence $1\le R\le k-2$, which are the hypotheses of the criterion in Step 4, and $k\ge1$, so that $a_k\,e^R>0$ (`Parking.cay_pos`).

**Step 2: the pair side.** Write $W_0=\frac R2-1.06385\,s+0.7184$. The three bounds
$$W_\Sigma(R)\ge W_0,\qquad G(k,R)\le2\,(0.478731\,s^3-0.974453\,s^2+0.642741\,s),\qquad\mathcal A(k,R)\le0.478731\,s^5-0.974453\,s^4+0.642741\,s^3$$
hold by `Parking.Wsum_ge`, `Parking.Gsum_le` and `Parking.Asum_le`; the last two need $s^3\le1.07593\,k$, which is Step 1. The lower bound of the pair sum, `Parking.pairSum_ge`, holds because $k\ge1$ and $R\le k$: for all real $\theta\ge0$ and $\mu$,
$$a_k\,e^R\,e^{-\mu}\Bigl((1+\mu)\,W_\Sigma(R)-\Bigl(\bigl(\log(1+\theta)-\tfrac{\theta}{1+\theta}\bigr)\,G(k,R)+\tfrac{1}{k\,(1+\theta)}\,\mathcal A(k,R)\Bigr)\Bigr)\ \le\ \mathcal{P}(k,R).$$
The statement `Parking.pair_numeric` is an inequality between real numbers that takes exactly these facts as hypotheses: $s\ge6.48$, $R=s^2$, $k\le s^3\le1.07593\,k$, a factor $C=a_ke^R\ge0$, the three bounds, and the last display for all $\theta\ge0$ and $\mu$. It chooses $\theta=R/(2k)$ and a value of $\mu$, and concludes
$$a_k\,e^R\cdot0.38385\,\Bigl(1+\frac{1}{10\,s}\Bigr)\,\frac{k}{s^3}\,W_0\ \le\ \mathcal{P}(k,R).\tag{1}$$

**Step 3: the impulse side.** Let $K=(R-1)(2R-1)/(2s)$. The statement `Parking.K_facts` says: if $s\ge6.48$, $R=s^2$, $K\cdot2s=(R-1)(2R-1)$ and $k^2\le(R-1)^3$, then $R\le K$ and $k\le K$. So the upper bound of the impulse, `Parking.impulse_le`, applies with the threshold $y=k$, since $R\ge1$, $0\le k\le K$ and $R\le K$, and with the parameter $c'=0.35$:
$$e^{-R}\,\Lambda_R(k+1;k+R)\ \le\ P(R)-e^{-0.35}\Bigl(1.35\cdot\frac{R-2}{2\,(K+R-1)}\,\kappa_2(R)-\frac{1}{K+1}\cdot\frac{R-3}{3}\,\kappa_3(R)\cdot\frac{\frac45R-1}{K+\frac35R}\Bigr).$$
The quantities on the right are controlled by five facts:

- $P(R)\le c_0/s$, Stirling's bound `Parking.poissonMass_le_c0`;
- $0<c_0\le0.39894229$ (`Parking.c0_pos`, `Parking.c0_le`);
- $0.704688\le e^{-0.35}\le0.704689$ (`Parking.exp_neg_035_bounds`);
- $\kappa_2(R)\ge\frac12-\bigl(\frac43+\frac{1}{15R}\bigr)P(R)$ (`Parking.kc2_lower`);
- $\kappa_3(R)=(R-1)\,P(R)-2\,\kappa_2(R)$ (`Parking.kc3_eq`).

In the bound of the impulse $\kappa_2(R)$ has a negative coefficient and $\kappa_3(R)$ a positive one, and the closed form of $\kappa_3$ makes the coefficient of $\kappa_2(R)$ more negative; so the lower bound of $\kappa_2$ is the bound that is needed. The statement `Parking.impulse_numeric` is an inequality between real numbers that takes as hypotheses $s\ge6.48$, $R=s^2$, the equation that defines $K$, the displayed bound of $e^{-R}\Lambda_R(k+1;k+R)$, and the five facts. It concludes
$$e^{-R}\,\Lambda_R(k+1;k+R)\ <\ \frac{2\cdot0.38385\;W_0\,\bigl(1+\frac{1}{10s}\bigr)}{s^3}.\tag{2}$$

**Step 4: the criterion.** By Step 1 the pair–impulse criterion `Parking.dq_pos_of_pair` applies: for $1\le R\le k-2$, if $k\,a_k\,\Lambda_R(k+1;k+R)<2\,\mathcal{P}(k,R)$, then $\delta^{(k)}_{k+R-1}>0$. Its hypothesis follows from (2) and (1). Since $e^R\,e^{-R}=1$ and $k\,a_k\,e^R>0$,
$$k\,a_k\,\Lambda_R(k+1;k+R)=k\,a_k\,e^R\cdot e^{-R}\Lambda_R(k+1;k+R)\ <\ k\,a_k\,e^R\cdot\frac{2\cdot0.38385\;W_0\,\bigl(1+\frac{1}{10s}\bigr)}{s^3}$$
by (2), and the right side equals
$$2\,a_k\,e^R\cdot0.38385\,\Bigl(1+\frac{1}{10\,s}\Bigr)\,\frac{k}{s^3}\,W_0\ \le\ 2\,\mathcal{P}(k,R)$$
by (1). Hence $\delta^{(k)}_{k+R-1}>0$, which by Step 0 is the claim.
