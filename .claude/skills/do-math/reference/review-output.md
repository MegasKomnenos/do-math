# Writing review findings

Your review leaves two connected outputs. The feedback document explains the examination and its mathematical grounds for later readers. `output/assessment.json` identifies the claims and decisions the runner must apply. The structured assessment should point into that explanation, so each recorded judgment can be understood in its actual scope.

Write both outputs in your own directory. The candidate or published records you assess remain unchanged. The next sections explain the candidate assessment, its formal-evidence attachment, and findings about previously published work. A comprehensive review uses those findings without making a new candidate publication decision.

## Candidate assessment

The assessment has these fields:

| Field | Content |
|---|---|
| `publish` | Boolean: whether useful material should be retained as a published record. |
| `reason` | The reason for publication or exclusion. |
| `index_assessment` | Short assessment displayed beside the immutable candidate description. |
| `feedback` | Relative path to the full feedback document. |
| `claims` | Exactly one `{claim, status, reason}` for each candidate claim ID. Status is `supported`, `unsupported` or `undetermined`. |
| `nodes` | Exactly one `{proposal, node, reason}` for each proposed node. `node` is the proposal ID when admitted, an existing node ID when identified with that node, or null when declined. |
| `relations` | Exactly one `{proposal, accepted, reason}` for each relation. `accepted` is Boolean. |
| `solutions` | Exactly one `{proposal, level, reason}` for each solution. `level` is `none`, `informal` or `formal`. |
| `glossary_approved` | Boolean: approval of the candidate's local glossary, including the consistency check of globally flagged entries. |
| `glossary` | Local terminology you introduce to explain your own assessment. Each entry has `id`, `name`, `definition`, and optional `symbol`, using the local entry format in [Record format](record-format.md). Include the definitions and their use in your feedback; omit this field or use an empty array when you introduce no terms. These entries explain your assessment and do not create new mathematical proof claims. |
| `concerns` | New concerns about identified claims, or an empty array. |
| `findings` | Findings on existing evidence or concerns, or an empty array. |

An accepted relation or solution cites a supported claim. Admitting a node requires a supported connection through an accepted relation to the existing research. A solution assessment can include `formal_dependencies`, replacing the candidate's list with the signed nodes actually required by the accepted argument. Assess every proposal, using null, false or `none` for those not accepted.

The feedback covers important mathematical assertions in the body as well as the structured list. Explain missing source content, defects, restrictions, unperformed checks and valuable supported work. The structured judgment does not limit the mathematical scope of review to what the peer happened to list.

If `publish` is false, accept no nodes, relations or solutions, and report no concerns or findings through that excluded candidate. An excluded candidate cannot change shared mathematical state, and the transport check rejects an exclusion whose assessment contains any of these. Preserve the reason in the feedback. Useful diagnostic mathematics is usually grounds to publish with qualifications. The runner retains that completed exclusion as an operational outcome. It finishes the producer's peer/review processing, releases the attempt's occupied nodes or completes the exploration cycle as applicable.

## Evidence for a formal solution

For `level: "formal"`, add `formal_check`:

```json
{
  "job": "<your finished broker job or build ID>",
  "theorem": "<exact candidate theorem name>",
  "alignment": "matches",
  "reason": "Explain correspondence to the exact node or its negation.",
  "axioms": ["propext", "Classical.choice", "Quot.sound"],
  "source_hashes": {"lean/Proof.lean": "<SHA-256 of the final candidate file>"},
  "source_files": {"lean/Proof.lean": "work/check/Proof.lean"}
}
```

These are placeholders, not evidence. `axioms` must be the actual list printed for this target, possibly empty. The job belongs to this reviewing session and must have completed successfully. For a build, compile the targets freshly with `--fresh-targets`. The target's name must match the candidate solution's `lean.theorem`.

For every file listed in `lean.sources`, `source_hashes` records the SHA-256 of the candidate bytes and `source_files` points to the corresponding working copy relative to your session directory. The working copy must preserve the candidate bytes; only `#print axioms` lines may be appended. The broker records the source identity used in the compile. Python's `hashlib.sha256(path.read_bytes()).hexdigest()` obtains the hash.

Copy the sources into a working directory with the same module layout. Append the audit command to the target file and run the broker. Then inspect the actual output, compare the theorem with the node, and record the evidence. The structural checker confirms the job ownership, successful fresh compile, source identities and printed axiom list. Your mathematical judgment establishes correspondence and sufficiency. The runner preserves the referenced broker evidence with the published assessment.

If compilation cannot be completed, do not issue formal acceptance. An informal proof can still be supported with its remaining formal work made explicit. If the source itself fails or its theorem differs, explain the specific defect rather than treating every kind of failed check as a false mathematical proposition.

## Concerns and later findings

A new concern has `id`, `targets`, `reason`, and `evidence`. Targets are `{record, claim}` references; a candidate review can use `record: "self"` for its candidate's claims. The reason identifies what is questioned, and the evidence tells another researcher how to inspect it. Publication gives the concern a stable ID `<publication-id>/<local-id>` and creates comprehensive review work.

A finding has `concerns` (the existing concern IDs it addresses), `status` (`cleared`, `confirmed` or `undetermined`), and `reason`. It may also have:

| Field | Effect |
|---|---|
| `invalidates` | Claim references whose offered support is withdrawn. |
| `validates` | Existing claim references whose support this review establishes or restores. |
| `clears` | Claim references whose use is sound despite the named concern. |
| `cleared_uses` | Exact relation applications cleared despite a concern: `{relation, premise_proofs}`. Use the relation and proof IDs from the research state, in the relation's premise order. |
| `dependency_updates` | `{proof, dependencies, reason}` entries correcting the formal dependencies of an existing proof route. |

Write only consequences supported by your examination of the evidence. Clearing one use is narrower than clearing the original claim or the whole concern. A confirmed defect can withdraw one argument while another argument continues to support the same node. The feedback explains the actual uses and what remains unresolved.

The `proofs` object in `knowledge/state.json` lists the currently supported proof routes. A direct solution has ID `<record-id>/<solution-id>`; an established application of a relation has ID `<record-id>/<relation-id>`. Each entry identifies its node, outcome and supporting claims, and an inferred application lists `premise_proofs` in premise order. Use those exact IDs in a clearance. The separate `relations` object contains the reviewed implication statements, including relations whose premises are not yet solved.

When a candidate review that publishes its candidate finds a defect in an earlier record, it can report a concern and its established findings. A withdrawal without a named existing concern creates a comprehensive review of its broader consequences. Do not claim that those consequences have all been assessed merely because the original defect was found.

## Comprehensive assessment

For a comprehensive assignment, `assessment.json` contains `feedback`, `index_assessment`, `findings`, and optional `concerns`. It has no candidate publication decision. Address the assigned concerns and requested evidence in the feedback, following the actual uses described in the role guide. The runner publishes this assessment directly as a review record and attaches its findings to their sources. It does not require another peer/review cycle for your judgment to take effect.

If you introduce notation needed to explain your assessment, add a `glossary` array in the local entry format of [Record format](record-format.md), and use it in the feedback. No entries are needed when you introduce no terms. These local definitions explain your output; they do not create new mathematical proof claims.

Run the transport check on your session directory before finishing. A completed assessment can state uncertainty; an interrupted assessment has not finished the stage. The runner preserves partial work and supplies it, with the original assignment, to a replacement reviewer.
