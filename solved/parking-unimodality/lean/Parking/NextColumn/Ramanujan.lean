import Parking.Cayley.Stirling
import Parking.NextColumn.BirthdayLaw

/-!
# The mean of the birthday law (Ramanujan's `Q`-function)

`s_r ≤ √(π r / 2) e^{1/(12 r)} - 1/3`.

Route: `s_r = 𝔭(r)/poissonMass(r) - 1` with `𝔭(m) = e^{-m} ∑_{i ≤ m} m^i/i!`; the sequence
`𝔭(m) - (2/3) poissonMass(m)` is nondecreasing in `m` and is at most `1/2 + poissonMass(M)/3` for
every `M` (`e^{-M} ∑_{i<M} M^i/i! ≤ 1/2`), and `poissonMass(M) → 0`; finally Robbins' bound.
-/

namespace Parking

open Finset

/-- `𝔭(m) = e^{-m} ∑_{i ≤ m} m^i / i!` (probability that a Poisson variable of mean `m` is
`≤ m`). -/
private noncomputable def ppois (m : ℕ) : ℝ :=
  Real.exp (-(m : ℝ)) * ∑ i ∈ range (m + 1), (m : ℝ) ^ i / (i.factorial : ℝ)

/-! ### Step 1: `s_r = 𝔭(r)/poissonMass(r) - 1` -/

