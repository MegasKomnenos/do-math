# do-math Lean canon: verification

do-math runs unattended mathematical research with sessions of six roles. In the redesign recorded in [the design record](lean-canon-design.md), the knowledge of a research instance is a Lean library from its first session on: every assertion the research keeps is a Lean declaration with a written record beside it, and sessions find their work, publish their results and read earlier results through that library. The redesign is implemented in the canonical skill, `.claude/skills/do-math/`.

This document records what was run to check that implementation, what each run showed, and what no run has shown. It is written for two decisions: how far the implementation can be relied on as it stands, and what has to be checked or decided before the first real research is started with it.

## What was agreed, and where it stands

The agreement that preceded the implementation fixed three conditions for calling the work complete. The tests pass. A small proposition runs from its Lean root to a dependency map and to the PDF of a paper. The guides pass independent reading.

The first and the third are met. The second, the run from the Lean root to the paper, is met except for its last step, the PDF.

| Condition | State | Where this document reports it |
|---|---|---|
| The tests pass | Met: all sixteen test modules pass | "Automated tests" |
| A small proposition runs from the Lean root to the dependency map and the paper's PDF | Met up to the paper's LaTeX manuscript. No PDF was produced, because the machine has no TeX and installing one needs the user's approval | "A research run by real sessions", "The dependency map and the paper" |
| The guides pass independent reading | Met: the design record and the final guides were read independently, and two rounds of review and repair followed | "Independent reading and the review rounds" |

Three limits qualify these results, and each has a section of its own. The research that real sessions ran was one small research, so it exercised the paths that one small research takes and no others. The tests replace the Lean compiler by a stand-in, so they do not show how the real compiler behaves. And nothing was run at the scale of a research that imports Mathlib.

## Automated tests

The test suite is `runtime/tests/` in the skill. Each module is run by itself, from the `runtime` folder, with `python -m unittest tests.<module>`. Every module passed in its last run; the note below the table says which runs those were.

| Module | Tests | What it covers |
|---|---|---|
| `test_canon` | 217 | Names and paths, record and approach formats, applying a candidate to the library, the structural index, the axioms a proof depends on, the machine checks of a candidate |
| `test_research` | 106 | Standing, settlement, contested and refuted statements, the frontier, which proofs are sent to a formalizer, coordination, the runner's scheduling |
| `test_publication` | 47 | A publication from candidate to commit, a runner that ends at each of eight points of a publication and is followed by one that completes it, the replacement peer, the organizer, the transport checks |
| `test_questions` | 51 | Questions, their understanding texts, merges, the operator's publication of questions |
| `test_views` | 26 | The derived views and every reading command |
| `test_lean_broker` | 90 | The Lean broker: scheduling, the module cache and its key, snapshots, recovery |
| `test_paper` | 21 | The paper command: materials, plan checks, manuscript checks, the repair loops, the stop without TeX |
| `test_depmap` | 20 | The dependency map: which elements are units, the kinds of line, the drawing. One test, of the optional ELK layout, is skipped because the `elkjs` package is not installed |
| `test_context`, `test_ending`, `test_resilience`, `test_retention`, `test_containment`, `test_cli_adapter`, `test_availability`, `test_pipeline` | 102 together | What a session receives at launch, ending and resumption, recovery from failures, retention of session work, process containment, the CLI adapters, the report that all work is occupied, and one scripted research from start to formal root |

The tests number 680 in all.

One test failed twice before its cause was found. In two runs of the suite made while the machine was under heavy load, the modules took three to four times as long as before, and one test of `test_research`, which creates an instance and expects the creation to be refused, ended in an error. The first time only the result lines had been kept. The second time the full output was kept, and it showed the cause: `init` asked the broker it had started to end and returned without waiting for it, so the test removed the instance's folder while the broker still held its log file open. `init` now waits until that broker has ended. After this change the test passed three times in a row under the same load, and four modules were run again and passed: `test_research`, `test_pipeline`, `test_availability` and `test_context`. The other twelve modules were last run before this change. The change is confined to the last step of `init`, where the broker is ended after the instance has been built.

**What the tests do not show.** The tests do not run Lean. A stand-in program, `tests/canon_lean.py`, takes the compiler's place: it reads a small subset of Lean and prints the rows that the index extraction prints. Scripted programs take the place of the AI sessions. The tests therefore show that the runtime does what it should with the outputs it is given. They do not show that the real compiler gives those outputs, and in particular the Lean program that extracts the structural index is exercised only by the runs with the real compiler described next.

