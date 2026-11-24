import Parking.ChainColumn.Main
import Parking.LeftHalf.Main
import Parking.NextColumn.Criterion
import Parking.NextColumn.Strip

/-!
# The position of the peak of a row

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`
(`Parking/Defs.lean`), and `d_{n,k} = b n k - b n (k-1)` is the step of column `k` in the row `n`.
The strip of a column `k` consists of the rows `k + r` with `r ≥ 1` and `25 r³ ≤ 121 k²`.

`root_unimodal` (`Parking/Unimodal.lean`) says that every row rises to a maximum and falls from
it, and it does not say where the maximum stands.  This module bounds, in the rows `n ≥ 335`, how
far from the end of the row the maximum can stand.  Nothing in the proof of `root_unimodal` uses
the statements of this module.

* `beyond_strip` : a column `k ≥ 265` is positive in every row beyond its strip: if
  `121 k² < 25 r³`, then `d_{k+r,k} > 0`.  By `crossing_strip` the column is positive in a row `j`
  with `25 (j-k-1)³ ≤ 121 k²`, which is at or before the row `k + r`.  The persistence in the
  chain range (`chain_column_iter`) carries the sign to the rows up to `2k - 1`, and the rows from
  `2k` on are `big_columns`.
* `strip_step` : in a row `k + r` of the strip of a column `k ≥ 265`, with `r ≥ 2`: if
  `d_{k+r,k} ≤ 0`, then `d_{k+r,k+1} < 0`.  This is the criterion `step_neg_of_Gfun` together with
  the positivity of the criterion function in the strip (`Gfun_pos`); the criterion applies
  because `r ≤ k - 1` in the strip (`strip_end_le`).
* `row_peak` : in a row `n ≥ 335` there is a column `p ≤ n - 1` with

    `b n 0 ≤ … ≤ b n 81 < b n 82 < … < b n p ≥ b n (p+1) > b n (p+2) > … > b n (n-1)`

  (for `p = n - 1` the chain ends at `b n p`) and `25 (n-1-p)³ ≤ 121 (p+1)²`.  So the row is
  unimodal with its maximum at the column `p`, the maximum is attained at no other column except
  possibly `p + 1`, and `p` lies within `(121/25)^{1/3} (p+1)^{2/3} < 1.692 n^{2/3}` of the last
  column `n - 1`.  The inequality also gives `p ≥ 265`: for `p ≤ 264` and `n ≥ 335` its left side
  is at least `25 · 70³`, which exceeds `121 · 265²`.

## The proof of `row_peak`

In a row `n ≥ 335` every column `1 ≤ k ≤ 264` is nonnegative, and positive if `k ≥ 82`
(`early_columns`): for `2k ≤ n` this is `left_half` and `big_columns`; for `2k > n` the column has
`k ≥ 168`, it is positive in the row `k + r` of `crossing_row`, where `r ≤ 27k/100` gives
`k + r ≤ 264 + 71 = 335 ≤ n`, and `chain_column_iter` carries the sign to the row `n`.

Let `p + 1` be the first column from `82` on that is not positive in the row `n`; if there is
none, `p = n - 1`.  The columns before it are nonnegative, and positive from `82` on.  The column
`p + 1` is not among the columns up to `264`, and by `beyond_strip` the row `n` is not beyond its
strip (`nonpos_in_strip`); this is the bound `25 (n-1-p)³ ≤ 121 (p+1)²`.  The strip of every later
column contains the row `n` as well, so `strip_step`, applied to one column after the other, makes
every column after `p + 1` negative (`strip_tail`).

## The constants

`265` is the column from which `crossing_strip` and `Gfun_pos` are proved.  The constant `121/25`
of the strip is the one of these two theorems: the strip is the range that their estimates reach,
and its last row is not the row in which the column turns positive.  The row `335 = 264 + 71`
comes from the bound `r ≤ 27k/100` of `crossing_row`, which places a positive row of every column
`82 ≤ k ≤ 264` at or before the row `335`.  Accordingly the inequality
`25 (n-1-p)³ ≤ 121 (p+1)²` bounds the distance of the maximum from the end of the row from above;
it gives no lower bound for that distance and is not the position of the maximum.
-/

namespace Parking

/-- **Beyond its strip a column `k ≥ 265` is positive.**  For `k ≥ 265` and `121 k² < 25 r³`:
`b (k+r) (k-1) < b (k+r) k`. -/
theorem beyond_strip {k r : ℕ} (hk : 265 ≤ k) (hr : 121 * k ^ 2 < 25 * r ^ 3) :
    b (k + r) (k - 1) < b (k + r) k := by
  obtain ⟨j, hkj, hj3, hjpos⟩ := crossing_strip hk
  -- the positive row `j` of `crossing_strip` is at or before the row `k + r`
  have hjn : j ≤ k + r := by
    by_contra hcon
    have hle : r ≤ j - k - 1 := by omega
    have h1 : 25 * r ^ 3 ≤ 25 * (j - k - 1) ^ 3 :=
      Nat.mul_le_mul_left 25 (Nat.pow_le_pow_left hle 3)
    exact absurd (lt_of_lt_of_le hr (le_trans h1 hj3)) (lt_irrefl _)
  rcases Nat.lt_or_ge (k + r) (2 * k) with hlt | hge
  · exact chain_column_iter (by omega) (by omega) hjn (by omega) ((dq_pos_iff k j).1 hjpos)
  · exact big_columns k (k + r) (by omega) hge

/-- **The step in the strip.**  For `k ≥ 265`, `r ≥ 2` and `25 r³ ≤ 121 k²`: if
`b (k+r) k ≤ b (k+r) (k-1)`, then `b (k+r) (k+1) < b (k+r) k`. -/
theorem strip_step {k r : ℕ} (hk : 265 ≤ k) (hr : 2 ≤ r) (hrk : 25 * r ^ 3 ≤ 121 * k ^ 2)
    (h : b (k + r) k ≤ b (k + r) (k - 1)) : b (k + r) (k + 1) < b (k + r) k := by
  -- a first-layer position
  have hfl : r ≤ k - 1 := by
    have hend := strip_end_le hk hrk
    omega
  have hstep : dq (k + 1) (k + r) < 0 :=
    step_neg_of_Gfun (by omega : 3 ≤ k) hr hfl (Gfun_pos hk hr hrk).le
      ((dq_nonpos_iff k (k + r)).2 h)
  have hlt := (dq_neg_iff (k + 1) (k + r)).1 hstep
  rwa [Nat.add_sub_cancel] at hlt

/-- In a row `n ≥ 335` every column `1 ≤ k ≤ 264` is nonnegative, and positive if `k ≥ 82`.  For
`2k ≤ n` this is `left_half` and `big_columns`.  For `2k > n` the row `k + r` of `crossing_row`
has `r ≤ 71`, so it is at or before the row `n`, and `chain_column_iter` carries its positive
sign to the row `n`. -/
private theorem early_columns {n k : ℕ} (hn : 335 ≤ n) (hk1 : 1 ≤ k) (hk : k ≤ 264) :
    b n (k - 1) ≤ b n k ∧ (82 ≤ k → b n (k - 1) < b n k) := by
  rcases Nat.lt_or_ge n (2 * k) with hlt | hge
  · obtain ⟨r, hr1, hr, hpos⟩ := crossing_row (k := k) (by omega)
    have h : b n (k - 1) < b n k :=
      chain_column_iter (by omega) (by omega) (by omega) (by omega)
        ((dq_pos_iff k (k + r)).1 hpos)
    exact ⟨h.le, fun _ => h⟩
  · exact ⟨left_half n k (by omega) hk1 hge, fun h82 => big_columns k n h82 hge⟩

/-- In a row `n ≥ 335`, a column `82 ≤ q ≤ n - 1` that is not positive is a column `q ≥ 265`
whose strip contains the row `n`: the columns `82 ≤ q ≤ 264` are positive (`early_columns`), and
so is a column `q ≥ 265` in a row beyond its strip (`beyond_strip`). -/
private theorem nonpos_in_strip {n q : ℕ} (hn : 335 ≤ n) (hq82 : 82 ≤ q) (hqn : q ≤ n - 1)
    (h : b n q ≤ b n (q - 1)) : 265 ≤ q ∧ 25 * (n - q) ^ 3 ≤ 121 * q ^ 2 := by
  have h265 : 265 ≤ q := by
    by_contra hcon
    have h0 := (early_columns hn (by omega) (by omega : q ≤ 264)).2 hq82
    omega
  refine ⟨h265, ?_⟩
  by_contra hcon
  have h0 := beyond_strip h265 (not_le.mp hcon)
  rw [show q + (n - q) = n by omega] at h0
  omega

/-- If a column `i ≥ 265` is not positive in a row `n` of its strip, then every later column of
the row is negative: `b n (ℓ+1) < b n ℓ` for `i ≤ ℓ ≤ n - 2`.  The row `n` lies in the strip of
every column `j ≥ i` as well, and `strip_step` passes from the column `j` to the column `j + 1`. -/
private theorem strip_tail {n i : ℕ} (hi : 265 ≤ i) (hs : 25 * (n - i) ^ 3 ≤ 121 * i ^ 2)
    (h : b n i ≤ b n (i - 1)) : ∀ ℓ, i ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) < b n ℓ := by
  -- `strip_step` in the row `n`, for the columns `j ≥ i`
  have step : ∀ j, i ≤ j → j + 1 ≤ n - 1 → b n j ≤ b n (j - 1) → b n (j + 1) < b n j := by
    intro j hij hj hle
    have hsj : 25 * (n - j) ^ 3 ≤ 121 * j ^ 2 :=
      calc 25 * (n - j) ^ 3 ≤ 25 * (n - i) ^ 3 :=
            Nat.mul_le_mul_left 25 (Nat.pow_le_pow_left (by omega) 3)
        _ ≤ 121 * i ^ 2 := hs
        _ ≤ 121 * j ^ 2 := Nat.mul_le_mul_left 121 (Nat.pow_le_pow_left hij 2)
    have e : j + (n - j) = n := by omega
    have hlt := strip_step (k := j) (r := n - j) (by omega) (by omega) hsj (by rw [e]; exact hle)
    rwa [e] at hlt
  intro ℓ hiℓ
  induction ℓ, hiℓ using Nat.le_induction with
  | base => exact fun hℓ => step i le_rfl hℓ h
  | succ ℓ hiℓ ih =>
    intro hℓ
    exact step (ℓ + 1) (by omega) hℓ (by rw [Nat.add_sub_cancel]; exact (ih (by omega)).le)

/-- **The peak of a row `n ≥ 335`.**  There is `p ≤ n - 1` with `25 (n-1-p)³ ≤ 121 (p+1)²` such
that `b n (ℓ-1) ≤ b n ℓ` for `1 ≤ ℓ ≤ p`, with `b n (ℓ-1) < b n ℓ` for `82 ≤ ℓ ≤ p`, and
`b n (ℓ+1) ≤ b n ℓ` for `p ≤ ℓ ≤ n - 2`, with `b n (ℓ+1) < b n ℓ` for `p + 1 ≤ ℓ ≤ n - 2`
(`ℓ ≤ n - 2` is written `ℓ + 1 ≤ n - 1`).  The column `p + 1` is the first column from `82` on
that is not positive in the row `n`, and `p = n - 1` if there is none. -/
theorem row_peak (n : ℕ) (hn : 335 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ 25 * (n - 1 - p) ^ 3 ≤ 121 * (p + 1) ^ 2 ∧
      (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, 82 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) < b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ) ∧
      (∀ ℓ, p + 1 ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) < b n ℓ) := by
  classical
  -- `p` is the least `p ≥ 81` that is the last column or is followed by a column that is not
  -- positive
  have hex : ∃ p, 81 ≤ p ∧ (p = n - 1 ∨ b n (p + 1) ≤ b n p) := ⟨n - 1, by omega, Or.inl rfl⟩
  obtain ⟨p, ⟨hp81, hp⟩, hmin⟩ :
      ∃ p, (81 ≤ p ∧ (p = n - 1 ∨ b n (p + 1) ≤ b n p)) ∧
        ∀ m < p, ¬ (81 ≤ m ∧ (m = n - 1 ∨ b n (m + 1) ≤ b n m)) :=
    ⟨Nat.find hex, Nat.find_spec hex, fun m hm => Nat.find_min hex hm⟩
  have hpn : p ≤ n - 1 := by
    by_contra hcon
    exact hmin (n - 1) (by omega) ⟨by omega, Or.inl rfl⟩
  -- the columns `82 ≤ ℓ ≤ p` are positive, and the columns before them are nonnegative
  have hpos : ∀ ℓ, 82 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) < b n ℓ := by
    intro ℓ h1 h2
    by_contra hcon
    refine hmin (ℓ - 1) (by omega) ⟨by omega, Or.inr ?_⟩
    rw [Nat.sub_add_cancel (by omega)]
    exact not_lt.mp hcon
  have hnonneg : ∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ := by
    intro ℓ h1 h2
    rcases Nat.lt_or_ge ℓ 82 with h | h
    · exact (early_columns hn h1 (by omega)).1
    · exact (hpos ℓ h h2).le
  rcases Nat.eq_or_lt_of_le hpn with heq | hlt
  · -- `p` is the last column: nothing follows it
    refine ⟨p, hpn, ?_, hnonneg, hpos, fun ℓ h1 h2 => by omega, fun ℓ h1 h2 => by omega⟩
    rw [heq, Nat.sub_self]
    exact Nat.zero_le _
  · -- the column `p + 1` is not positive: the row lies in its strip, and the later columns are
    -- negative
    have hle : b n (p + 1) ≤ b n p := hp.resolve_left (by omega)
    have hq : b n (p + 1) ≤ b n (p + 1 - 1) := by rwa [Nat.add_sub_cancel]
    obtain ⟨h265, hs⟩ := nonpos_in_strip hn (by omega) (by omega) hq
    have htail := strip_tail h265 hs hq
    refine ⟨p, hpn, ?_, hnonneg, hpos, fun ℓ h1 h2 => ?_, htail⟩
    · rw [show n - 1 - p = n - (p + 1) by omega]
      exact hs
    · rcases Nat.eq_or_lt_of_le h1 with rfl | h
      · exact hle
      · exact (htail ℓ (by omega) h2).le

end Parking
