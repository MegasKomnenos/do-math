import Parking.Basic.RealBounds
import Parking.Cayley.BorelSum
import Parking.ChainColumn.EpsKernel

/-!
# The resolvent kernel of the frozen feedback

The frozen kernel is `f_1 = (3/2) e^{-1}`, `f_i = e^{-i} ε_i` (`i ≥ 2`): the prime kernel in the
Borel scale, with `e^{-1}/2` added at `i = 1`.  Its renewal sequence is `G_s = e^{-s} H_s`, where

  `H_s = ∑_{j ≤ s} (1/2)^j [x^s] x^j P(x)^{j+1}`,   `P = ∑ c_n x^n`.

* `abel2`            : the convolution form of Abel's identity;
* `coeff_Pser_pow`   : `[x^n] P^{a+1} = (a+1)(a+1+n)^{n-1}/n!`;
* `Hres_renew`       : `H_s = ∑_{m=1}^{s} ε_m H_{s-m} + (1/2) H_{s-1}`;
* `fker_logconvex`   : the frozen kernel is log-convex;
* `Gres_isRenewal`   : `G` is the renewal sequence of `fker`;
* `Gres_sum_le`      : `∑_{s < N} G_s ≤ 2e`;
* `Hres_half_lower`  : `H_s ≥ c_s (4 - 21/(s+1))` for `s ≥ 6`;
* `Gres_lower`       : the resulting explicit lower bound of `G_s`.
-/

namespace Parking

open Finset TreeSeries

local notation "Xs" => (PowerSeries.X : PowerSeries ℝ)

/-! ### Abel's identity in convolution form -/

private theorem abelW_zero (x : ℝ) : abelW x 0 = 1 := by
  unfold abelW
  rw [ite_eq_left rfl]

private theorem abelW_succ (x : ℝ) (k : ℕ) : abelW x (k + 1) = x * (x + ((k : ℝ) + 1)) ^ k := by
  unfold abelW
  rw [ite_eq_right (by omega : ¬ k + 1 = 0), Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]

/-- `∑_k C(m+1,k) w_k(x) w_{m+1-k}(y) = (x+y)(x+y+m+1)^m`. -/
private theorem abel2 (m : ℕ) (x y : ℝ) :
    ∑ k ∈ range (m + 1 + 1), ((m + 1).choose k : ℝ) * abelW x k * abelW y (m + 1 - k)
      = (x + y) * (x + y + ((m : ℝ) + 1)) ^ m := by
  have I1 : ∑ k ∈ range (m + 1 + 1), ((m + 1).choose k : ℝ) * abelW x k
      * (y + ((m : ℝ) + 1) - k) ^ (m + 1 - k) = (x + (y + ((m : ℝ) + 1))) ^ (m + 1) :=
    abel_identity (m + 1) x (y + ((m : ℝ) + 1))
  have I2 : ∑ k ∈ range (m + 1), (m.choose k : ℝ) * abelW x k
      * (y + ((m : ℝ) + 1) - k) ^ (m - k) = (x + (y + ((m : ℝ) + 1))) ^ m :=
    abel_identity m x (y + ((m : ℝ) + 1))
  obtain ⟨S, hS⟩ : ∃ S : ℝ, S = ∑ k ∈ range (m + 1), ((m + 1).choose k : ℝ) * abelW x k
      * (y + ((m : ℝ) + 1) - k) ^ (m - k) := ⟨_, rfl⟩
  have hterm : ∀ k ∈ range (m + 1), ((m + 1).choose k : ℝ) * abelW x k
        * (y + ((m : ℝ) + 1) - k) ^ (m + 1 - k)
      = y * (((m + 1).choose k : ℝ) * abelW x k * (y + ((m : ℝ) + 1) - k) ^ (m - k))
        + ((m : ℝ) + 1) * ((m.choose k : ℝ) * abelW x k * (y + ((m : ℝ) + 1) - k) ^ (m - k)) := by
    intro k hk
    rw [mem_range] at hk
    have e : m + 1 - k = (m - k) + 1 := by omega
    have hc : ((m + 1).choose k : ℝ) * ((m : ℝ) + 1 - k) = (m.choose k : ℝ) * ((m : ℝ) + 1) := by
      have h := Nat.choose_mul_succ_eq m k
      have h' : ((m.choose k * (m + 1) : ℕ) : ℝ) = (((m + 1).choose k * (m + 1 - k) : ℕ) : ℝ) := by
        rw [h]
      rw [Nat.cast_mul, Nat.cast_mul, Nat.cast_sub (by omega : k ≤ m + 1)] at h'
      push_cast at h'
      linarith
    rw [e, pow_succ]
    linear_combination (abelW x k * (y + ((m : ℝ) + 1) - k) ^ (m - k)) * hc
  have hI1 : y * S + ((m : ℝ) + 1) * (x + (y + ((m : ℝ) + 1))) ^ m + abelW x (m + 1)
      = (x + (y + ((m : ℝ) + 1))) ^ (m + 1) := by
    rw [sum_range_succ, sum_congr rfl hterm, sum_add_distrib, ← mul_sum, ← mul_sum, I2, ← hS,
      Nat.choose_self, Nat.sub_self, pow_zero, Nat.cast_one, one_mul, mul_one] at I1
    exact I1
  have hterm2 : ∀ k ∈ range (m + 1), ((m + 1).choose k : ℝ) * abelW x k * abelW y (m + 1 - k)
      = y * (((m + 1).choose k : ℝ) * abelW x k * (y + ((m : ℝ) + 1) - k) ^ (m - k)) := by
    intro k hk
    rw [mem_range] at hk
    have e : m + 1 - k = (m - k) + 1 := by omega
    have e2 : y + (((m - k : ℕ) : ℝ) + 1) = y + ((m : ℝ) + 1) - k := by
      rw [Nat.cast_sub (by omega : k ≤ m)]
      ring
    rw [e, abelW_succ, e2]
    ring
  rw [sum_range_succ, sum_congr rfl hterm2, ← mul_sum, ← hS, Nat.choose_self, Nat.sub_self,
    abelW_zero, Nat.cast_one, one_mul, mul_one]
  linear_combination hI1

