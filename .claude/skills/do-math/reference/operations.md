# Operating a research instance

This guide continues the operator's entry point, [SKILL.md](../SKILL.md). Use it when preparing an instance or acting on an existing run.

The runner manages the research sessions after launch. Your commands affect that running process or supply inputs it will use. Understanding the difference matters when operating a run: stopping new dispatch leaves existing sessions alive, and delivering a user input makes it available to future launches without changing the instructions of sessions already underway.

## Fix the root in words and in Lean

An instance is created from two statements of the same proposition. The root file states it in words. The Lean statement of the root, together with the Lean definitions of the objects it speaks of, states it in the form in which the research will work.

The Lean statement carries more weight than a translation would. Every session receives what it takes on as Lean statements over these definitions, and every element the research adds is built on them. The instance is complete when the fixed Lean statement, or its negation, is settled by a formal proof. No later step judges whether the theorem that was proved corresponds to what the user meant, because the theorem to be proved is the fixed statement itself. The correspondence between the Lean statement and the user's proposition is therefore established here, by you and the user, before the research starts. Lean checks that the definitions and the statement are well formed. It cannot check that they say what the user means, and a statement that compiles can say something else.

The work has five parts, described in the subsections below: the root file, the Lean files, a record for each declaration, a check of the definitions against known values, and the user's own reading of the result. You do them together with the user. Ask the user whenever a choice changes what the proposition asserts, such as where an index starts, which boundary cases are included, or which of two definitions of an object is meant.

### The root file

The root file contains the mathematical proposition in words, with its objects, assumptions, domains and quantifiers defined. When the user's material gives values for small cases, such as the first rows of a table, include them; they are what the Lean definitions will be checked against. A proof of either that proposition or its negation settles the root.

Everything inside an instance is written in English: the root file, the Lean files and their records, the inputs, any questions you publish, and everything the sessions write. Write the root statement in English, whatever language the user speaks to you in.

### The canon folder

Prepare a folder, outside the new instance directory, that holds the beginning of the instance's Lean library. `init` copies it into the instance as the first state of the canon.

```text
<canon folder>/
  lean/<Library>/Defs.lean     the definitions of the objects the proposition speaks of
  lean/<Library>/Root.lean     the root statement, importing the definitions
  records/<name path>.md       one record for each declaration, at the path that follows its name
  bibliography.bib             optional: the sources of definitions or statements taken from the literature
```

`<Library>` is the one top-level module name under which every module of this instance will live, the sessions' later modules included. Choose a name for the mathematics, for example `Parking`. `init` refuses a folder whose modules do not share one top-level name. The name must differ from `Init`, `Lean`, `Std`, `Lake` and from the first component of any library the files import, such as `Mathlib`, because the Lean broker refuses a module that would shadow one of those. The broker also accepts only module paths whose components, the library name and every folder and file name under it, consist of ASCII letters, digits and `_` and do not begin with a digit. The file names `Defs.lean` and `Root.lean` are examples.

Put the definitions in one module and the root statement in a module of its own that imports it. The reason lies in how a proof of the root will later enter. A proof replaces the body of the root's declaration where it stands, and the runner adds to the header of the root's module the imports that the proof needs. Those imports are modules that sessions add during the research, and those modules import the definitions. If the definitions lived in the root's module, the later modules would import the root's module, the root's module would have to import them, and Lean does not allow modules to import one another in a cycle. The proof would then have to enter as a separate declaration beside the root. So the root's module holds the root statement and nothing that later work will use. When the objects are many, `init` accepts several definition modules under the same library name.

Every later module imports the definitions, so every compile of the instance loads whatever your definition modules import. Work out which library modules your definitions and their checks use, and import those and no others. [Lean](lean.md) explains, under Writing Lean that compiles cheaply, how an import is inherited by every module that reaches it and what `import Mathlib` or `import Mathlib.Tactic` costs in a module that everything imports.

### Lean conventions of the canon

The files you write follow the conventions of every file of the canon, the same ones the sessions follow when they add modules. [The canon](canon.md) describes them for the sessions. What you need is this.

**Each file is written in Lean's module system.** It begins with the word `module`, imports with `public import <module>`, and puts its declarations under `@[expose] public section`. Sessions write their modules in the same way and import yours. In a `module` file the statement of a theorem is part of the public compiled output and its proof is not, which is what later lets a proof be replaced without recompiling every module that uses the statement. `init` does not check these three things. A file that omits them can still compile by itself, and the fault appears later, when a session's module tries to import it, or imports it and cannot see a declaration or unfold a definition.

**A statement is a `theorem`.** The root is written as a theorem whose proof is left open with `by sorry`:

```lean
theorem <name> <binders> : <the proposition> := by
  sorry
```

The root has no proof at creation; supplying one is the research. Its standing is then "no proof", and the frontier of the new instance is the root alone. `init` refuses a root declaration that is not a theorem, and one that already has a proof, whether in Lean or as a `## Proof` in its record. A theorem you supply with the canon to check a definition is different: its Lean proof is complete, Lean checks it at `init`, and it stands as accepted from the start without a review.

**No `axiom`, and no `sorry` inside a definition.** `init` refuses both. An axiom would add an assumption to everything built on it, and a definition left open has no meaning for a statement to speak about. An object whose definition you cannot yet write completely is a question to settle with the user before the instance is created.

**Every declaration you write is an element and needs a record.** That covers definitions, structures and inductive types, theorems, and instances. A declaration marked `private`, and the auxiliary declarations Lean generates, such as the fields and constructor of a structure, are not elements and need no record. When a record is missing, `init` names the declaration and the path it expects. The names it reports may include one that Lean chose itself, as it does for an instance written without a name or for a notation; write the record under the reported name.

The following pair of files shows the shape. It is an example for a small proposition, and nothing in it but the header lines and the form of the root is prescribed.

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

The first file is `lean/OddSum/Defs.lean` and the second `lean/OddSum/Root.lean`. The root declaration is `OddSum.sum_eq_square`, and that full name is what `--root-declaration` takes. A file that needs the imported library adds its `public import` lines after `module`.

### A record for each declaration

Sessions read the records you write whenever they meet the root or its objects, and views that pass over many elements show the self-description as the only prose of each.

The record of the declaration `A.B.c` is the file `records/A/B/c.md`. A name component that Windows cannot use as a file name is encoded, for example `Aux` as `Aux%`; when in doubt, the path `init` reports for a missing record is the right one. `init` also refuses a record that belongs to no declaration.

A record begins with a header between two lines of `---`, followed by sections with exactly these top-level headings, each at most once and in any order. Deeper headings are free.

| Part | Content |
|---|---|
| `weight` (header, required) | `unit` or `step`. A unit is something a reader of the proof's structure would name; a step is a piece inside one proof. The dependency map draws units and folds steps, and the paper numbers units and absorbs steps. The root is a unit. An object the proposition is about is usually a unit, and an auxiliary definition usually a step. |
| `short` (header) | A short name. The frontier shows it for the element in place of the description. |
| `source` (header) | The key of an entry in `bibliography.bib`, for a definition or statement taken from the literature. |
| `## Description` (required) | The self-description: what this element is, in a line or two. |
| `## Statement` | The statement, or the definition, in natural language. For the root this is the proposition of the root file. |
| `## Explanation` | What the statement says about the object, why the definition was chosen, and how the Lean form corresponds to the mathematical one: indices that start from zero, a normalization, a coercion, a convention at a boundary. |
| `## Literature` | For something taken from the literature: the source, how much of it was read, and where the statement stands in what was read. |

The header keys `proves` and `refutes` and the section `## Proof` exist for elements the research adds later, and `init` reads them if they are present. Leave `proves` and `refutes` out, and write no `## Proof` in the root's record: the root has no proof at creation, and a nonempty `## Proof` would make the canon show the root as having one.

The record of the definition in the example above could read as follows. It is an example of the form.

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

The recursion adds the odd number $2n + 1$ at the step from $n$ to $n + 1$, so the argument of the Lean function counts how many odd numbers have been added. The values 9 and 16 that the root file gives for $n = 3$ and $n = 4$ are checked by compilation in the module of the definition.
```

Write the explanation with care. It is where a later session learns how to read the Lean form, and where the paper later finds the conventions that separate the Lean statement from the statement in words.

### Evaluate the definitions on known values

A definition that compiles can still denote a different object from the one intended. Lean's functions are total, so conventions fill in what the mathematics leaves undefined, and a small slip changes the object without causing an error. Subtraction of natural numbers stops at zero, division by zero returns zero, `Finset.range n` runs from 0 to n - 1, and a recursion can start one index early or late. These are examples of the kind of difference to look for, and the definitions of a particular problem have their own.

The check against known values is the means you have. The user's material usually carries values for small cases. Evaluate the Lean definitions on those cases and have the compiler confirm the agreement, by writing each value into the Lean files as something the compiler must prove. `init` shows no output of a compile that succeeds, so a command that only prints a value, such as `#eval`, confirms nothing; the check has to be a declaration whose failure fails the compile. The example above uses `example : oddSum 3 = 9 := by decide`. Which proof closes such a check depends on how the definition is written.

A check can take two forms, and they leave different things behind. An `example` is compiled and then discarded: it is not an element, needs no record, and leaves nothing in the canon. A named theorem with a complete proof is an element: it needs a record, and a session that later traverses what the canon knows about the definition finds the checked value there. Put the checks in the module of the definitions or in a module of their own that imports it, and keep them out of the root's module.

Agreement on these values is evidence that the definitions denote the intended objects. It is not a proof of it, and the values checked say nothing about cases unlike them. Say this to the user as it is, with the list of the values that were checked.

### Compile, and have the user confirm

`init` is the compile. Nothing in do-math compiles a canon folder before an instance exists, so you create the instance, as "Create and start" below describes, and read what `init` reports. It compiles the library through a Lean broker that it starts and stops, extracts the structural index, and refuses the canon when a module does not compile, when a value check fails, or when one of the conditions above is not met. A refusal names the module with the end of Lean's output, or the declaration and the condition. Correct the files and run `init` again on a new path.

