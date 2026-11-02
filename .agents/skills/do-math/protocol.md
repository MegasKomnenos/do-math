# do-math instance and output contract

This document is the contract by which the runner and the plan, research, exploration, peer and review sessions exchange files. Inside an **instance** that researches one goal, sessions write their results in their own folders, and the runner copies only the published output into the **accumulated knowledge**. The next session reads this knowledge and carries the research on. The human-readable mathematical exposition is the primary deliverable, and Lean sources are the evidence for the results concerned.

The implementation entry points are `check_session` and `main` in [check.py](check.py). The formats and small examples in this document are the contract of that checker. Research methods and judging principles are handled in the per-category working contexts, and the runner's user commands and the internal format of process state are decided by the runner.

## 1. Instance and file responsibilities

An instance is placed in a folder excluded from the main repository's Git (for example `.skill-workspace/do-math/<name>/`) or outside the repository. The instance's own Git is created at its root by the runner's `init` command when it creates the instance. The parent repository is not used as the instance Git.

```text
INSTANCE/
  .git/                     the instance's own history
  goal.md                   the user's goal, requirements and permissions
  settings.json             run settings
  knowledge/
    index.md                the general module of the index the runner renders: preamble, module table, entries
    index/                  the other index modules the last plan declared, one file each
      closed-route.md
    k0001/                  a record ID newly assigned by the runner
      output.json           classification and references of the published output
      exposition.md         a file the output provided (name is free)
      glossary-local.md     the record's local glossary (research, explore and peer)
      Proof.lean
  sessions/
    s0001/                  a session ID newly assigned by the runner
      input.json            the three-layer working context and the task target the runner gives
      output/               every file the session will publish
        output.json
      work/                 optional intermediate work directory
      work.tar.xz           the archive into which the runner moved work/ after the session ended
      ...                   records of the runner and the session, such as CLI logs
  runner/                   runner state, event queue, process information
    lean/                   the Lean broker: lock, state, calibration table, queue and jobs
  control/
    STOP                    when present, a mark that stops dispatch of new sessions
    inputs/                 user inputs added as uniquely named UTF-8 text files
```

A session writes only inside its own `sessions/<ID>/`. `input.json` is prepared by the runner and read by the session. Files outside the session's `output/` are not part of the published output. Only the runner adds new records to `knowledge/` and leaves a Git commit for every integration. The internal schema of `runner/` and the tracking of input consumption are the runner's responsibility. The one exception is `requests` in `runner/state.json`. A plan reads this field so as not to overlap with work already posted, and its format and meaning are the contract defined by 'Unfinished requests and events a plan reads' in [RUNTIME.md](RUNTIME.md). A plan does not rely on any other runner-state field. The raw input texts in `control/inputs/` are preserved, and what the runner has not yet handed over is put into the next plan's events. `STOP` does not terminate sessions already running.

JSON is UTF-8 (a BOM is also read). Strings other than paths may contain human-readable explanation. IDs begin with a letter or digit and use only letters, digits, `_` and `-`. Session IDs and record IDs are separate namespaces, each assigned by the runner without duplication within the instance. A result ID is unique within one research, peer or bundle-review record. The same result ID in different records is a different result. An empty array value is `[]`, and the absence of an optional result is the `null` specified below. Required explanatory strings must be nonempty. Unknown additional JSON fields are ignored. Additional fields alone never create new runner behavior.

### Settings

`settings.json` provides the following fields. The official output check does not check this file; the runner reads and uses the settings.

```json
{
  "max_sessions": 8,
  "defaults": {
    "plan": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "research": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "peer": {"model": "codex/gpt-6.1-sol", "effort": "medium"},
    "explore": {"model": "codex/gpt-6.1-sol", "effort": "high"},
    "review": {"model": "claude/sonnet", "effort": "high"}
  },
  "cli": {"codex": "C:/tools/codex.exe", "claude": "C:/tools/claude.exe"},
  "limit_wait_seconds": 300,
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"],
    "cwd": null,
    "env": {},
    "memory_budget_mb": null,
    "confidence": 1.3,
    "min_free_memory_mb": 2048,
    "cpu_threads_budget": null,
    "threads": 2,
    "priority": "below_normal",
    "max_passes": 3,
    "calibration_expect_mb": 2048,
    "default_spread": 0.5
  }
}
```

The paths and models above are a format example; configure the available installations and models. `defaults` must contain the plan, research, explore and review defaults. New settings also state peer explicitly. If existing settings have no peer, the review model and effort are copied and used. `max_sessions` is a positive-integer cap over all categories together. If the user does not specify a concurrency cap separately, state the default 8 explicitly in the new instance's `settings.json`. `limit_wait_seconds` is the positive number of seconds to wait when there is no provider limit reset time. A model string is `codex/<model to pass to the CLI>` or `claude/<model to pass to the CLI>`. The runner chooses the CLI by the prefix and passes everything after the `/` as the model argument. Effort is a nonempty string; for a `claude/` model use one of `low`, `medium`, `high`, `xhigh`, `max`. For a `codex/` model the string is passed as it is, and whether it is supported is decided by the CLI and the model. When specifying a model or effort, confirm both values that will actually be used after merging with the defaults. The way they are passed is in [CLI.md](CLI.md).

