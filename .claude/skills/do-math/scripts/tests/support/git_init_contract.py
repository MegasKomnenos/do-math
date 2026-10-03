"""Paired initialization/existence expectations; no product CLI or store replacement."""
from pathlib import Path
import tempfile

from support.fakes.git_backend import make_repository


class GitInitContract:
    def world(self, object_format):
        """Context manager yielding a backend with that external init default."""
        raise NotImplementedError

    def test_git_init_creates_and_reopens_with_external_default_format(self):
        for object_format in ('sha1', 'sha256'):
            with self.subTest(format=object_format), tempfile.TemporaryDirectory() as directory:
                repository = Path(directory) / 'repository'
                repository.mkdir()  # CLI owns this prerequisite, not the port.
                with self.world(object_format) as backend:
                    self.assertFalse(backend.repository_exists(repository))
                    self.assertIs(backend.initialize_repository(repository), True)
                    self.assertIs(backend.repository_exists(repository), True)
                    self.assertEqual(backend.describe(repository)[1], object_format)
                    blob = backend.write_object(repository, 'blob', b'initialized\n')
                    self.assertEqual(len(blob), 64 if object_format == 'sha256' else 40)
                with self.world(object_format) as reopened:
                    self.assertIs(reopened.repository_exists(repository), True)
                    self.assertEqual(reopened.describe(repository)[1], object_format)

    def test_git_init_missing_cwd_and_file_return_false_without_mkdir(self):
        with tempfile.TemporaryDirectory() as directory, self.world('sha1') as backend:
            root = Path(directory)
            file = root / 'file'
            file.write_bytes(b'not a directory')
            for repository in (root / 'missing', file):
                self.assertIs(backend.initialize_repository(repository), False)
                self.assertIs(backend.repository_exists(repository), False)
            self.assertFalse((root / 'missing').exists())

    def test_git_init_existing_repository_population(self):
        for object_format in ('sha1', 'sha256'):
            with tempfile.TemporaryDirectory() as directory, self.world(object_format) as backend:
                root = Path(directory)
                repository = make_repository(root / 'repository', object_format)
                child = repository / 'nested'
                child.mkdir()
                for path in (repository, child, repository / '.git'):
                    self.assertIs(backend.repository_exists(path), True)
                # Separate Git directory and gitfile, also the shape used by submodules.
                separate = root / 'separate'
                (repository / '.git').rename(separate)
                (repository / '.git').write_text('gitdir: ../separate\n', encoding='utf-8')
                for path in (repository, child, separate):
                    self.assertIs(backend.repository_exists(path), True)
                linked = root / 'linked'
                linked.mkdir()
                admin = separate / 'worktrees' / 'linked'
                admin.mkdir(parents=True)
                (admin / 'HEAD').write_text('ref: refs/heads/main\n', encoding='ascii')
                (admin / 'commondir').write_text('../..\n', encoding='ascii')
                (admin / 'gitdir').write_text(str(linked / '.git') + '\n', encoding='utf-8')
                (linked / '.git').write_text('gitdir: ' + str(admin) + '\n', encoding='utf-8')
                self.assertIs(backend.repository_exists(linked), True)
                bare = make_repository(root / 'bare-holder', object_format) / '.git'
                bare.rename(root / 'bare')
                config = root / 'bare/config'
                config.write_text(config.read_text(encoding='ascii').replace('bare = false', 'bare = true'),
                                  encoding='ascii')
                self.assertIs(backend.repository_exists(root / 'bare'), True)

    def test_git_init_objects_directory_alone_is_not_repository(self):
        with tempfile.TemporaryDirectory() as directory, self.world('sha1') as backend:
            root = Path(directory)
            (root / '.git/objects').mkdir(parents=True)
            self.assertIs(backend.repository_exists(root), False)
            (root / '.git/HEAD').write_bytes(b'ref: refs/heads/main\n')
            self.assertIs(backend.repository_exists(root), False)
            (root / '.git/refs').mkdir()
            self.assertIs(backend.repository_exists(root), True)
