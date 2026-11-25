import Parking.Cayley.Stirling
import Parking.Cayley.TreeSeries

/-!
# The tree function at its singularity

* `hasSum_borel` : `∑_{j ≥ 1} e^{-j} a_j = 1` (the Borel law is a probability law, `T(1/e) = 1`).
* `hasSum_cc`    : `∑_{n ≥ 0} e^{-n} c_n = e`.
* `hasSum_eps`   : `∑_{m ≥ 1} e^{-m} ε_m = 1 - e^{-1}`.

Proved from the finite convolution identities `ren_conv`, `eps_conv` by a renewal argument; the only
analytic input is `poissonMass n ≥ c/√n` (so `∑ poissonMass = ∞`), where
`poissonMass n = e^{-n} n^n/n!`.

## Structure of the proof

For real sequences `f, g ≥ 0` with `f 0 = 0`, `g 0 = 1` and the renewal equation
`g n = ∑_{m ≤ n} f m * g (n - m)` (`n ≥ 1`), write `F M = ∑_{m ≤ M} f m`, `G M = ∑_{n ≤ M} g n`.
Summing the renewal equation gives `G M - 1 = ∑_{m ≤ M} f m * G (M - m)` (`psum_conv`), hence
`F M * G k ≤ G (M + k) - 1` (`psum_conv_ge`) and `G M - 1 ≤ F M * G M` (`psum_conv_le`).

In both cases below the partial sums `F M` are squeezed between `1 - 1 / G M` and their limit
(`hasSum_of_psum_le`).

* If `G → ∞` and `g ≤ 1`, then `F M ≤ 1` and `F M ≥ 1 - 1 / G M → 1` (`renewal_hasSum_one`).
* If `G → E`, then `F M ≤ 1 - 1/E` and `F M ≥ 1 - 1 / G M → 1 - 1/E` (`renewal_hasSum_inv`).

The first case is applied to `f = e^{-j} a_j`, `g = poissonMass`; the second to `f = e^{-m} ε_m`,
`g = e^{-n} c_n`.
-/

namespace Parking

open Finset Filter Topology

/-! ### Partial sums and the summed renewal equation -/

/-- Partial sum `∑_{i ≤ n} a i`. -/
private noncomputable def psum (a : ℕ → ℝ) (n : ℕ) : ℝ := ∑ i ∈ range (n + 1), a i

private theorem psum_zero (a : ℕ → ℝ) : psum a 0 = a 0 :=
  sum_range_one a

private theorem psum_succ (a : ℕ → ℝ) (n : ℕ) : psum a (n + 1) = psum a n + a (n + 1) :=
  sum_range_succ a (n + 1)

private theorem psum_nonneg {a : ℕ → ℝ} (ha : ∀ i, 0 ≤ a i) (n : ℕ) : 0 ≤ psum a n :=
  sum_nonneg fun i _ => ha i

private theorem psum_mono {a : ℕ → ℝ} (ha : ∀ i, 0 ≤ a i) : Monotone (psum a) :=
  monotone_nat_of_le_succ fun n => by
    rw [psum_succ]
    linarith [ha (n + 1)]

private theorem one_le_psum {g : ℕ → ℝ} (hg : ∀ n, 0 ≤ g n) (hg0 : g 0 = 1) (n : ℕ) :
    1 ≤ psum g n := by
  have h := psum_mono hg (Nat.zero_le n)
  rw [psum_zero, hg0] at h
  exact h

/-- If `g ≤ 1` then `M` further terms add at most `M`. -/
private theorem psum_add_le {g : ℕ → ℝ} (hg1 : ∀ n, g n ≤ 1) (M k : ℕ) :
    psum g (M + k) ≤ psum g k + M := by
  induction M with
  | zero => simp
  | succ M ih =>
    have e : M + 1 + k = (M + k) + 1 := by omega
    rw [e, psum_succ]
    push_cast
    linarith [hg1 (M + k + 1)]

