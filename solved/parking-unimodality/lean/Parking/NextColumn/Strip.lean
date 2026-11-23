import Parking.NextColumn.BirthdayIneq
import Parking.NextColumn.Ramanujan
import Mathlib.Analysis.Complex.ExponentialBounds

/-!
# The criterion function is positive in the strip

For `k ≥ 265` and `2 ≤ r ≤ ϱ(k) = ⌊(11k/5)^{2/3}⌋` (i.e. `25 r³ ≤ 121 k²`, i.e. `11 k ≥ 5 r^{3/2}`)
the criterion function is positive, `𝖦(r,k) > 0` (`Gfun_pos`), and such a position is a
first-layer position, `r ≤ k - 1` (`strip_end_le`).  Recall

  `𝖦(r,k) = k φ(r) - 5/2 + (1/2) μ₀(X₋) + 2 (1 - 1/k) μ₀(X_mid) - (k/(k-1)) D_r`,

where `φ(r) = 1/(2r) - 1/(3r²)`, `X₋ = r(r+1)/(k-1)`, `X_mid = r(r+2)/(2k)`.

## Preparations

* (P1) `le_mul_phi` : `φ(R) = (3R - 2)/(6R²)`, so that `c ≤ K φ(R)` is the polynomial inequality
  `6 c R² ≤ K (3R - 2)` (this is how the monotonicity of `φ` is used).
* (P2) `mu0_ge` : if `(3/2) m² + (4 + X) m ≤ 2 (r - 1)` then `μ₀(X) ≥ m`
  (and `μ₀ ≥ 0` is `mu0_nonneg` in `Parking.NextColumn.BirthdayIneq`).
* (P3) `Dbirth_nonneg`, `Dbirth_mono`, `Dbirth_le` in `Parking.NextColumn.Birthday` : `D_r ≥ 0` is
  nondecreasing in `r` and `D_r ≤ (3/2)(s_r - 1)`.
* (P4) `sbirth_upper`, `Dbirth_le_lin` : with `x = √r`, `r ≥ 14`: `s_r ≤ 1.261 x - 1/3` (from
  `sbirth_le`, `π < 3.1416` and `e^t ≤ 1/(1-t)`), hence `D_r ≤ 1.8915 x - 2.6`.
* `Gfun_ge` : as `k ≥ 265`, `2 (1 - 1/k) ≥ 528/265` and `k/(k-1) ≤ 265/264`; since `μ₀ ≥ 0` and
  `D_r ≥ 0`, lower bounds `t, m₁, m₂` of `k φ(r)`, `μ₀(X₋)`, `μ₀(X_mid)` and an upper bound `d` of
  `D_r` give `𝖦(r,k) ≥ t - 5/2 + m₁/2 + (528/265) m₂ - (265/264) d`.

## The two frames

* Frame α (`2 ≤ r ≤ 13`, `Gfun_pos_alpha`): the two `μ₀` terms are dropped, `k φ(r) ≥ 265 φ(13)`
  and `D_r ≤ D_13 ≤ (3/2)(s_13 - 1)`, so `𝖦(r,k) ≥ 3635/507 - (265/176)(s_13 - 1)`; this is
  `> 2.32` because `s_13 ≤ 4.216`.
* Frame β (`r ≥ 14`, `Gfun_pos_beta`), with `x = √r ≥ 3.74`:
  - (β1) `beta_first_term` : `k φ(r) ≥ 1.88`;
  - (β2) `beta_X_le` : `X_mid ≤ 1.1315 x` and `X₋ ≤ 2.24 x`;
  - (β3) `mu0_lin` : `μ₀(X_mid) ≥ 0.837 x - 0.92` and `μ₀(X₋) ≥ 0.628 x - 0.62`;
  - (β4) `Dbirth_le_lin` : `D_r ≤ 1.8915 x - 2.6`;
  - (β5) `Gfun_ge` : `𝖦(r,k) ≥ 0.083 x - 0.1533 ≥ 0.083 · 3.74 - 0.1533 > 0`.

  The distinction `r ≤ 69` (use `k ≥ 265`) / `r ≥ 70` (use `11 k ≥ 5 x³`) occurs only inside (β1)
  and (β2).

