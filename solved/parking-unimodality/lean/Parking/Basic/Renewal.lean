import Parking.Basic.Sums
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.LinearCombination

/-!
# Renewal sequences

`u` is the renewal sequence of the kernel `f` when `u 0 = 1` and
`u n = ∑_{i=1}^{n} f i * u (n - i)` for `n ≥ 1`.

* `IsRenewal f u` : `u` is the renewal sequence of `f`.
* `renewal_pos` : a positive kernel has a positive renewal sequence.
* `ratio_mono_of_logConvex`, `logConvex_cross` : in a positive log-convex sequence the ratios of
  consecutive terms are nondecreasing; both statements are cross-multiplied, so that no division
  occurs.
* `renewal_logConvex` : a positive log-convex kernel has a log-convex renewal sequence
  (de Bruijn–Erdős 1953, Theorem 1).
* `resolvent` : if `v s = ι s + ∑_{i=1}^{s} f i * v (s - i)` for all `s`, then `v` is the
  convolution of the renewal sequence of `f` with `ι`.
-/

namespace Parking
open Finset

/-- `u` is the renewal sequence of the kernel `f` (only `f 1, f 2, …` matter). -/
def IsRenewal (f u : ℕ → ℝ) : Prop :=
  u 0 = 1 ∧ ∀ n : ℕ, 1 ≤ n → u n = ∑ i ∈ Icc 1 n, f i * u (n - i)

/-- The renewal equation at `n + 1`, written as a sum over the antidiagonal of `n`
(no truncated subtraction). -/
private theorem IsRenewal.succ_eq {f u : ℕ → ℝ} (hu : IsRenewal f u) (n : ℕ) :
    u (n + 1) = ∑ p ∈ antidiagonal n, f (p.1 + 1) * u p.2 := by
  have h := Finset.Nat.sum_antidiagonal_eq_sum_range_succ (fun i j => f (i + 1) * u j) n
  rw [hu.2 (n + 1) (by omega), sum_Icc_one_eq_range, h]
  exact sum_congr rfl fun k _ => by rw [Nat.add_sub_add_right]

/-! ### Positivity -/

/-- The renewal sequence of a kernel with positive terms $f_1,f_2,\dots$ is positive. -/
theorem renewal_pos {f u : ℕ → ℝ} (hf : ∀ i, 1 ≤ i → 0 < f i) (hu : IsRenewal f u) (n : ℕ) :
    0 < u n := by
  induction n using Nat.strongRecOn with
  | _ n ih =>
    rcases n with _ | n
    · rw [hu.1]
      exact zero_lt_one
    · rw [hu.succ_eq n]
      refine sum_pos (fun p hp => ?_) ⟨(0, n), mem_antidiagonal.mpr (Nat.zero_add n)⟩
      have hp' : p.1 + p.2 = n := mem_antidiagonal.mp hp
      exact mul_pos (hf (p.1 + 1) (by omega)) (ih p.2 (by omega))

/-! ### Positive log-convex sequences -/

/-- If `a` is positive and `a (j + 1) ^ 2 ≤ a j * a (j + 2)` for `j < N`, then the ratios
`a (k + 1) / a k` are nondecreasing for `k ≤ N`; in cross-multiplied form,
`a (i + 1) * a k ≤ a i * a (k + 1)` for `i ≤ k ≤ N`. -/
private theorem ratio_mono_of_logConvex {a : ℕ → ℝ} {N : ℕ} (hpos : ∀ i, 0 < a i)
    (hlc : ∀ j, j < N → a (j + 1) ^ 2 ≤ a j * a (j + 2)) {i k : ℕ} (hik : i ≤ k) (hk : k ≤ N) :
    a (i + 1) * a k ≤ a i * a (k + 1) := by
  induction k, hik using Nat.le_induction with
  | base => exact (mul_comm _ _).le
  | succ k hik ih =>
    refine le_of_mul_le_mul_left ?_ (hpos k)
    calc a k * (a (i + 1) * a (k + 1))
        = a (i + 1) * a k * a (k + 1) := by ring
      _ ≤ a i * a (k + 1) * a (k + 1) :=
          mul_le_mul_of_nonneg_right (ih (by omega)) (hpos (k + 1)).le
      _ = a i * a (k + 1) ^ 2 := by ring
      _ ≤ a i * (a k * a (k + 2)) := mul_le_mul_of_nonneg_left (hlc k (by omega)) (hpos i).le
      _ = a k * (a i * a (k + 2)) := by ring

