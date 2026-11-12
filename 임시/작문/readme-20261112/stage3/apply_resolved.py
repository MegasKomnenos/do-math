"""A resolved problem is not narrated in the current-state documents. Only the intervention timeline keeps the event."""
import io, os, sys, re
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    return t

apply("README.md", [
 (" One step was found on 12 November to rest on two monotonicity properties that a record had asserted without proof; three records proved them that evening, at the same informal level. |", " |"),
 (" One step was found on 12 November to rest on two monotonicity properties that a record had asserted and that its review had only checked numerically; the sessions were asked to prove them, and three records did so that evening, at the same informal level as the rest. Nor does a Lean proof", " Nor does a Lean proof"),
 ("One step on those routes was for a time unproved. Record r030ffaeb reads a lower bound from a table of values, and the table gives that bound only if two monotonicity properties hold. The record asserted the properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points not yet rigorous. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and a standing input at 14:15 Korean time asked the sessions to prove the two properties before any other work. The first proof, record rfc693208, was published at 16:12 that afternoon with all thirteen of its claims supported by review; two further records, r0e82912d and rc56f637b, gave independent derivations of the same properties that evening. The gap is closed at the level the rest of the routes have, by proofs that AI review sessions accepted.\n\n", ""),
 (" is being written, with the step that the sessions proved on 12 November written out from the three records that proved it]`", " is being written]`"),
])

p = os.path.join(root, "docs/do-math/first-run-parking-unimodality.md")
t = io.open(p, encoding="utf-8").read()
m = re.search(r"\n## A step found unproved and proved the same day\n.*?(?=\n## )", t, flags=re.S)
assert m, "section"
t = t[:m.start()] + t[m.end():]
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
apply("docs/do-math/first-run-parking-unimodality.md", [
 (" The size table below is a snapshot from 17:45 Korean time that day, and the section on the step found unproved records what happened after it.", " The size table below is a snapshot from 17:45 Korean time that day."),
 ("| 12 November, 14:15 | Standing input | Prove the two monotonicity properties of record r030ffaeb before any other work |",
  "| 12 November, 14:15 | Standing input | Prove the two monotonicity properties that the table used by record r030ffaeb depends on, before any other work; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove them |"),
 ("Every review was an AI session; no person has reviewed the records as a referee would, and the author's reading of them while writing a manuscript is how the gap above was found. Several records",
  "Every review was an AI session; no person has reviewed the records as a referee would. Several records"),
 (" The step found unproved on 12 November was proved the same day by three records, as described above, at the informal level. No Lean work", " No Lean work"),
])

apply("임시/작문/readme-20261112/stage3/zenodo-description.md", [
 (" On 12 November one record on the routes (r030ffaebcd164eb492cc4215ce1c2e56) was found to rely on two monotonicity properties that it asserted and that its review had checked numerically but that no record proved; the instance was asked to prove them, and this version holds the three records that did so that evening, rfc69320810634cf7a6bc05fc449d8fc7, r0e82912d13f3449c9b5efd7fed14e5bc and rc56f637b63e54cd08939cfe00bb4bfde, each accepted by an AI review session at the same informal level as the rest of the routes.", ""),
])
print("resolved-problem narration removed")
