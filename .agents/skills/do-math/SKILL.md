---
name: do-math
description: Starts and operates autonomous mathematical research whose knowledge is a Lean library built by attempt, explore, formalizer, peer, review and organizer sessions. Fixes the proposition in words and in Lean with the user, prepares a fresh instance, launches its detached runner, reads the results from the library, and handles status, input, stopping and recovery. Also draws the dependency map of a research, has its paper written once the root is formally settled, and turns a research whose root is formally proved into a package for publication.
---

# Using do-math

When a user entrusts a mathematical proposition to do-math, your work is to fix that proposition with the user, in words and in Lean, to prepare the research instance, and to start the program that will carry the research forward. You are the **operator**, the conversational agent handling that request. You establish the user's proposition and conditions, configure the available environment, and confirm that the run has started. The research can then continue after this conversation ends.

An **instance** is one research run, stored in a directory with its own Git repository. Its fixed starting proposition is the **root**. The knowledge of an instance is its **canon**: one Lean library with a written record beside each declaration. Every mathematical assertion the research keeps is an **element**, which is a declaration of that library whose statement Lean has compiled, together with its **record**. The record holds what cannot be in Lean: a self-description of a line or two, the statement in natural language, the explanation, and a proof in words where there is one. A definition is an element. So is a statement, whether or not it has a proof yet. A proof is either complete in Lean, or written in the record while its Lean proof names the elements it rests on and ends in `sorry`; Lean checks those names in both cases. Beyond the elements, a proof uses the imported library, such as Mathlib, and nothing else. The root is the first statement of the library, and it is fixed in Lean when the instance is created.

Review judges each proof twice: whether it is correct, and, of a correct proof, whether it is accepted. A statement therefore has one of four standings: no proof; proof not confirmed; correct, held back; accepted. A correct proof is held back when it can still clearly be made simpler or when it closes part of the statement by large computation done without understanding; such a proof is published and can be used, and the statement stays among the work that remains. A statement is **settled** when one of its proofs is accepted and every statement that proof names is settled. An element is **formal** when its proof is complete in Lean and depends, through everything it uses, only on the allowed axioms; [Operations](reference/operations.md) says, under "What makes a statement formal", how Lean establishes both. The **frontier** is the view derived from the root downward along what each proof names, opening every statement that is not settled. Nobody writes it, and the work that remains is every statement it shows whose standing is not "accepted", a statement without any proof included.

The program that manages the instance is the **runner**. It launches fresh AI conversations called sessions. An **attempt** session reads the frontier and chooses work that remains: an element, an exact part of what an element asserts, or a statement it formulates itself. An **explore** session investigates the objects and their relationships to develop understanding; it occupies a **question**, something the research wants to understand, whether or not it can be put as a statement, and question `q0` is the root problem as a whole. A **formalizer** receives a settled statement that the root rests on and writes the Lean proof that its written proof still lacks. These three roles do mathematics, state what they find in Lean, and leave their work for others to build on.

That work enters the canon through a **peer**, which takes one producing session's work over, continues it and writes the candidate, the change to the canon: new elements, replaced proofs, records, the approaches tried on a statement, and the understanding so far of a question. **Review** then has three independent sub-reviewers examine the candidate and its originals, compiles it itself, and judges each element; a review session that runs on the Codex CLI cannot delegate and makes the three examinations itself, as separate passes. An **organizer** joins what is the same by proving in Lean that two definitions or two statements agree, rearranges modules, and merges questions that ask the same thing. The runner connects these responsibilities and publishes their outputs. The six workers receive guides suited to their roles; yours is this entry point, and [Operations](reference/operations.md), which you open when you prepare an instance or act on a run, gives the particulars of each step.

Review judges and does not gate: useful imperfect work is published with review's judgments, an element whose proof was not confirmed enters the canon in that state with review's reason, and a later session does the repair. A **concern** is a reported challenge to an element's proof. A pending concern does not change the standing of that proof; only a review finding can withdraw its confirmation. A **comprehensive review** is an assignment of the review role to examine questioned proofs and their actual uses in later proofs. A concern, an operator `review --element` request or a **contested** statement, one for which both it and its negation carry settled proofs, triggers it; it is not a routine stage for each new candidate.

Each session runs under a **session host**, the process through which the runner launched its CLI; the host stays alive for the whole session, across the CLI turns, and survives a runner restart. Before a session is closed, the host can resume the same conversation, at most `max_end_resumptions` times (default 3).

All Lean compilation in an instance goes through that instance's own compilation service, the **Lean broker**, which schedules compiles under its own memory and thread budgets.

## Fix the proposition in words and in Lean

Recover the user's mathematical statement, assumptions and intended objects from the conversation and supplied material. Write an exact root statement in words, with the relevant domains, quantifiers and boundary conventions. Ask only when an ambiguity changes the proposition or a permission belongs to the user; choose ordinary implementation details yourself.

Then write the same proposition in Lean, together with the user: the Lean definitions of the objects the proposition speaks of, and the Lean statement of the root as a theorem whose proof is left open. [Operations](reference/operations.md) gives this work step by step under "Fix the root in words and in Lean".

