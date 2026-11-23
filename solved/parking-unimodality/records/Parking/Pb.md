---
weight: unit
short: birthday tail
---
## Description

The birthday tail $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$: the probability that $j$ independent uniform draws from $m$ values are pairwise distinct.

## Statement

For natural numbers $m \ge 1$ and $j \ge 0$,

$$P_{m,j} \;=\; \prod_{i=0}^{j-1}\Bigl(1-\frac{i}{m}\Bigr) \;=\; \frac{m(m-1)\cdots(m-j+1)}{m^{j}},$$

a real number; for $j = 0$ the product is empty and $P_{m,0} = 1$. For $m = 0$ the Lean definition gives $P_{0,j} = 1$ for every $j$, because Lean evaluates the quotient $i/0$ as $0$.

## Explanation

**The birthday problem.** Throw balls one after another into $m$ boxes, each ball independently of the others and uniformly over the boxes. When $i$ boxes are occupied, the next ball falls into an empty box with probability $1 - i/m$, so the first $j$ balls fall into $j$ different boxes with probability $P_{m,j}$. Let $Q$ be the number of balls thrown before the first ball that falls into an occupied box. Then $Q \ge j$ holds exactly when the first $j$ balls fall into different boxes, so

$$\Pr(Q \ge j) = P_{m,j} \quad (j \ge 1), \qquad \Pr(Q = q) = P_{m,q} - P_{m,q+1} = \frac{q}{m}\,P_{m,q},$$

where the last equality is `Parking.Pb_succ`. The variable $Q$ takes the values $1, \dots, m$, since $P_{m,1} = 1$ (`Parking.Pb_one`) and $P_{m,j} = 0$ for $j > m$ (`Parking.Pb_eq_zero`). The records of this part of the library call the law of $Q$ the *birthday law of $m$*, and they call $P_{m,j}$ its tail.

**Why the birthday law appears in the library.** The modules that prove that a column which has not yet become positive forces the next column to be negative write their quantities as sums over the compositions of an integer $m$, in which a part of size $p$ carries the weight $a_p = p^{p-1}/p!$ (`Parking.cay`, `Parking.Vc`). The theorem `Parking.Tq_eq` shows that the compositions of $m$ with exactly $q$ parts have the total weight $T_{m,q} = a_m\, q\, P_{m,q}$. Because $\sum_{q=1}^{m} q\,P_{m,q} = m$ (this is `Parking.Pb_moment` with the constant function $g = 1$), the compositions with $q$ parts carry the fraction $\frac{q}{m} P_{m,q}$ of the total weight $m\,a_m$. In other words: if a composition of $m$ is drawn with probability proportional to its weight, its number of parts follows the birthday law of $m$. What the later modules need to know about such compositions therefore reduces to facts about the numbers $P_{m,j}$. The mean of $Q$ is $s_m$ (`Parking.sbirth`), a ratio of two factorial moments of $Q$ is $D_m$ (`Parking.Dbirth`), and `Parking.tau_succ_le` and `Parking.mu0_le_muh` are inequalities for the laws that arise when every cut of a composition is given a constant weight $h$, under which the compositions with $q$ parts have the total weight $a_m\, q\, P_{m,q}\, h^{q-1}$.

**How the probabilistic language is to be read.** The library defines no probability space. Each statement about the birthday law is an identity or an inequality between finite sums of the numbers $P_{m,j}$, and the probabilistic words in the records say what these sums mean.

**Elementary properties.** The values at small indices and the recursion are `Parking.Pb_zero` ($P_{m,0} = 1$), `Parking.Pb_one` ($P_{m,1} = 1$) and `Parking.Pb_succ` ($P_{m,j+1} = P_{m,j}(1 - j/m)$); the vanishing beyond $m$ is `Parking.Pb_succ_self` and `Parking.Pb_eq_zero`; nonnegativity is `Parking.Pb_nonneg`. For $j \le m$ the definition can also be written $P_{m,j} = m!/((m-j)!\,m^{j})$.

**The Lean form.** `Pb m j` is the product over `Finset.range j`, that is over $i = 0, \dots, j-1$, of the real numbers `1 - (i : ℝ) / m`. The value $P_{0,j} = 1$ is a by-product of the convention $x/0 = 0$ and has no mathematical content. The statements that allow $m = 0$ are true with this value; the statements that need the vanishing of $P_{m,j}$ beyond $m$ assume $m \ge 1$.
