module

public import Parking.NextColumn.Birthday

/-!
# Two inequalities for the homogeneous laws on compositions

Under the homogeneous law with cut factor `h`, a composition of `r` with `j` cuts has weight
`a_r (j+1) h^j S_r(j)`, where `S_r(j) = Pb r (j+1)` is the birthday tail (`Tq_eq`).

* `tau_succ_le`  : "shortening by one",
  `τ_{r+1}(h) ≤ (1+1/r)^r (1 - (1-h)/(2h(r+1)) μ_h) τ_r(h)`; it rests on the comparison
  `Pb_compare` of the birthday tails for `r` and `r+1`.
* `mu0_le_muh`   : lower bound `μ_0(X) ≤ μ_h`, `X = r(1/h - 1)`, for the mean number of cuts `J`.
  It combines the recursion `E J² + (3+X) E J = 2(r-1)` (`bd_recur`) with the inequality
  `E J(J-1) ≤ (3/2)(E J)²` (`bd_negcorr`, a negative correlation statement for a log-concave
  sequence).
-/

@[expose] public section

namespace Parking

open Finset

/-! ### Auxiliary summation lemmas -/

/-- Index shift for a sum whose first and last-plus-one terms vanish. -/
private theorem bd_sum_range_shift (f : ℕ → ℝ) (n : ℕ) (h0 : f 0 = 0) (hn : f n = 0) :
    ∑ i ∈ range n, f i = ∑ i ∈ range n, f (i + 1) := by
  have h1 := Finset.sum_range_succ f n
  have h2 := Finset.sum_range_succ' f n
  rw [hn, add_zero] at h1
  rw [h0, add_zero] at h2
  rw [← h1, h2]

/-! ### `tau` and `muh` in terms of the birthday law -/

private theorem tau_eq_range (m : ℕ) (h : ℝ) :
    tau m h = cay m * ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1) * h ^ i := by
  rw [tau_eq, sum_Icc_one_eq_range, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Tq_eq (by omega : 1 ≤ i + 1), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]
  ring

private theorem muh_num_eq_range (r : ℕ) (h : ℝ) :
    ∑ q ∈ Icc 1 r, ((q : ℝ) - 1) * (Tq r q * h ^ (q - 1))
      = cay r * ∑ i ∈ range r, (i : ℝ) * (((i : ℝ) + 1) * Pb r (i + 1) * h ^ i) := by
  rw [sum_Icc_one_eq_range, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Tq_eq (by omega : 1 ≤ i + 1), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]
  ring

/-! ### Shortening by one -/

