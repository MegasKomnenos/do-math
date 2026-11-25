import Parking.Basic.Sums
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
# The persistence inequality

Rows are indexed by naturals; `k` is the column, `n` the target row.  Three sequences are given: a
kernel `ε`, a profile `u` and a column `δ`.  Assume

* the column equation at row `n`, as an inequality:
  `(2 / n) u (n - 1) + ((k + 1) / n) δ (n - 1) + ∑_{m=1}^{n-k} ε m δ (n - m) ≤ δ n`;
* the diagonal lower bound `γ u (j - 1) - u j ≤ δ j` on the rows `k ≤ j ≤ n - 1`, and
  `u (k - 1) = 0`;
* `ε (m + 1) ≤ γ ε m` for `1 ≤ m < τ`: the kernel in the diagonal scale, `ε m / γ ^ m`, is
  nonincreasing up to `τ`;
* `δ ≥ 0` on the `τ - 1` rows before `n`.

Then

  `(2 / n - ε τ / γ ^ (τ - 1)) u (n - 1) + ∑_{m=τ}^{n-k-1} (γ ε m - ε (m + 1)) u (n - 1 - m) ≤ δ n`.

Proof outline, with `ψ = ε τ / γ ^ (τ - 1)`, so that `ψ γ ^ (m - 1) ≤ ε m` for `1 ≤ m ≤ τ`:

1. drop the nonnegative term `((k + 1) / n) δ (n - 1)` of the column equation;
2. on the rows `1 ≤ m ≤ τ - 1` before `n`, where `δ ≥ 0`:
   `ε m δ (n - m) ≥ ψ γ ^ (m - 1) (γ u (n - 1 - m) - u (n - m))`, and the right sides telescope
   to `ε τ u (n - τ) - ψ u (n - 1)`;
3. on the older rows `τ ≤ m ≤ n - k`: `ε m δ (n - m) ≥ ε m (γ u (n - 1 - m) - u (n - m))`, and
   summation by parts turns the sum of the right sides into
   `- ε τ u (n - τ) + ∑_{m=τ}^{n-k-1} (γ ε m - ε (m + 1)) u (n - 1 - m)`
   plus a boundary term containing `u (k - 1) = 0`;
4. add 2 and 3.
-/

namespace Parking
open Finset

/-- Telescoping in the diagonal scale: if `q (m + 1) = p m` for all `m`, then
`∑_{m=1}^{N} c γ^(m-1) (γ p_m - q_m) = c (γ^N p_N - p_0)`. -/
private theorem sum_Icc_telescope (c γ : ℝ) (p q : ℕ → ℝ) (hpq : ∀ m, q (m + 1) = p m) (N : ℕ) :
    ∑ m ∈ Icc 1 N, c * γ ^ (m - 1) * (γ * p m - q m) = c * (γ ^ N * p N - p 0) := by
  induction N with
  | zero =>
    rw [Icc_eq_empty_of_lt (by omega : (0 : ℕ) < 1), sum_empty, pow_zero]
    ring
  | succ N ih =>
    rw [sum_Icc_succ_top (by omega : 1 ≤ N + 1), ih, Nat.add_sub_cancel, hpq N]
    ring

/-- Summation by parts: if `q (m + 1) = p m` for all `m` and `τ ≤ r`, then
`∑_{m=τ}^{r} a_m (γ p_m - q_m) = - a_τ q_τ + ∑_{m=τ}^{r-1} (γ a_m - a_{m+1}) p_m + γ a_r p_r`. -/
private theorem sum_Icc_abel (a p q : ℕ → ℝ) (γ : ℝ) {τ r : ℕ} (hτr : τ ≤ r)
    (hpq : ∀ m, q (m + 1) = p m) :
    ∑ m ∈ Icc τ r, a m * (γ * p m - q m)
      = - a τ * q τ + ∑ m ∈ Ico τ r, (γ * a m - a (m + 1)) * p m + γ * a r * p r := by
  induction r, hτr using Nat.le_induction with
  | base =>
    rw [Icc_self, sum_singleton, Ico_self, sum_empty]
    ring
  | succ r hτr ih =>
    rw [sum_Icc_succ_top (by omega : τ ≤ r + 1), ih, sum_Ico_succ_top hτr, hpq r]
    ring

