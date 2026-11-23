---
weight: unit
short: midpoint comparison for the threshold profile
---
## Description

For the cut profile $s\mapsto1/(N-s)$ with $N>m$, the total weights $V_q$ and $V_{q+1}$ of the compositions of $m$ with $q$ and with $q+1$ parts satisfy $(q+1)(m-q)\,V_q\le q\,m\,(N-\tfrac m2)\,V_{q+1}$ for every $q\ge1$: the ratio $V_{q+1}/V_q$ is at least its value for the constant profile equal to the threshold profile at the midpoint $m/2$.

## Statement

Let $a_p=p^{p-1}/p!$ for $p\ge1$ (`Parking.cay`). For a cut profile $f:\mathbb N\to\mathbb R$ and natural numbers $m$ and $q$, let $V_q(m;f)$ (`Parking.Vc`) be the total weight of the compositions of $m$ with $q$ parts, where the weight of a composition with part sizes $p_1,\dots,p_q$ and cut points $s_j=p_1+\dots+p_j$, $1\le j\le q-1$, is $a_{p_1}\cdots a_{p_q}\,f(s_1)\cdots f(s_{q-1})$. For a real number $N$ let $\lambda^{1,N}$ be the threshold profile $s\mapsto1/(N-s)$ (`Parking.thr` with the parameter $y=1$).

Let $m$ be a natural number and $N$ a real number with $m<N$. Then for every natural number $q\ge1$,
$$(q+1)(m-q)\,V_q(m;\lambda^{1,N})\le q\,m\,\Bigl(N-\frac m2\Bigr)\,V_{q+1}(m;\lambda^{1,N}).$$

## Explanation

**What the inequality says.** When every cut has the factor $1$, $q\,m\,T_{m,q+1}=(q+1)(m-q)\,T_{m,q}$ with $T_{m,q}=V_q(m;1)$ (`Parking.Tq_ratio`). For a constant profile $h>0$ each of the $q-1$ cuts carries the factor $h$, so $V_q(m;h)=h^{q-1}T_{m,q}$ and the ratio $V_{q+1}/V_q$ is $h$ times the ratio $T_{m,q+1}/T_{m,q}$. The statement says that for the threshold profile the ratio $V_{q+1}/V_q$ is at least the ratio for the constant profile $h=1/(N-\frac m2)$, which is the value that the formula $1/(N-s)$ takes at the midpoint $s=\frac m2$ of the segment that is cut. The cut points lie in $1\le s\le m-1$ and the profile increases with $s$, so the erasure rule described below gives at once the same comparison with the constant $1/(N-1)$, the smallest value of the profile at a cut point; the content of the statement is that this smallest value can be replaced by the larger value at the midpoint. For the threshold profile $\lambda^{y,N}:s\mapsto y/(N-s)$ with $y>0$ the same holds with $h=y/(N-\frac m2)$, since $V_q(m;\lambda^{y,N})=y^{q-1}V_q(m;\lambda^{1,N})$ (`Parking.Vc_thr`).

**Why it holds.** The statement is the third use of the erasure rule explained in the record of `Parking.Tq_ratio`. One counts the pairs formed by a composition $c$ of $m$ with $q+1$ parts and one of its cuts $s_i$, with the multiplicity $\omega_i(c)=(q+1-i)\,t_i+i\,t_{i+1}$, where $t_1,\dots,t_{q+1}$ are the part sizes of $c$; the multiplicities of the $q$ cuts of $c$ add up to $q\,m$. Counted with the weight of $c$ from which the factor of the chosen cut has been removed, the pairs weigh $(q+1)(m-q)\,V_q$. For the threshold profile, removing the factor $1/(N-s_i)$ is the same as multiplying by $N-s_i$. Hence
$$(q+1)(m-q)\,V_q=q\,m\,(N-\hat s)\,V_{q+1},$$
where, for $q<m$, $\hat s$ is the mean position of the chosen cut when the pair $(c,s_i)$ is drawn with probability proportional to $\omega_i(c)$ times the weight of $c$. For $q<m$ the statement is $\hat s\ge\frac m2$: the erased cut lies, on average, in the right half of the segment. For $q\ge m$ there is no composition with $q+1$ parts and the statement is trivial.

