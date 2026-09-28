"""Real Git backend port: the git executable, isolated from user configuration and hooks."""
import os
from pathlib import Path
import subprocess

from .ports.git_backend import GitBackendError


class GitProcess:
    def __init__(self):
        self._git_dirs = {}

    def _run(self, repository, *arguments, input=None):
        repository = Path(repository).absolute()
        # Until Git reports its directory, the work tree stands in for it (hooks path).
        git_dir = self._git_dirs.get(repository, repository)
        environment = os.environ.copy()
        environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_OPTIONAL_LOCKS": "0"})
        return subprocess.run(
            ["git", "-C", str(repository), "-c", "user.name=do-math", "-c", "user.email=do-math@invalid",
             "-c", f"core.hooksPath={git_dir / 'do-math-disabled-hooks'}", *arguments],
            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    @staticmethod
    def _fail(arguments, completed):
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise GitBackendError(f"git {' '.join(arguments)} failed: {detail}")

    def _checked(self, repository, *arguments, input=None):
        completed = self._run(repository, *arguments, input=input)
        if completed.returncode:
            self._fail(arguments, completed)
        return completed.stdout

    def describe(self, repository):
        facts = self._checked(repository, "rev-parse", "--absolute-git-dir", "--show-object-format",
                              "--git-path", "objects").decode("utf-8").strip().splitlines()
        if len(facts) != 3:
            raise GitBackendError("git rev-parse did not report the Git directory, object format and objects")
        self._git_dirs[Path(repository).absolute()] = Path(facts[0]).absolute()
        return facts[0], facts[1].strip(), facts[2].strip()

    def object_info(self, repository, specs):
        if not specs:
            return []
        arguments = ("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)")
        rows = self._checked(repository, *arguments,
                             input="".join(spec + "\n" for spec in specs).encode("utf-8")).decode("utf-8").splitlines()
        if len(rows) != len(specs):
            raise GitBackendError("batch object check response count differs")
        result = []
        for spec, row in zip(specs, rows):
            if row == f"{spec} missing":
                result.append(None)
                continue
            fields = row.split()
            if len(fields) != 3 or not fields[2].isdigit():
                raise GitBackendError("invalid batch object check row for " + spec)
            result.append((fields[0], fields[1], int(fields[2])))
        return result

    def read_objects(self, repository, specs):
        if not specs:
            return []
        raw = self._checked(repository, "cat-file", "--batch",
                            input="".join(spec + "\n" for spec in specs).encode("utf-8"))
        result, offset = [], 0
        for spec in specs:
            end = raw.find(b"\n", offset)
            if end >= 0 and raw[offset:end] == f"{spec} missing".encode("utf-8"):
                result.append(None)
                offset = end + 1
                continue
            header = raw[offset:end].split() if end >= 0 else []
            if len(header) != 3 or not header[2].isdigit():
                raise GitBackendError("batch read returned no object header for " + spec)
            size = int(header[2])
            start, offset = end + 1, end + 1 + size
            if raw[offset:offset + 1] != b"\n":
                raise GitBackendError("truncated batch object: " + spec)
            result.append((header[1].decode("ascii"), raw[start:offset]))
            offset += 1
        if offset != len(raw):
            raise GitBackendError("unexpected trailing batch output")
        return result

    def ref_oid(self, repository, ref):
        arguments = ("rev-parse", "--verify", "--quiet", ref)
        completed = self._run(repository, *arguments)
        if completed.returncode:
            if completed.returncode == 1 and not completed.stderr:
                return None
            self._fail(arguments, completed)
        return completed.stdout.decode("ascii").strip()

    def update_ref(self, repository, ref, new, old):
        return not self._run(repository, "update-ref", ref, new, old or "0" * len(new)).returncode

    def list_tree(self, repository, commit):
        rows = []
        for record in self._checked(repository, "ls-tree", "-r", "-t", "-z", commit).split(b"\0"):
            if not record:
                continue
            fields, _, path = record.partition(b"\t")
            mode, kind, oid = fields.decode("ascii").split(" ")
            rows.append((mode, kind, oid, path))
        return rows

    def first_parent_line(self, repository, parent, head):
        return self._checked(repository, "rev-list", "--first-parent", "--reverse",
                             parent + ".." + head).decode("ascii").splitlines()
