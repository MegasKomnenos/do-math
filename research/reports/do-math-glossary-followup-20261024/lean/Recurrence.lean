import Equivalence
import Mathlib.Algebra.BigOperators.Group.Finset.Powerset

namespace ParkingLastCar
open Parking
open scoped BigOperators
noncomputable section
set_option maxHeartbeats 2000000

theorem sum_subsets_card (n : ℕ) (f : ℕ → ℕ) :
    (∑ I : Finset (Fin n), f I.card) = ∑ k ∈ Finset.range (n+1), n.choose k * f k := by
  classical
  have hu : (Finset.univ : Finset (Fin n)).powerset = Finset.univ := by ext; simp
  rw [← hu, Finset.sum_powerset]
  simp_rw [Finset.sum_powersetCard]
  simp

/-- The universal last-car recurrence for the original finite-set count. -/
theorem A_recurrence (n l : ℕ) :
    A (n+1) l = ∑ k ∈ Finset.range (n+1),
      n.choose k * min (k+1) (l+1) * A k l * A (n-k) l := by
  classical
  calc
    A (n+1) l = Fintype.card (Trace (n+1) l) := (card_trace _ _).symm
    _ = Fintype.card (Pieces n l) := Fintype.card_congr (lastCarEquiv n l)
    _ = ∑ I : Finset (Fin n), min (I.card+1) (l+1) * A I.card l * A (n-I.card) l := by
      simp only [Pieces, Fintype.card_sigma, Fintype.card_prod, Fintype.card_fin, card_trace]
      apply Finset.sum_congr rfl
      intro I _
      rw [Finset.card_compl, Fintype.card_fin]
      ring
    _ = ∑ k ∈ Finset.range (n+1), n.choose k *
        (min (k+1) (l+1) * A k l * A (n-k) l) :=
      sum_subsets_card n (fun k => min (k+1) (l+1) * A k l * A (n-k) l)
    _ = _ := by apply Finset.sum_congr rfl; intro k _; ring

theorem A_recurrence_zero (l : ℕ) :
    A 1 l = min 1 (l+1) * A 0 l * A 0 l := by
  simpa using A_recurrence 0 l

theorem zero_distance_choices (k : ℕ) : min (k+1) (0+1) = 1 := by omega

theorem saturated_choices (k l : ℕ) (h : k ≤ l) : min (k+1) (l+1) = k+1 := by omega

theorem A_recurrence_distance_zero (n : ℕ) :
    A (n+1) 0 = ∑ k ∈ Finset.range (n+1), n.choose k * A k 0 * A (n-k) 0 := by
  simpa [zero_distance_choices] using A_recurrence n 0

#print axioms sum_subsets_card
#print axioms A_recurrence
#print axioms A_recurrence_zero
#print axioms zero_distance_choices
#print axioms saturated_choices
#print axioms A_recurrence_distance_zero
end
end ParkingLastCar
