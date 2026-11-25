import Parking.NextColumn.Compositions
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Matrix.Basic

/-!
# The erasure rule: ratio inequalities for the number of parts

`Vc f q m` is the total weight of the compositions of `m` with `q` parts
(`Parking.NextColumn.Compositions`).  This file compares the weights of `q` and of `q + 1` parts:

* `Tq_ratio`        : `q m T_{m,q+1} = (q+1)(m-q) T_{m,q}` (all cut factors equal to `1`);
* `Vc_ratio_le`     : cut factors in `[0,1]` ⇒ `q m V_{q+1} ≤ (q+1)(m-q) V_q`;
* `Vc_thr_ratio_ge` : threshold profile `1/(N-s)` ⇒ `(q+1)(m-q) V_q ≤ q m (N - m/2) V_{q+1}`
  (the midpoint comparison).

All three come from one matrix identity.  Let `G(x,y) = a_{y-x}` (`x < y`) be the strictly upper
triangular Cayley matrix, `X = diag(position)` and `δA = AX - XA`.  The convolution identity
`cay_conv` for the Cayley coefficients says

  `(δG) G = G (δG) = δG - G`   (`FI_left`, `FI_right`).

## Organisation of the proof

Everything lives in the ring of real `(M+1) × (M+1)` matrices (`CompRatio.Mat M`), positions
`0, …, M`.

* `Gm M` is the Cayley matrix `G`, `Dg M f` the diagonal matrix of a profile, `Xm M = Dg M id`,
  `Hm M = G X - X G = δG`, `Km M = H X - X H = δ²G`.
* `Ew M f a b C` is the entry `(0, M)` of the word `(G F)^a C (F G)^b`, `F = Dg M f`.  It is linear
  in `C`, absorbs `F G` on the right and `G F` on the left, and `Ew M f a b G = Vc f (a+b+1) M`
  (through `bridge`: the entry `(0, x)` of `G (F G)^q` is `Vc f (q+1) x`).
* `leibniz` / `Ew_leibniz`: `∑_p Ew p (q-p) (G Z - Z G) = (z M - z 0) V_{q+1}` for `Z = Dg M z`.
* `E1`: the erasure identity, obtained by inserting the fundamental identity into the Leibniz rule;
  `ID2`: its consequence for a general profile `f`, in which the defect of the ratio inequality is
  a sum of words containing the factor `1 - F`.  For `f = 1` the defect vanishes (`Tq_ratio`), for
  `0 ≤ f ≤ 1` it is nonnegative (`Vc_ratio_le`).
* For the threshold profile, `F (N - X) = 1` is inserted next to the marked factor instead, and the
  remaining words with marked factor `δ²G` are compared by `isNonneg_Yr` (`Vc_thr_ratio_ge`).
-/

namespace Parking

open Finset

namespace CompRatio

/-! ### Lemmas on finite sums of real sequences -/

/-- Index shift: the two "marked position" sums over `p ∈ {0..n-1}` combine into one over
`p ∈ {0..n}`. -/
private theorem sum_shift (e₁ e₂ : ℕ → ℝ) (n : ℕ) (c : ℝ) (hc : c = n) :
    ∑ p ∈ range n, ((c - p) * e₁ p + ((p : ℝ) + 1) * e₂ (p + 1))
      = ∑ p ∈ range (n + 1), ((c - p) * e₁ p + (p : ℝ) * e₂ p) := by
  subst hc
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib,
    Finset.sum_range_succ (fun p => ((n : ℝ) - p) * e₁ p) n,
    Finset.sum_range_succ' (fun p => (p : ℝ) * e₂ p) n]
  simp only [sub_self, zero_mul, add_zero, Nat.cast_zero, Nat.cast_add, Nat.cast_one]

/-- Abel summation for the weights `q - 2p`. -/
private theorem abel_sum (β : ℕ → ℝ) (q : ℝ) (n : ℕ) :
    ∑ p ∈ range (n + 1), (q - 2 * p) * β p
      = ∑ k ∈ range n, ((k : ℝ) + 1) * (q - k) * (β k - β (k + 1))
        + ((n : ℝ) + 1) * (q - n) * β n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih,
      Finset.sum_range_succ (fun k => ((k : ℝ) + 1) * (q - k) * (β k - β (k + 1))) n]
    push_cast
    ring

/-- A sequence that is nonincreasing on `{0..q}` has nonnegative `(q - 2p)`-moment. -/
private theorem sum_antitone_nonneg (β : ℕ → ℝ) (q : ℕ) (h : ∀ p, p < q → β (p + 1) ≤ β p) :
    0 ≤ ∑ p ∈ range (q + 1), ((q : ℝ) - 2 * p) * β p := by
  rw [abel_sum β (q : ℝ) q, sub_self, mul_zero, zero_mul, add_zero]
  apply Finset.sum_nonneg
  intro k hk
  rw [mem_range] at hk
  have h1 : (0 : ℝ) ≤ (k : ℝ) + 1 := by positivity
  have h2 : (0 : ℝ) ≤ (q : ℝ) - k := by
    have : (k : ℝ) ≤ q := by exact_mod_cast hk.le
    linarith
  have h3 : 0 ≤ β k - β (k + 1) := by linarith [h k hk]
  exact mul_nonneg (mul_nonneg h1 h2) h3

