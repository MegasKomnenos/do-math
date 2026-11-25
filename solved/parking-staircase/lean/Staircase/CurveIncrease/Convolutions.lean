import Parking.Cayley.Stirling
import Parking.NextColumn.Birthday
import Staircase.Cayley.MarkedCuts
import Staircase.CurveIncrease.Volterra
import Batteries.Tactic.OpenPrivate

/-!
# The convolutions `κ₂`, `κ₃` of the Poisson mass

Write `P(m) = poissonMass m = e^{-m} m^m/m!`.  Both sides of the pair–impulse criterion are bounded
by sums of the two convolutions

`κ₂(m) = ∑_{0<g<m} P(g) · P(m-g)` (`kc2`),  `κ₃(m) = ∑_{0<g<m} κ₂(g) · P(m-g)` (`kc3`),

and this module proves what the estimates use about them.

* Closed forms.  `kc2_eq : κ₂(m) = P(m) · (s_m - 1)` and `kc3_eq : κ₃(m) = (m-1) · P(m) - 2·κ₂(m)`,
  where `s_m = sbirth m` is the mean of the birthday law.  With the constant cut profile `1` the
  compositions of `m` have the total weight `ren m`, so `e^m κ₂(m)` and `e^m κ₃(m)` are the weights
  of the compositions of `m` with one and with two marked cut points (`Lam1`, `Lam2`); by
  `Lam1_eq_sum` and `Lam2_eq_sum` these are moments of the number of parts, and the number of parts
  follows the birthday law (`Tq_eq`; in the form `sum_Tq_poly`, a private lemma of
  `Parking.NextColumn.Birthday`), whose moments `Pb_moment` evaluates.
* Moments.  In a convolution of equal factors every factor has the same mean position, so
  `∑_g g · P(g) P(m-g) = (m/2) · κ₂(m)` (`kc2_mom`),
  `∑_a a · κ₂(a) P(m-a) = (2m/3) · κ₃(m)` (`kc3_mom_left`) and
  `∑_a a · P(a) κ₂(m-a) = (m/3) · κ₃(m)` (`kc3_mom_right`).  The proofs use that the convolution is
  commutative and associative and that `g ↦ g · u(g)` acts on it as a derivation.
* The weights `w_s = P(R-s) · (R-1-s) · κ₂(s)` of the impulse side: their sum is
  `((R-3)/3) · κ₃(R)` (`impulse_weight_sum`) and their mean position is at least `2R/5`
  (`impulse_weight_mean`).
-/

namespace Parking

open Finset

open private sum_Ioo_shift from Parking.NextColumn.Compositions
open private sum_Ioo_reflect from Parking.NextColumn.Frozen
open private sum_Tq_poly from Parking.NextColumn.Birthday

/-- `κ₂(m) = ∑_{0<g<m} P(g) · P(m-g)`, the convolution of the Poisson mass `P = poissonMass` with
itself over the proper splittings of `m`. -/
noncomputable def kc2 (m : ℕ) : ℝ := ∑ g ∈ Ioo 0 m, poissonMass g * poissonMass (m - g)

/-- `κ₃(m) = ∑_{0<g<m} κ₂(g) · P(m-g)`, the threefold convolution of the Poisson mass. -/
noncomputable def kc3 (m : ℕ) : ℝ := ∑ g ∈ Ioo 0 m, kc2 g * poissonMass (m - g)

/-- `κ₂ ≥ 0`. -/
theorem kc2_nonneg (m : ℕ) : 0 ≤ kc2 m :=
  Finset.sum_nonneg fun _ _ => mul_nonneg (poissonMass_pos _).le (poissonMass_pos _).le

/-- `κ₃ ≥ 0`. -/
theorem kc3_nonneg (m : ℕ) : 0 ≤ kc3 m :=
  Finset.sum_nonneg fun _ _ => mul_nonneg (kc2_nonneg _) (poissonMass_pos _).le

/-- `κ₂(1) = 0`: the number `1` has no proper splitting. -/
theorem kc2_one : kc2 1 = 0 :=
  Finset.sum_eq_zero fun g hg => by rw [mem_Ioo] at hg; omega

