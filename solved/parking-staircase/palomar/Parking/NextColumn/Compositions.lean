module

public import Parking.Cayley.Basic
public import Parking.NextColumn.BirthdayLaw
public import Mathlib.Analysis.Real.Sqrt

/-!
# Compositions with Cayley weights: definitions

A composition of `m` is a way of cutting a segment of length `m` into parts; a cut point is one of
`1, …, m-1`.  Its weight for a cut profile `f` is `∏_{parts γ} a_γ · ∏_{cut points s} f s`
(`a = cay`).

* `Vc f q m` : total weight of the compositions of `m` with exactly `q` parts.
* `Lam f m`  : total weight of all compositions of `m`.
* `thr y N`  : the threshold profile `s ↦ y/(N-s)`; `Lam (thr y N) m` is the chain sum `Λ_m(y;N)`.
* `Tq m q`, `tau m h`, `muh r h` : the homogeneous case (all cut factors `1`, resp. `h`).
* `Pb`, `sbirth`, `Dbirth` (defined in `Parking.NextColumn.BirthdayLaw`) : the birthday law
  `Pr(Q ≥ j) = (m)_j/m^j`, its mean `s_m`, and `D_m = E Q(Q-1)(Q-2) / E Q(Q-1)`.
* `mu0`, `Gfun` : the explicit lower bound for the mean number of cuts and the criterion function
  `𝖦`.

The rest of the file contains the elementary facts about `Vc` and `Lam`: vanishing, positivity,
monotonicity and homogeneity in the profile, and the recursions on the first and on the last part.
-/

@[expose] public section

namespace Parking

open Finset

/-- Total weight of the compositions of `m` with exactly `q` parts, for the cut profile `f`
(last-part recursion). -/
noncomputable def Vc (f : ℕ → ℝ) : ℕ → ℕ → ℝ
  | 0, _ => 0
  | 1, m => cay m
  | (q + 2), m => ∑ s ∈ Ioo 0 m, Vc f (q + 1) s * f s * cay (m - s)

/-- Total weight of all compositions of `m` for the cut profile `f`. -/
noncomputable def Lam (f : ℕ → ℝ) (m : ℕ) : ℝ := ∑ q ∈ Icc 1 m, Vc f q m

/-- Threshold profile `λ_s = y/(N-s)`. -/
noncomputable def thr (y N : ℝ) : ℕ → ℝ := fun s => y / (N - s)

/-- `T_{m,q}`: total `∏ a_part` weight of the compositions of `m` with `q` parts. -/
noncomputable def Tq (m q : ℕ) : ℝ := Vc (fun _ => 1) q m

/-- `τ_m(h) = ∑_q T_{m,q} h^(q-1)`. -/
noncomputable def tau (m : ℕ) (h : ℝ) : ℝ := Lam (fun _ => h) m

/-- Mean number of cuts `E_h[Q-1]` under the homogeneous law on the compositions of `r`. -/
noncomputable def muh (r : ℕ) (h : ℝ) : ℝ :=
  (∑ q ∈ Icc 1 r, ((q : ℝ) - 1) * (Tq r q * h ^ (q - 1))) / tau r h

/-- `μ_0(X) = (√((4+X)² + 12(r-1)) - (4+X))/3`. -/
noncomputable def mu0 (r : ℕ) (X : ℝ) : ℝ :=
  (Real.sqrt ((4 + X) ^ 2 + 12 * ((r : ℝ) - 1)) - (4 + X)) / 3

/-- The criterion function `𝖦(r,k)`. -/
noncomputable def Gfun (r k : ℕ) : ℝ :=
  (k : ℝ) * (1 / (2 * (r : ℝ)) - 1 / (3 * (r : ℝ) ^ 2)) - 5 / 2
    + 1 / 2 * mu0 r ((r : ℝ) * (r + 1) / ((k : ℝ) - 1))
    + 2 * (1 - 1 / (k : ℝ)) * mu0 r ((r : ℝ) * (r + 2) / (2 * (k : ℝ)))
    - (k : ℝ) / ((k : ℝ) - 1) * Dbirth r

/-! ### Basic facts about `thr` -/

/-- The threshold profile with parameters $y$ and $N$ takes the value $y/(N-s)$ at $s$; this is its
definition, stated as an equation. -/
theorem thr_apply (y N : ℝ) (s : ℕ) : thr y N s = y / (N - s) := rfl

/-- The threshold profile is nonnegative at the points `s ≤ N`. -/
theorem thr_nonneg {y N : ℝ} {s : ℕ} (hy : 0 ≤ y) (hs : (s : ℝ) ≤ N) : 0 ≤ thr y N s :=
  div_nonneg hy (sub_nonneg.2 hs)

