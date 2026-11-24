import Parking.ChainColumn.Resolvent
import Parking.Crossing.Bounds
import Mathlib.Analysis.Complex.ExponentialBounds

/-!
# Elementary bounds for the persistence argument

Notation: `g(i+1) = ε_{i+2}/ε_{i+1}` is the step ratio `gs i` of the prime kernel,
`γ_k = (1 + 1/k)^(k-2)`, `x = 1/γ_k`, `κ_m = x^m ε_m` the tilted kernel and `f` the frozen kernel.

* `gs_le_exp`      : `g(i+1) ≤ exp (1 - 3/(2(i+2)))` (`i ≥ 1`);
* `gam_ge_exp`     : `γ_k ≥ exp (1 - 5/(2k))`;
* `eps_succ_le_gam`, `kapx_succ_le`, `kapx_cross` : `ε_{m+1} ≤ γ_k ε_m` for `m + 1 ≤ 3k/5`, so
  that the tilted kernel is nonincreasing up to `3k/5`; it is log-convex;
* `Fk_anti`        : `(k+ρ) κ_ρ` is nonincreasing for `ρ ≤ 0.47 k` (`k ≥ 42`);
* `theta_f_le`     : the profile bound `(g(m) - γ_k) f_m ≤ 1.05 c₀ / k^{5/2}` of the far weights;
* `tail_sqrt`      : a telescoping lower bound for sums of `j^{-3/2}`;
* `exp_41_60`, `exp_4_3`, `exp_7_3` : three values of the exponential;
* `near_term_le`   : the bound `(N/2) ε_{t+1} x^t ≤ λ L e^{5σ/2} / (2σ √(2πσk))` of the near
  term, for `σ k ≤ t ≤ σ k + 1` and `0 ≤ N ≤ L k`;
* `P1_le`          : the comparison of this bound with a number `p`.
-/

namespace Parking

open Finset

/-! ### The step ratio and `γ_k` -/

private theorem gs_le_exp {i : ℕ} (hi : 1 ≤ i) : gs i ≤ Real.exp (1 - 3 / (2 * ((i : ℝ) + 2))) := by
  have ha1 : (1 : ℝ) ≤ (i : ℝ) := by exact_mod_cast hi
  have ha : (0 : ℝ) < (i : ℝ) := by linarith
  have ha0 : (i : ℝ) ≠ 0 := ha.ne'
  have hu : Real.log (1 + 1 / (i : ℝ))
      ≤ 1 / (i : ℝ) - (1 / (i : ℝ)) ^ 2 / 2 + (1 / (i : ℝ)) ^ 3 / 3 :=
    log_one_add_le3 (by positivity)
  have hw : 1 / ((i : ℝ) + 1) - (1 / ((i : ℝ) + 1)) ^ 2 / 2
      ≤ Real.log (1 + 1 / ((i : ℝ) + 1)) :=
    log_one_add_ge2 (by positivity)
  have e1 : (1 + 1 / (i : ℝ)) ^ i = Real.exp ((i : ℝ) * Real.log (1 + 1 / (i : ℝ))) := by
    rw [Real.exp_nat_mul, Real.exp_log (by positivity)]
  have e2 : ((i : ℝ) + 1) / ((i : ℝ) + 2) = Real.exp (-Real.log (1 + 1 / ((i : ℝ) + 1))) := by
    rw [Real.exp_neg, Real.exp_log (by positivity)]
    field
  have key : 1 - 3 / (2 * ((i : ℝ) + 2))
      - (-(1 / ((i : ℝ) + 1) - (1 / ((i : ℝ) + 1)) ^ 2 / 2)
          + (i : ℝ) * (1 / (i : ℝ) - (1 / (i : ℝ)) ^ 2 / 2 + (1 / (i : ℝ)) ^ 3 / 3))
      = (7 * (i : ℝ) ^ 3 + 4 * (i : ℝ) ^ 2 - 4 * (i : ℝ) - 4)
          / (6 * (i : ℝ) ^ 2 * ((i : ℝ) + 1) ^ 2 * ((i : ℝ) + 2)) := by
    field
  have hnum : (0 : ℝ) ≤ 7 * (i : ℝ) ^ 3 + 4 * (i : ℝ) ^ 2 - 4 * (i : ℝ) - 4 := by
    nlinarith [mul_nonneg (sub_nonneg.2 ha1)
      (by positivity : (0 : ℝ) ≤ 7 * (i : ℝ) ^ 2 + 11 * (i : ℝ) + 7)]
  have hq : (0 : ℝ) ≤ (7 * (i : ℝ) ^ 3 + 4 * (i : ℝ) ^ 2 - 4 * (i : ℝ) - 4)
      / (6 * (i : ℝ) ^ 2 * ((i : ℝ) + 1) ^ 2 * ((i : ℝ) + 2)) :=
    div_nonneg hnum (by positivity)
  have hmul := mul_le_mul_of_nonneg_left hu ha.le
  unfold gs
  rw [e1, e2, ← Real.exp_add]
  exact Real.exp_le_exp.mpr (by linarith)

private theorem gam_ge_exp {k : ℕ} (hk : 2 ≤ k) : Real.exp (1 - 5 / (2 * (k : ℝ))) ≤ gam k := by
  have h := (xk_bounds hk).2
  have e : Real.exp (1 - 5 / (2 * (k : ℝ))) * (Real.exp (-1) * Real.exp (abar k)) = 1 := by
    unfold abar
    rw [← Real.exp_add, ← Real.exp_add]
    have h0 : 1 - 5 / (2 * (k : ℝ)) + (-1 + 5 / (2 * (k : ℝ))) = 0 := by ring
    rw [h0, Real.exp_zero]
  have h1 : Real.exp (1 - 5 / (2 * (k : ℝ))) * xk k ≤ 1 := by
    calc Real.exp (1 - 5 / (2 * (k : ℝ))) * xk k
        ≤ Real.exp (1 - 5 / (2 * (k : ℝ))) * (Real.exp (-1) * Real.exp (abar k)) :=
          mul_le_mul_of_nonneg_left h (Real.exp_pos _).le
      _ = 1 := e
  have h2 := mul_le_mul_of_nonneg_right h1 (gam_pos k).le
  have h3 : Real.exp (1 - 5 / (2 * (k : ℝ))) * xk k * gam k
      = Real.exp (1 - 5 / (2 * (k : ℝ))) := by
    rw [mul_assoc, CrossCrit.xk_mul_gam, mul_one]
  linarith

