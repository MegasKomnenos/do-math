module

public import Parking.Cayley.TreeSeries
public import Parking.NextColumn.Frozen
public import Batteries.Tactic.OpenPrivate
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
import all Parking.NextColumn.Compositions
import all Parking.NextColumn.Frozen

/-!
# Volterra equations with the Cayley kernel

Write `a_m = cay m = m^{m-1}/m!` and `ren m = m^m/m!`.  Several sequences of the curve increase
satisfy an equation of the form

`u(M) = κ(M) + ∑_{a<t<M} cay (M-t) · w(t) · u(t)`,

in which the unknown at `M` is expressed by its values below `M` through the kernel `cay (M-t)`.
The lower limit `a` of the sum is a natural number, named as in the Lean statements; where it
occurs the kernel is written `cay`, and `a_m` elsewhere.  The equation holds for the total weight
`Lam f` of the compositions (remove the last part; `κ = cay`, `w = f`, `a = 0`), for the sequence
`ren` itself (`κ = cay`, `w = 1`, `a = 0`), and for the environment of a column in the rows up to
`2k`.  Here `A n l` is the number of parking functions of length `n` with all displacements at
most `l`, and the environment of the column `k` is the sequence `zr k n = A n (k-1)/n!`; the first
layer of the column, the rows `k + 1 ≤ n ≤ 2k - 1`, lies among these rows.  This module collects
what follows from the form of the equation alone.

* `ren_last` : `ren m = a_m + ∑_{0<s<m} a_{m-s} · ren s`.  So `ren` is the resolvent of the kernel:
  a convolution with `cay` applied again and again sums to a convolution with `ren`
  (`cay_conv_ren`).
* `Lam_defect` : the *first violating point* identity
  `ren m - Lam f m = ∑_{0<s<m} ren (m-s) · (1 - f s) · Lam f s`, and with it `Lam_one`: for the
  constant profile `1` the total weight of the compositions of `m` is `ren m`.
* `volterra_tangent` : if the weights are `w(t) = e^{-x(t)}` and `r` solves the equation without
  weights, then for every real `μ`
  `e^{-μ} · ((1+μ) · r(M) - ∑_{a<t<M} ren (M-t) · r(t) · x(t)) ≤ u(M)`.
  This is Jensen's inequality for the weights `e^{-x}` in tangent form: `u(M)/r(M)` is an average
  of products of the weights, `e^{-X} ≥ e^{-μ}(1 + μ - X)` for every `μ`, and the sum on the left
  is `r(M)` times the average of the exponent `X`.  Taking `μ` equal to that average gives Jensen's
  inequality itself (`jensen_of_tangent`).
* `Lam_tangent`, `Lam_jensen` : the two forms for `u = Lam (e^{-x})`, `r = ren`.
* `zr_jensen` : Jensen's inequality for the environment `zr k n = A n (k-1)/n!` of a column in the
  rows `n ≤ 2k`, written with `M = n + 1`: for `1 ≤ M ≤ 2k+1`,
  `a_M · exp (-(∑_{k<t<M} ren (M-t) · a_t · log (t/k)) / a_M) ≤ zr k (M-1)`.  In these rows the
  environment solves `zr k (M-1) = κ_k(M) + ∑_{k<t<M} a_{M-t} · (k/t) · zr k (t-1)` with
  `κ_k = kap k` (`zr_volterra`, a private lemma of `Parking.NextColumn.Frozen`); the weights are
  `k/t = e^{-log (t/k)}`, and without them the equation is solved by `a_M`, by the definition of
  `κ_k`.
-/

@[expose] public section

namespace Parking

open Finset

open private sum_Ioo_shift from Parking.NextColumn.Compositions
open private sum_Ioo_reflect zr_volterra from Parking.NextColumn.Frozen

/-! ### The renewal sequence as the resolvent of the kernel -/

