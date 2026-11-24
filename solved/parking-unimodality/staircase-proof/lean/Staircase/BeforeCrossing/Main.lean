import Staircase.BeforeCrossing.Table
import Staircase.Beyond.Table
import Staircase.Persistence

/-!
# The diagonal rule in the first layer of the columns `2 ≤ k ≤ 264`

`b n ℓ` is the number of `Parking/Defs.lean`, and `d_{n,k} = b n k - b n (k-1)` is the step of the
column `k` in the row `n`.  The first layer of the column `k` is the set of the rows
`k + 1 ≤ n ≤ 2k - 1`.

* `diagonal_rule_small` : for `2 ≤ k ≤ 264` and a row `n` of the first layer of the column `k`,
  `d_{n,k} ≤ 0` implies `d_{n+1,k+1} < 0`.

For `9 ≤ k ≤ 264` the column `k` is positive in the row `q = k + ztab k + 1` (`Tab.two_signs`), and
by persistence (`step_persists_iter`) it is positive in every later row of its first layer.  A step
of the first layer that is not positive therefore lies in a row `n < q`, and the column `k + 1` is
negative in every row `k + 2 ≤ n + 1 ≤ q` (`Tab.next_column_neg`).  For `2 ≤ k ≤ 8` no sign of the
column `k` is needed: the column `k + 1 ≤ 9` is negative in every row `k + 2 ≤ n + 1 ≤ 2k`, and
these are cells of `Tab.negative_cells`.
-/

namespace Parking

/-- **The diagonal rule in the first layer, columns `2 ≤ k ≤ 264`.**  If the step of the column `k`
in a row `k + 1 ≤ n ≤ 2k - 1` is not positive, then the step of the column `k + 1` in the row
`n + 1` is negative.  For `k ≥ 9` the row `n` lies before the row `k + ztab k + 1`, because the
column `k` is positive there and stays positive in its first layer; the table of the signs before
the crossing row then gives the sign of the column `k + 1` in the row `n + 1`.  For `k ≤ 8` the
position `(n + 1, k + 1)` is one of the negative cells of the columns up to `9`, which cover every
row `n + 1 ≤ 2k` of the column `k + 1`. -/
theorem diagonal_rule_small (n k : ℕ) (hk2 : 2 ≤ k) (hk : k ≤ 264) (hkn : k + 1 ≤ n)
    (hn : n ≤ 2 * k - 1) (h : b n k ≤ b n (k - 1)) : b (n + 1) (k + 1) < b (n + 1) k := by
  rcases Nat.lt_or_ge k 9 with h8 | h9
  · exact Tab.negative_cells (k := k + 1) (n := n + 1) (by omega) (by omega) (by omega)
  · obtain ⟨-, hpos, -⟩ := Tab.two_signs h9 hk
    have hnq : n ≤ k + Tab.ztab k := by
      by_contra hc
      exact absurd (step_persists_iter hk2 (by omega) (by omega) hn hpos) (not_lt.mpr h)
    exact Tab.next_column_neg h9 hk (by omega) (by omega)

end Parking
