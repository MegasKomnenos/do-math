module

public import Parking.Basic.Sums
public import Parking.Counting.SingleChain

/-!
# The column equations in the single-chain range

Normalised by `n!`: `zr y n = A n (y-1)/n!`, `bq k n = b n k/n!`, and the step of the column `k`,

  `dq k n = bq k n - bq (k-1) n = (b n k - b n (k-1))/n!`.

The sign of `dq k n` is the sign of the step `b n k - b n (k-1)` (`dq_nonneg_iff`, `dq_pos_iff`,
`dq_nonpos_iff`, `dq_neg_iff`).

* `bq_L0`  : the column equation of `bq l` on the rows `l+1 ≤ n ≤ 2l+1`.
* `dq_col` : the column equation of the step, on the rows `k+1 ≤ n ≤ 2k-1`, and its initial value
  `dq_base`.  Both are the single-chain formula `IsWSol.ez`, `IsWSol.fwd` read for two and three
  consecutive thresholds.
* `zr_diag_mono` : `Pr(M_n < y) ≤ Pr(M_{n+1} < y+1)` for every `n`, where `M_n` is the maximum
  displacement of a uniform parking function of length `n` (stochastic monotonicity along the
  diagonal).  It is proved by induction on `n`: the last-car recursion writes `Pr(M_{n+1} < y)`
  as an average, over the spot `j` of the last car, of products of two such probabilities for
  shorter streets, and the averaging weights for `n + 2` and `n + 1` cars are compared by an Abel
  summation (`col_coupling`).
* `gam k = (1+1/k)^(k-2)`: the factor of the diagonal lower bound, with
  `(1+1/k)^(k-1) = gam k (1+1/k)` (`psi_eq_gam`) and `gam` nondecreasing (`gam_mono`).
* `xi k t`: the tree curvature coefficients of the column `k`,
  `xi k t = δ_t / t!` with
  `δ_t = min(t,k+1) A_{t-1,k} - 2 min(t,k) A_{t-1,k-1} + min(t,k-1) A_{t-1,k-2}`.  They vanish for
  `t < k` (`xi_eq_zero`), and `n xi k n = (k+1) dq k (n-1) + 2 bq (k-1) (n-1)` for `n ≥ k+1`
  (`succ_mul_xi_succ`).

Helper declarations are prefixed `col_`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### The column equations -/

/-- The single-chain formula for `zr y` in the range `y ≤ n ≤ 2y+1`
(for `n = y` both sides vanish, so the two regimes of `IsWSol.ez` are covered uniformly). -/
private theorem col_zr_ez {y n : ℕ} (hy : 1 ≤ y) (hyn : y ≤ n) (hn : n ≤ 2 * y + 1) :
    zr y n - ∑ m ∈ Icc 1 n, eps m * zr y (n - m)
      = (y : ℝ) / n * zr y (n - 1) - cc (n - 1) := by
  have h : zr y n - ∑ m ∈ Icc 1 n, eps m * zr y (n - m)
      = if n ≤ y then 0 else ((min n y : ℕ) : ℝ) / n * zr y (n - 1) - cc (n - 1) :=
    (zr_isWSol hy).ez y (fun t _ ht => by simp [min_eq_left ht]) (by omega) hn
  rw [h]
  by_cases hny : n ≤ y
  · obtain rfl : n = y := le_antisymm hny hyn
    have hne : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    rw [ite_eq_left hny, zr_eq_cc hy (Nat.sub_le n 1), div_self hne, one_mul, sub_self]
  · rw [ite_eq_right hny, min_eq_right hyn]

