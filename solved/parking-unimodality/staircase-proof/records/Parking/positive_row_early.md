---
weight: unit
short: an early positive row in every column k ≥ 82
---
## Description

Every column $k\ge82$ has a positive step in a row $k+r$ with $1\le r\le27k/100$: $b(k+r,k-1)<b(k+r,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and let $d_{n,k}=b(n,k)-b(n,k-1)$ be the step of the column $k$ in the row $n$. For every natural number $k\ge82$ there is a natural number $r$ with
$$1\le r,\qquad100\,r\le27\,k,\qquad d_{k+r,k}>0 .$$

## Explanation

**What the statement says.** The rows $k+1\le n\le2k-1$ are the *first layer* of the column $k$ (some records call them the chain range of the column). The statement finds a row of the first layer in which the step of the column is positive, and it finds that row early: the layer has $k-1$ rows, and the row lies among the first $27k/100$ of them. The first row after the row $k$ in which the step of the column is positive is called the *first positive row* of the column. The row $k+r$ of the statement need not be that row. It is an upper bound for it: the first positive row of a column $k\ge82$ is at most $k+r$, hence at most $k+27k/100$.

**What it is used for.** The statement is used in one place, in `Parking.one_sign_change`. That statement takes the first positive row $q$ of the column and shows that the column is positive from $q$ to the end of its first layer; the bound on $r$ becomes the bound $100(q-k)\le27k$ on $q$. Two arguments need this bound. `Parking.persist`, which carries the positive sign from the row $q$ to the row $2k-1$, asks that $q$ lies in the first third of the layer, $3(q-k)\le k$, and $27/100<1/3$. The argument for the rows $n\ge2k$ of the column, in `Parking.step_pos_large`, uses $100(q-k)\le27k$ as it stands: it compares the weights that a row $n\ge2k$ gives to the rows before $q$ and to the rows from $q$ on, and that comparison needs the distance of at least $73k/100$ between the row $q$ and the row $2k$. Through `Parking.one_sign_change` the present statement therefore stands, in every column $k\ge82$, behind the persistence of the sign in the first layer (`Parking.step_persists`) and behind the positive steps in the rows beyond the first layer (`Parking.step_pos_large`). The statement begins at the column $82$ because these arguments do.

**The two sources of the row.** The row comes from a table in the smaller columns and from a theorem in the larger ones. For $82\le k\le264$ the table of two signs (`Parking.Tab.two_signs`), an exact computation, lists for each column $9\le k\le264$ a number $z(k)$ (`Parking.Tab.ztab`) and shows $d_{k+z(k)+1,k}>0$. The statement takes $r=z(k)+1$, and the bound $100(z(k)+1)\le27k$ is a finite check on the list of the numbers $z(k)$ (`Parking.Tab.ztab_27`).

For $k\ge265$ the row is supplied by the curve increase `Parking.curve_crossing`: there is a row $j>k$ with $(j-k-1)^3\le k^2$ in which the column is positive. The curve increase bounds the distance $j-k$ by a quantity of the order $k^{2/3}$, which is far more than is needed here, where a bound that is linear in $k$ suffices. At $k=265$ it gives $j-k\le42$, while $27k/100$ allows $71$, and the room grows with $k$. The constant $27/100$ is thus a bound that both sources meet and that is small enough for both arguments that use it.

The curve increase has a second use, in the diagonal rule `Parking.diagonal_rule`, where its bound is needed as sharp as it is; the record of `Parking.staircase` describes the two uses side by side.

**The Lean form.** The statement is `∃ r, 1 ≤ r ∧ 100 * r ≤ 27 * k ∧ 0 < dq k (k + r)`. The sign of the step is written as the positivity of the real number $\delta^{(k)}_{k+r}=d_{k+r,k}/(k+r)!$ (`Parking.dq`), which is equivalent to the comparison $b(k+r,k-1)<b(k+r,k)$ of natural numbers by `Parking.dq_pos_iff`. `Parking.one_sign_change` and `Parking.persist` are stated in the same form, so no conversion is needed between them. The bound $r\le27k/100$ is the inequality $100\,r\le27\,k$ of natural numbers.

## Proof

The proof distinguishes the columns $k\le264$ and $k\ge265$.

*The columns $82\le k\le264$.* Let $z=z(k)$ be the number listed for the column (`Parking.Tab.ztab`). `Parking.Tab.two_signs` states, for $9\le k\le264$, that $z+2\le k$, that $b(k+z+1,k-1)<b(k+z+1,k)$ and that $b(k+z,k+1)<b(k+z,k)$; the second of these is used. Take $r=z+1$. Then $r\ge1$, and $100\,(z+1)\le27\,k$ is `Parking.Tab.ztab_27`, which states this inequality for $82\le k\le264$. By `Parking.dq_pos_iff` the inequality $b(k+r,k-1)<b(k+r,k)$ is $\delta^{(k)}_{k+r}>0$, that is, $d_{k+r,k}>0$.

*The columns $k\ge265$.* `Parking.curve_crossing` gives a natural number $j$ with
$$k<j,\qquad(j-k-1)^3\le k^2,\qquad b(j,k-1)<b(j,k).$$
Put $s=j-k-1$, so that $j=k+s+1$ and $s^3\le k^2$, and take $r=s+1$. Then $r\ge1$, and $d_{k+r,k}=d_{j,k}>0$, again by `Parking.dq_pos_iff`. It remains to show $100\,(s+1)\le27\,k$.

Suppose $100\,(s+1)>27\,k$. Then $400\,s>108\,k-400\ge100\,k$, because $8k\ge400$; so $k<4s$. Hence
$$k^3\le(4s)^3=64\,s^3\le64\,k^2 .$$
On the other hand $k\ge265$ gives $k^3=k\cdot k^2\ge265\,k^2$, and $k^2>0$. The two together give $265\,k^2\le64\,k^2$, which is false. So $100\,(s+1)\le27\,k$, that is, $100\,r\le27\,k$.
