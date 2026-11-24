---
weight: step
short: last-part recursion for two marked cut points
---
## Description

For every cut profile $f$ and every $m$: $\Lambda^{(2)}_m[f] = \sum_{0<s<m} \bigl(\Lambda^{(1)}_s[f] + \Lambda^{(2)}_s[f]\bigr)\, f(s)\, a_{m-s}$, where $\Lambda^{(1)}$ and $\Lambda^{(2)}$ are the total weights of the compositions with one and with two marked cut points and $a_p = p^{p-1}/p!$.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function and $m$ a natural number. Then

$$\Lambda^{(2)}_m[f] \;=\; \sum_{0 < s < m} \bigl(\Lambda^{(1)}_s[f] + \Lambda^{(2)}_s[f]\bigr)\; f(s)\; a_{m-s},$$

where $\Lambda^{(1)}_s[f]$ and $\Lambda^{(2)}_s[f]$ are the total weights of the compositions of $s$ with one and with two marked cut points for the cut profile $f$ (`Parking.Lam1`, `Parking.Lam2`), and $a_p = p^{p-1}/p!$ (`Parking.cay`).

## Explanation

The recursion removes the last part of a composition of $m$ with two marked cut points $a < b$. Let $s$ be the last cut point, so that the last part has the size $m - s$ and the weight $a_{m-s}$, and the cut at $s$ has the weight $f(s)$. Either $s$ is the larger marked point $b$; then what remains is a composition of $s$ with one marked cut point, of total weight $\Lambda^{(1)}_s[f]$. Or $s$ lies after both marked points; then what remains is a composition of $s$ with two marked cut points, of total weight $\Lambda^{(2)}_s[f]$.

The statement is used in the proof of `Parking.curv_ge_pair`. There it is read as an equation for $G = \Lambda^{(1)} + \Lambda^{(2)}$, namely $G(m) = \Lambda^{(1)}_m[f] + \sum_{0<s<m} a_{m-s}\, f(s)\, G(s)$, and this equation is paired with the equation that the environment of the threshold $k$, the normalised number of parking functions with all displacements less than $k$, satisfies in the rows concerned.

## Proof

By definition, $\Lambda^{(2)}_m[f] = \sum_{0<b<m} \Lambda^{(1)}_b[f]\, f(b)\, \Lambda_{m-b}[f^{+b}]$ with $f^{+b}(s) = f(b+s)$. The last-cut recursion `Parking.Lam_last`, applied to the profile $f^{+b}$ and the length $m - b$, gives

$$\Lambda_{m-b}\bigl[f^{+b}\bigr] = a_{m-b} + \sum_{0<u<m-b} \Lambda_u\bigl[f^{+b}\bigr]\, f(b+u)\, a_{m-b-u} = a_{m-b} + \sum_{b<s<m} \Lambda_{s-b}\bigl[f^{+b}\bigr]\, f(s)\, a_{m-s},$$

where the second form is obtained by the substitution $s = b + u$. Multiply by $\Lambda^{(1)}_b[f]\, f(b)$ and sum over $0 < b < m$. The first terms give $\sum_{0<b<m} \Lambda^{(1)}_b[f]\, f(b)\, a_{m-b}$, which is the sum of the terms $\Lambda^{(1)}_s[f]\, f(s)\, a_{m-s}$ of the statement. The second terms give a double sum over $0 < b < s < m$; summing first over $b$ for a fixed $s$, it becomes

$$\sum_{0<s<m} \Bigl(\sum_{0<b<s} \Lambda^{(1)}_b[f]\, f(b)\, \Lambda_{s-b}\bigl[f^{+b}\bigr]\Bigr)\, f(s)\, a_{m-s} = \sum_{0<s<m} \Lambda^{(2)}_s[f]\; f(s)\; a_{m-s},$$

by the definition of $\Lambda^{(2)}_s[f]$. Adding the two contributions gives the statement.

The computation does not use what $\Lambda^{(1)}$ is: it shows, for an arbitrary function $g$ in the place of $\Lambda^{(1)}[f]$, that $\sum_{0<b<m} g(b)\, f(b)\, \Lambda_{m-b}[f^{+b}] = \sum_{0<s<m} \bigl(g(s) + \sum_{0<b<s} g(b)\, f(b)\, \Lambda_{s-b}[f^{+b}]\bigr) f(s)\, a_{m-s}$. In this general form it is also a step of the proof of `Parking.Lam1_eq_sum`.