All numerical side conditions are closed rational inequalities (`norm_num`), or inequalities
between polynomials with rational coefficients which are linear combinations of the listed
products of nonnegative factors (`linarith`).
-/

namespace Parking

open Finset

/-! ### Preparations -/

/-- (P1) `φ(R) = 1/(2R) - 1/(3R²) = (3R - 2)/(6R²)` for `R > 0`; hence `c ≤ K φ(R)` follows from
the polynomial inequality `6 c R² ≤ K (3R - 2)`. -/
private theorem le_mul_phi {K R c : ℝ} (hR : 0 < R) (h : 6 * c * R ^ 2 ≤ K * (3 * R - 2)) :
    c ≤ K * (1 / (2 * R) - 1 / (3 * R ^ 2)) := by
  have e0 : 1 / (2 * R) - 1 / (3 * R ^ 2)
      = (1 * (3 * R ^ 2) - 2 * R * 1) / (2 * R * (3 * R ^ 2)) :=
    div_sub_div _ _ (by positivity) (by positivity)
  have hden : (0 : ℝ) < 2 * R * (3 * R ^ 2) := by positivity
  have h' := mul_le_mul_of_nonneg_right h hR.le
  rw [e0, ← mul_div_assoc, le_div_iff₀ hden]
  linarith

/-- (P2) If `(3/2) m² + (4 + X) m ≤ 2 (r - 1)` then `m ≤ μ₀(X)`.  Indeed `μ = μ₀(X)` satisfies
`3μ + (4 + X) = √((4+X)² + 12(r-1))`, and the hypothesis says `(3m + 4 + X)² ≤ (4+X)² + 12(r-1)`.
No sign condition on `X` or `m` is needed. -/
private theorem mu0_ge {r : ℕ} {X m : ℝ}
    (h : 3 / 2 * m ^ 2 + (4 + X) * m ≤ 2 * ((r : ℝ) - 1)) : m ≤ mu0 r X := by
  have h1 : 3 * m + (4 + X) ≤ Real.sqrt ((4 + X) ^ 2 + 12 * ((r : ℝ) - 1)) :=
    Real.le_sqrt_of_sq_le (by linarith)
  unfold mu0
  linarith

/-- (β3), general form.  Let `x² = r`, `0 ≤ X ≤ c x` and `m = a x - b`.  If
`(3/2) m² + (4 + c x) m ≤ 2 (x² - 1)` — the difference of the two sides is the quadratic
`P_{c,a,b}(x) = (2 - (3/2)a² - ca) x² + (3ab - 4a + cb) x + (4b - 2 - (3/2)b²)` — then
`μ₀(X) ≥ a x - b`: if `m ≤ 0` because `μ₀ ≥ 0`, and if `m > 0` by (P2), since then
`(3/2) m² + (4 + X) m ≤ (3/2) m² + (4 + c x) m`. -/
private theorem mu0_lin {r : ℕ} (hr : 1 ≤ r) {x X c a b : ℝ} (hxx : x ^ 2 = (r : ℝ))
    (hX0 : 0 ≤ X) (hXc : X ≤ c * x)
    (hP : 3 / 2 * (a * x - b) ^ 2 + (4 + c * x) * (a * x - b) ≤ 2 * (x ^ 2 - 1)) :
    a * x - b ≤ mu0 r X := by
  rcases le_or_gt (a * x - b) 0 with hm | hm
  · exact le_trans hm (mu0_nonneg hr hX0)
  · have h1 : X * (a * x - b) ≤ c * x * (a * x - b) := mul_le_mul_of_nonneg_right hXc hm.le
    exact mu0_ge (by rw [← hxx]; linarith)

