module

public import Parking.Basic.RealBounds
public import Parking.Cayley.BorelSum
public import Parking.Crossing.Criterion

/-!
# Explicit bounds for the two sides of the crossing criterion

With `ā = 5/(2k)`, `a̲ = 5/(2k) - 4/(3k²)`, `q = 0.633`, `c₀ = 1/√(2π)`, and for `k ≥ 2`, `R ≥ 2`
(and `ā R ≤ 0.6679` where `q` occurs, so that `e^s ≤ 1 + s + q s²` for `0 ≤ s ≤ ā R`):

* (i) `xk_log_bounds`, `xk_bounds` : `a̲ ≤ 1 + log x ≤ ā`, hence `e^{-1} ≤ x ≤ e^{-1} e^{ā}`;
* (ii) `SR_le` : `S_R ≤ S̄`;
* (iii) `ecorSum_le` : `𝖤 ≤ Ē`;
* (iv) `ecor_Somg_bounds` : `0 ≤ 𝖾_{N-1} + Σ_ω ≤ H̄ + (5/k) Ḡ`;
* (v) `tlow_le_kbar`, `kbar_le_tup` : `t̲ ≤ κ̄_R ≤ t̄`;
* `cross_of_bounds` : if `ā R ≤ 0.6679`, `t̲ ≥ 0` and
  `(t̄ + e^{-1} e^{ā} (R+1)/N) (H̄ + (5/k) Ḡ) < e^{-1} (R(R+1)/N - 1 - S̄ - Ē)`, `N = k + R`,
  then column `k` turns positive by row `N`.

(iii) and (iv) rest on `log (x γ_i) ≤ 5 (i - k)/(2 k i)` (`log_xk_gam_le`) and on the recursion
`𝖾_{j+1} = (j-k+2)(1 - 1/(x γ_{j+1})) + 𝖾_j/(x γ_{j+1})`.  (ii) and (v) rest on the bounds
`c₀ (1 - 1/(12 i))/√i ≤ e^{-i} i^i/i! ≤ c₀/√i` and on writing `x = e^{a-1}`, `a = 1 + log x`:
then `(i x)^i/i! = e^{-i} i^i/i! · e^{a i}` and `κ_m = e^{a m} · e^{-m} ε_m`, where
`∑_{m ≥ 1} e^{-m} ε_m = 1 - e^{-1}`.

(In `tup` the constant `ζ(3/2)` is replaced by its upper bound `3`.)
-/

@[expose] public section

namespace Parking

open Finset

/-- `ā = 5/(2k)`. -/
noncomputable def abar (k : ℕ) : ℝ := 5 / (2 * (k : ℝ))

/-- `a̲ = 5/(2k) - 4/(3k²)`. -/
noncomputable def alow (k : ℕ) : ℝ := 5 / (2 * (k : ℝ)) - 4 / (3 * (k : ℝ) ^ 2)

/-- `S̄ = 1 + c₀ [2√(R-1) - 1 + (2ā/3) R^{3/2} + (2qā²/5) R^{5/2}]`, `q = 0.633`. -/
noncomputable def Sbar (k R : ℕ) : ℝ :=
  1 + c0 * (2 * Real.sqrt ((R : ℝ) - 1) - 1 + 2 * abar k / 3 * ((R : ℝ) * Real.sqrt R)
    + 2 * (633 / 1000) * abar k ^ 2 / 5 * ((R : ℝ) ^ 2 * Real.sqrt R))

/-- `Ē = 5(R-2)(R-1)R(R+1)/(24k³)`. -/
noncomputable def Ebar (k R : ℕ) : ℝ :=
  5 * ((R : ℝ) - 2) * ((R : ℝ) - 1) * R * ((R : ℝ) + 1) / (24 * (k : ℝ) ^ 3)

/-- `H̄ = (R-1) - k log((k+R+1)/(k+2))`. -/
noncomputable def Hbar (k R : ℕ) : ℝ :=
  ((R : ℝ) - 1) - k * Real.log (((k : ℝ) + R + 1) / ((k : ℝ) + 2))

/-- `Ḡ = (R²-1)/2 - (k-1)(R-1) + k(k-1) log((k+R)/(k+1))`. -/
noncomputable def Gbar (k R : ℕ) : ℝ :=
  ((R : ℝ) ^ 2 - 1) / 2 - ((k : ℝ) - 1) * ((R : ℝ) - 1)
    + (k : ℝ) * ((k : ℝ) - 1) * Real.log (((k : ℝ) + R) / ((k : ℝ) + 1))

/-- Lower bound `t̲` for the kernel deficit `κ̄_R` (`q = 0.633`). -/
noncomputable def tlow (k R : ℕ) : ℝ :=
  2 * Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((R : ℝ) + 1)
    - Real.exp (-1) * abar k * (Real.exp (abar k) + 1 + c0 * (2 * Real.sqrt ((R : ℝ) - 1) - 1))
    - Real.exp (-1) * (633 / 1000) * abar k ^ 2
        * (1 + c0 * (2 / 3 * ((R : ℝ) * Real.sqrt R) + 2 * Real.sqrt ((R : ℝ) - 1) - 1))

/-- Upper bound `t̄` for the kernel deficit `κ̄_R`. -/
noncomputable def tup (k R : ℕ) : ℝ :=
  2 * Real.exp (-1) * c0 / Real.sqrt ((R : ℝ) - 1)
    - Real.exp (-1) * alow k * (2 + c0 * (2 * Real.sqrt R - 2 - 1 / 4))

/-! ### (i) the tilt `x = 1/γ_k` -/

private theorem abar_pos {k : ℕ} (hk : 2 ≤ k) : 0 < abar k := by
  have hk0 : (2 : ℝ) ≤ k := by exact_mod_cast hk
  unfold abar
  exact div_pos (by norm_num) (by linarith)

private theorem alow_nonneg {k : ℕ} (hk : 2 ≤ k) : 0 ≤ alow k := by
  have hkr : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hkne : (k : ℝ) ≠ 0 := by linarith
  have e : 5 / (2 * (k : ℝ)) - 4 / (3 * (k : ℝ) ^ 2)
      = (15 * (k : ℝ) - 8) / (6 * (k : ℝ) ^ 2) := by
    field
  unfold alow
  rw [e]
  exact div_nonneg (by linarith) (by positivity)

/-- `log γ_m = (m - 2) log (1 + 1/m)`. -/
private theorem log_gam {m : ℕ} (hm : 2 ≤ m) :
    Real.log (gam m) = ((m : ℝ) - 2) * Real.log (1 + 1 / (m : ℝ)) := by
  have hc : ((m - 2 : ℕ) : ℝ) = (m : ℝ) - 2 := by
    rw [Nat.cast_sub hm]
    norm_num
  unfold gam
  rw [Real.log_pow, hc]

/-- (i) `a̲ ≤ 1 + log x ≤ ā`: here `1 + log x = 1 - (k-2) log (1 + 1/k)`, and
`1/k - 1/(2k²) ≤ log (1 + 1/k) ≤ 1/k - 1/(2k²) + 1/(3k³)`. -/
private theorem xk_log_bounds {k : ℕ} (hk : 2 ≤ k) :
    alow k ≤ 1 + Real.log (xk k) ∧ 1 + Real.log (xk k) ≤ abar k := by
  have hkr : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hkne : (k : ℝ) ≠ 0 := by linarith
  have hu : (0 : ℝ) ≤ 1 / (k : ℝ) := by positivity
  have hk2 : (0 : ℝ) ≤ (k : ℝ) - 2 := by linarith
  have hlo := mul_le_mul_of_nonneg_left (log_one_add_ge2 hu) hk2
  have hup := mul_le_mul_of_nonneg_left (log_one_add_le3 hu) hk2
  have e : 1 + Real.log (xk k) = 1 - ((k : ℝ) - 2) * Real.log (1 + 1 / (k : ℝ)) := by
    unfold xk
    rw [Real.log_inv, log_gam hk]
    ring
  have e1 : 1 - ((k : ℝ) - 2) * (1 / (k : ℝ) - (1 / (k : ℝ)) ^ 2 / 2)
      = 5 / (2 * (k : ℝ)) - 1 / (k : ℝ) ^ 2 := by
    field
  have e2 : 1 - ((k : ℝ) - 2) * (1 / (k : ℝ) - (1 / (k : ℝ)) ^ 2 / 2 + (1 / (k : ℝ)) ^ 3 / 3)
      = 5 / (2 * (k : ℝ)) - 4 / (3 * (k : ℝ) ^ 2) + 2 / (3 * (k : ℝ) ^ 3) := by
    field
  have h2 : (0 : ℝ) ≤ 1 / (k : ℝ) ^ 2 := by positivity
  have h3 : (0 : ℝ) ≤ 2 / (3 * (k : ℝ) ^ 3) := by positivity
  rw [e]
  unfold alow abar
  constructor <;> linarith

