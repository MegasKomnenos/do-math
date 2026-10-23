import SkeletonAlgebra
import Mathlib.Logic.Relation
import Mathlib.Data.Fintype.Option

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 3000000

namespace ParkingForest

/-- A parent function, with `none` denoting the virtual root. -/
abbrev Forest (V : Type*) [LT V] :=
  {p : V → Option V // ∀ u v, p u = some v → u < v}

instance {V : Type*} [LT V] [Fintype V] : Fintype (Forest V) := by
  classical
  unfold Forest
  infer_instance

def parent {V : Type*} [LT V] (G : Forest V) : V → Option V := G.val

def Edge {V : Type*} [LT V] (G : Forest V) (u v : V) : Prop :=
  parent G u = some v

def Anc {V : Type*} [LT V] (G : Forest V) : V → V → Prop :=
  Relation.ReflTransGen (Edge G)

def up {V : Type*} [LT V] (G : Forest V) : Option V → Option V
  | none => none
  | some u => parent G u

theorem anc_refl {V : Type*} [LT V] (G : Forest V) (u : V) : Anc G u u :=
  Relation.ReflTransGen.refl

theorem anc_trans {V : Type*} [LT V] (G : Forest V) {u v z : V}
    (h : Anc G u v) (h' : Anc G v z) : Anc G u z := h.trans h'

theorem anc_le {V : Type*} [LinearOrder V] (G : Forest V) {u v : V}
    (h : Anc G u v) : u ≤ v := by
  induction h with
  | refl => exact le_rfl
  | tail h e ih => exact ih.trans (le_of_lt (G.property _ _ e))

theorem up_none_iterate {V : Type*} [LT V] (G : Forest V) (k : ℕ) :
    (up G)^[k] none = none := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [Function.iterate_succ_apply', ih, up]

theorem anc_iterate {V : Type*} [LT V] (G : Forest V) (u v : V) :
    Anc G u v ↔ ∃ k : ℕ, (up G)^[k] (some u) = some v := by
  constructor
  · intro h
    induction h with
    | refl => exact ⟨0, rfl⟩
    | @tail v z h e ih =>
      obtain ⟨k,hk⟩ := ih
      exact ⟨k+1, by simpa only [Function.iterate_succ_apply', hk, up, Edge] using e⟩
  · rintro ⟨k,hk⟩
    induction k generalizing v with
    | zero =>
      have : u = v := Option.some.inj hk
      subst v
      exact anc_refl G u
    | succ k ih =>
      rw [Function.iterate_succ_apply'] at hk
      cases he : (up G)^[k] (some u) with
      | none => simp [he, up] at hk
      | some z =>
        have hz := ih z he
        exact hz.tail (by simpa [he, up, Edge] using hk)

def size {V : Type*} [LT V] (G : Forest V) (v : V) : ℕ :=
  Nat.card {u : V // Anc G u v}

def weight {V : Type*} [LT V] [Fintype V] (w : ℕ → ℕ) (G : Forest V) : ℕ :=
  ∏ v, w (size G v)

theorem size_eq_card_filter {V : Type*} [LT V] [Fintype V]
    (G : Forest V) (v : V) : size G v = (Finset.univ.filter (fun u => Anc G u v)).card := by
  simp [size, Nat.card_eq_fintype_card, Fintype.card_subtype]

def total {V : Type*} [LT V] [Fintype V] (w : ℕ → ℕ) : ℕ :=
  ∑ G : Forest V, weight w G

/-- Closure under taking a child (and hence any descendant). -/
def Closed {V : Type*} [LT V] (G : Forest V) (S : Set V) : Prop :=
  ∀ u v, Edge G u v → v ∈ S → u ∈ S

theorem closed_anc {V : Type*} [LT V] (G : Forest V) (S : Set V)
    (hc : Closed G S) {u v : V} (h : Anc G u v) (hv : v ∈ S) : u ∈ S := by
  induction h with
  | refl => exact hv
  | @tail v z h e ih => exact ih (hc _ _ e hv)

def restrict {V : Type*} [LT V] (G : Forest V) (S : Set V) : Forest S := by
  classical
  refine ⟨fun u => (parent G u).bind (fun v => if h : v ∈ S then some ⟨v,h⟩ else none), ?_⟩
  intro u v h
  cases he : parent G u with
  | none => simp [he] at h
  | some z =>
    simp only [he, Option.bind_some] at h
    split_ifs at h with hz
    · cases Option.some.inj h
      exact G.property _ _ he

theorem restrict_edge {V : Type*} [LT V] (G : Forest V) (S : Set V)
    (u v : S) : Edge (restrict G S) u v ↔ Edge G u.val v.val := by
  classical
  change ((parent G u).bind (fun z => if h : z ∈ S then some ⟨z,h⟩ else none)) = some v ↔ _
  cases he : parent G u with
  | none => simp [he, Edge]
  | some z =>
    simp only [Option.bind_some]
    split_ifs with hz
    · simp only [Option.some.injEq, Subtype.ext_iff, Edge, he, Option.some.injEq]
    · simp only [Option.noConfusion, false_iff, Edge, he, Option.some.injEq]
      intro hzv
      exact hz (hzv ▸ v.property)

theorem restrict_anc {V : Type*} [LT V] (G : Forest V) (S : Set V)
    (hc : Closed G S) (u v : S) :
    Anc (restrict G S) u v ↔ Anc G u.val v.val := by
  constructor
  · intro h
    induction h with
    | refl => exact anc_refl G _
    | tail h e ih => exact ih.tail ((restrict_edge G S _ _).mp e)
  · intro h
    have lift : ∀ {a b : V}, Anc G a b → ∀ (hb : b ∈ S),
        ∃ ha : a ∈ S, Anc (restrict G S) ⟨a,ha⟩ ⟨b,hb⟩ := by
      intro a b hab
      induction hab with
      | refl => intro hb; exact ⟨hb, anc_refl _ _⟩
      | @tail b c hab e ih =>
        intro hc'
        obtain ⟨ha, hh⟩ := ih (hc _ _ e hc')
        exact ⟨ha, hh.tail ((restrict_edge G S _ _).mpr e)⟩
    exact (lift h v.property).choose_spec

theorem restrict_size {V : Type*} [LT V] [Fintype V] (G : Forest V)
    (S : Set V) (hc : Closed G S) (v : S) :
    size (restrict G S) v = size G v.val := by
  classical
  unfold size
  apply Nat.card_congr
  refine { toFun := fun u => ⟨u.val.val, (restrict_anc G S hc _ _).mp u.property⟩
           invFun := fun u => ⟨⟨u.val, closed_anc G S hc u.property v.property⟩,
             (restrict_anc G S hc _ _).mpr u.property⟩
           left_inv := ?_, right_inv := ?_ }
  · intro u; rfl
  · intro u; rfl

theorem terminal_exists {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) (u : V) : ∃ z, Anc G u z ∧ parent G z = none := by
  classical
  let S := Finset.univ.filter (Anc G u)
  have hu : u ∈ S := by simp [S, anc_refl]
  let z := S.max' ⟨u,hu⟩
  have hz : z ∈ S := S.max'_mem _
  have huz : Anc G u z := (Finset.mem_filter.mp hz).2
  refine ⟨z,huz,?_⟩
  cases hp : parent G z with
  | none => rfl
  | some v =>
    have huv : Anc G u v := huz.tail hp
    have hv : v ∈ S := by simp [S,huv]
    have hle : v ≤ z := S.le_max' v hv
    exact (not_lt_of_ge hle (G.property _ _ hp)).elim

theorem reaches_virtual_root {V : Type*} [LinearOrder V] [Fintype V]
    (G : Forest V) (u : V) : ∃ k : ℕ, 1 ≤ k ∧ (up G)^[k] (some u) = none := by
  obtain ⟨z,huz,hz⟩ := terminal_exists G u
  obtain ⟨k,hk⟩ := (anc_iterate G u z).mp huz
  exact ⟨k+1, by omega, by simp only [Function.iterate_succ_apply',hk,up,hz]⟩

end ParkingForest
