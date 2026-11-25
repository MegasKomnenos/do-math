module

public import Staircase.Cayley.BorelRatio
public import Staircase.CurveIncrease.Convolutions
public import Staircase.CurveIncrease.PairCriterion
public import Batteries.Tactic.OpenPrivate
import all Parking.NextColumn.Compositions
import all Parking.NextColumn.Frozen

/-!
# The pair side: a lower bound of the pair sum

Fix `k ≥ 1` and `R ≤ k`, put `N = k + R`, and write `P = poissonMass`, `a_m = cay m`.  The module
bounds the pair sum of the pair–impulse criterion from below by sums of the convolutions `κ₂`, `κ₃`
of the Poisson mass (`pairSum_ge`): for all real `θ ≥ 0` and `μ`,

`a_k · e^R · e^{-μ} · ((1+μ) · W_Σ - (α · G + β · 𝒜)) ≤ pairSum k R`,

where `α = log (1+θ) - θ/(1+θ)`, `β = 1/(k(1+θ))`, and

* `W_Σ = Wsum R = ∑_{b≤R} κ₂(b)`,
* `G = Gsum k R = ∑_{b≤R} (7/2 κ₂(b) + 2 κ₃(b)) + ∑_{c<R} κ₃(c) (1 + ϱ_c)`,
* `𝒜 = Asum k R = ∑_{b≤R} ((R - b/2)(κ₂(b) + 2κ₃(b)) + 5/2 (R-b) κ₂(b))`
  `+ ∑_{c<R} (R-c) κ₃(c)(1 + ϱ_c)`,

with `ϱ_c = rhoC N c = c/(2(N-c)) + c²/(8(N-c)²)`.

The proof has three steps.

*One pair.*  The term of the pair sum for the marked points `a < b` is a product of two chain sums,
two cut factors and the environment below `b`.  Every cut factor is `k/(N-s) = e^{-L(R-s)}` with the
log-excess `L(y) = log (1 + y/k)`, so Jensen's inequality (`Lam_jensen` for the chains, `zr_jensen`
for the environment) bounds the term from below by `a_k · e^R · P(a) · P(b-a) · e^{-X_{ab}}`, where
the exponent `X_{ab}` is the sum of the mean log-excess of the cut points above `a`, of `a`, of the
cut points between `a` and `b`, of `b`, of the vertices below `b`, and of the end term
`log (a_k e^{R-b}/a_{N-b})` (`pair_term_ge`).

*The sum of the exponents.*  `∑_{a<b≤R} P(a) P(b-a) · X_{ab} ≤ α · G + β · 𝒜` (`pairExp_sum_le`).
The logarithm lies below its tangent at `θ`, `L(y) ≤ α + β y`, so each of the six parts of the
exponent becomes a weight sum and a first moment of `κ₂` or `κ₃`, which the moment identities of
`Convolutions` evaluate.  The end term is at most `(3/2) · L(R-b)` because `e^{-m} a_m m^{3/2}` does
not decrease (`borel_log_mono`), and the weights of the vertices below `b` are bounded by
`borel_ratio_le`; this is where `ϱ_c` comes from.

*Assembly.*  `e^{-X} ≥ e^{-μ}(1 + μ - X)` for every `μ`, summed over the pairs.
-/

@[expose] public section

namespace Parking

open Finset

open private sum_Ioo_shift from Parking.NextColumn.Compositions
open private sum_Ioo_reflect from Parking.NextColumn.Frozen

/-- `W_Σ = ∑_{b=1}^{R} κ₂(b)`, the total weight of the pairs. -/
noncomputable def Wsum (R : ℕ) : ℝ := ∑ b ∈ Icc 1 R, kc2 b

/-- `ϱ_c = c/(2(N-c)) + c²/(8(N-c)²)`, the correction of the weight of the vertices below a
marked point. -/
noncomputable def rhoC (N : ℝ) (c : ℕ) : ℝ :=
  (c : ℝ) / (2 * (N - c)) + (c : ℝ) ^ 2 / (8 * (N - c) ^ 2)

/-- `G = ∑_{b≤R} (7/2 κ₂(b) + 2 κ₃(b)) + ∑_{0<c<R} κ₃(c) (1 + ϱ_c)` with `N = k+R`: the total weight
of the logarithms in the exponents of the pairs. -/
noncomputable def Gsum (k R : ℕ) : ℝ :=
  ∑ b ∈ Icc 1 R, (7 / 2 * kc2 b + 2 * kc3 b)
    + ∑ c ∈ Ioo 0 R, kc3 c * (1 + rhoC ((k : ℝ) + R) c)

/-- `𝒜 = ∑_{b≤R} ((R - b/2)(κ₂(b) + 2κ₃(b)) + 5/2 (R-b) κ₂(b)) + ∑_{0<c<R} (R-c) κ₃(c) (1 + ϱ_c)`
with `N = k+R`: the total excess in the exponents of the pairs. -/
noncomputable def Asum (k R : ℕ) : ℝ :=
  ∑ b ∈ Icc 1 R, (((R : ℝ) - (b : ℝ) / 2) * (kc2 b + 2 * kc3 b) + 5 / 2 * ((R : ℝ) - b) * kc2 b)
    + ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c * (1 + rhoC ((k : ℝ) + R) c)

/-! ### The log-excess -/

/-- The log-excess `L(y) = log (1 + y/k)`: a cut point or a vertex of size `k + y` carries the
factor `k/(k+y) = e^{-L(y)}`. -/
private noncomputable def logExc (k : ℕ) (y : ℝ) : ℝ := Real.log (1 + y / k)

