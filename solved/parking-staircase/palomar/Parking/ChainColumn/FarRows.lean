module

public import Parking.ChainColumn.ExtremeColumn
public import Parking.ChainColumn.Numerics
public import Parking.ChainColumn.Persistence

/-!
# The rows beyond `k + 0.47 k`

For `n = k + r`, `0.47 k < r ≤ k - 1`, assuming positivity on the rows `k + rq ≤ j < n` with
`rq ≤ k/3`, the column `k ≥ 82` is positive at the row `n` (`caseFar`).

* `bq_chain_pos` : the profile `β^{(l)}_n = b(n,l)/n!` is positive on the chain rows
  `l + 1 ≤ n ≤ 2l + 1`;
* `vT_innov` : in the Borel scale, `v_σ = e^{-σ} β^{(k-1)}_{k+σ}` has nonnegative innovations
  with respect to the frozen kernel `fker`;
* `persist_ineq` : the persistence inequality (`persistence_inequality`) for the parking
  column, with the cut `τ = t0 + 1`:
  `(2/n - ε_τ x^{t0}) β_{n-1} + ∑_{m=τ}^{r-1} (γ_k ε_m - ε_{m+1}) β_{n-1-m} ≤ δ_n`;
* `near_struct`  : for `r ≤ 3k/5` every term of the sum is nonnegative, so that
  `(2/n - ε_τ x^{t0}) β_{n-1} ≤ δ_n`;
* `far_struct`   : for `r > 3k/5` the negative terms of the sum, those with `m ≥ 3k/5`, are
  bounded through the extreme column (`extreme_column_le`) and the profile bound
  `theta_f_le`;
* `far_num`, `SG_le_tail` : the numerics of the far term;
* `caseFar` : three regimes, `0.47 k < r ≤ 3k/5`, `3k/5 < r ≤ 4k/5` and `4k/5 < r ≤ k - 1`,
  each with its own cut `t0 = ⌊σ k⌋ + 1`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### The profile on the chain rows -/

/-- Positivity of the profile on the chain rows. -/
private theorem bq_chain_pos {l : ℕ} (hl : 1 ≤ l) : ∀ n,
    l + 1 ≤ n → n ≤ 2 * l + 1 → 0 < bq l n := by
  intro n hn1
  induction n, hn1 using Nat.le_induction with
  | base =>
    intro _
    have h := bq_L0 (l := l) (n := l + 1) hl (le_refl _) (by omega)
    have e1 : l + 1 - 1 = l := by omega
    have e2 : l + 1 - l - 1 = 0 := by omega
    have e3 : Finset.Icc 1 0 = (∅ : Finset ℕ) := Finset.Icc_eq_empty_of_lt (by omega)
    rw [e1, e2, e3, Finset.sum_empty, bq_eq_zero hl (le_refl l),
      zr_eq_cc (by omega : 1 ≤ l + 1) (by omega : l ≤ l + 1)] at h
    rw [h]
    have hcc := cc_pos l
    have hl1 : (0 : ℝ) < ((l + 1 : ℕ) : ℝ) := by positivity
    have h1 := div_pos hcc hl1
    linarith
  | succ n hn ih =>
    intro hn2
    have ih' := ih (by omega)
    have h := bq_L0 (l := l) (n := n + 1) hl (by omega) hn2
    have e1 : n + 1 - 1 = n := by omega
    rw [e1] at h
    rw [h]
    have hn1 : (0 : ℝ) < ((n + 1 : ℕ) : ℝ) := by positivity
    have hl0 : (0 : ℝ) < (l : ℝ) := by exact_mod_cast hl
    have h1 : 0 ≤ zr (l + 1) n / ((n + 1 : ℕ) : ℝ) := div_nonneg (zr_nonneg _ _) hn1.le
    have h2 : 0 < (l : ℝ) / ((n + 1 : ℕ) : ℝ) * bq l n := mul_pos (div_pos hl0 hn1) ih'
    have h3 : 0 ≤ ∑ m ∈ Icc 1 (n + 1 - l - 1), eps m * bq l (n + 1 - m) :=
      Finset.sum_nonneg (fun m _ => mul_nonneg (eps_nonneg m) (bq_nonneg _ _))
    linarith

/-- The profile in the Borel scale: `v_σ = e^{-σ} β^{(k-1)}_{k+σ}`. -/
private noncomputable def vT (k σ : ℕ) : ℝ := Real.exp (-1) ^ σ * bq (k - 1) (k + σ)

