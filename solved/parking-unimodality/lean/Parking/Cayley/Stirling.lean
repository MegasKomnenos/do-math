import Parking.Cayley.Basic
import Mathlib.Analysis.SpecialFunctions.Stirling
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.Real.Pi.Bounds

/-!
# Stirling's formula in Robbins' form, and the renewal masses

* `poissonMass n = e^{-n} n^n / n!` (the mass at `n` of the Poisson law of mean `n`;
  `poissonMass 0 = 1`).
* `factorial_le_robbins` : `n! ≤ √(2πn) (n/e)^n e^{1/(12n)}`.
* `poissonMass_le`, `poissonMass_ge`     :
  `c₀ n^{-1/2} (1 - 1/(12n)) ≤ poissonMass n ≤ c₀ n^{-1/2}`, `c₀ = 1/√(2π)`.
-/

namespace Parking

open Finset

/-- Renewal mass `poissonMass(n) = e^{-n} n^n / n!`. -/
noncomputable def poissonMass (n : ℕ) : ℝ := Real.exp (-(n : ℝ)) * ren n

/-- The Poisson mass $e^{-n} n^n/n!$ takes the value $1$ at $n = 0$. -/
theorem poissonMass_zero : poissonMass 0 = 1 := by
  simp [poissonMass, ren]

/-- The Poisson mass $e^{-n} n^n/n!$ is positive for every $n \ge 0$. -/
theorem poissonMass_pos (n : ℕ) : 0 < poissonMass n :=
  mul_pos (Real.exp_pos _) (ren_pos n)

/-- `poissonMass n = (n/e)^n / n!`. -/
theorem poissonMass_eq (n : ℕ) : poissonMass n = ((n : ℝ) / Real.exp 1) ^ n
    / (n.factorial : ℝ) := by
  have h : Real.exp 1 ^ n = Real.exp (n : ℝ) := by
    rw [← Real.exp_nat_mul, mul_one]
  have h2 : Real.exp (-(n : ℝ)) = (Real.exp (n : ℝ))⁻¹ := Real.exp_neg _
  unfold poissonMass ren
  rw [div_pow, h, h2]
  ring

/-- Telescoped form of Robbins' stepwise bound `Stirling.log_stirlingSeq_sdiff_le`. -/
private theorem log_stirlingSeq_le_add {n m : ℕ} (hn : 1 ≤ n) (hnm : n ≤ m) :
    Real.log (Stirling.stirlingSeq n) + 1 / (12 * (m : ℝ))
      ≤ Real.log (Stirling.stirlingSeq m) + 1 / (12 * (n : ℝ)) := by
  induction m, hnm using Nat.le_induction with
  | base => exact le_rfl
  | succ k hk ih =>
    have hk1 : 1 ≤ k := le_trans hn hk
    have hk0 : (0 : ℝ) < k := by exact_mod_cast hk1
    have hk0' : (k : ℝ) ≠ 0 := hk0.ne'
    have hk1' : (k : ℝ) + 1 ≠ 0 := by positivity
    have h := Stirling.log_stirlingSeq_sdiff_le k
    have e : (1 : ℝ) / (12 * (k : ℝ) * ((k : ℝ) + 1))
        = 1 / (12 * (k : ℝ)) - 1 / (12 * ((k : ℝ) + 1)) := by
      field
    rw [e] at h
    push_cast
    linarith