/-- (i) `e^{-1} ≤ x ≤ e^{-1} e^{ā}`. -/
theorem xk_bounds {k : ℕ} (hk : 2 ≤ k) :
    Real.exp (-1) ≤ xk k ∧ xk k ≤ Real.exp (-1) * Real.exp (abar k) := by
  obtain ⟨h1, h2⟩ := xk_log_bounds hk
  have ha0 : 0 ≤ alow k := alow_nonneg hk
  have e : Real.exp (Real.log (xk k)) = xk k := Real.exp_log (CrossCrit.xk_pos k)
  constructor
  · rw [← e]
    exact Real.exp_le_exp.mpr (by linarith)
  · rw [← e, ← Real.exp_add]
    exact Real.exp_le_exp.mpr (by linarith)

/-! ### `log (x γ_i) ≤ 5 (i - k) / (2 k i)` -/

/-- The rational inequality behind `log_gam_step`: with the upper Taylor bound of degree 3 at
`1/(m+1)` and the lower Taylor bound of degree 4 at `1/m`. -/
private theorem log_gam_step_poly (m : ℝ) (hm : 2 ≤ m) :
    (m - 1) * (1 / (m + 1) - (1 / (m + 1)) ^ 2 / 2 + (1 / (m + 1)) ^ 3 / 3)
        - (m - 2) * (1 / m - (1 / m) ^ 2 / 2 + (1 / m) ^ 3 / 3 - (1 / m) ^ 4 / 4)
      ≤ 5 / (2 * m * (m + 1)) := by
  have hmne : m ≠ 0 := by linarith
  have hm1ne : m + 1 ≠ 0 := by linarith
  have ht : 0 ≤ m - 2 := by linarith
  have key : 5 / (2 * m * (m + 1))
      - ((m - 1) * (1 / (m + 1) - (1 / (m + 1)) ^ 2 / 2 + (1 / (m + 1)) ^ 3 / 3)
        - (m - 2) * (1 / m - (1 / m) ^ 2 / 2 + (1 / m) ^ 3 / 3 - (1 / m) ^ 4 / 4))
      = (29 * (m - 2) ^ 4 + 253 * (m - 2) ^ 3 + 823 * (m - 2) ^ 2 + 1191 * (m - 2) + 656)
          / (12 * m ^ 4 * (m + 1) ^ 3) := by
    field
  have hpos : 0 ≤ (29 * (m - 2) ^ 4 + 253 * (m - 2) ^ 3 + 823 * (m - 2) ^ 2
      + 1191 * (m - 2) + 656) / (12 * m ^ 4 * (m + 1) ^ 3) :=
    div_nonneg (by positivity) (by positivity)
  linarith

/-- `log γ_{m+1} - log γ_m ≤ 5 / (2 m (m+1))` for `m ≥ 2`. -/
private theorem log_gam_step {m : ℕ} (hm : 2 ≤ m) :
    Real.log (gam (m + 1)) - Real.log (gam m) ≤ 5 / (2 * (m : ℝ) * ((m : ℝ) + 1)) := by
  have hmr : (2 : ℝ) ≤ (m : ℝ) := by exact_mod_cast hm
  have h1 : Real.log (gam (m + 1))
      = ((m : ℝ) - 1) * Real.log (1 + 1 / ((m : ℝ) + 1)) := by
    rw [log_gam (m := m + 1) (by omega), Nat.cast_add_one]
    ring
  have ha := mul_le_mul_of_nonneg_left (log_one_add_le3 (u := 1 / ((m : ℝ) + 1)) (by positivity))
    (by linarith : (0 : ℝ) ≤ (m : ℝ) - 1)
  have hb := mul_le_mul_of_nonneg_left (log_one_add_ge4 (u := 1 / (m : ℝ)) (by positivity))
    (by linarith : (0 : ℝ) ≤ (m : ℝ) - 2)
  have hpoly := log_gam_step_poly (m : ℝ) hmr
  rw [h1, log_gam hm]
  linarith

