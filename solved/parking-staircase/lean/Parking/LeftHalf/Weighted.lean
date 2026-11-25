import Parking.LeftHalf.FirstLayer.Main
import Parking.Series.AllRows
import Parking.Tilt.Monotone

/-!
# Weighted diagonal convexity on all sizes, and the weighted debt

Column `k`, critical tilt `x = xcrit k`.  Write `a_i = zrT (k+1) x i`, `b_i = zrT k x i`,
`d_i = zrT (k-1) x i` for the tilted environments of the thresholds `k+1, k, k-1`
(`d ≤ b ≤ a`), `U_i = Ut k x i = b_i - d_i`, `U⁺_i = Ut (k+1) x i = a_i - b_i`, and
`w_i = ccT x i = c_i x^i` for the free weights, with which `a`, `b`, `d` agree up to the index
`k - 1`.  The weight of this file is `Ψ′(N) = PsiW k N = max(N, 2k-1)`.

* `Ut_diag_lower`: the diagonal lower bound `γ_k β^{(k-1)}_{n-1} ≤ β^{(k)}_n` (`bq_diag_lower`, all
  rows `n ≥ 1`) at the critical tilt, where `(k+1) x_k γ_k = k`: `k U_{n-1} ≤ (k+1) U⁺_n`.
* `DeltaId_nonneg` (weighted convexity with the identity weight):
  `Δ_id(N) = (N+1) a_{N+1} - 2N b_N + (N-1) d_{N-1} ≥ 0` for every `N ≥ 2k-1`, `k ≥ 7`.  The three
  last-car recursions (`zrT_succ`) are split once, according to whether the first index, no index,
  or the second index is `≤ k-2` (`wd_conv_split`).  The outer parts are instances of
  `(c+1) a_{M+1} - 2c b_M + (c-1) d_{M-1} ≥ 0` with `k ≤ c ≤ 2k-1`, which for `M ≤ 2k-2` is the
  first-layer inequality `FirstLayer.zrT_weak_requirement` and for `M ≥ 2k-1` follows from
  `Δ_id(M) ≥ 0` (induction).  The middle part is bounded below with the tilted diagonal lower
  bound `k U_{n-1} ≤ (k+1) U⁺_n` (`Ut_diag_lower`) after one index shift (`wd_mid_lower`).
* `DeltaPsi_nonneg` (weighted convexity with the weight `Ψ′`):
  `Δ_{Ψ′}(N) = Ψ′(N+1) a_{N+1} - 2Ψ′(N) b_N + Ψ′(N-1) d_{N-1} ≥ 0` for `N ≥ k`, `k ≥ 7`.  On
  `k ≤ N ≤ 2k-2` the three weights are equal and this is the first-layer convexity
  `FirstLayer.zrT_diag_convex`; from `N = 2k-1` on it is `DeltaId_nonneg`.
* `weighted_debt`: with `η_n = dq k n · x^n = a_n - 2 b_n + d_n`,
  `∑_{n=k}^{J} Ψ′(n) η_n ≥ -(Ψ′(J) U_J + Ψ′(J-1) U_{J-1} + (Ψ′(J) - Ψ′(J-1)) b_J)`.
  Summation by parts turns the left-hand side plus the boundary terms into the sum of the
  `Δ_{Ψ′}(N)`, `k ≤ N < J`; the last step uses that `b` does not increase (`zrT_anti_crit`).
-/

namespace Parking
open Finset

/-! ### The diagonal lower bound at the critical tilt -/

/-- `(k+1) x_k γ_k = k` at the critical tilt. -/
private theorem succ_mul_xcrit_mul_gam {k : ℕ} (hk : 2 ≤ k) :
    ((k : ℝ) + 1) * (xcrit k * gam k) = (k : ℝ) := by
  have hpsi := xcrit_mul_psi (k := k) (by omega)
  rw [psi_eq_gam hk] at hpsi
  have hkne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have e : xcrit k * (gam k * (1 + 1 / (k : ℝ))) * (k : ℝ)
      = ((k : ℝ) + 1) * (xcrit k * gam k) := by
    field
  rw [← e, hpsi, one_mul]

