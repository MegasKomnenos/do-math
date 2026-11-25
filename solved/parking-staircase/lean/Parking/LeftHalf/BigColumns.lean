import Parking.ChainColumn.Main
import Parking.LeftHalf.KernelDecay

/-!
# The columns `k ≥ 82` on the rows `n ≥ 2k`

`big_columns`: for `k ≥ 82` and `n ≥ 2k`, `b_{n,k} > b_{n,k-1}`.

Let `q` be a row of the column with `k < q ≤ k + 27k/100`, `d ≤ 0` on `[k, q)` and `d > 0` on
`[q, 2k-1]`.  From such a row, the rows `n ≥ 2k` are obtained by strong induction with
`big_step`: writing `x = x_k`, `η_j = d_{j,k} x^j/j!`, `U_j = b_{j,k-1} x^j/j!`, `κ_m` the tilted
prime kernel and `L = n - q + 1`,

1. `n η_n ≥ 2x U_{n-1} + (k+1) x η_{n-1} + n ∑_{j=k}^{n-1} κ_{n-j} η_j`   (column inequality
   `col_eq_all`, tilted);
2. `κ_{n-j} η_j ≥ (κ_L/(2k-1)) Ψ′(j) η_j` for every `j` (the order of the kernel weights,
   `order_neg`, `order_pos`, and the signs of `η_j`), and `∑_{j=k}^{n-1} Ψ′(j) η_j ≥ -𝔇` with the
   weighted debt `𝔇` (`weighted_debt`);
3. `𝔇` is bounded by `U_{n-1}` and `η_{n-1}` (the diagonal lower bound `Ut_diag_lower`, and
   `lemma_S`);
4. `n (n-1) κ_L ≤ 3.762 √k` (`T_bound`, from the decay of the kernel and its values on the free
   range), which makes both resulting coefficients nonnegative, one of them strictly
   (`big_numeric`, `big_core`).

**The column mass dominates the environment** (`lemma_S`).  For a column `k ≥ 2`, a tilt `x ≥ 0`
at which the tilted environment `b_N = zrT k x N` is nonincreasing, `0 ≤ J ≤ k - 1` and
`M ≥ k - 1 + J`:

  `x · (∑_{j ≤ J} c_j x^j) · b_M ≤ (M + 1) · U_{M+1}`,   `U = Ut k x = b - d`,

where `d_N = zrT (k-1) x N` is the environment of the threshold `k - 1`.  Indeed, subtracting the
tilted last-car recursions of the thresholds `k` and `k - 1` (`zrT_succ`) gives
`(M+1) U_{M+1} = x ∑_{i ≤ M} F_i` with
`F_i = min(i+1,k) b_i b_{M-i} - min(i+1,k-1) d_i d_{M-i}`.
Every `F_i` is nonnegative (`d ≤ b`), and for `i = M - j` with `j ≤ J` (so `i ≥ k - 1`)
`F_i = k b_i b_j - (k-1) d_i d_j ≥ b_i b_j ≥ b_M · c_j x^j`.

The numerical facts used in step 4:

* `xcrit_ge`    : `x_k ≥ e^{-1} ≥ 0.3678` for `k ≥ 1`;
* `W8_ge`       : `∑_{j ≤ 8} c_j x^j ≥ 2.01` for `x ≥ 0.3678`;
* `sqrt_ge`     : `√K ≥ 9.05` for `K ≥ 82`;
* `big_numeric` : if `T ≤ 3.762 √K` (with `K ≥ 82`, `x ≥ 0.3678`, `W ≥ 2.01`) then
  `T (2 + 1/K + 1/(x W)) ≤ 2 x (2K - 1)` and `T < x K (2K - 1)`;
* `big_core`    : the real-variable form of the row step of the columns `k ≥ 82`.
-/

namespace Parking
open Finset

/-! ### The column mass dominates the environment -/

