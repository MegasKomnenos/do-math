"""Fixes from 사실대조_3단계 (U1-U13, F1-F2, Z1-Z2)."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = [
 # U1, U2: the lead's second sentence
 ("The sessions share nothing but a knowledge base: each is a new Claude Code or Codex conversation that knows nothing of the others, and what one session proves, writes up or assesses is published there as a record for later sessions to read.",
  "The sessions have no contact with one another. Each is a new Claude Code or Codex conversation that knows nothing of the others; what a session produces is handed on as files, and what survives review is published as a record in a shared knowledge base for every later session to read."),
 # U3: operator operates the run
 ("An AI conversation called the operator prepares the statement and the settings on the user's behalf, and a program called the runner",
  "An AI conversation called the operator prepares the statement and the settings and operates the run on the user's behalf, and a program called the runner"),
 # U6: first stage covers refutation and formalization
 ("First, a session works on the problem: it tries to prove a statement or understand some feature of the problem, and it keeps all of its work,",
  "First, a session works on the problem: it tries to prove or refute a statement, to understand some feature of the problem, or to turn an accepted proof into Lean, and it keeps all of its work,"),
 # U4, U5: publication decision; finding by a review session, defect or confirmation
 ("The record is then published with that assessment attached, and it is never edited afterwards. If a later session finds a mistake, it appends a finding to the record, so that the original claim and what later became of it remain visible together.",
  "If the review judges the work worth keeping, the record is published with that assessment attached, and it is never edited afterwards. If a later review session finds a mistake in it or confirms one of its results, it appends a finding to the record, so that the original claim and what later became of it remain visible together."),
 # U7, U8, U9
 ("The first is continuity. A run lasts for days and passes through hundreds of conversations, none of which remembers the one before, so the records are the only memory the research has, and they must carry everything that later sessions will need. The second is independent judgment. The session that has just produced an argument is poorly placed to notice what it has missed, so each piece of work is assessed by a session that took no part in producing it.",
  "The first is continuity. A run can last for days and pass through hundreds of conversations, none of which remembers the one before, so the records are the research's memory from one session to the next, and they must carry everything that later sessions will need. The second is independent judgment. Each piece of work is assessed by a session that took no part in producing it, so that no session certifies its own work."),
 # U10
 ("The knowledge base, with every record and every assessment, is public on Zenodo.", "The knowledge base is public on Zenodo."),
 # U11
 ("and version 3, which includes the proofs of 12 November, is being deposited `[placeholder: version 3 DOI]`. |",
  "and version 3 is being deposited `[placeholder: version 3 DOI]`. |"),
 # U12
 ("The second route shows that a weaker property suffices: a log-concavity required only at steps where the sequence has already started to decrease, which implies that the sequence cannot rise again once it has started to fall.",
  "The second route shows that a conditional log-concavity suffices: log-concavity required only at steps where the sequence has already started to decrease, which implies that the sequence cannot rise again once it has started to fall."),
 # U13
 ("and the section counts as occupied until the work has passed through peer and review and become a record.",
  "and the section counts as occupied until a peer and a review have processed the work."),
]
apply("README.md", readme)
for f in ["임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

apply("docs/do-math/first-run-parking-unimodality.md", [
 # F1
 ("The second route shows that a weaker property than unimodality suffices for the root: a log-concavity required only at steps where the sequence has already started to decrease, namely that",
  "The second route shows that a property weaker than full log-concavity suffices for the root: log-concavity required only at steps where the sequence has already started to decrease, namely that"),
 # F2
 ("A third version, taken after the three records of 12 November were published, is being deposited:",
  "A third version, taken late on 12 November, is being deposited:"),
])

apply("임시/작문/readme-20261112/stage3/zenodo-description.md", [
 # Z1, Z2
 ("The sessions share nothing but this knowledge base: each is a new conversation that knows nothing of the others, and what one session proves, writes up or assesses is published here as a record for later sessions to read.",
  "The sessions have no contact with one another. Each is a new conversation that knows nothing of the others; what a session produces is handed on as files, and what survives review is published here as a record for every later session to read."),
])
print("fact fixes applied")
