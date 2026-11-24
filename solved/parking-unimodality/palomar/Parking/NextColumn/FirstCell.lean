module

public import Parking.NextColumn.BirthdayIneq
public import Mathlib.Algebra.BigOperators.Group.Finset.Powerset
public import Mathlib.Combinatorics.SetFamily.FourFunctions

/-!
# Removing the first unit cell

`Λ_{r+1}(k-1;N) ≤ (τ_{r+1}(h)/τ_r(h)) Λ_r(k;N)` with `N = k+r+1`, `h = (k-1)/(N-1)`
(`Lam_first_cell`), and its combination with `tau_succ_le` (`Lam_shorten`).

The proof removes the first unit cell of a composition of `r+1`, and compares the law of the first
part under the profile `λ'_i = (k-1)/(N-1-i) ≥ h` with its law under the constant profile `h`
by the FKG inequality (the weight `∏ a_part` is log-supermodular in the cut set because the Cayley
coefficients are log-convex).

## Organisation of the proof

All auxiliary material lives in the namespace `Parking.NextColumn.FirstCell`.  A composition of `r`
is represented by its set of cut points `S ⊆ {1, …, r-1}`.

* `gs S n p x` ("scanning gap weight"): the product of the Cayley weights of the parts cut out by
  the cut set `S` on the segment from the base point `x` (the last cut seen so far) to the
  endpoint `p + n`, where only the positions `p, p+1, …, p+n-1` are inspected.  It is defined by
  structural recursion on the number `n` of positions still to be inspected.
* `fp S n p`: the first point of `S` among `p, …, p+n-1`, or the endpoint `p+n`.
* `gs_lattice`: log-supermodularity of `gs` on the product lattice (cut sets) × (base points),
  proved directly by induction on `n` from the log-convexity `cay_logconvex`.
* `sum_first_Lam`: first-part decomposition of the sums over all cut sets, which identifies them
  with the quantities of `Lam_first`.
* `FPs_fkg`: the correlation inequality, from the four functions theorem
  `Finset.four_functions_theorem`.
* `Lam_succ_first`: the first-cell recursion.
-/

@[expose] public section

namespace Parking

open Finset

namespace FirstCell

/-! ### Small utilities -/

private theorem Ioo_zero_eq_Ico_one (m : ℕ) : Ioo 0 m = Ico 1 m := by
  ext a
  simp only [Finset.mem_Ioo, Finset.mem_Ico]
  omega

/-- Log-convexity of the Cayley coefficients, in the form used below. -/
private theorem cay_cross {x x' q p : ℕ} (hx : x ≤ x') (hq : x' < q) (hp : q ≤ p) :
    cay (q - x) * cay (p - x') ≤ cay (q - x') * cay (p - x) := by
  have h := cay_logconvex (u := q - x') (v := p - x') (c := x' - x) (by omega) (by omega)
  have e1 : q - x' + (x' - x) = q - x := by omega
  have e2 : p - x' + (x' - x) = p - x := by omega
  rw [e1, e2] at h
  exact h

