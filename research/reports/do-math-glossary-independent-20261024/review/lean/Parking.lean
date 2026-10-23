import Mathlib.Data.Finset.Max
import Mathlib.Data.Fintype.Pi
import Mathlib.Data.List.OfFn
import Mathlib.Data.List.Forall2
import Mathlib.Data.Int.Basic
import Mathlib.Data.PNat.Basic
import Mathlib.Tactic.SplitIfs

/- Ordered preferences, cars, and slots use 0-based `Fin n` internally.
   Original car/slot number = internal value + 1. -/
namespace Parking

abbrev Pref (n : ℕ) := Fin n → Fin n

def candidates {n : ℕ} (a : Fin n) (occupied : Finset (Fin n)) : Finset (Fin n) :=
  Finset.univ.filter fun s => a ≤ s ∧ s ∉ occupied

def next {n : ℕ} (a : Fin n) (occupied : Finset (Fin n)) : Option (Fin n) :=
  if h : (candidates a occupied).Nonempty then
    some ((candidates a occupied).min' h)
  else none

theorem next_spec {n : ℕ} (a s : Fin n) (occupied : Finset (Fin n)) :
    next a occupied = some s ↔
      a ≤ s ∧ s ∉ occupied ∧ ∀ t, a ≤ t → t ∉ occupied → s ≤ t := by
  unfold next
  split_ifs with h
  · constructor
    · intro he
      have hs : (candidates a occupied).min' h = s := Option.some.inj he
      have hm := Finset.min'_mem (candidates a occupied) h
      rw [hs] at hm
      have hm' := (Finset.mem_filter.mp hm).2
      refine ⟨hm'.1, hm'.2, ?_⟩
      intro t hat hot
      rw [← hs]
      exact Finset.min'_le _ _ (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hat, hot⟩)
    · rintro ⟨has, hso, hmin⟩
      congr 1
      apply le_antisymm
      · exact Finset.min'_le _ _ (Finset.mem_filter.mpr ⟨Finset.mem_univ _, has, hso⟩)
      · have hm := (Finset.mem_filter.mp (Finset.min'_mem (candidates a occupied) h)).2
        exact hmin _ hm.1 hm.2
  · simp only [false_iff]
    rintro ⟨has, hso, _⟩
    exact h ⟨s, Finset.mem_filter.mpr ⟨Finset.mem_univ _, has, hso⟩⟩

theorem next_failure {n : ℕ} (a : Fin n) (occupied : Finset (Fin n)) :
    next a occupied = none ↔ ∀ s, a ≤ s → s ∈ occupied := by
  unfold next
  split_ifs with h
  · simp only [false_iff]
    intro hall
    obtain ⟨s, hs⟩ := h
    have hm := (Finset.mem_filter.mp hs).2
    exact hm.2 (hall s hm.1)
  · simp only [true_iff]
    intro s has
    by_contra hso
    exact h ⟨s, Finset.mem_filter.mpr ⟨Finset.mem_univ _, has, hso⟩⟩

def run {n : ℕ} : List (Fin n) → Finset (Fin n) → Option (List (Fin n))
  | [], _ => some []
  | a :: rest, occupied => do
      let s ← next a occupied
      let tail ← run rest (insert s occupied)
      pure (s :: tail)

def park {n : ℕ} (a : Pref n) : Option (List (Fin n)) :=
  run (List.ofFn a) ∅

theorem run_fresh {n : ℕ} (as_ ss : List (Fin n)) (o : Finset (Fin n))
    (h : run as_ o = some ss) : ss.Nodup ∧ ∀ s ∈ ss, s ∉ o := by
  induction as_ generalizing o ss with
  | nil =>
    have hs : ss = [] := by simpa [run] using h.symm
    subst ss
    simp
  | cons a rest ih =>
    simp only [run] at h
    cases he : next a o with
    | none => simp [he] at h
    | some s =>
      cases ht : run rest (insert s o) with
      | none => simp [he, ht] at h
      | some tail =>
        have hs : s :: tail = ss := by simpa [he, ht] using h
        subst ss
        have hi := ih _ _ ht
        constructor
        · apply List.nodup_cons.mpr
          refine ⟨?_, hi.1⟩
          intro hm
          exact hi.2 s hm (Finset.mem_insert_self s o)
        · intro t hm
          rcases List.mem_cons.mp hm with heq | htail
          · subst t
            exact ((next_spec a s o).mp he).2.1
          · intro hto
            exact hi.2 t htail (Finset.mem_insert_of_mem hto)

theorem run_valid {n : ℕ} (as_ ss : List (Fin n)) (o : Finset (Fin n))
    (h : run as_ o = some ss) : List.Forall₂ (· ≤ ·) as_ ss := by
  induction as_ generalizing o ss with
  | nil =>
    have hs : ss = [] := by simpa [run] using h.symm
    subst ss
    exact List.Forall₂.nil
  | cons a rest ih =>
    simp only [run] at h
    cases he : next a o with
    | none => simp [he] at h
    | some s =>
      cases ht : run rest (insert s o) with
      | none => simp [he, ht] at h
      | some tail =>
        have hs : s :: tail = ss := by simpa [he, ht] using h
        subst ss
        exact List.Forall₂.cons ((next_spec a s o).mp he).1 (ih _ _ ht)

def Success {n : ℕ} (a : Pref n) : Prop := (park a).isSome
instance {n : ℕ} (a : Pref n) : Decidable (Success a) := inferInstanceAs (Decidable ((park a).isSome = true))
abbrev PF (n : ℕ) := {a : Pref n // Success a}

def slots {n : ℕ} (a : PF n) : List (Fin n) := (park a.val).get a.property

theorem park_slots {n : ℕ} (a : PF n) : park a.val = some (slots a) := by
  exact (Option.some_get a.property).symm

theorem slots_valid {n : ℕ} (a : PF n) :
    List.Forall₂ (· ≤ ·) (List.ofFn a.val) (slots a) :=
  run_valid _ _ _ (park_slots a)

theorem slots_length {n : ℕ} (a : PF n) : (slots a).length = n := by
  have h := (slots_valid a).length_eq
  simpa using h.symm

theorem slots_nodup {n : ℕ} (a : PF n) : (slots a).Nodup :=
  (run_fresh _ _ _ (park_slots a)).1

def slot {n : ℕ} (a : PF n) (i : Fin n) : Fin n :=
  (slots a).get ⟨i.val, by rw [slots_length]; exact i.isLt⟩

theorem pref_le_slot {n : ℕ} (a : PF n) (i : Fin n) : a.val i ≤ slot a i := by
  have h := (slots_valid a).get (i := i.val)
    (by simp) (by rw [slots_length]; exact i.isLt)
  simpa [slot] using h

def displacement {n : ℕ} (a : PF n) (i : Fin n) : ℕ := (slot a i).val - (a.val i).val

def M {n : ℕ} (a : PF n) : ℕ := Finset.univ.sup (displacement a)

def A (n l : ℕ) : ℕ := (Finset.univ.filter fun a : PF n => M a ≤ l).card
def b (n : ℕ+) (l : ℕ) : ℕ := (Finset.univ.filter fun a : PF n => M a = l).card

def Aint (n : ℕ) (l : ℤ) : ℕ := if l < 0 then 0 else A n l.toNat

def Unimodal (m : ℕ) (x : ℕ → ℕ) : Prop :=
  ∃ c : ℕ, c ≤ m ∧ (∀ k : ℕ, k < c → x k ≤ x (k+1)) ∧
    (∀ k : ℕ, c ≤ k → k < m → x (k+1) ≤ x k)

def UnimodalAt (n : ℕ+) (c : ℕ) : Prop :=
  c < (n : ℕ) ∧ (∀ k : ℕ, k < c → b n k ≤ b n (k+1)) ∧
    (∀ k : ℕ, c ≤ k → k < (n : ℕ)-1 → b n (k+1) ≤ b n k)

def P : Prop := ∀ (n : ℕ) (hn : 1 ≤ n), ∃ c : ℕ, UnimodalAt ⟨n, hn⟩ c

theorem unimodal_iff (n : ℕ+) :
    Unimodal ((n : ℕ)-1) (b n) ↔ ∃ c : ℕ, UnimodalAt n c := by
  have hn := n.pos
  constructor
  · rintro ⟨c, hc, hu, hd⟩
    exact ⟨c, by omega, hu, hd⟩
  · rintro ⟨c, hc, hu, hd⟩
    exact ⟨c, by omega, hu, hd⟩

theorem P_iff_unimodal : P ↔ ∀ n : ℕ+, Unimodal ((n : ℕ)-1) (b n) := by
  constructor
  · intro h n
    exact (unimodal_iff n).mpr (h n n.pos)
  · intro h n hn
    exact (unimodal_iff ⟨n, hn⟩).mp (h ⟨n, hn⟩)

theorem original_slot_range {n : ℕ} (a : PF n) (i : Fin n) :
    1 ≤ (slot a i).val + 1 ∧ (slot a i).val + 1 ≤ n := by
  have h := (slot a i).isLt
  omega

theorem displacement_balance {n : ℕ} (a : PF n) (i : Fin n) :
    (a.val i).val + displacement a i = (slot a i).val := by
  exact Nat.add_sub_of_le (pref_le_slot a i)

theorem displacement_original {n : ℕ} (a : PF n) (i : Fin n) :
    (displacement a i : ℤ) =
      ((slot a i).val + 1 : ℤ) - ((a.val i).val + 1 : ℤ) := by
  have h := displacement_balance a i
  omega

theorem displacement_le {n : ℕ} (a : PF n) (i : Fin n) :
    displacement a i ≤ n - 1 := by
  have h := (slot a i).isLt
  unfold displacement
  omega

theorem displacement_range {n : ℕ} (a : PF n) (i : Fin n) :
    0 ≤ displacement a i ∧ displacement a i ≤ n-1 :=
  ⟨Nat.zero_le _, displacement_le a i⟩

theorem displacement_le_M {n : ℕ} (a : PF n) (i : Fin n) :
    displacement a i ≤ M a := Finset.le_sup (Finset.mem_univ i)

theorem M_le {n : ℕ} (a : PF n) : M a ≤ n-1 :=
  Finset.sup_le fun i _ => displacement_le a i

theorem M_attained {n : ℕ} (hn : 1 ≤ n) (a : PF n) :
    ∃ i : Fin n, M a = displacement a i := by
  have hne : (Finset.univ : Finset (Fin n)).Nonempty :=
    ⟨⟨0, by omega⟩, Finset.mem_univ _⟩
  obtain ⟨i, _, hi⟩ := Finset.exists_mem_eq_sup Finset.univ hne (displacement a)
  exact ⟨i, hi⟩

theorem A_saturation (n l : ℕ) (hl : n-1 ≤ l) : A n l = Fintype.card (PF n) := by
  unfold A
  rw [← Finset.card_univ]
  rw [Finset.card_filter_eq_iff]
  intro a _
  exact (M_le a).trans hl

theorem b_vanish (n : ℕ+) (l : ℕ) (hl : (n : ℕ) ≤ l) : b n l = 0 := by
  unfold b
  rw [Finset.card_filter_eq_zero_iff]
  intro a _ he
  have hm := M_le a
  have hn := n.pos
  omega

theorem A_monotone (n : ℕ) : Monotone (A n) := by
  intro l r hlr
  apply Finset.card_le_card
  intro a ha
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ha ⊢
  exact ha.trans hlr

theorem b_zero (n : ℕ+) : b n 0 = A n 0 := by
  unfold b A
  congr 1
  ext a
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  omega

theorem b_difference (n : ℕ+) (l : ℕ) (hl : 1 ≤ l) : b n l = A n l - A n (l-1) := by
  have hsub :
      (Finset.univ.filter fun a : PF n => M a ≤ l-1) ⊆
        (Finset.univ.filter fun a : PF n => M a ≤ l) := by
    intro a ha
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ha ⊢
    omega
  have hset :
      (Finset.univ.filter fun a : PF n => M a = l) =
        (Finset.univ.filter fun a : PF n => M a ≤ l) \
          (Finset.univ.filter fun a : PF n => M a ≤ l-1) := by
    ext a
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_sdiff]
    omega
  unfold b A
  rw [hset, Finset.card_sdiff_of_subset hsub]

theorem Aint_neg_one (n : ℕ) : Aint n (-1) = 0 := by simp [Aint]

theorem Aint_nat (n l : ℕ) : Aint n (l : ℤ) = A n l := by simp [Aint]

theorem b_difference_int (n : ℕ+) (l : ℕ) :
    b n l = Aint n (l : ℤ) - Aint n ((l : ℤ)-1) := by
  cases l with
  | zero => simpa [Aint] using b_zero n
  | succ k =>
    have he : ((k+1 : ℕ) : ℤ)-1 = (k : ℤ) := by omega
    rw [show (k.succ : ℤ) = ((k+1 : ℕ) : ℤ) from rfl, he, Aint_nat, Aint_nat]
    simpa using b_difference n (k+1) (by omega)

theorem park_empty (a : Pref 0) : park a = some [] := by simp [park, run]

theorem M_empty (a : PF 0) : M a = 0 := by simp [M]

theorem A_empty (l : ℕ) : A 0 l = 1 := by
  have hm : ∀ a : PF 0, M a ≤ l := by intro a; simp [M]
  have hc : Fintype.card (PF 0) = 1 := by decide
  unfold A
  rw [Finset.filter_true_of_mem (fun a _ => hm a)]
  simpa using hc

theorem park_one : park (fun _ : Fin 1 => 0) = some [0] := by decide
theorem park_two_11 : park (fun _ : Fin 2 => 0) = some [0, 1] := by decide
theorem park_two_12 : park (fun i : Fin 2 => i) = some [0, 1] := by decide
theorem park_two_21 : park (fun i : Fin 2 => if i = 0 then 1 else 0) =
    some [1, 0] := by decide
theorem park_two_22 : park (fun _ : Fin 2 => 1) = none := by decide

theorem b_one : List.ofFn (fun l : Fin 1 => b 1 l.val) = [1] := by decide
theorem b_two : List.ofFn (fun l : Fin 2 => b 2 l.val) = [2, 1] := by decide

theorem unimodal_one_at_zero : UnimodalAt 1 0 := by
  refine ⟨by decide, ?_, ?_⟩
  · intro k hk; omega
  · intro k _ hk
    change k < 0 at hk
    omega

theorem unimodal_two_at_zero : UnimodalAt 2 0 := by
  refine ⟨by decide, ?_, ?_⟩
  · intro k hk; omega
  · intro k _ hk
    change k < 1 at hk
    have he : k = 0 := by omega
    subst k
    decide

theorem P_one : ∃ c : ℕ, UnimodalAt 1 c := ⟨0, unimodal_one_at_zero⟩
theorem P_two : ∃ c : ℕ, UnimodalAt 2 c := ⟨0, unimodal_two_at_zero⟩

-- Transitive axiom audit: every theorem in this source.
#print axioms next_spec
#print axioms next_failure
#print axioms run_fresh
#print axioms run_valid
#print axioms park_slots
#print axioms slots_valid
#print axioms slots_length
#print axioms slots_nodup
#print axioms pref_le_slot
#print axioms unimodal_iff
#print axioms P_iff_unimodal
#print axioms original_slot_range
#print axioms displacement_balance
#print axioms displacement_original
#print axioms displacement_le
#print axioms displacement_range
#print axioms displacement_le_M
#print axioms M_le
#print axioms M_attained
#print axioms A_saturation
#print axioms b_vanish
#print axioms A_monotone
#print axioms b_zero
#print axioms b_difference
#print axioms Aint_neg_one
#print axioms Aint_nat
#print axioms b_difference_int
#print axioms park_empty
#print axioms M_empty
#print axioms A_empty
#print axioms park_one
#print axioms park_two_11
#print axioms park_two_12
#print axioms park_two_21
#print axioms park_two_22
#print axioms b_one
#print axioms b_two
#print axioms unimodal_one_at_zero
#print axioms unimodal_two_at_zero
#print axioms P_one
#print axioms P_two
#print axioms P
#print P
#print UnimodalAt
end Parking
