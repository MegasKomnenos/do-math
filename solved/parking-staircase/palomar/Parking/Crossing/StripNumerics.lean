module

public import Parking.Basic.RealBounds
public import Mathlib.Analysis.Real.Pi.Bounds

/-!
# Real-variable inequalities for the crossing inside the strip

Everything in this file is about real numbers only.  The scale parameter is
`u = (5/(11k))^{1/3}`, i.e. `k u³ = 5/11`; the condition `25 (R-1)³ ≤ 121 k² < 25 R³` on `R` reads
`1 < R u² ≤ 1 + u²`, and `k ≥ 265` gives `u ≤ 3/25`.  In the statements below `K`, `ρ`, `c`, `a`,
`al`, `E`, `sm`, `s0`, `sp` stand for `k`, `R`, `c₀`, `ā`, `a̲`, `e^{ā}`, `√(R-1)`, `√R`, `√(R+1)`.

* `cstrip_tlow_core` : the lower bound `t̲` for the kernel deficit is nonnegative.
* `cstrip_main` : `Θ Ψ < L` for the three closed forms
  `Θ = t̄ e + e^{ā} (R+1)/N`, `Ψ = H̄ + (5/k) Ḡ`, `L = R(R+1)/N - 1 - S̄ - Ē` (`N = k + R`).

`cstrip_main` is obtained from `0 ≤ Θ ≤ u T(u)`, `u Ψ ≤ P(u)`, `u L ≥ Λ(u)` with explicit
polynomials `T`, `P`, `Λ`, and from `u T(u) P(u) < Λ(u)` on `[0, 3/25]`.  The polynomial
inequalities are proved by `linarith` from products of the nonnegative quantities displayed in
each proof.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### Polynomial inequalities -/

/-- `x²/2 - x³/3 + x⁴/4` is nondecreasing on `[0, 1]`. -/
private theorem cstrip_m_mono {x X : ℝ} (hx : 0 ≤ x) (hxX : x ≤ X) (hX : X ≤ 1) :
    x ^ 2 / 2 - x ^ 3 / 3 + x ^ 4 / 4 ≤ X ^ 2 / 2 - X ^ 3 / 3 + X ^ 4 / 4 := by
  have hX0 : 0 ≤ X := hx.trans hxX
  have hx1 : x ≤ 1 := hxX.trans hX
  have hB : 0 ≤ (X + x) / 2 - (X ^ 2 + X * x + x ^ 2) / 3
      + (X ^ 3 + X ^ 2 * x + X * x ^ 2 + x ^ 3) / 4 := by
    have t1 := mul_nonneg hX0 (sub_nonneg.2 hX)
    have t2 := mul_nonneg hx (sub_nonneg.2 hx1)
    have t3 := mul_nonneg hX0 (sub_nonneg.2 hx1)
    have t4 := mul_nonneg hx (sub_nonneg.2 hX)
    have t5 := pow_nonneg hX0 3
    have t6 := mul_nonneg (pow_nonneg hX0 2) hx
    have t7 := mul_nonneg hX0 (pow_nonneg hx 2)
    have t8 := pow_nonneg hx 3
    linarith
  have h := mul_nonneg (sub_nonneg.2 hxX) hB
  linarith

/-- `z³/3 - z⁴/4 + z⁵/5` is nondecreasing on `[0, 1]`. -/
private theorem cstrip_n_mono {z Z : ℝ} (hz : 0 ≤ z) (hzZ : z ≤ Z) (hZ : Z ≤ 1) :
    z ^ 3 / 3 - z ^ 4 / 4 + z ^ 5 / 5 ≤ Z ^ 3 / 3 - Z ^ 4 / 4 + Z ^ 5 / 5 := by
  have hZ0 : 0 ≤ Z := hz.trans hzZ
  have hz1 : z ≤ 1 := hzZ.trans hZ
  have hC : 0 ≤ (Z ^ 2 + Z * z + z ^ 2) / 3 - (Z ^ 3 + Z ^ 2 * z + Z * z ^ 2 + z ^ 3) / 4
      + (Z ^ 4 + Z ^ 3 * z + Z ^ 2 * z ^ 2 + Z * z ^ 3 + z ^ 4) / 5 := by
    have t1 := mul_nonneg (pow_nonneg hZ0 2) (sub_nonneg.2 hZ)
    have t2 := mul_nonneg (mul_nonneg hZ0 hz) (sub_nonneg.2 hZ)
    have t3 := mul_nonneg (mul_nonneg hZ0 hz) (sub_nonneg.2 hz1)
    have t4 := mul_nonneg (pow_nonneg hz 2) (sub_nonneg.2 hz1)
    have t5 := sq_nonneg (Z - z)
    have t6 := pow_nonneg hZ0 4
    have t7 := mul_nonneg (pow_nonneg hZ0 3) hz
    have t8 := mul_nonneg (pow_nonneg hZ0 2) (pow_nonneg hz 2)
    have t9 := mul_nonneg hZ0 (pow_nonneg hz 3)
    have t10 := pow_nonneg hz 4
    linarith
  have h := mul_nonneg (sub_nonneg.2 hzZ) hC
  linarith

/-- Powers of `u ∈ [0, 3/25]`. -/
private theorem cstrip_upows {u : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) :
    u ^ 2 ≤ 9 / 625 ∧ u ^ 3 ≤ 27 / 15625 ∧ u ^ 4 ≤ 81 / 390625 ∧ u ^ 5 ≤ 243 / 9765625
      ∧ u ^ 6 ≤ 729 / 244140625 ∧ u ^ 7 ≤ 2187 / 6103515625
      ∧ u ^ 8 ≤ 6561 / 152587890625 :=
  ⟨(pow_le_pow_left₀ hu hU 2).trans (by norm_num), (pow_le_pow_left₀ hu hU 3).trans (by norm_num),
    (pow_le_pow_left₀ hu hU 4).trans (by norm_num), (pow_le_pow_left₀ hu hU 5).trans (by norm_num),
    (pow_le_pow_left₀ hu hU 6).trans (by norm_num), (pow_le_pow_left₀ hu hU 7).trans (by norm_num),
    (pow_le_pow_left₀ hu hU 8).trans (by norm_num)⟩

