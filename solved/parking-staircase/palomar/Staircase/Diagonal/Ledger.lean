module

public import Parking.Basic.RealBounds
public import Parking.NextColumn.BirthdayIneq
public import Staircase.Diagonal.KernelDeficit
public import Mathlib.Analysis.Real.Pi.Bounds

/-!
# The ledger of the diagonal step

The diagonal step is proved term by term: for each index `m` of the curvature sum it bounds how
four quantities change between a position behind the curve and the position one row down and one
column to the right.  After logarithms the four bounds fit together when one inequality between
closed forms holds, the *ledger*.  For a column `k ≥ 265`, `q` with `(q - 1)³ ≤ k²` (`q - 1` is the
deficit of the position), `1 ≤ a ≤ q - 2` and `m = q - a` it reads

  `(5/2) (1/k - 1/(k+a)) + T/k + μ̂ · ((q+a)/2) / (k (k+1)) < log (1 + 1/k) + E₀ · log (1 + x)`

(`ledger`).  The three terms on the left are the bound for `log γ_{k+a} - log γ_k`
(`γ_j = (1 + 1/j)^{j-2}`), the bound for the growth of the kernel deficit, with
`T = kapStepBound k a`, and the exponent of the curvature step, in which
`μ̂ = (401/400) ((3/2) √(π m / 2) - 8/5)` bounds `(401/400) (D_m + 1)`.  The two terms on the right
are `-log (k/(k+1))` and the logarithm of the gain of the boundary term, with
`E₀ = ((q+2)/(2q)) μ₀(q, q²/(k-1))` and `x = q / ((k-1)(k+q))`.

## The proof

Both sides are compared with fractions of denominator `k²`.  Let `t = √m`.

* *The left side* is at most `Φ/k²` (`left_le`), where
  `Φ = (5/2 + (3/2)·1.047) a + (3/2)·4.45 a²/k + (q + a) (0.94235 t - 0.8)`.
  The first term uses `1/k - 1/(k+a) ≤ a/k²`.  The second uses the chord `1.047 + 4.45 ξ` of the
  rational function of `ξ = a/k` in `kapStepBound` over `0 ≤ ξ ≤ 0.151` (`chord`,
  `kapStepBound_le`).  The third uses `π < 3.1416` (`muhat_le`).
* *The right side* is at least `(k - 1/2 + G)/k²` with the gain `G = k² E₀ (x - x²/2) ≥ 0`, because
  `log (1 + u) ≥ u - u²/2`.
* *In between*, `Φ < k - 1/2 + G`.  In both cases below the square root `t` is bounded by a tangent
  of the parabola, `t ≤ (m + t₀²)/(2t₀)`, which leaves polynomials.
  For `q ≤ 36` (`small_deficit`) the gain is not needed: with `t₀ = 7/2`, `Φ` is at most a
  quadratic in `q` plus a quadratic in `a`, and `Φ < 264.5 ≤ k - 1/2`.
  For `q ≥ 36` (`large_deficit`) let `s = √q`.  Then `s³ ≤ 1.036 k`, and
  `G ≥ 0.305 s³` (`gain_lower`, from the lower bound `mu0_lower` for `μ₀`).  With `t₀ = (3/5) s`
  and after division by `s³`, the claim is an inequality in `e = 1/s ≤ 1/6` and `w = m/q`
  (`large_core`).

The hypothesis `(q - 1)³ ≤ k²` enters only through `range_facts`: `q^{3/2} ≤ 1.036 k` and
`q - 2 ≤ 0.151 k`.  The constants are fitted to the column `k = 265`, where `q ≤ 42`,
`42³/265² = 1.055` and `40/265 = 0.1509`, and they leave little room: the chord fails at
`ξ = 0.16`, `small_deficit` has room `4.2` in `264.5`, `large_core` room `0.024` in `1.27`.
-/

@[expose] public section

namespace Parking

/-! ### The range -/

