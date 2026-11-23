---
weight: unit
short: crossing criterion in closed form
---
## Description

The crossing criterion with its five sums replaced by closed-form bounds: for $k\ge2$ and $2\le R\le k-1$, three explicit inequalities between elementary functions of $k$ and $R$ imply that $b(j,k)>b(j,k-1)$ in some row $j$ with $k<j\le k+R$.

## Statement

Let $k\ge2$ and $R$ be natural numbers with $2\le R\le k-1$, and put $N=k+R$. Let $\bar a=5/(2k)$ (`Parking.abar`), and let $\bar S$, $\bar{\mathsf E}$, $\bar H$, $\bar G$, $\underline t$, $\bar t$ be the closed forms `Parking.Sbar`, `Parking.Ebar`, `Parking.Hbar`, `Parking.Gbar`, `Parking.tlow`, `Parking.tup`, evaluated at $(k,R)$. Suppose that
$$\bar a\,R\le\frac{6679}{10000},\qquad\underline t\ge0,$$
and
$$\Bigl(\bar t+e^{-1}e^{\bar a}\,\frac{R+1}{N}\Bigr)\Bigl(\bar H+\frac5k\,\bar G\Bigr)<e^{-1}\Bigl(\frac{R(R+1)}{N}-1-\bar S-\bar{\mathsf E}\Bigr).$$
Then there is a natural number $j$ with $k<j\le N$ and $d_{j,k}>0$, where $d_{j,k}=b(j,k)-b(j,k-1)$ (`Parking.b`).

## Explanation

**What is gained.** The hypotheses of the crossing criterion `Parking.cross_criterion` are inequalities between finite sums whose number of terms grows with $R$: the kernel deficit $\bar\kappa_R$ (`Parking.kbar`), $S_R$ (`Parking.SR`), $\mathsf E$ (`Parking.ecorSum`), $\mathsf e_{N-1}$ (`Parking.ecor`) and $\Sigma_\omega$ (`Parking.Somg`). Here each of them is replaced by an expression in $k$, $R$, square roots, one exponential and two logarithms. This is what makes it possible to verify the criterion for all large $k$ at once, which `Parking.crossing_strip` does with $R$ of order $k^{2/3}$. The statement is for arbitrary $R$ in the given range; nothing in it refers to that choice.

**How the bounds are arranged.** Write the second hypothesis of the criterion as $\Theta\Psi<x\Lambda$ with
$$\Theta=\bar\kappa_R+\frac{x(R+1)}{N},\qquad\Psi=\mathsf e_{N-1}+\Sigma_\omega,\qquad\Lambda=\frac{R(R+1)}{N}-1-S_R-\mathsf E,$$
$x$ being the diagonal tilt (`Parking.xk`). The quantities on the smaller side, and those subtracted on the larger side, are bounded from above; the tilt on the larger side and the deficit in the first hypothesis are bounded from below:

| quantity | bound | source |
|---|---|---|
| $x$ | $e^{-1}\le x\le e^{-1}e^{\bar a}$ | Taylor polynomials of $\log(1+1/k)$ |
| $S_R$ | $\le\bar S$ | upper Stirling bound; $e^s\le1+s+0.633s^2$ |
| $\mathsf E$ | $\le\bar{\mathsf E}$ | $\log(x\gamma_i)\le\frac{5(i-k)}{2ki}$ and a recursion for $\mathsf e_j$ |
| $\Psi$ | $0\le\Psi\le\bar H+\frac5k\bar G$ | the same, summed against comparison functions |
| $\bar\kappa_R$ | $\underline t\le\bar\kappa_R\le\bar t$ | two-sided Stirling bound; $\sum_{m\ge1}e^{-m}\varepsilon_m=1-e^{-1}$ |

There are two analytic inputs. One is Stirling's formula with the sharp constant $c_0=1/\sqrt{2\pi}$ in both directions (`Parking.poissonMass_le_c0` and `Parking.poissonMass_ge_c0`; the lower bound rests on Robbins' bound `Parking.factorial_le_robbins`) together with the exact total mass of the kernel at the tilt $e^{-1}$ (`Parking.hasSum_eps`). The other is elementary: Taylor polynomials of the logarithm and of the exponential.

**Which bounds are tight.** For the smallest column of the application, $k=265$ with $R=70$, a floating-point evaluation of the definitions (not part of any proof) gives the following values.

