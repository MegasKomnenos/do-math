import Parking.Tilt.Basic

/-!
# The critical tilt

The ratio of consecutive tilted Cayley masses is
`ccT x (j+1) / ccT x j = x (1 + 1/(j+1))^j` (`ccT_succ`), and `(1 + 1/i)^(i-1)` increases with `i`
(`psi_mono`).  The critical tilt of the column `k` is the tilt at which this ratio is one for
`j + 1 = k`:

  `xcrit k = (k/(k+1))^(k-1)`,   `xcrit k * (1 + 1/k)^(k-1) = 1`   (`xcrit_mul_psi`).

At `x = xcrit k` the tilted Cayley masses `ccT (xcrit k) n` therefore do not increase up to the
index `k` (`ccT_succ_le`) and do not decrease from the index `k - 1` on (`ccT_le_succ`); in
particular `ccT (xcrit k) k = ccT (xcrit k) (k - 1)`.  The tilted free prime kernel
`epsT (xcrit k) m` does not increase on `1 ≤ m ≤ k` (`epsT_succ_le`).
-/

namespace Parking

open Finset

/-- The critical tilt `x_k = (k/(k+1))^(k-1)`. -/
noncomputable def xcrit (k : ℕ) : ℝ := ((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)

/-- The critical tilt $x_k = (k/(k+1))^{k-1}$ is positive for every natural number $k$. -/
theorem xcrit_pos (k : ℕ) : 0 < xcrit k := by
  rcases Nat.eq_zero_or_pos k with rfl | hk
  · simp [xcrit]
  · have h : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
    rw [xcrit]
    exact pow_pos (div_pos h (by linarith)) _

/-- The critical tilt $x_k = (k/(k+1))^{k-1}$ is at most $1$ for every natural number $k$. -/
theorem xcrit_le_one (k : ℕ) : xcrit k ≤ 1 := by
  have h0 : (0 : ℝ) ≤ (k : ℝ) := Nat.cast_nonneg k
  have h1 : (0 : ℝ) < (k : ℝ) + 1 := by linarith
  have h2 : (k : ℝ) / ((k : ℝ) + 1) ≤ 1 := by
    rw [div_le_one h1]
    linarith
  rw [xcrit]
  exact pow_le_one₀ (div_nonneg h0 h1.le) h2

/-- `x_k (1 + 1/k)^(k-1) = 1`. -/
theorem xcrit_mul_psi {k : ℕ} (hk : 1 ≤ k) : xcrit k * (1 + 1 / (k : ℝ)) ^ (k - 1) = 1 := by
  have hne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hne1 : (k : ℝ) + 1 ≠ 0 := by positivity
  have e : (k : ℝ) / ((k : ℝ) + 1) * (1 + 1 / (k : ℝ)) = 1 := by
    field
  rw [xcrit, ← mul_pow, e, one_pow]

/-! ### The tilted Cayley masses at the critical tilt -/

/-- The ratio of consecutive tilted Cayley masses: `c_{j+1} x^(j+1) = x (1 + 1/(j+1))^j c_j x^j`. -/
theorem ccT_succ (x : ℝ) (j : ℕ) :
    ccT x (j + 1) = x * (1 + 1 / ((j + 1 : ℕ) : ℝ)) ^ j * ccT x j := by
  have h := cay_ratio (j := j + 1) (Nat.succ_pos j)
  rw [Nat.add_sub_cancel] at h
  rw [ccT, ccT, cc, cc, h]
  ring

/-- `c_{j+1} x^(j+1) x_{j+1} = x c_j x^j`: at the tilt `x = x_{j+1}` the masses of the indices `j`
and `j + 1` are equal. -/
theorem ccT_succ_mul_xcrit (x : ℝ) (j : ℕ) : ccT x (j + 1) * xcrit (j + 1) = x * ccT x j := by
  have hx := xcrit_mul_psi (k := j + 1) (by omega)
  rw [Nat.add_sub_cancel] at hx
  rw [ccT_succ]
  linear_combination (x * ccT x j) * hx

/-- At the critical tilt the tilted Cayley masses do not increase up to the index `k`. -/
theorem ccT_succ_le {k n : ℕ} (hn : n + 1 ≤ k) : ccT (xcrit k) (n + 1) ≤ ccT (xcrit k) n := by
  have hx : 0 < xcrit k := xcrit_pos k
  have hpsi := psi_mono (i := n + 1) (j := k) (Nat.succ_pos n) hn
  rw [Nat.add_sub_cancel] at hpsi
  have h1 : xcrit k * (1 + 1 / ((n + 1 : ℕ) : ℝ)) ^ n ≤ 1 := by
    calc xcrit k * (1 + 1 / ((n + 1 : ℕ) : ℝ)) ^ n
        ≤ xcrit k * (1 + 1 / (k : ℝ)) ^ (k - 1) := mul_le_mul_of_nonneg_left hpsi hx.le
      _ = 1 := xcrit_mul_psi (by omega)
  rw [ccT_succ]
  exact mul_le_of_le_one_left (ccT_pos hx n).le h1

/-- At the critical tilt the tilted Cayley masses do not decrease from the index `k - 1` on. -/
theorem ccT_le_succ {k n : ℕ} (hk : 1 ≤ k) (hn : k ≤ n + 1) :
    ccT (xcrit k) n ≤ ccT (xcrit k) (n + 1) := by
  have hx : 0 < xcrit k := xcrit_pos k
  have hpsi := psi_mono (show 0 < k by omega) hn
  rw [Nat.add_sub_cancel] at hpsi
  have h1 : 1 ≤ xcrit k * (1 + 1 / ((n + 1 : ℕ) : ℝ)) ^ n := by
    calc (1 : ℝ) = xcrit k * (1 + 1 / (k : ℝ)) ^ (k - 1) := (xcrit_mul_psi hk).symm
      _ ≤ xcrit k * (1 + 1 / ((n + 1 : ℕ) : ℝ)) ^ n := mul_le_mul_of_nonneg_left hpsi hx.le
  rw [ccT_succ]
  exact le_mul_of_one_le_left (ccT_pos hx n).le h1

/-! ### The tilted free prime kernel at the critical tilt -/

/-- The tilted free prime kernel at the index $1$ is the tilt: $\varepsilon_1 x = x$. -/
theorem epsT_one (x : ℝ) : epsT x 1 = x := by
  rw [epsT, eps_one, one_mul, pow_one]

/-- The tilted free prime kernel at the index $2$ is $\varepsilon_2 x^2 = x^2/2$. -/
theorem epsT_two (x : ℝ) : epsT x 2 = x ^ 2 / 2 := by
  have h : eps 2 = ((1 : ℕ) : ℝ) ^ 1 / (((1 + 1 : ℕ).factorial : ℕ) : ℝ) := eps_succ 1
  have e : (1 + 1 : ℕ).factorial = 2 := rfl
  rw [epsT, h, e]
  push_cast
  ring

/-- `ε_{m+1} x^(m+1) (1 + 1/m)^m = a_{m+1} x^(m+1)`, since `ε_{m+1}/a_{m+1} = (m/(m+1))^m`. -/
private theorem epsT_mul_chi (x : ℝ) (m : ℕ) :
    epsT x (m + 1) * (1 + 1 / (m : ℝ)) ^ m = cayT x (m + 1) := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp [epsT, cayT, eps_one, cay_one]
  · have h0 : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hm.ne'
    have h1 : (m : ℝ) + 1 ≠ 0 := by positivity
    have hq : (m : ℝ) ^ m ≠ 0 := pow_ne_zero _ h0
    have hf : ((m + 1).factorial : ℝ) ≠ 0 := by positivity
    have e : (1 : ℝ) + 1 / (m : ℝ) = ((m : ℝ) + 1) / m := by field
    rw [epsT, cayT, eps_succ, cay_succ, e, div_pow]
    field

/-- The tilted free prime kernel does not increase on `[1, k]` at the critical tilt.  With
`χ_m = (1 + 1/m)^m`, which increases with `m`, and `a_n x^n = x c_{n-1} x^(n-1)`:
`ε_{m+1} x^(m+1) χ_m = a_{m+1} x^(m+1) ≤ a_m x^m = ε_m x^m χ_{m-1} ≤ ε_m x^m χ_m`. -/
theorem epsT_succ_le {k m : ℕ} (hm : 1 ≤ m) (hmk : m < k) :
    epsT (xcrit k) (m + 1) ≤ epsT (xcrit k) m := by
  have hx : 0 < xcrit k := xcrit_pos k
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  have hkf : 0 ≤ epsT (xcrit k) (i + 1) := mul_nonneg (eps_nonneg _) (pow_nonneg hx.le _)
  have hpos : (0 : ℝ) < (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1) := by positivity
  have hchi : (1 + 1 / (i : ℝ)) ^ i ≤ (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1) := by
    rcases Nat.eq_zero_or_pos i with rfl | hi
    · norm_num
    · exact chi_mono hi (show i ≤ i + 1 by omega)
  refine le_of_mul_le_mul_right ?_ hpos
  calc epsT (xcrit k) (i + 1 + 1) * (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1)
      = cayT (xcrit k) (i + 1 + 1) := epsT_mul_chi _ _
    _ ≤ cayT (xcrit k) (i + 1) := by
        rw [← x_mul_ccT, ← x_mul_ccT]
        exact mul_le_mul_of_nonneg_left (ccT_succ_le hmk.le) hx.le
    _ = epsT (xcrit k) (i + 1) * (1 + 1 / (i : ℝ)) ^ i := (epsT_mul_chi _ _).symm
    _ ≤ epsT (xcrit k) (i + 1) * (1 + 1 / ((i + 1 : ℕ) : ℝ)) ^ (i + 1) :=
        mul_le_mul_of_nonneg_left hchi hkf

end Parking
