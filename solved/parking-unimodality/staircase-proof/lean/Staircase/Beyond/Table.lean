import Parking.Table.Columns

/-!
# The junction table, and the negative cells of the columns up to `9`

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`,
`A n l` the number of those with all displacements at most `l`, and
`d_{n,k} = b n k - b n (k-1) = A n k - 2 A n (k-1) + A n (k-2)` is the step of column `k` in the
row `n`.

For a column `2 ≤ k ≤ 81` the table of the columns up to `81` lists a row `n0 k ≥ 2k`; from that
row on the sign of the step is decided by the propagation.  The rows `2k ≤ n < n0 k` are the
*junction* of the column: they lie beyond the first layer `k + 1 ≤ n ≤ 2k - 1` and before the
row `n0 k`.  This file reads from the numbers `A n l` the sign of the step in every row of the
junction, and in the rows of the first layer of the columns up to `9` in which the step is
negative.

* `junction_table` : for `2 ≤ k ≤ 81`, `2k + 3 ≤ n0 k`, and `d_{n,k} > 0` in every row
  `2k ≤ n < n0 k`, except in the row `2k` when `k ≤ 7` and in the row `2k + 1` when `k ≤ 5`
  (933 cells).
* `negative_cells` : for `2 ≤ k ≤ 9`, `d_{n,k} < 0` in every row `n ≥ k + 1` with `n ≤ 2k + 1`
  when `k ≤ 5`, with `n ≤ 2k` when `k ≤ 7`, with `n ≤ 2k - 1` when `k ≤ 8`, and with `n ≤ 2k - 2`
  when `k = 9` (45 cells).

Together: with `firstPos k = 2k + 2` for `k ≤ 5`, `2k + 1` for `k = 6, 7` and `2k` for `k ≥ 8`,
column `k` is positive in the rows `firstPos k ≤ n < n0 k`, and for `k ≤ 8` it is negative in
every row `k + 1 ≤ n < firstPos k` before them.  The column `9` is negative in the rows
`10 ≤ n ≤ 16` of its first layer; its junction begins at the row `18`.

A cell is one comparison between `2 A n (k-1)` and `A n k + A n (k-2)`.  The three numbers are
evaluated by the kernel through `Tab.hd`, where `Tab.hd l n = A n l` (`Tab.hd_eq`); each evaluation
runs the last-car recursion up to the row `n`.  The positive cells are evaluated in four blocks of
columns, the negative cells in one.
-/

namespace Parking
namespace Tab

/-! ### One cell

The cells `(n, k)` and `(n, k + 1)` both need `A n k` and `A n (k-1)`.  The kernel keeps the value
of a term that it has evaluated and takes it from there when it meets the same term again.  The
numbers are therefore read through `hdv`, which hands every `A n l` to the kernel as the same term
`hd l n` with numerals `l` and `n`, wherever in the table it occurs; a block of columns then
evaluates each number once instead of three times. -/

/-- `byValue a f = f a`.  The kernel reduces the recursor only after it has evaluated `a`, so that
`f` is applied to a numeral and not to the expression that `a` was. -/
private noncomputable def byValue (a : Nat) (f : Nat → Nat) : Nat :=
  Nat.rec (motive := fun _ => Nat) (f Nat.zero) (fun m _ => f (Nat.succ m)) a

/-- `hdv l n = hd l n = A n l`, with `l` and `n` evaluated first. -/
private noncomputable def hdv (l n : Nat) : Nat :=
  byValue l fun l' => byValue n fun n' => hd l' n'

private theorem hdv_eq (l n : ℕ) : hdv l n = A n l := by
  rw [← hd_eq]
  cases l <;> cases n <;> rfl

/-- `stepPos k n`: `2 A n (k-1) < A n k + A n (k-2)`, that is `d_{n,k} > 0` (for `k ≥ 2`). -/
private noncomputable def stepPos (k n : Nat) : Bool :=
  Nat.ble (2 * hdv (k - 1) n + 1) (hdv k n + hdv (k - 2) n)

/-- `stepNeg k n`: `A n k + A n (k-2) < 2 A n (k-1)`, that is `d_{n,k} < 0` (for `k ≥ 2`). -/
private noncomputable def stepNeg (k n : Nat) : Bool :=
  Nat.ble (hdv k n + hdv (k - 2) n + 1) (2 * hdv (k - 1) n)

private theorem stepPos_sound {k n : ℕ} (hk : 2 ≤ k) (h : stepPos k n = true) :
    b n (k - 1) < b n k := by
  unfold stepPos at h
  rw [hdv_eq, hdv_eq, hdv_eq] at h
  have h1 : 2 * A n (k - 1) + 1 ≤ A n k + A n (k - 2) := Nat.le_of_ble_eq_true h
  have h2 := d_eq_A hk n
  omega

private theorem stepNeg_sound {k n : ℕ} (hk : 2 ≤ k) (h : stepNeg k n = true) :
    b n k < b n (k - 1) := by
  unfold stepNeg at h
  rw [hdv_eq, hdv_eq, hdv_eq] at h
  have h1 : A n k + A n (k - 2) + 1 ≤ 2 * A n (k - 1) := Nat.le_of_ble_eq_true h
  have h2 := d_eq_A hk n
  omega

/-! ### The checks of a column -/

/-- `firstPos k`: the first row from which the junction of column `k` is positive; `2k + 2` for
`k ≤ 5`, `2k + 1` for `k = 6, 7`, and `2k` for `k ≥ 8`. -/
private def firstPos (k : Nat) : Nat := 2 * k + if k ≤ 5 then 2 else if k ≤ 7 then 1 else 0

/-- Column `k`: `2k + 3 ≤ n0 k`, and `d_{n,k} > 0` in the rows `firstPos k ≤ n < n0 k`. -/
private noncomputable def colPos (k : Nat) : Bool :=
  Nat.ble (2 * k + 3) (n0 k) && allRange (stepPos k) (firstPos k) (n0 k - firstPos k)

/-- Column `k`: `d_{n,k} < 0` in the rows `k + 1 ≤ n < firstPos k` with `n ≤ 16`.  The bound `16`
takes effect in the column `9` only, where `firstPos 9 = 18`. -/
private noncomputable def colNeg (k : Nat) : Bool :=
  allRange (stepNeg k) (k + 1) (min (firstPos k) 17 - (k + 1))

/-! ### The kernel evaluations

The positive cells of the columns `2 ≤ k ≤ 81` in four blocks, and the negative cells of the
columns `2 ≤ k ≤ 9`; each is one evaluation by the kernel. -/

private theorem pos_2_55 : allRange colPos 2 54 = true := by decide +kernel

private theorem pos_56_66 : allRange colPos 56 11 = true := by decide +kernel

private theorem pos_67_74 : allRange colPos 67 8 = true := by decide +kernel

private theorem pos_75_81 : allRange colPos 75 7 = true := by decide +kernel

private theorem neg_2_9 : allRange colNeg 2 8 = true := by decide +kernel

/-! ### The table statements -/

/-- Every column `2 ≤ k ≤ 81` passes the check of its positive cells (the four blocks). -/
private theorem pos_cols : ∀ k, 2 ≤ k → k < 82 → colPos k = true :=
  glue (allRange_sound colPos 2 54 pos_2_55) <|
  glue (allRange_sound colPos 56 11 pos_56_66) <|
  glue (allRange_sound colPos 67 8 pos_67_74) <|
  allRange_sound colPos 75 7 pos_75_81

/-- **The junction table.**  For `2 ≤ k ≤ 81`: the row `n0 k` is at least `2k + 3`, and the step of
column `k` is positive in every row `2k ≤ n < n0 k`, except in the row `2k` when `k ≤ 7` and in the
row `2k + 1` when `k ≤ 5`.

Each cell is the comparison `2 A n (k-1) < A n k + A n (k-2)`, evaluated by the kernel. -/
theorem junction_table {k : ℕ} (hk2 : 2 ≤ k) (hk81 : k ≤ 81) :
    2 * k + 3 ≤ n0 k ∧
    ∀ n, 2 * k ≤ n → n < n0 k → ¬(n = 2 * k ∧ k ≤ 7 ∨ n = 2 * k + 1 ∧ k ≤ 5) →
      b n (k - 1) < b n k := by
  have h := pos_cols k hk2 (by omega)
  unfold colPos at h
  rw [Bool.and_eq_true_iff] at h
  refine ⟨Nat.le_of_ble_eq_true h.1, fun n hn1 hn2 hex => stepPos_sound hk2 ?_⟩
  have hfirst : firstPos k ≤ n := by
    unfold firstPos
    split_ifs <;> omega
  exact allRange_sound (stepPos k) (firstPos k) _ h.2 n hfirst (by omega)

/-- **The negative cells.**  For `2 ≤ k ≤ 9` the step of column `k` is negative in every row
`n ≥ k + 1` with `n ≤ 2k + 1` when `k ≤ 5`, with `n ≤ 2k` when `k ≤ 7`, with `n ≤ 2k - 1` when
`k ≤ 8`, and with `n ≤ 2k - 2` when `k = 9`.  In the columns `2, …, 9` these are the rows from
`k + 1` up to the rows `5, 7, 9, 11, 12, 14, 15, 16`.

These are 45 comparisons `A n k + A n (k-2) < 2 A n (k-1)` in the rows up to `16`, evaluated by
the kernel. -/
theorem negative_cells {k n : ℕ} (hk2 : 2 ≤ k) (hkn : k + 1 ≤ n)
    (h : n ≤ 2 * k + 1 ∧ k ≤ 5 ∨ n ≤ 2 * k ∧ k ≤ 7 ∨ n + 1 ≤ 2 * k ∧ k ≤ 8
      ∨ n + 2 ≤ 2 * k ∧ k ≤ 9) :
    b n k < b n (k - 1) := by
  have hcol : colNeg k = true := allRange_sound colNeg 2 8 neg_2_9 k hk2 (by omega)
  have hlast : n < min (firstPos k) 17 := by
    unfold firstPos
    split_ifs <;> omega
  exact stepNeg_sound hk2 (allRange_sound (stepNeg k) (k + 1) _ hcol n hkn (by omega))

end Tab
end Parking
