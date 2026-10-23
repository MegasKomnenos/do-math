import PInterface
import Mathlib.Tactic

/- The evaluator is not a formal parent-function forest enumeration.
   The forest/evaluator identification is proved only in the exposition. -/
namespace ParkingSkeleton
open Parking
open ParkingLastCar
open scoped BigOperators

def weightedEval (w : ℕ → ℕ) (m : ℕ) : ℕ :=
  match m with
  | 0 => 1
  | n+1 => ∑ k : Fin (n+1),
      n.choose k.val * w (k.val+1) * weightedEval w k.val * weightedEval w (n-k.val)
termination_by m
decreasing_by all_goals have := k.isLt; omega

theorem weightedEval_congr (w v : ℕ → ℕ) (h : ∀ s, w s = v s) (m : ℕ) :
    weightedEval w m = weightedEval v m := by
  have : w = v := funext h
  rw [this]

theorem weightedEval_mono (w v : ℕ → ℕ) (h : ∀ s, w s ≤ v s) (m : ℕ) :
    weightedEval w m ≤ weightedEval v m := by
  induction m using Nat.strong_induction_on with
  | h m ih =>
    cases m with
    | zero => simp [weightedEval]
    | succ n =>
      rw [weightedEval, weightedEval]
      apply Finset.sum_le_sum
      intro k _
      apply Nat.mul_le_mul
      · apply Nat.mul_le_mul
        · exact Nat.mul_le_mul_left _ (h _)
        · exact ih k.val k.isLt
      · exact ih (n-k.val) (by omega)

theorem weightedEval_original (l m : ℕ) :
    weightedEval (fun s => min s (l+1)) m = A m l := by
  induction m using Nat.strong_induction_on with
  | h m ih =>
    cases m with
    | zero => simp [weightedEval, A_empty]
    | succ n =>
      rw [weightedEval, A_recurrence, ← Fin.sum_univ_eq_sum_range]
      apply Finset.sum_congr rfl
      intro k _
      rw [ih k.val k.isLt, ih (n-k.val) (by omega)]

def boxWeight (x c s : ℕ) : ℕ := if s ≤ x then s else c
def skeletonEval (x c n : ℕ) : ℕ := weightedEval (boxWeight x c) n

theorem skeleton_same (l n : ℕ) : skeletonEval (l+1) (l+1) n = A n l := by
  unfold skeletonEval
  rw [← weightedEval_original l n]
  apply weightedEval_congr
  intro s
  unfold boxWeight
  split_ifs with h
  · omega
  · omega

theorem skeleton_next (l n : ℕ) : skeletonEval (l+1) (l+2) n = A n (l+1) := by
  unfold skeletonEval
  rw [← weightedEval_original (l+1) n]
  apply weightedEval_congr
  intro s
  unfold boxWeight
  split_ifs with h
  · omega
  · omega

theorem mul_midpoint (a₀ a₁ a₂ b₀ b₁ b₂ : ℕ)
    (ha₀ : a₀ ≤ a₁) (ha₁ : a₁ ≤ a₂) (ha : 2*a₁ ≤ a₀+a₂)
    (hb₀ : b₀ ≤ b₁) (hb₁ : b₁ ≤ b₂) (hb : 2*b₁ ≤ b₀+b₂) :
    2*(a₁*b₁) ≤ a₀*b₀+a₂*b₂ := by
  have h1 : 0 ≤ ((a₂:ℤ)-a₁)*((b₂:ℤ)-b₁) :=
    mul_nonneg (by omega) (by omega)
  have h2 : 0 ≤ ((a₁:ℤ)-a₀)*((b₁:ℤ)-b₀) :=
    mul_nonneg (by omega) (by omega)
  have h3 : 0 ≤ (a₁:ℤ)*((b₀:ℤ)+b₂-2*b₁) :=
    mul_nonneg (by omega) (by omega)
  have h4 : 0 ≤ (b₁:ℤ)*((a₀:ℤ)+a₂-2*a₁) :=
    mul_nonneg (by omega) (by omega)
  have hz : 2*((a₁:ℤ)*b₁) ≤ (a₀:ℤ)*b₀+(a₂:ℤ)*b₂ := by nlinarith
  exact_mod_cast hz