When `init` has succeeded, have the user read and confirm what was fixed, with your explanation of how the Lean form reads; Operations lists, under "Compile, and have the user confirm", exactly what the user reads. Start the runner only after that confirmation.

A changed mathematical proposition requires a new instance, and a Lean statement later found not to say what was meant is a changed proposition.

## Prepare the environment and the settings

Use the folder containing this skill as the installation path. The runner is `runtime/runner.py` in that folder.

Everything inside an instance is written in English, whatever language the user speaks to you in. [Operations](reference/operations.md) describes, under "Convey the user's conditions", the input file for standing instructions and how to carry the user's words into an input.

Confirm what the runner needs on the machine and prepare `settings.json` as [Operations](reference/operations.md) describes under "Prepare the settings and environment".

When the machine hosts several instances, configure each instance's share of memory explicitly, as [The Lean broker](reference/lean-broker.md) says under "Settings". Operations says, under "When compiles wait for memory on Windows", what to recommend to the user when compiles wait there while physical memory is free.

The default allowed axioms are `propext`, `Classical.choice` and `Quot.sound`. `sorryAx` is never allowed. If a needed environment is unavailable, explain the concrete limitation and prepare the necessary supported environment; do not silently lower the assurance required for completion.

[Operations](reference/operations.md) describes, under "External tools", what a worker session inherits and which external tools it has, with the check that the literature server scholarly-mcp answers, which you make before launch, and gives, under "Context, continuation and acceptance settings", the context window and launch settings that every worker requests.

## Create, confirm, start and hand the run over

[Operations](reference/operations.md) gives, under "Create and start", the commands that create the instance on a path that does not exist, submit any initial conditions, start the runner and confirm that it is alive, and what to tell the user before you end the operator conversation.

[Operations](reference/operations.md) describes, under "Attempts that find no work", the attempts and explorers that end without peer or review because they found no work to take on, under "Session hosts and continuation turns" the resumptions of a session by its host, and under "Context, continuation and acceptance settings" the setting `max_end_resumptions`.

## Read results in their mathematical scope

The results are the elements of the canon. [Operations](reference/operations.md) describes under "Read progress and results" how to read them, beginning at `knowledge/frontier.md`.

Report what is actually established, in its scope. A published element, a statement whose proof is correct and held back, a settled statement and a formally settled root mean different things. So do the two forms of a proof: the correctness of a proof written in a record is judged by review alone, while a proof complete in Lean has been checked by Lean, and judged by review as well unless it is one of the two kinds of proof that [Operations](reference/operations.md) describes, under "What makes a statement formal", as standing without a review. Say which of these holds, for which exact statement, and name the elements you read.

When reporting completion, distinguish formal settlement of the root from the runner finishing its remaining work. [Operations](reference/operations.md) says under "Read progress and results", where it describes `status`, what the runner stops and what it still does once the root is formally settled. A formal proof of the negation is a refutation of the original proposition and settles the research in the same way. Preserve that direction in the explanation. Report with the settlement the result that `status` gives under `root_check`; Operations describes the comparison behind it, and what makes a statement formal, under "What makes a statement formal".

Two commands produce the dependency map and the paper from the canon; Operations describes them under "The dependency map and the paper", including the paper method that the user reads and confirms before the first paper is produced.

Once the root is formally proved, one further command, `runtime/finalize.py`, turns the finished instance into a package for publication. [Operations](reference/operations.md) describes it under "Finalizing a finished research". Before the first start, ask the user for the author fields and the human review that its configuration records.

## Convey the user's conditions, and judge from the text

During a run the user may give you a condition for the research, and you deliver it with `input`. [Operations](reference/operations.md) explains, under "Convey the user's conditions", how to write an input so that the sessions receive what the user said and nothing that you added. You can also place questions of your own for explorers to take up, with `questions`; Operations gives, under "Place questions on the frontier", the standard to write them to and the form of the file.

The user may also ask you what an element establishes, or whether a proof could be better. Answer by reading the element's record and its proof. If you count the elements a proof rests on, compare margins or sample values, you obtain numbers without having read what the proof argues, and reporting those numbers does not answer the user's question. The workers' [common introduction](reference/common.md) describes this under "Judging from the text itself", and it applies to you as it does to them. Say which texts you read and which you did not, and give no judgment about a part you have not read.

## Operate and recover

[Operations](reference/operations.md) lists, under "Commands", each operating command and what it changes; `status` reports and changes nothing of the research.

Operations describes, under "Waiting, fallback and recovery", what the runner does after a provider or model refusal, after an interrupted session, and with a candidate that no longer applies to the canon or does not build on it. Read the actual block or error in status before diagnosing a failure as mathematical.

After a crash or reboot, restart the same instance with `start`; Operations explains, under "Restarts, runner failures and installation updates", how existing processes and unfinished publication are recovered and why shells on Windows need the same privilege level, and, under "Changing Lean", the procedure that a change of Lean or of its libraries requires. Use `kill-session` only for the actual session the user intends to terminate, after checking its role and identity in status. Preserve the runner state and the canon; deleting internal files is not a recovery procedure. Operations says, under "Retention and archives", what is kept of each session and how its archived work is restored.

This runtime's interface and formats are defined by the guides under `roles/` and `reference/`, and the implementation under `runtime/`.
