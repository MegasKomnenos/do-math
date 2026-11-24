import Parking.LeftHalf.Propagate
import Batteries.Tactic.OpenPrivate

/-!
# The step bound, and how a positive step propagates down a column

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`,
`d_{n,k} = b n k - b n (k-1)` is the step of column `k` in the row `n`, and `dq k n = d_{n,k}/n!`.

Fix a column `k ≥ 2` and a tilt `x > 0` for which the tilted environment
`u_N = zrT k x N = z^{(k)}_N x^N` does not increase in `N`.  The numbers `ξ_t = xi k t` are the tree
curvatures of the column.  The propagation theorem `propagate` shows: if all the sums
`∑_{s ≤ t ≤ n} ξ_t x^t`, `k ≤ s ≤ n`, are nonnegative at one row `n = n0`, then `d_{n,k} ≥ 0` in
every row `n ≥ n0`.  This file gives the form of that theorem with strict signs.

* `step_bound` : if all the sums `∑_{s ≤ t ≤ n} ξ_t x^t`, `k ≤ s ≤ n`, are nonnegative at the row
  `n ≥ k`, then `(1 - x) ξ_n ≤ dq k n`.
* `propagate_pos` : if moreover `x < 1`, the sums are nonnegative at the row `m + 1`, and the step
  is positive in the row `m ≥ k`, then the step is positive in every row `n ≥ m`.

Proof of the step bound.  By the one-tree bound `one_tree_bound`, multiplied by `x^n`,

  `dq k n · x^n ≥ ∑_{t=k}^{n} a_t u_{n-t}`,   `a_t = ξ_t x^t`,

where `u_0 = 1` and `u_1 = x`.  Lower the last weight from `u_0` to `u_1`, that is, take the
weights `w_t = u_{max(n-t, 1)}`.  They are nonnegative and do not decrease in `t`, so Abel summation
(`abel_suffix`, a private lemma of `Parking.LeftHalf.Propagate`) and the nonnegative sums give
`∑_{t=k}^{n} a_t w_t ≥ 0`.  The two sums differ in the term `t = n` only, by
`a_n (u_0 - u_1) = ξ_n x^n (1 - x)`.

Proof of the propagation.  Since `(n+1) ξ_{n+1} = (k+1) dq k n + 2 bq (k-1) n`, a positive step in
the row `n` makes `ξ_{n+1}` positive.  A positive `ξ_{n+1}` gives `dq k (n+1) > 0` by the step
bound, and a positive `ξ_{n+2}` keeps all the sums nonnegative at the row `n + 2`.
-/

namespace Parking
open Finset

open private abel_suffix from Parking.LeftHalf.Propagate

/-- The tilted environment at `N = 1` is the tilt: `z^{(k)}_1 x = x`. -/
private theorem zrT_one {k : ℕ} (hk : 1 ≤ k) (x : ℝ) : zrT k x 1 = x := by
  rw [zrT_eq_ccT hk x hk, ccT, cc_eq]
  norm_num [Nat.factorial]

/-- A positive step in the row `n ≥ k` makes the next tree curvature positive: `ξ_{n+1} > 0`,
because `(n+1) ξ_{n+1} = (k+1) · dq k n + 2 · bq (k-1) n`. -/
private theorem xi_succ_pos {k n : ℕ} (hk : 2 ≤ k) (hn : k ≤ n) (hd : 0 < dq k n) :
    0 < xi k (n + 1) := by
  have h1 : 0 < ((k : ℝ) + 1) * dq k n := mul_pos (by positivity) hd
  have h2 := bq_nonneg (k - 1) n
  refine (mul_pos_iff_of_pos_left (show (0 : ℝ) < (n : ℝ) + 1 by positivity)).mp ?_
  rw [succ_mul_xi_succ hk hn]
  linarith

/-- **The step bound.**  Let `k ≥ 2`, and let `x > 0` be a tilt for which the tilted environment
`zrT k x` does not increase.  If all the sums `∑_{s ≤ t ≤ n} ξ_t x^t`, `k ≤ s ≤ n`, are nonnegative
at a row `n ≥ k`, then `(1 - x) ξ_n ≤ d_{n,k}/n!`.

By the one-tree bound, `dq k n · x^n ≥ ∑_{t=k}^{n} ξ_t x^t · u_{n-t}` with `u_N = zrT k x N`.  With
the last weight lowered from `u_0 = 1` to `u_1 = x` the weights still do not decrease, so Abel
summation makes that sum nonnegative; what was removed is `ξ_n x^n (1 - x)`. -/
theorem step_bound {k n : ℕ} (hk : 2 ≤ k) (hkn : k ≤ n) {x : ℝ} (hx : 0 < x)
    (hanti : ∀ N, zrT k x (N + 1) ≤ zrT k x N)
    (hI : ∀ s, k ≤ s → s ≤ n → 0 ≤ ∑ t ∈ Icc s n, xi k t * x ^ t) :
    (1 - x) * xi k n ≤ dq k n := by
  have hk1 : 1 ≤ k := by omega
  have hxn : 0 < x ^ n := pow_pos hx n
  -- the one-tree bound, tilted; the terms with `t < k` vanish
  have hone : ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t) ≤ dq k n * x ^ n := by
    have h1 : ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t)
        = (∑ t ∈ range (n + 1), xi k t * zr k (n - t)) * x ^ n := by
      rw [Finset.sum_mul]
      refine Finset.sum_subset_zero_on_sdiff (fun t ht => ?_) (fun t ht => ?_) (fun t ht => ?_)
      · rw [Finset.mem_Icc] at ht
        rw [Finset.mem_range]
        omega
      · rw [Finset.mem_sdiff, Finset.mem_range, Finset.mem_Icc] at ht
        rw [xi_eq_zero hk (by omega), zero_mul, zero_mul]
      · rw [Finset.mem_Icc] at ht
        rw [zrT, show x ^ n = x ^ t * x ^ (n - t) by rw [← pow_add, Nat.add_sub_cancel' ht.2]]
        ring
    rw [h1]
    exact mul_le_mul_of_nonneg_right (one_tree_bound hk n) hxn.le
  -- Abel summation with the weights `w_t = u_{max(n-t, 1)}`
  have hmono : Antitone (zrT k x) := antitone_nat_of_succ_le hanti
  have habel : zrT k x (max (n - k) 1) * ∑ t ∈ Icc k n, xi k t * x ^ t
      ≤ ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (max (n - t) 1) :=
    abel_suffix (fun t => xi k t * x ^ t) (fun t => zrT k x (max (n - t) 1))
      (fun s _ _ => hmono (by omega)) hI (le_refl k) hkn
  have hpos : 0 ≤ ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (max (n - t) 1) :=
    le_trans (mul_nonneg (zrT_nonneg k hx.le _) (hI k (le_refl k) hkn)) habel
  -- the two weighted sums differ in the term `t = n` only
  have hdiff : ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (n - t)
      - ∑ t ∈ Icc k n, xi k t * x ^ t * zrT k x (max (n - t) 1)
      = (1 - x) * xi k n * x ^ n := by
    have e : max (n - n) 1 = 1 := by omega
    rw [← Finset.sum_sub_distrib,
      Finset.sum_eq_single_of_mem n (Finset.mem_Icc.mpr ⟨hkn, le_refl n⟩) (fun t ht hne => ?_),
      e, Nat.sub_self, zrT_zero hk1, zrT_one hk1]
    · ring
    · rw [Finset.mem_Icc] at ht
      rw [max_eq_left (by omega : 1 ≤ n - t), sub_self]
  have hfin : (1 - x) * xi k n * x ^ n ≤ dq k n * x ^ n := by linarith
  exact le_of_mul_le_mul_right hfin hxn

/-- **Propagation of a positive step.**  Let `k ≥ 2`, and let `0 < x < 1` be a tilt for which the
tilted environment `zrT k x` does not increase.  If the step of column `k` is positive in a row
`m ≥ k` and all the sums `∑_{s ≤ t ≤ m+1} ξ_t x^t`, `k ≤ s ≤ m + 1`, are nonnegative, then the step
of column `k` is positive in every row `n ≥ m`.

Induction on `n`, carrying the nonnegative sums at the row `n + 1` and the positive step in the
row `n`: the positive step makes `ξ_{n+1}` positive, the step bound gives
`dq k (n+1) ≥ (1 - x) ξ_{n+1} > 0`, and the positive `ξ_{n+2}` keeps the sums nonnegative at the
row `n + 2`. -/
theorem propagate_pos {k m : ℕ} (hk : 2 ≤ k) (hkm : k ≤ m) {x : ℝ} (hx : 0 < x) (hx1 : x < 1)
    (hanti : ∀ N, zrT k x (N + 1) ≤ zrT k x N)
    (hsuf : ∀ s, k ≤ s → s ≤ m + 1 → 0 ≤ ∑ t ∈ Icc s (m + 1), xi k t * x ^ t)
    (hm : 0 < dq k m) :
    ∀ n, m ≤ n → 0 < dq k n := by
  have key : ∀ n, m ≤ n →
      (∀ s, k ≤ s → s ≤ n + 1 → 0 ≤ ∑ t ∈ Icc s (n + 1), xi k t * x ^ t) ∧ 0 < dq k n := by
    intro n hn
    induction n, hn using Nat.le_induction with
    | base => exact ⟨hsuf, hm⟩
    | succ n hn ih =>
      obtain ⟨hI, hd⟩ := ih
      have hd' : 0 < dq k (n + 1) :=
        lt_of_lt_of_le (mul_pos (sub_pos.mpr hx1) (xi_succ_pos hk (by omega) hd))
          (step_bound hk (by omega) hx hanti hI)
      have hxi : 0 ≤ xi k (n + 1 + 1) * x ^ (n + 1 + 1) :=
        (mul_pos (xi_succ_pos hk (by omega) hd') (pow_pos hx _)).le
      refine ⟨fun s hks hsn => ?_, hd'⟩
      rcases Nat.lt_or_ge (n + 1) s with h | h
      · rw [show s = n + 1 + 1 by omega, Finset.Icc_self, Finset.sum_singleton]
        exact hxi
      · rw [Finset.sum_Icc_succ_top (by omega : s ≤ n + 1 + 1)]
        exact add_nonneg (hI s hks h) hxi
  exact fun n hn => (key n hn).2

end Parking
