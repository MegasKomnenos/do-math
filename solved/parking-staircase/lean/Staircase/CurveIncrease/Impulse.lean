import Staircase.CurveIncrease.Convolutions
import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
# The impulse side: an upper bound of the boundary term

The boundary term of the pair–impulse criterion is the chain sum `Λ_R(k+1; k+R)`, the total weight
of the compositions of `R` with the cut factors `(k+1)/(k+R-s)`; it is called the impulse here.
Write `P = poissonMass`.  The module proves one statement, `impulse_le`: for `R ≥ 1`, a threshold
`0 ≤ y ≤ K` with `R ≤ K`, and every real `c'` with `1 + c' ≥ 0`,

`e^{-R} · Λ_R(y+1; y+R) ≤ P(R) - e^{-c'} · ((1+c') · (R-2)/(2(K+R-1)) · κ₂(R)`
`      - 1/(K+1) · ((R-3)/3) · κ₃(R) · (4R/5 - 1)/(K + 3R/5))`.

The proof has four steps.

* The chain sum does not decrease when the threshold is raised from `y` to `K` (`Lam_thr_mono`):
  each cut factor `(y+1)/(y+R-s)` is at most `1` and increases with `y`.
* The first violating point identity `Lam_defect` writes `ren R - Λ_R` as a sum over the first cut
  point `s` whose factor `1 - f(s) = (R-1-s)/(K+R-s)` is chosen, with the chain sum `Λ_s` below it.
  The tangent inequality `Lam_tangent` bounds `Λ_s` from below (`chain_below_ge`), the exponents
  being `log ((K+R-c)/(K+1)) ≤ (R-1-c)/(K+1)`.  This gives the bound with two sums in the place of
  the closed forms (`impulse_bound`).
* The first sum is at least `(R-2)/(2(K+R-1)) · κ₂(R)` by the mean position `kc2_mom`
  (`first_sum_ge`).
* The second sum is `∑_s w_s · h(s)` with the weights `w_s = P(R-s)(R-1-s) κ₂(s)` and
  `h(x) = (R-1-x/2)/(K+R-x)`, which is concave on `[0,R]` for `K ≥ R`.  Its tangent at `x₀ = 2R/5`
  lies above it, the mean position of the weights is at least `x₀` and the tangent has a negative
  slope, so the sum is at most `h(x₀) · ∑_s w_s` (`second_sum_le`).
-/

namespace Parking

open Finset

