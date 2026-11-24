module

public import Parking.NextColumn.Birthday
public import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Raising the threshold by two (midpoint comparison + Jensen)

`Λ_r(k+2;N) ≥ (1+2/k)^{μ_mid} Λ_r(k;N)` with `N = k+r+1`, `μ_mid = muh r (k/(k+1+r/2))`.
The law of the number of parts under the threshold profile dominates, in likelihood-ratio order,
the homogeneous law with the midpoint factor `h_mid = k/(N - r/2)` (`Vc_thr_ratio_ge`); then
Jensen's inequality for `x ↦ (1+2/k)^x`.
-/

@[expose] public section

namespace Parking

open Finset

/-- Jensen's inequality for the exponential function `x ↦ c^x` (tangent-line form): if `τ = ∑ u_q`
and `μ τ = ∑ (q-1) u_q` with `u ≥ 0`, then `c^μ τ ≤ ∑ u_q c^(q-1)`. -/
private theorem raise_rpow_mean_mul_le_sum (s : Finset ℕ) (u : ℕ → ℝ) (hu : ∀ q ∈ s, 0 ≤ u q)
    (hs : ∀ q ∈ s, 1 ≤ q) {c : ℝ} (hc : 0 < c) {τ μ : ℝ} (hτ : τ = ∑ q ∈ s, u q)
    (hμ : μ * τ = ∑ q ∈ s, ((q : ℝ) - 1) * u q) :
    c ^ μ * τ ≤ ∑ q ∈ s, u q * c ^ (q - 1) := by
  have key : ∀ q ∈ s,
      u q * (c ^ μ * (1 + Real.log c * (((q : ℝ) - 1) - μ))) ≤ u q * c ^ (q - 1) := by
    intro q hq
    have hq1 : 1 ≤ q := hs q hq
    have e1 : ((q - 1 : ℕ) : ℝ) = (q : ℝ) - 1 := by
      rw [Nat.cast_sub hq1, Nat.cast_one]
    have h1 : c ^ (q - 1) = c ^ μ * Real.exp (Real.log c * (((q : ℝ) - 1) - μ)) := by
      rw [← Real.rpow_natCast, Real.rpow_def_of_pos hc, Real.rpow_def_of_pos hc,
        ← Real.exp_add, e1]
      congr 1
      ring
    rw [h1]
    refine mul_le_mul_of_nonneg_left ?_ (hu q hq)
    refine mul_le_mul_of_nonneg_left ?_ (Real.rpow_nonneg hc.le μ)
    have := Real.add_one_le_exp (Real.log c * (((q : ℝ) - 1) - μ))
    linarith
  have hsum : ∑ q ∈ s, u q * (c ^ μ * (1 + Real.log c * (((q : ℝ) - 1) - μ))) = c ^ μ * τ := by
    have e : ∀ q ∈ s, u q * (c ^ μ * (1 + Real.log c * (((q : ℝ) - 1) - μ)))
        = c ^ μ * (1 - Real.log c * μ) * u q + c ^ μ * Real.log c * (((q : ℝ) - 1) * u q) := by
      intro q _
      ring
    rw [Finset.sum_congr rfl e, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum,
      ← hτ, ← hμ]
    ring
  rw [← hsum]
  exact Finset.sum_le_sum key

