module

public import Parking.NextColumn.FirstCell
public import Staircase.Cayley.MarkedCuts
public import Staircase.Diagonal.Profiles
public import Batteries.Tactic.OpenPrivate
public import Mathlib.Analysis.Convex.SpecificFunctions.Basic
import all Parking.NextColumn.FirstCell
import all Parking.NextColumn.Frozen
import all Parking.NextColumn.Compositions

/-!
# The boundary term along the diagonal

The boundary term of a step `d(n,k)` in the first layer, `n = k + r`, is
`a_k/k · Λ_q(k-1; k+q)` with `q = r + 1`, where `Λ_q(y;N) = Lam (thr y N) q` is the chain sum for
the profile `s ↦ y/(N-s)`.  One step along the diagonal raises the threshold and the size by one
each.  This module proves that the chain sum gains a definite factor:

`(1+x)^(E₀) · Λ_q(k-1; k+q) ≤ Λ_q(k; k+q+1)`,
`x = q/((k-1)(k+q))`,  `E₀ = (q+2)/(2q) · μ₀(q, q²/(k-1))`   (`Lam_gain`),

where `μ₀(r, X) = (√((4+X)² + 12(r-1)) - (4+X))/3` is the function `mu0`.

## Compositions as sets of cut points

A composition of `r` is determined by its set of cut points `S ⊆ {1, …, r-1}`.  For a cut profile
`f` its weight is `W_f(S) = ∏ a_part · ∏_{s ∈ S} f s`, where `a = cay` and the parts are the gaps
between consecutive points of `{0} ∪ S ∪ {r}`.  The module `Parking.NextColumn.FirstCell` has this
representation, where it is private, and it is opened here: the weight `FirstCell.Wt f r S`; the
product `FirstCell.gs` of the weights of the parts, computed by a scan of the positions from left
to right, and its log-supermodularity in the cut set (`FirstCell.gs_lattice`), which rests on the
log-convexity of the numbers `a_j`; and the sum of the weights of all cut sets,
`∑_S W_f(S) = Lam f r` (`FirstCell.sum_Wt`).  Two statements are added to it.

* `sum_cutWt_mem` : the cut sets that contain a given point `s` have the total weight
  `Lam f s · f s · Lam (f (s + ·)) (r - s)`; a composition with a cut at `s` is a composition of `s`
  followed by a composition of `r - s`.
* `cutWt_fkg` : for two profiles `0 ≤ g ≤ f` on the cut points and a nonnegative function `F` of
  the cut set that is monotone for inclusion, the mean of `F` under the weights of `g` is at most
  its mean under the weights of `f`.  This is the FKG inequality; it follows from the four
  functions theorem, because the weight of the parts is log-supermodular in the cut set.  The
  hypotheses are asked on the cut points only, since the profiles of the chain sums are negative
  beyond them.

## The gain

* The new profile `λ'_s = k/(k+q+1-s)` exceeds the old one `λ_s = (k-1)/(k+q-s)` by a factor that
  depends on the cut point: `λ'_s ≥ λ_s · (1+x)^((q+1-s)/q)` (`profile_gain`).  So the weight of a
  cut set `S` gains at least the factor `(1+x)^(U(S)/q)` with `U(S) = ∑_{s ∈ S} (q+1-s)`.
* By Jensen's inequality the mean of `(1+x)^(U/q)` under the weights of `λ` is at least `(1+x)` to
  the power of the mean of `U/q`.
* `U` is monotone in the cut set and `λ ≥ ρ = (k-1)/(k-1+q)`, so by the FKG inequality the mean of
  `U` under `λ` is at least its mean under the constant profile `ρ`.
* For a constant profile the reflection `s ↦ q - s` leaves the weights unchanged and turns `U`
  into `∑_{s ∈ S} (s+1)`, so the mean of `U` is `(q+2)/2` times `μ_q(ρ) = muh q ρ`, the mean
  number of cuts of a composition of `q` under the weights of the constant profile `ρ`
  (`sum_cutWt_const_stat`), and `μ_q(ρ) ≥ μ₀(q, q(1/ρ - 1))` is `mu0_le_muh`
  (`Parking.NextColumn.BirthdayIneq`).
-/

@[expose] public section

namespace Parking

open Finset

open private FirstCell.gs FirstCell.gs_zero FirstCell.gs_succ FirstCell.gs_nonneg
  FirstCell.gs_insert_of_lt FirstCell.gs_lattice FirstCell.Zs FirstCell.Zs_eq_Lam FirstCell.Wt
  FirstCell.sum_Wt FirstCell.Ioo_zero_eq_Ico_one from Parking.NextColumn.FirstCell
open private sum_Ioo_reflect from Parking.NextColumn.Frozen
open private Vc_smul from Parking.NextColumn.Compositions

/-! ### The weight of a cut set -/

/-- The weight of a cut set is nonnegative when the profile is nonnegative at its points. -/
private theorem cutWt_nonneg {f : ℕ → ℝ} {S : Finset ℕ} (hf : ∀ s ∈ S, 0 ≤ f s) (r : ℕ) :
    0 ≤ FirstCell.Wt f r S :=
  mul_nonneg (FirstCell.gs_nonneg _ _ _ _) (Finset.prod_nonneg hf)

