import Init

/-- The Boolean equality test for adding zero on the right returns true. -/
def natAddZeroBeqGoal (n : Nat) : Prop := (n + 0 == n) = true

theorem natAddZeroBeq_zero : natAddZeroBeqGoal 0 := by simp [natAddZeroBeqGoal]
theorem natAddZeroBeq_one : natAddZeroBeqGoal 1 := by simp [natAddZeroBeqGoal]
theorem natAddZeroBeq_two : natAddZeroBeqGoal 2 := by simp [natAddZeroBeqGoal]

theorem natAddZeroBeq_all (n : Nat) : natAddZeroBeqGoal n := by
  simp [natAddZeroBeqGoal]


