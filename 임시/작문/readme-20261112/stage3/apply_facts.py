"""Fact update of 12 November evening: the two monotonicity properties were proved; counts and Zenodo version 3.

Usage: python -I apply_facts.py <repo_root> <active_pipelines>
"""
import io, os, sys
root, npipe = sys.argv[1], sys.argv[2]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = [
 # lead: name the statement explicitly
 ("The statement comes from a person, called the user in this document,",
  "The statement to be proved or refuted comes from a person, called the user in this document,"),
 # at-a-glance: state of the root
 ("One step relies on two monotonicity properties that are asserted and numerically checked but not proved. |",
  "One step was found on 12 November to rest on two monotonicity properties that a record had asserted without proof; three records proved them that evening, at the same informal level. |"),
 # at-a-glance: evidence
 ("version 2 is [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218). |",
  "version 2 is [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), and version 3, which includes the proofs of 12 November, is being deposited `[placeholder: version 3 DOI]`. |"),
 # lead paragraph 4
 ("Several steps rest on computer-assisted inputs, and one step relies on two monotonicity properties that a record asserts and that its review checked numerically but that no record proves. Nor does a Lean proof",
  "Several steps rest on computer-assisted inputs. One step was found on 12 November to rest on two monotonicity properties that a record had asserted and that its review had only checked numerically; the sessions were asked to prove them, and three records did so that evening, at the same informal level as the rest. Nor does a Lean proof"),
 # first run: the gap paragraph
 ("One step on those routes is known to be unproved. Record r030ffaeb reads a lower bound from a table of values, and the table gives that bound only if two monotonicity properties hold. The record asserts the properties, its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points not yet rigorous, and no record proves them. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and a standing input of that day asks the sessions to prove the two properties before any other work. Until a record proves them, the root's state rests on this step as the reviews accepted it.",
  "One step on those routes was for a time unproved. Record r030ffaeb reads a lower bound from a table of values, and the table gives that bound only if two monotonicity properties hold. The record asserted the properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points not yet rigorous. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and a standing input at 14:15 Korean time asked the sessions to prove the two properties before any other work. The first proof, record rfc693208, was published at 16:12 that afternoon with all thirteen of its claims supported by review; two further records, r0e82912d and rc56f637b, gave independent derivations of the same properties that evening. The gap is closed at the level the rest of the routes have, by proofs that AI review sessions accepted."),
 # limits
 ("The result has limits beyond that gap. Every review was an AI session, and no person has reviewed the records as a referee would. Several records on the routes rest on binary64 computations with error models assumed in advance, so a reader who does not accept those models should treat what depends on them as unproved. No Lean work on the routes to the root has been published.",
  "The result has limits. Every review was an AI session, and no person has reviewed the records as a referee would. Several records on the routes rest on binary64 computations with error models assumed in advance, so a reader who does not accept those models should treat what depends on them as unproved. No Lean work on the routes to the root has been published."),
 ("The research is not finished: at 17:45 Korean time on 12 November the run had launched 1,227 sessions and published 337 records, the frontier held 108 nodes, and ten pipelines were still working on nodes and questions beside the root.",
  "The research is not finished: at 23:15 Korean time on 12 November the run had launched 1,237 sessions and published 340 records, the frontier held 108 nodes, and %s pipelines were still working on nodes and questions beside the root." % npipe),
 # evidence paragraph: version 3
 ("while the root was still unresolved. To check the result,",
  "while the root was still unresolved. A third version, taken after the three records of 12 November were published, is being deposited: `[placeholder: version 3 DOI, compression time and record count]`. To check the result,"),
 # placeholder: manuscript
 ("with the gap described above marked as open until the sessions close it]`",
  "with the step that the sessions proved on 12 November written out from the three records that proved it]`"),
]
apply("README.md", readme)

doc = [
 ("as of 17:45 Korean time on 12 November 2026; the run continues.",
  "as of the evening of 12 November 2026; the run continues. The size table below is a snapshot from 17:45 Korean time that day, and the section on the step found unproved records what happened after it."),
 ("## A step known to be unproved\n\nOne step of those routes is known to be unproved.",
  "## A step found unproved and proved the same day\n\nOne step of those routes was found to be unproved on 12 November and was proved that evening."),
 ("The record asserts these two properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points it judged not yet rigorous. The review did not write the missing proof; it judged the numerical check sufficient evidence for a computer-assisted claim and said so, and whether that judgment was right is open to any reader of the record.",
  "The record asserted these two properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points it judged not yet rigorous. The review did not write the missing proof; it judged the numerical check sufficient evidence for a computer-assisted claim and said so, and whether that judgment was right is open to any reader of the record."),
 ("No record proves the two properties. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and at 14:15 Korean time a standing input asked sessions launched afterwards to put proving the two properties before any other work; it assigned the work to no session, and no concern has been filed against the record. Until a record proves them, the root's state rests on this step as the reviews accepted it.",
  "The author and an operator session found the gap on 12 November while writing a manuscript from the records, and at 14:15 Korean time a standing input asked sessions launched afterwards to put proving the two properties before any other work; it assigned the work to no session, and no concern was filed against the record. At least three attempts took the request up independently. The first proof, record rfc693208, was published at 16:12 Korean time: it proves that the escape envelope used by the table is non-increasing in its y variable for all k ≥ 6600, that the six elementary pieces are each monotone in k, corrects a gap in the record's Lemma H(ii), and checks exactly, reading the stored binary64 values as rationals, that the stored table itself is strictly decreasing. Its review supported all thirteen of its claims. Record r0e82912d, published at 17:36, gives an independent second proof of the same two properties through a different normalization, in which the leading terms of numerator and denominator cancel and a margin of 3/2 remains, and record rc56f637b, published at 18:18, gives a third derivation and shows that it matches the first two theorem by theorem. All three were accepted by AI review sessions, so the step now has the same informal standing as the rest of the routes, and the root's state continues to rest on the reviews' judgment."),
 ("One step on the routes is asserted and numerically checked but not proved, as described above. No Lean work",
  "The step found unproved on 12 November was proved the same day by three records, as described above, at the informal level. No Lean work"),
 ("The research is not finished: at 17:45 Korean time on 12 November, ten pipelines were active, working on unresolved nodes and unresolved questions beside the root.",
  "The research is not finished: at 23:15 Korean time on 12 November the run had launched 1,237 sessions and published 340 records in 426 publication commits, and %s pipelines were active, working on unresolved nodes and unresolved questions beside the root." % npipe),
 ("while the root was still unresolved.\n\nTo check the result,",
  "while the root was still unresolved. A third version, taken after the three records of 12 November were published, is being deposited: `[placeholder: version 3 DOI, compression time and record count]`.\n\nTo check the result,"),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)
print("facts applied")