/-- Cross-ratio form of log-convexity: in a positive log-convex sequence,
`G (a + c) * G b ≤ G a * G (b + c)` for `a ≤ b`. -/
theorem logConvex_cross {G : ℕ → ℝ} (hpos : ∀ n, 0 < G n)
    (hLC : ∀ n, G (n + 1) ^ 2 ≤ G n * G (n + 2)) {a b : ℕ} (hab : a ≤ b) (c : ℕ) :
    G (a + c) * G b ≤ G a * G (b + c) := by
  induction c with
  | zero => exact le_rfl
  | succ c ih =>
    have h1 : G (a + c + 1) * G (b + c) ≤ G (a + c) * G (b + c + 1) :=
      ratio_mono_of_logConvex (N := b + c) hpos (fun j _ => hLC j) (Nat.add_le_add_right hab c)
        le_rfl
    refine le_of_mul_le_mul_left ?_ (hpos (b + c))
    calc G (b + c) * (G (a + c + 1) * G b)
        = G (a + c + 1) * G (b + c) * G b := by ring
      _ ≤ G (a + c) * G (b + c + 1) * G b := mul_le_mul_of_nonneg_right h1 (hpos b).le
      _ = G (a + c) * G b * G (b + c + 1) := by ring
      _ ≤ G a * G (b + c) * G (b + c + 1) := mul_le_mul_of_nonneg_right ih (hpos (b + c + 1)).le
      _ = G (b + c) * (G a * G (b + c + 1)) := by ring

/-! ### Log-convexity of the renewal sequence -/

/-- **de Bruijn–Erdős.**  The renewal sequence of a positive log-convex kernel is
log-convex.

