import Parking.Series.AllRows

/-!
# The crossing criterion

Fix a column `k ≥ 2` and `1 ≤ R ≤ k - 1`, and put `N = k + R`.  The following quantities are
explicit functions of `k` and `R`:

* `xk k`     : the diagonal tilt `x = 1/γ_k = (k/(k+1))^(k-2)`;
* `kapx k m` : the tilted kernel masses `κ_m = x^m ε_m`, and the kernel deficit
  `kbar k M = 1 - x - ∑_{m=1}^M κ_m`;
* `pix k j`  : `π_j = x^j a_j/j`, with the partial sums `pixSum k i = ∑_{n=k}^i π_n`;
* `ecor k j` : `𝖾_j = (j-k+2) - Π_{j+1}/π_{j+1}`, and `ecorSum k R = ∑_{j=k}^{N-2} 𝖾_j/(j+1)`;
* `omg k i`  : `ω_i = 1 - i/((i+1) x γ_i)`, and `Somg k R = ∑_{i=k+1}^{N-1} (i-k+1) ω_i`;
* `SR k R`   : `S_R = ∑_{i<R} (i x)^i/i!`;
* `profD k j`, `stepD k n` : the profile `x^j b_{j,k-1}/j!` and the step `x^n d_{n,k}/n!` of the
  column `k`, tilted by the diagonal tilt.

**The crossing criterion** (`cross_criterion`).  If `κ̄_R ≥ 0` and

`x [R(R+1)/N - 1 - S_R - 𝖤] > Θ₁ [𝖾_{N-1} + Σ_ω]`,  `Θ₁ = κ̄_R + x(R+1)/N`,

then the column `k` has turned positive by the row `N`: some `k < j ≤ N` has `d_{j,k} > 0`.

The proof assumes `d_{j,k} ≤ 0` for `k < j ≤ N` and derives the reverse inequality.  With
`u_j = profD k j = x^j b_{j,k-1}/j!`, `F(n) = Pr(M_n < k)`, `F'(n) = Pr(M_n < k-1)`,
`P(n) = Pr(M_n = k-1)`, `J(n+1) = F(n+1) - F'(n)` and `η_n = stepD k n = x^n d_{n,k}/n!`, the steps
are:

1. `profD_le_top`: the profile `u_j` is largest at `j = N` (by `d ≤ 0` and the diagonal lower bound
   `bq_diag_lower`);
2. `profD_rec`, `stepD_rec`: the column equation of the level `k - 1` (`bq_L0`) and the column
   equation of the step (`dq_col`), tilted by `x^n`;
3. `top_row`: `u_N Θ₁ ≤ π_N F(N-1)` (the equation of the row `N`);
4. `E1`: the identity obtained by summing the equations of the rows `k, …, N` and summing by parts,
   `F(N-1) Π_N = u_N + u_{N-1}(1 - x - (k-1)x/N) + ∑_j u_j (κ̄_{N-j} + x 𝖾_j/(j+1)) + ∑_i Π_i J(i)`;
5. `flow_bound`: `J(i) ≤ ω_i (1 - F'(i-1))` (from the diagonal lower bound summed over the levels);
6. `budget`: `∑_{j=k}^{N-1} P(j) ≤ 1/2` (from the summed column equation of the step);
7. the combination of 1–6 (`cross_criterion`).

The auxiliary statements live in the namespace `Parking.CrossCrit` and are written with
`k = l + 1` (`l ≥ 1`); rows are written `l + r + 1` (`= k + r`).
-/

namespace Parking

open Finset

/-! ### The quantities of the criterion -/

/-- The diagonal tilt `x_k = 1/γ_k`. -/
noncomputable def xk (k : ℕ) : ℝ := (gam k)⁻¹

/-- Tilted kernel masses `κ_m = x^m ε_m` at the diagonal tilt `x = xk k`. -/
noncomputable def kapx (k m : ℕ) : ℝ := xk k ^ m * eps m

/-- Kernel deficit `κ̄_M = 1 - x - ∑_{m=1}^M κ_m`. -/
noncomputable def kbar (k M : ℕ) : ℝ := 1 - xk k - ∑ m ∈ Icc 1 M, kapx k m

/-- `π_j = x^j a_j / j`. -/
noncomputable def pix (k j : ℕ) : ℝ := xk k ^ j * cay j / j

/-- `Π_i = ∑_{n=k}^i π_n`. -/
noncomputable def pixSum (k i : ℕ) : ℝ := ∑ n ∈ Icc k i, pix k n

/-- `𝖾_j = (j-k+2) - Π_{j+1}/π_{j+1}`. -/
noncomputable def ecor (k j : ℕ) : ℝ := ((j : ℝ) - k + 2) - pixSum k (j + 1) / pix k (j + 1)

/-- `𝖤 = ∑_{j=k}^{N-2} 𝖾_j/(j+1)`, `N = k + R`. -/
noncomputable def ecorSum (k R : ℕ) : ℝ := ∑ j ∈ Icc k (k + R - 2), ecor k j / ((j : ℝ) + 1)

/-- `ω_i = 1 - i/((i+1) x γ_i)`. -/
noncomputable def omg (k i : ℕ) : ℝ := 1 - (i : ℝ) / (((i : ℝ) + 1) * (xk k * gam i))

/-- `Σ_ω = ∑_{i=k+1}^{N-1} (i-k+1) ω_i`, `N = k + R`. -/
noncomputable def Somg (k R : ℕ) : ℝ :=
  ∑ i ∈ Icc (k + 1) (k + R - 1), ((i : ℝ) - k + 1) * omg k i

/-- `S_R = ∑_{i<R} (i x)^i / i!`. -/
noncomputable def SR (k R : ℕ) : ℝ := ∑ i ∈ range R, ((i : ℝ) * xk k) ^ i / (i.factorial : ℝ)

/-- The tilted profile `u_j = x^j b_{j,k-1}/j!` of the column `k` at the diagonal tilt. -/
noncomputable def profD (k j : ℕ) : ℝ := xk k ^ j * bq (k - 1) j

/-- The tilted step `η_n = x^n d_{n,k}/n!` of the column `k` at the diagonal tilt. -/
noncomputable def stepD (k n : ℕ) : ℝ := xk k ^ n * dq k n

namespace CrossCrit

/-! ### Summation lemmas -/

/-- Reflection of a convolution sum: `∑_{m=1}^n f m (n-m) = ∑_{i<n} f (n-i) i`. -/
private theorem sum_reflect (f : ℕ → ℕ → ℝ) (n : ℕ) :
    ∑ m ∈ Icc 1 n, f m (n - m) = ∑ i ∈ range n, f (n - i) i := by
  have h := sum_Icc_eq_range (fun m => f m (n - m)) 0 n
  simp only [zero_add] at h
  rw [h, ← sum_range_reflect (fun i => f (n - i) i) n]
  refine sum_congr rfl fun r hr => ?_
  rw [mem_range] at hr
  have e1 : n - (n - 1 - r) = r + 1 := by omega
  have e2 : n - 1 - r = n - (r + 1) := by omega
  rw [e1, e2]

