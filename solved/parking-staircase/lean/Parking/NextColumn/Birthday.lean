import Parking.NextColumn.Erasure

/-!
# The birthday law on compositions: `T_{m,q}`, and `D_m` as a ratio of moments

* `lr_sum_le`    : weighted Chebyshev inequality for two weights in likelihood-ratio order, and its
  consequence `lr_factorial_moment_le` for the ratio of the third to the second factorial moment.
* `Tq_eq`        : `T_{m,q} = a_m · q · (m)_q/m^q`, so that the number of parts of a composition of
  `m` with weight `∏ a_part` follows the size-biased birthday law.
* `Dbirth_spec`, `Dbirth_nonneg`, `Dbirth_mono` : `D_m` is the ratio of the third to the second
  factorial moment of the number of parts, is nonnegative and nondecreasing in `m`.

The facts about the birthday law that do not involve compositions are in
`Parking.NextColumn.BirthdayLaw`.
-/

namespace Parking

open Finset

/-! ### General summation lemmas -/

/-- Weighted Chebyshev inequality on an arbitrary finite set of natural numbers. -/
theorem lr_sum_le_finset (s : Finset ℕ) (u v φ : ℕ → ℝ)
    (hlr : ∀ q ∈ s, ∀ q' ∈ s, q ≤ q' → u q' * v q ≤ u q * v q')
    (hφ : ∀ q ∈ s, ∀ q' ∈ s, q ≤ q' → φ q ≤ φ q') :
    (∑ q ∈ s, u q * φ q) * (∑ q ∈ s, v q) ≤ (∑ q ∈ s, v q * φ q) * (∑ q ∈ s, u q) := by
  have key : ∀ q ∈ s, ∀ q' ∈ s, (u q * v q' - u q' * v q) * (φ q - φ q') ≤ 0 := by
    intro q hq q' hq'
    rcases le_total q q' with h | h
    · exact mul_nonpos_of_nonneg_of_nonpos (sub_nonneg.2 (hlr q hq q' hq' h))
        (sub_nonpos.2 (hφ q hq q' hq' h))
    · exact mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.2 (hlr q' hq' q hq h))
        (sub_nonneg.2 (hφ q' hq' q hq h))
  have hS : (∑ q ∈ s, u q * φ q) * (∑ q ∈ s, v q) - (∑ q ∈ s, v q * φ q) * (∑ q ∈ s, u q)
      = ∑ q ∈ s, ∑ q' ∈ s, u q * v q' * (φ q - φ q') := by
    rw [mul_comm (∑ q ∈ s, v q * φ q) (∑ q ∈ s, u q), Finset.sum_mul_sum, Finset.sum_mul_sum,
      ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun q _ => ?_
    rw [← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun q' _ => ?_
    ring
  have hS' : ∑ q ∈ s, ∑ q' ∈ s, u q * v q' * (φ q - φ q')
      = ∑ q ∈ s, ∑ q' ∈ s, u q' * v q * (φ q' - φ q) := Finset.sum_comm
  have h2S : (∑ q ∈ s, ∑ q' ∈ s, u q * v q' * (φ q - φ q'))
      + (∑ q ∈ s, ∑ q' ∈ s, u q' * v q * (φ q' - φ q))
      = ∑ q ∈ s, ∑ q' ∈ s, (u q * v q' - u q' * v q) * (φ q - φ q') := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun q _ => ?_
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun q' _ => ?_
    ring
  have hle : ∑ q ∈ s, ∑ q' ∈ s, (u q * v q' - u q' * v q) * (φ q - φ q') ≤ 0 :=
    Finset.sum_nonpos fun q hq => Finset.sum_nonpos fun q' hq' => key q hq q' hq'
  linarith

/-- Weighted Chebyshev inequality: if `u/v` is nonincreasing (cross-multiplied form) and `φ` is
nondecreasing on `[1,n]`, then `(∑ u φ)(∑ v) ≤ (∑ v φ)(∑ u)`. -/
theorem lr_sum_le (n : ℕ) (u v φ : ℕ → ℝ)
    (hlr : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ n → u q' * v q ≤ u q * v q')
    (hφ : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ n → φ q ≤ φ q') :
    (∑ q ∈ Icc 1 n, u q * φ q) * (∑ q ∈ Icc 1 n, v q)
      ≤ (∑ q ∈ Icc 1 n, v q * φ q) * (∑ q ∈ Icc 1 n, u q) :=
  lr_sum_le_finset (Icc 1 n) u v φ
    (fun q hq q' hq' h => hlr q q' (mem_Icc.1 hq).1 h (mem_Icc.1 hq').2)
    (fun q hq q' hq' h => hφ q q' (mem_Icc.1 hq).1 h (mem_Icc.1 hq').2)

/-- From consecutive ratios to the cross-multiplied likelihood-ratio condition. -/
theorem lr_of_consecutive (n : ℕ) (u v : ℕ → ℝ) (hv : ∀ q ∈ Icc 1 n, 0 < v q)
    (h : ∀ q, 1 ≤ q → q + 1 ≤ n → u (q + 1) * v q ≤ u q * v (q + 1)) :
    ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ n → u q' * v q ≤ u q * v q' := by
  intro q q' hq hqq'
  induction q', hqq' using Nat.le_induction with
  | base => intro _; exact le_refl _
  | succ k hk ih =>
    intro hkn
    have ih' := ih (by omega)
    have hc := h k (by omega) hkn
    have hvk : 0 < v k := hv k (mem_Icc.2 ⟨by omega, by omega⟩)
    have hvq : 0 < v q := hv q (mem_Icc.2 ⟨hq, by omega⟩)
    have hvk1 : 0 < v (k + 1) := hv (k + 1) (mem_Icc.2 ⟨by omega, hkn⟩)
    have h1 : u (k + 1) * v k * v q ≤ u k * v (k + 1) * v q :=
      mul_le_mul_of_nonneg_right hc hvq.le
    have h2 : u k * v q * v (k + 1) ≤ u q * v k * v (k + 1) :=
      mul_le_mul_of_nonneg_right ih' hvk1.le
    have h3 : (u (k + 1) * v q) * v k ≤ (u q * v (k + 1)) * v k := by nlinarith [h1, h2]
    exact le_of_mul_le_mul_right h3 hvk

/-- Two weights in likelihood-ratio order on `[1,n]` have ordered ratios of the third to the second
factorial moment (cross-multiplied):
`(∑ q(q-1)(q-2) u_q)(∑ q(q-1) v_q) ≤ (∑ q(q-1)(q-2) v_q)(∑ q(q-1) u_q)`. -/
theorem lr_factorial_moment_le (n : ℕ) (u v : ℕ → ℝ)
    (hlr : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ n → u q' * v q ≤ u q * v q') :
    (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * u q)
        * (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * v q)
      ≤ (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * v q)
        * (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * u q) := by
  have key : (∑ q ∈ Icc 1 n, ((q : ℝ) * ((q : ℝ) - 1) * u q) * ((q : ℝ) - 2))
        * (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * v q)
      ≤ (∑ q ∈ Icc 1 n, ((q : ℝ) * ((q : ℝ) - 1) * v q) * ((q : ℝ) - 2))
        * (∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * u q) := by
    refine lr_sum_le n (fun q => (q : ℝ) * ((q : ℝ) - 1) * u q)
      (fun q => (q : ℝ) * ((q : ℝ) - 1) * v q) (fun q => (q : ℝ) - 2) ?_ ?_
    · intro q q' hq hqq' hq'n
      have h := hlr q q' hq hqq' hq'n
      have hq1 : (1 : ℝ) ≤ (q : ℝ) := by exact_mod_cast hq
      have hq'1 : (1 : ℝ) ≤ (q' : ℝ) := by exact_mod_cast (le_trans hq hqq')
      have hw : 0 ≤ (q : ℝ) * ((q : ℝ) - 1) * ((q' : ℝ) * ((q' : ℝ) - 1)) :=
        mul_nonneg (mul_nonneg (by linarith) (by linarith))
          (mul_nonneg (by linarith) (by linarith))
      calc (q' : ℝ) * ((q' : ℝ) - 1) * u q' * ((q : ℝ) * ((q : ℝ) - 1) * v q)
          = ((q : ℝ) * ((q : ℝ) - 1) * ((q' : ℝ) * ((q' : ℝ) - 1))) * (u q' * v q) := by ring
        _ ≤ ((q : ℝ) * ((q : ℝ) - 1) * ((q' : ℝ) * ((q' : ℝ) - 1))) * (u q * v q') :=
            mul_le_mul_of_nonneg_left h hw
        _ = (q : ℝ) * ((q : ℝ) - 1) * u q * ((q' : ℝ) * ((q' : ℝ) - 1) * v q') := by ring
    · intro q q' _ hqq' _
      have h : (q : ℝ) ≤ (q' : ℝ) := by exact_mod_cast hqq'
      show (q : ℝ) - 2 ≤ (q' : ℝ) - 2
      linarith
  have e : ∀ w : ℕ → ℝ, ∑ q ∈ Icc 1 n, ((q : ℝ) * ((q : ℝ) - 1) * w q) * ((q : ℝ) - 2)
      = ∑ q ∈ Icc 1 n, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * w q :=
    fun w => Finset.sum_congr rfl (fun q _ => by ring)
  rw [e u, e v] at key
  exact key

/-! ### The numbers `T_{m,q}` -/

/-- The compositions of $m$ with exactly $q \ge 1$ parts, each part of size $p$ weighted by $a_p =
p^{p-1}/p!$, have the total weight $T_{m,q} = a_m\, q\, P_{m,q}$, where $P_{m,q} = \prod_{i<q}(1
- i/m)$ is the birthday tail. -/
theorem Tq_eq {m q : ℕ} (hq : 1 ≤ q) : Tq m q = cay m * q * Pb m q := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · have h0 : Tq 0 q = 0 := Vc_eq_zero_of_lt _ (by omega)
    rw [h0, cay_zero, zero_mul, zero_mul]
  · induction q, hq using Nat.le_induction with
    | base =>
      have h1 : Tq m 1 = cay m := Vc_one _ m
      rw [h1, Pb_one, Nat.cast_one, mul_one, mul_one]
    | succ k hk ih =>
      have hr := Tq_ratio m hk
      rw [ih] at hr
      have hm' : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
      have hk' : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.2 (by omega)
      have hd : (k : ℝ) / m * m = k := div_mul_cancel₀ _ hm'
      have hgoal : (k : ℝ) * m * Tq m (k + 1)
          = (k : ℝ) * m * (cay m * ((k + 1 : ℕ) : ℝ) * Pb m (k + 1)) := by
        rw [hr, Pb_succ, Nat.cast_add, Nat.cast_one]
        linear_combination ((k : ℝ) * cay m * ((k : ℝ) + 1) * Pb m k) * hd
      exact mul_left_cancel₀ (mul_ne_zero hk' hm') hgoal

/-- The total weight $T_{m,q}$ of the compositions of $m$ with $q$ parts is positive for $1 \le q
\le m$. -/
theorem Tq_pos {m q : ℕ} (hq : 1 ≤ q) (hqm : q ≤ m) : 0 < Tq m q :=
  Vc_pos (fun _ _ => one_pos) hq hqm

/-- The total weight $T_{m,q}$ of the compositions of $m$ with $q$ parts is nonnegative for all $m$
and $q$. -/
theorem Tq_nonneg (m q : ℕ) : 0 ≤ Tq m q := by
  show 0 ≤ Vc (fun _ => (1 : ℝ)) q m
  exact Vc_nonneg (fun _ _ => zero_le_one) q

/-- The total weight $\tau_m(h)$ of the compositions of $m \ge 1$ with constant cut weight $h \ge 0$
is positive. -/
theorem tau_pos {m : ℕ} (hm : 1 ≤ m) {h : ℝ} (hh : 0 ≤ h) : 0 < tau m h := by
  rw [tau_eq]
  have h1 : (1 : ℕ) ∈ Icc 1 m := mem_Icc.2 ⟨le_refl 1, hm⟩
  have hnn : ∀ q ∈ Icc 1 m, 0 ≤ Tq m q * h ^ (q - 1) := fun q _ =>
    mul_nonneg (Tq_nonneg m q) (pow_nonneg hh _)
  have hle : Tq m 1 * h ^ (1 - 1) ≤ ∑ q ∈ Icc 1 m, Tq m q * h ^ (q - 1) :=
    Finset.single_le_sum hnn h1
  have hpos : 0 < Tq m 1 * h ^ (1 - 1) := by
    rw [Nat.sub_self, pow_zero, mul_one]
    exact Tq_pos (le_refl 1) hm
  linarith

/-- The mean number of cuts times the total weight: $\mu_r(h)\,\tau_r(h) =
\sum_{q=1}^{r}(q-1)\,T_{r,q}\,h^{q-1}$ for $r \ge 1$ and $h \ge 0$. -/
theorem muh_mul_tau {r : ℕ} (hr : 1 ≤ r) {h : ℝ} (hh : 0 ≤ h) :
    muh r h * tau r h = ∑ q ∈ Icc 1 r, ((q : ℝ) - 1) * (Tq r q * h ^ (q - 1)) := by
  unfold muh
  exact div_mul_cancel₀ _ (tau_pos hr hh).ne'

/-- The mean number of cuts $\mu_r(h)$ of the compositions of $r \ge 1$ with constant cut weight $h
\ge 0$ is nonnegative. -/
theorem muh_nonneg {r : ℕ} (hr : 1 ≤ r) {h : ℝ} (hh : 0 ≤ h) : 0 ≤ muh r h := by
  unfold muh
  refine div_nonneg (Finset.sum_nonneg fun q hq => ?_) (tau_pos hr hh).le
  rw [mem_Icc] at hq
  have h1 : (1 : ℝ) ≤ q := by exact_mod_cast hq.1
  exact mul_nonneg (by linarith) (mul_nonneg (Tq_nonneg r q) (pow_nonneg hh _))

/-- Polynomially weighted sums of `T_{m,q}` in terms of the birthday law. -/
private theorem sum_Tq_poly {m : ℕ} (G : ℝ → ℝ) :
    ∑ q ∈ Icc 1 m, G q * Tq m q
      = cay m * ∑ i ∈ range m, G ((i : ℝ) + 1) * (((i : ℝ) + 1) * Pb m (i + 1)) := by
  rw [sum_Icc_one_eq_range, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Tq_eq (by omega : 1 ≤ i + 1), Nat.cast_add, Nat.cast_one]
  ring

private theorem sum_qq_Tq {m : ℕ} (hm : 1 ≤ m) :
    ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q = cay m * (2 * m * (m - sbirth m)) := by
  have h : ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q
      = cay m * ∑ i ∈ range m, ((i : ℝ) + 1) * (((i : ℝ) + 1) - 1)
          * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    sum_Tq_poly (fun x => x * (x - 1))
  rw [h, ← Pb_sum3 hm]
  congr 1
  exact Finset.sum_congr rfl (fun i _ => by ring)

private theorem sum_qqq_Tq {m : ℕ} (hm : 1 ≤ m) :
    ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q
      = cay m * (3 * m * (((m : ℝ) + 2) * sbirth m - 3 * m)) := by
  have h : ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q
      = cay m * ∑ i ∈ range m, ((i : ℝ) + 1) * (((i : ℝ) + 1) - 1) * (((i : ℝ) + 1) - 2)
          * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    sum_Tq_poly (fun x => x * (x - 1) * (x - 2))
  rw [h, ← Pb_sum4 hm]
  congr 1
  exact Finset.sum_congr rfl (fun i _ => by ring)

private theorem Dbirth_mul {m : ℕ} (hm : 2 ≤ m) :
    Dbirth m * (2 * ((m : ℝ) - sbirth m)) = 3 * (((m : ℝ) + 2) * sbirth m - 3 * m) := by
  have hs : (2 : ℝ) * ((m : ℝ) - sbirth m) ≠ 0 := by
    have h1 := sbirth_lt hm
    have h2 : (0 : ℝ) < 2 * ((m : ℝ) - sbirth m) := by linarith
    exact h2.ne'
  unfold Dbirth
  exact div_mul_cancel₀ _ hs

/-- `D_m` is the ratio of the third to the second factorial moment of the number of parts. -/
theorem Dbirth_spec {m : ℕ} (hm : 2 ≤ m) :
    ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q
      = Dbirth m * ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q := by
  rw [sum_qqq_Tq (by omega), sum_qq_Tq (by omega)]
  have hD := Dbirth_mul hm
  linear_combination (-(cay m * (m : ℝ))) * hD

/-- For $m \ge 2$ the sum $\sum_{q=1}^{m} q(q-1)\,T_{m,q}$ over the weights of the compositions of
$m$ with $q$ parts is positive. -/
theorem sum_qq_Tq_pos {m : ℕ} (hm : 2 ≤ m) :
    0 < ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q := by
  rw [sum_qq_Tq (by omega)]
  have hm' : (0 : ℝ) < m := Nat.cast_pos.2 (by omega)
  have hs := sbirth_lt hm
  exact mul_pos (cay_pos (by omega)) (mul_pos (mul_pos two_pos hm') (sub_pos.2 hs))

/-- The moment ratio of the birthday law is nonnegative: $D_m \ge 0$ for $m \ge 2$. -/
theorem Dbirth_nonneg {m : ℕ} (hm : 2 ≤ m) : 0 ≤ Dbirth m := by
  have h3 : 0 ≤ ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q := by
    refine Finset.sum_nonneg fun q hq => ?_
    rw [mem_Icc] at hq
    refine mul_nonneg ?_ (Tq_nonneg m q)
    rcases Nat.lt_or_ge q 2 with h | h
    · have hq1 : q = 1 := by omega
      rw [hq1]
      norm_num
    · have h2 : (2 : ℝ) ≤ q := by exact_mod_cast h
      have h4 : (0 : ℝ) ≤ (q : ℝ) * ((q : ℝ) - 1) := mul_nonneg (by linarith) (by linarith)
      exact mul_nonneg h4 (by linarith)
  rw [Dbirth_spec hm] at h3
  refine le_of_mul_le_mul_right ?_ (sum_qq_Tq_pos hm)
  rw [zero_mul]
  exact h3

private theorem Dbirth_succ {m : ℕ} (hm : 2 ≤ m) : Dbirth m ≤ Dbirth (m + 1) := by
  -- the numbers of parts for `m` and for `m + 1` are in likelihood-ratio order
  have hlr : ∀ q q', 1 ≤ q → q ≤ q' → q' ≤ m + 1 →
      Tq m q' * Tq (m + 1) q ≤ Tq m q * Tq (m + 1) q' := by
    intro q q' hq hqq' hq'
    have hq1 : 1 ≤ q' := le_trans hq hqq'
    rw [Tq_eq (m := m) hq, Tq_eq (m := m) hq1, Tq_eq (m := m + 1) hq, Tq_eq (m := m + 1) hq1]
    have hK : 0 ≤ cay m * cay (m + 1) * ((q : ℝ) * q') :=
      mul_nonneg (mul_nonneg (cay_nonneg m) (cay_nonneg (m + 1)))
        (mul_nonneg (Nat.cast_nonneg q) (Nat.cast_nonneg q'))
    have h5 := mul_le_mul_of_nonneg_left (Pb_lr m hqq' hq') hK
    linarith [h5]
  have hmain := lr_factorial_moment_le (m + 1) (Tq m) (Tq (m + 1)) hlr
  -- `T_{m,m+1} = 0`, so the sums for `m` stop at `m`
  have hTz : Tq m (m + 1) = 0 := Vc_eq_zero_of_lt _ (Nat.lt_succ_self m)
  have e1 : ∑ q ∈ Icc 1 (m + 1), (q : ℝ) * ((q : ℝ) - 1) * ((q : ℝ) - 2) * Tq m q
      = Dbirth m * ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q := by
    rw [Finset.sum_Icc_succ_top (by omega), hTz, ← Dbirth_spec hm, mul_zero, add_zero]
  have e2 : ∑ q ∈ Icc 1 (m + 1), (q : ℝ) * ((q : ℝ) - 1) * Tq m q
      = ∑ q ∈ Icc 1 m, (q : ℝ) * ((q : ℝ) - 1) * Tq m q := by
    rw [Finset.sum_Icc_succ_top (by omega), hTz, mul_zero, add_zero]
  rw [e1, e2, Dbirth_spec (by omega : 2 ≤ m + 1)] at hmain
  have hS1 := sum_qq_Tq_pos hm
  have hS2 := sum_qq_Tq_pos (by omega : 2 ≤ m + 1)
  refine le_of_mul_le_mul_right ?_ (mul_pos hS1 hS2)
  linarith [hmain]

/-- The moment ratio of the birthday law does not decrease: $D_m \le D_r$ for $2 \le m \le r$. -/
theorem Dbirth_mono {m r : ℕ} (hm : 2 ≤ m) (hmr : m ≤ r) : Dbirth m ≤ Dbirth r := by
  induction r, hmr using Nat.le_induction with
  | base => exact le_refl _
  | succ k hk ih => exact le_trans ih (Dbirth_succ (by omega))

end Parking
