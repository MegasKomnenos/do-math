"""Git port observation and another writer's commit, for storage tests over the in-process Git fake.

- ``ObservedGit``: the Git fake that lists every port operation it answers.
  Every git process the real backend runs belongs to one port operation, so a
  test that finds no operation also knows no process ran, and one ``list_tree``
  is one ``ls-tree`` (the boundary tests check the real backend's processes).
- ``rewrite_commit(repository, head, changes)``: a state commit made by a
  writer that is not do-math, for example damaged or replaced artifact bytes.
  ``GitStateStore.publish`` refuses to change an existing artifact bundle, so
  the product cannot make this state itself; it is what a later reader finds
  after the storage changed underneath.
"""
from support.fakes.git_backend import InProcessGit

ARTIFACTS = ':runtime/artifacts/'


class ObservedGit(InProcessGit):
    """``calls``: ``(operation, arguments)`` for each port operation, the repository argument left out.

    ``before(operation, arguments)``, when set, runs before each operation is answered.
    """

    def __init__(self, objects=None):
        super().__init__(objects)
        self.calls = []
        self.before = None

    def _observe(self, operation, arguments):
        self.calls.append((operation, arguments))
        if self.before is not None:
            self.before(operation, arguments)

    def operations(self, since=0, *, writes=False):
        """The operation names from call ``since`` on; object writes are left out unless ``writes``."""
        return [name for name, _ in self.calls[since:] if writes or name != 'write_object']

    def artifact_specs(self, operation, since=0):
        """For each ``operation`` call from ``since`` on that names artifact paths, its list of specs."""
        return [list(arguments[0]) for name, arguments in self.calls[since:]
                if name == operation and any(ARTIFACTS in spec for spec in arguments[0])]

    def describe(self, repository):
        self._observe('describe', ())
        return super().describe(repository)

    def write_object(self, repository, kind, body):
        self._observe('write_object', (kind,))
        return super().write_object(repository, kind, body)

    def object_info(self, repository, specs):
        self._observe('object_info', (list(specs),))
        return super().object_info(repository, specs)

    def read_objects(self, repository, specs):
        self._observe('read_objects', (list(specs),))
        return super().read_objects(repository, specs)

    def ref_oid(self, repository, ref):
        self._observe('ref_oid', (ref,))
        return super().ref_oid(repository, ref)

    def update_ref(self, repository, ref, new, old):
        self._observe('update_ref', (new, old))
        return super().update_ref(repository, ref, new, old)

    def list_tree(self, repository, commit):
        self._observe('list_tree', (commit,))
        return super().list_tree(repository, commit)

    def first_parent_line(self, repository, parent, head):
        self._observe('first_parent_line', (parent, head))
        return super().first_parent_line(repository, parent, head)


def rewrite_commit(repository, head, changes):
    """Commit ``changes`` (path: bytes, or None to remove) on ``head`` as another writer, and move the ref to it.

    The store's own tree and commit writer builds the objects, without its
    publication checks; the ref moves by the same compare-and-swap.
    """
    git = repository._store
    tree, _ = git._write_tree(git._tree(head).directories, changes)
    commit = git._write_commit(tree, head)
    if not git._backend.update_ref(git.repository, git.ref, commit, head):
        raise AssertionError('the ref moved while another writer committed')
    return commit
