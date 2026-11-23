import Parking.LeftHalf.FirstLayer.PairSum

/-!
# The last-car recursion in the first layer

`u_N(c) = zrT c (xcrit k) N = x_k^N A_{N,c-1}/N!` is the tilted environment of the threshold `c`
(all displacements `< c`) at the critical tilt `x_k`.  For `N ≤ c` it is the tilted Cayley mass
`ω_N = ccT (xcrit k) N` (`zrT_eq_ccT`).  Its last-car recursion is `zrT_succ`,

  `(N+1) u_{N+1}(c) = x_k ∑_{j ≤ N} min(j+1, c) u_j(c) u_{N-j}(c)`.

The first layer consists of the sizes `c < N + 1 ≤ 2c + 1`; write `N = c + P` with `P ≤ c`.  Then
at most one of the two pieces `j`, `N - j` is larger than `c`, and `zrT_split` sorts the sum
accordingly:

  `(c+P+1) u_{c+P+1}(c) = x_k ( ∑_{i < P} (c+i+1) ω_i u_{c+P-i}(c) + direct k c P )`.

The first sum is the *chain part*: one piece `i < P` is free and the other is again a first-layer
mass, of smaller excess.  `direct k c P` is the *direct part*, the terms `P ≤ j ≤ c`, in which both
pieces are free.  It is a symmetric sum of products of tilted Cayley numbers; for `P + 2 ≤ c` it
consists of the two boundary terms and of the pair sum with the mean weight (`direct_generic`):

  `direct k c P = (c+P+1) ω_P ω_c + ((c+P+2)/2) · pairT k (P+1) (c-P-2)`.
-/

namespace Parking.FirstLayer
open Real Finset

/-- The direct part of the last-car recursion at size `c + P + 1`, threshold `c`: the terms in
which both pieces have size at most `c`. -/
noncomputable def direct (k c P : ℕ) : ℝ :=
  ∑ a ∈ range (c + 1 - P), ((min (P + a + 1) c : ℕ) : ℝ) * ccT (xcrit k) (P + a)
      * ccT (xcrit k) (c - a)

/-! ### Splitting the recursion -/

/-- A sum over `[0, c+P]` split into `[0, P)`, `[P, c]` and the reflected `(c, c+P]`. -/
private theorem sum_three (g : ℕ → ℝ) (c P : ℕ) (hP : P ≤ c) :
    ∑ j ∈ range (c + P + 1), g j =
      ∑ j ∈ range P, g j + ∑ a ∈ range (c + 1 - P), g (P + a) +
        ∑ i ∈ range P, g (c + P - i) := by
  have hA : ∑ j ∈ range (c + 1), g j =
      ∑ j ∈ range P, g j + ∑ a ∈ range (c + 1 - P), g (P + a) := by
    have h := Finset.sum_range_add g P (c + 1 - P)
    rwa [show P + (c + 1 - P) = c + 1 by omega] at h
  have hB : ∑ x ∈ range P, g (c + 1 + x) = ∑ i ∈ range P, g (c + P - i) := by
    refine (Finset.sum_range_reflect (fun x => g (c + 1 + x)) P).symm.trans ?_
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    show g (c + 1 + (P - 1 - i)) = g (c + P - i)
    rw [show c + 1 + (P - 1 - i) = c + P - i by omega]
  have hT := Finset.sum_range_add g (c + 1) P
  rw [show c + 1 + P = c + P + 1 by omega] at hT
  rw [hT, hA, hB]

