"""Engine publication and reload judge live calls against the adopted, stored head.

The engine, repository, contract and Calls implementation are real. Only Git,
clock and calculation scheduling use the existing ports' deterministic fakes.
"""
from pathlib import Path
import tempfile
import threading
import unittest

from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.state_builders import current_state
from support.storage_records import engine_on, fake_ports, record_store


class PublicationStopTests(unittest.TestCase):
    def test_save_and_reload_judge_stops_after_adopting_the_published_head(self):
        for operation in ('save', 'reload'):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                clock, backend = FakeClock(), InProcessGit()
                ports = fake_ports(clock, backend)
                store = record_store(root / 'repository', backend=backend, clock=clock)
                engine, initial = engine_on(store, *current_state(runtime={'executions': {}}),
                                            workspace=root / 'work', ports=ports)
                owner = threading.get_ident()
                judgments, results = [], []

                def judge():
                    stored_head, _, runtime = store.load()
                    judgments.append((threading.get_ident(), engine.head, stored_head,
                                      engine.runtime['status'], runtime['status']))
                    return engine.runtime['status'] == 'paused'

                def continuation():
                    results.append((yield))

                calls = engine._calls = ports.calls.new()
                try:
                    generator = continuation()
                    next(generator)
                    future = calls.start_call(generator,
                        lambda should_stop: {'status': 'stopped' if should_stop() else 'completed'},
                        {'should_stop': judge}, execution_id='EX-publication-probe')
                    self.assertEqual(judgments, [(owner, initial, initial, 'initializing', 'initializing')])
                    if operation == 'save':
                        engine.runtime['status'] = 'paused'
                        engine._save()
                    else:
                        _, instance, runtime = store.load(initial)
                        runtime['status'] = 'paused'
                        published = store.save_with_state(initial, instance, runtime)[0]
                        self.assertEqual(engine.head, initial)
                        self.assertEqual(len(judgments), 1)
                        engine._reload(published)
                    self.assertNotEqual(engine.head, initial)
                    self.assertEqual(judgments, [(owner, initial, initial, 'initializing', 'initializing'),
                        (owner, engine.head, engine.head, 'paused', 'paused')])
                    self.assertTrue(future.stop.is_set())
                    self.assertEqual(store.load(initial)[2]['status'], 'initializing')
                    calls.wait(0)
                    calls.collect()
                    self.assertEqual(results, [{'status': 'stopped'}])
                    self.assertEqual(calls.futures, {})
                    if operation == 'save':
                        engine._save()
                        self.assertEqual(len(judgments), 2, 'an unchanged state needs no new stop judgment')
                finally:
                    calls.close()
                    engine._calls = None
