---
weight: unit
short: two-point persistence for abstract sequences
---
## Description

An abstract persistence statement. A sequence $\eta$ satisfies a column equation with feedback kernel $\kappa$ at a crossing row $q$ and at a later row $n$, is bounded below by the decrements of a nonnegative profile $U$ in between, is nonpositive before $q$ and positive on $[q, n)$; if $\kappa$ is positive, nonincreasing and log-convex in cross form and satisfies a condition comparing the two rows, then $\eta_n > 0$.

## Statement

Let $\eta$, $U$, $\kappa$ be sequences of real numbers indexed by the natural numbers, let $c_q$, $c_n$, $\varphi_q$, $\varphi_n$ be real numbers, and let $k$, $r_q$, $t$ be natural numbers with $r_q \ge 1$ and $t \ge 1$. Put $q = k + r_q$ and $n = q + t$. Assume $c_q \ge 0$, $\varphi_q \ge 0$, $\varphi_n > 0$, and:

1. (column equation at the two rows)
   $\eta_q = c_q\,U_{q-1} + \varphi_q\,\eta_{q-1} + \sum_{m=1}^{r_q}\kappa_m\,\eta_{q-m}$ and
   $\eta_n = c_n\,U_{n-1} + \varphi_n\,\eta_{n-1} + \sum_{m=1}^{r_q+t}\kappa_m\,\eta_{n-m}$;
2. (bottom row) $\eta_k = -U_k$;
3. (diagonal bound) $U_{j-1} - U_j \le \eta_j$ for every $j$ with $k + 1 \le j \le n - 1$;
4. (profile) $U_j \ge 0$ for every $j$;
5. (kernel) $\kappa_m > 0$ for $1 \le m \le r_q + t$, and $\kappa_{m+1} \le \kappa_m$ for $1 \le m \le r_q + t - 1$;
6. (cross inequality) $\kappa_{m+t}\,\kappa_{r_q} \le \kappa_{r_q+t}\,\kappa_m$ for $1 \le m \le r_q$;
7. (two-point condition) $\kappa_{r_q+t}\,c_q \le \kappa_{r_q}\,c_n$;
8. (signs) $\eta_j \le 0$ for $k \le j < q$, and $\eta_j > 0$ for $q \le j < n$.

Then $\eta_n > 0$.

## Explanation

The statement isolates, without any reference to parking functions, the mechanism by which a column stays positive on the rows shortly after its first positive row. In the application (`Parking.caseA`) $\eta_j$ is the tilted step $x^j d_{j,k}/j!$ of the column $k$, $U_j$ is the tilted profile $x^j b(j,k-1)/j!$ of the level $k-1$, $\kappa_m = x^m\varepsilon_m$ is the tilted prime kernel, and the coefficients are $c_j = 2x/j$, $\varphi_j = (k+1)x/j$.

The column equation says that the value at a row is a source, proportional to the profile, plus the feedback of all earlier rows of the column through the kernel. The rows before the crossing are nonpositive, so their feedback is a debt that the row $n$ still carries. The question is whether this debt can outweigh the source at the row $n$ although it did not at the row $q$. Three facts work against it. The debt as a whole is at most the profile: by the diagonal bound and $\eta_k = -U_k$, the sum of the nonpositive rows is at least $-U_{q-1}$. The weight of an old row at the row $n$, compared with its weight at the row $q$, has fallen by at least the factor $\kappa_{r_q+t}/\kappa_{r_q}$; this is the cross inequality, and it holds for a log-convex kernel. And by the two-point condition the source coefficient has fallen by no more than this factor between the two rows. The name of the statement comes from this: the column equation is used at two rows only, and the kernel is compared at two indices.

The argument does not need the positive run $[q, n)$ to have any particular length; it works for $t = 1$. This distinguishes it from `Parking.persistence_inequality`, which gains nothing unless many rows before $n$ are already known to be nonnegative. Its limits are hypotheses 5 and 7: the kernel must be nonincreasing over the whole range of distances $1,\dots,r_q+t$, and the two-point condition must hold. For the parking column both are available only while the row $n$ is not too far above $k$ (see `Parking.Fk_anti`).

No sign is assumed for $c_n$; hypothesis 7 with $c_q \ge 0$ is all that is used about it.

