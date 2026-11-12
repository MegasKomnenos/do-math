"""Fixes from 독해8_수학자 and 독해9_AI연구자."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

PAUSE_OLD = "so that the research could finish first"
PAUSE_NEW = "so that the sessions could finish the informal mathematics before formalization resumed"

readme = [
 # 9:R25, 8:R-2 at-a-glance; 8:R-3 margins wording; 8:R-7 chains
 ("| State of the root | *Informally proved* on 11 November 2026: every record and every reviewed implication on two routes to the root was accepted by an AI review session. No person has refereed the records. Several steps rest on computer-assisted inputs, some in binary64 floating point with error margins assumed rather than tracked. |",
  "| State of the root | *Informally proved* on 11 November 2026: every record and every implication on the two routes to the root was accepted by an AI review session. No person has refereed the records. Several steps, which the root depends on, rest on binary64 computations with error models assumed in advance. |"),
 ("| Formal proof | No Lean proof of the root exists; the user paused formalization on 9 November 2026. One necessary condition of the root has a Lean proof. |",
  "| Formal proof | No Lean proof of the root exists; the user paused formalization on 9 November 2026. One necessary condition of the root has a Lean proof, which leaves the root open. |"),
 # 9:R2, 8:R-4 lead: instance before definition; and-chain
 ("An AI conversation called the operator sets up the instance from the user's statement and settings and operates the run on the user's behalf, and a program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on.",
  "An AI conversation called the operator sets up the run from the user's statement and settings and operates it on the user's behalf. A program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on."),
 # 9:R3, 8:R-5
 ("and decides what the record should propose for the frontier, such as new statements to pursue.",
  "and decides what the record should propose to the knowledge base, such as new statements to pursue."),
 # 8:R-6 exception wording; 8:R-12 'appends' vs never edited
 ("If a later review session finds a mistake in it or confirms one of its results, it appends a finding to the record, so that the original claim and what later became of it remain visible together. No session assigns work to another. A session in the first stage reads the knowledge base and decides for itself what to work on; the one exception is formalization, which the runner requests once a review has accepted an informal proof.",
  "If a later review session finds a mistake in it or confirms one of its results, it records a finding against the record, so that the original claim and what later became of it remain visible together. No session assigns work to another. A session in the first stage reads the knowledge base and decides for itself what to work on; the one exception is formalization, which the runner requests for an accepted informal proof or refutation that can reach the root."),
 # 9:R4
 ("so that a later session can tell an established result from a claim that still needs more.",
  "so that a later session can tell an established result from a claim that still needs more work."),
 # 9:R5, 8:R-7, 9:R6, 8:R-8
 ("This is a technical term of the system, and it means less than the words might suggest: along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session.",
  "This is a technical term of the system, and it means less than the words might suggest: on the two routes that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two routes are not independent confirmations; both pass through one statement, as the first-run section explains."),
 ("And there is no Lean proof of the conjecture yet: do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session and matched against the exact statement, and the user paused formalization on 9 November so that the research could finish first.",
  "And there is no Lean proof of the conjecture yet. do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session and matched against the exact statement; the user paused formalization on 9 November " + PAUSE_NEW + "."),
 # 8:R-9 settled
 ("A node is **settled** once either it or its negation has been proved, at either of two levels of assurance, informal and formal, which the section \"What counts as established\" defines. The run as a whole is finished only when the root has been settled at the formal level.",
  "A node is **settled** once either it or its negation has been proved; the proof is either informal or formal, two levels of assurance that the section \"What counts as established\" defines. The run as a whole is finished only when the root has been settled at the formal level."),
 # 9:R24 merges; 8:R-18 cell
 ("| organizer | The published records not yet organized | Modules of records, the choice of shared context, glossary decisions, merges |",
  "| organizer | The published records not yet organized | Modules of records, the choice of shared context, glossary decisions, merges of nodes or questions found to be the same |"),
 ("| Computer-assisted step | A step rests on a computation whose inputs, range, arithmetic, code and output the record states |",
  "| Computer-assisted step | A step rests on a computation, and the record states its inputs, range, arithmetic, code and output |"),
 # 9:R10 retained work includes conversation
 ("the approaches that failed and what each failure actually rules out, and the steps that still have to be proved.",
  "the approaches that failed and what each failure actually rules out, and the steps that still have to be proved, together with the conversation itself, which the runner saves."),
 # 9:R7, 8:R-11 lease
 ("The lease has no time limit; it ends when the session registers its section, releases the lease, or ends.",
  "The lease has no time limit; it ends when the session registers its section or releases the lease, or when the session itself ends."),
 # 9:R8, 8:R-10 session host
 ("An attempt has no time cap, and the runner does not close it the moment its CLI process exits. A separate process called the **session host**, started with the session and alive for as long as the session is, resumes the same conversation and asks the session, under its role guide, to reconsider whether to end, up to three times by default. Each time, the session either continues",
  "An attempt has no time cap. Its session is a conversation that may run over several CLI turns, so the runner does not close it the moment one CLI process exits. Instead, a separate process called the **session host**, which starts with the session and lives as long as it does, resumes the conversation and asks the session to reconsider, under its role guide, whether to end; by default it does so up to three times. Each time, the session either continues"),
 # 9:R9
 ("a session that only checked for available work and found none ends without them.", "a session that only checked for available work and found none ends without a peer or a review."),
 # 8:R-17
 ("and later work may use the result for the cases the review supported.", "and later work may use the result within the range the review supported."),
 # 8:R-19 arithmetic
 ("In the first kind, which includes exact integer arithmetic, interval arithmetic and floating point with directed rounding used to compute bounds, every result comes with a guaranteed range.",
  "In the first kind, every result is either exact or comes with a guaranteed range: exact integer arithmetic, interval arithmetic, and floating point with directed rounding used to compute bounds."),
 # 9:R12, 8:R-20 two documents
 ("after reading the records of an earlier instance that had worked on the same problem under a previous implementation, and it draws its examples",
  "after reading the records of an earlier instance that had worked on the first run's problem under a previous implementation, and it draws its examples"),
 # 9:R13
 ("The other describes the writing the author prefers, with the occasions on which those preferences became clear.",
  "The other describes the writing the author prefers and the occasions on which those preferences became clear."),
 # 9:R16
 ("Work may close something, let the research see something it could not see before,", "Work may settle something, let the research see something it could not see before,"),
 # 9:R22
 ("a directory of modules with their descriptions, and the recent records not yet organized.", "a list of modules with their descriptions, and the recent records not yet organized."),
 # 8:R-31 findings location
 ("`provenance.json` names the producing, peer and review sessions. A formal record also has",
  "`provenance.json` names the producing, peer and review sessions. Concerns and findings are not written into the record they concern; they are in the assessment of the review that raised them, collected in `state.json`, and shown in `frontier.md` beside the affected node. A formal record also has"),
 # first run: 9:R17, 8:R-21, 9:R18, 9:R19, 8:R-24
 ("The second route shows that a conditional log-concavity suffices: log-concavity required only at steps where the sequence has already started to decrease, which implies that the sequence cannot rise again once it has started to fall. That property was settled on each side of the middle.",
  "The second route shows that a conditional form of log-concavity suffices: log-concavity required only at a step at which the sequence decreases, which implies that once the sequence has decreased at a step it cannot rise again. That property was settled on each side of the middle."),
 ("Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to close. The record that closed it, r5909c9e7, inherits computer-assisted inputs from earlier records: several binary64 computations with error models assumed in advance, and a certification that the root holds for all n ≤ 20000, carried out in interval arithmetic with integer endpoints and, for the steps below the middle, also in floating point with directed rounding.",
  "Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to be proved. The record that proved it, r5909c9e7, depends on computer-assisted inputs from earlier records: several binary64 computations with error models assumed in advance, and a finite verification that the root holds for all n ≤ 20000, carried out in interval arithmetic with integer endpoints and, for the steps below the middle, also in floating point with directed rounding."),
 # 9:R6 first run pause; 8:R-15 rule added later
 ("There is no Lean proof of the root. The user paused all formalization on 9 November so that the research could finish first, and the pause is still in force. One node does have a formal proof: record r0af7f414 contains the Lean theorem `Parking.critical_increment_unconditional`, whose transitive axioms are exactly `propext`, `Classical.choice` and `Quot.sound` and whose statement the review matched to the node. The node is a necessary condition of the root, a limit that unimodality for every n implies; its refutation would have refuted the root, while its proof leaves the root open.",
  "There is no Lean proof of the root. The user paused all formalization on 9 November " + PAUSE_NEW + ", and the pause is still in force. One node does have a formal proof: record r0af7f414 contains the Lean theorem `Parking.critical_increment_unconditional`, whose transitive axioms are exactly `propext`, `Classical.choice` and `Quot.sound` and whose statement the review matched to the node. The node is a necessary condition of the root: it states a limit that unimodality for every n implies, so its refutation would have refuted the root, while its proof leaves the root open. It was formalized before the rule that limits formalization to outcomes that can reach the root was added, as the full account explains."),
 # 8:R-24 limits
 ("Several records on the routes rest on binary64 computations with error models assumed in advance, so a reader who does not accept those models should treat whatever depends on them as unproved.",
  "Several records on the routes rest on binary64 computations with error models assumed in advance, and the root's informal proof depends on them, so a reader who does not accept those models should treat the root as unproved."),
 # 9:R20 Lean reason; 9:R21 skill
 ("It needs Lean 4 in every case, and Mathlib when the proofs will draw on it.", "It needs Lean 4 in every case, because the Lean broker starts with the runner, and Mathlib when the proofs will draw on it."),
 ("Then, from Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement.",
  "Then, from Claude Code or Codex started in the repository, ask the do-math skill, a folder of instructions that these CLIs load, to start research on a statement."),
 # 9:U6 web search in README
 ("Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read.",
  "Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read; the sessions also have the CLIs' built-in tools, which include web search."),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 # 9:F2
 ("and a standing input that it use no records or code from an earlier instance", "and a standing input that it should use no records or code from an earlier instance"),
 # 8:F-3, 8:F-16
 ("on Codex gpt-6.1-sol as their first choice until 7 November and on Claude Fable 5.1 afterwards, each with the other as fallback.",
  "on Codex gpt-6.1-sol as their first choice until 7 November and on Claude Fable 5.1 afterwards, with the other model as fallback in each period."),
 ("they were then moved to Claude Opus 5.5 as their first choice, and the default described in the README, under which peer and review prefer a different model from the producing roles, was adopted at the same time.",
  "they were then moved to Claude Opus 5.5 as their first choice, and at the same time do-math's default was changed to the one the README describes, under which peer and review prefer a different model from the producing roles."),
 # 9:F3
 ("in the third the descent is below m−1 and the ascent at or beyond m; in the fourth both are below m. Each case has a reviewed informal proof.",
  "in the third the descent is below m−1 and the ascent at or beyond m; in the fourth both are below m. These four cases cover every way the failure can occur, and each has a reviewed informal proof."),
 # 8:R-21 doc wording
 ("a property weaker than full log-concavity suffices for the root: log-concavity required only at steps where the sequence has already started to decrease, namely that",
  "a property weaker than full log-concavity suffices for the root: log-concavity required only at a step at which the sequence decreases, namely that"),
 # 9:F15, 8:F-7
 ("In the part of it that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records found that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows, and that their difference b(n, ℓ) − b(n, ℓ−1), whose sign decides the inequality, is smaller than either count by a factor of order ℓ^(−1/3).",
  "In the part of that statement's range that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records found that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows, and that their difference b(n, ℓ) − b(n, ℓ−1), whose sign decides the inequality, is only of order ℓ^(−1/3) times either count."),
 # 9:F13 pause by user's decision; pause wording
 ("On 9 November the user paused all formalization so that the research could finish first, and the five formalizations then in progress were ended without peer or review, so nothing of them was published.",
  "On 9 November the user paused all formalization " + PAUSE_NEW + ", and by the user's decision the five formalizations then in progress were ended without peer or review, so nothing of them was published."),
 # 9:F8 actors
 ("The user and the operator intervened in the run in the ways listed below. Standing inputs apply to sessions launched after them.",
  "The user and the operator intervened in the run in the ways listed below. Standing inputs and settings changes were the user's decisions, carried out by the operator; software changes were made by the repository's author, who is also the user of this run; the one action the operator took on its own initiative is marked as such. Standing inputs apply to sessions launched after them."),
 ("| 9 November | Operator action | Five questions placed on the frontier without review, when questions were introduced |",
  "| 9 November | Operator action | Five questions placed on the frontier without review, when questions were introduced; the operator wrote them from the research so far |"),
 ("| 9 November | Standing input and runner control | Formalization paused so that the research could finish first: a control file stops the runner from starting formalizers, and a standing input told the sessions |",
  "| 9 November | Standing input and runner control | Formalization paused " + PAUSE_NEW + ": a control file stops the runner from starting formalizers, and a standing input told the sessions |"),
 # 8:F-20
 ("written during this run and since part of do-math's reference folder |", "written during this run and since then part of do-math's reference folder |"),
 # 9:F10, 8:F-17 external material
 ("| 12 November, 04:54 | Standing input | Material from a session outside the instance, passed on as unverified material for the sessions to judge for themselves |",
  "| 12 November, 04:54 | Standing input | A decomposition of the size-growth probability into a uniform-attachment part and a leaf surplus, reported by an AI session outside the instance at the user's request, with the operator's exact-arithmetic checks and comparison against published records; passed on for the sessions to judge for themselves |"),
 # 9:F11, 8:F-18/F-19 14:15 row
 ("| 12 November, 14:15 | Standing input | Prove the two monotonicity properties that the table used by record r030ffaeb depends on, before any other work; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove them |",
  "| 12 November, 14:15 | Standing input | Give priority over all other work to proving two monotonicity properties that a table used by record r030ffaeb relies on and that its review had accepted on numerical evidence; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove both properties independently |"),
 # 9:R26 node count
 ("the run had launched 1,237 sessions and published 340 records in 426 publication commits, and 10 pipelines were active,",
  "the run had launched 1,237 sessions and published 340 records in 426 publication commits, the frontier held 108 nodes, and 10 pipelines were active,"),
 # 8:F-22
 ("changed the quality of the research has not been measured; the run shows only that they were exercised at this scale, and it does not show that they improve the research.",
  "changed the quality of the research has not been measured; the run shows only that they were exercised at this scale."),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 # 8:N-1
 ("it needs Mathlib when the proofs the sessions write will draw on it, which the user judges from the problem at setup.",
  "it needs Mathlib when the proofs the sessions write will draw on it, a judgment the user makes from the problem at setup."),
 # 9:U1, 8:N-2 defaults as a list
 ("The defaults are eight concurrent sessions (`max_sessions`), attempts and explorers launched at least 180 seconds apart (`launch_interval`), an exploration request raised by the runner each time an attempt is launched (`explore_every`; the request is granted when a question is free, that is, open and held by no session, and the interval has passed), an organizer after four research publications (`organizer_every_records`), and up to three reconsideration turns before a session may end (`max_end_resumptions`).",
  "The defaults are these.\n\n- `max_sessions`: eight concurrent sessions.\n- `launch_interval`: attempts and explorers are launched at least 180 seconds apart.\n- `explore_every`: the runner raises an exploration request each time an attempt is launched; the request is granted when a question is free, that is, open and held by no session, and the launch interval has passed.\n- `organizer_every_records`: an organizer is launched after every four published records from attempts and explorers.\n- `max_end_resumptions`: a session is asked to reconsider ending up to three times."),
 # 8:N-3
 ("each entry names a model as `provider/model` with the CLI's reasoning-effort setting, of which `xhigh` is the highest.",
  "each entry names a model as `provider/model` together with the CLI's reasoning-effort setting, whose highest value is `xhigh`."),
 # 9:U2
 ("as here with the Opus alias the Claude CLI resolves:", "as in this example, where `claude/opus` is an alias that the Claude CLI resolves to a model:"),
 # 8:N-5
 ("All sessions request a one-million-token context from their CLI; do-math only requests it, and the CLI and the account decide what the session actually gets.",
  "All sessions request a one-million-token context from their CLI; the CLI and the account decide what the session actually gets."),
 # 8:N-6
 ("`init` creates the instance at a new path.", "With the two files ready, `init` creates the instance at a new path."),
 # 9:U3
 ("waits until the runner has written the record that confirms it is up,", "waits until the runner has written the file that confirms it is up,"),
 # 8:N-7
 ("a state that `status` shows under `attempt_dispatch`; that report otherwise pauses attempt launches. |",
  "a state that `status` shows under `attempt_dispatch`; without this command, that report keeps attempt launches paused. |"),
 # 9:U4
 ("Retained research is still processed once launching is resumed. |", "The session's retained work is still processed, as long as launching is not stopped. |"),
 # 8:N-8
 ("A session interrupted by a provider's usage limit or another failure leaves its retained work for a peer.",
  "A session interrupted by a provider's usage limit or another failure leaves its retained work for a peer, if it had begun research."),
 # 8:N-9
 ("Formal settlement of the root stops new attempts and explorers. Existing sessions finish;",
  "When the root is formally settled, the runner stops launching new attempts and explorers. Existing sessions finish;"),
]
apply("docs/do-math/running.md", run)

zen = [
 # 8:Z-1 frontier gloss; 8:Z-2 'here'
 ("together with the index, frontier and glossary derived from them.", "together with the index, the frontier (the list of statements the research tracked, with their states) and the glossary derived from them."),
 ("and what survives review is published as a record for every later session to read.",
  "and what survives review is published as a record in the instance's knowledge base, of which this archive is a copy, for every later session to read."),
 # 9:Z4 Lean in stage one
 ("one worked on the problem, a second read everything the first left behind", "one worked on the problem, trying to prove or refute a statement, to understand some feature of the problem or to turn an accepted proof into Lean; a second read everything the first left behind"),
 # 9:Z3, 8:R-7/Z-5
 ("The term is do-math's own and claims less than the words may suggest: it means that along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session.",
  "The term is do-math's own, and it means less than the words may suggest: on the two routes that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two routes are not independent confirmations; both pass through one statement, that the sequence never decreases below its middle index."),
 # 9:Z2, 8:Z-8
 ("The state has qualifications that a reader should know before relying on it. Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, and a reader who does not accept such a model should treat what depends on it as unproved.",
  "This state has qualifications that a reader should know before relying on it. Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, the conjecture's informal proof depends on them, and a reader who does not accept such a model should treat the conjecture as unproved."),
 # 9:Z1, 8:Z-9
 ("The conjecture has no Lean proof, because the user paused formalization on 9 November so that the research could finish first. One necessary condition of the conjecture does have a Lean proof, whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7).",
  "The conjecture has no Lean proof; the user, the person who started the run, paused formalization on 9 November " + PAUSE_NEW + ". One necessary condition of the conjecture has a Lean proof, whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7); its proof leaves the conjecture open."),
 # 8:Z-10
 ("`frontier.md` lists the nodes, the exact statements the research tracked, with the conjecture first among them;",
  "`frontier.md` lists the nodes, that is, the exact statements the research tracked, with the conjecture first among them;"),
 # 8:Z-11, Z-14
 ("The standing inputs, the instructions that the user gave to the sessions during the run, and the sessions' own conversations are not part of `knowledge/`; the repository's first-run document lists the inputs.",
  "Two things are not part of `knowledge/`: the standing inputs, that is, the instructions the user gave to the sessions during the run, and the sessions' own conversations. The repository's first-run document (docs/do-math/first-run-parking-unimodality.md) lists the inputs."),
]
apply("임시/작문/readme-20261112/stage3/zenodo-description.md", zen)
print("reader fixes 2 applied")