If a request a plan posted has `model` or `effort`, only that field overrides the category default. If either is specified, write the reason in `selection_reason`. The plan session, automatic peers and automatic bundle reviews use the plan, peer and review category defaults respectively. Automatic standalone research reviews posted before the reorganization also use the review defaults.

`lean.command` is the command that compiles a Lean file. It is run by the instance's Lean broker, not by the sessions, with a `--threads` flag and the absolute path of the source file appended as the last arguments. The output of `version_command` is what the broker's `version` command reports, and it goes into the output's `lean.version`. `cwd` is an absolute working folder, or `null` for the folder of the session that submitted the compile. `env` holds string environment variables that override the inherited environment. If you use Mathlib, set `command` to `[".../lake.exe", "env", "lean"]`, set `cwd` to the Mathlib project, and if needed include the Lean bin and the existing PATH in `env.PATH`. The remaining nine keys are optional; they configure the broker's memory budget, thread budget, machine gate, process priority, queue order and calibration, and a file without them is valid. Their meaning and defaults are defined by 'Settings' in [LEAN.md](LEAN.md). The broker reads these settings again whenever the file changes. The installation state used is that at run time.

## 2. The input.json the runner gives a session

`input.json` is a fixed name in the session folder. All of the following common fields are required.

```json
{
  "instance": "C:/research/example",
  "category": "research",
  "context": {
    "common": ["C:/skill/common.md", "C:/skill/protocol.md", "C:/research/example/goal.md"],
    "category": "C:/skill/research.md"
  },
  "task": {
    "instructions": "Prove that n + 0 = n for every natural number n and write an exposition.",
    "references": [],
    "supersedes": []
  }
}
```

`instance` is the absolute path of an existing instance. The checker looks for `knowledge/` here. `category` is one of `plan`, `research`, `explore`, `peer`, `review`. `context.common` is the list of absolute paths of the common-elements documents and the goal and conditions file, and `context.category` is the absolute path of the task-common-elements file of that category. The files at these paths must exist. **The task-specific elements are the `task` object of this input.json.** `task.instructions` is this round's instructions, and `task.references` is the list of references to the published knowledge to use (section 3).

Per category, the following items are added to `task`.

| Category | Items the runner gives and their meaning |
|---|---|
| research | `supersedes`: the list of existing record IDs this task is to supersede. `[]` if none. Copied from the plan's research request. |
| explore | No items added. `instructions` and `references` are copied from the plan's exploration request. |
| peer | `target`: `{"kind":"research","record":"k0001"}` or `{"kind":"explore","record":"k0001"}`. An independent peer that works the published work directly. |
| review | `target`: `{"kind":"research","record":"k0001"}` or `{"kind":"bundle","work":"k0001","peer":"k0002"}`, or `{"kind":"goal"}`. A bundle is the original work and the peer on that work. Standalone research reviews and goal reviews are kept as well. |
| plan | `events`: the list of event objects this plan receives. The six kinds below are used. `previous_plan`: the record ID of the plan integrated immediately before, or `null` if there is none yet. The runner always includes this field. The checker allows both omission and `null`, and for any other value confirms that it is an existing plan record ID. |

An example of the structure of plan events. The checker confirms the `kind` of every event, the `record` of `review_finished`, `peer_finished` and `exploration_finished`, the `session` and `reason` of `session_failed`, and the `text` of `user_input`. The remaining fields of a failure event are facts the runner includes with it.

```json
[
  {"kind": "start"},
  {"kind": "review_finished", "record": "k0002"},
  {"kind": "exploration_finished", "record": "k0004"},
  {"kind": "peer_finished", "record": "k0005"},
  {"kind": "session_failed", "session": "s0003", "reason": "output/output.json is missing",
   "category": "research", "request": "k0001:research:0",
   "task": {"instructions": "...", "references": [], "supersedes": []},
   "origin": "k0001", "limit": null, "exit_code": 1, "launch_error": null},
  {"kind": "user_input", "text": "Natural numbers include 0."}
]
```

This list is an example of the event kinds. The actual first plan may have only the start event. `review_finished.record` is a review record that passed the re-check and was integrated, and `exploration_finished.record` and `peer_finished.record` are exploration and peer records integrated in the same way. A failure is a session with no output or one that failed the re-check, and includes plan and review failures. A failure event includes the facts the runner knows. `category` and `request` are the failed session's category and request key, and `request` is `null` for a plan that received events. `task` is the task-specific elements that session received, as given. The `task.events` of a failed plan contains, as they were, the events that plan received and could not process. `origin` is the ID of the published record that created the request, and `null` for a plan. `limit` is the detected provider limit `{retry_at, source, provider}`, `exit_code` is the CLI exit code if known, and `launch_error` is the launch-failure text; each is `null` when not applicable. The runner delivers to one plan all events not yet given to any plan, and events that arise while that plan runs are delivered to the next plan. Integration of a research record creates an automatic peer request and is not itself a plan event. Integration of an exploration creates an automatic peer request together with an exploration_finished event. Integration of a peer creates an automatic review request for the work–peer bundle together with a peer_finished event. Integration of a review becomes a review_finished event. That an event was delivered first does not mean the later review has finished, so the plan distinguishes the current standing of the claim concerned.

