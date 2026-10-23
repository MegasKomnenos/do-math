import Parking
import Mathlib.Data.Finset.Sort
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Tactic

namespace ParkingLastCar
open Parking

/-- A record of the first-free condition, with the arrival order explicit. -/
def Certified {m n : ℕ} (o : Finset (Fin n)) (a p : Fin m → Fin n) : Prop :=
  Function.Injective p ∧ (∀ i, p i ∉ o) ∧
  (∀ i, a i ≤ p i) ∧
  ∀ i s, a i ≤ s → s < p i → s ∈ o ∨ ∃ j, j < i ∧ p j = s

theorem certified_run {m n : ℕ} (o : Finset (Fin n)) (a p : Fin m → Fin n)
    (h : Certified o a p) :
    run (List.ofFn a) o = some (List.ofFn p) := by
  induction m generalizing o with
  | zero => simp [run]
  | succ m ih =>
    rcases h with ⟨hinj, hfree, hle, hcover⟩
    have hn : next (a 0) o = some (p 0) := by
      apply (next_spec _ _ _).mpr
      refine ⟨hle 0, hfree 0, ?_⟩
      intro s has hso
      by_contra hh
      rcases hcover 0 s has (lt_of_not_ge hh) with ho | ⟨j, hj, _⟩
      · exact hso ho
      · exact (not_lt_of_ge (Fin.zero_le j)) hj
    have ht : Certified (insert (p 0) o) (fun i => a i.succ) (fun i => p i.succ) := by
      refine ⟨hinj.comp (Fin.succ_injective m), ?_, (fun i => hle i.succ), ?_⟩
      · intro i hi
        rcases Finset.mem_insert.mp hi with he | ho
        · have he' := hinj he
          exact Fin.succ_ne_zero i he'
        · exact hfree i.succ ho
      · intro i s has hsp
        rcases hcover i.succ s has hsp with ho | ⟨j, hji, hpj⟩
        · exact Or.inl (Finset.mem_insert_of_mem ho)
        · refine Fin.cases ?_ (fun j hj hpj => ?_) j hji hpj
          · intro _ hp0
            exact Or.inl (hp0 ▸ Finset.mem_insert_self _ _)
          · exact Or.inr ⟨j, Fin.succ_lt_succ_iff.mp hj, hpj⟩
    simpa [List.ofFn_succ, run, hn, ih _ _ _ ht]

theorem run_certified {m n : ℕ} (o : Finset (Fin n)) (a p : Fin m → Fin n)
    (h : run (List.ofFn a) o = some (List.ofFn p)) : Certified o a p := by
  induction m generalizing o with
  | zero =>
    refine ⟨?_, ?_, ?_, ?_⟩ <;> intro i <;> exact Fin.elim0 i
  | succ m ih =>
    have hn : next (a 0) o = some (p 0) := by
      cases he : next (a 0) o with
      | none => simp [List.ofFn_succ, run, he] at h
      | some s =>
        cases hr : run (List.ofFn (fun i : Fin m => a i.succ)) (insert s o) with
        | none => simp [List.ofFn_succ, run, he, hr] at h
        | some ps =>
          have hh : s :: ps = p 0 :: List.ofFn (fun i : Fin m => p i.succ) := by
            simpa [List.ofFn_succ, run, he, hr] using h
          simpa [List.cons.inj hh |>.1] using he
    have hr : run (List.ofFn (fun i : Fin m => a i.succ)) (insert (p 0) o) =
        some (List.ofFn (fun i : Fin m => p i.succ)) := by
      cases he : run (List.ofFn (fun i : Fin m => a i.succ)) (insert (p 0) o) with
      | none => simp [List.ofFn_succ, run, hn, he] at h
      | some ps => simpa [List.ofFn_succ, run, hn, he] using h
    rcases ih _ _ _ hr with ⟨hinj, hfree, hle, hcover⟩
    have hs := (next_spec _ _ _).mp hn
    refine ⟨?_, ?_, ?_, ?_⟩
    · intro i
      refine Fin.cases ?_ (fun i => ?_) i
      · intro j
        refine Fin.cases ?_ (fun j => ?_) j
        · intro _; rfl
        · intro hj
          exact False.elim (hfree j (Finset.mem_insert.mpr (Or.inl hj.symm)))
      · intro j
        refine Fin.cases ?_ (fun j => ?_) j
        · intro hj
          exact False.elim (hfree i (Finset.mem_insert.mpr (Or.inl hj)))
        · intro hj
          exact congrArg Fin.succ (hinj hj)
    · intro i
      refine Fin.cases hs.2.1 (fun i ho => hfree i (Finset.mem_insert_of_mem ho)) i
    · intro i
      exact Fin.cases hs.1 hle i
    · intro i
      refine Fin.cases ?_ (fun i s has hsp => ?_) i
      · intro s has hsp
        left
        by_contra hso
        exact (not_le_of_gt hsp) (hs.2.2 s has hso)
      · rcases hcover i s has hsp with ho | ⟨j, hj, hpj⟩
        · rcases Finset.mem_insert.mp ho with he | ho
          · exact Or.inr ⟨0, Fin.succ_pos i, he.symm⟩
          · exact Or.inl ho
        · exact Or.inr ⟨j.succ, Fin.succ_lt_succ_iff.mpr hj, hpj⟩