/-- `stirlingSeq n ≤ √π e^{1/(12n)}`. -/
private theorem stirlingSeq_le {n : ℕ} (hn : 1 ≤ n) :
    Stirling.stirlingSeq n ≤ Real.sqrt Real.pi * Real.exp (1 / (12 * (n : ℝ))) := by
  have hpi : (0 : ℝ) < Real.sqrt Real.pi := Real.sqrt_pos.2 Real.pi_pos
  have hpos : 0 < Stirling.stirlingSeq n := by
    obtain ⟨k, rfl⟩ : ∃ k, n = k + 1 := ⟨n - 1, by omega⟩
    exact Stirling.stirlingSeq'_pos k
  have hlim : Filter.Tendsto (fun m : ℕ => Real.log (Stirling.stirlingSeq m)) Filter.atTop
      (nhds (Real.log (Real.sqrt Real.pi))) :=
    (Real.continuousAt_log hpi.ne').tendsto.comp Stirling.tendsto_stirlingSeq_sqrt_pi
  have hev : ∀ᶠ m : ℕ in Filter.atTop,
      Real.log (Stirling.stirlingSeq n) - 1 / (12 * (n : ℝ))
        ≤ Real.log (Stirling.stirlingSeq m) := by
    filter_upwards [Filter.eventually_ge_atTop n] with m hm
    have h := log_stirlingSeq_le_add hn hm
    have h0 : (0 : ℝ) ≤ 1 / (12 * (m : ℝ)) := by positivity
    linarith
  have hle : Real.log (Stirling.stirlingSeq n) - 1 / (12 * (n : ℝ))
      ≤ Real.log (Real.sqrt Real.pi) :=
    ge_of_tendsto hlim hev
  calc Stirling.stirlingSeq n
      = Real.exp (Real.log (Stirling.stirlingSeq n)) := (Real.exp_log hpos).symm
    _ ≤ Real.exp (Real.log (Real.sqrt Real.pi) + 1 / (12 * (n : ℝ))) :=
        Real.exp_le_exp.2 (by linarith)
    _ = Real.sqrt Real.pi * Real.exp (1 / (12 * (n : ℝ))) := by
        rw [Real.exp_add, Real.exp_log hpi]

/-- Robbins' upper bound for the factorial. -/
theorem factorial_le_robbins {n : ℕ} (hn : 1 ≤ n) :
    (n.factorial : ℝ)
      ≤ Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n
          * Real.exp (1 / (12 * (n : ℝ))) := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  have hD : 0 < Real.sqrt (2 * (n : ℝ)) * ((n : ℝ) / Real.exp 1) ^ n := by
    have h1 : 0 < Real.sqrt (2 * (n : ℝ)) := Real.sqrt_pos.2 (by positivity)
    have h2 : 0 < ((n : ℝ) / Real.exp 1) ^ n := by positivity
    exact mul_pos h1 h2
  have h := stirlingSeq_le hn
  unfold Stirling.stirlingSeq at h
  rw [div_le_iff₀ hD] at h
  have hs : Real.sqrt (2 * Real.pi * n) = Real.sqrt Real.pi * Real.sqrt (2 * (n : ℝ)) := by
    rw [show 2 * Real.pi * (n : ℝ) = Real.pi * (2 * (n : ℝ)) by ring,
      Real.sqrt_mul Real.pi_pos.le]
  rw [hs]
  calc (n.factorial : ℝ)
      ≤ Real.sqrt Real.pi * Real.exp (1 / (12 * (n : ℝ)))
          * (Real.sqrt (2 * (n : ℝ)) * ((n : ℝ) / Real.exp 1) ^ n) := h
    _ = Real.sqrt Real.pi * Real.sqrt (2 * (n : ℝ)) * ((n : ℝ) / Real.exp 1) ^ n
          * Real.exp (1 / (12 * (n : ℝ))) := by ring

/-- The Poisson mass is at most its Stirling approximation: $e^{-n} n^n/n! \le 1/\sqrt{2\pi n}$ for
every $n \ge 1$. -/
theorem poissonMass_le {n : ℕ} (hn : 1 ≤ n) : poissonMass n ≤ 1 / Real.sqrt (2 * Real.pi * n) := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  have hs : 0 < Real.sqrt (2 * Real.pi * n) := Real.sqrt_pos.2 (by positivity)
  have hf : (0 : ℝ) < n.factorial := by positivity
  have h := Stirling.le_factorial_stirling n
  rw [poissonMass_eq, div_le_div_iff₀ hf hs]
  linarith

/-- The Poisson mass is at least its Stirling approximation times $1 - \frac{1}{12n}$: $(1 -
\frac{1}{12n})/\sqrt{2\pi n} \le e^{-n} n^n/n!$ for every $n \ge 1$. -/
theorem poissonMass_ge {n : ℕ} (hn : 1 ≤ n) :
    (1 - 1 / (12 * (n : ℝ))) / Real.sqrt (2 * Real.pi * n) ≤ poissonMass n := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  have hs : 0 < Real.sqrt (2 * Real.pi * n) := Real.sqrt_pos.2 (by positivity)
  have hf : (0 : ℝ) < n.factorial := by positivity
  have h := factorial_le_robbins hn
  have h1 : 1 - 1 / (12 * (n : ℝ)) ≤ Real.exp (-(1 / (12 * (n : ℝ)))) := by
    have := Real.add_one_le_exp (-(1 / (12 * (n : ℝ))))
    linarith
  have h2 : Real.exp (-(1 / (12 * (n : ℝ)))) * Real.exp (1 / (12 * (n : ℝ))) = 1 := by
    rw [← Real.exp_add, neg_add_cancel, Real.exp_zero]
  rw [poissonMass_eq, div_le_div_iff₀ hs hf]
  calc (1 - 1 / (12 * (n : ℝ))) * (n.factorial : ℝ)
      ≤ Real.exp (-(1 / (12 * (n : ℝ)))) * (n.factorial : ℝ) :=
        mul_le_mul_of_nonneg_right h1 hf.le
    _ ≤ Real.exp (-(1 / (12 * (n : ℝ))))
          * (Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n
              * Real.exp (1 / (12 * (n : ℝ)))) :=
        mul_le_mul_of_nonneg_left h (Real.exp_pos _).le
    _ = ((n : ℝ) / Real.exp 1) ^ n * Real.sqrt (2 * Real.pi * n) := by
        linear_combination (Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n) * h2

/-! ### The constant `c₀ = 1/√(2π)` -/

/-- `c₀ = 1/√(2π)`. -/
noncomputable def c0 : ℝ := 1 / Real.sqrt (2 * Real.pi)

/-- `0.39894 ≤ c₀ ≤ 0.39895`. -/
theorem c0_bounds : (19947 / 50000 : ℝ) ≤ c0 ∧ c0 ≤ 7979 / 20000 := by
  unfold c0
  have hpi1 : (3141592 / 1000000 : ℝ) < Real.pi := lt_of_le_of_lt (by norm_num) Real.pi_gt_d6
  have hpi2 : Real.pi < 3141593 / 1000000 := lt_of_lt_of_le Real.pi_lt_d6 (by norm_num)
  have h2pi : (0 : ℝ) < 2 * Real.pi := by linarith
  have hs : 0 < Real.sqrt (2 * Real.pi) := Real.sqrt_pos.mpr h2pi
  have hup : Real.sqrt (2 * Real.pi) ≤ 50000 / 19947 := by
    rw [Real.sqrt_le_left (by norm_num)]
    have h : (2 : ℝ) * (3141593 / 1000000) ≤ (50000 / 19947) ^ 2 := by norm_num
    calc 2 * Real.pi ≤ 2 * (3141593 / 1000000) := by linarith
      _ ≤ (50000 / 19947) ^ 2 := h
  have hlo : (20000 / 7979 : ℝ) ≤ Real.sqrt (2 * Real.pi) := by
    apply Real.le_sqrt_of_sq_le
    have h : ((20000 / 7979 : ℝ)) ^ 2 ≤ 2 * (3141592 / 1000000) := by norm_num
    calc ((20000 / 7979 : ℝ)) ^ 2 ≤ 2 * (3141592 / 1000000) := h
      _ ≤ 2 * Real.pi := by linarith
  refine ⟨?_, ?_⟩
  · rw [le_div_iff₀ hs]; linarith
  · rw [div_le_iff₀ hs]; linarith

/-- The constant $c_0 = 1/\sqrt{2\pi}$ is positive. -/
theorem c0_pos : 0 < c0 :=
  div_pos one_pos (Real.sqrt_pos.2 (mul_pos zero_lt_two Real.pi_pos))

/-- `poissonMass i ≤ c₀/√i` for `i ≥ 1`. -/
theorem poissonMass_le_c0 {i : ℕ} (hi : 1 ≤ i) : poissonMass i ≤ c0 / Real.sqrt (i : ℝ) := by
  have h := poissonMass_le hi
  rw [Real.sqrt_mul (mul_pos zero_lt_two Real.pi_pos).le] at h
  unfold c0
  rw [div_div]
  exact h

/-- `poissonMass i ≥ c₀ (1 - 1/(12 i))/√i` for `i ≥ 1`. -/
theorem poissonMass_ge_c0 {i : ℕ} (hi : 1 ≤ i) :
    c0 * (1 - 1 / (12 * (i : ℝ))) / Real.sqrt (i : ℝ) ≤ poissonMass i := by
  have h := poissonMass_ge hi
  rw [Real.sqrt_mul (mul_pos zero_lt_two Real.pi_pos).le] at h
  have e : c0 * (1 - 1 / (12 * (i : ℝ))) / Real.sqrt (i : ℝ)
      = (1 - 1 / (12 * (i : ℝ))) / (Real.sqrt (2 * Real.pi) * Real.sqrt (i : ℝ)) := by
    unfold c0
    ring
  rw [e]
  exact h

end Parking
