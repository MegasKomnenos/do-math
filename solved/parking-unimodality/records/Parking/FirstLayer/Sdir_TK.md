---
weight: unit
short: property K of the direct term
---
## Description

For $k\ge 7$ and $1\le\rho\le k-2$, the values $S_\rho(k-1)$, $S_\rho(k)$, $S_\rho(k+1)$ of the direct term of the first-layer recursion at the critical tilt $x_k$ form a triple with property K at $k$.

## Statement

Let $k\ge 7$ and $\rho$ be natural numbers with $1\le\rho\le k-2$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $\omega_n=c_nx_k^{\,n}$ with $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT`), $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ (`Parking.FirstLayer.pairT`) and
$$S_\rho(c)=x_k\,\omega_{\rho-1}\,\omega_c+\frac{x_k}{2}\cdot\frac{c+\rho+1}{c+\rho}\cdot Q_\rho(c-\rho-1)$$
(`Parking.FirstLayer.Sdir`). Then $\big(S_\rho(k-1),S_\rho(k),S_\rho(k+1)\big)$ has property K at $k$ (`Parking.FirstLayer.TK`): for every $\mu\ge 0$,
$$2e^{\mu/k}S_\rho(k)\le e^{\mu}S_\rho(k+1)+e^{-\mu}S_\rho(k-1).$$

The Lean statement names the number $n=k-\rho-2$ and assumes $\rho+n+2=k$.

## Explanation

**What it is for.** $S_\rho(c)$ is the part of the tilted mass of the size $c+\rho$ and threshold $c$ that comes from two free pieces. In the induction of `Parking.FirstLayer.kernel_TK` it is the term that is not covered by the induction hypothesis, so its property K has to be proved directly. All three thresholds are taken at the same tilt $x_k$.

**Where the difficulty is.** Both ingredients of $S_\rho$ have property K by themselves: the triple $(\omega_{k-1},\omega_k,\omega_{k+1})$ (`Parking.FirstLayer.TK_ccT_top`) and the triple of pair sums $q_-=Q_\rho(k-\rho-2)$, $q_0=Q_\rho(k-\rho-1)$, $q_+=Q_\rho(k-\rho)$ (`Parking.FirstLayer.pairT_TK`). But the pair sums are multiplied by $\nu(c)=\frac{c+\rho+1}{c+\rho}$, which *decreases* in $c$, and property K is closed only under factors that do not decrease (`Parking.FirstLayer.TK.mul_ratio`). A decreasing factor moves the tilt downward (`Parking.FirstLayer.TK.shift`), and at tilts near $0$ there is nothing below to move to. So the pair-sum term $\nu q$ can fail property K, and the amount by which it fails, its *defect*, has to be paid by the *surplus* with which the first term $x_k\omega_{\rho-1}\omega_c$ satisfies it. The surplus exists because at the top $\omega_{k+1}>\omega_k=\omega_{k-1}$ (`Parking.FirstLayer.ccT_tilt_top`, `Parking.FirstLayer.ccT_tilt_top'`).

**How it is done.** Write $N=k+\rho$; then $\nu_-=\frac{N}{N-1}$, $\nu_0=\frac{N+1}{N}$, $\nu_+=\frac{N+2}{N+1}$ are the values of $\nu$ at $k-1,k,k+1$. The tilts are divided at $\mu_0=\frac{1}{k(k+2)}$. For $\mu\ge\mu_0$ the downward shift caused by $\nu$, which is at most $\mu_0$, stays within the nonnegative tilts, and the shift identity leaves a defect of second order in $1/N$. For $\mu\le\mu_0$ the shift is not available; instead the defect is bounded by $(\nu_0-\nu_+)$ times the tilted difference of the outer pair sums, which for such small tilts is at most its two end terms (`Parking.FirstLayer.pairT_D_le`). In both ranges the surplus is at least $\omega_k\,\delta$ and the defect at most $2\omega_\rho\omega_k\,\delta$ for one and the same $\delta$, and since the pair-sum term carries $x_k/2$ and the first term carries $x_k\omega_{\rho-1}$, what remains is $x_k\omega_k\delta\,(\omega_{\rho-1}-\omega_\rho)\ge 0$: the Cayley masses decrease from the index $\rho-1$ to $\rho$.