/-- `log (x γ_i) ≤ 5 (i - k) / (2 k i)` for `i ≥ k ≥ 2`: telescope `log_gam_step`, as
`5/(2m(m+1)) = (5/2)(1/m - 1/(m+1))`. -/
private theorem log_xk_gam_le {k i : ℕ} (hk : 2 ≤ k) (hi : k ≤ i) :
    Real.log (xk k * gam i) ≤ 5 * ((i : ℝ) - k) / (2 * (k : ℝ) * i) := by
  have hkne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hlog : Real.log (xk k * gam i) = Real.log (gam i) - Real.log (gam k) := by
    unfold xk
    rw [Real.log_mul (inv_ne_zero (gam_pos k).ne') (gam_pos i).ne',
      Real.log_inv]
    ring
  rw [hlog]
  clear hlog
  induction i, hi using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    have hstep := log_gam_step (m := n) (by omega)
    have hnne : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    have hn1ne : (n : ℝ) + 1 ≠ 0 := by positivity
    have e : 5 * ((n : ℝ) - k) / (2 * (k : ℝ) * n) + 5 / (2 * (n : ℝ) * ((n : ℝ) + 1))
        = 5 * ((n : ℝ) + 1 - k) / (2 * (k : ℝ) * ((n : ℝ) + 1)) := by
      field
    rw [Nat.cast_add_one]
    linarith

/-! ### (iii) the corrections `𝖾_j` and `𝖤` -/

/-- `𝖾_k = 0`. -/
private theorem ecor_base {k : ℕ} (hk : 2 ≤ k) : ecor k k = 0 := by
  have hp : pix k k ≠ 0 := (CrossCrit.pix_pos k (by omega : 0 < k)).ne'
  have h1 : pix k (k + 1) = pix k k := by
    rw [CrossCrit.pix_succ k hk, CrossCrit.xk_mul_gam, one_mul]
  have hP : pixSum k (k + 1) = pix k k + pix k (k + 1) := by
    unfold pixSum
    rw [Finset.sum_Icc_succ_top (by omega : k ≤ k + 1), Finset.Icc_self, Finset.sum_singleton]
  have h2 : (pix k k + pix k k) / pix k k = 2 := by
    field
  unfold ecor
  rw [hP, h1, h2]
  ring

/-- For `j ≥ k` and `r = x γ_{j+1}`: `𝖾_{j+1} = (j-k+2)(1 - 1/r) + 𝖾_j/r`.  Since `r ≥ 1`,
`1 - 1/r ≤ log r` and `𝖾_j ≥ 0`, this gives `𝖾_{j+1} ≤ (j-k+2) log (x γ_{j+1}) + 𝖾_j`. -/
private theorem ecor_succ_le {k j : ℕ} (hk : 2 ≤ k) (hj : k ≤ j) :
    ecor k (j + 1) ≤ ((j : ℝ) - k + 2) * Real.log (xk k * gam (j + 1)) + ecor k j := by
  have hr1 : 1 ≤ xk k * gam (j + 1) := CrossCrit.one_le_xk_mul_gam hk (by omega)
  have hr0 : 0 < xk k * gam (j + 1) := by linarith
  have hp : pix k (j + 1) ≠ 0 := (CrossCrit.pix_pos k (by omega)).ne'
  have hP : pixSum k (j + 1 + 1) = pixSum k (j + 1) + pix k (j + 1 + 1) :=
    Finset.sum_Icc_succ_top (by omega) _
  have alg : ∀ c P p r : ℝ, p ≠ 0 → r ≠ 0 →
      (c + 1) - (P + r * p) / (r * p) = c * (1 - r⁻¹) + (c - P / p) * r⁻¹ := by
    intro c P p r hp hr
    field
  have hrec : ecor k (j + 1) = ((j : ℝ) - k + 2) * (1 - (xk k * gam (j + 1))⁻¹)
      + ecor k j * (xk k * gam (j + 1))⁻¹ := by
    unfold ecor
    rw [hP, CrossCrit.pix_succ k (n := j + 1) (by omega), Nat.cast_add_one]
    linear_combination alg ((j : ℝ) - k + 2) (pixSum k (j + 1)) (pix k (j + 1))
      (xk k * gam (j + 1)) hp hr0.ne'
  have he : 0 ≤ ecor k j := CrossCrit.ecor_nonneg hk hj
  have hc : (0 : ℝ) ≤ (j : ℝ) - k + 2 := by
    have : (k : ℝ) ≤ (j : ℝ) := by exact_mod_cast hj
    linarith
  have h3 := mul_le_mul_of_nonneg_left (Real.one_sub_inv_le_log_of_pos hr0) hc
  have h4 := mul_le_mul_of_nonneg_left (inv_le_one_of_one_le₀ hr1) he
  rw [hrec]
  linarith

/-- `𝖾_j ≤ (5/(6k²)) ρ(ρ+1)(ρ+2)`, `ρ = j - k`. -/
private theorem ecor_le_cubic {k j : ℕ} (hk : 2 ≤ k) (hj : k ≤ j) :
    ecor k j ≤ 5 / (6 * (k : ℝ) ^ 2)
        * (((j : ℝ) - k) * ((j : ℝ) - k + 1) * ((j : ℝ) - k + 2)) := by
  have hkne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  induction j, hj using Nat.le_induction with
  | base =>
    rw [ecor_base hk]
    simp
  | succ n hn ih =>
    have hnr : (k : ℝ) ≤ (n : ℝ) := by exact_mod_cast hn
    have hn1ne : (n : ℝ) + 1 ≠ 0 := by positivity
    have hs := ecor_succ_le hk hn
    have hl := log_xk_gam_le hk (i := n + 1) (by omega)
    rw [Nat.cast_add_one] at hl
    have h1 := mul_le_mul_of_nonneg_left hl (by linarith : (0 : ℝ) ≤ (n : ℝ) - k + 2)
    have key : 5 / (6 * (k : ℝ) ^ 2)
          * (((n : ℝ) + 1 - k) * ((n : ℝ) + 1 - k + 1) * ((n : ℝ) + 1 - k + 2))
        - (((n : ℝ) - k + 2) * (5 * ((n : ℝ) + 1 - k) / (2 * (k : ℝ) * ((n : ℝ) + 1)))
          + 5 / (6 * (k : ℝ) ^ 2) * (((n : ℝ) - k) * ((n : ℝ) - k + 1) * ((n : ℝ) - k + 2)))
        = 5 * ((n : ℝ) - k + 1) ^ 2 * ((n : ℝ) - k + 2)
          / (2 * (k : ℝ) ^ 2 * ((n : ℝ) + 1)) := by
      field
    have hpos : 0 ≤ 5 * ((n : ℝ) - k + 1) ^ 2 * ((n : ℝ) - k + 2)
        / (2 * (k : ℝ) ^ 2 * ((n : ℝ) + 1)) :=
      div_nonneg (mul_nonneg (mul_nonneg (by norm_num) (sq_nonneg _)) (by linarith))
        (by positivity)
    rw [Nat.cast_add_one]
    linarith

/-- (iii) `𝖤 ≤ Ē`: sum `𝖾_j/(j+1) ≤ 𝖾_j/k` with the cubic bound for `𝖾_j`. -/
private theorem ecorSum_le {k R : ℕ} (hk : 2 ≤ k) (hR : 2 ≤ R) : ecorSum k R ≤ Ebar k R := by
  have hk0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hkne : (k : ℝ) ≠ 0 := hk0.ne'
  have key : ∀ n, k ≤ n → ∑ j ∈ Icc k n, ecor k j / ((j : ℝ) + 1)
      ≤ 5 / (24 * (k : ℝ) ^ 3)
        * (((n : ℝ) - k) * ((n : ℝ) - k + 1) * ((n : ℝ) - k + 2) * ((n : ℝ) - k + 3)) := by
    intro n hn
    induction n, hn using Nat.le_induction with
    | base =>
      rw [Icc_self, sum_singleton, ecor_base hk]
      simp
    | succ m hm ih =>
      have hmr : (k : ℝ) ≤ (m : ℝ) := by exact_mod_cast hm
      have he0 : 0 ≤ ecor k (m + 1) := CrossCrit.ecor_nonneg hk (by omega)
      have he1 := ecor_le_cubic hk (j := m + 1) (by omega)
      rw [Nat.cast_add_one] at he1
      have h1 : ecor k (m + 1) / ((m : ℝ) + 1 + 1) ≤ ecor k (m + 1) / k :=
        div_le_div_of_nonneg_left he0 hk0 (by linarith)
      have h2 := div_le_div_of_nonneg_right he1 hk0.le
      have e : 5 / (24 * (k : ℝ) ^ 3)
            * (((m : ℝ) - k) * ((m : ℝ) - k + 1) * ((m : ℝ) - k + 2) * ((m : ℝ) - k + 3))
          + 5 / (6 * (k : ℝ) ^ 2)
            * (((m : ℝ) + 1 - k) * ((m : ℝ) + 1 - k + 1) * ((m : ℝ) + 1 - k + 2)) / k
          = 5 / (24 * (k : ℝ) ^ 3) * (((m : ℝ) + 1 - k) * ((m : ℝ) + 1 - k + 1)
            * ((m : ℝ) + 1 - k + 2) * ((m : ℝ) + 1 - k + 3)) := by
        field
      rw [sum_Icc_succ_top (by omega : k ≤ m + 1), Nat.cast_add_one]
      linarith
  have h := key (k + R - 2) (by omega)
  have hc : ((k + R - 2 : ℕ) : ℝ) = (k : ℝ) + (R : ℝ) - 2 := by
    rw [Nat.cast_sub (by omega : 2 ≤ k + R), Nat.cast_add]
    norm_num
  rw [hc] at h
  have e : 5 / (24 * (k : ℝ) ^ 3)
      * (((k : ℝ) + (R : ℝ) - 2 - k) * ((k : ℝ) + (R : ℝ) - 2 - k + 1)
        * ((k : ℝ) + (R : ℝ) - 2 - k + 2) * ((k : ℝ) + (R : ℝ) - 2 - k + 3))
      = 5 * ((R : ℝ) - 2) * ((R : ℝ) - 1) * R * ((R : ℝ) + 1) / (24 * (k : ℝ) ^ 3) := by
    field
  unfold ecorSum Ebar
  linarith

/-! ### (iv) `𝖾_{N-1} + Σ_ω`

The bounds `𝖾_{j+1} - 𝖾_j ≤ (j-k+2) log (x γ_{j+1})` and `ω_i ≤ 1/(i+1) + log (x γ_i)` are summed
against the comparison functions `H(n) = (n-k) - k log ((n+2)/(k+2))` and
`G(n) = (n-k)(n-k+1)/2 + (3/2-k)(n-k) + k(k-1) log ((n+1)/(k+1))`, which vanish at `n = k` and
whose increments dominate the summands; `H̄ = H(k+R-1)` and `Ḡ = G(k+R-1)`. -/

/-- `ω_i ≤ 1/(i+1) + log (x γ_i)` for `i ≥ k`. -/
private theorem omg_le {k i : ℕ} (hk : 2 ≤ k) (hi : k ≤ i) :
    omg k i ≤ 1 / ((i : ℝ) + 1) + Real.log (xk k * gam i) := by
  have hr1 : 1 ≤ xk k * gam i := CrossCrit.one_le_xk_mul_gam hk hi
  have hr0 : 0 < xk k * gam i := by linarith
  have alg : ∀ I r : ℝ, I + 1 ≠ 0 → r ≠ 0 →
      1 - I / ((I + 1) * r) = 1 / (I + 1) + I / (I + 1) * (1 - r⁻¹) := by
    intro I r hI hr
    field
  have e : omg k i = 1 / ((i : ℝ) + 1) + (i : ℝ) / ((i : ℝ) + 1) * (1 - (xk k * gam i)⁻¹) :=
    alg (i : ℝ) (xk k * gam i) (by positivity) hr0.ne'
  have hq0 : (0 : ℝ) ≤ (i : ℝ) / ((i : ℝ) + 1) := by positivity
  have hq1 : (i : ℝ) / ((i : ℝ) + 1) ≤ 1 := by
    rw [div_le_one (by positivity)]
    linarith
  have h1 := mul_le_mul_of_nonneg_left (Real.one_sub_inv_le_log_of_pos hr0) hq0
  have h2 := mul_le_mul_of_nonneg_right hq1 (Real.log_nonneg hr1)
  rw [e]
  linarith

/-- The comparison function for the terms `(ρ+1)/(k+ρ+1)`. -/
private noncomputable def HbarR (k n : ℝ) : ℝ :=
  (n - k) - k * (Real.log (n + 2) - Real.log (k + 2))

/-- The comparison function for the terms `ρ(ρ+1)/(k+ρ)`. -/
private noncomputable def GbarR (k n : ℝ) : ℝ :=
  (n - k) * (n - k + 1) / 2 + (3 / 2 - k) * (n - k)
    + k * (k - 1) * (Real.log (n + 1) - Real.log (k + 1))

private theorem HbarR_self (k : ℝ) : HbarR k k = 0 := by
  unfold HbarR
  ring

private theorem GbarR_self (k : ℝ) : GbarR k k = 0 := by
  unfold GbarR
  ring

/-- `(ρ+1)/(k+ρ+1) ≤ H(k+ρ) - H(k+ρ-1)` (`n + 1 = k + ρ`), from `log (1 + u) ≤ u`. -/
private theorem HbarR_step (k n : ℝ) (hk : 0 ≤ k) (hn : 0 ≤ n) :
    HbarR k n + (n + 1 - k + 1) / (n + 1 + 1) ≤ HbarR k (n + 1) := by
  have h1 : 0 < n + 2 := by linarith
  have h2 : 0 < n + 3 := by linarith
  have h1ne : n + 2 ≠ 0 := h1.ne'
  have h11ne : n + 1 + 1 ≠ 0 := by positivity
  have hlog : Real.log (n + 3) - Real.log (n + 2) ≤ 1 / (n + 2) := by
    rw [← Real.log_div h2.ne' h1.ne']
    have h := Real.log_le_sub_one_of_pos (div_pos h2 h1)
    have e : (n + 3) / (n + 2) - 1 = 1 / (n + 2) := by
      field
    linarith
  have h3 : k * (Real.log (n + 3) - Real.log (n + 2)) ≤ k * (1 / (n + 2)) :=
    mul_le_mul_of_nonneg_left hlog hk
  have e2 : (n + 1 - k + 1) / (n + 1 + 1) = 1 - k * (1 / (n + 2)) := by
    field
  have e3 : n + 1 + 2 = n + 3 := by ring
  unfold HbarR
  rw [e2, e3]
  linarith

/-- `ρ(ρ+1)/(k+ρ) ≤ G(k+ρ) - G(k+ρ-1)` (`n + 1 = k + ρ`), from `u - u²/2 ≤ log (1 + u)`. -/
private theorem GbarR_step (k n : ℝ) (hk : 1 ≤ k) (hn : k ≤ n) :
    GbarR k n + (n + 1 - k) * (n + 1 - k + 1) / (n + 1) ≤ GbarR k (n + 1) := by
  have h1 : 0 < n + 1 := by linarith
  have h2 : 0 < n + 2 := by linarith
  have h1ne : n + 1 ≠ 0 := h1.ne'
  have hlog : 1 / (n + 1) - (1 / (n + 1)) ^ 2 / 2
      ≤ Real.log (n + 2) - Real.log (n + 1) := by
    have h := log_one_add_ge2 (u := 1 / (n + 1)) (by positivity)
    have e : 1 + 1 / (n + 1) = (n + 2) / (n + 1) := by
      field
    rw [e, Real.log_div h2.ne' h1.ne'] at h
    exact h
  have h3 : k * (k - 1) * (1 / (n + 1) - (1 / (n + 1)) ^ 2 / 2)
      ≤ k * (k - 1) * (Real.log (n + 2) - Real.log (n + 1)) :=
    mul_le_mul_of_nonneg_left hlog (mul_nonneg (by linarith) (by linarith))
  have key : (n + 1 - k) + 3 / 2 - k + k * (k - 1) * (1 / (n + 1) - (1 / (n + 1)) ^ 2 / 2)
      - (n + 1 - k) * (n + 1 - k + 1) / (n + 1)
      = ((n + 1) ^ 2 - k * (k - 1)) / (2 * (n + 1) ^ 2) := by
    field
  have hpos : 0 ≤ ((n + 1) ^ 2 - k * (k - 1)) / (2 * (n + 1) ^ 2) := by
    refine div_nonneg ?_ (by positivity)
    nlinarith [mul_nonneg (by linarith : (0 : ℝ) ≤ n - k) (by linarith : (0 : ℝ) ≤ n + k)]
  have e3 : n + 1 + 1 = n + 2 := by ring
  unfold GbarR
  rw [e3]
  linarith

/-- `(i-k+1) log (x γ_i) ≤ (5/(2k)) (G(i) - G(i-1))` for `i = n + 1 > k`. -/
private theorem log_term_le {k n : ℕ} (hk : 2 ≤ k) (hn : k ≤ n) :
    ((n : ℝ) - k + 2) * Real.log (xk k * gam (n + 1))
      ≤ 5 / (2 * (k : ℝ)) * (GbarR (k : ℝ) ((n : ℝ) + 1) - GbarR (k : ℝ) (n : ℝ)) := by
  have hk1 : (1 : ℝ) ≤ (k : ℝ) := by exact_mod_cast (by omega : 1 ≤ k)
  have hnr : (k : ℝ) ≤ (n : ℝ) := by exact_mod_cast hn
  have hkne : (k : ℝ) ≠ 0 := by linarith
  have hn1ne : (n : ℝ) + 1 ≠ 0 := by positivity
  have hl := log_xk_gam_le hk (i := n + 1) (by omega)
  rw [Nat.cast_add_one] at hl
  have h1 := mul_le_mul_of_nonneg_left hl (by linarith : (0 : ℝ) ≤ (n : ℝ) - k + 2)
  have e1 : ((n : ℝ) - k + 2) * (5 * ((n : ℝ) + 1 - k) / (2 * (k : ℝ) * ((n : ℝ) + 1)))
      = 5 / (2 * (k : ℝ)) * (((n : ℝ) + 1 - k) * ((n : ℝ) + 1 - k + 1) / ((n : ℝ) + 1)) := by
    field
  have h2 := mul_le_mul_of_nonneg_left (GbarR_step (k : ℝ) (n : ℝ) hk1 hnr)
    (by positivity : (0 : ℝ) ≤ 5 / (2 * (k : ℝ)))
  linarith

/-- `𝖾_j ≤ (5/(2k)) G(j)`. -/
private theorem ecor_le_Gf {k j : ℕ} (hk : 2 ≤ k) (hj : k ≤ j) :
    ecor k j ≤ 5 / (2 * (k : ℝ)) * GbarR (k : ℝ) (j : ℝ) := by
  induction j, hj using Nat.le_induction with
  | base => simp [ecor_base hk, GbarR_self]
  | succ n hn ih =>
    have h1 := ecor_succ_le hk hn
    have h2 := log_term_le hk hn
    rw [Nat.cast_add_one]
    linarith

/-- `∑_{i=k+1}^{n} (i-k+1) ω_i ≤ H(n) + (5/(2k)) G(n)`. -/
private theorem Somg_sum_le {k n : ℕ} (hk : 2 ≤ k) (hn : k ≤ n) :
    ∑ i ∈ Icc (k + 1) n, ((i : ℝ) - k + 1) * omg k i
      ≤ HbarR (k : ℝ) (n : ℝ) + 5 / (2 * (k : ℝ)) * GbarR (k : ℝ) (n : ℝ) := by
  induction n, hn using Nat.le_induction with
  | base =>
    rw [Icc_eq_empty_of_lt (by omega : k < k + 1), sum_empty]
    simp [HbarR_self, GbarR_self]
  | succ m hm ih =>
    have hmr : (k : ℝ) ≤ (m : ℝ) := by exact_mod_cast hm
    have hω := omg_le hk (i := m + 1) (by omega)
    rw [Nat.cast_add_one] at hω
    have h1 := mul_le_mul_of_nonneg_left hω (by linarith : (0 : ℝ) ≤ (m : ℝ) + 1 - k + 1)
    have hG := log_term_le hk hm
    have hH := HbarR_step (k : ℝ) (m : ℝ) (Nat.cast_nonneg k) (Nat.cast_nonneg m)
    have e : ((m : ℝ) + 1 - k + 1) * (1 / ((m : ℝ) + 1 + 1))
        = ((m : ℝ) + 1 - k + 1) / ((m : ℝ) + 1 + 1) := by
      ring
    rw [sum_Icc_succ_top (by omega : k + 1 ≤ m + 1), Nat.cast_add_one]
    linarith

/-- (iv) `0 ≤ 𝖾_{N-1} + Σ_ω ≤ H̄ + (5/k) Ḡ`. -/
private theorem ecor_Somg_bounds {k R : ℕ} (hk : 2 ≤ k) (hR : 2 ≤ R) :
    0 ≤ ecor k (k + R - 1) + Somg k R
      ∧ ecor k (k + R - 1) + Somg k R ≤ Hbar k R + 5 / (k : ℝ) * Gbar k R := by
  have hk0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hR0 : (0 : ℝ) < (R : ℝ) := Nat.cast_pos.mpr (by omega)
  have hkn : k ≤ k + R - 1 := by omega
  have hc : ((k + R - 1 : ℕ) : ℝ) = (k : ℝ) + (R : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega : 1 ≤ k + R), Nat.cast_add, Nat.cast_one]
  have he0 : 0 ≤ ecor k (k + R - 1) := CrossCrit.ecor_nonneg hk hkn
  have hS0 : 0 ≤ Somg k R := CrossCrit.Somg_nonneg hk R
  have he1 := ecor_le_Gf hk hkn
  have hS1 : Somg k R
      ≤ HbarR (k : ℝ) ((k + R - 1 : ℕ) : ℝ)
        + 5 / (2 * (k : ℝ)) * GbarR (k : ℝ) ((k + R - 1 : ℕ) : ℝ) :=
    Somg_sum_le hk hkn
  have hH : HbarR (k : ℝ) ((k : ℝ) + (R : ℝ) - 1) = Hbar k R := by
    have e : (k : ℝ) + (R : ℝ) - 1 + 2 = (k : ℝ) + (R : ℝ) + 1 := by ring
    unfold HbarR Hbar
    rw [Real.log_div (by positivity) (by positivity), e]
    ring
  have hG : GbarR (k : ℝ) ((k : ℝ) + (R : ℝ) - 1) = Gbar k R := by
    have e : (k : ℝ) + (R : ℝ) - 1 + 1 = (k : ℝ) + (R : ℝ) := by ring
    unfold GbarR Gbar
    rw [Real.log_div (by positivity) (by positivity), e]
    ring
  rw [hc, hG] at he1
  rw [hc, hH, hG] at hS1
  have e5 : 5 / (2 * (k : ℝ)) * Gbar k R + 5 / (2 * (k : ℝ)) * Gbar k R
      = 5 / (k : ℝ) * Gbar k R := by
    ring
  constructor <;> linarith

