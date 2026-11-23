---
weight: step
short: upper bound for the critical tilt
---
## Description

For $c \ge 1$ the critical tilt $x_c = (c/(c+1))^{c-1}$ satisfies $e\,x_c \le \exp(3/(2c))$.

## Statement

For every natural number $c \ge 1$,
$$e \cdot x_c \;\le\; \exp\!\Bigl(\frac{3}{2c}\Bigr),$$
where $x_c = (c/(c+1))^{c-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

Stirling's formula controls the tree numbers $a_n = n^{n-1}/n!$ (`Parking.cay`) at the tilt $e^{-1}$: $a_n e^{-n}$ is of the order $n^{-3/2}$. The critical tilt is larger than $e^{-1}$, and the statement bounds the excess: $(e\,x_c)^n \le \exp(3n/(2c))$, which stays bounded as long as $n$ is at most a fixed multiple of $c$. In this form it is used twice, to pass from the tilt $e^{-1}$ to the tilt $x_c$: in the bound of the Cayley sum (`Parking.cayleySum_le_one`), where $n \le c+1$, and in the bounds of the tilted prime kernel in the left half of the argument.

## Proof

The inequality $\log(1+t) \ge 2t/(t+2)$ for $t \ge 0$ (from Mathlib), at $t = 1/c$, gives $\log(1+1/c) \ge 2/(2c+1)$. Multiplying by $c - 1 \ge 0$,
$$(c-1)\log\Bigl(1+\frac1c\Bigr) \;\ge\; \frac{2(c-1)}{2c+1} \;\ge\; 1 - \frac{3}{2c};$$
the second inequality is $(2c-3)(2c+1) \le 4c(c-1)$, that is, $-3 \le 0$. Hence $(1+1/c)^{c-1} \ge \exp(1 - 3/(2c))$.

By `Parking.xcrit_mul_psi`, $x_c\,(1+1/c)^{c-1} = 1$, and $x_c > 0$ (`Parking.xcrit_pos`). So $x_c \exp(1 - 3/(2c)) \le 1$, and multiplying by $\exp(3/(2c))$ gives $e\,x_c \le \exp(3/(2c))$.
