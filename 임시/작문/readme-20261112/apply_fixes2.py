import io, sys
p = sys.argv[1]
t = io.open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    assert t.count(old) == 1, ("count", t.count(old), old[:70])
    t = t.replace(old, new)
# 1: drop the general claim about session endings; return to the old first sentence
rep("A session ends on its own judgment, after being asked to reconsider. An attempt has no time cap.", "An attempt has no time cap.")
# 2: kind name as a noun phrase
rep("| 9 November | Sessions ended | The five formalizations", "| 9 November | Session termination | The five formalizations")
# 3: computer-assisted proofs are proofs with such steps
rep("The reviews in the first run accepted steps of the second kind as computer-assisted proofs and named the dependence in their assessments;",
    "The reviews in the first run accepted proofs with steps of the second kind as computer-assisted proofs and named the dependence in their assessments;")
# 4: one 'in the frontier', and the range attached to the inequality
rep("The last open premise on the routes was one node, named pair-beats-capped-threshold in the frontier, an inequality, stated exactly in the frontier, between two counts of configurations where n lies between 2ℓ and about 2ℓ^(3/2);",
    "The last open premise on the routes was one node, pair-beats-capped-threshold, whose exact statement in the frontier is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2);")
# 5: tense
rep("In either case, if the session had begun research,", "In either case, if the session has begun research,")
# 6: compare model with model
rep("so that the assessing roles prefer a different model from the producing roles |",
    "so that the assessing roles prefer a model different from the one the producing roles prefer |")
# 7: what 'also' adds to
rep("Attempt, explorer, peer, review and organizer sessions also receive two documents in their starting context,",
    "Besides their role guides, attempt, explorer, peer, review and organizer sessions receive two documents in their starting context,")
# recommendation: name records/ among the top-level directories
rep("`events/` holds one file per publication with its time,",
    "`records/` holds one directory per record, described below. `events/` holds one file per publication with its time,")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("fixes 2 applied")
