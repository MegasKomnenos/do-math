---
weight: unit
short: displacements of the cars
---
## Description

The displacements of the cars: for a sequence of preferences $(a_1,\dots,a_m)$ and the sequence $(p_1,\dots,p_m)$ of the spots taken, the sequence of the differences $p_i-a_i$.

## Statement

Let $(a_1,\dots,a_m)$ and $(p_1,\dots,p_{m'})$ be finite sequences of natural numbers, the preferences and the spots taken. Their sequence of displacements is
$$\bigl(\max(p_1-a_1,0),\ \dots,\ \max(p_r-a_r,0)\bigr),\qquad r=\min(m,m').$$
When the two sequences have the same length and $p_i\ge a_i$ for every $i$, as is the case for the spots taken in the parking process, this is $(p_1-a_1,\dots,p_m-a_m)$.

## Explanation

The displacement of a car is the distance between the spot it takes and the spot it prefers. In the parking process (`Parking.parkFrom`) a car takes the first free spot at or after its preference, so $p_i\ge a_i$, and the process returns one spot for each car. For such data the two conventions in the statement never come into play, and the definition is the one of the root proposition, $d_i(\alpha)=\mathrm{pos}_i(\alpha)-a_i\ge0$; the shift between the numbering from $0$ and the numbering from $1$ cancels in the difference.

The conventions come from the Lean form, `List.zipWith (fun p a => p - a) ps prefs`: the subtraction of natural numbers gives $0$ when $p<a$, and `zipWith` stops at the end of the shorter list. Note the order of the arguments: `Parking.dispList prefs ps` takes the preferences first and the spots second.

The definition is stated for two arbitrary lists, and not for a function $\alpha$ and its list of spots, because the proof of the last-car recursion `Parking.A_succ` follows the displacements of preference lists of any length on streets of any length. For a preference sequence $\alpha$ the list used is `dispList (prefList α) ps` with `ps` the spots of `Parking.positions`; its maximum is `Parking.maxDisp`.
