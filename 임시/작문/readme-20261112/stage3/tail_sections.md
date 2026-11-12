## Reading a published knowledge base

### The top-level files and directories

A published knowledge base is the `knowledge/` directory of an instance. Its entry point is `index.md`, which lists records the organizer selected as shared context for new sessions, a directory of modules with their descriptions, and recent records not yet organized. Each entry shows the record's own description, written by its peer, and the review's short assessment beside it.

`frontier.md` gives every node's exact statement, its state (unresolved, informally proved or refuted, formally proved or refuted, or contested), the proofs that support that state with links to their records, the accepted relations with their premises and conclusions, how the node stands to the root, and any pending concern. After the nodes it lists the questions with their statements, grounds, state and source; a question the operator placed directly shows the operator as its source instead of a reviewed record. `glossary.md` is the shared vocabulary with each term's definition and its source record. `board.md` is the occupancy snapshot at the time the knowledge base was taken. `state.json` is a structured projection of the same evidence for programmatic inspection; its `proofs` object lists every supported proof with its claims and premises.

`records/` holds one directory per record, described below. `events/` holds one file per publication with its time, `organizations/` the organizer outputs, `questions/` the questions the operator published, and `reviews/` the comprehensive reviews, which examine already published evidence and therefore belong to no single record. The producing sessions' conversations and working files are not in `knowledge/`; they stay in the instance's `sessions/` directory, which the published knowledge base does not include.

### A record's directory

Each record is a directory under `records/` named by its identifier. `record.json` is the structured description: title, description, claims with their IDs and evidence, proposed nodes, relations, proofs, questions and terminology. `exposition.md` is the mathematical account. `evidence/` holds the code, data, logs and notes the account cites. `review/assessment.json` is the review's structured judgment, including the status of every claim and, for a formal proof, the compile job, the printed axioms and the source hashes; `review/feedback.md` is its full explanation. `provenance.json` names the producing, peer and review sessions. A formal record also has `lean/` with the sources and a `review/lean-evidence/` folder with the broker's retained compile output.

## Running do-math

### Requirements and what a run does on your machine

The runtime needs Python 3.12 or later and Git, and uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured. It needs Lean 4 in every case and Mathlib when the proofs will draw on it. Development and live verification were done on Windows; Linux is supported by the process helpers but has not been verified in a live run, and macOS is not supported.

Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read. A run has no cap on time, on the number of sessions, or on usage, and do-math collects no usage figures. do-math itself sends nothing outside your machine; publication is a commit to the instance's local Git repository, and the outbound traffic is the CLIs' own.

### Quick start

Clone this repository. From Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement; the conversation that handles the request is the operator, and it prepares the statement and settings, launches the detached runner and reports where the work lives. The skill is the folder `.claude/skills/do-math`, with its mirror for Codex at `.agents/skills/do-math`.

To launch by hand instead, write a UTF-8 `root.md` containing the exact statement and a `settings.json` that names your Lean installation, with the command that compiles a file and the command that prints the Lean version:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

This keeps the default models, which put Codex first and Claude second for every role and the reverse for peer and review; with only Claude Code installed, give the `models` list and the `roles` entries for peer and review Claude models only, as the running guide shows.

Then create the instance at a path outside this repository, or under its Git-ignored `.skill-workspace/` directory, and start the runner:

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/add-zero'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

The runner continues after the terminal or operator conversation ends, and `knowledge/` is updated with every publication. The [running guide](docs/do-math/running.md) covers the model and scheduling settings, Mathlib, the allowed Lean axioms, standing inputs, every runner command, how to end a run, and what happens on interruption and completion; the [operating guide](.claude/skills/do-math/reference/operations.md) in the skill is the complete reference for every setting and state.

## Repository layout, verification and tests

Within `.claude/skills/do-math/`, `SKILL.md` is the operator's entry point, `roles/` holds the six role guides, `reference/` the shared and specialist guides, `resume/` the texts delivered when a session is asked to reconsider ending, and `runtime/` the runner, the coordination tools, the Lean broker and their tests. `.agents/skills/do-math/` is the generated mirror for Codex. The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md), and the checks performed when it was installed, including live launches of both CLIs, a complete small instance whose root was formally proved with a Lean proof that a review session recompiled and checked, and recovery after a runner restart, are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md). The [full account of the first run](docs/do-math/first-run-parking-unimodality.md) and the [running guide](docs/do-math/running.md) are in the same folder.

The runtime tests use scripted CLI processes, Git and a controlled Lean stand-in. They cover evidence propagation, occupancy and leases, questions, scheduling, glossary and index rendering, formal-evidence identity, interruption, recovery and context delivery. Run them with:

```powershell
python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v
```

On 12 November 2026 the suite had 316 tests and all passed. These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce.

## Standalone tools and supporting skills

The repository also holds four programs that do not depend on do-math and are not needed to run it. Their READMEs are in Korean.

- [services/scholarly-mcp](services/scholarly-mcp/README.md): a local MCP server (a tool server that AI CLIs can call) that searches 49 academic sources and saves bibliographic data, abstracts, full text and supplements. The public sources need no login; some others go through one university library's login. When configured for an instance, it gives do-math's sessions literature search.
- [services/continuous-development](services/continuous-development/README.md): a multi-agent system for software development in which a Python runner dispatches Codex sessions in phases, with a manager session reading each phase's reports and writing the next.
- [services/async-development](services/async-development/README.md): a system of the same kind in which workers each get their own copy of the code and a manager merges accepted results as they arrive.
- [services/jev-cli](services/jev-cli/README.md): a command-line client for Jev, a hosted model from TypeSafe.

The repository's other skills support its development.

| Skill | What it does |
|---|---|
| graphify | Builds and queries a knowledge graph of do-math's own documents and scripts, for finding where a rule or procedure comes from |
| verify-rounds | Runs rounds in which several agents review a finished artifact and fix what they find |
| write-for-reader | Guides the design, writing and revision of text that a person or an AI will act on, and interviews the user when a decision is missing |
| grilling, grill-me | Interview the user one question at a time to stress-test a plan |
| skill-creator | Creates, improves and benchmarks skills |
| writing-skills | Explains principles for writing a skill's description, structure and tests |
| simplify | Prompts a short self-check: is this the simplest way to do what I am trying to do? |
| memory-harness | Defines the structure and rules of the working-memory graph in `기억/` |
| commit-harness | Sets out the commit procedure that pairs every commit with a memory node |
| dream-harness | On request, combines accumulated memory nodes into current principles and conventions |

## Language, roadmap, citation and license

The do-math operator and role guides, the file contracts, the runtime output and this README are in English. The supporting skills, the standalone tools' documentation and the working-memory directory are primarily in Korean. Planned work is in [ROADMAP.md](ROADMAP.md).

To cite the software, use the repository's [CITATION.cff](CITATION.cff), which GitHub renders under "Cite this repository". To cite the published knowledge base of the first run, cite the version you read by its own DOI (version 2 is 10.5281/zenodo.24142218) or all versions together by the concept DOI 10.5281/zenodo.24110810. The knowledge base is licensed CC BY 4.0 on Zenodo.

This project is licensed under the [Mozilla Public License 2.0](LICENSE). Four skill directories are adapted from third-party projects and keep their original licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
