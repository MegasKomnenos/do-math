module

public import Parking.Cayley.Basic
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
# The Borel weights decay no faster than `m^{-3/2}`

Write `a_m = cay m = m^{m-1}/m!`.  The numbers `e^{-m} a_m` are the weights of the Borel law, and by
Stirling's formula they behave like `m^{-3/2}/√(2π)`.  This module proves the exact one-sided form
of that statement which the estimates need:

* `borel_log_mono` : `m ↦ e^{-m} a_m m^{3/2}` does not decrease on `m ≥ 1`, stated in logarithms;
* `borel_ratio_le` : for `1 ≤ i ≤ j`, `e^{-i} a_i / (e^{-j} a_j) ≤ 1 + (3/2) z + (3/8) z²` with
  `z = (j-i)/i`.

One step of the monotonicity is `(m + 1/2) · log (1 + 1/m) ≥ 1`, by `a_{m+1}/a_m = (1+1/m)^{m-1}`.
The second statement follows because the ratio is at most `(j/i)^{3/2} = (1+z)^{3/2}` and
`(1+z)³ ≤ (1 + (3/2) z + (3/8) z²)²`.
-/

@[expose] public section

namespace Parking

/-- One step of `borel_log_mono`: the increment of `m ↦ log a_m - m + (3/2) log m` is
`(m + 1/2) · log (1 + 1/m) - 1`, which is nonnegative by `2x/(x+2) ≤ log (1+x)` at `x = 1/m`. -/
private theorem borel_log_step {j : ℕ} (hj : 1 ≤ j) :
    Real.log (cay j) - (j : ℝ) + 3 / 2 * Real.log (j : ℝ)
      ≤ Real.log (cay (j + 1)) - ((j + 1 : ℕ) : ℝ) + 3 / 2 * Real.log ((j + 1 : ℕ) : ℝ) := by
  have hj0 : (0 : ℝ) < j := Nat.cast_pos.mpr (by omega)
  have hx : (0 : ℝ) < 1 + 1 / (j : ℝ) := by positivity
  have hcj : 0 < cay j := cay_pos (by omega)
  have h1 : Real.log (cay (j + 1))
      = ((j : ℝ) - 1) * Real.log (1 + 1 / (j : ℝ)) + Real.log (cay j) := by
    rw [cay_ratio (j := j) (by omega), Real.log_mul (pow_ne_zero _ hx.ne') hcj.ne', Real.log_pow,
      Nat.cast_sub hj, Nat.cast_one]
  have h2 : Real.log ((j + 1 : ℕ) : ℝ) = Real.log (j : ℝ) + Real.log (1 + 1 / (j : ℝ)) := by
    rw [← Real.log_mul hj0.ne' hx.ne', Nat.cast_add_one]
    congr 1
    field_simp
  have h3 : 2 ≤ Real.log (1 + 1 / (j : ℝ)) * (2 * (j : ℝ) + 1) := by
    have h := Real.le_log_one_add_of_nonneg (x := 1 / (j : ℝ)) (by positivity)
    have e : 2 * (1 / (j : ℝ)) / (1 / (j : ℝ) + 2) = 2 / (2 * (j : ℝ) + 1) := by
      field_simp
      ring
    rw [e] at h
    exact (div_le_iff₀ (by positivity)).mp h
  rw [h1, h2, Nat.cast_add_one]
  linarith

/-- `m ↦ log a_m - m + (3/2) log m` does not decrease on `m ≥ 1`; that is, `e^{-m} a_m m^{3/2}` does
not decrease.  The proof is an induction whose step is `(m + 1/2) · log (1 + 1/m) ≥ 1`. -/
theorem borel_log_mono {i j : ℕ} (hi : 1 ≤ i) (hij : i ≤ j) :
    Real.log (cay i) - i + 3 / 2 * Real.log i ≤ Real.log (cay j) - j + 3 / 2 * Real.log j := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ k hk ih => exact ih.trans (borel_log_step (le_trans hi hk))

/-- **The ratio of two Borel weights.** For `1 ≤ i ≤ j` and `z = (j-i)/i`,
`e^{j-i} a_i / a_j ≤ 1 + (3/2) z + (3/8) z²`.  By `borel_log_mono` the square of the ratio is at
most `(j/i)³ = (1+z)³`, and `(1+z)³ ≤ (1 + (3/2) z + (3/8) z²)²` because the difference is
`z³/8 + 9z⁴/64`. -/
theorem borel_ratio_le {i j : ℕ} (hi : 1 ≤ i) (hij : i ≤ j) :
    Real.exp ((j : ℝ) - i) * cay i / cay j
      ≤ 1 + 3 / 2 * (((j : ℝ) - i) / i) + 3 / 8 * (((j : ℝ) - i) / i) ^ 2 := by
  have hi0 : (0 : ℝ) < i := Nat.cast_pos.mpr (by omega)
  have hj0 : (0 : ℝ) < j := Nat.cast_pos.mpr (by omega)
  have hci : 0 < cay i := cay_pos (by omega)
  have hcj : 0 < cay j := cay_pos (by omega)
  have hz : 0 ≤ ((j : ℝ) - i) / i := div_nonneg (sub_nonneg.2 (Nat.cast_le.2 hij)) hi0.le
  have hz1 : 1 + ((j : ℝ) - i) / i = (j : ℝ) / i := by field_simp; ring
  have hρ : 0 < Real.exp ((j : ℝ) - i) * cay i / cay j :=
    div_pos (mul_pos (Real.exp_pos _) hci) hcj
  have hsq : (Real.exp ((j : ℝ) - i) * cay i / cay j) ^ 2 ≤ (1 + ((j : ℝ) - i) / i) ^ 3 := by
    rw [← Real.log_le_log_iff (pow_pos hρ 2) (by positivity), Real.log_pow, Real.log_pow, hz1,
      Real.log_div hj0.ne' hi0.ne', Real.log_div (mul_pos (Real.exp_pos _) hci).ne' hcj.ne',
      Real.log_mul (Real.exp_pos _).ne' hci.ne', Real.log_exp]
    have hmono := borel_log_mono hi hij
    push_cast
    linarith
  have hcube : (1 + ((j : ℝ) - i) / i) ^ 3
      ≤ (1 + 3 / 2 * (((j : ℝ) - i) / i) + 3 / 8 * (((j : ℝ) - i) / i) ^ 2) ^ 2 := by
    nlinarith [pow_nonneg hz 3, pow_nonneg hz 4]
  exact le_of_sq_le_sq (hsq.trans hcube) (by positivity)

end Parking
