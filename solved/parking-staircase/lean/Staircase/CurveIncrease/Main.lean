import Staircase.CurveIncrease.Impulse
import Staircase.CurveIncrease.Ledger

/-!
# The curve increase

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`, and
the step of the column `k` in the row `n` is `b n k - b n (k-1)`.  The curve is the set of positions
`(n, k)` with `k² = (n-k)³`.  This module proves that every column `k ≥ 265` has a positive step in
a row at most one step beyond the curve:

* `curve_step_pos` : for `r ≥ 41` and `(r-1)³ ≤ k² ≤ r³`, `b (k+r) (k-1) < b (k+r) k`;
* `curve_crossing` : for `k ≥ 265` there is a row `j > k` with `(j-k-1)³ ≤ k²` and
  `b j (k-1) < b j k`.

The first statement is the content.  With `R = r + 1`, `N = k + R` and `s = √R ≥ 6.48`, the
hypothesis places the position on the curve, `k ≤ s³ ≤ 1.07593 · k`, and the pair–impulse criterion
`dq_pos_of_pair` reduces the claim to `k · a_k · Λ_R(k+1; N) < 2 · pairSum k R`.

* The pair side.  `pairSum_ge` bounds the pair sum from below by the three sums `W_Σ`, `G`, `𝒜`,
  which `Wsum_ge`, `Gsum_le`, `Asum_le` bound by polynomials in `s`; `pair_numeric` chooses the two
  free parameters of `pairSum_ge` and obtains
  `pairSum k R ≥ a_k e^R · 0.38385 · (1 + 1/(10s)) · (k/s³) · (s²/2 - 1.06385 s + 0.7184)`.
* The impulse side.  `impulse_le` bounds `e^{-R} Λ_R(k+1; N)` from above at the threshold
  `K = (R-1)(2R-1)/(2s) ≥ k`, with the tangent parameter `0.35`, in terms of `P(R)`, `κ₂(R)` and
  `κ₃(R)`; Stirling's bound, `kc2_lower` and `kc3_eq` turn this into an inequality in `s`, and
  `impulse_numeric` shows that the bound lies strictly below the lower bound of the pair side.

The second statement applies the first to the least `r` with `k² < r³`; for `k ≥ 265` this `r` is
at least `42`.
-/

namespace Parking

open Finset

/-- The positive step in the form of the estimates: for `R ≥ 42` and `(R-2)³ ≤ k² ≤ (R-1)³`, the
normalised step `dq k (k+R-1)` is positive. -/
private theorem dq_pos_on_curve {k R : ℕ} (hR : 42 ≤ R) (h1 : (R - 2) ^ 3 ≤ k ^ 2)
    (h2 : k ^ 2 ≤ (R - 1) ^ 3) : 0 < dq k (k + R - 1) := by
  obtain ⟨s, hs_eq⟩ : ∃ s : ℝ, s = Real.sqrt (R : ℝ) := ⟨_, rfl⟩
  have hs : (6.48 : ℝ) ≤ s := by rw [hs_eq]; exact sqrt_ge_648 hR
  have hs0 : 0 < s := by linarith only [hs]
  have hRr : (R : ℝ) = s ^ 2 := by
    rw [hs_eq]; exact (Real.sq_sqrt (Nat.cast_nonneg R)).symm
  have hR42 : (42 : ℝ) ≤ R := by exact_mod_cast hR
  have h1' : ((R : ℝ) - 2) ^ 3 ≤ (k : ℝ) ^ 2 := by
    rw [show (R : ℝ) - 2 = ((R - 2 : ℕ) : ℝ) by rw [Nat.cast_sub (by omega)]; norm_num]
    exact_mod_cast h1
  have h2' : (k : ℝ) ^ 2 ≤ ((R : ℝ) - 1) ^ 3 := by
    rw [show (R : ℝ) - 1 = ((R - 1 : ℕ) : ℝ) by rw [Nat.cast_sub (by omega)]; norm_num]
    exact_mod_cast h2
  have hk0 : (0 : ℝ) ≤ k := Nat.cast_nonneg k
  -- the position lies on the curve, and in the first layer
  obtain ⟨hk1, hk2⟩ := k_window hs0 hRr hR42 hk0 h1' h2'
  have hRk : R + 2 ≤ k := by
    have h3 : (R : ℝ) * 6.48 ≤ s ^ 3 := by
      rw [show s ^ 3 = (R : ℝ) * s by rw [hRr]; ring]
      exact mul_le_mul_of_nonneg_left hs (by linarith only [hR42])
    have h4 : (R : ℝ) + 2 ≤ k := by linarith only [h3, hk2, hR42]
    exact_mod_cast h4
  have hkpos : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  have hC : 0 < cay k * Real.exp (R : ℝ) := mul_pos (cay_pos (by omega)) (Real.exp_pos _)
  -- the pair side
  have hW := Wsum_ge hR
  have hG := Gsum_le (k := k) hR (by rw [← hs_eq]; exact hk2)
  have hA := Asum_le (k := k) hR (by rw [← hs_eq]; exact hk2)
  rw [← hs_eq] at hW hG hA
  have hpair := pair_numeric hs hRr hk1 hk2 hC.le hW hG hA
    (fun θ μ hθ => pairSum_ge (by omega : 1 ≤ k) (by omega : R ≤ k) θ μ hθ)
  -- the impulse side, at the threshold `K ≥ (R-1)^{3/2} ≥ k`
  obtain ⟨K, hKdef⟩ : ∃ K : ℝ, K = ((R : ℝ) - 1) * (2 * (R : ℝ) - 1) / (2 * s) := ⟨_, rfl⟩
  have hs' : s ≠ 0 := hs0.ne'
  have hK : K * (2 * s) = ((R : ℝ) - 1) * (2 * (R : ℝ) - 1) := by
    rw [hKdef]
    field
  obtain ⟨hKR, hkK⟩ := K_facts hs hRr hK h2'
  have himp := impulse_le (R := R) (by omega) hk0 hkK hKR (0.35 : ℝ) (by norm_num)
  have hρ : poissonMass R ≤ c0 / s := by rw [hs_eq]; exact poissonMass_le_c0 (by omega)
  have hX := impulse_numeric hs hRr rfl hK c0_pos c0_le
    (exp_neg_035_bounds rfl).1 (exp_neg_035_bounds rfl).2 hρ himp
    (kc2_lower (m := R) (by omega)) (kc3_eq (m := R) (by omega))
  -- the pair–impulse criterion
  apply dq_pos_of_pair (by omega : 1 ≤ R) (by omega : R ≤ k - 2)
  have hee : Real.exp (R : ℝ) * Real.exp (-(R : ℝ)) = 1 := by
    rw [← Real.exp_add, add_neg_cancel, Real.exp_zero]
  calc (k : ℝ) * cay k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R
      = (k : ℝ) * (cay k * Real.exp (R : ℝ))
          * (Real.exp (-(R : ℝ)) * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R) := by
        linear_combination (-(k : ℝ) * cay k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R) * hee
    _ < (k : ℝ) * (cay k * Real.exp (R : ℝ))
          * (2 * 0.38385 * ((R : ℝ) / 2 - 1.06385 * s + 0.7184) * (1 + 1 / (10 * s)) / s ^ 3) :=
        mul_lt_mul_of_pos_left hX (mul_pos hkpos hC)
    _ = 2 * (cay k * Real.exp (R : ℝ) * (0.38385 * (1 + 1 / (10 * s)) * ((k : ℝ) / s ^ 3)
          * ((R : ℝ) / 2 - 1.06385 * s + 0.7184))) := by
        ring
    _ ≤ 2 * pairSum k R := by linarith only [hpair]

/-- **A positive step on the curve.** For `r ≥ 41` and `(r-1)³ ≤ k² ≤ r³`, the step of the column
`k` in the row `k + r` is positive: `b (k+r) (k-1) < b (k+r) k`.  The position `(k+r, k)` lies
between the curve `k² = (n-k)³` and its translate by one row.  The proof is the pair–impulse
criterion `dq_pos_of_pair` with `R = r + 1`: the lower bound `pairSum_ge` of the pair sum and the
upper bound `impulse_le` of the impulse are compared as functions of `s = √R ≥ 6.48`. -/
theorem curve_step_pos {k r : ℕ} (hr : 41 ≤ r) (h1 : (r - 1) ^ 3 ≤ k ^ 2) (h2 : k ^ 2 ≤ r ^ 3) :
    b (k + r) (k - 1) < b (k + r) k := by
  have h := dq_pos_on_curve (k := k) (R := r + 1) (by omega)
    (by rwa [show r + 1 - 2 = r - 1 by omega]) (by rwa [Nat.add_sub_cancel])
  rw [show k + (r + 1) - 1 = k + r by omega] at h
  exact (dq_pos_iff k (k + r)).1 h

/-- **The curve increase.** Every column `k ≥ 265` has a positive step in a row `j > k` with
`(j-k-1)³ ≤ k²`, that is, at most one row beyond the curve `k² = (n-k)³`.  Take `j = k + r` with
`r` the least number such that `k² < r³`; then `(r-1)³ ≤ k² ≤ r³`, and `r ≥ 42` because
`41³ < 265²`, so `curve_step_pos` applies. -/
theorem curve_crossing (k : ℕ) (hk : 265 ≤ k) :
    ∃ j, k < j ∧ (j - k - 1) ^ 3 ≤ k ^ 2 ∧ b j (k - 1) < b j k := by
  have hex : ∃ r : ℕ, k ^ 2 < r ^ 3 :=
    ⟨k + 1, lt_of_lt_of_le (Nat.pow_lt_pow_left (Nat.lt_succ_self k) (by norm_num))
      (Nat.pow_le_pow_right (Nat.succ_pos k) (by norm_num))⟩
  obtain ⟨r, hr, hmin⟩ : ∃ r : ℕ, k ^ 2 < r ^ 3 ∧ ∀ m < r, ¬ k ^ 2 < m ^ 3 :=
    ⟨Nat.find hex, Nat.find_spec hex, fun m hm => Nat.find_min hex hm⟩
  have hr42 : 42 ≤ r := by
    by_contra hcon
    have h3 : r ^ 3 ≤ 41 ^ 3 := Nat.pow_le_pow_left (by omega) 3
    have h4 : 265 ^ 2 ≤ k ^ 2 := Nat.pow_le_pow_left hk 2
    norm_num at h3 h4
    linarith only [h3, h4, hr]
  have hprev : (r - 1) ^ 3 ≤ k ^ 2 := not_lt.1 (hmin (r - 1) (by omega))
  refine ⟨k + r, by omega, ?_, curve_step_pos (by omega) hprev hr.le⟩
  rwa [show k + r - k - 1 = r - 1 by omega]

end Parking
