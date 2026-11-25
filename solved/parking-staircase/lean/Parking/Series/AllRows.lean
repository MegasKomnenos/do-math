import Parking.Counting.Columns
import Parking.Tilt.Basic

/-!
# Three inequalities of a column on all rows

The column equations of `Parking/Counting/Columns.lean` hold on the rows of the single-chain
range.  This file proves, by power series with nonnegative coefficients, three inequalities that
hold on every row.

## Power series with nonnegative coefficients

`PSNonneg f` says that every coefficient of the real power series `f` is nonnegative.  The class is
closed under sums and products, and it contains every series `F` with `F(0) ≥ 0` whose derivative
satisfies a linear equation `F' = G F + S` with `G` and `S` in the class
(`PSNonneg.of_deriv_linear`).  Every positivity statement of this file is obtained from these
three closure properties.

## The series of a column

Fix a column `k ≥ 2` (thresholds `k+1`, `k`, `k-1`).  With `Zs y = ∑ zr y n Xⁿ` the series of the
threshold `y`, `Zs y' = Gp y · Zs y` its last-car equation, and `Ks y = 1 - 1/Zs y` its prime
kernel (`Parking/Series/PrimeKernel.lean`):

* `us k = 1 - Zs (k-1)/Zs k`, and `As k = ∑_{j ≥ k-1} zr (k-1) j X^j`, for which
  `Gp k - Gp (k-1) = k (Zs k - Zs (k-1)) + As k` (`Gp_sub_eq`) and
  `us' = (k Zs (k-1) - As) us + As` (`deriv_us`);
* `logZs y`, the series with `logZs y' = Gp y` and `logZs y (0) = 0` (so `Zs y = exp (logZs y)`);
* `Lg k = logZs k - logZs (k-1)`, with `Lg k' = k (Zs k - Zs (k-1)) + As k` (`deriv_Lg`);
* `Qp k = Zs (k+1) (1 - Ks k) = Zs (k+1)/Zs k`, with `Qp k' = Qp k · Lg (k+1)'` (`deriv_Qp`);
* `Dcol k = Zs (k+1) - 2 Zs k + Zs (k-1)`, whose coefficients are `dq k n` (`coeff_Dcol`).

`Zs k - Zs (k-1)`, `Lg k'`, `Lg k` and `us k` have nonnegative coefficients, and so have the two
series `Xp = Qp k - 1 - Lg (k+1)` and `Y0 = Lg k - us k` (`psNonneg_Xp`, `psNonneg_Y0`).  They
give the decomposition

  `Dcol k · (1 - Ks k) = (Lg (k+1) - Lg k) + Xp + Y0`      (`Dcol_decomp`);

the coefficients of a product `F (1 - Ks y)` are given by `coeff_mul_one_sub_Ks`.

## The three inequalities

Write `Z₊ = Zs (k+1)`, `Z₀ = Zs k`, `Z₋ = Zs (k-1)`, `K = Ks k`, `L₊ = Lg (k+1)`, `L₀ = Lg k`,
`D = Dcol k` (coefficients `δ_n = dq k n`).  The coefficients of `L₊ - L₀` are the tree curvatures
`ξ_t` (`coeff_Lsub`).

* **The column inequality** `col_eq_all`: for `n ≥ k+1`,
  `(k+1) δ_{n-1} + 2 β^{(k-1)}_{n-1} ≤ n (δ_n - ∑_{m=1}^{n-k} κ_m δ_{n-m})`, with `κ_m = kq k m`
  the prime kernel.  The right-hand side is `n [Xⁿ] (D (1 - K)) ≥ n ξ_n`, and
  `n ξ_n` is the left-hand side (`succ_mul_xi_succ`).  On the rows `n ≤ 2k-1` the two sides are
  equal (`Parking.dq_col`).
* **The one-tree bound** `one_tree_bound`: `∑_{t ≤ n} ξ_t · zr k (n-t) ≤ δ_n`.  Multiply the
  decomposition by `Z₀`, which has nonnegative coefficients and satisfies `Z₀ (1 - K) = 1`:
  `D = (L₊ - L₀) Z₀ + Z₀ Xp + Z₀ Y0`.  In terms of forests, the left-hand side keeps the forests in
  which exactly one tree is counted differently by the three thresholds.
* **The diagonal lower bound** `bq_diag_lower`: for `n ≥ 1`,
  `γ_k β^{(k-1)}_{n-1} ≤ β^{(k)}_n`, `γ_k = (1+1/k)^(k-2)`; in terms of the step,
  `γ_k β^{(k-1)}_{n-1} - β^{(k-1)}_n ≤ δ_n` (`dq_diag_lower`).  Put `μ = γ_k`,
  `𝔇 = (Z₊ - Z₀) - μ X (Z₀ - Z₋)` (coefficients `β^{(k)}_n - μ β^{(k-1)}_{n-1}`) and
  `𝔏 = L₊ - μ X L₀`.  Then `𝔇 (1 - K) = 𝔏 + Xp + μ X Y0`; for `i ≥ k`,
  `(i+1) [X^(i+1)] 𝔏 = k [X^i] 𝔇 + (≥ 0)`, the nonnegative part being
  `z^{(k+1)}_i - μ ((i+1)/i) z^{(k)}_{i-1}` (stochastic monotonicity `zr_diag_mono`, `cay_ratio`,
  `gam_mono`) plus `μ ((i+1-k)/i) β^{(k-1)}_{i-1}`; and
  `[X^n] (𝔇 (1 - K)) = [X^n] 𝔇 - ∑_{m=1}^{n} κ_m [X^(n-m)] 𝔇` with `κ_m ≥ 0`.  Strong induction on
  `n` gives `[X^n] 𝔇 ≥ 0`.
