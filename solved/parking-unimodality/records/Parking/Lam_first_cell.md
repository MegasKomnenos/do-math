---
weight: unit
short: removal of the first unit cell
---
## Description

Removing the first unit cell of a composition of $r+1$: with $N = k + r + 1$ and $h = (k-1)/(k+r)$, the chain sums satisfy $\Lambda_{r+1}(k-1;N)\,\tau_r(h) \le \tau_{r+1}(h)\,\Lambda_r(k;N)$, so the ratio of the chain sums of the lengths $r+1$ and $r$ is at most the ratio of the totals of the homogeneous model.

## Statement

Let $k \ge 2$ and $r \ge 1$ be natural numbers, and put $N = k + r + 1$ and $h = (k-1)/(k+r)$. Then

$$\Lambda_{r+1}(k-1;N)\ \tau_r(h) \ \le\ \tau_{r+1}(h)\ \Lambda_r(k;N).$$

Here $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam`, `Parking.thr`), and $\tau_m(h)$ is the total weight when every cut weighs $h$ (`Parking.tau`).

## Explanation

The two boundary terms of `Parking.dq_frozen` are chain sums of different lengths, $\Lambda_{r+1}(k-1;N)$ for column $k$ and $\Lambda_r(k+2;N)$ for column $k+1$. To compare them, the longer one has to be shortened by one. The present statement does this and at the same time raises the threshold from $k-1$ to $k$. The price is the ratio $\tau_{r+1}(h)/\tau_r(h)$ of the same shortening in the homogeneous model, which the birthday law makes explicit (`Parking.tau_succ_le`); the two are combined in `Parking.Lam_shorten`.

The idea is to look at the first part of a composition of $r+1$. If it is a unit cell, removing it leaves a composition of $r$ and costs the weight of the first cut. If it is larger, shrinking it by one leaves a composition of $r$ whose first part $j$ has been charged the factor $\psi(j) = a_{j+1}/a_j = (1+1/j)^{j-1}$. So $\Lambda_{r+1}$ is the weight of the first cut times $\Lambda_r$ plus $\Lambda_r$ times the mean of $\psi$ of the first part, and the same holds for the homogeneous model. The function $\psi$ is nondecreasing. Under a larger cut profile cuts are more likely, the first part is stochastically smaller, and the mean of $\psi$ of the first part is smaller. The threshold profile $(k-1)/(N-s)$ is smallest at the first cut point $s = 1$, where it equals $h$; so it is at least the constant profile $h$, while the weight of the first cut is the same in both models. This gives the inequality.

The comparison of the laws of the first part is a correlation inequality of FKG type on the lattice of cut sets. Its hypothesis is that the weight $\prod a_{\text{part}}$ is log-supermodular as a function of the set of cut points, and this is a consequence of the log-convexity of the Cayley numbers.

## Proof

Throughout, a profile is a function $\mathbb{N} \to \mathbb{R}$, $f(c + \cdot)$ denotes the shifted profile $s \mapsto f(c+s)$, and $\psi(j) = (1+1/j)^{j-1}$. For a function $\varphi : \mathbb{N} \to \mathbb{R}$, a profile $f$ and $r \ge 1$ put

$$\Phi_\varphi(r;f) = \varphi(r)\,a_r + \sum_{0<j<r} \varphi(j)\,a_j\,f(j)\,\Lambda_{r-j}[f(j+\cdot)].$$

By `Parking.Lam_first` the terms are the total weights of the compositions of $r$ whose first part is $r$, respectively $j$; so $\Phi_\varphi(r;f)$ is the sum over the compositions of $r$ of the weight times $\varphi$ of the first part, and $\Phi_{1}(r;f) = \Lambda_r[f]$.

**Step 1: the first-cell recursion.** For every profile $f$ and $r \ge 1$, with $f' = f(1+\cdot)$,

$$\Lambda_{r+1}[f] = f(1)\,\Lambda_r[f'] + \Phi_\psi(r;f').$$

Apply `Parking.Lam_first` to $\Lambda_{r+1}[f]$. The term of the first part $g = 1$ is $a_1 f(1) \Lambda_r[f'] = f(1)\Lambda_r[f']$. In the term of a first part $g = j + 1$ with $1 \le j \le r - 1$, write $a_{j+1} = \psi(j)\,a_j$ (`Parking.cay_ratio`), $f(j+1) = f'(j)$ and $f(j+1+\cdot) = f'(j+\cdot)$; the term becomes $\psi(j)\,a_j\,f'(j)\,\Lambda_{r-j}[f'(j+\cdot)]$. The term of the single part is $a_{r+1} = \psi(r)\,a_r$.

**Step 2: the correlation inequality.** Let $0 \le g(s) \le f(s)$ for all $s$, let $\varphi \ge 0$ satisfy $\varphi(i) \le \varphi(j)$ for $1 \le i \le j$, and let $r \ge 1$. Then

$$\Phi_\varphi(r;f)\ \Lambda_r[g] \ \le\ \Phi_\varphi(r;g)\ \Lambda_r[f].$$

Represent a composition of $r$ by its set $S \subseteq \{1, \dots, r-1\}$ of cut points. Let $w(S)$ be the product of the Cayley numbers of its parts, $W_f(S) = w(S)\prod_{s \in S} f(s)$ its weight, and $\mathrm{fp}(S)$ its first part, the least element of $S$, or $r$ if $S$ is empty. Then $\sum_S W_f(S)\,\varphi(\mathrm{fp}(S)) = \Phi_\varphi(r;f)$ and $\sum_S W_f(S) = \Lambda_r[f]$, the sums running over all subsets. Both follow by sorting the cut sets by their first point and identifying the total weight of the cut sets of the remaining segment with the total of `Parking.Lam`, by induction on its length through `Parking.Lam_first`.

The four functions theorem of Ahlswede and Daykin (Mathlib's `Finset.four_functions_theorem`) states: if $f_1, f_2, f_3, f_4$ are nonnegative functions on the subsets of a finite set with $f_1(S)\,f_2(T) \le f_3(S \cap T)\,f_4(S \cup T)$ for all $S$, $T$, then $\bigl(\sum_S f_1(S)\bigr)\bigl(\sum_T f_2(T)\bigr) \le \bigl(\sum_S f_3(S)\bigr)\bigl(\sum_S f_4(S)\bigr)$, all sums over all subsets. Apply it with

$$f_1(S) = W_f(S)\,\varphi(\mathrm{fp}(S)), \quad f_2(T) = W_g(T), \quad f_3(S) = W_g(S)\,\varphi(\mathrm{fp}(S)), \quad f_4(S) = W_f(S).$$

The conclusion is the claim. The hypothesis is the product of three inequalities between nonnegative quantities:

(a) $w(S)\,w(T) \le w(S \cap T)\,w(S \cup T)$;

(b) $\prod_{s \in S} f(s) \prod_{s \in T} g(s) \le \prod_{s \in S \cap T} g(s) \prod_{s \in S \cup T} f(s)$;

(c) $\varphi(\mathrm{fp}(S)) \le \varphi(\mathrm{fp}(S \cap T))$.

For (c): the first point of the smaller set $S \cap T$ is at least the first point of $S$, which is at least $1$, and $\varphi$ is nondecreasing from $1$ on. For (b): $\prod_{S \cup T} f = \prod_S f \cdot \prod_{T \setminus S} f$ and $\prod_T g = \prod_{S \cap T} g \cdot \prod_{T \setminus S} g$, and $g \le f$ on $T \setminus S$.

Inequality (a), the log-supermodularity of the Cayley weight, is proved by scanning the positions from left to right. For a cut set $S$, a position $p$, a base point $x < p$ and a number $n$ of positions still to be scanned, let $G_S(n,p,x)$ be the product of the Cayley numbers of the parts that $S$ cuts out of the segment from $x$ to $p + n$ when only the positions $p, \dots, p+n-1$ are examined; $x$ is the last cut seen so far. Formally $G_S(0,p,x) = a_{p-x}$, and $G_S(n+1,p,x)$ is $a_{p-x}\,G_S(n,p+1,p)$ if $p \in S$ and $G_S(n,p+1,x)$ otherwise. Then $w(S) = G_S(r-1,1,0)$, and (a) is the case $x = x' = 0$, $p = 1$, $n = r - 1$ of

$$G_S(n,p,x)\ G_T(n,p,x') \ \le\ G_{S \cap T}(n,p,\min(x,x'))\ G_{S \cup T}(n,p,\max(x,x')) \qquad (x, x' < p).$$

This is proved by induction on $n$. For $n = 0$ both sides are $a_{p-x}\,a_{p-x'}$. For the step there are four cases, according to whether $p$ belongs to $S$ and to $T$. If $p$ belongs to neither, the scan moves on with the same base points and the induction hypothesis applies. If it belongs to both, each side acquires the factor $a_{p-x}\,a_{p-x'}$ and all four base points become $p$. If $p \in S$ and $p \notin T$, the left side is $a_{p-x}\,G_S(n,p+1,p)\,G_T(n,p+1,x')$, and the induction hypothesis with the base points $p$ and $x'$ bounds it by $a_{p-x}\,G_{S \cap T}(n,p+1,x')\,G_{S \cup T}(n,p+1,p)$. The right side is $G_{S \cap T}(n,p+1,\min(x,x'))\cdot a_{p-\max(x,x')}\,G_{S \cup T}(n,p+1,p)$, so what remains is

$$a_{p-x}\ G_{S \cap T}(n,p+1,x') \ \le\ a_{p-\max(x,x')}\ G_{S \cap T}(n,p+1,\min(x,x')).$$

For $x \ge x'$ this is an equality. For $x \le x'$ it is the base-change inequality: for every cut set $I$ and $x \le x' < q \le p'$,

$$a_{q-x}\ G_I(n,p',x') \ \le\ a_{q-x'}\ G_I(n,p',x).$$

The base-change inequality is proved by induction on $n$: the part that begins at the base point ends at the first cut $c \ge p'$ of $I$ or at the endpoint, and the inequality reduces to $a_{q-x}\,a_{c-x'} \le a_{q-x'}\,a_{c-x}$ for $x \le x' < q \le c$, which is the log-convexity of the Cayley numbers (`Parking.cay_logconvex`: $a_{u+d}\,a_v \le a_u\,a_{v+d}$ for $1 \le u \le v$, with $u = q - x'$, $v = c - x'$, $d = x' - x$). The case $p \in T$, $p \notin S$ is symmetric.

**Step 3: profiles above a constant.** Let $h \ge 0$, let $f$ be a profile with $f(s) \ge h$ for all $s$ and $f(1) = h$, and let $r \ge 1$. Then

$$\Lambda_{r+1}[f]\ \tau_r(h) \ \le\ \tau_{r+1}(h)\ \Lambda_r[f'], \qquad f' = f(1+\cdot).$$

By step 1 for $f$ and for the constant profile $h$, the left side is $\bigl(h\,\Lambda_r[f'] + \Phi_\psi(r;f')\bigr)\tau_r(h)$ and the right side is $\bigl(h\,\tau_r(h) + \Phi_\psi(r;h)\bigr)\Lambda_r[f']$. The terms with the factor $h$ cancel, and what remains is $\Phi_\psi(r;f')\,\tau_r(h) \le \Phi_\psi(r;h)\,\Lambda_r[f']$. This is step 2 for the profiles $h \le f'$ and $\varphi = \psi$, which is nonnegative and nondecreasing on $i \ge 1$ by `Parking.psi_mono`; recall $\tau_r(h) = \Lambda_r[h]$.

**Step 4: the threshold profile.** Let $\lambda(s) = (k-1)/(N-s)$ be the threshold profile for the threshold $k - 1$. At the cut points $1 \le s \le r$ of a composition of $r + 1$ we have $N - s \le N - 1 = k + r$, so $\lambda(s) \ge h$, with equality at $s = 1$. Step 3 requires the lower bound at all natural numbers, so replace $\lambda$ by $\tilde\lambda = \max(\lambda, h)$; this does not change $\Lambda_{r+1}$ (`Parking.Lam_congr`), and $\tilde\lambda(1) = h$. Step 3 gives $\Lambda_{r+1}(k-1;N)\,\tau_r(h) \le \tau_{r+1}(h)\,\Lambda_r[\tilde\lambda(1+\cdot)]$. At a cut point $1 \le s \le r - 1$ of a composition of $r$,

$$h \le \tilde\lambda(1+s) = \frac{k-1}{N-1-s} \le \frac{k}{N-s},$$

the last inequality being equivalent to $k \le N - s$. Hence $\Lambda_r[\tilde\lambda(1+\cdot)] \le \Lambda_r(k;N)$ by `Parking.Lam_mono`. Multiplying by $\tau_{r+1}(h) \ge 0$ (`Parking.tau_pos`) gives the statement.