/-! ### Sums of the masses `e^{-i} i^i/i!` -/

/-- `∑_{i<R} poissonMass i ≤ 1 + c₀ (2√(R-1) - 1)` for `R ≥ 2`. -/
private theorem sum_poissonMass_le {R : ℕ} (hR : 2 ≤ R) :
    ∑ i ∈ range R, poissonMass i ≤ 1 + c0 * (2 * Real.sqrt ((R : ℝ) - 1) - 1) := by
  obtain ⟨n, rfl⟩ : ∃ n, R = n + 1 := ⟨R - 1, by omega⟩
  have e : ((n + 1 : ℕ) : ℝ) - 1 = (n : ℝ) := by
    rw [Nat.cast_add_one]
    ring
  rw [sum_range_succ', poissonMass_zero, e]
  have h1 : ∑ i ∈ range n, poissonMass (i + 1)
      ≤ ∑ i ∈ range n, c0 * (1 / Real.sqrt ((i : ℝ) + 1)) := by
    refine sum_le_sum fun i _ => ?_
    have h := poissonMass_le_c0 (i := i + 1) (by omega)
    rw [Nat.cast_add_one] at h
    calc poissonMass (i + 1) ≤ c0 / Real.sqrt ((i : ℝ) + 1) := h
      _ = c0 * (1 / Real.sqrt ((i : ℝ) + 1)) := by ring
  rw [← mul_sum] at h1
  have h3 := mul_le_mul_of_nonneg_left (sum_range_inv_sqrt_le (n := n) (by omega)) c0_pos.le
  linarith

/-- `i poissonMass i ≤ c₀ √i`. -/
private theorem mul_poissonMass_le (i : ℕ) : (i : ℝ) * poissonMass i ≤ c0 * Real.sqrt (i : ℝ) := by
  rcases Nat.eq_zero_or_pos i with rfl | hi
  · simp
  · have hi0 : (0 : ℝ) < i := by exact_mod_cast hi
    have h1 := mul_le_mul_of_nonneg_left (poissonMass_le_c0 (i := i) hi) hi0.le
    have e : (i : ℝ) * (c0 / Real.sqrt (i : ℝ)) = c0 * ((i : ℝ) / Real.sqrt (i : ℝ)) := by ring
    rw [e, Real.div_sqrt] at h1
    exact h1

/-- `∑_{i<R} i poissonMass i ≤ c₀ (2/3) R√R`. -/
private theorem sum_mul_poissonMass_le (R : ℕ) :
    ∑ i ∈ range R, (i : ℝ) * poissonMass i ≤ c0 * (2 / 3 * ((R : ℝ) * Real.sqrt (R : ℝ))) := by
  have h1 : ∑ i ∈ range R, (i : ℝ) * poissonMass i ≤ ∑ i ∈ range R, c0 * Real.sqrt (i : ℝ) :=
    sum_le_sum (fun i _ => mul_poissonMass_le i)
  rw [← mul_sum] at h1
  exact h1.trans (mul_le_mul_of_nonneg_left (sum_range_sqrt_le R) c0_pos.le)

/-- `∑_{i<R} i² poissonMass i ≤ c₀ (2/5) R²√R`. -/
private theorem sum_sq_mul_poissonMass_le (R : ℕ) :
    ∑ i ∈ range R, (i : ℝ) ^ 2 * poissonMass i
      ≤ c0 * (2 / 5 * ((R : ℝ) ^ 2 * Real.sqrt (R : ℝ))) := by
  have h1 : ∑ i ∈ range R, (i : ℝ) ^ 2 * poissonMass i
      ≤ ∑ i ∈ range R, c0 * ((i : ℝ) * Real.sqrt (i : ℝ)) := by
    refine sum_le_sum fun i _ => ?_
    have h := mul_le_mul_of_nonneg_left (mul_poissonMass_le i)
        (Nat.cast_nonneg i : (0 : ℝ) ≤ (i : ℝ))
    linarith
  rw [← mul_sum] at h1
  exact h1.trans (mul_le_mul_of_nonneg_left (sum_range_sqrt_cube_le R) c0_pos.le)

/-- `∑_{i<R} poissonMass i ≥ 1 + c₀ (2√R - 2 - 1/4)` for `R ≥ 1`. -/
private theorem sum_poissonMass_ge {R : ℕ} (hR : 1 ≤ R) :
    1 + c0 * (2 * Real.sqrt (R : ℝ) - 2 - 1 / 4) ≤ ∑ i ∈ range R, poissonMass i := by
  obtain ⟨n, rfl⟩ : ∃ n, R = n + 1 := ⟨R - 1, by omega⟩
  rw [sum_range_succ', poissonMass_zero, Nat.cast_add_one]
  have h1 : ∑ i ∈ range n, c0 * (1 / Real.sqrt ((i : ℝ) + 1)
        - 1 / 12 * (1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1))))
      ≤ ∑ i ∈ range n, poissonMass (i + 1) := by
    refine sum_le_sum fun i _ => ?_
    have h := poissonMass_ge_c0 (i := i + 1) (by omega)
    rw [Nat.cast_add_one] at h
    have hs : Real.sqrt ((i : ℝ) + 1) ≠ 0 := (Real.sqrt_pos.2 (by positivity)).ne'
    calc c0 * (1 / Real.sqrt ((i : ℝ) + 1)
          - 1 / 12 * (1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1))))
        = c0 * (1 - 1 / (12 * ((i : ℝ) + 1))) / Real.sqrt ((i : ℝ) + 1) := by field
      _ ≤ poissonMass (i + 1) := h
  rw [← mul_sum, sum_sub_distrib, ← mul_sum] at h1
  have h2 := sum_range_inv_sqrt_ge n
  have h3 := sum_range_inv_sqrt_cube_le n
  have h4 : c0 * (2 * Real.sqrt ((n : ℝ) + 1) - 2 - 1 / 4)
      ≤ c0 * (∑ i ∈ range n, 1 / Real.sqrt ((i : ℝ) + 1)
          - 1 / 12 * ∑ i ∈ range n, 1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1))) :=
    mul_le_mul_of_nonneg_left (by linarith) c0_pos.le
  linarith

