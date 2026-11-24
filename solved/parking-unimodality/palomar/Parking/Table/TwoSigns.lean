module

public import Parking.Counting.SingleChain
public import Parking.Table.Basic

/-!
# The table of two signs in the columns `9 ≤ k ≤ 264`

`b n ℓ` and `A n k` are the numbers of `Parking/Defs.lean`, and `d_{n,k} = b n k - b n (k-1)`.
Write `P n = (n+1)^(n-1)` for the number of parking functions of length `n`, and

  `Uf y n = P n - A n (y-1)`

for the number of parking functions of length `n` with some displacement `≥ y`.  For
`1 ≤ y < n ≤ 2y+1` the forward form of the single-chain formula (`Parking.IsWSol.fwd`) reads, in
natural numbers,

  `Uf y n = ∑_{t=y+1}^{n} C(n,t) · P(n-t) · Wf y t`,   `Wf y t = (t-y) · P(t-1) + y · Uf y (t-1)`.

The table is computed with this recursion:

* `conv n ws i c` : with `c = C(n,i)` and `ws = [w_0, w_1, …]`, the sum
  `∑_j C(n,i+j) · P(i+j) · w_j`; the binomial coefficient is updated by
  `C(n,i+1) = C(n,i) · (n-i) / (i+1)`.
* `urows y cnt n wrev` : with `wrev = [Wf y n, Wf y (n-1), …, Wf y (y+1)]`, the list
  `[Uf y n, Uf y (n+1), …]` of length `cnt`.
* `ucol y cnt = [Uf y (y+1), …, Uf y (y+cnt)]`.
* `ztab k` : the number `z` listed for the column `k` (`9 ≤ k ≤ 264`); the row `k + z + 1` is a
  row in which the column `k` is positive.
* `chk2 k z` : the Boolean check of column `k` with `z`: `2 ≤ z`, `z + 2 ≤ k`, and two signs,

    (i)  `d_{q,k} > 0` in the row `q = k + z + 1`,  i.e. `Uf (k+1) q + Uf (k-1) q < 2·Uf k q`;
    (ii) `d_{n,k+1} < 0` in the row `n = k + z`,    i.e. `2·Uf (k+1) n < Uf (k+2) n + Uf k n`.

The primitive operations are written as `Nat.add`, `Nat.mul`, … so that the kernel's built-in
arithmetic on numerals applies directly; the functions are only ever evaluated by the kernel
(`decide +kernel`), on sixteen blocks of sixteen columns each.  Their meaning is proved here:

* `urows_eq_ul`, `chk2_spec` : about the functions alone, `urows` returns the list of values of
  any two functions `U`, `W` that satisfy the two relations of the recursion, and what
  `chk2 k z = true` says about the lists;
* `Uf_fwd` : the single-chain forward formula in natural numbers;
* `conv_wl`, `conv_Wf` : the function `conv` computes the sum of that formula;
* `ucol_spec`, `nth_ucol` : `ucol y cnt = [Uf y (y+1), …, Uf y (y+cnt)]` for `1 ≤ y`,
  `cnt ≤ y+1`;
* `d_eq` : `b n c - b n (c-1) = 2·Uf c n - Uf (c+1) n - Uf (c-1) n` for `c ≥ 2`;
* `chk2_facts` : `chk2 k z = true` gives `z + 2 ≤ k`, `d_{k+z+1,k} > 0` and `d_{k+z,k+1} < 0`;
* `two_signs` : **the table statement.**  For `9 ≤ k ≤ 264` and `z = ztab k`: `z + 2 ≤ k`, the
  column `k` is positive in the row `k + z + 1`, and the column `k + 1` is negative in the row
  `k + z`;
* `ztab_27` : `100 (ztab k + 1) ≤ 27 k` for `82 ≤ k ≤ 264`, a bound on the listed positive row
  `k + ztab k + 1` (arithmetic on the list `zs`).
-/

@[expose] public section

namespace Parking
namespace Tab

open Finset

/-! ### The forward chain lists -/

