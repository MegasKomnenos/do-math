# Running Lean in a do-math instance

This document explains how Lean is run inside a do-math instance, why it is run that way, and what a session needs to know to use it well. It starts from what a Lean compile is and what it costs, because everything else follows from that.

## What a Lean compile is, and what it costs

When a session has written a Lean file and wants to know whether the proofs in it are correct, it has Lean check the file. Lean reads the file from top to bottom, loads every library module the file imports, elaborates each definition and theorem in turn, and reports errors, warnings and the output of commands such as `#print axioms`. In this document that whole run of Lean over one file is called a compile, and the process that performs it is a Lean process.

A compile takes time, and with Mathlib it takes a lot of it. Most of that time is spent at the start, loading the imported modules: a file that imports all of Mathlib reads several gigabytes of compiled library from disk before it looks at the first theorem. When those files are not yet in the operating system's cache, that alone took seven minutes on the machine this project was developed on. Time, though, only delays a result. A slow compile is a nuisance; it does not harm anything else that is running.

Memory is different. A compile that takes more memory than the machine has left does not merely run slowly; it pushes the machine into swapping, or gets itself or some other process killed, and every session on the machine suffers. So memory is what this document is mostly about, and to reason about it one has to know that a Lean process uses memory in two ways that behave very differently.

The first is the imported library itself. Lean maps the compiled modules into memory directly from the files on disk. The operating system treats such mappings as a cache: it keeps one copy of each file in memory no matter how many Lean processes are using it, and it can drop pages and read them again when memory is short. So this part of a compile's memory is shared between compiles, and under pressure it slows things down but does not run the machine out of memory.

The second is the memory that belongs to one Lean process alone. On import, Lean builds its own indexes over everything it loaded: the table of names, the sets of `simp` lemmas, the instances, the notations. For all of Mathlib this comes to about a gigabyte, and every running compile builds its own copy. Then, as the file's proofs are elaborated, Lean allocates terms, goals, tactic states and caches, and this part grows with what the proofs do: a `rfl` costs almost nothing, while an unbounded `simp` over all of Mathlib or a large `decide` can take gigabytes. Lean keeps the memory it has freed for reuse rather than returning it to the system, so within one compile this private memory mostly grows, and it reaches its peak late.

Of the two, it is the private memory that has to be managed. The shared library costs the same whether one compile or five are running; the private memory is paid once per compile, and it is the sum over all running compiles that must stay within what the machine has. That sum is what nothing used to control. Up to eight sessions could each start a compile whenever they liked, with nothing between them, and several Mathlib compiles at once were enough to make the machine unstable.

## The Lean broker

To prevent that, each instance runs a single process called the Lean broker, and every compile in the instance goes through it. The runner starts the broker when it starts and keeps it running for as long as the runner itself runs. A session does not run Lean itself; it asks the broker to compile a file, and the broker decides when to start that compile, runs it, and hands the result back.

Because the broker sees every compile of the instance, it can do several things that no session could do on its own.

It keeps the total memory of the running compiles within a budget. A session tells the broker, when it submits a file, how much private memory it expects the compile to need. The broker uses that estimate, together with what it has measured itself, to decide whether the compile can start now or must wait for others to finish.

It measures every compile. While a compile runs, the broker reads how much private memory the Lean process is using and keeps the peak; when the compile ends, it records the peak and the duration, returns them to the session, and adds them to a table it keeps for the instance. So the cost of every proof becomes visible, and the broker's later decisions are based on what compiles in this instance have actually cost, not only on what sessions predicted.

It keeps a compile alive independently of the session's shell tool. The shell tools of the CLIs give up on long commands, as 'Long-running commands' in [common.md](common.md) describes, and a Mathlib compile can outlast them. A compile submitted to the broker is a job that continues, and keeps its result, whatever happens to the command that submitted it. The session can come back for the result as many times as it needs.

