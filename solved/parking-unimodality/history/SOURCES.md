# Where the sources of the history are

`timeline.md` cites its sources by coordinates. This file says, for each kind of coordinate, where a reader finds the source, and lists the sources that are cited and not published.

There are three places.

- **The archives.** `solved/parking-unimodality/knowledge/` holds two archives, described in `MANIFEST.md` in that folder: `parking-unimodality-fresh-20261105-150803-knowledge.tar.xz` for the earlier instance (E) and `parking-unimodality-20261119-knowledge.tar.xz` for the later instance (L). Each contains the folder `knowledge/` of its instance at the last commit that the history considers (E: `12e91f442`, 13 November 2026, 06:12; L: `130a7a3`, 23 November 2026, 08:10; times are Korean Standard Time). Only the archive of the later instance is in the repository. The archive of the earlier instance is 349 MB and is left out of it, so a coordinate that leads into that archive can be opened only by a reader who has the file; `MANIFEST.md` gives its checksum.
- **The folder `sources/`**, beside this file. It holds copies of the cited files that are not in the archives and are not tracked files of the repository. Its layout shows where each file came from: `sources/earlier-instance/` and `sources/later-instance/` repeat the layout of the two instance directories; `sources/between/` holds the documents written between the two instances; `sources/operator/` holds files kept by the operating sessions outside the instances; `sources/machine/` holds the extract of the system log.
- **Tracked files of the repository**, cited by their path from the repository root.

In `timeline.md` a path that begins with `sources/` is relative to this folder; a path that begins with `knowledge/`, `control/`, `runner/` or `sessions/` is relative to the directory of the instance concerned; every other path is relative to the repository root.

## Coordinates and where they lead

