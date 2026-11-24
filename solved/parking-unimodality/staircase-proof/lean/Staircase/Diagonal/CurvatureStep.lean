import Staircase.Cayley.CurvatureSum
import Staircase.Diagonal.Profiles

/-!
# The curvature sum along the diagonal

For a threshold `y` and a size `N` the chain sum `Λ_m(y;N) = Lam (thr y N) m` is the total weight
of the compositions of `m` for the profile `s ↦ y/(N-s)`.  The curvature term of a step
`d(n,k)`, `N = n + 1`, is built from the second differences in the threshold of `y · Λ_m(y;N)`,
the curvature sums (`curvSum`, `Staircase/Cayley/CurvatureSum.lean`),

`curvSum y N m = (y+1) Λ_m(y+1;N) - 2 y Λ_m(y;N) + (y-1) Λ_m(y-1;N)`.

Since `y · Λ_m(y;N) = ∑_Q y^Q V_{m,Q}` with `V_{m,Q} = Vc (thr 1 N) Q m`, this is
`∑_Q ((y+1)^Q - 2y^Q + (y-1)^Q) V_{m,Q}` (`curvSum_eq_sum`): the term `Q = 1` vanishes, and for
`y > 0` and `N ≥ m` the others are nonnegative and the term `Q = 2`, present when `m ≥ 2`, is
positive (`curvSum_pos`).

The main result is the step along the diagonal, from `(y, N) = (k, k+q)` to `(k+1, k+q+1)`:

`curvSum (k+1) (k+q+1) m ≤ k/(k+1) · exp(μ (q - m/2) / (k (k+1))) · curvSum k (k+q) m`,
`μ = (1 + 1/400)(D_m + 1)`   (`curvSum_step`),

for `2 ≤ m < q` and `401 m² ≤ 12 k²`, where `D_m = Dbirth m` is the ratio of the third to the second
factorial moment of the number of parts.

The proof writes `(y+1)^Q - 2y^Q + (y-1)^Q = y^(Q-2) · s_Q(1/y)` with a normalised second
difference `s_Q(x) = ((1+x)^Q + (1-x)^Q - 2)/x²`, so that
`curvSum y N m = y⁻¹ ∑_Q s_Q(1/y) · Vc (thr y N) Q m`.  The numbers `s_Q(x)` increase with `x`, so
on the left `s_Q(1/(k+1))` may be replaced by `s_Q(1/k)`, and the claim becomes a comparison of the
two profiles `P'(s) = (k+1)/(k+q+1-s)` and `P(s) = k/(k+q-s)` under the same weights
`v_Q = s_Q(1/k)`.  That is `Vc_sum_pow_le`: `P'^(k+1) ≤ P^k` by Bernoulli's inequality,
`P'(s) P'(m-s) ≥ ρ²` with `ρ = (k+1)/(k+1+q-m/2)`, and the mean of `Q - 1` under the weights
`v_Q T_{m,Q}` is at most `μ`, because `Q(Q-1) ≤ s_Q(1/k) ≤ (1 + 1/400) Q(Q-1)` for `Q ≤ m`.
-/

namespace Parking

open Finset

/-! ### The second difference of `y ↦ y^Q` -/

/-- The pair `(s_n, d_n)` with `(1+x)^n + (1-x)^n - 2 = x² s_n` and `(1+x)^n - (1-x)^n = x d_n`,
defined by the recursion `s_{n+1} = s_n + d_n`, `d_{n+1} = d_n + x² s_n + 2`. -/
private noncomputable def sdPair (x : ℝ) : ℕ → ℝ × ℝ
  | 0 => (0, 0)
  | n + 1 => ((sdPair x n).1 + (sdPair x n).2, (sdPair x n).2 + x ^ 2 * (sdPair x n).1 + 2)

private theorem sdPair_zero (x : ℝ) : sdPair x 0 = (0, 0) := by
  simp only [sdPair]

private theorem sdPair_succ (x : ℝ) (n : ℕ) :
    sdPair x (n + 1)
      = ((sdPair x n).1 + (sdPair x n).2, (sdPair x n).2 + x ^ 2 * (sdPair x n).1 + 2) := by
  simp only [sdPair]

