import Parking.NextColumn.Frozen
import Staircase.Cayley.CurvatureSum
import Staircase.Cayley.MarkedCuts
import Batteries.Tactic.OpenPrivate

/-!
# The pair–impulse criterion

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`,
`A n l` the number of those with all displacements at most `l`, and `d(n,k) = b n k - b n (k-1)`
is the step of column `k` in the row `n`.  The environment of column `k` is the sequence of the
normalised counts `zr k n = A n (k-1)/n!`.  Write `a_j = cay j`, `κ_j = kap j`, and
`Λ_m(y; N) = Lam (thr y N) m` for the total weight of the compositions of `m` with the cut factors
`y/(N-s)`; `Lam1 f m` and `Lam2 f m` are the total weights of the compositions of `m` with one and
with two marked cut points (`Staircase/Cayley/MarkedCuts.lean`).

Fix a column `k` and a row `n = k + R - 1` with `1 ≤ R ≤ k - 2`, and put `N = k + R`.  These rows,
`k ≤ n ≤ 2k - 3`, are the first layer of the column `k - 1`; all of them but the row `n = k` lie in
the first layer of the column `k` as well.  `dq_frozen` (`Parking.NextColumn.Frozen`), at the
column `k - 1`, writes the normalised step `dq k n = d(n,k)/n!` as a curvature term minus a
boundary term: the second difference in `y` at `y = k` of the frozen
polynomial `Kpoly (k-1) n y = κ_{k-1}(N) + ∑_{m=1}^{R} κ_{k-1}(N-m)/(N-m) · y · Λ_m(y; N)`, minus
`(a_k/k) · Λ_R(k+1; N)`.

This module bounds the curvature term from below by a sum over pairs of marked cut points,

`pairSum k R = ∑_{1≤a<b≤R} Λ_a(k;N) · k/(N-a) · Λ_{b-a}(k;N-a) · k/(N-b) · zr k (N-b-1)`,

and so obtains a criterion in which the step no longer occurs:

* `curv_ge_pair` : `2 · pairSum k R ≤ k² ·` (the second difference of `Kpoly (k-1) n` at `k`);
* `dq_pos_of_pair` : if `k · a_k · Λ_R(k+1; N) < 2 · pairSum k R`, then `dq k n > 0`.

Why the pair sum appears.  As a polynomial in `y`, the frozen polynomial has nonnegative
coefficients, and a composition with `q` parts contributes to the coefficient of `y^q`.  For a
polynomial with nonnegative coefficients, `k²` times the second difference at `k` is at least the
sum of `q(q-1) · (coefficient of y^q) · k^q` (`second_diff_pow`), and `q(q-1)/2` is the number of
ways to mark one or two of the `q - 1` cut points (`sum_qq_Vc`).  This gives the curvature as a sum
over `m` of `κ(N-m) · k/(N-m) · (Lam1 + Lam2)(m)` with `κ = kap (k-1)`.  On the other side the
environment `Z(b) = zr k (N-b-1)` solves the Volterra equation `zr_volterra`, which holds in the
rows up to `2k - 1` and in the coordinate `b` reads
`Z(b) = κ(N-b) + ∑_{b<m≤R} a_{m-b} · k/(N-m) · Z(m)`, while `Lam1 + Lam2` solves the adjoint
equation `G(m) = Lam1(m) + ∑_{s<m} a_{m-s} · k/(N-s) · G(s)` (`Lam2_last`).
Pairing the two equations identifies the two sums (`volterra_duality`, `pairSum_eq`).
-/

namespace Parking

open Finset

open private sum_Ioo_shift from Parking.NextColumn.Compositions
open private sum_Ioo_reflect zr_volterra from Parking.NextColumn.Frozen

/-- The pair sum at the position `(n, k) = (k+R-1, k)`, with `N = k+R`: the sum over the larger
marked cut point `b` of the weight `Lam1 (thr k N) b` of the compositions of `b` with one marked
cut point, the cut factor `k/(N-b)` at `b`, and the environment `zr k (N-b-1)` below `b`. -/
noncomputable def pairSum (k R : ℕ) : ℝ :=
  ∑ b ∈ Icc 1 R, Lam1 (thr (k : ℝ) ((k : ℝ) + R)) b * thr (k : ℝ) ((k : ℝ) + R) b
    * zr k (k + R - b - 1)

/-! ### The second difference of a power -/

/-- For real `k > 0`: `q(q-1) · k^q ≤ k² · ((k+1)^q - 2k^q + (k-1)^q)`, and with it, for the
induction, `2q · k^q ≤ k · ((k+1)^q - (k-1)^q)`.  Writing `D_q` and `E_q` for the two differences,
`D_{q+1} = k·D_q + E_q` and `E_{q+1} = k·E_q + D_q + 2k^q`. -/
private theorem second_diff_pow {k : ℝ} (hk0 : 0 < k) (q : ℕ) :
    (q : ℝ) * ((q : ℝ) - 1) * k ^ q ≤ k ^ 2 * ((k + 1) ^ q - 2 * k ^ q + (k - 1) ^ q)
      ∧ 2 * (q : ℝ) * k ^ q ≤ k * ((k + 1) ^ q - (k - 1) ^ q) := by
  induction q with
  | zero => norm_num
  | succ q ih =>
    obtain ⟨hP, hQ⟩ := ih
    have hqq : (0 : ℝ) ≤ (q : ℝ) * ((q : ℝ) - 1) := by
      rcases Nat.eq_zero_or_pos q with rfl | h
      · simp
      · exact mul_nonneg (Nat.cast_nonneg q) (sub_nonneg.2 (by exact_mod_cast h))
    have hD : 0 ≤ (k + 1) ^ q - 2 * k ^ q + (k - 1) ^ q :=
      (mul_nonneg_iff_of_pos_left (pow_pos hk0 2)).1
        ((mul_nonneg hqq (pow_nonneg hk0.le q)).trans hP)
    have h1 := mul_le_mul_of_nonneg_left hP hk0.le
    have h2 := mul_le_mul_of_nonneg_left hQ hk0.le
    have h3 := mul_nonneg hk0.le hD
    push_cast
    rw [pow_succ k q, pow_succ (k + 1) q, pow_succ (k - 1) q]
    constructor <;> linarith

/-- The curvature sum `curvSum k N m`, the second difference in `y` of `y · Λ_m(y; N)`, at a real
`k > 0` dominates the compositions with one or two marked cut points:
`k · (2·Lam1 + 2·Lam2)(thr k N) m ≤ k² · curvSum k N m`.
Indeed `curvSum k N m = ∑_q ((k+1)^q - 2k^q + (k-1)^q) · V_q` with `V_q = Vc (thr 1 N) q m ≥ 0`
(`curvSum_eq_sum`), the left side is `∑_q q(q-1) · k^q · V_q` by `sum_qq_Vc`, and `second_diff_pow`
compares the two term by term. -/
private theorem chain_second_diff {k N : ℝ} (hk : 0 < k) {m : ℕ} (hN : (m : ℝ) ≤ N) :
    k * (2 * Lam1 (thr k N) m + 2 * Lam2 (thr k N) m) ≤ k ^ 2 * curvSum k N m := by
  have hV : ∀ q, 0 ≤ Vc (thr 1 N) q m := fun q =>
    Vc_nonneg (fun s hs => thr_nonneg zero_le_one
      (le_trans (Nat.cast_le.2 (mem_Ioo.1 hs).2.le) hN)) q
  calc k * (2 * Lam1 (thr k N) m + 2 * Lam2 (thr k N) m)
      = ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * k ^ q * Vc (thr 1 N) q m := by
        rw [← sum_qq_Vc, Finset.mul_sum]
        refine Finset.sum_congr rfl fun q hq => ?_
        obtain ⟨q', rfl⟩ : ∃ q', q = q' + 1 := ⟨q - 1, by have := (mem_Icc.1 hq).1; omega⟩
        rw [Vc_thr, Nat.add_sub_cancel]
        ring
    _ ≤ ∑ q ∈ Icc 1 m, k ^ 2 * ((k + 1) ^ q - 2 * k ^ q + (k - 1) ^ q) * Vc (thr 1 N) q m :=
        Finset.sum_le_sum fun q _ => mul_le_mul_of_nonneg_right (second_diff_pow hk q).1 (hV q)
    _ = k ^ 2 * curvSum k N m := by
        rw [curvSum_eq_sum, Finset.mul_sum]
        exact Finset.sum_congr rfl fun q _ => by ring

/-! ### The pair sum as a sum over the last marked point -/

/-- **Duality of two Volterra equations with the Cayley kernel.** If `Z` solves the equation from
above, `Z(b) = κ(b) + ∑_{b<m≤R} a_{m-b} · f(m) · Z(m)`, and `G` solves the adjoint equation from
below, `G(m) = L(m) + ∑_{0<s<m} a_{m-s} · f(s) · G(s)`, then
`∑_b L(b) · f(b) · Z(b) = ∑_m κ(m) · f(m) · G(m)`: substitute the first equation for `κ`, exchange
the two sums, and use the second equation. -/
private theorem volterra_duality (f κ Z L G : ℕ → ℝ) (R : ℕ)
    (hZ : ∀ b ∈ Icc 1 R, Z b = κ b + ∑ m ∈ Ioo b (R + 1), cay (m - b) * (f m * Z m))
    (hG : ∀ m ∈ Icc 1 R, G m = L m + ∑ s ∈ Ioo 0 m, cay (m - s) * (f s * G s)) :
    ∑ b ∈ Icc 1 R, L b * f b * Z b = ∑ m ∈ Icc 1 R, κ m * f m * G m := by
  have h1 : ∀ s ∈ Icc 1 R, κ s * f s * G s
      = Z s * f s * G s
        - ∑ m ∈ Ioo s (R + 1), f m * Z m * (cay (m - s) * (f s * G s)) := by
    intro s hs
    rw [show κ s = Z s - ∑ m ∈ Ioo s (R + 1), cay (m - s) * (f m * Z m) by linarith [hZ s hs],
      sub_mul, sub_mul, Finset.sum_mul, Finset.sum_mul]
    congr 1
    exact Finset.sum_congr rfl fun m _ => by ring
  have h2 : ∑ s ∈ Icc 1 R, ∑ m ∈ Ioo s (R + 1), f m * Z m * (cay (m - s) * (f s * G s))
      = ∑ m ∈ Icc 1 R, ∑ s ∈ Ioo 0 m, f m * Z m * (cay (m - s) * (f s * G s)) :=
    Finset.sum_comm' (by intro s m; simp only [mem_Icc, mem_Ioo]; omega)
  have h3 : ∀ m ∈ Icc 1 R, ∑ s ∈ Ioo 0 m, f m * Z m * (cay (m - s) * (f s * G s))
      = f m * Z m * (G m - L m) := by
    intro m hm
    rw [← Finset.mul_sum]
    congr 1
    linarith [hG m hm]
  rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib, h2, Finset.sum_congr rfl h3,
    ← Finset.sum_sub_distrib]
  exact Finset.sum_congr rfl fun m _ => by ring

/-- The pair sum as a sum over `m`, the last cut point that the frozen polynomial sees:
`pairSum k R = ∑_{m=1}^{R} κ(N-m) · k/(N-m) · (Lam1 + Lam2)(thr k N) m` with `κ = kap (k-1)` and
`N = k+R`.  This is `volterra_duality` for the environment `zr k (N-b-1)`, whose equation is
`zr_volterra` at the level `k-1`, and for `Lam1 + Lam2`, whose equation is `Lam2_last`. -/
private theorem pairSum_eq {k R : ℕ} (hR2 : R ≤ k - 2) :
    pairSum k R = ∑ m ∈ Icc 1 R, kap (k - 1) (k + R - m) * thr (k : ℝ) ((k : ℝ) + R) m
        * (Lam1 (thr (k : ℝ) ((k : ℝ) + R)) m + Lam2 (thr (k : ℝ) ((k : ℝ) + R)) m) := by
  refine volterra_duality (thr (k : ℝ) ((k : ℝ) + R)) (fun m => kap (k - 1) (k + R - m))
    (fun b => zr k (k + R - b - 1)) (Lam1 (thr (k : ℝ) ((k : ℝ) + R)))
    (fun m => Lam1 (thr (k : ℝ) ((k : ℝ) + R)) m + Lam2 (thr (k : ℝ) ((k : ℝ) + R)) m) R
    (fun b hb => ?_) (fun m _ => ?_)
  · -- `zr_volterra` in the row `N - b - 1`, with its sum over `t` written in the coordinate `N - t`
    rw [mem_Icc] at hb
    show zr k (k + R - b - 1) = kap (k - 1) (k + R - b)
      + ∑ m ∈ Ioo b (R + 1), cay (m - b) * (thr (k : ℝ) ((k : ℝ) + R) m * zr k (k + R - m - 1))
    have hV := zr_volterra (j := k) (k := k - 1) (n := k + R - b - 1) (by omega) (by omega)
      (by omega) (by omega)
    rw [show k + R - b - 1 + 1 = k + R - b by omega, sum_Ioo_reflect _ (k - 1) (k + R - b),
      show k + R - b - (k - 1) = R + 1 - b by omega] at hV
    rw [hV, sum_Ioo_shift _ b (R + 1)]
    congr 1
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [mem_Ioo] at hj
    have e : ((k + R - b - j : ℕ) : ℝ) = (k : ℝ) + R - ((b + j : ℕ) : ℝ) := by
      rw [show k + R - b - j = k + R - (b + j) by omega, Nat.cast_sub (by omega), Nat.cast_add]
    rw [show k + R - b - (k + R - b - j) = j by omega, show b + j - b = j by omega,
      show k + R - b - j - 1 = k + R - (b + j) - 1 by omega, e, mul_assoc]
    rfl
  · show Lam1 (thr (k : ℝ) ((k : ℝ) + R)) m + Lam2 (thr (k : ℝ) ((k : ℝ) + R)) m = _
    rw [Lam2_last]
    congr 1
    exact Finset.sum_congr rfl fun s _ => by ring

/-! ### The criterion -/

/-- **The curvature term dominates the pair sum.** At a position `(k+R-1, k)` with `R ≤ k-2`,
`2 · pairSum k R` is at most `k²` times the second difference in `y`, at `y = k`, of the frozen
polynomial `Kpoly (k-1) (k+R-1) y`.  By `Kpoly_second_diff` that second difference is
`∑_{m=1}^{R} κ(N-m)/(N-m) · curvSum k N m` with `κ = kap (k-1) > 0` and `N = k+R`;
`chain_second_diff` bounds each curvature sum from below, and `pairSum_eq` identifies the sum of the
bounds.  For `R = 0` both sides are zero, and `R ≥ 1` gives `k ≥ 3`. -/
theorem curv_ge_pair {k R : ℕ} (hR2 : R ≤ k - 2) :
    2 * pairSum k R
      ≤ (k : ℝ) ^ 2 * (Kpoly (k - 1) (k + R - 1) ((k : ℝ) + 1)
          - 2 * Kpoly (k - 1) (k + R - 1) k + Kpoly (k - 1) (k + R - 1) ((k : ℝ) - 1)) := by
  rw [Kpoly_second_diff, show k + R - 1 - (k - 1) = R by omega, pairSum_eq hR2, Finset.mul_sum,
    Finset.mul_sum]
  refine Finset.sum_le_sum fun m hm => ?_
  rw [mem_Icc] at hm
  have hkr : (0 : ℝ) < (k : ℝ) := by exact_mod_cast (show 0 < k by omega)
  have hmR : (m : ℝ) ≤ R := by exact_mod_cast hm.2
  have e : ((k + R - 1 : ℕ) : ℝ) + 1 = (k : ℝ) + R := by
    rw [Nat.cast_sub (by omega), Nat.cast_add, Nat.cast_one]
    ring
  rw [show k + R - 1 + 1 = k + R by omega, e]
  have hc : 0 ≤ kap (k - 1) (k + R - m) / ((k : ℝ) + R - m) :=
    div_nonneg (kap_pos (by omega) (by omega)).le (by linarith)
  have h := mul_le_mul_of_nonneg_left
    (chain_second_diff hkr (N := (k : ℝ) + R) (m := m) (by linarith)) hc
  calc 2 * (kap (k - 1) (k + R - m) * thr (k : ℝ) ((k : ℝ) + R) m
          * (Lam1 (thr (k : ℝ) ((k : ℝ) + R)) m + Lam2 (thr (k : ℝ) ((k : ℝ) + R)) m))
      = kap (k - 1) (k + R - m) / ((k : ℝ) + R - m)
          * ((k : ℝ) * (2 * Lam1 (thr (k : ℝ) ((k : ℝ) + R)) m
              + 2 * Lam2 (thr (k : ℝ) ((k : ℝ) + R)) m)) := by
        rw [thr_apply]
        ring
    _ ≤ _ := h
    _ = _ := by ring

/-- **The pair–impulse criterion.** At a position `(k+R-1, k)` with `1 ≤ R ≤ k-2`, so that
`k ≥ 3`, if `k · a_k · Λ_R(k+1; k+R) < 2 · pairSum k R`, then the step is positive:
`dq k (k+R-1) > 0`.  By
`dq_frozen` at the level `k-1` the step is the second difference of `Kpoly (k-1) (k+R-1)` at `k`
minus `(a_k/k) · Λ_R(k+1; k+R)`, and `curv_ge_pair` bounds the second difference from below. -/
theorem dq_pos_of_pair {k R : ℕ} (hR1 : 1 ≤ R) (hR2 : R ≤ k - 2)
    (h : (k : ℝ) * cay k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R < 2 * pairSum k R) :
    0 < dq k (k + R - 1) := by
  have hk0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hcurv := curv_ge_pair hR2
  have hfr := (dq_frozen (k := k - 1) (r := R) (by omega) hR1 (by omega)).2
  rw [show k - 1 + 1 = k by omega, show k - 1 + R = k + R - 1 by omega,
    Nat.cast_sub (show 1 ≤ k by omega), Nat.cast_one,
    show (k : ℝ) - 1 + 2 = (k : ℝ) + 1 by ring, show (k : ℝ) - 1 + 1 = (k : ℝ) by ring,
    show (k : ℝ) - 1 + (R : ℝ) + 1 = (k : ℝ) + R by ring] at hfr
  rw [hfr]
  refine (mul_pos_iff_of_pos_left (pow_pos hk0 2)).1 ?_
  have e : (k : ℝ) ^ 2 * (cay k / k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R)
      = (k : ℝ) * cay k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R := by
    linear_combination ((k : ℝ) * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R)
      * div_mul_cancel₀ (cay k) hk0.ne'
  rw [mul_sub, e]
  linarith

end Parking
