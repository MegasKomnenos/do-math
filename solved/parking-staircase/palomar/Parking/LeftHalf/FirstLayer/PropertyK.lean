module

public import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
# Property K

Let `W` be a function of the threshold and let `a = W(k-1)`, `b = W(k)`, `c = W(k+1)` be its three
values around `k`.  The triple has *property K at `k`*, `TK k a b c`, when

  `2 e^{μ/k} b ≤ e^μ c + e^{-μ} a`  for all `μ ≥ 0`.

At `μ = 0` this is the convexity `2b ≤ c + a` (`TK.convex`).  For `μ > 0` it says that the convexity
survives when the three values are tilted by `e^{-μ}, 1, e^{μ}`, with the margin `e^{μ/k}` on the
middle value.  The tilts are what makes the property stable under the operations of the last-car
recursion, and this file collects the stability statements:

* sums and nonnegative multiples (`TK.add`, `TK.sum`, `TK.smul`);
* multiplication by a positive factor `f` with `f(k-1) ≤ f(k+1)` and
  `(k+1) log (f(k+1)/f(k)) + (k-1) log (f(k-1)/f(k)) ≥ 0` (`TK.mul_factor`, a consequence of the
  tilt-shift identity `TK.shift`);
* in particular the factors `z ↦ (z+α)/(z+β)`, `0 ≤ α ≤ β` (`TK.mul_ratio`), and
  `z ↦ (z+a)(z+b)/z`, `a, b ≥ 0`, `ab ≤ k² - 1` (`TK.mul_prod`).
-/

@[expose] public section

namespace Parking.FirstLayer
open Real Finset

/-- Property K at `k` for the three values `a = W(k-1)`, `b = W(k)`, `c = W(k+1)`. -/
def TK (k a b c : ℝ) : Prop :=
  ∀ μ : ℝ, 0 ≤ μ → 2 * exp (μ / k) * b ≤ exp μ * c + exp (-μ) * a

/-- Property K contains the convexity of the triple (the case `μ = 0`). -/
theorem TK.convex {k a b c : ℝ} (h : TK k a b c) : 2 * b ≤ c + a := by
  simpa using h 0 le_rfl