## Proof

The kernel is nonincreasing on $[1, r_q + t]$ by hypothesis 5. Suppose, for a contradiction, that $\eta_n \le 0$. Introduce

- $P = \sum_{m=1}^{t}\kappa_m\eta_{n-m}$, the feedback at the row $n$ of the positive rows $q,\dots,n-1$;
- $M_n = \sum_{m=1}^{r_q}\kappa_{m+t}\,\eta_{q-m}$, the feedback at the row $n$ of the nonpositive rows $k,\dots,q-1$;
- $M_q = \sum_{m=1}^{r_q}\kappa_m\,\eta_{q-m}$, the feedback of the same rows at the row $q$;
- $E = \sum_{j=q}^{n-1}\eta_j > 0$ and $H = \sum_{j=k}^{q-1}\eta_j \le 0$.

Splitting the feedback sum of the row $n$ at $m = t$ and shifting the index, the two column equations read $\eta_n = c_nU_{n-1} + \varphi_n\eta_{n-1} + P + M_n$ and $\eta_q = c_qU_{q-1} + \varphi_q\eta_{q-1} + M_q$.

*Comparisons of the sums.* (a) Since $\kappa_m \ge \kappa_t$ for $m \le t$ and the rows involved are positive, $P \ge \kappa_tE$. (b) Since $\kappa_{m+t} \le \kappa_{t+1}$ for $m \ge 1$ and the rows involved are nonpositive, $M_n \ge \kappa_{t+1}H$. (c) Multiplying the cross inequality by $\eta_{q-m} \le 0$ and summing over $m$, $\kappa_{r_q+t}\,M_q \le \kappa_{r_q}\,M_n$.

*Consequences of the diagonal bound.* (d) Summing hypothesis 3 over the rows $q \le j \le n-1$ telescopes to $U_{q-1} - U_{n-1} \le E$. (e) Summing it over the rows $k+1 \le j \le q-1$ gives $U_k - U_{q-1} \le H - \eta_k$, and with $\eta_k = -U_k$ this is $-U_{q-1} \le H$. Together, $-(E + H) \le U_{n-1}$.

*First bound: $c_n < \kappa_{t+1}$.* From $\eta_n \le 0$ and $\varphi_n\eta_{n-1} > 0$ the column equation at $n$ gives

$$c_nU_{n-1} + P < -M_n.$$

Call this inequality $(*)$. Using (a), (b), then $\kappa_{t+1} \le \kappa_t$ with $E > 0$, then (d) and (e) with $\kappa_{t+1} > 0$:

$$c_nU_{n-1} < -M_n - P \le -\kappa_{t+1}H - \kappa_tE \le \kappa_{t+1}\bigl(-(E+H)\bigr) \le \kappa_{t+1}U_{n-1}.$$

If $U_{n-1}$ were $0$ this would read $0 < 0$; hence $U_{n-1} > 0$ by hypothesis 4, and $c_n < \kappa_{t+1}$.

*Second bound: $\kappa_t < c_n$.* At the row $q$ we have $\eta_q > 0$, $\eta_{q-1} \le 0$ and $\varphi_q \ge 0$, so the column equation at $q$ gives $-M_q < c_qU_{q-1}$: at the crossing row the source exceeds the debt. Transfer this to the row $n$: by (c), then the inequality just obtained multiplied by $\kappa_{r_q+t} > 0$, then (d) in the form $U_{q-1} \le U_{n-1} + E$ with $c_q \ge 0$, then the two-point condition with $U_{n-1} + E \ge 0$,

$$-\kappa_{r_q}M_n \le -\kappa_{r_q+t}M_q < \kappa_{r_q+t}\,c_q\,U_{q-1} \le \kappa_{r_q+t}\,c_q\,(U_{n-1}+E) \le \kappa_{r_q}\,c_n\,(U_{n-1}+E).$$

Dividing by $\kappa_{r_q} > 0$: $-M_n < c_n(U_{n-1} + E)$. Combined with $(*)$ this gives $P < c_nE$, and with (a), $\kappa_tE < c_nE$, so $\kappa_t < c_n$ because $E > 0$.

*Contradiction.* $\kappa_t < c_n < \kappa_{t+1} \le \kappa_t$.
