---
weight: unit
short: the extreme-column bound for renewal sequences
---
## Description

Let $G$ be the renewal sequence of a positive log-convex kernel $f$, let $v$ have nonnegative innovations with respect to $f$ up to time $\rho$, and let the weights $\theta$ be nonnegative and nondecreasing on $M,\dots,\rho$. Then $\bigl(\sum_{m=M}^{\rho}\theta_mf_mv_{\rho-m}\bigr)G_\rho \le \bigl(\sum_{m=M}^{\rho}\theta_mf_mG_{\rho-m}\bigr)v_\rho$.

## Statement

Let $f$, $G$, $v$, $\theta$ be sequences of real numbers indexed by the natural numbers, and let $\rho$ and $M \ge 1$ be natural numbers. Assume:

1. $f_i > 0$ for every $i \ge 1$, and $f_{i+1}^2 \le f_i\,f_{i+2}$ for every $i \ge 1$;
2. $G$ is the renewal sequence of $f$ (`Parking.IsRenewal`): $G_0 = 1$ and $G_n = \sum_{i=1}^{n}f_iG_{n-i}$ for $n \ge 1$;
3. $\theta_M \ge 0$, and $\theta_a \le \theta_b$ whenever $M \le a \le b \le \rho$;
4. (nonnegative innovations) $\sum_{i=1}^{s}f_i\,v_{s-i} \le v_s$ for every $s \le \rho$.

Then

$$\Bigl(\sum_{m=M}^{\rho}\theta_m\,f_m\,v_{\rho-m}\Bigr)\,G_\rho \;\le\; \Bigl(\sum_{m=M}^{\rho}\theta_m\,f_m\,G_{\rho-m}\Bigr)\,v_\rho.$$

## Explanation

The innovation of $v$ at the time $s$ is $\iota_s = v_s - \sum_{i=1}^{s}f_iv_{s-i}$; hypothesis 4 says $\iota_s \ge 0$ for $s \le \rho$ (in particular $v_0 \ge 0$). Since $G_\rho > 0$, the conclusion can be read as a bound for a ratio: the weighted feedback that $v$ receives at the time $\rho$ through the kernel indices $m \ge M$, measured against the value $v_\rho$ itself, is at most the same ratio computed for $v = G$. The sequence $G$ is the solution whose only innovation sits at time $0$. So among all sequences with nonnegative innovations, the one in which everything was injected as early as possible has the largest share of far feedback. This sequence is called the extreme column.

The reason is the following. Every such $v$ is a nonnegative combination of shifted copies of $G$, one for each innovation (`Parking.resolvent`). An innovation of age $s$ (injected at the time $\rho - s$) contributes $G_s$ to $v_\rho$ and $W(s) = \sum_{m=M}^{s}\theta_mf_mG_{s-m}$ to the far feedback. The claim is therefore that $W(s)/G_s$ is largest at the greatest age $s = \rho$. In terms of the renewal process, $f_mG_{s-m}/G_s$ is the share of $G_s$ that comes from histories whose last step has length $m$, and for a log-convex $G$ every ratio $G_{s-m}/G_s$ is nonincreasing in $s$. Hence the share of the last steps shorter than $M$ does not increase with the age $s$, and the share of the last steps of length at least $M$ does not decrease. Log-convexity of $G$ follows from that of $f$ by the theorem of de Bruijn and Erdős (`Parking.renewal_logConvex`). The weights must be nondecreasing so that shifting mass towards longer last steps can only increase the weighted share; the proof uses this at exactly two places, marked (A) and (B) below.

In `Parking.caseFar` the statement is applied with the frozen kernel $f$ of `Parking.fker`, its renewal sequence $G$ of `Parking.Gres`, the profile $v_\sigma = e^{-\sigma}b(k+\sigma,k-1)/(k+\sigma)!$ of the level $k-1$ in the Borel scale, $M = \lfloor\frac35k\rfloor$, and $\theta_m = \max(g_m - \gamma_k, 0)$. All that is known about the profile there is the sign of its innovations, and the statement converts this single piece of information into a bound of the far feedback by quantities that depend on $G$ only.

If $M > \rho$ both sums are empty and the statement is trivial. The statement is abstract: nothing in it refers to parking functions.