/-- **The chain sum is monotone in the threshold.** For `0 ≤ y ≤ y'`,
`Λ_R(y+1; y+R) ≤ Λ_R(y'+1; y'+R)`: at a cut point `0 < s < R` the factor `(y+1)/(y+R-s)` is
nonnegative and does not decrease with `y`, since `R - s ≥ 1`. -/
private theorem Lam_thr_mono {R : ℕ} {y y' : ℝ} (hy : 0 ≤ y) (hyy' : y ≤ y') :
    Lam (thr (y + 1) (y + R)) R ≤ Lam (thr (y' + 1) (y' + R)) R := by
  have hsR : ∀ s ∈ Ioo 0 R, (s : ℝ) + 1 ≤ R := fun s hs => by
    exact_mod_cast (mem_Ioo.1 hs).2
  refine Lam_mono (fun s hs => ?_) (fun s hs => ?_)
  · have := hsR s hs
    exact div_nonneg (by linarith) (by linarith)
  · have := hsR s hs
    show (y + 1) / (y + (R : ℝ) - (s : ℝ)) ≤ (y' + 1) / (y' + (R : ℝ) - (s : ℝ))
    rw [div_le_div_iff₀ (by linarith) (by linarith)]
    nlinarith [mul_nonneg (sub_nonneg.2 hyy') (show (0 : ℝ) ≤ (R : ℝ) - s - 1 by linarith)]

/-- The chain sum below a cut point `0 < s < R`, for the threshold `K > 0`:
`e^{-c'} · ((1+c') · P(s) - (R-1-s/2)/(K+1) · κ₂(s)) ≤ e^{-s} · Λ_s(K+1; K+R)`.  The cut factors
are `e^{-x(c)}` with `x(c) = log ((K+R-c)/(K+1)) ≤ (R-1-c)/(K+1)`, so this is `Lam_tangent`, with
the sum of the exponents evaluated by `kc2_mom`. -/
private theorem chain_below_ge {R s : ℕ} (hs1 : 0 < s) (hsR : s < R) {K : ℝ} (hK : 0 < K)
    (c' : ℝ) :
    Real.exp (-c') * ((1 + c') * poissonMass s
        - 1 / (K + 1) * (((R : ℝ) - 1 - (s : ℝ) / 2) * kc2 s))
      ≤ Real.exp (-(s : ℝ)) * Lam (thr (K + 1) (K + R)) s := by
  have hsRr : (s : ℝ) + 1 ≤ R := by exact_mod_cast hsR
  have hK1 : 0 < K + 1 := by linarith
  have hpos : ∀ c ∈ Ioo 0 s, 0 < (K + (R : ℝ) - (c : ℝ)) / (K + 1) := fun c hc => by
    have hcs : (c : ℝ) < s := Nat.cast_lt.2 (mem_Ioo.1 hc).2
    exact div_pos (by linarith) hK1
  -- the profile is `e^{-x}`
  have hcongr : Lam (thr (K + 1) (K + R)) s
      = Lam (fun c : ℕ => Real.exp (-(Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1))))) s :=
    Lam_congr fun c hc => by
      show (K + 1) / (K + (R : ℝ) - (c : ℝ)) = _
      rw [Real.exp_neg, Real.exp_log (hpos c hc), inv_div]
  have ht := Lam_tangent (fun c : ℕ => Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1))) c' hs1
  -- the exponents, weighted, are at most `(R-1-s/2)/(K+1) · κ₂(s)`
  have hsum : Real.exp (-(s : ℝ)) * ∑ c ∈ Ioo 0 s,
        ren (s - c) * (ren c * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1)))
      ≤ 1 / (K + 1) * (((R : ℝ) - 1 - (s : ℝ) / 2) * kc2 s) := by
    have h1 : ∀ c ∈ Ioo 0 s, Real.exp (-(s : ℝ))
          * (ren (s - c) * (ren c * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1))))
        ≤ ((R : ℝ) - 1) / (K + 1) * (poissonMass c * poissonMass (s - c))
          - 1 / (K + 1) * ((c : ℝ) * (poissonMass c * poissonMass (s - c))) := by
      intro c hc
      have hx : Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1)) ≤ ((R : ℝ) - 1 - c) / (K + 1) := by
        have h := Real.log_le_sub_one_of_pos (hpos c hc)
        rwa [div_sub_one hK1.ne', show K + (R : ℝ) - c - (K + 1) = (R : ℝ) - 1 - c by ring] at h
      have hw : 0 ≤ poissonMass c * poissonMass (s - c) :=
        mul_nonneg (poissonMass_pos _).le (poissonMass_pos _).le
      have h := mul_le_mul_of_nonneg_left hx hw
      rw [poissonMass_mul (mem_Ioo.1 hc).2.le] at h ⊢
      calc Real.exp (-(s : ℝ))
            * (ren (s - c) * (ren c * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1))))
          = Real.exp (-(s : ℝ)) * (ren c * ren (s - c))
              * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1)) := by ring
        _ ≤ _ := h
        _ = _ := by ring
    rw [Finset.mul_sum]
    refine (Finset.sum_le_sum h1).trans (le_of_eq ?_)
    rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc2_mom s]
    unfold kc2
    ring
  calc Real.exp (-c') * ((1 + c') * poissonMass s
          - 1 / (K + 1) * (((R : ℝ) - 1 - (s : ℝ) / 2) * kc2 s))
      ≤ Real.exp (-c') * ((1 + c') * poissonMass s
          - Real.exp (-(s : ℝ)) * ∑ c ∈ Ioo 0 s,
              ren (s - c) * (ren c * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1)))) :=
        mul_le_mul_of_nonneg_left (by linarith) (Real.exp_pos _).le
    _ = Real.exp (-(s : ℝ)) * (Real.exp (-c') * ((1 + c') * ren s
          - ∑ c ∈ Ioo 0 s,
              ren (s - c) * (ren c * Real.log ((K + (R : ℝ) - (c : ℝ)) / (K + 1))))) := by
        unfold poissonMass
        ring
    _ ≤ Real.exp (-(s : ℝ)) * Lam (thr (K + 1) (K + R)) s := by
        rw [hcongr]
        exact mul_le_mul_of_nonneg_left ht (Real.exp_pos _).le

