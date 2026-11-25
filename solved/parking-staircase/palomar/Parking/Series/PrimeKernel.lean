module

public import Parking.Counting.SingleChain

/-!
# The prime kernel of a threshold

For a threshold `y ≥ 1` let `Zs y = ∑ zr y n X^n` be the exponential generating series of the
parking functions all of whose displacements are `< y` (`zr y n = A n (y-1)/n!`).  The last-car
recursion is `Zs' = Gp Zs` (`deriv_Zs`), where `[X^j] Gp y = min (j+1) y * zr y j`.

* `Ks y = 1 - 1/Zs y`, with coefficients `kq y m`: the prime kernel of the threshold `y`.
  (Combinatorially it counts the parking functions that cannot be cut into two, but only the
  algebraic definition is used.)  It satisfies `Ks' = (1 - Ks) Gp` (`deriv_Ks`).
* `kq_eq_eps` : `kq y m = ε_m` for `1 ≤ m ≤ y`: up to the threshold, the prime kernel is the free
  prime kernel `eps` of the Cayley coefficients.
* `kq_rec` : `N kq y N = ∑_{γ=1}^{y-1} (y-γ) a_γ kq y (N-γ)` for `N ≥ y ≥ 2`.  This is the
  coefficient form of `Ks' = y - (1 - Ks) Hs`, where `Hs y = ∑ (y-1-j)⁺ c_j X^j` and
  `Gp y = y Zs y - Hs y`.  The right-hand side is written with the convolution
  `rconv g v N = ∑_{γ=1}^{N} g γ * v (N - γ)` and the weights `kqW y γ = (y-γ)⁺ a_γ`.
-/

@[expose] public section

namespace Parking

open Finset TreeSeries SingleChain

local notation "Dx" => PowerSeries.derivative (R := ℝ)

/-- `rconv g v N = ∑_{γ=1}^{N} g γ * v (N - γ)`.  The sum is taken over `j = γ - 1`. -/
def rconv (g v : ℕ → ℝ) (N : ℕ) : ℝ := ∑ j ∈ range N, g (j + 1) * v (N - 1 - j)

/-! ### The series of a threshold and its prime kernel -/

/-- `Zs y = ∑ zr y n X^n`. -/
noncomputable def Zs (y : ℕ) : PowerSeries ℝ := PowerSeries.mk (zr y)

/-- `Ks y = 1 - 1/Zs y`. -/
noncomputable def Ks (y : ℕ) : PowerSeries ℝ := 1 - (Zs y)⁻¹

/-- `kq y m = [X^m] (1 - 1/Zs y)`. -/
noncomputable def kq (y m : ℕ) : ℝ := PowerSeries.coeff m (Ks y)

/-- The weights `(y - γ)⁺ a_γ` of the recursion `kq_rec`. -/
noncomputable def kqW (y γ : ℕ) : ℝ := ((y - γ : ℕ) : ℝ) * cay γ

/-- The coefficient of $X^n$ in the series $Z_y$ of a threshold $y$ is $z^{(y)}_n = A(n,y-1)/n!$. -/
theorem coeff_Zs (y n : ℕ) : PowerSeries.coeff n (Zs y) = zr y n :=
  PowerSeries.coeff_mk n (zr y)

/-- For a threshold $y \ge 1$, $z^{(y)}_0 = 1$, where $z^{(y)}_n = A(n,y-1)/n!$. -/
theorem zr_zero {y : ℕ} (hy : 1 ≤ y) : zr y 0 = 1 :=
  (zr_isWSol hy).zero

private theorem constantCoeff_Zs {y : ℕ} (hy : 1 ≤ y) : PowerSeries.constantCoeff (Zs y) = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff_apply, coeff_Zs, zr_zero hy]

/-- `1/Zs y = 1 - Ks y`. -/
theorem inv_Zs (y : ℕ) : (Zs y)⁻¹ = 1 - Ks y := by
  rw [Ks, sub_sub_cancel]