/-- The innovations of `vT k` with respect to the frozen kernel are nonnegative on `s ≤ k - 2`. -/
private theorem vT_innov {k s : ℕ} (hk : 2 ≤ k) (hs : s + 2 ≤ k) :
    ∑ i ∈ Icc 1 s, fker i * vT k (s - i) ≤ vT k s := by
  have hE : 0 < Real.exp (-1) := Real.exp_pos _
  rcases Nat.eq_zero_or_pos s with rfl | hs0
  · have e3 : Finset.Icc 1 0 = (∅ : Finset ℕ) := Finset.Icc_eq_empty_of_lt (by omega)
    rw [e3, Finset.sum_empty]
    unfold vT
    exact mul_nonneg (pow_nonneg hE.le _) (bq_nonneg _ _)
  · obtain ⟨t, rfl⟩ : ∃ t, s = t + 1 := ⟨s - 1, by omega⟩
    have hsplit : ∀ i ∈ Icc 1 (t + 1), fker i * vT k (t + 1 - i)
        = Real.exp (-1) ^ (t + 1) * (eps i * bq (k - 1) (k + (t + 1) - i))
          + (if i = 1 then Real.exp (-1) / 2 else 0) * vT k (t + 1 - i) := by
      intro i hi
      rw [mem_Icc] at hi
      have e1 : Real.exp (-1) ^ i * Real.exp (-1) ^ (t + 1 - i) = Real.exp (-1) ^ (t + 1) := by
        rw [← pow_add, Nat.add_sub_cancel' hi.2]
      have e2 : k + (t + 1 - i) = k + (t + 1) - i := by omega
      unfold fker vT
      rw [exp_neg_nat, e2]
      linear_combination (eps i * bq (k - 1) (k + (t + 1) - i)) * e1
    have hone : ∑ i ∈ Icc 1 (t + 1), (if i = 1 then Real.exp (-1) / 2 else 0) * vT k (t + 1 - i)
        = Real.exp (-1) / 2 * vT k t := by
      rw [Finset.sum_eq_single_of_mem 1 (mem_Icc.mpr ⟨le_refl 1, by omega⟩)
        (fun b _ hb => by rw [ite_eq_right hb, zero_mul]), ite_eq_left rfl, Nat.add_sub_cancel]
    rw [sum_congr rfl hsplit, sum_add_distrib, ← mul_sum, hone]
    unfold vT
    have h := bq_L0 (l := k - 1) (n := k + (t + 1)) (by omega) (by omega) (by omega)
    have e3 : k + (t + 1) - (k - 1) - 1 = t + 1 := by omega
    have e4 : k + (t + 1) - 1 = k + t := by omega
    have e5 : k - 1 + 1 = k := by omega
    rw [e3, e4, e5] at h
    have hn1 : (0 : ℝ) < ((k + (t + 1) : ℕ) : ℝ) := by positivity
    have hZ : 0 ≤ zr k (k + t) / ((k + (t + 1) : ℕ) : ℝ) :=
      div_nonneg (zr_nonneg _ _) hn1.le
    have hhalf : (1 : ℝ) / 2 ≤ ((k - 1 : ℕ) : ℝ) / ((k + (t + 1) : ℕ) : ℝ) := by
      rw [le_div_iff₀ hn1]
      have h0 : k + (t + 1) ≤ 2 * (k - 1) := by omega
      have h' : ((k + (t + 1) : ℕ) : ℝ) ≤ 2 * ((k - 1 : ℕ) : ℝ) := by exact_mod_cast h0
      linarith
    have hu : 0 ≤ bq (k - 1) (k + t) := bq_nonneg _ _
    have h1 : (1 : ℝ) / 2 * bq (k - 1) (k + t)
        ≤ ((k - 1 : ℕ) : ℝ) / ((k + (t + 1) : ℕ) : ℝ) * bq (k - 1) (k + t) :=
      mul_le_mul_of_nonneg_right hhalf hu
    have hpos : 0 ≤ Real.exp (-1) ^ t * Real.exp (-1) :=
      mul_nonneg (pow_nonneg hE.le _) hE.le
    have h2 := mul_nonneg hpos hZ
    have h3 := mul_le_mul_of_nonneg_left h1 hpos
    rw [h, pow_succ]
    linarith

/-! ### The far weights -/

/-- `θ_m = max (g(m) - γ_k, 0)`, `g(m) = ε_{m+1}/ε_m`. -/
private noncomputable def thetaW (k m : ℕ) : ℝ := max (gs (m - 1) - gam k) 0

private theorem thetaW_nonneg (k m : ℕ) : 0 ≤ thetaW k m := le_max_right _ _

private theorem thetaW_mono (k : ℕ) {a b : ℕ} (hab : a ≤ b) : thetaW k a ≤ thetaW k b := by
  unfold thetaW
  exact max_le_max (sub_le_sub_right (gs_mono (Nat.sub_le_sub_right hab 1)) _) le_rfl

private theorem coef_ge {k m : ℕ} (hm : 1 ≤ m) :
    -(thetaW k m * eps m) ≤ gam k * eps m - eps (m + 1) := by
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  have h1 : gs i - gam k ≤ thetaW k (i + 1) := by
    unfold thetaW
    rw [Nat.add_sub_cancel]
    exact le_max_left _ _
  have h3 := mul_le_mul_of_nonneg_right h1 (eps_nonneg (i + 1))
  rw [eps_step i]
  linarith

private theorem thetaW_fker_le {k m : ℕ} (hm : 49 ≤ m) (hmk : m + 1 ≤ k)
    (h : 3 * k ≤ 5 * (m + 1)) :
    thetaW k m * fker m ≤ 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := by
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  have h1 := theta_f_le (k := k) (i := i) (by omega) (by omega) (by omega)
  have hf : 0 ≤ fker (i + 1) := (fker_pos (by omega)).le
  have hB : 0 ≤ 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := by
    unfold c0
    positivity
  unfold thetaW
  rw [Nat.add_sub_cancel, max_mul_of_nonneg _ _ hf, zero_mul]
  exact max_le h1 hB

/-! ### The persistence inequality for the parking column -/

private theorem persist_ineq {k r t0 : ℕ} (hk : 2 ≤ k) (hr : r + 1 ≤ k) (ht0 : 1 ≤ t0)
    (ht0r : t0 + 1 ≤ r) (hcap : 5 * (t0 + 1) ≤ 3 * k)
    (hpos : ∀ j, k + r - t0 ≤ j → j < k + r → 0 ≤ dq k j) :
    (2 / ((k + r : ℕ) : ℝ) - eps (t0 + 1) * xk k ^ t0) * bq (k - 1) (k + r - 1)
      + ∑ m ∈ Icc (t0 + 1) (r - 1),
          (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + r - 1 - m)
      ≤ dq k (k + r) := by
  have hCE0 := dq_col (k := k) (n := k + r) hk (by omega) (by omega)
  have hk0 : bq (k - 1) (k - 1) = 0 := bq_eq_zero (by omega) (le_refl _)
  have hCE : (2 / ((k + r : ℕ) : ℝ)) * bq (k - 1) (k + r - 1)
      + (((k : ℝ) + 1) / ((k + r : ℕ) : ℝ)) * dq k (k + r - 1)
      + ∑ m ∈ Icc 1 (k + r - k), eps m * dq k (k + r - m) ≤ dq k (k + r) := by
    rw [hCE0]
    exact le_of_eq (by ring)
  have hDg : ∀ j, k ≤ j → j ≤ k + r - 1 → gam k * bq (k - 1) (j - 1) - bq (k - 1) j ≤ dq k j := by
    intro j hj1 _
    exact dq_diag_lower hk (by omega)
  have h := persistence_inequality eps (bq (k - 1)) (dq k) (gam k) k (k + r) (t0 + 1)
    (gam_pos k) (fun m hm => eps_pos hm) (by omega) (by omega) (by omega) hk0 (by omega)
    hCE hDg (fun m hm1 hm2 => eps_succ_le_gam hk hm1 (by omega))
    (fun j hj1 hj2 => hpos j (by omega) (by omega))
  have e2 : k + r - k - 1 = r - 1 := by omega
  have e3 : t0 + 1 - 1 = t0 := by omega
  have e4 : eps (t0 + 1) / gam k ^ t0 = eps (t0 + 1) * xk k ^ t0 := by
    unfold xk
    rw [inv_pow, div_eq_mul_inv]
  rw [e2, e3, e4] at h
  exact h

/-- Rows `r ≤ 3k/5`: no far term. -/
private theorem near_struct {k r t0 : ℕ} (hk : 2 ≤ k) (hr : r + 1 ≤ k) (ht0 : 1 ≤ t0)
    (ht0r : t0 + 1 ≤ r) (h35 : 5 * r ≤ 3 * k)
    (hpos : ∀ j, k + r - t0 ≤ j → j < k + r → 0 ≤ dq k j) :
    (2 / ((k + r : ℕ) : ℝ) - eps (t0 + 1) * xk k ^ t0) * bq (k - 1) (k + r - 1)
      ≤ dq k (k + r) := by
  have h := persist_ineq hk hr ht0 ht0r (by omega) hpos
  have hs : 0 ≤ ∑ m ∈ Icc (t0 + 1) (r - 1),
      (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + r - 1 - m) := by
    refine Finset.sum_nonneg (fun m hm => ?_)
    rw [mem_Icc] at hm
    exact mul_nonneg (sub_nonneg.2 (eps_succ_le_gam hk (by omega) (by omega))) (bq_nonneg _ _)
  linarith

/-- Rows `r > 3k/5`: the far term through the extreme column. -/
private theorem far_struct {k ρ t0 : ℕ} (hk : 82 ≤ k) (hr : ρ + 2 ≤ k) (hrM : 3 * k / 5 ≤ ρ)
    (ht0 : 1 ≤ t0) (hcap : t0 + 1 ≤ 3 * k / 5)
    (hpos : ∀ j, k + (ρ + 1) - t0 ≤ j → j < k + (ρ + 1) → 0 ≤ dq k j) :
    ((2 / ((k + (ρ + 1) : ℕ) : ℝ) - eps (t0 + 1) * xk k ^ t0) * Gres ρ
        - 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k)
          * ∑ i ∈ range (ρ - 3 * k / 5 + 1), Gres i) * bq (k - 1) (k + (ρ + 1) - 1)
      ≤ dq k (k + (ρ + 1)) * Gres ρ := by
  obtain ⟨M, hM⟩ : ∃ M, M = 3 * k / 5 := ⟨_, rfl⟩
  rw [← hM] at hrM hcap ⊢
  have hM1 : 5 * M ≤ 3 * k := by omega
  have hM2 : 3 * k < 5 * M + 5 := by omega
  have hM49 : 49 ≤ M := by omega
  have hk2 : 2 ≤ k := by omega
  have h := persist_ineq (k := k) (r := ρ + 1) (t0 := t0) hk2 (by omega) ht0 (by omega)
    (by omega) hpos
  rw [Nat.add_sub_cancel] at h
  -- split the sum at `M`
  have hsplit : ∑ m ∈ Icc (t0 + 1) ρ,
        (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + (ρ + 1) - 1 - m)
      = ∑ m ∈ Icc (t0 + 1) (M - 1),
          (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + (ρ + 1) - 1 - m)
        + ∑ m ∈ Icc (M - 1 + 1) ρ,
          (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + (ρ + 1) - 1 - m) :=
    sum_Icc_split _ (by omega) (by omega)
  have eM : M - 1 + 1 = M := by omega
  rw [eM] at hsplit
  have hlow : 0 ≤ ∑ m ∈ Icc (t0 + 1) (M - 1),
      (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + (ρ + 1) - 1 - m) := by
    refine Finset.sum_nonneg (fun m hm => ?_)
    rw [mem_Icc] at hm
    exact mul_nonneg (sub_nonneg.2 (eps_succ_le_gam hk2 (by omega) (by omega))) (bq_nonneg _ _)
  -- the far part against the weights
  have hfar : -(∑ m ∈ Icc M ρ, thetaW k m * (eps m * bq (k - 1) (k + (ρ + 1) - 1 - m)))
      ≤ ∑ m ∈ Icc M ρ, (gam k * eps m - eps (m + 1)) * bq (k - 1) (k + (ρ + 1) - 1 - m) := by
    rw [← Finset.sum_neg_distrib]
    refine Finset.sum_le_sum (fun m hm => ?_)
    rw [mem_Icc] at hm
    have h1 := coef_ge (k := k) (m := m) (by omega)
    have h2 := bq_nonneg (k - 1) (k + (ρ + 1) - 1 - m)
    have h3 := mul_le_mul_of_nonneg_right h1 h2
    linarith
  -- the extreme column
  have hE : 0 < Real.exp (-1) := Real.exp_pos _
  have hext := extreme_column_le (v := vT k) (θ := thetaW k) (ρ := ρ) (M := M)
    (fun i hi => fker_pos hi) fker_logconvex Gres_isRenewal (by omega) (thetaW_nonneg k M)
    (fun a b _ hab _ => thetaW_mono k hab) (fun s hs => vT_innov hk2 (by omega))
  have hconv : ∑ m ∈ Icc M ρ, thetaW k m * (fker m * vT k (ρ - m))
      = Real.exp (-1) ^ ρ
        * ∑ m ∈ Icc M ρ, thetaW k m * (eps m * bq (k - 1) (k + (ρ + 1) - 1 - m)) := by
    rw [mul_sum]
    refine sum_congr rfl (fun m hm => ?_)
    rw [mem_Icc] at hm
    have e1 : Real.exp (-1) ^ m * Real.exp (-1) ^ (ρ - m) = Real.exp (-1) ^ ρ := by
      rw [← pow_add, Nat.add_sub_cancel' hm.2]
    have e2 : k + (ρ - m) = k + (ρ + 1) - 1 - m := by omega
    rw [fker_of_two_le (by omega : 2 ≤ m)]
    unfold vT
    rw [e2]
    linear_combination (thetaW k m * eps m * bq (k - 1) (k + (ρ + 1) - 1 - m)) * e1
  have hvρ : vT k ρ = Real.exp (-1) ^ ρ * bq (k - 1) (k + (ρ + 1) - 1) := by
    unfold vT
    rw [show k + (ρ + 1) - 1 = k + ρ from by omega]
  have hbound : ∑ m ∈ Icc M ρ, thetaW k m * (fker m * Gres (ρ - m))
      ≤ 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) * ∑ i ∈ range (ρ - M + 1), Gres i := by
    have h1 : ∑ m ∈ Icc M ρ, thetaW k m * (fker m * Gres (ρ - m))
        ≤ ∑ m ∈ Icc M ρ, 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) * Gres (ρ - m) := by
      refine Finset.sum_le_sum (fun m hm => ?_)
      rw [mem_Icc] at hm
      have h2 := thetaW_fker_le (k := k) (m := m) (by omega) (by omega) (by omega)
      calc thetaW k m * (fker m * Gres (ρ - m)) = (thetaW k m * fker m) * Gres (ρ - m) := by ring
        _ ≤ 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) * Gres (ρ - m) :=
            mul_le_mul_of_nonneg_right h2 (Gres_pos _).le
    have hrefl : ∑ m ∈ Icc M ρ, Gres (ρ - m) = ∑ i ∈ range (ρ - M + 1), Gres i := by
      rw [← Ico_add_one_right_eq_Icc, sum_Ico_reflect Gres M le_rfl, Nat.sub_self,
        Nat.Ico_zero_eq_range, Nat.sub_add_comm hrM]
    rw [← hrefl, mul_sum]
    exact h1
  -- abbreviations
  obtain ⟨B, hB⟩ : ∃ B : ℝ, B = 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := ⟨_, rfl⟩
  obtain ⟨SG, hSG⟩ : ∃ SG : ℝ, SG = ∑ i ∈ range (ρ - M + 1), Gres i := ⟨_, rfl⟩
  obtain ⟨S1, hS1⟩ : ∃ S1 : ℝ,
      S1 = ∑ m ∈ Icc M ρ, thetaW k m * (eps m * bq (k - 1) (k + (ρ + 1) - 1 - m)) := ⟨_, rfl⟩
  obtain ⟨FG, hFG⟩ : ∃ FG : ℝ, FG = ∑ m ∈ Icc M ρ, thetaW k m * (fker m * Gres (ρ - m)) :=
    ⟨_, rfl⟩
  obtain ⟨U, hU⟩ : ∃ U : ℝ, U = bq (k - 1) (k + (ρ + 1) - 1) := ⟨_, rfl⟩
  obtain ⟨a, ha⟩ : ∃ a : ℝ, a = 2 / ((k + (ρ + 1) : ℕ) : ℝ) - eps (t0 + 1) * xk k ^ t0 :=
    ⟨_, rfl⟩
  have hU0 : 0 ≤ U := by rw [hU]; exact bq_nonneg _ _
  have hG := Gres_pos ρ
  rw [← hB, ← hSG, ← hFG] at hbound
  rw [hconv, hvρ, ← hS1, ← hFG, ← hU] at hext
  rw [← hS1] at hfar
  rw [← ha, ← hU, hsplit] at h
  rw [← hB, ← hSG, ← ha, ← hU]
  -- `S1 * G ≤ B * SG * U`
  have hS1G : S1 * Gres ρ ≤ B * SG * U := by
    have h2 : Real.exp (-1) ^ ρ * (S1 * Gres ρ) ≤ Real.exp (-1) ^ ρ * (FG * U) := by
      calc Real.exp (-1) ^ ρ * (S1 * Gres ρ) = Real.exp (-1) ^ ρ * S1 * Gres ρ := by ring
        _ ≤ FG * (Real.exp (-1) ^ ρ * U) := hext
        _ = Real.exp (-1) ^ ρ * (FG * U) := by ring
    have h3 : S1 * Gres ρ ≤ FG * U := le_of_mul_le_mul_left h2 (pow_pos hE ρ)
    exact h3.trans (mul_le_mul_of_nonneg_right hbound hU0)
  have hmain : a * U - S1 ≤ dq k (k + (ρ + 1)) := by linarith
  have h5 := mul_le_mul_of_nonneg_right hmain hG.le
  have e6 : (a * Gres ρ - B * SG) * U = (a * U - S1) * Gres ρ + (S1 * Gres ρ - B * SG * U) := by
    ring
  rw [e6]
  linarith

