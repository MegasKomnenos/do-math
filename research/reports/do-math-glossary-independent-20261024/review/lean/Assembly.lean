import LastCar

namespace ParkingLastCar
open Parking
noncomputable section

theorem paste_injective {n : ℕ} (I : Finset (Fin n))
    (p : Pref I.card) (q : Pref Iᶜ.card)
    (hp : Function.Injective p) (hq : Function.Injective q) :
    Function.Injective (paste I p q (rootSlot I)) := by
  intro i j he
  rcases index_cases I i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩ <;>
    rcases index_cases I j with rfl | ⟨j, rfl⟩ | ⟨j, rfl⟩ <;>
    simp only [paste_last, paste_left, paste_right] at he
  · rfl
  · have hv := congrArg Fin.val he
    have hb := (p j).isLt
    simp only [rootSlot, leftLift] at hv
    omega
  · have hv := congrArg Fin.val he
    simp only [rootSlot, rightLift] at hv
    omega
  · have hv := congrArg Fin.val he
    have hb := (p i).isLt
    simp only [rootSlot, leftLift] at hv
    omega
  · congr 1
    apply hp
    apply Fin.ext
    exact congrArg (fun u : Fin (n+1) => u.val) he
  · have hv := congrArg Fin.val he
    have hb := (p i).isLt
    simp only [leftLift, rightLift] at hv
    omega
  · have hv := congrArg Fin.val he
    simp only [rootSlot, rightLift] at hv
    omega
  · have hv := congrArg Fin.val he
    have hb := (p j).isLt
    simp only [leftLift, rightLift] at hv
    omega
  · congr 1
    apply hq
    apply Fin.ext
    have hv := congrArg Fin.val he
    simp only [rightLift] at hv
    omega

theorem paste_certified {n : ℕ} (I : Finset (Fin n))
    (a p : Pref I.card) (b q : Pref Iᶜ.card)
    (ha : Certified ∅ a p) (hb : Certified ∅ b q)
    (z : Fin (n+1)) (hz : z ≤ rootSlot I) :
    Certified ∅ (paste I a b z) (paste I p q (rootSlot I)) := by
  have hinj := paste_injective I p q ha.1 hb.1
  refine ⟨hinj, by simp, ?_, ?_⟩
  · intro i
    rcases index_cases I i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩
    · simpa using hz
    · simp only [paste_left]
      exact ha.2.2.1 i
    · simp only [paste_right]
      change I.card+1+(b i).val ≤ I.card+1+(q i).val
      exact Nat.add_le_add_left (hb.2.2.1 i) _
  · intro i s has hsp
    rcases index_cases I i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩
    · obtain ⟨j, hj⟩ := Finite.surjective_of_injective hinj s
      right
      refine ⟨j, ?_, hj⟩
      rw [paste_last] at hsp
      have hs : s.val < I.card := hsp
      have hne : j ≠ Fin.last n := by
        intro he
        subst j
        have he' := congrArg Fin.val hj
        simp only [paste_last, rootSlot] at he'
        omega
      have hjb := j.isLt
      have hn : j.val ≠ n := fun hh => hne (Fin.ext hh)
      change j.val < n
      omega
    · simp only [paste_left] at has hsp
      have hs : s.val < I.card := lt_trans hsp (p i).isLt
      let s' : Fin I.card := ⟨s.val, hs⟩
      rcases ha.2.2.2 i s' has hsp with hh | ⟨j, hj, hpj⟩
      · simpa using hh
      · refine Or.inr ⟨index I j, (index I).strictMono hj, ?_⟩
        simp only [paste_left, hpj]
        rfl
    · simp only [paste_right] at has hsp
      have hslow : I.card+1 ≤ s.val := by
        change I.card+1+(b i).val ≤ s.val at has
        omega
      have hsup : s.val < I.card+1+Iᶜ.card := by
        have := (q i).isLt
        change s.val < I.card+1+(q i).val at hsp
        omega
      let s' : Fin Iᶜ.card := ⟨s.val-(I.card+1), by omega⟩
      have hs'a : b i ≤ s' := by
        change I.card+1+(b i).val ≤ s.val at has
        change (b i).val ≤ s.val-(I.card+1)
        omega
      have hs'p : s' < q i := by
        change s.val < I.card+1+(q i).val at hsp
        change s.val-(I.card+1) < (q i).val
        omega
      rcases hb.2.2.2 i s' hs'a hs'p with hh | ⟨j, hj, hpj⟩
      · simpa using hh
      · refine Or.inr ⟨index Iᶜ j, (index Iᶜ).strictMono hj, ?_⟩
        simp only [paste_right, hpj]
        apply Fin.ext
        change I.card+1+(s.val-(I.card+1)) = s.val
        omega

