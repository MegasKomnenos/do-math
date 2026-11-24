module

public import Parking.Tilt.Critical
public import Parking.LeftHalf.FirstLayer.PropertyK
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
# The tilted Cayley masses at the critical tilt

`ω_n = ccT (xcrit k) n = (n+1)^(n-1) x_k^n / n!` is the tilted Cayley mass at the critical tilt
`x_k = xcrit k = (k/(k+1))^(k-1)`.  With

  `phi y = (y-1) Lg y`,  `Lg y = log (1 + 1/y)`,

one has `x_k = exp (-phi k)` and

  `ω_{n+1} = ω_n exp (phi (n+1) - phi k)`   (`ccT_succ_exp`),

so every statement about `ω` is a statement about the increments of `phi` and about the
monotonicity of `(1+1/i)^(i-1)` and `(1+1/i)^i` (`psi_mono`, `chi_mono` of
`Parking/Cayley/Basic.lean`).

## Inequalities between logarithms of consecutive numbers

The facts about `phi` are inequalities between linear combinations of `log (y-1)`, `log y`,
`log (y+1)`, `log (y+2)` with polynomial coefficients, and all are obtained from one lemma,
`log_comb3`, the only place where calculus is used: if `α + β t ≤ ∑ cᵢ/(aᵢ+t)` on `[0,1]`, then
`α + β/2 ≤ ∑ cᵢ (log (aᵢ+1) - log aᵢ)`, because `∑ cᵢ log (aᵢ+t) - α t - β t²/2` is nondecreasing
on `[0,1]`.

* `phi_step_lb` : `phi y - phi (y-1) ≥ 3/(2 y (y+1))`;
* `delta_ratio` : `(y+2) (phi (y+1) - phi y) ≤ y (phi y - phi (y-1))`;
* `Lam_lb`      : `(y+1) (phi (y+1) - phi y) - ϰ(y) ≥ (y²-2y-1)/(2y(y+1)(y+2))`, where
  `ϰ(y) = (y+1) Lg y - (y-1) Lg (y-1)` (`kap`);
* `amgm_tilt`   : the weighted arithmetic–geometric mean inequality in the form in which `ϰ`
  enters: if `(k+1) p + (k-1) q ≥ ϰ(k) + ξ`, then
  `e^{μ+p} + e^{-μ+q} ≥ 2 e^{μ/k} e^{ξ/(2k)}` for every real `μ`;
* `exp_phi`     : `exp (phi n) = (1 + 1/n)^(n-1)` for a positive integer `n`.

## The tilted Cayley masses

* `ccT_top`, `ccT_anti` : `ω_k = ω_{k-1}`, and `ω` is nonincreasing up to `k` (`ccT_succ_le` of
  `Parking/Tilt/Critical.lean`);
* `ccT_step_down` : `e^μ ω_{j+1} ≤ ω_j` for `j + 2 ≤ k` and `μ ≤ 1/(k(k+2))`;
* `ccT_logconvex` : `ω_{ρ+a} ω_{ρ+m-a} ≤ ω_ρ ω_{ρ+m}` (from `cay_logconvex`);
* `ccT_tilt_mid` : tilted convexity at every place below the top, for every real tilt:
  `2 e^{μ/k} ω_{j+1} ≤ e^μ ω_{j+2} + e^{-μ} ω_j` for `j + 2 ≤ k`;
* `ccT_tilt_top`, `ccT_tilt_top'` : two lower bounds for the surplus
  `e^μ ω_{k+1} + e^{-μ} ω_{k-1} - 2 e^{μ/k} ω_k` of the tilted convexity at the top;
* `TK_ccT_top` : the triple `(ω_{k-1}, ω_k, ω_{k+1})` has property K at `k`.
-/

@[expose] public section

namespace Parking.FirstLayer

/-! ### Inequalities between logarithms of consecutive numbers -/

section LogComb
open Real Set