/-- `R(R+1)/(k+R)` from below, in the normalised variables `r = R u²`. -/
private theorem cstrip_poly_Q1 {u r : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) (hr : 1 ≤ r) :
    (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) * (5 / 11 + r * u)
      ≤ r * (r + u ^ 2) := by
  obtain ⟨h2, h3, h4, h5, h6, h7, h8⟩ := cstrip_upows hu hU
  have hg : 0 ≤ 2 + u ^ 2
      - u * (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) := by
    have t1 := sq_nonneg u
    have t2 := pow_nonneg hu 4
    linarith
  have t3 := sq_nonneg (r - 1)
  have t4 := mul_nonneg (sub_nonneg.2 hr) hg
  have t5 := pow_nonneg hu 4
  linarith

/-- `(R+1)/(k+R)` from above, in the normalised variables `r = R u²`. -/
private theorem cstrip_poly_Q2 {u r : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) (hr1 : 1 ≤ r)
    (hr2 : r ≤ 1 + u ^ 2) :
    r + u ^ 2
      ≤ 11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2)) * (5 / 11 + r * u) := by
  have h2 : 0 ≤ 1 - 11 / 5 * u + 121 / 25 * u ^ 2 := by
    have := sq_nonneg u
    linarith
  have hm : 0 ≤ 11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2)) :=
    mul_nonneg (by norm_num) (mul_nonneg (by positivity) h2)
  have t1 := mul_nonneg (sub_nonneg.2 hr1) (mul_nonneg hm hu)
  have t2 := mul_nonneg (by positivity : (0 : ℝ) ≤ 1 + 2 * u ^ 2) (pow_nonneg hu 3)
  linarith

/-- `(R-2)(R-1)R(R+1)` from above, in the normalised variables `r = R u²`. -/
private theorem cstrip_poly_E {u r : ℝ} (hu2 : u ^ 2 ≤ 1) (hr1 : 1 ≤ r) (hr2 : r ≤ 1 + u ^ 2) :
    (r - 2 * u ^ 2) * (r - u ^ 2) * r * (r + u ^ 2) ≤ (1 + u ^ 2) ^ 2 := by
  have h0 : 0 ≤ r - u ^ 2 := by linarith
  have h1 : r - u ^ 2 ≤ 1 := by linarith
  have hr0 : 0 ≤ r := by linarith
  have hB : r * (r - u ^ 2) ≤ (1 + u ^ 2) * 1 := mul_le_mul hr2 h1 h0 (by positivity)
  have hB0 : 0 ≤ r * (r - u ^ 2) := mul_nonneg hr0 h0
  have hsq : (r * (r - u ^ 2)) ^ 2 ≤ ((1 + u ^ 2) * 1) ^ 2 := pow_le_pow_left₀ hB0 hB 2
  have t := mul_nonneg hB0 (by positivity : (0 : ℝ) ≤ u ^ 4)
  linarith

/-- The polynomial inequality behind `t̲ ≥ 0` (margin `0.0529` at `u = 3/25`). -/
private theorem cstrip_poly_B {u c : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) (hc : 19947 / 50000 ≤ c) :
    0 ≤ 2 * c * ((1 - u ^ 2 / 12) * (u * (1 - u ^ 2)))
      - (11 / 2 * u ^ 3 * (106 / 105 + 1 - c) + 11 * c * u ^ 2)
      - 633 / 1000 * (121 / 4 * ((1 - c) * u ^ 6
          + 2 / 3 * c * u ^ 3 * ((1 + u ^ 2) * (1 + u ^ 2 / 2)) + 2 * c * u ^ 5)) := by
  obtain ⟨h2, h3, h4, h5, h6, h7, h8⟩ := cstrip_upows hu hU
  have p5 := pow_nonneg hu 5
  have hA : 0 ≤ 2 * ((1 - u ^ 2 / 12) * (1 - u ^ 2)) + 11 / 2 * u ^ 2 - 11 * u
      - 633 / 1000 * (121 / 4 * (-u ^ 5 + 2 / 3 * u ^ 2 * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
          + 2 * u ^ 4)) := by
    linarith
  have hF : 0 ≤ 19947 / 50000 * (2 * ((1 - u ^ 2 / 12) * (1 - u ^ 2)) + 11 / 2 * u ^ 2 - 11 * u
      - 633 / 1000 * (121 / 4 * (-u ^ 5 + 2 / 3 * u ^ 2 * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
          + 2 * u ^ 4)))
      - (11 / 2 * u ^ 2 * (106 / 105 + 1) + 633 / 1000 * (121 / 4 * u ^ 5)) := by
    linarith
  have t1 := mul_nonneg hu (mul_nonneg (sub_nonneg.2 hc) hA)
  have t2 := mul_nonneg hu hF
  linarith

/-- The polynomial inequality behind `Θ ≥ 0`. -/
private theorem cstrip_poly_T0 {u c : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) (hc : 19947 / 50000 ≤ c) :
    0 ≤ 2 * c * u - 11 * u ^ 3 - 11 * c * u ^ 2 * (1 + u ^ 2 / 2) := by
  obtain ⟨h2, h3, h4, h5, h6, h7, h8⟩ := cstrip_upows hu hU
  have hg : 0 ≤ 2 - 11 * u - 11 / 2 * u ^ 3 := by linarith
  have hF : 0 ≤ 19947 / 50000 * (2 - 11 * u - 11 / 2 * u ^ 3) - 11 * u ^ 2 := by linarith
  have t1 := mul_nonneg hu (mul_nonneg (sub_nonneg.2 hc) hg)
  have t2 := mul_nonneg hu hF
  linarith

