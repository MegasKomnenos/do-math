---
weight: step
short: the list of the rows n0(k) of the columns 2 to 81
---
## Description

The list of eighty natural numbers whose entries are, in order, the rows $n_0(2),n_0(3),\dots,n_0(81)$ of the table of the columns $2\le k\le81$: the table computes the rows below $n_0(k)$ of the column $k$ and checks its suffix sums at $n_0(k)$.

## Statement

`Parking.Tab.n0tab` is the list of the following eighty natural numbers, in this order:

7, 10, 13, 15, 18, 20, 23, 25, 28, 30, 32, 35, 37, 39, 41, 44, 46, 48, 50, 52, 55, 57, 59, 61, 63, 66, 68, 70, 72, 74, 76, 78, 80, 82, 85, 87, 89, 91, 93, 95, 97, 99, 101, 103, 105, 107, 109, 111, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170, 171, 173, 175.

## Explanation

The list is the data of the table of the columns $2\le k\le81$ (`Parking.Tab.small_table`). Its entry number $k-2$, counted from $0$, is the row $n_0(k)$ of the column $k$; the function $k\mapsto n_0(k)$ is `Parking.Tab.n0`, and the record of that function says what the rows are for and shows them against $k$. The list exists as a separate declaration only because Lean reads the function from a list (`Parking.Tab.nth`); mathematically the list and the function are the same object.