The position of the chosen cut is tied to the sizes of the parts. For a fixed composition, $\sum_i\omega_i(c)\,s_i-\frac m2\sum_i\omega_i(c)=\frac12\sum_{j=1}^{q+1}(q+2-2j)\,t_j^2$; this is the algebra of steps 2 and 3 of the proof, read for one composition. The right side is positive when the early parts are the long ones. So the statement follows once the total weight $\beta_p$ of the compositions with $q+1$ parts, each counted with the square of the size of its part number $p+1$, does not increase with $p$. This is the step of the proof at which the argument could fail, and it is where the form of the profile enters. Fix all the cuts except the one between the parts number $p+1$ and $p+2$, and reflect that cut about the midpoint of the interval that the two parts fill. The reflection exchanges the two sizes, leaves the product of the part weights unchanged, and changes only the factor of that cut. Since $1/(N-s)$ increases with $s$, of the two reflected positions the one further to the right has the larger factor, and that is the position in which the left part is the longer one. Summed over the two reflected positions, and then over all positions of that cut, the square of the left part therefore weighs at least as much as the square of the right part.

The proof gives the difference of the two sides exactly: $q\,m\,(N-\frac m2)\,V_{q+1}-(q+1)(m-q)\,V_q=\frac12\sum_{p=0}^{q}(q-2p)\,\beta_p$. Of the profile it uses only that $f(s)\,(N-s)=1$ and that $f$ is nonnegative and nondecreasing on the positions $0,\dots,m$.

**The hypotheses and the Lean form.** The hypothesis $m<N$ makes $N-s$ positive at all the positions $0,\dots,m$ of the matrix model of the proof, the two ends included, although $V_q(m;\cdot)$ depends on the profile only at the cut points $0<s<m$. In Lean, $N$ is a real number, the profile is `Parking.thr 1 N`, the numbers $q$ and $m$ are cast to real numbers, and $m-q$ and $N-\frac m2$ are real expressions. For $q\ge m$ the left side is $0$ and the right side is nonnegative. The hypothesis $q\ge1$ serves to write $q=r+1$.

**Where it is used.** In the proof of `Parking.Lam_raise`, with $m=r$, $N=k+r+1$ and the profile $\lambda^{k,N}$. Combined with `Parking.Tq_ratio` it shows there that the law of the number of parts under the threshold profile dominates, in likelihood-ratio order, the law for the constant profile $h_{\mathrm{mid}}=k/(N-\frac r2)$; from this comparison and Jensen's inequality, `Parking.Lam_raise` bounds the total weight $\Lambda_r(k+2;N)$ of all compositions of $r$ under the profile $\lambda^{k+2,N}$ (`Parking.Lam`) from below by $(1+\frac2k)^{\mu}\,\Lambda_r(k;N)$, where $\mu$ is the mean number of cuts under the constant profile $h_{\mathrm{mid}}$ (`Parking.muh`).

## Proof

Write $f=\lambda^{1,N}$, so $f(s)=1/(N-s)$, and $V_q=V_q(m;f)$. The proof inserts the relation $(N-s)\,f(s)=1$ at the erased cut of the erasure identity of the proof of `Parking.Tq_ratio`, which expresses the difference of the two sides of the statement as a weighted sum of the numbers $\beta_p$ (steps 1 to 3), and then shows that this sum is nonnegative because $\beta_p$ does not increase with $p$ (steps 4 and 5). The Lean file writes $q=r+1$.

**Notation and the facts taken from the proof of `Parking.Tq_ratio`.** All matrices are real, with rows and columns indexed by the positions $0,\dots,m$; $a_0=0$. $G$ is the strictly upper triangular matrix with $G_{ij}=a_{j-i}$ for $i<j$; $F$ is the diagonal matrix with the entries $f(0),\dots,f(m)$; $X$ is the diagonal matrix with the entries $0,\dots,m$; $H=GX-XG$, so $H_{ij}=(j-i)\,a_{j-i}$ for $i<j$; and $W_{a,b}(C)$ is the entry $(0,m)$ of $(GF)^a\,C\,(FG)^b$. The map $W_{a,b}$ is linear, and from the definition $W_{a,b}(C\,FG)=W_{a,b+1}(C)$ and $W_{a,b}(GF\,C)=W_{a+1,b}(C)$. The following facts hold for every profile. They are derived, with more comment, in the record of `Parking.Tq_ratio`; the derivations are repeated here in brief so that this proof can be checked by itself.

