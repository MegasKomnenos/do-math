# Digest C2: verification, Lean machinery, end-of-run commands, and the rest of the repository

## What this file is and how to read it

This file is an account of one area of the repository, taken from the sources on 2026-11-23, for the rewriting of `C:\math\README.md` and `C:\math\docs\do-math\running.md`. It is a digest and not a source: check a sentence against the location given after it before relying on it.

**Source notation.** Every fact is followed by `file:line`. Line numbers are those of the working tree on 2026-11-23. Most source files hold one paragraph per line, so a line number names a paragraph. Five files are cited so often that they have a short name:

| Short name | File |
|---|---|
| `V` | `C:\math\docs\do-math\lean-canon-verification.md` |
| `OPS` | `C:\math\.claude\skills\do-math\reference\operations.md` |
| `LB` | `C:\math\.claude\skills\do-math\reference\lean-broker.md` |
| `LEAN` | `C:\math\.claude\skills\do-math\reference\lean.md` |
| `PM` | `C:\math\.claude\skills\do-math\reference\paper-method.md` |

Other files are cited by a path relative to `C:\math\`, except that `SK` stands for `.claude/skills/do-math/SKILL.md` and `tests/` for `.claude/skills/do-math/runtime/tests/`.

**Three marks.** `[inferred]` marks a statement that no source makes in so many words and that I drew from the sources named beside it. `[counted]` marks a number I obtained by searching or listing, without running any program of the repository. `[listing]` marks a fact read from a directory listing or from `git status` / `git diff`.

**State of the working tree.** `git status` shows uncommitted changes: `CITATION.cff`, `LICENSE`, `README.md` and `THIRD-PARTY-NOTICES.md` are modified, and `ROADMAP.md` and `docs/do-math/first-run-parking-unimodality.md` are deleted `[listing]`. The modifications change the licence from the Mozilla Public License 2.0 to the GNU Affero General Public License v3.0 in all four files `[listing: git diff]`. This digest describes the working tree.

---

# Part 1. The current facts

## 1. Verification of the current implementation

All of this topic comes from `V`. The document says of itself that it records "what was run to check that implementation, what each run showed, and what no run has shown" (V:5), and that the implementation it describes is the canonical skill `.claude/skills/do-math/`, in which the knowledge of an instance is a Lean library from its first session on (V:3).

### 1.1 Dates

The document dates only three things. The first real research with this implementation was started on 22 November 2026 (V:217, V:302). Seven test modules and one module of the older copy were run on 23 November 2026 (V:274). The runners of both running instances were restarted "at about 04:05 that day" (V:289). No other run in the document carries a date. The folder of the small research run by real sessions is named `do-math-e2e-20261122` (V:63), from which a date of 22 November 2026 can be guessed `[inferred]`.

### 1.2 The three conditions and the document's own summary

The agreement before the implementation fixed three conditions: the tests pass; a small proposition runs from its Lean root to a dependency map and to the PDF of a paper; the guides pass independent reading (V:9). The document says all three are met, and that "the first is met in the sense that the table states" (V:11). The table's qualifications are these.

- Tests: each of "the sixteen test modules" passed in its last run; the runtime was changed several times after the last run of the whole suite, and the suite was not run as a whole again (V:15).
- Map and paper: the map was drawn and one command produced the paper as a LaTeX manuscript and its PDF; the paper command was changed twice after that run; one run of the changed command went to its end and produced a manuscript and a PDF, and ended with exit code 2 because the readings beside real papers still reported differences (V:16).
- Guides: the design record and the final guides were read independently and two rounds of review and repair followed; the guides were revised afterwards, and that revision "was compared with the text it replaced and was not read independently from the beginning" (V:17).

Three limits qualify the results (V:19): the research that real sessions ran was one small research and exercised only the paths one small research takes; the tests replace the Lean compiler by a stand-in and so do not show how the real compiler behaves; and at the scale of a research that imports Mathlib, what has been run is the first day of one research.

### 1.3 Runs with the real compiler and no AI sessions

- Lean 4.32.0 was used, without Mathlib (V:55).
- The scripted research that `test_pipeline` runs was run once against the real compiler in place of the stand-in. It finished in 579 seconds with the root formally proved. Creating the instance took 41.7 seconds (V:57).
- That run included a step the real-session research did not reach: the root first receives a proof in words with a Lean declaration ending in `sorry`, and the proof is then replaced in place by a complete Lean proof, with an import added to the root's module (V:57).
- The five compiles that extract the index had a median of 57 seconds, and each was charged about 2.1 GB of Windows commit charge, on the machine while another research instance was running on it (V:57).
- One measurement corrected an expectation of the design: replacing a proof leaves the compiled public output of its module unchanged only when the new proof makes the elaborator generate the same auxiliary declarations as the old one; otherwise the importing modules are compiled again (V:59).
- This scripted run was not repeated against the real compiler on Lean 4.36.0 (V:213).

### 1.4 The one research run from start to finish by real AI sessions and real Lean

- One research was run from start to finish by real AI sessions and the real compiler. Its proposition: the sum of the first n odd natural numbers is n squared (V:63).
- The operator's part followed the guide: the root in words, a definition and the root statement in Lean in two modules, a record for each declaration, and a check of the definition on six known values as a theorem with a complete proof (V:63).
- The instance is kept at `.skill-workspace/do-math-e2e-20261122/instance`, a local folder outside version control (V:63).
- The runner launched six sessions, all on one model (`claude/opus`, effort high): an attempt, an exploration, a peer for each, and a review for each candidate (V:65).
- The attempt found a complete Lean proof by induction; its peer made the candidate (V:67). The review compiled the candidate itself, read the axioms (`propext` and `Quot.sound`), confirmed and accepted the proof; the runner built, installed and committed. The root was formally proved 863 seconds after the attempt started (V:68).
- The exploration's peer published, 2,377 seconds after the attempt started, nineteen further elements with complete Lean proofs and the first understanding text of the root question; among them two proofs that review confirmed as correct and did not yet accept (V:69).
- The runner then ended (V:70). The canon at the end holds 23 elements: three definitions, eighteen statements whose proofs are accepted, two whose proofs are correct and held back. Twenty statements are formal (V:72).
- **What this run did not exercise** (V:74): no formalizer was launched; two publications were too few for an organizer; no candidate failed to build, so no replacement peer; no candidate offered a replacement for a proof the canon held; no concern or contested statement led to a comprehensive review; no statement was refuted. "These paths are covered by the tests and, for the formalizer's replacement in place, by the scripted run with the real compiler. No real session has yet followed the guides along them." (V:74)
- No real Codex session is recorded for this research: all six sessions were on `claude/opus` `[inferred from V:65]`.

### 1.5 The first research that imports Mathlib (running since 22 November 2026)

- Root: the Erdős–Rado sunflower conjecture. Lean 4.36.0 with Mathlib 4.36.0. Between six and twelve sessions ran at a time on a machine with four processor cores (V:217).
- A second research ran on the same machine throughout, from the copy `.agents/skills/do-math`, "which is a generation older and uses Lean 4.32.0" (V:217).
- Within hours the compiles of both were slow. The larger causes lay in the machine: the admitted compiles needed more physical memory than it had, and the sessions gave four cores more work than they carry. Part of the cause lay in the runtime: its own processes took processor time, and about a third of the time that compiles ran was spent on compiles that only measure memory (V:217).
- Four changes were made to the runtime during that first day, each after a measurement on the running instance and each measured again afterwards (V:217). The shares of a core were read while the processor was at or near full load, "so they are rough" (V:219).

| Change | Before | After | Source |
|---|---|---|---|
| A command waiting for a broker job looks only for the job's result file | read the 2.5 MB state file four times a second; about 30 ms per reading; about 5% of one core per waiting command | about 0.1 ms per look; about 0.2% of one core | V:221 |
| The broker saves its state without indentation, in one piece | 52% of profiler samples in the writing of the state file; one save 337 ms; broker about 30% of one core | one save 35 ms; broker 1% to 2% of one core; in the older copy 19–30% to about 7% | V:223 |
| The runner rereads a session file only when it changed; the broker lists processes once a second | runner about 5% of one core | runner 2.7%; the effect of the process listing "is not known" because no compile was running when it was read | V:225 |
| Baselines estimated from the size on disk of what a set of imports loads | 114 sets measured in 378 minutes of compiling | see next table | V:227 |

Checks of the baseline estimate (V:233–239):

| Check | Result | Source |
|---|---|---|
| The instance's 114 measured sets replayed in order, real Mathlib 4.36.0 library | 10 would have been measured, 104 estimated; estimates off by 0.6% in the median, 1.9% at most; 68 below the measurement (by 34 MB at most), 36 above (by 53 MB at most) | V:235 |
| The older instance's 47 measured sets, Lean 4.32.0 library | 8 measured, 39 estimated; off by 0.9% in the median, 2.4% at most | V:236 |
| One compile with a new import set on the new instance | estimated 2050.2 MB from 1534.2 MB of compiled files; the compile reached 2059.3 MB, which shows the estimate too low by 9.1 MB at most | V:237 |
| One such compile on the older instance | estimated 1894.4 MB; reached 1894.9 MB | V:238 |
| The new instance afterwards | in the next 65 compiles, two estimates and no measuring compile | V:239 |

- The brokers of both instances were replaced three times each to run the changed code; each time the queue was as before and no job failed. The runner of the new instance was restarted once with the documented command (V:248).
- Faults observed in this instance, each of which led to a repair: three of the first six finished reviews ended their only turn while their three sub-reviewers were still running, left no assessment and were replaced by new sessions (V:264); one peer's finished candidate went to a replacement peer because its end decision had been inside the candidate's receipt (V:265).
- What the recorded builds of the instance show, examined "without running anything", on its 93 finished builds with an extraction and its broker's job records (V:291): 122 declarations extracted more than once under differently compiled environments, 121 with one hash throughout (V:293); the one exception is the root, whose statement elaborated differently once because a Mathlib import reached its module, with unchanged meaning, and `prepare` refused that candidate (V:294); after the change 14 builds extracted the importing modules as well, two of them publications (revisions 6 and 7), none reporting a changed statement (V:295); the seven judge jobs of publications all ended with code 0, median 47 seconds and 3.0 GB at the peak, at most 213 seconds and 3.8 GB (V:296).
- One fault of the first day changed no code: compiles ran at a priority below normal, and when a session's computation and three abandoned whole-disk searches took all four cores, five running compiles received two to five seconds of processor time each in seven to eleven minutes. The operator set `lean.priority` to `normal` and ended the searches. "The runtime does nothing about such a case by itself." (V:256)
- The document does not say how this research ended or what it has established; it says the research "has been running" (V:302) `[inferred: no outcome is recorded]`.

### 1.6 What was run with the real Lean tools for the judge (no AI sessions)

On Lean 4.36.0 and Windows, on the small canon of the research of 1.4 (V:190):

| Case | Result | Source |
|---|---|---|
| `init` with the judge, canon with one theorem proved by `decide` | Accepted; the index records the theorem as judged at revision 0 | V:194 |
| The same theorem with one proved by `native_decide`, given to the judge's job through the broker | Rejected: the generated axiom is not permitted | V:195 |
| A complete Lean proof of the root, prepared and published through the runner's own publication, without sessions | Published; the judge accepted the root; the root's state is `formal_proved`. Ten minutes on a heavily loaded machine, nearly all in the judge's job | V:196 |
| The exports of the root as fixed and as proved, given to the comparator by hand | Accepted, and accepted again "with every kernel that Lean ships: `lean4lean`, `nanoda` and the two further checkers beside Lean's own" | V:197 |
| The unsolved root offered as its own solution, by hand | Rejected: `sorryAx` | V:198 |
| The proved root over a definition whose body had been changed, by hand | Rejected: the definition does not match | V:199 |
| The generated theorem for a root proved through another declaration and for a refuted root | Each compiles | V:200 |

Lean 4.36.0 itself: installed beside 4.32.0 with the Mathlib release for it; the archive matched its checksum; `init` created an instance from the small canon with no change to the runtime (V:186). A module compile writes a fifth file, `.ir.sig`, on 4.36.0, which the broker keeps; the test stand-in still writes four (V:186). "The measurements that the guides quote were taken on 4.32.0 and were not repeated." (V:186) Mathlib 4.36.0 was checked with one file that imports two of its modules and proves an identity with `ring`; the import of all of Mathlib was not made, because a research instance was running and about 6 GB of memory was left to commit (V:186).

### 1.7 A defect the tests could not see

The index counted an axiom of the canon only when the axiom was a public declaration with a place in the source. Lean's `native_decide` adds a private generated axiom for each computation, so a theorem proved by `native_decide` was recorded as proved from the allowed axioms. The defect was confirmed on the rows Lean 4.36.0 printed and corrected. "The stand-in compiler of the tests prints no generated axioms, and that is how the defect remained while every test passed." (V:184) An earlier defect of the same kind: the index extraction imported only the modules a change had touched, the real compiler therefore could not confirm a claim across modules, and the stand-in, which sees every module at once, confirmed it; a peer met the refusal in the real-session research and worked around it; the review rounds repaired both the extraction and the stand-in (V:51).

### 1.8 Independent reading and the review rounds

- The design record was read fifteen times by a reader that received the manuscript and a description of its reader and nothing else, and revised after each reading (V:118).
- The guides were read in three stages; the third was two rounds of review and repair over the guides, the runtime and the tests, 68 files. In each round six repairers wrote findings with complete repairs, and three judges decided each finding independently; a repair was applied only when all three approved (V:120–122).
- Round 1: 29 findings, 25 applied, 3 rejected, 1 left to the user. Round 2: 21 findings, 19 applied, 0 rejected, 2 left to the user (V:124–127).
- "The rounds ended after the second on the user's instruction, so they did not run until a round found nothing. The second round still found defects of substance, which is a reason to expect that some remain." (V:129)
- The three findings left to the user were decided afterwards. Each decision changes something the design record states, "and the design record is kept as it was written. Where the two differ, the guides and the code follow the decisions" (V:139). The decisions: the map of a research that ends with the root refuted (V:141); the removal of snapshots of Lean's state after import, so that every compile loads its imports in full, 9.7 seconds where a compile started from a snapshot took 2.8, for a file importing the Lean metaprogramming library (V:143); the rule for replacing the proof of a settled statement (V:145).
- The guides were revised after that. The check was a comparison with the committed text in three parts (V:172–176): seven comparisons by a reader on a different model, six of which found seventeen points, all repaired (V:174); a script comparison of the shared references in which 88 sentences no longer occurred word for word, 82 were traced and one was restored (V:175); more than twenty statements that disagreed with the code were corrected (V:176).
- Not checked for that revision: "The revised packs were not read from the beginning by an independent reader, as the guides before them were, and no session has worked from them." The comparisons "do not show how a session works with the new arrangement" (V:178). (The research of 1.5 started later; the document does not return to this sentence `[inferred]`.)

### 1.9 The test modules: what was run, when, with what result

The document describes a sequence of changes to the runtime and says which modules were run after each. No run of the whole suite is recorded after the first of these changes (V:15, V:47). The sequence:

| Step | Change | Modules run afterwards, and result | Source |
|---|---|---|---|
| a | (start) the last run of the whole suite; in two runs under heavy load one test of `test_research` ended in an error | — | V:45 |
| b | `init` now waits until the broker it started has ended | the failing test passed three times in a row; `test_research`, `test_pipeline`, `test_availability`, `test_context` passed. "The other twelve modules were last run before this change." | V:45 |
| c | the three decisions (map, rule for a settled statement's proof, snapshot removal last) | after the snapshot removal: `test_lean_broker`, `test_pipeline`, `test_resilience`, `test_availability`, `test_canon`, `test_cli_adapter`, `test_containment` passed. `test_publication`, `test_research`, `test_questions` last passed after the rule and before the snapshot removal; `test_depmap` after the change to the map. `test_context`, `test_ending`, `test_retention`, `test_views` last run before all three. The user ended that run. | V:47 |
| d | a change to the paper command | `test_paper` passed | V:47 |
| e | the revision of the guides, which changed `context.py`, `paper.py`, `test_context`, `test_paper` | "No test was run after it, on the user's instruction for that work." | V:47, V:178 |
| f | two more changes to the paper command | the 35 tests `test_paper` then held passed | V:47, V:102 |
| g | the bound on readings beside real papers raised to eight; one test added | the 36 tests of `test_paper` passed | V:47, V:114 |
| h | the judge of formal proofs added | `test_judge` passed; ten of the twelve other modules run passed: `test_canon`, `test_views`, `test_questions`, `test_pipeline`, `test_resilience`, `test_availability`, `test_context`, `test_depmap`, `test_ending`, `test_retention` (V:202). `test_publication` had two failures (a new key in `provenance.json`; repaired; the two tests pass when run by name). `test_research` had seventeen errors and two failures, each saying an empty folder of the test instance was missing; the run was made while several heavy runs were going on; four of the nineteen pass by name; "The cause was not found. Neither module was run again as a whole; the user ended the work before that." (V:204) | V:202, V:204 |
| i | the four changes of the first day of the Mathlib research; five test modules added | the five new modules (43 tests) passed, and were run once more on the files as committed (V:243). `test_lean_broker` passed as a whole, 76 tests, after the last change; in an earlier run of thirteen of its tests one test failed once and passed when run by itself (V:244). `test_judge` passed after the first change, with the two tests of `test_research` whose names contain `Initialize` (V:245). `test_questions`, `test_availability`, `test_views`, `test_ending`, `test_pipeline` passed after the third change (V:246). | V:243–246 |
| j | the repairs after a reading of the whole skill | on 23 November 2026, on a machine also carrying two research instances, run one after another, all passed in their last run: `test_paper` 39 tests in 606 s, `test_ending` 30 in 114 s, `test_judge` 20 in 159 s, `test_canon` 223 in 129 s, `test_publication` 52 in 528 s, `test_research` 108 in 468 s, `test_pipeline` 1 in 72 s (V:274–284). `test_ending` failed at first in one test because three new resume texts had Windows line endings in the working tree; they were converted and the module passed (V:287). "The other modules of both copies were not run after these changes." (V:287) | V:274–287 |

Modules not run after step h: `test_lean_broker`, `test_paper`, `test_cli_adapter`, `test_containment` `[inferred: the seventeen modules of that time less `test_judge` and the twelve named in V:202 and V:204]`.

What the document says was not run after step i: `test_research` and `test_publication` not as wholes; `test_canon`, `test_context`, `test_resilience`, `test_retention`, `test_containment`, `test_cli_adapter`, `test_depmap`, `test_paper` not at all; `test_judge` not after the second, third and fourth change (V:252).

The last recorded run of each module, put together from the rows above `[inferred from V:45, V:47, V:202, V:243–246, V:252, V:274–287]`:

| Module | Last recorded run | Result | Not run after |
|---|---|---|---|
| `test_paper`, `test_ending`, `test_judge`, `test_canon`, `test_publication`, `test_research`, `test_pipeline` | step j, 23 November 2026 | passed | — |
| `test_lean_broker` | step i, after the last of the four changes | passed (76) | step j |
| `test_waiting`, `test_state_save`, `test_cached_reads`, `test_sampling`, `test_baseline_estimate` | step i | passed (43 together) | step j |
| `test_questions`, `test_availability`, `test_views` | step i, after the third of the four changes | passed | the fourth change of step i; step j |
| `test_context`, `test_resilience`, `test_retention`, `test_depmap` | step h | passed | steps i, j |
| `test_cli_adapter`, `test_containment` | step c | passed | steps d to j |

No module is described as never run. What the document describes as never run are particular runs: the whole suite after step a (V:15, V:47); and the runs listed in 1.11.

The older copy `.agents/skills/do-math`: its three added modules (25 tests) passed and its `test_lean_broker` passed as a whole (74 tests) after the changes of step i (V:247); its `test_ending` (30 tests, 95 s) passed on 23 November 2026 after it was started from its `tests` folder, since that copy's tests import one another by bare name (V:285, V:287).

### 1.10 Real sessions and real Lean, against stand-ins only

| What | Real AI sessions | Real Lean | Source |
|---|---|---|---|
| The small research (sum of odd numbers), six sessions on `claude/opus` | yes | yes, Lean 4.32.0 `[inferred: V:55 gives 4.32.0 for the section before; V:63 says only "the real compiler"]` | V:63–72 |
| The paper command on that instance, four runs (see topic 5) | yes | not involved | V:82–112 |
| `depmap.py` on that instance, when the canon held four elements | none needed | not involved | V:80 |
| The Mathlib research since 22 November 2026 | yes | yes, Lean 4.36.0 and Mathlib 4.36.0 | V:217 |
| The scripted research of `test_pipeline` against the real compiler | no, scripted | yes, Lean 4.32.0 | V:55–57 |
| The judge cases of 1.6 | no | yes, Lean 4.36.0 on Windows | V:190–200 |
| The whole test suite | no, scripted programs | no, a stand-in | V:49 |
| The judge inside the tests | no | no; the exporter and the comparator are stand-ins | V:34, V:202 |
| The paper command inside the tests | no, stand-in sessions and a stand-in collection | — | V:102 |

### 1.11 What the document says no run has shown

- The tests "do not show that the real compiler gives those outputs", and the Lean program that extracts the structural index "is exercised only by the runs with the real compiler" (V:49).
- No real session has followed the guides along the paths of the formalizer, the organizer, the replacement peer, a declined replacement, a comprehensive review or a refutation, as of the small research (V:74). The later Mathlib research did meet replaced reviews and one replacement peer (V:264, V:265); the document records nothing about a formalizer, an organizer, a comprehensive review or a refutation in it `[inferred]`.
- The layout of the dependency map was not tested on a real canon of any size: the real map had two units (V:80).
- No run of the paper command with real sessions was made with the bound of eight readings (V:114), and no run showed the readings beside real papers ending with two in succession that find nothing (V:110).
- `judge.py` "was not carried to a verdict on a real instance" (V:208). The automatic judging of the root "has not been run" (V:298).
- Nothing was judged at the scale of a research that imports Mathlib, as of the judge's section; the judge's job for two small theorems reached 1.2 GB (V:209). (Seven judge jobs of publications were later recorded in the Mathlib instance, V:296.)
- A root proved through another declaration and a refuted root were not judged for real (V:212).
- No real session has met a rejection by the judge (V:211).
- No review or organizer launched under the new launch policy had ended when the section was written, "so the resumption has not been seen at work in a real session" (V:289).
- The baseline estimates were compared with measurements "on two libraries, on one machine, under Windows", and observed "for a few hours" (V:253, V:254). What a too-low estimate does to the admission of compiles over a long research was not observed (V:254).
- The quantities that decide the cost of a research at Mathlib scale "have still not been measured": how long the import takes in each compile, how often a replaced proof changes the public output of its module, how long a publication waits for its build, and how many publications an hour the single publication queue carries (V:302).

### 1.12 The limits named, the operating system and the judge's sandbox

- Every run whose operating system the document names is on Windows: the judge cases (V:190), the baseline comparison (V:253), the commit-charge figures (V:57). The document records no run on Linux `[inferred from the absence of any]`.
- The comparator's sandbox "needs Linux namespaces. do-math hands it exports of modules that its own broker compiled, and on Windows it switches the sandbox off. The verdict therefore rests on those builds having been made honestly. It does not rest on the index, the views or anything a session reported." (V:210)
- The judge runs at publication and not when a peer prepares its candidate, so a rejection costs a replacement peer (V:211).
- On Windows the page file bounds how many compiles run at once, since a Lean process is charged for the whole size of the library files it maps; the change is the user's to make (V:302).
- The redesign changed only the canonical skill. The copy `.agents/skills/do-math` was not regenerated, by the user's decision, because a running research instance uses it; three of the changes of 1.5 and one of the later repairs were made in it by hand; "The two now differ by a whole generation." The new runtime refuses an instance not created by it, so the copy is to be regenerated when that research has ended (V:306, V:270).

## 2. The test suite

**Location and command.** The suite is `runtime/tests/` in the skill. "Each module is run by itself, from the `runtime` folder, with `python -m unittest tests.<module>`." (V:23) No source gives a command that runs the whole suite at once.

**Modules and counts.** The folder holds 22 files named `test_*.py` and five other Python files: `canon_lean.py`, `fake_lake.py`, `fake_lean.py`, `pipeline_cli.py`, `support.py` `[listing]`. The counts below are occurrences of a line beginning with `def test_` (after indentation) in each file `[counted]`; nothing was run.

| Module | `def test_` `[counted]` | Count in the table at V:27–41 | Count in the table of 23 November at V:278–284 | What it covers, by V |
|---|---|---|---|---|
| `test_canon` | 223 | 221 (V:27) | 223 | names and paths, record and approach formats, applying a candidate, the structural index, the axioms a proof depends on, the machine checks of a candidate (V:27) |
| `test_research` | 108 | 108 (V:28) | 108 | standing, settlement, contested and refuted statements, the frontier, which proofs go to a formalizer, coordination, the runner's scheduling (V:28) |
| `test_publication` | 52 | 52 (V:29) | 52 | a publication from candidate to commit, a runner that ends at each of eight points of a publication and is followed by one that completes it, the replacement peer, the organizer, the transport checks (V:29) |
| `test_questions` | 51 | 51 (V:30) | — | questions, their understanding texts, merges, the operator's publication of questions (V:30) |
| `test_views` | 26 | 26 (V:31) | — | the derived views and every reading command (V:31) |
| `test_lean_broker` | 76 | 76 (V:32) | — | the broker: scheduling, the module cache and its key, recovery (V:32) |
| `test_paper` | 39 | 36 (V:33) | 39 | the paper command (V:33) |
| `test_judge` | 20 | 19 (V:34) | 20 | the judge, with stand-ins for the exporter and the comparator (V:34) |
| `test_depmap` | 21 | 21 (V:35) | — | the dependency map; one test, of the optional ELK layout, is skipped because `elkjs` is not installed (V:35) |
| `test_context` | 14 | 102 together for these eight (V:36) | — | what a session receives at launch (V:36) |
| `test_ending` | 30 | | 30 | ending and resumption (V:36) |
| `test_resilience` | 11 | | — | recovery from failures (V:36) |
| `test_retention` | 13 | | — | retention of session work (V:36) |
| `test_containment` | 7 | | — | process containment (V:36) |
| `test_cli_adapter` | 8 | | — | the CLI adapters (V:36) |
| `test_availability` | 20 | | — | the report that all work is occupied (V:36) |
| `test_pipeline` | 1 | | 1 | one scripted research from start to formal root (V:36) |
| `test_waiting` | 11 | 11 (V:37) | — | a command that waits for a broker job (V:37) |
| `test_state_save` | 8 | 8 (V:38) | — | the writer that saves the broker's state (V:38) |
| `test_cached_reads` | 7 | 7 (V:39) | — | reading a file again only when it has changed (V:39) |
| `test_sampling` | 4 | 4 (V:40) | — | the broker's listing of processes and reading of memory (V:40) |
| `test_baseline_estimate` | 13 | 13 (V:41) | — | baselines estimated from the size of what imports load (V:41) |
| **Total** | **763** | **755** (V:43) | | |

The eight modules of V:36 sum to 104 by my count against the document's 102. `support.py` holds one further `def test_settings`, which is a fixture and not a test (tests/support.py:111; tests/test_research.py:25 renames it "so that no loader takes it for a test"). The differences are recorded in Part 4.

**What stands in for real AI sessions and real Lean.**

- "The tests do not run Lean. A stand-in program, `tests/canon_lean.py`, takes the compiler's place: it reads a small subset of Lean and prints the rows that the index extraction prints. Scripted programs take the place of the AI sessions." (V:49)
- `canon_lean.py` "compiles" a module by parsing its declarations and writing the four files Lean 4.32 emits; it also plays the exporter and the comparator of the judge (tests/canon_lean.py:1–18).
- `fake_lean.py` is a second stand-in for `lean` with a controllable memory and time profile; "nothing is elaborated" (tests/fake_lean.py:1–19). `fake_lake.py` stands in for `lake env <command>` (tests/fake_lake.py:1–5). `test_lean_broker.py` uses both (tests/test_lean_broker.py:20, :1602).
- `pipeline_cli.py` holds the scripted session outputs; the Lean it writes is valid Lean 4, so the same script runs against the stand-in in the unit tests and against the real compiler "when the pipeline is tried end to end" (tests/pipeline_cli.py:1–5). `test_pipeline` starts it in the place of a CLI (tests/test_pipeline.py:33).
- The shared fixture creates a small instance through the real `initialize`, which builds the canon through a real broker with `canon_lean.py` as its compiler (tests/support.py:1–6). Its settings attach no external tools: "the tests do not depend on the literature server being installed" (tests/support.py:113).
- `test_paper` runs no AI session and no TeX; the test file itself plays the session and the TeX command (tests/test_paper.py:1–9), and it uses a stand-in collection of papers (V:102).
- The tests use real Git `[inferred from the import of `git` from `runtime_support` in tests/test_pipeline.py:12, tests/test_publication.py:22 and tests/test_questions.py:24]`.

**What the stand-ins mean for the evidence.** "The tests therefore show that the runtime does what it should with the outputs it is given. They do not show that the real compiler gives those outputs." (V:49) The difference has hidden two defects (see 1.7).

## 3. The Lean broker

**What it is.** Each instance runs a single process called the Lean broker, and every compile in the instance goes through it. A session does not run Lean itself, not even to ask for its version (LEAN:31). The broker is the `serve` command of `lean_broker.py`, run as a detached process; a lock file ensures there are never two brokers for one instance (LB:67). It compiles one file per job with the `lean` command of the instance's settings and does not run `lake build`; its own `build` command does for a session what `lake build` would (LEAN:45).

**Why all compilation goes through it.**

- Memory is the reason. A compile that takes more memory than the machine has left pushes the machine into swapping or gets a process killed, and every session suffers (LEAN:15). Private memory is paid once per running compile, and no session can keep the sum over all running compiles in bounds by itself (LEAN:23).
- On Windows a Lean process is charged against the commit limit for the whole size of the library it maps: with Lean 4.32.0, a process importing the Lean metaprogramming library was measured at a commit charge of 2,078 MB while it touched 803 MB of physical memory (LEAN:19, LB:29). A compile importing the analysis part of Mathlib was measured between 2 and 3.9 GB before it elaborated anything (LEAN:21).
- Because the broker sees every compile, it schedules against a shared budget, measures every compile, keeps a compile alive independently of the session's shell tool, cancels the compiles of sessions that have ended, and keeps what compiles produce (LEAN:33–43).
- What a compile costs a session on Windows is mostly the wait: in the research instance examined before the canon was introduced, 481 finished compiles ran for a median of 24 seconds and waited for a median of 179 seconds (LEAN:25).

**How it admits compiles.** The broker has no limit on the number of compiles running at once. It has a memory budget and a thread budget, and it starts the next compile when both have room and the machine itself has the memory free (LB:11).

- *The memory rule.* For each running compile and the candidate, the broker forms a reservation of three numbers: a certain part (the baseline of the compile's imports, replaced by the measured memory once that has grown past the baseline), an expected excess, and a spread (LB:13). A compile can start when the sum of certain parts, plus the sum of expected excesses, plus `confidence` times the square root of the sum of squared spreads, is at most `memory_budget_mb` (LB:17–21). The session's estimate is read as a ninetieth percentile (LB:13, LEAN:165). The spreads are pooled under a square root on an approximation of independence; the document says "this approximation is not a guarantee that simultaneous peaks will be avoided" and that these "are scheduling estimates, not measured guarantees of overflow probability" (LB:23). The rule is the equivalent-capacity admission control used in communication networks (LB:23).
- *The thread budget.* Each compile reserves `lean.threads` threads (default 2); the default budget is twice the number of logical cores (LB:25, LB:50–51).
- *The machine gate.* Whatever the budgets say, a compile starts only if the machine's actual free memory (`MemAvailable` on Linux, the commit headroom on Windows) would remain above `min_free_memory_mb` (default 2048) after the compile's certain part is taken; the gate also counts as taken what running compiles are certain to take and have not yet reached (LB:27, LB:49).
- *The order.* Queued compiles are considered in the order submitted and the first that fits starts; a compile that does not fit is passed over, at most `max_passes` times (three by default), after which nothing behind it starts until it has. This bounds the number of compiles that can pass it and not the waiting time. When no compile is running, one eligible compile may exceed the memory or thread budget; the machine gate still applies (LB:31).
- *Baselines.* The baseline of a set of external imports is the private memory a compile uses to load them (LB:7). The broker measures the first sets with a compile of only the `import` lines; once five sets have been measured in the current environment and launch mode, a new set whose size on disk lies between two measured sizes receives an estimated baseline and no compile (LB:33, LB:35).
- *Defaults.* `memory_budget_mb` defaults to the machine's physical memory minus `min_free_memory_mb` minus 512 MiB for each of `max_sessions`, at least 1024; `confidence` 1.3; `priority` `below_normal` (LB:47–52). When several instances run on one machine each derived budget assumes the whole machine, so the operator sets each instance's share explicitly (LB:63).
- *Windows.* On the development machine, with 15.9 GB of memory and a commit limit of 25.2 GB, about 3.4 GB of headroom was left while sixteen sessions ran, and compiles ran one at a time although physical memory was free. Enlarging the page file raises the commit limit; that is a setting of the user's machine, to be recommended and not changed by the operator (LB:29, OPS:228–230). "The effect on compiles that import Mathlib has not been measured." (OPS:230)

**What stops a compile.** A compile is cancelled when the session that submitted it has ended, or on a `cancel` request. "Nothing else stops a compile; there is no time limit and no memory limit on one that is running." (LB:37; LEAN:41)

**What it keeps and returns.**

- It measures the private memory of the compile's whole process tree four times a second and keeps the peak (LB:39). The command prints Lean's output exactly as Lean produced it and exits with Lean's exit code; a summary line gives the job, status, exit code, peak, baseline, excess, seconds and the ratio of peak to estimate (LEAN:63–71).
- A job continues and keeps its result whatever happens to the command that submitted it; `submit` and `wait` let a session come back for it (LEAN:39, LEAN:81–88).
- It keeps a calibration table, `runner/lean/calibration.json`, with one entry for each set of external imports, Lean environment and launch mode (LB:33).
- It keeps a cache of compiled modules. A module the broker compiled with exit code 0 is kept under a key made of the environment identity, the module's name, its source bytes and the compiled output of every local module the compile reads; a later build by any session that needs a module with the same key takes it from there (LB:79, LB:81). Because the key is made of content and not of paths, a session can build its own files in a copy of the canon without compiling the canon again (LB:87).
- It keeps files and never a loaded Lean process (LEAN:43).
- Its state is under `runner/lean/` in the instance, outside the instance's Git (LB:67).

**How it lives and recovers.** The runner starts a broker when it starts and another on any later tick where it finds none alive; the runner never stops a broker, and the runner's exit does not end it (LB:69). Each compile is supervised by a small process, the job host, so that when a broker dies in the middle of a compile nothing is lost: the next broker follows the jobs still alive and requeues those whose Lean had not started; a job whose host disappeared without an exit record is marked failed and "never silently run again" (LB:71). A session contained in a job, as on Windows, does not start a broker (LB:69). When `lean.command` is `lake env lean …`, the broker runs `lake env` once and from then on runs `lean` itself in that environment, which on the machine measured saved about a gigabyte of committed memory and a few seconds per compile (LB:73).

**What `lean.md` asks of the Lean that sessions write** (LEAN:186–208). The document presents these as "what experienced Mathlib users do as a matter of course", each with its reason (LEAN:188):

- Import only what is used. In one instance files importing the real numbers, finite sums and four tactics each from its own module had a baseline of about 2,200 MiB, and their proofs added less than 70 MiB; a file with `import Mathlib.Tactic` and three small imports had about 3,900 MiB (LEAN:190, LEAN:192). An import is inherited by every module that reaches the importing module (LEAN:194).
- Compile fewer times and compile less each time: first compile the statements together with proofs left as `sorry` (LEAN:198).
- Keep what is still changing apart from what has stopped changing; write files as `module` files (LEAN:200).
- Turn successful searches (`exact?`, `simp?` and the like) into explicit proofs (LEAN:202).
- Keep automation bounded: `simp only`, `linarith only`, `norm_num` and not `decide` for arithmetic; under the default axiom policy `native_decide` introduces an axiom that is not allowed (LEAN:204).
- Measure before optimizing (LEAN:206), and shape the file for how Lean runs it (LEAN:208).
- Every submission carries the session's estimate of the compile's peak private memory, meant as a probable peak and not a worst case (LEAN:163–165).

**When a statement counts as formal** (LEAN:210–228). A successful compile shows only that Lean accepts the file (LEAN:212). A statement is formal when every axiom it depends on, followed through everything of the canon it uses and the imported library, is in the instance's allowed list. By default the list holds `propext`, `Classical.choice` and `Quot.sound`; `sorryAx` is never allowed (LEAN:214). Review does not rest a formal verdict on the peer's build: it runs `commands.verify`, which compiles the changed modules afresh in the reviewing session's name and prints the axioms (LEAN:220). What Lean cannot settle is whether a statement or a definition says what was meant; that is review's judgment (LEAN:226).

## 4. The judge of formal proofs

**What it checks.** do-math takes a statement for formal from its structural index, which is computed inside a Lean process that has loaded the modules it describes. "The judge checks the same thing from outside." (OPS:409)

**With which tools.** Lean's exporter, `leanexport`, writes a theorem out together with everything it rests on, and `lake comparator` reads that export alone: it works out the axioms again, compares the export with a second one, and replays every declaration through the kernel. Both programs come with Lean 4.35 and later (OPS:409). The setting `lean.judge` is `"auto"` by default; with an earlier Lean there is no judge and `status` says so; `null` switches the judge off; a judge that is configured and cannot run makes `init` refuse (OPS:220). No session runs the judge (LEAN:222).

**The two moments.**

1. *At a publication* (OPS:411). Before a change is installed, the runner has the judge look at the theorems whose formal proof the change brings: those whose proof it adds or replaces and that are formal afterwards, and those that are formal only now because the last statement they rest on has received a formal proof. Here the export is compared with itself, "which leaves the axioms and the kernel". If the judge rejects, the change is not published and goes to a replacement peer with the judge's reason. If the judge cannot run, "nothing has been learned about the change": the runner makes the build once more and, if the judge still cannot run, ends with the reason in `last_error`. `init` has the formal theorems of the starting canon judged in the same way and refuses a canon the judge rejects.
2. *At the end* (OPS:413). `python <skill>/runtime/judge.py <instance> --out <new folder>` judges the root of an instance whose root is formally proved or refuted, against the root as the instance's first commit fixed it. It builds the canon of the first commit and the canon as it stands, each with one added theorem that states the root (or its negation), proved by the proof which settles the root. The judge accepts when the two statements are identical together with every definition they depend on, the axioms lie within `allowed_axioms`, and the proof is accepted by Lean's kernel and by the other kernels that Lean ships; `--no-paranoid` leaves those other kernels out. The runner starts this command itself, once for each proof through which the root becomes formally settled and once more before it finishes if the library has changed since; `status` gives the result under `root_judge` as `running`, `accepted`, `rejected` or `unavailable` (OPS:415). Exit codes: 0 accepted; 1 refused or could not run, which "says nothing about the proof"; 2 rejected, with a request for a comprehensive review written to the instance (OPS:417–421).

The purpose of the second moment is that "the statement proved is shown to be the statement posed, with every definition it depends on unchanged" (V:188; LEAN:222).

**What the verdict rests on, and what it does not.** `lake comparator` can build what it judges inside a sandbox, which needs Linux namespaces. do-math always hands it exports of modules that its own broker compiled, so that sandbox does not cover the builds, and where it cannot run at all, as on Windows, the commands carry the option that switches it off. "The verdict therefore rests on those builds having been made honestly: Lean code that a session wrote runs when it is compiled, as at every compile of the instance. What the verdict does not rest on is the structural index, the views, or anything a session reported." (OPS:425; the same in V:210)

**What has been run of it.** See 1.6 and 1.11: accepted and rejected cases by hand and through one publication on Lean 4.36.0 and Windows (V:194–200); seven judge jobs of publications in the Mathlib instance, all with code 0 (V:296); `judge.py` not carried to a verdict on a real instance (V:208); the automatic judging of the root not run (V:298).

## 5. The paper command and the dependency map

### The dependency map

- Command: `python <skill>/runtime/depmap.py <instance> --out <folder>`. It draws the map from the canon as it stands. "It can be run at any time, including while the instance runs, and it writes nothing into the instance. The command needs only Python." (OPS:376)
- It shows the elements whose record gives `weight: unit` and that the proof of the root rests on, grouped by the folder of their module; `--all` shows every unit; the steps are folded into the lines (OPS:378). When the research ended with the root refuted, the map shows the refutation (OPS:378; V:141).
- It writes three files: `dependency_map.svg`, `dependency_map.html` (the drawing for a browser, with clicks that narrow it and a panel with the unit's statement) and `dependency_map.json`, from which the map can be drawn again without the instance (OPS:380).
- Layout: `layered` is computed in Python; `elk` needs Node and the `elkjs` package, whose installation is the user's choice; `auto`, the default, uses ELK when installed and falls back to the Python layout (OPS:382). Exit code 0 on success, 2 on the failures listed (OPS:384).
- Verified by: one real run when the canon held four elements, two of them units joined by one line. "A map this small shows that the command runs on a real canon. It does not test the layout, which the tests exercise on larger canons made by hand." (V:80)

### The paper command

- Command: `python <skill>/runtime/paper.py <instance> --out <new folder>`. It writes the paper that presents the result, as LaTeX and a typeset PDF (OPS:388).
- **When it can run.** Only when the root is settled by a formal proof, that is, when the root's state is `formal_proved` or `formal_refuted`; otherwise it refuses and writes nothing. Once started it runs to the end without asking anything (OPS:388).
- **A precondition the command does not check.** The choices of the paper method are the user's: "before the first paper of an instance's user is produced, ask the user to read and confirm the document, and do not run the command until they have" (OPS:390).
- **How the paper is written.** The command takes from the canon everything the formal proof of the root rests on, and nothing else: results the proof does not use, abandoned approaches and open questions are not in the paper (OPS:390; PM:21). One session plans the paper and one session for each section writes it; both read real mathematical papers first and write as those are written (OPS:390). The planning session chooses six papers of the collection and leaves an account of how they are written as `study.md` (OPS:392; PM:156, PM:164). An element whose weight is unit becomes a numbered statement, and an element whose weight is step is absorbed into the proof that uses it (PM:57). One numbered statement states one element, and every numbered statement states an element (PM:65). The paper cites only works in the canon's bibliography and does not say that a result is new (PM:118, PM:120). The paper stands in natural language and does not mention Lean, a proof assistant or a formal proof anywhere (PM:128; OPS:390). An account of the formal verification is a separate document; it "has not been written, and no command produces it" (V:100). The manuscript names no author; who signs the paper is the user's decision (PM:51; OPS:400).
- **How it is checked**, in this order (OPS:390; PM:201–215):
  1. Machine checks and typesetting: every numbered statement is one the plan names; references and citations resolve; no Lean name of the canon and neither of the words Lean and Mathlib appears; then TeX typesets the manuscript. Failures go to a repair session (PM:205).
  2. A reading by a session that has the manuscript and the description of the reader and nothing else (PM:207). At each point it is read at most three times, with a repair after the first and the second and none after the third (OPS:402).
  3. Readings beside real papers: each such session has the manuscript and four papers of the collection that the plan did not choose, and reports every place where a mathematician would notice that the manuscript is written otherwise, with passages of at least two papers as evidence. A repair follows each report. These readings end when two in succession report no departure, and there are at most eight of them (OPS:392; PM:209; V:96, V:114). The script checks only the shape of a report and not that a quoted passage stands in the paper named (V:96).
  4. If a repair after a reading beside real papers changed the text, the reading of step 2 is made again (PM:211).
  5. Every numbered statement is compared with the statement of its element by a session whose only task is this; a difference goes to a repair, and no repair follows the last comparison (PM:112, PM:213). A correspondence file beside the paper gives, for each numbered statement, the record's statement, the Lean statement and the paper's statement (PM:112; OPS:396).
- Each loop is bounded, and what is still open at the end is reported: "the user confirms the result by reading them" (PM:215).
- **Models.** Planning, writing and repair use the first entry of the instance's `models`; the readings and the comparison use the first model of the `review` role, "so that by default a different model reads than wrote". The sessions receive no MCP servers (OPS:394).
- **What it produces.** `paper.tex`, `references.bib`, `paper.pdf`, `plan.json`, `study.md`, `materials.md`, `correspondence.json`, `log.json`, and working material (OPS:396).
- **Exit codes** (OPS:398–403): 0 the paper is complete; 1 the command refused or failed; 2 the manuscript was produced and findings stayed open after the bounded repairs; 3 the manuscript is complete and no TeX command was found, to be typeset later with `--typeset-only`.
- **TeX.** A TeX command is `tectonic`, `latexmk` or `pdflatex` on PATH, or the command given after `--tex`. Installing a TeX distribution needs the user's approval (OPS:405). In the recorded runs Tectonic 0.15.0 was used from a local folder outside version control, not on the PATH (V:84).

### The collection of real papers

- The folder `<skill>/exemplars` holds published research papers in mathematics, each as one LaTeX file; "they are read for how a paper is built and worded, and their mathematics is not used" (.claude/skills/do-math/exemplars/README.md:3). The paper does not cite them (V:96).
- 32 research papers; each an arXiv paper that a journal published between 2008 and 2023, 4 to 45 pages long, from combinatorics, number theory, probability, algebra, analysis, and geometry and topology (V:96).
- `manifest.json` lists each paper with arXiv identifier, title, authors, journal reference, field, pages, licence, abstract, the SHA-256 of the `.tex` file and one sentence on what makes it a good model (.claude/skills/do-math/exemplars/README.md:5).
- **Why the papers are not in Git.** "The copies themselves stay on the machine and are not committed, because only one of the 32 papers carries a licence that allows others to redistribute it." (V:98) The operating guide says "most of them may not be passed on" (OPS:392). The folder's `.gitignore` holds the single pattern `*.tex`, and Git tracks `.gitignore`, `README.md`, `fetch.py` and `manifest.json` there `[listing]`. In `manifest.json` the `licence` field reads `CC BY 4.0` once, `arXiv non-exclusive licence to distribute 1.0` 27 times and `not stated in the arXiv record` 4 times `[counted]`.
- `python fetch.py` downloads the source of every paper that is missing or differs from the manifest, joins it into one file, leaves out what the authors commented out, and checks its SHA-256; it needs only the Python standard library and waits three and a half seconds between requests to arXiv (.claude/skills/do-math/exemplars/README.md:7–13).
- The paper command checks the collection before it launches a session. If a paper is missing or differs, it runs `fetch.py` once, "which needs the network"; if a paper is still missing after that, the command stops and names it (OPS:392).

### The runs of the paper command recorded in the verification document

All on the instance of the small research (V:78). There were four runs with real sessions: the document counts two before the two later changes to the command (V:82) and two after the first of them (V:102). The only run of the command with both changes in place is the fourth, and it is the only one of the last two that went to its end.

| Run | State of the command | Sessions, time | Outcome | Source |
|---|---|---|---|---|
| 1 | before any change; the machine had no TeX | eight sessions, 591 s | exit code 3, manuscript left without a PDF | V:82 |
| 2 | with three repairs found at the first typesetting | eight sessions, 780 s | exit code 0; `paper.pdf` of three pages | V:90 |
| 3 | with the collection of real papers; before Lean was taken out of the paper | ten sessions, 1,792 s | stopped by hand during a repair; two readings beside real papers reported ten and eight departures | V:104 |
| 4 | with both changes; bound of four readings beside real papers | fifteen sessions, 2,651 s | exit code 2; `paper.pdf` left | V:106 |

The first typesetting of run 1's manuscript, with Tectonic 0.15.0, reported no TeX error and showed three defects that no check had been able to see: the running head capitalised the variable n, the character `^` came out as an accent, and one displayed formula was 69 points wider than the text block. All three were repaired (V:84–88).

What run 4 produced (V:106–112):

- One session planned the paper and two wrote its sections; two read the manuscript alone, each followed by a repair; four read it beside real papers, the first three followed by a repair; one compared the numbered statement with the statement of its element and found them the same. The manuscript was assembled six times; each time it passed the machine checks and TeX typeset it without an error and without a line too wide (V:106).
- The paper is one page long. It has an abstract, an introduction that defines the sum and states the theorem, and a proof by induction. "It mentions Lean nowhere." The page shows no defect of typesetting (V:108).
- The readings beside real papers did not reach the condition that ends them and stopped at the bound of four. They reported ten, six, six and five departures; the five of the fourth reading are the open findings (V:110).
- Four of those five "come from what this instance is": its proposition is a classical identity with a proof of a few lines and its canon holds no bibliography entry, "so the paper has nothing new to announce and no source that it is allowed to cite" (V:110).
- "So this run shows that the readings find such differences and that the repairs remove what a repair can remove ... It does not show the readings ending with two in succession that find nothing. Seeing that needs a research whose result is its own and whose canon holds its sources." (V:110)
- A departure in the title is one the repairs cannot act on, because the title belongs to the plan (V:112).

After run 4: the bound was raised from four readings to eight, with one new test, and "No run with real sessions has been made with the bound of eight" (V:114). A later repair changed the command again: the manuscript is read by itself again after a repair that followed a reading beside real papers or a comparison, no repair follows the last reading at each point, and `READING_ROUNDS` went from 2 to 3 (V:268); `test_paper`, 39 tests, passed after it (V:278). No run with real sessions is recorded after that repair `[inferred]`.

## 6. The four programs under `services/`

All four READMEs are in Korean.

- **scholarly-mcp** — A local MCP (Model Context Protocol) server that searches academic sources and obtains bibliographic data, abstracts, full texts and supplementary material, keeping the files locally; a client calls five tools (services/scholarly-mcp/README.md:3; the tools are `list_sources`, `describe_source`, `search`, `extract`, `fetch`, services/scholarly-mcp/README.md:66–70).
  - *Number of sources.* 49 sources are registered. 48 are marked `partial` (part of the source's functions supported) and Unpaywall is `deferred` (its use is put off) (services/scholarly-mcp/README.md:15; services/scholarly-mcp/docs/SUPPORT.md:1, :23). A request to a deferred source is refused (services/scholarly-mcp/server.py:105–106). Two of the 49, `society-journal` and `author-repository`, list no `search` function (services/scholarly-mcp/docs/SUPPORT.md:50–51).
  - *Which need no login.* The sources use public APIs, the public web, or the institutional access of Kyungpook National University (KUDOS), source by source; public sources need no KUDOS credential, and without institutional credentials an institutional access returns `restricted` (services/scholarly-mcp/README.md:15, :52). The README does not list which sources are public.
  - *`--public-only`.* Started with this option, the server serves only the sources that use neither an institutional login nor a browser; it creates no login object and no browser; `list_sources` returns only those sources, and `describe_source`, `search` and `fetch` on any other source are refused with status `unsupported` and code `source_not_enabled` (services/scholarly-mcp/docs/USAGE.md:19; services/scholarly-mcp/server.py:55–56, :96–99, :150–152, :162–165). The option exists for environments that start several server processes at once: without it each process logs in to the institutional account separately (services/scholarly-mcp/docs/USAGE.md:19). The service's own README does not mention the option; its table of start options lists only `--data-dir` and `--credential-root` (services/scholarly-mcp/README.md:47–50).
  - *How many sources `--public-only` serves.* The operating guide says "about twenty sources that are reached through public interfaces, among them zbMATH, arXiv, Crossref, OpenAlex and Semantic Scholar", and that sessions "cannot search MathSciNet or retrieve full texts that require a subscription" (OPS:249). The code enables the adapters registered before the login gateways are created: fifteen classes (Crossref, Crossmark, Arxiv, DBLP, ZBMath, OpenAlex, SemanticScholar, OpenCitations, Numdam, CORE, Zenodo, GitHub, Mathlib, MathComp, SoftwareHeritage; services/scholarly-mcp/api_adapters.py:1335) and six more (`figshare`, `dblp-kg`, `afp`, `eudml`, `aps`, `general-web`; services/scholarly-mcp/server.py:156–161), which makes 21 `[inferred from the code; the server was not run]`.
  - *Relation to do-math.* The default settings of do-math attach this server to every instance, started with `--public-only` (OPS:236; SK:42; .claude/skills/do-math/runtime/settings.py:21–28). `init` writes the entry when the settings file has no `mcp_servers` key; `"mcp_servers": {}` creates an instance without external tools; `init` refuses when the `command` of a configured server is not found (OPS:247).
- **continuous-development** — A phase-based development system: a goal is divided into tasks, tasks that need not wait for one another are grouped into a phase, `run.py` runs the task sessions of a phase in parallel (each one `codex exec` call), and when all have ended a manager session reads the reports and writes the next phase or declares the development complete (services/continuous-development/README.md:3–5). It needs Python 3.10 or later and the Codex CLI and uses no external Python package (services/continuous-development/README.md:9).
- **async-development** — A system of the same kind without phases: each worker receives its own copy of the code, a manager reads each finished task, integrates accepted changes into the shared code and assigns the next tasks, while other tasks keep running (services/async-development/README.md:3–13). It needs Python and the Codex CLI (services/async-development/README.md:21).
- **jev-cli** — A command-line tool that sends material and questions to Jev, a model of TypeSafe, and returns choices, scores and probabilities of truth as JSON; it uses Python 3.10 or later with the standard library only and needs a TypeSafe API key (services/jev-cli/README.md:3–5, :31).

## 7. The skills other than do-math

Eleven folders stand beside `do-math` under `.claude/skills/` `[listing]`.

| Folder | What it does | Source |
|---|---|---|
| `commit-harness` | The procedure for commits and pushes in this repository, which puts exactly one memory node into every work commit and applies checks by changed area | .claude/skills/commit-harness/SKILL.md:3, :8, :14 |
| `dream-harness` | On the user's explicit request, combines accumulated memory nodes into insights and conventions and updates the current-state layer | .claude/skills/dream-harness/SKILL.md:3, :8 |
| `graphify` | A knowledge graph of the documents and scripts inside `.claude/skills/do-math/`, queried to find relations and the source of a contract or procedure | .claude/skills/graphify/SKILL.md:3, :8 |
| `grill-me` | A user-invoked command that runs a `/grilling` session | .claude/skills/grill-me/SKILL.md:3–7 |
| `grilling` | Interviews the user about a plan, decision or idea, one result-changing decision at a time, and summarises the agreed contract | .claude/skills/grilling/SKILL.md:3, :8, :14 |
| `memory-harness` | Defines the structure, invariants, node format, index and reading path of the three-layer working-memory graph | .claude/skills/memory-harness/SKILL.md:3, :8 |
| `simplify` | Four questions the agent puts to itself about whether it is doing a thing in the simplest way; user-invoked | .claude/skills/simplify/SKILL.md:4, :7–14 |
| `skill-creator` | Creates new local skills, improves, tests and benchmarks the project's own skills, and optimises a skill's description for triggering | .claude/skills/skill-creator/SKILL.md:3, :9 |
| `verify-rounds` | Runs parameterised rounds in which several agents find defects in a finished artifact and repair them: repair, merge, judging, application | .claude/skills/verify-rounds/SKILL.md:3, :8–15 |
| `write-for-reader` | Guides the design, writing and revision of standalone text that an AI or a person will act on, and the questioning that fixes missing user decisions | .claude/skills/write-for-reader/SKILL.md:3 |
| `writing-skills` | A reference on the principles of writing a skill's description, structure, naming and examples and on designing a skill's verification | .claude/skills/writing-skills/SKILL.md:3, :9 |

Two observations from the same files. The `description` of `simplify` is the placeholder `foo` (.claude/skills/simplify/SKILL.md:3). The example commands of `graphify` name files, `계약/연구-수행.md` and `scripts/do_math/contracts.py` (.claude/skills/graphify/SKILL.md:18–23), that the current `do-math` folder does not hold: it has no `계약/` and no `scripts/` folder `[listing]`. Whether the graph itself is current was not checked; that needs the tool to be run.

**Third-party notices.** `THIRD-PARTY-NOTICES.md` lists four directories as adapted from third-party projects (THIRD-PARTY-NOTICES.md:5–10):

| Directory | Upstream as the file names it | Licence | Source |
|---|---|---|---|
| `.claude/skills/skill-creator/` | `skill-creator` plugin in anthropics/claude-plugins-official | Apache License 2.0 | THIRD-PARTY-NOTICES.md:7 |
| `.claude/skills/writing-skills/` | `writing-skills` skill in obra/superpowers 6.1.0, Copyright (c) 2025 Jesse Vincent | MIT | THIRD-PARTY-NOTICES.md:8 |
| `.claude/skills/grilling/` | mattpocock/skills, Copyright (c) 2026 Matt Pocock | MIT | THIRD-PARTY-NOTICES.md:9 |
| `.claude/skills/grill-me/` | mattpocock/skills, Copyright (c) 2026 Matt Pocock | MIT | THIRD-PARTY-NOTICES.md:10 |

Every directory the file names exists `[listing]`: the four skill directories; the licence file each row links to (`skill-creator/LICENSE.txt`, `writing-skills/LICENSE`, `grilling/LICENSE`, `grill-me/LICENSE`), all four tracked by Git; `references/원본_대조.md` in both `skill-creator` and `writing-skills`, which the file says record the adaptation (THIRD-PARTY-NOTICES.md:14); and `.agents/skills/`, which holds a folder for each of the four (THIRD-PARTY-NOTICES.md:3). The file says the project as a whole is licensed under the GNU Affero General Public License v3.0 (THIRD-PARTY-NOTICES.md:3); that sentence is an uncommitted change from "Mozilla Public License 2.0" `[listing: git diff]`.

## 8. `CITATION.cff`

Fields whose content describes the previous implementation or the parking-function run:

| Field | Line | Content | Why it is listed |
|---|---|---|---|
| `message` | CITATION.cff:2 | "... To cite the published knowledge base of the first run, cite the Zenodo record listed under references." | names the first run and its Zenodo record |
| `abstract` | CITATION.cff:5 | "... Each piece of work is produced by one session, developed into a record by a second session, and assessed by a third; published records are immutable and carry their assessments. A root proposition counts as settled only when an independently recompiled Lean proof has been checked against the exact statement." | describes knowledge as records; see below |
| `keywords` | CITATION.cff:18–19 | "parking functions", "unimodality" | the subject of the parking-function run |
| `references` (the whole block) | CITATION.cff:20–31 | a `data` reference titled "parking-unimodality-2026-11-10", DOI 10.5281/zenodo.24110810, publisher Zenodo, with the note "Concept DOI for all versions of the published knowledge base of the first run. Version 3 is 10.5281/zenodo.24165415." | the knowledge base of the first run |

On the abstract `[inferred, by comparison with the current sources]`: its first sentence, that do-math "runs research on one mathematical proposition through many fresh AI sessions that share no conversation", agrees with the current skill (SK:14). The rest does not describe the current implementation. The knowledge is now a Lean library with a record beside each declaration (SK:10); the second session, the peer, writes a candidate change to that library (SK:16); a proof in the library can be replaced, while a statement never changes in place (LEAN:116); and the root is fixed in Lean at creation, so that "no separate comparison of a proved theorem with the proposition is made" (LEAN:224).

Fields that do not describe either: `cff-version`, `type`, `title`, `authors`, `repository-code`, `url`, `license`, and the keywords at CITATION.cff:14–17. `license: AGPL-3.0-only` (CITATION.cff:12) is an uncommitted change from `MPL-2.0` `[listing: git diff]`. The file has no `version` and no `date-released` field.

---

# Part 2. `README.md` lines 220 to 262 against the current state

Marks: `true`, `partly`, `false`, `gone`, `to be deleted`. Line 222 and several other lines hold more than one sentence; each sentence has its own row.

| Line | Item | Mark | What is wrong, and the current fact |
|---|---|---|---|
| 220 | Heading "Repository layout, verification and tests" | true | — |
| 222 (1) | "Within `.claude/skills/do-math/`, `SKILL.md` is the operator's entry point, `roles/` holds the six role guides, `reference/` the shared and specialist guides, `resume/` the texts delivered when a session is asked to reconsider ending, and `runtime/` the runner, the coordination tools, the Lean broker and their tests." | partly | What it says of `SKILL.md`, `roles/` (six files `[listing]`) and `reference/` holds (SK:8, SK:16). Three things are missing or too narrow. The folder `exemplars/` is not named (.claude/skills/do-math/exemplars/README.md:3). `resume/` also holds the texts with which the host resumes a review or an organizer whose turn ended with output that fails the transport check: `resume/output.md`, `resume/review.md`, `resume/organizer.md` (V:264). `runtime/` also holds the canon tool and the three commands `depmap.py`, `paper.py` and `judge.py` (OPS:376, OPS:388, OPS:413; `[listing]`). |
| 222 (2) | "`.agents/skills/do-math/` is the generated mirror for Codex." | partly | The folder exists and is called the generated copy (V:306). It does not mirror the current skill: it was not regenerated, by the user's decision, because a running research instance uses it; "The two now differ by a whole generation"; some changes were made in it by hand; it is to be regenerated when that research has ended (V:306, V:270, V:217). |
| 222 (3) | "The design and decision record of the current implementation is docs/do-math/rebuild-design.md." | false | The design record of the current implementation is `docs/do-math/lean-canon-design.md` (V:3; the file exists `[listing]`). It is kept as written, and the guides and the code depart from it where three later decisions and the revision of the guides say so (V:139, V:151, V:168). |
| 222 (4) | "The checks performed when it was installed are in docs/do-math/rebuild-verification.md; they included live launches of both CLIs, a complete small instance whose root was formally proved with a Lean proof that a review session recompiled and checked, and recovery after a runner restart." | gone | The verification record of the current implementation is `docs/do-math/lean-canon-verification.md` (V:3, V:5). What it records in the place of the three items: one small research run by six real sessions, all on `claude/opus`, so no live launch of Codex is recorded `[inferred from V:65]`; its root formally proved after a review compiled the candidate itself and read the axioms (V:68); for restarts, tests in which a runner ends at each of eight points of a publication and another completes it (V:29), brokers replaced three times and a runner restarted once on the running Mathlib instance (V:248), and both runners restarted on 23 November 2026 (V:289). |
| 222 (5) | "The full account of the first run and the running guide are in the same folder." | to be deleted (first run); true for the location of the running guide | `docs/do-math/running.md` exists `[listing]`. The file `docs/do-math/first-run-parking-unimodality.md` is deleted in the working tree `[listing]`; not checked further, as instructed. |
| 224 (1) | "The runtime tests use scripted CLI processes, Git and a controlled Lean stand-in." | partly | True as far as it goes (V:49; tests/pipeline_cli.py:1–5; tests/canon_lean.py:1). The suite now has more stand-ins: a second Lean stand-in with a memory and time profile and a stand-in for `lake env` (tests/fake_lean.py:1; tests/fake_lake.py:1), stand-ins for the judge's exporter and comparator (V:34), and stand-in sessions, a stand-in TeX command and a stand-in collection of papers for the paper command (tests/test_paper.py:1–9; V:102). The use of real Git is `[inferred]` from imports (see Part 1, topic 2). |
| 224 (2) | "They cover evidence propagation, occupancy and leases, questions, scheduling, glossary and index rendering, formal-evidence identity, interruption, recovery and context delivery." | partly | The list is that of the previous suite. There is no glossary in the current system (SK:58). The current coverage, module by module, is the table at V:25–41: the canon and its index, standing and settlement, publication, questions, derived views, the broker, the paper command, the judge, the dependency map, session launch context, ending and resumption, recovery, retention, containment, CLI adapters, and one scripted research. |
| 226–228 | Code block: `python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v` | partly | This is not the command the sources give. "Each module is run by itself, from the `runtime` folder, with `python -m unittest tests.<module>`." (V:23) Whether the `discover` form works on the current suite is not established; I did not run it. The seven modules run on 23 November 2026 took 72 to 606 seconds each on a loaded machine, 2,076 seconds together (V:276–284). |
| 230 (1) | "On 12 November 2026 the suite had 316 tests and all passed." | gone | That figure belongs to the previous suite. The current document gives 755 tests (V:43); I count 763 `def test_` in 22 modules `[counted]`. The suite has not been run as a whole since the runtime was changed (V:15, V:47); the last recorded run of each module is in Part 1, 1.9. |
| 230 (2) | "These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce." | true | V:49. The source adds a second limit that the sentence does not state: the tests do not show how the real compiler behaves (V:19, V:49). |
| 232 | Heading "Standalone tools and supporting skills" | true | — |
| 234 | "The repository also holds four programs that do not depend on do-math and are not needed to run it. Their READMEs are in Korean." | partly | Four programs and Korean READMEs: true `[listing]`. "not needed to run it" no longer holds without qualification for scholarly-mcp: the default settings attach it to every instance, and `init` refuses when the configured server command is not found; an instance runs without it only when its settings give `"mcp_servers": {}` (OPS:236, OPS:247). |
| 236 | scholarly-mcp item | partly | "searches 49 academic sources": 49 are registered, 48 marked `partial` and Unpaywall `deferred` (services/scholarly-mcp/README.md:15). "The public sources need no login; some others go through one university library's login": true (services/scholarly-mcp/README.md:15, :52). "When configured for an instance, it gives do-math's sessions literature search": it is now attached by default, with `--public-only`, under which it serves about twenty login-free sources and refuses the others, so sessions cannot search MathSciNet or fetch subscription full texts (OPS:236, OPS:249). |
| 237 | continuous-development item | true | services/continuous-development/README.md:3–5 |
| 238 | async-development item | true | services/async-development/README.md:9–13 |
| 239 | jev-cli item | true | services/jev-cli/README.md:3 |
| 241 | "The repository's other skills support its development." | true | `[inferred]` from the descriptions in Part 1, topic 7 |
| 243–244 | Table header | true | — |
| 245 | graphify row | true | .claude/skills/graphify/SKILL.md:3, :8. Its example commands name files the current do-math folder does not hold (Part 1, topic 7). |
| 246 | verify-rounds row | true | .claude/skills/verify-rounds/SKILL.md:3, :8–15 |
| 247 | write-for-reader row | true | .claude/skills/write-for-reader/SKILL.md:3 |
| 248 | grilling, grill-me row | true | .claude/skills/grilling/SKILL.md:3, :8; .claude/skills/grill-me/SKILL.md:3–7 |
| 249 | skill-creator row | true | .claude/skills/skill-creator/SKILL.md:3 |
| 250 | writing-skills row | true | .claude/skills/writing-skills/SKILL.md:3 |
| 251 | simplify row | true | .claude/skills/simplify/SKILL.md:7–14 |
| 252 | memory-harness row | true | .claude/skills/memory-harness/SKILL.md:3, :8 |
| 253 | commit-harness row | true | .claude/skills/commit-harness/SKILL.md:3, :14 |
| 254 | dream-harness row | true | .claude/skills/dream-harness/SKILL.md:3 |
| 256 | Heading "Language, roadmap, citation and license" | to be deleted (the word "roadmap") | — |
| 258 (1) | "The do-math operator and role guides, the formats of the files that sessions exchange, the runtime output and this README are in English." | true | "Everything inside an instance is written in English" (SK:34); the guides read for this digest are in English. The runtime's output was not examined. |
| 258 (2) | "The supporting skills, the standalone tools' documentation and the working-memory directory are primarily in Korean." | true | The skill files and the four service READMEs read for this digest are in Korean, apart from the English descriptions of `grilling` and `grill-me`. |
| 258 (3) | "Planned work is in ROADMAP.md." | to be deleted | — |
| 260 (1) | "To cite the software, use the repository's CITATION.cff, which GitHub renders under 'Cite this repository'." | partly | The file exists. Its `message`, `abstract`, `keywords` and `references` describe the previous implementation and the parking-function run (Part 1, topic 8). GitHub's rendering was not checked. |
| 260 (2–3) | The sentences on the first run's knowledge base, its DOIs and its Zenodo licence | to be deleted | — |
| 262 (1) | "This project is licensed under the GNU Affero General Public License v3.0." | true in the working tree | `LICENSE` begins "GNU AFFERO GENERAL PUBLIC LICENSE Version 3" (LICENSE:1–2); CITATION.cff:12; THIRD-PARTY-NOTICES.md:3. All four are uncommitted changes from the Mozilla Public License 2.0 `[listing: git diff]`. |
| 262 (2) | "Four skill directories are adapted from third-party projects and keep their original licenses; see THIRD-PARTY-NOTICES.md." | true | THIRD-PARTY-NOTICES.md:5–10; all four directories and their licence files exist `[listing]` |

---

# Part 3. What exists in this area and is absent from README lines 220 to 262

Each item is something a reader who wants to judge the system's reliability would need and that those lines do not give.

**About the evidence.**

1. The verification record of the current implementation, `docs/do-math/lean-canon-verification.md`, and the design record, `docs/do-math/lean-canon-design.md`; and the fact that the design record is kept as written while the guides and the code depart from it in stated places (V:3, V:139, V:151).
2. The two limits of the test suite beyond "stand-ins": the tests do not show how the real compiler behaves, and that difference has hidden two defects, one of which let a theorem proved by `native_decide` count as proved from the allowed axioms while every test passed (V:49, V:51, V:184).
3. The suite has not been run as a whole since the runtime was changed; the state of each module's last run (V:15, V:47, V:252, V:287; Part 1, 1.9). Two modules have not been run since the snapshot removal `[inferred]`.
4. What real sessions have run: one small research of six sessions on one model (V:63–72), with the list of paths it did not exercise (V:74); and one research that imports Mathlib, running since 22 November 2026, whose outcome the record does not state (V:217, V:302).
5. The runs with the real compiler and no sessions: the scripted research on Lean 4.32.0 in 579 seconds (V:57), and the judge cases on Lean 4.36.0 (V:194–200).
6. The review rounds ended after the second on the user's instruction, and "the second round still found defects of substance, which is a reason to expect that some remain" (V:129).
7. The guides as they now stand were compared with the text they replaced and were not read independently from the beginning (V:17, V:178).
8. Every run whose operating system is named was on Windows; no run on Linux is recorded `[inferred]` (V:190, V:253).
9. The quantities that decide the cost of a research at Mathlib scale have not been measured (V:302), and the faults of the first day, among them reviews that ended while their sub-reviewers were still at work (V:256, V:264).

**About the machinery.**

10. The Lean broker: that every compile of an instance goes through one process which admits compiles under a memory budget, a thread budget and a check of the machine's free memory (LB:11; LEAN:31), that its reservations are model-based estimates and not guarantees (LB:23), and that on Windows the commit limit, which the user can raise through the page file, bounds how many compiles run at once (LB:29; OPS:228–230).
11. The judge of formal proofs: that formal standing is checked from outside the index with `leanexport` and `lake comparator` at every publication and once more for the settled root against the instance's first commit (OPS:409–415); that it needs Lean 4.35 or later (OPS:409); that on Windows the comparator's sandbox is switched off, so the verdict rests on the broker's builds having been made honestly (OPS:425; V:210); that `judge.py` has not been carried to a verdict on a real instance and the automatic judging of the root has not been run (V:208, V:298).
12. Lean versions: the measurements the guides quote were taken on Lean 4.32.0 and not repeated on 4.36.0 (V:186).
13. What settles whether a proof is formal: the allowed axioms, by default `propext`, `Classical.choice` and `Quot.sound`, with `sorryAx` never allowed (LEAN:214), and that whether a statement says what was meant is review's judgment and not Lean's (LEAN:226).
14. The dependency-map command and its three output files (OPS:376–380), verified on one real canon of four elements (V:80).
15. The paper command: that it runs only on a formally settled root (OPS:388); that the user must read and confirm the paper method first, which the command does not check (OPS:390); that the paper does not mention Lean and no command writes the account of the formal verification (PM:128; V:100); that it needs a TeX command and, for the collection of real papers, the network (OPS:405, OPS:392); and that the one run of the changed command that went to its end produced a one-page paper with exit code 2 and five open findings (V:106–110), with no real run since the bound was raised to eight (V:114).
16. The collection of 32 real papers: what it is for, and that only its list is in Git because one paper of the 32 carries a licence that allows redistribution (V:96, V:98).

**About the rest of the repository.**

17. The copy `.agents/skills/do-math` is a generation behind the canonical skill and carries hand edits; every command of the current runtime refuses an instance that the earlier runtime created (V:306; OPS:451; SK:82).
18. scholarly-mcp is attached to every instance by default with `--public-only`, which serves about twenty login-free sources and no subscription source (OPS:236, OPS:249); the service's own README does not document the option (services/scholarly-mcp/README.md:47–50).
19. The licence change to AGPL-3.0 is not yet committed `[listing]`.

---

# Part 4. What could not be established

## Questions from Part 1 that the sources do not answer

1. **Dates of most runs.** Only 22 November 2026 (start of the Mathlib research), 23 November 2026 (the last test runs) and "about 04:05 that day" are given (V:217, V:274, V:289). The small research, the scripted real-compiler run, the paper runs, the review rounds and the judge cases carry no date.
2. **Whether any run was made on Linux.** None is recorded; the broker and operating guides describe Linux behaviour (for example LB:27, LB:61, LB:69) without a record of a run.
3. **Whether any real Codex session has run on the current implementation.** The small research used `claude/opus` only (V:65). The models of the paper runs and of the Mathlib research are not stated. The operating guide says "Codex was tried separately" for calling a configured MCP server (OPS:253); it does not say with which generation of the runtime.
4. **The outcome of the Mathlib research.** The record says it has been running since 22 November 2026 (V:302) and reports its first day.
5. **Whether `python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v` runs the current suite.** No source gives that command, and I did not run it.
6. **The exact number of sources under `--public-only`.** The operating guide says "about twenty" (OPS:249); the code suggests 21 `[inferred]`; no source states a number, and the server was not run.
7. **Which of the 49 sources are public.** The service's README does not list them (services/scholarly-mcp/README.md:15, :52).
8. **Whether the graphify graph is current.** Not checked; it needs the tool to be run.
9. **What happened to the repository after the verification record's last section.** The record's text ends with the repairs of 23 November 2026; I did not compare it with the commit history beyond the five commit messages shown at the start of the session.

## Files not read in full

- `.claude/skills/do-math/reference/operations.md`: read lines 169–262 and 366–455 (the two sections asked for, with the settings and external-tools passages they depend on); the rest not read.
- `README.md`: read lines 210–262 only.
- The `SKILL.md` of the eleven other skills: lines 1–28 of each, which is the whole file for `grill-me`, `grilling` and `simplify`. Lines longer than 900 characters were cut in that reading (in `commit-harness`, `dream-harness`, `memory-harness`).
- Opened because a listed source pointed to them, in part: `services/scholarly-mcp/docs/USAGE.md` (lines 1–30), `services/scholarly-mcp/server.py` (lines 40–174), `services/scholarly-mcp/tests/test_mcp.py` (lines 30–69), `services/scholarly-mcp/api_adapters.py` (line 1335 only), `.claude/skills/do-math/runtime/settings.py` (lines 14–30), `.claude/skills/do-math/runtime/paper.py` (lines 78–84, by search), the first 22 lines of `tests/canon_lean.py`, `tests/fake_lean.py`, `tests/fake_lake.py`, `tests/pipeline_cli.py`, `tests/support.py`, and lines 1–30 of `tests/test_paper.py`. `.claude/skills/do-math/exemplars/manifest.json` was searched and not read.
- Read in full although not on the list: `.claude/skills/do-math/SKILL.md`, `services/scholarly-mcp/docs/SUPPORT.md`.
- No file was unreadable. `.agents/skills/do-math`, `docs/do-math/rebuild-design.md` and `docs/do-math/rebuild-verification.md` were not opened.

## Disagreements between sources

Each is reported with both locations and is not resolved here.

1. **Test counts.** The table under "Automated tests" gives `test_canon` 221, `test_paper` 36, `test_judge` 19, eight modules "102 together", and a total of 755 (V:27, V:33, V:34, V:36, V:43), and the text says "The table gives the number of tests each module holds now" (V:47). The table of 23 November 2026 in the same document gives `test_canon` 223, `test_paper` 39, `test_judge` 20, `test_ending` 30 (V:278–281). My count of `def test_` agrees with the later table and gives 104 for the eight modules and 763 in all `[counted]`.
2. **Number of test modules.** The summary speaks of "the sixteen test modules" (V:15). The table lists 22 modules (V:27–41), and the folder holds 22 `test_*.py` files `[listing]`.
3. **`test_research` and `test_publication`.** The summary table says that `test_research` "had failures that were not explained" and `test_publication` "was not run as a whole after a repair" (V:15; in detail V:204). The later section says both were run as wholes on 23 November 2026 and passed, 108 and 52 tests (V:282–283). The summary does not mention the later run.
4. **Accuracy of the baseline estimates.** `lean.md` says "The estimates have been within 2% of what a measurement gave" (LEAN:169). The verification record gives 1.9% at most for the new instance and 2.4% at most for the older instance (V:235, V:236). `lean-broker.md` quotes only the 0.6% and 1.9% of the new instance (LB:35).
5. **Files a module compile emits.** `lean-broker.md` says "A module compile emits four files" (LB:83). The verification record says that on Lean 4.36.0 "A module compile writes a fifth file, `.ir.sig`, which the broker keeps with the others" (V:186).
6. **The kernels of the judge.** One passage names "`lean4lean`, `nanoda` and the two further checkers beside Lean's own" (V:197); another names "the exporter and the further kernels (`lean4lean`, `nanoda`, `leanchecker`)" (V:296). The operating guide says "Lean's kernel and ... the other kernels that Lean ships" without a list (OPS:413).
7. **Paths not followed by real sessions.** "No real session has yet followed the guides along them", the replacement peer among them (V:74); a later section reports, from the Mathlib instance, reviews replaced by new sessions and a candidate that went to a replacement peer (V:264, V:265). The earlier sentence is about the small research and was not revised.
8. **Sessions working from the revised guides.** "no session has worked from them" (V:178); the research started on 22 November 2026 runs with this implementation (V:217). The earlier sentence was not revised.
9. **The README against the sources**, already marked in Part 2: the design and verification records named at README.md:222 against V:3; the 316 tests at README.md:230 against V:43; the test command at README.md:227 against V:23; "49 academic sources" at README.md:236 against services/scholarly-mcp/README.md:15.
10. **Upstream of `writing-skills`.** `THIRD-PARTY-NOTICES.md` names `obra/superpowers` 6.1.0 (THIRD-PARTY-NOTICES.md:8); the skill's own file names "claude-plugins-official / superpowers / 6.1.0 / writing-skills" as its origin (.claude/skills/writing-skills/SKILL.md:15). These may name the same thing by its repository and by the plugin collection it was installed from; the sources do not say.
11. **Inside the service READMEs.** The commands of `services/continuous-development/README.md` use the path `output/continuous-development/` (services/continuous-development/README.md:41–42, :96–104, :122), while the folder is `services/continuous-development/` `[listing]`. The example of `services/async-development/README.md` uses paths under `C:/stock2/` (services/async-development/README.md:64–66).
12. **Committed against working tree.** `LICENSE`, `CITATION.cff:12`, `THIRD-PARTY-NOTICES.md:3` and `README.md:262` say AGPL-3.0 in the working tree and MPL-2.0 in the last commit `[listing: git diff]`.
