module

public import Parking.Series.PrimeKernel

/-!
# Tilted sequences

Multiplying the `N`-th term of a sequence by `x ^ N` turns a convolution recursion into a
recursion of the same shape, and the tilt `x` can then be chosen so that the kernel of the
recursion has total mass one.  The modules that import this one use the sequences of the
counting layer in this tilted form.

* `zrT y x N = zr y N * x ^ N`: the tilted environment of the threshold `y`, where
  `zr y N = A N (y-1) / N!`.  It satisfies the tilted last-car recursion `zrT_succ`, increases with
  the threshold (`zrT_le_zrT`), and coincides on the free range `N ≤ y` with
* `ccT x N = cc N * x ^ N`: the tilted Cayley masses, `cc N = (N+1)^(N-1) / N!` (`zrT_eq_ccT`).
* `cayT x n = cay n * x ^ n`: the tilted tree numbers, `cay n = n^(n-1) / n!`; one index further,
  `x * ccT x N = cayT x (N + 1)`.
* `epsT x m = eps m * x ^ m`: the tilted free prime kernel.
* `kqT y x m = kq y m * x ^ m`: the tilted prime kernel of the threshold `y`.  It equals `epsT x m`
  for `1 ≤ m ≤ y` (`kqT_eq_epsT`) and satisfies the recursion `kqT_rec`,
  `N kqT y x N = ∑_{γ=1}^{y-1} (y-γ) cayT x γ * kqT y x (N-γ)` for `N ≥ y ≥ 2`.  Hence it is
  nonnegative (`kqT_nonneg`), and if the free kernel does not increase on `[1, y]`, then `kqT y x`
  does not increase on `[1, ∞)` and `m * kqT y x m` does not increase on `[y, ∞)` (`kqT_succ_le`,
  `kqT_harmonic`).
* `Ut k x N = zrT k x N - zrT (k-1) x N`: the tilted cell, equal to `bq (k-1) N * x ^ N` for
  `k ≥ 2` (`Ut_eq_bq`).
-/

@[expose] public section

namespace Parking

open Finset

/-! ### Definitions -/

/-- The tilted environment `zr y N * x ^ N` of the threshold `y`. -/
noncomputable def zrT (y : ℕ) (x : ℝ) (N : ℕ) : ℝ := zr y N * x ^ N

/-- The tilted Cayley masses `c_N x^N`, `c_N = (N+1)^(N-1) / N!`. -/
noncomputable def ccT (x : ℝ) (N : ℕ) : ℝ := cc N * x ^ N

/-- The tilted tree numbers `a_n x^n`, `a_n = n^(n-1) / n!`. -/
noncomputable def cayT (x : ℝ) (n : ℕ) : ℝ := cay n * x ^ n

/-- The tilted free prime kernel `ε_m x^m`. -/
noncomputable def epsT (x : ℝ) (m : ℕ) : ℝ := eps m * x ^ m

/-- The tilted prime kernel `kq y m * x ^ m` of the threshold `y`. -/
noncomputable def kqT (y : ℕ) (x : ℝ) (m : ℕ) : ℝ := kq y m * x ^ m

/-- The kernel `(y - γ)⁺ a_γ x^γ` of the recursion `kqT_rec`. -/
noncomputable def kqWT (y : ℕ) (x : ℝ) (γ : ℕ) : ℝ := ((y - γ : ℕ) : ℝ) * cayT x γ

/-- The tilted cell `b_{N,k-1} x^N / N!`, as the difference of two tilted environments. -/
noncomputable def Ut (k : ℕ) (x : ℝ) (N : ℕ) : ℝ := zrT k x N - zrT (k - 1) x N

/-! ### The tilted Cayley masses and tree numbers -/

/-- For a tilt $x > 0$ the tilted Cayley masses are positive: $c_N x^N > 0$. -/
theorem ccT_pos {x : ℝ} (hx : 0 < x) (N : ℕ) : 0 < ccT x N :=
  mul_pos (cc_pos N) (pow_pos hx N)

private theorem cayT_nonneg {x : ℝ} (hx : 0 ≤ x) (n : ℕ) : 0 ≤ cayT x n :=
  mul_nonneg (cay_nonneg n) (pow_nonneg hx n)

/-- `x c_N x^N = a_{N+1} x^(N+1)`. -/
theorem x_mul_ccT (x : ℝ) (N : ℕ) : x * ccT x N = cayT x (N + 1) := by
  rw [ccT, cayT, cc]
  ring

/-- For a tilt $x \ge 0$ the tilted weights $(y-\gamma)^+ a_\gamma x^\gamma$ of the prime-kernel
recursion are nonnegative. -/
theorem kqWT_nonneg (y : ℕ) {x : ℝ} (hx : 0 ≤ x) (γ : ℕ) : 0 ≤ kqWT y x γ :=
  mul_nonneg (Nat.cast_nonneg _) (cayT_nonneg hx γ)

/-! ### The tilted environments -/

/-- For a threshold $y \ge 1$ and any tilt $x$, the tilted environment equals $1$ at $N = 0$. -/
theorem zrT_zero {y : ℕ} (hy : 1 ≤ y) (x : ℝ) : zrT y x 0 = 1 := by
  rw [zrT, zr_zero hy, pow_zero, mul_one]

