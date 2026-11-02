# do-math

do-math is a multi-agent management system that provides governance for autonomous mathematical research. It consists of instruction documents that direct agent behavior and a Python program, the runner, which dispatches the agents. You can give it a goal, such as a theorem to prove, a computation to carry out or a question to settle from the literature, and the runner then keeps the work going across many sessions, each a fresh conversation with a single job: some decide what to try next, some attempt proofs and computations, and others verify what the rest have produced. The run ends when a reviewing session judges that the goal has been met.

Splitting the work this way addresses two problems. Long research does not fit in one conversation, and a model checking its own work tends to miss its own mistakes. So sessions share a folder rather than a conversation. Each one starts fresh, reads what earlier sessions recorded there, and leaves its results for the ones that follow. No result is relied on until a different session has reviewed it, and when the result is a Lean proof, the review includes recompiling it.

What you end up with is that folder. At its center are mathematical expositions meant for people to read. Around them are the Lean source of the formalized results, computation code and data, the approaches that failed, the questions still open, and a review of every result. For a goal that asks for a proof, the default standard is a Lean theorem stating the goal, which a reviewer has recompiled and found free of `sorry` and of axioms beyond the standard three, together with an exposition that the reviewer judged to say the same thing.

do-math is meant for problems that take many attempts, where what failed should shape what is tried next and every result needs verification before anything is built on it.

The repository also contains the supporting skills I use to develop and operate do-math, and a few standalone tools I built alongside it. The do-math skill itself — the session instructions, the file contract, the operating documents and the strings the runner writes — is in English. Most of the *supporting* skills and the standalone tools' documentation are still in Korean; those links are marked (Korean).

## How a run works

Each goal is researched in its own instance, which lives in a folder with its own Git repository. The folder holds `goal.md`, where you state the goal, the conditions the result must meet and what the sessions may do; `settings.json`, which names the models and tools to use; a folder for every session; and `knowledge/`, where the results accumulate. Within the limits set in `goal.md`, the sessions decide for themselves how to break the problem down and which methods to try.

The runner dispatches each task to a new session: a fresh, non-interactive Claude Code or Codex conversation (`claude --print` or `codex exec`) that runs under your own login and subscription. do-math never calls model APIs directly. A session reads its task and the existing records, writes its results into its own folder, checks their format with `check.py`, and exits. The runner then runs the same check. If the output passes, the runner copies it into `knowledge/` as a new record and commits it to the instance's repository. do-math calls this publishing, although nothing leaves your machine at this step. If the output fails, nothing is published and the failure is passed to the next plan.

There are five kinds of session:

| Session | What it does |
|---|---|
| plan | Decides what happens next. It reads the goal, the previous plan's notes and the published records, then requests research, explorations, extra peers or reviews, or a goal review. When it needs a decision that only you can make, it pauses the run and asks. Every plan also rewrites the research status and the global glossary, and decides how the index is split into modules. |
| research | Works on one assigned question by proof, counterexample search, computation or literature search. Proofs are formalized in Lean by default, compiled through the instance's Lean broker. Partial results and failed attempts are recorded along with successes. |
| explore | Gets to know the problem without a question to answer, for example by working through small cases, restating the problem or looking for connections to other areas. It labels each claim with one of five epistemic statuses: verified, observed, conjecture, hunch or literature. Plans ask for explorations early on and when progress stalls. |
| peer | Reads a newly published research or exploration record as a fellow researcher would, and works through the mathematics itself. It can confirm, criticize or extend the work, but gives no verdicts. The runner dispatches one automatically for every such record. |
| review | Decides what the work and the peer's response actually establish, result by result. The runner dispatches one automatically after every peer response. A goal review instead judges everything published against the goal. |

Together they form a loop:

```text
plan ─┬─> research ─> peer ─> review ─┐
      ├─> explore  ─> peer ─> review ─┤
      │                               └─> events ─> next plan
      └─> goal review ─> "achieved" completes the run
```

The plan is the only session that steers. Whenever a review, an exploration or a peer response is published, a session fails, or you send input, the runner records an event. As soon as no plan is running and a slot is free, it dispatches a new plan and hands it every event since the last one. A published research record is not an event in itself; the review that follows it is. Up to `max_sessions` sessions run at once (eight by default), and only one of them can be a plan.

### One Lean broker per instance

