import Staircase.Peak
import Staircase.Persistence
import Staircase.Beyond.Main
import Staircase.BeforeCrossing.Main
import Staircase.CurveIncrease.Main
import Staircase.Diagonal.Main

/-!
# The staircase, and unimodality as its corollary

`b n ℓ` (`Parking/Defs.lean`) is the number of parking functions of length `n` whose maximum
displacement is exactly `ℓ`.  Write `d_{n,k} = b n k - b n (k-1)` for the step of the row `n` at the
column `k`, `1 ≤ k ≤ n - 1`.  Two rules govern the signs of the steps when the length grows by one,
for `n ≥ 2` and `1 ≤ k ≤ n - 1`:

* `column_rule` : a positive step stays positive one row down in the same column,
  `d_{n,k} > 0 ⟹ d_{n+1,k} > 0`;
* `diagonal_rule` : a step that is not positive is followed by a negative step one row down and
  one column to the right, `d_{n,k} ≤ 0 ⟹ d_{n+1,k+1} < 0`.

For an arbitrary array the two rules give, by induction on the row, that every row `n ≥ 2` has a
peak and that the peak of the row `n + 1` is the same position or the next one (`peak_induction`).
For the array `b` this is the staircase (`staircase`), and unimodality of every row follows
(`unimodal_via_staircase`).

Each rule is assembled here from statements about one region of the array.  The first layer of a
column `k` consists of the rows `k + 1 ≤ n ≤ 2k - 1`.

* The column rule with its conclusion in the first layer is the persistence of the sign,
  `step_persists`; with its conclusion in a row `n + 1 ≥ 2k` it is `column_rule_beyond`.
* The diagonal rule at a position `n ≥ 2k` is `diagonal_rule_beyond`.  In the first layer of a
  column `k ≤ 264` it is `diagonal_rule_small`.  In the first layer of a column `k ≥ 265`, the
  column is positive in some row `j` with `(j - k - 1)³ ≤ k²` (`curve_crossing`) and stays
  positive in the later rows of the layer (`step_persists_iter`), so a step that is not positive
  lies in a row `n < j`, where `(n - k)³ ≤ k²`; there the rule is `diagonal_step_curve`.
-/

namespace Parking

/-- **The induction on the row.**  Let `f` be an array of natural numbers such that, for `n ≥ 2` and
`1 ≤ k ≤ n - 1`, `f n (k-1) < f n k` implies `f (n+1) (k-1) < f (n+1) k`, and `f n k ≤ f n (k-1)`
implies `f (n+1) (k+1) < f (n+1) k`.  Then for every `n ≥ 2` the row `n` has its peak at some `p`,
and the row `n + 1` has its peak at `p` or a strict peak at `p + 1`.