private theorem one_le_gam (k : ℕ) : 1 ≤ gam k := by
  unfold gam
  have h : (0 : ℝ) ≤ 1 / (k : ℝ) := by positivity
  exact one_le_pow₀ (by linarith)

private theorem gs_le_gam {k i : ℕ} (hk : 2 ≤ k) (h : 5 * (i + 2) ≤ 3 * k) : gs i ≤ gam k := by
  rcases Nat.eq_zero_or_pos i with rfl | hi
  · rw [gs_zero]
    linarith [one_le_gam k]
  · have hK2 : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
    have hK : (0 : ℝ) < (k : ℝ) := by linarith
    have hh : (5 : ℝ) * ((i : ℝ) + 2) ≤ 3 * (k : ℝ) := by exact_mod_cast h
    have hle : 5 / (2 * (k : ℝ)) ≤ 3 / (2 * ((i : ℝ) + 2)) := by
      rw [div_le_div_iff₀ (by positivity) (by positivity)]
      nlinarith
    exact (gs_le_exp hi).trans ((Real.exp_le_exp.mpr (by linarith)).trans (gam_ge_exp hk))

/-- For $k \ge 2$ and $1 \le m$ with $m + 1 \le \frac35k$: $\varepsilon_{m+1} \le
\gamma_k\,\varepsilon_m$, where $\varepsilon_m = (m-1)^{m-1}/m!$ and $\gamma_k = (1+1/k)^{k-2}$. -/
theorem eps_succ_le_gam {k m : ℕ} (hk : 2 ≤ k) (hm : 1 ≤ m) (h : 5 * (m + 1) ≤ 3 * k) :
    eps (m + 1) ≤ gam k * eps m := by
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  rw [eps_step i]
  exact mul_le_mul_of_nonneg_right (gs_le_gam hk (by omega)) (eps_nonneg _)

/-- At the diagonal tilt $x = 1/\gamma_k$ the tilted kernel $\kappa_m = x^m\varepsilon_m$ is
positive for every $m \ge 1$. -/
theorem kapx_pos (k : ℕ) {m : ℕ} (hm : 1 ≤ m) : 0 < kapx k m :=
  mul_pos (pow_pos (CrossCrit.xk_pos k) m) (eps_pos hm)

/-- At the diagonal tilt $x = 1/\gamma_k$ the tilted kernel $\kappa_m = x^m\varepsilon_m$ satisfies
$\kappa_{m+1} \le \kappa_m$ for $1 \le m$, $m + 1 \le \frac35k$ ($k \ge 2$). -/
theorem kapx_succ_le {k m : ℕ} (hk : 2 ≤ k) (hm : 1 ≤ m) (h : 5 * (m + 1) ≤ 3 * k) :
    kapx k (m + 1) ≤ kapx k m := by
  have h1 := eps_succ_le_gam hk hm h
  have hx := CrossCrit.xk_pos k
  have hxm : 0 ≤ xk k ^ m * xk k := mul_nonneg (pow_nonneg hx.le m) hx.le
  unfold kapx
  calc xk k ^ (m + 1) * eps (m + 1) = xk k ^ m * xk k * eps (m + 1) := by rw [pow_succ]
    _ ≤ xk k ^ m * xk k * (gam k * eps m) := mul_le_mul_of_nonneg_left h1 hxm
    _ = xk k ^ m * eps m * (xk k * gam k) := by ring
    _ = xk k ^ m * eps m := by rw [CrossCrit.xk_mul_gam, mul_one]

/-- At the diagonal tilt, the tilted kernel $\kappa_m = x^m\varepsilon_m$ satisfies
$\kappa_{m+t}\,\kappa_r \le \kappa_{r+t}\,\kappa_m$ for $1 \le m \le r$ and every $t \ge 0$. -/
theorem kapx_cross {k m r : ℕ} (hm : 1 ≤ m) (hmr : m ≤ r) (t : ℕ) :
    kapx k (m + t) * kapx k r ≤ kapx k (r + t) * kapx k m := by
  have h := eps_cross hm hmr t
  have hp : 0 ≤ xk k ^ (m + t) * xk k ^ r :=
    mul_nonneg (pow_nonneg (CrossCrit.xk_pos k).le _) (pow_nonneg (CrossCrit.xk_pos k).le _)
  unfold kapx
  calc xk k ^ (m + t) * eps (m + t) * (xk k ^ r * eps r)
      = xk k ^ (m + t) * xk k ^ r * (eps (m + t) * eps r) := by ring
    _ ≤ xk k ^ (m + t) * xk k ^ r * (eps m * eps (r + t)) := mul_le_mul_of_nonneg_left h hp
    _ = xk k ^ (r + t) * eps (r + t) * (xk k ^ m * eps m) := by ring

/-! ### The two-point condition: `(k+ρ) κ_ρ` is nonincreasing -/