/-- For a tilt $x \ge 0$ the tilted environment of a threshold is nonnegative: $z^{(y)}_N x^N \ge
0$. -/
theorem zrT_nonneg (y : ℕ) {x : ℝ} (hx : 0 ≤ x) (N : ℕ) : 0 ≤ zrT y x N :=
  mul_nonneg (zr_nonneg y N) (pow_nonneg hx N)

/-- The tilted environments increase with the threshold. -/
theorem zrT_le_zrT {y y' : ℕ} (h : y ≤ y') {x : ℝ} (hx : 0 ≤ x) (N : ℕ) :
    zrT y x N ≤ zrT y' x N :=
  mul_le_mul_of_nonneg_right (zr_mono h N) (pow_nonneg hx N)

/-- On the free range `N ≤ y` the tilted environment is the tilted Cayley mass. -/
theorem zrT_eq_ccT {y N : ℕ} (hy : 1 ≤ y) (x : ℝ) (hN : N ≤ y) : zrT y x N = ccT x N := by
  rw [zrT, ccT, zr_eq_cc hy hN]

/-- The tilted last-car recursion. -/
theorem zrT_succ {y : ℕ} (hy : 1 ≤ y) (x : ℝ) (N : ℕ) :
    ((N : ℝ) + 1) * zrT y x (N + 1) =
      x * ∑ i ∈ range (N + 1), ((min (i + 1) y : ℕ) : ℝ) * zrT y x i * zrT y x (N - i) := by
  have h : ((N : ℝ) + 1) * zr y (N + 1) =
      ∑ j ∈ range (N + 1), ((min (j + 1) y : ℕ) : ℝ) * zr y j * zr y (N - j) :=
    (zr_isWSol hy).succ N
  have hsum : x * ∑ i ∈ range (N + 1), ((min (i + 1) y : ℕ) : ℝ) * zrT y x i * zrT y x (N - i) =
      x ^ (N + 1) * ∑ j ∈ range (N + 1), ((min (j + 1) y : ℕ) : ℝ) * zr y j * zr y (N - j) := by
    rw [mul_sum, mul_sum]
    refine sum_congr rfl fun i hi => ?_
    rw [mem_range] at hi
    have hp : x ^ (N + 1) = x * x ^ i * x ^ (N - i) := by
      rw [mul_assoc, ← pow_add, ← pow_succ']
      congr 1
      omega
    rw [zrT, zrT, hp]
    ring
  rw [hsum, ← h, zrT]
  ring

/-- For a column $k \ge 2$ the tilted cell is the tilted normalised count of the level $k-1$: $U_N =
\beta^{(k-1)}_N x^N$ with $\beta^{(k-1)}_N = b(N,k-1)/N!$. -/
theorem Ut_eq_bq {k : ℕ} (hk : 2 ≤ k) (x : ℝ) (N : ℕ) : Ut k x N = bq (k - 1) N * x ^ N := by
  have h := bq_eq (show 1 ≤ k - 1 by omega) N
  rw [Nat.sub_add_cancel (show 1 ≤ k by omega)] at h
  rw [Ut, zrT, zrT, h]
  ring

/-- In the free range $1 \le m \le y$ the tilted prime kernel of the threshold $y$ is the tilted
free prime kernel: $\kappa^{(y)}_m x^m = \varepsilon_m x^m$. -/
theorem kqT_eq_epsT {y m : ℕ} (x : ℝ) (hy : 1 ≤ y) (hm1 : 1 ≤ m) (hm : m ≤ y) :
    kqT y x m = epsT x m := by
  rw [kqT, epsT, kq_eq_eps hy hm1 hm]

/-- The tilted prime kernel recursion. -/
theorem kqT_rec {y N : ℕ} (x : ℝ) (hy : 2 ≤ y) (hN : y ≤ N) :
    (N : ℝ) * kqT y x N = rconv (kqWT y x) (kqT y x) N := by
  have h := kq_rec hy hN
  have hsum : rconv (kqWT y x) (kqT y x) N = x ^ N * rconv (kqW y) (kq y) N := by
    rw [rconv, rconv, mul_sum]
    refine sum_congr rfl fun j hj => ?_
    rw [mem_range] at hj
    have hp : x ^ N = x ^ (j + 1) * x ^ (N - 1 - j) := by
      rw [← pow_add]
      congr 1
      omega
    rw [kqWT, cayT, kqT, kqW, hp]
    ring
  rw [hsum, kqT]
  linear_combination (x ^ N) * h

/-- For a threshold $y \ge 2$ and a tilt $x \ge 0$ the tilted prime kernel is nonnegative:
$\kappa^{(y)}_m x^m \ge 0$ for every $m$. With $x = 1$ this is the nonnegativity of the prime
kernel itself. -/
theorem kqT_nonneg {y : ℕ} (hy : 2 ≤ y) {x : ℝ} (hx : 0 ≤ x) (m : ℕ) : 0 ≤ kqT y x m := by
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    by_cases hm0 : m = 0
    · subst hm0
      rw [kqT, kq_zero (show 1 ≤ y by omega), zero_mul]
    · by_cases hmy : m ≤ y
      · rw [kqT_eq_epsT x (by omega) (by omega) hmy, epsT]
        exact mul_nonneg (eps_nonneg m) (pow_nonneg hx m)
      · have hrec := kqT_rec x hy (show y ≤ m by omega)
        have hsum : 0 ≤ rconv (kqWT y x) (kqT y x) m := by
          rw [rconv]
          refine Finset.sum_nonneg fun j hj => ?_
          rw [mem_range] at hj
          exact mul_nonneg (kqWT_nonneg y hx (j + 1)) (ih (m - 1 - j) (by omega))
        have hmpos : (0 : ℝ) < (m : ℝ) := Nat.cast_pos.mpr (by omega)
        rw [← hrec] at hsum
        exact nonneg_of_mul_nonneg_right hsum hmpos

private theorem kqT_step_aux {y : ℕ} (hy : 2 ≤ y) {x : ℝ} (hx : 0 ≤ x)
    (hfree : ∀ m, 1 ≤ m → m < y → epsT x (m + 1) ≤ epsT x m) :
    ∀ m, 1 ≤ m → kqT y x (m + 1) ≤ kqT y x m ∧
      (y ≤ m → ((m : ℝ) + 1) * kqT y x (m + 1) ≤ (m : ℝ) * kqT y x m) := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro hm1
    by_cases hmy : m + 1 ≤ y
    · refine ⟨?_, fun h => absurd h (by omega)⟩
      rw [kqT_eq_epsT x (by omega) (by omega) hmy, kqT_eq_epsT (y := y) x (by omega) hm1 (by omega)]
      exact hfree m hm1 (by omega)
    · have hym : y ≤ m := by omega
      have hharm : ((m : ℝ) + 1) * kqT y x (m + 1) ≤ (m : ℝ) * kqT y x m := by
        have h1 := kqT_rec x hy (show y ≤ m + 1 by omega)
        have h0 := kqT_rec x hy hym
        rw [Nat.cast_add, Nat.cast_one] at h1
        rw [h1, h0, rconv, rconv, Finset.sum_range_succ]
        have hlast : kqWT y x (m + 1) = 0 := by
          rw [kqWT, show y - (m + 1) = 0 by omega, Nat.cast_zero, zero_mul]
        rw [hlast, zero_mul, add_zero]
        refine Finset.sum_le_sum fun j hj => ?_
        rw [mem_range] at hj
        by_cases hjy : y ≤ j + 1
        · have hz : kqWT y x (j + 1) = 0 := by
            rw [kqWT, show y - (j + 1) = 0 by omega, Nat.cast_zero, zero_mul]
          have e : kqWT y x (j + 1) * kqT y x (m + 1 - 1 - j) =
              kqWT y x (j + 1) * kqT y x (m - 1 - j) := by
            rw [hz, zero_mul, zero_mul]
          exact le_of_eq e
        · have hle : kqT y x (m + 1 - 1 - j) ≤ kqT y x (m - 1 - j) := by
            have h := (ih (m - 1 - j) (by omega) (by omega)).1
            rwa [show m - 1 - j + 1 = m + 1 - 1 - j by omega] at h
          exact mul_le_mul_of_nonneg_left hle (kqWT_nonneg y hx (j + 1))
      have hk1 := kqT_nonneg hy hx (m + 1)
      have hmpos : (0 : ℝ) < (m : ℝ) := Nat.cast_pos.mpr (by omega)
      have h2 : (m : ℝ) * kqT y x (m + 1) ≤ (m : ℝ) * kqT y x m := by
        have e : ((m : ℝ) + 1) * kqT y x (m + 1) =
            (m : ℝ) * kqT y x (m + 1) + kqT y x (m + 1) := by
          ring
        linarith
      exact ⟨le_of_mul_le_mul_left h2 hmpos, fun _ => hharm⟩

/-- Beyond the free range the tilted kernel decays at least harmonically. -/
theorem kqT_harmonic {y : ℕ} (hy : 2 ≤ y) {x : ℝ} (hx : 0 ≤ x)
    (hfree : ∀ m, 1 ≤ m → m < y → epsT x (m + 1) ≤ epsT x m) :
    ∀ m, y ≤ m → ((m : ℝ) + 1) * kqT y x (m + 1) ≤ (m : ℝ) * kqT y x m := by
  intro m hm
  exact (kqT_step_aux hy hx hfree m (by omega)).2 hm

/-- If the free kernel is nonincreasing on `[1, y]`, the tilted prime kernel is nonincreasing on
`[1, ∞)`. -/
theorem kqT_succ_le {y : ℕ} (hy : 2 ≤ y) {x : ℝ} (hx : 0 ≤ x)
    (hfree : ∀ m, 1 ≤ m → m < y → epsT x (m + 1) ≤ epsT x m) :
    ∀ m, 1 ≤ m → kqT y x (m + 1) ≤ kqT y x m := by
  intro m hm
  exact (kqT_step_aux hy hx hfree m hm).1

end Parking
