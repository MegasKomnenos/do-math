---
weight: unit
short: the tilted environment does not increase at the critical tilt
---
## Description

For every column $k \ge 2$ the tilted environment of the threshold $k$ at the critical tilt, $z^{(k)}_N x_k^N$ with $z^{(k)}_N = A(N,k-1)/N!$ and $x_k = (k/(k+1))^{k-1}$, is nonincreasing in $N$.

## Statement

For every natural number $k \ge 2$ and every natural number $N$,
$$z^{(k)}_{N+1}\, x_k^{\,N+1} \;\le\; z^{(k)}_N\, x_k^{\,N} ,$$
where $z^{(k)}_N = A(N,k-1)/N!$ is the normalised number of parking functions of length $N$ all of whose displacements are smaller than $k$ (`Parking.zr`; tilted: `Parking.zrT`), and $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

In terms of the counts the statement is $A(N+1,k-1) \le (N+1)\,(1+1/k)^{k-1}\, A(N,k-1)$ for all $N$: adding one car multiplies the number of parking functions with all displacements smaller than $k$ by at most $(N+1)(1+1/k)^{k-1}$.

The tilt $x_k$ is the largest one for which this can hold. On the free range $N \le k$ the environment is $c_N x^N$ with $c_N = (N+1)^{N-1}/N!$, and $x_k$ is defined so that $c_{k-1} x_k^{k-1} = c_k x_k^k$ (see `Parking.xcrit`); for a larger tilt the step from $k-1$ to $k$ would be an increase. Without the threshold the sequence $c_N x_k^N$ increases again beyond $k$ (`Parking.ccT_le_succ`). The theorem says that the threshold removes this growth completely: the tilt that makes the free range end flat keeps the whole sequence from increasing.

The theorem turns the tilted environment into a system of monotone weights, and this is why the argument for the columns $k$ in the rows $n \ge 2k$ is carried out at the critical tilt. In the step bound `Parking.step_bound`, the one-tree bound `Parking.one_tree_bound`, multiplied by $x_k^n$, bounds the tilted step of the row $n$ from below by a sum of tilted tree curvatures against the weights $z^{(k)}_{n-t} x_k^{n-t}$; these weights are nonnegative and nondecreasing in $t$, and Abel summation then bounds the sum from below as soon as the tail sums of the curvatures are nonnegative. For the columns $2 \le k \le 81$ a finite table supplies the signs of the tail sums at one row (`Parking.Tab.small_table`), and `Parking.step_pos_beyond` applies the step bound, through `Parking.propagate_pos`, with the present theorem as the hypothesis on the weights. For the columns $k \ge 82$ the same monotonicity is used in the weighted debt (`Parking.weighted_debt`) and in the proof of `Parking.step_pos_large`.

The proof has a structural part and a numerical part. The structural part is a statement about any solution of the tilted last-car recursion: if the solution does not increase on the free range $[0,k]$ and has mass $x \sum_{j=1}^{k} u_j \le 1$ there, it never increases. The numerical part verifies these two conditions for the environment, where they concern only the explicit numbers $c_j x_k^j$. The condition on the mass is the bound of the Cayley sum, $x_k \sum_{j=1}^{k} c_j x_k^j \le 1$; it is proved by an estimate for $k \ge 12$ (`Parking.cayleySum_le_one`) and by exact evaluation of a rational number for each of $k = 2, \dots, 11$.

## Proof

Fix $k \ge 2$, put $x = x_k$, and $u_N = z^{(k)}_N x^N$. Then $x > 0$ (`Parking.xcrit_pos`), $u_0 = 1$ (`Parking.zrT_zero`), and by the tilted last-car recursion `Parking.zrT_succ`, with $m_i = \min(i+1,k)$,
$$(N+1)\, u_{N+1} \;=\; x \sum_{i=0}^{N} m_i\, u_i\, u_{N-i} \qquad (N \ge 0). \tag{1}$$

### A solution of the recursion that starts well never increases

We first prove a statement about real sequences in general. Let $y \ge 1$ be a natural number, $x \ge 0$ a real number, and let the real sequence $u$ satisfy $u_0 = 1$ and (1) with $m_i = \min(i+1,y)$. Suppose

- (a) $u_{N+1} \le u_N$ for all $N < y$, and
- (b) $x \sum_{j=1}^{y} u_j \le 1$.

Then $u_{N+1} \le u_N$ for all $N$.

*Nonnegativity.* By strong induction on $N$, $u_N \ge 0$: $u_0 = 1$, and (1) expresses $(N+1) u_{N+1}$ as $x \ge 0$ times a sum of products of nonnegative numbers.

