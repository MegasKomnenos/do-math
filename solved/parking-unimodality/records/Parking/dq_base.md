---
weight: unit
short: initial value of the step of a column
---
## Description

The first nonzero value of the step of the column $k\ge2$: $\delta^{(k)}_k=-a_k/k$ with $a_k=k^{k-1}/k!$; in integers, $b(k,k)-b(k,k-1)=-k^{k-2}$.

## Statement

For every natural number $k\ge2$,
$$\delta^{(k)}_k=-\frac{a_k}{k},$$
where $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $a_k=k^{k-1}/k!$ (`Parking.cay`).

## Explanation

Multiplied by $k!$ the statement is $d_{k,k}=-k^{k-2}$. Since $b(k,k)=0$ (`Parking.bq_eq_zero`), it says that exactly $k^{k-2}$ parking functions of length $k$ have the largest possible maximum displacement $k-1$. Every column $k\ge2$ therefore begins with a negative step in the row $n=k$, after the rows $n<k$ in which the step is zero (`Parking.dq_eq_zero`). This value is the initial condition of the column equation `Parking.dq_col`, which governs the rows $k+1\le n\le2k-1$; the question studied in the chain range is in which row the step, starting from this negative value, becomes positive. The statement is used in this way in the crossing criterion (`Parking.cross_criterion`) and in the proof that a column changes sign once in the chain range (`Parking.single_crossing`).

The same value appears as the first nonzero tree curvature: from the definition `Parking.xi` and `Parking.zr_eq_cc` one computes $\xi_k=-a_k/k$.

## Proof

Write $k=j+1$ with $j\ge1$. The proof computes $c_{j+1}-z^{(j)}_{j+1}$ by the forward form of the single-chain formula and then expresses $\delta^{(j+1)}_{j+1}$ through it. Here $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) and $c_n=(n+1)^{n-1}/n!=a_{n+1}$ (`Parking.cc`).

By `Parking.zr_isWSol`, $z^{(j)}$ solves the weighted last-car recursion with the weight $\min(t,j)$, which is $t$ for $t\le j$. So `Parking.IsWSol.fwd` applies with $k=j$ and $n=j+1\le2j+1$; its sum has the single term $t=j+1$:
$$c_{j+1}-z^{(j)}_{j+1}=c_0\Bigl(c_j-\frac{\min(j+1,j)}{j+1}\,z^{(j)}_j\Bigr)=c_j-\frac{j}{j+1}\,c_j=\frac{c_j}{j+1},$$
using $c_0=1$ (`Parking.cc_zero`) and $z^{(j)}_j=c_j$ (`Parking.zr_eq_cc`).

On the other hand, $\beta^{(j+1)}_{j+1}=0$ by `Parking.bq_eq_zero`, and $\beta^{(j)}_{j+1}=z^{(j+1)}_{j+1}-z^{(j)}_{j+1}=c_{j+1}-z^{(j)}_{j+1}$ by `Parking.bq_eq` and `Parking.zr_eq_cc`. Hence
$$\delta^{(j+1)}_{j+1}=\beta^{(j+1)}_{j+1}-\beta^{(j)}_{j+1}=-\bigl(c_{j+1}-z^{(j)}_{j+1}\bigr)=-\frac{c_j}{j+1}=-\frac{a_{j+1}}{j+1}.$$