theorem weightedEval_convex (w₀ w₁ w₂ : ℕ → ℕ)
    (h₀ : ∀ s, w₀ s ≤ w₁ s) (h₁ : ∀ s, w₁ s ≤ w₂ s)
    (hc : ∀ s, 2*w₁ s ≤ w₀ s+w₂ s) (m : ℕ) :
    2*weightedEval w₁ m ≤ weightedEval w₀ m+weightedEval w₂ m := by
  induction m using Nat.strong_induction_on with
  | h m ih =>
    cases m with
    | zero => simp [weightedEval]
    | succ n =>
      rw [weightedEval, weightedEval, weightedEval, Finset.mul_sum,
        ← Finset.sum_add_distrib]
      apply Finset.sum_le_sum
      intro k _
      have hl := ih k.val k.isLt
      have hr := ih (n-k.val) (by omega)
      have hm := mul_midpoint _ _ _ _ _ _ (h₀ (k.val+1)) (h₁ (k.val+1))
        (hc (k.val+1)) (weightedEval_mono _ _ h₀ k.val)
        (weightedEval_mono _ _ h₁ k.val) hl
      have hp := mul_midpoint _ _ _ _ _ _
        (Nat.mul_le_mul (h₀ _) (weightedEval_mono _ _ h₀ _))
        (Nat.mul_le_mul (h₁ _) (weightedEval_mono _ _ h₁ _)) hm
        (weightedEval_mono _ _ h₀ _) (weightedEval_mono _ _ h₁ _) hr
      calc
        2*(n.choose k.val*w₁ (k.val+1)*weightedEval w₁ k.val*
            weightedEval w₁ (n-k.val)) = n.choose k.val*
            (2*(w₁ (k.val+1)*weightedEval w₁ k.val*weightedEval w₁ (n-k.val))) := by ring
        _ ≤ n.choose k.val*(w₀ (k.val+1)*weightedEval w₀ k.val*weightedEval w₀ (n-k.val)+
            w₂ (k.val+1)*weightedEval w₂ k.val*weightedEval w₂ (n-k.val)) :=
            Nat.mul_le_mul_left _ hp
        _ = _ := by ring

def gammaPlus (n l : ℕ) : ℤ :=
  (A n (l+1):ℤ)-2*(A n l:ℤ)+(skeletonEval (l+1) l n:ℤ)
def gammaMinus (n l : ℕ) : ℤ :=
  (skeletonEval (l+1) l n:ℤ)-(A n (l-1):ℤ)

theorem gammaPlus_three_values (n l : ℕ) :
    gammaPlus n l = (skeletonEval (l+1) (l+2) n:ℤ)-
      2*(skeletonEval (l+1) (l+1) n:ℤ)+(skeletonEval (l+1) l n:ℤ) := by
  simp [gammaPlus, skeleton_same, skeleton_next]

theorem gammaPlus_nonneg (n l : ℕ) : 0 ≤ gammaPlus n l := by
  have h := weightedEval_convex (boxWeight (l+1) l) (boxWeight (l+1) (l+1))
    (boxWeight (l+1) (l+2))
    (by intro s; unfold boxWeight; split_ifs <;> omega)
    (by intro s; unfold boxWeight; split_ifs <;> omega)
    (by intro s; unfold boxWeight; split_ifs <;> omega) n
  change 2*skeletonEval (l+1) (l+1) n ≤
    skeletonEval (l+1) l n+skeletonEval (l+1) (l+2) n at h
  rw [skeleton_same, skeleton_next] at h
  unfold gammaPlus
  omega

theorem gammaMinus_nonneg (n l : ℕ) (hl : 1 ≤ l) : 0 ≤ gammaMinus n l := by
  have h := weightedEval_mono (fun s => min s ((l-1)+1)) (boxWeight (l+1) l)
    (by intro s; unfold boxWeight; split_ifs <;> omega) n
  rw [weightedEval_original] at h
  change A n (l-1) ≤ skeletonEval (l+1) l n at h
  unfold gammaMinus
  omega

theorem original_gain_minus_loss (n : ℕ+) (l : ℕ) (hl : 1 ≤ l) :
    (b n (l+1):ℤ)-(b n l:ℤ) = gammaPlus n l-gammaMinus n l := by
  rw [b_curvature n l hl]
  simp only [gammaPlus, gammaMinus]
  ring

/-- Actual failure of coefficientwise positivity in the exponential source.
    The link to the marked-chain source is nonformal, as explained in the text. -/
theorem signed_source_four_negative (u : ℕ) :
    let q : ℤ := (u:ℤ)+13
    let k : ℤ := q-4
    (1-k)*(q+1)^4+2*k*q^4-(1+k)*(q-1)^4 < 0 := by
  dsimp
  have hid : (1-((u:ℤ)+13-4))*((u:ℤ)+13+1)^4+
      2*((u:ℤ)+13-4)*((u:ℤ)+13)^4-
      (1+((u:ℤ)+13-4))*((u:ℤ)+13-1)^4 =
      -4*(u:ℤ)^3-108*(u:ℤ)^2-774*(u:ℤ)-590 := by ring
  rw [hid]
  have h1 : 0 ≤ (u:ℤ)^3 := by positivity
  have h2 : 0 ≤ (u:ℤ)^2 := by positivity
  omega

#print axioms weightedEval_congr
#print axioms weightedEval_mono
#print axioms weightedEval_original
#print axioms skeleton_same
#print axioms skeleton_next
#print axioms mul_midpoint
#print axioms weightedEval_convex
#print axioms gammaPlus_three_values
#print axioms gammaPlus_nonneg
#print axioms gammaMinus_nonneg
#print axioms original_gain_minus_loss
#print axioms signed_source_four_negative
end ParkingSkeleton
