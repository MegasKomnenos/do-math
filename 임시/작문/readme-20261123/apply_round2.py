"""Second-round revision: exact replacements, each asserted to match exactly once."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]

README = [
(r'''| What it is | A system for autonomous mathematical research in which many AI sessions work together to prove or refute a single mathematical statement. Every result the research keeps is a declaration in one Lean 4 library, with a written record beside it. |''',
 r'''| What it is | A system in which many AI sessions research one mathematical statement on their own, working to prove it or to refute it. Every result they keep is written in Lean 4, a proof assistant, as part of one library, with a written record beside it. |'''),
(r'''| When a run is complete | Only when the statement or its negation has a proof that is complete in Lean, uses only the allowed axioms and has been accepted, together with a proof of everything it rests on. The statement is fixed in Lean before the research starts. |''',
 r'''| When a run is complete | Only when the statement or its negation has a proof that is complete in Lean and uses only the allowed axioms, and when that proof and a proof of every statement it rests on have been accepted, a term defined below. The statement is fixed in Lean before the research starts. |'''),
(r'''One small statement has been carried from start to finish by real AI sessions and the real Lean compiler; the tests replace both by stand-ins.''',
 r'''One small statement has been carried to a formal proof by real AI sessions and the real Lean compiler; the tests replace both by stand-ins.'''),
(r'''| Design and verification | [docs/do-math/lean-canon-design.md](docs/do-math/lean-canon-design.md) and [docs/do-math/lean-canon-verification.md](docs/do-math/lean-canon-verification.md) |''',
 r'''| Design and verification | [docs/do-math/lean-canon-design.md](docs/do-math/lean-canon-design.md), written before the implementation, and [docs/do-math/lean-canon-verification.md](docs/do-math/lean-canon-verification.md), which says what was run to check it and where the code departs from the design |'''),
(r'''and it starts without the conversations of the others.''',
 r'''and it begins with no memory of the other conversations.'''),
(r'''The user supplies the statement to be proved or refuted and, before the research starts, fixes it in two forms: in words, and as a Lean theorem whose proof is left open. The user may add standing inputs, which are instructions that reach every session launched after them. The user does not launch sessions by hand. An AI conversation called the operator sets up the run together with the user and operates it on the user's behalf. A program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on.''',
 r'''The user supplies the statement to be proved or refuted. Before the research starts the statement is fixed in two forms, in words and as a Lean theorem whose proof is left open; an AI conversation called the operator writes the Lean form together with the user, and the user confirms it. The user may add standing inputs, which are instructions that reach every session launched after them. The user does not launch sessions by hand. The operator sets up the run and operates it on the user's behalf, and a program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on.'''),
(r'''Finally, a third session, the review, has the candidate examined three times, independently, against the producing session's files, compiles the candidate itself, and then judges each element: whether its Lean statement says what its record says, whether its proof is correct, and whether a correct proof should also be accepted, a second judgment that is explained below.''',
 r'''Finally, a third session, the review, judges the candidate. Before it judges, it has the candidate examined three times, independently, against the producing session's files, and it compiles the candidate itself. It then judges each element on three points: whether its Lean statement says what its record says, whether its proof is correct, and whether a correct proof should also be accepted. The last of these is a second judgment, which is explained below.'''),
(r'''No session plans the work of another. A producing session reads the library and decides for itself what to work on, and the runner assigns work only where the state of the research calls for it, such as a peer and a review for the work that a producing session leaves.''',
 r'''No session plans the work of another. A session that sets out to prove something or to understand something reads the library and decides for itself what to work on. The runner assigns work only where the state of the research calls for it; for example, it assigns a peer and a review to the work that a producing session leaves, and it gives an accepted proof in words to a session that is to write its Lean proof.'''),
(r'''A candidate is judged by a session that took no part in producing it, and because the judgment travels with the work, useful work that is not yet perfect can still be published, and a later session can tell an established result from one that still needs work.''',
 r'''A candidate is judged by a session that took no part in producing it. Because the judgment travels with the work, useful work that is not yet perfect can still be published, and a later session can tell an established result from one that still needs work.'''),
(r'''A result stated in Lean has one name, a proof that uses it must cite that name, and Lean checks the citation.''',
 r'''A result stated in Lean has one name; a proof that uses it must cite that name, and Lean checks the citation.'''),
(r'''Lean then guarantees that the proof establishes the statement as it is written.''',
 r'''Lean has then checked that the proof establishes the statement as it is written.'''),
(r'''what each standing of a result does and does not certify''',
 r'''what a published result does and does not certify'''),
(r'''a directory for every session that has run, and two folders that the following paragraphs describe. `canon/` holds the mathematics of the run. `knowledge/` holds the views that the runner derives from `canon/`, together with the published judgments of the reviews.''',
 r'''a directory for every session that has run, and two folders: `canon/`, which holds the mathematics of the run, and `knowledge/`, which holds the views that the runner derives from `canon/` together with the published judgments of the reviews.'''),
(r'''A record also gives the element's **weight**, which is one of two. A **unit** is a result that someone describing how the proof goes would name. A **step** is a result that lives inside one proof and exists because that proof was written in pieces. The frontier, a view described below, shows units; where a proof rests on a step whose own proof is accepted, the frontier shows in its place what the step rests on, so that a reader sees the structure of the proof and not every lemma. A step remains an element, proofs name it, and the list of all elements includes it.''',
 r'''A record also gives the element's **weight**, and there are two weights. A **unit** is a result that someone describing how the proof goes would name. A **step** is a result that lives inside one proof and exists because that proof was written in pieces. The views described below use the weight to show the structure of a proof and not every lemma; a step remains an element, and proofs name it.'''),
(r'''where the two names after `:=` are other statements of the library and the argument itself is in the record:''',
 r'''where `oddSum_succ` and `square_succ` are other statements of the library and the argument itself is in the record:'''),
(r'''Whenever a publication changes the Lean files, the runner extracts again from the compiled library a **structural index**, the file `canon/index.json`: for each declaration, the text of its statement, what the statement and the proof use, whether the Lean proof is complete, and the axioms the proof depends on.''',
 r'''Whenever a publication changes the Lean files, the runner extracts the **structural index** again from the compiled library. The index is the file `canon/index.json`, and it gives for each declaration the text of its statement, what the statement and the proof use, whether the Lean proof is complete, and the axioms the proof depends on.'''),
(r'''The second judgment exists because a correct proof is not always one after which work on the statement should end; the reasons are given under "What counts as established". According to the proof a statement carries and those two judgments, every statement of the canon has one of four **standings**.''',
 r'''The second judgment exists because work on a statement should sometimes continue after a correct proof of it has been found; the reasons are given under "What counts as established". Every statement of the canon has one of four **standings**, which depends on the proof the statement carries and on those two judgments.'''),
(r'''The statements that have one of the first three standings are the **work that remains**. A statement can have more than one proof: a further proof is a further declaration with the same statement, and each has a standing of its own. A statement is **settled**''',
 r'''The statements that have one of the first three standings are the **work that remains**. A proof that no review has judged has a standing too: it counts as accepted when it is complete in Lean and came with the root or from an organizer, and as not confirmed otherwise. Strictly, a standing belongs to a proof, that is, to the declaration that carries it. A statement can have more than one proof, because a further proof is a further declaration that states the same thing, and each proof has a standing of its own. A statement is **settled**'''),
(r'''Being **formal** is a matter of Lean: a statement is formal when its Lean proof is complete and depends, through everything in the canon that it uses, only on the axioms the instance allows.''',
 r'''Being **formal** is a matter of Lean. A proof is formal when it is complete in Lean and depends, through everything in the canon that it uses, only on the axioms the instance allows, and a statement is formal when it has such a proof.'''),
(r'''leaves out those that are settled, and opens each unsettled statement in the same way. A line of the frontier''',
 r'''leaves out those that are settled, and opens each unsettled statement in the same way. The frontier shows units: where a proof rests on a step whose own proof is accepted, the frontier shows in the step's place what the step rests on. A line of the frontier'''),
(r'''a **formalizer** makes formal a proof that is settled and not yet formal, usually by completing in Lean a proof that was accepted in words.''',
 r'''a **formalizer** gives a formal proof to a statement that is settled and not yet formal, usually by completing in Lean a proof that was accepted in words.'''),
(r'''| formalizer | One settled statement that the root, or a settled refutation of the root, rests on, whose accepted proof is not yet formal and names only statements that already have formal proofs | A Lean proof of that statement, complete or partial |''',
 r'''| formalizer | One settled statement whose accepted proof is not yet formal and names only statements that already have formal proofs. It is a statement that the root rests on, or that a settled refutation of the root rests on | A Lean proof of that statement, complete or partial |'''),
(r'''A producing session changes nothing in the canon itself.''',
 r'''A producing session does not write to the canon, which changes only when the runner publishes a candidate.'''),
(r'''or when the limit is reached, in which case the end is authorized without a decision from the session. The same reconsideration applies to explorers, formalizers and peers.''',
 r'''or when the limit is reached, in which case the session host authorizes the end without a decision from the session. The same reconsideration applies to explorers, formalizers and peers. It does not apply to an attempt or an explorer that found no work to take on, a case described below.'''),
(r'''because each of them ends with a definite output: a review with its assessment, an organizer with its changes to the canon. Their host resumes the conversation for a different reason. When a turn of the conversation has ended and the output does not yet have the form the runner needs in order to carry it to the next stage, the host tells the session what is missing, up to the same number of times. A review's turn can end while the sub-agents it delegated to are still at work, and without the resumption the whole review would have to be made again by a new session.''',
 r'''because each of them ends with a definite output: a review with its assessment, an organizer with its account of what it joined, rearranged or merged. Their host resumes the conversation for a different reason. When a turn of the conversation, that is, one run of the session's CLI process, has ended and the output does not yet have the form the runner needs in order to carry it to the next stage, the host tells the session what is missing, up to the same number of times. A review on Claude Code delegates part of its work to sub-agents, as "Peer, review and publication" describes, and its turn can end while they are still at work. Without the resumption the whole review would have to be made again by a new session.'''),
(r'''It then repeats the checks that a program can decide: no statement changed in place''',
 r'''It then checks again what a program can decide by itself: no statement changed in place'''),
(r'''where the new statement gives the old one, the old element's proof becomes a one-line derivation from it.''',
 r'''where the old statement follows from the new one, the old element's proof becomes a one-line derivation from it, at once if the old statement was not settled and otherwise once the new statement is settled as well.'''),
(r'''A question has a statement of what is to be understood and the grounds on which it was asked. An explorer takes one question, and a question is with one explorer at a time, except that two explorers whose questions an organizer merges both keep the merged question; the explorer works on it with no predetermined theorem to produce.''',
 r'''A question consists of a text that says what is to be understood and of the grounds on which it was asked. An explorer takes one question and works on it with no predetermined theorem to produce. A question is with one explorer at a time, with one exception: when an organizer merges two questions that each have an explorer, both explorers keep the merged question.'''),
(r'''Each question carries its **understanding so far**, a text that says what is now understood of the matter the question asks about, and what is not. The mathematical assertions in it are elements, to which the text refers by name; the text itself explains, connects and interprets.''',
 r'''Each question carries a text called its **understanding so far**, which says what is now understood of the matter the question asks about, and what is not. The mathematical assertions in it are elements, to which the text refers by name; the text itself explains the elements, connects them and interprets them.'''),
(r'''A question is resolved when a review judges that its understanding so far answers what its statement asks; what the answer leaves to be done is carried on as exact statements or as a sharper question. `q0` is resolved only by the formal settlement of the root.''',
 r'''A question is resolved when a review judges that the text of its understanding so far answers what the question asks; what the answer leaves to be done is carried on as exact statements or as a sharper question. `q0` is resolved only when the root is formally settled.'''),
(r'''A statement whose proof is not accepted carries its **approaches tried**, one entry for each approach, saying what the idea was, what the approach established and where it stops, with the review's assessment of what that work contributed added beneath. This is kept by approach because sessions approach the same statement in the same ways and stop in the same places, so that what is learned about the course of the work does not grow with the number of sessions.''',
 r'''A statement whose proof is not accepted carries a list of the **approaches tried** on it, with one entry for each approach. An entry says what the idea was, what the approach established and where it stops, and the review's assessment of what that work contributed is added beneath it. The entries are kept one for each approach, and not one for each session, because sessions approach the same statement in the same ways and stop in the same places, so what is learned about the course of the work does not grow with the number of sessions.'''),
(r'''after reading, in order, the records that an earlier research run had left; its first part says what they saw in those records,''',
 r'''after reading, in order, what the sessions of an earlier research run had written; its first part says what they saw there,'''),
(r'''and it keeps compiled modules, so that a module whose source and imports are unchanged is not compiled twice.''',
 r'''and it keeps compiled modules, so that a module whose source and imports are unchanged is not compiled again unless a fresh compile is asked for, as a review's is.'''),
(r'''The first is that the proof can still clearly be made simpler: the review can point to a place in the proof and say how it could be simplified there. The reason is that the simpler proof is the more concise one, and the research should have it. The second is that the proof establishes part of its statement only by a large computation carried out without an understanding of why that part holds. The reason is that a statement with an accepted proof appears finished, and no session would then go on to explain why that part is true. In both cases the element is published and other proofs may use it, but the statement keeps the standing "correct, held back", stays among the work that remains, and settles nothing that rests on it.''',
 r'''The first is that the proof can still clearly be made simpler: the review can point to a place in the proof and say how it could be simplified there. Such a proof is held back because the research should have the simpler proof, which is the more concise one. The second is that the proof establishes part of its statement only by a large computation carried out without an understanding of why that part holds. Such a proof is held back because a statement with an accepted proof appears finished, and no session would then go on to explain why that part is true. In both cases the element is published and other proofs may use it, but the statement keeps the standing "correct, held back", stays among the work that remains, and nothing that rests on it is settled through it. This holds for the root as well: a proof of the root that is complete in Lean and held back leaves the run incomplete.'''),
(r'''by reading the candidate against the producing session's retained work after the three independent examinations;''',
 r'''by reading the candidate against the producing session's retained work after the three examinations described above;'''),
(r'''establishes its own statement under that open statement as a hypothesis.''',
 r'''establishes its own statement on the hypothesis that the open statement holds.'''),
(r'''a program called the **judge** checked the proof from outside the structural index: Lean's exporter writes the theorem out together with everything it rests on, and a second program works out the axioms again from that export alone and replays every declaration through Lean's kernel, the small program that checks every proof.''',
 r'''a program called the **judge** checked the proof without using the structural index. Lean's exporter writes the theorem out together with everything it rests on. A second program, the comparator, then works out the axioms again from that export alone and replays every declaration through Lean's kernel, the small program that checks every proof.'''),
(r'''The judge's verdict holds only if the library it was given was compiled honestly, because Lean code that a session wrote runs when the library is compiled. The comparing program can run inside a sandbox as a guard against this; that sandbox needs Linux and is switched off on Windows, where every run recorded so far was made.''',
 r'''The judge's verdict holds only if the library was compiled honestly, because Lean code that a session wrote runs when the library is compiled. The comparator has a sandbox in which it can build what it judges, but do-math gives it modules that its own broker has already compiled, so that sandbox does not cover those builds on any system, and on Windows, where it cannot run, it is switched off. What the verdict does not rest on is the structural index, the views, or anything a session reported.'''),
(r'''the user's confirmation is the only judgment of meaning that the root's Lean statement receives from the person whose statement it is.''',
 r'''the user is the person whose statement it is, and this confirmation is the only time the user judges what the root's Lean statement means.'''),
(r'''For every element that a candidate adds, the review judges whether the Lean statement says what its record says and whether a definition denotes the intended object. Two kinds of element''',
 r'''For every element that a candidate adds, the review judges whether the Lean statement says what its record says and whether a definition denotes the intended object. Where it finds that a Lean statement does not say what was meant, it cannot repair the statement, which never changes in place; it says in its reason what the Lean statement asserts and what was intended, so that the intended statement can enter under a new name. Two kinds of element'''),
(r'''A proof that settles part of its statement by a large computation without an account of why that part holds''',
 r'''A proof that establishes part of its statement by a large computation without an account of why that part holds'''),
(r'''A **concern** is a challenge to the proof of an element, reported by a review session in its assessment.''',
 r'''A **concern** is a challenge to the proof of an element, reported by a review session in its assessment or opened by the runner when a finding withdraws a confirmation without naming a concern.'''),
(r'''and the questions, each with its statement, its grounds, whether it is open or resolved, and its source.''',
 r'''and the questions, each with its text, its grounds, whether it is open or resolved, and its source.'''),
(r'''The instance is complete in the two formal states.''',
 r'''The instance is complete in the two formal states. These are the system's own names: *informally proved* means that AI reviews have accepted a proof of the root and of everything beneath it, and that Lean has not yet checked all of it.'''),
(r'''One draws a dependency map of what the root's proof rests on, at any time.''',
 r'''One can be run at any time and draws a dependency map of what the root's proof rests on.'''),
(r'''No run on a system other than Windows has been recorded. The runtime also has code for Linux, and macOS is not supported.''',
 r'''Every run whose operating system is recorded was made on Windows, with Lean 4.32.0 or 4.36.0. The runtime has code for Linux as well, which no recorded run has used, and macOS is not supported.'''),
(r'''Outbound traffic comes from the programs they start: the CLIs, the literature server, which queries public literature services, any further tool servers you configure, and, when you run the command that writes a paper and its example papers are not yet on the machine, a script that downloads their sources from arXiv.''',
 r'''Outbound traffic comes from the programs they start. These are the CLIs; the literature server, which queries public literature services; any further tool servers you configure; and a script that downloads the sources of example papers from arXiv, which runs when you run the command that writes a paper and those papers are not yet on the machine.'''),
(r'''Write a UTF-8 `root.md` with the statement in English, and a folder that holds''',
 r'''Write a UTF-8 `root.md` with the statement in English, and prepare a folder that holds'''),
(r'''as the running guide shows.

Then create the instance''',
 r'''as the running guide shows. The default settings also attach the literature server, and `init` refuses when that server's Python environment is not installed; the running guide gives the commands that install it, and `"mcp_servers": {}` in the settings file runs without it.

Then create the instance'''),
(r'''read what was fixed, as the running guide describes: this reading is the only check of what the Lean statement means.''',
 r'''read what was fixed, as the running guide describes: nothing after this reading judges what the Lean statement means.'''),
(r'''The checks made on the implementation that the earlier design document describes are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md).''',
 r'''The earlier design document describes an earlier implementation, and the checks made on that implementation are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md).'''),
(r'''and six sessions carried it to a formally proved root. All six used one Claude model''',
 r'''and the run's six sessions took it to a formally proved root. All six used one Claude model'''),
(r'''on the small library of the first of these runs,''',
 r'''on the small library of the run described in the first item,'''),
(r'''They do not show that the real compiler gives those outputs, a difference that has already hidden two defects, each of which came to light only with the real compiler, and they do not evaluate the mathematics that real sessions produce.''',
 r'''They do not show that the real compiler gives those outputs. That difference has already hidden two defects, each of which came to light only with the real compiler. Nor do the tests evaluate the mathematics that real sessions produce.'''),
(r'''### Results that rest on computation''',
 r'''### What a program checks and what is asked of a session

Some of the rules above are enforced by a program, and others are instructions that a session is trusted to follow. A program checks that the library compiles and that every name a proof uses exists and fits. It reads the axioms that each proof depends on, so whether a proof is formal does not depend on what a review reports. It refuses a publication that changes a statement in place, declares an axiom or leaves a declaration without a record, and it lets a candidate replace the proof of an unsettled statement only when its pipeline holds a section there. When a review confirms a proof that is complete in Lean, a program also checks that the compile the review names is the review's own fresh one.

No program checks that a review made its three examinations, that a session read what the canon already holds before it took on a statement, that a session respected another session's section in the mathematics it pursued, or that the user confirmed the root before the runner was started. Sessions also run with full access to files under the user's account, so it is their instructions, and no barrier, that keep them from writing outside their own directories.

### Results that rest on computation'''),
]

GUIDE = [
(r'''`init`, the command that creates an instance, compiles the Lean form of the root, so Lean has to be installed, and named in the settings unless `lean` is on your PATH, before the instance exists.''',
 r'''`init`, the command that creates an instance, compiles the Lean form of the root. Lean therefore has to be installed before the instance exists, and it has to be named in the settings unless `lean` is on your PATH. The runs recorded so far used Lean 4.32.0 and 4.36.0.'''),
(r'''and a settings file with `"mcp_servers": {}` creates an instance without external tools. Beyond the servers named in the instance's settings, the sessions have the CLIs' built-in tools, which include shell commands and web search.''',
 r'''and a settings file with `"mcp_servers": {}` creates an instance without external tools. The server's own README, which is in Korean, gives these commands for installing the environment, to be run from the repository root in PowerShell:

```powershell
python -m venv services/scholarly-mcp/.venv
& services/scholarly-mcp/.venv/Scripts/python.exe -m pip install -r services/scholarly-mcp/requirements.txt
& services/scholarly-mcp/.venv/Scripts/python.exe -m playwright install firefox
```

Beyond the servers named in the instance's settings, the sessions have the CLIs' built-in tools, which include shell commands and web search.'''),
(r'''Two commands that are used once the research has results have requirements of their own. `paper.py`, which writes the paper, needs a TeX program, `tectonic`, `latexmk` or `pdflatex`, to produce the PDF; without one it still writes the manuscript.''',
 r'''Two commands have requirements of their own; both are used once the research has results. `paper.py`, which writes the paper, needs one of the TeX programs `tectonic`, `latexmk` and `pdflatex` to produce the PDF; without one it still writes the manuscript.'''),
(r'''No run on a system other than Windows has been recorded. The runtime also has code for Linux, where it reads `/proc`. macOS is not supported,''',
 r'''Every run whose operating system is recorded was made on Windows. The runtime has code for Linux as well, where it reads `/proc`, and no recorded run has used that code. macOS is not supported,'''),
(r'''A run has no cap on time, on the number of sessions, or on usage, and do-math collects no usage figures. The only limit of that kind is the number of sessions running at once.''',
 r'''A run has no cap on time, on the number of sessions it launches in all, or on usage, and do-math collects no usage figures. The only limit of that kind is on the number of sessions running at once.'''),
(r'''An instance is created from three things that you prepare outside the new instance directory: a root file, a folder that holds the beginning of the Lean library, and a settings file.''',
 r'''An instance is created from a root file and a folder that holds the beginning of the Lean library, usually with a settings file, all of which you prepare outside the new instance directory.'''),
(r'''The defaults are these.''',
 r'''The main defaults are these.'''),
(r'''as in this example, where `claude/opus` is an alias that the Claude CLI resolves to a model:''',
 r'''as in this example, where `claude/opus` names the Claude CLI's `opus` model; with only Codex installed, do the same with `codex/gpt-6.1-sol`:'''),
(r'''`--root` is the root file, `--canon` the folder with the Lean library, and `--root-declaration` the full Lean name of the root; all three are required. `--settings` is optional, and without it every default applies. `init` copies the files into the instance, compiles the library, extracts the structural index and makes the first Git commit. Nothing in do-math compiles the folder before this, so `init` is where you learn whether it compiles; with files that import Mathlib it takes minutes. It refuses, among other things, a library that does not compile, a value check that fails, a declaration without a record or a record without a declaration, a record without a weight or a description, an `axiom`, a definition that contains `sorry`, a root that is not a theorem or that already has a proof, a settings file that is not valid, and a tool server whose command is not found. A refusal names the cause. If `init` refuses after it has created the directory, the partial directory is not an instance; correct the files and run `init` again on a new path.''',
 r'''`--root` is the root file, `--canon` the folder with the Lean library, and `--root-declaration` the full Lean name of the root; all three are required. `--settings` is optional, and without it every default applies.

`init` copies the files into the instance, compiles the library, extracts the structural index and makes the first Git commit. Nothing in do-math compiles the folder before this, so `init` is where you learn whether it compiles; with files that import Mathlib it takes minutes.

`init` refuses, among other things:

- a library that does not compile, or a value check that fails;
- a declaration without a record, or a record without a declaration;
- a record without a weight or a description;
- an `axiom`, or a definition that contains `sorry`;
- a root that is not a theorem, or that already has a proof;
- a settings file that is not valid, or a tool server whose command is not found.

A refusal names the cause. If `init` refuses after it has created the directory, the partial directory is not an instance; correct the files and run `init` again on a new path.'''),
(r'''This reading is the only judgment of meaning that the Lean statement of the root receives.''',
 r'''Nothing after this reading judges what the Lean statement of the root means.'''),
(r'''When the operator delivers a condition for you, it gives your words in English translation as a quotation marked as yours and marks its own explanation as its own. It adds no reason that you did not give, and it adds an example of its own only rarely and marked as its own.''',
 r'''When the operator delivers a condition for you, it quotes your words in English translation and marks the quotation as yours, and it marks any explanation it adds as the operator's. It adds no reason that you did not give. It rarely adds an example, and when it does, it marks the example as the operator's too.'''),
(r'''It can be run at any time, also while the instance runs,''',
 r'''It can be run at any time, including while the instance is running,'''),
(r'''Run it by hand only when that result is unavailable and the cause has been repaired. Exit code 0 means accepted, 2 rejected, and 1 that the command refused or the judge could not run, which says nothing about the proof.''',
 r'''Run it by hand when that result is unavailable and the cause has been repaired. Exit code 0 means accepted, 2 rejected, and 1 that the command refused or the judge could not run, which says nothing about the proof.

For both `paper.py` and `judge.py`, a command line that the program cannot parse also exits with 2, with a usage message in place of a result.'''),
(r'''this also ends the session's host process and, on Windows, where a session's processes are contained, the processes the session started. When no session is running, end the runner process with `Stop-Process` on Windows or `kill` on Linux; its ID is the `pid` recorded in the instance's `runner/process.json`.''',
 r'''this also ends the session's host process. On Windows, where the session's processes were contained when it was launched, it ends the processes the session started as well, except any that a system service started on its behalf. When no session is running, end the runner process with `Stop-Process` on Windows or `kill` on Linux; its ID is the `pid` under `process` in the instance's `runner/process.json`.'''),
(r'''the runner has the root judged; and it finishes when that work has ended.''',
 r'''the runner has the root judged, where the instance has a judge; and it finishes when that work has ended.'''),
]


def apply(path, pairs):
    text = path.read_text(encoding='utf-8')
    failed = []
    for index, (old, new) in enumerate(pairs):
        count = text.count(old)
        if count != 1:
            failed.append((index, count, old[:70]))
            continue
        text = text.replace(old, new)
    if failed:
        for item in failed:
            print('NO MATCH', path.name, item)
        return False
    path.write_text(text, encoding='utf-8', newline='\n')
    print('applied', len(pairs), 'to', path.name)
    return True


ok = apply(ROOT / 'README.md', README)
ok = apply(ROOT / 'docs' / 'do-math' / 'running.md', GUIDE) and ok
sys.exit(0 if ok else 1)
