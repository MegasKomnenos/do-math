import Mathlib.Algebra.Group.ForwardDiff
import Mathlib.Algebra.Order.Ring.Pow
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Field
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Positivity

/-!
# Cayley coefficients and Abel's identity

* `cay j = j^(j-1)/j!` (`cay 0 = 0`): the number of rooted labelled trees on `j` vertices over `j!`.
* `cc n = cay (n+1) = (n+1)^(n-1)/n!`: the number of parking functions of length `n` over `n!`.
* `eps m = (m-1)^(m-1)/m!` (`eps 0 = 0`, `eps 1 = 1`): prime parking functions over `m!`.
* `ren n = n^n/n!`.

The one classical identity used by the whole development is Abel's binomial identity
(`abel_identity`).  At `x = 1`, `y = n + 1` it gives the last-car recursion without a displacement
bound, `(n+1) c_{n+1} = ∑_{j ≤ n} (j+1) c_j c_{n-j}` (`cc_rec`), which is the same statement as the
convolution identity `∑_{α+β=t} α a_α a_β = (t-1) a_t` (`cay_conv`).

The file ends with the ratio `a_{j+1}/a_j = (1+1/j)^(j-1)` (`cay_ratio`), the monotonicity of
`(1+1/i)^i` and of `(1+1/i)^(i-1)` (`chi_mono`, `psi_mono`), and the resulting log-convexity of
the Cayley coefficients (`cay_logconvex`).
-/

namespace Parking

open Finset

/-- Cayley coefficient `a_j = j^(j-1)/j!`, with `a_0 = 0`. -/
noncomputable def cay (j : ℕ) : ℝ := if j = 0 then 0 else (j : ℝ) ^ (j - 1) / (j.factorial : ℝ)

/-- `c_n = (n+1)^(n-1)/n! = a_{n+1}`. -/
noncomputable def cc (n : ℕ) : ℝ := cay (n + 1)

/-- `ε_m = (m-1)^(m-1)/m!` for `m ≥ 1` (`ε_1 = 1`), and `ε_0 = 0`. -/
noncomputable def eps (m : ℕ) : ℝ :=
  if m = 0 then 0 else ((m : ℝ) - 1) ^ (m - 1) / (m.factorial : ℝ)

/-- `ren n = n^n/n!` (`ren 0 = 1`). -/
noncomputable def ren (n : ℕ) : ℝ := (n : ℝ) ^ n / (n.factorial : ℝ)

/-- The Cayley coefficient of index $0$ is $a_0 = 0$. -/
@[simp] theorem cay_zero : cay 0 = 0 := by simp [cay]

/-- The Cayley coefficient at a positive index, written without a case distinction: $a_{j+1} =
(j+1)^j/(j+1)!$. -/
theorem cay_succ (j : ℕ) : cay (j + 1) = ((j : ℝ) + 1) ^ j / ((j + 1).factorial : ℝ) := by
  simp [cay]

/-- The Cayley coefficient of index $1$ is $a_1 = 1$. -/
theorem cay_one : cay 1 = 1 := by simp [cay]

/-- The Cayley coefficient $a_j = j^{j-1}/j!$ is positive for every $j \ge 1$. -/
theorem cay_pos {j : ℕ} (hj : 0 < j) : 0 < cay j := by
  obtain ⟨i, rfl⟩ : ∃ i, j = i + 1 := ⟨j - 1, by omega⟩
  rw [cay_succ]
  positivity

/-- The Cayley coefficients are nonnegative: $a_j \ge 0$ for every $j \ge 0$. -/
theorem cay_nonneg (j : ℕ) : 0 ≤ cay j := by
  rcases Nat.eq_zero_or_pos j with rfl | hj
  · simp
  · exact (cay_pos hj).le

/-- The normalised parking number in the form that its definition unfolds to: $c_n =
(n+1)^n/(n+1)!$. -/
theorem cc_eq (n : ℕ) : cc n = ((n : ℝ) + 1) ^ n / ((n + 1).factorial : ℝ) := by
  rw [cc, cay_succ]

