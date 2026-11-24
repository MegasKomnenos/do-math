import Parking.Crossing.Bounds
import Parking.Crossing.StripNumerics

/-!
# The crossing happens inside the strip

For `k ≥ 265` let `R` be the least positive integer with `121 k² < 25 R³`, that is,
`25 (R-1)³ ≤ 121 k² < 25 R³`, or `R = ϱ(k) + 1` with `ϱ(k) = ⌊(11k/5)^{2/3}⌋`.  With the closed
forms of `Parking.Crossing.Bounds` at `(k, R)` and `N = k + R`, put

`𝖠 = e t̄ + e^{ā} (R+1)/N`, `𝖡 = H̄ + (5/k) Ḡ`, `𝖢 = R(R+1)/N - 1 - S̄ - Ē`.

* `strip_tlow_nonneg` : `t̲ ≥ 0`;
* `strip_main` : `𝖠 𝖡 < 𝖢`;
* `crossing_strip` : column `k` turns positive at some row `j ≤ k + ϱ(k) + 1`;
* `strip_end_le` : for `k ≥ 265`, `25 s³ ≤ 121 k²` implies `100 (s + 1) ≤ 27 k`.

## Organisation

The scale parameter is `u = (5/(11k))^{1/3}` (`k u³ = 5/11`), so that the hypothesis on `R` reads
`1 < R u² ≤ 1 + u²`, and `k ≥ 265` gives `u ≤ 0.119705 ≤ 3/25`.  In terms of `u`
(`strip_relations`): `2 ≤ R`, `ā = (11/2) u³`, `a̲ = (11/2) u³ - (484/75) u⁶`, `e^{ā} ≤ 106/105`,
`√(R-1) u ≤ 1 ≤ √(R-1) u (1 + (51/100) u²)`, `1 ≤ √R u ≤ 1 + u²/2`, `√(R+1) u ≤ 1 + u²`.  With
these and `0.39894 ≤ c₀ ≤ 0.39895`, `cstrip_tlow_core` gives `strip_tlow_nonneg` and `cstrip_main`
gives `strip_main` (both in `Parking.Crossing.StripNumerics`, which works with real variables
only).

`crossing_strip` applies `cross_of_bounds` to `(k, R)`.  Of its hypotheses, `2 ≤ R ≤ k - 1` and
`ā R ≤ 0.6679` follow from the same relations, `t̲ ≥ 0` is `strip_tlow_nonneg`, and the main
inequality is `𝖠 𝖡 < 𝖢` multiplied by `e⁻¹`.
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

