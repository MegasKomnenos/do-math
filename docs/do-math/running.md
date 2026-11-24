# Running do-math

This guide covers the requirements, what a run does on your machine, starting a run through the skill or by hand, the settings, the commands, reading the results, ending a run, and interruptions and completion. The repository [README](../../README.md) gives a quick start taken from it and defines the terms used here, such as root, canon, element, record, standing, settled, formal, frontier, candidate, root check, standing input and Lean broker. The [operating guide](../../.claude/skills/do-math/reference/operations.md) in the skill is the reference that the operator works from, and it holds the detail that this guide leaves out.

## Requirements

The runtime needs Python 3.12 or later and Git, and it imports only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured, and do-math adds no accounting of its own.

The runtime needs Lean 4 in every case. `init`, the command that creates an instance, compiles the Lean form of the root. Lean therefore has to be installed before the instance exists, and it has to be named in the settings unless `lean` is on your PATH. The runs recorded so far used Lean 4.32.0 and 4.36.0. Mathlib is needed when the Lean definitions of the problem, or the proofs the sessions will write, draw on it.

The default settings attach one external tool to every session: scholarly-mcp, a local server for academic literature search that this repository keeps under `services/scholarly-mcp` and that runs in a Python environment of its own. `init` refuses to create an instance when it cannot find that environment's Python, and a settings file with `"mcp_servers": {}` creates an instance without external tools. The server's own README, which is in Korean, gives these commands for installing the environment, to be run from the repository root in PowerShell:

```powershell
python -m venv services/scholarly-mcp/.venv
& services/scholarly-mcp/.venv/Scripts/python.exe -m pip install -r services/scholarly-mcp/requirements.txt
& services/scholarly-mcp/.venv/Scripts/python.exe -m playwright install firefox
```

Beyond the servers named in the instance's settings, the sessions have the CLIs' built-in tools, which include shell commands and web search.

Two commands are used once the research has results, and one of them has a requirement of its own. `paper.py`, which writes the paper, needs one of the TeX programs `tectonic`, `latexmk` and `pdflatex` to produce the PDF; without one it still writes the manuscript. `depmap.py`, which draws the dependency map, needs only Python.

Every run whose operating system is recorded was made on Windows. The runtime has code for Linux as well, where it reads `/proc`, and no recorded run has used that code. macOS is not supported, because the runtime identifies processes and reads the machine's free memory only by the means that Windows and Linux provide.

## Permissions, caps and outbound traffic

Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read, as in ordinary CLI use. A run has no cap on time, on the number of sessions it launches in all, or on usage, and do-math collects no usage figures. The only limit of that kind is on the number of sessions running at once. A run ends when the root is formally settled and the remaining work has been processed, or when you end it as described below.

The runner, the session hosts and the Lean broker open no network connection themselves, and publication means a commit to the instance's local Git repository. Outbound traffic comes from the programs they start. The CLIs talk to their model providers and to the web tools the sessions use. The literature server sends queries to public literature services; every session starts its own copy, and all the copies send from your one network address, so a service that limits requests per address may turn some of them away. Any further tool server named in the settings adds whatever traffic it makes. And `paper.py` downloads the sources of its example papers from arXiv when they are not yet on the machine.

## Starting through the skill

To install, clone this repository. The skill is the folder `.claude/skills/do-math`, and `.agents/skills/do-math` is the copy of it generated for Codex. From Claude Code or Codex started in the repository, ask the assistant to start research on a statement with the do-math skill. The conversation that handles that request is the operator. It works out the exact statement with you in words, writes the Lean definitions and the Lean statement together with you, checks the definitions against the small cases for which you have values, prepares the settings and creates the instance. It then asks you to read what was fixed and explains how the Lean statement reads. Only after you have confirmed does it launch the detached runner and report where the work lives. The [operator entry point](../../.claude/skills/do-math/SKILL.md) and the [operating guide](../../.claude/skills/do-math/reference/operations.md) explain the full path.

## Starting by hand

A manual start takes the same steps as the operator takes. An instance is created from a root file and a folder that holds the beginning of the Lean library, usually with a settings file, all of which you prepare outside the new instance directory. The subsections below take them in order, with the records and the checks that belong to the Lean folder, and then come to creating the instance, confirming the root, standing inputs and starting the runner. Everything inside an instance is written in English, so the root file and the records are in English whatever language you work in.

### The root file

The root file is a UTF-8 text file with the mathematical statement in words, with its objects, assumptions, domains and quantifiers defined. When your material gives values for small cases, such as the first rows of a table, include them; you will check the Lean definitions against them. For example:

```text
For every natural number n, the sum of the first n odd natural numbers is n squared.
The sums for n = 3 and n = 4 are 9 and 16.
```

### The folder with the Lean library

The folder holds the first state of the instance's Lean library, which `init` copies into the instance.

```text
<canon folder>/
  lean/<Library>/Defs.lean     the definitions of the objects the statement speaks of
  lean/<Library>/Root.lean     the root statement, importing the definitions
  records/<name path>.md       one record for each declaration
  bibliography.bib             optional: sources of definitions or statements taken from the literature
```

`<Library>` is the one top-level module name under which every module of the instance will live, including the modules the sessions add later. Choose a name that describes the mathematics, such as `OddSum`. It must differ from `Init`, `Lean`, `Std` and `Lake`, and from the first component of any library the files import, such as `Mathlib`. Each component of a module path consists of ASCII letters, digits and `_`, and does not begin with a digit. The file names `Defs.lean` and `Root.lean` are examples.

Put the definitions in one module and the root statement in a module of its own that imports it. A proof of the root will later replace the body of the root's declaration where it stands, and it will need to import modules that the sessions add, which in turn import the definitions. If the definitions were in the root's module, those modules and the root's module would have to import each other, which Lean does not allow.

The files follow the conventions of every file of the canon. Each begins with the word `module`, imports with `public import`, and puts its declarations under `@[expose] public section`. The root is a `theorem` whose proof is left open with `by sorry`. No file declares an `axiom`, and no definition contains `sorry`. This pair of files shows the shape for the example above:

```lean
module

@[expose] public section

namespace OddSum

/-- The sum of the first `n` odd numbers. -/
def oddSum : Nat → Nat
  | 0 => 0
  | n + 1 => oddSum n + (2 * n + 1)

example : oddSum 3 = 9 := by decide
example : oddSum 4 = 16 := by decide

end OddSum
```

```lean
module

public import OddSum.Defs

@[expose] public section

namespace OddSum

/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem sum_eq_square (n : Nat) : oddSum n = n * n := by
  sorry

end OddSum
```

The first file is `lean/OddSum/Defs.lean` and the second `lean/OddSum/Root.lean`. The root declaration is `OddSum.sum_eq_square`, and that full name is what `init` takes as `--root-declaration`. The two `example` lines are checks of the definition on known values, which a later subsection explains; they are not elements and need no record.

Every later module imports the definitions, so every compile of the instance loads whatever the definition modules import. Import the modules of Lean's library or of Mathlib that the definitions use and no others; an `import Mathlib` in a module that everything imports is paid for at every compile of the run.

### A record for each declaration

Every declaration you write, whether a definition, a structure or inductive type, a theorem or an instance, is an element and needs a record; a declaration marked `private` is not an element and needs none. The record of the declaration `A.B.c` is the file `records/A/B/c.md`, and when a record is missing, `init` names the path it expects. A record begins with a header between two lines of `---` and continues with sections under second-level headings.

| Part | Content |
|---|---|
| `weight` (header, required) | `unit` or `step`. A unit is something a reader of the proof's structure would name; a step is a piece inside one proof. The root is a unit. |
| `short` (header) | A short name, which the frontier shows in place of the description. |
| `source` (header) | For a definition or statement taken from the literature, the key of its entry in `bibliography.bib`. |
| `## Description` (required) | What the element is, in a line or two. |
| `## Statement` | The statement, or the definition, in ordinary mathematical language. For the root this is the statement of the root file. |
| `## Explanation` | What the statement says about the object, why the definition was chosen, and how the Lean form corresponds to the mathematical one: counting that starts from zero, a normalization, a convention at a boundary. |
| `## Literature` | For something taken from the literature: the source, how much of it was read, and where in it the statement is found. |

Write no `## Proof` section in the root's record. The root has no proof when the instance is created, and a nonempty proof section would make the canon show it as having one. The record of the definition in the example, `records/OddSum/oddSum.md`, could read:

```markdown
---
weight: unit
short: sum of the first n odd numbers
---
## Description

The sum of the first n odd numbers, defined by recursion on n.

## Statement

For a natural number $n$, $\operatorname{oddSum}(n) = 1 + 3 + \dots + (2n - 1)$, and $\operatorname{oddSum}(0) = 0$.

## Explanation

The recursion adds the odd number $2n + 1$ at the step from $n$ to $n + 1$, so the argument of the Lean function counts how many odd numbers have been added.
```