/-- `T(u)`: `Θ ≤ u T(u)`. -/
private noncomputable def cstripT (u : ℝ) : ℝ :=
  2 * (7979 / 20000) * (1 + 51 / 100 * u ^ 2)
    - ((11 / 2 * u ^ 2 - 484 / 75 * u ^ 5) * (2 - 9 / 4 * (7979 / 20000))
        + 2 * (7979 / 20000) * (11 / 2 * u - 484 / 75 * u ^ 4))
    + 106 / 105 * (11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2)))

/-- `P(u)`: `u Ψ ≤ P(u)`. -/
private noncomputable def cstripP (u : ℝ) : ℝ := 11 / 10 + 484 / 75 * u + 26 / 25 * u ^ 2

/-- `Λ(u)`: `u L ≥ Λ(u)`. -/
private noncomputable def cstripL (u : ℝ) : ℝ :=
  (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) - u
    - (u + 7979 / 20000 * (2 - u + 11 / 3 * u * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
        + 121 / 10 * (633 / 1000) * u ^ 2 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2))))
    - 1331 / 600 * u ^ 2 * (1 + u ^ 2) ^ 2

/-- The bound for `u Ψ` simplified to a quadratic. -/
private theorem cstrip_poly_P {u : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) :
    (11 / 10 - 121 / 75 * u + 3531 / 500 * u ^ 2)
      + (25 / 11 * u * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2)
          + 363 / 10 * u ^ 3 + 242 / 5 * u ^ 5 + 1331 / 50 * u ^ 6)
      ≤ cstripP u := by
  obtain ⟨h2, h3, h4, h5, h6, h7, h8⟩ := cstrip_upows hu hU
  have hb : 0 ≤ 911 / 125 - 74657 / 1250 * u - 242 / 5 * u ^ 3 - 1331 / 50 * u ^ 4 := by
    linarith
  have t := mul_nonneg (sq_nonneg u) hb
  unfold cstripP
  linarith

/-- The final inequality `u T(u) P(u) < Λ(u)` on `[0, 3/25]` (margin `0.0468` at `u = 3/25`;
the proof bounds the monomials separately, which leaves `0.0189`). -/
private theorem cstrip_poly_M {u : ℝ} (hu : 0 ≤ u) (hU : u ≤ 3 / 25) :
    u * cstripT u * cstripP u < cstripL u := by
  obtain ⟨h2, h3, h4, h5, h6, h7, h8⟩ := cstrip_upows hu hU
  have p3 := pow_nonneg hu 3
  have p5 := pow_nonneg hu 5
  unfold cstripT cstripP cstripL
  linarith

private theorem cstripP_nonneg {u : ℝ} (hu : 0 ≤ u) : 0 ≤ cstripP u := by
  unfold cstripP
  positivity

/-! ### The closed forms -/

/-- `t̲ ≥ 0` (without the factor `e⁻¹`): the three terms of `t̲` are bounded by polynomials in `u`
(`1/√(R+1) ≥ u (1 - u²)`, `1/(12R) ≤ u²/12`, `√(R-1) u ≤ 1`, `R√R u³ ≤ (1+u²)(1+u²/2)`). -/
theorem cstrip_tlow_core {u c ρ sm s0 sp a E : ℝ}
    (hu : 0 < u) (hU : u ≤ 3 / 25) (hc1 : 19947 / 50000 ≤ c)
    (hρ0 : 0 < ρ) (hρ1 : 1 < ρ * u ^ 2)
    (ha : a = 11 / 2 * u ^ 3)
    (hsm : sm * u ≤ 1)
    (hrs : ρ * u ^ 2 * (s0 * u) ≤ (1 + u ^ 2) * (1 + u ^ 2 / 2))
    (hsp0 : 0 < sp) (hsp : sp * u ≤ 1 + u ^ 2)
    (hE : E ≤ 106 / 105) :
    0 ≤ 2 * c * (1 - 1 / (12 * ρ)) / sp
        - a * (E + 1 + c * (2 * sm - 1))
        - 633 / 1000 * a ^ 2 * (1 + c * (2 / 3 * (ρ * s0) + 2 * sm - 1)) := by
  have hc0 : 0 ≤ c := by linarith
  have hu2 : u ^ 2 ≤ 9 / 625 := (pow_le_pow_left₀ hu.le hU 2).trans (by norm_num)
  have h1u : 0 ≤ 1 - u ^ 2 := by linarith
  -- first term
  have hA0 : 0 ≤ 1 - u ^ 2 / 12 := by linarith
  have hA : 1 - u ^ 2 / 12 ≤ 1 - 1 / (12 * ρ) := by
    have h12 : (0 : ℝ) < 12 * ρ := by linarith
    have h : 1 / (12 * ρ) ≤ u ^ 2 / 12 := by
      rw [div_le_iff₀ h12]
      linarith
    linarith
  have hB0 : 0 ≤ u * (1 - u ^ 2) := mul_nonneg hu.le h1u
  have hB : u * (1 - u ^ 2) ≤ 1 / sp := by
    rw [le_div_iff₀ hsp0]
    have h1 := mul_le_mul_of_nonneg_right hsp h1u
    have h2 := sq_nonneg (u ^ 2)
    linarith
  have hAB : (1 - u ^ 2 / 12) * (u * (1 - u ^ 2)) ≤ (1 - 1 / (12 * ρ)) * (1 / sp) :=
    mul_le_mul hA hB hB0 (hA0.trans hA)
  have hX1 : 2 * c * ((1 - u ^ 2 / 12) * (u * (1 - u ^ 2)))
      ≤ 2 * c * (1 - 1 / (12 * ρ)) / sp := by
    have e : 2 * c * (1 - 1 / (12 * ρ)) / sp = 2 * c * ((1 - 1 / (12 * ρ)) * (1 / sp)) := by
      ring
    rw [e]
    exact mul_le_mul_of_nonneg_left hAB (mul_nonneg (by norm_num) hc0)
  -- second term
  have hX2 : a * (E + 1 + c * (2 * sm - 1))
      ≤ 11 / 2 * u ^ 3 * (106 / 105 + 1 - c) + 11 * c * u ^ 2 := by
    rw [ha]
    have h1 : u ^ 3 * E ≤ u ^ 3 * (106 / 105) :=
      mul_le_mul_of_nonneg_left hE (pow_nonneg hu.le 3)
    have h2 : c * u ^ 2 * (sm * u) ≤ c * u ^ 2 * 1 :=
      mul_le_mul_of_nonneg_left hsm (mul_nonneg hc0 (sq_nonneg u))
    linarith
  -- third term
  have hX3 : 633 / 1000 * a ^ 2 * (1 + c * (2 / 3 * (ρ * s0) + 2 * sm - 1))
      ≤ 633 / 1000 * (121 / 4 * ((1 - c) * u ^ 6
          + 2 / 3 * c * u ^ 3 * ((1 + u ^ 2) * (1 + u ^ 2 / 2)) + 2 * c * u ^ 5)) := by
    rw [ha]
    have h1 : c * u ^ 3 * (ρ * u ^ 2 * (s0 * u)) ≤ c * u ^ 3 * ((1 + u ^ 2) * (1 + u ^ 2 / 2)) :=
      mul_le_mul_of_nonneg_left hrs (mul_nonneg hc0 (pow_nonneg hu.le 3))
    have h2 : c * u ^ 5 * (sm * u) ≤ c * u ^ 5 * 1 :=
      mul_le_mul_of_nonneg_left hsm (mul_nonneg hc0 (pow_nonneg hu.le 5))
    linarith
  have hpoly := cstrip_poly_B hu.le hU hc1
  linarith

