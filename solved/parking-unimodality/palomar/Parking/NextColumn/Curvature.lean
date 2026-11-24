module

public import Parking.NextColumn.Birthday
public import Parking.NextColumn.Frozen
public import Mathlib.Analysis.Calculus.Deriv.Polynomial
public import Mathlib.Analysis.Convex.Deriv
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Tactic.IntervalCases

/-!
# The curvature ratio

With `K = Kpoly k n` (a polynomial in `y` with nonnegative coefficients), `n = k + r` a first-layer
position, the second differences `C_- = K(k+1) - 2K(k) + K(k-1)` and `C_+ = K(k+2) - 2K(k+1) + K(k)`
satisfy `C_+ ≤ e^{D_r/(k-1)} C_-` (`curv_ratio`).

Structure of the file (all auxiliary statements live in the namespace `Parking.Curv`):

* Part A (pure calculus, no parking functions): `Curv.curv_calculus` (Grönwall + convexity for a
  function with three explicit derivatives) and `Curv.poly_curv_le` (the same for
  `y ↦ c0 + ∑_{q ∈ s} p_q y^q` with `p ≥ 0`, where the hypothesis becomes a moment inequality).
* Part B: `Curv.Kpoly_eq_poly` (polynomial form of `Kpoly`), `Curv.pcoef_nonneg`, and the moment
  inequality `Curv.moment_star`, obtained for each `m` from a likelihood-ratio comparison of the
  number of parts under the threshold profile with the birthday law (`Curv.moment_m`).
* `curv_ratio`: assembly.
-/

@[expose] public section

namespace Parking

open Finset

namespace Curv

/-! ## Part A: abstract calculus -/

/-- `polyF s c j y = ∑_{q ∈ s} c_q y^(q-j)` (truncated subtraction in the exponent). -/
private noncomputable def polyF (s : Finset ℕ) (c : ℕ → ℝ) (j : ℕ) (y : ℝ) : ℝ :=
  ∑ q ∈ s, c q * y ^ (q - j)

/-- Coefficients of the derivative of `polyF s c j`. -/
private noncomputable def dcoef (c : ℕ → ℝ) (j : ℕ) : ℕ → ℝ := fun q => c q * ((q - j : ℕ) : ℝ)

private theorem polyF_hasDerivAt (s : Finset ℕ) (c : ℕ → ℝ) (j : ℕ) (y : ℝ) :
    HasDerivAt (polyF s c j) (polyF s (dcoef c j) (j + 1) y) y := by
  have h : ∀ q ∈ s, HasDerivAt (fun t : ℝ => c q * t ^ (q - j))
      (c q * (((q - j : ℕ) : ℝ) * y ^ (q - j - 1))) y :=
    fun q _ => (hasDerivAt_pow (q - j) y).const_mul (c q)
  have h2 := HasDerivAt.fun_sum h
  have e : polyF s (dcoef c j) (j + 1) y
      = ∑ q ∈ s, c q * (((q - j : ℕ) : ℝ) * y ^ (q - j - 1)) := by
    unfold polyF
    refine Finset.sum_congr rfl (fun q _ => ?_)
    show c q * ((q - j : ℕ) : ℝ) * y ^ (q - (j + 1))
      = c q * (((q - j : ℕ) : ℝ) * y ^ (q - j - 1))
    rw [Nat.sub_sub]
    ring
  rw [e]
  exact h2

private theorem polyF_nonneg {s : Finset ℕ} {c : ℕ → ℝ} (hc : ∀ q ∈ s, 0 ≤ c q) (j : ℕ) {y : ℝ}
    (hy : 0 ≤ y) : 0 ≤ polyF s c j y :=
  Finset.sum_nonneg (fun q hq => mul_nonneg (hc q hq) (pow_nonneg hy _))

private theorem dcoef_nonneg {c : ℕ → ℝ} {q : ℕ} (hc : 0 ≤ c q) (j : ℕ) : 0 ≤ dcoef c j q :=
  mul_nonneg hc (Nat.cast_nonneg _)