When `init` has succeeded, the instance exists and nothing is running. Before you start the runner, have the user read what was fixed:

- the root statement in words, from `root.md`;
- the source text of the root declaration and of every definition it uses, from `canon/lean/`;
- the root statement as Lean prints it after elaboration, which is the `statement` of the root's entry in `canon/index.json`. The printed form shows the types Lean inferred and the coercions it inserted, which the source text does not;
- the values on which the definitions were checked, and that nothing beyond those values was checked.

Explain to the user how the Lean statement reads, in the user's language, binder by binder and hypothesis by hypothesis, and point out each place where the Lean form differs from the usual mathematical notation. The user's confirmation is part of fixing the root, and it is the only judgment of meaning the Lean statement will receive from the person whose proposition it is. Do not start the runner before the user has confirmed.

If the user asks for a change, change the canon folder and create a new instance on a new path. An instance that was created and never started holds nothing but the copied files and can be deleted.

### If the Lean statement is later found not to say what was meant

The runner refuses to run an instance whose root file or whose root statement in Lean has changed. If the research or the user later finds that the Lean statement does not say what was meant, the proposition has changed, and a new instance is needed with the corrected statement. Tell the user what was found and what the existing instance has in fact been working on. Results of the old instance remain true of the statements they were proved for.

A definition that proves inconvenient is a different matter and needs nothing from you. A session introduces another representation as a new definition and establishes, as an element, that the two agree.

## Prepare the settings and environment

Put standing instructions, such as limits on permitted methods, in a separate input file, written as "Convey the user's conditions" below describes. Submit it before starting the runner to make it part of every initial session's context. Later inputs affect only sessions launched after submission. They do not rewrite existing sessions' instructions or their saved contexts. Inputs accumulate rather than replace one another: a session receives every input submitted before its launch, in the order of submission, and is told that a later condition overrides an earlier one on the same matter. To change or lift an earlier condition, submit a new input that says which condition it changes and how.

The runner needs Python 3.12 or later, Git, authenticated Codex and/or Claude native executables, and a Lean environment. The default models for attempt, explore, formalizer and organizer are `codex/gpt-6.1-sol` at `xhigh`, followed by `claude/opus` at `xhigh`; for peer and review the order is reversed, so that the candidate and its review come from a different model than the producers. These are ordered alternatives for each role. Defaults are eight concurrent AI sessions, attempt and exploration launches at least three minutes apart from one another, exploration requested at every attempt launch, and organization after four published changes.

An example settings file is:

```json
{
  "schema": 1,
  "max_sessions": 8,
  "explore_every": 1,
  "organizer_every_records": 4,
  "launch_interval": 180,
  "max_end_resumptions": 3,
  "acceptance": {
    "decline_reducible_proofs": true,
    "decline_uncomprehended_computation": true
  },
  "models": [
    {"model": "codex/gpt-6.1-sol", "effort": "xhigh"},
    {"model": "claude/opus", "effort": "xhigh"}
  ],
  "roles": {
    "peer": [{"model": "claude/opus", "effort": "xhigh"}, {"model": "codex/gpt-6.1-sol", "effort": "xhigh"}],
    "review": [{"model": "claude/opus", "effort": "xhigh"}, {"model": "codex/gpt-6.1-sol", "effort": "xhigh"}]
  },
  "cli": {"codex": "C:/tools/codex.exe", "claude": "C:/tools/claude.exe"},
  "mcp_servers": {
    "scholarly": {
      "command": "C:/math/services/scholarly-mcp/.venv/Scripts/python.exe",
      "args": ["C:/math/services/scholarly-mcp/server.py", "--public-only"]
    }
  },
  "retry_seconds": 60,
  "retry_max_seconds": 1800,
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"],
    "cwd": null,
    "env": {},
    "cache_epoch": "initial",
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "judge": "auto"
  }
}
```

Replace the executable paths with the actual installations. A role-specific ordered model list under `roles` replaces the common list for that role; the example shows the default lists for peer and review. A `roles` object that omits a role sends that role to the common list. An omitted setting receives its default. An unrecognized key, such as a misspelling or a setting carried over from the earlier do-math runtime, is rejected by name rather than ignored, because ignoring it would leave the default in force without notice. The runner checks structure; actual login and model availability are confirmed by execution. `init` writes the complete configuration, with defaults filled in, to the instance's own `settings.json`, and that file is the configuration in force afterwards. A running runner rereads it when it changes and uses the new values for its later scheduling and launches; a session already launched keeps the settings saved at its launch. An edit the runner rejects leaves its last valid settings in force and appears as `settings_error` in the runner state that `status` returns.

`lean.judge` decides whether formal proofs are judged from outside the structural index, as "The judge of formal proofs" below describes. With `"auto"`, the default, the runner uses `leanexport` and `lake` where they stand beside the Lean command, which is where Lean 4.35 and later have them. With an earlier Lean there is no judge, and `status` says so. `{"export": [...], "compare": [...]}` names the two commands yourself, and `null` switches the judge off. A judge that is configured and cannot run makes `init` refuse. With `"auto"`, `init` and `start` also refuse when one of the programs that `lake comparator` looks up is not found on the machine; "The judge of formal proofs" names those programs and says where they are looked for.

The `lean` block has to be right before `init`, because `init` compiles the canon folder with it. To use Mathlib, configure `lean.command` as `["<lake executable>", "env", "lean"]`, its version command with `"--version"` appended, and `cwd` as the Mathlib project. Supply any necessary PATH value through `lean.env`; JSON does not expand shell variables. The broker handles compilation and dependency builds. [Lean](lean.md) explains resource settings and estimates.

### When compiles wait for memory on Windows

All Lean compilation of an instance goes through its broker, and in this design compiles carry more of the work than before: sessions compile what they state, a peer's candidate is built before it is frozen, review builds it again, and every publication that changes a Lean file is a build of the library. How many compiles can run at once therefore bears on how fast the research moves.

On Windows, what limits that number is the commit limit, and the user can raise it. Windows keeps an account, the commit charge, of the memory it has promised to processes. The limit of that account is physical memory plus the page file, and an allocation beyond it fails even while physical memory is free. Whatever its own memory and thread budgets allow, the broker starts a compile only if the machine's remaining commit, less what the compile is certain to take, would be at least `lean.min_free_memory_mb`. A Lean process is charged far more commit than the memory it uses. Lean maps the compiled library into memory, and Windows appears to charge the whole size mapped, although most of those pages are shared between processes or never touched. One process that imported the Lean metaprogramming library was measured at a commit charge of 2,078 MB while it touched 803 MB of physical memory, and a compile that imported the analysis part of Mathlib held between 2 and 3.9 GB for the import alone. On the machine these measurements were taken on, with 15.9 GB of memory, a commit limit of 25.2 GB and sixteen sessions running, about 3.4 GB of the limit was free. Compiles then ran one at a time while physical memory was free: of 481 compiles, the median ran for 24 seconds and waited in the queue for 179 seconds.

Enlarging the page file raises the commit limit and would let the broker admit several compiles at once. When you see this situation, recommend it to the user and give the reason. The sign is compiles listed under `lean.queued` in `status`, with `waiting_for` null, while no compile is running and physical memory is not exhausted; Windows shows the commit charge and its limit as "Committed" in the memory view of Task Manager. While one compile is running, a second can also be held back by the broker's own memory or thread budget, and the `reserve` of each queued compile in `status` together with `lean.config` shows which; [Lean](lean.md) explains those budgets. The page file is a setting of the user's machine, so the choice and the size are the user's, and you do not change it yourself. The effect on compiles that import Mathlib has not been measured.

### External tools

Only the external tools configured in the instance's `mcp_servers` enter worker sessions. `mcp_servers` maps server names to configuration objects. A local server uses `command`, `args`, and optional `env`; an HTTP server uses `url` and the provider's supported transport configuration. Further tools that the research needs are added there; personal instructions and hooks do not supply them. Authentication remains with the installed CLIs. Worker launches disable personal/project instruction discovery, skills, hooks and memories; all do-math guides and user conditions are supplied explicitly.

The default settings attach scholarly-mcp, the literature server, to every instance. The session guides tell sessions to look actively for earlier work and cite it, and this server is the tool those guides direct them to. The default is the server that the repository holding this skill keeps under `services/scholarly-mcp`, run by the Python of that folder's own environment and started with the `--public-only` option. On one installation it reads:

```json
"mcp_servers": {
  "scholarly": {
    "command": "C:/math/services/scholarly-mcp/.venv/Scripts/python.exe",
    "args": ["C:/math/services/scholarly-mcp/server.py", "--public-only"]
  }
}
```

The runner computes the two paths from the place where the skill is installed. `init` writes this entry into the instance's `settings.json` when it is given no settings file, or a settings file without an `mcp_servers` key. A settings file that has the key replaces the default with what it gives. To use a server installed elsewhere, or to attach further servers, write the `scholarly` entry there together with the others. `"mcp_servers": {}` creates an instance without external tools. `init` refuses, before it creates anything, when the `command` of a server is not found, because a CLI whose configured server does not start begins the turn without it and raises no error.

The reason for `--public-only` is this. Every session starts its own copy of the server. Without the option, each copy logs in separately to the institutional account that the server uses for subscription sources, so an instance of sixteen sessions could hold dozens of logins on that account at once. Whether the institution or a publisher would treat that as misuse is not known, and if they did, the consequence would fall on the account and not only on this research. With the option, the server creates no login and opens no browser. It serves about twenty sources that are reached through public interfaces, among them zbMATH, arXiv, Crossref, OpenAlex and Semantic Scholar, and it refuses requests for the others. Sessions therefore cannot search MathSciNet or retrieve full texts that require a subscription; their literature guide tells them to record such a paper as not read.

