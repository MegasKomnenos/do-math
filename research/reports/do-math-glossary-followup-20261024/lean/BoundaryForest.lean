import GainLoss

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000

namespace ParkingForest

def descendants {V : Type*} [LT V] [Fintype V] (G : Forest V) (v : V) : Finset V :=
  Finset.univ.filter (fun u => Anc G u v)

theorem ancestors_comparable {V : Type*} [LT V] (G : Forest V) {u v w : V}
    (hv : Anc G u v) (hw : Anc G u w) : Anc G v w ∨ Anc G w v := by
  obtain ⟨k,hk⟩ := (anc_iterate G u v).mp hv
  obtain ⟨l,hl⟩ := (anc_iterate G u w).mp hw
  rcases le_total k l with h | h
  · left
    apply (anc_iterate G v w).mpr
    refine ⟨l-k,?_⟩
    rw [← hk, ← Function.iterate_add_apply, Nat.sub_add_cancel h, hl]
  · right
    apply (anc_iterate G w v).mpr
    refine ⟨k-l,?_⟩
    rw [← hl, ← Function.iterate_add_apply, Nat.sub_add_cancel h, hk]

theorem size_mono_ancestor {V : Type*} [LT V] [Fintype V] (G : Forest V)
    {v w : V} (h : Anc G v w) : size G v ≤ size G w := by
  rw [size_eq_card_filter,size_eq_card_filter]
  apply Finset.card_le_card
  intro u hu
  exact Finset.mem_filter.mpr ⟨Finset.mem_univ _,
    anc_trans G (Finset.mem_filter.mp hu).2 h⟩

theorem descendants_disjoint {V : Type*} [LT V] [Fintype V] (G : Forest V)
    {v w : V} (hv : ¬Anc G v w) (hw : ¬Anc G w v) :
    Disjoint (descendants G v) (descendants G w) := by
  apply Finset.disjoint_left.mpr
  intro u huv huw
  rcases ancestors_comparable G (Finset.mem_filter.mp huv).2
    (Finset.mem_filter.mp huw).2 with h | h
  · exact hv h
  · exact hw h

theorem disjoint_size_bound {V : Type*} [LT V] [Fintype V] (G : Forest V)
    {v w : V} (h : Disjoint (descendants G v) (descendants G w)) :
    size G v + size G w ≤ Fintype.card V := by
  rw [size_eq_card_filter,size_eq_card_filter]
  change (descendants G v).card + (descendants G w).card ≤ _
  rw [← Finset.card_union_of_disjoint h]
  exact le_trans (Finset.card_le_card (Finset.subset_univ _)) (by simp)

theorem large_subtrees_comparable {V : Type*} [LT V] [Fintype V]
    (G : Forest V) (q : ℕ) (hn : Fintype.card V ≤ 2*q+1)
    {v w : V} (hv : q < size G v) (hw : q < size G w) :
    Anc G v w ∨ Anc G w v := by
  by_contra hh
  push Not at hh
  have hc := disjoint_size_bound G (descendants_disjoint G hh.1 hh.2)
  omega

def skeletonLeaves {V : Type*} [LT V] [Fintype V] (G : Forest V) (q : ℕ) : Finset V :=
  Finset.univ.filter (fun v => q < size G v ∧ ∀w, q < size G w → ¬Edge G w v)

theorem leaf_not_ancestor {V : Type*} [LT V] [Fintype V] (G : Forest V)
    (q : ℕ) {v w : V} (hv : v ∈ skeletonLeaves G q)
    (hw : w ∈ skeletonLeaves G q) (hne : v ≠ w) : ¬Anc G v w := by
  intro h
  have hvq := (Finset.mem_filter.mp hv).2.1
  have hwleaf := (Finset.mem_filter.mp hw).2.2
  cases h with
  | refl => exact hne rfl
  | @tail z w h e =>
    exact hwleaf z (lt_of_lt_of_le hvq (size_mono_ancestor G h)) e

theorem skeletonLeaves_card_le_one {V : Type*} [LT V] [Fintype V]
    (G : Forest V) (q : ℕ) (hn : Fintype.card V ≤ 2*q+1) :
    (skeletonLeaves G q).card ≤ 1 := by
  apply Finset.card_le_one.mpr
  intro v hv w hw
  by_contra hne
  have h := large_subtrees_comparable G q hn
    (Finset.mem_filter.mp hv).2.1 (Finset.mem_filter.mp hw).2.1
  exact h.elim (leaf_not_ancestor G q hv hw hne) (leaf_not_ancestor G q hw hv (Ne.symm hne))

theorem skeletonLeaves_empty_iff {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) (q : ℕ) : skeletonLeaves G q = ∅ ↔ ∀v, size G v ≤ q := by
  constructor
  · intro hempty v
    by_contra hn
    have hv : q < size G v := by omega
    let S := Finset.univ.filter (fun u => q < size G u)
    have hs : S.Nonempty := ⟨v,by simp [S,hv]⟩
    let z := S.min' hs
    have hz : z ∈ S := S.min'_mem hs
    have hleaf : z ∈ skeletonLeaves G q := by
      apply Finset.mem_filter.mpr
      refine ⟨Finset.mem_univ _,(Finset.mem_filter.mp hz).2,?_⟩
      intro w hw he
      have hws : w ∈ S := by simp [S,hw]
      have hmin : z ≤ w := S.min'_le _ hws
      exact (not_lt_of_ge hmin (G.property _ _ he))
    rw [hempty] at hleaf
    exact Finset.notMem_empty _ hleaf
  · intro h
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro v hv
    exact (not_lt_of_ge (h v)) (Finset.mem_filter.mp hv).2.1