/-- `√(π R / 2) ≤ (31333/25000) √R` (from `π < 3.1416`). -/
private theorem sqrt_pi_half_le {R : ℝ} (hR : 0 ≤ R) :
    Real.sqrt (Real.pi * R / 2) ≤ 31333 / 25000 * Real.sqrt R := by
  have hpi : Real.pi < 3927 / 1250 := lt_of_lt_of_le Real.pi_lt_d4 (by norm_num)
  have h1 : Real.pi * R ≤ 3927 / 1250 * R := mul_le_mul_of_nonneg_right hpi.le hR
  have h2 : (31333 / 25000 * Real.sqrt R) ^ 2 = (31333 / 25000) ^ 2 * R := by
    rw [mul_pow, Real.sq_sqrt hR]
  have h3 : (3927 / 2500 : ℝ) ≤ (31333 / 25000) ^ 2 := by norm_num
  have h4 : 3927 / 2500 * R ≤ (31333 / 25000) ^ 2 * R := mul_le_mul_of_nonneg_right h3 hR
  have h5 : (0 : ℝ) ≤ 31333 / 25000 * Real.sqrt R :=
    mul_nonneg (by norm_num) (Real.sqrt_nonneg R)
  rw [Real.sqrt_le_left h5, h2]
  calc Real.pi * R / 2 ≤ 3927 / 2500 * R := by linarith
    _ ≤ (31333 / 25000) ^ 2 * R := h4

/-- (P4), first half: `s_r ≤ σ √r - 1/3` for `r ≥ r₀`, as soon as
`σ ≥ (31333/25000) / (1 - 1/(12 r₀))` (`sbirth_le` together with `π < 3.1416` and
`e^t ≤ 1/(1-t)`).  Used with `(r₀, σ) = (14, 1.261)` in frame β and `(13, 1.2615)` in frame α. -/
private theorem sbirth_upper {r r0 : ℕ} (h0 : 1 ≤ r0) (h : r0 ≤ r) {σ : ℝ}
    (hσ : 31333 / 25000 * (1 / (1 - 1 / (12 * (r0 : ℝ)))) ≤ σ) :
    sbirth r ≤ σ * Real.sqrt r - 1 / 3 := by
  have hr1 : 1 ≤ r := le_trans h0 h
  have hR0 : (1 : ℝ) ≤ (r0 : ℝ) := by exact_mod_cast h0
  have hRR : (r0 : ℝ) ≤ (r : ℝ) := by exact_mod_cast h
  have hR : (0 : ℝ) ≤ (r : ℝ) := Nat.cast_nonneg r
  have hx : 0 ≤ Real.sqrt r := Real.sqrt_nonneg _
  have h12R0 : (0 : ℝ) < 12 * (r0 : ℝ) := by linarith
  have h3 : 1 / (12 * (r : ℝ)) ≤ 1 / (12 * (r0 : ℝ)) :=
    one_div_le_one_div_of_le h12R0 (by linarith)
  have h4 : (0 : ℝ) ≤ 1 / (12 * (r0 : ℝ)) := le_of_lt (one_div_pos.mpr h12R0)
  have h5 : 1 / (12 * (r0 : ℝ)) < 1 := by
    rw [div_lt_one h12R0]; linarith
  have h6 : Real.exp (1 / (12 * (r : ℝ))) ≤ 1 / (1 - 1 / (12 * (r0 : ℝ))) :=
    le_trans (Real.exp_le_exp.mpr h3) (Real.exp_bound_div_one_sub_of_interval h4 h5)
  have h7 : 0 ≤ Real.exp (1 / (12 * (r : ℝ))) := (Real.exp_pos _).le
  have h9 : Real.sqrt (Real.pi * r / 2) * Real.exp (1 / (12 * (r : ℝ)))
      ≤ (31333 / 25000 * Real.sqrt r) * (1 / (1 - 1 / (12 * (r0 : ℝ)))) :=
    mul_le_mul (sqrt_pi_half_le hR) h6 h7 (mul_nonneg (by norm_num) hx)
  have h11 : 31333 / 25000 * (1 / (1 - 1 / (12 * (r0 : ℝ)))) * Real.sqrt r ≤ σ * Real.sqrt r :=
    mul_le_mul_of_nonneg_right hσ hx
  calc sbirth r ≤ Real.sqrt (Real.pi * r / 2) * Real.exp (1 / (12 * (r : ℝ))) - 1 / 3 :=
        sbirth_le hr1
    _ ≤ (31333 / 25000 * Real.sqrt r) * (1 / (1 - 1 / (12 * (r0 : ℝ)))) - 1 / 3 :=
        sub_le_sub_right h9 _
    _ = 31333 / 25000 * (1 / (1 - 1 / (12 * (r0 : ℝ)))) * Real.sqrt r - 1 / 3 := by ring
    _ ≤ σ * Real.sqrt r - 1 / 3 := sub_le_sub_right h11 _