/-- `0 ≤ Θ ≤ u T(u)` (without the factor `e⁻¹`). -/
private theorem cstrip_theta_core {u c K ρ sm s0 al E : ℝ}
    (hu : 0 < u) (hU : u ≤ 3 / 25) (hc1 : 19947 / 50000 ≤ c) (hc2 : c ≤ 7979 / 20000)
    (hK : K * u ^ 3 = 5 / 11) (hK0 : 0 < K) (hρ0 : 0 < ρ)
    (hρ1 : 1 < ρ * u ^ 2) (hρ2 : ρ * u ^ 2 ≤ 1 + u ^ 2)
    (hal : al = 11 / 2 * u ^ 3 - 484 / 75 * u ^ 6)
    (hsm0 : 0 < sm) (hsm : sm * u ≤ 1) (hsm' : 1 ≤ sm * u * (1 + 51 / 100 * u ^ 2))
    (hs00 : 0 ≤ s0) (hs0 : 1 ≤ s0 * u) (hs0' : s0 * u ≤ 1 + u ^ 2 / 2)
    (hE0 : 0 ≤ E) (hE : E ≤ 106 / 105) :
    0 ≤ 2 * c / sm - al * (2 + c * (2 * s0 - 2 - 1 / 4)) + E * (ρ + 1) / (K + ρ)
      ∧ 2 * c / sm - al * (2 + c * (2 * s0 - 2 - 1 / 4)) + E * (ρ + 1) / (K + ρ)
          ≤ u * cstripT u := by
  have hc0 : 0 ≤ c := by linarith
  obtain ⟨hu2, hu3, hu4, hu5, hu6, hu7, hu8⟩ := cstrip_upows hu.le hU
  have hKρ : 0 < K + ρ := by linarith
  -- the factor `(11/2) u² - (484/75) u⁵` and `a̲`
  have hfac0 : (0 : ℝ) ≤ 11 / 2 - 484 / 75 * u ^ 3 := by linarith
  have hfac : 0 ≤ 11 / 2 * u ^ 2 - 484 / 75 * u ^ 5 := by
    have h := mul_nonneg (sq_nonneg u) hfac0
    linarith
  have hal0 : 0 ≤ al := by
    rw [hal]
    have h := mul_nonneg (pow_nonneg hu.le 3) hfac0
    linarith
  have hal1 : al ≤ 11 / 2 * u ^ 3 := by
    rw [hal]
    have h := pow_nonneg hu.le 6
    linarith
  -- first term
  have hY1 : 2 * c / sm ≤ 2 * c * (u * (1 + 51 / 100 * u ^ 2)) := by
    rw [div_le_iff₀ hsm0]
    have h := mul_nonneg hc0 (sub_nonneg.2 hsm')
    linarith
  have hY1' : 2 * c * u ≤ 2 * c / sm := by
    rw [le_div_iff₀ hsm0]
    have h := mul_nonneg hc0 (sub_nonneg.2 hsm)
    linarith
  -- second term
  have hY2 : (11 / 2 * u ^ 3 - 484 / 75 * u ^ 6) * (2 - 9 / 4 * c)
        + 2 * c * (11 / 2 * u ^ 2 - 484 / 75 * u ^ 5)
      ≤ al * (2 + c * (2 * s0 - 2 - 1 / 4)) := by
    rw [hal]
    have h := mul_nonneg (mul_nonneg hc0 hfac) (sub_nonneg.2 hs0)
    linarith
  have hY2' : al * (2 + c * (2 * s0 - 2 - 1 / 4))
      ≤ 11 * u ^ 3 + 11 * c * u ^ 2 * (1 + u ^ 2 / 2) := by
    have hX : 2 + c * (2 * s0 - 2 - 1 / 4) ≤ 2 + 2 * c * s0 := by linarith
    have hX0 : 0 ≤ 2 + 2 * c * s0 := by
      have := mul_nonneg hc0 hs00
      linarith
    have h1 := mul_le_mul_of_nonneg_left hX hal0
    have h2 := mul_le_mul_of_nonneg_right hal1 hX0
    have h3 := mul_le_mul_of_nonneg_left hs0' (mul_nonneg hc0 (sq_nonneg u))
    linarith
  -- third term
  have hm0 : 0 ≤ 11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2)) := by
    have h2 : 0 ≤ 1 - 11 / 5 * u + 121 / 25 * u ^ 2 := by
      have := sq_nonneg u
      linarith
    exact mul_nonneg (by norm_num) (mul_nonneg (by positivity) h2)
  have hfrac : (ρ + 1) / (K + ρ)
      ≤ u * (11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2))) := by
    have key := cstrip_poly_Q2 hu.le hU hρ1.le hρ2
    have e1 : (ρ + 1) * u ^ 2 = ρ * u ^ 2 + u ^ 2 := by ring
    have e2 : u * (11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2))) * (K + ρ)
          * u ^ 2
        = 11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2))
          * (5 / 11 + ρ * u ^ 2 * u) := by
      linear_combination
        (11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2))) * hK
    rw [div_le_iff₀ hKρ]
    exact le_of_mul_le_mul_right (by rw [e1, e2]; exact key) (pow_pos hu 2)
  have hY3 : E * (ρ + 1) / (K + ρ)
      ≤ 106 / 105 * (u * (11 / 5 * ((1 + 2 * u ^ 2) * (1 - 11 / 5 * u + 121 / 25 * u ^ 2)))) := by
    have e : E * (ρ + 1) / (K + ρ) = E * ((ρ + 1) / (K + ρ)) := by ring
    rw [e]
    exact mul_le_mul hE hfrac (div_nonneg (by linarith) hKρ.le) (by norm_num)
  have hY3' : 0 ≤ E * (ρ + 1) / (K + ρ) := div_nonneg (mul_nonneg hE0 (by linarith)) hKρ.le
  refine ⟨?_, ?_⟩
  · have h0 := cstrip_poly_T0 hu.le hU hc1
    linarith
  · have hcoef : 0 ≤ 2 * (1 + 51 / 100 * u ^ 2) + 9 / 4 * (11 / 2 * u ^ 2 - 484 / 75 * u ^ 5)
        - 2 * (11 / 2 * u - 484 / 75 * u ^ 4) := by
      have t1 := sq_nonneg u
      have t2 := pow_nonneg hu.le 4
      linarith
    have hmono := mul_nonneg (sub_nonneg.2 hc2) (mul_nonneg hu.le hcoef)
    unfold cstripT
    linarith