-/

namespace Parking
open Finset

local notation "Dx" => PowerSeries.derivative (R := ℝ)

/-! ### The two-level series -/

/-- `us k = 1 - Zs (k-1)/Zs k = b_{k-1}/A_{k-1}` (as exponential generating series). -/
private noncomputable def us (k : ℕ) : PowerSeries ℝ := 1 - Zs (k - 1) * (Zs k)⁻¹

/-- `Zs k - Zs (k-1) = us k * Zs k`. -/
private theorem Zs_sub_eq {k : ℕ} (hk : 2 ≤ k) : Zs k - Zs (k - 1) = us k * Zs k := by
  have h1 := Zs_mul_one_sub_Ks (show 1 ≤ k by omega)
  rw [us, inv_Zs]
  linear_combination Zs (k - 1) * h1

/-- `As k = ∑_{j ≥ k-1} zr (k-1) j X^j`. -/
private noncomputable def As (k : ℕ) : PowerSeries ℝ :=
  PowerSeries.mk fun j => if k ≤ j + 1 then zr (k - 1) j else 0

private theorem coeff_As (k j : ℕ) :
    PowerSeries.coeff j (As k) = if k ≤ j + 1 then zr (k - 1) j else 0 :=
  PowerSeries.coeff_mk j (fun j => if k ≤ j + 1 then zr (k - 1) j else 0)

/-- `Gp k - Gp (k-1) = k (Zs k - Zs (k-1)) + As k`. -/
private theorem Gp_sub_eq {k : ℕ} (hk : 2 ≤ k) :
    Gp k - Gp (k - 1) = PowerSeries.C (k : ℝ) * (Zs k - Zs (k - 1)) + As k := by
  refine PowerSeries.ext fun j => ?_
  rw [map_sub, coeff_Gp, coeff_Gp, map_add, PowerSeries.coeff_C_mul, map_sub, coeff_Zs, coeff_Zs,
    coeff_As]
  by_cases hj : k ≤ j + 1
  · have h1 : min (j + 1) k = k := min_eq_right hj
    have h2 : min (j + 1) (k - 1) = k - 1 := min_eq_right (by omega)
    have h3 : ((k - 1 : ℕ) : ℝ) = (k : ℝ) - 1 := by
      rw [Nat.cast_sub (show 1 ≤ k by omega), Nat.cast_one]
    rw [h1, h2, ite_eq_left hj, h3]
    ring
  · have h1 : min (j + 1) k = j + 1 := min_eq_left (by omega)
    have h2 : min (j + 1) (k - 1) = j + 1 := min_eq_left (by omega)
    rw [h1, h2, ite_eq_right hj, zr_eq_cc (show 1 ≤ k by omega) (show j ≤ k by omega),
      zr_eq_cc (show 1 ≤ k - 1 by omega) (show j ≤ k - 1 by omega)]
    ring

/-- `us' = (k Zs (k-1) - As k) us + As k`. -/
private theorem deriv_us {k : ℕ} (hk : 2 ≤ k) :
    Dx (us k) = (PowerSeries.C (k : ℝ) * Zs (k - 1) - As k) * us k + As k := by
  have hk1 : 1 ≤ k := by omega
  have hk2 : 1 ≤ k - 1 := by omega
  have hZ := deriv_Zs hk2
  have hK := deriv_Ks hk1
  have hG := Gp_sub_eq hk
  have hZE := Zs_mul_one_sub_Ks hk1
  have hu : us k = 1 - Zs (k - 1) * (1 - Ks k) := by
    rw [us, inv_Zs]
  have hD : Dx (us k) = -(Zs (k - 1) * Dx (1 - Ks k) + (1 - Ks k) * Dx (Zs (k - 1))) := by
    rw [hu, map_sub, Derivation.map_one_eq_zero, zero_sub, Derivation.leibniz, smul_eq_mul,
      smul_eq_mul]
  have hE : Dx (1 - Ks k) = -Dx (Ks k) := by
    rw [map_sub, Derivation.map_one_eq_zero, zero_sub]
  linear_combination hD - Zs (k - 1) * hE + Zs (k - 1) * hK - (1 - Ks k) * hZ -
    (PowerSeries.C (k : ℝ) * Zs (k - 1) - As k) * hu + (Zs (k - 1) * (1 - Ks k)) * hG +
    (PowerSeries.C (k : ℝ) * Zs (k - 1)) * hZE

/-! ### Power series with nonnegative coefficients -/

/-- All coefficients of the power series are nonnegative. -/
private def PSNonneg (f : PowerSeries ℝ) : Prop := ∀ n, 0 ≤ PowerSeries.coeff n f

