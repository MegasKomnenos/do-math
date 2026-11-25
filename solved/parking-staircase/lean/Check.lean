import Staircase.Main

/-!
After `lake build`, run `lake env lean Check.lean`. It prints the statements of the staircase and of
unimodality as its corollary, and the axioms their proofs depend on. The expected output is in
`README.md`.
-/

#check @Parking.staircase
#check @Parking.unimodal_via_staircase
#print axioms Parking.staircase
#print axioms Parking.unimodal_via_staircase
