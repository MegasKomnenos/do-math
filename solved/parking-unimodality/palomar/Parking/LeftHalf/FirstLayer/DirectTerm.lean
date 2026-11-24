module

public import Parking.LeftHalf.FirstLayer.PairSum

/-!
# The direct term of the kernel recursion has property K

Divided by `c + ρ`, the last-car recursion at size `c + ρ`, threshold `c` (`1 ≤ ρ ≤ c - 1`) reads
`u_{c+ρ}(c) = (chain part) + S_ρ(c)` with the *direct term*

  `S_ρ(c) = x ω_{ρ-1} ω_c + (x/2) ν(c) q(c)`,   `ν(c) = (c+ρ+1)/(c+ρ)`,

where `q(c) = pairT k ρ (c-ρ-1)` is the pair sum (`Sdir`; the recursion in this form is
`zrT_rec_Sdir` of `Parking/LeftHalf/FirstLayer/Main.lean`).  `Sdir_TK` states that for `k ≥ 7` and
`1 ≤ ρ ≤ k-2` the triple `(S_ρ(k-1), S_ρ(k), S_ρ(k+1))` has property K at `k`.

Both `(ω_{k-1}, ω_k, ω_{k+1})` and the pair sums have property K, but the factor `ν` decreases in
`c`, so the closure of property K under factors does not apply to `ν q`: the surplus of the first
term has to pay for the defect of the second.  With `N = k + ρ` the proof splits the tilt at
`1/(k(k+2))`:

* for `μ ≤ 1/(k(k+2))` the defect is at most `(ν(k) - ν(k+1)) D`, where
  `D = e^μ q(k+1) - e^{-μ} q(k-1) ≤ 2 e^μ ω_ρ ω_k` (`pair_defect_small`, `pairT_D_le`); the surplus
  of the first term is at least `ω_k (3/(2(k+1)(k+2)) - 2(e^{μ/k}-1))` (`ccT_tilt_top'`), and
  `caseI_num` compares the two;
* for `μ ≥ 1/(k(k+2))` the factor `ν` is absorbed by a shift of the tilt (`TK.shift`), which leaves
  a second-order defect `≤ 2 e^{μ/k} ν(k) q(k) (N-k+1)/(N²(N+2)k)` (`pair_defect_large`,
  `nu_Xi_lb`) with `q(k) ≤ (2k-N) ω_ρ ω_k` (`pairT_mid_le`); the surplus of the first term is at
  least `ω_k e^{μ/k} (k²-2k-1)/(2k(k+1)(k+2)) / k` (`ccT_tilt_top`), and `caseII_num` compares the
  two.

In both cases the surplus is at least `ω_k δ` and the defect at most `2 ω_ρ ω_k δ` for the same
`δ`, and `ω_ρ ≤ ω_{ρ-1}` closes the argument (`Sdir_combine`).
-/

@[expose] public section

namespace Parking.FirstLayer
open Real Finset

/-- The direct term `S_ρ(c) = x ω_{ρ-1} ω_c + (x/2) ((c+ρ+1)/(c+ρ)) · pairT k ρ (c-ρ-1)`. -/
noncomputable def Sdir (k ρ c : ℕ) : ℝ :=
  xcrit k * ccT (xcrit k) (ρ - 1) * ccT (xcrit k) c +
    xcrit k / 2 * (((c : ℝ) + ρ + 1) / ((c : ℝ) + ρ)) * pairT k ρ (c - ρ - 1)

/-! ### Numerical inequalities -/

