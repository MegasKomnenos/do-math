import Parking.Basic.Renewal

/-!
# The extreme-column bound

Let `G` be the renewal sequence of a positive log-convex kernel `f`, so that `G` is positive and
log-convex (`renewal_pos`, `renewal_logConvex`).  If `v` has nonnegative innovations
`v s - ∑_{i=1}^{s} f i * v (s - i)` for `s ≤ ρ`, and the weights `θ` are nonnegative and
nondecreasing on `M … ρ`, then

  `(∑_{m=M}^{ρ} θ m * f m * v (ρ - m)) * G ρ ≤ (∑_{m=M}^{ρ} θ m * f m * G (ρ - m)) * v ρ`.

In words: among all sequences with nonnegative innovations, the weighted feedback through the
kernel indices `≥ M`, measured against the last value, is largest for the sequence whose only
innovation sits at time `0`, which is `G` itself: the "extreme column".

Proof outline:
* `tail_cross` (private):
  `(∑_{m=K+1}^{s} f m * G (s - m)) * G ρ ≤ (∑_{m=K+1}^{ρ} f m * G (ρ - m)) * G s`
  for `K + 1 ≤ s ≤ ρ` (the renewal equation at `s` and at `ρ`, and `logConvex_cross` for `m ≤ K`);
* `weighted_cross`: the same with the weights `θ`, for every `s ≤ ρ`;
* `extreme_column_le`: `v` is the convolution of `G` with its innovations (`resolvent`); exchange
  the two sums and apply `weighted_cross` to each innovation.
-/

namespace Parking
open Finset

/-- `logConvex_cross` with subtractions: for `m ≤ s ≤ ρ`, `G s * G (ρ - m) ≤ G (s - m) * G ρ`. -/
private theorem logConvex_cross_sub {G : ℕ → ℝ} (hpos : ∀ n, 0 < G n)
    (hLC : ∀ n, G (n + 1) ^ 2 ≤ G n * G (n + 2)) {m s ρ : ℕ} (hms : m ≤ s) (hsρ : s ≤ ρ) :
    G s * G (ρ - m) ≤ G (s - m) * G ρ := by
  have h := logConvex_cross hpos hLC (Nat.sub_le_sub_right hsρ m) m
  rwa [Nat.sub_add_cancel hms, Nat.sub_add_cancel (hms.trans hsρ)] at h

/-- The tail of the renewal equation compared at two times `K + 1 ≤ s ≤ ρ`. -/
private theorem tail_cross {f G : ℕ → ℝ} (hf : ∀ i, 1 ≤ i → 0 ≤ f i) (hG : IsRenewal f G)
    (hpos : ∀ n, 0 < G n) (hLC : ∀ n, G (n + 1) ^ 2 ≤ G n * G (n + 2)) {K s ρ : ℕ}
    (hKs : K + 1 ≤ s) (hsρ : s ≤ ρ) :
    (∑ m ∈ Icc (K + 1) s, f m * G (s - m)) * G ρ
      ≤ (∑ m ∈ Icc (K + 1) ρ, f m * G (ρ - m)) * G s := by
  -- the renewal equation at `s` and at `ρ`, split after `K`
  have h1 : G s = ∑ m ∈ Icc 1 K, f m * G (s - m) + ∑ m ∈ Icc (K + 1) s, f m * G (s - m) :=
    (hG.2 s (by omega)).trans (sum_Icc_split _ (by omega) (by omega))
  have h2 : G ρ = ∑ m ∈ Icc 1 K, f m * G (ρ - m) + ∑ m ∈ Icc (K + 1) ρ, f m * G (ρ - m) :=
    (hG.2 ρ (by omega)).trans (sum_Icc_split _ (by omega) (by omega))
  -- the heads compare the other way, by log-convexity
  have h3 : (∑ m ∈ Icc 1 K, f m * G (ρ - m)) * G s
      ≤ (∑ m ∈ Icc 1 K, f m * G (s - m)) * G ρ := by
    rw [sum_mul, sum_mul]
    refine sum_le_sum fun m hm => ?_
    rw [mem_Icc] at hm
    have hc : G s * G (ρ - m) ≤ G (s - m) * G ρ :=
      logConvex_cross_sub hpos hLC (by omega) hsρ
    calc f m * G (ρ - m) * G s = f m * (G s * G (ρ - m)) := by ring
      _ ≤ f m * (G (s - m) * G ρ) := mul_le_mul_of_nonneg_left hc (hf m hm.1)
      _ = f m * G (s - m) * G ρ := by ring
  have hTs : ∑ m ∈ Icc (K + 1) s, f m * G (s - m)
      = G s - ∑ m ∈ Icc 1 K, f m * G (s - m) := by linarith
  have hTρ : ∑ m ∈ Icc (K + 1) ρ, f m * G (ρ - m)
      = G ρ - ∑ m ∈ Icc 1 K, f m * G (ρ - m) := by linarith
  rw [hTs, hTρ]
  linarith

