"""In-process side of the shared Git initialization contract."""
from contextlib import contextmanager
import unittest

from support.fakes.git_backend import InProcessGit
from support.git_init_contract import GitInitContract


class FakeGitInitContract(GitInitContract, unittest.TestCase):
    @contextmanager
    def world(self, object_format):
        yield InProcessGit(init_object_format=object_format)
