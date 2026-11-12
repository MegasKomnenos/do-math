import io, os, sys
root = sys.argv[1]
def apply(path, pairs, optional=False):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        if optional and n == 0: continue
        assert n == 1, (path, n, old[:60])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
readme_pairs = [
 # 1-1
 ("gives the run's setup, its size, both routes to the root step by step, and every intervention",
  "gives the run's setup, its size, both routes to the root in outline, and every intervention"),
 # 1-2
 ("One route splits a failure of unimodality into four cases by the positions of the offending descent and ascent around the middle index ⌈n/2⌉ and proves each case; the other shows that a conditional log-concavity suffices for the root and proves it on each side of the middle.",
  "One route splits a failure of unimodality into four cases by the positions of the offending descent and ascent around the middle index ⌈n/2⌉, and each case has a reviewed informal proof; the other shows that a conditional log-concavity suffices for the root, and that condition was settled on each side of the middle."),
 # 1-4
 ("The author found the gap on 12 November while writing a manuscript", "The author and an operator session found the gap on 12 November while writing a manuscript"),
 # 3-1, 3-2
 ("accepted by an AI review session. No person has reviewed the records. One step relies on two monotonicity properties that are asserted and numerically checked but not proved. |",
  "accepted by an AI review session. No person has reviewed the records as a referee would. Several steps rest on computer-assisted inputs, some in binary64 with error models assumed in advance. One step relies on two monotonicity properties that are asserted and numerically checked but not proved. |"),
 # 2-3
 ("Then create the instance at a path outside this repository,",
  "This keeps the default models, which put Codex first and Claude second for every role and the reverse for peer and review; with only Claude Code installed, give the `models` list and the `roles` entries for peer and review Claude models only, as the running guide shows.\n\nThen create the instance at a path outside this repository,"),
 # 4-1, 4-2, 4-3
 ("The diagram shows one pipeline and the organizer's loop. The runner launches every box as a fresh session; the arrows carry files, not conversation.",
  "The diagram shows one pipeline and the organizer's loop. Every box except the knowledge base and the record is a session that the runner launches as a fresh conversation; the arrows carry files from one session to the next, and no two sessions converse."),
 ('  KB -- "read; the session chooses its own work" --> P',
  '  KB -- "read; an attempt or explorer chooses its own work, a formalizer receives a node whose informal proof review has accepted" --> P'),
]
apply("README.md", readme_pairs)
apply("임시/작문/readme-20261112/stage2/firstrun_short.md", readme_pairs[:3])
apply("임시/작문/readme-20261112/stage2/lead.md", readme_pairs[3:4])
apply("임시/작문/readme-20261112/stage2/running_short.md", readme_pairs[4:5])
apply("임시/작문/readme-20261112/stage2/mermaid.md", readme_pairs[5:7])
# 5-2
apply("docs/do-math/running.md", [
 ("in the skill is the complete reference for every setting and state.\n\n",
  "in the skill is the complete reference for every setting and state. Terms such as runner, broker, session host, frontier, standing input, retained work and comprehensive review are defined in the README under \"How the research is organized\" and \"What counts as established\".\n\n")])
print("fixes 3 applied")
