"""Fixes from 독해7_흐름 (reader items) applied to README (and copies), the two docs and the Zenodo description."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

readme = [
 # 2
 ("| Formal proof | None of the root. The user paused formalization on 9 November 2026. One necessary condition of the root has a Lean proof. |",
  "| Formal proof | No Lean proof of the root exists; the user paused formalization on 9 November 2026. One necessary condition of the root has a Lean proof. |"),
 # 4
 ("Several steps rest on computer-assisted inputs, some in binary64 with error models assumed in advance. |",
  "Several steps rest on computer-assisted inputs, some in binary64 floating point with error margins assumed rather than tracked. |"),
 # 5, U3
 ("An AI conversation called the operator prepares the statement and the settings and operates the run on the user's behalf, and a program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on.",
  "An AI conversation called the operator sets up the instance from the user's statement and settings and operates the run on the user's behalf, and a program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on."),
 # 7
 ("and decides what the record should propose to the research, such as new statements to pursue.",
  "and decides what the record should propose for the frontier, such as new statements to pursue."),
 # 10
 ("No session hands out work to another: a session in the first stage reads the knowledge base and decides for itself what to work on.",
  "No session assigns work to another. A session in the first stage reads the knowledge base and decides for itself what to work on; the one exception is formalization, which the runner requests once a review has accepted an informal proof."),
 # 11
 ("The first full run of this implementation began on 5 November 2026.", "The first research run of this implementation began on 5 November 2026."),
 # 13 route as chain (lead)
 ("along two routes leading from statements already proved to the conjecture itself, every record and every reviewed implication had been accepted by an AI review session.",
  "along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session."),
 # 14, 15, 16
 ("A node is an exact mathematical statement, with its objects, assumptions, domains and quantifiers all fixed, that the research is trying to settle.",
  "A node is an exact mathematical statement that the research is trying to settle, with its objects, assumptions, domains and quantifiers all fixed."),
 ("A node is **settled** once either it or its negation has been proved. Proofs come at two levels of assurance, informal and formal, which the section \"What counts as established\" defines, and the run as a whole is finished only when the root has been settled at the formal level.",
  "A node is **settled** once either it or its negation has been proved, at either of two levels of assurance, informal and formal, which the section \"What counts as established\" defines. The run as a whole is finished only when the root has been settled at the formal level."),
 ("A new node always enters through a **relation**,", "Every node other than the root enters through a **relation**,"),
 # 17
 ("| organizer | The published records not yet organized | Modules, shared-context selection, glossary decisions, merges |",
  "| organizer | The published records not yet organized | Modules of records, the choice of shared context, glossary decisions, merges |"),
 # 18
 ("Sessions coordinate through information rather than enforcement. The board shows which sections are occupied, the guide that each role receives, its **role guide**, explains how to respect that, and the sessions are trusted to follow the guide.",
  "Sessions coordinate through information rather than enforcement. The board shows which sections are occupied; the guide that each role receives, called its **role guide**, explains how to respect that; and the sessions are trusted to follow the guide."),
 # 19 (and U13)
 ("and the section counts as occupied until a peer and a review have processed the work.",
  "and the section counts as occupied until the record is published or the review decides there is nothing to publish."),
 # 20, 21, 80
 ("An attempt has no time cap, and the runner does not close it the moment its conversation stops. A separate process called the **session host**, started with the session and alive for as long as the session is, resumes the same conversation and asks the session to reconsider ending under its role guide, up to three times by default. Each time, the session either continues or submits an explicit decision that its work is complete or that it sees no way forward.",
  "An attempt has no time cap, and the runner does not close it the moment its CLI process exits. A separate process called the **session host**, started with the session and alive for as long as the session is, resumes the same conversation and asks the session, under its role guide, to reconsider whether to end, up to three times by default. Each time, the session either continues or submits an explicit decision that its work is complete or that it sees no way forward; once the limit is reached, the runner itself authorizes the end. The same reconsideration applies to explorers that have begun research, to formalizers and to peers."),
 # 12 accepted
 ("Separately, the review decides whether the record has enough useful content to be published at all.",
  "Separately, the review decides whether the record has enough useful content to be published at all, and which of the record's proposals it accepts: a proposed node, relation or proof is accepted only when the claim it rests on is supported, and only accepted proposals change the frontier."),
 # 13 route definition, 22
 ("The frontier also marks how each node stands to the root. A node is on a **route** to the root when a chain of relations lets a proof of the node contribute to settling the root; it is a necessary condition of the root when only its refutation can contribute. Formalization is requested only for outcomes that can reach the root in this sense.",
  "The frontier also marks how each node stands to the root. A node is on a **route** to the root when a chain of relations lets a proof of the node contribute to settling the root, and such a chain is itself called a route; a node is a necessary condition of the root when only its refutation can contribute. Formalization is requested only for the proof of a node on a route or for the refutation of a necessary condition."),
 # 23
 ("The role guides measure progress by the change a piece of work makes to what is known: it closes something, it lets the research see something it could not see before, it changes how the problem is approached, and the like. Extending the range over which a statement has been checked, without any such change, does not count as progress.",
  "The role guides measure progress by the change a piece of work makes to what is known. Work may close something, let the research see something it could not see before, or change how the problem is approached; the guides give these as examples rather than as a complete list. Extending the range over which a statement has been checked, without any such change, does not count as progress."),
 # 24
 ("The other describes the writing the author prefers, with the scenes in which those preferences became clear. Both are offered as understanding rather than as rules, and both are files in the skill's reference folder that a user can edit.",
  "The other describes the writing the author prefers, with the occasions on which those preferences became clear. Both are meant to inform the sessions' judgment rather than to be followed as rules, and both are files in the skill's reference folder that a user can edit."),
 # 26, 27
 ("All Lean compilation goes through one **Lean broker** per instance, a separate process that admits compiles within a limit on the total memory and threads they may use at once, and that keeps each compile's result so that a session can collect it even after its shell command has stopped waiting. Sessions inherit none of the user's personal instructions, hooks or memories; everything they read is supplied by do-math and saved in the session's directory at launch.",
  "All Lean compilation goes through one **Lean broker** per instance. The broker is a separate process that admits compile jobs within a limit on the total memory and threads they may use at once, and it keeps each job's result, so that a session can collect it even after the shell command that submitted it has stopped waiting. Sessions inherit none of the user's personal instructions, hooks or memories; their starting context is supplied by do-math and saved in the session's directory at launch."),
 # 28
 ("a claim that states a conjecture together with its grounds can be supported as that statement while the conjectured proposition remains unproved.",
  "a claim of the form \"we conjecture X, on these grounds\" can be supported as a claim about the grounds while X itself remains unproved."),
 # 29
 ("The records distinguish two kinds of arithmetic. Exact integer arithmetic, interval arithmetic and floating point with directed rounding control their own rounding. Binary64 floating point with an error model assumed in advance does not: margins added to the results are trusted to cover the rounding error rather than tracked by the arithmetic.",
  "The records distinguish two kinds of arithmetic. In the first kind, which includes exact integer arithmetic, interval arithmetic and floating point with directed rounding used to compute bounds, every result comes with a guaranteed range. In the second kind, binary64 floating point with an error model assumed in advance, margins added to the results are trusted to cover the rounding error rather than tracked by the arithmetic."),
 # 30
 ("| Anything beyond the range the computation covers; for a binary64 step, proof independent of the assumed error model |",
  "| Validity beyond the range the computation covers; for a binary64 step, validity independent of the assumed error model |"),
 # 31
 ("A pending concern changes nothing by itself: the claim and everything derived from it keep their standing, marked as resting on a questioned claim, until",
  "A pending concern does not change any claim's standing: the claim and everything derived from it keep their standing, but are marked as resting on a questioned claim, until"),
 # 32, 34
 ("The root of the run asks whether, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: non-decreasing up to some index and non-increasing after it, with a flat peak allowed.",
  "The root of the run is the statement that, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: non-decreasing up to some index and non-increasing after it, with a flat peak allowed."),
 ("Both routes pass through one statement, that the sequence increases below the middle, and this statement was the last part to close.",
  "Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to close."),
 # 79
 ("and a certification in integer interval arithmetic that the root holds for all n ≤ 20000.",
  "and a certification that the root holds for all n ≤ 20000, carried out in interval arithmetic with integer endpoints and, for the steps below the middle, also in floating point with directed rounding."),
 # 36
 ("was compressed on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records;",
  "was taken on 12 November at 01:52 Korean time, after the root had been informally proved, and holds 300 records;"),
 # 35
 ("To check the result, open `index.md`, go to `frontier.md`",
  "Records are cited here by the first eight characters of their identifiers; the directories in the knowledge base carry the full identifier. To check the result, open `index.md`, go to `frontier.md`"),
 # 37
 ("and ten pipelines were still working on nodes and questions beside the root.", "and ten pipelines were still working on nodes and questions other than the root."),
 # 6
 ("To launch by hand instead, write a UTF-8 `root.md`", "To set up an instance by hand instead, write a UTF-8 `root.md`"),
 # 38
 ("This keeps the default models, which put Codex first and Claude second for every role and the reverse for peer and review; with only Claude Code installed, give the `models` list and the `roles` entries for peer and review Claude models only, as the running guide shows.",
  "This keeps the default models: Codex first and Claude second for every role except peer and review, and the reverse for those two. With only Claude Code installed, list Claude models only, both in the `models` list and in the `roles` entries for peer and review, as the running guide shows."),
]
for f in ["README.md", "임시/작문/readme-20261112/README.md", "임시/작문/readme-20261112/stage3/README.md"]:
    apply(f, readme)

doc = [
 # 35 identifiers, header
 ("and the README's section \"Reading a published knowledge base\" explains the files of the published evidence.",
  "and the README's section \"Reading a published knowledge base\" explains the files of the published evidence. Records are cited by the first eight characters of their identifiers; the directories in the knowledge base carry the full identifier."),
 # 32
 ("Write b(n, ℓ) for the number of parking functions of length n with M(α) = ℓ. The root asks whether, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: whether there is an index c such that",
  "Write b(n, ℓ) for the number of parking functions of length n with M(α) = ℓ. The root states that, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: that there is an index c such that"),
 # 45
 ("and the default described in the README, under which the assessing roles prefer a different model, was adopted at the same time.",
  "and the default described in the README, under which peer and review prefer a different model from the producing roles, was adopted at the same time."),
 ("or on how often a fallback gave an assessing role the same model as the producers.",
  "or on how often a fallback gave a peer or a review the same model as the producers."),
 # 46
 ("In the first case the descent is at the step m−1 into the middle and the ascent at or beyond m;",
  "In the first case the descent is at the step from m−1 to m and the ascent at or beyond m;"),
 # 34
 ("by showing that the sequence has no descent at all below the middle, that is, that it increases there. Both routes therefore pass through that increase, and it was the last part to close.",
  "by showing that the sequence has no descent at all below the middle, that is, that it never decreases there. Both routes therefore pass through that statement, and it was the last part to close."),
 # 61
 ("and that the difference deciding the inequality is smaller than either count by a factor of order ℓ^(−1/3).",
  "and that their difference b(n, ℓ) − b(n, ℓ−1), whose sign decides the inequality, is smaller than either count by a factor of order ℓ^(−1/3)."),
 # 52
 ("and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November), which checked the steps at or beyond the middle in integer interval arithmetic and the steps below the middle twice, in integer interval arithmetic and in floating point with directed rounding. With that node proved,",
  "and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November). That certification checked the steps at or beyond the middle in interval arithmetic with integer endpoints, and the steps below the middle twice, once in the same arithmetic and once in floating point with directed rounding. With that node proved,"),
 # 48, 49
 ("With F_ℓ(z) = Σ_m A(m, ℓ) zᵐ / m! the exponential generating function of the numbers A(m, ℓ) of parking functions of length m with maximum displacement at most ℓ, the theorem states that",
  "Let A(j, ℓ) be the number of parking functions of length j with maximum displacement at most ℓ, and let F_ℓ(z) = Σ_j A(j, ℓ) zʲ / j! be the exponential generating function of these numbers. The theorem states that"),
 # 53
 ("was added to the runner afterwards, with this node as the occasion.", "was added to the runner afterwards, prompted by this node."),
 # 64 row
 ("| 9 November | Standing input | Formalization paused so that the research could finish first |",
  "| 9 November | Standing input and runner control | Formalization paused so that the research could finish first: a control file stops the runner from starting formalizers, and a standing input told the sessions |"),
 # 56
 ("Material from a session outside the instance, relayed as unverified matter for the sessions' own judgment",
  "Material from a session outside the instance, passed on as unverified material for the sessions to judge for themselves"),
 # 36, 59
 ("was compressed on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two inputs of that day;",
  "was taken on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two standing inputs of that day (04:54 and 14:15);"),
]
apply("docs/do-math/first-run-parking-unimodality.md", doc)

run = [
 # 71
 ("The runtime needs Lean 4 in every case, because the settings name a Lean installation and the broker starts with the runner;",
  "The runtime needs Lean 4 in every case, even for a problem whose proofs will not use it, because the settings name a Lean installation and the broker starts with the runner;"),
 # 65
 ("an explorer requested each time an attempt is launched (`explore_every`; the request is granted when a question is free and the interval has passed),",
  "an exploration request raised by the runner each time an attempt is launched (`explore_every`; the request is granted when a question is free, that is, open and held by no session, and the interval has passed),"),
 # 38
 ("With only Claude Code installed, give the common list and the two role entries Claude models only, as here with the Opus alias the Claude CLI resolves:",
  "With only Claude Code installed, list Claude models only, both in the common list and in the two role entries, as here with the Opus alias the Claude CLI resolves:"),
 # 62
 ("which is why compiles go through the broker. All sessions request a one-million-token context",
  "which is why compiles go through the broker.\n\nAll sessions request a one-million-token context"),
 # 63
 ("They apply only to sessions launched after them and accumulate; a later input that changes an earlier one must say which it changes. Changing the root's statement requires a new instance.",
  "They apply only to sessions launched after them and accumulate; a later input that changes an earlier one must say which it changes. The runner delivers the files in the instance's `control/inputs` directory to each new session, so an input is withdrawn by moving its file out of that directory, for example into `control/retired-inputs`; there is no command for this. Changing the root's statement requires a new instance."),
 # 67
 ("If the runner process has ended in the meantime, run `resume` and then `start`. |",
  "The stop is recorded in the instance, so if the runner process has ended in the meantime, run `resume` to clear it and then `start`. |"),
 # 66
 ("| `reconsider-attempts` | Launch one attempt to look again for available work after attempts have reported, in a state that `status` shows under `attempt_dispatch`, that every unresolved node is occupied; that report otherwise pauses attempt launches. |",
  "| `reconsider-attempts` | Launch one attempt to look again for available work. Use it after attempts have reported that every unresolved node is occupied, a state that `status` shows under `attempt_dispatch`; that report otherwise pauses attempt launches. |"),
 # 72
 ("Retained research is still processed once launching is allowed. |", "Retained research is still processed once launching is resumed. |"),
 # 68
 ("| `restart-broker` | Replace the Lean broker after an environment change, with launching stopped. |",
  "| `restart-broker` | Replace the Lean broker after an environment change. Stop launching first and let running CLI turns and compiles finish. |"),
 # 69, 15
 ("To end a run before the root is settled, take three steps in order. First run `stop`,", "To end a run before the root is formally settled, take three steps in order. First, run `stop`,"),
 # 70
 ("Formal settlement of the root stops new attempts and explorers; existing sessions finish, their peers and reviews, formalizations and organizations still launch as their inputs become ready, and the runner finishes when that work has ended.",
  "Formal settlement of the root stops new attempts and explorers. Existing sessions finish; their peers and reviews, and any formalizations and organizations, still launch as their inputs become ready; and the runner finishes when that work has ended."),
]
apply("docs/do-math/running.md", run)

zen = [
 # 73
 ("the records that a run of autonomous mathematical research published, together with the views derived from them.",
  "the records that a run of autonomous mathematical research published, together with the index, frontier and glossary derived from them."),
 # 13 lead
 ("it means that every record and every reviewed implication on two routes from proved statements to the conjecture had been accepted by an AI review session.",
  "it means that along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session."),
 # 36, 78
 ("This version of the archive was compressed on 12 November 2026 at [compression time] Korean time and deposited at [deposit time]; it holds [record count] records.",
  "This version of the archive was taken on 12 November 2026 at [compression time] Korean time and deposited at [deposit time]; it holds [record count] records."),
 # 75
 ("Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, and the reviews name them.",
  "Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, in which the rounding error is covered by assumed margins rather than tracked by the arithmetic; the reviews name these steps, and a reader who does not accept such a model should treat what depends on it as unproved."),
 # 74
 ("`frontier.md` gives every node's exact statement, its state, the proofs behind that state and the accepted relations between nodes; the root is listed first with its two routes.",
  "`frontier.md` lists the nodes, the exact statements the research tracked, with the conjecture first among them; for each it gives the statement, its state, the proofs behind that state and the accepted implications between nodes, and for the conjecture the two chains of implications, called routes, that lead to it."),
 ("The record that proved the last open premise on the routes to the conjecture is", "The record that proved the last open statement on those routes is"),
 # 76
 ("The standing inputs the user supplied to the run and the sessions' own conversations are not part of `knowledge/`; the repository's README and its first-run document summarize the inputs.",
  "The standing inputs, the instructions that the user gave to the sessions during the run, and the sessions' own conversations are not part of `knowledge/`; the repository's first-run document lists the inputs."),
]
apply("임시/작문/readme-20261112/stage3/zenodo-description.md", zen)
print("reader fixes applied")
