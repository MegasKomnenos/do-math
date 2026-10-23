import ForestSplit

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
universe u
namespace ParkingForest

theorem total_eq_eval (w : ℕ → ℕ) (n : ℕ) :
    ∀ (V : Type u) [LinearOrder V] [Fintype V], Fintype.card V = n →
      total (V := V) w = ParkingSkeleton.weightedEval w n := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro V _ _ hn
    cases n with
    | zero =>
      haveI : IsEmpty V := Fintype.card_eq_zero_iff.mp hn
      let G0 : Forest V := ⟨fun _ => none, fun u => isEmptyElim u⟩
      haveI : Subsingleton (Forest V) := by unfold Forest; infer_instance
      haveI : Unique (Forest V) := ⟨⟨G0⟩,fun _ => Subsingleton.elim _ _⟩
      simp [total,weight,ParkingSkeleton.weightedEval]
    | succ m =>
      have hne : (Finset.univ : Finset V).Nonempty := by
        have hc : 0 < Fintype.card V := by omega
        exact Finset.univ_nonempty_iff.mpr (Fintype.card_pos_iff.mp hc)
      let r := (Finset.univ : Finset V).max' hne
      have hr : ∀u : V, u ≤ r := fun u => Finset.le_max' _ u (Finset.mem_univ u)
      rw [total_split r hr]
      have ht : (∑ S : {S : Finset V // r ∉ S},
          w (S.val.card+1) * total (V := (S.val : Set V)) w * total (V := Outside r S.val) w) =
          ∑ S : {S : Finset V // r ∉ S}, w (S.val.card+1) *
            ParkingSkeleton.weightedEval w S.val.card * ParkingSkeleton.weightedEval w (m-S.val.card) := by
        apply Finset.sum_congr rfl
        intro S _
        have hc := card_outside r S.val S.property
        have hleft : S.val.card < m+1 := by omega
        have hright : Fintype.card (Outside r S.val) < m+1 := by omega
        have ho : Fintype.card (Outside r S.val) = m-S.val.card := by omega
        rw [ih S.val.card hleft (S.val : Set V) (by simp),
          ih (Fintype.card (Outside r S.val)) hright (Outside r S.val) rfl,ho]
      rw [ht,sum_avoid_card r (fun k => w (k+1) * ParkingSkeleton.weightedEval w k *
        ParkingSkeleton.weightedEval w (m-k))]
      simp only [hn,Nat.add_sub_cancel]
      rw [ParkingSkeleton.weightedEval]
      rw [Fin.sum_univ_eq_sum_range (fun k => m.choose k * w (k+1) *
        ParkingSkeleton.weightedEval w k * ParkingSkeleton.weightedEval w (m-k))]
      apply Finset.sum_congr rfl
      intro k _
      ring

theorem forest_sum_eq_weightedEval (w : ℕ → ℕ) (n : ℕ) :
    (∑ G : Forest (Fin n), ∏ v : Fin n, w (size G v)) = ParkingSkeleton.weightedEval w n :=
  total_eq_eval w n (Fin n) (Fintype.card_fin n)

theorem original_A_forest_sum (n l : ℕ) :
    Parking.A n l = ∑ G : Forest (Fin n), ∏v : Fin n, min (size G v) (l+1) := by
  exact ((forest_sum_eq_weightedEval (fun s => min s (l+1)) n).trans
    (ParkingSkeleton.weightedEval_original l n)).symm

def skeletonSum (n x c : ℕ) : ℕ :=
  ∑ G : Forest (Fin n), ∏v : Fin n, ParkingSkeleton.boxWeight x c (size G v)

theorem skeletonSum_eq (n x c : ℕ) :
    skeletonSum n x c = ParkingSkeleton.skeletonEval x c n :=
  forest_sum_eq_weightedEval _ n

end ParkingForest
