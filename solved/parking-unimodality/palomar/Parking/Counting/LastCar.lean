module

public import Parking.Defs
public import Mathlib.Order.Interval.Finset.Nat
public import Mathlib.Tactic.Ring
public import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
# The last-car recursion

`A n k` is the number of parking functions of length `n` all of whose displacements are at most
`k`, and `b n ℓ` the number of those whose maximum displacement is exactly `ℓ`
(`Parking/Defs.lean`).  This file proves the recursion on which every later count rests:

  `A (n+1) k = ∑_{j ≤ n} min (j+1) (k+1) * (C(n,j) * (A j k * A (n-j) k))`   (`A_succ`).

The last car parks in the unique spot `j` left empty by the first `n` cars.  The cars that parked
to the left of `j` form a parking function of length `j`, the cars to the right one of length
`n - j`, the two groups are interleaved arbitrarily, and the last car may prefer any of the
spots `j - min(j,k), …, j`.

The proof counts preference lists by the *set of spots taken* (`goodLists`), removes the last car
(`card_goodLists_succ`), shows that the count does not change when the spots are translated or the
street is lengthened (`card_goodLists_shift`), and that the count for two groups of spots separated
by a free spot is a binomial coefficient times the product of the two counts
(`card_goodLists_union`).  `A n k` is the count for the full set of spots (`A_eq_card_goodLists`).

The file ends with the elementary relations between `b` and `A`: `A_zero`, `A_mono`, `b_zero`,
`b_succ_add_A`, and `d_eq_A`, which writes the step `b n k - b n (k-1)` of a column `k ≥ 2` as the
second difference `A n k - 2 A n (k-1) + A n (k-2)`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### The parking process

Specification of `firstFree`, the unfolding of `parkFrom` at the first and at the last car, and
the elementary properties of the list of spots taken (length, bound, distinctness). -/

private theorem firstFree_eq_some_iff {n : ℕ} {occ : Finset ℕ} {a s : ℕ} :
    firstFree n occ a = some s ↔
      a ≤ s ∧ s < n ∧ s ∉ occ ∧ ∀ j, a ≤ j → j < s → j ∈ occ := by
  unfold firstFree
  rw [List.find?_range_eq_some]
  constructor
  · rintro ⟨hp, hmem, hlt⟩
    have hp' : a ≤ s ∧ s ∉ occ := by simpa using hp
    refine ⟨hp'.1, by simpa using hmem, hp'.2, fun j hj hjs => ?_⟩
    have h := hlt j hjs
    by_contra hcon
    simp [hj, hcon] at h
  · rintro ⟨h1, h2, h3, h4⟩
    refine ⟨by simp [h1, h3], by simpa using h2, fun j hjs => ?_⟩
    by_cases hj : a ≤ j
    · simp [h4 j hj hjs]
    · simp [hj]

@[simp] private theorem parkFrom_nil (n : ℕ) (occ : Finset ℕ) : parkFrom n occ [] = some [] := by
  simp [parkFrom]

/-- Unfolding of the process at the first car. -/
private theorem parkFrom_cons (n : ℕ) (occ : Finset ℕ) (a : ℕ) (rest : List ℕ) :
    parkFrom n occ (a :: rest) =
      (firstFree n occ a).bind fun s => (parkFrom n (insert s occ) rest).map (s :: ·) := by
  rw [parkFrom]
  cases h : firstFree n occ a with
  | none => simp
  | some s =>
    cases h' : parkFrom n (insert s occ) rest <;> simp [h']

/-- Unfolding of the process at the last car. -/
private theorem parkFrom_append_singleton (n : ℕ) (occ : Finset ℕ) (l : List ℕ) (a : ℕ) :
    parkFrom n occ (l ++ [a]) =
      (parkFrom n occ l).bind fun ps =>
        (firstFree n (occ ∪ ps.toFinset) a).map fun s => ps ++ [s] := by
  induction l generalizing occ with
  | nil =>
    rw [List.nil_append, parkFrom_cons, parkFrom_nil]
    simp only [Option.bind_some, List.toFinset_nil, Finset.union_empty, List.nil_append]
    cases firstFree n occ a <;> simp
  | cons c l ih =>
    rw [List.cons_append, parkFrom_cons, parkFrom_cons]
    cases h1 : firstFree n occ c with
    | none => simp
    | some s =>
      simp only [Option.bind_some]
      rw [ih]
      cases h2 : parkFrom n (insert s occ) l with
      | none => simp
      | some ps =>
        have hU : occ ∪ (s :: ps).toFinset = insert s occ ∪ ps.toFinset := by
          ext x
          simp only [List.toFinset_cons, Finset.mem_union, Finset.mem_insert]
          tauto
        simp only [Option.bind_some, Option.map_some, hU]
        cases firstFree n (insert s occ ∪ ps.toFinset) a <;> simp

