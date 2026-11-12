"""Zenodo part of the second reader round (the README/doc parts of apply_read2.py already ran)."""
import io, os, sys
root = sys.argv[1]
PAUSE_NEW = "so that the sessions could finish the informal mathematics before formalization resumed"
p = os.path.join(root, "임시/작문/readme-20261112/stage3/zenodo-description.md")
t = io.open(p, encoding="utf-8").read()
pairs = [
 ("together with the index, frontier and glossary derived from them.", "together with the index, the frontier (the list of statements the research tracked, with their states) and the glossary derived from them."),
 ("and what survives review is published here as a record for every later session to read.",
  "and what survives review is published as a record in the instance's knowledge base, of which this archive is a copy, for every later session to read."),
 ("one worked on the problem, a second read everything the first left behind", "one worked on the problem, trying to prove or refute a statement, to understand some feature of the problem or to turn an accepted proof into Lean; a second read everything the first left behind"),
 ("The term is do-math's own and claims less than the words may suggest: it means that along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session.",
  "The term is do-math's own, and it means less than the words may suggest: on the two routes that lead from statements proved in earlier records to the conjecture itself, every record and every implication had been accepted by an AI review session. The two routes are not independent confirmations; both pass through one statement, that the sequence never decreases below its middle index."),
 ("The state has qualifications that a reader should know before relying on it. Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, and a reader who does not accept such a model should treat what depends on it as unproved.",
  "This state has qualifications that a reader should know before relying on it. Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, the conjecture's informal proof depends on them, and a reader who does not accept such a model should treat the conjecture as unproved."),
 ("The conjecture has no Lean proof, because the user paused formalization on 9 November so that the research could finish first. One necessary condition of the conjecture does have a Lean proof, whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7).",
  "The conjecture has no Lean proof; the user, the person who started the run, paused formalization on 9 November " + PAUSE_NEW + ". One necessary condition of the conjecture has a Lean proof, whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7); its proof leaves the conjecture open."),
 ("`frontier.md` lists the nodes, the exact statements the research tracked, with the conjecture first among them;",
  "`frontier.md` lists the nodes, that is, the exact statements the research tracked, with the conjecture first among them;"),
 ("The standing inputs, the instructions that the user gave to the sessions during the run, and the sessions' own conversations are not part of `knowledge/`; the repository's first-run document lists the inputs.",
  "Two things are not part of `knowledge/`: the standing inputs, that is, the instructions the user gave to the sessions during the run, and the sessions' own conversations. The repository's first-run document (docs/do-math/first-run-parking-unimodality.md) lists the inputs."),
]
for old, new in pairs:
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("zenodo fixes applied")