Sessions do not run Lean themselves. Each instance has a single process, the Lean broker, which the runner starts and keeps alive for as long as it runs, and every compile goes through it. A session submits a file together with its estimate of how much memory the compile will need at its peak. The broker measures what the file's imports alone cost, the first time it sees that set of imports, and keeps a table of what compiles have cost since; it then starts queued compiles within one memory budget, reserving the part of each compile's memory that is certain in full and pooling the uncertain parts statistically, so that several compiles can share the budget without adding up their worst cases. It never stops a compile for using more memory than was estimated. The only compiles it cancels are those of sessions that have already ended. A compile keeps running, and keeps its result, even if the session's shell tool stops waiting for it, and the session gets back Lean's output and exit code together with the measured peak memory and duration. When a session's Lean is split into modules of its own that import one another, it hands the broker the module root and the target files, and the broker compiles the modules in dependency order, running independent ones side by side within the budget, and keeps every compiled module in a per-instance cache keyed by its content, so that later builds of the same sources by any session, a reviewer's recompilation included, reuse them. [LEAN.md](.claude/skills/do-math/LEAN.md) explains what a compile costs, the commands, the estimate, the scheduling rule and the settings, and how to write Lean that compiles cheaply.

### Keeping verification independent

Whether a result can be used is decided by its review, and do-math keeps that decision away from the session that produced the result.

- Peer and review sessions receive the published records and their own task, and nothing else: not the author's working files and not its logs. This is a rule the runner follows when it hands out work, not a sandbox.
- A reviewer writes down its own judgment before it reads any earlier review of the same work.
- A reviewer recompiles the Lean source in its own copy and runs `#print axioms` on every theorem. Only `propext`, `Classical.choice` and `Quot.sound` are allowed, plus whatever `goal.md` explicitly permits, and `sorryAx` never is. A clean compile is not enough, because Lean accepts a `sorry` with only a warning.
- Every result gets four verdicts: whether the argument supports the claim, whether the Lean source compiles within the allowed axioms, whether the exposition says the same thing as the Lean theorem, and whether it uses the global and local glossaries correctly. Only the first three decide whether the result is accepted.
- A result whose reviews disagree is not relied on, and neither is a result that builds on one that was rejected. A plan cannot overrule a negative verdict; only another review can.
- Sessions can run on different models. Running reviews on Claude while research runs on Codex, for example, makes it less likely that a reviewer shares the author's blind spots.
- Only a goal review can finish the run. A plan that believes the goal has been met has to request one.

### What the sessions share

Besides the records themselves, sessions rely on two documents that every plan rewrites. `research-status.md` sums up what is established, what is open, what has failed and what is under way. `glossary.md`, the global glossary, fixes a single name and definition for each object the research shares across sessions; only plans change it. Each research, exploration and peer record carries its own local glossary, `glossary-local.md`, for the names it uses internally, and flags in it the entries it thinks the run should share; the plan adopts, identifies or declines those candidates. The runner also keeps the index, `knowledge/index.md`, which lists the research and exploration records with their current reviews. On a long run the plan splits the index into modules: `index.md` keeps the records every session needs as base context, and records that only some tasks need are filed into further module files under `knowledge/index/`, each with a description, so that a session opens only the modules its task concerns.

### When a run stops

No session has a time limit, and there is no cap on how many sessions a run uses, so a long run can take a large share of your subscription's usage. The runner stops dispatching new sessions in five situations:

| Situation | What it takes to continue |
|---|---|
| A goal review returns `achieved`. | Nothing; the run is finished. Sessions already running are completed and published, and then the runner exits. |
| You run `stop`. | `resume`. Sessions already running carry on in the meantime. |
| A plan asks you a question, for instance whether to narrow or change the goal because it has run out of approaches. | Your answer, sent with `input`. do-math does not notify you, so look at `status` from time to time. |
| The provider reports a usage limit. | Nothing. The runner waits until the reported reset time, or for `limit_wait_seconds` if no time was given. |
| Three plans in a row fail for reasons other than a usage limit, which usually means a broken login, model name or CLI path. | Fix the cause and run `start` again. |

## Requirements