/-- **The last-car recursion in the first layer**, sorted into the chain part and the direct
part. -/
theorem zrT_split {k c P : ℕ} (hc : 1 ≤ c) (hP : P ≤ c) :
    ((c : ℝ) + P + 1) * zrT c (xcrit k) (c + P + 1) =
      xcrit k *
        (∑ i ∈ range P, ((c : ℝ) + i + 1) * ccT (xcrit k) i * zrT c (xcrit k) (c + (P - i)) +
          direct k c P) := by
  have hrec := zrT_succ hc (xcrit k) (c + P)
  rw [Nat.cast_add] at hrec
  rw [hrec, sum_three _ c P hP]
  congr 1
  -- the two outer ranges: one piece `i < P` is free, the other has size `c + (P - i) > c`
  have h13 : ∑ j ∈ range P, ((min (j + 1) c : ℕ) : ℝ) * zrT c (xcrit k) j
      * zrT c (xcrit k) (c + P - j) +
      ∑ i ∈ range P, ((min (c + P - i + 1) c : ℕ) : ℝ) * zrT c (xcrit k) (c + P - i) *
        zrT c (xcrit k) (c + P - (c + P - i)) =
      ∑ i ∈ range P, ((c : ℝ) + i + 1) * ccT (xcrit k) i * zrT c (xcrit k) (c + (P - i)) := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    rw [show min (i + 1) c = i + 1 by omega, show min (c + P - i + 1) c = c by omega,
      show c + P - (c + P - i) = i by omega, show c + P - i = c + (P - i) by omega,
      zrT_eq_ccT hc (xcrit k) (by omega : i ≤ c)]
    push_cast
    ring
  -- the middle range: both pieces are free
  have h2 : ∑ a ∈ range (c + 1 - P),
      ((min (P + a + 1) c : ℕ) : ℝ) * zrT c (xcrit k) (P + a) * zrT c (xcrit k) (c + P - (P + a)) =
      direct k c P := by
    refine Finset.sum_congr rfl fun a ha => ?_
    rw [Finset.mem_range] at ha
    rw [show c + P - (P + a) = c - a by omega, zrT_eq_ccT hc (xcrit k) (by omega : P + a ≤ c),
      zrT_eq_ccT hc (xcrit k) (by omega : c - a ≤ c)]
  linarith

/-! ### The direct part -/

/-- A weighted sum of a reflection-symmetric sequence. -/
private theorem sum_sym_weight (F : ℕ → ℝ) (L : ℕ) (α : ℝ)
    (hF : ∀ b, b < L → F (L - 1 - b) = F b) :
    ∑ b ∈ range L, (α + (b : ℝ)) * F b = (2 * α + (L : ℝ) - 1) / 2 * ∑ b ∈ range L, F b := by
  have h1 : ∑ b ∈ range L, (α + (b : ℝ)) * F b =
      ∑ b ∈ range L, (α + ((L - 1 - b : ℕ) : ℝ)) * F b := by
    refine (Finset.sum_range_reflect (fun b => (α + (b : ℝ)) * F b) L).symm.trans ?_
    refine Finset.sum_congr rfl fun b hb => ?_
    rw [Finset.mem_range] at hb
    show (α + ((L - 1 - b : ℕ) : ℝ)) * F (L - 1 - b) = (α + ((L - 1 - b : ℕ) : ℝ)) * F b
    rw [hF b hb]
  have h2 : ∑ b ∈ range L, (α + (b : ℝ)) * F b +
      ∑ b ∈ range L, (α + ((L - 1 - b : ℕ) : ℝ)) * F b =
      (2 * α + (L : ℝ) - 1) * ∑ b ∈ range L, F b := by
    rw [← Finset.sum_add_distrib, Finset.mul_sum]
    refine Finset.sum_congr rfl fun b hb => ?_
    rw [Finset.mem_range] at hb
    rw [Nat.cast_sub (by omega), Nat.cast_sub (by omega), Nat.cast_one]
    ring
  linarith

