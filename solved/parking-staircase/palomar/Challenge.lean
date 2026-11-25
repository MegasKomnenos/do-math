module

public import Mathlib.Data.Fintype.Pi
public import Mathlib.Data.List.OfFn
public import Mathlib.Data.Finset.Card

/-!
# The staircase of the parking functions counted by maximum displacement

Suppose that `n` cars arrive one after another at a one-way street with `n` spots. Each car has a
preferred spot; it drives to that spot and parks in the first empty spot at or after it. The
sequence of the `n` preferences, in the order of arrival, is a *parking function* of length `n` if
every car parks. The *displacement* of a car is the distance between the spot it takes and its
preferred spot, and the *maximum displacement* of a parking function is the largest displacement
of its cars. Let `b n ℓ` be the number of parking functions of length `n` whose maximum
displacement is exactly `ℓ`. Row `n` is the sequence `b n 0, b n 1, …, b n (n - 1)`.

Row `n` has its *peak at* `p`, where `p ≤ n - 1`, if

  `b n 0 < b n 1 < ⋯ < b n p ≥ b n (p + 1) > b n (p + 2) > ⋯ > b n (n - 1)`,

and a *strict peak at* `p` if in addition `b n p > b n (p + 1)`. For `p = n - 1` the part of the
chain after `b n p` is absent. So a row with a peak rises strictly and then falls strictly, and it
has at most one pair of equal neighbouring entries, which then stands directly after the peak.

**Theorem** (`Parking.staircase`). For every `n ≥ 2` there is a position `p` such that row `n` has
its peak at `p`, and row `n + 1` has its peak at the same `p` or a strict peak at `p + 1`.

**Corollary** (`Parking.unimodal_via_staircase`). For every `n ≥ 1` the sequence
`b n 0, b n 1, …, b n (n - 1)` is unimodal: there is an index `p ≤ n - 1` such that the sequence
does not decrease up to `p` and does not increase from `p` on.

The corollary is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin,
A. Priestley and G. Udell, *ℓ-Interval parking functions: Foata invariance, statistic generating
functions, and ciphers*, arXiv:2507.07243 (version 2; version 1 of July 2025 is titled
*Statistics on ℓ-interval parking functions* and numbers the conjecture the same way). The
conjecture asks for unimodality only. The staircase is not a statement of that paper. It is the
statement through which this formalization proves the conjecture, and it says more than the
conjecture: it makes the rise and the fall strict, it allows equal neighbours in one place only,
and it relates the peaks of two consecutive rows.

## Conventions

Spots and preferences are numbered `0, 1, …, n - 1` here, while the conjecture numbers them
`1, …, n`. A preference sequence is a function `α : Fin n → Fin n`, and car `i` (counted from `0`)
prefers spot `α i`. Shifting every spot and every preference by one does not change a
displacement, which is a difference of a spot and a preference, so `b n ℓ` is the number in the
conjecture.

`b n ℓ` is defined for every natural number `ℓ`; the two theorems use it only for `ℓ ≤ n - 1` in
row `n` and for `ℓ ≤ n` in row `n + 1`. The subtractions are subtractions of natural numbers, and
in the two theorems each of them is the ordinary difference: `n - 1` occurs for rows `n ≥ 1` only,
and `k - 1` and `ℓ - 1` occur under `1 ≤ k` and `1 ≤ ℓ`. In `dispList` the difference `p - a` of a
spot and a preference is the ordinary difference as well, because a car parks at or after its
preference. In the corollary the range `p ≤ ℓ ≤ n - 2` is written `ℓ + 1 ≤ n - 1`, so that it is
empty for `n = 1`.

The definitions below are, character for character, those of the proof development. The first
seven are from `Parking/Defs.lean`, where only `Parking.IsParkingFunction` and `Parking.A`, which
the statements do not use, are left out; `IsPeak` and `IsStrictPeak` are from
`Staircase/Peak.lean`. Comparator checks that the definitions used by the statements are the same
declarations in this file and in the proof.

* `firstFree n occ a`: the spot a car with preference `a` takes when the spots in `occ` are
  occupied, or `none` if the spots `a, …, n - 1` are all occupied.
* `parkFrom n occ prefs`: park the cars with preferences `prefs` one after another.
* `prefList α`, `positions α`: the preferences of `α` as a list, and the spots taken by the cars.
* `dispList`, `maxDisp α`: the displacements and their maximum, which is `none` exactly when `α`
  is not a parking function.
* `b n ℓ`: the number of `α : Fin n → Fin n` with `maxDisp α = some ℓ`.
* `IsPeak f n p`, `IsStrictPeak f n p`: row `n` of an arbitrary array `f : ℕ → ℕ → ℕ` has its
  peak, or a strict peak, at `p`. The theorems use them for the array `b`.
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

/-- **The staircase.** For every `n ≥ 2` there is `p` such that the row `b n 0, …, b n (n-1)` has
its peak at `p`,
`b n 0 < ⋯ < b n p ≥ b n (p+1) > ⋯ > b n (n-1)`,
and the row `n + 1` has its peak at `p` as well, or a strict peak at `p + 1`,
`b (n+1) 0 < ⋯ < b (n+1) (p+1) > b (n+1) (p+2) > ⋯ > b (n+1) n`. -/
theorem staircase (n : ℕ) (hn : 2 ≤ n) :
    ∃ p, IsPeak b n p ∧ (IsPeak b (n + 1) p ∨ IsStrictPeak b (n + 1) (p + 1)) := by
  sorry

/-- **Unimodality of the rows** (Conjecture 6.5 of arXiv:2507.07243). For every `n ≥ 1` there is
`p ≤ n - 1` such that `b n (ℓ - 1) ≤ b n ℓ` for `1 ≤ ℓ ≤ p` and `b n (ℓ + 1) ≤ b n ℓ` for
`p ≤ ℓ ≤ n - 2`. The second range is written `ℓ + 1 ≤ n - 1`, so that for `n = 1`, where the
natural-number subtraction `n - 2` would be `0`, it is empty, as it is in the conjecture. -/
theorem unimodal_via_staircase (n : ℕ) (hn : 1 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ) := by
  sorry

end Parking