/-- **The column mass dominates the environment.**  If the tilted environment of the threshold
`k` is nonincreasing at the tilt `x ≥ 0`, then `x (∑_{j ≤ J} c_j x^j) b_M ≤ (M + 1) U_{M+1}` for
`J ≤ k - 1` and `M ≥ k - 1 + J`. -/
private theorem lemma_S {k : ℕ} (hk : 2 ≤ k) {x : ℝ} (hx : 0 ≤ x)
    (hanti : ∀ N, zrT k x (N + 1) ≤ zrT k x N) {J M : ℕ} (hJ : J + 1 ≤ k) (hM : k - 1 + J ≤ M) :
    x * (∑ j ∈ range (J + 1), ccT x j) * zrT k x M ≤ ((M : ℝ) + 1) * Ut k x (M + 1) := by
  have hk1 : 1 ≤ k := by omega
  have hk1' : 1 ≤ k - 1 := by omega
  have hdb : ∀ N, zrT (k - 1) x N ≤ zrT k x N := zrT_le_zrT (Nat.sub_le k 1) hx
  have hb0 : ∀ N, 0 ≤ zrT k x N := zrT_nonneg k hx
  have hd0 : ∀ N, 0 ≤ zrT (k - 1) x N := zrT_nonneg (k - 1) hx
  -- the terms of the difference of the two recursions
  obtain ⟨F, hF⟩ : ∃ F : ℕ → ℝ, ∀ i, F i = ((min (i + 1) k : ℕ) : ℝ) * zrT k x i * zrT k x (M - i)
      - ((min (i + 1) (k - 1) : ℕ) : ℝ) * zrT (k - 1) x i * zrT (k - 1) x (M - i) :=
    ⟨_, fun _ => rfl⟩
  have hU : ((M : ℝ) + 1) * Ut k x (M + 1) = x * ∑ i ∈ range (M + 1), F i := by
    simp only [hF]
    rw [Ut, mul_sub, zrT_succ hk1 x M, zrT_succ hk1' x M, ← mul_sub, ← Finset.sum_sub_distrib]
  -- every term is nonnegative
  have hF0 : ∀ i, 0 ≤ F i := by
    intro i
    have hmin : ((min (i + 1) (k - 1) : ℕ) : ℝ) ≤ ((min (i + 1) k : ℕ) : ℝ) :=
      Nat.cast_le.mpr (by omega)
    have h1 : ((min (i + 1) (k - 1) : ℕ) : ℝ) * zrT (k - 1) x i
        ≤ ((min (i + 1) k : ℕ) : ℝ) * zrT k x i :=
      mul_le_mul hmin (hdb i) (hd0 i) (Nat.cast_nonneg _)
    rw [hF]
    exact sub_nonneg.mpr
      (mul_le_mul h1 (hdb (M - i)) (hd0 (M - i)) (mul_nonneg (Nat.cast_nonneg _) (hb0 i)))
  -- the terms with first index `M - j`, `j ≤ J`
  have hFJ : ∀ j, j < J + 1 → zrT k x M * (ccT x j) ≤ F (M - j) := by
    intro j hj
    rw [hF, show min (M - j + 1) k = k by omega, show min (M - j + 1) (k - 1) = k - 1 by omega,
      show M - (M - j) = j by omega, Nat.cast_sub hk1, Nat.cast_one,
      ← zrT_eq_ccT hk1 x (show j ≤ k by omega)]
    have hbi : zrT k x M ≤ zrT k x (M - j) := antitone_nat_of_succ_le hanti (Nat.sub_le M j)
    have hdd : zrT (k - 1) x (M - j) * zrT (k - 1) x j ≤ zrT k x (M - j) * zrT k x j :=
      mul_le_mul (hdb (M - j)) (hdb j) (hd0 j) (hb0 (M - j))
    have hk0 : (0 : ℝ) ≤ (k : ℝ) - 1 := by
      have hk1r : (1 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk1
      linarith
    have h3 := mul_le_mul_of_nonneg_left hdd hk0
    have h4 := mul_le_mul_of_nonneg_right hbi (hb0 j)
    linarith
  calc x * (∑ j ∈ range (J + 1), ccT x j) * zrT k x M
      = x * ∑ j ∈ range (J + 1), zrT k x M * (ccT x j) := by
        rw [mul_assoc, mul_comm (∑ j ∈ range (J + 1), ccT x j) (zrT k x M), Finset.mul_sum]
    _ ≤ x * ∑ j ∈ range (J + 1), F (M - j) :=
        mul_le_mul_of_nonneg_left
          (Finset.sum_le_sum fun j hj => hFJ j (Finset.mem_range.mp hj)) hx
    _ ≤ x * ∑ j ∈ range (M + 1), F (M - j) := by
        refine mul_le_mul_of_nonneg_left
          (Finset.sum_le_sum_of_subset_of_nonneg (fun j hj => ?_) fun j _ _ => hF0 _) hx
        rw [Finset.mem_range] at hj ⊢
        omega
    _ = x * ∑ i ∈ range (M + 1), F i := by
        rw [← Finset.sum_range_reflect F (M + 1)]
        simp only [Nat.add_sub_cancel]
    _ = ((M : ℝ) + 1) * Ut k x (M + 1) := hU.symm

/-! ### Numerical facts -/

/-- The critical tilt is at least `e^{-1}`; in particular `0.3678 ≤ x_k`.
(`x_k (1+1/k)^{k-1} = 1` and `(1+1/k)^{k-1} ≤ e^{(k-1)/k} ≤ e`.) -/
private theorem xcrit_ge {k : ℕ} (hk : 1 ≤ k) : (3678 : ℝ) / 10000 ≤ xcrit k := by
  have hK0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have h1 : 1 + 1 / (k : ℝ) ≤ Real.exp (1 / (k : ℝ)) := by
    have h := Real.add_one_le_exp (1 / (k : ℝ))
    linarith
  have h0 : (0 : ℝ) ≤ 1 + 1 / (k : ℝ) := by positivity
  have h2 : (1 + 1 / (k : ℝ)) ^ (k - 1) ≤ Real.exp (1 / (k : ℝ)) ^ (k - 1) :=
    pow_le_pow_left₀ h0 h1 (k - 1)
  have h3 : Real.exp (1 / (k : ℝ)) ^ (k - 1) = Real.exp (((k - 1 : ℕ) : ℝ) * (1 / (k : ℝ))) := by
    rw [← Real.exp_nat_mul]
  have h4 : ((k - 1 : ℕ) : ℝ) * (1 / (k : ℝ)) ≤ 1 := by
    rw [Nat.cast_sub hk, Nat.cast_one, mul_one_div, div_le_one hK0]
    linarith
  have h5 : (1 + 1 / (k : ℝ)) ^ (k - 1) ≤ Real.exp 1 := by
    rw [h3] at h2
    exact le_trans h2 (Real.exp_le_exp.mpr h4)
  have hx0 : 0 < xcrit k := xcrit_pos k
  have h6 : xcrit k * (1 + 1 / (k : ℝ)) ^ (k - 1) ≤ xcrit k * Real.exp 1 :=
    mul_le_mul_of_nonneg_left h5 hx0.le
  rw [xcrit_mul_psi hk] at h6
  have h7 : xcrit k * Real.exp 1 ≤ xcrit k * 2.7182818286 :=
    mul_le_mul_of_nonneg_left Real.exp_one_lt_d9.le hx0.le
  linarith

/-- `∑_{j ≤ 8} c_j x^j ≥ 2.01` for `x ≥ 0.3678`. -/
private theorem W8_ge {x : ℝ} (hx : (3678 : ℝ) / 10000 ≤ x) :
    (201 : ℝ) / 100 ≤ ∑ j ∈ range (8 + 1), ccT x j := by
  have h0 : (201 : ℝ) / 100 ≤ ∑ j ∈ range (8 + 1), ccT ((3678 : ℝ) / 10000) j := by
    norm_num [Finset.sum_range_succ, ccT, cc_eq, Nat.factorial]
  refine le_trans h0 (Finset.sum_le_sum fun j _ => ?_)
  exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (by norm_num) hx j) (cc_pos j).le

/-- `√K ≥ 9.05` for `K ≥ 82`. -/
private theorem sqrt_ge {K : ℝ} (hK : 82 ≤ K) : (905 : ℝ) / 100 ≤ Real.sqrt K := by
  have h1 : ((905 : ℝ) / 100) ^ 2 ≤ 82 := by norm_num
  exact Real.le_sqrt_of_sq_le (le_trans h1 hK)

/-- The two numerical conditions of the row step, from `T ≤ 3.762 √K`. -/
private theorem big_numeric {x K W T : ℝ} (hx : (3678 : ℝ) / 10000 ≤ x) (hK : 82 ≤ K)
    (hW : (201 : ℝ) / 100 ≤ W) (hT0 : 0 ≤ T) (hT : T ≤ 3762 / 1000 * Real.sqrt K) :
    T * (2 + 1 / K + 1 / (x * W)) ≤ 2 * x * (2 * K - 1) ∧ T < x * K * (2 * K - 1) := by
  have hK0 : 0 < K := by linarith
  -- `s = √K ≥ 9.05`
  obtain ⟨s, hsdef⟩ : ∃ s, s = Real.sqrt K := ⟨_, rfl⟩
  have hs : s ^ 2 = K := by
    rw [hsdef]
    exact Real.sq_sqrt hK0.le
  have hs0 : (905 : ℝ) / 100 ≤ s := by
    rw [hsdef]
    exact sqrt_ge hK
  rw [← hsdef] at hT
  have h1 : 1 / K ≤ 122 / 10000 := by
    rw [div_le_iff₀ hK0]
    linarith
  have hxW : (739278 : ℝ) / 1000000 ≤ x * W := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hx) (sub_nonneg.mpr hW)]
  have hxW0 : 0 < x * W := by linarith
  have h2 : 1 / (x * W) ≤ 1353 / 1000 := by
    rw [div_le_iff₀ hxW0]
    linarith
  have hB : 2 + 1 / K + 1 / (x * W) ≤ 33652 / 10000 := by linarith
  have a2 : (0 : ℝ) ≤ 2 * K - 1 := by linarith
  constructor
  · have a1 : T * (2 + 1 / K + 1 / (x * W)) ≤ T * (33652 / 10000) :=
      mul_le_mul_of_nonneg_left hB hT0
    have a3 : 2 * (3678 / 10000) * (2 * K - 1) ≤ 2 * x * (2 * K - 1) := by
      nlinarith [mul_nonneg (sub_nonneg.mpr hx) a2]
    have a4 : 3762 / 1000 * s * (33652 / 10000) ≤ 2 * (3678 / 10000) * (2 * K - 1) := by
      rw [← hs]
      nlinarith [mul_nonneg (sub_nonneg.mpr hs0) (sub_nonneg.mpr hs0)]
    linarith
  · have b1 : s ≤ K := by
      rw [← hs]
      nlinarith [mul_nonneg (show (0 : ℝ) ≤ s by linarith) (show (0 : ℝ) ≤ s - 1 by linarith)]
    have b2 : T ≤ 3762 / 1000 * K := by linarith
    have b0 : 0 ≤ K * (2 * K - 1) := mul_nonneg hK0.le a2
    have b3 : (3678 : ℝ) / 10000 * K * (2 * K - 1) ≤ x * K * (2 * K - 1) := by
      nlinarith [mul_nonneg (sub_nonneg.mpr hx) b0]
    nlinarith [mul_nonneg hK0.le (show (0 : ℝ) ≤ 2 * K - 164 by linarith)]