private theorem logExc_nonneg {k : ℕ} {y : ℝ} (hy : 0 ≤ y) : 0 ≤ logExc k y :=
  Real.log_nonneg (le_add_of_nonneg_right (div_nonneg hy (Nat.cast_nonneg k)))

/-- The log-excess at the size `j ≥ k`: `L(j - k) = log j - log k`. -/
private theorem logExc_sub {k j : ℕ} (hk : 1 ≤ k) (hkj : k ≤ j) :
    logExc k ((j : ℝ) - k) = Real.log j - Real.log k := by
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  have hj0 : (0 : ℝ) < j := Nat.cast_pos.mpr (by omega)
  unfold logExc
  rw [show 1 + ((j : ℝ) - k) / k = (j : ℝ) / k by field_simp; ring,
    Real.log_div hj0.ne' hk0.ne']

/-- The tangent of the logarithm at `θ ≥ 0`: `L(y) ≤ (log (1+θ) - θ/(1+θ)) + y/(k(1+θ))` for
`y ≥ 0`. -/
private theorem logExc_le_tangent {k : ℕ} (hk : 1 ≤ k) {θ : ℝ} (hθ : 0 ≤ θ) {y : ℝ} (hy : 0 ≤ y) :
    logExc k y ≤ (Real.log (1 + θ) - θ / (1 + θ)) + 1 / ((k : ℝ) * (1 + θ)) * y := by
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  have hv : (0 : ℝ) < 1 + θ := by linarith
  have hu : (0 : ℝ) < 1 + y / k := by
    have h0 : 0 ≤ y / (k : ℝ) := div_nonneg hy hk0.le
    linarith
  have h1 := Real.log_le_sub_one_of_pos (div_pos hu hv)
  rw [Real.log_div hu.ne' hv.ne'] at h1
  have h2 : (1 + y / k) / (1 + θ) - 1 = -(θ / (1 + θ)) + 1 / ((k : ℝ) * (1 + θ)) * y := by
    field_simp
    ring
  unfold logExc
  linarith

/-- For a cut point `s ≤ R` the cut factor `k/(N-s)` is `e^{-L(R-s)}`. -/
private theorem thr_eq_exp {k R s : ℕ} (hk : 1 ≤ k) (hs : s ≤ R) :
    thr (k : ℝ) ((k : ℝ) + R) s = Real.exp (-(logExc k ((R : ℝ) - s))) := by
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  have hsR : (s : ℝ) ≤ R := Nat.cast_le.2 hs
  have e : 1 + ((R : ℝ) - s) / k = ((k : ℝ) + R - s) / k := by
    field_simp
    ring
  unfold logExc
  rw [Real.exp_neg, e, Real.exp_log (div_pos (by linarith) hk0), inv_div]
  rfl

/-! ### One pair -/

/-- The exponent `X_{ab}` of the pair `a < b`: the mean log-excess of the cut points above `a`, the
log-excess of `a`, the mean log-excess of the cut points between `a` and `b`, the log-excess of
`b`, the end term `log (a_k e^{R-b}/a_{N-b})`, and the mean of `log (t/k)` over the vertices of
size `t > k` below `b`. -/
private noncomputable def pairExp (k R a b : ℕ) : ℝ :=
  (∑ c ∈ Ioo 0 a, ren (a - c) * (ren c * logExc k ((R : ℝ) - c))) / ren a
    + logExc k ((R : ℝ) - a)
    + (∑ c ∈ Ioo 0 (b - a), ren (b - a - c) * (ren c * logExc k ((R : ℝ) - a - c))) / ren (b - a)
    + logExc k ((R : ℝ) - b)
    + Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b))
    + (∑ t ∈ Ioo k (k + R - b), ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k)))
        / cay (k + R - b)

/-- The product of the five lower bounds of a pair term, with the exponentials collected. -/
private theorem pair_core {ck eR ea eba eRb ra rba cN u1 u2 u3 u4 u5 u6 L1 L2 Z : ℝ}
    (hra : 0 < ra) (hrba : 0 < rba) (hcN : 0 < cN)
    (hE : eR * ea * eba = eRb) (hY : Real.exp (-u5) * (ck * eRb) = cN)
    (h1 : ra * Real.exp (-u1) ≤ L1) (h3 : rba * Real.exp (-u3) ≤ L2)
    (h5 : cN * Real.exp (-u6) ≤ Z) :
    ck * eR * (ea * ra * (eba * rba) * Real.exp (-(u1 + u2 + u3 + u4 + u5 + u6)))
      ≤ L1 * Real.exp (-u2) * L2 * Real.exp (-u4) * Z := by
  have hX : Real.exp (-(u1 + u2 + u3 + u4 + u5 + u6))
      = Real.exp (-u1) * Real.exp (-u2) * Real.exp (-u3) * Real.exp (-u4) * Real.exp (-u5)
          * Real.exp (-u6) := by
    simp only [← Real.exp_add]
    congr 1
    ring
  have e1 := Real.exp_pos (-u1)
  have e2 := Real.exp_pos (-u2)
  have e3 := Real.exp_pos (-u3)
  have e4 := Real.exp_pos (-u4)
  have e6 := Real.exp_pos (-u6)
  have s2 : ra * Real.exp (-u1) * Real.exp (-u2) * (rba * Real.exp (-u3))
      ≤ L1 * Real.exp (-u2) * L2 :=
    mul_le_mul (mul_le_mul_of_nonneg_right h1 e2.le) h3 (mul_pos hrba e3).le
      (mul_nonneg ((mul_pos hra e1).le.trans h1) e2.le)
  have s4 : ra * Real.exp (-u1) * Real.exp (-u2) * (rba * Real.exp (-u3)) * Real.exp (-u4)
        * (cN * Real.exp (-u6))
      ≤ L1 * Real.exp (-u2) * L2 * Real.exp (-u4) * Z :=
    mul_le_mul (mul_le_mul_of_nonneg_right s2 e4.le) h5 (mul_pos hcN e6).le
      (mul_nonneg ((by positivity : (0 : ℝ) ≤ ra * Real.exp (-u1) * Real.exp (-u2)
        * (rba * Real.exp (-u3))).trans s2) e4.le)
  refine le_of_eq_of_le ?_ s4
  rw [hX]
  linear_combination (ra * rba * Real.exp (-u1) * Real.exp (-u2) * Real.exp (-u3)
      * Real.exp (-u4) * Real.exp (-u6) * ck * Real.exp (-u5)) * hE
    + (ra * rba * Real.exp (-u1) * Real.exp (-u2) * Real.exp (-u3)
      * Real.exp (-u4) * Real.exp (-u6)) * hY