/-- Last-part recursion of the renewal sequence: `ren m = a_m + ∑_{0<s<m} a_{m-s} · ren s`.  It is
the renewal identity `ren_conv` (`Parking.Cayley.TreeSeries`), read from the other end. -/
private theorem ren_last {m : ℕ} (hm : 1 ≤ m) :
    ren m = cay m + ∑ s ∈ Ioo 0 m, cay (m - s) * ren s := by
  have h0 : ∑ j ∈ Ioo 0 m, cay j * ren (m - j) = ∑ j ∈ range m, cay j * ren (m - j) := by
    refine Finset.sum_subset (fun c hc => mem_range.2 (mem_Ioo.1 hc).2) fun c hc hc' => ?_
    rw [mem_range] at hc
    rw [mem_Ioo] at hc'
    rw [show c = 0 by omega]
    simp
  have h := ren_conv hm
  rw [Finset.sum_range_succ, Nat.sub_self, show ren 0 = 1 by simp [ren], mul_one, ← h0,
    sum_Ioo_reflect _ 0 m, Nat.sub_zero] at h
  rw [← h, add_comm]
  congr 1
  refine Finset.sum_congr rfl fun s hs => ?_
  rw [mem_Ioo] at hs
  rw [show m - (m - s) = s by omega]

/-- A convolution with the kernel `cay`, applied to `g` and to the `ren`-convolution of `g`, is the
`ren`-convolution of `g`:
`∑_{a<t<M} cay (M-t) · (g(t) + ∑_{a<c<t} ren (t-c) · g(c)) = ∑_{a<c<M} ren (M-c) · g(c)`,
for every lower limit `a`.  Exchange the two sums and apply `ren_last` at `M - c`. -/
private theorem cay_conv_ren (g : ℕ → ℝ) (a M : ℕ) :
    ∑ t ∈ Ioo a M, cay (M - t) * (g t + ∑ c ∈ Ioo a t, ren (t - c) * g c)
      = ∑ c ∈ Ioo a M, ren (M - c) * g c := by
  have h1 : ∀ t ∈ Ioo a M, cay (M - t) * (g t + ∑ c ∈ Ioo a t, ren (t - c) * g c)
      = cay (M - t) * g t + ∑ c ∈ Ioo a t, g c * (cay (M - t) * ren (t - c)) := by
    intro t _
    rw [mul_add, Finset.mul_sum]
    congr 1
    exact Finset.sum_congr rfl fun c _ => by ring
  have h2 : ∑ t ∈ Ioo a M, ∑ c ∈ Ioo a t, g c * (cay (M - t) * ren (t - c))
      = ∑ c ∈ Ioo a M, ∑ t ∈ Ioo c M, g c * (cay (M - t) * ren (t - c)) :=
    Finset.sum_comm' (by intro t c; simp only [mem_Ioo]; omega)
  rw [Finset.sum_congr rfl h1, Finset.sum_add_distrib, h2, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun c hc => ?_
  rw [mem_Ioo] at hc
  rw [← Finset.mul_sum, sum_Ioo_shift _ c M, ren_last (show 1 ≤ M - c by omega)]
  have h3 : ∑ s ∈ Ioo 0 (M - c), cay (M - (c + s)) * ren (c + s - c)
      = ∑ s ∈ Ioo 0 (M - c), cay (M - c - s) * ren s :=
    Finset.sum_congr rfl fun s _ => by
      rw [show M - (c + s) = M - c - s by omega, show c + s - c = s by omega]
  rw [h3]
  ring

/-- **First violating point.** For every cut profile `f`,
`ren m - Lam f m = ∑_{0<s<m} ren (m-s) · (1 - f s) · Lam f s`.  In a composition weighted with the
profile `1` in the place of `f`, let `s` be the first cut point at which the factor `1 - f s` is
chosen; below `s` the profile is `f`, above it the profile is `1`.  Formally the difference
`w = ren - Lam f` satisfies `w(m) = ∑_s a_{m-s} · (g(s) + w(s))` with `g = (1 - f) · Lam f`, by the
last-part recursions of `ren` and `Lam`, and `cay_conv_ren` resolves this equation by induction. -/
theorem Lam_defect (f : ℕ → ℝ) {m : ℕ} (hm : 1 ≤ m) :
    ren m - Lam f m = ∑ s ∈ Ioo 0 m, ren (m - s) * ((1 - f s) * Lam f s) := by
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    refine Eq.trans ?_ (cay_conv_ren (fun s => (1 - f s) * Lam f s) 0 m)
    rw [ren_last hm, Lam_last f m, add_sub_add_left_eq_sub, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun s hs => ?_
    rw [mem_Ioo] at hs
    rw [← ih s hs.2 (by omega)]
    ring

/-- For the constant cut profile `1` the total weight of the compositions of `m ≥ 1` is `ren m`:
the defect of `Lam_defect` vanishes. -/
theorem Lam_one {m : ℕ} (hm : 1 ≤ m) : Lam (fun _ => (1 : ℝ)) m = ren m := by
  have h := Lam_defect (fun _ => (1 : ℝ)) hm
  simp only [sub_self, zero_mul, mul_zero, Finset.sum_const_zero] at h
  linarith

/-! ### Jensen's inequality in tangent form -/

/-- `e^{-μ}(1+μ) ≤ 1` for every real `μ`. -/
private theorem exp_neg_mul_one_add_le (μ : ℝ) : Real.exp (-μ) * (1 + μ) ≤ 1 := by
  have h := mul_le_mul_of_nonneg_left (Real.add_one_le_exp μ) (Real.exp_pos (-μ)).le
  rw [← Real.exp_add, neg_add_cancel, Real.exp_zero] at h
  linarith

/-- Linearity of a finite sum, in the form the tangent inequality uses. -/
private theorem sum_tangent_lin (S : Finset ℕ) (c p q : ℕ → ℝ) (E ν : ℝ) :
    ∑ t ∈ S, E * (c t * ((1 + ν) * p t - q t))
      = E * ((1 + ν) * ∑ t ∈ S, c t * p t - ∑ t ∈ S, c t * q t) := by
  rw [Finset.mul_sum, ← Finset.sum_sub_distrib, Finset.mul_sum]
  exact Finset.sum_congr rfl fun t _ => by ring

/-- **Tangent inequality for a Volterra equation with the Cayley kernel.** Let `κ ≥ 0`, let `r`
solve `r(M) = κ(M) + ∑_{a<t<M} cay (M-t) · r(t)` and `u` solve the same equation with the weights
`e^{-x(t)}`, `u(M) = κ(M) + ∑_{a<t<M} cay (M-t) · e^{-x(t)} · u(t)`, for `1 ≤ M ≤ B`; the lower
limit `a` of the sums is a natural number.  Then for every real `μ` and `1 ≤ M ≤ B`,
`e^{-μ} · ((1+μ) · r(M) - ∑_{a<t<M} ren (M-t) · r(t) · x(t)) ≤ u(M)`.

The proof is an induction on `M` for all `μ` at once.  In the equation of `u`, the term `κ(M)` is at
least `e^{-μ}(1+μ) · κ(M)`, and the induction hypothesis is used at `t` with the parameter
`μ - x(t)`, so that `e^{-x(t)} · e^{-(μ - x(t))} = e^{-μ}`.  The sums of the exponents that arise
recombine by `cay_conv_ren`. -/
theorem volterra_tangent {a B : ℕ} {κ r u x : ℕ → ℝ}
    (hκ : ∀ M, 1 ≤ M → M ≤ B → 0 ≤ κ M)
    (hr : ∀ M, 1 ≤ M → M ≤ B → r M = κ M + ∑ t ∈ Ioo a M, cay (M - t) * r t)
    (hu : ∀ M, 1 ≤ M → M ≤ B →
      u M = κ M + ∑ t ∈ Ioo a M, cay (M - t) * (Real.exp (-(x t)) * u t))
    (μ : ℝ) {M : ℕ} (hM1 : 1 ≤ M) (hM : M ≤ B) :
    Real.exp (-μ) * ((1 + μ) * r M - ∑ t ∈ Ioo a M, ren (M - t) * (r t * x t)) ≤ u M := by
  have key : ∀ M, 1 ≤ M → M ≤ B → ∀ ν : ℝ,
      Real.exp (-ν) * ((1 + ν) * r M - ∑ t ∈ Ioo a M, ren (M - t) * (r t * x t)) ≤ u M := by
    intro M
    induction M using Nat.strong_induction_on with
    | _ M ih =>
      intro hM1 hM ν
      -- one term of the equation of `u`, bounded by the induction hypothesis at `ν - x t`
      have hterm : ∀ t ∈ Ioo a M,
          Real.exp (-ν) * (cay (M - t) * ((1 + ν) * r t
              - (r t * x t + ∑ c ∈ Ioo a t, ren (t - c) * (r c * x c))))
            ≤ cay (M - t) * (Real.exp (-(x t)) * u t) := by
        intro t ht
        rw [mem_Ioo] at ht
        have hih := ih t ht.2 (by omega) (by omega) (ν - x t)
        have hsplit : Real.exp (-ν) = Real.exp (-(x t)) * Real.exp (-(ν - x t)) := by
          rw [← Real.exp_add]
          congr 1
          ring
        calc Real.exp (-ν) * (cay (M - t) * ((1 + ν) * r t
                - (r t * x t + ∑ c ∈ Ioo a t, ren (t - c) * (r c * x c))))
            = cay (M - t) * (Real.exp (-(x t)) * (Real.exp (-(ν - x t))
                * ((1 + (ν - x t)) * r t - ∑ c ∈ Ioo a t, ren (t - c) * (r c * x c)))) := by
              rw [hsplit]
              ring
          _ ≤ cay (M - t) * (Real.exp (-(x t)) * u t) :=
              mul_le_mul_of_nonneg_left
                (mul_le_mul_of_nonneg_left hih (Real.exp_pos _).le) (cay_nonneg _)
      calc Real.exp (-ν) * ((1 + ν) * r M - ∑ t ∈ Ioo a M, ren (M - t) * (r t * x t))
          = Real.exp (-ν) * (1 + ν) * κ M
            + ∑ t ∈ Ioo a M, Real.exp (-ν) * (cay (M - t) * ((1 + ν) * r t
                - (r t * x t + ∑ c ∈ Ioo a t, ren (t - c) * (r c * x c)))) := by
            rw [sum_tangent_lin, cay_conv_ren (fun t => r t * x t) a M, hr M hM1 hM]
            ring
        _ ≤ κ M + ∑ t ∈ Ioo a M, cay (M - t) * (Real.exp (-(x t)) * u t) :=
            add_le_add (mul_le_of_le_one_left (hκ M hM1 hM) (exp_neg_mul_one_add_le ν))
              (Finset.sum_le_sum hterm)
        _ = u M := (hu M hM1 hM).symm
  exact key M hM1 hM μ

/-- **From the tangent form to Jensen's inequality.** If `e^{-μ} · ((1+μ) · r - S) ≤ u` for every
real `μ` and `r > 0`, then `r · e^{-S/r} ≤ u`: take `μ = S/r`. -/
private theorem jensen_of_tangent {r S u : ℝ} (hr : 0 < r)
    (h : ∀ μ : ℝ, Real.exp (-μ) * ((1 + μ) * r - S) ≤ u) : r * Real.exp (-(S / r)) ≤ u := by
  have h1 := h (S / r)
  have e : (1 + S / r) * r - S = r := by
    field_simp
    ring
  rwa [e, mul_comm] at h1

/-- **Tangent inequality for the chain sums.** For a cut profile `e^{-x(s)}` and every real `μ`,
`e^{-μ} · ((1+μ) · ren m - ∑_{0<c<m} ren (m-c) · ren c · x(c)) ≤ Lam (e^{-x}) m`.  This is
`volterra_tangent` for the last-part recursions of `Lam` and of `ren`. -/
theorem Lam_tangent (x : ℕ → ℝ) (μ : ℝ) {m : ℕ} (hm : 1 ≤ m) :
    Real.exp (-μ) * ((1 + μ) * ren m - ∑ c ∈ Ioo 0 m, ren (m - c) * (ren c * x c))
      ≤ Lam (fun s => Real.exp (-(x s))) m := by
  refine volterra_tangent (B := m) (κ := cay) (fun M _ _ => cay_nonneg M)
    (fun M hM1 _ => ren_last hM1) (fun M _ _ => ?_) μ hm le_rfl
  rw [Lam_last]
  congr 1
  exact Finset.sum_congr rfl fun s _ => by ring

/-- **Jensen's inequality for the chain sums.** For a cut profile `e^{-x(s)}`,
`ren m · exp (-(∑_{0<c<m} ren (m-c) · ren c · x(c)) / ren m) ≤ Lam (e^{-x}) m`: the total weight is
at least the weight for the profile `1` times the exponential of minus the mean total exponent. -/
theorem Lam_jensen (x : ℕ → ℝ) {m : ℕ} (hm : 1 ≤ m) :
    ren m * Real.exp (-((∑ c ∈ Ioo 0 m, ren (m - c) * (ren c * x c)) / ren m))
      ≤ Lam (fun s => Real.exp (-(x s))) m :=
  jensen_of_tangent (ren_pos m) fun μ => Lam_tangent x μ hm

/-! ### The environment of a column in the rows up to `2k` -/

/-- **Jensen's inequality for the environment.** For `k ≥ 1` and `1 ≤ M ≤ 2k+1`, that is, in the
rows `n = M - 1 ≤ 2k`,
`a_M · exp (-(∑_{k<t<M} ren (M-t) · a_t · log (t/k)) / a_M) ≤ zr k (M-1)`.  The environment solves
the Volterra equation `zr_volterra` with the weights `k/t = e^{-log (t/k)}`, and `a_M` solves
the same equation without weights, so `volterra_tangent` applies; the tangent parameter is then
set to the mean exponent. -/
theorem zr_jensen {k : ℕ} (hk : 1 ≤ k) {M : ℕ} (hM1 : 1 ≤ M) (hM2 : M ≤ 2 * k + 1) :
    cay M * Real.exp (-((∑ t ∈ Ioo k M, ren (M - t) * (cay t * Real.log ((t : ℝ) / k))) / cay M))
      ≤ zr k (M - 1) := by
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  refine jensen_of_tangent (cay_pos (by omega)) fun μ =>
    volterra_tangent (a := k) (B := 2 * k + 1) (κ := kap k) (r := cay)
      (u := fun M => zr k (M - 1)) (x := fun t => Real.log ((t : ℝ) / k))
      (fun M h1 h2 => (kap_pos h1 h2).le) (fun M _ _ => ?_) (fun M h1 h2 => ?_) μ hM1 hM2
  · have h : ∑ i ∈ Ioo k M, cay i * cay (M - i) = ∑ t ∈ Ioo k M, cay (M - t) * cay t :=
      Finset.sum_congr rfl fun t _ => mul_comm _ _
    unfold kap
    linarith
  · obtain ⟨n, rfl⟩ : ∃ n, M = n + 1 := ⟨M - 1, by omega⟩
    show zr k (n + 1 - 1) = kap k (n + 1) + ∑ t ∈ Ioo k (n + 1),
      cay (n + 1 - t) * (Real.exp (-(Real.log ((t : ℝ) / k))) * zr k (t - 1))
    rw [Nat.add_sub_cancel, zr_volterra hk le_rfl (by omega) (by omega)]
    congr 1
    refine Finset.sum_congr rfl fun t ht => ?_
    have ht0 : (0 : ℝ) < t := Nat.cast_pos.mpr (by rw [mem_Ioo] at ht; omega)
    rw [Real.exp_neg, Real.exp_log (div_pos ht0 hk0), inv_div, mul_assoc]

end Parking
