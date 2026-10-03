"""Real side of the Git backend port contract: the git process."""
import unittest
import subprocess
import shutil

from support.port_contracts.git_backend import GitBackendContract
from do_math.wiring import real_ports


class GitProcessBackendContract(GitBackendContract, unittest.TestCase):
    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).git_backend

    def configure_project(self, *, head=True):
        (self.repo / 'research').mkdir(exist_ok=True)
        with (self.repo / '.git/config').open('a', encoding='utf-8') as config:
            config.write('\n[core]\n\tautocrlf = false\n\tabbrev = 7\n')
        if head:
            (self.repo / '.git/refs/heads/main').write_text(self.first + '\n', encoding='ascii')
            # Independent actual Git fixture, outside the adapter under test.
            subprocess.run(['git', '-C', str(self.repo), 'read-tree', '--reset', '-u', 'HEAD'],
                           check=True, capture_output=True)

    def declare_project_diff(self, raw):
        pass  # The real adapter observes the changed file through Git.

    def remove_project(self):
        shutil.rmtree(self.repo / '.git')


class GitProcessSha256BackendContract(GitProcessBackendContract):
    object_format = 'sha256'

    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).git_backend


if __name__ == '__main__':
    unittest.main()
