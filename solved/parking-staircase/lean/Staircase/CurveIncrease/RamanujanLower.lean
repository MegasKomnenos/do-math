import Parking.Basic.RealBounds
import Parking.Cayley.Stirling
import Parking.NextColumn.Ramanujan
import Batteries.Tactic.OpenPrivate

/-!
# The lower half of Ramanujan's estimate for the Poisson law

For a natural number `m` let `P(m) = e^{-m} ∑_{i ≤ m} m^i/i!` be the mass that the Poisson law of
mean `m` puts on `{0, …, m}`, and let `poissonMass m = e^{-m} m^m/m!` be its mass at the point `m`.
Ramanujan's estimate says that `P(m)` exceeds `1/2` by a little less than two thirds of
`poissonMass m`.  The module `Parking.NextColumn.Ramanujan` proves the upper half,
`P(m) ≤ 1/2 + (2/3) poissonMass m`, and from it the upper bound `sbirth_le` for the mean
`sbirth m = P(m)/poissonMass m - 1` of the birthday law.  This module proves the lower half,

`1/2 + (2/3 - 1/(15 m)) poissonMass m ≤ P(m)`  for `m ≥ 2`,

and states it for the mean of the birthday law.

## Result

* `sbirth_ge` : `1/(2 poissonMass m) - 1/3 - 1/(15 m) ≤ sbirth m` for `m ≥ 2`.

## The proof

Write `Ψ_m(x) = e^{-x} ∑_{i ≤ m} x^i/i!` (`psiF m x`) and `g_m(x) = e^{-x} x^m/m!`
(`gF m x`) for the mass that the Poisson law of mean `x` puts on `{0, …, m}` and on `{m}`.  These
are the functions of `Parking.NextColumn.Ramanujan`, where they are private; what is proved there
about them is used here: `Ψ_m' = -g_m` (`hasDerivAt_psiF`), the derivative of `g_m`
(`hasDerivAt_gF`), `poissonMass m = g_m(m)`, `poissonMass (m + 1) = g_m(m + 1)`, and
`sbirth m = P(m)/poissonMass m - 1` (`sbirth_eq`).  Moreover `P(m) = Ψ_m(m)` and
`P(m + 1) = Ψ_m(m + 1) + poissonMass (m + 1)`.

Two steps of the proof are private lemmas whose statements are of interest in themselves:
`poissonMass (m + 1) ≤ poissonMass m`, and `1/2 ≤ P(m)`, that is, the Poisson law of mean `m` puts
at least half of its mass on `{0, …, m}`.  Each of the three analytic steps below shows that a
function of one real variable does not increase on an interval, by showing that its derivative is
nonpositive there.

*The median.*  The function `u ↦ Ψ_m(m + u) + Ψ_m(m - u)` has the derivative
`g_m(m - u) - g_m(m + u)`.  For `0 ≤ u < m` this is nonpositive: the claim
`(m - u)^m e^{2u} ≤ (m + u)^m` is the `m`-th power of `e^{2u/m} ≤ (m + u)/(m - u)`, which is the
bound `2x/(x + 2) ≤ log (1 + x)` at `x = 2u/(m - u)`.  So the value at `u = m` is at most the value
at `u = 0`, that is, `1 ≤ Ψ_m(0) + Ψ_m(2m) ≤ 2 Ψ_m(m)`.

*One step.*  For `m ≥ 1` and `0 ≤ s ≤ m`,

`g_m(m) (1 - (s³/6 + s⁴/8)/m²) ≤ g_m(m + s) (1 + s²/(2(m + s)))`.

Indeed `g_m(m + s)/g_m(m) = e^{-s} (1 + s/m)^m`.  With `u = s/m` and `w = s²/(2(m + s))`, the
bounds `u - u²/2 + u³/3 - u⁴/4 ≤ log (1 + u)`, `w - w²/2 ≤ log (1 + w)` and `1 - y ≤ e^{-y}` reduce
the claim to an inequality between the exponents, and the difference of the two exponents is