/-- `P(g) · P(m-g) = e^{-m} · ren g · ren (m-g)` for `g ≤ m`. -/
theorem poissonMass_mul {g m : ℕ} (hg : g ≤ m) :
    poissonMass g * poissonMass (m - g) = Real.exp (-(m : ℝ)) * (ren g * ren (m - g)) := by
  have he : Real.exp (-(g : ℝ)) * Real.exp (-((m - g : ℕ) : ℝ)) = Real.exp (-(m : ℝ)) := by
    rw [← Real.exp_add, Nat.cast_sub hg]
    congr 1
    ring
  unfold poissonMass
  linear_combination (ren g * ren (m - g)) * he

/-! ### Closed forms -/

/-- `ren m = m · a_m` for `m ≥ 1`. -/
private theorem ren_eq_mul_cay {m : ℕ} (hm : 1 ≤ m) : ren m = (m : ℝ) * cay m := by
  obtain ⟨i, rfl⟩ : ∃ i, m = i + 1 := ⟨m - 1, by omega⟩
  rw [cay_succ]
  unfold ren
  push_cast
  ring

/-- The first factorial moment of the birthday law: `∑_{i<m} i · (i+1) · Pb m (i+1) = m·(s_m - 1)`,
from `Pb_moment` with `g(j) = j - 1`. -/
private theorem Pb_factorial_moment {m : ℕ} (hm : 1 ≤ m) :
    ∑ i ∈ range m, (i : ℝ) * (((i : ℝ) + 1) * Pb m (i + 1)) = m * (sbirth m - 1) := by
  have h := Pb_moment hm (fun j => (j : ℝ) - 1)
  have e1 : ∑ i ∈ range m, (i : ℝ) * (((i : ℝ) + 1) * Pb m (i + 1))
      = ∑ i ∈ range m, (((i + 1 : ℕ) : ℝ) - 1) * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring
  have e2 : ∑ i ∈ range m, ((((i + 1 : ℕ) : ℝ) - 1) - ((i : ℝ) - 1)) * Pb m (i + 1) = sbirth m := by
    unfold sbirth
    rw [sum_Icc_one_eq_range]
    exact Finset.sum_congr rfl fun i _ => by rw [Nat.cast_add, Nat.cast_one]; ring
  rw [e1, h, e2, Nat.cast_zero]
  ring

/-- With the constant profile `1`, one marked cut point gives the convolution of `ren` with
itself. -/
private theorem Lam1_one (m : ℕ) :
    Lam1 (fun _ => (1 : ℝ)) m = ∑ a ∈ Ioo 0 m, ren a * ren (m - a) := by
  unfold Lam1
  refine Finset.sum_congr rfl fun a ha => ?_
  rw [mem_Ioo] at ha
  rw [Lam_one (show 1 ≤ a by omega), Lam_one (show 1 ≤ m - a by omega), mul_one]

/-- With the constant profile `1`, two marked cut points give the threefold convolution of
`ren`. -/
private theorem Lam2_one (m : ℕ) :
    Lam2 (fun _ => (1 : ℝ)) m
      = ∑ b ∈ Ioo 0 m, (∑ a ∈ Ioo 0 b, ren a * ren (b - a)) * ren (m - b) := by
  unfold Lam2
  refine Finset.sum_congr rfl fun b hb => ?_
  rw [mem_Ioo] at hb
  rw [Lam1_one, Lam_one (show 1 ≤ m - b by omega), mul_one]

/-- `∑_{0<a<m} ren a · ren (m-a) = ren m · (s_m - 1)`. -/
private theorem ren_conv2 {m : ℕ} (hm : 1 ≤ m) :
    ∑ a ∈ Ioo 0 m, ren a * ren (m - a) = ren m * (sbirth m - 1) := by
  have h := sum_Tq_poly (m := m) (fun x => x - 1)
  unfold Tq at h
  have e : ∑ i ∈ range m, (((i : ℝ) + 1) - 1) * (((i : ℝ) + 1) * Pb m (i + 1))
      = ∑ i ∈ range m, (i : ℝ) * (((i : ℝ) + 1) * Pb m (i + 1)) :=
    Finset.sum_congr rfl fun i _ => by ring
  rw [← Lam1_one, Lam1_eq_sum, h, e, Pb_factorial_moment hm, ren_eq_mul_cay hm]
  ring

