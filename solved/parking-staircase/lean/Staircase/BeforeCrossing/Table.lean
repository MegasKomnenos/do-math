import Parking.Table.TwoSigns
import Batteries.Tactic.OpenPrivate

/-!
# The table of the signs before the crossing row, columns `10 ≤ c ≤ 265`

`b n ℓ` and `A n k` are the numbers of `Parking/Defs.lean`, and `d_{n,c} = b n c - b n (c-1)` is the
step of the column `c` in the row `n`.  The crossing row of a column is the first row in which its
step is positive.  For `9 ≤ k ≤ 264` the table `Tab.two_signs` (`Parking/Table/TwoSigns.lean`)
shows that the column `k` is positive in the row `k + ztab k + 1`.  This file computes the sign of
the column after it in the rows up to that row:

* `next_column_neg` : for `9 ≤ k ≤ 264` the column `k + 1` is negative in every row
  `k + 2 ≤ n ≤ k + ztab k + 1`, the last of which is the row in which the column `k` is positive.

`Tab.two_signs` contains one of these signs, that of the column `k + 1` in the row `k + ztab k`.
The others do not follow from it by persistence (`step_persists`), which passes on a positive step
only and so leaves open whether a step in an earlier row is zero.  They are computed.

The statement is read from a table, which the kernel evaluates (`decide +kernel`) in sixteen blocks
of columns:

  the column `c` is negative in the rows `c + 1 ≤ n ≤ c + ztab (c-1)`,   `10 ≤ c ≤ 265`
  (`negTab_all`).

A column `c` is read as far as the row `(c-1) + ztab (c-1) + 1` listed for the column before it.
The negative rows of the columns up to `9` are cells of `Tab.negative_cells`
(`Staircase/Beyond/Table.lean`).

## How the numbers are computed

Write `P n = (n+1)^(n-1)` for the number of parking functions of length `n`, and
`U y n = P n - A n (y-1)` for the number of those with some displacement `≥ y`.  For `c ≥ 2` the
inequality `d_{n,c} < 0` says `2·U c n < U (c+1) n + U (c-1) n` (`neg_of_Uf`).  For `1 ≤ y` and
`n ≤ 2y + 1` the forward form of the single-chain formula gives `U y y = 0` and then the numbers
`U y (y+1), U y (y+2), …` one after the other,

  `U y n = ∑_{t=y+1}^{n} C(n,t) · P(n-t) · W y t`,   `W y t = (t-y) · P(t-1) + y · U y (t-1)`.

The table of two signs computes with this recursion, and this file uses its functions and what is
proved there about them; they are private in `Parking/Table/TwoSigns.lean` and are opened here:
the numbers `U y n` and `W y t` (`Uf`, `Wf`), the list `wl (Wf y) y m = [W y (y+m), …, W y (y+1)]`,
the function `urows y cnt n wrev` that returns `cnt` rows of the recursion from the row `n` on, and
the statement `conv_Wf` that one row of the recursion, applied to the list of the weights, returns
`U y (y+m)` as long as `y + m ≤ 2y + 1`.

What is new here is the list of a whole column and the check.

* `fwdCol y = [U y y, U y (y+1), …, U y (2y+1)]`, for `1 ≤ y` (`nth_fwdCol`): the recursion is
  started at the row `y` with the empty list, where it produces `U y y = 0` as an empty sum, and
  runs through all rows of the range of the forward formula.  So the number of the row `n` is the
  entry `n - y` of the list, for every column.  The kernel computes an entry of the list only when
  a check reads it, so the length of the list costs nothing.
* `negCol c z` : the check of the column `c` on `z` rows: `z + 1 ≤ c`, and
  `2·U c n < U (c+1) n + U (c-1) n` for `c + 1 ≤ n ≤ c + z` (`negCol_sound`).  The condition
  `z + 1 ≤ c` keeps these rows within the range `n ≤ 2(c-1) + 1` of the forward formula for
  `U (c-1) n`.
-/

namespace Parking
namespace Tab

open private P urows Uf Wf wl Uf_add conv_Wf urows_succ from Parking.Table.TwoSigns

/-! ### The list of a column, and the check -/

/-- `fwdCol y`: the `y + 2` rows of the recursion that start at the row `y` with the empty list of
weights; for `1 ≤ y` this is `[U y y, U y (y+1), …, U y (2y+1)]`. -/
private def fwdCol (y : Nat) : List Nat := urows y (Nat.succ (Nat.succ y)) y []

