"""Fixes from 독해10 (native-speaker mathematician reading)."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n >= 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

P_OLD = "so that the sessions could finish the informal mathematics before formalization resumed"
P_NEW = "so that the sessions could finish the informal mathematics before formalization resumes"

readme = [
 (P_OLD, P_NEW),
 # 1, 3 table
 ("Several steps, which the root depends on, rest on binary64 computations with error models assumed in advance. |",
  "Several steps on which the root depends rest on binary64 computations with error models assumed in advance, that is, with rounding error covered by assumed margins rather than tracked. |"),
 ("One necessary condition of the root has a Lean proof, which leaves the root open. |", "One necessary condition of the root has a Lean proof, a proof that leaves the root open. |"),
 ("| Run it | [Quick start](#running-do-math) below;", "| Run it | [Running do-math](#running-do-math) below;"),
 # 6, 7
 ("it records a finding against the record, so that the original claim and what later became of it remain visible together. No session assigns work to another. A session in the first stage reads the knowledge base and decides for itself what to work on; the one exception is formalization, which the runner requests for an accepted informal proof or refutation that can reach the root.",
  "it records a finding on the record, so that the original claim and what later became of it remain visible together. No session assigns work to another, and a session in the first stage reads the knowledge base and decides for itself what to work on. The one exception to that free choice is formalization: the runner requests it for an accepted informal proof or refutation whose outcome bears on the root."),
 # 8
 ("Two concerns shaped this design.", "Two considerations shaped this design."),
 # 11
 ("a **peer** develops it into a record, and a **review** assesses that record.", "a **peer** develops it into a draft record, and a **review** assesses that draft."),
 # 12
 ("| attempt | The knowledge base; it chooses a node to settle |", "| attempt | The knowledge base, from which it chooses a node to settle |"),
 ("| explorer | The knowledge base; it works to understand one question about the problem |", "| explorer | The knowledge base, from which it chooses a question to understand |"),
 # 14
 ("The arrows are files passed from one session to the next; no two sessions ever converse.",
  "The arrows between sessions are files passed from one to the next, and the arrows to and from the knowledge base are reads and publications; no two sessions ever converse."),
 # 15
 ("They hold the definitions and assumptions it relied on, its arguments and partial results, its computations together with their code and output, the literature it drew on and the conditions under which each source applies, the approaches that failed and what each failure actually rules out, and the steps that still have to be proved, together with the conversation itself, which the runner saves.",
  "They hold the definitions and assumptions it relied on, its arguments and partial results, and its computations with their code and output. They also hold the literature it drew on with the conditions under which each source applies, the approaches that failed with what each failure actually rules out, and the steps that still have to be proved. The runner saves the session's conversation alongside these files, and the peer receives that as well."),
 # 16
 ("The **index** lists the published records, each with its own description and the review's short assessment beside it.",
  "The **index** is a guide to the published records: those selected as shared context for new sessions, the modules into which the organizer has grouped records, and recent records not yet organized, each shown with its own description and the review's short assessment beside it."),
 # 18
 ("Registering a section is how the attempt declares what it has taken on, and the section counts as occupied until the record is published or the review decides there is nothing to publish. The reason is that until then the work exists only in the attempt's own files, where no other session can see it, and a second attempt on the same part would repeat the work without knowing.",
  "Registering a section is how the attempt declares what it has taken on. The section counts as occupied until the resulting record is published or the review decides there is nothing to publish, because until then the work exists only in the attempt's own files, where no other session can see it, and a second attempt on the same part would repeat the work without knowing."),
 # 20
 ("The coordination tools refuse only what a program can decide on its own:", "The commands with which sessions register sections and take leases refuse only what a program can decide on its own:"),
 # 21-23
 ("An attempt has no time cap. Its session is a conversation that may run over several CLI turns, so the runner does not close it the moment one CLI process exits. Instead, a separate process called the **session host**, which starts with the session and lives as long as it does, resumes the conversation and asks the session to reconsider, under its role guide, whether to end; by default it does so up to three times. Each time, the session either continues or submits an explicit decision that its work is complete or that it sees no way forward; once the limit is reached, the runner itself authorizes the end. The same reconsideration applies to explorers that have begun research, to formalizers and to peers.",
  "An attempt has no time cap. Its session is a conversation that may continue over several CLI processes in turn, so the runner does not close the session when one of those processes exits. Instead, a separate process called the **session host**, which starts with the session and lives as long as the session does, resumes the conversation each time a process exits and asks the session to reconsider, under its role guide, whether to end; by default it does so up to three times. Each time, the session either continues or submits an explicit decision that its work is complete or that it sees no way forward; once the limit is reached, the host records the runner's authorization and the session ends. The same reconsideration applies to explorers that have begun research, to formalizers and to peers; reviews and organizers are not asked to reconsider."),
 # 24, 25, 26
 ("to look for the counterexample or the identity that the producer passed over,", "to look for a counterexample or an identity that the producer passed over,"),
 ("A claim is *supported* when the offered evidence establishes it, *unsupported* when the review has found that it does not, and *undetermined* when the review could not complete the assessment.",
  "A claim is *supported* when the review finds that the offered evidence establishes it, *unsupported* when the review finds that it does not, and *undetermined* when the review could not complete the assessment."),
 ("if accepting a claim would require an essential proof that the candidate does not contain,", "if accepting a claim would require a proof of an essential step that the candidate does not contain,"),
 # 27
 ("By default the peer and review roles prefer a different model from the one the producing roles prefer.", "By default the peer and review roles put first a different model from the one the producing roles put first."),
 # 28
 ("If a later review session, whether reviewing another candidate or examining published evidence, finds a defect in it or confirms a result, it appends a **finding** to the record, so that the original claim and what later happened to its standing are both visible.",
  "If a later review session, whether reviewing another candidate or examining published evidence, finds a defect in it or confirms a result, it records a **finding** on the record, kept with the review that made it, so that the original claim and what later happened to its standing are both visible."),
 # 29, 41
 ("A pending concern does not change any claim's standing: the claim and everything derived from it keep their standing, but are marked as resting on a questioned claim, until a **comprehensive review** issues a finding that withdraws or reaffirms the claim. A comprehensive review is a review session assigned to examine published evidence and its actual uses; the runner launches one when a concern is reported,",
  "A pending concern does not change any claim's standing: the claim and everything derived from it keep their standing, and the derived outcomes are marked as resting on a questioned claim, until a review session, usually a **comprehensive review**, issues a finding that withdraws or reaffirms the claim. A comprehensive review is a review session assigned to examine published evidence and its actual uses; the runner launches one when a concern is reported,"),
 # 30
 ("A relation says that its premises cannot all hold while its conclusion fails.", "A relation says that it is impossible for all of its premises to hold while its conclusion fails."),
 # 33
 ("The role guides measure progress by the change a piece of work makes to what is known.", "The role guides describe progress as the change a piece of work makes to what is known."),
 # 34
 ("Besides their role guides, attempt, explorer, peer, review and organizer sessions receive two documents in their starting context,", "Sessions in the attempt, explorer, peer, review and organizer roles receive, besides their role guides, two documents in their starting context,"),
 # 36
 ("there is no cap on the number of rounds.", "there is no cap on the number of such continuations."),
 # 38
 ("margins added to the results are trusted to cover the rounding error rather than tracked by the arithmetic.", "the rounding error is covered by margins added to the results rather than tracked by the arithmetic."),
 # 42
 ("The **maximum displacement** of a parking function is the largest distance any of its cars had to drive past its preferred spot.", "The **maximum displacement** of a parking function is the largest distance that any car had to drive past the spot it preferred."),
 ("is unimodal: non-decreasing up to some index and non-increasing after it, with a flat peak allowed.", "is unimodal: non-decreasing up to some index and non-increasing after it."),
 # 43, 44
 ("The first route splits that failure into four cases according to where the two steps lie relative to the middle index ⌈n/2⌉, and each case has a reviewed informal proof. The second route shows that a conditional form of log-concavity suffices: log-concavity required only at a step at which the sequence decreases, which implies that once the sequence has decreased at a step it cannot rise again. That property was settled on each side of the middle.",
  "The first route splits that failure into four cases according to where the two steps lie relative to the middle index ⌈n/2⌉; each case has a reviewed informal proof that it cannot occur. The second route shows that a conditional form of log-concavity suffices: whenever the sequence decreases from one term to the next, the square of the next term is at least the product of the terms on either side of it. From this it follows that once the sequence has decreased it cannot rise again. That property was proved on each side of the middle."),
 # 45
 ("Records are cited here by the first eight characters of their identifiers;", "Records are cited here by the letter r and the first eight hexadecimal digits of their identifiers;"),
 # 48
 ("and the only outbound traffic is the CLIs' own.", "and the only outbound traffic is the CLIs' own, together with that of any tool servers you configure for the sessions."),
 # 49
 ("Then, from Claude Code or Codex started in the repository, ask the do-math skill, a folder of instructions that these CLIs load, to start research on a statement.",
  "Then, from Claude Code or Codex started in the repository, ask for research on a statement to be started with the do-math skill, a folder of instructions that these CLIs load."),
 # 50
 ("The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md), and the checks performed when it was installed, including live launches of both CLIs, a complete small instance whose root was formally proved with a Lean proof that a review session recompiled and checked, and recovery after a runner restart, are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md).",
  "The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md). The checks performed when it was installed are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md); they included live launches of both CLIs, a complete small instance whose root was formally proved with a Lean proof that a review session recompiled and checked, and recovery after a runner restart."),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 (P_OLD, P_NEW),
 ("as of the evening of 12 November 2026; the run continues.", "as of 23:15 Korean time on 12 November 2026; the run continues."),
 ("Records are cited by the first eight characters of their identifiers;", "Records are cited by the letter r and the first eight hexadecimal digits of their identifiers;"),
 # 55
 ("Call a step ℓ a descent when b(n, ℓ) > b(n, ℓ+1) and an ascent when b(n, ℓ) < b(n, ℓ+1);",
  "Call the step from index ℓ to ℓ+1 a descent when b(n, ℓ) > b(n, ℓ+1) and an ascent when b(n, ℓ) < b(n, ℓ+1), and locate each step at the index ℓ where it begins;"),
 # 56
 ("and a reviewed relation in record rdc276812 derives the second part from the fourth case of the first route.",
  "and record rdc276812 proves that, for these particular sequences, the second part is equivalent to the fourth case of the first route, so the frontier derives it from that case."),
 # 58
 ("the records found that the neighboring counts", "the records established that the neighboring counts"),
 # 62
 ("so its refutation would have refuted the root, while its proof leaves the root open.",
  "so its refutation would have refuted the root, while its proof leaves the root open; the limit was in the end proved outright, which is what the theorem's name records."),
 # 64
 ("the one action the operator took on its own initiative is marked as such.", "the row marked Operator action records something the operator did directly rather than through a standing input."),
 # 65
 ("An attempt may take a node that is equivalent, through an accepted relation, to a node another session occupies", "An attempt may take a node that is equivalent, through accepted relations, to a node another session occupies"),
 # 67
 ("a control file stops the runner from starting formalizers, and a standing input told the sessions |", "a control file, recognised by a temporary change to the runner, stops it from starting formalizers, and a standing input told the sessions |"),
 # 68
 ("| 12 November, 04:54 | Standing input | A decomposition of the size-growth probability into a uniform-attachment part and a leaf surplus, reported by an AI session outside the instance at the user's request, with the operator's exact-arithmetic checks and comparison against published records; passed on for the sessions to judge for themselves |",
  "| 12 November, 04:54 | Standing input | Mathematical material from an AI session outside the instance, reported at the user's request and checked by the operator in exact arithmetic and against published records; passed on for the sessions to judge for themselves |"),
 # 47
 ("and 10 pipelines were active, working on unresolved nodes and unresolved questions beside the root.", "and ten pipelines were active, working on unresolved nodes and unresolved questions other than the root."),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 # 70, 71
 ("The runtime needs Lean 4 in every case, even for a problem whose proofs will not use it, because the settings name a Lean installation and the broker starts with the runner;", "The runtime needs Lean 4 in every case, because the settings name a Lean installation and the broker starts with the runner;"),
 ("The process helpers also support Linux, where they read `/proc`;", "The code that identifies and ends processes also supports Linux, where it reads `/proc`;"),
 # 72
 ("- `explore_every`: the runner raises an exploration request each time an attempt is launched; the request is granted when a question is free, that is, open and held by no session, and the launch interval has passed.",
  "- `explore_every` (default 1): the runner raises an exploration request each time the count of attempt launches reaches a multiple of this number; the request is granted when a question is free, that is, open and held by no session, and the launch interval has passed."),
 # 74
 ("are plain text files submitted with `input --file <file>`, before `start` when they should reach every session.", "are plain text files submitted with `input --file <file>`; submit them after `init` and before `start` when they should reach every session."),
 # 75
 ("| `stop` / `resume` | Stop or resume the launching of new sessions, including peers and reviews; the runner stays alive and running sessions continue.", "| `stop` / `resume` | Stop or resume the launching of new sessions, including peers and reviews. `stop` does not end the run: the runner stays alive and running sessions continue."),
 # 76
 ("without this command, that report keeps attempt launches paused. |", "after such a report, attempt launches stay paused until this command is given. |"),
]
apply("docs/do-math/running.md", run)

zen = [
 (P_OLD, P_NEW),
 # 77, 78
 ("and what survives review is published as a record in the instance's knowledge base, of which this archive is a copy, for every later session to read. Every record was produced in three stages by three different sessions: one worked on the problem, trying to prove or refute a statement, to understand some feature of the problem or to turn an accepted proof into Lean; a second read everything the first left behind and developed it into the record, and a third checked that record against the first session's files and assessed every claim in it.",
  "and what survives review is published as a record in the instance's knowledge base for every later session to read; this archive is a copy of that knowledge base. Every record was produced in three stages by three different sessions: one worked on the problem, trying to prove or refute a statement, to understand some feature of the problem or to turn an accepted proof into Lean; a second read everything the first left behind and developed it into a draft of the record; and a third checked that draft against the first session's files and assessed every claim in it."),
 # 81
 ("Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, the conjecture's informal proof depends on them, and a reader who does not accept such a model should treat the conjecture as unproved.",
  "Several steps rest on computer-assisted inputs: a finite verification that the conjecture holds for all n ≤ 20000, and binary64 floating-point computations with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic. The reviews name these steps, the conjecture's informal proof depends on them, and a reader who does not accept such an error model should treat the conjecture as unproved."),
 # 82
 ("for each it gives the statement, its state, the proofs behind that state and the accepted implications between nodes, and for the conjecture the two chains of implications, called routes, that lead to it.",
  "for each node it gives the state, the proofs behind that state and the accepted implications to other nodes. For the conjecture it also shows the two chains of implications, called routes, that lead to it."),
 # 79, 80
 ("Two things are not part of `knowledge/`: the standing inputs, that is, the instructions the user gave to the sessions during the run, and the sessions' own conversations.",
  "Three things are not part of `knowledge/`: the standing inputs, that is, the instructions the user gave to the sessions during the run; the sessions' working files, against which the reviews checked the drafts; and the sessions' conversations."),
 ("`review/assessment.json` and `review/feedback.md` (the independent assessment)", "`review/assessment.json` and `review/feedback.md` (the third session's assessment)"),
]
apply("임시/작문/readme-20261112/stage3/zenodo-description.md", zen)
print("reader fixes 3 applied")