/-- `P n = (n+1)^(n-1)`. -/
private def P (n : Nat) : Nat := Nat.pow (Nat.succ n) (Nat.pred n)

/-- `conv n [w_0, w_1, …] i c = ∑_j c_j · P (i+j) · w_j`, where `c_0 = c` and
`c_{j+1} = c_j · (n - (i+j)) / (i+j+1)`.  With `c = C(n,i)` this is
`∑_j C(n,i+j) · P(i+j) · w_j`. -/
private def conv (n : Nat) : List Nat → Nat → Nat → Nat
  | [], _, _ => 0
  | w :: ws, i, c =>
    Nat.add (Nat.mul (Nat.mul c (P i)) w)
      (conv n ws (Nat.succ i) (Nat.div (Nat.mul c (Nat.sub n i)) (Nat.succ i)))

/-- `urows y cnt n wrev`: `cnt` rows of the recursion
`u = conv n wrev 0 1`, next `wrev = ((n+1-y) · P n + y · u) :: wrev`, next `n = n+1`. -/
private def urows (y : Nat) : Nat → Nat → List Nat → List Nat
  | 0, _, _ => []
  | Nat.succ cnt, n, wrev =>
    let u := conv n wrev 0 1
    u :: urows y cnt (Nat.succ n)
      (Nat.add (Nat.mul (Nat.sub (Nat.succ n) y) (P n)) (Nat.mul y u) :: wrev)

/-- `ucol y cnt`: the first `cnt` rows, starting at row `y + 1` with `wrev = [P y]`. -/
private def ucol (y cnt : Nat) : List Nat := urows y cnt (Nat.succ y) [P y]

/-! ### The two signs of a column -/

/-- The two signs of column `k` with `z`: `2 ≤ z`, `z + 2 ≤ k`,
`U(q,k+1) + U(q,k-1) < 2·U(q,k)` for `q = k + z + 1` (i.e. `d_{q,k} > 0`), and
`2·U(n,k+1) < U(n,k+2) + U(n,k)` for `n = k + z` (i.e. `d_{n,k+1} < 0`). -/
private def chk2 (k z : Nat) : Bool :=
  let u0 := ucol (Nat.pred k) (Nat.succ (Nat.succ z))
  let u1 := ucol k (Nat.succ z)
  let u2 := ucol (Nat.succ k) z
  let u3 := 0 :: ucol (Nat.succ (Nat.succ k)) (Nat.pred (Nat.pred z))
  Nat.ble 2 z && Nat.ble (Nat.succ (Nat.succ z)) k
    && Nat.blt (Nat.add (nth u2 (Nat.pred z)) (nth u0 (Nat.succ z))) (Nat.mul 2 (nth u1 z))
    && Nat.blt (Nat.mul 2 (nth u2 (Nat.pred (Nat.pred z))))
        (Nat.add (nth u3 (Nat.pred (Nat.pred z))) (nth u1 (Nat.pred z)))

/-- The numbers `z` of the columns `k = 9, …, 264` (sixteen columns per line). -/
def zs : List Nat :=
  [7, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10,
   10, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 13,
   13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15,
   15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17,
   17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19,
   19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21, 21, 21,
   21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22,
   23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24,
   24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 26,
   26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 27, 27, 27, 27, 27, 27,
   27, 27, 27, 27, 27, 27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28,
   28, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 30, 30, 30,
   30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 31, 31, 31, 31, 31, 31,
   31, 31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
   32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33,
   34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35]

/-- `ztab k`: the number `z` listed for the column `k` (`9 ≤ k ≤ 264`). -/
def ztab (k : Nat) : Nat := nth zs (k - 9)

/-- The check of column `k` with `z = ztab k`. -/
private def chk2T (k : Nat) : Bool := chk2 k (ztab k)

/-! ### The definitions in ordinary notation -/

private theorem conv_cons (n w : Nat) (ws : List Nat) (i c : Nat) :
    conv n (w :: ws) i c = c * P i * w + conv n ws (i + 1) (c * (n - i) / (i + 1)) := rfl