/-- **The diagonal lower bound at the critical tilt.**  For `k ≥ 2` and `n ≥ 1`:
`k U_{n-1} ≤ (k+1) U⁺_n`. -/
theorem Ut_diag_lower {k n : ℕ} (hk : 2 ≤ k) (hn : 1 ≤ n) :
    (k : ℝ) * Ut k (xcrit k) (n - 1) ≤ ((k : ℝ) + 1) * Ut (k + 1) (xcrit k) n := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  rw [Nat.add_sub_cancel]
  have hx : 0 < xcrit k := xcrit_pos k
  have h1 := Ut_eq_bq hk (xcrit k) m
  have h2 := Ut_eq_bq (k := k + 1) (by omega) (xcrit k) (m + 1)
  rw [Nat.add_sub_cancel] at h2
  have hD := bq_diag_lower hk (show 1 ≤ m + 1 by omega)
  rw [Nat.add_sub_cancel] at hD
  have hxg := succ_mul_xcrit_mul_gam hk
  have hk0 : (0 : ℝ) ≤ (k : ℝ) + 1 := by positivity
  have hcoef : 0 ≤ ((k : ℝ) + 1) * xcrit k * xcrit k ^ m :=
    mul_nonneg (mul_nonneg hk0 hx.le) (pow_pos hx m).le
  rw [h1, h2, pow_succ']
  calc (k : ℝ) * (bq (k - 1) m * xcrit k ^ m)
      = ((k : ℝ) + 1) * xcrit k * xcrit k ^ m * (gam k * bq (k - 1) m) := by
        linear_combination (-(bq (k - 1) m * xcrit k ^ m)) * hxg
    _ ≤ ((k : ℝ) + 1) * xcrit k * xcrit k ^ m * bq k (m + 1) :=
        mul_le_mul_of_nonneg_left hD hcoef
    _ = ((k : ℝ) + 1) * (bq k (m + 1) * (xcrit k * xcrit k ^ m)) := by ring

/-! ### The weight `Ψ′` -/

/-- The weight `Ψ′(N) = max(N, 2k-1)`. -/
noncomputable def PsiW (k N : ℕ) : ℝ := ((max N (2 * k - 1) : ℕ) : ℝ)

/-- $\Psi'(N)=N$ for $N\ge 2k-1$, where $\Psi'(N)=\max(N,2k-1)$. -/
theorem PsiW_of_ge {k N : ℕ} (h : 2 * k - 1 ≤ N) : PsiW k N = (N : ℝ) := by
  rw [PsiW, Nat.max_eq_left h]

/-- $\Psi'(N)=2k-1$ for $N\le 2k-1$ and $k\ge 1$, where $\Psi'(N)=\max(N,2k-1)$. -/
theorem PsiW_low {k N : ℕ} (hk : 1 ≤ k) (h : N ≤ 2 * k - 1) : PsiW k N = 2 * (k : ℝ) - 1 := by
  rw [PsiW, Nat.max_eq_right h, Nat.cast_sub (by omega : 1 ≤ 2 * k), Nat.cast_mul, Nat.cast_ofNat,
    Nat.cast_one]

private theorem PsiW_nonneg (k N : ℕ) : 0 ≤ PsiW k N := Nat.cast_nonneg _

/-- $\Psi'(N)\le\Psi'(N')$ for $N\le N'$, where $\Psi'(N)=\max(N,2k-1)$. -/
theorem PsiW_mono {k N N' : ℕ} (h : N ≤ N') : PsiW k N ≤ PsiW k N' :=
  Nat.cast_le.mpr (max_le_max h (le_refl _))

/-- $N\le\Psi'(N)$, where $\Psi'(N)=\max(N,2k-1)$. -/
theorem PsiW_ge_self (k N : ℕ) : (N : ℝ) ≤ PsiW k N := Nat.cast_le.mpr (le_max_left _ _)

/-! ### Sums over ranges -/

/-- `range (p + m + p)` split into the first `p` indices, the middle `m` indices and the last `p`
indices (the last ones listed backwards). -/
private theorem wd_sum_range_split3 (f : ℕ → ℝ) (p m : ℕ) :
    ∑ i ∈ range (p + m + p), f i
      = ∑ l ∈ range p, f l + ∑ t ∈ range m, f (p + t)
        + ∑ l ∈ range p, f (p + m + (p - 1 - l)) := by
  have h := Finset.sum_range_reflect (fun l => f (p + m + l)) p
  rw [Finset.sum_range_add, Finset.sum_range_add]
  exact congrArg (fun z => ∑ l ∈ range p, f l + ∑ t ∈ range m, f (p + t) + z) h.symm

/-- One index shift in a difference of two sums. -/
private theorem wd_sum_shift (f g : ℕ → ℝ) (r : ℕ) :
    ∑ t ∈ range (r + 1), (f t - g t)
      = ∑ t ∈ range r, (f t - g (t + 1)) + f r - g 0 := by
  rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, Finset.sum_range_succ f r,
    Finset.sum_range_succ' g r]
  ring

set_option maxHeartbeats 400000 in
/-- The convolution of the last-car recursion with threshold `y`, split according to whether the
first index is `< p`, neither index is, or the second index is `< p`.  On the indices `< p` the
sequence `u` is the free sequence `w`. -/
private theorem wd_conv_split (u w : ℕ → ℝ) {y p m n : ℕ} (hn : n + 1 = p + m + p) (hp : p ≤ y)
    (hy : y ≤ p + m + 1) (hfree : ∀ i, i < p → u i = w i) :
    ∑ i ∈ range (n + 1), ((min (i + 1) y : ℕ) : ℝ) * u i * u (n - i)
      = ∑ l ∈ range p, ((l : ℝ) + 1 + (y : ℝ)) * w l * u (n - l)
        + ∑ t ∈ range m, ((min (p + t + 1) y : ℕ) : ℝ) * u (p + t) * u (n - (p + t)) := by
  have hs : ∑ i ∈ range (p + m + p), ((min (i + 1) y : ℕ) : ℝ) * u i * u (n - i)
      = ∑ l ∈ range p, ((min (l + 1) y : ℕ) : ℝ) * u l * u (n - l)
        + ∑ t ∈ range m, ((min (p + t + 1) y : ℕ) : ℝ) * u (p + t) * u (n - (p + t))
        + ∑ l ∈ range p, ((min (p + m + (p - 1 - l) + 1) y : ℕ) : ℝ) * u (p + m + (p - 1 - l))
            * u (n - (p + m + (p - 1 - l))) :=
    wd_sum_range_split3 (fun i => ((min (i + 1) y : ℕ) : ℝ) * u i * u (n - i)) p m
  have h1 : ∑ l ∈ range p, ((min (l + 1) y : ℕ) : ℝ) * u l * u (n - l)
      = ∑ l ∈ range p, ((l : ℝ) + 1) * w l * u (n - l) := by
    refine Finset.sum_congr rfl fun l hl => ?_
    rw [Finset.mem_range] at hl
    have e1 : min (l + 1) y = l + 1 := min_eq_left (by omega)
    rw [e1, hfree l hl, Nat.cast_add, Nat.cast_one]
  have h3 : ∑ l ∈ range p, ((min (p + m + (p - 1 - l) + 1) y : ℕ) : ℝ) * u (p + m + (p - 1 - l))
            * u (n - (p + m + (p - 1 - l)))
      = ∑ l ∈ range p, (y : ℝ) * w l * u (n - l) := by
    refine Finset.sum_congr rfl fun l hl => ?_
    rw [Finset.mem_range] at hl
    have e1 : p + m + (p - 1 - l) = n - l := by omega
    have e2 : n - (n - l) = l := by omega
    have e3 : min (n - l + 1) y = y := min_eq_right (by omega)
    rw [e1, e2, e3, hfree l hl]
    ring
  have h4 : ∑ l ∈ range p, ((l : ℝ) + 1 + (y : ℝ)) * w l * u (n - l)
      = ∑ l ∈ range p, ((l : ℝ) + 1) * w l * u (n - l)
        + ∑ l ∈ range p, (y : ℝ) * w l * u (n - l) := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun l _ => ?_
    ring
  rw [hn, hs, h1, h3, h4]
  ring

/-! ### The abstract positivity argument

Sequences `a ≥ b ≥ d ≥ 0` with free part `w`; `s = k - 2`, `r ≥ 0`, sizes `N = 2s + r + 3`. -/

set_option maxHeartbeats 800000 in
/-- The middle part of the split, together with the two boundary terms, is nonnegative. -/
private theorem wd_mid_lower (a b d w : ℕ → ℝ) (s r : ℕ)
    (hw : ∀ i, 0 ≤ w i) (ha0 : ∀ i, 0 ≤ a i) (hb0 : ∀ i, 0 ≤ b i)
    (hab : ∀ i, b i ≤ a i) (hdb : ∀ i, d i ≤ b i) (hbs : b s = d s)
    (hEp : ∀ i, s + 1 ≤ i → b i ≤ a (i + 1)) (hEm : ∀ i, s + 1 ≤ i → d i ≤ b (i + 1))
    (hT : ∀ t, t ≤ r →
      0 ≤ ((s : ℝ) + 3) * a (s + t + 1 + 1) - 2 * ((s : ℝ) + 2) * b (s + t + 1)
        + ((s : ℝ) + 1) * d (s + t))
    (hDg : ∀ j, ((s : ℝ) + 2) * (b j - d j) ≤ ((s : ℝ) + 3) * (a (j + 1) - b (j + 1)))
    (hbd : ((s : ℝ) + 1) * w s ≤ ((s : ℝ) + 2) * w (s + 1))
    (hd1 : d s = w s) (ha1 : a (s + 1) = w (s + 1)) :
    0 ≤ ∑ t ∈ range (r + 1), (((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1)
            - 2 * (((s : ℝ) + 2) * b (s + t + 1) * b (s + (r - t) + 1))
            + ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1))
        + (((s : ℝ) + 2) * a (s + 1) * a (s + r + 1 + 1)
            - ((s : ℝ) + 1) * d s * d (s + r + 1)) := by
  have hs0 : (0 : ℝ) ≤ (s : ℝ) := Nat.cast_nonneg s
  -- termwise: use `T ≥ 0` and the diagonal lower bound
  have hterm : ∀ t ∈ range (r + 1),
      ((s : ℝ) + 2) * a (s + t + 1 + 1) * (b (s + (r - t)) - d (s + (r - t)))
          - ((s : ℝ) + 1) * d (s + t) * (b (s + (r - t) + 1) - d (s + (r - t) + 1))
        ≤ ((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1)
            - 2 * (((s : ℝ) + 2) * b (s + t + 1) * b (s + (r - t) + 1))
            + ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1) := by
    intro t ht
    rw [Finset.mem_range] at ht
    have h1 := hT t (by omega)
    have h2 := hDg (s + (r - t))
    have h3 := hb0 (s + (r - t) + 1)
    have h4 := ha0 (s + t + 1 + 1)
    linarith only [mul_nonneg h3 h1, mul_nonneg h4 (sub_nonneg.mpr h2)]
  have hsum1 := Finset.sum_le_sum hterm
  -- shift the index of the subtracted terms
  have hshift : ∑ t ∈ range (r + 1),
        (((s : ℝ) + 2) * a (s + t + 1 + 1) * (b (s + (r - t)) - d (s + (r - t)))
          - ((s : ℝ) + 1) * d (s + t) * (b (s + (r - t) + 1) - d (s + (r - t) + 1)))
      = ∑ t ∈ range r,
          (((s : ℝ) + 2) * a (s + t + 1 + 1) * (b (s + (r - t)) - d (s + (r - t)))
            - ((s : ℝ) + 1) * d (s + (t + 1))
              * (b (s + (r - (t + 1)) + 1) - d (s + (r - (t + 1)) + 1)))
        + ((s : ℝ) + 2) * a (s + r + 1 + 1) * (b (s + (r - r)) - d (s + (r - r)))
        - ((s : ℝ) + 1) * d (s + 0) * (b (s + (r - 0) + 1) - d (s + (r - 0) + 1)) :=
    wd_sum_shift
      (fun t => ((s : ℝ) + 2) * a (s + t + 1 + 1) * (b (s + (r - t)) - d (s + (r - t))))
      (fun t => ((s : ℝ) + 1) * d (s + t) * (b (s + (r - t) + 1) - d (s + (r - t) + 1))) r
  have er : s + (r - r) = s := by omega
  have e0 : s + 0 = s := by omega
  have e0' : s + (r - 0) + 1 = s + r + 1 := by omega
  rw [er, e0, e0'] at hshift
  -- the shifted terms are nonnegative
  have hpair : ∀ t ∈ range r,
      0 ≤ ((s : ℝ) + 2) * a (s + t + 1 + 1) * (b (s + (r - t)) - d (s + (r - t)))
            - ((s : ℝ) + 1) * d (s + (t + 1))
              * (b (s + (r - (t + 1)) + 1) - d (s + (r - (t + 1)) + 1)) := by
    intro t ht
    rw [Finset.mem_range] at ht
    have e : s + (r - (t + 1)) + 1 = s + (r - t) := by omega
    rw [e]
    have h1 : d (s + (t + 1)) ≤ a (s + t + 1 + 1) := by
      have h := hEm (s + (t + 1)) (by omega)
      have h' := hab (s + (t + 1) + 1)
      have e2 : s + (t + 1) + 1 = s + t + 1 + 1 := by omega
      rw [e2] at h h'
      exact le_trans h h'
    have hU : 0 ≤ b (s + (r - t)) - d (s + (r - t)) := sub_nonneg.mpr (hdb (s + (r - t)))
    have ha' := ha0 (s + t + 1 + 1)
    linarith only [mul_nonneg (mul_nonneg hs0 (sub_nonneg.mpr h1)) hU,
      mul_nonneg (sub_nonneg.mpr h1) hU, mul_nonneg ha' hU]
  have hsum2 := Finset.sum_nonneg hpair
  -- the two boundary terms
  have hz : ((s : ℝ) + 2) * a (s + r + 1 + 1) * (b s - d s) = 0 := by
    rw [hbs, sub_self, mul_zero]
  have hXY : b (s + r + 1) ≤ a (s + r + 1 + 1) := hEp (s + r + 1) (by omega)
  have hfin : 0 ≤ ((s : ℝ) + 2) * a (s + 1) * a (s + r + 1 + 1)
      - ((s : ℝ) + 1) * d s * b (s + r + 1) := by
    rw [ha1, hd1]
    have hs2 : (0 : ℝ) ≤ (s : ℝ) + 2 := by linarith only [hs0]
    linarith only [mul_nonneg (mul_nonneg hs2 (hw (s + 1))) (sub_nonneg.mpr hXY),
      mul_nonneg (sub_nonneg.mpr hbd) (hb0 (s + r + 1))]
  linarith only [hsum1, hshift, hsum2, hz, hfin]

/-- The middle sum of the split of the `a`-convolution. -/
private theorem wd_midA (a : ℕ → ℝ) (s r n : ℕ) (hn : n = 2 * s + r + 1) :
    ∑ t ∈ range (r + 1 + 1), ((min (s + 1 + t + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + t)
        * a (n + 1 + 1 - (s + 1 + t))
      = ∑ t ∈ range (r + 1), ((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1)
        + ((s : ℝ) + 2) * a (s + 1) * a (s + r + 1 + 1) := by
  have c3 : ((s + 3 : ℕ) : ℝ) = (s : ℝ) + 3 := by push_cast; ring
  have h0 : ∑ t ∈ range (r + 1 + 1), ((min (s + 1 + t + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + t)
        * a (n + 1 + 1 - (s + 1 + t))
      = ∑ t ∈ range (r + 1), ((min (s + 1 + (t + 1) + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + (t + 1))
          * a (n + 1 + 1 - (s + 1 + (t + 1)))
        + ((min (s + 1 + 0 + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + 0)
          * a (n + 1 + 1 - (s + 1 + 0)) :=
    Finset.sum_range_succ' (fun t => ((min (s + 1 + t + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + t)
        * a (n + 1 + 1 - (s + 1 + t))) (r + 1)
  have h1 : ∑ t ∈ range (r + 1), ((min (s + 1 + (t + 1) + 1) (s + 3) : ℕ) : ℝ)
          * a (s + 1 + (t + 1)) * a (n + 1 + 1 - (s + 1 + (t + 1)))
      = ∑ t ∈ range (r + 1), ((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1) := by
    refine Finset.sum_congr rfl fun t ht => ?_
    rw [Finset.mem_range] at ht
    have e1 : min (s + 1 + (t + 1) + 1) (s + 3) = s + 3 := min_eq_right (by omega)
    have e2 : s + 1 + (t + 1) = s + t + 1 + 1 := by omega
    have e3 : n + 1 + 1 - (s + t + 1 + 1) = s + (r - t) + 1 := by omega
    rw [e1, e2, e3, c3]
  have h2 : ((min (s + 1 + 0 + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + 0)
        * a (n + 1 + 1 - (s + 1 + 0))
      = ((s : ℝ) + 2) * a (s + 1) * a (s + r + 1 + 1) := by
    have e1 : min (s + 1 + 0 + 1) (s + 3) = s + 1 + 0 + 1 := min_eq_left (by omega)
    have e3 : n + 1 + 1 - (s + 1 + 0) = s + r + 1 + 1 := by omega
    have e0 : s + 1 + 0 = s + 1 := by omega
    have c : ((s + 1 + 0 + 1 : ℕ) : ℝ) = (s : ℝ) + 2 := by push_cast; ring
    rw [e1, c, e3, e0]
  rw [h0, h1, h2]

/-- The middle sum of the split of the `b`-convolution. -/
private theorem wd_midB (b : ℕ → ℝ) (s r n : ℕ) (hn : n = 2 * s + r + 1) :
    ∑ t ∈ range (r + 1), ((min (s + 1 + t + 1) (s + 2) : ℕ) : ℝ) * b (s + 1 + t)
        * b (n + 1 - (s + 1 + t))
      = ∑ t ∈ range (r + 1), ((s : ℝ) + 2) * b (s + t + 1) * b (s + (r - t) + 1) := by
  have c2 : ((s + 2 : ℕ) : ℝ) = (s : ℝ) + 2 := by push_cast; ring
  refine Finset.sum_congr rfl fun t ht => ?_
  rw [Finset.mem_range] at ht
  have e1 : min (s + 1 + t + 1) (s + 2) = s + 2 := min_eq_right (by omega)
  have e2 : s + 1 + t = s + t + 1 := by omega
  have e3 : n + 1 - (s + t + 1) = s + (r - t) + 1 := by omega
  rw [e1, e2, e3, c2]

/-- The middle sum of the split of the `d`-convolution. -/
private theorem wd_midD (d : ℕ → ℝ) (s r n : ℕ) (hn : n = 2 * s + r + 1) :
    ∑ t ∈ range r, ((min (s + 1 + t + 1) (s + 1) : ℕ) : ℝ) * d (s + 1 + t)
        * d (n - (s + 1 + t))
      = ∑ t ∈ range (r + 1), ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1)
        - ((s : ℝ) + 1) * d s * d (s + r + 1) := by
  have c1 : ((s + 1 : ℕ) : ℝ) = (s : ℝ) + 1 := by push_cast; ring
  have h0 : ∑ t ∈ range (r + 1), ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1)
      = ∑ t ∈ range r, ((s : ℝ) + 1) * d (s + (t + 1)) * d (s + (r - (t + 1)) + 1)
        + ((s : ℝ) + 1) * d (s + 0) * d (s + (r - 0) + 1) :=
    Finset.sum_range_succ' (fun t => ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1)) r
  have h1 : ∑ t ∈ range r, ((min (s + 1 + t + 1) (s + 1) : ℕ) : ℝ) * d (s + 1 + t)
        * d (n - (s + 1 + t))
      = ∑ t ∈ range r, ((s : ℝ) + 1) * d (s + (t + 1)) * d (s + (r - (t + 1)) + 1) := by
    refine Finset.sum_congr rfl fun t ht => ?_
    rw [Finset.mem_range] at ht
    have e1 : min (s + 1 + t + 1) (s + 1) = s + 1 := min_eq_right (by omega)
    have e2 : s + 1 + t = s + (t + 1) := by omega
    have e3 : n - (s + (t + 1)) = s + (r - (t + 1)) + 1 := by omega
    rw [e1, e2, e3, c1]
  have e0 : s + 0 = s := by omega
  have e0' : s + (r - 0) + 1 = s + r + 1 := by omega
  rw [h0, h1, e0, e0']
  ring

/-- The outer parts of the three splits: every term is an instance of `c·DC(M) + e_M ≥ 0`. -/
private theorem wd_outer (a b d w : ℕ → ℝ) (s r n : ℕ) (hn : n = 2 * s + r + 1)
    (hw : ∀ i, 0 ≤ w i)
    (hT : ∀ (i : ℕ) (c : ℝ), s + 1 ≤ i → i ≤ n → (s : ℝ) + 2 ≤ c → c ≤ 2 * (s : ℝ) + 3 →
      0 ≤ (c + 1) * a (i + 1 + 1) - 2 * c * b (i + 1) + (c - 1) * d i) :
    2 * ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 2 : ℕ) : ℝ)) * w l * b (n + 1 - l)
      ≤ ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 3 : ℕ) : ℝ)) * w l * a (n + 1 + 1 - l)
        + ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 1 : ℕ) : ℝ)) * w l * d (n - l) := by
  have c3 : ((s + 3 : ℕ) : ℝ) = (s : ℝ) + 3 := by push_cast; ring
  have c2 : ((s + 2 : ℕ) : ℝ) = (s : ℝ) + 2 := by push_cast; ring
  have c1 : ((s + 1 : ℕ) : ℝ) = (s : ℝ) + 1 := by push_cast; ring
  rw [Finset.mul_sum, ← Finset.sum_add_distrib]
  refine Finset.sum_le_sum fun l hl => ?_
  rw [Finset.mem_range] at hl
  have hl' : (l : ℝ) ≤ (s : ℝ) := Nat.cast_le.mpr (by omega)
  have hl0 : (0 : ℝ) ≤ (l : ℝ) := Nat.cast_nonneg l
  have hT' := hT (n - l) ((l : ℝ) + (s : ℝ) + 3) (by omega) (by omega)
    (by linarith only [hl0]) (by linarith only [hl'])
  have e1 : n - l + 1 + 1 = n + 1 + 1 - l := by omega
  have e2 : n - l + 1 = n + 1 - l := by omega
  rw [e1, e2] at hT'
  rw [c3, c2, c1]
  linarith only [mul_nonneg (hw l) hT']

set_option maxHeartbeats 800000 in
/-- The abstract form of `DeltaId_nonneg` at the size `N = n + 2 = 2s + r + 3` (`k = s + 2`): the
combination `A₊ - 2A₀ + A₋` of the three convolutions is nonnegative. -/
private theorem wd_core_nonneg (a b d w : ℕ → ℝ) (s r n ya yb yd : ℕ)
    (hn : n = 2 * s + r + 1) (hya : ya = s + 3) (hyb : yb = s + 2) (hyd : yd = s + 1)
    (hw : ∀ i, 0 ≤ w i) (ha0 : ∀ i, 0 ≤ a i) (hb0 : ∀ i, 0 ≤ b i)
    (hab : ∀ i, b i ≤ a i) (hdb : ∀ i, d i ≤ b i)
    (hfa : ∀ i, i ≤ s + 1 → a i = w i) (hfb : ∀ i, i ≤ s + 1 → b i = w i)
    (hfd : ∀ i, i ≤ s + 1 → d i = w i)
    (hEp : ∀ i, s + 1 ≤ i → b i ≤ a (i + 1)) (hEm : ∀ i, s + 1 ≤ i → d i ≤ b (i + 1))
    (hT : ∀ (i : ℕ) (c : ℝ), s + 1 ≤ i → i ≤ n → (s : ℝ) + 2 ≤ c → c ≤ 2 * (s : ℝ) + 3 →
      0 ≤ (c + 1) * a (i + 1 + 1) - 2 * c * b (i + 1) + (c - 1) * d i)
    (hT0 : 0 ≤ ((s : ℝ) + 3) * a (s + 1 + 1) - 2 * ((s : ℝ) + 2) * b (s + 1)
      + ((s : ℝ) + 1) * d s)
    (hDg : ∀ j, ((s : ℝ) + 2) * (b j - d j) ≤ ((s : ℝ) + 3) * (a (j + 1) - b (j + 1)))
    (hbd : ((s : ℝ) + 1) * w s ≤ ((s : ℝ) + 2) * w (s + 1)) :
    0 ≤ (∑ i ∈ range (n + 1 + 1 + 1), ((min (i + 1) ya : ℕ) : ℝ) * a i * a (n + 1 + 1 - i))
        - 2 * (∑ i ∈ range (n + 1 + 1), ((min (i + 1) yb : ℕ) : ℝ) * b i * b (n + 1 - i))
        + ∑ i ∈ range (n + 1), ((min (i + 1) yd : ℕ) : ℝ) * d i * d (n - i) := by
  subst hya hyb hyd
  have hs0 : (0 : ℝ) ≤ (s : ℝ) := Nat.cast_nonneg s
  -- the three splits
  have hA : ∑ i ∈ range (n + 1 + 1 + 1), ((min (i + 1) (s + 3) : ℕ) : ℝ) * a i
        * a (n + 1 + 1 - i)
      = ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 3 : ℕ) : ℝ)) * w l * a (n + 1 + 1 - l)
        + ∑ t ∈ range (r + 1 + 1), ((min (s + 1 + t + 1) (s + 3) : ℕ) : ℝ) * a (s + 1 + t)
            * a (n + 1 + 1 - (s + 1 + t)) :=
    wd_conv_split a w (y := s + 3) (p := s + 1) (m := r + 1 + 1) (n := n + 1 + 1)
      (by omega) (by omega) (by omega) (fun i hi => hfa i (by omega))
  have hB : ∑ i ∈ range (n + 1 + 1), ((min (i + 1) (s + 2) : ℕ) : ℝ) * b i * b (n + 1 - i)
      = ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 2 : ℕ) : ℝ)) * w l * b (n + 1 - l)
        + ∑ t ∈ range (r + 1), ((min (s + 1 + t + 1) (s + 2) : ℕ) : ℝ) * b (s + 1 + t)
            * b (n + 1 - (s + 1 + t)) :=
    wd_conv_split b w (y := s + 2) (p := s + 1) (m := r + 1) (n := n + 1)
      (by omega) (by omega) (by omega) (fun i hi => hfb i (by omega))
  have hD : ∑ i ∈ range (n + 1), ((min (i + 1) (s + 1) : ℕ) : ℝ) * d i * d (n - i)
      = ∑ l ∈ range (s + 1), ((l : ℝ) + 1 + ((s + 1 : ℕ) : ℝ)) * w l * d (n - l)
        + ∑ t ∈ range r, ((min (s + 1 + t + 1) (s + 1) : ℕ) : ℝ) * d (s + 1 + t)
            * d (n - (s + 1 + t)) :=
    wd_conv_split d w (y := s + 1) (p := s + 1) (m := r) (n := n)
      (by omega) (by omega) (by omega) (fun i hi => hfd i (by omega))
  -- the middle sums and the outer sums
  have hmA := wd_midA a s r n hn
  have hmB := wd_midB b s r n hn
  have hmD := wd_midD d s r n hn
  have hS1 := wd_outer a b d w s r n hn hw hT
  -- the middle part with the boundary terms
  have hbs : b s = d s := by rw [hfb s (by omega), hfd s (by omega)]
  have hTm : ∀ t, t ≤ r →
      0 ≤ ((s : ℝ) + 3) * a (s + t + 1 + 1) - 2 * ((s : ℝ) + 2) * b (s + t + 1)
        + ((s : ℝ) + 1) * d (s + t) := by
    intro t ht
    rcases Nat.eq_zero_or_pos t with h0 | hpos
    · subst h0
      have e0 : s + 0 = s := by omega
      rw [e0]
      exact hT0
    · have h := hT (s + t) ((s : ℝ) + 2) (by omega) (by omega) (le_refl _)
        (by linarith only [hs0])
      linarith only [h]
  have hmid := wd_mid_lower a b d w s r hw ha0 hb0 hab hdb hbs hEp hEm hTm hDg hbd
    (hfd s (by omega)) (hfa (s + 1) (by omega))
  have hcomb : ∑ t ∈ range (r + 1), (((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1)
            - 2 * (((s : ℝ) + 2) * b (s + t + 1) * b (s + (r - t) + 1))
            + ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1))
      = ∑ t ∈ range (r + 1), ((s : ℝ) + 3) * a (s + t + 1 + 1) * a (s + (r - t) + 1)
        - 2 * ∑ t ∈ range (r + 1), ((s : ℝ) + 2) * b (s + t + 1) * b (s + (r - t) + 1)
        + ∑ t ∈ range (r + 1), ((s : ℝ) + 1) * d (s + t) * d (s + (r - t) + 1) := by
    rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.mul_sum]
  linarith only [hA, hB, hD, hmA, hmB, hmD, hS1, hmid, hcomb]

/-! ### The tilted environments at the critical tilt -/

set_option maxHeartbeats 400000 in
/-- `(k-1) w_{k-2} ≤ k w_{k-1}` for the free weights `w_i = c_i x_k^i` (`k = s + 2`): the ratio is
`(k²/(k²-1))^(k-1) ≥ 1`. -/
private theorem wd_w_bd (s : ℕ) {k : ℕ} (hs : k = s + 2) :
    ((s : ℝ) + 1) * ccT (xcrit k) s ≤ ((s : ℝ) + 2) * ccT (xcrit k) (s + 1) := by
  subst hs
  have hx : 0 < xcrit (s + 2) := xcrit_pos (s + 2)
  have hs1 : (0 : ℝ) < (s : ℝ) + 1 := by positivity
  have hne1 : (s : ℝ) + 1 ≠ 0 := hs1.ne'
  have hpsi : xcrit (s + 2) * (1 + 1 / ((s + 2 : ℕ) : ℝ)) ^ (s + 2 - 1) = 1 :=
    xcrit_mul_psi (by omega)
  have eb : s + 2 - 1 = s + 1 := by omega
  rw [eb] at hpsi
  have hq : ((s : ℝ) + 1) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) = (s : ℝ) + 2 := by
    push_cast
    field
  have hR : (1 : ℝ) + 1 / ((s + 2 : ℕ) : ℝ) ≤ 1 + 1 / ((s + 1 : ℕ) : ℝ) := by
    have h1 : (0 : ℝ) < ((s + 1 : ℕ) : ℝ) := by positivity
    have h2 : ((s + 1 : ℕ) : ℝ) ≤ ((s + 2 : ℕ) : ℝ) := by
      exact_mod_cast (by omega : s + 1 ≤ s + 2)
    have h3 := one_div_le_one_div_of_le h1 h2
    linarith only [h3]
  have hR0 : (0 : ℝ) ≤ 1 + 1 / ((s + 2 : ℕ) : ℝ) := by positivity
  have hpow : (1 + 1 / ((s + 2 : ℕ) : ℝ)) ^ (s + 1) ≤ (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ (s + 1) :=
    pow_le_pow_left₀ hR0 hR (s + 1)
  have h1 : 1 ≤ xcrit (s + 2) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ (s + 1) := by
    calc (1 : ℝ) = xcrit (s + 2) * (1 + 1 / ((s + 2 : ℕ) : ℝ)) ^ (s + 1) := hpsi.symm
      _ ≤ xcrit (s + 2) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ (s + 1) :=
          mul_le_mul_of_nonneg_left hpow hx.le
  have hW0 : 0 ≤ ccT (xcrit (s + 2)) s := (ccT_pos hx s).le
  have h2 : ((s : ℝ) + 1) * 1 * ccT (xcrit (s + 2)) s
      ≤ ((s : ℝ) + 1) * (xcrit (s + 2) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ (s + 1))
        * ccT (xcrit (s + 2)) s :=
    mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left h1 hs1.le) hW0
  rw [ccT_succ, ← hq]
  calc ((s : ℝ) + 1) * ccT (xcrit (s + 2)) s
      = ((s : ℝ) + 1) * 1 * ccT (xcrit (s + 2)) s := by ring
    _ ≤ ((s : ℝ) + 1) * (xcrit (s + 2) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ (s + 1))
          * ccT (xcrit (s + 2)) s := h2
    _ = ((s : ℝ) + 1) * (1 + 1 / ((s + 1 : ℕ) : ℝ))
          * (xcrit (s + 2) * (1 + 1 / ((s + 1 : ℕ) : ℝ)) ^ s * ccT (xcrit (s + 2)) s) := by
        ring

