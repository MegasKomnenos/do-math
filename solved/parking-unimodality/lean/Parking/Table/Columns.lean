import Parking.Counting.Columns
import Parking.Table.Basic

/-!
# The table of the columns `2 ≤ k ≤ 81`

`b n ℓ` is the number of parking functions of length `n` with maximum displacement exactly `ℓ`,
`A n l` the number of those with all displacements at most `l`, and
`d_{n,k} = b n k - b n (k-1) = A n k - 2 A n (k-1) + A n (k-2)` is the step of column `k` in the
row `n`.  The numbers `A n l` are produced by the last-car recursion

  `A (n+1) l = ∑_{j ≤ n} min(j+1, l+1) C(n,j) A j l A (n-j) l`,

as lists `col l N = [A N l, …, A 0 l]`.

For a column `k`, a row `a` and a row `n0 ≥ 2k`, the Boolean `colOK k a n0` checks three finite
statements on the lists `col l (n0 - 1)` of the levels `l = k, k - 1, k - 2`:

* (s1) on the rows `k + 1 ≤ n ≤ 2k - 2`: `d_{n,k} ≤ 0` or `d_{n+1,k} > 0`;
* (s2) on the rows `a ≤ n ≤ n0 - 1`: `d_{n,k} ≥ 0`;
* (s3) with `P = k^(k-1)`, `Q = (k+1)^(k-1)` and the integers
  `δ_t = min(t,k+1) A (t-1) k - 2 min(t,k) A (t-1) (k-1) + min(t,k-1) A (t-1) (k-2)`,
  the Horner values `R_{n0} = δ_{n0}`, `R_s = δ_s c_s + P R_{s+1}`
  (`c_s = Q^(n0-s) n0!/s!`, so `c_{s-1} = c_s Q s`) are nonnegative for `k ≤ s ≤ n0`.
  The positive and the negative part of `R_s` are carried separately, so that everything stays
  in `Nat`.

`δ_t / t!` is the number `ξ_t` of `Parking.xi`, and `R_s ≥ 0` says that the sum
`∑_{s ≤ t ≤ n0} ξ_t x^t` is nonnegative at `x = P/Q`.

`n0 k` is the row listed for the column `k`, and `colRange k0 c` is the check of the columns
`k0 ≤ k < k0 + c` with the rows `n0 k`, where (s2) starts at the row `max (2k) 17`.

The functions on lists are written with recursors so that the kernel evaluates them directly;
they are only ever evaluated by the kernel (`decide +kernel`), in nineteen blocks of columns.
Their meaning is proved here:

* `col_eq`      : `col l N = [A N l, …, A 0 l]` (the last-car recursion `A_succ`);
* `chkC_sound`, `chk1_sound`, `horner_sound` : what the three checks (s1), (s2), (s3) say about
  three such lists; the Horner check gives the nonnegativity of all the sums
  `∑_{s ≤ t ≤ n0} ξ_t x^t` at a rational `x = P/Q`;
* `colOK_sound` : what the check of one column says;
* `small_table` : **the table statement.**  For `2 ≤ k ≤ 81` and `n0 = n0 k ≥ 2k`:
  in the chain range `k + 1 ≤ n ≤ 2k - 2`, `d_{n,k} > 0` implies `d_{n+1,k} > 0`;
  `d_{n,k} ≥ 0` on the rows `max (2k) 17 ≤ n < n0`; and `∑_{s ≤ t ≤ n0} ξ_t x_k^t ≥ 0` for
  `k ≤ s ≤ n0` at `x_k = (k/(k+1))^(k-1)`.
-/

namespace Parking
namespace Tab

open Finset

/-! ### The last-car lists -/

/-- `seqN a x = x`.  The kernel reduces the recursor only after it has evaluated `a`. -/
private noncomputable def seqN {β : Type} (a : Nat) (x : β) : β :=
  Nat.rec (motive := fun _ => β) x (fun _ _ => x) a

/-- `wmin a b = min a b`. -/
private def wmin (a b : Nat) : Nat := cond (Nat.ble a b) a b

/-- `revAcc xs acc = xs.reverse ++ acc`. -/
private noncomputable def revAcc (xs : List Nat) : List Nat → List Nat :=
  List.rec (motive := fun _ => List Nat → List Nat) (fun acc => acc)
    (fun x _ ih acc => ih (x :: acc)) xs