`s⁴ [ (m - s)/(4 m³ (m + s)) + s (2m + s)/(8 m² (m + s)²) ] ≥ 0`.

Now let

`G(s) = Ψ_m(m + s) + s ((2/3) g_m(m) + (1/3) g_m(m + s)) - (g_m(m)/m²) (s⁴/36 + s⁵/60)`

(`twoPointGap m s`).  Its derivative at `s ≥ 0` is two thirds of the difference of the two sides of
the inequality above, so `G(1) ≤ G(0)`, which reads

`[P(m + 1) - (2/3) poissonMass (m + 1)] - [P(m) - (2/3) poissonMass m] ≤ (2/45) poissonMass m / m²`.

(The upper half of the estimate rests on the left side being nonnegative.)

*The monotone sequence.*  Let `S(m) = P(m) - (2/3) poissonMass m + poissonMass m/(15 m)`
(`ramanujanSeq m`).  By the step and `poissonMass (m + 1) ≤ poissonMass m`,

`S(m + 1) - S(m) ≤ poissonMass m · (2/(45 m²) + 1/(15 (m + 1)) - 1/(15 m))`
`= - poissonMass m · (m - 2)/(45 m² (m + 1)) ≤ 0`  for `m ≥ 2`.

*The limit.*  For `M ≥ m ≥ 2` therefore `S(m) ≥ S(M) ≥ 1/2 - (2/3) poissonMass M` by the median
bound, and `poissonMass M → 0` by Stirling's formula.  Hence `S(m) ≥ 1/2`, which is the lower half
of the estimate.

*The birthday law.*  Since `1 + sbirth m = P(m)/poissonMass m` (`sbirth_eq`), dividing
`S(m) ≥ 1/2` by `poissonMass m` gives `sbirth_ge`.
-/

namespace Parking

open Finset

open private psiF gF hasDerivAt_gF hasDerivAt_psiF poissonMass_eq_gF poissonMass_succ_eq_gF ppois
  sbirth_eq from Parking.NextColumn.Ramanujan

/-! ### The Poisson law as a function of its mean -/

/-- `g_m(x) = g_{m+1}(x) (m + 1)/x` for `x ≠ 0`. -/
private theorem gF_eq_succ (m : ℕ) {x : ℝ} (hx : x ≠ 0) :
    gF m x = gF (m + 1) x * ((m : ℝ) + 1) / x := by
  unfold gF
  rw [Nat.factorial_succ]
  push_cast
  field

/-- `Ψ_{m+1} = Ψ_m + g_{m+1}`. -/
private theorem psiF_succ (m : ℕ) (x : ℝ) :
    psiF (m + 1) x = psiF m x + gF (m + 1) x := by
  unfold psiF gF
  rw [sum_range_succ _ (m + 1)]
  ring

/-- `g_{m+1}' = g_m - g_{m+1}`: the derivative `hasDerivAt_gF`, written through `g_m`. -/
private theorem hasDerivAt_gF_succ (m : ℕ) (x : ℝ) :
    HasDerivAt (gF (m + 1)) (gF m x - gF (m + 1) x) x := by
  refine (hasDerivAt_gF m x).congr_deriv ?_
  unfold gF
  rw [Nat.factorial_succ]
  push_cast
  field

