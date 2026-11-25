# Putting back what the take removed and the library needs

The package presents one proof of the root, with `{{main}}` as its main theorem, and it contains only what that proof rests on. A script has therefore taken from the research's library the elements that are reached from `{{root}}` through what each statement mentions and each proof names, and has removed every other element as a whole. The library that remained does not build. This session finds which of the removed elements it still needs and puts them back, and does nothing else.

## Why the take can remove too much

The script works from the research's index, which records for each proof the elements that occur in the term Lean elaborated. Lean also uses declarations that leave no such trace. An earlier tool that pruned from proof terms alone removed a definition from the definitions file, a lemma proved by `rfl` that `simp` applied without it appearing in any term, and a local notation. The script is built to avoid those cases. It never removes anything from a definition module, never removes an element that carries an attribute or is an `instance`, and never touches what is no element: private declarations, notations, `open` and `variable` lines. It deletes a module only when no kept module imports it. A use it cannot see may still remain, for instance an element named in an attribute line that stands apart from its declaration, in a notation or a macro, or in a `variable` line that later statements depend on. The compile is the test, and it has failed.

## What you are given

- `errors.txt`: what the build of the taken library reported. Read it in full; it names the modules that failed and gives Lean's messages.
- `lean/`: the library as the take left it.
- `before/`: the same files before the take, with the same paths.
- `removed.json`: the elements the take removed, in this form, each with the file it stood in:

```json
[{"declaration": "Lib.x", "file": "Lib/A.lean"}]
```

## What you do

Read the errors and find for each the removed element whose absence causes it. Most are an unknown identifier or constant that names a removed declaration directly. Others are indirect: a tactic that no longer closes a goal because a lemma it found by attribute is gone, or an instance that can no longer be found. For those, compare the failing file with its form in `before/` and look for what the passage relied on among the entries of `removed.json`.

Put a needed element back by restoring exactly the text the take cut out. Compare `before/<file>` with `lean/<file>`: each removed declaration is one block that stands in the first and is missing in the second. Copy that block back to the place it had, byte for byte, with the comment and the attributes that belong to it. An element you restore can itself use removed elements, so follow the errors until the build passes.

The program accepts your output only if every file you return is the file of `before/` less whole removed elements. So change nothing but this: no edit of a proof to do without the missing lemma, no new import, no restored half of a declaration, no reformatting. Restore what the build needs and leave the rest removed, since what the chosen proof does not use is not to be in the package.

Build before you end, as the section "Compiling" describes, with `lean/` as the module root. Name as the files to compile those of every module that `errors.txt` reports, whether it was rejected itself or could not be compiled because a module it imports was rejected. The build has to end with exit code 0 for each.

## What you write

`output/lean/<file>` for each file you changed, at its path under `lean/`, complete. Return no file you did not change.

The form of this step has no field for a remark. If you could not bring the build to pass, return the files in which you restored what you found to be needed, provided each is still a file of `before/` less whole removed elements. The program builds what you return, and its report to the person who repairs the cause names the modules that still fail.
