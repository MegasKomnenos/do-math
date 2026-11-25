module

public import Parking.Basic.RealBounds
public import Parking.NextColumn.Ramanujan

/-!
# The moment ratio of the birthday law against a square root

For `m ≥ 2`, `D_m + 1 ≤ (3/2) √(π m / 2) - 8/5` (`Dbirth_add_one_le`).  Here
`s_m = ∑_{j=1}^m (m)_j/m^j` (`sbirth m`) is the mean number of parts under the birthday law on `m`
boxes, and `D_m = 3 ((m + 2) s_m - 3m) / (2 (m - s_m))` (`Dbirth m`) is the ratio of the third to
the second factorial moment of the number of parts.

Write `p = √(π m / 2)`.  Since `s_m < m`, the denominator of `D_m` is positive, and the claim is the
inequality

  `s_m (3m + 3p + 4/5) ≤ m (3p + 19/5)`,

whose left side increases with `s_m`.  For `m ≥ 4` it follows from `s_m ≤ p e^{1/(12m)} - 1/3`
(`sbirth_le`) and `e^{1/(12m)} ≤ 1 + 4/(47m)` (`exp_small_le`): after `p² = π m / 2` is
substituted, what remains is an inequality in `m`, `p` and `π` that holds because `π ≤ 3.1416`
(`birthday_poly`).  For `m = 2` and `m = 3` that upper bound for `s_m` is not sharp enough, and the
inequality is checked with the values `s_2 = 3/2` and `s_3 = 17/9`.

The bound that follows directly from `Dbirth_le` and `sbirth_le`,
`D_m + 1 ≤ (3/2) p e^{1/(12m)} - 1`, is larger by more than `3/5`.
-/

@[expose] public section

namespace Parking

open Finset

/-- `e^{1/(12m)} ≤ 1 + 4/(47m)` for `m ≥ 4`: with `y = 1/(12m) ≤ 1/48`,
`e^y ≤ 1 + y + y² ≤ 1 + (49/48) y`, and `49/48 ≤ 48/47`. -/
private theorem exp_small_le {m : ℝ} (hm : 4 ≤ m) : Real.exp (1 / (12 * m)) ≤ 1 + 4 / (47 * m) := by
  have hy0 : 0 ≤ 1 / (12 * m) := by positivity
  have hy : 1 / (12 * m) ≤ 1 / 48 := one_div_le_one_div_of_le (by norm_num) (by linarith)
  have h := exp_le_quadratic hy0 (by linarith)
  have e : 4 / (47 * m) = 48 / 47 * (1 / (12 * m)) := by
    field_simp
    ring
  rw [e]
  nlinarith

/-- The polynomial inequality behind `Dbirth_add_one_le` for `m ≥ 4`: if `p² = π m / 2` with
`π ≤ 3.1416`, then `(p (1 + 4/(47m)) - 1/3) (3m + 3p + 4/5) ≤ m (3p + 19/5)`.  Multiplied by `m`,
the difference of the two sides is
`(24/5 - 3π/2) m² - (13/235) p m - (6/47) π m - (16/235) p + (4/15) m`, in which `p` is bounded by
the tangent `p ≤ p²/5 + 5/4` of the parabola at `p = 5/2`. -/
private theorem birthday_poly {m p π' : ℝ} (hm : 4 ≤ m) (hp2 : p ^ 2 = π' * m / 2)
    (hπ : π' ≤ 3.1416) :
    (p * (1 + 4 / (47 * m)) - 1 / 3) * (3 * m + 3 * p + 4 / 5) ≤ m * (3 * p + 19 / 5) := by
  have hm0 : 0 < m := by linarith
  have hπm : π' * m ≤ 3.1416 * m := mul_le_mul_of_nonneg_right hπ hm0.le
  have hp : p ≤ 0.31416 * m + 1.25 := by linarith [sq_nonneg (p - 5 / 2)]
  have h1 : p ^ 2 * m = π' * m ^ 2 / 2 := by rw [hp2]; ring
  have h2 : π' * m ^ 2 ≤ 3.1416 * m ^ 2 := mul_le_mul_of_nonneg_right hπ (sq_nonneg m)
  have h3 : p * m ≤ (0.31416 * m + 1.25) * m := mul_le_mul_of_nonneg_right hp hm0.le
  have h4 : 4 * m ≤ m ^ 2 := by nlinarith
  have e : p * (1 + 4 / (47 * m)) - 1 / 3 = (p * (m + 4 / 47) - m / 3) / m := by
    field_simp
  rw [e, div_mul_eq_mul_div, div_le_iff₀ hm0]
  linarith

/-- **The moment ratio of the birthday law against a square root**:
`D_m + 1 ≤ (3/2) √(π m / 2) - 8/5` for `m ≥ 2`.  With `p = √(π m / 2)` the claim is
`s_m (3m + 3p + 4/5) ≤ m (3p + 19/5)`.  For `m = 2, 3` this holds with the values of `s_m`, because
`p ≥ 26/15` and `p ≥ 32/15`; for `m ≥ 4` it follows from `s_m ≤ p e^{1/(12m)} - 1/3`. -/
theorem Dbirth_add_one_le {m : ℕ} (hm : 2 ≤ m) :
    Dbirth m + 1 ≤ 3 / 2 * Real.sqrt (Real.pi * m / 2) - 8 / 5 := by
  have hlt := sbirth_lt hm
  suffices h : sbirth m * (3 * (m : ℝ) + 3 * Real.sqrt (Real.pi * m / 2) + 4 / 5)
      ≤ (m : ℝ) * (3 * Real.sqrt (Real.pi * m / 2) + 19 / 5) by
    unfold Dbirth
    rw [← le_sub_iff_add_le, div_le_iff₀ (by linarith)]
    linarith
  have hπ := Real.pi_gt_d2
  rcases Nat.lt_or_ge m 4 with hlt4 | hge4
  · obtain rfl | rfl : m = 2 ∨ m = 3 := by omega
    · have hs : sbirth 2 = 3 / 2 := by
        norm_num [sbirth, sum_Icc_one_eq_range, sum_range_succ, Pb, prod_range_succ]
      have hp : 26 / 15 ≤ Real.sqrt (Real.pi * (2 : ℕ) / 2) :=
        Real.le_sqrt_of_sq_le (by push_cast; linarith)
      rw [hs]
      push_cast at hp ⊢
      linarith
    · have hs : sbirth 3 = 17 / 9 := by
        norm_num [sbirth, sum_Icc_one_eq_range, sum_range_succ, Pb, prod_range_succ]
      have hp : 32 / 15 ≤ Real.sqrt (Real.pi * (3 : ℕ) / 2) :=
        Real.le_sqrt_of_sq_le (by push_cast; linarith)
      rw [hs]
      push_cast at hp ⊢
      linarith
  · have hm4 : (4 : ℝ) ≤ m := by exact_mod_cast hge4
    have hp0 : 0 ≤ Real.sqrt (Real.pi * m / 2) := Real.sqrt_nonneg _
    have hp2 : Real.sqrt (Real.pi * m / 2) ^ 2 = Real.pi * m / 2 :=
      Real.sq_sqrt (by positivity)
    have hs : sbirth m ≤ Real.sqrt (Real.pi * m / 2) * (1 + 4 / (47 * (m : ℝ))) - 1 / 3 :=
      (sbirth_le (by omega)).trans
        (sub_le_sub_right (mul_le_mul_of_nonneg_left (exp_small_le hm4) hp0) _)
    exact (mul_le_mul_of_nonneg_right hs (by positivity)).trans
      (birthday_poly hm4 hp2 Real.pi_lt_d4.le)

end Parking