/-- Diagonal monotonicity at the critical tilt: `zrT y n ≤ zrT (y+1) (n+1)` from the size `k - 1`
on (`zr_diag_mono` and `w_n ≤ w_{n+1}`).  These are `e⁺ ≥ 0` (`y = k`) and `e⁻ ≥ 0`
(`y = k - 1`). -/
private theorem wd_zrT_diag_le {k y n : ℕ} (hk : 1 ≤ k) (hy : 1 ≤ y) (hn : k ≤ n + 1) :
    zrT y (xcrit k) n ≤ zrT (y + 1) (xcrit k) (n + 1) := by
  have hx : 0 < xcrit k := xcrit_pos k
  have hcc : cc n * xcrit k ^ n ≤ cc (n + 1) * xcrit k ^ (n + 1) := ccT_le_succ hk hn
  have hd := zr_diag_mono hy n
  rw [div_le_div_iff₀ (cc_pos n) (cc_pos (n + 1))] at hd
  have hz : 0 ≤ zr (y + 1) (n + 1) := zr_nonneg _ _
  have hxn : 0 ≤ xcrit k ^ n := pow_nonneg hx.le n
  have hc1 : 0 < cc (n + 1) := cc_pos (n + 1)
  have h1 : zr y n * xcrit k ^ n * cc (n + 1)
      ≤ zr (y + 1) (n + 1) * xcrit k ^ (n + 1) * cc (n + 1) := by
    calc zr y n * xcrit k ^ n * cc (n + 1) = (zr y n * cc (n + 1)) * xcrit k ^ n := by ring
      _ ≤ (zr (y + 1) (n + 1) * cc n) * xcrit k ^ n := mul_le_mul_of_nonneg_right hd hxn
      _ = zr (y + 1) (n + 1) * (cc n * xcrit k ^ n) := by ring
      _ ≤ zr (y + 1) (n + 1) * (cc (n + 1) * xcrit k ^ (n + 1)) :=
          mul_le_mul_of_nonneg_left hcc hz
      _ = zr (y + 1) (n + 1) * xcrit k ^ (n + 1) * cc (n + 1) := by ring
  rw [zrT, zrT]
  exact le_of_mul_le_mul_right h1 hc1