/-- `P_j · (r-j)! · r^j = r!` for `j ≤ r`. -/
private theorem Pb_mul {r : ℕ} (hr : 1 ≤ r) {j : ℕ} (hj : j ≤ r) :
    Pb r j * ((r - j).factorial : ℝ) * (r : ℝ) ^ j = (r.factorial : ℝ) := by
  have hr0 : (r : ℝ) ≠ 0 := by
    have : (0 : ℝ) < r := by exact_mod_cast hr
    exact this.ne'
  induction j with
  | zero => simp [Pb]
  | succ j ih =>
    have ih' := ih (by omega)
    have e1 : r - j = (r - (j + 1)) + 1 := by omega
    have e2 : ((r - j).factorial : ℝ)
        = (((r - (j + 1) : ℕ) : ℝ) + 1) * ((r - (j + 1)).factorial : ℝ) := by
      rw [e1, Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
    have e3 : ((r - (j + 1) : ℕ) : ℝ) + 1 = (r : ℝ) - j := by
      rw [Nat.cast_sub hj, Nat.cast_add, Nat.cast_one]
      ring
    rw [e2, e3] at ih'
    rw [Pb_succ, ← ih']
    field

/-- `s_r = 𝔭(r)/poissonMass(r) - 1`. -/
private theorem sbirth_eq {r : ℕ} (hr : 1 ≤ r) : sbirth r = ppois r / poissonMass r - 1 := by
  have hr0 : (0 : ℝ) < r := by exact_mod_cast hr
  have hterm : ∀ i ∈ range (r + 1),
      (r : ℝ) ^ i / (i.factorial : ℝ) = Pb r (r - i) * ren r := by
    intro i hi
    rw [mem_range] at hi
    have h := Pb_mul hr (j := r - i) (Nat.sub_le r i)
    have e : r - (r - i) = i := by omega
    rw [e] at h
    have h1 : (i.factorial : ℝ) ≠ 0 := by positivity
    have h2 : (r : ℝ) ^ (r - i) ≠ 0 := (pow_pos hr0 _).ne'
    have h3 : (r : ℝ) ^ i ≠ 0 := (pow_pos hr0 _).ne'
    have h4 : (r.factorial : ℝ) ≠ 0 := by positivity
    have hp : (r : ℝ) ^ r = (r : ℝ) ^ (r - i) * (r : ℝ) ^ i := by
      rw [← pow_add]
      congr 1
      omega
    have hPb : Pb r (r - i)
        = (r.factorial : ℝ) / ((i.factorial : ℝ) * (r : ℝ) ^ (r - i)) := by
      rw [eq_div_iff (mul_ne_zero h1 h2)]
      linear_combination h
    rw [hPb, ren, hp]
    field
  have hsum : ∑ i ∈ range (r + 1), (r : ℝ) ^ i / (i.factorial : ℝ)
      = (∑ k ∈ range (r + 1), Pb r k) * ren r := by
    rw [sum_congr rfl hterm, ← sum_mul, sum_flip (fun k => Pb r k)]
  have hsplit : ∑ k ∈ range (r + 1), Pb r k = sbirth r + 1 := by
    rw [sum_range_succ', Pb_zero, sbirth, sum_Icc_one_eq_range]
  have h1 : Real.exp (-(r : ℝ)) ≠ 0 := (Real.exp_pos _).ne'
  have h2 : ren r ≠ 0 := (ren_pos r).ne'
  unfold ppois poissonMass
  rw [hsum, hsplit]
  field

/-! ### Step 2: the Poisson law of mean `M` puts mass at most `1/2` below `M` -/

/-- `(2j+1+d)! ≤ (j+1+d)^(2j+1) · d!`, i.e. `(M+j)!/(M-1-j)! ≤ M^(2j+1)` for `M = j+1+d`
(pair the factors `M-i`, `M+i`). -/
private theorem factorial_le_pow_mul (j d : ℕ) :
    (2 * j + 1 + d).factorial ≤ (j + 1 + d) ^ (2 * j + 1) * d.factorial := by
  induction j generalizing d with
  | zero =>
    have h : (1 + d).factorial = (1 + d) ^ 1 * d.factorial := by
      rw [pow_one, Nat.add_comm 1 d, Nat.factorial_succ]
    exact le_of_eq h
  | succ j ih =>
    have h := ih (d + 1)
    have e1 : 2 * (j + 1) + 1 + d = (2 * j + 1 + (d + 1)) + 1 := by omega
    have e2 : j + 1 + (d + 1) = j + 1 + 1 + d := by omega
    have e3 : 2 * (j + 1) + 1 = (2 * j + 1) + 2 := by omega
    rw [e2, Nat.factorial_succ d] at h
    rw [e1, Nat.factorial_succ (2 * j + 1 + (d + 1)), e3, pow_add]
    have h2 : (2 * j + 1 + (d + 1) + 1) * (d + 1) ≤ (j + 1 + 1 + d) ^ 2 := by
      have e : (j + 1 + 1 + d) ^ 2
          = (2 * j + 1 + (d + 1) + 1) * (d + 1) + (j + 1) ^ 2 := by ring
      rw [e]
      exact Nat.le_add_right _ _
    calc (2 * j + 1 + (d + 1) + 1) * (2 * j + 1 + (d + 1)).factorial
        ≤ (2 * j + 1 + (d + 1) + 1)
            * ((j + 1 + 1 + d) ^ (2 * j + 1) * ((d + 1) * d.factorial)) :=
          Nat.mul_le_mul_left _ h
      _ = (j + 1 + 1 + d) ^ (2 * j + 1) * ((2 * j + 1 + (d + 1) + 1) * (d + 1))
            * d.factorial := by ring
      _ ≤ (j + 1 + 1 + d) ^ (2 * j + 1) * (j + 1 + 1 + d) ^ 2 * d.factorial :=
          Nat.mul_le_mul_right _ (Nat.mul_le_mul_left _ h2)

/-- Termwise comparison: for `j < M`, `M^(M-1-j)/(M-1-j)! ≤ M^(M+j)/(M+j)!`. -/
private theorem pois_pair {M j : ℕ} (hj : j < M) :
    (M : ℝ) ^ (M - 1 - j) / ((M - 1 - j).factorial : ℝ)
      ≤ (M : ℝ) ^ (M + j) / ((M + j).factorial : ℝ) := by
  obtain ⟨d, rfl⟩ : ∃ d, M = j + 1 + d := ⟨M - 1 - j, by omega⟩
  have e1 : j + 1 + d - 1 - j = d := by omega
  have e2 : j + 1 + d + j = 2 * j + 1 + d := by omega
  have hfac := factorial_le_pow_mul j d
  have hfacR : ((2 * j + 1 + d).factorial : ℝ)
      ≤ ((j + 1 + d : ℕ) : ℝ) ^ (2 * j + 1) * (d.factorial : ℝ) := by
    exact_mod_cast hfac
  have hd0 : (0 : ℝ) < (d.factorial : ℝ) := by positivity
  have hf0 : (0 : ℝ) < ((2 * j + 1 + d).factorial : ℝ) := by positivity
  have hp : ((j + 1 + d : ℕ) : ℝ) ^ (2 * j + 1 + d)
      = ((j + 1 + d : ℕ) : ℝ) ^ d * ((j + 1 + d : ℕ) : ℝ) ^ (2 * j + 1) := by
    rw [← pow_add]
    congr 1
    omega
  have hd : (0 : ℝ) ≤ ((j + 1 + d : ℕ) : ℝ) ^ d := by positivity
  rw [e1, e2, div_le_div_iff₀ hd0 hf0, hp]
  calc ((j + 1 + d : ℕ) : ℝ) ^ d * ((2 * j + 1 + d).factorial : ℝ)
      ≤ ((j + 1 + d : ℕ) : ℝ) ^ d
          * (((j + 1 + d : ℕ) : ℝ) ^ (2 * j + 1) * (d.factorial : ℝ)) :=
        mul_le_mul_of_nonneg_left hfacR hd
    _ = ((j + 1 + d : ℕ) : ℝ) ^ d * ((j + 1 + d : ℕ) : ℝ) ^ (2 * j + 1)
          * (d.factorial : ℝ) := by ring

/-- `e^{-M} ∑_{i<M} M^i/i! ≤ 1/2`. -/
private theorem poisson_below_half (M : ℕ) :
    Real.exp (-(M : ℝ)) * ∑ i ∈ range M, (M : ℝ) ^ i / (i.factorial : ℝ) ≤ 1 / 2 := by
  have h1 : ∑ i ∈ range M, (M : ℝ) ^ i / (i.factorial : ℝ)
      = ∑ j ∈ range M, (M : ℝ) ^ (M - 1 - j) / ((M - 1 - j).factorial : ℝ) :=
    (sum_range_reflect (fun i => (M : ℝ) ^ i / (i.factorial : ℝ)) M).symm
  have h2 : ∑ j ∈ range M, (M : ℝ) ^ (M - 1 - j) / ((M - 1 - j).factorial : ℝ)
      ≤ ∑ j ∈ range M, (M : ℝ) ^ (M + j) / ((M + j).factorial : ℝ) :=
    sum_le_sum fun j hj => pois_pair (mem_range.1 hj)
  have h3 : ∑ i ∈ range (M + M), (M : ℝ) ^ i / (i.factorial : ℝ)
      = ∑ i ∈ range M, (M : ℝ) ^ i / (i.factorial : ℝ)
        + ∑ j ∈ range M, (M : ℝ) ^ (M + j) / ((M + j).factorial : ℝ) :=
    sum_range_add (fun i => (M : ℝ) ^ i / (i.factorial : ℝ)) M M
  have h4 : ∑ i ∈ range (M + M), (M : ℝ) ^ i / (i.factorial : ℝ) ≤ Real.exp (M : ℝ) :=
    Real.sum_le_exp_of_nonneg (Nat.cast_nonneg M) (M + M)
  have h5 : Real.exp (-(M : ℝ)) * Real.exp (M : ℝ) = 1 := by
    rw [← Real.exp_add, neg_add_cancel, Real.exp_zero]
  have h6 : 2 * ∑ i ∈ range M, (M : ℝ) ^ i / (i.factorial : ℝ) ≤ Real.exp (M : ℝ) := by
    linarith
  have he : 0 < Real.exp (-(M : ℝ)) := Real.exp_pos _
  have h7 := mul_le_mul_of_nonneg_left h6 he.le
  rw [h5] at h7
  linarith

/-! ### Step 3: the sequence `𝔭(m) - (2/3) poissonMass(m)` is nondecreasing -/

/-- `Ψ_m(x) = e^{-x} ∑_{i ≤ m} x^i/i!`. -/
private noncomputable def psiF (m : ℕ) (x : ℝ) : ℝ :=
  Real.exp (-x) * ∑ i ∈ range (m + 1), x ^ i / (i.factorial : ℝ)

/-- `g_m(x) = e^{-x} x^m/m!`. -/
private noncomputable def gF (m : ℕ) (x : ℝ) : ℝ :=
  Real.exp (-x) * x ^ m / (m.factorial : ℝ)

private theorem hasDerivAt_exp_neg (x : ℝ) :
    HasDerivAt (fun y : ℝ => Real.exp (-y)) (-Real.exp (-x)) x :=
  ((hasDerivAt_neg' x).exp).congr_deriv (by ring)

private theorem hasDerivAt_gF (k : ℕ) (x : ℝ) :
    HasDerivAt (gF (k + 1))
      (Real.exp (-x) * (((k : ℝ) + 1) * x ^ k - x ^ (k + 1)) / ((k + 1).factorial : ℝ)) x := by
  have h1 := hasDerivAt_exp_neg x
  have h2 := hasDerivAt_pow (k + 1) x
  have h3 := (h1.fun_mul h2).div_const ((k + 1).factorial : ℝ)
  refine h3.congr_deriv ?_
  simp only [Nat.add_sub_cancel]
  push_cast
  ring

/-- `Ψ_m' = -g_m`. -/
private theorem hasDerivAt_psiF (m : ℕ) (x : ℝ) :
    HasDerivAt (psiF m) (-gF m x) x := by
  induction m with
  | zero =>
    have e : psiF 0 = fun y : ℝ => Real.exp (-y) := by
      funext y
      simp [psiF]
    rw [e]
    exact (hasDerivAt_exp_neg x).congr_deriv (by simp [gF])
  | succ m ih =>
    have hm1 : (m : ℝ) + 1 ≠ 0 := by positivity
    have hmf : (m.factorial : ℝ) ≠ 0 := by positivity
    have e : psiF (m + 1) = fun y : ℝ => psiF m y + gF (m + 1) y := by
      funext y
      unfold psiF gF
      rw [sum_range_succ (fun i => y ^ i / (i.factorial : ℝ)) (m + 1)]
      ring
    rw [e]
    refine (ih.fun_add (hasDerivAt_gF m x)).congr_deriv ?_
    unfold gF
    rw [Nat.factorial_succ m]
    push_cast
    field

private theorem ppois_eq_psiF (m : ℕ) : ppois m = psiF m (m : ℝ) := rfl

private theorem poissonMass_eq_gF (m : ℕ) : poissonMass m = gF m (m : ℝ) := by
  unfold poissonMass ren gF
  ring

private theorem ppois_succ (m : ℕ) :
    ppois (m + 1) = psiF m ((m + 1 : ℕ) : ℝ) + poissonMass (m + 1) := by
  unfold ppois psiF poissonMass ren
  rw [sum_range_succ (fun i => ((m + 1 : ℕ) : ℝ) ^ i / (i.factorial : ℝ)) (m + 1)]
  ring

private theorem poissonMass_succ_eq_gF (m : ℕ) : poissonMass (m + 1) = gF m ((m + 1 : ℕ) : ℝ) := by
  have h1 : (m : ℝ) + 1 ≠ 0 := by positivity
  have h2 : (m.factorial : ℝ) ≠ 0 := by positivity
  unfold poissonMass ren gF
  rw [Nat.factorial_succ m, pow_succ ((m + 1 : ℕ) : ℝ) m]
  push_cast
  field

/-- `1 + u ≤ exp (u - u²/(2(1+u)))` for `u ≥ 0` (from `1 + s + s²/2 ≤ e^s`). -/
private theorem one_add_le_exp_aux {u : ℝ} (hu : 0 ≤ u) :
    1 + u ≤ Real.exp (u * (2 + u) / (2 * (1 + u))) := by
  have h1 : 0 < 1 + u := by linarith
  have h1' : 1 + u ≠ 0 := h1.ne'
  have hs0 : 0 ≤ u * (2 + u) / (2 * (1 + u)) :=
    div_nonneg (mul_nonneg hu (by linarith)) (by linarith)
  have hq := Real.quadratic_le_exp_of_nonneg hs0
  have e : 1 + u * (2 + u) / (2 * (1 + u)) + (u * (2 + u) / (2 * (1 + u))) ^ 2 / 2
      = 1 + u + u ^ 4 / (8 * (1 + u) ^ 2) := by
    field
  have h4 : 0 ≤ u ^ 4 / (8 * (1 + u) ^ 2) := by positivity
  rw [e] at hq
  linarith

/-- `(1+u)^m (1 + m u²/(2(1+u))) ≤ e^{mu}` for `u ≥ 0`, `m = k+1`. -/
private theorem key_core (k : ℕ) {u : ℝ} (hu : 0 ≤ u) :
    (1 + u) ^ (k + 1) * (1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)))
      ≤ Real.exp (((k : ℝ) + 1) * u) := by
  have h1u : 0 < 1 + u := by linarith
  have h1u' : 1 + u ≠ 0 := h1u.ne'
  have hA := one_add_le_exp_aux hu
  have hB : (1 + u) ^ (k + 1)
      ≤ Real.exp (((k : ℝ) + 1) * (u * (2 + u) / (2 * (1 + u)))) := by
    have h := pow_le_pow_left₀ h1u.le hA (k + 1)
    rw [← Real.exp_nat_mul] at h
    push_cast at h
    exact h
  have hc0 : 0 ≤ ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)) :=
    div_nonneg (mul_nonneg (by positivity) (sq_nonneg u)) (by linarith)
  have hC : 1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u))
      ≤ Real.exp (((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u))) := by
    have := Real.add_one_le_exp (((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)))
    linarith
  have hC0 : 0 ≤ 1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)) := by linarith
  calc (1 + u) ^ (k + 1) * (1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)))
      ≤ Real.exp (((k : ℝ) + 1) * (u * (2 + u) / (2 * (1 + u))))
          * Real.exp (((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u))) :=
        mul_le_mul hB hC hC0 (Real.exp_pos _).le
    _ = Real.exp (((k : ℝ) + 1) * u) := by
        rw [← Real.exp_add]
        congr 1
        field

