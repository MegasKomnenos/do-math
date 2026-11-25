module

public import Parking.NextColumn.Frozen
public import Staircase.Diagonal.CurvatureStep
public import Staircase.Diagonal.BoundaryGain
public import Staircase.Diagonal.KernelDeficit
public import Staircase.Diagonal.BirthdayBound
public import Staircase.Diagonal.Ledger

/-!
# The diagonal step behind the curve

In a column `k ≥ 265`, at a position `(k + r, k)` with `r ≥ 1` and `r³ ≤ k²`, a step that is not
positive is followed by a negative step one row down and one column to the right:

`b(k+r, k) ≤ b(k+r, k-1)  ⟹  b(k+r+1, k+1) < b(k+r+1, k)`   (`diagonal_step_curve`).

Write `d(n,k) = b(n,k) - b(n,k-1)`.  At a position of the first layer, with `N = k + r + 1` and
`q = r + 1`, `dq_frozen` (`Parking.NextColumn.Frozen`) gives `d(k+r,k)/(k+r)! = C - B`
(`dq_curv_sub_boundary`):

* the curvature term `C = ∑_{m=1}^{r} κ_k(N-m)/(N-m) · curvSum k N m`, where `κ_k = kap k` is the
  kernel deficit and `curvSum` the second difference in the threshold of `y · Λ_m(y;N)`;
* the boundary term `B = a_k/k · Λ_q(k-1; N)`.

Let `C'`, `B'` be the same at the position `(k+r+1, k+1)`.  The proof shows `C' · B < C · B'` for
`r ≥ 2`; then `C ≤ B` gives `C' · B < B · B'`, that is `C' < B'`.  For `r = 1` the curvature term
`C'` is zero.

The cross product is proved term by term (`term_step`): for `2 ≤ m ≤ r`, with `a = q - m` and
`M = k + a`, the term `c'_m` of `C'` and the term `c_m` of `C` satisfy `c'_m · B < c_m · B'`.  The
term `m = 1` is zero on both sides.  Four comparisons along the diagonal enter.  In them
`γ_n = gam n = (1+1/n)^(n-2)`; `D_m = Dbirth m` is the ratio of the third to the second factorial
moment of the number of parts of a composition of `m` (`Dbirth_spec`), and
`E_m = (1+1/400)(D_m+1)(q-m/2)/(k(k+1))`; `x = q/((k-1)(k+q))` and
`E₀ = (q+2)/(2q) · μ₀(q, q²/(k-1))` with `μ₀(r, X) = (√((4+X)² + 12(r-1)) - (4+X))/3` (`mu0`).

* the coefficient: `κ_{k+1}(M+1)/(M+1) ≤ γ_M (1 + T/k) · κ_k(M)/M` with `T = kapStepBound k a`
  (`kap_diag_le`);
* the curvature sum: `curvSum (k+1) (N+1) m ≤ k/(k+1) · e^(E_m) · curvSum k N m` (`curvSum_step`);
* the boundary term: `(1+x)^(E₀) · Λ_q(k-1;N) ≤ Λ_q(k;N+1)` (`Lam_gain`), and
  `a_{k+1}/(k+1) = γ_k · a_k/k`;
* the scalars: `γ_M (1 + T/k) · k/(k+1) · e^(E_m) < γ_k (1+x)^(E₀)` (`scalar_step`).  After
  logarithms this is the ledger inequality (`ledger`), with the bound `log_gam_sub_le` for
  `log γ_M - log γ_k` and the bound `Dbirth_add_one_le` for the exponent `E_m`.

The hypothesis `r³ ≤ k²` is used in the scalar inequality, and to see that `2r ≤ k` and that
`401 m² ≤ 12 k²` for `m ≤ r`.
-/

@[expose] public section

namespace Parking

open Finset

/-! ### Curvature minus boundary -/