The check that `init` makes finds a missing command and nothing more. Before `start`, confirm that the server answers as configured. In the server's folder, run `<its python> -m unittest tests.test_mcp.MCPContract.test_public_only_serves_the_login_free_sources_and_refuses_the_rest`. The test starts the server over standard input and output, as a session does, lists its sources and checks that a subscription source is refused; it contacts no external service. If the instance is to run without the server, tell the user so and why.

Three facts about running many copies were measured or remain open. First, one copy answers about seven seconds after it starts, and sixteen started together took between twenty-three and forty-one seconds. The Claude CLI waits about thirty seconds for a configured server and then begins the turn without it, so the runner sets `MCP_TIMEOUT` to 180 seconds in every worker's environment. Second, all copies send their requests from one network address, so a public interface that limits requests per address answers with the code `rate_limited` more often than it would for one copy; the sessions are told that this answer does not mean the work is absent. Third, Codex was tried separately. Launched with the full-access option the runner gives it, Codex called a configured server's tool and received the result; launched with a read-only sandbox, it refused such calls. Codex does not wait for a configured server before it begins a turn. A server that needed twenty seconds to start was not yet available when the turn began, and became available later in the same turn. A slower start than that was not tried. When an instance runs sessions on Codex, read one session's stream after launch for `mcp_tool_call` items and their results, and tell the user if none succeeds.

### Context, continuation and acceptance settings

Every worker role requests a 1,000,000-token context window, including role-specific model choices and fallback launches. Codex receives explicit `model_context_window=1000000` and `model_auto_compact_token_limit=900000` overrides, so isolation from the operator's configuration does not discard the context setting. Claude receives the model's `[1m]` variant, `CLAUDE_CODE_AUTO_COMPACT_WINDOW=900000` and `CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000`, twice the CLI's default output cap for one response; an inherited setting that disables 1M context or overrides the compaction percentage is removed from the worker environment. Existing `[1m]` suffixes are retained once, and `[200k]` is replaced. These are launch requests: the selected model, account and CLI determine actual capacity and access. The Claude selector follows its [model configuration interface](https://code.claude.com/docs/en/model-config#extended-context).

A Claude worker also receives `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=7200000`, two hours. Worker sessions run the CLI in print mode. In that mode the CLI can stop background tasks, such as sub-agents, that are still running after the main agent's turn has ended; the message it writes then names this variable as the limit, with a default of ten minutes. In the sessions of two instances the CLI did this when sub-agents were the only background work the main agent had left: 32 of its 35 stops happened in that state, while a main agent that had left a shell command of its own running was not stopped, twelve times for up to 45 minutes. The stops ended reviews: a reviewer finished its own checks and ended its turn to wait for its three sub-reviewers, the CLI stopped them ten minutes later, and the session ended without an assessment; 16 of 22 failed reviews carry the message. A sub-agent that finishes while the CLI is still running starts the main agent's next turn, which was seen 120 times, 27 of them with nothing else pending. Two hours is meant to give sub-agents that time. That the CLI honours a value other than 0 has not been observed; if it does, its message will name 120 minutes where it named ten. With this value a background task that never ends can hold its session for up to two hours after the main agent's last turn. `status` shows such a session as running, and `kill-session` ends it sooner.

`max_end_resumptions` is the maximum number of additional turns in which an attempt or explorer that undertook research, a formalizer or a peer receives continuation guidance. It is a nonnegative integer, default 3, fixed for that session at launch. The initial turn is not counted. At the limit, the host issues the same end authorization that permits the handoff to peer or review, with `source: runner` and `basis: resumption_limit`; it does not wait for operator approval or resume indefinitely. A value of 0 authorizes the initial ending without a reconsideration turn. A valid `no_research` outcome or an interruption ends the session without a reconsideration turn; the recorded end authorization then has `source: runner` with `basis: no_research` or `basis: interrupted`, and an interrupted session keeps its usual processing. A Claude turn that ends because one response exceeded the CLI's output-token cap is not an interruption: the CLI discards only that response, so the host resumes the same conversation, reporting the CLI message as the previous turn's problem. Such a resumption counts toward this maximum; when the maximum is already reached, the host issues `resumption_limit` with that message.

`acceptance` holds two settings that govern what review does with a proof it has found correct. With `decline_reducible_proofs` true, review does not yet accept a proof that it judges can still clearly be made simpler. With `decline_uncomprehended_computation` true, review does not yet accept a proof that closes part of the statement by large computation carried out without an understanding of why that part holds. Both are true by default, so they apply in every instance; set one to false only when the user asks for that in this research. A correct proof that review does not accept under either setting is still published, with the standing "correct, held back" and review's reason. Other proofs can use the element, the element stays among the work that remains, and nothing is settled through it, so research on it continues from the published proof. The workers' review guide describes the judgment each setting asks of review. When a setting changes, the runner does not revisit judgments that are already published.

## Create and start

Choose a path that does not exist, outside the development repository or in an ignored directory such as `.skill-workspace/`. The instance has its own Git repository; confirm that it will remain separate from the parent. Keep preparation files outside that path.

```powershell
$skill = 'C:/math/.claude/skills/do-math' # replace with the installed skill folder
$instance = 'C:/research/my-problem'     # a new path
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --canon C:/research-input/canon --root-declaration OddSum.sum_eq_square --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" input $instance --file C:/research-input/conditions.md
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

`--root` is the root file, `--canon` the canon folder, and `--root-declaration` the full Lean name of the root statement; all three are required. `--settings` is optional, and without it the defaults apply. The `input` command is optional when there are no additional standing conditions.

`init` copies the root file and the canon folder into the instance, compiles the library, extracts the structural index, and creates the configuration, the derived views, the session directories and the initial Git commit. It returns when the compile has finished. With files that import Mathlib this takes minutes, because the broker first measures what the imports cost and then compiles each module, so run it where the shell will wait for it. It refuses, with the reason on standard error, in this order. Before it creates anything: an empty root file, a canon folder without `lean/` or whose Lean files do not share exactly one top-level module name, a settings file that is not valid, an `mcp_servers` entry whose `command` is not found, and a path that already exists. After it has created the directory: a record that is malformed, for instance one with an unknown header key, without a valid `weight`, without a nonempty `## Description`, or with text before its first section; a library that does not compile; a declaration without a record or a record without a declaration; an `axiom`; a definition that contains `sorry`; a claim in a record's `proves` or `refutes` that Lean does not confirm; names that differ only in the case of their letters; and a root declaration that is not a theorem of the library or that already has a proof. A refusal of the second group leaves a partial directory, which has no `instance.json` and is not an instance. Fix the cause and use a new path.

Between `init` and `start`, have the user confirm what was fixed, as "Compile, and have the user confirm" above describes. `start` launches a detached runner and returns its PID and new stdout/stderr paths after confirming this launch's readiness token. Read those logs and `status` to confirm the actual launch; the runner's own start record is in the returned stdout log.

The caller can then end its conversation. The runner and session hosts continue independently. If readiness is not confirmed within ten seconds, inspect the named logs and liveness before retrying; a wait timeout alone does not show that the child died.

## Convey the user's conditions

A standing input is the way a decision of the user's reaches the sessions. Every session launched after it reads it in full, and reviewers decide what to accept by it. The sessions therefore follow whatever you write around the user's words as though the user had said it. In an earlier run this went wrong three times, and each time the user had to give a further condition to undo it.

The first time, the operator delivered a condition under which a correct proof is not yet accepted while it can clearly be made simpler. The user had given no reason. The operator supplied one: the cost of formalization, illustrated by the number of published assertions the proof depended on. Reviewers then judged whether a proof could be simplified by the length of its list of dependencies, and one asked that a citation be deleted so that the list would become shorter. The user's reason, given afterwards, was that a simpler proof is more concise, and nothing more.

The second time, the operator added an example of its own to that condition: a proof that relies on a wide range of computed results while using only a narrow part of them. The user had not meant that. Reviewers began counting how many entries of a table a proof read.

The third time, the user said that a proof which establishes part of a statement by computation should not yet be accepted, and meant crude large computation done without understanding. The operator wrote the condition as covering every proof that establishes any part of a statement by computation. That version stood for nine minutes before it was replaced, and the sessions launched in those minutes had received it.

What follows describes how to write an input so that the sessions receive what the user decided.

**Give the user's words, in translation, as the user's.** The instance is in English, and the user may speak to you in another language. Translate what the user said into English and set it apart as a quotation, labelled as the user's words in translation. That quotation is the condition. Translate what was said, and do not make the translation smoother or more complete than what the user said. Where a phrase could be translated in ways that would change what the condition requires, ask the user which is meant. Keep the original wording outside the instance, with your other preparation files, and put neither the original nor its path into the input. If a translation turns out to be wrong, submit a new input that says which earlier input it corrects.

**Mark your own text as yours.** Around the quotation you will usually need to write more: what happened in the research that led to the condition, which the sessions need in order to understand the case; what the condition changes in terms a session acts on, such as which field of an assessment takes which value; and what has already been changed in the instance on the user's instruction. Where a sentence is your reading of the user's words, and not something the user decided, say so at that sentence or passage. The sessions are told that the user's words are the condition and that your text explains it.

**Give no reason the user did not give.** If the user gave a reason, translate it with the rest. If the user gave none, say that none was given. If you supply a reason of your own, reviewers will apply the condition according to that reason, as in the first case above. When a session will need the reason in order to apply the condition, ask the user for it.

**Do not widen the condition, and add examples of your own rarely.** Write the condition so that it covers what the user said and no more. Sessions use an example to decide which cases a condition applies to, so an example the user did not give makes them apply the condition to every case that resembles the example, as in the second case. If you add an example, mark it as yours. Where it matters which cases a condition covers and the user has not said, leave that judgment to the sessions and say that you are leaving it to them.

**Say how the condition relates to the earlier ones.** Inputs accumulate, and a session reads all of them in order. Say which earlier condition concerns the same matter as this one, what this one changes in it and what it leaves unchanged. When you withdraw something you wrote in an earlier input, name the passages you withdraw; the user's quoted words in that input stand unless the user has changed them.