/-- The list of spots has the same length as the list of preferences. -/
private theorem parkFrom_length {n : ℕ} {occ : Finset ℕ} {l ps : List ℕ}
    (h : parkFrom n occ l = some ps) : ps.length = l.length := by
  induction l generalizing occ ps with
  | nil =>
    rw [parkFrom_nil] at h
    cases h
    rfl
  | cons a l ih =>
    rw [parkFrom_cons, Option.bind_eq_some_iff] at h
    obtain ⟨s, -, h⟩ := h
    obtain ⟨ps0, hps0, rfl⟩ := Option.map_eq_some_iff.mp h
    simp [ih hps0]

/-- Spots taken are spots of the street, were free at the start, and are pairwise distinct. -/
private theorem parkFrom_spec {n : ℕ} {occ : Finset ℕ} {l ps : List ℕ}
    (h : parkFrom n occ l = some ps) :
    (∀ s ∈ ps, s < n ∧ s ∉ occ) ∧ ps.Nodup := by
  induction l generalizing occ ps with
  | nil =>
    rw [parkFrom_nil] at h
    cases h
    simp
  | cons a l ih =>
    rw [parkFrom_cons, Option.bind_eq_some_iff] at h
    obtain ⟨s, hs, h⟩ := h
    obtain ⟨ps0, hps0, rfl⟩ := Option.map_eq_some_iff.mp h
    obtain ⟨h1, h2⟩ := ih hps0
    rw [firstFree_eq_some_iff] at hs
    refine ⟨?_, ?_⟩
    · intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact ⟨hs.2.1, hs.2.2.1⟩
      · have := h1 x hx
        exact ⟨this.1, fun hmem => this.2 (Finset.mem_insert_of_mem hmem)⟩
    · refine List.nodup_cons.mpr ⟨fun hmem => ?_, h2⟩
      exact (h1 s hmem).2 (Finset.mem_insert_self s occ)

/-- Displacement lists split at the last car. -/
private theorem dispList_append_singleton {l ps : List ℕ} (hlen : ps.length = l.length) (a s : ℕ) :
    dispList (l ++ [a]) (ps ++ [s]) = dispList l ps ++ [s - a] := by
  unfold dispList
  rw [List.zipWith_append hlen]
  rfl

/-! ### Displacement bound -/

/-- All displacements are at most `k`. -/
private def DispLE (k : ℕ) (prefs ps : List ℕ) : Prop := ∀ d ∈ dispList prefs ps, d ≤ k

private theorem dispLE_append_singleton {k : ℕ} {l ps : List ℕ} (hlen : ps.length = l.length)
    (a s : ℕ) : DispLE k (l ++ [a]) (ps ++ [s]) ↔ DispLE k l ps ∧ s - a ≤ k := by
  simp [DispLE, dispList_append_singleton hlen, or_imp, forall_and]

private theorem forall_le_iff_foldr_max_le (l : List ℕ) (k : ℕ) :
    (∀ d ∈ l, d ≤ k) ↔ l.foldr max 0 ≤ k := by
  induction l with
  | nil => simp
  | cons x l ih =>
    simp only [List.mem_cons, forall_eq_or_imp, List.foldr_cons, max_le_iff, ih]

private theorem toFinset_append_singleton (ps : List ℕ) (s : ℕ) :
    (ps ++ [s]).toFinset = insert s ps.toFinset := by
  ext x
  simp

/-! ### Preference lists -/

/-- All preference lists of length `m` with entries `< N`, built by appending one entry at a
time. -/
private def prefLists (N : ℕ) : ℕ → Finset (List ℕ)
  | 0 => {[]}
  | m + 1 => ((prefLists N m) ×ˢ range N).image fun p => p.1 ++ [p.2]

private theorem mem_prefLists {N m : ℕ} {l : List ℕ} :
    l ∈ prefLists N m ↔ l.length = m ∧ ∀ a ∈ l, a < N := by
  induction m generalizing l with
  | zero =>
    simp only [prefLists, mem_singleton]
    constructor
    · rintro rfl
      simp
    · rintro ⟨h, -⟩
      exact List.eq_nil_of_length_eq_zero h
  | succ m ih =>
    simp only [prefLists, mem_image, mem_product, mem_range, Prod.exists]
    constructor
    · rintro ⟨l0, a, ⟨hl0, ha⟩, rfl⟩
      obtain ⟨h1, h2⟩ := ih.mp hl0
      refine ⟨by simp [h1], fun x hx => ?_⟩
      rcases List.mem_append.mp hx with hx | hx
      · exact h2 x hx
      · have hxa : x = a := by simpa using hx
        rw [hxa]
        exact ha
    · rintro ⟨hlen, hlt⟩
      have hne : l ≠ [] := by
        intro h
        rw [h] at hlen
        simp at hlen
      refine ⟨l.dropLast, l.getLast hne, ⟨ih.mpr ⟨by simp [hlen], fun a ha =>
        hlt a (List.mem_of_mem_dropLast ha)⟩, hlt _ (List.getLast_mem hne)⟩,
        List.dropLast_append_getLast hne⟩