If the row `n` has its peak at `p`, the first hypothesis keeps the steps `1, …, p` of the row
`n + 1` positive, and the second makes its steps `p + 2, …, n` negative, since every step of the row
`n` from `p + 1` on is not positive.  The step `p + 1` of the row `n + 1` decides between the two
alternatives.  The row `2` has one step and so has a peak; the existence of a peak in every row
follows by induction. -/
theorem peak_induction {f : ℕ → ℕ → ℕ}
    (hcol : ∀ n k : ℕ, 2 ≤ n → 1 ≤ k → k ≤ n - 1 → f n (k - 1) < f n k →
      f (n + 1) (k - 1) < f (n + 1) k)
    (hdiag : ∀ n k : ℕ, 2 ≤ n → 1 ≤ k → k ≤ n - 1 → f n k ≤ f n (k - 1) →
      f (n + 1) (k + 1) < f (n + 1) k) :
    ∀ n, 2 ≤ n → ∃ p, IsPeak f n p ∧ (IsPeak f (n + 1) p ∨ IsStrictPeak f (n + 1) (p + 1)) := by
  -- from a peak of the row `n` to the row `n + 1`
  have step : ∀ n p, 2 ≤ n → IsPeak f n p →
      IsPeak f (n + 1) p ∨ IsStrictPeak f (n + 1) (p + 1) := by
    intro n p hn h
    obtain ⟨hp, hup, htie, hdown⟩ := h
    have hup' : ∀ k, 1 ≤ k → k ≤ p → f (n + 1) (k - 1) < f (n + 1) k := fun k hk1 hk2 =>
      hcol n k hn hk1 (by omega) (hup k hk1 hk2)
    have hnonpos : ∀ j, p + 1 ≤ j → j ≤ n - 1 → f n j ≤ f n (j - 1) := by
      intro j hj1 hj2
      rcases Nat.eq_or_lt_of_le hj1 with heq | hlt
      · subst heq
        rw [Nat.add_sub_cancel]
        exact htie hj2
      · exact (hdown j (by omega) hj2).le
    have hdown' : ∀ k, p + 2 ≤ k → k ≤ n + 1 - 1 → f (n + 1) k < f (n + 1) (k - 1) := by
      intro k hk1 hk2
      obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
      rw [Nat.add_sub_cancel]
      exact hdiag n j hn (by omega) (by omega) (hnonpos j (by omega) (by omega))
    by_cases hc : f (n + 1) p < f (n + 1) (p + 1)
    · right
      refine ⟨by omega, ?_, fun k hk1 hk2 => hdown' k (by omega) hk2⟩
      intro k hk1 hk2
      rcases Nat.eq_or_lt_of_le hk2 with heq | hlt
      · subst heq
        rw [Nat.add_sub_cancel]
        exact hc
      · exact hup' k hk1 (by omega)
    · left
      exact ⟨by omega, hup', fun _ => not_lt.mp hc, hdown'⟩
  -- every row `n ≥ 2` has a peak
  have ex : ∀ n, 2 ≤ n → ∃ p, IsPeak f n p := by
    intro n hn
    induction n, hn using Nat.le_induction with
    | base =>
      by_cases h : f 2 0 < f 2 1
      · refine ⟨1, by omega, ?_, fun hp => by omega, fun k hk1 hk2 => by omega⟩
        intro k hk1 hk2
        have hk : k = 1 := by omega
        subst hk
        exact h
      · exact ⟨0, by omega, fun k hk1 hk2 => by omega, fun _ => not_lt.mp h,
          fun k hk1 hk2 => by omega⟩
    | succ n hn ih =>
      obtain ⟨p, hp⟩ := ih
      rcases step n p hn hp with h | h
      · exact ⟨p, h⟩
      · obtain ⟨h1, h2, h3⟩ := h
        refine ⟨p + 1, h1, h2, fun hp1 => ?_, fun k hk1 hk2 => h3 k (by omega) hk2⟩
        have h4 := h3 (p + 1 + 1) (le_refl _) hp1
        rw [Nat.add_sub_cancel] at h4
        exact h4.le
  intro n hn
  obtain ⟨p, hp⟩ := ex n hn
  exact ⟨p, hp, step n p hn hp⟩

/-- **The column rule.**  For `n ≥ 2` and `1 ≤ k ≤ n - 1`, if `b n (k-1) < b n k` then
`b (n+1) (k-1) < b (n+1) k`: a positive step stays positive one row down in the same column.

