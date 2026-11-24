module

public import Parking.Basic.Sums
public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Linarith

/-!
# The two-point persistence argument

Rows are indexed by naturals.  `k` is the bottom row, `q = k + rq` the crossing row and
`n = k + rq + t` the target row.  `η` is the (tilted) column, `U` the (tilted) profile of the
previous level, `κ` the (tilted) kernel.  Assume

* the column equation at the rows `q` and `n`
  (`η j = c_j U (j-1) + φ_j η (j-1) + ∑_{m=1}^{j-k} κ m * η (j-m)`),
* `η k = -U k` and the tilted diagonal bound `U (j-1) - U j ≤ η j` on the rows `k < j < n`,
* `κ` positive and nonincreasing on `[1, rq + t]` and the cross inequality
  `κ (m+t) κ rq ≤ κ (rq+t) κ m` for `1 ≤ m ≤ rq` (log-convexity),
* the two-point condition `κ (rq+t) c_q ≤ κ rq c_n`,
* `η ≤ 0` on the rows `k ≤ j < q` and `η > 0` on the rows `q ≤ j < n`.

Then `η n > 0`.

The proof is by contradiction.  The feedback sum at row `n` splits into the part `Pf` over the
positive rows `q … n - 1` and the part `Mn` over the nonpositive rows `k … q - 1`.  If
`η n ≤ 0`, the column equation at `n` gives `c_n U (n-1) + Pf < -Mn`.  Comparing `Mn` with the sum
of the nonpositive rows, which the diagonal bound controls by `U (q-1)`, gives `c_n < κ (t+1)`;
comparing `Mn` with the corresponding part of the column equation at `q`, through the cross
inequality and the two-point condition, gives `κ t < c_n`.  Since `κ (t+1) ≤ κ t`, the two
contradict each other.
-/

@[expose] public section

namespace Parking

open Finset

/-- Shifting the summation index: `∑_{m=t+1}^{R+t} F m = ∑_{m=1}^{R} F (m+t)`. -/
private theorem sum_Icc_shift (F : ℕ → ℝ) (t R : ℕ) :
    ∑ m ∈ Icc (t + 1) (R + t), F m = ∑ m ∈ Icc 1 R, F (m + t) := by
  rw [← Ico_add_one_right_eq_Icc, ← Ico_add_one_right_eq_Icc, sum_Ico_add' F 1 (R + 1) t,
    Nat.add_comm 1 t, Nat.add_right_comm R 1 t]

/-- Telescoping lower bound from the tilted diagonal bound:
`U (N-1-s) - U (N-1) ≤ ∑_{m=1}^{s} η (N-m)` as long as the rows involved lie above `k`. -/
private theorem tp_tele (η U : ℕ → ℝ) (k N : ℕ)
    (hDg : ∀ j, k + 1 ≤ j → j + 1 ≤ N → U (j - 1) - U j ≤ η j) :
    ∀ s, s + k + 1 ≤ N → U (N - 1 - s) - U (N - 1) ≤ ∑ m ∈ Icc 1 s, η (N - m) := by
  intro s
  induction s with
  | zero =>
    intro _
    have h0 : Icc 1 0 = (∅ : Finset ℕ) := Icc_eq_empty_of_lt (by omega)
    exact le_of_eq (by rw [h0, sum_empty, Nat.sub_zero, sub_self])
  | succ s ih =>
    intro hs
    have h1 := ih (by omega)
    have h2 := hDg (N - (s + 1)) (by omega) (by omega)
    have hU1 : U (N - (s + 1) - 1) = U (N - 1 - (s + 1)) := congrArg U (by omega)
    have hU2 : U (N - (s + 1)) = U (N - 1 - s) := congrArg U (by omega)
    rw [sum_Icc_succ_top (by omega : 1 ≤ s + 1)]
    linarith [h1, h2, hU1, hU2]

