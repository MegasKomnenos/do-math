module

public import Parking.LeftHalf.FirstLayer.DirectTerm
public import Parking.LeftHalf.FirstLayer.Recursion

/-!
# Property K of the kernel triple, and diagonal convexity in the first layer

Fix a column `k` and the critical tilt `x_k = xcrit k`, and write `u_N(c) = zrT c x_k N` for the
tilted environment of the threshold `c`, and `ω_N = ccT x_k N` for the tilted Cayley masses.

**Property K of the kernel triple** (`kernel_TK`).  For `k ≥ 7` and `0 ≤ ρ ≤ k-2` the diagonal
triple

  `(u_{k-1+ρ}(k-1), u_{k+ρ}(k), u_{k+1+ρ}(k+1))`

has property K at `k` (`TK`, `Parking/LeftHalf/FirstLayer/PropertyK.lean`).

The proof is an induction on the excess `ρ`.  For `ρ = 0` the triple is `(ω_{k-1}, ω_k, ω_{k+1})`
(`TK_ccT_top`).  For `ρ ≥ 1` the last-car recursion, divided by the size (`zrT_rec_Sdir`), is

  `u_{c+ρ}(c) = ∑_{i ≤ ρ-2} x ω_i · (c+i+1)/(c+ρ) · u_{c+ρ-1-i}(c) + S_ρ(c)`.

In the chain part each term is a diagonal triple of smaller excess times a factor
`(z+i+1)/(z+ρ)`, under which property K is preserved (`TK.mul_ratio`); the direct term `S_ρ(c)` has
property K by `Sdir_TK`, which is where `k ≥ 7` enters.

**Diagonal convexity in the first layer.**  Write `a_N = u_N(k+1)`, `b_N = u_N(k)`,
`d_N = u_N(k-1)`, and for a size `N` in the first layer put

  `DC(N) = a_{N+1} - 2 b_N + d_{N-1}`,   `e_N = a_{N+1} - d_{N-1}`.

Property K of a diagonal triple contains its convexity (`TK.convex`, the tilt `μ = 0`).  Read in
this way, `kernel_TK` gives two inequalities for the sizes `N` of the first layer, that is,
for `k ≥ 7` and `k ≤ N ≤ 2k-2`:

* `zrT_diag_convex` : `DC(N) ≥ 0`;
* `zrT_weak_requirement` : `c · DC(N) + e_N ≥ 0` for every real `c ≥ k`.  The weight `z ↦ z + β`
  (`β = c - k`) is the factor `(z+β)(z+0)/z` of `TK.mul_prod`, so property K passes from the
  kernel triple to the weighted kernel triple for every `β ≥ 0`.

Both are stated with `N = M + 1`.
-/

@[expose] public section

namespace Parking.FirstLayer
open Real Finset

/-! ### Property K of the kernel triple -/

