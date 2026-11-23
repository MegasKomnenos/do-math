import Parking.ChainColumn.FarRows
import Parking.ChainColumn.NearRows
import Parking.Crossing.Strip
import Parking.Table.Columns
import Parking.Table.TwoSigns

/-!
# Persistence of the sign along a column in the chain range

`d_{n,k} = b n k - b n (k-1)` is the step of the column `k` in the row `n`, and
`dq k n = d_{n,k}/n!`.  The chain range of the column `k` consists of the rows `k + 1 ≤ n ≤ 2k - 1`.

* `persist` : if a column `k ≥ 82` is nonpositive on the rows `k ≤ j < q` and positive at
  `q = k + rq` with `3 rq ≤ k`, then it is positive on all the rows `q ≤ n ≤ 2k - 1`.  The rows up
  to `k + 0.47 k` are `caseA`, the rows beyond are `caseFar`.
* `crossing_row` : every column `k ≥ 82` is positive in some row `k + r` with `1 ≤ r` and
  `100 r ≤ 27 k`.  For `82 ≤ k ≤ 264` the row is the one listed in the table of two signs
  (`Tab.two_signs`); for `k ≥ 265` it comes from `crossing_strip`.
* `single_crossing` : every column `k ≥ 82` has a row `q` with `k + 1 ≤ q`, `100 (q - k) ≤ 27 k`,
  such that `d_{j,k} ≤ 0` for `k ≤ j < q` and `d_{n,k} > 0` for `q ≤ n ≤ 2k - 1`: `q` is the first
  positive row, which is at most the row of `crossing_row`, and `persist` carries the positive
  sign from `q` to the row `2k - 1`.
* `chain_column` : for `k ≥ 2` and `k + 1 ≤ n ≤ 2k - 2`, if `d_{n,k} > 0` then `d_{n+1,k} > 0`.
  For `k ≤ 81` this is read from the table of the columns `k ≤ 81` (`Tab.small_table`); for
  `k ≥ 82` it follows from `single_crossing`.
* `chain_column_iter` : the same statement iterated: a column that is positive in a row
  `m ≥ k + 1` is positive in every row `m ≤ n ≤ 2k - 1`.
-/

namespace Parking

open Tab

/-- **Persistence after an early crossing.**  If a column `k ≥ 82` is nonpositive on the rows
`k ≤ j < k + rq` and positive at the row `k + rq`, where `3 rq ≤ k`, then it is positive on all the
rows `k + rq ≤ n ≤ 2k - 1`. -/
theorem persist {k rq : ℕ} (hk : 82 ≤ k) (hrq : 1 ≤ rq) (h3 : 3 * rq ≤ k)
    (hneg : ∀ j, k ≤ j → j < k + rq → dq k j ≤ 0) (hq : 0 < dq k (k + rq)) :
    ∀ n, k + rq ≤ n → n ≤ 2 * k - 1 → 0 < dq k n := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro hn1 hn2
    rcases Nat.eq_or_lt_of_le hn1 with heq | hlt
    · rw [← heq]
      exact hq
    · obtain ⟨t, rfl⟩ : ∃ t, n = k + rq + t := ⟨n - (k + rq), by omega⟩
      have ht : 1 ≤ t := by omega
      have hpos : ∀ j, k + rq ≤ j → j < k + rq + t → 0 < dq k j :=
        fun j h1 h2 => ih j h2 h1 (by omega)
      rcases Nat.lt_or_ge (47 * k) (100 * (rq + t)) with h47 | h47
      · have h := caseFar (k := k) (r := rq + t) (rq := rq) hk h47 (by omega) h3
          (fun j h1 h2 => hpos j h1 (by omega))
        have e : k + (rq + t) = k + rq + t := by omega
        rw [e] at h
        exact h
      · exact caseA (by omega) hrq ht h47 hneg hpos

/-- **The crossing row.**  Every column `k ≥ 82` is positive in a row `k + r` with `1 ≤ r` and
`100 r ≤ 27 k`. -/
theorem crossing_row {k : ℕ} (hk : 82 ≤ k) :
    ∃ r, 1 ≤ r ∧ 100 * r ≤ 27 * k ∧ 0 < dq k (k + r) := by
  rcases Nat.lt_or_ge k 265 with h | h
  · obtain ⟨_, hpos, _⟩ := two_signs (show 9 ≤ k by omega) (show k ≤ 264 by omega)
    have e : k + (ztab k + 1) = k + ztab k + 1 := by omega
    refine ⟨ztab k + 1, by omega, ztab_27 k h hk, ?_⟩
    rw [e]
    exact (dq_pos_iff k (k + ztab k + 1)).mpr hpos
  · obtain ⟨j, hkj, hj3, hjpos⟩ := crossing_strip h
    have hend := strip_end_le h hj3
    have e : k + (j - k) = j := by omega
    refine ⟨j - k, by omega, by omega, ?_⟩
    rw [e]
    exact hjpos

/-- **Single crossing in the chain range.**  Every column `k ≥ 82` has a row `q` with
`k + 1 ≤ q` and `100 (q - k) ≤ 27 k` such that the column is nonpositive on the rows `k ≤ j < q`
and positive on the rows `q ≤ n ≤ 2k - 1`. -/
theorem single_crossing {k : ℕ} (hk : 82 ≤ k) :
    ∃ q, k + 1 ≤ q ∧ 100 * (q - k) ≤ 27 * k ∧ (∀ j, k ≤ j → j < q → dq k j ≤ 0) ∧
      (∀ n, q ≤ n → n ≤ 2 * k - 1 → 0 < dq k n) := by
  obtain ⟨r, hr1, hr, hc⟩ := crossing_row hk
  classical
  -- `q` is the first positive row after the row `k`
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

/-- **Persistence in the chain range.**  In the chain range `k + 1 ≤ n ≤ 2k - 2` (`k ≥ 2`),
`d_{n,k} > 0` implies `d_{n+1,k} > 0`. -/
theorem chain_column (k n : ℕ) (hk : 2 ≤ k) (hn1 : k + 1 ≤ n) (hn2 : n ≤ 2 * k - 2)
    (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k := by
  rcases Nat.lt_or_ge k 82 with hsmall | hbig
  · exact (small_table hk (by omega)).2.1 n hn1 hn2 h
  · obtain ⟨q, _, _, hneg, hpos⟩ := single_crossing hbig
    have hqn : q ≤ n := by
      by_contra hcon
      have h1 := hneg n (by omega) (by omega)
      have h2 := (dq_pos_iff k n).mpr h
      linarith
    exact (dq_pos_iff k (n + 1)).mp (hpos (n + 1) (by omega) (by omega))

/-- **Persistence in the chain range, iterated.**  A column `k ≥ 2` that is positive in a row
`m ≥ k + 1` is positive in every row `m ≤ n ≤ 2k - 1`. -/
theorem chain_column_iter {k m n : ℕ} (hk : 2 ≤ k) (hm : k + 1 ≤ m) (hmn : m ≤ n)
    (hn : n ≤ 2 * k - 1) (h : b m (k - 1) < b m k) : b n (k - 1) < b n k := by
  induction n, hmn using Nat.le_induction with
  | base => exact h
  | succ n hmn ih => exact chain_column k n hk (by omega) (by omega) (ih (by omega))

end Parking