/-- Behind the curve in a column `k ≥ 265`: `q^{3/2} ≤ 1.036 k` and `q - 2 ≤ 0.151 k`.  The first
is `q³ ≤ (1.036 k)²`.  For `q ≤ 42` both follow from `k ≥ 265`; for `q ≥ 43` from
`(q - 1)³ ≤ k²`, the first because `q/(q - 1) ≤ 43/42`. -/
private theorem range_facts {k q : ℕ} (hk : 265 ≤ k) (hq : 3 ≤ q) (hcurve : (q - 1) ^ 3 ≤ k ^ 2) :
    Real.sqrt q ^ 3 ≤ 1.036 * (k : ℝ) ∧ (q : ℝ) - 2 ≤ 0.151 * (k : ℝ) := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hc : ((q : ℝ) - 1) ^ 3 ≤ (k : ℝ) ^ 2 := by
    have h : (((q - 1 : ℕ) : ℝ)) ^ 3 ≤ (k : ℝ) ^ 2 := by exact_mod_cast hcurve
    rwa [Nat.cast_pred (by omega)] at h
  suffices h : (q : ℝ) ^ 3 ≤ (1.036 * (k : ℝ)) ^ 2 ∧ (q : ℝ) - 2 ≤ 0.151 * (k : ℝ) by
    refine ⟨le_of_pow_le_pow_left₀ two_ne_zero (by positivity) ?_, h.2⟩
    rw [← pow_mul, pow_mul', Real.sq_sqrt (Nat.cast_nonneg q)]
    exact h.1
  rcases Nat.lt_or_ge q 43 with hlt | hge
  · have hQ : (q : ℝ) ≤ 42 := by exact_mod_cast Nat.le_of_lt_succ hlt
    have h1 : (q : ℝ) ^ 3 ≤ 42 ^ 3 := pow_le_pow_left₀ (by positivity) hQ 3
    have h2 : (265 : ℝ) ^ 2 ≤ (k : ℝ) ^ 2 := pow_le_pow_left₀ (by norm_num) hK 2
    constructor <;> linarith
  · have hQ : (43 : ℝ) ≤ q := by exact_mod_cast hge
    have he : (0 : ℝ) ≤ (q : ℝ) - 43 := by linarith
    constructor
    · have h1 : (42 * (q : ℝ)) ^ 3 ≤ (43 * ((q : ℝ) - 1)) ^ 3 :=
        pow_le_pow_left₀ (by positivity) (by linarith) 3
      linarith [sq_nonneg (k : ℝ)]
    · refine le_of_pow_le_pow_left₀ two_ne_zero (by positivity) ?_
      nlinarith [mul_nonneg he he, mul_nonneg (mul_nonneg he he) he]

/-- Behind the curve in a column `k ≥ 265`, `a/k ≤ 0.151` for `a ≤ q - 2`. -/
private theorem ratio_le {k q a : ℕ} (hk : 265 ≤ k) (hq : 3 ≤ q) (hcurve : (q - 1) ^ 3 ≤ k ^ 2)
    (haq : a + 2 ≤ q) : (a : ℝ) / k ≤ 0.151 := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hAQ : (a : ℝ) + 2 ≤ q := by exact_mod_cast haq
  rw [div_le_iff₀ (by linarith)]
  linarith [(range_facts hk hq hcurve).2]

/-! ### The left side -/

/-- For `0 ≤ ξ ≤ 0.151` and `λ ≤ 1.0025` the denominator `23/24 - (3/2) ξ (1 + ξ/4)` is positive and
`λ (1 + (3/2) ξ + (3/8) ξ²) / (23/24 - (3/2) ξ (1 + ξ/4)) ≤ 1.047 + 4.45 ξ`. -/
private theorem chord {ξ lam : ℝ} (hξ0 : 0 ≤ ξ) (hξ : ξ ≤ 0.151) (hlam : lam ≤ 1.0025) :
    0 < 23 / 24 - 3 / 2 * ξ * (1 + ξ / 4) ∧
      lam * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) / (23 / 24 - 3 / 2 * ξ * (1 + ξ / 4))
        ≤ 1.047 + 4.45 * ξ := by
  have hu : 0 ≤ 0.151 - ξ := by linarith
  have h1 : 0 ≤ ξ * (0.151 - ξ) := mul_nonneg hξ0 hu
  have h2 : 0 ≤ ξ * ξ * (0.151 - ξ) := mul_nonneg (mul_nonneg hξ0 hξ0) hu
  have hD : 0 < 23 / 24 - 3 / 2 * ξ * (1 + ξ / 4) := by nlinarith
  refine ⟨hD, ?_⟩
  rw [div_le_iff₀ hD]
  have h3 : lam * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) ≤ 1.0025 * (1 + 3 / 2 * ξ + 3 / 8 * ξ ^ 2) :=
    mul_le_mul_of_nonneg_right hlam (by positivity)
  nlinarith [h1, h2, h3]