private theorem PSNonneg.add {f g : PowerSeries ℝ} (hf : PSNonneg f) (hg : PSNonneg g) :
    PSNonneg (f + g) := fun n => by
  rw [map_add]
  exact add_nonneg (hf n) (hg n)

private theorem PSNonneg.mul {f g : PowerSeries ℝ} (hf : PSNonneg f) (hg : PSNonneg g) :
    PSNonneg (f * g) := fun n => by
  rw [TreeSeries.coeff_mul_range]
  exact Finset.sum_nonneg fun j _ => mul_nonneg (hf j) (hg (n - j))

private theorem PSNonneg.C_mul {c : ℝ} (hc : 0 ≤ c) {f : PowerSeries ℝ} (hf : PSNonneg f) :
    PSNonneg (PowerSeries.C c * f) := fun n => by
  rw [PowerSeries.coeff_C_mul]
  exact mul_nonneg hc (hf n)

private theorem PSNonneg.X_mul {f : PowerSeries ℝ} (hf : PSNonneg f) :
    PSNonneg (PowerSeries.X * f)
  | 0 => (PowerSeries.coeff_zero_X_mul f).ge
  | n + 1 => by
    rw [PowerSeries.coeff_succ_X_mul]
    exact hf n

/-- If `F' = G F + S` with `G`, `S` coefficientwise nonnegative and `F(0) ≥ 0`, then `F` is
coefficientwise nonnegative. -/
private theorem PSNonneg.of_deriv_linear {F G S : PowerSeries ℝ} (hG : PSNonneg G) (hS : PSNonneg S)
    (h : Dx F = G * F + S) (h0 : 0 ≤ PowerSeries.coeff 0 F) : PSNonneg F := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => exact h0
    | succ n =>
      have hc := congrArg (PowerSeries.coeff n) h
      rw [PowerSeries.coeff_derivative, map_add, TreeSeries.coeff_mul_range] at hc
      have hpos : 0 ≤ PowerSeries.coeff (n + 1) F * ((n : ℝ) + 1) := by
        rw [hc]
        exact add_nonneg
          (Finset.sum_nonneg fun j _ => mul_nonneg (hG j) (ih (n - j) (by omega))) (hS n)
      exact nonneg_of_mul_nonneg_left hpos (by positivity)

/-- A series with nonnegative constant term and coefficientwise nonnegative derivative. -/
private theorem PSNonneg.of_deriv {F : PowerSeries ℝ} (h0 : 0 ≤ PowerSeries.coeff 0 F)
    (hd : PSNonneg (Dx F)) : PSNonneg F
  | 0 => h0
  | n + 1 => by
    have h := hd n
    rw [PowerSeries.coeff_derivative] at h
    exact nonneg_of_mul_nonneg_left h (by positivity)

/-- The constant coefficient of a product. -/
private theorem coeff_zero_mul (f g : PowerSeries ℝ) :
    PowerSeries.coeff 0 (f * g) = PowerSeries.coeff 0 f * PowerSeries.coeff 0 g := by
  simp only [PowerSeries.coeff_zero_eq_constantCoeff, map_mul]

/-! ### The series of one threshold -/

private theorem psNonneg_Zs (y : ℕ) : PSNonneg (Zs y) := fun n => by
  rw [coeff_Zs]
  exact zr_nonneg y n

private theorem psNonneg_As (k : ℕ) : PSNonneg (As k) := fun n => by
  rw [coeff_As]
  split_ifs
  exacts [zr_nonneg _ _, le_rfl]

/-- The prime kernel is nonnegative. -/
private theorem kq_nonneg {y : ℕ} (hy : 2 ≤ y) (m : ℕ) : 0 ≤ kq y m := by
  have h := kqT_nonneg hy (zero_le_one : (0 : ℝ) ≤ 1) m
  rwa [kqT, one_pow, mul_one] at h

/-- Coefficients of `F * (1 - Ks y)`: a renewal difference with the prime kernel. -/
private theorem coeff_mul_one_sub_Ks {y : ℕ} (hy : 1 ≤ y) (F : PowerSeries ℝ) (n : ℕ) :
    PowerSeries.coeff n (F * (1 - Ks y)) =
      PowerSeries.coeff n F - ∑ m ∈ Icc 1 n, kq y m * PowerSeries.coeff (n - m) F := by
  have hs : ∀ m ∈ Icc 1 n, PowerSeries.coeff m (1 - Ks y) * PowerSeries.coeff (n - m) F
      = -(kq y m * PowerSeries.coeff (n - m) F) := fun m hm => by
    rw [coeff_one_sub_Ks_of_pos y (Finset.mem_Icc.mp hm).1, neg_mul]
  rw [mul_comm F (1 - Ks y), TreeSeries.coeff_mul_split, coeff_one_sub_Ks_zero hy, one_mul,
    Finset.sum_congr rfl hs, Finset.sum_neg_distrib, sub_eq_add_neg]

/-- The series `Γ_y` with `Γ_y' = Gp y` and `Γ_y(0) = 0`. -/
private noncomputable def logZs (y : ℕ) : PowerSeries ℝ :=
  SingleChain.Gser (fun t => ((min t y : ℕ) : ℝ)) (zr y)

