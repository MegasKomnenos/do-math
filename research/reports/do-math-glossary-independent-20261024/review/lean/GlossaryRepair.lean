import InteriorLower
import Mathlib.RingTheory.PowerSeries.Basic

open scoped BigOperators
open MvPolynomial
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000

namespace GlossaryRepair
open ParkingForest

theorem power_gap_le_derivative (q : ℤ) (e : ℕ) (hq : 1 ≤ q) :
    q^e - (q-1)^e ≤ (e:ℤ)*q^(e-1) := by
  induction e with
  | zero => simp
  | succ e ih =>
    cases e with
    | zero => simp
    | succ e =>
      have hm : (q-1)^(e+1) ≤ q^(e+1) := by
        gcongr <;> omega
      have hh := mul_le_mul_of_nonneg_left ih (show (0:ℤ) ≤ q by omega)
      simp only [Nat.cast_add, Nat.cast_one, Nat.add_sub_cancel, pow_succ] at *
      nlinarith

theorem component_loss_le_Y (n q : ℕ) (hq : 2 ≤ q) :
    (evalComponents n q (q-1) q : ℤ) -
      (evalComponents n q (q-1) (q-1) : ℤ) ≤
    (MvPolynomial.eval (fun b : Bool => if b then q else q-1)
      (pderiv true (componentPolynomial n q)) : ℕ) := by
  rw [evalComponents_sum, evalComponents_sum, component_Y]
  push_cast
  rw [← Finset.sum_sub_distrib]
  apply Finset.sum_le_sum
  intro P _
  have hp := power_gap_le_derivative (q:ℤ) (hitCount P q) (by omega)
  have hm := mul_le_mul_of_nonneg_left hp
    (show (0:ℤ) ≤ (smallBase P q:ℤ)*((q-1:ℕ):ℤ)^largeCount P q by positivity)
  have hq1 : ((q-1:ℕ):ℤ)=(q:ℤ)-1 := by omega
  convert hm using 1 <;> simp only [hq1] <;> ring

theorem original_delta_F_restored (n l : ℕ+) :
    ((MvPolynomial.eval (fun _ : Bool => l.val+1)
      (pderiv false (pderiv false (componentPolynomial n.val (l.val+1)))) : ℕ) : ℤ) -
    ((MvPolynomial.eval (fun b : Bool => if b then l.val+1 else l.val)
      (pderiv true (componentPolynomial n.val (l.val+1))) : ℕ) : ℤ) ≤
      (delta n l : ℤ) := by
  have hq : 2 ≤ l.val+1 := by have := l.pos; omega
  have hb := original_delta_finite_loss_lower n l
  have hy := component_loss_le_Y n.val (l.val+1) hq
  have he : l.val+1-1=l.val := by omega
  rw [he] at hy
  simp only [ite_self] at hb
  linarith

#print axioms power_gap_le_derivative
#print axioms component_loss_le_Y
#print axioms original_delta_F_restored
end GlossaryRepair