/-- The inequality behind `H' ≥ 0`:
`e^{-x} x^k (2x + (x-m)²) ≤ 2 e^{-m} m^m` for `x ≥ m = k+1`. -/
private theorem key_K (k : ℕ) {x : ℝ} (hx : (k : ℝ) + 1 ≤ x) :
    Real.exp (-x) * (x ^ k * (2 * x + (x - ((k : ℝ) + 1)) ^ 2))
      ≤ 2 * (Real.exp (-((k : ℝ) + 1)) * ((k : ℝ) + 1) ^ (k + 1)) := by
  have hM0 : (0 : ℝ) < (k : ℝ) + 1 := by positivity
  have hMne : (k : ℝ) + 1 ≠ 0 := hM0.ne'
  obtain ⟨u, hu0, rfl⟩ : ∃ u : ℝ, 0 ≤ u ∧ x = ((k : ℝ) + 1) * (1 + u) :=
    ⟨(x - ((k : ℝ) + 1)) / ((k : ℝ) + 1), div_nonneg (by linarith) hM0.le, by field⟩
  have h1u : 0 < 1 + u := by linarith
  have h1u' : 1 + u ≠ 0 := h1u.ne'
  have hcore := key_core k hu0
  have e1 : (((k : ℝ) + 1) * (1 + u)) ^ k
        * (2 * (((k : ℝ) + 1) * (1 + u)) + (((k : ℝ) + 1) * (1 + u) - ((k : ℝ) + 1)) ^ 2)
      = 2 * ((k : ℝ) + 1) ^ (k + 1)
        * ((1 + u) ^ (k + 1) * (1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)))) := by
    rw [mul_pow, pow_succ ((k : ℝ) + 1) k, pow_succ (1 + u) k]
    generalize ((k : ℝ) + 1) ^ k = A
    generalize (1 + u) ^ k = B
    field
  have e2 : Real.exp (-(((k : ℝ) + 1) * (1 + u))) * Real.exp (((k : ℝ) + 1) * u)
      = Real.exp (-((k : ℝ) + 1)) := by
    rw [← Real.exp_add]
    congr 1
    ring
  rw [e1]
  calc Real.exp (-(((k : ℝ) + 1) * (1 + u))) * (2 * ((k : ℝ) + 1) ^ (k + 1)
          * ((1 + u) ^ (k + 1) * (1 + ((k : ℝ) + 1) * u ^ 2 / (2 * (1 + u)))))
      ≤ Real.exp (-(((k : ℝ) + 1) * (1 + u))) * (2 * ((k : ℝ) + 1) ^ (k + 1)
          * Real.exp (((k : ℝ) + 1) * u)) :=
        mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hcore (by positivity))
          (Real.exp_pos _).le
    _ = 2 * (Real.exp (-((k : ℝ) + 1)) * ((k : ℝ) + 1) ^ (k + 1)) := by
        linear_combination (2 * ((k : ℝ) + 1) ^ (k + 1)) * e2