### Checking the definitions on known values

A definition that compiles can still denote a different object from the one you meant. Lean's functions are total, so conventions fill in what the mathematics leaves undefined, and a small slip changes the object without causing an error: subtraction of natural numbers stops at zero, division by zero returns zero, and a recursion can start one index early or late.

The check available to you is a comparison with known values. Evaluate the Lean definitions on the small cases for which your material gives values, and write each value into the Lean files as something the compiler must prove, as the two `example` lines above do. A command that only prints a value, such as `#eval`, confirms nothing, because `init` shows no output of a compile that succeeds. A check can be written in two ways. An `example` is compiled and then discarded, whereas a named theorem with a complete proof stays in the library as an element: it needs a record, and a session that later looks up what the canon knows about the definition finds it. Put the checks in the module of the definitions or in a module of their own, and not in the root's module, which holds the root statement and nothing that later work will use.

Agreement on these values is evidence that the definitions denote the intended objects. It does not prove that they do, and the values checked say nothing about cases unlike them.

### Settings

Prepare `settings.json` with your actual executable paths. This minimal file names the Lean installation, with the command that compiles a file and the command that prints the Lean version, and keeps every default:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

The main defaults are these.

- `max_sessions`: eight sessions at a time.
- `launch_interval`: attempts and explorers are launched at least 180 seconds apart.
- `explore_every`: 1, meaning that the runner requests an exploration each time the count of attempt launches reaches a multiple of this number. The runner also requests one when it has spare capacity and no statement is available to a new attempt. A request is served when a question is open and no session has it or is waiting for it.
- `organizer_every_records`: an organizer is launched once four published changes have not yet been examined by an organizer.
- `max_end_resumptions`: a session is resumed up to three times, either to reconsider ending or, for a review or an organizer, because its output is not yet complete.
- `acceptance.decline_reducible_proofs` and `acceptance.decline_uncomprehended_computation`: both true. With the first, a review does not yet accept a correct proof that can still clearly be made simpler; with the second, it does not yet accept a correct proof that settles part of its statement by a large computation carried out without understanding. Such a proof is still published, with the standing "correct, held back".
- `lean.command` and `lean.version_command`: `lean` and `lean --version`, as found on your PATH.
- `lean.allowed_axioms`: `propext`, `Classical.choice` and `Quot.sound`. The list can be extended, and `sorryAx` is never allowed.
- `mcp_servers`: the one server `scholarly`, started with its `--public-only` option. Each session starts its own copy of the server, and under this option a copy creates no login and serves only the sources that are reached through public interfaces, about twenty of them, among them zbMATH, arXiv, Crossref, OpenAlex and Semantic Scholar. A settings file that gives `mcp_servers` replaces this default with what it gives.

The `models` list is the ordered model preference for every role, and an entry under `roles` replaces it for that role; each entry names a model as `provider/model` together with the CLI's reasoning-effort setting. The default `models` list puts Codex `gpt-6.1-sol` first and Claude `opus` second, and the default `roles` entries for peer and review reverse that order, so that a candidate and its review come from a different model than the work they are about. With only Claude Code installed, list Claude models only, both in the common list and in the two role entries, as in this example, where `claude/opus` names the Claude CLI's `opus` model; with only Codex installed, do the same with `codex/gpt-6.1-sol`:

```json
{
  "models": [{"model": "claude/opus", "effort": "xhigh"}],
  "roles": {
    "peer": [{"model": "claude/opus", "effort": "xhigh"}],
    "review": [{"model": "claude/opus", "effort": "xhigh"}]
  },
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

To use Mathlib, set `lean.command` to your Lake executable followed by `env` and `lean`, `lean.version_command` to the same with `--version` appended, and `lean.cwd` to the Mathlib project directory:

```json
{
  "lean": {
    "command": ["C:/tools/lake.exe", "env", "lean"],
    "version_command": ["C:/tools/lake.exe", "env", "lean", "--version"],
    "cwd": "C:/lean/mathlib4"
  }
}
```

The broker compiles the instance's own modules and does not build Mathlib, so the project's compiled library has to be there already. A file that imported all of Mathlib took about seven minutes to load on the development machine when Mathlib's files were not in the operating system's cache, which is one reason why compiles go through the broker.

All sessions request a one-million-token context from their CLI; the CLI and the account decide what the session actually gets. A setting that the runtime does not know, such as a misspelled name, is refused, and the refusal names it. The one exception is `lean.judge`, a key that an earlier version of do-math used: a settings file that still has it is accepted, and the key has no effect. `init` writes the complete configuration into the instance's own `settings.json`, and that file is the configuration in force afterwards: a running runner rereads it when it changes, and a session already launched keeps the settings it was launched with.

The Lean broker has settings of its own under `lean`, such as the memory it may reserve for compiles at one time; the [broker guide](../../.claude/skills/do-math/reference/lean-broker.md) lists them. Two cases need your attention. When several instances run on one machine, each broker derives its memory budget from the whole machine, so set `lean.memory_budget_mb` in each instance to that instance's share. And on Windows, compiles can wait although physical memory is free, because Windows charges a Lean process for the whole size of the library files it maps and counts that against the commit limit, which is physical memory plus the page file. Enlarging the page file raises the limit; that is a setting of your machine and yours to decide.

### Creating the instance and confirming the root

`init` creates the instance at a new path. The path should lie outside this repository, or under its `.skill-workspace/` directory, which Git ignores, so that the instance's own Git repository is not nested inside a tracked tree.

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/odd-sum'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --canon C:/research-input/canon --root-declaration OddSum.sum_eq_square --settings C:/research-input/settings.json
```