private theorem mono2 (q : ℕ) (y : ℝ) :
    y ^ 2 * (((q - 0 : ℕ) : ℝ) * ((q - 1 : ℕ) : ℝ) * y ^ (q - 2))
      = (q : ℝ) * ((q : ℝ) - 1) * y ^ q := by
  rcases Nat.lt_or_ge q 2 with h | h
  · interval_cases q <;> norm_num
  · obtain ⟨q', rfl⟩ : ∃ q', q = q' + 2 := ⟨q - 2, by omega⟩
    have e1 : q' + 2 - 0 = q' + 2 := by omega
    have e2 : q' + 2 - 1 = q' + 1 := by omega
    have e3 : q' + 2 - 2 = q' := by omega
    rw [e1, e2, e3]
    push_cast
    ring

private theorem mono3 (q : ℕ) (y : ℝ) :
    y ^ 3 * (((q - 0 : ℕ) : ℝ) * ((q - 1 : ℕ) : ℝ) * ((q - 2 : ℕ) : ℝ) * y ^ (q - 3))
      = (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * y ^ q := by
  rcases Nat.lt_or_ge q 3 with h | h
  · interval_cases q <;> norm_num
  · obtain ⟨q', rfl⟩ : ∃ q', q = q' + 3 := ⟨q - 3, by omega⟩
    have e1 : q' + 3 - 0 = q' + 3 := by omega
    have e2 : q' + 3 - 1 = q' + 2 := by omega
    have e3 : q' + 3 - 2 = q' + 1 := by omega
    have e4 : q' + 3 - 3 = q' := by omega
    rw [e1, e2, e3, e4]
    push_cast
    ring

private theorem polyF_two (s : Finset ℕ) (p : ℕ → ℝ) (y : ℝ) :
    y ^ 2 * polyF s (dcoef (dcoef p 0) 1) 2 y
      = ∑ q ∈ s, ((q : ℝ) * ((q : ℝ) - 1)) * (p q * y ^ q) := by
  unfold polyF
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl (fun q _ => ?_)
  have h := mono2 q y
  show y ^ 2 * (p q * ((q - 0 : ℕ) : ℝ) * ((q - 1 : ℕ) : ℝ) * y ^ (q - 2))
    = ((q : ℝ) * ((q : ℝ) - 1)) * (p q * y ^ q)
  linear_combination p q * h

private theorem polyF_three (s : Finset ℕ) (p : ℕ → ℝ) (y : ℝ) :
    y ^ 3 * polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y
      = ∑ q ∈ s, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) * (p q * y ^ q) := by
  unfold polyF
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl (fun q _ => ?_)
  have h := mono3 q y
  show y ^ 3 * (p q * ((q - 0 : ℕ) : ℝ) * ((q - 1 : ℕ) : ℝ) * ((q - 2 : ℕ) : ℝ) * y ^ (q - 3))
    = ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) * (p q * y ^ q)
  linear_combination p q * h