In the launch prompt the runner tells the session folder, this `input.json` and the location of the official check command. The review input and the launch prompt do not include the author session's folder, logs or intermediate-file locations. A review reads the whole of `knowledge/` and the published target record. This is a delivery rule, not a device that monitors file reads.

## 3. Published files, references and superseding records

Each session writes its output in `output/output.json` and also puts the files of its own that it points to under `output/`. The names and subfolders of expositions, Lean and computation data are free. File paths in the output are `/`-separated relative paths based on that `output/`. Absolute paths, `..` and filesystem links are not used as published file references. After integration the same paths are based on `knowledge/<record ID>/`.

The following four items are required in the `output.json` of every category.

```json
{
  "category": "research",
  "overview": {
    "title": "Right addition of zero on the natural numbers",
    "summary": "Using the definition of natural-number addition, proved n + 0 = n for every n. Confirmed the same proposition with Lean's rfl. The scope of this result is this equation."
  },
  "references": [],
  "supersedes": []
}
```

`overview` is the text that introduces the whole deliverable of the session. Write it so that a later reader can judge what was dealt with, how far it got, and which parts to read further. `title` is a nonempty single-line title that represents the subject of the whole output rather than its single strongest achievement. `summary` is concise prose that expands on that title. The title and summary are plain text; the runner attaches the links to sources and reviews.

The summary starts from the question and approach first addressed and connects what the actual attempts revealed with what remains. Include not only the results of proofs, disproofs, computations, literature searches and formalization but also important failures, excluded approaches, and parts not run or not verified, as far as they change the meaning of the output. A session centered on failure is introduced around the failure, its reasons and its scope of application. Distinguish a failed strengthening candidate from a counterexample to the original question, a finite confirmation from a universal proof, and an informal argument from Lean assurance. For example, if only an auxiliary proposition was disproved, explain together which route that disproof excluded and how far the original problem remains.

If there are several results, explain in a group how the main results contribute to the same question. The remaining items need not all be listed, but include the achievements, failures and limitations whose omission would lead to a misunderstanding of the whole session. The number of theorems or a passing check does not stand in for the research content. In research, write the summary by cross-checking `results`, `failed_attempts`, `open_questions` and the whole exposition. In a plan, introduce the chosen direction and reasons, the important approaches among those deferred or changed, and the next action; in an exploration, the angles examined, the changed understanding and the directions handed on; in a review, the scope of verdicts over the whole target, and the defects, withheld judgments and limits of verification. Do not add successes or failures that are not in the output, and keep the knowledge and confirmed scope as of the time of writing.

The runner gathers the `overview` of published research and exploration records into the index. Plan, peer and review records have no entries of their own: peers and reviews are linked under the original work, so that a peer is found by its title and source link and the certification status of its new content is not confused, and the latest plan is linked in the preamble. For research, the current review links, the verdict value of `overview_assessment` and whether there is a conflict are shown, and per-result verdict counts are not output. A goal review leaves its link and verdict in the preamble, and a superseding record gets a link. The grounds of verdicts are not transferred to the index; they are read in the review record. If the last plan record has `research-status.md` or `glossary.md`, a link to each is placed in the index preamble. An exploration gets a note telling the reader to distinguish observations and conjectures from individually reviewed claims. When a review is published or a record is superseded, the existing entries are updated too. Published research without a review is marked unreviewed.

The index is split into modules according to the `index` field of the last plan record (section 6). `knowledge/index.md` is the general module: it holds the preamble, the links above, a table of the other modules with each one's title, description and counts of records, unreviewed records and records with conflicting reviews, and the entries of every research and exploration record that the last plan did not file into another module. Each other module is rendered as `knowledge/index/<name>.md`, with the module's title and description at the top and its records' entries below, in publication order and with the same review marks; record links inside a module file are relative to `knowledge/index/`. A module file whose name the latest plan no longer declares is removed. If the last plan has no `index` field, every entry is in the general module. The index is a derived navigation file, and the record and review texts are the authoritative source of evidence. Record publication and the update of every index file are put in the same instance Git commit, and on restart all index files are rebuilt from the published records. Sessions do not modify the index directly.

`category` must equal the input. `references` is the array of references to the accumulated knowledge actually used. Each reference requires `record`, and `file` and `result` are optional. Both may be used together.

