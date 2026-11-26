# Reading the package as its public will

The package is assembled. In your folder, under `package/`, is a copy of it as it will be published, and this session is its first outside reader. A person who downloads the package has these files and nothing else: no access to the research, no knowledge of how the package was made, nobody to ask. You read the package's documents in that position, hold each of them against the package itself, and report what you find.

This instruction and the common text before it have told you things about the run that a visitor will not know. Read the package as if you had not been told them. A document that can only be understood with that knowledge has a fault, and that fault is a finding.

## What the reading is for

The user's requirement for the package is that it stand alone, so that the folder can be archived and uploaded as it is. Nothing in it may point outside itself or say that something exists on one machine only, and its build instructions have to work from the unpacked archive. Whether that holds cannot be seen by the sessions and scripts that made the package, since they all knew where everything came from. It can be seen by a reader who has only the result.

What you find is acted on at once. A finding in one of the two prose sections of the README, the outline of the proof and the account of how the result was obtained, goes to a session that corrects that passage. A finding in any other sentence cannot be corrected by the run, because the program wrote that sentence or an earlier stage fixed it. It is reported to the user as you wrote it, together with the package, and the user decides what to repair. So a finding has to be true, and it has to say what the package shows in its place. A point that you raised and that the package, on checking, bears out after all is dropped.

## What you are given

`package/`, with this layout:

```text
README.md                 what the package is, the result, what was checked and what was not, how to build
LICENSE
lean/                     the Lean project: lean-toolchain, lakefile.toml, lake-manifest.json, the library,
                          Check.lean, Challenge.lean, Solution.lean, comparator.json, formalization.yaml
records/                  one record for each public declaration of the library, and bibliography.bib
dependency-map/           dependency_map.html, .svg, .json
paper/                    paper.pdf, paper.tex, references.bib, correspondence.json
history/timeline.md
knowledge/MANIFEST.md
```

Two files of the published package are not in your copy, and their absence is not a finding. The archive of the research's records, which `knowledge/MANIFEST.md` describes, is left out for its size. `MANIFEST.sha256`, the list of checksums at the package's root, is written after your reading.

You have nothing else and you look nowhere else: not in the work folder of the run, not in the imported library, not on the web. You run no Lean and no build.

## What to read, and against what

The documents are `README.md`, `knowledge/MANIFEST.md`, `history/timeline.md`, `lean/formalization.yaml` and the paper, in `paper/paper.tex`. The library, the records and the other files are what the documents are held against. You are not asked to review the mathematics, the proofs or every record.

Begin with the README, from its first line, and follow it as a visitor would.

- **What it says exists.** Open every file and folder the README names, and follow every link. A name that is not there, or a link that leads out of the package, is a finding.
- **What it says the result is.** Find the declarations the README names as the root and the main theorem in the library, and compare their Lean statements with what the README prints. Compare the result as the README words it with the paper's main theorem.
- **Its figures.** Where the README gives a count, a version or a date that the package lets you check, check it: count the modules, the records, the entries of the timeline; read `lean/lean-toolchain` and `lean/lake-manifest.json` for the versions.
- **Its build instructions.** Follow them as far as reading allows. Does each command refer to a file that is there? Does each step say what a person needs who has only the unpacked folder: what to install, in which folder to run the command, what the output should be? Is anything assumed that only the machine of origin had, such as a library in a particular place?
- **What it says was checked and what was not.** Does the README make clear which checks a program made, which judgments AI sessions made, and what no person reviewed? Does `lean/formalization.yaml` say the same?
- **Its two prose sections.** Does the outline of the proof agree with the paper's introduction and name only declarations that the library has? Does the account of how the result was obtained agree with `history/timeline.md`?

Then read the other documents. `knowledge/MANIFEST.md` and `lean/formalization.yaml` are read as the README was: what each asserts about the package is held against the package, and each has to be clear to a visitor. The paper and the timeline were read closely in steps of their own, the paper for its mathematics and its writing and the timeline against the research's records, and that reading is not repeated here. Read them for what they share with the other documents: whether all documents agree in the title, in the statement of the result, in names and in figures.

Throughout, look for what must not be in a published package: a path of a drive or of a home folder, the name of an account, a reference to a folder or a tool that exists only where the package was made, and, outside the statements of what was checked and of how the library and the archive were made, a sentence that speaks of the run that assembled the package.

## What you write

`output/findings.json`, in this form:

```json
[{"file": "README.md", "quote": "...", "problem": "..."}]
```

`file` is the path of the document inside the package. `quote` is the passage, copied exactly, short enough to be found and long enough to be unique; where the finding is that something is missing, quote the sentence after which it would stand. `problem` says what is wrong and what the package shows in its place, with the file where you saw it, so that the session or the person who acts on the finding does not have to search.

If you could not read one of the documents named above, that is itself a finding: name the file, leave `quote` empty, and say under `problem` that it was not read and why.
