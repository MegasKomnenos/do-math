module

public import Parking.LeftHalf.FirstLayer.PropertyK
public import Mathlib.Analysis.SpecialFunctions.Arcosh

/-!
# Property K is preserved by a truncated self-convolution

`conv f j = ∑_{a ≤ j} f a f (j-a)`.  The main result is `conv_TK`: if `f` is positive on
`[0, n+2]`, `f (n+1) = f (n+2)` is its minimum on `[0, n+1]`, `n + 2 ≤ k`, and `f` satisfies the
tilted convexity

  `2 e^{μ/k} f (j+1) ≤ e^μ f (j+2) + e^{-μ} f j`   (`j ≤ n`, all `μ ≥ 0`),

then `(conv f n, conv f (n+1), conv f (n+2))` has property K at `k`.

The proof starts from the decomposition (`conv_decomp`)

  `A conv f (n+2) + B conv f n - D conv f (n+1)`
  `  = ∑_{j ≤ n} f (n-j) (A f (j+2) + B f j - D f (j+1)) + f (n+1) (A f 1 - D f 0) + A f (n+2) f 0`,

in which the tilted convexity of `f` makes every term of the sum nonnegative, while the boundary
term `f (n+1) (A f 1 - D f 0)` may be negative.  Two lower bounds for the sum pay for it:

* `conv_M` replaces `f (n-j)` by its minimum `f (n+1)`; it suffices when `cosh μ ≥ e^{μ/k}`;
* `conv_Q` compares the tilted sequence `F a = e^{μ a} f a` with the solution `g` of the three-term
  recurrence `g (y+1) + g (y-1) = 2 cosh ν · g y` through its two top values (a discrete maximum
  principle; `g` is written in closed form with `sinh`); it is used when `cosh μ < e^{μ/k}`, with
  `cosh ν = e^{μ/k}`, and leaves a bracket whose sign is settled by `Qsign`.
-/

@[expose] public section

namespace Parking.FirstLayer
open Real Finset

/-- Self-convolution `conv f j = ∑_{a=0}^{j} f a f (j-a)`. -/
noncomputable def conv (f : ℕ → ℝ) (j : ℕ) : ℝ := ∑ a ∈ range (j + 1), f a * f (j - a)

private theorem conv_succ (f : ℕ → ℝ) (n : ℕ) :
    conv f (n + 1) = ∑ a ∈ range (n + 1), f a * f (n + 1 - a) + f (n + 1) * f 0 := by
  unfold conv
  rw [Finset.sum_range_succ, Nat.sub_self]

private theorem conv_succ_succ (f : ℕ → ℝ) (n : ℕ) :
    conv f (n + 2) =
      ∑ a ∈ range (n + 1), f a * f (n + 2 - a) + f (n + 1) * f 1 + f (n + 2) * f 0 := by
  unfold conv
  rw [Finset.sum_range_succ, Finset.sum_range_succ]
  have e1 : n + 2 - (n + 1) = 1 := by omega
  rw [e1, Nat.sub_self]

private theorem conv_reflect (f : ℕ → ℝ) (n c : ℕ) :
    ∑ a ∈ range (n + 1), f a * f (n + c - a) = ∑ j ∈ range (n + 1), f (n - j) * f (j + c) := by
  refine (Finset.sum_range_reflect (fun a => f a * f (n + c - a)) (n + 1)).symm.trans ?_
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [Finset.mem_range] at hj
  have e1 : n + 1 - 1 - j = n - j := by omega
  have e2 : n + c - (n - j) = j + c := by omega
  show f (n + 1 - 1 - j) * f (n + c - (n + 1 - 1 - j)) = f (n - j) * f (j + c)
  rw [e1, e2]