private theorem Fk_step {k ρ : ℕ} (hk : 42 ≤ k) (hρ : 1 ≤ ρ) (h : 100 * (ρ + 1) ≤ 47 * k) :
    ((k : ℝ) + ((ρ : ℝ) + 1)) * kapx k (ρ + 1) ≤ ((k : ℝ) + (ρ : ℝ)) * kapx k ρ := by
  obtain ⟨i, rfl⟩ : ∃ i, ρ = i + 1 := ⟨ρ - 1, by omega⟩
  have hK42 : (42 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK : (0 : ℝ) < (k : ℝ) := by linarith
  have hK0 : (k : ℝ) ≠ 0 := hK.ne'
  have hI : (0 : ℝ) ≤ (i : ℝ) := Nat.cast_nonneg i
  have hx := CrossCrit.xk_pos k
  have hKR : (0 : ℝ) < (k : ℝ) + ((i : ℝ) + 1) := by linarith
  have hKR0 : (k : ℝ) + ((i : ℝ) + 1) ≠ 0 := hKR.ne'
  -- the main inequality `(k+ρ+1) g ≤ (k+ρ) γ`
  have hA : ((k : ℝ) + ((i : ℝ) + 1) + 1) * gs i ≤ ((k : ℝ) + ((i : ℝ) + 1)) * gam k := by
    rcases Nat.eq_zero_or_pos i with rfl | hi
    · rw [gs_zero, Nat.cast_zero]
      have hg := one_le_gam k
      have h1 : ((k : ℝ) + (0 + 1)) * 1 ≤ ((k : ℝ) + (0 + 1)) * gam k :=
        mul_le_mul_of_nonneg_left hg (by linarith)
      linarith
    · have hh : (100 : ℝ) * ((i : ℝ) + 1 + 1) ≤ 47 * (k : ℝ) := by exact_mod_cast h
      have hS0 : (0 : ℝ) ≤ 47 * (k : ℝ) - 100 * ((i : ℝ) + 1 + 1) := by linarith
      have hR0 : (0 : ℝ) ≤ (i : ℝ) + 1 := by linarith
      have hpoly : 5 * ((i : ℝ) + 1) ^ 2 + (4 * (k : ℝ) + 5) * ((i : ℝ) + 1) + 7 * (k : ℝ)
          ≤ 3 * (k : ℝ) ^ 2 := by
        nlinarith [mul_nonneg hK.le (sub_nonneg.2 hK42), mul_nonneg hS0 hR0,
          mul_nonneg hK.le hS0]
      have key : 3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ)) - 1 / ((k : ℝ) + ((i : ℝ) + 1))
          = (3 * (k : ℝ) ^ 2 - 5 * ((i : ℝ) + 1) ^ 2 - (4 * (k : ℝ) + 5) * ((i : ℝ) + 1)
              - 7 * (k : ℝ))
            / (2 * (k : ℝ) * ((i : ℝ) + 2) * ((k : ℝ) + ((i : ℝ) + 1))) := by
        field
      have hq : (0 : ℝ) ≤ (3 * (k : ℝ) ^ 2 - 5 * ((i : ℝ) + 1) ^ 2
            - (4 * (k : ℝ) + 5) * ((i : ℝ) + 1) - 7 * (k : ℝ))
          / (2 * (k : ℝ) * ((i : ℝ) + 2) * ((k : ℝ) + ((i : ℝ) + 1))) :=
        div_nonneg (by linarith) (by positivity)
      have hδ : 1 / ((k : ℝ) + ((i : ℝ) + 1))
          ≤ 3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ)) := by linarith
      have h1 : 1 + (3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ)))
          ≤ Real.exp (3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ))) := by
        linarith [Real.add_one_le_exp (3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ)))]
      have h2 : Real.exp (1 - 5 / (2 * (k : ℝ)))
          = Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
            * Real.exp (3 / (2 * ((i : ℝ) + 2)) - 5 / (2 * (k : ℝ))) := by
        rw [← Real.exp_add]
        congr 1
        ring
      have hexp : Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
            * (1 + 1 / ((k : ℝ) + ((i : ℝ) + 1)))
          ≤ Real.exp (1 - 5 / (2 * (k : ℝ))) := by
        rw [h2]
        exact mul_le_mul_of_nonneg_left (by linarith) (Real.exp_pos _).le
      calc ((k : ℝ) + ((i : ℝ) + 1) + 1) * gs i
          ≤ ((k : ℝ) + ((i : ℝ) + 1) + 1) * Real.exp (1 - 3 / (2 * ((i : ℝ) + 2))) :=
            mul_le_mul_of_nonneg_left (gs_le_exp hi) (by linarith)
        _ = ((k : ℝ) + ((i : ℝ) + 1)) * (Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
              * (1 + 1 / ((k : ℝ) + ((i : ℝ) + 1)))) := by
            field
        _ ≤ ((k : ℝ) + ((i : ℝ) + 1)) * Real.exp (1 - 5 / (2 * (k : ℝ))) :=
            mul_le_mul_of_nonneg_left hexp hKR.le
        _ ≤ ((k : ℝ) + ((i : ℝ) + 1)) * gam k :=
            mul_le_mul_of_nonneg_left (gam_ge_exp (by omega)) hKR.le
  have hnn : 0 ≤ xk k ^ (i + 1) * xk k * eps (i + 1) :=
    mul_nonneg (mul_nonneg (pow_nonneg hx.le _) hx.le) (eps_nonneg _)
  unfold kapx
  rw [eps_step i, Nat.cast_add, Nat.cast_one, pow_succ (xk k) (i + 1)]
  calc ((k : ℝ) + ((i : ℝ) + 1 + 1)) * (xk k ^ (i + 1) * xk k * (gs i * eps (i + 1)))
      = (((k : ℝ) + ((i : ℝ) + 1) + 1) * gs i) * (xk k ^ (i + 1) * xk k * eps (i + 1)) := by ring
    _ ≤ (((k : ℝ) + ((i : ℝ) + 1)) * gam k) * (xk k ^ (i + 1) * xk k * eps (i + 1)) :=
        mul_le_mul_of_nonneg_right hA hnn
    _ = ((k : ℝ) + ((i : ℝ) + 1)) * (xk k ^ (i + 1) * eps (i + 1)) * (xk k * gam k) := by ring
    _ = ((k : ℝ) + ((i : ℝ) + 1)) * (xk k ^ (i + 1) * eps (i + 1)) := by
        rw [CrossCrit.xk_mul_gam, mul_one]

/-- For $k \ge 42$ the quantity $(k+\rho)\,\kappa_\rho$, with $\kappa_\rho =
\varepsilon_\rho/\gamma_k^\rho$ the tilted kernel at the diagonal tilt, is nonincreasing in
$\rho$ on the range $1 \le \rho \le 0.47k$. -/
theorem Fk_anti {k a b : ℕ} (hk : 42 ≤ k) (ha : 1 ≤ a) (hab : a ≤ b) (hb : 100 * b ≤ 47 * k) :
    ((k : ℝ) + (b : ℝ)) * kapx k b ≤ ((k : ℝ) + (a : ℝ)) * kapx k a := by
  induction b, hab using Nat.le_induction with
  | base => exact le_rfl
  | succ c hac ih =>
    have h1 := ih (by omega)
    have h2 := Fk_step (ρ := c) hk (by omega) hb
    rw [Nat.cast_add, Nat.cast_one]
    exact h2.trans h1

/-! ### Stirling-type bounds -/

