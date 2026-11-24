module

public import Parking.Cayley.Basic
public import Mathlib.RingTheory.PowerSeries.Derivative
public import Mathlib.RingTheory.PowerSeries.Inverse

/-!
# Convolution identities for the tree series

With `P = ∑ c_n x^n`, `T = x P` and `E = 1/P`, the identity `cc_rec` says `P' = T' P`
(`deriv_Pser`).  Power-series algebra then gives `E' = -E T' = -(1 + x T')` and
`(1 - T)(1 + x T') = 1`.  Since the coefficients of `1 + x T'` are `ren n = n^n/n!`, the first
identity says that `E = 1 - ∑_{m ≥ 1} ε_m x^m` (`coeff_Eser_succ`), and comparing coefficients in
`E P = 1` and in `(1 - T)(1 + x T') = 1` gives the two convolution identities `eps_conv` and
`ren_conv`.

The power series and their properties live in the namespace `Parking.Cayley.TreeSeries`.
-/

@[expose] public section

namespace Parking

open Finset

namespace TreeSeries

local notation "Dx" => PowerSeries.derivative (R := ℝ)
local notation "Xs" => (PowerSeries.X : PowerSeries ℝ)

/-! ### Coefficients of a product -/

/-- Coefficient of a product of power series as a sum over `range (n + 1)`. -/
theorem coeff_mul_range (f g : PowerSeries ℝ) (n : ℕ) :
    PowerSeries.coeff n (f * g) =
      ∑ j ∈ range (n + 1), PowerSeries.coeff j f * PowerSeries.coeff (n - j) g := by
  rw [PowerSeries.coeff_mul]
  exact Finset.Nat.sum_antidiagonal_eq_sum_range_succ
    (fun i j => PowerSeries.coeff i f * PowerSeries.coeff j g) n

/-- Coefficient of a product of power series, with the term of index `0` split off. -/
theorem coeff_mul_split (f g : PowerSeries ℝ) (n : ℕ) :
    PowerSeries.coeff n (f * g) = PowerSeries.coeff 0 f * PowerSeries.coeff n g +
      ∑ m ∈ Icc 1 n, PowerSeries.coeff m f * PowerSeries.coeff (n - m) g := by
  rw [coeff_mul_range, Finset.sum_range_eq_add_Ico _ (show 0 < n + 1 by omega),
    Finset.Ico_add_one_right_eq_Icc, Nat.sub_zero]

/-! ### The series `P`, `T = x P`, `E = 1/P` -/

/-- The generating series `P = ∑ c_n x^n`. -/
noncomputable def Pser : PowerSeries ℝ := PowerSeries.mk cc

/-- The tree series `T = x P = ∑ a_j x^j`. -/
noncomputable def Tser : PowerSeries ℝ := PowerSeries.X * Pser

/-- `E = 1/P`. -/
noncomputable def Eser : PowerSeries ℝ := Pser⁻¹

/-- The coefficient of $X^n$ in the series $P$ is $c_n = (n+1)^{n-1}/n!$. -/
theorem coeff_Pser (n : ℕ) : PowerSeries.coeff n Pser = cc n :=
  PowerSeries.coeff_mk n cc

private theorem constantCoeff_Pser : PowerSeries.constantCoeff Pser = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff_apply, coeff_Pser, cc_zero]

/-- The coefficient of $X^n$ in the tree series $T = XP$ is the Cayley coefficient $a_n$, for every
$n \ge 0$. -/
theorem coeff_Tser (n : ℕ) : PowerSeries.coeff n Tser = cay n := by
  cases n with
  | zero => rw [Tser, PowerSeries.coeff_zero_X_mul, cay_zero]
  | succ n => rw [Tser, PowerSeries.coeff_succ_X_mul, coeff_Pser, cc]

/-- The series $E = 1/P$ is the inverse of $P = \sum_n c_n X^n$: $E \cdot P = 1$. -/
theorem Eser_mul_Pser : Eser * Pser = 1 :=
  PowerSeries.inv_mul_cancel Pser (by rw [constantCoeff_Pser]; exact one_ne_zero)

/-- `cc_rec` in power-series form: `P' = T' P`. -/
private theorem deriv_Pser : Dx Pser = Dx Tser * Pser := by
  refine PowerSeries.ext fun n => ?_
  rw [PowerSeries.coeff_derivative, coeff_mul_range, coeff_Pser, mul_comm (cc (n + 1)) _,
    cc_rec n]
  refine sum_congr rfl fun j _ => ?_
  rw [PowerSeries.coeff_derivative, coeff_Tser, coeff_Pser, show cay (j + 1) = cc j from rfl]
  ring

/-- `T' = P + x P'`. -/
private theorem deriv_Tser : Dx Tser = Pser + Xs * Dx Pser := by
  rw [Tser, Derivation.leibniz, PowerSeries.derivative_X, smul_eq_mul, smul_eq_mul, mul_one,
    add_comm]

/-- `E T' = 1 + x T'`. -/
private theorem Eser_mul_deriv_Tser : Eser * Dx Tser = 1 + Xs * Dx Tser := by
  have h1 := deriv_Pser
  have h2 := deriv_Tser
  have h3 := Eser_mul_Pser
  linear_combination Eser * h2 + Eser * Xs * h1 + (1 + Xs * Dx Tser) * h3

