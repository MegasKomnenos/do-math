import Parking.LeftHalf.BigColumns
import Parking.LeftHalf.Propagate

/-!
# The left half of the rows `n ≥ 17`

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`
(`Parking/Defs.lean`), and `d_{n,k} = b n k - b n (k-1)` is the step of column `k` in the row `n`.

`left_half` (**the left half**): for `n ≥ 17` and `k ≥ 1` with `2k ≤ n`, `d_{n,k} ≥ 0`.

* `k = 1` (`column_one`): `d_{n,1} ≥ 0` for every `n ≥ 3`, by a termwise comparison of the
  last-car recursions of the levels `1` and `0`.
* `2 ≤ k ≤ 81` (`small_columns`): the table of the columns `k ≤ 81` (`Tab.small_table`) gives
  `d_{n,k} ≥ 0` on the rows `max (2k) 17 ≤ n < n0` and the nonnegativity of the sums
  `∑_{s ≤ t ≤ n0} ξ_t x_k^t` at the critical tilt `x_k = (k/(k+1))^(k-1)`; since the sequence
  `z^{(k)}_N x_k^N` does not increase (`zrT_anti_crit`), the propagation theorem `propagate` gives
  `d_{n,k} ≥ 0` for every `n ≥ n0`.
* `k ≥ 82`: `big_columns`, which holds from the row `2k` on.
-/

namespace Parking

open Finset

/-! ### The column `k = 1` -/

/-- `2 A 3 0 ≤ A 3 1` (`12 ≤ 13`), evaluated by the kernel on the last-car lists. -/
private theorem base_one : Nat.ble (2 * Tab.hd 0 3) (Tab.hd 1 3) = true := by decide +kernel

/-- `2 A n 0 ≤ A n 1` for `n ≥ 3`: in the last-car recursion the terms `j ≥ 1` of the level `1`
carry the factor `2`, those of the level `0` the factor `1`, and `A m 0 ≤ A m 1`; the term `j = 0`
passes the inequality from the row `n` to the row `n + 1`. -/
private theorem two_A_zero_le (n : ℕ) (hn : 3 ≤ n) : 2 * A n 0 ≤ A n 1 := by
  induction n, hn using Nat.le_induction with
  | base =>
    have h := base_one
    rw [Tab.hd_eq, Tab.hd_eq] at h
    exact Nat.le_of_ble_eq_true h
  | succ n hn ih =>
    rw [A_succ n 0, A_succ n 1, Finset.sum_range_succ', Finset.sum_range_succ', Nat.mul_add,
      Finset.mul_sum]
    apply Nat.add_le_add
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

/-- **The column `k = 1`**: `b n 0 ≤ b n 1` for every `n ≥ 3`. -/
theorem column_one (n : ℕ) (hn : 3 ≤ n) : b n 0 ≤ b n 1 := by
  have h1 := two_A_zero_le n hn
  have h2 : b n 1 + A n 0 = A n 1 := b_succ_add_A n 0
  have h3 : b n 0 = A n 0 := b_zero n
  omega

/-! ### The columns `2 ≤ k ≤ 81` -/

/-- **The columns `2 ≤ k ≤ 81`**: `b n (k-1) ≤ b n k` for every `n ≥ max (2k) 17`.  Below the row
`n0 k` this is read from the table; from the row `n0 k` on it follows from the nonnegative sums
of the table by the propagation theorem. -/
theorem small_columns (k n : ℕ) (hk2 : 2 ≤ k) (hk81 : k ≤ 81) (hn : 2 * k ≤ n) (hn17 : 17 ≤ n) :
    b n (k - 1) ≤ b n k := by
  obtain ⟨hn0, _, hrows, hsuf⟩ := Tab.small_table hk2 hk81
  rcases Nat.lt_or_ge n (Tab.n0 k) with h | h
  · exact hrows n hn hn17 h
  · exact (dq_nonneg_iff k n).mp
      (propagate hk2 (show k ≤ Tab.n0 k by omega) (xcrit_pos k) (zrT_anti_crit hk2) hsuf n h)

/-- **The left half.**  For `n ≥ 17` and `k ≥ 1` with `2k ≤ n`: `b n (k-1) ≤ b n k`. -/
theorem left_half (n k : ℕ) (hn : 17 ≤ n) (hk : 1 ≤ k) (hkn : 2 * k ≤ n) :
    b n (k - 1) ≤ b n k := by
  rcases Nat.lt_or_ge k 82 with h82 | h82
  · rcases Nat.eq_or_lt_of_le hk with rfl | h2
    · exact column_one n (by omega)
    · exact small_columns k n h2 (by omega) hkn hn
  · exact (big_columns k n h82 hkn).le

end Parking