- Python 3.12 or later. The runner and the checker use only the standard library.
- Git.
- The Claude Code CLI, the Codex CLI or both, installed and logged in. Your settings decide which ones are used.
- Lean 4, which the runner's Lean broker runs on the sessions' behalf. Mathlib is optional.
- Optionally, scholarly-mcp for literature search (see [Standalone tools](#standalone-tools)). It needs its own Python environment with the packages pinned in [requirements.txt](services/scholarly-mcp/requirements.txt).

I develop and run do-math on Windows 11, and the commands below use PowerShell. The runner's process handling is also written for Linux, but I have not tested it there. macOS is not supported, because the runner tracks processes through `/proc`.

## Before you run anything

**Sessions run without permission prompts.** The runner starts Claude Code with `--dangerously-skip-permissions --permission-prompts none`, and Codex with `approval_policy="never"` and `--sandbox danger-full-access`. Each session is told to stay inside its own folder, but nothing at the operating-system level enforces that, so run do-math only on a machine and account where you are comfortable with it.

**Sessions pick up your own configuration.** Your user-level settings, your hooks, and any `CLAUDE.md` or `AGENTS.md` the CLI finds apply to every session.

**What the sessions read and write goes to the model provider,** Anthropic or OpenAI, as with any other use of their CLIs.

**This repository's own settings skip prompts too.** `.claude/settings.json` sets Claude Code's default permission mode to `bypassPermissions`, and `.codex/config.toml` gives Codex full access with no approval prompts. That is how I run long research on my own machine. If you do not want it, change these files before you open the repository with Claude Code or Codex.

**Some paths point at my machine.** The scholarly-mcp entries in `.mcp.json` and `.codex/config.toml` use absolute paths under `C:/math`. Change them to the location of your clone, or remove them if you do not use scholarly-mcp.

## Starting a run

### From Claude Code or Codex

Open Claude Code or Codex in this repository and ask it to start research on your goal. The do-math skill writes `goal.md` and `settings.json`, creates the instance, starts the runner as a background process that keeps going after the conversation ends, and tells you where to find the results. It asks you something only if the meaning of the goal, or a permission that only you can give, is unclear.

### By hand

1. Make sure `python` (3.12 or later), `git` and the CLIs you plan to use are installed and logged in, and that Lean runs.

2. Write `goal.md` in UTF-8. State the goal, the conditions the result must meet and what the sessions may do. Say what counts as done, and leave the strategy to the sessions. For example:

   ```markdown
   Prove in Lean that n + 0 = n for every natural number n, and write an exposition faithful to that proof. Natural numbers include 0.
   ```

   A goal that asks for a proof or disproof needs an accepted Lean theorem by default. If an informal proof is enough, or you want some other standard, say so in `goal.md`. The session instructions are written in English, so sessions write their records in English unless you say otherwise; if you want the records in a particular language, say that in `goal.md` as well.

3. Write `settings.json` in UTF-8. The paths and model names below are placeholders; use your own installation paths and models your CLIs accept.

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
       "env": {}
     }
   }
   ```

   - A model is written as `codex/<model>` or `claude/<model>`. The prefix picks the CLI, and the rest is passed to it as the model name.
   - Claude accepts the efforts `low`, `medium`, `high`, `xhigh` and `max`. Codex receives the effort string unchanged.
   - `defaults` sets the model and effort for each kind of session. A plan can override them for a single request, and records why when it does.
   - `max_sessions` counts sessions of every kind together.
   - `limit_wait_seconds` is how long to wait after a usage limit when the provider gives no reset time.
   - `lean.command` is run by the instance's Lean broker with the absolute path of a Lean file added as the last argument. With `"cwd": null` it runs in the submitting session's own folder.
   - To use Mathlib, set `command` to `["<path>/lake.exe", "env", "lean"]`, set `version_command` to the same with `"--version"` added, and set `cwd` to the absolute path of a Mathlib project. If Lean's `bin` folder has to be on `PATH`, write the full value into `env.PATH`; JSON does not expand `$env:PATH`.
   - The `lean` block also accepts optional keys for the broker: `memory_budget_mb`, `confidence`, `min_free_memory_mb`, `cpu_threads_budget`, `threads`, `priority`, `max_passes`, `calibration_expect_mb` and `default_spread`. Their defaults are derived from the machine; [LEAN.md](.claude/skills/do-math/LEAN.md) defines them.

   Section 1 of [protocol.md](.claude/skills/do-math/protocol.md) defines every field.

4. Create the instance at a path that does not exist yet, either outside this repository or under the ignored `.skill-workspace/` folder, so that its Git repository stays separate from this one. Then start the runner:

   ```powershell
   $skill = 'C:/path/to/do-math/.claude/skills/do-math'
   $instance = 'C:/path/to/do-math/.skill-workspace/do-math/add-zero'
   python "$skill/runner.py" init $instance --goal C:/path/to/goal.md --settings C:/path/to/settings.json
   python "$skill/runner.py" start $instance
   python "$skill/runner.py" status $instance
   ```

   `start` returns once it has confirmed that the new runner is alive, and prints the runner's PID and the paths of its log files. You can then close the terminal. If `init` fails partway, fix the problem and start over at a new path rather than reusing the half-created folder.

## Reading the results

Everything published lives under `<instance>/knowledge/`, one folder per record, each with an `output.json` that points to the record's files.

Start with `knowledge/index.md`. It lists the research and exploration records of the general module with the title and summary each session wrote, links to their peer responses and current reviews, and flags records that have not been reviewed yet or whose reviews conflict. At the top it links the latest research status, the global glossary and the latest plan record, shows the verdict of any goal review, and lists the other modules the last plan declared, each a file under `knowledge/index/` with the same kind of entries and a description of what it holds.

From there, open a record's `output.json`. For research, each entry under `results` points to its exposition (`exposition`), says what the author actually verified (`verification`) and lists any Lean files (`lean.sources`), with `failed_attempts` and `open_questions` alongside; the names the exposition uses internally are defined in the record's `glossary-local.md`. Then read the reviews linked from the index. A result counts as established only when its current reviews accept it, they do not conflict, and nothing it builds on has been rejected. Being published means only that a record passed the format check.

When the run is complete, `status` shows the ID of the deciding goal review in `state.complete`, and that review's `goal.reason` explains how the goal was met. The instance's Git log has one commit for each published record.

## Operating a run

Every command has the form `python "$skill/runner.py" <command> $instance ...` and prints JSON. Use shells with the same privilege level for every command on an instance; on Windows, mixing elevated and normal shells can make the runner mistake a live process for a finished one.

| Command | What it does |
|---|---|
| `init $instance --goal <file> --settings <file>` | Creates a new instance and its Git repository. |
| `start $instance` | Starts the runner in the background and confirms that it is alive. Run it again to restart after a crash or a reboot. |
| `status $instance` | Shows whether the runner is alive (`runner_alive`), what is blocking new dispatches (`dispatch_blocks`), the Lean broker and its queue (`lean`), and every session and request (`state`). It changes nothing. |
| `stop $instance` | Stops the runner from dispatching new sessions. Running sessions finish and are published. |
| `resume $instance` | Undoes `stop`. It does not start a runner that is not running. |
| `input $instance --file <file>` | Passes the text of a UTF-8 file to the next plan. This is also how you answer a plan's question. |
| `kill-session $instance <session id>` | Ends one session's CLI process, though not any processes that the CLI started; its Lean compiles are cancelled by the Lean broker once the session is dead. Whatever the session left in its output is still checked, and published if it passes. Session IDs are listed in `status`. |
| `index $instance` | Rebuilds `knowledge/index.md` and the module files under `knowledge/index/` while the runner is not running. |
| `run $instance` | Runs the runner in the foreground for debugging. It does not return until the run ends. |

If the runner or the machine stops, run `start` again on the same instance. The runner recognizes each recorded session by its process ID and creation time, waits for the ones still running, and processes whatever the finished ones left behind. It never relaunches a session that has already ended. Recovery depends on the files under `runner/`, so do not delete `runner/lock` or edit anything there by hand.

[SKILL.md](.claude/skills/do-math/SKILL.md) and [RUNTIME.md](.claude/skills/do-math/RUNTIME.md) cover every command's states and edge cases.

## Repository layout

```text
.claude/
  skills/do-math/     the runner, checker, session instructions and tests
  skills/...          11 supporting skills (listed below)
  agents/             subagent definitions with fixed model and effort
  CLAUDE.md           project instructions for Claude Code