/-- `u Ψ ≤ P(u)`, `Ψ = H̄ + (5/k) Ḡ`: with `x = (R-1)/(k+2)` and `z = (R-1)/(k+1)`, both at most
`(11/5) u`, the logarithms are bounded by their Taylor polynomials of degree 4 and 5. -/
private theorem cstrip_psi_core {u K ρ : ℝ} (hu : 0 < u) (hU : u ≤ 3 / 25)
    (hK : K * u ^ 3 = 5 / 11) (hK1 : 1 ≤ K) (hρ : 1 ≤ ρ)
    (hρ2 : ρ * u ^ 2 ≤ 1 + u ^ 2) :
    u * ((ρ - 1) - K * Real.log ((K + ρ + 1) / (K + 2))
        + 5 / K * ((ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1)
            + K * (K - 1) * Real.log ((K + ρ) / (K + 1))))
      ≤ cstripP u := by
  have hK0 : 0 < K := by linarith
  have hK2 : 0 < K + 2 := by linarith
  have hK1' : 0 < K + 1 := by linarith
  have hu3 : 0 < u ^ 3 := pow_pos hu 3
  have hX1 : 11 / 5 * u ≤ 1 := by linarith
  have hKK : 0 ≤ K * (K - 1) := mul_nonneg hK0.le (by linarith)
  -- the `H̄` part
  obtain ⟨x, hx⟩ : ∃ x : ℝ, x = (ρ - 1) / (K + 2) := ⟨_, rfl⟩
  have hx0 : 0 ≤ x := by rw [hx]; exact div_nonneg (by linarith) hK2.le
  have hxm : x * (K + 2) = ρ - 1 := by rw [hx]; exact div_mul_cancel₀ _ hK2.ne'
  have hxe : (K + ρ + 1) / (K + 2) = 1 + x := by
    have h : K + ρ + 1 = (K + 2) + (ρ - 1) := by ring
    rw [h, add_div, div_self hK2.ne', hx]
  have hxX : x ≤ 11 / 5 * u := by
    have h : x * (K + 2) * u ^ 2 ≤ 11 / 5 * u * (K + 2) * u ^ 2 := by
      rw [hxm]
      linarith
    exact le_of_mul_le_mul_right (le_of_mul_le_mul_right h (pow_pos hu 2)) hK2
  have hlog := log_one_add_ge4 hx0
  have hm := cstrip_m_mono hx0 hxX hX1
  have hH : u * ((ρ - 1) - K * Real.log ((K + ρ + 1) / (K + 2)))
      ≤ 11 / 10 - 121 / 75 * u + 3531 / 500 * u ^ 2 := by
    rw [hxe]
    have h1 : (ρ - 1) - K * Real.log (1 + x)
        ≤ 2 * x + K * (x ^ 2 / 2 - x ^ 3 / 3 + x ^ 4 / 4) := by
      have h := mul_le_mul_of_nonneg_left hlog hK0.le
      linarith
    have h2 : 2 * x + K * (x ^ 2 / 2 - x ^ 3 / 3 + x ^ 4 / 4)
        ≤ 2 * (11 / 5 * u)
          + K * ((11 / 5 * u) ^ 2 / 2 - (11 / 5 * u) ^ 3 / 3 + (11 / 5 * u) ^ 4 / 4) := by
      have h := mul_le_mul_of_nonneg_left hm hK0.le
      linarith
    have h3 : u * (2 * (11 / 5 * u)
          + K * ((11 / 5 * u) ^ 2 / 2 - (11 / 5 * u) ^ 3 / 3 + (11 / 5 * u) ^ 4 / 4))
        = 11 / 10 - 121 / 75 * u + 3531 / 500 * u ^ 2 := by
      linear_combination (121 / 50 - 1331 / 375 * u + 14641 / 2500 * u ^ 2) * hK
    calc u * ((ρ - 1) - K * Real.log (1 + x))
        ≤ u * (2 * (11 / 5 * u)
          + K * ((11 / 5 * u) ^ 2 / 2 - (11 / 5 * u) ^ 3 / 3 + (11 / 5 * u) ^ 4 / 4)) :=
          mul_le_mul_of_nonneg_left (h1.trans h2) hu.le
      _ = 11 / 10 - 121 / 75 * u + 3531 / 500 * u ^ 2 := h3
  -- the `Ḡ` part
  obtain ⟨z, hz⟩ : ∃ z : ℝ, z = (ρ - 1) / (K + 1) := ⟨_, rfl⟩
  have hz0 : 0 ≤ z := by rw [hz]; exact div_nonneg (by linarith) hK1'.le
  have hzm : z * (K + 1) = ρ - 1 := by rw [hz]; exact div_mul_cancel₀ _ hK1'.ne'
  have hze : (K + ρ) / (K + 1) = 1 + z := by
    have h : K + ρ = (K + 1) + (ρ - 1) := by ring
    rw [h, add_div, div_self hK1'.ne', hz]
  have hzZ : z ≤ 11 / 5 * u := by
    have h : z * (K + 1) * u ^ 2 ≤ 11 / 5 * u * (K + 1) * u ^ 2 := by
      rw [hzm]
      linarith
    exact le_of_mul_le_mul_right (le_of_mul_le_mul_right h (pow_pos hu 2)) hK1'
  have hlog5 := log_one_add_le5 hz0
  have h5K : 5 / K = 11 * u ^ 3 := by
    rw [div_eq_iff hK0.ne']
    linear_combination (-11 : ℝ) * hK
  have hν : 0 ≤ 1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2 := by
    have := sq_nonneg u
    linarith
  have hG : u * (5 / K * ((ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1)
        + K * (K - 1) * Real.log ((K + ρ) / (K + 1))))
      ≤ 25 / 11 * u * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2)
        + 363 / 10 * u ^ 3 + 242 / 5 * u ^ 5 + 1331 / 50 * u ^ 6 := by
    rw [hze, h5K]
    have hG1 : (ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1) + K * (K - 1) * Real.log (1 + z)
        ≤ 2 * z + (3 * K + 1) / 2 * z ^ 2
          + K * (K - 1) * (z ^ 3 / 3 - z ^ 4 / 4 + z ^ 5 / 5) := by
      have hsq : (ρ - 1) ^ 2 = (z * (K + 1)) ^ 2 := by rw [hzm]
      have hKz : K * (ρ - 1) = K * (z * (K + 1)) := by rw [hzm]
      have hKL := mul_le_mul_of_nonneg_left hlog5 hKK
      linarith
    have hG2 : 2 * z + (3 * K + 1) / 2 * z ^ 2
          + K * (K - 1) * (z ^ 3 / 3 - z ^ 4 / 4 + z ^ 5 / 5)
        ≤ 2 * (11 / 5 * u) + (3 * K + 1) / 2 * (11 / 5 * u) ^ 2
          + K * (K - 1) * ((11 / 5 * u) ^ 3 / 3 - (11 / 5 * u) ^ 4 / 4 + (11 / 5 * u) ^ 5 / 5) := by
      have h1 : z ^ 2 ≤ (11 / 5 * u) ^ 2 := pow_le_pow_left₀ hz0 hzZ 2
      have h2 := mul_le_mul_of_nonneg_left h1 (by linarith : (0 : ℝ) ≤ (3 * K + 1) / 2)
      have h3 := mul_le_mul_of_nonneg_left (cstrip_n_mono hz0 hzZ hX1) hKK
      linarith
    have hK2' : K ^ 2 * u ^ 6 = 25 / 121 := by
      have h : (K * u ^ 3) ^ 2 = (5 / 11) ^ 2 := by rw [hK]
      linear_combination h
    have e2 : 11 * u ^ 4 * (2 * (11 / 5 * u) + (3 * K + 1) / 2 * (11 / 5 * u) ^ 2
          + K * (K - 1) * ((11 / 5 * u) ^ 3 / 3 - (11 / 5 * u) ^ 4 / 4 + (11 / 5 * u) ^ 5 / 5))
        = 25 / 11 * u * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2)
          + 363 / 10 * u ^ 3
          - 5 * u ^ 4 * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2)
          + 242 / 5 * u ^ 5 + 1331 / 50 * u ^ 6 := by
      linear_combination
        (3993 / 50 * u ^ 3
            - 11 * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2) * u ^ 4) * hK
          + (11 * (1331 / 375 - 14641 / 2500 * u + 161051 / 15625 * u ^ 2) * u) * hK2'
    have h4 := mul_le_mul_of_nonneg_left (hG1.trans hG2)
      (mul_nonneg (by norm_num : (0 : ℝ) ≤ 11) (pow_nonneg hu.le 4))
    have h5 := mul_nonneg (mul_nonneg (by norm_num : (0 : ℝ) ≤ 5) (pow_nonneg hu.le 4)) hν
    have e1 : u * (11 * u ^ 3 * ((ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1)
          + K * (K - 1) * Real.log (1 + z)))
        = 11 * u ^ 4 * ((ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1)
          + K * (K - 1) * Real.log (1 + z)) := by ring
    rw [e1]
    linarith
  have hP := cstrip_poly_P hu.le hU
  linarith