/-- The impulse at the threshold `K > 0`, bounded by two sums over the first violating point:
`e^{-R} Λ_R(K+1; K+R) ≤ P(R) - e^{-c'} · ((1+c') · ∑_s δ(s) · P(s) P(R-s)`
`  - 1/(K+1) · ∑_s δ(s) · (R-1-s/2) · P(R-s) κ₂(s))` with `δ(s) = (R-1-s)/(K+R-s)`.  This is
`Lam_defect`, normalised by `e^{-R}`, with `chain_below_ge` for the chain sum below `s`. -/
private theorem impulse_bound {R : ℕ} (hR : 1 ≤ R) {K : ℝ} (hK : 0 < K) (c' : ℝ) :
    Real.exp (-(R : ℝ)) * Lam (thr (K + 1) (K + R)) R
      ≤ poissonMass R - Real.exp (-c') *
          ((1 + c') * ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
              * (poissonMass s * poissonMass (R - s))
            - 1 / (K + 1) * ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
                * (((R : ℝ) - 1 - (s : ℝ) / 2) * (poissonMass (R - s) * kc2 s))) := by
  -- the defect identity, normalised by `e^{-R}`
  have hsum : poissonMass R - Real.exp (-(R : ℝ)) * Lam (thr (K + 1) (K + R)) R
      = ∑ s ∈ Ioo 0 R, (1 - thr (K + 1) (K + R) s)
          * (Real.exp (-(s : ℝ)) * Lam (thr (K + 1) (K + R)) s) * poissonMass (R - s) := by
    have hdef := Lam_defect (thr (K + 1) (K + R)) hR
    rw [show poissonMass R - Real.exp (-(R : ℝ)) * Lam (thr (K + 1) (K + R)) R
        = Real.exp (-(R : ℝ)) * (ren R - Lam (thr (K + 1) (K + R)) R) by unfold poissonMass; ring,
      hdef, Finset.mul_sum]
    refine Finset.sum_congr rfl fun s hs => ?_
    have hexp : Real.exp (-(R : ℝ)) = Real.exp (-(s : ℝ)) * Real.exp (-((R - s : ℕ) : ℝ)) := by
      rw [← Real.exp_add, Nat.cast_sub (mem_Ioo.1 hs).2.le]
      congr 1
      ring
    rw [poissonMass, hexp]
    ring
  -- the bound for one `s`
  have hterm : ∀ s ∈ Ioo 0 R,
      ((R : ℝ) - 1 - s) / (K + R - s)
          * (Real.exp (-c') * ((1 + c') * poissonMass s
              - 1 / (K + 1) * (((R : ℝ) - 1 - (s : ℝ) / 2) * kc2 s))) * poissonMass (R - s)
        ≤ (1 - thr (K + 1) (K + R) s)
          * (Real.exp (-(s : ℝ)) * Lam (thr (K + 1) (K + R)) s) * poissonMass (R - s) := by
    intro s hs
    rw [mem_Ioo] at hs
    have hsR : (s : ℝ) + 1 ≤ R := by exact_mod_cast hs.2
    have hden : 0 < K + (R : ℝ) - s := by linarith
    have hδ : 1 - thr (K + 1) (K + R) s = ((R : ℝ) - 1 - s) / (K + R - s) := by
      show 1 - (K + 1) / (K + (R : ℝ) - (s : ℝ)) = _
      rw [one_sub_div hden.ne']
      congr 1
      ring
    rw [hδ]
    exact mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left (chain_below_ge hs.1 hs.2 hK c')
        (div_nonneg (by linarith) hden.le)) (poissonMass_pos _).le
  -- the sum of the bounds
  have hA : ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
          * (Real.exp (-c') * ((1 + c') * poissonMass s
              - 1 / (K + 1) * (((R : ℝ) - 1 - (s : ℝ) / 2) * kc2 s))) * poissonMass (R - s)
      = Real.exp (-c') *
          ((1 + c') * ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
              * (poissonMass s * poissonMass (R - s))
            - 1 / (K + 1) * ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
                * (((R : ℝ) - 1 - (s : ℝ) / 2) * (poissonMass (R - s) * kc2 s))) := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_sub_distrib, Finset.mul_sum]
    exact Finset.sum_congr rfl fun s _ => by ring
  have hle := Finset.sum_le_sum hterm
  rw [← hsum, hA] at hle
  linarith

/-- The first sum of `impulse_bound`:
`(R-2)/(2(K+R-1)) · κ₂(R) ≤ ∑_{0<s<R} (R-1-s)/(K+R-s) · P(s) P(R-s)`.  Replace the denominator
`K+R-s` by the larger `K+R-1` and evaluate with `kc2_mom`. -/
private theorem first_sum_ge {R : ℕ} (hR : 1 ≤ R) {K : ℝ} (hK : 0 < K) :
    ((R : ℝ) - 2) / (2 * (K + R - 1)) * kc2 R
      ≤ ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
          * (poissonMass s * poissonMass (R - s)) := by
  have hR1 : (1 : ℝ) ≤ R := by exact_mod_cast hR
  have hD : K + (R : ℝ) - 1 ≠ 0 := by
    have : 0 < K + (R : ℝ) - 1 := by linarith
    exact this.ne'
  have hterm : ∀ s ∈ Ioo 0 R,
      ((R : ℝ) - 1) / (K + R - 1) * (poissonMass s * poissonMass (R - s))
          - 1 / (K + R - 1) * ((s : ℝ) * (poissonMass s * poissonMass (R - s)))
        ≤ ((R : ℝ) - 1 - s) / (K + R - s) * (poissonMass s * poissonMass (R - s)) := by
    intro s hs
    rw [mem_Ioo] at hs
    have hs1 : (1 : ℝ) ≤ s := by exact_mod_cast hs.1
    have hsR : (s : ℝ) + 1 ≤ R := by exact_mod_cast hs.2
    have hw : 0 ≤ poissonMass s * poissonMass (R - s) :=
      mul_nonneg (poissonMass_pos _).le (poissonMass_pos _).le
    have hfr : ((R : ℝ) - 1 - s) / (K + R - 1) ≤ ((R : ℝ) - 1 - s) / (K + R - s) :=
      div_le_div_of_nonneg_left (by linarith) (by linarith) (by linarith)
    have h := mul_le_mul_of_nonneg_right hfr hw
    calc ((R : ℝ) - 1) / (K + R - 1) * (poissonMass s * poissonMass (R - s))
          - 1 / (K + R - 1) * ((s : ℝ) * (poissonMass s * poissonMass (R - s)))
        = ((R : ℝ) - 1 - s) / (K + R - 1) * (poissonMass s * poissonMass (R - s)) := by ring
      _ ≤ _ := h
  refine le_trans (le_of_eq ?_) (Finset.sum_le_sum hterm)
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc2_mom R]
  unfold kc2
  field

/-- The tangent of `h(x) = ((N - x)/2 - c/2)/(N - x)` at `x₀`, in the variables `D = N - x₀` and
`M = N - s`: `h(x₀) + h'(x₀)(s - x₀) - h(s) = c (D-M)²/(2 D² M)`. -/
private theorem concave_tangent_gap {D M c : ℝ} (hD : D ≠ 0) (hM : M ≠ 0) :
    (D / 2 - c / 2) / D - c / (2 * D ^ 2) * (D - M) - (M / 2 - c / 2) / M
      = c * (D - M) ^ 2 / (2 * D ^ 2 * M) := by
  field

/-- The second sum of `impulse_bound`: for `K ≥ R ≥ 1`,
`∑_{0<s<R} (R-1-s)/(K+R-s) · (R-1-s/2) · P(R-s) κ₂(s) ≤ ((R-3)/3) · κ₃(R) · (4R/5 - 1)/(K + 3R/5)`.
With the weights `w_s = P(R-s)(R-1-s) κ₂(s)` the sum is `∑_s w_s h(s)`, `h(x) = (R-1-x/2)/(K+R-x)`.
The tangent of `h` at `x₀ = 2R/5` lies above `h` (`concave_tangent_gap` with `c = K - R + 2 > 0`)
and has a negative slope, the mean position of the weights is at least `x₀`
(`impulse_weight_mean`), and their sum is `((R-3)/3) κ₃(R)` (`impulse_weight_sum`). -/
private theorem second_sum_le {R : ℕ} (hR : 1 ≤ R) {K : ℝ} (hK : (R : ℝ) ≤ K) :
    ∑ s ∈ Ioo 0 R, ((R : ℝ) - 1 - s) / (K + R - s)
        * (((R : ℝ) - 1 - (s : ℝ) / 2) * (poissonMass (R - s) * kc2 s))
      ≤ ((R : ℝ) - 3) / 3 * kc3 R * ((4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R)) := by
  have hR1 : (1 : ℝ) ≤ R := by exact_mod_cast hR
  have hD0 : 0 < K + 3 / 5 * (R : ℝ) := by linarith
  have hc : 0 < K - (R : ℝ) + 2 := by linarith
  have hterm : ∀ s ∈ Ioo 0 R,
      ((R : ℝ) - 1 - s) / (K + R - s)
          * (((R : ℝ) - 1 - (s : ℝ) / 2) * (poissonMass (R - s) * kc2 s))
        ≤ (4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R)
            * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)
          - (K - R + 2) / (2 * (K + 3 / 5 * R) ^ 2)
              * ((s : ℝ) * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)
                  - 2 * (R : ℝ) / 5 * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)) := by
    intro s hs
    rw [mem_Ioo] at hs
    have hsR : (s : ℝ) + 1 ≤ R := by exact_mod_cast hs.2
    have hden : 0 < K + (R : ℝ) - s := by linarith
    have hw : 0 ≤ poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s :=
      mul_nonneg (mul_nonneg (poissonMass_pos _).le (by linarith)) (kc2_nonneg s)
    have key := concave_tangent_gap (c := K - R + 2) hD0.ne' hden.ne'
    rw [show (K + 3 / 5 * (R : ℝ)) / 2 - (K - R + 2) / 2 = 4 / 5 * (R : ℝ) - 1 by ring,
      show (K + (R : ℝ) - s) / 2 - (K - R + 2) / 2 = (R : ℝ) - 1 - (s : ℝ) / 2 by ring,
      show K + 3 / 5 * (R : ℝ) - (K + (R : ℝ) - s) = (s : ℝ) - 2 * (R : ℝ) / 5 by ring] at key
    have hnn : 0 ≤ (K - R + 2) * ((s : ℝ) - 2 * (R : ℝ) / 5) ^ 2
        / (2 * (K + 3 / 5 * R) ^ 2 * (K + R - s)) :=
      div_nonneg (mul_nonneg hc.le (sq_nonneg _))
        (mul_pos (mul_pos two_pos (pow_pos hD0 2)) hden).le
    have hh := mul_le_mul_of_nonneg_left
      (show ((R : ℝ) - 1 - (s : ℝ) / 2) / (K + R - s)
        ≤ (4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R)
          - (K - R + 2) / (2 * (K + 3 / 5 * R) ^ 2) * ((s : ℝ) - 2 * (R : ℝ) / 5) by linarith) hw
    calc ((R : ℝ) - 1 - s) / (K + R - s)
          * (((R : ℝ) - 1 - (s : ℝ) / 2) * (poissonMass (R - s) * kc2 s))
        = poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
            * (((R : ℝ) - 1 - (s : ℝ) / 2) / (K + R - s)) := by ring
      _ ≤ _ := hh
      _ = _ := by ring
  have hprod : 0 ≤ (K - R + 2) / (2 * (K + 3 / 5 * (R : ℝ)) ^ 2)
      * (∑ s ∈ Ioo 0 R, (s : ℝ) * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)
          - 2 * (R : ℝ) / 5
            * ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s) :=
    mul_nonneg (div_nonneg hc.le (mul_pos two_pos (pow_pos hD0 2)).le)
      (sub_nonneg.2 (impulse_weight_mean R))
  have hle := Finset.sum_le_sum hterm
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, Finset.sum_sub_distrib,
    ← Finset.mul_sum, impulse_weight_sum R] at hle
  rw [impulse_weight_sum R] at hprod
  have e : ((R : ℝ) - 3) / 3 * kc3 R * ((4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R))
      = (4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R) * (((R : ℝ) - 3) / 3 * kc3 R) := by ring
  rw [e]
  linarith