/-! ### The tilt in exponential form: `x = e^{a-1}`, `a = 1 + log x` -/

private theorem xk_eq (k : ℕ) : xk k = Real.exp (1 + Real.log (xk k)) * Real.exp (-1) := by
  rw [← Real.exp_add]
  have h : 1 + Real.log (xk k) + -1 = Real.log (xk k) := by ring
  rw [h, Real.exp_log (CrossCrit.xk_pos k)]

/-- `(i x)^i / i! = poissonMass(i) e^{a i}`. -/
private theorem term_xk (k i : ℕ) :
    ((i : ℝ) * xk k) ^ i / (i.factorial : ℝ)
      = poissonMass i * Real.exp ((1 + Real.log (xk k)) * i) := by
  have h1 : Real.exp ((1 + Real.log (xk k)) * i) = Real.exp (1 + Real.log (xk k)) ^ i := by
    rw [mul_comm _ (i : ℝ), Real.exp_nat_mul]
  have h2 : (i : ℝ) * xk k = (i : ℝ) / Real.exp 1 * Real.exp (1 + Real.log (xk k)) := by
    nth_rewrite 1 [xk_eq k]
    rw [Real.exp_neg]
    ring
  rw [poissonMass_eq, h1, h2, mul_pow]
  ring

/-- `κ_m = e^{a m} · e^{-m} ε_m`. -/
private theorem kapx_eq (k m : ℕ) :
    kapx k m = Real.exp ((1 + Real.log (xk k)) * m) * (Real.exp (-(m : ℝ)) * eps m) := by
  have h1 : Real.exp ((1 + Real.log (xk k)) * m) = Real.exp (1 + Real.log (xk k)) ^ m := by
    rw [mul_comm _ (m : ℝ), Real.exp_nat_mul]
  have h2 : Real.exp (-(m : ℝ)) = Real.exp (-1) ^ m := by
    rw [← Real.exp_nat_mul]
    congr 1
    ring
  unfold kapx
  nth_rewrite 1 [xk_eq k]
  rw [h1, h2, mul_pow]
  ring

/-- `e^{-(i+1)} ε_{i+1} = e^{-1} poissonMass(i)/(i+1)`. -/
private theorem w_succ (i : ℕ) :
    Real.exp (-((i + 1 : ℕ) : ℝ)) * eps (i + 1) = Real.exp (-1) * poissonMass i
        / ((i : ℝ) + 1) := by
  have h1 : ((i : ℝ) + 1) ≠ 0 := by positivity
  have h2 : Real.exp (-((i + 1 : ℕ) : ℝ)) = Real.exp (-1) * Real.exp (-(i : ℝ)) := by
    rw [← Real.exp_add]
    congr 1
    rw [Nat.cast_add_one]
    ring
  have h3 := mul_eps i
  rw [h2, eq_div_iff h1]
  unfold poissonMass
  rw [← h3]
  ring