def lastPref {n l : ℕ} (I : Finset (Fin n)) (t : Fin (min (I.card+1) (l+1))) : Fin (n+1) :=
  ⟨I.card-t.val, by have := card_partition I; omega⟩

abbrev Pieces (n l : ℕ) :=
  Σ I : Finset (Fin n), Fin (min (I.card+1) (l+1)) × Trace I.card l × Trace Iᶜ.card l

def assemble {n l : ℕ} (d : Pieces n l) : Trace (n+1) l := by
  rcases d with ⟨I, t, a, b⟩
  refine ⟨(paste I a.val.1 b.val.1 (lastPref I t),
    paste I a.val.2 b.val.2 (rootSlot I)), ?_, ?_⟩
  · apply paste_certified I _ _ _ _ a.property.1 b.property.1
    change I.card-t.val ≤ I.card
    omega
  · intro i
    rcases index_cases I i with rfl | ⟨i, rfl⟩ | ⟨i, rfl⟩
    · simp only [paste_last, rootSlot, lastPref]
      have := t.isLt
      have ht := lt_min_iff.mp this
      omega
    · simpa only [paste_left, leftLift] using a.property.2 i
    · simpa only [paste_right, rightLift, Nat.add_sub_add_left] using b.property.2 i

@[simp] theorem assemble_left_a {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin I.card) :
    (assemble ⟨I,t,a,b⟩).val.1 (index I i) = leftLift I (a.val.1 i) := paste_left _ _ _ _ _
@[simp] theorem assemble_left_p {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin I.card) :
    (assemble ⟨I,t,a,b⟩).val.2 (index I i) = leftLift I (a.val.2 i) := paste_left _ _ _ _ _
@[simp] theorem assemble_right_a {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin Iᶜ.card) :
    (assemble ⟨I,t,a,b⟩).val.1 (index Iᶜ i) = rightLift I (b.val.1 i) := paste_right _ _ _ _ _
@[simp] theorem assemble_right_p {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin Iᶜ.card) :
    (assemble ⟨I,t,a,b⟩).val.2 (index Iᶜ i) = rightLift I (b.val.2 i) := paste_right _ _ _ _ _
@[simp] theorem assemble_last_a {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) :
    (assemble ⟨I,t,a,b⟩).val.1 (Fin.last n) = lastPref I t := paste_last _ _ _ _
@[simp] theorem assemble_last_p {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) :
    (assemble ⟨I,t,a,b⟩).val.2 (Fin.last n) = rootSlot I := paste_last _ _ _ _

theorem assemble_displacement_left {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin I.card) :
    ((assemble ⟨I,t,a,b⟩).val.2 (index I i)).val -
      ((assemble ⟨I,t,a,b⟩).val.1 (index I i)).val = (a.val.2 i).val-(a.val.1 i).val := by
  simp only [assemble_left_p, assemble_left_a, leftLift]

theorem assemble_displacement_right {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) (i : Fin Iᶜ.card) :
    ((assemble ⟨I,t,a,b⟩).val.2 (index Iᶜ i)).val -
      ((assemble ⟨I,t,a,b⟩).val.1 (index Iᶜ i)).val = (b.val.2 i).val-(b.val.1 i).val := by
  simp only [assemble_right_p, assemble_right_a, rightLift, Nat.add_sub_add_left]

theorem assemble_displacement_last {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) :
    ((assemble ⟨I,t,a,b⟩).val.2 (Fin.last n)).val -
      ((assemble ⟨I,t,a,b⟩).val.1 (Fin.last n)).val = t.val := by
  simp only [assemble_last_p, assemble_last_a, rootSlot, lastPref]
  have := (lt_min_iff.mp t.isLt).1
  omega

theorem assemble_success {n l : ℕ} (d : Pieces n l) :
    park (assemble d).val.1 = some (List.ofFn (assemble d).val.2) :=
  certified_run ∅ _ _ (assemble d).property.1

#print axioms paste_injective
#print axioms paste_certified
#print axioms assemble
#print axioms assemble_left_a
#print axioms assemble_left_p
#print axioms assemble_right_a
#print axioms assemble_right_p
#print axioms assemble_last_a
#print axioms assemble_last_p
#print axioms assemble_displacement_left
#print axioms assemble_displacement_right
#print axioms assemble_displacement_last
#print axioms assemble_success
end
end ParkingLastCar
