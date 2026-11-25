import Parking.Basic.RealBounds
import Parking.Basic.Sums
import Parking.Cayley.Stirling
import Parking.Tilt.Critical

/-!
# The Cayley sum at the critical tilt

`S(c) = x_c ∑_{j=1}^{c} c_j x_c^j = ∑_{n=2}^{c+1} n^{n-1} x_c^n / n!` is the sum of the tilted tree
numbers of the sizes `2, …, c+1` at the critical tilt `x_c = (c/(c+1))^(c-1)`.  The monotonicity of
the tilted environment at the critical tilt (`zrT_anti_crit`) needs `S(c) ≤ 1`.

`cayleySum_le_one` proves this for all `c ≥ 12` by estimates; `S(c)` is never evaluated.

* Stirling's bound `n! ≥ √(2πn) (n/e)^n` (`poissonMass_le`) gives, term by term,
  `x^n n^{n-1}/n! ≤ (e x)^n / (√(2π) n √n)` (`pow_mul_cc_le`).
* At the critical tilt `e x_c ≤ exp β` with `β = 3/(2c)` (`exp_one_mul_xcrit_le`, from
  `log (1+t) ≥ 2t/(t+2)`), so `(e x_c)^n ≤ exp (β n)` with `β n ≤ β (c+1) ≤ 1.625`.
* On that range `exp y ≤ 1 + y + y²` (`exp_le_quadratic`, for `0 ≤ y ≤ 1.7`), which leaves the
  three sums `∑ 1/(n√n)`, `∑ 1/√n`, `∑ √n` over `2 ≤ n ≤ c+1`.  The first is compared with the
  integral over intervals centred at the integers, by induction from the one-step inequality
  `inv_mul_sqrt_step`: `∑ 1/(n√n) ≤ 2/√(3/2) - 2/√(c+3/2)`.  The other two are the sums of
  `Parking/Basic/RealBounds.lean` without their first terms:
  `∑ 1/√n ≤ 2√(c+1) - 2`, `∑ √n ≤ (2/3)(c+2)√(c+2)`.
* Finally (`final_bound`)
  `2/√(3/2) - 2/√(c+3/2) + β (2√(c+1) - 2) + β² (2/3)(c+2)√(c+2) ≤ √(2π)` for `c ≥ 12`:
  the left side is `< 2.29` at `c = 12`; the proof bounds it by `1.6331 + 0.87`, and
  `√(2π) > 2.5066`.
-/

namespace Parking

open Finset

/-- `S(c) = x_c ∑_{j=1}^{c} c_j x_c^j`, at the critical tilt `x_c`. -/
private noncomputable def Sc (c : ℕ) : ℝ := xcrit c * ∑ j ∈ range c, ccT (xcrit c) (j + 1)

/-! ### Stirling -/