/-- For a threshold $y \ge 1$, $Z_y\,(1 - K_y) = 1$: the series of the threshold and one minus its
prime kernel series are inverse to each other. -/
theorem Zs_mul_one_sub_Ks {y : ℕ} (hy : 1 ≤ y) : Zs y * (1 - Ks y) = 1 := by
  rw [Ks, sub_sub_cancel]
  exact PowerSeries.mul_inv_cancel (Zs y) (by rw [constantCoeff_Zs hy]; exact one_ne_zero)

private theorem one_sub_Ks_mul_Zs {y : ℕ} (hy : 1 ≤ y) : (1 - Ks y) * Zs y = 1 :=
  (mul_comm (1 - Ks y) (Zs y)).trans (Zs_mul_one_sub_Ks hy)

/-- For a threshold $y \ge 1$, the prime kernel vanishes at the index $0$: $\kappa^{(y)}_0 = 0$. -/
theorem kq_zero {y : ℕ} (hy : 1 ≤ y) : kq y 0 = 0 := by
  rw [kq, PowerSeries.coeff_zero_eq_constantCoeff_apply, Ks, map_sub,
    PowerSeries.constantCoeff_inv, constantCoeff_Zs hy, PowerSeries.constantCoeff_one, inv_one,
    sub_self]

/-- For a threshold $y \ge 1$, the constant coefficient of $1 - K_y$ is $1$. -/
theorem coeff_one_sub_Ks_zero {y : ℕ} (hy : 1 ≤ y) : PowerSeries.coeff 0 (1 - Ks y) = 1 := by
  rw [map_sub, PowerSeries.coeff_zero_one, show PowerSeries.coeff 0 (Ks y) = kq y 0 from rfl,
    kq_zero hy, sub_zero]

/-- For $m \ge 1$, the coefficient of $X^m$ in $1 - K_y$ is $-\kappa^{(y)}_m$, the negative of the
prime kernel of the threshold $y$. -/
theorem coeff_one_sub_Ks_of_pos (y : ℕ) {m : ℕ} (hm : 1 ≤ m) :
    PowerSeries.coeff m (1 - Ks y) = -kq y m := by
  rw [kq, map_sub, PowerSeries.coeff_one, ite_eq_right (show ¬ m = 0 by omega), zero_sub]

/-- Renewal equation between `zr y` and `kq y`: the coefficients of `(1 - Ks) Zs = 1`. -/
private theorem zr_renewal {y n : ℕ} (hy : 1 ≤ y) (hn : 1 ≤ n) :
    zr y n = ∑ m ∈ Icc 1 n, kq y m * zr y (n - m) := by
  have h := congrArg (PowerSeries.coeff n) (one_sub_Ks_mul_Zs hy)
  rw [coeff_mul_split, coeff_one_sub_Ks_zero hy, one_mul, coeff_Zs, PowerSeries.coeff_one,
    ite_eq_right (show ¬ n = 0 by omega)] at h
  have hsum : ∑ m ∈ Icc 1 n, PowerSeries.coeff m (1 - Ks y) * PowerSeries.coeff (n - m) (Zs y) =
      -∑ m ∈ Icc 1 n, kq y m * zr y (n - m) := by
    rw [← Finset.sum_neg_distrib]
    refine sum_congr rfl fun m hm => ?_
    rw [mem_Icc] at hm
    rw [coeff_one_sub_Ks_of_pos y hm.1, coeff_Zs]
    ring
  rw [hsum] at h
  linarith