/-- The relations between `k ≥ 265`, `R` with `25 (R-1)³ ≤ 121 k² < 25 R³`, and the scale `u > 0`
with `k u³ = 5/11`: `u ≤ 0.119705`, `2 ≤ R`, `1 < R u² ≤ 1 + u²`, `ā = (11/2) u³`,
`a̲ = (11/2) u³ - (484/75) u⁶`, `e^{ā} ≤ 106/105`, `√(R-1) u ≤ 1 ≤ √(R-1) u (1 + (51/100) u²)`,
`1 ≤ √R u ≤ 1 + u²/2` and `√(R+1) u ≤ 1 + u²`. -/
private theorem strip_relations {k R : ℕ} (hk : 265 ≤ k) (hR : 25 * (R - 1) ^ 3 ≤ 121 * k ^ 2)
    (hR' : 121 * k ^ 2 < 25 * R ^ 3) :
    ∃ u : ℝ, 0 < u ∧ u ≤ 119705 / 1000000 ∧ (k : ℝ) * u ^ 3 = 5 / 11 ∧ 2 ≤ R ∧
      1 < (R : ℝ) * u ^ 2 ∧ (R : ℝ) * u ^ 2 ≤ 1 + u ^ 2 ∧
      abar k = 11 / 2 * u ^ 3 ∧ alow k = 11 / 2 * u ^ 3 - 484 / 75 * u ^ 6 ∧
      Real.exp (abar k) ≤ 106 / 105 ∧
      Real.sqrt ((R : ℝ) - 1) * u ≤ 1 ∧
      1 ≤ Real.sqrt ((R : ℝ) - 1) * u * (1 + 51 / 100 * u ^ 2) ∧
      1 ≤ Real.sqrt (R : ℝ) * u ∧ Real.sqrt (R : ℝ) * u ≤ 1 + u ^ 2 / 2 ∧
      Real.sqrt ((R : ℝ) + 1) * u ≤ 1 + u ^ 2 := by
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
  -- `2 ≤ R`
  have hR2 : 2 ≤ R := by
    by_contra hcon
    have hle : (R : ℝ) ≤ 1 := by exact_mod_cast (by omega : R ≤ 1)
    have h := mul_le_mul_of_nonneg_right hle (sq_nonneg u)
    linarith
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
  -- `e^{ā}`
  have ha0 : 0 ≤ abar k := by rw [ha]; exact mul_nonneg (by norm_num) (pow_pos hu 3).le
  have ha1 : abar k ≤ 1 / 106 := by
    unfold abar
    rw [div_le_iff₀ (mul_pos (by norm_num : (0 : ℝ) < 2) hK0)]
    linarith
  have hE := exp_le_of_le ha0 ha1
  -- square roots
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
  have hs0' : 1 ≤ Real.sqrt (R : ℝ) * u := le_sqrt_mul hρ0.le hu.le (by linarith)
  have hs0'' : Real.sqrt (R : ℝ) * u ≤ 1 + u ^ 2 / 2 := by
    refine sqrt_mul_le hρ0.le (by positivity) ?_
    have t := sq_nonneg (u ^ 2)
    linarith
  have hsp : Real.sqrt ((R : ℝ) + 1) * u ≤ 1 + u ^ 2 := by
    refine sqrt_mul_le (by linarith) (by positivity) ?_
    have t := sq_nonneg (u ^ 2)
    linarith
  exact ⟨u, hu, hU0, hK, hR2, hρ1, hρ2, ha, hal, hE, hsm, hsm', hs0', hs0'', hsp⟩

/-- **`t̲ ≥ 0` in the strip.**  Let `k ≥ 265` and let `R` be the least positive integer with
`121 k² < 25 R³`, i.e. `25 (R-1)³ ≤ 121 k² < 25 R³`.  Then the lower bound `t̲` (`tlow`) for the
kernel deficit of column `k` is nonnegative.  By `strip_relations` the numbers `u`, `c₀`, `R`,
`√(R-1)`, `√R`, `√(R+1)`, `ā`, `e^{ā}` satisfy the hypotheses of `cstrip_tlow_core`, whose
conclusion is `e t̲ ≥ 0`. -/
theorem strip_tlow_nonneg {k R : ℕ} (hk : 265 ≤ k) (hR : 25 * (R - 1) ^ 3 ≤ 121 * k ^ 2)
    (hR' : 121 * k ^ 2 < 25 * R ^ 3) : 0 ≤ tlow k R := by
  obtain ⟨u, hu, hU0, -, hR2, hρ1, hρ2, ha, -, hE, hsm, -, -, hs0'', hsp⟩ :=
    strip_relations hk hR hR'
  have hρ0 : (0 : ℝ) < (R : ℝ) := by exact_mod_cast (by omega : 0 < R)
  have hsp0 : 0 < Real.sqrt ((R : ℝ) + 1) := Real.sqrt_pos.mpr (by linarith)
  have hrs : (R : ℝ) * u ^ 2 * (Real.sqrt (R : ℝ) * u) ≤ (1 + u ^ 2) * (1 + u ^ 2 / 2) :=
    mul_le_mul hρ2 hs0'' (mul_nonneg (Real.sqrt_nonneg _) hu.le) (by positivity)
  have h := cstrip_tlow_core hu (hU0.trans (by norm_num)) c0_bounds.1 hρ0 hρ1 ha hsm hrs hsp0 hsp
    hE
  have e : tlow k R = Real.exp (-1)
      * (2 * c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((R : ℝ) + 1)
        - abar k * (Real.exp (abar k) + 1 + c0 * (2 * Real.sqrt ((R : ℝ) - 1) - 1))
        - 633 / 1000 * abar k ^ 2
            * (1 + c0 * (2 / 3 * ((R : ℝ) * Real.sqrt (R : ℝ))
                + 2 * Real.sqrt ((R : ℝ) - 1) - 1))) := by
    unfold tlow; ring
  rw [e]
  exact mul_nonneg (Real.exp_pos _).le h

/-- **`𝖠 𝖡 < 𝖢` in the strip.**  Let `k ≥ 265` and let `R` be the least positive integer with
`121 k² < 25 R³`, i.e. `25 (R-1)³ ≤ 121 k² < 25 R³`.  Then, with `N = k + R`,
`(e t̄ + e^{ā} (R+1)/N) (H̄ + (5/k) Ḡ) < R(R+1)/N - 1 - S̄ - Ē`.  Multiplied by `e⁻¹` this is the
main hypothesis of `cross_of_bounds`.  By `strip_relations` the numbers `u`, `c₀`, `k`, `R`,
`√(R-1)`, `√R`, `ā`, `a̲`, `e^{ā}` satisfy the hypotheses of `cstrip_main`, whose conclusion is the
assertion with `e t̄` written out. -/
theorem strip_main {k R : ℕ} (hk : 265 ≤ k) (hR : 25 * (R - 1) ^ 3 ≤ 121 * k ^ 2)
    (hR' : 121 * k ^ 2 < 25 * R ^ 3) :
    (Real.exp 1 * tup k R + Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
        * (Hbar k R + 5 / (k : ℝ) * Gbar k R)
      < (R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R := by
  obtain ⟨u, hu, hU0, hK, hR2, hρ1, hρ2, ha, hal, hE, hsm, hsm', hs0', hs0'', -⟩ :=
    strip_relations hk hR hR'
  have hK1 : (1 : ℝ) ≤ (k : ℝ) := by exact_mod_cast (by omega : 1 ≤ k)
  have hρ2' : (2 : ℝ) ≤ (R : ℝ) := by exact_mod_cast hR2
  have hsm0 : 0 < Real.sqrt ((R : ℝ) - 1) := Real.sqrt_pos.mpr (by linarith)
  have hmain := cstrip_main hu (hU0.trans (by norm_num)) c0_bounds.1 c0_bounds.2 hK hK1 hρ1 hρ2
    ha hal hsm0 hsm hsm' (Real.sqrt_nonneg _) hs0' hs0'' (Real.exp_pos _).le hE
  have he : Real.exp 1 * Real.exp (-1) = 1 := by rw [← Real.exp_add]; simp
  have hA : Real.exp 1 * tup k R + Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R)
      = 2 * c0 / Real.sqrt ((R : ℝ) - 1)
          - alow k * (2 + c0 * (2 * Real.sqrt (R : ℝ) - 2 - 1 / 4))
          + Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R) := by
    unfold tup
    linear_combination (2 * c0 / Real.sqrt ((R : ℝ) - 1)
      - alow k * (2 + c0 * (2 * Real.sqrt (R : ℝ) - 2 - 1 / 4))) * he
  rw [hA]
  exact hmain

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

/-- Column `k ≥ 265` turns positive at a row `j` with `j - k - 1 ≤ ϱ(k)`: for the least `R` with
`121 k² < 25 R³`, the pair `(k, R)` satisfies the hypotheses of `cross_of_bounds`. -/
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
  -- `2 ≤ R ≤ k - 1` and `ā R ≤ 0.6679`
  obtain ⟨u, hu, hU0, hK, hR2, -, hρ2, ha, -⟩ := strip_relations hk hR hR'
  have hU : u ≤ 3 / 25 := hU0.trans (by norm_num)
  have e1 := mul_nonneg hu.le (sub_nonneg.2 hρ2)
  have hRk : R ≤ k - 1 := by
    have hu3 : u ^ 3 ≤ 27 / 15625 := (pow_le_pow_left₀ hu.le hU 3).trans (by norm_num)
    have h : ((R : ℝ) + 1) * u ^ 3 < (k : ℝ) * u ^ 3 := by linarith
    have h' : (R : ℝ) + 1 < (k : ℝ) := lt_of_mul_lt_mul_right h (pow_pos hu 3).le
    have h'' : R + 1 < k := by exact_mod_cast h'
    omega
  have hs : abar k * (R : ℝ) ≤ 6679 / 10000 := by
    rw [ha]
    have t3 : u ^ 3 ≤ (119705 / 1000000 : ℝ) ^ 3 := pow_le_pow_left₀ hu.le hU0 3
    linarith
  -- `𝖠 𝖡 < 𝖢` multiplied by `e⁻¹`
  have he : Real.exp (-1) * Real.exp 1 = 1 := by rw [← Real.exp_add]; simp
  have hmain : (tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
        * (Hbar k R + 5 / (k : ℝ) * Gbar k R)
      < Real.exp (-1) * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R) := by
    have h := mul_lt_mul_of_pos_left (strip_main hk hR hR') (Real.exp_pos (-1))
    have e : (tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
          * (Hbar k R + 5 / (k : ℝ) * Gbar k R)
        = Real.exp (-1) * ((Real.exp 1 * tup k R
            + Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
          * (Hbar k R + 5 / (k : ℝ) * Gbar k R)) := by
      linear_combination (-(tup k R * (Hbar k R + 5 / (k : ℝ) * Gbar k R))) * he
    rw [e]
    exact h
  obtain ⟨j, hkj, hjR, hpos⟩ :=
    cross_of_bounds (by omega) hR2 hRk hs (strip_tlow_nonneg hk hR hR') hmain
  refine ⟨j, hkj, ?_, hpos⟩
  have hle : j - k - 1 ≤ R - 1 := by omega
  calc 25 * (j - k - 1) ^ 3 ≤ 25 * (R - 1) ^ 3 :=
        Nat.mul_le_mul_left 25 (Nat.pow_le_pow_left hle 3)
    _ ≤ 121 * k ^ 2 := hR

end Parking