| coordinate in the history | what it is | where to find it |
|---|---|---|
| "E seq 133", "L seq 62" | the publication with that sequence number | The index `sources/earlier-instance/publications.tsv` or `sources/later-instance/publications.tsv` gives, for each sequence number, the time, the kind, the identifier, the folder under `knowledge/`, and the commit. The publication itself is in the archive of its instance, at the folder named there; its event is `knowledge/events/<identifier>.json`. |
| a record token such as `rce3dc75` | the first characters of a record's identifier | In the archive: `knowledge/records/<identifier>/`, with `record.json` (description, claims, proposed nodes, relations, solutions), `exposition.md`, `review/assessment.json` and `review/feedback.md`, `provenance.json`, `evidence/`, and for formal records `lean/`. The index named above gives the full identifier. |
| a claim, a section of an exposition, a review's reason | parts of a record | In the record's folder in the archive, as above. |
| a Lean theorem such as `Parking.root_unimodal`; `lean/Parking/Defs.lean`; `evidence/peer/builds/modules/Parking.LP.DepAudit.stdout.txt` | Lean sources and build outputs of a formal record | In the record's folder in the archive, under `lean/` and `evidence/`. |
| the state of a node or of a question at the last commit | the frontier | In the archive: `knowledge/frontier.md` and `knowledge/questions/`. |
| "commit `5be357d72`" | a commit of an instance's own Git repository | `sources/earlier-instance/git-log.txt` and `sources/later-instance/git-log.txt` list every commit up to the last one considered, with its time and subject; the subject of a publication's commit names the identifier. The repositories themselves are not published (see below). |
| "input `1794234897325633500-…`", "L input `1795168467569364900`" | a standing input; the number is its submission time in nanoseconds since the epoch, UTC | `sources/earlier-instance/control/inputs/` and `sources/later-instance/control/inputs/`. The retired input of 7 November 22:02 is in `sources/earlier-instance/control/retired-inputs/`. The input of 6 November 20:43, which was withdrawn, is in the operator's copy `sources/operator/external-evaluation-route-20261106.md` and, as the sessions received it, in `sources/earlier-instance/sessions/s282ce842b87c433ebb75c58cf8070f59/input.json`. |
| `control/pause-formalization` | the flag file of the pause of 9 November | `sources/earlier-instance/control/pause-formalization` |
| `runner/state.json`, `runner/process.json`, `runner/seeds-inserted.json`, `runner/start-…` | state and logs of the program that launched the sessions | `sources/earlier-instance/runner/` and `sources/later-instance/runner/`. The later instance was still running when the copy was made (23 November, about 13:30), so its `state.json` also holds sessions later than the commit considered. |
| "the log of its Lean broker" | the log of the later instance's queue of Lean compilations | `sources/later-instance/runner/lean/broker.log` |
| `settings.json`; `git show d31ae5b4d:settings.json`; `git show c3d45ec:settings.json` | the settings of an instance, as they stand and as they were at its first commit | `sources/earlier-instance/settings.json` and `settings-at-d31ae5b4d.json`; `sources/later-instance/settings.json` and `settings-at-c3d45ec.json` |
| `root.md` | the statement under research as each instance has it | `sources/earlier-instance/root.md`, `sources/later-instance/root.md` |
| "the `input.json` of the sessions started at 18:06 and at 18:35" (7 November) | what two sessions of the earlier instance received, including their settings | `sources/earlier-instance/sessions/s76f3c0a0e57d42b489ec92293ea8849d/input.json` (18:06) and `sources/earlier-instance/sessions/s297efe21c21142f2a30d7b800dea6be8/input.json` (18:35) |
| "session `s118b408b…`, report §1.4" | the report of a session of the earlier instance | `sources/earlier-instance/sessions/s118b408bb2d242a4a586406e3958dd2c/output/report.md` |
| "`sessions/s4844ab8b…`", its report finished at 18:28 on 19 November | the report of a session of the later instance | `sources/later-instance/sessions/s4844ab8bc416499487c810e7fe24a972/output/report.md`, with `output/outcome.json` and `termination.json` |
| `knowledge/records/ra3e85e42…/evidence/producer/work/updates-final.json` | the registrations of sections of 6 November | In the archive of the earlier instance, at that path. |
| "M-0731" and other numbers of that form | a note in the working memory of the repository | Tracked file `기억/layer1/M-0731.md` (one file for each number). |
| the manuscript; `임시/주차함수_증명/장v2/…`; `합의.md`; `연구_파악.md`; `작업_장부.md` | the write-up of the earlier proof and three working files of its writing | Tracked files under `임시/주차함수_증명/`. |
| the structure document; the five reports; the chapter summaries; the note on the literature | the documents of the night of 19 November | `sources/between/structure-document/`: `단봉성의_구조.md`, `시도/` (five reports), `요약_장….md` (four summaries), `문헌.md` |
| the handoff | the first standing input of the later instance | `sources/later-instance/control/inputs/1795057444813564600-a61b69ea35b74ebbbd7f7ff2608e2423.txt` |
| the paper; its handoff; `contract.md`; `log.md`; `structure.md` | the paper and the documents of its making | `sources/between/paper/structure/` (`paper/paper.md`, `paper/handoff.md`, `contract.md`, `log.md`, `system/structure.md`) |
| the five documents on the Cayley–Borel coherence and the three notes | the documents from which the paper grew | `sources/between/paper/documents/` |
| the relay of 9 November to the running sessions | messages of the operator to eleven sessions | `sources/operator/messenger-20261109/` |
| the rehearsal of the insertion on a scratch instance | its record of the inserted package | `sources/operator/seeding-test-20261119/runner/seeds-inserted.json` |
| the Windows system log | start and shutdown events of the machine, 5 to 15 November | `sources/machine/system-events-1105-1115.txt` |
| `.agents/skills/do-math/runtime/knowledge.py` | the program text with the fixed wording of the root question's resolution | Tracked file at that path. |
| `solved/parking-unimodality/knowledge/MANIFEST.md` | the description of the two archives | At that path. |

## What is under `sources/`

131 files, 15,270,170 bytes.

| folder | files | bytes | contents |
|---|---|---|---|
| `earlier-instance/` (top level) | 5 | 111,434 | `root.md`, `settings.json`, `settings-at-d31ae5b4d.json`, `git-log.txt`, `publications.tsv` |
| `earlier-instance/control/` | 11 | 99,824 | nine standing inputs, one retired input, the pause flag |
| `earlier-instance/runner/` | 38 | 7,832,490 | `state.json`, `process.json`, the logs of the eighteen starts of the runner |
| `earlier-instance/sessions/` | 4 | 120,939 | one report, three `input.json` |
| `later-instance/` (top level) | 5 | 32,663 | `root.md`, `settings.json`, `settings-at-c3d45ec.json`, `git-log.txt`, `publications.tsv` |
| `later-instance/control/` | 14 | 135,152 | fourteen standing inputs |
| `later-instance/runner/` | 18 | 4,817,754 | `state.json`, `process.json`, `seeds-inserted.json`, the logs of the seven starts of the runner, `lean/broker.log` |
| `later-instance/sessions/` | 3 | 195,034 | one report with its outcome and termination files |
| `between/structure-document/` | 11 | 826,634 | the structure document, five reports, four chapter summaries, the note on the literature |
| `between/paper/documents/` | 8 | 297,580 | the five documents and three notes |
| `between/paper/structure/` | 5 | 760,974 | the paper, its handoff, the contract, the log, the structure |
| `operator/` | 8 | 37,733 | the copy of the outside evaluation, the relay of 9 November, the record of the rehearsal |
| `machine/` | 1 | 1,959 | the extract of the system log |