/-- **The lower bound for one pair.** For `0 < a < b ≤ R ≤ k`, the term of the pair sum for the
marked points `a < b` is at least `a_k · e^R · P(a) · P(b-a) · e^{-X_{ab}}`.  The two chain sums are
bounded by `Lam_jensen`, the environment by `zr_jensen`, and the two cut factors are exponentials
of log-excesses. -/
private theorem pair_term_ge {k R : ℕ} (hk : 1 ≤ k) (hR : R ≤ k) {a b : ℕ} (ha : 0 < a)
    (hab : a < b) (hb : b ≤ R) :
    cay k * Real.exp (R : ℝ)
        * (poissonMass a * poissonMass (b - a) * Real.exp (-(pairExp k R a b)))
      ≤ Lam (thr (k : ℝ) ((k : ℝ) + R)) a * thr (k : ℝ) ((k : ℝ) + R) a
          * Lam (fun s => thr (k : ℝ) ((k : ℝ) + R) (a + s)) (b - a)
          * thr (k : ℝ) ((k : ℝ) + R) b * zr k (k + R - b - 1) := by
  have hck : 0 < cay k := cay_pos (by omega)
  have hcN : 0 < cay (k + R - b) := cay_pos (by omega)
  -- the chain above `a`
  have hA : Lam (thr (k : ℝ) ((k : ℝ) + R)) a
      = Lam (fun s => Real.exp (-(logExc k ((R : ℝ) - s)))) a :=
    Lam_congr fun s hs => thr_eq_exp hk (by rw [mem_Ioo] at hs; omega)
  have h1 := Lam_jensen (fun s => logExc k ((R : ℝ) - s)) (show 1 ≤ a by omega)
  -- the chain between `a` and `b`
  have hB : Lam (fun s => thr (k : ℝ) ((k : ℝ) + R) (a + s)) (b - a)
      = Lam (fun s => Real.exp (-(logExc k ((R : ℝ) - a - s)))) (b - a) := by
    refine Lam_congr fun s hs => ?_
    rw [mem_Ioo] at hs
    have h := thr_eq_exp (k := k) (R := R) (s := a + s) hk (by omega)
    rw [Nat.cast_add, ← sub_sub] at h
    exact h
  have h3 := Lam_jensen (fun s => logExc k ((R : ℝ) - a - s)) (show 1 ≤ b - a by omega)
  -- the environment below `b`
  have h5 := zr_jensen hk (M := k + R - b) (by omega) (by omega)
  -- the exponentials of the sizes
  have hE : Real.exp (R : ℝ) * Real.exp (-(a : ℝ)) * Real.exp (-((b - a : ℕ) : ℝ))
      = Real.exp ((R : ℝ) - b) := by
    rw [← Real.exp_add, ← Real.exp_add, Nat.cast_sub hab.le]
    congr 1
    ring
  have hY : Real.exp (-(Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b))))
      * (cay k * Real.exp ((R : ℝ) - b)) = cay (k + R - b) := by
    have hx : 0 < cay k * Real.exp ((R : ℝ) - b) := mul_pos hck (Real.exp_pos _)
    rw [Real.exp_neg, Real.exp_log (div_pos hx hcN), inv_div]
    exact div_mul_cancel₀ _ hx.ne'
  rw [hA, hB, thr_eq_exp hk (show a ≤ R by omega), thr_eq_exp hk hb]
  unfold poissonMass pairExp
  exact pair_core (ren_pos a) (ren_pos (b - a)) hcN hE hY h1 h3 h5

/-! ### The sum of the exponents -/

