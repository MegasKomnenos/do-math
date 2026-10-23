import GlossaryRepair

open MvPolynomial
noncomputable section
set_option maxHeartbeats 6000000
namespace GlossaryRepair
open ParkingForest

def uDerivative (n q : ℕ) : ℕ → MvPolynomial Bool ℕ
  | 0 => componentPolynomial n q
  | a+1 => pderiv false (uDerivative n q a)

def markedSeries (q a : ℕ) : PowerSeries ℚ :=
  PowerSeries.mk fun n =>
    (q:ℚ)^a * (MvPolynomial.eval (fun _ : Bool => q) (uDerivative n q a) : ℕ) /
      (n.factorial:ℚ)

def dampedValueSeries (q : ℕ) : PowerSeries ℚ :=
  PowerSeries.mk fun n =>
    (evalComponents n q (q-1) q : ℚ) / (n.factorial:ℚ)

def dampedSeries (q : ℕ) : PowerSeries ℚ :=
  PowerSeries.mk fun n =>
    (q:ℚ) * (MvPolynomial.eval (fun b : Bool => if b then q else q-1)
      (pderiv true (componentPolynomial n q)) : ℕ) / (n.factorial:ℚ)

def numeratorSeries (q : ℕ) : PowerSeries ℚ :=
  markedSeries q 2 - PowerSeries.C (q:ℚ) * dampedSeries q

theorem marked_coeff (n q a : ℕ) :
    (n.factorial:ℚ) * PowerSeries.coeff n (markedSeries q a) =
      (q:ℚ)^a * (MvPolynomial.eval (fun _ : Bool => q) (uDerivative n q a) : ℕ) := by
  have hf : (n.factorial:ℚ) ≠ 0 := by exact_mod_cast Nat.factorial_ne_zero n
  simp only [markedSeries, PowerSeries.coeff_mk]
  field_simp

theorem dampedValue_coeff (n q : ℕ) :
    (n.factorial:ℚ) * PowerSeries.coeff n (dampedValueSeries q) =
      (evalComponents n q (q-1) q : ℚ) := by
  have hf : (n.factorial:ℚ) ≠ 0 := by exact_mod_cast Nat.factorial_ne_zero n
  simp only [dampedValueSeries, PowerSeries.coeff_mk]
  field_simp

theorem damped_coeff (n q : ℕ) :
    (n.factorial:ℚ) * PowerSeries.coeff n (dampedSeries q) =
      (q:ℚ) * (MvPolynomial.eval (fun b : Bool => if b then q else q-1)
        (pderiv true (componentPolynomial n q)) : ℕ) := by
  have hf : (n.factorial:ℚ) ≠ 0 := by exact_mod_cast Nat.factorial_ne_zero n
  simp only [dampedSeries, PowerSeries.coeff_mk]
  field_simp

theorem numerator_coeff (n q : ℕ) :
    (n.factorial:ℚ) * PowerSeries.coeff n (numeratorSeries q) =
    (q:ℚ)^2 *
      ((MvPolynomial.eval (fun _ : Bool => q)
        (pderiv false (pderiv false (componentPolynomial n q))) : ℕ) -
       (MvPolynomial.eval (fun b : Bool => if b then q else q-1)
        (pderiv true (componentPolynomial n q)) : ℕ) : ℚ) := by
  have hf : (n.factorial:ℚ) ≠ 0 := by exact_mod_cast Nat.factorial_ne_zero n
  simp only [numeratorSeries, map_sub, PowerSeries.coeff_C_mul,
    markedSeries, dampedSeries, PowerSeries.coeff_mk, uDerivative]
  field_simp

theorem numerator_coeff_original_lower (n l : ℕ+) :
    (n.val.factorial:ℚ) * PowerSeries.coeff n.val (numeratorSeries (l.val+1)) /
      ((l.val:ℚ)+1)^2 ≤
        (Parking.b n (l.val+1):ℚ) - (Parking.b n l.val:ℚ) := by
  rw [numerator_coeff]
  let u : ℕ := MvPolynomial.eval (fun _ : Bool => l.val+1)
    (pderiv false (pderiv false (componentPolynomial n.val (l.val+1))))
  let v : ℕ := MvPolynomial.eval (fun b : Bool => if b then l.val+1 else l.val)
    (pderiv true (componentPolynomial n.val (l.val+1)))
  have hi := original_delta_F_restored n l
  change (u:ℤ)-(v:ℤ) ≤ delta n l at hi
  have h : (u:ℚ)-(v:ℚ) ≤ (delta n l:ℚ) := by exact_mod_cast hi
  have he : l.val+1-1=l.val := by omega
  rw [he]
  change ((l.val+1:ℕ):ℚ)^2*((u:ℚ)-(v:ℚ))/((l.val:ℚ)+1)^2 ≤ _
  simp only [Nat.cast_add, Nat.cast_one]
  rw [mul_div_cancel_left₀ _ (show ((l.val:ℚ)+1)^2 ≠ 0 by positivity)]
  simpa [delta] using h

theorem original_increase_of_numerator_coeff (n l : ℕ+)
    (h : 0 ≤ PowerSeries.coeff n.val (numeratorSeries (l.val+1))) :
    Parking.b n l.val ≤ Parking.b n (l.val+1) := by
  have hb := numerator_coeff_original_lower n l
  have hz : (0:ℚ) ≤ (n.val.factorial:ℚ) *
      PowerSeries.coeff n.val (numeratorSeries (l.val+1)) / ((l.val:ℚ)+1)^2 :=
    div_nonneg (mul_nonneg (by positivity) h) (by positivity)
  have hi : (Parking.b n l.val:ℚ) ≤ (Parking.b n (l.val+1):ℚ) := by linarith
  exact_mod_cast hi

#print axioms markedSeries
#print axioms dampedValueSeries
#print axioms dampedSeries
#print axioms numeratorSeries
#print axioms marked_coeff
#print axioms dampedValue_coeff
#print axioms damped_coeff
#print axioms numerator_coeff
#print axioms numerator_coeff_original_lower
#print axioms original_increase_of_numerator_coeff
end GlossaryRepair