/-- The summed renewal equation: `G M - 1 = ∑_{m ≤ M} f m * G (M - m)`. -/
private theorem psum_conv {f g : ℕ → ℝ} (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n) (M : ℕ) :
    ∑ m ∈ range (M + 1), f m * psum g (M - m) = psum g M - 1 := by
  induction M with
  | zero => rw [zero_add, sum_range_one, hf0, zero_mul, psum_zero, hg0, sub_self]
  | succ M ih =>
    have h1 : ∀ m ∈ range (M + 1), f m * psum g (M + 1 - m)
        = f m * psum g (M - m) + f m * g (M + 1 - m) := by
      intro m hm
      rw [mem_range] at hm
      have e : M + 1 - m = (M - m) + 1 := by omega
      rw [e, psum_succ, mul_add]
    have h2 : ∑ m ∈ range (M + 1), f m * g (M + 1 - m) + f (M + 1) * g 0 = g (M + 1) := by
      rw [← hconv (M + 1) (Nat.le_add_left 1 M), sum_range_succ _ (M + 1), Nat.sub_self]
    rw [sum_range_succ, sum_congr rfl h1, sum_add_distrib, ih, Nat.sub_self, psum_zero, psum_succ]
    linarith

/-- Lower bound for the summed renewal equation: `F M * G k ≤ G (M + k) - 1`. -/
private theorem psum_conv_ge {f g : ℕ → ℝ} (hf : ∀ m, 0 ≤ f m) (hg : ∀ n, 0 ≤ g n)
    (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n) (M k : ℕ) :
    psum f M * psum g k ≤ psum g (M + k) - 1 := by
  have h0 := psum_conv hf0 hg0 hconv (M + k)
  have h1 : ∑ m ∈ range (M + 1), f m * psum g (M + k - m)
      ≤ ∑ m ∈ range (M + k + 1), f m * psum g (M + k - m) :=
    sum_le_sum_of_subset_of_nonneg (range_subset_range.2 (by omega))
      (fun m _ _ => mul_nonneg (hf m) (psum_nonneg hg _))
  have h2 : ∑ m ∈ range (M + 1), f m * psum g k
      ≤ ∑ m ∈ range (M + 1), f m * psum g (M + k - m) := by
    apply sum_le_sum
    intro m hm
    rw [mem_range] at hm
    exact mul_le_mul_of_nonneg_left (psum_mono hg (by omega)) (hf m)
  have h3 : ∑ m ∈ range (M + 1), f m * psum g k = psum f M * psum g k :=
    (sum_mul (range (M + 1)) f (psum g k)).symm
  linarith

/-- Upper bound for the summed renewal equation: `G M - 1 ≤ F M * G M`. -/
private theorem psum_conv_le {f g : ℕ → ℝ} (hf : ∀ m, 0 ≤ f m) (hg : ∀ n, 0 ≤ g n)
    (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n) (M : ℕ) :
    psum g M - 1 ≤ psum f M * psum g M := by
  have h0 := psum_conv hf0 hg0 hconv M
  have h2 : ∑ m ∈ range (M + 1), f m * psum g (M - m)
      ≤ ∑ m ∈ range (M + 1), f m * psum g M := by
    apply sum_le_sum
    intro m _
    exact mul_le_mul_of_nonneg_left (psum_mono hg (Nat.sub_le M m)) (hf m)
  have h3 : ∑ m ∈ range (M + 1), f m * psum g M = psum f M * psum g M :=
    (sum_mul (range (M + 1)) f (psum g M)).symm
  linarith