**Say what you read.** When an input reports facts about elements, their records or their reviews, say which texts you read and which you did not, so that a session does not take your account for a checked one. Ask the sessions to confirm at the source anything you point them to.

**Ask when the research shows a case the user has not addressed.** Sessions will meet cases that nobody had in mind when a condition was given. When the sessions' work shows such a case, for example a proposal withheld or refused under a reading of a condition that the user may not have intended, report the case to the user with the texts involved and ask. The user's answer becomes a new input, and it can settle that one case while leaving the rest of the condition as it was.

## Read progress and results

The results of an instance are the elements of its canon, and you read them where the sessions read them. Nothing is published per session: what a session found enters as elements with their records, and what it learned about the course of the work enters as the approaches tried on an element or as the understanding so far of a question.

Begin with `knowledge/frontier.md`. Its first lines give the revision, the root declaration and the root's state. The view below them is derived from the root downward along what each proof names. While the root is not settled it is shown with every proof it has. Beneath a proof stand the statements it names that are not settled, each again with every proof it has; a statement that is settled is not opened. A line gives the element's name, its short name or self-description, and its standing. For a proof that is not confirmed or that is correct and held back, the line carries the beginning of review's reason; it also shows how many approaches have been tried on the element and how many sessions hold a section on it. A step whose own proof is accepted is passed through to what it names, so the view stays at the level of the units of the proof. Once the root is settled the view is the root's line alone, which says whether the settlement is formal; nothing remains for an attempt then, and no attempt is launched, while formalization continues until the settlement is formal. At the start of an instance the view is the root alone, with no proof.

After the view, `frontier.md` lists the concerns that are not cleared and the questions the research is trying to understand: each with its statement, grounds, open or resolved state and source, followed by the proposals review did not admit. A question's source is either the change whose review admitted it or an operator publication under `knowledge/questions/`. You make an operator publication with the `questions` command under Commands. Its questions do not pass through peer or review, so their content is yours to answer for; on the frontier, explorers take them up and changes resolve them like any other question.

Write an operator question to the standard that review applies to a proposed one, because no review reads yours. Its statement says what is asked, about which objects and over which range of cases. It lets a later reviewer recognize an answer, a negative one included: "does this regularity come from that property" is closed by "no, it comes from this other one", while "what structure explains this" names nothing a reviewer could accept as the answer. Its grounds say what an answer would change in how the problem is worked. A question whose complete answer would be a proof of the root asks what `q0` already holds. And when a question asks for the counterpart, among the objects of the root, of something known about a related object such as a limit or a model, state the counterpart you hope for as a statement about the objects of the root. Otherwise explorers work on the related object, where results come more easily, and the question does not close. In an earlier run the operator placed five questions when the instance was created. Three days later four of them were still open, each after three to six explorations, and the fifth had been resolved: it asked whether a named regularity came from a named property, and the answer was that it did not. Questions also age, since the difficulty one was asked about can be passed by another route. You cannot withdraw a question. A change can resolve it by showing that its premise no longer holds, and you can place sharper questions beside it.

`knowledge/index.md` is the derived index: every element of the canon, grouped by module, with modules and elements in the order of their names, each with its weight, its standing and its self-description. A definition has no standing and is shown with its kind. Nobody writes this view, and it has no surveys. Use it to see everything the canon holds, including the elements the root does not rest on, which the frontier does not show.

For an element itself, read the canon:

| Path under the instance | Content |
|---|---|
| `canon/lean/` | The library: the Lean source of every declaration. |
| `canon/records/<name path>.md` | The record of an element: self-description, statement in natural language, explanation, the proof in words where there is one, literature. |
| `canon/approaches/<name path>/<id>.md` | The approaches tried on a statement whose proof is not accepted, one entry per approach, each ending with review's assessment of what the work contributed. |
| `canon/questions/<question>.md` | The understanding so far of a question. That of `q0` is the research's current account of the root problem as a whole. |
| `canon/history/` | What replacements left behind: the difference between a replaced text and the current one. |
| `canon/evidence/`, `canon/bibliography.bib` | Files that records refer to, and the sources of results taken from the literature. |
| `canon/index.json`, `canon/records.json` | The structural index extracted from the compiled library, and a summary of the record headers. The runner produces both at publication, and they are never edited. |
| `knowledge/changes/<id>/` | One published change: its manifest `change.json`, the elements it added and the proofs it replaced in `applied.json`, review's `assessment.json` with its feedback, the sessions involved in `provenance.json`, and review's own compile in `verify.json`. |
| `knowledge/reviews/<id>/`, `knowledge/organizations/<id>/`, `knowledge/questions/<id>/` | A comprehensive review's assessment, an organizer's output, and an operator publication of questions. |

The traversal commands that the sessions use are available to you as well, and they are the convenient way to read an element, because one view joins what Lean knows of it with what its record says. Each is `python <skill>/runtime/canon_tool.py <command> <instance> ...`: where a session gives its own folder, you give the instance folder. The reading commands work this way from the moment `init` has finished; `prepare`, `verify` and `checkout` belong to a session's work and refuse the instance folder. For example:

```powershell
python "$skill/runtime/canon_tool.py" frontier $instance
python "$skill/runtime/canon_tool.py" view $instance Parking.Columns.dq_col --full
python "$skill/runtime/canon_tool.py" list $instance --about Parking.zr
python "$skill/runtime/canon_tool.py" question $instance q0
python "$skill/runtime/canon_tool.py" log $instance --last 10
```

`frontier` prints the frontier as it is now. `view` prints one element: its Lean statement, what its proof rests on with the standing of each statement, whether it is settled and formal, what uses it, review's verdict with its reason, concerns, and the approaches tried; `--full` adds the parts of the record. `list` prints one line per element for a module, for what an element uses or is used by, for everything the canon says about a definition, or for the work that remains. `question` prints a question with its understanding so far, and `log` the recent changes with review's assessment of what each contributed. [The canon](canon.md) describes each view. `knowledge/state.json` holds the same derived state in structured form for detailed inspection.

Read a standing for what it says. "No proof" means the statement stands alone. "Proof not confirmed" means a proof was offered and review found a gap or could not complete its judgment; the reason says which. "Correct, held back" means review confirmed the proof and did not accept it, for one of the two reasons the acceptance settings name. "Accepted" means the proof is correct and accepted. A statement is **settled** when one of its proofs is accepted and every statement that proof names is settled, so an accepted proof that rests on an unsettled statement does not settle its own. The root's state combines these with whether the proof is formal:

| State | Meaning |
|---|---|
| `unresolved` | No proof of the root is settled, and no refutation of it is. |
| `informal_proved` | The root is settled, and no proof that settles it is formal yet: somewhere in what it rests on, a proof is still written in a record and not complete in Lean, or depends on an axiom that is not allowed. |
| `formal_proved` | The root is settled through a proof that is formal. |
| `informal_refuted`, `formal_refuted` | The same for an element whose statement Lean has confirmed to be the negation of the root's. |
| `contested` | Both the root and its negation carry settled proofs. |

The instance is complete when the root is `formal_proved` or `formal_refuted`. Whatever the root's state, the runner launches formalizers for settled statements that the root rests on, as "What creates new work" below explains, so formal proofs are already being written while the root is unresolved. It does the same for a settled refutation of the root and for what that refutation rests on, since a formal refutation completes the instance as a formal proof does.

A contested root is not treated as settled for completion; the opposing proofs must be resolved. Whenever no comprehensive review is pending or running, the runner assigns one that covers every concern that is not cleared and every contested statement's current set of opposing judgments it has not yet assigned. When that review leaves the concern uncleared or the statement contested, the runner does not assign it again; a further examination needs an operator `review` request.

Question `q0` is the root problem itself; no explanation resolves it, and it stays open until the root is formally proved or refuted. The frontier then shows it resolved by the root's formal settlement, with the declarations whose proofs carry it. `knowledge/state.json` records that ground under the question's `root_settlement` in place of `resolutions`. The runner derives whether `q0` is open or resolved from the root's state each time it replays the published events, so a later review that withdraws the confirmation of a proof the settlement rests on reopens `q0`, and the runner resumes research.

`knowledge/board.md` shows the work still underway. A **section** is what a session has taken responsibility for on an element: the whole of the statement, an exact part of what it asserts, or a statement the session formulated itself and registered with the element it is aimed at. An attempt, or a peer extending its work, registers one, and the runner records a formalizer's assigned element as a whole section. A session choosing a section on an element holds that element's **lease**, which lets one session at a time choose there. A producing session, the peer that takes its work over and the review that assesses the resulting candidate form one **pipeline**, and the sections and question its sessions hold stay occupied until publication or a review decision that there is nothing to publish. The workers' [common introduction](common.md) develops these terms. The board shows the sections producing work holds, the question each exploration occupies, its processing stages and the element leases; a session's declaration lists the sections it has registered or the question it holds.

The status command reads those declarations directly, including changes since the board file was last rendered, and reports under `questions` which questions are free, the sessions of the explorations holding each occupied one (`occupied` lists them, so both appear after an organizer merges two questions explorations held), how many explorers are still choosing, and whether exploration is requested.

`status` returns the root's current state, whether the runner has finished, active and pending jobs, the board, provider/model blocks and the Lean broker state. A successful status command means the query succeeded. A formal root and a finished runner are different states: after formal completion, new attempts and explorations stop, while existing sessions continue and the runner still prepares their peer and review stages, ready formalizations, comprehensive reviews and due organization batches. If a later review withdraws the confirmation of a proof the root's formal settlement rests on before exit, the same scheduler resumes research.

## The dependency map and the paper

Two further commands produce, from the canon, what was formerly made by hand after a research had ended.

### The dependency map

`python <skill>/runtime/depmap.py <instance> --out <folder>` draws the dependency map of the research from the canon as it stands. It can be run at any time, including while the instance runs, and it writes nothing into the instance. The command needs only Python.