```json
[
  {"record": "k0001"},
  {"record": "k0001", "file": "exposition.md"},
  {"record": "k0001", "result": "r1", "file": "Proof.lean"}
]
```

`record` is a record that has `knowledge/<ID>/output.json`, `file` is an actual file inside that record folder, and `result` is a `results[].id` of the designated research, peer or bundle-review record. Use the ID that is unique within that record, and distinguish it from the same ID in other records. References are to records of the same instance. Your own output files are linked by a result's `exposition` and `lean.sources` or by relative links in the exposition. Put additional evidence files in `output/` too and explain in the exposition the path to read. Dependence on existing knowledge used in a published exposition is also written in `references`. For web literature, write the bibliography and the cited URL in the exposition. The checker does not interpret the exposition body, Markdown links or web URLs, so the sufficiency of that evidence and whether it can actually be used are confirmed by the author and the reviewer. An output that would make a reviewer go to the author's `work/` or a local absolute path has not finished its delivery.

`supersedes` is the list of existing record IDs that this new record **supersedes in their entirety**. For a partial correction, produce a whole output that can be read including the results and evidence to keep in the new record, and reference the original record. A task's `supersedes` is the plan's intent, and an output's `supersedes` is the actual supersession declaration. It may differ according to the actual research results, and the checker does not force the two to be equal.

The rules for reading the current content are as follows. If B supersedes record A on the same subject with `supersedes`, the body starts at B and A is read as history and evidence. If C supersedes B, start at C. Records on different subjects remain together as current knowledge. If two branches supersede the same record, neither is chosen automatically; both are read and the next plan sorts it out. The winner is not chosen by time or by the size of the ID. A plan does not assign two tasks that supersede the same record at the same time. The index marks reviews not superseded in the explicit `supersedes` relation as current reviews, and marks a conflict when positive and negative verdicts on the same result and item exist together. This marking gathers the relations and verdict values of records; the propagation of defects in evidence and the mathematical validity between branches are judged by sessions reading the texts.

Supersession and mathematical establishment are different. A new result is the author's claim until reviewed. The reviews of an old record are not passed on to the new record automatically. The reviews of a research record R are found in standalone research reviews with category=review or in bundle reviews that designate R as work. The claims of peers and explorations are confirmed by following the source of a bundle review. If a review has been superseded, follow that history and read the current review. If, for the same item of one result, positive and negative verdicts of current reviews exist together (a conflict), the result is not used as an established result. The definition of conflict and the way to read verdicts whose confirmation was not finished are defined by 'Judging published knowledge' in [common.md](common.md). The plan decides on an additional review or revision research. Lean acceptance, agreement between exposition and Lean, and goal satisfaction are not judgments that substitute for one another.

## 4. Research output

To the four common fields, add the arrays `results`, `failed_attempts` and `open_questions`, and publish the local glossary `output/glossary-local.md` ('Glossaries' below). Continuing and finishing the research follow the principles of [research.md](research.md). A format that preserves only failures and open questions without results is also allowed. Failed approaches are not discarded but left as grounds for the next plan's judgment.

A small valid `output/output.json`:

```json
{
  "category": "research",
  "overview": {"title": "Right addition of zero on the natural numbers", "summary": "Proved n + 0 = n for every natural number n in Lean by the definition."},
  "references": [],
  "supersedes": [],
  "results": [{
    "id": "r1",
    "exposition": "exposition.md",
    "verification": "Compiled the core Lean file through the Lean broker (estimate 64 MiB; measured peak 38 MiB, 2 s) with #print axioms add_zero_example appended, which printed that it depends on no axioms. A universal proposition over the natural numbers; Mathlib was not used.",
    "lean": {"sources": ["Proof.lean"], "version": "Lean (version 4.32.0)"}
  }],
  "failed_attempts": [],
  "open_questions": []
}
```

The `output/exposition.md` of this example:

```markdown
# Right addition of zero on the natural numbers
The natural numbers n include 0. Claim: for every natural number n, n + 0 = n.
In Lean's Nat addition, the case where the right argument is 0 computes to n.
Therefore the two sides are equal by definition, and the rfl in Proof.lean proves this fact.
What this exposition claims is a proposition about natural-number addition.
```

`output/Proof.lean`:

```lean
theorem add_zero_example (n : Nat) : n + 0 = n := by rfl
```

The verification and version strings above are writing-format examples. In an actual output, write the confirmations you actually performed and the tools' actual output strings. In `verification`, write the commands, the input range, the observed results and the scope not confirmed so that a person understands. The exposition must contain definitions, assumptions, claims and argument. The checker confirms only file existence and string format.

For computation or literature results that do not use Lean, `lean` is `null`. If Lean is used, `sources` is one or more published source paths, and `version` is the version string the broker's `version` command reported at that time. Publish your own dependency sources together too, or link them as knowledge references, and leave how to compile in the exposition. The session compiles the source through the instance's Lean broker ([LEAN.md](LEAN.md)). If it could not compile, or the compile failed, it writes that fact in `verification`, together with the estimate it gave and the cost the broker measured. The version string is information, not a comparison value that blocks execution.