`--root` is the root file, `--canon` the folder with the Lean library, and `--root-declaration` the full Lean name of the root; all three are required. `--settings` is optional, and without it every default applies.

`init` copies the files into the instance, compiles the library, extracts the structural index and makes the first Git commit. Nothing in do-math compiles the folder before this, so `init` is where you learn whether it compiles; with files that import Mathlib it takes minutes.

`init` refuses, among other things:

- a library that does not compile, or a value check that fails;
- a declaration without a record, or a record without a declaration;
- a record without a weight or a description;
- an `axiom`, or a definition that contains `sorry`;
- a root that is not a theorem, or that already has a proof;
- a settings file that is not valid, or a tool server whose command is not found.

A refusal names the cause. If `init` refuses after it has created the directory, the partial directory is not an instance; correct the files and run `init` again on a new path.

When `init` has succeeded, the instance exists and nothing is running. Before you start the runner, read what was fixed:

- the root statement in words, in `root.md`;
- the source text of the root declaration and of every definition it uses, in `canon/lean/`;
- the root statement as Lean prints it after elaboration, which is the `statement` of the root's entry in `canon/index.json` and shows the types Lean inferred and the coercions it inserted;
- the values on which the definitions were checked, with the understanding that nothing beyond those values was checked.

Nothing after this reading judges what the Lean statement of the root means. The instance is complete when that statement, or its negation, is settled through a formal proof, and no later step compares the statement with what you meant. If you want a change, change the folder and create a new instance on a new path. If you find, after the research has started, that the Lean statement does not say what you meant, then what you want proved is a different statement, and it needs a new instance; the results of the old instance remain true of the statements they were proved for.

### Standing inputs

Standing inputs, such as limits on the methods the research may use, are plain text files in English, submitted with `python "$skill/runtime/runner.py" input $instance --file <file>`. Submit them now, after `init` and before `start`, when they should reach every session. An input applies only to sessions launched after it, and inputs accumulate: a session receives every input submitted before its launch, in order, and is told that a later condition overrides an earlier one on the same matter. To change or lift an earlier condition, submit a new input that says which condition it changes and how. A standing input cannot change the root; that requires a new instance.

Every session launched afterwards reads an input in full, and reviews decide what to accept by it, so the sessions treat everything in the file as your instruction, including any explanation or example written around the condition itself. When the operator delivers a condition for you, it quotes your words in English translation and marks the quotation as yours, and it marks any explanation it adds as the operator's. It adds no reason that you did not give. It rarely adds an example, and when it does, it marks the example as the operator's too.

### Starting the runner