private theorem deriv_logZs (y : ℕ) : Dx (logZs y) = Gp y := rfl

private theorem coeff_logZs (y t : ℕ) :
    PowerSeries.coeff t (logZs y) =
      if t = 0 then 0 else ((min t y : ℕ) : ℝ) / (t : ℝ) * zr y (t - 1) := by
  rw [logZs, SingleChain.Gser, PowerSeries.coeff_mk]

private theorem coeff_zero_logZs (y : ℕ) : PowerSeries.coeff 0 (logZs y) = 0 := by
  rw [coeff_logZs, ite_eq_left rfl]

/-! ### Two adjacent thresholds -/

/-- `Zs k - Zs (k-1)` has nonnegative coefficients. -/
private theorem psNonneg_Zs_sub (k : ℕ) : PSNonneg (Zs k - Zs (k - 1)) := fun n => by
  rw [map_sub, coeff_Zs, coeff_Zs]
  exact sub_nonneg.mpr (zr_mono (Nat.sub_le k 1) n)

/-- `L_k = Γ_k - Γ_{k-1}`. -/
private noncomputable def Lg (k : ℕ) : PowerSeries ℝ := logZs k - logZs (k - 1)

private theorem coeff_zero_Lg (k : ℕ) : PowerSeries.coeff 0 (Lg k) = 0 := by
  rw [Lg, map_sub, coeff_zero_logZs, coeff_zero_logZs, sub_zero]

/-- `L_k' = Gp k - Gp (k-1) = k (Zs k - Zs (k-1)) + As k`. -/
private theorem deriv_Lg {k : ℕ} (hk : 2 ≤ k) :
    Dx (Lg k) = PowerSeries.C (k : ℝ) * (Zs k - Zs (k - 1)) + As k := by
  rw [Lg, map_sub, deriv_logZs, deriv_logZs]
  exact Gp_sub_eq hk

private theorem psNonneg_deriv_Lg {k : ℕ} (hk : 2 ≤ k) : PSNonneg (Dx (Lg k)) := by
  rw [deriv_Lg hk]
  exact ((psNonneg_Zs_sub k).C_mul (Nat.cast_nonneg k)).add (psNonneg_As k)

private theorem psNonneg_Lg {k : ℕ} (hk : 2 ≤ k) : PSNonneg (Lg k) :=
  PSNonneg.of_deriv (coeff_zero_Lg k).ge (psNonneg_deriv_Lg hk)

private theorem coeff_zero_us {k : ℕ} (hk : 2 ≤ k) : PowerSeries.coeff 0 (us k) = 0 := by
  rw [us, inv_Zs, map_sub, PowerSeries.coeff_zero_one, coeff_zero_mul, coeff_Zs,
    zr_zero (show 1 ≤ k - 1 by omega), coeff_one_sub_Ks_zero (show 1 ≤ k by omega), mul_one,
    sub_self]

/-- `us k = 1 - Zs (k-1)/Zs k` has nonnegative coefficients: it satisfies
`us' = (k Zs (k-1) - As k) us + As k`, and the coefficients of `k Zs (k-1) - As k` are `k` or
`k - 1` times those of `Zs (k-1)`. -/
private theorem psNonneg_us {k : ℕ} (hk : 2 ≤ k) : PSNonneg (us k) := by
  have hG : PSNonneg (PowerSeries.C (k : ℝ) * Zs (k - 1) - As k) := fun j => by
    have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
    have h1 : 0 ≤ ((k : ℝ) - 1) * zr (k - 1) j := mul_nonneg (by linarith) (zr_nonneg _ _)
    have h2 : 0 ≤ (k : ℝ) * zr (k - 1) j := mul_nonneg (by linarith) (zr_nonneg _ _)
    rw [map_sub, PowerSeries.coeff_C_mul, coeff_Zs, coeff_As]
    split_ifs <;> linarith
  exact PSNonneg.of_deriv_linear hG (psNonneg_As k) (deriv_us hk) (coeff_zero_us hk).ge

/-- `Zs (k-1) / Zs k = 1 - us k`. -/
private theorem Zs_pred_mul_one_sub_Ks (k : ℕ) : Zs (k - 1) * (1 - Ks k) = 1 - us k := by
  rw [us, inv_Zs]
  ring

/-- `Zs (k-1) us k = (Zs k - Zs (k-1)) - (Zs k - Zs (k-1)) us k`. -/
private theorem Zs_pred_mul_us {k : ℕ} (hk : 2 ≤ k) :
    Zs (k - 1) * us k = (Zs k - Zs (k - 1)) - (Zs k - Zs (k - 1)) * us k := by
  linear_combination (-1 : PowerSeries ℝ) * Zs_sub_eq hk

/-- `Qp k = Zs (k+1) / Zs k`. -/
private noncomputable def Qp (k : ℕ) : PowerSeries ℝ := Zs (k + 1) * (1 - Ks k)

private theorem coeff_zero_Qp {k : ℕ} (hk : 1 ≤ k) : PowerSeries.coeff 0 (Qp k) = 1 := by
  rw [Qp, coeff_zero_mul, coeff_Zs, zr_zero (show 1 ≤ k + 1 by omega), coeff_one_sub_Ks_zero hk,
    mul_one]

