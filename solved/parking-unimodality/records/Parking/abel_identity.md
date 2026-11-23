---
weight: unit
short: Abel's binomial identity
---
## Description

Abel's binomial identity: $\sum_{k=0}^{n} \binom{n}{k}\, w_k(x)\,(y-k)^{n-k} = (x+y)^n$ for real $x$, $y$, where $w_0(x) = 1$ and $w_k(x) = x\,(x+k)^{k-1}$ for $k \ge 1$.

## Statement

For every natural number $n$ and all real numbers $x$ and $y$,

$$\sum_{k=0}^{n} \binom{n}{k}\, w_k(x)\,(y-k)^{n-k} = (x+y)^n,$$

where $w_0(x) = 1$ and $w_k(x) = x\,(x+k)^{k-1}$ for $k \ge 1$ (`Parking.abelW`). Written out,

$$y^n + \sum_{k=1}^{n} \binom{n}{k}\, x\,(x+k)^{k-1}\,(y-k)^{n-k} = (x+y)^n .$$

The power with exponent $0$ is $1$; this concerns the term $k = n$, whose factor $(y-n)^0$ is $1$ also when $y = n$.

## Explanation

This is the classical identity known as Abel's binomial identity, or Abel's generalisation of the binomial theorem. It is an identity of polynomials in $x$ and $y$; the library states it for real numbers. For comparison, the binomial theorem is the same statement with $x^k$ in place of $w_k(x)$ and $y^{n-k}$ in place of $(y-k)^{n-k}$.

It is the one classical identity on which the algebra of the Cayley coefficients in this library rests. At $x = 1$, $y = n+1$ and after division by $n!$ it becomes the recursion $(n+1)\,c_{n+1} = \sum_{j \le n} (j+1)\,c_j\,c_{n-j}$ of the normalised parking numbers $c_n = (n+1)^{n-1}/n!$ (`Parking.cc_rec`), from which the convolution identities `Parking.cay_conv`, `Parking.eps_conv` and `Parking.ren_conv` follow. With a general $x$ it is used in the module of the resolvent kernel (`Parking.Hres`) to compute the coefficients of the powers of the series $\sum_n c_n X^n$.

The proof does not go by induction on $n$. It expands $(y-k)^{n-k}$ around $x + y$, which turns the left-hand side into a combination of the powers $(x+y)^i$, and then shows that every coefficient except that of $(x+y)^n$ is $x$ times a finite difference of order $m \ge 1$ of the polynomial $r^{m-1}$, whose degree is less than $m$; such a difference is zero.

## Proof

*Step 1: expansion around $x+y$.* This step holds for arbitrary real weights $w_0, \dots, w_n$ in place of $w_k(x)$. Since $y - k = (x+y) - (x+k)$, the binomial theorem gives

$$(y-k)^{n-k} = \sum_{i=0}^{n-k} \binom{n-k}{i}\,(x+y)^i\,\bigl(-(x+k)\bigr)^{n-k-i}.$$

Substitute this into the left-hand side. The result is a sum over the pairs $(k,i)$ with $k + i \le n$, and exchanging the order of summation makes $i$ the outer index, $0 \le i \le n$, and $k$ the inner one, $0 \le k \le n - i$. The binomial coefficients satisfy $\binom{n}{k}\binom{n-k}{i} = \binom{n}{i}\binom{n-i}{k}$, both sides being $n!/(k!\,i!\,(n-k-i)!)$. Hence

$$\sum_{k=0}^{n} \binom{n}{k}\, w_k\,(y-k)^{n-k} = \sum_{i=0}^{n} \binom{n}{i}\,(x+y)^i\, S_{n-i}, \qquad S_m := \sum_{k=0}^{m} \binom{m}{k}\, w_k\,\bigl(-(x+k)\bigr)^{m-k}.$$

*Step 2: the inner sums.* Now let $w_k = w_k(x)$. We claim that $S_0 = 1$ and $S_m = 0$ for $m \ge 1$. For $m = 0$ the sum has the single term $w_0(x) = 1$. Let $m \ge 1$. The term $k = 0$ is $(-x)^m = x \cdot (-1)^m x^{m-1}$. For $1 \le k \le m$ the term is

$$\binom{m}{k}\, x\,(x+k)^{k-1}\,(-1)^{m-k}(x+k)^{m-k} = x \cdot (-1)^{m-k} \binom{m}{k}\,(x+k)^{m-1}.$$

So every term has the same shape, and

$$S_m = x \sum_{k=0}^{m} (-1)^{m-k} \binom{m}{k}\,(x+k)^{m-1}.$$

The sum on the right is the $m$-th forward difference, with step $1$, of the function $r \mapsto r^{m-1}$, evaluated at $r = x$. The $m$-th forward difference of a power $r^j$ with $j < m$ is identically zero. Therefore $S_m = 0$. This is the point where the particular form of the weights is used: the factor $(x+k)^{k-1}$ in $w_k(x)$ combines with $(x+k)^{m-k}$ to the power $(x+k)^{m-1}$, whose exponent does not depend on $k$ and is smaller than $m$.

*Step 3: conclusion.* In the sum over $i$ of Step 1 the inner sum is $S_{n-i}$, which vanishes unless $i = n$. The term $i = n$ is $\binom{n}{n}(x+y)^n S_0 = (x+y)^n$.
