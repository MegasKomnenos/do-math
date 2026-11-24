module

public import Parking.Cayley.TreeSeries
public import Parking.Counting.LastCar
public import Mathlib.Algebra.BigOperators.Field

/-!
# The weighted last-car recursion and the single-chain formula

`IsWSol ω W` says that `W` solves `W 0 = 1`, `(n+1) W (n+1) = ∑_{j ≤ n} ω (j+1) W j W (n-j)`.
For `ω t = t` the solution is `cc`; for `ω t = min t y` it is `zr y n = A n (y-1)/n!`
(the last-car recursion `A_succ`).

If `ω t = t` for `1 ≤ t ≤ k`, then `W/P ≡ 1 - D (mod x^(2k+2))` with
`D = ∑_{t>k} (c_{t-1} - (ω t/t) W_{t-1}) x^t`.  This is `IsWSol.ez` (coefficients of `W/P`) and
`IsWSol.fwd` (coefficients of `P - W = P D`).  The reason is that `V = W/P` satisfies
`V' = -D' V`, and `D` vanishes to order `k`: the coefficient of `x^i` in `D' V` then only involves
products of two coefficients of `D` of total degree `≤ i`, which vanish for `i ≤ 2k`.

The power-series lemmas live in the namespace `Parking.Counting.SingleChain`.

The last section applies this to the parking functions: `zr y n = A n (y-1)/n!` solves the
recursion with weight `min t y` (`zr_isWSol`), hence equals `cc n` for `n ≤ y` (`zr_eq_cc`, i.e.
`A n k = (n+1)^(n-1)` for `n ≤ k + 1`, `A_eq_pow`); and `bq k n = b n k/n!` is the difference
`zr (k+1) n - zr k n` (`bq_eq`).
-/

@[expose] public section

namespace Parking

open Finset

/-- `W` solves the weighted last-car recursion with weight `ω`. -/
structure IsWSol (ω : ℕ → ℝ) (W : ℕ → ℝ) : Prop where
  zero : W 0 = 1
  succ : ∀ n : ℕ,
    ((n : ℝ) + 1) * W (n + 1) = ∑ j ∈ range (n + 1), ω (j + 1) * W j * W (n - j)

private theorem cc_isWSol : IsWSol (fun t => (t : ℝ)) cc := by
  refine ⟨cc_zero, fun n => ?_⟩
  rw [cc_rec n]
  refine sum_congr rfl fun j _ => ?_
  show ((j : ℝ) + 1) * cc j * cc (n - j) = ((j + 1 : ℕ) : ℝ) * cc j * cc (n - j)
  rw [Nat.cast_add, Nat.cast_one]