/-! ### Numerics of the far term -/

private theorem far_num (K R SG G q ν D SGc : ℝ) (hK : 0 < K) (hR : 0 < R)
    (hSG : SG ≤ SGc * Real.exp 1) (hSGc : 0 ≤ SGc)
    (hG : Real.exp 1 * ((1 - 1 / (12 * R)) / Real.sqrt (2 * Real.pi * R)) / R * (4 - 21 / R) ≤ G)
    (hν : (K + R) * (R * Real.sqrt R) ≤ ν * (K ^ 2 * Real.sqrt K))
    (hD : D ≤ (1 - 1 / (12 * R)) * (4 - 21 / R)) (hq0 : 0 ≤ q)
    (hq : 105 / 100 * SGc * ν ≤ 2 * q * D) :
    (K + R) / 2 * (105 / 100 * c0 / (K ^ 2 * Real.sqrt K) * SG) ≤ q * G := by
  obtain ⟨sK, hsK⟩ : ∃ sK : ℝ, sK = Real.sqrt K := ⟨_, rfl⟩
  obtain ⟨sR, hsR⟩ : ∃ sR : ℝ, sR = Real.sqrt R := ⟨_, rfl⟩
  obtain ⟨w, hw⟩ : ∃ w : ℝ, w = Real.sqrt (2 * Real.pi) := ⟨_, rfl⟩
  have hsK0 : 0 < sK := by rw [hsK]; exact Real.sqrt_pos.2 hK
  have hsR0 : 0 < sR := by rw [hsR]; exact Real.sqrt_pos.2 hR
  have hw0 : 0 < w := by rw [hw]; exact Real.sqrt_pos.2 (mul_pos two_pos Real.pi_pos)
  have hsq : Real.sqrt (2 * Real.pi * R) = w * sR := by
    rw [hw, hsR]
    exact Real.sqrt_mul (mul_pos two_pos Real.pi_pos).le _
  have hc0 : c0 = 1 / w := by
    unfold c0
    rw [hw]
  have hE : 0 < Real.exp 1 := Real.exp_pos 1
  rw [hsq] at hG
  rw [← hsK] at hν ⊢
  rw [← hsR] at hν
  rw [hc0]
  have hsK1 : sK ≠ 0 := hsK0.ne'
  have hsR1 : sR ≠ 0 := hsR0.ne'
  have hw1 : w ≠ 0 := hw0.ne'
  have hK1 : K ≠ 0 := hK.ne'
  have hR1 : R ≠ 0 := hR.ne'
  have hK2 : 0 < K ^ 2 * sK := mul_pos (pow_pos hK 2) hsK0
  have hcoef : 0 ≤ (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) :=
    mul_nonneg (by linarith) (div_nonneg (mul_nonneg (by norm_num) (one_div_pos.2 hw0).le) hK2.le)
  have h1 : (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK) * SG)
      ≤ (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) * (SGc * Real.exp 1) := by
    calc (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK) * SG)
        = (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) * SG := by ring
      _ ≤ (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) * (SGc * Real.exp 1) :=
          mul_le_mul_of_nonneg_left hSG hcoef
  have core : (K + R) * (105 / 100) * SGc * (sR * R) ≤ 2 * q * D * (K ^ 2 * sK) := by
    have a1 : (105 / 100 * SGc) * ((K + R) * (R * sR))
        ≤ (105 / 100 * SGc) * (ν * (K ^ 2 * sK)) :=
      mul_le_mul_of_nonneg_left hν (mul_nonneg (by norm_num) hSGc)
    have a2 : (105 / 100 * SGc * ν) * (K ^ 2 * sK) ≤ (2 * q * D) * (K ^ 2 * sK) :=
      mul_le_mul_of_nonneg_right hq hK2.le
    linarith
  have hden : 0 < 2 * w * (K ^ 2 * sK) * (sR * R) :=
    mul_pos (mul_pos (mul_pos two_pos hw0) hK2) (mul_pos hsR0 hR)
  have hfac : 0 ≤ Real.exp 1 / (2 * w * (K ^ 2 * sK) * (sR * R)) := div_nonneg hE.le hden.le
  have h2 : (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) * (SGc * Real.exp 1)
      ≤ q * (Real.exp 1 * (D / (w * sR)) / R) := by
    have e1 : (K + R) / 2 * (105 / 100 * (1 / w) / (K ^ 2 * sK)) * (SGc * Real.exp 1)
        = Real.exp 1 / (2 * w * (K ^ 2 * sK) * (sR * R))
          * ((K + R) * (105 / 100) * SGc * (sR * R)) := by
      field
    have e2 : q * (Real.exp 1 * (D / (w * sR)) / R)
        = Real.exp 1 / (2 * w * (K ^ 2 * sK) * (sR * R)) * (2 * q * D * (K ^ 2 * sK)) := by
      field
    rw [e1, e2]
    exact mul_le_mul_of_nonneg_left core hfac
  have h3 : q * (Real.exp 1 * (D / (w * sR)) / R) ≤ q * G := by
    refine mul_le_mul_of_nonneg_left (le_trans ?_ hG) hq0
    have e3 : Real.exp 1 * ((1 - 1 / (12 * R)) / (w * sR)) / R * (4 - 21 / R)
        = Real.exp 1 / (w * sR * R) * ((1 - 1 / (12 * R)) * (4 - 21 / R)) := by
      field
    have e4 : Real.exp 1 * (D / (w * sR)) / R = Real.exp 1 / (w * sR * R) * D := by
      field
    rw [e3, e4]
    exact mul_le_mul_of_nonneg_left hD
      (div_nonneg hE.le (mul_pos (mul_pos hw0 hsR0) hR).le)
  exact h1.trans (h2.trans h3)