/-- `sumZ l n xs ys j c = ∑_i min(j+i+1, l+1) · C_i · xs[i] · ys[i]`, where `C_0 = c` and
`C_{i+1} = C_i (n-j-i)/(j+i+1)` (so `C_i = C(n,j+i)` when `c = C(n,j)`). -/
private noncomputable def sumZ (l n : Nat) (xs : List Nat) : List Nat → Nat → Nat → Nat :=
  List.rec (motive := fun _ => List Nat → Nat → Nat → Nat) (fun _ _ _ => 0)
    (fun x _ ih ys j c =>
      List.rec (motive := fun _ => Nat) 0
        (fun y ys' _ =>
          Nat.add (Nat.mul (wmin (Nat.succ j) (Nat.succ l)) (Nat.mul c (Nat.mul x y)))
            (ih ys' (Nat.succ j) (Nat.div (Nat.mul c (Nat.sub n j)) (Nat.succ j)))) ys) xs

/-- `A (n+1) l` from `xs = [A n l, …, A 0 l]`, by the last-car recursion. -/
private noncomputable def nextA (l n : Nat) (xs : List Nat) : Nat := sumZ l n (revAcc xs []) xs 0 1

/-- One more row: the new entry `a` is evaluated, then put on top of `xs`. -/
private noncomputable def growStep (ih : Nat → List Nat → List Nat) (n : Nat) (xs : List Nat)
    (a : Nat) :
    List Nat :=
  seqN a (ih (Nat.succ n) (a :: xs))

/-- `grow l m n xs`: `m` further rows on top of `xs = [A n l, …, A 0 l]`. -/
private noncomputable def grow (l : Nat) (m : Nat) : Nat → List Nat → List Nat :=
  Nat.rec (motive := fun _ => Nat → List Nat → List Nat) (fun _ xs => xs)
    (fun _ ih n xs => growStep ih n xs (nextA l n xs)) m

/-- `col l N = [A N l, A (N-1) l, …, A 0 l]`. -/
private noncomputable def col (l N : Nat) : List Nat := grow l N 0 [1]

/-- `hd l n = A n l`: the head of the list `col l n`. -/
noncomputable def hd (l n : Nat) : Nat := (col l n).headD 0

/-! ### The three checks of a column

The lists `la, lb, lc` are `[A M l, …, A 0 l]` for the levels `l = k, k - 1, k - 2`. -/

/-- (s1) on `m` pairs of consecutive entries: for the rows `n + 1` (head) and `n` (next entry),
`A n k + A n (k-2) ≤ 2 A n (k-1)` or `2 A (n+1) (k-1) < A (n+1) k + A (n+1) (k-2)`. -/
private noncomputable def chkC (m : Nat) : List Nat → List Nat → List Nat → Bool :=
  Nat.rec (motive := fun _ => List Nat → List Nat → List Nat → Bool) (fun _ _ _ => true)
    (fun _ ih la lb lc =>
      (Nat.ble (la.tail.headD 0 + lc.tail.headD 0) (2 * lb.tail.headD 0)
          || Nat.ble (2 * lb.headD 0 + 1) (la.headD 0 + lc.headD 0))
        && ih la.tail lb.tail lc.tail) m

/-- `chkC m` after the first `s` entries of the three lists. -/
private noncomputable def chkCFrom (s m : Nat) : List Nat → List Nat → List Nat → Bool :=
  Nat.rec (motive := fun _ => List Nat → List Nat → List Nat → Bool) (chkC m)
    (fun _ ih la lb lc => ih la.tail lb.tail lc.tail) s

/-- (s2) on the first `m` entries: `2 A n (k-1) ≤ A n k + A n (k-2)`. -/
private noncomputable def chk1 (m : Nat) : List Nat → List Nat → List Nat → Bool :=
  Nat.rec (motive := fun _ => List Nat → List Nat → List Nat → Bool) (fun _ _ _ => true)
    (fun _ ih la lb lc =>
      Nat.ble (2 * lb.headD 0) (la.headD 0 + lc.headD 0) && ih la.tail lb.tail lc.tail) m

/-- The test `rn ≤ rp` of one Horner step, and the passage to the next row. -/
private def hstep (Q : Nat)
    (ih : List Nat → List Nat → List Nat → Nat → Nat → Nat → Nat → Bool)
    (la lb lc : List Nat) (t c rp rn : Nat) : Bool :=
  Nat.ble rn rp && ih la.tail lb.tail lc.tail (t - 1) (c * Q * t) rp rn

/-- (s3): `m` Horner steps.  The heads of `la, lb, lc` are the rows `t - 1` of the levels
`k, k-1, k-2`; `c = c_t`; `rp`, `rn` are the positive and the negative part of `R_{t+1}`. -/
private noncomputable def horner (k P Q : Nat) (m : Nat) :
    List Nat → List Nat → List Nat → Nat → Nat → Nat → Nat → Bool :=
  Nat.rec (motive := fun _ => List Nat → List Nat → List Nat → Nat → Nat → Nat → Nat → Bool)
    (fun _ _ _ _ _ _ _ => true)
    (fun _ ih la lb lc t c rp rn =>
      hstep Q ih la lb lc t c
        ((wmin t (k + 1) * la.headD 0 + wmin t (k - 1) * lc.headD 0) * c + P * rp)
        (2 * wmin t k * lb.headD 0 * c + P * rn)) m

/-- The three checks of column `k` on the lists `la, lb, lc = [A (n0-1) l, …, A 0 l]`,
`l = k, k-1, k-2`. -/
private noncomputable def colChk (k a n0 : Nat) (la lb lc : List Nat) : Bool :=
  chkCFrom (n0 - 2 * k) (k - 2) la lb lc
    && (chk1 (n0 - a) la lb lc
      && horner k (k ^ (k - 1)) ((k + 1) ^ (k - 1)) (n0 - k + 1) la lb lc n0 1 0 0)

/-- Column `k` with the first row `a` of the check (s2) and the row `n0 ≥ 2k`. -/
private noncomputable def colOK (k a n0 : Nat) : Bool :=
  Nat.ble (2 * k) n0
    && colChk k a n0 (col k (n0 - 1)) (col (k - 1) (n0 - 1)) (col (k - 2) (n0 - 1))

/-! ### The rows `n0 k` and the blocks of columns -/

/-- The rows `n0 k` of the columns `k = 2, …, 81`. -/
def n0tab : List Nat :=
  [7, 10, 13, 15, 18, 20, 23, 25, 28, 30, 32, 35, 37, 39, 41, 44, 46, 48, 50, 52,
   55, 57, 59, 61, 63, 66, 68, 70, 72, 74, 76, 78, 80, 82, 85, 87, 89, 91, 93, 95,
   97, 99, 101, 103, 105, 107, 109, 111, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134,
   136, 138, 140, 142, 144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170, 171,
   173, 175]

/-- `n0 k`: the row up to which the column `k` (`2 ≤ k ≤ 81`) is computed. -/
def n0 (k : Nat) : Nat := nth n0tab (k - 2)

/-- `firstRow k = max (2k) 17`: the first row of the check (s2) of column `k`. -/
private def firstRow (k : Nat) : Nat := cond (Nat.ble 17 (2 * k)) (2 * k) 17

/-- The check of column `k` with the rows `firstRow k` and `n0 k`. -/
private noncomputable def colT (k : Nat) : Bool := colOK k (firstRow k) (n0 k)

/-- The columns `k0 ≤ k < k0 + c`. -/
private noncomputable def colRange (k0 c : Nat) : Bool := allRange colT k0 c

/-! ### Unfolding lemmas -/

private theorem seqN_eq {β : Type} (a : ℕ) (x : β) : seqN a x = x := by
  cases a <;> rfl

private theorem wmin_eq (a b : ℕ) : wmin a b = min a b := by
  by_cases h : a ≤ b
  · have hb : Nat.ble a b = true := Nat.ble_eq_true_of_le h
    have h1 : wmin a b = a := (congrArg (fun c => cond c a b) hb).trans rfl
    rw [h1, Nat.min_eq_left h]
  · have hb : Nat.ble a b = false := by
      cases hc : Nat.ble a b with
      | false => rfl
      | true => exact absurd (Nat.le_of_ble_eq_true hc) h
    have h1 : wmin a b = b := (congrArg (fun c => cond c a b) hb).trans rfl
    rw [h1, Nat.min_eq_right (by omega : b ≤ a)]

private theorem sumZ_cons (l n x : ℕ) (xs : List ℕ) (y : ℕ) (ys : List ℕ) (j c : ℕ) :
    sumZ l n (x :: xs) (y :: ys) j c
      = wmin (j + 1) (l + 1) * (c * (x * y))
        + sumZ l n xs ys (j + 1) (c * (n - j) / (j + 1)) := rfl

private theorem grow_succ (l m n : ℕ) (xs : List ℕ) :
    grow l (m + 1) n xs = grow l m (n + 1) (nextA l n xs :: xs) :=
  seqN_eq (nextA l n xs) (grow l m (n + 1) (nextA l n xs :: xs))

private theorem chkC_succ (m : ℕ) (la lb lc : List ℕ) :
    chkC (m + 1) la lb lc
      = ((Nat.ble (la.tail.headD 0 + lc.tail.headD 0) (2 * lb.tail.headD 0)
            || Nat.ble (2 * lb.headD 0 + 1) (la.headD 0 + lc.headD 0))
          && chkC m la.tail lb.tail lc.tail) := rfl

private theorem chkCFrom_succ (s m : ℕ) (la lb lc : List ℕ) :
    chkCFrom (s + 1) m la lb lc = chkCFrom s m la.tail lb.tail lc.tail := rfl

private theorem chk1_succ (m : ℕ) (la lb lc : List ℕ) :
    chk1 (m + 1) la lb lc
      = (Nat.ble (2 * lb.headD 0) (la.headD 0 + lc.headD 0)
          && chk1 m la.tail lb.tail lc.tail) := rfl

private theorem horner_succ (k P Q m : ℕ) (la lb lc : List ℕ) (t c rp rn : ℕ) :
    horner k P Q (m + 1) la lb lc t c rp rn
      = (Nat.ble (2 * wmin t k * lb.headD 0 * c + P * rn)
            ((wmin t (k + 1) * la.headD 0 + wmin t (k - 1) * lc.headD 0) * c + P * rp)
          && horner k P Q m la.tail lb.tail lc.tail (t - 1) (c * Q * t)
            ((wmin t (k + 1) * la.headD 0 + wmin t (k - 1) * lc.headD 0) * c + P * rp)
            (2 * wmin t k * lb.headD 0 * c + P * rn)) := rfl

/-! ### Lists of values of a function -/

/-- `dn f m = [f (m-1), …, f 0]`. -/
private def dn (f : ℕ → ℕ) : ℕ → List ℕ
  | 0 => []
  | m + 1 => f m :: dn f m

/-- `up f a m = [f a, …, f (a+m-1)]`. -/
private def up (f : ℕ → ℕ) : ℕ → ℕ → List ℕ
  | _, 0 => []
  | a, m + 1 => f a :: up f (a + 1) m

private theorem dn_headD (f : ℕ → ℕ) (m : ℕ) : (dn f (m + 1)).headD 0 = f m := rfl

private theorem dn_tail (f : ℕ → ℕ) (m : ℕ) : (dn f (m + 1)).tail = dn f m := rfl

private theorem up_snoc (f : ℕ → ℕ) : ∀ (m a : ℕ), up f a (m + 1) = up f a m ++ [f (a + m)] := by
  intro m
  induction m with
  | zero =>
    intro a
    rfl
  | succ m ih =>
    intro a
    have e : a + 1 + m = a + (m + 1) := by omega
    show f a :: up f (a + 1) (m + 1) = (f a :: up f (a + 1) m) ++ [f (a + (m + 1))]
    rw [ih (a + 1), e, List.cons_append]

private theorem revAcc_dn (f : ℕ → ℕ) : ∀ (m : ℕ) (acc : List ℕ),
    revAcc (dn f m) acc = up f 0 m ++ acc := by
  intro m
  induction m with
  | zero =>
    intro acc
    rfl
  | succ m ih =>
    intro acc
    show revAcc (dn f m) (f m :: acc) = up f 0 (m + 1) ++ acc
    rw [ih, up_snoc, Nat.zero_add, List.append_assoc, List.singleton_append]

/-! ### The last-car recursion -/

/-- The weighted convolution of an ascending and a descending list. -/
private theorem sumZ_up_dn (l n : ℕ) (f g : ℕ → ℕ) : ∀ (m a j : ℕ),
    sumZ l n (up f a m) (dn g m) j (n.choose j)
      = ∑ i ∈ range m,
          min (j + i + 1) (l + 1) * (n.choose (j + i) * (f (a + i) * g (m - 1 - i))) := by
  intro m
  induction m with
  | zero =>
    intro a j
    rw [Finset.sum_range_zero]
    rfl
  | succ m ih =>
    intro a j
    have hc : n.choose j * (n - j) / (j + 1) = n.choose (j + 1) :=
      Nat.div_eq_of_eq_mul_left (Nat.succ_pos j) (Nat.choose_succ_right_eq n j).symm
    have h1 : ∑ i ∈ range m,
          min (j + 1 + i + 1) (l + 1) * (n.choose (j + 1 + i) * (f (a + 1 + i) * g (m - 1 - i)))
        = ∑ i ∈ range m,
          min (j + (i + 1) + 1) (l + 1)
            * (n.choose (j + (i + 1)) * (f (a + (i + 1)) * g (m + 1 - 1 - (i + 1)))) := by
      refine Finset.sum_congr rfl (fun i _ => ?_)
      have e1 : j + 1 + i = j + (i + 1) := by omega
      have e2 : a + 1 + i = a + (i + 1) := by omega
      have e3 : m + 1 - 1 - (i + 1) = m - 1 - i := by omega
      rw [e1, e2, e3]
    show sumZ l n (f a :: up f (a + 1) m) (g m :: dn g m) j (n.choose j) = _
    rw [sumZ_cons, hc, ih (a + 1) (j + 1), Finset.sum_range_succ', h1, wmin_eq, Nat.add_zero,
      Nat.add_zero, Nat.sub_zero, Nat.add_sub_cancel]
    exact Nat.add_comm _ _

private theorem nextA_dn (l n : ℕ) (f : ℕ → ℕ) :
    nextA l n (dn f (n + 1))
      = ∑ j ∈ range (n + 1), min (j + 1) (l + 1) * (n.choose j * (f j * f (n - j))) := by
  have h := sumZ_up_dn l n f f (n + 1) 0 0
  rw [Nat.choose_zero_right] at h
  unfold nextA
  rw [revAcc_dn, List.append_nil, h]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  rw [Nat.zero_add, Nat.add_sub_cancel]

private theorem grow_dn (l : ℕ) (f : ℕ → ℕ)
    (hf : ∀ n, f (n + 1)
      = ∑ j ∈ range (n + 1), min (j + 1) (l + 1) * (n.choose j * (f j * f (n - j)))) :
    ∀ (m n : ℕ), grow l m n (dn f (n + 1)) = dn f (n + m + 1) := by
  intro m
  induction m with
  | zero =>
    intro n
    rfl
  | succ m ih =>
    intro n
    have e : n + (m + 1) + 1 = n + 1 + m + 1 := by omega
    rw [grow_succ, nextA_dn, ← hf n, e]
    exact ih (n + 1)

/-- **The table is the table of the numbers `A n l`.** -/
private theorem col_eq (l N : ℕ) : col l N = dn (fun i => A i l) (N + 1) := by
  have h := grow_dn l (fun i => A i l) (fun n => A_succ n l) N 0
  have e : 0 + N + 1 = N + 1 := by omega
  have h0 : dn (fun i => A i l) (0 + 1) = [1] := by
    show [A 0 l] = [1]
    rw [A_zero]
  rw [e, h0] at h
  exact h

/-- The head of the list `col l n` is `A n l`. -/
theorem hd_eq (l n : ℕ) : hd l n = A n l := by
  unfold hd
  rw [col_eq]
  exact dn_headD (fun i => A i l) n

/-! ### The checks (s1) and (s2) -/

/-- (s1) on the pairs of rows `(n + 1, n)` with `n + 2 ≤ M ≤ n + 1 + m`. -/
private theorem chkC_sound (fa fb fc : ℕ → ℕ) : ∀ (m M : ℕ),
    chkC m (dn fa M) (dn fb M) (dn fc M) = true →
    ∀ n, n + 2 ≤ M → M ≤ n + 1 + m →
      fa n + fc n ≤ 2 * fb n ∨ 2 * fb (n + 1) + 1 ≤ fa (n + 1) + fc (n + 1) := by
  intro m
  induction m with
  | zero =>
    intro M _ n h1 h2
    omega
  | succ m ih =>
    intro M h n h1 h2
    obtain ⟨M', rfl⟩ : ∃ M', M = M' + 1 + 1 := ⟨M - 2, by omega⟩
    rw [chkC_succ] at h
    simp only [dn_headD, dn_tail, Bool.and_eq_true, Bool.or_eq_true, Nat.ble_eq] at h
    rcases Nat.eq_or_lt_of_le (show n ≤ M' by omega) with rfl | hlt
    · exact h.1
    · exact ih (M' + 1) h.2 n (by omega) (by omega)

/-- After its first `s` entries, the list of the rows below `M` is the list of the rows below
`M - s`. -/
private theorem chkCFrom_sound (fa fb fc : ℕ → ℕ) (m : ℕ) : ∀ (s M : ℕ), s ≤ M →
    chkCFrom s m (dn fa M) (dn fb M) (dn fc M) = true →
    chkC m (dn fa (M - s)) (dn fb (M - s)) (dn fc (M - s)) = true := by
  intro s
  induction s with
  | zero =>
    intro M _ h
    exact h
  | succ s ih =>
    intro M hs h
    obtain ⟨M', rfl⟩ : ∃ M', M = M' + 1 := ⟨M - 1, by omega⟩
    rw [chkCFrom_succ] at h
    simp only [dn_tail] at h
    have e : M' + 1 - (s + 1) = M' - s := by omega
    rw [e]
    exact ih M' (by omega) h

/-- (s2) on the rows `n < M ≤ n + m`. -/
private theorem chk1_sound (fa fb fc : ℕ → ℕ) : ∀ (m M : ℕ),
    chk1 m (dn fa M) (dn fb M) (dn fc M) = true →
    ∀ n, n < M → M ≤ n + m → 2 * fb n ≤ fa n + fc n := by
  intro m
  induction m with
  | zero =>
    intro M _ n h1 h2
    omega
  | succ m ih =>
    intro M h n h1 h2
    obtain ⟨M', rfl⟩ : ∃ M', M = M' + 1 := ⟨M - 1, by omega⟩
    rw [chk1_succ] at h
    simp only [dn_headD, dn_tail, Bool.and_eq_true, Nat.ble_eq] at h
    rcases Nat.eq_or_lt_of_le (show n ≤ M' by omega) with rfl | hlt
    · exact h.1
    · exact ih M' h.2 n hlt (by omega)

/-! ### The Horner check (s3) -/

private theorem zr_fact (y n : ℕ) : zr y n * (n.factorial : ℝ) = (A n (y - 1) : ℝ) := by
  have h : (n.factorial : ℝ) ≠ 0 := by positivity
  unfold zr
  field

/-- `(u+1)! ξ_{u+1}` is the integer tree curvature `δ_{u+1}`. -/
private theorem xi_fact (k u : ℕ) :
    xi k (u + 1) * ((u + 1).factorial : ℝ)
      = ((min (u + 1) (k + 1) : ℕ) : ℝ) * (A u k : ℝ)
        - 2 * ((min (u + 1) k : ℕ) : ℝ) * (A u (k - 1) : ℝ)
        + ((min (u + 1) (k - 1) : ℕ) : ℝ) * (A u (k - 2) : ℝ) := by
  have hf : ((u + 1).factorial : ℝ) = ((u : ℝ) + 1) * (u.factorial : ℝ) := by
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  have hu1 : ((u : ℝ) + 1) ≠ 0 := by positivity
  have h1 := zr_fact (k + 1) u
  have h2 := zr_fact k u
  have h3 := zr_fact (k - 1) u
  rw [Nat.add_sub_cancel] at h1
  rw [show k - 1 - 1 = k - 2 by omega] at h3
  rw [xi_succ, hf, ← h1, ← h2, ← h3]
  field

/-- The Horner recursion.  On entry the heads of the three lists are the rows `t - 1`,
`c t! = Q^(n0-t) n0!` and `(rp - rn) P^(t+1) = σ n0! Q^n0`, where `σ` is the suffix sum from
`t + 1` on; each of the `m` steps tests the sign of the next suffix sum. -/
private theorem horner_sound (k n0 P Q : ℕ) (hQ : 0 < Q) (x : ℝ) (hx : x = (P : ℝ) / (Q : ℝ)) :
    ∀ (m t c rp rn : ℕ) (σ : ℝ), m ≤ t → t ≤ n0 →
      (c : ℝ) * (t.factorial : ℝ) = (Q : ℝ) ^ (n0 - t) * (n0.factorial : ℝ) →
      ((rp : ℝ) - (rn : ℝ)) * (P : ℝ) ^ (t + 1) = σ * ((n0.factorial : ℝ) * (Q : ℝ) ^ n0) →
      horner k P Q m (dn (fun i => A i k) t) (dn (fun i => A i (k - 1)) t)
        (dn (fun i => A i (k - 2)) t) t c rp rn = true →
      ∀ s, t < s + m → s ≤ t → 0 ≤ σ + ∑ v ∈ Icc s t, xi k v * x ^ v := by
  have hQR : (0 : ℝ) < (Q : ℝ) := Nat.cast_pos.mpr hQ
  have hQ0 : (Q : ℝ) ≠ 0 := hQR.ne'
  have hxQ : x * (Q : ℝ) = (P : ℝ) := by
    rw [hx]
    field
  have hN : (0 : ℝ) < (n0.factorial : ℝ) * (Q : ℝ) ^ n0 :=
    mul_pos (Nat.cast_pos.mpr (Nat.factorial_pos n0)) (pow_pos hQR n0)
  intro m
  induction m with
  | zero =>
    intro t c rp rn σ _ _ _ _ _ s hs1 hs2
    omega
  | succ m ih =>
    intro t c rp rn σ hmt htn hc hR h s hs1 hs2
    obtain ⟨u, rfl⟩ : ∃ u, t = u + 1 := ⟨t - 1, by omega⟩
    rw [horner_succ, Bool.and_eq_true_iff, Nat.add_sub_cancel] at h
    obtain ⟨h1, h2⟩ := h
    simp only [dn_headD, dn_tail, wmin_eq] at h1 h2
    have h1' : 2 * min (u + 1) k * A u (k - 1) * c + P * rn
        ≤ (min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c + P * rp :=
      Nat.le_of_ble_eq_true h1
    have h2' : horner k P Q m (dn (fun i => A i k) u) (dn (fun i => A i (k - 1)) u)
        (dn (fun i => A i (k - 2)) u) u (c * Q * (u + 1))
        ((min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c + P * rp)
        (2 * min (u + 1) k * A u (k - 1) * c + P * rn) = true := h2
    -- powers and factorials
    have hf : ((u + 1).factorial : ℝ) = ((u : ℝ) + 1) * (u.factorial : ℝ) := by
      rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
    have hpow : (Q : ℝ) ^ (n0 - u) = (Q : ℝ) ^ (n0 - (u + 1)) * (Q : ℝ) := by
      have e : n0 - u = n0 - (u + 1) + 1 := by omega
      rw [e, pow_succ]
    have hQn : (Q : ℝ) ^ n0 = (Q : ℝ) ^ (n0 - (u + 1)) * (Q : ℝ) ^ (u + 1) := by
      rw [← pow_add, Nat.sub_add_cancel htn]
    have hX : x ^ (u + 1) * (Q : ℝ) ^ (u + 1) = (P : ℝ) ^ (u + 1) := by
      rw [← mul_pow, hxQ]
    have hxi := xi_fact k u
    -- the casts of the new accumulators
    have hrpR : (((min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c
          + P * rp : ℕ) : ℝ)
        = (((min (u + 1) (k + 1) : ℕ) : ℝ) * (A u k : ℝ)
            + ((min (u + 1) (k - 1) : ℕ) : ℝ) * (A u (k - 2) : ℝ)) * (c : ℝ)
          + (P : ℝ) * (rp : ℝ) := by
      simp only [Nat.cast_add, Nat.cast_mul]
    have hrnR : ((2 * min (u + 1) k * A u (k - 1) * c + P * rn : ℕ) : ℝ)
        = 2 * ((min (u + 1) k : ℕ) : ℝ) * (A u (k - 1) : ℝ) * (c : ℝ) + (P : ℝ) * (rn : ℝ) := by
      simp only [Nat.cast_add, Nat.cast_mul, Nat.cast_ofNat]
    have hcR : ((c * Q * (u + 1) : ℕ) : ℝ) = (c : ℝ) * (Q : ℝ) * ((u : ℝ) + 1) := by
      simp only [Nat.cast_add, Nat.cast_mul, Nat.cast_one]
    -- the invariants after the step
    have hc' : ((c * Q * (u + 1) : ℕ) : ℝ) * (u.factorial : ℝ)
        = (Q : ℝ) ^ (n0 - u) * (n0.factorial : ℝ) := by
      have hc2 := hc
      rw [hf] at hc2
      rw [hcR, hpow]
      linear_combination (Q : ℝ) * hc2
    have hR' : ((((min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c
            + P * rp : ℕ) : ℝ)
          - ((2 * min (u + 1) k * A u (k - 1) * c + P * rn : ℕ) : ℝ)) * (P : ℝ) ^ (u + 1)
        = (σ + xi k (u + 1) * x ^ (u + 1)) * ((n0.factorial : ℝ) * (Q : ℝ) ^ n0) := by
      have hR2 := hR
      rw [pow_succ, hQn] at hR2
      rw [hrpR, hrnR, hQn]
      linear_combination hR2 - (c : ℝ) * (P : ℝ) ^ (u + 1) * hxi
        + xi k (u + 1) * (P : ℝ) ^ (u + 1) * hc
        - xi k (u + 1) * (Q : ℝ) ^ (n0 - (u + 1)) * (n0.factorial : ℝ) * hX
    have hIH := ih u (c * Q * (u + 1))
      ((min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c + P * rp)
      (2 * min (u + 1) k * A u (k - 1) * c + P * rn)
      (σ + xi k (u + 1) * x ^ (u + 1)) (by omega) (by omega) hc' hR' h2'
    rcases Nat.eq_or_lt_of_le hs2 with heq | hlt
    · have hle : ((2 * min (u + 1) k * A u (k - 1) * c + P * rn : ℕ) : ℝ)
          ≤ (((min (u + 1) (k + 1) * A u k + min (u + 1) (k - 1) * A u (k - 2)) * c
            + P * rp : ℕ) : ℝ) := Nat.cast_le.mpr h1'
      have h0 : 0 * ((n0.factorial : ℝ) * (Q : ℝ) ^ n0)
          ≤ (σ + xi k (u + 1) * x ^ (u + 1)) * ((n0.factorial : ℝ) * (Q : ℝ) ^ n0) := by
        rw [zero_mul, ← hR']
        exact mul_nonneg (sub_nonneg.mpr hle) (pow_nonneg (Nat.cast_nonneg P) _)
      rw [heq, Finset.Icc_self, Finset.sum_singleton]
      exact le_of_mul_le_mul_right h0 hN
    · have h3 := hIH s (by omega) (by omega)
      rw [Finset.sum_Icc_succ_top (by omega : s ≤ u + 1)]
      linarith

/-! ### One column -/

/-- **One column.**  If `colOK k a n0 = true`, then `2k ≤ n0`; in the chain range
`k + 1 ≤ n ≤ 2k - 2` a positive step `d_{n,k} > 0` is followed by a positive step
`d_{n+1,k} > 0`; `d_{n,k} ≥ 0` on the rows `a ≤ n < n0`; and all the sums
`∑_{s ≤ t ≤ n0} ξ_t x^t`, `k ≤ s ≤ n0`, are nonnegative at `x = (k/(k+1))^(k-1)`. -/
private theorem colOK_sound {k a n0 : ℕ} (hk : 2 ≤ k) (h : colOK k a n0 = true) :
    2 * k ≤ n0 ∧
    (∀ n, k + 1 ≤ n → n ≤ 2 * k - 2 →
      b n (k - 1) < b n k → b (n + 1) (k - 1) < b (n + 1) k) ∧
    (∀ n, a ≤ n → n < n0 → b n (k - 1) ≤ b n k) ∧
    (∀ s, k ≤ s → s ≤ n0 →
      0 ≤ ∑ t ∈ Icc s n0, xi k t * (((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)) ^ t) := by
  unfold colOK colChk at h
  rw [Bool.and_eq_true_iff, Bool.and_eq_true_iff, Bool.and_eq_true_iff] at h
  obtain ⟨h0, h1, h2, h3⟩ := h
  have hn0 : 2 * k ≤ n0 := Nat.le_of_ble_eq_true h0
  have e : n0 - 1 + 1 = n0 := by omega
  rw [col_eq, col_eq, col_eq, e] at h1 h2 h3
  refine ⟨hn0, ?_, ?_, ?_⟩
  · intro n hn1 hn2 hlt
    have h4 : A n k + A n (k - 2) ≤ 2 * A n (k - 1)
        ∨ 2 * A (n + 1) (k - 1) + 1 ≤ A (n + 1) k + A (n + 1) (k - 2) :=
      chkC_sound _ _ _ (k - 2) (n0 - (n0 - 2 * k))
        (chkCFrom_sound _ _ _ (k - 2) (n0 - 2 * k) n0 (Nat.sub_le _ _) h1) n
        (by omega) (by omega)
    have d1 := d_eq_A hk n
    have d2 := d_eq_A hk (n + 1)
    omega
  · intro n hn1 hn2
    have h4 : 2 * A n (k - 1) ≤ A n k + A n (k - 2) :=
      chk1_sound _ _ _ (n0 - a) n0 h2 n hn2 (by omega)
    have d1 := d_eq_A hk n
    omega
  · intro s hs1 hs2
    have hQ : 0 < (k + 1) ^ (k - 1) := by positivity
    have hx : ((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)
        = ((k ^ (k - 1) : ℕ) : ℝ) / (((k + 1) ^ (k - 1) : ℕ) : ℝ) := by
      rw [div_pow, Nat.cast_pow, Nat.cast_pow, Nat.cast_add, Nat.cast_one]
    have h4 := horner_sound k n0 (k ^ (k - 1)) ((k + 1) ^ (k - 1)) hQ _ hx
      (n0 - k + 1) n0 1 0 0 0 (by omega) (le_refl n0)
      (by rw [Nat.cast_one, one_mul, Nat.sub_self, pow_zero, one_mul])
      (by rw [Nat.cast_zero, sub_zero, zero_mul, zero_mul])
      h3 s (by omega) hs2
    rw [zero_add] at h4
    exact h4

/-! ### The kernel evaluations

The columns `2 ≤ k ≤ 81` in nineteen blocks; each block is one evaluation by the kernel. -/

private theorem cols_2_8 : colRange 2 7 = true := by decide +kernel

private theorem cols_9_25 : colRange 9 17 = true := by decide +kernel

private theorem cols_26_35 : colRange 26 10 = true := by decide +kernel

private theorem cols_36_42 : colRange 36 7 = true := by decide +kernel

private theorem cols_43_47 : colRange 43 5 = true := by decide +kernel

private theorem cols_48_51 : colRange 48 4 = true := by decide +kernel

private theorem cols_52_55 : colRange 52 4 = true := by decide +kernel

private theorem cols_56_58 : colRange 56 3 = true := by decide +kernel

private theorem cols_59_61 : colRange 59 3 = true := by decide +kernel

private theorem cols_62_64 : colRange 62 3 = true := by decide +kernel

private theorem cols_65_66 : colRange 65 2 = true := by decide +kernel

private theorem cols_67_68 : colRange 67 2 = true := by decide +kernel

private theorem cols_69_70 : colRange 69 2 = true := by decide +kernel

private theorem cols_71_72 : colRange 71 2 = true := by decide +kernel

private theorem cols_73_74 : colRange 73 2 = true := by decide +kernel

private theorem cols_75_76 : colRange 75 2 = true := by decide +kernel

private theorem cols_77_78 : colRange 77 2 = true := by decide +kernel

private theorem cols_79_80 : colRange 79 2 = true := by decide +kernel

private theorem cols_81_81 : colRange 81 1 = true := by decide +kernel

/-! ### The columns `2 ≤ k ≤ 81` -/

/-- Every column `2 ≤ k ≤ 81` passes the check with the rows `firstRow k` and `n0 k`
(the nineteen kernel-evaluated blocks). -/
private theorem small_cols : ∀ k, 2 ≤ k → k < 82 → colT k = true :=
  glue (allRange_sound colT 2 7 cols_2_8) <|
  glue (allRange_sound colT 9 17 cols_9_25) <|
  glue (allRange_sound colT 26 10 cols_26_35) <|
  glue (allRange_sound colT 36 7 cols_36_42) <|
  glue (allRange_sound colT 43 5 cols_43_47) <|
  glue (allRange_sound colT 48 4 cols_48_51) <|
  glue (allRange_sound colT 52 4 cols_52_55) <|
  glue (allRange_sound colT 56 3 cols_56_58) <|
  glue (allRange_sound colT 59 3 cols_59_61) <|
  glue (allRange_sound colT 62 3 cols_62_64) <|
  glue (allRange_sound colT 65 2 cols_65_66) <|
  glue (allRange_sound colT 67 2 cols_67_68) <|
  glue (allRange_sound colT 69 2 cols_69_70) <|
  glue (allRange_sound colT 71 2 cols_71_72) <|
  glue (allRange_sound colT 73 2 cols_73_74) <|
  glue (allRange_sound colT 75 2 cols_75_76) <|
  glue (allRange_sound colT 77 2 cols_77_78) <|
  glue (allRange_sound colT 79 2 cols_79_80) <|
  allRange_sound colT 81 1 cols_81_81

private theorem firstRow_le {k n : ℕ} (h1 : 2 * k ≤ n) (h2 : 17 ≤ n) : firstRow k ≤ n := by
  unfold firstRow
  cases Nat.ble 17 (2 * k)
  · exact h2
  · exact h1

/-- **The table of the columns `2 ≤ k ≤ 81`.**  With `n0 = n0 k`: `2k ≤ n0`; in the chain range
`k + 1 ≤ n ≤ 2k - 2`, `d_{n,k} > 0` implies `d_{n+1,k} > 0`; `d_{n,k} ≥ 0` on the rows
`max (2k) 17 ≤ n < n0`; and all the sums `∑_{s ≤ t ≤ n0} ξ_t x^t`, `k ≤ s ≤ n0`, are nonnegative
at `x = (k/(k+1))^(k-1)`. -/
theorem small_table {k : ℕ} (hk2 : 2 ≤ k) (hk81 : k ≤ 81) :
    2 * k ≤ n0 k ∧
    (∀ n, k + 1 ≤ n → n ≤ 2 * k - 2 →
      b n (k - 1) < b n k → b (n + 1) (k - 1) < b (n + 1) k) ∧
    (∀ n, 2 * k ≤ n → 17 ≤ n → n < n0 k → b n (k - 1) ≤ b n k) ∧
    (∀ s, k ≤ s → s ≤ n0 k →
      0 ≤ ∑ t ∈ Icc s (n0 k), xi k t * (((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)) ^ t) := by
  obtain ⟨h1, h2, h3, h4⟩ := colOK_sound hk2 (small_cols k hk2 (by omega))
  exact ⟨h1, h2, fun n hn1 hn2 => h3 n (firstRow_le hn1 hn2), h4⟩

end Tab
end Parking