private theorem urows_succ (y cnt n : Nat) (wrev : List Nat) :
    urows y (cnt + 1) n wrev =
      conv n wrev 0 1 ::
        urows y cnt (n + 1) (((n + 1 - y) * P n + y * conv n wrev 0 1) :: wrev) := rfl

private theorem nth_cons_zero (a : Nat) (l : List Nat) : nth (a :: l) 0 = a := rfl

private theorem nth_cons_succ (a : Nat) (l : List Nat) (i : Nat) : nth (a :: l) (i + 1)
    = nth l i := rfl

private theorem chk2_eq (k z : Nat) : chk2 k z =
    (Nat.ble 2 z && Nat.ble (z + 2) k
      && Nat.blt (nth (ucol (k + 1) z) (z - 1) + nth (ucol (k - 1) (z + 2)) (z + 1))
          (2 * nth (ucol k (z + 1)) z)
      && Nat.blt (2 * nth (ucol (k + 1) z) (z - 2))
          (nth (0 :: ucol (k + 2) (z - 2)) (z - 2) + nth (ucol k (z + 1)) (z - 1))) := rfl

/-- What `chk2 k z = true` says about the lists `ucol`. -/
private theorem chk2_spec {k z : Nat} (h : chk2 k z = true) :
    2 ≤ z ∧ z + 2 ≤ k ∧
    nth (ucol (k + 1) z) (z - 1) + nth (ucol (k - 1) (z + 2)) (z + 1)
      < 2 * nth (ucol k (z + 1)) z ∧
    2 * nth (ucol (k + 1) z) (z - 2)
      < nth (0 :: ucol (k + 2) (z - 2)) (z - 2) + nth (ucol k (z + 1)) (z - 1) := by
  rw [chk2_eq] at h
  simp only [Bool.and_eq_true, Nat.ble_eq, Nat.blt_eq] at h
  obtain ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ := h
  exact ⟨h1, h2, h3, h4⟩

/-! ### The lists the recursion works with -/

/-- `wl W y m = [W (y+m), W (y+m-1), …, W (y+1)]`. -/
private def wl (W : Nat → Nat) (y : Nat) : Nat → List Nat
  | 0 => []
  | m + 1 => W (y + m + 1) :: wl W y m

/-- `ul U cnt n = [U n, U (n+1), …, U (n+cnt-1)]`. -/
private def ul (U : Nat → Nat) : Nat → Nat → List Nat
  | 0, _ => []
  | cnt + 1, n => U n :: ul U cnt (n + 1)

private theorem nth_ul (U : Nat → Nat) :
    ∀ (cnt n i : Nat), i < cnt → nth (ul U cnt n) i = U (n + i) := by
  intro cnt
  induction cnt with
  | zero =>
    intro n i h
    omega
  | succ cnt ih =>
    intro n i h
    cases i with
    | zero => rfl
    | succ i =>
      have e : n + (i + 1) = n + 1 + i := by omega
      rw [e]
      exact ih (n + 1) i (by omega)

/-- If `U` and `W` satisfy the two relations of the recursion on the rows `y + m ≤ B`, then `urows`
started at the row `y + m` with `wrev = [W (y+m), …, W (y+1)]` returns the values of `U`. -/
private theorem urows_eq_ul (U W : Nat → Nat) (y B : Nat)
    (hconv : ∀ m, 1 ≤ m → y + m ≤ B → conv (y + m) (wl W y m) 0 1 = U (y + m))
    (hW : ∀ m, 1 ≤ m → y + m ≤ B →
      W (y + m + 1) = (y + m + 1 - y) * P (y + m) + y * U (y + m)) :
    ∀ (cnt m : Nat), 1 ≤ m → y + m + cnt ≤ B + 1 →
      urows y cnt (y + m) (wl W y m) = ul U cnt (y + m) := by
  intro cnt
  induction cnt with
  | zero =>
    intro m _ _
    rfl
  | succ cnt ih =>
    intro m hm hB
    have h1 := hconv m hm (by omega)
    have h2 := hW m hm (by omega)
    have h3 : urows y cnt (y + m + 1) (W (y + m + 1) :: wl W y m) = ul U cnt (y + m + 1) :=
      ih (m + 1) (by omega) (by omega)
    rw [urows_succ, h1, ← h2, h3]
    rfl

