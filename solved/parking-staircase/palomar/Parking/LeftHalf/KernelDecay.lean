module

public import Parking.LeftHalf.Weighted
public import Mathlib.Analysis.Complex.ExponentialBounds

/-!
# The prime kernel at the critical tilt: decay and order

`κ_m = kqT k (xcrit k) m` is the tilted prime kernel of the level `k` at the critical tilt
`x_k = xcrit k`.

* `kap_anti`: `κ` does not increase on `[1, ∞)`.
* The decay of `κ` beyond the free range: `kap_K2` (`(m+1) κ_{m+1} ≤ (m+1-j) κ_m` for
  `m ≥ k + (j-1)(k-1)`), `kap_K3a` (`L κ_L ≤ k κ_k`), `kap_K3b` (`(L-1) L κ_L ≤ 2k(k-1) κ_k` for
  `L ≥ 2k-1`), `kap_K4_mul` (`(2k-1) κ_l ≤ (2k-2) κ_{l-1}` for `l ≥ k+1`).
* `kap_free`: on the free range `2 ≤ L ≤ k`, `κ_L = poissonMass (L-1) (e x_k)^L / (e L)`, where
  `poissonMass n = e^{-n} n^n/n!` lies between `(1 - 1/(12n))/√(2πn)` and `1/√(2πn)` and
  `e x_k ≤ exp (3/(2k))`.
* Numeric bounds obtained from `kap_free`: `kap_drop` (`1.22 κ_{l'} ≤ κ_l` for
  `l' - l ≥ 0.73 k`, `l' ≤ k`) and, for `k ≥ 82`, `kap_at_k` (`κ_k ≤ 0.662/(k√k)`) and `kap_far`
  (`κ_L ≤ 0.73/(k√k)` for `L - 1 ≥ 0.73 k`).
* **The order of the kernel weights against the weight `Ψ′`.**  For a column `k ≥ 2`, a crossing
  row `q ≤ k + 27k/100`, a row `n ≥ 2k` and `L = n - q + 1`, with
  `Ψ′(j) = PsiW k j = max(j, 2k-1)`:
  `κ_{n-j} (2k-1) ≤ κ_L Ψ′(j)` for `j < q` (`order_neg`), and
  `κ_L Ψ′(j) ≤ κ_{n-j} (2k-1)` for `q ≤ j ≤ n-1` (`order_pos`).
  So `κ_{n-j} / Ψ′(j)` lies below `κ_L/(2k-1)` on the rows where the column is nonpositive and
  above it on the rows where it is positive.
-/

@[expose] public section

namespace Parking
open Finset

/-! ### Signs and monotonicity -/

/-- The free kernel does not increase on `[1, k]` at the critical tilt. -/
private theorem epsT_free (k : ℕ) :
    ∀ m, 1 ≤ m → m < k → epsT (xcrit k) (m + 1) ≤ epsT (xcrit k) m :=
  fun _ hm hmk => epsT_succ_le hm hmk

