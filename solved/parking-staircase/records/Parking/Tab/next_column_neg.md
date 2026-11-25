---
weight: unit
short: the next column is negative up to the positive row, columns 9 to 264
---
## Description

For every column $9\le k\le264$, with the listed number $z=z(k)$: the column $k+1$ is negative, $b(n,k+1)<b(n,k)$, in every row $k+2\le n\le k+z+1$. The last of these rows is the row in which the column $k$ is positive by the table of two signs. Established by evaluating exact values: these signs are the $5{,}934$ comparisons of one computed table.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ be an integer with $9\le k\le264$, and let $z(k)$ be the number listed for the column $k$ (`Parking.Tab.ztab`). Then for every $n$ with $k+2\le n\le k+z(k)+1$,
$$b(n,k+1)<b(n,k).$$

## Explanation

**What the statement says.** Write $d_{n,c}=b(n,c)-b(n,c-1)$ for the step of the column $c$ in the row $n$. The first layer of a column $c$ consists of the rows $c+1\le n\le2c-1$ (also called the chain range of the column). For $9\le k\le264$ the table of two signs `Parking.Tab.two_signs` shows that the column $k$ is positive in the row $q=k+z(k)+1$, and that $z(k)+2\le k$, so that $q\le2k-1$. The present statement says that the column $k+1$ is negative in every row from the first row $k+2$ of its first layer to that row $q$. In particular the column $k+1$ is still negative in a row in which the column $k$ is already positive, and it has no positive row among the rows of its first layer up to $q$. Read by the column $c=k+1$ in which the signs lie: for $10\le c\le265$ the column $c$ is negative in the rows $c+1\le n\le c+z(c-1)$.

**What it is used for.** It gives the diagonal rule, by which a step that is not positive is followed by a negative step one row down and one column to the right, in the first layer of the columns $9\le k\le264$ (`Parking.diagonal_rule_small`). A step of the column $k$ that is not positive, in a row $n$ of the first layer, can only lie in a row $n<q$, because the positive sign of the row $q$ persists in the later rows of the layer. The rule then asks for $d_{n+1,k+1}<0$, and $n+1$ is one of the rows $k+2,\dots,q$.

**Why the signs are computed.** The table of two signs contains one of these signs: its third part is $d_{k+z,k+1}<0$, the row before the last. The others do not follow from it by what is known about the first layer. The persistence of the sign in the first layer passes a positive step on to the later rows of the layer. Applied to the column $k+1$ and the negative step of the row $k+z$, it shows that the steps of the earlier rows are not positive, since a positive one would have persisted; it does not show that they are negative, because it says nothing about a step equal to zero, and it gives nothing for the row $k+z+1$. The diagonal rule needs the strict sign in every one of these rows. So each sign is computed: $\sum_{k=9}^{264}z(k)=5{,}934$ cells in the rows up to $300$.

**Why the numbers are computed by the forward recursion.** The table of the columns up to $81$ and the junction table compute the numbers $A(n,l)$ of parking functions of length $n$ with maximum displacement at most $l$ by the last-car recursion, which has to start from the row $0$ for every level. Here the columns go up to $265$ and the rows up to $300$, but every cell lies in the first layer of its column. For a threshold $y$ the numbers $U_y(n)=(n+1)^{n-1}-A(n,y-1)$ satisfy on the rows $y\le n\le2y+1$ a linear recursion in $n$, the forward form of the single-chain formula, which starts at the row $y$ with the value $0$. The table of two signs computes with it for the same reason, and the present table uses the same functions.

**The Lean form.** The sign is the comparison `b n (k + 1) < b n k` of natural numbers, and the rows are given by the hypotheses `k + 2 ≤ n` and `n ≤ k + ztab k + 1`. The table from which the statement is read is indexed by the column $c=k+1$ in which the signs lie: for $10\le c\le265$ the column $c$ is negative in the rows $c+1\le n\le c+z(c-1)$. The corresponding signs of the columns $3\le c\le9$, in the rows $c+1\le n\le2c-2$, are not part of this table; they are cells of `Parking.Tab.negative_cells`, which computes its numbers by the last-car recursion. The functions that compute the numbers are private definitions of the module of the table of two signs, which the present module opens; the list of a whole column and the check are its own.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means. The computation is one table for the columns $10\le c\le265$, where $c=k+1$ is the column in which the signs lie.