It cleans up after sessions that have ended. A compile whose session has finished, failed or been killed has no one left to read its result; it only takes memory. The broker cancels such compiles. Apart from a cancellation that a session asks for itself, this is the only situation in which the broker stops a compile: it never stops one for using more memory than was estimated.

There are also things the broker does not do, and it helps to know them from the start. It compiles one file per job with the `lean` command from the instance's settings; it does not run `lake build`, and it does not keep a Lean environment loaded between compiles to save the import time. Each compile imports everything it needs from scratch. And it does not limit how long a compile may run.

## Compiling a file

The launch prompt of every session contains the exact command to use, with the session's own ID filled in. In its general form it is

```text
python <skill>/lean_broker.py run <instance> <file.lean> --session <session ID> --expect-mb <MiB>
```

where `<file.lean>` is the absolute path of the file to compile, `<session ID>` is the session's own ID as given in its launch prompt, and `<MiB>` is the session's estimate of the compile's peak private memory, in mebibytes. The next section explains how to arrive at that number.

The broker compiles the file with the `lean.command` of `settings.json`, adding the thread count it has been configured with and the path of the file. The working directory is `lean.cwd` from the settings, or the session's folder when that is `null`, as it was when sessions ran Lean themselves. When the compile finishes, the command prints Lean's output exactly as Lean produced it, the standard output on standard output and the standard error on standard error, so that error messages, `#print axioms` lines and `sorry` warnings read as they would from Lean. It then exits with Lean's exit code. The last line on standard error is a summary from the broker:

```text
lean-broker: {"job": "j…", "status": "finished", "exit_code": 0, "reason": null, "expect_mb": 1800,
  "measured": {"peak_mb": 1466.2, "baseline_mb": 1103.5, "excess_mb": 362.7, "seconds": 41.3, "estimate_ratio": 0.81, …},
  "dir": "<instance>/runner/lean/jobs/j…"}
```

The numbers in this line are made up to show the fields. `peak_mb` is the highest private memory the broker measured during the compile, `baseline_mb` is what the compile's imports alone cost (explained below), `excess_mb` is the difference, `seconds` is how long the compile ran, and `estimate_ratio` is the measured peak divided by the estimate. `dir` is the folder where the broker keeps the job's files: Lean's output in `stdout.log` and `stderr.log`, the job's record in `result.json`, and a few process receipts. The output can be read again from there at any time.

A `status` other than `finished` means that Lean did not run to the end. The status is `failed`, with a `reason`, when the request could not be accepted, the file had disappeared, Lean could not be started, or the process that was supervising Lean was lost; the command then exits with code 3. The status is `cancelled`, with exit code 4, when the job was cancelled. Neither says anything about the Lean source. In a review, such an outcome is grounds for `not_checked`, never for `rejected`.

### When the shell tool will not wait

The `run` command waits for the compile, and a compile can take longer than a CLI's shell tool is willing to wait: Claude's tool moves a command to the background after 120 seconds, or after 600 seconds if a `timeout` is given, and abandons it ten minutes after that; Codex's tool returns after about ten seconds and expects the session to poll. A compile that imports Mathlib, or that has to wait its turn behind other compiles, can exceed both.

For such compiles, submit and wait in two steps:

```text
python <skill>/lean_broker.py submit <instance> <file.lean> --session <session ID> --expect-mb <MiB>
python <skill>/lean_broker.py wait <instance> <job> --timeout 500
```

`submit` returns at once and prints the job ID. `wait` returns either the finished result, printed exactly as `run` would print it, or, if the timeout passes first, exit code 124 and a note that the job is still running. Nothing is lost between calls; `wait` can be run again and again until the result is there. If a `run` was started and its shell tool gave up, the same recovery works, because the job ID is the first thing `run` prints on standard error.

Submitting a file again while its earlier job is still queued or running does not start a second compile. The broker answers the new submission with the ID of the job already in progress, and waiting on either ID gives the same result.

### The other commands

