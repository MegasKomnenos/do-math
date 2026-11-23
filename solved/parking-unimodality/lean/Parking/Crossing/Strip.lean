import Parking.Crossing.Bounds
import Parking.Crossing.StripNumerics

/-!
# The crossing happens inside the strip

For every `k ≥ 265`, `R = ϱ(k) + 1` (i.e. `25 (R-1)³ ≤ 121 k² < 25 R³`) satisfies the hypotheses of
`cross_of_bounds` (`cross_strip_hyp`).  Hence column `k` turns positive at some row
`j ≤ k + ϱ(k) + 1` (`crossing_strip`).

## Organisation of the proof of `cross_strip_hyp`

The scale parameter is `u = (5/(11k))^{1/3}` (`k u³ = 5/11`), so that the hypothesis on `R` reads
`1 < R u² ≤ 1 + u²`, and `k ≥ 265` gives `u ≤ 0.119705 ≤ 3/25`.  In terms of `u`:
`ā = (11/2) u³`, `a̲ = (11/2) u³ - (484/75) u⁶`, `ā R ≤ 0.6679`, `e^{ā} ≤ 106/105`,
`0.39894 ≤ c₀ ≤ 0.39895`, `1 - (101/200) u² ≤ √(R-1) u ≤ 1`, `1 ≤ √R u ≤ 1 + u²/2`,
`√(R+1) u ≤ 1 + u²`.  With these, `cstrip_tlow_core` gives `t̲ ≥ 0` and `cstrip_main` gives the
main inequality (both in `Parking.Crossing.StripNumerics`, which works with real variables only).
-/

namespace Parking

open Finset

/-- For `K > 0` there is `u > 0` with `K u³ = 5/11`. -/
private theorem exists_scale {K : ℝ} (hK : 0 < K) : ∃ u : ℝ, 0 < u ∧ K * u ^ 3 = 5 / 11 := by
  have hK' : K ≠ 0 := hK.ne'
  refine ⟨Real.exp (Real.log (5 / (11 * K)) / 3), Real.exp_pos _, ?_⟩
  have h : Real.exp (Real.log (5 / (11 * K)) / 3) ^ 3 = 5 / (11 * K) := by
    have h2 : ((3 : ℕ) : ℝ) * (Real.log (5 / (11 * K)) / 3) = Real.log (5 / (11 * K)) := by
      push_cast
      ring
    rw [← Real.exp_nat_mul, h2, Real.exp_log (by positivity)]
  rw [h]
  field

/-- `e^a ≤ 106/105` for `0 ≤ a ≤ 1/106`. -/
private theorem exp_le_of_le {a : ℝ} (h0 : 0 ≤ a) (h1 : a ≤ 1 / 106) :
    Real.exp a ≤ 106 / 105 := by
  have h3 := Real.exp_bound_div_one_sub_of_interval h0 (by linarith : a < 1)
  have h4 : 1 / (1 - a) ≤ 106 / 105 := by
    rw [div_le_iff₀ (by linarith : (0 : ℝ) < 1 - a)]
    linarith
  linarith

/-- `√x · u ≤ b` if `x u² ≤ b²`. -/
private theorem sqrt_mul_le {x u b : ℝ} (hx : 0 ≤ x) (hb : 0 ≤ b) (h : x * u ^ 2 ≤ b ^ 2) :
    Real.sqrt x * u ≤ b := by
  have e : (Real.sqrt x * u) ^ 2 = x * u ^ 2 := by rw [mul_pow, Real.sq_sqrt hx]
  exact le_of_sq_le_sq (by rw [e]; exact h) hb

/-- `b ≤ √x · u` if `b² ≤ x u²`. -/
private theorem le_sqrt_mul {x u b : ℝ} (hx : 0 ≤ x) (hu : 0 ≤ u) (h : b ^ 2 ≤ x * u ^ 2) :
    b ≤ Real.sqrt x * u := by
  have e : (Real.sqrt x * u) ^ 2 = x * u ^ 2 := by rw [mul_pow, Real.sq_sqrt hx]
  exact le_of_sq_le_sq (by rw [e]; exact h) (mul_nonneg (Real.sqrt_nonneg x) hu)