The map shows the elements whose record gives `weight: unit` and that the proof of the root rests on, grouped by the folder of their module; `--all` shows every unit of the canon. The steps are folded into the lines that pass through them. A solid line means that the proof of one unit, or the body of a definition, names another. A dashed line means that it reaches the other only through folded steps, which are named on the line. A dotted line joins a statement to a definition it mentions, and a definition to a definition that its type mentions; a heavy line joins another proof of a statement to that statement. When the research has ended with the root refuted, the result is the refutation, and the map shows it: the root's card says that the root is refuted, a heavy dashed line joins the statement that refutes it to the root, and the map shows what that refutation rests on. Each card gives the short name, the Lean name, the kind, the standing of the proof, whether the statement is settled, and, independently of that, whether one of its proofs is formal.

The folder receives three files. `dependency_map.svg` is the drawing. `dependency_map.html` is the same drawing for a browser: a click on a unit keeps what it rests on and what rests on it, a second click keeps its direct neighbours, and a panel shows the unit's statement. `dependency_map.json` holds the units and lines the drawing was made from, and `python <skill>/runtime/depmap.py <folder>/dependency_map.json --out <folder>` draws the map again from it without the instance.

The layout is chosen with `--layout`. `layered` computes it in Python and needs nothing else. `elk` uses ELK, which needs Node and the `elkjs` package; installing them is the user's choice (`npm install` in `runtime/depmap`). The default, `auto`, uses ELK when both are installed and the folders of the canon do not depend on each other in a cycle, and the Python layout otherwise; it also falls back to the Python layout when ELK is installed and fails. The line the command prints names the layout that was used. A note follows it when ELK was installed and not used, because it failed or because of such a cycle; when ELK is not installed, no note says so unless `--elkjs <folder>` was given to say where the package is.

The exit code is 0 on success. It is 2 when the command cannot read its input, when `--all` is given with a `dependency_map.json`, when `--layout elk` is given and ELK is missing or fails, and when the operating system reports an error, for example on a folder that cannot be written; the message on standard error says which.

### The paper

`python <skill>/runtime/paper.py <instance> --out <new folder>` writes the paper that presents the result, as LaTeX and a typeset PDF. It runs only when the root is settled by a formal proof, that is, when the root's state is `formal_proved` or `formal_refuted`; otherwise it refuses and writes nothing. Once started it runs to the end without asking anything. Its options are `--parallel <n>`, `--resume` and `--dry-run`, which this section describes below, `--model` and `--effort`, `--typeset-only`, and `--tex`, which comes last.

The command takes from the canon everything the formal proof of the root rests on. One session plans the paper, and one session for each section writes it. Both read real mathematical papers first and write as those are written; the collection they read from is described below. The command then assembles the manuscript, checks it by machine and typesets it, has it read by a session that sees nothing but the manuscript, and has it read beside real papers by sessions that report where it is written otherwise than those papers are. If a repair that followed one of the readings beside real papers rewrote the manuscript, the command has it read again, after those readings have ended, by a session that sees nothing but the manuscript. Last, it has every numbered statement compared with the statement of its element; if a repair of what that comparison found changed the manuscript, the manuscript is read in the same way once more before its statements are compared again. What a check or a reading finds goes to repair sessions, a bounded number of times, and no repair follows the last reading or the last comparison, so that the text that comes out is text that was read and compared.

No session is given the whole of what the proof rests on in one file. The planning session receives a digest, which gives every element by its statement, and has the full record of each element beside it as a file of its own. A session that writes a section receives a brief that the script makes for that section: its part of the plan, the records in full of the elements the plan puts into it, and the statements of the elements of other sections that those name. The introduction is written first. The other sections are then written side by side, and `--parallel <n>` says how many sessions run at a time; the default is 4. The same number bounds the repairs and the comparisons, which are made section by section: what was found in one section goes to a session that repairs that section alone, with the brief of that section, and the numbered statements of each section are compared by a session of their own. A finding that concerns no single section, and an error of the typesetting, go to one session that may change every part. The sessions follow [the paper method](paper-method.md), which fixes in advance how the canon becomes a paper: which elements receive a number, in which order they stand, what of the canon the paper leaves out, and that nothing of the Lean implementation shows: the paper stands in natural language and does not mention Lean. The choices in that document are the user's, and the command does not check that the user has made them: before the first paper of an instance's user is produced, ask the user to read and confirm the document, and do not run the command until they have.

The collection of real papers is the folder `<skill>/exemplars`. Its `manifest.json` lists the papers: research articles from refereed journals, of several fields and lengths, chosen for their writing and their structure. The papers themselves are their LaTeX sources from arXiv with the comment lines left out. They are copies for reading on this machine, and a `.gitignore` in the folder keeps them out of Git, since most of them may not be passed on. The command checks the collection before it launches a session. If a paper is missing or differs from the manifest, it runs `python <skill>/exemplars/fetch.py` once, which needs the network. If a paper is still missing or still differs after that, the command stops and names those papers. The planning session chooses six papers that are near the paper in subject and length, reads them whole, and leaves its account of how they are written as `study.md`. For each section it names two of the six in the plan. A session that writes or repairs a section receives that account and reads the two papers of its section. Each reading beside real papers is given four papers that the plan did not choose. These readings end when two in succession report no departure, and there are at most eight of them. When every paper that the plan did not choose has been given to a reading, the next readings are given those papers again from the first.

Planning, writing and repair use the instance's `cli` and the first entry of `models`. The reading, the readings beside real papers and the comparison use the first model of the `review` role, so that by default a different model reads than wrote. `--model <provider/model>`, for example `claude/opus`, puts every session on that one model, the reading and the comparison included. `--effort <level>` sets the effort of planning, writing and repair, and of every session when `--model` is given with it. The sessions receive no MCP servers, although a session on Codex runs with web search enabled. What confines the citations to the canon's bibliography is one of the machine checks: a citation whose key is not in that bibliography is a finding.

The folder receives `paper.tex`, `references.bib`, `paper.pdf`, `plan.json`, `study.md`, `materials.md`, `correspondence.json` and `log.json`, and the working material: `materials.json`, the parts of the manuscript under `parts/`, `state.json`, a folder for each session under `sessions/`, and `typeset/`, where the manuscript is typeset. `materials.md` holds everything the paper was written from as one text, for you and the user; the sessions are given the digest, the briefs and the records of the elements one file each, and the folder of a session holds exactly what that session was given.

A run that was stopped is continued with `--resume` and the same `--out`: after an interruption, after the command ended with exit code 1 because a session left nothing usable, or after the machine was restarted. Everything a later step needs is in the folder as soon as it exists. The command takes the materials from the canon again and compares them with `materials.json`; if they differ, the canon has changed since the run began, and the command refuses and says in what they differ. It uses a plan that is there and passes the check, does not write a part again that is in `parts/`, and reads from `state.json` which of the stages after the writing are complete: the first reading, the readings beside real papers, the reading after them, and the comparison. A stage that was begun and not ended is made again from its start on the parts as they stand, so its sessions are launched again and its bound counts from the beginning. A run that came to its end, with exit code 0, 2 or 3, has nothing to continue, and `--resume` refuses it. Without `--resume` the folder given to `--out` has to be new or empty. When a session of a section fails for good while others run beside it, the command lets those others finish and keeps what they wrote before it stops, so the next `--resume` starts from all of it.

`--dry-run` launches no session and writes nothing. It makes the checks that come before the first session, with `--resume` those of a continued run as well, and prints what the run would do next and how many bytes each session would be given. Use it before a long run to see that the folder is accepted and what the sessions will receive. The correspondence file says which element each numbered statement states, with the record's statement, the Lean statement and the paper's statement side by side, the comparison's verdict, and under `record_disagreement` any disagreement the comparison found between the record's statement and the Lean statement of the element; none of this is in the paper. Such a disagreement lies in the canon, and no repair of the paper removes it, so report it to the user. The log lists every session launched and what every check found.

| Exit code | Meaning | What to do |
|---|---|---|
| 0 | The paper is complete. | Read the paper and the correspondence file yourself before handing them over. The author line is left empty for the user. |
| 1 | The command refused or failed. | Read its message. When it failed after the run had begun, the folder holds what was made up to that point, and `--resume` with the same `--out` continues from it once the cause is removed. |
| 2 | The manuscript was produced, and findings stayed open after the bounded repairs. | Read the last `end` event of `log.json`, which lists them, and report the open findings to the user; do not repair the manuscript by hand. A numbered statement whose present text has no verdict of the comparison is one of them: the comparison did not reach it, or a repair changed it afterwards. So are the findings of the last reading of the manuscript by itself, that is, by a session that sees nothing but the manuscript. The manuscript is read in that way at three points: after it is written, after the readings beside real papers if a repair that followed one of them rewrote it, and after a repair that followed the comparison. At each point it is read at most three times. The second and the third reading take place only when the reading before had findings, and a repair follows the first and the second but not the third. Because no repair follows the last reading at a point, every part of the text has been read by such a reader, and what that reader still found is listed for you. So is a line that TeX set wider than the text block and that the repairs did not remove, and so are the departures that the readings beside real papers still reported when they ended without two readings in succession that found none. Neither a wide line nor such departures keep the paper from being typeset. `paper.pdf` is missing in two cases. In the first, the machine checks or the typesetting stayed open. The run then ended without finishing its readings and its comparison, and `--typeset-only` refuses such a manuscript. In the second, no TeX command was found, which the command's message then says. Unless the machine checks or the typesetting stayed open as well, `--typeset-only`, as in the next row, typesets the manuscript and reports the same findings again. |
| 3 | The manuscript is complete and no TeX command was found. | Once a TeX command is available, run the command again with `--typeset-only` and the same `--out`; it typesets the manuscript without repeating the planning, the writing, the reading or the comparison. A repair session is launched only if the typesetting or a machine check fails. When that repair changes a numbered statement, the statement is not compared again: the exit code is then 2, and the `end` event lists the statement as one whose present text was not compared. Only a new run of the command into a new folder compares every statement, and it writes a new manuscript. |

