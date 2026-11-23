---
weight: step
short: joining two adjacent ranges
---
## Description

A statement that holds for all $k$ with $a\le k<b$ and for all $k$ with $b\le k<c$ holds for all $k$ with $a\le k<c$.

## Statement

Let $P$ be a property of natural numbers and let $a,b,c$ be natural numbers. If $P(k)$ holds for every $k$ with $a\le k<b$ and for every $k$ with $b\le k<c$, then $P(k)$ holds for every $k$ with $a\le k<c$.

## Explanation

The tables are evaluated in blocks of consecutive columns (`Parking.Tab.allRange`), and each block gives its statement on its own range (`Parking.Tab.allRange_sound`). `glue` joins the ranges of adjacent blocks; applied repeatedly it produces the statement for the whole range, $2\le k<82$ for the table of the columns and $9\le k<265$ for the table of two signs. No relation between $a$, $b$ and $c$ is assumed. A mathematical text uses this without mention.

## Proof

A number $k$ with $a\le k<c$ satisfies $k<b$ or $b\le k$; the first hypothesis applies in the first case and the second in the second.
