module

public import Parking.Series.AllRows

/-!
# Critical-tilt propagation

Fix a column `k ≥ 2`, a tilt `x > 0` for which the tilted environment `zrT k x` is nonincreasing,
and a row `n0 ≥ k` such that all suffix sums

  `∑_{t = s}^{n0} ξ_t x^t ≥ 0`   (`k ≤ s ≤ n0`)

are nonnegative.  Then `dq k n ≥ 0` for every `n ≥ n0` (`propagate`).

Proof.  Invariant `I(n)`: all suffix sums up to `n` are nonnegative.
(i) `I(n) ⇒ dq k n ≥ 0`: by the one-tree bound,
`dq k n · x^n ≥ ∑_{t=k}^{n} (ξ_t x^t) · zrT k x (n-t)`, the weights `zrT k x (n-t)` are nonnegative
and nondecreasing in `t`, and Abel summation gives `∑_{t=k}^{n} a_t w_t ≥ w_k ∑_{t=k}^{n} a_t ≥ 0`
(`abel_suffix`). (ii) `dq k n ≥ 0`, `n ≥ k` `⇒ ξ_{n+1} ≥ 0`, because
`(n+1) ξ_{n+1} = (k+1) · dq k n + 2 · bq (k-1) n` (`xi_succ_nonneg`).
(iii) `I(n)` and `ξ_{n+1} ≥ 0` give `I(n+1)`.
-/

@[expose] public section

namespace Parking
open Finset

/-- Abel summation: if all suffix sums of `a` over `[s, n]` (`k ≤ s`) are nonnegative and the
weight `w` is nondecreasing on `[k, n]`, then `w s · ∑_{t=s}^{n} a_t ≤ ∑_{t=s}^{n} a_t w_t`. -/
private theorem abel_suffix (a w : ℕ → ℝ) {k n : ℕ}
    (hw : ∀ s, k ≤ s → s < n → w s ≤ w (s + 1))
    (hS : ∀ s, k ≤ s → s ≤ n → 0 ≤ ∑ t ∈ Icc s n, a t) {s : ℕ} (hks : k ≤ s) (hsn : s ≤ n) :
    w s * ∑ t ∈ Icc s n, a t ≤ ∑ t ∈ Icc s n, a t * w t := by
  obtain ⟨j, hj⟩ : ∃ j, s + j = n := ⟨n - s, by omega⟩
  induction j generalizing s with
  | zero =>
    obtain rfl : s = n := by omega
    rw [Finset.Icc_self, Finset.sum_singleton, Finset.sum_singleton, mul_comm]
  | succ j ih =>
    have h1 := ih (s := s + 1) (by omega) (by omega) (by omega)
    have h2 : w s * ∑ t ∈ Icc (s + 1) n, a t ≤ w (s + 1) * ∑ t ∈ Icc (s + 1) n, a t :=
      mul_le_mul_of_nonneg_right (hw s hks (by omega)) (hS (s + 1) (by omega) (by omega))
    -- split off the terms of index `s`
    rw [← Finset.add_sum_Ioc_eq_sum_Icc hsn, ← Finset.add_sum_Ioc_eq_sum_Icc hsn,
      ← Finset.Icc_add_one_left_eq_Ioc]
    linarith

/-- The curvature of the next tree: `(n+1) ξ_{n+1} = (k+1) · dq k n + 2 · bq (k-1) n` for
`n ≥ k`; hence `ξ_{n+1} ≥ 0` when `dq k n ≥ 0`. -/
private theorem xi_succ_nonneg {k n : ℕ} (hk : 2 ≤ k) (hn : k ≤ n) (hd : 0 ≤ dq k n) :
    0 ≤ xi k (n + 1) := by
  have h1 : 0 ≤ ((k : ℝ) + 1) * dq k n := mul_nonneg (by positivity) hd
  have h2 := bq_nonneg (k - 1) n
  refine nonneg_of_mul_nonneg_right ?_ (show (0 : ℝ) < (n : ℝ) + 1 by positivity)
  rw [succ_mul_xi_succ hk hn]
  linarith

