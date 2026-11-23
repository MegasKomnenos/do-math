---
weight: unit
short: criterion function
---
## Description

The criterion function $\mathsf{G}(r,k)$: an explicit function of the column $k$ and of the distance $r = n - k$ of a row from it, whose nonnegativity implies that a nonpositive step of column $k$ in the row $n$ forces a negative step of column $k+1$ in the same row.

## Statement

For natural numbers $r$ and $k$,

$$\mathsf{G}(r,k) = k\Bigl(\frac{1}{2r} - \frac{1}{3r^2}\Bigr) - \frac{5}{2} + \frac{1}{2}\,\mu^0_r\Bigl(\frac{r(r+1)}{k-1}\Bigr) + 2\Bigl(1 - \frac{1}{k}\Bigr)\mu^0_r\Bigl(\frac{r(r+2)}{2k}\Bigr) - \frac{k}{k-1}\,D_r,$$

where $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2 + 12(r-1)} - (4+X)\bigr)/3$ (`Parking.mu0`) and $D_r = 3\bigl((r+2)s_r - 3r\bigr)/\bigl(2(r - s_r)\bigr)$ with $s_r = \sum_{j=1}^{r} r(r-1)\cdots(r-j+1)/r^j$ (`Parking.Dbirth`, `Parking.sbirth`).

## Explanation

The function is used through `Parking.step_neg_of_Gfun`, and its form is best read against the proof of that statement. Let $n = k + r$ with $2 \le r \le k-1$. By `Parking.dq_frozen` the normalised steps of the columns $k$ and $k+1$ in the row $n$ are $C_- - B_-$ and $C_+ - B_+$, where $C_\pm$ are two second differences of one polynomial (the curvatures) and $B_\pm$ are two positive boundary terms. If $C_- \le B_-$, then $C_+ < B_+$ follows as soon as the boundary term grows by a larger factor than the curvature when one passes from column $k$ to column $k+1$. The proof bounds the two factors separately:

$$\frac{C_+}{C_-} \le e^{D_r/(k-1)}, \qquad \frac{B_+}{B_-} \ge \frac{(1+1/k)^{k-2}\,(1+2/k)^{\mu_{\mathrm{mid}}}}{(1+1/r)^{r}\, e^{-\mu_-/(2(k-1))}},$$

where $\mu_-$ and $\mu_{\mathrm{mid}}$ are the mean numbers of cuts under two homogeneous laws on the compositions of $r$ (`Parking.muh` at $h_- = (k-1)/(k+r)$ and at $h_{\mathrm{mid}} = k/(k+1+r/2)$). The logarithm of the quotient of the two bounds is the margin

$$(k-2)\log\Bigl(1+\frac1k\Bigr) + \mu_{\mathrm{mid}}\log\Bigl(1+\frac2k\Bigr) - r\log\Bigl(1+\frac1r\Bigr) + \frac{\mu_-}{2(k-1)} - \frac{D_r}{k-1},$$

and $\mathsf{G}(r,k)$ is $k$ times an explicit lower bound for it: the proof of `Parking.step_neg_of_Gfun` shows that the margin is at least $\mathsf{G}(r,k)/k + 1/k^2$. Each term of $\mathsf{G}$ comes from one term of the margin.

- The terms $k\bigl(1/(2r) - 1/(3r^2)\bigr) - 5/2$ come from the two powers. The factor $(1+1/k)^{k-2}$ is the ratio of the constants $a_{k+1}/(k+1)$ and $a_k/k$ in front of the two boundary terms, and $(1+1/r)^r$ is the cost of shortening a composition from length $r+1$ to length $r$. Both are close to $e$: $(k-2)\log(1+1/k) \ge 1 - 5/(2k) + 1/k^2$ and $r\log(1+1/r) \le 1 - 1/(2r) + 1/(3r^2)$. The leading terms cancel and the difference, times $k$, is what remains.
- The term $\tfrac12\mu^0_r\bigl(r(r+1)/(k-1)\bigr)$ comes from $\mu_-/(2(k-1))$, the gain in the shortening step (`Parking.Lam_shorten`), with $\mu_-$ replaced by its lower bound from `Parking.mu0_le_muh`. The argument $r(r+1)/(k-1)$ is $X = r(1/h - 1)$ at $h = h_-$.
- The term $2(1 - 1/k)\,\mu^0_r\bigl(r(r+2)/(2k)\bigr)$ comes from $\mu_{\mathrm{mid}}\log(1+2/k)$, the gain from raising the threshold by two (`Parking.Lam_raise`), with $\log(1+2/k) \ge (2/k)(1 - 1/k)$ and $\mu_{\mathrm{mid}}$ replaced by its lower bound. The argument $r(r+2)/(2k)$ is $X$ at $h = h_{\mathrm{mid}}$.
- The term $-\tfrac{k}{k-1} D_r$ is the loss $D_r/(k-1)$ from the curvature ratio (`Parking.curv_ratio`).

So $\mathsf{G}$ weighs the gains of the boundary term, which are of the size of a mean number of cuts under a homogeneous law, against the loss of the curvature, which is governed by a moment ratio of the birthday law. Both are of the order $\sqrt{r}$ as long as the arguments of $\mu^0_r$ stay bounded by a multiple of $\sqrt{r}$, that is, as long as $r^{3/2}$ is at most of the order of $k$. `Parking.Gfun_pos` proves $\mathsf{G}(r,k) > 0$ for $k \ge 265$, $r \ge 2$ and $25 r^3 \le 121 k^2$, which is the range of rows in which a column $k \ge 265$ can still be nonpositive (`Parking.crossing_strip`).

In Lean the definition is `Gfun r k`, with $r$ and $k$ natural numbers cast to real numbers. The formula contains divisions by $r$, $k$, $k-1$ and, inside $D_r$, by $r - s_r$. The function is used for $k \ge 3$ and $r \ge 2$, where all of them are positive.