/-- The generating polynomial of the birthday law, `Ξ_m = 1 - (1-h) ∑_j h^(j-1) S_m(j)`: this is
the Abel summation `Pb_moment` for the weights `g(q) = h^(q-1)`. -/
private theorem bd_Nsum_eq {m : ℕ} (hm : 1 ≤ m) (h : ℝ) :
    ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1) * h ^ i
      = m * (1 - (1 - h) * ∑ i ∈ range m, h ^ i * Pb m (i + 1 + 1)) := by
  have hM : ∑ i ∈ range m, h ^ (i + 1 - 1) * (((i : ℝ) + 1) * Pb m (i + 1))
      = m * (∑ i ∈ range m, (h ^ (i + 1 - 1) - h ^ (i - 1)) * Pb m (i + 1) + h ^ (0 - 1)) :=
    Pb_moment hm (fun q => h ^ (q - 1))
  have e1 : ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1) * h ^ i
      = ∑ i ∈ range m, h ^ (i + 1 - 1) * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl fun i _ => by
      rw [Nat.add_sub_cancel]
      ring
  have e2 : ∑ i ∈ range m, (h ^ (i + 1 - 1) - h ^ (i - 1)) * Pb m (i + 1)
      = -(1 - h) * ∑ i ∈ range m, h ^ i * Pb m (i + 1 + 1) := by
    rw [bd_sum_range_shift (fun i => (h ^ (i + 1 - 1) - h ^ (i - 1)) * Pb m (i + 1)) m
      (by simp) (by simp [Pb_succ_self hm]), Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    show (h ^ (i + 1 + 1 - 1) - h ^ (i + 1 - 1)) * Pb m (i + 1 + 1)
      = -(1 - h) * (h ^ i * Pb m (i + 1 + 1))
    rw [Nat.add_sub_cancel, Nat.add_sub_cancel]
    ring
  have e0 : h ^ (0 - 1) = 1 := by simp
  rw [e1, hM, e2, e0]
  ring

/-- One step of the comparison of `S_{r+1}(j)` with `S_r(j)` (pure algebra). -/
private theorem bd_compare_step {R K x y α β : ℝ} (hR : 0 < R) (hK : 0 ≤ K) (hx : 0 ≤ x)
    (hα : α * R = R - (K + 1)) (hβ : β * (R + 1) = R - K) (hβ0 : 0 ≤ β)
    (ih : (2 * R * (R + 1) + K * (K + 1)) * x ≤ 2 * R * (R + 1) * y) :
    (2 * R * (R + 1) + (K + 1) * (K + 1 + 1)) * (x * α) ≤ 2 * R * (R + 1) * (y * β) := by
  have hD : ((2 * R * (R + 1) + K * (K + 1)) * β
        - (2 * R * (R + 1) + (K + 1) * (K + 1 + 1)) * α) * (R * (R + 1))
      = (K + 1) ^ 2 * (2 * R + K + 2) := by
    linear_combination ((2 * R * (R + 1) + K * (K + 1)) * R) * hβ
      - ((2 * R * (R + 1) + (K + 1) * (K + 1 + 1)) * (R + 1)) * hα
  have hRR : 0 < R * (R + 1) := mul_pos hR (by linarith)
  have hD0 : (2 * R * (R + 1) + (K + 1) * (K + 1 + 1)) * α
      ≤ (2 * R * (R + 1) + K * (K + 1)) * β := by
    have h2 : 0 ≤ (K + 1) ^ 2 * (2 * R + K + 2) := mul_nonneg (sq_nonneg _) (by linarith)
    refine le_of_mul_le_mul_right ?_ hRR
    linarith
  have h3 := mul_le_mul_of_nonneg_right ih hβ0
  have h4 := mul_le_mul_of_nonneg_left hD0 hx
  nlinarith [h3, h4]

/-- `S_{r+1}(j) ≥ (1 + j(j+1)/(2r(r+1))) S_r(j)` for `j ≤ r`, in cross-multiplied form. -/
private theorem Pb_compare {r : ℕ} (hr : 1 ≤ r) :
    ∀ j : ℕ, j ≤ r →
      (2 * (r : ℝ) * ((r : ℝ) + 1) + (j : ℝ) * ((j : ℝ) + 1)) * Pb r (j + 1)
        ≤ 2 * (r : ℝ) * ((r : ℝ) + 1) * Pb (r + 1) (j + 1) := by
  have hR : (0 : ℝ) < r := Nat.cast_pos.2 (by omega)
  intro j
  induction j with
  | zero =>
    intro _
    have h1 : Pb r (0 + 1) = 1 := Pb_one r
    have h2 : Pb (r + 1) (0 + 1) = 1 := Pb_one (r + 1)
    rw [h1, h2, Nat.cast_zero]
    exact le_of_eq (by ring)
  | succ k ih =>
    intro hk
    have ih' := ih (by omega)
    have hx : 0 ≤ Pb r (k + 1) := Pb_nonneg r (k + 1)
    have hkr : (k : ℝ) + 1 ≤ r := by exact_mod_cast hk
    have hk0 : (0 : ℝ) ≤ k := Nat.cast_nonneg k
    have e1 : Pb r (k + 1 + 1) = Pb r (k + 1) * (1 - ((k : ℝ) + 1) / (r : ℝ)) := by
      rw [Pb_succ r (k + 1), Nat.cast_add, Nat.cast_one]
    have e2 : Pb (r + 1) (k + 1 + 1)
        = Pb (r + 1) (k + 1) * (1 - ((k : ℝ) + 1) / ((r : ℝ) + 1)) := by
      rw [Pb_succ (r + 1) (k + 1)]
      simp only [Nat.cast_add, Nat.cast_one]
    have hα : (1 - ((k : ℝ) + 1) / (r : ℝ)) * (r : ℝ) = (r : ℝ) - ((k : ℝ) + 1) := by
      rw [sub_mul, one_mul, div_mul_cancel₀ _ hR.ne']
    have hR1 : (r : ℝ) + 1 ≠ 0 := by positivity
    have hβ : (1 - ((k : ℝ) + 1) / ((r : ℝ) + 1)) * ((r : ℝ) + 1) = (r : ℝ) - (k : ℝ) := by
      rw [sub_mul, one_mul, div_mul_cancel₀ _ hR1]
      ring
    have hβ0 : 0 ≤ 1 - ((k : ℝ) + 1) / ((r : ℝ) + 1) := by
      have : ((k : ℝ) + 1) / ((r : ℝ) + 1) ≤ 1 := (div_le_one (by linarith)).2 (by linarith)
      linarith
    rw [e1, e2, Nat.cast_add, Nat.cast_one]
    exact bd_compare_step hR hk0 hx hα hβ hβ0 ih'

/-- The final algebra of `tau_succ_le`. -/
private theorem bd_tau_succ_aux {R h A B K ι e : ℝ} (hR : 0 < R) (hh : 0 < h) (hh1 : h ≤ 1)
    (hι : ι * R = 1) (he : e * (2 * h * (R + 1)) = 1 - h)
    (hK : K ≤ 2 * h * R * (R + 1) * (B - A)) :
    (R + 1) * (1 - (1 - h) * B) ≤ (1 + ι) * (R * (1 - (1 - h) * A) - e * K) := by
  have hD : ((1 + ι) * (R * (1 - (1 - h) * A) - e * K) - (R + 1) * (1 - (1 - h) * B))
        * (2 * h * R)
      = (1 - h) * (2 * h * R * (R + 1) * (B - A) - K) := by
    linear_combination (2 * h * R * (1 - (1 - h) * A) - 2 * h * e * K) * hι - K * he
  have h2 : 0 ≤ (1 - h) * (2 * h * R * (R + 1) * (B - A) - K) :=
    mul_nonneg (by linarith) (by linarith)
  have h3 : 0 < 2 * h * R := mul_pos (mul_pos two_pos hh) hR
  refine le_of_mul_le_mul_right ?_ h3
  linarith

/-- **Shortening by one** (birthday-law inequality). For `r ≥ 1`, `0 < h ≤ 1`:
`τ_{r+1}(h) ≤ (1+1/r)^r (1 - (1-h)/(2h(r+1)) μ_h) τ_r(h)`. -/
theorem tau_succ_le {r : ℕ} (hr : 1 ≤ r) {h : ℝ} (hh : 0 < h) (hh1 : h ≤ 1) :
    tau (r + 1) h
      ≤ (1 + 1 / (r : ℝ)) ^ r * (1 - (1 - h) / (2 * h * ((r : ℝ) + 1)) * muh r h) * tau r h := by
  have hR : (0 : ℝ) < r := Nat.cast_pos.2 (by omega)
  obtain ⟨A, hA⟩ : ∃ A : ℝ, A = ∑ i ∈ range r, h ^ i * Pb r (i + 1 + 1) := ⟨_, rfl⟩
  obtain ⟨B, hB⟩ : ∃ B : ℝ, B = ∑ i ∈ range r, h ^ i * Pb (r + 1) (i + 1 + 1) := ⟨_, rfl⟩
  obtain ⟨K, hK⟩ : ∃ K : ℝ,
      K = ∑ i ∈ range r, (i : ℝ) * (((i : ℝ) + 1) * Pb r (i + 1) * h ^ i) := ⟨_, rfl⟩
  have hτ : tau r h = cay r * ((r : ℝ) * (1 - (1 - h) * A)) := by
    rw [tau_eq_range, bd_Nsum_eq hr, ← hA]
  have hτ1 : tau (r + 1) h = cay (r + 1) * (((r : ℝ) + 1) * (1 - (1 - h) * B)) := by
    rw [tau_eq_range, bd_Nsum_eq (by omega : 1 ≤ r + 1), Finset.sum_range_succ,
      Pb_succ_self (by omega : 1 ≤ r + 1), mul_zero, add_zero, Nat.cast_add, Nat.cast_one, ← hB]
  have hμ : muh r h * tau r h = cay r * K := by
    rw [muh_mul_tau hr hh.le, muh_num_eq_range, ← hK]
  have hKle : K ≤ 2 * h * (r : ℝ) * ((r : ℝ) + 1) * (B - A) := by
    have hshift : ∑ i ∈ range r, (i : ℝ) * (((i : ℝ) + 1) * Pb r (i + 1) * h ^ i)
        = ∑ i ∈ range r, ((i + 1 : ℕ) : ℝ)
            * ((((i + 1 : ℕ) : ℝ) + 1) * Pb r (i + 1 + 1) * h ^ (i + 1)) :=
      bd_sum_range_shift (fun i : ℕ => (i : ℝ) * (((i : ℝ) + 1) * Pb r (i + 1) * h ^ i)) r
        (by simp) (by simp [Pb_succ_self hr])
    rw [hK, hshift, hA, hB, ← Finset.sum_sub_distrib, Finset.mul_sum]
    refine Finset.sum_le_sum fun i hi => ?_
    rw [mem_range] at hi
    have hcmp := Pb_compare hr (i + 1) (by omega)
    have hH : 0 ≤ h ^ i * h := mul_nonneg (pow_nonneg hh.le i) hh.le
    have h5 := mul_le_mul_of_nonneg_left hcmp hH
    rw [pow_succ]
    nlinarith [h5]
  have hι : 1 / (r : ℝ) * (r : ℝ) = 1 := div_mul_cancel₀ _ hR.ne'
  have hden : (2 : ℝ) * h * ((r : ℝ) + 1) ≠ 0 :=
    (mul_pos (mul_pos two_pos hh) (by linarith)).ne'
  have he : (1 - h) / (2 * h * ((r : ℝ) + 1)) * (2 * h * ((r : ℝ) + 1)) = 1 - h :=
    div_mul_cancel₀ _ hden
  have haux := bd_tau_succ_aux hR hh hh1 hι he hKle
  have hcay : cay (r + 1) = (1 + 1 / (r : ℝ)) ^ (r - 1) * cay r := cay_ratio (by omega)
  have hp : (1 + 1 / (r : ℝ)) ^ r = (1 + 1 / (r : ℝ)) ^ (r - 1) * (1 + 1 / (r : ℝ)) := by
    rw [← pow_succ, Nat.sub_add_cancel hr]
  have hP : 0 ≤ (1 + 1 / (r : ℝ)) ^ (r - 1) := pow_nonneg (by positivity) _
  have hfin := mul_le_mul_of_nonneg_left haux (mul_nonneg hP (cay_nonneg r))
  calc tau (r + 1) h
      = (1 + 1 / (r : ℝ)) ^ (r - 1) * cay r * (((r : ℝ) + 1) * (1 - (1 - h) * B)) := by
        rw [hτ1, hcay]
    _ ≤ (1 + 1 / (r : ℝ)) ^ (r - 1) * cay r
          * ((1 + 1 / (r : ℝ)) * ((r : ℝ) * (1 - (1 - h) * A)
            - (1 - h) / (2 * h * ((r : ℝ) + 1)) * K)) := hfin
    _ = (1 + 1 / (r : ℝ)) ^ r * (1 - (1 - h) / (2 * h * ((r : ℝ) + 1)) * muh r h)
          * tau r h := by
        rw [hp]
        linear_combination (-((1 + 1 / (r : ℝ)) ^ (r - 1) * (1 + 1 / (r : ℝ)))) * hτ
          + ((1 + 1 / (r : ℝ)) ^ (r - 1) * (1 + 1 / (r : ℝ))
              * ((1 - h) / (2 * h * ((r : ℝ) + 1)))) * hμ

/-! ### The mean bound -/

/-- `v_j = h^j S_r(j)`; the weight of `j` cuts is `w_j = a_r (j+1) v_j`. -/
private noncomputable def bdv (r : ℕ) (h : ℝ) (j : ℕ) : ℝ := h ^ j * Pb r (j + 1)

private theorem bdv_nonneg (r : ℕ) {h : ℝ} (hh : 0 ≤ h) (j : ℕ) : 0 ≤ bdv r h j :=
  mul_nonneg (pow_nonneg hh j) (Pb_nonneg r (j + 1))

private theorem bdv_eq_zero {r : ℕ} (hr : 1 ≤ r) (h : ℝ) {j : ℕ} (hj : r ≤ j) : bdv r h j = 0 := by
  unfold bdv
  rw [Pb_eq_zero hr (by omega), mul_zero]

private theorem bdv_succ (r : ℕ) (h : ℝ) (j : ℕ) :
    bdv r h (j + 1) = h * (1 - ((j : ℝ) + 1) / r) * bdv r h j := by
  unfold bdv
  rw [Pb_succ r (j + 1), pow_succ, Nat.cast_add, Nat.cast_one]
  ring

/-- A nonnegative sequence with nonincreasing consecutive ratios is log-concave
(cross-multiplied form, zeros allowed). -/
private theorem bd_logconc (v ρ : ℕ → ℝ) (hv : ∀ j, 0 ≤ v j) (hρ : ∀ a b, a ≤ b → ρ b ≤ ρ a)
    (hrec : ∀ j, v (j + 1) = ρ j * v j) :
    ∀ d a b, a ≤ b → v a * v (b + d) ≤ v (a + d) * v b := by
  intro d
  induction d with
  | zero =>
    intro a b _
    exact le_refl _
  | succ d ih =>
    intro a b hab
    have h1 := ih a b hab
    rw [← Nat.add_assoc, ← Nat.add_assoc, hrec (b + d), hrec (a + d)]
    rcases le_or_gt 0 (ρ (b + d)) with hneg | hneg
    · have h2 : ρ (b + d) ≤ ρ (a + d) := hρ _ _ (by omega)
      have h3 : 0 ≤ v (a + d) * v b := mul_nonneg (hv _) (hv _)
      calc v a * (ρ (b + d) * v (b + d)) = ρ (b + d) * (v a * v (b + d)) := by ring
        _ ≤ ρ (b + d) * (v (a + d) * v b) := mul_le_mul_of_nonneg_left h1 hneg
        _ ≤ ρ (a + d) * (v (a + d) * v b) := mul_le_mul_of_nonneg_right h2 h3
        _ = ρ (a + d) * v (a + d) * v b := by ring
    · have h4 : ρ (b + d) * v (b + d) = 0 := by
        have h5 : 0 ≤ v (b + d + 1) := hv _
        rw [hrec] at h5
        have h6 : ρ (b + d) * v (b + d) ≤ 0 :=
          mul_nonpos_of_nonpos_of_nonneg hneg.le (hv _)
        linarith
      rw [h4, mul_zero]
      have h7 : 0 ≤ v (a + d + 1) := hv _
      rw [hrec] at h7
      exact mul_nonneg h7 (hv _)

private theorem bdv_logconc {r : ℕ} (hr : 1 ≤ r) {h : ℝ} (hh : 0 ≤ h) :
    ∀ d a b, a ≤ b → bdv r h a * bdv r h (b + d) ≤ bdv r h (a + d) * bdv r h b := by
  have hR : (0 : ℝ) < r := Nat.cast_pos.2 (by omega)
  refine bd_logconc (bdv r h) (fun j => h * (1 - ((j : ℝ) + 1) / r)) (bdv_nonneg r hh) ?_
    (bdv_succ r h)
  intro a b hab
  have hab' : (a : ℝ) ≤ b := Nat.cast_le.2 hab
  have h1 : ((a : ℝ) + 1) / r ≤ ((b : ℝ) + 1) / r :=
    (div_le_div_iff_of_pos_right hR).2 (by linarith)
  show h * (1 - ((b : ℝ) + 1) / r) ≤ h * (1 - ((a : ℝ) + 1) / r)
  exact mul_le_mul_of_nonneg_left (by linarith) hh

/-- Summation along the diagonals `i + l = j` of a square, for a sequence vanishing beyond `r`. -/
private theorem bd_diag {r : ℕ} (v : ℕ → ℝ) (hv0 : ∀ j, r ≤ j → v j = 0) (g : ℕ → ℕ → ℝ) (G : ℕ → ℝ)
    (hG : ∀ j, ∑ k ∈ range (j + 1), g k (j - k) = G j) :
    ∑ i ∈ range r, ∑ l ∈ range r, v (i + l) * g i l = ∑ j ∈ range r, v j * G j := by
  have h1 : ∀ i ∈ range r, ∑ l ∈ range r, v (i + l) * g i l
      = ∑ l ∈ range (r - i), v (i + l) * g i l := by
    intro i _
    symm
    refine Finset.sum_subset (Finset.range_subset_range.2 (Nat.sub_le r i)) ?_
    intro l _ hl
    rw [mem_range] at hl
    rw [hv0 (i + l) (by omega), zero_mul]
  have h2 : ∑ j ∈ range r, ∑ k ∈ range (j + 1), v (k + (j - k)) * g k (j - k)
      = ∑ i ∈ range r, ∑ l ∈ range (r - i), v (i + l) * g i l :=
    Finset.sum_range_diag_flip r (fun i l => v (i + l) * g i l)
  rw [Finset.sum_congr rfl h1, ← h2]
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [← hG j, Finset.mul_sum]
  refine Finset.sum_congr rfl fun k hk => ?_
  rw [mem_range] at hk
  rw [Nat.add_sub_of_le (by omega : k ≤ j)]

private theorem bd_sum_one (j : ℕ) : ∑ _k ∈ range (j + 1), (1 : ℝ) = (j : ℝ) + 1 := by
  rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul, mul_one, Nat.cast_add, Nat.cast_one]

private theorem bd_sum_id (j : ℕ) : ∑ k ∈ range (j + 1), (k : ℝ) = (j : ℝ) * ((j : ℝ) + 1) / 2 := by
  induction j with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih, Nat.cast_add, Nat.cast_one]
    ring

