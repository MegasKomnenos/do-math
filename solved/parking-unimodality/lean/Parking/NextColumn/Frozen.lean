import Parking.Counting.Columns
import Parking.NextColumn.Compositions

/-!
# The frozen polynomial in the single-chain range

`Kpoly k n y` is a polynomial in `y` (the frozen polynomial `K_{n,k}(y)`): the chain expansion
`κ_k(N) + ∑_m κ_k(N-m)/(N-m) · y · Λ_m(y;N)`, `N = n+1`.  For `n ≤ 2k+1` and a level
`j ∈ {k, k+1}` the column sum `zr j` satisfies a Volterra equation (`zr_volterra`, from the
single-chain formula `IsWSol.fwd`), whose solution is this chain expansion (`volterra_chain`), so
`zr j n = Kpoly k n j` (`zr_eq_Kpoly`).  Two consecutive levels differ by the knot identity
`Kpoly_knot`.  The main statement is `dq_frozen`: the two steps `d_{n,k}`, `d_{n,k+1}` as
"curvature minus boundary".
-/

namespace Parking

open Finset

/-- `κ_k(t) = a_t - ∑_{k < i < t} a_i a_{t-i}`. -/
noncomputable def kap (k t : ℕ) : ℝ := cay t - ∑ i ∈ Ioo k t, cay i * cay (t - i)

/-- Reflection `i ↦ b - i` of a sum over an open interval. -/
private theorem sum_Ioo_reflect (F : ℕ → ℝ) (a b : ℕ) :
    ∑ i ∈ Ioo a b, F i = ∑ j ∈ Ioo 0 (b - a), F (b - j) := by
  refine Finset.sum_nbij' (fun i => b - i) (fun j => b - j) ?_ ?_ ?_ ?_ ?_
  · intro i hi
    simp only [mem_Ioo] at hi ⊢
    omega
  · intro j hj
    simp only [mem_Ioo] at hj ⊢
    omega
  · intro i hi
    simp only [mem_Ioo] at hi
    show b - (b - i) = i
    omega
  · intro j hj
    simp only [mem_Ioo] at hj
    show b - (b - j) = j
    omega
  · intro i hi
    simp only [mem_Ioo] at hi
    show F i = F (b - (b - i))
    rw [show b - (b - i) = i by omega]

/-- `κ_k(t) > 0` for `1 ≤ t ≤ 2k+1`: the indices `k < i < t` and their reflections `t - i` are
disjoint, so the sum is at most half of the full convolution `∑_i a_i a_{t-i} = 2(t-1)/t · a_t`. -/
theorem kap_pos {k t : ℕ} (ht1 : 1 ≤ t) (ht2 : t ≤ 2 * k + 1) : 0 < kap k t := by
  have hsym := cay_conv_sym t
  have ht : (0 : ℝ) < (t : ℝ) := Nat.cast_pos.mpr (by omega)
  have hc : 0 < cay t := cay_pos (by omega)
  -- the reflection `i ↦ t - i` maps `Ioo k t` onto `Ioo 0 (t - k)`
  have hrefl : ∑ i ∈ Ioo k t, cay i * cay (t - i)
      = ∑ j ∈ Ioo 0 (t - k), cay j * cay (t - j) := by
    rw [sum_Ioo_reflect (fun i => cay i * cay (t - i)) k t]
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [mem_Ioo] at hj
    show cay (t - j) * cay (t - (t - j)) = cay j * cay (t - j)
    rw [show t - (t - j) = j by omega, mul_comm]
  have hdisj : Disjoint (Ioo k t) (Ioo 0 (t - k)) := by
    rw [Finset.disjoint_left]
    intro i hi hi'
    rw [mem_Ioo] at hi hi'
    omega
  have hsub : Ioo k t ∪ Ioo 0 (t - k) ⊆ range (t + 1) := by
    intro i hi
    rw [mem_union, mem_Ioo, mem_Ioo] at hi
    rw [mem_range]
    omega
  have hle : ∑ i ∈ Ioo k t ∪ Ioo 0 (t - k), cay i * cay (t - i)
      ≤ ∑ i ∈ range (t + 1), cay i * cay (t - i) :=
    Finset.sum_le_sum_of_subset_of_nonneg hsub
      (fun i _ _ => mul_nonneg (cay_nonneg _) (cay_nonneg _))
  rw [Finset.sum_union hdisj, ← hrefl] at hle
  have h2 : (t : ℝ) * (∑ i ∈ Ioo k t, cay i * cay (t - i) + ∑ i ∈ Ioo k t, cay i * cay (t - i))
      ≤ 2 * ((t : ℝ) - 1) * cay t := by
    rw [← hsym]
    exact mul_le_mul_of_nonneg_left hle ht.le
  unfold kap
  have h3 : 0 < (t : ℝ) * (cay t - ∑ i ∈ Ioo k t, cay i * cay (t - i)) := by
    nlinarith [h2, hc]
  exact (mul_pos_iff_of_pos_left ht).mp h3