/-- Preference lists of length `m` (entries `< N`) for which every car parks, the set of spots
taken is exactly `O`, and every displacement is at most `k`. -/
private noncomputable def goodLists (N k : ℕ) (O : Finset ℕ) (m : ℕ) : Finset (List ℕ) :=
  @Finset.filter _ (fun l => ∃ ps, parkFrom N ∅ l = some ps ∧ ps.toFinset = O ∧ DispLE k l ps)
    (Classical.decPred _) (prefLists N m)

private theorem mem_goodLists {N k m : ℕ} {O : Finset ℕ} {l : List ℕ} :
    l ∈ goodLists N k O m ↔ l ∈ prefLists N m ∧
      ∃ ps, parkFrom N ∅ l = some ps ∧ ps.toFinset = O ∧ DispLE k l ps := by
  unfold goodLists
  exact @Finset.mem_filter _ _ (Classical.decPred _) _ _

/-- The preferences `a` with which a car arriving last takes spot `s`, leaving exactly the spots
of `O` occupied, with displacement at most `k`. -/
private def lastChoices (N k : ℕ) (O : Finset ℕ) (s : ℕ) : Finset ℕ :=
  (range N).filter fun a => firstFree N (O.erase s) a = some s ∧ s - a ≤ k

private theorem mem_lastChoices {N k s a : ℕ} {O : Finset ℕ} :
    a ∈ lastChoices N k O s ↔ a < N ∧ firstFree N (O.erase s) a = some s ∧ s - a ≤ k := by
  unfold lastChoices
  rw [mem_filter, mem_range]

/-- A car arriving last with preference `a` takes spot `s` exactly when the spots from `a` up to
`s` (excluded) are occupied. -/
private theorem mem_lastChoices' {N k s a : ℕ} {O : Finset ℕ} :
    a ∈ lastChoices N k O s ↔
      s < N ∧ a ≤ s ∧ (∀ j, a ≤ j → j < s → j ∈ O) ∧ s - a ≤ k := by
  rw [mem_lastChoices, firstFree_eq_some_iff]
  constructor
  · rintro ⟨-, ⟨h1, h2, -, h4⟩, h5⟩
    exact ⟨h2, h1, fun j hj hjs => (mem_erase.mp (h4 j hj hjs)).2, h5⟩
  · rintro ⟨h2, h1, h4, h5⟩
    exact ⟨lt_of_le_of_lt h1 h2, ⟨h1, h2, notMem_erase s O, fun j hj hjs =>
      mem_erase.mpr ⟨ne_of_lt hjs, h4 j hj hjs⟩⟩, h5⟩

/-! ### Removing the last car -/