/-! ### Basic facts about `Vc` and `Lam` -/

private theorem Vc_zero (f : ℕ → ℝ) (m : ℕ) : Vc f 0 m = 0 := by simp [Vc]

/-- The only composition of $m$ with one part has the weight $a_m = m^{m-1}/m!$, whatever the cut
profile: $V_1(m;f) = a_m$. -/
theorem Vc_one (f : ℕ → ℝ) (m : ℕ) : Vc f 1 m = cay m := by simp [Vc]

/-- The weight of the compositions of $m$ with $q+2$ parts is obtained from the weights with $q+1$
parts by removing the last part: $V_{q+2}(m;f) = \sum_{0<s<m} V_{q+1}(s;f)\,f(s)\,a_{m-s}$. -/
theorem Vc_succ_succ (f : ℕ → ℝ) (q m : ℕ) :
    Vc f (q + 2) m = ∑ s ∈ Ioo 0 m, Vc f (q + 1) s * f s * cay (m - s) := by
  simp [Vc]

/-- No composition of `m` has more than `m` parts. -/
theorem Vc_eq_zero_of_lt (f : ℕ → ℝ) {q m : ℕ} (h : m < q) : Vc f q m = 0 := by
  induction q generalizing m with
  | zero => exact Vc_zero f m
  | succ q ih =>
    cases q with
    | zero =>
      have hm : m = 0 := by omega
      rw [hm]
      exact (Vc_one f 0).trans cay_zero
    | succ q =>
      show Vc f (q + 2) m = 0
      rw [Vc_succ_succ f q m]
      apply Finset.sum_eq_zero
      intro s hs
      rw [mem_Ioo] at hs
      have h0 : Vc f (q + 1) s = 0 := @ih s (by omega)
      rw [h0, zero_mul, zero_mul]

/-- For a cut profile that is nonnegative at the cut points $1, \dots, m-1$, the weight $V_q(m;f)$
of the compositions of $m$ with $q$ parts is nonnegative. -/
theorem Vc_nonneg {f : ℕ → ℝ} {m : ℕ} (hf : ∀ s ∈ Ioo 0 m, 0 ≤ f s) (q : ℕ) : 0 ≤ Vc f q m := by
  induction q generalizing m with
  | zero => exact le_of_eq (Vc_zero f m).symm
  | succ q ih =>
    cases q with
    | zero =>
      show 0 ≤ Vc f 1 m
      rw [Vc_one]
      exact cay_nonneg m
    | succ q =>
      show 0 ≤ Vc f (q + 2) m
      rw [Vc_succ_succ f q m]
      apply Finset.sum_nonneg
      intro s hs
      have hs' := mem_Ioo.mp hs
      have h1 : 0 ≤ Vc f (q + 1) s :=
        @ih s (fun u hu => hf u (by rw [mem_Ioo] at hu ⊢; omega))
      exact mul_nonneg (mul_nonneg h1 (hf s hs)) (cay_nonneg _)

/-- `Vc` only depends on the profile at the cut points `1, …, m-1`. -/
theorem Vc_congr {f g : ℕ → ℝ} {m : ℕ} (hfg : ∀ s ∈ Ioo 0 m, f s = g s) (q : ℕ) :
    Vc f q m = Vc g q m := by
  induction q generalizing m with
  | zero => exact (Vc_zero f m).trans (Vc_zero g m).symm
  | succ q ih =>
    cases q with
    | zero => exact (Vc_one f m).trans (Vc_one g m).symm
    | succ q =>
      show Vc f (q + 2) m = Vc g (q + 2) m
      rw [Vc_succ_succ f q m, Vc_succ_succ g q m]
      apply Finset.sum_congr rfl
      intro s hs
      have hs' := mem_Ioo.mp hs
      have h1 : Vc f (q + 1) s = Vc g (q + 1) s :=
        @ih s (fun u hu => hfg u (by rw [mem_Ioo] at hu ⊢; omega))
      rw [h1, hfg s hs]

/-- Homogeneity in the profile: each of the `q-1` cut points carries one factor. -/
private theorem Vc_smul (f : ℕ → ℝ) (y : ℝ) :
    ∀ q m : ℕ, Vc (fun s => y * f s) q m = y ^ (q - 1) * Vc f q m
  | 0, m => by rw [Vc_zero, Vc_zero, mul_zero]
  | 1, m => by rw [Vc_one, Vc_one, Nat.sub_self, pow_zero, one_mul]
  | q + 2, m => by
    have e1 : q + 2 - 1 = q + 1 := by omega
    have e2 : q + 1 - 1 = q := by omega
    rw [Vc_succ_succ (fun s => y * f s) q m, Vc_succ_succ f q m, Finset.mul_sum, e1]
    refine Finset.sum_congr rfl fun s _ => ?_
    rw [Vc_smul f y (q + 1) s, e2]
    ring

