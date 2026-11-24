module

public import Parking.Table.Columns

/-!
# The table of the rows `n ≤ 16`

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`.
For every `n ≤ 16` the kernel checks that the row `b n 0, …, b n (n-1)` first does not decrease
and then does not increase, and therefore has no strict descent followed by a strict ascent
(`small_rows`).

The values are read from the last-car lists of `Parking.Table.Columns`: `hd l n = A n l`, and
`b n 0 = A n 0`, `b n (l+1) = A n (l+1) - A n l`.

* `updown f m a` : on the positions `a, …, a + m` the function `f` does not decrease up to some
  position and does not increase after it;
* `rowsOK N`     : `updown` for the rows `1 ≤ n ≤ N`;
* `rows_16`      : the kernel evaluation;
* `small_rows`   : **the table statement.**
-/

@[expose] public section

namespace Parking
namespace Tab

/-- `bT n ℓ = b n ℓ`, computed from the last-car lists. -/
private noncomputable def bT (n : Nat) : Nat → Nat
  | 0 => hd 0 n
  | Nat.succ l => hd (Nat.succ l) n - hd l n

/-- `f (a+1) ≤ f a`, …, `f (a+m) ≤ f (a+m-1)`. -/
private def down (f : Nat → Nat) : Nat → Nat → Bool
  | 0, _ => true
  | Nat.succ m, a => Nat.ble (f (a + 1)) (f a) && down f m (a + 1)

/-- On the positions `a, …, a + m`: `f` does not decrease as long as `f a ≤ f (a+1)`, and does not
increase from the first position with `f (a+1) < f a` on. -/
private def updown (f : Nat → Nat) : Nat → Nat → Bool
  | 0, _ => true
  | Nat.succ m, a => cond (Nat.ble (f a) (f (a + 1))) (updown f m (a + 1)) (down f m (a + 1))

/-- `updown` for the rows `n = 1, …, N` (the row `n` has the positions `0, …, n - 1`). -/
private noncomputable def rowsOK : Nat → Bool
  | 0 => true
  | Nat.succ n => updown (bT (Nat.succ n)) n 0 && rowsOK n

/-- The rows `n ≤ 16`, checked by the kernel. -/
private theorem rows_16 : rowsOK 16 = true := by decide +kernel

private theorem bT_eq (n ℓ : ℕ) : bT n ℓ = b n ℓ := by
  cases ℓ with
  | zero =>
    show hd 0 n = b n 0
    rw [hd_eq, b_zero]
  | succ l =>
    show hd (l + 1) n - hd l n = b n (l + 1)
    have h := b_succ_add_A n l
    rw [hd_eq, hd_eq]
    omega

private theorem down_sound (f : ℕ → ℕ) : ∀ (m a : ℕ), down f m a = true →
    ∀ j, a + 1 ≤ j → j ≤ a + m → f j ≤ f (j - 1) := by
  intro m
  induction m with
  | zero =>
    intro a _ j h1 h2
    omega
  | succ m ih =>
    intro a h j h1 h2
    have h' : (Nat.ble (f (a + 1)) (f a) && down f m (a + 1)) = true := h
    simp only [Bool.and_eq_true, Nat.ble_eq] at h'
    rcases Nat.eq_or_lt_of_le h1 with rfl | hlt
    · exact h'.1
    · exact ih (a + 1) h'.2 j hlt (by omega)

/-- A function that passes `updown` on the positions `a, …, a + m` has no strict descent followed
by a strict ascent there. -/
private theorem updown_sound (f : ℕ → ℕ) : ∀ (m a : ℕ), updown f m a = true →
    ∀ i j, a + 1 ≤ i → i < j → j ≤ a + m → f i < f (i - 1) → f (j - 1) < f j → False := by
  intro m
  induction m with
  | zero =>
    intro a _ i j h1 h2 h3
    omega
  | succ m ih =>
    intro a h i j h1 h2 h3 hdi hdj
    have h' : cond (Nat.ble (f a) (f (a + 1))) (updown f m (a + 1)) (down f m (a + 1)) = true := h
    cases hc : Nat.ble (f a) (f (a + 1)) with
    | true =>
      rw [hc] at h'
      rcases Nat.eq_or_lt_of_le h1 with rfl | hlt
      · have hle : f a ≤ f (a + 1) := Nat.le_of_ble_eq_true hc
        rw [Nat.add_sub_cancel] at hdi
        omega
      · exact ih (a + 1) h' i j hlt h2 (by omega) hdi hdj
    | false =>
      rw [hc] at h'
      have hle := down_sound f m (a + 1) h' j (by omega) (by omega)
      omega

private theorem rowsOK_sound : ∀ N, rowsOK N = true →
    ∀ n, 1 ≤ n → n ≤ N → updown (bT n) (n - 1) 0 = true := by
  intro N
  induction N with
  | zero =>
    intro _ n h1 h2
    omega
  | succ N ih =>
    intro h n h1 h2
    have h' : (updown (bT (N + 1)) N 0 && rowsOK N) = true := h
    simp only [Bool.and_eq_true] at h'
    rcases Nat.eq_or_lt_of_le h2 with rfl | hlt
    · exact h'.1
    · exact ih h'.2 n h1 (by omega)

/-- **The rows `n ≤ 16`.**  No row `n ≤ 16` has a strict descent `b n i < b n (i-1)` followed by a
strict ascent `b n (j-1) < b n j`, `1 ≤ i < j ≤ n - 1`. -/
theorem small_rows (n i j : ℕ) (hn : n ≤ 16) (hi : 1 ≤ i) (hij : i < j) (hj : j ≤ n - 1)
    (hdi : b n i < b n (i - 1)) (hdj : b n (j - 1) < b n j) : False := by
  have h := rowsOK_sound 16 rows_16 n (by omega) hn
  have e : bT n = b n := funext (bT_eq n)
  rw [e] at h
  exact updown_sound (b n) (n - 1) 0 h i j (by omega) hij (by omega) hdi hdj

end Tab
end Parking