/-- `x^(n+1) c_n ≤ (e x)^(n+1) / (√(2π) (n+1) √(n+1))`, where `c_n = (n+1)^n/(n+1)!`. -/
private theorem pow_mul_cc_le {x : ℝ} (hx : 0 ≤ x) (n : ℕ) :
    x ^ (n + 1) * cc n
      ≤ (Real.exp 1 * x) ^ (n + 1)
          / (Real.sqrt (2 * Real.pi) * (((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1))) := by
  have hn1 : (0 : ℝ) < (n : ℝ) + 1 := by positivity
  have hn1' : (n : ℝ) + 1 ≠ 0 := hn1.ne'
  have he : Real.exp 1 ≠ 0 := (Real.exp_pos 1).ne'
  have hf : ((n + 1).factorial : ℝ) ≠ 0 := by positivity
  have hid : x ^ (n + 1) * cc n
      = (Real.exp 1 * x) ^ (n + 1) * poissonMass (n + 1) / ((n : ℝ) + 1) := by
    rw [cc_eq, poissonMass_eq]
    push_cast
    rw [mul_pow, div_pow, pow_succ ((n : ℝ) + 1) n]
    field
  have hR := poissonMass_le (n := n + 1) (by omega)
  have hsq : Real.sqrt (2 * Real.pi * ((n + 1 : ℕ) : ℝ))
      = Real.sqrt (2 * Real.pi) * Real.sqrt ((n : ℝ) + 1) := by
    rw [Real.sqrt_mul (by positivity), Nat.cast_add, Nat.cast_one]
  rw [hsq] at hR
  rw [hid]
  have hρ : 0 ≤ (Real.exp 1 * x) ^ (n + 1) :=
    pow_nonneg (mul_nonneg (Real.exp_pos 1).le hx) _
  have hs2 : 0 < Real.sqrt (2 * Real.pi) := Real.sqrt_pos.2 (by positivity)
  have hs1 : 0 < Real.sqrt ((n : ℝ) + 1) := Real.sqrt_pos.2 hn1
  have hs2' : Real.sqrt (2 * Real.pi) ≠ 0 := hs2.ne'
  have hs1' : Real.sqrt ((n : ℝ) + 1) ≠ 0 := hs1.ne'
  calc (Real.exp 1 * x) ^ (n + 1) * poissonMass (n + 1) / ((n : ℝ) + 1)
      ≤ (Real.exp 1 * x) ^ (n + 1)
            * (1 / (Real.sqrt (2 * Real.pi) * Real.sqrt ((n : ℝ) + 1))) / ((n : ℝ) + 1) :=
        div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left hR hρ) hn1.le
    _ = (Real.exp 1 * x) ^ (n + 1)
          / (Real.sqrt (2 * Real.pi) * (((n : ℝ) + 1) * Real.sqrt ((n : ℝ) + 1))) := by
        field

/-! ### The critical tilt -/

/-- `e x_c ≤ exp (3/(2c))`. -/
theorem exp_one_mul_xcrit_le {c : ℕ} (hc : 1 ≤ c) :
    Real.exp 1 * xcrit c ≤ Real.exp (3 / (2 * (c : ℝ))) := by
  have hc0 : (0 : ℝ) < (c : ℝ) := by exact_mod_cast hc
  have hc1 : (1 : ℝ) ≤ (c : ℝ) := by exact_mod_cast hc
  have hcne : (c : ℝ) ≠ 0 := hc0.ne'
  -- `log (1 + 1/c) ≥ 2/(2c+1)`
  have hlog : 2 / (2 * (c : ℝ) + 1) ≤ Real.log (1 + 1 / (c : ℝ)) := by
    have h := Real.le_log_one_add_of_nonneg (x := 1 / (c : ℝ)) (by positivity)
    have e : 2 * (1 / (c : ℝ)) / (1 / (c : ℝ) + 2) = 2 / (2 * (c : ℝ) + 1) := by
      rw [div_eq_div_iff (by positivity) (by positivity)]
      field
    rw [e] at h
    exact h
  -- `(1 + 1/c)^(c-1) ≥ exp (1 - 3/(2c))`
  have hbase : (0 : ℝ) < 1 + 1 / (c : ℝ) := by positivity
  have hpow : Real.exp (1 - 3 / (2 * (c : ℝ))) ≤ (1 + 1 / (c : ℝ)) ^ (c - 1) := by
    rw [← Real.exp_log (pow_pos hbase (c - 1)), Real.log_pow, Real.exp_le_exp]
    have hcast : ((c - 1 : ℕ) : ℝ) = (c : ℝ) - 1 := by
      rw [Nat.cast_sub hc, Nat.cast_one]
    rw [hcast]
    have h1 : ((c : ℝ) - 1) * (2 / (2 * (c : ℝ) + 1))
        ≤ ((c : ℝ) - 1) * Real.log (1 + 1 / (c : ℝ)) :=
      mul_le_mul_of_nonneg_left hlog (by linarith)
    have h2 : 1 - 3 / (2 * (c : ℝ)) ≤ ((c : ℝ) - 1) * (2 / (2 * (c : ℝ) + 1)) := by
      have e1 : 1 - 3 / (2 * (c : ℝ)) = (2 * (c : ℝ) - 3) / (2 * (c : ℝ)) := by
        field
      have e2 : ((c : ℝ) - 1) * (2 / (2 * (c : ℝ) + 1))
          = (2 * ((c : ℝ) - 1)) / (2 * (c : ℝ) + 1) := by
        ring
      rw [e1, e2, div_le_div_iff₀ (by linarith) (by linarith)]
      nlinarith
    linarith
  have hx := xcrit_mul_psi hc
  have hxpos : 0 < xcrit c := xcrit_pos c
  have h3 : xcrit c * Real.exp (1 - 3 / (2 * (c : ℝ))) ≤ 1 :=
    calc xcrit c * Real.exp (1 - 3 / (2 * (c : ℝ)))
        ≤ xcrit c * (1 + 1 / (c : ℝ)) ^ (c - 1) := mul_le_mul_of_nonneg_left hpow hxpos.le
      _ = 1 := hx
  have h4 : Real.exp 1
      = Real.exp (1 - 3 / (2 * (c : ℝ))) * Real.exp (3 / (2 * (c : ℝ))) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have h5 : 0 ≤ Real.exp (3 / (2 * (c : ℝ))) := (Real.exp_pos _).le
  have h6 := mul_le_mul_of_nonneg_right h3 h5
  rw [h4]
  linarith

