"""Fixes from 독해11 (criteria: definition before use, order, one name per object, English, links, mathematics)."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n >= 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = [
 # at-a-glance table: plain words, no terms defined later
 ("| What it is | A system for autonomous mathematical research in which many AI sessions work together to prove or refute a single mathematical statement. The session that produces a piece of mathematics, the session that writes it up for others and the session that assesses it are three different conversations, and every result is published together with its assessment. |",
  "| What it is | A system for autonomous mathematical research in which many AI sessions work together to prove or refute a single mathematical statement. Each piece of mathematics is produced, written up and assessed by three different sessions, and every result is published together with its assessment. |"),
 ("| State of the root | *Informally proved* on 11 November 2026: every record and every implication in the two chains of reasoning that lead to the root was accepted by an AI review session. No person has refereed the records. Several steps on which the root depends rest on binary64 computations with error models assumed in advance, that is, with rounding error covered by assumed margins rather than tracked. |",
  "| State of the conjecture | *Informally proved* on 11 November 2026, a status defined below: every piece of the argument that leads to the conjecture was written up and passed review by an AI session, and every implication between the pieces was accepted by such a review. No person has refereed the work. Several steps on which the conjecture depends rest on binary64 floating-point computations whose rounding error is covered by assumed margins rather than tracked by the arithmetic. |"),
 ("| Formal proof | No Lean proof of the root exists; the user paused formalization on 9 November 2026. One necessary condition of the root has a Lean proof, a proof that leaves the root open. |",
  "| Formal proof | None for the conjecture. The user who started the run paused formalization, the writing of machine-checked proofs in Lean 4, on 9 November 2026. One statement that the conjecture implies has a Lean proof, which leaves the conjecture itself open. |"),
 ("| Evidence | The knowledge base on Zenodo,", "| Evidence | The knowledge base, that is, every published result with its review, on Zenodo:"),
 # lead
 ("or to turn an accepted proof into a formal proof in Lean 4, a proof assistant, and it keeps all of its work,", "or to turn an already reviewed proof into a formal proof in Lean 4, a proof assistant, and it keeps all of its work,"),
 ("Next, a second session, the peer, takes over from those files. It writes the account that other sessions will read, completes arguments where it can, looks for what the first session missed, and decides what the record should propose to the knowledge base, such as new statements to pursue. Finally, a third session, the review, checks the peer's draft against the first session's files and assesses whether each claim in it is supported.",
  "Next, a second session, the peer, starts from those files. It writes the exposition that other sessions will read, completes arguments where it can, looks for what the first session missed, and decides what the record should propose to the knowledge base, such as new statements to pursue; the result is a record candidate. Finally, a third session, the review, checks the candidate against the first session's files and assesses whether each claim in it is supported."),
 ("If the review judges the work worth keeping, the record is published with that assessment attached, and it is never edited afterwards. If a later review session finds a mistake in it or confirms one of its results, it records a finding on the record, so that the original claim and what later became of it remain visible together. No session assigns work to another, and a session in the first stage reads the knowledge base and decides for itself what to work on. The one exception to that free choice is formalization: the runner requests it for an accepted informal proof or refutation whose outcome bears on the root.",
  "If the review judges the work worth keeping, the candidate is published as a record with that assessment attached, and it is never edited afterwards. If a later review session finds a mistake in a record or confirms one of its results, it issues a finding on that record, so that the original claim and what later became of it remain visible together. No session assigns work to another: a session in the first stage reads the knowledge base and decides for itself what to work on. Formalization is the one exception. The runner requests it when a reviewed proof or refutation bears on the statement under research."),
 ("The second is independent judgment. Each piece of work is assessed by a session that took no part in producing it, so that no session certifies its own work. Useful work that is not yet perfect is still published, together with its assessment, so that a later session can tell an established result from a claim that still needs more work.",
  "The second is independent judgment. Each piece of work is assessed by a session that took no part in producing it, so that no session certifies its own work. Because the assessment travels with the work, useful work that is not yet perfect can still be published, and a later session can tell an established result from a claim that still needs more work."),
 ("along the two chains of implications that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two chains are not independent confirmations; both pass through one statement, as the first-run section explains.",
  "along the two chains of implications that lead from statements proved in earlier records to the conjecture itself, every record had passed review and every implication had been accepted by an AI review session. The two chains are not independent confirmations; both pass through one statement, as the first-run section explains."),
 ("No person has refereed the records. Several steps depend on computer-assisted inputs. And there is no Lean proof of the conjecture yet. do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session and matched against the exact statement; the user paused formalization on 9 November so that the sessions could finish the informal mathematics before formalization resumes. The knowledge base is public on Zenodo.",
  "No person has refereed the records, several steps depend on computer-assisted inputs, and there is as yet no Lean proof of the conjecture. do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session and matched against the exact statement; the user paused formalization on 9 November so that the sessions can finish the informal mathematics before formalization resumes. Everything described here can be checked, because the knowledge base is public on Zenodo."),
 # settled vs contested (F4); parts (F6)
 ("A node is **settled** once either it or its negation has been proved; the proof is either informal or formal, two levels of assurance that the section \"What counts as established\" defines.",
  "A node is **settled** once it or its negation, and not both, has been proved; the proof is either informal or formal, two levels of assurance that the section \"What counts as established\" defines."),
 ("In the same way, a record that settles part of what a node asserts can propose the parts as nodes, with the relation that the parts together cover the whole.",
  "In the same way, a record that settles part of what a node asserts can propose that part and the remainder as nodes, with the relation that together they imply the whole."),
 # roles: candidate; formalizer input includes refutation (C2, C17)
 ("a **peer** develops it into a draft record, and a **review** assesses that draft.", "a **peer** develops it into a record candidate, and a **review** assesses that candidate."),
 ("| formalizer | A node whose informal proof the review has accepted | Its retained work: Lean sources, complete or partial |", "| formalizer | A node whose informal proof or refutation the review has accepted | Its retained work: Lean sources, complete or partial |"),
 ("a formalizer receives a node whose informal proof the review has accepted\" --> P", "a formalizer receives a node whose informal proof or refutation the review has accepted\" --> P"),
 # retained work (C8)
 ("What a producing session leaves behind is its **retained work**: the files it keeps in its own directory while it works. They hold",
  "What a producing session leaves behind is its **retained work**: everything in its own directory when it ends, which is the files it kept while it worked together with its conversation, which the runner saves there. The files hold"),
 ("the approaches that failed with what each failure actually rules out, and the steps that still have to be proved. The runner saves the session's conversation alongside these files, and the peer receives that as well.",
  "the approaches that failed with what each failure actually rules out, and the steps that still have to be proved."),
 # session host (D7, E9)
 ("Instead, a separate process called the **session host**, which starts with the session and lives as long as the session does, resumes the conversation each time a process exits and asks the session to reconsider, under its role guide, whether to end; by default it does so up to three times. Each time, the session either continues or submits an explicit decision that its work is complete or that it sees no way forward; once the limit is reached, the runner authorizes the end. The same reconsideration applies",
  "Instead, a separate process, the **session host**, keeps the session alive. It starts with the session, and each time a CLI process exits it resumes the conversation and asks the session to reconsider, under its role guide, whether to end; by default it does so up to three times. The session ends when it submits an explicit decision that its work is complete or that it sees no way forward, or when the limit is reached and the runner authorizes the end; otherwise it continues. The same reconsideration applies"),
 # peer paragraph uses 'a new session' etc fine; model default (D6)
 ("By default the peer and review roles list a different model first than the producing roles do.", "By default, the first model listed for the peer and review roles differs from the first model listed for the producing roles."),
 ("it records a **finding** on the record, kept with the review that made it, so that the original claim and what later happened to its standing are both visible.",
  "it issues a **finding** on the record, kept with the review that made it, so that the original claim and what later happened to its status are both visible."),
 # route definition (D8, F5); heading (C6)
 ("### Relations, propagation and the standing of nodes", "### Relations, propagation and how nodes stand to the root"),
 ("The frontier also marks how each node stands to the root. A node is on a **route** to the root when a chain of relations lets a proof of the node contribute to settling the root, and such a chain is itself called a route; a node is a necessary condition of the root when only its refutation can contribute.",
  "The frontier also marks how each node stands to the root. A **route** to the root is a path of relations, each feeding the next and some with several premises, along which a proof of a node contributes to settling the root; such a node is said to be on a route. A node is a necessary condition of the root when only its refutation can contribute."),
 # progress (D27)
 ("Work may settle something, let the research see something it could not see before, or change how the problem is approached;", "Work may settle something, make visible what could not be seen before, or change how the problem is approached;"),
 # two documents (D9, C11)
 ("receive, besides their role guides, two documents in their starting context, in every instance started with the current do-math.", "receive, besides their role guides, two documents in their starting context."),
 ("This repository's author and an operator session wrote it", "This repository's author and an operator conversation wrote it"),
 # formalizer paragraph (C17), glossary (C13)
 ("A **formalizer** receives a node whose informal proof the review has accepted and works to build a Lean proof of the exact statement,", "A **formalizer** receives a node whose informal proof or refutation the review has accepted and works to build a Lean proof of the exact statement or of its negation,"),
 ("decides which locally introduced terms become shared vocabulary,", "decides which locally introduced terms enter the shared glossary,"),
 # computer-assisted (D10); informal (F12)
 ("In the second kind, binary64 floating point with an error model assumed in advance, the rounding error is covered by margins added to the results rather than tracked by the arithmetic.",
  "The second kind is binary64 floating point with an error model assumed in advance: the rounding error is covered by margins added to the results rather than tracked by the arithmetic."),
 ("and later work may use the result within the range the review supported.", "and later work may use the result to the extent the review supported it."),
 # concerns (D23, C6)
 ("A pending concern does not change any claim's standing: the claim and everything derived from it keep their standing, and the derived outcomes are marked as resting on a questioned claim, until a review session, usually a **comprehensive review**, issues a finding that withdraws or reaffirms the claim.",
  "A pending concern changes no status by itself. The questioned claim keeps its status, and the outcomes derived from it keep their states but are marked as resting on a questioned claim. This lasts until a review session, usually a **comprehensive review**, issues a finding that withdraws or reaffirms the claim."),
 # first run: positivity (F3); boundary (F1); Lean (D11, D15)
 ("From this it follows that once the sequence has decreased it cannot rise again. That property was proved on each side of the middle.",
  "Since all the counts are positive, it follows that once the sequence has decreased it cannot rise again. That property was proved on each side of the middle."),
 ("Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to be proved.",
  "Both routes pass through one statement, that the sequence never decreases over the steps below the middle, in the exact range of steps that the frontier's statements give; this statement was the last part to be proved."),
 ("It was formalized before the rule that limits formalization to outcomes that can reach the root was added, as the full account explains.",
  "The rule that limits formalization to outcomes bearing on the root was added after this node had been formalized, as the full account explains."),
 # Zenodo versions (D12, D18)
 ("Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records; version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved. A third version, taken at 23:25 Korean time on 12 November with 340 records, is being deposited:",
  "Each version is a snapshot of the directory. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved. A third version, taken at 23:25 Korean time on 12 November with 340 records, is being deposited:"),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 ("The terms it uses, such as node, relation, route, record, review, informally proved and computer-assisted, are defined in the repository [README](../../README.md) under \"How the research is organized\" and \"What counts as established\", and the README's section",
  "The terms it uses, such as node, relation, route, section, record, review, standing input, operator, informally proved and computer-assisted, are defined in the repository [README](../../README.md), and the README's section"),
 ("and record rdc276812 proves that, for these particular sequences, the second part is equivalent to the fourth case of the first route, so the frontier derives it from that case.",
  "and record rdc276812 proves that, for these particular sequences, the second part is equivalent to the statement that the fourth case of the first route cannot occur, so the frontier derives it from that statement."),
 ("From this property it follows that once the sequence has started to decrease it cannot rise again, which is unimodality.", "Since all the counts are positive, it follows from this property that once the sequence has started to decrease it cannot rise again, which is unimodality."),
 ("while its proof leaves the root open; the limit was in the end proved outright, which is what the theorem's name records.",
  "while its proof leaves the root open. The limit was later proved without any assumption, which the word unconditional in the theorem's name records."),
 ("and by the user's decision the five formalizations then in progress were ended without peer or review, so nothing of them was published.",
  "and by the user's decision the five formalizer pipelines then in progress were ended without peer or review, so none of their work was published."),
 ("a control file, recognised by a temporary change to the runner,", "a control file, recognized by a temporary change to the runner,"),
 ("| 12 November, 04:54 | Standing input | Mathematical material from an AI session outside the instance, reported at the user's request and checked by the operator in exact arithmetic and against published records; passed on for the sessions to judge for themselves |",
  "| 12 November, 04:54 | Standing input | Mathematical material that an AI session outside the instance had produced at the user's request; the operator checked it in exact arithmetic and against published records and passed it on for the sessions to judge for themselves |"),
 ("| 9 November | Session termination | The five formalizations in progress ended without peer or review |", "| 9 November | Session termination | The five formalizer pipelines in progress ended without peer or review |"),
 ("so that the sessions could finish the informal mathematics before formalization resumes", "so that the sessions can finish the informal mathematics before formalization resumes"),
 ("Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time and deposited at 02:38,",
  "Each version is a snapshot of the directory. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time and deposited at 02:38,"),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 ("are defined in the README under \"How the research is organized\" and \"What counts as established\".", "are defined in the README."),
 ("The runtime needs Lean 4 in every case, because the settings name a Lean installation and the broker starts with the runner;", "The runtime needs Lean 4 in every case, because the Lean broker starts with the runner;"),
 ("Changing the root's statement requires a new instance.", "A standing input cannot change the root's statement; that requires a new instance."),
 ("Existing sessions finish; their peers and reviews, and any formalizations and organizations, still launch as their inputs become ready;", "Existing sessions finish; their peers and reviews, and any formalizer and organizer sessions, still launch as their inputs become ready;"),
]
apply("docs/do-math/running.md", run)

zen = [
 ("This archive is a copy of that knowledge base for one instance: the records,", "This archive is a copy of that knowledge base for one instance, that is, one run on one statement: the records,"),
 ("or to turn an accepted proof into a formal proof in Lean 4;", "or to turn an already reviewed proof into a formal proof in Lean 4, a proof assistant;"),
 ("That state has qualifications that a reader should know before relying on it.", "The state informally proved has qualifications that a reader should know before relying on it."),
 ("so that the sessions could finish the informal mathematics before formalization resumes", "so that the sessions can finish the informal mathematics before formalization resumes"),
 ("whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7);", "whose axioms are exactly propext, Classical.choice and Quot.sound, the three standard axioms of Lean's logic, with no unproved assumption left (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7);"),
 ("which lists the records selected as shared context for new sessions, the modules into which the records were grouped, and the most recent records, each with", "which lists the records chosen as orientation for new sessions, the groups (called modules) into which records were sorted, and the records not yet sorted, each with"),
 ("`state.json` is a structured projection of the same evidence.", "`state.json` holds the same information in structured form."),
 ("Three things are not part of `knowledge/`:", "Three things are not part of the archive:"),
 ("This version of the archive was taken on 12 November 2026 at 23:25 Korean time", "This version is a snapshot taken on 12 November 2026 at 23:25 Korean time"),
 ("Version 2 was taken on 12 November at 01:52 Korean time with 300 records, and version 1 on 11 November at 00:19, while the conjecture was still open.", "Version 2 was a snapshot taken on 12 November at 01:52 Korean time with 300 records, and version 1 one taken on 11 November at 00:19, while the conjecture was still open."),
]
apply("임시/작문/readme-20261112/stage3/zenodo-description.md", zen)
print("reader fixes 5 applied")
