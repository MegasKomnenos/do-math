---
weight: unit
short: order of the kernel weights on the rows from the crossing on
---
## Description

For a column $k\ge 2$, a row $q$ with $k+1\le q\le k+\frac{27}{100}k$, a row $n\ge 2k$ and every $j$ with $q\le j\le n-1$: $\kappa_{n-q+1}\,\Psi'(j)\le\kappa_{n-j}\,(2k-1)$, where $\kappa$ is the prime kernel of the threshold $k$ at the critical tilt and $\Psi'(j)=\max(j,2k-1)$.

## Statement

Let $k\ge 2$, $q$, $n$, $j$ be natural numbers with $k+1\le q$, $100\,(q-k)\le 27\,k$, $n\ge 2k$ and $q\le j\le n-1$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`), and $\Psi'(j)=\max(j,2k-1)$ (`Parking.PsiW`). Then
$$\kappa_{n-q+1}\,\Psi'(j)\ \le\ \kappa_{n-j}\,(2k-1).$$

## Explanation

With $L=n-q+1$ and $\theta=\kappa_L/(2k-1)$ the statement is $\kappa_{n-j}/\Psi'(j)\ge\theta$ on the rows from $q$ to $n-1$; `Parking.order_neg` is the reverse inequality on the rows before $q$, and that record says how the pair is used in the proof of `Parking.step_pos_large`.

Here the weight is not constant. For $j\le 2k-1$ it is, and the inequality is again the monotonicity of the kernel, since $n-j<L$. For $j\ge 2k$ the weight is $j$, and the claim is that, as $j$ increases and the kernel index $l=n-j$ decreases, the kernel grows at least in proportion to $j$. Whether it does depends on where the two indices $l$ and $L$ lie relative to the free range $1\le m\le k$ of the kernel, and the proof has a case for each position:

- both beyond the free range: there the kernel decays at least by the factor $\frac{2k-2}{2k-1}$ per step, and this covers the growth $\frac{j+1}{j}$ of the weight precisely when $j\ge 2k-2$; so the argument allows a weight that grows like $j$ from the row $2k-1$ on and no earlier;
- both in the free range: the two indices are at least $0.73k$ apart, and across such a gap the free kernel drops by a factor of at least $1.22$, while $j\le 1.22\,(2k-1)$;
- $l$ in the free range and $L$ beyond it: $\kappa_L$ is compared with $\kappa_k$ by `Parking.kap_K3a` and $\kappa_k$ with $\kappa_l$ by the drop or by monotonicity.

The hypothesis $q\le k+\frac{27}{100}k$ gives the gap $0.73k$; no lower bound on $k$ beyond $k\ge 2$ is needed.

## Proof

Throughout, $\kappa_m\ge 0$ (`Parking.kqT_nonneg`) and $\kappa$ does not increase on the indices $m\ge 1$ (`Parking.kqT_succ_le` with `Parking.epsT_succ_le`, as in the record of `Parking.order_neg`). Note $q\le 1.27k$, hence $q\le 2k$ and $q\le n$. Put $L=n-q+1$ and $l=n-j$; then $1\le l<L$.

**Case $j\le 2k-1$.** $\Psi'(j)=2k-1$ (`Parking.PsiW_low`) and $\kappa_L\le\kappa_l$ by monotonicity.

**Case $j\ge 2k$.** $\Psi'(j)=j$ (`Parking.PsiW_of_ge`), and the claim is $\kappa_L\,j\le(2k-1)\,\kappa_l$. Three auxiliary facts are needed.

*(a) Decay by a fixed factor beyond the free range:* $(2k-1)\,\kappa_{m+1}\le(2k-2)\,\kappa_m$ for $m\ge k$. Write $m-k=(k-1)d+r$ with $0\le r<k-1$. The record of `Parking.kap_K3b` shows $(m+1)\kappa_{m+1}\le(m+1-j')\kappa_m$ whenever $m\ge k+(j'-1)(k-1)$; with $j'=d+1$ this is $(m+1)\kappa_{m+1}\le(m-d)\kappa_m$. Since $m+1\le k+(k-1)d+(k-1)\le(d+1)(2k-1)$, one has $(2k-1)(m-d)\le(2k-2)(m+1)$, and the claim follows.

*(b) The ratio $\kappa_{n-j}/j$ beyond the free range:* for $j\ge 2k-1$ with $n-j\ge k$, $\;j\,\kappa_{n-(2k-1)}\le(2k-1)\,\kappa_{n-j}$. Induction on $j$ from $2k-1$: if it holds for $j$ and $n-(j+1)\ge k$, then by (a) with $m=n-j-1$, $(2k-1)\kappa_{n-j}\le(2k-2)\kappa_{n-j-1}$, so $j\,\kappa_{n-(2k-1)}\le(2k-2)\,\kappa_{n-j-1}$. Multiplying by $\frac{j+1}{j}$ and using $(2k-2)(j+1)\le(2k-1)\,j$, which holds because $j\ge 2k-2$, gives $(j+1)\,\kappa_{n-(2k-1)}\le(2k-1)\,\kappa_{n-(j+1)}$.

*(c) The drop in the free range:* if $1\le l_1<l_2\le k$ and $100\,(l_2-l_1)\ge 73\,k$, then $1.22\,\kappa_{l_2}\le\kappa_{l_1}$. If $l_1=1$: in the free range $\kappa_m=\varepsilon_mx_k^{\,m}$ with $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.kqT_eq_epsT`), so $\kappa_1=x_k$ and $\kappa_2=x_k^2/2$ (`Parking.epsT_one`, `Parking.epsT_two`), and $\kappa_{l_2}\le\kappa_2\le x_k/2$ since $x_k\le 1$ (`Parking.xcrit_le_one`). If $l_1\ge 2$: by the closed form of the record of `Parking.kap_at_k`, $\kappa_L=p_{L-1}(e\,x_k)^{L}/(eL)$ with $p_n=e^{-n}n^n/n!$, so
$$\frac{\kappa_{l_2}}{\kappa_{l_1}}=\frac{p_{l_2-1}}{p_{l_1-1}}\,(e\,x_k)^{l_2-l_1}\,\frac{l_1}{l_2}\ \le\ \frac{12}{11}\sqrt{\frac{l_1-1}{l_2-1}}\cdot e^{3/2}\cdot\frac{l_1}{l_2},$$
using $p_n\le 1/\sqrt{2\pi n}$ and $p_n\ge(1-\frac{1}{12n})/\sqrt{2\pi n}\ge\frac{11}{12}/\sqrt{2\pi n}$ (`Parking.poissonMass_le`, `Parking.poissonMass_ge`) and $(e\,x_k)^{d}\le e^{3d/(2k)}\le e^{3/2}$ for $d\le k$ (`Parking.exp_one_mul_xcrit_le`). The gap gives $l_1\le 0.27\,l_2$ and $l_1-1\le 0.27\,(l_2-1)$, so the right side is at most $\frac{12}{11}\,e^{3/2}\cdot 0.27^{3/2}<\frac{1}{1.22}$; the Lean proof verifies this after squaring, with $e^3\le 20.0856$.