/-- Reflection argument: a nondecreasing weight against an antisymmetric kernel which is nonnegative
on the upper half. -/
private theorem refl_sum_nonneg_aux (t : ℕ) (ℓ w : ℕ → ℝ)
    (hℓ : ∀ a b, a ≤ b → b ≤ t → ℓ a ≤ ℓ b)
    (hwt : w t = 0)
    (hanti : ∀ α, α ≤ t → w (t - α) = - w α)
    (hpos : ∀ α, α ≤ t → t - α ≤ α → 0 ≤ w α) :
    0 ≤ ∑ α ∈ range t, ℓ α * w α := by
  have h1 : ∑ α ∈ range (t + 1), ℓ α * w α = ∑ α ∈ range t, ℓ α * w α := by
    rw [Finset.sum_range_succ, hwt, mul_zero, add_zero]
  have h2 : ∑ α ∈ range (t + 1), ℓ (t - α) * w α = - ∑ α ∈ range (t + 1), ℓ α * w α := by
    rw [← Finset.sum_range_reflect (fun α => ℓ α * w α) (t + 1), ← Finset.sum_neg_distrib]
    apply Finset.sum_congr rfl
    intro α hα
    rw [mem_range] at hα
    have e1 : t + 1 - 1 - α = t - α := by omega
    rw [e1, hanti α (by omega)]
    ring
  have h3 : 0 ≤ ∑ α ∈ range (t + 1), (ℓ α - ℓ (t - α)) * w α := by
    apply Finset.sum_nonneg
    intro α hα
    rw [mem_range] at hα
    have hαt : α ≤ t := by omega
    by_cases hc : t - α ≤ α
    · exact mul_nonneg (sub_nonneg.mpr (hℓ _ _ hc hαt)) (hpos α hαt hc)
    · have hc' : α ≤ t - α := by omega
      have hw : w α ≤ 0 := by
        have h5 := hpos (t - α) (by omega) (by omega)
        rw [hanti α hαt] at h5
        linarith
      have hl : ℓ α - ℓ (t - α) ≤ 0 := sub_nonpos.mpr (hℓ _ _ hc' (by omega))
      exact mul_nonneg_of_nonpos_of_nonpos hl hw
  have h4 : ∑ α ∈ range (t + 1), (ℓ α - ℓ (t - α)) * w α
      = ∑ α ∈ range (t + 1), ℓ α * w α - ∑ α ∈ range (t + 1), ℓ (t - α) * w α := by
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro α _
    ring
  rw [h4, h2, h1] at h3
  linarith

/-- The kernel `a_α a_{t-α} (α² - (t-α)²)` against a nondecreasing weight. -/
private theorem refl_sum_nonneg (t : ℕ) (ℓ : ℕ → ℝ) (hℓ : ∀ a b, a ≤ b → b ≤ t → ℓ a ≤ ℓ b) :
    0 ≤ ∑ α ∈ range t,
      ℓ α * (cay α * cay (t - α) * ((α : ℝ) ^ 2 - ((t - α : ℕ) : ℝ) ^ 2)) := by
  refine refl_sum_nonneg_aux t ℓ
    (fun α => cay α * cay (t - α) * ((α : ℝ) ^ 2 - ((t - α : ℕ) : ℝ) ^ 2)) hℓ ?_ ?_ ?_
  · show cay t * cay (t - t) * ((t : ℝ) ^ 2 - ((t - t : ℕ) : ℝ) ^ 2) = 0
    rw [Nat.sub_self, cay_zero, mul_zero, zero_mul]
  · intro α hα
    show cay (t - α) * cay (t - (t - α))
        * (((t - α : ℕ) : ℝ) ^ 2 - ((t - (t - α) : ℕ) : ℝ) ^ 2)
      = - (cay α * cay (t - α) * ((α : ℝ) ^ 2 - ((t - α : ℕ) : ℝ) ^ 2))
    have e : t - (t - α) = α := by omega
    rw [e]
    ring
  · intro α _ hc
    show 0 ≤ cay α * cay (t - α) * ((α : ℝ) ^ 2 - ((t - α : ℕ) : ℝ) ^ 2)
    have hcast : ((t - α : ℕ) : ℝ) ≤ (α : ℝ) := by exact_mod_cast hc
    have hsq : ((t - α : ℕ) : ℝ) ^ 2 ≤ (α : ℝ) ^ 2 :=
      pow_le_pow_left₀ (Nat.cast_nonneg _) hcast 2
    exact mul_nonneg (mul_nonneg (cay_nonneg _) (cay_nonneg _)) (sub_nonneg.mpr hsq)

/-- Reflected form of `cay_conv`: `∑_{α<t} a_α (t-α) a_{t-α} = (t-1) a_t`. -/
private theorem cay_conv_refl (t : ℕ) :
    ∑ α ∈ range t, cay α * (((t - α : ℕ) : ℝ) * cay (t - α)) = ((t : ℝ) - 1) * cay t := by
  have hA : ∑ α ∈ range (t + 1), cay α * (((t - α : ℕ) : ℝ) * cay (t - α))
      = ∑ α ∈ range t, cay α * (((t - α : ℕ) : ℝ) * cay (t - α)) := by
    rw [Finset.sum_range_succ, Nat.sub_self, cay_zero, mul_zero, mul_zero, add_zero]
  have hB : ∑ α ∈ range (t + 1), (α : ℝ) * cay α * cay (t - α)
      = ∑ α ∈ range t, (α : ℝ) * cay α * cay (t - α) := by
    rw [Finset.sum_range_succ, Nat.sub_self, cay_zero, mul_zero, add_zero]
  rw [← cay_conv t, ← hA, ← hB,
    ← Finset.sum_range_reflect (fun α => (α : ℝ) * cay α * cay (t - α)) (t + 1)]
  apply Finset.sum_congr rfl
  intro α hα
  rw [mem_range] at hα
  have e1 : t + 1 - 1 - α = t - α := by omega
  have e2 : t - (t - α) = α := by omega
  rw [e1, e2]
  ring

/-! ### The matrix model -/

/-- Real square matrices indexed by the positions `0, …, M`. -/
private abbrev Mat (M : ℕ) : Type := Matrix (Fin (M + 1)) (Fin (M + 1)) ℝ

/-- The strictly upper triangular Cayley matrix `G(i,j) = a_{j-i}` (`i < j`). -/
private noncomputable def Gm (M : ℕ) : Mat M :=
  Matrix.of fun (i j : Fin (M + 1)) => if (i : ℕ) < (j : ℕ) then cay ((j : ℕ) - (i : ℕ)) else 0

/-- The diagonal matrix of a profile. -/
private noncomputable def Dg (M : ℕ) (f : ℕ → ℝ) : Mat M :=
  Matrix.diagonal fun (i : Fin (M + 1)) => f (i : ℕ)

/-- The position matrix `X`. -/
private noncomputable def Xm (M : ℕ) : Mat M := Dg M fun s => (s : ℝ)

/-- `δG = G X - X G`. -/
private noncomputable def Hm (M : ℕ) : Mat M := Gm M * Xm M - Xm M * Gm M

/-- `δ²G = (δG) X - X (δG)`. -/
private noncomputable def Km (M : ℕ) : Mat M := Hm M * Xm M - Xm M * Hm M

private theorem Gm_apply (M : ℕ) (i j : Fin (M + 1)) :
    Gm M i j = if (i : ℕ) < (j : ℕ) then cay ((j : ℕ) - (i : ℕ)) else 0 := rfl

private theorem Dg_apply (M : ℕ) (f : ℕ → ℝ) (i j : Fin (M + 1)) :
    Dg M f i j = if i = j then f (i : ℕ) else 0 := by
  unfold Dg
  exact Matrix.diagonal_apply _ _ _

private theorem mul_Dg_apply (M : ℕ) (A : Mat M) (f : ℕ → ℝ) (i j : Fin (M + 1)) :
    (A * Dg M f) i j = A i j * f (j : ℕ) := by
  unfold Dg
  exact Matrix.mul_diagonal _ _ _ _

private theorem Dg_mul_apply (M : ℕ) (f : ℕ → ℝ) (A : Mat M) (i j : Fin (M + 1)) :
    (Dg M f * A) i j = f (i : ℕ) * A i j := by
  unfold Dg
  exact Matrix.diagonal_mul _ _ _ _

private theorem mul_Xm_apply (M : ℕ) (A : Mat M) (i j : Fin (M + 1)) :
    (A * Xm M) i j = A i j * ((j : ℕ) : ℝ) :=
  mul_Dg_apply M A (fun s => (s : ℝ)) i j

private theorem Xm_mul_apply (M : ℕ) (A : Mat M) (i j : Fin (M + 1)) :
    (Xm M * A) i j = ((i : ℕ) : ℝ) * A i j :=
  Dg_mul_apply M (fun s => (s : ℝ)) A i j

private theorem Hm_apply (M : ℕ) (i j : Fin (M + 1)) :
    Hm M i j = if (i : ℕ) < (j : ℕ)
      then (((j : ℕ) - (i : ℕ) : ℕ) : ℝ) * cay ((j : ℕ) - (i : ℕ)) else 0 := by
  unfold Hm
  rw [Matrix.sub_apply, mul_Xm_apply, Xm_mul_apply, Gm_apply]
  split_ifs with h
  · rw [Nat.cast_sub h.le]
    ring
  · ring

private theorem Km_apply (M : ℕ) (i j : Fin (M + 1)) :
    Km M i j = if (i : ℕ) < (j : ℕ)
      then (((j : ℕ) - (i : ℕ) : ℕ) : ℝ) ^ 2 * cay ((j : ℕ) - (i : ℕ)) else 0 := by
  unfold Km
  rw [Matrix.sub_apply, mul_Xm_apply, Xm_mul_apply, Hm_apply]
  split_ifs with h
  · rw [Nat.cast_sub h.le]
    ring
  · ring

private theorem Dg_comm (M : ℕ) (f g : ℕ → ℝ) : Dg M f * Dg M g = Dg M g * Dg M f := by
  unfold Dg
  rw [Matrix.diagonal_mul_diagonal, Matrix.diagonal_mul_diagonal]
  exact congrArg Matrix.diagonal (funext fun i => mul_comm _ _)

private theorem Dg_one_sub (M : ℕ) (f : ℕ → ℝ) : Dg M (fun s => 1 - f s) = 1 - Dg M f := by
  ext i j
  rw [Matrix.sub_apply, Dg_apply, Dg_apply, Matrix.one_apply]
  split_ifs <;> ring

private theorem Dg_zero (M : ℕ) : Dg M (fun _ => (0 : ℝ)) = 0 := by
  ext i j
  rw [Dg_apply, Matrix.zero_apply]
  split_ifs <;> rfl

/-! ### Entrywise nonnegativity -/

/-- Entrywise nonnegative matrices. -/
private def IsNonneg {M : ℕ} (A : Mat M) : Prop := ∀ i j, 0 ≤ A i j

private theorem IsNonneg.mul {M : ℕ} {A B : Mat M} (hA : IsNonneg A) (hB : IsNonneg B) :
    IsNonneg (A * B) := by
  intro i j
  rw [Matrix.mul_apply]
  exact Finset.sum_nonneg fun u _ => mul_nonneg (hA i u) (hB u j)

private theorem isNonneg_one (M : ℕ) : IsNonneg (1 : Mat M) := by
  intro i j
  rw [Matrix.one_apply]
  split_ifs
  · exact zero_le_one
  · exact le_refl 0

private theorem IsNonneg.pow {M : ℕ} {A : Mat M} (hA : IsNonneg A) (n : ℕ) : IsNonneg (A ^ n) := by
  induction n with
  | zero =>
    rw [pow_zero]
    exact isNonneg_one M
  | succ n ih =>
    rw [pow_succ]
    exact ih.mul hA

private theorem isNonneg_Gm (M : ℕ) : IsNonneg (Gm M) := by
  intro i j
  rw [Gm_apply]
  split_ifs
  · exact cay_nonneg _
  · exact le_refl 0

private theorem isNonneg_Dg (M : ℕ) {f : ℕ → ℝ} (hf : ∀ s, s ≤ M → 0 ≤ f s) :
    IsNonneg (Dg M f) := by
  intro i j
  rw [Dg_apply]
  split_ifs
  · exact hf _ (Nat.lt_succ_iff.mp i.isLt)
  · exact le_refl 0

private theorem isNonneg_Hm (M : ℕ) : IsNonneg (Hm M) := by
  intro i j
  rw [Hm_apply]
  split_ifs
  · exact mul_nonneg (Nat.cast_nonneg _) (cay_nonneg _)
  · exact le_refl 0

/-! ### Sums over the middle index -/

/-- The sum over the middle index of a product of two strictly upper triangular "difference
kernels" with a diagonal factor in the middle, as a convolution. -/
private theorem sum_mid (M : ℕ) (a b f : ℕ → ℝ) (ha : a 0 = 0) (i j : Fin (M + 1)) :
    ∑ u : Fin (M + 1), (if (i : ℕ) < (u : ℕ) then a ((u : ℕ) - (i : ℕ)) else 0) * f (u : ℕ) *
        (if (u : ℕ) < (j : ℕ) then b ((j : ℕ) - (u : ℕ)) else 0)
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)), a α * f ((i : ℕ) + α) * b ((j : ℕ) - (i : ℕ) - α) := by
  have h1 : ∑ u : Fin (M + 1), (if (i : ℕ) < (u : ℕ) then a ((u : ℕ) - (i : ℕ)) else 0) *
        f (u : ℕ) * (if (u : ℕ) < (j : ℕ) then b ((j : ℕ) - (u : ℕ)) else 0)
      = ∑ u ∈ range (M + 1), (if (i : ℕ) < u then a (u - (i : ℕ)) else 0) * f u *
        (if u < (j : ℕ) then b ((j : ℕ) - u) else 0) :=
    Fin.sum_univ_eq_sum_range (fun u => (if (i : ℕ) < u then a (u - (i : ℕ)) else 0) * f u *
        (if u < (j : ℕ) then b ((j : ℕ) - u) else 0)) (M + 1)
  rw [h1]
  have hsub : Ico (i : ℕ) (j : ℕ) ⊆ range (M + 1) := by
    intro u hu
    rw [mem_Ico] at hu
    rw [mem_range]
    have := j.isLt
    omega
  rw [← Finset.sum_subset hsub, Finset.sum_Ico_eq_sum_range]
  · apply Finset.sum_congr rfl
    intro α hα
    rw [mem_range] at hα
    by_cases h0 : α = 0
    · subst h0
      simp [ha]
    · have h1 : (i : ℕ) < (i : ℕ) + α := by omega
      have h2 : (i : ℕ) + α < (j : ℕ) := by omega
      have e1 : (i : ℕ) + α - (i : ℕ) = α := by omega
      have e2 : (j : ℕ) - ((i : ℕ) + α) = (j : ℕ) - (i : ℕ) - α := by omega
      rw [ite_eq_left h1, ite_eq_left h2, e1, e2]
  · intro u _ hnot
    rw [mem_Ico] at hnot
    by_cases h1 : (i : ℕ) < u
    · have h2 : ¬ (u < (j : ℕ)) := by omega
      rw [ite_eq_right h2, mul_zero]
    · rw [ite_eq_right h1, zero_mul, zero_mul]

