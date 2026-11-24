module

public import Parking.Basic.Sums
public import Mathlib.Algebra.Order.BigOperators.Ring.Finset
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.LinearCombination
public import Mathlib.Tactic.Positivity

/-!
# The birthday law

Throw balls independently and uniformly into `m` boxes.  The probability that the first `j` balls
fall into distinct boxes is `P_j = (m)_j/m^j = ∏_{i<j} (1 - i/m)` (`Pb m j`).

* `Pb`, `sbirth`, `Dbirth` : the tail `P_j`, the sum `s_m = ∑_{j=1}^m P_j` (Ramanujan's `Q(m)`), and
  `D_m = 3((m+2)s_m - 3m) / (2(m - s_m))`.
* `Pb_key`       : `(q/m) P_q = P_q - P_{q+1}`.
* `Pb_lr`        : likelihood-ratio comparison of the tails for `m` and `m+1`.
* `Pb_moment`, `Pb_sum1`, …, `Pb_sum4` : the sums `∑_q g(q) q P_q` by Abel summation.
* `sbirth_sq_le`, `sbirth_lt`, `Dbirth_le` : `s_m² + s_m ≤ 2m`, `s_m < m`, `D_m ≤ (3/2)(s_m - 1)`.
-/

@[expose] public section

namespace Parking

open Finset

/-- Birthday tail `P_j = (m)_j / m^j = ∏_{i<j} (1 - i/m)`. -/
noncomputable def Pb (m j : ℕ) : ℝ := ∏ i ∈ range j, (1 - (i : ℝ) / m)

/-- `s_m = ∑_{j=1}^m (m)_j/m^j` (mean number of parts under the birthday law; Ramanujan's
`Q(m)`). -/
noncomputable def sbirth (m : ℕ) : ℝ := ∑ j ∈ Icc 1 m, Pb m j

/-- `D_m = 3((m+2)s_m - 3m) / (2(m - s_m))`. -/
noncomputable def Dbirth (m : ℕ) : ℝ :=
  3 * (((m : ℝ) + 2) * sbirth m - 3 * m) / (2 * ((m : ℝ) - sbirth m))

/-! ### Sums over `[1,n]` -/

/-- Abel summation. -/
private theorem abel_sum' (g p : ℕ → ℝ) (n : ℕ) :
    ∑ i ∈ range n, g (i + 1) * (p (i + 1) - p (i + 1 + 1))
      = ∑ i ∈ range n, (g (i + 1) - g i) * p (i + 1) + g 0 * p 1 - g n * p (n + 1) := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, Finset.sum_range_succ, ih]
    ring

/-! ### The birthday tail `Pb` -/

/-- The birthday tail at the index $0$ is $1$: $P_{m,0} = 1$. -/
theorem Pb_zero (m : ℕ) : Pb m 0 = 1 := by simp [Pb]

/-- The recursion of the birthday tail: $P_{m,j+1} = P_{m,j}\,(1 - j/m)$. -/
theorem Pb_succ (m j : ℕ) : Pb m (j + 1) = Pb m j * (1 - (j : ℝ) / m) := by
  unfold Pb
  rw [Finset.prod_range_succ]

/-- The birthday tail at the index $1$ is $1$: $P_{m,1} = 1$. -/
theorem Pb_one (m : ℕ) : Pb m 1 = 1 := by
  have h := Pb_succ m 0
  rw [Pb_zero, Nat.cast_zero, zero_div, sub_zero, mul_one] at h
  exact h