| Command | What it does |
|---|---|
| `result <job>` | Prints the job's record as it currently stands. |
| `status` | Prints whether the broker is alive, the configuration it is using, the Lean version, and the jobs that are queued, running and recently finished, each with its estimate, its reservation and its measurements. |
| `cancel <job>` | Cancels one of your own jobs that you no longer need. |
| `version` | Prints the Lean version string, which the broker obtained by running `version_command` once. This is the string to put in a result's `lean.version`, and it is the reason there is never a need to run Lean directly, even for `--version`. |

All of these take the instance path as their first argument, like `run`.

## Estimating what a compile will need

Every submission carries an estimate of the compile's peak private memory. This is the number the broker reserves on when deciding whether the compile can start, so the quality of the scheduling depends on it. It is worth understanding what the broker does with the number, because that shows what kind of number to give.

The estimate is read as a probable peak: the amount that the compile will, with about ninety percent confidence, stay under. It is not meant to be the worst case. The broker reserves memory on the assumption that the compile may reach this number but is not likely to exceed it, and it pools the uncertainty of all running compiles rather than adding their worst cases, as the section on scheduling explains. An estimate padded up to the worst case therefore does not make the compile safer; it makes the broker hold memory idle and delays the compiles that come after, including the session's own. An estimate that is too low is not punished either, but it is visible: the broker compares every estimate with the measured peak and reports the ratio in the summary line, and the pooled spread and the machine gate, described under scheduling, are what stand between an under-estimate and an over-committed machine. An honest, well-reasoned number is the one that serves the session best.

The estimate is built from two parts, and the broker provides the first.

The first part is the baseline: the private memory that the file's imports alone will cost, before any proof is elaborated. This depends only on which modules are imported, so it is the same for every file with the same imports, and it can be measured once. The broker does that. The first time it sees a file with a particular set of imports, it compiles a file containing only those `import` lines and records the peak memory and the time that took. It keeps these measurements in the calibration table, `<instance>/runner/lean/calibration.json`, with one entry per set of imports under the Lean version in use. Each entry records the baseline, the import time, and, as real compiles with those imports go through, how much memory each one used above the baseline and how long it ran. An entry whose calibration compile failed records the failure instead of a baseline. A session can read the entry for its own imports and take the baseline from there. If there is no entry yet, the broker will create one before the session's compile runs, and the compile waits for it; this happens once per set of imports in an instance.

The second part is the allowance for elaboration: how much the file's proofs will add above the baseline. This is a judgment about the file, and it is the part only the author can make. The table below gives orders of magnitude for the usual cases. When the calibration table already has measurements for this set of imports, those are better evidence than the table, because they come from this run's own files.

| What the proofs do | Memory above the baseline |
|---|---|
| `rfl`, `exact`, `rw`, `intro` and `apply` chains, `simp only` with a few named lemmas, `omega` or `linarith only` with the context cleared | small: tens of MiB |
| `simp` with named lemma sets, `norm_num` on ordinary numerals, `ring`, `field_simp`, ordinary `aesop` calls, several such declarations in one file | moderate: a few hundred MiB |
| unrestricted `simp` or `simp at *` over a large import, `nlinarith` or `polyrith`, `omega` with many hypotheses, instance searches through large class hierarchies | large: around a gigabyte |
| `decide` on anything beyond tiny finite problems, `norm_num` on very large numerals, kernel reduction of big definitions, `#eval` of heavy computations | very large and hard to bound; these are also the cases worth rewriting, as the next section explains |

Lean elaborates declarations in parallel when it has more than one thread, and the broker gives each compile the number of threads set in `lean.threads` (two by default), so a file with several heavy declarations can have that many elaborating at once. Allow for that.

When a session has neither table entries nor a clear reading of the file to go on, it should say so in its `verification`, estimate from the table above, and let the measurement correct it. Afterwards, the `verification` of the result should record the estimate that was given and the peak and duration the broker measured, with a note on any notable difference. That gives a reviewer who recompiles the file a measured number to start from, and lets the plan see which results are expensive to verify again.