/-- The real-variable core of the row step.  `U1 = U_{n-1}`, `U2 = U_{n-2}`, `b1 = b_{n-1}`,
`η1 = η_{n-1} > 0`, `ηn = η_n`, `S` the kernel sum, `ω = κ_L/(2K-1)`, `Ψ2 = Ψ′(n-2)`. -/
private theorem big_core {x K N ω U1 U2 b1 η1 ηn S Ψ2 W : ℝ}
    (hx : 0 < x) (hK : 82 ≤ K) (hN : 2 * K ≤ N) (hω0 : 0 ≤ ω)
    (hU1 : 0 ≤ U1) (hU2 : 0 ≤ U2) (hb1 : 0 ≤ b1) (hη1 : 0 < η1) (hW : 0 < W)
    (hΨlo : N - 2 ≤ Ψ2) (hΨhi : Ψ2 ≤ N - 1)
    (h1 : (K + 1) * x * η1 + 2 * x * U1 ≤ N * (ηn - S))
    (h2 : -(ω * ((N - 1) * U1 + Ψ2 * U2 + ((N - 1) - Ψ2) * b1)) ≤ S)
    (h3 : K * U2 ≤ (K + 1) * (U1 + η1))
    (h4 : x * W * b1 ≤ (N - 1) * U1)
    (hA : N * (N - 1) * ω * (2 + 1 / K + 1 / (x * W)) ≤ 2 * x)
    (hB : N * (N - 1) * ω < x * K) : 0 < ηn := by
  have hK0 : 0 < K := by linarith
  have hKne : K ≠ 0 := hK0.ne'
  have hN1 : 0 ≤ N - 1 := by linarith
  have hN0 : 0 < N := by linarith
  have hxW : 0 < x * W := mul_pos hx hW
  have hxWne : x * W ≠ 0 := hxW.ne'
  obtain ⟨ik, hik⟩ : ∃ ik : ℝ, ik = 1 / K := ⟨_, rfl⟩
  obtain ⟨iw, hiw⟩ : ∃ iw : ℝ, iw = 1 / (x * W) := ⟨_, rfl⟩
  have hik0 : 0 < ik := by
    rw [hik]
    exact one_div_pos.mpr hK0
  have hiw0 : 0 < iw := by
    rw [hiw]
    exact one_div_pos.mpr hxW
  have hikK : ik * K = 1 := by
    rw [hik]
    exact one_div_mul_cancel hKne
  have hiwW : iw * (x * W) = 1 := by
    rw [hiw]
    exact one_div_mul_cancel hxWne
  rw [← hik, ← hiw] at hA
  -- `U2 ≤ (1 + 1/K) (U1 + η1)`
  have hU2' : U2 ≤ (1 + ik) * (U1 + η1) := by
    have h := mul_le_mul_of_nonneg_left h3 hik0.le
    have e1 : ik * (K * U2) = U2 := by linear_combination U2 * hikK
    have e2 : ik * ((K + 1) * (U1 + η1)) = (1 + ik) * (U1 + η1) := by
      linear_combination (U1 + η1) * hikK
    rw [e1, e2] at h
    exact h
  -- `b1 ≤ (N-1) U1 / (x W)`
  have hb1' : b1 ≤ iw * ((N - 1) * U1) := by
    have h := mul_le_mul_of_nonneg_left h4 hiw0.le
    have e1 : iw * (x * W * b1) = b1 := by linear_combination b1 * hiwW
    rw [e1] at h
    exact h
  -- the debt
  have hD : (N - 1) * U1 + Ψ2 * U2 + ((N - 1) - Ψ2) * b1
      ≤ (N - 1) * (U1 * (2 + ik + iw) + (1 + ik) * η1) := by
    have a1 : Ψ2 * U2 ≤ (N - 1) * U2 := mul_le_mul_of_nonneg_right hΨhi hU2
    have a2 : (N - 1) * U2 ≤ (N - 1) * ((1 + ik) * (U1 + η1)) :=
      mul_le_mul_of_nonneg_left hU2' hN1
    have a3 : ((N - 1) - Ψ2) * b1 ≤ 1 * b1 :=
      mul_le_mul_of_nonneg_right (by linarith) hb1
    have a4 : (N - 1) * (U1 * (2 + ik + iw) + (1 + ik) * η1)
        = (N - 1) * U1 + (N - 1) * ((1 + ik) * (U1 + η1)) + iw * ((N - 1) * U1) := by ring
    rw [a4]
    linarith
  have hS : -(ω * ((N - 1) * (U1 * (2 + ik + iw) + (1 + ik) * η1))) ≤ S := by
    have h := mul_le_mul_of_nonneg_left hD hω0
    linarith
  have hmain : (K + 1) * x * η1 + 2 * x * U1
      - N * (ω * ((N - 1) * (U1 * (2 + ik + iw) + (1 + ik) * η1))) ≤ N * ηn := by
    have h := mul_le_mul_of_nonneg_left hS hN0.le
    have e : N * (ηn - S) = N * ηn - N * S := by ring
    rw [e] at h1
    linarith
  have hbr1 : 0 ≤ U1 * (2 * x - N * (N - 1) * ω * (2 + ik + iw)) :=
    mul_nonneg hU1 (by linarith)
  have hR : N * (N - 1) * ω * ik < x := by
    have h := mul_lt_mul_of_pos_right hB hik0
    have e : x * K * ik = x := by linear_combination x * hikK
    rw [e] at h
    exact h
  have hbr2 : 0 < η1 * ((K + 1) * (x - N * (N - 1) * ω * ik)) :=
    mul_pos hη1 (mul_pos (by linarith) (by linarith))
  have e : (K + 1) * x * η1 + 2 * x * U1
      - N * (ω * ((N - 1) * (U1 * (2 + ik + iw) + (1 + ik) * η1)))
      = U1 * (2 * x - N * (N - 1) * ω * (2 + ik + iw))
        + η1 * ((K + 1) * (x - N * (N - 1) * ω * ik)) := by
    linear_combination (η1 * N * (N - 1) * ω) * hikK
  rw [e] at hmain
  have hfin : 0 < N * ηn := by linarith
  exact pos_of_mul_pos_right hfin hN0.le

