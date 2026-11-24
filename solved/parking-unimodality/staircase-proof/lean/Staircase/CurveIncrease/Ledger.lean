import Staircase.CurveIncrease.PairLower
import Staircase.CurveIncrease.RamanujanLower
import Staircase.CurveIncrease.PowerSums
import Staircase.CurveIncrease.Numerics

/-!
# The three sums of the pair side, bounded in `s = √R`

Write `P = poissonMass` and `c₀ = 1/√(2π)`.  The lower bound `pairSum_ge` of the pair sum is stated
with three sums of the convolutions `κ₂`, `κ₃`: `W_Σ = Wsum R`, `G = Gsum k R` and `𝒜 = Asum k R`.
This module bounds them by polynomials in `s = √R`, for `R ≥ 42` and a column `k` with
`s³ ≤ 1.07593 · k`:

* `Wsum_ge` : `W_Σ ≥ s²/2 - 1.06385 s + 0.7184`;
* `Gsum_le` : `G ≤ 2 (0.478731 s³ - 0.974453 s² + 0.642741 s)`;
* `Asum_le` : `𝒜 ≤ 0.478731 s⁵ - 0.974453 s⁴ + 0.642741 s³`.

Three inputs reduce the sums to sums of half-integer powers of `b`.  The closed form `kc3_eq`
expresses `κ₃` by `κ₂` and `P`.  Stirling's bound `poissonMass_le_c0` gives `P(b) ≤ c₀/√b`.  And
`kc2_lower`, the lower half of Ramanujan's estimate in the form
`κ₂(m) ≥ 1/2 - (4/3 + 1/(15m)) · P(m)`, bounds `κ₂` from below; here only a lower bound of `κ₂`
is needed, because `κ₂` enters `G` and `𝒜` with a negative sign after `kc3_eq` is used.  The sums
of `b^{-1/2}`, `b^{-3/2}`, `b^{1/2}`, `b^{3/2}` are bounded in `PowerSums`, and the resulting
inequalities between real numbers are proved in `Numerics`.
-/

namespace Parking

open Finset

/-! ### Bounds of `κ₂` and `κ₃` at one point -/

