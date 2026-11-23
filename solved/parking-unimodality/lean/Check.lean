import Parking.Unimodal

/-!
After `lake build`, run `lake env lean Check.lean`. It prints the statement of the main theorem and
the axioms its proof depends on. The expected output is in `README.md`.
-/

#check @Parking.root_unimodal
#print axioms Parking.root_unimodal
