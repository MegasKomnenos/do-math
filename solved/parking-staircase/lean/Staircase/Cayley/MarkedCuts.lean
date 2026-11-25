import Parking.NextColumn.Compositions
import Batteries.Tactic.OpenPrivate

/-!
# Compositions with marked cut points

A composition of `m` with `q` parts has `q - 1` cut points.  `Lam1 f m` is the total weight, for the
cut profile `f`, of the compositions of `m` in which one cut point is marked, and `Lam2 f m` the
total weight of those in which two cut points are marked.  A marked cut point `a` splits a
composition of `m` into a composition of `a` and a composition of `m - a`, the second with the
profile shifted by `a`; this is how the two sums are defined.

The module proves that marking counts cut points:

* `Lam1_eq_sum` : `Lam1 f m = ∑_q (q-1) · V_q(m;f)`,
* `Lam2_eq_sum` : `Lam2 f m = ∑_q (q-1)(q-2)/2 · V_q(m;f)`,
* `sum_qq_Vc`   : `∑_q q(q-1) · V_q(m;f) = 2·Lam1 f m + 2·Lam2 f m`,

where `V_q(m;f) = Vc f q m` is the weight of the compositions with `q` parts, and the recursion
`Lam2_last` of `Lam2` on the last part.

Method.  For a weight `c` on the number of cut points let `S_c(m) = ∑_q c(q) · V_{q+1}(m;f)`.
Removing the last part of a composition gives a recursion for `S_c` (`cutSum_last`), and the same
operation gives a recursion for the sum in which a cut point of a composition is marked
(`mark_last`): the marked point is the last cut point, or the last cut point lies after it.
Comparing the two recursions shows that marking a cut point in `S_c` gives `S_d`, where
`d(q) = c(0) + ⋯ + c(q-1)` (`mark_cutSum`).  With `c = 1` this is `Lam1`, and with `c(q) = q` it is
`Lam2`.
-/

namespace Parking

open Finset

open private sum_Ioo_shift from Parking.NextColumn.Compositions

/-- Total weight of the compositions of `m` with one marked cut point `a`: the composition is cut
at `a` into a composition of `a` and a composition of `m - a`. -/
noncomputable def Lam1 (f : ℕ → ℝ) (m : ℕ) : ℝ :=
  ∑ a ∈ Ioo 0 m, Lam f a * f a * Lam (fun s => f (a + s)) (m - a)

/-- Total weight of the compositions of `m` with two marked cut points `a < b`: the composition is
cut at the larger marked point `b`, and the part below `b` carries the other mark. -/
noncomputable def Lam2 (f : ℕ → ℝ) (m : ℕ) : ℝ :=
  ∑ b ∈ Ioo 0 m, Lam1 f b * f b * Lam (fun s => f (b + s)) (m - b)

/-! ### Sums weighted by the number of cut points -/

/-- `S_c(m) = ∑_q c(q) · V_{q+1}(m;f)`: the compositions of `m`, each counted with a weight that
depends on its number `q` of cut points. -/
private noncomputable def cutSum (f : ℕ → ℝ) (c : ℕ → ℝ) (m : ℕ) : ℝ :=
  ∑ q ∈ range m, c q * Vc f (q + 1) m

/-- `S_c(m)` as a sum over `q < n` for any `n ≥ m`: a composition of `m` has fewer than `m` cut
points. -/
private theorem cutSum_eq_range (f c : ℕ → ℝ) {m n : ℕ} (h : m ≤ n) :
    cutSum f c m = ∑ q ∈ range n, c q * Vc f (q + 1) m := by
  refine Finset.sum_subset (Finset.range_subset_range.2 h) fun q _ hq => ?_
  rw [mem_range] at hq
  rw [Vc_eq_zero_of_lt f (by omega), mul_zero]

/-- With the weight `1`, `S_c` is the total weight of all compositions. -/
private theorem cutSum_one (f : ℕ → ℝ) (m : ℕ) : cutSum f (fun _ => 1) m = Lam f m := by
  unfold Lam cutSum
  rw [sum_Icc_one_eq_range]
  exact Finset.sum_congr rfl fun q _ => one_mul _

