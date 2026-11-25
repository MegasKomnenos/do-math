import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Intervals

/-!
# Sums over intervals of natural numbers

The recursions of this library are written as sums over `Finset.Icc`.  The rearrangements of
such sums that several proofs use are collected here: splitting at an interior point, shifting
the index to a sum over `Finset.range`, splitting off the first term, and dropping a tail of
vanishing terms.
-/

namespace Parking

open Finset

/-- Splitting a sum over `Icc a n` after `s`, where `a ≤ s + 1` and `s ≤ n`. -/
theorem sum_Icc_split (g : ℕ → ℝ) {a s n : ℕ} (has : a ≤ s + 1) (hsn : s ≤ n) :
    ∑ m ∈ Icc a n, g m = ∑ m ∈ Icc a s, g m + ∑ m ∈ Icc (s + 1) n, g m := by
  simp only [← Ico_add_one_right_eq_Icc]
  exact (sum_Ico_consecutive g has (Nat.succ_le_succ hsn)).symm

/-- `∑_{j=a+1}^{a+n} f j = ∑_{r<n} f (a+r+1)`. -/
theorem sum_Icc_eq_range (f : ℕ → ℝ) (a n : ℕ) :
    ∑ j ∈ Icc (a + 1) (a + n), f j = ∑ r ∈ range n, f (a + r + 1) := by
  induction n with
  | zero =>
    rw [Finset.Icc_eq_empty (show ¬ a + 1 ≤ a + 0 by omega), sum_empty, range_zero, sum_empty]
  | succ n ih =>
    have h := Finset.sum_Icc_succ_top (show a + 1 ≤ a + n + 1 by omega) f
    rw [sum_range_succ, ← ih]
    exact h

/-- A sum over `Icc 1 n` as a sum over `range n`. -/
theorem sum_Icc_one_eq_range (g : ℕ → ℝ) (n : ℕ) :
    ∑ m ∈ Icc 1 n, g m = ∑ i ∈ range n, g (i + 1) := by
  rw [← Nat.Ico_zero_eq_range, sum_Ico_add' g 0 n 1, Nat.zero_add, Ico_add_one_right_eq_Icc]

/-- If `f` vanishes on `(a, n]`, the sum over `Icc 1 n` reduces to the sum over `Icc 1 a`. -/
theorem sum_Icc_trunc {f : ℕ → ℝ} {a n : ℕ} (han : a ≤ n)
    (hf : ∀ m, a < m → m ≤ n → f m = 0) :
    ∑ m ∈ Icc 1 n, f m = ∑ m ∈ Icc 1 a, f m := by
  symm
  apply Finset.sum_subset
  · intro m hm
    rw [Finset.mem_Icc] at hm ⊢
    exact ⟨hm.1, le_trans hm.2 han⟩
  · intro m hm hm'
    rw [Finset.mem_Icc] at hm hm'
    exact hf m (by omega) hm.2

end Parking