/-- The check of the column `c` on `z` rows: `z + 1 ≤ c`, and `2·u1[i+1] < u2[i] + u0[i+2]` for
`i < z`, where `u0`, `u1`, `u2` are the lists `fwdCol` of `c - 1`, `c`, `c + 1`.  The three entries
belong to the row `c + 1 + i`. -/
private def negCol (c z : Nat) : Bool :=
  let u0 := fwdCol (Nat.pred c)
  let u1 := fwdCol c
  let u2 := fwdCol (Nat.succ c)
  Nat.ble (Nat.succ z) c &&
    allRange (fun i => Nat.blt (Nat.mul 2 (nth u1 (Nat.succ i)))
      (Nat.add (nth u2 i) (nth u0 (Nat.succ (Nat.succ i))))) 0 z

/-- The check of the column `c` on `ztab (c-1)` rows: the table reads the column `c` in the rows
`c + 1, …, c + ztab (c-1)`. -/
private def negTab (c : Nat) : Bool := negCol c (ztab (c - 1))

/-! ### The list of a column is the list of the numbers `U` -/

/-- Started at the row `y + m` with the list `[W y (y+m), …, W y (y+1)]`, the recursion returns
the numbers `U y (y+m), U y (y+m+1), …`, as long as the rows are rows `≤ 2y + 1`.  Each row is
`conv_Wf`, and the entry it adds to the list of the weights is the next weight by definition. -/
private theorem nth_fwdRows {y : ℕ} (hy : 1 ≤ y) : ∀ cnt m i, m + cnt ≤ y + 2 → i < cnt →
    nth (urows y cnt (y + m) (wl (Wf y) y m)) i = Uf y (y + m + i) := by
  intro cnt
  induction cnt with
  | zero =>
    intro m i _ hi
    omega
  | succ cnt ih =>
    intro m i hB hi
    rw [urows_succ, conv_Wf hy (show y + m ≤ 2 * y + 1 by omega)]
    cases i with
    | zero => rfl
    | succ i =>
      have e : y + m + (i + 1) = y + (m + 1) + i := by omega
      rw [e]
      exact ih (m + 1) i (by omega) (by omega)

/-- **The computed column.**  For `1 ≤ y` the list `fwdCol y` is
`[U y y, U y (y+1), …, U y (2y+1)]`: the number of the row `n` is its entry `n - y`. -/
private theorem nth_fwdCol {y n : ℕ} (hy : 1 ≤ y) (h1 : y ≤ n) (h2 : n ≤ 2 * y + 1) :
    nth (fwdCol y) (n - y) = Uf y n := by
  have h := nth_fwdRows hy (y + 2) 0 (n - y) (by omega) (by omega)
  rw [show y + 0 + (n - y) = n by omega] at h
  exact h

/-! ### The check as a statement about `b` -/

/-- **The sign of a step in terms of the numbers `U`.**  For `c ≥ 2`, if
`2·U c n < U (c+1) n + U (c-1) n` then `b n c < b n (c-1)`.  The three numbers `U` are
`P n - A n j` for `j = c - 1, c, c - 2`, and `b n c = A n c - A n (c-1)`,
`b n (c-1) = A n (c-1) - A n (c-2)`. -/
private theorem neg_of_Uf {c n : ℕ} (hc : 2 ≤ c)
    (h : 2 * Uf c n < Uf (c + 1) n + Uf (c - 1) n) : b n c < b n (c - 1) := by
  obtain ⟨j, rfl⟩ : ∃ j, c = j + 2 := ⟨c - 2, by omega⟩
  have h' : 2 * Uf (j + 2) n < Uf (j + 3) n + Uf (j + 1) n := h
  have u0 : Uf (j + 1) n + A n j = P n := Uf_add (j + 1) n
  have u1 : Uf (j + 2) n + A n (j + 1) = P n := Uf_add (j + 2) n
  have u2 : Uf (j + 3) n + A n (j + 2) = P n := Uf_add (j + 3) n
  have b1 : b n (j + 1) + A n j = A n (j + 1) := b_succ_add_A n j
  have b2 : b n (j + 2) + A n (j + 1) = A n (j + 2) := b_succ_add_A n (j + 1)
  show b n (j + 2) < b n (j + 1)
  omega