An item of `failed_attempts` is `{"description":"the attempt and what failed", "verification":"how far was actually confirmed and what is unknown"}`. `open_questions` is a list of strings of the questions that remain. An empty list means there are no items to record in that output.

### Exploration output

An exploration adds `exposition` and `questions` to the four common fields and publishes `glossary-local.md` like research. `exposition` is the relative path, based on `output/`, of the exploration body file, and `questions` is the list of strings of the questions that arose during the exploration. An exploration record does not supersede other records, so `supersedes` is written as `[]`. An exploration gets an automatic peer, and when the peer finishes, an automatic review that sees the original exploration and the peer together. What the body contains is defined by [explore.md](explore.md).

```json
{
  "category": "explore",
  "overview": {"title": "The structure of parking functions seen in small cases", "summary": "Listed the parking functions for n ≤ 6 directly and saw the relation between car order and empty spots in several expressions. The observed symmetry is left as a conjecture, and the direction seen in the generating-function expression is handed on."},
  "references": [],
  "supersedes": [],
  "exposition": "exploration.md",
  "questions": ["Does the observed symmetry hold for every n?"]
}
```

### Glossaries

A plan publishes the global glossary currently in force in `output/glossary.md`, and the history of candidate processing, holds and retirements in `output/glossary-history.md`, together with `output/research-status.md`. Every research, exploration and peer session publishes its local glossary in `output/glossary-local.md`: the names, symbols and auxiliary objects the record uses internally, in the same entry format as the global glossary plus a `Global candidate` field by which the author flags entries the run should share. The format of both glossaries and the rule for flagging candidates are defined by 'Glossaries' in [common.md](common.md), and the plan's handling of candidates by 'Updating the global glossary' in [plan.md](plan.md).

A minimal valid `glossary-local.md` with one entry:

```markdown
<!-- do-math-local-glossary -->
Local glossary of this record. Global glossary applied: k0003 (glossary.md). Local entries of other records used as they are: none.

<a id="local-1"></a>
## 1. Right-zero identity

| Field | Content |
|---|---|
| Name and symbol | right-zero identity, RZ(n) |
| Kind | property or relation |
| Definition | RZ(n) :⇔ n + 0 = n, for a natural number n |
| Well-definedness | Not applicable |
| Related expressions | The instance n = 0 is the base case of the goal |
| Current formal correspondence | `add_zero_example` in Proof.lean |
| Provenance | exposition.md, first paragraph |
| Global candidate | None |
```

A record that introduces no name of its own publishes the marker and the preamble sentences with no entries. The checker confirms, for a plan, that glossary.md, glossary-history.md and research-status.md are nonempty and that the glossary marker, the unique numbers with their immediately preceding `term-N` anchors, the order and non-duplication of the seven fields, additions outside the table, local entry links, and the existence of family files and their glossary links are correct. For a research, exploration or peer output it confirms that glossary-local.md is nonempty, carries the local marker, and has the same entry structure with `local-N` anchors and the eight fields. The mathematical validity of entries and relations, collisions between local and global names, and the merit of a candidate are not subject to machine checking. A family description may be published with the global glossary as the optional file glossary-relations.md.

### Peer output

`category: "peer"` is a peer response that works the original work directly. `target` is the same research or exploration record as in the input. `exposition` is the self-contained response body, `questions` are the questions genuinely left open, and `results` are the proofs, counterexamples and computation results the peer newly wrote. The result format is the same `id/exposition/verification/lean` as research, and the array is empty if there are no new results. A peer publishes `glossary-local.md` like research; it usually adopts the work's local entries by reference in the preamble and lists only the names it introduces itself. A peer does not issue an `overview_assessment` or a `goal` verdict. `supersedes` is an empty array.

```json
{
  "category": "peer",
  "overview": {"title": "A response that read and worked the parking-forest expression", "summary": "Re-confirmed the meaning of the conditional distribution and left the questions that arose under parameter changes."},
  "references": [], "supersedes": [],
  "target": {"kind": "explore", "record": "k0001"},
  "exposition": "response.md", "results": [], "questions": []
}
```

The `result` of a result reference may point to an explicit result ID of a research record or a peer, or to a result ID of a bundle review. Being referenceable does not mean mathematical acceptance. Follow the review's verdict scope and the original source.

## 5. Review output

The review target must match the input's `task.target`. A research review targets the whole published output of one research session and judges every result ID in it exactly once. A research review also requires `overview_assessment: {"verdict": "supported | not_supported | undetermined", "reason": "grounds of the verdict"}`. Judge whether the target's title and summary are a valid introduction of the whole output including successes and failures, without important omissions or exaggerations. Even if there are no results, judge the title and summary and leave a review of the failed approaches and open questions with `results: []` and `summary`. A goal review does not require `overview_assessment`.

A valid example when the preceding research has been integrated into `knowledge/k0001/`:

```json
{
  "category": "review", "references": [], "supersedes": [],
  "overview": {"title": "Review of the right-addition-of-zero result", "summary": "Confirmed the correspondence between the original proposition and the Lean proof and the allowed axioms. The submitted title and summary also match that scope."},
  "overview_assessment": {"verdict": "supported", "reason": "The title and summary accurately describe the actual natural-number equation and the scope of formal verification."},
  "target": {"kind": "research", "record": "k0001"},
  "results": [{
    "result": "r1",
    "assessment": {"verdict": "supported", "reason": "The claim of right addition of zero on the natural numbers holds by the definition and proof presented."},
    "lean": {"verdict": "accepted", "reason": "Recompiled a copy of the published Proof.lean through the Lean broker and confirmed exit code 0, and the appended #print axioms add_zero_example printed that it depends on no axioms."},
    "alignment": {"verdict": "matches", "reason": "Both the exposition and Lean say n + 0 = n for every natural number n."},
    "terminology": {"verdict": "conforms", "reason": "The natural numbers and addition in the exposition are used with the same names and meanings as the definitions in goal.md."}
  }],
  "summary": "Reviewed result r1 of this research output and its confirmed scope."
}
```

Each judgment has a `verdict` and a nonempty `reason`. The verdicts in the example do not stand in for an actual review.

| Item | Allowed verdicts | Meaning |
|---|---|---|
| `assessment` | `supported`, `not_supported`, `undetermined` | The evidence presented supports the claimed result / does not support it / the judgment was not finished |
| `lean` | `accepted`, `rejected`, `not_checked`, `not_applicable` | Recompilation of the published source and the axiom criteria of [common.md](common.md) passed / compile failure or an axiom outside the allowed ones / not confirmed / a result without Lean |
| `alignment` | `matches`, `differs`, `not_checked`, `not_applicable` | The mathematics of the exposition and Lean agree / differ / not confirmed / a result without Lean |
| `terminology` | `conforms`, `deviates` | Follows the global and local glossaries / there is a name violation or a meaning violation. Does not enter into the establishment of the result or the judgment of conflict. |

A reviewer does not conclude from Lean acceptance alone that the result or the exposition is correct. Reproduce computations or inspect their method, cross-check literature against the source, and write the grounds and limits in `assessment.reason`. Supplementary material the reviewer produced may also be put in its own `output/` and published together.

### Work–peer bundle review

In `target: {"kind":"bundle","work":"k0001","peer":"k0002"}`, work is a research record or an exploration, and peer must be the peer record that targets exactly that work. The reviewer reads the whole bodies and evidence of both outputs. The results of research and peer records that have result IDs are each judged exactly once. For explorations and additional claims in prose, designate the published location and the exact statement. Do not judge it a defect that a conjecture is unresolved.

A bundle review has `exposition`, `overview_assessments`, `results` and `summary`. There is one overview assessment each for the original work and the peer, and each result has the review's own unique ID, the original source and the existing four verdicts.

```json
{
  "category": "review",
  "overview": {"title": "Independent review of the work and the peer response", "summary": "Cross-checked the two bodies and judged the confirmed scope of the stated claims."},
  "references": [], "supersedes": [],
  "target": {"kind": "bundle", "work": "k0001", "peer": "k0002"},
  "exposition": "review.md",
  "overview_assessments": [
    {"record": "k0001", "assessment": {"verdict": "supported", "reason": "The overview preserves the scope of the body's claims."}},
    {"record": "k0002", "assessment": {"verdict": "supported", "reason": "Distinguishes the unconfirmed parts."}}
  ],
  "results": [{
    "id": "c1", "source": {"record": "k0001", "result": "r1"},
    "assessment": {"verdict": "supported", "reason": "Confirmed the exact assumptions and argument of the original r1."},
    "lean": {"verdict": "not_applicable", "reason": "A result without Lean."},
    "alignment": {"verdict": "not_applicable", "reason": "A result without Lean."},
    "terminology": {"verdict": "conforms", "reason": "Matches the glossary's definitions."}
  }],
  "summary": "An example in which the peer has no new results. In reality every stated result of the original work and the peer must be judged."
}
```

The source of an exploration or prose claim without a result ID is written as `{"record":"k0001","file":"exploration.md","statement":"an exact statement specifying the definitions, assumptions, quantification and conclusion"}`. The source must be one of the two records of the bundle. Do not accept a key argument newly created by the reviewer by attributing it to the original author's claim. A defect in an external record used as evidence is recorded in the summary and handed to the plan for a separate review.

Only a review of the identical work/peer pair is superseded with supersedes. Verdicts of different bundles or of past standalone reviews are handled as conflicts by cross-checking the original source. The formats and existing verdicts of old standalone research reviews and goal reviews are not changed. An exploration or a peer is not certified as a whole.

A goal review targets the whole instance, not a specific result. It uses the following format in the same review category. `goal` is required instead of `results` and `summary`.