/-- If `f` has the derivative `f'` at every point from `a` on and `f' ≤ 0` between `a` and `b`,
then `f b ≤ f a`. -/
private theorem le_of_hasDerivAt_nonpos {f f' : ℝ → ℝ} {a b : ℝ} (hab : a ≤ b)
    (hf : ∀ x, a ≤ x → HasDerivAt f (f' x) x) (hf' : ∀ x, a < x → x < b → f' x ≤ 0) :
    f b ≤ f a :=
  antitoneOn_of_hasDerivWithinAt_nonpos (convex_Icc a b)
    (fun x hx => (hf x hx.1).continuousAt.continuousWithinAt)
    (fun x hx => (hf x (interior_subset hx).1).hasDerivWithinAt)
    (fun x hx => by rw [interior_Icc] at hx; exact hf' x hx.1 hx.2)
    (Set.left_mem_Icc.2 hab) (Set.right_mem_Icc.2 hab) hab

/-! ### The Poisson mass does not increase -/

/-- The Poisson mass `e^{-m} m^m/m!` does not increase with `m`:
`poissonMass (m + 1) ≤ poissonMass m`.  For `m ≥ 1` the quotient of the two masses is
`e^{-1} (1 + 1/m)^m`, which is at most `1`. -/
private theorem poissonMass_succ_le (m : ℕ) : poissonMass (m + 1) ≤ poissonMass m := by
  have h : Real.exp (-1) * ((m : ℝ) + 1) ^ m ≤ (m : ℝ) ^ m := by
    rcases Nat.eq_zero_or_pos m with rfl | hm
    · simp
    · have hm0 : (0 : ℝ) < m := by exact_mod_cast hm
      rw [show (m : ℝ) + 1 = m * (1 + (m : ℝ)⁻¹) by field, mul_pow]
      calc Real.exp (-1) * ((m : ℝ) ^ m * (1 + (m : ℝ)⁻¹) ^ m)
          ≤ Real.exp (-1) * ((m : ℝ) ^ m * Real.exp 1) := by
            gcongr
            exact Real.one_add_inv_pow_le_exp
        _ = (m : ℝ) ^ m := by
            rw [mul_left_comm, ← Real.exp_add]
            simp
  rw [poissonMass_succ_eq_gF, poissonMass_eq_gF, Nat.cast_add_one]
  unfold gF
  rw [neg_add, Real.exp_add, mul_assoc]
  gcongr

/-! ### The median -/

/-- `g_m(m - u) ≤ g_m(m + u)` for `0 ≤ u < m`: the `m`-th power of
`e^{2u/m} ≤ (m + u)/(m - u)`. -/
private theorem gF_reflect_le {m : ℕ} {u : ℝ} (hu0 : 0 ≤ u) (hum : u < m) :
    gF m (m - u) ≤ gF m (m + u) := by
  have hm : (0 : ℝ) < m := hu0.trans_lt hum
  have hmu : 0 < (m : ℝ) - u := sub_pos.2 hum
  have h1 : Real.exp (2 * u / m) ≤ ((m : ℝ) + u) / (m - u) := by
    have h := Real.le_log_one_add_of_nonneg (x := 2 * u / (m - u))
      (div_nonneg (by linarith) hmu.le)
    rw [show 2 * (2 * u / (m - u)) / (2 * u / (m - u) + 2) = 2 * u / m by field,
      show 1 + 2 * u / (m - u) = ((m : ℝ) + u) / (m - u) by field] at h
    exact (Real.le_log_iff_exp_le (div_pos (by linarith) hmu)).1 h
  have h2 : Real.exp (2 * u) * ((m : ℝ) - u) ^ m ≤ ((m : ℝ) + u) ^ m := by
    have h := pow_le_pow_left₀ (mul_nonneg (Real.exp_pos _).le hmu.le)
      ((le_div_iff₀ hmu).1 h1) m
    rwa [mul_pow, ← Real.exp_nat_mul, mul_div_cancel₀ _ hm.ne'] at h
  unfold gF
  rw [show -((m : ℝ) - u) = -(m + u) + 2 * u by ring, Real.exp_add, mul_assoc]
  gcongr

/-- The Poisson law of mean `m` puts mass at least `1/2` on `{0, …, m}`:
`1/2 ≤ e^{-m} ∑_{i ≤ m} m^i/i!`.  With `Ψ(x) = e^{-x} ∑_{i ≤ m} x^i/i!`, the function
`u ↦ Ψ(m + u) + Ψ(m - u)` does not increase on `[0, m]`, because its derivative is the difference
`e^{-(m-u)} (m-u)^m/m! - e^{-(m+u)} (m+u)^m/m! ≤ 0`; comparing `u = m` with `u = 0` gives
`1 = Ψ(0) ≤ Ψ(0) + Ψ(2m) ≤ 2 Ψ(m)`. -/
private theorem half_le_poisson_atMost_mean (m : ℕ) :
    1 / 2 ≤ Real.exp (-(m : ℝ)) * ∑ i ∈ range (m + 1), (m : ℝ) ^ i / (i.factorial : ℝ) := by
  have hd : ∀ u : ℝ, HasDerivAt (fun v : ℝ => psiF m (m + v) + psiF m (m - v))
      (-gF m (m + u) + gF m (m - u)) u := fun u =>
    (((hasDerivAt_psiF m (m + u)).comp_const_add (m : ℝ) u).fun_add
      ((hasDerivAt_psiF m (m - u)).comp_const_sub (m : ℝ) u)).congr_deriv (by ring)
  have h := le_of_hasDerivAt_nonpos (Nat.cast_nonneg m) (fun u _ => hd u) fun u h0 h1 => by
    linarith [gF_reflect_le h0.le h1]
  have h0 : psiF m 0 = 1 := by simp [psiF, sum_range_succ']
  have h2 : 0 ≤ psiF m (m + m) := by unfold psiF; positivity
  simp only [sub_self, add_zero, sub_zero, h0] at h
  change 1 / 2 ≤ psiF m m
  linarith

/-! ### One step of the sequence -/

/-- The inequality between exponents behind `gF_shift_ge` (there `u = s/M` and
`w = s²/(2(M + s))`): the right side minus the left side is
`s⁴ [(M - s)/(4 M³ (M + s)) + s (2M + s)/(8 M² (M + s)²)]`. -/
private theorem shift_exponent_le {M s : ℝ} (hM : 0 < M) (hs0 : 0 ≤ s) (hs1 : s ≤ M) :
    -((s ^ 3 / 6 + s ^ 4 / 8) / M ^ 2)
      ≤ -s + M * (s / M - (s / M) ^ 2 / 2 + (s / M) ^ 3 / 3 - (s / M) ^ 4 / 4)
          + (s ^ 2 / (2 * (M + s)) - (s ^ 2 / (2 * (M + s))) ^ 2 / 2) := by
  have hx : 0 < M + s := by linarith
  rw [← sub_nonneg]
  calc (0 : ℝ) ≤ s ^ 4 * ((M - s) / (4 * M ^ 3 * (M + s))
        + s * (2 * M + s) / (8 * M ^ 2 * (M + s) ^ 2)) :=
        mul_nonneg (pow_nonneg hs0 4)
          (add_nonneg (div_nonneg (sub_nonneg.2 hs1) (by positivity)) (by positivity))
    _ = _ := by field

/-- `g_m(m) (1 - (s³/6 + s⁴/8)/m²) ≤ g_m(m + s) (1 + s²/(2(m + s)))` for `m ≥ 1`, `0 ≤ s ≤ m`.
Since `g_m(m + s) = g_m(m) e^{-s} (1 + s/m)^m`, this follows from the Taylor bounds of the
logarithm of orders four and two, from `1 - y ≤ e^{-y}` and from `shift_exponent_le`. -/
private theorem gF_shift_ge {m : ℕ} (hm : 1 ≤ m) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ m) :
    gF m m * (1 - (s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2)
      ≤ gF m (m + s) * (1 + s ^ 2 / (2 * (m + s))) := by
  have hM : (0 : ℝ) < m := by exact_mod_cast hm
  have hu : 0 ≤ s / m := div_nonneg hs0 hM.le
  have hw : 0 ≤ s ^ 2 / (2 * (m + s)) := by positivity
  have h1 : Real.exp (m * (s / m - (s / m) ^ 2 / 2 + (s / m) ^ 3 / 3 - (s / m) ^ 4 / 4))
      ≤ (1 + s / m) ^ m := by
    rw [Real.exp_nat_mul]
    exact pow_le_pow_left₀ (Real.exp_pos _).le
      ((Real.le_log_iff_exp_le (by linarith)).1 (log_one_add_ge4 hu)) m
  have h2 : Real.exp (s ^ 2 / (2 * (m + s)) - (s ^ 2 / (2 * (m + s))) ^ 2 / 2)
      ≤ 1 + s ^ 2 / (2 * (m + s)) :=
    (Real.le_log_iff_exp_le (by linarith)).1 (log_one_add_ge2 hw)
  have h3 : 1 - (s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2
      ≤ Real.exp (-s) * (1 + s / m) ^ m * (1 + s ^ 2 / (2 * (m + s))) :=
    calc 1 - (s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2
        ≤ Real.exp (-((s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2)) := by
          linarith [Real.add_one_le_exp (-((s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2))]
      _ ≤ Real.exp (-s + m * (s / m - (s / m) ^ 2 / 2 + (s / m) ^ 3 / 3 - (s / m) ^ 4 / 4)
            + (s ^ 2 / (2 * (m + s)) - (s ^ 2 / (2 * (m + s))) ^ 2 / 2)) :=
          Real.exp_le_exp.2 (shift_exponent_le hM hs0 hs1)
      _ ≤ Real.exp (-s) * (1 + s / m) ^ m * (1 + s ^ 2 / (2 * (m + s))) := by
          rw [Real.exp_add, Real.exp_add]
          gcongr
  have h4 : gF m (m + s) = gF m m * (Real.exp (-s) * (1 + s / m) ^ m) := by
    unfold gF
    rw [neg_add, Real.exp_add, show (m : ℝ) + s = m * (1 + s / m) by field, mul_pow]
    ring
  rw [h4, mul_assoc]
  exact mul_le_mul_of_nonneg_left h3 (by unfold gF; positivity)

/-- `G(s) = Ψ_m(m + s) + s ((2/3) g_m(m) + (1/3) g_m(m + s)) - (g_m(m)/m²) (s⁴/36 + s⁵/60)`.
Since `Ψ_m(m + s) = Ψ_m(m) - ∫_m^{m+s} g_m`, the first two terms are `Ψ_m(m)` plus the excess of
the two-point rule `s ((2/3) g_m(m) + (1/3) g_m(m + s))` over the integral of `g_m` on
`[m, m + s]`; the last term is the bound for that excess.  (Without the last term this is the
private `HF` of `Parking.NextColumn.Ramanujan`, as a function of `s = x - m`.) -/
private noncomputable def twoPointGap (m : ℕ) (s : ℝ) : ℝ :=
  psiF m (m + s) + s * (2 / 3 * gF m m + 1 / 3 * gF m (m + s))
    - gF m m / (m : ℝ) ^ 2 * (s ^ 4 / 36 + s ^ 5 / 60)

/-- `G'(s) = (2/3) [g_m(m) (1 - (s³/6 + s⁴/8)/m²) - g_m(m + s) (1 + s²/(2(m + s)))]` for `m ≥ 1`
and `s ≥ 0`. -/
private theorem hasDerivAt_twoPointGap {m : ℕ} (hm : 1 ≤ m) {s : ℝ} (hs : 0 ≤ s) :
    HasDerivAt (twoPointGap m)
      (2 / 3 * (gF m m * (1 - (s ^ 3 / 6 + s ^ 4 / 8) / (m : ℝ) ^ 2)
        - gF m (m + s) * (1 + s ^ 2 / (2 * (m + s))))) s := by
  obtain ⟨k, rfl⟩ : ∃ k, m = k + 1 := ⟨m - 1, by omega⟩
  have hx : ((k + 1 : ℕ) : ℝ) + s ≠ 0 := by positivity
  have h1 := (hasDerivAt_psiF (k + 1) (((k + 1 : ℕ) : ℝ) + s)).comp_const_add _ s
  have h2 := (hasDerivAt_gF_succ k (((k + 1 : ℕ) : ℝ) + s)).comp_const_add _ s
  have h3 := (hasDerivAt_id' s).fun_mul
    ((h2.const_mul (1 / 3)).const_add (2 / 3 * gF (k + 1) (k + 1 : ℕ)))
  have h4 := (((hasDerivAt_pow 4 s).div_const 36).fun_add
    ((hasDerivAt_pow 5 s).div_const 60)).const_mul
      (gF (k + 1) (k + 1 : ℕ) / ((k + 1 : ℕ) : ℝ) ^ 2)
  refine ((h1.fun_add h3).fun_sub h4).congr_deriv ?_
  rw [gF_eq_succ k hx]
  push_cast at hx ⊢
  field

/-- The sequence `P(m) - (2/3) poissonMass m` increases by at most `(2/45) poissonMass m / m²`
from `m ≥ 1` to `m + 1`: this is `G(1) ≤ G(0)`, and `G' ≤ 0` on `[0, 1]` by
`gF_shift_ge`. -/
private theorem psiF_sub_mass_step {m : ℕ} (hm : 1 ≤ m) :
    psiF (m + 1) (m + 1 : ℕ) - 2 / 3 * poissonMass (m + 1)
      ≤ psiF m m - 2 / 3 * poissonMass m + 2 / 45 * (poissonMass m / (m : ℝ) ^ 2) := by
  have hm1 : (1 : ℝ) ≤ m := by exact_mod_cast hm
  have h := le_of_hasDerivAt_nonpos zero_le_one (fun s hs => hasDerivAt_twoPointGap hm hs)
    fun s h0 h1 => by linarith [gF_shift_ge hm h0.le (by linarith : s ≤ m)]
  have e := poissonMass_succ_eq_gF m
  rw [Nat.cast_add_one] at e
  unfold twoPointGap at h
  rw [add_zero, ← poissonMass_eq_gF, ← e] at h
  rw [psiF_succ, ← poissonMass_eq_gF, Nat.cast_succ]
  linarith

/-! ### The monotone sequence and its limit -/

/-- `S(m) = P(m) - (2/3) poissonMass m + poissonMass m/(15 m)`. -/
private noncomputable def ramanujanSeq (m : ℕ) : ℝ :=
  psiF m m - 2 / 3 * poissonMass m + poissonMass m / (15 * (m : ℝ))

/-- `S(m + 1) ≤ S(m)` for `m ≥ 2`. -/
private theorem ramanujanSeq_succ_le {m : ℕ} (hm : 2 ≤ m) :
    ramanujanSeq (m + 1) ≤ ramanujanSeq m := by
  have hm2 : (2 : ℝ) ≤ m := by exact_mod_cast hm
  have h1 : poissonMass (m + 1) / (15 * ((m + 1 : ℕ) : ℝ))
      ≤ poissonMass m / (15 * ((m + 1 : ℕ) : ℝ)) :=
    div_le_div_of_nonneg_right (poissonMass_succ_le m) (by positivity)
  have h2 : 2 / 45 * (poissonMass m / (m : ℝ) ^ 2) + poissonMass m / (15 * ((m + 1 : ℕ) : ℝ))
      ≤ poissonMass m / (15 * (m : ℝ)) := by
    rw [← sub_nonneg]
    calc (0 : ℝ) ≤ poissonMass m * ((m : ℝ) - 2) / (45 * (m : ℝ) ^ 2 * ((m : ℝ) + 1)) :=
          div_nonneg (mul_nonneg (poissonMass_pos m).le (sub_nonneg.2 hm2)) (by positivity)
      _ = _ := by push_cast; field
  unfold ramanujanSeq
  linarith [psiF_sub_mass_step (m := m) (by omega)]

/-- `poissonMass M → 0`, by the Stirling bound `poissonMass M ≤ c₀/√M`. -/
private theorem tendsto_poissonMass : Filter.Tendsto poissonMass Filter.atTop (nhds 0) :=
  squeeze_zero' (Filter.Eventually.of_forall fun n => (poissonMass_pos n).le)
    ((Filter.eventually_ge_atTop 1).mono fun _ hn => poissonMass_le_c0 hn)
    (tendsto_const_nhds.div_atTop (Real.tendsto_sqrt_atTop.comp tendsto_natCast_atTop_atTop))

/-- The lower half of Ramanujan's estimate: `1/2 ≤ S(m)`, that is,
`1/2 + (2/3 - 1/(15 m)) poissonMass m ≤ P(m)`, for `m ≥ 2`. -/
private theorem half_le_ramanujanSeq {m : ℕ} (hm : 2 ≤ m) : 1 / 2 ≤ ramanujanSeq m := by
  have hmono : ∀ M, m ≤ M → ramanujanSeq M ≤ ramanujanSeq m := fun M hM => by
    induction M, hM using Nat.le_induction with
    | base => exact le_rfl
    | succ k hk ih => exact (ramanujanSeq_succ_le (hm.trans hk)).trans ih
  have hlim : Filter.Tendsto (fun M => 1 / 2 - 2 / 3 * poissonMass M) Filter.atTop
      (nhds (1 / 2)) := by
    have h := (tendsto_poissonMass.const_mul (2 / 3)).const_sub (1 / 2)
    rwa [mul_zero, sub_zero] at h
  refine le_of_tendsto hlim ((Filter.eventually_ge_atTop m).mono fun M hM =>
    le_trans ?_ (hmono M hM))
  have h1 := half_le_poisson_atMost_mean M
  have h2 : 0 ≤ poissonMass M / (15 * (M : ℝ)) :=
    div_nonneg (poissonMass_pos M).le (by positivity)
  unfold ramanujanSeq psiF
  linarith

/-! ### The mean of the birthday law -/

/-- **Lower bound for the mean of the birthday law**:
`1/(2 poissonMass m) - 1/3 - 1/(15 m) ≤ s_m` for `m ≥ 2`, where
`poissonMass m = e^{-m} m^m/m!`.  Since `s_m = P(m)/poissonMass m - 1` with
`P(m) = e^{-m} ∑_{i ≤ m} m^i/i!`, this is the lower half of Ramanujan's estimate,
`1/2 + (2/3 - 1/(15 m)) poissonMass m ≤ P(m)`.  That estimate holds because the sequence
`P(m) - (2/3) poissonMass m + poissonMass m/(15 m)` does not increase from `m = 2` on and is at
least `1/2 - (2/3) poissonMass M` at every `M`, where `poissonMass M → 0`. -/
theorem sbirth_ge {m : ℕ} (hm : 2 ≤ m) :
    1 / (2 * poissonMass m) - 1 / 3 - 1 / (15 * (m : ℝ)) ≤ sbirth m := by
  have hR := poissonMass_pos m
  have hm0 : (0 : ℝ) < m := by exact_mod_cast (by omega : 0 < m)
  have h := half_le_ramanujanSeq hm
  unfold ramanujanSeq at h
  have hp : ppois m = psiF m m := rfl
  rw [sbirth_eq (by omega : 1 ≤ m), hp]
  calc 1 / (2 * poissonMass m) - 1 / 3 - 1 / (15 * (m : ℝ))
      = (1 / 2 + 2 / 3 * poissonMass m - poissonMass m / (15 * (m : ℝ))) / poissonMass m - 1 := by
        field
    _ ≤ psiF m m / poissonMass m - 1 := by
        gcongr
        linarith

end Parking
