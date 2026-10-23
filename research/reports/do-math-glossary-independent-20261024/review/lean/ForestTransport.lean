import Forest

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 3000000
namespace ParkingForest

def relabel {A B : Type*} [LinearOrder A] [LinearOrder B]
    (e : A ≃o B) (G : Forest A) : Forest B := by
  refine ⟨fun b => (parent G (e.symm b)).map e, ?_⟩
  intro u v h
  cases hp : parent G (e.symm u) with
  | none => simp [hp] at h
  | some z =>
    simp only [hp, Option.map_some, Option.some.injEq] at h
    have hz := e.strictMono (G.property _ _ hp)
    simpa [h] using hz

@[simp] theorem relabel_parent {A B : Type*} [LinearOrder A] [LinearOrder B]
    (e : A ≃o B) (G : Forest A) (a : A) :
    parent (relabel e G) (e a) = (parent G a).map e := by
  simp [parent, relabel]

theorem relabel_edge {A B : Type*} [LinearOrder A] [LinearOrder B]
    (e : A ≃o B) (G : Forest A) (u v : A) :
    Edge (relabel e G) (e u) (e v) ↔ Edge G u v := by
  simp only [Edge, relabel_parent]
  cases hp : parent G u <;> simp [e.injective.eq_iff]

theorem relabel_anc {A B : Type*} [LinearOrder A] [LinearOrder B]
    (e : A ≃o B) (G : Forest A) (u v : A) :
    Anc (relabel e G) (e u) (e v) ↔ Anc G u v := by
  constructor
  · intro h
    have hh : ∀ {a b : B}, Anc (relabel e G) a b → Anc G (e.symm a) (e.symm b) := by
      intro a b hab
      induction hab with
      | refl => exact anc_refl _ _
      | @tail b c h edge ih =>
        apply ih.tail
        apply (relabel_edge e G _ _).mp
        simpa using edge
    simpa using hh h
  · intro h
    induction h with
    | refl => exact anc_refl _ _
    | tail h edge ih => exact ih.tail ((relabel_edge e G _ _).mpr edge)

theorem relabel_size {A B : Type*} [LinearOrder A] [LinearOrder B]
    [Fintype A] [Fintype B] (e : A ≃o B) (G : Forest A) (v : A) :
    size (relabel e G) (e v) = size G v := by
  classical
  unfold size
  apply Nat.card_congr
  refine { toFun := fun u => ⟨e.symm u.val, (relabel_anc e G _ _).mp (by simpa using u.property)⟩
           invFun := fun u => ⟨e u.val, (relabel_anc e G _ _).mpr u.property⟩
           left_inv := ?_, right_inv := ?_ }
  · intro u; apply Subtype.ext; simp
  · intro u; apply Subtype.ext; simp

theorem relabel_weight {A B : Type*} [LinearOrder A] [LinearOrder B]
    [Fintype A] [Fintype B] (e : A ≃o B) (G : Forest A) (w : ℕ → ℕ) :
    weight w (relabel e G) = weight w G := by
  unfold weight
  rw [← e.toEquiv.prod_comp (fun b => w (size (relabel e G) b))]
  change (∏ a : A, w (size (relabel e G) (e a))) = ∏ a : A, w (size G a)
  simp_rw [relabel_size]

def relabelEquiv {A B : Type*} [LinearOrder A] [LinearOrder B]
    (e : A ≃o B) : Forest A ≃ Forest B where
  toFun := relabel e
  invFun := relabel e.symm
  left_inv G := by
    apply Subtype.ext
    funext u
    change ((parent G (e.symm (e u))).map e).map e.symm = parent G u
    cases h : parent G u <;> simp [h]
  right_inv G := by
    apply Subtype.ext
    funext u
    change ((parent G (e (e.symm u))).map e.symm).map e = parent G u
    cases h : parent G u <;> simp [h]

theorem relabel_total {A B : Type*} [LinearOrder A] [LinearOrder B]
    [Fintype A] [Fintype B] (e : A ≃o B) (w : ℕ → ℕ) :
    total (V := A) w = total (V := B) w := by
  classical
  apply Fintype.sum_equiv (relabelEquiv e)
  intro G
  exact (relabel_weight e G w).symm

def standardizeEquiv (V : Type*) [LinearOrder V] [Fintype V] :
    Forest (Fin (Fintype.card V)) ≃ Forest V :=
  relabelEquiv (Fintype.orderIsoFinOfCardEq V rfl)

theorem standardize_size (V : Type*) [LinearOrder V] [Fintype V]
    (G : Forest (Fin (Fintype.card V))) (v : Fin (Fintype.card V)) :
    size (standardizeEquiv V G) (Fintype.orderIsoFinOfCardEq V rfl v) = size G v :=
  relabel_size _ G v

end ParkingForest