/-- `[x^n] P^{a+1} = w_n(a+1)/n!`. -/
private theorem coeff_Pser_pow (a n : ℕ) :
    PowerSeries.coeff n (Pser ^ (a + 1)) = abelW ((a : ℝ) + 1) n / (n.factorial : ℝ) := by
  induction a generalizing n with
  | zero =>
    rw [Nat.zero_add, pow_one, coeff_Pser, Nat.cast_zero, zero_add, ← cc_eq_abelW]
  | succ a ih =>
    rw [pow_succ, coeff_mul_range]
    have hterm : ∀ j ∈ range (n + 1),
        PowerSeries.coeff j (Pser ^ (a + 1)) * PowerSeries.coeff (n - j) Pser
        = ((n.choose j : ℝ) * abelW ((a : ℝ) + 1) j * abelW 1 (n - j)) * (n.factorial : ℝ)⁻¹ := by
      intro j hj
      rw [mem_range] at hj
      have hjn : j ≤ n := by omega
      have h1 : (j.factorial : ℝ) ≠ 0 := by positivity
      have h2 : ((n - j).factorial : ℝ) ≠ 0 := by positivity
      have h3 : (n.factorial : ℝ) ≠ 0 := by positivity
      have hch : (n.choose j : ℝ) * (j.factorial : ℝ) * ((n - j).factorial : ℝ)
          = (n.factorial : ℝ) := by
        exact_mod_cast Nat.choose_mul_factorial_mul_factorial hjn
      have hC : (n.choose j : ℝ)
          = (n.factorial : ℝ) / ((j.factorial : ℝ) * ((n - j).factorial : ℝ)) := by
        rw [eq_div_iff (mul_ne_zero h1 h2)]
        linear_combination hch
      rw [ih j, coeff_Pser, cc_eq_abelW (n - j), hC]
      field
    rw [sum_congr rfl hterm, ← sum_mul]
    rcases n with _ | m
    · simp [abelW_zero]
    · rw [abel2 m ((a : ℝ) + 1) 1, abelW_succ]
      push_cast
      ring

/-! ### The coefficients `[x^s] x^j P^{j+1}` -/

/-- `hcoef j s = [x^s] x^j P^{j+1}`. -/
noncomputable def hcoef (j s : ℕ) : ℝ := PowerSeries.coeff s (Xs ^ j * Pser ^ (j + 1))