/-- `H(x) = Ψ_m(x) + (x - m) ((2/3) g_m(m) + (1/3) g_m(x))`, `m = k+1`. -/
private noncomputable def HF (k : ℕ) (x : ℝ) : ℝ :=
  psiF (k + 1) x
    + (x - ((k : ℝ) + 1)) * (2 / 3 * gF (k + 1) ((k : ℝ) + 1) + 1 / 3 * gF (k + 1) x)

/-- The derivative of `HF k`. -/
private noncomputable def HF' (k : ℕ) (x : ℝ) : ℝ :=
  -gF (k + 1) x
    + (1 * (2 / 3 * gF (k + 1) ((k : ℝ) + 1) + 1 / 3 * gF (k + 1) x)
      + (x - ((k : ℝ) + 1))
        * (1 / 3 * (Real.exp (-x) * (((k : ℝ) + 1) * x ^ k - x ^ (k + 1))
            / ((k + 1).factorial : ℝ))))

private theorem hasDerivAt_HF (k : ℕ) (x : ℝ) : HasDerivAt (HF k) (HF' k x) x := by
  have h1 := hasDerivAt_psiF (k + 1) x
  have h2 : HasDerivAt (fun y : ℝ => y - ((k : ℝ) + 1)) 1 x :=
    (hasDerivAt_id' x).sub_const ((k : ℝ) + 1)
  have h3 : HasDerivAt
      (fun y : ℝ => 2 / 3 * gF (k + 1) ((k : ℝ) + 1) + 1 / 3 * gF (k + 1) y)
      (1 / 3 * (Real.exp (-x) * (((k : ℝ) + 1) * x ^ k - x ^ (k + 1))
            / ((k + 1).factorial : ℝ))) x :=
    ((hasDerivAt_gF k x).const_mul (1 / 3)).const_add (2 / 3 * gF (k + 1) ((k : ℝ) + 1))
  exact h1.fun_add (h2.fun_mul h3)

private theorem HF'_nonneg (k : ℕ) {x : ℝ} (hx : (k : ℝ) + 1 ≤ x) : 0 ≤ HF' k x := by
  have hK := key_K k hx
  have hf : (0 : ℝ) < ((k + 1).factorial : ℝ) := by positivity
  have hfne : ((k + 1).factorial : ℝ) ≠ 0 := hf.ne'
  have e : HF' k x = (2 * (Real.exp (-((k : ℝ) + 1)) * ((k : ℝ) + 1) ^ (k + 1))
      - Real.exp (-x) * (x ^ k * (2 * x + (x - ((k : ℝ) + 1)) ^ 2)))
        / (3 * ((k + 1).factorial : ℝ)) := by
    unfold HF' gF
    field
  rw [e]
  exact div_nonneg (by linarith) (by positivity)

private theorem HF_le (k : ℕ) : HF k ((k : ℝ) + 1) ≤ HF k ((k : ℝ) + 1 + 1) := by
  have hmono : MonotoneOn (HF k) (Set.Ici ((k : ℝ) + 1)) := by
    refine monotoneOn_of_hasDerivWithinAt_nonneg (convex_Ici _) (f' := HF' k) ?_ ?_ ?_
    · exact fun x _ => (hasDerivAt_HF k x).continuousAt.continuousWithinAt
    · exact fun x _ => (hasDerivAt_HF k x).hasDerivWithinAt
    · intro x hx
      exact HF'_nonneg k (Set.mem_Ici.1 (interior_subset hx))
  exact hmono (Set.mem_Ici.2 le_rfl) (Set.mem_Ici.2 (by linarith)) (by linarith)

/-- The sequence `𝔭(m) - (2/3) poissonMass(m)` is nondecreasing. -/
private theorem ppois_step {m : ℕ} (hm : 1 ≤ m) :
    ppois m - 2 / 3 * poissonMass m ≤ ppois (m + 1) - 2 / 3 * poissonMass (m + 1) := by
  obtain ⟨k, rfl⟩ : ∃ k, m = k + 1 := ⟨m - 1, by omega⟩
  have h := HF_le k
  have hc : ((k + 1 : ℕ) : ℝ) = (k : ℝ) + 1 := Nat.cast_add_one k
  have hc2 : ((k + 1 + 1 : ℕ) : ℝ) = (k : ℝ) + 1 + 1 := by
    rw [Nat.cast_add_one (k + 1), hc]
  have e1 : ppois (k + 1) = psiF (k + 1) ((k : ℝ) + 1) :=
    (ppois_eq_psiF (k + 1)).trans (by rw [hc])
  have e2 : poissonMass (k + 1) = gF (k + 1) ((k : ℝ) + 1) :=
    (poissonMass_eq_gF (k + 1)).trans (by rw [hc])
  have e3 : ppois (k + 1 + 1) = psiF (k + 1) ((k : ℝ) + 1 + 1) + poissonMass (k + 1 + 1) :=
    (ppois_succ (k + 1)).trans (by rw [hc2])
  have e4 : poissonMass (k + 1 + 1) = gF (k + 1) ((k : ℝ) + 1 + 1) :=
    (poissonMass_succ_eq_gF (k + 1)).trans (by rw [hc2])
  have hH0 : HF k ((k : ℝ) + 1) = psiF (k + 1) ((k : ℝ) + 1) := by
    unfold HF
    rw [sub_self, zero_mul, add_zero]
  have hH1 : HF k ((k : ℝ) + 1 + 1) = psiF (k + 1) ((k : ℝ) + 1 + 1)
      + (2 / 3 * gF (k + 1) ((k : ℝ) + 1) + 1 / 3 * gF (k + 1) ((k : ℝ) + 1 + 1)) := by
    have e : (k : ℝ) + 1 + 1 - ((k : ℝ) + 1) = 1 := by ring
    unfold HF
    rw [e, one_mul]
  rw [hH0, hH1] at h
  rw [e1, e3, e2, e4]
  linarith

/-! ### Step 4: `𝔭(m) ≤ 1/2 + (2/3) poissonMass(m)` -/

/-- `𝔭(m) ≤ 1/2 + (2/3) poissonMass(m)`. -/
private theorem ppois_le {m : ℕ} (hm : 1 ≤ m) : ppois m ≤ 1 / 2 + 2 / 3 * poissonMass m := by
  have hmono : ∀ M, m ≤ M → ppois m - 2 / 3 * poissonMass m ≤ ppois M - 2 / 3 * poissonMass M := by
    intro M hM
    induction M, hM using Nat.le_induction with
    | base => exact le_rfl
    | succ k hk ih => exact ih.trans (ppois_step (le_trans hm hk))
  have hbound : ∀ M, 1 ≤ M → ppois M - 2 / 3 * poissonMass M
      ≤ 1 / 2 + 1 / 3 * (Real.sqrt (2 * Real.pi * (M : ℝ)))⁻¹ := by
    intro M hM
    have h1 := poisson_below_half M
    have h2 := poissonMass_le hM
    have h3 : ppois M
        = Real.exp (-(M : ℝ)) * ∑ i ∈ range M, (M : ℝ) ^ i / (i.factorial : ℝ) + poissonMass M := by
      unfold ppois poissonMass ren
      rw [sum_range_succ (fun i => (M : ℝ) ^ i / (i.factorial : ℝ)) M]
      ring
    rw [one_div] at h2
    linarith
  have hlim : Filter.Tendsto
      (fun M : ℕ => 1 / 2 + 1 / 3 * (Real.sqrt (2 * Real.pi * (M : ℝ)))⁻¹)
      Filter.atTop (nhds (1 / 2 + 1 / 3 * 0)) := by
    have h1 : Filter.Tendsto (fun M : ℕ => 2 * Real.pi * (M : ℝ)) Filter.atTop Filter.atTop :=
      Filter.Tendsto.const_mul_atTop (mul_pos two_pos Real.pi_pos)
        (tendsto_natCast_atTop_atTop (R := ℝ))
    have h2 : Filter.Tendsto (fun M : ℕ => Real.sqrt (2 * Real.pi * (M : ℝ))) Filter.atTop
        Filter.atTop := Real.tendsto_sqrt_atTop.comp h1
    have h3 : Filter.Tendsto (fun M : ℕ => (Real.sqrt (2 * Real.pi * (M : ℝ)))⁻¹) Filter.atTop
        (nhds 0) := tendsto_inv_atTop_zero.comp h2
    exact (h3.const_mul (1 / 3)).const_add (1 / 2)
  have hev : ∀ᶠ M : ℕ in Filter.atTop, ppois m - 2 / 3 * poissonMass m
      ≤ 1 / 2 + 1 / 3 * (Real.sqrt (2 * Real.pi * (M : ℝ)))⁻¹ := by
    filter_upwards [Filter.eventually_ge_atTop m] with M hM
    exact (hmono M hM).trans (hbound M (le_trans hm hM))
  have hfin := ge_of_tendsto hlim hev
  linarith

/-! ### Step 5: the bound for `s_r` -/

/-- **Upper bound for the mean of the birthday law**:
`s_r ≤ √(π r / 2) e^{1/(12 r)} - 1/3`. -/
theorem sbirth_le {r : ℕ} (hr : 1 ≤ r) :
    sbirth r ≤ Real.sqrt (Real.pi * r / 2) * Real.exp (1 / (12 * (r : ℝ))) - 1 / 3 := by
  have hr0 : (0 : ℝ) < r := by exact_mod_cast hr
  have hR : 0 < poissonMass r := poissonMass_pos r
  have hRne : poissonMass r ≠ 0 := hR.ne'
  have hf : (0 : ℝ) < r.factorial := by positivity
  have hP : 0 < ((r : ℝ) / Real.exp 1) ^ r := by positivity
  have h2P : 0 < 2 * ((r : ℝ) / Real.exp 1) ^ r := by positivity
  have h4 : Real.sqrt 4 = 2 := by
    rw [show (4 : ℝ) = 2 ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  have hs : Real.sqrt (Real.pi * r / 2) = Real.sqrt (2 * Real.pi * r) / 2 := by
    rw [show Real.pi * (r : ℝ) / 2 = 2 * Real.pi * r / 4 by ring,
      Real.sqrt_div' (2 * Real.pi * r) (by norm_num : (0 : ℝ) ≤ 4), h4]
  have h1 : ppois r / poissonMass r ≤ (1 / 2 + 2 / 3 * poissonMass r) / poissonMass r :=
    div_le_div_of_nonneg_right (ppois_le hr) hR.le
  have h2 : (1 / 2 + 2 / 3 * poissonMass r) / poissonMass r = 1 / (2 * poissonMass r) + 2 / 3 := by
    field
  have h3 : 1 / (2 * poissonMass r)
      ≤ Real.sqrt (2 * Real.pi * r) / 2 * Real.exp (1 / (12 * (r : ℝ))) := by
    have hfac := factorial_le_robbins hr
    have e : 1 / (2 * poissonMass r) = (r.factorial : ℝ) / (2 * ((r : ℝ) / Real.exp 1) ^ r) := by
      rw [poissonMass_eq]
      generalize ((r : ℝ) / Real.exp 1) ^ r = P at hP ⊢
      have hPne : P ≠ 0 := hP.ne'
      have hfne : (r.factorial : ℝ) ≠ 0 := hf.ne'
      field
    rw [e, div_le_iff₀ h2P]
    calc (r.factorial : ℝ)
        ≤ Real.sqrt (2 * Real.pi * r) * ((r : ℝ) / Real.exp 1) ^ r
            * Real.exp (1 / (12 * (r : ℝ))) := hfac
      _ = Real.sqrt (2 * Real.pi * r) / 2 * Real.exp (1 / (12 * (r : ℝ)))
            * (2 * ((r : ℝ) / Real.exp 1) ^ r) := by ring
  calc sbirth r = ppois r / poissonMass r - 1 := sbirth_eq hr
    _ ≤ (1 / 2 + 2 / 3 * poissonMass r) / poissonMass r - 1 := sub_le_sub_right h1 1
    _ = 1 / (2 * poissonMass r) - 1 / 3 := by rw [h2]; ring
    _ ≤ Real.sqrt (2 * Real.pi * r) / 2 * Real.exp (1 / (12 * (r : ℝ))) - 1 / 3 :=
        sub_le_sub_right h3 _
    _ = Real.sqrt (Real.pi * r / 2) * Real.exp (1 / (12 * (r : ℝ))) - 1 / 3 := by rw [hs]

end Parking
