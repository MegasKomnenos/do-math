import Assembly

namespace ParkingLastCar
open Parking
noncomputable section

theorem left_slot_bound {n l : ℕ} (x : Trace (n+1) l) (i : Fin (leftSet x).card) :
    (x.val.2 (index (leftSet x) i)).val < (leftSet x).card := by
  have hb := (mem_leftSet x _).mp (index_mem (leftSet x) i)
  change (x.val.2 (index (leftSet x) i)).val < (x.val.2 (Fin.last n)).val at hb
  have hc := leftSet_card x
  omega

theorem right_slot_bound {n l : ℕ} (x : Trace (n+1) l) (i : Fin (leftSet x)ᶜ.card) :
    (leftSet x).card < (x.val.2 (index (leftSet x)ᶜ i)).val := by
  rw [leftSet_card]
  have hn := Finset.mem_compl.mp (index_mem (leftSet x)ᶜ i)
  have hnot : ¬ x.val.2 (index (leftSet x)ᶜ i) < x.val.2 (Fin.last n) :=
    fun h => hn ((mem_leftSet x _).mpr h)
  have hne : x.val.2 (index (leftSet x)ᶜ i) ≠ x.val.2 (Fin.last n) := by
    intro he
    have hi := x.property.1.1 he
    exact (ne_of_lt (index_lt_last _ _)) hi
  have hh : x.val.2 (Fin.last n) < x.val.2 (index (leftSet x)ᶜ i) :=
    lt_of_le_of_ne (le_of_not_gt hnot) (Ne.symm hne)
  exact hh

theorem right_pref_bound {n l : ℕ} (x : Trace (n+1) l) (i : Fin (leftSet x)ᶜ.card) :
    (leftSet x).card < (x.val.1 (index (leftSet x)ᶜ i)).val := by
  rw [leftSet_card]
  exact last_barrier x.property.1 _ (by
    change (x.val.2 (Fin.last n)).val < (x.val.2 (index (leftSet x)ᶜ i)).val
    rw [← leftSet_card]
    exact right_slot_bound x i)

def extractLeftA {n l : ℕ} (x : Trace (n+1) l) : Pref (leftSet x).card := fun i =>
  ⟨(x.val.1 (index (leftSet x) i)).val, by
    have hle := x.property.1.2.2.1 (index (leftSet x) i)
    exact lt_of_le_of_lt hle (left_slot_bound x i)⟩

def extractLeftP {n l : ℕ} (x : Trace (n+1) l) : Pref (leftSet x).card := fun i =>
  ⟨(x.val.2 (index (leftSet x) i)).val, left_slot_bound x i⟩

def extractRightA {n l : ℕ} (x : Trace (n+1) l) : Pref (leftSet x)ᶜ.card := fun i =>
  ⟨(x.val.1 (index (leftSet x)ᶜ i)).val - ((leftSet x).card+1), by
    have hlow := right_pref_bound x i
    have hhigh := (x.val.1 (index (leftSet x)ᶜ i)).isLt
    have hsum := card_partition (leftSet x)
    omega⟩

def extractRightP {n l : ℕ} (x : Trace (n+1) l) : Pref (leftSet x)ᶜ.card := fun i =>
  ⟨(x.val.2 (index (leftSet x)ᶜ i)).val - ((leftSet x).card+1), by
    have hlow := right_slot_bound x i
    have hhigh := (x.val.2 (index (leftSet x)ᶜ i)).isLt
    have hsum := card_partition (leftSet x)
    omega⟩

theorem left_closed {n l : ℕ} (x : Trace (n+1) l) (j : Fin (n+1))
    (hj : (x.val.2 j).val < (leftSet x).card) :
    ∃ i, index (leftSet x) i = j := by
  rcases Fin.eq_castSucc_or_eq_last j with ⟨j, rfl⟩ | rfl
  · apply (index_range _ _).mpr
    apply (mem_leftSet x j).mpr
    simpa [leftSet_card] using hj
  · rw [leftSet_card] at hj
    omega

