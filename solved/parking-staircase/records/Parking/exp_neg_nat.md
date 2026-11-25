---
weight: step
short: exp(-i) as a power of exp(-1)
---
## Description

$e^{-i}=(e^{-1})^i$ for every natural number $i$.

## Statement

For every natural number $i$, $\ e^{-i}=(e^{-1})^{i}$.

## Explanation

A rewriting step. The persistence argument for the far rows works with the frozen kernel `Parking.fker`, which is $e^{-i}\varepsilon_i$ with $e^{-1}/2$ added at $i=1$ (here $\varepsilon_i=(i-1)^{i-1}/i!$, `Parking.eps`), and with its renewal sequence $e^{-s}H_s$ (`Parking.Gres`, with $H_s$ the numbers of `Parking.Hres`), in which the factor $e^{-i}$ occurs with a natural number $i$ cast to a real number; products and convolutions of such sequences are handled by writing the factor as a power of the constant $e^{-1}$. In Lean the left-hand side is `Real.exp (-(i : ℝ))` and the right-hand side `Real.exp (-1) ^ i`.

## Proof

$(e^{-1})^i=e^{i\cdot(-1)}=e^{-i}$, by the rule for the exponential of a natural multiple.