/-! ### The row step and the conclusion -/

/-- `U⁺ = U + η`: the column masses of the levels `k` and `k-1`. -/
private theorem Ut_succ_eq {k : ℕ} (hk : 2 ≤ k) (x : ℝ) (j : ℕ) :
    Ut (k + 1) x j = Ut k x j + dq k j * x ^ j := by
  have h1 := Ut_eq_bq (show 2 ≤ k + 1 by omega) x j
  rw [Nat.add_sub_cancel] at h1
  rw [h1, Ut_eq_bq hk, dq]
  ring

/-- The column inequality, tilted and with the kernel sum indexed by the row `j = n - m`:
`(k+1) x η_{n-1} + 2x U_{n-1} ≤ n (η_n - ∑_{j=k}^{n-1} κ_{n-j} η_j)`. -/
private theorem col_eq_tilt {k n : ℕ} (hk : 2 ≤ k) (hn : k + 1 ≤ n) {x : ℝ} (hx : 0 ≤ x) :
    ((k : ℝ) + 1) * x * (dq k (n - 1) * x ^ (n - 1)) + 2 * x * Ut k x (n - 1)
      ≤ (n : ℝ) * (dq k n * x ^ n
          - ∑ j ∈ Icc k (n - 1), kqT k x (n - j) * (dq k j * x ^ j)) := by
  have hs : (∑ m ∈ Icc 1 (n - k), kq k m * dq k (n - m)) * x ^ n
      = ∑ j ∈ Icc k (n - 1), kqT k x (n - j) * (dq k j * x ^ j) := by
    rw [Finset.sum_mul]
    refine Finset.sum_nbij' (fun m => n - m) (fun j => n - j) ?_ ?_ ?_ ?_ ?_
    · intro m hm
      rw [Finset.mem_Icc] at hm
      exact Finset.mem_Icc.mpr (show k ≤ n - m ∧ n - m ≤ n - 1 by omega)
    · intro j hj
      rw [Finset.mem_Icc] at hj
      exact Finset.mem_Icc.mpr (show 1 ≤ n - j ∧ n - j ≤ n - k by omega)
    · intro m hm
      rw [Finset.mem_Icc] at hm
      show n - (n - m) = m
      omega
    · intro j hj
      rw [Finset.mem_Icc] at hj
      show n - (n - j) = j
      omega
    · intro m hm
      rw [Finset.mem_Icc] at hm
      show kq k m * dq k (n - m) * x ^ n = kqT k x (n - (n - m)) * (dq k (n - m) * x ^ (n - m))
      rw [show n - (n - m) = m by omega, kqT, show x ^ n = x ^ m * x ^ (n - m) by
        rw [← pow_add, Nat.add_sub_cancel' (by omega : m ≤ n)]]
      ring
  have h := mul_le_mul_of_nonneg_right (col_eq_all hk hn) (pow_nonneg hx n)
  have e : ((k : ℝ) + 1) * x * (dq k (n - 1) * x ^ (n - 1))
        + 2 * x * (bq (k - 1) (n - 1) * x ^ (n - 1))
      = (((k : ℝ) + 1) * dq k (n - 1) + 2 * bq (k - 1) (n - 1)) * x ^ n := by
    rw [show x ^ n = x * x ^ (n - 1) by rw [← pow_succ', Nat.sub_add_cancel (by omega : 1 ≤ n)]]
    ring
  rw [Ut_eq_bq hk, e, ← hs]
  linarith

/-- The kernel weight of the crossing: `n (n-1) κ_L ≤ 3.762 √k`, `L = n - q + 1`. -/
private theorem T_bound {k q n : ℕ} (hk : 82 ≤ k) (hq1 : k + 1 ≤ q) (hq2 : 100 * (q - k) ≤ 27 * k)
    (hn : 2 * k ≤ n) :
    (n : ℝ) * ((n : ℝ) - 1) * kqT k (xcrit k) (n - q + 1) ≤ 3762 / 1000 * Real.sqrt (k : ℝ) := by
  have hk2 : 2 ≤ k := by omega
  have hK : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK0 : (0 : ℝ) < (k : ℝ) := by linarith
  obtain ⟨s, hsdef⟩ : ∃ s, s = Real.sqrt (k : ℝ) := ⟨_, rfl⟩
  have hs2 : s ^ 2 = (k : ℝ) := by
    rw [hsdef]
    exact Real.sq_sqrt hK0.le
  have hs9 : (905 : ℝ) / 100 ≤ s := by
    rw [hsdef]
    exact sqrt_ge hK
  have hs0 : 0 < s := by linarith
  have hsne : s ≠ 0 := hs0.ne'
  have hκ0 : ∀ m, 0 ≤ kqT k (xcrit k) m := fun m => kqT_nonneg hk2 (xcrit_pos k).le m
  have hqn : q ≤ n := by omega
  have hQ2 : 100 * (q : ℝ) ≤ 127 * (k : ℝ) := by
    exact_mod_cast (show 100 * q ≤ 127 * k by omega)
  have hN : 2 * (k : ℝ) ≤ (n : ℝ) := by exact_mod_cast hn
  have hN0 : (0 : ℝ) ≤ (n : ℝ) := by linarith
  have hL : ((n - q + 1 : ℕ) : ℝ) = (n : ℝ) - (q : ℝ) + 1 := by
    rw [Nat.cast_add, Nat.cast_sub hqn, Nat.cast_one]
  have hat : kqT k (xcrit k) k ≤ 662 / 1000 / ((k : ℝ) * s) := by
    rw [hsdef]
    exact le_trans (kap_at_k hk) (le_of_eq (by norm_num))
  have h1 : (n : ℝ) * ((n : ℝ) - 1) ≤ (n : ℝ) * (n : ℝ) :=
    mul_le_mul_of_nonneg_left (by linarith) hN0
  rw [← hsdef]
  rcases Nat.lt_or_ge (n - q + 1) (k + 1) with hc1 | hc1
  · -- `L ≤ k`: the free kernel far from the crossing
    have hfar : kqT k (xcrit k) (n - q + 1) ≤ 73 / 100 / ((k : ℝ) * s) := by
      rw [hsdef]
      exact le_trans (kap_far hk (by omega)) (le_of_eq (by norm_num))
    have hLk : (n : ℝ) - (q : ℝ) + 1 ≤ (k : ℝ) := by
      rw [← hL]
      exact_mod_cast (show n - q + 1 ≤ k by omega)
    have hNle : (n : ℝ) ≤ 227 / 100 * (k : ℝ) := by linarith
    have h2 : (n : ℝ) * (n : ℝ) ≤ (227 / 100 * (k : ℝ)) * (227 / 100 * (k : ℝ)) :=
      mul_le_mul hNle hNle hN0 (by linarith)
    have h3 : (n : ℝ) * ((n : ℝ) - 1) * kqT k (xcrit k) (n - q + 1)
        ≤ (227 / 100 * (k : ℝ)) * (227 / 100 * (k : ℝ)) * (73 / 100 / ((k : ℝ) * s)) :=
      mul_le_mul (le_trans h1 h2) hfar (hκ0 _) (by positivity)
    have h4 : (227 / 100 * (k : ℝ)) * (227 / 100 * (k : ℝ)) * (73 / 100 / ((k : ℝ) * s))
        = 51529 / 10000 * (73 / 100) * s := by
      rw [← hs2]
      field
    rw [h4] at h3
    linarith
  · have hLk : (k : ℝ) + 1 ≤ (n : ℝ) - (q : ℝ) + 1 := by
      rw [← hL]
      exact_mod_cast hc1
    rcases Nat.lt_or_ge (n - q + 1) (2 * k + 1) with hc2 | hc2
    · -- `k < L ≤ 2k`: harmonic decay
      have hL2k : (n : ℝ) - (q : ℝ) + 1 ≤ 2 * (k : ℝ) := by
        rw [← hL]
        exact_mod_cast (show n - q + 1 ≤ 2 * k by omega)
      have h3a := kap_K3a (L := n - q + 1) hk2 (by omega)
      rw [hL] at h3a
      obtain ⟨Lr, hLr⟩ : ∃ Lr : ℝ, Lr = (n : ℝ) - (q : ℝ) + 1 := ⟨_, rfl⟩
      rw [← hLr] at h3a hLk hL2k
      have hNle : (n : ℝ) ≤ Lr + 127 / 100 * (k : ℝ) := by
        rw [hLr]
        linarith
      have h2 : (n : ℝ) * (n : ℝ)
          ≤ (Lr + 127 / 100 * (k : ℝ)) * (Lr + 127 / 100 * (k : ℝ)) :=
        mul_le_mul hNle hNle hN0 (by linarith)
      have h2' : (Lr + 127 / 100 * (k : ℝ)) * (Lr + 127 / 100 * (k : ℝ))
          ≤ 535 / 100 * (k : ℝ) * Lr := by
        nlinarith [mul_nonneg (sub_nonneg.mpr (show (k : ℝ) ≤ Lr by linarith))
            (sub_nonneg.mpr hL2k),
          mul_nonneg hK0.le (sub_nonneg.mpr hL2k), mul_nonneg hK0.le hK0.le]
      have h3 : (n : ℝ) * ((n : ℝ) - 1) * kqT k (xcrit k) (n - q + 1)
          ≤ 535 / 100 * (k : ℝ) * Lr * kqT k (xcrit k) (n - q + 1) :=
        mul_le_mul_of_nonneg_right (le_trans h1 (le_trans h2 h2')) (hκ0 _)
      have h4 : 535 / 100 * (k : ℝ) * Lr * kqT k (xcrit k) (n - q + 1)
          ≤ 535 / 100 * (k : ℝ) * ((k : ℝ) * (662 / 1000 / ((k : ℝ) * s))) := by
        have a1 : Lr * kqT k (xcrit k) (n - q + 1) ≤ (k : ℝ) * (662 / 1000 / ((k : ℝ) * s)) :=
          le_trans h3a (mul_le_mul_of_nonneg_left hat hK0.le)
        have a2 := mul_le_mul_of_nonneg_left a1 (show (0 : ℝ) ≤ 535 / 100 * (k : ℝ) by positivity)
        linarith
      have h5 : 535 / 100 * (k : ℝ) * ((k : ℝ) * (662 / 1000 / ((k : ℝ) * s)))
          = 35417 / 10000 * s := by
        rw [← hs2]
        field
      rw [h5] at h4
      linarith
    · -- `L > 2k`: quadratic decay
      have hL2k : 2 * (k : ℝ) + 1 ≤ (n : ℝ) - (q : ℝ) + 1 := by
        rw [← hL]
        exact_mod_cast hc2
      have h3b := kap_K3b (L := n - q + 1) hk2 (by omega)
      rw [hL] at h3b
      obtain ⟨Lr, hLr⟩ : ∃ Lr : ℝ, Lr = (n : ℝ) - (q : ℝ) + 1 := ⟨_, rfl⟩
      rw [← hLr] at h3b hL2k
      have hNa : (n : ℝ) ≤ 1635 / 1000 * Lr - 1 := by
        have e : (n : ℝ) = Lr + (q : ℝ) - 1 := by
          rw [hLr]
          ring
        linarith
      have hpoly : (n : ℝ) * ((n : ℝ) - 1) ≤ 2675 / 1000 * ((Lr - 1) * Lr) := by
        nlinarith [mul_nonneg (sub_nonneg.mpr hNa)
            (show (0 : ℝ) ≤ 1635 / 1000 * Lr - 1 + (n : ℝ) - 1 by linarith),
          mul_nonneg (show (0 : ℝ) ≤ Lr by linarith) (show (0 : ℝ) ≤ Lr by linarith)]
      have h3 : (n : ℝ) * ((n : ℝ) - 1) * kqT k (xcrit k) (n - q + 1)
          ≤ 2675 / 1000 * ((Lr - 1) * Lr) * kqT k (xcrit k) (n - q + 1) :=
        mul_le_mul_of_nonneg_right hpoly (hκ0 _)
      have h4 : 2675 / 1000 * ((Lr - 1) * Lr) * kqT k (xcrit k) (n - q + 1)
          ≤ 2675 / 1000 * (2 * (k : ℝ) * (k : ℝ) * (662 / 1000 / ((k : ℝ) * s))) := by
        have a0 : 2 * (k : ℝ) * ((k : ℝ) - 1) * kqT k (xcrit k) k
            ≤ 2 * (k : ℝ) * (k : ℝ) * kqT k (xcrit k) k :=
          mul_le_mul_of_nonneg_right (by nlinarith) (hκ0 k)
        have a1 : (Lr - 1) * Lr * kqT k (xcrit k) (n - q + 1)
            ≤ 2 * (k : ℝ) * (k : ℝ) * (662 / 1000 / ((k : ℝ) * s)) :=
          le_trans h3b (le_trans a0 (mul_le_mul_of_nonneg_left hat (by positivity)))
        have a2 := mul_le_mul_of_nonneg_left a1 (show (0 : ℝ) ≤ 2675 / 1000 by norm_num)
        linarith
      have h5 : 2675 / 1000 * (2 * (k : ℝ) * (k : ℝ) * (662 / 1000 / ((k : ℝ) * s)))
          = 35417 / 10000 * s := by
        rw [← hs2]
        field
      rw [h5] at h4
      linarith

/-- **The row step** of a column `k ≥ 82`: if the column is nonpositive on `[k, q)` and positive
on `[q, n-1]`, where `k < q ≤ k + 27k/100` and `n ≥ 2k`, then it is positive in row `n`. -/
private theorem big_step {k q n : ℕ} (hk : 82 ≤ k) (hq1 : k + 1 ≤ q) (hq2 : 100 * (q - k) ≤ 27 * k)
    (hn : 2 * k ≤ n)
    (hneg : ∀ j, k ≤ j → j < q → dq k j ≤ 0) (hpos : ∀ j, q ≤ j → j ≤ n - 1 → 0 < dq k j) :
    0 < dq k n := by
  have hk2 : 2 ≤ k := by omega
  have hx : 0 < xcrit k := xcrit_pos k
  have hanti := zrT_anti_crit hk2
  have hK : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hN : 2 * (k : ℝ) ≤ (n : ℝ) := by exact_mod_cast hn
  have h2K : (0 : ℝ) < 2 * (k : ℝ) - 1 := by linarith
  -- the kernel weight `κ_L` and `ω = κ_L/(2k-1)`
  obtain ⟨κ, hκ⟩ : ∃ κ, κ = kqT k (xcrit k) (n - q + 1) := ⟨_, rfl⟩
  have hκ0 : 0 ≤ κ := by
    rw [hκ]
    exact kqT_nonneg hk2 hx.le _
  obtain ⟨ω, hω⟩ : ∃ ω, ω = κ / (2 * (k : ℝ) - 1) := ⟨_, rfl⟩
  have hω0 : 0 ≤ ω := by
    rw [hω]
    exact div_nonneg hκ0 h2K.le
  have hωκ : ω * (2 * (k : ℝ) - 1) = κ := by
    rw [hω]
    exact div_mul_cancel₀ κ h2K.ne'
  -- 1. the tilted column inequality
  have h1 := col_eq_tilt hk2 (show k + 1 ≤ n by omega) hx.le
  -- 2. the order of the kernel weights, term by term, and the weighted debt
  have hterm : ∀ j ∈ Icc k (n - 1), ω * (PsiW k j * (dq k j * xcrit k ^ j))
      ≤ kqT k (xcrit k) (n - j) * (dq k j * xcrit k ^ j) := by
    intro j hj
    rw [Finset.mem_Icc] at hj
    have hxj : 0 < xcrit k ^ j := pow_pos hx j
    have e : ω * (2 * (k : ℝ) - 1) * PsiW k j = ω * PsiW k j * (2 * (k : ℝ) - 1) := by ring
    rcases Nat.lt_or_ge j q with hjq | hjq
    · have ho := order_neg hk2 hq2 hn hjq
      rw [← hκ, ← hωκ, e] at ho
      have h := mul_le_mul_of_nonpos_right (le_of_mul_le_mul_right ho h2K)
        (mul_nonpos_of_nonpos_of_nonneg (hneg j hj.1 hjq) hxj.le)
      linarith
    · have ho := order_pos hk2 hq1 hq2 hn hjq hj.2
      rw [← hκ, ← hωκ, e] at ho
      have h := mul_le_mul_of_nonneg_right (le_of_mul_le_mul_right ho h2K)
        (mul_nonneg (hpos j hjq hj.2).le hxj.le)
      linarith
  have hdebt := weighted_debt (show 7 ≤ k by omega) (n - 1) (by omega)
  have hΨ1 : PsiW k (n - 1) = (n : ℝ) - 1 := by
    rw [PsiW_of_ge (by omega : 2 * k - 1 ≤ n - 1), Nat.cast_sub (by omega : 1 ≤ n), Nat.cast_one]
  rw [hΨ1] at hdebt
  have e2 : ((n - 1 - 1 : ℕ) : ℝ) = (n : ℝ) - 2 := by
    rw [Nat.cast_sub (by omega : 1 ≤ n - 1), Nat.cast_sub (by omega : 1 ≤ n), Nat.cast_one]
    ring
  have hΨlo : (n : ℝ) - 2 ≤ PsiW k (n - 1 - 1) := by
    rw [← e2]
    exact PsiW_ge_self k (n - 1 - 1)
  have hΨhi : PsiW k (n - 1 - 1) ≤ (n : ℝ) - 1 := by
    rw [← hΨ1]
    exact PsiW_mono (Nat.sub_le (n - 1) 1)
  have h2 : -(ω * (((n : ℝ) - 1) * Ut k (xcrit k) (n - 1)
        + PsiW k (n - 1 - 1) * Ut k (xcrit k) (n - 1 - 1)
        + (((n : ℝ) - 1) - PsiW k (n - 1 - 1)) * zrT k (xcrit k) (n - 1)))
      ≤ ∑ j ∈ Icc k (n - 1), kqT k (xcrit k) (n - j) * (dq k j * xcrit k ^ j) := by
    have a1 : ω * ∑ j ∈ Icc k (n - 1), PsiW k j * (dq k j * xcrit k ^ j)
        ≤ ∑ j ∈ Icc k (n - 1), kqT k (xcrit k) (n - j) * (dq k j * xcrit k ^ j) := by
      rw [Finset.mul_sum]
      exact Finset.sum_le_sum hterm
    have a2 := mul_le_mul_of_nonneg_left hdebt hω0
    linarith
  -- 3. the diagonal lower bound and `lemma_S`
  have h3 : (k : ℝ) * Ut k (xcrit k) (n - 1 - 1)
      ≤ ((k : ℝ) + 1) * (Ut k (xcrit k) (n - 1) + dq k (n - 1) * xcrit k ^ (n - 1)) := by
    rw [← Ut_succ_eq hk2]
    exact Ut_diag_lower hk2 (show 1 ≤ n - 1 by omega)
  have e1 : n - 1 - 1 + 1 = n - 1 := by omega
  have h4 : xcrit k * (∑ j ∈ range (8 + 1), ccT (xcrit k) j) * zrT k (xcrit k) (n - 1)
      ≤ ((n : ℝ) - 1) * Ut k (xcrit k) (n - 1) := by
    have hLS := lemma_S hk2 hx.le hanti (J := 8) (M := n - 1 - 1) (by omega) (by omega)
    rw [e1, e2, show (n : ℝ) - 2 + 1 = (n : ℝ) - 1 by ring] at hLS
    have hb : zrT k (xcrit k) (n - 1) ≤ zrT k (xcrit k) (n - 1 - 1) := by
      have h := hanti (n - 1 - 1)
      rwa [e1] at h
    have hW0 : 0 ≤ xcrit k * (∑ j ∈ range (8 + 1), ccT (xcrit k) j) :=
      mul_nonneg hx.le
        (Finset.sum_nonneg fun j _ => mul_nonneg (cc_pos j).le (pow_nonneg hx.le j))
    exact le_trans (mul_le_mul_of_nonneg_left hb hW0) hLS
  -- 4. the numerics
  have hxr := xcrit_ge (show 1 ≤ k by omega)
  have hT := T_bound hk hq1 hq2 hn
  rw [← hκ] at hT
  have hT0 : 0 ≤ (n : ℝ) * ((n : ℝ) - 1) * κ :=
    mul_nonneg (mul_nonneg (by linarith) (by linarith)) hκ0
  obtain ⟨hA', hB'⟩ := big_numeric hxr hK (W8_ge hxr) hT0 hT
  rw [← hωκ] at hA' hB'
  have hA : (n : ℝ) * ((n : ℝ) - 1) * ω
      * (2 + 1 / (k : ℝ) + 1 / (xcrit k * ∑ j ∈ range (8 + 1), ccT (xcrit k) j))
      ≤ 2 * xcrit k :=
    le_of_mul_le_mul_right (by linarith) h2K
  have hB : (n : ℝ) * ((n : ℝ) - 1) * ω < xcrit k * (k : ℝ) :=
    lt_of_mul_lt_mul_right (by linarith) h2K.le
  have hη1 : 0 < dq k (n - 1) * xcrit k ^ (n - 1) :=
    mul_pos (hpos (n - 1) (by omega) (le_refl _)) (pow_pos hx _)
  have hU : ∀ j, 0 ≤ Ut k (xcrit k) j := fun j => by
    rw [Ut_eq_bq hk2]
    exact mul_nonneg (bq_nonneg _ _) (pow_nonneg hx.le _)
  have hcore : 0 < dq k n * xcrit k ^ n :=
    big_core hx hK hN hω0 (hU _) (hU _) (zrT_nonneg k hx.le (n - 1)) hη1
      (lt_of_lt_of_le (by norm_num) (W8_ge hxr)) hΨlo hΨhi h1 h2 h3 h4 hA hB
  exact pos_of_mul_pos_left hcore (pow_nonneg hx.le n)

/-- **The columns `k ≥ 82`**: `b_{n,k} > b_{n,k-1}` for every `n ≥ 2k`. -/
theorem big_columns (k n : ℕ) (hk : 82 ≤ k) (hn : 2 * k ≤ n) : b n (k - 1) < b n k := by
  -- the crossing row
  obtain ⟨q, hq1, hq2, hneg, hfirst⟩ := single_crossing hk
  have hall : ∀ m, q ≤ m → 0 < dq k m := by
    intro m
    induction m using Nat.strong_induction_on with
    | _ m ih =>
      intro hqm
      rcases Nat.lt_or_ge m (2 * k) with h | h
      · exact hfirst m hqm (by omega)
      · exact big_step hk hq1 hq2 h hneg (fun j hj1 hj2 => ih j (by omega) hj1)
  exact (dq_pos_iff k n).mp (hall n (by omega))

end Parking