/-- **The column equation of the level `l`.**  For `l ≥ 1`, `l+1 ≤ n ≤ 2l+1`:
`b_{n,l}/n! = z^{(l+1)}_{n-1}/n + (l/n) b_{n-1,l}/(n-1)! + ∑_{m=1}^{n-l-1} ε_m b_{n-m,l}/(n-m)!`. -/
theorem bq_L0 {l n : ℕ} (hl : 1 ≤ l) (hn1 : l + 1 ≤ n) (hn2 : n ≤ 2 * l + 1) :
    bq l n = zr (l + 1) (n - 1) / n + (l : ℝ) / n * bq l (n - 1)
      + ∑ m ∈ Icc 1 (n - l - 1), eps m * bq l (n - m) := by
  have e1 := col_zr_ez (y := l + 1) (n := n) (by omega) hn1 (by omega)
  have e2 := col_zr_ez (y := l) (n := n) hl (by omega) hn2
  have hsum : ∑ m ∈ Icc 1 (n - l - 1), eps m * bq l (n - m)
      = ∑ m ∈ Icc 1 n, eps m * bq l (n - m) :=
    (sum_Icc_trunc (f := fun m => eps m * bq l (n - m)) (a := n - l - 1) (n := n)
      (by omega) (fun m hm1 hm2 => by
        show eps m * bq l (n - m) = 0
        rw [bq_eq_zero (k := l) (n := n - m) hl (by omega), mul_zero])).symm
  have hsum2 : ∑ m ∈ Icc 1 n, eps m * bq l (n - m)
      = ∑ m ∈ Icc 1 n, eps m * zr (l + 1) (n - m) - ∑ m ∈ Icc 1 n, eps m * zr l (n - m) := by
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro m _
    rw [bq_eq hl]
    ring
  rw [hsum, hsum2, bq_eq hl n, bq_eq hl (n - 1)]
  push_cast at e1
  linear_combination e1 - e2

/-- `dq k n = (b n k - b n (k-1))/n!` (used for `k ≥ 1`). -/
noncomputable def dq (k n : ℕ) : ℝ := bq k n - bq (k - 1) n

/-- The sign of the step in terms of the counts: `0 ≤ d_{n,k}` iff `b(n,k-1) ≤ b(n,k)`. -/
theorem dq_nonneg_iff (k n : ℕ) : 0 ≤ dq k n ↔ b n (k - 1) ≤ b n k := by
  have hf : (0 : ℝ) < (n.factorial : ℝ) := Nat.cast_pos.mpr (Nat.factorial_pos n)
  rw [dq, bq, bq, ← sub_div, le_div_iff₀ hf, zero_mul, sub_nonneg, Nat.cast_le]

/-- `0 < d_{n,k}` iff `b(n,k-1) < b(n,k)`. -/
theorem dq_pos_iff (k n : ℕ) : 0 < dq k n ↔ b n (k - 1) < b n k := by
  have hf : (0 : ℝ) < (n.factorial : ℝ) := Nat.cast_pos.mpr (Nat.factorial_pos n)
  unfold dq bq
  rw [← sub_div, div_pos_iff_of_pos_right hf, sub_pos, Nat.cast_lt]

/-- `d_{n,k} ≤ 0` iff `b(n,k) ≤ b(n,k-1)`. -/
theorem dq_nonpos_iff (k n : ℕ) : dq k n ≤ 0 ↔ b n k ≤ b n (k - 1) := by
  rw [← not_lt, dq_pos_iff, not_lt]

/-- `d_{n,k} < 0` iff `b(n,k) < b(n,k-1)`. -/
theorem dq_neg_iff (k n : ℕ) : dq k n < 0 ↔ b n k < b n (k - 1) := by
  rw [← not_le, dq_nonneg_iff, not_le]

/-- For $k\ge2$ the normalised step of the column $k$ vanishes in the rows $n<k$:
$\delta^{(k)}_n=0$. -/
theorem dq_eq_zero {k n : ℕ} (hk : 2 ≤ k) (hn : n < k) : dq k n = 0 := by
  unfold dq
  rw [bq_eq_zero (k := k) (n := n) (by omega) (by omega),
    bq_eq_zero (k := k - 1) (n := n) (by omega) (by omega), sub_zero]

/-- `d_{k,k} = -k^(k-2)`, i.e. `dq k k = -a_k/k`. -/
theorem dq_base {k : ℕ} (hk : 2 ≤ k) : dq k k = -(cay k / k) := by
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
  have hj : 1 ≤ j := by omega
  have hf : cc (j + 1) - zr j (j + 1)
      = ∑ t ∈ Icc (j + 1) (j + 1),
          cc (j + 1 - t) * (cc (t - 1) - ((min t j : ℕ) : ℝ) / t * zr j (t - 1)) :=
    (zr_isWSol hj).fwd j (fun t _ ht => by simp [min_eq_left ht]) (by omega)
  rw [Finset.Icc_self, Finset.sum_singleton, Nat.sub_self, cc_zero, Nat.add_sub_cancel,
    min_eq_right (by omega : j ≤ j + 1), zr_eq_cc hj (le_refl j)] at hf
  have hcc : cc j = cay (j + 1) := rfl
  have hd : dq (j + 1) (j + 1) = -(cc (j + 1) - zr j (j + 1)) := by
    unfold dq
    rw [Nat.add_sub_cancel, bq_eq_zero (k := j + 1) (n := j + 1) (by omega) (le_refl _),
      bq_eq hj, zr_eq_cc (y := j + 1) (n := j + 1) (by omega) (le_refl _)]
    ring
  rw [hd, hf, hcc]
  have h2 : (j : ℝ) + 1 ≠ 0 := by positivity
  push_cast
  field