/-- (P4), second half: if `s_r ≤ σ x - 1/3` with `σ = 1.261` (`x = √r`), then
`D_r ≤ 1.8915 x - 2.6`.  For `0 < s < r` the inequality `((r+2)s - 3r)/(r - s) ≤ s - 7/5` is
equivalent to `s² + (3/5)s ≤ (8/5) r`, and with `s̄ = σ x - 1/3` one has
`s_r² + (3/5)s_r ≤ s̄² + (3/5)s̄ = σ²x² - (σ/15)x - 4/45 ≤ σ² x² ≤ (8/5) x²` (`σ² = 1.590121`;
`x > 0` because `s̄ ≥ s_r ≥ 1`).  Hence `D_r ≤ (3/2)(s_r - 7/5) ≤ (3/2)(σ x - 1/3 - 7/5)`. -/
private theorem Dbirth_le_lin {r : ℕ} (hr : 2 ≤ r) {x : ℝ} (hxx : x ^ 2 = (r : ℝ))
    (hs : sbirth r ≤ 1261 / 1000 * x - 1 / 3) : Dbirth r ≤ 3783 / 2000 * x - 13 / 5 := by
  have h1 : 1 ≤ sbirth r := one_le_sbirth (by omega)
  have h2 : sbirth r < (r : ℝ) := sbirth_lt hr
  have hpos : (0 : ℝ) < 2 * ((r : ℝ) - sbirth r) := by linarith
  have ha : 0 ≤ 1261 / 1000 * x - 1 / 3 - sbirth r := by linarith
  have hb : 0 ≤ 1261 / 1000 * x - 1 / 3 + sbirth r + 3 / 5 := by linarith
  have hab := mul_nonneg ha hb
  have h3 : sbirth r ^ 2 + 3 / 5 * sbirth r ≤ 8 / 5 * (r : ℝ) := by
    rw [← hxx]; linarith [sq_nonneg x]
  have hap := mul_nonneg ha hpos.le
  unfold Dbirth
  rw [div_le_iff₀ hpos]
  linarith

/-- (β5), first half (it is also the first step of frame α).  As `k ≥ 265`, `2 (1 - 1/k) ≥ 528/265`
and `k/(k-1) ≤ 265/264`; since `μ₀(X_mid) ≥ 0` and `D_r ≥ 0`, these one-sided bounds can be
inserted into `𝖦(r,k)` together with bounds of the four pieces. -/
private theorem Gfun_ge {r k : ℕ} (hk : 265 ≤ k) (hr : 2 ≤ r) {t m1 m2 d : ℝ}
    (hT : t ≤ (k : ℝ) * (1 / (2 * (r : ℝ)) - 1 / (3 * (r : ℝ) ^ 2)))
    (hM1 : m1 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 1) / ((k : ℝ) - 1)))
    (hM2 : m2 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 2) / (2 * (k : ℝ))))
    (hD : Dbirth r ≤ d) :
    t - 5 / 2 + 1 / 2 * m1 + 528 / 265 * m2 - 265 / 264 * d ≤ Gfun r k := by
  have hK : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have hM20 : 0 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 2) / (2 * (k : ℝ))) :=
    mu0_nonneg (by omega) (by positivity)
  have hD0 : 0 ≤ Dbirth r := Dbirth_nonneg hr
  have hA : 528 / 265 ≤ 2 * (1 - 1 / (k : ℝ)) := by
    have h : 1 / (k : ℝ) ≤ 1 / 265 := one_div_le_one_div_of_le (by norm_num) hK
    linarith
  have hB : (k : ℝ) / ((k : ℝ) - 1) ≤ 265 / 264 := by
    rw [div_le_iff₀ hK1]; linarith
  have e1 := mul_le_mul_of_nonneg_right hA hM20
  have e2 := mul_le_mul_of_nonneg_right hB hD0
  unfold Gfun
  linarith

/-! ### Frame α: `2 ≤ r ≤ 13` -/