/-- `P(a) · (∑_{0<c<a} ren (a-c) · ren c · F(c)) / ren a = ∑_{0<c<a} P(c) · P(a-c) · F(c)`: a mean
over the cut points of a chain of length `a`, weighted with `P(a)`. -/
private theorem poissonMass_mul_mean (F : ℕ → ℝ) (a : ℕ) :
    poissonMass a * ((∑ c ∈ Ioo 0 a, ren (a - c) * (ren c * F c)) / ren a)
      = ∑ c ∈ Ioo 0 a, poissonMass c * poissonMass (a - c) * F c := by
  rw [poissonMass, mul_assoc, mul_div_cancel₀ _ (ren_pos a).ne', Finset.mul_sum]
  refine Finset.sum_congr rfl fun c hc => ?_
  rw [poissonMass_mul (mem_Ioo.1 hc).2.le]
  ring

/-- The marked point `a` itself: for a line `α + β y` above `L` on `y ≥ 0` and an offset `ρ ≥ b`,
`∑_{0<a<b} P(a) P(b-a) · L(ρ - a) ≤ (α + β (ρ - b/2)) · κ₂(b)`, by `kc2_mom`. -/
private theorem exp_row_point {k : ℕ} {α β : ℝ}
    (hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y) {ρ : ℝ} {b : ℕ} (hb : (b : ℝ) ≤ ρ) :
    ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * logExc k (ρ - a)
      ≤ (α + β * (ρ - (b : ℝ) / 2)) * kc2 b := by
  have h1 : ∀ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * logExc k (ρ - a)
      ≤ (α + β * ρ) * (poissonMass a * poissonMass (b - a))
        - β * ((a : ℝ) * (poissonMass a * poissonMass (b - a))) := by
    intro a ha
    have ha' : (a : ℝ) ≤ b := Nat.cast_le.2 (mem_Ioo.1 ha).2.le
    have hw : 0 ≤ poissonMass a * poissonMass (b - a) :=
      mul_nonneg (poissonMass_pos a).le (poissonMass_pos (b - a)).le
    have h := mul_le_mul_of_nonneg_left (hL (ρ - a) (by linarith)) hw
    linarith
  refine (Finset.sum_le_sum h1).trans (le_of_eq ?_)
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc2_mom b]
  unfold kc2
  ring

/-- The cut points above `a`:
`∑_{0<a<b} P(a) P(b-a) · (mean of L(R-c) over the cut points c of the chain above a)`
`≤ (α + β (R - b/3)) · κ₃(b)`, by `exp_row_point` and `kc3_mom_left`. -/
private theorem exp_row_above {k : ℕ} {α β : ℝ}
    (hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y) {R b : ℕ} (hb : b ≤ R) :
    ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
        * ((∑ c ∈ Ioo 0 a, ren (a - c) * (ren c * logExc k ((R : ℝ) - c))) / ren a)
      ≤ (α + β * ((R : ℝ) - (b : ℝ) / 3)) * kc3 b := by
  have h1 : ∀ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
        * ((∑ c ∈ Ioo 0 a, ren (a - c) * (ren c * logExc k ((R : ℝ) - c))) / ren a)
      ≤ (α + β * R) * (kc2 a * poissonMass (b - a))
        - β / 2 * ((a : ℝ) * (kc2 a * poissonMass (b - a))) := by
    intro a ha
    have haR : (a : ℝ) ≤ R := Nat.cast_le.2 (le_trans (mem_Ioo.1 ha).2.le hb)
    have hrow := mul_le_mul_of_nonneg_left (exp_row_point hL (ρ := (R : ℝ)) (b := a) haR)
      (poissonMass_pos (b - a)).le
    rw [mul_right_comm, poissonMass_mul_mean (fun c => logExc k ((R : ℝ) - c)) a, mul_comm]
    linarith
  refine (Finset.sum_le_sum h1).trans (le_of_eq ?_)
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc3_mom_left b]
  unfold kc3
  ring

/-- The cut points between `a` and `b`:
`∑_{0<a<b} P(a) P(b-a) · (mean of L(R-a-c) over the cut points c of the chain between a and b)`
`≤ (α + β (R - 2b/3)) · κ₃(b)`, by `exp_row_point` and `kc3_mom_right`. -/
private theorem exp_row_between {k : ℕ} {α β : ℝ}
    (hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y) {R b : ℕ} (hb : b ≤ R) :
    ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
        * ((∑ c ∈ Ioo 0 (b - a), ren (b - a - c) * (ren c * logExc k ((R : ℝ) - a - c)))
            / ren (b - a))
      ≤ (α + β * ((R : ℝ) - 2 * (b : ℝ) / 3)) * kc3 b := by
  have hbR : (b : ℝ) ≤ R := Nat.cast_le.2 hb
  have h1 : ∀ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
        * ((∑ c ∈ Ioo 0 (b - a), ren (b - a - c) * (ren c * logExc k ((R : ℝ) - a - c)))
            / ren (b - a))
      ≤ (α + β * ((R : ℝ) - (b : ℝ) / 2)) * (poissonMass a * kc2 (b - a))
        - β / 2 * ((a : ℝ) * (poissonMass a * kc2 (b - a))) := by
    intro a ha
    have hcast : ((b - a : ℕ) : ℝ) = (b : ℝ) - a := Nat.cast_sub (mem_Ioo.1 ha).2.le
    have hrow := mul_le_mul_of_nonneg_left
      (exp_row_point hL (ρ := (R : ℝ) - a) (b := b - a) (by rw [hcast]; linarith))
      (poissonMass_pos a).le
    rw [mul_assoc, poissonMass_mul_mean (fun c => logExc k ((R : ℝ) - a - c)) (b - a)]
    rw [hcast] at hrow
    linarith
  refine (Finset.sum_le_sum h1).trans (le_of_eq ?_)
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc3_mom_right b, kc3_comm b]
  ring