/-- **Grönwall + convexity.** If `G0' = G1`, `G1' = G2`, `G2' = G3`, and on `[x-1, x+2]` we have
`G3 ≥ 0` and `y G3(y) ≤ D G2(y)`, then the second difference of `G0` at `x+1` is at most
`e^{D/(x-1)}` times the second difference at `x`. -/
private theorem curv_calculus {G0 G1 G2 G3 : ℝ → ℝ} {x D : ℝ} (hx : 1 < x)
    (h01 : ∀ y, HasDerivAt G0 (G1 y) y) (h12 : ∀ y, HasDerivAt G1 (G2 y) y)
    (h23 : ∀ y, HasDerivAt G2 (G3 y) y)
    (hG3 : ∀ y, x - 1 ≤ y → y ≤ x + 2 → 0 ≤ G3 y)
    (hstar : ∀ y, x - 1 ≤ y → y ≤ x + 2 → y * G3 y ≤ D * G2 y) :
    G0 (x + 2) - 2 * G0 (x + 1) + G0 x
      ≤ Real.exp (D / (x - 1)) * (G0 (x + 1) - 2 * G0 x + G0 (x - 1)) := by
  have hx1 : 0 < x - 1 := by linarith
  obtain ⟨c, hc⟩ : ∃ c : ℝ, c = D / (x - 1) := ⟨_, rfl⟩
  rw [← hc]
  -- Step 1: `G3 ≤ c G2` on `[x-1, x+2]`.
  have hG3le : ∀ y, x - 1 ≤ y → y ≤ x + 2 → G3 y ≤ c * G2 y := by
    intro y hy1 hy2
    have h1 := hstar y hy1 hy2
    have h2 := hG3 y hy1 hy2
    have h3 : (x - 1) * G3 y ≤ y * G3 y := mul_le_mul_of_nonneg_right hy1 h2
    rw [hc, div_mul_eq_mul_div, le_div_iff₀ hx1]
    linarith
  -- Step 2: `t ↦ e^{-ct} G2 t` is antitone on `[x-1, x+2]`.
  have hd : ∀ t, HasDerivAt (fun t => Real.exp (-(c * t)) * G2 t)
      (Real.exp (-(c * t)) * (-c) * G2 t + Real.exp (-(c * t)) * G3 t) t := by
    intro t
    have h1 : HasDerivAt (fun t : ℝ => -(c * t)) (-c) t := (hasDerivAt_const_mul c).fun_neg
    exact h1.exp.fun_mul (h23 t)
  have hφ : AntitoneOn (fun t => Real.exp (-(c * t)) * G2 t) (Set.Icc (x - 1) (x + 2)) := by
    refine antitoneOn_of_hasDerivWithinAt_nonpos
      (f' := fun t => Real.exp (-(c * t)) * (-c) * G2 t + Real.exp (-(c * t)) * G3 t)
      (convex_Icc _ _) (fun t _ => (hd t).continuousAt.continuousWithinAt)
      (fun t _ => (hd t).hasDerivWithinAt) ?_
    intro t ht
    rw [interior_Icc] at ht
    have h1 := hG3le t ht.1.le ht.2.le
    have h2 : 0 < Real.exp (-(c * t)) := Real.exp_pos _
    have h3 := mul_le_mul_of_nonneg_left h1 h2.le
    show Real.exp (-(c * t)) * (-c) * G2 t + Real.exp (-(c * t)) * G3 t ≤ 0
    linarith
  -- Step 3: `G2 (y+1) ≤ e^c G2 y` for `y ∈ [x-1, x+1]`.
  have hstep : ∀ y, x - 1 ≤ y → y ≤ x + 1 → G2 (y + 1) ≤ Real.exp c * G2 y := by
    intro y hy1 hy2
    have h1 : Real.exp (-(c * (y + 1))) * G2 (y + 1) ≤ Real.exp (-(c * y)) * G2 y :=
      hφ (Set.mem_Icc.mpr ⟨hy1, by linarith⟩) (Set.mem_Icc.mpr ⟨by linarith, by linarith⟩)
        (by linarith)
    have e : Real.exp (-(c * y)) = Real.exp (-(c * (y + 1))) * Real.exp c := by
      rw [← Real.exp_add]
      congr 1
      ring
    rw [e, mul_assoc] at h1
    exact le_of_mul_le_mul_left h1 (Real.exp_pos _)
  -- Step 4: `H t = e^c G0 t - G0 (t+1)` is convex on `[x-1, x+1]`.
  have hH : ∀ y, HasDerivAt (fun t => Real.exp c * G0 t - G0 (t + 1))
      (Real.exp c * G1 y - G1 (y + 1)) y :=
    fun y => ((h01 y).const_mul (Real.exp c)).fun_sub ((h01 (y + 1)).comp_add_const y 1)
  have hH' : ∀ y, HasDerivAt (fun t => Real.exp c * G1 t - G1 (t + 1))
      (Real.exp c * G2 y - G2 (y + 1)) y :=
    fun y => ((h12 y).const_mul (Real.exp c)).fun_sub ((h12 (y + 1)).comp_add_const y 1)
  have hconv : ConvexOn ℝ (Set.Icc (x - 1) (x + 1))
      (fun t => Real.exp c * G0 t - G0 (t + 1)) := by
    refine convexOn_of_hasDerivWithinAt2_nonneg
      (f' := fun t => Real.exp c * G1 t - G1 (t + 1))
      (f'' := fun t => Real.exp c * G2 t - G2 (t + 1))
      (convex_Icc _ _) (fun t _ => (hH t).continuousAt.continuousWithinAt)
      (fun t _ => (hH t).hasDerivWithinAt) (fun t _ => (hH' t).hasDerivWithinAt) ?_
    intro t ht
    rw [interior_Icc] at ht
    have h1 := hstep t ht.1.le ht.2.le
    show 0 ≤ Real.exp c * G2 t - G2 (t + 1)
    linarith
  -- Step 5: midpoint inequality.
  have hmid : (fun t => Real.exp c * G0 t - G0 (t + 1))
        ((1 / 2 : ℝ) • (x - 1) + (1 / 2 : ℝ) • (x + 1))
      ≤ (1 / 2 : ℝ) • (fun t => Real.exp c * G0 t - G0 (t + 1)) (x - 1)
        + (1 / 2 : ℝ) • (fun t => Real.exp c * G0 t - G0 (t + 1)) (x + 1) :=
    hconv.2 (Set.mem_Icc.mpr ⟨le_refl _, by linarith⟩) (Set.mem_Icc.mpr ⟨by linarith, le_refl _⟩)
      (by norm_num) (by norm_num) (by norm_num)
  have e1 : (1 / 2 : ℝ) • (x - 1) + (1 / 2 : ℝ) • (x + 1) = x := by
    simp only [smul_eq_mul]
    ring
  rw [e1] at hmid
  simp only [smul_eq_mul] at hmid
  have e2 : x - 1 + 1 = x := by ring
  have e3 : x + 1 + 1 = x + 2 := by ring
  rw [e2, e3] at hmid
  have e4 : Real.exp c * (G0 (x + 1) - 2 * G0 x + G0 (x - 1))
      = Real.exp c * G0 (x + 1) - 2 * (Real.exp c * G0 x) + Real.exp c * G0 (x - 1) := by ring
  rw [e4]
  linarith

/-- The curvature ratio for a polynomial with nonnegative coefficients satisfying the moment
inequality `(*)` on `[x-1, x+2]`. -/
private theorem poly_curv_le (s : Finset ℕ) (p : ℕ → ℝ) (c0 D x : ℝ)
    (hp : ∀ q ∈ s, 0 ≤ p q) (hx : 1 < x)
    (hstar : ∀ y : ℝ, x - 1 ≤ y → y ≤ x + 2 →
      ∑ q ∈ s, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) * (p q * y ^ q)
        ≤ D * ∑ q ∈ s, ((q : ℝ) * ((q : ℝ) - 1)) * (p q * y ^ q))
    (K : ℝ → ℝ) (hK : ∀ y, K y = c0 + ∑ q ∈ s, p q * y ^ q) :
    K (x + 2) - 2 * K (x + 1) + K x
      ≤ Real.exp (D / (x - 1)) * (K (x + 1) - 2 * K x + K (x - 1)) := by
  have hc1 : ∀ q ∈ s, 0 ≤ dcoef p 0 q := fun q hq => dcoef_nonneg (hp q hq) 0
  have hc2 : ∀ q ∈ s, 0 ≤ dcoef (dcoef p 0) 1 q := fun q hq => dcoef_nonneg (hc1 q hq) 1
  have hc3 : ∀ q ∈ s, 0 ≤ dcoef (dcoef (dcoef p 0) 1) 2 q :=
    fun q hq => dcoef_nonneg (hc2 q hq) 2
  have h01 : ∀ y, HasDerivAt (polyF s p 0) (polyF s (dcoef p 0) 1 y) y :=
    fun y => polyF_hasDerivAt s p 0 y
  have h12 : ∀ y, HasDerivAt (polyF s (dcoef p 0) 1) (polyF s (dcoef (dcoef p 0) 1) 2 y) y :=
    fun y => polyF_hasDerivAt s (dcoef p 0) 1 y
  have h23 : ∀ y, HasDerivAt (polyF s (dcoef (dcoef p 0) 1) 2)
      (polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y) y :=
    fun y => polyF_hasDerivAt s (dcoef (dcoef p 0) 1) 2 y
  have hG3 : ∀ y, x - 1 ≤ y → y ≤ x + 2 → 0 ≤ polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y :=
    fun y hy1 _ => polyF_nonneg hc3 3 (by linarith)
  have hst : ∀ y, x - 1 ≤ y → y ≤ x + 2 →
      y * polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y
        ≤ D * polyF s (dcoef (dcoef p 0) 1) 2 y := by
    intro y hy1 hy2
    have hy0 : 0 < y := by linarith
    have h := hstar y hy1 hy2
    rw [← polyF_two s p y, ← polyF_three s p y] at h
    have hy2' : 0 < y ^ 2 := by positivity
    have h' : y ^ 2 * (y * polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y)
        ≤ y ^ 2 * (D * polyF s (dcoef (dcoef p 0) 1) 2 y) := by
      calc y ^ 2 * (y * polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y)
          = y ^ 3 * polyF s (dcoef (dcoef (dcoef p 0) 1) 2) 3 y := by ring
        _ ≤ D * (y ^ 2 * polyF s (dcoef (dcoef p 0) 1) 2 y) := h
        _ = y ^ 2 * (D * polyF s (dcoef (dcoef p 0) 1) 2 y) := by ring
    exact le_of_mul_le_mul_left h' hy2'
  have key := curv_calculus (D := D) hx h01 h12 h23 hG3 hst
  have hK' : ∀ y, K y = c0 + polyF s p 0 y := by
    intro y
    rw [hK]
    simp [polyF]
  have e1 : ∀ a b c : ℝ, c0 + a - 2 * (c0 + b) + (c0 + c) = a - 2 * b + c :=
    fun a b c => by ring
  simp only [hK', e1]
  exact key

/-! ## Part B: the frozen polynomial -/

/-- `c_m = κ_k(N-m)/(N-m)`, `N = k+r+1`. -/
private noncomputable def ccoef (k r m : ℕ) : ℝ :=
  kap k (k + r + 1 - m) / (((k + r : ℕ) : ℝ) + 1 - (m : ℝ))

/-- `p_q = ∑_{m=1}^r c_m V_{m,q}` (`V_{m,q} = 0` for `q > m`). -/
private noncomputable def pcoef (k r q : ℕ) : ℝ :=
  ∑ m ∈ Icc 1 r, ccoef k r m * Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m

/-- Exchange of summation, with a weight `w q`. -/
private theorem sum_swap_aux (r : ℕ) (c : ℕ → ℝ) (V : ℕ → ℕ → ℝ) (hV : ∀ m q, m < q → V m q = 0)
    (w : ℕ → ℝ) (y : ℝ) :
    ∑ m ∈ Icc 1 r, c m * y * ∑ q ∈ Icc 1 m, w q * (y ^ (q - 1) * V m q)
      = ∑ q ∈ Icc 1 r, w q * ((∑ m ∈ Icc 1 r, c m * V m q) * y ^ q) := by
  have h1 : ∀ m ∈ Icc 1 r, c m * y * ∑ q ∈ Icc 1 m, w q * (y ^ (q - 1) * V m q)
      = ∑ q ∈ Icc 1 r, w q * (c m * V m q * y ^ q) := by
    intro m hm
    have hmr : m ≤ r := (Finset.mem_Icc.mp hm).2
    rw [Finset.mul_sum]
    have h2 : ∀ q ∈ Icc 1 m, c m * y * (w q * (y ^ (q - 1) * V m q))
        = w q * (c m * V m q * y ^ q) := by
      intro q hq
      have hq1 : q ≠ 0 := by
        have := (Finset.mem_Icc.mp hq).1
        omega
      rw [← mul_pow_sub_one hq1 y]
      ring
    rw [Finset.sum_congr rfl h2]
    refine Finset.sum_subset (Finset.Icc_subset_Icc_right hmr) ?_
    intro q hq hq'
    have hlt : m < q := by
      rw [Finset.mem_Icc] at hq hq'
      omega
    rw [hV m q hlt]
    ring
  rw [Finset.sum_congr rfl h1, Finset.sum_comm]
  refine Finset.sum_congr rfl (fun q _ => ?_)
  rw [Finset.sum_mul, Finset.mul_sum]

/-- Polynomial form of the frozen polynomial at `n = k + r`. -/
private theorem Kpoly_eq_poly (k r : ℕ) (y : ℝ) :
    Kpoly k (k + r) y = kap k (k + r + 1) + ∑ q ∈ Icc 1 r, pcoef k r q * y ^ q := by
  have h : ∑ m ∈ Icc 1 r, ccoef k r m * y
        * ∑ q ∈ Icc 1 m, 1 * (y ^ (q - 1) * Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m)
      = ∑ q ∈ Icc 1 r, 1 * (pcoef k r q * y ^ q) :=
    sum_swap_aux r (ccoef k r) (fun m q => Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m)
      (fun m q hlt => Vc_eq_zero_of_lt _ hlt) (fun _ => 1) y
  simp only [one_mul] at h
  have h2 : ∀ m ∈ Icc 1 r, kap k (k + r + 1 - m) / (((k + r : ℕ) : ℝ) + 1 - (m : ℝ)) * y
        * Lam (thr y (((k + r : ℕ) : ℝ) + 1)) m
      = ccoef k r m * y
        * ∑ q ∈ Icc 1 m, y ^ (q - 1) * Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m := by
    intro m _
    rw [Lam_thr]
    rfl
  unfold Kpoly
  rw [Nat.add_sub_cancel_left, Finset.sum_congr rfl h2, h]

private theorem ccoef_pos {k r m : ℕ} (hr2 : r ≤ k - 1) (hm1 : 1 ≤ m) (hmr : m ≤ r) :
    0 < ccoef k r m := by
  unfold ccoef
  apply div_pos
  · exact kap_pos (by omega) (by omega)
  · have h : (m : ℝ) ≤ ((k + r : ℕ) : ℝ) := Nat.cast_le.mpr (by omega)
    linarith

private theorem pcoef_nonneg {k r : ℕ} (hr2 : r ≤ k - 1) (q : ℕ) : 0 ≤ pcoef k r q := by
  unfold pcoef
  refine Finset.sum_nonneg (fun m hm => ?_)
  rw [Finset.mem_Icc] at hm
  refine mul_nonneg (ccoef_pos hr2 hm.1 hm.2).le
    (Vc_nonneg (fun s hs => thr_nonneg zero_le_one ?_) q)
  have h : (s : ℝ) ≤ ((k + r : ℕ) : ℝ) := Nat.cast_le.mpr (by have := Finset.mem_Ioo.mp hs; omega)
  linarith

/-- The moment inequality for one `m ≥ 2` (likelihood-ratio comparison with the birthday law). -/
private theorem moment_m {m : ℕ} (hm2 : 2 ≤ m) {y N : ℝ} (hy0 : 0 < y)
    (hN : ∀ s ∈ Ioo 0 m, y ≤ N - (s : ℝ)) :
    ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2))
        * (y ^ (q - 1) * Vc (thr 1 N) q m)
      ≤ Dbirth m * ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1)) * (y ^ (q - 1) * Vc (thr 1 N) q m) := by
  have hf : ∀ s ∈ Ioo 0 m, 0 ≤ thr y N s ∧ thr y N s ≤ 1 := by
    intro s hs
    have h1 := hN s hs
    have h2 : 0 < N - (s : ℝ) := lt_of_lt_of_le hy0 h1
    exact ⟨div_nonneg hy0.le h2.le, (div_le_one h2).mpr h1⟩
  have hcons : ∀ q, 1 ≤ q → q + 1 ≤ m →
      Vc (thr y N) (q + 1) m * Tq m q ≤ Vc (thr y N) q m * Tq m (q + 1) := by
    intro q hq hqm
    have h1 := Vc_ratio_le hf hq
    have h2 := Tq_ratio m hq
    have hq0 : (0 : ℝ) < (q : ℝ) := Nat.cast_pos.mpr (by omega)
    have hm0 : (0 : ℝ) < (m : ℝ) := Nat.cast_pos.mpr (by omega)
    have hqm_pos : (0 : ℝ) < (q : ℝ) * m := mul_pos hq0 hm0
    have hT : 0 ≤ Tq m q := Tq_nonneg m q
    have h3 : (q : ℝ) * m * (Vc (thr y N) (q + 1) m * Tq m q)
        ≤ (q : ℝ) * m * (Vc (thr y N) q m * Tq m (q + 1)) := by
      calc (q : ℝ) * m * (Vc (thr y N) (q + 1) m * Tq m q)
          = ((q : ℝ) * m * Vc (thr y N) (q + 1) m) * Tq m q := by ring
        _ ≤ (((q : ℝ) + 1) * ((m : ℝ) - q) * Vc (thr y N) q m) * Tq m q :=
            mul_le_mul_of_nonneg_right h1 hT
        _ = Vc (thr y N) q m * (((q : ℝ) + 1) * ((m : ℝ) - q) * Tq m q) := by ring
        _ = Vc (thr y N) q m * ((q : ℝ) * m * Tq m (q + 1)) := by rw [h2]
        _ = (q : ℝ) * m * (Vc (thr y N) q m * Tq m (q + 1)) := by ring
    exact le_of_mul_le_mul_left h3 hqm_pos
  have hlr : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ m →
      Vc (thr y N) q' m * Tq m q ≤ Vc (thr y N) q m * Tq m q' :=
    lr_of_consecutive m (fun q => Vc (thr y N) q m) (fun q => Tq m q)
      (fun q hq => Tq_pos (Finset.mem_Icc.mp hq).1 (Finset.mem_Icc.mp hq).2) hcons
  have key : (∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Vc (thr y N) q m)
        * (∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q)
      ≤ (∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q)
        * (∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Vc (thr y N) q m) :=
    lr_factorial_moment_le m (fun q => Vc (thr y N) q m) (Tq m) hlr
  rw [Dbirth_spec hm2] at key
  have e2 : ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2))
        * (y ^ (q - 1) * Vc (thr 1 N) q m)
      = ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Vc (thr y N) q m := by
    refine Finset.sum_congr rfl (fun q _ => ?_)
    rw [Vc_thr y N q m]
  have e3 : ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1)) * (y ^ (q - 1) * Vc (thr 1 N) q m)
      = ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Vc (thr y N) q m := by
    refine Finset.sum_congr rfl (fun q _ => ?_)
    rw [Vc_thr y N q m]
  rw [e2, e3]
  refine le_of_mul_le_mul_right ?_ (sum_qq_Tq_pos hm2)
  linarith