/-- **The persistence inequality.** -/
theorem persistence_inequality (ε u δ : ℕ → ℝ) (γ : ℝ) (k n τ : ℕ)
    (hγ : 0 < γ) (hε : ∀ m, 1 ≤ m → 0 < ε m)
    (hkn : k + 1 ≤ n) (hτ2 : 2 ≤ τ) (hτr : τ ≤ n - k)
    (hk : u (k - 1) = 0) (hk1 : 1 ≤ k)
    -- the column equation at row `n`
    (hCE : (2 / (n : ℝ)) * u (n - 1) + ((k + 1 : ℝ) / n) * δ (n - 1)
              + ∑ m ∈ Icc 1 (n - k), ε m * δ (n - m) ≤ δ n)
    -- the diagonal lower bound on the rows `k … n - 1`
    (hDg : ∀ j, k ≤ j → j ≤ n - 1 → γ * u (j - 1) - u j ≤ δ j)
    -- the kernel in the diagonal scale is nonincreasing up to `τ`
    (hstep : ∀ m, 1 ≤ m → m < τ → ε (m + 1) ≤ γ * ε m)
    -- the column is nonnegative on the `τ - 1` rows before `n`
    (hpos : ∀ j, n - τ + 1 ≤ j → j ≤ n - 1 → 0 ≤ δ j) :
    (2 / (n : ℝ) - ε τ / γ ^ (τ - 1)) * u (n - 1)
        + ∑ m ∈ Icc τ (n - k - 1), (γ * ε m - ε (m + 1)) * u (n - 1 - m) ≤ δ n := by
  -- the constant `ψ = ε τ / γ ^ (τ - 1)`
  have hγpow : 0 < γ ^ (τ - 1) := pow_pos hγ (τ - 1)
  obtain ⟨ψ, hψdef⟩ : ∃ ψ : ℝ, ψ = ε τ / γ ^ (τ - 1) := ⟨_, rfl⟩
  have hψpos : 0 < ψ := by
    rw [hψdef]
    exact div_pos (hε τ (by omega)) hγpow
  have hψ : ψ * γ ^ (τ - 1) = ε τ := by
    rw [hψdef]
    exact div_mul_cancel₀ (ε τ) hγpow.ne'
  rw [← hψdef]
  -- `ψ * γ ^ (m - 1) ≤ ε m` for `1 ≤ m ≤ τ`, by descending induction from `m = τ`
  have hψm : ∀ m, 1 ≤ m → m ≤ τ → ψ * γ ^ (m - 1) ≤ ε m := by
    intro m hm1 hmτ
    induction hmτ using Nat.decreasingInduction with
    | self => exact hψ.le
    | of_succ m hm ih =>
      have h1 : ψ * γ ^ m ≤ ε (m + 1) := ih (by omega)
      have h2 : γ ^ m = γ * γ ^ (m - 1) := by rw [← pow_succ', Nat.sub_add_cancel hm1]
      refine le_of_mul_le_mul_left ?_ hγ
      calc γ * (ψ * γ ^ (m - 1)) = ψ * γ ^ m := by rw [h2]; ring
        _ ≤ ε (m + 1) := h1
        _ ≤ γ * ε m := hstep m hm1 hm
  -- step 1: drop the nonnegative term `((k + 1) / n) * δ (n - 1)`
  have h1 : (2 / (n : ℝ)) * u (n - 1) + ∑ m ∈ Icc 1 (n - k), ε m * δ (n - m) ≤ δ n := by
    have h2 : 0 ≤ ((k + 1 : ℝ) / n) * δ (n - 1) :=
      mul_nonneg (div_nonneg (add_nonneg (Nat.cast_nonneg k) zero_le_one) (Nat.cast_nonneg n))
        (hpos (n - 1) (by omega) le_rfl)
    linarith only [hCE, h2]
  -- split the feedback sum at `τ`
  have hsplit : ∑ m ∈ Icc 1 (n - k), ε m * δ (n - m)
      = ∑ m ∈ Icc 1 (τ - 1), ε m * δ (n - m) + ∑ m ∈ Icc (τ - 1 + 1) (n - k), ε m * δ (n - m) :=
    sum_Icc_split _ (by omega) (by omega)
  rw [Nat.sub_add_cancel (by omega : 1 ≤ τ)] at hsplit
  -- the diagonal lower bound at the row `n - m`
  have hdiag : ∀ m, 1 ≤ m → m ≤ n - k → γ * u (n - 1 - m) - u (n - m) ≤ δ (n - m) := by
    intro m hm1 hm2
    have h := hDg (n - m) (by omega) (by omega)
    rwa [show n - m - 1 = n - 1 - m by omega] at h
  have hpq : ∀ m, u (n - (m + 1)) = u (n - 1 - m) := fun m =>
    congrArg u (by omega : n - (m + 1) = n - 1 - m)
  -- step 2: the rows `1 ≤ m ≤ τ - 1` before `n`
  have hA : ∑ m ∈ Icc 1 (τ - 1), ψ * γ ^ (m - 1) * (γ * u (n - 1 - m) - u (n - m))
      ≤ ∑ m ∈ Icc 1 (τ - 1), ε m * δ (n - m) := by
    refine sum_le_sum fun m hm => ?_
    rw [mem_Icc] at hm
    calc ψ * γ ^ (m - 1) * (γ * u (n - 1 - m) - u (n - m))
        ≤ ψ * γ ^ (m - 1) * δ (n - m) :=
          mul_le_mul_of_nonneg_left (hdiag m hm.1 (by omega))
            (mul_nonneg hψpos.le (pow_pos hγ (m - 1)).le)
      _ ≤ ε m * δ (n - m) :=
          mul_le_mul_of_nonneg_right (hψm m hm.1 (by omega)) (hpos (n - m) (by omega) (by omega))
  have hT : ∑ m ∈ Icc 1 (τ - 1), ψ * γ ^ (m - 1) * (γ * u (n - 1 - m) - u (n - m))
      = ε τ * u (n - τ) - ψ * u (n - 1) := by
    rw [sum_Icc_telescope ψ γ (fun m => u (n - 1 - m)) (fun m => u (n - m)) hpq (τ - 1),
      show n - 1 - (τ - 1) = n - τ by omega, Nat.sub_zero, ← hψ]
    ring
  -- step 3: the older rows `τ ≤ m ≤ n - k`
  have hB : ∑ m ∈ Icc τ (n - k), ε m * (γ * u (n - 1 - m) - u (n - m))
      ≤ ∑ m ∈ Icc τ (n - k), ε m * δ (n - m) := by
    refine sum_le_sum fun m hm => ?_
    rw [mem_Icc] at hm
    exact mul_le_mul_of_nonneg_left (hdiag m (by omega) hm.2) (hε m (by omega)).le
  have hS : ∑ m ∈ Icc τ (n - k), ε m * (γ * u (n - 1 - m) - u (n - m))
      = - ε τ * u (n - τ)
        + ∑ m ∈ Icc τ (n - k - 1), (γ * ε m - ε (m + 1)) * u (n - 1 - m) := by
    rw [sum_Icc_abel ε (fun m => u (n - 1 - m)) (fun m => u (n - m)) γ hτr hpq,
      show n - 1 - (n - k) = k - 1 by omega, hk, mul_zero, add_zero,
      ← Ico_add_one_right_eq_Icc, Nat.sub_add_cancel (by omega : 1 ≤ n - k)]
  -- step 4: assemble
  linarith only [h1, hsplit, hA, hT, hB, hS]

end Parking