**The numbers.** Let $A(n,l)$ be the number of parking functions of length $n$ with maximum displacement at most $l$ (`Parking.A`). Put $P(n)=(n+1)^{n-1}$ for $n\ge1$ and $P(0)=1$, and for $y\ge1$
$$U_y(n)=P(n)-A(n,y-1),\qquad W_y(t)=(t-y)\,P(t-1)+y\,U_y(t-1)\quad(t\ge y+1).$$
The subtraction is exact, $A(n,y-1)\le P(n)$: by `Parking.A_mono`, $A(n,y-1)\le A(n,l)$ for $l\ge\max(y-1,n)$, and $A(n,l)=P(n)$ for $n\le l+1$ by `Parking.A_eq_pow`. So
$$U_y(n)+A(n,y-1)=P(n).\tag{1}$$
$U_y(n)$ is the number of parking functions of length $n$ in which some displacement is at least $y$.

**The forward recursion.** For $y\ge1$ and $n\le2y+1$,
$$U_y(n)=\sum_{t=y+1}^{n}\binom nt\,P(n-t)\,W_y(t).\tag{2}$$
For $n\le y$ the sum is empty and $U_y(n)=0$. To prove (2), let $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). The sequence $z^{(y)}$ solves the weighted last-car recursion with the weight $\min(t,y)$ (`Parking.zr_isWSol`), and this weight equals $t$ for $1\le t\le y$ and $y$ for $t\ge y+1$. So the forward form of the single-chain formula, `Parking.IsWSol.fwd`, applies. It is stated with the numbers $(m+1)^{m-1}/m!$ (`Parking.cc`), which are $P(m)/m!$, and gives for $n\le2y+1$
$$\frac{P(n)}{n!}-z^{(y)}_n=\sum_{t=y+1}^{n}\frac{P(n-t)}{(n-t)!}\Bigl(\frac{P(t-1)}{(t-1)!}-\frac yt\,z^{(y)}_{t-1}\Bigr).$$
(In the library the identification of those numbers with $P(m)/m!$ goes through `Parking.zr_eq_cc` and `Parking.A_eq_pow`: they equal $z^{(m+1)}_m=A(m,m)/m!$, and $A(m,m)=P(m)$.) Multiply by $n!$. The left-hand side becomes $P(n)-A(n,y-1)=U_y(n)$. In the term of index $t$, $n!/((n-t)!\,(t-1)!)=t\binom nt$, so the term becomes $\binom nt\,P(n-t)\,\bigl(t\,P(t-1)-y\,A(t-1,y-1)\bigr)$, and $t\,P(t-1)-y\,A(t-1,y-1)=(t-y)\,P(t-1)+y\,U_y(t-1)=W_y(t)$ by (1). This is an identity between real numbers whose two sides are natural numbers, hence (2).

**One row of the computation.** For a row $n$ and a list $[w_0,w_1,\dots,w_{m-1}]$ of natural numbers the computation forms
$$\sum_{j=0}^{m-1}g_j\,P(j)\,w_j,\qquad g_0=1,\quad g_{j+1}=\Bigl\lfloor\frac{g_j\,(n-j)}{j+1}\Bigr\rfloor .$$
The numbers $g_j$ are the binomial coefficients $\binom nj$, because $\binom nj(n-j)=\binom n{j+1}(j+1)$ makes the division exact; that the function returns $\sum_j\binom njP(j)\,w_j$ is proved by induction along the list. Apply it at the row $n=y+m$ to the list of weights $[W_y(n),W_y(n-1),\dots,W_y(y+1)]$, that is, $w_j=W_y(n-j)$. With $t=n-j$ and $\binom nj=\binom nt$ the sum is the right-hand side of (2). Hence, as long as $n\le2y+1$, one row of the computation applied to the list of the weights returns $U_y(n)$. For $m=0$ the list is empty and the value is $0=U_y(y)$.

**The list of a column.** For a threshold $y\ge1$ the computation runs through the rows $n=y,y+1,\dots,2y+1$, starting at the row $y$ with the empty list. At a row $n$ it computes the value $u$ of the previous paragraph from its list, records $u$, puts the number $(n+1-y)\,P(n)+y\,u$ in front of the list, and passes to the row $n+1$. By induction on the row, the list held at the row $n$ is $[W_y(n),\dots,W_y(y+1)]$ and the value recorded is $U_y(n)$: if this holds at a row $n\le2y+1$, then $u=U_y(n)$ by the previous paragraph, and the number put in front is $(n+1-y)\,P(n)+y\,U_y(n)=W_y(n+1)$ by the definition of $W_y$. So the recorded values form the list
$$L_y=[\,U_y(y),\,U_y(y+1),\,\dots,\,U_y(2y+1)\,],$$
in which the number of the row $n$ stands at the position $n-y$, for every $y\le n\le2y+1$. All arithmetic is that of natural numbers of arbitrary size and is exact. (As an indication of the sizes, from a computation made for this record outside the library: $P(300)$ has $742$ decimal digits.)

