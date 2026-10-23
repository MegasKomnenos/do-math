import ForestEvaluation

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
namespace ParkingForest

/-- Exactly the parent functions on {0,...,n}, with virtual root 0. -/
def ParentForest (n : ℕ) := {p : Fin (n+1) → Fin (n+1) //
  p 0 = 0 ∧ ∀v, v ≠ 0 → p v = 0 ∨ v < p v}

instance (n : ℕ) : Fintype (ParentForest n) := by unfold ParentForest; infer_instance

def optionFin (n : ℕ) : Option (Fin n) ≃ Fin (n+1) where
  toFun := fun u => match u with | none => 0 | some v => v.succ
  invFun := Fin.cases none some
  left_inv u := by cases u <;> simp
  right_inv u := by refine Fin.cases ?_ (fun i => ?_) u <;> simp

@[simp] theorem optionFin_none (n : ℕ) : optionFin n none = 0 := rfl
@[simp] theorem optionFin_some (n : ℕ) (u : Fin n) : optionFin n (some u) = u.succ := rfl
@[simp] theorem optionFin_symm_zero (n : ℕ) : (optionFin n).symm 0 = none := rfl
@[simp] theorem optionFin_symm_succ (n : ℕ) (u : Fin n) :
    (optionFin n).symm u.succ = some u := by simp [optionFin]

def encode {n : ℕ} (G : Forest (Fin n)) : ParentForest n := by
  refine ⟨fun v => optionFin n (up G ((optionFin n).symm v)), ?_, ?_⟩
  · rfl
  · intro v
    refine Fin.cases ?_ (fun u hu => ?_) v
    · simp
    · change optionFin n (parent G u) = 0 ∨ u.succ < optionFin n (parent G u)
      cases hp : parent G u with
      | none => exact Or.inl rfl
      | some z => exact Or.inr (Fin.succ_lt_succ_iff.mpr (G.property _ _ hp))

def decode {n : ℕ} (P : ParentForest n) : Forest (Fin n) := by
  refine ⟨fun u => (optionFin n).symm (P.val u.succ), ?_⟩
  intro u v h
  have hp : P.val u.succ = v.succ := by
    have hh := congrArg (optionFin n) h
    simpa using hh
  rcases P.property.2 u.succ (by simp) with hz | hlt
  · rw [hp] at hz
    exact (Fin.succ_ne_zero v hz).elim
  · rw [hp] at hlt
    exact Fin.succ_lt_succ_iff.mp hlt

def parentEquiv (n : ℕ) : Forest (Fin n) ≃ ParentForest n where
  toFun := encode
  invFun := decode
  left_inv G := by
    apply Subtype.ext
    funext u
    change (optionFin n).symm (optionFin n (up G ((optionFin n).symm u.succ))) = parent G u
    simp [up]
  right_inv P := by
    apply Subtype.ext
    funext u
    refine Fin.cases ?_ (fun i => ?_) u
    · exact P.property.1.symm
    · change optionFin n ((optionFin n).symm (P.val i.succ)) = P.val i.succ
      exact (optionFin n).apply_symm_apply _

theorem encode_iterate {n : ℕ} (G : Forest (Fin n)) (k : ℕ) (u : Option (Fin n)) :
    (encode G).val^[k] (optionFin n u) = optionFin n ((up G)^[k] u) := by
  induction k with
  | zero => rfl
  | succ k ih =>
    rw [Function.iterate_succ_apply',Function.iterate_succ_apply',ih]
    change optionFin n (up G ((optionFin n).symm (optionFin n ((up G)^[k] u)))) = _
    rw [Equiv.symm_apply_apply]

theorem parent_reaches_zero {n : ℕ} (P : ParentForest n) (v : Fin (n+1)) (hv : v ≠ 0) :
    ∃ k : ℕ, 1 ≤ k ∧ P.val^[k] v = 0 := by
  obtain ⟨G,rfl⟩ := (parentEquiv n).surjective P
  change ∃k : ℕ, 1 ≤ k ∧ (encode G).val^[k] v = 0
  revert hv
  refine Fin.cases ?_ (fun u _ => ?_) v
  · intro hz; exact (hz rfl).elim
  · obtain ⟨k,hk,he⟩ := reaches_virtual_root G u
    exact ⟨k,hk,by simpa [he] using encode_iterate G k (some u)⟩