/-- `(K+R) R √R ≤ (1+c²) c³ K² √K` when `R ≤ c² K`. -/
private theorem nu_bound (K R c : ℝ) (hK : 0 < K) (hR0 : 0 ≤ R) (hc : 0 ≤ c) (hR : R ≤ c ^ 2 * K) :
    (K + R) * (R * Real.sqrt R) ≤ (1 + c ^ 2) * c ^ 3 * (K ^ 2 * Real.sqrt K) := by
  have hsK : 0 ≤ Real.sqrt K := Real.sqrt_nonneg K
  have hsR : 0 ≤ Real.sqrt R := Real.sqrt_nonneg R
  have h1 : Real.sqrt R ≤ c * Real.sqrt K := by
    rw [Real.sqrt_le_left (mul_nonneg hc hsK), mul_pow, Real.sq_sqrt hK.le]
    exact hR
  have h2 : K + R ≤ (1 + c ^ 2) * K := by linarith
  have h3 : R * Real.sqrt R ≤ (c ^ 2 * K) * (c * Real.sqrt K) :=
    mul_le_mul hR h1 hsR (mul_nonneg (pow_nonneg hc 2) hK.le)
  have h4 : (K + R) * (R * Real.sqrt R) ≤ ((1 + c ^ 2) * K) * ((c ^ 2 * K) * (c * Real.sqrt K)) :=
    mul_le_mul h2 h3 (mul_nonneg hR0 hsR) (mul_nonneg (by positivity) hK.le)
  calc (K + R) * (R * Real.sqrt R)
      ≤ ((1 + c ^ 2) * K) * ((c ^ 2 * K) * (c * Real.sqrt K)) := h4
    _ = (1 + c ^ 2) * c ^ 3 * (K ^ 2 * Real.sqrt K) := by ring

