---
weight: step
short: the strip ends within 27k/100 of the diagonal
---
## Description

For $k\ge265$ and a natural number $s$ with $25s^3\le121k^2$, one has $100\,(s+1)\le27k$.

## Statement

Let $k\ge265$ and $s$ be natural numbers with $25\,s^3\le121\,k^2$. Then $100\,(s+1)\le27\,k$.

## Explanation

The condition $25s^3\le121k^2$ says $s\le(11k/5)^{2/3}$. The positions of the column $k$ in the rows $k+s$ with such $s$ form the *strip* of the column; `Parking.crossing_strip` shows that a column $k\ge265$ turns positive at the latest one row after the end of its strip. The present statement compares the strip, whose width grows like $1.69\,k^{2/3}$, with the linear bound $\frac{27}{100}k$: for $k\ge265$ even $s+1$ is at most $\frac{27}{100}k$.

It is used three times. In `Parking.crossing_row` it turns the row found by `Parking.crossing_strip` into a row $k+r$ with $1\le r$ and $100r\le27k$, the same form in which a positive row of the columns $82\le k\le264$ is read from the table `Parking.Tab.two_signs`; the later arguments of the chain range and of the left half are stated for a crossing row within $\frac{27}{100}k$. In `Parking.mono265` and in `Parking.strip_step` it shows that a row of the strip is a first-layer position, $s\le k-1$.

The constant is close at the lower end: for $k=265$ the largest $s$ is $69$, and $100\cdot70=7000\le7155=27\cdot265$.

## Proof

Suppose $27k<100\,(s+1)$. Then $100s\ge27k-99$, hence $1000s\ge270k-990\ge266k$, the last step because $4k\ge990$ for $k\ge265$. Cubing and using the hypothesis,
$$25\cdot266^3\,k^3\le25\,(1000s)^3=10^9\cdot25s^3\le121\cdot10^9\,k^2 .$$
Here $25\cdot266^3=470\,527\,400$, so after division by $k^2>0$ we get $470\,527\,400\,k\le121\cdot10^9$, while $k\ge265$ gives $470\,527\,400\,k\ge124\,689\,761\,000>121\cdot10^9$. This is a contradiction. All steps are computations with natural numbers.