/-- Stirling's bound for the prime kernel: `e^{-t} ε_{t+1} ≤ 1 / ((t+1) √(2πt))` for `t ≥ 1`. -/
private theorem exp_neg_mul_eps_le {t : ℕ} (ht : 1 ≤ t) :
    Real.exp (-1) ^ t * eps (t + 1) ≤ 1 / (((t : ℝ) + 1) * Real.sqrt (2 * Real.pi * t)) := by
  have hT0 : (0 : ℝ) < (t : ℝ) := by exact_mod_cast ht
  have hT : (0 : ℝ) < (t : ℝ) + 1 := by linarith
  have hs : 0 < Real.sqrt (2 * Real.pi * t) :=
    Real.sqrt_pos.2 (mul_pos (mul_pos two_pos Real.pi_pos) hT0)
  have hs0 : Real.sqrt (2 * Real.pi * t) ≠ 0 := hs.ne'
  have hT1 : ((t : ℝ) + 1) ≠ 0 := hT.ne'
  have h1 := poissonMass_le ht
  unfold poissonMass at h1
  rw [exp_neg_nat] at h1
  have h5 : eps (t + 1) = ren t / ((t : ℝ) + 1) := by
    rw [eq_div_iff hT1, mul_comm]
    exact mul_eps t
  calc Real.exp (-1) ^ t * eps (t + 1) = Real.exp (-1) ^ t * ren t / ((t : ℝ) + 1) := by
        rw [h5]
        ring
    _ ≤ 1 / Real.sqrt (2 * Real.pi * t) / ((t : ℝ) + 1) := div_le_div_of_nonneg_right h1 hT.le
    _ = 1 / (((t : ℝ) + 1) * Real.sqrt (2 * Real.pi * t)) := by field

/-- `ε_{t+1} x^t ≤ exp (5t/(2k)) / ((t+1) √(2πt))`. -/
private theorem psi_le {k t : ℕ} (hk : 2 ≤ k) (ht : 1 ≤ t) :
    eps (t + 1) * xk k ^ t
      ≤ Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) / (((t : ℝ) + 1) * Real.sqrt (2 * Real.pi * t)) := by
  have h3 : xk k ^ t ≤ Real.exp (-1) ^ t * Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) := by
    have eb : Real.exp (abar k) ^ t = Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) := by
      rw [← Real.exp_nat_mul]
      congr 1
      unfold abar
      ring
    rw [← eb, ← mul_pow]
    exact pow_le_pow_left₀ (CrossCrit.xk_pos k).le (xk_bounds hk).2 t
  calc eps (t + 1) * xk k ^ t
      ≤ eps (t + 1) * (Real.exp (-1) ^ t * Real.exp (5 * (t : ℝ) / (2 * (k : ℝ)))) :=
        mul_le_mul_of_nonneg_left h3 (eps_nonneg _)
    _ = Real.exp (-1) ^ t * eps (t + 1) * Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) := by ring
    _ ≤ 1 / (((t : ℝ) + 1) * Real.sqrt (2 * Real.pi * t))
          * Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) :=
        mul_le_mul_of_nonneg_right (exp_neg_mul_eps_le ht) (Real.exp_pos _).le
    _ = Real.exp (5 * (t : ℝ) / (2 * (k : ℝ)))
          / (((t : ℝ) + 1) * Real.sqrt (2 * Real.pi * t)) := by ring

/-- `f_{j+1} ≤ e^{-1} / ((j+1) √(2πj))` for `j ≥ 1`. -/
private theorem fker_le {j : ℕ} (hj : 1 ≤ j) :
    fker (j + 1) ≤ Real.exp (-1) / (((j : ℝ) + 1) * Real.sqrt (2 * Real.pi * j)) := by
  rw [fker_of_two_le (by omega : 2 ≤ j + 1), pow_succ]
  calc Real.exp (-1) ^ j * Real.exp (-1) * eps (j + 1)
      = Real.exp (-1) * (Real.exp (-1) ^ j * eps (j + 1)) := by ring
    _ ≤ Real.exp (-1) * (1 / (((j : ℝ) + 1) * Real.sqrt (2 * Real.pi * j))) :=
        mul_le_mul_of_nonneg_left (exp_neg_mul_eps_le hj) (Real.exp_pos _).le
    _ = Real.exp (-1) / (((j : ℝ) + 1) * Real.sqrt (2 * Real.pi * j)) := by ring

/-! ### The far weights -/

private theorem gs_sub_gam_le {k i : ℕ} (hk : 2 ≤ k) (hi : 1 ≤ i) (h : 3 * k ≤ 5 * (i + 2)) :
    gs i - gam k ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))) := by
  have h1 := gs_le_exp hi
  have h2 := gam_ge_exp hk
  have hK2 : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK : (0 : ℝ) < (k : ℝ) := by linarith
  have hh : 3 * (k : ℝ) ≤ 5 * ((i : ℝ) + 2) := by exact_mod_cast h
  have hAB : 3 / (2 * ((i : ℝ) + 2)) ≤ 5 / (2 * (k : ℝ)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    nlinarith
  have hA : (0 : ℝ) ≤ 3 / (2 * ((i : ℝ) + 2)) := by positivity
  have e1 : Real.exp (1 - 5 / (2 * (k : ℝ)))
      = Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
        * Real.exp (-(5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have h3 : 1 - (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
      ≤ Real.exp (-(5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))) := by
    linarith [Real.add_one_le_exp (-(5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))))]
  have h4 : Real.exp (1 - 3 / (2 * ((i : ℝ) + 2))) ≤ Real.exp 1 :=
    Real.exp_le_exp.mpr (by linarith)
  have hE : 0 < Real.exp (1 - 3 / (2 * ((i : ℝ) + 2))) := Real.exp_pos _
  have h5 : Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
        * (1 - (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))))
      ≤ Real.exp (1 - 5 / (2 * (k : ℝ))) := by
    rw [e1]
    exact mul_le_mul_of_nonneg_left h3 hE.le
  have h6 : Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
        * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
      ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))) :=
    mul_le_mul_of_nonneg_right h4 (by linarith)
  have h7 : Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
        * (1 - (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))))
      = Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
        - Real.exp (1 - 3 / (2 * ((i : ℝ) + 2)))
          * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))) := by ring
  linarith

