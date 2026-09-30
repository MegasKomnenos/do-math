"""An interpretation's rework keeps the original import-rework lineage (``governance_engine._queue_intent_rework``,
``revisions``; layer 2), moved from ``test_repetition`` (``RepetitionLineageTests``).

The legacy test authored one interpretation of an input and applied a failing
independent check on an in-memory engine with replaced methods
(``engine_fixtures.routing_engine``, ``intent_import``, ``intent_verdict``). Here a
restored Sim's real engine receives a user's input by public control; the model
double answers its interpretation through the worker and the independent check
returns ``revision_required``, so the engine's own receiver queues the rework.
The two role calls make the scene longer than one Sim test's budget.
"""
from copy import deepcopy
import unittest

from do_math import revisions, task_contracts
from support.engine_lifecycle import clear_work
from support.model import amend
from support.sim import Sim, warm_template

setUpModule = warm_template


class RepetitionLineageTests(unittest.TestCase):
    def test_real_intent_rework_producer_keeps_original_lineage(self):
        """About 4.5 s: an input's interpretation and its failing check are two model calls through the worker."""
        sim = Sim.activated()
        clear_work(sim)
        # The independent check of the user's input fails; the engine queues the interpretation's rework.
        sim.model.on('intent_interpretation', stage='check').reply(
            amend(decision='revision_required', scope_complete=False, findings=['Missing second clause']))
        sim.control('input', text='Keep the original purpose.', request_id='input-rework')
        sim.run_until(lambda s: any(a.get('intent_repair') for a in s.runtime['queue']), max_steps=12)
        engine = sim.engine
        rework = next(a for a in engine.runtime['queue'] if a.get('intent_repair'))
        check_execution = rework['intent_repair']['check_execution_id']
        self.assertEqual(engine.runtime['executions'][check_execution]['action']['stage'], 'check')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, rework)
        engine.runtime['executions']['EX-rework'] = {'role': rework['role'], 'action': deepcopy(rework)}
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        counts = task_contracts.repetition_lineages(engine.runtime)
        self.assertEqual(counts['import_rework']['count'], 1)
        retry = {**deepcopy(rework), 'id': 'AC-next', 'previous_import_id': 'IM-next'}
        retry.pop('repetition_bases')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, retry)
        self.assertEqual(retry['repetition_bases'], rework['repetition_bases'])
        check = {**rework, 'stage': 'check', 'continuation_of': check_execution}
        self.assertFalse(revisions.import_rework(engine.runtime, check))
        engine.instance['config']['import_rework_limit'] = 1
        later = deepcopy(rework)
        revisions.record_repetition(engine.instance, engine.runtime, lineage='import_rework',
            lineage_id=rework['repetition_bases']['import_rework'], event_ref='EX-rework-2',
            outcome='reauthored', owner='ai', reason='Second registered reauthor')
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, later))
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, check))
        other = {**later, 'target': 'UC-unrelated'}
        other.pop('repetition_bases')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, other)
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, other))


if __name__ == '__main__':
    unittest.main()
