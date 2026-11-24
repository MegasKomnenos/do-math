module


/-!
# Tables: what the two kernel tables share (no imports)

A *table* is a Boolean function on natural numbers that the Lean kernel evaluates
(`decide +kernel`), together with a soundness theorem that turns the value `true` into a statement
about the numbers `b n ℓ`.  Two tables check one column per entry of a list of data and are
evaluated in blocks of consecutive columns:

* `nth l i`       : the entry of a list of data;
* `allRange p k0 c` : `p k` for the columns `k0 ≤ k < k0 + c` (one block);
* `allRange_sound`, `glue` : a block gives `p k = true` on its range, and adjacent ranges combine.
-/

@[expose] public section

namespace Parking
namespace Tab

/-- `nth l i` is the `i`-th entry of `l` (`0` beyond the end). -/
def nth : List Nat → Nat → Nat
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: as, Nat.succ i => nth as i

/-- `allRange p k0 c`: `p k` holds for `k0 ≤ k < k0 + c`. -/
def allRange (p : Nat → Bool) (k0 : Nat) : Nat → Bool
  | 0 => true
  | Nat.succ c => allRange p k0 c && p (k0 + c)

/-- If the Boolean check of a block of columns $k_0\le k<k_0+c$ has the value true, then the check
has the value true for each column of the block. -/
theorem allRange_sound (p : Nat → Bool) (k0 : Nat) : ∀ c, allRange p k0 c = true →
    ∀ k, k0 ≤ k → k < k0 + c → p k = true := by
  intro c
  induction c with
  | zero =>
    intro _ k h1 h2
    omega
  | succ c ih =>
    intro h k h1 h2
    have h' : (allRange p k0 c && p (k0 + c)) = true := h
    simp only [Bool.and_eq_true] at h'
    rcases Nat.lt_or_ge k (k0 + c) with hlt | hge
    · exact ih h'.1 k h1 hlt
    · have e : k = k0 + c := by omega
      rw [e]
      exact h'.2

/-- A statement that holds for `a ≤ k < b` and for `b ≤ k < c` holds for `a ≤ k < c`. -/
theorem glue {P : Nat → Prop} {a b c : Nat} (h1 : ∀ k, a ≤ k → k < b → P k)
    (h2 : ∀ k, b ≤ k → k < c → P k) : ∀ k, a ≤ k → k < c → P k := by
  intro k hk1 hk2
  rcases Nat.lt_or_ge k b with h | h
  · exact h1 k hk1 h
  · exact h2 k h hk2

end Tab
end Parking