/-- For `k ≥ 265` and `25 (R-1)³ ≤ 121 k² < 25 R³`, the pair `(k, R)` satisfies the hypotheses of
`cross_of_bounds`. -/
private theorem cross_strip_hyp {k R : ℕ} (hk : 265 ≤ k) (hR : 25 * (R - 1) ^ 3 ≤ 121 * k ^ 2)
    (hR' : 121 * k ^ 2 < 25 * R ^ 3) :
    2 ≤ R ∧ R ≤ k - 1 ∧ abar k * R ≤ 6679 / 10000 ∧ 0 ≤ tlow k R ∧
      (tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
          * (Hbar k R + 5 / (k : ℝ) * Gbar k R)
        < Real.exp (-1) * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R) := by
  -- the real parameters
  have hk' : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK0 : (0 : ℝ) < (k : ℝ) := by linarith
  have hR1 : 1 ≤ R := Nat.pos_of_ne_zero (by rintro rfl; simp at hR')
  have hcast : ((R - 1 : ℕ) : ℝ) = (R : ℝ) - 1 := by rw [Nat.cast_sub hR1, Nat.cast_one]
  have h1 : (25 : ℝ) * ((R : ℝ) - 1) ^ 3 ≤ 121 * (k : ℝ) ^ 2 := by
    rw [← hcast]; exact_mod_cast hR
  have h2 : (121 : ℝ) * (k : ℝ) ^ 2 < 25 * (R : ℝ) ^ 3 := by exact_mod_cast hR'
  obtain ⟨u, hu, hK⟩ := exists_scale hK0
  have hu6 : (0 : ℝ) < u ^ 6 := pow_pos hu 6
  have hK2 : (121 : ℝ) * (k : ℝ) ^ 2 * u ^ 6 = 25 := by
    have h : ((k : ℝ) * u ^ 3) ^ 2 = (5 / 11) ^ 2 := by rw [hK]
    linear_combination 121 * h
  -- `1 < R u² ≤ 1 + u²`
  have hρ1 : 1 < (R : ℝ) * u ^ 2 := by
    by_contra hcon
    have hle : (R : ℝ) * u ^ 2 ≤ 1 := not_lt.mp hcon
    have h0 : 0 ≤ (R : ℝ) * u ^ 2 := mul_nonneg (Nat.cast_nonneg R) (sq_nonneg u)
    have h3 : ((R : ℝ) * u ^ 2) ^ 3 ≤ 1 := pow_le_one₀ h0 hle
    have h4 : (121 : ℝ) * (k : ℝ) ^ 2 * u ^ 6 < 25 * (R : ℝ) ^ 3 * u ^ 6 :=
      mul_lt_mul_of_pos_right h2 hu6
    linarith
  have hρ2 : (R : ℝ) * u ^ 2 ≤ 1 + u ^ 2 := by
    by_contra hcon
    have hgt : 1 < ((R : ℝ) - 1) * u ^ 2 := by linarith [not_le.mp hcon]
    have h3 : 1 < (((R : ℝ) - 1) * u ^ 2) ^ 3 := one_lt_pow₀ hgt (by norm_num)
    have h4 : (25 : ℝ) * ((R : ℝ) - 1) ^ 3 * u ^ 6 ≤ 121 * (k : ℝ) ^ 2 * u ^ 6 :=
      mul_le_mul_of_nonneg_right h1 hu6.le
    linarith
  -- `u ≤ 0.119705`
  have hU0 : u ≤ 119705 / 1000000 := by
    by_contra hcon
    have hlt : (119705 / 1000000 : ℝ) < u := not_le.mp hcon
    have h3 : (119705 / 1000000 : ℝ) ^ 3 < u ^ 3 :=
      pow_lt_pow_left₀ hlt (by norm_num) (by norm_num)
    have h4 : (265 : ℝ) * u ^ 3 ≤ (k : ℝ) * u ^ 3 :=
      mul_le_mul_of_nonneg_right hk' (pow_pos hu 3).le
    have h5 : (5 / 11 : ℝ) < 265 * (119705 / 1000000 : ℝ) ^ 3 := by norm_num
    linarith
  have hU : u ≤ 3 / 25 := hU0.trans (by norm_num)
  have hu2 : u ^ 2 ≤ 9 / 625 := (pow_le_pow_left₀ hu.le hU 2).trans (by norm_num)
  have hu3 : u ^ 3 ≤ 27 / 15625 := (pow_le_pow_left₀ hu.le hU 3).trans (by norm_num)
  -- `2 ≤ R ≤ k - 1`
  have hR2 : 2 ≤ R := by
    by_contra hcon
    have hle : (R : ℝ) ≤ 1 := by exact_mod_cast (by omega : R ≤ 1)
    have h := mul_le_mul_of_nonneg_right hle (sq_nonneg u)
    linarith
  have hRk : R ≤ k - 1 := by
    have e1 := mul_nonneg hu.le (sub_nonneg.2 hρ2)
    have h : ((R : ℝ) + 1) * u ^ 3 < (k : ℝ) * u ^ 3 := by linarith
    have h' : (R : ℝ) + 1 < (k : ℝ) := lt_of_mul_lt_mul_right h (pow_pos hu 3).le
    have h'' : R + 1 < k := by exact_mod_cast h'
    omega
  have hρ0 : (0 : ℝ) < (R : ℝ) := by exact_mod_cast (by omega : 0 < R)
  have hρ2' : (2 : ℝ) ≤ (R : ℝ) := by exact_mod_cast hR2
  -- `ā` and `a̲`
  have ea : 5 / (2 * (k : ℝ)) = 11 / 2 * u ^ 3 := by
    rw [div_eq_iff (mul_pos (by norm_num : (0 : ℝ) < 2) hK0).ne']
    linear_combination (-11 : ℝ) * hK
  have ha : abar k = 11 / 2 * u ^ 3 := by unfold abar; exact ea
  have hal : alow k = 11 / 2 * u ^ 3 - 484 / 75 * u ^ 6 := by
    have e2 : 4 / (3 * (k : ℝ) ^ 2) = 484 / 75 * u ^ 6 := by
      rw [div_eq_iff (mul_pos (by norm_num : (0 : ℝ) < 3) (pow_pos hK0 2)).ne']
      linear_combination (-(484 / 25 : ℝ)) * ((k : ℝ) * u ^ 3 + 5 / 11) * hK
    unfold alow
    rw [ea, e2]
  -- `ā R ≤ 0.6679`
  have hs1 : abar k * (R : ℝ) ≤ 6679 / 10000 := by
    rw [ha]
    have t1 := mul_nonneg hu.le (sub_nonneg.2 hρ2)
    have t3 : u ^ 3 ≤ (119705 / 1000000 : ℝ) ^ 3 := pow_le_pow_left₀ hu.le hU0 3
    linarith
  -- `e^{ā}`
  have ha0 : 0 ≤ abar k := by rw [ha]; exact mul_nonneg (by norm_num) (pow_pos hu 3).le
  have ha1 : abar k ≤ 1 / 106 := by
    unfold abar
    rw [div_le_iff₀ (mul_pos (by norm_num : (0 : ℝ) < 2) hK0)]
    linarith
  have hE := exp_le_of_le ha0 ha1
  have hE0 : 0 ≤ Real.exp (abar k) := (Real.exp_pos _).le
  -- `c₀`
  have hc : 19947 / 50000 ≤ c0 ∧ c0 ≤ 7979 / 20000 := c0_bounds
  -- square roots
  have hsm0 : 0 < Real.sqrt ((R : ℝ) - 1) := Real.sqrt_pos.mpr (by linarith)
  have hsm : Real.sqrt ((R : ℝ) - 1) * u ≤ 1 :=
    sqrt_mul_le (by linarith) zero_le_one (by linarith)
  have hσm : 1 - 101 / 200 * u ^ 2 ≤ Real.sqrt ((R : ℝ) - 1) * u := by
    refine le_sqrt_mul (by linarith) hu.le ?_
    have t := mul_nonneg (sq_nonneg u) (sub_nonneg.2 hu2)
    have t' := sq_nonneg u
    linarith
  have hsm' : 1 ≤ Real.sqrt ((R : ℝ) - 1) * u * (1 + 51 / 100 * u ^ 2) := by
    have h := mul_le_mul_of_nonneg_right hσm (by positivity : (0 : ℝ) ≤ 1 + 51 / 100 * u ^ 2)
    have t := mul_nonneg (sq_nonneg u) (sub_nonneg.2 hu2)
    have t' := sq_nonneg u
    linarith
  have hs00 : 0 ≤ Real.sqrt (R : ℝ) := Real.sqrt_nonneg _
  have hs0' : 1 ≤ Real.sqrt (R : ℝ) * u := le_sqrt_mul hρ0.le hu.le (by linarith)
  have hs0'' : Real.sqrt (R : ℝ) * u ≤ 1 + u ^ 2 / 2 := by
    refine sqrt_mul_le hρ0.le (by positivity) ?_
    have t := sq_nonneg (u ^ 2)
    linarith
  have hsp0 : 0 < Real.sqrt ((R : ℝ) + 1) := Real.sqrt_pos.mpr (by linarith)
  have hsp : Real.sqrt ((R : ℝ) + 1) * u ≤ 1 + u ^ 2 := by
    refine sqrt_mul_le (by linarith) (by positivity) ?_
    have t := sq_nonneg (u ^ 2)
    linarith
  have hrs : (R : ℝ) * u ^ 2 * (Real.sqrt (R : ℝ) * u) ≤ (1 + u ^ 2) * (1 + u ^ 2 / 2) :=
    mul_le_mul hρ2 hs0'' (mul_nonneg hs00 hu.le) (by positivity)
  -- `t̲ ≥ 0`
  have htl : 0 ≤ tlow k R := by
    have h := cstrip_tlow_core hu hU hc.1 hρ0 hρ1 ha hsm hrs hsp0 hsp hE
    have e : tlow k R = Real.exp (-1)
        * (2 * c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((R : ℝ) + 1)
          - abar k * (Real.exp (abar k) + 1 + c0 * (2 * Real.sqrt ((R : ℝ) - 1) - 1))
          - 633 / 1000 * abar k ^ 2
              * (1 + c0 * (2 / 3 * ((R : ℝ) * Real.sqrt (R : ℝ))
                  + 2 * Real.sqrt ((R : ℝ) - 1) - 1))) := by
      unfold tlow; ring
    rw [e]
    exact mul_nonneg (Real.exp_pos _).le h
  -- the main inequality
  have hmain := cstrip_main hu hU hc.1 hc.2 hK (by linarith : (1 : ℝ) ≤ (k : ℝ)) hρ1 hρ2 ha hal
    hsm0 hsm hsm' hs00 hs0' hs0'' hE0 hE
  refine ⟨hR2, hRk, hs1, htl, ?_⟩
  have hA : tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R)
      = Real.exp (-1) * (2 * c0 / Real.sqrt ((R : ℝ) - 1)
          - alow k * (2 + c0 * (2 * Real.sqrt (R : ℝ) - 2 - 1 / 4))
          + Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R)) := by
    unfold tup; ring
  rw [hA, mul_assoc]
  exact mul_lt_mul_of_pos_left hmain (Real.exp_pos _)

/-- For `k ≥ 265`, `25 s³ ≤ 121 k²` implies `100 (s + 1) ≤ 27 k`: otherwise
`266 k ≤ 1000 s`, and then `25 · 266³ k³ ≤ 121 · 10⁹ k²` contradicts `k ≥ 265`. -/
theorem strip_end_le {k s : ℕ} (hk : 265 ≤ k) (hs : 25 * s ^ 3 ≤ 121 * k ^ 2) :
    100 * (s + 1) ≤ 27 * k := by
  by_contra hcon
  have h1 : 27 * k < 100 * (s + 1) := not_le.mp hcon
  have h2 : 266 * k ≤ 1000 * s := by omega
  have h3 : (266 * k) ^ 3 ≤ (1000 * s) ^ 3 := Nat.pow_le_pow_left h2 3
  have h4 : 25 * (1000 * s) ^ 3 ≤ 121000000000 * k ^ 2 := by
    calc 25 * (1000 * s) ^ 3 = 1000000000 * (25 * s ^ 3) := by ring
      _ ≤ 1000000000 * (121 * k ^ 2) := Nat.mul_le_mul_left _ hs
      _ = 121000000000 * k ^ 2 := by ring
  have h6 : 470527400 * k ^ 3 ≤ 121000000000 * k ^ 2 := by
    calc 470527400 * k ^ 3 = 25 * (266 * k) ^ 3 := by ring
      _ ≤ 25 * (1000 * s) ^ 3 := Nat.mul_le_mul_left _ h3
      _ ≤ 121000000000 * k ^ 2 := h4
  have h7 : 124689761000 * k ^ 2 ≤ 470527400 * k ^ 3 := by
    calc 124689761000 * k ^ 2 = 470527400 * (265 * k ^ 2) := by ring
      _ ≤ 470527400 * (k * k ^ 2) := Nat.mul_le_mul_left _ (Nat.mul_le_mul_right _ hk)
      _ = 470527400 * k ^ 3 := by ring
  have hk2 : 0 < k ^ 2 := by positivity
  have h8 : 124689761000 * k ^ 2 ≤ 121000000000 * k ^ 2 := le_trans h7 h6
  have h9 : 124689761000 ≤ 121000000000 := Nat.le_of_mul_le_mul_right h8 hk2
  omega

/-- Column `k ≥ 265` turns positive at a row `j` with `j - k - 1 ≤ ϱ(k)`. -/
theorem crossing_strip {k : ℕ} (hk : 265 ≤ k) :
    ∃ j, k < j ∧ 25 * (j - k - 1) ^ 3 ≤ 121 * k ^ 2 ∧ 0 < dq k j := by
  have hk0 : 0 < k := by omega
  -- `R` is the least natural number with `121 k² < 25 R³`
  have hex : ∃ R : ℕ, 121 * k ^ 2 < 25 * R ^ 3 := by
    refine ⟨k, ?_⟩
    have h1 : 121 * k ^ 2 < 25 * k * k ^ 2 :=
      mul_lt_mul_of_pos_right (by omega) (pow_pos hk0 2)
    calc 121 * k ^ 2 < 25 * k * k ^ 2 := h1
      _ = 25 * k ^ 3 := by ring
  obtain ⟨R, hR', hmin⟩ :
      ∃ R : ℕ, 121 * k ^ 2 < 25 * R ^ 3 ∧ ∀ m < R, ¬ (121 * k ^ 2 < 25 * m ^ 3) :=
    ⟨Nat.find hex, Nat.find_spec hex, fun m hm => Nat.find_min hex hm⟩
  have hR1 : 1 ≤ R := Nat.pos_of_ne_zero (by rintro rfl; simp at hR')
  have hR : 25 * (R - 1) ^ 3 ≤ 121 * k ^ 2 := not_lt.mp (hmin (R - 1) (by omega))
  obtain ⟨h2R, hRk, hs, ht, hmain⟩ := cross_strip_hyp hk hR hR'
  obtain ⟨j, hkj, hjR, hpos⟩ := cross_of_bounds (by omega) h2R hRk hs ht hmain
  refine ⟨j, hkj, ?_, hpos⟩
  have hle : j - k - 1 ≤ R - 1 := by omega
  calc 25 * (j - k - 1) ^ 3 ≤ 25 * (R - 1) ^ 3 :=
        Nat.mul_le_mul_left 25 (Nat.pow_le_pow_left hle 3)
    _ ≤ 121 * k ^ 2 := hR

end Parking
