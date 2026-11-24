module

public import Parking.LeftHalf.FirstLayer.Conv
public import Parking.LeftHalf.FirstLayer.Omega

/-!
# The pair sums of tilted Cayley numbers

`pairT k ρ j = ∑_{a ≤ j} ω_{ρ+a} ω_{ρ+j-a}` is the sum of the products `ω_a ω_b` over the pairs
`a, b ≥ ρ` with `a + b = 2ρ + j`.  It is the part of the last-car recursion in which both pieces are
free and both are larger than the excess.  For `ρ + n + 2 = k` the three values
`pairT k ρ n`, `pairT k ρ (n+1)`, `pairT k ρ (n+2)` are the pair sums of the thresholds `k-1`, `k`,
`k+1` (all indices at most `k`).

* `pairT_TK`     : these three values have property K at `k` (`conv_TK` applied to `ω`);
* `pairT_mid_le` : `pairT k ρ (n+1) ≤ (n+2) ω_ρ ω_k` (log-convexity of `ω`);
* `pairT_D_le`   : `e^μ pairT k ρ (n+2) - e^{-μ} pairT k ρ n ≤ 2 e^μ ω_ρ ω_k` for `μ ≤ 1/(k(k+2))`.
-/

@[expose] public section

namespace Parking.FirstLayer
open Real Finset

/-- The pair sum `∑_{a ≤ j} ω_{ρ+a} ω_{ρ+j-a}`. -/
noncomputable def pairT (k ρ j : ℕ) : ℝ := conv (fun a => ccT (xcrit k) (ρ + a)) j

/-- The pair sum of `Parking.FirstLayer.pairT` written as an explicit sum:
$Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+(j-a)}$. -/
theorem pairT_eq (k ρ j : ℕ) :
    pairT k ρ j = ∑ a ∈ range (j + 1), ccT (xcrit k) (ρ + a) * ccT (xcrit k) (ρ + (j - a)) := rfl

/-- The pair sums $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+j-a}$ of tilted Cayley
masses are nonnegative. -/
theorem pairT_nonneg (k ρ j : ℕ) : 0 ≤ pairT k ρ j := by
  have hx := xcrit_pos k
  rw [pairT_eq]
  exact Finset.sum_nonneg fun a _ => mul_nonneg (ccT_pos hx _).le (ccT_pos hx _).le

/-- **The pair sums have property K at `k`.** -/
theorem pairT_TK {k ρ n : ℕ} (hk : 3 ≤ k) (hn : ρ + n + 2 = k) :
    TK k (pairT k ρ n) (pairT k ρ (n + 1)) (pairT k ρ (n + 2)) := by
  have hk1 : 1 ≤ k := by omega
  unfold pairT
  refine conv_TK n (by omega) (fun a => ccT (xcrit k) (ρ + a)) (fun a _ => ccT_pos (xcrit_pos k) _)
      ?_ ?_ ?_
  · intro a ha
    show ccT (xcrit k) (ρ + (n + 1)) ≤ ccT (xcrit k) (ρ + a)
    exact ccT_anti (by omega) (by omega)
  · have e1 : ρ + (n + 2) = k := by omega
    have e2 : ρ + (n + 1) = k - 1 := by omega
    show ccT (xcrit k) (ρ + (n + 2)) = ccT (xcrit k) (ρ + (n + 1))
    rw [e1, e2]
    exact ccT_top hk1
  · intro μ _ j hj
    have h := ccT_tilt_mid (k := k) (j := ρ + j) hk (by omega) μ
    show 2 * exp (μ / k) * ccT (xcrit k) (ρ + (j + 1)) ≤
      exp μ * ccT (xcrit k) (ρ + (j + 2)) + exp (-μ) * ccT (xcrit k) (ρ + j)
    exact h

/-- The middle pair sum is at most its number of terms times `ω_ρ ω_k`. -/
theorem pairT_mid_le {k ρ n : ℕ} (hk : 3 ≤ k) (hn : ρ + n + 2 = k) :
    pairT k ρ (n + 1) ≤ ((n : ℝ) + 2) * (ccT (xcrit k) ρ * ccT (xcrit k) k) := by
  have hk1 : 1 ≤ k := by omega
  have hterm : ∀ a ∈ range (n + 1 + 1),
      ccT (xcrit k) (ρ + a) * ccT (xcrit k) (ρ + (n + 1 - a)) ≤ ccT (xcrit k) ρ
          * ccT (xcrit k) k := by
    intro a ha
    rw [Finset.mem_range] at ha
    have h := ccT_logconvex k (ρ := ρ) (m := n + 1) (a := a) (by omega)
    have e1 : ρ + (n + 1) - a = ρ + (n + 1 - a) := by omega
    have e2 : ρ + (n + 1) = k - 1 := by omega
    rw [e1, e2, ← ccT_top hk1] at h
    exact h
  rw [pairT_eq]
  refine le_trans (Finset.sum_le_sum hterm) (le_of_eq ?_)
  rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  push_cast
  ring