theorem size_lt_parent {V : Type*} [LinearOrder V] [Fintype V] (G : Forest V)
    {v w : V} (he : Edge G v w) : size G v < size G w := by
  have hw : w ∉ descendants G v := by
    intro hm
    have hle := anc_le G (Finset.mem_filter.mp hm).2
    exact (not_lt_of_ge hle (G.property _ _ he))
  have hsub : insert w (descendants G v) ⊆ descendants G w := by
    intro u hu
    rcases Finset.mem_insert.mp hu with hu | hu
    · subst u
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _,anc_refl G w⟩
    · exact Finset.mem_filter.mpr ⟨Finset.mem_univ _,
        (Finset.mem_filter.mp hu).2.tail he⟩
  have hc := Finset.card_le_card hsub
  rw [Finset.card_insert_of_notMem hw] at hc
  have hc' : size G v + 1 ≤ size G w := by
    simpa only [descendants,← size_eq_card_filter] using hc
  omega

theorem empty_threshold_vertex_root {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) (q : ℕ) (h : skeletonLeaves G q = ∅)
    (v : V) (hv : size G v = q) : parent G v = none := by
  have hall := (skeletonLeaves_empty_iff G q).mp h
  cases hp : parent G v with
  | none => rfl
  | some w =>
    have hs := size_lt_parent G hp
    have ht := hall w
    omega

def canonicalSkeletonLeaves {n : ℕ} (P : ParentForest n) (q : ℕ) : Finset (Fin n) :=
  Finset.univ.filter (fun v => q < subtreeSize P v ∧
    ∀w, q < subtreeSize P w → P.val w.succ ≠ v.succ)

def canonicalLeafCount {n : ℕ} (P : ParentForest n) (q : ℕ) : ℕ :=
  (canonicalSkeletonLeaves P q).card

theorem encode_parent_eq {n : ℕ} (G : Forest (Fin n)) (w v : Fin n) :
    (encode G).val w.succ = v.succ ↔ Edge G w v := by
  change optionFin n (parent G w) = optionFin n (some v) ↔ parent G w = some v
  exact (optionFin n).injective.eq_iff

theorem canonicalLeaves_encode {n : ℕ} (G : Forest (Fin n)) (q : ℕ) :
    canonicalSkeletonLeaves (encode G) q = skeletonLeaves G q := by
  ext v
  simp only [canonicalSkeletonLeaves,skeletonLeaves,Finset.mem_filter,Finset.mem_univ,
    true_and,subtreeSize_encode,ne_eq,encode_parent_eq]

theorem canonicalLeafCount_le_one {n : ℕ} (P : ParentForest n) (q : ℕ)
    (hn : n ≤ 2*q+1) : canonicalLeafCount P q ≤ 1 := by
  obtain ⟨G,rfl⟩ := (parentEquiv n).surjective P
  change canonicalLeafCount (encode G) q ≤ 1
  rw [canonicalLeafCount,canonicalLeaves_encode]
  exact skeletonLeaves_card_le_one G q (by simpa using hn)

theorem canonicalLeafCount_zero_iff {n : ℕ} (P : ParentForest n) (q : ℕ) :
    canonicalLeafCount P q = 0 ↔ ∀v, subtreeSize P v ≤ q := by
  obtain ⟨G,rfl⟩ := (parentEquiv n).surjective P
  change canonicalLeafCount (encode G) q = 0 ↔ ∀v, subtreeSize (encode G) v ≤ q
  simp only [canonicalLeafCount,canonicalLeaves_encode,Finset.card_eq_zero,
    skeletonLeaves_empty_iff,subtreeSize_encode]

/-- Exactly the three products in the canonical definition of D^(k). -/
def forestCurvature {n : ℕ} (P : ParentForest n) (l : ℕ+) : ℤ :=
  (∏v : Fin n, min (subtreeSize P v) (l.val+2) : ℕ) -
  2*(∏v : Fin n, min (subtreeSize P v) (l.val+1) : ℕ) +
  (∏v : Fin n, min (subtreeSize P v) l.val : ℕ)

def canonicalClassContribution (n l : ℕ+) (k : ℕ) : ℤ :=
  ∑ P : ParentForest n.val,
    if canonicalLeafCount P (l.val+1) = k then forestCurvature P l else 0

theorem sum_forestCurvature_original (n l : ℕ+) :
    (∑ P : ParentForest n.val, forestCurvature P l) = delta n l := by
  rw [delta,ParkingLastCar.b_curvature n l.val l.pos]
  have he : l.val-1+1 = l.val := by have := l.pos; omega
  simp only [forestCurvature,Finset.sum_add_distrib,Finset.sum_sub_distrib,
    ← Finset.mul_sum,← Nat.cast_sum]
  rw [← original_A_parent_sum n.val (l.val+1),
    ← original_A_parent_sum n.val l.val]
  have ha := original_A_parent_sum n.val (l.val-1)
  rw [he] at ha
  rw [← ha]

theorem original_delta_empty_path (n l : ℕ+) (hn : n.val ≤ 2*(l.val+1)+1) :
    delta n l = canonicalClassContribution n l 0 + canonicalClassContribution n l 1 := by
  rw [← sum_forestCurvature_original,canonicalClassContribution,canonicalClassContribution,
    ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro P _
  have h := canonicalLeafCount_le_one P (l.val+1) hn
  have hh : canonicalLeafCount P (l.val+1) = 0 ∨ canonicalLeafCount P (l.val+1) = 1 := by omega
  rcases hh with hh | hh <;> simp [hh]

end ParkingForest