/-- **What a passed check says.**  If `negCol c z = true` and `c ≥ 2`, then the column `c` is
negative in the rows `c + 1 ≤ n ≤ c + z`.  The check compares the entries of the three lists that
belong to the row `n`; by `nth_fwdCol` they are `U c n`, `U (c+1) n` and `U (c-1) n`. -/
private theorem negCol_sound {c z n : ℕ} (hc : 2 ≤ c) (h : negCol c z = true) (h1 : c + 1 ≤ n)
    (h2 : n ≤ c + z) : b n c < b n (c - 1) := by
  have h' : (Nat.ble (z + 1) c && allRange (fun i =>
      Nat.blt (2 * nth (fwdCol c) (i + 1))
        (nth (fwdCol (c + 1)) i + nth (fwdCol (c - 1)) (i + 2))) 0 z) = true := h
  rw [Bool.and_eq_true, Nat.ble_eq] at h'
  have hF := allRange_sound _ 0 z h'.2 (n - (c + 1)) (Nat.zero_le _) (by omega)
  simp only [Nat.blt_eq] at hF
  have e1 : n - (c + 1) + 1 = n - c := by omega
  have e2 : n - (c + 1) + 2 = n - (c - 1) := by omega
  rw [e1, e2, nth_fwdCol (by omega) (by omega) (by omega),
    nth_fwdCol (by omega) (by omega) (by omega), nth_fwdCol (by omega) (by omega) (by omega)] at hF
  exact neg_of_Uf hc hF

/-! ### The kernel evaluations

The columns `10 ≤ c ≤ 265` in sixteen blocks; each block is one evaluation by the kernel. -/

private theorem neg_10 : allRange negTab 10 15 = true := by decide +kernel

private theorem neg_25 : allRange negTab 25 16 = true := by decide +kernel

private theorem neg_41 : allRange negTab 41 16 = true := by decide +kernel

private theorem neg_57 : allRange negTab 57 16 = true := by decide +kernel

private theorem neg_73 : allRange negTab 73 16 = true := by decide +kernel

private theorem neg_89 : allRange negTab 89 16 = true := by decide +kernel

private theorem neg_105 : allRange negTab 105 16 = true := by decide +kernel

private theorem neg_121 : allRange negTab 121 16 = true := by decide +kernel

private theorem neg_137 : allRange negTab 137 16 = true := by decide +kernel

private theorem neg_153 : allRange negTab 153 16 = true := by decide +kernel

private theorem neg_169 : allRange negTab 169 16 = true := by decide +kernel

private theorem neg_185 : allRange negTab 185 16 = true := by decide +kernel

private theorem neg_201 : allRange negTab 201 16 = true := by decide +kernel

private theorem neg_217 : allRange negTab 217 16 = true := by decide +kernel

private theorem neg_233 : allRange negTab 233 16 = true := by decide +kernel

private theorem neg_249 : allRange negTab 249 17 = true := by decide +kernel

/-- **Every column `10 ≤ c ≤ 265` passes the check on `ztab (c-1)` rows.** -/
private theorem negTab_all : ∀ c, 10 ≤ c → c < 266 → negTab c = true :=
  glue (allRange_sound negTab 10 15 neg_10) <|
  glue (allRange_sound negTab 25 16 neg_25) <|
  glue (allRange_sound negTab 41 16 neg_41) <|
  glue (allRange_sound negTab 57 16 neg_57) <|
  glue (allRange_sound negTab 73 16 neg_73) <|
  glue (allRange_sound negTab 89 16 neg_89) <|
  glue (allRange_sound negTab 105 16 neg_105) <|
  glue (allRange_sound negTab 121 16 neg_121) <|
  glue (allRange_sound negTab 137 16 neg_137) <|
  glue (allRange_sound negTab 153 16 neg_153) <|
  glue (allRange_sound negTab 169 16 neg_169) <|
  glue (allRange_sound negTab 185 16 neg_185) <|
  glue (allRange_sound negTab 201 16 neg_201) <|
  glue (allRange_sound negTab 217 16 neg_217) <|
  glue (allRange_sound negTab 233 16 neg_233) <|
  allRange_sound negTab 249 17 neg_249

/-! ### The table statement -/

/-- **The next column up to the positive row, columns `9 ≤ k ≤ 264`.**  The column `k + 1` is
negative in every row `k + 2 ≤ n ≤ k + ztab k + 1`, the last of which is the row in which the
column `k` is positive by `two_signs`.  These are the rows `c + 1 ≤ n ≤ c + ztab (c-1)` that the
table reads in the column `c = k + 1`. -/
theorem next_column_neg {k n : ℕ} (h9 : 9 ≤ k) (h264 : k ≤ 264) (h1 : k + 2 ≤ n)
    (h2 : n ≤ k + ztab k + 1) : b n (k + 1) < b n k := by
  have h : negCol (k + 1) (ztab k) = true := negTab_all (k + 1) (by omega) (by omega)
  exact negCol_sound (by omega) h (by omega) (by omega)

end Tab
end Parking