private theorem sdPair_spec (x : ℝ) : ∀ n : ℕ,
    (1 + x) ^ n + (1 - x) ^ n - 2 = x ^ 2 * (sdPair x n).1
      ∧ (1 + x) ^ n - (1 - x) ^ n = x * (sdPair x n).2
  | 0 => by
    rw [sdPair_zero]
    constructor <;> norm_num
  | n + 1 => by
    obtain ⟨h1, h2⟩ := sdPair_spec x n
    rw [sdPair_succ, pow_succ, pow_succ]
    constructor
    · linear_combination h1 + x * h2
    · linear_combination h2 + x * h1

private theorem sdPair_nonneg (x : ℝ) : ∀ n : ℕ, 0 ≤ (sdPair x n).1 ∧ 0 ≤ (sdPair x n).2
  | 0 => by
    rw [sdPair_zero]
    exact ⟨le_rfl, le_rfl⟩
  | n + 1 => by
    obtain ⟨h1, h2⟩ := sdPair_nonneg x n
    rw [sdPair_succ]
    exact ⟨add_nonneg h1 h2, by positivity⟩

/-- Both sequences increase with `x ≥ 0`. -/
private theorem sdPair_mono {x x' : ℝ} (hx : 0 ≤ x) (hxx : x ≤ x') : ∀ n : ℕ,
    (sdPair x n).1 ≤ (sdPair x' n).1 ∧ (sdPair x n).2 ≤ (sdPair x' n).2
  | 0 => by
    rw [sdPair_zero, sdPair_zero]
    exact ⟨le_rfl, le_rfl⟩
  | n + 1 => by
    obtain ⟨h1, h2⟩ := sdPair_mono hx hxx n
    rw [sdPair_succ, sdPair_succ]
    refine ⟨add_le_add h1 h2, ?_⟩
    have h3 : x ^ 2 * (sdPair x n).1 ≤ x' ^ 2 * (sdPair x' n).1 :=
      mul_le_mul (pow_le_pow_left₀ hx hxx 2) h1 (sdPair_nonneg x n).1 (sq_nonneg x')
    show (sdPair x n).2 + x ^ 2 * (sdPair x n).1 + 2
      ≤ (sdPair x' n).2 + x' ^ 2 * (sdPair x' n).1 + 2
    linarith

/-- The values at `x = 0` are lower bounds: `n(n-1) ≤ s_n` and `2n ≤ d_n`. -/
private theorem sdPair_lower (x : ℝ) : ∀ n : ℕ,
    (n : ℝ) * ((n : ℝ) - 1) ≤ (sdPair x n).1 ∧ 2 * (n : ℝ) ≤ (sdPair x n).2
  | 0 => by
    rw [sdPair_zero]
    constructor <;> norm_num
  | n + 1 => by
    obtain ⟨h1, h2⟩ := sdPair_lower x n
    have h3 : 0 ≤ x ^ 2 * (sdPair x n).1 := mul_nonneg (sq_nonneg x) (sdPair_nonneg x n).1
    rw [sdPair_succ]
    constructor
    · show ((n + 1 : ℕ) : ℝ) * (((n + 1 : ℕ) : ℝ) - 1) ≤ (sdPair x n).1 + (sdPair x n).2
      push_cast
      nlinarith
    · show 2 * ((n + 1 : ℕ) : ℝ) ≤ (sdPair x n).2 + x ^ 2 * (sdPair x n).1 + 2
      push_cast
      linarith

/-- If `s ≤ n(n-1) + x²(1+θ) n(n-1)(n-2)(n-3)/12` with `n ≤ m` and `x² (1+θ) m² ≤ 12 θ`, then
`s ≤ (1+θ) n(n-1)`: the factor `(n-2)(n-3)` is at most `m²` whenever `n(n-1) ≠ 0`. -/
private theorem le_of_quartic {x θ s : ℝ} {m n : ℕ} (hθ : 0 ≤ θ)
    (hx : x ^ 2 * (1 + θ) * (m : ℝ) ^ 2 ≤ 12 * θ) (hn : n ≤ m)
    (h1 : s ≤ (n : ℝ) * ((n : ℝ) - 1)
        + x ^ 2 * (1 + θ) * ((n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2) * ((n : ℝ) - 3)) / 12) :
    s ≤ (1 + θ) * ((n : ℝ) * ((n : ℝ) - 1)) := by
  have hnm : (n : ℝ) ≤ m := by exact_mod_cast hn
  have hc : 0 ≤ x ^ 2 * (1 + θ) := mul_nonneg (sq_nonneg x) (by linarith)
  have hnn : 0 ≤ (n : ℝ) * ((n : ℝ) - 1) ∧ (n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2) * ((n : ℝ) - 3)
      ≤ (n : ℝ) * ((n : ℝ) - 1) * (m : ℝ) ^ 2 := by
    rcases Nat.lt_or_ge n 2 with h2 | h2
    · obtain rfl | rfl : n = 0 ∨ n = 1 := by omega
      · norm_num
      · norm_num
    · have hn2 : (2 : ℝ) ≤ n := by exact_mod_cast h2
      have hA : 0 ≤ (n : ℝ) * ((n : ℝ) - 1) := mul_nonneg (by linarith) (by linarith)
      have hB : ((n : ℝ) - 2) * ((n : ℝ) - 3) ≤ (m : ℝ) ^ 2 := by nlinarith
      exact ⟨hA, by rw [mul_assoc]; exact mul_le_mul_of_nonneg_left hB hA⟩
  have e1 := mul_le_mul_of_nonneg_left hnn.2 hc
  have e3 : (x ^ 2 * (1 + θ) * (m : ℝ) ^ 2) * ((n : ℝ) * ((n : ℝ) - 1))
      ≤ (12 * θ) * ((n : ℝ) * ((n : ℝ) - 1)) := mul_le_mul_of_nonneg_right hx hnn.1
  linarith

/-- The Taylor bounds of second and third order: for `n ≤ m` and `x² (1+θ) m² ≤ 12 θ`,
`s_n ≤ n(n-1) + x²(1+θ) n(n-1)(n-2)(n-3)/12` and `d_n ≤ 2n + x²(1+θ) n(n-1)(n-2)/3`. -/
private theorem sdPair_upper_aux {x θ : ℝ} {m : ℕ} (hθ : 0 ≤ θ)
    (hx : x ^ 2 * (1 + θ) * (m : ℝ) ^ 2 ≤ 12 * θ) : ∀ n : ℕ, n ≤ m →
    (sdPair x n).1 ≤ (n : ℝ) * ((n : ℝ) - 1)
        + x ^ 2 * (1 + θ) * ((n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2) * ((n : ℝ) - 3)) / 12
      ∧ (sdPair x n).2 ≤ 2 * (n : ℝ)
        + x ^ 2 * (1 + θ) * ((n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2)) / 3
  | 0, _ => by
    rw [sdPair_zero]
    constructor <;> norm_num
  | n + 1, hn => by
    obtain ⟨h1, h2⟩ := sdPair_upper_aux hθ hx n (by omega)
    have h3 : x ^ 2 * (sdPair x n).1 ≤ x ^ 2 * ((1 + θ) * ((n : ℝ) * ((n : ℝ) - 1))) :=
      mul_le_mul_of_nonneg_left (le_of_quartic hθ hx (by omega : n ≤ m) h1) (sq_nonneg x)
    rw [sdPair_succ]
    constructor
    · show (sdPair x n).1 + (sdPair x n).2 ≤ ((n + 1 : ℕ) : ℝ) * (((n + 1 : ℕ) : ℝ) - 1)
          + x ^ 2 * (1 + θ) * (((n + 1 : ℕ) : ℝ) * (((n + 1 : ℕ) : ℝ) - 1)
            * (((n + 1 : ℕ) : ℝ) - 2) * (((n + 1 : ℕ) : ℝ) - 3)) / 12
      push_cast
      linear_combination h1 + h2
    · show (sdPair x n).2 + x ^ 2 * (sdPair x n).1 + 2 ≤ 2 * ((n + 1 : ℕ) : ℝ)
          + x ^ 2 * (1 + θ) * (((n + 1 : ℕ) : ℝ) * (((n + 1 : ℕ) : ℝ) - 1)
            * (((n + 1 : ℕ) : ℝ) - 2)) / 3
      push_cast
      linear_combination h2 + h3

/-- For `n ≤ m` and `x² (1+θ) m² ≤ 12 θ`: `s_n ≤ (1+θ) n(n-1)`. -/
private theorem sdPair_upper {x θ : ℝ} {m : ℕ} (hθ : 0 ≤ θ)
    (hx : x ^ 2 * (1 + θ) * (m : ℝ) ^ 2 ≤ 12 * θ) {n : ℕ} (hn : n ≤ m) :
    (sdPair x n).1 ≤ (1 + θ) * ((n : ℝ) * ((n : ℝ) - 1)) :=
  le_of_quartic hθ hx hn (sdPair_upper_aux hθ hx n hn).1

/-- `(y+1)^Q - 2y^Q + (y-1)^Q = y^Q · (1/y)² · s_Q(1/y)`. -/
private theorem pow_second_diff {y : ℝ} (hy : y ≠ 0) (Q : ℕ) :
    (y + 1) ^ Q - 2 * y ^ Q + (y - 1) ^ Q = y ^ Q * ((1 / y) ^ 2 * (sdPair (1 / y) Q).1) := by
  have a1 : (1 : ℝ) + 1 / y = (y + 1) / y := by field_simp
  have a2 : (1 : ℝ) - 1 / y = (y - 1) / y := by field_simp
  have hyQ : y ^ Q ≠ 0 := pow_ne_zero Q hy
  rw [← (sdPair_spec (1 / y) Q).1, a1, a2, div_pow, div_pow]
  field_simp
  ring

/-! ### The curvature sum -/

/-- The curvature sum in terms of the profile `thr y N` itself:
`curvSum y N m = y⁻¹ ∑_Q s_Q(1/y) · Vc (thr y N) Q m`. -/
private theorem curvSum_eq_inv {y : ℝ} (hy : y ≠ 0) (N : ℝ) (m : ℕ) :
    curvSum y N m = y⁻¹ * ∑ Q ∈ Icc 1 m, (sdPair (1 / y) Q).1 * Vc (thr y N) Q m := by
  rw [curvSum_eq_sum, Finset.mul_sum]
  refine Finset.sum_congr rfl fun Q hQ => ?_
  have e2 : y ^ Q = y * y ^ (Q - 1) := by
    rw [← pow_succ', Nat.sub_add_cancel (mem_Icc.mp hQ).1]
  have h1 : y * (1 / y) ^ 2 = y⁻¹ := by field_simp
  rw [pow_second_diff hy, Vc_thr y N Q m, e2]
  linear_combination (y ^ (Q - 1) * (sdPair (1 / y) Q).1 * Vc (thr 1 N) Q m) * h1

/-- For `m = 1` the curvature sum vanishes: `y · Λ_1(y;N) = y` is linear in `y`. -/
theorem curvSum_one (y N : ℝ) : curvSum y N 1 = 0 := by
  rw [curvSum_eq_sum, Finset.Icc_self, Finset.sum_singleton]
  ring

/-- For `m ≥ 2`, `y > 0` and `N ≥ m` the curvature sum is positive: every term of its expansion by
the number of parts is nonnegative, and the term of two parts is positive. -/
theorem curvSum_pos {y N : ℝ} {m : ℕ} (hy : 0 < y) (hm : 2 ≤ m) (hN : (m : ℝ) ≤ N) :
    0 < curvSum y N m := by
  have hthr : ∀ s ∈ Ioo 0 m, 0 < thr y N s := fun s hs => by
    have hsm : (s : ℝ) < m := by exact_mod_cast (mem_Ioo.mp hs).2
    exact div_pos hy (by linarith)
  have h2 : (2 : ℝ) ≤ (sdPair (1 / y) 2).1 :=
    calc (2 : ℝ) = ((2 : ℕ) : ℝ) * (((2 : ℕ) : ℝ) - 1) := by norm_num
      _ ≤ (sdPair (1 / y) 2).1 := (sdPair_lower (1 / y) 2).1
  rw [curvSum_eq_inv hy.ne']
  refine mul_pos (inv_pos.mpr hy) (lt_of_lt_of_le ?_ (Finset.single_le_sum
    (fun Q _ => mul_nonneg (sdPair_nonneg _ Q).1 (Vc_nonneg (fun s hs => (hthr s hs).le) Q))
    (mem_Icc.mpr ⟨by omega, hm⟩ : 2 ∈ Icc 1 m)))
  exact mul_pos (by linarith) (Vc_pos hthr (by omega) hm)

/-! ### The step along the diagonal -/

/-- The two profiles compared at one cut point (Bernoulli's inequality):
`((k+1)/(k+1+h))^(k+1) ≤ (k/(k+h))^k` for `k ≥ 1`, `h > 0`. -/
private theorem profile_pow_le {k : ℕ} (hk : 1 ≤ k) {h : ℝ} (hh : 0 < h) :
    (((k : ℝ) + 1) / ((k : ℝ) + 1 + h)) ^ (k + 1) ≤ ((k : ℝ) / ((k : ℝ) + h)) ^ k := by
  have hK : (0 : ℝ) < k := by exact_mod_cast hk
  have hK1 : (0 : ℝ) < (k : ℝ) + 1 := by linarith
  have hKh : (0 : ℝ) < (k : ℝ) + h := by linarith
  have hKh1 : (0 : ℝ) < (k : ℝ) + 1 + h := by linarith
  obtain ⟨P, hP⟩ : ∃ P : ℝ, P = (k : ℝ) / ((k : ℝ) + h) := ⟨_, rfl⟩
  obtain ⟨P', hP'⟩ : ∃ P' : ℝ, P' = ((k : ℝ) + 1) / ((k : ℝ) + 1 + h) := ⟨_, rfl⟩
  have hPpos : 0 < P := by rw [hP]; exact div_pos hK hKh
  have hP'pos : 0 < P' := by rw [hP']; exact div_pos hK1 hKh1
  rw [← hP, ← hP']
  -- Bernoulli with `a = -h/((k+1)(k+h))`: `1 + (k+1) a = P` and `1 + a = P / P'`
  have hden : (0 : ℝ) < ((k : ℝ) + 1) * ((k : ℝ) + h) := mul_pos hK1 hKh
  have ha : (-2 : ℝ) ≤ -h / (((k : ℝ) + 1) * ((k : ℝ) + h)) := by
    rw [le_div_iff₀ hden]
    nlinarith
  have hB := one_add_mul_le_pow ha (k + 1)
  have e1 : (1 : ℝ) + ((k + 1 : ℕ) : ℝ) * (-h / (((k : ℝ) + 1) * ((k : ℝ) + h))) = P := by
    rw [hP]
    push_cast
    field_simp
    ring
  have e2 : (1 : ℝ) + -h / (((k : ℝ) + 1) * ((k : ℝ) + h)) = P / P' := by
    rw [hP, hP']
    field_simp
    ring
  rw [e1, e2, div_pow, le_div_iff₀ (pow_pos hP'pos _)] at hB
  refine le_of_mul_le_mul_right ?_ hPpos
  calc P' ^ (k + 1) * P = P * P' ^ (k + 1) := by ring
    _ ≤ P ^ (k + 1) := hB
    _ = P ^ k * P := by ring

/-- **The curvature sum along the diagonal.**  For `2 ≤ m < q` and `401 m² ≤ 12 k²`,
`curvSum (k+1) (k+q+1) m ≤ k/(k+1) · exp((1+1/400)(D_m+1)(q-m/2)/(k(k+1))) · curvSum k (k+q) m`,
where `D_m = Dbirth m`.

Both sides are written as `y⁻¹ ∑_Q s_Q(1/y) · Vc (thr y N) Q m`.  Since `s_Q` increases, it is
enough to compare `X = ∑_Q v_Q Vc P' Q m` with `Y = ∑_Q v_Q Vc P Q m` for the weights
`v_Q = s_Q(1/k)` and the profiles `P' = thr (k+1) (k+q+1)`, `P = thr k (k+q)`.  `Vc_sum_pow_le`
gives `X^k ≤ ρ^(-μ) Y^k` with `ρ = (k+1)/(k+1+q-m/2)`, and `ρ^(-μ) ≤ exp(μ (q-m/2)/(k+1))`.  The
bound `μ` for the mean of `Q - 1` comes from `Q(Q-1) ≤ v_Q ≤ (1+1/400) Q(Q-1)` and from the
definition of `D_m` (`Dbirth_spec`). -/
theorem curvSum_step {k q m : ℕ} (hk : 1 ≤ k) (hm2 : 2 ≤ m) (hmq : m + 1 ≤ q)
    (hmk : 401 * m ^ 2 ≤ 12 * k ^ 2) :
    curvSum ((k : ℝ) + 1) ((k : ℝ) + q + 1) m
      ≤ (k : ℝ) / ((k : ℝ) + 1)
          * Real.exp ((1 + 1 / 400) * (Dbirth m + 1) * ((q : ℝ) - (m : ℝ) / 2)
              / ((k : ℝ) * ((k : ℝ) + 1)))
          * curvSum (k : ℝ) ((k : ℝ) + q) m := by
  have hK : (0 : ℝ) < k := by exact_mod_cast hk
  have hK1 : (0 : ℝ) < (k : ℝ) + 1 := by linarith
  have hmR : (2 : ℝ) ≤ m := by exact_mod_cast hm2
  have hqR : (m : ℝ) + 1 ≤ q := by exact_mod_cast hmq
  have hmkR : 401 * (m : ℝ) ^ 2 ≤ 12 * (k : ℝ) ^ 2 := by exact_mod_cast hmk
  obtain ⟨μ, hμdef⟩ : ∃ μ : ℝ, μ = (1 + 1 / 400) * (Dbirth m + 1) := ⟨_, rfl⟩
  have hμ0 : 0 ≤ μ := by
    rw [hμdef]
    nlinarith [Dbirth_nonneg hm2]
  obtain ⟨δ, hδ⟩ : ∃ δ : ℝ, δ = (q : ℝ) - (m : ℝ) / 2 := ⟨_, rfl⟩
  have hδ0 : 0 ≤ δ := by rw [hδ]; linarith
  obtain ⟨ρ, hρdef⟩ : ∃ ρ : ℝ, ρ = ((k : ℝ) + 1) / ((k : ℝ) + 1 + δ) := ⟨_, rfl⟩
  have hρden : 0 < (k : ℝ) + 1 + δ := by linarith
  have hρ0 : 0 < ρ := by rw [hρdef]; exact div_pos hK1 hρden
  have hρ1 : ρ ≤ 1 := by rw [hρdef, div_le_one hρden]; linarith
  -- the weights `v_Q = s_Q(1/k)`
  obtain ⟨v, hv⟩ : ∃ v : ℕ → ℝ, v = fun Q => (sdPair (1 / (k : ℝ)) Q).1 := ⟨_, rfl⟩
  have hv0 : ∀ Q, 0 ≤ v Q := fun Q => by rw [hv]; exact (sdPair_nonneg _ Q).1
  have hvlow : ∀ Q : ℕ, (Q : ℝ) * ((Q : ℝ) - 1) ≤ v Q := fun Q => by
    rw [hv]
    exact (sdPair_lower _ Q).1
  have hvup : ∀ Q ∈ Icc 1 m, v Q ≤ (1 + 1 / 400) * ((Q : ℝ) * ((Q : ℝ) - 1)) := fun Q hQ => by
    rw [hv]
    refine sdPair_upper (m := m) (by norm_num) ?_ (mem_Icc.mp hQ).2
    rw [one_div, inv_pow, inv_mul_eq_div, div_mul_eq_mul_div, div_le_iff₀ (pow_pos hK 2)]
    linarith
  -- the two profiles
  have hP'nn : ∀ s ∈ Ioo 0 m, 0 ≤ thr ((k : ℝ) + 1) ((k : ℝ) + q + 1) s := fun s hs => by
    have hsm : (s : ℝ) < m := by exact_mod_cast (mem_Ioo.mp hs).2
    exact div_nonneg hK1.le (by linarith)
  have hPnn : ∀ s ∈ Ioo 0 m, 0 ≤ thr (k : ℝ) ((k : ℝ) + q) s := fun s hs => by
    have hsm : (s : ℝ) < m := by exact_mod_cast (mem_Ioo.mp hs).2
    exact div_nonneg hK.le (by linarith)
  have hgw : ∀ s ∈ Ioo 0 m,
      thr ((k : ℝ) + 1) ((k : ℝ) + q + 1) s ^ (k + 1) ≤ thr (k : ℝ) ((k : ℝ) + q) s ^ k := by
    intro s hs
    have hsm : (s : ℝ) < m := by exact_mod_cast (mem_Ioo.mp hs).2
    have h := profile_pow_le hk (show (0 : ℝ) < (q : ℝ) - s by linarith)
    rw [thr_apply, thr_apply, show (k : ℝ) + q + 1 - (s : ℝ) = (k : ℝ) + 1 + ((q : ℝ) - s) by ring,
      show (k : ℝ) + q - (s : ℝ) = (k : ℝ) + ((q : ℝ) - s) by ring]
    exact h
  have hsym : ∀ s ∈ Ioo 0 m, ρ ^ 2
      ≤ thr ((k : ℝ) + 1) ((k : ℝ) + q + 1) s * thr ((k : ℝ) + 1) ((k : ℝ) + q + 1) (m - s) := by
    intro s hs
    have hs' := mem_Ioo.mp hs
    have hsm : (s : ℝ) < m := by exact_mod_cast hs'.2
    have hA : (0 : ℝ) < ((k : ℝ) + q + 1 - (s : ℝ)) * ((k : ℝ) + q + 1 - ((m : ℝ) - s)) :=
      mul_pos (by linarith) (by linarith)
    rw [thr_apply, thr_apply, Nat.cast_sub hs'.2.le, hρdef, hδ, div_pow, div_mul_div_comm,
      ← sq]
    refine div_le_div_of_nonneg_left (sq_nonneg _) hA ?_
    nlinarith [sq_nonneg ((m : ℝ) / 2 - s)]
  -- the mean of `Q - 1` under the weights `v_Q T_{m,Q}`
  have hlow : ∑ Q ∈ Icc 1 m, (Q : ℝ) * ((Q : ℝ) - 1) * Tq m Q ≤ ∑ Q ∈ Icc 1 m, v Q * Tq m Q :=
    Finset.sum_le_sum fun Q _ => mul_le_mul_of_nonneg_right (hvlow Q) (Tq_nonneg m Q)
  have hpos : 0 < ∑ Q ∈ Icc 1 m, v Q * Tq m Q := lt_of_lt_of_le (sum_qq_Tq_pos hm2) hlow
  have hμ : ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1) ≤ μ * ∑ Q ∈ Icc 1 m, v Q * Tq m Q := by
    have hup : ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1)
        ≤ ∑ Q ∈ Icc 1 m, (1 + 1 / 400)
            * ((Q : ℝ) * ((Q : ℝ) - 1) * ((Q : ℝ) - 2) * Tq m Q
              + (Q : ℝ) * ((Q : ℝ) - 1) * Tq m Q) := by
      refine Finset.sum_le_sum fun Q hQ => ?_
      have hQ1 : (1 : ℝ) ≤ Q := by exact_mod_cast (mem_Icc.mp hQ).1
      calc v Q * Tq m Q * ((Q : ℝ) - 1)
          ≤ (1 + 1 / 400) * ((Q : ℝ) * ((Q : ℝ) - 1)) * Tq m Q * ((Q : ℝ) - 1) :=
            mul_le_mul_of_nonneg_right
              (mul_le_mul_of_nonneg_right (hvup Q hQ) (Tq_nonneg m Q)) (by linarith)
        _ = (1 + 1 / 400) * ((Q : ℝ) * ((Q : ℝ) - 1) * ((Q : ℝ) - 2) * Tq m Q
              + (Q : ℝ) * ((Q : ℝ) - 1) * Tq m Q) := by ring
    rw [← Finset.mul_sum, Finset.sum_add_distrib, Dbirth_spec hm2] at hup
    calc ∑ Q ∈ Icc 1 m, v Q * Tq m Q * ((Q : ℝ) - 1)
        ≤ μ * ∑ Q ∈ Icc 1 m, (Q : ℝ) * ((Q : ℝ) - 1) * Tq m Q := by
          rw [hμdef]
          linear_combination hup
      _ ≤ μ * ∑ Q ∈ Icc 1 m, v Q * Tq m Q := mul_le_mul_of_nonneg_left hlow hμ0
  -- the comparison of the two profiles
  have hL := Vc_sum_pow_le hk (fun Q _ => hv0 Q) hP'nn hPnn hgw hρ0 hρ1 hsym hpos hμ
  obtain ⟨X, hX⟩ : ∃ X : ℝ, X = ∑ Q ∈ Icc 1 m,
      v Q * Vc (thr ((k : ℝ) + 1) ((k : ℝ) + q + 1)) Q m := ⟨_, rfl⟩
  obtain ⟨Y, hY⟩ : ∃ Y : ℝ, Y = ∑ Q ∈ Icc 1 m, v Q * Vc (thr (k : ℝ) ((k : ℝ) + q)) Q m :=
    ⟨_, rfl⟩
  rw [← hX, ← hY] at hL
  have hY0 : 0 ≤ Y := by
    rw [hY]
    exact Finset.sum_nonneg fun Q _ => mul_nonneg (hv0 Q) (Vc_nonneg hPnn Q)
  obtain ⟨E, hE⟩ : ∃ E : ℝ, E = μ * δ / ((k : ℝ) * ((k : ℝ) + 1)) := ⟨_, rfl⟩
  have hXY : X ≤ Real.exp E * Y := by
    refine le_of_pow_le_pow_left₀ (Nat.pos_iff_ne_zero.mp hk) (mul_nonneg (Real.exp_pos E).le hY0)
      ?_
    rw [mul_pow, ← Real.exp_nat_mul]
    refine le_trans hL (mul_le_mul_of_nonneg_right ?_ (pow_nonneg hY0 k))
    -- `ρ^(-μ) = (1 + δ/(k+1))^μ ≤ exp(δ/(k+1) · μ) = exp(k E)`
    have e2 : ρ⁻¹ = 1 + δ / ((k : ℝ) + 1) := by
      rw [hρdef, inv_div]
      field_simp
    have e3 : ρ⁻¹ ≤ Real.exp (δ / ((k : ℝ) + 1)) := by
      rw [e2]
      linarith [Real.add_one_le_exp (δ / ((k : ℝ) + 1))]
    have e4 : (k : ℝ) * E = δ / ((k : ℝ) + 1) * μ := by
      rw [hE]
      field_simp
    rw [Real.rpow_neg hρ0.le, ← Real.inv_rpow hρ0.le, e4, Real.exp_mul]
    exact Real.rpow_le_rpow (inv_nonneg.mpr hρ0.le) e3 hμ0
  -- back to the curvature sums
  have hA : ∑ Q ∈ Icc 1 m, (sdPair (1 / ((k : ℝ) + 1)) Q).1
        * Vc (thr ((k : ℝ) + 1) ((k : ℝ) + q + 1)) Q m ≤ X := by
    rw [hX, hv]
    exact Finset.sum_le_sum fun Q _ => mul_le_mul_of_nonneg_right
      (sdPair_mono (by positivity) (one_div_le_one_div_of_le hK (by linarith)) Q).1
      (Vc_nonneg hP'nn Q)
  have hE' : (1 + 1 / 400) * (Dbirth m + 1) * ((q : ℝ) - (m : ℝ) / 2)
      / ((k : ℝ) * ((k : ℝ) + 1)) = E := by rw [hE, hμdef, hδ]
  rw [hv] at hY
  rw [hE', curvSum_eq_inv hK1.ne', curvSum_eq_inv hK.ne', ← hY]
  calc ((k : ℝ) + 1)⁻¹ * ∑ Q ∈ Icc 1 m, (sdPair (1 / ((k : ℝ) + 1)) Q).1
        * Vc (thr ((k : ℝ) + 1) ((k : ℝ) + q + 1)) Q m
      ≤ ((k : ℝ) + 1)⁻¹ * (Real.exp E * Y) :=
        mul_le_mul_of_nonneg_left (hA.trans hXY) (inv_nonneg.mpr hK1.le)
    _ = (k : ℝ) / ((k : ℝ) + 1) * Real.exp E * ((k : ℝ)⁻¹ * Y) := by field_simp

end Parking
