import Mathlib.Data.Nat.Notation

/-!
# The peak of a row

An array `f : ℕ → ℕ → ℕ` is read by rows: the row `n` consists of the `n` entries
`f n 0, …, f n (n-1)`.  This file defines what it means for a row to rise strictly to a position
`p` and to fall strictly after it.

* `IsPeak f n p` : `f n 0 < f n 1 < ⋯ < f n p ≥ f n (p+1) > f n (p+2) > ⋯ > f n (n-1)`.  The row
  rises strictly up to the position `p`; the next entry, if there is one, is not larger; and from
  there on the row falls strictly.  The only place where two neighbouring entries may be equal is
  directly after `p`.
* `IsStrictPeak f n p` : `f n 0 < f n 1 < ⋯ < f n p > f n (p+1) > ⋯ > f n (n-1)`.  The same without
  the possible equality.

A row has at most one `p` with `IsPeak f n p`, since `p` is the number of positions `k` with
`f n (k-1) < f n k`.
-/

namespace Parking

/-- `IsPeak f n p` says that the row `f n 0, …, f n (n-1)` has its peak at the position `p ≤ n - 1`:
`f n (k-1) < f n k` for `1 ≤ k ≤ p`, then `f n (p+1) ≤ f n p` if `p + 1 ≤ n - 1`, and
`f n k < f n (k-1)` for `p + 2 ≤ k ≤ n - 1`. -/
def IsPeak (f : ℕ → ℕ → ℕ) (n p : ℕ) : Prop :=
  p ≤ n - 1 ∧
    (∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k) ∧
    (p + 1 ≤ n - 1 → f n (p + 1) ≤ f n p) ∧
    (∀ k, p + 2 ≤ k → k ≤ n - 1 → f n k < f n (k - 1))

/-- `IsStrictPeak f n p` says that the row `f n 0, …, f n (n-1)` has its peak at the position
`p ≤ n - 1` and no two neighbouring entries are equal: `f n (k-1) < f n k` for `1 ≤ k ≤ p` and
`f n k < f n (k-1)` for `p + 1 ≤ k ≤ n - 1`. -/
def IsStrictPeak (f : ℕ → ℕ → ℕ) (n p : ℕ) : Prop :=
  p ≤ n - 1 ∧
    (∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k) ∧
    (∀ k, p + 1 ≤ k → k ≤ n - 1 → f n k < f n (k - 1))

end Parking