/-- Critical-tilt propagation. -/
theorem propagate {k n0 : ℕ} (hk : 2 ≤ k) (hn0 : k ≤ n0) {x : ℝ} (hx : 0 < x)
    (hanti : ∀ N, zrT k x (N + 1) ≤ zrT k x N)
    (hsuf : ∀ s, k ≤ s → s ≤ n0 → 0 ≤ ∑ t ∈ Icc s n0, xi k t * x ^ t) :
    ∀ n, n0 ≤ n → 0 ≤ dq k n := by
  -- (i) the invariant at `n` gives `dq k n ≥ 0`
  have step1 : ∀ n, k ≤ n →
      (∀ s, k ≤ s → s ≤ n → 0 ≤ ∑ t ∈ Icc s n, xi k t * x ^ t) → 0 ≤ dq k n := by
    intro n hkn hI
    have hxn : 0 < x ^ n := pow_pos hx n
    -- the one-tree bound, tilted; the terms with `t < k` vanish
    have h1 : ∑ t ∈ range (n + 1), xi k t * zr k (n - t) * x ^ n
        = ∑ t ∈ range (n + 1), xi k t * x ^ t * zrT k x (n - t) := by
      refine Finset.sum_congr rfl fun t ht => ?_
      rw [Finset.mem_range] at ht
      rw [zrT, show x ^ n = x ^ t * x ^ (n - t) by
        rw [← pow_add, Nat.add_sub_cancel' (by omega : t ≤ n)]]
      ring
    have h2 : ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t)
        = ∑ t ∈ range (n + 1), xi k t * x ^ t * zrT k x (n - t) := by
      refine Finset.sum_subset (fun t ht => ?_) fun t ht ht' => ?_
      · rw [Finset.mem_Icc] at ht
        rw [Finset.mem_range]
        omega
      · rw [Finset.mem_Icc] at ht'
        rw [Finset.mem_range] at ht
        rw [xi_eq_zero hk (by omega), zero_mul, zero_mul]
    have hmul : ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t) ≤ dq k n * x ^ n := by
      rw [h2, ← h1, ← Finset.sum_mul]
      exact mul_le_mul_of_nonneg_right (one_tree_bound hk n) hxn.le
    -- Abel summation with the weights `zrT k x (n - t)`
    have hw : ∀ s, k ≤ s → s < n → zrT k x (n - s) ≤ zrT k x (n - (s + 1)) := by
      intro s _ hsn
      rw [show n - s = n - (s + 1) + 1 by omega]
      exact hanti (n - (s + 1))
    have habel : zrT k x (n - k) * ∑ t ∈ Icc k n, xi k t * x ^ t
        ≤ ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t) :=
      abel_suffix (fun t => xi k t * x ^ t) (fun t => zrT k x (n - t)) hw hI (le_refl k) hkn
    have hpos : 0 ≤ zrT k x (n - k) * ∑ t ∈ Icc k n, xi k t * x ^ t :=
      mul_nonneg (zrT_nonneg k hx.le (n - k)) (hI k (le_refl k) hkn)
    exact nonneg_of_mul_nonneg_left (le_trans hpos (le_trans habel hmul)) hxn
  -- (iii) the invariant is inherited
  have step3 : ∀ n, k ≤ n →
      (∀ s, k ≤ s → s ≤ n → 0 ≤ ∑ t ∈ Icc s n, xi k t * x ^ t) →
      ∀ s, k ≤ s → s ≤ n + 1 → 0 ≤ ∑ t ∈ Icc s (n + 1), xi k t * x ^ t := by
    intro n hkn hI s hks hsn
    have hxi : 0 ≤ xi k (n + 1) * x ^ (n + 1) :=
      mul_nonneg (xi_succ_nonneg hk hkn (step1 n hkn hI)) (pow_pos hx (n + 1)).le
    rcases Nat.lt_or_ge n s with h | h
    · rw [show s = n + 1 by omega, Finset.Icc_self, Finset.sum_singleton]
      exact hxi
    · rw [Finset.sum_Icc_succ_top (by omega : s ≤ n + 1)]
      exact add_nonneg (hI s hks h) hxi
  -- the invariant holds from `n0` on
  have hinv : ∀ n, n0 ≤ n → ∀ s, k ≤ s → s ≤ n → 0 ≤ ∑ t ∈ Icc s n, xi k t * x ^ t := by
    intro n hn
    induction n, hn using Nat.le_induction with
    | base => exact hsuf
    | succ n hn ih => exact step3 n (le_trans hn0 hn) ih
  intro n hn
  exact step1 n (le_trans hn0 hn) (hinv n hn)

end Parking