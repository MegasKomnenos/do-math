---
weight: unit
short: erasure inequality for cut factors between 0 and 1
---
## Description

If every cut of a composition of $m$ carries a factor between $0$ and $1$, the total weights $V_q$ and $V_{q+1}$ of the compositions with $q$ and with $q+1$ parts satisfy $q\,m\,V_{q+1}\le(q+1)(m-q)\,V_q$ for every $q\ge1$: the ratio $V_{q+1}/V_q$ is at most its value when every cut has the factor $1$.

## Statement

Let $a_p=p^{p-1}/p!$ for $p\ge1$ (`Parking.cay`). For a function $f:\mathbb N\to\mathbb R$, the cut profile, and natural numbers $m$ and $q$, let $V_q(m;f)$ (`Parking.Vc`) be the total weight of the compositions of $m$ with $q$ parts, where the weight of a composition with part sizes $p_1,\dots,p_q$ and cut points $s_j=p_1+\dots+p_j$, $1\le j\le q-1$, is $a_{p_1}\cdots a_{p_q}\,f(s_1)\cdots f(s_{q-1})$.

Let $m$ be a natural number and let $f$ satisfy $0\le f(s)\le1$ for every integer $s$ with $0<s<m$. Then for every natural number $q\ge1$,
$$q\,m\,V_{q+1}(m;f)\le(q+1)(m-q)\,V_q(m;f).$$

## Explanation

**What the inequality says.** For the constant profile $1$ the two sides are equal: this is `Parking.Tq_ratio`, $q\,m\,T_{m,q+1}=(q+1)(m-q)\,T_{m,q}$ with $T_{m,q}=V_q(m;1)$ (`Parking.Tq`). So the statement is that cut factors in $[0,1]$ can only lower the ratio of the weight of $q+1$ parts to the weight of $q$ parts, whatever their dependence on the position: $V_{q+1}(m;f)\,T_{m,q}\le V_q(m;f)\,T_{m,q+1}$. In the language of laws on compositions, the number of parts under the profile $f$ is dominated, in likelihood-ratio order, by the number of parts when every cut has the factor $1$, which follows the birthday law (`Parking.Tq_eq`).

**Why it holds.** A composition with $q+1$ parts has one cut more than a composition with $q$ parts, hence one factor $f(s)\le1$ more, but the two families are not matched with each other in any evident way, so the weights cannot simply be compared term by term. The comparison is made by the erasure rule explained in the record of `Parking.Tq_ratio`: one counts the pairs formed by a composition $c$ with $q+1$ parts and one of its cuts $s_i$, with the multiplicity $\omega_i(c)=(q+1-i)\,t_i+i\,t_{i+1}$, where $t_i$ and $t_{i+1}$ are the sizes of the parts to the left and to the right of that cut. Counted with the full weight of $c$, the pairs weigh $q\,m\,V_{q+1}(m;f)$. Counted with the weight of $c$ from which the factor $f(s_i)$ of the chosen cut has been removed, they weigh $(q+1)(m-q)\,V_q(m;f)$, because without that factor the weight depends on the two neighbouring parts only through the composition obtained by erasing the cut, and the convolution identity $\sum_{\alpha+\beta=u}\alpha\,a_\alpha a_\beta=(u-1)\,a_u$ (`Parking.cay_conv`) sums over the places of the erased cut. The difference of the two counts is the sum over the same pairs in which the chosen cut carries $1-f(s_i)$ in place of $f(s_i)$:
$$(q+1)(m-q)\,V_q(m;f)-q\,m\,V_{q+1}(m;f)=\sum_{c}\ \sum_{i=1}^{q}\omega_i(c)\,\bigl(1-f(s_i)\bigr)\prod_{j=1}^{q+1}a_{t_j}\prod_{l\ne i}f(s_l),$$
the outer sum running over the compositions of $m$ with $q+1$ parts. Every factor on the right is nonnegative under the hypothesis. The lower bound $f\ge0$ is needed for the factors of the cuts that are not erased, the upper bound $f\le1$ for the erased one.

The upper bound cannot be dropped. For a constant profile $f=h>0$ each of the $q-1$ cuts carries the factor $h$, so $V_q(m;h)=h^{q-1}T_{m,q}$, and for $1\le q<m$ the inequality is equivalent to $h\le1$.

**The Lean form.** The hypothesis is asked only at the cut points $0<s<m$ (the set `Finset.Ioo 0 m`), which are the only values of $f$ on which $V_q(m;f)$ depends (`Parking.Vc_congr`). The numbers $q$ and $m$ are cast to real numbers and $m-q$ is a difference of real numbers. For $q\ge m$ both sides are $0$. The hypothesis $q\ge1$ serves to write $q=r+1$.

**Where it is used.** In the proof of `Parking.curv_ratio` it is applied to the threshold profile $s\mapsto y/(N-s)$ (`Parking.thr`) at parameters for which this profile takes values in $[0,1]$ at the cut points. Together with `Parking.Tq_ratio` it gives there the likelihood-ratio comparison with the birthday law, from which the third factorial moment of the number of parts is bounded by $D_m$ (`Parking.Dbirth`) times the second.

## Proof

The proof has three steps: a reduction to a profile that lies in $[0,1]$ at every position, the identity (E) of the proof of `Parking.Tq_ratio`, and the sign of each term of that identity. The Lean file writes $q=r+1$.

**Step 1: reduction.** Let $g(s)=f(s)$ for $0<s<m$ and $g(s)=0$ for all other $s$. Then $0\le g(s)\le1$ for every natural number $s$, and $V_q(m;g)=V_q(m;f)$ for every $q$ by `Parking.Vc_congr`, which says that $V_q(m;\cdot)$ depends on the profile only at the cut points $0<s<m$. It is therefore enough to prove the inequality for a profile with values in $[0,1]$ at every position, and we assume this of $f$ from now on. The reduction is needed because the matrix $F$ below has $f(0)$ and $f(m)$ among its diagonal entries, and the hypothesis says nothing about these two values.

