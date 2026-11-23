---
weight: unit
short: the table of two signs for the columns 9 to 264
---
## Description

The two computed signs of each column $9\le k\le264$: with the listed number $z=z(k)$, which satisfies $z+2\le k$, the column $k$ is positive in the row $k+z+1$, $b(k+z+1,k-1)<b(k+z+1,k)$, and the column $k+1$ is negative in the row $k+z$, $b(k+z,k+1)<b(k+z,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ be an integer with $9\le k\le264$ and let $z=z(k)$ be the number listed for the column $k$ (`Parking.Tab.ztab`). Then

1. $z+2\le k$;
2. $b(k+z+1,\,k-1)<b(k+z+1,\,k)$;
3. $b(k+z,\,k+1)<b(k+z,\,k)$.

## Explanation

**The two signs.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. Part 2 says $d_{k+z+1,k}>0$ and part 3 says $d_{k+z,k+1}<0$: in two consecutive rows, the column $k$ has turned positive by the later one and the column $k+1$ is still negative in the earlier one. The chain range of a column $c$ consists of the rows $c+1\le n\le2c-1$. Part 1 gives $k+z+1\le2k-1$, so both rows lie below the upper ends of the chain ranges of their columns $k$ and $k+1$; they lie above the lower ends because every listed $z$ is at least $7$.

**Why two signs per column suffice.** The statement on the next column (`Parking.mono`) says, for $n\ge k+2$: if $d_{j,k}\le0$ for all $k+1\le j\le n$, then $d_{n,k+1}\le0$. Taken literally it concerns every row $n$. For $9\le k\le264$ it follows from the two signs and from the persistence of the sign in the chain range (`Parking.chain_column_iter`). By part 2 the hypothesis fails for $n\ge k+z+1$, so only the rows $n\le k+z$ remain. If $d_{n,k+1}$ were positive for such an $n$, persistence for the column $k+1$ would give $d_{k+z,k+1}>0$, against part 3. Without persistence one would have to compute the sign of the column $k+1$ in each of the rows $k+2,\dots,k+z$.

Part 2 has a second use. For $82\le k\le264$ it is the positive row from which the analytic arguments for the columns $k\ge82$ start (`Parking.crossing_row`), together with the bound `Parking.Tab.ztab_27`. For the columns $k\ge265$ both uses are taken over by theorems (`Parking.crossing_strip`, `Parking.mono265`); the table ends at $264$ because those theorems are proved from $265$ on.

**Why this table computes differently from the table of the columns $k\le81$.** Here the columns go up to $264$ and the rows up to $300$, but only two positions per column are needed, both in the chain range of their column. For a single threshold $y$, which stands for the condition that all displacements are smaller than $y$, the numbers $A(n,y-1)$ satisfy on the rows $y+1\le n\le2y+1$ a linear recursion, the forward form of the single-chain formula (`Parking.IsWSol.fwd`). It produces these rows without computing the rows $n\le y$: there the count is $(n+1)^{n-1}$. The table uses this recursion and not the last-car recursion, which would have to start from the row $0$.

**The Lean form.** The signs are comparisons of natural numbers; `k - 1` is exact. For $k=9$ the listed number is $z=7$, so $z+2=k$ and part 1 holds with equality. An exact computation made for this record, outside the library, found that for $2\le k\le8$ the column $k$ has no positive row in its chain range (its first positive rows are $6,8,10,12,13,15,16$), which is why a table of this kind starts at the column $9$; this is not a statement of the library.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means.

**The numbers computed.** Put $P(n)=(n+1)^{n-1}$ (with $P(0)=1$), the number of parking functions of length $n$; in the library it enters as the value of $A(n,l)$ for $n\le l+1$ (`Parking.A_eq_pow`). For $y\ge1$ put
$$U_y(n)=P(n)-A(n,y-1),\qquad W_y(t)=(t-y)\,P(t-1)+y\,U_y(t-1),$$
where $A(n,l)$ is the number of parking functions of length $n$ with maximum displacement at most $l$ (`Parking.A`). $U_y(n)$ is the number of parking functions of length $n$ in which some displacement is at least $y$. The subtraction is exact because $A(n,y-1)\le P(n)$: by `Parking.A_mono`, $A(n,y-1)\le A(n,l)$ for a large $l$, and $A(n,l)=P(n)$ for $n\le l+1$ by `Parking.A_eq_pow`. The same fact gives $U_y(n)=0$ for $n\le y$.

**The recursion.** For $y\ge1$ and $n\le2y+1$,
$$U_y(n)=\sum_{t=y+1}^{n}\binom nt\,P(n-t)\,W_y(t).\tag{1}$$
This is the forward form of the single-chain formula in natural numbers. `Parking.IsWSol.fwd`, applied to the sequence $z^{(y)}_n=A(n,y-1)/n!$, which solves the weighted last-car recursion with the weight $\min(t,y)$ (`Parking.zr_isWSol`), states for $n\le2y+1$
$$c_n-z^{(y)}_n=\sum_{t=y+1}^{n}c_{n-t}\Bigl(c_{t-1}-\frac yt\,z^{(y)}_{t-1}\Bigr),\qquad c_m=\frac{P(m)}{m!}.$$
Multiplying by $n!$ and using $n!/((n-t)!\,(t-1)!)=t\binom nt$ turns the term of index $t$ into $\binom nt P(n-t)\bigl(t\,P(t-1)-y\,A(t-1,y-1)\bigr)$, and $t\,P(t-1)-y\,A(t-1,y-1)=(t-y)P(t-1)+y\,U_y(t-1)=W_y(t)$.

**What is computed.** For a threshold $y$ the computation produces the list $U_y(y+1),U_y(y+2),\dots,U_y(y+c)$ of a given length $c$, row by row. It keeps the list of the values $W_y(n),W_y(n-1),\dots,W_y(y+1)$, which at the first row $n=y+1$ consists of $W_y(y+1)=P(y)$ alone. At a row $n$ it computes the sum $\sum_{j\ge0}\binom nj P(j)\,W_y(n-j)$ over this list, the binomial coefficients being carried along as a running product with an exact division; by $\binom nj=\binom n{n-j}$ this is the right-hand side of (1), hence $U_y(n)$. It then puts $W_y(n+1)=(n+1-y)P(n)+y\,U_y(n)$ in front of the list and goes on to the row $n+1$. By induction on the row, using (1), the list produced is the list of the numbers $U_y$ as long as the rows stay within $n\le2y+1$, that is, for $c\le y+1$. All arithmetic is that of natural numbers of arbitrary size and is exact. (As an indication of the sizes, not a statement of the library: the numbers $P(n)$ that occur have up to about $740$ decimal digits.)

**The check of a column.** For $k$ and $z$ the computation forms the lists of the thresholds $k-1$, $k$, $k+1$, $k+2$ of the lengths $z+2$, $z+1$, $z$, $z-2$, reads from them the values at the rows $q=k+z+1$ and $n=k+z$, and evaluates the conjunction of
$$2\le z,\qquad z+2\le k,\qquad U_{k+1}(q)+U_{k-1}(q)<2\,U_k(q),\qquad 2\,U_{k+1}(n)<U_{k+2}(n)+U_k(n).$$
The lengths satisfy the condition $c\le y+1$; for the threshold $k-1$ this is $z+2\le k$, which is how part 1 enters. For the threshold $k+2$ the list starts at the row $k+3$, and when $z=2$ the value needed is $U_{k+2}(k+2)=0$, which the computation supplies by putting a $0$ in front of the list.

**What the check means.** For $c\ge2$, `Parking.d_eq_A` gives $d_{n,c}=A(n,c)-2A(n,c-1)+A(n,c-2)$, hence
$$d_{n,c}=2\,U_c(n)-U_{c+1}(n)-U_{c-1}(n).$$
With $c=k$ at the row $q$, the third condition is $d_{q,k}>0$, which is part 2. With $c=k+1$ at the row $n$, the fourth is $d_{n,k+1}<0$, which is part 3.

**The evaluation.** For each column $9\le k\le264$ the check is formed with $z=z(k)$ from the list `Parking.Tab.zs`. The $256$ columns are evaluated in sixteen blocks of sixteen consecutive columns, beginning at $k=9,25,41,\dots,249$; for each block the kernel reduces the conjunction of the values of its columns (`Parking.Tab.allRange`) to true. No compiled code and no external program is involved: the definitions are part of the Lean source, and the evaluation is a step of the type checking of that source. `Parking.Tab.allRange_sound` gives the value true for each column of a block, and `Parking.Tab.glue` joins the sixteen ranges to $9\le k<265$. With the meaning of the check this gives the three parts for every $9\le k\le264$.