/-- `V_{m,q}` for the threshold profile `y/(N-s)` is `y^(q-1)` times its value for `1/(N-s)`. -/
theorem Vc_thr (y N : ℝ) (q m : ℕ) : Vc (thr y N) q m = y ^ (q - 1) * Vc (thr 1 N) q m := by
  have h : thr y N = fun s => y * thr 1 N s := by
    funext s
    simp only [thr]
    ring
  rw [h]
  exact Vc_smul (thr 1 N) y q m

/-- With positive cut factors, the compositions of `m` with `q` parts have positive total weight
whenever `1 ≤ q ≤ m`. -/
theorem Vc_pos {f : ℕ → ℝ} :
    ∀ {q m : ℕ}, (∀ s ∈ Ioo 0 m, 0 < f s) → 1 ≤ q → q ≤ m → 0 < Vc f q m
  | 0, _, _, h, _ => absurd h (by omega)
  | 1, m, _, _, h => by
    rw [Vc_one]
    exact cay_pos h
  | q + 2, m, hf, _, h => by
    have hm : q + 1 ∈ Ioo 0 m := mem_Ioo.2 ⟨by omega, by omega⟩
    have hsub : ∀ s ∈ Ioo 0 m, ∀ u ∈ Ioo 0 s, 0 < f u := fun s hs u hu =>
      hf u (mem_Ioo.2 ⟨(mem_Ioo.1 hu).1, lt_trans (mem_Ioo.1 hu).2 (mem_Ioo.1 hs).2⟩)
    rw [Vc_succ_succ]
    refine Finset.sum_pos' (fun s hs => ?_) ⟨q + 1, hm, ?_⟩
    · exact mul_nonneg
        (mul_nonneg (Vc_nonneg (fun u hu => (hsub s hs u hu).le) _) (hf s hs).le) (cay_nonneg _)
    · exact mul_pos (mul_pos (Vc_pos (hsub _ hm) (by omega) le_rfl) (hf _ hm))
        (cay_pos (by omega))

/-- Monotonicity in the profile. -/
private theorem Vc_mono {f g : ℕ → ℝ} {m : ℕ} (hf : ∀ s ∈ Ioo 0 m, 0 ≤ f s)
    (hfg : ∀ s ∈ Ioo 0 m, f s ≤ g s) (q : ℕ) : Vc f q m ≤ Vc g q m := by
  induction q generalizing m with
  | zero => exact le_of_eq ((Vc_zero f m).trans (Vc_zero g m).symm)
  | succ q ih =>
    cases q with
    | zero => exact le_of_eq ((Vc_one f m).trans (Vc_one g m).symm)
    | succ q =>
      show Vc f (q + 2) m ≤ Vc g (q + 2) m
      rw [Vc_succ_succ f q m, Vc_succ_succ g q m]
      apply Finset.sum_le_sum
      intro s hs
      have hs' := mem_Ioo.mp hs
      have hsub : ∀ u ∈ Ioo 0 s, u ∈ Ioo 0 m := by
        intro u hu
        rw [mem_Ioo] at hu ⊢
        omega
      have h1 : Vc f (q + 1) s ≤ Vc g (q + 1) s :=
        @ih s (fun u hu => hf u (hsub u hu)) (fun u hu => hfg u (hsub u hu))
      have h2 : 0 ≤ Vc f (q + 1) s := Vc_nonneg (fun u hu => hf u (hsub u hu)) (q + 1)
      exact mul_le_mul_of_nonneg_right
        (mul_le_mul h1 (hfg s hs) (hf s hs) (le_trans h2 h1)) (cay_nonneg _)

/-- Shifting the summation index of a sum over an open interval. -/
private theorem sum_Ioo_shift (F : ℕ → ℝ) (g m : ℕ) :
    ∑ s ∈ Ioo g m, F s = ∑ s ∈ Ioo 0 (m - g), F (g + s) := by
  refine Finset.sum_nbij' (fun s => s - g) (fun s => g + s) ?_ ?_ ?_ ?_ ?_
  · intro s hs
    simp only [mem_Ioo] at hs ⊢
    omega
  · intro s hs
    simp only [mem_Ioo] at hs ⊢
    omega
  · intro s hs
    simp only [mem_Ioo] at hs
    show g + (s - g) = s
    omega
  · intro s hs
    show g + s - g = s
    omega
  · intro s hs
    simp only [mem_Ioo] at hs
    show F s = F (g + (s - g))
    rw [show g + (s - g) = s by omega]

