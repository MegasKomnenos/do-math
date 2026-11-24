module

public import Parking.ChainColumn.Numerics
public import Parking.ChainColumn.TwoPoint

/-!
# The rows up to `k + 0.47 k`: the parking column in the two-point theorem

With `x = 1/γ_k`, the tilted column `η_j = x^j δ_j` and the tilted profile `U_j = x^j β^{(k-1)}_j`
satisfy the hypotheses of `two_point` for the tilted kernel `κ_m = x^m ε_m`.

* `caseA` : if column `k ≥ 42` is nonpositive on the rows `k ≤ j < k + rq` and positive on the
  rows `k + rq ≤ j < n`, where `n - k ≤ 0.47 k`, then it is positive at the row `n`.
-/

@[expose] public section

namespace Parking

open Finset

/-- The column equation in tilted form. -/
private theorem stepD_col {k n : ℕ} (hk : 2 ≤ k) (hn1 : k + 1 ≤ n) (hn2 : n ≤ 2 * k - 1) :
    stepD k n = 2 * xk k / (n : ℝ) * profD k (n - 1)
      + ((k : ℝ) + 1) * xk k / (n : ℝ) * stepD k (n - 1)
      + ∑ m ∈ Icc 1 (n - k), kapx k m * stepD k (n - m) := by
  have h := dq_col hk hn1 hn2
  have e1 : xk k ^ n = xk k * xk k ^ (n - 1) := by
    rw [← pow_succ', Nat.sub_add_cancel (by omega)]
  have hsum : ∑ m ∈ Icc 1 (n - k), kapx k m * stepD k (n - m)
      = xk k ^ n * ∑ m ∈ Icc 1 (n - k), eps m * dq k (n - m) := by
    rw [mul_sum]
    refine sum_congr rfl (fun m hm => ?_)
    rw [mem_Icc] at hm
    have e2 : xk k ^ n = xk k ^ m * xk k ^ (n - m) := by
      rw [← pow_add, Nat.add_sub_cancel' (by omega)]
    unfold kapx stepD
    rw [e2]
    ring
  rw [hsum]
  unfold stepD profD
  rw [h, e1]
  ring

private theorem stepD_base {k : ℕ} (hk : 2 ≤ k) : stepD k k = -profD k k := by
  unfold stepD profD dq
  rw [bq_eq_zero (k := k) (n := k) (by omega) (le_refl k)]
  ring

/-- The diagonal lower bound in tilted form. -/
private theorem stepD_diag {k j : ℕ} (hk : 2 ≤ k) (hj1 : k + 1 ≤ j) (hj2 : j ≤ 2 * k) :
    profD k (j - 1) - profD k j ≤ stepD k j := by
  have h := bq_diag_lower hk (show 1 ≤ j by omega)
  have hx := CrossCrit.xk_pos k
  have e1 : xk k ^ j = xk k * xk k ^ (j - 1) := by
    rw [← pow_succ', Nat.sub_add_cancel (by omega)]
  have h2 := mul_le_mul_of_nonneg_left h (pow_nonneg hx.le j)
  have e3 : xk k ^ j * (gam k * bq (k - 1) (j - 1)) = xk k ^ (j - 1) * bq (k - 1) (j - 1) := by
    rw [e1]
    calc xk k * xk k ^ (j - 1) * (gam k * bq (k - 1) (j - 1))
        = (xk k * gam k) * (xk k ^ (j - 1) * bq (k - 1) (j - 1)) := by ring
      _ = xk k ^ (j - 1) * bq (k - 1) (j - 1) := by rw [CrossCrit.xk_mul_gam, one_mul]
  rw [e3] at h2
  unfold stepD profD dq
  linarith

/-- **The rows up to `k + 0.47 k`.**  If column `k ≥ 42` is nonpositive on the rows
`k ≤ j < k + rq` and positive on the rows `k + rq ≤ j < k + rq + t`, and `rq + t ≤ 0.47 k`, then
it is positive at the row `k + rq + t`. -/
theorem caseA {k rq t : ℕ} (hk : 42 ≤ k) (hrq : 1 ≤ rq) (ht : 1 ≤ t)
    (h47 : 100 * (rq + t) ≤ 47 * k)
    (hneg : ∀ j, k ≤ j → j < k + rq → dq k j ≤ 0)
    (hpos : ∀ j, k + rq ≤ j → j < k + rq + t → 0 < dq k j) :
    0 < dq k (k + rq + t) := by
  have hk2 : 2 ≤ k := by omega
  have hx := CrossCrit.xk_pos k
  have hK : (0 : ℝ) < (k : ℝ) + 1 := by positivity
  have hq0 : (0 : ℝ) < ((k + rq : ℕ) : ℝ) := by
    have h0 : 0 < k + rq := by omega
    exact_mod_cast h0
  have hn0 : (0 : ℝ) < ((k + rq + t : ℕ) : ℝ) := by
    have h0 : 0 < k + rq + t := by omega
    exact_mod_cast h0
  -- the column equation at the rows `q = k + rq` and `n = k + rq + t`
  have hCq := stepD_col (k := k) (n := k + rq) hk2 (by omega) (by omega)
  rw [show k + rq - k = rq by omega] at hCq
  have hCn := stepD_col (k := k) (n := k + rq + t) hk2 (by omega) (by omega)
  rw [show k + rq + t - k = rq + t by omega] at hCn
  -- the two-point condition, from the monotonicity of `(k + ρ) κ_ρ`
  have hii : kapx k (rq + t) * (2 * xk k / ((k + rq : ℕ) : ℝ))
      ≤ kapx k rq * (2 * xk k / ((k + rq + t : ℕ) : ℝ)) := by
    have hF := Fk_anti (k := k) (a := rq) (b := rq + t) hk hrq (by omega) h47
    have eq1 : ((k + rq : ℕ) : ℝ) = (k : ℝ) + (rq : ℝ) := Nat.cast_add k rq
    have eq2 : ((k + rq + t : ℕ) : ℝ) = (k : ℝ) + ((rq + t : ℕ) : ℝ) := by
      rw [Nat.add_assoc, Nat.cast_add]
    rw [mul_div_assoc', mul_div_assoc', div_le_div_iff₀ hq0 hn0, eq1, eq2]
    have h1 := mul_le_mul_of_nonneg_left hF (mul_nonneg zero_le_two hx.le)
    linarith
  have h : 0 < xk k ^ (k + rq + t) * dq k (k + rq + t) :=
    two_point (stepD k) (profD k) (kapx k)
      (2 * xk k / ((k + rq : ℕ) : ℝ)) (2 * xk k / ((k + rq + t : ℕ) : ℝ))
      (((k : ℝ) + 1) * xk k / ((k + rq : ℕ) : ℝ)) (((k : ℝ) + 1) * xk k / ((k + rq + t : ℕ) : ℝ))
      k rq t hrq ht
      (div_nonneg (mul_nonneg zero_le_two hx.le) hq0.le)
      (div_nonneg (mul_nonneg hK.le hx.le) hq0.le)
      (div_pos (mul_pos hK hx) hn0)
      hCq hCn (stepD_base hk2)
      (fun j hj1 hj2 => stepD_diag hk2 hj1 (by omega))
      (fun j => mul_nonneg (pow_nonneg hx.le j) (bq_nonneg _ _))
      (fun m hm _ => kapx_pos k hm)
      (fun m hm hm2 => kapx_succ_le hk2 hm (by omega))
      (fun m hm hmr => kapx_cross hm hmr t)
      hii
      (fun j h1 h2 => mul_nonpos_of_nonneg_of_nonpos (pow_nonneg hx.le j) (hneg j h1 h2))
      (fun j h1 h2 => mul_pos (pow_pos hx j) (hpos j h1 h2))
  exact (mul_pos_iff_of_pos_left (pow_pos hx _)).mp h

end Parking
