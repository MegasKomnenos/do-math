import Parking.LeftHalf.Main
import Parking.NextColumn.Main
import Parking.Table.Rows

/-!
# Unimodality of the rows

For every `n ≥ 1` the sequence `b n 0, …, b n (n-1)` is unimodal, where `b n ℓ`
(`Parking/Defs.lean`) is the number of parking functions of length `n` whose maximum displacement
is exactly `ℓ`.

Write `d_{n,k} = b n k - b n (k-1)` for the step of column `k` in the row `n`.  A row is unimodal
as soon as it has no strict descent followed by a strict ascent, that is, no pair
`1 ≤ i < j ≤ n - 1` with `d_{n,i} < 0 < d_{n,j}` (`unimodal_of_no_pair`).  There is no such
pair (`no_descent_ascent`):

* `n ≤ 16`: the rows are checked directly (`Tab.small_rows`).
* `n ≥ 17` and `2i ≤ n`: the left half (`left_half`) gives `d_{n,i} ≥ 0`.
* `n ≥ 17` and `n ≤ 2i - 1`: then `i ≥ 9`, and the row `n` lies in the chain range
  `j + 1 ≤ n ≤ 2j - 1` of every column `j ≥ i`.  By the persistence of the sign in the chain range
  (`chain_column_iter`) the column `i`, which is nonpositive in the row `n`, is nonpositive in all
  the rows `i + 1 ≤ m ≤ n`; by `mono` the same holds for the column `i + 1`, and then for every
  column `j ≥ i` (`right_tail`).  So `d_{n,j} ≤ 0`.
-/

namespace Parking

/-- A sequence `f` of natural numbers that has no pair `1 ≤ i < j ≤ N` with a strict descent at
`i` (`f i < f (i-1)`) and a strict ascent at `j` (`f (j-1) < f j`) is unimodal on the positions
`0, …, N`: for some `p ≤ N` it is nondecreasing up to `p` and nonincreasing from `p` on.

By induction on `N`, the position `p` is chosen so that, when `p < N`, there is a strict descent
right after it. -/
theorem unimodal_of_no_pair (f : ℕ → ℕ) (N : ℕ)
    (h : ∀ i j, 1 ≤ i → i < j → j ≤ N → f i < f (i - 1) → f (j - 1) < f j → False) :
    ∃ p, p ≤ N ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → f (ℓ - 1) ≤ f ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ N → f (ℓ + 1) ≤ f ℓ) := by
  suffices key : ∃ p, p ≤ N ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → f (ℓ - 1) ≤ f ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ N → f (ℓ + 1) ≤ f ℓ) ∧ (p < N → f (p + 1) < f p) by
    obtain ⟨p, h1, h2, h3, _⟩ := key
    exact ⟨p, h1, h2, h3⟩
  induction N with
  | zero =>
    exact ⟨0, le_refl 0, fun ℓ h1 h2 => by omega, fun ℓ h1 h2 => by omega, fun h0 => by omega⟩
  | succ N ih =>
    obtain ⟨p, hp, hup, hdown, hstrict⟩ :=
      ih (fun i j hi hij hj => h i j hi hij (by omega))
    rcases Nat.eq_or_lt_of_le hp with heq | hpN
    · -- `f` is nondecreasing up to `N`
      subst heq
      by_cases hasc : f p ≤ f (p + 1)
      · refine ⟨p + 1, le_refl _, fun ℓ h1 h2 => ?_, fun ℓ h1 h2 => by omega, fun h0 => by omega⟩
        rcases Nat.eq_or_lt_of_le h2 with rfl | hlt
        · exact hasc
        · exact hup ℓ h1 (by omega)
      · refine ⟨p, by omega, hup, fun ℓ h1 h2 => ?_, fun _ => not_le.mp hasc⟩
        have e : ℓ = p := by omega
        rw [e]
        exact (not_le.mp hasc).le
    · -- there is a strict descent at `p + 1 ≤ N`, so there is no strict ascent at `N + 1`
      have hle : f (N + 1) ≤ f N := by
        by_contra hcon
        exact h (p + 1) (N + 1) (by omega) (by omega) (le_refl _) (hstrict hpN) (not_le.mp hcon)
      refine ⟨p, by omega, hup, fun ℓ h1 h2 => ?_, fun _ => hstrict hpN⟩
      rcases Nat.eq_or_lt_of_le (show ℓ ≤ N by omega) with heq | hlt
      · rw [heq]
        exact hle
      · exact hdown ℓ h1 (by omega)

/-- **The right of the middle.**  Let `i ≥ 9` and `n ≤ 2i - 1`.  If the column `i` is nonpositive
in the row `n`, then every column `j ≥ i` is nonpositive in all the rows `j + 1 ≤ m ≤ n`.  For
`j = i` this is the persistence of the sign in the chain range (`chain_column_iter`); the step from
`j` to `j + 1` is `mono`. -/
theorem right_tail {n i : ℕ} (hi : 9 ≤ i) (hn : n + 1 ≤ 2 * i) (h : b n i ≤ b n (i - 1)) :
    ∀ j, i ≤ j → ∀ m, j + 1 ≤ m → m ≤ n → b m j ≤ b m (j - 1) := by
  intro j hj
  induction j, hj using Nat.le_induction with
  | base =>
    intro m hm hmn
    by_contra hcon
    have hpos := chain_column_iter (show 2 ≤ i by omega) hm hmn (by omega) (not_le.mp hcon)
    omega
  | succ j hj ih =>
    intro m hm hmn
    rw [Nat.add_sub_cancel]
    exact mono m j (by omega) (by omega) (fun l hl1 hl2 => ih l hl1 (by omega))

/-- **No row has a strict descent followed by a strict ascent.**  For `1 ≤ i < j ≤ n - 1` it is
not the case that `b n i < b n (i-1)` and `b n (j-1) < b n j`. -/
theorem no_descent_ascent (n i j : ℕ) (hi : 1 ≤ i) (hij : i < j) (hj : j ≤ n - 1)
    (hdi : b n i < b n (i - 1)) (hdj : b n (j - 1) < b n j) : False := by
  rcases Nat.lt_or_ge n 17 with hsmall | hbig
  · exact Tab.small_rows n i j (by omega) hi hij hj hdi hdj
  rcases Nat.lt_or_ge n (2 * i) with hright | hleft
  · have h := right_tail (show 9 ≤ i by omega) (show n + 1 ≤ 2 * i by omega) hdi.le j hij.le n
      (by omega) (le_refl n)
    omega
  · have h := left_half n i hbig hi hleft
    omega

set_option linter.unusedVariables false in
/-- **Unimodality of the rows.**  For every `n ≥ 1` there is `p ≤ n - 1` such that
`b n (ℓ-1) ≤ b n ℓ` for `1 ≤ ℓ ≤ p` and `b n (ℓ+1) ≤ b n ℓ` for `p ≤ ℓ ≤ n - 2`
(written `ℓ + 1 ≤ n - 1`).  The proof does not use the hypothesis `1 ≤ n`, which belongs to the
statement. -/
theorem root_unimodal (n : ℕ) (hn : 1 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ) :=
  unimodal_of_no_pair (b n) (n - 1)
    (fun i j hi hij hj hdi hdj => no_descent_ascent n i j hi hij hj hdi hdj)

end Parking
