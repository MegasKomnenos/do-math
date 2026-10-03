"""A real engine waits for a toolchain rerecord and retries through its default verifier."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import os
from pathlib import Path
import threading
import unittest

import setup_lean
from do_math import formal, trust_inventory
from do_math.engine import ResearchEngine
from do_math.repository import ResearchRepository
from support.knowledge_formal_engine import scene, run_formal
from support.provider_probes import ObservedCalls
from support.sim import warm_template
from support.storage_probes import Returns


class PublicationObservation:
    """Observe real saves; never supply storage state or publication behaviour.

    Check owner identity and complete publication ordering in cleanup.
    A captured failure is always raised; repaired code has no defect exception.
    """
    def __init__(self, test):
        self.test = test
        self.owner = threading.get_ident()
        self.events = []
        self.error = None

    def record(self, kind, subject=None, head=None):
        thread = threading.get_ident()
        self.events.append((kind, thread, subject, head))
        self.test.assertEqual(thread, self.owner, 'engine mutation escaped the owner thread')

    def __enter__(self):
        with ExitStack() as stack:
            stack.enter_context(ObservedCalls(
                save=ResearchEngine._save, repository=ResearchRepository.save_with_state,
                stops=ResearchEngine._evaluate_stops,
                capture={
                    'save': lambda a: self.record('save', a['self'], a['self'].head),
                    'repository': lambda a: self.record('repository', a['self'], a['expected_head']),
                    'stops': lambda a: self.record('stops', a['self'], a['self'].head)}))
            stack.enter_context(Returns(ResearchRepository.save_with_state,
                snapshot=lambda value: self.record('published', head=value[0])))
            stack.enter_context(Returns(ResearchEngine._save,
                snapshot=lambda value: self.record('saved')))
            self.stack = stack.pop_all()
        return self

    def __exit__(self, kind, error, traceback):
        self.error = error
        return self.stack.__exit__(kind, error, traceback)

    def assert_valid(self):
        test = self.test
        # These checks run outside expectedFailure, including failures raised
        # by a monitoring callback before it could finish recording a save.
        test.assertTrue(self.events, 'no engine publication calls observed')
        for _, thread, _, _ in self.events:
            test.assertEqual(thread, self.owner, 'engine mutation escaped the owner thread')
        if self.error is not None:
            raise self.error

        active = []
        publications = 0
        for kind, _, subject, head in self.events:
            if kind == 'save':
                active.append({'engine': subject, 'before': head, 'stage': 'save'})
            elif kind == 'repository':
                test.assertTrue(active, 'repository publication escaped engine save')
                row = active[-1]
                test.assertEqual(row['stage'], 'save')
                test.assertIs(subject, row['engine'].store)
                test.assertEqual(head, row['before'])
                row['stage'] = 'repository'
            elif kind == 'published':
                test.assertTrue(active)
                row = active[-1]
                test.assertEqual(row['stage'], 'repository')
                test.assertNotEqual(head, row['before'], 'publication did not advance the head')
                row.update(stage='published', head=head)
                publications += 1
            elif kind == 'stops' and active:
                row = active[-1]
                test.assertIs(subject, row['engine'])
                test.assertEqual(row['stage'], 'published', 'stop judgment must follow publication')
                test.assertEqual(head, row['head'], 'stop judgment did not see the published head')
                row['stage'] = 'judged'
            elif kind == 'saved':
                test.assertTrue(active)
                row = active.pop()
                # Real _save skips unchanged state. Every actual publication,
                # unlike such a no-op, must judge stops before returning.
                test.assertIn(row['stage'], ('save', 'judged'), 'publication returned without judging stops')
        test.assertGreater(publications, 0, 'no successful repository publication observed')
        test.assertEqual(active, [])


def setUpModule():
    warm_template()


class MachineFoundationEnvironmentTests(unittest.TestCase):
    def test_foundation_environment_failure_waits_for_rerecord_before_compiler_retry(self):
        publication = PublicationObservation(self)
        self.addCleanup(publication.assert_valid)
        with publication:
            sim, action = scene(source='theorem fixture : 1 = 1 := rfl', declarations=('fixture',))
            sim.lean.allow('theorem fixture : 1 = 1 := rfl', ['fixture'],
                           signatures={'fixture': 'fixture : 1 = 1'})
            host = sim.engine
            environment = host.instance['trust_environments'][host.instance['active_trust_environment']]
            bound = deepcopy(host.runtime['trust_bindings'][environment['id']])
            olean = Path(environment['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
            info = os.stat(olean)
            # Template trust files are shared; restore their metadata after this scene.
            self.addCleanup(os.utime, olean, ns=(info.st_atime_ns, info.st_mtime_ns))
            os.utime(olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
            before = len(sim.lean.checks)
            with ObservedCalls(verifier=formal.verify_lean) as observed:
                run_formal(sim, action)
            self.assertEqual(observed.captured('verifier'), [])
            self.assertEqual(len(sim.lean.checks), before)
            waiting = host.runtime['waiting_actions'][action['id']]
            self.assertEqual(waiting['kind'], 'formal_environment')
            self.assertEqual(waiting['next_owner'], 'trust_governance')
            previous = waiting['execution_id']
            host._resume_formal_waits()
            self.assertIn(action['id'], host.runtime['waiting_actions'])
            record_path = Path(environment['toolchain_record']['path'])
            original_record = record_path.read_bytes()
            self.addCleanup(record_path.write_bytes, original_record)
            source, _ = trust_inventory.validation_program(environment['toolchain'])
            sim.lean.inputs[source.encode('utf-8')] = {}  # Exact representative baseline, without extraction.
            recorded = setup_lean.rerecord(['unused'], record_path.parent, record_path.parent / 'evidence', None,
                identity=environment['toolchain'], jobs=sim.jobs, clock=sim.clock, environment=sim.environment)
            host._resume_formal_waits()
            successor = next(a for a in host.runtime['queue'] if a['id'] == action['id'])
            self.assertEqual(successor['continuation_of'], previous)
            self.assertNotIn(action['id'], host.runtime['waiting_actions'])
            with ObservedCalls(verifier=formal.verify_lean) as observed:
                run_formal(sim, successor)
            args, = observed.captured('verifier')
            self.assertIs(args['jobs'], sim.jobs)
            self.assertIs(args['clock'], sim.clock)
            latest = next(e for e in host.runtime['executions'].values() if e.get('continuation_of') == previous)
            self.assertEqual(latest['outcome'], 'output_accepted')
            self.assertEqual(host.runtime['trust_bindings'][environment['id']], recorded['binding'])
            rebound = [row for row in host.runtime['events'] if row['kind'] == 'trust_environment_rebound']
            self.assertEqual([(row['basis']['previous'], row['basis']['current']) for row in rebound], [(bound, recorded['binding'])])

    def test_foundation_default_engine_verifier_uses_jobs_and_clock_and_publishes(self):
        publication = PublicationObservation(self)
        self.addCleanup(publication.assert_valid)
        with publication:
            sim, action = scene(source='theorem fixture : 1 = 1 := rfl', declarations=('fixture',))
            sim.lean.allow('theorem fixture : 1 = 1 := rfl', ['fixture'],
                           signatures={'fixture': 'fixture : 1 = 1'})
            before = len(sim.lean.checks)
            with ObservedCalls(verifier=formal.verify_lean) as observed:
                run_formal(sim, action)
            args, = observed.captured('verifier')
            self.assertIs(args['jobs'], sim.jobs)
            self.assertIs(args['clock'], sim.clock)
            self.assertEqual(len(sim.lean.checks), before + 1)
            execution, = [row for row in sim.runtime['executions'].values() if row['role'] == 'formal_check']
            self.assertEqual(execution['outcome'], 'output_accepted')
            self.assertEqual(execution['formal_status'], 'verified')
            self.assertTrue(sim.engine.store.read(execution['result_ref'], sim.engine.head))

    def test_publication_observer_rejects_engine_and_repository_on_non_owner_thread(self):
        sim, _ = scene()
        host = sim.engine
        head = host.head
        for publish, arguments in ((host._save, ()),
                (host.store.save_with_state, (head, host.instance, host.runtime))):
            with self.subTest(publication=publish.__qualname__):
                observation = PublicationObservation(self)
                with observation, ThreadPoolExecutor(max_workers=1) as worker:
                    with self.assertRaisesRegex(AssertionError, 'engine mutation escaped the owner thread'):
                        worker.submit(publish, *arguments).result(timeout=10)
                # The same cleanup validator also refuses this observation;
                # neither failure is covered by a known-defect mark.
                with self.assertRaisesRegex(AssertionError, 'engine mutation escaped the owner thread'):
                    observation.assert_valid()
                self.assertEqual(len(observation.events), 1)
                kind, thread, subject, _ = observation.events[0]
                self.assertIn(kind, ('save', 'repository'))
                self.assertIs(subject, publish.__self__)
                self.assertNotEqual(thread, observation.owner)
                self.assertEqual(host.head, head)
                self.assertEqual(host.store.load()[0], head)