/-- The frozen polynomial `K_{n,k}(y)` (normalised like `zr`) as a chain expansion, `N = n+1`:
`κ_k(N) + ∑_{m=1}^{n-k} κ_k(N-m)/(N-m) · y · Λ_m(y;N)`. -/
noncomputable def Kpoly (k n : ℕ) (y : ℝ) : ℝ :=
  kap k (n + 1) + ∑ m ∈ Icc 1 (n - k),
    kap k (n + 1 - m) / ((n : ℝ) + 1 - m) * y * Lam (thr y ((n : ℝ) + 1)) m

/-! ### Auxiliary lemmas for the chain expansion -/

/-- Shifting the threshold profile: `s ↦ thr y M (M - t + s)` is `thr y t`. -/
private theorem thr_shift (y : ℝ) {t M : ℕ} (h : t ≤ M) :
    (fun s : ℕ => thr y (M : ℝ) (M - t + s)) = thr y (t : ℝ) := by
  funext s
  simp only [thr]
  rw [Nat.cast_add, Nat.cast_sub h]
  congr 1
  ring

/-- First-part recursion for the chain sums, indexed by the bottom size:
`Λ_{M-τ}(y;M) = a_{M-τ} + ∑_{τ<t<M} a_{M-t} (y/t) Λ_{t-τ}(y;t)`. -/
private theorem Lam_thr_first (y : ℝ) (τ M : ℕ) :
    Lam (thr y (M : ℝ)) (M - τ)
      = cay (M - τ)
        + ∑ t ∈ Ioo τ M, cay (M - t) * (y / (t : ℝ)) * Lam (thr y (t : ℝ)) (t - τ) := by
  rw [Lam_first (thr y (M : ℝ)) (M - τ),
    sum_Ioo_reflect (fun t => cay (M - t) * (y / (t : ℝ)) * Lam (thr y (t : ℝ)) (t - τ)) τ M]
  congr 1
  refine Finset.sum_congr rfl fun g hg => ?_
  rw [mem_Ioo] at hg
  show cay g * thr y (M : ℝ) g * Lam (fun s => thr y (M : ℝ) (g + s)) (M - τ - g)
    = cay (M - (M - g)) * (y / ((M - g : ℕ) : ℝ))
        * Lam (thr y ((M - g : ℕ) : ℝ)) (M - g - τ)
  have hgM : g ≤ M := by omega
  have e1 : M - (M - g) = g := by omega
  have e2 : M - τ - g = M - g - τ := by omega
  have e3 : (fun s : ℕ => thr y (M : ℝ) (g + s)) = thr y ((M - g : ℕ) : ℝ) := by
    have h := thr_shift y (t := M - g) (M := M) (Nat.sub_le M g)
    rw [e1] at h
    exact h
  have e4 : thr y (M : ℝ) g = y / ((M - g : ℕ) : ℝ) := by
    simp only [thr]
    rw [Nat.cast_sub hgM]
  rw [e1, e2, e3, e4]