If the row `n + 1` lies in the first layer of the column, `n + 1 ≤ 2k - 1`, this is `step_persists`;
otherwise it is `column_rule_beyond`. -/
theorem column_rule (n k : ℕ) (hn : 2 ≤ n) (hk1 : 1 ≤ k) (hk2 : k ≤ n - 1)
    (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k := by
  rcases Nat.lt_or_ge (n + 1) (2 * k) with hlt | hge
  · exact step_persists k n (by omega) (by omega) (by omega) h
  · exact column_rule_beyond n k hk1 (by omega) hge h

/-- **The diagonal rule.**  For `n ≥ 2` and `1 ≤ k ≤ n - 1`, if `b n k ≤ b n (k-1)` then
`b (n+1) (k+1) < b (n+1) k`: a step that is not positive is followed by a negative step one row
down and one column to the right.

For `n ≥ 2k` this is `diagonal_rule_beyond`, and for `n ≤ 2k - 1` and `k ≤ 264` it is
`diagonal_rule_small`.  Let `n ≤ 2k - 1` and `k ≥ 265`.  By `curve_crossing` the column `k` is
positive in a row `j > k` with `(j - k - 1)³ ≤ k²`.  If `j ≤ n`, the sign would persist from the row
`j` to the row `n` (`step_persists_iter`), against the hypothesis; so `n < j`, hence
`(n - k)³ ≤ (j - k - 1)³ ≤ k²`, and `diagonal_step_curve` applies with `r = n - k`. -/
theorem diagonal_rule (n k : ℕ) (hn : 2 ≤ n) (hk1 : 1 ≤ k) (hk2 : k ≤ n - 1)
    (h : b n k ≤ b n (k - 1)) : b (n + 1) (k + 1) < b (n + 1) k := by
  rcases Nat.lt_or_ge n (2 * k) with hlt | hge
  · rcases Nat.lt_or_ge k 265 with hs | hl
    · exact diagonal_rule_small n k (by omega) (by omega) (by omega) (by omega) h
    · obtain ⟨j, hkj, hcube, hpos⟩ := curve_crossing k hl
      have hnj : n < j := by
        by_contra hc
        have := step_persists_iter (k := k) (m := j) (n := n) (by omega) (by omega) (by omega)
          (by omega) hpos
        omega
      have hr : (n - k) ^ 3 ≤ k ^ 2 :=
        le_trans (Nat.pow_le_pow_left (by omega : n - k ≤ j - k - 1) 3) hcube
      have hstep := diagonal_step_curve k (n - k) hl (by omega) hr
      have e : k + (n - k) = n := by omega
      rw [e] at hstep
      exact hstep h
  · exact diagonal_rule_beyond n k hk1 hge h

/-- **The staircase.**  For every `n ≥ 2` there is `p` such that the row `b n 0, …, b n (n-1)` has
its peak at `p`,
`b n 0 < ⋯ < b n p ≥ b n (p+1) > ⋯ > b n (n-1)`,
and the row `n + 1` has its peak at `p` as well, or a strict peak at `p + 1`,
`b (n+1) 0 < ⋯ < b (n+1) (p+1) > b (n+1) (p+2) > ⋯ > b (n+1) n`.

It is `peak_induction` for the array `b`, with `column_rule` and `diagonal_rule`. -/
theorem staircase (n : ℕ) (hn : 2 ≤ n) :
    ∃ p, IsPeak b n p ∧ (IsPeak b (n + 1) p ∨ IsStrictPeak b (n + 1) (p + 1)) :=
  peak_induction column_rule diagonal_rule n hn

set_option linter.unusedVariables false in
/-- **Unimodality of the rows, from the staircase.**  For every `n ≥ 1` there is `p ≤ n - 1` such
that `b n (ℓ-1) ≤ b n ℓ` for `1 ≤ ℓ ≤ p` and `b n (ℓ+1) ≤ b n ℓ` for `p ≤ ℓ ≤ n - 2` (written
`ℓ + 1 ≤ n - 1`).

For `n ≥ 2` the peak `p` of the row `n` given by `staircase` is such a position: the row rises
strictly up to `p`, the entry after `p` is not larger, and from there on the row falls strictly.
For `n ≤ 1` both conditions are empty and `p = 0` serves; the hypothesis `1 ≤ n` belongs to the
statement and is not used. -/
theorem unimodal_via_staircase (n : ℕ) (hn : 1 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ) := by
  rcases Nat.lt_or_ge n 2 with h1 | h2
  · exact ⟨0, by omega, fun ℓ h1 h2 => by omega, fun ℓ h1 h2 => by omega⟩
  · obtain ⟨p, ⟨hp, hup, htie, hdown⟩, _⟩ := staircase n h2
    refine ⟨p, hp, fun ℓ h1 h2 => (hup ℓ h1 h2).le, fun ℓ h1 h2 => ?_⟩
    rcases Nat.eq_or_lt_of_le h1 with heq | hlt
    · subst heq
      exact htie h2
    · have := hdown (ℓ + 1) (by omega) h2
      rw [Nat.add_sub_cancel] at this
      exact this.le

end Parking
