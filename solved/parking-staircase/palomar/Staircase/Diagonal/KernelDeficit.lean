module

public import Parking.Basic.RealBounds
public import Parking.Cayley.BorelSum
public import Parking.Crossing.Bounds
public import Parking.NextColumn.Frozen
public import Staircase.Cayley.BorelRatio
public import Batteries.Tactic.OpenPrivate
import all Parking.Crossing.Bounds

/-!
# The kernel deficit along the diagonal

The kernel deficit is `κ_k(t) = a_t - ∑_{k<i<t} a_i a_{t-i}` (`kap k t`), with the Cayley
coefficients `a_j = j^{j-1}/j!` (`cay j`).  The diagonal step passes from `κ_k(k+a)` to
`κ_{k+1}(k+a+1)`.  This module proves that the normalised deficit `κ_k(t)/a_t` grows on that step
by at most the factor `1 + T/k`, where `T` is a closed form in `ξ = a/k` and `k`
(`kapStepBound`, `kap_diag_le`).

Write `M = k + a`.  Reflecting the sum gives `κ_k(M)/a_M = 1 - ∑_{0<j<a} a_j a_{M-j}/a_M`, and the
deficit of the successor is the same sum with `M + 1` in the place of `M`.  The proof has three
parts.

* **Two comparisons of Cayley coefficients.**  The Borel mass is `e^{-j} a_j = p_j/j`, where
  `p_j = e^{-j} j^j/j!` is the Poisson mass (`poissonMass j`).  The bound `borel_ratio_le` for the
  ratio of two Borel masses gives `a_j a_i/a_{i+j} ≤ (p_j/j)(1 + (3/2)z + (3/8)z²)` with `z = j/i`.
  The ratio of successive coefficients is `a_{n+1}/a_n = (1+1/n)^{n-1} = γ_n (1+1/n)`, with
  `γ_n = (1+1/n)^{n-2}` (`gam n`), and `log γ` increases slowly:
  `log γ_i - log γ_k ≤ (5/2)(1/k - 1/i)` (`log_gam_sub_le`).  Hence
  `a_i/a_{i+j} - a_{i+1}/a_{i+j+1} ≤ (a_i/a_{i+j}) · (j/(i+j)) (3/(2i) + 1/(i(i+1)))`.
* **Two bounds by the Poisson masses.**  With `S = ∑_{0<j<a} p_j` and the Borel tail
  `B = 1 - ∑_{0<j<a} p_j/j`, summing the first comparison over `j` gives
  `κ_k(M)/a_M ≥ B - (3/2)(1 + ξ/4) · S/(k+1)`, and summing the product of the two gives
  `κ_{k+1}(M+1)/a_{M+1} - κ_k(M)/a_M
    ≤ (1 + (3/2)ξ + (3/8)ξ²) · (3/2)(1 + 2/(3(k+2))) · S/((k+a)(k+1))`.
* **The sum of the masses against the Borel tail.**  Stirling's bounds for `p_j` give
  `S ≤ c₀(2√(a-1) - 1)` and, because the Borel masses sum to `1`, `B ≥ 2c₀(1 - 1/(12a))/√a`, with
  `c₀ = 1/√(2π)`.  Together, `(23/24) S ≤ a B`.

The three combine as follows.  The lower bound and `(23/24) S ≤ a B` give
`(23/24 - (3/2)ξ(1 + ξ/4)) · S/(k+1) ≤ ξ · κ_k(M)/a_M`, which turns the upper bound for the
increase into a multiple of `κ_k(M)/a_M` itself.  The first factor is the denominator of `T`; it
is positive for `ξ ≤ 1/2`.
-/

@[expose] public section

namespace Parking

open Finset

open private log_xk_gam_le sum_poissonMass_le from Parking.Crossing.Bounds

/-! ### The increase of `log γ` -/

