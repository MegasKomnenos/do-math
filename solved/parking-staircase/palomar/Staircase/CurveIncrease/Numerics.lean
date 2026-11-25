module

public import Parking.Cayley.Stirling
public import Parking.Basic.RealBounds
public import Mathlib.Analysis.Real.Pi.Bounds

/-!
# The curve increase: inequalities between real numbers

Everything in this module is a statement about real numbers; no parking function occurs.  It holds
the numerical constants, the polynomial certificates and the algebra of the explicit estimates, in
the form in which `Staircase.CurveIncrease.Ledger` and `Staircase.CurveIncrease.Main` use them.

Notation: `s = √R ≥ 6.48` (`R ≥ 42`); `c₀ = 1/√(2π)`, which enters the statements as a number
`a ≤ 0.39894229`; `W₀ = s²/2 - 1.06385 s + 0.7184`,
`A₀ = 0.478731 s⁵ - 0.974453 s⁴ + 0.642741 s³` and `G₀ = 2A₀/s²`.

* For `Ledger`: `rho_bound`, `term_G` and `term_A` bound one term of the sums, and `Wsum_numeric`,
  `Asum_numeric`, `Gsum_numeric` turn the bounds of the power sums into `W_Σ ≥ W₀`, `𝒜 ≤ A₀` and
  `G ≤ G₀`.
* For `Main`: `k_window` and `K_facts` place the column and the threshold, `pair_numeric` bounds
  the pair side from below, and `impulse_numeric` shows that the bound of the impulse side lies
  strictly below it.

Each polynomial certificate (`cert_*`) stands directly before the statement that uses it, and all
are proved in the same way: after the substitution `s = 6.48 + t` (`exists_shift`) the polynomial
has nonnegative coefficients in `t`, so its Horner form is positive by `positivity`, and `ring`
checks that the Horner form is the polynomial.
-/

@[expose] public section

namespace Parking

/-! ### Constants -/

/-- `c₀ = 1/√(2π) ≤ 0.39894229`. -/
theorem c0_le : c0 ≤ 0.39894229 := by
  have hpi1 := Real.pi_gt_d20
  have h2pi : (0 : ℝ) < 2 * Real.pi := by linarith
  have hs : 0 < Real.sqrt (2 * Real.pi) := Real.sqrt_pos.mpr h2pi
  have hlo : (1 / 0.39894229 : ℝ) ≤ Real.sqrt (2 * Real.pi) := by
    apply Real.le_sqrt_of_sq_le
    have h : ((1 / 0.39894229 : ℝ)) ^ 2 ≤ 2 * 3.14159265358979323846 := by norm_num
    linarith
  unfold c0
  rw [div_le_iff₀ hs]
  have h := mul_le_mul_of_nonneg_left hlo (by norm_num : (0 : ℝ) ≤ 0.39894229)
  have e : (0.39894229 : ℝ) * (1 / 0.39894229) = 1 := by norm_num
  linarith

/-- On `[0, 1]` the exponential is at most its Taylor polynomial of degree 11 plus the remainder
term `13 x¹²/(12 · 12!)`. -/
private theorem exp_upper12_aux {x : ℝ} (h0 : 0 ≤ x) (h1 : x ≤ 1) :
    Real.exp x ≤ 1 + x + x ^ 2 / 2 + x ^ 3 / 6 + x ^ 4 / 24 + x ^ 5 / 120 + x ^ 6 / 720
        + x ^ 7 / 5040 + x ^ 8 / 40320 + x ^ 9 / 362880 + x ^ 10 / 3628800 + x ^ 11 / 39916800
        + x ^ 12 * 13 / (479001600 * 12) := by
  have h := Real.exp_bound' h0 h1 (n := 12) (by norm_num)
  norm_num [Finset.sum_range_succ, Nat.factorial] at h
  linarith

/-- For `x ≥ 0` the exponential is at least its Taylor polynomial of degree 7. -/
private theorem exp_lower8_aux {x : ℝ} (h0 : 0 ≤ x) :
    1 + x + x ^ 2 / 2 + x ^ 3 / 6 + x ^ 4 / 24 + x ^ 5 / 120 + x ^ 6 / 720 + x ^ 7 / 5040
        ≤ Real.exp x := by
  have h := Real.sum_le_exp_of_nonneg h0 8
  norm_num [Finset.sum_range_succ, Nat.factorial] at h
  linarith

/-- `0.704688 ≤ e^{-0.35} ≤ 0.704689`. -/
theorem exp_neg_035_bounds {c : ℝ} (hc : c = 0.35) :
    (0.704688 : ℝ) ≤ Real.exp (-c) ∧ Real.exp (-c) ≤ 0.704689 := by
  have h0 : 0 ≤ c := by rw [hc]; norm_num
  have h1 : c ≤ 1 := by rw [hc]; norm_num
  have hU : Real.exp c ≤ 1.4190676 := (exp_upper12_aux h0 h1).trans (by rw [hc]; norm_num)
  have hL : (1.4190675 : ℝ) ≤ Real.exp c := le_trans (by rw [hc]; norm_num) (exp_lower8_aux h0)
  have hm : Real.exp (-c) * Real.exp c = 1 := by rw [← Real.exp_add]; simp
  have hp : 0 < Real.exp (-c) := Real.exp_pos _
  constructor
  · nlinarith [mul_le_mul_of_nonneg_left hU hp.le]
  · nlinarith [mul_le_mul_of_nonneg_left hL hp.le]

/-- `0.38385 ≤ e^{-0.9575}`. -/
private theorem exp_neg_09575 {c : ℝ} (hc : c = 0.9575) : (0.38385 : ℝ) ≤ Real.exp (-c) := by
  have h0 : 0 ≤ c := by rw [hc]; norm_num
  have h1 : c ≤ 1 := by rw [hc]; norm_num
  have hU : Real.exp c ≤ 2.60518 := (exp_upper12_aux h0 h1).trans (by rw [hc]; norm_num)
  have hm : Real.exp (-c) * Real.exp c = 1 := by rw [← Real.exp_add]; simp
  have hp : 0 < Real.exp (-c) := Real.exp_pos _
  nlinarith [mul_le_mul_of_nonneg_left hU hp.le]

/-! ### Square roots, the window of `k` and the threshold -/