**Step 2: the identity.** We use the matrix model of the proof of `Parking.Tq_ratio`. All matrices are real, with rows and columns indexed by the positions $0,\dots,m$; $a_0=0$. $G$ is the strictly upper triangular matrix with $G_{ij}=a_{j-i}$ for $i<j$; $F$ is the diagonal matrix with the entries $f(0),\dots,f(m)$; $X$ is the diagonal matrix with the entries $0,\dots,m$; $H=GX-XG$, so that $H_{ij}=(j-i)\,a_{j-i}$ for $i<j$ and $H_{ij}=0$ otherwise; $1$ is the identity matrix; and $W_{a,b}(C)$ denotes the entry $(0,m)$ of $(GF)^a\,C\,(FG)^b$, which is linear in $C$. The identity to be used is, for every profile $f$ and every $q\ge1$,
$$(q+1)(m-q)\,V_q(m;f)-q\,m\,V_{q+1}(m;f)=\sum_{p=0}^{q-1}\Bigl[(q-p)\,W_{p,q-1-p}\bigl(H(1-F)G\bigr)+(p+1)\,W_{p,q-1-p}\bigl(G(1-F)H\bigr)\Bigr].\tag{E}$$
The term of index $p$ on the right is the part of the sum over pairs displayed in the explanation in which the erased cut is the cut $s_{p+1}$. The identity is derived, with more comment, in the record of `Parking.Tq_ratio`; the derivation is repeated here in brief so that this proof can be checked by itself.

- (B) For every $q\ge0$ and every position $x$, the entry $(0,x)$ of $G(FG)^q$ is $V_{q+1}(x;f)$. This is an induction on $q$: $G_{0x}=a_x=V_1(x;f)$ (`Parking.Vc_one`), and the entry $(0,x)$ of $G(FG)^q\,FG$ is $\sum_{u<x}V_{q+1}(u;f)\,f(u)\,a_{x-u}$, in which the term $u=0$ vanishes (`Parking.Vc_eq_zero_of_lt`) and the rest is the recursion `Parking.Vc_succ_succ`. Since $(GF)^aG(FG)^b=G(FG)^{a+b}$, it follows that $W_{a,b}(G)=V_{a+b+1}(m;f)$. From the definition, $W_{a,b}(C\,FG)=W_{a,b+1}(C)$ and $W_{a,b}(GF\,C)=W_{a+1,b}(C)$.
- (L1) For every $q\ge0$, $\sum_{p=0}^{q}W_{p,q-p}(H)=m\,V_{q+1}(m;f)$. Since $X$ commutes with $F$, the map $A\mapsto AX-XA$ is a derivation that vanishes on $F$; applied to $G(FG)^q$ it gives $G(FG)^qX-XG(FG)^q=\sum_{p=0}^{q}(GF)^p\,H\,(FG)^{q-p}$, and by (B) the entry $(0,m)$ of the left side is $(m-0)\,V_{q+1}(m;f)$.
- (F) $HG=GH=H-G$. For $i<j$ and $t=j-i$, the entry $(i,j)$ of $HG$ is $\sum_{\alpha=1}^{t-1}\alpha\,a_\alpha a_{t-\alpha}$ and that of $GH$ is the same sum with $\alpha$ replaced by $t-\alpha$; both equal $(t-1)\,a_t=H_{ij}-G_{ij}$ by `Parking.cay_conv`. The other entries are $0$.
- (E1) $\sum_{p=0}^{q-1}\bigl[(q-p)\,W_{p,q-1-p}(HG)+(p+1)\,W_{p,q-1-p}(GH)\bigr]=(q+1)(m-q)\,V_q(m;f)$. By (F) the bracket is $(q+1)\bigl(W_{p,q-1-p}(H)-V_q(m;f)\bigr)$, and the sum over the $q$ values of $p$ is $(q+1)(m-q)\,V_q(m;f)$ by (L1) with $q-1$ in place of $q$.
- (S) $\sum_{p=0}^{q-1}\bigl[(q-p)\,W_{p,q-p}(H)+(p+1)\,W_{p+1,q-1-p}(H)\bigr]=q\,m\,V_{q+1}(m;f)$. After replacing $p+1$ by $p$ in the second family, the word $W_{p,q-p}(H)$, $0\le p\le q$, has the total coefficient $(q-p)+p=q$, and (L1) applies.

Now $H(1-F)G=HG-HFG$ and $G(1-F)H=GH-GFH$, so $W_{p,q-1-p}(H(1-F)G)=W_{p,q-1-p}(HG)-W_{p,q-p}(H)$ and $W_{p,q-1-p}(G(1-F)H)=W_{p,q-1-p}(GH)-W_{p+1,q-1-p}(H)$. Hence the right side of (E) is the left side of (E1) minus the left side of (S), which is (E).

**Step 3: the sign.** The matrices $G$ and $H$ have nonnegative entries because $a_p\ge0$ (`Parking.cay_nonneg`), and $F$ and $1-F$ have nonnegative entries because $0\le f\le1$ at every position. A product of matrices with nonnegative entries has nonnegative entries, so $(GF)^a$, $(FG)^b$, $H(1-F)G$ and $G(1-F)H$ do, and every $W_{p,q-1-p}(\cdot)$ on the right of (E) is nonnegative. The coefficients $q-p$ and $p+1$ are positive for $0\le p\le q-1$. Hence the right side of (E) is nonnegative, which is the inequality of the statement.