The difference has already hidden one defect. The extraction file imported only the modules a change had touched, so the real compiler could not confirm a record's claim that a new declaration proves or refutes a statement declared in a module the new one does not import. The stand-in sees every module at once and confirmed the claim. In the research described below, a peer met the refusal while it prepared its candidate, before the candidate was handed to review, and worked around it. The review rounds found the cause in that session's record and repaired both the extraction and the stand-in.

## Runs with the real compiler

Lean 4.32.0 was used, without Mathlib.

A scripted research, the one `test_pipeline` runs, was run once against the real compiler in place of the stand-in. It finished in 579 seconds with the root formally proved. Creating the instance took 41.7 seconds. The run included the step that the research by real sessions did not reach: the root first receives a proof written in words, and its Lean declaration names the lemma that proof rests on and ends in `sorry`. The proof of the same declaration is then replaced in place by a complete Lean proof, and an import is added to the root's module. The five compiles that extract the index had a median of 57 seconds, and each was charged about 2.1 GB against the memory that Windows had promised to processes, its commit charge, on the machine while another research instance was running on it.

The measurements that the design rests on are in section 12 of the design record. One of them corrects an expectation of the design and matters for cost: replacing a proof leaves the compiled public output of its module unchanged only when the new proof makes the elaborator generate the same auxiliary declarations as the old one. Otherwise the modules that import it are compiled again.

## A research run by real sessions

One research was run from start to finish by real AI sessions and the real compiler. The proposition was that the sum of the first n odd natural numbers is n squared. The operator's part followed the guide: the root in words, a definition and the root statement in Lean in two modules, a record for each declaration, and a check of the definition on six known values as a theorem with a complete proof. The instance is kept at `.skill-workspace/do-math-e2e-20261122/instance`, a local folder outside version control.

The runner launched six sessions, all on the same model (`claude/opus`, effort high): an attempt, an exploration, a peer for each, and a review for each candidate. The following happened.

- The attempt found a complete Lean proof of the root by induction and left it as the text of the root's declaration. Its peer made the candidate: the proof in place of `sorry`, the root's record with the written proof and an explanation, an approach entry, and one new element stating that the recursive definition equals the literal sum for every n.
- The review compiled the candidate itself, read the axioms (`propext` and `Quot.sound`), confirmed and accepted the proof. The runner built the candidate on the canon, installed it and committed. The root was formally proved 863 seconds after the attempt started, and the instance counted as complete from then on.
- The exploration was assigned the root question. Its peer published, 2,377 seconds after the attempt started, nineteen further elements with complete Lean proofs and the first understanding text of the root question. Among them are a second proof of the root's statement as a separate declaration, and two proofs that review confirmed as correct and did not yet accept, giving its reason. Such a proof is published and can be used, and its statement stays marked as work that remains. This is the second of review's two judgments at work.
- The runner then found nothing left to do and ended.

The canon at the end holds 23 elements: three definitions, eighteen statements whose proofs are accepted and two whose proofs are correct and held back. Twenty statements are formal.

**What this run did not exercise.** The first proof of the root was already a complete Lean proof, so no formalizer was launched. Two publications were too few for an organizer. No candidate failed to build, so no replacement peer was needed. No candidate offered a new proof in the place of an existing one, so review never had to decline such a replacement, and no concern or contested statement led to a comprehensive review. No statement was refuted. These paths are covered by the tests and, for the formalizer's replacement in place, by the scripted run with the real compiler. No real session has yet followed the guides along them.

## The dependency map and the paper

Both commands were run on the instance of the previous section.

`depmap.py` drew the map after the first publication, when the canon held four elements. The map shows the units, the elements whose record marks them as results one would name when describing how the proof goes; the other elements are steps and are folded into the lines. Two of the four are units, the definition of the sum and the root, and the map joins them by one line. It wrote the SVG drawing, the page for a browser and the JSON file from which the map can be drawn again. A map this small shows that the command runs on a real canon. It does not test the layout, which the tests exercise on larger canons made by hand.

`paper.py` went through every stage except the typesetting, with real sessions: one planned the paper, two wrote its two sections, the manuscript passed the machine checks, two sessions read it with nothing but the manuscript before them, a repair session followed each reading, and one session compared the paper's one numbered statement with the statement of its element and found them the same. The eight sessions took 591 seconds. The command then stopped with exit code 3, as it is meant to when no TeX command is available, leaving the manuscript `paper.tex`, the plan, the correspondence file and the log under `.skill-workspace/do-math-e2e-20261122/out/paper`.