theorem anc_encode_iff {n : ℕ} (G : Forest (Fin n)) (u v : Fin n) :
    Anc G u v ↔ ∃ k : ℕ, (encode G).val^[k] u.succ = v.succ := by
  rw [anc_iterate]
  constructor
  · rintro ⟨k,hk⟩
    exact ⟨k,by simpa [hk] using encode_iterate G k (some u)⟩
  · rintro ⟨k,hk⟩
    refine ⟨k,(optionFin n).injective ?_⟩
    simpa [← encode_iterate G k (some u)] using hk

/-- The canonical 1 + number of proper descendants, defined by parent iteration. -/
def subtreeSize {n : ℕ} (P : ParentForest n) (v : Fin n) : ℕ :=
  1 + Nat.card {u : Fin n // u ≠ v ∧ ∃ k : ℕ, 1 ≤ k ∧ P.val^[k] u.succ = v.succ}

theorem subtreeSize_encode {n : ℕ} (G : Forest (Fin n)) (v : Fin n) :
    subtreeSize (encode G) v = size G v := by
  have hproper : ∀u : Fin n, u ≠ v → (Anc G u v ↔
      ∃ k : ℕ, 1 ≤ k ∧ (encode G).val^[k] u.succ = v.succ) := by
    intro u huv
    rw [anc_encode_iff]
    constructor
    · rintro ⟨k,hk⟩
      have hpos : 1 ≤ k := by
        by_contra hn
        have hz : k = 0 := by omega
        subst k
        have he : u = v := Fin.succ_injective _ hk
        exact huv he
      exact ⟨k,hpos,hk⟩
    · rintro ⟨k,_,hk⟩; exact ⟨k,hk⟩
  let S := Finset.univ.filter (fun u => Anc G u v)
  have hv : v ∈ S := by simp [S,anc_refl]
  have he : Finset.univ.filter (fun u : Fin n => u ≠ v ∧ ∃ k : ℕ,
      1 ≤ k ∧ (encode G).val^[k] u.succ = v.succ) = S.erase v := by
    ext u
    simp only [Finset.mem_filter,Finset.mem_univ,true_and,Finset.mem_erase,S]
    by_cases huv : u = v
    · simp [huv]
    · simp [huv,← hproper u huv]
  rw [subtreeSize,Nat.card_eq_fintype_card,Fintype.card_subtype,he,size_eq_card_filter]
  change 1+(S.erase v).card = S.card
  have hc := Finset.card_erase_add_one hv
  omega

theorem parent_forest_sum_eq_weightedEval (w : ℕ → ℕ) (n : ℕ) :
    (∑ G : ParentForest n, ∏v : Fin n, w (subtreeSize G v)) = ParkingSkeleton.weightedEval w n := by
  rw [← forest_sum_eq_weightedEval]
  symm
  apply Fintype.sum_equiv (parentEquiv n)
  intro G
  apply Finset.prod_congr rfl
  intro v _
  exact congrArg w (subtreeSize_encode G v).symm

theorem original_A_parent_sum (n l : ℕ) :
    Parking.A n l = ∑ G : ParentForest n, ∏v : Fin n, min (subtreeSize G v) (l+1) := by
  exact ((parent_forest_sum_eq_weightedEval (fun s => min s (l+1)) n).trans
    (ParkingSkeleton.weightedEval_original l n)).symm

def canonicalMaxSplitEquiv (n : ℕ) : ParentForest (n+1) ≃ Parts (Fin.last n) :=
  (parentEquiv (n+1)).symm.trans (splitEquiv (Fin.last n) (fun u => Fin.le_last u))

theorem empty_parent_sum (w : ℕ → ℕ) :
    (∑G : ParentForest 0, ∏v : Fin 0, w (subtreeSize G v)) = 1 := by
  rw [parent_forest_sum_eq_weightedEval]
  simp [ParkingSkeleton.weightedEval]

end ParkingForest
