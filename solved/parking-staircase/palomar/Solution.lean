module

public import Staircase.Main

/-!
# Solution

The theorems `Parking.staircase` and `Parking.unimodal_via_staircase` that `Challenge.lean` states
are proved in `Staircase/Main.lean`. The definitions they speak of are in `Parking/Defs.lean` and
`Staircase/Peak.lean`. This module imports that proof, so that Comparator finds the two proved
declarations, and the definitions, under the names the Challenge uses.
-/