/-- The profile bound: for `m = i + 1` with `3k/5 ≤ m + 1 ≤ k`, `m + 1 ≥ 50`,
`(g(m) - γ_k) f_m ≤ 1.05 c₀ / k^{5/2}`. -/
theorem theta_f_le {k i : ℕ} (hi : 48 ≤ i) (hik : i + 2 ≤ k) (h : 3 * k ≤ 5 * (i + 2)) :
    (gs i - gam k) * fker (i + 1) ≤ 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := by
  have hI48 : (48 : ℝ) ≤ (i : ℝ) := by exact_mod_cast hi
  have hI : (0 : ℝ) < (i : ℝ) := by linarith
  have hsK : (i : ℝ) + 2 ≤ (k : ℝ) := by exact_mod_cast hik
  have hK : (0 : ℝ) < (k : ℝ) := by linarith
  have hh : 3 * (k : ℝ) ≤ 5 * ((i : ℝ) + 2) := by exact_mod_cast h
  have hθ := gs_sub_gam_le (k := k) (i := i) (by omega) (by omega) h
  have hf := fker_le (j := i) (by omega)
  have hf0 : 0 ≤ fker (i + 1) := (fker_pos (by omega)).le
  -- square roots
  obtain ⟨a, ha⟩ : ∃ a : ℝ, a = Real.sqrt ((i : ℝ) + 2) := ⟨_, rfl⟩
  obtain ⟨b, hb⟩ : ∃ b : ℝ, b = Real.sqrt (k : ℝ) := ⟨_, rfl⟩
  obtain ⟨d, hd⟩ : ∃ d : ℝ, d = Real.sqrt (i : ℝ) := ⟨_, rfl⟩
  obtain ⟨w, hw⟩ : ∃ w : ℝ, w = Real.sqrt (2 * Real.pi) := ⟨_, rfl⟩
  have ha2 : a ^ 2 = (i : ℝ) + 2 := by rw [ha]; exact Real.sq_sqrt (by linarith)
  have hb2 : b ^ 2 = (k : ℝ) := by rw [hb]; exact Real.sq_sqrt hK.le
  have hd2 : d ^ 2 = (i : ℝ) := by rw [hd]; exact Real.sq_sqrt hI.le
  have ha0 : 0 < a := by rw [ha]; exact Real.sqrt_pos.2 (by linarith)
  have hb0 : 0 < b := by rw [hb]; exact Real.sqrt_pos.2 hK
  have hd0 : 0 < d := by rw [hd]; exact Real.sqrt_pos.2 hI
  have hw0 : 0 < w := by
    rw [hw]
    exact Real.sqrt_pos.2 (mul_pos two_pos Real.pi_pos)
  have hsq : Real.sqrt (2 * Real.pi * (i : ℝ)) = w * d := by
    rw [hw, hd]
    exact Real.sqrt_mul (mul_pos two_pos Real.pi_pos).le _
  have hc0 : c0 = 1 / w := by
    unfold c0
    rw [hw]
  have hee : Real.exp 1 * Real.exp (-1) = 1 := by
    rw [← Real.exp_add]
    norm_num
  -- the profile inequalities
  have h_i : (5 * a ^ 2 - 3 * b ^ 2) * b ^ 3 ≤ 2 * a ^ 5 := by
    have hcub : 0 ≤ 2 * a ^ 3 + 4 * a ^ 2 * b + 6 * a * b ^ 2 + 3 * b ^ 3 := by positivity
    nlinarith [mul_nonneg (sq_nonneg (a - b)) hcub]
  have h_ii : a ^ 3 ≤ 105 / 100 * ((a ^ 2 - 1) * d) := by
    have hpos : 0 ≤ 105 / 100 * ((a ^ 2 - 1) * d) := by
      have h1 : (0 : ℝ) ≤ a ^ 2 - 1 := by rw [ha2]; linarith
      exact mul_nonneg (by norm_num) (mul_nonneg h1 hd0.le)
    refine le_of_pow_le_pow_left₀ two_ne_zero hpos ?_
    have e1 : (a ^ 3) ^ 2 = (a ^ 2) ^ 3 := by ring
    have e2 : (105 / 100 * ((a ^ 2 - 1) * d)) ^ 2
        = 11025 / 10000 * ((a ^ 2 - 1) ^ 2 * d ^ 2) := by ring
    rw [e1, e2, ha2, hd2]
    have h50 : (0 : ℝ) ≤ (i : ℝ) + 2 - 50 := by linarith
    nlinarith [mul_nonneg (sq_nonneg ((i : ℝ) + 2)) h50, sq_nonneg ((i : ℝ) + 2)]
  -- combine
  have hδ0 : 0 ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))) := by
    have hAB : 3 / (2 * ((i : ℝ) + 2)) ≤ 5 / (2 * (k : ℝ)) := by
      rw [div_le_div_iff₀ (by positivity) (by positivity)]
      nlinarith
    exact mul_nonneg (Real.exp_pos 1).le (by linarith)
  have hstep1 : (gs i - gam k) * fker (i + 1)
      ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
        * (Real.exp (-1) / (((i : ℝ) + 1) * (w * d))) := by
    rw [hsq] at hf
    calc (gs i - gam k) * fker (i + 1)
        ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2))) * fker (i + 1) :=
          mul_le_mul_of_nonneg_right hθ hf0
      _ ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
            * (Real.exp (-1) / (((i : ℝ) + 1) * (w * d))) :=
          mul_le_mul_of_nonneg_left hf hδ0
  have hstep2 : Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
        * (Real.exp (-1) / (((i : ℝ) + 1) * (w * d)))
      = (5 * a ^ 2 - 3 * b ^ 2) / (2 * b ^ 2 * a ^ 2 * ((a ^ 2 - 1) * d) * w) := by
    rw [ha2, hb2]
    have hw1 : w ≠ 0 := hw0.ne'
    have hd1 : d ≠ 0 := hd0.ne'
    have hK1 : (k : ℝ) ≠ 0 := hK.ne'
    have hi2 : ((i : ℝ) + 2) ≠ 0 := by linarith
    have hi1 : ((i : ℝ) + 1) ≠ 0 := by linarith
    have hi1' : ((i : ℝ) + 2 - 1) ≠ 0 := by linarith
    have e : Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
          * (Real.exp (-1) / (((i : ℝ) + 1) * (w * d)))
        = (Real.exp 1 * Real.exp (-1)) * ((5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
          / (((i : ℝ) + 1) * (w * d))) := by ring
    rw [e, hee, one_mul]
    field
  have hstep3 : (5 * a ^ 2 - 3 * b ^ 2) / (2 * b ^ 2 * a ^ 2 * ((a ^ 2 - 1) * d) * w)
      ≤ 105 / 100 * (1 / w) / ((b ^ 2) ^ 2 * b) := by
    have h1 : (0 : ℝ) < a ^ 2 - 1 := by rw [ha2]; linarith
    have hden1 : 0 < 2 * b ^ 2 * a ^ 2 * ((a ^ 2 - 1) * d) * w :=
      mul_pos (mul_pos (mul_pos (mul_pos two_pos (pow_pos hb0 2)) (pow_pos ha0 2))
        (mul_pos h1 hd0)) hw0
    have hden2 : 0 < (b ^ 2) ^ 2 * b := mul_pos (pow_pos (pow_pos hb0 2) 2) hb0
    have e : 105 / 100 * (1 / w) / ((b ^ 2) ^ 2 * b) = 105 / 100 / (w * ((b ^ 2) ^ 2 * b)) := by
      field
    rw [e, div_le_div_iff₀ hden1 (mul_pos hw0 hden2)]
    -- (5a² - 3b²) (w b⁵) ≤ 1.05 · 2 b² a² (a²-1) d w
    have hmain : (5 * a ^ 2 - 3 * b ^ 2) * b ^ 3 ≤ 2 * a ^ 2 * (105 / 100 * ((a ^ 2 - 1) * d)) := by
      have h2 : 2 * a ^ 5 = 2 * a ^ 2 * a ^ 3 := by ring
      have h3 : 2 * a ^ 2 * a ^ 3 ≤ 2 * a ^ 2 * (105 / 100 * ((a ^ 2 - 1) * d)) :=
        mul_le_mul_of_nonneg_left h_ii (mul_nonneg zero_le_two (pow_pos ha0 2).le)
      linarith
    have hfin := mul_le_mul_of_nonneg_left hmain (mul_pos hw0 (pow_pos hb0 2)).le
    have e3 : (5 * a ^ 2 - 3 * b ^ 2) * (w * ((b ^ 2) ^ 2 * b))
        = w * b ^ 2 * ((5 * a ^ 2 - 3 * b ^ 2) * b ^ 3) := by ring
    have e4 : 105 / 100 * (2 * b ^ 2 * a ^ 2 * ((a ^ 2 - 1) * d) * w)
        = w * b ^ 2 * (2 * a ^ 2 * (105 / 100 * ((a ^ 2 - 1) * d))) := by ring
    rw [e3, e4]
    exact hfin
  have hfinal : 105 / 100 * (1 / w) / ((b ^ 2) ^ 2 * b)
      = 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := by
    rw [hc0, hb2, hb]
  calc (gs i - gam k) * fker (i + 1)
      ≤ Real.exp 1 * (5 / (2 * (k : ℝ)) - 3 / (2 * ((i : ℝ) + 2)))
          * (Real.exp (-1) / (((i : ℝ) + 1) * (w * d))) := hstep1
    _ = (5 * a ^ 2 - 3 * b ^ 2) / (2 * b ^ 2 * a ^ 2 * ((a ^ 2 - 1) * d) * w) := hstep2
    _ ≤ 105 / 100 * (1 / w) / ((b ^ 2) ^ 2 * b) := hstep3
    _ = 105 / 100 * c0 / ((k : ℝ) ^ 2 * Real.sqrt k) := hfinal

/-! ### A telescoping lower bound -/

/-- If $G_i \ge c\,(i+1)^{-3/2}$ for all $i \ge a$, with $c \ge 0$, then $\sum_{a\le i<b}G_i \ge
2c\,\bigl(\frac1{\sqrt{a+1}} - \frac1{\sqrt{b+1}}\bigr)$ for every $b \ge a$. -/
theorem tail_sqrt (G : ℕ → ℝ) (c : ℝ) (hc : 0 ≤ c) (a : ℕ)
    (hG : ∀ i, a ≤ i → c / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1)) ≤ G i) :
    ∀ b, a ≤ b → c * (2 * (1 / Real.sqrt ((a : ℝ) + 1) - 1 / Real.sqrt ((b : ℝ) + 1)))
      ≤ ∑ i ∈ Finset.Ico a b, G i := by
  intro b hab
  induction b, hab using Nat.le_induction with
  | base =>
    exact le_of_eq (by rw [Finset.Ico_self, Finset.sum_empty, sub_self, mul_zero, mul_zero])
  | succ n han ih =>
    rw [Finset.sum_Ico_succ_top han]
    have h1 := (inv_sqrt_diff_bounds (y := (n : ℝ) + 1) (by positivity)).2
    have h3 := hG n han
    have h4 : c * (2 * (1 / Real.sqrt ((n : ℝ) + 1) - 1 / Real.sqrt ((n : ℝ) + 1 + 1)))
        ≤ c * (1 / (((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1))) :=
      mul_le_mul_of_nonneg_left h1 hc
    have h5 : c * (1 / (((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)))
        = c / (((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)) := by ring
    rw [Nat.cast_add, Nat.cast_one]
    linarith

/-! ### Numerical constants -/

private theorem exp_rat_le (p q : ℕ) (B : ℝ) (hq : q ≠ 0) (hB : 0 ≤ B)
    (h : (27183 / 10000 : ℝ) ^ p ≤ B ^ q) : Real.exp ((p : ℝ) / (q : ℝ)) ≤ B := by
  have he : Real.exp 1 ≤ 27183 / 10000 :=
    le_of_lt (lt_of_lt_of_le Real.exp_one_lt_d9 (by norm_num))
  have hq' : (q : ℝ) ≠ 0 := by exact_mod_cast hq
  have h1 : Real.exp ((p : ℝ) / (q : ℝ)) ^ q = Real.exp 1 ^ p := by
    rw [← Real.exp_nat_mul, ← Real.exp_nat_mul]
    congr 1
    field
  have h2 : Real.exp 1 ^ p ≤ (27183 / 10000 : ℝ) ^ p :=
    pow_le_pow_left₀ (Real.exp_pos 1).le he p
  refine le_of_pow_le_pow_left₀ hq hB ?_
  rw [h1]
  exact h2.trans h

/-- The numerical inequality $e^{41/60} \le 2$. -/
theorem exp_41_60 : Real.exp (41 / 60) ≤ 2 := by
  have h := exp_rat_le 41 60 2 (by norm_num) (by norm_num) (by norm_num)
  norm_num at h
  linarith

/-- The numerical inequality $e^{4/3} \le 3.8$. -/
theorem exp_4_3 : Real.exp (4 / 3) ≤ 38 / 10 := by
  have h := exp_rat_le 4 3 (38 / 10) (by norm_num) (by norm_num) (by norm_num)
  norm_num at h
  linarith

/-- The numerical inequality $e^{7/3} \le 10.32$. -/
theorem exp_7_3 : Real.exp (7 / 3) ≤ 1032 / 100 := by
  have h := exp_rat_le 7 3 (1032 / 100) (by norm_num) (by norm_num) (by norm_num)
  norm_num at h
  linarith

/-- `e^x ≤ 1 + 6x/5` for `0 ≤ x ≤ 1/6`. -/
private theorem exp_le_small {x : ℝ} (hx0 : 0 ≤ x) (hx : x ≤ 1 / 6) :
    Real.exp x ≤ 1 + 6 / 5 * x := by
  have h1 : 1 - x ≤ Real.exp (-x) := by linarith [Real.add_one_le_exp (-x)]
  have h2 : Real.exp (-x) * Real.exp x = 1 := by
    rw [← Real.exp_add, neg_add_cancel, Real.exp_zero]
  have hpos : 0 < Real.exp x := Real.exp_pos x
  have h3 : (1 - x) * Real.exp x ≤ 1 := by
    calc (1 - x) * Real.exp x ≤ Real.exp (-x) * Real.exp x :=
          mul_le_mul_of_nonneg_right h1 hpos.le
      _ = 1 := h2
  have h4 : 1 ≤ (1 - x) * (1 + 6 / 5 * x) := by
    nlinarith [mul_nonneg hx0 (sub_nonneg.2 hx)]
  have h5 : (0 : ℝ) < 1 - x := by linarith
  exact le_of_mul_le_mul_left (h3.trans h4) h5

/-! ### The near term -/

/-- The bound of the near term: for `k ≥ 15`, `t ≥ 1`, `σ > 0` and `λ > 0` with
`σ (k + 3) ≤ λ (σ k + 1)`, `σ k ≤ t ≤ σ k + 1` and `0 ≤ N ≤ L k`,
`(N/2) ε_{t+1} x^t ≤ λ L e^{5σ/2} / (2σ √(2πσk))`. -/
theorem near_term_le {k t : ℕ} (hk : 15 ≤ k) (ht : 1 ≤ t) (σ lam L N : ℝ)
    (hσ : 0 < σ) (hlam0 : 0 < lam) (hlam : σ * ((k : ℝ) + 3) ≤ lam * (σ * (k : ℝ) + 1))
    (hT1 : σ * (k : ℝ) ≤ (t : ℝ)) (hT2 : (t : ℝ) ≤ σ * (k : ℝ) + 1)
    (hN0 : 0 ≤ N) (hN : N ≤ L * (k : ℝ)) :
    N / 2 * (eps (t + 1) * xk k ^ t)
      ≤ lam * L * Real.exp (5 * σ / 2)
        / (2 * σ * Real.sqrt (2 * Real.pi * (σ * (k : ℝ)))) := by
  have hK15 : (15 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hK : (0 : ℝ) < (k : ℝ) := by linarith
  have hK0 : (k : ℝ) ≠ 0 := hK.ne'
  have hT0 : (0 : ℝ) < (t : ℝ) := by exact_mod_cast ht
  have hT : (0 : ℝ) < (t : ℝ) + 1 := by linarith
  have hσK : 0 < σ * (k : ℝ) := mul_pos hσ hK
  have h2pi : (0 : ℝ) < 2 * Real.pi := mul_pos two_pos Real.pi_pos
  have hψ := psi_le (k := k) (t := t) (by omega) ht
  obtain ⟨S, hSdef⟩ : ∃ S : ℝ, S = Real.sqrt (2 * Real.pi * (t : ℝ)) := ⟨_, rfl⟩
  rw [← hSdef] at hψ
  have hS : 0 < S := by rw [hSdef]; exact Real.sqrt_pos.2 (mul_pos h2pi hT0)
  have hψ0 : 0 ≤ eps (t + 1) * xk k ^ t :=
    mul_nonneg (eps_nonneg _) (pow_nonneg (CrossCrit.xk_pos k).le t)
  obtain ⟨ψ, hψdef⟩ : ∃ ψ : ℝ, ψ = eps (t + 1) * xk k ^ t := ⟨_, rfl⟩
  rw [← hψdef] at hψ hψ0 ⊢
  obtain ⟨Eh, hEhdef⟩ : ∃ Eh : ℝ, Eh = Real.exp (5 * σ / 2) := ⟨_, rfl⟩
  have hEh : 0 < Eh := by rw [hEhdef]; exact Real.exp_pos _
  -- the exponential factor
  have hx0 : (0 : ℝ) ≤ 5 / (2 * (k : ℝ)) := by positivity
  have hx1 : 5 / (2 * (k : ℝ)) ≤ 1 / 6 := by
    rw [div_le_div_iff₀ (by positivity) (by norm_num)]
    linarith
  have hexp1 := exp_le_small hx0 hx1
  have hEsplit : Real.exp (5 * (t : ℝ) / (2 * (k : ℝ)))
      ≤ Eh * Real.exp (5 / (2 * (k : ℝ))) := by
    rw [hEhdef, ← Real.exp_add]
    refine Real.exp_le_exp.mpr ?_
    have e : 5 * σ / 2 + 5 / (2 * (k : ℝ)) = 5 * (σ * (k : ℝ) + 1) / (2 * (k : ℝ)) := by
      field
    rw [e]
    exact div_le_div_of_nonneg_right (by linarith) (by positivity)
  have hE : Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) ≤ Eh * (1 + 3 / (k : ℝ)) := by
    have e2 : 1 + 6 / 5 * (5 / (2 * (k : ℝ))) = 1 + 3 / (k : ℝ) := by field
    calc Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) ≤ Eh * Real.exp (5 / (2 * (k : ℝ))) := hEsplit
      _ ≤ Eh * (1 + 6 / 5 * (5 / (2 * (k : ℝ)))) := mul_le_mul_of_nonneg_left hexp1 hEh.le
      _ = Eh * (1 + 3 / (k : ℝ)) := by rw [e2]
  have hW : (1 + 3 / (k : ℝ)) * (σ * (k : ℝ)) ≤ lam * ((t : ℝ) + 1) := by
    have e : (1 + 3 / (k : ℝ)) * (σ * (k : ℝ)) = σ * ((k : ℝ) + 3) := by field
    rw [e]
    have h1 : lam * (σ * (k : ℝ) + 1) ≤ lam * ((t : ℝ) + 1) :=
      mul_le_mul_of_nonneg_left (by linarith) hlam0.le
    linarith
  have hψ' : ψ * (((t : ℝ) + 1) * S) ≤ Real.exp (5 * (t : ℝ) / (2 * (k : ℝ))) := by
    rw [le_div_iff₀ (mul_pos hT hS)] at hψ
    exact hψ
  have hA : ψ * (S * (σ * (k : ℝ))) * ((t : ℝ) + 1) ≤ (lam * Eh) * ((t : ℝ) + 1) := by
    calc ψ * (S * (σ * (k : ℝ))) * ((t : ℝ) + 1)
        = (ψ * (((t : ℝ) + 1) * S)) * (σ * (k : ℝ)) := by ring
      _ ≤ (Eh * (1 + 3 / (k : ℝ))) * (σ * (k : ℝ)) :=
          mul_le_mul_of_nonneg_right (hψ'.trans hE) hσK.le
      _ = Eh * ((1 + 3 / (k : ℝ)) * (σ * (k : ℝ))) := by ring
      _ ≤ Eh * (lam * ((t : ℝ) + 1)) := mul_le_mul_of_nonneg_left hW hEh.le
      _ = (lam * Eh) * ((t : ℝ) + 1) := by ring
  have hB : ψ * (S * (σ * (k : ℝ))) ≤ lam * Eh := le_of_mul_le_mul_right hA hT
  have hC : (N / 2 * ψ) * (2 * σ * S) * (k : ℝ) ≤ (lam * L * Eh) * (k : ℝ) := by
    calc (N / 2 * ψ) * (2 * σ * S) * (k : ℝ) = N * (ψ * (S * (σ * (k : ℝ)))) := by ring
      _ ≤ N * (lam * Eh) := mul_le_mul_of_nonneg_left hB hN0
      _ ≤ (L * (k : ℝ)) * (lam * Eh) :=
          mul_le_mul_of_nonneg_right hN (mul_pos hlam0 hEh).le
      _ = (lam * L * Eh) * (k : ℝ) := by ring
  have hD : (N / 2 * ψ) * (2 * σ * S) ≤ lam * L * Eh := le_of_mul_le_mul_right hC hK
  -- from `√(2πt)` to `√(2πσk)`
  have hSS : Real.sqrt (2 * Real.pi * (σ * (k : ℝ))) ≤ S := by
    rw [hSdef]
    exact Real.sqrt_le_sqrt (mul_le_mul_of_nonneg_left hT1 h2pi.le)
  have hσ2 : (0 : ℝ) < 2 * σ := mul_pos two_pos hσ
  rw [← hEhdef, le_div_iff₀ (mul_pos hσ2 (Real.sqrt_pos.2 (mul_pos h2pi hσK)))]
  exact (mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hSS hσ2.le)
    (mul_nonneg (by linarith) hψ0)).trans hD

/-- The comparison of the bound `near_term_le` with a number `p ≥ 0`: for `E₀ ≥ e^{5σ}` and
`N ≤ c k`, `(N/2) ε_{t+1} x^t ≤ p` as soon as `λ² c² E₀ ≤ p² · 8 · 3.14 · σ³ k`. -/
theorem P1_le {k t : ℕ} (hk : 15 ≤ k) (ht : 1 ≤ t) (σ c E0 lam N p : ℝ)
    (hσ : 0 < σ) (hlam0 : 0 < lam) (hlam : σ * ((k : ℝ) + 3) ≤ lam * (σ * (k : ℝ) + 1))
    (hT1 : σ * (k : ℝ) ≤ (t : ℝ)) (hT2 : (t : ℝ) ≤ σ * (k : ℝ) + 1)
    (hE0 : Real.exp (5 * σ) ≤ E0) (hN0 : 0 ≤ N) (hN : N ≤ c * (k : ℝ))
    (hp : 0 ≤ p)
    (hnum : lam ^ 2 * c ^ 2 * E0 ≤ p ^ 2 * (8 * (314 / 100) * σ ^ 3 * (k : ℝ))) :
    N / 2 * (eps (t + 1) * xk k ^ t) ≤ p := by
  have hK : (0 : ℝ) < (k : ℝ) := by exact_mod_cast (by omega : 0 < k)
  have h2pi : (0 : ℝ) < 2 * Real.pi * (σ * (k : ℝ)) :=
    mul_pos (mul_pos two_pos Real.pi_pos) (mul_pos hσ hK)
  have hloss := near_term_le hk ht σ lam c N hσ hlam0 hlam hT1 hT2 hN0 hN
  obtain ⟨S, hSdef⟩ : ∃ S : ℝ, S = Real.sqrt (2 * Real.pi * (σ * (k : ℝ))) := ⟨_, rfl⟩
  rw [← hSdef] at hloss
  have hS2 : S ^ 2 = 2 * Real.pi * (σ * (k : ℝ)) := by rw [hSdef]; exact Real.sq_sqrt h2pi.le
  have hpos : 0 < 2 * σ * S := by
    rw [hSdef]
    exact mul_pos (mul_pos two_pos hσ) (Real.sqrt_pos.2 h2pi)
  have hpi : (314 / 100 : ℝ) ≤ Real.pi := le_of_lt (lt_of_le_of_lt (by norm_num) Real.pi_gt_d2)
  have hE : Real.exp (5 * σ / 2) ^ 2 = Real.exp (5 * σ) := by
    rw [← Real.exp_nat_mul]
    congr 1
    push_cast
    ring
  -- the square of the right side of `near_term_le` is `λ² c² e^{5σ} / (8π σ³ k)`
  have hsq : (lam * c * Real.exp (5 * σ / 2)) ^ 2 ≤ (p * (2 * σ * S)) ^ 2 := by
    calc (lam * c * Real.exp (5 * σ / 2)) ^ 2 = lam ^ 2 * c ^ 2 * Real.exp (5 * σ) := by
          rw [mul_pow, mul_pow, hE]
      _ ≤ lam ^ 2 * c ^ 2 * E0 := mul_le_mul_of_nonneg_left hE0 (by positivity)
      _ ≤ p ^ 2 * (8 * (314 / 100) * σ ^ 3 * (k : ℝ)) := hnum
      _ ≤ p ^ 2 * (8 * Real.pi * σ ^ 3 * (k : ℝ)) :=
          mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right
            (mul_le_mul_of_nonneg_left hpi (by norm_num)) (pow_pos hσ 3).le) hK.le) (sq_nonneg p)
      _ = (p * (2 * σ * S)) ^ 2 := by
          rw [mul_pow, mul_pow, mul_pow, hS2]
          ring
  exact hloss.trans ((div_le_iff₀ hpos).2
    (le_of_pow_le_pow_left₀ two_ne_zero (mul_nonneg hp hpos.le) hsq))

end Parking