/-- If every cut point `t` of `S` carries a factor `c t` with `0 ≤ f t · c t ≤ g t`, then the weight
of `S` for the profile `f`, multiplied by these factors, is at most its weight for `g`: the weight
of the parts is the same on both sides. -/
private theorem cutWt_mul_prod_le {f g c : ℕ → ℝ} {S : Finset ℕ} (h0 : ∀ t ∈ S, 0 ≤ f t * c t)
    (h : ∀ t ∈ S, f t * c t ≤ g t) (r : ℕ) :
    FirstCell.Wt f r S * ∏ t ∈ S, c t ≤ FirstCell.Wt g r S := by
  show FirstCell.gs S (r - 1) 1 0 * (∏ s ∈ S, f s) * ∏ t ∈ S, c t
    ≤ FirstCell.gs S (r - 1) 1 0 * ∏ s ∈ S, g s
  rw [mul_assoc, ← Finset.prod_mul_distrib]
  exact mul_le_mul_of_nonneg_left (Finset.prod_le_prod₀ h0 h) (FirstCell.gs_nonneg _ _ _ _)

/-! ### The cut sets through a given point -/

/-- One step of the scan for a sum over the cut sets `S ⊆ [p, r)` with an additional factor `h S`:
the position `p` either is not a cut, or it is one, and then the part from the base point to `p`
is complete. -/
private theorem sum_powerset_scan (f : ℕ → ℝ) (h : Finset ℕ → ℝ) (r n p x : ℕ) (hp : p < r) :
    ∑ S ∈ (Ico p r).powerset, FirstCell.gs S (n + 1) p x * (∏ t ∈ S, f t) * h S
      = ∑ S ∈ (Ico (p + 1) r).powerset, FirstCell.gs S n (p + 1) x * (∏ t ∈ S, f t) * h S
        + cay (p - x) * f p
          * ∑ S ∈ (Ico (p + 1) r).powerset,
              FirstCell.gs S n (p + 1) p * (∏ t ∈ S, f t) * h (insert p S) := by
  have hnot : p ∉ Ico (p + 1) r := by simp
  have hins : Ico p r = insert p (Ico (p + 1) r) := by
    ext a
    simp only [mem_Ico, mem_insert]
    omega
  rw [hins, Finset.sum_powerset_insert hnot, Finset.mul_sum]
  congr 1 <;> refine Finset.sum_congr rfl fun S hS => ?_
  · rw [FirstCell.gs_succ, ite_eq_right (fun h' => hnot (mem_powerset.mp hS h'))]
  · rw [FirstCell.gs_succ, ite_eq_left (mem_insert_self p S),
      Finset.prod_insert (fun h' => hnot (mem_powerset.mp hS h')),
      FirstCell.gs_insert_of_lt (Nat.lt_add_one p) S n p]
    ring

/-- One step of the scan for the total weight `FirstCell.Zs` of the cut sets of `[p, r)`. -/
private theorem scanSum_step (f : ℕ → ℝ) {r p : ℕ} (n x : ℕ) (hp : p < r) :
    FirstCell.Zs f r (n + 1) p x
      = FirstCell.Zs f r n (p + 1) x + cay (p - x) * f p * FirstCell.Zs f r n (p + 1) p := by
  have h := sum_powerset_scan f (fun _ => 1) r n p x hp
  simp only [mul_one] at h
  exact h