/-- A sequence satisfying the Volterra equation
`u M = κ M + ∑_{k<t<M} a_{M-t} (y/t) u t` has the chain expansion
`u M = κ M + ∑_{k<τ<M} κ τ (y/τ) Λ_{M-τ}(y;M)`. -/
private theorem volterra_chain (k : ℕ) (y : ℝ) (κ u : ℕ → ℝ) (B : ℕ)
    (hu : ∀ M, 1 ≤ M → M ≤ B →
      u M = κ M + ∑ t ∈ Ioo k M, cay (M - t) * (y / (t : ℝ)) * u t) :
    ∀ M, 1 ≤ M → M ≤ B →
      u M = κ M + ∑ τ ∈ Ioo k M, κ τ * (y / (τ : ℝ)) * Lam (thr y (M : ℝ)) (M - τ) := by
  intro M
  induction M using Nat.strong_induction_on with
  | _ M ih =>
    intro hM1 hMB
    rw [hu M hM1 hMB]
    congr 1
    -- insert the induction hypothesis
    have h1 : ∀ t ∈ Ioo k M, cay (M - t) * (y / (t : ℝ)) * u t
        = cay (M - t) * (y / (t : ℝ)) * κ t
          + ∑ τ ∈ Ioo k t,
              κ τ * (y / (τ : ℝ))
                * (cay (M - t) * (y / (t : ℝ)) * Lam (thr y (t : ℝ)) (t - τ)) := by
      intro t ht
      rw [mem_Ioo] at ht
      rw [ih t ht.2 (by omega) (by omega), mul_add, Finset.mul_sum]
      congr 1
      apply Finset.sum_congr rfl
      intro τ _
      ring
    rw [Finset.sum_congr rfl h1, Finset.sum_add_distrib]
    -- exchange the two summations
    have h2 : ∑ t ∈ Ioo k M, ∑ τ ∈ Ioo k t,
          κ τ * (y / (τ : ℝ)) * (cay (M - t) * (y / (t : ℝ)) * Lam (thr y (t : ℝ)) (t - τ))
        = ∑ τ ∈ Ioo k M, ∑ t ∈ Ioo τ M,
          κ τ * (y / (τ : ℝ)) * (cay (M - t) * (y / (t : ℝ)) * Lam (thr y (t : ℝ)) (t - τ)) :=
      Finset.sum_comm' (by intro t τ; simp only [mem_Ioo]; omega)
    rw [h2, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro τ _
    rw [Lam_thr_first y τ M, ← Finset.mul_sum]
    ring

/-- The Volterra equation of the column sum `zr j` at a level `j ∈ {k, k+1}`, in the size
coordinate `M = n + 1`: for `n ≤ 2k+1`,
`Z_n(j) = κ_k(M) + ∑_{k<t<M} a_{M-t} (j/t) Z_{t-1}(j)`.  The weight `t ↦ min t j` of `zr j` is `t`
for `t ≤ k` and `j` for `t > k`. -/
private theorem zr_volterra {j k n : ℕ} (hj : 1 ≤ j) (hkj : k ≤ j) (hjk : j ≤ k + 1)
    (hn : n ≤ 2 * k + 1) :
    zr j n = kap k (n + 1)
      + ∑ t ∈ Ioo k (n + 1), cay (n + 1 - t) * ((j : ℝ) / (t : ℝ)) * zr j (t - 1) := by
  have hω : ∀ t, 1 ≤ t → t ≤ k → ((min t j : ℕ) : ℝ) = t := by
    intro t _ ht
    rw [min_eq_left (show t ≤ j by omega)]
  have hfwd := (zr_isWSol hj).fwd k hω hn
  have hI : Icc (k + 1) n = Ioo k (n + 1) := by
    ext t
    simp only [mem_Icc, mem_Ioo]
    omega
  rw [hI] at hfwd
  have h1 : ∀ t ∈ Ioo k (n + 1),
      cc (n - t) * (cc (t - 1) - ((min t j : ℕ) : ℝ) / (t : ℝ) * zr j (t - 1))
        = cay t * cay (n + 1 - t)
          - cay (n + 1 - t) * ((j : ℝ) / (t : ℝ)) * zr j (t - 1) := by
    intro t ht
    rw [mem_Ioo] at ht
    have e1 : cc (n - t) = cay (n + 1 - t) := by
      unfold cc
      congr 1
      omega
    have e2 : cc (t - 1) = cay t := by
      unfold cc
      congr 1
      omega
    rw [e1, e2, min_eq_right (show j ≤ t by omega)]
    ring
  rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib] at hfwd
  have e0 : cc n = cay (n + 1) := rfl
  rw [e0] at hfwd
  unfold kap
  linarith