```json
{
  "category": "review",
  "overview": {"title": "Goal-achievement review", "summary": "Cross-checked the published proofs and independent reviews and judged that the goal proposition is satisfied."},
  "references": [{"record": "k0001"}, {"record": "k0002"}],
  "supersedes": [],
  "target": {"kind": "goal"},
  "goal": {"verdict": "achieved", "reason": "The goal's universal proposition over the natural numbers is satisfied by the published proof and exposition, and the independent reviews agree."}
}
```

`goal.verdict` is one of `achieved`, `not_achieved`, `undetermined`. The runner completes by reading **`goal.verdict == "achieved"` of an integrated goal review**. It does not complete on the `supported` or `accepted` of a research review. The goal reviewer cross-checks the goal, the user's conditions and the whole accumulated knowledge, and leaves the grounds in `references` and `reason`.

## 6. Plan output and dispatch

Besides the four common fields, `reason`, `research`, `explorations`, `reviews`, `goal_review` and `wait` are required. Additional peer requests go in `peers`, and the index layout goes in `index`. A new plan writes `peers: []` and `index: {"modules": []}` even when empty, and for compatibility with existing plans an omission of either is read as empty. Below is a valid example that posts one first research request.

```json
{
  "category": "plan", "references": [], "supersedes": [],
  "overview": {"title": "Assigning the proof of the first equation", "summary": "Starts research that proves and explains the goal's basic equation in Lean. The next task is decided after the result is reviewed."},
  "reason": "Obtain a proof and exposition starting from the goal's basic proposition.",
  "research": [{
    "instructions": "Prove in Lean that n + 0 = n for every natural number n and write a faithful exposition.",
    "references": [], "supersedes": []
  }],
  "explorations": [],
  "peers": [],
  "reviews": [],
  "goal_review": null,
  "wait": null,
  "index": {"modules": []}
}
```

The identity of an array item can be identified by **plan record ID + array name + 0-based position**. The runner dispatches each request once as a new session, and whether to do it again after the session ended in failure is decided by the next plan as a new request. An empty list in a later plan does not cancel other requests already posted.

`research[]` has `instructions`, `references` and `supersedes`. The runner copies these three fields into the research `task`. `explorations[]` has `instructions` and `references`, and the runner copies these two fields into the exploration `task`. `peers[]` has `instructions`, `references` and a research or exploration `target`. `reviews[]` has `instructions`, `references` and a standalone research or work–peer bundle `target`. It is a request for an additional review of an already integrated research output. `goal_review` is `null` or an object with `instructions` and `references`, and the runner creates the review by attaching `target: {"kind":"goal"}`. All five kinds of request may optionally have `model`, `effort` and the reason for the specification `selection_reason`. Example:

```json
{
  "instructions": "Independently of the existing review, confirm the universal scope of the exposition.",
  "references": [{"record": "k0002"}],
  "target": {"kind": "research", "record": "k0001"},
  "model": "claude/sonnet",
  "selection_reason": "Confirm the same scope independently on a different model."
}
```

When a research record or an exploration is published, the runner assigns a peer automatically, and when the peer is published, it assigns a review of the work–peer bundle automatically. A plan does not post these follow-ups again in peers or reviews. If a follow-up ended in failure or a separate confirmation is needed, confirm the current requests and results and then issue an additional request. An additional review is requested when the plan judges it necessary.

### Index layout

`index` declares how the runner splits the index into modules. It is an object with a `modules` array; each module has `name`, `title`, `description` and `records`.

```json
"index": {
  "modules": [
    {"name": "general", "title": "General",
     "description": "Base context of the run: the bijective approach, the lemmas it rests on and the open obstacles.",
     "records": []},
    {"name": "generating-functions", "title": "Generating-function route (closed)",
     "description": "Closed by the counterexample k0007; the partial identities for small n remain valid. Open this if a task revisits generating functions.",
     "records": ["k0002", "k0004", "k0007"]}
  ]
}
```

`name` is an identifier (letters, digits, `_`, `-`), unique within the plan, and becomes the file name `knowledge/index/<name>.md`. `title` is a nonempty single line. `description` is nonempty prose telling a reader what the records inside have in common, what state that line of work is in, and which kind of task should open the module. `records` lists research and exploration records only, a record appears in at most one module, and a module other than `general` has at least one record (a module that has run empty is dropped). Module names are file names, so two names that differ only by letter case are rejected. The name `general` is reserved for the general module, which always exists and is rendered inside `knowledge/index.md`: every research and exploration record not named in another module belongs to it. A plan lists `general` only to give it a title and description of its own, which are then shown above its entries; records listed under it are redundant. The latest plan's layout is the one in force, so a plan carries the previous layout forward and republishes it, edited, every round. The checker confirms the structure, the existence and category of the records and that no record is filed twice; how the records are grouped is the plan's judgment ('Organizing the index' in [plan.md](plan.md)).

