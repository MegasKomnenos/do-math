# Putting back what the take removed and the library needs

The package presents one proof of the root, with `{{main}}` as its main theorem, and it contains only what that proof rests on. A script has therefore taken from the research's library the elements that are reached from `{{root}}` through what each statement mentions and each proof names, and has removed every other element as a whole. The library that remained does not build. This session brings it to build in two ways and in no other: it puts back the removed elements that the library still needs, and where what is needed is a theorem that the research left without a proof, it deletes the declarations that need it.

## Why the take can remove too much

The script works from the research's index, which records for each proof the elements that occur in the term Lean elaborated. Lean also uses declarations that leave no such trace, so a pruning from proof terms alone can remove a definition in a definition module, a lemma proved by `rfl` that `simp` applies without it appearing in any term, or a local notation. The script therefore never removes anything from a definition module, never removes an element that carries an attribute or is an `instance`, except a theorem that is not proved, and never touches what is no element: private declarations, notations, `open` and `variable` lines. A line that ends with `in`, such as `open Classical in`, belongs to the declaration below it and is removed with it. The script deletes a module only when no kept module imports it. A use it cannot see may still remain, for instance an element named in a notation or a macro, or in a `variable` line that later statements depend on. The compile is the test, and it has failed.

## What you are given

- `errors.txt`: what the build of the taken library reported. Read it in full; it names the modules that failed and gives Lean's messages.
- `lean/`: the library as the take left it.
- `before/`: the same files before the take, with the same paths.
- `removed.json`: the elements the take removed, in this form, each with the file it stood in and with `proved`, which is `false` for a theorem that the research left without a proof from the allowed axioms:

```json
[{"declaration": "Lib.x", "file": "Lib/A.lean", "proved": true}]
```

## What you do

Read the errors and find for each the removed element whose absence causes it. Most are an unknown identifier or constant that names a removed declaration directly. Others are indirect: a tactic that no longer closes a goal because a lemma it found by attribute is gone, or an instance that can no longer be found. For those, compare the failing file with its form in `before/` and look for what the passage relied on among the entries of `removed.json`.

Put a needed element back by restoring exactly the text the take cut out. Compare `before/<file>` with `lean/<file>`: each removed declaration is one block that stands in the first and is missing in the second. Copy that block back to the place it had, byte for byte, with the comment, the attributes and the lines ending with `in` that belong to it. An element you restore can itself use removed elements, so follow the errors until the build passes.

Some entries of `removed.json` have `proved` as `false`. A finished research holds, beside the proof of its root, theorems that were never proved from the allowed axioms, left from work that the proof of the root does not use, and the take removes them, because no theorem of the package may be left open. Such an element is never put back, whatever the errors ask for. What asks for it is a declaration that is no element, which the take left in place: a private lemma, a notation or an `attribute` line that names the theorem. It belongs to the same unused work, and you delete it: the whole declaration, with its comment, its attributes and the lines ending with `in` that belong to it, and then each declaration that is no element and uses one you deleted. A line goes whole or stays as it is. No element has to go for this: an element that used such a theorem, directly or through a private lemma, would not be proved itself, and the take has removed it. If an error shows that something which stays does need what you had to delete, the build cannot pass; return what you have, as the end of this instruction says.

The program accepts your output only if every file you return is the file of `before/` less whole removed elements and less the lines you deleted: no line is added or altered, no element with `proved` as `false` is back, and every element that stays, whether the take kept it or you put it back, stands as it stood. So change nothing but this: no edit of a proof to do without the missing lemma, no new import, no restored half of a declaration, no reformatting. Restore what the build needs and is proved, delete what needs a theorem without a proof, and leave the rest removed, since what the chosen proof does not use is not to be in the package. The program cannot tell whether the lines you deleted are exactly such declarations, so it records them for the user as you deleted them.

Build before you end, as the section "Compiling" describes, with `lean/` as the module root. Name as the files to compile those of every module that `errors.txt` reports, whether it was rejected itself or could not be compiled because a module it imports was rejected. The build has to end with exit code 0 for each.

## What you write

`output/lean/<file>` for each file you changed, at its path under `lean/`, complete. Return no file you did not change.

The form of this step has no field for a remark. If you could not bring the build to pass, return the files in which you restored and deleted what you found to be needed, provided each still has the form that the program accepts. The program builds what you return, and its report to the person who repairs the cause names the modules that still fail.