/-- First-layer formula: for a level `j ∈ {k, k+1}` and `n ≤ 2k+1`, the column sum is the chain
expansion, `Z_n(j) = K_{n,k}(j)`. -/
private theorem zr_eq_Kpoly {j k n : ℕ} (hj : 1 ≤ j) (hkj : k ≤ j) (hjk : j ≤ k + 1)
    (hn : n ≤ 2 * k + 1) :
    zr j n = Kpoly k n j := by
  have hV : ∀ M, 1 ≤ M → M ≤ 2 * k + 2 →
      zr j (M - 1) = kap k M
        + ∑ t ∈ Ioo k M, cay (M - t) * ((j : ℝ) / (t : ℝ)) * zr j (t - 1) := by
    intro M hM1 hM2
    obtain ⟨n', rfl⟩ : ∃ n', M = n' + 1 := ⟨M - 1, by omega⟩
    exact zr_volterra hj hkj hjk (n := n') (by omega)
  have hC : zr j n = kap k (n + 1)
      + ∑ τ ∈ Ioo k (n + 1),
          kap k τ * ((j : ℝ) / (τ : ℝ)) * Lam (thr (j : ℝ) ((n + 1 : ℕ) : ℝ)) (n + 1 - τ) :=
    volterra_chain k (j : ℝ) (kap k) (fun M => zr j (M - 1)) (2 * k + 2) hV (n + 1)
      (by omega) (by omega)
  have hI : Ioo 0 (n + 1 - k) = Icc 1 (n - k) := by
    ext m
    simp only [mem_Ioo, mem_Icc]
    omega
  rw [hC, sum_Ioo_reflect
    (fun τ => kap k τ * ((j : ℝ) / (τ : ℝ)) * Lam (thr (j : ℝ) ((n + 1 : ℕ) : ℝ)) (n + 1 - τ))
    k (n + 1), hI]
  unfold Kpoly
  congr 1
  refine Finset.sum_congr rfl fun m hm => ?_
  rw [mem_Icc] at hm
  show kap k (n + 1 - m) * ((j : ℝ) / ((n + 1 - m : ℕ) : ℝ))
        * Lam (thr (j : ℝ) ((n + 1 : ℕ) : ℝ)) (n + 1 - (n + 1 - m))
    = kap k (n + 1 - m) / ((n : ℝ) + 1 - (m : ℝ)) * (j : ℝ) * Lam (thr (j : ℝ) ((n : ℝ) + 1)) m
  have e1 : n + 1 - (n + 1 - m) = m := by omega
  have e2 : ((n + 1 - m : ℕ) : ℝ) = (n : ℝ) + 1 - (m : ℝ) := by
    rw [Nat.cast_sub (show m ≤ n + 1 by omega), Nat.cast_add_one]
  have e3 : ((n + 1 : ℕ) : ℝ) = (n : ℝ) + 1 := Nat.cast_add_one n
  rw [e1, e2, e3]
  ring

/-- `κ_{k-1}(t) = κ_k(t) - a_k a_{t-k}` for `1 ≤ k < t`. -/
private theorem kap_pred {k t : ℕ} (hk : 1 ≤ k) (ht : k < t) :
    kap (k - 1) t = kap k t - cay k * cay (t - k) := by
  unfold kap
  have h : Ioo (k - 1) t = insert k (Ioo k t) := by
    ext i
    simp only [mem_Ioo, mem_insert]
    omega
  rw [h, Finset.sum_insert (show k ∉ Ioo k t by rw [mem_Ioo]; omega)]
  ring

/-- `κ_{k-1}(k) = a_k` for `k ≥ 1`. -/
private theorem kap_pred_self {k : ℕ} (hk : 1 ≤ k) : kap (k - 1) k = cay k := by
  unfold kap
  have h : ∑ i ∈ Ioo (k - 1) k, cay i * cay (k - i) = 0 := by
    apply Finset.sum_eq_zero
    intro i hi
    rw [mem_Ioo] at hi
    exfalso
    omega
  rw [h, sub_zero]

/-- Knot identity: `K_{n,k-1}(y) - K_{n,k}(y) = (y - k) (a_k/k) Λ_{N-k}(y;N)`, `N = n+1`. -/
private theorem Kpoly_knot {k n : ℕ} (hk : 1 ≤ k) (hn : k ≤ n) (y : ℝ) :
    Kpoly (k - 1) n y - Kpoly k n y
      = (y - k) * (cay k / k) * Lam (thr y ((n : ℝ) + 1)) (n + 1 - k) := by
  have hk0 : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hd : cay k / (k : ℝ) * (k : ℝ) = cay k := div_mul_cancel₀ (cay k) hk0
  unfold Kpoly
  have e1 : n - (k - 1) = n - k + 1 := by omega
  have e2 : n + 1 - (n - k + 1) = k := by omega
  have e3 : (n : ℝ) + 1 - ((n - k + 1 : ℕ) : ℝ) = (k : ℝ) := by
    rw [Nat.cast_add_one, Nat.cast_sub hn]
    ring
  have e4 : n + 1 - k = n - k + 1 := by omega
  rw [e1, Finset.sum_Icc_succ_top (show 1 ≤ n - k + 1 by omega), e2, e3, kap_pred_self hk,
    kap_pred hk (show k < n + 1 by omega), e4]
  have h1 : ∀ m ∈ Icc 1 (n - k),
      kap (k - 1) (n + 1 - m) / ((n : ℝ) + 1 - (m : ℝ)) * y * Lam (thr y ((n : ℝ) + 1)) m
        = kap k (n + 1 - m) / ((n : ℝ) + 1 - (m : ℝ)) * y * Lam (thr y ((n : ℝ) + 1)) m
          - cay k * (Lam (thr y ((n : ℝ) + 1)) m * thr y ((n : ℝ) + 1) m
              * cay (n - k + 1 - m)) := by
    intro m hm
    rw [mem_Icc] at hm
    have e5 : n + 1 - m - k = n - k + 1 - m := by omega
    have e6 : thr y ((n : ℝ) + 1) m = y / ((n : ℝ) + 1 - (m : ℝ)) := rfl
    rw [kap_pred hk (show k < n + 1 - m by omega), e5, e6]
    ring
  rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib, ← Finset.mul_sum]
  have h2 := Lam_last (thr y ((n : ℝ) + 1)) (n - k + 1)
  have e7 : Ioo 0 (n - k + 1) = Icc 1 (n - k) := by
    ext i
    simp only [mem_Ioo, mem_Icc]
    omega
  rw [e7] at h2
  linear_combination (cay k) * h2 + (Lam (thr y ((n : ℝ) + 1)) (n - k + 1)) * hd

