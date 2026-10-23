import Recurrence

namespace ParkingLastCar
open Parking

/- The two algebraic bridges below reuse the original b-difference theorems.
   They state the already accepted original_bridge result in the current module. -/
theorem b_curvature (n : ℕ+) (l : ℕ) (hl : 1 ≤ l) :
    (b n (l+1) : ℤ) - (b n l : ℤ) =
      (A n (l+1) : ℤ) - 2*(A n l : ℤ) + (A n (l-1) : ℤ) := by
  have hn := A_monotone n (show l ≤ l+1 by omega)
  have hp := A_monotone n (show l-1 ≤ l by omega)
  rw [b_difference n (l+1) (by omega), b_difference n l hl]
  simp only [Nat.add_sub_cancel_right]
  rw [Int.ofNat_sub hn, Int.ofNat_sub hp]
  ring

theorem b_first_curvature (n : ℕ+) :
    (b n 1 : ℤ) - (b n 0 : ℤ) = (A n 1 : ℤ) - 2*(A n 0 : ℤ) := by
  have hn := A_monotone n (show 0 ≤ 1 by omega)
  rw [b_zero, b_difference n 1 (by omega)]
  norm_num only [Nat.sub_self] at *
  rw [Int.ofNat_sub hn]
  ring

/-- An explicit conditional interface for the separate sign research.
    The cutoff hypothesis itself is not proved here. The first difference is separate. -/
theorem P_from_cumulative_cutoffs
    (h : ∀ (n : ℕ), 1 ≤ n → ∃ c : ℕ, c < n ∧
      (0 < c → 2*(A n 0 : ℤ) ≤ (A n 1 : ℤ)) ∧
      (c = 0 → 1 < n → (A n 1 : ℤ) ≤ 2*(A n 0 : ℤ)) ∧
      (∀ k : ℕ, 1 ≤ k → k < c →
        2*(A n k : ℤ) ≤ (A n (k+1) : ℤ) + (A n (k-1) : ℤ)) ∧
      (∀ k : ℕ, 1 ≤ k → c ≤ k → k < n-1 →
        (A n (k+1) : ℤ) + (A n (k-1) : ℤ) ≤ 2*(A n k : ℤ))) : P := by
  intro n hn
  obtain ⟨c,hc,hfirstup,hfirstdown,hup,hdown⟩ := h n hn
  refine ⟨c,hc,?_,?_⟩
  · intro k hk
    by_cases hz : k = 0
    · subst k
      change b ⟨n,hn⟩ 0 ≤ b ⟨n,hn⟩ 1
      have hb := b_first_curvature (⟨n,hn⟩ : ℕ+)
      change (b ⟨n,hn⟩ 1 : ℤ) - (b ⟨n,hn⟩ 0 : ℤ) =
        (A n 1 : ℤ) - 2*(A n 0 : ℤ) at hb
      have ha := hfirstup hk
      omega
    · have hb := b_curvature (⟨n,hn⟩ : ℕ+) k (by omega)
      change (b ⟨n,hn⟩ (k+1) : ℤ) - (b ⟨n,hn⟩ k : ℤ) =
        (A n (k+1) : ℤ) - 2*(A n k : ℤ) + (A n (k-1) : ℤ) at hb
      have ha := hup k (by omega) hk
      omega
  · intro k hck hkn
    change k < n-1 at hkn
    by_cases hz : k = 0
    · subst k
      change b ⟨n,hn⟩ 1 ≤ b ⟨n,hn⟩ 0
      have hb := b_first_curvature (⟨n,hn⟩ : ℕ+)
      change (b ⟨n,hn⟩ 1 : ℤ) - (b ⟨n,hn⟩ 0 : ℤ) =
        (A n 1 : ℤ) - 2*(A n 0 : ℤ) at hb
      have ha := hfirstdown (by omega) (by omega)
      omega
    · have hb := b_curvature (⟨n,hn⟩ : ℕ+) k (by omega)
      change (b ⟨n,hn⟩ (k+1) : ℤ) - (b ⟨n,hn⟩ k : ℤ) =
        (A n (k+1) : ℤ) - 2*(A n k : ℤ) + (A n (k-1) : ℤ) at hb
      have ha := hdown k (by omega) hck hkn
      omega

#print axioms b_curvature
#print axioms b_first_curvature
#print axioms P_from_cumulative_cutoffs
end ParkingLastCar