With `S = ∑_{i+j=M} (f (M+3) f (i+1) - f (M+2) f (i+2)) (u (M+2) u j - u (M+1) u (j+1))`, the
ratio monotonicity of `f` and of `u` (the latter up to the index reached by the induction) makes
every summand nonnegative, and the renewal equations at `M + 1`, `M + 2` and `M + 3` give
`S = f (M+2) (u (M+1) u (M+3) - u (M+2)²)`. -/
theorem renewal_logConvex {f u : ℕ → ℝ} (hf : ∀ i, 1 ≤ i → 0 < f i)
    (hlc : ∀ j, f (j + 2) ^ 2 ≤ f (j + 1) * f (j + 3)) (hu : IsRenewal f u) (n : ℕ) :
    u (n + 1) ^ 2 ≤ u n * u (n + 2) := by
  have hupos : ∀ n, 0 < u n := renewal_pos hf hu
  induction n using Nat.strongRecOn with
  | _ n ih =>
    rcases n with _ | M
    · -- `u 1 = f 1` and `u 2 = f 1 ^ 2 + f 2`
      have h1 : u 1 = f 1 * u 0 := by
        have h := hu.2 1 le_rfl
        rw [Icc_self, sum_singleton] at h
        exact h
      have h2 : u 2 = f 1 * u 1 + f 2 * u 0 := by
        have h := hu.2 2 (by omega)
        rw [sum_Icc_succ_top (show 1 ≤ 1 + 1 by omega), Icc_self, sum_singleton] at h
        exact h
      show u 1 ^ 2 ≤ u 0 * u 2
      rw [h2, h1, hu.1]
      linarith [hf 2 (by omega)]
    · show u (M + 2) ^ 2 ≤ u (M + 1) * u (M + 3)
      -- ratio monotonicity of the kernel, and of `u` up to the index `M + 1`
      have hfr : ∀ i, i ≤ M + 1 → f (i + 2) * f (M + 2) ≤ f (i + 1) * f (M + 3) := fun i hi =>
        ratio_mono_of_logConvex (a := fun x => f (x + 1)) (N := M + 1)
          (fun x => hf (x + 1) (by omega)) (fun j _ => hlc j) hi le_rfl
      have hur : ∀ j, j ≤ M + 1 → u (j + 1) * u (M + 1) ≤ u j * u (M + 2) := fun j hj =>
        ratio_mono_of_logConvex hupos ih hj le_rfl
      -- the renewal equations at `M + 1`, `M + 2` (two ways) and `M + 3`
      have hS1 : u (M + 1) = ∑ p ∈ antidiagonal M, f (p.1 + 1) * u p.2 := hu.succ_eq M
      have hS2 : u (M + 2) = f (M + 2) * u 0
          + ∑ p ∈ antidiagonal M, f (p.1 + 1) * u (p.2 + 1) :=
        (hu.succ_eq (M + 1)).trans
          (Finset.Nat.sum_antidiagonal_succ' (n := M) (f := fun p => f (p.1 + 1) * u p.2))
      have hS3 : u (M + 2) = f 1 * u (M + 1)
          + ∑ p ∈ antidiagonal M, f (p.1 + 2) * u p.2 :=
        (hu.succ_eq (M + 1)).trans
          (Finset.Nat.sum_antidiagonal_succ (n := M) (f := fun p => f (p.1 + 1) * u p.2))
      have hS4 : u (M + 3) = f 1 * u (M + 2)
          + (f (M + 3) * u 0 + ∑ p ∈ antidiagonal M, f (p.1 + 2) * u (p.2 + 1)) := by
        have h1 : u (M + 3) = f 1 * u (M + 2)
            + ∑ p ∈ antidiagonal (M + 1), f (p.1 + 2) * u p.2 :=
          (hu.succ_eq (M + 2)).trans
            (Finset.Nat.sum_antidiagonal_succ (n := M + 1) (f := fun p => f (p.1 + 1) * u p.2))
        have h2 : ∑ p ∈ antidiagonal (M + 1), f (p.1 + 2) * u p.2
            = f (M + 3) * u 0 + ∑ p ∈ antidiagonal M, f (p.1 + 2) * u (p.2 + 1) :=
          Finset.Nat.sum_antidiagonal_succ' (n := M) (f := fun p => f (p.1 + 2) * u p.2)
        rw [h1, h2]
      -- every summand of the de Bruijn–Erdős sum is nonnegative
      have hT : 0 ≤ ∑ p ∈ antidiagonal M,
          (f (M + 3) * f (p.1 + 1) - f (M + 2) * f (p.1 + 2))
            * (u (M + 2) * u p.2 - u (M + 1) * u (p.2 + 1)) := by
        refine sum_nonneg fun p hp => ?_
        have hp' : p.1 + p.2 = M := mem_antidiagonal.mp hp
        have hA := hfr p.1 (by omega)
        have hB := hur p.2 (by omega)
        exact mul_nonneg (by linarith) (by linarith)
      -- the sum, expanded and evaluated with the renewal equations
      have hexp : ∑ p ∈ antidiagonal M,
          (f (M + 3) * f (p.1 + 1) - f (M + 2) * f (p.1 + 2))
            * (u (M + 2) * u p.2 - u (M + 1) * u (p.2 + 1))
          = f (M + 3) * u (M + 2) * (∑ p ∈ antidiagonal M, f (p.1 + 1) * u p.2)
            - f (M + 3) * u (M + 1) * (∑ p ∈ antidiagonal M, f (p.1 + 1) * u (p.2 + 1))
            - f (M + 2) * u (M + 2) * (∑ p ∈ antidiagonal M, f (p.1 + 2) * u p.2)
            + f (M + 2) * u (M + 1)
              * (∑ p ∈ antidiagonal M, f (p.1 + 2) * u (p.2 + 1)) := by
        rw [mul_sum, mul_sum, mul_sum, mul_sum, ← sum_sub_distrib, ← sum_sub_distrib,
          ← sum_add_distrib]
        exact sum_congr rfl fun p _ => by ring
      have hid : ∑ p ∈ antidiagonal M,
          (f (M + 3) * f (p.1 + 1) - f (M + 2) * f (p.1 + 2))
            * (u (M + 2) * u p.2 - u (M + 1) * u (p.2 + 1))
          = f (M + 2) * (u (M + 1) * u (M + 3) - u (M + 2) ^ 2) := by
        rw [hexp]
        linear_combination (-(f (M + 3) * u (M + 2))) * hS1 + (f (M + 3) * u (M + 1)) * hS2
          + (f (M + 2) * u (M + 2)) * hS3 - (f (M + 2) * u (M + 1)) * hS4
      rw [hid] at hT
      have h := (mul_nonneg_iff_of_pos_left (hf (M + 2) (by omega))).mp hT
      linarith

/-! ### The resolvent representation -/

/-- **Resolvent representation.**  If `G` is the renewal sequence of `f` and
`v s = ι s + ∑_{i=1}^{s} f i * v (s - i)` for all `s`, then `v` is the convolution of `G` and
`ι`.  (Strong induction on `s` and one exchange of a triangular double sum.) -/
theorem resolvent {f G v ι : ℕ → ℝ} (hG : IsRenewal f G)
    (hι : ∀ s, v s = ι s + ∑ i ∈ Icc 1 s, f i * v (s - i)) (s : ℕ) :
    v s = ∑ c ∈ range (s + 1), G (s - c) * ι c := by
  induction s using Nat.strong_induction_on with
  | _ s ih =>
    have h1 : ∑ i ∈ Icc 1 s, f i * v (s - i)
        = ∑ i ∈ Icc 1 s, ∑ c ∈ range (s - i + 1), f i * (G (s - i - c) * ι c) := by
      refine sum_congr rfl fun i hi => ?_
      rw [mem_Icc] at hi
      rw [ih (s - i) (by omega), mul_sum]
    have h2 : ∑ i ∈ Icc 1 s, ∑ c ∈ range (s - i + 1), f i * (G (s - i - c) * ι c)
        = ∑ c ∈ range s, ∑ i ∈ Icc 1 (s - c), f i * (G (s - i - c) * ι c) := by
      refine sum_comm' fun i c => ?_
      simp only [mem_Icc, mem_range]
      omega
    have h3 : ∑ c ∈ range s, ∑ i ∈ Icc 1 (s - c), f i * (G (s - i - c) * ι c)
        = ∑ c ∈ range s, G (s - c) * ι c := by
      refine sum_congr rfl fun c hc => ?_
      rw [mem_range] at hc
      rw [hG.2 (s - c) (by omega), sum_mul]
      refine sum_congr rfl fun i _ => ?_
      rw [show s - i - c = s - c - i by omega]
      ring
    have h4 : ∑ c ∈ range (s + 1), G (s - c) * ι c
        = ∑ c ∈ range s, G (s - c) * ι c + ι s := by
      rw [sum_range_succ, Nat.sub_self, hG.1, one_mul]
    have h5 := hι s
    linarith

end Parking