/-- `sum_mid` without the diagonal factor. -/
private theorem sum_mid2 (M : ℕ) (a b : ℕ → ℝ) (ha : a 0 = 0) (i j : Fin (M + 1)) :
    ∑ u : Fin (M + 1), (if (i : ℕ) < (u : ℕ) then a ((u : ℕ) - (i : ℕ)) else 0) *
        (if (u : ℕ) < (j : ℕ) then b ((j : ℕ) - (u : ℕ)) else 0)
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)), a α * b ((j : ℕ) - (i : ℕ) - α) := by
  have h := sum_mid M a b (fun _ => 1) ha i j
  simp only [mul_one] at h
  exact h

/-! ### The fundamental identity `(δG) G = G (δG) = δG - G` -/

private theorem FI_left (M : ℕ) : Hm M * Gm M = Hm M - Gm M := by
  ext i j
  rw [Matrix.mul_apply, Matrix.sub_apply]
  have h1 : ∑ u : Fin (M + 1), Hm M i u * Gm M u j
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)), (α : ℝ) * cay α * cay ((j : ℕ) - (i : ℕ) - α) := by
    have h := sum_mid2 M (fun α => (α : ℝ) * cay α) cay (by simp) i j
    simp only [Hm_apply, Gm_apply]
    exact h
  rw [h1, cay_conv, Hm_apply, Gm_apply]
  by_cases h : (i : ℕ) < (j : ℕ)
  · rw [ite_eq_left h, ite_eq_left h]
    ring
  · have ht : (j : ℕ) - (i : ℕ) = 0 := by omega
    rw [ite_eq_right h, ite_eq_right h, ht, cay_zero]
    ring