/-- **The upper bound of the impulse.** For `R ≥ 1`, a threshold `0 ≤ y ≤ K` with `R ≤ K`, and a
real `c'` with `1 + c' ≥ 0`,
`e^{-R} · Λ_R(y+1; y+R) ≤ P(R) - e^{-c'} · ((1+c') · (R-2)/(2(K+R-1)) · κ₂(R)`
`      - 1/(K+1) · ((R-3)/3) · κ₃(R) · (4R/5 - 1)/(K + 3R/5))`.
The chain sum is raised to the threshold `K` (`Lam_thr_mono`), bounded there through the first
violating point (`impulse_bound`), and the two sums of that bound are replaced by their closed
forms (`first_sum_ge`, `second_sum_le`). -/
theorem impulse_le {R : ℕ} (hR : 1 ≤ R) {y K : ℝ} (hy : 0 ≤ y) (hyK : y ≤ K) (hRK : (R : ℝ) ≤ K)
    (c' : ℝ) (hc : 0 ≤ 1 + c') :
    Real.exp (-(R : ℝ)) * Lam (thr (y + 1) (y + R)) R
      ≤ poissonMass R - Real.exp (-c') *
          ((1 + c') * (((R : ℝ) - 2) / (2 * (K + R - 1)) * kc2 R)
            - 1 / (K + 1)
              * (((R : ℝ) - 3) / 3 * kc3 R * ((4 / 5 * (R : ℝ) - 1) / (K + 3 / 5 * R)))) := by
  have hR1 : (1 : ℝ) ≤ R := by exact_mod_cast hR
  have hK : 0 < K := by linarith
  have h1 := mul_le_mul_of_nonneg_left (Lam_thr_mono (R := R) hy hyK) (Real.exp_pos (-(R : ℝ))).le
  have h2 := impulse_bound hR hK c'
  have h3 := mul_le_mul_of_nonneg_left (first_sum_ge hR hK) hc
  have h4 := mul_le_mul_of_nonneg_left (second_sum_le hR hRK)
    (show (0 : ℝ) ≤ 1 / (K + 1) by positivity)
  have h5 := mul_le_mul_of_nonneg_left (sub_le_sub h3 h4) (Real.exp_pos (-c')).le
  linarith

end Parking