## Proof

By `Parking.renewal_pos` and `Parking.renewal_logConvex`, $G_n > 0$ and $G_{n+1}^2 \le G_nG_{n+2}$ for all $n$. By `Parking.logConvex_cross` this gives, for $m \le s \le \rho$,

$$G_s\,G_{\rho-m} \le G_{s-m}\,G_\rho.$$

This inequality is referred to as (1) below.

*Step 1: the tail of the renewal equation at two times.* Let $M \le s \le \rho$. Then

$$\Bigl(\sum_{m=M}^{s}f_mG_{s-m}\Bigr)G_\rho \le \Bigl(\sum_{m=M}^{\rho}f_mG_{\rho-m}\Bigr)G_s.$$

Indeed, by the renewal equation at $s$ and at $\rho$, the two tails equal $G_s - \sum_{m=1}^{M-1}f_mG_{s-m}$ and $G_\rho - \sum_{m=1}^{M-1}f_mG_{\rho-m}$. After multiplying by $G_\rho$ and $G_s$ respectively the leading terms agree, and the claim reduces to $\sum_{m<M}f_m\,G_{\rho-m}G_s \le \sum_{m<M}f_m\,G_{s-m}G_\rho$, which holds term by term by (1). The heads of the two equations are ordered one way by log-convexity, so the tails are ordered the other way.

*Step 2: the same with weights.* For every $s \le \rho$,

$$\Bigl(\sum_{m=M}^{s}\theta_mf_mG_{s-m}\Bigr)G_\rho \le W\,G_s, \qquad W = \sum_{m=M}^{\rho}\theta_mf_mG_{\rho-m}.$$

If $s < M$ the left side is $0$ and the right side is nonnegative, since $\theta_m \ge \theta_M \ge 0$ on $[M,\rho]$. Let $M \le s \le \rho$ and split $W$ into the parts $m \le s$ and $m > s$.

(A) On $M \le m \le s$ we have $\theta_m \le \theta_s$, and each difference $G_{s-m}G_\rho - G_sG_{\rho-m}$ is nonnegative by (1). Hence

$$\sum_{m=M}^{s}\theta_mf_m\bigl(G_{s-m}G_\rho - G_sG_{\rho-m}\bigr) \le \theta_s\sum_{m=M}^{s}f_m\bigl(G_{s-m}G_\rho - G_sG_{\rho-m}\bigr).$$

By Step 1 the right side is at most $\theta_s\bigl(\sum_{m=s+1}^{\rho}f_mG_{\rho-m}\bigr)G_s$.

(B) On $s < m \le \rho$ we have $\theta_m \ge \theta_s$, so $\theta_s\sum_{m=s+1}^{\rho}f_mG_{\rho-m} \le \sum_{m=s+1}^{\rho}\theta_mf_mG_{\rho-m}$.

Combining (A) and (B) and moving the part $m \le s$ of $W\,G_s$ to the right gives the claim of Step 2.

*Step 3: decomposition into innovations.* Let $\iota_s = v_s - \sum_{i=1}^{s}f_iv_{s-i}$, so that $\iota_s \ge 0$ for $s \le \rho$. By `Parking.resolvent`, $v_s = \sum_{c=0}^{s}G_{s-c}\,\iota_c$ for every $s$. Insert this for $v_{\rho-m}$ and exchange the two sums:

$$\sum_{m=M}^{\rho}\theta_mf_mv_{\rho-m} = \sum_{c=0}^{\rho-M}\iota_c\sum_{m=M}^{\rho-c}\theta_mf_mG_{(\rho-c)-m}.$$

Multiply by $G_\rho$ and apply Step 2 with $s = \rho - c$ to each inner sum, using $\iota_c \ge 0$:

$$\Bigl(\sum_{m=M}^{\rho}\theta_mf_mv_{\rho-m}\Bigr)G_\rho \le W\sum_{c=0}^{\rho-M}G_{\rho-c}\,\iota_c \le W\sum_{c=0}^{\rho}G_{\rho-c}\,\iota_c = W\,v_\rho.$$

The second inequality adds the terms $\rho - M < c \le \rho$, which are nonnegative because $W \ge 0$, $G > 0$ and $\iota_c \ge 0$.