/-- `Qp' = Qp L_{k+1}'`. -/
private theorem deriv_Qp {k : ℕ} (hk : 1 ≤ k) : Dx (Qp k) = Qp k * Dx (Lg (k + 1)) := by
  have hZ := deriv_Zs (y := k + 1) (by omega)
  have hK := deriv_Ks (y := k) hk
  have hQ : Qp k = Zs (k + 1) * (1 - Ks k) := rfl
  have hD : Dx (Qp k) = Zs (k + 1) * Dx (1 - Ks k) + (1 - Ks k) * Dx (Zs (k + 1)) := by
    rw [hQ, Derivation.leibniz, smul_eq_mul, smul_eq_mul]
  have hE : Dx (1 - Ks k) = -Dx (Ks k) := by
    rw [map_sub, Derivation.map_one_eq_zero, zero_sub]
  have hL : Dx (Lg (k + 1)) = Gp (k + 1) - Gp k := map_sub _ _ _
  rw [hL]
  linear_combination hD + Zs (k + 1) * hE - Zs (k + 1) * hK + (1 - Ks k) * hZ
    - (Gp (k + 1) - Gp k) * hQ

/-! ### The second difference of a column and its decomposition -/

/-- The second difference series `D = Zs (k+1) - 2 Zs k + Zs (k-1)`. -/
private noncomputable def Dcol (k : ℕ) : PowerSeries ℝ := (Zs (k + 1) - Zs k) - (Zs k - Zs (k - 1))

private theorem coeff_Dcol {k : ℕ} (hk : 2 ≤ k) (n : ℕ) : PowerSeries.coeff n (Dcol k)
    = dq k n := by
  rw [Dcol, map_sub, map_sub, map_sub, coeff_Zs, coeff_Zs, coeff_Zs, dq,
    bq_eq (show 1 ≤ k by omega), bq_eq (show 1 ≤ k - 1 by omega),
    Nat.sub_add_cancel (show 1 ≤ k by omega)]

/-- `Xp = Qp - 1 - L_{k+1}` has nonnegative coefficients: `Xp(0) = 0` and
`Xp' = L_{k+1}' Xp + L_{k+1} L_{k+1}'`. -/
private theorem psNonneg_Xp {k : ℕ} (hk : 1 ≤ k) : PSNonneg (Qp k - 1 - Lg (k + 1)) := by
  have hk2 : 2 ≤ k + 1 := by omega
  refine PSNonneg.of_deriv_linear (psNonneg_deriv_Lg hk2)
    ((psNonneg_Lg hk2).mul (psNonneg_deriv_Lg hk2)) ?_ (le_of_eq ?_)
  · rw [map_sub, map_sub, Derivation.map_one_eq_zero, sub_zero, deriv_Qp hk]
    ring
  · rw [map_sub, map_sub, coeff_zero_Qp hk, PowerSeries.coeff_zero_one, coeff_zero_Lg, sub_self,
      sub_zero]

/-- `Y0 = L_k - us k` has nonnegative coefficients: `Y0(0) = 0` and `Y0' = us L_k'`. -/
private theorem psNonneg_Y0 {k : ℕ} (hk : 2 ≤ k) : PSNonneg (Lg k - us k) := by
  refine PSNonneg.of_deriv (le_of_eq ?_) ?_
  · rw [map_sub, coeff_zero_Lg, coeff_zero_us hk, sub_zero]
  · have hd : Dx (Lg k - us k) = us k * Dx (Lg k) := by
      rw [map_sub, deriv_us hk, deriv_Lg hk]
      linear_combination (-(PowerSeries.C (k : ℝ))) * Zs_pred_mul_us hk
    rw [hd]
    exact (psNonneg_us hk).mul (psNonneg_deriv_Lg hk)

/-- **The decomposition** `D (1 - Ks k) = (L_{k+1} - L_k) + Xp + Y0`
(both sides are `Qp - 1 - us`). -/
private theorem Dcol_decomp {k : ℕ} (hk : 1 ≤ k) :
    Dcol k * (1 - Ks k) = (Lg (k + 1) - Lg k) + (Qp k - 1 - Lg (k + 1)) + (Lg k - us k) := by
  rw [Dcol, Qp]
  linear_combination (-2 : PowerSeries ℝ) * Zs_mul_one_sub_Ks hk + Zs_pred_mul_one_sub_Ks k


/-- `[X^t] (L₊ - L₀) = ξ_t`. -/
private theorem coeff_Lsub (k t : ℕ) : PowerSeries.coeff t (Lg (k + 1) - Lg k) = xi k t := by
  rw [Lg, Lg, Nat.add_sub_cancel, map_sub, map_sub, map_sub, coeff_logZs, coeff_logZs, coeff_logZs,
      xi]
  split_ifs <;> ring

/-! ### The column inequality -/

