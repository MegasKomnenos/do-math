"""The public command line on a real Git repository (``cli.main``, layer 3), for the engine region's CLI tests.

``cli.main`` and ``cli.execute`` open the repository and the engine with the
ports explicitly assembled at the boundary, so a command that reads or
writes an instance runs the real Git process. Tests that need one live
with the boundary tests, as ``boundary/test_cli_file_reads.py`` does.

- ``cli_instance(root, shared)``: a ``research_fixtures.restore_template`` build
  of one instance the CLI's ``init`` created: repository ``root / 'repository'``,
  workspace ``root / 'workspace'`` and the configuration ``init`` read,
  ``root / 'operator-disabled.json'`` (no scheduled operator, so ``init``
  installs no operator schedule). It returns the ``init`` result.
- ``body(completed)``: the response envelope's ``result`` or ``error`` body,
  after checking the envelope's invariants: wire version 5, the envelope's exit
  code equals the process's, and exactly one of ``result`` and ``error``.
- ``CliInstanceTest``: a test case on a fresh copy of ``cli_instance`` with
  ``root``, ``repository``, ``workspace``, ``instance``, ``initial`` (the
  ``init`` result), ``cli(*arguments)`` (``research_fixtures.run_cli`` in
  ``root``, in this process), ``instance_args()``, and the same instance
  outside the CLI on the product's real ports: ``store()`` (its
  ``ResearchRepository``), ``control(action, **options)`` (the public
  ``control``) and ``engine()`` (a ``ResearchEngine``).
"""
import json
import unittest

from do_math.engine import ResearchEngine, control
from do_math.repository import ResearchRepository
from do_math.wiring import real_ports
from support.fakes.git_backend import make_repository
from support.cli_inputs import run_cli
from support.cli_images import initialized_cli


def body(completed):
    """The envelope body of a CLI run, after its invariants hold."""
    envelope = json.loads(completed.stdout)
    problems = []
    if envelope.get('schema_version') != 5:
        problems.append('wire version is not 5')
    if envelope.get('exit_code') != completed.returncode:
        problems.append('envelope exit code differs from the process exit code')
    if ('result' in envelope) == ('error' in envelope):
        problems.append('the envelope must carry exactly one of result and error')
    if problems:
        raise AssertionError('; '.join(problems) + ': ' + completed.stdout)
    return envelope.get('result', envelope.get('error'))


def cli_instance(root):
    """``restore_template`` build: one instance the CLI's ``init`` created; returns its result."""
    repository = make_repository(root / 'repository')
    configuration = root / 'operator-disabled.json'
    configuration.write_text(json.dumps({'operator_enabled': False}), encoding='utf-8')
    initialized = run_cli('init', '--repository', str(repository), '--workspace', str(root / 'workspace'),
                          '--goal', 'Prove a small theorem', '--title', 'Small theorem',
                          '--config-file', str(configuration), cwd=root)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stdout + initialized.stderr)
    return body(initialized)


class CliInstanceTest(unittest.TestCase):
    def setUp(self):
        self.root, self.initial = initialized_cli('existing')
        self.repository = self.root / 'repository'
        self.workspace = self.root / 'workspace'
        self.operator_disabled = self.root / 'operator-disabled.json'
        self.instance = self.initial['instance_id']

    def cli(self, *arguments):
        return run_cli(*arguments, cwd=self.root)

    def instance_args(self):
        return ('--repository', str(self.repository), '--instance', self.instance)

    def store(self, instance=None):
        from support.entry import entry
        _entry = entry()
        ports = real_ports(environment=_entry.environment)
        return ResearchRepository(self.repository, instance or self.instance, backend=ports.git_backend, clock=ports.clock)

    def control(self, action, **options):
        from support.entry import entry
        _entry = entry()
        return control(self.repository, self.instance, action, ports=real_ports(environment=_entry.environment), **options, host_id=_entry.host_id)

    def engine(self):
        from support.entry import entry
        _entry = entry()
        return ResearchEngine(self.repository, self.instance, ports=real_ports(environment=_entry.environment), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
