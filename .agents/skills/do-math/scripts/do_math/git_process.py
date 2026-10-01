"""Real Git backend port: the git executable, isolated from user configuration and hooks.

Objects are written in process as loose objects, the form Git itself writes;
the git executable reads them back.
"""
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import zlib

from .ports.git_backend import GitBackendError
from .storage_finish_git_output import parse_object_info, parse_read_objects


class GitProcess:
    def __init__(self, *, environment, run=subprocess.run):
        self._run_process = run
        self.environment = environment
        self._git_dirs = {}
        self._objects = {}

    def _run(self, repository, *arguments, input=None):
        repository = Path(repository).absolute()
        # Until Git reports its directory, the work tree stands in for it (hooks path).
        git_dir = self._git_dirs.get(repository, repository)
        environment = dict(self.environment)
        environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_OPTIONAL_LOCKS": "0"})
        return self._run_process(
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
        key = Path(repository).absolute()
        self._git_dirs[key] = Path(facts[0]).absolute()
        # --git-path is relative to the work tree unless Git reports it absolute
        # (a linked worktree's common directory, GIT_OBJECT_DIRECTORY).
        self._objects[key] = (facts[1].strip(), key / facts[2].strip())
        return facts[0], facts[1].strip(), facts[2].strip()

    def write_object(self, repository, kind, body):
        """Store one loose object as installed Git does by default, returning its OID.

        The OID hashes ``"<kind> <size>\\0"`` and the exact body, so writing is
        idempotent: an existing loose object is kept, and a concurrent writer of
        the same object only loses the final rename. Like Git for Windows
        (``core.fsyncObjectFiles=true`` by default) each new object is flushed
        before its final name appears; the directory is not, as Git does not.
        """
        key = Path(repository).absolute()
        if key not in self._objects:
            self.describe(repository)  # GitStateStore has already described it; no second git process then
        object_format, directory = self._objects[key]
        data = b"%s %d\0" % (kind.encode("ascii"), len(body)) + body
        oid = hashlib.new(object_format, data).hexdigest()
        target = directory / oid[:2] / oid[2:]
        if target.exists():
            return oid
        target.parent.mkdir(exist_ok=True)
        # Git's prefix, so ``git prune`` removes a temporary a crash leaves behind.
        descriptor, temporary = tempfile.mkstemp(prefix="tmp_obj_", dir=target.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(zlib.compress(data, 1))  # core.looseCompression default
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o444)  # Git's mode for loose objects (read-only on Windows)
            try:
                os.rename(temporary, target)
            except FileExistsError:
                pass  # Windows: another writer stored the identical object first
        finally:
            if os.path.lexists(temporary):
                os.chmod(temporary, stat.S_IREAD | stat.S_IWRITE)
                os.unlink(temporary)
        return oid

    def object_info(self, repository, specs):
        if not specs:
            return []
        arguments = ("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)")
        raw = self._checked(repository, *arguments,
                            input="".join(spec + "\n" for spec in specs).encode("utf-8"))
        return parse_object_info(specs, raw)

    def read_objects(self, repository, specs):
        if not specs:
            return []
        raw = self._checked(repository, "cat-file", "--batch",
                            input="".join(spec + "\n" for spec in specs).encode("utf-8"))
        return parse_read_objects(specs, raw)

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