/-- `u L ≥ Λ(u)`, `L = R(R+1)/N - 1 - S̄ - Ē`. -/
private theorem cstrip_L_core {u c K ρ sm s0 a : ℝ} (hu : 0 < u) (hU : u ≤ 3 / 25)
    (hc0 : 0 ≤ c) (hc2 : c ≤ 7979 / 20000)
    (hK : K * u ^ 3 = 5 / 11) (hK0 : 0 < K) (hρ0 : 0 < ρ)
    (hρ1 : 1 < ρ * u ^ 2) (hρ2 : ρ * u ^ 2 ≤ 1 + u ^ 2)
    (ha : a = 11 / 2 * u ^ 3)
    (hsm : sm * u ≤ 1) (hs00 : 0 ≤ s0) (hs0' : s0 * u ≤ 1 + u ^ 2 / 2) :
    cstripL u ≤ u * (ρ * (ρ + 1) / (K + ρ) - 1
        - (1 + c * (2 * sm - 1 + 2 * a / 3 * (ρ * s0)
            + 2 * (633 / 1000) * a ^ 2 / 5 * (ρ ^ 2 * s0)))
        - 5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1) / (24 * K ^ 3)) := by
  have hu2 : u ^ 2 ≤ 9 / 625 := (pow_le_pow_left₀ hu.le hU 2).trans (by norm_num)
  have hKρ : 0 < K + ρ := by linarith
  -- the main term
  have hQ : 11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3
      ≤ u * (ρ * (ρ + 1) / (K + ρ)) := by
    have key := cstrip_poly_Q1 hu.le hU hρ1.le
    have e1 : (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) * (K + ρ)
          * u ^ 3
        = (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3)
          * (5 / 11 + ρ * u ^ 2 * u) := by
      linear_combination (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) * hK
    have e2 : u * (ρ * (ρ + 1)) * u ^ 3 = ρ * u ^ 2 * (ρ * u ^ 2 + u ^ 2) := by ring
    have h3 : (11 / 5 - 121 / 25 * u + 1606 / 125 * u ^ 2 - 17666 / 625 * u ^ 3) * (K + ρ)
        ≤ u * (ρ * (ρ + 1)) :=
      le_of_mul_le_mul_right (by rw [e1, e2]; exact key) (pow_pos hu 3)
    have e3 : u * (ρ * (ρ + 1) / (K + ρ)) = u * (ρ * (ρ + 1)) / (K + ρ) := by ring
    rw [e3, le_div_iff₀ hKρ]
    exact h3
  -- `S̄`
  have hS : u * (1 + c * (2 * sm - 1 + 2 * a / 3 * (ρ * s0)
        + 2 * (633 / 1000) * a ^ 2 / 5 * (ρ ^ 2 * s0)))
      ≤ u + 7979 / 20000 * (2 - u + 11 / 3 * u * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
          + 121 / 10 * (633 / 1000) * u ^ 2 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2))) := by
    have hr0 : 0 ≤ ρ * u ^ 2 := mul_nonneg hρ0.le (sq_nonneg u)
    have hσ0 : 0 ≤ s0 * u := mul_nonneg hs00 hu.le
    have h1 : ρ * u ^ 2 * (s0 * u) ≤ (1 + u ^ 2) * (1 + u ^ 2 / 2) :=
      mul_le_mul hρ2 hs0' hσ0 (by positivity)
    have h2 : (ρ * u ^ 2) ^ 2 ≤ (1 + u ^ 2) ^ 2 := pow_le_pow_left₀ hr0 hρ2 2
    have h3 : (ρ * u ^ 2) ^ 2 * (s0 * u) ≤ (1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2) :=
      mul_le_mul h2 hs0' hσ0 (by positivity)
    have h4 : 633 / 1000 * ((ρ * u ^ 2) ^ 2 * (s0 * u))
        ≤ 633 / 1000 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2)) :=
      mul_le_mul_of_nonneg_left h3 (by norm_num)
    have h5 := mul_le_mul_of_nonneg_left h1 hu.le
    have h6 := mul_le_mul_of_nonneg_left h4 (sq_nonneg u)
    have hin : 2 * (sm * u) - u + 11 / 3 * u * (ρ * u ^ 2 * (s0 * u))
          + 121 / 10 * (633 / 1000) * u ^ 2 * ((ρ * u ^ 2) ^ 2 * (s0 * u))
        ≤ 2 - u + 11 / 3 * u * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
          + 121 / 10 * (633 / 1000) * u ^ 2 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2)) := by
      linarith
    have hXS0 : 0 ≤ 2 - u + 11 / 3 * u * ((1 + u ^ 2) * (1 + u ^ 2 / 2))
          + 121 / 10 * (633 / 1000) * u ^ 2 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2)) := by
      have t1 : 0 ≤ 11 / 3 * u * ((1 + u ^ 2) * (1 + u ^ 2 / 2)) :=
        mul_nonneg (mul_nonneg (by norm_num) hu.le) (by positivity)
      have t2 : 0 ≤ 121 / 10 * (633 / 1000) * u ^ 2 * ((1 + u ^ 2) ^ 2 * (1 + u ^ 2 / 2)) := by
        positivity
      linarith
    have h7 := mul_le_mul_of_nonneg_left hin hc0
    have h8 := mul_le_mul_of_nonneg_right hc2 hXS0
    have e : u * (1 + c * (2 * sm - 1 + 2 * a / 3 * (ρ * s0)
          + 2 * (633 / 1000) * a ^ 2 / 5 * (ρ ^ 2 * s0)))
        = u + c * (2 * (sm * u) - u + 11 / 3 * u * (ρ * u ^ 2 * (s0 * u))
          + 121 / 10 * (633 / 1000) * u ^ 2 * ((ρ * u ^ 2) ^ 2 * (s0 * u))) := by
      rw [ha]; ring
    rw [e]
    linarith
  -- `Ē`
  have hE : u * (5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1) / (24 * K ^ 3))
      ≤ 1331 / 600 * u ^ 2 * (1 + u ^ 2) ^ 2 := by
    have hK3 : K ^ 3 * u ^ 9 = 125 / 1331 := by
      have h : (K * u ^ 3) ^ 3 = (5 / 11) ^ 3 := by rw [hK]
      linear_combination h
    have h24 : (0 : ℝ) < 24 * K ^ 3 := by positivity
    have key := cstrip_poly_E (u := u) (r := ρ * u ^ 2) (by linarith) hρ1.le hρ2
    have e1 : u * (5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1)) * u ^ 9
        = 5 * u ^ 2 * ((ρ * u ^ 2 - 2 * u ^ 2) * (ρ * u ^ 2 - u ^ 2) * (ρ * u ^ 2)
          * (ρ * u ^ 2 + u ^ 2)) := by ring
    have e2 : 1331 / 600 * u ^ 2 * (1 + u ^ 2) ^ 2 * (24 * K ^ 3) * u ^ 9
        = 5 * u ^ 2 * (1 + u ^ 2) ^ 2 := by
      linear_combination (1331 / 600 * u ^ 2 * (1 + u ^ 2) ^ 2 * 24) * hK3
    have h3 : u * (5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1))
        ≤ 1331 / 600 * u ^ 2 * (1 + u ^ 2) ^ 2 * (24 * K ^ 3) :=
      le_of_mul_le_mul_right
        (by rw [e1, e2]
            exact mul_le_mul_of_nonneg_left key
              (mul_nonneg (by norm_num : (0 : ℝ) ≤ 5) (sq_nonneg u)))
        (pow_pos hu 9)
    have e3 : u * (5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1) / (24 * K ^ 3))
        = u * (5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1)) / (24 * K ^ 3) := by ring
    rw [e3, div_le_iff₀ h24]
    exact h3
  unfold cstripL
  linarith