/-- The normalised parking number of length $0$ is $c_0 = 1$. -/
theorem cc_zero : cc 0 = 1 := by simp [cc, cay]

/-- The normalised parking numbers $c_n = (n+1)^{n-1}/n!$ are positive for every $n \ge 0$. -/
theorem cc_pos (n : ℕ) : 0 < cc n := cay_pos (Nat.succ_pos n)

/-- The first value of the kernel $\varepsilon_m = (m-1)^{m-1}/m!$ is $\varepsilon_1 = 1$. -/
theorem eps_one : eps 1 = 1 := by simp [eps]

/-- The kernel $\varepsilon$ at a positive index, written without a case distinction:
$\varepsilon_{m+1} = m^m/(m+1)!$. -/
theorem eps_succ (m : ℕ) : eps (m + 1) = (m : ℝ) ^ m / ((m + 1).factorial : ℝ) := by
  simp [eps]

/-- The kernel $\varepsilon_m = (m-1)^{m-1}/m!$ ($\varepsilon_0 = 0$) is nonnegative for every $m
\ge 0$. -/
theorem eps_nonneg (m : ℕ) : 0 ≤ eps m := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp [eps]
  · obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
    rw [eps_succ]
    positivity

/-- The numbers $\operatorname{ren}(n) = n^n/n!$ are positive for every $n \ge 0$. -/
theorem ren_pos (n : ℕ) : 0 < ren n := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp [ren]
  · have h : (0 : ℝ) < n := by exact_mod_cast hn
    unfold ren
    exact div_pos (pow_pos h n) (by positivity)

