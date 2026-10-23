import CanonicalForest

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
namespace ParkingForest
open Parking ParkingLastCar ParkingSkeleton

/-- The actual forest sum in the canonical definition, at natural parameters. -/
def canonicalSkeleton (n x c : ℕ) : ℕ :=
  ∑ G : ParentForest n, ∏v : Fin n, boxWeight x c (subtreeSize G v)

theorem canonicalSkeleton_eq (n x c : ℕ) :
    canonicalSkeleton n x c = skeletonEval x c n := parent_forest_sum_eq_weightedEval _ n

def canonicalGammaPlus (n l : ℕ+) : ℤ :=
  (A n (l+1) : ℤ) - 2*(A n l : ℤ) + (canonicalSkeleton n (l+1) l : ℤ)

def canonicalGammaMinus (n l : ℕ+) : ℤ :=
  (canonicalSkeleton n (l+1) l : ℤ) - (A n (l-1) : ℤ)

theorem canonicalGammaPlus_eq (n l : ℕ+) :
    canonicalGammaPlus n l = gammaPlus n l := by
  simp only [canonicalGammaPlus,canonicalSkeleton_eq,gammaPlus]

theorem canonicalGammaMinus_eq (n l : ℕ+) :
    canonicalGammaMinus n l = gammaMinus n l := by
  simp only [canonicalGammaMinus,canonicalSkeleton_eq,gammaMinus]

theorem canonicalGammaPlus_nonneg (n l : ℕ+) : 0 ≤ canonicalGammaPlus n l := by
  rw [canonicalGammaPlus_eq]
  exact gammaPlus_nonneg _ _

theorem canonicalGammaMinus_nonneg (n l : ℕ+) : 0 ≤ canonicalGammaMinus n l := by
  rw [canonicalGammaMinus_eq]
  exact gammaMinus_nonneg _ _ l.pos

theorem original_A_pos (n l : ℕ) : 0 < A n l := by
  induction n with
  | zero => simp [A_empty]
  | succ n ih =>
    rw [A_recurrence]
    have hm : min (0+1) (l+1) = 1 := by omega
    have ht : 0 < n.choose 0 * min (0+1) (l+1) * A 0 l * A (n-0) l := by
      simpa [hm,A_empty] using ih
    exact lt_of_lt_of_le ht (Finset.single_le_sum
      (f := fun k => n.choose k * min (k+1) (l+1) * A k l * A (n-k) l)
      (fun _ _ => Nat.zero_le _)
      (Finset.mem_range.mpr (show 0 < n+1 by omega)))

def normalizedGain (n l : ℕ+) : ℚ :=
  ((l.val+1 : ℚ)^2) * (canonicalGammaPlus n l : ℚ) / (A n l : ℚ)

def normalizedLoss (n l : ℕ+) : ℚ :=
  ((l.val+1 : ℚ)^2) * (canonicalGammaMinus n l : ℚ) / (A n l : ℚ)

theorem normalizedGain_eq (n l : ℕ+) :
    normalizedGain n l = ((l.val+1 : ℚ)^2) * (gammaPlus n l : ℚ) / (A n l : ℚ) := by
  rw [normalizedGain,canonicalGammaPlus_eq]

theorem normalizedLoss_eq (n l : ℕ+) :
    normalizedLoss n l = ((l.val+1 : ℚ)^2) * (gammaMinus n l : ℚ) / (A n l : ℚ) := by
  rw [normalizedLoss,canonicalGammaMinus_eq]

def delta (n l : ℕ+) : ℤ := (b n (l+1) : ℤ) - (b n l : ℤ)

theorem delta_gain_loss (n l : ℕ+) :
    delta n l = canonicalGammaPlus n l - canonicalGammaMinus n l := by
  rw [canonicalGammaPlus_eq,canonicalGammaMinus_eq]
  exact original_gain_minus_loss n l l.pos

theorem normalization_factor_pos (n l : ℕ+) :
    0 < (A n l : ℚ) / ((l.val+1 : ℚ)^2) := by
  apply div_pos
  · exact_mod_cast original_A_pos n l
  · positivity

theorem delta_normalized (n l : ℕ+) :
    (delta n l : ℚ) = ((A n l : ℚ) / ((l.val+1 : ℚ)^2)) *
      (normalizedGain n l - normalizedLoss n l) := by
  have hA : (A n l : ℚ) ≠ 0 := ne_of_gt (by exact_mod_cast original_A_pos n l)
  have hL : (l.val+1 : ℚ) ≠ 0 := by positivity
  rw [delta_gain_loss]
  push_cast
  unfold normalizedGain normalizedLoss
  field_simp
  <;> ring

theorem delta_pos_iff (n l : ℕ+) :
    0 < delta n l ↔ normalizedLoss n l < normalizedGain n l := by
  have he := delta_normalized n l
  have hp := normalization_factor_pos n l
  have hc : (0 : ℚ) < (delta n l : ℚ) ↔ normalizedLoss n l < normalizedGain n l := by
    rw [he]
    exact (mul_pos_iff_of_pos_left hp).trans sub_pos
  exact (by exact_mod_cast hc)

