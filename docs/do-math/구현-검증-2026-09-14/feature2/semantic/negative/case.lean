theorem successor_witness : ∀ n : Nat, ∃ m : Nat, m = n + 1 := by
  intro n
  exact ⟨n + 1, rfl⟩