/-- The birthday tail of $m \ge 1$ vanishes at the index $m + 1$: $P_{m,m+1} = 0$. -/
theorem Pb_succ_self {m : ℕ} (hm : 1 ≤ m) : Pb m (m + 1) = 0 := by
  have hm' : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
  rw [Pb_succ, div_self hm', sub_self, mul_zero]

/-- The birthday tail of $m \ge 1$ vanishes beyond $m$: $P_{m,j} = 0$ for $j \ge m + 1$. -/
theorem Pb_eq_zero {m j : ℕ} (hm : 1 ≤ m) (hj : m + 1 ≤ j) : Pb m j = 0 := by
  have hm' : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
  unfold Pb
  exact Finset.prod_eq_zero (mem_range.2 (by omega : m < j))
    (by show (1 : ℝ) - (m : ℝ) / (m : ℝ) = 0; rw [div_self hm', sub_self])

/-- The birthday tail is nonnegative: $P_{m,j} \ge 0$. -/
theorem Pb_nonneg (m j : ℕ) : 0 ≤ Pb m j := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp [Pb]
  · rcases le_or_gt j m with hj | hj
    · unfold Pb
      refine Finset.prod_nonneg fun i hi => ?_
      rw [mem_range] at hi
      have hm' : (0 : ℝ) < m := Nat.cast_pos.2 hm
      have : (i : ℝ) / m ≤ 1 := (div_le_one hm').2 (by exact_mod_cast (by omega : i ≤ m))
      linarith
    · exact le_of_eq (Pb_eq_zero hm (by omega)).symm

private theorem Pb_le_one (m j : ℕ) : Pb m j ≤ 1 := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp [Pb]
  · rcases le_or_gt j m with hj | hj
    · unfold Pb
      have hm' : (0 : ℝ) < m := Nat.cast_pos.2 hm
      refine Finset.prod_le_one₀ (fun i hi => ?_) (fun i hi => ?_)
      · rw [mem_range] at hi
        have : (i : ℝ) / m ≤ 1 := (div_le_one hm').2 (by exact_mod_cast (by omega : i ≤ m))
        linarith
      · have : 0 ≤ (i : ℝ) / m := div_nonneg (Nat.cast_nonneg i) hm'.le
        linarith
    · rw [Pb_eq_zero hm (by omega)]
      exact zero_le_one

/-- `(q/m) P_q = P_q - P_{q+1}`. -/
private theorem Pb_key {m : ℕ} (hm : 1 ≤ m) (q : ℕ) :
    (q : ℝ) * Pb m q = m * (Pb m q - Pb m (q + 1)) := by
  have hm' : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
  rw [Pb_succ]
  have h : (m : ℝ) * ((q : ℝ) / m) = q := mul_div_cancel₀ _ hm'
  linear_combination (-(Pb m q)) * h

/-- Likelihood-ratio comparison of the birthday tails for `m` and `m+1`. -/
theorem Pb_lr (m : ℕ) {q q' : ℕ} (hqq' : q ≤ q') :
    q' ≤ m + 1 → Pb m q' * Pb (m + 1) q ≤ Pb m q * Pb (m + 1) q' := by
  induction q', hqq' using Nat.le_induction with
  | base => intro _; exact le_refl _
  | succ k hk ih =>
    intro hk1
    have ih' := ih (by omega)
    rw [Pb_succ m k, Pb_succ (m + 1) k]
    have hPm : 0 ≤ Pb m q := Pb_nonneg m q
    have hPk : 0 ≤ Pb (m + 1) k := Pb_nonneg (m + 1) k
    have hα : 0 ≤ 1 - (k : ℝ) / m := by
      rcases Nat.eq_zero_or_pos m with hm0 | hm
      · rw [hm0]; simp
      · have hm' : (0 : ℝ) < m := Nat.cast_pos.2 hm
        have : (k : ℝ) / m ≤ 1 := (div_le_one hm').2 (by exact_mod_cast (by omega : k ≤ m))
        linarith
    have hαβ : 1 - (k : ℝ) / m ≤ 1 - (k : ℝ) / ((m + 1 : ℕ) : ℝ) := by
      rcases Nat.eq_zero_or_pos m with hm0 | hm
      · have hk0 : k = 0 := by omega
        rw [hk0]; simp
      · have hm' : (0 : ℝ) < m := Nat.cast_pos.2 hm
        have : (k : ℝ) / ((m + 1 : ℕ) : ℝ) ≤ (k : ℝ) / m :=
          div_le_div_of_nonneg_left (Nat.cast_nonneg k) hm'
            (by rw [Nat.cast_add, Nat.cast_one]; linarith)
        linarith
    calc Pb m k * (1 - (k : ℝ) / m) * Pb (m + 1) q
        = (Pb m k * Pb (m + 1) q) * (1 - (k : ℝ) / m) := by ring
      _ ≤ (Pb m q * Pb (m + 1) k) * (1 - (k : ℝ) / m) := mul_le_mul_of_nonneg_right ih' hα
      _ ≤ (Pb m q * Pb (m + 1) k) * (1 - (k : ℝ) / ((m + 1 : ℕ) : ℝ)) :=
          mul_le_mul_of_nonneg_left hαβ (mul_nonneg hPm hPk)
      _ = Pb m q * (Pb (m + 1) k * (1 - (k : ℝ) / ((m + 1 : ℕ) : ℝ))) := by ring

/-! ### Moments of the birthday law -/

private theorem sbirth_eq_range (m : ℕ) : sbirth m = ∑ i ∈ range m, Pb m (i + 1) := by
  unfold sbirth
  exact sum_Icc_one_eq_range (Pb m) m

/-- Abel summation against the birthday law. -/
theorem Pb_moment {m : ℕ} (hm : 1 ≤ m) (g : ℕ → ℝ) :
    ∑ i ∈ range m, g (i + 1) * (((i : ℝ) + 1) * Pb m (i + 1))
      = m * (∑ i ∈ range m, (g (i + 1) - g i) * Pb m (i + 1) + g 0) := by
  have h1 : ∀ i ∈ range m, g (i + 1) * (((i : ℝ) + 1) * Pb m (i + 1))
      = m * (g (i + 1) * (Pb m (i + 1) - Pb m (i + 1 + 1))) := by
    intro i _
    have h := Pb_key hm (i + 1)
    rw [Nat.cast_add, Nat.cast_one] at h
    rw [h]
    ring
  rw [Finset.sum_congr rfl h1, ← Finset.mul_sum, abel_sum' g (Pb m) m, Pb_one, Pb_succ_self hm]
  ring

private theorem Pb_sum1 {m : ℕ} (hm : 1 ≤ m) :
    ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1) = m := by
  have h := Pb_moment hm (fun _ => (1 : ℝ))
  simp only [one_mul, sub_self, zero_mul, Finset.sum_const_zero, zero_add, mul_one] at h
  exact h

private theorem Pb_sum2 {m : ℕ} (hm : 1 ≤ m) :
    ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * Pb m (i + 1) = m * sbirth m := by
  have h := Pb_moment hm (fun j => (j : ℝ))
  have e1 : ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * Pb m (i + 1)
      = ∑ i ∈ range m, ((i + 1 : ℕ) : ℝ) * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  have e2 : ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) - (i : ℝ)) * Pb m (i + 1)
      = ∑ i ∈ range m, Pb m (i + 1) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  rw [e1, h, e2, ← sbirth_eq_range, Nat.cast_zero, add_zero]

private theorem Pb_sum_quad {m : ℕ} (hm : 1 ≤ m) (c2 c1 c0 : ℝ) :
    ∑ i ∈ range m, (c2 * ((i : ℝ) + 1) ^ 2 + c1 * ((i : ℝ) + 1) + c0) * Pb m (i + 1)
      = c2 * (m * sbirth m) + c1 * m + c0 * sbirth m := by
  have e : ∑ i ∈ range m, (c2 * ((i : ℝ) + 1) ^ 2 + c1 * ((i : ℝ) + 1) + c0) * Pb m (i + 1)
      = c2 * ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * Pb m (i + 1)
        + c1 * ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1)
        + c0 * ∑ i ∈ range m, Pb m (i + 1) := by
    rw [Finset.mul_sum, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib,
      ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl (fun i _ => by ring)
  rw [e, Pb_sum2 hm, Pb_sum1 hm, ← sbirth_eq_range]

/-- The second factorial moment of the birthday law in terms of its mean: $\sum_{q=1}^{m}
q^2(q-1)\,P_{m,q} = 2m\,(m - s_m)$ for $m \ge 1$. -/
theorem Pb_sum3 {m : ℕ} (hm : 1 ≤ m) :
    ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * Pb m (i + 1) = 2 * m * (m - sbirth m) := by
  have h := Pb_moment hm (fun j => (j : ℝ) * ((j : ℝ) - 1))
  have e1 : ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * Pb m (i + 1)
      = ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) * (((i + 1 : ℕ) : ℝ) - 1))
          * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  have e2 : ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) * (((i + 1 : ℕ) : ℝ) - 1)
        - (i : ℝ) * ((i : ℝ) - 1)) * Pb m (i + 1)
      = ∑ i ∈ range m, (0 * ((i : ℝ) + 1) ^ 2 + 2 * ((i : ℝ) + 1) + (-2)) * Pb m (i + 1) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  rw [e1, h, e2, Pb_sum_quad hm, Nat.cast_zero]
  ring

/-- The third factorial moment of the birthday law in terms of its mean: $\sum_{q=1}^{m}
q^2(q-1)(q-2)\,P_{m,q} = 3m\,((m+2)\,s_m - 3m)$ for $m \ge 1$. -/
theorem Pb_sum4 {m : ℕ} (hm : 1 ≤ m) :
    ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * ((i : ℝ) - 1) * Pb m (i + 1)
      = 3 * m * (((m : ℝ) + 2) * sbirth m - 3 * m) := by
  have h := Pb_moment hm (fun j => (j : ℝ) * ((j : ℝ) - 1) * ((j : ℝ) - 2))
  have e1 : ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * ((i : ℝ) - 1) * Pb m (i + 1)
      = ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) * (((i + 1 : ℕ) : ℝ) - 1) * (((i + 1 : ℕ) : ℝ) - 2))
          * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  have e2 : ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) * (((i + 1 : ℕ) : ℝ) - 1) * (((i + 1 : ℕ) : ℝ) - 2)
        - (i : ℝ) * ((i : ℝ) - 1) * ((i : ℝ) - 2)) * Pb m (i + 1)
      = ∑ i ∈ range m, (3 * ((i : ℝ) + 1) ^ 2 + (-9) * ((i : ℝ) + 1) + 6) * Pb m (i + 1) :=
    Finset.sum_congr rfl (fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring)
  rw [e1, h, e2, Pb_sum_quad hm, Nat.cast_zero]
  ring