/-- The cut sets `S ⊆ [p, r)` that contain the point `s`: their total weight splits at `s` into
the weight of the cut sets of `[p, s)` and the weight of the cut sets of `[s + 1, r)` scanned from
the base point `s`. -/
private theorem scanSum_mem (f : ℕ → ℝ) (r s : ℕ) (hsr : s < r) : ∀ n p x, p + n = r → p ≤ s →
    ∑ S ∈ (Ico p r).powerset,
        FirstCell.gs S n p x * (∏ t ∈ S, f t) * (if s ∈ S then (1 : ℝ) else 0)
      = FirstCell.Zs f s (s - p) p x * f s * FirstCell.Zs f r (r - s - 1) (s + 1) s
  | 0, p, x, hp, hps => by omega
  | n + 1, p, x, hp, hps => by
    have hmem : ∀ S ∈ (Ico (p + 1) r).powerset, p ∉ S := fun S hS h' => by
      have := mem_Ico.mp (mem_powerset.mp hS h')
      omega
    rw [sum_powerset_scan f _ r n p x (by omega)]
    rcases Nat.eq_or_lt_of_le hps with heq | hlt
    · -- the scan is at the marked point
      subst heq
      have hA : ∑ S ∈ (Ico (p + 1) r).powerset,
          FirstCell.gs S n (p + 1) x * (∏ t ∈ S, f t) * (if p ∈ S then (1 : ℝ) else 0) = 0 :=
        Finset.sum_eq_zero fun S hS => by rw [ite_eq_right (hmem S hS), mul_zero]
      have hB : ∑ S ∈ (Ico (p + 1) r).powerset,
          FirstCell.gs S n (p + 1) p * (∏ t ∈ S, f t)
            * (if p ∈ insert p S then (1 : ℝ) else 0)
          = FirstCell.Zs f r n (p + 1) p :=
        Finset.sum_congr rfl fun S _ => by rw [ite_eq_left (mem_insert_self p S), mul_one]
      have hZ0 : FirstCell.Zs f p (p - p) p x = cay (p - x) := by
        show ∑ S ∈ (Ico p p).powerset, FirstCell.gs S (p - p) p x * ∏ t ∈ S, f t = cay (p - x)
        rw [Nat.sub_self, Finset.Ico_self, Finset.powerset_empty, Finset.sum_singleton,
          FirstCell.gs_zero, Finset.prod_empty, mul_one]
      rw [hA, hB, hZ0, show r - p - 1 = n by omega, zero_add]
    · -- the marked point lies to the right
      have hB : ∀ S ∈ (Ico (p + 1) r).powerset,
          FirstCell.gs S n (p + 1) p * (∏ t ∈ S, f t)
              * (if s ∈ insert p S then (1 : ℝ) else 0)
            = FirstCell.gs S n (p + 1) p * (∏ t ∈ S, f t) * (if s ∈ S then (1 : ℝ) else 0) :=
        fun S _ => by
          have hne : s ≠ p := by omega
          simp only [mem_insert, hne, false_or]
      rw [Finset.sum_congr rfl hB, scanSum_mem f r s hsr n (p + 1) x (by omega) (by omega),
        scanSum_mem f r s hsr n (p + 1) p (by omega) (by omega),
        show s - p = s - (p + 1) + 1 by omega, scanSum_step f (s - (p + 1)) x hlt]
      ring

/-- **The cut sets through a given point.**  For `0 < s < r` the cut sets `S ⊆ {1, …, r-1}` that
contain `s` have the total weight `Λ_s[f] · f(s) · Λ_{r-s}[f(s + ·)]`: a composition of `r` with a
cut at `s` is a composition of `s`, the cut, and a composition of `r - s` for the shifted profile.
The scan passes the positions before `s`, where it produces the cut sets of `[1, s)`, then the
position `s`, and from there it starts again with the base point `s`. -/
private theorem sum_cutWt_mem (f : ℕ → ℝ) {r s : ℕ} (hs : 0 < s) (hsr : s < r) :
    ∑ S ∈ (Ioo 0 r).powerset with s ∈ S, FirstCell.Wt f r S
      = Lam f s * f s * Lam (fun i => f (s + i)) (r - s) := by
  have h := scanSum_mem f r s hsr (r - 1) 1 0 (by omega) (by omega)
  have h1 := FirstCell.Zs_eq_Lam f (s - 1) 0 s s (by omega) (by omega)
  have h2 := FirstCell.Zs_eq_Lam f (r - s - 1) s r (r - s) (by omega) (by omega)
  simp only [zero_add] at h1
  rw [h1, h2] at h
  rw [Finset.sum_filter, FirstCell.Ioo_zero_eq_Ico_one]
  refine Eq.trans (Finset.sum_congr rfl fun S _ => ?_) h
  split_ifs
  · exact (mul_one _).symm
  · exact (mul_zero _).symm

/-! ### The correlation inequality -/

private theorem prod_inter_union_le {f g : ℕ → ℝ} {s t : Finset ℕ} (hf : ∀ x ∈ s, 0 ≤ f x)
    (hg : ∀ x ∈ t, 0 ≤ g x) (hgf : ∀ x ∈ t, g x ≤ f x) :
    (∏ x ∈ s, f x) * (∏ x ∈ t, g x) ≤ (∏ x ∈ s ∩ t, g x) * (∏ x ∈ s ∪ t, f x) := by
  have e1 : ∏ x ∈ s ∪ t, f x = (∏ x ∈ s, f x) * ∏ x ∈ t \ s, f x := by
    rw [← Finset.prod_union Finset.disjoint_sdiff, Finset.union_sdiff_self_eq_union]
  have e2 : ∏ x ∈ t, g x = (∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x := by
    rw [Finset.inter_comm, Finset.prod_inter_mul_prod_sdiff]
  have h3 : ∏ x ∈ t \ s, g x ≤ ∏ x ∈ t \ s, f x :=
    Finset.prod_le_prod₀ (fun x hx => hg x (mem_sdiff.mp hx).1)
      (fun x hx => hgf x (mem_sdiff.mp hx).1)
  have h4 : 0 ≤ (∏ x ∈ s, f x) * ∏ x ∈ s ∩ t, g x :=
    mul_nonneg (Finset.prod_nonneg hf) (Finset.prod_nonneg fun x hx => hg x (mem_inter.mp hx).2)
  rw [e1, e2]
  calc (∏ x ∈ s, f x) * ((∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x)
      = ((∏ x ∈ s, f x) * ∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x := by ring
    _ ≤ ((∏ x ∈ s, f x) * ∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, f x :=
        mul_le_mul_of_nonneg_left h3 h4
    _ = (∏ x ∈ s ∩ t, g x) * ((∏ x ∈ s, f x) * ∏ x ∈ t \ s, f x) := by ring

/-- The weights of the cut sets for two profiles `0 ≤ g ≤ f` satisfy the hypothesis of the four
functions theorem: `W_f(s) · W_g(t) ≤ W_g(s ∩ t) · W_f(s ∪ t)`.  The weight of the parts is
log-supermodular (`FirstCell.gs_lattice`), and the cut factors are compared point by point. -/
private theorem cutWt_modular {f g : ℕ → ℝ} {r : ℕ} (hg : ∀ x ∈ Ioo 0 r, 0 ≤ g x)
    (hgf : ∀ x ∈ Ioo 0 r, g x ≤ f x) {s t : Finset ℕ} (hs : s ⊆ Ioo 0 r) (ht : t ⊆ Ioo 0 r) :
    FirstCell.Wt f r s * FirstCell.Wt g r t
      ≤ FirstCell.Wt g r (s ∩ t) * FirstCell.Wt f r (s ∪ t) := by
  have hf : ∀ x ∈ Ioo 0 r, 0 ≤ f x := fun x hx => (hg x hx).trans (hgf x hx)
  have hG := FirstCell.gs_lattice s t (r - 1) 1 0 0 Nat.zero_lt_one Nat.zero_lt_one
  rw [min_self, max_self] at hG
  have hP := prod_inter_union_le (fun x hx => hf x (hs hx)) (fun x hx => hg x (ht hx))
    (fun x hx => hgf x (ht hx))
  show FirstCell.gs s (r - 1) 1 0 * (∏ x ∈ s, f x) * (FirstCell.gs t (r - 1) 1 0 * ∏ x ∈ t, g x)
    ≤ FirstCell.gs (s ∩ t) (r - 1) 1 0 * (∏ x ∈ s ∩ t, g x)
      * (FirstCell.gs (s ∪ t) (r - 1) 1 0 * ∏ x ∈ s ∪ t, f x)
  calc FirstCell.gs s (r - 1) 1 0 * (∏ x ∈ s, f x) * (FirstCell.gs t (r - 1) 1 0 * ∏ x ∈ t, g x)
      = (FirstCell.gs s (r - 1) 1 0 * FirstCell.gs t (r - 1) 1 0)
          * ((∏ x ∈ s, f x) * ∏ x ∈ t, g x) := by ring
    _ ≤ (FirstCell.gs (s ∩ t) (r - 1) 1 0 * FirstCell.gs (s ∪ t) (r - 1) 1 0)
          * ((∏ x ∈ s ∩ t, g x) * ∏ x ∈ s ∪ t, f x) :=
        mul_le_mul hG hP
          (mul_nonneg (Finset.prod_nonneg fun x hx => hf x (hs hx))
            (Finset.prod_nonneg fun x hx => hg x (ht hx)))
          (mul_nonneg (FirstCell.gs_nonneg _ _ _ _) (FirstCell.gs_nonneg _ _ _ _))
    _ = FirstCell.gs (s ∩ t) (r - 1) 1 0 * (∏ x ∈ s ∩ t, g x)
          * (FirstCell.gs (s ∪ t) (r - 1) 1 0 * ∏ x ∈ s ∪ t, f x) := by ring

/-- The four functions theorem for the subsets of a set `u`, with all hypotheses asked only for
subsets of `u`. -/
private theorem four_functions_powerset {u : Finset ℕ} {f₁ f₂ f₃ f₄ : Finset ℕ → ℝ}
    (h₁ : ∀ S ⊆ u, 0 ≤ f₁ S) (h₂ : ∀ S ⊆ u, 0 ≤ f₂ S) (h₃ : ∀ S ⊆ u, 0 ≤ f₃ S)
    (h₄ : ∀ S ⊆ u, 0 ≤ f₄ S)
    (h : ∀ s ⊆ u, ∀ t ⊆ u, f₁ s * f₂ t ≤ f₃ (s ∩ t) * f₄ (s ∪ t)) :
    (∑ S ∈ u.powerset, f₁ S) * (∑ S ∈ u.powerset, f₂ S)
      ≤ (∑ S ∈ u.powerset, f₃ S) * (∑ S ∈ u.powerset, f₄ S) := by
  have e : ∀ f : Finset ℕ → ℝ, ∑ S ∈ u.powerset, f (S ∩ u) = ∑ S ∈ u.powerset, f S := fun f =>
    Finset.sum_congr rfl fun S hS => by rw [inter_eq_left.mpr (mem_powerset.mp hS)]
  have key := Finset.four_functions_theorem (u := u)
    (f₁ := fun S => f₁ (S ∩ u)) (f₂ := fun S => f₂ (S ∩ u))
    (f₃ := fun S => f₃ (S ∩ u)) (f₄ := fun S => f₄ (S ∩ u))
    (fun S => h₁ _ inter_subset_right) (fun S => h₂ _ inter_subset_right)
    (fun S => h₃ _ inter_subset_right) (fun S => h₄ _ inter_subset_right)
    (fun s hs t ht => by
      show f₁ (s ∩ u) * f₂ (t ∩ u) ≤ f₃ (s ∩ t ∩ u) * f₄ ((s ∪ t) ∩ u)
      rw [inter_eq_left.mpr hs, inter_eq_left.mpr ht,
        inter_eq_left.mpr (inter_subset_left.trans hs), inter_eq_left.mpr (union_subset hs ht)]
      exact h s hs t ht)
    (𝒜 := u.powerset) (ℬ := u.powerset) (Finset.Subset.refl _) (Finset.Subset.refl _)
  rwa [Finset.infs_eq_inter (Finset.isLowerSet_coe_powerset _) (Finset.isLowerSet_coe_powerset _),
    Finset.inter_self, Finset.powerset_sups_powerset_self, e f₁, e f₂, e f₃, e f₄] at key

/-- **The FKG inequality for cut sets.**  Let `0 ≤ g ≤ f` be two cut profiles on `{1, …, r-1}` and
`F` a nonnegative function of the cut set that is monotone for inclusion.  Then the mean of `F`
under the weights of `g` is at most its mean under the weights of `f`; cross-multiplied,
`(∑_S W_g(S) F(S)) · Λ_r[f] ≤ Λ_r[g] · ∑_S W_f(S) F(S)`.  A larger profile favours larger cut
sets.  The proof applies the four functions theorem to `W_g · F`, `W_f`, `W_g`, `W_f · F`. -/
private theorem cutWt_fkg {f g : ℕ → ℝ} {r : ℕ} (hr : 1 ≤ r) (hg : ∀ s ∈ Ioo 0 r, 0 ≤ g s)
    (hgf : ∀ s ∈ Ioo 0 r, g s ≤ f s) {F : Finset ℕ → ℝ} (hF0 : ∀ S ⊆ Ioo 0 r, 0 ≤ F S)
    (hF : ∀ S ⊆ Ioo 0 r, ∀ T ⊆ Ioo 0 r, S ⊆ T → F S ≤ F T) :
    (∑ S ∈ (Ioo 0 r).powerset, FirstCell.Wt g r S * F S) * Lam f r
      ≤ Lam g r * ∑ S ∈ (Ioo 0 r).powerset, FirstCell.Wt f r S * F S := by
  have hf : ∀ s ∈ Ioo 0 r, 0 ≤ f s := fun s hs => (hg s hs).trans (hgf s hs)
  have hWg : ∀ S ⊆ Ioo 0 r, 0 ≤ FirstCell.Wt g r S := fun S hS =>
    cutWt_nonneg (fun s hs => hg s (hS hs)) r
  have hWf : ∀ S ⊆ Ioo 0 r, 0 ≤ FirstCell.Wt f r S := fun S hS =>
    cutWt_nonneg (fun s hs => hf s (hS hs)) r
  rw [← FirstCell.sum_Wt f hr, ← FirstCell.sum_Wt g hr]
  refine four_functions_powerset (fun S hS => mul_nonneg (hWg S hS) (hF0 S hS)) hWf hWg
    (fun S hS => mul_nonneg (hWf S hS) (hF0 S hS)) fun s hs t ht => ?_
  have hmod := cutWt_modular hg hgf ht hs
  rw [inter_comm t s, union_comm t s] at hmod
  calc FirstCell.Wt g r s * F s * FirstCell.Wt f r t
      = (FirstCell.Wt f r t * FirstCell.Wt g r s) * F s := by ring
    _ ≤ (FirstCell.Wt g r (s ∩ t) * FirstCell.Wt f r (s ∪ t)) * F (s ∪ t) :=
        mul_le_mul hmod (hF s hs _ (union_subset hs ht) subset_union_left) (hF0 s hs)
          (mul_nonneg (hWg _ (inter_subset_left.trans hs)) (hWf _ (union_subset hs ht)))
    _ = FirstCell.Wt g r (s ∩ t) * (FirstCell.Wt f r (s ∪ t) * F (s ∪ t)) := by ring

/-! ### An additive statistic of the cut set -/

/-- The sum of a statistic `∑_{t ∈ S} u t` against the weights of the cut sets: the point `t`
contributes `u t` times the total weight of the cut sets through `t`. -/
private theorem sum_cutWt_stat (f u : ℕ → ℝ) (r : ℕ) :
    ∑ S ∈ (Ioo 0 r).powerset, FirstCell.Wt f r S * ∑ t ∈ S, u t
      = ∑ t ∈ Ioo 0 r, u t * (Lam f t * f t * Lam (fun i => f (t + i)) (r - t)) := by
  calc ∑ S ∈ (Ioo 0 r).powerset, FirstCell.Wt f r S * ∑ t ∈ S, u t
      = ∑ S ∈ (Ioo 0 r).powerset, ∑ t ∈ S, u t * FirstCell.Wt f r S :=
        Finset.sum_congr rfl fun S _ => by
          rw [Finset.mul_sum]
          exact Finset.sum_congr rfl fun t _ => mul_comm _ _
    _ = ∑ t ∈ Ioo 0 r, ∑ S ∈ (Ioo 0 r).powerset with t ∈ S, u t * FirstCell.Wt f r S :=
        Finset.sum_comm' fun S t => by
          simp only [mem_powerset, mem_filter]
          exact ⟨fun h => ⟨h, h.1 h.2⟩, fun h => h.1⟩
    _ = ∑ t ∈ Ioo 0 r, u t * (Lam f t * f t * Lam (fun i => f (t + i)) (r - t)) :=
        Finset.sum_congr rfl fun t ht => by
          rw [← Finset.mul_sum, sum_cutWt_mem f (mem_Ioo.mp ht).1 (mem_Ioo.mp ht).2]

/-- For a constant profile `ρ` the statistic `U(S) = ∑_{t ∈ S} (q+1-t)` has the total weight
`(q+2)/2 · μ_q(ρ) · τ_q(ρ)`, where `τ_m(ρ) = tau m ρ` is the total weight of the compositions of
`m` for the constant profile `ρ` and `μ_q(ρ) = muh q ρ` the mean number of cuts under these
weights.  The cut sets through `t` have the weight `τ_t(ρ) · ρ · τ_{q-t}(ρ)`,
which is symmetric under `t ↦ q - t`; so `q + 1 - t` may be replaced by the average `(q+2)/2` of
`q + 1 - t` and `t + 1`, and the weights of the cut sets through the points add up to the weight
of the compositions with one marked cut (`Lam1_eq_sum`). -/
private theorem sum_cutWt_const_stat {ρ : ℝ} (hρ : 0 ≤ ρ) {q : ℕ} (hq : 1 ≤ q) :
    ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt (fun _ => ρ) q S * ∑ t ∈ S, ((q : ℝ) + 1 - t)
      = ((q : ℝ) + 2) / 2 * (muh q ρ * tau q ρ) := by
  have hrefl : ∑ t ∈ Ioo 0 q, ((q : ℝ) + 1 - t) * (tau t ρ * ρ * tau (q - t) ρ)
      = ∑ t ∈ Ioo 0 q, ((t : ℝ) + 1) * (tau t ρ * ρ * tau (q - t) ρ) := by
    rw [sum_Ioo_reflect (fun t => ((t : ℝ) + 1) * (tau t ρ * ρ * tau (q - t) ρ)) 0 q,
      Nat.sub_zero]
    refine Finset.sum_congr rfl fun t ht => ?_
    have ht' := mem_Ioo.mp ht
    show ((q : ℝ) + 1 - t) * (tau t ρ * ρ * tau (q - t) ρ)
      = (((q - t : ℕ) : ℝ) + 1) * (tau (q - t) ρ * ρ * tau (q - (q - t)) ρ)
    rw [show q - (q - t) = t by omega, Nat.cast_sub ht'.2.le]
    ring
  have hsum : ∑ t ∈ Ioo 0 q, tau t ρ * ρ * tau (q - t) ρ = muh q ρ * tau q ρ := by
    have h1 : ∑ t ∈ Ioo 0 q, tau t ρ * ρ * tau (q - t) ρ = Lam1 (fun _ => ρ) q := rfl
    rw [h1, Lam1_eq_sum, muh_mul_tau hq hρ]
    refine Finset.sum_congr rfl fun Q _ => ?_
    have hc := Vc_smul (fun _ => (1 : ℝ)) ρ Q q
    simp only [mul_one] at hc
    show ((Q : ℝ) - 1) * Vc (fun _ => ρ) Q q
      = ((Q : ℝ) - 1) * (Vc (fun _ => (1 : ℝ)) Q q * ρ ^ (Q - 1))
    rw [hc, mul_comm (ρ ^ (Q - 1))]
  have h2 : ∑ t ∈ Ioo 0 q, ((q : ℝ) + 1 - t) * (tau t ρ * ρ * tau (q - t) ρ)
        + ∑ t ∈ Ioo 0 q, ((t : ℝ) + 1) * (tau t ρ * ρ * tau (q - t) ρ)
      = ((q : ℝ) + 2) * ∑ t ∈ Ioo 0 q, tau t ρ * ρ * tau (q - t) ρ := by
    rw [← Finset.sum_add_distrib, Finset.mul_sum]
    exact Finset.sum_congr rfl fun t _ => by ring
  rw [← hrefl, hsum] at h2
  rw [sum_cutWt_stat (fun _ => ρ) (fun t => (q : ℝ) + 1 - t) q]
  show ∑ t ∈ Ioo 0 q, ((q : ℝ) + 1 - t) * (tau t ρ * ρ * tau (q - t) ρ)
    = ((q : ℝ) + 2) / 2 * (muh q ρ * tau q ρ)
  linarith

/-! ### The gain -/

/-- The gain of the profile at one cut point: with `x = q/((k-1)(k+q))`,
`λ_s · (1+x)^((q+1-s)/q) ≤ λ'_s` for `λ_s = (k-1)/(k+q-s)` and `λ'_s = k/(k+q+1-s)`.  By
Bernoulli's inequality the power is at most `1 + (q+1-s)/((k-1)(k+q))`, and
`λ'_s = λ_s · (1 + (q+1-s)/((k-1)(k+q+1-s)))` exactly. -/
private theorem profile_gain {k q s : ℕ} (hk : 2 ≤ k) (hs : s ∈ Ioo 0 q) :
    thr ((k : ℝ) - 1) ((k : ℝ) + q) s
        * (1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q))) ^ (((q : ℝ) + 1 - s) / q)
      ≤ thr (k : ℝ) ((k : ℝ) + q + 1) s := by
  have hs' := mem_Ioo.mp hs
  have hK : (2 : ℝ) ≤ k := by exact_mod_cast hk
  have hS1 : (1 : ℝ) ≤ s := by exact_mod_cast hs'.1
  have hSQ : (s : ℝ) + 1 ≤ q := by exact_mod_cast hs'.2
  have hQ0 : (0 : ℝ) < q := by linarith
  have hK1 : (k : ℝ) - 1 ≠ 0 := by linarith
  have hKQ : (k : ℝ) + q ≠ 0 := by linarith
  have hKs : (k : ℝ) + q - s ≠ 0 := by linarith
  have hKs1 : (k : ℝ) + q + 1 - s ≠ 0 := by linarith
  have hx0 : 0 ≤ (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)) :=
    div_nonneg hQ0.le (mul_nonneg (by linarith) (by linarith))
  have hB := rpow_one_add_le_one_add_mul_self
    (s := (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q))) (by linarith)
    (div_nonneg (by linarith : (0 : ℝ) ≤ (q : ℝ) + 1 - s) hQ0.le)
    ((div_le_one hQ0).mpr (by linarith))
  have e1 : ((q : ℝ) + 1 - s) / q * ((q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)))
      = ((q : ℝ) + 1 - s) / (((k : ℝ) - 1) * ((k : ℝ) + q)) := by
    field_simp
  rw [e1] at hB
  have hle : ((q : ℝ) + 1 - s) / (((k : ℝ) - 1) * ((k : ℝ) + q))
      ≤ ((q : ℝ) + 1 - s) / (((k : ℝ) - 1) * ((k : ℝ) + q + 1 - s)) :=
    div_le_div_of_nonneg_left (by linarith) (mul_pos (by linarith) (by linarith))
      (mul_le_mul_of_nonneg_left (by linarith) (by linarith))
  have e2 : ((k : ℝ) - 1) / ((k : ℝ) + q - s)
        * (1 + ((q : ℝ) + 1 - s) / (((k : ℝ) - 1) * ((k : ℝ) + q + 1 - s)))
      = (k : ℝ) / ((k : ℝ) + q + 1 - s) := by
    field_simp
    ring
  rw [thr_apply, thr_apply, ← e2]
  exact mul_le_mul_of_nonneg_left (hB.trans (by linarith))
    (div_nonneg (by linarith) (by linarith))

/-- **The gain of the boundary term along the diagonal.**  For `k ≥ 2` and `q ≥ 1`, with
`x = q/((k-1)(k+q))` and `μ₀ = mu0`:
`(1+x)^((q+2)/(2q) · μ₀(q, q²/(k-1))) · Λ_q(k-1; k+q) ≤ Λ_q(k; k+q+1)`.

Write both chain sums as sums over cut sets.  The weight of a cut set `S` gains at least the
factor `(1+x)^(U(S)/q)`, `U(S) = ∑_{s ∈ S} (q+1-s)` (`profile_gain`).  Jensen's inequality bounds
the mean of these factors from below by `(1+x)^ē`, where `ē` is the mean of `U/q` under the old
profile.  The FKG inequality compares that mean with the mean under the constant profile
`ρ = (k-1)/(k-1+q)`, which is `(q+2)/(2q) · μ_q(ρ)` with `μ_q(ρ) = muh q ρ` the mean number of
cuts under the constant profile, and `μ_q(ρ) ≥ μ₀(q, q²/(k-1))` (`mu0_le_muh`). -/
theorem Lam_gain {k q : ℕ} (hk : 2 ≤ k) (hq : 1 ≤ q) :
    (1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)))
        ^ (((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1)))
      * Lam (thr ((k : ℝ) - 1) ((k : ℝ) + q)) q
    ≤ Lam (thr (k : ℝ) ((k : ℝ) + q + 1)) q := by
  have hK : (2 : ℝ) ≤ k := by exact_mod_cast hk
  have hQ : (1 : ℝ) ≤ q := by exact_mod_cast hq
  have hQ0 : (0 : ℝ) < q := by linarith
  obtain ⟨ρ, hρdef⟩ : ∃ ρ : ℝ, ρ = ((k : ℝ) - 1) / ((k : ℝ) - 1 + q) := ⟨_, rfl⟩
  have hρ0 : 0 < ρ := by rw [hρdef]; exact div_pos (by linarith) (by linarith)
  have hρ1 : ρ ≤ 1 := by rw [hρdef, div_le_one (by linarith)]; linarith
  obtain ⟨c, hcdef⟩ : ∃ c : ℝ, c = 1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)) := ⟨_, rfl⟩
  have hc1 : 1 ≤ c := by
    rw [hcdef]
    linarith [div_nonneg hQ0.le (mul_nonneg (by linarith : (0 : ℝ) ≤ (k : ℝ) - 1)
      (by linarith : (0 : ℝ) ≤ (k : ℝ) + q))]
  have hc0 : 0 < c := by linarith
  obtain ⟨lam, hlam⟩ : ∃ lam : ℕ → ℝ, lam = thr ((k : ℝ) - 1) ((k : ℝ) + q) := ⟨_, rfl⟩
  obtain ⟨U, hU⟩ : ∃ U : Finset ℕ → ℝ, U = fun S : Finset ℕ => ∑ t ∈ S, ((q : ℝ) + 1 - t) :=
    ⟨_, rfl⟩
  rw [← hcdef, ← hlam]
  -- the old profile is at least `ρ` on the cut points, and the statistic `U` is monotone
  have hlamρ : ∀ s ∈ Ioo 0 q, ρ ≤ lam s := fun s hs => by
    have hs1 : (1 : ℝ) ≤ s := by exact_mod_cast (mem_Ioo.mp hs).1
    have hsq : (s : ℝ) < q := by exact_mod_cast (mem_Ioo.mp hs).2
    rw [hlam, hρdef, thr_apply]
    exact div_le_div_of_nonneg_left (by linarith) (by linarith) (by linarith)
  have hlam0 : ∀ s ∈ Ioo 0 q, 0 ≤ lam s := fun s hs => hρ0.le.trans (hlamρ s hs)
  have hu : ∀ t ∈ Ioo 0 q, (0 : ℝ) ≤ (q : ℝ) + 1 - t := fun t ht => by
    have : (t : ℝ) < q := by exact_mod_cast (mem_Ioo.mp ht).2
    linarith
  have hU0 : ∀ S ⊆ Ioo 0 q, 0 ≤ U S := fun S hS => by
    rw [hU]
    exact Finset.sum_nonneg fun t ht => hu t (hS ht)
  have hUmono : ∀ S ⊆ Ioo 0 q, ∀ T ⊆ Ioo 0 q, S ⊆ T → U S ≤ U T := fun S _ T hT hST => by
    rw [hU]
    exact Finset.sum_le_sum_of_subset_of_nonneg hST fun t ht _ => hu t (hT ht)
  have hWnn : ∀ S ∈ (Ioo 0 q).powerset, 0 ≤ FirstCell.Wt lam q S := fun S hS =>
    cutWt_nonneg (fun s hs => hlam0 s (mem_powerset.mp hS hs)) q
  have hLpos : 0 < Lam lam q := by
    rw [hlam]
    exact Lam_thr_pos hq (by linarith) (by linarith)
  -- the weight of every cut set gains the factor `c^(U(S)/q)`
  have hA : ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * c ^ (U S / q)
      ≤ Lam (thr (k : ℝ) ((k : ℝ) + q + 1)) q := by
    rw [← FirstCell.sum_Wt (thr (k : ℝ) ((k : ℝ) + q + 1)) hq]
    refine Finset.sum_le_sum fun S hS => ?_
    have hsub : S ⊆ Ioo 0 q := mem_powerset.mp hS
    have e1 : c ^ (U S / q) = ∏ t ∈ S, c ^ (((q : ℝ) + 1 - t) / q) := by
      rw [hU, Finset.sum_div, Real.rpow_sum_of_pos hc0]
    rw [e1]
    exact cutWt_mul_prod_le
      (fun t ht => mul_nonneg (hlam0 t (hsub ht)) (Real.rpow_pos_of_pos hc0 _).le)
      (fun t ht => by rw [hlam, hcdef]; exact profile_gain hk (hsub ht)) q
  -- Jensen: the mean of `c^(U/q)` is at least `c` to the mean `ē` of `U/q`
  obtain ⟨eb, hebdef⟩ : ∃ eb : ℝ,
      eb = (∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * (U S / q)) / Lam lam q := ⟨_, rfl⟩
  have heb : eb * Lam lam q = ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * (U S / q) := by
    rw [hebdef, div_mul_cancel₀ _ hLpos.ne']
  have hJ : c ^ eb * Lam lam q
      ≤ ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * c ^ (U S / q) :=
    jensen_rpow (Ioo 0 q).powerset (fun S => FirstCell.Wt lam q S) (fun S => U S / q) hWnn hc0
      (FirstCell.sum_Wt lam hq).symm heb
  -- FKG against the constant profile: `(q+2)/2 · μ_q(ρ) ≤ q · ē`
  have hfkg := cutWt_fkg (f := lam) (g := fun _ => ρ) hq (fun _ _ => hρ0.le) hlamρ hU0 hUmono
  have hconst : ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt (fun _ => ρ) q S * U S
      = ((q : ℝ) + 2) / 2 * (muh q ρ * tau q ρ) := by
    rw [hU]
    exact sum_cutWt_const_stat hρ0.le hq
  have hstat : ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * U S
      = (q : ℝ) * (eb * Lam lam q) := by
    rw [heb, Finset.mul_sum]
    exact Finset.sum_congr rfl fun S _ => by field_simp
  rw [hconst, hstat] at hfkg
  have hτpos : 0 < tau q ρ := tau_pos hq hρ0.le
  have hmean : ((q : ℝ) + 2) / 2 * muh q ρ ≤ (q : ℝ) * eb := by
    refine le_of_mul_le_mul_right ?_ (mul_pos hτpos hLpos)
    calc ((q : ℝ) + 2) / 2 * muh q ρ * (tau q ρ * Lam lam q)
        = ((q : ℝ) + 2) / 2 * (muh q ρ * tau q ρ) * Lam lam q := by ring
      _ ≤ tau q ρ * ((q : ℝ) * (eb * Lam lam q)) := hfkg
      _ = (q : ℝ) * eb * (tau q ρ * Lam lam q) := by ring
  have hmu := mu0_le_muh hq hρ0 hρ1
  have hX : (q : ℝ) * (1 / ρ - 1) = (q : ℝ) ^ 2 / ((k : ℝ) - 1) := by
    have hK1 : (k : ℝ) - 1 ≠ 0 := by linarith
    rw [hρdef]
    field_simp
    ring
  rw [hX] at hmu
  have hexp : ((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1)) ≤ eb := by
    have h2 : ((q : ℝ) + 2) / 2 * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1)) ≤ (q : ℝ) * eb :=
      le_trans (mul_le_mul_of_nonneg_left hmu (by positivity)) hmean
    rw [show ((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1))
        = (((q : ℝ) + 2) / 2 * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1))) / q by field_simp,
      div_le_iff₀ hQ0]
    linarith
  calc c ^ (((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1))) * Lam lam q
      ≤ c ^ eb * Lam lam q :=
        mul_le_mul_of_nonneg_right (Real.rpow_le_rpow_of_exponent_le hc1 hexp) hLpos.le
    _ ≤ ∑ S ∈ (Ioo 0 q).powerset, FirstCell.Wt lam q S * c ^ (U S / q) := hJ
    _ ≤ Lam (thr (k : ℝ) ((k : ℝ) + q + 1)) q := hA

end Parking