/-- The end term is at most `3/2` of the log-excess of `b`:
`log (a_k e^{R-b}/a_{N-b}) ≤ (3/2) · L(R-b)`, because `e^{-m} a_m m^{3/2}` does not decrease. -/
private theorem end_term_le {k R b : ℕ} (hk : 1 ≤ k) (hb : b ≤ R) :
    Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b))
      ≤ 3 / 2 * logExc k ((R : ℝ) - b) := by
  have hck : 0 < cay k := cay_pos (by omega)
  have hcj : 0 < cay (k + R - b) := cay_pos (by omega)
  have hcast : ((k + R - b : ℕ) : ℝ) = (k : ℝ) + R - b := by
    rw [Nat.cast_sub (by omega), Nat.cast_add]
  have hmono := borel_log_mono hk (show k ≤ k + R - b by omega)
  have hL := logExc_sub hk (show k ≤ k + R - b by omega)
  rw [hcast, show (k : ℝ) + R - b - k = (R : ℝ) - b by ring] at hL
  rw [hcast] at hmono
  rw [Real.log_div (mul_pos hck (Real.exp_pos _)).ne' hcj.ne',
    Real.log_mul hck.ne' (Real.exp_pos _).ne', Real.log_exp, hL]
  linarith

/-- The marked point `b` and the end term:
`∑_{0<a<b} P(a) P(b-a) · (L(R-b) + log (a_k e^{R-b}/a_{N-b})) ≤ (α + β (R-b)) · (5/2) κ₂(b)`. -/
private theorem exp_row_end {k R b : ℕ} (hk : 1 ≤ k) (hb : b ≤ R) {α β : ℝ}
    (hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y) :
    ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
        * (logExc k ((R : ℝ) - b) + Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b)))
      ≤ (α + β * ((R : ℝ) - b)) * (5 / 2 * kc2 b) := by
  have hbR : (0 : ℝ) ≤ (R : ℝ) - b := sub_nonneg.2 (Nat.cast_le.2 hb)
  have h1 := end_term_le hk hb
  have h2 := hL _ hbR
  have h3 := mul_le_mul_of_nonneg_left
    (show logExc k ((R : ℝ) - b)
        + Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b))
      ≤ 5 / 2 * (α + β * ((R : ℝ) - b)) by linarith) (kc2_nonneg b)
  rw [← Finset.sum_mul]
  show kc2 b * _ ≤ _
  linarith

/-- The vertices below `b`, in the coordinate `c = N - t` of a cut point: `b < c < R`. -/
private theorem below_sum_reindex {k R b : ℕ} (hk : 1 ≤ k) (hb : b ≤ R) :
    ∑ t ∈ Ioo k (k + R - b), ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k))
      = ∑ c ∈ Ioo b R, ren (c - b) * cay (k + R - c) * logExc k ((R : ℝ) - c) := by
  rw [sum_Ioo_reflect _ k (k + R - b), show k + R - b - k = R - b by omega, sum_Ioo_shift _ b R]
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [mem_Ioo] at hj
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  have ht0 : (0 : ℝ) < ((k + R - (b + j) : ℕ) : ℝ) := Nat.cast_pos.mpr (by omega)
  have hcast : ((k + R - (b + j) : ℕ) : ℝ) - k = (R : ℝ) - ((b + j : ℕ) : ℝ) := by
    rw [Nat.cast_sub (show b + j ≤ k + R by omega), Nat.cast_add]
    ring
  have hL := logExc_sub hk (show k ≤ k + R - (b + j) by omega)
  rw [hcast] at hL
  rw [show k + R - b - (k + R - b - j) = j by omega, show b + j - b = j by omega,
    show k + R - b - j = k + R - (b + j) by omega, hL, Real.log_div ht0.ne' hk0.ne']
  ring

/-- The weight of a vertex below `b`, at the cut point `c > b`:
`ren (c-b) · a_{N-c}/a_{N-b} ≤ P(c-b) · (1 + (3/2) z + (3/8) z²)` with `z = (c-b)/(N-c)`, by
`borel_ratio_le`. -/
private theorem below_weight_le {k R b c : ℕ} (hk : 1 ≤ k) (hbc : b < c) (hcR : c < R) :
    ren (c - b) * cay (k + R - c) / cay (k + R - b)
      ≤ poissonMass (c - b) * (1 + 3 / 2 * (((c : ℝ) - b) / ((k : ℝ) + R - c))
          + 3 / 8 * (((c : ℝ) - b) / ((k : ℝ) + R - c)) ^ 2) := by
  have hρ := borel_ratio_le (show 1 ≤ k + R - c by omega) (show k + R - c ≤ k + R - b by omega)
  have hci : ((k + R - c : ℕ) : ℝ) = (k : ℝ) + R - c := by
    rw [Nat.cast_sub (by omega), Nat.cast_add]
  have hcj : ((k + R - b : ℕ) : ℝ) = (k : ℝ) + R - b := by
    rw [Nat.cast_sub (by omega), Nat.cast_add]
  rw [hci, hcj, show (k : ℝ) + R - b - ((k : ℝ) + R - c) = (c : ℝ) - b by ring] at hρ
  have hren : ren (c - b) = Real.exp ((c : ℝ) - b) * poissonMass (c - b) := by
    unfold poissonMass
    rw [← mul_assoc, ← Real.exp_add, Nat.cast_sub hbc.le, add_neg_cancel, Real.exp_zero, one_mul]
  calc ren (c - b) * cay (k + R - c) / cay (k + R - b)
      = poissonMass (c - b)
          * (Real.exp ((c : ℝ) - b) * cay (k + R - c) / cay (k + R - b)) := by
        rw [hren]
        ring
    _ ≤ _ := mul_le_mul_of_nonneg_left hρ (poissonMass_pos (c - b)).le

