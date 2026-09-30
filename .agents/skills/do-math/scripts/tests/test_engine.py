"""The research engine's own operations: initialization and activation, queueing, dispatch, publication and installation checks.

Stage 1f moved the other tests of this module to unit.test_engine_record_rules,
sim.test_engine_queue, sim.test_engine_flow and boundary.test_engine_model_process.
These remain: three replace the installation manifest (no seam reaches it) and one
forbids the owner's periodic upkeep during input preparation (no port observes it).
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from do_math.engine import control, ResearchEngine
from research_fixtures import charter_change, FixtureAdapter, restore_template, send_control
from runner_fixtures import ScriptedRunner


def efficiency_instance(root, shared, *, config, charter):
    """``restore_template`` build: the synthetic active state with one queued, published preparation.

    These tests start after activation. They keep real state publication and
    the preparation request they exercise, without replaying input approval.
    ``charter`` also approves academic requirement ``explain`` through a public
    charter control, which opens a plan for the charter event.
    """
    from state_fixtures import active_instance
    instance_id = active_instance(root, shared, config=config)
    engine = ResearchEngine(root / "repository", instance_id)
    (root / "work-0" / "runs").mkdir(exist_ok=True)
    engine._enqueue("research_preparation", reason="Prepare the bounded efficiency fixture")
    engine._save()
    if charter:
        send_control(engine, "decision", config={"change":
            charter_change(engine, academic_requirements=[
                {"id": "explain", "scope": "solution", "criteria": ["explain structure"],
                 "assessor": "research_plan"}])})
    return instance_id


EFFICIENCY_CONFIG = {"operator_enabled": False, "scholarly_enabled": False, "lean_command": ["test-lean"],
                     "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}


class QueuedPreparationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch('do_math.local_host.adapter_for', return_value=FixtureAdapter()))
        self.open(charter=False)

    def open(self, *, charter):
        """Make ``self.engine`` a new engine, with a new ``ScriptedRunner``, on a copy of ``efficiency_instance``."""
        self.root, instance_id = restore_template(efficiency_instance, config=EFFICIENCY_CONFIG, charter=charter)
        self.workspace = self.root / "work-0"
        self.engine = ResearchEngine(self.root / "repository", instance_id, runner=ScriptedRunner())

    def test_pause_received_during_input_preparation_prevents_model_start(self):
        e = self.engine
        before_executions = set(e.runtime["executions"])
        before_calls = len(e.runner.prompts)
        before_runs = set((self.workspace / "runs").iterdir())
        original = e._context
        def prepare(action, workspace, **kwargs):
            context = original(action, workspace, **kwargs)
            control(e.store.repository, e.instance["id"], "pause", text="stop during materialization")
            return context
        # Preparation applies user controls only; periodic upkeep waits for the owner loop.
        with patch.object(e, '_context', side_effect=prepare), \
                patch.object(e, '_upkeep', side_effect=AssertionError('input preparation ran the upkeep')):
            generator = e._call_steps(e.runtime["queue"][0])
            with self.assertRaises(StopIteration):
                next(generator)
        self.assertEqual(e.runtime["status"], "paused")
        self.assertEqual(len(e.runner.prompts), before_calls)
        added = set(e.runtime['executions']) - before_executions
        self.assertEqual(len(added), 1)
        execution = e.runtime['executions'][added.pop()]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'cancelled'))
        self.assertIsNone(execution.get('started_at'))
        self.assertNotIn('capacity', execution)
        self.assertEqual(set((self.workspace / "runs").iterdir()), before_runs)

    def test_installation_polling_is_bounded_and_forced_checks_still_detect_edits(self):
        e = self.engine
        self.assertTrue(callable(getattr(e, '_check_installation', None)), 'bounded installation checks required')
        with patch.object(e, '_installation_manifest', return_value=e._installation) as probe:
            for _ in range(10):
                self.assertTrue(e._check_installation())
            self.assertLessEqual(probe.call_count, 1)
        with patch.object(e, '_installation_manifest', return_value={"sha256": "changed"}):
            self.assertFalse(e._check_installation(force=True))
        self.assertEqual(e.runtime["status"], "paused")

    def test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check(self):
        from do_math import engine as engine_module
        repository = self.engine.store.repository
        source = self.root / 'note.txt'
        source.write_bytes(b'archived source bytes')
        control(repository, self.engine.instance['id'], 'source', config={'path': str(source)})
        self.engine.process_controls()
        self.assertTrue(self.engine.instance['sources'])
        with patch.object(ResearchEngine, '_installation_manifest', side_effect=AssertionError('run hashes the installation')), \
                patch.object(engine_module, 'all_prompt_documents', side_effect=AssertionError('a prompt loads documents')):
            engine = ResearchEngine(repository, self.engine.instance['id'])
            with patch.object(engine.store, 'read', side_effect=AssertionError('status reads no artifact bytes')), \
                    patch.object(engine.store, 'read_many', side_effect=AssertionError('status reads no artifact bytes')):
                status = engine.status()
        self.assertEqual(status['submission_checks']['status'], 'not_evaluated')
        storage = next(area for area in status['inspection']['areas'] if area['name'] == 'record_storage')
        self.assertIn('artifact presence and length', storage['checked_invariants'])

    def test_installation_change_cannot_reopen_a_terminal_instance(self):
        e = self.engine
        e._installation  # run hashes the loaded edition before any periodic check
        for terminal in ('closed', 'completed'):
            with self.subTest(terminal=terminal):
                e.runtime['status'] = terminal
                with patch.object(e, '_installation_manifest', return_value={'sha256': 'changed'}):
                    self.assertFalse(e._check_installation(force=True))
                self.assertEqual(e.runtime['status'], terminal)


if __name__ == "__main__": unittest.main(verbosity=2)