/-- Monotonicity of the lower-bound factor. -/
private theorem D_bound (R r0 : ℝ) (hr0 : 6 ≤ r0) (hR : r0 ≤ R) :
    (1 - 1 / (12 * r0)) * (4 - 21 / r0) ≤ (1 - 1 / (12 * R)) * (4 - 21 / R) := by
  have hr1 : (0 : ℝ) < r0 := by linarith
  have hR1 : (0 : ℝ) < R := by linarith
  have hA : 1 - 1 / (12 * r0) ≤ 1 - 1 / (12 * R) := by
    have h : 1 / (12 * R) ≤ 1 / (12 * r0) :=
      div_le_div_of_nonneg_left zero_le_one (by positivity) (by linarith)
    linarith
  have hB : 4 - 21 / r0 ≤ 4 - 21 / R := by
    have h : 21 / R ≤ 21 / r0 := div_le_div_of_nonneg_left (by norm_num) hr1 hR
    linarith
  have hB0 : 0 ≤ 4 - 21 / r0 := by
    have h : 21 / r0 ≤ 4 := by
      rw [div_le_iff₀ hr1]
      linarith
    linarith
  have hA0 : 0 ≤ 1 - 1 / (12 * R) := by
    have h : 1 / (12 * R) ≤ 1 := by
      rw [div_le_iff₀ (by positivity)]
      linarith
    linarith
  exact mul_le_mul hA hB hB0 hA0

/-- `G_i ≥ 1.12 e / ((i+1) √(i+1))` for `i ≥ 17`. -/
private theorem Gres_ge_m32 {i : ℕ} (hi : 17 ≤ i) :
    112 / 100 * Real.exp 1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1)) ≤ Gres i := by
  have hI17 : (17 : ℝ) ≤ (i : ℝ) := by exact_mod_cast hi
  have hI : (18 : ℝ) ≤ (i : ℝ) + 1 := by linarith
  have hI0 : (0 : ℝ) < (i : ℝ) + 1 := by linarith
  have hG := Gres_lower (s := i) (by omega)
  obtain ⟨sI, hsI⟩ : ∃ sI : ℝ, sI = Real.sqrt ((i : ℝ) + 1) := ⟨_, rfl⟩
  obtain ⟨w, hw⟩ : ∃ w : ℝ, w = Real.sqrt (2 * Real.pi) := ⟨_, rfl⟩
  have hsI0 : 0 < sI := by rw [hsI]; exact Real.sqrt_pos.2 hI0
  have hw0 : 0 < w := by rw [hw]; exact Real.sqrt_pos.2 (mul_pos two_pos Real.pi_pos)
  have hsq : Real.sqrt (2 * Real.pi * ((i : ℝ) + 1)) = w * sI := by
    rw [hw, hsI]
    exact Real.sqrt_mul (mul_pos two_pos Real.pi_pos).le _
  rw [hsq] at hG
  rw [← hsI]
  have hc : (19947 / 50000 : ℝ) ≤ 1 / w := by
    rw [hw]
    exact c0_bounds.1
  have h1 : (215 / 216 : ℝ) ≤ 1 - 1 / (12 * ((i : ℝ) + 1)) := by
    have h : 1 / (12 * ((i : ℝ) + 1)) ≤ 1 / 216 := by
      rw [div_le_div_iff₀ (by positivity) (by norm_num)]
      linarith
    linarith
  have h2 : (17 / 6 : ℝ) ≤ 4 - 21 / ((i : ℝ) + 1) := by
    have h : 21 / ((i : ℝ) + 1) ≤ 7 / 6 := by
      rw [div_le_div_iff₀ hI0 (by norm_num)]
      linarith
    linarith
  have h3 : (112 / 100 : ℝ)
      ≤ 1 / w * ((1 - 1 / (12 * ((i : ℝ) + 1))) * (4 - 21 / ((i : ℝ) + 1))) := by
    have a1 : (215 / 216 : ℝ) * (17 / 6)
        ≤ (1 - 1 / (12 * ((i : ℝ) + 1))) * (4 - 21 / ((i : ℝ) + 1)) :=
      mul_le_mul h1 h2 (by norm_num) (by linarith)
    have a2 : (19947 / 50000 : ℝ) * ((215 / 216 : ℝ) * (17 / 6))
        ≤ 1 / w * ((1 - 1 / (12 * ((i : ℝ) + 1))) * (4 - 21 / ((i : ℝ) + 1))) :=
      mul_le_mul hc a1 (by norm_num) (one_div_pos.2 hw0).le
    have a3 : (112 / 100 : ℝ) ≤ (19947 / 50000 : ℝ) * ((215 / 216 : ℝ) * (17 / 6)) := by
      norm_num
    linarith
  have hsI1 : sI ≠ 0 := hsI0.ne'
  have hw1 : w ≠ 0 := hw0.ne'
  have hI1 : ((i : ℝ) + 1) ≠ 0 := hI0.ne'
  have e : Real.exp 1 * ((1 - 1 / (12 * ((i : ℝ) + 1))) / (w * sI)) / ((i : ℝ) + 1)
        * (4 - 21 / ((i : ℝ) + 1))
      = Real.exp 1 / (((i : ℝ) + 1) * sI)
        * (1 / w * ((1 - 1 / (12 * ((i : ℝ) + 1))) * (4 - 21 / ((i : ℝ) + 1)))) := by
    field
  rw [e] at hG
  have h4 : Real.exp 1 / (((i : ℝ) + 1) * sI) * (112 / 100)
      ≤ Real.exp 1 / (((i : ℝ) + 1) * sI)
        * (1 / w * ((1 - 1 / (12 * ((i : ℝ) + 1))) * (4 - 21 / ((i : ℝ) + 1)))) :=
    mul_le_mul_of_nonneg_left h3 (div_nonneg (Real.exp_pos 1).le (mul_pos hI0 hsI0).le)
  have e5 : 112 / 100 * Real.exp 1 / (((i : ℝ) + 1) * sI)
      = Real.exp 1 / (((i : ℝ) + 1) * sI) * (112 / 100) := by ring
  rw [e5]
  exact h4.trans hG

