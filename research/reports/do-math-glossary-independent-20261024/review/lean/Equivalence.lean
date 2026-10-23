import Extraction

namespace ParkingLastCar
open Parking
noncomputable section

theorem leftSet_assemble {n l : ℕ} (I : Finset (Fin n))
    (t : Fin (min (I.card+1) (l+1))) (a : Trace I.card l) (b : Trace Iᶜ.card l) :
    leftSet (assemble ⟨I,t,a,b⟩) = I := by
  ext i
  rw [mem_leftSet, assemble_last_p]
  by_cases hi : i ∈ I
  · obtain ⟨j, hj⟩ := (index_range I i).mpr hi
    rw [← hj, assemble_left_p]
    exact iff_of_true (a.val.2 j).isLt hi
  · obtain ⟨j, hj⟩ := (index_range Iᶜ i).mpr (Finset.mem_compl.mpr hi)
    rw [← hj, assemble_right_p]
    apply iff_of_false _ hi
    change ¬ I.card+1+(b.val.2 j).val < I.card
    omega

theorem assemble_injective (n l : ℕ) : Function.Injective (@assemble n l) := by
  rintro ⟨I,t,a,b⟩ ⟨J,u,c,d⟩ h
  have hI := congrArg leftSet h
  simp only [leftSet_assemble] at hI
  subst J
  have ht : t = u := by
    apply Fin.ext
    have hh := congrArg (fun x : Trace (n+1) l => (x.val.1 (Fin.last n)).val) h
    simp only [assemble_last_a, lastPref] at hh
    have htb := (lt_min_iff.mp t.isLt).1
    have hub := (lt_min_iff.mp u.isLt).1
    omega
  have ha : a = c := by
    apply Subtype.ext
    apply Prod.ext
    · funext i
      apply Fin.ext
      have hh := congrArg (fun x : Trace (n+1) l => (x.val.1 (index I i)).val) h
      simpa only [assemble_left_a, leftLift] using hh
    · funext i
      apply Fin.ext
      have hh := congrArg (fun x : Trace (n+1) l => (x.val.2 (index I i)).val) h
      simpa only [assemble_left_p, leftLift] using hh
  have hb : b = d := by
    apply Subtype.ext
    apply Prod.ext
    · funext i
      apply Fin.ext
      have hh := congrArg (fun x : Trace (n+1) l => (x.val.1 (index Iᶜ i)).val) h
      simp only [assemble_right_a, rightLift] at hh
      omega
    · funext i
      apply Fin.ext
      have hh := congrArg (fun x : Trace (n+1) l => (x.val.2 (index Iᶜ i)).val) h
      simp only [assemble_right_p, rightLift] at hh
      omega
  subst u
  subst c
  subst d
  rfl

theorem extract_assemble {n l : ℕ} (d : Pieces n l) : extract (assemble d) = d := by
  apply assemble_injective n l
  exact assemble_extract (assemble d)

/-- The two maps operate on actual successful, displacement-bounded parking executions. -/
def lastCarEquiv (n l : ℕ) : Trace (n+1) l ≃ Pieces n l where
  toFun := extract
  invFun := assemble
  left_inv := assemble_extract
  right_inv := extract_assemble

abbrev OriginalPieces (n l : ℕ) :=
  Σ I : Finset (Fin n), Fin (min (I.card+1) (l+1)) ×
    {a : PF I.card // M a ≤ l} × {b : PF Iᶜ.card // M b ≤ l}

def piecesOriginalEquiv (n l : ℕ) : Pieces n l ≃ OriginalPieces n l :=
  Equiv.sigmaCongrRight (fun I => Equiv.prodCongr (Equiv.refl _)
    (Equiv.prodCongr (traceEquiv I.card l).symm (traceEquiv Iᶜ.card l).symm))

def originalTracePiecesEquiv (n l : ℕ) :
    {a : PF (n+1) // M a ≤ l} ≃ Pieces n l :=
  (traceEquiv (n+1) l).trans (lastCarEquiv n l)

def originalLastCarEquiv (n l : ℕ) :
    {a : PF (n+1) // M a ≤ l} ≃ OriginalPieces n l :=
  (originalTracePiecesEquiv n l).trans (piecesOriginalEquiv n l)

#print axioms leftSet_assemble
#print axioms assemble_injective
#print axioms extract_assemble
#print axioms lastCarEquiv
#print axioms piecesOriginalEquiv
#print axioms originalTracePiecesEquiv
#print axioms originalLastCarEquiv
end
end ParkingLastCar
