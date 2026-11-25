module

public import Parking.Basic.RealBounds

/-!
# Sums of half-integer powers

Explicit bounds for the sums of `b^{-1/2}`, `b^{-3/2}`, `b^{1/2}`, `b^{3/2}` over `2 ≤ b ≤ R`, and
for the sums of `c^{3/2}` and `c^{3/2} (R - c)` over `0 < c < R`.  The powers are written with
`Real.sqrt`: `b^{3/2} = b √b`, `b^{-3/2} = 1/(b √b)`, and so on.

Every bound compares a sum with an integral, one unit interval at a time.  Let `F` be an
antiderivative of `g`.  A quadrature rule bounds the term `g (b + 1)` by an increment
`G (b + 1) - G b` of a function `G` built from `F`, and adding these inequalities for `m ≤ b < n`
leaves `∑_{b=m+1}^{n} g b ≤ G n - G m` (`sum_Icc_le_of_step`).  Three rules occur.

* **Midpoint rule.**  The value of a convex function at the midpoint of an interval is at most
  its mean over the interval: `g (b + 1) ≤ F (b + 3/2) - F (b + 1/2)`, so `G x = F (x + 1/2)`.
  For `x^{-1/2}` and `x^{-3/2}`, started at `m = 1`, this gives
  `∑_{b=2}^{R} b^{-1/2} ≤ 2√(R + 1/2) - 2√(3/2)` and `∑_{b=2}^{R} b^{-3/2} ≤ 2/√(3/2)`.
* **Trapezoid rule.**  The mean of the two end values of a concave function is at most its mean
  over the interval: `(g b + g (b + 1))/2 ≤ F (b + 1) - F b`, so `G = F + g/2`.  For a convex
  function the inequality is reversed.  Started at `m = 2`, with the term `b = 2` added
  separately, this gives `∑_{b=2}^{R} b^{1/2} ≤ (2/3) R^{3/2} + (1/2) R^{1/2} - (5/6)√2` for the
  concave `x^{1/2}` and `∑_{b=2}^{R} b^{3/2} ≥ (2/5) R^{5/2} + (1/2) R^{3/2} - (3/5)√2` for the
  convex `x^{3/2}`.
* **Left endpoint rule.**  The value of an increasing function at the left end of an interval is
  at most its mean over the interval.  For `x^{3/2}` this is `sum_range_sqrt_cube_le`.  For
  `x^{5/2}` it bounds the weighted sum `∑_{0<c<R} c^{3/2} (R - c)`, which increases by
  `∑_{c≤R} c^{3/2}` when `R` is replaced by `R + 1`.

With `p = √y` and `q = √(y + 1)`, so that `q² - p² = 1`, the trapezoid and left endpoint rules on
`[y, y + 1]` are polynomial inequalities in `p` and `q`: in each of them the difference of the two
sides is a power of `q - p` times a polynomial with nonnegative coefficients.  The midpoint rule
rests on `√(x + 1/2) + √(x - 1/2) ≤ 2√x`.

The decimal constants of the public statements come from `2√(3/2) ≥ 2.44948`,
`2/√(3/2) ≤ 1.63300`, `(5/6)√2 ≥ 1.17851` and `(3/5)√2 ≤ 0.84853`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### Telescoping -/

/-- If `g (b + 1) ≤ G (b + 1) - G b` for every natural number `b`, then
`∑_{b=m+1}^{n} g b ≤ G n - G m`. -/
private theorem sum_Icc_le_of_step {g G : ℝ → ℝ} {m n : ℕ} (hmn : m ≤ n)
    (step : ∀ b : ℕ, g ((b : ℝ) + 1) ≤ G ((b : ℝ) + 1) - G (b : ℝ)) :
    ∑ b ∈ Icc (m + 1) n, g (b : ℝ) ≤ G (n : ℝ) - G (m : ℝ) := by
  induction n, hmn using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    rw [sum_Icc_succ_top (Nat.add_le_add_right hn 1), Nat.cast_add_one]
    linarith [step n]