/-- **Curvature minus boundary.**  At a position `(k + r, k)` of the first layer, `1 ≤ r ≤ k - 1`,
with `N = k + r + 1`:
`d(k+r,k)/(k+r)! = ∑_{m=1}^{r} κ_k(N-m)/(N-m) · curvSum k N m - a_k/k · Λ_{r+1}(k-1; N)`.
This is the first statement of `dq_frozen` (`Parking.NextColumn.Frozen`); its curvature term, a
second difference of the frozen polynomial `Kpoly k (k+r)` at the threshold `k`, is written out by
`Kpoly_second_diff`. -/
theorem dq_curv_sub_boundary {k r : ℕ} (hk : 2 ≤ k) (hr1 : 1 ≤ r) (hr2 : r ≤ k - 1) :
    dq k (k + r)
      = (∑ m ∈ Icc 1 r, kap k (k + r + 1 - m) / ((k : ℝ) + r + 1 - m)
            * curvSum (k : ℝ) ((k : ℝ) + r + 1) m)
        - cay k / k * Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1) := by
  rw [(dq_frozen hk hr1 hr2).1, Kpoly_second_diff, Nat.add_sub_cancel_left, Nat.cast_add]

/-! ### The range -/

/-- Behind the curve the deficit is at most half the column: `r³ ≤ k²` and `k ≥ 8` give
`2r ≤ k`. -/
private theorem two_mul_le_of_curve {k r : ℕ} (hk : 8 ≤ k) (hcurve : r ^ 3 ≤ k ^ 2) :
    2 * r ≤ k := by
  by_contra hc
  have h1 : k ^ 3 < (2 * r) ^ 3 := Nat.pow_lt_pow_left (by omega) (by norm_num)
  have h2 : (2 * r) ^ 3 = 8 * r ^ 3 := by ring
  have h3 : 8 * k ^ 2 ≤ k * k ^ 2 := Nat.mul_le_mul_right _ hk
  rw [show k * k ^ 2 = k ^ 3 by ring] at h3
  omega

/-! ### The scalar inequality -/

/-- **The scalar inequality.**  For `k ≥ 265`, `q` with `(q-1)³ ≤ k²` and `1 ≤ a ≤ q - 2`,
with `m = q - a`, `T = kapStepBound k a` and `x = q/((k-1)(k+q))`:
`γ_{k+a} (1 + T/k) · k/(k+1) · exp((1+1/400)(D_m+1)(q-m/2)/(k(k+1))) < γ_k (1+x)^(E₀)`,
`E₀ = (q+2)/(2q) · μ₀(q, q²/(k-1))`, where `γ_n = gam n`, `D_m = Dbirth m` and `μ₀ = mu0`.  The
left side collects the factors that the coefficient and the curvature sum of one term gain along
the diagonal, the right side those of the boundary term.