/-- The weights of the vertices below, summed over the upper point `b` for a fixed cut point `c`:
`∑_{0<b<c} κ₂(b) · P(c-b) · (1 + (3/2) z + (3/8) z²) ≤ κ₃(c) · (1 + c/(2D) + c²/(8D²))` with
`z = (c-b)/D`, by `(c-b)² ≤ c(c-b)` and `kc3_mom_left`. -/
private theorem below_weight_sum (c : ℕ) {D : ℝ} (hD : 0 < D) :
    ∑ b ∈ Ioo 0 c, kc2 b * (poissonMass (c - b)
        * (1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * (((c : ℝ) - b) / D) ^ 2))
      ≤ kc3 c * (1 + ((c : ℝ) / (2 * D) + (c : ℝ) ^ 2 / (8 * D ^ 2))) := by
  have h1 : ∀ b ∈ Ioo 0 c, kc2 b * (poissonMass (c - b)
        * (1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * (((c : ℝ) - b) / D) ^ 2))
      ≤ (1 + 3 / 2 * (c : ℝ) / D + 3 / 8 * (c : ℝ) ^ 2 / D ^ 2) * (kc2 b * poissonMass (c - b))
        - (3 / 2 / D + 3 / 8 * (c : ℝ) / D ^ 2) * ((b : ℝ) * (kc2 b * poissonMass (c - b))) := by
    intro b hb
    have hb0 : (0 : ℝ) ≤ b := Nat.cast_nonneg b
    have hbc : (b : ℝ) ≤ c := Nat.cast_le.2 (mem_Ioo.1 hb).2.le
    have hw : 0 ≤ kc2 b * poissonMass (c - b) :=
      mul_nonneg (kc2_nonneg b) (poissonMass_pos (c - b)).le
    have hsq : (((c : ℝ) - b) / D) ^ 2 ≤ (c : ℝ) * ((c : ℝ) - b) / D ^ 2 := by
      rw [div_pow]
      exact div_le_div_of_nonneg_right (by nlinarith [mul_nonneg (sub_nonneg.2 hbc) hb0])
        (pow_pos hD 2).le
    have h := mul_le_mul_of_nonneg_left
      (show 1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * (((c : ℝ) - b) / D) ^ 2
        ≤ 1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * ((c : ℝ) * ((c : ℝ) - b) / D ^ 2) by
          linarith) hw
    calc kc2 b * (poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * (((c : ℝ) - b) / D) ^ 2))
        = kc2 b * poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / D) + 3 / 8 * (((c : ℝ) - b) / D) ^ 2) := by ring
      _ ≤ _ := h
      _ = _ := by ring
  refine (Finset.sum_le_sum h1).trans (le_of_eq ?_)
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, kc3_mom_left c]
  unfold kc3
  ring

/-- `ϱ_c ≥ 0` for a cut point `c ≤ R`. -/
theorem rhoC_nonneg {k R c : ℕ} (hc : c ≤ R) : 0 ≤ rhoC ((k : ℝ) + R) c := by
  have hd : (0 : ℝ) ≤ (k : ℝ) + R - c := by
    have h1 : (c : ℝ) ≤ R := Nat.cast_le.2 hc
    have h2 : (0 : ℝ) ≤ k := Nat.cast_nonneg k
    linarith
  unfold rhoC
  positivity

/-- The vertices below `b`:
`∑_{b≤R} κ₂(b) · (mean of log (t/k) over the vertices of size t > k below b)`
`≤ ∑_{0<c<R} κ₃(c) · (1 + ϱ_c) · (α + β (R-c))`.  The mean is rewritten as a sum over the cut
points `c > b` (`below_sum_reindex`), each weight is bounded by `below_weight_le`, and the sums
over `b < c` are exchanged (`below_weight_sum`). -/
private theorem exp_row_below {k R : ℕ} (hk : 1 ≤ k) {α β : ℝ}
    (hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y) :
    ∑ b ∈ Icc 1 R, kc2 b
        * ((∑ t ∈ Ioo k (k + R - b), ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k)))
            / cay (k + R - b))
      ≤ ∑ c ∈ Ioo 0 R, kc3 c * (1 + rhoC ((k : ℝ) + R) c) * (α + β * ((R : ℝ) - c)) := by
  have hk0 : (0 : ℝ) < k := Nat.cast_pos.mpr (by omega)
  -- the bound for one `b`
  have h1 : ∀ b ∈ Icc 1 R, kc2 b
        * ((∑ t ∈ Ioo k (k + R - b), ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k)))
            / cay (k + R - b))
      ≤ ∑ c ∈ Ioo b R, kc2 b * (poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / ((k : ℝ) + R - c))
            + 3 / 8 * (((c : ℝ) - b) / ((k : ℝ) + R - c)) ^ 2)) * logExc k ((R : ℝ) - c) := by
    intro b hb
    rw [below_sum_reindex hk (mem_Icc.1 hb).2, Finset.sum_div, Finset.mul_sum]
    refine Finset.sum_le_sum fun c hc => ?_
    rw [mem_Ioo] at hc
    have hLx : 0 ≤ logExc k ((R : ℝ) - c) :=
      logExc_nonneg (sub_nonneg.2 (Nat.cast_le.2 hc.2.le))
    have h := mul_le_mul_of_nonneg_left
      (mul_le_mul_of_nonneg_right (below_weight_le hk hc.1 hc.2) hLx) (kc2_nonneg b)
    calc kc2 b * (ren (c - b) * cay (k + R - c) * logExc k ((R : ℝ) - c) / cay (k + R - b))
        = kc2 b * (ren (c - b) * cay (k + R - c) / cay (k + R - b)
            * logExc k ((R : ℝ) - c)) := by ring
      _ ≤ _ := h
      _ = _ := by ring
  -- exchange the two sums
  have h2 : ∑ b ∈ Icc 1 R, ∑ c ∈ Ioo b R, kc2 b * (poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / ((k : ℝ) + R - c))
            + 3 / 8 * (((c : ℝ) - b) / ((k : ℝ) + R - c)) ^ 2)) * logExc k ((R : ℝ) - c)
      = ∑ c ∈ Ioo 0 R, ∑ b ∈ Ioo 0 c, kc2 b * (poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / ((k : ℝ) + R - c))
            + 3 / 8 * (((c : ℝ) - b) / ((k : ℝ) + R - c)) ^ 2)) * logExc k ((R : ℝ) - c) :=
    Finset.sum_comm' (by intro x y; simp only [mem_Icc, mem_Ioo]; omega)
  -- the bound for one `c`
  have h3 : ∀ c ∈ Ioo 0 R, ∑ b ∈ Ioo 0 c, kc2 b * (poissonMass (c - b)
          * (1 + 3 / 2 * (((c : ℝ) - b) / ((k : ℝ) + R - c))
            + 3 / 8 * (((c : ℝ) - b) / ((k : ℝ) + R - c)) ^ 2)) * logExc k ((R : ℝ) - c)
      ≤ kc3 c * (1 + rhoC ((k : ℝ) + R) c) * (α + β * ((R : ℝ) - c)) := by
    intro c hc
    rw [mem_Ioo] at hc
    have hcR : (0 : ℝ) ≤ (R : ℝ) - c := sub_nonneg.2 (Nat.cast_le.2 hc.2.le)
    have hw := below_weight_sum c (D := (k : ℝ) + R - c) (by linarith)
    have hV : 0 ≤ kc3 c * (1 + rhoC ((k : ℝ) + R) c) :=
      mul_nonneg (kc3_nonneg c) (by linarith [rhoC_nonneg (k := k) hc.2.le])
    rw [← Finset.sum_mul]
    exact (mul_le_mul_of_nonneg_right hw (logExc_nonneg hcR)).trans
      (mul_le_mul_of_nonneg_left (hL _ hcR) hV)
  exact (Finset.sum_le_sum h1).trans (h2.le.trans (Finset.sum_le_sum h3))