A reviewer estimating for a file written by someone else has the same means: the author's reported measurement, the calibration table's entry for the file's imports, and the file itself. Appending `#print axioms` lines to a working copy does not change its cost.

## Writing Lean that compiles cheaply

The broker bounds the harm of an expensive compile, but it cannot make a compile cheap. That is in the hands of whoever writes the file. The practices below are what experienced Mathlib users do as a matter of course; each is given with the reason, so that the same reasoning can be applied to cases not listed here. In a do-math session, where every compile shares one budget with every other session's compiles, they are the expected way of working.

**Import only what is used.** `import Mathlib` loads the whole library and builds Lean's full private index on every compile. Importing only the modules actually needed cuts both the baseline and the import time by an order of magnitude or more. Start from the modules the relevant objects are defined in. Once a proof is finished, Mathlib's `#min_imports` command prints the smallest set of imports the file needs; replace the imports with its answer. Broad imports are fine while looking for lemma names, but not in the file that is compiled over and over.

**Compile fewer times, and compile less each time.** Every compile imports from scratch, so there is no saving from compiling often. Write all the statements first, each with `sorry` as its proof, and compile once: statement errors are the cheap kind, and `sorry` costs nothing to elaborate. Then fill in proofs a few at a time. When one lemma is hard, work on it in a scratch file that contains only the imports and the statements it depends on, and move the finished proof back. And before the final compile, append the `#print axioms` lines to the working copy, so that the proof and its axiom check are one compile rather than two.

**Use search tactics to find things, not to prove things.** `exact?`, `apply?`, `rw?`, `simp?`, `aesop?`, `hint` and `polyrith` search the library. Their cost grows with the size of the import, and they are the most common reason a small file compiles slowly. Run one of them once, read what it found, and put the explicit term, or the `simp only [...]` call that `simp?` prints, into the file. A published file contains no `?` tactics.

**Keep automation bounded.** Write `simp only [a, b]` rather than bare `simp`, and `linarith only [h1, h2]` rather than `linarith`. Before calling `omega`, `linarith` or `nlinarith`, `clear` the hypotheses they do not need, because they consume the whole context and `nlinarith` grows combinatorially with it. Use `norm_num` for arithmetic on numerals rather than `decide`: `decide` is evaluated by the kernel, which has no heartbeat limit, and a large `decide` is the classic way for a compile to take gigabytes without producing any error before the operating system steps in. `native_decide` is not an alternative, because the axiom it introduces is outside the allowed ones in [common.md](common.md). When instance search is slow, give the instance explicitly with `haveI` or `(inst := ...)`. While iterating, put `set_option maxHeartbeats 50000 in` before a declaration so that a runaway tactic fails within seconds; raise the limit locally, with `in`, only for a proof that needs it.

**Measure before optimizing.** Mathlib's `count_heartbeats in theorem ...` prints what a declaration costs in heartbeats. `set_option profiler true` prints the time of each step. `set_option trace.Meta.synthInstance true` shows an instance search that is looping, and `set_option trace.Meta.Tactic.simp.rewrite true` shows what `simp` is rewriting. The broker's measured peak and duration are the same kind of evidence for the file as a whole.

**Shape the file for how Lean runs it.** Prefer many small lemmas to one large `by` block: the memory of a declaration is released when it finishes, and small declarations can be elaborated in parallel. Give every `have` its type, so that Lean does not have to infer a large term. Mark heavy definitions `@[irreducible]`, or define them with `irreducible_def`, so that tactics do not unfold them by accident. Use `rw` for a single rewrite, and `show` or `change` to fix the goal before handing it to automation.

**Across sessions.** An author publishes the file with narrowed imports and no search tactics, together with its measured cost. A peer works through the mathematics and does not need to recompile ([peer.md](peer.md)). A reviewer recompiles once, with the axiom lines appended ([review.md](review.md)).

## How the broker decides what runs

