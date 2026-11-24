import Parking.NextColumn.Frozen

/-!
# The curvature sum, and the curvature term of the frozen polynomial

For a threshold `y` and a size `N` the chain sum `Λ_m(y;N) = Lam (thr y N) m` is the total weight
of the compositions of `m` for the profile `s ↦ y/(N-s)`.  The curvature sum is the second
difference in the threshold of `y · Λ_m(y;N)`,

`curvSum y N m = (y+1) Λ_m(y+1;N) - 2 y Λ_m(y;N) + (y-1) Λ_m(y-1;N)`.

* `curvSum_eq_sum` : `curvSum y N m = ∑_Q ((y+1)^Q - 2y^Q + (y-1)^Q) · V_{m,Q}` with
  `V_{m,Q} = Vc (thr 1 N) Q m`, because `y · Λ_m(y;N) = ∑_Q y^Q · V_{m,Q}`.
* `Kpoly_second_diff` : the frozen polynomial is
  `Kpoly j n y = κ_j(N) + ∑_{m=1}^{n-j} κ_j(N-m)/(N-m) · y · Λ_m(y;N)` with `N = n + 1` and
  `κ_j = kap j`, so its second difference in `y` is `∑_{m=1}^{n-j} κ_j(N-m)/(N-m) · curvSum y N m`.

In `dq_frozen` the curvature term of a step is a second difference of a frozen polynomial.  The
pair–impulse criterion (`curv_ge_pair`) and the diagonal step (`dq_curv_sub_boundary`) both write it
out by `Kpoly_second_diff`.
-/

namespace Parking

open Finset

/-- The curvature sum: the second difference in the threshold `y` of `y · Λ_m(y;N)`, where
`Λ_m(y;N) = Lam (thr y N) m` is the chain sum for the profile `s ↦ y/(N-s)`. -/
noncomputable def curvSum (y N : ℝ) (m : ℕ) : ℝ :=
  (y + 1) * Lam (thr (y + 1) N) m - 2 * (y * Lam (thr y N) m) + (y - 1) * Lam (thr (y - 1) N) m

/-- The curvature sum by the number of parts:
`curvSum y N m = ∑_Q ((y+1)^Q - 2y^Q + (y-1)^Q) · V_{m,Q}`, `V_{m,Q} = Vc (thr 1 N) Q m`. -/
theorem curvSum_eq_sum (y N : ℝ) (m : ℕ) :
    curvSum y N m
      = ∑ Q ∈ Icc 1 m, ((y + 1) ^ Q - 2 * y ^ Q + (y - 1) ^ Q) * Vc (thr 1 N) Q m := by
  have h : ∀ z : ℝ, z * Lam (thr z N) m = ∑ Q ∈ Icc 1 m, z ^ Q * Vc (thr 1 N) Q m := fun z => by
    rw [Lam_thr, Finset.mul_sum]
    refine Finset.sum_congr rfl fun Q hQ => ?_
    rw [← mul_assoc, ← pow_succ', Nat.sub_add_cancel (mem_Icc.mp hQ).1]
  unfold curvSum
  rw [h (y + 1), h y, h (y - 1), Finset.mul_sum, ← Finset.sum_sub_distrib,
    ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun Q _ => by ring

/-- **The curvature term of the frozen polynomial.**  With `N = n + 1`, the second difference in
`y` of `Kpoly j n y` is `∑_{m=1}^{n-j} κ_j(N-m)/(N-m) · curvSum y N m`, `κ_j = kap j`: the frozen
polynomial is `κ_j(N) + ∑_m κ_j(N-m)/(N-m) · y · Λ_m(y;N)`, the constant term cancels, and the
second difference of `y · Λ_m(y;N)` is the curvature sum. -/
theorem Kpoly_second_diff (j n : ℕ) (y : ℝ) :
    Kpoly j n (y + 1) - 2 * Kpoly j n y + Kpoly j n (y - 1)
      = ∑ m ∈ Icc 1 (n - j),
          kap j (n + 1 - m) / ((n : ℝ) + 1 - m) * curvSum y ((n : ℝ) + 1) m := by
  unfold Kpoly curvSum
  rw [show ∀ c x y z : ℝ, c + x - 2 * (c + y) + (c + z) = x - 2 * y + z from
    fun c x y z => by ring, Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun m _ => by ring

end Parking