/-- `∑_{0<b<m} (∑_{0<a<b} ren a · ren (b-a)) · ren (m-b) = ren m · (m + 1 - 2 s_m)`. -/
private theorem ren_conv3 {m : ℕ} (hm : 1 ≤ m) :
    ∑ b ∈ Ioo 0 m, (∑ a ∈ Ioo 0 b, ren a * ren (b - a)) * ren (m - b)
      = ren m * ((m : ℝ) + 1 - 2 * sbirth m) := by
  have h := sum_Tq_poly (m := m) (fun x => (x - 1) * (x - 2) / 2)
  unfold Tq at h
  have e : ∑ i ∈ range m, (((i : ℝ) + 1) - 1) * (((i : ℝ) + 1) - 2) / 2
        * (((i : ℝ) + 1) * Pb m (i + 1))
      = 1 / 2 * ∑ i ∈ range m, ((i : ℝ) + 1) ^ 2 * (i : ℝ) * Pb m (i + 1)
        - ∑ i ∈ range m, (i : ℝ) * (((i : ℝ) + 1) * Pb m (i + 1)) := by
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    exact Finset.sum_congr rfl fun i _ => by ring
  rw [← Lam2_one, Lam2_eq_sum, h, e, Pb_sum3 hm, Pb_factorial_moment hm, ren_eq_mul_cay hm]
  ring

/-- `κ₂(m) = e^{-m} · ∑_{0<g<m} ren g · ren (m-g)`. -/
private theorem kc2_eq_ren (m : ℕ) :
    kc2 m = Real.exp (-(m : ℝ)) * ∑ g ∈ Ioo 0 m, ren g * ren (m - g) := by
  unfold kc2
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl fun g hg => poissonMass_mul (mem_Ioo.1 hg).2.le

/-- **The closed form of `κ₂`.** `κ₂(m) = P(m) · (s_m - 1)` for `m ≥ 1`, where `s_m` is the mean of
the birthday law: `e^m κ₂(m)` is the weight of the compositions of `m` with one marked cut point
for the profile `1`, that is, `ren m` times the mean number of cut points. -/
theorem kc2_eq {m : ℕ} (hm : 1 ≤ m) : kc2 m = poissonMass m * (sbirth m - 1) := by
  rw [kc2_eq_ren, ren_conv2 hm]
  unfold poissonMass
  ring

/-- **The closed form of `κ₃`.** `κ₃(m) = (m-1) · P(m) - 2·κ₂(m)` for `m ≥ 1`: `e^m κ₃(m)` is the
weight of the compositions of `m` with two marked cut points for the profile `1`. -/
theorem kc3_eq {m : ℕ} (hm : 1 ≤ m) : kc3 m = ((m : ℝ) - 1) * poissonMass m - 2 * kc2 m := by
  have h : kc3 m = Real.exp (-(m : ℝ))
      * ∑ b ∈ Ioo 0 m, (∑ a ∈ Ioo 0 b, ren a * ren (b - a)) * ren (m - b) := by
    unfold kc3
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun b hb => ?_
    have he : Real.exp (-(b : ℝ)) * Real.exp (-((m - b : ℕ) : ℝ)) = Real.exp (-(m : ℝ)) := by
      rw [← Real.exp_add, Nat.cast_sub (mem_Ioo.1 hb).2.le]
      congr 1
      ring
    rw [kc2_eq_ren b]
    unfold poissonMass
    linear_combination ((∑ a ∈ Ioo 0 b, ren a * ren (b - a)) * ren (m - b)) * he
  rw [h, ren_conv3 hm, kc2_eq hm]
  unfold poissonMass
  ring

/-! ### Convolutions over proper splittings -/

/-- The convolution `(u ⋆ v)(m) = ∑_{0<g<m} u(g) · v(m-g)` over the proper splittings of `m`. -/
private noncomputable def cutConv (u v : ℕ → ℝ) (m : ℕ) : ℝ := ∑ g ∈ Ioo 0 m, u g * v (m - g)

private theorem cutConv_comm (u v : ℕ → ℝ) (m : ℕ) : cutConv u v m = cutConv v u m := by
  unfold cutConv
  rw [sum_Ioo_reflect _ 0 m, Nat.sub_zero]
  refine Finset.sum_congr rfl fun g hg => ?_
  rw [mem_Ioo] at hg
  rw [show m - (m - g) = g by omega, mul_comm]