| | true value | closed form |
|---|---|---|
| $S_R$ | $8.773$ | $\bar S=9.067$ |
| $\mathsf E$ | $0.183$ | $\bar{\mathsf E}=0.261$ |
| $\mathsf e_{N-1}+\Sigma_\omega$ | $14.67$ | $\bar H+\frac5k\bar G=15.04$ |
| $\bar\kappa_R$ | $0.00432$ | $\underline t=0.00282$, $\bar t=0.00840$ |
| the two sides of the main inequality | $1.218<1.812$ | $1.310<1.658$ |

The bounds for $S_R$ and for $\mathsf e_{N-1}+\Sigma_\omega$ lose about three percent; the bound for $\mathsf E$ is cruder, but $\mathsf E$ is small. The main inequality keeps a margin of about a fifth of its larger side. The kernel deficit is different in kind. It is the difference of a tail of size about $0.035$ and an excess of size about $0.031$, so an error of one part in twelve in the bound for either would make the lower bound $\underline t$ negative. Part (v) of the proof is therefore the part that leaves the least room. The tail has to be computed from the exact total mass with the sharp Stirling constant in both directions, and the excess has to be bounded to second order in $\bar a$, so that the total error stays small compared with $0.003$.

**The hypothesis $\bar aR\le0.6679$.** It is needed only for the quadratic bound $e^s\le1+s+0.633\,s^2$ on $0\le s\le0.6679$ (`Parking.exp_le_quad`), which is applied with $s\le\bar aR$. The research that produced the argument used the best constant $(e^{s_0}-1-s_0)/s_0^2$ for $s_0=\bar aR$ in place of $0.633$; the library fixes the number and adds the hypothesis. Likewise $\bar t$ contains $\frac14=\frac{3}{12}$ where the sharp constant would be $\zeta(3/2)/12$ (see `Parking.tup`).

**The Lean form.** The conclusion is `∃ j, k < j ∧ j ≤ k + R ∧ 0 < dq k j`, where `dq k j` $=d_{j,k}/j!$ (`Parking.dq`); by `Parking.dq_pos_iff` its positivity is the inequality $b(j,k-1)<b(j,k)$. The hypothesis $R\le k-1$ is written with the subtraction of natural numbers.

## Proof

**Notation.** $x$ is the diagonal tilt of the column $k$, $\alpha=1+\log x$ (so $x=e^{\alpha-1}$), $\gamma_i=(1+1/i)^{i-2}$ (`Parking.gam`), $\pi_n$ and $\Pi_i$ are the weights and their partial sums (`Parking.pix`, `Parking.pixSum`), $\mathsf e_j$ and $\omega_i$ are as in `Parking.ecor` and `Parking.omg`, $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`), $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), $q=633/1000$, $\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`), and
$$p_i=\frac{e^{-i}\,i^i}{i!}\ \ (\text{`Parking.poissonMass`};\ p_0=1),\qquad v_i=\frac{e^{-1}\,p_i}{i+1}\quad(i\ge0).$$
With $\bar\kappa_R$, $S_R$, $\mathsf E$, $\Sigma_\omega$ the quantities `Parking.kbar`, `Parking.SR`, `Parking.ecorSum`, `Parking.Somg` of the column $k$, the hypotheses of `Parking.cross_criterion` are $\bar\kappa_R\ge0$ and $\Theta\Psi<x\Lambda$, where
$$\Theta=\bar\kappa_R+\frac{x(R+1)}{N},\qquad\Psi=\mathsf e_{N-1}+\Sigma_\omega,\qquad\Lambda=\frac{R(R+1)}{N}-1-S_R-\mathsf E .$$

**Organisation.** Five parts bound the quantities of the criterion: (i) $e^{-1}\le x\le e^{-1}e^{\bar a}$; (ii) $S_R\le\bar S$; (iii) $\mathsf E\le\bar{\mathsf E}$; (iv) $0\le\Psi\le\bar H+\frac5k\bar G$; (v) $\underline t\le\bar\kappa_R\le\bar t$. A last part deduces the hypotheses of `Parking.cross_criterion` from them. Parts (i), (iii) and (iv) concern the tilt and use only Taylor polynomials of the logarithm; (ii) and (v) concern sums of the numbers $p_i$ and use Stirling's bounds. The estimates within each part are given in the order in which they are used.