/-- **Column equation** for `k ≥ 2`, `k+1 ≤ n ≤ 2k-1`:
`δ_n = ((k+1)/n) δ_{n-1} + (2/n) β^{(k-1)}_{n-1} + ∑_{m=1}^{n-k} ε_m δ_{n-m}`. -/
theorem dq_col {k n : ℕ} (hk : 2 ≤ k) (hn1 : k + 1 ≤ n) (hn2 : n ≤ 2 * k - 1) :
    dq k n = ((k : ℝ) + 1) / n * dq k (n - 1) + 2 / (n : ℝ) * bq (k - 1) (n - 1)
      + ∑ m ∈ Icc 1 (n - k), eps m * dq k (n - m) := by
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
  have hj : 1 ≤ j := by omega
  have hdq : ∀ i, dq (j + 1) i = zr (j + 1 + 1) i - 2 * zr (j + 1) i + zr j i := by
    intro i
    unfold dq
    rw [Nat.add_sub_cancel, bq_eq (by omega : 1 ≤ j + 1), bq_eq hj]
    ring
  have e2 := col_zr_ez (y := j + 1 + 1) (n := n) (by omega) (by omega) (by omega)
  have e1 := col_zr_ez (y := j + 1) (n := n) (by omega) (by omega) (by omega)
  have e0 := col_zr_ez (y := j) (n := n) hj (by omega) (by omega)
  have hsum : ∑ m ∈ Icc 1 (n - (j + 1)), eps m * dq (j + 1) (n - m)
      = ∑ m ∈ Icc 1 n, eps m * dq (j + 1) (n - m) :=
    (sum_Icc_trunc (f := fun m => eps m * dq (j + 1) (n - m)) (a := n - (j + 1)) (n := n)
      (by omega) (fun m hm1 hm2 => by
        show eps m * dq (j + 1) (n - m) = 0
        rw [dq_eq_zero (k := j + 1) (n := n - m) (by omega) (by omega), mul_zero])).symm
  have hsum2 : ∑ m ∈ Icc 1 n, eps m * dq (j + 1) (n - m)
      = ∑ m ∈ Icc 1 n, eps m * zr (j + 1 + 1) (n - m)
        - 2 * ∑ m ∈ Icc 1 n, eps m * zr (j + 1) (n - m)
        + ∑ m ∈ Icc 1 n, eps m * zr j (n - m) := by
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro m _
    rw [hdq]
    ring
  rw [hsum, hsum2, hdq n, hdq (n - 1), Nat.add_sub_cancel, bq_eq hj]
  push_cast at e2 e1 ⊢
  linear_combination e2 - 2 * e1 + e0

/-! ### Stochastic monotonicity -/

/-- **Coupling lemma** (Abel summation). Let `q` be a weight sequence on `{0,…,n}` and `q'` one on
`{0,…,n-1}` with the same total mass, such that `q j ≤ q' j` and `q (j+1) ≤ q' j` for `j < n`.
If `G' j ≤ G j` and `G' j ≤ G (j+1)` for `j < n`, then `∑ q' G' ≤ ∑ q G`.