- (B) For every $q\ge0$ and every position $x$, the entry $(0,x)$ of $G(FG)^q$ is $V_{q+1}(x;f)$. This is an induction on $q$: $G_{0x}=a_x=V_1(x;f)$ (`Parking.Vc_one`), and the entry $(0,x)$ of $G(FG)^q\,FG$ is $\sum_{u<x}V_{q+1}(u;f)\,f(u)\,a_{x-u}$, in which the term $u=0$ vanishes (`Parking.Vc_eq_zero_of_lt`) and the rest is the recursion `Parking.Vc_succ_succ`. Since $(GF)^aG(FG)^b=G(FG)^{a+b}$, it follows that $W_{a,b}(G)=V_{a+b+1}$.
- (L) For a diagonal matrix $Z$ with the entries $z(0),\dots,z(m)$ and every $q\ge0$: $\sum_{p=0}^{q}W_{p,q-p}(GZ-ZG)=(z(m)-z(0))\,V_{q+1}$. Since $Z$ commutes with $F$, the map $A\mapsto AZ-ZA$ is a derivation that vanishes on $F$; applied to $G(FG)^q$ it gives $G(FG)^qZ-ZG(FG)^q=\sum_{p=0}^{q}(GF)^p\,(GZ-ZG)\,(FG)^{q-p}$, and by (B) the entry $(0,m)$ of the left side is $(z(m)-z(0))\,V_{q+1}$. For $Z=X$ it reads $\sum_{p=0}^{q}W_{p,q-p}(H)=m\,V_{q+1}$ (L1).
- (F) $HG=GH=H-G$. For $i<j$ and $t=j-i$, the entry $(i,j)$ of $HG$ is $\sum_{\alpha=1}^{t-1}\alpha\,a_\alpha a_{t-\alpha}$ and that of $GH$ is the same sum with $\alpha$ replaced by $t-\alpha$; both equal $(t-1)\,a_t=H_{ij}-G_{ij}$ by `Parking.cay_conv`. The other entries are $0$.
- (E1) For every $q\ge1$: $\sum_{p=0}^{q-1}\bigl[(q-p)\,W_{p,q-1-p}(HG)+(p+1)\,W_{p,q-1-p}(GH)\bigr]=(q+1)(m-q)\,V_q$. By (F) the bracket is $(q+1)\bigl(W_{p,q-1-p}(H)-V_q\bigr)$, and the sum over the $q$ values of $p$ is $(q+1)(m-q)\,V_q$ by (L1) with $q-1$ in place of $q$.
- (S) For every $q\ge1$: $\sum_{p=0}^{q-1}\bigl[(q-p)\,W_{p,q-p}(H)+(p+1)\,W_{p+1,q-1-p}(H)\bigr]=q\,m\,V_{q+1}$. After replacing $p+1$ by $p$ in the second family, the word $W_{p,q-p}(H)$, $0\le p\le q$, has the total coefficient $(q-p)+p=q$, and (L1) applies.

**Properties of the profile.** For every position $s\le m$ we have $N-s>0$, since $m<N$. Hence $f(s)>0$ at these positions (`Parking.thr_nonneg`), $f(a)\le f(b)$ for positions $a\le b\le m$, and $N\,f(s)-f(s)\,s=1$, that is, $NF-FX=1$ with the identity matrix on the right. Diagonal matrices commute, so $FX=XF$.

**Step 1: inserting $1=NF-FX$ at the erased cut.** We have $HG=H\,(NF-FX)\,G=N\,HFG-(HX)\,FG$ and $GH=G\,(NF-FX)\,H=N\,GFH-GF\,(XH)$. By linearity and the absorption rules,
$$W_{p,q-1-p}(HG)=N\,W_{p,q-p}(H)-W_{p,q-p}(HX),\qquad W_{p,q-1-p}(GH)=N\,W_{p+1,q-1-p}(H)-W_{p+1,q-1-p}(XH).$$
Substituting into (E1) and using (S) for the terms with the factor $N$ gives
$$(q+1)(m-q)\,V_q=N\,q\,m\,V_{q+1}-B,\qquad B=\sum_{p=0}^{q-1}\Bigl[(q-p)\,W_{p,q-p}(HX)+(p+1)\,W_{p+1,q-1-p}(XH)\Bigr].$$
In $W_{p,q-p}(HX)$ the marked part, number $p+1$, is weighted by its size and by the position of its right end, and in $W_{p,q-p}(XH)$ by its size and by the position of its left end; so $B$ is the sum over the pairs of the explanation of the position of the chosen cut, and $B=q\,m\,\hat s\,V_{q+1}$.

**Step 2: regrouping by the marked part.** Replacing $p+1$ by $p$ in the second family, as in (S),
$$B=\sum_{p=0}^{q}\Bigl[(q-p)\,W_{p,q-p}(HX)+p\,W_{p,q-p}(XH)\Bigr].$$