/-- The moment inequality for one `m ≥ 1`, with the constant `D_r`, `r ≥ m`. -/
private theorem moment_m' {m r : ℕ} (hm1 : 1 ≤ m) (hmr : m ≤ r) {y N : ℝ} (hy0 : 0 < y)
    (hN : ∀ s ∈ Ioo 0 m, y ≤ N - (s : ℝ)) :
    ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2))
        * (y ^ (q - 1) * Vc (thr 1 N) q m)
      ≤ Dbirth r * ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1)) * (y ^ (q - 1) * Vc (thr 1 N) q m) := by
  rcases Nat.lt_or_ge m 2 with h | h
  · have hm : m = 1 := by omega
    subst hm
    simp
  · have h1 := moment_m h hy0 hN
    have h2 : Dbirth m ≤ Dbirth r := Dbirth_mono h hmr
    have h3 : 0 ≤ ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1))
        * (y ^ (q - 1) * Vc (thr 1 N) q m) := by
      refine Finset.sum_nonneg (fun q hq => ?_)
      have hq1 : (1 : ℝ) ≤ (q : ℝ) := by exact_mod_cast (Finset.mem_Icc.mp hq).1
      have hV : 0 ≤ Vc (thr 1 N) q m :=
        Vc_nonneg (fun s hs => thr_nonneg zero_le_one (by linarith [hN s hs])) q
      exact mul_nonneg (mul_nonneg (by linarith) (by linarith))
        (mul_nonneg (pow_nonneg hy0.le _) hV)
    have h4 := mul_le_mul_of_nonneg_right h2 h3
    linarith