/-- The decomposition of a three-term combination of consecutive self-convolutions. -/
private theorem conv_decomp (f : ℕ → ℝ) (A B D : ℝ) (n : ℕ) :
    A * conv f (n + 2) + B * conv f n - D * conv f (n + 1) =
      ∑ j ∈ range (n + 1), f (n - j) * (A * f (j + 2) + B * f j - D * f (j + 1))
        + f (n + 1) * (A * f 1 - D * f 0) + A * (f (n + 2) * f 0) := by
  have h2 := conv_reflect f n 2
  have h1 := conv_reflect f n 1
  have h0 : ∑ a ∈ range (n + 1), f a * f (n - a) = ∑ j ∈ range (n + 1), f (n - j) * f j := by
    have h := conv_reflect f n 0
    simpa using h
  have hsum : ∑ j ∈ range (n + 1), f (n - j) * (A * f (j + 2) + B * f j - D * f (j + 1)) =
      A * ∑ j ∈ range (n + 1), f (n - j) * f (j + 2) + B * ∑ j ∈ range (n + 1), f (n - j) * f j
        - D * ∑ j ∈ range (n + 1), f (n - j) * f (j + 1) := by
    rw [Finset.mul_sum, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib,
      ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun a _ => ?_
    ring
  rw [hsum, ← h2, ← h1, ← h0, conv_succ_succ, conv_succ]
  unfold conv
  ring

/-- Comparison with a constant sequence: in the decomposition `conv_decomp`, `f (n-j)` is replaced
by its minimum `f (n+1)`. -/
private theorem conv_M (f : ℕ → ℝ) (n : ℕ) (lam C : ℝ)
    (hmin : ∀ a, a ≤ n → f (n + 1) ≤ f a) (htop : f (n + 2) = f (n + 1))
    (hs : ∀ j, j ≤ n → 2 * C * f (j + 1) ≤ exp lam * f (j + 2) + exp (-lam) * f j) :
    2 * f (n + 1) * ((cosh lam - C) * ∑ a ∈ range (n + 2), f a + sinh lam * f (n + 1)) ≤
      exp lam * conv f (n + 2) + exp (-lam) * conv f n - 2 * C * conv f (n + 1) := by
  rw [conv_decomp f (exp lam) (exp (-lam)) (2 * C) n]
  have h1 : ∑ j ∈ range (n + 1),
        f (n + 1) * (exp lam * f (j + 2) + exp (-lam) * f j - 2 * C * f (j + 1)) ≤
      ∑ j ∈ range (n + 1),
        f (n - j) * (exp lam * f (j + 2) + exp (-lam) * f j - 2 * C * f (j + 1)) := by
    refine Finset.sum_le_sum fun j hj => ?_
    rw [Finset.mem_range] at hj
    have hsj := hs j (by omega)
    exact mul_le_mul_of_nonneg_right (hmin (n - j) (by omega)) (by linarith)
  have h2 : ∑ j ∈ range (n + 1),
        f (n + 1) * (exp lam * f (j + 2) + exp (-lam) * f j - 2 * C * f (j + 1)) =
      f (n + 1) * (exp lam * ∑ j ∈ range (n + 1), f (j + 2) +
        exp (-lam) * ∑ j ∈ range (n + 1), f j - 2 * C * ∑ j ∈ range (n + 1), f (j + 1)) := by
    rw [← Finset.mul_sum, Finset.sum_sub_distrib, Finset.sum_add_distrib, ← Finset.mul_sum,
      ← Finset.mul_sum, ← Finset.mul_sum]
  have e0 : ∑ a ∈ range (n + 2), f a = ∑ j ∈ range (n + 1), f j + f (n + 1) :=
    Finset.sum_range_succ f (n + 1)
  have e1 : ∑ a ∈ range (n + 2), f a = ∑ j ∈ range (n + 1), f (j + 1) + f 0 :=
    Finset.sum_range_succ' f (n + 1)
  have e2 : ∑ j ∈ range (n + 2), f (j + 1) = ∑ j ∈ range (n + 1), f (j + 2) + f 1 :=
    Finset.sum_range_succ' (fun j => f (j + 1)) (n + 1)
  have e2' : ∑ j ∈ range (n + 2), f (j + 1) = ∑ j ∈ range (n + 1), f (j + 1) + f (n + 2) :=
    Finset.sum_range_succ (fun j => f (j + 1)) (n + 1)
  have hS0 : ∑ j ∈ range (n + 1), f j = ∑ a ∈ range (n + 2), f a - f (n + 1) := by linarith
  have hS1 : ∑ j ∈ range (n + 1), f (j + 1) = ∑ a ∈ range (n + 2), f a - f 0 := by linarith
  have hS2 : ∑ j ∈ range (n + 1), f (j + 2) =
      ∑ a ∈ range (n + 2), f a - f 0 + f (n + 1) - f 1 := by linarith
  rw [hS0, hS1, hS2] at h2
  rw [h2] at h1
  rw [Real.cosh_eq lam, Real.sinh_eq lam, htop]
  linarith

/-! ### The comparison solution -/

/-- The solution of `g (y+1) + g (y-1) = 2 cosh μ · g y` with
`g (n+1) = sinh μ · F (n+1)`, `g (n+2) = sinh μ · F (n+2)`. -/
private noncomputable def gq (F : ℕ → ℝ) (n : ℕ) (μ : ℝ) (y : ℝ) : ℝ :=
  sinh (((n : ℝ) + 2 - y) * μ) * F (n + 1) - F (n + 2) * sinh (((n : ℝ) + 1 - y) * μ)

private theorem gq_rec (F : ℕ → ℝ) (n : ℕ) (μ y : ℝ) :
    gq F n μ (y + 1) + gq F n μ (y - 1) = 2 * cosh μ * gq F n μ y := by
  unfold gq
  have e1 : ((n : ℝ) + 2 - (y + 1)) * μ = ((n : ℝ) + 2 - y) * μ - μ := by ring
  have e2 : ((n : ℝ) + 2 - (y - 1)) * μ = ((n : ℝ) + 2 - y) * μ + μ := by ring
  have e3 : ((n : ℝ) + 1 - (y + 1)) * μ = ((n : ℝ) + 1 - y) * μ - μ := by ring
  have e4 : ((n : ℝ) + 1 - (y - 1)) * μ = ((n : ℝ) + 1 - y) * μ + μ := by ring
  rw [e1, e2, e3, e4, Real.sinh_sub, Real.sinh_add, Real.sinh_sub, Real.sinh_add]
  ring

private theorem gq_top (F : ℕ → ℝ) (n : ℕ) (μ : ℝ) :
    gq F n μ ((n : ℝ) + 1) = sinh μ * F (n + 1) := by
  unfold gq
  have e1 : ((n : ℝ) + 2 - ((n : ℝ) + 1)) * μ = μ := by ring
  have e2 : ((n : ℝ) + 1 - ((n : ℝ) + 1)) * μ = 0 := by ring
  rw [e1, e2, Real.sinh_zero]
  ring

private theorem gq_top' (F : ℕ → ℝ) (n : ℕ) (μ : ℝ) :
    gq F n μ ((n : ℝ) + 2) = sinh μ * F (n + 2) := by
  unfold gq
  have e1 : ((n : ℝ) + 2 - ((n : ℝ) + 2)) * μ = 0 := by ring
  have e2 : ((n : ℝ) + 1 - ((n : ℝ) + 2)) * μ = -μ := by ring
  rw [e1, e2, Real.sinh_zero, Real.sinh_neg]
  ring

/-- Discrete maximum principle: `sinh μ · F - g` is nonnegative and nonincreasing on `[0, n+2]`. -/
private theorem gq_le (F : ℕ → ℝ) (n : ℕ) (μ : ℝ) (hμ : 0 < μ)
    (hS : ∀ j, j ≤ n → 2 * cosh μ * F (j + 1) ≤ F (j + 2) + F j) :
    ∀ d j : ℕ, j + d = n + 1 →
      0 ≤ sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1) ∧
        sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1) ≤ sinh μ * F j - gq F n μ (j : ℝ) := by
  have hs0 : 0 < sinh μ := Real.sinh_pos_iff.mpr hμ
  have hC1 : 1 ≤ cosh μ := Real.one_le_cosh μ
  intro d
  induction d with
  | zero =>
    intro j hj
    have hjn : j = n + 1 := by omega
    subst hjn
    have c1 : ((n + 1 : ℕ) : ℝ) = (n : ℝ) + 1 := by push_cast; ring
    have c2 : (n : ℝ) + 1 + 1 = (n : ℝ) + 2 := by ring
    rw [c1, c2, gq_top', gq_top]
    constructor
    · show 0 ≤ sinh μ * F (n + 1 + 1) - sinh μ * F (n + 2)
      simp
    · show sinh μ * F (n + 1 + 1) - sinh μ * F (n + 2) ≤ sinh μ * F (n + 1) - sinh μ * F (n + 1)
      simp
  | succ d ih =>
    intro j hj
    have hjn : j ≤ n := by omega
    obtain ⟨h1, h2⟩ := ih (j + 1) (by omega)
    have c1 : ((j + 1 : ℕ) : ℝ) = (j : ℝ) + 1 := by push_cast; ring
    rw [c1] at h1 h2
    have hrec := gq_rec F n μ ((j : ℝ) + 1)
    have c0 : (j : ℝ) + 1 - 1 = j := by ring
    rw [c0] at hrec
    have hSj := hS j hjn
    have hSj' := mul_le_mul_of_nonneg_left hSj hs0.le
    -- notation: e2 = e (j+2), e1 = e (j+1), e0 = e j
    have h3 : 0 ≤ sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1) := le_trans h1 h2
    refine ⟨h3, ?_⟩
    -- e0 ≥ 2 C e1 - e2 ≥ 2 e1 - e2 ≥ e1
    have h4 : (sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1)) * 2 ≤
        (sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1)) * (2 * cosh μ) :=
      mul_le_mul_of_nonneg_left (by linarith) h3
    have h5 : (sinh μ * F (j + 1 + 1) - gq F n μ ((j : ℝ) + 1 + 1)) +
        (sinh μ * F j - gq F n μ (j : ℝ)) -
          (sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1)) * (2 * cosh μ) =
        sinh μ * (F (j + 2) + F j) - sinh μ * (2 * cosh μ * F (j + 1)) := by
      have : gq F n μ ((j : ℝ) + 1 + 1) + gq F n μ (j : ℝ) =
          2 * cosh μ * gq F n μ ((j : ℝ) + 1) := hrec
      show (sinh μ * F (j + 2) - gq F n μ ((j : ℝ) + 1 + 1)) +
        (sinh μ * F j - gq F n μ (j : ℝ)) -
          (sinh μ * F (j + 1) - gq F n μ ((j : ℝ) + 1)) * (2 * cosh μ) =
        sinh μ * (F (j + 2) + F j) - sinh μ * (2 * cosh μ * F (j + 1))
      linear_combination (-1 : ℝ) * this
    linarith