private theorem bd_sum_sq (j : ℕ) :
    ∑ k ∈ range (j + 1), (k : ℝ) ^ 2 = (j : ℝ) * ((j : ℝ) + 1) * (2 * (j : ℝ) + 1) / 6 := by
  induction j with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih, Nat.cast_add, Nat.cast_one]
    ring

private theorem bd_sum_sub (j : ℕ) :
    ∑ k ∈ range (j + 1), ((j - k : ℕ) : ℝ) = (j : ℝ) * ((j : ℝ) + 1) / 2 := by
  have h1 : ∀ k ∈ range (j + 1), ((j - k : ℕ) : ℝ) = (j : ℝ) - (k : ℝ) := by
    intro k hk
    rw [mem_range] at hk
    exact Nat.cast_sub (by omega)
  rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib, bd_sum_id, Finset.sum_const,
    Finset.card_range, nsmul_eq_mul, Nat.cast_add, Nat.cast_one]
  ring

private theorem bd_sum_sub_mul (j : ℕ) :
    ∑ k ∈ range (j + 1), ((j - k : ℕ) : ℝ) * (k : ℝ)
      = ((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6 := by
  have h1 : ∀ k ∈ range (j + 1), ((j - k : ℕ) : ℝ) * (k : ℝ)
      = (j : ℝ) * (k : ℝ) - (k : ℝ) ^ 2 := by
    intro k hk
    rw [mem_range] at hk
    rw [Nat.cast_sub (by omega : k ≤ j)]
    ring
  rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib, ← Finset.mul_sum, bd_sum_id, bd_sum_sq]
  ring

/-- Negative correlation of the two coordinates under the weight `W(i,l) = v_{i+l}` on a square,
for a log-concave `v`:  `E[I L] ≤ E[I] E[L]`, written with the diagonal sums. -/
private theorem bd_negcorr {r : ℕ} (v : ℕ → ℝ) (hv0 : ∀ j, r ≤ j → v j = 0)
    (hlc : ∀ d a b, a ≤ b → v a * v (b + d) ≤ v (a + d) * v b) :
    (∑ j ∈ range r, v j * (((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6))
        * (∑ j ∈ range r, v j * ((j : ℝ) + 1))
      ≤ (∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2))
        * (∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2)) := by
  have hinner : ∀ i ∈ range r, ∀ i' ∈ range r, i ≤ i' →
      (∑ l ∈ range r, v (i' + l) * (l : ℝ)) * (∑ l ∈ range r, v (i + l))
        ≤ (∑ l ∈ range r, v (i + l) * (l : ℝ)) * (∑ l ∈ range r, v (i' + l)) := by
    intro i _ i' _ hii'
    refine lr_sum_le_finset (range r) (fun l => v (i' + l)) (fun l => v (i + l))
      (fun l => (l : ℝ)) ?_ ?_
    · intro l _ l' _ hll'
      obtain ⟨d, rfl⟩ := Nat.exists_eq_add_of_le hll'
      have h1 := hlc d (i + l) (i' + l) (by omega)
      show v (i' + (l + d)) * v (i + l) ≤ v (i' + l) * v (i + (l + d))
      rw [← Nat.add_assoc, ← Nat.add_assoc]
      linarith [h1]
    · intro l _ l' _ hll'
      exact Nat.cast_le.2 hll'
  have houter : (∑ i ∈ range r, (∑ l ∈ range r, v (i + l) * (l : ℝ)) * (i : ℝ))
        * (∑ i ∈ range r, ∑ l ∈ range r, v (i + l))
      ≤ (∑ i ∈ range r, (∑ l ∈ range r, v (i + l)) * (i : ℝ))
        * (∑ i ∈ range r, ∑ l ∈ range r, v (i + l) * (l : ℝ)) :=
    lr_sum_le_finset (range r) (fun i => ∑ l ∈ range r, v (i + l) * (l : ℝ))
      (fun i => ∑ l ∈ range r, v (i + l)) (fun i => (i : ℝ)) hinner
      (fun i _ i' _ hii' => Nat.cast_le.2 hii')
  have d00 : ∑ i ∈ range r, ∑ l ∈ range r, v (i + l) = ∑ j ∈ range r, v j * ((j : ℝ) + 1) := by
    have e := bd_diag v hv0 (fun _ _ => (1 : ℝ)) (fun j => (j : ℝ) + 1) bd_sum_one
    rw [← e]
    refine Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun l _ => ?_
    exact (mul_one _).symm
  have d01 : ∑ i ∈ range r, ∑ l ∈ range r, v (i + l) * (l : ℝ)
      = ∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2) :=
    bd_diag v hv0 (fun _ l => (l : ℝ)) (fun j => (j : ℝ) * ((j : ℝ) + 1) / 2) bd_sum_sub
  have d10 : ∑ i ∈ range r, (∑ l ∈ range r, v (i + l)) * (i : ℝ)
      = ∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2) := by
    have e := bd_diag v hv0 (fun i _ => (i : ℝ)) (fun j => (j : ℝ) * ((j : ℝ) + 1) / 2) bd_sum_id
    rw [← e]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [Finset.sum_mul]
  have d11 : ∑ i ∈ range r, (∑ l ∈ range r, v (i + l) * (l : ℝ)) * (i : ℝ)
      = ∑ j ∈ range r, v j * (((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6) := by
    have e := bd_diag v hv0 (fun i l => (l : ℝ) * (i : ℝ))
      (fun j => ((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6) bd_sum_sub_mul
    rw [← e]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [Finset.sum_mul]
    exact Finset.sum_congr rfl fun l _ => mul_assoc _ _ _
  calc (∑ j ∈ range r, v j * (((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6))
        * (∑ j ∈ range r, v j * ((j : ℝ) + 1))
      = (∑ i ∈ range r, (∑ l ∈ range r, v (i + l) * (l : ℝ)) * (i : ℝ))
        * (∑ i ∈ range r, ∑ l ∈ range r, v (i + l)) := by rw [d11, d00]
    _ ≤ (∑ i ∈ range r, (∑ l ∈ range r, v (i + l)) * (i : ℝ))
        * (∑ i ∈ range r, ∑ l ∈ range r, v (i + l) * (l : ℝ)) := houter
    _ = (∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2))
        * (∑ j ∈ range r, v j * ((j : ℝ) * ((j : ℝ) + 1) / 2)) := by rw [d10, d01]

/-- The recursion `r (j+1) w_{j+1} = h (j+2)(r-1-j) w_j`, summed over `j`:
`r E J = h (2(r-1) + (r-3) E J - E J²)` (before normalisation). -/
private theorem bd_recur {r : ℕ} (hr : 1 ≤ r) (h : ℝ) :
    (r : ℝ) * ∑ j ∈ range r, (j : ℝ) * (((j : ℝ) + 1) * bdv r h j)
      = h * (2 * ((r : ℝ) - 1) * ∑ j ∈ range r, ((j : ℝ) + 1) * bdv r h j
          + ((r : ℝ) - 3) * ∑ j ∈ range r, (j : ℝ) * (((j : ℝ) + 1) * bdv r h j)
          - ∑ j ∈ range r, (j : ℝ) ^ 2 * (((j : ℝ) + 1) * bdv r h j)) := by
  have hR : (r : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
  have hshift : ∑ j ∈ range r, (j : ℝ) * (((j : ℝ) + 1) * bdv r h j)
      = ∑ j ∈ range r, ((j + 1 : ℕ) : ℝ) * ((((j + 1 : ℕ) : ℝ) + 1) * bdv r h (j + 1)) :=
    bd_sum_range_shift (fun j : ℕ => (j : ℝ) * (((j : ℝ) + 1) * bdv r h j)) r (by simp)
      (by simp [bdv_eq_zero hr h (le_refl r)])
  have hterm : ∀ j ∈ range r,
      (r : ℝ) * (((j + 1 : ℕ) : ℝ) * ((((j + 1 : ℕ) : ℝ) + 1) * bdv r h (j + 1)))
        = h * (2 * ((r : ℝ) - 1) * (((j : ℝ) + 1) * bdv r h j)
            + ((r : ℝ) - 3) * ((j : ℝ) * (((j : ℝ) + 1) * bdv r h j))
            - (j : ℝ) ^ 2 * (((j : ℝ) + 1) * bdv r h j)) := by
    intro j _
    have hd : ((j : ℝ) + 1) / (r : ℝ) * (r : ℝ) = (j : ℝ) + 1 := div_mul_cancel₀ _ hR
    rw [bdv_succ, Nat.cast_add, Nat.cast_one]
    linear_combination (-(((j : ℝ) + 1) * ((j : ℝ) + 2) * h * bdv r h j)) * hd
  have hmain : (r : ℝ) * ∑ j ∈ range r,
        ((j + 1 : ℕ) : ℝ) * ((((j + 1 : ℕ) : ℝ) + 1) * bdv r h (j + 1))
      = h * (2 * ((r : ℝ) - 1) * ∑ j ∈ range r, ((j : ℝ) + 1) * bdv r h j
          + ((r : ℝ) - 3) * ∑ j ∈ range r, (j : ℝ) * (((j : ℝ) + 1) * bdv r h j)
          - ∑ j ∈ range r, (j : ℝ) ^ 2 * (((j : ℝ) + 1) * bdv r h j)) := by
    rw [Finset.mul_sum, Finset.sum_congr rfl hterm, ← Finset.mul_sum]
    congr 1
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib, ← Finset.sum_sub_distrib]
  rw [← hshift] at hmain
  exact hmain

/-- From the quadratic inequality `2(r-1) ≤ (3/2) μ² + (4+X) μ` to `μ_0(X) ≤ μ`: the hypothesis says
`(4+X)² + 12(r-1) ≤ (3μ + 4 + X)²`. -/
private theorem mu0_le_of_quad {r : ℕ} {X μ : ℝ} (hX : 0 ≤ X) (hμ : 0 ≤ μ)
    (hE : 2 * ((r : ℝ) - 1) ≤ 3 / 2 * μ ^ 2 + (4 + X) * μ) : mu0 r X ≤ μ := by
  have h1 : Real.sqrt ((4 + X) ^ 2 + 12 * ((r : ℝ) - 1)) ≤ 3 * μ + (4 + X) :=
    (Real.sqrt_le_left (by linarith)).2 (by linarith)
  unfold mu0
  linarith

/-- Lower bound for the mean number of cuts: `μ_h ≥ μ_0(X)`, `X = r(1/h - 1)`. -/
theorem mu0_le_muh {r : ℕ} (hr : 1 ≤ r) {h : ℝ} (hh : 0 < h) (hh1 : h ≤ 1) :
    mu0 r ((r : ℝ) * (1 / h - 1)) ≤ muh r h := by
  have hR : (0 : ℝ) < r := Nat.cast_pos.2 (by omega)
  obtain ⟨m0, hm0⟩ : ∃ m0 : ℝ, m0 = ∑ j ∈ range r, ((j : ℝ) + 1) * bdv r h j := ⟨_, rfl⟩
  obtain ⟨m1, hm1⟩ : ∃ m1 : ℝ,
      m1 = ∑ j ∈ range r, (j : ℝ) * (((j : ℝ) + 1) * bdv r h j) := ⟨_, rfl⟩
  obtain ⟨m2, hm2⟩ : ∃ m2 : ℝ,
      m2 = ∑ j ∈ range r, (j : ℝ) ^ 2 * (((j : ℝ) + 1) * bdv r h j) := ⟨_, rfl⟩
  have hτ : tau r h = cay r * m0 := by
    rw [tau_eq_range, hm0]
    congr 1
    exact Finset.sum_congr rfl fun j _ => by unfold bdv; ring
  have hμτ : muh r h * tau r h = cay r * m1 := by
    rw [muh_mul_tau hr hh.le, muh_num_eq_range, hm1]
    congr 1
    exact Finset.sum_congr rfl fun j _ => by unfold bdv; ring
  have hc : 0 < cay r := cay_pos (by omega)
  have hτpos : 0 < tau r h := tau_pos hr hh.le
  have hm0pos : 0 < m0 := by
    rw [hτ] at hτpos
    exact pos_of_mul_pos_right hτpos hc.le
  have hμm : muh r h * m0 = m1 := by
    rw [hτ] at hμτ
    have h1 : cay r * (muh r h * m0) = cay r * m1 := by
      rw [← hμτ]
      ring
    exact mul_left_cancel₀ hc.ne' h1
  have hι : 1 / h * h = 1 := div_mul_cancel₀ _ hh.ne'
  -- (a) the recursion
  have ha := bd_recur hr h
  rw [← hm0, ← hm1, ← hm2] at ha
  -- (b) negative correlation
  have hb := bd_negcorr (bdv r h) (fun j hj => bdv_eq_zero hr h hj) (bdv_logconc hr hh.le)
  have e11 : ∑ j ∈ range r, bdv r h j * (((j : ℝ) - 1) * (j : ℝ) * ((j : ℝ) + 1) / 6)
      = 1 / 6 * (m2 - m1) := by
    rw [hm2, hm1, ← Finset.sum_sub_distrib, Finset.mul_sum]
    exact Finset.sum_congr rfl fun j _ => by ring
  have e00 : ∑ j ∈ range r, bdv r h j * ((j : ℝ) + 1) = m0 := by
    rw [hm0]
    exact Finset.sum_congr rfl fun j _ => by ring
  have e10 : ∑ j ∈ range r, bdv r h j * ((j : ℝ) * ((j : ℝ) + 1) / 2) = 1 / 2 * m1 := by
    rw [hm1, Finset.mul_sum]
    exact Finset.sum_congr rfl fun j _ => by ring
  rw [e11, e00, e10] at hb
  -- (c) combine
  have ha' : h * m2 * m0
      = (h * (2 * ((r : ℝ) - 1) * m0 + ((r : ℝ) - 3) * m1) - (r : ℝ) * m1) * m0 := by
    linear_combination m0 * ha
  have hb' := mul_le_mul_of_nonneg_left hb (mul_nonneg (by norm_num : (0 : ℝ) ≤ 6) hh.le)
  have hpos : 0 ≤ 3 / 2 * h * m1 ^ 2 + (4 * h + (r : ℝ) - (r : ℝ) * h) * m1 * m0
      - 2 * ((r : ℝ) - 1) * h * m0 ^ 2 := by
    nlinarith [hb', ha']
  have hEq : (3 / 2 * muh r h ^ 2 + (4 + (r : ℝ) * (1 / h - 1)) * muh r h
        - 2 * ((r : ℝ) - 1)) * (h * m0 ^ 2)
      = 3 / 2 * h * m1 ^ 2 + (4 * h + (r : ℝ) - (r : ℝ) * h) * m1 * m0
        - 2 * ((r : ℝ) - 1) * h * m0 ^ 2 := by
    linear_combination
      (3 / 2 * h * (muh r h * m0 + m1) + (4 + (r : ℝ) * (1 / h - 1)) * h * m0) * hμm
        + ((r : ℝ) * m1 * m0) * hι
  have hE : 2 * ((r : ℝ) - 1)
      ≤ 3 / 2 * muh r h ^ 2 + (4 + (r : ℝ) * (1 / h - 1)) * muh r h := by
    have hhm : 0 < h * m0 ^ 2 := mul_pos hh (pow_pos hm0pos 2)
    refine le_of_mul_le_mul_right ?_ hhm
    linarith
  have hX : 0 ≤ (r : ℝ) * (1 / h - 1) := by
    have h9 : 1 ≤ 1 / h := (le_div_iff₀ hh).2 (by linarith)
    exact mul_nonneg hR.le (by linarith)
  exact mu0_le_of_quad hX (muh_nonneg hr hh.le) hE

/-! ### The explicit lower bound `μ_0` -/

/-- The explicit bound $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2 + 12(r-1)} - (4+X)\bigr)/3$ is nonnegative
for $r \ge 1$ and $X \ge 0$. -/
theorem mu0_nonneg {r : ℕ} (hr : 1 ≤ r) {X : ℝ} (hX : 0 ≤ X) : 0 ≤ mu0 r X := by
  have hr' : (1 : ℝ) ≤ r := by exact_mod_cast hr
  have h2 : 4 + X ≤ Real.sqrt ((4 + X) ^ 2 + 12 * ((r : ℝ) - 1)) :=
    (Real.le_sqrt' (by linarith)).2 (by linarith)
  unfold mu0
  exact div_nonneg (by linarith) (by norm_num)

end Parking
