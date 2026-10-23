import ForestTransport

open scoped BigOperators
noncomputable section
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 6000000
namespace ParkingForest

variable {V : Type*} [LinearOrder V] [Fintype V]

abbrev Outside (r : V) (S : Finset V) := {v : V // v ≠ r ∧ v ∉ S}

abbrev Parts (r : V) :=
  Σ S : {S : Finset V // r ∉ S}, Forest (S.val : Set V) × Forest (Outside r S.val)


def subtreeLabels (G : Forest V) (r : V) : Finset V := by
  classical
  exact Finset.univ.filter (fun u => u ≠ r ∧ Anc G u r)

theorem mem_subtreeLabels (G : Forest V) (r u : V) :
    u ∈ subtreeLabels G r ↔ u ≠ r ∧ Anc G u r := by
  classical
  simp [subtreeLabels]

theorem root_not_mem (G : Forest V) (r : V) : r ∉ subtreeLabels G r := by
  simp [mem_subtreeLabels]

theorem root_parent (G : Forest V) (r : V) (hr : ∀u, u ≤ r) : parent G r = none := by
  cases hp : parent G r with
  | none => rfl
  | some v => exact (not_lt_of_ge (hr v) (G.property _ _ hp)).elim

theorem subtree_closed (G : Forest V) (r : V) : Closed G (subtreeLabels G r : Set V) := by
  intro u v huv hv
  obtain ⟨hvr,hv⟩ := (mem_subtreeLabels G r v).mp hv
  have hur : u ≠ r := by
    intro hur
    subst u
    have hh := anc_le G hv
    have hi := G.property _ _ huv
    exact (not_lt_of_ge hh) hi
  exact (mem_subtreeLabels G r u).mpr ⟨hur, hv.head huv⟩

theorem outside_closed (G : Forest V) (r : V) (hr : ∀u, u ≤ r) :
    Closed G {v | v ≠ r ∧ v ∉ subtreeLabels G r} := by
  intro u v huv hv
  have hur : u ≠ r := by
    intro h; subst u
    have hi := G.property _ _ huv
    exact (not_lt_of_ge (hr v)) hi
  refine ⟨hur, ?_⟩
  intro hu
  obtain ⟨_,hu⟩ := (mem_subtreeLabels G r u).mp hu
  have hvr : Anc G v r := by
    rcases hu.cases_head with he | ⟨z,hez,hzr⟩
    · exact (hur he).elim
    · have : z = v := Option.some.inj (hez.symm.trans huv)
      simpa only [this, Anc] using hzr
  exact hv.2 ((mem_subtreeLabels G r v).mpr ⟨hv.1,hvr⟩)

def split (G : Forest V) (r : V) : Parts r :=
  ⟨⟨subtreeLabels G r, root_not_mem G r⟩,
    restrict G (subtreeLabels G r : Set V),
    restrict G {v | v ≠ r ∧ v ∉ subtreeLabels G r}⟩

def pasteParent (r : V) (S : Finset V) (F : Forest (S : Set V))
    (H : Forest (Outside r S)) (u : V) : Option V := by
  classical
  exact if hu : u = r then none else if hs : u ∈ S then
    match parent F ⟨u,hs⟩ with
    | none => some r
    | some v => some v.val
  else (parent H ⟨u,hu,hs⟩).map Subtype.val

def paste (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) : Forest V := by
  classical
  refine ⟨pasteParent r S F H, ?_⟩
  intro u v h
  unfold pasteParent at h
  split_ifs at h with hur huS
  · cases hp : parent F ⟨u,huS⟩ with
    | none =>
      simp only [hp, Option.some.injEq] at h
      subst v
      exact lt_of_le_of_ne (hr u) hur
    | some z =>
      simp only [hp, Option.some.injEq] at h
      subst v
      exact F.property _ _ hp
  · cases hp : parent H ⟨u,hur,huS⟩ with
    | none => simp [hp] at h
    | some z =>
      simp only [hp, Option.map_some, Option.some.injEq] at h
      subst v
      exact H.property _ _ hp

def join (r : V) (hr : ∀u, u ≤ r) (P : Parts r) : Forest V :=
  paste r hr P.1.val P.1.property P.2.1 P.2.2

@[simp] theorem paste_parent_root (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    parent (paste r hr S hs F H) r = none := by
  simp [parent,paste,pasteParent]

theorem paste_parent_left (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : (S : Set V)) :
    parent (paste r hr S hs F H) u.val =
      match parent F u with | none => some r | some v => some v.val := by
  have hur : u.val ≠ r := by intro h; exact hs (h ▸ u.property)
  simp [parent,paste,pasteParent,hur,u.property]

theorem paste_parent_right (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : Outside r S) :
    parent (paste r hr S hs F H) u.val = (parent H u).map Subtype.val := by
  simp [parent,paste,pasteParent,u.property.1,u.property.2]

theorem restrict_paste_left (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    restrict (paste r hr S hs F H) (S : Set V) = F := by
  apply Subtype.ext
  funext u
  change (parent (paste r hr S hs F H) u.val).bind _ = parent F u
  rw [paste_parent_left]
  cases hp : parent F u with
  | none => simp [hs]
  | some v => simp [v.property] <;> rfl

theorem restrict_paste_right (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    restrict (paste r hr S hs F H) {u | u ≠ r ∧ u ∉ S} = H := by
  apply Subtype.ext
  funext u
  change (parent (paste r hr S hs F H) u.val).bind _ = parent H u
  rw [paste_parent_right]
  cases hp : parent H u with
  | none => simp
  | some v => simp [v.property] <;> rfl

theorem paste_closed_left (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    Closed (paste r hr S hs F H) (S : Set V) := by
  intro u v huv hv
  by_cases hur : u = r
  · subst u
    change parent (paste r hr S hs F H) r = some v at huv
    simp at huv
  by_cases huS : u ∈ S
  · exact huS
  change parent (paste r hr S hs F H) u = some v at huv
  rw [paste_parent_right r hr S hs F H ⟨u,hur,huS⟩] at huv
  cases hp : parent H ⟨u,hur,huS⟩ with
  | none => simp [hp] at huv
  | some z =>
    simp only [hp,Option.map_some,Option.some.injEq] at huv
    exact (z.property.2 (huv.symm ▸ hv)).elim

theorem paste_closed_right (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    Closed (paste r hr S hs F H) {u | u ≠ r ∧ u ∉ S} := by
  intro u v huv hv
  by_cases hur : u = r
  · subst u
    change parent (paste r hr S hs F H) r = some v at huv
    simp at huv
  refine ⟨hur,?_⟩
  intro huS
  change parent (paste r hr S hs F H) u = some v at huv
  rw [paste_parent_left r hr S hs F H ⟨u,huS⟩] at huv
  cases hp : parent F ⟨u,huS⟩ with
  | none => simp only [hp,Option.some.injEq] at huv; exact hv.1 huv.symm
  | some z =>
    simp only [hp,Option.some.injEq] at huv
    exact hv.2 (huv ▸ z.property)

theorem paste_left_reaches_root (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : (S : Set V)) :
    Anc (paste r hr S hs F H) u.val r := by
  obtain ⟨z,huz,hz⟩ := terminal_exists F u
  have ha : Anc (restrict (paste r hr S hs F H) (S : Set V)) u z := by
    rw [restrict_paste_left]
    exact huz
  have ha' := (restrict_anc _ _ (paste_closed_left r hr S hs F H) u z).mp ha
  apply ha'.tail
  change parent (paste r hr S hs F H) z.val = some r
  rw [paste_parent_left,hz]

theorem paste_anc_root (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : V) :
    Anc (paste r hr S hs F H) u r ↔ u = r ∨ u ∈ S := by
  constructor
  · intro ha
    have hc : Closed (paste r hr S hs F H) {u | u = r ∨ u ∈ S} := by
      intro a b hab hb
      by_cases har : a = r
      · exact Or.inl har
      by_cases haS : a ∈ S
      · exact Or.inr haS
      change parent (paste r hr S hs F H) a = some b at hab
      rw [paste_parent_right r hr S hs F H ⟨a,har,haS⟩] at hab
      cases hp : parent H ⟨a,har,haS⟩ with
      | none => simp [hp] at hab
      | some z =>
        simp only [hp,Option.map_some,Option.some.injEq] at hab
        rcases hb with hb | hb
        · exact (z.property.1 (hab.trans hb)).elim
        · exact (z.property.2 (hab.symm ▸ hb)).elim
    exact closed_anc _ _ hc ha (Or.inl rfl)
  · rintro (rfl | hu)
    · exact anc_refl _ _
    · exact paste_left_reaches_root r hr S hs F H ⟨u,hu⟩

theorem paste_labels (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    subtreeLabels (paste r hr S hs F H) r = S := by
  ext u
  rw [mem_subtreeLabels,paste_anc_root]
  constructor
  · rintro ⟨hn,he|hm⟩
    · exact (hn he).elim
    · exact hm
  · intro hu
    exact ⟨by intro he; exact hs (he ▸ hu), Or.inr hu⟩

theorem paste_size_left (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : (S : Set V)) :
    size (paste r hr S hs F H) u.val = size F u := by
  have h := restrict_size (paste r hr S hs F H) (S : Set V)
    (paste_closed_left r hr S hs F H) u
  rw [restrict_paste_left] at h
  exact h.symm

theorem paste_size_right (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (u : Outside r S) :
    size (paste r hr S hs F H) u.val = size H u := by
  have h := restrict_size (paste r hr S hs F H) {u | u ≠ r ∧ u ∉ S}
    (paste_closed_right r hr S hs F H) u
  rw [restrict_paste_right] at h
  exact h.symm

theorem paste_size_root (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) :
    size (paste r hr S hs F H) r = S.card + 1 := by
  rw [size_eq_card_filter]
  have he : Finset.univ.filter (fun u => Anc (paste r hr S hs F H) u r) = insert r S := by
    ext u
    simp only [Finset.mem_filter,Finset.mem_univ,true_and,Finset.mem_insert,paste_anc_root]
  rw [he,Finset.card_insert_of_notMem hs]

theorem join_split (G : Forest V) (r : V) (hr : ∀u, u ≤ r) :
    join r hr (split G r) = G := by
  apply Subtype.ext
  funext u
  change parent (paste r hr (subtreeLabels G r) (root_not_mem G r)
    (restrict G (subtreeLabels G r : Set V))
    (restrict G {v | v ≠ r ∧ v ∉ subtreeLabels G r})) u = parent G u
  by_cases hur : u = r
  · subst u
    rw [paste_parent_root,root_parent G r hr]
  by_cases huS : u ∈ subtreeLabels G r
  · rw [paste_parent_left r hr _ _ _ _ ⟨u,huS⟩]
    have ha := ((mem_subtreeLabels G r u).mp huS).2
    rcases ha.cases_head with he | ⟨v,huv,hvr⟩
    · exact (hur he).elim
    change parent G u = some v at huv
    by_cases hvr' : v = r
    · subst v
      have hn : parent (restrict G (subtreeLabels G r : Set V)) ⟨u,huS⟩ = none := by
        cases hp : parent (restrict G (subtreeLabels G r : Set V)) ⟨u,huS⟩ with
        | none => rfl
        | some z =>
          have hz := (restrict_edge G _ ⟨u,huS⟩ z).mp hp
          have he : z.val = r := Option.some.inj (hz.symm.trans huv)
          have hzS : z.val ∈ subtreeLabels G r := z.property
          rw [he] at hzS
          exact (root_not_mem G r hzS).elim
      rw [hn,huv]
    · have hvS := (mem_subtreeLabels G r v).mpr ⟨hvr',hvr⟩
      have hp := (restrict_edge G _ ⟨u,huS⟩ ⟨v,hvS⟩).mpr huv
      change parent (restrict G (subtreeLabels G r : Set V)) ⟨u,huS⟩ = some ⟨v,hvS⟩ at hp
      rw [hp,huv]
  · rw [paste_parent_right r hr _ _ _ _ ⟨u,hur,huS⟩]
    cases hp : parent G u with
    | none =>
      have hn : parent (restrict G {v | v ≠ r ∧ v ∉ subtreeLabels G r}) ⟨u,hur,huS⟩ = none := by
        cases hq : parent (restrict G {v | v ≠ r ∧ v ∉ subtreeLabels G r}) ⟨u,hur,huS⟩ with
        | none => rfl
        | some z =>
          have hz := (restrict_edge G {v | v ≠ r ∧ v ∉ subtreeLabels G r} ⟨u,hur,huS⟩ z).mp hq
          change parent G u = some z.val at hz
          simp [hp] at hz
      exact (congrArg (fun o : Option {v : V // v ≠ r ∧ v ∉ subtreeLabels G r} =>
        o.map Subtype.val) hn).trans rfl
    | some v =>
      have hvr : v ≠ r := by
        intro he; subst v
        exact huS ((mem_subtreeLabels G r u).mpr ⟨hur,Relation.ReflTransGen.single hp⟩)
      have hvS : v ∉ subtreeLabels G r := by
        intro hv
        exact huS (subtree_closed G r u v hp hv)
      have hq := (restrict_edge G {v | v ≠ r ∧ v ∉ subtreeLabels G r}
        ⟨u,hur,huS⟩ ⟨v,hvr,hvS⟩).mpr hp
      change parent (restrict G {v | v ≠ r ∧ v ∉ subtreeLabels G r}) ⟨u,hur,huS⟩ = some ⟨v,hvr,hvS⟩ at hq
      exact (congrArg (fun o : Option {v : V // v ≠ r ∧ v ∉ subtreeLabels G r} =>
        o.map Subtype.val) hq).trans rfl

theorem join_injective (r : V) (hr : ∀u, u ≤ r) : Function.Injective (join r hr) := by
  rintro ⟨⟨S,hs⟩,F,H⟩ ⟨⟨T,ht⟩,F',H'⟩ he
  change paste r hr S hs F H = paste r hr T ht F' H' at he
  have hST : S = T := by
    rw [← paste_labels r hr S hs F H, ← paste_labels r hr T ht F' H',he]
  subst T
  have hF : F = F' := by
    rw [← restrict_paste_left r hr S hs F H, ← restrict_paste_left r hr S hs F' H',he]
  have hH : H = H' := by
    rw [← restrict_paste_right r hr S hs F H, ← restrict_paste_right r hr S hs F' H',he]
  subst F'; subst H'; rfl

theorem split_join (r : V) (hr : ∀u, u ≤ r) (P : Parts r) :
    split (join r hr P) r = P := by
  apply join_injective r hr
  exact join_split (join r hr P) r hr

def splitEquiv (r : V) (hr : ∀u, u ≤ r) : Forest V ≃ Parts r where
  toFun := fun G => split G r
  invFun := join r hr
  left_inv := fun G => join_split G r hr
  right_inv := split_join r hr

def vertexEquiv (r : V) (S : Finset V) (hs : r ∉ S) :
    V ≃ Unit ⊕ ((S : Set V) ⊕ Outside r S) where
  toFun u := if hu : u = r then Sum.inl () else if hS : u ∈ S then
    Sum.inr (Sum.inl ⟨u,hS⟩) else Sum.inr (Sum.inr ⟨u,hu,hS⟩)
  invFun := fun u => match u with
    | Sum.inl _ => r
    | Sum.inr (Sum.inl v) => v.val
    | Sum.inr (Sum.inr v) => v.val
  left_inv u := by dsimp; split_ifs <;> simp_all
  right_inv u := by
    rcases u with u | (u|u)
    · cases u; simp
    · have hur : u.val ≠ r := by intro h; exact hs (h ▸ u.property)
      simp [hur,u.property]
    · simp [u.property.1,u.property.2]

theorem card_outside (r : V) (S : Finset V) (hs : r ∉ S) :
    Fintype.card (Outside r S) + S.card + 1 = Fintype.card V := by
  have he := Fintype.card_congr (vertexEquiv r S hs)
  have hc : Fintype.card (S : Set V) = S.card := by
    simp [Fintype.card_subtype]
  simp only [Fintype.card_sum,Fintype.card_unit,hc] at he
  omega

theorem paste_weight (r : V) (hr : ∀u, u ≤ r) (S : Finset V) (hs : r ∉ S)
    (F : Forest (S : Set V)) (H : Forest (Outside r S)) (w : ℕ → ℕ) :
    weight w (paste r hr S hs F H) = w (S.card+1) * weight w F * weight w H := by
  unfold weight
  rw [← (vertexEquiv r S hs).symm.prod_comp (fun u => w (size (paste r hr S hs F H) u))]
  simp only [Fintype.prod_sum_type,Fintype.prod_unique,Equiv.symm_apply_apply]
  change w (size (paste r hr S hs F H) r) *
    ((∏u : (S : Set V), w (size (paste r hr S hs F H) u.val)) *
      ∏u : Outside r S, w (size (paste r hr S hs F H) u.val)) = _
  simp_rw [paste_size_root,paste_size_left,paste_size_right]
  ring

theorem total_split (r : V) (hr : ∀u, u ≤ r) (w : ℕ → ℕ) :
    total (V := V) w = ∑ S : {S : Finset V // r ∉ S},
      w (S.val.card+1) * total (V := (S.val : Set V)) w * total (V := Outside r S.val) w := by
  unfold total
  rw [← (splitEquiv r hr).symm.sum_comp (weight w)]
  change (∑ P : Parts r, weight w (join r hr P)) = _
  simp only [join,paste_weight]
  rw [Fintype.sum_sigma]
  simp only [Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro S _
  simp only [Finset.mul_sum,Finset.sum_mul]
  rw [Finset.sum_comm]

theorem sum_avoid_card (r : V) (f : ℕ → ℕ) :
    (∑ S : {S : Finset V // r ∉ S}, f S.val.card) =
      ∑ k ∈ Finset.range (Fintype.card V), (Fintype.card V-1).choose k * f k := by
  let U := (Finset.univ : Finset V).erase r
  have hu : U.card = Fintype.card V - 1 := by simp [U]
  have he : (Finset.univ.filter (fun S : Finset V => r ∉ S)) = U.powerset := by
    ext S
    simp only [Finset.mem_filter,Finset.mem_univ,true_and,Finset.mem_powerset]
    simp [U,Finset.subset_erase]
  rw [← Finset.sum_subtype (Finset.univ.filter (fun S : Finset V => r ∉ S))
    (by simp) (fun S : Finset V => f S.card),he,Finset.sum_powerset]
  simp_rw [Finset.sum_powersetCard]
  have hp : 1 ≤ Fintype.card V := Fintype.card_pos_iff.mpr ⟨r⟩
  simpa [hu,show Fintype.card V-1+1=Fintype.card V by omega]

end ParkingForest