/-- **The sum of the exponents.** For `θ ≥ 0`,
`∑_{b≤R} ∑_{0<a<b} P(a) P(b-a) · X_{ab} ≤ (log (1+θ) - θ/(1+θ)) · G + 𝒜/(k(1+θ))`.
The six parts of the exponent are bounded by the five rows above, for the tangent of the logarithm
at `θ`, and added. -/
private theorem pairExp_sum_le {k R : ℕ} (hk : 1 ≤ k) (θ : ℝ) (hθ : 0 ≤ θ) :
    ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * pairExp k R a b
      ≤ (Real.log (1 + θ) - θ / (1 + θ)) * Gsum k R + 1 / ((k : ℝ) * (1 + θ)) * Asum k R := by
  obtain ⟨α, hα⟩ : ∃ α : ℝ, α = Real.log (1 + θ) - θ / (1 + θ) := ⟨_, rfl⟩
  obtain ⟨β, hβ⟩ : ∃ β : ℝ, β = 1 / ((k : ℝ) * (1 + θ)) := ⟨_, rfl⟩
  have hL : ∀ y : ℝ, 0 ≤ y → logExc k y ≤ α + β * y := fun y hy => by
    rw [hα, hβ]
    exact logExc_le_tangent hk hθ hy
  rw [← hα, ← hβ]
  have hrow : ∀ b ∈ Icc 1 R,
      ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * pairExp k R a b
      ≤ α * (7 / 2 * kc2 b + 2 * kc3 b)
        + β * (((R : ℝ) - (b : ℝ) / 2) * (kc2 b + 2 * kc3 b) + 5 / 2 * ((R : ℝ) - b) * kc2 b)
        + kc2 b * ((∑ t ∈ Ioo k (k + R - b),
            ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k))) / cay (k + R - b)) := by
    intro b hb
    have hbR := (mem_Icc.1 hb).2
    have hsplit : ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * pairExp k R a b
        = ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
              * ((∑ c ∈ Ioo 0 a, ren (a - c) * (ren c * logExc k ((R : ℝ) - c))) / ren a)
          + ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a) * logExc k ((R : ℝ) - a)
          + ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
              * ((∑ c ∈ Ioo 0 (b - a), ren (b - a - c) * (ren c * logExc k ((R : ℝ) - a - c)))
                  / ren (b - a))
          + ∑ a ∈ Ioo 0 b, poissonMass a * poissonMass (b - a)
              * (logExc k ((R : ℝ) - b)
                + Real.log (cay k * Real.exp ((R : ℝ) - b) / cay (k + R - b)))
          + kc2 b * ((∑ t ∈ Ioo k (k + R - b),
              ren (k + R - b - t) * (cay t * Real.log ((t : ℝ) / k))) / cay (k + R - b)) := by
      unfold kc2
      rw [Finset.sum_mul, ← Finset.sum_add_distrib, ← Finset.sum_add_distrib,
        ← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
      refine Finset.sum_congr rfl fun a _ => ?_
      unfold pairExp
      ring
    have r1 := exp_row_point hL (ρ := (R : ℝ)) (b := b) (Nat.cast_le.2 hbR)
    have r2 := exp_row_above hL hbR
    have r3 := exp_row_between hL hbR
    have r4 := exp_row_end hk hbR hL
    rw [hsplit]
    linarith
  have h4 := exp_row_below (R := R) hk hL
  have hlast : ∑ c ∈ Ioo 0 R, kc3 c * (1 + rhoC ((k : ℝ) + R) c) * (α + β * ((R : ℝ) - c))
      = α * ∑ c ∈ Ioo 0 R, kc3 c * (1 + rhoC ((k : ℝ) + R) c)
        + β * ∑ c ∈ Ioo 0 R, ((R : ℝ) - c) * kc3 c * (1 + rhoC ((k : ℝ) + R) c) := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  have hsum := Finset.sum_le_sum hrow
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum] at hsum
  unfold Gsum Asum
  rw [hlast] at h4
  linarith