`wait` is `null` or `{"needed":"the input the user is to give", "reason":"why it is needed"}`. When a wait is declared, the runner stops all new dispatch. Even if the same output has requests, they wait as posted, and sessions already running are left to finish. When user input comes in, the wait is released and the input event is delivered to the next plan. A plan may leave requests if work is expected to be needed during the wait, but must judge for itself whether actually performing them is meaningful. The check does not judge that research value.

## 7. Official check and integration order

Python 3.12 or later, standard library only. The session runs the following command, and the runner performs **the same check** again with the `check_session` function below. The argument is **one session folder**, not the instance or `output/`.

```powershell
python C:/path/to/skill/check.py C:/research/example/sessions/s0001
```

Success is exit code `0` and standard output `{"ok":true,"errors":[]}`. A format or reference failure is exit code `1`, with the location and reason of the first error in standard output such as `{"ok":false,"errors":["output.json.results[0].exposition: ..."]}`. Fix that error and run the same command again. A command-argument usage error is argparse's explanation and exit code `2`. The check result changes no files.

Python consumers can call `check_session(session: str | pathlib.Path) -> list[str]`. An empty list is a pass, and a one-element list is the reason of the first failure. JSON parsing, encoding and ordinary file-access errors also return as this diagnosis. It does not swallow programming errors. The CLI and the function use the identical check of `Checker.run()`.

The checker confirms the required items and format of input and output, the agreement of categories, the existence of file, record and result references, and the target of a research review and the completeness of its per-result items. Every plan output is also checked for the global glossary files and entry structure and for the index layout of the preceding sections, and every research, exploration and peer output for its local glossary. It does not judge the mathematical meaning of definitions, the identity of objects, the accuracy of the scope of acceptance, whether the output conforms to the glossaries, whether a local name collides with a global one, whether a candidate deserves adoption, or whether records are grouped into the right modules. It does not recursively check referenced records as a whole or judge the currency of existing records. It does not run Lean, and does not judge the correctness of expositions and evidence, goal satisfaction, the mathematical validity between review verdicts, or the value of a plan. Whether the knowledge used was referenced without omission is the session's responsibility.

The runner consumes this contract in the following order.

1. Prepares `input.json` and launches a new session. The session writes the published output, confirms it with the check above, and ends. There is no separate approval or completion field.
2. When the process ends, runs the check above again regardless of the exit code and the manner of exit. If there is no output or it fails, does not integrate it and hands it to the next plan as a `session_failed` event.
3. If it passes, assigns a new record ID and copies **the entire contents of `sessions/<ID>/output/`** into a new `knowledge/<record ID>/`. `output.json` is copied too, and internal paths are not changed. The target directory must be new, and existing files are not overwritten. The input, the work folder and the logs are not copied and remain in the session folder. Commits the new record to the instance Git.
4. Reads the requests from an integrated plan. Attaches one default peer to an integrated research record or exploration, and after a peer is integrated, one review of the work–peer bundle. The integration of an exploration, a peer or a review each becomes a plan event. If an integrated goal review says achieved, completes. After completion no new sessions are launched, including automatic peers, reviews and plans, but the outputs of sessions already running go through the same re-check and integration when they end.

The `work/` of a session whose processing ended in integration or failure is compressed by the runner into `work.tar.xz` in the same session folder, and after the archive is verified the original directory is deleted. After that the files cannot be read at the `work/` path and the archive must be extracted. The timing of compression and the preservation rules on failure are defined by [RUNTIME.md](RUNTIME.md).

The runner keeps a single runner, the concurrency cap and one plan at a time. During a user stop, an external-input wait, a provider-limit wait or a halt after consecutive plan failures, no new sessions are launched. A session that has ended is not relaunched as it is. The release condition of each stop, process management, restart and state saving are defined by [RUNTIME.md](RUNTIME.md).

## Carrying over existing instances

The published records of the former four categories and their input and review formats continue to be read. The verdicts of past records are not changed. If existing settings have no peer defaults, the review model and effort are copied and used, and explicit peer defaults or a plan's selection take precedence. The inputs and models of sessions still running are not changed. Automatic peers are assigned starting with the research records and explorations newly integrated after the reorganization. Legacy automatic research review requests already posted are performed in their meaning. Past explorations are not assigned retroactively and automatically; if needed, a plan requests them in peers. For an instance created before the English port, the last plan's `glossary.md` still carries the former Korean field labels (이름·기호 … 출처, header 칸/내용); the next plan rewrites them into the current English labels, because the checker accepts only the current labels. `knowledge/index.md` is rebuilt with English labels automatically at the next start.

For an instance created before index modules and local glossaries existed, the index is rebuilt at the next start without plan entries and with every record in the general module, since no plan has declared a layout yet; the next plan declares one. Records published before the change have no `glossary-local.md` and are read as before, with their names defined in their expositions and, where they exist, in their `glossary-proposals.md`. The next plan harvests candidates both from such legacy proposals files and from the local glossaries of new records. Published records are not modified to add a local glossary.