private theorem cutConv_assoc (u v w : ℕ → ℝ) (m : ℕ) :
    cutConv (cutConv u v) w m = cutConv u (cutConv v w) m := by
  have h1 : cutConv (cutConv u v) w m
      = ∑ b ∈ Ioo 0 m, ∑ a ∈ Ioo 0 b, u a * v (b - a) * w (m - b) :=
    Finset.sum_congr rfl fun b _ => Finset.sum_mul _ _ _
  have h2 : cutConv u (cutConv v w) m
      = ∑ a ∈ Ioo 0 m, ∑ b ∈ Ioo a m, u a * v (b - a) * w (m - b) := by
    refine Finset.sum_congr rfl fun a _ => ?_
    unfold cutConv
    rw [Finset.mul_sum, sum_Ioo_shift _ a m]
    refine Finset.sum_congr rfl fun h _ => ?_
    rw [show a + h - a = h by omega, show m - (a + h) = m - a - h by omega]
    ring
  rw [h1, h2]
  exact Finset.sum_comm' (by intro x y; simp only [mem_Ioo]; omega)

/-- The moment `g ↦ g · u(g)` acts on the convolution as a derivation:
`(g·u) ⋆ v + u ⋆ (g·v) = m · (u ⋆ v)`. -/
private theorem cutConv_mom (u v : ℕ → ℝ) (m : ℕ) :
    cutConv (fun g => (g : ℝ) * u g) v m + cutConv u (fun g => (g : ℝ) * v g) m
      = (m : ℝ) * cutConv u v m := by
  unfold cutConv
  rw [← Finset.sum_add_distrib, Finset.mul_sum]
  refine Finset.sum_congr rfl fun g hg => ?_
  show (g : ℝ) * u g * v (m - g) + u g * (((m - g : ℕ) : ℝ) * v (m - g))
    = (m : ℝ) * (u g * v (m - g))
  rw [Nat.cast_sub (mem_Ioo.1 hg).2.le]
  ring

private theorem cutConv_smul_left (c : ℝ) (u v : ℕ → ℝ) (m : ℕ) :
    cutConv (fun g => c * u g) v m = c * cutConv u v m := by
  unfold cutConv
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl fun g _ => by ring

private theorem cutConv_smul_right (c : ℝ) (u v : ℕ → ℝ) (m : ℕ) :
    cutConv u (fun g => c * v g) m = c * cutConv u v m := by
  unfold cutConv
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl fun g _ => by ring

/-- A convolution with a moment, written as a sum. -/
private theorem cutConv_mom_eq (u v : ℕ → ℝ) (m : ℕ) :
    cutConv (fun g => (g : ℝ) * u g) v m = ∑ g ∈ Ioo 0 m, (g : ℝ) * (u g * v (m - g)) :=
  Finset.sum_congr rfl fun g _ => by ring

/-! ### Moments -/

/-- `(g·P) ⋆ P = (m/2) · κ₂`. -/
private theorem kc2_mom_conv (m : ℕ) :
    cutConv (fun g => (g : ℝ) * poissonMass g) poissonMass m = (m : ℝ) / 2 * kc2 m := by
  have h1 := cutConv_mom poissonMass poissonMass m
  have h2 := cutConv_comm poissonMass (fun g => (g : ℝ) * poissonMass g) m
  show _ = (m : ℝ) / 2 * cutConv poissonMass poissonMass m
  linear_combination (1 / 2 : ℝ) * h1 - (1 / 2 : ℝ) * h2

/-- **The mean position in `κ₂`.** `∑_{0<g<m} g · P(g) · P(m-g) = (m/2) · κ₂(m)`: the two factors
of the convolution are exchangeable. -/
theorem kc2_mom (m : ℕ) :
    ∑ g ∈ Ioo 0 m, (g : ℝ) * (poissonMass g * poissonMass (m - g)) = (m : ℝ) / 2 * kc2 m :=
  (cutConv_mom_eq poissonMass poissonMass m).symm.trans (kc2_mom_conv m)