/-- **Moment inequality `(*)`**: `∑ q(q-1)(q-2) p_q y^q ≤ D_r ∑ q(q-1) p_q y^q` on `(0, k+2]`. -/
private theorem moment_star {k r : ℕ} (hr2 : r ≤ k - 1) {y : ℝ} (hy0 : 0 < y)
    (hy : y ≤ (k : ℝ) + 2) :
    ∑ q ∈ Icc 1 r, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) * (pcoef k r q * y ^ q)
      ≤ Dbirth r * ∑ q ∈ Icc 1 r, ((q : ℝ) * ((q : ℝ) - 1)) * (pcoef k r q * y ^ q) := by
  have hV : ∀ m q, m < q → (fun m q => Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m) m q = 0 :=
    fun m q hlt => Vc_eq_zero_of_lt _ hlt
  have h3 : ∑ m ∈ Icc 1 r, ccoef k r m * y
        * ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2))
            * (y ^ (q - 1) * Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m)
      = ∑ q ∈ Icc 1 r, ((q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) * (pcoef k r q * y ^ q) :=
    sum_swap_aux r (ccoef k r) (fun m q => Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m) hV
      (fun q => (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2)) y
  have h2 : ∑ m ∈ Icc 1 r, ccoef k r m * y
        * ∑ q ∈ Icc 1 m, ((q : ℝ) * ((q : ℝ) - 1))
            * (y ^ (q - 1) * Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m)
      = ∑ q ∈ Icc 1 r, ((q : ℝ) * ((q : ℝ) - 1)) * (pcoef k r q * y ^ q) :=
    sum_swap_aux r (ccoef k r) (fun m q => Vc (thr 1 (((k + r : ℕ) : ℝ) + 1)) q m) hV
      (fun q => (q : ℝ) * ((q : ℝ) - 1)) y
  rw [← h3, ← h2, Finset.mul_sum]
  refine Finset.sum_le_sum (fun m hm => ?_)
  have hm' := Finset.mem_Icc.mp hm
  have hc : 0 ≤ ccoef k r m * y := mul_nonneg (ccoef_pos hr2 hm'.1 hm'.2).le hy0.le
  have hN : ∀ s ∈ Ioo 0 m, y ≤ ((k + r : ℕ) : ℝ) + 1 - (s : ℝ) := by
    intro s hs
    have hs' := Finset.mem_Ioo.mp hs
    have h : ((s + 1 : ℕ) : ℝ) ≤ (r : ℝ) := Nat.cast_le.mpr (by omega)
    push_cast at h ⊢
    linarith
  have hmom := moment_m' hm'.1 hm'.2 hy0 hN
  have h4 := mul_le_mul_of_nonneg_left hmom hc
  linarith

end Curv

open Curv in
/-- **The curvature ratio.** At a first-layer position `n = k + r`, `r ≤ k - 1`, the second
differences of `K = Kpoly k n` at `k + 1` and at `k` satisfy `C_+ ≤ e^{D_r/(k-1)} C_-`. -/
theorem curv_ratio {k r : ℕ} (hk : 2 ≤ k) (hr2 : r ≤ k - 1) :
    Kpoly k (k + r) ((k : ℝ) + 2) - 2 * Kpoly k (k + r) ((k : ℝ) + 1) + Kpoly k (k + r) k
      ≤ Real.exp (Dbirth r / ((k : ℝ) - 1))
        * (Kpoly k (k + r) ((k : ℝ) + 1) - 2 * Kpoly k (k + r) k
            + Kpoly k (k + r) ((k : ℝ) - 1)) := by
  have hk2 : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  exact poly_curv_le (Icc 1 r) (pcoef k r) (kap k (k + r + 1)) (Dbirth r) (k : ℝ)
    (fun q _ => pcoef_nonneg hr2 q) (by linarith)
    (fun y hy1 hy2 => moment_star hr2 (by linarith) hy2)
    (Kpoly k (k + r)) (fun y => Kpoly_eq_poly k r y)

end Parking