/-- Comparison with the solution of the three-term recurrence through the two top values: if
`2 cosh μ · F (j+1) ≤ F (j+2) + F j` for `j ≤ n`, the three-term combination of the
self-convolutions of `F` is bounded below by an explicit expression in `F (n+1)`, `F (n+2)`. -/
private theorem conv_Q (F : ℕ → ℝ) (n : ℕ) (μ : ℝ) (hμ : 0 < μ)
    (hS : ∀ j, j ≤ n → 2 * cosh μ * F (j + 1) ≤ F (j + 2) + F j) :
    2 * F (n + 1) * F (n + 2) * sinh (((n : ℝ) + 2) * μ)
        - F (n + 2) ^ 2 * sinh (((n : ℝ) + 1) * μ) - F (n + 1) ^ 2 * sinh (((n : ℝ) + 3) * μ) ≤
      sinh μ * (conv F (n + 2) + conv F n - 2 * cosh μ * conv F (n + 1)) := by
  have hdec := conv_decomp F 1 1 (2 * cosh μ) n
  rw [one_mul, one_mul] at hdec
  -- the terms of the sum, split into the comparison part and the nonnegative part
  have hterm : ∀ j ∈ range (n + 1),
      sinh μ * (F (n - j) * (1 * F (j + 2) + 1 * F j - 2 * cosh μ * F (j + 1))) =
        (sinh μ * F (n - j) - gq F n μ ((n : ℝ) - j)) *
            (F (j + 2) + F j - 2 * cosh μ * F (j + 1)) +
          ((gq F n μ ((n : ℝ) + 1 - ((j + 1 : ℕ) : ℝ)) * F (j + 1 + 1) -
              gq F n μ ((n : ℝ) - ((j + 1 : ℕ) : ℝ)) * F (j + 1)) -
            (gq F n μ ((n : ℝ) + 1 - (j : ℝ)) * F (j + 1) -
              gq F n μ ((n : ℝ) - (j : ℝ)) * F j)) := by
    intro j _
    have hrec := gq_rec F n μ ((n : ℝ) - j)
    have c1 : (n : ℝ) + 1 - ((j + 1 : ℕ) : ℝ) = (n : ℝ) - j := by push_cast; ring
    have c2 : (n : ℝ) - ((j + 1 : ℕ) : ℝ) = (n : ℝ) - j - 1 := by push_cast; ring
    have c3 : (n : ℝ) + 1 - (j : ℝ) = (n : ℝ) - j + 1 := by ring
    rw [c1, c2, c3]
    linear_combination (F (j + 1)) * hrec
  have hsumeq : sinh μ * ∑ j ∈ range (n + 1),
        F (n - j) * (1 * F (j + 2) + 1 * F j - 2 * cosh μ * F (j + 1)) =
      ∑ j ∈ range (n + 1), (sinh μ * F (n - j) - gq F n μ ((n : ℝ) - j)) *
          (F (j + 2) + F j - 2 * cosh μ * F (j + 1)) +
        ((gq F n μ ((n : ℝ) + 1 - ((n + 1 : ℕ) : ℝ)) * F (n + 1 + 1) -
            gq F n μ ((n : ℝ) - ((n + 1 : ℕ) : ℝ)) * F (n + 1)) -
          (gq F n μ ((n : ℝ) + 1 - ((0 : ℕ) : ℝ)) * F (0 + 1) -
            gq F n μ ((n : ℝ) - ((0 : ℕ) : ℝ)) * F 0)) := by
    rw [Finset.mul_sum, Finset.sum_congr rfl hterm, Finset.sum_add_distrib]
    congr 1
    exact Finset.sum_range_sub
      (fun j : ℕ => gq F n μ ((n : ℝ) + 1 - (j : ℝ)) * F (j + 1) -
        gq F n μ ((n : ℝ) - (j : ℝ)) * F j) (n + 1)
  -- the nonnegative part
  have hnonneg : 0 ≤ ∑ j ∈ range (n + 1), (sinh μ * F (n - j) - gq F n μ ((n : ℝ) - j)) *
      (F (j + 2) + F j - 2 * cosh μ * F (j + 1)) := by
    refine Finset.sum_nonneg fun j hj => ?_
    rw [Finset.mem_range] at hj
    have hjn : j ≤ n := by omega
    have hcast : ((n - j : ℕ) : ℝ) = (n : ℝ) - j := by rw [Nat.cast_sub hjn]
    -- e (n-j) ≥ 0
    have he : 0 ≤ sinh μ * F (n - j) - gq F n μ ((n : ℝ) - j) := by
      obtain ⟨h1, h2⟩ := gq_le F n μ hμ hS (j + 1) (n - j) (by omega)
      rw [hcast] at h1 h2
      exact le_trans h1 h2
    exact mul_nonneg he (by linarith [hS j hjn])
  -- the boundary values of the comparison solution
  have b1 : gq F n μ ((n : ℝ) + 1 - ((0 : ℕ) : ℝ)) = sinh μ * F (n + 1) := by
    have e : (n : ℝ) + 1 - ((0 : ℕ) : ℝ) = (n : ℝ) + 1 := by push_cast; ring
    rw [e, gq_top]
  have b2 : gq F n μ ((n : ℝ) - ((0 : ℕ) : ℝ)) =
      2 * cosh μ * (sinh μ * F (n + 1)) - sinh μ * F (n + 2) := by
    have e : (n : ℝ) - ((0 : ℕ) : ℝ) = (n : ℝ) + 1 - 1 := by push_cast; ring
    have hrec := gq_rec F n μ ((n : ℝ) + 1)
    have e' : (n : ℝ) + 1 + 1 = (n : ℝ) + 2 := by ring
    rw [e', gq_top', gq_top] at hrec
    rw [e]
    linarith
  have b3 : gq F n μ ((n : ℝ) + 1 - ((n + 1 : ℕ) : ℝ)) =
      sinh (((n : ℝ) + 2) * μ) * F (n + 1) - F (n + 2) * sinh (((n : ℝ) + 1) * μ) := by
    have e : (n : ℝ) + 1 - ((n + 1 : ℕ) : ℝ) = 0 := by push_cast; ring
    rw [e]
    unfold gq
    rw [sub_zero, sub_zero]
  have b4 : gq F n μ ((n : ℝ) - ((n + 1 : ℕ) : ℝ)) =
      sinh (((n : ℝ) + 3) * μ) * F (n + 1) - F (n + 2) * sinh (((n : ℝ) + 2) * μ) := by
    have e : (n : ℝ) - ((n + 1 : ℕ) : ℝ) = -1 := by push_cast; ring
    rw [e]
    unfold gq
    have e1 : (n : ℝ) + 2 - -1 = (n : ℝ) + 3 := by ring
    have e2 : (n : ℝ) + 1 - -1 = (n : ℝ) + 2 := by ring
    rw [e1, e2]
  rw [b1, b2, b3, b4] at hsumeq
  have hmul : sinh μ * (conv F (n + 2) + conv F n - 2 * cosh μ * conv F (n + 1)) =
      sinh μ * ∑ j ∈ range (n + 1),
          F (n - j) * (1 * F (j + 2) + 1 * F j - 2 * cosh μ * F (j + 1)) +
        sinh μ * (F (n + 1) * (1 * F 1 - 2 * cosh μ * F 0) + 1 * (F (n + 2) * F 0)) := by
    rw [hdec]
    ring
  rw [hmul, hsumeq]
  have e5 : F (n + 1 + 1) = F (n + 2) := rfl
  have e6 : F (0 + 1) = F 1 := by rw [zero_add]
  rw [e5, e6]
  linarith