/-- First-part recursion for `Vc`. -/
private theorem Vc_first (f : ℕ → ℝ) (q m : ℕ) :
    Vc f (q + 2) m = ∑ g ∈ Ioo 0 m, cay g * f g * Vc (fun s => f (g + s)) (q + 1) (m - g) := by
  induction q generalizing m with
  | zero =>
    rw [Vc_succ_succ f 0 m]
    apply Finset.sum_congr rfl
    intro s _
    have h1 : Vc f (0 + 1) s = cay s := Vc_one f s
    have h2 : Vc (fun u => f (s + u)) (0 + 1) (m - s) = cay (m - s) := Vc_one _ _
    rw [h1, h2]
  | succ q ih =>
    rw [Vc_succ_succ f (q + 1) m]
    have h1 : ∀ s ∈ Ioo 0 m, Vc f (q + 1 + 1) s * f s * cay (m - s)
        = ∑ g ∈ Ioo 0 s,
            cay g * f g * Vc (fun u => f (g + u)) (q + 1) (s - g) * f s * cay (m - s) := by
      intro s _
      have ih' : Vc f (q + 1 + 1) s
          = ∑ g ∈ Ioo 0 s, cay g * f g * Vc (fun u => f (g + u)) (q + 1) (s - g) := ih s
      rw [ih', Finset.sum_mul, Finset.sum_mul]
    rw [Finset.sum_congr rfl h1]
    have h2 : ∀ g ∈ Ioo 0 m, cay g * f g * Vc (fun u => f (g + u)) (q + 1 + 1) (m - g)
        = ∑ s ∈ Ioo g m,
            cay g * f g * Vc (fun u => f (g + u)) (q + 1) (s - g) * f s * cay (m - s) := by
      intro g _
      have hV : Vc (fun u => f (g + u)) (q + 1 + 1) (m - g)
          = ∑ s ∈ Ioo 0 (m - g),
              Vc (fun u => f (g + u)) (q + 1) s * f (g + s) * cay (m - g - s) :=
        Vc_succ_succ (fun u => f (g + u)) q (m - g)
      rw [hV, Finset.mul_sum, sum_Ioo_shift _ g m]
      apply Finset.sum_congr rfl
      intro s _
      rw [show g + s - g = s by omega, show m - (g + s) = m - g - s by omega]
      ring
    rw [Finset.sum_congr rfl h2]
    exact Finset.sum_comm' (by intro x y; simp only [mem_Ioo]; omega)

private theorem Lam_zero (f : ℕ → ℝ) : Lam f 0 = 0 :=
  Finset.sum_eq_zero fun q hq => absurd (mem_Icc.1 hq) (by omega)

/-- `Lam f m` as a sum over `range n` for any `n ≥ m` (there are at most `m` parts). -/
private theorem Lam_eq_sum_range (f : ℕ → ℝ) {m n : ℕ} (h : m ≤ n) :
    Lam f m = ∑ q ∈ range n, Vc f (q + 1) m := by
  unfold Lam
  rw [sum_Icc_one_eq_range]
  refine Finset.sum_subset (Finset.range_subset_range.2 h) fun q _ hq => ?_
  rw [mem_range] at hq
  exact Vc_eq_zero_of_lt f (by omega)

/-- Last-cut recursion for `Lam`. -/
theorem Lam_last (f : ℕ → ℝ) (m : ℕ) :
    Lam f m = cay m + ∑ s ∈ Ioo 0 m, Lam f s * f s * cay (m - s) := by
  cases m with
  | zero => simp [Lam_zero]
  | succ m =>
    have h0 : Vc f (0 + 1) (m + 1) = cay (m + 1) := Vc_one f (m + 1)
    rw [Lam_eq_sum_range f (le_refl (m + 1)), Finset.sum_range_succ', h0, add_comm]
    congr 1
    have h1 : ∀ q ∈ range m, Vc f (q + 1 + 1) (m + 1)
        = ∑ s ∈ Ioo 0 (m + 1), Vc f (q + 1) s * f s * cay (m + 1 - s) :=
      fun q _ => Vc_succ_succ f q (m + 1)
    rw [Finset.sum_congr rfl h1, Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro s hs
    rw [mem_Ioo] at hs
    rw [Lam_eq_sum_range f (show s ≤ m by omega), Finset.sum_mul, Finset.sum_mul]

/-- First-part recursion for `Lam`. -/
theorem Lam_first (f : ℕ → ℝ) (m : ℕ) :
    Lam f m = cay m + ∑ g ∈ Ioo 0 m, cay g * f g * Lam (fun s => f (g + s)) (m - g) := by
  cases m with
  | zero => simp [Lam_zero]
  | succ m =>
    have h0 : Vc f (0 + 1) (m + 1) = cay (m + 1) := Vc_one f (m + 1)
    rw [Lam_eq_sum_range f (le_refl (m + 1)), Finset.sum_range_succ', h0, add_comm]
    congr 1
    have h1 : ∀ q ∈ range m, Vc f (q + 1 + 1) (m + 1)
        = ∑ g ∈ Ioo 0 (m + 1), cay g * f g * Vc (fun s => f (g + s)) (q + 1) (m + 1 - g) :=
      fun q _ => Vc_first f q (m + 1)
    rw [Finset.sum_congr rfl h1, Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro g hg
    rw [mem_Ioo] at hg
    rw [Lam_eq_sum_range (fun s => f (g + s)) (show m + 1 - g ≤ m by omega), Finset.mul_sum]

/-- Two cut profiles that agree at the points $1, \dots, m-1$ give the same total weight of the
compositions of $m$: $\Lambda_m[f] = \Lambda_m[g]$. -/
theorem Lam_congr {f g : ℕ → ℝ} {m : ℕ} (hfg : ∀ s ∈ Ioo 0 m, f s = g s) : Lam f m = Lam g m := by
  unfold Lam
  exact Finset.sum_congr rfl (fun q _ => Vc_congr hfg q)

/-- The total weight of the compositions of $m$ is monotone in a nonnegative cut profile: if $0 \le
f \le g$ at the cut points $1, \dots, m-1$, then $\Lambda_m[f] \le \Lambda_m[g]$. -/
theorem Lam_mono {f g : ℕ → ℝ} {m : ℕ} (hf : ∀ s ∈ Ioo 0 m, 0 ≤ f s)
    (hfg : ∀ s ∈ Ioo 0 m, f s ≤ g s) : Lam f m ≤ Lam g m := by
  unfold Lam
  exact Finset.sum_le_sum (fun q _ => Vc_mono hf hfg q)

private theorem Lam_pos {f : ℕ → ℝ} {m : ℕ} (hm : 1 ≤ m) (hf : ∀ s ∈ Ioo 0 m, 0 ≤ f s) :
    0 < Lam f m := by
  unfold Lam
  have h1 : Vc f 1 m ≤ ∑ q ∈ Icc 1 m, Vc f q m :=
    Finset.single_le_sum (f := fun q => Vc f q m) (fun q _ => Vc_nonneg hf q)
      (mem_Icc.mpr ⟨le_refl 1, hm⟩)
  rw [Vc_one] at h1
  exact lt_of_lt_of_le (cay_pos (by omega)) h1

/-- `Λ_m(y;N) = ∑_q y^(q-1) V_{m,q}` with `V_{m,q} = Vc (thr 1 N) q m`. -/
theorem Lam_thr (y N : ℝ) (m : ℕ) :
    Lam (thr y N) m = ∑ q ∈ Icc 1 m, y ^ (q - 1) * Vc (thr 1 N) q m := by
  unfold Lam
  exact Finset.sum_congr rfl fun q _ => Vc_thr y N q m

/-- `Λ_m(y;N) > 0` for `y ≥ 0` and `1 ≤ m ≤ N`. -/
theorem Lam_thr_pos {y N : ℝ} {m : ℕ} (hm : 1 ≤ m) (hy : 0 ≤ y) (hN : (m : ℝ) ≤ N) :
    0 < Lam (thr y N) m :=
  Lam_pos hm fun _ hs => thr_nonneg hy (le_trans (Nat.cast_le.2 (mem_Ioo.1 hs).2.le) hN)

/-- The total weight of the compositions of $m$ for the constant cut profile $h$ is $\tau_m(h) =
\sum_{q=1}^{m} T_{m,q}\, h^{q-1}$. -/
theorem tau_eq (m : ℕ) (h : ℝ) : tau m h = ∑ q ∈ Icc 1 m, Tq m q * h ^ (q - 1) := by
  unfold tau Lam Tq
  refine Finset.sum_congr rfl fun q _ => ?_
  have e := Vc_smul (fun _ : ℕ => (1 : ℝ)) h q m
  simp only [mul_one] at e
  rw [e, mul_comm]

end Parking