theorem run_iff_certified {m n : ℕ} (o : Finset (Fin n)) (a p : Fin m → Fin n) :
    run (List.ofFn a) o = some (List.ofFn p) ↔ Certified o a p :=
  ⟨run_certified o a p, certified_run o a p⟩

theorem slots_ofFn {n : ℕ} (a : PF n) : List.ofFn (slot a) = slots a := by
  apply List.ext_getElem
  · simp [slots_length]
  · intro i hi hj
    simp [slot]

theorem original_certified {n : ℕ} (a : PF n) : Certified ∅ a.val (slot a) := by
  apply run_certified
  rw [slots_ofFn]
  exact park_slots a

theorem max_le_iff {n : ℕ} (a : PF n) (l : ℕ) :
    M a ≤ l ↔ ∀ i, (slot a i).val - (a.val i).val ≤ l := by
  simp [M, displacement, Finset.sup_le_iff]

/-- Certificates retain the actual preference, rather than defining a recurrence sequence. -/
abbrev Trace (n l : ℕ) :=
  {ap : Pref n × Pref n // Certified ∅ ap.1 ap.2 ∧ ∀ i, (ap.2 i).val - (ap.1 i).val ≤ l}

noncomputable instance traceFintype (n l : ℕ) : Fintype (Trace n l) := by
  classical
  exact Fintype.ofFinite _

def traceOf {n l : ℕ} (a : {a : PF n // M a ≤ l}) : Trace n l :=
  ⟨(a.val.val, slot a.val), original_certified a.val, (max_le_iff _ _).mp a.property⟩

def originalOf {n l : ℕ} (x : Trace n l) : {a : PF n // M a ≤ l} := by
  have hr := certified_run ∅ x.val.1 x.val.2 x.property.1
  let a : PF n := ⟨x.val.1, by simp [Success, park, hr]⟩
  have hp : slot a = x.val.2 := by
    have he : List.ofFn (slot a) = List.ofFn x.val.2 := by
      rw [slots_ofFn]
      exact Option.some.inj ((park_slots a).symm.trans hr)
    exact List.ofFn_inj.mp he
  exact ⟨a, (max_le_iff _ _).mpr (by simpa [a, hp] using x.property.2)⟩

def traceEquiv (n l : ℕ) : {a : PF n // M a ≤ l} ≃ Trace n l where
  toFun := traceOf
  invFun := originalOf
  left_inv a := by apply Subtype.ext; apply Subtype.ext; rfl
  right_inv x := by
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · have h1 := certified_run ∅ x.val.1 x.val.2 x.property.1
      have h2 := certified_run ∅ (originalOf x).val.val (slot (originalOf x).val)
        (original_certified (originalOf x).val)
      have he := Option.some.inj (h2.symm.trans h1)
      exact List.ofFn_inj.mp he

theorem card_trace (n l : ℕ) : Fintype.card (Trace n l) = A n l := by
  rw [← Fintype.card_congr (traceEquiv n l)]
  exact Fintype.card_subtype (fun a : PF n => M a ≤ l)

#print axioms certified_run
#print axioms run_certified
#print axioms run_iff_certified
#print axioms slots_ofFn
#print axioms original_certified
#print axioms max_le_iff
#print axioms traceOf
#print axioms originalOf
#print axioms traceEquiv
#print axioms card_trace
end ParkingLastCar
