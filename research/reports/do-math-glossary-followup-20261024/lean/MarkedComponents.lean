import BoundaryForest
import Mathlib.Algebra.MvPolynomial.PDeriv

open scoped BigOperators
open MvPolynomial
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000

namespace ParkingForest

def smallBase {n : ℕ} (P : ParentForest n) (q : ℕ) : ℕ :=
  ∏ v : Fin n, if subtreeSize P v < q then subtreeSize P v else 1

def largeCount {n : ℕ} (P : ParentForest n) (q : ℕ) : ℕ :=
  (Finset.univ.filter (fun v : Fin n => q < subtreeSize P v)).card

def hitCount {n : ℕ} (P : ParentForest n) (q : ℕ) : ℕ :=
  (Finset.univ.filter (fun v : Fin n => subtreeSize P v = q)).card

def markedFactor (q t : ℕ) : MvPolynomial Bool ℕ :=
  if t < q then C t else if t = q then X true else X false

def componentPolynomial (n q : ℕ) : MvPolynomial Bool ℕ :=
  ∑ P : ParentForest n, ∏ v : Fin n, markedFactor q (subtreeSize P v)

def smallWeightedCoefficient (n q a e : ℕ) : ℕ :=
  ∑ P : ParentForest n,
    if largeCount P q = a ∧ hitCount P q = e then smallBase P q else 0

def aeExponent (a e : ℕ) : Bool →₀ ℕ :=
  Finsupp.single false a + Finsupp.single true e

theorem forestMonomial_factor {n : ℕ} (P : ParentForest n) (q : ℕ) :
    (∏ v : Fin n, markedFactor q (subtreeSize P v)) =
      C (smallBase P q) * X false ^ largeCount P q * X true ^ hitCount P q := by
  have h : ∀ t : ℕ, markedFactor q t =
      C (if t < q then t else 1) *
      (if q < t then X false else 1) *
      (if t = q then X true else 1) := by
    intro t
    unfold markedFactor
    split_ifs <;> simp_all <;> omega
  simp_rw [h, Finset.prod_mul_distrib]
  simp [smallBase, largeCount, hitCount, Finset.prod_ite, -map_prod]

theorem componentPolynomial_factor (n q : ℕ) :
    componentPolynomial n q = ∑ P : ParentForest n,
      C (smallBase P q) * X false ^ largeCount P q * X true ^ hitCount P q := by
  apply Finset.sum_congr rfl
  intro P _
  exact forestMonomial_factor P q

theorem aeExponent_inj (a e b f : ℕ) :
    aeExponent a e = aeExponent b f ↔ a = b ∧ e = f := by
  constructor
  · intro h
    have h0 := congrArg (fun v : Bool →₀ ℕ => v false) h
    have h1 := congrArg (fun v : Bool →₀ ℕ => v true) h
    simpa [aeExponent] using And.intro h0 h1
  · rintro ⟨rfl,rfl⟩
    rfl

theorem aeMonomial (B a e : ℕ) :
    (C B * X false ^ a * X true ^ e : MvPolynomial Bool ℕ) =
      monomial (aeExponent a e) B := by
  simp only [X_pow_eq_monomial, C_mul_monomial, monomial_mul, one_mul, mul_one]
  rfl

theorem componentPolynomial_coefficient (n q a e : ℕ) :
    MvPolynomial.coeff (aeExponent a e) (componentPolynomial n q) =
      smallWeightedCoefficient n q a e := by
  rw [componentPolynomial_factor]
  simp only [aeMonomial,coeff_sum,coeff_monomial,aeExponent_inj]
  unfold smallWeightedCoefficient
  apply Finset.sum_congr rfl
  intro P _
  simp only [eq_comm]

def evalComponents (n q U Y : ℕ) : ℕ :=
  MvPolynomial.eval (fun b : Bool => if b then Y else U) (componentPolynomial n q)

theorem evalComponents_sum (n q U Y : ℕ) :
    evalComponents n q U Y = ∑ P : ParentForest n,
      smallBase P q * U ^ largeCount P q * Y ^ hitCount P q := by
  simp [evalComponents, componentPolynomial_factor]

theorem evalComponents_parent (n q U Y : ℕ) :
    evalComponents n q U Y = ∑ P : ParentForest n, ∏ v : Fin n,
      if subtreeSize P v < q then subtreeSize P v
      else if subtreeSize P v = q then Y else U := by
  unfold evalComponents componentPolynomial
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro P _
  rw [map_prod]
  apply Finset.prod_congr rfl
  intro v _
  by_cases h : subtreeSize P v < q
  · simp [markedFactor, h]
  · by_cases he : subtreeSize P v = q <;> simp [markedFactor, h, he]