/-- **The lower bound of `κ₂`.** `κ₂(m) ≥ 1/2 - (4/3 + 1/(15m)) · P(m)` for `m ≥ 2`.  By the closed
form `kc2_eq` this is the lower bound `sbirth_ge` of the mean of the birthday law, the lower half
of Ramanujan's estimate. -/
theorem kc2_lower {m : ℕ} (hm : 2 ≤ m) :
    1 / 2 - (4 / 3 + 1 / (15 * (m : ℝ))) * poissonMass m ≤ kc2 m := by
  have hP := poissonMass_pos m
  have h := mul_le_mul_of_nonneg_left (sbirth_ge hm) hP.le
  have e : poissonMass m * (1 / (2 * poissonMass m)) = 1 / 2 := by
    rw [mul_one_div, mul_comm 2, ← div_div, div_self hP.ne']
  rw [kc2_eq (by omega)]
  linarith

/-- `κ₂(b) ≥ 1/2 - (4/3) c₀/√b - (c₀/15)/(b√b)` for `b ≥ 2`: `kc2_lower` with Stirling's bound. -/
private theorem kc2_ge_sqrt {b : ℕ} (hb : 2 ≤ b) :
    1 / 2 - 4 / 3 * c0 * (1 / Real.sqrt (b : ℝ)) - c0 / 15 * (1 / ((b : ℝ) * Real.sqrt (b : ℝ)))
      ≤ kc2 b := by
  have hb0 : (0 : ℝ) < b := Nat.cast_pos.mpr (by omega)
  have hp : 0 < Real.sqrt (b : ℝ) := Real.sqrt_pos.2 hb0
  have h2 := mul_le_mul_of_nonneg_left (poissonMass_le_c0 (show 1 ≤ b by omega))
    (show (0 : ℝ) ≤ 4 / 3 + 1 / (15 * (b : ℝ)) by positivity)
  have e : (4 / 3 + 1 / (15 * (b : ℝ))) * (c0 / Real.sqrt (b : ℝ))
      = 4 / 3 * c0 * (1 / Real.sqrt (b : ℝ))
        + c0 / 15 * (1 / ((b : ℝ) * Real.sqrt (b : ℝ))) := by
    field
  linarith [kc2_lower hb]

/-- `κ₃(c) ≤ c₀ √c` for `c ≥ 1`: by `kc3_eq`, `κ₃(c) ≤ c · P(c)`, and Stirling's bound. -/
private theorem kc3_le_sqrt {c : ℕ} (hc : 1 ≤ c) : kc3 c ≤ c0 * Real.sqrt (c : ℝ) := by
  have hc0 : (0 : ℝ) < c := Nat.cast_pos.mpr (by omega)
  have hp : 0 < Real.sqrt (c : ℝ) := Real.sqrt_pos.2 hc0
  have h4 := mul_le_mul_of_nonneg_left (poissonMass_le_c0 hc) hc0.le
  have e : (c : ℝ) * (c0 / Real.sqrt (c : ℝ)) = c0 * Real.sqrt (c : ℝ) := by
    nth_rewrite 1 [← Real.mul_self_sqrt hc0.le]
    field
  rw [kc3_eq hc]
  linarith [kc2_nonneg c, poissonMass_pos c]

/-- `ϱ_c ≤ 0.560302 · c/s³` for a cut point `c ≤ R`, when `s³ ≤ 1.07593 · k`. -/
private theorem rhoC_le {k R c : ℕ} (hR : 42 ≤ R)
    (hk : Real.sqrt (R : ℝ) ^ 3 ≤ 1.07593 * (k : ℝ)) (hc : c ≤ R) :
    rhoC ((k : ℝ) + R) c ≤ 0.560302 * (c : ℝ) / Real.sqrt (R : ℝ) ^ 3 := by
  have hcR : (c : ℝ) ≤ R := Nat.cast_le.2 hc
  unfold rhoC
  exact rho_bound (sqrt_ge_648 hR) hk (Nat.cast_nonneg c)
    (by rw [Real.sq_sqrt (Nat.cast_nonneg R)]; exact hcR) (by linarith)

/-! ### Two elementary sums -/

private theorem sum_Icc_two_const (c : ℝ) {n : ℕ} (hn : 1 ≤ n) :
    ∑ _b ∈ Icc 2 n, c = ((n : ℝ) - 1) * c := by
  induction n, hn using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    rw [Finset.sum_Icc_succ_top (by omega : 2 ≤ n + 1), ih]
    push_cast
    ring

private theorem sum_Icc_two_lin (ρ : ℝ) {n : ℕ} (hn : 1 ≤ n) :
    ∑ b ∈ Icc 2 n, (ρ - (b : ℝ)) / 2
      = (((n : ℝ) - 1) * ρ - ((n : ℝ) * ((n : ℝ) + 1) / 2 - 1)) / 2 := by
  induction n, hn using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    rw [Finset.sum_Icc_succ_top (by omega : 2 ≤ n + 1), ih]
    push_cast
    ring

/-! ### The three sums -/

/-- **The weight sum.** For `R ≥ 42` and `s = √R`: `W_Σ ≥ s²/2 - 1.06385 s + 0.7184`.  Each
`κ₂(b)`, `b ≥ 2`, is bounded from below by `kc2_ge_sqrt`, and the sums of `b^{-1/2}` and `b^{-3/2}`
by `sum_Icc_two_inv_sqrt_le` and `sum_Icc_two_inv_sqrt_cube_le`. -/
theorem Wsum_ge {R : ℕ} (hR : 42 ≤ R) :
    (R : ℝ) / 2 - 1.06385 * Real.sqrt (R : ℝ) + 0.7184 ≤ Wsum R := by
  have hs2 : (R : ℝ) = Real.sqrt (R : ℝ) ^ 2 := (Real.sq_sqrt (Nat.cast_nonneg R)).symm
  have h1 : ∑ b ∈ Icc 2 R, kc2 b ≤ Wsum R :=
    Finset.sum_le_sum_of_subset_of_nonneg
      (fun b hb => by rw [mem_Icc] at hb ⊢; omega) (fun b _ _ => kc2_nonneg b)
  have h2 := Finset.sum_le_sum fun b (hb : b ∈ Icc 2 R) => kc2_ge_sqrt (mem_Icc.1 hb).1
  rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum,
    sum_Icc_two_const (1 / 2 : ℝ) (by omega : 1 ≤ R)] at h2
  have h5 := Wsum_numeric (sqrt_ge_648 hR) hs2 c0_pos.le c0_le
    (sum_Icc_two_inv_sqrt_le (by omega : 2 ≤ R)) (sum_Icc_two_inv_sqrt_cube_le R)
  linarith