theorem delta_nonpos_iff (n l : ℕ+) :
    delta n l ≤ 0 ↔ normalizedGain n l ≤ normalizedLoss n l := by
  have hc : ((delta n l : ℤ) : ℚ) ≤ 0 ↔ normalizedGain n l ≤ normalizedLoss n l := by
    rw [delta_normalized]
    have hp := normalization_factor_pos n l
    constructor
    · intro h
      by_contra hh
      have hd : 0 < normalizedGain n l - normalizedLoss n l := by linarith
      have hmul := mul_pos hp hd
      linarith
    · intro h
      exact mul_nonpos_of_nonneg_of_nonpos (le_of_lt hp) (sub_nonpos.mpr h)
  exact (by exact_mod_cast hc)

theorem delta_neg_iff (n l : ℕ+) :
    delta n l < 0 ↔ normalizedGain n l < normalizedLoss n l := by
  have hc : ((delta n l : ℤ) : ℚ) < 0 ↔ normalizedGain n l < normalizedLoss n l := by
    rw [delta_normalized]
    have hp := normalization_factor_pos n l
    constructor
    · intro h
      by_contra hh
      have hd : 0 ≤ normalizedGain n l - normalizedLoss n l := by linarith
      have hmul := mul_nonneg (le_of_lt hp) hd
      linarith
    · intro h
      exact mul_neg_of_pos_of_neg hp (sub_neg.mpr h)
  exact (by exact_mod_cast hc)

/-- A sufficient implication for U at this fixed n. Its monotonicity and early
    positivity hypotheses are not proved here. All later indices are covered. -/
theorem U_of_normalized_monotonicity (n : ℕ+) (hn : 19 ≤ n.val) (l0 : ℕ)
    (h0 : n.val/2 ≤ l0) (h1 : l0 ≤ n.val-2)
    (hpre : ∀l : ℕ+, n.val/2 ≤ l.val → l.val < l0 → 0 < delta n l)
    (hg : ∀l : ℕ+, l0 ≤ l.val → l.val < n.val-2 →
      normalizedGain n (l+1) ≤ normalizedGain n l)
    (hloss : ∀l : ℕ+, l0 ≤ l.val → l.val < n.val-2 →
      normalizedLoss n l ≤ normalizedLoss n (l+1)) :
    ∀i j : ℕ, n.val/2 ≤ i → i < j → j < n.val-1 →
      b n (i+1) < b n i → b n (j+1) ≤ b n j := by
  intro i j hi hij hj hneg
  have hhalf : 1 ≤ n.val/2 := by omega
  have hip : 0 < i := by omega
  have hjp : 0 < j := by omega
  have hdi : delta n ⟨i,hip⟩ < 0 := by dsimp [delta]; omega
  have h0i : l0 ≤ i := by
    by_contra hh
    have hp := hpre ⟨i,hip⟩ hi (by change i < l0; omega)
    omega
  have hdif : normalizedGain n ⟨i,hip⟩ - normalizedLoss n ⟨i,hip⟩ < 0 := by
    exact sub_neg.mpr ((delta_neg_iff n ⟨i,hip⟩).mp hdi)
  have hchain : ∀ d : ℕ, i+d ≤ n.val-2 →
      normalizedGain n ⟨i+d,by omega⟩ - normalizedLoss n ⟨i+d,by omega⟩ ≤
      normalizedGain n ⟨i,hip⟩ - normalizedLoss n ⟨i,hip⟩ := by
    intro d
    induction d with
    | zero => intro _; exact le_rfl
    | succ d ih =>
      intro hd
      have hdd : i+d < n.val-2 := by omega
      have hgg := hg ⟨i+d,by omega⟩ (by change l0 ≤ i+d; omega) hdd
      have hll := hloss ⟨i+d,by omega⟩ (by change l0 ≤ i+d; omega) hdd
      have ihh := ih (by omega)
      have hstep : normalizedGain n ⟨i+(d+1),by omega⟩ - normalizedLoss n ⟨i+(d+1),by omega⟩ ≤
          normalizedGain n ⟨i+d,by omega⟩ - normalizedLoss n ⟨i+d,by omega⟩ := by
        have hgg' : normalizedGain n ⟨i+(d+1),by omega⟩ ≤ normalizedGain n ⟨i+d,by omega⟩ := hgg
        have hll' : normalizedLoss n ⟨i+d,by omega⟩ ≤ normalizedLoss n ⟨i+(d+1),by omega⟩ := hll
        linarith
      exact hstep.trans ihh
  have hjj := hchain (j-i) (by omega)
  have hsub : i+(j-i) = j := by omega
  simp only [hsub] at hjj
  have hgj : normalizedGain n ⟨j,hjp⟩ < normalizedLoss n ⟨j,hjp⟩ := by linarith
  have hdj := (delta_neg_iff n ⟨j,hjp⟩).mpr hgj
  dsimp [delta] at hdj
  omega

end ParkingForest