/-- **Curvature minus boundary.** At a first-layer position `n = k + r`, `1 ≤ r ≤ k-1`, with
`K = Kpoly k n` and `N = n+1`:
`d_{n,k}/n! = C_- - B_-` and `d_{n,k+1}/n! = C_+ - B_+`. -/
theorem dq_frozen {k r : ℕ} (hk : 2 ≤ k) (hr1 : 1 ≤ r) (hr2 : r ≤ k - 1) :
    dq k (k + r) =
        (Kpoly k (k + r) ((k : ℝ) + 1) - 2 * Kpoly k (k + r) k + Kpoly k (k + r) ((k : ℝ) - 1))
          - cay k / k * Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1)
    ∧ dq (k + 1) (k + r) =
        (Kpoly k (k + r) ((k : ℝ) + 2) - 2 * Kpoly k (k + r) ((k : ℝ) + 1) + Kpoly k (k + r) k)
          - cay (k + 1) / ((k : ℝ) + 1) * Lam (thr ((k : ℝ) + 2) ((k : ℝ) + r + 1)) r := by
  have hk1 : 1 ≤ k := by omega
  have hnk : k ≤ k + r := by omega
  have hN : ((k + r : ℕ) : ℝ) + 1 = (k : ℝ) + r + 1 := by rw [Nat.cast_add]
  -- the values of `zr` at the four levels `k - 1`, `k`, `k + 1`, `k + 2`
  have hcm : ((k - 1 : ℕ) : ℝ) = (k : ℝ) - 1 := by
    rw [Nat.cast_sub hk1, Nat.cast_one]
  have hc1 : ((k + 1 : ℕ) : ℝ) = (k : ℝ) + 1 := Nat.cast_add_one k
  have hc2 : ((k + 1 + 1 : ℕ) : ℝ) = (k : ℝ) + 2 := by
    rw [Nat.cast_add_one, Nat.cast_add_one]
    ring
  have hzk : zr k (k + r) = Kpoly k (k + r) k := zr_eq_Kpoly hk1 le_rfl (by omega) (by omega)
  have hzk1 : zr (k + 1) (k + r) = Kpoly k (k + r) ((k : ℝ) + 1) := by
    rw [← hc1]
    exact zr_eq_Kpoly (by omega) (by omega) le_rfl (by omega)
  have hzkm : zr (k - 1) (k + r) = Kpoly (k - 1) (k + r) ((k : ℝ) - 1) := by
    rw [← hcm]
    exact zr_eq_Kpoly (by omega) le_rfl (by omega) (by omega)
  have hzk2 : zr (k + 1 + 1) (k + r) = Kpoly (k + 1) (k + r) ((k : ℝ) + 2) := by
    rw [← hc2]
    exact zr_eq_Kpoly (by omega) (by omega) le_rfl (by omega)
  -- the two knot identities
  have hknot1 := Kpoly_knot hk1 hnk ((k : ℝ) - 1)
  have e1 : k + r + 1 - k = r + 1 := by omega
  rw [e1, hN] at hknot1
  have hknot2 := Kpoly_knot (k := k + 1) (n := k + r) (by omega) (by omega) ((k : ℝ) + 2)
  have e2 : k + r + 1 - (k + 1) = r := by omega
  have e3 : k + 1 - 1 = k := by omega
  rw [e2, e3, hN, hc1] at hknot2
  -- `bq` in terms of `zr`
  have hb1 : bq k (k + r) = zr (k + 1) (k + r) - zr k (k + r) := bq_eq hk1 _
  have hb0 : bq (k - 1) (k + r) = zr k (k + r) - zr (k - 1) (k + r) := by
    have h := bq_eq (k := k - 1) (by omega) (k + r)
    have e4 : k - 1 + 1 = k := by omega
    rw [e4] at h
    exact h
  have hb2 : bq (k + 1) (k + r) = zr (k + 1 + 1) (k + r) - zr (k + 1) (k + r) :=
    bq_eq (by omega) _
  constructor
  · show bq k (k + r) - bq (k - 1) (k + r) = _
    linear_combination hb1 - hb0 + hzk1 - 2 * hzk + hzkm + hknot1
  · show bq (k + 1) (k + r) - bq k (k + r) = _
    linear_combination hb2 - hb1 + hzk2 - 2 * hzk1 + hzk - hknot2

end Parking
