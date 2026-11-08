---
name: do-math
description: Starts and operates autonomous mathematical research across attempt, explore, formalizer, peer, review and organizer sessions. Prepares a fresh instance, launches its detached runner, reads published results, and handles status, input, stopping and recovery.
---

# Using do-math

When a user entrusts a mathematical proposition to do-math, your work is to prepare the research instance and start the program that will carry it forward. You are the **operator**, the conversational agent handling that request. You establish the user's question and conditions, configure the available environment, and confirm that the run has started. The research can then continue after this conversation ends.

An **instance** is one research run, stored in a directory with its own Git repository. Its fixed starting proposition is the **root**. The research represents that proposition and further propositions worth settling as **nodes**, each with an exact mathematical statement. Review admits a new node only when an established mathematical connection relates it to the existing nodes. A proof that Q implies P, for example, can establish a reason to pursue Q while Q itself remains unresolved. Settling a node means proving its statement or its negation; the final root solution also requires independently reviewed Lean evidence.

The program that manages the instance is the **runner**. It launches fresh AI conversations called sessions. An **attempt** session reads the current research and chooses a node to try to settle. An **explore** session investigates the objects and their relationships to develop understanding; it occupies a **question**, an object of understanding that the research keeps beside its nodes, and question 0 is the root problem itself. A **formalizer** works from an accepted informal solution to construct a Lean proof. These roles leave retained mathematical work for other sessions to build on.

That work becomes shared knowledge through a **peer**, which studies one producing session's complete retained work and develops a record candidate, followed by **review**, which independently assesses the candidate and its originals. An **organizer** groups published records, maintains shared terminology and reconciles duplicate questions. The runner connects these responsibilities and preserves their outputs. The six workers receive guides suited to their roles; this entry point explains your preparation and operating responsibilities.

## Establish the question and prepare the instance

Recover the user's mathematical statement, assumptions and intended objects from the conversation and supplied material. Write an exact root statement with the relevant domains, quantifiers and boundary conventions. This statement stays fixed throughout the instance. A changed mathematical proposition requires a new instance. Ask only when an ambiguity changes the question or a permission belongs to the user; choose ordinary implementation details yourself.

Use the folder containing this skill as the installation path. The runner is `runtime/runner.py` in that folder. Read [Operations](reference/operations.md) for the preparation, settings and launch contract. Confirm Python 3.12 or later, Git, the actual native CLI paths and existing authentication, and the Lean environment the problem needs. Use available installations and tools. Passing a settings check establishes the format, not login or model access.

Prepare a UTF-8 root file outside the new instance directory. Put standing instructions in a separate input file when needed, including the language of records and explicit constraints on methods or resources. New standing inputs apply only to sessions launched afterward. The operator should therefore submit initial conditions before starting the runner. Mathematical suggestions remain information for the researchers' judgment.

Prepare `settings.json` using the format in Operations, which also states the default concurrency, attempt spacing, exploration and organization cadences, and each role's ordered models, including why peer and review prefer a different model from the producing roles. Use configured alternatives automatically. Lean compilation has a separate broker budget; configure shares explicitly when the machine hosts several instances.

The default formal-proof axiom list is `propext`, `Classical.choice` and `Quot.sound`. `sorryAx` is never allowed. A formal result also requires independent compilation and correspondence with the exact node. If a needed environment is unavailable, explain the concrete limitation and prepare the necessary supported environment; do not silently lower the assurance required for completion.

Worker sessions inherit no personal/project instructions, hooks or memories. Their guides, references and standing inputs are supplied by do-math and saved at launch. All worker models explicitly request 1M context and a 900,000-token compaction setting; Operations explains the provider-specific launch settings and actual-capacity limits. Existing CLI authentication and explicitly configured external tools are separate. Configure capabilities such as scholarly-mcp in `mcp_servers` when useful, rather than relying on the operator's personal settings to appear in workers.

Choose an instance path that does not exist. Put it outside the development repository or under an ignored directory such as `.skill-workspace/`, and confirm that its Git repository will remain separate from the parent. Create it with `init --root <file> --settings <file>`, submit any initial conditions with `input --file <file>`, then use `start`. A failed initialization can leave a partial folder; fix the problem and use a new path.

## Confirm launch and hand the run over

`start` creates a detached runner with new log paths and a launch token, and returns the runner's PID and those log paths once the runner's own start record has matched the token. Confirm current liveness with `status`; the start record itself is in the returned stdout log. If launch confirmation times out, inspect those logs and process state before trying again; the timeout alone does not show that the runner died.

Tell the user the absolute instance path, runner PID, new log paths, current running or waiting state, and `knowledge/index.md`, where the results can be found. Then end the operator conversation. The runner carries the work forward without keeping this conversation open.

The runner sends retained research from attempts, explorations and formalizers through peer and review. Each session runs under a **session host**, the process through which the runner launched its CLI; the host stays alive for the whole session, across the CLI turns, and survives a runner restart. Before closing an attempt that undertook research, an explorer, a formalizer or a peer, its host resumes the same conversation with common and role-specific continuation guidance, up to `max_end_resumptions` additional turns (default 3). A valid worker end decision or reaching that limit authorizes the handoff; the recorded issuer distinguishes the two. An attempt that only checked availability, or an explorer that found no free question to occupy, can report `no_research` and end without those stages. The runner retains its files and conversation. Useful imperfect records publish with feedback, and reviewed informal solutions can be used within their supported scope while formalization continues. The runner stops launching attempts and explorations when the root has an accepted formal solution, and continues remaining sessions and eligible follow-ups until finished. Existing sessions retain their normal scope.

## Read results in their mathematical scope

Begin at `knowledge/index.md`, then open the relevant records and their reviews. The index contains shared-context records, a directory of organizer-described modules, and new records awaiting organization. A record can appear in several modules. Its description remains unchanged, with review's short assessment and later findings alongside it.

Use `knowledge/frontier.md` to locate precise node statements, current solutions, reviewed connections and concerns, and the questions the research is trying to understand, with their resolutions where review has accepted one. Use the full `knowledge/glossary.md` to recover shared definitions and aliases, then follow local definitions and arguments in the records. A published folder, a supported finite computation and a formally solved root have different meanings. Report the claim actually established, its scope and the independent evidence that supports it.

When reporting completion, distinguish formal settlement of the root from the runner finishing its remaining work. A proof of the negation is a refutation of the original proposition and can settle the research. Preserve that direction in the explanation.

## Operate and recover

Use the commands in [Operations](reference/operations.md). `status` is read-only. `stop` blocks new dispatch while active CLI turns finish; reconsideration turns and queued follow-ups wait. `resume` removes that stop and requires `start` as well if the runner is no longer alive. `input` preserves new standing information for future sessions. `review` requests independent examination of existing evidence, and `organize` requests a repository organization pass.

A provider or model refusal causes a scoped wait and permits configured fallback for later launches. A producing session interrupted after doing work ends and its retained material goes to peer. Partial peer, review or organizer processing is supplied to a replacement session. Read the actual block or error in status before diagnosing a failure as mathematical.

After a crash or reboot, restart the same instance with `start`. Existing processes and unfinished publication are recovered from their saved identities and receipts. Use `kill-session` only for the actual session the user intends to terminate, after checking its role and identity in status. Use shells at the same privilege level on Windows. Preserve the runner state and published evidence; deleting internal files is not a recovery procedure.

This runtime targets fresh instances. Its interface and record formats are defined by the guides under `roles/` and `reference/`, and the implementation under `runtime/`.