/-- The factor `γ_n = (1+1/n)^{n-2}` increases slowly:
`log γ_i - log γ_k ≤ (5/2)(1/k - 1/i)` for `2 ≤ k ≤ i`.  Each step from `m` to `m + 1` contributes
at most `(5/2)(1/m - 1/(m+1))`, by Taylor bounds for the logarithm, and the steps telescope.  This
is `log_xk_gam_le`, a private lemma of `Parking.Crossing.Bounds`, which states the bound for
`log (γ_i/γ_k)` with `1/γ_k` written as `xk k`. -/
theorem log_gam_sub_le {k i : ℕ} (hk : 2 ≤ k) (hi : k ≤ i) :
    Real.log (gam i) - Real.log (gam k) ≤ 5 / 2 * (1 / (k : ℝ) - 1 / (i : ℝ)) := by
  have hk0 : (0 : ℝ) < k := by exact_mod_cast (by omega : 0 < k)
  have hi0 : (0 : ℝ) < i := by exact_mod_cast (by omega : 0 < i)
  have h := log_xk_gam_le hk hi
  unfold xk at h
  rw [Real.log_mul (inv_ne_zero (gam_pos k).ne') (gam_pos i).ne', Real.log_inv] at h
  have e : 5 * ((i : ℝ) - k) / (2 * (k : ℝ) * i) = 5 / 2 * (1 / (k : ℝ) - 1 / (i : ℝ)) := by
    field
  linarith

/-! ### Two comparisons of Cayley coefficients -/

/-- The Borel mass `e^{-j} a_j` is the Poisson mass `e^{-j} j^j/j!` divided by `j`. -/
private theorem exp_neg_mul_cay {j : ℕ} (hj : 1 ≤ j) :
    Real.exp (-(j : ℝ)) * cay j = poissonMass j / j := by
  obtain ⟨i, rfl⟩ : ∃ i, j = i + 1 := ⟨j - 1, by omega⟩
  rw [poissonMass, ren, cay_succ, Nat.factorial_succ, pow_succ]
  push_cast
  field

/-- The weight of a term of the convolution: `a_j a_i/a_{i+j} ≤ (p_j/j)(1 + (3/2)z + (3/8)z²)`,
`z = j/i`.  The left side is the Borel mass `e^{-j} a_j` times the ratio of the Borel masses of `i`
and `i + j`, which `borel_ratio_le` bounds. -/
private theorem conv_weight_le {i j : ℕ} (hi : 1 ≤ i) (hj : 1 ≤ j) :
    cay j * cay i / cay (i + j)
      ≤ poissonMass j / j * (1 + 3 / 2 * ((j : ℝ) / i) + 3 / 8 * ((j : ℝ) / i) ^ 2) := by
  have h := borel_ratio_le hi (Nat.le_add_right i j)
  rw [Nat.cast_add, add_sub_cancel_left] at h
  have hP : 0 ≤ poissonMass j / j := div_nonneg (poissonMass_pos j).le (Nat.cast_nonneg j)
  calc cay j * cay i / cay (i + j)
      = Real.exp (-(j : ℝ)) * Real.exp (j : ℝ) * (cay j * cay i / cay (i + j)) := by
        rw [← Real.exp_add, neg_add_cancel, Real.exp_zero, one_mul]
    _ = poissonMass j / j * (Real.exp (j : ℝ) * cay i / cay (i + j)) := by
        rw [← exp_neg_mul_cay hj]
        ring
    _ ≤ poissonMass j / j * (1 + 3 / 2 * ((j : ℝ) / i) + 3 / 8 * ((j : ℝ) / i) ^ 2) := by
        gcongr

/-- Raising both indices by one lowers the ratio `a_i/a_{i+j}` by little: for `i ≥ 2`,
`a_i/a_{i+j} - a_{i+1}/a_{i+j+1} ≤ (a_i/a_{i+j}) · (j/(i+j)) (3/(2i) + 1/(i(i+1)))`.
With `ψ_n = a_{n+1}/a_n = (1+1/n)^{n-1}` the left side is `(a_i/a_{i+j})(1 - ψ_i/ψ_{i+j})`, and
`1 - ψ_i/ψ_{i+j} ≤ log ψ_{i+j} - log ψ_i`.  As `ψ_n = γ_n (1+1/n)`, the difference of the logarithms
is at most `(5/2)(1/i - 1/(i+j))`, by `log_gam_sub_le`, plus `(1+1/(i+j))/(1+1/i) - 1`. -/
private theorem cay_div_succ_sub_le {i : ℕ} (j : ℕ) (hi : 2 ≤ i) :
    cay i / cay (i + j) - cay (i + 1) / cay (i + j + 1)
      ≤ cay i / cay (i + j)
          * ((j : ℝ) / ((i : ℝ) + j) * (3 / (2 * (i : ℝ)) + 1 / ((i : ℝ) * ((i : ℝ) + 1)))) := by
  have hi0 : (0 : ℝ) < i := by exact_mod_cast (by omega : 0 < i)
  have hc : 0 ≤ cay i / cay (i + j) := div_nonneg (cay_nonneg _) (cay_nonneg _)
  set ψ : ℕ → ℝ := fun n => (1 + 1 / (n : ℝ)) ^ (n - 1)
  have hpos : ∀ n, 0 < ψ n := fun n => by positivity
  have hlog : ∀ n, 2 ≤ n → Real.log (ψ n) = Real.log (gam n) + Real.log (1 + 1 / (n : ℝ)) :=
    fun n hn => by
      show Real.log ((1 + 1 / (n : ℝ)) ^ (n - 1)) = _
      rw [psi_eq_gam hn, Real.log_mul (gam_pos n).ne' (by positivity)]
  have hquot : cay (i + 1) / cay (i + j + 1) = cay i / cay (i + j) * (ψ i / ψ (i + j)) := by
    rw [cay_ratio (by omega : 0 < i), cay_ratio (by omega : 0 < i + j), mul_div_mul_comm, mul_comm]
  have h1 := Real.one_sub_inv_le_log_of_pos (div_pos (hpos (i + j)) (hpos i))
  rw [inv_div, Real.log_div (hpos _).ne' (hpos _).ne', hlog i hi, hlog (i + j) (by omega)] at h1
  have h2 := log_gam_sub_le hi (Nat.le_add_right i j)
  have h3 := Real.log_le_sub_one_of_pos (div_pos
    (by positivity : (0 : ℝ) < 1 + 1 / ((i + j : ℕ) : ℝ))
    (by positivity : (0 : ℝ) < 1 + 1 / (i : ℝ)))
  rw [Real.log_div (by positivity) (by positivity)] at h3
  rw [hquot, ← mul_one_sub]
  gcongr
  push_cast at h1 h2 h3
  calc 1 - ψ i / ψ (i + j)
      ≤ 5 / 2 * (1 / (i : ℝ) - 1 / ((i : ℝ) + j))
          + ((1 + 1 / ((i : ℝ) + j)) / (1 + 1 / (i : ℝ)) - 1) := by
        linarith
    _ = (j : ℝ) / ((i : ℝ) + j) * (3 / (2 * (i : ℝ)) + 1 / ((i : ℝ) * ((i : ℝ) + 1))) := by
        field

/-! ### The normalised deficit as a sum, and its two bounds -/

/-- The normalised deficit as a sum over the short side: for `t = k + a`,
`κ_k(t)/a_t = 1 - ∑_{0<j<a} a_j a_{t-j}/a_t`, by the reflection `i ↦ t - i` of the sum over
`k < i < t`. -/
private theorem kap_div_cay {k t a : ℕ} (ht : t = k + a) (ht0 : 0 < t) :
    kap k t / cay t = 1 - ∑ j ∈ Ico 1 a, cay j * cay (t - j) / cay t := by
  have hrefl : ∑ i ∈ Ioo k t, cay i * cay (t - i) = ∑ j ∈ Ico 1 a, cay j * cay (t - j) := by
    have h := sum_Ico_reflect (fun i => cay i * cay (t - i)) 1 (m := a) (n := t) (by omega)
    rw [show t + 1 - a = k + 1 by omega, Nat.add_sub_cancel, Ico_add_one_left_eq_Ioo] at h
    rw [← h]
    refine sum_congr rfl fun j hj => ?_
    rw [show t - (t - j) = j by have := mem_Ico.mp hj; omega, mul_comm]
  rw [kap, hrefl, sub_div, div_self (cay_pos ht0).ne', sum_div]

/-- A lower bound for the normalised deficit, with `ξ = a/k`:
`κ_k(k+a)/a_{k+a} ≥ 1 - ∑_{0<j<a} p_j/j - (3/2)(1 + ξ/4)/(k+1) · ∑_{0<j<a} p_j`.
Each term of the sum is bounded by `conv_weight_le` with `z = j/(k+a-j)`, where `z ≤ ξ` and
`z ≤ j/(k+1)`. -/
private theorem kap_div_cay_ge {k a : ℕ} (hk : 1 ≤ k) :
    1 - ∑ j ∈ Ico 1 a, poissonMass j / j
        - 3 / 2 * (1 + (a : ℝ) / k / 4) / ((k : ℝ) + 1) * ∑ j ∈ Ico 1 a, poissonMass j
      ≤ kap k (k + a) / cay (k + a) := by
  have hk0 : (0 : ℝ) < k := by exact_mod_cast hk
  have hterm : ∀ j ∈ Ico 1 a, cay j * cay (k + a - j) / cay (k + a)
      ≤ poissonMass j / j + 3 / 2 * (1 + (a : ℝ) / k / 4) / ((k : ℝ) + 1) * poissonMass j := by
    intro j hj
    obtain ⟨hj1, hja⟩ := mem_Ico.mp hj
    obtain ⟨i, hi⟩ : ∃ i, k + a = i + j := ⟨k + a - j, by omega⟩
    have hik : (k : ℝ) + 1 ≤ i := by exact_mod_cast (by omega : k + 1 ≤ i)
    have hja' : (j : ℝ) ≤ a := by exact_mod_cast hja.le
    have hj0 : (0 : ℝ) < j := by exact_mod_cast hj1
    have hP := (poissonMass_pos j).le
    rw [hi, Nat.add_sub_cancel]
    calc cay j * cay i / cay (i + j)
        ≤ poissonMass j / j * (1 + 3 / 2 * ((j : ℝ) / i) + 3 / 8 * ((j : ℝ) / i) ^ 2) :=
          conv_weight_le (by omega) hj1
      _ = poissonMass j / j * (1 + 3 / 2 * (1 + (j : ℝ) / i / 4) * ((j : ℝ) / i)) := by ring
      _ ≤ poissonMass j / j
            * (1 + 3 / 2 * (1 + (a : ℝ) / k / 4) * ((j : ℝ) / ((k : ℝ) + 1))) := by
          gcongr
          linarith
      _ = poissonMass j / j
            + 3 / 2 * (1 + (a : ℝ) / k / 4) / ((k : ℝ) + 1) * poissonMass j := by
          field
  have h := sum_le_sum hterm
  rw [sum_add_distrib, ← mul_sum] at h
  rw [kap_div_cay rfl (by omega)]
  linarith

/-- An upper bound for the increase of the normalised deficit on a diagonal step, with `ξ = a/k`:
`κ_{k+1}(k+a+1)/a_{k+a+1} - κ_k(k+a)/a_{k+a}
  ≤ (1 + (3/2)ξ + (3/8)ξ²) · (3/2)(1 + 2/(3(k+2)))/((k+a)(k+1)) · ∑_{0<j<a} p_j`.
The increase is `∑_{0<j<a} a_j (a_i/a_{i+j} - a_{i+1}/a_{i+j+1})` with `i = k + a - j ≥ k + 1`;
each term is bounded by `cay_div_succ_sub_le` and then by `conv_weight_le`. -/
private theorem kap_div_cay_succ_sub_le {k a : ℕ} (hk : 1 ≤ k) :
    kap (k + 1) (k + a + 1) / cay (k + a + 1) - kap k (k + a) / cay (k + a)
      ≤ (1 + 3 / 2 * ((a : ℝ) / k) + 3 / 8 * ((a : ℝ) / k) ^ 2)
          * (3 / 2 * (1 + 2 / (3 * ((k : ℝ) + 2))) / (((k : ℝ) + a) * ((k : ℝ) + 1)))
          * ∑ j ∈ Ico 1 a, poissonMass j := by
  have hk0 : (0 : ℝ) < k := by exact_mod_cast hk
  rw [kap_div_cay (k := k + 1) (a := a) (by omega) (by omega), kap_div_cay (k := k) rfl (by omega),
    sub_sub_sub_cancel_left, ← sum_sub_distrib, mul_sum]
  refine sum_le_sum fun j hj => ?_
  obtain ⟨hj1, hja⟩ := mem_Ico.mp hj
  obtain ⟨i, hi⟩ : ∃ i, k + a = i + j := ⟨k + a - j, by omega⟩
  have hik : (k : ℝ) + 1 ≤ i := by exact_mod_cast (by omega : k + 1 ≤ i)
  have hja' : (j : ℝ) ≤ a := by exact_mod_cast hja.le
  have hj0 : (0 : ℝ) < j := by exact_mod_cast hj1
  have hij : (i : ℝ) + j = k + a := by exact_mod_cast hi.symm
  have hP := (poissonMass_pos j).le
  have hc := cay_nonneg j
  rw [hi, Nat.add_sub_cancel, show i + j + 1 - j = i + 1 by omega]
  calc cay j * cay i / cay (i + j) - cay j * cay (i + 1) / cay (i + j + 1)
      = cay j * (cay i / cay (i + j) - cay (i + 1) / cay (i + j + 1)) := by ring
    _ ≤ cay j * (cay i / cay (i + j)
          * ((j : ℝ) / ((i : ℝ) + j) * (3 / (2 * (i : ℝ)) + 1 / ((i : ℝ) * ((i : ℝ) + 1))))) := by
        gcongr
        exact cay_div_succ_sub_le j (by omega)
    _ = cay j * cay i / cay (i + j)
          * ((j : ℝ) / ((i : ℝ) + j) * (3 / (2 * (i : ℝ)) + 1 / ((i : ℝ) * ((i : ℝ) + 1)))) := by
        ring
    _ ≤ poissonMass j / j * (1 + 3 / 2 * ((j : ℝ) / i) + 3 / 8 * ((j : ℝ) / i) ^ 2)
          * ((j : ℝ) / ((i : ℝ) + j) * (3 / (2 * (i : ℝ)) + 1 / ((i : ℝ) * ((i : ℝ) + 1)))) := by
        gcongr
        exact conv_weight_le (by omega) hj1
    _ ≤ poissonMass j / j * (1 + 3 / 2 * ((a : ℝ) / k) + 3 / 8 * ((a : ℝ) / k) ^ 2)
          * ((j : ℝ) / ((k : ℝ) + a)
            * (3 / (2 * ((k : ℝ) + 1)) + 1 / (((k : ℝ) + 1) * ((k : ℝ) + 1 + 1)))) := by
        rw [hij]
        gcongr <;> linarith
    _ = (1 + 3 / 2 * ((a : ℝ) / k) + 3 / 8 * ((a : ℝ) / k) ^ 2)
          * (3 / 2 * (1 + 2 / (3 * ((k : ℝ) + 2))) / (((k : ℝ) + a) * ((k : ℝ) + 1)))
          * poissonMass j := by
        field

/-! ### The sum of the Poisson masses against the Borel tail -/

/-- The tail of the Borel law: `1 - ∑_{0<j<a} p_j/j ≥ 2c₀(1 - 1/(12a))/√a` for `a ≥ 1`.  For
`n ≥ a` the mass `p_n/n` is at least `c₀(1 - 1/(12a)) n^{-3/2}`, by Stirling's lower bound, and
`n^{-3/2} ≥ 2(1/√n - 1/√(n+1))`.  The differences telescope, so that every partial sum of the
Borel masses beyond `a` is at least `2c₀(1 - 1/(12a))(1/√a - 1/√N)` above the partial sum up to
`a`; it is also at most `1`, the sum of all Borel masses.  Letting `N` tend to infinity gives the
bound. -/
private theorem borel_tail_ge {a : ℕ} (ha : 1 ≤ a) :
    2 * c0 * (1 - 1 / (12 * (a : ℝ))) / Real.sqrt (a : ℝ)
      ≤ 1 - ∑ j ∈ Ico 1 a, poissonMass j / j := by
  have hc0 := c0_pos
  have ha1 : (1 : ℝ) ≤ a := by exact_mod_cast ha
  have hcor : 0 ≤ c0 * (1 - 1 / (12 * (a : ℝ))) := by
    have : 1 / (12 * (a : ℝ)) ≤ 1 := by
      rw [div_le_one (by positivity)]
      linarith
    exact mul_nonneg hc0.le (by linarith)
  set C : ℝ := 2 * c0 * (1 - 1 / (12 * (a : ℝ))) with hC
  -- from `a` on, each Borel mass is at least a difference of the values `C/√n`
  have hstep : ∀ n : ℕ, a ≤ n →
      C / Real.sqrt (n : ℝ) - C / Real.sqrt ((n : ℝ) + 1) ≤ poissonMass n / n := by
    intro n hn
    have han : (a : ℝ) ≤ n := by exact_mod_cast hn
    have hn0 : (0 : ℝ) < n := by linarith
    have hs : 0 < Real.sqrt (n : ℝ) := Real.sqrt_pos.2 hn0
    have hmass : c0 * (1 - 1 / (12 * (a : ℝ))) / Real.sqrt (n : ℝ) ≤ poissonMass n :=
      le_trans (by gcongr) (poissonMass_ge_c0 (by omega : 1 ≤ n))
    calc C / Real.sqrt (n : ℝ) - C / Real.sqrt ((n : ℝ) + 1)
        = c0 * (1 - 1 / (12 * (a : ℝ)))
            * (2 * (1 / Real.sqrt (n : ℝ) - 1 / Real.sqrt ((n : ℝ) + 1))) := by
          rw [hC]
          ring
      _ ≤ c0 * (1 - 1 / (12 * (a : ℝ))) * (1 / ((n : ℝ) * Real.sqrt (n : ℝ))) :=
          mul_le_mul_of_nonneg_left (inv_sqrt_diff_bounds hn0).2 hcor
      _ = c0 * (1 - 1 / (12 * (a : ℝ))) / Real.sqrt (n : ℝ) / n := by field
      _ ≤ poissonMass n / n := by gcongr
  -- the differences telescope
  have hpart : ∀ N : ℕ, a ≤ N →
      ∑ j ∈ Ico 1 a, poissonMass j / j + (C / Real.sqrt (a : ℝ) - C / Real.sqrt (N : ℝ))
        ≤ ∑ j ∈ Ico 1 N, poissonMass j / j := by
    intro N hN
    induction N, hN using Nat.le_induction with
    | base => simp
    | succ n hn ih =>
      have h := hstep n hn
      rw [sum_Ico_succ_top (by omega : 1 ≤ n), Nat.cast_add_one]
      linarith
  -- every partial sum of the Borel masses is at most their sum `1`
  have hle : ∀ N : ℕ, ∑ j ∈ Ico 1 N, poissonMass j / j ≤ 1 := by
    intro N
    rw [← sum_congr rfl fun j hj => exp_neg_mul_cay (mem_Ico.mp hj).1]
    exact sum_le_hasSum _ (fun j _ => mul_nonneg (Real.exp_pos _).le (cay_nonneg j)) hasSum_borel
  -- let `N` tend to infinity
  have hlim : Filter.Tendsto
      (fun N : ℕ => ∑ j ∈ Ico 1 a, poissonMass j / j
        + (C / Real.sqrt (a : ℝ) - C / Real.sqrt (N : ℝ)))
      Filter.atTop (nhds (∑ j ∈ Ico 1 a, poissonMass j / j + (C / Real.sqrt (a : ℝ) - 0))) :=
    tendsto_const_nhds.add (tendsto_const_nhds.sub
      (tendsto_const_nhds.div_atTop (Real.tendsto_sqrt_atTop.comp tendsto_natCast_atTop_atTop)))
  have h := le_of_tendsto hlim
    (Filter.eventually_atTop.2 ⟨a, fun N hN => (hpart N hN).trans (hle N)⟩)
  linarith

/-- The sum of the Poisson masses below `a` against the Borel tail at `a`:
`(23/24) ∑_{0<j<a} p_j ≤ a (1 - ∑_{0<j<a} p_j/j)`.  For `a ≤ 1` the sums are empty.
For `a ≥ 2`, with `u = √(a-1)` and `w = √a`, the left side is at most `(23/24) c₀ (2u - 1)`
(`sum_poissonMass_le`, a private lemma of `Parking.Crossing.Bounds`, without its term `p_0 = 1`) and
the right side at least `c₀ (2a - 1/6)/w`, and `(2u - 1) w ≤ u² + w² - w ≤ 2a - 1`. -/
private theorem sum_poissonMass_le_tail (a : ℕ) :
    23 / 24 * ∑ j ∈ Ico 1 a, poissonMass j ≤ (a : ℝ) * (1 - ∑ j ∈ Ico 1 a, poissonMass j / j) := by
  rcases Nat.lt_or_ge a 2 with ha1 | ha2
  · interval_cases a <;> simp
  have hc0 := c0_pos
  have ha' : (2 : ℝ) ≤ a := by exact_mod_cast ha2
  have hS : ∑ j ∈ Ico 1 a, poissonMass j ≤ c0 * (2 * Real.sqrt ((a : ℝ) - 1) - 1) := by
    have h := sum_poissonMass_le ha2
    rw [range_eq_Ico, sum_eq_sum_Ico_succ_bot (by omega : 0 < a), poissonMass_zero,
      Nat.zero_add] at h
    linarith
  have hB := mul_le_mul_of_nonneg_left (borel_tail_ge (a := a) (by omega))
    (by linarith : (0 : ℝ) ≤ a)
  have hu : Real.sqrt ((a : ℝ) - 1) ^ 2 = a - 1 := Real.sq_sqrt (by linarith)
  have hw : Real.sqrt (a : ℝ) ^ 2 = a := Real.sq_sqrt (by linarith)
  have hw0 : 0 < Real.sqrt (a : ℝ) := Real.sqrt_pos.2 (by linarith)
  set u := Real.sqrt ((a : ℝ) - 1)
  set w := Real.sqrt (a : ℝ)
  have h1 : (2 * u - 1) * w ≤ 2 * a - 1 := by nlinarith [sq_nonneg (u - w)]
  have h2 : 23 / 24 * (c0 * (2 * u - 1)) ≤ a * (2 * c0 * (1 - 1 / (12 * (a : ℝ))) / w) := by
    rw [show (a : ℝ) * (2 * c0 * (1 - 1 / (12 * (a : ℝ))) / w) = c0 * (2 * a - 1 / 6) / w by field,
      le_div_iff₀ hw0]
    nlinarith [mul_le_mul_of_nonneg_left h1 hc0.le, mul_pos hc0 (by linarith : (0 : ℝ) < a)]
  linarith

/-! ### The step of the normalised deficit along the diagonal -/

/-- The closed form `T` that bounds the relative increase of the normalised kernel deficit on a
diagonal step: with `ξ = a/k`,
`T = (3/2) ξ · (1 + 2/(3(k+2))) · (1 + (3/2)ξ + (3/8)ξ²) / (23/24 - (3/2) ξ (1 + ξ/4))`. -/
noncomputable def kapStepBound (k a : ℕ) : ℝ :=
  3 / 2 * ((a : ℝ) / k) * (1 + 2 / (3 * ((k : ℝ) + 2)))
    * (1 + 3 / 2 * ((a : ℝ) / k) + 3 / 8 * ((a : ℝ) / k) ^ 2)
    / (23 / 24 - 3 / 2 * ((a : ℝ) / k) * (1 + (a : ℝ) / k / 4))

/-- For `2a ≤ k` the denominator `23/24 - (3/2) ξ (1 + ξ/4)` of `kapStepBound k a` is positive,
because `ξ = a/k ≤ 1/2`. -/
private theorem kapStepBound_den_pos {k a : ℕ} (hak : 2 * a ≤ k) :
    0 < 23 / 24 - 3 / 2 * ((a : ℝ) / k) * (1 + (a : ℝ) / k / 4) := by
  have hξ0 : 0 ≤ (a : ℝ) / k := by positivity
  have hξ : (a : ℝ) / k ≤ 1 / 2 := by
    rcases Nat.eq_zero_or_pos k with rfl | hk
    · simp
    · rw [div_le_iff₀ (by exact_mod_cast hk)]
      have h : (2 : ℝ) * a ≤ k := by exact_mod_cast hak
      linarith
  nlinarith [mul_le_mul_of_nonneg_left hξ hξ0]

/-- The closed form `kapStepBound k a` is nonnegative for `2a ≤ k`: its denominator is positive,
and every other factor is nonnegative. -/
theorem kapStepBound_nonneg {k a : ℕ} (hak : 2 * a ≤ k) : 0 ≤ kapStepBound k a :=
  div_nonneg (by positivity) (kapStepBound_den_pos hak).le

/-- **The kernel deficit along the diagonal.**  For `k ≥ 1` and `2a ≤ k` the normalised kernel
deficit grows on a diagonal step by at most the factor `1 + T/k`, `T = kapStepBound k a`:
`κ_{k+1}(k+a+1)/a_{k+a+1} ≤ (1 + T/k) · κ_k(k+a)/a_{k+a}`.

With `S = ∑_{0<j<a} p_j`, the sum of the Poisson masses, and `B = 1 - ∑_{0<j<a} p_j/j`, the Borel
tail, the increase of the normalised deficit is at most a multiple of `S/((k+a)(k+1))`, and the
deficit itself is at least `B - (3/2)(1 + ξ/4) · S/(k+1)`.  Since `(23/24) S ≤ a B`, the second
bound gives `(23/24 - (3/2) ξ (1 + ξ/4)) · S/(k+1) ≤ ξ · κ_k(k+a)/a_{k+a}`, and with this the
first bound becomes the claim. -/
theorem kap_diag_le {k a : ℕ} (hk : 1 ≤ k) (hak : 2 * a ≤ k) :
    kap (k + 1) (k + a + 1) / cay (k + a + 1)
      ≤ (1 + kapStepBound k a / k) * (kap k (k + a) / cay (k + a)) := by
  have hden := kapStepBound_den_pos hak
  have hk0 : (0 : ℝ) < k := by exact_mod_cast hk
  have ha0 : (0 : ℝ) ≤ a := Nat.cast_nonneg a
  have hgap := kap_div_cay_succ_sub_le (a := a) hk
  have hlow := kap_div_cay_ge (a := a) hk
  have hkey := sum_poissonMass_le_tail a
  have hS : 0 ≤ ∑ j ∈ Ico 1 a, poissonMass j := sum_nonneg fun j _ => (poissonMass_pos j).le
  unfold kapStepBound
  set S := ∑ j ∈ Ico 1 a, poissonMass j
  set B := 1 - ∑ j ∈ Ico 1 a, poissonMass j / j
  set κ := kap k (k + a) / cay (k + a)
  set ξ : ℝ := (a : ℝ) / k
  set D := 23 / 24 - 3 / 2 * ξ * (1 + ξ / 4) with hD
  have hξ0 : 0 ≤ ξ := div_nonneg ha0 hk0.le
  -- the deficit dominates the sum of the masses: `D · S/(k+1) ≤ ξ κ`
  have h1 : 23 / 24 * (S / ((k : ℝ) + 1)) ≤ ξ * B :=
    calc 23 / 24 * (S / ((k : ℝ) + 1)) ≤ 23 / 24 * (S / k) := by
          gcongr
          linarith
      _ = 23 / 24 * S / k := by ring
      _ ≤ a * B / k := by gcongr
      _ = ξ * B := by ring
  have h2 : ξ * B - 3 / 2 * ξ * (1 + ξ / 4) * (S / ((k : ℝ) + 1)) ≤ ξ * κ :=
    calc ξ * B - 3 / 2 * ξ * (1 + ξ / 4) * (S / ((k : ℝ) + 1))
        = ξ * (B - 3 / 2 * (1 + ξ / 4) / ((k : ℝ) + 1) * S) := by ring
      _ ≤ ξ * κ := by gcongr
  have h3 : S / ((k : ℝ) + 1) ≤ ξ * κ / D := by
    rw [le_div_iff₀' hden, hD]
    linarith
  -- the increase is a multiple of `S/(k+1)`, hence of `κ`
  calc kap (k + 1) (k + a + 1) / cay (k + a + 1)
      ≤ κ + (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2)
          * (3 / 2 * (1 + 2 / (3 * ((k : ℝ) + 2))) / (((k : ℝ) + a) * ((k : ℝ) + 1))) * S := by
        linarith
    _ = κ + 3 / 2 * (1 + 2 / (3 * ((k : ℝ) + 2))) * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) / k
          * ((k : ℝ) / ((k : ℝ) + a)) * (S / ((k : ℝ) + 1)) := by
        field
    _ ≤ κ + 3 / 2 * (1 + 2 / (3 * ((k : ℝ) + 2))) * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) / k
          * 1 * (ξ * κ / D) := by
        gcongr
        rw [div_le_one (by positivity)]
        linarith
    _ = (1 + 3 / 2 * ξ * (1 + 2 / (3 * ((k : ℝ) + 2))) * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) / D / k)
          * κ := by
        field

end Parking
