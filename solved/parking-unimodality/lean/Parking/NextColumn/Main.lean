import Parking.ChainColumn.Main
import Parking.NextColumn.Large

/-!
# The first positive rows of the columns do not decrease

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`
(`Parking/Defs.lean`), and `d_{n,k} = b n k - b n (k-1)` is the step of column `k` in the row `n`.

`mono`: for `k ≥ 9` and `n ≥ k + 2`, if `d_{j,k} ≤ 0` for all `k + 1 ≤ j ≤ n`, then
`d_{n,k+1} ≤ 0`.  In words: as long as the column `k` has not turned positive, the column `k + 1`
has not turned positive either.

* `9 ≤ k ≤ 264`: the table of two signs (`Tab.two_signs`) gives a number `z` with
  `d_{k+z+1,k} > 0` and `d_{k+z,k+1} < 0`.  The first sign forces `n ≤ k + z`.  If `d_{n,k+1}`
  were positive, the persistence in the chain range of the column `k + 1` (`chain_column_iter`)
  would carry the positive sign
  from the row `n` to the row `k + z`, against the second sign.
* `k ≥ 265`: `mono265`.
-/

namespace Parking

open Tab

/-- **The next column.**  For `k ≥ 9` and `n ≥ k + 2`: if `b j k ≤ b j (k-1)` for all
`k + 1 ≤ j ≤ n`, then `b n (k+1) ≤ b n k`. -/
theorem mono (n k : ℕ) (hk : 9 ≤ k) (hn : k + 2 ≤ n)
    (h : ∀ j, k + 1 ≤ j → j ≤ n → b j k ≤ b j (k - 1)) : b n (k + 1) ≤ b n k := by
  rcases Nat.lt_or_ge k 265 with h265 | h265
  · obtain ⟨hzk, hpos, hlast⟩ := two_signs hk (show k ≤ 264 by omega)
    -- the column `k` is positive in the row `k + z + 1`, so `n ≤ k + z`
    have hnz : n ≤ k + ztab k := by
      by_contra hcon
      have h1 := h (k + ztab k + 1) (by omega) (by omega)
      omega
    -- a positive step of the column `k + 1` in the row `n` would persist up to the row `k + z`
    by_contra hcon
    have hit : b (k + ztab k) (k + 1 - 1) < b (k + ztab k) (k + 1) :=
      chain_column_iter (k := k + 1) (by omega) (by omega) hnz (by omega)
        (by rw [Nat.add_sub_cancel]; omega)
    rw [Nat.add_sub_cancel] at hit
    omega
  · exact (mono265 k n h265 hn h).le

end Parking
