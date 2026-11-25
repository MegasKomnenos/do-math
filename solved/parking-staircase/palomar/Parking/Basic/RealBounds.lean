module

public import Mathlib.Analysis.SpecialFunctions.Log.Deriv
public import Mathlib.Analysis.SpecialFunctions.Sqrt

/-!
# Elementary real inequalities

Everything in this file is about real numbers only.

* **Logarithm.**  For `u ≥ 0` the Taylor polynomials of `log (1 + u)` bound it alternately from
  below and from above (`log_one_add_taylor`).  The cases of degree 2, 3, 4, 5 are
  `log_one_add_ge2`, `log_one_add_le3`, `log_one_add_ge4`, `log_one_add_le5`.
* **Exponential.**  `e^s ≤ 1 + s + 0.633 s²` for `0 ≤ s ≤ 0.6679` (`exp_le_quad`), and
  `e^y ≤ 1 + y + y²` for `0 ≤ y ≤ 1.7` (`exp_le_quadratic`).
* **Square roots.**  With `p = √y` and `q = √(y+1)` one has `0 ≤ p ≤ q` and `q² = p² + 1`.
  Comparing a power of `√·` with the increment of its antiderivative then becomes a polynomial
  inequality in `p`, `q`; summing the increments gives
  `∑_{i=1}^{n} i^{-1/2} ∈ [2√(n+1) - 2, 2√n - 1]`, `∑_{i<R} i^{1/2} ≤ (2/3) R^{3/2}`,
  `∑_{i<R} i^{3/2} ≤ (2/5) R^{5/2}` and `∑_{i=1}^{n} i^{-3/2} ≤ 3`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### The logarithm -/

