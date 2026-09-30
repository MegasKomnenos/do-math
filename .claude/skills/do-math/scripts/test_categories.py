"""Shards and isolation labels for do-math tests.

``SHARDS`` is the one list of which test module runs in which shard;
``run_tests.py`` refuses to run while a ``tests/test_*.py`` module is missing
from it or it names a module that does not exist. The shard time targets and
when to run what are in ``tests/시험-지침.md``.

``test_group('lean')`` and ``test_group('resource')`` mark tests that call the
real Lean toolchain or manage real process lifetimes and resources; the runner
runs them per class in an owned Windows Job with a deadline. A label goes on
the class when every test in it needs isolation, otherwise on each such method;
a method's label overrides its class's.
"""
from pathlib import Path

SHARDS = {name: frozenset(modules.split()) for name, modules in {
    'foundation': '''
        test_context_store
        test_environment_validation
        test_execution_window
        test_git_store test_installation_discovery test_model_metadata_boundary test_owned_job_children test_preparation_cache test_provider_final_contract test_reference_catalog test_repair_execution test_standalone test_supervisor_recovery
        test_test_runner test_trust_continuation
        ''',
    'host': '''
        test_diagnosed_installation_recovery
        test_formal_runtime test_host_resources test_lean_preview
        test_machine_parallel test_operator test_probe_cli
        test_provider_wait
        test_worker_temporary_outputs''',
    'lifecycle': '''
        test_checkpoint_persistence test_engine test_formal_engine
        test_lifecycle_engine
        test_live_observation
         test_provider_recovery test_role_input
        ''',
    'research': '''
        test_purpose_engine test_research_recovery test_session_scheduler''',
    'review': '''
        test_submission_tools''',
    'academic': '',
}.items()}
LABELS = ('lean', 'resource')
_SHARD_OF = {module: name for name, modules in SHARDS.items() for module in modules}


def unregistered_modules(tests_dir):
    """(test modules on disk missing from SHARDS, SHARDS entries with no module on disk)."""
    present = {path.stem for path in Path(tests_dir).glob('test_*.py')}
    return sorted(present - _SHARD_OF.keys()), sorted(_SHARD_OF.keys() - present)


def test_group(label):
    if label not in LABELS:
        raise ValueError('unknown test label: ' + str(label))
    def decorate(target):
        target.do_math_test_group = label
        return target
    return decorate


def isolation_for(test):
    """'lean' or 'resource' when the test must run isolated, else None; a method label overrides its class."""
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    return getattr(method, 'do_math_test_group', None) or getattr(type(test), 'do_math_test_group', None)


def shard_for(test):
    return _SHARD_OF[type(test).__module__.split('.')[-1]]