The two comparisons of the weights say that the partial sums interlace,
`∑_{j<t} q j ≤ ∑_{j<t} q' j ≤ ∑_{j≤t} q j`, so that the mass `q' j` can be split into a part moved
to the index `j` and a part moved to the index `j + 1`. -/
private theorem col_coupling (q q' G G' : ℕ → ℝ) (n : ℕ)
    (hsum : ∑ j ∈ range (n + 1), q j = ∑ j ∈ range n, q' j)
    (h1 : ∀ j, j < n → q j ≤ q' j)
    (h2 : ∀ j, j < n → q (j + 1) ≤ q' j)
    (hG1 : ∀ j, j < n → G' j ≤ G j)
    (hG2 : ∀ j, j < n → G' j ≤ G (j + 1)) :
    ∑ j ∈ range n, q' j * G' j ≤ ∑ j ∈ range (n + 1), q j * G j := by
  -- partial sums of `q` are dominated by those of `q'`
  have hQ1 : ∀ t, t ≤ n → ∑ j ∈ range t, q j ≤ ∑ j ∈ range t, q' j := fun t ht =>
    Finset.sum_le_sum fun j hj => h1 j (lt_of_lt_of_le (Finset.mem_range.mp hj) ht)
  -- and dominate them with one more term: compare the complementary tails
  have hQ2 : ∀ t, t ≤ n → ∑ j ∈ range t, q' j ≤ ∑ j ∈ range (t + 1), q j := by
    intro t ht
    have e1 := Finset.sum_range_add_sum_Ico q' ht
    have e2 := Finset.sum_range_add_sum_Ico q (show t + 1 ≤ n + 1 by omega)
    have e3 := Finset.sum_Ico_add' q t n 1
    have e4 : ∑ j ∈ Ico t n, q (j + 1) ≤ ∑ j ∈ Ico t n, q' j :=
      Finset.sum_le_sum fun j hj => h2 j (Finset.mem_Ico.mp hj).2
    linarith
  -- Abel summation, by induction on the number of terms
  have key : ∀ t, t ≤ n →
      ∑ j ∈ range t, q' j * G' j ≤ ∑ j ∈ range t, q j * G j
        + ((∑ j ∈ range t, q' j) - ∑ j ∈ range t, q j) * G t := by
    intro t
    induction t with
    | zero =>
      intro _
      simp
    | succ t ih =>
      intro ht
      have IH := ih (by omega)
      have hp0 : 0 ≤ (∑ j ∈ range (t + 1), q j) - ∑ j ∈ range t, q' j :=
        sub_nonneg.mpr (hQ2 t (by omega))
      have hp1 : 0 ≤ (∑ j ∈ range (t + 1), q' j) - ∑ j ∈ range (t + 1), q j :=
        sub_nonneg.mpr (hQ1 (t + 1) ht)
      have e1 := mul_le_mul_of_nonneg_left (hG1 t (by omega)) hp0
      have e2 := mul_le_mul_of_nonneg_left (hG2 t (by omega)) hp1
      simp only [Finset.sum_range_succ] at e1 e2 ⊢
      linarith
  have hfin := key n le_rfl
  rw [Finset.sum_range_succ] at hsum ⊢
  rw [show (∑ j ∈ range n, q' j) - ∑ j ∈ range n, q j = q n by linarith] at hfin
  exact hfin

/-- Monotonicity of a product of three nonnegative factors. -/
private theorem col_mul3_le {a b c a' b' c' : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c)
    (h1 : a ≤ a') (h2 : b ≤ b') (h3 : c ≤ c') : a * b * c ≤ a' * b' * c' := by
  have ha' : 0 ≤ a' := le_trans ha h1
  have hb' : 0 ≤ b' := le_trans hb h2
  exact mul_le_mul (mul_le_mul h1 h2 hb ha') h3 hc (mul_nonneg ha' hb')

/-- `M/(j+1) ≤ (M+1)/(j+2)` for `M ≤ j+1`. -/
private theorem col_hfrac (M j : ℕ) (hM : M ≤ j + 1) :
    (M : ℝ) / ((j : ℝ) + 1) ≤ ((M + 1 : ℕ) : ℝ) / (((j + 1 : ℕ) : ℝ) + 1) := by
  have h : (M : ℝ) ≤ (j : ℝ) + 1 := by exact_mod_cast hM
  have h1 : (0 : ℝ) < (j : ℝ) + 1 := by positivity
  have h2 : (0 : ℝ) < ((j + 1 : ℕ) : ℝ) + 1 := by positivity
  rw [div_le_div_iff₀ h1 h2]
  push_cast
  nlinarith [h]

/-- `(i+1) (1+1/i)^(i-1) = i (1+1/i)^i`. -/
private theorem col_chi_eq {i : ℕ} (hi : 0 < i) :
    ((i : ℝ) + 1) * (1 + 1 / (i : ℝ)) ^ (i - 1) = (i : ℝ) * (1 + 1 / (i : ℝ)) ^ i := by
  have hi' : (i : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hx : (i : ℝ) * (1 + 1 / (i : ℝ)) = (i : ℝ) + 1 := by field
  have hpow : (1 + 1 / (i : ℝ)) ^ i = (1 + 1 / (i : ℝ)) ^ (i - 1) * (1 + 1 / (i : ℝ)) := by
    rw [← pow_succ]
    congr 1
    omega
  rw [hpow]
  linear_combination (-(1 + 1 / (i : ℝ)) ^ (i - 1)) * hx

/-- Real-arithmetic core of the weight comparison (iv). -/
private theorem col_chi_core {I Mm a b ψi χi ψm χm ψm1 : ℝ} (hI : 0 ≤ I) (hM : 0 ≤ Mm) (ha : 0 ≤ a)
    (hb : 0 ≤ b) (c1 : (I + 1) * ψi = I * χi) (c2 : (Mm + 1) * ψm = Mm * χm)
    (m1 : χi ≤ χm) (m2 : ψm ≤ ψm1) :
    (I + 1) * (ψi * a) * (Mm * b) ≤ I * a * ((Mm + 1) * (ψm1 * b)) := by
  have hK : 0 ≤ I * a * (Mm * b) := mul_nonneg (mul_nonneg hI ha) (mul_nonneg hM hb)
  have hM1 : 0 ≤ Mm + 1 := by linarith
  have hK2 : 0 ≤ I * a * ((Mm + 1) * b) := mul_nonneg (mul_nonneg hI ha) (mul_nonneg hM1 hb)
  calc (I + 1) * (ψi * a) * (Mm * b) = χi * (I * a * (Mm * b)) := by
        linear_combination (a * (Mm * b)) * c1
    _ ≤ χm * (I * a * (Mm * b)) := mul_le_mul_of_nonneg_right m1 hK
    _ = ψm * (I * a * ((Mm + 1) * b)) := by
        linear_combination (-(I * a * b)) * c2
    _ ≤ ψm1 * (I * a * ((Mm + 1) * b)) := mul_le_mul_of_nonneg_right m2 hK2
    _ = I * a * ((Mm + 1) * (ψm1 * b)) := by ring

/-- Weight comparison (iv) in cross-multiplied form:
`(j+2) c_{j+1} (n+1) c_{n+1} ≤ (j+1) c_j (n+2) c_{n+2}` for `j ≤ n`. -/
private theorem col_cc_chi_ineq {j n : ℕ} (hj : j ≤ n) :
    ((j : ℝ) + 1 + 1) * cc (j + 1) * (((n : ℝ) + 1) * cc (n + 1))
      ≤ ((j : ℝ) + 1) * cc j * (((n : ℝ) + 1 + 1) * cc (n + 1 + 1)) := by
  have e1 : cc (j + 1) = (1 + 1 / ((j + 1 : ℕ) : ℝ)) ^ (j + 1 - 1) * cc j :=
    cay_ratio (j := j + 1) (by omega)
  have e2 : cc (n + 1 + 1) = (1 + 1 / ((n + 1 + 1 : ℕ) : ℝ)) ^ (n + 1 + 1 - 1) * cc (n + 1) :=
    cay_ratio (j := n + 1 + 1) (by omega)
  have c1 := col_chi_eq (i := j + 1) (by omega)
  have c2 := col_chi_eq (i := n + 1) (by omega)
  have m1 := chi_mono (i := j + 1) (j := n + 1) (by omega) (by omega)
  have m2 := psi_mono (i := n + 1) (j := n + 1 + 1) (by omega) (by omega)
  have h := col_chi_core (I := ((j + 1 : ℕ) : ℝ)) (Mm := ((n + 1 : ℕ) : ℝ)) (a := cc j)
    (b := cc (n + 1)) (Nat.cast_nonneg _) (Nat.cast_nonneg _) (cc_pos j).le (cc_pos (n + 1)).le
    c1 c2 m1 m2
  rw [e1, e2]
  push_cast at h ⊢
  exact h

/-- The weights `q_{n+1}(j) = (j+1) c_j c_{n-j} / ((n+1) c_{n+1})`, `0 ≤ j ≤ n`
(a probability distribution on `{0,…,n}` by `cc_rec`). -/
private noncomputable def col_qw (n j : ℕ) : ℝ :=
  ((j : ℝ) + 1) * cc j * cc (n - j) / (((n : ℝ) + 1) * cc (n + 1))

/-- The values `G(j) = (min(j+1,y)/(j+1)) F^y_j F^y_{n-j}` with `F^y_m = zr y m / cc m`. -/
private noncomputable def col_Gv (y n j : ℕ) : ℝ :=
  ((min (j + 1) y : ℕ) : ℝ) / ((j : ℝ) + 1) * (zr y j / cc j) * (zr y (n - j) / cc (n - j))

private theorem col_qw_sum (n : ℕ) : ∑ j ∈ range (n + 1), col_qw n j = 1 := by
  unfold col_qw
  rw [← Finset.sum_div, ← cc_rec n]
  have hpos : (0 : ℝ) < ((n : ℝ) + 1) * cc (n + 1) := mul_pos (by positivity) (cc_pos _)
  exact div_self hpos.ne'

/-- Weight comparison (iii): `q_{n+2}(j) ≤ q_{n+1}(j)` for `j ≤ n`, by the log-convexity
`c_{n-j+1} c_{n+1} ≤ c_{n-j} c_{n+2}`. -/
private theorem col_qw_le1 {n j : ℕ} (hj : j ≤ n) : col_qw (n + 1) j ≤ col_qw n j := by
  have hcj := cc_pos j
  have hc1 := cc_pos (n - j)
  have hc1' := cc_pos (n - j + 1)
  have hc2 := cc_pos (n + 1)
  have hc3 := cc_pos (n + 1 + 1)
  have hlc : cc (n - j + 1) * cc (n + 1) ≤ cc (n - j) * cc (n + 1 + 1) :=
    cay_logconvex (u := n - j + 1) (v := n + 1 + 1) (c := 1) (by omega) (by omega)
  unfold col_qw
  rw [show n + 1 - j = n - j + 1 by omega, div_le_div_iff₀ (by positivity) (by positivity)]
  push_cast
  calc ((j : ℝ) + 1) * cc j * cc (n - j + 1) * (((n : ℝ) + 1) * cc (n + 1))
      = ((j : ℝ) + 1) * cc j * ((n : ℝ) + 1) * (cc (n - j + 1) * cc (n + 1)) := by ring
    _ ≤ ((j : ℝ) + 1) * cc j * ((n : ℝ) + 1 + 1) * (cc (n - j) * cc (n + 1 + 1)) :=
        mul_le_mul (mul_le_mul_of_nonneg_left (by linarith) (by positivity)) hlc
          (by positivity) (by positivity)
    _ = ((j : ℝ) + 1) * cc j * cc (n - j) * (((n : ℝ) + 1 + 1) * cc (n + 1 + 1)) := by ring

/-- Weight comparison (iv): `q_{n+2}(j+1) ≤ q_{n+1}(j)` for `j ≤ n`. -/
private theorem col_qw_le2 {n j : ℕ} (hj : j ≤ n) : col_qw (n + 1) (j + 1) ≤ col_qw n j := by
  unfold col_qw
  rw [Nat.add_sub_add_right]
  have hD1 : 0 < (((n + 1 : ℕ) : ℝ) + 1) * cc (n + 1 + 1) :=
    mul_pos (by positivity) (cc_pos _)
  have hD2 : 0 < ((n : ℝ) + 1) * cc (n + 1) := mul_pos (by positivity) (cc_pos _)
  have hc : 0 ≤ cc (n - j) := (cc_pos _).le
  have key := mul_le_mul_of_nonneg_left (col_cc_chi_ineq hj) hc
  rw [div_le_div_iff₀ hD1 hD2]
  push_cast
  linarith [key]

/-- The normalised last-car recursion: `F^y_{n+1} = ∑_{j ≤ n} q_{n+1}(j) G(j)`. -/
private theorem col_zr_ratio_eq {y : ℕ} (hy : 1 ≤ y) (n : ℕ) :
    zr y (n + 1) / cc (n + 1) = ∑ j ∈ range (n + 1), col_qw n j * col_Gv y n j := by
  have hs : ((n : ℝ) + 1) * zr y (n + 1)
      = ∑ j ∈ range (n + 1), ((min (j + 1) y : ℕ) : ℝ) * zr y j * zr y (n - j) :=
    (zr_isWSol hy).succ n
  have hn1 : (0 : ℝ) < (n : ℝ) + 1 := by positivity
  have hterm : ∀ j ∈ range (n + 1), col_qw n j * col_Gv y n j
      = ((min (j + 1) y : ℕ) : ℝ) * zr y j * zr y (n - j) / (((n : ℝ) + 1) * cc (n + 1)) := by
    intro j _
    have h1 : cc j ≠ 0 := (cc_pos j).ne'
    have h2 : cc (n - j) ≠ 0 := (cc_pos (n - j)).ne'
    have h3 : (j : ℝ) + 1 ≠ 0 := by positivity
    have h4 : cc (n + 1) ≠ 0 := (cc_pos (n + 1)).ne'
    have h5 : (n : ℝ) + 1 ≠ 0 := hn1.ne'
    unfold col_qw col_Gv
    field
  rw [Finset.sum_congr rfl hterm, ← Finset.sum_div, ← hs]
  exact (mul_div_mul_left _ _ hn1.ne').symm

/-- **Stochastic monotonicity** `Pr(M_n < y) ≤ Pr(M_{n+1} < y+1)`. -/
theorem zr_diag_mono {y : ℕ} (hy : 1 ≤ y) (n : ℕ) :
    zr y n / cc n ≤ zr (y + 1) (n + 1) / cc (n + 1) := by
  induction n using Nat.strong_induction_on generalizing y with
  | _ n ih =>
    rcases Nat.eq_zero_or_pos n with rfl | hn
    · exact le_of_eq (by
        rw [zr_eq_cc hy (Nat.zero_le y), zr_eq_cc (Nat.succ_pos y) (by omega),
          div_self (cc_pos 0).ne', div_self (cc_pos (0 + 1)).ne'])
    · obtain ⟨N, rfl⟩ : ∃ N, n = N + 1 := ⟨n - 1, by omega⟩
      have hy1 : 1 ≤ y + 1 := by omega
      rw [col_zr_ratio_eq hy N, col_zr_ratio_eq hy1 (N + 1)]
      refine col_coupling (col_qw (N + 1)) (col_qw N) (col_Gv (y + 1) (N + 1)) (col_Gv y N)
        (N + 1) ?_ ?_ ?_ ?_ ?_
      · rw [col_qw_sum (N + 1), col_qw_sum N]
      · intro j hj
        exact col_qw_le1 (by omega)
      · intro j hj
        exact col_qw_le2 (by omega)
      · -- (i) `G'(j) ≤ G(j)`
        intro j hj
        unfold col_Gv
        apply col_mul3_le
        · positivity
        · exact div_nonneg (zr_nonneg _ _) (cc_pos _).le
        · exact div_nonneg (zr_nonneg _ _) (cc_pos _).le
        · have hmin : min (j + 1) y ≤ min (j + 1) (y + 1) := by omega
          exact div_le_div_of_nonneg_right (Nat.cast_le.mpr hmin) (by positivity)
        · exact div_le_div_of_nonneg_right (zr_mono (Nat.le_succ y) j) (cc_pos j).le
        · have h := ih (N - j) (by omega) hy
          rwa [show N - j + 1 = N + 1 - j by omega] at h
      · -- (ii) `G'(j) ≤ G(j+1)`
        intro j hj
        unfold col_Gv
        rw [Nat.add_sub_add_right]
        apply col_mul3_le
        · positivity
        · exact div_nonneg (zr_nonneg _ _) (cc_pos _).le
        · exact div_nonneg (zr_nonneg _ _) (cc_pos _).le
        · rw [show min (j + 1 + 1) (y + 1) = min (j + 1) y + 1 by omega]
          exact col_hfrac _ j (min_le_left _ _)
        · exact ih j (by omega) hy
        · exact div_le_div_of_nonneg_right (zr_mono (Nat.le_succ y) (N - j)) (cc_pos _).le

/-! ### The factor `γ_k` of the diagonal lower bound -/

/-- `γ_k = (1+1/k)^(k-2)`. -/
noncomputable def gam (k : ℕ) : ℝ := (1 + 1 / (k : ℝ)) ^ (k - 2)

/-- $\gamma_k=(1+1/k)^{k-2}$ is positive. -/
theorem gam_pos (k : ℕ) : 0 < gam k := by
  unfold gam
  positivity

/-- `(1+1/m)^(m-1) = γ_m (1+1/m)` for `m ≥ 2`. -/
theorem psi_eq_gam {m : ℕ} (hm : 2 ≤ m) :
    (1 + 1 / (m : ℝ)) ^ (m - 1) = gam m * (1 + 1 / (m : ℝ)) := by
  rw [gam, ← pow_succ, show m - 2 + 1 = m - 1 by omega]

/-- The factor $\gamma_k=(1+1/k)^{k-2}$ is nondecreasing for $k\ge2$. -/
theorem gam_mono {i j : ℕ} (hi : 2 ≤ i) (hij : i ≤ j) : gam i ≤ gam j := by
  have hir : (0 : ℝ) < i := Nat.cast_pos.mpr (by omega)
  have h1 : 1 + 1 / (j : ℝ) ≤ 1 + 1 / (i : ℝ) := by
    have h := one_div_le_one_div_of_le hir (Nat.cast_le.mpr hij)
    linarith
  have hgj : 0 ≤ gam j := by
    unfold gam
    positivity
  have hpsi := psi_mono (show 0 < i by omega) hij
  rw [psi_eq_gam hi, psi_eq_gam (hi.trans hij)] at hpsi
  exact le_of_mul_le_mul_right (hpsi.trans (mul_le_mul_of_nonneg_left h1 hgj)) (by positivity)

/-! ### The tree curvature -/

/-- Tree curvature coefficient `ξ_t = δ_t/t!` of column `k` (thresholds `k+1, k, k-1`). -/
noncomputable def xi (k t : ℕ) : ℝ :=
  if t = 0 then 0 else
    (((min t (k + 1) : ℕ) : ℝ) * zr (k + 1) (t - 1) - 2 * ((min t k : ℕ) : ℝ) * zr k (t - 1)
      + ((min t (k - 1) : ℕ) : ℝ) * zr (k - 1) (t - 1)) / (t : ℝ)

/-- The defining formula of the tree curvature at the index $t+1$: $(t+1)\,\xi_{t+1}=\min(t+1,k+1)\,
z^{(k+1)}_t-2\min(t+1,k)\,z^{(k)}_t+\min(t+1,k-1)\,z^{(k-1)}_t$. -/
theorem xi_succ (k t : ℕ) : xi k (t + 1) =
    (((min (t + 1) (k + 1) : ℕ) : ℝ) * zr (k + 1) t - 2 * ((min (t + 1) k : ℕ) : ℝ) * zr k t
      + ((min (t + 1) (k - 1) : ℕ) : ℝ) * zr (k - 1) t) / ((t : ℝ) + 1) := by
  rw [xi, ite_eq_right (Nat.succ_ne_zero t), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]

/-- Below the column index the three thresholds give the same trees: `ξ_t = 0` for `t < k`. -/
theorem xi_eq_zero {k t : ℕ} (hk : 2 ≤ k) (ht : t < k) : xi k t = 0 := by
  cases t with
  | zero => exact ite_eq_left rfl
  | succ t =>
    rw [xi_succ, Nat.min_eq_left (by omega : t + 1 ≤ k + 1), Nat.min_eq_left (by omega : t + 1 ≤ k),
      Nat.min_eq_left (by omega : t + 1 ≤ k - 1),
      zr_eq_cc (by omega : 1 ≤ k + 1) (by omega : t ≤ k + 1),
      zr_eq_cc (by omega : 1 ≤ k) (by omega : t ≤ k),
      zr_eq_cc (by omega : 1 ≤ k - 1) (by omega : t ≤ k - 1)]
    ring

/-- Beyond the column index the curvature is the left-hand side of the column inequality:
`(n+1) ξ_{n+1} = (k+1) δ_n + 2 β^{(k-1)}_n` for `n ≥ k`. -/
theorem succ_mul_xi_succ {k n : ℕ} (hk : 2 ≤ k) (hn : k ≤ n) :
    ((n : ℝ) + 1) * xi k (n + 1) = ((k : ℝ) + 1) * dq k n + 2 * bq (k - 1) n := by
  have hk1 : 1 ≤ k := by omega
  have hn1 : (n : ℝ) + 1 ≠ 0 := by positivity
  rw [xi_succ, Nat.min_eq_right (by omega : k + 1 ≤ n + 1), Nat.min_eq_right (by omega : k ≤ n + 1),
    Nat.min_eq_right (by omega : k - 1 ≤ n + 1), Nat.cast_add, Nat.cast_one, Nat.cast_sub hk1,
    Nat.cast_one, dq, bq_eq hk1, bq_eq (show 1 ≤ k - 1 by omega), Nat.sub_add_cancel hk1]
  field

end Parking