/-! ### The numbers computed -/

/-- `P n = (n+1)^(n-1)`, the number of parking functions of length `n`. -/
private theorem P_eq (n : ℕ) : P n = (n + 1) ^ (n - 1) := by rfl

/-- `A n k = P n` as soon as `n ≤ k + 1`. -/
private theorem A_eq_P {n k : ℕ} (h : n ≤ k + 1) : A n k = P n := by
  rw [P_eq]
  exact A_eq_pow h

/-- `Uf y n = (n+1)^(n-1) - A n (y-1)`: the number of parking functions of length `n` with some
displacement `≥ y` (for `y ≥ 1`). -/
private def Uf (y n : ℕ) : ℕ := P n - A n (y - 1)

/-- `Wf y t = (t-y) · P(t-1) + y · Uf y (t-1)`; for `t ≥ y` this is
`t · P(t-1) - y · A (t-1) (y-1)`. -/
private def Wf (y t : ℕ) : ℕ := (t - y) * P (t - 1) + y * Uf y (t - 1)

private theorem A_le_P (n k : ℕ) : A n k ≤ P n :=
  calc A n k ≤ A n (max k n) := A_mono n (le_max_left k n)
    _ = P n := A_eq_P (le_trans (le_max_right k n) (Nat.le_succ _))

private theorem Uf_add (y n : ℕ) : Uf y n + A n (y - 1) = P n :=
  Nat.sub_add_cancel (A_le_P n (y - 1))

private theorem Uf_eq_zero {y n : ℕ} (hy : 1 ≤ y) (h : n ≤ y) : Uf y n = 0 := by
  have hA : A n (y - 1) = P n := A_eq_P (show n ≤ y - 1 + 1 by omega)
  have hU : Uf y n = P n - A n (y - 1) := rfl
  rw [hU, hA]
  exact Nat.sub_self _

private theorem Uf_cast (y n : ℕ) : (Uf y n : ℝ) = (P n : ℝ) - (A n (y - 1) : ℝ) := by
  have hU : Uf y n = P n - A n (y - 1) := rfl
  rw [hU]
  exact Nat.cast_sub (A_le_P n (y - 1))

private theorem Wf_cast {y t : ℕ} (hyt : y ≤ t) :
    (Wf y t : ℝ) = (t : ℝ) * (P (t - 1) : ℝ) - (y : ℝ) * (A (t - 1) (y - 1) : ℝ) := by
  have hW : Wf y t = (t - y) * P (t - 1) + y * Uf y (t - 1) := rfl
  rw [hW, Nat.cast_add, Nat.cast_mul, Nat.cast_mul, Nat.cast_sub hyt, Uf_cast]
  ring

/-! ### The single-chain forward formula in natural numbers -/

/-- `c_m = P m / m!`. -/
private theorem cc_eq_P (m : ℕ) : cc m = (P m : ℝ) / (m.factorial : ℝ) := by
  have h : zr (m + 1) m = cc m := zr_eq_cc (Nat.succ_pos m) (Nat.le_succ m)
  have hA : A m (m + 1 - 1) = P m := A_eq_P (show m ≤ m + 1 - 1 + 1 by omega)
  have hz : zr (m + 1) m = (A m (m + 1 - 1) : ℝ) / (m.factorial : ℝ) := rfl
  rw [← h, hz, hA]