/-- The partial sums of `G` stay below `2e` by the tail: for `17 ≤ a`, `a + 1 ≤ 44`. -/
private theorem SG_le_tail {a : ℕ} (ha : 17 ≤ a) (ha2 : a + 1 ≤ 44) :
    ∑ i ∈ range a, Gres i ≤ (2 - 253 / 1000) * Real.exp 1 := by
  obtain ⟨b, hb⟩ : ∃ b, b = 16 * (a + 1) - 1 := ⟨_, rfl⟩
  have hab : a ≤ b := by omega
  have htail := tail_sqrt Gres (112 / 100 * Real.exp 1)
    (mul_nonneg (by norm_num) (Real.exp_pos 1).le) a (fun i hi => Gres_ge_m32 (le_trans ha hi)) b
    hab
  have hsum := Gres_sum_le b
  rw [← Finset.sum_range_add_sum_Ico Gres hab] at hsum
  have hb1 : ((b : ℝ) + 1) = 16 * ((a : ℝ) + 1) := by
    have h0 : b + 1 = 16 * (a + 1) := by omega
    exact_mod_cast h0
  have hA0 : (0 : ℝ) < (a : ℝ) + 1 := by positivity
  have hs16 : Real.sqrt ((b : ℝ) + 1) = 4 * Real.sqrt ((a : ℝ) + 1) := by
    have h16 : Real.sqrt (16 : ℝ) = 4 := by
      rw [show (16 : ℝ) = 4 ^ 2 by norm_num]
      exact Real.sqrt_sq (by norm_num)
    rw [hb1, Real.sqrt_mul (by norm_num : (0 : ℝ) ≤ 16), h16]
  obtain ⟨sA, hsA⟩ : ∃ sA : ℝ, sA = Real.sqrt ((a : ℝ) + 1) := ⟨_, rfl⟩
  have hsA0 : 0 < sA := by rw [hsA]; exact Real.sqrt_pos.2 hA0
  have hsA2 : sA ≠ 0 := hsA0.ne'
  have hsA1 : sA ≤ 664 / 100 := by
    rw [hsA, Real.sqrt_le_left (by norm_num)]
    have h44 : ((a : ℝ) + 1) ≤ 44 := by exact_mod_cast ha2
    have h44' : (44 : ℝ) ≤ (664 / 100) ^ 2 := by norm_num
    linarith
  rw [hs16, ← hsA] at htail
  have hE := Real.exp_pos 1
  have h1 : 112 / 100 * Real.exp 1 * (2 * (1 / sA - 1 / (4 * sA)))
      = 168 / 100 * Real.exp 1 / sA := by
    field
  have h2 : 168 / 100 * Real.exp 1 / (664 / 100) ≤ 168 / 100 * Real.exp 1 / sA :=
    div_le_div_of_nonneg_left (mul_nonneg (by norm_num) hE.le) hsA0 hsA1
  have h3 : 253 / 1000 * Real.exp 1 ≤ 168 / 100 * Real.exp 1 / (664 / 100) := by
    rw [le_div_iff₀ (by norm_num)]
    linarith
  linarith

/-- The final step of the far regimes. -/
private theorem far_final (n ψ B SG G U d p q : ℝ) (hn : 0 < n) (hG : 0 < G) (hU : 0 < U)
    (hstruct : ((2 / n - ψ) * G - B * SG) * U ≤ d * G)
    (hP : n / 2 * ψ ≤ p) (hfar : n / 2 * (B * SG) ≤ q * G) (hpq : p + q < 1) : 0 < d := by
  have hn1 : n ≠ 0 := hn.ne'
  have h1 : n / 2 * ((2 / n - ψ) * G - B * SG) = G - (n / 2 * ψ) * G - n / 2 * (B * SG) := by
    field
  have h2 : (n / 2 * ψ) * G ≤ p * G := mul_le_mul_of_nonneg_right hP hG.le
  have h8 := mul_pos (sub_pos.2 hpq) hG
  have h3 : 0 < n / 2 * ((2 / n - ψ) * G - B * SG) := by
    rw [h1]
    linarith
  have h4 : 0 < (2 / n - ψ) * G - B * SG := by
    by_contra hc
    have h5 := mul_nonneg (by linarith : (0 : ℝ) ≤ n / 2) (neg_nonneg.2 (not_lt.mp hc))
    linarith
  have h6 : 0 < d * G := lt_of_lt_of_le (mul_pos h4 hU) hstruct
  by_contra hc
  have h7 := mul_nonneg (neg_nonneg.2 (not_lt.mp hc)) hG.le
  linarith

/-! ### The three regimes -/

/-- A natural number `t` with `a k ≤ b t ≤ a k + b` lies in `[σ k, σ k + 1]`, where
`σ = a / b`. -/
private theorem cut_bounds {a b k t : ℕ} {σ : ℝ} (hb : 0 < b) (hσ : σ * (b : ℝ) = (a : ℝ))
    (h1 : a * k ≤ b * t) (h2 : b * t ≤ a * k + b) :
    σ * (k : ℝ) ≤ (t : ℝ) ∧ (t : ℝ) ≤ σ * (k : ℝ) + 1 := by
  have hb' : (0 : ℝ) < (b : ℝ) := by exact_mod_cast hb
  have h1' : (a : ℝ) * (k : ℝ) ≤ (b : ℝ) * (t : ℝ) := by exact_mod_cast h1
  have h2' : (b : ℝ) * (t : ℝ) ≤ (a : ℝ) * (k : ℝ) + (b : ℝ) := by exact_mod_cast h2
  rw [← hσ] at h1' h2'
  constructor
  · refine le_of_mul_le_mul_left ?_ hb'
    linarith
  · refine le_of_mul_le_mul_left ?_ hb'
    linarith