.agents/              a generated copy of the skills for Codex, with Codex's project instructions
.codex/               Codex configuration
.mcp.json             MCP servers registered for Claude Code
AGENTS.md             short project instructions for Codex
services/             standalone tools (listed below)
기억/                 the project's working memory, linked to commits
ROADMAP.md            planned work
```

Inside `.claude/skills/do-math/`:

| File | Content |
|---|---|
| `runner.py` | The runner and its commands |
| `check.py` | The format checker that both the sessions and the runner run |
| `cli_adapter.py` | Builds the Claude Code and Codex command lines and reads usage limits from their logs |
| `lean_broker.py` | The Lean broker, its job host and the commands sessions use to compile through it |
| `common.md`, `protocol.md` | Instructions that direct every session, and the file contract between the sessions and the runner |
| `plan.md`, `research.md`, `explore.md`, `peer.md`, `review.md` | Instructions that direct each kind of session |
| `SKILL.md`, `RUNTIME.md`, `CLI.md` | How to operate the runner and how it calls the CLIs |
| `LEAN.md` | The Lean broker: commands, the estimate sessions give, scheduling, settings, and how to write Lean that compiles cheaply |
| `tests/` | Tests that use fake CLI processes with the real checker and real Git: `python -B -m unittest discover -s .claude/skills/do-math/tests -v` |

## Standalone tools

None of these is needed to run do-math. When scholarly-mcp is registered as an MCP server, research and explore sessions use it for literature search; otherwise they search the web and say so in their records. I built the current version of do-math with async-development, but do-math does not use it at run time. The tools' READMEs are in Korean.

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

The do-math skill is in English: every term that carries a do-math-specific meaning has one fixed English name, used the same way in the session instructions, the file contract, the operating documents and the strings the runner writes. A freshly created instance behaves exactly as before the port. Instances created before it can still be restarted; their next plan relabels the inherited Korean glossary fields into English, as described in `protocol.md`. The supporting skills, the standalone tools' documentation, the working-memory directory and the commit messages are still in Korean; porting them is item 3 of the roadmap.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

This project is licensed under the [Mozilla Public License 2.0](LICENSE). Four skill directories are adapted from third-party projects and keep their original licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