/-- The kernel deficit term against its chord: `kapStepBound k a ≤ (3/2) ξ (1.047 + 4.45 ξ)` with
`ξ = a/k`. -/
private theorem kapStepBound_le {k q a : ℕ} (hk : 265 ≤ k) (hq : 3 ≤ q)
    (hcurve : (q - 1) ^ 3 ≤ k ^ 2) (haq : a + 2 ≤ q) :
    kapStepBound k a ≤ 3 / 2 * ((a : ℝ) / k) * (1.047 + 4.45 * ((a : ℝ) / k)) := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hlam : 1 + 2 / (3 * ((k : ℝ) + 2)) ≤ 1.0025 := by
    have h : 2 / (3 * ((k : ℝ) + 2)) ≤ 0.0025 := by
      rw [div_le_iff₀ (by positivity)]
      linarith
    linarith
  unfold kapStepBound
  rw [mul_assoc, mul_div_assoc]
  exact mul_le_mul_of_nonneg_left (chord (by positivity) (ratio_le hk hq hcurve haq) hlam).2
    (by positivity)

/-- `(401/400) ((3/2) √(π m / 2) - 8/5) ≤ 2 (0.94235 t - 0.8)` for `t = √m`, from `π < 3.1416`. -/
private theorem muhat_le {m t : ℝ} (ht0 : 0 ≤ t) (ht : t ^ 2 = m) :
    401 / 400 * (3 / 2 * Real.sqrt (Real.pi * m / 2) - 8 / 5) ≤ 2 * (0.94235 * t - 0.8) := by
  have hm0 : 0 ≤ m := ht ▸ sq_nonneg t
  have hm : Real.pi * m ≤ 3.1416 * m := mul_le_mul_of_nonneg_right Real.pi_lt_d4.le hm0
  have h1 : Real.sqrt (Real.pi * m / 2) ≤ 1.25332 * t := by
    rw [Real.sqrt_le_left (by positivity), mul_pow, ht]
    linarith
  linarith

/-- The left side of the ledger is at most `Φ/K²`: three bounds with the common denominator `K²`,
from `1/K - 1/(K+A) ≤ A/K²`, the chord `T ≤ (3/2) (A/K) (1.047 + 4.45 A/K)` and `μ̂ ≤ 2τ`. -/
private theorem left_le {K A Q T μh τ : ℝ} (hK : 1 ≤ K) (hA : 0 ≤ A) (hQA : 0 ≤ Q + A)
    (hT : T ≤ 3 / 2 * (A / K) * (1.047 + 4.45 * (A / K))) (hτ0 : 0 ≤ τ) (hμ : μh ≤ 2 * τ) :
    5 / 2 * (1 / K - 1 / (K + A)) + T / K + μh * ((Q + A) / 2) / (K * (K + 1))
      ≤ ((5 / 2 + 3 / 2 * 1.047) * A + 3 / 2 * 4.45 * A ^ 2 / K + (Q + A) * τ) / K ^ 2 := by
  have hK0 : 0 < K := by linarith
  have hK2 : 0 < K ^ 2 := by positivity
  have h1 : 1 / K - 1 / (K + A) ≤ A / K ^ 2 := by
    have e : 1 / K - 1 / (K + A) = A / (K * (K + A)) := by
      field_simp
      ring
    rw [e]
    exact div_le_div_of_nonneg_left hA hK2 (by nlinarith)
  have h2 : T / K ≤ 3 / 2 * (A / K) * (1.047 + 4.45 * (A / K)) / K :=
    div_le_div_of_nonneg_right hT hK0.le
  have h3 : μh * ((Q + A) / 2) / (K * (K + 1)) ≤ (Q + A) * τ / K ^ 2 :=
    (div_le_div_of_nonneg_right (by nlinarith) (by positivity)).trans
      (div_le_div_of_nonneg_left (mul_nonneg hQA hτ0) hK2 (by nlinarith))
  have e : ((5 / 2 + 3 / 2 * 1.047) * A + 3 / 2 * 4.45 * A ^ 2 / K + (Q + A) * τ) / K ^ 2
      = 5 / 2 * (A / K ^ 2) + 3 / 2 * (A / K) * (1.047 + 4.45 * (A / K)) / K
        + (Q + A) * τ / K ^ 2 := by
    field_simp
    ring
  rw [e]
  linarith