/-! ### The midpoint rule: `∑ b^{-1/2}` and `∑ b^{-3/2}` -/

/-- `√(y + 3/2) · √(y + 1/2) ≤ y + 1`: the geometric mean of `y + 3/2` and `y + 1/2` is at most
their arithmetic mean. -/
private theorem sqrt_mul_sqrt_le_midpoint {y : ℝ} (hy : 0 ≤ y) :
    Real.sqrt (y + 1 + 1 / 2) * Real.sqrt (y + 1 / 2) ≤ y + 1 := by
  linarith [two_mul_le_add_sq (Real.sqrt (y + 1 + 1 / 2)) (Real.sqrt (y + 1 / 2)),
    Real.sq_sqrt (show 0 ≤ y + 1 + 1 / 2 by linarith),
    Real.sq_sqrt (show 0 ≤ y + 1 / 2 by linarith)]

/-- Midpoint rule for the convex `x^{-1/2}` on `[y + 1/2, y + 3/2]`:
`1/√(y+1) ≤ 2√(y + 3/2) - 2√(y + 1/2)`.  Write `u`, `w` for the two square roots on the right.
Then `(u + w)² = 2(y + 1) + 2uw ≤ 4(y + 1)`, so `u + w ≤ 2√(y+1)`, and
`1 = (u - w)(u + w) ≤ (u - w) · 2√(y+1)`. -/
private theorem inv_sqrt_midpoint_le {y : ℝ} (hy : 0 ≤ y) :
    1 / Real.sqrt (y + 1) ≤ 2 * Real.sqrt (y + 1 + 1 / 2) - 2 * Real.sqrt (y + 1 / 2) := by
  have hu : Real.sqrt (y + 1 + 1 / 2) ^ 2 = y + 1 + 1 / 2 := Real.sq_sqrt (by linarith)
  have hw : Real.sqrt (y + 1 / 2) ^ 2 = y + 1 / 2 := Real.sq_sqrt (by linarith)
  have hp : Real.sqrt (y + 1) ^ 2 = y + 1 := Real.sq_sqrt (by linarith)
  have hwu : Real.sqrt (y + 1 / 2) ≤ Real.sqrt (y + 1 + 1 / 2) := Real.sqrt_le_sqrt (by linarith)
  have hsum : Real.sqrt (y + 1 + 1 / 2) + Real.sqrt (y + 1 / 2) ≤ 2 * Real.sqrt (y + 1) :=
    (sq_le_sq₀ (by positivity) (by positivity)).1 (by linarith [sqrt_mul_sqrt_le_midpoint hy])
  rw [div_le_iff₀ (Real.sqrt_pos.2 (by linarith))]
  linarith [mul_le_mul_of_nonneg_left hsum (sub_nonneg.2 hwu)]

/-- Midpoint rule for the convex `x^{-3/2}` on `[y + 1/2, y + 3/2]`:
`1/((y+1)√(y+1)) ≤ 2/√(y + 1/2) - 2/√(y + 3/2)`.  With `u = √(y + 3/2)` and `w = √(y + 1/2)` the
right-hand side is `2(u - w)/(uw)`; here `2(u - w) ≥ 1/√(y+1)` by the midpoint rule for
`x^{-1/2}`, and `uw ≤ y + 1`. -/
private theorem inv_sqrt_cube_midpoint_le {y : ℝ} (hy : 0 ≤ y) :
    1 / ((y + 1) * Real.sqrt (y + 1))
      ≤ 2 / Real.sqrt (y + 1 / 2) - 2 / Real.sqrt (y + 1 + 1 / 2) := by
  have hu : 0 < Real.sqrt (y + 1 + 1 / 2) := Real.sqrt_pos.2 (by linarith)
  have hw : 0 < Real.sqrt (y + 1 / 2) := Real.sqrt_pos.2 (by linarith)
  have hwu : Real.sqrt (y + 1 / 2) ≤ Real.sqrt (y + 1 + 1 / 2) := Real.sqrt_le_sqrt (by linarith)
  calc 1 / ((y + 1) * Real.sqrt (y + 1))
      = 1 / Real.sqrt (y + 1) / (y + 1) := by rw [div_div, mul_comm]
    _ ≤ (2 * Real.sqrt (y + 1 + 1 / 2) - 2 * Real.sqrt (y + 1 / 2)) / (y + 1) :=
        div_le_div_of_nonneg_right (inv_sqrt_midpoint_le hy) (by linarith)
    _ ≤ (2 * Real.sqrt (y + 1 + 1 / 2) - 2 * Real.sqrt (y + 1 / 2))
          / (Real.sqrt (y + 1 + 1 / 2) * Real.sqrt (y + 1 / 2)) :=
        div_le_div_of_nonneg_left (by linarith) (mul_pos hu hw) (sqrt_mul_sqrt_le_midpoint hy)
    _ = 2 / Real.sqrt (y + 1 / 2) - 2 / Real.sqrt (y + 1 + 1 / 2) := by field_simp