A TeX command is `tectonic`, `latexmk` or `pdflatex` on PATH, or the command given after `--tex`. `--tex` takes everything that follows it on the command line as that command, so it is the last option. `log.json` is a JSON list of events in the order they happened. The field `event` of each names what it is, such as `session`, `check`, `reading` or `end`, and the last one is an `end` event; the field `kind` of a `session` event names the kind of session, such as `plan` or `repair`. Installing a TeX distribution needs the user's approval.

## The judge of formal proofs

do-math takes a statement for formal from its structural index: the Lean proof is complete, and every axiom it depends on is allowed. The index is computed inside a Lean process that has loaded the modules it describes. The judge checks the same thing from outside. Lean's exporter, `leanexport`, writes a theorem out together with everything it rests on, and `lake comparator` reads that export alone: it works out the axioms again, compares the export with a second one, and replays every declaration through the kernel. Both programs come with Lean 4.35 and later. `status` says under `judge` whether the instance has a judge and, when it has none, why.

**At a publication.** Before a change is installed, the runner has the judge look at the theorems whose formal proof the change brings: those whose proof it adds or replaces and that are formal afterwards, and those it did not touch that are formal only now, because the last statement they rest on has received a formal proof. The export follows a theorem through everything it rests on, whichever publication brought each part. For that reason the judge is handed, of these theorems, only those that none of the others uses, directly or through other elements: the export of such a theorem contains the others, so they are judged in it, and handing them over as well would repeat nearly the same export once for every command line their names fill. Here the export is compared with itself, which leaves the axioms and the kernel. If the judge rejects, the change is not published: it goes to a replacement peer with the judge's reason, as a change that does not build does. If the judge cannot run, because a tool does not start or an export fails, nothing has been learned about the change. The runner then makes the publication's build once more, and if the judge still cannot run it ends with the reason in `last_error`; the publication stays where it stood and is carried on by the next `start` after the repair. The broker keeps the compiled modules of that publication's build meanwhile, however many later builds finish, so the judge finds them when it is asked again. The theorems that were judged are named in the change's `provenance.json` under `judged`, and the view of an element says at which revision its proof was judged. `init` has the formal theorems of the canon it starts from judged in the same way, and refuses a canon the judge rejects.

**At the end.** `python <skill>/runtime/judge.py <instance> --out <new folder>` judges the root of an instance whose root is formally proved or refuted, against the root as the instance's first commit fixed it. Through the instance's broker it builds the canon of the first commit and the canon as it stands, each with one added theorem that states the root, or its negation for a refuted root, and that is proved by the proof which settles the root. The judge accepts when the two statements are identical together with every definition they depend on, the axioms lie within `allowed_axioms`, and the proof is accepted by Lean's kernel and by the other kernels that Lean ships. `--no-paranoid` leaves those other kernels out.

The runner starts this command itself, as a process of its own, in two cases: once for each proof through which the root becomes formally settled, and once more before it finishes if the library has changed since that judging. It starts it only where the instance has a judge and while no publication is underway, and the runner does not finish while the command runs. `status` gives the result under `root_judge`: the proof that was judged, the library revision, the folder under `runner/` that holds `verdict.json`, and a status of `running`, `accepted`, `rejected` or `unavailable` with the reason. A rejection has left the request for a comprehensive review described below, which the runner takes up. `unavailable` means that the command gave no answer, and the runner does not try the same proof on the same library again; run the command yourself after the repair. Report the result under `root_judge` together with the formal settlement, and say so when there is none.

| Exit code | Meaning | What to do |
|---|---|---|
| 0 | Accepted. | Report it with the result. `verdict.json` in the folder records what was compared and with which commands. |
| 1 | The command refused, or the judge could not run. | Read its message. This says nothing about the proof. |
| 2 | Rejected. | Report it to the user with the reason in `verdict.json`. The command has written a request for a comprehensive review of the proof, in the form the `review` command writes, and the runner takes it up when it runs; `--no-review` leaves the request out. |

The folder receives `verdict.json`, the two source trees under `challenge/` and `solution/`, and the judge's own files under `judge/`.

**What the judge needs on the machine.** Before `lake comparator` reads anything it was given, it looks up two programs through PATH, `git` and `env`, and it does so by running a third, `which`. It makes these lookups with its sandbox switched off as well, and when both exports are handed to it and it has nothing to build. When a lookup fails it ends without judging, and it reports a missing `which` as a missing `git`. On Windows `which` and `env` are not part of the system. They come with Git for Windows, in the folder `usr\bin` of its installation, and that folder is on PATH only inside Git's own shell.

With `"auto"`, do-math therefore finds the three programs itself each time it plans a judging. It looks on the PATH of the process that plans, which is the runner, `init` or `judge.py`, and on Windows also in `usr\bin` of the Git installation in which `git` stands. It starts the comparator with the folders it found placed first on the comparator's PATH. The environment in which the Lean broker was started therefore plays no part in whether the comparator finds them, whichever process started the broker. When one of the three is not found, `init` and `start` refuse and name it, `status` gives the same reason under `judge`, and a runner that is already running ends with it in `last_error` when it next carries a change to publication. Commands that you name yourself in `lean.judge` are started in the broker's environment as it is, and what they need on PATH is yours to provide.

**What the verdict rests on.** `lake comparator` can build what it judges inside a sandbox, which needs Linux namespaces. do-math always hands it exports of modules that its own broker compiled, so that sandbox does not cover the builds, and where it cannot run at all, as on Windows, the commands carry the option that switches it off. The verdict therefore rests on those builds having been made honestly: Lean code that a session wrote runs when it is compiled, as at every compile of the instance. What the verdict does not rest on is the structural index, the views, or anything a session reported.

## Commands

Every command below is `python <skill>/runtime/runner.py <command> <instance> ...`. `init` is described under Create and start.

| Command | Effect |
|---|---|
| `start` | Launch the detached runner when none is alive, such as after a crash or reboot, checking its new readiness record. It does not replace a live runner; to restart one, end its process first, as the paragraph on restarting a live runner under Waiting, fallback and recovery explains. |
| `run` | Run in the foreground for observation; remains attached until the runner exits. |
| `status` | Read current liveness, mathematical state and operational queues. |
| `stop` | Stop new dispatch. Running CLI turns finish; pending reconsideration turns and queued follow-ups wait. The runner process stays alive; `resume` lifts the stop. To end the runner itself, wait until no session is active and end the process that `runner/process.json` names; `start` brings it back. |
| `resume` | Remove the dispatch stop. If the runner is not alive, also use `start`. |
| `reconsider-attempts` | Request one reassessment of work availability, overriding an occupancy report. Attempts then launch one at a time, each a reassessment, until one registers a section; this holds even when no occupancy report was in force. Does not remove a dispatch stop. |
| `input --file <file>` | Preserve standing information for future launches. It does not notify running sessions of new instructions. |
| `review --element <name>` | Request a comprehensive review of published elements; `--element` may be repeated, and takes the declaration name as the canon shows it. `--concern <id>` and `--reason <text>` can identify the issue. A request that names no element and no concern is refused, because the reviewer would have nothing to examine, and so is one that names an unknown element or concern. |
| `organize` | Request an organizer session for the published changes not yet in an organizer's batch. |
| `questions --file <file>` | Place questions of your own on the frontier as an operator publication, without peer or review. The file is UTF-8 JSON of the form `{"reason": "...", "questions": [{"id": "...", "statement": "...", "grounds": "..."}]}` with no other keys. `reason`, recorded in the publication, says why you place them; the list is nonempty; `statement` says what is to be understood and `grounds` what raises the question and why an answer matters, both nonempty. Each `id` matches `[A-Za-z0-9][A-Za-z0-9_-]*`, is unique in the file, is not `q0`, and does not name an existing question or question alias; a prefix such as `op-` keeps operator questions recognizable beside peer proposals, which carry a session-ID prefix. The command refuses a file that breaks these rules and otherwise leaves a request. On its next pass the runner publishes it as `knowledge/questions/<event>/questions.json` with its event and Git commit. If a publication since the command has taken one of the identifiers, the runner refuses the whole request and keeps running; the refusal and its reason appear in the runner state's top-level `last_error`. |
| `kill-session <session-id>` | Cancel the identified session's pending resumption and terminate its current CLI after confirming its OS creation identity. The session ends as an interruption: retained producing work still goes to peer, a producer that left no research material is launched again, and an interrupted peer, review or organizer stage passes to a replacement session, as Waiting, fallback and recovery describes. |
| `render` | Rebuild the derived views while the runner is off. |
| `restart-broker` | With dispatch stopped and running CLI turns, publications and compiles finished, replace the broker after an environment change. Sessions held behind the stop for their next turn do not block it; the result lists them as `held_sessions`, and they continue with the replaced broker after `resume`. A session whose work is still being published does block it, and the refusal names that session among those whose publication is to finish; publication goes on under the stop, so run the command again once `state.publication` and `state.publish_queue` in `status` are empty. |

Use status to identify the intended session before termination. The command targets that session's CLI, not arbitrary processes on the machine, but ending the CLI also ends the session: its host then exits, and on Windows, where the session's `process-job.json` records that containment was applied, the system ends every process the session started, as Waiting, fallback and recovery describes. The broker cancels its compiles after observing that the session has ended. Where containment was not applied, including on Linux, computations the session started can outlive it; interpret them from their retained outputs and actual process state.

The runner reads `review`, `organize`, `reconsider-attempts` and `questions` requests on its next pass, so a request made while no runner is alive waits until `start`. This includes a finished instance: once the root is formally settled and the remaining work has ended, the runner exits, and a later `review`, `organize` or `questions` request takes effect only after `start`, whose runner then continues until that work has ended.

