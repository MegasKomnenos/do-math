import Parking.NextColumn.Birthday
import Parking.NextColumn.Frozen
import Batteries.Tactic.OpenPrivate
import Mathlib.Analysis.MeanInequalities

/-!
# Composition sums under a change of the cut profile

`Vc f q m` is the total weight of the compositions of `m` with `q` parts for the cut profile `f`: a
composition with the cut points `S` has the weight `∏ a_part · ∏_{s ∈ S} f s`, where `a = cay`.
As a function of the values of `f` it is a polynomial with nonnegative coefficients, and the
coefficient of a composition does not change when the composition is read backwards.  This module
draws the consequences of these two facts that the diagonal step needs.

* `Vc_rpow_mul_rpow_le` : the sum is log-convex in the profile,
  `Vc (a^α b^β) ≤ (Vc a)^α (Vc b)^β` for `α + β = 1`.  This is Hölder's inequality, carried through
  the recursion on the last part.
* `Vc_reverse` : the sum for the reflected profile `s ↦ f (m - s)` equals the sum for `f`.
* `Vc_sum_pow_le` : the comparison of two profiles `g`, `w` with `g^(k+1) ≤ w^k`.  For nonnegative
  weights `v_q`, `X = ∑_q v_q Vc g q m` and `Y = ∑_q v_q Vc w q m` satisfy `X^k ≤ ρ^(-μ) Y^k`, where
  `ρ² ≤ g(s) g(m-s)` at every cut point and `μ` is at least the mean of `q - 1` for the weights
  `v_q T_{m,q}`.  Log-convexity gives `X^(k+1) ≤ Z · Y^k` with `Z = ∑_q v_q T_{m,q}`; reflection and
  Jensen's inequality give `ρ^μ · Z ≤ X`.

The module also states Jensen's inequality for an exponential function (`jensen_rpow`), which the
boundary term uses as well.  Three facts about the sums are taken from
`Parking.NextColumn.Compositions`, where they are private: the sums are monotone in a nonnegative
profile (`Vc_mono`), homogeneous in the profile (`Vc_smul`), and satisfy a recursion on the first
part (`Vc_first`).
-/

namespace Parking

open Finset

open private Vc_smul Vc_mono Vc_first from Parking.NextColumn.Compositions
open private sum_Ioo_reflect from Parking.NextColumn.Frozen

/-! ### Two inequalities for finite sums -/

