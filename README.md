# do-math

do-math is a multi-agent management system that provides governance for autonomous mathematical research. It consists of instruction documents that direct agent behavior and a Python program, the runner, which dispatches the agents. You give it a precise mathematical proposition, and the runner keeps the research going across fresh sessions: some choose questions and attempt proofs, some explore the mathematics, some formalize results in Lean, and others develop, review and organize what the research produces. The root is settled when an independent review validates a Lean proof of the proposition or its negation. The runner then finishes processing the remaining work.

Long research needs both continuity and independent judgment. Sessions share recorded mathematics: definitions, arguments, computations, failed approaches and unresolved opportunities. A peer reads a producing session's complete retained work and develops a record candidate for future researchers. A separate review assesses this candidate against that session's original material and checks any mathematics the peer added. Useful imperfect work is retained with the review's feedback, so a later researcher can distinguish established results from claims that need more work.

The result is a research folder with readable mathematical expositions, their evidence and independent assessments. Around those records are the current questions and their reviewed connections, a live board of occupied questions, a full shared glossary, and an index organized into modules. Each attempt uses this information to choose its own work. There is no planning session assigning its mathematical task.

The do-math skill and runtime documentation are in English. The repository also contains supporting skills and standalone tools, most of whose documentation is in Korean.

## How a run works

Each proposition is researched in its own instance, a folder with its own Git repository. It holds the fixed statement in `root.md`, the models and tools in `settings.json`, a directory for every session, and `knowledge/`, where reviewed records accumulate. User conditions are supplied explicitly. Within those conditions, researchers decide which questions and methods to pursue.

The runner launches each job as a fresh, non-interactive Claude Code or Codex conversation under your existing authentication. It uses the CLIs, not direct model API calls. Each worker receives a saved context containing its guides, the root, the full global glossary, current research views and the inputs specific to its role. Attempts choose their own mathematical target; the other roles receive the source work, node, candidate, evidence or publication batch they are to work on. Personal/project instructions, hooks and memories are excluded from worker launches. The worker's instruction references and user conditions are fixed at launch; published research and occupancy remain available as live information.

The root is the instance's first node: a precisely stated mathematical question. Other nodes arise from established, reviewed connections to the research. For example, if an attempt on P proves that Q implies P, review can admit Q as a new question even while Q remains unresolved. Solving a node means proving its statement or its negation.

There are six roles:

| Role | Responsibility |
|---|---|
| attempt | Chooses an unresolved node and tries to prove or refute it, retaining the work and obstacles. |
| explore | Develops understanding and insight by working with the mathematics from useful angles. |
| formalizer | Produces a Lean solution from reviewed informal mathematics and available formal dependencies. |
| peer | Reads a producing session's complete retained work, develops opportunities and writes its record candidate. |
| review | Independently assesses a candidate and its producing originals, or investigates defective evidence and the later arguments that used that evidence. |
| organizer | Maintains shared terminology, groups records into modules and reconciles duplicate node identities. |

An attempt, exploration or formalizer is followed by peer and review. The runner publishes useful records with their assessments and commits them to the instance's Git repository. Publishing is a local operation. Records and their descriptions remain immutable; subsequent findings attach to them separately.

A node can be informally or formally proved or refuted. Informal solutions accepted by review remove nodes from the questions needing fresh attempts. Formalizers wait for the validated Lean dependencies their arguments require. Every formal solution receives an independent compile, an audit of the target's transitive axioms, and a comparison with the exact mathematical statement. The default allowed axioms are `propext`, `Classical.choice` and `Quot.sound`; `sorryAx` is never allowed.

An attempt ordinarily occupies each node it takes on until its work has passed through peer and review. The live board informs sessions of that occupancy, and they follow the coordination instructions. An attempt can add available nodes while keeping its earlier nodes occupied. Exploration has a broader purpose and may develop a proof when that improves understanding. Only one exploration cycle, including its peer and review, is present at a time.

Dispatch priority is **review → peer → formalizer → organizer → eligible explore → attempt**. Defaults are eight concurrent AI sessions, an exploration request every three attempt dispatches, and an organizer after four research publications. Spare capacity can also request exploration when no node is available for another attempt. A requested exploration is eligible once the preceding exploration cycle has finished, subject to the same capacity and model-availability conditions as other launches. Each role prefers Codex `gpt-6.1-sol/xhigh` and uses Claude `opus/xhigh` as its configured fallback. These settings are configurable.

### Lean compilation

Every compile goes through one Lean broker per instance. The broker schedules compiles against shared memory and thread budgets, measures their costs, retains results across shell-tool timeouts, and builds local modules in dependency order. Unchanged dependencies can be reused from its cache. Independent reviewers force a new target compile and retain the actual axiom output. [The Lean guide](.claude/skills/do-math/reference/lean.md) explains the commands, estimates and environment settings.

### Interruption and completion

A producing session interrupted by a provider limit or another execution failure leaves its retained material for peer processing. An incomplete final manifest does not discard its mathematics. Interrupted processing stages receive fresh sessions with their partial work. A provider refusal blocks launches through that provider; a model-specific refusal blocks only that model. Configured alternatives can serve later launches.

Formal completion of the root prevents new attempt and explore launches. Existing sessions retain their normal scope, including an attempt's ability to claim additional available nodes. The runner still launches peers and reviewers to process finished work, formalizers for accepted informal solutions whose dependencies are available, and organizers when a publication batch is due. Status distinguishes the root being settled from the runner having finished. There is no fixed session-duration cap or automatic cap on formalizer rounds for a node whose informal solution remains supported.