Now the three positions of $l$ and $L$.

*$l\ge k$.* By (b), $j\,\kappa_{n-(2k-1)}\le(2k-1)\,\kappa_l$. Since $q\le 2k$, $L\ge n-(2k-1)\ge 1$, so $\kappa_L\le\kappa_{n-(2k-1)}$ by monotonicity.

*$l<k$ and $L\le k$.* The gap is $L-l=j-q+1\ge 2k-1.27k+1\ge 0.73k$, so (c) gives $1.22\,\kappa_L\le\kappa_l$. From $L\le k$, $n\le k+q-1$ and $j\le n-1\le 2.27k-2\le 1.22\,(2k-1)$. Hence $\kappa_L\,j\le 1.22\,\kappa_L(2k-1)\le\kappa_l\,(2k-1)$.

*$l<k$ and $L>k$.* `Parking.kap_K3a` gives $L\,\kappa_L\le k\,\kappa_k$. It suffices to find a constant $c$ with $c\,\kappa_k\le\kappa_l$ and $k\,j\le c\,(2k-1)\,L$, for then $L\,\kappa_L\,j\le k\,\kappa_k\,j\le c\,(2k-1)\,L\,\kappa_k\le(2k-1)\,L\,\kappa_l$. If $l\le 0.27k$, take $c=1.22$: the first condition is (c) for the indices $l<k$, and the second follows from $j\le L+1.27k-2$ and $L\ge k+1$, because $1.27k^2-2k\le(1.44k-1.22)(k+1)$. If $l>0.27k$, take $c=1$: the first condition is monotonicity, and the second follows from $j\le L+k-2$ (a consequence of $l>0.27k$ and $q\le 1.27k$) and $L\ge k+1$, because $k^2-2k\le(k-1)(k+1)$.
