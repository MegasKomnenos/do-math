---
weight: step
short: the list of the numbers z(k) for the columns 9 to 264
---
## Description

The list of $256$ natural numbers whose entries are, in order, the numbers $z(9),z(10),\dots,z(264)$ of the table of two signs.

## Statement

`Parking.Tab.zs` is the list of $256$ natural numbers that consists, in this order, of

7 (once), 8 (5 times), 9 (6 times), 10 (5 times), 11 (6 times), 12 (6 times), 13 (7 times), 14 (7 times), 15 (7 times), 16 (8 times), 17 (8 times), 18 (9 times), 19 (8 times), 20 (10 times), 21 (9 times), 22 (10 times), 23 (10 times), 24 (11 times), 25 (10 times), 26 (11 times), 27 (12 times), 28 (11 times), 29 (12 times), 30 (13 times), 31 (12 times), 32 (13 times), 33 (13 times), 34 (13 times), 35 (3 times).

## Explanation

The list is the data of the table of two signs (`Parking.Tab.two_signs`). Its entry number $k-9$, counted from $0$, is the number $z(k)$ of the column $k$; the function $k\mapsto z(k)$ is `Parking.Tab.ztab`, and the record of that function says what the numbers mean and gives them against $k$. The list exists as a separate declaration only because Lean reads the function from a list (`Parking.Tab.nth`); mathematically the list and the function are the same object. The entries do not decrease along the list.
