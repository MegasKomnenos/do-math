module

public import Parking.Cayley.Basic
public import Mathlib.Analysis.SpecialFunctions.Stirling
public import Mathlib.Analysis.SpecialFunctions.Sqrt
public import Mathlib.Analysis.Real.Pi.Bounds

/-!
# Stirling's formula in Robbins' form, and the renewal masses

* `poissonMass n = e^{-n} n^n / n!` (the mass at `n` of the Poisson law of mean `n`;
  `poissonMass 0 = 1`).
* `robbins_lt_factorial`, `factorial_lt_robbins` :
  `√(2πn) (n/e)^n e^{1/(12n+1)} < n! < √(2πn) (n/e)^n e^{1/(12n)}` for `n ≥ 1`.
* `poissonMass_le`, `poissonMass_ge`     :
  `c₀ n^{-1/2} (1 - 1/(12n)) ≤ poissonMass n ≤ c₀ n^{-1/2}`, `c₀ = 1/√(2π)`.
-/

@[expose] public section

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

/-! ### Robbins' bounds for the factorial -/

/-- Robbins' bounds for one step of the Stirling sequence `s_n = n!/(√(2n) (n/e)^n)`, both strict:
`1/(12n+1) - 1/(12(n+1)+1) < log s_n - log s_{n+1} < 1/(12n) - 1/(12(n+1))` for `n = m + 1`. -/
private theorem log_stirlingSeq_sdiff_bounds (m : ℕ) :
    1 / (12 * ((m + 1 : ℕ) : ℝ) + 1) - 1 / (12 * ((m + 1 + 1 : ℕ) : ℝ) + 1)
        < Real.log (Stirling.stirlingSeq (m + 1)) - Real.log (Stirling.stirlingSeq (m + 1 + 1))
      ∧ Real.log (Stirling.stirlingSeq (m + 1)) - Real.log (Stirling.stirlingSeq (m + 1 + 1))
        < 1 / (12 * ((m + 1 : ℕ) : ℝ)) - 1 / (12 * ((m + 1 + 1 : ℕ) : ℝ)) := by
  have hs := Stirling.log_stirlingSeq_sdiff_hasSum m
  have hx1 : (1 : ℝ) ≤ ((m + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.le_add_left 1 m
  have hx2 : ((m + 1 + 1 : ℕ) : ℝ) = ((m + 1 : ℕ) : ℝ) + 1 := by push_cast; ring
  rw [hx2]
  generalize ((m + 1 : ℕ) : ℝ) = x at hs hx1 ⊢
  have hx0 : (0 : ℝ) < x := by linarith
  constructor
  · have e : 1 / 3 * (1 / (2 * x + 1)) ^ 2 - (1 / (12 * x + 1) - 1 / (12 * (x + 1) + 1))
        = (24 * x - 23) / (3 * (2 * x + 1) ^ 2 * (12 * x + 1) * (12 * (x + 1) + 1)) := by
      field
    calc 1 / (12 * x + 1) - 1 / (12 * (x + 1) + 1)
        < 1 / 3 * (1 / (2 * x + 1)) ^ 2 := by
          rw [← sub_pos, e]
          exact div_pos (by linarith) (by positivity)
      _ = 1 / (2 * ((0 + 1 : ℕ) : ℝ) + 1) * ((1 / (2 * x + 1)) ^ 2) ^ (0 + 1) := by norm_num
      _ ≤ Real.log (Stirling.stirlingSeq (m + 1))
            - Real.log (Stirling.stirlingSeq (m + 1 + 1)) :=
          le_hasSum hs 0 fun j _ => by positivity
  · set r : ℝ := (1 / (2 * x + 1)) ^ 2 with hr
    have hr0 : 0 < r := by positivity
    have hr1 : r < 1 :=
      pow_lt_one₀ (by positivity) (by rw [div_lt_one (by positivity)]; linarith) two_ne_zero
    have e1 : 1 - r = 4 * x * (x + 1) * r := by rw [hr]; field
    have e2 : 1 / 3 * ((1 - r)⁻¹ * r) = 1 / (12 * x) - 1 / (12 * (x + 1)) := by
      rw [e1]; field
    have hg : HasSum (fun k : ℕ => 1 / 3 * r ^ (k + 1)) (1 / (12 * x) - 1 / (12 * (x + 1))) := by
      have h := ((hasSum_geometric_of_lt_one hr0.le hr1).mul_right r).mul_left (1 / 3)
      rw [e2] at h
      simpa only [pow_succ] using h
    refine hasSum_lt (i := 1) (fun k => ?_) ?_ hs hg
    · have h3 : (1 : ℝ) / (2 * ((k + 1 : ℕ) : ℝ) + 1) ≤ 1 / 3 :=
        one_div_le_one_div_of_le (by norm_num)
          (by push_cast; linarith [(k.cast_nonneg : (0 : ℝ) ≤ k)])
      exact mul_le_mul_of_nonneg_right h3 (pow_nonneg hr0.le _)
    · exact mul_lt_mul_of_pos_right (by norm_num) (pow_pos hr0 _)

/-- For every real `a`, `log s_{m+1} - 1/(12(m+1) + a) → log √π` as `m → ∞`, where `s` is the
Stirling sequence. -/
private theorem tendsto_log_stirlingSeq_sub (a : ℝ) :
    Filter.Tendsto (fun m : ℕ => Real.log (Stirling.stirlingSeq (m + 1))
        - 1 / (12 * ((m + 1 : ℕ) : ℝ) + a)) Filter.atTop
      (nhds (Real.log (Real.sqrt Real.pi))) := by
  have hpi : Real.sqrt Real.pi ≠ 0 := (Real.sqrt_pos.2 Real.pi_pos).ne'
  have hs : Filter.Tendsto (fun m : ℕ => Real.log (Stirling.stirlingSeq (m + 1))) Filter.atTop
      (nhds (Real.log (Real.sqrt Real.pi))) :=
    (Stirling.tendsto_stirlingSeq_sqrt_pi.log hpi).comp (Filter.tendsto_add_atTop_nat 1)
  have hd : Filter.Tendsto (fun m : ℕ => 12 * ((m + 1 : ℕ) : ℝ) + a) Filter.atTop Filter.atTop :=
    Filter.tendsto_atTop_add_const_right _ _
      ((tendsto_natCast_atTop_atTop.comp (Filter.tendsto_add_atTop_nat 1)).const_mul_atTop
        (by norm_num))
  have h := hs.sub ((tendsto_const_nhds (x := (1 : ℝ))).div_atTop hd)
  rwa [sub_zero] at h

/-- Robbins' bounds for the Stirling sequence `s`: `1/(12n+1) < log s_n - log √π < 1/(12n)` for
`n ≥ 1`. -/
private theorem log_stirlingSeq_bounds {n : ℕ} (hn : 1 ≤ n) :
    Real.log (Real.sqrt Real.pi) + 1 / (12 * (n : ℝ) + 1) < Real.log (Stirling.stirlingSeq n)
      ∧ Real.log (Stirling.stirlingSeq n) < Real.log (Real.sqrt Real.pi) + 1 / (12 * (n : ℝ)) := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  obtain ⟨hlo, hup⟩ := log_stirlingSeq_sdiff_bounds m
  constructor
  · have hanti : Antitone fun k : ℕ => Real.log (Stirling.stirlingSeq (k + 1))
        - 1 / (12 * ((k + 1 : ℕ) : ℝ) + 1) :=
      antitone_nat_of_succ_le fun k => by linarith [(log_stirlingSeq_sdiff_bounds k).1]
    have hlim := hanti.le_of_tendsto (tendsto_log_stirlingSeq_sub 1) (m + 1)
    beta_reduce at hlim
    linarith
  · have hmono : Monotone fun k : ℕ => Real.log (Stirling.stirlingSeq (k + 1))
        - 1 / (12 * ((k + 1 : ℕ) : ℝ)) :=
      monotone_nat_of_le_succ fun k => by linarith [(log_stirlingSeq_sdiff_bounds k).2]
    have hlim := hmono.ge_of_tendsto
      (by simpa only [add_zero] using tendsto_log_stirlingSeq_sub 0) (m + 1)
    beta_reduce at hlim
    linarith

/-- Robbins' form of the factorial: `n! = √(2πn) (n/e)^n e^{r_n}` for `n ≥ 1`, with
`r_n = log s_n - log √π` and `s` the Stirling sequence. -/
private theorem factorial_eq_robbins {n : ℕ} (hn : 1 ≤ n) :
    (n.factorial : ℝ) = Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n
      * Real.exp (Real.log (Stirling.stirlingSeq n) - Real.log (Real.sqrt Real.pi)) := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  have hpi : (0 : ℝ) < Real.sqrt Real.pi := Real.sqrt_pos.2 Real.pi_pos
  have hf : (0 : ℝ) < n.factorial := by positivity
  have h1 : 0 < Real.sqrt (2 * (n : ℝ)) := Real.sqrt_pos.2 (by positivity)
  have h2 : 0 < ((n : ℝ) / Real.exp 1) ^ n := by positivity
  have hs : Real.sqrt (2 * Real.pi * n) = Real.sqrt Real.pi * Real.sqrt (2 * (n : ℝ)) := by
    rw [show 2 * Real.pi * (n : ℝ) = Real.pi * (2 * (n : ℝ)) by ring,
      Real.sqrt_mul Real.pi_pos.le]
  have hpos : 0 < Stirling.stirlingSeq n := div_pos hf (mul_pos h1 h2)
  rw [Real.exp_sub, Real.exp_log hpos, Real.exp_log hpi, hs]
  unfold Stirling.stirlingSeq
  field

/-- The factor `√(2πn) (n/e)^n` of Robbins' bounds is positive for `n ≥ 1`. -/
private theorem robbins_pos {n : ℕ} (hn : 1 ≤ n) :
    0 < Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  exact mul_pos (Real.sqrt_pos.2 (by positivity)) (by positivity)

/-- **Robbins' lower bound for the factorial**: `√(2πn) (n/e)^n e^{1/(12n+1)} < n!` for `n ≥ 1`. -/
theorem robbins_lt_factorial {n : ℕ} (hn : 1 ≤ n) :
    Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n
          * Real.exp (1 / (12 * (n : ℝ) + 1))
      < (n.factorial : ℝ) :=
  (mul_lt_mul_of_pos_left
    (Real.exp_lt_exp.2 (by linarith [(log_stirlingSeq_bounds hn).1])) (robbins_pos hn)).trans_eq
    (factorial_eq_robbins hn).symm

/-- **Robbins' upper bound for the factorial**: `n! < √(2πn) (n/e)^n e^{1/(12n)}` for `n ≥ 1`. -/
theorem factorial_lt_robbins {n : ℕ} (hn : 1 ≤ n) :
    (n.factorial : ℝ)
      < Real.sqrt (2 * Real.pi * n) * ((n : ℝ) / Real.exp 1) ^ n
          * Real.exp (1 / (12 * (n : ℝ))) :=
  (factorial_eq_robbins hn).trans_lt
    (mul_lt_mul_of_pos_left
      (Real.exp_lt_exp.2 (by linarith [(log_stirlingSeq_bounds hn).2])) (robbins_pos hn))

/-! ### The Stirling bounds of the Poisson mass -/

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
  have h := (factorial_lt_robbins hn).le
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