/-- `s_m² + s_m ≤ 2m` (the variance of the number of parts is nonnegative). -/
private theorem sbirth_sq_le {m : ℕ} (hm : 1 ≤ m) : sbirth m ^ 2 + sbirth m ≤ 2 * m := by
  have hm' : (0 : ℝ) < m := Nat.cast_pos.2 (by omega)
  have hvar : 0 ≤ ∑ i ∈ range m,
      ((i : ℝ) + 1 - sbirth m) ^ 2 * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_nonneg fun i _ =>
      mul_nonneg (sq_nonneg _) (mul_nonneg (by positivity) (Pb_nonneg m _))
  have e : ∑ i ∈ range m, ((i : ℝ) + 1 - sbirth m) ^ 2 * (((i : ℝ) + 1) * Pb m (i + 1))
      = ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * Pb m (i + 1)
        + (1 - 2 * sbirth m) * ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * Pb m (i + 1)
        + sbirth m ^ 2 * ∑ i ∈ range m, ((i : ℝ) + 1) * Pb m (i + 1) := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl (fun i _ => by ring)
  rw [e, Pb_sum3 hm, Pb_sum2 hm, Pb_sum1 hm] at hvar
  have h : (m : ℝ) * (sbirth m ^ 2 + sbirth m) ≤ m * (2 * m) := by linarith [hvar]
  exact le_of_mul_le_mul_left h hm'