/-! ### Three sums -/

/-- `1/(a√a) ≤ 2/√(a - 1/2) - 2/√(a + 1/2)`. -/
private theorem inv_mul_sqrt_step {a : ℝ} (ha : 1 ≤ a) :
    1 / (a * Real.sqrt a)
      ≤ 2 / Real.sqrt (a - 1 / 2) - 2 / Real.sqrt (a + 1 / 2) := by
  obtain ⟨s, hsdef⟩ : ∃ s, s = Real.sqrt a := ⟨_, rfl⟩
  obtain ⟨p, hpdef⟩ : ∃ p, p = Real.sqrt (a - 1 / 2) := ⟨_, rfl⟩
  obtain ⟨q, hqdef⟩ : ∃ q, q = Real.sqrt (a + 1 / 2) := ⟨_, rfl⟩
  have ha0 : 0 < a := by linarith
  have hs0 : 0 < s := by rw [hsdef]; exact Real.sqrt_pos.2 (by linarith)
  have hp0 : 0 < p := by rw [hpdef]; exact Real.sqrt_pos.2 (by linarith)
  have hq0 : 0 < q := by rw [hqdef]; exact Real.sqrt_pos.2 (by linarith)
  have hs : s ^ 2 = a := by rw [hsdef]; exact Real.sq_sqrt (by linarith)
  have hp : p ^ 2 = a - 1 / 2 := by rw [hpdef]; exact Real.sq_sqrt (by linarith)
  have hq : q ^ 2 = a + 1 / 2 := by rw [hqdef]; exact Real.sq_sqrt (by linarith)
  rw [← hsdef, ← hpdef, ← hqdef]
  -- `p q ≤ a`
  have hpq : p * q ≤ a := by
    by_contra h
    rw [not_le] at h
    have e : (p * q) ^ 2 = a ^ 2 - 1 / 4 := by
      rw [mul_pow, hp, hq]
      ring
    have h' := mul_pos (by linarith : (0 : ℝ) < p * q - a) (add_pos (mul_pos hp0 hq0) ha0)
    nlinarith
  -- `p + q ≤ 2 s`
  have hsum : p + q ≤ 2 * s := by
    by_contra h
    rw [not_le] at h
    have h' := mul_pos (by linarith : (0 : ℝ) < p + q - 2 * s)
      (by linarith : (0 : ℝ) < p + q + 2 * s)
    nlinarith
  have hkey : p * q * (p + q) ≤ 2 * (a * s) := by
    have h1 : p * q * (p + q) ≤ a * (2 * s) :=
      mul_le_mul hpq hsum (by linarith) ha0.le
    linarith
  have hqp : (q - p) * (q + p) = 1 := by
    have e : (q - p) * (q + p) = q ^ 2 - p ^ 2 := by ring
    rw [e, hp, hq]
    ring
  rw [div_sub_div _ _ hp0.ne' hq0.ne', div_le_div_iff₀ (mul_pos ha0 hs0) (mul_pos hp0 hq0)]
  have h2 : 0 ≤ (p + q) * ((2 * q - p * 2) * (a * s) - 1 * (p * q)) := by
    have e2 : (p + q) * ((2 * q - p * 2) * (a * s))
        = 2 * (a * s) * ((q - p) * (q + p)) := by ring
    rw [mul_sub, e2, hqp]
    linarith
  have h3 := nonneg_of_mul_nonneg_right h2 (by linarith : (0 : ℝ) < p + q)
  linarith