Take logarithms.  `log γ_{k+a} - log γ_k ≤ (5/2)(1/k - 1/(k+a))` (`log_gam_sub_le`),
`log (1 + T/k) ≤ T/k`, `log (k/(k+1)) = -log (1 + 1/k)`, and `D_m + 1 ≤ (3/2)√(πm/2) - 8/5`
(`Dbirth_add_one_le`).  What remains is the ledger inequality (`ledger`). -/
theorem scalar_step {k q a : ℕ} (hk : 265 ≤ k) (hcurve : (q - 1) ^ 3 ≤ k ^ 2) (ha1 : 1 ≤ a)
    (haq : a + 2 ≤ q) :
    gam (k + a) * (1 + kapStepBound k a / k) * ((k : ℝ) / ((k : ℝ) + 1))
        * Real.exp ((1 + 1 / 400) * (Dbirth (q - a) + 1) * ((q : ℝ) - ((q - a : ℕ) : ℝ) / 2)
            / ((k : ℝ) * ((k : ℝ) + 1)))
      < gam k * (1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)))
          ^ (((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1))) := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hK0 : (0 : ℝ) < k := by linarith
  have hA1 : (1 : ℝ) ≤ a := by exact_mod_cast ha1
  have hAQ : (a : ℝ) + 2 ≤ q := by exact_mod_cast haq
  have hcm : ((q - a : ℕ) : ℝ) = (q : ℝ) - a := Nat.cast_sub (by omega)
  -- the four bounds
  have hled := ledger hk hcurve ha1 haq
  obtain ⟨T, hT⟩ : ∃ T : ℝ, T = kapStepBound k a / k := ⟨_, rfl⟩
  have hT0 : 0 ≤ T := by
    rw [hT]
    have h2 := two_mul_le_of_curve (by omega : 8 ≤ k) hcurve
    exact div_nonneg (kapStepBound_nonneg (by omega)) hK0.le
  have hlogT : Real.log (1 + T) ≤ T := by
    linarith [Real.log_le_sub_one_of_pos (show 0 < 1 + T by linarith)]
  have hgam := log_gam_sub_le (k := k) (i := k + a) (by omega) (by omega)
  rw [Nat.cast_add] at hgam
  have hA := Dbirth_add_one_le (m := q - a) (by omega)
  rw [hcm] at hA ⊢
  obtain ⟨Em, hEm⟩ : ∃ Em : ℝ, Em = (1 + 1 / 400) * (Dbirth (q - a) + 1)
      * ((q : ℝ) - ((q : ℝ) - a) / 2) / ((k : ℝ) * ((k : ℝ) + 1)) := ⟨_, rfl⟩
  have hE : Em ≤ 401 / 400 * (3 / 2 * Real.sqrt (Real.pi * ((q : ℝ) - a) / 2) - 8 / 5)
      * (((q : ℝ) + a) / 2) / ((k : ℝ) * ((k : ℝ) + 1)) := by
    rw [hEm, show (q : ℝ) - ((q : ℝ) - a) / 2 = ((q : ℝ) + a) / 2 by ring,
      show (1 : ℝ) + 1 / 400 = 401 / 400 by norm_num]
    exact div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left hA (by norm_num)) (by linarith)) (by positivity)
  obtain ⟨c, hc⟩ : ∃ c : ℝ, c = 1 + (q : ℝ) / (((k : ℝ) - 1) * ((k : ℝ) + q)) := ⟨_, rfl⟩
  obtain ⟨E0, hE0⟩ : ∃ E0 : ℝ,
      E0 = ((q : ℝ) + 2) / (2 * q) * mu0 q ((q : ℝ) ^ 2 / ((k : ℝ) - 1)) := ⟨_, rfl⟩
  rw [← hT, ← hc, ← hE0] at hled
  rw [← hEm, ← hT, ← hc, ← hE0]
  have hc0 : 0 < c := by
    rw [hc]
    linarith [div_nonneg (by linarith : (0 : ℝ) ≤ q)
      (mul_nonneg (by linarith : (0 : ℝ) ≤ (k : ℝ) - 1) (by linarith : (0 : ℝ) ≤ (k : ℝ) + q))]
  -- logarithms
  have hgM := gam_pos (k + a)
  have hgk := gam_pos k
  have hu : 0 < 1 + T := by linarith
  have hfr : (0 : ℝ) < (k : ℝ) / ((k : ℝ) + 1) := div_pos hK0 (by linarith)
  have hlogfr : Real.log ((k : ℝ) / ((k : ℝ) + 1)) = -Real.log (1 + 1 / (k : ℝ)) := by
    rw [show (k : ℝ) / ((k : ℝ) + 1) = (1 + 1 / (k : ℝ))⁻¹ by field_simp, Real.log_inv]
  have hL0 : 0 < gam (k + a) * (1 + T) * ((k : ℝ) / ((k : ℝ) + 1)) * Real.exp Em :=
    mul_pos (mul_pos (mul_pos hgM hu) hfr) (Real.exp_pos _)
  have hR0 : 0 < gam k * c ^ E0 := mul_pos hgk (Real.rpow_pos_of_pos hc0 _)
  refine (Real.log_lt_log_iff hL0 hR0).mp ?_
  rw [Real.log_mul (mul_pos (mul_pos hgM hu) hfr).ne' (Real.exp_pos _).ne',
    Real.log_mul (mul_pos hgM hu).ne' hfr.ne', Real.log_mul hgM.ne' hu.ne', Real.log_exp,
    Real.log_mul hgk.ne' (Real.rpow_pos_of_pos hc0 _).ne', Real.log_rpow hc0, hlogfr]
  linarith

