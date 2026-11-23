import Parking.Basic.RealBounds
import Parking.NextColumn.Curvature
import Parking.NextColumn.FirstCell
import Parking.NextColumn.Raise

/-!
# The criterion

At a first-layer position `(n,k)`, `n = k + r`, `2 ≤ r ≤ k-1`: if `𝖦(r,k) ≥ 0` then
`d_{n,k} ≤ 0 ⟹ d_{n,k+1} < 0` (`step_neg_of_Gfun`).

By `dq_frozen` the two steps are "curvature minus boundary", `d_{n,k}/n! = C_- - B_-` and
`d_{n,k+1}/n! = C_+ - B_+`.  The curvatures are compared by `curv_ratio`, the boundary terms by
`Lam_shorten` and `Lam_raise`, and the means occurring there are bounded below by `mu0_le_muh`.
What remains is an inequality between real numbers (`crit_scalar_log`), which follows from
`𝖦(r,k) ≥ 0` and the Taylor bounds for `log (1 + x)`.
-/

namespace Parking

open Finset

/-! ### The scalar inequality -/

/-- The scalar inequality in logarithmic form, for real parameters. `m1`, `m2` are lower bounds
for the two means `μm`, `μmid`; the hypothesis `hG` is `0 ≤ 𝖦`. -/
private theorem crit_scalar_log {k r D μm μmid m1 m2 : ℝ} (hk : 3 ≤ k) (hr : 1 ≤ r)
    (hm1 : 0 ≤ m1) (hm1μ : m1 ≤ μm) (hm2μ : m2 ≤ μmid) (hmid : 0 ≤ μmid)
    (hG : 0 ≤ k * (1 / (2 * r) - 1 / (3 * r ^ 2)) - 5 / 2 + 1 / 2 * m1
            + 2 * (1 - 1 / k) * m2 - k / (k - 1) * D) :
    D / (k - 1) + r * Real.log (1 + 1 / r) + -(μm / (2 * (k - 1)))
      < (k - 2) * Real.log (1 + 1 / k) + Real.log (1 + 2 / k) * μmid := by
  have hk0 : 0 < k := by linarith
  have hk1 : 0 < k - 1 := by linarith
  have hr0 : 0 < r := by linarith
  -- the three inverses as atoms
  obtain ⟨a, ha⟩ : ∃ a : ℝ, a = 1 / r := ⟨_, rfl⟩
  obtain ⟨b, hb⟩ : ∃ b : ℝ, b = 1 / k := ⟨_, rfl⟩
  obtain ⟨d, hd⟩ : ∃ d : ℝ, d = 1 / (k - 1) := ⟨_, rfl⟩
  have hb0 : 0 < b := by rw [hb]; exact one_div_pos.mpr hk0
  have hra : r * a = 1 := by rw [ha]; exact mul_one_div_cancel hr0.ne'
  have hkb : k * b = 1 := by rw [hb]; exact mul_one_div_cancel hk0.ne'
  have hkd : (k - 1) * d = 1 := by rw [hd]; exact mul_one_div_cancel hk1.ne'
  have hb3 : b ≤ 1 / 3 := by
    rw [hb]; exact one_div_le_one_div_of_le (by norm_num) hk
  have hbd : b ≤ d := by
    rw [hb, hd]; exact one_div_le_one_div_of_le hk1 (by linarith)
  -- logarithm bounds
  have L2 : Real.log (1 + 1 / r) ≤ a - a ^ 2 / 2 + a ^ 3 / 3 := by
    rw [ha]; exact log_one_add_le3 (one_div_pos.mpr hr0).le
  have L3 : b - b ^ 2 / 2 + b ^ 3 / 3 - b ^ 4 / 4 ≤ Real.log (1 + 1 / k) := by
    rw [hb]; exact log_one_add_ge4 (one_div_pos.mpr hk0).le
  have e2 : 2 / k = 2 * b := by rw [hb]; ring
  have L1 : 2 * b - (2 * b) ^ 2 / 2 ≤ Real.log (1 + 2 / k) := by
    rw [← e2]; exact log_one_add_ge2 (div_pos (by norm_num) hk0).le
  -- consequences
  have A1 : r * Real.log (1 + 1 / r) ≤ 1 - a / 2 + a ^ 2 / 3 := by
    have h := mul_le_mul_of_nonneg_left L2 hr0.le
    have e : r * (a - a ^ 2 / 2 + a ^ 3 / 3) = 1 - a / 2 + a ^ 2 / 3 := by
      linear_combination (1 - a / 2 + a ^ 2 / 3) * hra
    linarith
  have A2 : 1 - 5 / 2 * b + b ^ 2 ≤ (k - 2) * Real.log (1 + 1 / k) := by
    have h := mul_le_mul_of_nonneg_left L3 (by linarith : (0 : ℝ) ≤ k - 2)
    have e : (k - 2) * (b - b ^ 2 / 2 + b ^ 3 / 3 - b ^ 4 / 4)
        = 1 - 5 / 2 * b + 4 / 3 * b ^ 2 - 11 / 12 * b ^ 3 + 1 / 2 * b ^ 4 := by
      linear_combination (1 - b / 2 + b ^ 2 / 3 - b ^ 3 / 4) * hkb
    have hpoly : 0 ≤ b ^ 2 * ((4 - 3 * b) * (1 - 2 * b)) :=
      mul_nonneg (sq_nonneg b) (mul_nonneg (by linarith) (by linarith))
    linarith [hpoly, h, e]
  have A3 : 2 * b * (1 - b) * μmid ≤ Real.log (1 + 2 / k) * μmid := by
    have h := mul_le_mul_of_nonneg_right L1 hmid
    have e : (2 * b - (2 * b) ^ 2 / 2) * μmid = 2 * b * (1 - b) * μmid := by ring
    rw [e] at h
    exact h
  -- the hypothesis `0 ≤ G`, divided by `k`
  have hG' : 0 ≤ (a / 2 - a ^ 2 / 3) - 5 / 2 * b + 1 / 2 * m1 * b + 2 * b * (1 - b) * m2
      - D * d := by
    have e : k * (1 / (2 * r) - 1 / (3 * r ^ 2)) - 5 / 2 + 1 / 2 * m1
          + 2 * (1 - 1 / k) * m2 - k / (k - 1) * D
        = k * (a / 2 - a ^ 2 / 3) - 5 / 2 + 1 / 2 * m1 + 2 * (1 - b) * m2 - k * d * D := by
      have e1 : 1 / (2 * r) = a / 2 := by rw [ha]; ring
      have e2 : 1 / (3 * r ^ 2) = a ^ 2 / 3 := by rw [ha]; ring
      have e3 : k / (k - 1) = k * d := by rw [hd]; ring
      rw [e1, e2, e3, ← hb]
    rw [e] at hG
    have h := mul_nonneg hb0.le hG
    have e' : b * (k * (a / 2 - a ^ 2 / 3) - 5 / 2 + 1 / 2 * m1 + 2 * (1 - b) * m2 - k * d * D)
        = (a / 2 - a ^ 2 / 3) - 5 / 2 * b + 1 / 2 * m1 * b + 2 * b * (1 - b) * m2 - D * d := by
      linear_combination (a / 2 - a ^ 2 / 3 - d * D) * hkb
    rw [e'] at h
    exact h
  have P1 : 0 ≤ b * (1 - b) * (μmid - m2) :=
    mul_nonneg (mul_nonneg hb0.le (by linarith)) (by linarith)
  have P2 : m1 * b ≤ μm * d := mul_le_mul hm1μ hbd hb0.le (le_trans hm1 hm1μ)
  have P3 : 0 < b ^ 2 := pow_pos hb0 2
  have E1 : D / (k - 1) = D * d := by
    rw [div_eq_iff hk1.ne']
    linear_combination (-D) * hkd
  have E2 : μm / (2 * (k - 1)) = μm * d / 2 := by
    rw [div_eq_iff (mul_pos two_pos hk1).ne']
    linear_combination (-μm) * hkd
  rw [E1, E2]
  linarith [A1, A2, A3, hG', P1, P2, P3]

/-! ### Assembly -/

/-- The chain `C₊ ≤ e^c C₋ ≤ e^c B₋ ≤ … < … ≤ B₊` for real numbers. -/
private theorem crit_assemble {Cm Cp Lm Λ Lp A E P X Y Z t : ℝ}
    (hA : 0 < A) (hΛ : 0 < Λ) (hE : 0 < E) (hP : 0 ≤ P) (hY : 0 ≤ Y)
    (h1 : Cm - A * Lm ≤ 0) (h2 : Cp ≤ E * Cm) (h3 : Lm ≤ P * (1 - t) * Λ) (ht : 1 - t ≤ X)
    (h4 : Z * Λ ≤ Lp) (hS : E * P * X < Y * Z) :
    Cp - Y * A * Lp < 0 := by
  have h3' : Lm ≤ P * X * Λ :=
    le_trans h3 (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left ht hP) hΛ.le)
  have h1' : Cm ≤ A * (P * X * Λ) :=
    le_trans (by linarith) (mul_le_mul_of_nonneg_left h3' hA.le)
  have h5 : Cp ≤ E * (A * (P * X * Λ)) :=
    le_trans h2 (mul_le_mul_of_nonneg_left h1' hE.le)
  have h6 : E * (A * (P * X * Λ)) < Y * A * (Z * Λ) := by
    have e1 : E * (A * (P * X * Λ)) = (A * Λ) * (E * P * X) := by ring
    have e2 : Y * A * (Z * Λ) = (A * Λ) * (Y * Z) := by ring
    rw [e1, e2]
    exact mul_lt_mul_of_pos_left hS (mul_pos hA hΛ)
  have h7 : Y * A * (Z * Λ) ≤ Y * A * Lp :=
    mul_le_mul_of_nonneg_left h4 (mul_nonneg hY hA.le)
  linarith

/-- **The criterion.** At a first-layer position `n = k + r`, `2 ≤ r ≤ k - 1`, with `𝖦(r,k) ≥ 0`:
if `d_{n,k} ≤ 0` then `d_{n,k+1} < 0`. -/
theorem step_neg_of_Gfun {k r : ℕ} (hk : 3 ≤ k) (hr1 : 2 ≤ r) (hr2 : r ≤ k - 1)
    (hG : 0 ≤ Gfun r k) (hd : dq k (k + r) ≤ 0) : dq (k + 1) (k + r) < 0 := by
  have hk2 : 2 ≤ k := by omega
  have hk1 : 1 ≤ k := by omega
  have hr : 1 ≤ r := by omega
  have hkR : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hrR : (2 : ℝ) ≤ r := by exact_mod_cast hr1
  have hk0 : (0 : ℝ) < k := by linarith
  have hk10 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have hr0 : (0 : ℝ) < r := by linarith
  have hkr0 : (0 : ℝ) < (k : ℝ) + r := by linarith
  have hM : (0 : ℝ) < (k : ℝ) + 1 + (r : ℝ) / 2 := by linarith
  obtain ⟨hd1, hd2⟩ := dq_frozen hk2 hr hr2
  have hC := curv_ratio hk2 hr2
  have hsh := Lam_shorten (k := k) (r := r) hk2 hr
  have hra := Lam_raise (k := k) (r := r) hk1 hr
  have hcr := cay_ratio (j := k) (by omega)
  -- positivity of `Λ_r(k;N)` and of `a_k/k`
  have hΛ : 0 < Lam (thr k ((k : ℝ) + r + 1)) r := Lam_thr_pos hr hk0.le (by linarith)
  have hA : 0 < cay k / k := div_pos (cay_pos (by omega)) hk0
  -- the two means and their lower bounds
  have hμmid0 : 0 ≤ muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)) :=
    muh_nonneg hr (div_pos hk0 hM).le
  have hm1 : mu0 r ((r : ℝ) * (r + 1) / ((k : ℝ) - 1))
      ≤ muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) := by
    have h := mu0_le_muh (r := r) hr (h := ((k : ℝ) - 1) / ((k : ℝ) + r))
      (div_pos hk10 hkr0) ((div_le_one hkr0).mpr (by linarith))
    have e : (r : ℝ) * (1 / (((k : ℝ) - 1) / ((k : ℝ) + r)) - 1)
        = (r : ℝ) * (r + 1) / ((k : ℝ) - 1) := by
      rw [one_div_div, eq_div_iff hk10.ne']
      have h3 : ((k : ℝ) + r) / ((k : ℝ) - 1) * ((k : ℝ) - 1) = (k : ℝ) + r :=
        div_mul_cancel₀ _ hk10.ne'
      linear_combination (r : ℝ) * h3
    rw [e] at h
    exact h
  have hm2 : mu0 r ((r : ℝ) * (r + 2) / (2 * (k : ℝ)))
      ≤ muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)) := by
    have h := mu0_le_muh (r := r) hr (h := (k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2))
      (div_pos hk0 hM) ((div_le_one hM).mpr (by linarith))
    have e : (r : ℝ) * (1 / ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)) - 1)
        = (r : ℝ) * (r + 2) / (2 * (k : ℝ)) := by
      have h2k : (2 : ℝ) * (k : ℝ) ≠ 0 := by positivity
      rw [one_div_div, eq_div_iff h2k]
      have h3 : ((k : ℝ) + 1 + (r : ℝ) / 2) / (k : ℝ) * (k : ℝ) = (k : ℝ) + 1 + (r : ℝ) / 2 :=
        div_mul_cancel₀ _ hk0.ne'
      linear_combination (2 * (r : ℝ)) * h3
    rw [e] at h
    exact h
  have hm10 : 0 ≤ mu0 r ((r : ℝ) * (r + 1) / ((k : ℝ) - 1)) :=
    mu0_nonneg hr (div_nonneg (by positivity) hk10.le)
  -- the scalar inequality
  have hG' := hG
  unfold Gfun at hG'
  have hlog := crit_scalar_log (k := (k : ℝ)) (r := (r : ℝ)) (D := Dbirth r)
    (μm := muh r (((k : ℝ) - 1) / ((k : ℝ) + r)))
    (μmid := muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)))
    (m1 := mu0 r ((r : ℝ) * (r + 1) / ((k : ℝ) - 1)))
    (m2 := mu0 r ((r : ℝ) * (r + 2) / (2 * (k : ℝ))))
    hkR (by linarith) hm10 hm1 hm2 hμmid0 hG'
  have hr1pos : (0 : ℝ) < 1 + 1 / (r : ℝ) := by positivity
  have hk1pos : (0 : ℝ) < 1 + 1 / (k : ℝ) := by positivity
  have hk2pos : (0 : ℝ) < 1 + 2 / (k : ℝ) := by positivity
  have hS : Real.exp (Dbirth r / ((k : ℝ) - 1)) * (1 + 1 / (r : ℝ)) ^ r
        * Real.exp (-(muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1))))
      < (1 + 1 / (k : ℝ)) ^ (k - 2)
        * (1 + 2 / (k : ℝ)) ^ (muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2))) := by
    have e1 : (1 + 1 / (r : ℝ)) ^ r = Real.exp ((r : ℝ) * Real.log (1 + 1 / (r : ℝ))) := by
      rw [Real.exp_nat_mul, Real.exp_log hr1pos]
    have e2 : (1 + 1 / (k : ℝ)) ^ (k - 2)
        = Real.exp (((k : ℝ) - 2) * Real.log (1 + 1 / (k : ℝ))) := by
      have hc : ((k - 2 : ℕ) : ℝ) = (k : ℝ) - 2 := by
        rw [Nat.cast_sub hk2]
        norm_num
      rw [← hc, Real.exp_nat_mul, Real.exp_log hk1pos]
    have e3 : (1 + 2 / (k : ℝ)) ^ (muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)))
        = Real.exp (Real.log (1 + 2 / (k : ℝ))
            * muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2))) :=
      Real.rpow_def_of_pos hk2pos _
    rw [e1, e2, e3, ← Real.exp_add, ← Real.exp_add, ← Real.exp_add, Real.exp_lt_exp]
    exact hlog
  -- `a_{k+1}/(k+1) = (1+1/k)^(k-2) · a_k/k`
  have hcay : cay (k + 1) / ((k : ℝ) + 1) = (1 + 1 / (k : ℝ)) ^ (k - 2) * (cay k / k) := by
    have ek : k - 1 = (k - 2) + 1 := by omega
    have hkb : (k : ℝ) * (1 / (k : ℝ)) = 1 := mul_one_div_cancel hk0.ne'
    have hk1' : (k : ℝ) + 1 ≠ 0 := by positivity
    rw [hcr, ek, pow_succ, div_eq_iff hk1']
    linear_combination (-((1 + 1 / (k : ℝ)) ^ (k - 2) * cay k)) * hkb
  -- assembly
  have ht : 1 - muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1))
      ≤ Real.exp (-(muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1)))) := by
    have h := Real.add_one_le_exp (-(muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1))))
    linarith
  rw [hd1] at hd
  rw [hd2, hcay]
  exact crit_assemble hA hΛ (Real.exp_pos _) (pow_nonneg hr1pos.le _) (pow_nonneg hk1pos.le _)
    hd hC hsh ht hra hS

end Parking
