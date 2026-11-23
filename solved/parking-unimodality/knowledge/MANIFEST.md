# Archives of the two research instances' `knowledge/` directories

This file describes one archive for each of the two do-math instances that researched the unimodality of the maximum-displacement counts of parking functions. Each archive is the instance's `knowledge/` directory exactly as it stands in one Git commit of the instance's own repository. It was made from the commit and not from the working directory, so that it is a consistent published state even where a runner was still writing files.

Only the first of the two archives is in the repository. The second, of the earlier instance, is 349 MB and is left out of the repository (it is listed in `.gitignore`); it is kept on the machine on which it was made. Its description and its checksum are given below, so that a copy of it can be checked against them.

Both archives were made on 2026-11-23 (KST) with

```sh
git -C <instance> archive --format=tar <commit> knowledge | xz -6 -T1 > <name>-knowledge.tar.xz
```

where `<commit>` is the full hash that `git -C <instance> rev-parse HEAD` returned immediately before the archive was started. The two compressions were run one after the other. Paths inside each archive begin with `knowledge/`.

## 1. `parking-unimodality-20261119-knowledge.tar.xz` (the later instance)

| | |
|---|---|
| Instance | `C:\math\.skill-workspace\parking-unimodality-20261119` |
| Commit archived | `130a7a356c289478272d800139550685f69e16f6` (`Publish r3d3d37acd8a7446b8f47d472502d231a`; the 125th commit of the repository) |
| Commit date | 2026-11-23 08:10:25 KST (`2026-11-23T08:10:25+09:00`) |
| Files | 15,500 (the tar listing has 16,635 entries, of which 1,135 are directories) |
| Uncompressed size | 195,711,702 bytes of file content (the tar stream is 199.7 MiB) |
| Archive size | 67,850,692 bytes |
| SHA-256 | `07ab803f2a85738acb0ffca06fc5e037fc6d91e8b881f9c4d8c22fd9eb7b547d` |

This commit is the one that publishes the record `r3d3d37acd8a7446b8f47d472502d231a`, through which `knowledge/frontier.md` reports the root as `formal_proved` (Lean theorem `Parking.root_unimodal`).

How the working directory differed from the commit when the archive was made (`git status --short -- knowledge`, and `git ls-files --others` with and without `--ignored`, run at about 09:00 KST):

- `knowledge/board.md` was modified in the working directory and not committed. The board is the table of work in progress, which the runner rewrites as sessions change stage; the uncommitted version had dropped the finished pipeline of the record above and moved three running pipelines from "producing" to "peer". The archive contains the board as committed in `130a7a3`.
- There were no untracked files and no ignored files under `knowledge/`.

The instance's runner was still running. At 09:29:30 KST, after this archive was finished, the instance committed `e88f2a0` (`Publish r1c25d8325e824b28b28fc98178a7b4d5`). That commit and anything later are not in the archive.

## 2. `parking-unimodality-fresh-20261105-150803-knowledge.tar.xz` (the earlier instance)

This archive is not in the repository, as said at the head of this file.

| | |
|---|---|
| Instance | `C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803` |
| Commit archived | `12e91f4421840de7c08eadf89e43e61ee080a36a` (`Publish rfc427ffbb4f242688f1263c34e8476f1`; the 438th and last commit of the repository) |
| Commit date | 2026-11-13 06:12:05 KST (`2026-11-13T06:12:05+09:00`) |
| Files | 36,393 (the tar listing has 40,425 entries, of which 4,032 are directories) |
| Uncompressed size | 756,409,762 bytes of file content (the tar stream is 756.6 MiB) |
| Archive size | 348,855,748 bytes |
| SHA-256 | `65009fbf22cf6442ad3867cbb266c24e844354e9cfd1c4bab47d36f65650b22e` |

How the working directory differed from the commit when the archive was made:

- `knowledge/board.md` was modified in the working directory and not committed (two lines added, one removed: the state of the pipelines at the moment the runner stopped). The archive contains the board as committed.
- Four files that the commit contains had been deleted from the working directory: the compiled Python caches `cert_assembly_mono.cpython-312.pyc`, `cert_lib.cpython-312.pyc`, `fixes.cpython-312.pyc` and `window_lib.cpython-312.pyc` under `knowledge/records/r030ffaebcd164eb492cc4215ce1c2e56/evidence/peer/rerun/work/__pycache__/`. Because the archive follows the commit, it includes these four files. (The commit tracks 149 `__pycache__/*.pyc` files in all; they are by-products of scripts the sessions ran and all of them are in the archive.)
- There were no untracked files and no ignored files under `knowledge/`.

The runner of this instance was stopped; its repository has no commit after the one archived.

An older archive, `knowledge.7z` (351,123,006 bytes, dated 2026-11-14), lies inside the instance directory. It was left where it is and was not compared with this archive.

## Verifying and restoring

Each archive was checked after it was written: `xz -t` reported no error, and the number of regular files in `tar -tJf` equalled the number of files that `git ls-tree -r <commit> -- knowledge` lists (15,500 and 36,393). For the first archive the commit hash embedded by `git archive` was also read back (`xz -dc … | git get-tar-commit-id` printed `130a7a356c289478272d800139550685f69e16f6`).

To check an archive's integrity:

```sh
sha256sum parking-unimodality-20261119-knowledge.tar.xz
sha256sum parking-unimodality-fresh-20261105-150803-knowledge.tar.xz
xz -t parking-unimodality-20261119-knowledge.tar.xz parking-unimodality-fresh-20261105-150803-knowledge.tar.xz
```

To restore one into an empty directory (this creates `<target>/knowledge/…`):

```sh
mkdir -p <target>
tar -xJf parking-unimodality-20261119-knowledge.tar.xz -C <target>
# or, for the earlier instance
tar -xJf parking-unimodality-fresh-20261105-150803-knowledge.tar.xz -C <target>
```

Where `tar` has no built-in xz support, `xz -dc <archive> | tar -xf - -C <target>` does the same. The commit an archive was made from can be read from the archive itself with `xz -dc <archive> | git get-tar-commit-id`.

## What the archives do not contain

Only `knowledge/` is archived. The rest of each instance is not here: the sessions' working directories and transcripts (`sessions/`), the runner's state and logs (`runner/`), the standing inputs (`control/inputs/`), `root.md`, `settings.json`, and the Git history itself (an archive holds one commit's tree, not the sequence of commits). The written history in `../history/timeline.md` cites those sources by their paths in the instances.