/-! ### The lower bound of the pair sum -/

/-- **The lower bound of the pair sum.** For `1 ≤ k`, `R ≤ k`, and all real `θ ≥ 0` and `μ`,
`a_k · e^R · e^{-μ} · ((1+μ) · W_Σ - (α · G + β · 𝒜)) ≤ pairSum k R` with
`α = log (1+θ) - θ/(1+θ)` and `β = 1/(k(1+θ))`.  Each pair term is at least
`a_k e^R · P(a) P(b-a) · e^{-X_{ab}}` (`pair_term_ge`), `e^{-X} ≥ e^{-μ}(1 + μ - X)`, the weights
`P(a) P(b-a)` sum to `W_Σ`, and the weighted exponents sum to at most `α G + β 𝒜`
(`pairExp_sum_le`). -/
theorem pairSum_ge {k R : ℕ} (hk : 1 ≤ k) (hR : R ≤ k) (θ μ : ℝ) (hθ : 0 ≤ θ) :
    cay k * Real.exp (R : ℝ) * (Real.exp (-μ) * ((1 + μ) * Wsum R
        - ((Real.log (1 + θ) - θ / (1 + θ)) * Gsum k R + 1 / ((k : ℝ) * (1 + θ)) * Asum k R)))
      ≤ pairSum k R := by
  have hC : 0 ≤ cay k * Real.exp (R : ℝ) := (mul_pos (cay_pos (by omega)) (Real.exp_pos _)).le
  -- one pair, with the tangent of the exponential at `μ`
  have hT : ∀ b ∈ Icc 1 R, ∀ a ∈ Ioo 0 b,
      cay k * Real.exp (R : ℝ) * (Real.exp (-μ) * ((1 + μ) * (poissonMass a * poissonMass (b - a))
          - poissonMass a * poissonMass (b - a) * pairExp k R a b))
        ≤ Lam (thr (k : ℝ) ((k : ℝ) + R)) a * thr (k : ℝ) ((k : ℝ) + R) a
          * Lam (fun s => thr (k : ℝ) ((k : ℝ) + R) (a + s)) (b - a)
          * thr (k : ℝ) ((k : ℝ) + R) b * zr k (k + R - b - 1) := by
    intro b hb a ha
    rw [mem_Ioo] at ha
    refine le_trans ?_ (pair_term_ge hk hR ha.1 ha.2 (mem_Icc.1 hb).2)
    have h2 : Real.exp (-μ) * (1 + μ - pairExp k R a b) ≤ Real.exp (-(pairExp k R a b)) := by
      have h3 := mul_le_mul_of_nonneg_left (Real.add_one_le_exp (μ - pairExp k R a b))
        (Real.exp_pos (-μ)).le
      rw [← Real.exp_add, show -μ + (μ - pairExp k R a b) = -(pairExp k R a b) by ring] at h3
      linarith
    have h5 : 0 ≤ poissonMass a * poissonMass (b - a) :=
      mul_nonneg (poissonMass_pos a).le (poissonMass_pos (b - a)).le
    have h7 := mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left h2 h5) hC
    linarith
  -- the sum over the pairs
  have hP : pairSum k R = ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b,
      Lam (thr (k : ℝ) ((k : ℝ) + R)) a * thr (k : ℝ) ((k : ℝ) + R) a
        * Lam (fun s => thr (k : ℝ) ((k : ℝ) + R) (a + s)) (b - a)
        * thr (k : ℝ) ((k : ℝ) + R) b * zr k (k + R - b - 1) := by
    unfold pairSum Lam1
    exact Finset.sum_congr rfl fun b _ => by rw [Finset.sum_mul, Finset.sum_mul]
  have hS : ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b,
      cay k * Real.exp (R : ℝ) * (Real.exp (-μ) * ((1 + μ) * (poissonMass a * poissonMass (b - a))
          - poissonMass a * poissonMass (b - a) * pairExp k R a b))
      = cay k * Real.exp (R : ℝ) * (Real.exp (-μ) * ((1 + μ) * Wsum R
          - ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b,
              poissonMass a * poissonMass (b - a) * pairExp k R a b)) := by
    have e1 : (1 + μ) * Wsum R - ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b,
          poissonMass a * poissonMass (b - a) * pairExp k R a b
        = ∑ b ∈ Icc 1 R, ∑ a ∈ Ioo 0 b, ((1 + μ) * (poissonMass a * poissonMass (b - a))
            - poissonMass a * poissonMass (b - a) * pairExp k R a b) := by
      unfold Wsum kc2
      rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
      exact Finset.sum_congr rfl fun b _ => by rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    rw [e1]
    simp only [Finset.mul_sum]
  have hsum := Finset.sum_le_sum fun b hb => Finset.sum_le_sum fun a ha => hT b hb a ha
  rw [hS, ← hP] at hsum
  refine le_trans ?_ hsum
  refine mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left ?_ (Real.exp_pos _).le) hC
  linarith [pairExp_sum_le (R := R) hk θ hθ]

end Parking