/-! ### Small deficits: `q ≤ 36` -/

/-- For `q ≤ 36` no gain is needed: `Φ < 264.5 ≤ K - 1/2`.  The tangent `t ≤ (m + 49/4)/7` of the
parabola at `t = 7/2` bounds `Φ` by `αQ² + βQ` plus a quadratic in `A`
(`α = 0.94235/7`, `β = 0.94235 · 7/4 - 0.8`), which are at most `205.1` and `55.3`. -/
private theorem small_deficit {K Q A t : ℝ} (hK : 265 ≤ K) (hQ : Q ≤ 36) (hA1 : 1 ≤ A)
    (hAQ : A + 2 ≤ Q) (ht : t ^ 2 = Q - A) :
    (5 / 2 + 3 / 2 * 1.047) * A + 3 / 2 * 4.45 * A ^ 2 / K + (Q + A) * (0.94235 * t - 0.8)
      < K - 1 / 2 := by
  have h1 : t ≤ (Q - A + 12.25) / 7 := by linarith [sq_nonneg (t - 7 / 2)]
  have h2 : A ^ 2 / K ≤ A ^ 2 / 265 :=
    div_le_div_of_nonneg_left (sq_nonneg A) (by norm_num) hK
  have h3 : (Q + A) * t ≤ (Q + A) * ((Q - A + 12.25) / 7) :=
    mul_le_mul_of_nonneg_left h1 (by linarith)
  have h4 : 0 ≤ (36 - Q) * (36 + Q) := mul_nonneg (by linarith) (by linarith)
  rw [mul_div_assoc]
  linarith [sq_nonneg (A - 22.478)]

/-! ### Large deficits: `q ≥ 36` -/

/-- The inequality of the large deficits in the variables `e = 1/√q` and `w = m/q`.  The left side
is at most linear in `e` on `0 ≤ e ≤ 1/6` (`e² ≤ e/6`, `e³ ≤ e/36`), and at the two ends it is a
quadratic in `w`, at most `1.1 + 0.02` at `e = 0` and `1.23 + 0.02` at `e = 1/6`. -/
private theorem large_core {e w : ℝ} (he0 : 0 ≤ e) (he : e ≤ 1 / 6) :
    4.0705 * (1 - w) * e + 6.9153 * (1 - w) ^ 2 * e ^ 2
        + (2 - w) * (18847 / 24000 * (w + 0.36) - 0.8 * e) + e ^ 3 / 2 + 0.02
      ≤ 250 / 259 + 0.305 := by
  have h2 : e ^ 2 ≤ e / 6 := by nlinarith
  have h3 : e ^ 3 ≤ e / 36 := by nlinarith [mul_nonneg he0 (by linarith : (0 : ℝ) ≤ e / 6 - e ^ 2)]
  have hP0 : (2 - w) * (18847 / 24000 * (w + 0.36)) ≤ 1.1 := by
    nlinarith [sq_nonneg (w - 0.82)]
  have hP1 : (2 - w) * (18847 / 24000 * (w + 0.36))
      + (4.0705 * (1 - w) + 6.9153 * (1 - w) ^ 2 / 6 - 0.8 * (2 - w) + 1 / 72) / 6 ≤ 1.23 := by
    nlinarith [sq_nonneg (w - 0.3023)]
  have hc2 : 6.9153 * (1 - w) ^ 2 * e ^ 2 ≤ 6.9153 * (1 - w) ^ 2 * (e / 6) :=
    mul_le_mul_of_nonneg_left h2 (by positivity)
  have ha := mul_le_mul_of_nonneg_left hP0 (by linarith : (0 : ℝ) ≤ 1 - 6 * e)
  have hb := mul_le_mul_of_nonneg_left hP1 (by linarith : (0 : ℝ) ≤ 6 * e)
  linarith

