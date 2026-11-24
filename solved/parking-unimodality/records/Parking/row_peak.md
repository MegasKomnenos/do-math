---
weight: unit
short: the shape of a row n ≥ 335 and a bound for the position of its peak
---
## Description

In a row $n \ge 335$ there is a column $p \le n-1$ with $25\,(n-1-p)^3 \le 121\,(p+1)^2$ such that the row does not decrease up to the column $p$, increases strictly from the column $81$ to the column $p$, does not increase from the column $p$ on, and decreases strictly from the column $p+1$ on.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $n \ge 335$ be a natural number. Then there is a natural number $p \le n-1$ with the following five properties.

1. $25\,(n-1-p)^3 \le 121\,(p+1)^2$.
2. $b(n,\ell-1) \le b(n,\ell)$ for $1 \le \ell \le p$.
3. $b(n,\ell-1) < b(n,\ell)$ for $82 \le \ell \le p$.
4. $b(n,\ell+1) \le b(n,\ell)$ for $p \le \ell \le n-2$.
5. $b(n,\ell+1) < b(n,\ell)$ for $p+1 \le \ell \le n-2$.

Written as one chain, properties 2 to 5 say
$$b(n,0) \le \dots \le b(n,81) < b(n,82) < \dots < b(n,p) \ \ge\ b(n,p+1) > b(n,p+2) > \dots > b(n,n-1).$$
If $p = n-1$, the chain ends at $b(n,p)$, and properties 4 and 5 say nothing.

## Explanation

**What the statement adds to the main theorem.** Properties 2 and 4 are the conclusion of `Parking.root_unimodal` for the row $n$: the row rises to the column $p$ and falls from it. That theorem does not say where $p$ stands, and it allows equalities everywhere. The present statement adds property 1, which bounds the position of $p$, and properties 3 and 5, which make the inequalities strict except in the columns up to $81$ and at the one step from $p$ to $p+1$.

**The position.** Put $r = n-1-p$, the number of columns between $p$ and the last column $n-1$ of the row. Property 1 reads $25r^3 \le 121(p+1)^2$, that is, $r \le (11(p+1)/5)^{2/3}$. Since $p + 1 \le n$, this gives
$$n-1-p \ \le\ \Bigl(\frac{121}{25}\Bigr)^{1/3} n^{2/3} \ <\ 1.692\,n^{2/3},$$
because $1.692^3 > 4.84 = \frac{121}{25}$. So the column $p$ lies within $1.692\,n^{2/3}$ columns of the right end of the row. In the terms used for columns, the *strip* of a column $k$ consists of the rows $k+r$ with $r \ge 1$ and $25r^3 \le 121k^2$; when $p < n-1$, property 1 says that the row $n = (p+1) + r$ lies in the strip of the column $p+1$.

Property 1 also bounds $p$ from below by a number that does not depend on $n$: $p \ge 265$. Indeed, if $p \le 264$, then $n-1-p \ge 334 - 264 = 70$ and $p + 1 \le 265$, and $25 \cdot 70^3 = 8\,575\,000$ exceeds $121 \cdot 265^2 = 8\,497\,225$, against property 1. In particular the range $82 \le \ell \le p$ of property 3 is not empty. The value $p = 265$ is not excluded by property 1 in the row $335$, since $25 \cdot 69^3 = 8\,212\,725 \le 8\,561\,476 = 121 \cdot 266^2$.

**The maximum of the row.** The largest entry of the row is $b(n,p)$, and it is attained at the column $p$ and at no other column except possibly $p+1$. To the left, properties 2 and 3 with $p \ge 265$ give $b(n,\ell) \le b(n,p-1) < b(n,p)$ for $\ell < p$. To the right, properties 4 and 5 give $b(n,\ell) < b(n,p+1) \le b(n,p)$ for $\ell \ge p+2$.