**The hypothesis $k\ge 7$.** It is used only in the two numerical comparisons of surplus and defect. In the range of large tilts the comparison reduces to $\frac{1}{4(k+1)}\le\frac{k^2-2k-1}{2k(k+1)(k+2)}$, that is, to $k^2-6k-2\ge 0$, which holds from $k=7$ on and fails for $k=6$.

## Proof

Fix $\mu\ge 0$ and write $A=e^{\mu}$, $B=e^{-\mu}$, $C=e^{\mu/k}$. Since $\omega_{k-1}=\omega_k$ (`Parking.FirstLayer.ccT_top`), the three values are
$$S_\rho(k-1)=x_k\omega_{\rho-1}\omega_k+\tfrac{x_k}{2}\nu_-q_-,\quad S_\rho(k)=x_k\omega_{\rho-1}\omega_k+\tfrac{x_k}{2}\nu_0q_0,\quad S_\rho(k+1)=x_k\omega_{\rho-1}\omega_{k+1}+\tfrac{x_k}{2}\nu_+q_+ .$$
Put
$$\mathrm{Sur}=A\,\omega_{k+1}+B\,\omega_k-2C\,\omega_k,\qquad \mathrm{Def}=A\,\nu_+q_++B\,\nu_-q_--2C\,\nu_0q_0 ,$$
so that $A\,S_\rho(k+1)+B\,S_\rho(k-1)-2C\,S_\rho(k)=x_k\,\omega_{\rho-1}\,\mathrm{Sur}+\frac{x_k}{2}\,\mathrm{Def}$.

**Combination.** Suppose that for some $\delta\ge 0$ both $\mathrm{Sur}\ge\omega_k\delta$ and $\mathrm{Def}\ge-2\,\omega_\rho\,\omega_k\,\delta$. Then $x_k\omega_{\rho-1}\mathrm{Sur}+\frac{x_k}{2}\mathrm{Def}\ge x_k\,\omega_k\,\delta\,(\omega_{\rho-1}-\omega_\rho)\ge 0$, because $\omega_\rho\le\omega_{\rho-1}$ (`Parking.ccT_succ_le`, as $\rho\le k$) and $x_k,\omega_k>0$. It remains to produce $\delta$ in each range of $\mu$. Throughout, $N\ge k+1$, the $q$'s are nonnegative (`Parking.FirstLayer.pairT_nonneg`), and property K of the pair sums is $2Cq_0\le Aq_++Bq_-$ (`Parking.FirstLayer.pairT_TK`).

**Small tilts, $\mu\le\frac{1}{k(k+2)}$.** Here $\delta=\dfrac{e^{\mu}}{N(N+1)}$.

*Defect.* Put $d=\nu_0-\nu_+=\frac{1}{N(N+1)}$; then $\nu_--\nu_0=\frac{1}{N(N-1)}\ge d$. Write
$$\mathrm{Def}=\nu_0\,(Aq_++Bq_--2Cq_0)+(\nu_+-\nu_0)\,Aq_++(\nu_--\nu_0)\,Bq_- .$$
The first term is nonnegative by property K of the pair sums; the second is $-d\,Aq_+$; the third is at least $d\,Bq_-$. Hence $\mathrm{Def}\ge-d\,(Aq_+-Bq_-)$, and `Parking.FirstLayer.pairT_D_le` gives $Aq_+-Bq_-\le 2e^{\mu}\omega_\rho\omega_k$. So $\mathrm{Def}\ge-2\omega_\rho\omega_k\,\delta$.