**Step 3: the symmetric and the antisymmetric part.** Let $K=HX-XH$, so that $K_{ij}=(j-i)^2a_{j-i}$ for $i<j$ and $K_{ij}=0$ otherwise. Then $HX=\frac12(HX+XH)+\frac12K$ and $XH=\frac12(HX+XH)-\frac12K$, hence $(q-p)\,HX+p\,XH=\frac q2\,(HX+XH)+\frac{q-2p}{2}\,K$. Moreover $HX+XH=GX^2-X^2G$, so (L) with $Z=X^2$, that is $z(s)=s^2$, gives $\sum_{p=0}^{q}W_{p,q-p}(HX+XH)=m^2\,V_{q+1}$. With
$$\beta_p=W_{p,q-p}(K)\qquad(0\le p\le q),$$
the total weight of the compositions of $m$ with $q+1$ parts in which the part number $p+1$ is counted with the square of its size, we get $B=\frac q2\,m^2\,V_{q+1}+\frac12\sum_{p=0}^{q}(q-2p)\,\beta_p$, and with step 1
$$q\,m\,\Bigl(N-\frac m2\Bigr)V_{q+1}-(q+1)(m-q)\,V_q=\frac12\sum_{p=0}^{q}(q-2p)\,\beta_p.$$
It remains to show that the sum on the right is nonnegative. Its weights $q-2p$ are positive for the early parts and negative for the late ones, and they add up to $0$.

**Step 4: summation by parts.** For every sequence $\beta_0,\dots,\beta_q$,
$$\sum_{p=0}^{q}(q-2p)\,\beta_p=\sum_{k=0}^{q-1}(k+1)(q-k)\,(\beta_k-\beta_{k+1}),$$
because $\beta_k$ has the coefficient $(k+1)(q-k)-k(q-k+1)=q-2k$ on the right, also for $k=0$ and for $k=q$ (in Lean, an induction on the upper limit with a boundary term that vanishes at the limit $q$). The coefficients $(k+1)(q-k)$ are positive. So it is enough to prove $\beta_{p+1}\le\beta_p$ for $0\le p<q$.

**Step 5: $\beta_p$ does not increase.** By the absorption rules, $\beta_p=W_{p,q-1-p}(K\,FG)$ and $\beta_{p+1}=W_{p,q-1-p}(GF\,K)$, so
$$\beta_p-\beta_{p+1}=W_{p,q-1-p}\bigl(KFG-GFK\bigr).$$
The matrices $G$ and $F$ have nonnegative entries, because $a_p\ge0$ (`Parking.cay_nonneg`) and $f>0$ at the positions $0,\dots,m$; hence so do $(GF)^p$ and $(FG)^{q-1-p}$, and it is enough to show that every entry of $KFG-GFK$ is nonnegative. The matrix is strictly upper triangular. For $i<j$ put $t=j-i$. Summing over the middle position $i+\alpha$,
$$(KFG-GFK)_{ij}=\sum_{\alpha=0}^{t}\ell(\alpha)\,w(\alpha),\qquad \ell(\alpha)=f(i+\alpha),\quad w(\alpha)=a_\alpha\,a_{t-\alpha}\,\bigl(\alpha^2-(t-\alpha)^2\bigr),$$
where the terms $\alpha=0$ and $\alpha=t$ are $0$ because $a_0=0$. The kernel $w$ is antisymmetric under the reflection $\alpha\mapsto t-\alpha$, that is $w(t-\alpha)=-w(\alpha)$, and $w(\alpha)\ge0$ when $\alpha\ge t-\alpha$. The weight $\ell$ is nondecreasing on $0\le\alpha\le t$, because $f$ is nondecreasing on the positions $i,\dots,j$, which are at most $m$. Reflecting the index of summation gives $\sum_\alpha\ell(t-\alpha)\,w(\alpha)=-\sum_\alpha\ell(\alpha)\,w(\alpha)$, hence
$$2\sum_{\alpha=0}^{t}\ell(\alpha)\,w(\alpha)=\sum_{\alpha=0}^{t}\bigl(\ell(\alpha)-\ell(t-\alpha)\bigr)\,w(\alpha).$$
Each term on the right is nonnegative: for $\alpha\ge t-\alpha$ both factors are nonnegative, and for $\alpha<t-\alpha$ both are nonpositive, the second because $w(\alpha)=-w(t-\alpha)$. So the entry is nonnegative. This is the reflection of one cut about the midpoint of the two parts next to it, described in the explanation.

Steps 3, 4 and 5 together give the inequality of the statement.
