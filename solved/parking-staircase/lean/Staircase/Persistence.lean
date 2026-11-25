import Parking.ChainColumn.Main
import Parking.LeftHalf.BigColumns
import Staircase.CurveIncrease.Main
import Batteries.Tactic.OpenPrivate

/-!
# Persistence of the sign in the first layer, and the columns `k ≥ 82` beyond it

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`.
`d_{n,k} = b n k - b n (k-1)` is the step of the column `k` in the row `n`, and
`dq k n = d_{n,k}/n!`, so that the two have the same sign (`dq_pos_iff`).  The first layer of the
column `k` consists of the rows `k + 1 ≤ n ≤ 2k - 1`.

This module proves that a positive step in the first layer of a column is followed by positive
steps in all the later rows of that layer, and that the steps of a column `k ≥ 82` are positive in
all the rows beyond its first layer.  Both rest, for the columns `k ≥ 82`, on the fact that the
sign of the step changes exactly once in the first layer, and that it does so early.

* `positive_row_early` : every column `k ≥ 82` has a positive step in a row `k + r` with `1 ≤ r`
  and `100 r ≤ 27 k`.  For `82 ≤ k ≤ 264` the row is `k + ztab k + 1`, which the table of two
  signs lists for the column (`Tab.two_signs`, `Tab.ztab_27`).  For `k ≥ 265` it is the row `j`
  of the curve crossing (`curve_crossing`), which satisfies `(j - k - 1)³ ≤ k²`; this bound and
  `k ≥ 265` give `100 (j - k) ≤ 27 k`.
* `one_sign_change` : every column `k ≥ 82` has a row `q` with `k + 1 ≤ q` and
  `100 (q - k) ≤ 27 k` such that `d_{j,k} ≤ 0` for `k ≤ j < q` and `d_{n,k} > 0` for
  `q ≤ n ≤ 2k - 1`.  The row `q` is the first row after the row `k` in which the step is positive.
  It is at most the row of `positive_row_early`, and from it the positive sign is carried to the
  row `2k - 1`.
* `step_persists` : for `k ≥ 2` and `k + 1 ≤ n ≤ 2k - 2`, `d_{n,k} > 0` implies `d_{n+1,k} > 0`.
  For `k ≥ 82` both rows lie on the positive side of the row `q` of `one_sign_change`.
* `step_persists_iter` : the same statement iterated: a column `k ≥ 2` with a positive step in a
  row `m ≥ k + 1` has a positive step in every row `m ≤ n ≤ 2k - 1`.
* `step_pos_large` : for `k ≥ 82` and `n ≥ 2k`, `d_{n,k} > 0`.  The steps are positive from the
  row `q` of `one_sign_change` to the row `2k - 1`, and each row `n ≥ 2k` follows from the rows
  before it.

The proofs take three results on persistence as they are.

* `persist` (`Parking/ChainColumn/Main.lean`) : if the steps of a column `k ≥ 82` are not positive
  in the rows `k ≤ j < q` and the step in the row `q = k + rq` is positive, where `3 rq ≤ k`, then
  the steps are positive in all the rows `q ≤ n ≤ 2k - 1`.
* `Tab.small_table` (`Parking/Table/Columns.lean`) : for `2 ≤ k ≤ 81` and `k + 1 ≤ n ≤ 2k - 2`,
  `d_{n,k} > 0` implies `d_{n+1,k} > 0`; this is read from a table of these columns.
* `big_step` (`Parking/LeftHalf/BigColumns.lean`) : let `k ≥ 82` and let `q` be a row with
  `k + 1 ≤ q` and `100 (q - k) ≤ 27 k` such that the steps of the column `k` are not positive in
  the rows `k ≤ j < q`.  If `n ≥ 2k` and the steps are positive in the rows `q ≤ j ≤ n - 1`, then
  the step in the row `n` is positive.
-/

namespace Parking

open private big_step from Parking.LeftHalf.BigColumns

/-- **An early row with a positive step.**  Every column `k ≥ 82` has a positive step in a row
`k + r` with `1 ≤ r` and `100 r ≤ 27 k`.

For `82 ≤ k ≤ 264` the table of two signs gives the row `k + ztab k + 1` (`Tab.two_signs`), and
`100 (ztab k + 1) ≤ 27 k` is `Tab.ztab_27`.  For `k ≥ 265` the curve crossing gives a row
`j = k + s + 1` with a positive step and `s³ ≤ k²` (`curve_crossing`).  If `100 (s + 1) ≤ 27 k`
failed, then `k ≤ 4 s`, hence `k³ ≤ 64 s³ ≤ 64 k²`, against `k ≥ 265`. -/
theorem positive_row_early {k : ℕ} (hk : 82 ≤ k) :
    ∃ r, 1 ≤ r ∧ 100 * r ≤ 27 * k ∧ 0 < dq k (k + r) := by
  rcases Nat.lt_or_ge k 265 with h | h
  · obtain ⟨_, hpos, _⟩ := Tab.two_signs (show 9 ≤ k by omega) (show k ≤ 264 by omega)
    have e : k + (Tab.ztab k + 1) = k + Tab.ztab k + 1 := by omega
    refine ⟨Tab.ztab k + 1, by omega, Tab.ztab_27 k h hk, ?_⟩
    rw [e]
    exact (dq_pos_iff k (k + Tab.ztab k + 1)).mpr hpos
  · obtain ⟨j, hkj, hj3, hjpos⟩ := curve_crossing k h
    obtain ⟨s, rfl⟩ : ∃ s, j = k + (s + 1) := ⟨j - k - 1, by omega⟩
    rw [show k + (s + 1) - k - 1 = s by omega] at hj3
    have hs : 100 * (s + 1) ≤ 27 * k := by
      by_contra hcon
      have h1 : k ^ 3 ≤ (4 * s) ^ 3 := Nat.pow_le_pow_left (by omega) 3
      have h2 : 265 * k ^ 2 ≤ k * k ^ 2 := Nat.mul_le_mul_right (k ^ 2) h
      have h3 : 0 < k ^ 2 := by positivity
      linarith only [h1, h2, h3, hj3]
    exact ⟨s + 1, by omega, hs, (dq_pos_iff k (k + (s + 1))).mpr hjpos⟩

/-- **One change of sign in the first layer.**  Every column `k ≥ 82` has a row `q` with
`k + 1 ≤ q` and `100 (q - k) ≤ 27 k` such that the step of the column is not positive in the rows
`k ≤ j < q` and positive in the rows `q ≤ n ≤ 2k - 1`.

Let `q` be the first row after the row `k` in which the step is positive; by `positive_row_early`
it exists and `100 (q - k) ≤ 27 k`.  The step in the row `k` is not positive, since
`dq k k = -(cay k)/k` (`dq_base`) and `cay k ≥ 0`, and the steps in the rows between `k` and `q`
are not positive because `q` is the first.  Since `3 (q - k) ≤ k`, `persist` carries the positive
sign from the row `q` to the row `2k - 1`. -/
theorem one_sign_change {k : ℕ} (hk : 82 ≤ k) :
    ∃ q, k + 1 ≤ q ∧ 100 * (q - k) ≤ 27 * k ∧ (∀ j, k ≤ j → j < q → dq k j ≤ 0) ∧
      (∀ n, q ≤ n → n ≤ 2 * k - 1 → 0 < dq k n) := by
  obtain ⟨r, hr1, hr, hc⟩ := positive_row_early hk
  classical
  -- `q` is the first row after the row `k` with a positive step
  have hex : ∃ j, k + 1 ≤ j ∧ 0 < dq k j := ⟨k + r, by omega, hc⟩
  obtain ⟨hq1, hq2⟩ := Nat.find_spec hex
  have hqr : Nat.find hex ≤ k + r := Nat.find_min' hex ⟨by omega, hc⟩
  have hqmin : ∀ j, j < Nat.find hex → ¬ (k + 1 ≤ j ∧ 0 < dq k j) := fun j => Nat.find_min hex
  generalize Nat.find hex = q at hq1 hq2 hqr hqmin
  have hneg : ∀ j, k ≤ j → j < q → dq k j ≤ 0 := by
    intro j hj1 hj2
    rcases Nat.eq_or_lt_of_le hj1 with heq | hlt
    · rw [← heq, dq_base (show 2 ≤ k by omega)]
      have h1 : 0 ≤ cay k / (k : ℝ) := div_nonneg (cay_nonneg k) (Nat.cast_nonneg k)
      linarith
    · exact not_lt.mp fun hpos => hqmin j hj2 ⟨hlt, hpos⟩
  obtain ⟨rq, rfl⟩ : ∃ rq, q = k + rq := ⟨q - k, by omega⟩
  exact ⟨k + rq, hq1, by omega, hneg, persist hk (by omega) (by omega) hneg hq2⟩

/-- **Persistence in the first layer.**  For `k ≥ 2` and `k + 1 ≤ n ≤ 2k - 2`, if
`b n (k-1) < b n k` then `b (n+1) (k-1) < b (n+1) k`: a positive step in a row of the first layer
is followed by a positive step in the next row of that layer.

For `k ≤ 81` this is read from the table of these columns (`Tab.small_table`).  For `k ≥ 82` let
`q` be the row of `one_sign_change`.  The step in the row `n` is positive, so `q ≤ n`, and then the
row `n + 1 ≤ 2k - 1` is one of the rows from `q` on, in which the step is positive. -/
theorem step_persists (k n : ℕ) (hk : 2 ≤ k) (hn1 : k + 1 ≤ n) (hn2 : n ≤ 2 * k - 2)
    (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k := by
  rcases Nat.lt_or_ge k 82 with hsmall | hbig
  · exact (Tab.small_table hk (by omega)).2.1 n hn1 hn2 h
  · obtain ⟨q, _, _, hneg, hpos⟩ := one_sign_change hbig
    have hqn : q ≤ n := by
      by_contra hcon
      have h1 := hneg n (by omega) (by omega)
      have h2 := (dq_pos_iff k n).mpr h
      linarith
    exact (dq_pos_iff k (n + 1)).mp (hpos (n + 1) (by omega) (by omega))

/-- **Persistence in the first layer, iterated.**  For `k ≥ 2`, if `b m (k-1) < b m k` in a row
`m ≥ k + 1`, then `b n (k-1) < b n k` in every row `m ≤ n ≤ 2k - 1`: a positive step in a row of
the first layer is followed by positive steps in all the later rows of that layer.  This is
`step_persists`, by induction on `n`. -/
theorem step_persists_iter {k m n : ℕ} (hk : 2 ≤ k) (hm : k + 1 ≤ m) (hmn : m ≤ n)
    (hn : n ≤ 2 * k - 1) (h : b m (k - 1) < b m k) : b n (k - 1) < b n k := by
  induction n, hmn using Nat.le_induction with
  | base => exact h
  | succ n hmn ih => exact step_persists k n hk (by omega) (by omega) (ih (by omega))

/-- **The columns `k ≥ 82` beyond the first layer.**  For `k ≥ 82` and `n ≥ 2k`,
`b n (k-1) < b n k`.

Let `q` be the row of `one_sign_change`.  The step of the column is positive in every row
`m ≥ q`, by strong induction on `m`: for `m ≤ 2k - 1` this is part of `one_sign_change`, and for
`m ≥ 2k` the positive steps in the rows `q ≤ j ≤ m - 1` give the positive step in the row `m`
(`big_step` of `Parking/LeftHalf/BigColumns.lean`).  The row `n` is one of these rows, because
`q ≤ k + 27k/100 < 2k`. -/
theorem step_pos_large (k n : ℕ) (hk : 82 ≤ k) (hn : 2 * k ≤ n) : b n (k - 1) < b n k := by
  obtain ⟨q, hq1, hq2, hneg, hfirst⟩ := one_sign_change hk
  have hall : ∀ m, q ≤ m → 0 < dq k m := by
    intro m
    induction m using Nat.strong_induction_on with
    | _ m ih =>
      intro hqm
      rcases Nat.lt_or_ge m (2 * k) with h | h
      · exact hfirst m hqm (by omega)
      · exact big_step hk hq1 hq2 h hneg (fun j hj1 hj2 => ih j (by omega) hj1)
  exact (dq_pos_iff k n).mp (hall n (by omega))

end Parking
