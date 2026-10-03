"""Actual Git side: external default is a fixture fact, never a product argument."""
from contextlib import contextmanager
import os
import unittest
from unittest.mock import patch

from do_math.git_process import GitProcess
from support.git_init_contract import GitInitContract


class RealGitInitContract(GitInitContract, unittest.TestCase):
    @contextmanager
    def world(self, object_format):
        environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        environment.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                           GIT_DEFAULT_HASH=object_format, GIT_TEMPLATE_DIR='')
        with patch.dict(os.environ, environment, clear=True):
            yield GitProcess(environment=environment)