/-- Removing the last part of a composition lowers the number of cut points by one:
`S_c(m) = c(0)·a_m + ∑_{0<s<m} S_{c(·+1)}(s) · f(s) · a_{m-s}`. -/
private theorem cutSum_last (f c : ℕ → ℝ) (m : ℕ) :
    cutSum f c m
      = c 0 * cay m + ∑ s ∈ Ioo 0 m, cutSum f (fun q => c (q + 1)) s * f s * cay (m - s) := by
  cases m with
  | zero => simp [cutSum]
  | succ m =>
    have h1 : ∀ q ∈ range m, c (q + 1) * Vc f (q + 1 + 1) (m + 1)
        = ∑ s ∈ Ioo 0 (m + 1), c (q + 1) * Vc f (q + 1) s * f s * cay (m + 1 - s) := by
      intro q _
      rw [Vc_succ_succ f q (m + 1), Finset.mul_sum]
      exact Finset.sum_congr rfl fun s _ => by ring
    unfold cutSum
    rw [Finset.sum_range_succ', Vc_one, add_comm, Finset.sum_congr rfl h1, Finset.sum_comm]
    congr 1
    refine Finset.sum_congr rfl fun s hs => ?_
    rw [mem_Ioo] at hs
    have h2 := cutSum_eq_range f (fun q => c (q + 1)) (show s ≤ m by omega)
    unfold cutSum at h2
    rw [h2, Finset.sum_mul, Finset.sum_mul]

/-- Marking a cut point `b` of a composition of `m` whose part below `b` has the weight `g b`:
either `b` is the last cut point, or the last cut point `s` lies after `b`, and then `b` is a
marked cut point of the composition of `s` that remains when the last part is removed. -/
private theorem mark_last (f g : ℕ → ℝ) (m : ℕ) :
    ∑ b ∈ Ioo 0 m, g b * f b * Lam (fun s => f (b + s)) (m - b)
      = ∑ s ∈ Ioo 0 m, (g s + ∑ b ∈ Ioo 0 s, g b * f b * Lam (fun u => f (b + u)) (s - b))
          * f s * cay (m - s) := by
  have h1 : ∀ b ∈ Ioo 0 m, g b * f b * Lam (fun s => f (b + s)) (m - b)
      = g b * f b * cay (m - b)
        + ∑ s ∈ Ioo b m, g b * f b * Lam (fun u => f (b + u)) (s - b) * f s * cay (m - s) := by
    intro b _
    rw [Lam_last (fun s => f (b + s)) (m - b), mul_add, Finset.mul_sum, sum_Ioo_shift _ b m]
    congr 1
    refine Finset.sum_congr rfl fun s _ => ?_
    rw [show b + s - b = s by omega, show m - (b + s) = m - b - s by omega]
    ring
  have h2 : ∑ b ∈ Ioo 0 m, ∑ s ∈ Ioo b m,
        g b * f b * Lam (fun u => f (b + u)) (s - b) * f s * cay (m - s)
      = ∑ s ∈ Ioo 0 m, ∑ b ∈ Ioo 0 s,
        g b * f b * Lam (fun u => f (b + u)) (s - b) * f s * cay (m - s) :=
    Finset.sum_comm' (by intro x y; simp only [mem_Ioo]; omega)
  rw [Finset.sum_congr rfl h1, Finset.sum_add_distrib, h2, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun s _ => ?_
  rw [add_mul, add_mul, Finset.sum_mul, Finset.sum_mul]

/-- Marking a cut point in `S_c` gives `S_d` with `d(q) = c(0) + ⋯ + c(q-1)`: a composition with
`q` cut points arises once for each of its cut points, with the weight that `c` gives to the number
of cut points below the marked one.  Both sides satisfy the same recursion on the last part. -/
private theorem mark_cutSum (f c d : ℕ → ℝ) (h0 : d 0 = 0) (hd : ∀ q, d (q + 1) = d q + c q)
    (m : ℕ) :
    ∑ b ∈ Ioo 0 m, cutSum f c b * f b * Lam (fun s => f (b + s)) (m - b) = cutSum f d m := by
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    rw [mark_last f (cutSum f c) m, cutSum_last f d m, h0, zero_mul, zero_add]
    refine Finset.sum_congr rfl fun s hs => ?_
    have hsum : cutSum f (fun q => d (q + 1)) s = cutSum f c s + cutSum f d s := by
      unfold cutSum
      rw [← Finset.sum_add_distrib]
      exact Finset.sum_congr rfl fun q _ => by simp only [hd]; ring
    rw [ih s (mem_Ioo.1 hs).2, hsum]

/-- `Lam1 f m = ∑_q q · V_{q+1}(m;f)`. -/
private theorem Lam1_eq_cutSum (f : ℕ → ℝ) (m : ℕ) : Lam1 f m = cutSum f (fun q => (q : ℝ)) m := by
  have h := mark_cutSum f (fun _ => 1) (fun q => (q : ℝ)) Nat.cast_zero (fun q => Nat.cast_succ q) m
  simp only [cutSum_one] at h
  exact h

/-- `Lam2 f m = ∑_q q(q-1)/2 · V_{q+1}(m;f)`. -/
private theorem Lam2_eq_cutSum (f : ℕ → ℝ) (m : ℕ) :
    Lam2 f m = cutSum f (fun q => (q : ℝ) * ((q : ℝ) - 1) / 2) m := by
  have h := mark_cutSum f (fun q => (q : ℝ)) (fun q => (q : ℝ) * ((q : ℝ) - 1) / 2) (by simp)
    (fun q => by push_cast; ring) m
  simp only [← Lam1_eq_cutSum] at h
  exact h

/-- Last-part recursion for two marked cut points: the larger marked point is the last cut point
`s`, and then the composition of `s` below it carries one mark, or the last cut point `s` lies
after both marks: `Lam2 f m = ∑_{0<s<m} (Lam1 f s + Lam2 f s) · f(s) · a_{m-s}`. -/
theorem Lam2_last (f : ℕ → ℝ) (m : ℕ) :
    Lam2 f m = ∑ s ∈ Ioo 0 m, (Lam1 f s + Lam2 f s) * f s * cay (m - s) :=
  mark_last f (Lam1 f) m

/-! ### Marked cut points and the number of parts -/

/-- **One marked cut point.** The total weight of the compositions of `m` with one marked cut point
is `∑_q (q-1) · V_q(m;f)`, because a composition with `q` parts has `q - 1` cut points.  Both sides
satisfy the same recursion on the last part. -/
theorem Lam1_eq_sum (f : ℕ → ℝ) (m : ℕ) :
    Lam1 f m = ∑ q ∈ Icc 1 m, ((q : ℝ) - 1) * Vc f q m := by
  rw [Lam1_eq_cutSum, sum_Icc_one_eq_range]
  exact Finset.sum_congr rfl fun q _ => by push_cast; ring

/-- **Two marked cut points.** The total weight of the compositions of `m` with two marked cut
points is `∑_q (q-1)(q-2)/2 · V_q(m;f)`, the number of pairs among the `q - 1` cut points.  The
proof is that of `Lam1_eq_sum`, applied to `Lam1` in the place of `Lam`. -/
theorem Lam2_eq_sum (f : ℕ → ℝ) (m : ℕ) :
    Lam2 f m = ∑ q ∈ Icc 1 m, ((q : ℝ) - 1) * ((q : ℝ) - 2) / 2 * Vc f q m := by
  rw [Lam2_eq_cutSum, sum_Icc_one_eq_range]
  exact Finset.sum_congr rfl fun q _ => by push_cast; ring

/-- The second factorial moment of the number of parts: `∑_q q(q-1) · V_q(m;f) = 2·Lam1 f m +
2·Lam2 f m`, from `q(q-1) = 2(q-1) + (q-1)(q-2)`. -/
theorem sum_qq_Vc (f : ℕ → ℝ) (m : ℕ) :
    ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Vc f q m = 2 * Lam1 f m + 2 * Lam2 f m := by
  rw [Lam1_eq_sum, Lam2_eq_sum, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun q _ => by ring

end Parking