/-- The numerical comparison for small tilts: for `k ≥ 7`, `N ≥ k+1`, `0 ≤ μ ≤ 1/(k(k+2))`,
`e^μ/(N(N+1)) ≤ 3/(2(k+1)(k+2)) - 2(e^{μ/k} - 1)`. -/
private theorem caseI_num {k N μ : ℝ} (hk : 7 ≤ k) (hN : k + 1 ≤ N) (h0 : 0 ≤ μ)
    (h1 : μ ≤ 1 / (k * (k + 2))) :
    exp μ * (1 / (N * (N + 1))) ≤ 3 / (2 * (k + 1) * (k + 2)) - 2 * (exp (μ / k) - 1) := by
  have hk0 : 0 < k := by linarith
  have hN0 : 0 < N := by linarith
  have hkk : 63 ≤ k * (k + 2) := by nlinarith
  have hμ63 : μ ≤ 1 / 63 := by
    refine le_trans h1 ?_
    rw [div_le_div_iff₀ (by positivity) (by norm_num)]
    linarith
  -- `exp μ ≤ 63/62`
  have hexp1 : exp μ ≤ 63 / 62 := by
    have h := Real.add_one_le_exp (-μ)
    have hpos := exp_pos μ
    have hinv : exp μ * exp (-μ) = 1 := by
      rw [← exp_add]
      simp
    have t1 := mul_le_mul_of_nonneg_left h hpos.le
    have t2 : 0 ≤ exp μ * (1 - μ - 62 / 63) := mul_nonneg hpos.le (by linarith)
    linarith
  -- `y = μ/k ≤ 1/(k²(k+2)) ≤ 1/441`
  have hy0 : 0 ≤ μ / k := div_nonneg h0 hk0.le
  have hy1 : μ / k ≤ 1 / (k ^ 2 * (k + 2)) := by
    rw [div_le_div_iff₀ hk0 (by positivity)]
    have h2 := mul_le_mul_of_nonneg_right h1 (by positivity : (0 : ℝ) ≤ k * (k + 2))
    rw [div_mul_cancel₀ _ (by positivity)] at h2
    have h3 := mul_le_mul_of_nonneg_left h2 hk0.le
    linarith
  have hk2 : 49 ≤ k ^ 2 := by nlinarith
  have h441 : 441 ≤ k ^ 2 * (k + 2) := by
    have := mul_nonneg (sub_nonneg.mpr hk2) (by linarith : (0 : ℝ) ≤ k + 2)
    linarith
  have hy441 : μ / k ≤ 1 / 441 := by
    refine le_trans hy1 ?_
    rw [div_le_div_iff₀ (by positivity) (by norm_num)]
    linarith
  -- `exp y - 1 ≤ (441/440) y`
  have hexp2 : exp (μ / k) - 1 ≤ 441 / 440 * (μ / k) := by
    have h := Real.add_one_le_exp (-(μ / k))
    have hpos := exp_pos (μ / k)
    have hinv : exp (μ / k) * exp (-(μ / k)) = 1 := by
      rw [← exp_add]
      simp
    have hge : 1 ≤ exp (μ / k) := Real.one_le_exp hy0
    have t1 := mul_le_mul_of_nonneg_left h hpos.le
    have t2 : 0 ≤ (exp (μ / k) - 1) * (1 - μ / k - 440 / 441) :=
      mul_nonneg (by linarith) (by linarith)
    linarith
  -- compare everything with `U = 1/((k+1)(k+2))`
  have hD : (k + 1) * (k + 2) ≤ N * (N + 1) :=
    mul_le_mul hN (by linarith) (by linarith) hN0.le
  have hu : 1 / (N * (N + 1)) ≤ 1 / ((k + 1) * (k + 2)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    linarith
  have hv : 1 / (k ^ 2 * (k + 2)) ≤ 8 / 49 * (1 / ((k + 1) * (k + 2))) := by
    rw [mul_one_div, div_le_div_iff₀ (by positivity) (by positivity)]
    have := mul_nonneg (mul_nonneg (by linarith : (0 : ℝ) ≤ k + 2) (by linarith : (0 : ℝ) ≤ k - 7))
      (by linarith : (0 : ℝ) ≤ 8 * k + 7)
    linarith
  have hU0 : (0 : ℝ) ≤ 1 / ((k + 1) * (k + 2)) := by positivity
  have s1 : exp μ * (1 / (N * (N + 1))) ≤ 63 / 62 * (1 / ((k + 1) * (k + 2))) :=
    mul_le_mul hexp1 hu (by positivity) (by norm_num)
  have s2 : μ / k ≤ 8 / 49 * (1 / ((k + 1) * (k + 2))) := le_trans hy1 hv
  have e3 : 3 / (2 * (k + 1) * (k + 2)) = 3 / 2 * (1 / ((k + 1) * (k + 2))) := by
    rw [div_mul_div_comm, mul_one, mul_assoc]
  rw [e3]
  linarith

/-- The numerical comparison for large tilts: for `k ≥ 7`, `N ≥ k+1`,
`((N+1)/N) (2k-N) (N-k+1)/(N²(N+2)k) ≤ (k²-2k-1)/(2k(k+1)(k+2)k)`. -/
private theorem caseII_num {k N : ℝ} (hk : 7 ≤ k) (hN1 : k + 1 ≤ N) :
    (N + 1) / N * (2 * k - N) * (2 * (N - k + 1) / (N ^ 2 * (N + 2)) / (2 * k)) ≤
      (k ^ 2 - 2 * k - 1) / (2 * k * (k + 1) * (k + 2)) / k := by
  have hk0 : 0 < k := by linarith
  have hN0 : 0 < N := by linarith
  have e : (N + 1) / N * (2 * k - N) * (2 * (N - k + 1) / (N ^ 2 * (N + 2)) / (2 * k)) =
      (N + 1) / N * (2 * k - N) * (2 * (N - k + 1) / (N ^ 2 * (N + 2)) / 2) / k := by
    ring
  rw [e]
  refine div_le_div_of_nonneg_right ?_ hk0.le
  have h1 : (N + 1) / N * (2 * k - N) * (2 * (N - k + 1) / (N ^ 2 * (N + 2)) / 2) =
      ((N + 1) * (2 * k - N) * (N - k + 1)) / (N ^ 3 * (N + 2)) := by
    field_simp
  have h2 : ((N + 1) * (2 * k - N) * (N - k + 1)) / (N ^ 3 * (N + 2)) ≤ 1 / (4 * (k + 1)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    have a1 : 4 * ((2 * k - N) * (N - k + 1)) ≤ (k + 1) ^ 2 := by
      nlinarith [sq_nonneg ((2 * k - N) - (N - k + 1))]
    have a2 : (k + 1) ^ 3 ≤ N ^ 3 := pow_le_pow_left₀ (by positivity) hN1 3
    have b1 : (N + 1) * (2 * k - N) * (N - k + 1) * (4 * (k + 1)) =
        (N + 1) * (k + 1) * (4 * ((2 * k - N) * (N - k + 1))) := by ring
    have b2 : (N + 1) * (k + 1) * (4 * ((2 * k - N) * (N - k + 1))) ≤
        (N + 1) * (k + 1) * (k + 1) ^ 2 := mul_le_mul_of_nonneg_left a1 (by positivity)
    have b3 : (N + 1) * (k + 1) * (k + 1) ^ 2 = (N + 1) * (k + 1) ^ 3 := by ring
    have b4 : (N + 1) * (k + 1) ^ 3 ≤ (N + 2) * N ^ 3 :=
      mul_le_mul (by linarith) a2 (by positivity) (by positivity)
    linarith
  have h3 : 1 / (4 * (k + 1)) ≤ (k ^ 2 - 2 * k - 1) / (2 * k * (k + 1) * (k + 2)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    have := mul_nonneg (mul_nonneg (by linarith : (0 : ℝ) ≤ k + 1) (by linarith : (0 : ℝ) ≤ k - 7))
      (by linarith : (0 : ℝ) ≤ k + 1)
    nlinarith
  rw [h1]
  exact le_trans h2 h3

/-! ### The factor `ν(c) = (c+ρ+1)/(c+ρ)` at `c = k-1, k, k+1` (`N = k+ρ`) -/

private theorem nu_diff1 {N : ℝ} (hN : 1 < N) :
    (N + 1) / N - (N + 2) / (N + 1) = 1 / (N * (N + 1)) := by
  have hN0 : 0 < N := by linarith
  field_simp
  ring

private theorem nu_diff2 {N : ℝ} (hN : 1 < N) :
    1 / (N * (N + 1)) ≤ N / (N - 1) - (N + 1) / N := by
  have hN0 : 0 < N := by linarith
  have hN1 : 0 < N - 1 := by linarith
  have e : N / (N - 1) - (N + 1) / N = 1 / (N * (N - 1)) := by
    field_simp
    ring
  rw [e, div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith

/-- `log (ν₊/ν₀) ≥ -1/(N(N+2))`. -/
private theorem nu_logL_lb {N : ℝ} (hN : 1 < N) :
    -(1 / (N * (N + 2))) ≤ Real.log (((N + 2) / (N + 1)) / ((N + 1) / N)) := by
  have hN0 : 0 < N := by linarith
  have hx : 0 < ((N + 2) / (N + 1)) / ((N + 1) / N) := by positivity
  have h := Real.log_le_sub_one_of_pos (inv_pos.mpr hx)
  rw [Real.log_inv] at h
  have e : (((N + 2) / (N + 1)) / ((N + 1) / N))⁻¹ - 1 = 1 / (N * (N + 2)) := by
    field_simp
    ring
  rw [e] at h
  linarith

/-- `1/N² ≤ log (ν₋/ν₀) ≤ 1/((N-1)(N+1))`. -/
private theorem nu_logM_bounds {N : ℝ} (hN : 1 < N) :
    1 / N ^ 2 ≤ Real.log ((N / (N - 1)) / ((N + 1) / N)) ∧
      Real.log ((N / (N - 1)) / ((N + 1) / N)) ≤ 1 / ((N - 1) * (N + 1)) := by
  have hN0 : 0 < N := by linarith
  have hN1 : 0 < N - 1 := by linarith
  have hx : 0 < (N / (N - 1)) / ((N + 1) / N) := by positivity
  constructor
  · have h := Real.log_le_sub_one_of_pos (inv_pos.mpr hx)
    rw [Real.log_inv] at h
    have e : ((N / (N - 1)) / ((N + 1) / N))⁻¹ - 1 = -(1 / N ^ 2) := by
      field_simp
      ring
    rw [e] at h
    linarith
  · have h := Real.log_le_sub_one_of_pos hx
    have e : (N / (N - 1)) / ((N + 1) / N) - 1 = 1 / ((N - 1) * (N + 1)) := by
      field_simp
      ring
    rw [e] at h
    exact h

/-- The tilt shift caused by `ν` is at most `1/(k(k+2))`. -/
private theorem nu_shift_small {k N : ℝ} (hk : 7 ≤ k) (hN : k + 1 ≤ N) :
    (Real.log ((N / (N - 1)) / ((N + 1) / N)) -
        Real.log (((N + 2) / (N + 1)) / ((N + 1) / N))) / 2 ≤ 1 / (k * (k + 2)) := by
  have hk0 : 0 < k := by linarith
  have hN0 : 0 < N := by linarith
  have hN1 : 0 < N - 1 := by linarith
  have hL := nu_logL_lb (N := N) (by linarith)
  have hM := (nu_logM_bounds (N := N) (by linarith)).2
  have h3 : 1 / (N * (N + 2)) ≤ 1 / ((N - 1) * (N + 1)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    nlinarith
  have h4 : 1 / ((N - 1) * (N + 1)) ≤ 1 / (k * (k + 2)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    nlinarith [mul_self_le_mul_self (by linarith : (0 : ℝ) ≤ k + 1) hN]
  linarith

/-- The second-order defect of `ν`:
`(k+1) log (ν₊/ν₀) + (k-1) log (ν₋/ν₀) ≥ -2(N-k+1)/(N²(N+2))`. -/
private theorem nu_Xi_lb {k N : ℝ} (hk : 7 ≤ k) (hN : k + 1 ≤ N) :
    -(2 * (N - k + 1) / (N ^ 2 * (N + 2))) ≤
      (k + 1) * Real.log (((N + 2) / (N + 1)) / ((N + 1) / N)) +
        (k - 1) * Real.log ((N / (N - 1)) / ((N + 1) / N)) := by
  have hN0 : 0 < N := by linarith
  have hL := nu_logL_lb (N := N) (by linarith)
  have hM := (nu_logM_bounds (N := N) (by linarith)).1
  have t1 := mul_le_mul_of_nonneg_left hL (by linarith : (0 : ℝ) ≤ k + 1)
  have t2 := mul_le_mul_of_nonneg_left hM (by linarith : (0 : ℝ) ≤ k - 1)
  have e : (k + 1) * -(1 / (N * (N + 2))) + (k - 1) * (1 / N ^ 2) =
      -(2 * (N - k + 1) / (N ^ 2 * (N + 2))) := by
    field_simp
    ring
  linarith

/-! ### The defect of the pair-sum term, and the combination -/

/-- The defect of the pair-sum term for small tilts.  Since `ν₀ - ν₊ = d ≤ ν₋ - ν₀`, the property K
of the pair sums leaves the defect `d (a T₊ - b T₋)`. -/
private theorem pair_defect_small {a b c Tm T0 Tp νm ν0 νp d M : ℝ} (hb : 0 ≤ b) (hTm : 0 ≤ Tm)
    (hν0 : 0 ≤ ν0) (hd0 : 0 ≤ d) (hd1 : ν0 - νp = d) (hd2 : d ≤ νm - ν0)
    (hTK : 2 * c * T0 ≤ a * Tp + b * Tm) (hD : a * Tp - b * Tm ≤ M) :
    -(d * M) ≤ a * (νp * Tp) + b * (νm * Tm) - 2 * c * (ν0 * T0) := by
  have t1 : 0 ≤ ν0 * (a * Tp + b * Tm - 2 * c * T0) := mul_nonneg hν0 (by linarith)
  have t2 : 0 ≤ (νm - ν0 - d) * (b * Tm) := mul_nonneg (by linarith) (mul_nonneg hb hTm)
  have t3 : d * (a * Tp - b * Tm) ≤ d * M := mul_le_mul_of_nonneg_left hD hd0
  have t4 : (ν0 - νp - d) * (a * Tp) = 0 := by rw [hd1, sub_self, zero_mul]
  linarith

/-- The defect of the pair-sum term for large tilts.  If the tilt shift gives the inequality of the
pair sums with the middle value multiplied by `E ≥ 1 - e`, the defect is at most `2 c ν₀ e T₀`. -/
private theorem pair_defect_large {a b c Tm T0 Tp νm ν0 νp E e M : ℝ} (hc : 0 ≤ c) (hν0 : 0 ≤ ν0)
    (hT0 : 0 ≤ T0) (he : 0 ≤ e)
    (hsh : ν0 * (2 * c * E * T0) ≤ a * (νp * Tp) + b * (νm * Tm)) (hE : 1 - e ≤ E)
    (hmid : T0 ≤ M) :
    -(2 * c * ν0 * e * M) ≤ a * (νp * Tp) + b * (νm * Tm) - 2 * c * (ν0 * T0) := by
  have e1 : 2 * c * (ν0 * T0) * (1 - e) ≤ 2 * c * (ν0 * T0) * E :=
    mul_le_mul_of_nonneg_left hE (by positivity)
  have e2 : 2 * c * ν0 * e * T0 ≤ 2 * c * ν0 * e * M :=
    mul_le_mul_of_nonneg_left hmid (by positivity)
  linarith

/-- The two terms of the direct term combined (`X = x`, `W = ω_{ρ-1}`, `V = ω_ρ`, `w0 = ω_k`,
`wp = ω_{k+1}`; `a = e^μ`, `b = e^{-μ}`, `c = e^{μ/k}`).  If the surplus of the first term is at
least `ω_k δ` and the defect of the pair-sum term is at most `2 ω_ρ ω_k δ`, the tilted convexity
of the direct term follows, because `ω_ρ ≤ ω_{ρ-1}`. -/
private theorem Sdir_combine {X W V w0 wp Tm T0 Tp a b c νm ν0 νp δ : ℝ}
    (hX : 0 ≤ X) (hV : 0 ≤ V) (hVW : V ≤ W) (hw0 : 0 ≤ w0) (hδ : 0 ≤ δ)
    (hB : w0 * δ ≤ a * wp + b * w0 - 2 * c * w0)
    (hE : -(2 * (V * w0) * δ) ≤ a * (νp * Tp) + b * (νm * Tm) - 2 * c * (ν0 * T0)) :
    2 * c * (X * W * w0 + X / 2 * ν0 * T0) ≤
      a * (X * W * wp + X / 2 * νp * Tp) + b * (X * W * w0 + X / 2 * νm * Tm) := by
  have h1 : X * W * (w0 * δ) ≤ X * W * (a * wp + b * w0 - 2 * c * w0) :=
    mul_le_mul_of_nonneg_left hB (mul_nonneg hX (hV.trans hVW))
  have h2 : X * V * (w0 * δ) ≤ X * W * (w0 * δ) :=
    mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hVW hX) (mul_nonneg hw0 hδ)
  have h3 := mul_le_mul_of_nonneg_left hE (by linarith : (0 : ℝ) ≤ X / 2)
  linarith

/-! ### The theorem -/

/-- **The direct term has property K**: for `k ≥ 7` and `1 ≤ ρ ≤ k-2` (`ρ + n + 2 = k`) the triple
`(S_ρ(k-1), S_ρ(k), S_ρ(k+1))` has property K at `k`. -/
theorem Sdir_TK {k ρ n : ℕ} (hk : 7 ≤ k) (hρ : 1 ≤ ρ) (hn : ρ + n + 2 = k) :
    TK k (Sdir k ρ (k - 1)) (Sdir k ρ k) (Sdir k ρ (k + 1)) := by
  have hk1 : 1 ≤ k := by omega
  have hk3 : 3 ≤ k := by omega
  have hkr : (7 : ℝ) ≤ k := by exact_mod_cast hk
  have hk0 : (0 : ℝ) < k := by linarith
  have hρr : (1 : ℝ) ≤ ρ := by exact_mod_cast hρ
  have hρk : (ρ : ℝ) + 2 ≤ k := by exact_mod_cast (by omega : ρ + 2 ≤ k)
  -- `N = k + ρ` is the size of the middle value
  obtain ⟨N, hNdef⟩ : ∃ N : ℝ, N = (k : ℝ) + ρ := ⟨_, rfl⟩
  have hN : (k : ℝ) + 1 ≤ N := by rw [hNdef]; linarith
  have hN1 : (1 : ℝ) < N := by linarith
  have hNpos : (0 : ℝ) < N := by linarith
  have hNm1 : (0 : ℝ) < N - 1 := by linarith
  have hnr : (n : ℝ) + 2 = 2 * (k : ℝ) - N := by
    have h : ((ρ + n + 2 : ℕ) : ℝ) = (k : ℝ) := by exact_mod_cast hn
    push_cast at h
    rw [hNdef]
    linarith
  -- the three values of the direct term, with `ω_{k-1} = ω_k`
  have hSm : Sdir k ρ (k - 1) = xcrit k * ccT (xcrit k) (ρ - 1) * ccT (xcrit k) k +
      xcrit k / 2 * (N / (N - 1)) * pairT k ρ n := by
    unfold Sdir
    rw [show k - 1 - ρ - 1 = n by omega, Nat.cast_sub hk1, Nat.cast_one,
      show (k : ℝ) - 1 + ρ + 1 = N by rw [hNdef]; ring,
      show (k : ℝ) - 1 + ρ = N - 1 by rw [hNdef]; ring, ← ccT_top hk1]
  have hS0 : Sdir k ρ k = xcrit k * ccT (xcrit k) (ρ - 1) * ccT (xcrit k) k +
      xcrit k / 2 * ((N + 1) / N) * pairT k ρ (n + 1) := by
    unfold Sdir
    rw [show k - ρ - 1 = n + 1 by omega, ← hNdef]
  have hSp : Sdir k ρ (k + 1) = xcrit k * ccT (xcrit k) (ρ - 1) * ccT (xcrit k) (k + 1) +
      xcrit k / 2 * ((N + 2) / (N + 1)) * pairT k ρ (n + 2) := by
    unfold Sdir
    rw [show k + 1 - ρ - 1 = n + 2 by omega, Nat.cast_add, Nat.cast_one,
      show (k : ℝ) + 1 + ρ + 1 = N + 2 by rw [hNdef]; ring,
      show (k : ℝ) + 1 + ρ = N + 1 by rw [hNdef]; ring]
  rw [hSm, hS0, hSp]
  intro μ hμ
  -- the ingredients
  have hX := (xcrit_pos k).le
  have hV := (ccT_pos (xcrit_pos k) ρ).le
  have hVW : ccT (xcrit k) ρ ≤ ccT (xcrit k) (ρ - 1) := by
    have h := ccT_succ_le (k := k) (n := ρ - 1) (by omega)
    rwa [Nat.sub_add_cancel hρ] at h
  have hw0 := (ccT_pos (xcrit_pos k) k).le
  have hTK := pairT_TK (k := k) (ρ := ρ) (n := n) hk3 hn
  have hT0 := pairT_nonneg k ρ (n + 1)
  have hTm := pairT_nonneg k ρ n
  have hν0 : (0 : ℝ) ≤ (N + 1) / N := by positivity
  rcases le_total μ (1 / ((k : ℝ) * ((k : ℝ) + 2))) with hsmall | hlarge
  · -- small tilt: surplus and defect are compared through `δ = e^μ/(N(N+1))`
    have hB := ccT_tilt_top' hk3 μ
    rw [← ccT_top hk1] at hB
    have hβ := caseI_num hkr hN hμ hsmall
    have hE := pair_defect_small (exp_pos (-μ)).le hTm hν0 (by positivity) (nu_diff1 hN1)
      (nu_diff2 hN1) (hTK μ hμ) (pairT_D_le hk3 hn hsmall)
    refine Sdir_combine hX hV hVW hw0 (δ := exp μ * (1 / (N * (N + 1)))) (by positivity) ?_ ?_
    · exact le_trans (mul_le_mul_of_nonneg_left hβ hw0) hB
    · linarith
  · -- large tilt: the factor `ν` is absorbed by a shift of the tilt, which multiplies the middle
    -- value by `E ≥ 1 - e`, `e = (N-k+1)/(N²(N+2)k)`
    have hc := (exp_pos (μ / k)).le
    have hB := ccT_tilt_top hk3 μ
    rw [← ccT_top hk1] at hB
    have hmid := pairT_mid_le (k := k) (ρ := ρ) (n := n) hk3 hn
    rw [hnr] at hmid
    have hpL : 0 < (N + 2) / (N + 1) / ((N + 1) / N) := by positivity
    have hpM : 0 < N / (N - 1) / ((N + 1) / N) := by positivity
    have hsh := hTK.shift hk0 (Real.log ((N + 2) / (N + 1) / ((N + 1) / N)))
      (Real.log (N / (N - 1) / ((N + 1) / N))) μ (by linarith [nu_shift_small hkr hN])
    rw [Real.exp_log hpL, Real.exp_log hpM] at hsh
    have hsh' := mul_le_mul_of_nonneg_left hsh hν0
    have eR : (N + 1) / N * (exp μ * ((N + 2) / (N + 1) / ((N + 1) / N) * pairT k ρ (n + 2)) +
          exp (-μ) * (N / (N - 1) / ((N + 1) / N) * pairT k ρ n)) =
        exp μ * ((N + 2) / (N + 1) * pairT k ρ (n + 2)) +
          exp (-μ) * (N / (N - 1) * pairT k ρ n) := by
      field_simp
    rw [eR] at hsh'
    have hE1 : 1 - 2 * (N - k + 1) / (N ^ 2 * (N + 2)) / (2 * k) ≤
        exp ((((k : ℝ) + 1) * Real.log ((N + 2) / (N + 1) / ((N + 1) / N)) +
          ((k : ℝ) - 1) * Real.log (N / (N - 1) / ((N + 1) / N))) / (2 * k)) := by
      have h1 := Real.add_one_le_exp ((((k : ℝ) + 1) *
          Real.log ((N + 2) / (N + 1) / ((N + 1) / N)) +
        ((k : ℝ) - 1) * Real.log (N / (N - 1) / ((N + 1) / N))) / (2 * k))
      have h2 := div_le_div_of_nonneg_right (nu_Xi_lb hkr hN) (by positivity : (0 : ℝ) ≤ 2 * k)
      rw [neg_div] at h2
      linarith
    have he : (0 : ℝ) ≤ 2 * (N - k + 1) / (N ^ 2 * (N + 2)) / (2 * k) := by
      have : (0 : ℝ) ≤ N - k + 1 := by linarith
      positivity
    have hm' : (0 : ℝ) ≤ 2 * (k : ℝ) - N := by rw [hNdef]; linarith
    have hE := pair_defect_large hc hν0 hT0 he hsh' hE1 hmid
    refine Sdir_combine hX hV hVW hw0
      (δ := exp (μ / k) * ((N + 1) / N * (2 * (k : ℝ) - N) *
        (2 * (N - k + 1) / (N ^ 2 * (N + 2)) / (2 * k))))
      (mul_nonneg hc (mul_nonneg (mul_nonneg hν0 hm') he)) ?_ ?_
    · exact le_trans (mul_le_mul_of_nonneg_left
        (mul_le_mul_of_nonneg_left (caseII_num hkr hN) hc) hw0) hB
    · linarith

end Parking.FirstLayer