/-- `∑_{i ≥ 0} e^{-1} poissonMass(i)/(i+1) = 1 - e^{-1}` (the kernel masses at tilt `e^{-1}`). -/
private theorem hasSum_v :
    HasSum (fun i : ℕ => Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)) (1 - Real.exp (-1)) := by
  have e0 : eps 0 = 0 := by simp [eps]
  have h1 : HasSum (fun i : ℕ => Real.exp (-((i + 1 : ℕ) : ℝ)) * eps (i + 1))
      (1 - Real.exp (-1)) := by
    refine (hasSum_nat_add_iff (f := fun m : ℕ => Real.exp (-(m : ℝ)) * eps m) 1).mpr ?_
    simpa [e0] using hasSum_eps
  have h2 : (fun i : ℕ => Real.exp (-1) * poissonMass i / ((i : ℝ) + 1))
      = fun i : ℕ => Real.exp (-((i + 1 : ℕ) : ℝ)) * eps (i + 1) := by
    funext i
    exact (w_succ i).symm
  rw [h2]
  exact h1

/-- The kernel deficit in terms of `a = 1 + log x`:
`κ̄_R = 1 - e^{a} e^{-1} - ∑_{i<R} e^{a(i+1)} · e^{-1} poissonMass(i)/(i+1)`. -/
private theorem kbar_eq (k R : ℕ) :
    kbar k R = 1 - Real.exp (1 + Real.log (xk k)) * Real.exp (-1)
      - ∑ i ∈ range R, Real.exp ((1 + Real.log (xk k)) * ((i : ℝ) + 1))
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)) := by
  have h1 : ∑ m ∈ Icc 1 R, kapx k m
      = ∑ i ∈ range R, Real.exp ((1 + Real.log (xk k)) * ((i : ℝ) + 1))
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)) := by
    have h := sum_Icc_eq_range (fun m => kapx k m) 0 R
    simp only [zero_add] at h
    rw [h]
    refine sum_congr rfl fun i _ => ?_
    rw [kapx_eq, w_succ, Nat.cast_add_one]
  unfold kbar
  rw [h1, ← xk_eq k]

/-- For `0 ≤ y ≤ R` and `ā R ≤ 0.6679`: `e^{a y} ≤ 1 + ā y + q (ā y)²`, since `a ≤ ā`. -/
private theorem exp_tilt_le {k R : ℕ} (hk : 2 ≤ k) (hs : abar k * R ≤ 6679 / 10000) {y : ℝ}
    (hy0 : 0 ≤ y) (hy : y ≤ R) :
    Real.exp ((1 + Real.log (xk k)) * y) ≤ 1 + abar k * y + 633 / 1000 * (abar k * y) ^ 2 := by
  have ha0 := abar_pos hk
  have h1 : (1 + Real.log (xk k)) * y ≤ abar k * y :=
    mul_le_mul_of_nonneg_right (xk_log_bounds hk).2 hy0
  exact (Real.exp_le_exp.mpr h1).trans
    (exp_le_quad (mul_nonneg ha0.le hy0) ((mul_le_mul_of_nonneg_left hy ha0.le).trans hs))

/-! ### (ii) the sum `S_R` -/

/-- (ii) `S_R ≤ S̄` when `ā R ≤ 0.6679`: termwise,
`(i x)^i/i! = poissonMass(i) e^{a i} ≤ poissonMass(i) (1 + ā i + q ā² i²)`. -/
private theorem SR_le {k R : ℕ} (hk : 2 ≤ k) (hR : 2 ≤ R) (hs : abar k * R ≤ 6679 / 10000) :
    SR k R ≤ Sbar k R := by
  have ha0 := abar_pos hk
  have hterm : ∀ i ∈ range R, ((i : ℝ) * xk k) ^ i / (i.factorial : ℝ)
      ≤ poissonMass i + abar k * ((i : ℝ) * poissonMass i)
        + 633 / 1000 * abar k ^ 2 * ((i : ℝ) ^ 2 * poissonMass i) := by
    intro i hi
    have hiR : (i : ℝ) ≤ R := by exact_mod_cast (mem_range.mp hi).le
    have h := mul_le_mul_of_nonneg_left (exp_tilt_le hk hs (Nat.cast_nonneg i) hiR)
      (poissonMass_pos i).le
    rw [term_xk]
    linarith
  have hsum := sum_le_sum hterm
  rw [sum_add_distrib, sum_add_distrib, ← mul_sum, ← mul_sum] at hsum
  have hS0 := sum_poissonMass_le hR
  have hS1 := mul_le_mul_of_nonneg_left (sum_mul_poissonMass_le R) ha0.le
  have hS2 := mul_le_mul_of_nonneg_left (sum_sq_mul_poissonMass_le R)
    (mul_nonneg (by norm_num : (0 : ℝ) ≤ 633 / 1000) (sq_nonneg (abar k)))
  unfold SR Sbar
  linarith

/-! ### (v) the kernel deficit `κ̄_R`

Write `v_i = e^{-1} poissonMass(i)/(i+1) = e^{-(i+1)} ε_{i+1}`, so that `∑_{i ≥ 0} v_i = 1 - e^{-1}`
and `κ̄_R = Tail_R - e^{-1}(e^{a} - 1) - ∑_{i<R} (e^{a(i+1)} - 1) v_i`, `Tail_R = ∑_{i ≥ R} v_i`. -/

/-- For `i ≥ 2`: `v_i ≤ e^{-1} c₀ · 2(1/√(i-1) - 1/√i)`. -/
private theorem v_le {i : ℕ} (hi : 2 ≤ i) :
    Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
      ≤ Real.exp (-1) * c0 * (2 * (1 / Real.sqrt ((i : ℝ) - 1) - 1 / Real.sqrt (i : ℝ))) := by
  have hi2 : (2 : ℝ) ≤ i := by exact_mod_cast hi
  have hi0 : (0 : ℝ) < i := by linarith
  have h2 : poissonMass i / ((i : ℝ) + 1) ≤ poissonMass i / (i : ℝ) :=
    div_le_div_of_nonneg_left (poissonMass_pos i).le hi0 (by linarith)
  have h3 : poissonMass i / (i : ℝ) ≤ c0 / Real.sqrt (i : ℝ) / (i : ℝ) :=
    div_le_div_of_nonneg_right (poissonMass_le_c0 (by omega)) hi0.le
  have h4 := (inv_sqrt_diff_bounds (y := (i : ℝ) - 1) (by linarith)).1
  rw [sub_add_cancel] at h4
  have h5 := mul_le_mul_of_nonneg_left h4 c0_pos.le
  have e : c0 / Real.sqrt (i : ℝ) / (i : ℝ) = c0 * (1 / ((i : ℝ) * Real.sqrt (i : ℝ))) := by
    ring
  rw [e] at h3
  calc Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
      = Real.exp (-1) * (poissonMass i / ((i : ℝ) + 1)) := mul_div_assoc _ _ _
    _ ≤ Real.exp (-1) * (c0 * (2 * (1 / Real.sqrt ((i : ℝ) - 1) - 1 / Real.sqrt (i : ℝ)))) :=
        mul_le_mul_of_nonneg_left (h2.trans (h3.trans h5)) (Real.exp_pos _).le
    _ = Real.exp (-1) * c0 * (2 * (1 / Real.sqrt ((i : ℝ) - 1) - 1 / Real.sqrt (i : ℝ))) := by
        ring