theorem evalComponents_mid (n q : ℕ) (hq : 1 ≤ q) :
    evalComponents n q q q = Parking.A n (q-1) := by
  rw [evalComponents_parent, original_A_parent_sum]
  have he : q-1+1 = q := by omega
  rw [he]
  apply Finset.sum_congr rfl
  intro P _
  apply Finset.prod_congr rfl
  intro v _
  split_ifs <;> omega

theorem evalComponents_next (n q : ℕ) :
    evalComponents n q (q+1) q = Parking.A n q := by
  rw [evalComponents_parent, original_A_parent_sum]
  apply Finset.sum_congr rfl
  intro P _
  apply Finset.prod_congr rfl
  intro v _
  split_ifs <;> omega

theorem evalComponents_prev (n q : ℕ) (hq : 2 ≤ q) :
    evalComponents n q (q-1) (q-1) = Parking.A n (q-2) := by
  rw [evalComponents_parent, original_A_parent_sum]
  have he : q-2+1 = q-1 := by omega
  rw [he]
  apply Finset.sum_congr rfl
  intro P _
  apply Finset.prod_congr rfl
  intro v _
  split_ifs <;> omega

theorem original_delta_components (n l : ℕ+) :
    delta n l = (evalComponents n.val (l.val+1) (l.val+2) (l.val+1) : ℤ) -
      2 * (evalComponents n.val (l.val+1) (l.val+1) (l.val+1) : ℤ) +
      (evalComponents n.val (l.val+1) l.val l.val : ℤ) := by
  have h := l.pos
  have hp := evalComponents_prev n.val (l.val+1) (by omega)
  have hm := evalComponents_mid n.val (l.val+1) (by omega)
  have hn := evalComponents_next n.val (l.val+1)
  have ha : l.val+1-1 = l.val := by omega
  have hb : l.val+1-2 = l.val-1 := by omega
  rw [ha,hb] at hp
  rw [ha] at hm
  rw [show l.val+2 = (l.val+1)+1 by omega, hn, hm, hp]
  exact ParkingLastCar.b_curvature n l.val l.pos

theorem monomial_UU (B a e : ℕ) :
    pderiv false (pderiv false
      (C B * X false ^ a * X true ^ e : MvPolynomial Bool ℕ)) =
      C (B * a * (a-1)) * X false ^ (a-2) * X true ^ e := by
  cases a with
  | zero => simp
  | succ a =>
    cases a with
    | zero => simp
    | succ a =>
      simp [Nat.cast_add, Nat.cast_mul]
      ring

theorem monomial_Y (B a e : ℕ) :
    pderiv true (C B * X false ^ a * X true ^ e : MvPolynomial Bool ℕ) =
      C (B * e) * X false ^ a * X true ^ (e-1) := by
  simp [Nat.cast_mul]
  ring

theorem monomial_YY (B a e : ℕ) :
    pderiv true (pderiv true
      (C B * X false ^ a * X true ^ e : MvPolynomial Bool ℕ)) =
      C (B * e * (e-1)) * X false ^ a * X true ^ (e-2) := by
  rw [monomial_Y, monomial_Y]
  congr 1

theorem component_UU (n q U Y : ℕ) :
    MvPolynomial.eval (fun b : Bool => if b then Y else U)
      (pderiv false (pderiv false (componentPolynomial n q))) =
    ∑ P : ParentForest n, smallBase P q * largeCount P q * (largeCount P q-1) *
      U ^ (largeCount P q-2) * Y ^ hitCount P q := by
  rw [componentPolynomial_factor]
  simp only [map_sum, monomial_UU]
  simp

theorem component_Y (n q U Y : ℕ) :
    MvPolynomial.eval (fun b : Bool => if b then Y else U)
      (pderiv true (componentPolynomial n q)) =
    ∑ P : ParentForest n, smallBase P q * hitCount P q *
      U ^ largeCount P q * Y ^ (hitCount P q-1) := by
  rw [componentPolynomial_factor]
  simp only [map_sum, monomial_Y]
  simp

theorem component_YY (n q U Y : ℕ) :
    MvPolynomial.eval (fun b : Bool => if b then Y else U)
      (pderiv true (pderiv true (componentPolynomial n q))) =
    ∑ P : ParentForest n, smallBase P q * hitCount P q * (hitCount P q-1) *
      U ^ largeCount P q * Y ^ (hitCount P q-2) := by
  rw [componentPolynomial_factor]
  simp only [map_sum, monomial_YY]
  simp

end ParkingForest