/-- Regime B: `0.47 k < r ≤ 3k/5`, with the cut `t0 = ⌊41k/300⌋ + 1`. -/
private theorem caseB {k r rq : ℕ} (hk : 82 ≤ k) (h47 : 47 * k < 100 * r) (h35 : 5 * r ≤ 3 * k)
    (h3 : 3 * rq ≤ k) (hpos : ∀ j, k + rq ≤ j → j < k + r → 0 < dq k j) :
    0 < dq k (k + r) := by
  obtain ⟨t0, ht0⟩ : ∃ t0, t0 = 41 * k / 300 + 1 := ⟨_, rfl⟩
  have hK82 : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  obtain ⟨hT1, hT2⟩ := cut_bounds (σ := 41 / 300) (a := 41) (b := 300) (k := k) (t := t0)
    (by norm_num) (by norm_num) (by omega) (by omega)
  have hN : ((k + r : ℕ) : ℝ) ≤ 8 / 5 * (k : ℝ) := by
    have h1 : (5 : ℝ) * ((k + r : ℕ) : ℝ) ≤ 8 * (k : ℝ) := by
      exact_mod_cast (by omega : 5 * (k + r) ≤ 8 * k)
    linarith
  have hE0 : Real.exp (5 * (41 / 300 : ℝ)) ≤ 2 := by
    rw [show (5 : ℝ) * (41 / 300) = 41 / 60 by norm_num]
    exact exp_41_60
  have hnum : (1 : ℝ) ^ 2 * (8 / 5) ^ 2 * 2
      ≤ (99 / 100) ^ 2 * (8 * (314 / 100) * (41 / 300) ^ 3 * (k : ℝ)) := by
    norm_num
    linarith
  have hP := P1_le (k := k) (t := t0) (by omega) (by omega) (41 / 300) (8 / 5) 2 1
    ((k + r : ℕ) : ℝ) (99 / 100) (by norm_num) (by norm_num) (by linarith) hT1 hT2 hE0
    (Nat.cast_nonneg _) hN (by norm_num) hnum
  -- `(2/n - ε_{t0+1} x^{t0}) β_{n-1} ≤ δ_n`, with a positive left side
  have h := near_struct (t0 := t0) (by omega : 2 ≤ k) (by omega) (by omega) (by omega) h35
    (fun j hj1 hj2 => (hpos j (by omega) hj2).le)
  have hU := bq_chain_pos (l := k - 1) (by omega) (k + r - 1) (by omega) (by omega)
  have hn0 : (0 : ℝ) < ((k + r : ℕ) : ℝ) := by
    exact_mod_cast (by omega : 0 < k + r)
  have hc : 0 < 2 / ((k + r : ℕ) : ℝ) - eps (t0 + 1) * xk k ^ t0 := by
    rw [sub_pos, lt_div_iff₀ hn0]
    linarith
  exact lt_of_lt_of_le (mul_pos hc hU) h

/-- The rows `r = ρ + 1 > 3k/5`, given the bounds `p` of the near term and `q` of the far term
with `p + q < 1`.  The far term is bounded through `ρ + 1 ≤ c² k`, `ρ + 1 ≥ r0` and
`∑_{i ≤ ρ - 3k/5} G_i ≤ SGc · e`. -/
private theorem far_common {k ρ t0 : ℕ} (hk : 82 ≤ k) (hr : ρ + 2 ≤ k) (hrM : 3 * k / 5 ≤ ρ)
    (ht0 : 1 ≤ t0) (hcap : t0 + 1 ≤ 3 * k / 5)
    (hpos : ∀ j, k + (ρ + 1) - t0 ≤ j → j < k + (ρ + 1) → 0 ≤ dq k j)
    (p q c r0 SGc : ℝ) (hc : 0 ≤ c) (hR : (ρ : ℝ) + 1 ≤ c ^ 2 * (k : ℝ))
    (hr0 : 6 ≤ r0) (hr0R : r0 ≤ (ρ : ℝ) + 1) (hq0 : 0 ≤ q) (hSGc : 0 ≤ SGc)
    (hSG : ∑ i ∈ range (ρ - 3 * k / 5 + 1), Gres i ≤ SGc * Real.exp 1)
    (hq : 105 / 100 * SGc * ((1 + c ^ 2) * c ^ 3)
      ≤ 2 * q * ((1 - 1 / (12 * r0)) * (4 - 21 / r0)))
    (hP : ((k + (ρ + 1) : ℕ) : ℝ) / 2 * (eps (t0 + 1) * xk k ^ t0) ≤ p)
    (hpq : p + q < 1) :
    0 < dq k (k + (ρ + 1)) := by
  have hK82 : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK : (0 : ℝ) < (k : ℝ) := by linarith
  have hR0 : (0 : ℝ) < (ρ : ℝ) + 1 := by positivity
  have hstruct := far_struct hk hr hrM ht0 hcap hpos
  have hn : ((k + (ρ + 1) : ℕ) : ℝ) = (k : ℝ) + ((ρ : ℝ) + 1) := by
    rw [Nat.cast_add, Nat.cast_add, Nat.cast_one]
  have hn0 : (0 : ℝ) < ((k + (ρ + 1) : ℕ) : ℝ) := by
    rw [hn]
    linarith
  have hfar := far_num (k : ℝ) ((ρ : ℝ) + 1) (∑ i ∈ range (ρ - 3 * k / 5 + 1), Gres i)
    (Gres ρ) q ((1 + c ^ 2) * c ^ 3) ((1 - 1 / (12 * r0)) * (4 - 21 / r0)) SGc hK hR0 hSG hSGc
    (Gres_lower (s := ρ) (by omega))
    (nu_bound (k : ℝ) ((ρ : ℝ) + 1) c hK hR0.le hc hR)
    (D_bound ((ρ : ℝ) + 1) r0 hr0 hr0R) hq0 hq
  rw [← hn] at hfar
  have hU := bq_chain_pos (l := k - 1) (by omega) (k + (ρ + 1) - 1) (by omega) (by omega)
  exact far_final ((k + (ρ + 1) : ℕ) : ℝ) (eps (t0 + 1) * xk k ^ t0)
    (105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k)) (∑ i ∈ range (ρ - 3 * k / 5 + 1), Gres i)
    (Gres ρ) (bq (k - 1) (k + (ρ + 1) - 1)) (dq k (k + (ρ + 1))) p q hn0 (Gres_pos ρ) hU
    hstruct hP hfar hpq

/-- Regime α: `3k/5 < r ≤ 4k/5`, with the cut `t0 = ⌊4k/15⌋ + 1`. -/
private theorem caseAlpha {k r rq : ℕ} (hk : 82 ≤ k) (h35 : 3 * k < 5 * r) (h45 : 5 * r ≤ 4 * k)
    (h3 : 3 * rq ≤ k) (hpos : ∀ j, k + rq ≤ j → j < k + r → 0 < dq k j) :
    0 < dq k (k + r) := by
  obtain ⟨ρ, rfl⟩ : ∃ ρ, r = ρ + 1 := ⟨r - 1, by omega⟩
  obtain ⟨t0, ht0⟩ : ∃ t0, t0 = 4 * k / 15 + 1 := ⟨_, rfl⟩
  have hK82 : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  obtain ⟨hT1, hT2⟩ := cut_bounds (σ := 4 / 15) (a := 4) (b := 15) (k := k) (t := t0)
    (by norm_num) (by norm_num) (by omega) (by omega)
  have hN : ((k + (ρ + 1) : ℕ) : ℝ) ≤ 9 / 5 * (k : ℝ) := by
    have h1 : (5 : ℝ) * ((k + (ρ + 1) : ℕ) : ℝ) ≤ 9 * (k : ℝ) := by
      exact_mod_cast (by omega : 5 * (k + (ρ + 1)) ≤ 9 * k)
    linarith
  have hE0 : Real.exp (5 * (4 / 15 : ℝ)) ≤ 38 / 10 := by
    rw [show (5 : ℝ) * (4 / 15) = 4 / 3 by norm_num]
    exact exp_4_3
  have hnum : (1 : ℝ) ^ 2 * (9 / 5) ^ 2 * (38 / 10)
      ≤ (57 / 100) ^ 2 * (8 * (314 / 100) * (4 / 15) ^ 3 * (k : ℝ)) := by
    norm_num
    linarith
  have hP := P1_le (k := k) (t := t0) (by omega) (by omega) (4 / 15) (9 / 5) (38 / 10) 1
    ((k + (ρ + 1) : ℕ) : ℝ) (57 / 100) (by norm_num) (by norm_num) (by linarith) hT1 hT2 hE0
    (Nat.cast_nonneg _) hN (by norm_num) hnum
  have hR : (ρ : ℝ) + 1 ≤ (8945 / 10000 : ℝ) ^ 2 * (k : ℝ) := by
    have h1 : (5 : ℝ) * ((ρ : ℝ) + 1) ≤ 4 * (k : ℝ) := by exact_mod_cast h45
    norm_num
    linarith
  have hr0R : (50 : ℝ) ≤ (ρ : ℝ) + 1 := by
    exact_mod_cast (by omega : 50 ≤ ρ + 1)
  exact far_common hk (by omega) (by omega) (by omega) (by omega)
    (fun j hj1 hj2 => (hpos j (by omega) hj2).le)
    (57 / 100) (385 / 1000) (8945 / 10000) 50 2 (by norm_num) hR (by norm_num) hr0R
    (by norm_num) (by norm_num) (Gres_sum_le _) (by norm_num) hP (by norm_num)