/-- For `μ ≤ 1/(k(k+2))` the tilted difference of the outer pair sums is at most its two boundary
terms: `e^μ pairT k ρ (n+2) - e^{-μ} pairT k ρ n ≤ 2 e^μ ω_ρ ω_k`. -/
theorem pairT_D_le {k ρ n : ℕ} (hk : 3 ≤ k) (hn : ρ + n + 2 = k) {μ : ℝ}
    (hμ : μ ≤ 1 / ((k : ℝ) * ((k : ℝ) + 2))) :
    exp μ * pairT k ρ (n + 2) - exp (-μ) * pairT k ρ n ≤ 2 * exp μ
        * (ccT (xcrit k) ρ * ccT (xcrit k) k) := by
  have hk1 : 1 ≤ k := by omega
  have hk' : ρ + (n + 2) = k := by omega
  have e1 : pairT k ρ (n + 2) =
      ∑ b ∈ range (n + 1), ccT (xcrit k) (ρ + (b + 1)) * ccT (xcrit k) (ρ + (n + 2 - (b + 1))) +
        ccT (xcrit k) (ρ + 0) * ccT (xcrit k) (ρ + (n + 2 - 0)) +
          ccT (xcrit k) (ρ + (n + 2)) * ccT (xcrit k) (ρ + (n + 2 - (n + 2))) := by
    rw [pairT_eq, Finset.sum_range_succ, Finset.sum_range_succ']
  have hterm : ∀ b ∈ range (n + 1),
      exp μ * (ccT (xcrit k) (ρ + (b + 1)) * ccT (xcrit k) (ρ + (n + 2 - (b + 1)))) ≤
        exp (-μ) * (ccT (xcrit k) (ρ + b) * ccT (xcrit k) (ρ + (n - b))) := by
    intro b hb
    rw [Finset.mem_range] at hb
    have h1 := ccT_step_down (k := k) (j := ρ + b) hk (by omega) hμ
    have h2 := ccT_step_down (k := k) (j := ρ + (n - b)) hk (by omega) hμ
    have e : ρ + (n + 2 - (b + 1)) = ρ + (n - b) + 1 := by omega
    rw [e]
    have p1 := (ccT_pos (xcrit_pos k) (ρ + b + 1)).le
    have p2 := (ccT_pos (xcrit_pos k) (ρ + (n - b) + 1)).le
    have p3 := (ccT_pos (xcrit_pos k) (ρ + b)).le
    have hprod := mul_le_mul h1 h2 (mul_nonneg (exp_pos μ).le p2) p3
    have hneg := mul_le_mul_of_nonneg_left hprod (exp_pos (-μ)).le
    have hexp : exp (-μ) * exp μ = 1 := by
      rw [← exp_add]
      simp
    have e3 : exp (-μ) * (exp μ * ccT (xcrit k) (ρ + b + 1)
        * (exp μ * ccT (xcrit k) (ρ + (n - b) + 1))) =
        exp μ * (ccT (xcrit k) (ρ + b + 1) * ccT (xcrit k) (ρ + (n - b) + 1)) := by
      linear_combination (exp μ * ccT (xcrit k) (ρ + b + 1) * ccT (xcrit k) (ρ + (n - b) + 1))
          * hexp
    rw [e3] at hneg
    exact hneg
  have hsum := Finset.sum_le_sum hterm
  rw [← Finset.mul_sum, ← Finset.mul_sum] at hsum
  have b1 : ccT (xcrit k) (ρ + 0) * ccT (xcrit k) (ρ + (n + 2 - 0)) = ccT (xcrit k) ρ
      * ccT (xcrit k) k := by
    have h1 : ρ + 0 = ρ := by omega
    have h2 : ρ + (n + 2 - 0) = k := by omega
    rw [h1, h2]
  have b2 : ccT (xcrit k) (ρ + (n + 2)) * ccT (xcrit k) (ρ + (n + 2 - (n + 2))) = ccT (xcrit k) k
      * ccT (xcrit k) ρ := by
    have h1 : ρ + (n + 2 - (n + 2)) = ρ := by omega
    rw [h1, hk']
  rw [e1, b1, b2, pairT_eq]
  linarith

end Parking.FirstLayer