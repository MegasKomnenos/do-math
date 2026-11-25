# Reading the merged library whole, and arranging it by subject

The library that the chosen proof rests on, with `{{root}}` as its root and `{{main}}` as its main theorem, has just been simplified by several sessions side by side, each on one part and none seeing another's work. Their results have been put together, and the merged library compiles. This session reads the entire library as one thing. It finishes what the simplification of single parts had to leave open, removes what that work left behind, and arranges the modules by subject. It returns the whole library.

## What the step is for

Three things can only be done by a reader who has the whole library and may change all of it.

The first is to finish the simplifications that cross parts. The reviewing session gave each such item to one part, and the session of that part carried it out inside its own modules with the old declaration kept under its name, because the sessions of the other parts were writing against the old form at that moment. The proofs in those other parts still use the old form. You move them to the new one.

The second is to remove what is left behind once that is done: the old declaration that now only derives itself from its successor, a module that shrank to a few lines because another part still imported it, a general fact that two parts each kept private and that should be stated once. The user's standing decision for this work is that what is not used is deleted.

The third is the arrangement. The research added each module where the session that wrote it happened to put it, and the simplification kept every module in its part. A reader looks for a result where its subject is. The folder of a module is also how the dependency map of the package groups the results, and it is how the remaining work on the library is divided: after the records are written, the last changes to the library are given out folder by folder, one session for each folder, with the same rule that a session changes only its own. So a folder should be one portion of the mathematics that can be understood by itself, of a size one session can read through, and the cuts between folders should fall where few results cross. This follows the instruction the user gave when such a library was first prepared for publication: merge the parts, then have one session read the entire library and rearrange it by subject.

## What you are given

- `lean/`: the merged library, every file of it. Read it in full, proofs included.
- `review.json`: the review that preceded the simplification. Its `parts` name the modules of each part and what the review found worth simplifying inside it. Its `cross` lists the items that cross parts, each with its `owner`, with `what` the owner was to do, and under `touches` the parts whose modules use what the item changes.
- `reports/<part>.json`: the report of each part whose work was accepted: the modules it `deleted`, for each of its `cross` items whether it is `done` with a note on what remains in other parts, and `notes`: what it changed, which statements received a new form under a new name, which general facts it kept private, and what it saw and did not do. A part of `review.json` without a report stands as it was before the simplification, and its items are not done.
- `declarations.md`: the public declarations of the merged library, as the program's index has them. These are the names your output is held to.

Read `review.json` and all reports before the Lean, so that you read the library knowing what to look for.

## What you do

**Finish the cross-part items.** For each item that its owner reports as done, find the new form and move every use of the old form to it. For an item that is not done, decide from the Lean as it stands whether you can carry it out now that you may change both sides; the review's `what` and the owner's note are your material. Take up in the same way what the reports' `notes` describe as seen and not done, where it leaves a reader less mathematics to take in, as a proof made shorter by an opaque automation call or a lemma stated more generally than anything needs does not, and you can get it through the compiler.

**Remove what was left behind.** Remove a superseded declaration once nothing uses it. Remove a declaration that nothing in the library uses and that states nothing a reader of this proof would look for. Unite duplicates under one name. Where a declaration is used only inside its own module and exists only because one proof was written in pieces, it can become `private`. Search all of `lean/` for a name before you remove or rename it, since a use in a notation or an attribute line appears in no list, and let the compile decide.

**Arrange by subject.** Decide the folders from the mathematics: what the proof's main portions are, which results belong to each, and in which order a reader would meet them. Move declarations to the module of their subject, join modules that hold one topic in pieces, divide a module that holds two, and give modules and folders names that say what they hold. Every module stays under `{{library}}`. Rename a declaration where its name misleads or still carries the bookkeeping of the research, such as a namespace named after a session. A rename has a cost, because every record that mentions the old name is written again in the next step, so rename for the reader and not for taste.

**Bring the comments to the mathematics.** A comment that describes how the research went, or that mentions another proof, comes to say what the declaration states, or goes. The common text gives the rule and its reason.

Some things stay as they are. The definition modules keep their paths and their bytes. `{{root}}` and `{{main}}` keep their names and their statements. Every convention of the common text holds for every file.

Work in this order, in `lean/` itself, and build after each kind of change, with `lean/` as the module root and every `.lean` file under it named as a file to compile, in several commands if the list is too long for one. When a build has passed, keep a copy of that state in a folder of your own before you go on, so that you can return to it. Changing the name of a module changes the import line of every module that imports it; make such changes by script, and build afterwards.

## By what your output is judged

The program takes the library you return and requires the following. Every file is a module of at most 10,000 lines. Each definition module has the bytes it had when the root was posed. The whole library builds. The root is a theorem with the statement that was posed. Every theorem has a complete proof, and Lean reports for it no axiom beyond the three. No two names differ only in case. And every public declaration that `declarations.md` lists is accounted for: it is in the new library under its name, or under the new name that `renames.json` gives for it, or it is listed in `removed.json`. A declaration that you made private is no longer public and is listed in `removed.json` with that reason. A declaration that you united with another is listed there with the name of the one that remains.

Your arrangement is taken whole or not at all. If it fails one of these checks, it is discarded and the merged library goes on as you received it, so the cross-part items stay unfinished and the leftovers stay in. End on a state that builds. If you cannot bring a rearrangement to build, return the last state that did, even where that means a smaller rearrangement than you intended.

## What you write

- `output/lean/`: the library, with every file of it, at the paths of your arrangement. This is the whole library from here on: a file you leave out is a file removed. Copy the tree when your work is done and the build has passed, and see that no trial file lies in it.
- `output/renames.json`: an object that maps the full old name of each declaration you renamed to its full new name. A declaration that only moved to another module and kept its name has no entry. An empty object when you renamed nothing.

```json
{"Lib.old_name": "Lib.new_name"}
```

- `output/removed.json`: an array with one entry for each public declaration of `declarations.md` that the new library no longer has as a public declaration, with the reason. An empty array when there is none.

```json
[{"declaration": "Lib.unused", "reason": "..."}]
```

Write each reason for someone who has this file and not the library: what the declaration was, and why the library is better without it or what stands in its place.