*Surplus.* `Parking.FirstLayer.ccT_tilt_top'` gives $\mathrm{Sur}\ge\omega_k\big(\frac{3}{2(k+1)(k+2)}-2(e^{\mu/k}-1)\big)$, and the bracket is at least $\delta$ by the following numerical comparison: for real $k\ge 7$, $N\ge k+1$ and $0\le\mu\le\frac{1}{k(k+2)}$,
$$\frac{e^{\mu}}{N(N+1)}\le\frac{3}{2(k+1)(k+2)}-2\big(e^{\mu/k}-1\big).$$
With $U=\frac{1}{(k+1)(k+2)}$: $\mu\le\frac1{63}$ gives $e^{\mu}\le\frac{63}{62}$, and $\frac{1}{N(N+1)}\le U$, so the left side is at most $\frac{63}{62}U$; $\mu/k\le\frac{1}{k^2(k+2)}\le\frac1{441}$ gives $e^{\mu/k}-1\le\frac{441}{440}\cdot\frac{\mu}{k}$, and $\frac{1}{k^2(k+2)}\le\frac{8}{49}U$ for $k\ge 7$, so the right side is at least $\big(\frac32-2\cdot\frac{441}{440}\cdot\frac{8}{49}\big)U>\frac{63}{62}U$. These steps are routine.

**Large tilts, $\mu\ge\frac{1}{k(k+2)}$.** Here $\delta=e^{\mu/k}\cdot\nu_0\cdot(2k-N)\cdot e_N$ with $e_N=\dfrac{N-k+1}{N^2(N+2)\,k}$.

*Defect.* Let $L=\log(\nu_+/\nu_0)$ and $M=\log(\nu_-/\nu_0)$. From $\log r\ge 1-\frac1r$ and $\log r\le r-1$ one gets
$$L\ge-\frac{1}{N(N+2)},\qquad \frac{1}{N^2}\le M\le\frac{1}{(N-1)(N+1)} .$$
Hence $\frac{M-L}{2}\le\frac{1}{(N-1)(N+1)}\le\frac{1}{k(k+2)}\le\mu$, so $\mu+\frac{L-M}{2}\ge 0$ and `Parking.FirstLayer.TK.shift` applies to the triple of pair sums:
$$2C\,E\,q_0\le A\,\frac{\nu_+}{\nu_0}q_++B\,\frac{\nu_-}{\nu_0}q_-,\qquad E=\exp\!\Big(\frac{(k+1)L+(k-1)M}{2k}\Big).$$
The bounds on $L$ and $M$ give $(k+1)L+(k-1)M\ge-\frac{k+1}{N(N+2)}+\frac{k-1}{N^2}=-\frac{2(N-k+1)}{N^2(N+2)}$, so $E\ge 1-e_N$ by $e^{t}\ge 1+t$. Multiplying the shifted inequality by $\nu_0$: $\mathrm{Def}\ge 2C\nu_0q_0(E-1)\ge-2C\,\nu_0\,e_N\,q_0$. Finally $q_0=Q_\rho(k-\rho-1)\le(k-\rho)\,\omega_\rho\omega_k=(2k-N)\,\omega_\rho\omega_k$ (`Parking.FirstLayer.pairT_mid_le`). So $\mathrm{Def}\ge-2\omega_\rho\omega_k\,\delta$.

*Surplus.* `Parking.FirstLayer.ccT_tilt_top` gives $\mathrm{Sur}\ge\omega_k\,e^{\mu/k}\cdot\frac1k\cdot\frac{k^2-2k-1}{2k(k+1)(k+2)}$, and this is at least $\omega_k\delta$ by the numerical comparison: for real $k\ge 7$ and $N\ge k+1$,
$$\frac{N+1}{N}\,(2k-N)\,\frac{N-k+1}{N^2(N+2)}\le\frac{k^2-2k-1}{2k(k+1)(k+2)} .$$
The left side is $\frac{(N+1)(2k-N)(N-k+1)}{N^3(N+2)}$. By the inequality between the arithmetic and the geometric mean, $4(2k-N)(N-k+1)\le(k+1)^2$; and $(N+1)(k+1)^3\le(N+2)N^3$ since $N\ge k+1$. So the left side is at most $\frac{1}{4(k+1)}$, and $\frac{1}{4(k+1)}\le\frac{k^2-2k-1}{2k(k+1)(k+2)}$ is equivalent to $k^2-6k-2\ge 0$.

In both ranges $\delta\ge 0$ (for the large tilts because $N\le 2k-2$ and $N\ge k+1$), and the combination step concludes.