/-- Frame α: `𝖦(r,k) ≥ 265 φ(13) - 5/2 - (265/264)(3/2)(s_13 - 1) > 2.32` for `2 ≤ r ≤ 13`. -/
private theorem Gfun_pos_alpha {r k : ℕ} (hk : 265 ≤ k) (hr : 2 ≤ r) (hr13 : r ≤ 13) :
    0 < Gfun r k := by
  have hK : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hR2 : (2 : ℝ) ≤ (r : ℝ) := by exact_mod_cast hr
  have hR13 : (r : ℝ) ≤ 13 := by exact_mod_cast hr13
  have hr1 : 1 ≤ r := by omega
  -- the first term: `k φ(r) ≥ 265 φ(13) = 265 · 37/1014`
  have hT : 265 * (37 / 1014 : ℝ) ≤ (k : ℝ) * (1 / (2 * (r : ℝ)) - 1 / (3 * (r : ℝ) ^ 2)) := by
    refine le_mul_phi (by linarith) ?_
    have e1 : 0 ≤ ((k : ℝ) - 265) * (3 * (r : ℝ) - 2) := mul_nonneg (by linarith) (by linarith)
    have e2 : 0 ≤ (13 - (r : ℝ)) * (37 * (r : ℝ) - 26) := mul_nonneg (by linarith) (by linarith)
    linarith
  -- the two `mu0` terms are nonnegative and are dropped
  have hM1 : 0 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 1) / ((k : ℝ) - 1)) :=
    mu0_nonneg hr1 (div_nonneg (by positivity) (by linarith))
  have hM2 : 0 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 2) / (2 * (k : ℝ))) :=
    mu0_nonneg hr1 (by positivity)
  -- the `Dbirth` term: `D_r ≤ D_13 ≤ (3/2)(s_13 - 1)` and `s_13 ≤ 4.216`
  have hs13 : sbirth 13 ≤ 4216 / 1000 := by
    have h1 : sbirth 13 ≤ 2523 / 2000 * Real.sqrt ((13 : ℕ) : ℝ) - 1 / 3 :=
      sbirth_upper (r0 := 13) (by norm_num) le_rfl (by norm_num)
    have h2 : Real.sqrt ((13 : ℕ) : ℝ) ≤ 3606 / 1000 := by
      rw [Real.sqrt_le_left (by norm_num)]; norm_num
    linarith
  have hD : Dbirth r ≤ 3 / 2 * (4216 / 1000 - 1) := by
    have h1 : Dbirth r ≤ Dbirth 13 := Dbirth_mono hr hr13
    have h2 : Dbirth 13 ≤ 3 / 2 * (sbirth 13 - 1) := Dbirth_le (by norm_num)
    linarith
  have hfin := Gfun_ge hk hr hT hM1 hM2 hD
  have hnum : (0 : ℝ) < 265 * (37 / 1014 : ℝ) - 5 / 2 + 1 / 2 * 0 + 528 / 265 * 0
      - 265 / 264 * (3 / 2 * (4216 / 1000 - 1)) := by norm_num
  exact lt_of_lt_of_le hnum hfin

/-! ### Frame β: `r ≥ 14`

Throughout `x = √r` (as a real `x > 0` with `x² = r`), and `25 r³ ≤ 121 k²` is used in the form
`5 x³ ≤ 11 k`. -/