private theorem sum_inv_mul_sqrt_le (c : ℕ) :
    ∑ j ∈ range c, 1 / (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))
      ≤ 2 / Real.sqrt (3 / 2) - 2 / Real.sqrt ((c : ℝ) + 3 / 2) := by
  induction c with
  | zero => simp
  | succ c ih =>
    rw [sum_range_succ,
      show ((c + 1 : ℕ) : ℝ) + 3 / 2 = (c : ℝ) + 2 + 1 / 2 by
        rw [Nat.cast_add, Nat.cast_one]; ring]
    have hc0 : (0 : ℝ) ≤ (c : ℝ) := Nat.cast_nonneg c
    have h := inv_mul_sqrt_step (a := (c : ℝ) + 2) (by linarith)
    rw [show (c : ℝ) + 2 - 1 / 2 = (c : ℝ) + 3 / 2 by ring] at h
    linarith

/-- `∑_{n=2}^{c+1} 1/√n ≤ 2√(c+1) - 2`, from `sum_range_inv_sqrt_le`. -/
private theorem sum_inv_sqrt_le (c : ℕ) :
    ∑ j ∈ range c, 1 / Real.sqrt ((j : ℝ) + 2) ≤ 2 * Real.sqrt ((c : ℝ) + 1) - 2 := by
  have h := sum_range_inv_sqrt_le (n := c + 1) (by omega)
  have e : ∑ i ∈ range (c + 1), 1 / Real.sqrt ((i : ℝ) + 1)
      = ∑ j ∈ range c, 1 / Real.sqrt ((j : ℝ) + 2) + 1 := by
    rw [sum_range_succ']
    congr 1
    · refine sum_congr rfl fun j _ => ?_
      congr 2
      push_cast
      ring
    · norm_num
  rw [e] at h
  push_cast at h
  linarith

/-- `∑_{n=2}^{c+1} √n ≤ (2/3)(c+2)√(c+2)`, from `sum_range_sqrt_le`. -/
private theorem sum_sqrt_le (c : ℕ) :
    ∑ j ∈ range c, Real.sqrt ((j : ℝ) + 2)
      ≤ 2 / 3 * (((c : ℝ) + 2) * Real.sqrt ((c : ℝ) + 2)) := by
  have h := sum_range_sqrt_le (c + 2)
  have e : ∑ i ∈ range (c + 2), Real.sqrt (i : ℝ)
      = ∑ j ∈ range c, Real.sqrt ((j : ℝ) + 2) + 1 := by
    rw [sum_range_succ', sum_range_succ', add_assoc]
    congr 1
    · refine sum_congr rfl fun j _ => ?_
      congr 1
      push_cast
      ring
    · norm_num
  rw [e] at h
  push_cast at h
  linarith

/-! ### The final inequality -/

private theorem final_bound {c : ℝ} (hc : 12 ≤ c) :
    2 / Real.sqrt (3 / 2) - 2 / Real.sqrt (c + 3 / 2)
        + 3 / (2 * c) * (2 * Real.sqrt (c + 1) - 2)
        + (3 / (2 * c)) ^ 2 * (2 / 3 * ((c + 2) * Real.sqrt (c + 2)))
      ≤ Real.sqrt (2 * Real.pi) := by
  have hc0 : 0 < c := by linarith
  have hcne : c ≠ 0 := hc0.ne'
  obtain ⟨r, hrdef⟩ : ∃ r, r = Real.sqrt (c + 2) := ⟨_, rfl⟩
  have hr2 : r ^ 2 = c + 2 := by rw [hrdef]; exact Real.sq_sqrt (by linarith)
  have hr374 : 3.74 ≤ r := by
    rw [hrdef, Real.le_sqrt' (by norm_num)]
    have e : (3.74 : ℝ) ^ 2 = 13.9876 := by norm_num
    rw [e]
    linarith
  have hr0 : 0 < r := by linarith
  have hrne : r ≠ 0 := hr0.ne'
  -- the two constants
  have h1 : 2 / Real.sqrt (3 / 2) ≤ 1.6331 := by
    have hs : (1.2247 : ℝ) ≤ Real.sqrt (3 / 2) := by
      rw [Real.le_sqrt' (by norm_num)]
      norm_num
    rw [div_le_iff₀ (by linarith)]
    linarith
  have h2 : (2.5066 : ℝ) ≤ Real.sqrt (2 * Real.pi) := by
    rw [Real.le_sqrt' (by norm_num)]
    have e : (2.5066 : ℝ) ^ 2 = 6.28304356 := by norm_num
    rw [e]
    linarith [Real.pi_gt_d6]
  -- comparison of the square roots with `r = √(c+2)`
  have h3 : Real.sqrt (c + 1) ≤ r := by
    rw [hrdef]
    exact Real.sqrt_le_sqrt (by linarith)
  have h4 : 2 / r ≤ 2 / Real.sqrt (c + 3 / 2) := by
    have hpos : 0 < Real.sqrt (c + 3 / 2) := Real.sqrt_pos.2 (by linarith)
    have hle : Real.sqrt (c + 3 / 2) ≤ r := by
      rw [hrdef]
      exact Real.sqrt_le_sqrt (by linarith)
    exact div_le_div_of_nonneg_left (by norm_num) hpos hle
  -- the part depending on `c`
  have hT : -(2 / r) + 3 * (r - 1) / c + 3 * r ^ 3 / (2 * c ^ 2) ≤ 0.87 := by
    have key : 2.5 * c ^ 2 + 12 * c + 6 ≤ r * c * (0.87 * c + 3) := by
      have hA : 0 ≤ (r - 3.74) * (c * (0.87 * c + 3)) :=
        mul_nonneg (by linarith) (mul_nonneg hc0.le (by linarith))
      nlinarith [mul_nonneg (by linarith : (0 : ℝ) ≤ c - 12) hc0.le]
    have h4' : r ^ 4 = (c + 2) ^ 2 := by
      rw [show r ^ 4 = (r ^ 2) ^ 2 by ring, hr2]
    have hcr : c * r ^ 2 = c * (c + 2) := by rw [hr2]
    have e : -(2 / r) + 3 * (r - 1) / c + 3 * r ^ 3 / (2 * c ^ 2)
        = (-4 * c ^ 2 + 6 * r * (r - 1) * c + 3 * r ^ 4) / (2 * r * c ^ 2) := by
      field
    rw [e, div_le_iff₀ (by positivity)]
    nlinarith
  have hA2 : 3 / (2 * c) * (2 * Real.sqrt (c + 1) - 2) ≤ 3 * (r - 1) / c := by
    have h5 : 3 / (2 * c) * (2 * Real.sqrt (c + 1) - 2) ≤ 3 / (2 * c) * (2 * r - 2) :=
      mul_le_mul_of_nonneg_left (by linarith) (by positivity)
    have e5 : 3 / (2 * c) * (2 * r - 2) = 3 * (r - 1) / c := by
      field
    linarith
  have hA3 : (3 / (2 * c)) ^ 2 * (2 / 3 * ((c + 2) * r)) = 3 * r ^ 3 / (2 * c ^ 2) := by
    rw [← hr2]
    field
  rw [← hrdef, hA3]
  linarith

/-- The bound of one term, split into the three sums (`s = √n`, `P = √(2π)`). -/
private theorem term_alg {β s P : ℝ} (hs : 0 < s) (hP : 0 < P) :
    (1 + β * s ^ 2 + (β * s ^ 2) ^ 2) / (P * (s ^ 2 * s))
      = (1 / (s ^ 2 * s) + β * (1 / s) + β ^ 2 * s) / P := by
  have hs' : s ≠ 0 := hs.ne'
  have hP' : P ≠ 0 := hP.ne'
  field

/-- **The Cayley sum is at most `1`**: `S(c) ≤ 1` for `c ≥ 12`. -/
private theorem Sc_le_one {c : ℕ} (hc : 12 ≤ c) : Sc c ≤ 1 := by
  have hc1 : 1 ≤ c := by omega
  have hcR : (12 : ℝ) ≤ (c : ℝ) := by exact_mod_cast hc
  have hc0 : (0 : ℝ) < (c : ℝ) := by linarith
  have hx0 : 0 < xcrit c := xcrit_pos c
  have hρ0 : 0 ≤ Real.exp 1 * xcrit c := mul_nonneg (Real.exp_pos 1).le hx0.le
  have hρ := exp_one_mul_xcrit_le hc1
  obtain ⟨β, hβ⟩ : ∃ β : ℝ, β = 3 / (2 * (c : ℝ)) := ⟨_, rfl⟩
  rw [← hβ] at hρ
  have hβ0 : 0 ≤ β := by rw [hβ]; positivity
  have hs2 : 0 < Real.sqrt (2 * Real.pi) := Real.sqrt_pos.2 (by positivity)
  -- termwise bound
  have hterm : ∀ j ∈ range c, xcrit c * ccT (xcrit c) (j + 1)
      ≤ (1 / (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))
          + β * (1 / Real.sqrt ((j : ℝ) + 2))
          + β ^ 2 * Real.sqrt ((j : ℝ) + 2)) / Real.sqrt (2 * Real.pi) := by
    intro j hj
    rw [mem_range] at hj
    have hj0 : (0 : ℝ) ≤ (j : ℝ) := Nat.cast_nonneg j
    have ha0 : (0 : ℝ) < (j : ℝ) + 2 := by linarith
    have hsa : 0 < Real.sqrt ((j : ℝ) + 2) := Real.sqrt_pos.2 ha0
    have hsq : Real.sqrt ((j : ℝ) + 2) ^ 2 = (j : ℝ) + 2 := Real.sq_sqrt ha0.le
    -- Stirling
    have h1 := pow_mul_cc_le hx0.le (j + 1)
    have e1 : xcrit c * ccT (xcrit c) (j + 1) = xcrit c ^ (j + 1 + 1) * cc (j + 1) := by
      unfold ccT
      ring
    have e2 : (((j + 1 : ℕ) : ℝ) + 1) = (j : ℝ) + 2 := by
      rw [Nat.cast_add, Nat.cast_one]
      ring
    rw [e2] at h1
    -- the power of `e x_c`
    have hy1 : β * ((j : ℝ) + 2) ≤ 1.7 := by
      have hj1 : j + 1 ≤ c := hj
      have hj' : ((j + 1 : ℕ) : ℝ) ≤ (c : ℝ) := by exact_mod_cast hj1
      rw [Nat.cast_add, Nat.cast_one] at hj'
      rw [hβ, div_mul_eq_mul_div, div_le_iff₀ (by linarith)]
      linarith
    have hy0 : 0 ≤ β * ((j : ℝ) + 2) := mul_nonneg hβ0 ha0.le
    have h2 : (Real.exp 1 * xcrit c) ^ (j + 1 + 1)
        ≤ 1 + β * ((j : ℝ) + 2) + (β * ((j : ℝ) + 2)) ^ 2 := by
      calc (Real.exp 1 * xcrit c) ^ (j + 1 + 1) ≤ Real.exp β ^ (j + 1 + 1) :=
            pow_le_pow_left₀ hρ0 hρ _
        _ = Real.exp (β * ((j : ℝ) + 2)) := by
            rw [← Real.exp_nat_mul]
            congr 1
            push_cast
            ring
        _ ≤ 1 + β * ((j : ℝ) + 2) + (β * ((j : ℝ) + 2)) ^ 2 := exp_le_quadratic hy0 hy1
    have hD : 0 < Real.sqrt (2 * Real.pi) * (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2)) :=
      mul_pos hs2 (mul_pos ha0 hsa)
    have hal := term_alg (β := β) hsa hs2
    rw [hsq] at hal
    rw [e1]
    calc xcrit c ^ (j + 1 + 1) * cc (j + 1)
        ≤ (Real.exp 1 * xcrit c) ^ (j + 1 + 1)
            / (Real.sqrt (2 * Real.pi) * (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))) := h1
      _ ≤ (1 + β * ((j : ℝ) + 2) + (β * ((j : ℝ) + 2)) ^ 2)
            / (Real.sqrt (2 * Real.pi) * (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))) :=
          div_le_div_of_nonneg_right h2 hD.le
      _ = (1 / (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))
            + β * (1 / Real.sqrt ((j : ℝ) + 2))
            + β ^ 2 * Real.sqrt ((j : ℝ) + 2)) / Real.sqrt (2 * Real.pi) := hal
  -- sum the terms
  have hsum : Sc c ≤ ∑ j ∈ range c, (1 / (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))
          + β * (1 / Real.sqrt ((j : ℝ) + 2))
          + β ^ 2 * Real.sqrt ((j : ℝ) + 2)) / Real.sqrt (2 * Real.pi) := by
    unfold Sc
    rw [mul_sum]
    exact sum_le_sum hterm
  rw [← sum_div, sum_add_distrib, sum_add_distrib, ← mul_sum, ← mul_sum] at hsum
  have hS1 := sum_inv_mul_sqrt_le c
  have hS2 := sum_inv_sqrt_le c
  have hS3 := sum_sqrt_le c
  have hF := final_bound hcR
  rw [← hβ] at hF
  have hnum : ∑ j ∈ range c, 1 / (((j : ℝ) + 2) * Real.sqrt ((j : ℝ) + 2))
        + β * ∑ j ∈ range c, 1 / Real.sqrt ((j : ℝ) + 2)
        + β ^ 2 * ∑ j ∈ range c, Real.sqrt ((j : ℝ) + 2) ≤ Real.sqrt (2 * Real.pi) := by
    have h2 := mul_le_mul_of_nonneg_left hS2 hβ0
    have h3 := mul_le_mul_of_nonneg_left hS3 (sq_nonneg β)
    linarith
  calc Sc c ≤ _ := hsum
    _ ≤ Real.sqrt (2 * Real.pi) / Real.sqrt (2 * Real.pi) :=
        div_le_div_of_nonneg_right hnum hs2.le
    _ = 1 := div_self hs2.ne'

/-- **The Cayley sum at the critical tilt**: `x_k ∑_{j=1}^{k} c_j x_k^j ≤ 1` for `k ≥ 12`. -/
theorem cayleySum_le_one {k : ℕ} (hk : 12 ≤ k) : xcrit k * ∑ j ∈ Icc 1 k, ccT (xcrit k) j ≤ 1 := by
  rw [sum_Icc_one_eq_range]
  exact Sc_le_one hk

end Parking
