import Certificates

namespace ParkingLastCar
open Parking
noncomputable section

theorem certified_restrict {N k c : ℕ} {a p : Fin N → Fin N}
    (h : Certified ∅ a p) (e : Fin k ↪o Fin N) (a' p' : Fin k → Fin k)
    (hbound : c + k ≤ N)
    (ha : ∀ i, (a (e i)).val = c + (a' i).val)
    (hp : ∀ i, (p (e i)).val = c + (p' i).val)
    (hclosed : ∀ j, c ≤ (p j).val → (p j).val < c + k → ∃ i, e i = j) :
    Certified ∅ a' p' := by
  rcases h with ⟨hinj, hfree, hle, hcover⟩
  refine ⟨?_, by simp, ?_, ?_⟩
  · intro i j hij
    apply e.injective
    apply hinj
    apply Fin.ext
    rw [hp, hp, hij]
  · intro i
    have hi := hle (e i)
    have hai := ha i
    have hpi := hp i
    change (a' i).val ≤ (p' i).val
    change (a (e i)).val ≤ (p (e i)).val at hi
    omega
  · intro i s has hsp
    let sN : Fin N := ⟨c+s.val, by have := s.isLt; omega⟩
    have hsa : a (e i) ≤ sN := by
      change (a (e i)).val ≤ c+s.val
      rw [ha]
      exact Nat.add_le_add_left has c
    have hps : sN < p (e i) := by
      change c+s.val < (p (e i)).val
      rw [hp]
      exact Nat.add_lt_add_left hsp c
    rcases hcover (e i) sN hsa hps with hh | ⟨j, hj, hpj⟩
    · simpa using hh
    · have hpjv : (p j).val = c+s.val := congrArg Fin.val hpj
      obtain ⟨j', hj'⟩ := hclosed j (by omega) (by have := s.isLt; omega)
      refine Or.inr ⟨j', e.lt_iff_lt.mp (hj' ▸ hj), ?_⟩
      apply Fin.ext
      have hval := hp j'
      rw [hj'] at hval
      omega

theorem last_barrier {n : ℕ} {a p : Pref (n+1)} (h : Certified ∅ a p)
    (i : Fin n) (hp : p (Fin.last n) < p i.castSucc) :
    p (Fin.last n) < a i.castSucc := by
  by_contra ha
  have hle : a i.castSucc ≤ p (Fin.last n) := le_of_not_gt ha
  rcases h.2.2.2 i.castSucc (p (Fin.last n)) hle hp with hz | ⟨j, hj, hpj⟩
  · simpa using hz
  · have he : j = Fin.last n := h.1 hpj
    subst j
    exact (not_lt_of_ge (Fin.le_last _)) hj

def leftSet {n l : ℕ} (x : Trace (n+1) l) : Finset (Fin n) :=
  Finset.univ.filter fun i => x.val.2 i.castSucc < x.val.2 (Fin.last n)

theorem mem_leftSet {n l : ℕ} (x : Trace (n+1) l) (i : Fin n) :
    i ∈ leftSet x ↔ x.val.2 i.castSucc < x.val.2 (Fin.last n) := by simp [leftSet]

theorem leftSet_card {n l : ℕ} (x : Trace (n+1) l) :
    (leftSet x).card = (x.val.2 (Fin.last n)).val := by
  let k := (x.val.2 (Fin.last n)).val
  let f : leftSet x → Fin k := fun i =>
    ⟨(x.val.2 i.val.castSucc).val, (mem_leftSet x i.val).mp i.property⟩
  have hf : Function.Bijective f := by
    constructor
    · intro i j he
      apply Subtype.ext
      apply Fin.castSucc_injective
      apply x.property.1.1
      apply Fin.ext
      exact congrArg (fun u : Fin k => u.val) he
    · intro s
      have hsurj := Finite.surjective_of_injective x.property.1.1
      let sN : Fin (n+1) := ⟨s.val, by have := s.isLt; have := (x.val.2 (Fin.last n)).isLt; omega⟩
      obtain ⟨j, hj⟩ := hsurj sN
      rcases Fin.eq_castSucc_or_eq_last j with ⟨i, rfl⟩ | rfl
      · have hi : i ∈ leftSet x := by
          apply (mem_leftSet x i).mpr
          change (x.val.2 i.castSucc).val < k
          rw [hj]
          exact s.isLt
        refine ⟨⟨i, hi⟩, ?_⟩
        apply Fin.ext
        exact congrArg (fun u : Fin (n+1) => u.val) hj
      · have he := congrArg Fin.val hj
        have := s.isLt
        change (x.val.2 (Fin.last n)).val = s.val at he
        change s.val < (x.val.2 (Fin.last n)).val at this
        omega
  have hh := Fintype.card_congr (Equiv.ofBijective f hf)
  simpa using hh

/-- Increasing enumeration of the selected arrival labels, before the last car. -/
def index {n : ℕ} (I : Finset (Fin n)) : Fin I.card ↪o Fin (n+1) where
  toFun i := ((I.orderIsoOfFin rfl i).val).castSucc
  inj' := fun _ _ h => (I.orderIsoOfFin rfl).injective
    (Subtype.ext ((Fin.castSucc_injective n) h))
  map_rel_iff' := by intro i j; simp

theorem index_mem {n : ℕ} (I : Finset (Fin n)) (i : Fin I.card) :
    I.orderEmbOfFin rfl i ∈ I := I.orderEmbOfFin_mem rfl i

theorem index_range {n : ℕ} (I : Finset (Fin n)) (i : Fin n) :
    (∃ j, index I j = i.castSucc) ↔ i ∈ I := by
  constructor
  · rintro ⟨j, hj⟩
    have he : I.orderEmbOfFin rfl j = i := (Fin.castSucc_injective n) hj
    simpa [he] using index_mem I j
  · intro hi
    refine ⟨(I.orderIsoOfFin rfl).symm ⟨i, hi⟩, ?_⟩
    change ((I.orderIsoOfFin rfl) ((I.orderIsoOfFin rfl).symm ⟨i, hi⟩)).val.castSucc = i.castSucc
    simp

theorem index_cases {n : ℕ} (I : Finset (Fin n)) (i : Fin (n+1)) :
    i = Fin.last n ∨ (∃ j, index I j = i) ∨ ∃ j, index Iᶜ j = i := by
  rcases Fin.eq_castSucc_or_eq_last i with ⟨j, rfl⟩ | rfl
  · by_cases hj : j ∈ I
    · exact Or.inr (Or.inl ((index_range I j).mpr hj))
    · exact Or.inr (Or.inr ((index_range Iᶜ j).mpr (Finset.mem_compl.mpr hj)))
  · exact Or.inl rfl

theorem index_lt_last {n : ℕ} (I : Finset (Fin n)) (i : Fin I.card) :
    index I i < Fin.last n := by
  exact Fin.castSucc_lt_last _

theorem index_disjoint {n : ℕ} (I : Finset (Fin n)) (i : Fin I.card) (j : Fin Iᶜ.card) :
    index I i ≠ index Iᶜ j := by
  intro he
  have he' : I.orderEmbOfFin rfl i = Iᶜ.orderEmbOfFin rfl j := (Fin.castSucc_injective n) he
  have h1 := index_mem I i
  have h2 := index_mem Iᶜ j
  rw [← he'] at h2
  exact (Finset.mem_compl.mp h2) h1

theorem card_partition {n : ℕ} (I : Finset (Fin n)) : I.card + Iᶜ.card = n := by
  simpa using Finset.card_add_card_compl I

def leftLift {n : ℕ} (I : Finset (Fin n)) (s : Fin I.card) : Fin (n+1) :=
  ⟨s.val, by have := card_partition I; have := s.isLt; omega⟩

def rightLift {n : ℕ} (I : Finset (Fin n)) (s : Fin Iᶜ.card) : Fin (n+1) :=
  ⟨I.card+1+s.val, by have := card_partition I; have := s.isLt; omega⟩

def rootSlot {n : ℕ} (I : Finset (Fin n)) : Fin (n+1) :=
  ⟨I.card, by have := card_partition I; omega⟩

/-- Paste two functions in their original arrival order, with a final value. -/
def paste {n : ℕ} (I : Finset (Fin n))
    (f : Fin I.card → Fin I.card) (g : Fin Iᶜ.card → Fin Iᶜ.card)
    (z : Fin (n+1)) : Pref (n+1) :=
  Fin.lastCases z (fun i => if hi : i ∈ I then
    leftLift I (f ((I.orderIsoOfFin rfl).symm ⟨i, hi⟩)) else
    rightLift I (g ((Iᶜ.orderIsoOfFin rfl).symm ⟨i, Finset.mem_compl.mpr hi⟩)))

@[simp] theorem paste_last {n : ℕ} (I : Finset (Fin n)) (f g) (z : Fin (n+1)) :
    paste I f g z (Fin.last n) = z := by simp [paste]

@[simp] theorem paste_left {n : ℕ} (I : Finset (Fin n)) (f g) (z : Fin (n+1)) (i : Fin I.card) :
    paste I f g z (index I i) = leftLift I (f i) := by
  unfold paste
  change Fin.lastCases (motive := fun _ => Fin (n+1)) z _ ((I.orderIsoOfFin rfl i).val.castSucc) = _
  simp only [Fin.lastCases_castSucc]
  rw [dif_pos (I.orderIsoOfFin rfl i).property]
  change leftLift I (f ((I.orderIsoOfFin rfl).symm (I.orderIsoOfFin rfl i))) = _
  rw [OrderIso.symm_apply_apply]

@[simp] theorem paste_right {n : ℕ} (I : Finset (Fin n)) (f g) (z : Fin (n+1)) (i : Fin Iᶜ.card) :
    paste I f g z (index Iᶜ i) = rightLift I (g i) := by
  unfold paste
  change Fin.lastCases (motive := fun _ => Fin (n+1)) z _ ((Iᶜ.orderIsoOfFin rfl i).val.castSucc) = _
  simp only [Fin.lastCases_castSucc]
  rw [dif_neg (Finset.mem_compl.mp (Iᶜ.orderIsoOfFin rfl i).property)]
  change rightLift I (g ((Iᶜ.orderIsoOfFin rfl).symm (Iᶜ.orderIsoOfFin rfl i))) = _
  rw [OrderIso.symm_apply_apply]

#print axioms certified_restrict
#print axioms last_barrier
#print axioms mem_leftSet
#print axioms leftSet_card
#print axioms index_mem
#print axioms index_range
#print axioms index_cases
#print axioms index_lt_last
#print axioms index_disjoint
#print axioms card_partition
#print axioms paste_last
#print axioms paste_left
#print axioms paste_right
end
end ParkingLastCar