/-- The direct part when the excess is at most `c - 1`: the two boundary terms, and the pair sum
with the mean weight `(c+P+2)/2`. -/
theorem direct_generic {k c P : ℕ} (hP : P + 2 ≤ c) :
    direct k c P = ((c : ℝ) + P + 1) * ccT (xcrit k) P * ccT (xcrit k) c +
      ((c : ℝ) + P + 2) / 2 * pairT k (P + 1) (c - P - 2) := by
  obtain ⟨L, hL⟩ : ∃ L, c = P + 1 + L := ⟨c - P - 1, by omega⟩
  have hL1 : 1 ≤ L := by omega
  unfold direct
  rw [show c + 1 - P = L + 1 + 1 by omega, Finset.sum_range_succ, Finset.sum_range_succ']
  -- the first term `a = 0`
  have t0 : ((min (P + 0 + 1) c : ℕ) : ℝ) * ccT (xcrit k) (P + 0) * ccT (xcrit k) (c - 0) =
      ((P : ℝ) + 1) * ccT (xcrit k) P * ccT (xcrit k) c := by
    rw [show min (P + 0 + 1) c = P + 1 by omega, show P + 0 = P from rfl, show c - 0 = c from rfl]
    push_cast
    ring
  -- the last term `a = L + 1`
  have t1 : ((min (P + (L + 1) + 1) c : ℕ) : ℝ) * ccT (xcrit k) (P + (L + 1))
      * ccT (xcrit k) (c - (L + 1)) =
      (c : ℝ) * ccT (xcrit k) c * ccT (xcrit k) P := by
    rw [show min (P + (L + 1) + 1) c = c by omega, show P + (L + 1) = c by omega,
      show c - (L + 1) = P by omega]
  -- the middle terms
  have tmid : ∀ b ∈ range L,
      ((min (P + (b + 1) + 1) c : ℕ) : ℝ) * ccT (xcrit k) (P + (b + 1))
          * ccT (xcrit k) (c - (b + 1)) =
      ((P : ℝ) + 2 + (b : ℝ)) * (ccT (xcrit k) (P + 1 + b)
          * ccT (xcrit k) (P + 1 + (L - 1 - b))) := by
    intro b hb
    rw [Finset.mem_range] at hb
    rw [show min (P + (b + 1) + 1) c = P + b + 2 by omega, show P + (b + 1) = P + 1 + b by omega,
      show c - (b + 1) = P + 1 + (L - 1 - b) by omega]
    push_cast
    ring
  rw [t0, t1, Finset.sum_congr rfl tmid]
  -- symmetrize the middle sum
  have hsym : ∑ b ∈ range L, ((P : ℝ) + 2 + (b : ℝ)) *
        (ccT (xcrit k) (P + 1 + b) * ccT (xcrit k) (P + 1 + (L - 1 - b))) =
      (2 * ((P : ℝ) + 2) + (L : ℝ) - 1) / 2 *
        ∑ b ∈ range L, ccT (xcrit k) (P + 1 + b) * ccT (xcrit k) (P + 1 + (L - 1 - b)) :=
    sum_sym_weight (fun b => ccT (xcrit k) (P + 1 + b) * ccT (xcrit k) (P + 1 + (L - 1 - b))) L
    ((P : ℝ) + 2) (by
      intro b hb
      show ccT (xcrit k) (P + 1 + (L - 1 - b)) * ccT (xcrit k) (P + 1 + (L - 1 - (L - 1 - b))) =
        ccT (xcrit k) (P + 1 + b) * ccT (xcrit k) (P + 1 + (L - 1 - b))
      rw [show L - 1 - (L - 1 - b) = b by omega, mul_comm])
  have hpair : pairT k (P + 1) (c - P - 2) =
      ∑ b ∈ range L, ccT (xcrit k) (P + 1 + b) * ccT (xcrit k) (P + 1 + (L - 1 - b)) := by
    rw [show c - P - 2 = L - 1 by omega, pairT_eq, show L - 1 + 1 = L by omega]
  have hcL : (c : ℝ) = (P : ℝ) + 1 + L := by
    rw [hL]
    push_cast
    ring
  rw [hpair, hsym, hcL]
  ring

end Parking.FirstLayer