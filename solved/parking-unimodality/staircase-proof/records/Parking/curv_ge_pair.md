---
weight: unit
short: the curvature term dominates the pair sum
---
## Description

For natural numbers $k$ and $R$ with $R \le k-2$, and $n = k+R-1$: $2\,\mathcal{P}(k,R) \le k^2\,\bigl(K(k+1) - 2K(k) + K(k-1)\bigr)$, where $\mathcal{P}(k,R)$ is the pair sum and $K = K_{n,k-1}$ is the frozen polynomial of the position $(n,k-1)$. For $R \ge 1$ the right side is $k^2$ times the curvature term of the step of column $k$ in the row $n$.

## Statement

Let $k$ and $R$ be natural numbers with $R \le k - 2$; that is, either $R = 0$, or $R \ge 1$ and $k \ge R + 2$. Put $n = k + R - 1$. Let $K(y) = K_{n,k-1}(y)$ be the frozen polynomial of `Parking.Kpoly` for the column $k - 1$ and the row $n$, and let $\mathcal{P}(k,R)$ be the pair sum of `Parking.pairSum`. Then

$$2\,\mathcal{P}(k,R) \;\le\; k^2\,\bigl(K(k+1) - 2\,K(k) + K(k-1)\bigr).$$

For $R = 0$ both sides are $0$, for every $k$.

## Explanation

**What is compared.** For $1 \le R \le k - 2$ the rows $n = k + R - 1$ are the rows $k \le n \le 2k - 3$, the first layer of the column $k - 1$; all of them but the row $n = k$ lie in the first layer of the column $k$ as well. In these rows, by `Parking.dq_frozen`, applied to the column $k - 1$, the normalised step of column $k$ in the row $n$ is the second difference $K(k+1) - 2K(k) + K(k-1)$, the curvature term, minus a boundary term. The statement bounds the curvature term from below by a quantity in which the frozen polynomial no longer occurs. Together with the formula for the step it gives the criterion `Parking.dq_pos_of_pair`, and that is its only use.

**Why the pair sum appears.** Put $N = k + R$. By its definition the frozen polynomial is

$$K(y) = \kappa_{k-1}(N) + \sum_{m=1}^{R} \frac{\kappa_{k-1}(N-m)}{N-m}\; y\,\Lambda_m(y;N),$$

where $\kappa_{k-1}(t) = a_t - \sum_{k-1<i<t} a_i\, a_{t-i}$ with $a_p = p^{p-1}/p!$ (`Parking.kap`), and $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the cut factors $y/(N-s)$ (`Parking.Lam`, `Parking.thr`). Every cut point contributes one factor $y$, so $y\,\Lambda_m(y;N) = \sum_q V_q\, y^q$, where $V_q \ge 0$ is the weight of the compositions of $m$ with $q$ parts for the cut factors $1/(N-s)$. This is a polynomial in $y$ with nonnegative coefficients, in which the compositions of $m$ with $q$ parts contribute to the coefficient of $y^q$. For a power $y^q$, $k^2$ times the second difference at $y = k$ is at least $q(q-1)\,k^q$. The factor $q(q-1)$ is twice the number of ways to mark one or two of the $q - 1$ cut points of a composition with $q$ parts (`Parking.sum_qq_Vc`). This bounds $k^2$ times the curvature term from below by twice a sum over $m$ of the weights of the compositions of $m$ with one or two marked cut points.

The pair sum is a sum of a different shape: it is organised by the lower of two marked points, and what lies below that point is collected in the environment $z^{(k)}_n = A(n,k-1)/n!$ of the threshold $k$ (`Parking.zr`). The two sums are equal, and the proof shows this without expanding either of them. In the rows concerned the environment satisfies a Volterra equation with the kernel $a_{m-b}$ that expresses its value at a point by its values at larger points; the marked compositions satisfy the adjoint equation, which expresses the value at a point by the values at smaller points (`Parking.Lam2_last`). Pairing the two equations identifies the two sums. The record of `Parking.pairSum` describes what the two sums count.