/-- **The sum `G`.** For `R ≥ 42`, `s = √R` and `s³ ≤ 1.07593 · k`:
`G ≤ 2 (0.478731 s³ - 0.974453 s² + 0.642741 s)`.  By `kc3_eq` the first two sums of `G` are
`∑_{b≥2} (3(b-1) P(b) - (5/2) κ₂(b))`, which Stirling's bound and `kc2_ge_sqrt` reduce to sums of
half-integer powers; the correction `∑_c κ₃(c) ϱ_c` is bounded by `kc3_le_sqrt` and `rhoC_le`. -/
theorem Gsum_le {k R : ℕ} (hR : 42 ≤ R) (hk : Real.sqrt (R : ℝ) ^ 3 ≤ 1.07593 * (k : ℝ)) :
    Gsum k R ≤ 2 * (0.478731 * Real.sqrt (R : ℝ) ^ 3 - 0.974453 * Real.sqrt (R : ℝ) ^ 2
      + 0.642741 * Real.sqrt (R : ℝ)) := by
  have hs2 : (R : ℝ) = Real.sqrt (R : ℝ) ^ 2 := (Real.sq_sqrt (Nat.cast_nonneg R)).symm
  have hsplit : ∑ c ∈ Ioo 0 R, kc3 c * (1 + rhoC ((k : ℝ) + R) c)
      = ∑ c ∈ Ioo 0 R, kc3 c + ∑ c ∈ Ioo 0 R, kc3 c * rhoC ((k : ℝ) + R) c := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  have hext : ∑ c ∈ Ioo 0 R, kc3 c ≤ ∑ b ∈ Icc 1 R, kc3 b :=
    Finset.sum_le_sum_of_subset_of_nonneg
      (fun b hb => by rw [mem_Ioo] at hb; rw [mem_Icc]; omega) (fun b _ _ => kc3_nonneg b)
  have hmain : ∑ b ∈ Icc 1 R, (7 / 2 * kc2 b + 2 * kc3 b) + ∑ b ∈ Icc 1 R, kc3 b
      = ∑ b ∈ Icc 2 R, (3 * ((b : ℝ) - 1) * poissonMass b - 5 / 2 * kc2 b) := by
    rw [← Finset.sum_add_distrib]
    have e1 : ∑ b ∈ Icc 1 R, (7 / 2 * kc2 b + 2 * kc3 b + kc3 b)
        = ∑ b ∈ Icc 1 R, (3 * ((b : ℝ) - 1) * poissonMass b - 5 / 2 * kc2 b) :=
      Finset.sum_congr rfl fun b hb => by rw [kc3_eq (mem_Icc.1 hb).1]; ring
    rw [e1]
    symm
    refine Finset.sum_subset (fun b hb => by rw [mem_Icc] at hb ⊢; omega) fun b hb hnb => ?_
    rw [mem_Icc] at hb hnb
    rw [show b = 1 by omega, kc2_one]
    simp
  have hsum := Finset.sum_le_sum fun b (hb : b ∈ Icc 2 R) =>
    term_G (Real.sqrt_pos.2 (show (0 : ℝ) < b from Nat.cast_pos.mpr (by rw [mem_Icc] at hb; omega)))
      (Real.sq_sqrt (Nat.cast_nonneg b)).symm
      (show (1 : ℝ) ≤ b by exact_mod_cast (show 1 ≤ b by rw [mem_Icc] at hb; omega))
      (poissonMass_le_c0 (show 1 ≤ b by rw [mem_Icc] at hb; omega)) (kc2_ge_sqrt (mem_Icc.1 hb).1)
  have hlin : ∑ b ∈ Icc 2 R, (c0 * (3 * Real.sqrt (b : ℝ) + 1 / 3 * (1 / Real.sqrt (b : ℝ))
          + 1 / 6 * (1 / ((b : ℝ) * Real.sqrt (b : ℝ)))) - 5 / 4)
      = c0 * (3 * ∑ b ∈ Icc 2 R, Real.sqrt (b : ℝ) + 1 / 3 * ∑ b ∈ Icc 2 R, 1 / Real.sqrt (b : ℝ)
          + 1 / 6 * ∑ b ∈ Icc 2 R, 1 / ((b : ℝ) * Real.sqrt (b : ℝ)))
        - ((R : ℝ) - 1) * (5 / 4) := by
    rw [Finset.sum_sub_distrib, ← Finset.mul_sum, Finset.sum_add_distrib, Finset.sum_add_distrib,
      ← Finset.mul_sum, ← Finset.mul_sum, ← Finset.mul_sum,
      sum_Icc_two_const (5 / 4 : ℝ) (by omega : 1 ≤ R)]
  rw [hlin] at hsum
  have hrho : ∑ c ∈ Ioo 0 R, kc3 c * rhoC ((k : ℝ) + R) c
      ≤ c0 * 0.560302 / Real.sqrt (R : ℝ) ^ 3
        * ∑ c ∈ Ioo 0 R, (c : ℝ) * Real.sqrt (c : ℝ) := by
    rw [Finset.mul_sum]
    refine Finset.sum_le_sum fun c hc => ?_
    rw [mem_Ioo] at hc
    have h4 := mul_le_mul (kc3_le_sqrt (show 1 ≤ c by omega)) (rhoC_le (k := k) hR hk hc.2.le)
      (rhoC_nonneg (k := k) hc.2.le) (mul_nonneg c0_pos.le (Real.sqrt_nonneg _))
    exact h4.trans (le_of_eq (by ring))
  have hfin := Gsum_numeric (sqrt_ge_648 hR) hs2 c0_pos.le c0_le
    (sum_Icc_two_inv_sqrt_le (by omega : 2 ≤ R)) (sum_Icc_two_inv_sqrt_cube_le R)
    (sum_Icc_two_sqrt_le (by omega : 2 ≤ R)) (sum_Ioo_sqrt_cube_le R)
  unfold Gsum
  rw [hsplit]
  linarith