/-- **Two-point persistence.** -/
theorem two_point (η U κ : ℕ → ℝ) (cq cn φq φn : ℝ) (k rq t : ℕ)
    (hrq : 1 ≤ rq) (ht : 1 ≤ t) (hcq : 0 ≤ cq) (hφq : 0 ≤ φq) (hφn : 0 < φn)
    (hCq : η (k + rq) = cq * U (k + rq - 1) + φq * η (k + rq - 1)
        + ∑ m ∈ Icc 1 rq, κ m * η (k + rq - m))
    (hCn : η (k + rq + t) = cn * U (k + rq + t - 1) + φn * η (k + rq + t - 1)
        + ∑ m ∈ Icc 1 (rq + t), κ m * η (k + rq + t - m))
    (hbase : η k = -U k)
    (hDg : ∀ j, k + 1 ≤ j → j + 1 ≤ k + rq + t → U (j - 1) - U j ≤ η j)
    (hU : ∀ j, 0 ≤ U j)
    (hκpos : ∀ m, 1 ≤ m → m ≤ rq + t → 0 < κ m)
    (hκmono : ∀ m, 1 ≤ m → m + 1 ≤ rq + t → κ (m + 1) ≤ κ m)
    (hκcross : ∀ m, 1 ≤ m → m ≤ rq → κ (m + t) * κ rq ≤ κ (rq + t) * κ m)
    (hii : κ (rq + t) * cq ≤ κ rq * cn)
    (hneg : ∀ j, k ≤ j → j < k + rq → η j ≤ 0)
    (hpos : ∀ j, k + rq ≤ j → j < k + rq + t → 0 < η j) :
    0 < η (k + rq + t) := by
  -- the kernel is nonincreasing on `[1, rq + t]`
  have hanti : ∀ a b, 1 ≤ a → a ≤ b → b ≤ rq + t → κ b ≤ κ a := by
    intro a b ha hab
    induction b, hab using Nat.le_induction with
    | base => intro _; exact le_rfl
    | succ b hab ih =>
      intro hb
      exact le_trans (hκmono b (by omega) hb) (ih (by omega))
  by_contra hcon
  have hcon' : η (k + rq + t) ≤ 0 := not_lt.mp hcon
  -- split the feedback at row `n` into the rows after and before the crossing
  have hsplit : ∑ m ∈ Icc 1 (rq + t), κ m * η (k + rq + t - m)
      = ∑ m ∈ Icc 1 t, κ m * η (k + rq + t - m)
        + ∑ m ∈ Icc (t + 1) (rq + t), κ m * η (k + rq + t - m) :=
    sum_Icc_split _ (by omega) (by omega)
  have hshift : ∑ m ∈ Icc (t + 1) (rq + t), κ m * η (k + rq + t - m)
      = ∑ m ∈ Icc 1 rq, κ (m + t) * η (k + rq - m) := by
    rw [sum_Icc_shift (fun m => κ m * η (k + rq + t - m)) t rq]
    exact sum_congr rfl fun m _ => by rw [show k + rq + t - (m + t) = k + rq - m by omega]
  -- abbreviations
  obtain ⟨Pf, hPf⟩ : ∃ Pf : ℝ, Pf = ∑ m ∈ Icc 1 t, κ m * η (k + rq + t - m) := ⟨_, rfl⟩
  obtain ⟨Mn, hMn⟩ : ∃ Mn : ℝ, Mn = ∑ m ∈ Icc 1 rq, κ (m + t) * η (k + rq - m) :=
    ⟨_, rfl⟩
  obtain ⟨Mq, hMq⟩ : ∃ Mq : ℝ, Mq = ∑ m ∈ Icc 1 rq, κ m * η (k + rq - m) := ⟨_, rfl⟩
  obtain ⟨E, hE⟩ : ∃ E : ℝ, E = ∑ m ∈ Icc 1 t, η (k + rq + t - m) := ⟨_, rfl⟩
  obtain ⟨Hn, hHn⟩ : ∃ Hn : ℝ, Hn = ∑ m ∈ Icc 1 rq, η (k + rq - m) := ⟨_, rfl⟩
  have hCn' : η (k + rq + t) = cn * U (k + rq + t - 1) + φn * η (k + rq + t - 1) + (Pf + Mn) := by
    rw [hCn, hsplit, hshift, ← hPf, ← hMn]
  have hCq' : η (k + rq) = cq * U (k + rq - 1) + φq * η (k + rq - 1) + Mq := by
    rw [hCq, ← hMq]
  -- (c) the repaid part is at least `κ t * E`
  have hc : κ t * E ≤ Pf := by
    rw [hE, hPf, mul_sum]
    refine sum_le_sum (fun m hm => ?_)
    rw [mem_Icc] at hm
    have h1 : κ t ≤ κ m := hanti m t hm.1 hm.2 (by omega)
    have h2 : 0 < η (k + rq + t - m) := hpos _ (by omega) (by omega)
    exact mul_le_mul_of_nonneg_right h1 h2.le
  -- (d) the memory at row `n` against the debt
  have hd : κ (t + 1) * Hn ≤ Mn := by
    rw [hHn, hMn, mul_sum]
    refine sum_le_sum (fun m hm => ?_)
    rw [mem_Icc] at hm
    have h1 : κ (m + t) ≤ κ (t + 1) := hanti (t + 1) (m + t) (by omega) (by omega) (by omega)
    have h2 : η (k + rq - m) ≤ 0 := hneg _ (by omega) (by omega)
    exact mul_le_mul_of_nonpos_right h1 h2
  -- (e) the memory at row `n` against the memory at row `q` (log-convexity)
  have he : κ (rq + t) * Mq ≤ κ rq * Mn := by
    rw [hMq, hMn, mul_sum, mul_sum]
    refine sum_le_sum (fun m hm => ?_)
    rw [mem_Icc] at hm
    have h1 := hκcross m hm.1 hm.2
    have h2 : η (k + rq - m) ≤ 0 := hneg _ (by omega) (by omega)
    have h3 := mul_le_mul_of_nonpos_right h1 h2
    calc κ (rq + t) * (κ m * η (k + rq - m))
        = κ (rq + t) * κ m * η (k + rq - m) := by ring
      _ ≤ κ (m + t) * κ rq * η (k + rq - m) := h3
      _ = κ rq * (κ (m + t) * η (k + rq - m)) := by ring
  -- (D2) the source does not fall by more than what was repaid
  have hE2 : U (k + rq - 1) - U (k + rq + t - 1) ≤ E := by
    have h := tp_tele η U k (k + rq + t) hDg t (by omega)
    have hU1 : U (k + rq + t - 1 - t) = U (k + rq - 1) := congrArg U (by omega)
    rw [hE]
    linarith [h, hU1]
  -- (D1) the debt is at most the profile
  have hH2 : -U (k + rq - 1) ≤ Hn := by
    obtain ⟨s, hs⟩ : ∃ s, rq = s + 1 := ⟨rq - 1, by omega⟩
    have h := tp_tele η U k (k + rq)
      (fun j hj1 hj2 => hDg j hj1 (by omega)) s (by omega)
    have hU1 : U (k + rq - 1 - s) = U k := congrArg U (by omega)
    have hη1 : η (k + rq - (s + 1)) = η k := congrArg η (by omega)
    have hsum : Hn = ∑ m ∈ Icc 1 s, η (k + rq - m) + η (k + rq - (s + 1)) := by
      rw [hHn]
      have e : Icc 1 rq = Icc 1 (s + 1) := by rw [hs]
      rw [e, sum_Icc_succ_top (by omega : 1 ≤ s + 1)]
    linarith [h, hU1, hη1, hsum, hbase]
  -- positivity facts
  have hη1 : 0 < η (k + rq + t - 1) := hpos _ (by omega) (by omega)
  have hEpos : 0 < E := by
    rw [hE]
    refine sum_pos (fun m hm => ?_) ⟨1, mem_Icc.mpr ⟨le_rfl, ht⟩⟩
    rw [mem_Icc] at hm
    exact hpos _ (by omega) (by omega)
  have hκt1 : κ (t + 1) ≤ κ t := hκmono t ht (by omega)
  have hκt1pos : 0 < κ (t + 1) := hκpos (t + 1) (by omega) (by omega)
  have hκr : 0 < κ (rq + t) := hκpos _ (by omega) le_rfl
  have hκq : 0 < κ rq := hκpos rq hrq (by omega)
  -- (*) the memory exceeds source plus repayment
  have hstar : cn * U (k + rq + t - 1) + Pf < -Mn := by
    have h := mul_pos hφn hη1
    linarith [hCn', hcon', h]
  -- the re-rise bound `cn < κ (t + 1)`
  have h1 : cn * U (k + rq + t - 1) < κ (t + 1) * U (k + rq + t - 1) := by
    have a1 : κ (t + 1) * E ≤ κ t * E := mul_le_mul_of_nonneg_right hκt1 hEpos.le
    have hEH : -(E + Hn) ≤ U (k + rq + t - 1) := by linarith [hE2, hH2]
    have a2 : κ (t + 1) * (-(E + Hn)) ≤ κ (t + 1) * U (k + rq + t - 1) :=
      mul_le_mul_of_nonneg_left hEH hκt1pos.le
    have a3 : κ (t + 1) * (-(E + Hn)) = -(κ (t + 1) * E) - κ (t + 1) * Hn := by ring
    linarith [hc, hd, hstar, a1, a2, a3]
  have hU1 : 0 < U (k + rq + t - 1) := by
    by_contra hc0
    have h0 : U (k + rq + t - 1) = 0 := le_antisymm (not_lt.mp hc0) (hU _)
    rw [h0, mul_zero, mul_zero] at h1
    exact lt_irrefl _ h1
  have hrr : cn < κ (t + 1) := by
    by_contra hc0
    have h := mul_le_mul_of_nonneg_right (not_lt.mp hc0) hU1.le
    linarith [h, h1]
  -- row `q`: the memory is smaller than the source
  have hηq : 0 < η (k + rq) := hpos _ le_rfl (by omega)
  have hηq1 : η (k + rq - 1) ≤ 0 := hneg _ (by omega) (by omega)
  have hMq' : -Mq < cq * U (k + rq - 1) := by
    have h := mul_nonneg hφq (neg_nonneg.mpr hηq1)
    have h' : φq * -η (k + rq - 1) = -(φq * η (k + rq - 1)) := by ring
    linarith [hCq', hηq, h, h']
  -- transfer to row `n` and use the two-point condition
  have h2 : -(κ rq * Mn) < κ (rq + t) * (cq * U (k + rq - 1)) := by
    have h := mul_lt_mul_of_pos_left hMq' hκr
    have h' : κ (rq + t) * -Mq = -(κ (rq + t) * Mq) := by ring
    linarith [h, h', he]
  have hUE : U (k + rq - 1) ≤ U (k + rq + t - 1) + E := by linarith [hE2]
  have hUE0 : 0 ≤ U (k + rq + t - 1) + E := by linarith [hU (k + rq + t - 1), hEpos]
  have h3 : κ (rq + t) * (cq * U (k + rq - 1)) ≤ κ rq * (cn * (U (k + rq + t - 1) + E)) := by
    calc κ (rq + t) * (cq * U (k + rq - 1))
        = κ (rq + t) * cq * U (k + rq - 1) := by ring
      _ ≤ κ (rq + t) * cq * (U (k + rq + t - 1) + E) :=
          mul_le_mul_of_nonneg_left hUE (mul_nonneg hκr.le hcq)
      _ ≤ κ rq * cn * (U (k + rq + t - 1) + E) := mul_le_mul_of_nonneg_right hii hUE0
      _ = κ rq * (cn * (U (k + rq + t - 1) + E)) := by ring
  have h4 : -Mn < cn * (U (k + rq + t - 1) + E) := by
    have h : κ rq * -Mn < κ rq * (cn * (U (k + rq + t - 1) + E)) := by
      have h' : κ rq * -Mn = -(κ rq * Mn) := by ring
      linarith [h2, h3, h']
    exact lt_of_mul_lt_mul_left h hκq.le
  -- conclusion: `κ t < cn < κ (t + 1) ≤ κ t`
  have h5 : Pf < cn * E := by
    have h' : cn * (U (k + rq + t - 1) + E) = cn * U (k + rq + t - 1) + cn * E := by ring
    linarith [hstar, h4, h']
  have h6 : κ t * E < cn * E := lt_of_le_of_lt hc h5
  have h7 : κ t < cn := lt_of_mul_lt_mul_right h6 hEpos.le
  linarith [hrr, hκt1, h7]

end Parking