/-- The tilted second difference of the column: `η_n = a_n - 2 b_n + d_n`. -/
private theorem wd_dq_tilt {k : ℕ} (hk : 2 ≤ k) (x : ℝ) (n : ℕ) :
    dq k n * x ^ n = zrT (k + 1) x n - 2 * zrT k x n + zrT (k - 1) x n := by
  have h1 := bq_eq (show 1 ≤ k by omega) n
  have h2 := bq_eq (show 1 ≤ k - 1 by omega) n
  rw [Nat.sub_add_cancel (show 1 ≤ k by omega)] at h2
  rw [dq, h1, h2, zrT, zrT, zrT]
  ring

/-! ### Weighted convexity with the identity weight -/

set_option maxHeartbeats 1000000 in
/-- **Weighted diagonal convexity beyond the first layer.**  For `k ≥ 7` and every
`N = M + 1 ≥ 2k - 1`: `Δ_id(N) = (N+1) a_{N+1} - 2N b_N + (N-1) d_{N-1} ≥ 0`. -/
theorem DeltaId_nonneg {k : ℕ} (hk : 7 ≤ k) : ∀ M, 2 * k - 1 ≤ M + 1 →
    0 ≤ ((M : ℝ) + 2) * zrT (k + 1) (xcrit k) (M + 1 + 1)
      - 2 * ((M : ℝ) + 1) * zrT k (xcrit k) (M + 1) + (M : ℝ) * zrT (k - 1) (xcrit k) M := by
  intro M
  induction M using Nat.strong_induction_on with
  | _ M ih =>
    intro hM
    have hx : 0 < xcrit k := xcrit_pos k
    -- `k = s + 2`, `M = n + 1`, `n = 2s + r + 1`
    obtain ⟨s, hs⟩ : ∃ s, k = s + 2 := ⟨k - 2, by omega⟩
    obtain ⟨n, rfl⟩ : ∃ n, M = n + 1 := ⟨M - 1, by omega⟩
    obtain ⟨r, hn⟩ : ∃ r, n = 2 * s + r + 1 := ⟨n - (2 * s + 1), by omega⟩
    have hk1 : 1 ≤ k := by omega
    have hs0 : (0 : ℝ) ≤ (s : ℝ) := Nat.cast_nonneg s
    have hkr : (k : ℝ) = (s : ℝ) + 2 := by
      rw [hs]
      push_cast
      ring
    -- signs and order
    have hw' : ∀ i, 0 ≤ ccT (xcrit k) i := fun i => (ccT_pos hx i).le
    have ha0' : ∀ i, 0 ≤ zrT (k + 1) (xcrit k) i := fun i => zrT_nonneg (k + 1) hx.le i
    have hb0' : ∀ i, 0 ≤ zrT k (xcrit k) i := fun i => zrT_nonneg k hx.le i
    have hab' : ∀ i, zrT k (xcrit k) i ≤ zrT (k + 1) (xcrit k) i :=
      fun i => zrT_le_zrT (Nat.le_succ k) hx.le i
    have hdb' : ∀ i, zrT (k - 1) (xcrit k) i ≤ zrT k (xcrit k) i :=
      fun i => zrT_le_zrT (Nat.sub_le k 1) hx.le i
    -- free ranges
    have hfa' : ∀ i, i ≤ s + 1 → zrT (k + 1) (xcrit k) i = ccT (xcrit k) i :=
      fun i hi => zrT_eq_ccT (by omega) (xcrit k) (by omega)
    have hfb' : ∀ i, i ≤ s + 1 → zrT k (xcrit k) i = ccT (xcrit k) i :=
      fun i hi => zrT_eq_ccT (by omega) (xcrit k) (by omega)
    have hfd' : ∀ i, i ≤ s + 1 → zrT (k - 1) (xcrit k) i = ccT (xcrit k) i :=
      fun i hi => zrT_eq_ccT (by omega) (xcrit k) (by omega)
    -- `e⁺ ≥ 0` and `e⁻ ≥ 0`
    have hEp' : ∀ i, s + 1 ≤ i → zrT k (xcrit k) i ≤ zrT (k + 1) (xcrit k) (i + 1) :=
      fun i hi => wd_zrT_diag_le hk1 hk1 (by omega)
    have hEm' : ∀ i, s + 1 ≤ i → zrT (k - 1) (xcrit k) i ≤ zrT k (xcrit k) (i + 1) := by
      intro i hi
      have h := wd_zrT_diag_le (k := k) (y := k - 1) (n := i) hk1 (by omega) (by omega)
      rw [Nat.sub_add_cancel hk1] at h
      exact h
    -- `(c+1) a_{i+2} - 2c b_{i+1} + (c-1) d_i ≥ 0` below the size `N`
    have hT' : ∀ (i : ℕ) (c : ℝ), s + 1 ≤ i → i ≤ n → (s : ℝ) + 2 ≤ c → c ≤ 2 * (s : ℝ) + 3 →
        0 ≤ (c + 1) * zrT (k + 1) (xcrit k) (i + 1 + 1) - 2 * c * zrT k (xcrit k) (i + 1)
            + (c - 1) * zrT (k - 1) (xcrit k) i := by
      intro i c hi1 hi2 hc1 hc2
      by_cases hi : i + 1 ≤ 2 * k - 2
      · -- the first layer
        exact FirstLayer.zrT_weak_requirement hk (by omega) hi (by linarith only [hkr, hc1])
      · -- from `Δ_id(i+1) ≥ 0`:
        -- `(i+1) [(c+1) a - 2c b + (c-1) d] = c Δ_id(i+1) + (i+1-c) (a - d)`
        have hm := ih i (by omega) (by omega)
        have hE : zrT (k - 1) (xcrit k) i ≤ zrT (k + 1) (xcrit k) (i + 1 + 1) :=
          le_trans (hEm' i hi1) (hEp' (i + 1) (by omega))
        have hik : 2 * (k : ℝ) ≤ (i : ℝ) + 2 := by
          exact_mod_cast (show 2 * k ≤ i + 2 by omega)
        have hi0 : (0 : ℝ) < (i : ℝ) + 1 := by positivity
        have hc0 : (0 : ℝ) ≤ c := by linarith only [hs0, hc1]
        have hic : 0 ≤ (i : ℝ) + 1 - c := by linarith only [hik, hkr, hc2]
        have hmul : 0 ≤ ((i : ℝ) + 1) * ((c + 1) * zrT (k + 1) (xcrit k) (i + 1 + 1)
            - 2 * c * zrT k (xcrit k) (i + 1) + (c - 1) * zrT (k - 1) (xcrit k) i) := by
          linarith only [mul_nonneg hc0 hm, mul_nonneg hic (sub_nonneg.mpr hE)]
        exact nonneg_of_mul_nonneg_right hmul hi0
    -- the same inequality at the size `k - 1`, with `c = k`
    have hT0' : 0 ≤ ((s : ℝ) + 3) * zrT (k + 1) (xcrit k) (s + 1 + 1)
        - 2 * ((s : ℝ) + 2) * zrT k (xcrit k) (s + 1)
        + ((s : ℝ) + 1) * zrT (k - 1) (xcrit k) s := by
      rw [zrT_eq_ccT (y := k + 1) (N := s + 1 + 1) (by omega) (xcrit k) (by omega),
        zrT_eq_ccT (y := k) (N := s + 1) hk1 (xcrit k) (by omega),
        zrT_eq_ccT (y := k - 1) (N := s) (by omega) (xcrit k) (by omega)]
      have h1 := ccT_le_succ (k := k) (n := s + 1) hk1 (by omega)
      have h2 := ccT_succ_le (k := k) (n := s) (by omega)
      have hs3 : (0 : ℝ) ≤ (s : ℝ) + 3 := by linarith only [hs0]
      have hs1 : (0 : ℝ) ≤ (s : ℝ) + 1 := by linarith only [hs0]
      linarith only [mul_le_mul_of_nonneg_left h1 hs3, mul_le_mul_of_nonneg_left h2 hs1]
    -- the diagonal lower bound
    have hDg' : ∀ j, ((s : ℝ) + 2) * (zrT k (xcrit k) j - zrT (k - 1) (xcrit k) j)
        ≤ ((s : ℝ) + 3) * (zrT (k + 1) (xcrit k) (j + 1) - zrT k (xcrit k) (j + 1)) := by
      intro j
      have h := Ut_diag_lower (show 2 ≤ k by omega) (show 1 ≤ j + 1 by omega)
      rw [Nat.add_sub_cancel, Ut, Ut, Nat.add_sub_cancel, hkr] at h
      linarith only [h]
    have hcore := wd_core_nonneg (zrT (k + 1) (xcrit k)) (zrT k (xcrit k))
      (zrT (k - 1) (xcrit k)) (ccT (xcrit k)) s r n (k + 1) k (k - 1) hn (by omega) hs
      (by omega) hw' ha0' hb0' hab' hdb' hfa' hfb' hfd' hEp' hEm' hT' hT0' hDg' (wd_w_bd s hs)
    -- the three last-car recursions
    have ha_rec := zrT_succ (y := k + 1) (by omega) (xcrit k) (n + 1 + 1)
    have hb_rec := zrT_succ (y := k) hk1 (xcrit k) (n + 1)
    have hd_rec := zrT_succ (y := k - 1) (by omega) (xcrit k) n
    have c2 : ((n + 1 + 1 : ℕ) : ℝ) = (n : ℝ) + 2 := by push_cast; ring
    have c1 : ((n + 1 : ℕ) : ℝ) = (n : ℝ) + 1 := by push_cast; ring
    rw [c2] at ha_rec
    rw [c1] at hb_rec ⊢
    linarith only [mul_nonneg hx.le hcore, ha_rec, hb_rec, hd_rec]

