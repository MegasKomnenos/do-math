---
weight: step
short: the direct part as two boundary terms and a pair sum
---
## Description

For $P+2\le c$ the direct part of the last-car recursion is $D(c,P)=(c+P+1)\,\omega_P\,\omega_c+\frac{c+P+2}{2}\,Q_{P+1}(c-P-2)$, with $\omega$ the tilted Cayley masses at the tilt $x_k$ and $Q$ their pair sums.

## Statement

Let $k$, $c$, $P$ be natural numbers with $P+2\le c$, $\omega_n=c_nx_k^{\,n}$ the tilted Cayley masses at the critical tilt $x_k$ (`Parking.ccT`, `Parking.xcrit`), $D(c,P)=\sum_{a=0}^{c-P}\min(P+a+1,c)\,\omega_{P+a}\,\omega_{c-a}$ (`Parking.FirstLayer.direct`) and $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ (`Parking.FirstLayer.pairT`). Then
$$D(c,P)=(c+P+1)\,\omega_P\,\omega_c+\frac{c+P+2}{2}\;Q_{P+1}(c-P-2).$$

## Explanation

The direct part is a sum of the products $\omega_p\omega_q$ over the pairs with $p+q=c+P$ and $P\le p,q\le c$, each with the weight $\min(p+1,c)$. The two end pairs $(P,c)$ and $(c,P)$ have the weights $P+1$ and $c$. Every other pair $(p,q)$ has $p,q\le c-1$ and the weight $p+1$; since the set of these pairs is symmetric under exchanging $p$ and $q$ and the product is symmetric, the weight may be replaced by the mean $\frac{(p+1)+(q+1)}{2}=\frac{c+P+2}{2}$, which does not depend on the pair. This is how the pair sum appears in the recursion. Dividing by the size $c+P+1$ gives the direct term of `Parking.FirstLayer.Sdir`.

The condition $P+2\le c$ says that the size $c+P+1$ exceeds the threshold by $\rho=P+1\le c-1$; it guarantees that there is at least one inner pair and that the two end pairs are distinct.

## Proof

Write $c=P+1+L$ with $L\ge 1$. The sum defining $D(c,P)$ has the terms $a=0,\dots,L+1$.

The term $a=0$ is $\min(P+1,c)\,\omega_P\omega_c=(P+1)\,\omega_P\omega_c$, and the term $a=L+1$ is $\min(c+1,c)\,\omega_c\omega_P=c\,\omega_c\omega_P$; their sum is $(c+P+1)\,\omega_P\omega_c$.

The terms $a=b+1$, $0\le b\le L-1$, are $(P+2+b)\,F_b$ with $F_b=\omega_{P+1+b}\,\omega_{P+1+(L-1-b)}$, because $P+b+2\le c$ and $c-(b+1)=P+1+(L-1-b)$. The numbers $F_b$ satisfy $F_{L-1-b}=F_b$. For a sequence with this symmetry, $\sum_{b<L}(\alpha+b)F_b=\frac{2\alpha+L-1}{2}\sum_{b<L}F_b$ for every real $\alpha$: add the sum to its reflection $\sum_{b<L}(\alpha+L-1-b)F_b$, which equals it. With $\alpha=P+2$ the coefficient is $\frac{2P+3+L}{2}=\frac{c+P+2}{2}$, and $\sum_{b<L}F_b=Q_{P+1}(L-1)=Q_{P+1}(c-P-2)$ by `Parking.FirstLayer.pairT_eq`.