/-- (β1) `k φ(r) ≥ 1.88`. -/
private theorem beta_first_term {r k : ℕ} (hk : 265 ≤ k) (hr : 14 ≤ r) {x : ℝ} (hx : 0 < x)
    (hxx : x ^ 2 = (r : ℝ)) (hcube : 5 * x ^ 3 ≤ 11 * (k : ℝ)) :
    47 / 25 ≤ (k : ℝ) * (1 / (2 * (r : ℝ)) - 1 / (3 * (r : ℝ) ^ 2)) := by
  have hK : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hR : (14 : ℝ) ≤ (r : ℝ) := by exact_mod_cast hr
  refine le_mul_phi (by linarith) ?_
  rcases Nat.lt_or_ge r 70 with h70 | h70
  · -- `14 ≤ r ≤ 69`: `k φ(r) ≥ 265 φ(r) ≥ 265 φ(69) = 1.9017…`
    have hR69 : (r : ℝ) ≤ 69 := by exact_mod_cast (by omega : r ≤ 69)
    have e1 : 0 ≤ ((k : ℝ) - 265) * (3 * (r : ℝ) - 2) := mul_nonneg (by linarith) (by linarith)
    have e2 : 0 ≤ ((r : ℝ) - 14) * (69 - (r : ℝ)) := mul_nonneg (by linarith) (by linarith)
    linarith
  · -- `r ≥ 70`: `x ≥ 8.36` and `k φ(r) ≥ (5/11) x³ φ(x²) = (5/11)(x/2 - 1/(3x)) ≥ 1.8818…`
    have hR70 : (70 : ℝ) ≤ (r : ℝ) := by exact_mod_cast h70
    have hx1 : 209 / 25 ≤ x := by
      have e : (209 / 25 : ℝ) ^ 2 ≤ 70 := by norm_num
      exact le_of_sq_le_sq (by rw [hxx]; linarith) hx.le
    have e1 : 0 ≤ (11 * (k : ℝ) - 5 * x ^ 3) * (3 * x ^ 2 - 2) :=
      mul_nonneg (by linarith) (by linarith)
    have hq : 0 ≤ 15 * x ^ 2 - 3102 / 25 * x - 10 := by linarith [sq_nonneg (x - 209 / 25)]
    have e2 : 0 ≤ x ^ 3 * (15 * x ^ 2 - 3102 / 25 * x - 10) := mul_nonneg (by positivity) hq
    rw [← hxx]
    linarith

/-- (β2) `X_mid ≤ 1.1315 x` and `X₋ ≤ 2.24 x`. -/
private theorem beta_X_le {r k : ℕ} (hk : 265 ≤ k) {x : ℝ} (hx : 0 < x)
    (hxx : x ^ 2 = (r : ℝ)) (hcube : 5 * x ^ 3 ≤ 11 * (k : ℝ)) :
    (r : ℝ) * ((r : ℝ) + 2) / (2 * (k : ℝ)) ≤ 2263 / 2000 * x ∧
      (r : ℝ) * ((r : ℝ) + 1) / ((k : ℝ) - 1) ≤ 56 / 25 * x := by
  have hK : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have e0 : 0 ≤ x * ((k : ℝ) - 265) := mul_nonneg hx.le (by linarith)
  rw [div_le_iff₀ (by linarith : (0 : ℝ) < 2 * (k : ℝ)),
    div_le_iff₀ (by linarith : (0 : ℝ) < (k : ℝ) - 1), ← hxx]
  rcases Nat.lt_or_ge r 70 with h70 | h70
  · -- `r ≤ 69`: `k ≥ 265`, `x ≤ 8.31`; `x (x² + 2) ≤ 8.31 · 71` and `x (x² + 1) ≤ 8.31 · 70`
    have hR69 : x ^ 2 ≤ 69 := by rw [hxx]; exact_mod_cast (by omega : r ≤ 69)
    have hx1 : x ≤ 831 / 100 := le_of_sq_le_sq (le_trans hR69 (by norm_num)) (by norm_num)
    have e1 : 0 ≤ x * (69 - x ^ 2) := mul_nonneg hx.le (by linarith)
    have e2 : 0 ≤ (831 / 100 - x) * (x * (x ^ 2 + 2)) := mul_nonneg (by linarith) (by positivity)
    have e3 : 0 ≤ (831 / 100 - x) * (x * (x ^ 2 + 1)) := mul_nonneg (by linarith) (by positivity)
    constructor <;> linarith
  · -- `r ≥ 70`: `k ≥ (5/11) x³` and `k - 1 ≥ (264/265) k`, so that
    -- `X_mid ≤ (11/10)(72/70) x` and `X₋ ≤ (11/5)(71/70)(265/264) x`
    have hR70 : (70 : ℝ) ≤ x ^ 2 := by rw [hxx]; exact_mod_cast h70
    have e1 : 0 ≤ x * (11 * (k : ℝ) - 5 * x ^ 3) := mul_nonneg hx.le (by linarith)
    have e2 : 0 ≤ x ^ 2 * (x ^ 2 - 70) := mul_nonneg (sq_nonneg x) (by linarith)
    constructor <;> linarith