/-! ### One term of the curvature sum -/

/-- The coefficient of one term along the diagonal: with `M = k + a`,
`κ_{k+1}(M+1)/(M+1) ≤ γ_M (1 + T/k) · κ_k(M)/M`, `T = kapStepBound k a`, `γ_M = gam M`.  This is
`kap_diag_le` with `a_{M+1}/(M+1) = γ_M · a_M/M`. -/
private theorem kap_coeff_le {k a : ℕ} (hk : 2 ≤ k) (hak : 2 * a ≤ k) :
    kap (k + 1) (k + a + 1) / ((k : ℝ) + a + 1)
      ≤ gam (k + a) * (1 + kapStepBound k a / k) * (kap k (k + a) / ((k : ℝ) + a)) := by
  have h := kap_diag_le (by omega) hak
  obtain ⟨T, hT⟩ : ∃ T : ℝ, T = kapStepBound k a / k := ⟨_, rfl⟩
  rw [← hT] at h ⊢
  have hKA : (0 : ℝ) < (k : ℝ) + a := by positivity
  have hg := gam_pos (k + a)
  have hc : 0 < cay (k + a) := cay_pos (by omega)
  have hKA' : (k : ℝ) + a ≠ 0 := hKA.ne'
  have hc0 : cay (k + a) ≠ 0 := hc.ne'
  have hc' : cay (k + a + 1) = gam (k + a) * (1 + 1 / ((k : ℝ) + a)) * cay (k + a) := by
    rw [cay_ratio (by omega : 0 < k + a), psi_eq_gam (by omega : 2 ≤ k + a), Nat.cast_add]
  rw [hc', div_le_iff₀ (by positivity)] at h
  rw [div_le_iff₀ (by linarith)]
  calc kap (k + 1) (k + a + 1)
      ≤ (1 + T) * (kap k (k + a) / cay (k + a))
          * (gam (k + a) * (1 + 1 / ((k : ℝ) + a)) * cay (k + a)) := h
    _ = gam (k + a) * (1 + T) * (kap k (k + a) / ((k : ℝ) + a)) * ((k : ℝ) + a + 1) := by
        field_simp

/-- The algebra of `term_step`: the coefficient `c`, the curvature sum `Cs` and the boundary term
`b · Λ` of one position against those of its diagonal successor. -/
private theorem cross_alg {c c' Cs Cs' b Λ Λ' g0 g1 T φ ex cE : ℝ} (hc : 0 < c) (hc' : 0 ≤ c')
    (hCs : 0 < Cs) (hb : 0 < b) (hΛ : 0 < Λ) (hg0 : 0 ≤ g0) (hφ : 0 ≤ φ) (hex : 0 ≤ ex)
    (F0 : c' ≤ g1 * (1 + T) * c) (F1 : Cs' ≤ φ * ex * Cs) (F2 : cE * Λ ≤ Λ')
    (F3 : g1 * (1 + T) * φ * ex < g0 * cE) :
    c' * Cs' * (b * Λ) < c * Cs * (g0 * b * Λ') := by
  have hbΛ : 0 < b * Λ := mul_pos hb hΛ
  calc c' * Cs' * (b * Λ)
      ≤ c' * (φ * ex * Cs) * (b * Λ) :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left F1 hc') hbΛ.le
    _ ≤ g1 * (1 + T) * c * (φ * ex * Cs) * (b * Λ) :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right F0
          (mul_nonneg (mul_nonneg hφ hex) hCs.le)) hbΛ.le
    _ = (g1 * (1 + T) * φ * ex) * (c * Cs * (b * Λ)) := by ring
    _ < (g0 * cE) * (c * Cs * (b * Λ)) :=
        mul_lt_mul_of_pos_right F3 (mul_pos (mul_pos hc hCs) hbΛ)
    _ = (c * Cs * b * g0) * (cE * Λ) := by ring
    _ ≤ (c * Cs * b * g0) * Λ' := mul_le_mul_of_nonneg_left F2 (by positivity)
    _ = c * Cs * (g0 * b * Λ') := by ring

/-- **One term of the cross product.**  For `k ≥ 265`, `r³ ≤ k²` and `2 ≤ m ≤ r`, the term `m` of
the curvature sum at `(k+r+1, k+1)`, multiplied by the boundary term at `(k+r, k)`, is smaller than
the term `m` at `(k+r, k)` multiplied by the boundary term at `(k+r+1, k+1)`.

With `a = r + 1 - m`: the coefficient is compared by `kap_diag_le`, the curvature sum by
`curvSum_step`, the boundary term by `Lam_gain`, and the scalar factors that these three leave by
`scalar_step`.  The inequality is strict because the scalar inequality is strict and the term at
`(k+r, k)` is positive. -/
theorem term_step {k r m : ℕ} (hk : 265 ≤ k) (hcurve : r ^ 3 ≤ k ^ 2) (hm2 : 2 ≤ m)
    (hmr : m ≤ r) :
    kap (k + 1) (k + 1 + r + 1 - m) / ((k : ℝ) + 1 + r + 1 - m)
        * curvSum ((k : ℝ) + 1) ((k : ℝ) + 1 + r + 1) m
        * (cay k / k * Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1))
      < kap k (k + r + 1 - m) / ((k : ℝ) + r + 1 - m) * curvSum (k : ℝ) ((k : ℝ) + r + 1) m
        * (cay (k + 1) / ((k : ℝ) + 1) * Lam (thr (k : ℝ) ((k : ℝ) + 1 + r + 1)) (r + 1)) := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hK0 : (0 : ℝ) < k := by linarith
  have hmrR : (m : ℝ) ≤ r := by exact_mod_cast hmr
  have h2r := two_mul_le_of_curve (by omega : 8 ≤ k) hcurve
  have hrk : r < k := by omega
  obtain ⟨a, hadef⟩ : ∃ a : ℕ, a = r + 1 - m := ⟨_, rfl⟩
  have ha1 : 1 ≤ a := by omega
  have haq : a + 2 ≤ r + 1 := by omega
  have hA : (a : ℝ) = (r : ℝ) + 1 - m := by
    rw [hadef, Nat.cast_sub (by omega), Nat.cast_add, Nat.cast_one]
  have hA0 : (0 : ℝ) < a := by exact_mod_cast ha1
  have hcurve' : (r + 1 - 1) ^ 3 ≤ k ^ 2 := by rwa [Nat.add_sub_cancel]
  have hmk : 401 * m ^ 2 ≤ 12 * k ^ 2 := by
    have h3 : 265 ^ 2 ≤ k ^ 2 := Nat.pow_le_pow_left hk 2
    rcases Nat.lt_or_ge r 42 with h | h
    · have h2 : m ^ 2 ≤ 41 ^ 2 := Nat.pow_le_pow_left (by omega) 2
      omega
    · have h1 : m ^ 2 ≤ r ^ 2 := Nat.pow_le_pow_left hmr 2
      have h4 : 42 * r ^ 2 ≤ r * r ^ 2 := Nat.mul_le_mul_right _ h
      rw [show r * r ^ 2 = r ^ 3 by ring] at h4
      omega
  -- the four comparisons
  have F0 := kap_coeff_le (k := k) (a := a) (by omega) (by omega)
  have F1 := curvSum_step (k := k) (q := r + 1) (m := m) (by omega) hm2 (by omega) hmk
  have F2 := Lam_gain (k := k) (q := r + 1) (by omega) (by omega)
  have F3 := scalar_step (k := k) (q := r + 1) (a := a) hk hcurve' ha1 haq
  rw [show r + 1 - a = m by omega] at F3
  rw [Nat.cast_add_one] at F1 F2 F3
  rw [show (k : ℝ) + ((r : ℝ) + 1) + 1 = (k : ℝ) + 1 + r + 1 by ring,
    show (k : ℝ) + ((r : ℝ) + 1) = (k : ℝ) + r + 1 by ring] at F1 F2
  rw [show (k : ℝ) + ((r : ℝ) + 1) = (k : ℝ) + r + 1 by ring] at F3
  -- the quantities of the two positions
  have hκ : 0 < kap k (k + a) := kap_pos (by omega) (by omega)
  have hκ' : 0 < kap (k + 1) (k + a + 1) := kap_pos (by omega) (by omega)
  have hCs : 0 < curvSum (k : ℝ) ((k : ℝ) + r + 1) m := curvSum_pos hK0 hm2 (by linarith)
  have hΛ : 0 < Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1) :=
    Lam_thr_pos (by omega) (by linarith) (by push_cast; linarith)
  have hb' : cay (k + 1) / ((k : ℝ) + 1) = gam k * (cay k / k) := by
    have hKne : (k : ℝ) ≠ 0 := hK0.ne'
    rw [cay_ratio (by omega : 0 < k), psi_eq_gam (by omega : 2 ≤ k)]
    field_simp
  rw [show k + r + 1 - m = k + a by omega, show k + 1 + r + 1 - m = k + a + 1 by omega,
    show (k : ℝ) + r + 1 - m = (k : ℝ) + a by rw [hA]; ring,
    show (k : ℝ) + 1 + r + 1 - m = (k : ℝ) + a + 1 by rw [hA]; ring, hb']
  exact cross_alg (div_pos hκ (by linarith)) (div_pos hκ' (by linarith)).le hCs
    (div_pos (cay_pos (by omega)) hK0) hΛ (gam_pos k).le (div_pos hK0 (by linarith)).le
    (Real.exp_pos _).le F0 F1 F2 F3

/-! ### The diagonal step -/

/-- **The diagonal step behind the curve.**  In a column `k ≥ 265`, at a position `(k + r, k)`
with `r ≥ 1` and `r³ ≤ k²`: if the step is not positive, `b(k+r, k) ≤ b(k+r, k-1)`, then the step
one row down and one column to the right is negative, `b(k+r+1, k+1) < b(k+r+1, k)`.

Both steps are curvature minus boundary (`dq_curv_sub_boundary`), `C - B` and `C' - B'` with
`B, B' > 0`.  For `r = 1` the curvature term `C'` consists of the term `m = 1`, which is zero.  For
`r ≥ 2` the sum of `term_step` over `2 ≤ m ≤ r` gives `C' · B < C · B'`, and `C ≤ B` then gives
`C' · B < B · B'`, that is `C' < B'`. -/
theorem diagonal_step_curve (k r : ℕ) (hk : 265 ≤ k) (hr : 1 ≤ r) (hcurve : r ^ 3 ≤ k ^ 2)
    (h : b (k + r) k ≤ b (k + r) (k - 1)) : b (k + r + 1) (k + 1) < b (k + r + 1) k := by
  have hK : (265 : ℝ) ≤ k := by exact_mod_cast hk
  have hK0 : (0 : ℝ) < k := by linarith
  have h2r := two_mul_le_of_curve (by omega : 8 ≤ k) hcurve
  have hrk : r < k := by omega
  have hd : dq k (k + r) ≤ 0 := (dq_nonpos_iff k (k + r)).mpr h
  have hfr := dq_curv_sub_boundary (k := k) (r := r) (by omega) hr (by omega)
  have hfr' := dq_curv_sub_boundary (k := k + 1) (r := r) (by omega) hr (by omega)
  rw [Nat.cast_add_one, show (k : ℝ) + 1 - 1 = (k : ℝ) by ring] at hfr'
  obtain ⟨B, hB⟩ : ∃ B : ℝ,
      B = cay k / k * Lam (thr ((k : ℝ) - 1) ((k : ℝ) + r + 1)) (r + 1) := ⟨_, rfl⟩
  obtain ⟨B', hB'⟩ : ∃ B' : ℝ,
      B' = cay (k + 1) / ((k : ℝ) + 1) * Lam (thr (k : ℝ) ((k : ℝ) + 1 + r + 1)) (r + 1) :=
    ⟨_, rfl⟩
  have hBpos : 0 < B := by
    rw [hB]
    exact mul_pos (div_pos (cay_pos (by omega)) hK0)
      (Lam_thr_pos (by omega) (by linarith) (by push_cast; linarith))
  have hB'pos : 0 < B' := by
    rw [hB']
    exact mul_pos (div_pos (cay_pos (by omega)) (by linarith))
      (Lam_thr_pos (by omega) (by linarith) (by push_cast; linarith))
  rw [← hB] at hfr
  rw [← hB'] at hfr'
  have hlt : dq (k + 1) (k + 1 + r) < 0 := by
    rcases Nat.lt_or_ge r 2 with h1 | h2
    · -- `r = 1`: the curvature term at `(k + 2, k + 1)` vanishes
      obtain rfl : r = 1 := by omega
      rw [Finset.Icc_self, Finset.sum_singleton, curvSum_one, mul_zero] at hfr'
      linarith
    · -- `r ≥ 2`: the cross product `C' · B < C · B'`
      have hx : (∑ m ∈ Icc 1 r, kap (k + 1) (k + 1 + r + 1 - m) / ((k : ℝ) + 1 + r + 1 - m)
            * curvSum ((k : ℝ) + 1) ((k : ℝ) + 1 + r + 1) m) * B
          < (∑ m ∈ Icc 1 r, kap k (k + r + 1 - m) / ((k : ℝ) + r + 1 - m)
            * curvSum (k : ℝ) ((k : ℝ) + r + 1) m) * B' := by
        rw [hB, hB', Finset.sum_mul, Finset.sum_mul]
        refine Finset.sum_lt_sum (fun m hm => ?_)
          ⟨2, mem_Icc.mpr ⟨by omega, h2⟩, term_step hk hcurve le_rfl h2⟩
        rcases Nat.lt_or_ge m 2 with hm1 | hm2
        · obtain rfl : m = 1 := by have := (mem_Icc.mp hm).1; omega
          rw [curvSum_one, curvSum_one]
          simp
        · exact (term_step hk hcurve hm2 (mem_Icc.mp hm).2).le
      obtain ⟨C, hC⟩ : ∃ C : ℝ, C = ∑ m ∈ Icc 1 r, kap k (k + r + 1 - m) / ((k : ℝ) + r + 1 - m)
          * curvSum (k : ℝ) ((k : ℝ) + r + 1) m := ⟨_, rfl⟩
      obtain ⟨C', hC'⟩ : ∃ C' : ℝ, C' = ∑ m ∈ Icc 1 r,
          kap (k + 1) (k + 1 + r + 1 - m) / ((k : ℝ) + 1 + r + 1 - m)
            * curvSum ((k : ℝ) + 1) ((k : ℝ) + 1 + r + 1) m := ⟨_, rfl⟩
      rw [← hC] at hfr hx
      rw [← hC'] at hfr' hx
      have h3 : C' * B < B' * B := by
        nlinarith [mul_le_mul_of_nonneg_right (show C ≤ B by linarith) hB'pos.le]
      have h5 : C' < B' := lt_of_mul_lt_mul_right h3 hBpos.le
      linarith
  have hfin := (dq_neg_iff (k + 1) (k + 1 + r)).mp hlt
  rwa [Nat.add_sub_cancel, show k + 1 + r = k + r + 1 by omega] at hfin

end Parking
