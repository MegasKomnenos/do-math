"""A simulated owner restart loses the old process's file and artifact facts."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from do_math import core_engine, file_io
from do_math.state_contract import default_state_contract
from support.provider_probes import settle
from support.sim import Sim, warm_template

setUpModule = warm_template


class RestartStateTests(unittest.TestCase):
    def test_restart_ends_only_the_known_owner_and_rebinds_recovery_to_the_same_world(self):
        """About 2.6s under shared load: actual workers, owner loss and repeated durable recovery."""
        from copy import deepcopy
        from do_math.launch import mark_dispatched, termination_confirmed
        from do_math import codex_worker
        from do_math.model_policy import MODELS
        from support.fakes.calls import owner_turn
        from support.fakes.jobs import job_turn
        from support.provider_runs import ScriptedCLI
        from support.scheduling_slots import reserve

        sim = Sim.activated()
        sim.engine._enqueue('maintenance', reason='Preserve an actual worker response across owner restart')
        sim.engine._save()
        sim.step()
        self.assertTrue(sim.model.calls, 'the real ModelRunner and worker must leave response history')
        previous, old_engine, old_ports = sim.jobs.owner_identity(), sim.engine, sim.ports
        model, history, objects = sim.model, sim.model.calls, sim.ports.git_backend.objects
        before_history = deepcopy(history)
        ran = []

        def program(argv, cwd, env):
            ran.append('job started')
            job_turn()
            ran.append('old job resumed')
            return 0

        sim.jobs.programs.insert(0, (lambda argv: argv == ['restart-fixture'], program))
        with sim.engine.store.writer_lock():
            admitted, execution = reserve(sim, 'EX-restart-owner')
            self.assertTrue(admitted)
            mark_dispatched(execution['launch_ticket'])
            ticket = deepcopy(execution['launch_ticket'])
            sim.engine._save()
        job = sim.jobs.launch(['restart-fixture'], name=ticket['job_name'])
        job.live = True
        job.resume()
        self.assertEqual(ran, ['job started'])
        self.assertFalse(termination_confirmed(ticket, recovering=True, jobs=sim.jobs))

        def suspended():
            owner_turn()
            ran.append('old calculation resumed')

        calls = sim.ports.calls.new(on_returned=lambda *args: ran.append('old owner callback'))
        running = calls.start_call(None, suspended, {})
        calls.wait(0)
        pending = calls.start_call(None, lambda: ran.append('unstarted calculation'), {})
        self.assertFalse(running.done())
        self.assertFalse(pending.done())

        # An unbound ModelRunner consumer can launch even after the Job owner
        # changes. Prove the same real runner/worker route works before losing
        # its next call; stopping it after launch would already be too late.
        cli = ScriptedCLI()
        sim.jobs.programs.insert(0, (
            lambda argv: Path(argv[1]).name == 'codex_worker.py',
            lambda argv, cwd, env: codex_worker.run(Path(argv[2]), spawn=cli.spawn)))
        other = sim.ports.calls.new(on_returned=lambda *args: ran.append('old runner callback'))
        self.assertIsNot(other, calls)
        workspace = sim.root / 'restart-worker'
        workspace.mkdir()
        arguments = dict(prompt='Restart worker probe', output_schema={'type': 'object'},
                         workspace=workspace, evidence_dir=sim.root / 'returned-runner',
                         model=MODELS['high'], effort='high', timeout_seconds=30,
                         should_stop=lambda: False,
                         on_observation=lambda *args: ran.append('old observation'))
        returned = other.start_call(None, sim.engine.runner.run, arguments)
        other.wait(0)
        actual_result = returned.result(timeout=0)
        self.assertEqual(actual_result['status'], 'completed')
        self.assertEqual(len(cli.calls), 1)
        self.assertTrue(returned.observations)
        lost_evidence = sim.root / 'unstarted-runner'
        lost = other.start_call(None, sim.engine.runner.run, {
            **arguments, 'evidence_dir': lost_evidence,
            'on_started': lambda *args: ran.append('old start callback')})
        turns = list(calls.turns) + list(other.turns)
        self.assertIsNone(other.turns[-1].thread)
        launched = list(sim.jobs.launched)
        durable = deepcopy(sim.engine.store.load()[2])
        sim.restart()

        self.assertEqual(sim.jobs.launched, launched, 'lost calls must not launch Jobs under the new owner')
        self.assertFalse(lost_evidence.exists(), 'the unstarted runner body must not execute')
        self.assertEqual(len(cli.calls), 1)
        self.assertTrue(lost.cancelled())
        self.assertIs(returned.result(timeout=0), actual_result)
        self.assertFalse(returned.observations)
        self.assertEqual((other.turns, other.futures), ([], {}))
        self.assertEqual(other.collect(), 0)
        self.assertTrue(all(turn.thread is None or not turn.thread.is_alive() for turn in turns))
        self.assertTrue(all(future.stop.is_set() for future in (running, pending, returned, lost)))
        self.assertEqual(sim.ports.calls.created, [])
        self.assertIs(sim.clock, old_ports.clock)
        for key in ('executions', 'reservations'):
            self.assertEqual(sim.engine.store.load()[2][key], durable[key])
        self.assertNotEqual(sim.jobs.owner_identity()['pid'], previous['pid'])
        self.assertNotEqual(sim.jobs.owner_identity()['creation_filetime'], previous['creation_filetime'])
        self.assertTrue(sim.jobs.owner_ended(previous))
        self.assertFalse(sim.jobs.owner_ended(sim.jobs.owner_identity()))
        self.assertIsNone(sim.jobs.owner_ended({**previous, 'pid': previous['pid'] + 999}))
        self.assertIsNone(sim.jobs.owner_ended({**previous, 'host': 'unknown foreign host'}))
        self.assertTrue(job.closed and job.done)
        self.assertEqual(job.inspect().active_processes, 0)
        self.assertTrue(termination_confirmed(ticket, recovering=True, jobs=sim.jobs))
        self.assertTrue(running.done())
        self.assertTrue(pending.cancelled())
        self.assertEqual((calls.turns, calls.futures), ([], {}))
        calls.wait(0)
        self.assertEqual(calls.collect(), 0)
        self.assertEqual(ran, ['job started'])
        self.assertIsNot(sim.engine, old_engine)
        self.assertIsNot(sim.ports.calls, old_ports.calls)
        self.assertIs(sim.ports.jobs, old_ports.jobs)
        self.assertIs(sim.ports.git_backend.objects, objects)
        self.assertIs(sim.model, model)
        self.assertIs(sim.model.calls, history)
        self.assertEqual(history, before_history)
        self.assertIs(sim.engine.ports, sim.ports)
        with sim.engine.store.writer_lock():
            sim.engine._recover_disappeared()
            sim.engine._save()
        recovered = sim.engine.store.load()[2]
        self.assertEqual(recovered['executions']['EX-restart-owner']['status'], 'ended')
        self.assertEqual(recovered['executions']['EX-restart-owner']['capacity']['local_termination'], 'confirmed')
        self.assertFalse([row for row in recovered['reservations'].values()
                          if row['owner_id'] == 'EX-restart-owner' and row['state'] == 'held'])
        with sim.engine.store.writer_lock():
            sim.engine._recover_disappeared()
            sim.engine._save()
        for key in ('executions', 'reservations'):
            self.assertEqual(sim.engine.store.load()[2][key], recovered[key])

    def test_restart_discards_old_artifact_bytes_and_reads_the_durable_resource(self):
        sim = Sim.activated()
        path = 'runtime/artifacts/BA-restart-facts/output.txt'
        raw = b'original artifact bytes'
        head, instance, runtime = sim.engine.store.load()
        head, _, _ = sim.engine.store.save_with_state(head, instance, runtime, artifacts={path: raw})
        self.assertEqual(sim.engine.store.read(path, head), raw)
        oid = hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
        objects = sim.ports.git_backend.objects[str(sim.engine.store.git_dir)]
        self.assertEqual(objects[oid], ('blob', raw))
        changed = b'changed artifact bytes!'
        objects[oid] = ('blob', changed)
        # Facts already held by the original owner still yield its bytes.
        self.assertEqual(sim.engine.store.read(path, head), raw)
        sim.restart()
        self.assertEqual(sim.engine.store.read(path, head), changed)

    def test_restart_discards_unrelated_file_hash_and_default_contract_caches(self):
        sim = Sim.activated()
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = root / 'outside-instance.txt'
        path.write_bytes(b'file fact')
        settle(path)
        self.assertEqual(file_io.cached_sha256(path), hashlib.sha256(b'file fact').hexdigest())
        key = os.path.normcase(os.path.abspath(path))
        self.assertIn(key, file_io._hashed)
        contract = default_state_contract()
        sim.engine._installation_manifest()
        self.assertTrue(core_engine._HASHED_INSTALLATION)
        sim.restart()
        self.assertNotIn(key, file_io._hashed)
        self.assertIsNot(default_state_contract(), contract)
        self.assertEqual(core_engine._HASHED_INSTALLATION, {})