/-- For `q ≥ 36`, with `s = √q`, `s³ ≤ 1.036 K` and a gain `G ≥ 0.305 s³`: `Φ < K - 1/2 + G`.
The tangent `t ≤ (m + 0.36 s²)/(1.2 s)` of the parabola at `t = (3/5) s` and `A²/K ≤ 1.036 A²/s³`
bound `Φ + 1/2 + 0.02 s³` by `s³` times the left side of `large_core` at `e = 1/s`, `w = m/s²`,
and `s³ (250/259 + 0.305) ≤ K + G`. -/
private theorem large_deficit {K Q A t s G : ℝ} (hs : 6 ≤ s) (hsQ : s ^ 2 = Q) (hA1 : 1 ≤ A)
    (hAQ : A + 2 ≤ Q) (hU : s ^ 3 ≤ 1.036 * K) (ht : t ^ 2 = Q - A) (hG : 0.305 * s ^ 3 ≤ G) :
    (5 / 2 + 3 / 2 * 1.047) * A + 3 / 2 * 4.45 * A ^ 2 / K + (Q + A) * (0.94235 * t - 0.8)
      < K - 1 / 2 + G := by
  have hs0 : 0 < s := by linarith
  have hs3 : 0 < s ^ 3 := by positivity
  have hK0 : 0 < K := by linarith
  have h1 : t ≤ (Q - A + 0.36 * s ^ 2) / (1.2 * s) := by
    rw [le_div_iff₀ (by positivity)]
    linarith [sq_nonneg (t - 0.6 * s)]
  have h2 : A ^ 2 / K ≤ 1.036 * A ^ 2 / s ^ 3 := by
    rw [div_le_div_iff₀ hK0 hs3]
    nlinarith [sq_nonneg A]
  have h3 : (Q + A) * (0.94235 * t - 0.8)
      ≤ (Q + A) * (0.94235 * ((Q - A + 0.36 * s ^ 2) / (1.2 * s)) - 0.8) :=
    mul_le_mul_of_nonneg_left (by linarith) (by linarith)
  have hcore := mul_le_mul_of_nonneg_left
    (large_core (e := 1 / s) (w := (Q - A) / s ^ 2) (by positivity)
      (one_div_le_one_div_of_le (by norm_num) hs)) hs3.le
  have hid : s ^ 3 * (4.0705 * (1 - (Q - A) / s ^ 2) * (1 / s)
        + 6.9153 * (1 - (Q - A) / s ^ 2) ^ 2 * (1 / s) ^ 2
        + (2 - (Q - A) / s ^ 2) * (18847 / 24000 * ((Q - A) / s ^ 2 + 0.36) - 0.8 * (1 / s))
        + (1 / s) ^ 3 / 2 + 0.02)
      = (5 / 2 + 3 / 2 * 1.047) * A + 3 / 2 * 4.45 * (1.036 * A ^ 2 / s ^ 3)
        + (Q + A) * (0.94235 * ((Q - A + 0.36 * s ^ 2) / (1.2 * s)) - 0.8)
        + 1 / 2 + 0.02 * s ^ 3 := by
    rw [← hsQ]
    field_simp
    ring
  rw [hid] at hcore
  rw [mul_div_assoc]
  linarith

/-! ### The gain -/