/-! ### The mean `s_m` and the ratio `D_m` -/

/-- The mean of the birthday law of $m \ge 1$ is at least $1$: $s_m \ge 1$. -/
theorem one_le_sbirth {m : ℕ} (hm : 1 ≤ m) : 1 ≤ sbirth m := by
  have h : Pb m 1 ≤ ∑ j ∈ Icc 1 m, Pb m j :=
    Finset.single_le_sum (fun j _ => Pb_nonneg m j) (mem_Icc.2 ⟨le_refl 1, hm⟩)
  rw [Pb_one] at h
  exact h

/-- The mean of the birthday law of $m \ge 2$ is less than $m$: $s_m < m$. -/
theorem sbirth_lt {m : ℕ} (hm : 2 ≤ m) : sbirth m < m := by
  have hm' : (0 : ℝ) < m := Nat.cast_pos.2 (by omega)
  have h2 : Pb m (1 + 1) < 1 := by
    rw [Pb_succ, Pb_one, one_mul, Nat.cast_one]
    have : 0 < (1 : ℝ) / m := div_pos one_pos hm'
    linarith
  have h : ∑ j ∈ Icc 1 m, Pb m j < ∑ j ∈ Icc 1 m, (1 : ℝ) :=
    Finset.sum_lt_sum (fun j _ => Pb_le_one m j) ⟨1 + 1, mem_Icc.2 ⟨by omega, by omega⟩, h2⟩
  have hc : ∑ j ∈ Icc 1 m, (1 : ℝ) = m := by simp
  rw [hc] at h
  exact h

/-- The moment ratio of the birthday law is bounded by its mean: $D_m \le \frac32\,(s_m - 1)$ for $m
\ge 2$. -/
theorem Dbirth_le {m : ℕ} (hm : 2 ≤ m) : Dbirth m ≤ 3 / 2 * (sbirth m - 1) := by
  have hD : (0 : ℝ) < 2 * ((m : ℝ) - sbirth m) := by
    have := sbirth_lt hm
    linarith
  have hs := sbirth_sq_le (by omega : 1 ≤ m)
  unfold Dbirth
  rw [div_le_iff₀ hD]
  nlinarith [hs]

end Parking