/-- **The column inequality on all rows.**  For `k ≥ 2` and `n ≥ k+1`:
`(k+1) δ_{n-1} + 2 β^{(k-1)}_{n-1} ≤ n (δ_n - ∑_{m=1}^{n-k} κ_m δ_{n-m})`. -/
theorem col_eq_all {k n : ℕ} (hk : 2 ≤ k) (hn : k + 1 ≤ n) :
    ((k : ℝ) + 1) * dq k (n - 1) + 2 * bq (k - 1) (n - 1)
      ≤ (n : ℝ) * (dq k n - ∑ m ∈ Finset.Icc 1 (n - k), kq k m * dq k (n - m)) := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  have hk1 : 1 ≤ k := by omega
  -- the coefficient of `X^(m+1)` in the decomposition of `D (1 - K)`
  have h := congrArg (PowerSeries.coeff (m + 1)) (Dcol_decomp hk1)
  rw [coeff_mul_one_sub_Ks hk1, coeff_Dcol hk, map_add, map_add, coeff_Lsub] at h
  -- the kernel sum stops at `m + 1 - k`, because `δ_j = 0` for `j < k`
  have hsum : ∑ i ∈ Icc 1 (m + 1), kq k i * PowerSeries.coeff (m + 1 - i) (Dcol k)
      = ∑ i ∈ Icc 1 (m + 1 - k), kq k i * dq k (m + 1 - i) := by
    simp only [coeff_Dcol hk]
    exact sum_Icc_trunc (f := fun i => kq k i * dq k (m + 1 - i)) (by omega)
      fun i hi1 hi2 => by
        show kq k i * dq k (m + 1 - i) = 0
        rw [dq_eq_zero hk (by omega : m + 1 - i < k), mul_zero]
  rw [hsum] at h
  have hX := psNonneg_Xp hk1 (m + 1)
  have hY := psNonneg_Y0 hk (m + 1)
  rw [Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one, ← succ_mul_xi_succ hk (show k ≤ m by omega)]
  exact mul_le_mul_of_nonneg_left (by linarith) (by positivity)

/-! ### The one-tree bound -/

/-- **The one-tree lower bound**: `∑_{t ≤ n} ξ_t · zr k (n-t) ≤ δ_n`. -/
theorem one_tree_bound {k : ℕ} (hk : 2 ≤ k) (n : ℕ) :
    ∑ t ∈ range (n + 1), xi k t * zr k (n - t) ≤ dq k n := by
  have hk1 : 1 ≤ k := by omega
  -- the decomposition multiplied by `Zs k`
  have hid : Dcol k = (Lg (k + 1) - Lg k) * Zs k + Zs k * (Qp k - 1 - Lg (k + 1))
      + Zs k * (Lg k - us k) := by
    linear_combination Zs k * Dcol_decomp hk1 - Dcol k * Zs_mul_one_sub_Ks hk1
  have hc := congrArg (PowerSeries.coeff n) hid
  rw [coeff_Dcol hk, map_add, map_add, TreeSeries.coeff_mul_range (Lg (k + 1) - Lg k)] at hc
  simp only [coeff_Lsub, coeff_Zs] at hc
  have hX := ((psNonneg_Zs k).mul (psNonneg_Xp hk1)) n
  have hY := ((psNonneg_Zs k).mul (psNonneg_Y0 hk)) n
  linarith

/-! ### The diagonal lower bound -/

/-- `𝔇 = (Zs (k+1) - Zs k) - γ_k X (Zs k - Zs (k-1))`. -/
private noncomputable def Dser (k : ℕ) : PowerSeries ℝ :=
  (Zs (k + 1) - Zs k) - PowerSeries.C (gam k) * (PowerSeries.X * (Zs k - Zs (k - 1)))

/-- `𝔏 = L₊ - γ_k X L₀`. -/
private noncomputable def Lser (k : ℕ) : PowerSeries ℝ :=
  Lg (k + 1) - PowerSeries.C (gam k) * (PowerSeries.X * Lg k)

private theorem gam_nonneg (k : ℕ) : 0 ≤ gam k := by
  unfold gam
  positivity

private theorem coeff_Dser_pos {k i : ℕ} (hi : 1 ≤ i) :
    PowerSeries.coeff i (Dser k) =
      (zr (k + 1) i - zr k i) - gam k * (zr k (i - 1) - zr (k - 1) (i - 1)) := by
  obtain ⟨m, rfl⟩ : ∃ m, i = m + 1 := ⟨i - 1, by omega⟩
  rw [Dser, map_sub, map_sub, coeff_Zs, coeff_Zs, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_succ_X_mul, map_sub, coeff_Zs, coeff_Zs, Nat.add_sub_cancel]

/-- The coefficients of `𝔇` vanish up to the index `k`. -/
private theorem coeff_Dser_of_le {k n : ℕ} (hk : 2 ≤ k) (hn : n ≤ k) :
    PowerSeries.coeff n (Dser k) = 0 := by
  rcases Nat.eq_zero_or_pos n with rfl | hn0
  · rw [Dser, map_sub, map_sub, coeff_Zs, coeff_Zs, PowerSeries.coeff_C_mul,
      PowerSeries.coeff_zero_X_mul, zr_zero (by omega : 1 ≤ k + 1), zr_zero (by omega : 1 ≤ k)]
    ring
  · rw [coeff_Dser_pos (k := k) hn0,
      zr_eq_cc (y := k + 1) (n := n) (by omega) (by omega),
      zr_eq_cc (y := k) (n := n) (by omega) (by omega),
      zr_eq_cc (y := k) (n := n - 1) (by omega) (by omega),
      zr_eq_cc (y := k - 1) (n := n - 1) (by omega) (by omega)]
    ring