Every command of this runtime refuses an instance that the earlier runtime created, whose knowledge was a repository of records and not a Lean library.

## Waiting, fallback and recovery

### What creates new work

When a producing session ends, its retained material creates peer work. A peer output that passes its **transport check**, the check that a finished session's output has the structure and references the runner needs to carry it to the next stage, is frozen as a candidate and creates review work; that check does not judge the mathematics. A review that decides to publish puts the candidate into the publication queue, described next. Available capacity and an available configured model permit each launch.

A formalizer is created for a settled statement that the root rests on, through any of its proofs, and that has no formal proof yet; once a refutation of the root is settled, the same holds for the refutation and the statements it rests on. The runner gives it one proof of that statement: among the proofs that settle the statement, with the statement's own declaration first and the others in the order of their names, the first that is not formal and whose named statements all have formal proofs. That proof's Lean text usually ends in `sorry`. It can also be complete and still not formal, when it names a declaration whose own Lean proof ends in `sorry` although that declaration's statement has a formal proof under another declaration, or when it uses an axiom the instance does not allow; status then shows a formalizer on a proof with no `sorry` of its own, and that is intended. Until there is such a proof, no formalizer is launched for the statement, so formal proofs are written from the bottom of the root's proof upward, and the root itself is given to a formalizer once it is settled and everything its proof names is formal. The runner reads what the formal proof will need from what the written proof names in Lean. One formalizer at a time works on an element, and it holds that element whole.

The organizer is created when the number of published changes that no organizer has yet taken into its batch reaches `organizer_every_records`. Organizer outputs and comprehensive reviews do not count toward that number. A concern or a contested statement creates comprehensive review work, as Read progress and results describes.

### Publication of a candidate

Publications are queued and made one at a time, because each changes the one library that every session reads and that every later candidate is built on. For a candidate, the runner copies the canon's library and applies the candidate to the copy without the replacements review declined. When that changes a Lean file, it builds every module of the library through the broker and extracts the structural index of the modules that changed and of every module that imports one of them, directly or through others; a candidate that changes only written files needs no build. The importing modules are extracted again because Lean reads a declaration in the environment its module imports: when a change enlarges that environment, for example by an import of a Mathlib module that brings another instance into scope, Lean can turn an unchanged statement into another term, and the check that no statement changed in place then finds it. Where the instance has a judge, the formal proofs the candidate brings are then exported and judged, as "The judge of formal proofs" describes. A module whose source and whose imports' compiled output are unchanged comes from the broker's cache, so most of a build is usually reuse. The runner then repeats the checks a machine can decide: no statement changed in place, every added declaration has a record and every record a declaration, no axiom was declared, no definition contains `sorry`, and Lean confirms each claim that one declaration proves or refutes the statement of another. Only then does it put the changed files into `canon/`, write the records, the approaches tried with review's assessment of what the work contributed, the understanding texts, evidence and bibliography entries, write the event, and commit.

While this runs, `status` shows the publication under `state.publication` with its stage (`apply`, `build`, `check`, `judge`, `commit`) and the waiting ones under `state.publish_queue`. A session whose work waits there has the status `publishing` and still counts toward `max_sessions`, so a queue that grows because builds wait for memory also holds back new launches.

A candidate was frozen when its peer's session ended, and other publications have changed the canon since. Statements never change in place, so what the candidate rests on is still there. It can nevertheless fail to apply or to build, through no defect of its mathematics: another publication replaced the proof it replaces, a new module's path is now taken, two candidates introduced the same name, or a machine check fails on the canon as it now is. A candidate that would not build would break the canon for every session, so the runner does not publish it. The work goes to a replacement peer, which receives the producer's work, the earlier peer's work and the reason, makes a new candidate, and that candidate receives a new review. An organizer's change that fails in the same way is made again by a replacement organizer. The pending job's error in `status` names the reason.

### Session hosts and continuation turns

An attempt, explorer, formalizer or peer's host can keep the same logical session alive across several CLI turns. After an ordinary turn exit, it resumes the exact native conversation with the same provider, model, effort and launch-time instructions. A current `output/end-decision.json` or the configured resumption limit authorizes normal handoff. Each request has a fresh ID, so an older decision cannot authorize a later ending. The protocol is described in [Retained work](retained-work.md). This does not create another attempt, another occupied section or question, or another concurrency slot.

The host of a review or an organizer keeps its session alive in the same way, for a different reason. Such a session ends with its output, an assessment or an organization, and writes no end decision. When one of its turns ends and the output does not pass the transport check, the host resumes the same conversation and tells it what the check found, at most `max_end_resumptions` times. A reviewer's turn can end while the sub-reviewers it delegated to are still at work, and without this the whole review would be made again by a new session. The authorization in the session's `end_check` record then has the basis `output_checked` when the check passed, and `resumption_limit` when it still failed at the limit; in the second case the runner starts a new session for the stage, as it does after an interruption.

`status` exposes the host's `end_check` record in each session's state, including `maximum`, `resumptions`, `status`, the current request and `authorization`. A host waiting behind the dispatch stop reports `waiting_dispatch`; a provider/model availability block reports `waiting_provider`. It retains its existing slot and scope while waiting. `resume` allows it to proceed once the availability block has also expired. `kill-session` cancels a pending resumption even between CLI processes. The host survives runner restart, and the runner collects the logical session only once after the host and CLI have ended. Host loss is recorded as an interruption, without inventing a worker end decision.

The session root retains its initial prompt and CLI streams; `turns/0001/` and later directories retain each resumed invocation separately. `end-check.json` contains the authorization and its issuer. Missing native identity or an identity change is recorded as `resume_unavailable` rather than silently starting a different conversation. Like the resumption limit, this runner authorization ends the session without interruption: a producer's retained work goes to peer, and a peer's output goes to review once it passes its transport check. A provider refusal or failed invocation instead ends this continuation through the usual interruption path. Availability handling still applies to later sessions.

On Windows the host places itself in a job object before its first turn. Processes the session starts inherit membership, including computations detached with `nohup` or left in the background, and the system ends them all when the host exits: after the last turn, through `kill-session`, or if the host dies. The job does not let a process leave it. Git Bash asks to leave on every program it starts whenever its job permits that, so a job that permitted it would not hold the computations a session runs from its shell; a tool that explicitly asks to leave is refused and does not start. Two kinds of process are outside the job. The Lean broker is shared and not session-owned, so a session held in such a job never starts it: a broker started inside the job would end with that session. The runner starts it and starts another when it has ended. A contained session's client that finds no broker waits up to twenty seconds for the runner's, and if none appears it reports that no broker is alive; the session can submit again once the runner is running. Processes started on a session's behalf by a service, for example through COM or `wsl.exe`, were never in the job. `process-job.json` in the session folder records whether containment was applied; when it could not be, the session runs uncontained, as every session on Linux does.

### Launch priority and spacing

Priority is review, peer, formalizer, organizer, eligible explore, then attempt. Fresh attempts require free capacity, at least `launch_interval` seconds since the previous attempt or exploration launch, and an element among the work that remains in the frontier that no pipeline holds whole and for whose lease no session is waiting. The runner does not judge whether mathematical work remains on such an element; that is the judgment of the attempt it launches. Attempts and explorations share the one spacing, which gives each new attempt or explorer time to take its lease before the next one reads the board. An exploration is eligible when exploration is requested, a question is free for it and the same interval has passed; the paragraphs on explorers and their questions further below explain when a question is free and when exploration is requested. An eligible exploration launches before a waiting attempt, while a request that no free question can serve does not hold attempts back. Each role waits only for its own object: attempts for an available element, explorers for a free question. The runner fills free capacity in this priority order before it launches a fresh attempt, so when every slot is in use, a slot that opens goes to waiting review or peer work first. Work that waits for something other than capacity does not hold attempts back while slots remain free: a review or peer waiting out a retry delay or for an available model, and a comprehensive review or organization pass waiting for another of its kind. Comprehensive reviews launch one at a time, as organizers do, so a requested review or organization pass waits, without an error or block in `status`, while another of its kind is running. Running sessions are not preempted when higher-priority work appears.

### Attempts that find no work

An attempt that only checked availability can write `disposition: no_research` in `output/outcome.json`. It must have registered no section and begun no mathematical investigation. An explorer that found no free question to occupy can end the same way; it must occupy no question, and its outcome carries no availability report. When the session exits successfully, the runner retains that session's files and conversation and closes the pipeline without peer or review. The session stays closed regardless of later changes in available work. Failed research and interrupted investigations still go to peer.

The attempt can also submit an `all_unresolved_work_occupied` report with the snapshot token from its coordination updates. The token identifies the elements that remained and the sections registered on them when the attempt looked. The runner evaluates that report separately. An invalid or stale report does not prevent the session from closing, but it cannot suppress dispatch. An accepted report stops the runner from launching fresh or pending attempts while the reported occupancy remains applicable.

The runner waits until one of three changes occurs: a section's occupancy ends on an element that is still among the work that remains, an element newly appears among the work that remains, whether it is new or a finding withdrew the confirmation of its proof, or the operator requests reconsideration. Occupancy ends through publication or a completed review decision that there is nothing to publish; releasing a lease or leaving its queue does not end it. Elapsed time, publications that add no work that remains, organization changes and sections that other sessions newly register do not end that wait. The runner then permits one reassessment attempt at a time. Once an attempt registers work, normal scheduling resumes. Another applicable report of full occupancy makes the runner wait again. An interrupted reassessment can be replaced, and any research it retained follows the ordinary processing path.

`status` reports this wait or reassessment under `attempt_dispatch`. It identifies the reporting session, snapshot token, current grounds and any reassessment session. Use `reconsider-attempts` to request reassessment explicitly. An older report cannot undo that request. The command does not remove a dispatch stop; a stopped instance still requires `resume` before any new session can launch.

Full occupancy also requests exploration, so capacity that attempts cannot use goes to understanding while they wait.

### Explorers and their questions

