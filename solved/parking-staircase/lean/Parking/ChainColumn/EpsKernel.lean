import Parking.Cayley.Basic
import Parking.Basic.Renewal

/-!
# The prime kernel `ε_m = (m-1)^(m-1)/m!` is log-convex

* `eps_pos`        : `0 < ε_m` for `m ≥ 1`;
* `gs i`           : the step ratio `ε_{i+2}/ε_{i+1} = (i+1)/(i+2) · (1+1/i)^i`;
* `eps_step`       : `ε_{i+2} = gs i · ε_{i+1}`;
* `gs_mono`        : the step ratio is nondecreasing;
* `eps_logconvex`  : `ε_{n+2}² ≤ ε_{n+1} ε_{n+3}`;
* `eps_cross`      : `ε_{m+t} ε_r ≤ ε_m ε_{r+t}` for `1 ≤ m ≤ r`.
-/

namespace Parking

open Finset

/-- The numbers $\varepsilon_m = (m-1)^{m-1}/m!$ are positive for every $m \ge 1$. -/
theorem eps_pos {m : ℕ} (hm : 1 ≤ m) : 0 < eps m := by
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  rw [eps_succ]
  rcases i with _ | j
  · norm_num
  · positivity

/-- The step ratio `ε_{i+2}/ε_{i+1}`. -/
noncomputable def gs (i : ℕ) : ℝ := ((i : ℝ) + 1) / ((i : ℝ) + 2) * (1 + 1 / (i : ℝ)) ^ i

/-- The first step ratio of the prime kernel is $g_1 = \frac12$. -/
theorem gs_zero : gs 0 = 1 / 2 := by
  unfold gs
  norm_num

private theorem eps_two : eps 2 = 1 / 2 := by
  have h := eps_succ 1
  have hf : (1 + 1).factorial = 2 := rfl
  rw [hf] at h
  norm_num at h
  linarith

/-- Consecutive values of the prime kernel are related by the step ratio: $\varepsilon_{m+1} =
g_m\,\varepsilon_m$ for every $m \ge 1$. -/
theorem eps_step (i : ℕ) : eps (i + 1 + 1) = gs i * eps (i + 1) := by
  rcases Nat.eq_zero_or_pos i with rfl | hi
  · show eps 2 = gs 0 * eps 1
    rw [eps_two, eps_one, gs_zero]
    norm_num
  · have ha : (0 : ℝ) < (i : ℝ) := by exact_mod_cast hi
    have ha0 : (i : ℝ) ≠ 0 := ha.ne'
    have hpi : (i : ℝ) ^ i ≠ 0 := pow_ne_zero _ ha.ne'
    have hF : ((i + 1).factorial : ℝ) ≠ 0 := by positivity
    have h2 : ((i : ℝ) + 1 + 1) ≠ 0 := by positivity
    have h3 : ((i : ℝ) + 2) ≠ 0 := by positivity
    have e : (1 + 1 / (i : ℝ)) = ((i : ℝ) + 1) / (i : ℝ) := by field
    rw [eps_succ (i + 1), eps_succ i, Nat.factorial_succ (i + 1)]
    unfold gs
    rw [e, div_pow]
    push_cast
    rw [pow_succ]
    field

/-- The step ratio $g_m = \varepsilon_{m+1}/\varepsilon_m$ of the prime kernel is nondecreasing in
$m$. -/
theorem gs_mono : Monotone gs := by
  refine monotone_nat_of_le_succ fun i => ?_
  rcases Nat.eq_zero_or_pos i with rfl | hi
  · unfold gs
    norm_num
  · have ha : (0 : ℝ) < (i : ℝ) := by exact_mod_cast hi
    have h1 : ((i : ℝ) + 1) / ((i : ℝ) + 2) ≤ (((i + 1 : ℕ) : ℝ) + 1)
        / (((i + 1 : ℕ) : ℝ) + 2) := by
      rw [div_le_div_iff₀ (by positivity) (by positivity)]
      push_cast
      nlinarith
    have h2 : (1 + 1 / (i : ℝ)) ^ i ≤ (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1) :=
      chi_mono hi (Nat.le_add_right i 1)
    have h3 : (0 : ℝ) ≤ (1 + 1 / (i : ℝ)) ^ i := by positivity
    have h4 : (0 : ℝ) ≤ (((i + 1 : ℕ) : ℝ) + 1) / (((i + 1 : ℕ) : ℝ) + 2) := by positivity
    unfold gs
    exact mul_le_mul h1 h2 h3 h4

/-- Log-convexity of the prime kernel: `ε_{n+2}² ≤ ε_{n+1} ε_{n+3}`. -/
theorem eps_logconvex (n : ℕ) : eps (n + 2) ^ 2 ≤ eps (n + 1) * eps (n + 3) := by
  have h1 : eps (n + 2) = gs n * eps (n + 1) := eps_step n
  have h2 : eps (n + 3) = gs (n + 1) * eps (n + 2) := eps_step (n + 1)
  have hp1 : 0 < eps (n + 1) := eps_pos (by omega)
  have hp2 : 0 < eps (n + 2) := eps_pos (by omega)
  calc eps (n + 2) ^ 2 = eps (n + 2) * (gs n * eps (n + 1)) := by rw [← h1]; ring
    _ ≤ eps (n + 2) * (gs (n + 1) * eps (n + 1)) :=
        mul_le_mul_of_nonneg_left
          (mul_le_mul_of_nonneg_right (gs_mono (Nat.le_succ n)) hp1.le) hp2.le
    _ = eps (n + 1) * eps (n + 3) := by rw [h2]; ring

/-- Cross form of log-convexity: for `1 ≤ m ≤ r`, `ε_{m+t} ε_r ≤ ε_m ε_{r+t}`. -/
theorem eps_cross {m r : ℕ} (hm : 1 ≤ m) (hmr : m ≤ r) (t : ℕ) :
    eps (m + t) * eps r ≤ eps m * eps (r + t) := by
  obtain ⟨a, rfl⟩ : ∃ a, m = a + 1 := ⟨m - 1, by omega⟩
  obtain ⟨b, rfl⟩ : ∃ b, r = b + 1 := ⟨r - 1, by omega⟩
  have h : eps (a + t + 1) * eps (b + 1) ≤ eps (a + 1) * eps (b + t + 1) :=
    logConvex_cross (G := fun n => eps (n + 1)) (fun n => eps_pos (by omega))
      eps_logconvex (show a ≤ b by omega) t
  rw [Nat.add_right_comm a t 1, Nat.add_right_comm b t 1] at h
  exact h

end Parking