/-- **The sum `𝒜`.** For `R ≥ 42`, `s = √R` and `s³ ≤ 1.07593 · k`:
`𝒜 ≤ 0.478731 s⁵ - 0.974453 s⁴ + 0.642741 s³`.  The proof is that of `Gsum_le` with the weights
`R - b/2`, `R - b` and `R - c`: by `kc3_eq` the main part is
`∑_{b≥2} ((3R - 2b)(b-1) P(b) - (5R/2 - b) κ₂(b))`. -/
theorem Asum_le {k R : ℕ} (hR : 42 ≤ R) (hk : Real.sqrt (R : ℝ) ^ 3 ≤ 1.07593 * (k : ℝ)) :
    Asum k R ≤ 0.478731 * Real.sqrt (R : ℝ) ^ 5 - 0.974453 * Real.sqrt (R : ℝ) ^ 4
      + 0.642741 * Real.sqrt (R : ℝ) ^ 3 := by
  have hs2 : (R : ℝ) = Real.sqrt (R : ℝ) ^ 2 := (Real.sq_sqrt (Nat.cast_nonneg R)).symm
  have hsplit : ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c * (1 + rhoC ((k : ℝ) + R) c)
      = ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c
        + ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c * rhoC ((k : ℝ) + R) c := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  have hext : ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c = ∑ b ∈ Icc 1 R, ((R : ℝ) - b) * kc3 b := by
    refine Finset.sum_subset (fun b hb => by rw [mem_Ioo] at hb; rw [mem_Icc]; omega)
      fun b hb hnb => ?_
    rw [mem_Icc] at hb
    rw [mem_Ioo] at hnb
    rw [show b = R by omega]
    simp
  have hmain : ∑ b ∈ Icc 1 R, (((R : ℝ) - (b : ℝ) / 2) * (kc2 b + 2 * kc3 b)
          + 5 / 2 * ((R : ℝ) - b) * kc2 b)
        + ∑ b ∈ Icc 1 R, ((R : ℝ) - b) * kc3 b
      = ∑ b ∈ Icc 2 R, ((3 * (R : ℝ) - 2 * (b : ℝ)) * ((b : ℝ) - 1) * poissonMass b
          - (5 / 2 * (R : ℝ) - (b : ℝ)) * kc2 b) := by
    rw [← Finset.sum_add_distrib]
    have e1 : ∑ b ∈ Icc 1 R, (((R : ℝ) - (b : ℝ) / 2) * (kc2 b + 2 * kc3 b)
          + 5 / 2 * ((R : ℝ) - b) * kc2 b + ((R : ℝ) - b) * kc3 b)
        = ∑ b ∈ Icc 1 R, ((3 * (R : ℝ) - 2 * (b : ℝ)) * ((b : ℝ) - 1) * poissonMass b
          - (5 / 2 * (R : ℝ) - (b : ℝ)) * kc2 b) :=
      Finset.sum_congr rfl fun b hb => by rw [kc3_eq (mem_Icc.1 hb).1]; ring
    rw [e1]
    symm
    refine Finset.sum_subset (fun b hb => by rw [mem_Icc] at hb ⊢; omega) fun b hb hnb => ?_
    rw [mem_Icc] at hb hnb
    rw [show b = 1 by omega, kc2_one]
    simp
  have hsum := Finset.sum_le_sum fun b (hb : b ∈ Icc 2 R) =>
    term_A (Rr := (R : ℝ))
      (Real.sqrt_pos.2 (show (0 : ℝ) < b from Nat.cast_pos.mpr (by rw [mem_Icc] at hb; omega)))
      (Real.sq_sqrt (Nat.cast_nonneg b)).symm
      (show (1 : ℝ) ≤ b by exact_mod_cast (show 1 ≤ b by rw [mem_Icc] at hb; omega))
      (Nat.cast_le.2 (mem_Icc.1 hb).2)
      (poissonMass_le_c0 (show 1 ≤ b by rw [mem_Icc] at hb; omega)) (kc2_ge_sqrt (mem_Icc.1 hb).1)
  have hlin : ∑ b ∈ Icc 2 R, (c0 * (-2 * ((b : ℝ) * Real.sqrt (b : ℝ))
            + (3 * (R : ℝ) + 2 / 3) * Real.sqrt (b : ℝ)
            + ((R : ℝ) / 3 - 1 / 15) * (1 / Real.sqrt (b : ℝ))
            + (R : ℝ) / 6 * (1 / ((b : ℝ) * Real.sqrt (b : ℝ))))
          - (5 / 2 * (R : ℝ) - (b : ℝ)) / 2)
      = c0 * (-2 * ∑ b ∈ Icc 2 R, (b : ℝ) * Real.sqrt (b : ℝ)
            + (3 * (R : ℝ) + 2 / 3) * ∑ b ∈ Icc 2 R, Real.sqrt (b : ℝ)
            + ((R : ℝ) / 3 - 1 / 15) * ∑ b ∈ Icc 2 R, 1 / Real.sqrt (b : ℝ)
            + (R : ℝ) / 6 * ∑ b ∈ Icc 2 R, 1 / ((b : ℝ) * Real.sqrt (b : ℝ)))
        - (((R : ℝ) - 1) * (5 / 2 * (R : ℝ)) - ((R : ℝ) * ((R : ℝ) + 1) / 2 - 1)) / 2 := by
    rw [Finset.sum_sub_distrib, ← Finset.mul_sum, Finset.sum_add_distrib, Finset.sum_add_distrib,
      Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, ← Finset.mul_sum,
      ← Finset.mul_sum, sum_Icc_two_lin (5 / 2 * (R : ℝ)) (by omega : 1 ≤ R)]
  rw [hlin] at hsum
  have hrho : ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c * rhoC ((k : ℝ) + R) c
      ≤ c0 * 0.560302 / Real.sqrt (R : ℝ) ^ 3
        * ∑ c ∈ Ioo 0 R, (c : ℝ) * Real.sqrt (c : ℝ) * ((R : ℝ) - c) := by
    rw [Finset.mul_sum]
    refine Finset.sum_le_sum fun c hc => ?_
    rw [mem_Ioo] at hc
    have hcR : (0 : ℝ) ≤ (R : ℝ) - c := sub_nonneg.2 (Nat.cast_le.2 hc.2.le)
    have h4 := mul_le_mul (kc3_le_sqrt (show 1 ≤ c by omega)) (rhoC_le (k := k) hR hk hc.2.le)
      (rhoC_nonneg (k := k) hc.2.le) (mul_nonneg c0_pos.le (Real.sqrt_nonneg _))
    have h5 := mul_le_mul_of_nonneg_left h4 hcR
    calc ((R : ℝ) - c) * kc3 c * rhoC ((k : ℝ) + R) c
        = ((R : ℝ) - c) * (kc3 c * rhoC ((k : ℝ) + R) c) := by ring
      _ ≤ _ := h5
      _ = _ := by ring
  have hfin := Asum_numeric (sqrt_ge_648 hR) hs2 c0_pos.le c0_le
    (sum_Icc_two_inv_sqrt_le (by omega : 2 ≤ R)) (sum_Icc_two_inv_sqrt_cube_le R)
    (sum_Icc_two_sqrt_le (by omega : 2 ≤ R)) (sum_Icc_two_sqrt_cube_ge (by omega : 2 ≤ R))
    (sum_Ioo_sqrt_cube_mul_le R)
  unfold Asum
  rw [hsplit]
  linarith

end Parking