/-- From `0 ≤ Θ ≤ u T`, `u Ψ ≤ P`, `P ≥ 0`, `Λ ≤ u L` and `u T P < Λ` conclude `Θ Ψ < L`. -/
private theorem cstrip_assemble {u Th Ps L T P Lh : ℝ} (hu : 0 < u) (hT0 : 0 ≤ Th)
    (hT : Th ≤ u * T) (hPs : u * Ps ≤ P) (hP0 : 0 ≤ P) (hL : Lh ≤ u * L)
    (hfin : u * T * P < Lh) : Th * Ps < L := by
  have h1 : Th * (u * Ps) ≤ Th * P := mul_le_mul_of_nonneg_left hPs hT0
  have h2 : Th * P ≤ u * T * P := mul_le_mul_of_nonneg_right hT hP0
  have h3 : u * (Th * Ps) < u * L := by
    have e : u * (Th * Ps) = Th * (u * Ps) := by ring
    rw [e]
    linarith
  exact lt_of_mul_lt_mul_left h3 hu.le

/-- The main inequality `Θ Ψ < L` (without the factor `e⁻¹` on both sides), where
`Θ = 2c₀/√(R-1) - a̲ (2 + c₀ (2√R - 9/4)) + e^{ā} (R+1)/(k+R)`, `Ψ = H̄ + (5/k) Ḡ` and
`L = R(R+1)/(k+R) - 1 - S̄ - Ē`. -/
theorem cstrip_main {u c K ρ sm s0 a al E : ℝ} (hu : 0 < u) (hU : u ≤ 3 / 25)
    (hc1 : 19947 / 50000 ≤ c) (hc2 : c ≤ 7979 / 20000)
    (hK : K * u ^ 3 = 5 / 11) (hK1 : 1 ≤ K)
    (hρ1 : 1 < ρ * u ^ 2) (hρ2 : ρ * u ^ 2 ≤ 1 + u ^ 2)
    (ha : a = 11 / 2 * u ^ 3) (hal : al = 11 / 2 * u ^ 3 - 484 / 75 * u ^ 6)
    (hsm0 : 0 < sm) (hsm : sm * u ≤ 1) (hsm' : 1 ≤ sm * u * (1 + 51 / 100 * u ^ 2))
    (hs00 : 0 ≤ s0) (hs0 : 1 ≤ s0 * u) (hs0' : s0 * u ≤ 1 + u ^ 2 / 2)
    (hE0 : 0 ≤ E) (hE : E ≤ 106 / 105) :
    (2 * c / sm - al * (2 + c * (2 * s0 - 2 - 1 / 4)) + E * (ρ + 1) / (K + ρ))
        * ((ρ - 1) - K * Real.log ((K + ρ + 1) / (K + 2))
          + 5 / K * ((ρ ^ 2 - 1) / 2 - (K - 1) * (ρ - 1)
            + K * (K - 1) * Real.log ((K + ρ) / (K + 1))))
      < ρ * (ρ + 1) / (K + ρ) - 1
        - (1 + c * (2 * sm - 1 + 2 * a / 3 * (ρ * s0)
            + 2 * (633 / 1000) * a ^ 2 / 5 * (ρ ^ 2 * s0)))
        - 5 * (ρ - 2) * (ρ - 1) * ρ * (ρ + 1) / (24 * K ^ 3) := by
  have hK0 : 0 < K := by linarith
  have hρ : 1 ≤ ρ := by
    by_contra h
    have h1 : ρ * u ^ 2 < 1 * u ^ 2 := mul_lt_mul_of_pos_right (not_le.mp h) (pow_pos hu 2)
    have h2 : u ^ 2 ≤ 9 / 625 := (pow_le_pow_left₀ hu.le hU 2).trans (by norm_num)
    linarith
  have hρ0 : 0 < ρ := by linarith
  obtain ⟨hT0, hT⟩ := cstrip_theta_core hu hU hc1 hc2 hK hK0 hρ0 hρ1 hρ2 hal hsm0 hsm hsm'
    hs00 hs0 hs0' hE0 hE
  have hPs := cstrip_psi_core hu hU hK hK1 hρ hρ2
  have hL := cstrip_L_core hu hU (by linarith : (0 : ℝ) ≤ c) hc2 hK hK0 hρ0 hρ1 hρ2 ha hsm hs00
    hs0'
  exact cstrip_assemble hu hT0 hT hPs (cstripP_nonneg hu.le) hL (cstrip_poly_M hu.le hU)

end Parking