/-- `m ε_m = ren (m-1)` for `m ≥ 1`. -/
theorem mul_eps (m : ℕ) : ((m : ℝ) + 1) * eps (m + 1) = ren m := by
  have h1 : ((m : ℝ) + 1) ≠ 0 := by positivity
  rw [eps_succ, ren, Nat.factorial_succ]
  push_cast
  rw [mul_div_assoc', mul_div_mul_left _ _ h1]

/-! ### Abel's binomial identity -/

/-- The `m`-th forward difference of the polynomial `r ↦ r^(m-1)` vanishes (`m ≥ 1`):
`∑_k (-1)^(m-k) C(m,k) (x+k)^(m-1) = 0`. -/
private theorem alt_sum_zero {m : ℕ} (hm : 0 < m) (x : ℝ) :
    ∑ k ∈ range (m + 1), (-1 : ℝ) ^ (m - k) * (m.choose k : ℝ) * (x + k) ^ (m - 1) = 0 := by
  have h1 := fwdDiff_iter_eq_sum_shift (1 : ℝ) (fun r : ℝ => r ^ (m - 1)) m x
  have h2 : (fwdDiff (1 : ℝ))^[m] (fun r : ℝ => r ^ (m - 1)) = 0 :=
    fwdDiff_iter_pow_eq_zero_of_lt (by omega)
  rw [h2] at h1
  simp only [Pi.zero_apply, zsmul_eq_mul, Int.cast_mul, Int.cast_pow, Int.cast_neg, Int.cast_one,
    Int.cast_natCast, nsmul_eq_mul, mul_one] at h1
  exact h1.symm

/-- The inner sum of Abel's identity: `∑_k C(m,k) w_k (-(x+k))^(m-k) = [m = 0]`. -/
private theorem abel_inner (m : ℕ) (x : ℝ) :
    ∑ k ∈ range (m + 1), (m.choose k : ℝ) *
      (if k = 0 then 1 else x * (x + k) ^ (k - 1)) * (-(x + k)) ^ (m - k)
      = if m = 0 then 1 else 0 := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  · have hm0 : m ≠ 0 := by omega
    rw [ite_eq_right hm0]
    have key : ∀ k ∈ range (m + 1), (m.choose k : ℝ) *
        (if k = 0 then 1 else x * (x + k) ^ (k - 1)) * (-(x + k)) ^ (m - k)
        = x * ((-1 : ℝ) ^ (m - k) * (m.choose k : ℝ) * (x + k) ^ (m - 1)) := by
      intro k hk
      rw [mem_range] at hk
      rcases Nat.eq_zero_or_pos k with rfl | hk0
      · have hx : x ^ m = x * x ^ (m - 1) := by
          rw [← pow_succ']
          congr 1
          omega
        rw [ite_eq_left rfl]
        simp only [Nat.cast_zero, add_zero, Nat.sub_zero, Nat.choose_zero_right, Nat.cast_one,
          one_mul, mul_one]
        rw [neg_pow, hx]
        ring
      · have hk0' : k ≠ 0 := by omega
        have e1 : m - 1 = (k - 1) + (m - k) := by omega
        rw [ite_eq_right hk0', e1, pow_add, neg_pow]
        ring
    rw [sum_congr rfl key, ← mul_sum, alt_sum_zero hm x, mul_zero]

/-- `C(n,k) C(n-k,i) = C(n,i) C(n-i,k)` (both are the trinomial coefficient). -/
private theorem choose_mul_choose_swap (n k i : ℕ) :
    n.choose k * (n - k).choose i = n.choose i * (n - i).choose k := by
  have h1 := Nat.choose_mul (n := n) (k := k + i) (s := k) (Nat.le_add_right k i)
  have h2 := Nat.choose_mul (n := n) (k := k + i) (s := i) (Nat.le_add_left i k)
  rw [Nat.add_sub_cancel_left] at h1
  rw [Nat.add_sub_cancel] at h2
  rw [← h1, ← h2, Nat.choose_symm_add]

/-- Binomial expansion of `(y-k)^(n-k) = ((x+y) - (x+k))^(n-k)` and exchange of summations,
for an arbitrary weight `w`. -/
private theorem abel_expand (n : ℕ) (w : ℕ → ℝ) (x y : ℝ) :
    ∑ k ∈ range (n + 1), (n.choose k : ℝ) * w k * (y - k) ^ (n - k)
      = ∑ i ∈ range (n + 1), (n.choose i : ℝ) * (x + y) ^ i *
          ∑ k ∈ range (n - i + 1), ((n - i).choose k : ℝ) * w k * (-(x + k)) ^ (n - i - k) := by
  have hexp : ∀ k ∈ range (n + 1), (n.choose k : ℝ) * w k * (y - k) ^ (n - k)
      = ∑ i ∈ range (n - k + 1), (n.choose k : ℝ) * w k *
          ((x + y) ^ i * (-(x + k)) ^ (n - k - i) * ((n - k).choose i : ℝ)) := by
    intro k _
    have h : y - k = (x + y) + (-(x + k)) := by ring
    rw [h, add_pow, mul_sum]
  have hswap : ∑ k ∈ range (n + 1), ∑ i ∈ range (n - k + 1), (n.choose k : ℝ) * w k *
          ((x + y) ^ i * (-(x + k)) ^ (n - k - i) * ((n - k).choose i : ℝ))
      = ∑ i ∈ range (n + 1), ∑ k ∈ range (n - i + 1), (n.choose k : ℝ) * w k *
          ((x + y) ^ i * (-(x + k)) ^ (n - k - i) * ((n - k).choose i : ℝ)) := by
    apply sum_comm'
    intro k i
    simp only [mem_range]
    omega
  rw [sum_congr rfl hexp, hswap]
  apply sum_congr rfl
  intro i _
  rw [mul_sum]
  apply sum_congr rfl
  intro k _
  have e : n - k - i = n - i - k := by omega
  have hc : (n.choose k : ℝ) * ((n - k).choose i : ℝ)
      = (n.choose i : ℝ) * ((n - i).choose k : ℝ) := by
    exact_mod_cast choose_mul_choose_swap n k i
  rw [e]
  linear_combination (w k * (x + y) ^ i * (-(x + k)) ^ (n - i - k)) * hc

/-- The weight of Abel's identity: `w_0(x) = 1`, `w_k(x) = x (x+k)^(k-1)` for `k ≥ 1`. -/
noncomputable def abelW (x : ℝ) (k : ℕ) : ℝ := if k = 0 then 1 else x * (x + k) ^ (k - 1)

/-- **Abel's binomial identity**: `∑_k C(n,k) w_k(x) (y-k)^(n-k) = (x+y)^n`. -/
theorem abel_identity (n : ℕ) (x y : ℝ) :
    ∑ k ∈ range (n + 1), (n.choose k : ℝ) * abelW x k * (y - k) ^ (n - k) = (x + y) ^ n := by
  unfold abelW
  refine (abel_expand n _ x y).trans ?_
  rw [sum_range_succ, sum_eq_zero (s := range n), zero_add]
  · rw [abel_inner (n - n) x]
    simp
  · intro i hi
    rw [mem_range] at hi
    have h0 : n - i ≠ 0 := by omega
    rw [abel_inner (n - i) x, ite_eq_right h0, mul_zero]

/-! ### The convolution identity -/

/-- `(j+1) c_j = (j+1)^j / j!`. -/
private theorem succ_mul_cc (j : ℕ) :
    ((j : ℝ) + 1) * cc j = ((j : ℝ) + 1) ^ j / (j.factorial : ℝ) := by
  have h1 : ((j : ℝ) + 1) ≠ 0 := by positivity
  rw [cc_eq, Nat.factorial_succ]
  push_cast
  rw [mul_div_assoc', mul_div_mul_left _ _ h1]

/-- `c_k = w_k(1) / k!`, where `w` is the weight of Abel's identity. -/
theorem cc_eq_abelW (k : ℕ) : cc k = abelW 1 k / (k.factorial : ℝ) := by
  unfold abelW
  rcases k with _ | i
  · simp [cc_zero]
  · have h1 : ((i : ℝ) + 1 + 1) ≠ 0 := by positivity
    have h2 : ((i + 1).factorial : ℝ) ≠ 0 := by positivity
    rw [cc_eq, ite_eq_right (Nat.succ_ne_zero i), Nat.factorial_succ (i + 1), Nat.add_sub_cancel]
    push_cast
    rw [pow_succ]
    field

/-- The last-car recursion without a displacement bound, solved by `cc`:
`(n+1) c_{n+1} = ∑_{j ≤ n} (j+1) c_j c_{n-j}`.  After the reflection `j ↦ n - j` and
multiplication by `n!`, this is Abel's identity at `x = 1`, `y = n + 1`. -/
theorem cc_rec (n : ℕ) :
    ((n : ℝ) + 1) * cc (n + 1) = ∑ j ∈ range (n + 1), ((j : ℝ) + 1) * cc j * cc (n - j) := by
  have hrefl : ∑ j ∈ range (n + 1), ((j : ℝ) + 1) * cc j * cc (n - j)
      = ∑ k ∈ range (n + 1), (((n - k : ℕ) : ℝ) + 1) * cc (n - k) * cc (n - (n - k)) :=
    (sum_flip (fun j => ((j : ℝ) + 1) * cc j * cc (n - j))).symm
  have hterm : ∀ k ∈ range (n + 1),
      (((n - k : ℕ) : ℝ) + 1) * cc (n - k) * cc (n - (n - k))
      = (n.choose k : ℝ) * abelW 1 k * ((n : ℝ) + 1 - k) ^ (n - k) * (n.factorial : ℝ)⁻¹ := by
    intro k hk
    rw [mem_range] at hk
    have hkn : k ≤ n := by omega
    have e2 : n - (n - k) = k := by omega
    have h1 : (k.factorial : ℝ) ≠ 0 := by positivity
    have h2 : ((n - k).factorial : ℝ) ≠ 0 := by positivity
    have h3 : (n.factorial : ℝ) ≠ 0 := by positivity
    have hch : (n.choose k : ℝ) * (k.factorial : ℝ) * ((n - k).factorial : ℝ)
        = (n.factorial : ℝ) := by
      exact_mod_cast Nat.choose_mul_factorial_mul_factorial hkn
    have hC : (n.choose k : ℝ)
        = (n.factorial : ℝ) / ((k.factorial : ℝ) * ((n - k).factorial : ℝ)) := by
      rw [eq_div_iff (mul_ne_zero h1 h2)]
      linear_combination hch
    have e3 : ((n : ℝ) + 1 - k) = ((n - k : ℕ) : ℝ) + 1 := by
      rw [Nat.cast_sub hkn]
      ring
    rw [e2, succ_mul_cc, cc_eq_abelW, hC, e3]
    field
  have hlhs : ((n : ℝ) + 1) * cc (n + 1) = (1 + ((n : ℝ) + 1)) ^ n * (n.factorial : ℝ)⁻¹ := by
    have h3 : (n.factorial : ℝ) ≠ 0 := by positivity
    have h4 : ((n : ℝ) + 1) ≠ 0 := by positivity
    have h5 : ((n : ℝ) + 1 + 1) ≠ 0 := by positivity
    rw [cc_eq (n + 1), Nat.factorial_succ (n + 1), Nat.factorial_succ n]
    push_cast
    rw [pow_succ]
    field
  rw [hrefl, sum_congr rfl hterm, ← sum_mul, abel_identity n 1 ((n : ℝ) + 1), hlhs]

/-- The fundamental convolution identity `∑_{α=1}^{t-1} α a_α a_{t-α} = (t-1) a_t`
(equivalently `z T'(z) (1 - T(z)) = T(z)` for the tree function): `cc_rec` written with
`a_j = c_{j-1}`. -/
theorem cay_conv (t : ℕ) :
    ∑ α ∈ range t, (α : ℝ) * cay α * cay (t - α) = ((t : ℝ) - 1) * cay t := by
  rcases t with _ | _ | n
  · simp
  · simp
  · have h1 : ∑ α ∈ range (n + 1 + 1), (α : ℝ) * cay α * cay (n + 1 + 1 - α)
        = ∑ j ∈ range (n + 1), ((j : ℝ) + 1) * cc j * cc (n - j) := by
      rw [sum_range_succ']
      simp only [Nat.cast_zero, zero_mul, add_zero]
      refine sum_congr rfl fun j hj => ?_
      rw [mem_range] at hj
      rw [show n + 1 + 1 - (j + 1) = n - j + 1 by omega, Nat.cast_add, Nat.cast_one]
      rfl
    rw [h1, ← cc_rec n, cc]
    push_cast
    ring

/-- Symmetric form: `t ∑_{α+β=t} a_α a_β = 2 (t-1) a_t`. -/
theorem cay_conv_sym (t : ℕ) :
    (t : ℝ) * ∑ α ∈ range (t + 1), cay α * cay (t - α) = 2 * ((t : ℝ) - 1) * cay t := by
  have h1 : ∑ α ∈ range (t + 1), (α : ℝ) * cay α * cay (t - α) = ((t : ℝ) - 1) * cay t := by
    rw [sum_range_succ, cay_conv t, Nat.sub_self, cay_zero, mul_zero, add_zero]
  have h2 : ∑ α ∈ range (t + 1), ((t - α : ℕ) : ℝ) * cay (t - α) * cay (t - (t - α))
      = ((t : ℝ) - 1) * cay t := by
    rw [← h1]
    exact sum_flip (fun α => (α : ℝ) * cay α * cay (t - α))
  have h3 : ∀ α ∈ range (t + 1), (t : ℝ) * (cay α * cay (t - α))
      = (α : ℝ) * cay α * cay (t - α)
        + ((t - α : ℕ) : ℝ) * cay (t - α) * cay (t - (t - α)) := by
    intro α hα
    rw [mem_range] at hα
    have hle : α ≤ t := by omega
    have e : t - (t - α) = α := by omega
    rw [e, Nat.cast_sub hle]
    ring
  rw [mul_sum, sum_congr rfl h3, sum_add_distrib, h1, h2]
  ring

/-! ### Ratios and monotonicity -/

/-- `a_{j+1}/a_j = (1+1/j)^(j-1)`. -/
theorem cay_ratio {j : ℕ} (hj : 0 < j) : cay (j + 1) = (1 + 1 / (j : ℝ)) ^ (j - 1) * cay j := by
  obtain ⟨i, rfl⟩ : ∃ i, j = i + 1 := ⟨j - 1, by omega⟩
  have h1 : ((i : ℝ) + 1) ≠ 0 := by positivity
  have h2 : ((i : ℝ) + 1 + 1) ≠ 0 := by positivity
  have h3 : ((i + 1).factorial : ℝ) ≠ 0 := by positivity
  have hq : ((i : ℝ) + 1) ^ i ≠ 0 := pow_ne_zero _ h1
  have e1 : (1 : ℝ) + 1 / ((i + 1 : ℕ) : ℝ) = ((i : ℝ) + 1 + 1) / ((i : ℝ) + 1) := by
    push_cast
    field
  rw [e1, cay_succ (i + 1), cay_succ i, Nat.factorial_succ (i + 1), Nat.add_sub_cancel, div_pow]
  push_cast
  rw [pow_succ]
  field

/-- One step of `chi_mono`: `(1+1/i)^i ≤ (1+1/(i+1))^(i+1)`. -/
private theorem chi_step {i : ℕ} (hi : 0 < i) :
    (1 + 1 / (i : ℝ)) ^ i ≤ (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1) := by
  have ha : (0 : ℝ) < i := by exact_mod_cast hi
  have ha1 : (0 : ℝ) < (i : ℝ) + 1 := by linarith
  have hne : (i : ℝ) ≠ 0 := ha.ne'
  have hne1 : (i : ℝ) + 1 ≠ 0 := ha1.ne'
  -- Bernoulli's inequality
  have hb : 1 + ((i + 1 : ℕ) : ℝ) * (-(1 / ((i : ℝ) + 1) ^ 2))
      ≤ (1 + -(1 / ((i : ℝ) + 1) ^ 2)) ^ (i + 1) := by
    apply one_add_mul_le_pow
    have h : 1 / ((i : ℝ) + 1) ^ 2 ≤ 1 := by
      rw [div_le_one (by positivity)]
      nlinarith
    linarith
  have e1 : (1 : ℝ) + 1 / ((i + 1 : ℕ) : ℝ)
      = (1 + 1 / (i : ℝ)) * (1 + -(1 / ((i : ℝ) + 1) ^ 2)) := by
    push_cast
    field
  have e2 : (1 + 1 / (i : ℝ)) * (1 + ((i + 1 : ℕ) : ℝ) * (-(1 / ((i : ℝ) + 1) ^ 2))) = 1 := by
    push_cast
    field
  rw [e1, mul_pow, pow_succ (1 + 1 / (i : ℝ)) i]
  calc (1 + 1 / (i : ℝ)) ^ i
      = (1 + 1 / (i : ℝ)) ^ i
          * ((1 + 1 / (i : ℝ)) * (1 + ((i + 1 : ℕ) : ℝ) * (-(1 / ((i : ℝ) + 1) ^ 2)))) := by
        rw [e2, mul_one]
    _ = (1 + 1 / (i : ℝ)) ^ i * (1 + 1 / (i : ℝ))
          * (1 + ((i + 1 : ℕ) : ℝ) * (-(1 / ((i : ℝ) + 1) ^ 2))) := by ring
    _ ≤ (1 + 1 / (i : ℝ)) ^ i * (1 + 1 / (i : ℝ))
          * (1 + -(1 / ((i : ℝ) + 1) ^ 2)) ^ (i + 1) := by
        apply mul_le_mul_of_nonneg_left hb
        positivity

/-- `(1+1/i)^i` is nondecreasing in `i ≥ 1`. -/
theorem chi_mono {i j : ℕ} (hi : 0 < i) (hij : i ≤ j) :
    (1 + 1 / (i : ℝ)) ^ i ≤ (1 + 1 / (j : ℝ)) ^ j := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ k hk ih => exact ih.trans (chi_step (by omega))

/-- One step of `psi_mono`: `(1+1/i)^(i-1) ≤ (1+1/(i+1))^i`.  It follows from `chi_step`, since
`(1+1/i)^(i-1) (1+1/i) = (1+1/i)^i ≤ (1+1/(i+1))^(i+1) ≤ (1+1/(i+1))^i (1+1/i)`. -/
private theorem psi_step {i : ℕ} (hi : 0 < i) :
    (1 + 1 / (i : ℝ)) ^ (i - 1) ≤ (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1 - 1) := by
  obtain ⟨m, rfl⟩ : ∃ m, i = m + 1 := ⟨i - 1, by omega⟩
  have hpos : (0 : ℝ) < 1 + 1 / ((m + 1 : ℕ) : ℝ) := by positivity
  have hba : 1 + 1 / ((m + 1 + 1 : ℕ) : ℝ) ≤ 1 + 1 / ((m + 1 : ℕ) : ℝ) := by
    have h : ((m + 1 : ℕ) : ℝ) ≤ ((m + 1 + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.le_succ (m + 1)
    have h' := one_div_le_one_div_of_le (by positivity) h
    linarith
  have h := chi_step (Nat.succ_pos m)
  rw [pow_succ, pow_succ _ (m + 1)] at h
  simp only [Nat.add_sub_cancel]
  refine le_of_mul_le_mul_right (h.trans ?_) hpos
  gcongr

/-- `(1+1/i)^(i-1)` is nondecreasing in `i ≥ 1`. -/
theorem psi_mono {i j : ℕ} (hi : 0 < i) (hij : i ≤ j) :
    (1 + 1 / (i : ℝ)) ^ (i - 1) ≤ (1 + 1 / (j : ℝ)) ^ (j - 1) := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ k hk ih => exact ih.trans (psi_step (by omega))

/-- Log-convexity in ratio form: for `1 ≤ u`, `u ≤ v`, `c ≥ 0`:
`a_{u+c} a_v ≤ a_u a_{v+c}`. -/
theorem cay_logconvex {u v c : ℕ} (hu : 0 < u) (huv : u ≤ v) :
    cay (u + c) * cay v ≤ cay u * cay (v + c) := by
  induction c with
  | zero => simp
  | succ c ih =>
    have h1 : cay (u + (c + 1))
        = (1 + 1 / ((u + c : ℕ) : ℝ)) ^ (u + c - 1) * cay (u + c) :=
      cay_ratio (j := u + c) (by omega)
    have h2 : cay (v + (c + 1))
        = (1 + 1 / ((v + c : ℕ) : ℝ)) ^ (v + c - 1) * cay (v + c) :=
      cay_ratio (j := v + c) (by omega)
    have hpsi : (1 + 1 / ((u + c : ℕ) : ℝ)) ^ (u + c - 1)
        ≤ (1 + 1 / ((v + c : ℕ) : ℝ)) ^ (v + c - 1) :=
      psi_mono (by omega) (by omega)
    have hnn : 0 ≤ (1 + 1 / ((u + c : ℕ) : ℝ)) ^ (u + c - 1) := by positivity
    rw [h1, h2]
    calc (1 + 1 / ((u + c : ℕ) : ℝ)) ^ (u + c - 1) * cay (u + c) * cay v
        = (1 + 1 / ((u + c : ℕ) : ℝ)) ^ (u + c - 1) * (cay (u + c) * cay v) := by ring
      _ ≤ (1 + 1 / ((v + c : ℕ) : ℝ)) ^ (v + c - 1) * (cay u * cay (v + c)) :=
          mul_le_mul hpsi ih (mul_nonneg (cay_nonneg _) (cay_nonneg _)) (hnn.trans hpsi)
      _ = cay u * ((1 + 1 / ((v + c : ℕ) : ℝ)) ^ (v + c - 1) * cay (v + c)) := by ring

end Parking