/-- Coefficients of `Γ_y` beyond the threshold. -/
private theorem coeff_Gam_of_le {y t : ℕ} (ht0 : 1 ≤ t) (hyt : y ≤ t) :
    PowerSeries.coeff t (logZs y) = (y : ℝ) / (t : ℝ) * zr y (t - 1) := by
  rw [coeff_logZs, ite_eq_right (by omega : ¬ t = 0), min_eq_right hyt]

private theorem coeff_Lser_succ {k i : ℕ} (hk : 2 ≤ k) (hki : k ≤ i) :
    PowerSeries.coeff (i + 1) (Lser k) =
      ((k : ℝ) + 1) / ((i : ℝ) + 1) * zr (k + 1) i - (k : ℝ) / ((i : ℝ) + 1) * zr k i
        - gam k * ((k : ℝ) / (i : ℝ) * zr k (i - 1)
            - ((k : ℝ) - 1) / (i : ℝ) * zr (k - 1) (i - 1)) := by
  have h1 := coeff_Gam_of_le (y := k + 1) (t := i + 1) (by omega) (by omega)
  have h2 := coeff_Gam_of_le (y := k) (t := i + 1) (by omega) (by omega)
  have h3 := coeff_Gam_of_le (y := k) (t := i) (by omega) hki
  have h4 := coeff_Gam_of_le (y := k - 1) (t := i) (by omega) (by omega)
  rw [Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one, Nat.cast_add, Nat.cast_one] at h1
  rw [Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one] at h2
  rw [Nat.cast_sub (by omega : 1 ≤ k), Nat.cast_one] at h4
  rw [Lser, Lg, Lg, Nat.add_sub_cancel, map_sub, map_sub, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_succ_X_mul, map_sub, h1, h2, h3, h4]

/-- `𝔇 (1 - Ks k) = 𝔏 + Xp + γ_k X Y0`. -/
private theorem Dser_decomp {k : ℕ} (hk : 2 ≤ k) :
    Dser k * (1 - Ks k) =
      Lser k + (Qp k - 1 - Lg (k + 1))
        + PowerSeries.C (gam k) * (PowerSeries.X * (Lg k - us k)) := by
  rw [Dser, Lser, Qp]
  linear_combination
    (-1 - PowerSeries.C (gam k) * PowerSeries.X) * Zs_mul_one_sub_Ks (show 1 ≤ k by omega)
    + (PowerSeries.C (gam k) * PowerSeries.X) * Zs_pred_mul_one_sub_Ks k