/-- One term of the forward formula, multiplied by `n!`. -/
private theorem fwd_term {y n t : ℕ} (hy : y < t) (ht : t ≤ n) :
    (n.factorial : ℝ) * (cc (n - t) * (cc (t - 1) - (y : ℝ) / (t : ℝ) * zr y (t - 1)))
      = ((n.choose t * P (n - t) * Wf y t : ℕ) : ℝ) := by
  have ht0 : t ≠ 0 := by omega
  have hC : (n.choose t : ℝ) * (t.factorial : ℝ) * ((n - t).factorial : ℝ)
      = (n.factorial : ℝ) := by
    exact_mod_cast Nat.choose_mul_factorial_mul_factorial ht
  have hT : (t : ℝ) * ((t - 1).factorial : ℝ) = (t.factorial : ℝ) := by
    exact_mod_cast Nat.mul_factorial_pred ht0
  have h1 : ((n - t).factorial : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
  have h2 : ((t - 1).factorial : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
  have h3 : (t : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr ht0
  have hz : zr y (t - 1) = (A (t - 1) (y - 1) : ℝ) / ((t - 1).factorial : ℝ) := rfl
  rw [Nat.cast_mul, Nat.cast_mul, Wf_cast hy.le, cc_eq_P (n - t), cc_eq_P (t - 1), hz, ← hC, ← hT]
  field_simp

/-- **The single-chain forward formula in natural numbers.** For `1 ≤ y` and `n ≤ 2y+1`,
`Uf y n = ∑_{t=y+1}^{n} C(n,t) · P(n-t) · Wf y t`. -/
private theorem Uf_fwd {y n : ℕ} (hy : 1 ≤ y) (hn : n ≤ 2 * y + 1) :
    Uf y n = ∑ t ∈ Icc (y + 1) n, n.choose t * P (n - t) * Wf y t := by
  have hfwd := (zr_isWSol hy).fwd y (fun t _ ht => by
      show ((min t y : ℕ) : ℝ) = (t : ℝ)
      rw [min_eq_left ht]) hn
  have hF : (n.factorial : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero n)
  have hz : zr y n = (A n (y - 1) : ℝ) / (n.factorial : ℝ) := rfl
  have hL : (Uf y n : ℝ) = (n.factorial : ℝ) * (cc n - zr y n) := by
    rw [Uf_cast, cc_eq_P n, hz]
    field_simp
  apply Nat.cast_injective (R := ℝ)
  rw [hL, hfwd, Finset.mul_sum, Nat.cast_sum]
  refine Finset.sum_congr rfl fun t ht => ?_
  rw [Finset.mem_Icc] at ht
  have hmin : ((min t y : ℕ) : ℝ) = (y : ℝ) := by
    rw [min_eq_right (by omega : y ≤ t)]
  have key := fwd_term (y := y) (n := n) (t := t) (by omega) ht.2
  rw [← hmin] at key
  exact key

/-! ### The function `conv` computes the sum of the forward formula -/

/-- `conv n [W (y+m), …, W (y+1)] i C(n,i) = ∑_{j<m} C(n,i+j) · P(i+j) · W (y+m-j)`. -/
private theorem conv_wl (W : ℕ → ℕ) (n y : ℕ) : ∀ (m i : ℕ),
    conv n (wl W y m) i (n.choose i)
      = ∑ j ∈ range m, n.choose (i + j) * P (i + j) * W (y + m - j) := by
  intro m
  induction m with
  | zero =>
    intro i
    have h0 : conv n (wl W y 0) i (n.choose i) = 0 := rfl
    rw [h0, Finset.sum_range_zero]
  | succ m ih =>
    intro i
    have hstep : n.choose i * (n - i) / (i + 1) = n.choose (i + 1) := by
      rw [← Nat.choose_succ_right_eq]
      exact Nat.mul_div_cancel _ (Nat.succ_pos i)
    have hw : wl W y (m + 1) = W (y + m + 1) :: wl W y m := rfl
    have hS : ∑ j ∈ range m, n.choose (i + 1 + j) * P (i + 1 + j) * W (y + m - j)
        = ∑ j ∈ range m,
            n.choose (i + (j + 1)) * P (i + (j + 1)) * W (y + (m + 1) - (j + 1)) := by
      refine Finset.sum_congr rfl fun j _ => ?_
      have e1 : i + 1 + j = i + (j + 1) := by omega
      have e2 : y + (m + 1) - (j + 1) = y + m - j := by omega
      rw [e1, e2]
    have e3 : y + (m + 1) = y + m + 1 := by omega
    rw [hw, conv_cons, hstep, ih (i + 1), hS, Finset.sum_range_succ', Nat.add_zero, Nat.sub_zero,
      e3]
    exact Nat.add_comm _ _

/-- On the rows of the single-chain range, `conv` applied to the list of the `Wf` returns `Uf`. -/
private theorem conv_Wf {y m : ℕ} (hy : 1 ≤ y) (hB : y + m ≤ 2 * y + 1) :
    conv (y + m) (wl (Wf y) y m) 0 1 = Uf y (y + m) := by
  have h := conv_wl (Wf y) (y + m) y m 0
  rw [Nat.choose_zero_right] at h
  rw [h, Uf_fwd hy hB]
  refine Finset.sum_nbij' (fun j => y + m - j) (fun t => y + m - t) ?_ ?_ ?_ ?_ ?_
  · intro j hj
    rw [Finset.mem_range] at hj
    rw [Finset.mem_Icc]
    omega
  · intro t ht
    rw [Finset.mem_Icc] at ht
    rw [Finset.mem_range]
    omega
  · intro j hj
    rw [Finset.mem_range] at hj
    show y + m - (y + m - j) = j
    omega
  · intro t ht
    rw [Finset.mem_Icc] at ht
    show y + m - (y + m - t) = t
    omega
  · intro j hj
    rw [Finset.mem_range] at hj
    have e1 : y + m - (y + m - j) = j := by omega
    have e2 : 0 + j = j := Nat.zero_add j
    show (y + m).choose (0 + j) * P (0 + j) * Wf y (y + m - j)
      = (y + m).choose (y + m - j) * P (y + m - (y + m - j)) * Wf y (y + m - j)
    rw [e2, e1, Nat.choose_symm (by omega : j ≤ y + m)]

/-! ### The computed columns -/

private theorem Wf_succ (y m : ℕ) :
    Wf y (y + m + 1) = (y + m + 1 - y) * P (y + m) + y * Uf y (y + m) := rfl

private theorem wl_one {y : ℕ} (hy : 1 ≤ y) : wl (Wf y) y 1 = [P y] := by
  have h1 : wl (Wf y) y 1 = [Wf y (y + 0 + 1)] := rfl
  have h2 : Wf y (y + 0 + 1) = (y + 0 + 1 - y) * P (y + 0) + y * Uf y (y + 0) := rfl
  have h3 : y + 0 + 1 - y = 1 := by omega
  rw [h1, h2, h3, Nat.add_zero, Uf_eq_zero hy (le_refl y), Nat.mul_zero, Nat.add_zero,
    Nat.one_mul]

/-- **The computed column.** For `1 ≤ y` and `cnt ≤ y + 1`,
`ucol y cnt = [Uf y (y+1), …, Uf y (y+cnt)]`. -/
private theorem ucol_spec {y cnt : ℕ} (hy : 1 ≤ y) (hcnt : cnt ≤ y + 1) :
    ucol y cnt = ul (Uf y) cnt (y + 1) := by
  have h := urows_eq_ul (Uf y) (Wf y) y (2 * y + 1)
    (fun m _ hB => conv_Wf hy hB) (fun m _ _ => Wf_succ y m) cnt 1 (le_refl 1) (by omega)
  rw [wl_one hy] at h
  exact h

private theorem nth_ucol {y cnt i : ℕ} (hy : 1 ≤ y) (hcnt : cnt ≤ y + 1) (hi : i < cnt) :
    nth (ucol y cnt) i = Uf y (y + 1 + i) := by
  rw [ucol_spec hy hcnt]
  exact nth_ul (Uf y) cnt (y + 1) i hi

/-! ### The checks as statements about `b` -/

/-- `d_{n,c} = b n c - b n (c-1) = 2·Uf c n - Uf (c+1) n - Uf (c-1) n` for `c ≥ 2`. -/
private theorem d_eq (c n : ℕ) (hc : 2 ≤ c) :
    (b n c : ℤ) - (b n (c - 1) : ℤ)
      = 2 * (Uf c n : ℤ) - (Uf (c + 1) n : ℤ) - (Uf (c - 1) n : ℤ) := by
  have h := d_eq_A hc n
  have u0 := Uf_add (c - 1) n
  have u1 := Uf_add c n
  have u2 := Uf_add (c + 1) n
  have e3 : c - 1 - 1 = c - 2 := by omega
  have e4 : c + 1 - 1 = c := by omega
  rw [e3] at u0
  rw [e4] at u2
  omega

/-- **What a passed check says.** If `chk2 k z = true`, then `z + 2 ≤ k`, column `k` is positive
in the row `k + z + 1`, and column `k + 1` is negative in the row `k + z`. -/
private theorem chk2_facts {k z : ℕ} (h : chk2 k z = true) :
    z + 2 ≤ k ∧ b (k + z + 1) (k - 1) < b (k + z + 1) k ∧ b (k + z) (k + 1) < b (k + z) k := by
  obtain ⟨hz, hzk, hF1, hF2⟩ := chk2_spec h
  refine ⟨hzk, ?_, ?_⟩
  · -- the row `q = k + z + 1` of column `k`
    have a1 : nth (ucol k (z + 1)) z = Uf k (k + z + 1) := by
      have j : k + 1 + z = k + z + 1 := by omega
      rw [nth_ucol (y := k) (cnt := z + 1) (i := z) (by omega) (by omega) (by omega), j]
    have a0 : nth (ucol (k - 1) (z + 2)) (z + 1) = Uf (k - 1) (k + z + 1) := by
      have j : k - 1 + 1 + (z + 1) = k + z + 1 := by omega
      rw [nth_ucol (y := k - 1) (cnt := z + 2) (i := z + 1) (by omega) (by omega) (by omega), j]
    have a2 : nth (ucol (k + 1) z) (z - 1) = Uf (k + 1) (k + z + 1) := by
      have j : k + 1 + 1 + (z - 1) = k + z + 1 := by omega
      rw [nth_ucol (y := k + 1) (cnt := z) (i := z - 1) (by omega) (by omega) (by omega), j]
    rw [a2, a0, a1] at hF1
    have hd := d_eq k (k + z + 1) (by omega)
    omega
  · -- the row `n = k + z` of column `k + 1`
    have a1 : nth (ucol k (z + 1)) (z - 1) = Uf k (k + z) := by
      have j : k + 1 + (z - 1) = k + z := by omega
      rw [nth_ucol (y := k) (cnt := z + 1) (i := z - 1) (by omega) (by omega) (by omega), j]
    have a2 : nth (ucol (k + 1) z) (z - 2) = Uf (k + 1) (k + z) := by
      have j : k + 1 + 1 + (z - 2) = k + z := by omega
      rw [nth_ucol (y := k + 1) (cnt := z) (i := z - 2) (by omega) (by omega) (by omega), j]
    have a3 : nth (0 :: ucol (k + 2) (z - 2)) (z - 2) = Uf (k + 2) (k + z) := by
      rcases Nat.eq_or_lt_of_le hz with e | hlt
      · have hU : Uf (k + 2) (k + z) = 0 :=
          Uf_eq_zero (y := k + 2) (n := k + z) (by omega) (by omega)
        have hi : z - 2 = 0 := by omega
        rw [hU, hi, nth_cons_zero]
      · obtain ⟨i', hi'⟩ : ∃ i', z - 2 = i' + 1 := ⟨z - 2 - 1, by omega⟩
        have j : k + 2 + 1 + i' = k + z := by omega
        rw [hi', nth_cons_succ,
          nth_ucol (y := k + 2) (cnt := i' + 1) (i := i') (by omega) (by omega) (by omega), j]
    rw [a2, a3, a1] at hF2
    have hd := d_eq (k + 1) (k + z) (by omega)
    have e1 : k + 1 + 1 = k + 2 := by omega
    have e2 : k + 1 - 1 = k := by omega
    rw [e1, e2] at hd
    omega

/-! ### The kernel evaluations

The columns `9 ≤ k ≤ 264` in sixteen blocks of sixteen columns; each block is one evaluation by
the kernel. -/

private theorem two_9 : allRange chk2T 9 16 = true := by decide +kernel

private theorem two_25 : allRange chk2T 25 16 = true := by decide +kernel

private theorem two_41 : allRange chk2T 41 16 = true := by decide +kernel

private theorem two_57 : allRange chk2T 57 16 = true := by decide +kernel

private theorem two_73 : allRange chk2T 73 16 = true := by decide +kernel

private theorem two_89 : allRange chk2T 89 16 = true := by decide +kernel

private theorem two_105 : allRange chk2T 105 16 = true := by decide +kernel

private theorem two_121 : allRange chk2T 121 16 = true := by decide +kernel

private theorem two_137 : allRange chk2T 137 16 = true := by decide +kernel

private theorem two_153 : allRange chk2T 153 16 = true := by decide +kernel

private theorem two_169 : allRange chk2T 169 16 = true := by decide +kernel

private theorem two_185 : allRange chk2T 185 16 = true := by decide +kernel

private theorem two_201 : allRange chk2T 201 16 = true := by decide +kernel

private theorem two_217 : allRange chk2T 217 16 = true := by decide +kernel

private theorem two_233 : allRange chk2T 233 16 = true := by decide +kernel

private theorem two_249 : allRange chk2T 249 16 = true := by decide +kernel

/-- **Every column `9 ≤ k ≤ 264` passes `chk2` with `z = ztab k`.** -/
private theorem chk2_ztab : ∀ k, 9 ≤ k → k < 265 → chk2 k (ztab k) = true :=
  glue (allRange_sound chk2T 9 16 two_9) <|
  glue (allRange_sound chk2T 25 16 two_25) <|
  glue (allRange_sound chk2T 41 16 two_41) <|
  glue (allRange_sound chk2T 57 16 two_57) <|
  glue (allRange_sound chk2T 73 16 two_73) <|
  glue (allRange_sound chk2T 89 16 two_89) <|
  glue (allRange_sound chk2T 105 16 two_105) <|
  glue (allRange_sound chk2T 121 16 two_121) <|
  glue (allRange_sound chk2T 137 16 two_137) <|
  glue (allRange_sound chk2T 153 16 two_153) <|
  glue (allRange_sound chk2T 169 16 two_169) <|
  glue (allRange_sound chk2T 185 16 two_185) <|
  glue (allRange_sound chk2T 201 16 two_201) <|
  glue (allRange_sound chk2T 217 16 two_217) <|
  glue (allRange_sound chk2T 233 16 two_233) <|
  allRange_sound chk2T 249 16 two_249

/-- `100 (ztab k + 1) ≤ 27 k` for `82 ≤ k ≤ 264`. -/
theorem ztab_27 : ∀ k, k < 265 → 82 ≤ k → 100 * (ztab k + 1) ≤ 27 * k := by decide +kernel

/-! ### The table statement -/

/-- **The two signs of the columns `9 ≤ k ≤ 264`.**  With `z = ztab k`: `z + 2 ≤ k`, the column
`k` is positive in the row `k + z + 1`, and the column `k + 1` is negative in the row `k + z`. -/
theorem two_signs {k : ℕ} (h9 : 9 ≤ k) (h264 : k ≤ 264) :
    ztab k + 2 ≤ k ∧ b (k + ztab k + 1) (k - 1) < b (k + ztab k + 1) k ∧
      b (k + ztab k) (k + 1) < b (k + ztab k) k :=
  chk2_facts (chk2_ztab k h9 (by omega))

end Tab
end Parking