/-- **Raising the threshold by two**: `(1+2/k)^{μ_mid} Λ_r(k;N) ≤ Λ_r(k+2;N)` with `N = k+r+1` and
`μ_mid = muh r (k/(k+1+r/2))`. -/
theorem Lam_raise {k r : ℕ} (hk : 1 ≤ k) (hr : 1 ≤ r) :
    (1 + 2 / (k : ℝ)) ^ (muh r ((k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2)))
        * Lam (thr k ((k : ℝ) + r + 1)) r
      ≤ Lam (thr ((k : ℝ) + 2) ((k : ℝ) + r + 1)) r := by
  have hk0 : (0 : ℝ) < k := by exact_mod_cast hk
  have hr0 : (0 : ℝ) < r := by exact_mod_cast hr
  have hN₀ : (r : ℝ) < (k : ℝ) + r + 1 := by linarith
  have hM : (0 : ℝ) < (k : ℝ) + 1 + (r : ℝ) / 2 := by positivity
  have hc₀ : (0 : ℝ) < 1 + 2 / (k : ℝ) := by positivity
  have hc₁ : (1 : ℝ) ≤ 1 + 2 / (k : ℝ) := by
    have : (0 : ℝ) ≤ 2 / (k : ℝ) := by positivity
    linarith
  have hhM₀ : (k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2) * ((k : ℝ) + r + 1 - (r : ℝ) / 2) = k := by
    have e : (k : ℝ) + r + 1 - (r : ℝ) / 2 = (k : ℝ) + 1 + (r : ℝ) / 2 := by ring
    rw [e]
    exact div_mul_cancel₀ _ hM.ne'
  have hkc₀ : (k : ℝ) * (1 + 2 / (k : ℝ)) = (k : ℝ) + 2 := by
    rw [mul_add, mul_one, mul_div_assoc', mul_div_cancel_left₀ _ hk0.ne']
  -- abstract the three real parameters
  obtain ⟨N, hNdef⟩ : ∃ N : ℝ, N = (k : ℝ) + r + 1 := ⟨_, rfl⟩
  obtain ⟨h, hhdef⟩ : ∃ h : ℝ, h = (k : ℝ) / ((k : ℝ) + 1 + (r : ℝ) / 2) := ⟨_, rfl⟩
  obtain ⟨c, hcdef⟩ : ∃ c : ℝ, c = 1 + 2 / (k : ℝ) := ⟨_, rfl⟩
  rw [← hNdef, ← hhdef, ← hcdef]
  rw [← hNdef] at hN₀
  rw [← hNdef, ← hhdef] at hhM₀
  rw [← hcdef] at hc₀ hc₁ hkc₀
  have hh0 : 0 < h := by rw [hhdef]; exact div_pos hk0 hM
  -- positivity facts
  have hVpos : ∀ q ∈ Icc 1 r, 0 < Vc (thr 1 N) q r := by
    intro q hq
    refine Vc_pos (fun s hs => ?_) (mem_Icc.mp hq).1 (mem_Icc.mp hq).2
    have hs' : (s : ℝ) < r := Nat.cast_lt.2 (mem_Ioo.mp hs).2
    rw [thr_apply]
    exact div_pos one_pos (by linarith)
  have hu : ∀ q ∈ Icc 1 r, 0 ≤ Tq r q * h ^ (q - 1) := fun q _ =>
    mul_nonneg (Tq_nonneg r q) (pow_nonneg hh0.le _)
  have hw : ∀ q ∈ Icc 1 r, 0 < (k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r := fun q hq =>
    mul_pos (pow_pos hk0 _) (hVpos q hq)
  -- consecutive likelihood ratios
  have hcons : ∀ q, 1 ≤ q → q + 1 ≤ r →
      Tq r (q + 1) * h ^ (q + 1 - 1) * ((k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r)
        ≤ Tq r q * h ^ (q - 1) * ((k : ℝ) ^ (q + 1 - 1) * Vc (thr 1 N) (q + 1) r) := by
    intro q hq hq1
    obtain ⟨p, rfl⟩ : ∃ p, q = p + 1 := ⟨q - 1, by omega⟩
    simp only [Nat.add_sub_cancel]
    have E1 := Tq_ratio r (q := p + 1) hq
    have E2 := Vc_thr_ratio_ge hN₀ (q := p + 1) hq
    have hQ : (0 : ℝ) < ((p + 1 : ℕ) : ℝ) := Nat.cast_pos.mpr (Nat.succ_pos p)
    have hQR : (0 : ℝ) < ((p + 1 : ℕ) : ℝ) * r := mul_pos hQ hr0
    have hcoef : 0 ≤ Tq r (p + 1) * h ^ (p + 1) * (k : ℝ) ^ p :=
      mul_nonneg (mul_nonneg (Tq_nonneg r (p + 1)) (pow_nonneg hh0.le _)) (pow_nonneg hk0.le _)
    have h5 := mul_le_mul_of_nonneg_left E2 hcoef
    refine le_of_mul_le_mul_left ?_ hQR
    calc ((p + 1 : ℕ) : ℝ) * r
          * (Tq r (p + 1 + 1) * h ^ (p + 1) * ((k : ℝ) ^ p * Vc (thr 1 N) (p + 1) r))
        = (((p + 1 : ℕ) : ℝ) * r * Tq r (p + 1 + 1))
            * (h ^ (p + 1) * (k : ℝ) ^ p * Vc (thr 1 N) (p + 1) r) := by ring
      _ = ((((p + 1 : ℕ) : ℝ) + 1) * ((r : ℝ) - ((p + 1 : ℕ) : ℝ)) * Tq r (p + 1))
            * (h ^ (p + 1) * (k : ℝ) ^ p * Vc (thr 1 N) (p + 1) r) := by rw [E1]
      _ = Tq r (p + 1) * h ^ (p + 1) * (k : ℝ) ^ p
            * ((((p + 1 : ℕ) : ℝ) + 1) * ((r : ℝ) - ((p + 1 : ℕ) : ℝ))
                * Vc (thr 1 N) (p + 1) r) := by ring
      _ ≤ Tq r (p + 1) * h ^ (p + 1) * (k : ℝ) ^ p
            * (((p + 1 : ℕ) : ℝ) * r * (N - (r : ℝ) / 2) * Vc (thr 1 N) (p + 1 + 1) r) := h5
      _ = ((p + 1 : ℕ) : ℝ) * r
            * (Tq r (p + 1) * h ^ p
                * ((k : ℝ) ^ p * (h * (N - (r : ℝ) / 2)) * Vc (thr 1 N) (p + 1 + 1) r)) := by
          ring
      _ = ((p + 1 : ℕ) : ℝ) * r
            * (Tq r (p + 1) * h ^ p * ((k : ℝ) ^ (p + 1) * Vc (thr 1 N) (p + 1 + 1) r)) := by
          rw [hhM₀]
          ring
  have hlr := lr_of_consecutive r (fun q => Tq r q * h ^ (q - 1))
    (fun q => (k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r) hw hcons
  have hφ : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ r → c ^ (q - 1) ≤ c ^ (q' - 1) := by
    intro q q' _ hqq' _
    exact pow_le_pow_right₀ hc₁ (by omega)
  have hsum := lr_sum_le r (fun q => Tq r q * h ^ (q - 1))
    (fun q => (k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r) (fun q => c ^ (q - 1)) hlr hφ
  -- the three sums
  have hΛk : Lam (thr k N) r = ∑ q ∈ Icc 1 r, (k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r :=
    Lam_thr k N r
  have hΛk2 : Lam (thr ((k : ℝ) + 2) N) r
      = ∑ q ∈ Icc 1 r, (k : ℝ) ^ (q - 1) * Vc (thr 1 N) q r * c ^ (q - 1) := by
    rw [Lam_thr]
    refine Finset.sum_congr rfl fun q _ => ?_
    rw [← hkc₀, mul_pow]
    ring
  have hτ : tau r h = ∑ q ∈ Icc 1 r, Tq r q * h ^ (q - 1) := tau_eq r h
  have hτpos : 0 < tau r h := tau_pos hr hh0.le
  have hμ := muh_mul_tau hr hh0.le
  -- Jensen
  have hJ : c ^ (muh r h) * tau r h ≤ ∑ q ∈ Icc 1 r, Tq r q * h ^ (q - 1) * c ^ (q - 1) :=
    raise_rpow_mean_mul_le_sum (Icc 1 r) (fun q => Tq r q * h ^ (q - 1)) hu
      (fun q hq => (mem_Icc.mp hq).1) hc₀ hτ hμ
  have hΛ0 : 0 ≤ Lam (thr k N) r := by
    rw [hΛk]
    exact Finset.sum_nonneg fun q hq => (hw q hq).le
  refine le_of_mul_le_mul_right ?_ hτpos
  calc c ^ (muh r h) * Lam (thr k N) r * tau r h
      = (c ^ (muh r h) * tau r h) * Lam (thr k N) r := by ring
    _ ≤ (∑ q ∈ Icc 1 r, Tq r q * h ^ (q - 1) * c ^ (q - 1)) * Lam (thr k N) r :=
        mul_le_mul_of_nonneg_right hJ hΛ0
    _ ≤ Lam (thr ((k : ℝ) + 2) N) r * tau r h := by
        rw [hΛk, hΛk2, hτ]
        exact hsum

end Parking
