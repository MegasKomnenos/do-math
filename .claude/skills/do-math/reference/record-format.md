# The peer's record candidate

The peer's exposition gives a future researcher a coherent account of the producing session's work and the peer's additions. Review also needs to identify particular claims, proposed questions and solutions so that its judgments refer unambiguously to that account. The record candidate combines these two forms: readable mathematics and a structured description of the contribution.

Write the structured description in `output/record.json`, with the exposition and its evidence in companion files. The sections below introduce the information in the order a record is built: its account and claims, its proposed consequences for nodes, and the terminology it introduces. Review writes a separate assessment. The runner freezes the candidate before that review and publishes its bytes unchanged if review finds useful material.

File references in `record.json` are relative to the candidate directory and use `/`. They cannot contain `..` or point through filesystem links. This keeps the candidate's evidence together when the runner copies it into the published record. Reserve the candidate's top-level names `review` and `provenance.json` for the runner's assessment attachment and processing identities. Put copied historical reviews or provenance under another evidence path, such as `evidence/source-review/` or `evidence/source-provenance.json`, and refer to that path in the account. The transport check rejects a candidate containing either reserved top-level name before review or publication.

## The account and its claims

`title` names the contribution and `description` introduces it for the index. `exposition` points to the mathematical account. `claims` gives addressable IDs to the assertions that review needs to assess explicitly. The exposition can develop these claims in the order the argument requires. It should also explain limitations, failures and remaining opportunities; a result list cannot carry that work by itself.

Each claim has `id`, `statement`, `evidence`, `by`, and optionally `dependencies`. Write the exact mathematical assertion in `statement`, including its scope and whether it is proved, observed, conjectural or from literature. `evidence` explains where its support is found. `by` is `producer` or `peer`, identifying who developed it. A dependency is `{"record": "<published-record-id>", "claim": "<claim-id>"}`; `record: "self"` refers to another claim in this candidate. List mathematical premises and explain their use in the exposition.

IDs use letters, digits, `_` and `-`, beginning with a letter or digit. Claim IDs are unique within the record. After publication, the record ID and claim ID together identify a claim. The runner assigns the record ID. The peer can choose local claim, relation, solution and term IDs; solution and relation IDs must also be distinct from one another because they identify proof routes.

## Nodes, relations and solutions

Use existing node IDs where the precise statement is already on the frontier. A proposed node has `id`, `statement`, and `connection`, the claim ID that establishes its connection to the research. Generate a distinct proposal ID, for example `n` followed by a UUID's hexadecimal digits. Review either admits this proposal, identifies it with an existing node, or declines it. Speculative statements stay in the exposition and do not need node proposals.

A relation has `id`, `claim`, `premises`, and `conclusion`. Each premise and conclusion is a signed node statement: `{"node": "<id>", "outcome": "proved"}` for the statement, or `outcome: "refuted"` for its negation. The premises are conjunctive. A separate relation represents an alternative route, and two directions can represent an equivalence. `claim` names the candidate's proof of this exact implication. Merely suggesting a connection does not justify its acceptance.

A solution has `id`, `node`, `outcome`, `claim`, optional `formal_dependencies`, and optional `lean`. It asserts that the cited claim settles the whole node or its negation. `formal_dependencies` lists the signed nodes whose validated Lean results are needed for the intended formalization. Review checks that dependency choice and can correct it. An implication that still needs its premises is a relation; it is not an unconditional solution of its conclusion.

For a supplied Lean solution, `lean` has `theorem` and `sources`. List every source file needed from this candidate, including its own dependency modules. Use one module root, conventionally `lean/`, so that a path such as `lean/Objects/Basic.lean` names module `Objects.Basic`. Sources imported from earlier records can be copied with provenance or linked clearly for review to obtain. The actual theorem, its scope and its relationship to the node must be explained in the exposition.

## Local terminology

`glossary` is an array of introduced local entries. Each has `id`, `name`, `definition`, optional `symbol`, and Boolean `global_candidate` (default false). The definition includes domains and necessary conditions. Existing shared terms and inherited local definitions are referenced in the exposition rather than registered again. A record introducing no terminology uses an empty array.

Explain a global recommendation in the exposition or an additional `global_reason` field: which other mathematics benefits from a fixed shared name, and why an existing expression is insufficient. Review assesses the local glossary and the consistency of flagged entries. Approved, flagged entries become globally usable candidates at publication; the organizer decides permanent membership later.

## A small candidate

This example shows transport structure. Its mathematical exposition and evidence must be written and assessed during actual research.

```json
{
  "title": "Right addition of zero on the natural numbers",
  "description": "Establishes n + 0 = n for all natural numbers by the defining equation of addition.",
  "exposition": "exposition.md",
  "claims": [{"id": "c1", "statement": "For every n in Nat, n + 0 = n.",
              "evidence": "The argument in exposition.md unfolds the right-zero equation.",
              "by": "producer", "dependencies": []}],
  "nodes": [], "relations": [],
  "solutions": [{"id": "s1", "node": "root", "outcome": "proved", "claim": "c1",
                 "formal_dependencies": []}],
  "glossary": []
}
```

For a reduction from a proposed Q to an existing P, add the precise Q under `nodes`, a claim proving Q implies P, and a relation whose premise is proved Q and conclusion is proved P. Leave Q out of `solutions` until its statement or negation has actually been established. An unresolved premise does not prevent publication of the useful implication.

## Handoff

Put the exposition and all evidence needed by later readers in `output/`. The review sees the originals as well, so preserve attribution to the producer's report, conversation or artifacts where relevant. Those private references help review reconstruct the producer's work; the public account must still stand with its published evidence.

Run the check command on the peer session directory. A passing check establishes structural usability, not mathematical validity. When the peer ends, the runner copies the candidate to a fixed location and gives that location, its file hashes and the producing originals to a fresh reviewer. The reviewer writes its assessment in its own output folder.