/-! ### Elementary inequalities for `sinh` and `cosh` -/

private theorem sinh_le_mul_cosh {y : ℝ} (hy : 0 ≤ y) : sinh y ≤ y * cosh y := by
  rcases hy.eq_or_lt with h0 | hpos
  · rw [← h0]
    simp
  · have hderiv : ∀ t : ℝ, HasDerivAt (fun t : ℝ => t * cosh t - sinh t) (t * sinh t) t := by
      intro t
      have d1 := (hasDerivAt_id' t).fun_mul (Real.hasDerivAt_cosh t)
      have d := d1.fun_sub (Real.hasDerivAt_sinh t)
      refine d.congr_deriv ?_
      show 1 * cosh t + t * sinh t - cosh t = t * sinh t
      ring
    obtain ⟨c, hc, hc'⟩ := exists_hasDerivAt_eq_slope (fun t : ℝ => t * cosh t - sinh t)
      (fun t : ℝ => t * sinh t) hpos (fun x _ => (hderiv x).continuousAt.continuousWithinAt)
      (fun x _ => hderiv x)
    have h1 : 0 ≤ c * sinh c := mul_nonneg hc.1.le (Real.sinh_nonneg_iff.mpr hc.1.le)
    simp only [zero_mul, Real.sinh_zero, sub_zero] at hc'
    rw [hc'] at h1
    have h2 := mul_nonneg h1 hpos.le
    rw [div_mul_cancel₀ _ hpos.ne'] at h2
    linarith

private theorem one_add_sq_div_two_le_cosh (x : ℝ) : 1 + x ^ 2 / 2 ≤ cosh x := by
  have e : 2 * (|x| / 2) = |x| := by ring
  have hs : |x| / 2 ≤ sinh (|x| / 2) := Real.self_le_sinh_iff.mpr (by positivity)
  have hsq : (|x| / 2) ^ 2 ≤ sinh (|x| / 2) ^ 2 := pow_le_pow_left₀ (by positivity) hs 2
  have hx : (|x| / 2) ^ 2 = x ^ 2 / 4 := by
    rw [div_pow, sq_abs]
    norm_num
  have hc : cosh x = cosh (|x| / 2) ^ 2 + sinh (|x| / 2) ^ 2 := by
    rw [← Real.cosh_two_mul, e, Real.cosh_abs]
  rw [hc, Real.cosh_sq]
  linarith

/-- The lower bound of `conv_Q`, for `F (n+2) = e^λ F (n+1)` (`m = n + 1`), is nonnegative when
`cosh μ = e^{λ/k}`, `λ ≤ μ` and `m + 1 ≤ k`. -/
private theorem Qsign {m k : ℕ} (hmk : m + 1 ≤ k) {lam μ : ℝ} (hμ : 0 < μ) (hlμ : lam ≤ μ)
    (hC : cosh μ = exp (lam / k)) :
    0 ≤ 2 * exp lam * sinh (((m : ℝ) + 1) * μ) - exp lam ^ 2 * sinh ((m : ℝ) * μ)
        - sinh (((m : ℝ) + 2) * μ) := by
  have hk0 : (k : ℝ) ≠ 0 := by
    have : (0 : ℝ) < k := by exact_mod_cast (by omega : 0 < k)
    exact this.ne'
  have ha0 : 0 ≤ (m : ℝ) * μ / 2 := by positivity
  have e1 : (m : ℝ) * μ = 2 * ((m : ℝ) * μ / 2) := by ring
  have e2 : ((m : ℝ) + 2) * μ = 2 * ((m : ℝ) * μ / 2 + μ) := by ring
  have e3 : ((m : ℝ) + 1) * μ = (m : ℝ) * μ / 2 + ((m : ℝ) * μ / 2 + μ) := by ring
  rw [e2, e3, Real.sinh_two_mul, Real.sinh_add ((m : ℝ) * μ / 2) ((m : ℝ) * μ / 2 + μ)]
  have e1' : sinh ((m : ℝ) * μ) =
      2 * sinh ((m : ℝ) * μ / 2) * cosh ((m : ℝ) * μ / 2) := by
    rw [← Real.sinh_two_mul, ← e1]
  rw [e1']
  have hsa : 0 ≤ sinh ((m : ℝ) * μ / 2) := Real.sinh_nonneg_iff.mpr ha0
  have hca : 1 ≤ cosh ((m : ℝ) * μ / 2) := Real.one_le_cosh _
  have hsμ : 0 < sinh μ := Real.sinh_pos_iff.mpr hμ
  have hcμ : 1 ≤ cosh μ := Real.one_le_cosh μ
  -- R sinh a ≤ sinh (a + μ)
  have c2 : exp lam * sinh ((m : ℝ) * μ / 2) ≤ sinh ((m : ℝ) * μ / 2 + μ) := by
    have h1 : exp lam ≤ exp μ := Real.exp_le_exp.mpr hlμ
    have h2 : exp μ = cosh μ + sinh μ := (Real.cosh_add_sinh μ).symm
    have h3 : sinh ((m : ℝ) * μ / 2) ≤ cosh ((m : ℝ) * μ / 2) := (Real.sinh_lt_cosh _).le
    have h1' : exp lam * sinh ((m : ℝ) * μ / 2) ≤
        (cosh μ + sinh μ) * sinh ((m : ℝ) * μ / 2) := by
      rw [← h2]
      exact mul_le_mul_of_nonneg_right h1 hsa
    have h3' := mul_le_mul_of_nonneg_right h3 hsμ.le
    rw [Real.sinh_add]
    linarith
  -- cosh (a + μ) ≤ R cosh a
  have c1 : cosh ((m : ℝ) * μ / 2 + μ) ≤ exp lam * cosh ((m : ℝ) * μ / 2) := by
    have h1 : sinh ((m : ℝ) * μ / 2) ≤ (m : ℝ) * μ / 2 * cosh ((m : ℝ) * μ / 2) :=
      sinh_le_mul_cosh ha0
    have h2 : sinh μ ≤ μ * cosh μ := sinh_le_mul_cosh hμ.le
    have h3 : sinh ((m : ℝ) * μ / 2) * sinh μ ≤
        ((m : ℝ) * μ / 2 * cosh ((m : ℝ) * μ / 2)) * (μ * cosh μ) :=
      mul_le_mul h1 h2 hsμ.le (by positivity)
    have h3' : sinh ((m : ℝ) * μ / 2) * sinh μ ≤
        ((m : ℝ) * (μ ^ 2 / 2)) * (cosh ((m : ℝ) * μ / 2) * cosh μ) := by
      have e : ((m : ℝ) * μ / 2 * cosh ((m : ℝ) * μ / 2)) * (μ * cosh μ) =
          ((m : ℝ) * (μ ^ 2 / 2)) * (cosh ((m : ℝ) * μ / 2) * cosh μ) := by ring
      rw [← e]
      exact h3
    have h4 : 1 + (m : ℝ) * (μ ^ 2 / 2) ≤ (1 + μ ^ 2 / 2) ^ m :=
      one_add_mul_le_pow (by have : 0 ≤ μ ^ 2 / 2 := by positivity
                             linarith) m
    have h5 : (1 + μ ^ 2 / 2) ^ m ≤ cosh μ ^ m :=
      pow_le_pow_left₀ (by positivity) (one_add_sq_div_two_le_cosh μ) m
    have h6 : cosh μ ^ (m + 1) ≤ cosh μ ^ k := pow_le_pow_right₀ hcμ hmk
    have h7 : cosh μ ^ k = exp lam := by
      rw [hC, ← Real.exp_nat_mul]
      congr 1
      field_simp
    have hcc : 0 ≤ cosh ((m : ℝ) * μ / 2) * cosh μ := by positivity
    have h9 : cosh ((m : ℝ) * μ / 2) * cosh μ * (1 + (m : ℝ) * (μ ^ 2 / 2)) ≤
        cosh ((m : ℝ) * μ / 2) * cosh μ * cosh μ ^ m :=
      mul_le_mul_of_nonneg_left (le_trans h4 h5) hcc
    have h10 : cosh ((m : ℝ) * μ / 2) * cosh μ ^ (m + 1) ≤
        cosh ((m : ℝ) * μ / 2) * cosh μ ^ k :=
      mul_le_mul_of_nonneg_left h6 (by positivity)
    rw [h7] at h10
    have h11 : cosh ((m : ℝ) * μ / 2) * cosh μ * cosh μ ^ m =
        cosh ((m : ℝ) * μ / 2) * cosh μ ^ (m + 1) := by
      rw [pow_succ]
      ring
    rw [Real.cosh_add]
    linarith
  have hprod : 0 ≤ 2 * (sinh ((m : ℝ) * μ / 2 + μ) - exp lam * sinh ((m : ℝ) * μ / 2)) *
      (exp lam * cosh ((m : ℝ) * μ / 2) - cosh ((m : ℝ) * μ / 2 + μ)) :=
    mul_nonneg (mul_nonneg zero_le_two (by linarith)) (by linarith)
  linarith

/-! ### Tilting a convolution -/

private theorem conv_tilt (f : ℕ → ℝ) (lam : ℝ) (j : ℕ) :
    conv (fun a => exp (lam * a) * f a) j = exp (lam * j) * conv f j := by
  unfold conv
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun a ha => ?_
  rw [Finset.mem_range] at ha
  have e : exp (lam * (j : ℝ)) = exp (lam * (a : ℝ)) * exp (lam * ((j - a : ℕ) : ℝ)) := by
    rw [← exp_add, ← mul_add]
    congr 2
    rw [Nat.cast_sub (by omega)]
    ring
  show exp (lam * (a : ℝ)) * f a * (exp (lam * ((j - a : ℕ) : ℝ)) * f (j - a)) =
    exp (lam * (j : ℝ)) * (f a * f (j - a))
  rw [e]
  ring

/-- **Tilted convexity is preserved by the truncated self-convolution.** -/
theorem conv_TK {k : ℕ} (n : ℕ) (hnk : n + 2 ≤ k) (f : ℕ → ℝ)
    (hpos : ∀ a, a ≤ n + 2 → 0 < f a) (hmin : ∀ a, a ≤ n → f (n + 1) ≤ f a)
    (htop : f (n + 2) = f (n + 1))
    (hs : ∀ μ : ℝ, 0 ≤ μ → ∀ j, j ≤ n →
      2 * exp (μ / k) * f (j + 1) ≤ exp μ * f (j + 2) + exp (-μ) * f j) :
    TK k (conv f n) (conv f (n + 1)) (conv f (n + 2)) := by
  intro lam hlam
  have hk0 : (0 : ℝ) < k := by exact_mod_cast (by omega : 0 < k)
  by_cases hcase : exp (lam / k) ≤ cosh lam
  · -- `cosh λ ≥ e^{λ/k}`: comparison with a constant sequence
    have hM := conv_M f n lam (exp (lam / k)) hmin htop
      (fun j hj => by have := hs lam hlam j hj; linarith)
    have hf := (hpos (n + 1) (by omega)).le
    have hsum : 0 ≤ ∑ a ∈ range (n + 2), f a :=
      Finset.sum_nonneg fun a ha => (hpos a (by rw [Finset.mem_range] at ha; omega)).le
    have hsh : 0 ≤ sinh lam := Real.sinh_nonneg_iff.mpr hlam
    have hc : 0 ≤ cosh lam - exp (lam / k) := by linarith
    have h1 : 0 ≤ 2 * f (n + 1) *
        ((cosh lam - exp (lam / k)) * ∑ a ∈ range (n + 2), f a + sinh lam * f (n + 1)) := by
      positivity
    linarith
  · -- `cosh λ < e^{λ/k}`: comparison with the three-term recurrence, `cosh μ = e^{λ/k}`
    rw [not_le] at hcase
    have hlam0 : 0 < lam := by
      rcases hlam.eq_or_lt with h0 | h
      · exfalso
        rw [← h0] at hcase
        simp at hcase
      · exact h
    have hC1 : 1 < exp (lam / k) := Real.one_lt_exp_iff.mpr (div_pos hlam0 hk0)
    have hμC : cosh (Real.arcosh (exp (lam / k))) = exp (lam / k) := Real.cosh_arcosh hC1.le
    have hμ : 0 < Real.arcosh (exp (lam / k)) := Real.arcosh_pos hC1
    have hlμ : lam ≤ Real.arcosh (exp (lam / k)) := by
      have h1 : cosh lam < cosh (Real.arcosh (exp (lam / k))) := by
        rw [hμC]
        exact hcase
      have h2 := Real.cosh_lt_cosh.mp h1
      rw [abs_of_nonneg hlam, abs_of_pos hμ] at h2
      exact h2.le
    generalize Real.arcosh (exp (lam / k)) = μ at hμC hμ hlμ
    -- the tilted sequence satisfies the three-term inequality
    have hS' : ∀ j, j ≤ n →
        2 * cosh μ * ((fun a : ℕ => exp (lam * a) * f a) (j + 1)) ≤
          (fun a : ℕ => exp (lam * a) * f a) (j + 2) + (fun a : ℕ => exp (lam * a) * f a) j := by
      intro j hj
      have h := hs lam hlam j hj
      have hE : 0 ≤ exp (lam * ((j : ℝ) + 1)) := (exp_pos _).le
      have h' := mul_le_mul_of_nonneg_left h hE
      have a1 : exp (lam * ((j + 1 : ℕ) : ℝ)) = exp (lam * ((j : ℝ) + 1)) := by
        congr 1
        push_cast
        ring
      have a2 : exp (lam * ((j + 2 : ℕ) : ℝ)) = exp (lam * ((j : ℝ) + 1)) * exp lam := by
        rw [← exp_add]
        congr 1
        push_cast
        ring
      have a0 : exp (lam * (j : ℝ)) = exp (lam * ((j : ℝ) + 1)) * exp (-lam) := by
        rw [← exp_add]
        congr 1
        ring
      show 2 * cosh μ * (exp (lam * ((j + 1 : ℕ) : ℝ)) * f (j + 1)) ≤
        exp (lam * ((j + 2 : ℕ) : ℝ)) * f (j + 2) + exp (lam * (j : ℝ)) * f j
      rw [a1, a2, a0, hμC]
      linarith
    have hQ := conv_Q (fun a : ℕ => exp (lam * a) * f a) n μ hμ hS'
    simp only [conv_tilt] at hQ
    have hE2 : exp (lam * ((n + 2 : ℕ) : ℝ)) = exp (lam * ((n : ℝ) + 1)) * exp lam := by
      rw [← exp_add]
      congr 1
      push_cast
      ring
    have hE0 : exp (lam * (n : ℝ)) = exp (lam * ((n : ℝ) + 1)) * exp (-lam) := by
      rw [← exp_add]
      congr 1
      ring
    have hE1 : exp (lam * ((n + 1 : ℕ) : ℝ)) = exp (lam * ((n : ℝ) + 1)) := by
      congr 1
      push_cast
      ring
    rw [hE2, hE0, hE1, htop, hμC] at hQ
    have hQs := Qsign (m := n + 1) (k := k) (by omega) hμ hlμ hμC
    have c1 : ((n + 1 : ℕ) : ℝ) + 1 = (n : ℝ) + 2 := by push_cast; ring
    have c3 : ((n + 1 : ℕ) : ℝ) + 2 = (n : ℝ) + 3 := by push_cast; ring
    have c2 : ((n + 1 : ℕ) : ℝ) = (n : ℝ) + 1 := by push_cast; ring
    rw [c1, c3, c2] at hQs
    have hEpos : 0 < exp (lam * ((n : ℝ) + 1)) := exp_pos _
    have hsμ : 0 < sinh μ := Real.sinh_pos_iff.mpr hμ
    have hL : 0 ≤ (exp (lam * ((n : ℝ) + 1)) * f (n + 1)) ^ 2 *
        (2 * exp lam * sinh (((n : ℝ) + 2) * μ) - exp lam ^ 2 * sinh (((n : ℝ) + 1) * μ)
          - sinh (((n : ℝ) + 3) * μ)) := mul_nonneg (sq_nonneg _) hQs
    have hfinal : (sinh μ * exp (lam * ((n : ℝ) + 1))) * 0 ≤
        (sinh μ * exp (lam * ((n : ℝ) + 1))) *
          (exp lam * conv f (n + 2) + exp (-lam) * conv f n
            - 2 * exp (lam / k) * conv f (n + 1)) := by
      rw [mul_zero]
      linarith
    have h0 := le_of_mul_le_mul_left hfinal (mul_pos hsμ hEpos)
    linarith

end Parking.FirstLayer