/-- `μ₀(q, X) ≥ 4(q-1)/(4.657 s + 5.25)` for `s = √q ≥ 6` and `X ≤ 1.04 s`.  The number
`μ = 4(q-1)/(4.657 s + 5.25)` satisfies `3μ ≤ 2.577 s - 2.75`, hence
`μ (2(4 + X) + 3μ) ≤ μ (4.657 s + 5.25) = 4(q-1)`, which is `(4 + X + 3μ)² ≤ (4 + X)² + 12(q-1)`. -/
private theorem mu0_lower {q : ℕ} {s X : ℝ} (hs : 6 ≤ s) (hsQ : s ^ 2 = (q : ℝ))
    (hX : X ≤ 1.04 * s) :
    4 * ((q : ℝ) - 1) / (4.657 * s + 5.25) ≤ mu0 q X := by
  have hS : 0 < 4.657 * s + 5.25 := by linarith
  obtain ⟨μ, hμ⟩ : ∃ μ : ℝ, μ = 4 * ((q : ℝ) - 1) / (4.657 * s + 5.25) := ⟨_, rfl⟩
  have hμS : μ * (4.657 * s + 5.25) = 4 * ((q : ℝ) - 1) := by
    rw [hμ]
    exact div_mul_cancel₀ _ hS.ne'
  have hμ0 : 0 ≤ μ := by
    rw [hμ, ← hsQ]
    exact div_nonneg (by nlinarith) hS.le
  have h3 : 3 * μ ≤ 2.577 * s - 2.75 := by
    refine le_of_mul_le_mul_right ?_ hS
    rw [mul_assoc, hμS, ← hsQ]
    nlinarith
  have h4 : μ * (2 * (4 + X) + 3 * μ) ≤ μ * (4.657 * s + 5.25) :=
    mul_le_mul_of_nonneg_left (by linarith) hμ0
  have h5 : 4 + X + 3 * μ ≤ Real.sqrt ((4 + X) ^ 2 + 12 * ((q : ℝ) - 1)) :=
    Real.le_sqrt_of_sq_le (by nlinarith)
  rw [← hμ]
  unfold mu0
  rw [le_div_iff₀ (by norm_num)]
  linarith