**What the statement leaves open.** It does not exclude $b(n,p+1) = b(n,p)$, nor equalities among the entries of the columns $0, \dots, 81$. It does not exclude $p = n-1$, a row with no descent; in that case property 1 reads $0 \le 121n^2$ and properties 4 and 5 are empty. Most important for its reading, property 1 is a bound in one direction only. It says that the maximum is not further than $(11(p+1)/5)^{2/3}$ columns from the right end, and it gives no lower bound for that distance, so it does not determine the position of the maximum. The curve $25(n-k)^3 = 121k^2$ is where the estimates of the library stop, as the paragraph on the constants explains, and it is not claimed to be where the maximum stands.

**How the statement is obtained.** It joins two statements about a column $k \ge 265$, read along the row $n$. By `Parking.beyond_strip` such a column is positive in every row beyond its strip, so a column that is not positive in the row $n$ has the row $n$ in its strip. By `Parking.strip_step`, in a row of the strip of the column $k$ a nonpositive step of the column $k$ is followed by a negative step of the column $k+1$; and when the row $n$ lies in the strip of a column, it lies in the strip of every later column of the row, because from a column to the next the distance to the end of the row decreases and the column number increases. So from the first column that is not positive, every later column is negative. This argument needs the first column that is not positive to be a column $k \ge 265$, and that is what the hypothesis $n \ge 335$ provides: in such a row the columns $1, \dots, 264$ are nonnegative, and the columns $82, \dots, 264$ are positive.

Properties 2 and 4 are thus proved here again for the rows $n \ge 335$, and not taken from `Parking.root_unimodal`. Conversely the proof of `Parking.root_unimodal` does not use the present statement or the two statements it rests on. A row $n \le 334$ is not reached by the argument, because there a column $k \le 264$ may fail to be positive, and for such a column `Parking.strip_step` is not available.

**The constants.** The column $265$ is the one from which `Parking.crossing_strip`, on which `Parking.beyond_strip` rests, and `Parking.Gfun_pos`, on which `Parking.strip_step` rests, are proved. The constant $\frac{121}{25}$ is that of the strip in these two theorems; the record of `Parking.crossing_strip` explains how it was chosen, and it shows that the end of the strip is not the row in which a column turns positive: for $k = 265$ the first positive row is $k+36$ and the strip ends at $k+69$. The row $335 = 264 + 71$ comes from `Parking.crossing_row`, which gives a positive row $k+r$ of a column $k \ge 82$ with $r \le \frac{27}{100}k$: for $82 \le k \le 264$ this row is at most $264 + 71$, and a row $n \ge 335$ is therefore at or after it. Strictness in property 3 begins at $\ell = 82$ because `Parking.big_columns` gives the strict inequality $b(n,k-1) < b(n,k)$ from the column $82$ on; for the columns $k \le 81$ the library has only the inequality $b(n,k-1) \le b(n,k)$ of `Parking.left_half`.

**The Lean form.** The statement is

`∃ p, p ≤ n - 1 ∧ 25 * (n - 1 - p) ^ 3 ≤ 121 * (p + 1) ^ 2 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧ (∀ ℓ, 82 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) < b n ℓ) ∧ (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ) ∧ (∀ ℓ, p + 1 ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) < b n ℓ)`.

The condition `p ≤ n - 1` together with the two parts that state properties 2 and 4 is, word for word, the conclusion of `Parking.root_unimodal`. The subtractions are those of natural numbers and are exact: $n - 1$ because $n \ge 335$, $n-1-p$ because $p \le n-1$, and $\ell - 1$ because $\ell \ge 1$. The condition $\ell \le n-2$ is written `ℓ + 1 ≤ n - 1`.

## Proof

The proof has three preparatory steps, which are private lemmas of the module, and then chooses $p$.

**Step 1: the columns up to $264$** (`early_columns`). *Let $n \ge 335$ and $1 \le k \le 264$. Then $b(n,k-1) \le b(n,k)$, and $b(n,k-1) < b(n,k)$ if $k \ge 82$.*

If $2k \le n$, the first inequality is `Parking.left_half`, which states it for $n \ge 17$ and $k \ge 1$ with $2k \le n$ and applies because $n \ge 335$, and the second is `Parking.big_columns`, which states it for $k \ge 82$ and $n \ge 2k$.