/-- `κ₃` with the factors in the other order: `∑_{0<a<m} P(a) · κ₂(m-a) = κ₃(m)`. -/
theorem kc3_comm (m : ℕ) : ∑ a ∈ Ioo 0 m, poissonMass a * kc2 (m - a) = kc3 m :=
  cutConv_comm poissonMass kc2 m

/-- `(g·κ₂) ⋆ P = 2 · κ₂ ⋆ (g·P)`: by `kc2_mom_conv`, `g·κ₂ = 2 · (g·P) ⋆ P`, and the convolution
is associative and commutative. -/
private theorem kc3_mom_aux (m : ℕ) :
    cutConv (fun g => (g : ℝ) * kc2 g) poissonMass m
      = 2 * cutConv kc2 (fun g => (g : ℝ) * poissonMass g) m := by
  have e : (fun g : ℕ => (g : ℝ) * kc2 g)
      = fun g => 2 * cutConv (fun g => (g : ℝ) * poissonMass g) poissonMass g :=
    funext fun g => by rw [kc2_mom_conv]; ring
  rw [e, cutConv_smul_left, cutConv_assoc,
    cutConv_comm (fun g => (g : ℝ) * poissonMass g) (cutConv poissonMass poissonMass)]
  rfl

/-- `(g·κ₂) ⋆ P = (2m/3) · κ₃`. -/
private theorem kc3_mom_left_conv (m : ℕ) :
    cutConv (fun g => (g : ℝ) * kc2 g) poissonMass m = 2 * (m : ℝ) / 3 * kc3 m := by
  have h1 := cutConv_mom kc2 poissonMass m
  have h2 := kc3_mom_aux m
  show _ = 2 * (m : ℝ) / 3 * cutConv kc2 poissonMass m
  linear_combination (2 / 3 : ℝ) * h1 + (1 / 3 : ℝ) * h2

/-- **The mean position of the first two factors in `κ₃`.**
`∑_{0<a<m} a · κ₂(a) · P(m-a) = (2m/3) · κ₃(m)`. -/
theorem kc3_mom_left (m : ℕ) :
    ∑ a ∈ Ioo 0 m, (a : ℝ) * (kc2 a * poissonMass (m - a)) = 2 * (m : ℝ) / 3 * kc3 m :=
  (cutConv_mom_eq kc2 poissonMass m).symm.trans (kc3_mom_left_conv m)

/-- **The mean position of the first factor in `κ₃`.**
`∑_{0<a<m} a · P(a) · κ₂(m-a) = (m/3) · κ₃(m)`. -/
theorem kc3_mom_right (m : ℕ) :
    ∑ a ∈ Ioo 0 m, (a : ℝ) * (poissonMass a * kc2 (m - a)) = (m : ℝ) / 3 * kc3 m := by
  have h1 := cutConv_mom kc2 poissonMass m
  have h2 := kc3_mom_aux m
  have h3 := cutConv_comm (fun g => (g : ℝ) * poissonMass g) kc2 m
  rw [← cutConv_mom_eq]
  show _ = (m : ℝ) / 3 * cutConv kc2 poissonMass m
  linear_combination (1 / 3 : ℝ) * h1 - (1 / 3 : ℝ) * h2 + h3

/-! ### The weights of the impulse side -/

/-- **The sum of the impulse weights.**
`∑_{0<s<R} P(R-s) · (R-1-s) · κ₂(s) = ((R-3)/3) · κ₃(R)`, by `kc3_mom_left`. -/
theorem impulse_weight_sum (R : ℕ) :
    ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
      = ((R : ℝ) - 3) / 3 * kc3 R := by
  have h1 := kc3_mom_left R
  have h3 : ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
      = ((R : ℝ) - 1) * kc3 R - ∑ s ∈ Ioo 0 R, (s : ℝ) * (kc2 s * poissonMass (R - s)) := by
    unfold kc3
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    exact Finset.sum_congr rfl fun s _ => by ring
  rw [h3, h1]
  ring

/-- `(g·κ₂) ⋆ κ₂ = (R/2) · κ₂ ⋆ κ₂`. -/
private theorem kc22_mom (R : ℕ) :
    cutConv (fun g => (g : ℝ) * kc2 g) kc2 R = (R : ℝ) / 2 * cutConv kc2 kc2 R := by
  have h1 := cutConv_mom kc2 kc2 R
  have h2 := cutConv_comm kc2 (fun g => (g : ℝ) * kc2 g) R
  linear_combination (1 / 2 : ℝ) * h1 - (1 / 2 : ℝ) * h2

