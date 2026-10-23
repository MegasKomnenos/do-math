import MarkedComponents

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
namespace ParkingForest

theorem size_strict_ancestor {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) {v w : V} (h : Anc G v w) (hne : v ≠ w) :
    size G v < size G w := by
  have hw : w ∉ descendants G v := by
    intro hh
    have h1 := anc_le G h
    have h2 := anc_le G (Finset.mem_filter.mp hh).2
    exact hne (le_antisymm h1 h2)
  have hsub : insert w (descendants G v) ⊆ descendants G w := by
    intro u hu
    rcases Finset.mem_insert.mp hu with hu | hu
    · subst u
      simp [descendants, anc_refl]
    · exact Finset.mem_filter.mpr ⟨Finset.mem_univ _,
        anc_trans G (Finset.mem_filter.mp hu).2 h⟩
  have hc := Finset.card_le_card hsub
  rw [Finset.card_insert_of_notMem hw] at hc
  have hc' : size G v + 1 ≤ size G w := by
    simpa only [descendants, ← size_eq_card_filter] using hc
  omega

theorem size_hit_packing {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) (q : ℕ) :
    (Finset.univ.filter (fun v : V => q < size G v)).card +
      q * (Finset.univ.filter (fun v : V => size G v = q)).card ≤ Fintype.card V := by
  let H := Finset.univ.filter (fun v : V => size G v = q)
  let L := Finset.univ.filter (fun v : V => q < size G v)
  let D := H.biUnion (descendants G)
  have hd : (H : Set V).Pairwise (fun v w => Disjoint (descendants G v) (descendants G w)) := by
    intro v hv w hw hne
    have hvq := (Finset.mem_filter.mp hv).2
    have hwq := (Finset.mem_filter.mp hw).2
    apply descendants_disjoint G
    · intro h
      have := size_strict_ancestor G h hne
      omega
    · intro h
      have := size_strict_ancestor G h (Ne.symm hne)
      omega
  have hcard : D.card = q * H.card := by
    rw [Finset.card_biUnion hd]
    calc
      ∑ v ∈ H, (descendants G v).card = ∑ v ∈ H, q := by
        apply Finset.sum_congr rfl
        intro v hv
        simpa only [descendants, ← size_eq_card_filter] using (Finset.mem_filter.mp hv).2
      _ = q * H.card := by simp [Nat.mul_comm]
  have hld : Disjoint L D := by
    apply Finset.disjoint_left.mpr
    intro v hv hdv
    obtain ⟨w, hw, hvw⟩ := Finset.mem_biUnion.mp hdv
    have h1 := (Finset.mem_filter.mp hv).2
    have h2 := (Finset.mem_filter.mp hw).2
    have h3 := size_mono_ancestor G (Finset.mem_filter.mp hvw).2
    omega
  have hc : L.card + D.card ≤ Fintype.card V := by
    rw [← Finset.card_union_of_disjoint hld]
    exact le_trans (Finset.card_le_card (Finset.subset_univ _)) (by simp)
  rw [hcard] at hc
  exact hc

theorem canonical_hit_packing {n : ℕ} (P : ParentForest n) (q : ℕ) :
    largeCount P q + q * hitCount P q ≤ n := by
  obtain ⟨G,rfl⟩ := (parentEquiv n).surjective P
  change largeCount (encode G) q + q * hitCount (encode G) q ≤ n
  simpa [largeCount,hitCount,subtreeSize_encode] using size_hit_packing G q

theorem boundary_hit_bounds {n : ℕ} (P : ParentForest n) (q : ℕ)
    (hq : 2 ≤ q) (hn : n ≤ 2*q+1) :
    hitCount P q ≤ 2 ∧ (hitCount P q = 2 → largeCount P q ≤ 1) := by
  have h := canonical_hit_packing P q
  constructor
  · by_contra hh
    have he : 3 ≤ hitCount P q := by omega
    nlinarith
  · intro he
    rw [he] at h
    omega

theorem central_power_bounds (q : ℤ) (hq : 1 ≤ q) (k : ℕ) :
    ((k+2 : ℕ) : ℤ) * ((k+1 : ℕ) : ℤ) * q^k ≤
      (q+1)^(k+2) - 2*q^(k+2) + (q-1)^(k+2) ∧
    2*((k+2 : ℕ) : ℤ)*q^(k+1) ≤ (q+1)^(k+2) - (q-1)^(k+2) := by
  induction k with
  | zero => constructor <;> norm_num <;> ring_nf <;> omega
  | succ k ih =>
    have heH : (q+1)^(k+1+2) - 2*q^(k+1+2) + (q-1)^(k+1+2) =
        q*((q+1)^(k+2)-2*q^(k+2)+(q-1)^(k+2)) +
        ((q+1)^(k+2)-(q-1)^(k+2)) := by
      rw [show k+1+2 = (k+2)+1 by omega]
      simp only [pow_succ]
      ring
    have heD : (q+1)^(k+1+2) - (q-1)^(k+1+2) =
        q*((q+1)^(k+2)-(q-1)^(k+2)) +
        ((q+1)^(k+2)-2*q^(k+2)+(q-1)^(k+2)) + 2*q^(k+2) := by
      rw [show k+1+2 = (k+2)+1 by omega]
      simp only [pow_succ]
      ring
    have hH := mul_le_mul_of_nonneg_left ih.1 (by omega : 0 ≤ q)
    have hD := mul_le_mul_of_nonneg_left ih.2 (by omega : 0 ≤ q)
    have hnon : 0 ≤ (q+1)^(k+2)-2*q^(k+2)+(q-1)^(k+2) :=
      le_trans (by positivity) ih.1
    constructor
    · rw [heH]
      calc
        _ = q*(((k+2 : ℕ) : ℤ)*((k+1 : ℕ) : ℤ)*q^k) +
            2*((k+2 : ℕ) : ℤ)*q^(k+1) := by
          push_cast
          rw [pow_succ]
          ring
        _ ≤ _ := add_le_add hH ih.2
    · rw [heD]
      calc
        _ = q*(2*((k+2 : ℕ) : ℤ)*q^(k+1)) + 2*q^(k+2) := by
          push_cast
          rw [show k+1+1 = k+2 by omega, pow_succ q (k+1)]
          ring
        _ ≤ _ := by linarith