/-- A function vanishing at `0` whose derivative is nonnegative on `[0, ∞)` is nonnegative
on `[0, ∞)`. -/
private theorem nonneg_of_deriv_nonneg {f f' : ℝ → ℝ} (h0 : f 0 = 0)
    (hd : ∀ x, 0 ≤ x → HasDerivAt f (f' x) x) (hn : ∀ x, 0 ≤ x → 0 ≤ f' x)
    {u : ℝ} (hu : 0 ≤ u) : 0 ≤ f u := by
  have hmono : MonotoneOn f (Set.Ici (0 : ℝ)) := by
    refine monotoneOn_of_deriv_nonneg (convex_Ici (0 : ℝ)) ?_ ?_ ?_
    · intro x hx
      exact (hd x hx).continuousAt.continuousWithinAt
    · intro x hx
      exact (hd x (interior_subset hx)).differentiableAt.differentiableWithinAt
    · intro x hx
      rw [(hd x (interior_subset hx)).deriv]
      exact hn x (interior_subset hx)
  have h := hmono (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hu) hu
  rwa [h0] at h

/-- For `u ≥ 0` the Taylor polynomials of `log (1 + u)` bound it alternately from below (even
degree) and from above (odd degree):
`0 ≤ (-1)^n (log (1 + u) - ∑_{i<n} (-1)^i u^{i+1}/(i+1))`.
Indeed the right-hand side vanishes at `u = 0` and its derivative is `u^n/(1+u) ≥ 0`. -/
theorem log_one_add_taylor (n : ℕ) {u : ℝ} (hu : 0 ≤ u) :
    0 ≤ (-1) ^ n
      * (Real.log (1 + u) - ∑ i ∈ range n, (-1) ^ i * u ^ (i + 1) / ((i : ℝ) + 1)) := by
  refine nonneg_of_deriv_nonneg
    (f := fun w : ℝ => (-1) ^ n
      * (Real.log (1 + w) - ∑ i ∈ range n, (-1) ^ i * w ^ (i + 1) / ((i : ℝ) + 1)))
    (f' := fun v : ℝ => v ^ n / (1 + v)) (by simp [pow_succ]) ?_ ?_ hu
  · intro v hv
    have h1v : 1 + v ≠ 0 := by positivity
    have hlog : HasDerivAt (fun w : ℝ => Real.log (1 + w)) (1 / (1 + v)) v :=
      ((hasDerivAt_id' v).const_add 1).log h1v
    have hsum : HasDerivAt
        (fun w : ℝ => ∑ i ∈ range n, (-1) ^ i * w ^ (i + 1) / ((i : ℝ) + 1))
        (∑ i ∈ range n, (-v) ^ i) v := by
      refine HasDerivAt.fun_sum fun i _ => ?_
      have hi : (i : ℝ) + 1 ≠ 0 := by positivity
      refine (((hasDerivAt_pow (i + 1) v).const_mul ((-1 : ℝ) ^ i)).div_const
        ((i : ℝ) + 1)).congr_deriv ?_
      rw [Nat.add_sub_cancel, Nat.cast_add_one, neg_pow v i]
      field
    -- `(∑_{i<n} (-v)^i) (1 + v) = 1 - (-v)^n`
    have hgeom : (∑ i ∈ range n, (-v) ^ i) * (1 + v) = 1 - (-v) ^ n := by
      have h := geom_sum_mul_neg (-v) n
      rwa [sub_neg_eq_add] at h
    have hsign : (-1 : ℝ) ^ n * (-v) ^ n = v ^ n := by
      rw [← mul_pow, neg_one_mul, neg_neg]
    refine ((hlog.fun_sub hsum).const_mul ((-1 : ℝ) ^ n)).congr_deriv ?_
    show (-1 : ℝ) ^ n * (1 / (1 + v) - ∑ i ∈ range n, (-v) ^ i) = v ^ n / (1 + v)
    rw [eq_div_iff h1v]
    linear_combination (-1 : ℝ) ^ n * one_div_mul_cancel h1v - (-1 : ℝ) ^ n * hgeom + hsign
  · intro v hv
    exact div_nonneg (pow_nonneg hv n) (by linarith)

/-- `u - u²/2 ≤ log (1 + u)` for `u ≥ 0`. -/
theorem log_one_add_ge2 {u : ℝ} (hu : 0 ≤ u) : u - u ^ 2 / 2 ≤ Real.log (1 + u) := by
  have h := log_one_add_taylor 2 hu
  norm_num [sum_range_succ] at h
  linarith

/-- `log (1 + u) ≤ u - u²/2 + u³/3` for `u ≥ 0`. -/
theorem log_one_add_le3 {u : ℝ} (hu : 0 ≤ u) :
    Real.log (1 + u) ≤ u - u ^ 2 / 2 + u ^ 3 / 3 := by
  have h := log_one_add_taylor 3 hu
  norm_num [sum_range_succ] at h
  linarith

/-- `u - u²/2 + u³/3 - u⁴/4 ≤ log (1 + u)` for `u ≥ 0`. -/
theorem log_one_add_ge4 {u : ℝ} (hu : 0 ≤ u) :
    u - u ^ 2 / 2 + u ^ 3 / 3 - u ^ 4 / 4 ≤ Real.log (1 + u) := by
  have h := log_one_add_taylor 4 hu
  norm_num [sum_range_succ] at h
  linarith

/-- `log (1 + u) ≤ u - u²/2 + u³/3 - u⁴/4 + u⁵/5` for `u ≥ 0`. -/
theorem log_one_add_le5 {u : ℝ} (hu : 0 ≤ u) :
    Real.log (1 + u) ≤ u - u ^ 2 / 2 + u ^ 3 / 3 - u ^ 4 / 4 + u ^ 5 / 5 := by
  have h := log_one_add_taylor 5 hu
  norm_num [sum_range_succ] at h
  linarith

/-! ### The exponential -/

/-- `e^s ≤ 1 + s + 0.633 s²` for `0 ≤ s ≤ 0.6679`, from the Taylor bound
`e^s ≤ 1 + s + s²/2 + s³/6 + s⁴/24 + s⁵/100` on `[0, 1]`. -/
theorem exp_le_quad {s : ℝ} (h0 : 0 ≤ s) (h1 : s ≤ 6679 / 10000) :
    Real.exp s ≤ 1 + s + 633 / 1000 * s ^ 2 := by
  have hT : Real.exp s ≤ 1 + s + s ^ 2 / 2 + s ^ 3 / 6 + s ^ 4 / 24 + s ^ 5 / 100 := by
    have h := Real.exp_bound' h0 (by linarith : s ≤ 1) (n := 5) (by norm_num)
    norm_num [Finset.sum_range_succ, Nat.factorial] at h
    linarith
  have hs2 : 0 ≤ s ^ 2 := sq_nonneg s
  have e3 : s ^ 2 * s ≤ s ^ 2 * (6679 / 10000) := mul_le_mul_of_nonneg_left h1 hs2
  have e4 : s ^ 2 * s ^ 2 ≤ s ^ 2 * (6679 / 10000) ^ 2 :=
    mul_le_mul_of_nonneg_left (pow_le_pow_left₀ h0 h1 2) hs2
  have e5 : s ^ 2 * s ^ 3 ≤ s ^ 2 * (6679 / 10000) ^ 3 :=
    mul_le_mul_of_nonneg_left (pow_le_pow_left₀ h0 h1 3) hs2
  linarith

private theorem exp_le_poly4 {z : ℝ} (h0 : 0 ≤ z) (h1 : z ≤ 1) :
    Real.exp z ≤ 1 + z + z ^ 2 / 2 + z ^ 3 / 6 + z ^ 4 * (5 / 96) := by
  have hb := Real.exp_bound' h0 h1 (n := 4) (by norm_num)
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, Nat.factorial] at hb
  norm_num at hb
  linarith

/-- `exp y ≤ 1 + y + y²` for `0 ≤ y ≤ 1.7`. -/
theorem exp_le_quadratic {y : ℝ} (h0 : 0 ≤ y) (h1 : y ≤ 1.7) :
    Real.exp y ≤ 1 + y + y ^ 2 := by
  obtain ⟨z, hz⟩ : ∃ z, z = y / 2 := ⟨_, rfl⟩
  have hy : y = 2 * z := by rw [hz]; ring
  have hz0 : 0 ≤ z := by rw [hz]; linarith
  have hz1 : z ≤ 0.85 := by rw [hz]; linarith
  have hd : 0 ≤ 0.85 - z := sub_nonneg.2 hz1
  have hP := exp_le_poly4 hz0 (by linarith : z ≤ 1)
  -- the cubic and quartic terms are at most `0.2 z²`
  have hq : 0 ≤ 0.2 - z / 6 - z ^ 2 * (5 / 96) := by
    nlinarith [mul_nonneg hz0 hd]
  have hE1 : Real.exp z ≤ 1 + z + 0.7 * z ^ 2 := by
    nlinarith [mul_nonneg (sq_nonneg z) hq]
  have hE0 : 0 < Real.exp z := Real.exp_pos z
  have hB : 0 ≤ 1 + z + 0.7 * z ^ 2 := by
    have := sq_nonneg z
    linarith
  have hsq : Real.exp y = Real.exp z * Real.exp z := by
    rw [hy, two_mul, Real.exp_add]
  have hmul : Real.exp z * Real.exp z
      ≤ (1 + z + 0.7 * z ^ 2) * (1 + z + 0.7 * z ^ 2) :=
    mul_le_mul hE1 hE1 hE0.le hB
  have hfin : (1 + z + 0.7 * z ^ 2) * (1 + z + 0.7 * z ^ 2) ≤ 1 + y + y ^ 2 := by
    rw [hy]
    nlinarith [mul_nonneg hz0 hd, mul_nonneg (mul_nonneg hz0 hz0) hd,
      mul_nonneg (mul_nonneg (mul_nonneg hz0 hz0) hz0) hd, sq_nonneg z]
  rw [hsq]
  exact le_trans hmul hfin

/-- `e^{-i} = (e^{-1})^i`. -/
theorem exp_neg_nat (i : ℕ) : Real.exp (-(i : ℝ)) = Real.exp (-1) ^ i := by
  rw [← Real.exp_nat_mul]
  congr 1
  ring

/-! ### Square roots: comparison of sums with integrals -/

/-- `p = √y` and `q = √(y+1)` satisfy `0 ≤ p ≤ q` and `q² = p² + 1`. -/
private theorem sqrt_succ_facts {y : ℝ} (hy : 0 ≤ y) :
    0 ≤ Real.sqrt y ∧ Real.sqrt y ≤ Real.sqrt (y + 1)
      ∧ Real.sqrt (y + 1) * Real.sqrt (y + 1) = Real.sqrt y * Real.sqrt y + 1 := by
  have h1 : Real.sqrt y * Real.sqrt y = y := Real.mul_self_sqrt hy
  have h2 : Real.sqrt (y + 1) * Real.sqrt (y + 1) = y + 1 := Real.mul_self_sqrt (by linarith)
  exact ⟨Real.sqrt_nonneg y, Real.sqrt_le_sqrt (by linarith), by rw [h1, h2]⟩

/-- `p ≤ (2/3)(q³ - p³)`:
`2(q³ - p³) - 3p = (q - p)²(2q + p) + 3p(q² - p² - 1)`. -/
private theorem sqrt_alg3 {p q : ℝ} (hp : 0 ≤ p) (hpq : p ≤ q) (h : q * q = p * p + 1) :
    p ≤ 2 / 3 * (q * q * q - p * p * p) := by
  have h1 : 0 ≤ (q - p) ^ 2 * (2 * q + p) := mul_nonneg (sq_nonneg _) (by linarith)
  linear_combination (1 / 3 : ℝ) * h1 - p * h

/-- `p³ ≤ (2/5)(q⁵ - p⁵)`:
`2(q⁵ - p⁵) - 5p³ = (q - p)²(2q³ + 4pq² + 6p²q + 3p³) + 5p³(q² - p² - 1)`. -/
private theorem sqrt_alg5 {p q : ℝ} (hp : 0 ≤ p) (hpq : p ≤ q) (h : q * q = p * p + 1) :
    p * p * p ≤ 2 / 5 * (q * q * q * q * q - p * p * p * p * p) := by
  have hq : 0 ≤ q := hp.trans hpq
  have h1 : 0 ≤ (q - p) ^ 2 * (2 * q ^ 3 + 4 * p * q ^ 2 + 6 * p ^ 2 * q + 3 * p ^ 3) :=
    mul_nonneg (sq_nonneg _) (by positivity)
  linear_combination (1 / 5 : ℝ) * h1 - p ^ 3 * h

/-- `1/q³ ≤ 2(1/p - 1/q)`:
`2(q - p)q² - p = (q - p)²(2q + p) + p(q² - p² - 1)`. -/
private theorem sqrt_alg_m32_up {p q : ℝ} (hp : 0 < p) (hpq : p ≤ q) (h : q * q = p * p + 1) :
    1 / (q * q * q) ≤ 2 * (1 / p - 1 / q) := by
  have hq : 0 < q := lt_of_lt_of_le hp hpq
  have h1 : 0 ≤ (q - p) ^ 2 * (2 * q + p) := mul_nonneg (sq_nonneg _) (by linarith)
  have e : 2 * (1 / p - 1 / q) - 1 / (q * q * q)
      = (2 * (q - p) * (q * q) - p) / (p * (q * q * q)) := by
    field
  have h3 : 0 ≤ (2 * (q - p) * (q * q) - p) / (p * (q * q * q)) :=
    div_nonneg (by linear_combination h1 - p * h) (by positivity)
  linarith

/-- `2(1/p - 1/q) ≤ 1/p³`:
`q - 2(q - p)p² = (q - p)²(q + 2p) - q(q² - p² - 1)`. -/
private theorem sqrt_alg_m32_low {p q : ℝ} (hp : 0 < p) (hpq : p ≤ q) (h : q * q = p * p + 1) :
    2 * (1 / p - 1 / q) ≤ 1 / (p * p * p) := by
  have hq : 0 < q := lt_of_lt_of_le hp hpq
  have h1 : 0 ≤ (q - p) ^ 2 * (q + 2 * p) := mul_nonneg (sq_nonneg _) (by linarith)
  have e : 1 / (p * p * p) - 2 * (1 / p - 1 / q)
      = (q - 2 * (q - p) * (p * p)) / (p * p * p * q) := by
    field
  have h3 : 0 ≤ (q - 2 * (q - p) * (p * p)) / (p * p * p * q) :=
    div_nonneg (by linear_combination h1 + q * h) (by positivity)
  linarith

/-- `(y+1)^{-3/2} ≤ 2(1/√y - 1/√(y+1)) ≤ y^{-3/2}` for `y > 0`. -/
theorem inv_sqrt_diff_bounds {y : ℝ} (hy : 0 < y) :
    1 / ((y + 1) * Real.sqrt (y + 1)) ≤ 2 * (1 / Real.sqrt y - 1 / Real.sqrt (y + 1))
      ∧ 2 * (1 / Real.sqrt y - 1 / Real.sqrt (y + 1)) ≤ 1 / (y * Real.sqrt y) := by
  obtain ⟨_, hpq, h⟩ := sqrt_succ_facts hy.le
  have hp : 0 < Real.sqrt y := Real.sqrt_pos.2 hy
  have h1 : Real.sqrt y * Real.sqrt y = y := Real.mul_self_sqrt hy.le
  have h2 : Real.sqrt (y + 1) * Real.sqrt (y + 1) = y + 1 := Real.mul_self_sqrt (by linarith)
  have hup := sqrt_alg_m32_up hp hpq h
  have hlow := sqrt_alg_m32_low hp hpq h
  rw [h2] at hup
  rw [h1] at hlow
  exact ⟨hup, hlow⟩

/-- `∑_{i=1}^{n} 1/√i ≤ 2√n - 1` for `n ≥ 1`. -/
theorem sum_range_inv_sqrt_le {n : ℕ} (hn : 1 ≤ n) :
    ∑ i ∈ range n, 1 / Real.sqrt ((i : ℝ) + 1) ≤ 2 * Real.sqrt (n : ℝ) - 1 := by
  induction n, hn using Nat.le_induction with
  | base =>
    rw [sum_range_one]
    norm_num
  | succ n hn ih =>
    -- `1/q ≤ 2(q - p)`, i.e. `1 ≤ (q - p)² + 1`
    obtain ⟨_, _, h⟩ := sqrt_succ_facts (y := (n : ℝ)) (Nat.cast_nonneg n)
    have hq : 0 < Real.sqrt ((n : ℝ) + 1) := Real.sqrt_pos.2 (by positivity)
    have hstep : 1 / Real.sqrt ((n : ℝ) + 1)
        ≤ 2 * (Real.sqrt ((n : ℝ) + 1) - Real.sqrt (n : ℝ)) := by
      rw [div_le_iff₀ hq]
      nlinarith [sq_nonneg (Real.sqrt ((n : ℝ) + 1) - Real.sqrt (n : ℝ))]
    rw [sum_range_succ, Nat.cast_add, Nat.cast_one]
    linarith

/-- `2√(n+1) - 2 ≤ ∑_{i=1}^{n} 1/√i`. -/
theorem sum_range_inv_sqrt_ge (n : ℕ) :
    2 * Real.sqrt ((n : ℝ) + 1) - 2 ≤ ∑ i ∈ range n, 1 / Real.sqrt ((i : ℝ) + 1) := by
  induction n with
  | zero => norm_num
  | succ n ih =>
    -- `2(q - p) ≤ 1/p`, i.e. `1 - (q - p)² ≤ 1`, with `y = n + 1`
    have hy : (0 : ℝ) < (n : ℝ) + 1 := by positivity
    obtain ⟨_, _, h⟩ := sqrt_succ_facts hy.le
    have hp : 0 < Real.sqrt ((n : ℝ) + 1) := Real.sqrt_pos.2 hy
    have hstep : 2 * (Real.sqrt ((n : ℝ) + 1 + 1) - Real.sqrt ((n : ℝ) + 1))
        ≤ 1 / Real.sqrt ((n : ℝ) + 1) := by
      rw [le_div_iff₀ hp]
      nlinarith [sq_nonneg (Real.sqrt ((n : ℝ) + 1 + 1) - Real.sqrt ((n : ℝ) + 1))]
    rw [sum_range_succ, Nat.cast_add, Nat.cast_one]
    linarith

/-- `∑_{i<R} √i ≤ (2/3) R√R`. -/
theorem sum_range_sqrt_le (R : ℕ) :
    ∑ i ∈ range R, Real.sqrt (i : ℝ) ≤ 2 / 3 * ((R : ℝ) * Real.sqrt (R : ℝ)) := by
  induction R with
  | zero => simp
  | succ n ih =>
    have hy : (0 : ℝ) ≤ (n : ℝ) := Nat.cast_nonneg n
    obtain ⟨hp, hpq, h⟩ := sqrt_succ_facts hy
    have h1 : Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) = (n : ℝ) := Real.mul_self_sqrt hy
    have h2 : Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1) = (n : ℝ) + 1 :=
      Real.mul_self_sqrt (by linarith)
    have hstep := sqrt_alg3 hp hpq h
    rw [h1, h2] at hstep
    rw [sum_range_succ, Nat.cast_add, Nat.cast_one]
    linarith

/-- `∑_{i<R} i√i ≤ (2/5) R²√R`. -/
theorem sum_range_sqrt_cube_le (R : ℕ) :
    ∑ i ∈ range R, (i : ℝ) * Real.sqrt (i : ℝ) ≤ 2 / 5 * ((R : ℝ) ^ 2 * Real.sqrt (R : ℝ)) := by
  induction R with
  | zero => simp
  | succ n ih =>
    have hy : (0 : ℝ) ≤ (n : ℝ) := Nat.cast_nonneg n
    obtain ⟨hp, hpq, h⟩ := sqrt_succ_facts hy
    have h1 : Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) = (n : ℝ) := Real.mul_self_sqrt hy
    have h2 : Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1) = (n : ℝ) + 1 :=
      Real.mul_self_sqrt (by linarith)
    have hstep := sqrt_alg5 hp hpq h
    have e1 : Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ)
        = (n : ℝ) * Real.sqrt (n : ℝ) := by rw [h1]
    have e2 : Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ)
        * Real.sqrt (n : ℝ) = (n : ℝ) ^ 2 * Real.sqrt (n : ℝ) := by
      calc Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ)
            * Real.sqrt (n : ℝ)
          = (Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ)) * (Real.sqrt (n : ℝ) * Real.sqrt (n : ℝ))
            * Real.sqrt (n : ℝ) := by ring
        _ = (n : ℝ) ^ 2 * Real.sqrt (n : ℝ) := by rw [h1]; ring
    have e3 : Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)
        * Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)
        = ((n : ℝ) + 1) ^ 2 * Real.sqrt ((n : ℝ) + 1) := by
      calc Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)
            * Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)
          = (Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1))
            * (Real.sqrt ((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1)) * Real.sqrt ((n : ℝ) + 1) := by
            ring
        _ = ((n : ℝ) + 1) ^ 2 * Real.sqrt ((n : ℝ) + 1) := by rw [h2]; ring
    rw [e3, e2, e1] at hstep
    rw [sum_range_succ, Nat.cast_add, Nat.cast_one]
    linarith

/-- `∑_{i=1}^{n} i^{-3/2} ≤ 3`. -/
theorem sum_range_inv_sqrt_cube_le (n : ℕ) :
    ∑ i ∈ range n, 1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1)) ≤ 3 := by
  have key : ∀ m : ℕ, 1 ≤ m →
      ∑ i ∈ range m, 1 / (((i : ℝ) + 1) * Real.sqrt ((i : ℝ) + 1))
        ≤ 3 - 2 * (1 / Real.sqrt (m : ℝ)) := by
    intro m hm
    induction m, hm using Nat.le_induction with
    | base =>
      rw [sum_range_one]
      norm_num
    | succ m hm ih =>
      have h := (inv_sqrt_diff_bounds (y := (m : ℝ)) (by exact_mod_cast hm)).1
      rw [sum_range_succ, Nat.cast_add, Nat.cast_one]
      linarith
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · norm_num
  · have h := key n hn
    have h0 : (0 : ℝ) ≤ 1 / Real.sqrt (n : ℝ) := by positivity
    linarith

end Parking