/-- If two triples have property K at $k$, so does their componentwise sum. -/
theorem TK.add {k a b c a' b' c' : ℝ} (h : TK k a b c) (h' : TK k a' b' c') :
    TK k (a + a') (b + b') (c + c') := by
  intro μ hμ
  have h1 := h μ hμ
  have h2 := h' μ hμ
  linarith

/-- If a triple has property K at $k$, so does its multiple by a nonnegative real number. -/
theorem TK.smul {k a b c : ℝ} {r : ℝ} (hr : 0 ≤ r) (h : TK k a b c) :
    TK k (r * a) (r * b) (r * c) := by
  intro μ hμ
  have h1 := mul_le_mul_of_nonneg_left (h μ hμ) hr
  linarith

/-- A finite sum of triples that have property K at $k$ has property K at $k$. -/
theorem TK.sum {ι : Type*} (s : Finset ι) (k : ℝ) (a b c : ι → ℝ)
    (h : ∀ i ∈ s, TK k (a i) (b i) (c i)) :
    TK k (∑ i ∈ s, a i) (∑ i ∈ s, b i) (∑ i ∈ s, c i) := by
  intro μ hμ
  rw [Finset.mul_sum, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
  exact Finset.sum_le_sum fun i hi => h i hi μ hμ

/-! ### Multiplication by a factor -/

/-- **Tilt shift.** Multiplying `c` by `e^L` and `a` by `e^M` shifts the tilt by `(L-M)/2` and
multiplies the middle value by `exp(((k+1)L + (k-1)M)/(2k))`. -/
theorem TK.shift {k a b c : ℝ} (hk : 0 < k) (h : TK k a b c) (L M μ : ℝ)
    (hμ : 0 ≤ μ + (L - M) / 2) :
    2 * exp (μ / k) * exp (((k + 1) * L + (k - 1) * M) / (2 * k)) * b ≤
      exp μ * (exp L * c) + exp (-μ) * (exp M * a) := by
  have hk0 : k ≠ 0 := hk.ne'
  have h1 := h (μ + (L - M) / 2) hμ
  have hA : 0 ≤ exp ((L + M) / 2) := (exp_pos _).le
  have h2 := mul_le_mul_of_nonneg_left h1 hA
  have e1 : exp ((L + M) / 2) * exp ((μ + (L - M) / 2) / k) =
      exp (μ / k) * exp (((k + 1) * L + (k - 1) * M) / (2 * k)) := by
    rw [← exp_add, ← exp_add]
    congr 1
    field_simp
    ring
  have e2 : exp ((L + M) / 2) * exp (μ + (L - M) / 2) = exp μ * exp L := by
    rw [← exp_add, ← exp_add]
    congr 1
    ring
  have e3 : exp ((L + M) / 2) * exp (-(μ + (L - M) / 2)) = exp (-μ) * exp M := by
    rw [← exp_add, ← exp_add]
    congr 1
    ring
  calc 2 * exp (μ / k) * exp (((k + 1) * L + (k - 1) * M) / (2 * k)) * b
      = exp ((L + M) / 2) * (2 * exp ((μ + (L - M) / 2) / k) * b) := by
        linear_combination (-(2 * b)) * e1
    _ ≤ exp ((L + M) / 2) *
          (exp (μ + (L - M) / 2) * c + exp (-(μ + (L - M) / 2)) * a) := h2
    _ = exp μ * (exp L * c) + exp (-μ) * (exp M * a) := by
        rw [mul_add, ← mul_assoc, ← mul_assoc, e2, e3]; ring

/-- Property K is preserved by a factor with positive values `fm, f0, fp` at `k-1, k, k+1` such
that `fm ≤ fp` and `(k+1) log (fp/f0) + (k-1) log (fm/f0) ≥ 0`. -/
private theorem TK.mul_factor {k a b c : ℝ} (hk : 0 < k) (h : TK k a b c) (hb : 0 ≤ b)
    {fm f0 fp : ℝ} (hm : 0 < fm) (h0 : 0 < f0) (hmp : fm ≤ fp)
    (hΞ : 0 ≤ (k + 1) * Real.log (fp / f0) + (k - 1) * Real.log (fm / f0)) :
    TK k (fm * a) (f0 * b) (fp * c) := by
  have hp : 0 < fp := lt_of_lt_of_le hm hmp
  intro μ hμ
  have hLM : Real.log (fm / f0) ≤ Real.log (fp / f0) :=
    Real.log_le_log (div_pos hm h0) (div_le_div_of_nonneg_right hmp h0.le)
  have hsh := h.shift hk (Real.log (fp / f0)) (Real.log (fm / f0)) μ (by linarith)
  rw [Real.exp_log (div_pos hp h0), Real.exp_log (div_pos hm h0)] at hsh
  have hone : 1 ≤ exp (((k + 1) * Real.log (fp / f0) + (k - 1) * Real.log (fm / f0)) / (2 * k)) :=
    Real.one_le_exp (div_nonneg hΞ (by positivity))
  have hpos : 0 ≤ 2 * exp (μ / k) * b := by positivity
  have h3 := mul_le_mul_of_nonneg_left hone hpos
  have h4 : 2 * exp (μ / k) * b ≤ exp μ * (fp / f0 * c) + exp (-μ) * (fm / f0 * a) := by
    linarith
  have h5 := mul_le_mul_of_nonneg_left h4 h0.le
  have e1 : f0 * (exp μ * (fp / f0 * c) + exp (-μ) * (fm / f0 * a)) =
      exp μ * (fp * c) + exp (-μ) * (fm * a) := by
    field_simp
  rw [e1] at h5
  linarith

/-- The logarithmic hypothesis of `TK.mul_factor` for a factor whose upper ratio is `1 + u`
(`u ≥ 0`) and whose lower ratio `r` has `1/r - 1 = w`: by `log (1+u) ≥ 2u/(u+2)` and
`log r ≥ 1 - 1/r` it suffices that `(k-1) w ≤ (k+1) · 2u/(u+2)`. -/
private theorem log_factor_nonneg {k u w rp rm : ℝ} (hk : 1 < k) (hu : 0 ≤ u) (hrp : rp = 1 + u)
    (hrm : 0 < rm) (hw : rm⁻¹ - 1 = w) (h : (k - 1) * w ≤ (k + 1) * (2 * u / (u + 2))) :
    0 ≤ (k + 1) * Real.log rp + (k - 1) * Real.log rm := by
  have h1 := Real.le_log_one_add_of_nonneg hu
  have h2 := Real.log_le_sub_one_of_pos (inv_pos.mpr hrm)
  rw [Real.log_inv, hw] at h2
  rw [hrp]
  have t1 := mul_le_mul_of_nonneg_left h1 (by linarith : (0 : ℝ) ≤ k + 1)
  have t2 := mul_le_mul_of_nonneg_left h2 (by linarith : (0 : ℝ) ≤ k - 1)
  linarith

/-- Property K is preserved by the factor `z ↦ (z+α)/(z+β)`, `0 ≤ α ≤ β`. -/
theorem TK.mul_ratio {k a b c α β : ℝ} (hk : 1 < k) (h : TK k a b c) (hb : 0 ≤ b)
    (hα : 0 ≤ α) (hαβ : α ≤ β) :
    TK k ((k - 1 + α) / (k - 1 + β) * a) ((k + α) / (k + β) * b)
      ((k + 1 + α) / (k + 1 + β) * c) := by
  have hβ : 0 ≤ β := le_trans hα hαβ
  have hd : 0 ≤ β - α := by linarith
  have p1 : 0 < k + α := by linarith
  have p2 : 0 < k + β := by linarith
  have p3 : 0 < k + 1 + α := by linarith
  have p4 : 0 < k + 1 + β := by linarith
  have p5 : 0 < k - 1 + α := by linarith
  have p6 : 0 < k - 1 + β := by linarith
  refine h.mul_factor (by linarith) hb (by positivity) (by positivity) ?_ ?_
  · rw [div_le_div_iff₀ p6 p4]
    nlinarith [mul_nonneg hα hd]
  · -- upper ratio `1 + u`, lower ratio `r` with `1/r - 1 = w`
    refine log_factor_nonneg hk (u := (β - α) / ((k + α) * (k + 1 + β)))
      (w := (β - α) / ((k + β) * (k - 1 + α))) (by positivity) ?_ (by positivity) ?_ ?_
    · field_simp
      ring
    · field_simp
      ring
    · have e : 2 * ((β - α) / ((k + α) * (k + 1 + β))) /
          ((β - α) / ((k + α) * (k + 1 + β)) + 2) =
          2 * (β - α) / (2 * ((k + α) * (k + 1 + β)) + (β - α)) := by
        field_simp
        ring
      rw [e, ← mul_div_assoc, ← mul_div_assoc, div_le_div_iff₀ (by positivity) (by positivity)]
      have hpoly : 0 ≤ α * (4 * β + 3 * k + 1) + β * (k - 1) :=
        add_nonneg (mul_nonneg hα (by linarith)) (mul_nonneg hβ (by linarith))
      nlinarith [mul_nonneg hd hpoly]

/-- Property K is preserved by the factor `z ↦ (z+a)(z+b)/z`, `a, b ≥ 0`, `a b ≤ k² - 1`.  With
`u = (k(k+1) - ab)/((k+a)(k+b)(k+1))` and `w = (k(k-1) - ab)/((k-1+a)(k-1+b)k)` the logarithmic
hypothesis reduces to
`k²(k-1)²(k+1) + 4k²(k²-1)(a+b) + ab (10k³ + 2k² - 4k - (3k+1) ab) ≥ 0`. -/
theorem TK.mul_prod {k a' b' c' a b : ℝ} (hk : 1 < k) (h : TK k a' b' c') (hb' : 0 ≤ b')
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a * b ≤ k ^ 2 - 1) :
    TK k ((k - 1 + a) * (k - 1 + b) / (k - 1) * a') ((k + a) * (k + b) / k * b')
      ((k + 1 + a) * (k + 1 + b) / (k + 1) * c') := by
  have k0 : 0 < k := by linarith
  have k1 : 0 < k - 1 := by linarith
  have k2 : 0 < k + 1 := by linarith
  have p1 : 0 < k + a := by linarith
  have p2 : 0 < k + b := by linarith
  have p3 : 0 < k + 1 + a := by linarith
  have p4 : 0 < k + 1 + b := by linarith
  have p5 : 0 < k - 1 + a := by linarith
  have p6 : 0 < k - 1 + b := by linarith
  have hd : 0 ≤ k * (k + 1) - a * b := by nlinarith [hab]
  refine h.mul_factor k0 hb' (by positivity) (by positivity) ?_ ?_
  · rw [div_le_div_iff₀ k1 k2]
    nlinarith [hab]
  · refine log_factor_nonneg hk (u := (k * (k + 1) - a * b) / ((k + a) * (k + b) * (k + 1)))
      (w := (k * (k - 1) - a * b) / ((k - 1 + a) * (k - 1 + b) * k)) (by positivity) ?_
      (by positivity) ?_ ?_
    · field_simp
      ring
    · field_simp
      ring
    · have e : 2 * ((k * (k + 1) - a * b) / ((k + a) * (k + b) * (k + 1))) /
          ((k * (k + 1) - a * b) / ((k + a) * (k + b) * (k + 1)) + 2) =
          2 * (k * (k + 1) - a * b) /
            (2 * ((k + a) * (k + b) * (k + 1)) + (k * (k + 1) - a * b)) := by
        field_simp
        ring
      rw [e, ← mul_div_assoc, ← mul_div_assoc, div_le_div_iff₀ (by positivity) (by positivity)]
      have hk21 : 0 ≤ k ^ 2 - 1 := by nlinarith [mul_pos k1 k2]
      have h1 : 0 ≤ k ^ 2 * (k - 1) ^ 2 * (k + 1) := by positivity
      have h2 : 0 ≤ 4 * k ^ 2 * (k ^ 2 - 1) * (a + b) :=
        mul_nonneg (mul_nonneg (by positivity) hk21) (add_nonneg ha hb)
      have hk3 : 0 ≤ 7 * k ^ 3 + k ^ 2 - k + 1 := by
        nlinarith [mul_nonneg (sq_nonneg k) k1.le, mul_nonneg k0.le k1.le]
      have h3' : (3 * k + 1) * (a * b) ≤ (3 * k + 1) * (k ^ 2 - 1) :=
        mul_le_mul_of_nonneg_left hab (by linarith)
      have hq : 0 ≤ 10 * k ^ 3 + 2 * k ^ 2 - 4 * k - (3 * k + 1) * (a * b) := by
        nlinarith [h3', hk3]
      have h3 : 0 ≤ a * b * (10 * k ^ 3 + 2 * k ^ 2 - 4 * k - (3 * k + 1) * (a * b)) :=
        mul_nonneg (mul_nonneg ha hb) hq
      nlinarith [h1, h2, h3]

end Parking.FirstLayer