/-! ### Weighted convexity with the weight `Ψ′`, and the weighted debt -/

set_option maxHeartbeats 400000 in
/-- **Weighted diagonal convexity with the weight `Ψ′`**:
`Δ_{Ψ′}(N) = Ψ′(N+1) a_{N+1} - 2Ψ′(N) b_N + Ψ′(N-1) d_{N-1} ≥ 0` for `N ≥ k`, `k ≥ 7`
(`N = M + 1`). -/
theorem DeltaPsi_nonneg {k : ℕ} (hk : 7 ≤ k) (M : ℕ) (hM : k ≤ M + 1) :
    0 ≤ PsiW k (M + 1 + 1) * zrT (k + 1) (xcrit k) (M + 1 + 1)
        - 2 * PsiW k (M + 1) * zrT k (xcrit k) (M + 1) + PsiW k M * zrT (k - 1) (xcrit k) M := by
  have hx : 0 < xcrit k := xcrit_pos k
  have hk1 : 1 ≤ k := by omega
  have hd0 : 0 ≤ zrT (k - 1) (xcrit k) M := zrT_nonneg (k - 1) hx.le M
  by_cases h1 : M + 1 ≤ 2 * k - 2
  · -- the three weights are `2k - 1`
    rw [PsiW_low (k := k) (N := M + 1 + 1) hk1 (by omega),
      PsiW_low (k := k) (N := M + 1) hk1 (by omega), PsiW_low (k := k) (N := M) hk1 (by omega)]
    have h := FirstLayer.zrT_diag_convex hk hM h1
    have hk7 : (7 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
    have hp : (0 : ℝ) ≤ 2 * (k : ℝ) - 1 := by linarith only [hk7]
    linarith only [mul_nonneg hp h]
  · have hId := DeltaId_nonneg hk M (by omega)
    have c1 : ((M + 1 : ℕ) : ℝ) = (M : ℝ) + 1 := by push_cast; ring
    have c2 : ((M + 1 + 1 : ℕ) : ℝ) = (M : ℝ) + 2 := by push_cast; ring
    rw [PsiW_of_ge (k := k) (N := M + 1 + 1) (by omega),
      PsiW_of_ge (k := k) (N := M + 1) (by omega), c2, c1]
    by_cases h2 : M + 1 = 2 * k - 1
    · -- `N = 2k - 1`: `Ψ′(N-1) = 2k - 1 = N`
      have hMk : (M : ℝ) + 1 + 1 = 2 * (k : ℝ) := by
        have h3 : M + 1 + 1 = 2 * k := by omega
        exact_mod_cast h3
      rw [PsiW_low (k := k) (N := M) hk1 (by omega), ← hMk]
      linarith only [hId, hd0]
    · -- `N ≥ 2k`
      rw [PsiW_of_ge (k := k) (N := M) (by omega)]
      linarith only [hId]

set_option maxHeartbeats 400000 in
/-- **The weighted debt** in the form of a nonnegative quantity: the weighted sum of `η`, corrected
by the boundary terms, is a sum of the nonnegative `Δ_{Ψ′}(N)`, `k ≤ N < J`. -/
private theorem wd_lemmaB {k : ℕ} (hk : 7 ≤ k) :
    ∀ J, k ≤ J →
      0 ≤ ∑ n ∈ Icc k J, PsiW k n * (dq k n * xcrit k ^ n) + PsiW k J * Ut k (xcrit k) J
          + PsiW k (J - 1) * Ut k (xcrit k) (J - 1) - PsiW k (J - 1) * zrT k (xcrit k) (J - 1)
          + PsiW k J * zrT k (xcrit k) J := by
  intro J hJ
  have hx : 0 < xcrit k := xcrit_pos k
  have hk1 : 1 ≤ k := by omega
  have hk2 : 2 ≤ k := by omega
  induction J, hJ using Nat.le_induction with
  | base =>
    have e : k - 1 + 1 = k := Nat.sub_add_cancel hk1
    have h1 : zrT k (xcrit k) (k - 1) ≤ zrT (k + 1) (xcrit k) k := by
      have h := wd_zrT_diag_le (k := k) (y := k) (n := k - 1) hk1 hk1 (by omega)
      rw [e] at h
      exact h
    have h2 : zrT (k - 1) (xcrit k) (k - 1) ≤ zrT k (xcrit k) (k - 1) :=
      zrT_le_zrT (Nat.sub_le k 1) hx.le (k - 1)
    have hk7 : (7 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
    have hp : (0 : ℝ) ≤ 2 * (k : ℝ) - 1 := by linarith only [hk7]
    rw [Finset.Icc_self, Finset.sum_singleton, wd_dq_tilt hk2 (xcrit k) k, Ut, Ut,
      PsiW_low (k := k) (N := k) hk1 (by omega), PsiW_low (k := k) (N := k - 1) hk1 (by omega)]
    linarith only [mul_nonneg hp (sub_nonneg.mpr (le_trans h2 h1))]
  | succ J hJ ih =>
    have hJ1 : 1 ≤ J := by omega
    have hDel := DeltaPsi_nonneg hk (J - 1) (by omega)
    rw [Nat.sub_add_cancel hJ1] at hDel
    have hsum : ∑ n ∈ Icc k (J + 1), PsiW k n * (dq k n * xcrit k ^ n)
        = ∑ n ∈ Icc k J, PsiW k n * (dq k n * xcrit k ^ n)
          + PsiW k (J + 1) * (dq k (J + 1) * xcrit k ^ (J + 1)) :=
      Finset.sum_Icc_succ_top (by omega) _
    rw [hsum, Nat.add_sub_cancel, wd_dq_tilt hk2 (xcrit k) (J + 1), Ut, Ut]
    rw [Ut, Ut] at ih
    linarith only [ih, hDel]

/-- **The weighted debt.**  For `k ≥ 7` and `J ≥ k`,
`∑_{n=k}^{J} Ψ′(n) η_n ≥ -(Ψ′(J) U_J + Ψ′(J-1) U_{J-1} + (Ψ′(J) - Ψ′(J-1)) b_J)`. -/
theorem weighted_debt {k : ℕ} (hk : 7 ≤ k) (J : ℕ) (hJ : k ≤ J) :
    -(PsiW k J * Ut k (xcrit k) J + PsiW k (J - 1) * Ut k (xcrit k) (J - 1)
        + (PsiW k J - PsiW k (J - 1)) * zrT k (xcrit k) J)
      ≤ ∑ n ∈ Finset.Icc k J, PsiW k n * (dq k n * xcrit k ^ n) := by
  have hB := wd_lemmaB hk J hJ
  have h1 : zrT k (xcrit k) J ≤ zrT k (xcrit k) (J - 1) := by
    have h := zrT_anti_crit (show 2 ≤ k by omega) (J - 1)
    rw [Nat.sub_add_cancel (by omega : 1 ≤ J)] at h
    exact h
  linarith only [hB, mul_nonneg (PsiW_nonneg k (J - 1)) (sub_nonneg.mpr h1)]

end Parking