/-- The weighted tail of the renewal equation compared at two times `s ≤ ρ`, for weights `θ`
that are nonnegative and nondecreasing on `K + 1 … ρ`. -/
private theorem weighted_cross {f G θ : ℕ → ℝ} (hf : ∀ i, 1 ≤ i → 0 ≤ f i) (hG : IsRenewal f G)
    (hpos : ∀ n, 0 < G n) (hLC : ∀ n, G (n + 1) ^ 2 ≤ G n * G (n + 2)) {K s ρ : ℕ}
    (hθ0 : 0 ≤ θ (K + 1)) (hθ : ∀ a b, K + 1 ≤ a → a ≤ b → b ≤ ρ → θ a ≤ θ b) (hsρ : s ≤ ρ) :
    (∑ m ∈ Icc (K + 1) s, θ m * (f m * G (s - m))) * G ρ
      ≤ (∑ m ∈ Icc (K + 1) ρ, θ m * (f m * G (ρ - m))) * G s := by
  have hθnn : ∀ m, K + 1 ≤ m → m ≤ ρ → 0 ≤ θ m :=
    fun m hm1 hm2 => hθ0.trans (hθ (K + 1) m le_rfl hm1 hm2)
  rcases Nat.lt_or_ge s (K + 1) with hKs | hKs
  · -- the left sum is empty
    rw [Icc_eq_empty_of_lt hKs, sum_empty, zero_mul]
    refine mul_nonneg (sum_nonneg fun m hm => ?_) (hpos s).le
    rw [mem_Icc] at hm
    exact mul_nonneg (hθnn m hm.1 hm.2) (mul_nonneg (hf m (by omega)) (hpos (ρ - m)).le)
  · have hθs : 0 ≤ θ s := hθnn s hKs hsρ
    -- the two sums over `Icc (K + 1) ρ`, split after `s`
    have hsplitθ : ∑ m ∈ Icc (K + 1) ρ, θ m * (f m * G (ρ - m))
        = ∑ m ∈ Icc (K + 1) s, θ m * (f m * G (ρ - m))
          + ∑ m ∈ Icc (s + 1) ρ, θ m * (f m * G (ρ - m)) :=
      sum_Icc_split _ (by omega) hsρ
    have hsplit : ∑ m ∈ Icc (K + 1) ρ, f m * G (ρ - m)
        = ∑ m ∈ Icc (K + 1) s, f m * G (ρ - m) + ∑ m ∈ Icc (s + 1) ρ, f m * G (ρ - m) :=
      sum_Icc_split _ (by omega) hsρ
    -- (A) on `Icc (K + 1) s` the weights are at most `θ s` and the differences are nonnegative
    have hA : (∑ m ∈ Icc (K + 1) s, θ m * (f m * G (s - m))) * G ρ
        - (∑ m ∈ Icc (K + 1) s, θ m * (f m * G (ρ - m))) * G s
        ≤ θ s * ((∑ m ∈ Icc (K + 1) s, f m * G (s - m)) * G ρ
          - (∑ m ∈ Icc (K + 1) s, f m * G (ρ - m)) * G s) := by
      have e1 : (∑ m ∈ Icc (K + 1) s, θ m * (f m * G (s - m))) * G ρ
          - (∑ m ∈ Icc (K + 1) s, θ m * (f m * G (ρ - m))) * G s
          = ∑ m ∈ Icc (K + 1) s, θ m * (f m * (G (s - m) * G ρ - G s * G (ρ - m))) := by
        rw [sum_mul, sum_mul, ← sum_sub_distrib]
        exact sum_congr rfl fun m _ => by ring
      have e2 : θ s * ((∑ m ∈ Icc (K + 1) s, f m * G (s - m)) * G ρ
          - (∑ m ∈ Icc (K + 1) s, f m * G (ρ - m)) * G s)
          = ∑ m ∈ Icc (K + 1) s, θ s * (f m * (G (s - m) * G ρ - G s * G (ρ - m))) := by
        rw [sum_mul, sum_mul, ← sum_sub_distrib, mul_sum]
        exact sum_congr rfl fun m _ => by ring
      rw [e1, e2]
      refine sum_le_sum fun m hm => ?_
      rw [mem_Icc] at hm
      have hc : G s * G (ρ - m) ≤ G (s - m) * G ρ := logConvex_cross_sub hpos hLC hm.2 hsρ
      exact mul_le_mul_of_nonneg_right (hθ m s hm.1 hm.2 hsρ)
        (mul_nonneg (hf m (by omega)) (by linarith))
    -- (B) on `Icc (s + 1) ρ` the weights are at least `θ s`
    have hB : θ s * (∑ m ∈ Icc (s + 1) ρ, f m * G (ρ - m))
        ≤ ∑ m ∈ Icc (s + 1) ρ, θ m * (f m * G (ρ - m)) := by
      rw [mul_sum]
      refine sum_le_sum fun m hm => ?_
      rw [mem_Icc] at hm
      exact mul_le_mul_of_nonneg_right (hθ s m hKs (by omega) hm.2)
        (mul_nonneg (hf m (by omega)) (hpos (ρ - m)).le)
    -- (C) the unweighted comparison
    have hC := tail_cross hf hG hpos hLC hKs hsρ
    rw [hsplit] at hC
    have hC' : θ s * ((∑ m ∈ Icc (K + 1) s, f m * G (s - m)) * G ρ
          - (∑ m ∈ Icc (K + 1) s, f m * G (ρ - m)) * G s)
        ≤ θ s * ((∑ m ∈ Icc (s + 1) ρ, f m * G (ρ - m)) * G s) :=
      mul_le_mul_of_nonneg_left (by linarith) hθs
    have hB' : θ s * (∑ m ∈ Icc (s + 1) ρ, f m * G (ρ - m)) * G s
        ≤ (∑ m ∈ Icc (s + 1) ρ, θ m * (f m * G (ρ - m))) * G s :=
      mul_le_mul_of_nonneg_right hB (hpos s).le
    rw [hsplitθ]
    linarith

