import MarkedLower

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
namespace ParkingForest

theorem curvature_finite_loss_lower (q : ℤ) (a e : ℕ) (hq : 1 ≤ q) :
    (a*(a-1) : ℕ)*q^(a-2)*q^e -
      (q^e-(q-1)^e)*(q-1)^a ≤
    (q+1)^a*q^e-2*q^(a+e)+(q-1)^(a+e) := by
  have hm := mul_le_mul_of_nonneg_right (central_power_lower_int q a hq)
    (show 0 ≤ q^e by positivity)
  calc
    _ ≤ ((q+1)^a-2*q^a+(q-1)^a)*q^e - (q^e-(q-1)^e)*(q-1)^a :=
      sub_le_sub_right hm _
    _ = _ := by simp only [pow_add]; ring

theorem monomial_finite_loss_lower (B q a e : ℕ) (hq : 2 ≤ q) :
    (B*a*(a-1)*q^(a-2)*q^e : ℕ) -
      ((B*(q-1)^a*q^e : ℕ) - (B*(q-1)^a*(q-1)^e : ℕ) : ℤ) ≤
    ((B*(q+1)^a*q^e : ℕ) - 2*(B*q^a*q^e : ℕ) +
      (B*(q-1)^a*(q-1)^e : ℕ) : ℤ) := by
  have hm := mul_le_mul_of_nonneg_left
    (curvature_finite_loss_lower (q : ℤ) a e (by omega))
    (show (0 : ℤ) ≤ B by positivity)
  have hq1 : ((q-1 : ℕ) : ℤ) = (q : ℤ)-1 := by omega
  convert hm using 1 <;> first | rfl | (push_cast; try simp only [hq1,pow_add]; ring)

theorem original_delta_finite_loss_lower (n l : ℕ+) :
    (MvPolynomial.eval (fun b : Bool => if b then l.val+1 else l.val+1)
      (MvPolynomial.pderiv false (MvPolynomial.pderiv false
        (componentPolynomial n.val (l.val+1)))) : ℕ) -
      ((evalComponents n.val (l.val+1) l.val (l.val+1) : ℤ) -
       (evalComponents n.val (l.val+1) l.val l.val : ℤ)) ≤ delta n l := by
  have hq : 2 ≤ l.val+1 := by have := l.pos; omega
  have h := Finset.sum_le_sum (s := (Finset.univ : Finset (ParentForest n.val)))
    (fun P _ => monomial_finite_loss_lower (smallBase P (l.val+1)) (l.val+1)
      (largeCount P (l.val+1)) (hitCount P (l.val+1)) hq)
  have hpred : l.val+1-1 = l.val := by omega
  rw [original_delta_components]
  simp_rw [evalComponents_sum]
  rw [component_UU]
  rw [hpred] at h
  convert h using 1 <;>
    first | rfl | (simp only [Nat.cast_sum,Nat.cast_mul,Nat.cast_pow,mul_add,mul_sub,
      Finset.sum_sub_distrib,Finset.sum_add_distrib,Finset.mul_sum])

theorem curvature_two_hits_lower (q : ℤ) (a e : ℕ) (hq : 1 ≤ q)
    (he : e ≤ 2) :
    2*((q+1)^a*q^e-2*q^(a+e)+(q-1)^(a+e)) ≥
    2*(a*(a-1) : ℕ)*q^(a-2)*q^e -
      2*(e : ℤ)*(q-1)^a*(0 : ℤ)^(e-1) -
      (2*q-1)*(e*(e-1) : ℕ)*(q-1)^a*(0 : ℤ)^(e-2) := by
  have h := curvature_finite_loss_lower q a e hq
  interval_cases e <;> norm_num at * <;> (try simp only [pow_add,pow_two] at *) <;> nlinarith

theorem monomial_two_hits_lower (B q a e : ℕ) (hq : 2 ≤ q) (he : e ≤ 2) :
    2*((B*(q+1)^a*q^e : ℕ) - 2*(B*q^a*q^e : ℕ) +
      (B*(q-1)^a*(q-1)^e : ℕ) : ℤ) ≥
    2*(B*a*(a-1)*q^(a-2)*q^e : ℕ) -
      2*(B*e*(q-1)^a*0^(e-1) : ℕ) -
      (2*(q : ℤ)-1)*(B*e*(e-1)*(q-1)^a*0^(e-2) : ℕ) := by
  have hm := mul_le_mul_of_nonneg_left
    (curvature_two_hits_lower (q : ℤ) a e (by omega) he)
    (show (0 : ℤ) ≤ B by positivity)
  have hq1 : ((q-1 : ℕ) : ℤ) = (q : ℤ)-1 := by omega
  convert hm using 1 <;>
    first | rfl | (push_cast; try simp only [hq1,pow_add]; ring)

theorem three_cap_hit_bounds {n : ℕ} (P : ParentForest n) (q : ℕ)
    (hq : 1 ≤ q) (hn : n < 3*q) : hitCount P q ≤ 2 := by
  have hp := canonical_hit_packing P q
  by_contra hh
  have he : 3 ≤ hitCount P q := by omega
  nlinarith