/-- Stochastic monotonicity in the form used here: for `k ≤ i`,
`γ_k z^{(k)}_{i-1}/i ≤ z^{(k+1)}_i/(i+1)`. -/
private theorem diag_bracket {k i : ℕ} (hk : 2 ≤ k) (hki : k ≤ i) :
    gam k * (zr k (i - 1) / (i : ℝ)) ≤ zr (k + 1) i / ((i : ℝ) + 1) := by
  have hi1 : 1 ≤ i := by omega
  have hir : (0 : ℝ) < (i : ℝ) := Nat.cast_pos.mpr (by omega)
  have hine : (i : ℝ) ≠ 0 := hir.ne'
  have hi1' : (0 : ℝ) < (i : ℝ) + 1 := by positivity
  have hc0 : 0 < cc (i - 1) := cc_pos _
  -- `c_i = γ_i (1 + 1/i) c_{i-1}`
  have hcr : cc i = gam i * (1 + 1 / (i : ℝ)) * cc (i - 1) := by
    rw [← psi_eq_gam (show 2 ≤ i by omega), cc, cc, Nat.sub_add_cancel hi1]
    exact cay_ratio (by omega)
  have hd := zr_diag_mono (y := k) (by omega) (i - 1)
  rw [Nat.sub_add_cancel hi1, div_le_div_iff₀ hc0 (cc_pos i), hcr] at hd
  have hd2 : zr k (i - 1) * (gam i * (1 + 1 / (i : ℝ))) ≤ zr (k + 1) i :=
    le_of_mul_le_mul_right (by linarith) hc0
  rw [le_div_iff₀ hi1']
  calc gam k * (zr k (i - 1) / (i : ℝ)) * ((i : ℝ) + 1)
      ≤ gam i * (zr k (i - 1) / (i : ℝ)) * ((i : ℝ) + 1) :=
        mul_le_mul_of_nonneg_right
          (mul_le_mul_of_nonneg_right (gam_mono hk hki) (div_nonneg (zr_nonneg _ _) hir.le))
          hi1'.le
    _ = zr k (i - 1) * (gam i * (1 + 1 / (i : ℝ))) := by
        field
    _ ≤ zr (k + 1) i := hd2

/-- For `i ≥ k`: `k [X^i] 𝔇 ≤ (i+1) [X^(i+1)] 𝔏`. -/
private theorem Lser_coeff_ge {k i : ℕ} (hk : 2 ≤ k) (hki : k ≤ i) :
    (k : ℝ) * PowerSeries.coeff i (Dser k)
      ≤ ((i : ℝ) + 1) * PowerSeries.coeff (i + 1) (Lser k) := by
  have hi1 : 1 ≤ i := by omega
  have hI : (0 : ℝ) < (i : ℝ) := Nat.cast_pos.mpr (by omega)
  have hI0 : (i : ℝ) ≠ 0 := hI.ne'
  have hI1 : (0 : ℝ) < (i : ℝ) + 1 := by positivity
  have hI1' : (i : ℝ) + 1 ≠ 0 := hI1.ne'
  have hKI : (k : ℝ) ≤ (i : ℝ) := Nat.cast_le.mpr hki
  have hmono : zr (k - 1) (i - 1) ≤ zr k (i - 1) := zr_mono (Nat.sub_le k 1) (i - 1)
  have t1 : 0 ≤ ((i : ℝ) + 1) *
      (zr (k + 1) i / ((i : ℝ) + 1) - gam k * (zr k (i - 1) / (i : ℝ))) :=
    mul_nonneg hI1.le (sub_nonneg.mpr (diag_bracket hk hki))
  have hfrac : 0 ≤ ((i : ℝ) + 1 - (k : ℝ)) / (i : ℝ) := div_nonneg (by linarith) hI.le
  have t2 : 0 ≤ gam k * (((i : ℝ) + 1 - (k : ℝ)) / (i : ℝ)) *
      (zr k (i - 1) - zr (k - 1) (i - 1)) :=
    mul_nonneg (mul_nonneg (gam_nonneg k) hfrac) (sub_nonneg.mpr hmono)
  have key : ((i : ℝ) + 1) * PowerSeries.coeff (i + 1) (Lser k) =
      (k : ℝ) * PowerSeries.coeff i (Dser k)
        + ((i : ℝ) + 1) * (zr (k + 1) i / ((i : ℝ) + 1) - gam k * (zr k (i - 1) / (i : ℝ)))
        + gam k * (((i : ℝ) + 1 - (k : ℝ)) / (i : ℝ)) * (zr k (i - 1) - zr (k - 1) (i - 1)) := by
    rw [coeff_Lser_succ hk hki, coeff_Dser_pos (k := k) hi1]
    field
  rw [key]
  linarith

private theorem psNonneg_Dser {k : ℕ} (hk : 2 ≤ k) : PSNonneg (Dser k) := by
  have hk1 : 1 ≤ k := by omega
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    rcases Nat.lt_or_ge n (k + 1) with hn | hn
    · exact (coeff_Dser_of_le hk (by omega)).ge
    · obtain ⟨i, rfl⟩ : ∃ i, n = i + 1 := ⟨n - 1, by omega⟩
      have hki : k ≤ i := by omega
      -- the coefficient of `X^(i+1)` in the decomposition of `𝔇 (1 - Ks k)`
      have hc := congrArg (PowerSeries.coeff (i + 1)) (Dser_decomp hk)
      rw [coeff_mul_one_sub_Ks hk1, map_add, map_add] at hc
      have hsum : 0 ≤ ∑ m ∈ Icc 1 (i + 1), kq k m * PowerSeries.coeff (i + 1 - m) (Dser k) :=
        Finset.sum_nonneg fun m hm =>
          mul_nonneg (kq_nonneg hk m) (ih (i + 1 - m) (by have := (Finset.mem_Icc.mp hm).1; omega))
      have hLnn : 0 ≤ PowerSeries.coeff (i + 1) (Lser k) :=
        nonneg_of_mul_nonneg_right
          (le_trans (mul_nonneg (Nat.cast_nonneg k) (ih i (by omega))) (Lser_coeff_ge hk hki))
          (by positivity)
      have hXn := psNonneg_Xp hk1 (i + 1)
      have hYn := (((psNonneg_Y0 hk).X_mul).C_mul (gam_nonneg k)) (i + 1)
      linarith

/-- **The diagonal lower bound** for every row `n ≥ 1`: `γ_k β^{(k-1)}_{n-1} ≤ β^{(k)}_n`. -/
theorem bq_diag_lower {k n : ℕ} (hk : 2 ≤ k) (hn : 1 ≤ n) :
    gam k * bq (k - 1) (n - 1) ≤ bq k n := by
  have h := psNonneg_Dser hk n
  rw [coeff_Dser_pos (k := k) hn] at h
  rw [bq_eq (show 1 ≤ k by omega), bq_eq (show 1 ≤ k - 1 by omega),
    Nat.sub_add_cancel (show 1 ≤ k by omega)]
  linarith

/-- The diagonal lower bound in terms of the step of the column:
`γ_k β^{(k-1)}_{n-1} - β^{(k-1)}_n ≤ δ_n` for every row `n ≥ 1`. -/
theorem dq_diag_lower {k n : ℕ} (hk : 2 ≤ k) (hn : 1 ≤ n) :
    gam k * bq (k - 1) (n - 1) - bq (k - 1) n ≤ dq k n := by
  have h := bq_diag_lower hk hn
  unfold dq
  linarith

end Parking