A session does not need this section to use the broker, but it makes the output of `status` readable and explains why a compile is waiting. The broker has no limit on the number of compiles running at once. It has a memory budget and a thread budget, and it starts the next compile when both have room for it.

**The memory rule.** For each compile that is running, and for the one the broker is considering, it forms a reservation made of three numbers. The first is the certain part: the baseline for the compile's imports, because every compile with those imports will reach it, replaced by the compile's measured memory once that has grown past the baseline. The second is the expected excess: how much more the compile is expected to take above the certain part. The third is the spread: how uncertain that expectation is. The expected excess and the spread are derived from the session's estimate, read as a ninetieth percentile, and from the spread the broker has observed for that set of imports in this instance, using `default_spread` until there are measurements. As a compile runs and its measured memory grows, what it has already taken moves into the certain part, and what the expectation had already predicted is no longer counted again.

A compile can start when, over the running compiles and the candidate together,

```text
sum of certain parts + sum of expected excesses + confidence × sqrt(sum of squared spreads) ≤ memory_budget_mb
```

The certain parts and the expectations are simply added. The spreads are not: they are combined under a square root, because the compiles do not all reach their peaks at the same moment, and the chance that they do falls quickly as their number grows. Four uncertain compiles need about twice the safety margin of one, not four times. This is what lets several compiles share the budget. The `confidence` setting is the one knob: at 1.3, which is the default, there is roughly a ninety percent chance that the sum stays under the budget; at 2, about ninety-eight percent; at 0, only the expectations are reserved. Adding up every compile's full estimate instead would be the infinitely cautious end of the same scale, and it is not the rule because it would leave most of the budget idle most of the time. (The rule is the equivalent-capacity admission control used in communication networks; the problem is the same.)

**The thread budget.** Each compile reserves the number of threads in `lean.threads`; a calibration compile reserves one. A compile can start when the reserved threads, with its own, do not exceed `cpu_threads_budget`. The default budget is twice the number of logical cores, on purpose: a compile uses its threads only while elaborating, not while loading imports, so letting one compile's import overlap another's elaboration keeps the cores busy.

**The machine gate.** Whatever the budgets say, a compile starts only if the machine's actual free memory (`MemAvailable` on Linux, the commit headroom on Windows) would remain above `min_free_memory_mb` after the compile's certain part is taken. The budgets know nothing about the CLI processes, the archiver, another instance on the same machine, or anything else that uses memory. The gate is what sees them.

**The order.** Queued compiles are considered in the order they were submitted, and the first one that fits is started. A compile that does not fit yet is passed over, so a small core-only compile can go ahead of a queued Mathlib compile that is waiting for memory. Passing over is limited, so that a stream of small compiles cannot keep a large one waiting forever: each queued compile counts how many later compiles have started ahead of it, and once that count reaches `max_passes` (three by default), nothing behind it may start until it has. The running compiles then finish on their own, and as soon as the waiting compile fits, it starts. This bounds how long any compile can wait without the broker having to predict how long compiles take. A compile that would not fit even on its own is started when nothing else is running, because refusing it forever would amount to a kill policy.

**Calibration.** A compile whose imports have no entry in the calibration table waits for a calibration compile of those imports, which the broker creates itself: a file of only the `import` lines, compiled with one thread and reserved at `calibration_expect_mb`, since its cost is by definition not yet known. Its measured peak becomes the baseline and its duration the import time. If Lean runs the calibration compile and rejects it, for instance because an import does not exist, the failure is recorded in the table instead of a baseline, and compiles with those imports go ahead on their own estimates, with the whole estimate treated as certain, and succeed or fail on their own terms; that closure is calibrated again only under a different Lean version, or if the entry is removed from the table by hand. If the calibration compile could not be run at all, or was cancelled, nothing is recorded, and the next compile with those imports triggers calibration again.

**Cancellation.** A compile is cancelled, and its process tree terminated, when the session that submitted it has been integrated, has failed, or is recorded as running while both its host and its CLI are dead. Such a compile has no reader, and compiles like this are how orphaned Lean processes used to pile up after a shell tool's ten-minute abandonment or a `kill-session`. The `cancel` command does the same on request. Nothing else stops a compile; there is no time limit and no memory limit on one that is running.

