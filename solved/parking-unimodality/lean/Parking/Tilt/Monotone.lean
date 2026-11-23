import Parking.Tilt.CayleySum

/-!
# The environment at the critical tilt does not increase

`zrT_anti_crit`: for every column `k ≥ 2` the tilted environment
`zrT k (xcrit k) N = zr k N * x_k^N` never increases in `N`.

The tilted environment solves the tilted last-car recursion
`(N+1) u_{N+1} = x ∑_{i ≤ N} min(i+1, k) u_i u_{N-i}`, `u_0 = 1` (`zrT_succ`).  A solution of this
recursion that does not increase on the free range `[0, k]` and satisfies `x ∑_{j=1}^{k} u_j ≤ 1`
never increases (`lastcar_antitone`).  On the free range the environment is the tilted Cayley
mass `ccT (xcrit k) N`, which does not increase there (`ccT_succ_le`), and the second hypothesis
is the bound on the Cayley sum

  `x_k ∑_{j=1}^{k} c_j x_k^j ≤ 1`.

For `k ≥ 12` this is `cayleySum_le_one`, proved by estimates.  For `2 ≤ k ≤ 11` it is a
comparison of two explicit rational numbers, evaluated for the ten columns.
-/

namespace Parking
open Finset

/-- A sequence with `u 0 = 1` solving the tilted last-car recursion with threshold `y`, which
does not increase on its free range `[0, y]` and satisfies `x ∑_{j=1}^{y} u_j ≤ 1`, never
increases.