/-- If `α + β t ≤ c₁/(a₁+t) + c₂/(a₂+t) + c₃/(a₃+t)` for `0 ≤ t ≤ 1`, then
`α + β/2 ≤ ∑ cᵢ (log (aᵢ+1) - log aᵢ)`. -/
private theorem log_comb3 (c₁ c₂ c₃ a₁ a₂ a₃ α β : ℝ) (h₁ : 0 < a₁) (h₂ : 0 < a₂) (h₃ : 0 < a₃)
    (h : ∀ t : ℝ, 0 ≤ t → t ≤ 1 →
      α + β * t ≤ c₁ / (a₁ + t) + c₂ / (a₂ + t) + c₃ / (a₃ + t)) :
    α + β / 2 ≤ c₁ * (Real.log (a₁ + 1) - Real.log a₁) +
      c₂ * (Real.log (a₂ + 1) - Real.log a₂) + c₃ * (Real.log (a₃ + 1) - Real.log a₃) := by
  have hlog : ∀ (a t : ℝ), 0 < a → 0 ≤ t →
      HasDerivAt (fun y : ℝ => Real.log (a + y)) (1 / (a + t)) t := by
    intro a t ha ht
    have h1 : HasDerivAt (fun y : ℝ => a + y) 1 t := (hasDerivAt_id' t).const_add a
    exact h1.log (by positivity)
  have hderiv : ∀ t : ℝ, 0 ≤ t →
      HasDerivAt (fun y : ℝ => c₁ * Real.log (a₁ + y) + c₂ * Real.log (a₂ + y) +
          c₃ * Real.log (a₃ + y) - α * y - β * y ^ 2 / 2)
        (c₁ / (a₁ + t) + c₂ / (a₂ + t) + c₃ / (a₃ + t) - α - β * t) t := by
    intro t ht
    have d1 := (hlog a₁ t h₁ ht).const_mul c₁
    have d2 := (hlog a₂ t h₂ ht).const_mul c₂
    have d3 := (hlog a₃ t h₃ ht).const_mul c₃
    have d4 : HasDerivAt (fun y : ℝ => α * y) α t := by
      simpa using (hasDerivAt_id' t).const_mul α
    have d5 : HasDerivAt (fun y : ℝ => β * y ^ 2 / 2) (β * t) t := by
      refine (((hasDerivAt_pow 2 t).const_mul β).div_const 2).congr_deriv ?_
      first
        | (norm_num; done)
        | (norm_num; ring)
    refine ((((d1.fun_add d2).fun_add d3).fun_sub d4).fun_sub d5).congr_deriv ?_
    ring
  obtain ⟨c, hc, hc'⟩ := exists_hasDerivAt_eq_slope
    (fun y : ℝ => c₁ * Real.log (a₁ + y) + c₂ * Real.log (a₂ + y) +
      c₃ * Real.log (a₃ + y) - α * y - β * y ^ 2 / 2)
    (fun t : ℝ => c₁ / (a₁ + t) + c₂ / (a₂ + t) + c₃ / (a₃ + t) - α - β * t)
    (zero_lt_one' ℝ) (fun x hx => (hderiv x hx.1).continuousAt.continuousWithinAt)
    (fun x hx => hderiv x hx.1.le)
  have hpos := h c hc.1.le hc.2.le
  norm_num at hc'
  linarith

/-- `Lg y = log (y+1) - log y = log (1 + 1/y)`. -/
private noncomputable def Lg (y : ℝ) : ℝ := Real.log (y + 1) - Real.log y

/-- `phi y = (y-1) log (1 + 1/y)`. -/
private noncomputable def phi (y : ℝ) : ℝ := (y - 1) * Lg y

/-- `ϰ(y) = (y+1) log ((y+1)/y) + (y-1) log ((y-1)/y)`. -/
private noncomputable def kap (y : ℝ) : ℝ := (y + 1) * Lg y - (y - 1) * Lg (y - 1)

private theorem Lg_sub_one (y : ℝ) : Lg (y - 1) = Real.log y - Real.log (y - 1) := by
  unfold Lg
  rw [sub_add_cancel]

/-- `phi y - phi (y-1) ≥ 3/(2 y (y+1))`. -/
private theorem phi_step_lb {y : ℝ} (hy : 2 ≤ y) : 3 / (2 * y * (y + 1)) ≤ phi y - phi (y - 1) := by
  have key := log_comb3 (y - 1) (-(y - 2)) 0 y (y - 1) 1 (1 / (y * (y + 1))) (1 / (y * (y + 1)))
    (by linarith) (by linarith) one_pos ?_
  · have e2 : 1 / (y * (y + 1)) + 1 / (y * (y + 1)) / 2 = 3 / (2 * y * (y + 1)) := by
      have hy0 : y ≠ 0 := by linarith
      have hy1 : y + 1 ≠ 0 := by linarith
      field_simp
      ring
    have e : y - 1 + 1 = y := by ring
    rw [e] at key
    unfold phi
    rw [Lg_sub_one]
    unfold Lg
    linarith
  · intro t ht0 ht1
    have p1 : 0 < y + t := by linarith
    have p2 : 0 < y - 1 + t := by linarith
    have p3 : 0 < y * (y + 1) := by nlinarith
    have e : (y - 1) / (y + t) + -(y - 2) / (y - 1 + t) + 0 / (1 + t) =
        (1 + t) / ((y + t) * (y - 1 + t)) := by
      field_simp
      ring
    have e' : 1 / (y * (y + 1)) + 1 / (y * (y + 1)) * t = (1 + t) / (y * (y + 1)) := by
      field_simp
    rw [e, e', div_le_div_iff₀ p3 (mul_pos p1 p2)]
    have h1 : (y + t) * (y - 1 + t) ≤ y * (y + 1) := by nlinarith
    exact mul_le_mul_of_nonneg_left h1 (by linarith)

/-- `y (y+1) (phi y - phi (y-1))` is nonincreasing: `(y+2) (phi (y+1) - phi y) ≤
y (phi y - phi (y-1))`. -/
private theorem delta_ratio {y : ℝ} (hy : 2 ≤ y) :
    (y + 2) * (phi (y + 1) - phi y) ≤ y * (phi y - phi (y - 1)) := by
  have key := log_comb3 (-(y * (y - 2))) (2 * (y ^ 2 - 1)) (-(y * (y + 2))) (y - 1) y (y + 1) 0 0
    (by linarith) (by linarith) (by linarith) ?_
  · have e : y - 1 + 1 = y := by ring
    have e3 : y + 1 - 1 = y := by ring
    rw [e] at key
    unfold phi
    rw [Lg_sub_one, e3]
    unfold Lg
    linarith
  · intro t ht0 ht1
    have p1 : 0 < y - 1 + t := by linarith
    have p2 : 0 < y + t := by linarith
    have p3 : 0 < y + 1 + t := by linarith
    have e : -(y * (y - 2)) / (y - 1 + t) + 2 * (y ^ 2 - 1) / (y + t) +
        -(y * (y + 2)) / (y + 1 + t) =
        2 * (1 - t ^ 2) / ((y - 1 + t) * (y + t) * (y + 1 + t)) := by
      field_simp
      ring
    rw [e]
    have h1 : 0 ≤ 1 - t ^ 2 := by nlinarith
    have h2 : 0 ≤ 2 * (1 - t ^ 2) / ((y - 1 + t) * (y + t) * (y + 1 + t)) :=
      div_nonneg (mul_nonneg zero_le_two h1) (by positivity)
    linarith

/-- `(y+1) (phi (y+1) - phi y) - ϰ(y) ≥ (y²-2y-1)/(2y(y+1)(y+2))`. -/
private theorem Lam_lb {y : ℝ} (hy : 3 ≤ y) :
    (y ^ 2 - 2 * y - 1) / (2 * y * (y + 1) * (y + 2)) ≤
      (y + 1) * (phi (y + 1) - phi y) - kap y := by
  have hq : 0 ≤ y ^ 2 - 2 * y - 1 := by nlinarith
  have key := log_comb3 (y - 1) (-(y * (y + 1))) (y * (y + 1)) (y - 1) y (y + 1) 0
    ((y ^ 2 - 2 * y - 1) / (y * (y + 1) * (y + 2))) (by linarith) (by linarith) (by linarith) ?_
  · have e2 : 0 + (y ^ 2 - 2 * y - 1) / (y * (y + 1) * (y + 2)) / 2 =
        (y ^ 2 - 2 * y - 1) / (2 * y * (y + 1) * (y + 2)) := by
      have hy0 : y ≠ 0 := by linarith
      have hy1 : y + 1 ≠ 0 := by linarith
      have hy2 : y + 2 ≠ 0 := by linarith
      field_simp
      ring
    have e : y - 1 + 1 = y := by ring
    have e3 : y + 1 - 1 = y := by ring
    rw [e] at key
    unfold phi kap
    rw [Lg_sub_one, e3]
    unfold Lg
    linarith
  · intro t ht0 ht1
    have p1 : 0 < y - 1 + t := by linarith
    have p2 : 0 < y + t := by linarith
    have p3 : 0 < y + 1 + t := by linarith
    have pD : 0 < y * (y + 1) * (y + 2) := by positivity
    have pd : 0 < (y - 1 + t) * (y + t) * (y + 1 + t) := by positivity
    have e : (y - 1) / (y - 1 + t) + -(y * (y + 1)) / (y + t) + y * (y + 1) / (y + 1 + t) =
        t * (y ^ 2 - 2 * y - 1 + (y - 1) * t) / ((y - 1 + t) * (y + t) * (y + 1 + t)) := by
      field_simp
      ring
    have e' : 0 + (y ^ 2 - 2 * y - 1) / (y * (y + 1) * (y + 2)) * t =
        t * (y ^ 2 - 2 * y - 1) / (y * (y + 1) * (y + 2)) := by
      rw [zero_add, div_mul_eq_mul_div, mul_comm]
    rw [e, e', div_le_div_iff₀ pD pd]
    -- the denominator on the right is the larger one
    have hden : (y - 1 + t) * (y + t) * (y + 1 + t) ≤ y * (y + 1) * (y + 2) :=
      mul_le_mul (mul_le_mul (by linarith) (by linarith) p2.le (by linarith)) (by linarith)
        p3.le (by positivity)
    have hA : 0 ≤ t * (y ^ 2 - 2 * y - 1) := mul_nonneg ht0 hq
    have hB : 0 ≤ t * ((y - 1) * t) := mul_nonneg ht0 (mul_nonneg (by linarith) ht0)
    have s1 := mul_le_mul_of_nonneg_left hden hA
    have s2 : 0 ≤ t * ((y - 1) * t) * (y * (y + 1) * (y + 2)) := mul_nonneg hB pD.le
    nlinarith [s1, s2]

/-- **Weighted AM–GM in tilt form.**  If `(k+1) p + (k-1) q ≥ ϰ(k) + ξ`, then for every real `μ`
`e^{μ+p} + e^{-μ+q} ≥ 2 e^{μ/k} e^{ξ/(2k)}`.  (The left side is the mean, with weights
`(k+1)/(2k)` and `(k-1)/(2k)`, of two exponentials whose exponents have weighted mean at least
`μ/k + ξ/(2k)`; each exponential is bounded below by its tangent line at that point.) -/
private theorem amgm_tilt {k : ℝ} (hk : 1 < k) (p q ξ : ℝ)
    (h : kap k + ξ ≤ (k + 1) * p + (k - 1) * q) (μ : ℝ) :
    2 * exp (μ / k) * exp (ξ / (2 * k)) ≤ exp (μ + p) + exp (-μ + q) := by
  have hk0 : 0 < k := by linarith
  have hk1 : 0 < k - 1 := by linarith
  have hk2 : 0 < k + 1 := by linarith
  rw [kap, Lg_sub_one, Lg] at h
  -- the two tangent points
  set u : ℝ := μ + p - (Real.log (k + 1) - Real.log k) with hu
  set v : ℝ := -μ + q + (Real.log k - Real.log (k - 1)) with hv
  set E : ℝ := μ / k + ξ / (2 * k) with hE
  have e1 : exp (μ + p) = (k + 1) / k * exp u := by
    have : exp (Real.log (k + 1) - Real.log k) = (k + 1) / k := by
      rw [Real.exp_sub, Real.exp_log hk2, Real.exp_log hk0]
    rw [← this, ← exp_add]
    congr 1
    rw [hu]; ring
  have e2 : exp (-μ + q) = (k - 1) / k * exp v := by
    have : exp (Real.log (k - 1) - Real.log k) = (k - 1) / k := by
      rw [Real.exp_sub, Real.exp_log hk1, Real.exp_log hk0]
    rw [← this, ← exp_add]
    congr 1
    rw [hv]; ring
  -- tangent line of `exp` at `E`
  have tangent : ∀ w : ℝ, exp E * (1 + (w - E)) ≤ exp w := by
    intro w
    have h2 : exp w = exp E * exp (w - E) := by rw [← exp_add]; congr 1; ring
    rw [h2]
    exact mul_le_mul_of_nonneg_left (by linarith [Real.add_one_le_exp (w - E)]) (exp_pos E).le
  have s1 := mul_le_mul_of_nonneg_left (tangent u) (by positivity : (0 : ℝ) ≤ (k + 1) / k)
  have s2 := mul_le_mul_of_nonneg_left (tangent v) (by positivity : (0 : ℝ) ≤ (k - 1) / k)
  -- the weighted mean of the two tangent points is at least `E`
  have hmean : 0 ≤ (k + 1) / k * (u - E) + (k - 1) / k * (v - E) := by
    have e : (k + 1) / k * (u - E) + (k - 1) / k * (v - E) =
        ((k + 1) * p + (k - 1) * q - ((k + 1) * (Real.log (k + 1) - Real.log k) -
          (k - 1) * (Real.log k - Real.log (k - 1)) + ξ)) / k := by
      rw [hu, hv, hE]
      field_simp
      ring
    rw [e]
    exact div_nonneg (by linarith) hk0.le
  have hsum : (k + 1) / k + (k - 1) / k = 2 := by
    field_simp
    ring
  have hEE : 2 * exp (μ / k) * exp (ξ / (2 * k)) = 2 * exp E := by
    rw [hE, exp_add]; ring
  rw [hEE, e1, e2]
  have hpos : 0 ≤ exp E := (exp_pos E).le
  nlinarith [mul_nonneg hpos hmean]

/-- `exp (phi n) = (1 + 1/n)^(n-1)` for a positive integer `n`. -/
private theorem exp_phi {n : ℕ} (hn : 1 ≤ n) : Real.exp (phi n) = (1 + 1 / (n : ℝ)) ^ (n - 1) := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn
  have h1 : (1 : ℝ) + 1 / n = ((n : ℝ) + 1) / n := by field_simp
  have hpos : (0 : ℝ) < (1 + 1 / (n : ℝ)) ^ (n - 1) := by positivity
  rw [← Real.exp_log hpos, Real.log_pow, h1, Real.log_div (by positivity) hn0.ne']
  congr 1
  unfold phi Lg
  rw [Nat.cast_sub hn, Nat.cast_one]

end LogComb

open Real Finset

/-! ### The ratio of consecutive tilted Cayley masses -/

/-- `x_k = exp (-phi k)`. -/
private theorem xcrit_eq_exp {k : ℕ} (hk : 1 ≤ k) : xcrit k = Real.exp (-phi k) := by
  have h : xcrit k * Real.exp (phi k) = 1 := by
    rw [exp_phi hk]
    exact xcrit_mul_psi hk
  rw [Real.exp_neg]
  exact eq_inv_of_mul_eq_one_left h

/-- `phi` is nondecreasing on the positive integers (`psi_mono` in logarithmic form). -/
private theorem phi_mono_nat {i j : ℕ} (hi : 1 ≤ i) (hij : i ≤ j) : phi (i : ℝ) ≤ phi (j : ℝ) := by
  refine Real.exp_le_exp.mp ?_
  rw [exp_phi hi, exp_phi (le_trans hi hij)]
  exact psi_mono hi hij

/-- The ratio of consecutive tilted Cayley numbers: `ω_{n+1} = ω_n exp (phi (n+1) - phi k)`
(`ccT_succ_mul_xcrit` in exponential form). -/
private theorem ccT_succ_exp {k : ℕ} (hk : 1 ≤ k) (n : ℕ) :
    ccT (xcrit k) (n + 1) = ccT (xcrit k) n * Real.exp (phi ((n : ℝ) + 1) - phi k) := by
  have h : ccT (xcrit k) (n + 1) * xcrit (n + 1) = xcrit k * ccT (xcrit k) n := ccT_succ_mul_xcrit
      (xcrit k) n
  have h1 := xcrit_eq_exp (k := n + 1) (by omega)
  rw [Nat.cast_add, Nat.cast_one] at h1
  have hratio : xcrit k = Real.exp (phi ((n : ℝ) + 1) - phi k) * xcrit (n + 1) := by
    rw [xcrit_eq_exp hk, h1, ← Real.exp_add]
    congr 1
    ring
  apply mul_right_cancel₀ (xcrit_pos (n + 1)).ne'
  rw [h, mul_assoc, ← hratio]
  ring

/-- `ccT_succ_exp` read downwards: `ω_n = ω_{n+1} exp (phi k - phi (n+1))`. -/
private theorem ccT_pred_exp {k : ℕ} (hk : 1 ≤ k) (n : ℕ) :
    ccT (xcrit k) n = ccT (xcrit k) (n + 1) * Real.exp (phi k - phi ((n : ℝ) + 1)) := by
  rw [ccT_succ_exp hk n, mul_assoc, ← Real.exp_add]
  have : phi ((n : ℝ) + 1) - phi k + (phi k - phi ((n : ℝ) + 1)) = 0 := by ring
  rw [this, Real.exp_zero, mul_one]

/-! ### Monotonicity and log-convexity -/

/-- `ω_k = ω_{k-1}` at the critical tilt. -/
theorem ccT_top {k : ℕ} (hk : 1 ≤ k) : ccT (xcrit k) k = ccT (xcrit k) (k - 1) := by
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
  rw [Nat.add_sub_cancel, ccT_succ_exp hk j, Nat.cast_add, Nat.cast_one, sub_self, Real.exp_zero,
    mul_one]

/-- At the critical tilt $x_k$, the tilted Cayley masses $\omega_n=c_nx_k^{\,n}$ do not increase on
the indices $0,\dots,k$: $\omega_j\le\omega_i$ for $i\le j\le k$. -/
theorem ccT_anti {k i j : ℕ} (hij : i ≤ j) (hj : j ≤ k) : ccT (xcrit k) j ≤ ccT (xcrit k) i := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ m him ih => exact le_trans (ccT_succ_le hj) (ih (by omega))

/-- For `j + 2 ≤ k` and `μ ≤ 1/(k(k+2))`: `e^μ ω_{j+1} ≤ ω_j`
(the ratio `ω_j/ω_{j+1}` is at least `exp (phi k - phi (k-1))`, and
`phi k - phi (k-1) ≥ 3/(2k(k+1)) ≥ 1/(k(k+2))`). -/
theorem ccT_step_down {k j : ℕ} (hk : 3 ≤ k) (hj : j + 2 ≤ k) {μ : ℝ}
    (hμ : μ ≤ 1 / ((k : ℝ) * ((k : ℝ) + 2))) : Real.exp μ * ccT (xcrit k) (j + 1)
        ≤ ccT (xcrit k) j := by
  have hk1 : 1 ≤ k := by omega
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have h1 := phi_mono_nat (i := j + 1) (j := k - 1) (by omega) (by omega)
  rw [Nat.cast_add, Nat.cast_one, Nat.cast_sub hk1, Nat.cast_one] at h1
  have h2 := phi_step_lb (y := (k : ℝ)) (by linarith)
  have h3 : 1 / ((k : ℝ) * ((k : ℝ) + 2)) ≤ 3 / (2 * (k : ℝ) * ((k : ℝ) + 1)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    nlinarith
  have h5 : Real.exp μ ≤ Real.exp (phi k - phi ((j : ℝ) + 1)) :=
    Real.exp_le_exp.mpr (by linarith)
  rw [ccT_pred_exp hk1 j, mul_comm]
  exact mul_le_mul_of_nonneg_left h5 (ccT_pos (xcrit_pos k) (j + 1)).le

/-- Log-convexity of `ω`: for `a ≤ m`, `ω_{ρ+a} ω_{ρ+m-a} ≤ ω_ρ ω_{ρ+m}`. -/
theorem ccT_logconvex (k : ℕ) {ρ m a : ℕ} (ha : a ≤ m) :
    ccT (xcrit k) (ρ + a) * ccT (xcrit k) (ρ + m - a) ≤ ccT (xcrit k) ρ
        * ccT (xcrit k) (ρ + m) := by
  have h := cay_logconvex (u := ρ + 1) (v := ρ + m - a + 1) (c := a) (by omega) (by omega)
  have e1 : ρ + 1 + a = ρ + a + 1 := by omega
  have e2 : ρ + m - a + 1 + a = ρ + m + 1 := by omega
  rw [e1, e2] at h
  have hx : xcrit k ^ (ρ + a) * xcrit k ^ (ρ + m - a) = xcrit k ^ ρ * xcrit k ^ (ρ + m) := by
    rw [← pow_add, ← pow_add]
    congr 1
    omega
  have hxpos : 0 ≤ xcrit k ^ ρ * xcrit k ^ (ρ + m) := by
    have := xcrit_pos k
    positivity
  show cay (ρ + a + 1) * xcrit k ^ (ρ + a) * (cay (ρ + m - a + 1) * xcrit k ^ (ρ + m - a)) ≤
    cay (ρ + 1) * xcrit k ^ ρ * (cay (ρ + m + 1) * xcrit k ^ (ρ + m))
  calc cay (ρ + a + 1) * xcrit k ^ (ρ + a) * (cay (ρ + m - a + 1) * xcrit k ^ (ρ + m - a))
      = (xcrit k ^ ρ * xcrit k ^ (ρ + m)) * (cay (ρ + a + 1) * cay (ρ + m - a + 1)) := by
        rw [← hx]
        ring
    _ ≤ (xcrit k ^ ρ * xcrit k ^ (ρ + m)) * (cay (ρ + 1) * cay (ρ + m + 1)) :=
        mul_le_mul_of_nonneg_left h hxpos
    _ = cay (ρ + 1) * xcrit k ^ ρ * (cay (ρ + m + 1) * xcrit k ^ (ρ + m)) := by ring

/-! ### Tilted convexity below the top -/

/-- The exponent inequality behind `ccT_tilt_mid`: for `1 ≤ n ≤ k-1`,
`(k+1) (phi (n+1) - phi k) + (k-1) (phi k - phi n) ≥ ϰ(k)`.  The left side is nonincreasing in `n`
(by `delta_ratio` and `phi_step_lb`), and at `n = k-1` the difference of the two sides is
`(k-3) (k log (1+1/k) - (k-1) log (1+1/(k-1)))`, nonnegative by `chi_mono`. -/
private theorem Xi_nonneg {k n : ℕ} (hk : 3 ≤ k) (hn1 : 1 ≤ n) (hn : n + 1 ≤ k) :
    kap k ≤ ((k : ℝ) + 1) * (phi ((n : ℝ) + 1) - phi k) + ((k : ℝ) - 1) * (phi k - phi n) := by
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  -- `G m = (k+1) phi (m+1) - (k-1) phi m` is nonincreasing for `1 ≤ m`, `m + 2 ≤ k`
  have hstep : ∀ m : ℕ, 1 ≤ m → m + 2 ≤ k →
      ((k : ℝ) + 1) * phi ((m : ℝ) + 1 + 1) - ((k : ℝ) - 1) * phi ((m : ℝ) + 1) ≤
        ((k : ℝ) + 1) * phi ((m : ℝ) + 1) - ((k : ℝ) - 1) * phi m := by
    intro m hm1 hm2
    have hm : (1 : ℝ) ≤ m := by exact_mod_cast hm1
    have hmk : (m : ℝ) + 2 ≤ k := by exact_mod_cast hm2
    have h1 := delta_ratio (y := (m : ℝ) + 1) (by linarith)
    have h2 := phi_step_lb (y := (m : ℝ) + 1) (by linarith)
    rw [add_sub_cancel_right] at h1 h2
    have hδ : 0 ≤ phi ((m : ℝ) + 1) - phi m := le_trans (by positivity) h2
    have h3 : ((k : ℝ) + 1) * ((m : ℝ) + 1) ≤ ((k : ℝ) - 1) * ((m : ℝ) + 1 + 2) := by nlinarith
    have h4 := mul_le_mul_of_nonneg_left h1 (by linarith : (0 : ℝ) ≤ (k : ℝ) + 1)
    have h5 := mul_le_mul_of_nonneg_right h3 hδ
    have h6 : ((m : ℝ) + 1 + 2) *
        (((k : ℝ) + 1) * (phi ((m : ℝ) + 1 + 1) - phi ((m : ℝ) + 1)) -
          ((k : ℝ) - 1) * (phi ((m : ℝ) + 1) - phi m)) ≤ ((m : ℝ) + 1 + 2) * 0 := by
      linarith
    have h8 := le_of_mul_le_mul_left h6 (by linarith : (0 : ℝ) < (m : ℝ) + 1 + 2)
    linarith
  have hmono : ∀ m : ℕ, n ≤ m → m + 1 ≤ k →
      ((k : ℝ) + 1) * phi ((m : ℝ) + 1) - ((k : ℝ) - 1) * phi m ≤
        ((k : ℝ) + 1) * phi ((n : ℝ) + 1) - ((k : ℝ) - 1) * phi n := by
    intro m hnm
    induction m, hnm using Nat.le_induction with
    | base => intro _; exact le_rfl
    | succ m hnm ih =>
      intro hm
      have h1 := hstep m (le_trans hn1 hnm) (by omega)
      have h2 := ih (by omega)
      rw [Nat.cast_add, Nat.cast_one]
      linarith
  have hkm := hmono (k - 1) (by omega) (by omega)
  have ek : ((k - 1 : ℕ) : ℝ) = (k : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega), Nat.cast_one]
  rw [ek, sub_add_cancel] at hkm
  -- `k Lg k ≥ (k-1) Lg (k-1)`: `chi_mono` in logarithmic form
  have hpsi : 0 ≤ (k : ℝ) * Lg k - ((k : ℝ) - 1) * Lg ((k : ℝ) - 1) := by
    have hk0 : (0 : ℝ) < k := by linarith
    have hk1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
    have hA : (0 : ℝ) < (k : ℝ) - 1 + 1 := by linarith
    have hB : (0 : ℝ) < (k : ℝ) + 1 := by linarith
    have h := chi_mono (i := k - 1) (j := k) (by omega) (by omega)
    rw [ek, one_add_div hk1.ne', one_add_div hk0.ne'] at h
    have hl := Real.log_le_log (pow_pos (div_pos hA hk1) _) h
    rw [Real.log_pow, Real.log_pow, ek, Real.log_div hA.ne' hk1.ne',
      Real.log_div hB.ne' hk0.ne'] at hl
    unfold Lg
    linarith
  have hid : ((k : ℝ) + 1) * phi k - ((k : ℝ) - 1) * phi ((k : ℝ) - 1) - 2 * phi k - kap k =
      ((k : ℝ) - 3) * ((k : ℝ) * Lg k - ((k : ℝ) - 1) * Lg ((k : ℝ) - 1)) := by
    unfold phi kap
    ring
  have h3 : 0 ≤ ((k : ℝ) - 3) * ((k : ℝ) * Lg k - ((k : ℝ) - 1) * Lg ((k : ℝ) - 1)) :=
    mul_nonneg (by linarith) hpsi
  linarith

/-- **Tilted convexity of `ω` below the top**: for `j + 2 ≤ k` and every real `μ`,
`2 e^{μ/k} ω_{j+1} ≤ e^μ ω_{j+2} + e^{-μ} ω_j`. -/
theorem ccT_tilt_mid {k j : ℕ} (hk : 3 ≤ k) (hj : j + 2 ≤ k) (μ : ℝ) :
    2 * exp (μ / k) * ccT (xcrit k) (j + 1) ≤ exp μ * ccT (xcrit k) (j + 2) + exp (-μ)
        * ccT (xcrit k) j := by
  have hk1 : 1 ≤ k := by omega
  have hkr : (1 : ℝ) < k := by exact_mod_cast (by omega : 1 < k)
  have h1 : ccT (xcrit k) (j + 2) = ccT (xcrit k) (j + 1)
      * exp (phi ((j : ℝ) + 1 + 1) - phi k) := by
    have h := ccT_succ_exp hk1 (j + 1)
    rw [Nat.cast_add, Nat.cast_one] at h
    exact h
  have hXi := Xi_nonneg (k := k) (n := j + 1) hk (by omega) (by omega)
  rw [Nat.cast_add, Nat.cast_one] at hXi
  have ham := amgm_tilt hkr (phi ((j : ℝ) + 1 + 1) - phi k) (phi k - phi ((j : ℝ) + 1)) 0
    (by linarith) μ
  rw [zero_div, exp_zero, mul_one] at ham
  have hpos := (ccT_pos (xcrit_pos k) (j + 1)).le
  calc 2 * exp (μ / k) * ccT (xcrit k) (j + 1) = ccT (xcrit k) (j + 1)
      * (2 * exp (μ / k)) := by ring
    _ ≤ ccT (xcrit k) (j + 1) * (exp (μ + (phi ((j : ℝ) + 1 + 1) - phi k)) +
          exp (-μ + (phi k - phi ((j : ℝ) + 1)))) := mul_le_mul_of_nonneg_left ham hpos
    _ = exp μ * (ccT (xcrit k) (j + 1) * exp (phi ((j : ℝ) + 1 + 1) - phi k)) +
          exp (-μ) * (ccT (xcrit k) (j + 1) * exp (phi k - phi ((j : ℝ) + 1))) := by
        rw [exp_add, exp_add]; ring
    _ = exp μ * ccT (xcrit k) (j + 2) + exp (-μ) * ccT (xcrit k) j := by
        rw [← h1, ← ccT_pred_exp hk1 j]

/-! ### Tilted convexity at the top -/

/-- The surplus of the tilted convexity at the top, with `ω_{k-1} = ω_k` and
`ω_{k+1} = ω_k e^ζ`, `ζ = phi (k+1) - phi k`. -/
private theorem ccT_top_surplus {k : ℕ} (hk : 1 ≤ k) (μ : ℝ) :
    exp μ * ccT (xcrit k) (k + 1) + exp (-μ) * ccT (xcrit k) (k - 1) - 2 * exp (μ / k)
        * ccT (xcrit k) k =
      ccT (xcrit k) k * (exp (μ + (phi ((k : ℝ) + 1) - phi k)) + exp (-μ) - 2 * exp (μ / k)) := by
  rw [ccT_succ_exp hk k, ← ccT_top hk, exp_add]
  ring

/-- For every real `μ`,
`e^μ ω_{k+1} + e^{-μ} ω_{k-1} - 2 e^{μ/k} ω_k ≥ ω_k e^{μ/k} · (k²-2k-1)/(2k(k+1)(k+2)) / k`
(weighted AM–GM with `p = ζ`, `q = 0`, and `Lam_lb`). -/
theorem ccT_tilt_top {k : ℕ} (hk : 3 ≤ k) (μ : ℝ) :
    ccT (xcrit k) k * (exp (μ / k) *
        (((k : ℝ) ^ 2 - 2 * k - 1) / (2 * (k : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 2)) / k)) ≤
      exp μ * ccT (xcrit k) (k + 1) + exp (-μ) * ccT (xcrit k) (k - 1) - 2 * exp (μ / k)
          * ccT (xcrit k) k := by
  have hk1 : 1 ≤ k := by omega
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hkr : (1 : ℝ) < k := by linarith
  have hk0 : (0 : ℝ) < k := by linarith
  have hLam := Lam_lb (y := (k : ℝ)) hk3
  have ham := amgm_tilt hkr (phi ((k : ℝ) + 1) - phi k) 0
    (((k : ℝ) + 1) * (phi ((k : ℝ) + 1) - phi k) - kap k) (by linarith) μ
  rw [add_zero] at ham
  have hexp := Real.add_one_le_exp
    ((((k : ℝ) + 1) * (phi ((k : ℝ) + 1) - phi k) - kap k) / (2 * k))
  have hpos : 0 ≤ 2 * exp (μ / k) := by positivity
  have h1 := mul_le_mul_of_nonneg_left hexp hpos
  have h2 : ((k : ℝ) ^ 2 - 2 * k - 1) / (2 * (k : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 2)) / (2 * k) ≤
      (((k : ℝ) + 1) * (phi ((k : ℝ) + 1) - phi k) - kap k) / (2 * k) :=
    div_le_div_of_nonneg_right hLam (by positivity)
  have h3 := mul_le_mul_of_nonneg_left h2 hpos
  have e4 : 2 * exp (μ / k) *
      (((k : ℝ) ^ 2 - 2 * k - 1) / (2 * (k : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 2)) / (2 * k)) =
      exp (μ / k) *
        (((k : ℝ) ^ 2 - 2 * k - 1) / (2 * (k : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 2)) / k) := by
    field_simp
  rw [ccT_top_surplus hk1]
  exact mul_le_mul_of_nonneg_left (by rw [← e4]; linarith) (ccT_pos (xcrit_pos k) k).le

/-- For every real `μ`,
`e^μ ω_{k+1} + e^{-μ} ω_{k-1} - 2 e^{μ/k} ω_k ≥ ω_k (3/(2(k+1)(k+2)) - 2 (e^{μ/k} - 1))`
(from `e^x ≥ 1 + x` and `ζ ≥ 3/(2(k+1)(k+2))`). -/
theorem ccT_tilt_top' {k : ℕ} (hk : 3 ≤ k) (μ : ℝ) :
    ccT (xcrit k) k * (3 / (2 * ((k : ℝ) + 1) * ((k : ℝ) + 2)) - 2 * (exp (μ / k) - 1)) ≤
      exp μ * ccT (xcrit k) (k + 1) + exp (-μ) * ccT (xcrit k) (k - 1) - 2 * exp (μ / k)
          * ccT (xcrit k) k := by
  have hk1 : 1 ≤ k := by omega
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hζ := phi_step_lb (y := (k : ℝ) + 1) (by linarith)
  rw [add_sub_cancel_right,
    show (2 : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 1 + 1) = 2 * ((k : ℝ) + 1) * ((k : ℝ) + 2) by ring]
    at hζ
  have ha := Real.add_one_le_exp (μ + (phi ((k : ℝ) + 1) - phi k))
  have hb := Real.add_one_le_exp (-μ)
  rw [ccT_top_surplus hk1]
  exact mul_le_mul_of_nonneg_left (by linarith) (ccT_pos (xcrit_pos k) k).le

/-- The triple `(ω_{k-1}, ω_k, ω_{k+1})` has property K at `k`. -/
theorem TK_ccT_top {k : ℕ} (hk : 3 ≤ k) : TK k (ccT (xcrit k) (k - 1)) (ccT (xcrit k) k)
    (ccT (xcrit k) (k + 1)) := by
  intro μ _
  have hk1 : 1 ≤ k := by omega
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have h := ccT_tilt_top hk μ
  have hq : (0 : ℝ) ≤ (k : ℝ) ^ 2 - 2 * k - 1 := by nlinarith
  have hnn : 0 ≤ ccT (xcrit k) k * (exp (μ / k) *
      (((k : ℝ) ^ 2 - 2 * k - 1) / (2 * (k : ℝ) * ((k : ℝ) + 1) * ((k : ℝ) + 2)) / k)) := by
    have := (ccT_pos (xcrit_pos k) k).le
    positivity
  linarith

end Parking.FirstLayer
