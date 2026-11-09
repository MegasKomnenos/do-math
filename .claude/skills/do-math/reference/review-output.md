# Writing review findings

Your review leaves two connected outputs. The feedback document explains the examination and its mathematical grounds for later readers. `output/assessment.json` identifies the claims and decisions the runner must apply. The structured assessment should point into that explanation, so each recorded judgment can be understood in its actual scope.

Write both outputs in your own directory. The candidate or published records you assess remain unchanged. The next sections explain the candidate assessment, its formal-evidence attachment, and findings about previously published work. A comprehensive review uses those findings without making a new candidate publication decision.

## Candidate assessment

The assessment has these fields:

| Field | Content |
|---|---|
| `publish` | Boolean: whether useful material should be retained as a published record. |
| `reason` | The reason for publication or exclusion. |
| `index_assessment` | Short assessment displayed beside the immutable candidate description: the supported scope, the limitations a reader needs, and what the record contributed to the research. |
| `feedback` | Relative path to the full feedback document. |
| `claims` | Exactly one `{claim, status, reason}` for each candidate claim ID. Status is `supported`, `unsupported` or `undetermined`. |
| `nodes` | Exactly one `{proposal, node, reason}` for each proposed node. `node` is the proposal ID when admitted, an existing node ID when identified with that node, or null when declined. |
| `relations` | Exactly one `{proposal, accepted, reason}` for each relation. `accepted` is Boolean. |
| `solutions` | Exactly one `{proposal, level, reason}` for each solution. `level` is `none`, `informal` or `formal`. |
| `questions` | Exactly one `{proposal, verdict, reason}` for each proposed question. `verdict` is `admitted`, `declined` or `revise`; a declined duplicate also names the existing question in `duplicate_of`. Omit the field or use an empty array when the candidate proposes none. |
| `question_resolutions` | Exactly one `{proposal, resolved, reason}` for each proposed resolution. `resolved` is Boolean. Omit the field or use an empty array when the candidate proposes none. |
| `glossary_approved` | Boolean: approval of the candidate's local glossary, including the consistency check of globally flagged entries. |
| `glossary` | Local terminology you introduce to explain your own assessment. Each entry has `id`, `name`, `definition`, and optional `symbol`, using the local entry format in [Record format](record-format.md). Include the definitions and their use in your feedback; omit this field or use an empty array when you introduce no terms. These entries explain your assessment and do not create new mathematical proof claims. |
| `concerns` | New concerns about identified claims, or an empty array. |
| `findings` | Findings on existing evidence or concerns, or an empty array. |

An accepted relation or solution cites a supported claim. Admitting a node requires a supported connection through an accepted relation to the existing research. A solution assessment can include `formal_dependencies`, replacing the candidate's list with the signed nodes actually required by the accepted argument. Assess every proposal, using null, false or `none` for those not accepted.

`declined` and `revise` record two different judgments behind a refusal, which later peers read differently; the role guide explains when each applies and what its reason says. An accepted resolution requires the cited claim to be supported; its reason says why the account settles the question rather than part of it.

The feedback covers important mathematical assertions in the body as well as the structured list. Explain missing source content, defects, restrictions, unperformed checks and valuable supported work. The structured judgment does not limit the mathematical scope of review to what the peer happened to list.

If `publish` is false, accept no nodes, relations, solutions, questions or resolutions, and report no concerns or findings through that excluded candidate. An excluded candidate cannot change shared mathematical state, and the transport check rejects an exclusion whose assessment contains any of these. Preserve the reason in the feedback. Useful diagnostic mathematics is usually grounds to publish with qualifications. The runner retains that completed exclusion as an operational outcome. It finishes the producer's peer/review processing and ends the occupancy its pipeline held: the sections recorded for its producer and peers, including a formalizer's assigned whole node, or the exploration's question.

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

Copy the sources into a working directory with the same module layout. Append the audit command to the target file and run the broker. Then inspect the actual output, compare the theorem with the node, and record the evidence. The transport check confirms the job ownership, successful fresh compile, source identities and printed axiom list. Your mathematical judgment establishes correspondence and sufficiency. The runner preserves the referenced broker evidence with the published assessment.

If compilation cannot be completed, do not issue formal acceptance. An informal proof can still be supported with its remaining formal work made explicit. If the source itself fails or its theorem differs, explain the specific defect rather than treating every kind of failed check as a false mathematical proposition.

## Concerns and later findings

A new concern has `id`, `targets`, `reason`, and `evidence`. Targets are `{record, claim}` references; a candidate review can use `record: "self"` for its candidate's claims. The reason identifies what is questioned, and the evidence tells another researcher how to inspect it. Publication gives the concern a stable ID `<publication-id>/<local-id>` and creates comprehensive review work. It does not change the standing of the claims it names; only a finding does.

A finding has `concerns` (the existing concern IDs it addresses), `status` (`cleared`, `confirmed` or `undetermined`), and `reason`. The status records your judgment on the named concerns and is shown beside them; the standing of claims changes only through the arrays below, so a status alone leaves every claim as it was. It may also have:

| Field | Effect |
|---|---|
| `invalidates` | Claim references whose offered support is withdrawn. |
| `validates` | Existing claim references whose support this review establishes or restores. |
| `dependency_updates` | `{proof, dependencies, reason}` entries correcting the formal dependencies of an existing proof route. |

Write only consequences supported by your examination of the evidence. A pending concern leaves the questioned claim in force; a finding that withdraws the claim removes every outcome derived through it, that is, the solutions, relation applications and question resolutions that cite it and whatever was derived from them, and a finding that reaffirms it leaves them standing. A claim that lists the withdrawn claim among its `dependencies` is different: it is a use of that claim, and it keeps its standing, with the outcomes it supports, until a finding names it in `invalidates` as well. A confirmed defect can withdraw one argument while another argument continues to support the same node. The feedback explains the actual uses and what remains unresolved.

The `proofs` object in `knowledge/state.json` lists the currently supported proof routes. A direct solution has ID `<record-id>/<solution-id>`. A relation applied forward, to its conclusion, has ID `<record-id>/<relation-id>`; applied backward, so that one premise fails and its node receives the opposite of the outcome written for that premise, it has that ID followed by `~` and the position of that premise, counted from zero. Each entry identifies its node, outcome and supporting claims, and a derived outcome lists in `premise_proofs` the proofs it used. Use those exact IDs in `dependency_updates`. The separate `relations` object contains the reviewed implication statements, including relations whose premises are not yet solved.

When a candidate review that publishes its candidate finds a defect in an earlier record, it can report a concern and its established findings. A withdrawal without a named existing concern creates a comprehensive review of its broader consequences. Do not claim that those consequences have all been assessed merely because the original defect was found.

## Comprehensive assessment

For a comprehensive assignment, `assessment.json` contains `feedback`, `index_assessment`, `findings`, and optional `concerns`. It has no candidate publication decision. Address the assigned concerns and requested evidence in the feedback, following the actual uses described in the role guide. The runner publishes this assessment directly as a review record and attaches its findings to their sources. It does not require another peer/review cycle for your judgment to take effect.

If you introduce notation needed to explain your assessment, add a `glossary` array in the local entry format of [Record format](record-format.md), and use it in the feedback. No entries are needed when you introduce no terms. These local definitions explain your output; they do not create new mathematical proof claims.

Run the transport check on your session directory before finishing. A completed assessment can state uncertainty; an interrupted assessment has not finished the stage. The runner preserves partial work and supplies it, with the original assignment, to a replacement reviewer.