/-- The gain is at least `0.305 q^{3/2}` for `q ≥ 36`: with `s = √q`, `S = 4.657 s + 5.25` and
`x = q/((K-1)(K+q))`, the factor `((q+2)/(2q)) μ₀` is at least `2q/S` (`mu0_lower`),
`x - x²/2 ≥ 0.998 x` because `x ≤ 1/264`, and `K² x ≥ q s/(s + 1.036)` because `s³ ≤ 1.036 K`; the
product of the three lower bounds is `1.996 s⁵/((s + 1.036) S) ≥ 0.305 s³`. -/
private theorem gain_lower {q : ℕ} {K s : ℝ} (hs : 6 ≤ s) (hsQ : s ^ 2 = (q : ℝ)) (hK : 265 ≤ K)
    (hU : s ^ 3 ≤ 1.036 * K) :
    0.305 * s ^ 3 ≤ K ^ 2 * (((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / (K - 1)))
      * ((q : ℝ) / ((K - 1) * (K + q)) - ((q : ℝ) / ((K - 1) * (K + q))) ^ 2 / 2) := by
  have hs0 : 0 < s := by linarith
  have hQ : (36 : ℝ) ≤ q := by rw [← hsQ]; nlinarith
  have hS : 0 < 4.657 * s + 5.25 := by linarith
  have hX : (q : ℝ) ^ 2 / (K - 1) ≤ 1.04 * s := by
    rw [div_le_iff₀ (by linarith), ← hsQ]
    nlinarith [mul_le_mul_of_nonneg_left hU hs0.le,
      mul_nonneg hs0.le (by linarith : (0 : ℝ) ≤ K - 265)]
  have hμ := mu0_lower hs hsQ hX
  generalize mu0 q ((q : ℝ) ^ 2 / (K - 1)) = μ at hμ ⊢
  generalize (q : ℝ) = Q at hsQ hQ hμ ⊢
  have hden : 0 < (K - 1) * (K + Q) := mul_pos (by linarith) (by linarith)
  obtain ⟨x, hx⟩ : ∃ x : ℝ, x = Q / ((K - 1) * (K + Q)) := ⟨_, rfl⟩
  rw [← hx]
  have hx0 : 0 ≤ x := by rw [hx]; exact div_nonneg (by linarith) hden.le
  have hx1 : x ≤ 1 / 264 := by
    rw [hx, div_le_div_iff₀ hden (by norm_num)]
    nlinarith [mul_le_mul (by linarith : (264 : ℝ) ≤ K - 1) (by linarith : Q ≤ K + Q)
      (by linarith) (by linarith)]
  -- `E ≥ 2Q/S`
  have hE : 2 * Q / (4.657 * s + 5.25) ≤ (Q + 2) / (2 * Q) * μ := by
    refine le_trans ?_ (mul_le_mul_of_nonneg_left hμ (div_nonneg (by linarith) (by linarith)))
    rw [div_mul_div_comm, div_le_div_iff₀ hS (mul_pos (by linarith) hS)]
    nlinarith [mul_pos hS (by linarith : (0 : ℝ) < Q - 2), mul_pos hS (by linarith : (0 : ℝ) < Q)]
  -- `K² x ≥ Q s/(s + 1.036)`
  have hKx : Q * (s / (s + 1.036)) ≤ K ^ 2 * x := by
    have e : K ^ 2 * x = Q * (K ^ 2 / ((K - 1) * (K + Q))) := by rw [hx]; ring
    rw [e]
    refine mul_le_mul_of_nonneg_left ?_ (by linarith)
    rw [div_le_div_iff₀ (by linarith) hden]
    have e3 : s * Q = s ^ 3 := by rw [← hsQ]; ring
    nlinarith [mul_nonneg hs0.le (by linarith : (0 : ℝ) ≤ K + Q)]
  have h6 : 0.305 * ((s + 1.036) * (4.657 * s + 5.25)) ≤ 1.996 * s ^ 2 := by
    nlinarith [sq_nonneg (s - 6)]
  have hE0 : 0 ≤ (Q + 2) / (2 * Q) * μ := le_trans (div_nonneg (by linarith) hS.le) hE
  calc 0.305 * s ^ 3
      = s ^ 3 * (0.305 * ((s + 1.036) * (4.657 * s + 5.25)))
          / ((s + 1.036) * (4.657 * s + 5.25)) := by
        field_simp
    _ ≤ s ^ 3 * (1.996 * s ^ 2) / ((s + 1.036) * (4.657 * s + 5.25)) :=
        div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left h6 (by positivity)) (by positivity)
    _ = 0.998 * (Q * (s / (s + 1.036))) * (2 * Q / (4.657 * s + 5.25)) := by
        rw [← hsQ]
        field_simp
        ring
    _ ≤ 0.998 * (K ^ 2 * x) * ((Q + 2) / (2 * Q) * μ) :=
        mul_le_mul (mul_le_mul_of_nonneg_left hKx (by norm_num)) hE
          (div_nonneg (by linarith) hS.le)
          (mul_nonneg (by norm_num) (mul_nonneg (sq_nonneg K) hx0))
    _ = K ^ 2 * ((Q + 2) / (2 * Q) * μ) * (0.998 * x) := by ring
    _ ≤ K ^ 2 * ((Q + 2) / (2 * Q) * μ) * (x - x ^ 2 / 2) :=
        mul_le_mul_of_nonneg_left (by nlinarith) (mul_nonneg (sq_nonneg K) hE0)

/-! ### The ledger -/

/-- **The ledger.**  Behind the curve in a column `k ≥ 265`, for `q` with `(q - 1)³ ≤ k²` and
`1 ≤ a ≤ q - 2`:
`(5/2)(1/k - 1/(k+a)) + T/k + μ̂ ((q+a)/2)/(k(k+1)) < log (1 + 1/k) + E₀ log (1 + x)`, with
`T = kapStepBound k a`, `μ̂ = (401/400)((3/2)√(π(q-a)/2) - 8/5)`,
`E₀ = ((q+2)/(2q)) μ₀(q, q²/(k-1))` and `x = q/((k-1)(k+q))`.

