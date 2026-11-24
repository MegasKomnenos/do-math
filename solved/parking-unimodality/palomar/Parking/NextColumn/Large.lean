module

public import Parking.Crossing.Strip
public import Parking.NextColumn.Criterion
public import Parking.NextColumn.Strip

/-!
# Before its crossing, a column `k ≥ 265` forces the next column to decrease

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`
(`Parking/Defs.lean`), `d_{n,k} = b n k - b n (k-1)`, and `dq k n = d_{n,k}/n!`.

**Theorem** (`mono265`). For all integers `k ≥ 265` and `n ≥ k + 2`: if `d_{j,k} ≤ 0` for all
integers `j` with `k + 1 ≤ j ≤ n`, then `d_{n,k+1} < 0`.

The proof, with `r = n - k`:

1. the crossing of column `k` happens inside the strip (`crossing_strip`), so the hypothesis forces
   `25 r³ ≤ 121 k²`;
2. such a position is a first-layer position, `r ≤ k - 1` (`strip_end_le`);
3. the criterion function is positive there (`Gfun_pos`);
4. the criterion gives `d_{n,k} ≤ 0 ⟹ d_{n,k+1} < 0` (`step_neg_of_Gfun`).
-/

@[expose] public section

namespace Parking

open Finset

/-- **Before its crossing, a column `k ≥ 265` forces the next column to decrease.**  For
`k ≥ 265` and `n ≥ k + 2`: if `b j k ≤ b j (k-1)` for all `k + 1 ≤ j ≤ n`, then
`b n (k+1) < b n k`. -/
theorem mono265 (k n : ℕ) (hk : 265 ≤ k) (hn : k + 2 ≤ n)
    (h : ∀ j, k + 1 ≤ j → j ≤ n → b j k ≤ b j (k - 1)) : b n (k + 1) < b n k := by
  -- the crossing of column `k` happens inside the strip
  obtain ⟨j, hkj, hj3, hjpos⟩ := crossing_strip hk
  -- the crossing row lies beyond `n`
  have hjn : n < j := by
    by_contra hcon
    have h2 : dq k j ≤ 0 := (dq_nonpos_iff k j).2 (h j (by omega) (not_lt.mp hcon))
    linarith
  -- so the deficit `r = n - k` lies in the strip
  obtain ⟨r, rfl⟩ : ∃ r, n = k + r := ⟨n - k, by omega⟩
  have hr2 : 2 ≤ r := by omega
  have hrk : 25 * r ^ 3 ≤ 121 * k ^ 2 := by
    have hle : r ≤ j - k - 1 := by omega
    calc 25 * r ^ 3 ≤ 25 * (j - k - 1) ^ 3 := by gcongr
      _ ≤ 121 * k ^ 2 := hj3
  -- a first-layer position at which the criterion function is positive
  have hfl : r ≤ k - 1 := by
    have hend := strip_end_le hk hrk
    omega
  have hG : 0 < Gfun r k := Gfun_pos hk hr2 hrk
  have hd : dq k (k + r) ≤ 0 := (dq_nonpos_iff k (k + r)).2 (h (k + r) (by omega) le_rfl)
  have hstep : dq (k + 1) (k + r) < 0 :=
    step_neg_of_Gfun (by omega : 3 ≤ k) hr2 hfl hG.le hd
  have hlt := (dq_neg_iff (k + 1) (k + r)).1 hstep
  rwa [Nat.add_sub_cancel] at hlt

end Parking