## Requirements

- Python 3.12 or later and Git. The runtime uses Python's standard library.
- Codex CLI, Claude Code CLI, or both, installed and authenticated.
- Lean 4; Mathlib when the problem requires it.
- Optional external tools, such as scholarly-mcp, configured explicitly in the instance.

Development and live verification use Windows. The process helpers also contain Linux support; the verification report states which paths were exercised. macOS process identification is not implemented.

Workers run unattended with file and command access under your account. Their workspace boundaries are instructions, not an OS sandbox. Their model providers receive the material they read, as in ordinary CLI use. The instance explicitly configures external tools while excluding personal/project behavioral instructions, hooks and memories.

## Starting a run

From Claude Code or Codex, ask the do-math skill to start research on a proposition. The operator prepares the statement and settings, launches the detached runner and reports where the work lives. The [operator entry point](.claude/skills/do-math/SKILL.md) and [operating guide](.claude/skills/do-math/reference/operations.md) explain the full path.

For a manual launch, write a UTF-8 `root.md` containing the exact proposition, for example:

```text
For every natural number n, including zero, n + 0 = n.
```

Prepare settings with your actual executable paths. The operating guide gives the full example; this minimal file overrides the Lean installation while retaining the model and scheduling defaults:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

Create an instance at a new path outside the repository or under its ignored `.skill-workspace/`, then start it:

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/add-zero'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

If you have standing conditions, submit their file with `input --file <file>` before `start`. Later standing inputs apply only to subsequently launched sessions. Changing the root's mathematical proposition requires a new instance.

`start` confirms its new process and returns log paths; the runner then continues after the terminal or operator conversation ends. Inspect those logs and status if launch confirmation fails before attempting another start.

## Reading and operating the instance

Start at `knowledge/index.md`, then follow records to their expositions and reviews. `knowledge/frontier.md` shows the mathematical questions and current evidence. `knowledge/glossary.md` supplies the shared definitions and aliases. `knowledge/board.md` shows occupied nodes and processing stages. A published record's description and its review assessment have different purposes; read both before using its results.

All commands have the form `python <skill>/runtime/runner.py <command> <instance> ...`.

| Command | Purpose |
|---|---|
| `status` | Read the root state, runner liveness, sessions, pending work and provider/model blocks. |
| `stop` / `resume` | Stop or resume new dispatch; already-running sessions continue. |
| `input --file <file>` | Supply standing information to future sessions. |
| `review --record <id>` | Request a comprehensive examination of published evidence. |
| `organize` | Request organization of current unprocessed publications. |
| `kill-session <id>` | End the identified CLI process, retaining its work for processing. |
| `start` | Restart after a runner crash or machine reboot, recovering existing work. |
| `render` | Rebuild derived views while the runner is off. |

The [operating guide](.claude/skills/do-math/reference/operations.md) explains states, failures, fallback and Lean environment changes. Preserve the instance's operational files when recovering; the runner uses saved process and publication identities to avoid duplicating work.

## Development layout and verification

Within `.claude/skills/do-math/`, the new implementation is in `runtime/`, worker guides are in `roles/`, and shared and specialist guides are in `reference/`. `SKILL.md` is the operator's entry point. `.agents/skills/do-math/` is the Codex mirror. Fresh instances use the new runtime; old top-level runtime files remain in this checkout for a research instance already using those paths.

The runtime tests use scripted CLI processes, the runtime's structural output checker and Git, and a controlled Lean stand-in. They check evidence propagation, occupancy, scheduling, glossary/index behavior, formal-evidence identity, interruption, recovery and context delivery. Run them with:

```powershell
python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v
```

Documentation is also read independently through the context assembled for each role. Live CLI and Lean probes complement the scripted tests. Their results and limits are recorded in [the implementation verification report](docs/do-math/rebuild-verification.md).

## Standalone tools

None of these is needed to run do-math. When explicitly configured for an instance, scholarly-mcp gives its workers academic literature search; otherwise they can use the available web tools and record their search limits. The standalone development tools are independent of do-math's runtime. The tools' READMEs are in Korean.

- [services/scholarly-mcp](services/scholarly-mcp/README.md): a local MCP server that searches 49 academic sources and saves bibliographic data, abstracts, full text and supplements. The public sources need no login; some of the others go through one university library's login.
- [services/continuous-development](services/continuous-development/README.md): a multi-agent management system for software development, made up of instruction documents that direct Codex sessions and a Python runner that dispatches those sessions in phases. Each phase runs several Codex task sessions in parallel, after which a manager session reads their reports and writes the next phase.
- [services/async-development](services/async-development/README.md): a multi-agent management system of the same kind, in which Codex workers each get their own copy of the code. A manager session reviews each result as it comes in, merges the work it accepts, and starts the next tasks as soon as their inputs are ready.
- [services/jev-cli](services/jev-cli/README.md): a command-line client for Jev, a hosted model from TypeSafe that returns a choice, a score and a probability for a question and material you give it. It is unrelated to do-math.

## Supporting skills

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

## Language

The new do-math operator and worker guides, file contracts, runtime output and README are in English. Supporting skills, standalone-tool documentation and the working-memory directory remain primarily in Korean.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

This project is licensed under the [Mozilla Public License 2.0](LICENSE). Four skill directories are adapted from third-party projects and keep their original licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