private theorem cay_min_max (p x x' : ℕ) :
    cay (p - x) * cay (p - x') = cay (p - min x x') * cay (p - max x x') := by
  rcases le_total x x' with h | h
  · rw [min_eq_left h, max_eq_right h]
  · rw [min_eq_right h, max_eq_left h, mul_comm]

/-! ### The scanning gap weight -/

/-- `gs S n p x`: the product of the Cayley weights of the parts cut out by `S` on the segment
from the base point `x` to the endpoint `p + n`, where only the positions `p, …, p+n-1` are
inspected for membership in `S`. -/
private noncomputable def gs (S : Finset ℕ) : ℕ → ℕ → ℕ → ℝ
  | 0, p, x => cay (p - x)
  | n + 1, p, x => if p ∈ S then cay (p - x) * gs S n (p + 1) p else gs S n (p + 1) x

private theorem gs_zero (S : Finset ℕ) (p x : ℕ) : gs S 0 p x = cay (p - x) := by
  simp only [gs]

private theorem gs_succ (S : Finset ℕ) (n p x : ℕ) :
    gs S (n + 1) p x
      = if p ∈ S then cay (p - x) * gs S n (p + 1) p else gs S n (p + 1) x := by
  simp only [gs]

private theorem gs_nonneg (S : Finset ℕ) : ∀ n p x, 0 ≤ gs S n p x := by
  intro n
  induction n with
  | zero =>
    intro p x
    rw [gs_zero]
    exact cay_nonneg _
  | succ n ih =>
    intro p x
    rw [gs_succ]
    split_ifs
    · exact mul_nonneg (cay_nonneg _) (ih _ _)
    · exact ih _ _

/-- `gs S n p x` only depends on `S ∩ [p, ∞)`. -/
private theorem gs_congr {S S' : Finset ℕ} :
    ∀ n p x, (∀ s, p ≤ s → (s ∈ S ↔ s ∈ S')) → gs S n p x = gs S' n p x := by
  intro n
  induction n with
  | zero =>
    intro p x _
    rw [gs_zero, gs_zero]
  | succ n ih =>
    intro p x h
    have hp : p ∈ S ↔ p ∈ S' := h p le_rfl
    have h' : ∀ s, p + 1 ≤ s → (s ∈ S ↔ s ∈ S') := fun s hs => h s (by omega)
    rw [gs_succ, gs_succ, ih (p + 1) p h', ih (p + 1) x h']
    by_cases hpS : p ∈ S
    · rw [ite_eq_left hpS, ite_eq_left (hp.mp hpS)]
    · rw [ite_eq_right hpS, ite_eq_right (fun hc => hpS (hp.mpr hc))]

private theorem gs_insert_of_lt {a p : ℕ} (h : a < p) (S : Finset ℕ) (n x : ℕ) :
    gs (insert a S) n p x = gs S n p x := by
  apply gs_congr
  intro s hs
  rw [Finset.mem_insert]
  constructor
  · intro h'
    rcases h' with h' | h'
    · omega
    · exact h'
  · exact fun h' => Or.inr h'

/-- Changing the base point: for `x ≤ x' < q ≤ p`,
`a_{q-x} · gs(x') ≤ a_{q-x'} · gs(x)`. -/
private theorem gs_base_change (I : Finset ℕ) {x x' q : ℕ} (hx : x ≤ x') (hq : x' < q) :
    ∀ n p, q ≤ p → cay (q - x) * gs I n p x' ≤ cay (q - x') * gs I n p x := by
  intro n
  induction n with
  | zero =>
    intro p hp
    rw [gs_zero, gs_zero]
    exact cay_cross hx hq hp
  | succ n ih =>
    intro p hp
    rw [gs_succ, gs_succ]
    by_cases hpI : p ∈ I
    · rw [ite_eq_left hpI, ite_eq_left hpI]
      have h1 := cay_cross hx hq hp
      have h2 := gs_nonneg I n (p + 1) p
      calc cay (q - x) * (cay (p - x') * gs I n (p + 1) p)
          = (cay (q - x) * cay (p - x')) * gs I n (p + 1) p := by ring
        _ ≤ (cay (q - x') * cay (p - x)) * gs I n (p + 1) p :=
            mul_le_mul_of_nonneg_right h1 h2
        _ = cay (q - x') * (cay (p - x) * gs I n (p + 1) p) := by ring
    · rw [ite_eq_right hpI, ite_eq_right hpI]
      exact ih (p + 1) (by omega)

private theorem gs_cut_aux (I : Finset ℕ) (n : ℕ) {p x x' : ℕ} (hx' : x' < p) :
    cay (p - x) * gs I n (p + 1) x' ≤ cay (p - max x x') * gs I n (p + 1) (min x x') := by
  rcases le_total x x' with h | h
  · have h1 := gs_base_change I h hx' n (p + 1) (by omega)
    simp only [min_eq_left h, max_eq_right h]
    exact h1
  · simp only [min_eq_right h, max_eq_left h, le_refl]

/-- **Log-supermodularity of the gap weight** on (cut sets) × (base points). -/
private theorem gs_lattice (S S' : Finset ℕ) : ∀ n p x x', x < p → x' < p →
    gs S n p x * gs S' n p x'
      ≤ gs (S ∩ S') n p (min x x') * gs (S ∪ S') n p (max x x') := by
  intro n
  induction n with
  | zero =>
    intro p x x' _ _
    simp only [gs_zero]
    exact (cay_min_max p x x').le
  | succ n ih =>
    intro p x x' hx hx'
    have hp : p < p + 1 := Nat.lt_add_one p
    rw [gs_succ S, gs_succ S', gs_succ (S ∩ S'), gs_succ (S ∪ S')]
    by_cases h1 : p ∈ S <;> by_cases h2 : p ∈ S'
    · -- `p` is a cut of both
      have hI : p ∈ S ∩ S' := Finset.mem_inter.mpr ⟨h1, h2⟩
      have hU : p ∈ S ∪ S' := Finset.mem_union.mpr (Or.inl h1)
      rw [ite_eq_left h1, ite_eq_left h2, ite_eq_left hI, ite_eq_left hU]
      have h := ih (p + 1) p p hp hp
      rw [min_self, max_self] at h
      have hc := cay_min_max p x x'
      have hc0 : 0 ≤ cay (p - x) * cay (p - x') := mul_nonneg (cay_nonneg _) (cay_nonneg _)
      calc cay (p - x) * gs S n (p + 1) p * (cay (p - x') * gs S' n (p + 1) p)
          = (cay (p - x) * cay (p - x')) * (gs S n (p + 1) p * gs S' n (p + 1) p) := by ring
        _ ≤ (cay (p - x) * cay (p - x'))
              * (gs (S ∩ S') n (p + 1) p * gs (S ∪ S') n (p + 1) p) :=
            mul_le_mul_of_nonneg_left h hc0
        _ = (cay (p - min x x') * cay (p - max x x'))
              * (gs (S ∩ S') n (p + 1) p * gs (S ∪ S') n (p + 1) p) := by rw [hc]
        _ = cay (p - min x x') * gs (S ∩ S') n (p + 1) p
              * (cay (p - max x x') * gs (S ∪ S') n (p + 1) p) := by ring
    · -- `p` is a cut of `S` only
      have hI : p ∉ S ∩ S' := fun h => h2 (Finset.mem_inter.mp h).2
      have hU : p ∈ S ∪ S' := Finset.mem_union.mpr (Or.inl h1)
      rw [ite_eq_left h1, ite_eq_right h2, ite_eq_right hI, ite_eq_left hU]
      have h := ih (p + 1) p x' hp (by omega)
      rw [min_eq_right hx'.le, max_eq_left hx'.le] at h
      have ha := gs_cut_aux (S ∩ S') n (x := x) hx'
      calc cay (p - x) * gs S n (p + 1) p * gs S' n (p + 1) x'
          = cay (p - x) * (gs S n (p + 1) p * gs S' n (p + 1) x') := by ring
        _ ≤ cay (p - x) * (gs (S ∩ S') n (p + 1) x' * gs (S ∪ S') n (p + 1) p) :=
            mul_le_mul_of_nonneg_left h (cay_nonneg _)
        _ = (cay (p - x) * gs (S ∩ S') n (p + 1) x') * gs (S ∪ S') n (p + 1) p := by ring
        _ ≤ (cay (p - max x x') * gs (S ∩ S') n (p + 1) (min x x'))
              * gs (S ∪ S') n (p + 1) p :=
            mul_le_mul_of_nonneg_right ha (gs_nonneg _ _ _ _)
        _ = gs (S ∩ S') n (p + 1) (min x x')
              * (cay (p - max x x') * gs (S ∪ S') n (p + 1) p) := by ring
    · -- `p` is a cut of `S'` only
      have hI : p ∉ S ∩ S' := fun h => h1 (Finset.mem_inter.mp h).1
      have hU : p ∈ S ∪ S' := Finset.mem_union.mpr (Or.inr h2)
      rw [ite_eq_right h1, ite_eq_left h2, ite_eq_right hI, ite_eq_left hU]
      have h := ih (p + 1) x p (by omega) hp
      rw [min_eq_left hx.le, max_eq_right hx.le] at h
      have ha := gs_cut_aux (S ∩ S') n (x := x') hx
      rw [max_comm x' x, min_comm x' x] at ha
      calc gs S n (p + 1) x * (cay (p - x') * gs S' n (p + 1) p)
          = cay (p - x') * (gs S n (p + 1) x * gs S' n (p + 1) p) := by ring
        _ ≤ cay (p - x') * (gs (S ∩ S') n (p + 1) x * gs (S ∪ S') n (p + 1) p) :=
            mul_le_mul_of_nonneg_left h (cay_nonneg _)
        _ = (cay (p - x') * gs (S ∩ S') n (p + 1) x) * gs (S ∪ S') n (p + 1) p := by ring
        _ ≤ (cay (p - max x x') * gs (S ∩ S') n (p + 1) (min x x'))
              * gs (S ∪ S') n (p + 1) p :=
            mul_le_mul_of_nonneg_right ha (gs_nonneg _ _ _ _)
        _ = gs (S ∩ S') n (p + 1) (min x x')
              * (cay (p - max x x') * gs (S ∪ S') n (p + 1) p) := by ring
    · -- `p` is not a cut
      have hI : p ∉ S ∩ S' := fun h => h1 (Finset.mem_inter.mp h).1
      have hU : p ∉ S ∪ S' := fun h => (Finset.mem_union.mp h).elim h1 h2
      rw [ite_eq_right h1, ite_eq_right h2, ite_eq_right hI, ite_eq_right hU]
      exact ih (p + 1) x x' (by omega) (by omega)

/-! ### The first cut -/

/-- First point of `S` among `p, …, p+n-1`, or the endpoint `p + n` if there is none. -/
private def fp (S : Finset ℕ) : ℕ → ℕ → ℕ
  | 0, p => p
  | n + 1, p => if p ∈ S then p else fp S n (p + 1)

private theorem fp_zero (S : Finset ℕ) (p : ℕ) : fp S 0 p = p := by
  simp only [fp]

private theorem fp_succ (S : Finset ℕ) (n p : ℕ) :
    fp S (n + 1) p = if p ∈ S then p else fp S n (p + 1) := by
  simp only [fp]

private theorem le_fp (S : Finset ℕ) : ∀ n p, p ≤ fp S n p := by
  intro n
  induction n with
  | zero =>
    intro p
    exact (fp_zero S p).ge
  | succ n ih =>
    intro p
    rw [fp_succ]
    split_ifs
    · exact le_rfl
    · have := ih (p + 1)
      omega

/-- The first cut is antitone in the cut set. -/
private theorem fp_anti {S S' : Finset ℕ} (h : S ⊆ S') : ∀ n p, fp S' n p ≤ fp S n p := by
  intro n
  induction n with
  | zero =>
    intro p
    simp only [fp_zero, le_refl]
  | succ n ih =>
    intro p
    rw [fp_succ S', fp_succ S]
    by_cases hp' : p ∈ S'
    · rw [ite_eq_left hp']
      split_ifs
      · exact le_rfl
      · have := le_fp S n (p + 1)
        omega
    · rw [ite_eq_right hp', ite_eq_right (fun hp => hp' (h hp))]
      exact ih (p + 1)

/-! ### Sums over all cut sets: first-part decomposition -/

/-- Total weight of the cut sets `S ⊆ [p, r)`, seen from the base point `x`. -/
private noncomputable def Zs (f : ℕ → ℝ) (r n p x : ℕ) : ℝ :=
  ∑ S ∈ (Ico p r).powerset, gs S n p x * ∏ s ∈ S, f s

/-- First-part decomposition of the sum over the cut sets `S ⊆ [p, r)`, `r = p + n`,
with a test function `F` of the first cut. -/
private theorem sum_first_Zs (f F : ℕ → ℝ) (r : ℕ) : ∀ n p x, p + n = r →
    ∑ S ∈ (Ico p r).powerset, gs S n p x * (∏ s ∈ S, f s) * F (fp S n p)
      = F r * cay (r - x)
        + ∑ g ∈ Ico p r, F g * (cay (g - x) * f g * Zs f r (r - g - 1) (g + 1) g) := by
  intro n
  induction n with
  | zero =>
    intro p x hp
    have hpr : p = r := by omega
    subst hpr
    simp only [Finset.Ico_self, Finset.powerset_empty, Finset.sum_singleton, Finset.sum_empty,
      Finset.prod_empty, gs_zero, fp_zero, mul_one, add_zero]
    ring
  | succ n ih =>
    intro p x hp
    have hpr : p < r := by omega
    have hnot : p ∉ Ico (p + 1) r := by simp
    have h1 : ∑ S ∈ (Ico (p + 1) r).powerset,
          gs S (n + 1) p x * (∏ s ∈ S, f s) * F (fp S (n + 1) p)
        = ∑ S ∈ (Ico (p + 1) r).powerset,
          gs S n (p + 1) x * (∏ s ∈ S, f s) * F (fp S n (p + 1)) := by
      refine Finset.sum_congr rfl fun S hS => ?_
      have hpS : p ∉ S := fun h => hnot (Finset.mem_powerset.mp hS h)
      rw [gs_succ, fp_succ, ite_eq_right hpS, ite_eq_right hpS]
    have h2 : ∑ S ∈ (Ico (p + 1) r).powerset,
          gs (insert p S) (n + 1) p x * (∏ s ∈ insert p S, f s) * F (fp (insert p S) (n + 1) p)
        = F p * (cay (p - x) * f p * Zs f r n (p + 1) p) := by
      rw [Zs, Finset.mul_sum, Finset.mul_sum]
      refine Finset.sum_congr rfl fun S hS => ?_
      have hpS : p ∉ S := fun h => hnot (Finset.mem_powerset.mp hS h)
      rw [gs_succ, fp_succ, ite_eq_left (Finset.mem_insert_self p S),
        ite_eq_left (Finset.mem_insert_self p S), Finset.prod_insert hpS,
        gs_insert_of_lt (Nat.lt_add_one p)]
      ring
    have hins : Ico p r = insert p (Ico (p + 1) r) := by
      ext a
      simp only [Finset.mem_Ico, Finset.mem_insert]
      omega
    rw [hins, Finset.sum_powerset_insert hnot, h1, h2,
      ih (p + 1) x (by omega), Finset.sum_insert hnot]
    have hn : r - p - 1 = n := by omega
    rw [hn]
    ring

private theorem Zs_first (f : ℕ → ℝ) (r n p x : ℕ) (hp : p + n = r) :
    Zs f r n p x
      = cay (r - x) + ∑ g ∈ Ico p r, cay (g - x) * f g * Zs f r (r - g - 1) (g + 1) g := by
  have h := sum_first_Zs f (fun _ => 1) r n p x hp
  simp only [mul_one, one_mul] at h
  exact h

/-- The total weight of the cut sets of the segment `[x, r]` is `Λ_{r-x}[f(x+·)]`. -/
private theorem Zs_eq_Lam (f : ℕ → ℝ) : ∀ n x r m, x + 1 + n = r → m = n + 1 →
    Zs f r n (x + 1) x = Lam (fun s => f (x + s)) m := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro x r m hr hm
    subst hm
    have hs : ∑ g ∈ Ico (x + 1) r, cay (g - x) * f g * Zs f r (r - g - 1) (g + 1) g
        = ∑ g ∈ Ico 1 (n + 1),
            cay (x + g - x) * f (x + g) * Zs f r (r - (x + g) - 1) (x + g + 1) (x + g) := by
      have h := Finset.sum_Ico_add
        (fun g => cay (g - x) * f g * Zs f r (r - g - 1) (g + 1) g) 1 (n + 1) x
      have e1 : 1 + x = x + 1 := by omega
      have e2 : n + 1 + x = r := by omega
      rw [e1, e2] at h
      exact h.symm
    have e0 : r - x = n + 1 := by omega
    rw [Zs_first f r n (x + 1) x hr, Lam_first, hs, Ioo_zero_eq_Ico_one, e0]
    congr 1
    refine Finset.sum_congr rfl fun g hg => ?_
    have hg' := Finset.mem_Ico.mp hg
    rw [Nat.add_sub_cancel_left,
      ih (r - (x + g) - 1) (by omega) (x + g) r (n + 1 - g) (by omega) (by omega)]
    simp only [add_assoc]

/-- First-part decomposition, in terms of `Lam`. -/
private theorem sum_first_Lam (f F : ℕ → ℝ) (r n p x : ℕ) (hp : p + n = r) :
    ∑ S ∈ (Ico p r).powerset, gs S n p x * (∏ s ∈ S, f s) * F (fp S n p)
      = F r * cay (r - x)
        + ∑ g ∈ Ico p r, F g * (cay (g - x) * f g * Lam (fun s => f (g + s)) (r - g)) := by
  rw [sum_first_Zs f F r n p x hp]
  congr 1
  refine Finset.sum_congr rfl fun g hg => ?_
  have hg' := Finset.mem_Ico.mp hg
  rw [Zs_eq_Lam f (r - g - 1) g r (r - g) (by omega) (by omega)]

/-- Weight of the cut set `S ⊆ {1, …, r-1}` of a composition of `r`, for the profile `f`. -/
private noncomputable def Wt (f : ℕ → ℝ) (r : ℕ) (S : Finset ℕ) : ℝ :=
  gs S (r - 1) 1 0 * ∏ s ∈ S, f s

/-- The `φ`-weighted first-part sum `φ(r) a_r + ∑_j φ(j) a_j f(j) Λ_{r-j}[f(j+·)]`. -/
private noncomputable def FPs (φ f : ℕ → ℝ) (r : ℕ) : ℝ :=
  φ r * cay r + ∑ g ∈ Ioo 0 r, φ g * (cay g * f g * Lam (fun s => f (g + s)) (r - g))

private theorem sum_Wt_first (f F : ℕ → ℝ) {r : ℕ} (hr : 1 ≤ r) :
    ∑ S ∈ (Ioo 0 r).powerset, Wt f r S * F (fp S (r - 1) 1) = FPs F f r := by
  have h := sum_first_Lam f F r (r - 1) 1 0 (by omega)
  simp only [Nat.sub_zero] at h
  rw [← Ioo_zero_eq_Ico_one] at h
  exact h

private theorem sum_Wt (f : ℕ → ℝ) {r : ℕ} (hr : 1 ≤ r) :
    ∑ S ∈ (Ioo 0 r).powerset, Wt f r S = Lam f r := by
  have h := sum_Wt_first f (fun _ => 1) hr
  simp only [mul_one] at h
  rw [h, Lam_first f r, FPs]
  simp only [one_mul]

/-! ### The FKG inequality for the first part -/

private theorem prod_mixed_le {f g : ℕ → ℝ} (hg : ∀ s, 0 ≤ g s) (hgf : ∀ s, g s ≤ f s)
    (s t : Finset ℕ) :
    (∏ x ∈ s, f x) * (∏ x ∈ t, g x) ≤ (∏ x ∈ s ∩ t, g x) * (∏ x ∈ s ∪ t, f x) := by
  have hf : ∀ s, 0 ≤ f s := fun s => (hg s).trans (hgf s)
  have e1 : ∏ x ∈ s ∪ t, f x = (∏ x ∈ s, f x) * ∏ x ∈ t \ s, f x := by
    rw [← Finset.prod_union Finset.disjoint_sdiff, Finset.union_sdiff_self_eq_union]
  have e2 : ∏ x ∈ t, g x = (∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x := by
    rw [Finset.inter_comm, Finset.prod_inter_mul_prod_sdiff]
  have h3 : ∏ x ∈ t \ s, g x ≤ ∏ x ∈ t \ s, f x :=
    Finset.prod_le_prod₀ (fun x _ => hg x) (fun x _ => hgf x)
  have h4 : 0 ≤ ∏ x ∈ s, f x := Finset.prod_nonneg fun x _ => hf x
  have h5 : 0 ≤ ∏ x ∈ s ∩ t, g x := Finset.prod_nonneg fun x _ => hg x
  rw [e1, e2]
  calc (∏ x ∈ s, f x) * ((∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x)
      = ((∏ x ∈ s, f x) * ∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, g x := by ring
    _ ≤ ((∏ x ∈ s, f x) * ∏ x ∈ s ∩ t, g x) * ∏ x ∈ t \ s, f x :=
        mul_le_mul_of_nonneg_left h3 (mul_nonneg h4 h5)
    _ = (∏ x ∈ s ∩ t, g x) * ((∏ x ∈ s, f x) * ∏ x ∈ t \ s, f x) := by ring

private theorem Wt_nonneg {e : ℕ → ℝ} (he : ∀ s, 0 ≤ e s) (r : ℕ) (S : Finset ℕ) :
    0 ≤ Wt e r S := by
  unfold Wt
  exact mul_nonneg (gs_nonneg _ _ _ _) (Finset.prod_nonneg fun s _ => he s)

/-- The hypothesis of the four functions theorem. -/
private theorem Wt_modular {f g φ : ℕ → ℝ} (r : ℕ) (hg : ∀ s, 0 ≤ g s) (hgf : ∀ s, g s ≤ f s)
    (hφ0 : ∀ i, 0 ≤ φ i) (hφ : ∀ i j, 1 ≤ i → i ≤ j → φ i ≤ φ j) (s t : Finset ℕ) :
    (Wt f r s * φ (fp s (r - 1) 1)) * Wt g r t
      ≤ (Wt g r (s ∩ t) * φ (fp (s ∩ t) (r - 1) 1)) * Wt f r (s ∪ t) := by
  have hf : ∀ s, 0 ≤ f s := fun s => (hg s).trans (hgf s)
  have hG := gs_lattice s t (r - 1) 1 0 0 Nat.zero_lt_one Nat.zero_lt_one
  rw [min_self, max_self] at hG
  have hP := prod_mixed_le hg hgf s t
  have hφ' : φ (fp s (r - 1) 1) ≤ φ (fp (s ∩ t) (r - 1) 1) :=
    hφ _ _ (le_fp s (r - 1) 1) (fp_anti Finset.inter_subset_left (r - 1) 1)
  have hG0 : 0 ≤ gs (s ∩ t) (r - 1) 1 0 * gs (s ∪ t) (r - 1) 1 0 :=
    mul_nonneg (gs_nonneg _ _ _ _) (gs_nonneg _ _ _ _)
  have hP0 : 0 ≤ (∏ x ∈ s, f x) * ∏ x ∈ t, g x :=
    mul_nonneg (Finset.prod_nonneg fun x _ => hf x) (Finset.prod_nonneg fun x _ => hg x)
  have hP1 : 0 ≤ (∏ x ∈ s ∩ t, g x) * ∏ x ∈ s ∪ t, f x :=
    mul_nonneg (Finset.prod_nonneg fun x _ => hg x) (Finset.prod_nonneg fun x _ => hf x)
  have h1 : (gs s (r - 1) 1 0 * gs t (r - 1) 1 0) * ((∏ x ∈ s, f x) * ∏ x ∈ t, g x)
      ≤ (gs (s ∩ t) (r - 1) 1 0 * gs (s ∪ t) (r - 1) 1 0)
          * ((∏ x ∈ s ∩ t, g x) * ∏ x ∈ s ∪ t, f x) :=
    mul_le_mul hG hP hP0 hG0
  have h2 := mul_le_mul h1 hφ' (hφ0 _) (mul_nonneg hG0 hP1)
  unfold Wt
  calc gs s (r - 1) 1 0 * (∏ x ∈ s, f x) * φ (fp s (r - 1) 1)
          * (gs t (r - 1) 1 0 * ∏ x ∈ t, g x)
      = (gs s (r - 1) 1 0 * gs t (r - 1) 1 0) * ((∏ x ∈ s, f x) * ∏ x ∈ t, g x)
          * φ (fp s (r - 1) 1) := by ring
    _ ≤ (gs (s ∩ t) (r - 1) 1 0 * gs (s ∪ t) (r - 1) 1 0)
          * ((∏ x ∈ s ∩ t, g x) * ∏ x ∈ s ∪ t, f x) * φ (fp (s ∩ t) (r - 1) 1) := h2
    _ = gs (s ∩ t) (r - 1) 1 0 * (∏ x ∈ s ∩ t, g x) * φ (fp (s ∩ t) (r - 1) 1)
          * (gs (s ∪ t) (r - 1) 1 0 * ∏ x ∈ s ∪ t, f x) := by ring

/-- **FKG inequality for the first part**: for profiles `0 ≤ g ≤ f` and a nonnegative nondecreasing
`φ`, the first part is stochastically smaller under `f` than under `g`:
`(∑_j φ(j) w_f(j)) (∑_j w_g(j)) ≤ (∑_j φ(j) w_g(j)) (∑_j w_f(j))`. -/
private theorem FPs_fkg {f g φ : ℕ → ℝ} {r : ℕ} (hr : 1 ≤ r) (hg : ∀ s, 0 ≤ g s)
    (hgf : ∀ s, g s ≤ f s) (hφ0 : ∀ i, 0 ≤ φ i) (hφ : ∀ i j, 1 ≤ i → i ≤ j → φ i ≤ φ j) :
    FPs φ f r * Lam g r ≤ FPs φ g r * Lam f r := by
  have hf : ∀ s, 0 ≤ f s := fun s => (hg s).trans (hgf s)
  have key : (∑ S ∈ (Ioo 0 r).powerset, Wt f r S * φ (fp S (r - 1) 1))
        * (∑ S ∈ (Ioo 0 r).powerset, Wt g r S)
      ≤ (∑ S ∈ (Ioo 0 r).powerset, Wt g r S * φ (fp S (r - 1) 1))
        * (∑ S ∈ (Ioo 0 r).powerset, Wt f r S) := by
    have h4 := Finset.four_functions_theorem (u := Ioo 0 r)
      (f₁ := fun S => Wt f r S * φ (fp S (r - 1) 1)) (f₂ := fun S => Wt g r S)
      (f₃ := fun S => Wt g r S * φ (fp S (r - 1) 1)) (f₄ := fun S => Wt f r S)
      (fun S => mul_nonneg (Wt_nonneg hf r S) (hφ0 _)) (fun S => Wt_nonneg hg r S)
      (fun S => mul_nonneg (Wt_nonneg hg r S) (hφ0 _)) (fun S => Wt_nonneg hf r S)
      (fun s _ t _ => Wt_modular r hg hgf hφ0 hφ s t)
      (𝒜 := (Ioo 0 r).powerset) (ℬ := (Ioo 0 r).powerset)
      (Finset.Subset.refl _) (Finset.Subset.refl _)
    rw [Finset.infs_eq_inter (Finset.isLowerSet_coe_powerset _) (Finset.isLowerSet_coe_powerset _),
      Finset.inter_self, Finset.powerset_sups_powerset_self] at h4
    exact h4
  rw [← sum_Wt_first f φ hr, ← sum_Wt_first g φ hr, ← sum_Wt f hr, ← sum_Wt g hr]
  exact key

/-! ### The first-cell recursion -/

/-- `ψ(j) = (1+1/j)^(j-1) = a_{j+1}/a_j`. -/
private noncomputable def psi (j : ℕ) : ℝ := (1 + 1 / (j : ℝ)) ^ (j - 1)

private theorem psi_nonneg (j : ℕ) : 0 ≤ psi j := by
  unfold psi
  positivity

private theorem psi_le {i j : ℕ} (hi : 1 ≤ i) (hij : i ≤ j) : psi i ≤ psi j := by
  unfold psi
  exact psi_mono (by omega) hij

private theorem cay_succ_eq {j : ℕ} (hj : 0 < j) : cay (j + 1) = psi j * cay j := by
  unfold psi
  exact cay_ratio hj

/-- **First-cell recursion**: `Λ_{r+1}[f] = f(1) Λ_r[f'] + ∑_j ψ(j) w_{f'}(j)` with
`f' = f(1+·)`. -/
private theorem Lam_succ_first (f : ℕ → ℝ) {r : ℕ} (hr : 1 ≤ r) :
    Lam f (r + 1) = f 1 * Lam (fun s => f (1 + s)) r + FPs psi (fun s => f (1 + s)) r := by
  have hsplit : ∑ g ∈ Ioo 0 (r + 1), cay g * f g * Lam (fun s => f (g + s)) (r + 1 - g)
      = cay 1 * f 1 * Lam (fun s => f (1 + s)) (r + 1 - 1)
        + ∑ j ∈ Ioo 0 r,
            cay (j + 1) * f (j + 1) * Lam (fun s => f (j + 1 + s)) (r + 1 - (j + 1)) := by
    rw [Ioo_zero_eq_Ico_one (r + 1), Ioo_zero_eq_Ico_one r,
      Finset.sum_eq_sum_Ico_succ_bot (by omega : 1 < r + 1)]
    congr 1
    exact (Finset.sum_Ico_add'
      (fun g => cay g * f g * Lam (fun s => f (g + s)) (r + 1 - g)) 1 r 1).symm
  have hr1 : cay (r + 1) = psi r * cay r := cay_succ_eq (by omega)
  have hterm : ∀ j ∈ Ioo 0 r,
      cay (j + 1) * f (j + 1) * Lam (fun s => f (j + 1 + s)) (r + 1 - (j + 1))
        = psi j * (cay j * f (1 + j) * Lam (fun s => f (1 + (j + s))) (r - j)) := by
    intro j hj
    have hj' := Finset.mem_Ioo.mp hj
    have e1 : cay (j + 1) = psi j * cay j := cay_succ_eq hj'.1
    have e2 : r + 1 - (j + 1) = r - j := by omega
    have e3 : (fun s => f (j + 1 + s)) = (fun s => f (1 + (j + s))) := by
      funext s
      congr 1
      omega
    rw [e1, e2, e3, Nat.add_comm j 1]
    ring
  rw [Lam_first f (r + 1), hsplit, FPs, Finset.sum_congr rfl hterm, hr1, cay_one,
    Nat.add_sub_cancel]
  ring

/-- The abstract form of `Lam_first_cell`: for a profile `f ≥ h ≥ 0` with `f 1 = h`,
`Λ_{r+1}[f] τ_r(h) ≤ τ_{r+1}(h) Λ_r[f(1+·)]`. -/
private theorem Lam_succ_mul_tau_le {f : ℕ → ℝ} {h : ℝ} {r : ℕ} (hr : 1 ≤ r) (hh : 0 ≤ h)
    (hf1 : f 1 = h) (hf : ∀ s, h ≤ f s) :
    Lam f (r + 1) * tau r h ≤ tau (r + 1) h * Lam (fun s => f (1 + s)) r := by
  have hFC := Lam_succ_first f hr
  have hFCh : tau (r + 1) h = h * tau r h + FPs psi (fun _ => h) r :=
    Lam_succ_first (fun _ => h) hr
  have hFK : FPs psi (fun s => f (1 + s)) r * Lam (fun _ => h) r
      ≤ FPs psi (fun _ => h) r * Lam (fun s => f (1 + s)) r :=
    FPs_fkg hr (fun _ => hh) (fun s => hf (1 + s)) psi_nonneg (fun i j hi hij => psi_le hi hij)
  have hτ : tau r h = Lam (fun _ => h) r := rfl
  rw [hFC, hFCh, hf1, hτ]
  nlinarith [hFK]

/-- The algebraic identity `(1-h)/(2h(r+1)) = 1/(2(k-1))` for `h = (k-1)/(k+r)`. -/
private theorem shorten_const {a b c : ℝ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) (hab : b = a + c) :
    (1 - a / b) / (2 * (a / b) * c) = 1 / (2 * a) := by
  have h1 : a / b * b = a := div_mul_cancel₀ a hb.ne'
  have h2 : 2 * (a / b) * c ≠ 0 := by positivity
  have h3 : 2 * a ≠ 0 := by positivity
  rw [div_eq_div_iff h2 h3]
  rw [hab] at h1 ⊢
  linear_combination (-2 : ℝ) * h1

end FirstCell

/-- **Removing the first unit cell**, cross-multiplied:
`Λ_{r+1}(k-1;N) τ_r(h) ≤ τ_{r+1}(h) Λ_r(k;N)` with `N = k+r+1`, `h = (k-1)/(k+r)`. -/
theorem Lam_first_cell {k r : ℕ} (hk : 2 ≤ k) (hr : 1 ≤ r) :
    Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1) * tau r (((k : ℝ) - 1) / ((k : ℝ) + r))
      ≤ tau (r + 1) (((k : ℝ) - 1) / ((k : ℝ) + r)) * Lam (thr k ((k : ℝ) + r + 1)) r := by
  have hk1 : (2 : ℝ) ≤ k := by exact_mod_cast hk
  have hr1 : (1 : ℝ) ≤ r := by exact_mod_cast hr
  have hkr : (0 : ℝ) < (k : ℝ) + r := by linarith
  have hh0 : (0 : ℝ) ≤ ((k : ℝ) - 1) / ((k : ℝ) + r) := div_nonneg (by linarith) hkr.le
  -- on the cut points `1, …, r` the profile `(k-1)/(N-s)` is at least `h = (k-1)/(N-1)`
  have hthr : ∀ s ∈ Ioo 0 (r + 1),
      ((k : ℝ) - 1) / ((k : ℝ) + r) ≤ thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) s := by
    intro s hs
    have hs' := Finset.mem_Ioo.mp hs
    have hs1 : (1 : ℝ) ≤ s := by
      have : 1 ≤ s := by omega
      exact_mod_cast this
    have hs2 : (s : ℝ) ≤ r := by
      have : s ≤ r := by omega
      exact_mod_cast this
    rw [thr_apply]
    exact div_le_div_of_nonneg_left (by linarith) (by linarith) (by linarith)
  -- clamp the profile from below by `h`; this does not change it on the cut points
  have hcl : Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1)
      = Lam (fun s => max (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) s)
          (((k : ℝ) - 1) / ((k : ℝ) + r))) (r + 1) :=
    Lam_congr fun s hs => (max_eq_left (hthr s hs)).symm
  have hF1 : max (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) 1) (((k : ℝ) - 1) / ((k : ℝ) + r))
      = ((k : ℝ) - 1) / ((k : ℝ) + r) := by
    apply max_eq_right
    apply le_of_eq
    rw [thr_apply, Nat.cast_one]
    congr 1
    ring
  have hcore := FirstCell.Lam_succ_mul_tau_le
    (f := fun s => max (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) s)
      (((k : ℝ) - 1) / ((k : ℝ) + r)))
    (h := ((k : ℝ) - 1) / ((k : ℝ) + r)) hr hh0 hF1 (fun s => le_max_right _ _)
  -- profile comparison `λ'_i ≤ k/(N-i)`
  have hmono : Lam (fun s => max (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) (1 + s))
        (((k : ℝ) - 1) / ((k : ℝ) + r))) r
      ≤ Lam (thr k ((k : ℝ) + r + 1)) r := by
    apply Lam_mono
    · intro s _
      exact le_trans hh0 (le_max_right _ _)
    · intro s hs
      have hs' := Finset.mem_Ioo.mp hs
      have hs2 : (s : ℝ) + 1 ≤ r := by
        have : s + 1 ≤ r := by omega
        exact_mod_cast this
      have h1 : thr ((k : ℝ) - 1) ((k : ℝ) + r + 1) (1 + s) ≤ thr k ((k : ℝ) + r + 1) s := by
        rw [thr_apply, thr_apply,
          div_le_div_iff₀ (by push_cast; linarith) (by linarith)]
        push_cast
        nlinarith
      exact max_le h1 ((hthr (1 + s) (Finset.mem_Ioo.mpr ⟨by omega, by omega⟩)).trans h1)
  rw [hcl]
  exact hcore.trans (mul_le_mul_of_nonneg_left hmono (tau_pos (by omega) hh0).le)

/-- "Shortening by one" with the birthday-law gain (`Lam_first_cell` and `tau_succ_le`):
`Λ_{r+1}(k-1) ≤ (1+1/r)^r (1 - μ₋ / (2(k-1))) Λ_r(k)`, `μ₋ = muh r ((k-1)/(k+r))`. -/
theorem Lam_shorten {k r : ℕ} (hk : 2 ≤ k) (hr : 1 ≤ r) :
    Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1)
      ≤ (1 + 1 / (r : ℝ)) ^ r * (1 - muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1)))
          * Lam (thr k ((k : ℝ) + r + 1)) r := by
  have hk1 : (2 : ℝ) ≤ k := by exact_mod_cast hk
  have hr1 : (1 : ℝ) ≤ r := by exact_mod_cast hr
  have hkr : (0 : ℝ) < (k : ℝ) + r := by linarith
  have hh0 : (0 : ℝ) < ((k : ℝ) - 1) / ((k : ℝ) + r) := div_pos (by linarith) hkr
  have hh1 : ((k : ℝ) - 1) / ((k : ℝ) + r) ≤ 1 := by
    rw [div_le_one hkr]
    linarith
  have hτ : 0 < tau r (((k : ℝ) - 1) / ((k : ℝ) + r)) := tau_pos hr hh0.le
  have hL : 0 < Lam (thr k ((k : ℝ) + r + 1)) r := Lam_thr_pos hr (by linarith) (by linarith)
  have h1 := Lam_first_cell hk hr
  have h2 := tau_succ_le hr hh0 hh1
  have hc := FirstCell.shorten_const (a := (k : ℝ) - 1) (b := (k : ℝ) + r) (c := (r : ℝ) + 1)
    (by linarith) hkr (by linarith) (by ring)
  rw [hc] at h2
  have h3 : Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1)
        * tau r (((k : ℝ) - 1) / ((k : ℝ) + r))
      ≤ ((1 + 1 / (r : ℝ)) ^ r
          * (1 - muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1)))
          * Lam (thr k ((k : ℝ) + r + 1)) r) * tau r (((k : ℝ) - 1) / ((k : ℝ) + r)) := by
    calc Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1)
          * tau r (((k : ℝ) - 1) / ((k : ℝ) + r))
        ≤ tau (r + 1) (((k : ℝ) - 1) / ((k : ℝ) + r)) * Lam (thr k ((k : ℝ) + r + 1)) r := h1
      _ ≤ ((1 + 1 / (r : ℝ)) ^ r
            * (1 - 1 / (2 * ((k : ℝ) - 1)) * muh r (((k : ℝ) - 1) / ((k : ℝ) + r)))
            * tau r (((k : ℝ) - 1) / ((k : ℝ) + r))) * Lam (thr k ((k : ℝ) + r + 1)) r :=
          mul_le_mul_of_nonneg_right h2 hL.le
      _ = ((1 + 1 / (r : ℝ)) ^ r
            * (1 - muh r (((k : ℝ) - 1) / ((k : ℝ) + r)) / (2 * ((k : ℝ) - 1)))
            * Lam (thr k ((k : ℝ) + r + 1)) r) * tau r (((k : ℝ) - 1) / ((k : ℝ) + r)) := by
          ring
  exact le_of_mul_le_mul_right h3 hτ

end Parking