/-- `E' = -E T'`. -/
theorem deriv_Eser : Dx Eser = -(Eser * Dx Tser) := by
  have h1 := deriv_Pser
  have h3 := Eser_mul_Pser
  have h4 : Dx Eser = -Eser ^ 2 * Dx Pser := PowerSeries.derivative_inv' Pser
  linear_combination h4 - Eser ^ 2 * h1 - Eser * Dx Tser * h3

/-- `(1 - T)(1 + x T') = 1`. -/
private theorem one_sub_Tser_mul : (1 - Tser) * (1 + Xs * Dx Tser) = 1 := by
  have h1 := deriv_Pser
  have h2 := deriv_Tser
  have h5 : Tser = Xs * Pser := rfl
  linear_combination Xs * h2 + Xs ^ 2 * h1 - (1 + Xs * Dx Tser) * h5

/-- The coefficients of `1 + x T'` are `ren n = n^n/n!`. -/
private theorem coeff_Rser (n : ℕ) : PowerSeries.coeff n (1 + Xs * Dx Tser) = ren n := by
  cases n with
  | zero =>
    rw [map_add, PowerSeries.coeff_zero_X_mul, PowerSeries.coeff_zero_one, add_zero, ren,
      Nat.cast_zero, pow_zero, Nat.factorial_zero, Nat.cast_one, div_one]
  | succ n =>
    rw [map_add, PowerSeries.coeff_succ_X_mul, PowerSeries.coeff_derivative, coeff_Tser,
      PowerSeries.coeff_one, ite_eq_right (show ¬ (n + 1 = 0) by omega), zero_add, cay_succ, ren,
      Nat.cast_add, Nat.cast_one]
    ring

/-- The constant coefficient of the series $E = 1/P$ is $1$, where $P = \sum_n c_n X^n$ and $c_n =
(n+1)^{n-1}/n!$. -/
theorem coeff_Eser_zero : PowerSeries.coeff 0 Eser = 1 := by
  rw [PowerSeries.coeff_zero_eq_constantCoeff_apply, Eser, PowerSeries.constantCoeff_inv,
    constantCoeff_Pser, inv_one]

private theorem coeff_Eser_succ (m : ℕ) : PowerSeries.coeff (m + 1) Eser = -eps (m + 1) := by
  have h := congrArg (PowerSeries.coeff m) deriv_Eser
  rw [Eser_mul_deriv_Tser, PowerSeries.coeff_derivative, map_neg, coeff_Rser, ← mul_eps m] at h
  have hm : ((m : ℝ) + 1) ≠ 0 := by positivity
  have h' : PowerSeries.coeff (m + 1) Eser * ((m : ℝ) + 1) = -eps (m + 1) * ((m : ℝ) + 1) := by
    rw [h]
    ring
  exact mul_right_cancel₀ hm h'

/-- Coefficients of `E f`: `[x^n](E f) = f_n - ∑_{m=1}^n ε_m f_{n-m}`. -/
theorem coeff_Eser_mul (f : PowerSeries ℝ) (n : ℕ) :
    PowerSeries.coeff n (Eser * f) =
      PowerSeries.coeff n f - ∑ m ∈ Icc 1 n, eps m * PowerSeries.coeff (n - m) f := by
  rw [coeff_mul_split, coeff_Eser_zero, one_mul, sub_eq_add_neg, ← Finset.sum_neg_distrib]
  congr 1
  refine sum_congr rfl fun m hm => ?_
  rw [mem_Icc] at hm
  obtain ⟨m', rfl⟩ : ∃ m', m = m' + 1 := ⟨m - 1, by omega⟩
  rw [coeff_Eser_succ]
  ring

end TreeSeries

open TreeSeries

/-- `∑_{m=1}^n ε_m c_{n-m} = c_n` for `n ≥ 1`: the coefficients of `E P = 1`. -/
theorem eps_conv {n : ℕ} (hn : 1 ≤ n) : ∑ m ∈ Icc 1 n, eps m * cc (n - m) = cc n := by
  have h := congrArg (PowerSeries.coeff n) Eser_mul_Pser
  rw [coeff_Eser_mul, PowerSeries.coeff_one, ite_eq_right (show ¬ n = 0 by omega), coeff_Pser] at h
  simp only [coeff_Pser] at h
  linarith

/-- Renewal identity `∑_{j ≤ n} a_j ren_{n-j} = ren_n` for `n ≥ 1` (the term `j = 0` vanishes):
the coefficients of `(1 - T)(1 + x T') = 1`. -/
theorem ren_conv {n : ℕ} (hn : 1 ≤ n) : ∑ j ∈ range (n + 1), cay j * ren (n - j) = ren n := by
  have h := congrArg (PowerSeries.coeff n) one_sub_Tser_mul
  rw [sub_mul, one_mul, map_sub, coeff_mul_range, coeff_Rser, PowerSeries.coeff_one,
    ite_eq_right (show ¬ n = 0 by omega)] at h
  simp only [coeff_Tser, coeff_Rser] at h
  linarith

end Parking