/-- Two solutions whose weights agree on `[1, n]` agree up to index `n`. -/
private theorem IsWSol.congr {ω ω' : ℕ → ℝ} {W W' : ℕ → ℝ} (h : IsWSol ω W) (h' : IsWSol ω' W')
    (n : ℕ) (hω : ∀ t, 1 ≤ t → t ≤ n → ω t = ω' t) : ∀ m, m ≤ n → W m = W' m := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro hm
    cases m with
    | zero => rw [h.zero, h'.zero]
    | succ m =>
      have hsum : ∑ j ∈ range (m + 1), ω (j + 1) * W j * W (m - j) =
          ∑ j ∈ range (m + 1), ω' (j + 1) * W' j * W' (m - j) := by
        refine sum_congr rfl fun j hj => ?_
        rw [mem_range] at hj
        rw [hω (j + 1) (by omega) (by omega), ih j (by omega) (by omega),
          ih (m - j) (by omega) (by omega)]
      have hpos : ((m : ℝ) + 1) ≠ 0 := by positivity
      have key : ((m : ℝ) + 1) * W (m + 1) = ((m : ℝ) + 1) * W' (m + 1) := by
        rw [h.succ m, h'.succ m, hsum]
      exact mul_left_cancel₀ hpos key

/-- If `ω t = t` for `1 ≤ t ≤ k` then `W n = cc n` for `n ≤ k`. -/
private theorem IsWSol.eq_cc {ω : ℕ → ℝ} {W : ℕ → ℝ} (h : IsWSol ω W) (k : ℕ)
    (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {n : ℕ} (hn : n ≤ k) : W n = cc n :=
  h.congr cc_isWSol k hω n hn

/-! ### Power-series form of the weighted recursion -/

namespace SingleChain

open TreeSeries

local notation "Dx" => PowerSeries.derivative (R := ℝ)

variable {ω W : ℕ → ℝ} {k : ℕ}

/-- The series `G = ∑_{t ≥ 1} (ω t/t) W_{t-1} x^t`. -/
noncomputable def Gser (ω W : ℕ → ℝ) : PowerSeries ℝ :=
  PowerSeries.mk fun t => if t = 0 then 0 else ω t / (t : ℝ) * W (t - 1)

/-- The series `V = W/P = E W`. -/
private noncomputable def Vser (W : ℕ → ℝ) : PowerSeries ℝ := Eser * PowerSeries.mk W

/-- The weighted recursion in power-series form: `W' = G' W`. -/
theorem deriv_mk (h : IsWSol ω W) :
    Dx (PowerSeries.mk W) = Dx (Gser ω W) * PowerSeries.mk W := by
  refine PowerSeries.ext fun n => ?_
  rw [PowerSeries.coeff_derivative, coeff_mul_range, PowerSeries.coeff_mk,
    mul_comm (W (n + 1)) _, h.succ n]
  refine sum_congr rfl fun j _ => ?_
  have hj : ((j : ℝ) + 1) ≠ 0 := by positivity
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_mk, Gser, PowerSeries.coeff_mk,
    ite_eq_right (show ¬ (j + 1 = 0) by omega), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]
  field

/-- `V' = -(T - G)' V`. -/
private theorem deriv_Vser (h : IsWSol ω W) :
    Dx (Vser W) = -(Dx (Tser - Gser ω W) * Vser W) := by
  have h1 := deriv_mk h
  have h2 := deriv_Eser
  have h3 : Dx (Vser W) = Eser * Dx (PowerSeries.mk W) + PowerSeries.mk W * Dx Eser := by
    rw [Vser, Derivation.leibniz, smul_eq_mul, smul_eq_mul]
  rw [map_sub, h3, h1, h2, Vser]
  ring

/-- Coefficients of `D = T - G`. -/
private theorem coeff_Dser (ω W : ℕ → ℝ) {t : ℕ} (ht : 1 ≤ t) :
    PowerSeries.coeff t (Tser - Gser ω W) = cc (t - 1) - ω t / (t : ℝ) * W (t - 1) := by
  have hcay : cay t = cc (t - 1) := by rw [cc, Nat.sub_add_cancel ht]
  rw [map_sub, coeff_Tser, Gser, PowerSeries.coeff_mk, ite_eq_right (show ¬ t = 0 by omega), hcay]

/-- `D` vanishes to order `k`. -/
private theorem coeff_Dser_eq_zero (h : IsWSol ω W) (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {t : ℕ}
    (ht : t ≤ k) : PowerSeries.coeff t (Tser - Gser ω W) = 0 := by
  by_cases ht0 : t = 0
  · subst ht0
    rw [map_sub, coeff_Tser, Gser, PowerSeries.coeff_mk, ite_eq_left rfl, cay_zero, sub_zero]
  · have ht1 : 1 ≤ t := by omega
    have htne : (t : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr ht0
    rw [coeff_Dser ω W ht1, hω t ht1 ht, h.eq_cc k hω (show t - 1 ≤ k by omega), div_self htne,
      one_mul, sub_self]

private theorem coeff_Vser_zero (h : IsWSol ω W) : PowerSeries.coeff 0 (Vser W) = 1 := by
  have e : PowerSeries.constantCoeff Eser = 1 := by
    rw [← PowerSeries.coeff_zero_eq_constantCoeff_apply, coeff_Eser_zero]
  rw [PowerSeries.coeff_zero_eq_constantCoeff_apply, Vser, map_mul, e,
    PowerSeries.constantCoeff_mk, h.zero, one_mul]

/-- The coefficient recursion for `V` coming from `V' = -D' V`. -/
private theorem coeff_Vser_succ (h : IsWSol ω W) (i : ℕ) :
    PowerSeries.coeff (i + 1) (Vser W) * ((i : ℝ) + 1) =
      -∑ j ∈ range (i + 1), PowerSeries.coeff (j + 1) (Tser - Gser ω W) * ((j : ℝ) + 1) *
        PowerSeries.coeff (i - j) (Vser W) := by
  have h1 := congrArg (PowerSeries.coeff i) (deriv_Vser h)
  rw [PowerSeries.coeff_derivative, map_neg, coeff_mul_range] at h1
  rw [h1]
  congr 1
  refine sum_congr rfl fun j _ => ?_
  rw [PowerSeries.coeff_derivative]

/-- `[x^i] V = 0` for `1 ≤ i ≤ k`. -/
private theorem coeff_Vser_eq_zero (h : IsWSol ω W) (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {i : ℕ}
    (hi1 : 1 ≤ i) (hik : i ≤ k) : PowerSeries.coeff i (Vser W) = 0 := by
  obtain ⟨i', rfl⟩ : ∃ i', i = i' + 1 := ⟨i - 1, by omega⟩
  have hrec := coeff_Vser_succ h i'
  have hz : ∑ j ∈ range (i' + 1), PowerSeries.coeff (j + 1) (Tser - Gser ω W) * ((j : ℝ) + 1) *
      PowerSeries.coeff (i' - j) (Vser W) = 0 := by
    refine sum_eq_zero fun j hj => ?_
    rw [mem_range] at hj
    rw [coeff_Dser_eq_zero h hω (show j + 1 ≤ k by omega), zero_mul, zero_mul]
  rw [hz, neg_zero] at hrec
  have hpos : ((i' : ℝ) + 1) ≠ 0 := by positivity
  exact (mul_eq_zero.mp hrec).resolve_right hpos

/-- `[x^i] V = -[x^i] D` for `1 ≤ i ≤ 2k+1`. -/
private theorem coeff_Vser_eq (h : IsWSol ω W) (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {i : ℕ}
    (hi1 : 1 ≤ i) (hi2 : i ≤ 2 * k + 1) :
    PowerSeries.coeff i (Vser W) = -PowerSeries.coeff i (Tser - Gser ω W) := by
  obtain ⟨i', rfl⟩ : ∃ i', i = i' + 1 := ⟨i - 1, by omega⟩
  have hrec := coeff_Vser_succ h i'
  rw [Finset.sum_range_succ] at hrec
  have hz : ∑ j ∈ range i', PowerSeries.coeff (j + 1) (Tser - Gser ω W) * ((j : ℝ) + 1) *
      PowerSeries.coeff (i' - j) (Vser W) = 0 := by
    refine sum_eq_zero fun j hj => ?_
    rw [mem_range] at hj
    by_cases hjk : j + 1 ≤ k
    · rw [coeff_Dser_eq_zero h hω hjk, zero_mul, zero_mul]
    · rw [coeff_Vser_eq_zero h hω (show 1 ≤ i' - j by omega) (show i' - j ≤ k by omega),
        mul_zero]
  rw [hz, zero_add, Nat.sub_self, coeff_Vser_zero h, mul_one] at hrec
  have hpos : ((i' : ℝ) + 1) ≠ 0 := by positivity
  have h' : PowerSeries.coeff (i' + 1) (Vser W) * ((i' : ℝ) + 1) =
      -PowerSeries.coeff (i' + 1) (Tser - Gser ω W) * ((i' : ℝ) + 1) := by
    rw [hrec]
    ring
  exact mul_right_cancel₀ hpos h'

/-- Coefficients of `V = E W`. -/
private theorem coeff_Vser (W : ℕ → ℝ) (n : ℕ) :
    PowerSeries.coeff n (Vser W) = W n - ∑ m ∈ Icc 1 n, eps m * W (n - m) := by
  rw [Vser, coeff_Eser_mul]
  simp only [PowerSeries.coeff_mk]

/-- `W = V P`. -/
private theorem mk_eq_Vser_mul (W : ℕ → ℝ) : PowerSeries.mk W = Vser W * Pser := by
  have h3 := Eser_mul_Pser
  rw [Vser]
  linear_combination (-(PowerSeries.mk W)) * h3

end SingleChain

/-- **Single-chain formula, `W/P` form.** If `ω t = t` for `1 ≤ t ≤ k`, then for `1 ≤ n ≤ 2k+1`
the `n`-th coefficient of `W/P` is `0` if `n ≤ k` and `(ω n/n) W_{n-1} - c_{n-1}` otherwise. -/
theorem IsWSol.ez {ω : ℕ → ℝ} {W : ℕ → ℝ} (h : IsWSol ω W) (k : ℕ)
    (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {n : ℕ} (hn0 : 1 ≤ n) (hn : n ≤ 2 * k + 1) :
    W n - ∑ m ∈ Icc 1 n, eps m * W (n - m)
      = if n ≤ k then 0 else ω n / n * W (n - 1) - cc (n - 1) := by
  rw [← SingleChain.coeff_Vser W n]
  split_ifs with hnk
  · exact SingleChain.coeff_Vser_eq_zero h hω hn0 hnk
  · rw [SingleChain.coeff_Vser_eq h hω hn0 hn, SingleChain.coeff_Dser ω W hn0]
    ring

/-- **Single-chain formula, forward form.** If `ω t = t` for `1 ≤ t ≤ k`, then for `n ≤ 2k+1`:
`c_n - W_n = ∑_{t=k+1}^n c_{n-t} (c_{t-1} - (ω t/t) W_{t-1})`. -/
theorem IsWSol.fwd {ω : ℕ → ℝ} {W : ℕ → ℝ} (h : IsWSol ω W) (k : ℕ)
    (hω : ∀ t, 1 ≤ t → t ≤ k → ω t = t) {n : ℕ} (hn : n ≤ 2 * k + 1) :
    cc n - W n = ∑ t ∈ Icc (k + 1) n, cc (n - t) * (cc (t - 1) - ω t / t * W (t - 1)) := by
  have hcoef := congrArg (PowerSeries.coeff n) (SingleChain.mk_eq_Vser_mul W)
  rw [PowerSeries.coeff_mk, TreeSeries.coeff_mul_split, SingleChain.coeff_Vser_zero h, one_mul,
    TreeSeries.coeff_Pser] at hcoef
  have hsub : Icc (k + 1) n ⊆ Icc 1 n := by
    intro t ht
    rw [mem_Icc] at ht ⊢
    omega
  have hstep : ∑ t ∈ Icc (k + 1) n, PowerSeries.coeff t (SingleChain.Vser W) *
        PowerSeries.coeff (n - t) TreeSeries.Pser =
      ∑ t ∈ Icc 1 n, PowerSeries.coeff t (SingleChain.Vser W) *
        PowerSeries.coeff (n - t) TreeSeries.Pser := by
    refine Finset.sum_subset hsub fun t ht hnt => ?_
    rw [mem_Icc] at ht hnt
    rw [SingleChain.coeff_Vser_eq_zero h hω ht.1 (show t ≤ k by omega), zero_mul]
  have hsum : ∑ t ∈ Icc (k + 1) n, PowerSeries.coeff t (SingleChain.Vser W) *
        PowerSeries.coeff (n - t) TreeSeries.Pser =
      -∑ t ∈ Icc (k + 1) n, cc (n - t) * (cc (t - 1) - ω t / t * W (t - 1)) := by
    rw [← Finset.sum_neg_distrib]
    refine sum_congr rfl fun t ht => ?_
    rw [mem_Icc] at ht
    rw [SingleChain.coeff_Vser_eq h hω (show 1 ≤ t by omega) (show t ≤ 2 * k + 1 by omega),
      SingleChain.coeff_Dser ω W (show 1 ≤ t by omega), TreeSeries.coeff_Pser]
    ring
  rw [← hstep, hsum] at hcoef
  linarith

/-! ### The parking instance -/

/-- `zr y n = A n (y-1)/n!`: parking functions of length `n` with all displacements `< y`
(`y ≥ 1`), divided by `n!`. -/
noncomputable def zr (y n : ℕ) : ℝ := (A n (y - 1) : ℝ) / (n.factorial : ℝ)

/-- The last-car recursion `A_succ`, divided by `n!`. -/
theorem zr_isWSol {y : ℕ} (hy : 1 ≤ y) : IsWSol (fun t => ((min t y : ℕ) : ℝ)) (zr y) := by
  refine ⟨by simp [zr, A_zero], fun n => ?_⟩
  have hn0 : (n.factorial : ℝ) ≠ 0 := by positivity
  have hn1 : ((n : ℝ) + 1) ≠ 0 := by positivity
  have hA : (A (n + 1) (y - 1) : ℝ) = ∑ j ∈ range (n + 1), ((min (j + 1) y : ℕ) : ℝ) *
      ((n.choose j : ℝ) * ((A j (y - 1) : ℝ) * (A (n - j) (y - 1) : ℝ))) := by
    have h := A_succ n (y - 1)
    rw [Nat.sub_add_cancel hy] at h
    exact_mod_cast h
  have lhs : ((n : ℝ) + 1) * zr y (n + 1) = (A (n + 1) (y - 1) : ℝ) / (n.factorial : ℝ) := by
    rw [zr, Nat.factorial_succ]
    push_cast
    field
  rw [lhs, hA, Finset.sum_div]
  refine sum_congr rfl fun j hj => ?_
  have hc : (n.choose j : ℝ) * (j.factorial : ℝ) * ((n - j).factorial : ℝ) =
      (n.factorial : ℝ) := by
    exact_mod_cast Nat.choose_mul_factorial_mul_factorial (Nat.lt_succ_iff.mp (mem_range.mp hj))
  have hj0 : (j.factorial : ℝ) ≠ 0 := by positivity
  have hnj0 : ((n - j).factorial : ℝ) ≠ 0 := by positivity
  simp only [zr]
  rw [div_eq_iff hn0, ← hc]
  field

/-- The normalised cumulative counts are nonnegative: $z^{(y)}_n=A(n,y-1)/n!\ge0$. -/
theorem zr_nonneg (y n : ℕ) : 0 ≤ zr y n := by
  unfold zr
  exact div_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _)

/-- The environment increases with the threshold. -/
theorem zr_mono {y y' : ℕ} (h : y ≤ y') (n : ℕ) : zr y n ≤ zr y' n := by
  unfold zr
  have hA : (A n (y - 1) : ℝ) ≤ (A n (y' - 1) : ℝ) := by
    exact_mod_cast A_mono n (Nat.sub_le_sub_right h 1)
  exact div_le_div_of_nonneg_right hA (Nat.cast_nonneg _)

/-- In the free range `n ≤ y` the displacement bound is no restriction. -/
theorem zr_eq_cc {y n : ℕ} (hy : 1 ≤ y) (hn : n ≤ y) : zr y n = cc n :=
  (zr_isWSol hy).eq_cc y (fun t _ ht => by simp [min_eq_left ht]) hn

/-- `bq k n = b n k / n!`. -/
noncomputable def bq (k n : ℕ) : ℝ := (b n k : ℝ) / (n.factorial : ℝ)

/-- The normalised counts are nonnegative: $\beta^{(k)}_n=b(n,k)/n!\ge0$. -/
theorem bq_nonneg (k n : ℕ) : 0 ≤ bq k n := by
  unfold bq
  exact div_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _)

/-- For $k\ge1$ the normalised count of the column $k$ is the difference of the environments of the
thresholds $k+1$ and $k$: $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$. -/
theorem bq_eq {k : ℕ} (hk : 1 ≤ k) (n : ℕ) : bq k n = zr (k + 1) n - zr k n := by
  have h := b_succ_add_A n (k - 1)
  rw [Nat.sub_add_cancel hk] at h
  have h' : (b n k : ℝ) + (A n (k - 1) : ℝ) = (A n k : ℝ) := by exact_mod_cast h
  show (b n k : ℝ) / (n.factorial : ℝ) =
    (A n (k + 1 - 1) : ℝ) / (n.factorial : ℝ) - (A n (k - 1) : ℝ) / (n.factorial : ℝ)
  rw [Nat.add_sub_cancel, ← h']
  ring

/-- For $k\ge1$ and $n\le k$ there is no parking function of length $n$ with maximum displacement
exactly $k$: $\beta^{(k)}_n=b(n,k)/n!=0$. -/
theorem bq_eq_zero {k n : ℕ} (hk : 1 ≤ k) (hn : n ≤ k) : bq k n = 0 := by
  rw [bq_eq hk, zr_eq_cc (show 1 ≤ k + 1 by omega) (show n ≤ k + 1 by omega), zr_eq_cc hk hn,
    sub_self]

/-- `A n k = (n+1)^(n-1)` as soon as `n ≤ k + 1`: then the bound `M(α) ≤ k` is no restriction,
and `A n k` is the number of all parking functions of length `n`. -/
theorem A_eq_pow {n k : ℕ} (h : n ≤ k + 1) : A n k = (n + 1) ^ (n - 1) := by
  have hz : zr (k + 1) n = cc n := zr_eq_cc (Nat.succ_pos k) h
  have hF : (n.factorial : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero n)
  have hn1 : ((n : ℝ) + 1) ≠ 0 := by positivity
  have hfac : ((n + 1).factorial : ℝ) = (n.factorial : ℝ) * ((n : ℝ) + 1) := by
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, mul_comm]
  have hpow : ((n : ℝ) + 1) ^ n = ((n : ℝ) + 1) ^ (n - 1) * ((n : ℝ) + 1) := by
    rcases Nat.eq_zero_or_pos n with rfl | hn
    · simp
    · rw [← pow_succ, Nat.sub_add_cancel hn]
  have h1 : (A n k : ℝ) / (n.factorial : ℝ) = ((n : ℝ) + 1) ^ (n - 1) / (n.factorial : ℝ) := by
    rw [show (A n k : ℝ) / (n.factorial : ℝ) = zr (k + 1) n from rfl, hz, cc_eq, hfac, hpow,
      mul_div_mul_right _ _ hn1]
  exact_mod_cast (div_left_inj' hF).mp h1

end Parking
