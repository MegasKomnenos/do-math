import io, re, sys
p = sys.argv[1]
t = io.open(p, encoding="utf-8").read()
def rep(old, new, count=1):
    global t
    assert t.count(old) == count, ("count", t.count(old), old[:70])
    t = t.replace(old, new)
# 1-1-a / 1-1-b: restore role classification by name; explorer cell; review cell
rep("Six roles do the work, and the runner launches a fresh session for each piece of it. Three roles produce mathematics, two process what the producing roles leave, and one keeps the knowledge base navigable. A producing session together with its peer and review is a **pipeline**.",
    "Six roles do the work, and the runner launches a fresh session for each piece of it. Three roles produce mathematics: an **attempt** tries to settle a node, an **explorer** works to understand the problem, and a **formalizer** constructs a Lean proof. Two roles process what the producing roles leave: a **peer** develops it into a record, and a **review** assesses the record. An **organizer** keeps the knowledge base navigable. A producing session together with its peer and review is a **pipeline**.")
for r in ["attempt", "explorer", "formalizer", "peer", "review", "organizer"]:
    rep("| **%s** |" % r, "| %s |" % r)
rep("| explorer | The knowledge base; it occupies a question to understand | Its retained work on that question |",
    "| explorer | The knowledge base; it works to understand one question about the problem | Its retained work on that question |")
rep("| review | The candidate and the producing session's retained work | The assessment: claim statuses, publication decision, concerns and findings |",
    "| review | The candidate and the producing session's retained work | Its assessment and feedback: claim statuses, a publication decision and any concerns |")
# 4-a: bridge between the frontier's two levels and computer-assisted steps
rep("and counts a computer-assisted proof as informal.", "and counts a proof with computer-assisted steps as informal.")
rep('"Informal" here means that the argument is written in ordinary mathematical language and was checked by an AI review session',
    '"Informal" here means that the argument is written in ordinary mathematical language, with any computer-assisted steps stated as such, and was checked by an AI review session')
rep("A finite verification proves the finite claim it covers and nothing beyond it.",
    "A finite verification proves the finite claim it covers and nothing beyond it. A proof with computer-assisted steps stands at the informal level on the frontier.")
# 1-2-a / 1-2-b: 'does not mean' cells
rep("| Rigorous beyond the arithmetic used; binary64 steps depend on an assumed error model |",
    "| Anything beyond the range the computation covers; for a binary64 step, proof independent of the assumed error model |")
rep("| Anything about relations derived from it, which stay informal |",
    "| Formal standing for what the frontier derives from it through relations, which stays informal |")
# 3-a, 3-b, 3-c, 3-d and related pronouns
rep("While it chooses, it holds the node's **lease**", "While an attempt chooses, it holds the node's **lease**")
rep("\n\nIt needs Lean 4 in every case,", "\n\nThe runtime needs Lean 4 in every case,")
rep("is treated the same as one that ended. Whenever the session has begun research, its retained work then goes on to the processing roles;",
    "is treated the same as one that ended. In either case, if the session had begun research, its retained work goes on to the processing roles;")
rep("An attempt has no time cap. When the CLI process", "A session ends on its own judgment, after being asked to reconsider. An attempt has no time cap. When the CLI process")
rep("an inequality between two counts of configurations in that part whose exact statement is in the frontier;",
    "an inequality, stated exactly in the frontier, between two counts of configurations where n lies between 2ℓ and about 2ℓ^(3/2);")
rep("The third and fourth cases were in turn proved", "The third and fourth cases of the first route were in turn proved")
rep("No record proves the properties.", "No record proves the two properties.")
rep("the Lean development that led to this one, and all were published", "the Lean development that led to this theorem, and all were published")
rep("That state comes with qualifications.", "The informal proof of the root comes with qualifications.")
rep("Whether the mechanisms described in the previous sections, such as sections,",
    'Whether the mechanisms described under the heading "How the research is organized", such as sections,')
# 1-4-a and timeline recommendations
rep("| 6 November, evening | Settings | Peer and review moved to Claude Opus 5.5 as first choice; the same arrangement became the default |",
    "| 6 November, evening | Settings and software | Peer and review moved to Claude Opus 5.5 as first choice; do-math's default was changed at the same time so that the assessing roles prefer a different model from the producing roles |")
rep("| 9 November | Software | Questions on the frontier, with explorers occupying them |", "| 9 November | Software | Questions on the frontier |")
rep("| 9 November | Standing input and operator action | Formalization paused; the five formalizations in progress ended without peer or review |",
    "| 9 November | Standing input | Formalization paused so that the research could finish first |\n| 9 November | Sessions ended | The five formalizations in progress ended without peer or review |")
# 2-a: own subheading for the two documents
rep("\n\nAttempt, explorer, peer, review and organizer sessions also receive two documents",
    "\n\n### Two documents on research and writing\n\nAttempt, explorer, peer, review and organizer sessions also receive two documents")
# 2-b: move the top-level directories paragraph out of the record section
m = re.search(r"\n\n(`events/` holds one file per publication[^\n]*)\n", t)
assert m, "events paragraph"
para = m.group(1)
t = t.replace("\n\n" + para + "\n", "\n", 1)
rep("its `proofs` object lists every supported proof with its claims and premises.\n",
    "its `proofs` object lists every supported proof with its claims and premises.\n\n" + para + "\n")
# headings
for old, new in [
    ("### How an attempt chooses and declares its work", "### The choice of work: frontier, sections and leases"),
    ("### How a session ends", "### The end of a session"),
    ("### From retained work to a published record", "### Peer, review and the published record"),
    ("### Questions and what counts as progress", "### Questions and progress"),
    ("### The run\n", "### Setup and size of the run\n"),
    ("### The one Lean proof\n", "### The one Lean proof and the formalization pause\n"),
    ("### What the user and the operator changed during the run", "### Interventions during the run"),
    ("### Where the evidence is", "### The published evidence"),
    ("### Not yet public", "### Artifacts not yet public"),
    ("### The top-level files\n", "### The top-level files and directories\n"),
    ("### What a run does on your machine", "### Permissions, caps and outbound traffic"),
]:
    rep(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("edits applied")
