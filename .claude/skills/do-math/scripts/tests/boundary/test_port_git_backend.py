"""Real side of the Git backend port contract: the git process."""
import unittest

from contracts.test_port_git_backend import GitBackendContract
from do_math.wiring import real_ports


class GitProcessBackendContract(GitBackendContract, unittest.TestCase):
    def make(self):
        return real_ports().git_backend


class GitProcessSha256BackendContract(GitBackendContract, unittest.TestCase):
    object_format = 'sha256'

    def make(self):
        return real_ports().git_backend


if __name__ == '__main__':
    unittest.main()