**Measurement.** Four times a second, the broker reads the private memory of the compile's whole process tree, since `lake env lean` is two processes, and keeps the highest value. When the compile ends it records the excess above the baseline and the duration in the calibration table, the ratio of measured peak to estimate in the job's summary, and the whole job in its `result.json`.

## Settings

The broker's settings live in the `lean` block of `settings.json`, alongside `command`, `version_command`, `cwd` and `env`. All of them are optional: a settings file written before the broker existed is valid and receives the defaults.

| Key | Meaning | Default |
|---|---|---|
| `memory_budget_mb` | The private memory the broker may have reserved for compiles at one time | `null`, which means the machine's physical memory minus `min_free_memory_mb` minus 512 MiB for each of `max_sessions`, and at least 1024 |
| `confidence` | The multiplier of the pooled spread in the memory rule | `1.3` |
| `min_free_memory_mb` | The machine gate: how much free memory must remain after a compile starts | `2048` |
| `cpu_threads_budget` | How many threads the running compiles may reserve together | `null`, which means twice the number of logical cores |
| `threads` | The `--threads` value given to each compile | `2` |
| `priority` | The process priority of every compile: `below_normal`, `normal` or `idle` | `below_normal` |
| `max_passes` | How many later compiles may start ahead of a queued compile that does not fit before it closes the queue behind it; `0` makes the order strictly first come, first served | `3` |
| `calibration_expect_mb` | The memory reserved for a calibration compile, whose cost is by definition not yet known | `2048` |
| `default_spread` | The spread of a compile's elaboration excess relative to its mean, used for a set of imports until the broker has measured its own; `0` reserves the expected excess only | `0.5` |

The keys are validated by `load_settings` in [runner.py](runner.py) at `init` and at every start of the runner, so an invalid value stops the runner with the error in its start log. The broker validates them again when it starts, since a session may start it while no runner is running.

The broker re-reads `settings.json` whenever the file changes. A valid change takes effect within a second and is written to `runner/lean/broker.log`; an invalid one is logged and ignored, and the last valid configuration stays in force. The `status` command shows both the configuration in force and any current `config_error`. The Lean version is read once, when the broker starts, and calibration entries are keyed by it, so after a change of Lean or Mathlib the broker should be restarted (stop the runner, let it and the broker exit, start again): the new version then gets fresh baselines while the old entries stay in the file as history. A compile that is already running keeps the `threads` and `priority` it started with.

Two notes on the defaults. On a machine with simultaneous multithreading the number of logical cores is twice the number of physical cores, so the default thread budget is four times the physical cores; this is intended, and all thread arithmetic in this document is in logical cores. The priority is applied by the process that supervises each compile, with `nice` on Linux and the priority class on Windows, so the runner, the session hosts and the CLIs get the processor ahead of compiles when it is contended. Priority does not limit anything; it only decides who goes first.

When several instances run on one machine, each has its own broker with its own budget, and each derived budget assumes the whole machine. Set `memory_budget_mb` explicitly in each instance to its share, and let the machine gate handle the rest.

## How the broker lives and recovers

The broker is the `serve` command of `lean_broker.py`, run as a detached process like the runner's other helpers. It holds the lock file `runner/lean/lock`, the same kind of operating-system lock as the runner's own `runner/lock`, released automatically when the process dies, so there can never be two brokers for one instance. It records its identity in `runner/lean/process.json`, its state in `runner/lean/state.json`, the calibration table in `runner/lean/calibration.json`, new requests in `runner/lean/queue/` and each job in `runner/lean/jobs/<job>/`. All of this is under `runner/`, outside the instance's Git.