**What is lost.** The one inequality of the proof is $q(q-1)\,k^q \le k^2\bigl((k+1)^q - 2k^q + (k-1)^q\bigr)$, applied to each power. By the binomial theorem the right side is $2\sum_{i \ge 1} \binom{q}{2i} k^{q-2i+2}$. Its first term is the left side, and the second term is smaller than the first by the factor $(q-2)(q-3)/(12k^2)$. Here $q$ is at most $R \le k - 2$. Near the curve, where the statement is applied, the number of parts of a typical composition of $m \le R$ is of the order $\sqrt{R}$, while $k$ is of the order $R^{3/2}$; so the statement loses little there.

**The hypotheses.** For $R \ge 1$ the condition $R \le k - 2$ places the row $n$ in the range $n \le 2k - 3$. It is used twice: the numbers $\kappa_{k-1}(N-m)$ are positive for $N - m \le 2k - 1$ (`Parking.kap_pos`), and the environment $z^{(k)}_{n'}$ satisfies its Volterra equation with the kernel deficit $\kappa_{k-1}$ for $n' \le 2k - 1$. For $R = 0$ the pair sum and the sum that expresses the second difference of $K$ are both empty, so both sides are $0$, whatever $k$ is. The statement has no separate hypothesis on $k$: for $R \ge 1$ the condition $R \le k - 2$ gives $k \ge 3$, and of this the proof uses $k \ge 1$, which makes the subtraction $k - 1$ exact and gives $k > 0$ for Step 2.

**The Lean form.** The hypothesis is `R ≤ k - 2` with the subtraction of natural numbers, which is $0$ for $k \le 2$; it therefore admits $R = 0$ for every $k$, and $R \ge 1$ only for $k \ge R + 2$. The right side is written with `Kpoly (k - 1) (k + R - 1)` at the real arguments `(k : ℝ) + 1`, `k` and `(k : ℝ) - 1`. For $R \ge 1$ the subtractions $k - 1$, $k + R - 1$ and $k - 2$ of natural numbers are exact, because $k \ge 3$. For $R = 0$ and $k = 0$ the truncated subtractions give the column $0$ and the row $0$; the inequality reads $0 \le 0$ there as for every other $k$.

## Proof

Throughout, $N = k + R$, $a_p = p^{p-1}/p!$ (`Parking.cay`), $\kappa(t) = \kappa_{k-1}(t) = a_t - \sum_{k-1<i<t} a_i\, a_{t-i}$ (`Parking.kap`), $\lambda(s) = k/(N-s)$ is the threshold profile with $y = k$ (`Parking.thr`), $\Lambda_m(y) = \Lambda_m(y;N)$ is the chain sum for the profile $s \mapsto y/(N-s)$ (`Parking.Lam`), and $\Lambda^{(1)}_m$, $\Lambda^{(2)}_m$ are the weights of the compositions of $m$ with one and with two marked cut points for the profile $\lambda$ (`Parking.Lam1`, `Parking.Lam2`). The proof has five steps: the second difference of $K$ as a sum over $m$; an inequality for the second difference of a power; its consequence for one term of the sum; the identification of the pair sum; the conclusion. The sums over $1 \le m \le R$ and over $1 \le b \le R$ that occur are empty for $R = 0$, and then both sides of the statement are $0$. Where a term of such a sum is considered, $R \ge 1$, and therefore $k \ge R + 2 \ge 3$.

**Step 1: the second difference of the frozen polynomial.** By `Parking.Kpoly_second_diff`, for the column $k - 1$, the row $n$ and the threshold $k$, with $n + 1 = N$ and $n - (k-1) = R$,

$$K(k+1) - 2K(k) + K(k-1) = \sum_{m=1}^{R} \frac{\kappa(N-m)}{N-m}\; \mathsf C_m, \qquad \mathsf C_m = (k+1)\Lambda_m(k+1) - 2k\,\Lambda_m(k) + (k-1)\Lambda_m(k-1),$$

where $\mathsf C_m = \mathsf C_m(k;N)$ is the curvature sum (`Parking.curvSum`): the frozen polynomial is $K(y) = \kappa(N) + \sum_{m=1}^{R} \frac{\kappa(N-m)}{N-m}\, y\,\Lambda_m(y)$, its constant term cancels in the second difference, and the term $m$ contributes its coefficient times the second difference of $y\,\Lambda_m(y)$.

**Step 2: the second difference of a power.** For a real number $k > 0$ and every natural number $q$,

$$q(q-1)\,k^q \le k^2\,\Delta_q \qquad\text{and}\qquad 2q\,k^q \le k\,E_q,$$

where $\Delta_q = (k+1)^q - 2k^q + (k-1)^q$ and $E_q = (k+1)^q - (k-1)^q$. The two inequalities are proved together by induction on $q$. For $q = 0$ both read $0 \le 0$. For the step, multiplying out gives the recursions $\Delta_{q+1} = k\,\Delta_q + E_q$ and $E_{q+1} = k\,E_q + \Delta_q + 2k^q$. The first recursion and the two induction hypotheses give

$$k^2\,\Delta_{q+1} = k\cdot k^2\Delta_q + k\cdot k E_q \;\ge\; q(q-1)\,k^{q+1} + 2q\,k^{q+1} = (q+1)\,q\,k^{q+1}.$$

The first induction hypothesis also shows $\Delta_q \ge 0$, since $q(q-1) \ge 0$. With this, the second recursion gives

$$k\,E_{q+1} = k\cdot k E_q + k\,\Delta_q + 2k^{q+1} \;\ge\; 2q\,k^{q+1} + 2k^{q+1} = 2(q+1)\,k^{q+1}.$$

**Step 3: one term of the sum.** For $1 \le m \le R$,

$$k\,\bigl(2\Lambda^{(1)}_m + 2\Lambda^{(2)}_m\bigr) \;\le\; k^2\, \mathsf C_m .$$

Let $V_q = V_q(m;\lambda^{1,N})$ be the weight of the compositions of $m$ with $q$ parts for the profile $s \mapsto 1/(N-s)$ (`Parking.Vc`). These numbers are nonnegative by `Parking.Vc_nonneg`, because the profile is nonnegative at the cut points $s < m \le N$ (`Parking.thr_nonneg`). By `Parking.curvSum_eq_sum`, the expansion of the curvature sum by the number of parts, $\mathsf C_m = \sum_{q=1}^{m} V_q\, \Delta_q$: every cut point contributes one factor $y$, so $y\,\Lambda_m(y) = \sum_{q=1}^{m} V_q\, y^q$, and the second difference is taken power by power. On the other side, `Parking.sum_qq_Vc` gives $2\Lambda^{(1)}_m + 2\Lambda^{(2)}_m = \sum_{q=1}^{m} q(q-1)\, V_q(m;\lambda)$, and $V_q(m;\lambda) = k^{q-1} V_q$ by `Parking.Vc_thr`, so the left side of the claim is $\sum_{q=1}^{m} q(q-1)\,k^q\, V_q$. The claim follows from the first inequality of Step 2, term by term, since $V_q \ge 0$; Step 2 applies because $k \ge 3$ when the sum over $m$ has a term.

**Step 4: the pair sum as a sum over the last point.** We show

$$\mathcal{P}(k,R) = \sum_{m=1}^{R} \kappa(N-m)\;\lambda(m)\;\bigl(\Lambda^{(1)}_m + \Lambda^{(2)}_m\bigr). \tag{1}$$

*The equation of the environment.* For $R = 0$ both sides of (1) are empty sums; let $R \ge 1$, so that $k \ge 3$. Let $z^{(k)}_{n'} = A(n',k-1)/n'!$ (`Parking.zr`). For every natural number $n' \le 2k - 1$,

$$z^{(k)}_{n'} = \kappa(n'+1) + \sum_{k-1<t<n'+1} a_{n'+1-t}\;\frac{k}{t}\; z^{(k)}_{t-1}. \tag{2}$$

Indeed, by `Parking.zr_isWSol` the sequence $z^{(k)}$ solves the weighted last-car recursion with the weight $\omega(t) = \min(t,k)$, which equals $t$ for $1 \le t \le k - 1$. The single-chain formula `Parking.IsWSol.fwd` with the parameter $k - 1$ therefore gives, for $n' \le 2(k-1) + 1$ and with $c_m = a_{m+1}$,

$$c_{n'} - z^{(k)}_{n'} = \sum_{t=k}^{n'} c_{n'-t}\Bigl(c_{t-1} - \frac{\omega(t)}{t}\, z^{(k)}_{t-1}\Bigr),$$

and $\omega(t) = k$ for $t \ge k$. Writing $c_{n'} = a_{n'+1}$, $c_{n'-t} = a_{n'+1-t}$, $c_{t-1} = a_t$ and collecting the terms without $z$ into $\kappa(n'+1)$ gives (2). (In the Lean source this equation is a private lemma of the module of the frozen polynomial.)

Now put $Z(b) = z^{(k)}_{N-b-1}$ for $1 \le b \le R$. Since $N - b - 1 \le 2k - 4$, equation (2) applies with $n' = N - b - 1$. Substituting $t = N - m$, the range $k - 1 < t < N - b$ becomes $b < m \le R$, the kernel becomes $a_{N-b-t} = a_{m-b}$, the weight becomes $k/t = \lambda(m)$, and $z^{(k)}_{t-1} = Z(m)$. Hence

$$Z(b) = \kappa(N-b) + \sum_{b<m\le R} a_{m-b}\;\lambda(m)\; Z(m) \qquad (1 \le b \le R). \tag{3}$$

*The adjoint equation.* Put $G(m) = \Lambda^{(1)}_m + \Lambda^{(2)}_m$. By `Parking.Lam2_last`, $\Lambda^{(2)}_m = \sum_{0<s<m} \bigl(\Lambda^{(1)}_s + \Lambda^{(2)}_s\bigr)\lambda(s)\, a_{m-s}$, that is,

$$G(m) = \Lambda^{(1)}_m + \sum_{0<s<m} a_{m-s}\;\lambda(s)\; G(s). \tag{4}$$

*The duality.* Equation (3) expresses $Z$ at $b$ by the values of $Z$ at larger arguments, equation (4) expresses $G$ at $m$ by the values of $G$ at smaller arguments, and both have the kernel $a_{m-s}\,\lambda$. Solve (3) for $\kappa(N-s)$, multiply by $\lambda(s)\, G(s)$ and sum over $1 \le s \le R$:

$$\sum_{s=1}^{R} \kappa(N-s)\,\lambda(s)\,G(s) = \sum_{s=1}^{R} Z(s)\,\lambda(s)\,G(s) - \sum_{1 \le s < m \le R} \lambda(m)\,Z(m)\; a_{m-s}\,\lambda(s)\,G(s).$$

In the double sum, sum first over $s$ for a fixed $m$; by (4) the inner sum $\sum_{0<s<m} a_{m-s}\,\lambda(s)\,G(s)$ equals $G(m) - \Lambda^{(1)}_m$. The right side becomes

$$\sum_{m=1}^{R} Z(m)\,\lambda(m)\,G(m) - \sum_{m=1}^{R} \lambda(m)\,Z(m)\,\bigl(G(m) - \Lambda^{(1)}_m\bigr) = \sum_{m=1}^{R} \Lambda^{(1)}_m\;\lambda(m)\;Z(m),$$

which is $\mathcal{P}(k,R)$ by the definition of `Parking.pairSum`. This proves (1). The computation uses nothing about $Z$, $G$, $\kappa$, $\Lambda^{(1)}$ and $\lambda$ beyond the two equations (3) and (4).

**Step 5: conclusion.** For $1 \le m \le R$ we have $1 \le N - m \le 2k - 3$, so $\kappa(N-m) > 0$ by `Parking.kap_pos`, and $N - m > 0$. Multiplying the inequality of Step 3 by the nonnegative number $\kappa(N-m)/(N-m)$ and summing over $m$, Step 1 gives

$$k^2\,\bigl(K(k+1) - 2K(k) + K(k-1)\bigr) \;\ge\; \sum_{m=1}^{R} \frac{\kappa(N-m)}{N-m}\; k\,\bigl(2\Lambda^{(1)}_m + 2\Lambda^{(2)}_m\bigr) = 2\sum_{m=1}^{R} \kappa(N-m)\;\lambda(m)\;\bigl(\Lambda^{(1)}_m + \Lambda^{(2)}_m\bigr),$$

because $k/(N-m) = \lambda(m)$. By (1) the right side is $2\,\mathcal{P}(k,R)$.
