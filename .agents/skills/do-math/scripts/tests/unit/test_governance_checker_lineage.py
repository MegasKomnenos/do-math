"""실제 해석 생산자의 원문·질문·봉인 계약을 한 필드씩 검증한다."""
from copy import deepcopy
import re
from pathlib import Path
import tempfile
import unittest

from do_math import governance as gov
from support.governance_sim import checked_sim, checked_bundle

class GovernanceCheckerLineageTests(unittest.TestCase):
    def test_shared_context_ancestor_is_yielded_once_without_a_revisit_error(self):
        from support.governance_sim import returned
        sim = checked_sim()
        for identifier, origins in (('EX-root', []), ('EX-left', ['EX-root']),
                                    ('EX-right', ['EX-root']), ('EX-join', ['EX-left', 'EX-right'])):
            execution = returned(sim.engine, {'id': 'AC-' + identifier, 'role': 'maintenance'}, identifier)
            execution['context_origin'] = origins
        before = deepcopy(sim.runtime)
        rows = list(gov.execution_lineage(sim.runtime, 'EX-join', ('context_origin',)))
        self.assertEqual([identifier for identifier, _ in rows],
                         ['EX-join', 'EX-right', 'EX-root', 'EX-left'])
        self.assertEqual(dict(rows), {identifier: sim.runtime['executions'][identifier]
                                    for identifier, _ in rows})
        self.assertEqual(sim.runtime, before)

    def test_stored_check_binds_the_preserved_import_without_execution_session_aliases(self):
        from support.storage_records import record_store
        sim = checked_sim()
        reader = record_store(sim.repository, instance_id=sim.instance_id,
                              backend=sim.ports.git_backend, clock=sim.clock)
        _, _, runtime = reader.load(sim.engine.head)
        bundle = runtime['intent_imports'][checked_bundle(sim)['id']]
        checker = runtime['executions'][bundle['check']['execution_id']]
        self.assertEqual(checker['intent_import_sha256'], bundle['sha256'])
        self.assertNotEqual(checker['id'], bundle['execution_id'])
        self.assertIsNone(checker['continuation_of'])
        self.assertEqual(checker['context_origin'], [])
        self.assertIsNone(gov.validate_independent_execution(runtime, checker['id'], [bundle['execution_id']]))
        for identifier in (checker['id'], bundle['execution_id']):
            self.assertFalse(set(runtime['executions'][identifier]) & {'conversation_id', 'provider_session_id'})

    def test_actual_worker_requests_start_fresh_conversations_for_both_providers(self):
        from contracts.pairs import worker_request_run
        from do_math.worker_request import check_codex_request, check_claude_request
        with tempfile.TemporaryDirectory() as directory:
            for provider, receive in (('codex', check_codex_request), ('claude', check_claude_request)):
                run = worker_request_run(Path(directory) / provider, provider, identity=True,
                    limits=False, control=True, scholarly=False, only=False)
                command = run['jobs'].cli.calls[0]['command']
                for field in ('execution_id', 'profile_ref', 'control_binding'):
                    self.assertEqual(run['request'][field], run['staged'][field])
                self.assertIn('--ephemeral' if provider == 'codex' else '--no-session-persistence', command)
                if provider == 'codex':
                    self.assertEqual(command[3], 'exec')
                else:
                    self.assertIn('--print', command)
                self.assertEqual(set(command) & {'resume', '--resume', '--continue', '-r', '-c'}, set())
                for field in ('conversation_id', 'provider_session_id'):
                    with self.subTest(provider=provider, field=field):
                        with self.assertRaises(ValueError) as rejected:
                            receive({**run['request'], field: 'old-session'})
                        self.assertIs(type(rejected.exception), ValueError)
                        self.assertEqual(str(rejected.exception), 'unknown worker request fields: ' + field)

    def test_checker_absent(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        checker = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('independent checker execution required') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_is_author(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        checker = author
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('independent checker execution required') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_resumes_author(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = author
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker resumes an author lineage') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_missing_predecessor(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker continuation lineage does not resolve') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_cycle(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = checker
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker resumes an author lineage') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