```powershell
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

`start` launches the runner as a detached process, waits until the runner has confirmed that it is up, and returns its process ID and the paths of its log files under the instance's `runner/` directory. The runner then continues after the terminal or the operator conversation ends, and `canon/` and `knowledge/` are updated with every publication.

## Commands

All runner commands have the form `python <skill>/runtime/runner.py <command> <instance> ...`.

| Command | Purpose |
|---|---|
| `start` | Launch the detached runner when none is alive, including after a crash or reboot; existing sessions and an unfinished publication are recovered. It does not replace a runner that is alive. |
| `run` | Run the runner in the foreground for observation. |
| `status` | Show the root's state, whether the runner is alive and whether it has finished, the sessions and the pending work, the board, the blocks on providers and models, the root check and the Lean broker. It changes nothing. |
| `stop` / `resume` | Stop or resume the launching of new sessions and of further turns of running sessions; a turn is one run of a session's CLI process. `stop` does not end the run: the runner stays alive, the turns that are running finish, and publication goes on. The stop is recorded in the instance, so if the runner process has ended in the meantime, run `resume` to clear it and then `start`. |
| `reconsider-attempts` | Ask for one attempt to look again for available work. After an attempt has reported that every statement that remains is occupied, the runner launches no further attempts until an occupation ends, a statement newly appears among the work that remains, or this command is given; `status` shows that wait under `attempt_dispatch`. |
| `input --file <file>` | Supply a standing input to the sessions launched from now on. |
| `review --element <name>` | Request a comprehensive review of published elements. `--element` takes the declaration's name and may be repeated; `--concern <id>` and `--reason <text>` can identify the issue. |
| `organize` | Request an organizer for the published changes that no organizer has examined yet. |
| `questions --file <file>` | Place questions of your own on the frontier from a JSON file, without a peer or a review; the operating guide gives the format and the standard such a question should meet. A question cannot be withdrawn afterwards. |
| `kill-session <id>` | End the identified session's CLI process and its session host; session IDs are in the `status` output. The session ends as an interruption, so work it retained still goes to a peer. |
| `render` | Rebuild the derived views when no runner process is alive. |
| `restart-broker` | Replace the Lean broker after a change of the Lean environment. Stop launching first and let the running turns, publications and compiles finish. |

A request made with `review`, `organize`, `reconsider-attempts` or `questions` is read by the runner on its next pass, so one made while no runner is alive waits until `start`. The runner's commands refuse an instance created by an earlier version of do-math, which did not keep its knowledge as a Lean library.

## Reading the results

Start with `knowledge/frontier.md` and `knowledge/index.md`, which the README describes. For one element, the commands with which the sessions read the canon work on the instance folder as well, from the moment `init` has finished:

```powershell
python "$skill/runtime/canon_tool.py" frontier $instance
python "$skill/runtime/canon_tool.py" view $instance OddSum.sum_eq_square --full
python "$skill/runtime/canon_tool.py" list $instance --about OddSum.oddSum
python "$skill/runtime/canon_tool.py" question $instance q0
python "$skill/runtime/canon_tool.py" log $instance --last 10
```

`frontier` prints the frontier as it is now. `view` prints one element: its Lean statement, what its proof rests on with the standing of each statement, whether it is settled and formal, what uses it, the review's judgment with its reason, any concerns, and the approaches tried; `--full` adds the parts of the record. `list` prints one line for each element it selects: the elements of a module, what an element uses or is used by, everything the canon states about a definition, or, with `--remaining`, the work that remains. `question` prints a question with its understanding so far, and `log` the recent changes with the review's assessment of what each contributed.

## The dependency map, the paper and the root check

Two further commands work from the canon: one draws the dependency map and the other writes the paper. The root check, which the last subsection describes, is no command; the runner makes it by itself once the root is formally settled.

### The dependency map

`python <skill>/runtime/depmap.py <instance> --out <folder>` draws the dependency map of the research from the canon as it stands. It can be run at any time, including while the instance is running, and it writes nothing into the instance. The map shows the units that the proof of the root rests on, grouped by the folder of their module, and folds the steps into the lines that pass through them; `--all` shows every unit of the canon. The folder receives the drawing as `dependency_map.svg`, the same drawing for a browser as `dependency_map.html`, and the data it was made from as `dependency_map.json`.

### The paper

`python <skill>/runtime/paper.py <instance> --out <new folder>` writes the paper that presents the result, as LaTeX and a typeset PDF. It runs only when the root is formally proved or formally refuted, and it then runs to the end without asking anything.

The command takes from the canon what the formal proof of the root rests on. Sessions plan and write the paper after reading published mathematical papers as models, and further sessions read the manuscript by itself, read it beside published papers, and compare every numbered statement with the statement of its element, with a bounded number of repairs after each. The paper is written in ordinary mathematical language and does not mention Lean. The published papers used as models are not in this repository, since most of them may not be redistributed; the command downloads them from arXiv on first use.

How the canon becomes a paper is fixed in the skill's [paper method](../../.claude/skills/do-math/reference/paper-method.md). That document records choices that are yours to make. Read and confirm it before your first paper is produced; the command does not check that you have.

The exit code is:

- 0 when the paper is complete;
- 1 when the command refused or failed;
- 2 when the manuscript was produced and findings stayed open after the repairs; the log in the output folder lists them;
- 3 when the manuscript is complete and no TeX program was found.

A command line that `paper.py` cannot parse also exits with 2, with a usage message in place of a result.

### The root check

A statement is formal on two facts that both come from Lean: the library compiles, and the axioms that Lean reports for the proof are all allowed. The README explains this under "Formal proofs and the root check". When the root is formally settled, one thing remains to be known, namely that the root's statement, with every definition it is built on, is still what the instance's first commit fixed. No publication can change either, because the runner refuses a publication that changes a statement or the text of a definition in place. The canon and its index are files, however, and something other than a publication can change them. The runner therefore compares the present state with the first commit itself, in the root check, and there is no command for you to run.

The root check compares the structural index in the instance's first commit with `canon/index.json` as it stands. It starts at the root and goes to every element that the root's statement names, and from a definition on to what the body of the definition names. Each element it reaches must have the same kind and the same statement in both indexes, and a definition must have the same source text as well. The check compiles nothing. The runner makes it as soon as it finds the root formally settled, and repeats it whenever another proof comes to settle the root or a publication changes the library.

`status` gives the result under `root_check`, which is `null` until the root is formally settled and a runner has made the comparison. The entry names the proof that settles the root and the commit that the present index was compared with, and its `status` is `unchanged` or `changed`. With `changed`, the entry's `differences` hold one sentence for each element that differs or that is under the statement in only one of the two indexes. The runner has then written a request for a comprehensive review of the proof that settles the root, and it takes that request up itself. A result of `changed` means that something other than a publication changed the canon or its index, such as an edit by hand of a file under `canon/`. Read the differences together with the settlement, because they say that what was proved may not be what was posed.

The root check has two limits. It compares elements, so it does not see a declaration that is not an element, such as a private helper that a definition uses. And it does not see a definition whose text is unchanged and which Lean now reads as a different term.

## Ending a run

To end a run before the root is formally settled, take these steps in order. First, run `stop`, so that no new session and no further turn is launched. Then run `kill-session` for each session that `status` shows as running; this also ends the session's host process. On Windows, if the session's processes were contained when it was launched, which the session's `process-job.json` records, it ends the processes the session started as well, except any that a system service started on its behalf. When no session is running, end the runner process with `Stop-Process` on Windows or `kill` on Linux; its ID is the `pid` under `process` in the instance's `runner/process.json`. The Lean broker is a separate process whose ID is in `runner/lean/process.json`. It exits by itself only after a run has finished with a formally settled root, so after an early end it stays alive until you end it in the same way.

End each of these processes by its ID and never by its name. The runner, the session hosts and the broker all run as Python processes, and a command that selects processes by name ends all of them together.

Ending a run in this way pauses the instance. Nothing in it is deleted, and `resume` followed by `start` continues it from the work that was pending. Do not delete lock files or edit the runner's state to force a restart.

## Interruptions and completion

A producing session interrupted by a provider's usage limit or another failure leaves its retained work for a peer, if it left any; a session that left none is launched again. When a provider refuses a launch because of a usage limit, launches through that provider are blocked until the limit resets, or for a growing delay when the reset time is not known; a refusal specific to one model blocks only that model, and the next model in the role's list serves later launches. Interrupted peers, reviews and organizers are replaced by new sessions that receive the partial work. A candidate that no longer applies to the canon, or no longer compiles on it, because of what was published while it waited, is not published; a new peer makes a new candidate from the same work, and that candidate receives a new review.

After a crash of the runner or a reboot of the machine, run `start` on the same instance. The runner finds the processes that are still alive, collects the work of those that have ended, and completes a publication that was underway without publishing anything twice. On Windows, use a shell at the same privilege level as the one that started the run, because the runner has to be able to query its processes.

When the root is formally settled, the runner stops launching new attempts and explorers. Existing sessions finish; their peers and reviews, and any formalizers, comprehensive reviews and organizers, still launch as their inputs become ready; the runner makes the root check; and it finishes when that work has ended. A root that is formally settled and a runner that has finished are therefore different states, and `status` reports both. If a later review withdraws the confirmation of a proof that the settlement rests on before the runner has finished, the research resumes.

The [operating guide](../../.claude/skills/do-math/reference/operations.md) explains the states, the failures and the recovery in full; the [Lean guide](../../.claude/skills/do-math/reference/lean.md) explains how sessions use the broker, and the [broker guide](../../.claude/skills/do-math/reference/lean-broker.md) its scheduling and settings.