theorem interior_hit_bounds {n : ℕ} (P : ParentForest n) (q : ℕ)
    (hq : 4 ≤ q) (hn : n ≤ 2*q+3) :
    hitCount P q ≤ 2 ∧ (hitCount P q = 2 → largeCount P q ≤ n-2*q) := by
  constructor
  · exact three_cap_hit_bounds P q (by omega) (by omega)
  · intro he
    have hp := canonical_hit_packing P q
    rw [he] at hp
    omega

theorem original_delta_two_hits_lower (n l : ℕ+) (hn : n.val < 3*(l.val+1)) :
    2*delta n l ≥
    2*(MvPolynomial.eval (fun b : Bool => if b then l.val+1 else l.val+1)
      (MvPolynomial.pderiv false (MvPolynomial.pderiv false
        (componentPolynomial n.val (l.val+1)))) : ℕ) -
    2*(MvPolynomial.eval (fun b : Bool => if b then 0 else l.val)
      (MvPolynomial.pderiv true (componentPolynomial n.val (l.val+1))) : ℕ) -
    (2*((l.val+1 : ℕ) : ℤ)-1)*
      (MvPolynomial.eval (fun b : Bool => if b then 0 else l.val)
        (MvPolynomial.pderiv true (MvPolynomial.pderiv true
          (componentPolynomial n.val (l.val+1)))) : ℕ) := by
  have hq : 2 ≤ l.val+1 := by have := l.pos; omega
  have h := Finset.sum_le_sum (s := (Finset.univ : Finset (ParentForest n.val)))
    (fun P _ => monomial_two_hits_lower (smallBase P (l.val+1)) (l.val+1)
      (largeCount P (l.val+1)) (hitCount P (l.val+1)) hq
      (three_cap_hit_bounds P _ (by omega) hn))
  have hpred : l.val+1-1 = l.val := by omega
  rw [original_delta_components]
  simp_rw [evalComponents_sum]
  rw [component_UU,component_Y,component_YY]
  rw [hpred] at h
  convert h using 1 <;>
    first | rfl | (simp only [Nat.cast_sum,Nat.cast_mul,Nat.cast_pow,mul_add,mul_sub,
      Finset.sum_sub_distrib,Finset.sum_add_distrib,Finset.mul_sum])

theorem evalComponents_eq_weightedEval (n q U Y : ℕ) :
    evalComponents n q U Y = ParkingSkeleton.weightedEval
      (fun s => if s < q then s else if s = q then Y else U) n := by
  rw [evalComponents_parent]
  exact parent_forest_sum_eq_weightedEval
    (fun s : ℕ => if s < q then s else if s = q then Y else U) n

theorem evalComponents_succ (n q U Y : ℕ) :
    evalComponents (n+1) q U Y = ∑ k : Fin (n+1),
      n.choose k.val * (if k.val+1 < q then k.val+1 else if k.val+1 = q then Y else U) *
        evalComponents k.val q U Y * evalComponents (n-k.val) q U Y := by
  rw [evalComponents_eq_weightedEval, ParkingSkeleton.weightedEval]
  apply Finset.sum_congr rfl
  intro k _
  rw [← evalComponents_eq_weightedEval, ← evalComponents_eq_weightedEval]

theorem curvature_two_hits_negative (q : ℤ) (a : ℕ) (hq : 6 ≤ q)
    (ha : a ≤ 3) : (q+1)^a*q^2-2*q^(a+2)+(q-1)^(a+2) < 0 := by
  let u := q-6
  have hu : 0 ≤ u := by dsimp [u]; omega
  have he : q = u+6 := by dsimp [u]; ring
  rw [he]
  interval_cases a <;> norm_num <;> ring_nf <;>
    nlinarith [pow_nonneg hu 2, pow_nonneg hu 3, pow_nonneg hu 4]

theorem two_hit_subsum_nonpos (n q : ℕ) (hq : 6 ≤ q) (hn : n ≤ 2*q+3) :
    (∑ P : ParentForest n, if hitCount P q = 2 then
      (smallBase P q : ℤ) * (((q+1 : ℕ) : ℤ)^largeCount P q*(q : ℤ)^2 -
        2*(q : ℤ)^(largeCount P q+2) + ((q-1 : ℕ) : ℤ)^(largeCount P q+2))
      else 0) ≤ 0 := by
  apply Finset.sum_nonpos
  intro P _
  split_ifs with hh
  · have hp := canonical_hit_packing P q
    rw [hh] at hp
    have ha : largeCount P q ≤ 3 := by omega
    have hc := curvature_two_hits_negative (q : ℤ) (largeCount P q) (by omega) ha
    have hpred : ((q-1 : ℕ) : ℤ) = (q : ℤ)-1 := by omega
    have hnext : ((q+1 : ℕ) : ℤ) = (q : ℤ)+1 := by push_cast; rfl
    rw [hpred,hnext]
    exact mul_nonpos_of_nonneg_of_nonpos (by positivity) (le_of_lt hc)
  · exact le_rfl

end ParkingForest