/-- `(g·κ₂) ⋆ κ₃ = (2R/5) · κ₂ ⋆ κ₃`: `κ₂ ⋆ κ₃` is a fivefold convolution of `P`, of which `κ₂`
holds two factors. -/
private theorem kc23_mom (R : ℕ) :
    cutConv (fun g => (g : ℝ) * kc2 g) kc3 R = 2 * (R : ℝ) / 5 * cutConv kc2 kc3 R := by
  have h1 := cutConv_mom kc2 kc3 R
  have hX : cutConv (fun g => (g : ℝ) * kc2 g) kc3 R
      = cutConv (cutConv (fun g => (g : ℝ) * kc2 g) kc2) poissonMass R :=
    (cutConv_assoc (fun g => (g : ℝ) * kc2 g) kc2 poissonMass R).symm
  have hY : cutConv kc2 (fun g => (g : ℝ) * kc3 g) R
      = 3 / 2 * cutConv (cutConv (fun g => (g : ℝ) * kc2 g) kc2) poissonMass R := by
    have e : (fun g : ℕ => (g : ℝ) * kc3 g)
        = fun g => 3 / 2 * cutConv (fun g => (g : ℝ) * kc2 g) poissonMass g :=
      funext fun g => by rw [kc3_mom_left_conv]; ring
    have e2 : cutConv kc2 (fun g => (g : ℝ) * kc2 g)
        = cutConv (fun g => (g : ℝ) * kc2 g) kc2 :=
      funext fun g => cutConv_comm _ _ g
    rw [e, cutConv_smul_right, ← cutConv_assoc, e2]
  linear_combination (2 / 5 : ℝ) * h1 + (3 / 5 : ℝ) * hX - (2 / 5 : ℝ) * hY

/-- The impulse weight in terms of `κ₂` and `κ₃`:
`P(R-s) · (R-1-s) · κ₂(s) = κ₂(s) · (κ₃(R-s) + 2 κ₂(R-s))`, by `kc3_eq` at `R - s`. -/
private theorem impulse_weight_eq {R s : ℕ} (hs : s ∈ Ioo 0 R) :
    poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
      = kc2 s * (kc3 (R - s) + 2 * kc2 (R - s)) := by
  rw [mem_Ioo] at hs
  rw [kc3_eq (show 1 ≤ R - s by omega), Nat.cast_sub hs.2.le]
  ring

/-- **The mean position of the impulse weights.** The weights `w_s = P(R-s) · (R-1-s) · κ₂(s)`
satisfy `(2R/5) · ∑_s w_s ≤ ∑_s s · w_s`.  Indeed `w_s = κ₂(s) · (κ₃(R-s) + 2 κ₂(R-s))`; in
`κ₂ ⋆ κ₃` the factor `κ₂` has the mean position `2R/5`, and in `κ₂ ⋆ κ₂` the mean position `R/2`,
which is larger. -/
theorem impulse_weight_mean (R : ℕ) :
    2 * (R : ℝ) / 5 * ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
      ≤ ∑ s ∈ Ioo 0 R, (s : ℝ) * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s) := by
  have hA : ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s
      = cutConv kc2 kc3 R + 2 * cutConv kc2 kc2 R := by
    unfold cutConv
    rw [Finset.mul_sum, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun s hs => by rw [impulse_weight_eq hs]; ring
  have hB : ∑ s ∈ Ioo 0 R, (s : ℝ) * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)
      = cutConv (fun g => (g : ℝ) * kc2 g) kc3 R
        + 2 * cutConv (fun g => (g : ℝ) * kc2 g) kc2 R := by
    unfold cutConv
    rw [Finset.mul_sum, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun s hs => by rw [impulse_weight_eq hs]; ring
  have hB0 : 0 ≤ cutConv kc2 kc2 R :=
    Finset.sum_nonneg fun _ _ => mul_nonneg (kc2_nonneg _) (kc2_nonneg _)
  rw [hA, hB, kc22_mom R, kc23_mom R]
  nlinarith [mul_nonneg (Nat.cast_nonneg (α := ℝ) R) hB0]

end Parking