**What is missing.** No PDF exists. The LaTeX that the script itself writes, the preamble and the command that typesets the Lean statement, has never been typeset, and an error there could not be repaired by the repair sessions, which rewrite the parts and not the preamble. The first run on a machine with TeX is the test of it. Running the command again with `--typeset-only` and the same output folder typesets the existing manuscript.

Both readings raised the same point, which no repair could settle because it is not a matter of wording: the paper says that its main theorem has been verified in Lean, and a reader has no way to reach the Lean source. Where that source is published, and how the paper refers to it, is for the user to decide.

## Independent reading and the review rounds

The design record was read fifteen times by a reader that received the manuscript and a description of its reader and nothing else, and it was revised after each reading until the reading reconstructed what had been agreed.

The guides were read in three stages. The agents that wrote them had fresh readers read their drafts. After the runtime had stopped changing, four readers read the final guides as the sessions of the roles and the operator receive them, first alone and then against the code. This second stage found what the first could not: places where guides written at the same time by different authors said different things about one matter, and places where the code had come to behave otherwise than a guide said. They were corrected before the first commit.

The third stage was two rounds of review and repair over the guides, the runtime and the tests, 68 files. In each round six repairers, five with an area of files and one following the design's decisions and the guides' promises into the code, wrote findings with complete repairs, and three judges decided each finding independently; a repair was applied only when all three approved it. The record of the rounds is `임시/do-math-lean-canon_검증_20261122/장부.md` with its closing report `종료보고.md` beside it.

| Round | Findings | Applied | Rejected | Left to the user |
|---|---|---|---|---|
| 1 | 29 | 25 | 3 | 1 |
| 2 | 21 | 19 | 0 | 2 |

The rounds ended after the second on the user's instruction, so they did not run until a round found nothing. The second round still found defects of substance, which is a reason to expect that some remain.

Among the repairs that changed behaviour: the broker's gate on free memory now subtracts the memory still owed to compiles that have started and not yet loaded their imports, where before compiles started a fraction of a second apart all passed on the same free memory; the paper command no longer reports a manuscript with open findings as complete when it is typeset later; the index extraction can confirm a claim across modules; approach entries of a statement whose proof is accepted go to the history by every path; and two formalizers are no longer sent to one statement.

The three findings of the first round that were rejected named real defects with a flawed repair. Two were found again and repaired in the second round. The third, that a refutation is not counted when the negation of a statement is settled through a proof held by another declaration of that negation, was repaired afterwards, outside the rounds, with a test.

Three findings propose a choice that belongs to the user and were left as they are. None of them prevents a research from being started. The third can cost a peer a refused candidate until it is decided, and the first matters only to a research that ends in a refutation.

- A research that ends in a refutation of the root: the dependency map does not show the refutation or what it rests on.
- The broker does not run a compile again without its snapshot when the snapshot it loaded had been proven sound by an earlier compile. The agreed proposal and the design record state the fallback without this exception, and two guides say that no compile is reported as failed because of a snapshot.
- A statement that supersedes a settled statement: the agreement lets the old statement's proof become one line deriving it from the new one, and no path carries that out for a statement that is already settled: a session may replace the proof only of a statement it has registered as its work, and that registration is refused for a statement that is already settled. Two guides still direct the peer along that path.

## What has not been measured

No research that imports Mathlib has been run with this implementation, and the quantities that decide its cost at that scale are unknown: how long the import takes in each compile and how much of it the snapshots save, how often a replaced proof changes the public output of its module and sets off compiles downstream, how long a publication waits for its build while other compiles hold the memory, and how many publications an hour the single publication queue carries. Section 16 of the design record lists what to observe in the first real run. On Windows the page file bounds how many compiles run at once, since a Lean process is charged for the whole size of the library files it maps; the operator's guide gives the measurement and the recommendation, and the change is the user's to make.

## Installation and scope

Only the canonical skill was changed. The generated copy `.agents/skills/do-math` was not regenerated, by the user's decision, because a running research instance uses it. The two now differ by a whole generation. The new runtime refuses an instance that was not created by it, so regenerating the copy while that instance exists would leave its runner unable to start. The copy is to be regenerated when that instance has been ended.