/-- Hölder's inequality as a weighted geometric mean: for `x, y ≥ 0` and `α, β > 0`, `α + β = 1`,
`∑ x_i^α y_i^β ≤ (∑ x_i)^α (∑ y_i)^β`. -/
private theorem sum_rpow_mul_rpow_le {ι : Type*} (s : Finset ι) (x y : ι → ℝ)
    (hx : ∀ i ∈ s, 0 ≤ x i) (hy : ∀ i ∈ s, 0 ≤ y i) {α β : ℝ} (hα : 0 < α) (hβ : 0 < β)
    (hαβ : α + β = 1) :
    ∑ i ∈ s, x i ^ α * y i ^ β ≤ (∑ i ∈ s, x i) ^ α * (∑ i ∈ s, y i) ^ β := by
  have h : ∑ i ∈ s, x i ^ α * y i ^ β
      ≤ (∑ i ∈ s, (x i ^ α) ^ α⁻¹) ^ (1 / α⁻¹) * (∑ i ∈ s, (y i ^ β) ^ β⁻¹) ^ (1 / β⁻¹) :=
    Real.inner_le_Lp_mul_Lq_of_nonneg s (Real.HolderConjugate.inv_inv hα hβ hαβ)
      (fun i hi => Real.rpow_nonneg (hx i hi) α) (fun i hi => Real.rpow_nonneg (hy i hi) β)
  have e1 : ∀ i ∈ s, (x i ^ α) ^ α⁻¹ = x i := fun i hi => by
    rw [← Real.rpow_mul (hx i hi), mul_inv_cancel₀ hα.ne', Real.rpow_one]
  have e2 : ∀ i ∈ s, (y i ^ β) ^ β⁻¹ = y i := fun i hi => by
    rw [← Real.rpow_mul (hy i hi), mul_inv_cancel₀ hβ.ne', Real.rpow_one]
  rwa [Finset.sum_congr rfl e1, Finset.sum_congr rfl e2, one_div, one_div, inv_inv, inv_inv] at h

/-- **Jensen's inequality for an exponential function.**  For weights `w_i ≥ 0` with sum `W`, real
numbers `e_i` with weighted mean `ē` (that is, `ē · W = ∑ w_i e_i`) and a base `c > 0`:
`c^ē · W ≤ ∑ w_i c^(e_i)`.  Each term is bounded from below by the tangent of `e ↦ c^e` at `ē`,
and the linear parts cancel in the sum. -/
theorem jensen_rpow {ι : Type*} (s : Finset ι) (w e : ι → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i) {c : ℝ}
    (hc : 0 < c) {W eb : ℝ} (hW : W = ∑ i ∈ s, w i) (heb : eb * W = ∑ i ∈ s, w i * e i) :
    c ^ eb * W ≤ ∑ i ∈ s, w i * c ^ e i := by
  have hterm : ∀ i ∈ s, w i * (c ^ eb * (1 + Real.log c * (e i - eb))) ≤ w i * c ^ e i := by
    intro i hi
    have h1 : c ^ e i = c ^ eb * c ^ (e i - eb) := by
      rw [← Real.rpow_add hc, add_sub_cancel]
    rw [h1, Real.rpow_def_of_pos hc (e i - eb)]
    exact mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left
      (by linarith [Real.add_one_le_exp (Real.log c * (e i - eb))])
      (Real.rpow_pos_of_pos hc _).le) (hw i hi)
  have e1 : ∑ i ∈ s, w i * (c ^ eb * (1 + Real.log c * (e i - eb))) = c ^ eb * W := by
    have h2 : ∀ i ∈ s, w i * (c ^ eb * (1 + Real.log c * (e i - eb)))
        = c ^ eb * ((1 - Real.log c * eb) * w i + Real.log c * (w i * e i)) := fun i _ => by ring
    rw [Finset.sum_congr rfl h2, ← Finset.mul_sum, Finset.sum_add_distrib, ← Finset.mul_sum,
      ← Finset.mul_sum, ← hW, ← heb]
    ring
  rw [← e1]
  exact Finset.sum_le_sum hterm

/-- `c = c^α c^β` for `c ≥ 0`, `α + β = 1`. -/
private theorem rpow_split {c α β : ℝ} (hc : 0 ≤ c) (hαβ : α + β = 1) : c = c ^ α * c ^ β := by
  rw [← Real.rpow_add' hc (by rw [hαβ]; exact one_ne_zero), hαβ, Real.rpow_one]

/-! ### The constant profile -/

/-- For a constant cut profile `ρ` each of the `q - 1` cut points carries the factor `ρ`:
`V_q(m; ρ) = ρ^(q-1) · T_{m,q}`.  This is the homogeneity `Vc_smul` of the sums for the
profile `1`. -/
private theorem Vc_const (ρ : ℝ) (q m : ℕ) : Vc (fun _ => ρ) q m = ρ ^ (q - 1) * Tq m q := by
  have h := Vc_smul (fun _ => (1 : ℝ)) ρ q m
  simp only [mul_one] at h
  exact h

/-! ### Log-convexity and reflection -/

/-- **Log-convexity of the composition sums in the cut profile.**  For profiles `a, b ≥ 0` on the
cut points and `α, β > 0` with `α + β = 1`: `V_q(m; a^α b^β) ≤ V_q(m; a)^α · V_q(m; b)^β`.  By
induction on the number of parts: the recursion on the last part writes the sum with `q + 2` parts
as a sum of products, each factor is bounded by the induction hypothesis, and Hölder's inequality
bounds the sum. -/
theorem Vc_rpow_mul_rpow_le {a b : ℕ → ℝ} {α β : ℝ} (hα : 0 < α) (hβ : 0 < β) (hαβ : α + β = 1) :
    ∀ (q m : ℕ), (∀ s ∈ Ioo 0 m, 0 ≤ a s) → (∀ s ∈ Ioo 0 m, 0 ≤ b s) →
      Vc (fun s => a s ^ α * b s ^ β) q m ≤ Vc a q m ^ α * Vc b q m ^ β
  | 0, m, _, _ => by
    simp only [Vc]
    exact mul_nonneg (Real.rpow_nonneg le_rfl _) (Real.rpow_nonneg le_rfl _)
  | 1, m, _, _ => by
    rw [Vc_one, Vc_one, Vc_one]
    exact le_of_eq (rpow_split (cay_nonneg m) hαβ)
  | q + 2, m, ha, hb => by
    have hsub : ∀ s ∈ Ioo 0 m, ∀ u ∈ Ioo 0 s, u ∈ Ioo 0 m := fun s hs u hu => by
      rw [mem_Ioo] at hs hu ⊢
      omega
    have hA : ∀ s ∈ Ioo 0 m, 0 ≤ Vc a (q + 1) s := fun s hs =>
      Vc_nonneg (fun u hu => ha u (hsub s hs u hu)) (q + 1)
    have hB : ∀ s ∈ Ioo 0 m, 0 ≤ Vc b (q + 1) s := fun s hs =>
      Vc_nonneg (fun u hu => hb u (hsub s hs u hu)) (q + 1)
    have hterm : ∀ s ∈ Ioo 0 m,
        Vc (fun s => a s ^ α * b s ^ β) (q + 1) s * (a s ^ α * b s ^ β) * cay (m - s)
          ≤ (Vc a (q + 1) s * a s * cay (m - s)) ^ α
            * (Vc b (q + 1) s * b s * cay (m - s)) ^ β := by
      intro s hs
      have h1 := Vc_rpow_mul_rpow_le hα hβ hαβ (q + 1) s (fun u hu => ha u (hsub s hs u hu))
        (fun u hu => hb u (hsub s hs u hu))
      have h2 : 0 ≤ a s ^ α * b s ^ β :=
        mul_nonneg (Real.rpow_nonneg (ha s hs) _) (Real.rpow_nonneg (hb s hs) _)
      rw [Real.mul_rpow (mul_nonneg (hA s hs) (ha s hs)) (cay_nonneg _),
        Real.mul_rpow (hA s hs) (ha s hs),
        Real.mul_rpow (mul_nonneg (hB s hs) (hb s hs)) (cay_nonneg _),
        Real.mul_rpow (hB s hs) (hb s hs)]
      calc Vc (fun s => a s ^ α * b s ^ β) (q + 1) s * (a s ^ α * b s ^ β) * cay (m - s)
          ≤ Vc a (q + 1) s ^ α * Vc b (q + 1) s ^ β * (a s ^ α * b s ^ β) * cay (m - s) :=
            mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right h1 h2) (cay_nonneg _)
        _ = Vc a (q + 1) s ^ α * Vc b (q + 1) s ^ β * (a s ^ α * b s ^ β)
              * (cay (m - s) ^ α * cay (m - s) ^ β) := by
            rw [← rpow_split (cay_nonneg _) hαβ]
        _ = Vc a (q + 1) s ^ α * a s ^ α * cay (m - s) ^ α
              * (Vc b (q + 1) s ^ β * b s ^ β * cay (m - s) ^ β) := by ring
    rw [Vc_succ_succ (fun s => a s ^ α * b s ^ β) q m, Vc_succ_succ a q m, Vc_succ_succ b q m]
    exact le_trans (Finset.sum_le_sum hterm) (sum_rpow_mul_rpow_le (Ioo 0 m) _ _
      (fun s hs => mul_nonneg (mul_nonneg (hA s hs) (ha s hs)) (cay_nonneg _))
      (fun s hs => mul_nonneg (mul_nonneg (hB s hs) (hb s hs)) (cay_nonneg _)) hα hβ hαβ)

/-- **Reflection.**  The weight `∏ a_part` of a composition does not change when the composition is
read backwards, so the profile may be reflected: `V_q(m; s ↦ f(m-s)) = V_q(m; f)`.  By induction on
the number of parts, with the recursion on the last part on one side and the recursion on the first
part (`Vc_first`) on the other. -/
theorem Vc_reverse : ∀ (q m : ℕ) (f : ℕ → ℝ), Vc (fun s => f (m - s)) q m = Vc f q m
  | 0, m, f => by simp [Vc]
  | 1, m, f => by rw [Vc_one, Vc_one]
  | q + 2, m, f => by
    rw [Vc_succ_succ (fun s => f (m - s)) q m, Vc_first f q m,
      sum_Ioo_reflect (fun g => cay g * f g * Vc (fun v => f (g + v)) (q + 1) (m - g)) 0 m,
      Nat.sub_zero]
    refine Finset.sum_congr rfl fun s hs => ?_
    have hs' := mem_Ioo.mp hs
    show Vc (fun u => f (m - u)) (q + 1) s * f (m - s) * cay (m - s)
      = cay (m - s) * f (m - s) * Vc (fun v => f (m - s + v)) (q + 1) (m - (m - s))
    have h1 : Vc (fun u => f (m - u)) (q + 1) s = Vc (fun v => f (m - s + v)) (q + 1) s := by
      rw [← Vc_reverse (q + 1) s (fun v => f (m - s + v))]
      refine Vc_congr (fun u hu => ?_) (q + 1)
      have hu' := mem_Ioo.mp hu
      show f (m - u) = f (m - s + (s - u))
      rw [show m - s + (s - u) = m - u by omega]
    rw [h1, show m - (m - s) = s by omega]
    ring

/-! ### The comparison of two profiles -/

/-- If `ρ ≥ 0` and `ρ² ≤ g(s) · g(m-s)` at every cut point, the constant profile `ρ` gives at most
the sum of `g`: the geometric mean of `g` and its reflection is at least `ρ`, and by log-convexity
and reflection its sum is at most the sum of `g`. -/
private theorem Vc_const_le_of_sq_le {g : ℕ → ℝ} {ρ : ℝ} {m : ℕ} (hρ : 0 ≤ ρ)
    (hg : ∀ s ∈ Ioo 0 m, 0 ≤ g s) (h : ∀ s ∈ Ioo 0 m, ρ ^ 2 ≤ g s * g (m - s)) (q : ℕ) :
    Vc (fun _ => ρ) q m ≤ Vc g q m := by
  have hgr : ∀ s ∈ Ioo 0 m, 0 ≤ g (m - s) := fun s hs =>
    hg _ (by rw [mem_Ioo] at hs ⊢; omega)
  have hpt : ∀ s ∈ Ioo 0 m, ρ ≤ g s ^ (1 / 2 : ℝ) * g (m - s) ^ (1 / 2 : ℝ) := fun s hs => by
    rw [← Real.mul_rpow (hg s hs) (hgr s hs), ← Real.sqrt_eq_rpow]
    exact Real.le_sqrt_of_sq_le (h s hs)
  have h2 := Vc_rpow_mul_rpow_le (a := g) (b := fun s => g (m - s)) (α := 1 / 2) (β := 1 / 2)
    (by norm_num) (by norm_num) (by norm_num) q m hg hgr
  rw [Vc_reverse q m g, ← rpow_split (Vc_nonneg hg q) (by norm_num)] at h2
  exact le_trans (Vc_mono (fun _ _ => hρ) hpt q) h2

/-- If `0 ≤ g ≤ w^β` on the cut points, with `w ≥ 0` and `0 < β < 1`, then
`V_q(m; g) ≤ T_{m,q}^(1-β) · V_q(m; w)^β`: log-convexity between the constant profile `1` and
`w`. -/
private theorem Vc_le_rpow_one_mul_rpow {g w : ℕ → ℝ} {β : ℝ} {m : ℕ} (hβ0 : 0 < β) (hβ1 : β < 1)
    (hg : ∀ s ∈ Ioo 0 m, 0 ≤ g s) (hw : ∀ s ∈ Ioo 0 m, 0 ≤ w s)
    (h : ∀ s ∈ Ioo 0 m, g s ≤ w s ^ β) (q : ℕ) :
    Vc g q m ≤ Tq m q ^ (1 - β) * Vc w q m ^ β := by
  have h1 : Vc g q m ≤ Vc (fun s => (fun _ : ℕ => (1 : ℝ)) s ^ (1 - β) * w s ^ β) q m := by
    refine Vc_mono hg (fun s hs => ?_) q
    show g s ≤ (1 : ℝ) ^ (1 - β) * w s ^ β
    rw [Real.one_rpow, one_mul]
    exact h s hs
  exact le_trans h1 (Vc_rpow_mul_rpow_le (a := fun _ : ℕ => (1 : ℝ)) (b := w) (α := 1 - β) (β := β)
    (by linarith) hβ0 (by ring) q m (fun _ _ => zero_le_one) hw)

/-- **The comparison of two profiles.**  Let `v_q ≥ 0` be weights, `g` and `w` nonnegative profiles
on the cut points of `m` with `g^(k+1) ≤ w^k`, `0 < ρ ≤ 1` with `ρ² ≤ g(s) · g(m-s)`, and `μ` a
bound for the mean of `q - 1` under the weights `v_q T_{m,q}`.  Then `X = ∑_q v_q V_q(m; g)` and
`Y = ∑_q v_q V_q(m; w)` satisfy `X^k ≤ ρ^(-μ) · Y^k`.

With `Z = ∑_q v_q T_{m,q}`, the same sum for the constant profile `1`: log-convexity gives
`X ≤ Z^(1/(k+1)) · Y^(k/(k+1))`, that is `X^(k+1) ≤ Z · Y^k`; the reflection gives
`X ≥ ∑_q v_q T_{m,q} ρ^(q-1)`, which by Jensen's inequality is at least `ρ^μ · Z`.  Together
`ρ^μ · X^(k+1) ≤ X · Y^k`. -/
theorem Vc_sum_pow_le {v g w : ℕ → ℝ} {m k : ℕ} {ρ μ : ℝ} (hk : 1 ≤ k)
    (hv : ∀ Q ∈ Icc 1 m, 0 ≤ v Q)
    (hg : ∀ s ∈ Ioo 0 m, 0 ≤ g s) (hw : ∀ s ∈ Ioo 0 m, 0 ≤ w s)
    (hgw : ∀ s ∈ Ioo 0 m, g s ^ (k + 1) ≤ w s ^ k)
    (hρ0 : 0 < ρ) (hρ1 : ρ ≤ 1)
    (hsym : ∀ s ∈ Ioo 0 m, ρ ^ 2 ≤ g s * g (m - s))
    (hpos : 0 < ∑ Q ∈ Icc 1 m, v Q * Tq m Q)
    (hμ : ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1) ≤ μ * ∑ Q ∈ Icc 1 m, v Q * Tq m Q) :
    (∑ Q ∈ Icc 1 m, v Q * Vc g Q m) ^ k
      ≤ ρ ^ (-μ) * (∑ Q ∈ Icc 1 m, v Q * Vc w Q m) ^ k := by
  obtain ⟨X, hX⟩ : ∃ X : ℝ, X = ∑ Q ∈ Icc 1 m, v Q * Vc g Q m := ⟨_, rfl⟩
  obtain ⟨Y, hY⟩ : ∃ Y : ℝ, Y = ∑ Q ∈ Icc 1 m, v Q * Vc w Q m := ⟨_, rfl⟩
  obtain ⟨Z, hZ⟩ : ∃ Z : ℝ, Z = ∑ Q ∈ Icc 1 m, v Q * Tq m Q := ⟨_, rfl⟩
  rw [← hX, ← hY]
  rw [← hZ] at hpos hμ
  have hk0 : (0 : ℝ) < k := by exact_mod_cast hk
  have hY0 : 0 ≤ Y := by
    rw [hY]
    exact Finset.sum_nonneg fun Q hQ => mul_nonneg (hv Q hQ) (Vc_nonneg hw Q)
  have hX0 : 0 ≤ X := by
    rw [hX]
    exact Finset.sum_nonneg fun Q hQ => mul_nonneg (hv Q hQ) (Vc_nonneg hg Q)
  -- log-convexity: `X^(k+1) ≤ Z · Y^k`
  obtain ⟨β, hβ⟩ : ∃ β : ℝ, β = (k : ℝ) / ((k : ℝ) + 1) := ⟨_, rfl⟩
  have hβ0 : 0 < β := by rw [hβ]; positivity
  have hβ1 : β < 1 := by rw [hβ, div_lt_one (by positivity)]; linarith
  have hpt : ∀ s ∈ Ioo 0 m, g s ≤ w s ^ β := by
    intro s hs
    have h2 : (w s ^ k) ^ (((k + 1 : ℕ) : ℝ)⁻¹) = w s ^ β := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul (hw s hs), hβ]
      congr 1
      push_cast
      ring
    rw [← Real.pow_rpow_inv_natCast (hg s hs) (Nat.succ_ne_zero k), ← h2]
    exact Real.rpow_le_rpow (pow_nonneg (hg s hs) _) (hgw s hs) (by positivity)
  have hH : X ≤ Z ^ (1 - β) * Y ^ β := by
    have hterm : ∀ Q ∈ Icc 1 m,
        v Q * Vc g Q m ≤ (v Q * Tq m Q) ^ (1 - β) * (v Q * Vc w Q m) ^ β := by
      intro Q hQ
      rw [Real.mul_rpow (hv Q hQ) (Tq_nonneg m Q), Real.mul_rpow (hv Q hQ) (Vc_nonneg hw Q)]
      calc v Q * Vc g Q m
          ≤ v Q * (Tq m Q ^ (1 - β) * Vc w Q m ^ β) :=
            mul_le_mul_of_nonneg_left (Vc_le_rpow_one_mul_rpow hβ0 hβ1 hg hw hpt Q) (hv Q hQ)
        _ = (v Q ^ (1 - β) * v Q ^ β) * (Tq m Q ^ (1 - β) * Vc w Q m ^ β) := by
            rw [← rpow_split (hv Q hQ) (by ring)]
        _ = v Q ^ (1 - β) * Tq m Q ^ (1 - β) * (v Q ^ β * Vc w Q m ^ β) := by ring
    rw [hX, hZ, hY]
    exact le_trans (Finset.sum_le_sum hterm) (sum_rpow_mul_rpow_le (Icc 1 m) _ _
      (fun Q hQ => mul_nonneg (hv Q hQ) (Tq_nonneg m Q))
      (fun Q hQ => mul_nonneg (hv Q hQ) (Vc_nonneg hw Q)) (by linarith) hβ0 (by ring))
  have hpow : X ^ (k + 1) ≤ Z * Y ^ k := by
    have h1 : X ^ (k + 1) ≤ (Z ^ (1 - β) * Y ^ β) ^ (k + 1) := pow_le_pow_left₀ hX0 hH (k + 1)
    have e1 : (Z ^ (1 - β)) ^ (k + 1) = Z := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul hpos.le,
        show (1 - β) * ((k + 1 : ℕ) : ℝ) = 1 by rw [hβ]; push_cast; field_simp; ring,
        Real.rpow_one]
    have e2 : (Y ^ β) ^ (k + 1) = Y ^ k := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul hY0,
        show β * ((k + 1 : ℕ) : ℝ) = (k : ℝ) by rw [hβ]; push_cast; field_simp,
        Real.rpow_natCast]
    rwa [mul_pow, e1, e2] at h1
  -- reflection and Jensen: `ρ^μ · Z ≤ X`
  have hJ : ρ ^ μ * Z ≤ X := by
    obtain ⟨μb, hμb⟩ : ∃ μb : ℝ, μb = (∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1)) / Z :=
      ⟨_, rfl⟩
    have hμb1 : μb * Z = ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1) := by
      rw [hμb, div_mul_cancel₀ _ hpos.ne']
    have hμb2 : μb ≤ μ := by rwa [hμb, div_le_iff₀ hpos]
    have hsymm : ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ρ ^ ((Q : ℝ) - 1) ≤ X := by
      rw [hX]
      refine Finset.sum_le_sum fun Q hQ => ?_
      have h1 := Vc_const_le_of_sq_le hρ0.le hg hsym Q
      rw [Vc_const ρ Q m] at h1
      have e : ρ ^ ((Q : ℝ) - 1) = ρ ^ (Q - 1) := by
        rw [← Real.rpow_natCast, Nat.cast_sub (mem_Icc.mp hQ).1, Nat.cast_one]
      calc v Q * Tq m Q * ρ ^ ((Q : ℝ) - 1) = v Q * (ρ ^ (Q - 1) * Tq m Q) := by rw [e]; ring
        _ ≤ v Q * Vc g Q m := mul_le_mul_of_nonneg_left h1 (hv Q hQ)
    calc ρ ^ μ * Z
        ≤ ρ ^ μb * Z :=
          mul_le_mul_of_nonneg_right (Real.rpow_le_rpow_of_exponent_ge hρ0 hρ1 hμb2) hpos.le
      _ ≤ ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ρ ^ ((Q : ℝ) - 1) :=
          jensen_rpow (Icc 1 m) (fun Q => v Q * Tq m Q) (fun Q => (Q : ℝ) - 1)
            (fun Q hQ => mul_nonneg (hv Q hQ) (Tq_nonneg m Q)) hρ0 hZ hμb1
      _ ≤ X := hsymm
  -- together
  have hρμ : 0 < ρ ^ μ := Real.rpow_pos_of_pos hρ0 μ
  have hXpos : 0 < X := lt_of_lt_of_le (mul_pos hρμ hpos) hJ
  have h6 : ρ ^ μ * X ^ k ≤ Y ^ k := by
    refine le_of_mul_le_mul_left ?_ hXpos
    calc X * (ρ ^ μ * X ^ k) = ρ ^ μ * X ^ (k + 1) := by ring
      _ ≤ ρ ^ μ * (Z * Y ^ k) := mul_le_mul_of_nonneg_left hpow hρμ.le
      _ = (ρ ^ μ * Z) * Y ^ k := by ring
      _ ≤ X * Y ^ k := mul_le_mul_of_nonneg_right hJ (pow_nonneg hY0 k)
  calc X ^ k = ρ ^ (-μ) * (ρ ^ μ * X ^ k) := by
        rw [← mul_assoc, ← Real.rpow_add hρ0, neg_add_cancel, Real.rpow_zero, one_mul]
    _ ≤ ρ ^ (-μ) * Y ^ k := mul_le_mul_of_nonneg_left h6 (Real.rpow_pos_of_pos hρ0 _).le

end Parking