/-- Frame β: `𝖦(r,k) ≥ 0.083 √r - 0.1533 > 0.157` for `r ≥ 14`. -/
private theorem Gfun_pos_beta {r k : ℕ} (hk : 265 ≤ k) (hr : 14 ≤ r)
    (hrk : 25 * r ^ 3 ≤ 121 * k ^ 2) : 0 < Gfun r k := by
  have hK : (265 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hR : (14 : ℝ) ≤ (r : ℝ) := by exact_mod_cast hr
  have hr1 : 1 ≤ r := by omega
  -- `x = √r`, with `s_r ≤ 1.261 x - 1/3` (P4)
  obtain ⟨x, hx, hxx, hs⟩ : ∃ x : ℝ, 0 < x ∧ x ^ 2 = (r : ℝ) ∧
      sbirth r ≤ 1261 / 1000 * x - 1 / 3 :=
    ⟨Real.sqrt r, Real.sqrt_pos.mpr (by linarith), Real.sq_sqrt (by linarith),
      sbirth_upper (r0 := 14) (by norm_num) hr (by norm_num)⟩
  -- `x ≥ 3.74`
  have hx0 : 187 / 50 ≤ x := by
    have e : (187 / 50 : ℝ) ^ 2 ≤ 14 := by norm_num
    exact le_of_sq_le_sq (by rw [hxx]; linarith) hx.le
  -- `25 r³ ≤ 121 k²` means `5 x³ ≤ 11 k`
  have hcube : 5 * x ^ 3 ≤ 11 * (k : ℝ) := by
    have hcast : (25 : ℝ) * (r : ℝ) ^ 3 ≤ 121 * (k : ℝ) ^ 2 := by exact_mod_cast hrk
    rw [← hxx] at hcast
    exact le_of_sq_le_sq (by linarith) (by positivity)
  -- (β1)
  have hT := beta_first_term hk hr hx hxx hcube
  -- (β2)
  obtain ⟨hXm, hXn⟩ := beta_X_le hk hx hxx hcube
  -- (β3) for `X_mid`, `(c, a, b) = (1.1315, 0.837, 0.92)`: `P(x) = 0.002081 x² + 0.0031 x + 0.4104`
  have hMm : 837 / 1000 * x - 23 / 25 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 2) / (2 * (k : ℝ))) :=
    mu0_lin hr1 hxx (by positivity) hXm (by linarith [sq_nonneg x])
  -- (β3) for `X₋`, `(c, a, b) = (2.24, 0.628, 0.62)`: `P(x) = 0.001704 x² + 0.04488 x - 0.0966`
  have hMn : 157 / 250 * x - 31 / 50 ≤ mu0 r ((r : ℝ) * ((r : ℝ) + 1) / ((k : ℝ) - 1)) :=
    mu0_lin hr1 hxx (div_nonneg (by positivity) (by linarith)) hXn (by linarith [sq_nonneg x])
  -- (β4)
  have hD := Dbirth_le_lin (by omega) hxx hs
  -- (β5): the sum is `0.083018… x - 0.153208…`
  have hfin := Gfun_ge hk (by omega) hT hMn hMm hD
  have hlow : 83 / 1000 * x - 1533 / 10000 ≤ Gfun r k := by linarith
  linarith

/-- **Positivity of the criterion function in the strip**: for `k ≥ 265` and
`2 ≤ r` with `25 r³ ≤ 121 k²` (i.e. `11 k ≥ 5 r^{3/2}`) the criterion function is positive.
Frame α covers `2 ≤ r ≤ 13`, frame β covers `r ≥ 14`. -/
theorem Gfun_pos {r k : ℕ} (hk : 265 ≤ k) (hr : 2 ≤ r) (hrk : 25 * r ^ 3 ≤ 121 * k ^ 2) :
    0 < Gfun r k := by
  rcases Nat.lt_or_ge r 14 with h14 | h14
  · exact Gfun_pos_alpha hk hr (by omega)
  · exact Gfun_pos_beta hk h14 hrk

end Parking