/-- For `i ≥ R ≥ 1`:
`e^{-1} c₀ (1 - 1/(12R)) · 2(1/√(i+1) - 1/√(i+2)) ≤ v_i`. -/
private theorem v_ge {R i : ℕ} (hR : 1 ≤ R) (hi : R ≤ i) :
    Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
        * (2 * (1 / Real.sqrt ((i : ℝ) + 1) - 1 / Real.sqrt ((i : ℝ) + 1 + 1)))
      ≤ Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) := by
  have hR1 : (1 : ℝ) ≤ R := by exact_mod_cast hR
  have hRi : (R : ℝ) ≤ i := by exact_mod_cast hi
  have hi0 : (0 : ℝ) < i := by linarith
  have hi1 : (0 : ℝ) < (i : ℝ) + 1 := by linarith
  have hρ0 : 0 ≤ 1 - 1 / (12 * (R : ℝ)) := by
    have h : 1 / (12 * (R : ℝ)) ≤ 1 := by
      rw [div_le_one (by linarith)]
      linarith
    linarith
  have hρ : 1 - 1 / (12 * (R : ℝ)) ≤ 1 - 1 / (12 * (i : ℝ)) := by
    have h : 1 / (12 * (i : ℝ)) ≤ 1 / (12 * (R : ℝ)) :=
      one_div_le_one_div_of_le (by linarith) (by linarith)
    linarith
  have hs : 0 < Real.sqrt (i : ℝ) := Real.sqrt_pos.2 hi0
  have hs1 : 0 < Real.sqrt ((i : ℝ) + 1) := Real.sqrt_pos.2 hi1
  have hss : Real.sqrt (i : ℝ) ≤ Real.sqrt ((i : ℝ) + 1) := Real.sqrt_le_sqrt (by linarith)
  have hcρ : 0 ≤ c0 * (1 - 1 / (12 * (R : ℝ))) := mul_nonneg c0_pos.le hρ0
  have h2 : c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((i : ℝ) + 1) ≤ poissonMass i :=
    calc c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((i : ℝ) + 1)
        ≤ c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt (i : ℝ) :=
          div_le_div_of_nonneg_left hcρ hs hss
      _ ≤ c0 * (1 - 1 / (12 * (i : ℝ))) / Real.sqrt (i : ℝ) :=
          div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left hρ c0_pos.le) hs.le
      _ ≤ poissonMass i := poissonMass_ge_c0 (by omega)
  have h3 : c0 * (1 - 1 / (12 * (R : ℝ)))
        * (1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1)))
      ≤ poissonMass i / ((i : ℝ) + 1) := by
    have e : c0 * (1 - 1 / (12 * (R : ℝ))) * (1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1)))
        = c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((i : ℝ) + 1) / ((i : ℝ) + 1) := by
      have hs1' := hs1.ne'
      have hi1' := hi1.ne'
      field
    rw [e]
    exact div_le_div_of_nonneg_right h2 hi1.le
  have h5 := mul_le_mul_of_nonneg_left (inv_sqrt_diff_bounds hi1).2 hcρ
  calc Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
        * (2 * (1 / Real.sqrt ((i : ℝ) + 1) - 1 / Real.sqrt ((i : ℝ) + 1 + 1)))
      = Real.exp (-1) * (c0 * (1 - 1 / (12 * (R : ℝ)))
          * (2 * (1 / Real.sqrt ((i : ℝ) + 1) - 1 / Real.sqrt ((i : ℝ) + 1 + 1)))) := by
        ring
    _ ≤ Real.exp (-1) * (poissonMass i / ((i : ℝ) + 1)) :=
        mul_le_mul_of_nonneg_left (h5.trans h3) (Real.exp_pos _).le
    _ = Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) := (mul_div_assoc _ _ _).symm

/-- `Tail_R ≤ 2 e^{-1} c₀/√(R-1)` for `R ≥ 2`: telescope `v_le` and let the number of terms tend
to infinity. -/
private theorem tail_le {R : ℕ} (hR : 2 ≤ R) :
    (1 - Real.exp (-1)) - ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
      ≤ 2 * Real.exp (-1) * c0 / Real.sqrt ((R : ℝ) - 1) := by
  have hc0 := c0_pos
  have hpart : ∀ N, R ≤ N → ∑ i ∈ range N, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
      ≤ ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
        + Real.exp (-1) * c0
          * (2 * (1 / Real.sqrt ((R : ℝ) - 1) - 1 / Real.sqrt ((N : ℝ) - 1))) := by
    intro N hN
    induction N, hN using Nat.le_induction with
    | base => exact le_of_eq (by ring)
    | succ n hn ih =>
      have h := v_le (i := n) (by omega)
      have e : ((n + 1 : ℕ) : ℝ) - 1 = (n : ℝ) := by
        rw [Nat.cast_add_one]
        ring
      rw [sum_range_succ, e]
      linarith
  have key : 1 - Real.exp (-1) ≤ ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
      + Real.exp (-1) * c0 * (2 * (1 / Real.sqrt ((R : ℝ) - 1))) := by
    refine le_of_tendsto hasSum_v.tendsto_sum_nat (Filter.eventually_atTop.2 ⟨R, fun N hN => ?_⟩)
    have h := hpart N hN
    have h0 : 0 ≤ Real.exp (-1) * c0 * (2 * (1 / Real.sqrt ((N : ℝ) - 1))) := by positivity
    linarith
  have e : 2 * Real.exp (-1) * c0 / Real.sqrt ((R : ℝ) - 1)
      = Real.exp (-1) * c0 * (2 * (1 / Real.sqrt ((R : ℝ) - 1))) := by ring
  rw [e]
  linarith

/-- `Tail_R ≥ 2 e^{-1} c₀ (1 - 1/(12R))/√(R+1)` for `R ≥ 1`: telescope `v_ge` and let the number
of terms tend to infinity. -/
private theorem tail_ge {R : ℕ} (hR : 1 ≤ R) :
    2 * Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((R : ℝ) + 1)
      ≤ (1 - Real.exp (-1)) - ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) := by
  have hpart : ∀ N, R ≤ N → ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
        + Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
          * (2 * (1 / Real.sqrt ((R : ℝ) + 1) - 1 / Real.sqrt ((N : ℝ) + 1)))
      ≤ ∑ i ∈ range N, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) := by
    intro N hN
    induction N, hN using Nat.le_induction with
    | base => exact le_of_eq (by ring)
    | succ n hn ih =>
      have h := v_ge hR hn
      rw [sum_range_succ, Nat.cast_add_one]
      linarith
  have hv : ∀ i : ℕ, 0 ≤ Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) := fun i =>
    div_nonneg (mul_nonneg (Real.exp_pos _).le (poissonMass_pos i).le) (by positivity)
  -- `1/√(N+1) → 0`
  have hlim0 : Filter.Tendsto (fun N : ℕ => 1 / Real.sqrt ((N : ℝ) + 1)) Filter.atTop
      (nhds 0) := by
    have h := tendsto_inv_atTop_zero.comp (Real.tendsto_sqrt_atTop.comp
      (Filter.tendsto_atTop_add_const_right _ 1 (tendsto_natCast_atTop_atTop (R := ℝ))))
    refine h.congr fun N => ?_
    simp [one_div]
  have hlim : Filter.Tendsto
      (fun N : ℕ => Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
        * (2 * (1 / Real.sqrt ((N : ℝ) + 1))))
      Filter.atTop (nhds (Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))) * (2 * 0))) :=
    (hlim0.const_mul 2).const_mul (Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))))
  have key : ∑ i ∈ range R, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
        + Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
          * (2 * (1 / Real.sqrt ((R : ℝ) + 1)))
        - (1 - Real.exp (-1))
      ≤ Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))) * (2 * 0) := by
    refine ge_of_tendsto hlim (Filter.eventually_atTop.2 ⟨R, fun N hN => ?_⟩)
    have h := hpart N hN
    have h2 : ∑ i ∈ range N, Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) ≤ 1 - Real.exp (-1) :=
      sum_le_hasSum (range N) (fun i _ => hv i) hasSum_v
    linarith
  have e : 2 * Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ))) / Real.sqrt ((R : ℝ) + 1)
      = Real.exp (-1) * c0 * (1 - 1 / (12 * (R : ℝ)))
        * (2 * (1 / Real.sqrt ((R : ℝ) + 1))) := by ring
  rw [e]
  linarith

