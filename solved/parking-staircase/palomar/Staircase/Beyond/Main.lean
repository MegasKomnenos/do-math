module

public import Parking.Tilt.Monotone
public import Staircase.Beyond.StepBound
public import Staircase.Beyond.Table
public import Staircase.Persistence

/-!
# Beyond the first layer

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`,
`A n l` the number of those with all displacements at most `l`, and `d_{n,k} = b n k - b n (k-1)`
is the step of column `k` in the row `n`.  The first layer of column `k` is the set of rows
`k + 1 ≤ n ≤ 2k - 1`; this file is about the rows `n ≥ 2k` beyond it.

* `step_pos_beyond` (**the signs beyond the first layer**): for `k ≥ 1` and `n ≥ 2k`,
  `d_{n,k} > 0`, except at the eleven positions `(2k, k)` with `k ≤ 7` and `(2k + 1, k)` with
  `2 ≤ k ≤ 5`.
* `column_rule_beyond` : for `k ≥ 1`, `n ≥ k + 1` and `n + 1 ≥ 2k`, `d_{n,k} > 0` implies
  `d_{n+1,k} > 0`.
* `diagonal_rule_beyond` : for `k ≥ 1` and `n ≥ 2k`, `d_{n,k} ≤ 0` implies `d_{n+1,k+1} < 0`.

The positive signs, by the column.

* `k = 1`: `2 A n 0 < A n 1` for `n ≥ 3`, by a termwise comparison of the last-car recursions of
  the levels `1` and `0`.
* `2 ≤ k ≤ 81`: below the row `n0 k` the sign is a cell of the junction table
  (`Tab.junction_table`).  The table of the columns up to `81` (`Tab.small_table`) gives the
  nonnegativity of the sums `∑_{s ≤ t ≤ n0 k} ξ_t x_k^t` at the critical tilt
  `x_k = (k/(k+1))^(k-1) < 1`, at which the tilted environment does not increase
  (`zrT_anti_crit`); so the positive step of the last junction row `n0 k - 1` propagates to
  every later row (`propagate_pos`).
* `k ≥ 82`: `step_pos_large`.

The two rules follow from the signs.  A position beyond the first layer with a step that is not
positive is one of the eleven, and its diagonal successor is a negative cell (`Tab.negative_cells`):
`(2k + 1, k + 1)` is in the last row of the first layer of a column up to `8`, and `(2k + 2, k + 1)`
is in the row `2(k + 1)` of a column up to `6`.  For the column rule the conclusion at `(n + 1, k)`
can fail only at one of the eleven positions, and then `(n, k)` is a negative cell, against the
hypothesis.
-/

@[expose] public section

namespace Parking

/-! ### The column `k = 1` -/

/-- `2 A 3 0 < A 3 1` (`12 < 13`), evaluated by the kernel. -/
private theorem column_one_cell : Nat.ble (2 * Tab.hd 0 3 + 1) (Tab.hd 1 3) = true := by
  decide +kernel

/-- `2 A n 0 < A n 1` for `n ≥ 3`: in the last-car recursion the terms `j ≥ 1` of the level `1`
carry the factor `2`, those of the level `0` the factor `1`, and `A m 0 ≤ A m 1`; the term `j = 0`
passes the strict inequality from the row `n` to the row `n + 1`.  (This is the strict form of
`two_A_zero_le`, which is private in `Parking.LeftHalf.Main`.) -/
private theorem two_A_zero_lt (n : ℕ) (hn : 3 ≤ n) : 2 * A n 0 < A n 1 := by
  induction n, hn using Nat.le_induction with
  | base =>
    have h := column_one_cell
    rw [Tab.hd_eq, Tab.hd_eq] at h
    exact Nat.le_of_ble_eq_true h
  | succ n hn ih =>
    rw [A_succ n 0, A_succ n 1, Finset.sum_range_succ', Finset.sum_range_succ', Nat.mul_add,
      Finset.mul_sum]
    apply Nat.add_lt_add_of_le_of_lt
    · apply Finset.sum_le_sum
      intro j _
      have hX : n.choose (j + 1) * (A (j + 1) 0 * A (n - (j + 1)) 0)
          ≤ n.choose (j + 1) * (A (j + 1) 1 * A (n - (j + 1)) 1) :=
        Nat.mul_le_mul_left _
          (Nat.mul_le_mul (A_mono _ (Nat.zero_le 1)) (A_mono _ (Nat.zero_le 1)))
      have m1 : min (j + 1 + 1) (0 + 1) = 1 := by omega
      have m2 : min (j + 1 + 1) (1 + 1) = 2 := by omega
      rw [m1, m2]
      omega
    · have m1 : min (0 + 1) (0 + 1) = 1 := by omega
      have m2 : min (0 + 1) (1 + 1) = 1 := by omega
      rw [m1, m2, Nat.choose_zero_right, A_zero, A_zero, Nat.sub_zero]
      omega

/-! ### The signs beyond the first layer -/

/-- The critical tilt `x_k = (k/(k+1))^(k-1)` is smaller than `1` for `k ≥ 2`. -/
private theorem xcrit_lt_one {k : ℕ} (hk : 2 ≤ k) : xcrit k < 1 := by
  have h0 : (0 : ℝ) ≤ (k : ℝ) := Nat.cast_nonneg k
  have h1 : (k : ℝ) / ((k : ℝ) + 1) < 1 := by
    rw [div_lt_one (by linarith)]
    linarith
  exact pow_lt_one₀ (div_nonneg h0 (by linarith)) h1 (by omega)

/-- **Beyond the first layer the steps are positive**, except at eleven positions: for `k ≥ 1` and
`n ≥ 2k`, `b n (k-1) < b n k`, unless `n = 2k` and `k ≤ 7`, or `n = 2k + 1` and `2 ≤ k ≤ 5`.

For `k = 1` this is `2 A n 0 < A n 1`.  For `2 ≤ k ≤ 81` the rows below `n0 k` are cells of the
junction table, and the positive step of the row `n0 k - 1` propagates to every later row, because
the sums of the table of the columns up to `81` are nonnegative at the row `n0 k`.  For `k ≥ 82` it
is `step_pos_large`. -/
theorem step_pos_beyond (k n : ℕ) (hk : 1 ≤ k) (hn : 2 * k ≤ n)
    (hex : ¬(n = 2 * k ∧ k ≤ 7 ∨ n = 2 * k + 1 ∧ 2 ≤ k ∧ k ≤ 5)) : b n (k - 1) < b n k := by
  rcases Nat.lt_or_ge k 2 with hk2 | hk2
  · -- the column `k = 1`
    obtain rfl : k = 1 := by omega
    have h1 := two_A_zero_lt n (by omega)
    have h2 : b n 1 + A n 0 = A n 1 := b_succ_add_A n 0
    have h3 : b n 0 = A n 0 := b_zero n
    show b n 0 < b n 1
    omega
  rcases Nat.lt_or_ge k 82 with hk82 | hk82
  · -- the columns `2 ≤ k ≤ 81`
    obtain ⟨hn0, hrows⟩ := Tab.junction_table hk2 (by omega)
    rcases Nat.lt_or_ge n (Tab.n0 k) with hlt | hge
    · exact hrows n hn hlt (by omega)
    · obtain ⟨m, hm⟩ : ∃ m, Tab.n0 k = m + 1 := ⟨Tab.n0 k - 1, by omega⟩
      have hprev : 0 < dq k m := (dq_pos_iff k m).mpr (hrows m (by omega) (by omega) (by omega))
      have hsuf := (Tab.small_table hk2 (by omega)).2.2.2
      rw [hm] at hsuf
      exact (dq_pos_iff k n).mp (propagate_pos hk2 (by omega) (xcrit_pos k) (xcrit_lt_one hk2)
        (zrT_anti_crit hk2) hsuf hprev n (by omega))
  · exact step_pos_large k n hk82 hn

/-! ### The two rules beyond the first layer -/

/-- **The column rule beyond the first layer.**  For `k ≥ 1`, `n ≥ k + 1` and `n + 1 ≥ 2k`: if
`b n (k-1) < b n k`, then `b (n+1) (k-1) < b (n+1) k`.

The conclusion lies beyond the first layer, where the step is positive except at the eleven
positions.  If `(n + 1, k)` is one of them, then `(n, k)` is a negative cell, `(2k - 1, k)` with
`k ≤ 7` or `(2k, k)` with `k ≤ 5`, and the hypothesis fails. -/
theorem column_rule_beyond (n k : ℕ) (hk : 1 ≤ k) (hkn : k + 1 ≤ n) (hn : 2 * k ≤ n + 1)
    (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k := by
  by_cases hex : n + 1 = 2 * k ∧ k ≤ 7 ∨ n + 1 = 2 * k + 1 ∧ 2 ≤ k ∧ k ≤ 5
  · have hneg := Tab.negative_cells (k := k) (n := n) (by omega) hkn (by omega)
    omega
  · exact step_pos_beyond k (n + 1) hk hn hex

/-- **The diagonal rule beyond the first layer.**  For `k ≥ 1` and `n ≥ 2k`: if
`b n k ≤ b n (k-1)`, then `b (n+1) (k+1) < b (n+1) k`.

The hypothesis holds only at the eleven positions.  The diagonal successor of `(2k, k)`, `k ≤ 7`,
is `(2(k+1) - 1, k + 1)`, and that of `(2k + 1, k)`, `k ≤ 5`, is `(2(k+1), k + 1)`; both are
negative cells. -/
theorem diagonal_rule_beyond (n k : ℕ) (hk : 1 ≤ k) (hn : 2 * k ≤ n)
    (h : b n k ≤ b n (k - 1)) : b (n + 1) (k + 1) < b (n + 1) k := by
  have hex : n = 2 * k ∧ k ≤ 7 ∨ n = 2 * k + 1 ∧ 2 ≤ k ∧ k ≤ 5 := by
    by_contra hc
    have hpos := step_pos_beyond k n hk hn hc
    omega
  exact Tab.negative_cells (k := k + 1) (n := n + 1) (by omega) (by omega) (by omega)

end Parking