/-- The squeeze: `F M ≥ 1 - 1 / G M` by `psum_conv_le`, so if `F M ≤ L` for all `M` and
`1 - 1 / G M → L`, then `∑ f = L`. -/
private theorem hasSum_of_psum_le {f g : ℕ → ℝ} {L : ℝ} (hf : ∀ m, 0 ≤ f m) (hg : ∀ n, 0 ≤ g n)
    (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n)
    (hub : ∀ M, psum f M ≤ L)
    (hlim : Tendsto (fun M => 1 - (psum g M)⁻¹) atTop (𝓝 L)) : HasSum f L := by
  have hlow : ∀ M, 1 - (psum g M)⁻¹ ≤ psum f M := by
    intro M
    have hp : 0 < psum g M := by linarith [one_le_psum hg hg0 M]
    have h2 : 1 - (psum g M)⁻¹ = (psum g M - 1) / psum g M := by
      rw [sub_div, div_self hp.ne', one_div]
    rw [h2, div_le_iff₀ hp]
    exact psum_conv_le hf hg hf0 hg0 hconv M
  have hpart : Tendsto (psum f) atTop (𝓝 L) :=
    tendsto_of_tendsto_of_tendsto_of_le_of_le' hlim tendsto_const_nhds
      (Eventually.of_forall hlow) (Eventually.of_forall hub)
  rw [hasSum_iff_tendsto_nat_of_nonneg hf]
  exact (tendsto_add_atTop_iff_nat (f := fun n => ∑ i ∈ range n, f i) 1).mp hpart

/-! ### The two renewal theorems -/

/-- Renewal theorem, divergent case: if `g ≤ 1` and `∑ g = ∞`, then `∑ f = 1`. -/
private theorem renewal_hasSum_one {f g : ℕ → ℝ} (hf : ∀ m, 0 ≤ f m) (hg : ∀ n, 0 ≤ g n)
    (hg1 : ∀ n, g n ≤ 1) (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n)
    (hdiv : Tendsto (psum g) atTop atTop) : HasSum f 1 := by
  have hub : ∀ M, psum f M ≤ 1 := by
    intro M
    by_contra hcon
    have hcon' : 0 < psum f M - 1 := by linarith [not_le.mp hcon]
    obtain ⟨k, hk⟩ := (hdiv.eventually_ge_atTop ((M : ℝ) / (psum f M - 1))).exists
    have h1 := psum_conv_ge hf hg hf0 hg0 hconv M k
    have h2 := psum_add_le hg1 M k
    rw [div_le_iff₀ hcon'] at hk
    nlinarith [hk, h1, h2]
  have hlim : Tendsto (fun M => 1 - (psum g M)⁻¹) atTop (𝓝 1) := by
    have h : Tendsto (fun M => (psum g M)⁻¹) atTop (𝓝 0) := tendsto_inv_atTop_zero.comp hdiv
    have h2 : Tendsto (fun M => 1 - (psum g M)⁻¹) atTop (𝓝 (1 - 0)) := tendsto_const_nhds.sub h
    rwa [sub_zero] at h2
  exact hasSum_of_psum_le hf hg hf0 hg0 hconv hub hlim

/-- Renewal theorem, convergent case: if `∑ g = E`, then `∑ f = 1 - 1/E`. -/
private theorem renewal_hasSum_inv {f g : ℕ → ℝ} {E : ℝ} (hf : ∀ m, 0 ≤ f m)
    (hg : ∀ n, 0 ≤ g n) (hf0 : f 0 = 0) (hg0 : g 0 = 1)
    (hconv : ∀ n, 1 ≤ n → ∑ m ∈ range (n + 1), f m * g (n - m) = g n)
    (hE : HasSum g E) : HasSum f (1 - E⁻¹) := by
  have hU : Tendsto (psum g) atTop (𝓝 E) :=
    (tendsto_add_atTop_iff_nat (f := fun n => ∑ i ∈ range n, g i) 1).mpr hE.tendsto_sum_nat
  have hUle : ∀ n, psum g n ≤ E := fun n =>
    sum_le_hasSum (range (n + 1)) (fun i _ => hg i) hE
  have hEpos : 0 < E := by linarith [one_le_psum hg hg0 0, hUle 0]
  have hub : ∀ M, psum f M ≤ 1 - E⁻¹ := by
    intro M
    have h1 : ∀ k, psum f M * psum g k ≤ E - 1 := by
      intro k
      have h := psum_conv_ge hf hg hf0 hg0 hconv M k
      linarith [hUle (M + k)]
    have h2 : Tendsto (fun k => psum f M * psum g k) atTop (𝓝 (psum f M * E)) :=
      hU.const_mul (psum f M)
    have h3 : psum f M * E ≤ E - 1 := le_of_tendsto' h2 h1
    have h4 : 1 - E⁻¹ = (E - 1) / E := by
      rw [sub_div, div_self hEpos.ne', one_div]
    rw [h4, le_div_iff₀ hEpos]
    exact h3
  exact hasSum_of_psum_le hf hg hf0 hg0 hconv hub
    (tendsto_const_nhds.sub (hU.inv₀ hEpos.ne'))

/-! ### The concrete renewal equations -/

/-- Multiplying a convolution by `e^{-n}` distributes the exponential weights. -/
private theorem exp_conv (a b : ℕ → ℝ) (n : ℕ) :
    ∑ m ∈ range (n + 1),
        (Real.exp (-(m : ℝ)) * a m) * (Real.exp (-((n - m : ℕ) : ℝ)) * b (n - m))
      = Real.exp (-(n : ℝ)) * ∑ m ∈ range (n + 1), a m * b (n - m) := by
  rw [mul_sum]
  apply sum_congr rfl
  intro m hm
  rw [mem_range] at hm
  have hle : m ≤ n := by omega
  have e : Real.exp (-(n : ℝ)) = Real.exp (-(m : ℝ)) * Real.exp (-((n - m : ℕ) : ℝ)) := by
    rw [← Real.exp_add, Nat.cast_sub hle]
    congr 1
    ring
  rw [e]
  ring

/-- `eps_conv` as a sum over `range (n + 1)`: the term `m = 0` vanishes. -/
private theorem eps_conv_range {n : ℕ} (hn : 1 ≤ n) :
    ∑ m ∈ range (n + 1), eps m * cc (n - m) = cc n := by
  rw [Finset.sum_range_eq_add_Ico _ (show 0 < n + 1 by omega), Finset.Ico_add_one_right_eq_Icc,
    eps_conv hn]
  simp [eps]

/-- The renewal equation (R): `poissonMass n = ∑_{j ≤ n} Bor j * poissonMass (n - j)` for
`n ≥ 1`. -/
private theorem poissonMass_conv {n : ℕ} (hn : 1 ≤ n) :
    ∑ m ∈ range (n + 1), (Real.exp (-(m : ℝ)) * cay m) * poissonMass (n - m) = poissonMass n := by
  have h := exp_conv cay ren n
  rw [ren_conv hn] at h
  exact h

/-! ### The renewal masses: `poissonMass ≤ 1` and `∑ poissonMass = ∞` -/

private theorem poissonMass_le_one (n : ℕ) : poissonMass n ≤ 1 := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · exact poissonMass_zero.le
  · have hn1 : 1 ≤ n := Nat.succ_le_of_lt hn
    have hn' : (1 : ℝ) ≤ n := by exact_mod_cast hn1
    have hpi := Real.two_le_pi
    have hprod : (0 : ℝ) ≤ (Real.pi - 2) * ((n : ℝ) - 1) :=
      mul_nonneg (by linarith) (by linarith)
    have h1 : (1 : ℝ) ≤ 2 * Real.pi * n := by nlinarith [hprod, hpi, hn']
    have h2 : (1 : ℝ) ≤ Real.sqrt (2 * Real.pi * n) := by
      have h := Real.sqrt_le_sqrt h1
      rwa [Real.sqrt_one] at h
    have h3 : (1 : ℝ) / Real.sqrt (2 * Real.pi * n) ≤ 1 := by
      rw [div_le_one (by linarith)]
      exact h2
    exact (poissonMass_le hn1).trans h3

/-- For `1 ≤ k ≤ n`: `poissonMass k ≥ (11/12) / √(2πn)`. -/
private theorem poissonMass_ge_of_le {k n : ℕ} (hk : 1 ≤ k) (hkn : k ≤ n) :
    (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi * n) ≤ poissonMass k := by
  have hk1 : (1 : ℝ) ≤ k := by exact_mod_cast hk
  have hkn' : (k : ℝ) ≤ n := by exact_mod_cast hkn
  have h2pi : (0 : ℝ) < 2 * Real.pi := mul_pos zero_lt_two Real.pi_pos
  have hs0 : 0 < Real.sqrt (2 * Real.pi * k) :=
    Real.sqrt_pos.mpr (mul_pos h2pi (by linarith))
  have hs : Real.sqrt (2 * Real.pi * k) ≤ Real.sqrt (2 * Real.pi * n) :=
    Real.sqrt_le_sqrt (mul_le_mul_of_nonneg_left hkn' h2pi.le)
  have h12 : (11 / 12 : ℝ) ≤ 1 - 1 / (12 * (k : ℝ)) := by
    have h : 1 / (12 * (k : ℝ)) ≤ 1 / 12 :=
      one_div_le_one_div_of_le (by norm_num) (by linarith)
    linarith
  calc (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi * n)
      ≤ (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi * k) :=
        div_le_div_of_nonneg_left (by norm_num) hs0 hs
    _ ≤ (1 - 1 / (12 * (k : ℝ))) / Real.sqrt (2 * Real.pi * k) :=
        div_le_div_of_nonneg_right h12 hs0.le
    _ ≤ poissonMass k := poissonMass_ge hk

private theorem sqrt_alg {c t s x : ℝ} (ht : t ≠ 0) (hs : s ≠ 0) (hx : s * s = x) :
    x * (c / (t * s)) = c / t * s := by
  subst hx
  field

/-- `∑_{i ≤ n} poissonMass i ≥ (11/12) √n / √(2π)`. -/
private theorem psum_poissonMass_ge (n : ℕ) :
    (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi) * Real.sqrt n ≤ psum poissonMass n := by
  have hnn : ∀ k, 0 ≤ poissonMass k := fun k => (poissonMass_pos k).le
  have h2pi : (0 : ℝ) < 2 * Real.pi := mul_pos zero_lt_two Real.pi_pos
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · rw [Nat.cast_zero, Real.sqrt_zero, mul_zero]
    exact psum_nonneg hnn 0
  · have hn' : (0 : ℝ) < n := by exact_mod_cast hn
    have h1 : ∑ _i ∈ range n, (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi * n)
        ≤ ∑ i ∈ range n, poissonMass (i + 1) :=
      sum_le_sum fun i hi =>
        poissonMass_ge_of_le (Nat.le_add_left 1 i) (Nat.succ_le_of_lt (mem_range.mp hi))
    have h2 : psum poissonMass n = ∑ i ∈ range n, poissonMass (i + 1)
        + poissonMass 0 := sum_range_succ' poissonMass n
    have h3 : ∑ _i ∈ range n, (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi * n)
        = (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi) * Real.sqrt n := by
      rw [sum_const, card_range, nsmul_eq_mul, Real.sqrt_mul h2pi.le (n : ℝ)]
      exact sqrt_alg (Real.sqrt_pos.mpr h2pi).ne' (Real.sqrt_pos.mpr hn').ne'
        (Real.mul_self_sqrt hn'.le)
    linarith [hnn 0]

private theorem tendsto_psum_poissonMass : Tendsto (psum poissonMass) atTop atTop := by
  have h2pi : (0 : ℝ) < 2 * Real.pi := mul_pos zero_lt_two Real.pi_pos
  have hc : (0 : ℝ) < (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi) :=
    div_pos (by norm_num) (Real.sqrt_pos.mpr h2pi)
  have h1 : Tendsto (fun n : ℕ => Real.sqrt (n : ℝ)) atTop atTop :=
    Real.tendsto_sqrt_atTop.comp tendsto_natCast_atTop_atTop
  have h2 : Tendsto (fun n : ℕ => (11 / 12 : ℝ) / Real.sqrt (2 * Real.pi) * Real.sqrt (n : ℝ))
      atTop atTop := h1.const_mul_atTop hc
  exact tendsto_atTop_mono psum_poissonMass_ge h2

/-! ### The three sums -/

/-- The series $\sum_{j \ge 1} e^{-j} a_j$, with the Cayley coefficients $a_j = j^{j-1}/j!$,
converges and has the sum $1$: the Borel law with parameter $1$ is a probability law, or, in
other words, the tree function takes the value $1$ at its singularity $e^{-1}$. -/
theorem hasSum_borel : HasSum (fun j : ℕ => Real.exp (-(j : ℝ)) * cay j) 1 := by
  refine renewal_hasSum_one (g := poissonMass) ?_ (fun n => (poissonMass_pos n).le)
      poissonMass_le_one ?_ poissonMass_zero
    (fun n hn => poissonMass_conv hn) tendsto_psum_poissonMass
  · intro m
    exact mul_nonneg (Real.exp_pos _).le (cay_nonneg m)
  · simp

/-- The series $\sum_{n \ge 0} e^{-n} c_n$, with $c_n = (n+1)^{n-1}/n!$, converges and has the sum
$e$. -/
theorem hasSum_cc : HasSum (fun n : ℕ => Real.exp (-(n : ℝ)) * cc n) (Real.exp 1) := by
  have h1 : HasSum (fun n : ℕ => Real.exp (-((n + 1 : ℕ) : ℝ)) * cay (n + 1)) 1 := by
    refine (hasSum_nat_add_iff (f := fun j : ℕ => Real.exp (-(j : ℝ)) * cay j) 1).mpr ?_
    simpa using hasSum_borel
  have h2 : HasSum (fun n : ℕ => Real.exp 1 * (Real.exp (-((n + 1 : ℕ) : ℝ)) * cay (n + 1)))
      (Real.exp 1 * 1) := h1.mul_left (Real.exp 1)
  rw [mul_one] at h2
  have hfun : (fun n : ℕ => Real.exp (-(n : ℝ)) * cc n)
      = fun n : ℕ => Real.exp 1 * (Real.exp (-((n + 1 : ℕ) : ℝ)) * cay (n + 1)) := by
    funext n
    have e : Real.exp 1 * Real.exp (-((n + 1 : ℕ) : ℝ)) = Real.exp (-(n : ℝ)) := by
      rw [← Real.exp_add]
      congr 1
      push_cast
      ring
    rw [cc, ← mul_assoc, e]
  rw [hfun]
  exact h2

/-- The series $\sum_{m \ge 1} e^{-m} \varepsilon_m$, with $\varepsilon_m = (m-1)^{m-1}/m!$,
converges and has the sum $1 - e^{-1}$. -/
theorem hasSum_eps : HasSum (fun m : ℕ => Real.exp (-(m : ℝ)) * eps m) (1 - Real.exp (-1)) := by
  have key : HasSum (fun m : ℕ => Real.exp (-(m : ℝ)) * eps m) (1 - (Real.exp 1)⁻¹) := by
    refine renewal_hasSum_inv (g := fun n : ℕ => Real.exp (-(n : ℝ)) * cc n)
      ?_ ?_ ?_ ?_ ?_ hasSum_cc
    · intro m
      exact mul_nonneg (Real.exp_pos _).le (eps_nonneg m)
    · intro n
      exact mul_nonneg (Real.exp_pos _).le (cc_pos n).le
    · simp [eps]
    · simp [cc_zero]
    · intro n hn
      have h := exp_conv eps cc n
      rw [eps_conv_range hn] at h
      exact h
  have e : Real.exp (-1) = (Real.exp 1)⁻¹ := Real.exp_neg 1
  rw [e]
  exact key

end Parking