Three kinds of file in `sources/` are not copies of files on the machine but were made for publication from the instances' data, by reading only: `git-log.txt` (the output of `git log` up to the last commit considered: abbreviated hash, time, subject), `publications.tsv` (from `knowledge/events/` and the Git log), and `settings-at-<commit>.json` (the output of `git show <commit>:settings.json`).

**One change was made to the copies.** The name of the Windows account of the machine has been replaced by `<account>` wherever it occurred, in ten files: `between/paper/structure/contract.md`, `earlier-instance/settings.json`, `earlier-instance/settings-at-d31ae5b4d.json`, the three `input.json` under `earlier-instance/sessions/`, `later-instance/settings.json`, `later-instance/settings-at-c3d45ec.json`, `machine/system-events-1105-1115.txt`, and `operator/messenger-20261109/run_relay.sh`. Nothing else in any copy was changed. Before copying, every file was searched for e-mail addresses and for strings of the form of credentials or access tokens; none was found, and no file was left out for that reason.

## Cited and not published

| source | where the history uses it | why it is not published |
|---|---|---|
| The archive of the earlier instance's `knowledge/` | every coordinate of the form "E seq N" and every record token of the earlier instance | It is 349 MB and is left out of the repository for its size; `MANIFEST.md` describes it and gives its checksum. What is published of the earlier instance is under `sources/earlier-instance/`: the index of its publications, the list of its commits, its inputs, its settings, and the runner's state and logs. |
| A private session transcript of 19 November 2026 | sections 5 and 6.1: the user's messages of that day, with their times | It is a private transcript of an interactive session, and it is withheld by the user's decision. The history quotes the user's words from it in English. |
| The transcripts of the instances' sessions (`sessions/<id>/cli.stdout.jsonl` and the like) | section 4.11 and the milestone of 13 November 06:12: only the times at which these files were last written | They were not read for the history, apart from those times; they are many gigabytes of raw session output. |
| The session folders other than the files listed above | session identifiers given as coordinates (for example `s94cb8754…`) | The times and roles of every session are in the published `runner/state.json`; the folders hold transcripts and working files that the history does not cite. |
| The Git repositories of the two instances | commits; the state of the frontier at earlier commits; the earlier verdicts of the three reviews that the operator edited (L seq 28, 29, 35) | A repository is not a file that can be laid beside the history, and the earlier instance's is several times the size of its archive. The published `git-log.txt` gives every commit with its time; the content of a commit other than the last is not published. |
| The older runs on the same conjecture: `.skill-workspace/do-math/parking-unimodality-fresh-20261022-071132` and `.skill-workspace/do-math-inputs/parking-unimodality-fresh-20261023-014524/` | section 4.1 and the first milestone: that they exist, with their dates | They were not read for the history, which says so; only their existence and dates are cited. |
| The data bundle of the manuscript, `임시/주차함수_증명/원고_자료/` (copies of the certificate files of eighteen records of the earlier instance, one folder per record) | section 5.4: that these copies lay within reach of the later instance's sessions | It is 192 MB in 1,704 files, of which four are tracked; with it the folder `sources/` would pass 200 MB. The history cites its existence, not its content; the certificate files themselves belong to records of the earlier instance, whose folders are in that instance's archive. |
| The computations that accompany the five reports and the paper (folders of scripts and outputs beside them) | section 5.2 and 5.3 mention that they exist | The history cites the reports and the paper, not the scripts. |
| The rest of the later instance's `runner/lean/` (build cache and job files, about 21 GB) | not cited; only `broker.log` is | Not cited. |
| The working files of this history (the source readers' reports, the checkers' reports, the scripts of every correction) | section 9 describes them | They lie in a folder of the repository that version control ignores (`.skill-workspace/parking-root-paper/history-work/`) and are not part of the publication. |
