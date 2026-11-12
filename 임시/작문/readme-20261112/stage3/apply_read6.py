"""Fixes from 독해12 (sixth reading)."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n >= 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

PAUSE_OLD = "so that the sessions can finish the informal mathematics before formalization resumes"
PAUSE_NEW = "so that the sessions could finish the informal mathematics before formalization is resumed"

readme = [
 (PAUSE_OLD, PAUSE_NEW),
 ("so that the sessions could finish the informal mathematics before formalization resumes", PAUSE_NEW),
 # table (G9, E4, D5, C16, G10)
 ("Each piece of mathematics is produced, written up and assessed by three different sessions, and every result is published together with its assessment. |",
  "Mathematics is produced, written up and assessed by three different sessions, and every result is published together with its assessment. |"),
 ("*Informally proved* on 11 November 2026, a status defined below: every piece of the argument", "*Informally proved* on 11 November 2026, a status defined below. In brief, every piece of the argument"),
 ("One statement that the conjecture implies has a Lean proof, which leaves the conjecture itself open. |", "One statement that the conjecture implies has a Lean proof; the conjecture itself remains open. |"),
 ("| Evidence | The knowledge base, that is, every published result with its review, on Zenodo:", "| Evidence | The knowledge base, which holds every published record with its review, on Zenodo:"),
 ("| Cite | [CITATION.cff](CITATION.cff) for the software; the knowledge base by its DOI. |", "| Cite | [CITATION.cff](CITATION.cff) for the software; the knowledge base by the DOI of the version you read. |"),
 # lead (D3, E1, D6, G3, G6)
 ("or to turn an already reviewed proof into a formal proof in Lean 4, a proof assistant, and it keeps all of its work, from definitions and computations to approaches that failed, in its own working files.",
  "or to turn an already reviewed proof into a formal proof in Lean 4, a proof assistant. It keeps all of its work, from definitions and computations to approaches that failed, in its own working files."),
 ("If the review judges the work worth keeping, the candidate is published as a record with that assessment attached, and it is never edited afterwards.", "If the review judges the work worth keeping, the candidate is published as a record with that assessment attached, and the record is never edited afterwards."),
 ("No session assigns work to another: a session in the first stage reads the knowledge base and decides for itself what to work on. Formalization is the one exception. The runner requests it when a reviewed proof or refutation bears on the statement under research.",
  "No session plans the work of another. A session in the first stage reads the knowledge base and decides for itself what to work on, and the runner assigns work only where it follows from what has already happened: a peer and a review for every piece of retained work, and a formalizer when a reviewed proof or refutation bears on the statement under research."),
 ("has been recompiled by a review session and matched against the exact statement;", "has been recompiled by a review session, audited for the axioms it uses and matched against the exact statement;"),
 ("Everything described here can be checked, because the knowledge base is public on Zenodo.", "The records and their assessments can be checked, because the knowledge base is public on Zenodo."),
 # roles table and diagram (G11)
 ("| formalizer | A node whose informal proof or refutation the review has accepted | Its retained work: Lean sources, complete or partial |",
  "| formalizer | A node whose informal proof or refutation the review has accepted and whose outcome can reach the root | Its retained work: Lean sources, complete or partial |"),
 ("a formalizer receives a node whose informal proof or refutation the review has accepted\" --> P", "a formalizer receives an accepted proof or refutation that can reach the root\" --> P"),
 # retained work (D1)
 ("What a producing session leaves behind is its **retained work**: everything in its own directory when it ends, which is the files it kept while it worked together with its conversation, which the runner saves there. The files hold",
  "What a producing session leaves behind is its **retained work**: the contents of its own directory when it ends. Those are the files it kept while it worked, together with its conversation, which the runner saves there. The files hold"),
 # end of session (A7, G4)
 ("The same reconsideration applies to explorers that have begun research, to formalizers and to peers; reviews and organizers are not asked to reconsider.",
  "The same reconsideration applies to explorers that have begun research, that is, that have taken a question and started on it, to formalizers and to peers; reviews and organizers are not asked to reconsider."),
 ("A session interrupted from outside, by a provider's usage limit for example, is treated the same as one that ended on its own. In either case, if the session had begun research, its retained work goes on to a peer and a review; a session that only checked for available work and found none ends without a peer or a review.",
  "A producing session interrupted from outside, by a provider's usage limit for example, is treated the same as one that ended on its own. In either case, if the session had begun research, its retained work goes on to a peer and a review; a session that only checked for available work and found none ends without a peer or a review. An interrupted peer, review or organizer is replaced by a new session that receives the partial work."),
 # model paragraph (E2)
 ("By default, the first model listed for the peer and review roles differs from the first model listed for the producing roles. Each role's model setting is an ordered list with fallbacks,",
  "By default, the first model listed for the peer and review roles differs from the first model listed for the producing roles. This default is part of the independent judgment described at the start, and it has a limit: each role's model setting is an ordered list with fallbacks,"),
 # relations (A6, D7, F3)
 ("The runner applies each accepted relation in every direction that propositional logic allows, and the frontier shows the result. A relation says that it is impossible for all of its premises to hold while its conclusion fails.",
  "The runner applies each accepted relation in every direction that propositional logic allows, and the frontier shows the result. A relation's premises and conclusion are **outcomes**, that is, proofs or refutations of nodes, and the relation says that it is impossible for all of its premises to hold while its conclusion fails."),
 ("A **route** to the root is a path of relations, each feeding the next and some with several premises, along which a proof of a node contributes to settling the root; such a node is said to be on a route.",
  "A **route** to the root is a chain of relations, branching where a relation has several premises, along which proving a node helps settle the root; such a node is said to be on a route."),
 ("A question is resolved when a published record gives an account of it that the review judges to settle it.", "A question is resolved when a published record gives an account of it that the review judges to answer it."),
 # progress (E3)
 ("Extending the range over which a statement has been checked, without any such change, does not count as progress.",
  "Extending the range over which a statement has been checked, without any such change, does not count as progress. These descriptions inform the sessions' own choices and the reviews' judgments; the runner applies no such filter itself."),
 # two documents (G8)
 ("receive, besides their role guides, two documents in their starting context.", "receive, besides their role guides, two documents in their starting context; in the first run, which began before the documents existed, they reached the sessions as a standing input from 8 November."),
 # first run (D9, D10, G5, G1, C9)
 ("A **parking function** of length n describes n cars arriving one at a time at n parking spots in a row.", "Parking functions of length n arise from n cars arriving one at a time at n parking spots in a row."),
 ("whenever the sequence decreases from one term to the following one is not here", "x"),  # placeholder guard, removed below
]
readme = [p for p in readme if p[1] != "x"]
readme += [
 ("whenever the sequence decreases from one term to the next, the square of the next term is at least the product of the terms on either side of it.",
  "whenever the sequence decreases from one term to the following one, the square of that following term is at least the product of its two neighbours."),
 ("That property was proved on each side of the middle.", "That property was proved directly for the steps at or beyond the middle; for the steps below it, it was derived from the fourth case of the first route, which is where the two routes meet."),
 ("in the exact range of steps that the frontier's statements give; this statement was the last part to be proved. The record that proved it, r5909c9e7, depends on computer-assisted inputs from earlier records:",
  "in the exact range of steps that the frontier's statements give; this statement was the last part to be proved, and its last open premise was closed by record r5909c9e7, which depends on computer-assisted inputs from earlier records:"),
 ("The rule that limits formalization to outcomes bearing on the root was added after this node had been formalized, as the full account explains.", "The rule that limits formalization to outcomes that can reach the root was added after this node had been formalized, as the full account explains."),
 # versions order (B3)
 ("Each version is a snapshot of the directory. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved. Version 3, [10.5281/zenodo.24165415](https://doi.org/10.5281/zenodo.24165415), was taken at 23:25 Korean time on 12 November and deposited at 00:45 on 13 November; it holds 340 records.",
  "Each version is a snapshot of the directory. Version 3, [10.5281/zenodo.24165415](https://doi.org/10.5281/zenodo.24165415), the latest, was taken at 23:25 Korean time on 12 November and deposited at 00:45 on 13 November; it holds 340 records. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved."),
 # language section (A15, G10)
 ("The do-math operator and role guides, the file contracts, the runtime output and this README are in English.", "The do-math operator and role guides, the formats of the files that sessions exchange, the runtime output and this README are in English."),
 ("cite the version you read by its own DOI (version 2 is 10.5281/zenodo.24142218)", "cite the version you read by its own DOI (version 3 is 10.5281/zenodo.24165415)"),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 (PAUSE_OLD, PAUSE_NEW),
 ("and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November). That certification checked", "and the finite verification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November). That verification checked"),
 ("The limit was later proved without any assumption, which the word unconditional in the theorem's name records.", "The limit itself was then proved without assuming the root, which the word unconditional in the theorem's name records."),
 ("each prove both properties independently |", "each prove both properties by separate arguments |"),
 ("Each version is a snapshot of the directory. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two standing inputs of that day (04:54 and 14:15); it holds 300 records, including r5909c9e7, r030ffaeb and r0af7f414, with every review, organization and question published up to that moment. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved. Version 3, [10.5281/zenodo.24165415](https://doi.org/10.5281/zenodo.24165415), was taken at 23:25 Korean time on 12 November and deposited at 00:45 on 13 November; it holds 340 records, including the three published that afternoon and evening.",
  "Each version is a snapshot of the directory. Version 3, [10.5281/zenodo.24165415](https://doi.org/10.5281/zenodo.24165415), the latest, was taken at 23:25 Korean time on 12 November and deposited at 00:45 on 13 November; it holds 340 records, including the three published that afternoon and evening. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two standing inputs of that day (04:54 and 14:15); it holds 300 records, including r5909c9e7, r030ffaeb and r0af7f414, with every review, organization and question published up to that moment. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved."),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 ("| `status` | Read the root state,", "| `status` | Show the root state,"),
 ("| `kill-session <id>` | End the identified session's CLI process; session IDs are in the `status` output.", "| `kill-session <id>` | End the identified session's CLI process and its session host; session IDs are in the `status` output."),
 ("- `explore_every` (default 1): the runner raises", "- `explore_every`: 1, meaning that the runner raises"),
 ("With the two files ready, `init` creates the instance at a new path.", "With the two files ready, `init` creates the instance at a new path; if you want standing inputs to reach every session, submit them between `init` and `start`, as described after the commands."),
]
apply("docs/do-math/running.md", run)

zen = [
 (PAUSE_OLD, PAUSE_NEW),
 ("Records that passed this assessment were published in the knowledge base, where every later session read them, and published records were never changed; later assessments were recorded beside them.",
  "Records that the third session judged worth keeping were published in the knowledge base, each with its assessment, including any claims the assessment did not support; every later session read them. Published records were never changed; later assessments were recorded beside them."),
 ("The state informally proved has qualifications", "The state called informally proved has qualifications"),
 ("in which the rounding error is covered by assumed margins rather than tracked by the arithmetic.", "in which the rounding error is covered by preset margins rather than tracked by the arithmetic."),
 ("and version 1 a snapshot taken on 11 November at 00:19, while the conjecture was still open.", "and version 1 a snapshot taken on 11 November at 00:19 Korean time, while the conjecture was still unresolved."),
 ("both pass through one statement, that the sequence never decreases below its middle index.", "both pass through one statement, that the sequence never decreases over the steps below its middle index, in the exact range the frontier states."),
]
apply("임시/작문/readme-20261112/stage3/zenodo-description.md", zen)
print("reader fixes 6 applied")
