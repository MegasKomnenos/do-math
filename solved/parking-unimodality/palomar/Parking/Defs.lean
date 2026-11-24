module

public import Mathlib.Data.Fintype.Pi
public import Mathlib.Data.List.OfFn
public import Mathlib.Data.Finset.Card

/-!
# Parking functions and the numbers `b n ℓ`

This file states the objects of the root proposition.

Spots and preferences are numbered `0, 1, …, n-1` here; the root statement numbers them
`1, …, n`. Displacements `pos_i - a_i` are unaffected by this shift.

* `firstFree n occ a` : the spot a car with preference `a` takes when the spots in `occ` are occupied.
* `parkFrom n occ prefs` : park the cars with preferences `prefs` one after another.
* `positions α`, `maxDisp α` : outcome and maximum displacement of a preference sequence
  `α : Fin n → Fin n`.
* `b n ℓ` : the number of parking functions of length `n` with maximum displacement exactly `ℓ`.
-/

@[expose] public section

namespace Parking

/-- `firstFree n occ a` is the spot taken by a car whose preference is `a` when exactly the spots in
`occ` are occupied: the first empty spot among `a, a+1, …, n-1`, or `none` if they are all occupied. -/
def firstFree (n : ℕ) (occ : Finset ℕ) (a : ℕ) : Option ℕ :=
  (List.range n).find? fun s => decide (a ≤ s ∧ s ∉ occ)

/-- `parkFrom n occ prefs`: cars with preferences `prefs` arrive one after another at a street with
spots `0, …, n-1`, of which those in `occ` are already occupied. Each car takes the first empty spot
at or after its preference. The result is `none` if some car cannot park, and otherwise `some ps`,
where `ps` is the list of spots taken by the cars, in order of arrival. -/
def parkFrom (n : ℕ) : Finset ℕ → List ℕ → Option (List ℕ)
  | _, [] => some []
  | occ, a :: rest =>
    match firstFree n occ a with
    | none => none
    | some s =>
      match parkFrom n (insert s occ) rest with
      | none => none
      | some ps => some (s :: ps)

/-- The preferences `a_1, …, a_n` of `α`, as a list of natural numbers. -/
def prefList {n : ℕ} (α : Fin n → Fin n) : List ℕ := List.ofFn fun i => (α i : ℕ)

/-- The spots `pos_1(α), …, pos_n(α)` taken by the cars, or `none` if some car cannot park. -/
def positions {n : ℕ} (α : Fin n → Fin n) : Option (List ℕ) := parkFrom n ∅ (prefList α)

/-- `α` is a parking function if every car parks. -/
def IsParkingFunction {n : ℕ} (α : Fin n → Fin n) : Prop := (positions α).isSome

/-- The list of displacements `pos_i - a_i`, given the preferences and the spots taken. -/
def dispList (prefs ps : List ℕ) : List ℕ := List.zipWith (fun p a => p - a) ps prefs

/-- The maximum displacement `M(α)` of a parking function `α`; `none` if `α` is not a parking
function. -/
def maxDisp {n : ℕ} (α : Fin n → Fin n) : Option ℕ :=
  (positions α).map fun ps => (dispList (prefList α) ps).foldr max 0

/-- `b n ℓ` is the number of parking functions of length `n` whose maximum displacement is
exactly `ℓ`. -/
def b (n ℓ : ℕ) : ℕ :=
  (Finset.univ.filter fun α : Fin n → Fin n => maxDisp α = some ℓ).card

/-- `A n k` is the number of parking functions of length `n` whose maximum displacement is
at most `k`. -/
def A (n k : ℕ) : ℕ :=
  (Finset.univ.filter fun α : Fin n → Fin n => ∃ m, m ≤ k ∧ maxDisp α = some m).card

end Parking