/-- `√R ≥ 6.48` for `R ≥ 42`. -/
theorem sqrt_ge_648 {R : ℕ} (hR : 42 ≤ R) : (6.48 : ℝ) ≤ Real.sqrt (R : ℝ) := by
  rw [Real.le_sqrt' (by norm_num)]
  have h : (42 : ℝ) ≤ R := by exact_mod_cast hR
  have h2 : (6.48 : ℝ) ^ 2 ≤ 42 := by norm_num
  linarith

/-- For `s > 0`, `R = s² ≥ 42` and `k ≥ 0`, the window `(R-2)³ ≤ k² ≤ (R-1)³` gives
`k ≤ s³ ≤ 1.07593 k`. -/
theorem k_window {s kk Rr : ℝ} (hs0 : 0 < s) (hRr : Rr = s ^ 2) (hR42 : 42 ≤ Rr) (hk0 : 0 ≤ kk)
    (h1 : (Rr - 2) ^ 3 ≤ kk ^ 2) (h2 : kk ^ 2 ≤ (Rr - 1) ^ 3) :
    kk ≤ s ^ 3 ∧ s ^ 3 ≤ 1.07593 * kk := by
  subst hRr
  have hs3 : 0 < s ^ 3 := by positivity
  have hb : (s ^ 2) ^ 3 = (s ^ 3) ^ 2 := by ring
  constructor
  · have ha : (s ^ 2 - 1) ^ 3 ≤ (s ^ 2) ^ 3 := pow_le_pow_left₀ (by linarith) (by linarith) 3
    by_contra hcon
    have hcon' : s ^ 3 < kk := not_le.mp hcon
    have h3 : 0 < (kk - s ^ 3) * (kk + s ^ 3) := mul_pos (by linarith) (by linarith)
    nlinarith only [h3, ha, hb, h2]
  · have hd : s ^ 2 ≤ 21 / 20 * (s ^ 2 - 2) := by linarith
    have he : (s ^ 2) ^ 3 ≤ (21 / 20 * (s ^ 2 - 2)) ^ 3 := pow_le_pow_left₀ (by positivity) hd 3
    have hf : (21 / 20 * (s ^ 2 - 2)) ^ 3 = (21 / 20) ^ 3 * (s ^ 2 - 2) ^ 3 := by ring
    have hg : (s ^ 3) ^ 2 ≤ (1.07593 * kk) ^ 2 := by
      have i1 : (21 / 20 : ℝ) ^ 3 * (s ^ 2 - 2) ^ 3 ≤ (21 / 20) ^ 3 * kk ^ 2 :=
        mul_le_mul_of_nonneg_left h1 (by norm_num)
      have i2 : ((21 : ℝ) / 20) ^ 3 * kk ^ 2 ≤ (1.07593 * kk) ^ 2 := by
        have e : ((1.07593 : ℝ) * kk) ^ 2 = 1.07593 ^ 2 * kk ^ 2 := by ring
        rw [e]
        exact mul_le_mul_of_nonneg_right (by norm_num) (sq_nonneg kk)
      linarith
    by_contra hcon
    have hcon' : 1.07593 * kk < s ^ 3 := not_le.mp hcon
    have h3 : 0 < (s ^ 3 - 1.07593 * kk) * (s ^ 3 + 1.07593 * kk) :=
      mul_pos (by linarith) (by positivity)
    nlinarith only [h3, hg]

/-- The threshold `K = (R-1)(2R-1)/(2s)` is positive. -/
private theorem K_pos {s K : ℝ} (hs : 6.48 ≤ s)
    (hK : K * (2 * s) = (s ^ 2 - 1) * (2 * s ^ 2 - 1)) : 0 < K := by
  have hs2 : (41.99 : ℝ) ≤ s ^ 2 := by nlinarith only [hs]
  have h : 0 < K * (2 * s) := by
    rw [hK]; exact mul_pos (by linarith only [hs2]) (by linarith only [hs2])
  exact pos_of_mul_pos_left h (by linarith only [hs])

/-- The threshold `K = (R-1)(2R-1)/(2s)`, for `R = s²` and `s ≥ 6.48`: it is at least `R`, by a
polynomial inequality in `s`, and at least `k` when `k² ≤ (R-1)³`, because `K² ≥ (R-1)³`. -/
theorem K_facts {s Rr K kk : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2)
    (hK : K * (2 * s) = (Rr - 1) * (2 * Rr - 1)) (h2 : kk ^ 2 ≤ (Rr - 1) ^ 3) :
    Rr ≤ K ∧ kk ≤ K := by
  subst hRr
  have hs0 : 0 < s := by linarith
  have hs2 : (41.99 : ℝ) ≤ s ^ 2 := by nlinarith
  have hK0 : 0 < K := K_pos hs hK
  refine ⟨?_, ?_⟩
  · have h : s ^ 2 * (2 * s) ≤ K * (2 * s) := by
      rw [hK]
      nlinarith [mul_nonneg (sq_nonneg s) (by nlinarith : (0 : ℝ) ≤ 2 * s ^ 2 - 2 * s - 3)]
    exact le_of_mul_le_mul_right h (by linarith)
  · have h3 : (s ^ 2 - 1) ^ 3 * (2 * s) ^ 2 ≤ (K * (2 * s)) ^ 2 := by
      rw [hK]
      nlinarith [sq_nonneg (s ^ 2 - 1)]
    by_contra hcon
    have hcon' : K < kk := not_le.mp hcon
    have h4 : 0 < (kk - K) * (kk + K) := mul_pos (by linarith) (by linarith)
    have h5 : K ^ 2 * (2 * s) ^ 2 < (s ^ 2 - 1) ^ 3 * (2 * s) ^ 2 :=
      mul_lt_mul_of_pos_right (by nlinarith only [h4, h2]) (by positivity)
    nlinarith only [h3, h5]

/-! ### The shift behind the polynomial certificates -/

/-- A number `s ≥ 6.48` is `6.48 + t` with `t ≥ 0`.  The polynomial certificates of this module are
polynomials in `t` with nonnegative coefficients. -/
private theorem exists_shift {s : ℝ} (hs : 6.48 ≤ s) : ∃ t : ℝ, 0 ≤ t ∧ s = 162 / 25 + t :=
  ⟨s - 162 / 25, by linarith [show (6.48 : ℝ) = 162 / 25 by norm_num], by ring⟩

/-! ### One term of the sums (`B = b`, `p = √b`) -/

/-- For `s ≥ 6.48`, `s³ ≤ 1.07593 · k`, `0 ≤ c ≤ s²` and `d ≥ k`:
`c/(2d) + c²/(8d²) ≤ 0.560302 · c/s³`. -/
theorem rho_bound {s kk c d : ℝ} (hs : 6.48 ≤ s) (hk : s ^ 3 ≤ 1.07593 * kk) (hc0 : 0 ≤ c)
    (hc : c ≤ s ^ 2) (hd : kk ≤ d) :
    c / (2 * d) + c ^ 2 / (8 * d ^ 2) ≤ 0.560302 * c / s ^ 3 := by
  have hs0 : 0 < s := by linarith
  have hs3 : 0 < s ^ 3 := by positivity
  have hkk : 0 < kk := by linarith
  have hd0 : 0 < d := by linarith
  have hd' : d ≠ 0 := hd0.ne'
  obtain ⟨v, hv⟩ : ∃ v : ℝ, v = 1 / d := ⟨_, rfl⟩
  have hv0 : 0 ≤ v := by rw [hv]; positivity
  have hvd : v * d = 1 := by rw [hv]; field
  have hvs : v * s ^ 3 ≤ 1.07593 := by
    nlinarith [mul_le_mul_of_nonneg_left hk hv0, mul_le_mul_of_nonneg_left hd hv0]
  have e1 : c / (2 * d) + c ^ 2 / (8 * d ^ 2) = c * v / 2 + (c * v) ^ 2 / 8 := by
    rw [hv]; field
  rw [e1, le_div_iff₀ hs3]
  have hcv : 0 ≤ c * v := mul_nonneg hc0 hv0
  have h1 : c * (v * s ^ 3) ≤ c * 1.07593 := mul_le_mul_of_nonneg_left hvs hc0
  have h2 : c * (v * s) ≤ s ^ 2 * (v * s) := mul_le_mul_of_nonneg_right hc (mul_nonneg hv0 hs0.le)
  have h3 : c * v * 6.48 ≤ 1.07593 := by
    nlinarith [mul_nonneg hcv (sub_nonneg.2 hs)]
  have h4 : c * v * c * (v * s ^ 3) ≤ c * v * c * 1.07593 :=
    mul_le_mul_of_nonneg_left hvs (mul_nonneg hcv hc0)
  have h5 : 1.07593 * c * (c * v * 6.48) ≤ 1.07593 * c * 1.07593 :=
    mul_le_mul_of_nonneg_left h3 (by positivity)
  nlinarith [h1, h4, h5]

/-- One term of the sum `G`, with `B = b` and `p = √b`: if `r ≤ a/p` and
`κ ≥ 1/2 - (4/3) a/p - (a/15)/(Bp)`, then
`3 (B-1) r - (5/2) κ ≤ a (3p + 1/(3p) + 1/(6Bp)) - 5/4`. -/
theorem term_G {a p B r κ : ℝ} (hp : 0 < p) (hB : B = p ^ 2) (hB1 : 1 ≤ B)
    (hr : r ≤ a / p)
    (hκ : 1 / 2 - 4 / 3 * a * (1 / p) - a / 15 * (1 / (B * p)) ≤ κ) :
    3 * (B - 1) * r - 5 / 2 * κ
      ≤ a * (3 * p + 1 / 3 * (1 / p) + 1 / 6 * (1 / (B * p))) - 5 / 4 := by
  subst hB
  have hp' : p ≠ 0 := hp.ne'
  obtain ⟨u, hu⟩ : ∃ u : ℝ, u = 1 / p := ⟨_, rfl⟩
  have hup : u * p = 1 := by rw [hu]; field
  have e1 : a / p = a * u := by rw [hu]; ring
  have e3 : 1 / (p ^ 2 * p) = u ^ 3 := by rw [hu]; field
  rw [e1] at hr
  rw [e3, ← hu] at hκ ⊢
  have h1 : 3 * (p ^ 2 - 1) * r ≤ 3 * (p ^ 2 - 1) * (a * u) :=
    mul_le_mul_of_nonneg_left hr (by linarith)
  have e2 : 3 * (p ^ 2 - 1) * (a * u) = 3 * a * (p - u) := by
    linear_combination (3 * a * p) * hup
  linarith

/-- One term of the sum `𝒜`, with `B = b ≤ R` and `p = √b`: under the same two hypotheses,
`(3R-2B)(B-1) r - (5R/2 - B) κ`
`  ≤ a (-2Bp + (3R + 2/3) p + (R/3 - 1/15)/p + (R/6)/(Bp)) - (5R/2 - B)/2`. -/
theorem term_A {a p B Rr r κ : ℝ} (hp : 0 < p) (hB : B = p ^ 2) (hB1 : 1 ≤ B) (hBR : B ≤ Rr)
    (hr : r ≤ a / p)
    (hκ : 1 / 2 - 4 / 3 * a * (1 / p) - a / 15 * (1 / (B * p)) ≤ κ) :
    (3 * Rr - 2 * B) * (B - 1) * r - (5 / 2 * Rr - B) * κ
      ≤ a * (-2 * (B * p) + (3 * Rr + 2 / 3) * p + (Rr / 3 - 1 / 15) * (1 / p)
            + Rr / 6 * (1 / (B * p)))
        - (5 / 2 * Rr - B) / 2 := by
  subst hB
  have hp' : p ≠ 0 := hp.ne'
  obtain ⟨u, hu⟩ : ∃ u : ℝ, u = 1 / p := ⟨_, rfl⟩
  have hup : u * p = 1 := by rw [hu]; field
  have e1 : a / p = a * u := by rw [hu]; ring
  have e3 : 1 / (p ^ 2 * p) = u ^ 3 := by rw [hu]; field
  rw [e1] at hr
  rw [e3, ← hu] at hκ ⊢
  have h1 : (3 * Rr - 2 * p ^ 2) * (p ^ 2 - 1) * r
      ≤ (3 * Rr - 2 * p ^ 2) * (p ^ 2 - 1) * (a * u) :=
    mul_le_mul_of_nonneg_left hr (mul_nonneg (by linarith) (by linarith))
  have h2 : (5 / 2 * Rr - p ^ 2) * (1 / 2 - 4 / 3 * a * u - a / 15 * u ^ 3)
      ≤ (5 / 2 * Rr - p ^ 2) * κ :=
    mul_le_mul_of_nonneg_left hκ (by linarith)
  have e2 : (3 * Rr - 2 * p ^ 2) * (p ^ 2 - 1) * (a * u)
        + (5 / 2 * Rr - p ^ 2) * (4 / 3 * a * u + a / 15 * u ^ 3)
      = a * (-2 * (p ^ 2 * p) + (3 * Rr + 2 / 3) * p + (Rr / 3 - 1 / 15) * u + Rr / 6 * u ^ 3) := by
    linear_combination (3*Rr*a*p - 2*a*p ^ 3 - a*p*u ^ 2/15 + 2*a*p/3 - a*u/15) * hup
  linarith

/-! ### The sums `W_Σ`, `𝒜`, `G`: the inequalities behind `Wsum_ge`, `Asum_le`, `Gsum_le` -/

/-- **The sum `W_Σ`.** If `S₁ ≤ 2s + 1/(2s) - 2.44948` and `S₂ ≤ 1.63300` (in `Ledger` these are
the sums of `b^{-1/2}` and of `b^{-3/2}` over `2 ≤ b ≤ R`), then
`(R-1)/2 - (4/3) a S₁ - (a/15) S₂ ≥ s²/2 - 1.06385 s + 0.7184`. -/
theorem Wsum_numeric {s a Rr S1 S2 : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2) (ha0 : 0 ≤ a)
    (ha : a ≤ 0.39894229)
    (h1 : S1 ≤ 2 * s + 1 / (2 * s) - 2.44948) (h2 : S2 ≤ 1.63300) :
    Rr / 2 - 1.06385 * s + 0.7184 ≤ (Rr - 1) / 2 - 4 / 3 * a * S1 - a / 15 * S2 := by
  subst hRr
  have hs0 : 0 < s := by linarith
  have hs' : s ≠ 0 := hs0.ne'
  obtain ⟨q, hq⟩ : ∃ q : ℝ, q = 1 / (2 * s) := ⟨_, rfl⟩
  have hq1 : q * (2 * s) = 1 := by rw [hq]; field
  have hq0 : 0 < q := by rw [hq]; positivity
  have hqle : q ≤ 25 / 324 := by nlinarith [mul_nonneg hq0.le (sub_nonneg.2 hs)]
  rw [← hq] at h1
  have hA1 : a * S1 ≤ a * (2 * s + q - 2.44948) := mul_le_mul_of_nonneg_left h1 ha0
  have hA2 : a * S2 ≤ a * 1.63300 := mul_le_mul_of_nonneg_left h2 ha0
  have hP : (0 : ℝ) ≤ 2 * s + q - 2.44948 := by linarith
  have hA3 : a * (2 * s + q - 2.44948) ≤ 0.39894229 * (2 * s + q - 2.44948) :=
    mul_le_mul_of_nonneg_right ha hP
  linarith

/-- The bracket of `Asum_bracket`, a polynomial in `s`, is nonnegative. -/
private theorem cert_Asum_bracket {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ (-2 * (2 / 5 * s ^ 5 + 1 / 2 * s ^ 3 - 0.84853) + (3 * s ^ 2 + 2 / 3) * (2 / 3 * s ^ 3
        + 1 / 2 * s - 1.17851) + (s ^ 2 / 3 - 1 / 15) * (2 * s - 2.44948) + s ^ 2 / 6 * 1.63300
        + s / 6) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 8192056522379 / 585937500 + t * (100590070099 / 9375000
      + t * (4938620471 / 1500000 + t * (5686829 / 11250 + t * (972 / 25 + t * (6 / 5))))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- The bracket of the bound of `𝒜`, with the four power sums `S₁`, …, `S₄` replaced by their
bounds. -/
private theorem Asum_bracket {s q S1 S2 S3 S4 : ℝ} (hs : 6.48 ≤ s) (hq1 : q * (2 * s) = 1)
    (hq0 : 0 < q)
    (h1 : S1 ≤ 2 * s + q - 2.44948) (h2 : S2 ≤ 1.63300)
    (h3 : S3 ≤ 2 / 3 * (s ^ 2 * s) + 1 / 2 * s - 1.17851)
    (h4 : 2 / 5 * ((s ^ 2) ^ 2 * s) + 1 / 2 * (s ^ 2 * s) - 0.84853 ≤ S4) :
    -2 * S4 + (3 * s ^ 2 + 2 / 3) * S3 + (s ^ 2 / 3 - 1 / 15) * S1 + s ^ 2 / 6 * S2
      ≤ (-2 * (2 / 5 * s ^ 5 + 1 / 2 * s ^ 3 - 0.84853) + (3 * s ^ 2 + 2 / 3) * (2 / 3 * s ^ 3
          + 1 / 2 * s - 1.17851) + (s ^ 2 / 3 - 1 / 15) * (2 * s - 2.44948) + s ^ 2 / 6 * 1.63300
          + s / 6) := by
  have hs2 : (41.99 : ℝ) ≤ s ^ 2 := by nlinarith only [hs]
  have hq2 : s ^ 2 * q = s / 2 := by linear_combination (s / 2) * hq1
  have i3 := mul_le_mul_of_nonneg_left h3 (by positivity : (0 : ℝ) ≤ 3 * s ^ 2 + 2 / 3)
  have i1 := mul_le_mul_of_nonneg_left h1 (by linarith only [hs2] : (0 : ℝ) ≤ s ^ 2 / 3 - 1 / 15)
  have i2 := mul_le_mul_of_nonneg_left h2 (by positivity : (0 : ℝ) ≤ s ^ 2 / 6)
  linarith only [i1, i2, i3, h4, hq2, hq0]

/-- `(s²+1)³(2s²+1) ≤ 2s⁸ + 7.22 s⁶`, in the form `0 ≤ 0.22 s⁶ - 9s⁴ - 5s² - 1`. -/
private theorem cert_Asum_correction {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ 0.22 * s ^ 6 - 9 * s ^ 4 - 5 * s ^ 2 - 1 := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 1272525763187 / 6103515625 + t * (1274739514956 / 244140625
      + t * (6925893719 / 1953125 + t * (75308616 / 78125 + t * (404901 / 3125 + t * (5346 / 625
      + t * (11 / 50)))))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- The correction term of the bound of `𝒜`: if `S_T ≤ (4/35) (s²+1)³ √(s²+1)`, then
`a · 0.560302/s³ · S_T ≤ 0.39894229 · 0.560302 · (4/35) (s⁴ + 3.61 s²)`. -/
private theorem Asum_correction {s q a ST : ℝ} (hs : 6.48 ≤ s) (hq1 : q * (2 * s) = 1) (hq0 : 0 < q)
    (ha0 : 0 ≤ a) (ha : a ≤ 0.39894229)
    (hT : ST ≤ 4 / 35 * ((s ^ 2 + 1) ^ 3 * Real.sqrt (s ^ 2 + 1))) :
    a * 0.560302 / s ^ 3 * ST
      ≤ 0.39894229 * (0.560302 * (4 / 35) * (s ^ 4 + 3.61 * s ^ 2)) := by
  have hs0 : 0 < s := by linarith only [hs]
  have hs' : s ≠ 0 := hs0.ne'
  have hsq : Real.sqrt (s ^ 2 + 1) ≤ s + q := by
    rw [Real.sqrt_le_left (by positivity)]
    nlinarith only [sq_nonneg q, hq1]
  have h72 := cert_Asum_correction hs
  have hpow : (s ^ 2 + 1) ^ 3 * (s + q) ≤ s ^ 7 + 3.61 * s ^ 5 := by
    have e : (s ^ 2 + 1) ^ 3 * (s + q) * (2 * s) = (s ^ 2 + 1) ^ 3 * (2 * s ^ 2 + 1) := by
      linear_combination ((s ^ 2 + 1) ^ 3) * hq1
    have h : (s ^ 2 + 1) ^ 3 * (s + q) * (2 * s) ≤ (s ^ 7 + 3.61 * s ^ 5) * (2 * s) := by
      rw [e]; linarith only [h72]
    exact le_of_mul_le_mul_right h (by linarith only [hs0])
  have hT' : ST ≤ 4 / 35 * (s ^ 7 + 3.61 * s ^ 5) := by
    have i := mul_le_mul_of_nonneg_left hsq (by positivity : (0 : ℝ) ≤ (s ^ 2 + 1) ^ 3)
    linarith only [i, hT, hpow]
  have t3 : a * 0.560302 / s ^ 3 * ST
      ≤ a * 0.560302 / s ^ 3 * (4 / 35 * (s ^ 7 + 3.61 * s ^ 5)) :=
    mul_le_mul_of_nonneg_left hT' (by positivity)
  have e2 : a * 0.560302 / s ^ 3 * (4 / 35 * (s ^ 7 + 3.61 * s ^ 5))
      = a * (0.560302 * (4 / 35) * (s ^ 4 + 3.61 * s ^ 2)) := by
    field
  have t4 : a * (0.560302 * (4 / 35) * (s ^ 4 + 3.61 * s ^ 2))
      ≤ 0.39894229 * (0.560302 * (4 / 35) * (s ^ 4 + 3.61 * s ^ 2)) :=
    mul_le_mul_of_nonneg_right ha (by positivity)
  linarith only [t3, e2, t4]

/-- The polynomial inequality behind `Asum_numeric`: the bound assembled there is at most
`0.478731 s⁵ - 0.974453 s⁴ + 0.642741 s³`. -/
private theorem cert_Asum {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ (0.478731 * s ^ 5 - 0.974453 * s ^ 4 + 0.642741 * s ^ 3)
        - (0.39894229 * (-2 * (2 / 5 * s ^ 5 + 1 / 2 * s ^ 3 - 0.84853) + (3 * s ^ 2
        + 2 / 3) * (2 / 3 * s ^ 3 + 1 / 2 * s - 1.17851) + (s ^ 2 / 3 - 1 / 15) * (2 * s
        - 2.44948) + s ^ 2 / 6 * 1.63300 + s / 6) - (s ^ 4 - 3 / 2 * s ^ 2 + 1 / 2)
        + 0.39894229 * 0.560302 * (4 / 35) * (s ^ 4 + 3.61 * s ^ 2)) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 315191231381025000293 / 512695312500000000000
      + t * (3239126376908918453 / 10253906250000000000
      + t * (59615529696217039 / 1640625000000000000 + t * (3209450974943 / 24609375000000000
      + t * (3976451421 / 437500000000000 + t * (63 / 250000000))))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- **The sum `𝒜`.** From the bounds of the four power sums `S₁`, …, `S₄` (in `Ledger` the sums of
`b^{-1/2}`, `b^{-3/2}`, `b^{1/2}`, `b^{3/2}`) and of the correction sum `S_T`, the bound of `𝒜` is
at most `0.478731 s⁵ - 0.974453 s⁴ + 0.642741 s³`. -/
theorem Asum_numeric {s a Rr S1 S2 S3 S4 ST : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2)
    (ha0 : 0 ≤ a) (ha : a ≤ 0.39894229)
    (h1 : S1 ≤ 2 * s + 1 / (2 * s) - 2.44948) (h2 : S2 ≤ 1.63300)
    (h3 : S3 ≤ 2 / 3 * (Rr * s) + 1 / 2 * s - 1.17851)
    (h4 : 2 / 5 * (Rr ^ 2 * s) + 1 / 2 * (Rr * s) - 0.84853 ≤ S4)
    (hT : ST ≤ 4 / 35 * ((Rr + 1) ^ 3 * Real.sqrt (Rr + 1))) :
    a * (-2 * S4 + (3 * Rr + 2 / 3) * S3 + (Rr / 3 - 1 / 15) * S1 + Rr / 6 * S2)
        - (Rr ^ 2 - 3 / 2 * Rr + 1 / 2) + a * 0.560302 / s ^ 3 * ST
      ≤ 0.478731 * s ^ 5 - 0.974453 * s ^ 4 + 0.642741 * s ^ 3 := by
  subst hRr
  have hs0 : 0 < s := by linarith only [hs]
  have hs' : s ≠ 0 := hs0.ne'
  obtain ⟨q, hq⟩ : ∃ q : ℝ, q = 1 / (2 * s) := ⟨_, rfl⟩
  have hq1 : q * (2 * s) = 1 := by rw [hq]; field
  have hq0 : 0 < q := by rw [hq]; positivity
  rw [← hq] at h1
  have hB := Asum_bracket hs hq1 hq0 h1 h2 h3 h4
  have hU0 := cert_Asum_bracket hs
  have t1 := mul_le_mul_of_nonneg_left hB ha0
  have t2 := mul_le_mul_of_nonneg_right ha hU0
  have t3 := Asum_correction hs hq1 hq0 ha0 ha hT
  have hc := cert_Asum hs
  linarith only [t1, t2, t3, hc]

/-- The bracket of the bound of `G`, a polynomial in `s`, is nonnegative. -/
private theorem cert_Gsum_bracket {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ (3 * (2 / 3 * s ^ 3 + 1 / 2 * s - 1.17851) + 1 / 3 * (2 * s + 25 / 324 - 2.44948)
        + 1 / 6 * 1.63300) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 67333045871 / 121500000 + t * (952909 / 3750 + t * (972 / 25 + t * (2))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- The polynomial inequality behind `Gsum_numeric`: the bound assembled there is at most
`2 (0.478731 s³ - 0.974453 s² + 0.642741 s)`. -/
private theorem cert_Gsum {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ (2 * (0.478731 * s ^ 3 - 0.974453 * s ^ 2 + 0.642741 * s))
        - (0.39894229 * (3 * (2 / 3 * s ^ 3 + 1 / 2 * s - 1.17851) + 1 / 3 * (2 * s + 25 / 324
        - 2.44948) + 1 / 6 * 1.63300) - 5 / 4 * (s ^ 2 - 1)
        + 0.39894229 * 0.560302 * (2 / 5) * s ^ 2) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 509352544950961979489 / 37968750000000000000
      + t * (24156268058889053 / 2343750000000000 + t * (289233472451421 / 125000000000000
      + t * (7978871 / 50000000))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- **The sum `G`.** From the bounds of the power sums `S₁`, `S₂`, `S₃` and of the correction sum
`S_G`, the bound of `G` is at most `2 (0.478731 s³ - 0.974453 s² + 0.642741 s)`. -/
theorem Gsum_numeric {s a Rr S1 S2 S3 SG : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2)
    (ha0 : 0 ≤ a) (ha : a ≤ 0.39894229)
    (h1 : S1 ≤ 2 * s + 1 / (2 * s) - 2.44948) (h2 : S2 ≤ 1.63300)
    (h3 : S3 ≤ 2 / 3 * (Rr * s) + 1 / 2 * s - 1.17851)
    (hG : SG ≤ 2 / 5 * (Rr ^ 2 * s)) :
    a * (3 * S3 + 1 / 3 * S1 + 1 / 6 * S2) - 5 / 4 * (Rr - 1) + a * 0.560302 / s ^ 3 * SG
      ≤ 2 * (0.478731 * s ^ 3 - 0.974453 * s ^ 2 + 0.642741 * s) := by
  subst hRr
  have hs0 : 0 < s := by linarith only [hs]
  have hs' : s ≠ 0 := hs0.ne'
  obtain ⟨q, hq⟩ : ∃ q : ℝ, q = 1 / (2 * s) := ⟨_, rfl⟩
  have hq1 : q * (2 * s) = 1 := by rw [hq]; field
  have hq0 : 0 < q := by rw [hq]; positivity
  have hqle : q ≤ 25 / 324 := by nlinarith only [mul_nonneg hq0.le (sub_nonneg.2 hs), hq1]
  rw [← hq] at h1
  have hB : 3 * S3 + 1 / 3 * S1 + 1 / 6 * S2
      ≤ (3 * (2 / 3 * s ^ 3 + 1 / 2 * s - 1.17851) + 1 / 3 * (2 * s + 25 / 324 - 2.44948)
          + 1 / 6 * 1.63300) := by
    linarith only [h1, h2, h3, hqle]
  have hU0 := cert_Gsum_bracket hs
  have t1 := mul_le_mul_of_nonneg_left hB ha0
  have t2 := mul_le_mul_of_nonneg_right ha hU0
  have t3 : a * 0.560302 / s ^ 3 * SG ≤ a * 0.560302 / s ^ 3 * (2 / 5 * ((s ^ 2) ^ 2 * s)) :=
    mul_le_mul_of_nonneg_left hG (by positivity)
  have e2 : a * 0.560302 / s ^ 3 * (2 / 5 * ((s ^ 2) ^ 2 * s))
      = a * (0.560302 * (2 / 5) * s ^ 2) := by
    field
  have t4 : a * (0.560302 * (2 / 5) * s ^ 2) ≤ 0.39894229 * (0.560302 * (2 / 5) * s ^ 2) :=
    mul_le_mul_of_nonneg_right ha (by positivity)
  have hc := cert_Gsum hs
  linarith only [t1, t2, t3, e2, t4, hc]

/-! ### The pair side: the three sum bounds and the exponent -/

/-- The bracket of the lower bound `pairSum_ge` at the tangent parameters `θ = R/(2k)` and
`μ = G₀ log(1+θ)/W₀` is at least `W₀`. -/
private theorem pair_bracket {s kk W0 P2 θ L μ WSv GSv ASv : ℝ} (hkk : 0 < kk) (hθ0 : 0 < θ)
    (hθk : θ * (2 * kk) = s ^ 2) (hL : L = Real.log (1 + θ)) (hμ0 : 0 ≤ μ)
    (hμW : μ * W0 = 2 * s * P2 * L)
    (hW : W0 ≤ WSv) (hG : GSv ≤ 2 * s * P2) (hA : ASv ≤ s ^ 3 * P2) :
    W0 ≤ (1 + μ) * WSv - ((L - θ / (1 + θ)) * GSv + 1 / (kk * (1 + θ)) * ASv) := by
  have hkk' : kk ≠ 0 := hkk.ne'
  have h1θ : 1 + θ ≠ 0 := by
    have h : 0 < 1 + θ := by linarith only [hθ0]
    exact h.ne'
  have hα : 0 ≤ L - θ / (1 + θ) := by
    have h := Real.one_sub_inv_le_log_of_pos (by linarith only [hθ0] : (0 : ℝ) < 1 + θ)
    have e : 1 - (1 + θ)⁻¹ = θ / (1 + θ) := by field
    rw [hL]; linarith only [h, e]
  have hβ : 0 ≤ 1 / (kk * (1 + θ)) := by positivity
  have i1 := mul_le_mul_of_nonneg_left hW (by linarith only [hμ0] : (0 : ℝ) ≤ 1 + μ)
  have i2 := mul_le_mul_of_nonneg_left hG hα
  have i3 := mul_le_mul_of_nonneg_left hA hβ
  have e1 : θ / (1 + θ) * (2 * s * P2) = 1 / (kk * (1 + θ)) * (s ^ 3 * P2) := by
    rw [div_mul_eq_mul_div, div_mul_eq_mul_div, div_eq_div_iff h1θ (mul_ne_zero hkk' h1θ)]
    linear_combination ((1 + θ) * s * P2) * hθk
  have e : (1 + μ) * W0 - ((L - θ / (1 + θ)) * (2 * s * P2)
      + 1 / (kk * (1 + θ)) * (s ^ 3 * P2)) = W0 := by
    linear_combination hμW + e1
  linarith only [i1, i2, i3, e]

/-- `P₂ (s² - s/4 + 1/12) ≤ W₀ (0.9575 s² - s/10)`, where
`P₂ = 0.478731 s² - 0.974453 s + 0.642741`; `mu_bound` uses it for the exponent `μ`. -/
private theorem cert_exponent {s : ℝ} (hs : 6.48 ≤ s) :
    0 ≤ (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (0.9575 * s ^ 2 - s / 10) - (0.478731 * s ^ 2
        - 0.974453 * s + 0.642741) * (s ^ 2 - s / 4 + 1 / 12) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 3871313377861 / 1562500000000 + t * (158648839393 / 93750000000
      + t * (921248139 / 2500000000 + t * (5198371 / 200000000 + t * (19 / 1000000)))) := by
    positivity
  exact key.le.trans_eq (by ring)

/-- `μ ≤ x (0.9575 - 1/(10 s))`, where `x = s³/k`, `θ = x/(2s)`, `μ W₀ = G₀ L` and
`L ≤ θ - θ²/2 + θ³/3`. -/
private theorem mu_bound {s x θ L μ W0 P2 c : ℝ} (hs : 6.48 ≤ s) (hx1 : 1 ≤ x) (hx2 : x ≤ 1.07593)
    (hθx : θ * (2 * s) = x) (hLc : L ≤ θ - θ ^ 2 / 2 + θ ^ 3 / 3)
    (hW0 : W0 = s ^ 2 / 2 - 1.06385 * s + 0.7184)
    (hP2 : P2 = 0.478731 * s ^ 2 - 0.974453 * s + 0.642741)
    (hμW : μ * W0 = 2 * s * P2 * L) (hcs : c * s ^ 2 = 0.9575 * s ^ 2 - s / 10) :
    μ ≤ x * c := by
  have hs0 : 0 < s := by linarith only [hs]
  have hxpos : 0 < x := by linarith only [hx1]
  have hW0pos : 0 < W0 := by
    rw [hW0]
    nlinarith only [mul_nonneg hs0.le (by linarith only [hs] : (0 : ℝ) ≤ s / 2 - 1.06385)]
  have hP2pos : 0 < P2 := by
    rw [hP2]
    nlinarith only [mul_nonneg hs0.le
      (by linarith only [hs] : (0 : ℝ) ≤ 0.478731 * s - 0.974453)]
  obtain ⟨y, hy⟩ : ∃ y : ℝ, y = θ * s := ⟨_, rfl⟩
  have hy2 : 2 * y = x := by rw [hy]; linear_combination hθx
  have h5 : μ * W0 * s ^ 2 ≤ x * P2 * (s ^ 2 - y * s / 2 + y ^ 2 / 3) := by
    have h := mul_le_mul_of_nonneg_left hLc (by positivity : (0 : ℝ) ≤ 2 * s * P2 * s ^ 2)
    have e : 2 * s * P2 * s ^ 2 * (θ - θ ^ 2 / 2 + θ ^ 3 / 3)
        = x * P2 * (s ^ 2 - y * s / 2 + y ^ 2 / 3) := by
      rw [← hy2, hy]; ring
    calc μ * W0 * s ^ 2 = 2 * s * P2 * s ^ 2 * L := by rw [hμW]; ring
      _ ≤ 2 * s * P2 * s ^ 2 * (θ - θ ^ 2 / 2 + θ ^ 3 / 3) := h
      _ = x * P2 * (s ^ 2 - y * s / 2 + y ^ 2 / 3) := e
  have h6 : s ^ 2 - y * s / 2 + y ^ 2 / 3 ≤ s ^ 2 - s / 4 + 1 / 12 := by
    nlinarith only [mul_nonneg (by linarith only [hy2, hx1] : (0 : ℝ) ≤ y - 1 / 2)
      (by linarith only [hy2, hx2, hs] : (0 : ℝ) ≤ s / 2 - (y + 1 / 2) / 3)]
  have h7 : P2 * (s ^ 2 - s / 4 + 1 / 12) ≤ W0 * (0.9575 * s ^ 2 - s / 10) := by
    have hc := cert_exponent hs
    rw [hP2, hW0]; linarith only [hc]
  have h8 : μ * W0 * s ^ 2 ≤ x * (W0 * (0.9575 * s ^ 2 - s / 10)) := by
    calc μ * W0 * s ^ 2 ≤ x * P2 * (s ^ 2 - y * s / 2 + y ^ 2 / 3) := h5
      _ ≤ x * P2 * (s ^ 2 - s / 4 + 1 / 12) := mul_le_mul_of_nonneg_left h6 (by positivity)
      _ = x * (P2 * (s ^ 2 - s / 4 + 1 / 12)) := by ring
      _ ≤ x * (W0 * (0.9575 * s ^ 2 - s / 10)) := mul_le_mul_of_nonneg_left h7 hxpos.le
  have h : μ * (W0 * s ^ 2) ≤ (x * c) * (W0 * s ^ 2) := by
    calc μ * (W0 * s ^ 2) = μ * W0 * s ^ 2 := by ring
      _ ≤ x * (W0 * (0.9575 * s ^ 2 - s / 10)) := h8
      _ = (x * c) * (W0 * s ^ 2) := by rw [← hcs]; ring
  exact le_of_mul_le_mul_right h (by positivity)

/-- `E₁ (1+δ)/x ≤ e^{-x c}` for `1 ≤ x ≤ 1.07593`, `c = 0.9575 - δ`, `δ ≥ 0`. -/
private theorem exp_xc_bound {x c c9 δ : ℝ} (hx1 : 1 ≤ x) (hx2 : x ≤ 1.07593) (hc9 : c9 = 0.9575)
    (hδ0 : 0 ≤ δ) (hc : c = c9 - δ) :
    0.38385 * (1 + δ) * (1 / x) ≤ Real.exp (-(x * c)) := by
  have hxpos : 0 < x := by linarith only [hx1]
  have hc1 : c ≤ 0.9575 := by rw [hc, hc9]; linarith only [hδ0]
  have hlogx : (x - 1) * c ≤ Real.log x := by
    have h := Real.le_log_one_add_of_nonneg (by linarith only [hx1] : (0 : ℝ) ≤ x - 1)
    have e : (1 : ℝ) + (x - 1) = x := by ring
    rw [e] at h
    have h2 : (x - 1) * 0.9575 ≤ 2 * (x - 1) / (x - 1 + 2) := by
      rw [le_div_iff₀ (by linarith only [hx1])]
      nlinarith only [mul_nonneg (by linarith only [hx1] : (0 : ℝ) ≤ x - 1)
        (by linarith only [hx2] : (0 : ℝ) ≤ 2 - 0.9575 * (x + 1))]
    have h3 : (x - 1) * c ≤ (x - 1) * 0.9575 :=
      mul_le_mul_of_nonneg_left hc1 (by linarith only [hx1])
    linarith only [h, h2, h3]
  have he2 : Real.exp ((x - 1) * c) ≤ x := by
    calc Real.exp ((x - 1) * c) ≤ Real.exp (Real.log x) := Real.exp_le_exp.2 hlogx
      _ = x := Real.exp_log hxpos
  have hE1 := exp_neg_09575 hc9
  have hEδ : 1 + δ ≤ Real.exp δ := by
    have h := Real.add_one_le_exp δ
    linarith only [h]
  have hsplit : Real.exp (-(x * c))
      = Real.exp (-c9) * Real.exp δ * Real.exp (-((x - 1) * c)) := by
    rw [← Real.exp_add, ← Real.exp_add]
    congr 1
    rw [hc]; ring
  have hinv : 1 / x ≤ Real.exp (-((x - 1) * c)) := by
    rw [div_le_iff₀ hxpos]
    have hm : Real.exp (-((x - 1) * c)) * Real.exp ((x - 1) * c) = 1 := by
      rw [← Real.exp_add]; simp
    have h := mul_le_mul_of_nonneg_left he2 (Real.exp_pos (-((x - 1) * c))).le
    linarith only [h, hm]
  rw [hsplit]
  exact mul_le_mul (mul_le_mul hE1 hEδ (by linarith only [hδ0]) (Real.exp_pos _).le) hinv
    (by positivity) (by positivity)

/-- From the lower bound `pairSum_ge` (hypothesis `hB`, for all tangent parameters) and the three
sum bounds:
`pairSum ≥ C · E₁ (1 + 1/(10s)) (k/s³) W₀` with `E₁ = 0.38385 ≤ e^{-0.9575}`. -/
theorem pair_numeric {s Rr kk WSv GSv ASv C P : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2)
    (hk1 : kk ≤ s ^ 3) (hk2 : s ^ 3 ≤ 1.07593 * kk) (hC : 0 ≤ C)
    (hW : Rr / 2 - 1.06385 * s + 0.7184 ≤ WSv)
    (hG : GSv ≤ 2 * (0.478731 * s ^ 3 - 0.974453 * s ^ 2 + 0.642741 * s))
    (hA : ASv ≤ 0.478731 * s ^ 5 - 0.974453 * s ^ 4 + 0.642741 * s ^ 3)
    (hB : ∀ θ μ : ℝ, 0 ≤ θ → C * (Real.exp (-μ) * ((1 + μ) * WSv
        - ((Real.log (1 + θ) - θ / (1 + θ)) * GSv + 1 / (kk * (1 + θ)) * ASv))) ≤ P) :
    C * (0.38385 * (1 + 1 / (10 * s)) * (kk / s ^ 3) * (Rr / 2 - 1.06385 * s + 0.7184)) ≤ P := by
  subst hRr
  have hs0 : 0 < s := by linarith only [hs]
  have hs' : s ≠ 0 := hs0.ne'
  have hs3 : 0 < s ^ 3 := by positivity
  have hkk : 0 < kk := by linarith only [hs3, hk2]
  have hkk' : kk ≠ 0 := hkk.ne'
  obtain ⟨W0, hW0⟩ : ∃ W0 : ℝ, W0 = s ^ 2 / 2 - 1.06385 * s + 0.7184 := ⟨_, rfl⟩
  obtain ⟨P2, hP2⟩ : ∃ P2 : ℝ, P2 = 0.478731 * s ^ 2 - 0.974453 * s + 0.642741 := ⟨_, rfl⟩
  have hG0 : 2 * (0.478731 * s ^ 3 - 0.974453 * s ^ 2 + 0.642741 * s) = 2 * s * P2 := by
    rw [hP2]; ring
  have hA0 : 0.478731 * s ^ 5 - 0.974453 * s ^ 4 + 0.642741 * s ^ 3 = s ^ 3 * P2 := by
    rw [hP2]; ring
  rw [hG0] at hG
  rw [hA0] at hA
  rw [← hW0] at hW ⊢
  have hW0pos : 0 < W0 := by
    rw [hW0]
    nlinarith only [mul_nonneg hs0.le (by linarith only [hs] : (0 : ℝ) ≤ s / 2 - 1.06385)]
  have hP2pos : 0 < P2 := by
    rw [hP2]
    nlinarith only [mul_nonneg hs0.le
      (by linarith only [hs] : (0 : ℝ) ≤ 0.478731 * s - 0.974453)]
  have hW0' : W0 ≠ 0 := hW0pos.ne'
  -- the tangent parameters
  obtain ⟨θ, hθ⟩ : ∃ θ : ℝ, θ = s ^ 2 / (2 * kk) := ⟨_, rfl⟩
  have hθ0 : 0 < θ := by rw [hθ]; positivity
  have hθk : θ * (2 * kk) = s ^ 2 := by rw [hθ]; field
  obtain ⟨L, hL⟩ : ∃ L : ℝ, L = Real.log (1 + θ) := ⟨_, rfl⟩
  have hL0 : 0 ≤ L := by rw [hL]; exact Real.log_nonneg (by linarith only [hθ0])
  obtain ⟨μ, hμ⟩ : ∃ μ : ℝ, μ = 2 * s * P2 * L / W0 := ⟨_, rfl⟩
  have hμ0 : 0 ≤ μ := by rw [hμ]; positivity
  have hμW : μ * W0 = 2 * s * P2 * L := by rw [hμ]; field
  have hbr := pair_bracket hkk hθ0 hθk hL hμ0 hμW hW hG hA
  -- the exponent
  obtain ⟨x, hx⟩ : ∃ x : ℝ, x = s ^ 3 / kk := ⟨_, rfl⟩
  have hx1 : 1 ≤ x := by rw [hx, le_div_iff₀ hkk]; linarith only [hk1]
  have hx2 : x ≤ 1.07593 := by rw [hx, div_le_iff₀ hkk]; linarith only [hk2]
  have hxpos : 0 < x := by linarith only [hx1]
  have hx' : x ≠ 0 := hxpos.ne'
  have hθx : θ * (2 * s) = x := by rw [hθ, hx]; field
  have hLc : L ≤ θ - θ ^ 2 / 2 + θ ^ 3 / 3 := by
    rw [hL]; exact log_one_add_le3 hθ0.le
  obtain ⟨c9, hc9⟩ : ∃ c9 : ℝ, c9 = 0.9575 := ⟨_, rfl⟩
  obtain ⟨δ, hδ⟩ : ∃ δ : ℝ, δ = 1 / (10 * s) := ⟨_, rfl⟩
  have hδ0 : 0 ≤ δ := by rw [hδ]; positivity
  have hδs : δ * (10 * s) = 1 := by rw [hδ]; field
  obtain ⟨c, hc⟩ : ∃ c : ℝ, c = c9 - δ := ⟨_, rfl⟩
  have hcs : c * s ^ 2 = 0.9575 * s ^ 2 - s / 10 := by
    rw [hc, hc9]; linear_combination (-s / 10) * hδs
  have hμc := mu_bound hs hx1 hx2 hθx hLc hW0 hP2 hμW hcs
  have he1 : Real.exp (-(x * c)) ≤ Real.exp (-μ) := Real.exp_le_exp.2 (by linarith only [hμc])
  have hfin := exp_xc_bound hx1 hx2 hc9 hδ0 hc
  have hkx : kk / s ^ 3 = 1 / x := by rw [hx]; field
  have hBθ := hB θ μ hθ0.le
  rw [← hL] at hBθ
  rw [← hδ, hkx]
  calc C * (0.38385 * (1 + δ) * (1 / x) * W0)
      ≤ C * (Real.exp (-μ) * W0) := by
        refine mul_le_mul_of_nonneg_left ?_ hC
        refine mul_le_mul_of_nonneg_right ?_ hW0pos.le
        exact hfin.trans he1
    _ ≤ C * (Real.exp (-μ) * ((1 + μ) * WSv
          - ((L - θ / (1 + θ)) * GSv + 1 / (kk * (1 + θ)) * ASv))) := by
        refine mul_le_mul_of_nonneg_left ?_ hC
        exact mul_le_mul_of_nonneg_left hbr (Real.exp_pos _).le
    _ ≤ P := hBθ

/-! ### The impulse side: the final inequality -/

/-- Insert the lower bound of `κ₂` and the upper bound of `κ₃` into the bound of `impulse_le`, and
replace `ρ = poissonMass R` by its Stirling bound `ρb` (the bound is nondecreasing in `ρ`). -/
private theorem imp_step1 {X ρ ρb e u c1 c2' a' b k2 k3 : ℝ} (he0 : 0 ≤ e) (hu0 : 0 ≤ u)
    (hc1_0 : 0 ≤ c1) (hc2'_0 : 0 ≤ c2') (ha'_0 : 0 ≤ a') (hb0 : 0 ≤ b) (hρ : ρ ≤ ρb)
    (hX : X ≤ ρ - e * ((1 + 0.35) * (c1 * k2) - u * (c2' * k3)))
    (hk2 : 1 / 2 - a' * ρ ≤ k2) (hk3 : k3 ≤ b * ρ - 1) :
    X ≤ ρb - e * ((1 + 0.35) * (c1 * (1 / 2 - a' * ρb)) - u * c2' * (b * ρb - 1)) := by
  have h1 : c1 * (1 / 2 - a' * ρ) ≤ c1 * k2 := mul_le_mul_of_nonneg_left hk2 hc1_0
  have h2 : u * (c2' * k3) ≤ u * (c2' * (b * ρ - 1)) :=
    mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hk3 hc2'_0) hu0
  have h3 := mul_le_mul_of_nonneg_left
    (by linarith only [h1, h2] :
      (1 + 0.35) * (c1 * (1 / 2 - a' * ρ)) - u * (c2' * (b * ρ - 1))
        ≤ (1 + 0.35) * (c1 * k2) - u * (c2' * k3)) he0
  have hcoef : 0 ≤ e * ((1 + 0.35) * (c1 * a') + u * c2' * b) :=
    mul_nonneg he0 (add_nonneg (mul_nonneg (by norm_num) (mul_nonneg hc1_0 ha'_0))
      (mul_nonneg (mul_nonneg hu0 hc2'_0) hb0))
  have h4 := mul_le_mul_of_nonneg_left hρ
    (by linarith only [hcoef] : 0 ≤ 1 + e * ((1 + 0.35) * (c1 * a') + u * c2' * b))
  linarith only [hX, h3, h4]

/-- Replace `1/(2ρb) - a'` by `J`, `b - 1/ρb` by `H` and `e^{-0.35}` by its decimal bounds. -/
private theorem imp_step2 {X ρb e u c1 c2' a' b J H : ℝ} (he1 : 0.704688 ≤ e) (he2 : e ≤ 0.704689)
    (hu0 : 0 ≤ u) (hc1_0 : 0 ≤ c1) (hc2'_0 : 0 ≤ c2') (hρb0 : 0 ≤ ρb) (hJ0 : 0 ≤ J)
    (hH0 : 0 ≤ H) (h5 : ρb * J ≤ 1 / 2 - a' * ρb) (h6 : b * ρb - 1 ≤ ρb * H)
    (h4 : X ≤ ρb - e * ((1 + 0.35) * (c1 * (1 / 2 - a' * ρb)) - u * c2' * (b * ρb - 1))) :
    X ≤ ρb * (1 - (1 + 0.35) * 0.704688 * c1 * J + 0.704689 * (u * c2') * H) := by
  have he0 : 0 ≤ e := by linarith only [he1]
  have i1 : c1 * (ρb * J) ≤ c1 * (1 / 2 - a' * ρb) := mul_le_mul_of_nonneg_left h5 hc1_0
  have i2 : u * c2' * (b * ρb - 1) ≤ u * c2' * (ρb * H) :=
    mul_le_mul_of_nonneg_left h6 (mul_nonneg hu0 hc2'_0)
  have i3 := mul_le_mul_of_nonneg_left
    (by linarith only [i1, i2] :
      (1 + 0.35) * (c1 * (ρb * J)) - u * c2' * (ρb * H)
        ≤ (1 + 0.35) * (c1 * (1 / 2 - a' * ρb)) - u * c2' * (b * ρb - 1)) he0
  have j1 : 0.704688 * (c1 * J * ρb) ≤ e * (c1 * J * ρb) :=
    mul_le_mul_of_nonneg_right he1 (mul_nonneg (mul_nonneg hc1_0 hJ0) hρb0)
  have j2 : e * (u * c2' * H * ρb) ≤ 0.704689 * (u * c2' * H * ρb) :=
    mul_le_mul_of_nonneg_right he2
      (mul_nonneg (mul_nonneg (mul_nonneg hu0 hc2'_0) hH0) hρb0)
  linarith only [h4, i3, j1, j2]

/-- The final inequality with its denominators cleared: the polynomial to which `imp_cert` reduces
the comparison of the impulse side with the pair side is positive. -/
private theorem cert_final {s : ℝ} (hs : 6.48 ≤ s) :
    0 < (1.9243 * (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (10 * s + 1)) * (3 * ((s ^ 2
        - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
        + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s)) - 30 * s ^ 3 * ((s ^ 2
        - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
        + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s) + (1
        + 0.35) * 0.704688 * (s * (s ^ 2 - 2)) * (15 * 1.253314 * s ^ 3 - 20 * s ^ 2
        - 1) * (2 * s) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 6 / 5 * s ^ 3) * ((s ^ 2
        - 1) * (2 * s ^ 2 - 1) + 2 * s) - 0.704689 * (4 * s ^ 2 * ((s ^ 2 - 3) * (4 / 5 * s ^ 2
        - 1))) * (s ^ 2 - 2.5066 * s + 1.67) * (10 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s
        - 1)) := by
  obtain ⟨t, ht, rfl⟩ := exists_shift hs
  have key : 0 < 167985278733377715569112118845646151677038147 / 58207660913467407226562500000000
      + t * (25473454912587810338262252882672391749404043 / 931322574615478515625000000000
      + t * (19414057707755611124463563927475986097969 / 372529029846191406250000000
      + t * (74583210998310773166844545697785350582541 / 1490116119384765625000000000
      + t * (112645615761826053848475139423686855363 / 3725290298461914062500000
      + t * (150993434654671944726484390459227056211 / 11920928955078125000000000
      + t * (92346701369663510673110373419007417 / 23841857910156250000000
      + t * (678893552468980140636941906197297 / 762939453125000000000
      + t * (11890567324955124950889586214423 / 76293945312500000000
      + t * (63779886295807335501044301049 / 3051757812500000000
      + t * (40712318293215513269790927 / 19073486328125000
      + t * (797850801912132250465021 / 4882812500000000
      + t * (177538699592492296909 / 19531250000000 + t * (169598366858762417 / 488281250000
      + t * (637443118608609 / 78125000000 + t * (1388961694331 / 15625000000))))))))))))))) := by
    positivity
  exact key.trans_eq (by ring)

/-- The final inequality in terms of the coefficients `c₁`, `c₂'`, `u`, `J`, `H`: the factor of the
bound of the impulse side is strictly below the factor `Pv` of the bound of the pair side
(certificate `cert_final`). -/
private theorem imp_cert {s K c1 c2' u J H Pv : ℝ} (hs : 6.48 ≤ s)
    (hK : K * (2 * s) = (s ^ 2 - 1) * (2 * s ^ 2 - 1))
    (hc1K : c1 * (2 * (K + s ^ 2 - 1)) = s ^ 2 - 2)
    (hc2K : c2' * (3 * (K + 3 / 5 * s ^ 2)) = (s ^ 2 - 3) * (4 / 5 * s ^ 2 - 1))
    (huK : u * (K + 1) = 1)
    (hJD : J * (15 * s ^ 2) = 15 * 1.253314 * s ^ 3 - 20 * s ^ 2 - 1)
    (hH : H = s ^ 2 - 2.5066 * s + 1.67)
    (hPv : Pv * (10 * s ^ 3) = 1.9243 * (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (10 * s + 1)) :
    1 - (1 + 0.35) * 0.704688 * c1 * J + 0.704689 * (u * c2') * H < Pv := by
  have hs0 : 0 < s := by linarith only [hs]
  have hs2 : (41.99 : ℝ) ≤ s ^ 2 := by nlinarith only [hs]
  have hPK : 0 < (s ^ 2 - 1) * (2 * s ^ 2 - 1) :=
    mul_pos (by linarith only [hs2]) (by linarith only [hs2])
  have hc1D : c1 * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) = (s * (s ^ 2 - 2)) := by
    linear_combination s * hc1K - c1 * hK
  have hprod : (u * (K + 1)) * (c2' * (3 * (K + 3 / 5 * s ^ 2)))
      = 1 * ((s ^ 2 - 3) * (4 / 5 * s ^ 2 - 1)) := by
    rw [huK, hc2K]
  have hc2D : u * c2' * (3 * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 6 / 5 * s ^ 3) * ((s ^ 2
      - 1) * (2 * s ^ 2 - 1) + 2 * s))
      = 4 * s ^ 2 * ((s ^ 2 - 3) * (4 / 5 * s ^ 2 - 1)) := by
    linear_combination (4 * s ^ 2) * hprod
      - (u * c2' * 3 * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + K * (2 * s) + 6 / 5 * s ^ 3 + 2 * s)) * hK
  have key := cert_final hs
  have d1 : 0 < ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) :=
    mul_pos (by linarith only [hs2]) (by linarith only [hs2, hs])
  have d2 : 0 < ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 6 / 5 * s ^ 3) := add_pos hPK (by positivity)
  have d3 : 0 < ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s) := add_pos hPK (by positivity)
  have hM : 0 < (30 * s ^ 3 * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2
      - 1) + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
      + 2 * s)) := mul_pos (mul_pos (mul_pos (by positivity) d1) d2) d3
  have hid : (Pv - (1 - (1 + 0.35) * 0.704688 * c1 * J + 0.704689 * (u * c2') * H))
      * (30 * s ^ 3 * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s))
      = (1.9243 * (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (10 * s + 1)) * (3 * ((s ^ 2
          - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s)) - 30 * s ^ 3 * ((s ^ 2
          - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s) + (1
          + 0.35) * 0.704688 * (s * (s ^ 2 - 2)) * (15 * 1.253314 * s ^ 3 - 20 * s ^ 2
          - 1) * (2 * s) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 6 / 5 * s ^ 3) * ((s ^ 2
          - 1) * (2 * s ^ 2 - 1) + 2 * s) - 0.704689 * (4 * s ^ 2 * ((s ^ 2 - 3) * (4 / 5 * s ^ 2
          - 1))) * (s ^ 2 - 2.5066 * s + 1.67) * (10 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s
          - 1)) := by
    rw [hH]
    linear_combination (3 * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2
        - 1) + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s)) * hPv
      + ((1 + 0.35) * 0.704688 * (2 * s) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s) * J * (15 * s ^ 2)) * hc1D
      + ((1 + 0.35) * 0.704688 * (2 * s) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s) * (s * (s ^ 2 - 2))) * hJD
      - (0.704689 * (s ^ 2 - 2.5066 * s + 1.67) * (10 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s
          - 1))) * hc2D
  have hpos : 0 < (Pv - (1 - (1 + 0.35) * 0.704688 * c1 * J + 0.704689 * (u * c2') * H))
      * (30 * s ^ 3 * ((s ^ 2 - 1) * (2 * s ^ 2 + 2 * s - 1)) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1)
          + 6 / 5 * s ^ 3) * ((s ^ 2 - 1) * (2 * s ^ 2 - 1) + 2 * s)) := by
    rw [hid]; exact key
  have h := pos_of_mul_pos_left hpos hM.le
  linarith only [h]

/-- The bound of `impulse_le` (hypothesis `hX`), with the lower bound `kc2_lower` of `κ₂`, the
closed form `kc3_eq` of `κ₃` and Stirling's bound of `ρ = poissonMass R` inserted, is strictly
below the pair-side bound `2 E₁ W₀ (1 + 1/(10s))/s³`, where `E₁ = 0.38385`. -/
theorem impulse_numeric {s Rr K a ρ e cc X k2 k3 : ℝ} (hs : 6.48 ≤ s) (hRr : Rr = s ^ 2)
    (hcc : cc = 0.35)
    (hK : K * (2 * s) = (Rr - 1) * (2 * Rr - 1))
    (ha0 : 0 < a) (ha2 : a ≤ 0.39894229)
    (he1 : 0.704688 ≤ e) (he2 : e ≤ 0.704689)
    (hρ : ρ ≤ a / s)
    (hX : X ≤ ρ - e * ((1 + cc) * ((Rr - 2) / (2 * (K + Rr - 1)) * k2)
      - 1 / (K + 1) * ((Rr - 3) / 3 * k3 * ((4 / 5 * Rr - 1) / (K + 3 / 5 * Rr)))))
    (hk2 : 1 / 2 - (4 / 3 + 1 / (15 * Rr)) * ρ ≤ k2)
    (hk3 : k3 = (Rr - 1) * ρ - 2 * k2) :
    X < 2 * 0.38385 * (Rr / 2 - 1.06385 * s + 0.7184) * (1 + 1 / (10 * s)) / s ^ 3 := by
  subst hRr hcc
  have hs0 : 0 < s := by linarith only [hs]
  have hs' : s ≠ 0 := hs0.ne'
  have hs2 : (41.99 : ℝ) ≤ s ^ 2 := by nlinarith only [hs]
  have he0 : 0 < e := by linarith only [he1]
  have hK0 : 0 < K := K_pos hs hK
  have hK1 : K + s ^ 2 - 1 ≠ 0 := by
    have h : 0 < K + s ^ 2 - 1 := by linarith only [hK0, hs2]
    exact h.ne'
  have hK2 : K + 1 ≠ 0 := by
    have h : 0 < K + 1 := by linarith only [hK0]
    exact h.ne'
  have hK3 : K + 3 / 5 * s ^ 2 ≠ 0 := by
    have h : 0 < K + 3 / 5 * s ^ 2 := by linarith only [hK0, hs2]
    exact h.ne'
  -- the coefficients
  obtain ⟨c1, hc1⟩ : ∃ c1 : ℝ, c1 = (s ^ 2 - 2) / (2 * (K + s ^ 2 - 1)) := ⟨_, rfl⟩
  obtain ⟨c2', hc2'⟩ : ∃ c2' : ℝ,
      c2' = (s ^ 2 - 3) / 3 * ((4 / 5 * s ^ 2 - 1) / (K + 3 / 5 * s ^ 2)) := ⟨_, rfl⟩
  obtain ⟨u, hu⟩ : ∃ u : ℝ, u = 1 / (K + 1) := ⟨_, rfl⟩
  obtain ⟨a', ha'⟩ : ∃ a' : ℝ, a' = 4 / 3 + 1 / (15 * s ^ 2) := ⟨_, rfl⟩
  have hc1K : c1 * (2 * (K + s ^ 2 - 1)) = s ^ 2 - 2 := by rw [hc1]; field
  have hc2K : c2' * (3 * (K + 3 / 5 * s ^ 2)) = (s ^ 2 - 3) * (4 / 5 * s ^ 2 - 1) := by
    rw [hc2']; field
  have huK : u * (K + 1) = 1 := by rw [hu]; field
  have ha'K : a' * (15 * s ^ 2) = 20 * s ^ 2 + 1 := by rw [ha']; field
  have hc1_0 : 0 ≤ c1 := by
    rw [hc1]
    exact div_nonneg (by linarith only [hs2]) (by linarith only [hK0, hs2])
  have hc2'_0 : 0 ≤ c2' := by
    rw [hc2']
    exact mul_nonneg (div_nonneg (by linarith only [hs2]) (by norm_num))
      (div_nonneg (by linarith only [hs2]) (by linarith only [hK0, hs2]))
  have hu0 : 0 < u := by rw [hu]; positivity
  have ha'_0 : 0 ≤ a' := by rw [ha']; positivity
  have ha'_le : a' ≤ 1.335 := by
    have h : 1 / (15 * s ^ 2) ≤ 1 / 600 :=
      one_div_le_one_div_of_le (by norm_num) (by linarith only [hs2])
    rw [ha']; linarith only [h]
  -- insert the bound of `κ₂`, the closed form of `κ₃` and Stirling's bound
  have e1 : (s ^ 2 - 3) / 3 * k3 * ((4 / 5 * s ^ 2 - 1) / (K + 3 / 5 * s ^ 2)) = c2' * k3 := by
    rw [hc2']; ring
  rw [← hc1, e1, ← hu] at hX
  rw [← ha'] at hk2
  have hk3le : k3 ≤ (s ^ 2 - 1 + 2 * a') * ρ - 1 := by rw [hk3]; linarith only [hk2]
  have hb0 : 0 ≤ s ^ 2 - 1 + 2 * a' := by linarith only [hs2, ha'_0]
  obtain ⟨ρb, hρb⟩ : ∃ ρb : ℝ, ρb = a / s := ⟨_, rfl⟩
  rw [← hρb] at hρ
  have hρbs : ρb * s = a := by rw [hρb]; field
  have hρb0 : 0 < ρb := by rw [hρb]; positivity
  have h4 := imp_step1 he0.le hu0.le hc1_0 hc2'_0 ha'_0 hb0 hρ hX hk2 hk3le
  obtain ⟨J, hJ⟩ : ∃ J : ℝ, J = 1.253314 * s - a' := ⟨_, rfl⟩
  obtain ⟨H, hH⟩ : ∃ H : ℝ, H = s ^ 2 - 2.5066 * s + 1.67 := ⟨_, rfl⟩
  have hJ0 : 0 ≤ J := by rw [hJ]; linarith only [hs, ha'_le]
  have hH0 : 0 ≤ H := by
    rw [hH]
    nlinarith only [mul_nonneg hs0.le (by linarith only [hs] : (0 : ℝ) ≤ s - 2.5066)]
  have h5 : ρb * J ≤ 1 / 2 - a' * ρb := by
    have e1 : ρb * J = 1.253314 * a - a' * ρb := by
      rw [hJ]; linear_combination 1.253314 * hρbs
    linarith only [e1, ha2]
  have h6 : (s ^ 2 - 1 + 2 * a') * ρb - 1 ≤ ρb * H := by
    have e1 : ρb * H - ((s ^ 2 - 1 + 2 * a') * ρb - 1)
        = 1 - 2.5066 * a + ρb * (2.67 - 2 * a') := by
      rw [hH]; linear_combination (-2.5066) * hρbs
    have h := mul_nonneg hρb0.le (by linarith only [ha'_le] : (0 : ℝ) ≤ 2.67 - 2 * a')
    linarith only [e1, h, ha2]
  have h8 := imp_step2 he1 he2 hu0.le hc1_0 hc2'_0 hρb0.le hJ0 hH0 h5 h6 h4
  -- the certificate
  obtain ⟨T, hT⟩ : ∃ T : ℝ,
      T = (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (1 + 1 / (10 * s)) / s ^ 3 := ⟨_, rfl⟩
  have hW0pos : 0 < s ^ 2 / 2 - 1.06385 * s + 0.7184 := by
    nlinarith only [mul_nonneg hs0.le (by linarith only [hs] : (0 : ℝ) ≤ s / 2 - 1.06385)]
  have hT0 : 0 ≤ T := by
    rw [hT]; exact div_nonneg (mul_nonneg hW0pos.le (by positivity)) (by positivity)
  obtain ⟨Pv, hPvdef⟩ : ∃ Pv : ℝ, Pv = 1.9243 * T * s := ⟨_, rfl⟩
  have hPv : Pv * (10 * s ^ 3)
      = 1.9243 * (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (10 * s + 1) := by
    rw [hPvdef, hT]; field
  have hJD : J * (15 * s ^ 2) = 15 * 1.253314 * s ^ 3 - 20 * s ^ 2 - 1 := by
    rw [hJ]; linear_combination (-1 : ℝ) * ha'K
  have hcert := imp_cert hs hK hc1K hc2K huK hJD hH hPv
  have h9 : X < ρb * Pv := lt_of_le_of_lt h8 (mul_lt_mul_of_pos_left hcert hρb0)
  have h10 : ρb * Pv = a * 1.9243 * T := by
    rw [hPvdef]; linear_combination (1.9243 * T) * hρbs
  have h11 : a * 1.9243 * T ≤ 2 * 0.38385 * T :=
    mul_le_mul_of_nonneg_right (by linarith only [ha2]) hT0
  have h12 : 2 * 0.38385 * (s ^ 2 / 2 - 1.06385 * s + 0.7184) * (1 + 1 / (10 * s)) / s ^ 3
      = 2 * 0.38385 * T := by
    rw [hT]; ring
  rw [h12]; linarith only [h9, h10, h11]

end Parking