With `t = √(q - a)` the left side is at most `Φ/k²` (`left_le`), and by `log (1 + u) ≥ u - u²/2`
the right side is at least `(k - 1/2 + G)/k²` with `G = k² E₀ (x - x²/2) ≥ 0`.  In between,
`Φ < k - 1/2 + G`: for `q ≤ 36` without the gain (`small_deficit`), for `q > 36` with
`G ≥ 0.305 q^{3/2}` (`large_deficit`, `gain_lower`). -/
theorem ledger {k q a : ℕ} (hk : 265 ≤ k) (hcurve : (q - 1) ^ 3 ≤ k ^ 2) (ha1 : 1 ≤ a)
    (haq : a + 2 ≤ q) :
    5 / 2 * (1 / (k : ℝ) - 1 / ((k : ℝ) + a)) + kapStepBound k a / k
        + 401 / 400 * (3 / 2 * Real.sqrt (Real.pi * ((q : ℝ) - a) / 2) - 8 / 5)
            * (((q : ℝ) + a) / 2) / ((k : ℝ) * ((k : ℝ) + 1))
      < Real.log (1 + 1 / (k : ℝ))
        + ((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1))
            * Real.log (1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q))) := by
  have hq : 3 ≤ q := by omega
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hA1 : (1 : ℝ) ≤ a := by exact_mod_cast ha1
  have hAQ : (a : ℝ) + 2 ≤ q := by exact_mod_cast haq
  have hK2 : (0 : ℝ) < (k : ℝ) ^ 2 := by positivity
  -- the left side
  obtain ⟨t, htdef⟩ : ∃ t : ℝ, t = Real.sqrt ((q : ℝ) - a) := ⟨_, rfl⟩
  have ht : t ^ 2 = (q : ℝ) - a := by rw [htdef]; exact Real.sq_sqrt (by linarith)
  have ht2 : 1.4 ≤ t := by rw [htdef]; exact Real.le_sqrt_of_sq_le (by linarith)
  have hL := left_le (K := (k : ℝ)) (Q := (q : ℝ)) (by linarith) (by linarith) (by linarith)
    (kapStepBound_le hk hq hcurve haq) (by linarith : (0 : ℝ) ≤ 0.94235 * t - 0.8)
    (muhat_le (by linarith) ht)
  -- the right side
  obtain ⟨x, hx⟩ : ∃ x : ℝ, x = (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)) := ⟨_, rfl⟩
  obtain ⟨E, hE⟩ : ∃ E : ℝ,
      E = ((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1)) := ⟨_, rfl⟩
  rw [← hx, ← hE]
  have hx0 : 0 ≤ x := by
    rw [hx]
    exact div_nonneg (by positivity) (mul_nonneg (by linarith) (by positivity))
  have hx1 : x ≤ 1 := by
    rw [hx]
    exact div_le_one_of_le₀ (by nlinarith) (mul_nonneg (by linarith) (by positivity))
  have hE0 : 0 ≤ E := by
    rw [hE]
    exact mul_nonneg (by positivity)
      (mu0_nonneg (by omega) (div_nonneg (by positivity) (by linarith)))
  have hlog1 := log_one_add_ge2 (u := 1 / (k : ℝ)) (by positivity)
  have hlog2 := mul_le_mul_of_nonneg_left (log_one_add_ge2 hx0) hE0
  have hG0 : 0 ≤ (k : ℝ) ^ 2 * E * (x - x ^ 2 / 2) :=
    mul_nonneg (mul_nonneg hK2.le hE0) (by nlinarith)
  -- in between
  have hΦ : (5 / 2 + 3 / 2 * 1.047) * (a : ℝ) + 3 / 2 * 4.45 * (a : ℝ) ^ 2 / k
        + ((q : ℝ) + a) * (0.94235 * t - 0.8)
      < (k : ℝ) - 1 / 2 + (k : ℝ) ^ 2 * E * (x - x ^ 2 / 2) := by
    rcases le_or_gt (q : ℝ) 36 with h36 | h36
    · linarith [small_deficit hK h36 hA1 hAQ ht]
    · have hsQ : Real.sqrt q ^ 2 = (q : ℝ) := Real.sq_sqrt (Nat.cast_nonneg q)
      have hs : 6 ≤ Real.sqrt q := Real.le_sqrt_of_sq_le (by linarith)
      have hU := (range_facts hk hq hcurve).1
      rw [hE, hx]
      exact large_deficit hs hsQ hA1 hAQ hU ht (gain_lower hs hsQ hK hU)
  have hmid := div_lt_div_of_pos_right hΦ hK2
  have e : ((k : ℝ) - 1 / 2 + (k : ℝ) ^ 2 * E * (x - x ^ 2 / 2)) / (k : ℝ) ^ 2
      = (1 / (k : ℝ) - (1 / (k : ℝ)) ^ 2 / 2) + E * (x - x ^ 2 / 2) := by
    field_simp
  rw [e] at hmid
  linarith

end Parking