Proof: with `D_N = u_N - u_{N+1}` and `m_i = min(i+1, y)`, subtracting the recursion at `N - 1`
from the one at `N` gives `(N+1) D_N = (1 - x y) u_N + x ∑_{i<N} m_i u_i D_{N-1-i}` for `N ≥ y`.
By induction the differences `D_j`, `j < N`, are nonnegative.  Keeping the terms `i = N-1-j`,
`j < y`, where `m_i ≥ y - j` and `u_i ≥ u_N`, and using
`∑_{j<y} (y-j) D_j = y - ∑_{j=1}^{y} u_j`, one gets
`(N+1) D_N ≥ u_N (1 - x ∑_{j=1}^{y} u_j) ≥ 0`. -/
private theorem lastcar_antitone {y : ℕ} {x : ℝ} {u : ℕ → ℝ} (hy : 1 ≤ y) (hx : 0 ≤ x)
    (hu0 : u 0 = 1)
    (hsucc : ∀ N : ℕ, ((N : ℝ) + 1) * u (N + 1)
      = x * ∑ i ∈ range (N + 1), ((min (i + 1) y : ℕ) : ℝ) * u i * u (N - i))
    (hfree : ∀ N, N < y → u (N + 1) ≤ u N)
    (hS : x * ∑ j ∈ Icc 1 y, u j ≤ 1) :
    ∀ N, u (N + 1) ≤ u N := by
  have hS' : x * ∑ j ∈ range y, u (j + 1) ≤ 1 := by
    rw [← Finset.Ico_add_one_right_eq_Icc, Finset.sum_Ico_eq_sum_range, Nat.add_sub_cancel] at hS
    simpa only [add_comm 1] using hS
  -- the sequence is nonnegative
  have hnn : ∀ N, 0 ≤ u N := by
    intro N
    induction N using Nat.strong_induction_on with
    | _ N ih =>
      rcases N with _ | N
      · rw [hu0]
        exact zero_le_one
      · have h : 0 ≤ ((N : ℝ) + 1) * u (N + 1) := by
          rw [hsucc N]
          refine mul_nonneg hx (Finset.sum_nonneg fun i hi => ?_)
          have hi' := Finset.mem_range.mp hi
          exact mul_nonneg (mul_nonneg (Nat.cast_nonneg _) (ih i (by omega)))
            (ih (N - i) (by omega))
        exact nonneg_of_mul_nonneg_right h (by positivity)
  intro N
  induction N using Nat.strong_induction_on with
  | _ N ih =>
    rcases Nat.lt_or_ge N y with hNy | hyN
    · exact hfree N hNy
    obtain ⟨n, rfl⟩ : ∃ n, N = n + 1 := ⟨N - 1, by omega⟩
    -- by induction, the sequence does not increase up to the index `n + 1`
    have hD : ∀ j, j ≤ n → 0 ≤ u j - u (j + 1) := fun j hj => sub_nonneg.mpr (ih j (by omega))
    have hmono : ∀ d i, i + d = n + 1 → u (n + 1) ≤ u i := by
      intro d
      induction d with
      | zero =>
        intro i hi
        rw [show i = n + 1 by omega]
      | succ d ihd =>
        intro i hi
        exact (ihd (i + 1) (by omega)).trans (ih i (by omega))
    -- the recursion at `n + 1`, with the last term `i = n + 1` split off
    have h1 : ((n : ℝ) + 1 + 1) * u (n + 1 + 1)
        = x * (∑ i ∈ range (n + 1), ((min (i + 1) y : ℕ) : ℝ) * u i * u (n + 1 - i)
            + (y : ℝ) * u (n + 1)) := by
      have h := hsucc (n + 1)
      rw [Finset.sum_range_succ, Nat.sub_self, hu0, mul_one,
        min_eq_right (show y ≤ n + 1 + 1 by omega), Nat.cast_add, Nat.cast_one] at h
      exact h
    -- `(n+2) D_{n+1} = (1 - x y) u_{n+1} + x ∑_{i ≤ n} m_i u_i (u_{n-i} - u_{n+1-i})`
    have hkey : ((n : ℝ) + 1 + 1) * (u (n + 1) - u (n + 1 + 1))
        = (1 - x * (y : ℝ)) * u (n + 1)
          + x * ∑ i ∈ range (n + 1),
              ((min (i + 1) y : ℕ) : ℝ) * u i * (u (n - i) - u (n + 1 - i)) := by
      have h0 := hsucc n
      simp only [mul_sub, Finset.sum_sub_distrib]
      linarith
    -- reflection `i = n - j`
    have hre : ∑ i ∈ range (n + 1), ((min (i + 1) y : ℕ) : ℝ) * u i * (u (n - i) - u (n + 1 - i))
        = ∑ j ∈ range (n + 1), ((min (n - j + 1) y : ℕ) : ℝ) * u (n - j) * (u j - u (j + 1)) := by
      refine (Finset.sum_range_reflect
        (fun i => ((min (i + 1) y : ℕ) : ℝ) * u i * (u (n - i) - u (n + 1 - i))) (n + 1)).symm.trans
        (Finset.sum_congr rfl fun j hj => ?_)
      have hj' := Finset.mem_range.mp hj
      simp only [show n + 1 - 1 - j = n - j by omega, show n - (n - j) = j by omega,
        show n + 1 - (n - j) = j + 1 by omega]
    -- keep the terms `j < y`, where `m_{n-j} ≥ y - j` and `u_{n-j} ≥ u_{n+1}`
    have hlow1 : ∑ j ∈ range y, ((y : ℝ) - j) * u (n + 1) * (u j - u (j + 1))
        ≤ ∑ j ∈ range y, ((min (n - j + 1) y : ℕ) : ℝ) * u (n - j) * (u j - u (j + 1)) := by
      refine Finset.sum_le_sum fun j hj => ?_
      have hj' := Finset.mem_range.mp hj
      have hm : (y : ℝ) - j ≤ ((min (n - j + 1) y : ℕ) : ℝ) := by
        rw [← Nat.cast_sub hj'.le]
        exact Nat.cast_le.mpr (le_min (by omega) (Nat.sub_le y j))
      exact mul_le_mul_of_nonneg_right
        (mul_le_mul hm (hmono (j + 1) (n - j) (by omega)) (hnn _) (Nat.cast_nonneg _))
        (hD j (by omega))
    have hlow2 : ∑ j ∈ range y, ((min (n - j + 1) y : ℕ) : ℝ) * u (n - j) * (u j - u (j + 1))
        ≤ ∑ j ∈ range (n + 1),
            ((min (n - j + 1) y : ℕ) : ℝ) * u (n - j) * (u j - u (j + 1)) :=
      Finset.sum_le_sum_of_subset_of_nonneg (Finset.range_subset_range.mpr hyN) fun j hj _ =>
        mul_nonneg (mul_nonneg (Nat.cast_nonneg _) (hnn _))
          (hD j (Nat.lt_succ_iff.mp (Finset.mem_range.mp hj)))
    -- Abel summation: `∑_{j<t} (y - j) D_j = y u_0 - (y - t) u_t - ∑_{j<t} u_{j+1}`
    have hab : ∀ t : ℕ, ∑ j ∈ range t, ((y : ℝ) - j) * u (n + 1) * (u j - u (j + 1))
        = u (n + 1) * ((y : ℝ) * u 0 - ((y : ℝ) - t) * u t - ∑ j ∈ range t, u (j + 1)) := by
      intro t
      induction t with
      | zero => simp
      | succ t iht =>
        rw [Finset.sum_range_succ, Finset.sum_range_succ, iht, Nat.cast_add, Nat.cast_one]
        ring
    have hfin : 0 ≤ ((n : ℝ) + 1 + 1) * (u (n + 1) - u (n + 1 + 1)) := by
      have hT := mul_le_mul_of_nonneg_left (hlow1.trans hlow2) hx
      rw [hab y, hu0, sub_self, zero_mul] at hT
      have hpos := mul_nonneg (hnn (n + 1)) (sub_nonneg.mpr hS')
      rw [hkey, hre]
      linarith
    exact sub_nonneg.mp (nonneg_of_mul_nonneg_right hfin (by positivity))

/-- The Cayley sum as an explicit sum. -/
private theorem cayleySum_eq_range (x : ℝ) (k : ℕ) :
    x * ∑ j ∈ Icc 1 k, ccT x j
      = ∑ i ∈ range k,
          ((i : ℝ) + 1 + 1) ^ (i + 1) / ((i + 1 + 1).factorial : ℝ) * x ^ (i + 1 + 1) := by
  rw [sum_Icc_one_eq_range, mul_sum]
  refine sum_congr rfl fun i _ => ?_
  rw [ccT, cc_eq]
  push_cast
  ring

/-- The bound on the Cayley sum, `x_k ∑_{j=1}^{k} c_j x_k^j ≤ 1`, for `2 ≤ k ≤ 11`. -/
private theorem cayleySum_small {k : ℕ} (h2 : 2 ≤ k) (h12 : k < 12) :
    xcrit k * ∑ j ∈ Icc 1 k, ccT (xcrit k) j ≤ 1 := by
  obtain rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl :
      k = 2 ∨ k = 3 ∨ k = 4 ∨ k = 5 ∨ k = 6 ∨ k = 7 ∨ k = 8 ∨ k = 9 ∨ k = 10 ∨ k = 11 := by
    omega
  all_goals
    rw [cayleySum_eq_range, xcrit]
    norm_num [Finset.sum_range_succ, Nat.factorial]

/-- **The environment at the critical tilt does not increase**: for every column `k ≥ 2` the
sequence `zr k N * x_k^N` is nonincreasing in `N`. -/
theorem zrT_anti_crit {k : ℕ} (hk : 2 ≤ k) : ∀ N, zrT k (xcrit k) (N + 1) ≤ zrT k (xcrit k) N := by
  have hk1 : 1 ≤ k := by omega
  have hx : 0 < xcrit k := xcrit_pos k
  refine lastcar_antitone hk1 hx.le (zrT_zero hk1 (xcrit k)) (zrT_succ hk1 (xcrit k))
    (fun N hN => ?_) ?_
  · -- on the free range the environment is the tilted Cayley mass
    rw [zrT_eq_ccT hk1 _ (show N + 1 ≤ k by omega), zrT_eq_ccT hk1 _ (show N ≤ k by omega)]
    exact ccT_succ_le (show N + 1 ≤ k by omega)
  · have e : ∑ j ∈ Icc 1 k, zrT k (xcrit k) j = ∑ j ∈ Icc 1 k, ccT (xcrit k) j :=
      Finset.sum_congr rfl fun j hj => zrT_eq_ccT hk1 _ (Finset.mem_Icc.mp hj).2
    rw [e]
    rcases Nat.lt_or_ge k 12 with h | h
    · exact cayleySum_small hk h
    · exact cayleySum_le_one h

end Parking
