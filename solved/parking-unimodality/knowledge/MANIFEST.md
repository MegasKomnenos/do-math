# Archives of the two research instances' `knowledge/` directories

This file describes two archives and says how to verify and unpack them; each archive holds what one instance of do-math had published at one commit, including its records with their reviews and evidence. An instance is one run of the autonomous research system do-math on one statement, and it is a directory with its own Git repository. Two instances researched the unimodality of the maximum-displacement counts of parking functions, and there is one archive for each. The later instance started after the earlier had stopped, and it did not receive the earlier instance's records. `../history/timeline.md` tells how the work passed from one to the other, and its section 2.2 describes the system.

Each archive is the instance's `knowledge/` directory as it stands in one Git commit of the instance's own repository, file for file. The bytes of a file differ from the committed ones in line endings only, as the last section of this file says. The commit is the one that was at the head of that repository immediately before the archive was started. A piece of the instance's work becomes a record when a review decides to publish it, and the record's publication is one commit of that repository. The archive was made from the commit and not from the working directory, so that it is a consistent published state even where a runner was still writing files (the runner is the program that launches the AI sessions working in an instance). Both archives were made on 2026-11-23 (KST), with `git archive` piped into `xz`.

Only the archive of the later instance is in this repository, the one that holds this folder, and it lies in the same folder as this file. The archive of the earlier instance is 349 MB and is left out of this repository (it is listed in `.gitignore`); at present it can be obtained only on the machine on which it was made. Its description and its checksum are given below, so that a copy of it can be checked against them. The commands for checking and unpacking an archive are under [Verifying and unpacking](#verifying-and-unpacking).

## `parking-unimodality-20261119-knowledge.tar.xz` (the later instance)

| | |
|---|---|
| Directory of the instance | `C:\math\.skill-workspace\parking-unimodality-20261119` |
| Commit archived | `130a7a356c289478272d800139550685f69e16f6` |
| Subject of the commit | `Publish r3d3d37acd8a7446b8f47d472502d231a` |
| Commit date | 2026-11-23 08:10:25 KST (`2026-11-23T08:10:25+09:00`) |
| Files | 15,500 |
| Uncompressed size, file content | 196,976,063 bytes in the archive; 195,711,702 bytes in the commit |
| Uncompressed size, tar stream | 199.7 MiB |
| Archive size | 67,850,692 bytes |
| SHA-256 | `07ab803f2a85738acb0ffca06fc5e037fc6d91e8b881f9c4d8c22fd9eb7b547d` |

The statement under research is called the root, and it is one of the propositions on the instance's map of the problem. The commit archived is the 125th commit of the instance's repository, and it is the commit at which the root is formally proved. It was not picked out among the commits: it was the head of the repository when the archive was started, less than an hour after the commit was made, and the instance published nothing in between. The commit publishes the record `r3d3d37acd8a7446b8f47d472502d231a`, through which `knowledge/frontier.md`, a file of the map, reports the root as `formal_proved` (Lean theorem `Parking.root_unimodal`). A proposition on the map is in that state only through a Lean proof of its own statement, which a review of the instance has itself compiled and compared with the statement.

The instance's runner was still running. This is how the working directory differed from the commit when the archive was made:

- `knowledge/board.md` was modified in the working directory and not committed. The board is the table of work in progress, which the runner rewrites as sessions change stage; the uncommitted version had dropped the finished pipeline of the record above and moved three running pipelines from "producing" to "peer". The archive contains the board as committed in `130a7a3`.
- There were no untracked files and no ignored files under `knowledge/`.

The comparison was made with `git status --short -- knowledge`, and `git ls-files --others` with and without `--ignored`, run at about 09:00 KST. At 09:29:30 KST, after this archive was finished, the instance committed `e88f2a0` (`Publish r1c25d8325e824b28b28fc98178a7b4d5`). That commit and anything later are not in the archive.

## `parking-unimodality-fresh-20261105-150803-knowledge.tar.xz` (the earlier instance)

This archive is not in this repository; at present it can be obtained only on the machine on which it was made.

| | |
|---|---|
| Directory of the instance | `C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803` |
| Commit archived | `12e91f4421840de7c08eadf89e43e61ee080a36a` |
| Subject of the commit | `Publish rfc427ffbb4f242688f1263c34e8476f1` |
| Commit date | 2026-11-13 06:12:05 KST (`2026-11-13T06:12:05+09:00`) |
| Files | 36,393 |
| Uncompressed size, file content | 763,418,015 bytes in the archive; 756,409,762 bytes in the commit |
| Uncompressed size, tar stream | 756.6 MiB |
| Archive size | 348,855,748 bytes |
| SHA-256 | `65009fbf22cf6442ad3867cbb266c24e844354e9cfd1c4bab47d36f65650b22e` |

The runner of this instance was stopped; its repository has no commit after the one archived, which is the 438th and last commit of that repository. At this commit the root is `informal_proved`, according to section 2.3 of `../history/timeline.md`. Sections 1 and 3 of the history say that the instance had reached a proof that its reviews accepted, and that the proof was never formalized.

This is how the working directory differed from the commit when the archive was made:

- `knowledge/board.md` was modified in the working directory and not committed (two lines added, one removed: the state of the pipelines at the moment the runner stopped). The archive contains the board as committed.
- Four files that the commit contains had been deleted from the working directory: the compiled Python caches `cert_assembly_mono.cpython-312.pyc`, `cert_lib.cpython-312.pyc`, `fixes.cpython-312.pyc` and `window_lib.cpython-312.pyc` under `knowledge/records/r030ffaebcd164eb492cc4215ce1c2e56/evidence/peer/rerun/work/__pycache__/`. Because the archive follows the commit, it includes these four files. (The commit tracks 149 `__pycache__/*.pyc` files in all, every one of them under `knowledge/` and these four among them; they are by-products of scripts the sessions ran, and all 149 are in the archive.)
- There were no untracked files and no ignored files under `knowledge/`.

An older archive, `knowledge.7z` (351,123,006 bytes, dated 2026-11-14), lies inside the directory of the instance, beside its `knowledge/` folder. It is a 7-Zip archive of that folder, made from the working directory and not from a commit. Its listing names the same 36,393 files as the commit archived here, with the board in its uncommitted version; the contents of the files were not compared with this archive. It was left where it was.

## Verifying and unpacking

The commands below name both archives. Where they name the archive of the earlier instance, they are for you if you have a copy of it.

To check an archive's integrity:

```sh
sha256sum parking-unimodality-20261119-knowledge.tar.xz
sha256sum parking-unimodality-fresh-20261105-150803-knowledge.tar.xz
xz -t parking-unimodality-20261119-knowledge.tar.xz parking-unimodality-fresh-20261105-150803-knowledge.tar.xz
```

The values that `sha256sum` should print are those of the two tables above:

- for the later instance, `07ab803f2a85738acb0ffca06fc5e037fc6d91e8b881f9c4d8c22fd9eb7b547d`
- for the earlier instance, `65009fbf22cf6442ad3867cbb266c24e844354e9cfd1c4bab47d36f65650b22e`

To unpack one into an empty directory (this creates `<target>/knowledge/…`):

```sh
mkdir -p <target>
tar -xJf parking-unimodality-20261119-knowledge.tar.xz -C <target>
# or, for the earlier instance
tar -xJf parking-unimodality-fresh-20261105-150803-knowledge.tar.xz -C <target>
```

Where `tar` has no built-in xz support, `xz -dc <archive> | tar -xf - -C <target>` does the same.

The commit an archive was made from can be read from the archive itself with `xz -dc <archive> | git get-tar-commit-id`.

## What an archive holds, and what it does not

Paths inside each archive begin with `knowledge/`. That directory includes the following.

- `knowledge/frontier.md` and `knowledge/questions/` give the state of a proposition on the instance's map of the problem, or of a question, at the commit.
- `knowledge/records/` has one folder for each record, named by the record's identifier. The folder holds the record's exposition, its review and its evidence, and for a formal record the Lean sources.
- `knowledge/events/` has one file for each publication, with its sequence number and time.
- `knowledge/board.md` is the board, the table of work in progress.

Only `knowledge/` is archived. The rest of each instance is not here: the sessions' working directories and transcripts (`sessions/`), the runner's state and logs (`runner/`), the standing inputs (`control/inputs/`), the file with the statement under research (`root.md`), `settings.json`, and the Git history itself (an archive holds one commit's tree, not the sequence of commits). The written history in `../history/timeline.md` cites those sources by their paths in the instances. `../history/SOURCES.md` says where each kind of source that the history cites is found, and lists the sources that are cited and not published.

## How the archives were made and checked

Each archive was made with

```sh
git -C <instance> archive --format=tar <commit> knowledge | xz -6 -T1 > <name>-knowledge.tar.xz
```

where `<commit>` is the full hash that `git -C <instance> rev-parse HEAD` returned immediately before the archive was started. The two compressions were run one after the other. In the names of the two files, `<name>` is `parking-unimodality-20261119` for the later instance and `parking-unimodality-fresh-20261105-150803` for the earlier.

Each archive was checked after it was written. `xz -t` reported no error. The number of regular files in `tar -tJf` equalled the number of files that `git ls-tree -r <commit> -- knowledge` lists: 15,500 for the later instance and 36,393 for the earlier. The tar listing of the later instance's archive has 16,635 entries, of which 1,135 are directories; that of the earlier instance's archive has 40,425 entries, of which 4,032 are directories. In each listing the entries that are not directories are as many as the files. The commit hash that `git archive` embeds was read back from both archives: `xz -dc … | git get-tar-commit-id` printed `130a7a356c289478272d800139550685f69e16f6` for the later instance and `12e91f4421840de7c08eadf89e43e61ee080a36a` for the earlier.

The files of each archive were also compared, one by one, with the files of its commit. They differ in line endings and in nothing else. Git on the machine on which the archives were made is set to `core.autocrlf=true`, and with that setting `git archive` writes a file that Git takes for text with CRLF line endings, where the commit stores it with LF. In the archive of the later instance 14,958 of the 15,500 files have CRLF line endings for that reason and 542 have the committed bytes; in the archive of the earlier instance the numbers are 34,792 and 1,601 of 36,393. Each file of the first kind has exactly the committed bytes once every CRLF is turned back into LF. This is why the file content of an archive is larger than that of its commit in the tables above, by 1,264,361 bytes for the later instance and by 7,008,253 for the earlier. Where a record gives a checksum of one of its own files, as the file `evidence/peer/lean-manifest.json` of the record `r3d3d37acd8a7446b8f47d472502d231a` does for its Lean sources, it is the checksum of the committed bytes, and a file with CRLF line endings does not match it as unpacked.