The runner starts a broker when it starts, and starts another on any later tick where it finds no live broker, for as long as the runner runs. It checks liveness by process identity, the PID together with the process's creation time, so a reused PID is not mistaken for the broker. A broker it finds alive is adopted, whoever started it. The runner never stops a broker, and the runner's own exit does not end it: the broker keeps serving the sessions that are still running. A session that finds no live broker starts one itself before submitting, and the `wait` command does the same while waiting, so compiling never depends on the runner being alive. If two starts race, the lock decides: the loser exits at once and the session waits for the winner. The broker exits on its own when the instance is complete or halted, no session is active, and no job is queued or running, which is the same condition under which the runner exits.

Each compile is supervised by a small process called the job host, the `_job` command of the same file. It is the counterpart of the session host described in [RUNTIME.md](RUNTIME.md), and it exists for the same reason: on Linux, only a process's parent can learn its exit code, so the process that starts Lean must be one that will still be there when Lean finishes, even if the broker has died in between. The broker writes the job's launch file and records the host's identity in its state before it writes the `GO` file that allows the host to start Lean; a host that never receives `GO` exits without starting anything. The host records Lean's identity in `process.json` when it starts and the exit code in `exit.json` when it ends. So when a broker dies in the middle of a compile, nothing is lost. The next broker reads the jobs the old one left as running, follows by identity those whose host or Lean process is still alive, reads their `exit.json` when it appears, and puts back into the queue any job whose Lean had not started. A job whose host has disappeared without writing an `exit.json` is marked failed, with that reason; it is never silently run again.

The runner's `status` command includes a `lean` object with the broker's liveness, its configuration, the Lean version, the queued and running jobs with their estimates, reservations and measurements, the number of finished jobs, and the path of the broker's log. The `kill-session` command now also ends the session's compiles, indirectly: once the session is dead, the broker cancels its jobs by the rule above. The archiver that compresses finished sessions' `work/` leaves `runner/lean/` alone; finished job folders hold only Lean's output and a few small receipts.

## Instances created before the broker

An instance created before the broker existed needs no change to its files. Its `settings.json` is valid and receives the defaults; the runner starts a broker at its next start; the first compile with each set of imports triggers that set's calibration. Sessions that were started under the old instructions will keep running Lean directly until they finish, outside the budget. So block new dispatch with `stop`, let the running sessions finish and be integrated, and only then replace the code and restart, as the other notes on carrying instances over in [RUNTIME.md](RUNTIME.md) describe. Nothing in the published records changes.

## What has been confirmed, and what has not

[tests/test_lean_broker.py](tests/test_lean_broker.py) exercises the broker with a stand-in for Lean, [tests/fake_lean.py](tests/fake_lean.py), whose memory use and running time the tests control. It confirms the reservation arithmetic and the pooling of spreads; the settings defaults, derivations and rejections; the job host's `GO` and `CANCEL` gate and its exit records; calibration of a new set of imports and the wait for it; admission under the memory budget where adding up peaks would have refused; the thread budget and the rule for a compile that fits only on its own; first fit with the limit on passing that prevents starvation; duplicate submissions; cancellation of orphaned and of queued jobs; live reload of settings with the last valid configuration kept; the machine gate; the required estimate; the exit rule; the relay of output, exit code and measurements by the client; `wait` with a timeout; the lock between two brokers; a broker killed in the middle of a compile, with the compile's output and exit code surviving; the return to the queue of a job whose Lean had not started; and the runner's starting, adopting and restarting of the broker.

These tests have been run on Linux and on Windows 11. The Windows code paths, which enumerate processes through a Toolhelp snapshot, read private memory with `GetProcessMemoryInfo`, and set priority classes, follow the documented API and the patterns already used in [runner.py](runner.py), and the Windows run exercised them under the stand-in. No real Lean was run: what this document says about Lean's memory, about `--threads`, and about the cost of particular tactics is Lean 4 and Mathlib behaviour as documented, not a measurement from this machine. The calibration table exists precisely so that each instance measures its own numbers, and the table of memory allowances above is there to orient a first estimate until the calibration table can replace it.