**The check of a column.** For a column $c$ and a number $r$ of rows the computation forms the lists $L_{c-1}$, $L_c$, $L_{c+1}$ and evaluates the conjunction of the comparison $r+1\le c$ and, for each $i$ with $0\le i<r$, of
$$2\,L_c[i+1]\ <\ L_{c+1}[i]+L_{c-1}[i+2],$$
where $L[j]$ is the entry of $L$ at the position $j$ (`Parking.Tab.nth`). The three entries belong to the row $n=c+1+i$, whose positions in the three lists are $n-c$, $n-(c+1)$ and $n-(c-1)$. Suppose $c\ge2$ and the value is true. For $c+1\le n\le c+r$ the row $n$ lies in the range $y\le n\le2y+1$ of each of the thresholds $y=c-1,c,c+1$: the lower bounds hold because $n\ge c+1$, and the upper bounds because $n\le c+r\le2c-1=2(c-1)+1$, which is where the condition $r+1\le c$ is needed. So the three entries are $U_c(n)$, $U_{c+1}(n)$ and $U_{c-1}(n)$, and the check says
$$2\,U_c(n)<U_{c+1}(n)+U_{c-1}(n)\qquad\text{for } c+1\le n\le c+r .\tag{3}$$

**What the check means.** Let $c\ge2$. By (1), the three numbers $U_c(n)$, $U_{c+1}(n)$, $U_{c-1}(n)$ of (3) are $P(n)-A(n,c-1)$, $P(n)-A(n,c)$ and $P(n)-A(n,c-2)$. By `Parking.b_succ_add_A`, $b(n,c)+A(n,c-1)=A(n,c)$ and $b(n,c-1)+A(n,c-2)=A(n,c-1)$. Therefore
$$b(n,c)-b(n,c-1)=A(n,c)-2A(n,c-1)+A(n,c-2)=2\,U_c(n)-U_{c+1}(n)-U_{c-1}(n),$$
and (3) gives $b(n,c)<b(n,c-1)$ for $c+1\le n\le c+r$.

**The evaluation.** For each column $10\le c\le265$ the check is formed with $r=z(c-1)$, the number listed for the column $c-1$ (`Parking.Tab.ztab`), which is read from the list `Parking.Tab.zs`. The $256$ columns are evaluated in sixteen blocks of consecutive columns: $10$–$24$, then fourteen blocks of sixteen columns beginning at $c=25,41,\dots,233$, and $249$–$265$. For each block the kernel reduces the conjunction of the checks of its columns (`Parking.Tab.allRange`) to true. In all $\sum_{c=10}^{265}z(c-1)=5{,}934$ comparisons (3) are evaluated, in the rows up to $300$. Each check forms its three lists anew, so the list of a threshold is formed once for each of the columns whose check reads it. The list $L_y$ is defined with all its rows $y\le n\le2y+1$, but a check reads its entries up to the row $c+r$ only, and the largest such row is $300$; the entries of later rows play no part in the result. (The module remarks that the kernel does not compute an entry that no comparison reads.) No compiled code and no external program is involved: the definitions are part of the Lean source, and the evaluation is a step of the type checking of that source. `Parking.Tab.allRange_sound` gives the value true for the check of each column of a block, and `Parking.Tab.glue` joins the sixteen ranges to $10\le c<266$. Every column $c\ge10$ satisfies $c\ge2$, so the meaning of the check applies, and this is the table: for $10\le c\le265$,
$$b(n,c)<b(n,c-1)\qquad\text{for } c+1\le n\le c+z(c-1).\tag{4}$$

**Conclusion.** Let $9\le k\le264$ and $k+2\le n\le k+z(k)+1$. Put $c=k+1$. Then $10\le c\le265$, $z(c-1)=z(k)$, and $c+1\le n\le c+z(c-1)$. By (4), $b(n,k+1)<b(n,k)$.