/-- `∑_{b=2}^{R} b^{-1/2} ≤ 2√R + 1/(2√R) - 2.44948` for `R ≥ 2`.  The midpoint rule gives
`2√(R + 1/2) - 2√(3/2)`; then `√(R + 1/2) ≤ √R + 1/(4√R)`, because the square of the right-hand
side is `R + 1/2 + 1/(16R)`, and `2√(3/2) ≥ 2.44948`. -/
theorem sum_Icc_two_inv_sqrt_le {R : ℕ} (hR : 2 ≤ R) :
    ∑ b ∈ Icc 2 R, 1 / Real.sqrt (b : ℝ)
      ≤ 2 * Real.sqrt (R : ℝ) + 1 / (2 * Real.sqrt (R : ℝ)) - 2.44948 := by
  have h := sum_Icc_le_of_step (g := fun x => 1 / Real.sqrt x)
    (G := fun x => 2 * Real.sqrt (x + 1 / 2)) (m := 1) (by omega : 1 ≤ R)
    fun b => inv_sqrt_midpoint_le (Nat.cast_nonneg b)
  rw [Nat.cast_one, show (1 + 1 / 2 : ℝ) = 3 / 2 by norm_num] at h
  have hconst : (2.44948 : ℝ) ≤ 2 * Real.sqrt (3 / 2) := by
    linarith [(Real.le_sqrt' (by norm_num)).2 (by norm_num : (1.22474 : ℝ) ^ 2 ≤ 3 / 2)]
  have hs : 0 < Real.sqrt (R : ℝ) := Real.sqrt_pos.2 (Nat.cast_pos.2 (by omega))
  have hs2 : Real.sqrt (R : ℝ) ^ 2 = R := Real.sq_sqrt (Nat.cast_nonneg R)
  have hc : Real.sqrt (R : ℝ) * (1 / (2 * Real.sqrt (R : ℝ))) = 1 / 2 := by field_simp
  have htan : Real.sqrt ((R : ℝ) + 1 / 2)
      ≤ Real.sqrt (R : ℝ) + 1 / (2 * Real.sqrt (R : ℝ)) / 2 :=
    Real.sqrt_le_iff.2 ⟨by positivity, by linarith [sq_nonneg (1 / (2 * Real.sqrt (R : ℝ)))]⟩
  linarith

/-- `∑_{b=2}^{R} b^{-3/2} ≤ 1.63300`.  The midpoint rule gives `2/√(3/2) - 2/√(R + 1/2)`, and
`2/√(3/2) ≤ 1.633`. -/
theorem sum_Icc_two_inv_sqrt_cube_le (R : ℕ) :
    ∑ b ∈ Icc 2 R, 1 / ((b : ℝ) * Real.sqrt (b : ℝ)) ≤ 1.63300 := by
  rcases Nat.eq_zero_or_pos R with rfl | hR
  · norm_num
  · have h := sum_Icc_le_of_step (g := fun x => 1 / (x * Real.sqrt x))
      (G := fun x => -(2 / Real.sqrt (x + 1 / 2))) (m := 1) hR
      fun b => by linarith [inv_sqrt_cube_midpoint_le (y := (b : ℝ)) (Nat.cast_nonneg b)]
    rw [Nat.cast_one, show (1 + 1 / 2 : ℝ) = 3 / 2 by norm_num] at h
    have hconst : 2 / Real.sqrt (3 / 2 : ℝ) ≤ 1.633 :=
      (div_le_iff₀ (by positivity)).2 (by
        linarith [(Real.le_sqrt' (by norm_num)).2 (by norm_num : (1.224744 : ℝ) ^ 2 ≤ 3 / 2)])
    have htail : 0 ≤ 2 / Real.sqrt ((R : ℝ) + 1 / 2) := by positivity
    linarith

/-! ### The trapezoid rule: `∑ b^{1/2}` and `∑ b^{3/2}` -/

/-- For `y ≥ 0` the numbers `p = √y` and `q = √(y + 1)` satisfy `0 ≤ p ≤ q`, `y = p²` and
`y + 1 = q²`.  (These are the facts of `sqrt_succ_facts`, a private lemma of
`Parking.Basic.RealBounds`, in the form in which a statement about `y`, `√y` and `√(y+1)` is
turned into one about `p` and `q`.) -/
private theorem exists_sqrt_succ_pair {y : ℝ} (hy : 0 ≤ y) :
    ∃ p q : ℝ, 0 ≤ p ∧ p ≤ q ∧ Real.sqrt y = p ∧ Real.sqrt (y + 1) = q
      ∧ y = p ^ 2 ∧ y + 1 = q ^ 2 :=
  ⟨Real.sqrt y, Real.sqrt (y + 1), Real.sqrt_nonneg y, Real.sqrt_le_sqrt (by linarith), rfl, rfl,
    (Real.sq_sqrt hy).symm, (Real.sq_sqrt (by linarith)).symm⟩

/-- Trapezoid rule for the concave `x^{1/2}` on `[y, y + 1]`:
`(√y + √(y+1))/2 ≤ (2/3)((y+1)^{3/2} - y^{3/2})`.  With `p = √y`, `q = √(y+1)`:
`(2/3)(q³ - p³) - ((p + q)/2)(q² - p²) = (q - p)³/6`. -/
private theorem sqrt_trapezoid_le {y : ℝ} (hy : 0 ≤ y) :
    (Real.sqrt y + Real.sqrt (y + 1)) / 2
      ≤ 2 / 3 * ((y + 1) * Real.sqrt (y + 1) - y * Real.sqrt y) := by
  obtain ⟨p, q, -, hpq, hp, hq, rfl, h⟩ := exists_sqrt_succ_pair hy
  rw [hp, hq, h]
  linear_combination 1 / 6 * pow_nonneg (sub_nonneg.2 hpq) 3 + (p + q) / 2 * h

/-- Trapezoid rule for the convex `x^{3/2}` on `[y, y + 1]`:
`(2/5)((y+1)^{5/2} - y^{5/2}) ≤ (y^{3/2} + (y+1)^{3/2})/2`.  With `p = √y`, `q = √(y+1)`:
`((p³ + q³)/2)(q² - p²) - (2/5)(q⁵ - p⁵) = (q - p)³ (q² + 3qp + p²)/10`. -/
private theorem le_sqrt_cube_trapezoid {y : ℝ} (hy : 0 ≤ y) :
    2 / 5 * ((y + 1) ^ 2 * Real.sqrt (y + 1) - y ^ 2 * Real.sqrt y)
      ≤ (y * Real.sqrt y + (y + 1) * Real.sqrt (y + 1)) / 2 := by
  obtain ⟨p, q, hp0, hpq, hp, hq, rfl, h⟩ := exists_sqrt_succ_pair hy
  rw [hp, hq, h]
  have hq0 : 0 ≤ q := hp0.trans hpq
  have hT : 0 ≤ (q - p) ^ 3 * (q ^ 2 + 3 * q * p + p ^ 2) :=
    mul_nonneg (pow_nonneg (sub_nonneg.2 hpq) 3) (by positivity)
  linear_combination 1 / 10 * hT - (p ^ 3 + q ^ 3) / 2 * h

/-- `∑_{b=2}^{R} b^{1/2} ≤ (2/3) R^{3/2} + (1/2) R^{1/2} - 1.17851` for `R ≥ 2`.  With
`G(x) = (2/3) x^{3/2} + (1/2) x^{1/2}` the trapezoid rule reads `√(b+1) ≤ G(b+1) - G(b)`, so the
terms after the first sum to at most `G(R) - G(2)`, and `G(2) - √2 = (5/6)√2 ≥ 1.17851`. -/
theorem sum_Icc_two_sqrt_le {R : ℕ} (hR : 2 ≤ R) :
    ∑ b ∈ Icc 2 R, Real.sqrt (b : ℝ)
      ≤ 2 / 3 * ((R : ℝ) * Real.sqrt (R : ℝ)) + 1 / 2 * Real.sqrt (R : ℝ) - 1.17851 := by
  have h := sum_Icc_le_of_step (g := fun x => Real.sqrt x)
    (G := fun x => 2 / 3 * (x * Real.sqrt x) + 1 / 2 * Real.sqrt x) hR
    fun b => by linarith [sqrt_trapezoid_le (y := (b : ℝ)) (Nat.cast_nonneg b)]
  have hconst : (1.17851 : ℝ) ≤ 5 / 6 * Real.sqrt 2 := by
    linarith [(Real.le_sqrt' (by norm_num)).2 (by norm_num : (1.414212 : ℝ) ^ 2 ≤ 2)]
  rw [Nat.cast_ofNat] at h
  rw [← add_sum_Ioc_eq_sum_Icc hR, ← Icc_add_one_left_eq_Ioc, Nat.cast_ofNat]
  linarith

/-- `∑_{b=2}^{R} b^{3/2} ≥ (2/5) R^{5/2} + (1/2) R^{3/2} - 0.84853` for `R ≥ 2`.  With
`G(x) = (2/5) x^{5/2} + (1/2) x^{3/2}` the trapezoid rule reads `G(b+1) - G(b) ≤ (b+1)^{3/2}`, so
the terms after the first sum to at least `G(R) - G(2)` (the telescoping lemma is applied to `-g`
and `-G`), and `G(2) - 2√2 = (3/5)√2 ≤ 0.84853`. -/
theorem sum_Icc_two_sqrt_cube_ge {R : ℕ} (hR : 2 ≤ R) :
    2 / 5 * ((R : ℝ) ^ 2 * Real.sqrt (R : ℝ)) + 1 / 2 * ((R : ℝ) * Real.sqrt (R : ℝ)) - 0.84853
      ≤ ∑ b ∈ Icc 2 R, (b : ℝ) * Real.sqrt (b : ℝ) := by
  have h := sum_Icc_le_of_step (g := fun x => -(x * Real.sqrt x))
    (G := fun x => -(2 / 5 * (x ^ 2 * Real.sqrt x) + 1 / 2 * (x * Real.sqrt x))) hR
    fun b => by linarith [le_sqrt_cube_trapezoid (y := (b : ℝ)) (Nat.cast_nonneg b)]
  have hconst : 3 / 5 * Real.sqrt 2 ≤ (0.84853 : ℝ) := by
    linarith [(Real.sqrt_le_left (by norm_num)).2 (by norm_num : (2 : ℝ) ≤ 1.414216 ^ 2)]
  rw [Nat.cast_ofNat, sum_neg_distrib] at h
  rw [← add_sum_Ioc_eq_sum_Icc hR, ← Icc_add_one_left_eq_Ioc, Nat.cast_ofNat]
  linarith

/-! ### Sums over `0 < c < R` -/

/-- `∑_{0<c<R} c^{3/2} ≤ (2/5) R^{5/2}`.  This is `sum_range_sqrt_cube_le`, whose sum has the
additional term `c = 0`, which is zero. -/
theorem sum_Ioo_sqrt_cube_le (R : ℕ) :
    ∑ c ∈ Ioo 0 R, (c : ℝ) * Real.sqrt (c : ℝ) ≤ 2 / 5 * ((R : ℝ) ^ 2 * Real.sqrt (R : ℝ)) :=
  (sum_le_sum_of_subset_of_nonneg (fun c hc => mem_range.2 (mem_Ioo.1 hc).2)
    fun c _ _ => by positivity).trans (sum_range_sqrt_cube_le R)

/-- Left endpoint rule for the increasing `x^{5/2}` on `[y, y + 1]`:
`y^{5/2} ≤ (2/7)((y+1)^{7/2} - y^{7/2})`.  With `p = √y`, `q = √(y+1)`:
`(2/7)(q⁷ - p⁷) - p⁵(q² - p²) = (q - p)² (2q⁵ + 4q⁴p + 6q³p² + 8q²p³ + 10qp⁴ + 5p⁵)/7`. -/
private theorem sqrt_fifth_left_le {y : ℝ} (hy : 0 ≤ y) :
    y ^ 2 * Real.sqrt y ≤ 2 / 7 * ((y + 1) ^ 3 * Real.sqrt (y + 1) - y ^ 3 * Real.sqrt y) := by
  obtain ⟨p, q, hp0, hpq, hp, hq, rfl, h⟩ := exists_sqrt_succ_pair hy
  rw [hp, hq, h]
  have hq0 : 0 ≤ q := hp0.trans hpq
  have hS : 0 ≤ (q - p) ^ 2 * (2 * q ^ 5 + 4 * q ^ 4 * p + 6 * q ^ 3 * p ^ 2 + 8 * q ^ 2 * p ^ 3
      + 10 * q * p ^ 4 + 5 * p ^ 5) := mul_nonneg (sq_nonneg _) (by positivity)
  linear_combination 1 / 7 * hS + p ^ 5 * h

/-- The increment in `n` of `∑_{c<n} f(c) (n - c)` is `∑_{c≤n} f(c)`. -/
private theorem sum_range_succ_mul_sub (f : ℕ → ℝ) (n : ℕ) :
    ∑ c ∈ range (n + 1), f c * (((n + 1 : ℕ) : ℝ) - c)
      = ∑ c ∈ range n, f c * ((n : ℝ) - c) + ∑ c ∈ range (n + 1), f c := by
  rw [sum_range_succ, sum_range_succ f, ← add_assoc, ← sum_add_distrib]
  congr 1
  · exact sum_congr rfl fun c _ => by push_cast; ring
  · push_cast; ring

/-- `∑_{0<c<R} c^{3/2} (R - c) ≤ (4/35) (R+1)^{7/2}`.  The term `c = 0` may be added to the sum,
since it is zero.  Then the bound is proved by induction on `R`: the sum increases by
`∑_{c≤R} c^{3/2} ≤ (2/5) (R+1)^{5/2}` when `R` is replaced by `R + 1`, and
`(2/5) (R+1)^{5/2} ≤ (4/35) ((R+2)^{7/2} - (R+1)^{7/2})` by the left endpoint rule for
`x^{5/2}`. -/
theorem sum_Ioo_sqrt_cube_mul_le (R : ℕ) :
    ∑ c ∈ Ioo 0 R, (c : ℝ) * Real.sqrt (c : ℝ) * ((R : ℝ) - c)
      ≤ 4 / 35 * (((R : ℝ) + 1) ^ 3 * Real.sqrt ((R : ℝ) + 1)) := by
  refine (sum_le_sum_of_subset_of_nonneg (fun c hc => mem_range.2 (mem_Ioo.1 hc).2)
    fun c hc _ => mul_nonneg (by positivity)
      (sub_nonneg.2 (Nat.cast_le.2 (mem_range.1 hc).le))).trans ?_
  induction R with
  | zero => norm_num
  | succ n ih =>
    have h5 := sum_range_sqrt_cube_le (n + 1)
    rw [Nat.cast_add_one] at h5
    rw [sum_range_succ_mul_sub, Nat.cast_add_one]
    linarith [sqrt_fifth_left_le (y := (n : ℝ) + 1) (by positivity)]

end Parking