private theorem hcoef_eq {j s : ℕ} (h : j ≤ s) :
    hcoef j s = abelW ((j : ℝ) + 1) (s - j) / ((s - j).factorial : ℝ) := by
  unfold hcoef
  rw [PowerSeries.coeff_X_pow_mul', ite_eq_left h, coeff_Pser_pow]

private theorem hcoef_eq_zero {j s : ℕ} (h : s < j) : hcoef j s = 0 := by
  unfold hcoef
  rw [PowerSeries.coeff_X_pow_mul', ite_eq_right (by omega)]

private theorem hcoef_zero (s : ℕ) : hcoef 0 s = cc s := by
  rw [hcoef_eq (Nat.zero_le s), Nat.sub_zero, Nat.cast_zero, zero_add, ← cc_eq_abelW]

/-- The renewal identity of a single coefficient family. -/
private theorem hcoef_renew (j s : ℕ) (hs : 1 ≤ s) :
    hcoef j s - ∑ m ∈ Icc 1 s, eps m * hcoef j (s - m)
      = if j = 0 then 0 else hcoef (j - 1) (s - 1) := by
  have h := coeff_Eser_mul (Xs ^ j * Pser ^ (j + 1)) s
  have e : Eser * (Xs ^ j * Pser ^ (j + 1)) = Xs ^ j * Pser ^ j := by
    rw [pow_succ]
    calc Eser * (Xs ^ j * (Pser ^ j * Pser)) = Xs ^ j * Pser ^ j * (Eser * Pser) := by ring
      _ = Xs ^ j * Pser ^ j := by rw [Eser_mul_Pser, mul_one]
  rw [e] at h
  unfold hcoef
  rw [← h]
  rcases j with _ | i
  · rw [ite_eq_left rfl, pow_zero, pow_zero, one_mul, PowerSeries.coeff_one,
      ite_eq_right (by omega)]
  · obtain ⟨t, rfl⟩ : ∃ t, s = t + 1 := ⟨s - 1, by omega⟩
    rw [ite_eq_right (by omega), Nat.add_sub_cancel, Nat.add_sub_cancel]
    have e2 : Xs ^ (i + 1) * Pser ^ (i + 1) = Xs * (Xs ^ i * Pser ^ (i + 1)) := by ring
    rw [e2, PowerSeries.coeff_succ_X_mul]

/-- The step of the coefficients in `j`:
`hcoef (j+1) s · (j+1)(s+1) = hcoef j s · (j+2)(s-j)`. -/
private theorem hcoef_step {j s : ℕ} (h : j + 1 ≤ s) :
    hcoef (j + 1) s * (((j : ℝ) + 1) * ((s : ℝ) + 1))
      = hcoef j s * (((j : ℝ) + 2) * ((s : ℝ) - j)) := by
  obtain ⟨d, rfl⟩ : ∃ d, s = j + 1 + d := ⟨s - (j + 1), by omega⟩
  have e1 : j + 1 + d - (j + 1) = d := by omega
  have e2 : j + 1 + d - j = d + 1 := by omega
  rw [hcoef_eq h, hcoef_eq (by omega : j ≤ j + 1 + d), e1, e2, abelW_succ]
  rcases d with _ | e
  · have hf0 : ((0 : ℕ).factorial : ℝ) = 1 := by norm_num [Nat.factorial]
    have hf1 : ((0 + 1 : ℕ).factorial : ℝ) = 1 := by norm_num [Nat.factorial]
    rw [abelW_zero, hf0, hf1, pow_zero]
    push_cast
    ring
  · have h1 : ((e + 1).factorial : ℝ) ≠ 0 := by positivity
    have h2 : ((e : ℝ) + 1 + 1) ≠ 0 := by positivity
    rw [abelW_succ, Nat.factorial_succ (e + 1)]
    push_cast
    rw [pow_succ]
    field

/-- Lower bound of the coefficients against the main one. -/
private theorem hcoef_lower (s : ℕ) : ∀ j, j ≤ s →
    cc s * (((j : ℝ) + 1) * (1 - (j : ℝ) * ((j : ℝ) + 1) / (2 * ((s : ℝ) + 1)))) ≤ hcoef j s := by
  intro j
  induction j with
  | zero =>
    intro _
    rw [hcoef_zero, Nat.cast_zero]
    exact le_of_eq (by ring)
  | succ j ih =>
    intro hj
    have ih' := ih (by omega)
    have hstep := hcoef_step hj
    have hS : (0 : ℝ) < (s : ℝ) + 1 := by positivity
    have hS0 : ((s : ℝ) + 1) ≠ 0 := hS.ne'
    have hJ : (0 : ℝ) ≤ (j : ℝ) := Nat.cast_nonneg j
    have hsj : (0 : ℝ) ≤ (s : ℝ) - j := by
      have h1 : ((j + 1 : ℕ) : ℝ) ≤ (s : ℝ) := by exact_mod_cast hj
      push_cast at h1
      linarith
    have hcc : 0 < cc s := cc_pos s
    have hpos : (0 : ℝ) < ((j : ℝ) + 1) * ((s : ℝ) + 1) := by positivity
    have h1 := mul_le_mul_of_nonneg_right ih'
      (mul_nonneg (by positivity : (0 : ℝ) ≤ (j : ℝ) + 2) hsj)
    have key : cc s * (((j : ℝ) + 1 + 1) * (1 - ((j : ℝ) + 1) * ((j : ℝ) + 1 + 1)
          / (2 * ((s : ℝ) + 1)))) * (((j : ℝ) + 1) * ((s : ℝ) + 1))
        = cc s * (((j : ℝ) + 1) * (1 - (j : ℝ) * ((j : ℝ) + 1) / (2 * ((s : ℝ) + 1))))
            * (((j : ℝ) + 2) * ((s : ℝ) - j))
          - cc s * ((j : ℝ) + 1) * ((j : ℝ) + 2)
            * ((j : ℝ) * ((j : ℝ) + 1) ^ 2 / (2 * ((s : ℝ) + 1))) := by
      field
    have hnn : 0 ≤ cc s * ((j : ℝ) + 1) * ((j : ℝ) + 2)
        * ((j : ℝ) * ((j : ℝ) + 1) ^ 2 / (2 * ((s : ℝ) + 1))) := by positivity
    rw [Nat.cast_add, Nat.cast_one]
    refine le_of_mul_le_mul_right ?_ hpos
    rw [hstep, key]
    linarith

/-! ### The resolvent kernel -/

/-- `H_s = ∑_{j ≤ s} (1/2)^j [x^s] x^j P^{j+1}`. -/
noncomputable def Hres (s : ℕ) : ℝ := ∑ j ∈ range (s + 1), (1 / 2 : ℝ) ^ j * hcoef j s

private theorem Hres_eq_range {s N : ℕ} (h : s + 1 ≤ N) :
    Hres s = ∑ j ∈ range N, (1 / 2 : ℝ) ^ j * hcoef j s := by
  unfold Hres
  refine Finset.sum_subset (Finset.range_subset_range.2 h) ?_
  intro j _ hj
  rw [mem_range, not_lt] at hj
  rw [hcoef_eq_zero (by omega), mul_zero]

private theorem Hres_zero : Hres 0 = 1 := by
  unfold Hres
  rw [Nat.zero_add, Finset.sum_range_one, pow_zero, one_mul, hcoef_zero, cc_zero]

/-- The renewal identity: `H_s = ∑_{m=1}^{s} ε_m H_{s-m} + (1/2) H_{s-1}` for `s ≥ 1`. -/
private theorem Hres_renew {s : ℕ} (hs : 1 ≤ s) :
    Hres s = ∑ m ∈ Icc 1 s, eps m * Hres (s - m) + 1 / 2 * Hres (s - 1) := by
  obtain ⟨t, rfl⟩ : ∃ t, s = t + 1 := ⟨s - 1, by omega⟩
  rw [Nat.add_sub_cancel]
  have h1 : ∑ m ∈ Icc 1 (t + 1), eps m * Hres (t + 1 - m)
      = ∑ j ∈ range (t + 1 + 1), (1 / 2 : ℝ) ^ j * ∑ m ∈ Icc 1 (t + 1),
          eps m * hcoef j (t + 1 - m) := by
    have h : ∀ m ∈ Icc 1 (t + 1), eps m * Hres (t + 1 - m)
        = ∑ j ∈ range (t + 1 + 1), (1 / 2 : ℝ) ^ j * (eps m * hcoef j (t + 1 - m)) := by
      intro m hm
      rw [mem_Icc] at hm
      rw [Hres_eq_range (by omega : t + 1 - m + 1 ≤ t + 1 + 1), mul_sum]
      refine sum_congr rfl (fun j _ => ?_)
      ring
    rw [sum_congr rfl h, sum_comm]
    refine sum_congr rfl (fun j _ => ?_)
    rw [mul_sum]
  have h2 : Hres (t + 1) - ∑ m ∈ Icc 1 (t + 1), eps m * Hres (t + 1 - m)
      = ∑ j ∈ range (t + 1 + 1), (1 / 2 : ℝ) ^ j * (if j = 0 then 0 else hcoef (j - 1) t) := by
    rw [h1]
    unfold Hres
    rw [← sum_sub_distrib]
    refine sum_congr rfl (fun j _ => ?_)
    have h := hcoef_renew j (t + 1) (by omega)
    rw [Nat.add_sub_cancel] at h
    rw [← h]
    ring
  have h3 : ∑ j ∈ range (t + 1 + 1), (1 / 2 : ℝ) ^ j * (if j = 0 then 0 else hcoef (j - 1) t)
      = 1 / 2 * Hres t := by
    rw [sum_range_succ', ite_eq_left rfl, mul_zero, add_zero]
    unfold Hres
    rw [mul_sum]
    refine sum_congr rfl (fun j _ => ?_)
    rw [ite_eq_right (by omega), Nat.add_sub_cancel, pow_succ]
    ring
  linarith [h2, h3]

/-- The frozen kernel: `f_1 = (3/2) e^{-1}`, `f_i = e^{-i} ε_i` (`i ≥ 2`). -/
noncomputable def fker (i : ℕ) : ℝ :=
  Real.exp (-(i : ℝ)) * eps i + if i = 1 then Real.exp (-1) / 2 else 0

/-- The resolvent kernel `G_s = e^{-s} H_s`. -/
noncomputable def Gres (s : ℕ) : ℝ := Real.exp (-(s : ℝ)) * Hres s

/-- For $i \ge 2$ the frozen kernel is the prime kernel in the Borel scale: $f_i =
e^{-i}\varepsilon_i$. -/
theorem fker_of_two_le {i : ℕ} (hi : 2 ≤ i) : fker i = Real.exp (-1) ^ i * eps i := by
  unfold fker
  rw [ite_eq_right (by omega), add_zero, exp_neg_nat]

/-- The frozen kernel is positive: $f_i > 0$ for every $i \ge 1$. -/
theorem fker_pos {i : ℕ} (hi : 1 ≤ i) : 0 < fker i := by
  unfold fker
  have h1 : 0 < Real.exp (-(i : ℝ)) * eps i := mul_pos (Real.exp_pos _) (eps_pos hi)
  have h2 : (0 : ℝ) ≤ if i = 1 then Real.exp (-1) / 2 else 0 := by
    split_ifs
    · positivity
    · exact le_refl 0
  linarith

/-- The frozen kernel dominates the prime kernel in the Borel scale. -/
private theorem fker_ge (i : ℕ) : Real.exp (-1) ^ i * eps i ≤ fker i := by
  unfold fker
  rw [exp_neg_nat]
  split_ifs
  · linarith [Real.exp_pos (-1)]
  · linarith

/-- Log-convexity of the frozen kernel: `f_{j+2}² ≤ f_{j+1} f_{j+3}`.  The kernel
`e^{-i} ε_i` is log-convex, and the frozen kernel differs from it only by being larger at
`i = 1`. -/
theorem fker_logconvex (j : ℕ) : fker (j + 2) ^ 2 ≤ fker (j + 1) * fker (j + 3) := by
  have hE : 0 < Real.exp (-1) := Real.exp_pos _
  rw [fker_of_two_le (by omega : 2 ≤ j + 2), fker_of_two_le (by omega : 2 ≤ j + 3)]
  calc (Real.exp (-1) ^ (j + 2) * eps (j + 2)) ^ 2
      = Real.exp (-1) ^ (j + 1) * Real.exp (-1) ^ (j + 3) * eps (j + 2) ^ 2 := by ring
    _ ≤ Real.exp (-1) ^ (j + 1) * Real.exp (-1) ^ (j + 3) * (eps (j + 1) * eps (j + 3)) :=
        mul_le_mul_of_nonneg_left (eps_logconvex j) (by positivity)
    _ = Real.exp (-1) ^ (j + 1) * eps (j + 1) * (Real.exp (-1) ^ (j + 3) * eps (j + 3)) := by
        ring
    _ ≤ fker (j + 1) * (Real.exp (-1) ^ (j + 3) * eps (j + 3)) :=
        mul_le_mul_of_nonneg_right (fker_ge (j + 1))
          (mul_nonneg (pow_pos hE _).le (eps_nonneg _))

/-- `G` is the renewal sequence of the frozen kernel. -/
theorem Gres_isRenewal : IsRenewal fker Gres := by
  refine And.intro ?_ ?_
  · unfold Gres
    rw [Hres_zero, Nat.cast_zero, neg_zero, Real.exp_zero, mul_one]
  · intro n hn
    have h := Hres_renew hn
    have hsplit : ∀ i ∈ Icc 1 n, fker i * Gres (n - i)
        = Real.exp (-(n : ℝ)) * (eps i * Hres (n - i))
          + (if i = 1 then Real.exp (-1) / 2 else 0) * Gres (n - i) := by
      intro i hi
      rw [mem_Icc] at hi
      have he : Real.exp (-(i : ℝ)) * Real.exp (-((n - i : ℕ) : ℝ)) = Real.exp (-(n : ℝ)) := by
        rw [← Real.exp_add, Nat.cast_sub hi.2]
        congr 1
        ring
      unfold fker Gres
      linear_combination (eps i * Hres (n - i)) * he
    have hone : ∑ i ∈ Icc 1 n, (if i = 1 then Real.exp (-1) / 2 else 0) * Gres (n - i)
        = Real.exp (-1) / 2 * Gres (n - 1) := by
      rw [Finset.sum_eq_single_of_mem 1 (mem_Icc.mpr ⟨le_refl 1, hn⟩)
        (fun b _ hb => by rw [ite_eq_right hb, zero_mul]), ite_eq_left rfl]
    have he1 : Real.exp (-1) * Real.exp (-((n - 1 : ℕ) : ℝ)) = Real.exp (-(n : ℝ)) := by
      rw [← Real.exp_add, Nat.cast_sub hn]
      congr 1
      push_cast
      ring
    rw [sum_congr rfl hsplit, sum_add_distrib, ← mul_sum, hone]
    unfold Gres
    rw [h]
    linear_combination (-(1 / 2) * Hres (n - 1)) * he1

/-- The resolvent sequence of the frozen kernel is positive: $G_s > 0$ for every $s \ge 0$. -/
theorem Gres_pos (s : ℕ) : 0 < Gres s :=
  renewal_pos (fun _ hi => fker_pos hi) Gres_isRenewal s

/-! ### The total mass of the resolvent kernel -/

private theorem fker_sum_le (N : ℕ) : ∑ i ∈ Icc 1 N, fker i ≤ 1 - Real.exp (-1) / 2 := by
  have h1 : ∑ i ∈ Icc 1 N, Real.exp (-(i : ℝ)) * eps i ≤ 1 - Real.exp (-1) :=
    sum_le_hasSum (Icc 1 N)
      (fun i _ => mul_nonneg (Real.exp_pos _).le (eps_nonneg i)) hasSum_eps
  have h2 : ∑ i ∈ Icc 1 N, (if i = 1 then Real.exp (-1) / 2 else 0) ≤ Real.exp (-1) / 2 := by
    rw [Finset.sum_ite_eq']
    split_ifs
    · exact le_refl _
    · positivity
  unfold fker
  rw [sum_add_distrib]
  linarith

/-- `∑_{s < N} G_s ≤ 2e`: the constant sequence `1` has innovations `1 - ∑_{i ≤ s} f_i ≥ e^{-1}/2`
with respect to the frozen kernel, and is the convolution of `G` with them. -/
theorem Gres_sum_le (N : ℕ) : ∑ s ∈ range N, Gres s ≤ 2 * Real.exp 1 := by
  rcases N with _ | N
  · rw [range_zero, sum_empty]
    positivity
  have hres : (1 : ℝ) = ∑ c ∈ range (N + 1), Gres (N - c) * (1 - ∑ i ∈ Icc 1 c, fker i) :=
    resolvent (v := fun _ => 1) Gres_isRenewal (fun s => by simp) N
  have h1 : ∑ c ∈ range (N + 1), Gres (N - c) * (Real.exp (-1) / 2) ≤ 1 :=
    calc ∑ c ∈ range (N + 1), Gres (N - c) * (Real.exp (-1) / 2)
        ≤ ∑ c ∈ range (N + 1), Gres (N - c) * (1 - ∑ i ∈ Icc 1 c, fker i) :=
          sum_le_sum fun c _ =>
            mul_le_mul_of_nonneg_left (by linarith [fker_sum_le c]) (Gres_pos _).le
      _ = 1 := hres.symm
  rw [← sum_mul, sum_flip] at h1
  have he : Real.exp (-1) * Real.exp 1 = 1 := by
    rw [← Real.exp_add]
    norm_num
  have h2 := mul_le_mul_of_nonneg_right h1 (by positivity : (0 : ℝ) ≤ 2 * Real.exp 1)
  have h3 : (∑ s ∈ range (N + 1), Gres s) * (Real.exp (-1) / 2) * (2 * Real.exp 1)
      = (∑ s ∈ range (N + 1), Gres s) * (Real.exp (-1) * Real.exp 1) := by ring
  rw [h3, he, mul_one] at h2
  linarith

/-! ### The lower bound of `H` -/

private theorem sumA (s : ℕ) :
    ∑ j ∈ range (s + 1), (1 / 2 : ℝ) ^ j * ((j : ℝ) + 1) = 4 - ((s : ℝ) + 3) * (1 / 2) ^ s := by
  induction s with
  | zero => norm_num
  | succ s ih =>
    rw [sum_range_succ, ih, pow_succ]
    push_cast
    ring

private theorem sumB (s : ℕ) :
    ∑ j ∈ range (s + 1), (1 / 2 : ℝ) ^ j * ((j : ℝ) * ((j : ℝ) + 1) ^ 2)
      = 40 - ((s : ℝ) ^ 3 + 8 * (s : ℝ) ^ 2 + 27 * (s : ℝ) + 40) * (1 / 2) ^ s := by
  induction s with
  | zero => norm_num
  | succ s ih =>
    rw [sum_range_succ, ih, pow_succ]
    push_cast
    ring

private theorem half_pow_bound {s : ℕ} (hs : 6 ≤ s) :
    ((s : ℝ) + 3) * ((s : ℝ) + 1) * (1 / 2) ^ s ≤ 1 := by
  induction s, hs using Nat.le_induction with
  | base => norm_num
  | succ s hs ih =>
    have h6 : (6 : ℝ) ≤ (s : ℝ) := by exact_mod_cast hs
    have hp : (0 : ℝ) ≤ (1 / 2 : ℝ) ^ s := by positivity
    have hq : (0 : ℝ) ≤ (s : ℝ) ^ 2 + 2 * (s : ℝ) - 2 := by nlinarith
    have hpq := mul_nonneg hp hq
    rw [pow_succ]
    push_cast
    nlinarith

/-- `H_s ≥ c_s (4 - 21/(s+1))` for `s ≥ 6`. -/
private theorem Hres_half_lower {s : ℕ} (hs : 6 ≤ s) :
    cc s * (4 - 21 / ((s : ℝ) + 1)) ≤ Hres s := by
  have hS : (0 : ℝ) < (s : ℝ) + 1 := by positivity
  have hS0 : ((s : ℝ) + 1) ≠ 0 := hS.ne'
  have hterm : ∀ j ∈ range (s + 1),
      cc s * ((1 / 2 : ℝ) ^ j * ((j : ℝ) + 1))
        - cc s / (2 * ((s : ℝ) + 1)) * ((1 / 2 : ℝ) ^ j * ((j : ℝ) * ((j : ℝ) + 1) ^ 2))
      ≤ (1 / 2 : ℝ) ^ j * hcoef j s := by
    intro j hj
    rw [mem_range] at hj
    have h := hcoef_lower s j (by omega)
    have hp : (0 : ℝ) ≤ (1 / 2 : ℝ) ^ j := by positivity
    have h2 := mul_le_mul_of_nonneg_left h hp
    have e : (1 / 2 : ℝ) ^ j * (cc s * (((j : ℝ) + 1)
          * (1 - (j : ℝ) * ((j : ℝ) + 1) / (2 * ((s : ℝ) + 1)))))
        = cc s * ((1 / 2 : ℝ) ^ j * ((j : ℝ) + 1))
          - cc s / (2 * ((s : ℝ) + 1)) * ((1 / 2 : ℝ) ^ j * ((j : ℝ) * ((j : ℝ) + 1) ^ 2)) := by
      field
    rw [e] at h2
    exact h2
  have hsum := Finset.sum_le_sum hterm
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, sumA, sumB] at hsum
  have hpw := half_pow_bound hs
  have hh : (0 : ℝ) ≤ (1 / 2 : ℝ) ^ s := by positivity
  have hcc : 0 < cc s := cc_pos s
  have key : cc s * (4 - ((s : ℝ) + 3) * (1 / 2) ^ s)
        - cc s / (2 * ((s : ℝ) + 1))
          * (40 - ((s : ℝ) ^ 3 + 8 * (s : ℝ) ^ 2 + 27 * (s : ℝ) + 40) * (1 / 2) ^ s)
        - cc s * (4 - 21 / ((s : ℝ) + 1))
      = cc s / ((s : ℝ) + 1) * ((1 - ((s : ℝ) + 3) * ((s : ℝ) + 1) * (1 / 2) ^ s)
          + ((s : ℝ) ^ 3 + 8 * (s : ℝ) ^ 2 + 27 * (s : ℝ) + 40) * (1 / 2) ^ s / 2) := by
    field
  have hnn : 0 ≤ cc s / ((s : ℝ) + 1) * ((1 - ((s : ℝ) + 3) * ((s : ℝ) + 1) * (1 / 2) ^ s)
      + ((s : ℝ) ^ 3 + 8 * (s : ℝ) ^ 2 + 27 * (s : ℝ) + 40) * (1 / 2) ^ s / 2) := by
    have h5 : (0 : ℝ) ≤ ((s : ℝ) ^ 3 + 8 * (s : ℝ) ^ 2 + 27 * (s : ℝ) + 40) * (1 / 2) ^ s / 2 := by
      positivity
    exact mul_nonneg (by positivity) (by linarith)
  unfold Hres
  linarith

/-! ### The explicit lower bound of `G` -/

private theorem exp_neg_mul_cc (s : ℕ) :
    Real.exp (-(s : ℝ)) * cc s = Real.exp 1 * poissonMass (s + 1) / ((s : ℝ) + 1) := by
  have h1 : ((s : ℝ) + 1) ≠ 0 := by positivity
  have hF : ((s + 1).factorial : ℝ) ≠ 0 := by positivity
  have he : Real.exp 1 * Real.exp (-((s + 1 : ℕ) : ℝ)) = Real.exp (-(s : ℝ)) := by
    rw [← Real.exp_add]
    congr 1
    push_cast
    ring
  unfold poissonMass ren
  rw [cc_eq, ← he]
  push_cast
  rw [pow_succ]
  field

/-- `G_s ≥ e (1 - 1/(12(s+1))) (4 - 21/(s+1)) / ((s+1) √(2π(s+1)))` for `s ≥ 6`. -/
theorem Gres_lower {s : ℕ} (hs : 6 ≤ s) :
    Real.exp 1 * ((1 - 1 / (12 * ((s : ℝ) + 1))) / Real.sqrt (2 * Real.pi * ((s : ℝ) + 1)))
        / ((s : ℝ) + 1) * (4 - 21 / ((s : ℝ) + 1)) ≤ Gres s := by
  have h1 := Hres_half_lower hs
  have h2 := poissonMass_ge (n := s + 1) (by omega)
  rw [Nat.cast_add, Nat.cast_one] at h2
  have hE : 0 < Real.exp (-(s : ℝ)) := Real.exp_pos _
  have hS : (0 : ℝ) < (s : ℝ) + 1 := by positivity
  have h3 : 0 ≤ 4 - 21 / ((s : ℝ) + 1) := by
    have h6 : (6 : ℝ) ≤ (s : ℝ) := by exact_mod_cast hs
    rw [sub_nonneg, div_le_iff₀ hS]
    linarith
  have h4 : Real.exp 1 * ((1 - 1 / (12 * ((s : ℝ) + 1)))
        / Real.sqrt (2 * Real.pi * ((s : ℝ) + 1))) / ((s : ℝ) + 1)
      ≤ Real.exp 1 * poissonMass (s + 1) / ((s : ℝ) + 1) :=
    div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left h2 (Real.exp_pos 1).le) hS.le
  unfold Gres
  calc Real.exp 1 * ((1 - 1 / (12 * ((s : ℝ) + 1))) / Real.sqrt (2 * Real.pi * ((s : ℝ) + 1)))
        / ((s : ℝ) + 1) * (4 - 21 / ((s : ℝ) + 1))
      ≤ Real.exp 1 * poissonMass (s + 1) / ((s : ℝ) + 1) * (4 - 21 / ((s : ℝ) + 1)) :=
        mul_le_mul_of_nonneg_right h4 h3
    _ = Real.exp (-(s : ℝ)) * (cc s * (4 - 21 / ((s : ℝ) + 1))) := by
        rw [← exp_neg_mul_cc]
        ring
    _ ≤ Real.exp (-(s : ℝ)) * Hres s := mul_le_mul_of_nonneg_left h1 hE.le

end Parking