**(i) The tilt.** As in the proof of `Parking.xk_bounds`: $\alpha=1-(k-2)\log(1+1/k)$, and the bounds $u-\frac{u^2}2\le\log(1+u)\le u-\frac{u^2}2+\frac{u^3}3$ at $u=1/k$ give
$$0\le\underline a\le\alpha\le\bar a,\qquad e^{-1}\le x\le e^{-1}e^{\bar a}.\tag{i}$$
For (iii) and (iv) one further fact about the tilt is needed: for $i\ge k$,
$$0\le\log(x\gamma_i)\le\frac{5\,(i-k)}{2\,k\,i}.\tag{L}$$
The lower bound is $x\gamma_i\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`). For the upper bound, $\log(x\gamma_i)=\log\gamma_i-\log\gamma_k$ is a telescoping sum of the differences $\log\gamma_{m+1}-\log\gamma_m$, $k\le m<i$, and each difference is at most $\frac{5}{2m(m+1)}=\frac52\bigl(\frac1m-\frac1{m+1}\bigr)$ for $m\ge2$. To see the latter, write $\log\gamma_{m+1}=(m-1)\log(1+\frac1{m+1})$ and $\log\gamma_m=(m-2)\log(1+\frac1m)$, bound the first from above by the Taylor polynomial of degree $3$ at $\frac1{m+1}$ and the second from below by the Taylor polynomial of degree $4$ at $\frac1m$ (`Parking.log_one_add_le3`, `Parking.log_one_add_ge4`). The resulting inequality between rational functions of $m$ holds because, with $t=m-2\ge0$,
$$\frac{5}{2m(m+1)}-\bigl[\text{difference of the two polynomials}\bigr]=\frac{29t^4+253t^3+823t^2+1191t+656}{12\,m^4(m+1)^3}\ge0 .$$
Verifying this identity is a routine calculation with rational functions.

**(ii) $S_R\le\bar S$.** Since $x=e^{\alpha-1}$, each term of $S_R$ is $(ix)^i/i!=p_i\,e^{\alpha i}$. For $0\le y\le R$ we have $\alpha y\le\bar a\,y$ by (i) and $0\le\bar a\,y\le\bar aR\le0.6679$, so the monotonicity of the exponential and `Parking.exp_le_quad` (which states $e^s\le1+s+0.633\,s^2$ for $0\le s\le0.6679$) give
$$e^{\alpha y}\le e^{\bar a y}\le1+\bar a\,y+q\,(\bar a\,y)^2\qquad(0\le y\le R).\tag{Q}$$
Hence $S_R\le\sum_{i<R}p_i+\bar a\sum_{i<R}i\,p_i+q\,\bar a^2\sum_{i<R}i^2p_i$. The upper Stirling bound $p_i\le c_0/\sqrt i$ for $i\ge1$ (`Parking.poissonMass_le_c0`) and three elementary sums (`Parking.sum_range_inv_sqrt_le`, `Parking.sum_range_sqrt_le`, `Parking.sum_range_sqrt_cube_le`) give
$$\sum_{i<R}p_i\le1+c_0\bigl(2\sqrt{R-1}-1\bigr),\qquad\sum_{i<R}i\,p_i\le\tfrac23\,c_0\,R\sqrt R,\qquad\sum_{i<R}i^2p_i\le\tfrac25\,c_0\,R^2\sqrt R,\tag{P}$$
and the sum of the three bounds is $\bar S$. These estimates are routine.

**(iii) $\mathsf E\le\bar{\mathsf E}$.** First, $\mathsf e_k=0$: by `Parking.CrossCrit.pix_succ` and $x\gamma_k=1$, $\pi_{k+1}=\pi_k$, so $\Pi_{k+1}/\pi_{k+1}=2$. Second, for $j\ge k$ and $r=x\gamma_{j+1}\ge1$,
$$\mathsf e_{j+1}=(j-k+2)\Bigl(1-\frac1r\Bigr)+\frac{\mathsf e_j}{r},$$
because $\Pi_{j+2}=\Pi_{j+1}+\pi_{j+2}$ and $\pi_{j+2}=r\,\pi_{j+1}$, so that $\Pi_{j+2}/\pi_{j+2}=1+\frac1r\,\Pi_{j+1}/\pi_{j+1}$. With $1-\frac1r\le\log r$, $\frac1r\le1$ and $\mathsf e_j\ge0$ (`Parking.CrossCrit.ecor_nonneg`),
$$\mathsf e_{j+1}\le(j-k+2)\,\log(x\gamma_{j+1})+\mathsf e_j .\tag{R}$$
Inserting (L) and inducting on $j$ gives $\mathsf e_j\le\frac{5}{6k^2}\,\rho(\rho+1)(\rho+2)$ with $\rho=j-k$: the induction step needs $\frac{5(\rho+1)(\rho+2)}{2k(j+1)}\le\frac{5(\rho+1)(\rho+2)}{2k^2}$, which holds since $j+1\ge k$. Finally $\frac{\mathsf e_j}{j+1}\le\frac{\mathsf e_j}{k}$ and $\sum_{\rho=0}^{R-2}\rho(\rho+1)(\rho+2)=\frac14(R-2)(R-1)R(R+1)$ give $\mathsf E\le\bar{\mathsf E}$. (The library proves the last summation by induction on the upper end.)

**(iv) $0\le\Psi\le\bar H+\frac5k\bar G$.** The lower bound is `Parking.CrossCrit.ecor_nonneg` and `Parking.CrossCrit.Somg_nonneg`. For the upper bound, two comparison functions of a real variable $n$ are used,
$$H(n)=(n-k)-k\log\frac{n+2}{k+2},\qquad G(n)=\frac{(n-k)(n-k+1)}{2}+\Bigl(\frac32-k\Bigr)(n-k)+k(k-1)\log\frac{n+1}{k+1},$$
which vanish at $n=k$ and satisfy $H(N-1)=\bar H$, $G(N-1)=\bar G$. Their increments dominate two families of summands: for $i>k$,
$$\frac{i-k+1}{i+1}\le H(i)-H(i-1),\qquad\frac{(i-k)(i-k+1)}{i}\le G(i)-G(i-1).$$
The first follows from $\log\frac{i+2}{i+1}\le\frac1{i+1}$. The second follows from $\log\frac{i+1}{i}\ge\frac1i-\frac1{2i^2}$ (`Parking.log_one_add_ge2`): the difference of the two sides is then at least $\frac{i^2-k(k-1)}{2i^2}\ge0$. Now combine. By (L) and the second increment bound,
$$(i-k+1)\,\log(x\gamma_i)\le\frac{5}{2k}\cdot\frac{(i-k)(i-k+1)}{i}\le\frac{5}{2k}\bigl(G(i)-G(i-1)\bigr)\qquad(i>k).$$
Summing (R) from $\mathsf e_k=0$ gives $\mathsf e_j\le\frac{5}{2k}G(j)$, in particular $\mathsf e_{N-1}\le\frac{5}{2k}\bar G$. For the flow factors, $\omega_i=\frac{1}{i+1}+\frac{i}{i+1}\bigl(1-\frac{1}{x\gamma_i}\bigr)\le\frac1{i+1}+\log(x\gamma_i)$ for $i\ge k$, so each term of $\Sigma_\omega$ satisfies $(i-k+1)\,\omega_i\le\bigl(H(i)-H(i-1)\bigr)+\frac{5}{2k}\bigl(G(i)-G(i-1)\bigr)$, and summing over $k<i\le N-1$ gives $\Sigma_\omega\le\bar H+\frac{5}{2k}\bar G$. Adding the two bounds gives (iv). All of this is routine once (L) is available.

**(v) $\underline t\le\bar\kappa_R\le\bar t$.** *Decomposition.* By `Parking.mul_eps`, $(i+1)\,\varepsilon_{i+1}=i^i/i!$, hence $e^{-(i+1)}\varepsilon_{i+1}=v_i$ and $\kappa_{i+1}=e^{\alpha(i+1)}v_i$. The sum of the kernel at the tilt $e^{-1}$ is known exactly: $\sum_{m\ge1}e^{-m}\varepsilon_m=1-e^{-1}$ (`Parking.hasSum_eps`), that is $\sum_{i\ge0}v_i=1-e^{-1}$. Therefore, with $\mathrm{Tail}_R=\sum_{i\ge R}v_i=(1-e^{-1})-\sum_{i<R}v_i$,
$$\bar\kappa_R=1-e^{-1}e^{\alpha}-\sum_{i<R}e^{\alpha(i+1)}v_i=\mathrm{Tail}_R-e^{-1}\bigl(e^{\alpha}-1\bigr)-\sum_{i<R}\bigl(e^{\alpha(i+1)}-1\bigr)\,v_i .$$
The deficit is a positive tail minus the excess of mass caused by $\alpha>0$.

*The tail.* For $y>0$, $\frac{1}{(y+1)\sqrt{y+1}}\le2\bigl(\frac1{\sqrt y}-\frac1{\sqrt{y+1}}\bigr)\le\frac{1}{y\sqrt y}$ (`Parking.inv_sqrt_diff_bounds`). For $i\ge2$, the upper Stirling bound gives $v_i\le e^{-1}c_0/(i\sqrt i)\le2e^{-1}c_0\bigl(\frac1{\sqrt{i-1}}-\frac1{\sqrt i}\bigr)$. For $i\ge R\ge1$, the lower Stirling bound $p_i\ge c_0(1-\frac1{12i})/\sqrt i$ (`Parking.poissonMass_ge_c0`), with $1-\frac1{12i}\ge1-\frac1{12R}$ and $\sqrt i\le\sqrt{i+1}$, gives $v_i\ge e^{-1}c_0(1-\frac1{12R})/((i+1)\sqrt{i+1})\ge2e^{-1}c_0(1-\frac1{12R})\bigl(\frac1{\sqrt{i+1}}-\frac1{\sqrt{i+2}}\bigr)$. Both bounds telescope over $R\le i<M$, and letting $M\to\infty$ in the partial sums of the convergent series $\sum v_i$ yields, for $R\ge2$,
$$\frac{2e^{-1}c_0\bigl(1-\frac{1}{12R}\bigr)}{\sqrt{R+1}}\le\mathrm{Tail}_R\le\frac{2e^{-1}c_0}{\sqrt{R-1}}.$$

*The lower bound $\underline t\le\bar\kappa_R$.* Here the excess is bounded from above. From $1-\alpha\le e^{-\alpha}$, $e^{\alpha}-1\le\alpha e^{\alpha}\le\bar a\,e^{\bar a}$. For $i<R$, (Q) with $y=i+1\le R$ gives $\bigl(e^{\alpha(i+1)}-1\bigr)v_i\le\bigl(\bar a(i+1)+q\bar a^2(i+1)^2\bigr)v_i=e^{-1}\bar a\,p_i+e^{-1}q\,\bar a^2(i+1)\,p_i$. By (P),
$$\sum_{i<R}p_i\le1+c_0\bigl(2\sqrt{R-1}-1\bigr),\qquad\sum_{i<R}(i+1)\,p_i\le1+c_0\Bigl(\tfrac23R\sqrt R+2\sqrt{R-1}-1\Bigr).$$
Subtracting these three bounds for the excess from the lower bound for the tail gives exactly $\underline t$.

*The upper bound $\bar\kappa_R\le\bar t$.* Here the excess is bounded from below, by its first-order part: $e^{\alpha}-1\ge\alpha$ and $e^{\alpha(i+1)}-1\ge\alpha(i+1)$, so the excess is at least $e^{-1}\alpha\,\bigl(1+\sum_{i<R}p_i\bigr)$. The lower Stirling bound, $\sum_{i=1}^{n}i^{-1/2}\ge2\sqrt{n+1}-2$ (`Parking.sum_range_inv_sqrt_ge`) and $\sum_{i=1}^{n}i^{-3/2}\le3$ (`Parking.sum_range_inv_sqrt_cube_le`) give $\sum_{i<R}p_i\ge1+c_0\bigl(2\sqrt R-2-\frac14\bigr)$. Since $\alpha\ge\underline a\ge0$ by (i), the excess is at least $e^{-1}\underline a\,\bigl[2+c_0(2\sqrt R-2-\frac14)\bigr]$, and subtracting this from the upper bound for the tail gives $\bar t$.

**Deduction of the hypotheses of the criterion.** By (v) and $\underline t\ge0$, $\bar\kappa_R\ge0$; this is the first hypothesis of `Parking.cross_criterion`. By (i) and (v),
$$0\le\Theta\le\bar\Theta:=\bar t+e^{-1}e^{\bar a}\,\frac{R+1}{N},$$
and by (iv), $0\le\Psi\le\bar\Psi:=\bar H+\frac5k\bar G$; hence $0\le\Theta\Psi\le\bar\Theta\,\bar\Psi$. Put $\bar\Lambda=\frac{R(R+1)}{N}-1-\bar S-\bar{\mathsf E}$. The third hypothesis says $\bar\Theta\bar\Psi<e^{-1}\bar\Lambda$, so $\bar\Lambda>0$. Then $e^{-1}\bar\Lambda\le x\,\bar\Lambda$ by (i), and $\bar\Lambda\le\Lambda$ by (ii) and (iii). Altogether
$$\Theta\,\Psi\le\bar\Theta\,\bar\Psi<e^{-1}\bar\Lambda\le x\,\bar\Lambda\le x\,\Lambda,$$
which is the second hypothesis of `Parking.cross_criterion`. Since $1\le R\le k-1$, that theorem gives a row $j$ with $k<j\le N$ and $d_{j,k}>0$. The positivity of $\bar\Lambda$, which is needed to replace $e^{-1}$ by the larger $x$, is not assumed; it follows from the hypothesis because its smaller side is nonnegative.