/-- A kernel that is nonincreasing step by step on `[1, ∞)` is antitone there. -/
private theorem antitone_of_step {g : ℕ → ℝ} (hg : ∀ c, 1 ≤ c → g (c + 1) ≤ g c) {c c' : ℕ}
    (hc : 1 ≤ c) (hcc : c ≤ c') : g c' ≤ g c := by
  induction c', hcc using Nat.le_induction with
  | base => exact le_refl _
  | succ n hn ih => exact le_trans (hg n (le_trans hc hn)) ih

/-- The prime kernel at the critical tilt does not increase on `[1, ∞)`. -/
private theorem kap_anti {k m m' : ℕ} (hk : 2 ≤ k) (hm : 1 ≤ m) (hmm : m ≤ m') :
    kqT k (xcrit k) m' ≤ kqT k (xcrit k) m :=
  antitone_of_step (g := kqT k (xcrit k))
    (kqT_succ_le hk (xcrit_pos k).le (epsT_free k)) hm hmm

/-! ### The decay beyond the free range -/

/-- If `κ_{i+1} ≤ ρ κ_i` on the window `m-k+1 ≤ i ≤ m-1`, then
`(m+1) κ_{m+1} ≤ ρ m κ_m` (`m ≥ k`): one step of the kernel recursion. -/
private theorem kap_K1 {k m : ℕ} (hk : 2 ≤ k) (hm : k ≤ m) {ρ : ℝ}
    (h : ∀ i, m + 1 ≤ i + k → i + 1 ≤ m →
      kqT k (xcrit k) (i + 1) ≤ ρ * kqT k (xcrit k) i) :
    ((m : ℝ) + 1) * kqT k (xcrit k) (m + 1) ≤ ρ * ((m : ℝ) * kqT k (xcrit k) m) := by
  have hx : 0 ≤ xcrit k := (xcrit_pos k).le
  have h1 := kqT_rec (xcrit k) hk (show k ≤ m + 1 by omega)
  have h0 := kqT_rec (xcrit k) hk hm
  rw [Nat.cast_add, Nat.cast_one] at h1
  rw [h1, h0, rconv, rconv, Finset.sum_range_succ, Finset.mul_sum]
  have hlast : kqWT k (xcrit k) (m + 1) = 0 := by
    rw [kqWT, show k - (m + 1) = 0 by omega, Nat.cast_zero, zero_mul]
  rw [hlast, zero_mul, add_zero]
  refine Finset.sum_le_sum fun j hj => ?_
  rw [Finset.mem_range] at hj
  by_cases hjy : k ≤ j + 1
  · have hz : kqWT k (xcrit k) (j + 1) = 0 := by
      rw [kqWT, show k - (j + 1) = 0 by omega, Nat.cast_zero, zero_mul]
    have e : kqWT k (xcrit k) (j + 1) * kqT k (xcrit k) (m + 1 - 1 - j)
        = ρ * (kqWT k (xcrit k) (j + 1) * kqT k (xcrit k) (m - 1 - j)) := by
      rw [hz, zero_mul, zero_mul, mul_zero]
    exact le_of_eq e
  · have hle : kqT k (xcrit k) (m + 1 - 1 - j) ≤ ρ * kqT k (xcrit k) (m - 1 - j) := by
      have h' := h (m - 1 - j) (by omega) (by omega)
      rwa [show m - 1 - j + 1 = m + 1 - 1 - j by omega] at h'
    calc kqWT k (xcrit k) (j + 1) * kqT k (xcrit k) (m + 1 - 1 - j)
        ≤ kqWT k (xcrit k) (j + 1) * (ρ * kqT k (xcrit k) (m - 1 - j)) :=
          mul_le_mul_of_nonneg_left hle (kqWT_nonneg k hx (j + 1))
      _ = ρ * (kqWT k (xcrit k) (j + 1) * kqT k (xcrit k) (m - 1 - j)) := by ring

/-- `(m+1) κ_{m+1} ≤ (m+1-j) κ_m` for `m ≥ k + (j-1)(k-1)`, `j ≥ 1`. -/
private theorem kap_K2 {k : ℕ} (hk : 2 ≤ k) : ∀ j, 1 ≤ j → ∀ m, k + (j - 1) * (k - 1) ≤ m →
    ((m : ℝ) + 1) * kqT k (xcrit k) (m + 1) ≤ ((m : ℝ) + 1 - (j : ℝ)) * kqT k (xcrit k) m := by
  have hx : 0 ≤ xcrit k := (xcrit_pos k).le
  intro j hj
  induction j, hj using Nat.le_induction with
  | base =>
    intro m hm
    rw [Nat.cast_one, add_sub_cancel_right]
    exact kqT_harmonic hk hx (epsT_free k) m (le_trans (Nat.le_add_right _ _) hm)
  | succ j hj ih =>
    intro m hm
    rw [Nat.add_sub_cancel] at hm
    have hjk : (j - 1) * (k - 1) + (k - 1) = j * (k - 1) := by
      rw [← Nat.succ_mul, Nat.succ_eq_add_one, Nat.sub_add_cancel hj]
    have hm0 : (0 : ℝ) < (m : ℝ) := Nat.cast_pos.mpr (by omega)
    have hstep : ∀ i, m + 1 ≤ i + k → i + 1 ≤ m →
        kqT k (xcrit k) (i + 1) ≤ ((m : ℝ) - (j : ℝ)) / (m : ℝ) * kqT k (xcrit k) i := by
      intro i hi1 hi2
      have h1 := ih i (by omega)
      have hκ' : kqT k (xcrit k) (i + 1) ≤ kqT k (xcrit k) i :=
        kap_anti hk (by omega) (Nat.le_add_right i 1)
      have hi : (i : ℝ) + 1 ≤ (m : ℝ) := by exact_mod_cast hi2
      have h2 : ((m : ℝ) - ((i : ℝ) + 1)) * kqT k (xcrit k) (i + 1)
          ≤ ((m : ℝ) - ((i : ℝ) + 1)) * kqT k (xcrit k) i :=
        mul_le_mul_of_nonneg_left hκ' (by linarith)
      rw [div_mul_eq_mul_div, le_div_iff₀ hm0]
      linarith
    have h3 := kap_K1 hk (show k ≤ m by omega) hstep
    have e : ((m : ℝ) - (j : ℝ)) / (m : ℝ) * ((m : ℝ) * kqT k (xcrit k) m)
        = ((m : ℝ) + 1 - ((j + 1 : ℕ) : ℝ)) * kqT k (xcrit k) m := by
      rw [← mul_assoc, div_mul_cancel₀ _ hm0.ne', Nat.cast_add, Nat.cast_one]
      ring
    rw [e] at h3
    exact h3

/-- `L κ_L ≤ k κ_k` for `L ≥ k`. -/
theorem kap_K3a {k L : ℕ} (hk : 2 ≤ k) (hL : k ≤ L) :
    (L : ℝ) * kqT k (xcrit k) L ≤ (k : ℝ) * kqT k (xcrit k) k := by
  induction L, hL using Nat.le_induction with
  | base => exact le_refl _
  | succ L hL ih =>
    have h := kqT_harmonic hk (xcrit_pos k).le (epsT_free k) L hL
    rw [Nat.cast_add, Nat.cast_one]
    exact le_trans h ih

/-- `(L-1) L κ_L ≤ 2k(k-1) κ_k` for `L ≥ 2k-1`. -/
theorem kap_K3b {k L : ℕ} (hk : 2 ≤ k) (hL : 2 * k - 1 ≤ L) :
    ((L : ℝ) - 1) * (L : ℝ) * kqT k (xcrit k) L
      ≤ 2 * (k : ℝ) * ((k : ℝ) - 1) * kqT k (xcrit k) k := by
  have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  induction L, hL using Nat.le_induction with
  | base =>
    have e : ((2 * k - 1 : ℕ) : ℝ) = 2 * (k : ℝ) - 1 := by
      rw [Nat.cast_sub (by omega : 1 ≤ 2 * k), Nat.cast_mul, Nat.cast_ofNat, Nat.cast_one]
    have h := kap_K3a hk (show k ≤ 2 * k - 1 by omega)
    rw [e] at h ⊢
    have h2 : (2 * (k : ℝ) - 2) * ((2 * (k : ℝ) - 1) * kqT k (xcrit k) (2 * k - 1))
        ≤ (2 * (k : ℝ) - 2) * ((k : ℝ) * kqT k (xcrit k) k) :=
      mul_le_mul_of_nonneg_left h (by linarith)
    linarith
  | succ L hL ih =>
    have hm : k + (2 - 1) * (k - 1) ≤ L := by
      have e : (2 - 1) * (k - 1) = k - 1 := by
        rw [show (2 - 1 : ℕ) = 1 from rfl, Nat.one_mul]
      rw [e]
      omega
    have h := kap_K2 hk 2 (by omega) L hm
    rw [Nat.cast_ofNat] at h
    have hL0 : (0 : ℝ) ≤ (L : ℝ) := Nat.cast_nonneg L
    have h' : (L : ℝ) * (((L : ℝ) + 1) * kqT k (xcrit k) (L + 1))
        ≤ (L : ℝ) * (((L : ℝ) + 1 - 2) * kqT k (xcrit k) L) :=
      mul_le_mul_of_nonneg_left h hL0
    rw [Nat.cast_add, Nat.cast_one]
    linarith

/-- `(2k-1) κ_l ≤ (2k-2) κ_{l-1}` for `l ≥ k+1`: beyond the free range the kernel decays by the
factor `(2k-2)/(2k-1)` at each step. -/
private theorem kap_K4_mul {k l : ℕ} (hk : 2 ≤ k) (hl : k + 1 ≤ l) :
    (2 * (k : ℝ) - 1) * kqT k (xcrit k) l ≤ (2 * (k : ℝ) - 2) * kqT k (xcrit k) (l - 1) := by
  obtain ⟨m, rfl⟩ : ∃ m, l = m + 1 := ⟨l - 1, by omega⟩
  rw [Nat.add_sub_cancel]
  have hx : 0 ≤ xcrit k := (xcrit_pos k).le
  have hkm : k ≤ m := by omega
  have hk1 : 0 < k - 1 := by omega
  -- `m - k = (k-1) d + r` with `r < k - 1`
  have hdm := Nat.div_add_mod (m - k) (k - 1)
  have hrl := Nat.mod_lt (m - k) hk1
  generalize (m - k) / (k - 1) = d at hdm
  generalize (m - k) % (k - 1) = r at hdm hrl
  have ha : k + (d + 1 - 1) * (k - 1) ≤ m := by
    rw [Nat.add_sub_cancel, Nat.mul_comm d (k - 1)]
    omega
  have hK2 := kap_K2 hk (d + 1) (by omega) m ha
  rw [Nat.cast_add, Nat.cast_one] at hK2
  have hb : m + 1 ≤ k + (k - 1) * d + (k - 1) := by omega
  have hκ0 : 0 ≤ kqT k (xcrit k) m := kqT_nonneg hk hx m
  have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hd0 : (0 : ℝ) ≤ (d : ℝ) := Nat.cast_nonneg d
  have hcast : ((k - 1 : ℕ) : ℝ) = (k : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega : 1 ≤ k), Nat.cast_one]
  have hbR : (m : ℝ) + 1 ≤ (k : ℝ) + ((k : ℝ) - 1) * (d : ℝ) + ((k : ℝ) - 1) := by
    have h : ((m + 1 : ℕ) : ℝ) ≤ ((k + (k - 1) * d + (k - 1) : ℕ) : ℝ) := Nat.cast_le.mpr hb
    rw [Nat.cast_add, Nat.cast_add, Nat.cast_add, Nat.cast_mul, Nat.cast_one, hcast] at h
    linarith
  have hlj : (m : ℝ) + 1 ≤ ((d : ℝ) + 1) * (2 * (k : ℝ) - 1) := by
    linarith [mul_nonneg hd0 (by linarith : (0 : ℝ) ≤ (k : ℝ))]
  have hm1 : (0 : ℝ) < (m : ℝ) + 1 := by positivity
  have h2 : (2 * (k : ℝ) - 1) * (((m : ℝ) + 1) * kqT k (xcrit k) (m + 1))
      ≤ (2 * (k : ℝ) - 1) * (((m : ℝ) + 1 - ((d : ℝ) + 1)) * kqT k (xcrit k) m) :=
    mul_le_mul_of_nonneg_left hK2 (by linarith)
  have h3 : 0 ≤ (((d : ℝ) + 1) * (2 * (k : ℝ) - 1) - ((m : ℝ) + 1)) * kqT k (xcrit k) m :=
    mul_nonneg (by linarith) hκ0
  have h1 : ((m : ℝ) + 1) * ((2 * (k : ℝ) - 1) * kqT k (xcrit k) (m + 1))
      ≤ ((m : ℝ) + 1) * ((2 * (k : ℝ) - 2) * kqT k (xcrit k) m) := by
    linarith
  exact le_of_mul_le_mul_left h1 hm1

/-! ### The free range -/

/-- On the free range the kernel is a renewal mass:
`κ_L = poissonMass (L-1) (e x_k)^L / (e L)` for `2 ≤ L ≤ k`. -/
private theorem kap_free {k L : ℕ} (hL2 : 2 ≤ L) (hLk : L ≤ k) :
    kqT k (xcrit k) L
      = poissonMass (L - 1) * (Real.exp 1 * xcrit k) ^ L / (Real.exp 1 * (L : ℝ)) := by
  obtain ⟨m, rfl⟩ : ∃ m, L = m + 1 := ⟨L - 1, by omega⟩
  rw [Nat.add_sub_cancel, kqT_eq_epsT (xcrit k) (by omega : 1 ≤ k) (by omega : 1 ≤ m + 1) hLk, epsT]
  have hm1 : ((m : ℝ) + 1) ≠ 0 := by positivity
  have he : Real.exp 1 ≠ 0 := (Real.exp_pos 1).ne'
  have heps : eps (m + 1) = ren m / ((m : ℝ) + 1) := by
    rw [eq_div_iff hm1, mul_comm]
    exact mul_eps m
  have hexp : Real.exp 1 ^ m = Real.exp (m : ℝ) := by
    rw [← Real.exp_nat_mul, mul_one]
  have hren : poissonMass m * Real.exp 1 ^ m = ren m := by
    rw [poissonMass, hexp, mul_right_comm, ← Real.exp_add, neg_add_cancel, Real.exp_zero, one_mul]
  rw [heps, ← hren, mul_pow, pow_succ (Real.exp 1) m, Nat.cast_add, Nat.cast_one]
  field

/-! ### Numeric tools -/

/-- `e x_k ≤ exp (3/(2k))`. -/
private theorem ex_le {k : ℕ} (hk : 1 ≤ k) :
    Real.exp 1 * xcrit k ≤ Real.exp (3 / (2 * (k : ℝ))) :=
  exp_one_mul_xcrit_le hk

/-- `(e x_k)^d ≤ exp (3/2)` for `d ≤ k`. -/
private theorem ex_pow_le {k d : ℕ} (hk : 1 ≤ k) (hd : d ≤ k) :
    (Real.exp 1 * xcrit k) ^ d ≤ Real.exp (3 / 2) := by
  have hk0 : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hk0' : (k : ℝ) ≠ 0 := hk0.ne'
  have hr0 : 0 ≤ Real.exp 1 * xcrit k := mul_nonneg (Real.exp_pos 1).le (xcrit_pos k).le
  have h1 : (Real.exp 1 * xcrit k) ^ d ≤ Real.exp (3 / (2 * (k : ℝ))) ^ d :=
    pow_le_pow_left₀ hr0 (ex_le hk) d
  have h2 : Real.exp (3 / (2 * (k : ℝ))) ^ d = Real.exp ((d : ℝ) * (3 / (2 * (k : ℝ)))) :=
    (Real.exp_nat_mul _ d).symm
  have hdR : (d : ℝ) ≤ (k : ℝ) := Nat.cast_le.mpr hd
  have h3 : (d : ℝ) * (3 / (2 * (k : ℝ))) ≤ 3 / 2 := by
    calc (d : ℝ) * (3 / (2 * (k : ℝ))) ≤ (k : ℝ) * (3 / (2 * (k : ℝ))) :=
          mul_le_mul_of_nonneg_right hdR (by positivity)
      _ = 3 / 2 := by field
  rw [h2] at h1
  exact le_trans h1 (Real.exp_le_exp.mpr h3)

/-- On the free range, by `poissonMass (L-1) ≤ 1/√(2π(L-1))` and `e x_k ≤ exp (3/(2k))`:
`κ_L ≤ exp (3L/(2k) - 1) / (L √(2π(L-1)))` for `2 ≤ L ≤ k`. -/
private theorem kap_free_le {k L : ℕ} (hL2 : 2 ≤ L) (hLk : L ≤ k) :
    kqT k (xcrit k) L ≤ Real.exp ((L : ℝ) * (3 / (2 * (k : ℝ))) - 1)
      / ((L : ℝ) * Real.sqrt (2 * Real.pi * ((L : ℝ) - 1))) := by
  have hLR : (2 : ℝ) ≤ (L : ℝ) := by exact_mod_cast hL2
  have hL0 : (0 : ℝ) < (L : ℝ) := by linarith
  have hL0' : (L : ℝ) ≠ 0 := hL0.ne'
  have he0 : (0 : ℝ) < Real.exp 1 := Real.exp_pos 1
  have he0' : Real.exp 1 ≠ 0 := he0.ne'
  have hr0 : 0 ≤ Real.exp 1 * xcrit k := mul_nonneg he0.le (xcrit_pos k).le
  have hS : 0 < Real.sqrt (2 * Real.pi * ((L : ℝ) - 1)) :=
    Real.sqrt_pos.2 (mul_pos (mul_pos (by norm_num) Real.pi_pos) (by linarith))
  have hS' : Real.sqrt (2 * Real.pi * ((L : ℝ) - 1)) ≠ 0 := hS.ne'
  have hR : poissonMass (L - 1) ≤ 1 / Real.sqrt (2 * Real.pi * ((L : ℝ) - 1)) := by
    have h := poissonMass_le (n := L - 1) (by omega)
    rwa [Nat.cast_sub (by omega : 1 ≤ L), Nat.cast_one] at h
  have hpow : (Real.exp 1 * xcrit k) ^ L
      ≤ Real.exp 1 * Real.exp ((L : ℝ) * (3 / (2 * (k : ℝ))) - 1) := by
    rw [← Real.exp_add, add_sub_cancel, Real.exp_nat_mul]
    exact pow_le_pow_left₀ hr0 (ex_le (by omega)) L
  rw [kap_free hL2 hLk]
  calc poissonMass (L - 1) * (Real.exp 1 * xcrit k) ^ L / (Real.exp 1 * (L : ℝ))
      ≤ 1 / Real.sqrt (2 * Real.pi * ((L : ℝ) - 1))
          * (Real.exp 1 * Real.exp ((L : ℝ) * (3 / (2 * (k : ℝ))) - 1))
          / (Real.exp 1 * (L : ℝ)) :=
        div_le_div_of_nonneg_right
          (mul_le_mul hR hpow (pow_nonneg hr0 L) (one_div_nonneg.mpr hS.le)) (mul_pos he0 hL0).le
    _ = Real.exp ((L : ℝ) * (3 / (2 * (k : ℝ))) - 1)
          / ((L : ℝ) * Real.sqrt (2 * Real.pi * ((L : ℝ) - 1))) := by
        field

/-! ### The kernel at `m = k` -/

/-- `exp (1/2) √k ≤ 0.662 √(2π(k-1))` for `k ≥ 82`. -/
private theorem at_k_num {k : ℝ} (hk : 82 ≤ k) :
    Real.exp (1 / 2) * Real.sqrt k ≤ 0.662 * Real.sqrt (2 * Real.pi * (k - 1)) := by
  have hk0 : (0 : ℝ) ≤ k := by linarith
  have hA : 0 ≤ 2 * Real.pi * (k - 1) :=
    mul_nonneg (mul_nonneg (by norm_num) Real.pi_pos.le) (by linarith)
  -- compare the squares: `e k ≤ 0.662² · 2π (k-1)`
  refine le_of_sq_le_sq ?_ (mul_nonneg (by norm_num) (Real.sqrt_nonneg _))
  rw [mul_pow, mul_pow, Real.sq_sqrt hk0, Real.sq_sqrt hA, ← Real.exp_nat_mul,
    show ((2 : ℕ) : ℝ) * (1 / 2) = 1 by norm_num]
  have h1 : Real.exp 1 * k ≤ 2.7182818286 * k :=
    mul_le_mul_of_nonneg_right Real.exp_one_lt_d9.le hk0
  have h2 : 3.1415 * (k - 1) ≤ Real.pi * (k - 1) :=
    mul_le_mul_of_nonneg_right Real.pi_gt_d4.le (by linarith)
  linarith

/-- `κ_k ≤ 0.662 / (k √k)` for `k ≥ 82`. -/
theorem kap_at_k {k : ℕ} (hk : 82 ≤ k) :
    kqT k (xcrit k) k ≤ 0.662 / ((k : ℝ) * Real.sqrt (k : ℝ)) := by
  have hkR : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have hk0 : (0 : ℝ) < (k : ℝ) := by linarith
  have hk0' : (k : ℝ) ≠ 0 := hk0.ne'
  have hS : 0 < Real.sqrt (2 * Real.pi * ((k : ℝ) - 1)) :=
    Real.sqrt_pos.2 (mul_pos (mul_pos (by norm_num) Real.pi_pos) (by linarith))
  have hsk : 0 < Real.sqrt (k : ℝ) := Real.sqrt_pos.2 hk0
  refine le_trans (kap_free_le (by omega) (le_refl k)) ?_
  rw [show (k : ℝ) * (3 / (2 * (k : ℝ))) - 1 = 1 / 2 by field,
    div_le_div_iff₀ (mul_pos hk0 hS) (mul_pos hk0 hsk)]
  have h3 := mul_le_mul_of_nonneg_left (at_k_num hkR) hk0.le
  linarith

/-! ### The kernel far from the origin -/

/-- Polynomial part of `kap_far`: with `z = (3/2)(t+1) - k`,
`k² + z k + z² ≤ 1.563368 (t+1) k` for `0.73 k ≤ t ≤ 0.73 k + 0.99`, `k ≥ 82`. -/
private theorem far_poly {k t : ℝ} (hk : 82 ≤ k) (h1 : 73 * k ≤ 100 * t)
    (h2 : 100 * t ≤ 73 * k + 99) :
    k * k + (3 / 2 * (t + 1) - k) * k + (3 / 2 * (t + 1) - k) ^ 2
      ≤ 1.563368 * (t + 1) * k := by
  have hk0 : (0 : ℝ) ≤ k := by linarith
  have hs1 : (0 : ℝ) ≤ 0.73 * k + 0.99 - t := by linarith
  have hs2 : (0 : ℝ) ≤ t + 2.99 - 0.73 * k := by linarith
  linarith [mul_nonneg hk0 (sub_nonneg.mpr hk), mul_nonneg hk0 hs1, mul_nonneg hs1 hs2]

/-- Real-variable core of `kap_far`. -/
private theorem far_core {k t : ℝ} (hk : 82 ≤ k) (h1 : 73 * k ≤ 100 * t)
    (h2 : 100 * t ≤ 73 * k + 99) :
    Real.exp ((t + 1) * (3 / (2 * k)) - 1) / ((t + 1) * Real.sqrt (2 * Real.pi * t))
      ≤ 0.73 / (k * Real.sqrt k) := by
  have hk0 : (0 : ℝ) < k := by linarith
  have hk0' : k ≠ 0 := hk0.ne'
  have ht0 : (0 : ℝ) < t := by linarith
  have ht1 : (0 : ℝ) < t + 1 := by linarith
  have hpi : (3.1415 : ℝ) < Real.pi := Real.pi_gt_d4
  have hpi0 : (0 : ℝ) < Real.pi := Real.pi_pos
  have hsk : 0 < Real.sqrt k := Real.sqrt_pos.2 hk0
  have hS : 0 < Real.sqrt (2 * Real.pi * t) :=
    Real.sqrt_pos.2 (mul_pos (mul_pos (by norm_num) hpi0) ht0)
  obtain ⟨y, hy⟩ : ∃ y : ℝ, y = (t + 1) * (3 / (2 * k)) - 1 := ⟨_, rfl⟩
  have hyk : y * k = 3 / 2 * (t + 1) - k := by
    rw [hy]
    field
  have hy0 : 0 ≤ y := by
    have h : 0 ≤ y * k := by
      rw [hyk]
      linarith
    exact nonneg_of_mul_nonneg_left h hk0
  have hy1 : y ≤ 1.7 := by
    have h : y * k ≤ 1.7 * k := by
      rw [hyk]
      linarith
    exact le_of_mul_le_mul_right h hk0
  have hexp : Real.exp y ≤ 1 + y + y ^ 2 := exp_le_quadratic hy0 hy1
  have hpoly : (1 + y + y ^ 2) * k ≤ 1.563368 * (t + 1) := by
    have h := far_poly hk h1 h2
    rw [← hyk] at h
    have h' : (1 + y + y ^ 2) * k * k ≤ 1.563368 * (t + 1) * k := by
      have e : (1 + y + y ^ 2) * k * k = k * k + y * k * k + (y * k) ^ 2 := by ring
      rw [e]
      exact h
    exact le_of_mul_le_mul_right h' hk0
  have hsq : 2.1416 * Real.sqrt k ≤ Real.sqrt (2 * Real.pi * t) := by
    have e : (2.1416 : ℝ) * Real.sqrt k = Real.sqrt (2.1416 ^ 2 * k) := by
      rw [Real.sqrt_mul (by norm_num), Real.sqrt_sq (by norm_num)]
    rw [e]
    apply Real.sqrt_le_sqrt
    have hp : 3.1415 * t ≤ Real.pi * t := mul_le_mul_of_nonneg_right hpi.le ht0.le
    linarith [hp]
  rw [← hy, div_le_div_iff₀ (mul_pos ht1 hS) (mul_pos hk0 hsk)]
  have hA : Real.exp y * (k * Real.sqrt k) ≤ (1 + y + y ^ 2) * (k * Real.sqrt k) :=
    mul_le_mul_of_nonneg_right hexp (mul_pos hk0 hsk).le
  have hB : (1 + y + y ^ 2) * k * Real.sqrt k ≤ 1.563368 * (t + 1) * Real.sqrt k :=
    mul_le_mul_of_nonneg_right hpoly hsk.le
  have hC : 0.73 * (t + 1) * (2.1416 * Real.sqrt k)
      ≤ 0.73 * (t + 1) * Real.sqrt (2 * Real.pi * t) :=
    mul_le_mul_of_nonneg_left hsq (mul_nonneg (by norm_num) ht1.le)
  linarith [hA, hB, hC]

/-- `κ_L ≤ 0.73 / (k √k)` when `L - 1 ≥ 0.73 k` (`k ≥ 82`). -/
theorem kap_far {k L : ℕ} (hk : 82 ≤ k) (hL : 73 * k ≤ 100 * (L - 1)) :
    kqT k (xcrit k) L ≤ 0.73 / ((k : ℝ) * Real.sqrt (k : ℝ)) := by
  -- by monotonicity it suffices to bound `κ_{t+1}` for `t = ⌈0.73 k⌉`, in the free range
  obtain ⟨t, ht⟩ : ∃ t, t = (73 * k + 99) / 100 := ⟨_, rfl⟩
  have hkR : (82 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  have h1R : (73 : ℝ) * (k : ℝ) ≤ 100 * (t : ℝ) := by
    exact_mod_cast (show 73 * k ≤ 100 * t by omega)
  have h2R : (100 : ℝ) * (t : ℝ) ≤ 73 * (k : ℝ) + 99 := by
    exact_mod_cast (show 100 * t ≤ 73 * k + 99 by omega)
  refine le_trans (kap_anti (m := t + 1) (by omega) (by omega) (by omega))
    (le_trans (kap_free_le (by omega) (by omega)) ?_)
  rw [Nat.cast_add, Nat.cast_one, add_sub_cancel_right]
  exact far_core hkR h1R h2R

/-! ### The drop across a gap of `0.73 k` inside the free range -/

/-- Real-variable core of `kap_drop`: if `2 ≤ l` and `l ≤ 0.27 l'` then
`1.22 e^{3/2} l √(2π(l-1)) ≤ (11/12) l' √(2π(l'-1))`. -/
private theorem drop_num {l l' : ℝ} (hl : 2 ≤ l) (hll : 100 * l ≤ 27 * l') :
    1.22 * Real.exp (3 / 2) * l * Real.sqrt (2 * Real.pi * (l - 1))
      ≤ 11 / 12 * l' * Real.sqrt (2 * Real.pi * (l' - 1)) := by
  have hpi0 : (0 : ℝ) < Real.pi := Real.pi_pos
  have hl0 : (0 : ℝ) ≤ l := by linarith
  have hl'0 : (0 : ℝ) ≤ l' := by linarith
  have hA : 0 ≤ 2 * Real.pi * (l - 1) :=
    mul_nonneg (mul_nonneg (by norm_num) hpi0.le) (by linarith)
  have hA' : 0 ≤ 2 * Real.pi * (l' - 1) :=
    mul_nonneg (mul_nonneg (by norm_num) hpi0.le) (by linarith)
  have he3 : Real.exp 1 ^ 3 ≤ 20.0856 := by
    have h : Real.exp 1 ^ 3 ≤ (2.7182818286 : ℝ) ^ 3 :=
      pow_le_pow_left₀ (Real.exp_pos 1).le Real.exp_one_lt_d9.le 3
    have h' : (2.7182818286 : ℝ) ^ 3 ≤ 20.0856 := by norm_num
    exact le_trans h h'
  have hEE : Real.exp (3 / 2) ^ 2 = Real.exp 1 ^ 3 := by
    rw [← Real.exp_nat_mul, ← Real.exp_nat_mul]
    norm_num
  -- compare the squares
  refine le_of_sq_le_sq ?_ (mul_nonneg (mul_nonneg (by norm_num) hl'0) (Real.sqrt_nonneg _))
  simp only [mul_pow]
  rw [Real.sq_sqrt hA, Real.sq_sqrt hA', hEE]
  have hu : l * l ≤ 27 / 100 * l' * (27 / 100 * l') :=
    mul_self_le_mul_self hl0 (by linarith)
  have hv : l - 1 ≤ 27 / 100 * (l' - 1) := by linarith
  have huv : l * l * (l - 1) ≤ 27 / 100 * l' * (27 / 100 * l') * (27 / 100 * (l' - 1)) :=
    mul_le_mul hu hv (by linarith) (mul_self_nonneg _)
  have hX : 0 ≤ l * l * (l - 1) := mul_nonneg (mul_self_nonneg l) (by linarith)
  have hY : 0 ≤ l' * l' * (l' - 1) := mul_nonneg (mul_self_nonneg l') (by linarith)
  have s1 : Real.exp 1 ^ 3 * (l * l * (l - 1)) ≤ 20.0856 * (l * l * (l - 1)) :=
    mul_le_mul_of_nonneg_right he3 hX
  have hfin : 1.22 * 1.22 * (Real.exp 1 ^ 3 * (l * l * (l - 1)))
      ≤ 11 / 12 * (11 / 12) * (l' * l' * (l' - 1)) := by
    linarith [s1, huv, hY]
  have hfin2 := mul_le_mul_of_nonneg_left hfin (mul_nonneg (by norm_num : (0 : ℝ) ≤ 2) hpi0.le)
  linarith [hfin2]

set_option maxHeartbeats 400000 in
-- a long chain of explicit real-arithmetic steps
/-- Across a gap of at least `0.73 k` inside the free range the kernel drops by the factor
`1.22` at least. -/
private theorem kap_drop {k l l' : ℕ} (hk2 : 2 ≤ k) (hl : 1 ≤ l) (hll : l < l') (hl' : l' ≤ k)
    (hgap : 73 * k ≤ 100 * (l' - l)) : 1.22 * kqT k (xcrit k) l' ≤ kqT k (xcrit k) l := by
  have hx0 : 0 < xcrit k := xcrit_pos k
  have hx1 : xcrit k ≤ 1 := xcrit_le_one k
  rcases Nat.lt_or_ge l 2 with hl1 | hl2
  · -- `l = 1`: `κ_1 = x ≥ 2 κ_2`
    have hl1' : l = 1 := by omega
    subst hl1'
    have h2 : kqT k (xcrit k) l' ≤ kqT k (xcrit k) 2 := kap_anti hk2 (by omega) (by omega)
    have e1 : kqT k (xcrit k) 1 = xcrit k := by
      rw [kqT_eq_epsT (xcrit k) (by omega : 1 ≤ k) (le_refl 1) (by omega : 1 ≤ k), epsT_one]
    have e2 : kqT k (xcrit k) 2 = xcrit k ^ 2 / 2 := by
      rw [kqT_eq_epsT (xcrit k) (by omega : 1 ≤ k) (by omega : 1 ≤ 2) hk2, epsT_two]
    rw [e1]
    rw [e2] at h2
    linarith [mul_nonneg hx0.le (sub_nonneg.mpr hx1), h2]
  · -- `2 ≤ l < l' ≤ k`: both indices in the free range
    have he0 : (0 : ℝ) < Real.exp 1 := Real.exp_pos 1
    have hr0 : 0 ≤ Real.exp 1 * xcrit k := mul_nonneg he0.le hx0.le
    have hrpos : 0 < Real.exp 1 * xcrit k := mul_pos he0 hx0
    have hlR : (2 : ℝ) ≤ (l : ℝ) := by exact_mod_cast hl2
    have hl0 : (0 : ℝ) < (l : ℝ) := by linarith
    have hgapN : 100 * l ≤ 27 * l' := by omega
    have hgapR : (100 : ℝ) * (l : ℝ) ≤ 27 * (l' : ℝ) := by exact_mod_cast hgapN
    have hl'0 : (0 : ℝ) < (l' : ℝ) := by linarith
    have hc1 : ((l - 1 : ℕ) : ℝ) = (l : ℝ) - 1 := by
      rw [Nat.cast_sub (by omega : 1 ≤ l), Nat.cast_one]
    have hc2 : ((l' - 1 : ℕ) : ℝ) = (l' : ℝ) - 1 := by
      rw [Nat.cast_sub (by omega : 1 ≤ l'), Nat.cast_one]
    rw [kap_free (by omega : 2 ≤ l') hl', kap_free hl2 (by omega : l ≤ k)]
    have hRu := poissonMass_le (n := l' - 1) (by omega)
    have hRl := poissonMass_ge (n := l - 1) (by omega)
    rw [hc2] at hRu
    rw [hc1] at hRl
    have hS : 0 < Real.sqrt (2 * Real.pi * ((l : ℝ) - 1)) :=
      Real.sqrt_pos.2 (mul_pos (mul_pos (by norm_num) Real.pi_pos) (by linarith))
    have hS' : 0 < Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1)) :=
      Real.sqrt_pos.2 (mul_pos (mul_pos (by norm_num) Real.pi_pos) (by linarith))
    have hB : 11 / 12 ≤ poissonMass (l - 1) * Real.sqrt (2 * Real.pi * ((l : ℝ) - 1)) := by
      have h1 : (11 : ℝ) / 12 ≤ 1 - 1 / (12 * ((l : ℝ) - 1)) := by
        have h0 : 1 / (12 * ((l : ℝ) - 1)) ≤ 1 / 12 := by
          apply one_div_le_one_div_of_le (by norm_num)
          linarith
        linarith
      have h2 : 11 / 12 / Real.sqrt (2 * Real.pi * ((l : ℝ) - 1)) ≤ poissonMass (l - 1) :=
        le_trans (div_le_div_of_nonneg_right h1 hS.le) hRl
      rwa [div_le_iff₀ hS] at h2
    have hA : poissonMass (l' - 1) * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1)) ≤ 1 := by
      rwa [le_div_iff₀ hS'] at hRu
    have hp : (Real.exp 1 * xcrit k) ^ l'
        = (Real.exp 1 * xcrit k) ^ l * (Real.exp 1 * xcrit k) ^ (l' - l) := by
      rw [← pow_add]
      congr 1
      omega
    have hq : (Real.exp 1 * xcrit k) ^ (l' - l) ≤ Real.exp (3 / 2) :=
      ex_pow_le (by omega) (by omega)
    have hp0 : 0 < (Real.exp 1 * xcrit k) ^ l := pow_pos hrpos _
    have hR'0 : 0 ≤ poissonMass (l' - 1) := (poissonMass_pos _).le
    have hN := drop_num hlR hgapR
    have key : 1.22 * poissonMass (l' - 1) * (Real.exp 1 * xcrit k) ^ (l' - l) * (l : ℝ)
        ≤ poissonMass (l - 1) * (l' : ℝ) := by
      have h1 : 1.22 * poissonMass (l' - 1) * (Real.exp 1 * xcrit k) ^ (l' - l) * (l : ℝ)
          ≤ 1.22 * poissonMass (l' - 1) * Real.exp (3 / 2) * (l : ℝ) := by
        have h := mul_le_mul_of_nonneg_left hq
          (mul_nonneg (by norm_num : (0 : ℝ) ≤ 1.22) hR'0)
        exact mul_le_mul_of_nonneg_right h hl0.le
      have h2 : 1.22 * poissonMass (l' - 1) * Real.exp (3 / 2) * (l : ℝ)
            * (Real.sqrt (2 * Real.pi * ((l : ℝ) - 1))
                * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1)))
          ≤ poissonMass (l - 1) * (l' : ℝ)
            * (Real.sqrt (2 * Real.pi * ((l : ℝ) - 1))
                * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1))) := by
        have t1 : poissonMass (l' - 1) * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1))
              * (1.22 * Real.exp (3 / 2) * (l : ℝ) * Real.sqrt (2 * Real.pi * ((l : ℝ) - 1)))
            ≤ 1 * (1.22 * Real.exp (3 / 2) * (l : ℝ)
                * Real.sqrt (2 * Real.pi * ((l : ℝ) - 1))) :=
          mul_le_mul_of_nonneg_right hA
            (mul_nonneg (mul_nonneg (mul_nonneg (by norm_num) (Real.exp_pos _).le) hl0.le)
              hS.le)
        have t2 : 11 / 12 * ((l' : ℝ) * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1)))
            ≤ poissonMass (l - 1) * Real.sqrt (2 * Real.pi * ((l : ℝ) - 1))
              * ((l' : ℝ) * Real.sqrt (2 * Real.pi * ((l' : ℝ) - 1))) :=
          mul_le_mul_of_nonneg_right hB (mul_nonneg hl'0.le hS'.le)
        linarith [t1, t2, hN]
      exact le_trans h1 (le_of_mul_le_mul_right h2 (mul_pos hS hS'))
    rw [hp]
    have hel : (0 : ℝ) < Real.exp 1 * (l : ℝ) := mul_pos he0 hl0
    have hel' : (0 : ℝ) < Real.exp 1 * (l' : ℝ) := mul_pos he0 hl'0
    rw [← mul_div_assoc, div_le_div_iff₀ hel' hel]
    have h3 := mul_le_mul_of_nonneg_right key (mul_pos hp0 he0).le
    linarith [h3]

/-! ### The order of the kernel weights against the weight `Ψ′` -/

/-- Beyond the free range, `j ↦ κ_{n-j} / j` does not decrease on `j ≥ 2k-1` (from `kap_K4_mul`):
`j κ_{n-(2k-1)} ≤ (2k-1) κ_{n-j}` as long as `n - j ≥ k`. -/
private theorem ratio_mono {k n : ℕ} (hk : 2 ≤ k) : ∀ j, 2 * k - 1 ≤ j → k ≤ n - j →
    (j : ℝ) * kqT k (xcrit k) (n - (2 * k - 1)) ≤ (2 * (k : ℝ) - 1) * kqT k (xcrit k) (n - j) := by
  have e : ((2 * k - 1 : ℕ) : ℝ) = 2 * (k : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega : 1 ≤ 2 * k), Nat.cast_mul, Nat.cast_ofNat, Nat.cast_one]
  have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  intro j hj
  induction j, hj using Nat.le_induction with
  | base =>
    intro _
    rw [e]
  | succ j hj ih =>
    intro hl
    have ih' := ih (by omega)
    have hK4 := kap_K4_mul hk (l := n - j) (by omega)
    rw [show n - j - 1 = n - (j + 1) by omega] at hK4
    have hκ0 : 0 ≤ kqT k (xcrit k) (n - (2 * k - 1)) := kqT_nonneg hk (xcrit_pos k).le _
    have hjR : 2 * (k : ℝ) - 1 ≤ (j : ℝ) := by
      rw [← e]
      exact Nat.cast_le.mpr hj
    have h1 : 0 ≤ ((j : ℝ) - (2 * (k : ℝ) - 2)) * kqT k (xcrit k) (n - (2 * k - 1)) :=
      mul_nonneg (by linarith) hκ0
    have h2 := mul_le_mul_of_nonneg_left ih' (show (0 : ℝ) ≤ 2 * (k : ℝ) - 1 by linarith)
    have h3 := mul_le_mul_of_nonneg_left hK4 (show (0 : ℝ) ≤ 2 * (k : ℝ) - 1 by linarith)
    refine le_of_mul_le_mul_left ?_ (show (0 : ℝ) < 2 * (k : ℝ) - 2 by linarith)
    rw [Nat.cast_add, Nat.cast_one]
    linarith

/-- The order of the kernel weights on the rows `j < q` (where the column is nonpositive). -/
theorem order_neg {k q n j : ℕ} (hk : 2 ≤ k) (hq2 : 100 * (q - k) ≤ 27 * k) (hn : 2 * k ≤ n)
    (hj2 : j < q) :
    kqT k (xcrit k) (n - j) * (2 * (k : ℝ) - 1) ≤ kqT k (xcrit k) (n - q + 1) * PsiW k j := by
  have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
  rw [PsiW_low (by omega : 1 ≤ k) (by omega : j ≤ 2 * k - 1)]
  exact mul_le_mul_of_nonneg_right (kap_anti (by omega) (by omega) (by omega)) (by linarith)

set_option maxHeartbeats 400000 in
-- four cases, each with several `omega` calls over truncated subtractions
/-- The order of the kernel weights on the positive rows `q ≤ j ≤ n-1`. -/
theorem order_pos {k q n j : ℕ} (hk2 : 2 ≤ k) (hq1 : k + 1 ≤ q) (hq2 : 100 * (q - k) ≤ 27 * k)
    (hn : 2 * k ≤ n) (hj1 : q ≤ j) (hj2 : j ≤ n - 1) :
    kqT k (xcrit k) (n - q + 1) * PsiW k j ≤ kqT k (xcrit k) (n - j) * (2 * (k : ℝ) - 1) := by
  have hx : 0 ≤ xcrit k := (xcrit_pos k).le
  have hkR : (2 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk2
  have hk0 : (0 : ℝ) < (k : ℝ) := by linarith
  have h2k1 : (0 : ℝ) ≤ 2 * (k : ℝ) - 1 := by linarith
  by_cases hj : j ≤ 2 * k - 1
  · -- `Ψ′(j) = 2k-1` and `1 ≤ n-j ≤ L`
    rw [PsiW_low (by omega : 1 ≤ k) hj]
    exact mul_le_mul_of_nonneg_right (kap_anti hk2 (by omega) (by omega)) h2k1
  · -- `Ψ′(j) = j ≥ 2k`
    rw [PsiW_of_ge (by omega : 2 * k - 1 ≤ j)]
    have hκL0 : 0 ≤ kqT k (xcrit k) (n - q + 1) := kqT_nonneg hk2 hx _
    have hj0 : (0 : ℝ) ≤ (j : ℝ) := Nat.cast_nonneg j
    by_cases hl : k ≤ n - j
    · -- the kernel index `n - j` is beyond the free range: `ratio_mono`
      have h1 := ratio_mono hk2 (n := n) j (by omega) hl
      have h2 : kqT k (xcrit k) (n - q + 1) ≤ kqT k (xcrit k) (n - (2 * k - 1)) :=
        kap_anti hk2 (by omega) (by omega)
      have h3 := mul_le_mul_of_nonneg_right h2 hj0
      linarith
    · by_cases hL : n - q + 1 ≤ k
      · -- both indices in the free range, at distance `≥ 0.73 k`
        have hd := kap_drop hk2 (l := n - j) (l' := n - q + 1) (by omega) (by omega) hL
          (by omega)
        have hjR : (100 : ℝ) * (j : ℝ) + 122 ≤ 244 * (k : ℝ) := by
          exact_mod_cast (show 100 * j + 122 ≤ 244 * k by omega)
        calc kqT k (xcrit k) (n - q + 1) * (j : ℝ)
            ≤ kqT k (xcrit k) (n - q + 1) * (1.22 * (2 * (k : ℝ) - 1)) :=
              mul_le_mul_of_nonneg_left (by linarith) hκL0
          _ = 1.22 * kqT k (xcrit k) (n - q + 1) * (2 * (k : ℝ) - 1) := by ring
          _ ≤ kqT k (xcrit k) (n - j) * (2 * (k : ℝ) - 1) :=
              mul_le_mul_of_nonneg_right hd h2k1
      · -- `L > k` and `n - j < k`: `kap_K3a` for `κ_L`, and `c κ_k ≤ κ_{n-j}` with a constant `c`
        -- such that `k j ≤ c (2k-1) L`
        have hK3 := kap_K3a hk2 (L := n - q + 1) (by omega)
        have hκk0 : 0 ≤ kqT k (xcrit k) k := kqT_nonneg hk2 hx k
        obtain ⟨Lr, hLr⟩ : ∃ Lr : ℝ, Lr = ((n - q + 1 : ℕ) : ℝ) := ⟨_, rfl⟩
        rw [← hLr] at hK3
        have hLR : (k : ℝ) + 1 ≤ Lr := by
          rw [hLr]
          exact_mod_cast (show k + 1 ≤ n - q + 1 by omega)
        have hL0 : (0 : ℝ) < Lr := by linarith
        obtain ⟨c, hc, hP⟩ : ∃ c : ℝ, c * kqT k (xcrit k) k ≤ kqT k (xcrit k) (n - j)
            ∧ (k : ℝ) * (j : ℝ) ≤ c * (2 * (k : ℝ) - 1) * Lr := by
          by_cases hg : 73 * k ≤ 100 * (k - (n - j))
          · -- `n - j ≤ 0.27 k`: the drop from `n - j` to `k`, `c = 1.22`
            refine ⟨1.22, kap_drop hk2 (by omega) (by omega) (le_refl k) hg, ?_⟩
            have hjR : (100 : ℝ) * (j : ℝ) + 200 ≤ 127 * (k : ℝ) + 100 * Lr := by
              rw [hLr]
              exact_mod_cast (show 100 * j + 200 ≤ 127 * k + 100 * (n - q + 1) by omega)
            linarith [mul_nonneg hk0.le
                (by linarith : (0 : ℝ) ≤ 1.27 * (k : ℝ) + Lr - 2 - (j : ℝ)),
              mul_nonneg (by linarith : (0 : ℝ) ≤ Lr - ((k : ℝ) + 1))
                (by linarith : (0 : ℝ) ≤ 1.44 * (k : ℝ) - 1.22),
              mul_nonneg hk0.le hk0.le]
          · -- `0.27 k < n - j < k`: monotonicity only, `c = 1`
            refine ⟨1, by rw [one_mul]; exact kap_anti hk2 (by omega) (by omega), ?_⟩
            have hjR : (j : ℝ) + 2 ≤ (k : ℝ) + Lr := by
              rw [hLr]
              exact_mod_cast (show j + 2 ≤ k + (n - q + 1) by omega)
            linarith [mul_nonneg hk0.le
                (by linarith : (0 : ℝ) ≤ (k : ℝ) + Lr - 2 - (j : ℝ)),
              mul_nonneg (by linarith : (0 : ℝ) ≤ Lr - ((k : ℝ) + 1))
                (by linarith : (0 : ℝ) ≤ (k : ℝ) - 1)]
        have t1 := mul_le_mul_of_nonneg_right hK3 hj0
        have t2 := mul_le_mul_of_nonneg_right hP hκk0
        have t3 := mul_le_mul_of_nonneg_right hc (mul_nonneg h2k1 hL0.le)
        refine le_of_mul_le_mul_right ?_ hL0
        linarith

end Parking