/-- In the free range the prime kernel is `ε`: there `zr y = cc`, and `ε` is the kernel of the
renewal equation of `cc` (`eps_conv`). -/
theorem kq_eq_eps {y m : ℕ} (hy : 1 ≤ y) (hm1 : 1 ≤ m) (hm : m ≤ y) : kq y m = eps m := by
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    have h1 : cc m = ∑ i ∈ Icc 1 m, kq y i * zr y (m - i) := by
      rw [← zr_eq_cc hy hm]
      exact zr_renewal hy hm1
    have h2 : ∑ i ∈ Icc 1 m, eps i * cc (m - i) = cc m := eps_conv hm1
    have e : ∑ i ∈ Icc 1 m, (kq y i - eps i) * cc (m - i) =
        ∑ i ∈ Icc 1 m, kq y i * zr y (m - i) - ∑ i ∈ Icc 1 m, eps i * cc (m - i) := by
      rw [← Finset.sum_sub_distrib]
      refine sum_congr rfl fun i hi => ?_
      rw [mem_Icc] at hi
      rw [zr_eq_cc hy (show m - i ≤ y by omega)]
      ring
    have hsingle : ∑ i ∈ Icc 1 m, (kq y i - eps i) * cc (m - i) = kq y m - eps m := by
      have hs : ∑ i ∈ Icc 1 m, (kq y i - eps i) * cc (m - i) =
          (kq y m - eps m) * cc (m - m) := by
        refine Finset.sum_eq_single m (fun i hi hne => ?_) (fun hnot => ?_)
        · rw [mem_Icc] at hi
          have hi' : kq y i = eps i := ih i (by omega) hi.1 (by omega)
          show (kq y i - eps i) * cc (m - i) = 0
          rw [hi', sub_self, zero_mul]
        · exact absurd (mem_Icc.mpr ⟨hm1, le_rfl⟩) hnot
      rw [hs, Nat.sub_self, cc_zero, mul_one]
    linarith

/-! ### The derivative of `Ks` -/

/-- `Gp y = G'`, where `G` is the series of the last-car recursion with threshold `y`;
`[X^j] Gp y = min (j+1) y * zr y j`. -/
noncomputable def Gp (y : ℕ) : PowerSeries ℝ :=
  Dx (SingleChain.Gser (fun t => ((min t y : ℕ) : ℝ)) (zr y))

/-- The last-car recursion: `Zs' = Gp Zs`. -/
theorem deriv_Zs {y : ℕ} (hy : 1 ≤ y) : Dx (Zs y) = Gp y * Zs y :=
  SingleChain.deriv_mk (zr_isWSol hy)

/-- The coefficient of $X^j$ in the series $\Gamma_y'$ of a threshold $y$ is $\min(j+1,y)\,
z^{(y)}_j$. -/
theorem coeff_Gp (y j : ℕ) :
    PowerSeries.coeff j (Gp y) = ((min (j + 1) y : ℕ) : ℝ) * zr y j := by
  have hj : ((j : ℝ) + 1) ≠ 0 := by positivity
  rw [Gp, PowerSeries.coeff_derivative, SingleChain.Gser, PowerSeries.coeff_mk,
    ite_eq_right (show ¬ (j + 1 = 0) by omega), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]
  field

/-- `Hs y = ∑_j (y - 1 - j)⁺ c_j X^j`. -/
private noncomputable def Hs (y : ℕ) : PowerSeries ℝ :=
  PowerSeries.mk fun j => ((y - 1 - j : ℕ) : ℝ) * cc j

private theorem coeff_Hs (y j : ℕ) : PowerSeries.coeff j (Hs y) = ((y - 1 - j : ℕ) : ℝ) * cc j :=
  PowerSeries.coeff_mk j (fun j => ((y - 1 - j : ℕ) : ℝ) * cc j)

/-- `Gp y = y Zs y - Hs y`. -/
private theorem Gp_eq {y : ℕ} (hy : 1 ≤ y) : Gp y = PowerSeries.C (y : ℝ) * Zs y - Hs y := by
  refine PowerSeries.ext fun j => ?_
  rw [coeff_Gp, map_sub, PowerSeries.coeff_C_mul, coeff_Zs, coeff_Hs]
  by_cases hj : j + 1 ≤ y
  · have h1 : min (j + 1) y = j + 1 := min_eq_left hj
    have h2 : ((y - 1 - j : ℕ) : ℝ) = (y : ℝ) - 1 - (j : ℝ) := by
      rw [Nat.cast_sub (show j ≤ y - 1 by omega), Nat.cast_sub hy, Nat.cast_one]
    rw [h1, h2, zr_eq_cc hy (show j ≤ y by omega), Nat.cast_add, Nat.cast_one]
    ring
  · have h1 : min (j + 1) y = y := min_eq_right (by omega)
    have h2 : ((y - 1 - j : ℕ) : ℝ) = 0 := by
      rw [show y - 1 - j = 0 by omega, Nat.cast_zero]
    rw [h1, h2]
    ring

/-- `Ks' = (1 - Ks) Gp`. -/
theorem deriv_Ks {y : ℕ} (hy : 1 ≤ y) : Dx (Ks y) = (1 - Ks y) * Gp y := by
  have h1 := deriv_Zs hy
  have h2 := Zs_mul_one_sub_Ks hy
  have h3 : Dx (Zs y * (1 - Ks y)) = Zs y * Dx (1 - Ks y) + (1 - Ks y) * Dx (Zs y) := by
    rw [Derivation.leibniz, smul_eq_mul, smul_eq_mul]
  have h4 : Dx (1 - Ks y) = -Dx (Ks y) := by
    rw [map_sub, Derivation.map_one_eq_zero, zero_sub]
  have h5 : Dx (Zs y * (1 - Ks y)) = 0 := by
    rw [h2, Derivation.map_one_eq_zero]
  linear_combination (1 - Ks y) * h3 - (1 - Ks y) * h5 + (1 - Ks y) * Zs y * h4 +
    (1 - Ks y) * (1 - Ks y) * h1 - (Dx (Ks y) - (1 - Ks y) * Gp y) * h2

/-- `Ks' = y - (1 - Ks) Hs`. -/
private theorem deriv_Ks_eq {y : ℕ} (hy : 1 ≤ y) :
    Dx (Ks y) = PowerSeries.C (y : ℝ) - (1 - Ks y) * Hs y := by
  have h1 := deriv_Ks hy
  have h2 := Zs_mul_one_sub_Ks hy
  have h3 := Gp_eq hy
  linear_combination h1 + (1 - Ks y) * h3 + PowerSeries.C (y : ℝ) * h2

/-- The prime kernel recursion `N kq y N = ∑_{γ=1}^{y-1} (y-γ) a_γ kq y (N-γ)` for `N ≥ y ≥ 2`:
the coefficients of `Ks' = y - (1 - Ks) Hs`. -/
theorem kq_rec {y N : ℕ} (hy : 2 ≤ y) (hN : y ≤ N) :
    (N : ℝ) * kq y N = rconv (kqW y) (kq y) N := by
  have hy1 : 1 ≤ y := by omega
  obtain ⟨n, rfl⟩ : ∃ n, N = n + 1 := ⟨N - 1, by omega⟩
  have hn : ¬ n = 0 := by omega
  have hsum : ∑ j ∈ range (n + 1),
      PowerSeries.coeff j (Hs y) * PowerSeries.coeff (n - j) (1 - Ks y) =
      -rconv (kqW y) (kq y) (n + 1) := by
    rw [rconv, ← Finset.sum_neg_distrib]
    refine sum_congr rfl fun j hj => ?_
    rw [mem_range] at hj
    rw [coeff_Hs, kqW]
    by_cases hjn : j = n
    · have e0 : ((y - 1 - j : ℕ) : ℝ) = 0 := by
        rw [show y - 1 - j = 0 by omega, Nat.cast_zero]
      have e1 : ((y - (j + 1) : ℕ) : ℝ) = 0 := by
        rw [show y - (j + 1) = 0 by omega, Nat.cast_zero]
      rw [e0, e1]
      ring
    · have hpos : 1 ≤ n - j := by omega
      have e0 : y - 1 - j = y - (j + 1) := by omega
      have e2 : n + 1 - 1 - j = n - j := by omega
      rw [coeff_one_sub_Ks_of_pos y hpos, e0, e2, cc]
      ring
  have h := congrArg (PowerSeries.coeff n) (deriv_Ks_eq hy1)
  rw [PowerSeries.coeff_derivative, map_sub, PowerSeries.coeff_C, ite_eq_right hn, zero_sub,
    mul_comm (1 - Ks y) (Hs y), coeff_mul_range, hsum, neg_neg] at h
  have hk : kq y (n + 1) = PowerSeries.coeff (n + 1) (Ks y) := rfl
  rw [hk, Nat.cast_add, Nat.cast_one]
  linear_combination h

end Parking