/-- **Extreme-column bound.**  Let `G` be the renewal sequence of a positive log-convex kernel
`f`.  If `v` has nonnegative innovations up to `ρ` and the weights `θ` are nonnegative and
nondecreasing on `M … ρ`, then the weighted feedback through the kernel indices `≥ M`, measured
against `v ρ`, is at most its value for `v = G`. -/
theorem extreme_column_le {f G v θ : ℕ → ℝ} {ρ M : ℕ}
    (hf : ∀ i, 1 ≤ i → 0 < f i) (hlc : ∀ j, f (j + 2) ^ 2 ≤ f (j + 1) * f (j + 3))
    (hG : IsRenewal f G) (hM : 1 ≤ M) (hθ0 : 0 ≤ θ M)
    (hθ : ∀ a b, M ≤ a → a ≤ b → b ≤ ρ → θ a ≤ θ b)
    (hinn : ∀ s, s ≤ ρ → ∑ i ∈ Icc 1 s, f i * v (s - i) ≤ v s) :
    (∑ m ∈ Icc M ρ, θ m * (f m * v (ρ - m))) * G ρ
      ≤ (∑ m ∈ Icc M ρ, θ m * (f m * G (ρ - m))) * v ρ := by
  obtain ⟨K, rfl⟩ : ∃ K, M = K + 1 := ⟨M - 1, by omega⟩
  have hf0 : ∀ i, 1 ≤ i → 0 ≤ f i := fun i hi => (hf i hi).le
  have hpos : ∀ n, 0 < G n := renewal_pos hf hG
  have hLC : ∀ n, G (n + 1) ^ 2 ≤ G n * G (n + 2) := renewal_logConvex hf hlc hG
  -- the innovations `ι` of `v`; `v` is the convolution of `G` and `ι`
  obtain ⟨ι, hι⟩ : ∃ ι : ℕ → ℝ, ∀ s, ι s = v s - ∑ i ∈ Icc 1 s, f i * v (s - i) :=
    ⟨fun s => v s - ∑ i ∈ Icc 1 s, f i * v (s - i), fun _ => rfl⟩
  have hι0 : ∀ s, s ≤ ρ → 0 ≤ ι s := fun s hs => by
    rw [hι s]
    exact sub_nonneg.mpr (hinn s hs)
  have hres : ∀ s, v s = ∑ c ∈ range (s + 1), G (s - c) * ι c :=
    resolvent hG fun s => by rw [hι s]; ring
  -- the weighted feedback of `G`, abbreviated
  obtain ⟨W, hW⟩ : ∃ W : ℝ, W = ∑ m ∈ Icc (K + 1) ρ, θ m * (f m * G (ρ - m)) := ⟨_, rfl⟩
  have hW0 : 0 ≤ W := by
    rw [hW]
    refine sum_nonneg fun m hm => ?_
    rw [mem_Icc] at hm
    exact mul_nonneg (hθ0.trans (hθ (K + 1) m le_rfl hm.1 hm.2))
      (mul_nonneg (hf0 m (by omega)) (hpos (ρ - m)).le)
  rw [← hW]
  -- expand `v (ρ - m)` and exchange the two sums
  have h1 : ∑ m ∈ Icc (K + 1) ρ, θ m * (f m * v (ρ - m))
      = ∑ c ∈ range (ρ - K), ∑ m ∈ Icc (K + 1) (ρ - c), θ m * (f m * (G (ρ - m - c) * ι c)) := by
    have h : ∑ m ∈ Icc (K + 1) ρ, θ m * (f m * v (ρ - m))
        = ∑ m ∈ Icc (K + 1) ρ, ∑ c ∈ range (ρ - m + 1),
            θ m * (f m * (G (ρ - m - c) * ι c)) :=
      sum_congr rfl fun m _ => by rw [hres (ρ - m), mul_sum, mul_sum]
    rw [h]
    refine sum_comm' fun m c => ?_
    simp only [mem_Icc, mem_range]
    omega
  -- each innovation contributes at most its share of `W * v ρ`
  have h2 : (∑ c ∈ range (ρ - K), ∑ m ∈ Icc (K + 1) (ρ - c),
        θ m * (f m * (G (ρ - m - c) * ι c))) * G ρ
      ≤ ∑ c ∈ range (ρ - K), W * (G (ρ - c) * ι c) := by
    rw [sum_mul]
    refine sum_le_sum fun c hc => ?_
    rw [mem_range] at hc
    have e : ∑ m ∈ Icc (K + 1) (ρ - c), θ m * (f m * (G (ρ - m - c) * ι c))
        = (∑ m ∈ Icc (K + 1) (ρ - c), θ m * (f m * G (ρ - c - m))) * ι c := by
      rw [sum_mul]
      refine sum_congr rfl fun m _ => ?_
      rw [show ρ - m - c = ρ - c - m by omega]
      ring
    have hw := weighted_cross hf0 hG hpos hLC hθ0 hθ (Nat.sub_le ρ c)
    rw [← hW] at hw
    rw [e]
    calc (∑ m ∈ Icc (K + 1) (ρ - c), θ m * (f m * G (ρ - c - m))) * ι c * G ρ
        = (∑ m ∈ Icc (K + 1) (ρ - c), θ m * (f m * G (ρ - c - m))) * G ρ * ι c := by ring
      _ ≤ W * G (ρ - c) * ι c := mul_le_mul_of_nonneg_right hw (hι0 c (by omega))
      _ = W * (G (ρ - c) * ι c) := by ring
  -- the innovations left out are nonnegative
  have h3 : ∑ c ∈ range (ρ - K), W * (G (ρ - c) * ι c)
      ≤ ∑ c ∈ range (ρ + 1), W * (G (ρ - c) * ι c) := by
    refine sum_le_sum_of_subset_of_nonneg (range_subset_range.2 (by omega)) fun c hc _ => ?_
    rw [mem_range] at hc
    exact mul_nonneg hW0 (mul_nonneg (hpos (ρ - c)).le (hι0 c (by omega)))
  calc (∑ m ∈ Icc (K + 1) ρ, θ m * (f m * v (ρ - m))) * G ρ
      ≤ ∑ c ∈ range (ρ + 1), W * (G (ρ - c) * ι c) := by
        rw [h1]
        exact h2.trans h3
    _ = W * v ρ := by rw [hres ρ, mul_sum]

end Parking