/-- Regime β: `4k/5 < r ≤ k - 1`, with the cut `t0 = ⌊7k/15⌋ + 1`. -/
private theorem caseBeta {k r rq : ℕ} (hk : 82 ≤ k) (h45 : 4 * k < 5 * r) (hr : r + 1 ≤ k)
    (h3 : 3 * rq ≤ k) (hpos : ∀ j, k + rq ≤ j → j < k + r → 0 < dq k j) :
    0 < dq k (k + r) := by
  obtain ⟨ρ, rfl⟩ : ∃ ρ, r = ρ + 1 := ⟨r - 1, by omega⟩
  obtain ⟨t0, ht0⟩ : ∃ t0, t0 = 7 * k / 15 + 1 := ⟨_, rfl⟩
  have hK82 : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  obtain ⟨hT1, hT2⟩ := cut_bounds (σ := 7 / 15) (a := 7) (b := 15) (k := k) (t := t0)
    (by norm_num) (by norm_num) (by omega) (by omega)
  have hN : ((k + (ρ + 1) : ℕ) : ℝ) ≤ 2 * (k : ℝ) := by
    exact_mod_cast (by omega : k + (ρ + 1) ≤ 2 * k)
  have hE0 : Real.exp (5 * (7 / 15 : ℝ)) ≤ 1032 / 100 := by
    rw [show (5 : ℝ) * (7 / 15) = 7 / 3 by norm_num]
    exact exp_7_3
  have hR : (ρ : ℝ) + 1 ≤ (1 : ℝ) ^ 2 * (k : ℝ) := by
    have h1 : (ρ : ℝ) + 1 ≤ (k : ℝ) := by exact_mod_cast (by omega : ρ + 1 ≤ k)
    linarith
  -- the near term, for a bound `p` chosen below
  have hP : ∀ p : ℝ, 0 ≤ p →
      (1011 / 1000 : ℝ) ^ 2 * 2 ^ 2 * (1032 / 100)
        ≤ p ^ 2 * (8 * (314 / 100) * (7 / 15) ^ 3 * (k : ℝ)) →
      ((k + (ρ + 1) : ℕ) : ℝ) / 2 * (eps (t0 + 1) * xk k ^ t0) ≤ p := fun p hp hnum =>
    P1_le (k := k) (t := t0) (by omega) (by omega) (7 / 15) 2 (1032 / 100) (1011 / 1000)
      ((k + (ρ + 1) : ℕ) : ℝ) p (by norm_num) (by norm_num) (by linarith) hT1 hT2
      hE0 (Nat.cast_nonneg _) hN hp hnum
  rcases Nat.lt_or_ge k 110 with hk110 | hk110
  · -- `82 ≤ k ≤ 109`: the partial sums of the resolvent kernel are bounded through its tail
    have hr0R : (66 : ℝ) ≤ (ρ : ℝ) + 1 := by
      exact_mod_cast (by omega : 66 ≤ ρ + 1)
    have hSG := SG_le_tail (a := ρ - 3 * k / 5 + 1) (by omega) (by omega)
    have hnum : (1011 / 1000 : ℝ) ^ 2 * 2 ^ 2 * (1032 / 100)
        ≤ (455 / 1000) ^ 2 * (8 * (314 / 100) * (7 / 15) ^ 3 * (k : ℝ)) := by
      norm_num
      linarith
    exact far_common hk (by omega) (by omega) (by omega) (by omega)
      (fun j hj1 hj2 => (hpos j (by omega) hj2).le)
      (455 / 1000) (50 / 100) 1 66 (2 - 253 / 1000) (by norm_num) hR (by norm_num) hr0R
      (by norm_num) (by norm_num) hSG (by norm_num)
      (hP (455 / 1000) (by norm_num) hnum) (by norm_num)
  · -- `k ≥ 110`
    have hK110 : (110 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk110
    have hr0R : (89 : ℝ) ≤ (ρ : ℝ) + 1 := by
      exact_mod_cast (by omega : 89 ≤ ρ + 1)
    have hnum : (1011 / 1000 : ℝ) ^ 2 * 2 ^ 2 * (1032 / 100)
        ≤ (395 / 1000) ^ 2 * (8 * (314 / 100) * (7 / 15) ^ 3 * (k : ℝ)) := by
      norm_num
      linarith
    exact far_common hk (by omega) (by omega) (by omega) (by omega)
      (fun j hj1 hj2 => (hpos j (by omega) hj2).le)
      (395 / 1000) (56 / 100) 1 89 2 (by norm_num) hR (by norm_num) hr0R
      (by norm_num) (by norm_num) (Gres_sum_le _) (by norm_num)
      (hP (395 / 1000) (by norm_num) hnum) (by norm_num)

/-- **The rows beyond `k + 0.47 k`.**  If column `k ≥ 82` is positive on the rows
`k + rq ≤ j < k + r`, where `rq ≤ k/3` and `0.47 k < r ≤ k - 1`, then it is positive at the row
`k + r`. -/
theorem caseFar {k r rq : ℕ} (hk : 82 ≤ k) (h47 : 47 * k < 100 * r) (hr : r + 1 ≤ k)
    (h3 : 3 * rq ≤ k) (hpos : ∀ j, k + rq ≤ j → j < k + r → 0 < dq k j) :
    0 < dq k (k + r) := by
  rcases Nat.lt_or_ge (3 * k) (5 * r) with h5 | h5
  · rcases Nat.lt_or_ge (4 * k) (5 * r) with h4 | h4
    · exact caseBeta hk h4 hr h3 hpos
    · exact caseAlpha hk h5 h4 h3 hpos
  · exact caseB hk h47 h5 h3 hpos

end Parking