*The difference identity.* Put $D_N = u_N - u_{N+1}$. Let $N \ge y$. Then
$$(N+1)\, D_N \;=\; (1 - x y)\, u_N \;+\; x \sum_{i=0}^{N-1} m_i\, u_i\, D_{N-1-i} . \tag{2}$$
To see this, write $(N+1) D_N = u_N + N u_N - (N+1) u_{N+1}$ and use (1) twice. With $N-1$ in place of $N$ it gives $N u_N = x \sum_{i=0}^{N-1} m_i u_i u_{N-1-i}$. For the index $N$ the last term, $i = N$, is $m_N u_N u_0 = y\, u_N$, because $N + 1 > y$ and $u_0 = 1$, so $(N+1) u_{N+1} = x \sum_{i=0}^{N-1} m_i u_i u_{N-i} + x y\, u_N$. The difference of the two sums is $\sum_{i=0}^{N-1} m_i u_i (u_{N-1-i} - u_{N-i})$, which is the sum in (2).

*The induction.* We prove $D_N \ge 0$ by strong induction on $N$. For $N < y$ it is (a). Let $N \ge y$ and suppose $D_j \ge 0$ for all $j < N$. Then $u_N \le u_i$ for every $i \le N$, and every term of the sum in (2) is nonnegative. Reindex the sum by $j = N-1-i$, so that it reads $\sum_{j=0}^{N-1} m_{N-1-j}\, u_{N-1-j}\, D_j$, and keep only the terms with $j < y$ (there are such terms among $j \le N-1$ because $y \le N$). For these,
$$m_{N-1-j} = \min(N-j,\, y) \;\ge\; y - j \qquad\text{and}\qquad u_{N-1-j} \;\ge\; u_N ,$$
the first because $N \ge y$. Hence
$$\sum_{i=0}^{N-1} m_i\, u_i\, D_{N-1-i} \;\ge\; u_N \sum_{j=0}^{y-1} (y-j)\, D_j .$$
The last sum is evaluated by Abel summation. Since $D_j = u_j - u_{j+1}$, one has $\sum_{j<t} (y-j) D_j = y\,u_0 - (y-t)\,u_t - \sum_{j=1}^{t} u_j$ for every $t$ (induction on $t$), and for $t = y$, with $u_0 = 1$,
$$\sum_{j=0}^{y-1} (y-j)\, D_j \;=\; y - \sum_{j=1}^{y} u_j .$$
Inserting this in (2), the terms $x y\, u_N$ cancel:
$$(N+1)\, D_N \;\ge\; (1 - xy)\, u_N + x\, u_N \Bigl( y - \sum_{j=1}^{y} u_j \Bigr) \;=\; u_N \Bigl( 1 - x \sum_{j=1}^{y} u_j \Bigr) \;\ge\; 0$$
by (b) and $u_N \ge 0$. So $D_N \ge 0$.

The point of the argument is the choice of the terms that are kept. The negative term $-xy\,u_N$ in (2) comes from the weight $y$ of the last car when it parks behind all the others. It is compensated by the decrease that the sequence has already made on its free range, weighted by $y - j$; what remains is $u_N$ times the deficit $1 - x \sum_{j=1}^{y} u_j$ of the mass, and (b) says that this deficit is not negative.

### The two conditions for the environment

We apply the statement with $y = k$ to $u_N = z^{(k)}_N x_k^N$. On the free range, $u_N = c_N x^N$ for $N \le k$ (`Parking.zrT_eq_ccT`), where $c_N = (N+1)^{N-1}/N!$.

*Condition (a).* For $N < k$, $c_{N+1} x_k^{N+1} \le c_N x_k^N$ by `Parking.ccT_succ_le`.

*Condition (b).* It reads $x_k \sum_{j=1}^{k} c_j x_k^j \le 1$. For $k \ge 12$ this is `Parking.cayleySum_le_one`. For $2 \le k \le 11$ it is verified separately for each of the ten values of $k$. With $c_j = (j+1)^j/(j+1)!$ (`Parking.cc_eq`) the left-hand side is
$$\sum_{i=0}^{k-1} \frac{(i+2)^{i+1}}{(i+2)!}\; x^{\,i+2}, \qquad x = \Bigl(\frac{k}{k+1}\Bigr)^{k-1},$$
a finite sum of rational numbers, at most eleven terms. Lean evaluates this sum exactly in rational arithmetic and compares the result with $1$ (the normalisation procedure `norm_num`, which produces an ordinary proof term; no floating-point arithmetic and no compiled code is involved). For orientation, the values of the sum, computed exactly outside the library and rounded, are

| $k$ | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|
| sum | 0.889 | 0.850 | 0.830 | 0.817 | 0.807 | 0.799 | 0.793 | 0.788 | 0.783 | 0.779 |

(for $k = 2$ the sum is $x^2 + \tfrac32 x^3$ with $x = \tfrac23$, that is, $\tfrac89$). The Lean proof contains only the comparison with $1$.

With (a) and (b) the general statement gives $u_{N+1} \le u_N$ for all $N$.
