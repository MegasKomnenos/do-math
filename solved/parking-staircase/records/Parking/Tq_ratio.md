---
weight: unit
short: erasure rule for compositions without cut factors
---
## Description

For the compositions of $m$ in which a part of size $p$ weighs $a_p=p^{p-1}/p!$ and the cuts contribute no factor, the total weights $T_{m,q}$ and $T_{m,q+1}$ of the compositions with $q$ and with $q+1$ parts satisfy $q\,m\,T_{m,q+1}=(q+1)(m-q)\,T_{m,q}$ for every $q\ge1$.

## Statement

Let $a_p=p^{p-1}/p!$ for $p\ge1$ (`Parking.cay`). For natural numbers $m$ and $q$ let $T_{m,q}$ (`Parking.Tq`) be the sum of the products $a_{p_1}a_{p_2}\cdots a_{p_q}$ over the compositions $(p_1,\dots,p_q)$ of $m$ with $q$ parts, that is, over the $q$-tuples of positive integers with sum $m$. Then for all natural numbers $m$ and $q$ with $q\ge1$,
$$q\,m\,T_{m,q+1}=(q+1)(m-q)\,T_{m,q}.$$

## Explanation

**What the identity gives.** It determines the ratio of the weights of $q+1$ and of $q$ parts: $T_{m,q+1}/T_{m,q}=\frac{q+1}{q}\bigl(1-\frac qm\bigr)$ for $1\le q<m$. Since $T_{m,1}=a_m$, all the $T_{m,q}$ follow, $T_{m,q}=a_m\,q\,\prod_{i=1}^{q-1}(1-\frac im)$, which is `Parking.Tq_eq`. With $P_{m,q}=\prod_{i<q}(1-\frac im)$ (`Parking.Pb`), the probability that the first $q$ balls thrown independently and uniformly into $m$ boxes fall into distinct boxes, this reads $T_{m,q}=a_m\,q\,P_{m,q}$. Since $\frac qm P_{m,q}=P_{m,q}-P_{m,q+1}$, the weights $T_{m,q}$, $1\le q\le m$, add up to $m\,a_m$ for $m\ge1$, and the number of parts $Q$ of a composition of $m$ drawn with probability proportional to its weight satisfies $\Pr(Q=q)=P_{m,q}-P_{m,q+1}$: it has the law of the number of balls thrown before the first repetition, which the library calls the birthday law. The value agrees with the one that Lagrange inversion gives for the coefficient of $x^m$ in the $q$-th power of the tree series $\sum_p a_px^p$, namely $\frac qm\,\frac{m^{m-q}}{(m-q)!}$; the library does not use Lagrange inversion and gets the closed form from this ratio. For $q\ge m$ both sides of the identity are $0$, because no composition of $m$ has more than $m$ parts and the factor $m-q$ vanishes at $q=m$.

**The erasure rule.** The identity is called the erasure rule because it compares the compositions with $q+1$ parts and those with $q$ parts through one operation: erasing a cut. Describe a composition $c$ of $m$ with $q+1$ parts by its cut points $0<s_1<\dots<s_q<m$ and its part sizes $t_i=s_i-s_{i-1}$, where $s_0=0$ and $s_{q+1}=m$, and let $\operatorname{wt}(c)=a_{t_1}\cdots a_{t_{q+1}}$. Erasing the cut $s_i$ merges the neighbouring parts $t_i$ and $t_{i+1}$ into one part of size $t_i+t_{i+1}$ and leaves a composition with $q$ parts. Count the pairs formed by a composition $c$ and one of its cuts $s_i$, giving the pair the multiplicity
$$\omega_i(c)=(q+1-i)\,t_i+i\,t_{i+1}.$$
The multiplicity is chosen so that, on each side of the operation, every composition is counted a number of times that does not depend on the composition: $q\,m$ times on the side with $q+1$ parts, and $(q+1)(m-q)$ times on the side with $q$ parts.

On the side of $c$: in the sum $\sum_{i=1}^q\omega_i(c)$ the part $t_j$ occurs with the coefficient $q+1-j$ as the left neighbour of the cut $s_j$ and with the coefficient $j-1$ as the right neighbour of the cut $s_{j-1}$ (the first part has no cut to its left and the last part none to its right, and the corresponding coefficients $j-1$ and $q+1-j$ are $0$ there), hence $q$ times in all, and the sum is $q\,m$ whatever $c$ is. So the pairs, each counted with the weight of its composition, have total weight $q\,m\,T_{m,q+1}$.