private theorem append_mem_goodLists_succ {N k m : ℕ} {O : Finset ℕ} {l : List ℕ} {a : ℕ} :
    l ++ [a] ∈ goodLists N k O (m + 1) ↔
      ∃ s ∈ O, l ∈ goodLists N k (O.erase s) m ∧ a ∈ lastChoices N k O s := by
  rw [mem_goodLists]
  constructor
  · rintro ⟨hpl, ps', hpark, hO, hdisp⟩
    rw [mem_prefLists] at hpl
    obtain ⟨hlen, hlt⟩ := hpl
    have hlen' : l.length = m := by simpa using hlen
    rw [parkFrom_append_singleton, Option.bind_eq_some_iff] at hpark
    obtain ⟨ps, hps, h⟩ := hpark
    obtain ⟨s, hs, rfl⟩ := Option.map_eq_some_iff.mp h
    have hs' : firstFree N ps.toFinset a = some s := by simpa using hs
    have hsnot : s ∉ ps.toFinset := (firstFree_eq_some_iff.mp hs').2.2.1
    rw [toFinset_append_singleton] at hO
    have hsO : s ∈ O := by
      rw [← hO]
      exact mem_insert_self _ _
    have herase : ps.toFinset = O.erase s := by
      rw [← hO, erase_insert hsnot]
    have hpslen := parkFrom_length hps
    rw [dispLE_append_singleton hpslen] at hdisp
    refine ⟨s, hsO, ?_, ?_⟩
    · rw [mem_goodLists]
      exact ⟨mem_prefLists.mpr ⟨hlen', fun x hx => hlt x (List.mem_append_left _ hx)⟩,
        ps, hps, herase, hdisp.1⟩
    · rw [mem_lastChoices]
      refine ⟨hlt a (by simp), ?_, hdisp.2⟩
      rw [← herase]
      exact hs'
  · rintro ⟨s, hsO, hl, ha⟩
    rw [mem_goodLists] at hl
    obtain ⟨hpl, ps, hps, hOps, hdisp⟩ := hl
    rw [mem_lastChoices] at ha
    obtain ⟨haN, hff, hk⟩ := ha
    rw [mem_prefLists] at hpl
    refine ⟨mem_prefLists.mpr ⟨by simp [hpl.1], fun x hx => ?_⟩, ps ++ [s], ?_, ?_, ?_⟩
    · rcases List.mem_append.mp hx with hx | hx
      · exact hpl.2 x hx
      · have hxa : x = a := by simpa using hx
        rw [hxa]
        exact haN
    · rw [parkFrom_append_singleton, hps]
      simp [hOps, hff]
    · rw [toFinset_append_singleton, hOps, insert_erase hsO]
    · exact (dispLE_append_singleton (parkFrom_length hps) a s).mpr ⟨hdisp, hk⟩

private theorem card_goodLists_succ (N k m : ℕ) (O : Finset ℕ) :
    (goodLists N k O (m + 1)).card =
      ∑ s ∈ O, (goodLists N k (O.erase s) m).card * (lastChoices N k O s).card := by
  classical
  have key : goodLists N k O (m + 1) =
      O.biUnion fun s => ((goodLists N k (O.erase s) m) ×ˢ (lastChoices N k O s)).image
        fun p => p.1 ++ [p.2] := by
    ext l'
    simp only [mem_biUnion, mem_image, mem_product, Prod.exists]
    constructor
    · intro h
      have hpl : l' ∈ prefLists N (m + 1) := (mem_goodLists.mp h).1
      simp only [prefLists, mem_image, mem_product, Prod.exists] at hpl
      obtain ⟨l, a, -, rfl⟩ := hpl
      obtain ⟨s, hsO, hl, ha⟩ := append_mem_goodLists_succ.mp h
      exact ⟨s, hsO, l, a, ⟨hl, ha⟩, rfl⟩
    · rintro ⟨s, hsO, l, a, ⟨hl, ha⟩, rfl⟩
      exact append_mem_goodLists_succ.mpr ⟨s, hsO, hl, ha⟩
  rw [key, card_biUnion]
  · refine sum_congr rfl fun s _ => ?_
    rw [card_image_of_injective, card_product]
    rintro ⟨l1, a1⟩ ⟨l2, a2⟩ h
    have h' := List.append_inj' h rfl
    have h2 : a1 = a2 := by simpa using h'.2
    exact Prod.ext h'.1 h2
  · intro s hs s' hs' hne
    have hsO : s ∈ O := mem_coe.mp hs
    change Disjoint _ _
    rw [Finset.disjoint_left]
    intro l' h1 h2
    simp only [mem_image, mem_product, Prod.exists] at h1 h2
    obtain ⟨l1, a1, ⟨hl1, -⟩, rfl⟩ := h1
    obtain ⟨l2, a2, ⟨hl2, -⟩, h⟩ := h2
    have hl : l2 = l1 := (List.append_inj' h rfl).1
    subst hl
    obtain ⟨-, ps1, hp1, hO1, -⟩ := mem_goodLists.mp hl1
    obtain ⟨-, ps2, hp2, hO2, -⟩ := mem_goodLists.mp hl2
    rw [hp1] at hp2
    have hps : ps1 = ps2 := Option.some.inj hp2
    have heq : O.erase s = O.erase s' := by rw [← hO1, ← hO2, hps]
    have hmem : s ∈ O.erase s' := mem_erase.mpr ⟨hne, hsO⟩
    rw [← heq] at hmem
    exact notMem_erase s O hmem

private theorem card_goodLists_zero (N k : ℕ) : (goodLists N k ∅ 0).card = 1 := by
  have h : goodLists N k ∅ 0 = {[]} := by
    ext l
    rw [mem_goodLists, mem_prefLists, mem_singleton]
    constructor
    · rintro ⟨⟨h, -⟩, -⟩
      exact List.eq_nil_of_length_eq_zero h
    · rintro rfl
      exact ⟨⟨rfl, by simp⟩, [], by simp, by simp, by simp [DispLE, dispList]⟩
  rw [h, card_singleton]

/-! ### Translation invariance and independence of the length of the street -/

private theorem lastChoices_shift (N N' k c : ℕ) (O : Finset ℕ) (s : ℕ) (hs : s < N)
    (hs' : s + c < N') :
    lastChoices N' k (O.image (· + c)) (s + c) = (lastChoices N k O s).image (· + c) := by
  ext a'
  rw [mem_lastChoices', mem_image]
  constructor
  · rintro ⟨-, h2, h3, h4⟩
    have hca : c ≤ a' := by
      by_contra hcon
      have hmem := h3 a' le_rfl (by omega)
      rw [mem_image] at hmem
      obtain ⟨x, -, hx⟩ := hmem
      omega
    refine ⟨a' - c, ?_, by omega⟩
    rw [mem_lastChoices']
    refine ⟨hs, by omega, fun j hj hjs => ?_, by omega⟩
    have hmem := h3 (j + c) (by omega) (by omega)
    rw [mem_image] at hmem
    obtain ⟨x, hx, hxj⟩ := hmem
    have hxj' : x = j := by omega
    rw [← hxj']
    exact hx
  · rintro ⟨a, ha, rfl⟩
    rw [mem_lastChoices'] at ha
    obtain ⟨-, h2, h3, h4⟩ := ha
    refine ⟨hs', by omega, fun j hj hjs => ?_, by omega⟩
    rw [mem_image]
    exact ⟨j - c, h3 (j - c) (by omega) (by omega), by omega⟩

/-- The count depends neither on the position of the set of spots nor on the length of the
street: translating `O` by `c` inside a street of any sufficient length leaves it unchanged. -/
private theorem card_goodLists_shift (k c : ℕ) :
    ∀ (m N N' : ℕ) (O : Finset ℕ), O.card = m → (∀ x ∈ O, x < N) → (∀ x ∈ O, x + c < N') →
      (goodLists N' k (O.image (· + c)) m).card = (goodLists N k O m).card := by
  intro m
  induction m with
  | zero =>
    intro N N' O hO _ _
    have hO' : O = ∅ := card_eq_zero.mp hO
    subst hO'
    rw [image_empty, card_goodLists_zero, card_goodLists_zero]
  | succ m ih =>
    intro N N' O hO hN hN'
    have hinj : Function.Injective (· + c : ℕ → ℕ) := add_left_injective c
    rw [card_goodLists_succ, card_goodLists_succ, sum_image (fun x _ y _ h => hinj h)]
    refine sum_congr rfl fun s hs => ?_
    rw [← image_erase hinj, lastChoices_shift N N' k c O s (hN s hs) (hN' s hs),
      card_image_of_injective _ hinj]
    congr 1
    refine ih N N' (O.erase s) ?_ (fun x hx => hN x (mem_of_mem_erase hx))
      (fun x hx => hN' x (mem_of_mem_erase hx))
    rw [card_erase_of_mem hs, hO]
    rfl

/-! ### Two groups of spots separated by a free spot -/

/-- `O₁` lies to the left of the spot `g` and `O₂` to the right of it. -/
private def Separated (O₁ O₂ : Finset ℕ) (g : ℕ) : Prop := (∀ x ∈ O₁, x < g) ∧ (∀ y ∈ O₂, g < y)

private theorem Separated.disjoint {O₁ O₂ : Finset ℕ} {g : ℕ} (h : Separated O₁ O₂ g) :
    Disjoint O₁ O₂ := by
  rw [Finset.disjoint_left]
  intro x h1 h2
  have := h.1 x h1
  have := h.2 x h2
  omega

private theorem lastChoices_union_left (N k : ℕ) {O₁ O₂ : Finset ℕ} {g s : ℕ}
    (hsep : Separated O₁ O₂ g) (hs : s ∈ O₁) :
    lastChoices N k (O₁ ∪ O₂) s = lastChoices N k O₁ s := by
  ext a
  rw [mem_lastChoices', mem_lastChoices']
  constructor
  · rintro ⟨h1, h2, h3, h4⟩
    refine ⟨h1, h2, fun j hj hjs => ?_, h4⟩
    rcases mem_union.mp (h3 j hj hjs) with h | h
    · exact h
    · have := hsep.2 j h
      have := hsep.1 s hs
      omega
  · rintro ⟨h1, h2, h3, h4⟩
    exact ⟨h1, h2, fun j hj hjs => mem_union_left _ (h3 j hj hjs), h4⟩

private theorem lastChoices_union_right (N k : ℕ) {O₁ O₂ : Finset ℕ} {g s : ℕ}
    (hsep : Separated O₁ O₂ g) (hs : s ∈ O₂) :
    lastChoices N k (O₁ ∪ O₂) s = lastChoices N k O₂ s := by
  ext a
  rw [mem_lastChoices', mem_lastChoices']
  constructor
  · rintro ⟨h1, h2, h3, h4⟩
    have hgs : g < s := hsep.2 s hs
    have hga : g < a := by
      by_contra hcon
      have hg : g ∈ O₁ ∪ O₂ := h3 g (by omega) hgs
      rcases mem_union.mp hg with h | h
      · exact absurd (hsep.1 g h) (lt_irrefl g)
      · exact absurd (hsep.2 g h) (lt_irrefl g)
    refine ⟨h1, h2, fun j hj hjs => ?_, h4⟩
    rcases mem_union.mp (h3 j hj hjs) with h | h
    · have := hsep.1 j h
      omega
    · exact h
  · rintro ⟨h1, h2, h3, h4⟩
    exact ⟨h1, h2, fun j hj hjs => mem_union_right _ (h3 j hj hjs), h4⟩

/-- The count for two groups of spots separated by a free spot: the two groups of cars are
interleaved arbitrarily. -/
private theorem card_goodLists_union (N k : ℕ) :
    ∀ (M : ℕ) (O₁ O₂ : Finset ℕ) (g : ℕ), O₁.card + O₂.card = M → Separated O₁ O₂ g →
      (goodLists N k (O₁ ∪ O₂) M).card =
        M.choose O₁.card *
          ((goodLists N k O₁ O₁.card).card * (goodLists N k O₂ O₂.card).card) := by
  intro M
  induction M with
  | zero =>
    intro O₁ O₂ g hM _
    have h1 : O₁ = ∅ := card_eq_zero.mp (by omega)
    have h2 : O₂ = ∅ := card_eq_zero.mp (by omega)
    subst h1 h2
    simp [card_goodLists_zero]
  | succ M ih =>
    intro O₁ O₂ g hM hsep
    have hdisj := hsep.disjoint
    -- the two partial sums
    have e1 : ∀ s ∈ O₁, (goodLists N k ((O₁ ∪ O₂).erase s) M).card *
        (lastChoices N k (O₁ ∪ O₂) s).card =
        M.choose (O₁.card - 1) * (goodLists N k O₂ O₂.card).card *
          ((goodLists N k (O₁.erase s) (O₁.card - 1)).card * (lastChoices N k O₁ s).card) := by
      intro s hs
      have hs2 : s ∉ O₂ := fun h => (Finset.disjoint_left.mp hdisj hs) h
      have hc : (O₁.erase s).card = O₁.card - 1 := card_erase_of_mem hs
      have hpos : 0 < O₁.card := card_pos.mpr ⟨s, hs⟩
      rw [erase_union_distrib, erase_eq_of_notMem hs2, lastChoices_union_left N k hsep hs,
        ih (O₁.erase s) O₂ g (by rw [hc]; omega)
          ⟨fun x hx => hsep.1 x (mem_of_mem_erase hx), hsep.2⟩, hc]
      ring
    have e2 : ∀ s ∈ O₂, (goodLists N k ((O₁ ∪ O₂).erase s) M).card *
        (lastChoices N k (O₁ ∪ O₂) s).card =
        M.choose O₁.card * (goodLists N k O₁ O₁.card).card *
          ((goodLists N k (O₂.erase s) (O₂.card - 1)).card * (lastChoices N k O₂ s).card) := by
      intro s hs
      have hs1 : s ∉ O₁ := fun h => (Finset.disjoint_left.mp hdisj h) hs
      have hc : (O₂.erase s).card = O₂.card - 1 := card_erase_of_mem hs
      have hpos : 0 < O₂.card := card_pos.mpr ⟨s, hs⟩
      rw [erase_union_distrib, erase_eq_of_notMem hs1, lastChoices_union_right N k hsep hs,
        ih O₁ (O₂.erase s) g (by rw [hc]; omega)
          ⟨hsep.1, fun x hx => hsep.2 x (mem_of_mem_erase hx)⟩, hc]
      ring
    rw [card_goodLists_succ, sum_union hdisj, sum_congr rfl e1, sum_congr rfl e2,
      ← mul_sum, ← mul_sum]
    -- evaluate the two inner sums by the recursion for `O₁` and for `O₂`
    rcases Nat.eq_zero_or_pos O₁.card with h1 | h1
    · have hO1 : O₁ = ∅ := card_eq_zero.mp h1
      subst hO1
      have hc2 : O₂.card = M + 1 := by simpa using hM
      have hrec := card_goodLists_succ N k M O₂
      rw [hc2]
      simp only [card_empty, sum_empty, mul_zero, zero_add, Nat.choose_zero_right, one_mul,
        card_goodLists_zero, Nat.add_sub_cancel]
      rw [← hrec]
    · obtain ⟨m1, hm1⟩ : ∃ m1, O₁.card = m1 + 1 := ⟨O₁.card - 1, by omega⟩
      have hrec1 := card_goodLists_succ N k m1 O₁
      rcases Nat.eq_zero_or_pos O₂.card with h2 | h2
      · have hO2 : O₂ = ∅ := card_eq_zero.mp h2
        subst hO2
        have hMm : M = m1 := by
          rw [card_empty] at hM
          omega
        subst hMm
        rw [hm1]
        simp only [card_empty, sum_empty, mul_zero, add_zero, Nat.add_sub_cancel,
          Nat.choose_self, one_mul, card_goodLists_zero, mul_one]
        rw [← hrec1]
      · obtain ⟨m2, hm2⟩ : ∃ m2, O₂.card = m2 + 1 := ⟨O₂.card - 1, by omega⟩
        have hrec2 := card_goodLists_succ N k m2 O₂
        have hMm : M = m1 + m2 + 1 := by omega
        rw [hm1, hm2]
        simp only [Nat.add_sub_cancel]
        rw [← hrec1, ← hrec2, hMm, Nat.choose_succ_succ' (m1 + m2 + 1) m1]
        ring

/-! ### The cumulative count as a count of lists -/

private theorem prefList_injective (n : ℕ) : Function.Injective
    (prefList : (Fin n → Fin n) → List ℕ) := by
  intro α β h
  unfold prefList at h
  have h' := List.ofFn_injective h
  funext i
  exact Fin.val_injective (congrFun h' i)

private theorem prefList_mem_prefLists {n : ℕ} (α : Fin n → Fin n) :
    prefList α ∈ prefLists n n := by
  rw [mem_prefLists]
  refine ⟨by simp [prefList], fun a ha => ?_⟩
  unfold prefList at ha
  rw [List.mem_ofFn] at ha
  obtain ⟨i, rfl⟩ := ha
  exact (α i).isLt

private theorem exists_prefList_eq {n : ℕ} {l : List ℕ} (hl : l ∈ prefLists n n) :
    ∃ α : Fin n → Fin n, prefList α = l := by
  rw [mem_prefLists] at hl
  obtain ⟨hlen, hlt⟩ := hl
  subst hlen
  refine ⟨fun i => ⟨l.get i, hlt _ (List.get_mem l i)⟩, ?_⟩
  unfold prefList
  exact List.ofFn_get l

/-- If `n` cars park on `n` spots then they take all the spots. -/
private theorem toFinset_eq_range_of_parkFrom {n : ℕ} {l ps : List ℕ} (hlen : l.length = n)
    (h : parkFrom n ∅ l = some ps) : ps.toFinset = range n := by
  obtain ⟨h1, h2⟩ := parkFrom_spec h
  apply eq_of_subset_of_card_le
  · intro x hx
    rw [mem_range]
    exact (h1 x (List.mem_toFinset.mp hx)).1
  · rw [card_range, List.toFinset_card_of_nodup h2, parkFrom_length h, hlen]

private theorem maxDisp_eq_some_iff {n : ℕ} (α : Fin n → Fin n) (m : ℕ) :
    maxDisp α = some m ↔
      ∃ ps, parkFrom n ∅ (prefList α) = some ps ∧
        (dispList (prefList α) ps).foldr max 0 = m := by
  unfold maxDisp positions
  rw [Option.map_eq_some_iff]

/-- `A n k` counts the preference lists of length `n` that fill the street `{0, …, n-1}` with
all displacements at most `k`. -/
private theorem A_eq_card_goodLists (n k : ℕ) : A n k = (goodLists n k (range n) n).card := by
  classical
  unfold A
  rw [← card_image_of_injective _ (prefList_injective n)]
  congr 1
  ext l
  rw [mem_image, mem_goodLists]
  constructor
  · rintro ⟨α, hα, rfl⟩
    rw [mem_filter] at hα
    obtain ⟨-, m, hmk, hm⟩ := hα
    rw [maxDisp_eq_some_iff] at hm
    obtain ⟨ps, hps, hfold⟩ := hm
    refine ⟨prefList_mem_prefLists α, ps, hps,
      toFinset_eq_range_of_parkFrom (by simp [prefList]) hps, ?_⟩
    unfold DispLE
    rw [forall_le_iff_foldr_max_le, hfold]
    exact hmk
  · rintro ⟨hl, ps, hps, -, hdisp⟩
    obtain ⟨α, rfl⟩ := exists_prefList_eq hl
    refine ⟨α, ?_, rfl⟩
    rw [mem_filter]
    refine ⟨mem_univ _, (dispList (prefList α) ps).foldr max 0, ?_, ?_⟩
    · exact (forall_le_iff_foldr_max_le _ _).mp hdisp
    · rw [maxDisp_eq_some_iff]
      exact ⟨ps, hps, rfl⟩

/-! ### The recursion -/

/-- When the last car takes spot `j` of a full street, it may prefer any of the spots
`j - min(j,k), …, j`. -/
private theorem card_lastChoices_range (n k j : ℕ) (hj : j ≤ n) :
    (lastChoices (n + 1) k (range (n + 1)) j).card = min (j + 1) (k + 1) := by
  have h : lastChoices (n + 1) k (range (n + 1)) j = Icc (j - k) j := by
    ext a
    rw [mem_lastChoices', mem_Icc]
    constructor
    · rintro ⟨-, h2, -, h4⟩
      omega
    · rintro ⟨h1, h2⟩
      refine ⟨by omega, h2, fun i _ hi => ?_, by omega⟩
      rw [mem_range]
      omega
  rw [h, Nat.card_Icc]
  omega

/-- **Last-car recursion** for the number of parking functions of length `n + 1` with all
displacements at most `k`. -/
theorem A_succ (n k : ℕ) :
    A (n + 1) k =
      ∑ j ∈ range (n + 1), min (j + 1) (k + 1) * (n.choose j * (A j k * A (n - j) k)) := by
  rw [A_eq_card_goodLists, card_goodLists_succ]
  refine sum_congr rfl fun j hj => ?_
  have hjn : j ≤ n := by
    rw [mem_range] at hj
    omega
  have hinj : Function.Injective (· + (j + 1) : ℕ → ℕ) := add_left_injective (j + 1)
  -- the spots other than `j`: those to the left and those to the right
  have hsplit : (range (n + 1)).erase j = range j ∪ (range (n - j)).image (· + (j + 1)) := by
    ext x
    simp only [mem_erase, mem_range, mem_union, mem_image]
    constructor
    · rintro ⟨hne, hlt⟩
      by_cases hx : x < j
      · exact Or.inl hx
      · exact Or.inr ⟨x - (j + 1), by omega, by omega⟩
    · rintro (h | ⟨y, hy, rfl⟩)
      · exact ⟨by omega, by omega⟩
      · exact ⟨by omega, by omega⟩
  have hsep : Separated (range j) ((range (n - j)).image (· + (j + 1))) j := by
    refine ⟨fun x hx => mem_range.mp hx, fun y hy => ?_⟩
    rw [mem_image] at hy
    obtain ⟨z, -, rfl⟩ := hy
    omega
  have hc1 : (range j).card = j := card_range j
  have hc2 : ((range (n - j)).image (· + (j + 1))).card = n - j := by
    rw [card_image_of_injective _ hinj, card_range]
  rw [hsplit, card_goodLists_union (n + 1) k n _ _ j (by rw [hc1, hc2]; omega) hsep, hc1, hc2,
    card_lastChoices_range n k j hjn]
  have hleft : (goodLists (n + 1) k (range j) j).card = A j k := by
    rw [A_eq_card_goodLists]
    simpa using card_goodLists_shift k 0 j j (n + 1) (range j) hc1 (fun x hx => mem_range.mp hx)
      (fun x hx => by have := mem_range.mp hx; omega)
  have hright : (goodLists (n + 1) k ((range (n - j)).image (· + (j + 1))) (n - j)).card =
      A (n - j) k := by
    rw [A_eq_card_goodLists]
    exact card_goodLists_shift k (j + 1) (n - j) (n - j) (n + 1) (range (n - j))
      (card_range _) (fun x hx => mem_range.mp hx)
      (fun x hx => by have := mem_range.mp hx; omega)
  rw [hleft, hright]
  ring

/-! ### Elementary relations between `b` and `A` -/

/-- $A(0,k)=1$ for every $k$: the empty sequence is the one parking function of length $0$, and its
maximum displacement counts as $0$. -/
theorem A_zero (k : ℕ) : A 0 k = 1 := by
  rw [A_eq_card_goodLists, Finset.range_zero]
  exact card_goodLists_zero 0 k

/-- `A n k` is nondecreasing in `k`. -/
theorem A_mono (n : ℕ) {k k' : ℕ} (h : k ≤ k') : A n k ≤ A n k' := by
  unfold A
  apply Finset.card_le_card
  intro α hα
  rw [mem_filter] at hα ⊢
  obtain ⟨hu, m, hm, hα⟩ := hα
  exact ⟨hu, m, le_trans hm h, hα⟩

/-- $b(n,0)=A(n,0)$: maximum displacement exactly $0$ and maximum displacement at most $0$ are the
same condition. -/
theorem b_zero (n : ℕ) : b n 0 = A n 0 := by
  unfold b A
  refine congrArg Finset.card (Finset.filter_congr fun α _ => ?_)
  simp

/-- $b(n,\ell+1)+A(n,\ell)=A(n,\ell+1)$: the parking functions with maximum displacement at most
$\ell+1$ are those with maximum displacement exactly $\ell+1$ together with those with maximum
displacement at most $\ell$. -/
theorem b_succ_add_A (n ℓ : ℕ) : b n (ℓ + 1) + A n ℓ = A n (ℓ + 1) := by
  classical
  unfold b A
  rw [← card_union_of_disjoint]
  · congr 1
    ext α
    simp only [mem_union, mem_filter, mem_univ, true_and]
    constructor
    · rintro (h | ⟨m, hm, h⟩)
      · exact ⟨ℓ + 1, le_rfl, h⟩
      · exact ⟨m, by omega, h⟩
    · rintro ⟨m, hm, h⟩
      rcases Nat.lt_or_ge m (ℓ + 1) with hlt | hge
      · exact Or.inr ⟨m, by omega, h⟩
      · have hm' : m = ℓ + 1 := by omega
        rw [hm'] at h
        exact Or.inl h
  · rw [Finset.disjoint_left]
    intro α h1 h2
    simp only [mem_filter, mem_univ, true_and] at h1 h2
    obtain ⟨m, hm, h⟩ := h2
    rw [h1] at h
    have := Option.some.inj h
    omega

/-- The step of column `k ≥ 2` in the row `n` in terms of the cumulative counts:
`b n k - b n (k-1) = A n k - 2 A n (k-1) + A n (k-2)`. -/
theorem d_eq_A {k : ℕ} (hk : 2 ≤ k) (n : ℕ) :
    (b n k : ℤ) - (b n (k - 1) : ℤ)
      = (A n k : ℤ) - 2 * (A n (k - 1) : ℤ) + (A n (k - 2) : ℤ) := by
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 2 := ⟨k - 2, by omega⟩
  have h1 : b n (j + 2) + A n (j + 1) = A n (j + 2) := b_succ_add_A n (j + 1)
  have h2 : b n (j + 1) + A n j = A n (j + 1) := b_succ_add_A n j
  have e1 : j + 2 - 1 = j + 1 := by omega
  have e2 : j + 2 - 2 = j := by omega
  rw [e1, e2]
  omega

end Parking