theorem right_closed {n l : ℕ} (x : Trace (n+1) l) (j : Fin (n+1))
    (hj : (leftSet x).card+1 ≤ (x.val.2 j).val) :
    ∃ i, index (leftSet x)ᶜ i = j := by
  rcases Fin.eq_castSucc_or_eq_last j with ⟨j, rfl⟩ | rfl
  · apply (index_range _ _).mpr
    apply Finset.mem_compl.mpr
    intro hm
    have hh := (mem_leftSet x j).mp hm
    change (x.val.2 j.castSucc).val < (x.val.2 (Fin.last n)).val at hh
    have hc := leftSet_card x
    omega
  · rw [leftSet_card] at hj
    omega

def extractLeft {n l : ℕ} (x : Trace (n+1) l) : Trace (leftSet x).card l := by
  refine ⟨(extractLeftA x, extractLeftP x), ?_, ?_⟩
  · apply certified_restrict x.property.1 (index (leftSet x)) _ _ (c := 0)
    · have := card_partition (leftSet x); omega
    · intro i; simp [extractLeftA]
    · intro i; simp [extractLeftP]
    · intro j _ hj; exact left_closed x j (by simpa using hj)
  · intro i
    exact x.property.2 (index (leftSet x) i)

def extractRight {n l : ℕ} (x : Trace (n+1) l) : Trace (leftSet x)ᶜ.card l := by
  refine ⟨(extractRightA x, extractRightP x), ?_, ?_⟩
  · apply certified_restrict x.property.1 (index (leftSet x)ᶜ) _ _ (c := (leftSet x).card+1)
    · have := card_partition (leftSet x); omega
    · intro i
      simp only [extractRightA]
      have := right_pref_bound x i
      omega
    · intro i
      simp only [extractRightP]
      have := right_slot_bound x i
      omega
    · intro j hj _; exact right_closed x j hj
  · intro i
    have h := x.property.2 (index (leftSet x)ᶜ i)
    have hlow := right_pref_bound x i
    have hhigh := right_slot_bound x i
    change (x.val.2 (index (leftSet x)ᶜ i)).val - ((leftSet x).card+1) -
      ((x.val.1 (index (leftSet x)ᶜ i)).val - ((leftSet x).card+1)) ≤ l
    omega

def extractT {n l : ℕ} (x : Trace (n+1) l) : Fin (min ((leftSet x).card+1) (l+1)) :=
  ⟨(x.val.2 (Fin.last n)).val-(x.val.1 (Fin.last n)).val, by
    apply lt_min_iff.mpr
    have hc := leftSet_card x
    have hb := x.property.2 (Fin.last n)
    constructor <;> omega⟩

def extract {n l : ℕ} (x : Trace (n+1) l) : Pieces n l :=
  ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩

theorem assemble_extract {n l : ℕ} (x : Trace (n+1) l) : assemble (extract x) = x := by
  apply Subtype.ext
  apply Prod.ext
  · funext i
    rcases index_cases (leftSet x) i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.1 _ = _
      rw [assemble_last_a]
      apply Fin.ext
      change (leftSet x).card - ((x.val.2 (Fin.last n)).val-(x.val.1 (Fin.last n)).val) = _
      have hc := leftSet_card x
      have hle := x.property.1.2.2.1 (Fin.last n)
      change (x.val.1 (Fin.last n)).val ≤ (x.val.2 (Fin.last n)).val at hle
      omega
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.1 _ = _
      rw [assemble_left_a]
      rfl
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.1 _ = _
      rw [assemble_right_a]
      apply Fin.ext
      change (leftSet x).card+1+((x.val.1 (index (leftSet x)ᶜ i)).val-((leftSet x).card+1)) = _
      have := right_pref_bound x i
      omega
  · funext i
    rcases index_cases (leftSet x) i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.2 _ = _
      rw [assemble_last_p]
      exact Fin.ext (leftSet_card x)
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.2 _ = _
      rw [assemble_left_p]
      rfl
    · change (assemble ⟨leftSet x, extractT x, extractLeft x, extractRight x⟩).val.2 _ = _
      rw [assemble_right_p]
      apply Fin.ext
      change (leftSet x).card+1+((x.val.2 (index (leftSet x)ᶜ i)).val-((leftSet x).card+1)) = _
      have := right_slot_bound x i
      omega

#print axioms left_slot_bound
#print axioms right_slot_bound
#print axioms right_pref_bound
#print axioms left_closed
#print axioms right_closed
#print axioms extractLeft
#print axioms extractRight
#print axioms extractT
#print axioms extract
#print axioms assemble_extract
end
end ParkingLastCar