On the side of the composition $c'$ that is left after the erasure: the pairs that give $c'$ by merging into its $i$-th part, of size $u$, correspond to the $u-1$ places at which that part can be cut into a left piece $\alpha$ and a right piece $\beta$. The other parts are the same in $c$ and in $c'$, and for the two pieces the convolution identity of the numbers $a_p$,
$$\sum_{\alpha+\beta=u}\alpha\,a_\alpha a_\beta=\sum_{\alpha+\beta=u}\beta\,a_\alpha a_\beta=(u-1)\,a_u$$
(`Parking.cay_conv` states the first form; the second is the first with the names of the two pieces exchanged), says that the weights of the $u-1$ cut versions, each multiplied by the size of its left piece, or each by the size of its right piece, add up to $u-1$ times the weight of the uncut part. With the multiplicity $(q+1-i)\alpha+i\beta$ these pairs therefore weigh $(q+1)(u-1)\operatorname{wt}(c')$ in all, and summing over the $q$ parts of $c'$, whose sizes add up to $m$, gives $(q+1)(m-q)\operatorname{wt}(c')$. So the same pairs have total weight $(q+1)(m-q)\,T_{m,q}$.

The convolution identity is the only property of the numbers $a_p$ that enters. When each cut at a position $s$ carries a factor $f(s)$, the first count is unchanged, and in the second count the factor of the erased cut is missing. The two counts then differ by the terms in which the erased cut has the factor $1-f(s)$ in place of $f(s)$; this is the identity (E) in the proof below. When no cut carries a factor, that is for $f=1$, these terms vanish and the two counts agree.

**The form of the proof.** The Lean proof does not sum over compositions. It writes the weights as entries of products of matrices indexed by the positions $0,\dots,m$: a matrix $G$ that holds the numbers $a_p$ stands for a part and a diagonal matrix $F$ for the factor of a cut. The two counts above then become two algebraic facts. That the part sizes of a composition add up to $m$ becomes a Leibniz rule for the commutator with the diagonal matrix $X$ of the positions, and the convolution identity becomes the matrix identity $HG=GH=H-G$ for $H=GX-XG$. The proof below follows the Lean proof; the count over pairs is the same computation read entry by entry.

**The Lean form.** `Parking.Tq m q` is defined as `Parking.Vc (fun _ => 1) q m`: the arguments of `Tq` are the size $m$ and then the number of parts $q$, and those of `Vc` are the profile, the number of parts and then the size. In the Lean statement $q$ and $m$ are cast to real numbers and $m-q$ is the difference of real numbers, so the statement is the one above for all $m$ and all $q\ge1$, without truncation. The hypothesis $q\ge1$ is used to write $q=r+1$; at $q=0$ both sides would be $0$.

**Where it is used.** `Parking.Tq_eq` derives the birthday law from it by induction on $q$.

## Proof

The proof establishes an identity (E) for an arbitrary cut profile $f:\mathbb N\to\mathbb R$ and then puts $f=1$. Here $V_q(m;f)$ denotes `Parking.Vc`: the total weight of the compositions of $m$ with $q$ parts when each part of size $p$ weighs $a_p$ and each cut at a position $s$ weighs $f(s)$; it satisfies $V_1(x;f)=a_x$ (`Parking.Vc_one`), $V_{q+2}(x;f)=\sum_{0<s<x}V_{q+1}(s;f)\,f(s)\,a_{x-s}$ (`Parking.Vc_succ_succ`) and $V_q(x;f)=0$ for $x<q$ (`Parking.Vc_eq_zero_of_lt`), and $T_{m,q}=V_q(m;1)$ by definition. We put $a_0=0$, as `Parking.cay` does. The Lean file writes $q=r+1$ throughout.

**The matrix model.** Fix $m$ and $f$. All matrices are real, with rows and columns indexed by the positions $0,1,\dots,m$. Let $G$ be the strictly upper triangular matrix with $G_{ij}=a_{j-i}$ for $i<j$ and $G_{ij}=0$ otherwise, let $F$ be the diagonal matrix with the entries $f(0),\dots,f(m)$, let $X$ be the diagonal matrix with the entries $0,1,\dots,m$, and let $H=GX-XG$. Then $H_{ij}=(j-i)\,a_{j-i}$ for $i<j$ and $H_{ij}=0$ otherwise.

**(B) Entries of words are weights of compositions.** For every $q\ge0$ and every position $x$, the entry $(0,x)$ of $G(FG)^q$ is $V_{q+1}(x;f)$. This is an induction on $q$. For $q=0$ the entry is $G_{0x}=a_x=V_1(x;f)$. For the step, the entry $(0,x)$ of $G(FG)^{q+1}=G(FG)^q\,F\,G$ is $\sum_{u<x}V_{q+1}(u;f)\,f(u)\,a_{x-u}$ by the induction hypothesis; the term $u=0$ vanishes because $V_{q+1}(0;f)=0$, and what remains is the recursion for $V_{q+2}(x;f)$.

For natural numbers $a$, $b$ and a matrix $C$, write $W_{a,b}(C)$ for the entry $(0,m)$ of the word $(GF)^a\,C\,(FG)^b$. It is linear in $C$, and directly from the definition
$$W_{a,b}(C\,FG)=W_{a,b+1}(C),\qquad W_{a,b}(GF\,C)=W_{a+1,b}(C),\qquad W_{a,b}(G)=V_{a+b+1}(m;f),$$
the last because $(GF)^aG(FG)^b=G(FG)^{a+b}$ and by (B). Read as a sum over compositions, $W_{a,b}(C)$ runs over the compositions of $m$ in which $a$ parts come before a marked piece and $b$ parts after it, the marked piece from position $i$ to position $j$ contributing $C_{ij}$ in place of $a_{j-i}$; for $C=H$ the marked piece is a part weighted by its size.

**(L) The Leibniz rule.** Let $Z$ be a diagonal matrix with the entries $z(0),\dots,z(m)$. Since $Z$ commutes with $F$, the map $A\mapsto AZ-ZA$ is a derivation that vanishes on $F$, and applied to the product $G(FG)^q$, which has $q+1$ factors $G$, it gives
$$G(FG)^q\,Z-Z\,G(FG)^q=\sum_{p=0}^{q}(GF)^p\,(GZ-ZG)\,(FG)^{q-p}$$
(in Lean, an induction on $q$ in an arbitrary ring). By (B) the entry $(0,m)$ of the left side is $(z(m)-z(0))\,V_{q+1}(m;f)$, so $\sum_{p=0}^qW_{p,q-p}(GZ-ZG)=(z(m)-z(0))\,V_{q+1}(m;f)$. For $Z=X$ this reads
$$\sum_{p=0}^{q}W_{p,q-p}(H)=m\,V_{q+1}(m;f).\tag{L1}$$

**(F) The fundamental identity** $HG=GH=H-G$. All three matrices are strictly upper triangular. For $i<j$ put $t=j-i$. The entry $(i,j)$ of $HG$ is $\sum_{i<u<j}(u-i)\,a_{u-i}\,a_{j-u}=\sum_{\alpha=1}^{t-1}\alpha\,a_\alpha a_{t-\alpha}$, which is $(t-1)\,a_t=H_{ij}-G_{ij}$ by `Parking.cay_conv`. The entry $(i,j)$ of $GH$ is $\sum_{\alpha=1}^{t-1}a_\alpha\,(t-\alpha)\,a_{t-\alpha}$, the same sum with $\alpha$ replaced by $t-\alpha$.

**(E1) The erasure identity.** For every $q\ge1$,
$$\sum_{p=0}^{q-1}\Bigl[(q-p)\,W_{p,q-1-p}(HG)+(p+1)\,W_{p,q-1-p}(GH)\Bigr]=(q+1)(m-q)\,V_q(m;f).$$
Indeed, by (F) and linearity the bracket equals $(q+1)\bigl(W_{p,q-1-p}(H)-W_{p,q-1-p}(G)\bigr)=(q+1)\bigl(W_{p,q-1-p}(H)-V_q(m;f)\bigr)$, and the sum over the $q$ values of $p$ is $(q+1)\bigl(m\,V_q(m;f)-q\,V_q(m;f)\bigr)$ by (L1) with $q-1$ in place of $q$. In the words on the left the two neighbouring parts $HG$, or $GH$, have no factor $F$ between them: these are the compositions with $q+1$ parts in which the factor of one cut has been erased.

**(S) The same sum with the factor of the cut in place.** For every $q\ge1$,
$$\sum_{p=0}^{q-1}\Bigl[(q-p)\,W_{p,q-p}(H)+(p+1)\,W_{p+1,q-1-p}(H)\Bigr]=q\,m\,V_{q+1}(m;f).$$
In the second family replace $p+1$ by $p$. The word $W_{p,q-p}(H)$, $0\le p\le q$, then has the coefficient $(q-p)+p=q$ (for $p=q$ only the second family contributes and for $p=0$ only the first, and the missing coefficients $q-p$ and $p$ are $0$ there), and the sum is $q\sum_{p=0}^{q}W_{p,q-p}(H)=q\,m\,V_{q+1}(m;f)$ by (L1).

**(E) The defect.** Write $1$ for the identity matrix. Since $H(1-F)G=HG-HFG$ and $G(1-F)H=GH-GFH$, linearity and the two absorption rules give $W_{p,q-1-p}(H(1-F)G)=W_{p,q-1-p}(HG)-W_{p,q-p}(H)$ and $W_{p,q-1-p}(G(1-F)H)=W_{p,q-1-p}(GH)-W_{p+1,q-1-p}(H)$. Subtracting (S) from (E1) therefore gives, for every profile $f$ and every $q\ge1$,
$$(q+1)(m-q)\,V_q(m;f)-q\,m\,V_{q+1}(m;f)=\sum_{p=0}^{q-1}\Bigl[(q-p)\,W_{p,q-1-p}\bigl(H(1-F)G\bigr)+(p+1)\,W_{p,q-1-p}\bigl(G(1-F)H\bigr)\Bigr].\tag{E}$$

**Conclusion.** For the constant profile $f=1$ the matrix $F$ is the identity, $1-F=0$, and every word on the right of (E) is $0$. Since $V_q(m;1)=T_{m,q}$ and $V_{q+1}(m;1)=T_{m,q+1}$, (E) is the identity of the statement.