private theorem FI_right (M : ℕ) : Gm M * Hm M = Hm M - Gm M := by
  ext i j
  rw [Matrix.mul_apply, Matrix.sub_apply]
  have h1 : ∑ u : Fin (M + 1), Gm M i u * Hm M u j
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)),
          cay α * ((((j : ℕ) - (i : ℕ) - α : ℕ) : ℝ) * cay ((j : ℕ) - (i : ℕ) - α)) := by
    have h := sum_mid2 M cay (fun β => (β : ℝ) * cay β) cay_zero i j
    simp only [Hm_apply, Gm_apply]
    exact h
  rw [h1, cay_conv_refl, Hm_apply, Gm_apply]
  by_cases h : (i : ℕ) < (j : ℕ)
  · rw [ite_eq_left h, ite_eq_left h]
    ring
  · have ht : (j : ℕ) - (i : ℕ) = 0 := by omega
    rw [ite_eq_right h, ite_eq_right h, ht, cay_zero]
    ring

/-! ### The bridge between matrix entries and `Vc` -/

private theorem bridge_sum (M : ℕ) (v f : ℕ → ℝ) (hv : v 0 = 0) (x : Fin (M + 1)) :
    ∑ u : Fin (M + 1), v (u : ℕ) * f (u : ℕ) * Gm M u x
      = ∑ s ∈ Ioo 0 (x : ℕ), v s * f s * cay ((x : ℕ) - s) := by
  have h1 : ∑ u : Fin (M + 1), v (u : ℕ) * f (u : ℕ) * Gm M u x
      = ∑ u ∈ range (M + 1), v u * f u * (if u < (x : ℕ) then cay ((x : ℕ) - u) else 0) :=
    Fin.sum_univ_eq_sum_range
      (fun u => v u * f u * (if u < (x : ℕ) then cay ((x : ℕ) - u) else 0)) (M + 1)
  rw [h1]
  have hsub : Ioo 0 (x : ℕ) ⊆ range (M + 1) := by
    intro u hu
    rw [mem_Ioo] at hu
    rw [mem_range]
    have := x.isLt
    omega
  rw [← Finset.sum_subset hsub]
  · apply Finset.sum_congr rfl
    intro s hs
    rw [mem_Ioo] at hs
    rw [ite_eq_left hs.2]
  · intro u _ hnot
    rw [mem_Ioo] at hnot
    by_cases h0 : u = 0
    · rw [h0, hv, zero_mul, zero_mul]
    · have h2 : ¬ (u < (x : ℕ)) := by omega
      rw [ite_eq_right h2, mul_zero]

/-- The entry `(0, x)` of `G (F G)^q` is the weight of the compositions of `x` with `q+1` parts. -/
private theorem bridge (M : ℕ) (f : ℕ → ℝ) (q : ℕ) :
    ∀ x : Fin (M + 1), (Gm M * (Dg M f * Gm M) ^ q) 0 x = Vc f (q + 1) (x : ℕ) := by
  induction q with
  | zero =>
    intro x
    rw [pow_zero, mul_one, Gm_apply, zero_add, Vc_one, Fin.val_zero]
    by_cases hx : 0 < (x : ℕ)
    · rw [ite_eq_left hx, Nat.sub_zero]
    · have hx0 : (x : ℕ) = 0 := by omega
      rw [ite_eq_right hx, hx0, cay_zero]
  | succ q ih =>
    intro x
    have e : Gm M * (Dg M f * Gm M) ^ (q + 1)
        = Gm M * (Dg M f * Gm M) ^ q * Dg M f * Gm M := by
      rw [pow_succ]
      simp only [mul_assoc]
    rw [e, Matrix.mul_apply, Vc_succ_succ,
      ← bridge_sum M (fun s => Vc f (q + 1) s) f (Vc_eq_zero_of_lt f (Nat.succ_pos q)) x]
    apply Finset.sum_congr rfl
    intro u _
    rw [mul_Dg_apply, ih u]

/-! ### Words `(G F)^a C (F G)^b` and their `(0, M)` entry -/