Explorers occupy **questions**, the frontier's objects of understanding; the workers' [common introduction](common.md) defines them. Several explorations can run at once, each holding a different question, and a question stays occupied through its exploration's peer and review. An organizer's merge is the one exception to a question's single holder: when two questions that explorations already hold are merged, both explorations keep the merged question, each until its own pipeline ends, because each took its question rightfully and the merge does not cut work short. The question is not free while either occupation lasts, so no new explorer duplicates their work, and it becomes free once both have ended; `status` and the board then show two explorations on it.

A question is **free** when it is open, no unfinished exploration holds it or was assigned it, and no live session holds or waits for its lease. One case is counted differently. An exploration whose launch ended without research material waits to launch again, and until then its pipeline still names the failed session, whose declaration may still record the question that launch held. `status` and the board show that session holding the question, though no live explorer does, and when the runner launches a waiting exploration it does not count such a question as occupied.

The runner launches one more explorer only while the free questions outnumber the explorers that have not yet chosen one, so that every explorer launched can find a question of its own. When question `q0` is free at launch, the runner assigns it to the new explorer and records the occupation before the session starts; otherwise the explorer chooses among the free questions through the question lease. While `q0` is free in this sense, the question commands refuse every other question, so an explorer still choosing when `q0` becomes free takes it.

Exploration is **requested** by a single flag. Two events set it: an attempt launch when the count of attempt launches reaches a multiple of `explore_every`, every launch by default; and the runner finding spare capacity while no element of the work that remains is available to a new attempt or while attempt dispatch is suppressed. The second event, spare capacity with no element available, is the usual one once the root is settled and only formal proofs are still to be written. Repeated triggers coalesce into one request. When the flag is set and a question is free, one explorer launches ahead of any waiting attempt once the launch interval has passed, and the flag clears. When the flag is set but no question is free, it stays set until a question opens or an occupation ends, and attempts dispatch as usual meanwhile. While no element is available the flag is set again after each launch, so the free questions fill with explorers one by one, a launch interval apart, until none is free or capacity is used. Launching an explorer does not reset the attempt-launch counter. Each attempt launch counts once, whether or not that attempt later registers a section or ends without research.

### Refusals, failed outputs and damaged candidates

A typed provider usage refusal blocks that provider until its known reset, or a configured backoff when the reset is unavailable. Model-specific refusals block that model. A new launch uses the first available alternative in its role's list. If all are unavailable, the job remains pending. A producer interrupted after doing work ends and proceeds to peer; it is not silently resumed under another model. A session that failed before leaving any research material can be retried as an operational launch.

Interrupted peers, reviewers and organizers receive fresh replacement sessions with their partial material and the error. When a completed session's output fails its transport check, the affected job waits for an exponential retry delay, up to `retry_max_seconds`. The same delay precedes the replacement of a peer, reviewer or organizer interrupted by anything other than a provider/model refusal or a failed launch, such as a crash or `kill-session`, and the relaunch of a producer cancelled before it left research material. Neither delay blocks the model for other jobs or changes their configured model preference. Actual provider/model refusals and operational launch failures retain their availability handling, so a configured alternative can be used while the affected service is unavailable. Status exposes the pending job's error and retry time as well as availability blocks. Repair broken paths, login or configuration when necessary. Mathematical uncertainty and incomplete formalization are handled through the elements and their reviews, not inferred from process failure.

A successful session launched after an availability block's deadline clears that provider's or model's old backoff history. A later isolated refusal therefore begins with the initial delay. A session that was already in flight before a newer block cannot clear it merely by finishing successfully; the newer refusal still governs new launches.

If a frozen candidate's files change during review or before publication, retrying the same damaged files cannot complete that review. The runner preserves the damaged candidate and compares the peer's retained output with the hashes fixed at review assignment. Matching output is copied to a new candidate location for a fresh review under the same hashes. If those bytes are unavailable, a replacement peer receives the original research and earlier peer work, develops a new candidate, and sends it through independent review. An assessment of the damaged candidate never authorizes publication of the replacement. A candidate whose files are intact and which no longer applies to the canon or does not build on it takes the path described under Publication of a candidate above.

### Restarts, runner failures and installation updates

After a runner crash or machine reboot, use `start` on the same instance. The runner identifies existing processes by PID and creation identity, follows those still alive, and collects ended work. Publication uses a saved identity, staging directory and Git commit; restarting continues the same publication, with the build it had started, and completes it and its follow-ups without publishing anything twice. Do not delete locks or edit runner state to force recovery. Use shells at the same privilege level on Windows, because process-query access is part of liveness detection.

The runner also ends by itself when one of its own operations fails, such as a Git commit or a read or write of its state files. `status` then reports `runner_alive` as false while `finished` is false. When the error is a Python `OSError`, `ValueError`, `KeyError` or `RuntimeError`, the four kinds the runner records and among which those two examples fall, the runner state's top-level `last_error` holds that error and its time, apart from the errors of individual jobs, provided the state file could still be written. Whatever the kind, the call stack is in the stderr log that `start` named when it launched that runner, and for an error of another kind that log is the only record. Repair the cause before using `start`, because a restart that meets the same failure ends again, possibly after `start` has already confirmed readiness. A recorded `last_error` stays in the state after later starts, so compare its time with the `at` of `runner/process.json`, which records when the current runner started, before attributing a present problem to it. A `questions` request the runner refused is also recorded there, naming the request, while the runner keeps running.

Running out of memory is the exception: the runner does not end. It holds a small memory reserve for this case. When one of its operations fails for lack of memory, it releases the reserve, writes `Runner memory reserve released; dispatch will wait for recovery.` to the same stderr log, and then makes no pass at all, collecting, publishing and dispatching nothing, while the machine's free memory (`MemAvailable` on Linux, the commit headroom on Windows) stays below 512 MiB. Once free memory reaches 512 MiB, it takes the reserve back, reloads its saved state and the published research, and continues. Meanwhile `status` reports the runner alive and records no new `last_error`, although nothing advances; freeing memory on the machine lets it continue without a restart.

Worker guides and launch options are fixed for sessions already started. Updated guides are read for later launches. A runner already running keeps its imported launch code until it is restarted, and a session host already running keeps the code it loaded at launch; updating the installation does not rewrite saved session contexts or commands. Continuation messages are the exception: before each resumption, the session host reads `resume/common.md` and `resume/<role>.md` from its configured installation. Editing those files changes the next resumption without a runner or host restart. A continuation file the host cannot use, a `resume/<role>.md` that is missing or empty or a `resume/common.md` without exactly one of each placeholder, ends the session host at that session's next resumption. The error and its call stack are in the session's `host.log`, and the runner records the end reconsideration as `interrupted`: a producing session goes to its peer without that reconsideration, and a peer is replaced, each later session ending the same way until the file is repaired. The exact source files are saved under that turn's `guidance/` directory along with its rendered `prompt.txt`; turns already underway retain their delivered text. The code behind a session's commands is a second exception. The command arrays in `input.json` name the installed `runtime/coordination.py`, `canon_tool.py`, `check.py` and `lean_broker.py`, and each coordination, canon, transport-check or broker-client command starts that installed file afresh, together with the modules it imports, such as `knowledge.py` and `canon.py`. An edit to that code therefore reaches running sessions at their next command, while the runner, the session hosts and the broker keep the code they loaded, so until those are restarted the two sides read and write the shared coordination and state files with different code.

Changing runtime code still requires restarting the runner for future launches. `start` does not replace a runner that is still alive: the new process cannot take the instance's lock, so it exits and `start` reports that the runner exited before readiness. To restart a live runner, end the one process that `runner/process.json` identifies as this instance's runner, then use `start`. Session hosts and the Lean broker are separate processes and keep running; the new runner follows them and completes unfinished publication as it does after a crash.

### Retention and archives

Each launch retains its guides, references, user inputs, settings and the views of the research it was given. The available conversation and artifacts are retained for each producing session. The work of one producing session finishes processing after its peer has prepared a candidate and review has either led to publication or decided there is nothing to publish. The runner launches a separate archiver process to compress each associated session's work/ into work.tar.xz in that session directory. It verifies file names and hashes before removing work/. When work/ cannot be read or verified, or contains a symbolic link or junction, which could lead outside the session, the archiver leaves work/ in place, along with any archive already there, and records the session and the error in `runner/archive.log`; later archive passes try that session again. A standalone review or organizer's work directory becomes eligible when its own job completes. Output files, context and retained conversations remain available; restore archived work with an xz-capable tar reader when needed.

The canon contains what later researchers need, and a session's own account stays outside it. The originals remain recoverable for the operator and for a designated reviewer examining the elements that came from them, within the scope described in the [review guide](../roles/review.md). `provenance.json` in a published change's folder names the producing, peer and review sessions, and an entry of the approaches tried names the sessions that contributed to it.

### Changing Lean

Changing Lean or its libraries requires a new `lean.cache_epoch`. Stop new dispatch and let running CLI turns, publications and compile jobs finish; sessions waiting behind the stop for their next turn need not end. Update the Lean configuration in the instance's own `settings.json`, including a new `cache_epoch`, then run `restart-broker` and resume. This prevents a module cache identified by an old environment from being treated as evidence for a changed installation.

The canon is itself a library compiled in that environment. A peer's preparation of its candidate, review's verification and every publication that changes a Lean file build all of it. After the change the cache holds nothing for the new environment, so the next such build compiles every module of the canon again. If a module of the canon no longer compiles under the changed Lean or imported library, no candidate can be prepared: each peer's output fails its transport check and the peer is replaced, again and again, and a candidate that was already under review fails its build at publication. Before you resume, you can therefore build the canon in the new environment with the broker's own `build` command, in the form [Lean](lean.md) gives, with `<instance>/canon/lean` as the module root, its files as targets, a memory estimate, and a name of your own, such as `operator`, as the session. The build writes its output to the broker's folders and leaves the canon as it is. A canon that no longer compiles is a reason to return to the earlier environment and report to the user.
