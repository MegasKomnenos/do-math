"""In-process Git backend fake: objects in memory, loose objects and ref files on disk.

Objects written through the port stay in ``objects`` (one map per Git
directory), which stands for the disk: they outlive an engine restart that keeps
the ports, and a Sim template hands a copy to each restore. They are never
files, so a test pays no file write, copy or removal per object; objects are
immutable, so a copy of the map shares the bytes. Reads also find loose objects
already on disk (repositories a test wrote without the port); packfiles are not
read. Refs are plain files under ``.git/refs``; ``update_ref`` is a
compare-and-swap guarded by an exclusive ``<ref>.lock`` file, as Git's own ref
transaction is.
"""
import hashlib
import os
import re
from pathlib import Path
import zlib


from do_math.ports.git_backend import GitBackendError


class InProcessGit:
    def __init__(self, objects=None):
        self.objects = objects if objects is not None else {}

    def _git_dir(self, repository):
        repository = Path(repository)
        return repository / '.git' if (repository / '.git').is_dir() else repository

    def _format(self, git_dir):
        config = (git_dir / 'config').read_text(encoding='utf-8') if (git_dir / 'config').exists() else ''
        return 'sha256' if 'objectformat = sha256' in config.replace('\t', ' ') else 'sha1'

    def describe(self, repository):
        git_dir = self._git_dir(repository)
        if not (git_dir / 'objects').is_dir():
            raise GitBackendError(f'not a git repository: {repository}')
        return str(git_dir.absolute()), self._format(git_dir), os.path.relpath(git_dir / 'objects', Path(repository))

    def _object(self, git_dir, oid):
        stored = self.objects.get(str(git_dir.absolute()), {}).get(oid)
        if stored is not None:
            return stored
        path = git_dir / 'objects' / oid[:2] / oid[2:]
        if not path.is_file():
            return None
        raw = zlib.decompress(path.read_bytes())
        header, _, body = raw.partition(b'\0')
        kind, size = header.decode('ascii').split(' ')
        assert int(size) == len(body)
        return kind, body

    def _entries(self, git_dir, tree_oid):
        width = 32 if self._format(git_dir) == 'sha256' else 20
        body = self._object(git_dir, tree_oid)[1]
        entries, offset = [], 0
        while offset < len(body):
            space = body.index(b' ', offset)
            nul = body.index(b'\0', space)
            mode, name = body[offset:space].decode('ascii'), body[space + 1:nul]
            oid = body[nul + 1:nul + 1 + width].hex()
            entries.append((mode, 'tree' if mode == '40000' else 'blob', oid, name))
            offset = nul + 1 + width
        return entries

    def _commit_field(self, git_dir, oid, field):
        body = self._object(git_dir, oid)[1].decode('utf-8')
        return [line.split(' ', 1)[1] for line in body.split('\n\n', 1)[0].split('\n') if line.startswith(field + ' ')]

    def _resolve(self, git_dir, spec):
        revision, _, path = spec.partition(':')
        if revision.startswith('refs/'):
            ref = git_dir / revision
            oid = ref.read_text(encoding='ascii').strip() if ref.is_file() else None
        else:
            oid = revision
        if oid is None or self._object(git_dir, oid) is None:
            return None
        if not _:
            return oid
        kind, _body = self._object(git_dir, oid)
        current = self._commit_field(git_dir, oid, 'tree')[0] if kind == 'commit' else oid
        for part in path.split('/'):
            match = [entry for entry in self._entries(git_dir, current) if entry[3] == part.encode('utf-8')]
            if not match:
                return None
            current = match[0][2]
        return current

    def write_object(self, repository, kind, body):
        git_dir = self._git_dir(repository)
        data = kind.encode('ascii') + b' %d\0' % len(body) + body
        oid = hashlib.new(self._format(git_dir), data).hexdigest()
        self.objects.setdefault(str(git_dir.absolute()), {}).setdefault(oid, (kind, bytes(body)))
        return oid

    def object_info(self, repository, specs):
        git_dir, result = self._git_dir(repository), []
        for spec in specs:
            oid = self._resolve(git_dir, spec)
            found = self._object(git_dir, oid) if oid else None
            result.append((oid, found[0], len(found[1])) if found else None)
        return result

    def read_objects(self, repository, specs):
        git_dir = self._git_dir(repository)
        found = [self._object(git_dir, oid) if oid else None for oid in (self._resolve(git_dir, s) for s in specs)]
        return [(item[0], item[1]) if item else None for item in found]

    def ref_oid(self, repository, ref):
        path = self._git_dir(repository) / ref
        if not path.is_file():
            return None
        raw = path.read_bytes().strip()
        width = 64 if self._format(self._git_dir(repository)) == 'sha256' else 40
        if re.fullmatch(rb'[0-9a-fA-F]{%d}' % width, raw) is None:
            raise GitBackendError('broken reference: ' + ref)
        return raw.decode('ascii').lower()

    def update_ref(self, repository, ref, new, old):
        path = self._git_dir(repository) / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = path.with_name(path.name + '.lock')
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        try:
            current = path.read_text(encoding='ascii').strip() if path.is_file() else None
            if current != old:
                return False
            os.write(descriptor, (new + '\n').encode('ascii'))
            os.close(descriptor)
            descriptor = None
            os.replace(lock, path)
            return True
        finally:
            if descriptor is not None:
                os.close(descriptor)
                os.unlink(lock)

    def list_tree(self, repository, commit):
        git_dir = self._git_dir(repository)
        rows = []

        def walk(tree_oid, prefix):
            for mode, kind, oid, name in self._entries(git_dir, tree_oid):
                path = prefix + name
                rows.append((mode, kind, oid, path))
                if kind == 'tree':
                    walk(oid, path + b'/')
        walk(self._commit_field(git_dir, commit, 'tree')[0], b'')
        return rows

    def first_parent_line(self, repository, parent, head):
        git_dir, line, current = self._git_dir(repository), [], head
        while current and current != parent:
            line.append(current)
            parents = self._commit_field(git_dir, current, 'parent')
            current = parents[0] if parents else None
        return list(reversed(line)) if current == parent else []


def make_repository(root, object_format='sha1'):
    """A new repository at ``root`` without a git process: the minimal layout Git reads."""
    git = Path(root) / '.git'
    (git / 'objects').mkdir(parents=True)
    (git / 'refs' / 'heads').mkdir(parents=True)
    (git / 'HEAD').write_bytes(b'ref: refs/heads/main\n')
    extensions = '[extensions]\n\tobjectformat = sha256\n' if object_format == 'sha256' else ''
    version = 1 if object_format == 'sha256' else 0
    (git / 'config').write_text(f'[core]\n\trepositoryformatversion = {version}\n\tbare = false\n{extensions}',
                                encoding='utf-8')
    return Path(root)



def make_fake(objects=None):
    return InProcessGit(objects)