/-- The last-car recursion at threshold `c` and excess `ρ = P + 1 ≤ c - 1`, divided by the size:
chain part plus direct term. -/
private theorem zrT_rec_Sdir {k c P : ℕ} (hP : P + 2 ≤ c) :
    zrT c (xcrit k) (c + (P + 1)) =
      ∑ i ∈ range P, xcrit k * ccT (xcrit k) i *
          (((c : ℝ) + ((i : ℝ) + 1)) / ((c : ℝ) + ((P : ℝ) + 1))) * zrT c (xcrit k) (c + (P - i)) +
        Sdir k (P + 1) c := by
  have hne : (c : ℝ) + ((P : ℝ) + 1) ≠ 0 := by positivity
  have hD : (c : ℝ) + P + 1 ≠ 0 := by positivity
  have hsplit := zrT_split (k := k) (c := c) (P := P) (by omega) (by omega)
  rw [direct_generic hP] at hsplit
  have hsum : (∑ i ∈ range P, xcrit k * ccT (xcrit k) i *
        (((c : ℝ) + ((i : ℝ) + 1)) / ((c : ℝ) + ((P : ℝ) + 1))) * zrT c (xcrit k) (c + (P - i))) *
        ((c : ℝ) + P + 1) =
      xcrit k * ∑ i ∈ range P, ((c : ℝ) + i + 1) * ccT (xcrit k) i
          * zrT c (xcrit k) (c + (P - i)) := by
    rw [Finset.sum_mul, Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    field_simp
    ring
  have hdir : Sdir k (P + 1) c * ((c : ℝ) + P + 1) =
      xcrit k * (((c : ℝ) + P + 1) * ccT (xcrit k) P * ccT (xcrit k) c +
        ((c : ℝ) + P + 2) / 2 * pairT k (P + 1) (c - P - 2)) := by
    unfold Sdir
    rw [show P + 1 - 1 = P by omega, show c - (P + 1) - 1 = c - P - 2 by omega, Nat.cast_add,
      Nat.cast_one]
    field_simp
    ring
  refine mul_right_cancel₀ hD ?_
  rw [show c + (P + 1) = c + P + 1 by omega, add_mul, hsum, hdir, ← mul_add, mul_comm]
  exact hsplit

/-- **Property K for the kernel masses.**  For `k ≥ 7` and `0 ≤ ρ ≤ k-2` the diagonal triple of
tilted kernel masses has property K at `k`. -/
theorem kernel_TK {k : ℕ} (hk : 7 ≤ k) : ∀ ρ : ℕ, ρ + 2 ≤ k →
    TK k (zrT (k - 1) (xcrit k) (k - 1 + ρ)) (zrT k (xcrit k) (k + ρ))
        (zrT (k + 1) (xcrit k) (k + 1 + ρ)) := by
  have hk1 : 1 ≤ k := by omega
  have hkr : (1 : ℝ) < k := by exact_mod_cast (by omega : 1 < k)
  intro ρ
  induction ρ using Nat.strong_induction_on with
  | _ ρ ih =>
    intro hρk
    rcases Nat.eq_zero_or_pos ρ with rfl | hpos
    · -- excess `0`: the triple is `(ω_{k-1}, ω_k, ω_{k+1})`
      show TK (k : ℝ) (zrT (k - 1) (xcrit k) (k - 1)) (zrT k (xcrit k) k)
          (zrT (k + 1) (xcrit k) (k + 1))
      rw [zrT_eq_ccT (y := k - 1) (by omega) (xcrit k) le_rfl,
          zrT_eq_ccT (y := k) hk1 (xcrit k) le_rfl,
        zrT_eq_ccT (y := k + 1) (by omega) (xcrit k) le_rfl]
      exact TK_ccT_top (by omega)
    · obtain ⟨P, rfl⟩ : ∃ P, ρ = P + 1 := ⟨ρ - 1, by omega⟩
      rw [zrT_rec_Sdir (k := k) (c := k - 1) (P := P) (by omega),
        zrT_rec_Sdir (k := k) (c := k) (P := P) (by omega),
        zrT_rec_Sdir (k := k) (c := k + 1) (P := P) (by omega)]
      refine TK.add ?_ (Sdir_TK hk (by omega) (by omega : P + 1 + (k - P - 3) + 2 = k))
      -- the chain part: the triples of smaller excess, each times a factor `(z+i+1)/(z+P+1)`
      refine TK.sum (range P) (k : ℝ) _ _ _ fun i hi => ?_
      rw [Finset.mem_range] at hi
      have hih := ih (P - i) (by omega) (by omega)
      have hiP : (i : ℝ) + 1 ≤ (P : ℝ) + 1 := by
        have : (i : ℝ) ≤ P := by exact_mod_cast hi.le
        linarith
      have hr := hih.mul_ratio hkr (zrT_nonneg _ (xcrit_pos k).le _) (α := (i : ℝ) + 1)
          (β := (P : ℝ) + 1)
        (by positivity) hiP
      have hs := hr.smul (r := xcrit k * ccT (xcrit k) i)
        (mul_nonneg (xcrit_pos k).le (ccT_pos (xcrit_pos k) i).le)
      have c1 : ((k - 1 : ℕ) : ℝ) = (k : ℝ) - 1 := by rw [Nat.cast_sub hk1, Nat.cast_one]
      have c2 : ((k + 1 : ℕ) : ℝ) = (k : ℝ) + 1 := by push_cast; ring
      simpa only [c1, c2, mul_assoc] using hs

/-! ### Diagonal convexity in the first layer -/

/-- **Diagonal convexity of the kernel masses in the first layer.**  For `k ≥ 7` and
`k ≤ N ≤ 2k-2` (`N = M + 1`), `a_{N+1} - 2 b_N + d_{N-1} ≥ 0`. -/
theorem zrT_diag_convex {k M : ℕ} (hk : 7 ≤ k) (hM1 : k ≤ M + 1) (hM2 : M + 1 ≤ 2 * k - 2) :
    0 ≤ zrT (k + 1) (xcrit k) (M + 1 + 1) - 2 * zrT k (xcrit k) (M + 1)
        + zrT (k - 1) (xcrit k) M := by
  have h := (kernel_TK hk (M + 1 - k) (by omega)).convex
  rw [show k - 1 + (M + 1 - k) = M by omega, show k + (M + 1 - k) = M + 1 by omega,
    show k + 1 + (M + 1 - k) = M + 1 + 1 by omega] at h
  linarith

/-- **The weighted diagonal convexity from the property K of the kernel masses.**  For `k ≥ 7`,
`k ≤ N ≤ 2k-2` (`N = M + 1`) and every real `c ≥ k`,
`(c+1) a_{N+1} - 2c b_N + (c-1) d_{N-1} ≥ 0`. -/
theorem zrT_weak_requirement {k M : ℕ} (hk : 7 ≤ k) (hM1 : k ≤ M + 1)
    (hM2 : M + 1 ≤ 2 * k - 2) {c : ℝ} (hc1 : (k : ℝ) ≤ c) :
    0 ≤ (c + 1) * zrT (k + 1) (xcrit k) (M + 1 + 1) - 2 * c * zrT k (xcrit k) (M + 1)
        + (c - 1) * zrT (k - 1) (xcrit k) M := by
  have hk1 : 1 ≤ k := by omega
  have hkr : (1 : ℝ) < k := by exact_mod_cast (by omega : 1 < k)
  have n1 : (k : ℝ) - 1 ≠ 0 := (by linarith : (0 : ℝ) < (k : ℝ) - 1).ne'
  have n2 : (k : ℝ) ≠ 0 := (by linarith : (0 : ℝ) < k).ne'
  have n3 : (k : ℝ) + 1 ≠ 0 := (by linarith : (0 : ℝ) < (k : ℝ) + 1).ne'
  -- the factor `z + β = (z+β)(z+0)/z` with `β = c - k`
  have h := ((kernel_TK hk (M + 1 - k) (by omega)).mul_prod hkr (zrT_nonneg _ (xcrit_pos k).le _)
    (a := c - k) (b := 0) (by linarith) le_rfl (by rw [mul_zero]; nlinarith)).convex
  have em : ((k : ℝ) - 1 + (c - k)) * ((k : ℝ) - 1 + 0) / ((k : ℝ) - 1) = c - 1 := by
    rw [add_zero, mul_div_cancel_right₀ _ n1]
    ring
  have e0 : ((k : ℝ) + (c - k)) * ((k : ℝ) + 0) / (k : ℝ) = c := by
    rw [add_zero, mul_div_cancel_right₀ _ n2]
    ring
  have ep : ((k : ℝ) + 1 + (c - k)) * ((k : ℝ) + 1 + 0) / ((k : ℝ) + 1) = c + 1 := by
    rw [add_zero, mul_div_cancel_right₀ _ n3]
    ring
  rw [em, e0, ep, show k - 1 + (M + 1 - k) = M by omega, show k + (M + 1 - k) = M + 1 by omega,
    show k + 1 + (M + 1 - k) = M + 1 + 1 by omega] at h
  linarith

end Parking.FirstLayer