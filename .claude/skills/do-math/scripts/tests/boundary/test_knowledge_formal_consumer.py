"""The owner's formal check with the installed Lean, the installed compiler's approved identity, and the record query.

``FormalConsumerLeanTests`` runs the owner's formal check on a Sim whose active
trust environment adopts the installed Lean and whose Lean seam starts it as a
real process (``support.knowledge_installed_lean``); the owner's continuation
records, publishes and settles the result through the storage contract. The
instance configures no Lean command and the host port finds the installed one,
so the configured command differs from the approved command, as the legacy
fixture's did (조사 K-42): an owner that handed the verifier the configured
command would not verify. The Lean worker's Job is the Jobs port fake's (the
verifier gets ``jobs=sim.ports.jobs``); ``InstalledCompilerTests`` and
``boundary.test_knowledge_lean_verifier`` run ``verify_lean`` in real Jobs. The
legacy tests ran ``_formal`` on ``knowledge_fixtures.formal_boundary_engine``, a
bare engine whose admission, storage, registration, activity and review start
were autospec doubles, with ``governance.authorize`` patched to allow. Here the
verifier that records its arguments and runs ``verify_lean`` is
``engine_lifecycle.recorded_verifier``; engine calls are observed as they
start (``ObservedCalls``). Authority, clock, persistence and noncompiler build
attestations are synthetic; no full Mathlib build is claimed.

``InstalledCompilerTests`` runs ``verify_lean`` on the installed Lean in real
Jobs. ``ImportedRecordQueryTests`` reads a Sim's repository with a real ``git``:
the record query opens the repository with the real Git backend.
"""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from do_math import formal, knowledge_records as kr
from do_math.engine import query_records
from do_math.knowledge import assess_use
from do_math.local_host import LocalHost
from do_math.trust_validation import EnvironmentUnavailable, require_active_environment
from support.knowledge_builders import knowledge_candidate
from support.provider_inputs import actual_command
from support.engine_lifecycle import applied, clear_work, only, recorded_verifier
from support.knowledge_installed_lean import adopt_installed, installed_toolchain
from support.provider_probes import ObservedCalls
from support.knowledge_formal_engine import ReturnedValues
from do_math.trust_validation import verify_formal
from support.review_sim import export_objects
from support.sim import Sim
from test_categories import test_group as category


def require_installed_lean():
    if not Path(actual_command()[0]).is_file():
        raise unittest.SkipTest('portable Lean is not installed')


def imported(sim, candidate):
    clear_work(sim)
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
    kid = next(kid for kid, row in sim.instance['knowledge'].items() if row['title'] == candidate['title'])
    only(sim, 'formal_check')
    sim.engine._save()
    return kid


def formal_execution(sim, kid):
    [execution] = [row for row in sim.runtime['executions'].values()
                   if row.get('role') == 'formal_check' and row['action'].get('target') == kid]
    return execution


def stored_result(sim, execution):
    return json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head))


def after_compile(sim, change):
    """Change external state when the actual compiler exits, at its spawn seam."""
    spawn = sim.lean.spawn

    def start(command, **options):
        process = spawn(command, **options)
        wait = process.wait

        def completed(timeout=None):
            code = wait(timeout)
            change()
            return code
        process.wait = completed
        return process
    sim.lean.spawn = start