theorem central_power_lower (q a : ℕ) (hq : 2 ≤ q) :
    (a*(a-1)*q^(a-2) : ℕ) ≤
      ((q+1 : ℕ) : ℤ)^a - 2*(q : ℤ)^a + ((q-1 : ℕ) : ℤ)^a := by
  cases a with
  | zero => simp
  | succ a =>
    cases a with
    | zero => push_cast; norm_num; omega
    | succ k =>
      have h := (central_power_bounds (q : ℤ) (by omega) k).1
      have hq1 : ((q-1 : ℕ) : ℤ) = (q : ℤ)-1 := by omega
      simpa [Nat.cast_mul,Nat.cast_pow,hq1,Nat.cast_add,Nat.add_assoc] using h

theorem central_power_lower_int (q : ℤ) (a : ℕ) (hq : 1 ≤ q) :
    (a*(a-1) : ℕ) * q^(a-2) ≤ (q+1)^a - 2*q^a + (q-1)^a := by
  cases a with
  | zero => simp
  | succ a =>
    cases a with
    | zero => norm_num; omega
    | succ k =>
      simpa [Nat.cast_mul,Nat.cast_add,Nat.add_assoc] using (central_power_bounds q hq k).1

theorem curvature_marked_lower (q : ℤ) (a e : ℕ) (hq : 1 ≤ q)
    (he : e ≤ 2) (h2 : e = 2 → a ≤ 1) :
    2*((q+1)^a*q^e-2*q^(a+e)+(q-1)^(a+e)) ≥
    2*(a*(a-1) : ℕ)*q^(a-2)*q^e -
      2*(e : ℤ)*(q-1)^a*(0 : ℤ)^(e-1) -
      (2*q-1)*(e*(e-1) : ℕ)*(q-1)^a*(0 : ℤ)^(e-2) := by
  have hh := central_power_lower_int q a hq
  interval_cases e
  · norm_num at *
    linarith
  · have hm := mul_le_mul_of_nonneg_left hh (by omega : 0 ≤ q)
    norm_num at *
    simp only [pow_succ] at *
    nlinarith
  · have ha := h2 rfl
    interval_cases a <;> norm_num <;> ring_nf <;> omega

theorem monomial_evaluated_lower (B q a e : ℕ) (hq : 2 ≤ q)
    (he : e ≤ 2) (h2 : e = 2 → a ≤ 1) :
    2*((B*(q+1)^a*q^e : ℕ) - 2*(B*q^a*q^e : ℕ) +
      (B*(q-1)^a*(q-1)^e : ℕ) : ℤ) ≥
    2*(B*a*(a-1)*q^(a-2)*q^e : ℕ) -
      2*(B*e*(q-1)^a*0^(e-1) : ℕ) -
      (2*(q : ℤ)-1)*(B*e*(e-1)*(q-1)^a*0^(e-2) : ℕ) := by
  have h := curvature_marked_lower (q : ℤ) a e (by omega) he h2
  have hm := mul_le_mul_of_nonneg_left h (by positivity : (0 : ℤ) ≤ B)
  have hq1 : ((q-1 : ℕ) : ℤ) = (q : ℤ)-1 := by omega
  convert hm using 1 <;>
    first | rfl | (push_cast; try simp only [hq1,pow_add]; ring)

theorem original_delta_marked_lower (n l : ℕ+) (hn : n.val ≤ 2*(l.val+1)+1) :
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
    (fun P _ => monomial_evaluated_lower (smallBase P (l.val+1)) (l.val+1)
      (largeCount P (l.val+1)) (hitCount P (l.val+1)) hq
      (boundary_hit_bounds P _ hq hn).1 (boundary_hit_bounds P _ hq hn).2)
  have hpred : l.val+1-1 = l.val := by omega
  rw [original_delta_components]
  simp_rw [evalComponents_sum]
  rw [component_UU,component_Y,component_YY]
  rw [hpred] at h
  convert h using 1 <;>
    first | rfl | (simp only [Nat.cast_sum,Nat.cast_mul,Nat.cast_pow,mul_add,mul_sub,
      Finset.sum_sub_distrib,Finset.sum_add_distrib,Finset.mul_sum])

end ParkingForest