/-- Entry `(0, M)` of the word `(G F)^a C (F G)^b`, where `F = Dg M f`. -/
private noncomputable def Ew (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (C : Mat M) : ℝ :=
  ((Gm M * Dg M f) ^ a * C * (Dg M f * Gm M) ^ b) 0 (Fin.last M)

private theorem Ew_add (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (C₁ C₂ : Mat M) :
    Ew M f a b (C₁ + C₂) = Ew M f a b C₁ + Ew M f a b C₂ := by
  unfold Ew
  rw [mul_add, add_mul, Matrix.add_apply]

private theorem Ew_sub (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (C₁ C₂ : Mat M) :
    Ew M f a b (C₁ - C₂) = Ew M f a b C₁ - Ew M f a b C₂ := by
  unfold Ew
  rw [mul_sub, sub_mul, Matrix.sub_apply]

private theorem Ew_smul (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (c : ℝ) (C : Mat M) :
    Ew M f a b (c • C) = c * Ew M f a b C := by
  unfold Ew
  rw [Matrix.mul_smul, Matrix.smul_mul, Matrix.smul_apply, smul_eq_mul]

private theorem Ew_zero (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) : Ew M f a b 0 = 0 := by
  unfold Ew
  rw [mul_zero, zero_mul, Matrix.zero_apply]

private theorem Ew_Km (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) :
    Ew M f a b (Km M) = Ew M f a b (Hm M * Xm M) - Ew M f a b (Xm M * Hm M) :=
  Ew_sub M f a b (Hm M * Xm M) (Xm M * Hm M)

/-- A word absorbs a factor `F G` on the right of the marked factor. -/
private theorem Ew_right (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (C : Mat M) :
    Ew M f a b (C * Dg M f * Gm M) = Ew M f a (b + 1) C := by
  unfold Ew
  rw [pow_succ']
  simp only [mul_assoc]

/-- A word absorbs a factor `G F` on the left of the marked factor. -/
private theorem Ew_left (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) (C : Mat M) :
    Ew M f a b (Gm M * Dg M f * C) = Ew M f (a + 1) b C := by
  unfold Ew
  rw [pow_succ]
  simp only [mul_assoc]

private theorem Ew_G (M : ℕ) (f : ℕ → ℝ) (a b : ℕ) : Ew M f a b (Gm M) = Vc f (a + b + 1) M := by
  unfold Ew
  rw [mul_pow_mul, mul_assoc, ← pow_add, bridge, Fin.val_last]

private theorem Ew_nonneg (M : ℕ) {f : ℕ → ℝ} (hf : ∀ s, s ≤ M → 0 ≤ f s) (a b : ℕ) {C : Mat M}
    (hC : IsNonneg C) : 0 ≤ Ew M f a b C := by
  have hG := isNonneg_Gm M
  have hF := isNonneg_Dg M hf
  have h1 : IsNonneg ((Gm M * Dg M f) ^ a) := (hG.mul hF).pow a
  have h2 : IsNonneg ((Dg M f * Gm M) ^ b) := (hF.mul hG).pow b
  exact ((h1.mul hC).mul h2) 0 (Fin.last M)

/-! ### The Leibniz rule for commutators with a diagonal matrix -/

/-- Leibniz rule for `A ↦ A Z - Z A` on the word `G (F G)^q`, when `Z` commutes with `F`. -/
private theorem leibniz {R : Type*} [Ring R] (G F Z : R) (hZ : F * Z = Z * F) (q : ℕ) :
    G * (F * G) ^ q * Z - Z * (G * (F * G) ^ q)
      = ∑ p ∈ range (q + 1), (G * F) ^ p * (G * Z - Z * G) * (F * G) ^ (q - p) := by
  induction q with
  | zero => simp
  | succ q ih =>
    have hsum : ∑ p ∈ range (q + 1), (G * F) ^ p * (G * Z - Z * G) * (F * G) ^ (q + 1 - p)
        = (∑ p ∈ range (q + 1), (G * F) ^ p * (G * Z - Z * G) * (F * G) ^ (q - p)) * (F * G) := by
      rw [Finset.sum_mul]
      apply Finset.sum_congr rfl
      intro p hp
      rw [mem_range] at hp
      have e : q + 1 - p = (q - p) + 1 := by omega
      rw [e, pow_succ, ← mul_assoc]
    have hW : (G * F) ^ (q + 1) = G * (F * G) ^ q * F := by
      rw [pow_succ, ← mul_assoc, mul_pow_mul]
    have hZ' : ∀ A : R, F * (Z * A) = Z * (F * A) := fun A => by
      rw [← mul_assoc, hZ, mul_assoc]
    rw [Finset.sum_range_succ, hsum, ← ih, Nat.sub_self, pow_zero, mul_one, hW, pow_succ]
    simp only [mul_sub, sub_mul, mul_assoc, hZ']
    abel

/-- Entry form of the Leibniz rule. -/
private theorem Ew_leibniz (M : ℕ) (f z : ℕ → ℝ) (q : ℕ) :
    ∑ p ∈ range (q + 1), Ew M f p (q - p) (Gm M * Dg M z - Dg M z * Gm M)
      = (z M - z 0) * Vc f (q + 1) M := by
  have h := Matrix.ext_iff.mpr (leibniz (Gm M) (Dg M f) (Dg M z) (Dg_comm M f z) q) 0 (Fin.last M)
  rw [Matrix.sub_apply, mul_Dg_apply, Dg_mul_apply, bridge, Matrix.sum_apply] at h
  simp only [Fin.val_zero, Fin.val_last] at h
  have h' : ∑ p ∈ range (q + 1), Ew M f p (q - p) (Gm M * Dg M z - Dg M z * Gm M)
      = Vc f (q + 1) M * z M - z 0 * Vc f (q + 1) M := h.symm
  rw [h']
  ring

private theorem sum_Ew_Hm (M : ℕ) (f : ℕ → ℝ) (q : ℕ) :
    ∑ p ∈ range (q + 1), Ew M f p (q - p) (Hm M) = (M : ℝ) * Vc f (q + 1) M := by
  have h := Ew_leibniz M f (fun s => (s : ℝ)) q
  simp only [Nat.cast_zero, sub_zero] at h
  exact h

private theorem sum_Ew_sq (M : ℕ) (f : ℕ → ℝ) (q : ℕ) :
    ∑ p ∈ range (q + 1), Ew M f p (q - p) (Hm M * Xm M + Xm M * Hm M)
      = (M : ℝ) ^ 2 * Vc f (q + 1) M := by
  have h := Ew_leibniz M f (fun s => (s : ℝ) * (s : ℝ)) q
  have e : Hm M * Xm M + Xm M * Hm M
      = Gm M * Dg M (fun s => (s : ℝ) * (s : ℝ)) - Dg M (fun s => (s : ℝ) * (s : ℝ)) * Gm M := by
    have hX : Dg M (fun s => (s : ℝ) * (s : ℝ)) = Xm M * Xm M := by
      unfold Xm Dg
      rw [Matrix.diagonal_mul_diagonal]
    rw [hX]
    unfold Hm
    simp only [mul_sub, sub_mul, mul_assoc]
    abel
  rw [e, h]
  simp only [Nat.cast_zero, mul_zero, sub_zero]
  ring

/-! ### The erasure identity -/

/-- The erasure identity (E1), entry `(0, M)`. -/
private theorem E1 (M : ℕ) (f : ℕ → ℝ) (r : ℕ) :
    ∑ p ∈ range (r + 1), (((r : ℝ) + 1 - p) * Ew M f p (r - p) (Hm M * Gm M)
        + ((p : ℝ) + 1) * Ew M f p (r - p) (Gm M * Hm M))
      = ((r : ℝ) + 2) * ((M : ℝ) - (r + 1)) * Vc f (r + 1) M := by
  have hterm : ∀ p ∈ range (r + 1), (((r : ℝ) + 1 - p) * Ew M f p (r - p) (Hm M * Gm M)
        + ((p : ℝ) + 1) * Ew M f p (r - p) (Gm M * Hm M))
      = ((r : ℝ) + 2) * Ew M f p (r - p) (Hm M) - ((r : ℝ) + 2) * Vc f (r + 1) M := by
    intro p hp
    rw [mem_range] at hp
    have e : p + (r - p) + 1 = r + 1 := by omega
    rw [FI_left, FI_right, Ew_sub, Ew_G, e]
    ring
  rw [Finset.sum_congr rfl hterm, Finset.sum_sub_distrib, ← Finset.mul_sum, sum_Ew_Hm,
    Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  push_cast
  ring

/-- The shifted sum of the words with marked factor `δG`. -/
private theorem sum_e (M : ℕ) (f : ℕ → ℝ) (r : ℕ) :
    ∑ p ∈ range (r + 1), (((r : ℝ) + 1 - p) * Ew M f p (r + 1 - p) (Hm M)
        + ((p : ℝ) + 1) * Ew M f (p + 1) (r + 1 - (p + 1)) (Hm M))
      = ((r : ℝ) + 1) * ((M : ℝ) * Vc f (r + 2) M) := by
  have hs : ∑ p ∈ range (r + 1), (((r : ℝ) + 1 - p) * Ew M f p (r + 1 - p) (Hm M)
        + ((p : ℝ) + 1) * Ew M f (p + 1) (r + 1 - (p + 1)) (Hm M))
      = ∑ p ∈ range (r + 2), (((r : ℝ) + 1 - p) * Ew M f p (r + 1 - p) (Hm M)
        + (p : ℝ) * Ew M f p (r + 1 - p) (Hm M)) :=
    sum_shift (fun p => Ew M f p (r + 1 - p) (Hm M)) (fun p => Ew M f p (r + 1 - p) (Hm M))
      (r + 1) ((r : ℝ) + 1) (Nat.cast_succ r).symm
  have hL : ∑ p ∈ range (r + 2), Ew M f p (r + 1 - p) (Hm M) = (M : ℝ) * Vc f (r + 2) M :=
    sum_Ew_Hm M f (r + 1)
  rw [hs, ← hL, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro p _
  ring

/-- Consequence of (E1) for a general profile: the defect of the ratio inequality is a sum of words
containing the factor `1 - F`. -/
private theorem ID2 (M : ℕ) (f : ℕ → ℝ) (r : ℕ) :
    ((r : ℝ) + 2) * ((M : ℝ) - (r + 1)) * Vc f (r + 1) M - ((r : ℝ) + 1) * M * Vc f (r + 2) M
      = ∑ p ∈ range (r + 1),
          (((r : ℝ) + 1 - p) * Ew M f p (r - p) (Hm M * Dg M (fun s => 1 - f s) * Gm M)
            + ((p : ℝ) + 1) * Ew M f p (r - p) (Gm M * Dg M (fun s => 1 - f s) * Hm M)) := by
  have hterm : ∀ p ∈ range (r + 1),
      (((r : ℝ) + 1 - p) * Ew M f p (r - p) (Hm M * Dg M (fun s => 1 - f s) * Gm M)
          + ((p : ℝ) + 1) * Ew M f p (r - p) (Gm M * Dg M (fun s => 1 - f s) * Hm M))
      = (((r : ℝ) + 1 - p) * Ew M f p (r - p) (Hm M * Gm M)
          + ((p : ℝ) + 1) * Ew M f p (r - p) (Gm M * Hm M))
        - (((r : ℝ) + 1 - p) * Ew M f p (r + 1 - p) (Hm M)
          + ((p : ℝ) + 1) * Ew M f (p + 1) (r + 1 - (p + 1)) (Hm M)) := by
    intro p hp
    rw [mem_range] at hp
    have e1 : r + 1 - p = (r - p) + 1 := by omega
    have e2 : r + 1 - (p + 1) = r - p := by omega
    have m1 : Hm M * Dg M (fun s => 1 - f s) * Gm M
        = Hm M * Gm M - Hm M * Dg M f * Gm M := by
      rw [Dg_one_sub, mul_sub, mul_one, sub_mul]
    have m2 : Gm M * Dg M (fun s => 1 - f s) * Hm M
        = Gm M * Hm M - Gm M * Dg M f * Hm M := by
      rw [Dg_one_sub, mul_sub, mul_one, sub_mul]
    rw [m1, m2, Ew_sub, Ew_sub, Ew_right, Ew_left, e1, e2]
    ring
  rw [Finset.sum_congr rfl hterm, Finset.sum_sub_distrib, E1, sum_e]
  ring

/-- `Tq_ratio` in the form `q = r + 1`. -/
private theorem Tq_aux (m r : ℕ) :
    ((r : ℝ) + 1) * m * Vc (fun _ => (1 : ℝ)) (r + 2) m
      = ((r : ℝ) + 2) * ((m : ℝ) - (r + 1)) * Vc (fun _ => (1 : ℝ)) (r + 1) m := by
  have h := ID2 m (fun _ => (1 : ℝ)) r
  simp only [sub_self, Dg_zero, mul_zero, zero_mul, Ew_zero, add_zero,
    Finset.sum_const_zero] at h
  linarith

/-- `Vc_ratio_le` in the form `q = r + 1`, for a profile with values in `[0,1]` everywhere. -/
private theorem ratio_le_aux (m : ℕ) {g : ℕ → ℝ} (hg0 : ∀ s, 0 ≤ g s) (hg1 : ∀ s, g s ≤ 1) (r : ℕ) :
    ((r : ℝ) + 1) * m * Vc g (r + 2) m
      ≤ ((r : ℝ) + 2) * ((m : ℝ) - (r + 1)) * Vc g (r + 1) m := by
  have h := ID2 m g r
  have hD : IsNonneg (Dg m (fun s => 1 - g s)) :=
    isNonneg_Dg m (fun s _ => sub_nonneg.mpr (hg1 s))
  have hF : ∀ s, s ≤ m → 0 ≤ g s := fun s _ => hg0 s
  have hnn : 0 ≤ ∑ p ∈ range (r + 1),
      (((r : ℝ) + 1 - p) * Ew m g p (r - p) (Hm m * Dg m (fun s => 1 - g s) * Gm m)
        + ((p : ℝ) + 1) * Ew m g p (r - p) (Gm m * Dg m (fun s => 1 - g s) * Hm m)) := by
    apply Finset.sum_nonneg
    intro p hp
    rw [mem_range] at hp
    have c1 : (0 : ℝ) ≤ (r : ℝ) + 1 - p := by
      have : (p : ℝ) ≤ r := by exact_mod_cast Nat.lt_succ_iff.mp hp
      linarith
    have c2 : (0 : ℝ) ≤ (p : ℝ) + 1 := by positivity
    exact add_nonneg
      (mul_nonneg c1 (Ew_nonneg m (f := g) hF p (r - p)
        (((isNonneg_Hm m).mul hD).mul (isNonneg_Gm m))))
      (mul_nonneg c2 (Ew_nonneg m (f := g) hF p (r - p)
        (((isNonneg_Gm m).mul hD).mul (isNonneg_Hm m))))
  linarith

/-! ### The threshold profile -/

private theorem thr_mono (m : ℕ) (N : ℝ) (hN : (m : ℝ) < N) (a b : ℕ) (hab : a ≤ b) (hb : b ≤ m) :
    thr 1 N a ≤ thr 1 N b := by
  have hb' : (b : ℝ) ≤ m := by exact_mod_cast hb
  have hab' : (a : ℝ) ≤ b := by exact_mod_cast hab
  have e1 : thr 1 N a = 1 / (N - (a : ℝ)) := rfl
  have e2 : thr 1 N b = 1 / (N - (b : ℝ)) := rfl
  rw [e1, e2]
  exact one_div_le_one_div_of_le (by linarith) (by linarith)

private theorem thr_one_mul (N : ℝ) (s : ℕ) (h : N - (s : ℝ) ≠ 0) :
    N * thr 1 N s - thr 1 N s * (s : ℝ) = 1 := by
  have e : thr 1 N s = 1 / (N - (s : ℝ)) := rfl
  rw [e]
  have e2 : N * (1 / (N - (s : ℝ))) - 1 / (N - (s : ℝ)) * (s : ℝ)
      = (N - (s : ℝ)) / (N - (s : ℝ)) := by ring
  rw [e2, div_self h]

/-- `F Y = 1` for `F = diag (1/(N-s))`, `Y = N - X`, written as `N F - F X = 1`. -/
private theorem thr_diag (m : ℕ) (N : ℝ) (hN : (m : ℝ) < N) :
    N • Dg m (thr 1 N) - Dg m (thr 1 N) * Xm m = 1 := by
  ext i j
  rw [Matrix.sub_apply, Matrix.smul_apply, mul_Xm_apply, Dg_apply, Matrix.one_apply, smul_eq_mul]
  by_cases h : i = j
  · rw [ite_eq_left h, ite_eq_left h, ← h]
    have hi : ((i : ℕ) : ℝ) ≤ m := by exact_mod_cast Nat.lt_succ_iff.mp i.isLt
    have hne : N - ((i : ℕ) : ℝ) ≠ 0 := by
      have : 0 < N - ((i : ℕ) : ℝ) := by linarith
      exact ne_of_gt this
    exact thr_one_mul N (i : ℕ) hne
  · rw [ite_eq_right h, ite_eq_right h]
    ring

private theorem KFG_apply (M : ℕ) (L : ℕ → ℝ) (i j : Fin (M + 1)) :
    (Km M * Dg M L * Gm M) i j
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)),
          ((α : ℝ) ^ 2 * cay α) * L ((i : ℕ) + α) * cay ((j : ℕ) - (i : ℕ) - α) := by
  rw [Matrix.mul_apply]
  have h := sum_mid M (fun α => (α : ℝ) ^ 2 * cay α) cay L (by simp) i j
  simp only [mul_Dg_apply, Km_apply, Gm_apply]
  exact h

private theorem GFK_apply (M : ℕ) (L : ℕ → ℝ) (i j : Fin (M + 1)) :
    (Gm M * Dg M L * Km M) i j
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)),
          cay α * L ((i : ℕ) + α)
            * ((((j : ℕ) - (i : ℕ) - α : ℕ) : ℝ) ^ 2 * cay ((j : ℕ) - (i : ℕ) - α)) := by
  rw [Matrix.mul_apply]
  have h := sum_mid M cay (fun β => (β : ℝ) ^ 2 * cay β) L cay_zero i j
  simp only [mul_Dg_apply, Km_apply, Gm_apply]
  exact h

/-- `(δ²G) F G - G F (δ²G)` is entrywise nonnegative when the profile is nondecreasing. -/
private theorem isNonneg_Yr (M : ℕ) (L : ℕ → ℝ) (hL : ∀ a b, a ≤ b → b ≤ M → L a ≤ L b) :
    IsNonneg (Km M * Dg M L * Gm M - Gm M * Dg M L * Km M) := by
  intro i j
  rw [Matrix.sub_apply, KFG_apply, GFK_apply, ← Finset.sum_sub_distrib]
  have h3 := refl_sum_nonneg ((j : ℕ) - (i : ℕ)) (fun α => L ((i : ℕ) + α)) (by
    intro a b hab hb
    apply hL
    · omega
    · have h1 := j.isLt
      have h2 := i.isLt
      omega)
  have h4 : ∑ α ∈ range ((j : ℕ) - (i : ℕ)),
        (((α : ℝ) ^ 2 * cay α) * L ((i : ℕ) + α) * cay ((j : ℕ) - (i : ℕ) - α)
          - cay α * L ((i : ℕ) + α)
            * ((((j : ℕ) - (i : ℕ) - α : ℕ) : ℝ) ^ 2 * cay ((j : ℕ) - (i : ℕ) - α)))
      = ∑ α ∈ range ((j : ℕ) - (i : ℕ)),
        L ((i : ℕ) + α) * (cay α * cay ((j : ℕ) - (i : ℕ) - α)
          * ((α : ℝ) ^ 2 - (((j : ℕ) - (i : ℕ) - α : ℕ) : ℝ) ^ 2)) := by
    apply Finset.sum_congr rfl
    intro α _
    ring
  rw [h4]
  exact h3

/-- `Vc_thr_ratio_ge` in the form `q = r + 1`. -/
private theorem thr_aux (m : ℕ) (N : ℝ) (hN : (m : ℝ) < N) (r : ℕ) :
    ((r : ℝ) + 2) * ((m : ℝ) - (r + 1)) * Vc (thr 1 N) (r + 1) m
      ≤ ((r : ℝ) + 1) * m * (N - (m : ℝ) / 2) * Vc (thr 1 N) (r + 2) m := by
  have hL0 : ∀ s, s ≤ m → 0 ≤ thr 1 N s := fun s hs =>
    thr_nonneg zero_le_one (le_trans (Nat.cast_le.2 hs) hN.le)
  have hLmono : ∀ a b, a ≤ b → b ≤ m → thr 1 N a ≤ thr 1 N b := thr_mono m N hN
  have hFY := thr_diag m N hN
  have hFX : Dg m (thr 1 N) * Xm m = Xm m * Dg m (thr 1 N) :=
    Dg_comm m (thr 1 N) (fun s => (s : ℝ))
  -- insertion of `1 = N F - F X` next to the marked factor
  have hHG : Hm m * Gm m
      = N • (Hm m * Dg m (thr 1 N) * Gm m) - Hm m * Xm m * Dg m (thr 1 N) * Gm m := by
    have h0 : Hm m * Gm m
        = Hm m * (N • Dg m (thr 1 N) - Dg m (thr 1 N) * Xm m) * Gm m := by
      rw [hFY, mul_one]
    rw [h0, mul_sub, sub_mul, Matrix.mul_smul, Matrix.smul_mul, hFX, ← mul_assoc (Hm m)]
  have hGH : Gm m * Hm m
      = N • (Gm m * Dg m (thr 1 N) * Hm m) - Gm m * Dg m (thr 1 N) * (Xm m * Hm m) := by
    have h0 : Gm m * Hm m
        = Gm m * (N • Dg m (thr 1 N) - Dg m (thr 1 N) * Xm m) * Hm m := by
      rw [hFY, mul_one]
    rw [h0, mul_sub, sub_mul, Matrix.mul_smul, Matrix.smul_mul, ← mul_assoc (Gm m),
      mul_assoc (Gm m * Dg m (thr 1 N))]
  have hterm : ∀ p ∈ range (r + 1),
      (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r - p) (Hm m * Gm m)
        + ((p : ℝ) + 1) * Ew m (thr 1 N) p (r - p) (Gm m * Hm m))
      = N * (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r + 1 - p) (Hm m)
          + ((p : ℝ) + 1) * Ew m (thr 1 N) (p + 1) (r + 1 - (p + 1)) (Hm m))
        - (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m)
          + ((p : ℝ) + 1) * Ew m (thr 1 N) (p + 1) (r + 1 - (p + 1)) (Xm m * Hm m)) := by
    intro p hp
    rw [mem_range] at hp
    have e1 : r + 1 - p = (r - p) + 1 := by omega
    have e2 : r + 1 - (p + 1) = r - p := by omega
    rw [hHG, hGH, Ew_sub, Ew_sub, Ew_smul, Ew_smul, Ew_right, Ew_right, Ew_left, Ew_left,
      e1, e2]
    ring
  have hE1 := E1 m (thr 1 N) r
  rw [Finset.sum_congr rfl hterm, Finset.sum_sub_distrib, ← Finset.mul_sum, sum_e] at hE1
  -- the remaining sum, regrouped by the position of the marked factor
  have hB : ∑ p ∈ range (r + 1),
        (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m)
          + ((p : ℝ) + 1) * Ew m (thr 1 N) (p + 1) (r + 1 - (p + 1)) (Xm m * Hm m))
      = ∑ p ∈ range (r + 2),
        (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m)
          + (p : ℝ) * Ew m (thr 1 N) p (r + 1 - p) (Xm m * Hm m)) :=
    sum_shift (fun p => Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m))
      (fun p => Ew m (thr 1 N) p (r + 1 - p) (Xm m * Hm m)) (r + 1) ((r : ℝ) + 1)
      (Nat.cast_succ r).symm
  have hsq : ∑ p ∈ range (r + 2), Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m + Xm m * Hm m)
      = (m : ℝ) ^ 2 * Vc (thr 1 N) (r + 2) m := sum_Ew_sq m (thr 1 N) (r + 1)
  have hC : ∑ p ∈ range (r + 2),
        (((r : ℝ) + 1 - p) * Ew m (thr 1 N) p (r + 1 - p) (Hm m * Xm m)
          + (p : ℝ) * Ew m (thr 1 N) p (r + 1 - p) (Xm m * Hm m))
      = ((r : ℝ) + 1) / 2 * ((m : ℝ) ^ 2 * Vc (thr 1 N) (r + 2) m)
        + 1 / 2 * ∑ p ∈ range (r + 2),
            (((r + 1 : ℕ) : ℝ) - 2 * p) * Ew m (thr 1 N) p (r + 1 - p) (Km m) := by
    rw [← hsq, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro p _
    rw [Ew_Km, Ew_add]
    push_cast
    ring
  -- monotonicity of the words with marked factor `δ²G`
  have hmono : ∀ p, p < r + 1 →
      (fun p => Ew m (thr 1 N) p (r + 1 - p) (Km m)) (p + 1)
        ≤ (fun p => Ew m (thr 1 N) p (r + 1 - p) (Km m)) p := by
    intro p hp
    show Ew m (thr 1 N) (p + 1) (r + 1 - (p + 1)) (Km m)
      ≤ Ew m (thr 1 N) p (r + 1 - p) (Km m)
    have e1 : r + 1 - p = (r + 1 - (p + 1)) + 1 := by omega
    have hr : Ew m (thr 1 N) p (r + 1 - p) (Km m)
        = Ew m (thr 1 N) p (r + 1 - (p + 1)) (Km m * Dg m (thr 1 N) * Gm m) := by
      rw [Ew_right, ← e1]
    have hl : Ew m (thr 1 N) (p + 1) (r + 1 - (p + 1)) (Km m)
        = Ew m (thr 1 N) p (r + 1 - (p + 1)) (Gm m * Dg m (thr 1 N) * Km m) :=
      (Ew_left m (thr 1 N) p (r + 1 - (p + 1)) (Km m)).symm
    have hY := Ew_nonneg m (f := thr 1 N) hL0 p (r + 1 - (p + 1))
      (isNonneg_Yr m (thr 1 N) hLmono)
    rw [Ew_sub] at hY
    rw [hr, hl]
    linarith
  have hnn : 0 ≤ ∑ p ∈ range (r + 2),
      (((r + 1 : ℕ) : ℝ) - 2 * p) * Ew m (thr 1 N) p (r + 1 - p) (Km m) :=
    sum_antitone_nonneg (fun p => Ew m (thr 1 N) p (r + 1 - p) (Km m)) (r + 1) hmono
  rw [hB, hC] at hE1
  linarith

end CompRatio

/-! ### The three ratio statements -/

/-- For the compositions of $m$ in which a part of size $p$ weighs $a_p=p^{p-1}/p!$ and the cuts
contribute no factor, the total weights $T_{m,q}$ and $T_{m,q+1}$ of the compositions with $q$
and with $q+1$ parts satisfy $q\,m\,T_{m,q+1}=(q+1)(m-q)\,T_{m,q}$ for every $q\ge1$. -/
theorem Tq_ratio (m : ℕ) {q : ℕ} (hq : 1 ≤ q) :
    (q : ℝ) * m * Tq m (q + 1) = ((q : ℝ) + 1) * ((m : ℝ) - q) * Tq m q := by
  obtain ⟨r, rfl⟩ : ∃ r, q = r + 1 := ⟨q - 1, by omega⟩
  have h := CompRatio.Tq_aux m r
  have h2 : Tq m (r + 1 + 1) = Vc (fun _ => (1 : ℝ)) (r + 2) m := rfl
  have h1 : Tq m (r + 1) = Vc (fun _ => (1 : ℝ)) (r + 1) m := rfl
  rw [h2, h1]
  simp only [Nat.cast_add, Nat.cast_one]
  linarith

/-- If every cut of a composition of $m$ carries a factor between $0$ and $1$, the total weights
$V_q$ and $V_{q+1}$ of the compositions with $q$ and with $q+1$ parts satisfy
$q\,m\,V_{q+1}\le(q+1)(m-q)\,V_q$ for every $q\ge1$: the ratio $V_{q+1}/V_q$ is at most its
value when every cut has the factor $1$. -/
theorem Vc_ratio_le {f : ℕ → ℝ} {m : ℕ} (hf : ∀ s ∈ Ioo 0 m, 0 ≤ f s ∧ f s ≤ 1) {q : ℕ}
    (hq : 1 ≤ q) :
    (q : ℝ) * m * Vc f (q + 1) m ≤ ((q : ℝ) + 1) * ((m : ℝ) - q) * Vc f q m := by
  obtain ⟨r, rfl⟩ : ∃ r, q = r + 1 := ⟨q - 1, by omega⟩
  have hfg : ∀ s ∈ Ioo 0 m, f s = (fun s => if s ∈ Ioo 0 m then f s else 0) s := by
    intro s hs
    exact (ite_eq_left hs).symm
  have hg0 : ∀ s, 0 ≤ (fun s => if s ∈ Ioo 0 m then f s else 0) s := by
    intro s
    show 0 ≤ if s ∈ Ioo 0 m then f s else 0
    split_ifs with hs
    · exact (hf s hs).1
    · exact le_refl 0
  have hg1 : ∀ s, (fun s => if s ∈ Ioo 0 m then f s else 0) s ≤ 1 := by
    intro s
    show (if s ∈ Ioo 0 m then f s else 0) ≤ 1
    split_ifs with hs
    · exact (hf s hs).2
    · exact zero_le_one
  have h := CompRatio.ratio_le_aux m (g := fun s => if s ∈ Ioo 0 m then f s else 0) hg0 hg1 r
  have e2 : Vc f (r + 1 + 1) m = Vc (fun s => if s ∈ Ioo 0 m then f s else 0) (r + 2) m :=
    Vc_congr hfg (r + 2)
  have e1 : Vc f (r + 1) m = Vc (fun s => if s ∈ Ioo 0 m then f s else 0) (r + 1) m :=
    Vc_congr hfg (r + 1)
  rw [e2, e1]
  simp only [Nat.cast_add, Nat.cast_one]
  linarith

/-- For the cut profile $s\mapsto1/(N-s)$ with $N>m$, the total weights $V_q$ and $V_{q+1}$ of the
compositions of $m$ with $q$ and with $q+1$ parts satisfy $(q+1)(m-q)\,V_q\le q\,m\,(N-\tfrac
m2)\,V_{q+1}$ for every $q\ge1$: the ratio $V_{q+1}/V_q$ is at least its value for the constant
profile equal to the threshold profile at the midpoint $m/2$. -/
theorem Vc_thr_ratio_ge {m : ℕ} {N : ℝ} (hN : (m : ℝ) < N) {q : ℕ} (hq : 1 ≤ q) :
    ((q : ℝ) + 1) * ((m : ℝ) - q) * Vc (thr 1 N) q m
      ≤ (q : ℝ) * m * (N - (m : ℝ) / 2) * Vc (thr 1 N) (q + 1) m := by
  obtain ⟨r, rfl⟩ : ∃ r, q = r + 1 := ⟨q - 1, by omega⟩
  have h := CompRatio.thr_aux m N hN r
  have e : Vc (thr 1 N) (r + 1 + 1) m = Vc (thr 1 N) (r + 2) m := rfl
  rw [e]
  simp only [Nat.cast_add, Nat.cast_one]
  linarith

end Parking
