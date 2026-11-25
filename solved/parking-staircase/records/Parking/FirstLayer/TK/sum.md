---
weight: step
short: property K of a finite sum of triples
---
## Description

A finite sum of triples that have property K at $k$ has property K at $k$.

## Statement

Let $k$ be a real number, $s$ a finite set, and $(a_i,b_i,c_i)$, $i\in s$, triples of real numbers each of which has property K at $k$ (`Parking.FirstLayer.TK`). Then $\big(\sum_{i\in s}a_i,\ \sum_{i\in s}b_i,\ \sum_{i\in s}c_i\big)$ has property K at $k$.

## Explanation

The finite form of `Parking.FirstLayer.TK.add`. The empty sum is the triple $(0,0,0)$, which has the property trivially.

## Proof

For each $\mu\ge 0$, sum the defining inequalities $2e^{\mu/k}b_i\le e^{\mu}c_i+e^{-\mu}a_i$ over $i\in s$.