@category('lean')
class FormalConsumerLeanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_installed_lean()
        cls.baseline = installed_toolchain()

    def start(self, toolchain=None):
        """A Sim on the installed Lean (``toolchain``, default the observed one); returns ``(sim, environment)``."""
        sim = Sim.activated()
        environment = adopt_installed(sim, toolchain or self.baseline, sim.root / 'installed')
        return sim, environment

    def test_actual_approved_command_seals_result_and_ends_execution(self):
        sim, environment = self.start()
        results = self.enterContext(ReturnedValues(verify_formal)).values
        calls = self.enterContext(recorded_verifier())
        kid = imported(sim, knowledge_candidate())
        engine = sim.engine
        with ObservedCalls(capture={'review': lambda arguments: arguments['knowledge_id'],
                                    'settle': lambda arguments: arguments['execution_id']},
                           review=engine._start_identity_review, settle=engine._settle_activity) as observed:
            sim.step()
        approved = sim.instance['trust_environments'][environment]['toolchain']
        record = sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]
        self.assertEqual(record['publication_state'], 'accepted')
        self.assertEqual(record['verification']['toolchain'], approved)
        execution = formal_execution(sim, kid)
        result = stored_result(sim, execution)
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(len(results), 1)
        self.assertIn('True.intro', result['dependency_closure']['truth'])
        # K-42: the configured command (none; the host found Lean) differs from the approved one, and the
        # verifier received and the worker started the approved command, not the configured one.
        self.assertIsNone(sim.instance['config']['lean_command'])
        self.assertNotEqual(sim.instance['config']['lean_command'], approved['configured_command'])
        self.assertEqual([arguments['lean_command'] for arguments in calls], [approved['configured_command']])
        [started] = sim.lean.commands
        self.assertEqual(started[:len(approved['configured_command'])], approved['configured_command'])
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
        self.assertEqual([row['id'] for row in sim.runtime['executions'].values() if row['status'] != 'ended'], [])
        self.assertEqual([knowledge_id for _, knowledge_id in observed.calls['review']], [kid])
        self.assertEqual([execution_id for _, execution_id in observed.calls['settle']], [execution['id']])

    def test_actual_exact_source_and_compiler_names_reach_authoritative_consumer_and_artifact(self):
        source = 'theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
        names = ['\u212a', 'K']
        sim, _ = self.start()
        results = self.enterContext(ReturnedValues(verify_formal)).values
        calls = self.enterContext(recorded_verifier())
        kid = imported(sim, knowledge_candidate(lean_code=source, declaration_names=names))
        sim.step()
        self.assertEqual([arguments['source'].encode() for arguments in calls], [source.encode()])
        self.assertEqual([arguments['declarations'] for arguments in calls], [names])
        self.assertEqual(results[0]['status'], 'verified', results[0].get('reason'))
        record = sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]
        self.assertEqual(record['publication_state'], 'accepted')
        self.assertEqual(record['verification']['declarations'], names)
        self.assertEqual(record['verification']['declaration_evidence'], results[0]['declaration_evidence'])
        self.assertEqual(stored_result(sim, formal_execution(sim, kid)), results[0])

    def test_identity_change_after_actual_compile_is_caught_at_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            # A copied checker is the one identity file this test may change.
            copied = Path(directory) / 'checked-checker/scripts/do_math'
            shutil.copytree(Path(formal.__file__).parent, copied, ignore=shutil.ignore_patterns('__pycache__'))
            checker = (copied / 'formal.py').resolve()
            sim, environment = self.start({**deepcopy(self.baseline), 'verifier_path': str(checker)})
            results = self.enterContext(ReturnedValues(verify_formal)).values

            def change():
                recorded = Path(sim.engine.instance['trust_environments'][environment]['toolchain']['verifier_path'])
                self.assertTrue(recorded.resolve().is_relative_to(Path(directory).resolve()))
                checker.write_text('changed after actual compilation', encoding='utf-8')
            after_compile(sim, change)
            kid = imported(sim, knowledge_candidate())
            sim.step()
            # Nothing is re-observed after compiling; the formal result itself is accepted.
            self.assertEqual((results[0]['status'], stored_result(sim, formal_execution(sim, kid))['status']),
                             ('verified', 'verified'))
            self.assertEqual(sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]['publication_state'], 'accepted')
            with self.assertRaises(EnvironmentUnavailable) as caught:
                require_active_environment(sim.instance, sim.runtime, current_identity=True, host=LocalHost(clock=sim.ports.clock, environment=sim.environment, jobs=sim.ports.jobs))
            self.assertIn('approved toolchain file changed: ' + str(checker), str(caught.exception))
            self.assertEqual(sim.instance['active_trust_environment'], environment)

    def test_current_environment_change_after_actual_compile_prevents_publication(self):
        sim, environment = self.start()
        results = self.enterContext(ReturnedValues(verify_formal)).values

        def change():
            sim.engine.instance['trust_environments'][environment]['source_ref'] = 'different-current-approval'
        after_compile(sim, change)
        kid = imported(sim, knowledge_candidate())
        sim.step()
        self.assertEqual(results[0]['status'], 'verified')
        execution = formal_execution(sim, kid)
        result = stored_result(sim, execution)
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(result['reason'], 'trust_environment_changed')
        self.assertEqual(sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]['verification'], {})
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))


@category('lean')
class InstalledCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_installed_lean()
        cls.baseline = installed_toolchain()

    def test_actual_compile_reuses_pinned_version_observation_without_reprobing(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        approved = deepcopy(self.baseline)
        # Version text is a pinned observation; executable identities, rather
        # than a second process's display string, bind the approved compiler.
        approved['version'] = 'pinned approval observation'
        with tempfile.TemporaryDirectory() as d, \
                ObservedCalls(capture={'job': lambda arguments: list(arguments['command'])}, job=formal._job_run) as observed:
            result = formal.verify_lean(source=knowledge_candidate()['lean_code'], declarations=['truth'],
                workspace=Path(d), lean_command=actual_command(), expected_toolchain=approved, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertEqual(result['status'], 'verified', result)
        self.assertEqual(result['toolchain'], approved)
        self.assertEqual(len(observed.calls['job']), 1)
        self.assertNotIn('--version', observed.calls['job'][0][1])
        self.assertIn('True.intro', result['dependency_closure']['truth'])

    def test_actual_executable_identity_different_from_approved_input_is_rejected(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        approved = deepcopy(self.baseline)
        approved['sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as d:
            result = formal.verify_lean(source=knowledge_candidate()['lean_code'], declarations=['truth'],
                workspace=Path(d), lean_command=actual_command(), expected_toolchain=approved, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['reason'], 'approved toolchain changed before execution')
        self.assertIsNone(result['command'])


class ImportedRecordQueryTests(unittest.TestCase):
    def test_imported_record_query_has_snapshot_evidence(self):
        """The query half of the legacy import test: the imported record's row names the published head and bytes."""
        from support.entry import entry
        from do_math.wiring import real_ports
        _entry = entry()
        _entry.ports = real_ports(environment=_entry.environment)
        sim = Sim.activated()
        data = knowledge_candidate()
        data.update(lean_code='theorem \u212a : True := True.intro\r\ntheorem K : True := True.intro\n-- e\u0301\n',
                    declaration_names=['\u212a', 'K'])
        clear_work(sim)
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': data})
        kid = next(kid for kid, row in sim.instance['knowledge'].items() if row['title'] == data['title'])
        head = sim.engine.head
        export_objects(sim)
        page = query_records(sim.repository, sim.instance_id, kind='knowledge', backend=_entry.ports.git_backend, clock=_entry.ports.clock)
        row = next(r for r in page['items'] if r['record']['id'] == kid)
        self.assertEqual(row['snapshot'], head)
        stored = sim.engine.store.read_record(kid, head)
        self.assertIn(row['path'], [stored['path']])
        self.assertEqual(row['sha256'], stored['sha256'])
        self.assertEqual(kr.proposal_view(sim.instance, kid)['lean_code'].encode(), data['lean_code'].encode())
        self.assertFalse(assess_use(sim.instance['knowledge'][kid], sim.instance)['valid'])


if __name__ == '__main__':
    unittest.main()
