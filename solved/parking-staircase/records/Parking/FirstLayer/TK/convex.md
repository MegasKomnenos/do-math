---
weight: step
short: property K contains convexity
---
## Description

A triple $(a,b,c)$ with property K at $k$ is convex: $2b\le c+a$.

## Statement

Let $k,a,b,c$ be real numbers such that $(a,b,c)$ has property K at $k$ (`Parking.FirstLayer.TK`: $2e^{\mu/k}b\le e^{\mu}c+e^{-\mu}a$ for every $\mu\ge 0$). Then $2b\le c+a$.

## Explanation

This is how a result about property K is read as a plain inequality at the end of an argument: `Parking.FirstLayer.zrT_diag_convex` and `Parking.FirstLayer.zrT_weak_requirement` are obtained in this way from `Parking.FirstLayer.kernel_TK`.

## Proof

Take $\mu=0$ in the defining inequality.