/-- (v), lower bound `t̲ ≤ κ̄_R`: use `Tail_R ≥ …`, `e^{a} - 1 ≤ a e^{a} ≤ ā e^{ā}` and
`(e^{a(i+1)} - 1) v_i ≤ e^{-1} (ā + q ā² (i+1)) poissonMass(i)`. -/
private theorem tlow_le_kbar {k R : ℕ} (hk : 2 ≤ k) (hR : 2 ≤ R) (hs : abar k * R ≤ 6679 / 10000) :
    tlow k R ≤ kbar k R := by
  obtain ⟨hlo, hhi⟩ := xk_log_bounds hk
  have hab0 := abar_pos hk
  have hE : 0 < Real.exp (-1) := Real.exp_pos _
  have hT := tail_ge (R := R) (by omega)
  have h1 : Real.exp (1 + Real.log (xk k)) - 1 ≤ abar k * Real.exp (abar k) := by
    have hpos := Real.exp_pos (1 + Real.log (xk k))
    have h2 : Real.exp (1 + Real.log (xk k)) * Real.exp (-(1 + Real.log (xk k))) = 1 := by
      rw [← Real.exp_add, add_neg_cancel, Real.exp_zero]
    have h3 := mul_le_mul_of_nonneg_left (Real.one_sub_le_exp_neg (1 + Real.log (xk k))) hpos.le
    have h5 : (1 + Real.log (xk k)) * Real.exp (1 + Real.log (xk k))
        ≤ abar k * Real.exp (abar k) :=
      mul_le_mul hhi (Real.exp_le_exp.2 hhi) hpos.le hab0.le
    linarith
  have hterm : ∀ i ∈ range R,
      Real.exp ((1 + Real.log (xk k)) * ((i : ℝ) + 1))
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1))
        ≤ Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) + Real.exp (-1) * abar k * poissonMass i
          + Real.exp (-1) * (633 / 1000) * abar k ^ 2 * (((i : ℝ) + 1) * poissonMass i) := by
    intro i hi
    have hiR : (i : ℝ) + 1 ≤ R := by exact_mod_cast Nat.succ_le_of_lt (mem_range.mp hi)
    have hi1 : (0 : ℝ) < (i : ℝ) + 1 := by positivity
    have hnn : 0 ≤ Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) :=
      div_nonneg (mul_nonneg hE.le (poissonMass_pos i).le) hi1.le
    have h := mul_le_mul_of_nonneg_right (exp_tilt_le hk hs hi1.le hiR) hnn
    have e : (1 + abar k * ((i : ℝ) + 1) + 633 / 1000 * (abar k * ((i : ℝ) + 1)) ^ 2)
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1))
        = Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) + Real.exp (-1) * abar k * poissonMass i
          + Real.exp (-1) * (633 / 1000) * abar k ^ 2 * (((i : ℝ) + 1) * poissonMass i) := by
      field
    rw [e] at h
    exact h
  have hsum := sum_le_sum hterm
  rw [sum_add_distrib, sum_add_distrib, ← mul_sum, ← mul_sum] at hsum
  have hS1 := sum_poissonMass_le hR
  have hS2 : ∑ i ∈ range R, ((i : ℝ) + 1) * poissonMass i
      ≤ 1 + c0 * (2 / 3 * ((R : ℝ) * Real.sqrt R) + 2 * Real.sqrt ((R : ℝ) - 1) - 1) := by
    have h := sum_mul_poissonMass_le R
    have e : ∑ i ∈ range R, ((i : ℝ) + 1) * poissonMass i
        = ∑ i ∈ range R, (i : ℝ) * poissonMass i + ∑ i ∈ range R, poissonMass i := by
      rw [← sum_add_distrib]
      refine sum_congr rfl fun i _ => ?_
      ring
    rw [e]
    linarith
  have hA := mul_le_mul_of_nonneg_left h1 hE.le
  have hB := mul_le_mul_of_nonneg_left hS1 (mul_nonneg hE.le hab0.le)
  have hC := mul_le_mul_of_nonneg_left hS2
    (mul_nonneg (mul_nonneg hE.le (by norm_num : (0 : ℝ) ≤ 633 / 1000)) (sq_nonneg (abar k)))
  rw [kbar_eq]
  unfold tlow
  linarith

/-- (v), upper bound `κ̄_R ≤ t̄`: use `Tail_R ≤ …`, `e^{a} - 1 ≥ a` and
`(e^{a(i+1)} - 1) v_i ≥ e^{-1} a poissonMass(i)`, with `a ≥ a̲ ≥ 0`. -/
private theorem kbar_le_tup {k R : ℕ} (hk : 2 ≤ k) (hR : 2 ≤ R) : kbar k R ≤ tup k R := by
  obtain ⟨hlo, -⟩ := xk_log_bounds hk
  have hal := alow_nonneg hk
  have hE : 0 < Real.exp (-1) := Real.exp_pos _
  have hT := tail_le hR
  have h1 := Real.add_one_le_exp (1 + Real.log (xk k))
  have hterm : ∀ i ∈ range R,
      Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) + Real.exp (-1) * (1 + Real.log (xk k))
          * poissonMass i
        ≤ Real.exp ((1 + Real.log (xk k)) * ((i : ℝ) + 1))
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)) := by
    intro i _
    have hi1 : (i : ℝ) + 1 ≠ 0 := by positivity
    have hnn : 0 ≤ Real.exp (-1) * poissonMass i / ((i : ℝ) + 1) :=
      div_nonneg (mul_nonneg hE.le (poissonMass_pos i).le) (by positivity)
    have h := mul_le_mul_of_nonneg_right
      (Real.add_one_le_exp ((1 + Real.log (xk k)) * ((i : ℝ) + 1))) hnn
    have e : ((1 + Real.log (xk k)) * ((i : ℝ) + 1) + 1)
          * (Real.exp (-1) * poissonMass i / ((i : ℝ) + 1))
        = Real.exp (-1) * poissonMass i / ((i : ℝ) + 1)
          + Real.exp (-1) * (1 + Real.log (xk k)) * poissonMass i := by
      field
    rw [e] at h
    exact h
  have hsum := sum_le_sum hterm
  rw [sum_add_distrib, ← mul_sum] at hsum
  have hS := sum_poissonMass_ge (R := R) (by omega)
  have hSnn : 0 ≤ ∑ i ∈ range R, poissonMass i := sum_nonneg (fun i _ => (poissonMass_pos i).le)
  have hA : Real.exp (-1) * alow k * (1 + ∑ i ∈ range R, poissonMass i)
      ≤ Real.exp (-1) * (1 + Real.log (xk k)) * (1 + ∑ i ∈ range R, poissonMass i) :=
    mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hlo hE.le) (by linarith)
  have hB : Real.exp (-1) * alow k * (2 + c0 * (2 * Real.sqrt R - 2 - 1 / 4))
      ≤ Real.exp (-1) * alow k * (1 + ∑ i ∈ range R, poissonMass i) :=
    mul_le_mul_of_nonneg_left (by linarith) (mul_nonneg hE.le hal)
  have hC := mul_le_mul_of_nonneg_left h1 hE.le
  rw [kbar_eq]
  unfold tup
  linarith

/-! ### The criterion in terms of the explicit bounds -/

/-- If `ā R ≤ 0.6679`, `t̲ ≥ 0` and
`(t̄ + e^{-1} e^{ā} (R+1)/N) (H̄ + (5/k) Ḡ) < e^{-1} (R(R+1)/N - 1 - S̄ - Ē)`, `N = k + R`, then
`d_{j,k} > 0` for some `k < j ≤ N`: by (i)–(v) the two sides of the crossing criterion are
bounded by the two sides of this inequality. -/
theorem cross_of_bounds {k R : ℕ} (hk : 2 ≤ k) (hR1 : 2 ≤ R) (hR2 : R ≤ k - 1)
    (hs : abar k * R ≤ 6679 / 10000) (ht : 0 ≤ tlow k R)
    (h : (tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
          * (Hbar k R + 5 / (k : ℝ) * Gbar k R)
        < Real.exp (-1) * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R)) :
    ∃ j, k < j ∧ j ≤ k + R ∧ 0 < dq k j := by
  obtain ⟨hx1, hx2⟩ := xk_bounds hk
  have hS := SR_le hk hR1 hs
  have hE1 := ecorSum_le hk hR1
  obtain ⟨hB0, hB1⟩ := ecor_Somg_bounds hk hR1
  have hκ1 := tlow_le_kbar hk hR1 hs
  have hκ2 := kbar_le_tup hk hR1
  have hκ0 : 0 ≤ kbar k R := le_trans ht hκ1
  have hk0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hR0 : (0 : ℝ) < (R : ℝ) := Nat.cast_pos.mpr (by omega)
  have hN : (0 : ℝ) < (k : ℝ) + R := by linarith
  have hR' : (0 : ℝ) ≤ (R : ℝ) + 1 := by linarith
  have hxpos : 0 < xk k := CrossCrit.xk_pos k
  have hA0 : 0 ≤ xk k * ((R : ℝ) + 1) / ((k : ℝ) + R) :=
    div_nonneg (mul_nonneg hxpos.le hR') hN.le
  have hA1 : xk k * ((R : ℝ) + 1) / ((k : ℝ) + R)
      ≤ Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R) :=
    div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_right hx2 hR') hN.le
  -- the right side of the criterion is at most the left side of the hypothesis
  have hAB : (kbar k R + xk k * ((R : ℝ) + 1) / ((k : ℝ) + R))
        * (ecor k (k + R - 1) + Somg k R)
      ≤ (tup k R + Real.exp (-1) * Real.exp (abar k) * ((R : ℝ) + 1) / ((k : ℝ) + R))
        * (Hbar k R + 5 / (k : ℝ) * Gbar k R) :=
    mul_le_mul (by linarith) hB1 hB0 (by linarith)
  have hAB0 : 0 ≤ (kbar k R + xk k * ((R : ℝ) + 1) / ((k : ℝ) + R))
        * (ecor k (k + R - 1) + Somg k R) :=
    mul_nonneg (by linarith) hB0
  -- hence the bracket on the right of the hypothesis is positive
  have hC : 0 < (R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R :=
    pos_of_mul_pos_right (lt_of_le_of_lt (le_trans hAB0 hAB) h) (Real.exp_pos _).le
  -- the right side of the hypothesis is at most the left side of the criterion
  have h1 : Real.exp (-1) * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R)
      ≤ xk k * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R) :=
    mul_le_mul_of_nonneg_right hx1 hC.le
  have h2 : xk k * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - Sbar k R - Ebar k R)
      ≤ xk k * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - SR k R - ecorSum k R) :=
    mul_le_mul_of_nonneg_left (by linarith) hxpos.le
  exact cross_criterion hk (by omega) hR2 hκ0
    (lt_of_le_of_lt hAB (lt_of_lt_of_le h (le_trans h1 h2)))

end Parking