/-- Summing a recursion `w (r+1) = a r + c r * w r + ∑_{i ≤ r} κ (r+1-i) * w i` over `r < R`:
`∑_{r<R} a r = w R - w 0 + ∑_{i<R} w i (1 - c i - ∑_{m=1}^{R-i} κ m)`. -/
private theorem sum_rec (w a c κ : ℕ → ℝ) (R : ℕ)
    (h : ∀ r, r < R → w (r + 1) = a r + c r * w r + ∑ i ∈ range (r + 1), κ (r + 1 - i) * w i) :
    ∑ r ∈ range R, a r = w R - w 0
      + ∑ i ∈ range R, w i * (1 - c i - ∑ m ∈ Icc 1 (R - i), κ m) := by
  induction R with
  | zero => simp
  | succ R ih =>
    have ih' := ih (fun r hr => h r (by omega))
    have hR := h R (by omega)
    have e1 : R + 1 - R = 1 := by omega
    rw [sum_range_succ, e1] at hR
    have hsplit : ∑ i ∈ range R, w i * (1 - c i - ∑ m ∈ Icc 1 (R + 1 - i), κ m)
        = ∑ i ∈ range R, w i * (1 - c i - ∑ m ∈ Icc 1 (R - i), κ m)
          - ∑ i ∈ range R, κ (R + 1 - i) * w i := by
      rw [← sum_sub_distrib]
      refine sum_congr rfl fun i hi => ?_
      rw [mem_range] at hi
      have e : R + 1 - i = (R - i) + 1 := by omega
      rw [e, sum_Icc_succ_top (show 1 ≤ R - i + 1 by omega)]
      ring
    rw [sum_range_succ, sum_range_succ (fun i => w i * (1 - c i - ∑ m ∈ Icc 1 (R + 1 - i), κ m)) R,
      hsplit, ih', e1, Icc_self, sum_singleton]
    linear_combination (-1 : ℝ) * hR

/-- `sum_rec` for a sequence indexed by the rows `l + r + 1`, with the convolution written as in
the column equations (`∑_{m=1}^{r+1} κ_m U_{n-m}`, `n = l + r + 2`). -/
private theorem sum_rec' (U a c κ : ℕ → ℝ) (l R : ℕ)
    (hrec : ∀ r, r < R → U (l + r + 1 + 1) = a r + c r * U (l + r + 1)
        + ∑ m ∈ Icc 1 (r + 1), κ m * U (l + r + 1 + 1 - m)) :
    ∑ r ∈ range R, a r = U (l + R + 1) - U (l + 1)
      + ∑ i ∈ range R, U (l + i + 1) * (1 - c i - ∑ m ∈ Icc 1 (R - i), κ m) := by
  refine sum_rec (fun r => U (l + r + 1)) a c κ R fun r hr => ?_
  have h := hrec r hr
  have hs : ∑ m ∈ Icc 1 (r + 1), κ m * U (l + r + 1 + 1 - m)
      = ∑ i ∈ range (r + 1), κ (r + 1 - i) * U (l + i + 1) := by
    rw [← sum_reflect (fun m j => κ m * U (l + j + 1)) (r + 1)]
    refine sum_congr rfl fun m hm => ?_
    rw [mem_Icc] at hm
    have e : l + r + 1 + 1 - m = l + (r + 1 - m) + 1 := by omega
    rw [e]
  rw [hs] at h
  exact h

/-- Summation by parts. -/
private theorem abel_sum (p G : ℕ → ℝ) (R : ℕ) :
    ∑ r ∈ range (R + 1), p r * G r
      = G R * ∑ r ∈ range (R + 1), p r
        + ∑ i ∈ range R, (∑ r ∈ range (i + 1), p r) * (G i - G (i + 1)) := by
  induction R with
  | zero => simp [mul_comm]
  | succ R ih =>
    rw [sum_range_succ, ih, sum_range_succ (fun r => p r) (R + 1),
      sum_range_succ (fun i => (∑ r ∈ range (i + 1), p r) * (G i - G (i + 1))) R]
    ring

/-- Tilting a column recursion in row `n + 1` by `x^{n+1}`. -/
private theorem tilt (x : ℝ) (β : ℕ → ℝ) (A C : ℝ) {n M : ℕ} (hM : M ≤ n + 1)
    (h : β (n + 1) = A + C / ((n + 1 : ℕ) : ℝ) * β n + ∑ m ∈ Icc 1 M, eps m * β (n + 1 - m)) :
    x ^ (n + 1) * β (n + 1) = x ^ (n + 1) * A + C * x / ((n + 1 : ℕ) : ℝ) * (x ^ n * β n)
      + ∑ m ∈ Icc 1 M, (x ^ m * eps m) * (x ^ (n + 1 - m) * β (n + 1 - m)) := by
  have h2 : ∑ m ∈ Icc 1 M, (x ^ m * eps m) * (x ^ (n + 1 - m) * β (n + 1 - m))
      = x ^ (n + 1) * ∑ m ∈ Icc 1 M, eps m * β (n + 1 - m) := by
    rw [mul_sum]
    refine sum_congr rfl fun m hm => ?_
    rw [mem_Icc] at hm
    have e : x ^ (n + 1) = x ^ m * x ^ (n + 1 - m) := by
      rw [← pow_add]
      congr 1
      omega
    rw [e]
    ring
  rw [h2, h]
  ring

/-! ### The tilt `x = 1/γ_k`, the kernel masses and the deficits -/

/-- The diagonal tilt $x=1/\gamma_k$ is positive, for every natural number $k$. -/
theorem xk_pos (k : ℕ) : 0 < xk k := inv_pos.mpr (gam_pos k)

/-- The diagonal tilt $x=1/\gamma_k$ satisfies $x\,\gamma_k=1$, for every natural number $k$. -/
theorem xk_mul_gam (k : ℕ) : xk k * gam k = 1 := by
  unfold xk
  exact inv_mul_cancel₀ (gam_pos k).ne'

/-- `x γ_i ≥ 1` for `i ≥ k` (`γ` is nondecreasing). -/
theorem one_le_xk_mul_gam {k i : ℕ} (hk : 2 ≤ k) (hki : k ≤ i) : 1 ≤ xk k * gam i := by
  have h := mul_le_mul_of_nonneg_left (gam_mono hk hki) (xk_pos k).le
  rw [xk_mul_gam] at h
  exact h

private theorem kapx_nonneg (k m : ℕ) : 0 ≤ kapx k m :=
  mul_nonneg (pow_nonneg (xk_pos k).le m) (eps_nonneg m)

private theorem kapx_one (k : ℕ) : kapx k 1 = xk k := by
  unfold kapx
  rw [pow_one, eps_one, mul_one]

private theorem kbar_zero (k : ℕ) : kbar k 0 = 1 - xk k := by
  unfold kbar
  rw [Finset.Icc_eq_empty (show ¬ (1 : ℕ) ≤ 0 by omega), sum_empty, sub_zero]

private theorem kbar_succ (k M : ℕ) : kbar k (M + 1) = kbar k M - kapx k (M + 1) := by
  unfold kbar
  rw [sum_Icc_succ_top (show 1 ≤ M + 1 by omega)]
  ring

private theorem kbar_one (k : ℕ) : kbar k 1 = 1 - 2 * xk k := by
  unfold kbar
  rw [Icc_self, sum_singleton, kapx_one]
  ring

/-- The deficits `κ̄_M` are nonincreasing in `M`. -/
private theorem kbar_anti (k : ℕ) {M M' : ℕ} (h : M ≤ M') : kbar k M' ≤ kbar k M := by
  induction M', h using Nat.le_induction with
  | base => exact le_rfl
  | succ n hn ih =>
    rw [kbar_succ]
    have := kapx_nonneg k (n + 1)
    linarith

/-- `∑_{M=0}^R κ̄_M = (R+1) κ̄_R + x S_R` (i.e. `∑_{m ≤ R} m κ_m = x S_R`). -/
private theorem sum_kbar (k R : ℕ) :
    ∑ M ∈ range (R + 1), kbar k M = ((R : ℝ) + 1) * kbar k R + xk k * SR k R := by
  induction R with
  | zero => simp [SR]
  | succ R ih =>
    have hk : ((R : ℝ) + 1) * kapx k (R + 1)
        = xk k * (((R : ℝ) * xk k) ^ R / (R.factorial : ℝ)) := by
      have h := mul_eps R
      unfold ren at h
      unfold kapx
      calc ((R : ℝ) + 1) * (xk k ^ (R + 1) * eps (R + 1))
          = xk k ^ (R + 1) * (((R : ℝ) + 1) * eps (R + 1)) := by ring
        _ = xk k ^ (R + 1) * ((R : ℝ) ^ R / (R.factorial : ℝ)) := by rw [h]
        _ = xk k * (((R : ℝ) * xk k) ^ R / (R.factorial : ℝ)) := by ring
    have hS : SR k (R + 1) = SR k R + ((R : ℝ) * xk k) ^ R / (R.factorial : ℝ) := by
      unfold SR
      rw [sum_range_succ]
    have ec : ((R + 1 : ℕ) : ℝ) = (R : ℝ) + 1 := Nat.cast_add_one R
    rw [sum_range_succ, ih, kbar_succ, hS, ec]
    linear_combination hk

/-- `∑_{M=2}^{R} κ̄_M` in closed form (`R = R' + 1`). -/
private theorem sum_kbar_rev (k R' : ℕ) :
    ∑ i ∈ range R', kbar k (R' + 1 - i)
      = ((R' : ℝ) + 2) * kbar k (R' + 1) + xk k * SR k (R' + 1)
        - (1 - xk k) - (1 - 2 * xk k) := by
  have hrev : ∑ i ∈ range R', kbar k (R' + 1 - i) = ∑ M ∈ range R', kbar k (M + 1 + 1) := by
    rw [← sum_range_reflect (fun M => kbar k (M + 1 + 1)) R']
    refine sum_congr rfl fun i hi => ?_
    rw [mem_range] at hi
    have e : R' + 1 - i = R' - 1 - i + 1 + 1 := by omega
    rw [e]
  have h1 := sum_kbar k (R' + 1)
  rw [sum_range_succ', sum_range_succ'] at h1
  have h2 : kbar k (0 + 1) = 1 - 2 * xk k := kbar_one k
  have ec : ((R' + 1 : ℕ) : ℝ) = (R' : ℝ) + 1 := Nat.cast_add_one R'
  rw [h2, kbar_zero, ec] at h1
  rw [hrev]
  linarith

/-! ### The weights `π_j`, their partial sums, and the corrections `𝖾_j`, `ω_i` -/

/-- The weights $\pi_n=x^na_n/n$ of a column $k$ are positive for $n\ge1$. -/
theorem pix_pos (k : ℕ) {n : ℕ} (hn : 0 < n) : 0 < pix k n := by
  unfold pix
  have h1 : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  exact div_pos (mul_pos (pow_pos (xk_pos k) n) (cay_pos hn)) h1

/-- `a_{n+1} = γ_n (1 + 1/n) a_n` for `n ≥ 2`. -/
private theorem cay_succ_gam {n : ℕ} (hn : 2 ≤ n) :
    cay (n + 1) = gam n * (1 + 1 / (n : ℝ)) * cay n := by
  have e : n - 2 + 1 = n - 1 := by omega
  unfold gam
  rw [cay_ratio (show 0 < n by omega), ← pow_succ, e]

/-- `π_{n+1} = x γ_n π_n` for `n ≥ 2`. -/
theorem pix_succ (k : ℕ) {n : ℕ} (hn : 2 ≤ n) : pix k (n + 1) = xk k * gam n * pix k n := by
  have hn0 : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hn1 : (n : ℝ) + 1 ≠ 0 := by positivity
  have ec : ((n + 1 : ℕ) : ℝ) = (n : ℝ) + 1 := Nat.cast_add_one n
  unfold pix
  rw [cay_succ_gam hn, pow_succ (xk k) n, ec]
  field

/-- `π` is nondecreasing on `[k, ∞)`. -/
private theorem pix_mono {k i j : ℕ} (hk : 2 ≤ k) (hki : k ≤ i) (hij : i ≤ j) : pix k i
    ≤ pix k j := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ n hn ih =>
    refine ih.trans ?_
    rw [pix_succ k (show 2 ≤ n by omega)]
    exact le_mul_of_one_le_left (pix_pos k (by omega)).le (one_le_xk_mul_gam hk (by omega))

/-- `π_{j+1} · (z / c_j) = x^{j+1} z / (j+1)`. -/
private theorem pix_mul_div (k j : ℕ) (z : ℝ) :
    pix k (j + 1) * (z / cc j) = xk k ^ (j + 1) * z / ((j : ℝ) + 1) := by
  have h1 : cc j ≠ 0 := (cc_pos j).ne'
  have h2 : (j : ℝ) + 1 ≠ 0 := by positivity
  have h3 : cay (j + 1) = cc j := rfl
  have ec : ((j + 1 : ℕ) : ℝ) = (j : ℝ) + 1 := Nat.cast_add_one j
  unfold pix
  rw [h3, ec]
  field

private theorem pixSum_eq (l i : ℕ) :
    pixSum (l + 1) (l + i + 1) = ∑ r ∈ range (i + 1), pix (l + 1) (l + r + 1) :=
  sum_Icc_eq_range (fun j => pix (l + 1) j) l (i + 1)

/-- `Π_i ≤ (i-k+1) π_i`. -/
private theorem pixSum_le {l : ℕ} (hl : 1 ≤ l) (i : ℕ) :
    pixSum (l + 1) (l + i + 1) ≤ ((i : ℝ) + 1) * pix (l + 1) (l + i + 1) := by
  rw [pixSum_eq]
  have h : ∑ r ∈ range (i + 1), pix (l + 1) (l + r + 1)
      ≤ ∑ _r ∈ range (i + 1), pix (l + 1) (l + i + 1) := by
    refine sum_le_sum fun r hr => ?_
    rw [mem_range] at hr
    exact pix_mono (by omega) (by omega) (by omega)
  have ec : ((i + 1 : ℕ) : ℝ) = (i : ℝ) + 1 := Nat.cast_add_one i
  rw [sum_const, card_range, nsmul_eq_mul, ec] at h
  exact h

private theorem ecor_eq (l i : ℕ) :
    ecor (l + 1) (l + i + 1)
      = ((i : ℝ) + 2) - pixSum (l + 1) (l + i + 1 + 1) / pix (l + 1) (l + i + 1 + 1) := by
  unfold ecor
  push_cast
  ring

/-- `𝖾_j ≥ 0` for `j ≥ k`, since `Π_{j+1} ≤ (j-k+2) π_{j+1}`. -/
theorem ecor_nonneg {k j : ℕ} (hk : 2 ≤ k) (hj : k ≤ j) : 0 ≤ ecor k j := by
  obtain ⟨l, rfl⟩ : ∃ l, k = l + 1 := ⟨k - 1, by omega⟩
  obtain ⟨i, rfl⟩ : ∃ i, j = l + i + 1 := ⟨j - l - 1, by omega⟩
  rw [ecor_eq]
  have hp : 0 < pix (l + 1) (l + i + 1 + 1) := pix_pos (l + 1) (by omega)
  have h : pixSum (l + 1) (l + i + 1 + 1)
      ≤ (((i + 1 : ℕ) : ℝ) + 1) * pix (l + 1) (l + i + 1 + 1) := pixSum_le (by omega) (i + 1)
  have h2 : pixSum (l + 1) (l + i + 1 + 1) / pix (l + 1) (l + i + 1 + 1)
      ≤ ((i + 1 : ℕ) : ℝ) + 1 := by
    rw [div_le_iff₀ hp]
    exact h
  have ec : ((i + 1 : ℕ) : ℝ) = (i : ℝ) + 1 := Nat.cast_add_one i
  rw [ec] at h2
  linarith

private theorem ecorSum_eq (l R' : ℕ) :
    ecorSum (l + 1) (R' + 1)
      = ∑ i ∈ range R', ecor (l + 1) (l + i + 1) / ((l : ℝ) + i + 2) := by
  unfold ecorSum
  have e : l + 1 + (R' + 1) - 2 = l + R' := by omega
  rw [e, sum_Icc_eq_range (fun j => ecor (l + 1) j / ((j : ℝ) + 1)) l R']
  refine sum_congr rfl fun i _ => ?_
  push_cast
  ring

private theorem Somg_eq (l R' : ℕ) :
    Somg (l + 1) (R' + 1)
      = ∑ r ∈ range R', ((r : ℝ) + 2) * omg (l + 1) (l + r + 1 + 1) := by
  unfold Somg
  have e : l + 1 + (R' + 1) - 1 = l + 1 + R' := by omega
  rw [e, sum_Icc_eq_range (fun i => ((i : ℝ) - ((l + 1 : ℕ) : ℝ) + 1) * omg (l + 1) i) (l + 1) R']
  refine sum_congr rfl fun r _ => ?_
  have e2 : l + 1 + r + 1 = l + r + 1 + 1 := by omega
  rw [e2]
  push_cast
  ring

/-- `ω_i ≥ 0` for `i ≥ k`, since `x γ_i ≥ 1`. -/
private theorem omg_nonneg {k i : ℕ} (hk : 2 ≤ k) (hi : k ≤ i) : 0 ≤ omg k i := by
  have h1 : 1 ≤ xk k * gam i := one_le_xk_mul_gam hk hi
  have hi0 : (0 : ℝ) ≤ (i : ℝ) := Nat.cast_nonneg i
  have h2 : (i : ℝ) + 1 ≤ ((i : ℝ) + 1) * (xk k * gam i) :=
    le_mul_of_one_le_right (by linarith) h1
  unfold omg
  rw [sub_nonneg, div_le_one (by linarith)]
  linarith

/-- For $k\ge2$ and every $R$, the sum $\Sigma_\omega=\sum_{i=k+1}^{k+R-1}(i-k+1)\,\omega_i$ of the
flow factors of the column $k$ is nonnegative. -/
theorem Somg_nonneg {k : ℕ} (hk : 2 ≤ k) (R : ℕ) : 0 ≤ Somg k R := by
  unfold Somg
  refine sum_nonneg fun i hi => ?_
  rw [mem_Icc] at hi
  have hik : (k : ℝ) + 1 ≤ (i : ℝ) := by exact_mod_cast hi.1
  exact mul_nonneg (by linarith) (omg_nonneg hk (by omega))

/-! ### The auxiliary sequences -/

/-- `F(n) = Pr(M_n < k)`, `k = l + 1`. -/
private noncomputable def tF (l n : ℕ) : ℝ := zr (l + 1) n / cc n

/-- `F'(n) = Pr(M_n < k - 1)`. -/
private noncomputable def tF' (l n : ℕ) : ℝ := zr l n / cc n

/-- `P(n) = Pr(M_n = k - 1)`. -/
private noncomputable def tP (l n : ℕ) : ℝ := bq l n / cc n

/-- The flow `J(n+1) = F(n+1) - F'(n)`. -/
private noncomputable def tJ (l n : ℕ) : ℝ := tF l (n + 1) - tF' l n

/-- Coefficient of `u_j` in the summed column equation of the level `k - 1`:
`1 - (k-1)x/(j+1) - ∑_{m=1}^{N-j} κ_m` (`j = l+i+1`, `N = l+R+1`). -/
private noncomputable def af (l R i : ℕ) : ℝ :=
  1 - (l : ℝ) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ) - ∑ m ∈ Icc 1 (R - i), kapx (l + 1) m

/-- Coefficient of `u_j`, `k ≤ j ≤ N-2`, in `E1`: `κ̄_{N-j} + x 𝖾_j/(j+1)` (`j = l+i+1`,
`N = l+R'+2`). -/
private noncomputable def cf (l R' i : ℕ) : ℝ :=
  kbar (l + 1) (R' + 1 - i) + xk (l + 1) * ecor (l + 1) (l + i + 1) / ((l : ℝ) + i + 2)

/-- Coefficient of `u_{N-1}` in `E1`: `1 - x - (k-1)x/N`. -/
private noncomputable def cf1 (l R' : ℕ) : ℝ :=
  1 - xk (l + 1) - (l : ℝ) * xk (l + 1) / ((l : ℝ) + R' + 2)

private theorem profD_nonneg (l j : ℕ) : 0 ≤ profD (l + 1) j :=
  mul_nonneg (pow_nonneg (xk_pos (l + 1)).le j) (bq_nonneg l j)

private theorem profD_eq_zero {l j : ℕ} (hl : 1 ≤ l) (hj : j ≤ l) : profD (l + 1) j = 0 := by
  unfold profD
  rw [Nat.add_sub_cancel l 1, bq_eq_zero hl hj, mul_zero]

private theorem tP_nonneg (l n : ℕ) : 0 ≤ tP l n := div_nonneg (bq_nonneg l n) (cc_pos n).le

private theorem tP_eq_zero {l n : ℕ} (hl : 1 ≤ l) (hn : n ≤ l) : tP l n = 0 := by
  unfold tP
  rw [bq_eq_zero hl hn, zero_div]

private theorem tF_eq_one {l n : ℕ} (hn : n ≤ l + 1) : tF l n = 1 := by
  unfold tF
  rw [zr_eq_cc (y := l + 1) (n := n) (by omega) hn]
  exact div_self (cc_pos n).ne'

private theorem tF_split {l : ℕ} (hl : 1 ≤ l) (n : ℕ) : tF l n = tF' l n + tP l n := by
  unfold tF tF' tP
  rw [bq_eq hl]
  ring

private theorem tJ_nonneg {l : ℕ} (hl : 1 ≤ l) (n : ℕ) : 0 ≤ tJ l n := by
  unfold tJ tF tF'
  exact sub_nonneg.mpr (zr_diag_mono hl n)

private theorem tJ_base {l : ℕ} (hl : 1 ≤ l) : tJ l l = 0 := by
  unfold tJ tF'
  rw [tF_eq_one (l := l) (n := l + 1) le_rfl, zr_eq_cc hl le_rfl, div_self (cc_pos l).ne',
    sub_self]

/-- `F(n) - F(n+1) = P(n) - J(n+1)`. -/
private theorem tF_step {l : ℕ} (hl : 1 ≤ l) (n : ℕ) :
    tF l n - tF l (n + 1) = tP l n - tJ l n := by
  unfold tJ
  rw [tF_split hl n]
  ring

/-! ### Step 2: the tilted column equations -/

/-- The tilted column equation of the level `l = k - 1`, in row `n = l + r + 1 ≤ 2k - 1`:
`u_n = π_n F(n-1) + ((k-1)x/n) u_{n-1} + ∑_{m=1}^{n-k} κ_m u_{n-m}`. -/
private theorem profD_rec {l r : ℕ} (hl : 1 ≤ l) (hr : r ≤ l) :
    profD (l + 1) (l + r + 1) = pix (l + 1) (l + r + 1) * tF l (l + r)
      + (l : ℝ) * xk (l + 1) / ((l + r + 1 : ℕ) : ℝ) * profD (l + 1) (l + r)
      + ∑ m ∈ Icc 1 r, kapx (l + 1) m * profD (l + 1) (l + r + 1 - m) := by
  have h := bq_L0 hl (n := l + r + 1) (by omega) (by omega)
  have e1 : l + r + 1 - l - 1 = r := by omega
  rw [e1, Nat.add_sub_cancel] at h
  have hpi : pix (l + 1) (l + r + 1) * tF l (l + r)
      = xk (l + 1) ^ (l + r + 1) * (zr (l + 1) (l + r) / ((l + r + 1 : ℕ) : ℝ)) := by
    unfold tF
    rw [pix_mul_div]
    push_cast
    ring
  rw [hpi]
  unfold profD kapx
  exact tilt (xk (l + 1)) (bq l) _ _ (by omega) h

/-- The tilted column equation of the step, in row `n = l + r + 2 ≤ 2k - 1`:
`η_n = 2 π_n P(n-1) + ((k+1)x/n) η_{n-1} + ∑_{m=1}^{n-k} κ_m η_{n-m}`. -/
private theorem stepD_rec {l r : ℕ} (hl : 1 ≤ l) (hr : r < l) :
    stepD (l + 1) (l + r + 1 + 1) = 2 * (pix (l + 1) (l + r + 1 + 1) * tP l (l + r + 1))
      + ((l : ℝ) + 2) * xk (l + 1) / ((l + r + 1 + 1 : ℕ) : ℝ) * stepD (l + 1) (l + r + 1)
      + ∑ m ∈ Icc 1 (r + 1), kapx (l + 1) m * stepD (l + 1) (l + r + 1 + 1 - m) := by
  have h := dq_col (k := l + 1) (n := l + r + 1 + 1) (by omega) (by omega) (by omega)
  have e1 : l + r + 1 + 1 - (l + 1) = r + 1 := by omega
  rw [e1] at h
  simp only [Nat.add_sub_cancel] at h
  have h' : dq (l + 1) (l + r + 1 + 1) = 2 / ((l + r + 1 + 1 : ℕ) : ℝ) * bq l (l + r + 1)
      + (((l + 1 : ℕ) : ℝ) + 1) / ((l + r + 1 + 1 : ℕ) : ℝ) * dq (l + 1) (l + r + 1)
      + ∑ m ∈ Icc 1 (r + 1), eps m * dq (l + 1) (l + r + 1 + 1 - m) := by
    rw [h]
    ring
  have ht := tilt (xk (l + 1)) (dq (l + 1)) _ _ (by omega) h'
  have hA : 2 * (pix (l + 1) (l + r + 1 + 1) * tP l (l + r + 1))
      = xk (l + 1) ^ (l + r + 1 + 1)
        * (2 / ((l + r + 1 + 1 : ℕ) : ℝ) * bq l (l + r + 1)) := by
    unfold tP
    rw [pix_mul_div]
    push_cast
    ring
  have ec : ((l + 1 : ℕ) : ℝ) + 1 = (l : ℝ) + 2 := by
    push_cast
    ring
  rw [ec] at ht
  rw [hA]
  unfold stepD kapx
  exact ht

/-! ### Step 1: the profile is largest in the top row -/

/-- If `d_{n+1,k} ≤ 0` then `u_n ≤ u_{n+1}` (`n = l + r + 1 ≤ 2k - 1`): by the diagonal lower
bound, `u_n = x^{n+1} γ_k b_{n,k-1}/n! ≤ x^{n+1} b_{n+1,k}/(n+1)! ≤ u_{n+1}`. -/
private theorem profD_step {l r : ℕ} (hl : 1 ≤ l)
    (hd : dq (l + 1) (l + r + 1 + 1) ≤ 0) : profD (l + 1) (l + r + 1)
        ≤ profD (l + 1) (l + r + 1 + 1) := by
  have h1 : bq (l + 1) (l + r + 1 + 1) ≤ bq l (l + r + 1 + 1) := by
    unfold dq at hd
    rw [Nat.add_sub_cancel] at hd
    linarith
  have h2 : gam (l + 1) * bq l (l + r + 1) ≤ bq (l + 1) (l + r + 1 + 1) := by
    have h := bq_diag_lower (k := l + 1) (n := l + r + 1 + 1) (by omega) (by omega)
    rw [Nat.add_sub_cancel, Nat.add_sub_cancel] at h
    exact h
  unfold profD
  calc xk (l + 1) ^ (l + r + 1) * bq l (l + r + 1)
      = xk (l + 1) ^ (l + r + 1 + 1) * (gam (l + 1) * bq l (l + r + 1)) := by
        linear_combination
          (-(xk (l + 1) ^ (l + r + 1) * bq l (l + r + 1))) * xk_mul_gam (l + 1)
    _ ≤ xk (l + 1) ^ (l + r + 1 + 1) * bq l (l + r + 1 + 1) :=
        mul_le_mul_of_nonneg_left (h2.trans h1) (pow_pos (xk_pos (l + 1)) _).le

/-- **Step 1.** If `d_{j,k} ≤ 0` for `k < j ≤ N` then `u_j ≤ u_N` for all `j ≤ N`
(`N = l + R + 1`). -/
private theorem profD_le_top {l R : ℕ} (hl : 1 ≤ l)
    (hN : ∀ j, l + 1 < j → j ≤ l + R + 1 → dq (l + 1) j ≤ 0) :
    ∀ j, j ≤ l + R + 1 → profD (l + 1) j ≤ profD (l + 1) (l + R + 1) := by
  have key : ∀ i j, i ≤ j → j ≤ R → profD (l + 1) (l + i + 1) ≤ profD (l + 1) (l + j + 1) := by
    intro i j hij
    induction j, hij using Nat.le_induction with
    | base => intro _; exact le_rfl
    | succ n hn ih =>
      intro hn'
      exact (ih (by omega)).trans
        (profD_step (r := n) hl (hN (l + n + 1 + 1) (by omega) (by omega)))
  intro j hj
  rcases Nat.lt_or_ge j (l + 1) with h | h
  · rw [profD_eq_zero (l := l) (j := j) hl (by omega)]
    exact profD_nonneg _ _
  · obtain ⟨i, rfl⟩ : ∃ i, j = l + i + 1 := ⟨j - l - 1, by omega⟩
    exact key i R (by omega) le_rfl

/-! ### Step 3: the top row -/

/-- **Step 3.** `u_N (κ̄_R + x(R+1)/N) ≤ π_N F(N-1)`: in the equation of row `N = l + R + 1`
every `u_j` on the right is at most `u_N`. -/
private theorem top_row {l R : ℕ} (hl : 1 ≤ l) (hR : R ≤ l)
    (hmono : ∀ j, j ≤ l + R + 1 → profD (l + 1) j ≤ profD (l + 1) (l + R + 1)) :
    profD (l + 1) (l + R + 1) * (kbar (l + 1) R + xk (l + 1) * ((R : ℝ) + 1) / ((l : ℝ) + R + 1))
      ≤ pix (l + 1) (l + R + 1) * tF l (l + R) := by
  have hx := xk_pos (l + 1)
  have h := profD_rec hl hR
  have ec : ((l + R + 1 : ℕ) : ℝ) = (l : ℝ) + R + 1 := by
    rw [Nat.cast_add_one, Nat.cast_add]
  have hN0 : (l : ℝ) + R + 1 ≠ 0 := by positivity
  rw [ec] at h
  have h1 : profD (l + 1) (l + R) ≤ profD (l + 1) (l + R + 1) := hmono _ (by omega)
  have h2 : ∑ m ∈ Icc 1 R, kapx (l + 1) m * profD (l + 1) (l + R + 1 - m)
      ≤ (∑ m ∈ Icc 1 R, kapx (l + 1) m) * profD (l + 1) (l + R + 1) := by
    rw [sum_mul]
    refine sum_le_sum fun m _ => ?_
    exact mul_le_mul_of_nonneg_left (hmono _ (by omega)) (kapx_nonneg _ _)
  have hc : 0 ≤ (l : ℝ) * xk (l + 1) / ((l : ℝ) + R + 1) :=
    div_nonneg (mul_nonneg (Nat.cast_nonneg l) hx.le) (by positivity)
  have h3 := mul_le_mul_of_nonneg_left h1 hc
  have e3 : profD (l + 1) (l + R + 1) * (kbar (l + 1) R + xk (l + 1) * ((R : ℝ) + 1)
      / ((l : ℝ) + R + 1))
      = profD (l + 1) (l + R + 1) - (l : ℝ) * xk (l + 1) / ((l : ℝ) + R + 1)
          * profD (l + 1) (l + R + 1)
        - (∑ m ∈ Icc 1 R, kapx (l + 1) m) * profD (l + 1) (l + R + 1) := by
    unfold kbar
    field
  rw [e3]
  linarith

/-! ### Step 5: the flow bound -/

/-- `z^{(y+t)}_i - z^{(y)}_i = ∑_{s<t} b_{i,y+s}/i!`. -/
private theorem zr_tel {y : ℕ} (hy : 1 ≤ y) (t i : ℕ) :
    zr (y + t) i - zr y i = ∑ s ∈ range t, bq (y + s) i := by
  induction t with
  | zero => simp
  | succ t ih =>
    rw [sum_range_succ, ← ih, bq_eq (show 1 ≤ y + t by omega), ← Nat.add_assoc]
    ring

/-- The diagonal lower bound summed over the levels `k, …, i-1`:
`γ_k (c_{i-1} - z^{(k-1)}_{i-1}) ≤ c_i - z^{(k)}_i`, `i = l + t + 1 ≤ 2k`. -/
private theorem diag_sum {l t : ℕ} (hl : 1 ≤ l) (ht : t ≤ l + 1) :
    gam (l + 1) * (cc (l + t) - zr l (l + t)) ≤ cc (l + t + 1) - zr (l + 1) (l + t + 1) := by
  have h1 : cc (l + t) - zr l (l + t) = ∑ s ∈ range t, bq (l + s) (l + t) := by
    rw [← zr_tel hl t (l + t), zr_eq_cc (y := l + t) (n := l + t) (by omega) le_rfl]
  have h2 : cc (l + t + 1) - zr (l + 1) (l + t + 1)
      = ∑ s ∈ range t, bq (l + 1 + s) (l + t + 1) := by
    rw [← zr_tel (show 1 ≤ l + 1 by omega) t (l + t + 1),
      zr_eq_cc (y := l + 1 + t) (n := l + t + 1) (by omega) (by omega)]
  rw [h1, h2, mul_sum]
  refine sum_le_sum fun s hs => ?_
  rw [mem_range] at hs
  have hd := bq_diag_lower (k := l + 1 + s) (n := l + t + 1) (by omega) (by omega)
  have e1 : l + 1 + s - 1 = l + s := by omega
  rw [e1, Nat.add_sub_cancel] at hd
  have hg := gam_mono (i := l + 1) (j := l + 1 + s) (by omega) (by omega)
  exact (mul_le_mul_of_nonneg_right hg (bq_nonneg _ _)).trans hd

/-- **Step 5.** `J(i) ≤ ω_i (1 - F'(i-1))`, `i = l + t + 1 ≤ 2k`: divide `diag_sum` by `c_i` and
use `c_i = γ_i (1 + 1/i) c_{i-1}`. -/
private theorem flow_bound {l t : ℕ} (hl : 1 ≤ l) (ht : t ≤ l + 1) :
    tJ l (l + t) ≤ omg (l + 1) (l + t + 1) * (1 - tF' l (l + t)) := by
  have hx : xk (l + 1) ≠ 0 := (xk_pos (l + 1)).ne'
  have hc0 : cc (l + t) ≠ 0 := (cc_pos _).ne'
  have hc1 : 0 < cc (l + t + 1) := cc_pos _
  have hgi : gam (l + t + 1) ≠ 0 := (gam_pos _).ne'
  have hI : ((l + t + 1 : ℕ) : ℝ) ≠ 0 := by positivity
  have hI1 : ((l + t + 1 : ℕ) : ℝ) + 1 ≠ 0 := by positivity
  have hcc : cc (l + t + 1) = gam (l + t + 1) * (1 + 1 / ((l + t + 1 : ℕ) : ℝ)) * cc (l + t) :=
    cay_succ_gam (n := l + t + 1) (by omega)
  have hg : gam (l + 1) = 1 / xk (l + 1) := by
    unfold xk
    rw [one_div, inv_inv]
  have h1 : gam (l + 1) * (cc (l + t) - zr l (l + t)) / cc (l + t + 1)
      ≤ (cc (l + t + 1) - zr (l + 1) (l + t + 1)) / cc (l + t + 1) :=
    div_le_div_of_nonneg_right (diag_sum hl ht) hc1.le
  have e1 : tJ l (l + t)
      = (cc (l + t) - zr l (l + t)) / cc (l + t)
        - (cc (l + t + 1) - zr (l + 1) (l + t + 1)) / cc (l + t + 1) := by
    have h0' : cc (l + t + 1) ≠ 0 := hc1.ne'
    unfold tJ tF tF'
    field
  have e2 : omg (l + 1) (l + t + 1) * (1 - tF' l (l + t))
      = (cc (l + t) - zr l (l + t)) / cc (l + t)
        - gam (l + 1) * (cc (l + t) - zr l (l + t)) / cc (l + t + 1) := by
    unfold omg tF'
    rw [hcc, hg]
    field
  rw [e1, e2]
  linarith

/-! ### Step 6: the budget -/

private theorem one_sub_tF_le {l : ℕ} (hl : 1 ≤ l) (t : ℕ) :
    1 - tF l (l + t + 1) ≤ ∑ s ∈ range t, tP l (l + s + 1) := by
  induction t with
  | zero =>
    have h : tF l (l + 0 + 1) = 1 := tF_eq_one (by omega)
    have h0 : ∑ s ∈ range 0, tP l (l + s + 1) = 0 := by rw [range_zero, sum_empty]
    linarith
  | succ t ih =>
    have h1 := tF_step hl (l + t + 1)
    have h2 := tJ_nonneg hl (l + t + 1)
    have h3 : tF l (l + (t + 1) + 1) = tF l (l + t + 1 + 1) := rfl
    rw [sum_range_succ, h3]
    linarith

/-- **Step 6.** `∑_{j=k}^{N-1} P(j) ≤ 1/2`.  Summing the tilted column equation of the step over
the rows `k+1, …, N` gives
`2 ∑_j π_{j+1} P(j) = η_N - η_k + ∑_i η_i (1 - (k+1)x/(i+1) - ∑_{m=1}^{N-i} κ_m)`,
in which `η_i ≤ 0`, the coefficients are nonnegative (as `κ̄_R ≥ 0`), `η_k = -π_k` and
`π_{j+1} ≥ π_k`. -/
private theorem budget {l R : ℕ} (hl : 1 ≤ l) (hR : R ≤ l) (hκ : 0 ≤ kbar (l + 1) R)
    (hN : ∀ j, l + 1 < j → j ≤ l + R + 1 → dq (l + 1) j ≤ 0) :
    ∑ r ∈ range R, tP l (l + r + 1) ≤ 1 / 2 := by
  have hx := xk_pos (l + 1)
  have hpk : 0 < pix (l + 1) (l + 1) := pix_pos (l + 1) (by omega)
  have hsum : ∑ r ∈ range R, 2 * (pix (l + 1) (l + r + 1 + 1) * tP l (l + r + 1))
      = stepD (l + 1) (l + R + 1) - stepD (l + 1) (l + 1)
        + ∑ i ∈ range R, stepD (l + 1) (l + i + 1)
            * (1 - ((l : ℝ) + 2) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ)
                - ∑ m ∈ Icc 1 (R - i), kapx (l + 1) m) :=
    sum_rec' (stepD (l + 1)) (fun r => 2 * (pix (l + 1) (l + r + 1 + 1) * tP l (l + r + 1)))
      (fun i => ((l : ℝ) + 2) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ))
      (kapx (l + 1)) l R (fun r hr => stepD_rec hl (by omega))
  have hη0 : stepD (l + 1) (l + 1) = -pix (l + 1) (l + 1) := by
    unfold stepD pix
    rw [dq_base (k := l + 1) (by omega)]
    ring
  have hηle : ∀ i, i ≤ R → stepD (l + 1) (l + i + 1) ≤ 0 := by
    intro i hi
    rcases Nat.eq_zero_or_pos i with rfl | hpos
    · have h : stepD (l + 1) (l + 0 + 1) = -pix (l + 1) (l + 1) := hη0
      rw [h]
      linarith
    · exact mul_nonpos_of_nonneg_of_nonpos (pow_nonneg hx.le (l + i + 1))
        (hN (l + i + 1) (by omega) (by omega))
  have hcoef : ∀ i, i < R →
      0 ≤ 1 - ((l : ℝ) + 2) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ)
        - ∑ m ∈ Icc 1 (R - i), kapx (l + 1) m := by
    intro i _
    have h1 : ((l : ℝ) + 2) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ) ≤ xk (l + 1) := by
      rw [div_le_iff₀ (by positivity)]
      push_cast
      nlinarith [mul_nonneg hx.le (Nat.cast_nonneg i : (0 : ℝ) ≤ (i : ℝ))]
    have h2 : ∑ m ∈ Icc 1 (R - i), kapx (l + 1) m ≤ ∑ m ∈ Icc 1 R, kapx (l + 1) m :=
      sum_le_sum_of_subset_of_nonneg (Icc_subset_Icc le_rfl (Nat.sub_le R i))
        (fun m _ _ => kapx_nonneg _ _)
    unfold kbar at hκ
    linarith
  have hS : ∑ i ∈ range R, stepD (l + 1) (l + i + 1)
        * (1 - ((l : ℝ) + 2) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ)
            - ∑ m ∈ Icc 1 (R - i), kapx (l + 1) m) ≤ 0 := by
    refine sum_nonpos fun i hi => ?_
    rw [mem_range] at hi
    exact mul_nonpos_of_nonpos_of_nonneg (hηle i hi.le) (hcoef i hi)
  have hle : pix (l + 1) (l + 1) * (2 * ∑ r ∈ range R, tP l (l + r + 1))
      ≤ ∑ r ∈ range R, 2 * (pix (l + 1) (l + r + 1 + 1) * tP l (l + r + 1)) := by
    rw [mul_sum, mul_sum]
    refine sum_le_sum fun r _ => ?_
    have hm : pix (l + 1) (l + 1) ≤ pix (l + 1) (l + r + 1 + 1) :=
      pix_mono (by omega) le_rfl (by omega)
    have h3 := mul_le_mul_of_nonneg_right hm (tP_nonneg l (l + r + 1))
    linarith
  rw [hsum, hη0] at hle
  have hηN := hηle R le_rfl
  have hfin : pix (l + 1) (l + 1) * (2 * ∑ r ∈ range R, tP l (l + r + 1))
      ≤ pix (l + 1) (l + 1) * 1 := by
    linarith
  have h5 := le_of_mul_le_mul_left hfin hpk
  linarith

/-! ### Step 4: the summed identity -/

/-- The sum of the tilted column equation of the level `k - 1` over the rows `k, …, N = l + R + 1`:
`∑_{n=k}^{N} π_n F(n-1) = u_N + ∑_{j=k}^{N-1} u_j (1 - (k-1)x/(j+1) - ∑_{m=1}^{N-j} κ_m)`. -/
private theorem sum33 {l R : ℕ} (hl : 1 ≤ l) (hR : R ≤ l) :
    ∑ r ∈ range (R + 1), pix (l + 1) (l + r + 1) * tF l (l + r)
      = profD (l + 1) (l + R + 1) + ∑ i ∈ range R, profD (l + 1) (l + i + 1) * af l R i := by
  have hsum : ∑ r ∈ range R, pix (l + 1) (l + (r + 1) + 1) * tF l (l + (r + 1))
      = profD (l + 1) (l + R + 1) - profD (l + 1) (l + 1) + ∑ i ∈ range R,
          profD (l + 1) (l + i + 1) * af l R i :=
    sum_rec' (profD (l + 1)) (fun r => pix (l + 1) (l + (r + 1) + 1) * tF l (l + (r + 1)))
      (fun i => (l : ℝ) * xk (l + 1) / ((l + i + 1 + 1 : ℕ) : ℝ)) (kapx (l + 1)) l R
      (fun r hr => profD_rec (r := r + 1) hl (by omega))
  have h0 : pix (l + 1) (l + 0 + 1) * tF l (l + 0) = profD (l + 1) (l + 1) := by
    have h := profD_rec (r := 0) hl (Nat.zero_le l)
    simp only [Finset.Icc_eq_empty (show ¬ (1 : ℕ) ≤ 0 by omega), sum_empty, add_zero,
      profD_eq_zero hl (le_refl l), mul_zero] at h
    exact h.symm
  rw [sum_range_succ', hsum, h0]
  ring

private theorem af_last (l R' : ℕ) : af l (R' + 1) R' = cf1 l R' := by
  unfold af cf1
  have e1 : R' + 1 - R' = 1 := by omega
  rw [e1, Icc_self, sum_singleton, kapx_one]
  push_cast
  ring

private theorem af_sub (l R' i : ℕ) :
    af l (R' + 1) i
        - xk (l + 1) * (((i : ℝ) + 2) - ecor (l + 1) (l + i + 1)) / ((l : ℝ) + i + 2)
      = cf l R' i := by
  have hN0 : (l : ℝ) + i + 2 ≠ 0 := by positivity
  have ec : ((l + i + 1 + 1 : ℕ) : ℝ) = (l : ℝ) + i + 2 := by push_cast; ring
  unfold af cf kbar
  rw [ec]
  field

/-- **Step 4** (no hypothesis on the signs of `d`): for `N = l + R' + 2 ≤ 2k - 1`,
`F(N-1) Π_N = u_N + u_{N-1} (1 - x - (k-1)x/N) + ∑_{j=k}^{N-2} u_j (κ̄_{N-j} + x 𝖾_j/(j+1))
  + ∑_{i=k}^{N-1} Π_i J(i)`.
(Sum the tilted column equation of the level `k - 1` over the rows `k, …, N`, sum the left side
by parts using
`F(n) - F(n+1) = P(n) - J(n+1)`, and use `Π_{j+1} P(j) = u_j x (j-k+2-𝖾_j)/(j+1)`.) -/
private theorem E1 {l R' : ℕ} (hl : 1 ≤ l) (hR : R' + 1 ≤ l) :
    tF l (l + R' + 1) * pixSum (l + 1) (l + R' + 1 + 1)
      = profD (l + 1) (l + R' + 1 + 1) + profD (l + 1) (l + R' + 1) * cf1 l R'
        + ∑ i ∈ range R', profD (l + 1) (l + i + 1) * cf l R' i
        + ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * tJ l (l + i) := by
  have h33 : ∑ r ∈ range (R' + 1 + 1), pix (l + 1) (l + r + 1) * tF l (l + r)
      = profD (l + 1) (l + R' + 1 + 1) + ∑ i ∈ range (R' + 1),
          profD (l + 1) (l + i + 1) * af l (R' + 1) i :=
    sum33 hl hR
  have hP : pixSum (l + 1) (l + R' + 1 + 1) = ∑ r ∈ range (R' + 1 + 1), pix (l + 1) (l + r + 1) :=
    pixSum_eq l (R' + 1)
  -- summation by parts on the left side
  have hab : ∑ r ∈ range (R' + 1 + 1), pix (l + 1) (l + r + 1) * tF l (l + r)
      = tF l (l + R' + 1) * pixSum (l + 1) (l + R' + 1 + 1)
        + ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * (tP l (l + i) - tJ l (l + i)) := by
    have h := abel_sum (fun r => pix (l + 1) (l + r + 1)) (fun r => tF l (l + r)) (R' + 1)
    have hterm : ∀ i ∈ range (R' + 1),
        (∑ r ∈ range (i + 1), pix (l + 1) (l + r + 1)) * (tF l (l + i) - tF l (l + (i + 1)))
          = pixSum (l + 1) (l + i + 1) * (tP l (l + i) - tJ l (l + i)) := by
      intro i _
      have h1 : tF l (l + i) - tF l (l + (i + 1)) = tP l (l + i) - tJ l (l + i) :=
        tF_step hl (l + i)
      rw [pixSum_eq l i, h1]
    rw [sum_congr rfl hterm, ← hP] at h
    exact h
  have hsplitU : ∑ i ∈ range (R' + 1), profD (l + 1) (l + i + 1) * af l (R' + 1) i
      = ∑ i ∈ range R', profD (l + 1) (l + i + 1) * af l (R' + 1) i + profD (l + 1) (l + R' + 1)
          * cf1 l R' := by
    rw [sum_range_succ, af_last]
  have hJsum : ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * (tP l (l + i) - tJ l (l + i))
      = ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * tP l (l + i)
        - ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * tJ l (l + i) := by
    rw [← sum_sub_distrib]
    refine sum_congr rfl fun i _ => ?_
    ring
  -- the `P`-sum: `Π_{j+1} P(j) = u_j x (j-k+2-𝖾_j)/(j+1)`
  have hPsum : ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * tP l (l + i)
      = ∑ j ∈ range R', profD (l + 1) (l + j + 1)
          * (xk (l + 1) * (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1)) / ((l : ℝ) + j + 2)) := by
    have h0 : pixSum (l + 1) (l + 0 + 1) * tP l (l + 0) = 0 := by
      have h00 : tP l (l + 0) = 0 := tP_eq_zero hl (by omega)
      rw [h00, mul_zero]
    rw [sum_range_succ', h0, add_zero]
    refine sum_congr rfl fun j _ => ?_
    have hpj : pix (l + 1) (l + j + 1 + 1) ≠ 0 := (pix_pos (l + 1) (by omega)).ne'
    have hpm := pix_mul_div (l + 1) (l + j + 1) (bq l (l + j + 1))
    have ec : ((l + j + 1 : ℕ) : ℝ) + 1 = (l : ℝ) + j + 2 := by push_cast; ring
    rw [ec] at hpm
    have hPix : pixSum (l + 1) (l + j + 1 + 1)
        = pix (l + 1) (l + j + 1 + 1) * (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1)) := by
      rw [ecor_eq l j]
      field
    show pixSum (l + 1) (l + j + 1 + 1) * tP l (l + j + 1) = _
    rw [hPix]
    unfold tP profD
    calc pix (l + 1) (l + j + 1 + 1) * (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1))
          * (bq l (l + j + 1) / cc (l + j + 1))
        = (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1))
          * (pix (l + 1) (l + j + 1 + 1) * (bq l (l + j + 1) / cc (l + j + 1))) := by ring
      _ = (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1))
          * (xk (l + 1) ^ (l + j + 1 + 1) * bq l (l + j + 1) / ((l : ℝ) + j + 2)) := by
        rw [hpm]
      _ = xk (l + 1) ^ (l + j + 1) * bq l (l + j + 1)
          * (xk (l + 1) * (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1)) / ((l : ℝ) + j + 2)) := by
        ring
  have hcomb : ∑ i ∈ range R', profD (l + 1) (l + i + 1) * af l (R' + 1) i
        - ∑ j ∈ range R', profD (l + 1) (l + j + 1)
          * (xk (l + 1) * (((j : ℝ) + 2) - ecor (l + 1) (l + j + 1)) / ((l : ℝ) + j + 2))
      = ∑ i ∈ range R', profD (l + 1) (l + i + 1) * cf l R' i := by
    rw [← sum_sub_distrib]
    refine sum_congr rfl fun i _ => ?_
    rw [← af_sub l R' i]
    ring
  rw [hab, hsplitU, hJsum, hPsum] at h33
  linarith

/-! ### Step 7: combination -/

/-- The flow term of `E1` is at most `(π_N/2) Σ_ω`: by Step 5, `J(i) ≤ ω_i (1 - F'(i-1))`, by
Step 6, `1 - F'(i-1) ≤ ∑_j P(j) ≤ 1/2`, and `Π_i ≤ (i-k+1) π_i ≤ (i-k+1) π_N`. -/
private theorem flow_sum {l R' : ℕ} (hl : 1 ≤ l) (hR : R' + 1 ≤ l)
    (hP : ∑ r ∈ range (R' + 1), tP l (l + r + 1) ≤ 1 / 2) :
    ∑ i ∈ range (R' + 1), pixSum (l + 1) (l + i + 1) * tJ l (l + i)
      ≤ pix (l + 1) (l + R' + 1 + 1) / 2 * Somg (l + 1) (R' + 1) := by
  have h0 : pixSum (l + 1) (l + 0 + 1) * tJ l (l + 0) = 0 := by
    have h00 : tJ l (l + 0) = 0 := tJ_base hl
    rw [h00, mul_zero]
  rw [sum_range_succ', h0, add_zero, Somg_eq, mul_sum]
  refine sum_le_sum fun j hj => ?_
  rw [mem_range] at hj
  have hpN : 0 < pix (l + 1) (l + R' + 1 + 1) := pix_pos (l + 1) (by omega)
  have hPix : pixSum (l + 1) (l + j + 1 + 1)
      ≤ (((j + 1 : ℕ) : ℝ) + 1) * pix (l + 1) (l + j + 1 + 1) := pixSum_le hl (j + 1)
  have hmono : pix (l + 1) (l + j + 1 + 1) ≤ pix (l + 1) (l + R' + 1 + 1) :=
    pix_mono (by omega) (by omega) (by omega)
  have hJ0 : 0 ≤ tJ l (l + j + 1) := tJ_nonneg hl (l + j + 1)
  have hω : 0 ≤ omg (l + 1) (l + j + 1 + 1) := omg_nonneg (by omega) (by omega)
  have hflow : tJ l (l + j + 1) ≤ omg (l + 1) (l + j + 1 + 1) * (1 - tF' l (l + j + 1)) :=
    flow_bound (t := j + 1) hl (by omega)
  have hQ : 1 - tF' l (l + j + 1) ≤ 1 / 2 := by
    have h1 := one_sub_tF_le hl j
    have h2 := tF_split hl (l + j + 1)
    have h3 : ∑ s ∈ range (j + 1), tP l (l + s + 1) ≤ ∑ r ∈ range (R' + 1), tP l (l + r + 1) :=
      sum_le_sum_of_subset_of_nonneg (range_subset_range.mpr (by omega))
        (fun i _ _ => tP_nonneg _ _)
    rw [sum_range_succ] at h3
    linarith
  have hJ : tJ l (l + j + 1) ≤ omg (l + 1) (l + j + 1 + 1) * (1 / 2) :=
    hflow.trans (mul_le_mul_of_nonneg_left hQ hω)
  have ec : ((j + 1 : ℕ) : ℝ) + 1 = (j : ℝ) + 2 := by push_cast; ring
  rw [ec] at hPix
  have hj2 : (0 : ℝ) ≤ (j : ℝ) + 2 := by positivity
  have hPix2 : pixSum (l + 1) (l + j + 1 + 1) ≤ ((j : ℝ) + 2) * pix (l + 1) (l + R' + 1 + 1) :=
    hPix.trans (mul_le_mul_of_nonneg_left hmono hj2)
  show pixSum (l + 1) (l + j + 1 + 1) * tJ l (l + j + 1) ≤ _
  calc pixSum (l + 1) (l + j + 1 + 1) * tJ l (l + j + 1)
      ≤ ((j : ℝ) + 2) * pix (l + 1) (l + R' + 1 + 1)
          * (omg (l + 1) (l + j + 1 + 1) * (1 / 2)) :=
        mul_le_mul hPix2 hJ hJ0 (mul_nonneg hj2 hpN.le)
    _ = pix (l + 1) (l + R' + 1 + 1) / 2 * (((j : ℝ) + 2) * omg (l + 1) (l + j + 1 + 1)) := by
        ring

/-- Real-arithmetic core of Step 7: from `u Θ ≤ p F` (Step 3), `F Π ≤ u C + (p/2) Σ` (Steps 1,
4, 5, 6), `Π = p (ρ - 𝖾)` and `F ≥ 1/2` conclude `ρ Θ - C ≤ Θ (𝖾 + Σ)`. -/
private theorem final_arith {Fv PN pN uN C Θ Sω eN ρ : ℝ} (hp : 0 < pN) (hΘ : 0 < Θ)
    (hC : 0 ≤ C) (hSω : 0 ≤ Sω) (hF : 1 / 2 ≤ Fv) (hPi : PN = pN * (ρ - eN))
    (htop : uN * Θ ≤ pN * Fv) (hstar : Fv * PN ≤ uN * C + pN / 2 * Sω) :
    ρ * Θ - C ≤ Θ * (eN + Sω) := by
  have h1 : Fv * PN * Θ ≤ (uN * C + pN / 2 * Sω) * Θ := mul_le_mul_of_nonneg_right hstar hΘ.le
  have h2 : uN * Θ * C ≤ pN * Fv * C := mul_le_mul_of_nonneg_right htop hC
  have h3 : pN * (Fv * ((ρ - eN) * Θ - C)) ≤ pN * (Sω * Θ / 2) := by
    rw [hPi] at h1
    nlinarith [h1, h2]
  have h4 : Fv * ((ρ - eN) * Θ - C) ≤ Sω * Θ / 2 := le_of_mul_le_mul_left h3 hp
  have h5 : 0 ≤ Sω * Θ := mul_nonneg hSω hΘ.le
  by_cases hB : (ρ - eN) * Θ - C ≤ 0
  · nlinarith [hB, h5]
  · have hB' : 0 ≤ (ρ - eN) * Θ - C := (not_le.mp hB).le
    have h6 : 1 / 2 * ((ρ - eN) * Θ - C) ≤ Fv * ((ρ - eN) * Θ - C) :=
      mul_le_mul_of_nonneg_right hF hB'
    nlinarith [h4, h6]

/-- The contrapositive of the crossing criterion, with `k = l + 1`, `R = R' + 1`. -/
private theorem core {l R' : ℕ} (hl : 1 ≤ l) (hR : R' + 1 ≤ l)
    (hκ : 0 ≤ kbar (l + 1) (R' + 1))
    (hN : ∀ j, l + 1 < j → j ≤ l + (R' + 1) + 1 → dq (l + 1) j ≤ 0) :
    xk (l + 1) * (((R' : ℝ) + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2) - 1
        - SR (l + 1) (R' + 1) - ecorSum (l + 1) (R' + 1))
      ≤ (kbar (l + 1) (R' + 1) + xk (l + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2))
        * (ecor (l + 1) (l + R' + 1) + Somg (l + 1) (R' + 1)) := by
  have hx := xk_pos (l + 1)
  have hNr : (0 : ℝ) < (l : ℝ) + R' + 2 := by positivity
  have hpN : 0 < pix (l + 1) (l + R' + 1 + 1) := pix_pos (l + 1) (by omega)
  -- Step 1
  have hmono : ∀ j, j ≤ l + R' + 1 + 1 → profD (l + 1) j ≤ profD (l + 1) (l + R' + 1 + 1) :=
      profD_le_top hl hN
  -- Step 3
  have htop : profD (l + 1) (l + R' + 1 + 1)
        * (kbar (l + 1) (R' + 1) + xk (l + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2))
      ≤ pix (l + 1) (l + R' + 1 + 1) * tF l (l + R' + 1) := by
    have h := top_row hl hR hmono
    have e1 : (((R' + 1 : ℕ) : ℝ) + 1) = (R' : ℝ) + 2 := by push_cast; ring
    have e2 : ((l : ℝ) + ((R' + 1 : ℕ) : ℝ) + 1) = (l : ℝ) + R' + 2 := by push_cast; ring
    rw [e1, e2] at h
    exact h
  -- Step 6
  have hbud := budget hl hR hκ hN
  have hF : 1 / 2 ≤ tF l (l + R' + 1) := by
    have h1 := one_sub_tF_le hl R'
    have h2 := tP_nonneg l (l + R' + 1)
    rw [sum_range_succ] at hbud
    linarith
  -- Steps 4, 5
  have hE1 := E1 hl hR
  have hflow := flow_sum hl hR hbud
  -- signs of the coefficients
  have hc1 : 0 ≤ cf1 l R' := by
    have hx2 : xk (l + 1) ≤ 1 / 2 := by
      have h1 := kbar_anti (l + 1) (show 1 ≤ R' + 1 by omega)
      rw [kbar_one] at h1
      linarith
    have h1 : (l : ℝ) * xk (l + 1) / ((l : ℝ) + R' + 2) ≤ xk (l + 1) := by
      rw [div_le_iff₀ hNr]
      nlinarith [mul_nonneg hx.le (Nat.cast_nonneg R' : (0 : ℝ) ≤ (R' : ℝ))]
    unfold cf1
    linarith
  have hci : ∀ i ∈ range R', 0 ≤ cf l R' i := by
    intro i _
    have h1 : kbar (l + 1) (R' + 1) ≤ kbar (l + 1) (R' + 1 - i) :=
      kbar_anti (l + 1) (Nat.sub_le _ _)
    have h2 : 0 ≤ xk (l + 1) * ecor (l + 1) (l + i + 1) / ((l : ℝ) + i + 2) :=
      div_nonneg (mul_nonneg hx.le (ecor_nonneg (by omega) (by omega))) (by positivity)
    unfold cf
    linarith
  have hsumU : ∑ i ∈ range R', profD (l + 1) (l + i + 1) * cf l R' i
      ≤ profD (l + 1) (l + R' + 1 + 1) * ∑ i ∈ range R', cf l R' i := by
    rw [mul_sum]
    refine sum_le_sum fun i hi => ?_
    have hi' := mem_range.mp hi
    exact mul_le_mul_of_nonneg_right (hmono (l + i + 1) (by omega)) (hci i hi)
  have hstar : tF l (l + R' + 1) * pixSum (l + 1) (l + R' + 1 + 1)
      ≤ profD (l + 1) (l + R' + 1 + 1) * (1 + cf1 l R' + ∑ i ∈ range R', cf l R' i)
        + pix (l + 1) (l + R' + 1 + 1) / 2 * Somg (l + 1) (R' + 1) := by
    have h1 := mul_le_mul_of_nonneg_right (hmono (l + R' + 1) (by omega)) hc1
    rw [hE1]
    linarith
  have hC : 0 ≤ 1 + cf1 l R' + ∑ i ∈ range R', cf l R' i := by
    have h1 := sum_nonneg hci
    linarith
  -- the coefficient sum in closed form
  have hCeq : 1 + cf1 l R' + ∑ i ∈ range R', cf l R' i
      = ((R' : ℝ) + 2) * kbar (l + 1) (R' + 1) + xk (l + 1) * SR (l + 1) (R' + 1)
        + 2 * xk (l + 1) - (l : ℝ) * xk (l + 1) / ((l : ℝ) + R' + 2)
        + xk (l + 1) * ecorSum (l + 1) (R' + 1) := by
    have hs : ∑ i ∈ range R', cf l R' i
        = ∑ i ∈ range R', kbar (l + 1) (R' + 1 - i)
          + xk (l + 1) * ∑ i ∈ range R', ecor (l + 1) (l + i + 1) / ((l : ℝ) + i + 2) := by
      rw [mul_sum, ← sum_add_distrib]
      refine sum_congr rfl fun i _ => ?_
      unfold cf
      ring
    rw [hs, sum_kbar_rev, ← ecorSum_eq l R']
    unfold cf1
    ring
  have hPi : pixSum (l + 1) (l + R' + 1 + 1)
      = pix (l + 1) (l + R' + 1 + 1) * (((R' : ℝ) + 2) - ecor (l + 1) (l + R' + 1)) := by
    have hp0 := hpN.ne'
    rw [ecor_eq l R']
    field
  have hΘ : 0 < kbar (l + 1) (R' + 1) + xk (l + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2) := by
    have h1 : 0 < xk (l + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2) :=
      div_pos (mul_pos hx (by positivity)) hNr
    linarith
  have hfinal := final_arith hpN hΘ hC (Somg_nonneg (by omega) (R' + 1)) hF hPi htop hstar
  have hid : xk (l + 1) * (((R' : ℝ) + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2) - 1
        - SR (l + 1) (R' + 1) - ecorSum (l + 1) (R' + 1))
      = ((R' : ℝ) + 2)
          * (kbar (l + 1) (R' + 1) + xk (l + 1) * ((R' : ℝ) + 2) / ((l : ℝ) + R' + 2))
        - (1 + cf1 l R' + ∑ i ∈ range R', cf l R' i) := by
    have hNr0 := hNr.ne'
    rw [hCeq]
    field
  rw [hid]
  exact hfinal

end CrossCrit

/-- **The crossing criterion.**  If `κ̄_R ≥ 0` and
`(κ̄_R + x(R+1)/N) (𝖾_{N-1} + Σ_ω) < x (R(R+1)/N - 1 - S_R - 𝖤)`, `N = k + R`, then
`d_{j,k} > 0` for some `k < j ≤ N`. -/
theorem cross_criterion {k R : ℕ} (hk : 2 ≤ k) (hR1 : 1 ≤ R) (hR2 : R ≤ k - 1)
    (hκ : 0 ≤ kbar k R)
    (hK : (kbar k R + xk k * ((R : ℝ) + 1) / ((k : ℝ) + R)) * (ecor k (k + R - 1) + Somg k R)
        < xk k * ((R : ℝ) * (R + 1) / ((k : ℝ) + R) - 1 - SR k R - ecorSum k R)) :
    ∃ j, k < j ∧ j ≤ k + R ∧ 0 < dq k j := by
  obtain ⟨l, rfl⟩ : ∃ l, k = l + 1 := ⟨k - 1, by omega⟩
  obtain ⟨R', rfl⟩ : ∃ R', R = R' + 1 := ⟨R - 1, by omega⟩
  by_contra hcon
  have hN : ∀ j, l + 1 < j → j ≤ l + (R' + 1) + 1 → dq (l + 1) j ≤ 0 := by
    intro j h1 h2
    by_contra h
    exact hcon ⟨j, h1, by omega, not_le.mp h⟩
  have hcore := CrossCrit.core (l := l) (R' := R') (by omega) (by omega) hκ hN
  have e1 : l + 1 + (R' + 1) - 1 = l + R' + 1 := by omega
  have e2 : ((R' + 1 : ℕ) : ℝ) = (R' : ℝ) + 1 := Nat.cast_add_one R'
  have e3 : ((l + 1 : ℕ) : ℝ) = (l : ℝ) + 1 := Nat.cast_add_one l
  rw [e1, e2, e3] at hK
  have e4 : (R' : ℝ) + 1 + 1 = (R' : ℝ) + 2 := by ring
  have e5 : (l : ℝ) + 1 + ((R' : ℝ) + 1) = (l : ℝ) + R' + 2 := by ring
  rw [e4, e5] at hK
  exact absurd hcore (not_le.mpr hK)

end Parking