If $n < 2k$, then $2k > 335$, so $k \ge 168$. `Parking.crossing_row` applies to every column $k \ge 82$, hence to this one: there is $r \ge 1$ with $100r \le 27k$ such that the column $k$ is positive in the row $k+r$, that is, $b(k+r,k-1) < b(k+r,k)$ (`Parking.dq_pos_iff`). Since $k \le 264$, we have $100r \le 7128$, so $r \le 71$ and $k + r \le 335 \le n$. Thus $k+1 \le k+r \le n \le 2k-1$, and `Parking.chain_column_iter`, by which a column $k \ge 2$ that is positive in a row $m \ge k+1$ is positive in every row from $m$ to $2k-1$, gives $b(n,k-1) < b(n,k)$.

**Step 2: a column from $82$ on that is not positive** (`nonpos_in_strip`). *Let $n \ge 335$ and $82 \le q \le n-1$ with $b(n,q) \le b(n,q-1)$. Then $q \ge 265$ and $25\,(n-q)^3 \le 121\,q^2$.*

If $q \le 264$, Step 1 gives $b(n,q-1) < b(n,q)$, against the assumption; so $q \ge 265$. If $121q^2 < 25(n-q)^3$, then `Parking.beyond_strip`, applied to the column $q$ and to $r = n - q$, gives $b(n,q-1) < b(n,q)$, again against the assumption; so $25(n-q)^3 \le 121q^2$.

**Step 3: the columns after it** (`strip_tail`). *Let $i \ge 265$ and $n$ be such that $25\,(n-i)^3 \le 121\,i^2$ and $b(n,i) \le b(n,i-1)$. Then $b(n,\ell+1) < b(n,\ell)$ for every $\ell$ with $i \le \ell \le n-2$.*

First, for every column $j$ with $i \le j \le n-2$: if $b(n,j) \le b(n,j-1)$, then $b(n,j+1) < b(n,j)$. Indeed $n - j \le n - i$ and $i \le j$ give
$$25\,(n-j)^3 \le 25\,(n-i)^3 \le 121\,i^2 \le 121\,j^2,$$
and $n - j \ge 2$, so `Parking.strip_step` applies to the column $j \ge 265$ and to $r = n - j$, in the row $j + r = n$.

The claim now follows by induction on $\ell \ge i$; what is proved for each $\ell$ is: if $\ell \le n-2$, then $b(n,\ell+1) < b(n,\ell)$. For $\ell = i$ it is the implication just proved with $j = i$ and the assumption $b(n,i) \le b(n,i-1)$. Suppose it is proved for some $\ell \ge i$, and let $\ell + 1 \le n-2$. Then $\ell \le n-2$ as well, so $b(n,\ell+1) < b(n,\ell)$, which says that the column $\ell+1$ is not positive, and the implication with $j = \ell+1$ gives $b(n,\ell+2) < b(n,\ell+1)$.

**Step 4: the choice of $p$.** Let $n \ge 335$, and let $p$ be the least natural number with $p \ge 81$ such that $p = n-1$ or $b(n,p+1) \le b(n,p)$. Such numbers exist, since $n-1 \ge 81$ is one of them, and $p \le n-1$ because $p$ is the least of them. By the minimality of $p$, every $m$ with $81 \le m < p$ satisfies $b(n,m) < b(n,m+1)$. With $\ell = m+1$ this is property 3. Property 2 follows: for $\ell \le 81$ it is Step 1, and for $82 \le \ell \le p$ it is property 3.

*If $p = n-1$,* property 1 reads $0 \le 121n^2$, and there is no $\ell$ with $p \le \ell \le n-2$, so properties 4 and 5 are empty.

*If $p < n-1$,* then $b(n,p+1) \le b(n,p)$ by the choice of $p$. Put $q = p+1$, so that $82 \le q \le n-1$ and the column $q$ is not positive in the row $n$. By Step 2, $q \ge 265$ and $25\,(n-q)^3 \le 121\,q^2$; since $n - q = n-1-p$, this is property 1. By Step 3 with $i = q$, $b(n,\ell+1) < b(n,\ell)$ for $p+1 \le \ell \le n-2$, which is property 5. Property 4 holds for $\ell = p$ by the choice of $p$ and for $\ell \ge p+1$ by property 5.
