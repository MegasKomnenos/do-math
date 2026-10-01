"""Question links (``questions``, ``question_engine.question_view``, ``revisions``): routing, waits and resolution.

A question stays in its original source; its link records the source, owner,
affected targets and whether it blocks. Only a blocking user question stops
work on the targets it names, only a user decision resolves a user question,
and a repetition limit's question is read from the history row it points to.
The records are plain runtime families on which the product functions run;
each rejection is pinned to its reason.
"""
from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from do_math import governance as gov, questions, revisions
from do_math.governance import preserve_source
from do_math.question_engine import question_view, user_questions
from do_math.record_schemas import RECORDS
from support.record_builders import domain_governance


class QuestionTests(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        self.instance = {"id": "I", "knowledge": {}}
        self.runtime = {"tasks": {"A": {"id": "A"}, "B": {"id": "B"}}, "question_links": []}
        self.a = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True, clock=_entry.ports.clock)
        self.b = questions.link(self.runtime, execution_id="E2", field="output/questions/0", owner="user", targets=["B"], blocks=True, clock=_entry.ports.clock)

    def test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks(self):
        from support.entry import entry
        _entry = entry()
        waits = questions.user_waits({"role": "research_work", "target": "A"}, self.instance, self.runtime)
        self.assertEqual([row["question_id"] for row in waits], [self.a["id"]])
        self.assertEqual(questions.user_waits({"role": "research_work", "target": "C"}, self.instance, self.runtime), [])
        self.assertEqual(questions.user_waits({"role": "research_plan"}, self.instance, self.runtime), [])
        whole = questions.link(self.runtime, execution_id="E3", field="output/questions/0", owner="user", targets=["I"], blocks=True, clock=_entry.ports.clock)
        waits = questions.user_waits({"role": "research_plan"}, self.instance, self.runtime)
        self.assertEqual([row["question_id"] for row in waits], [whole["id"]])
        self.assertEqual(questions.user_waits({"role": "intent_interpretation"}, self.instance, self.runtime), [])

    def test_resolving_one_user_question_preserves_the_other(self):
        questions.resolve_user(self.runtime, [self.a["id"]], resolution_ref="D", affected_ids=["A"])
        self.assertEqual(self.a["status"], "resolved")
        self.assertEqual(self.b["status"], "open")
        with self.assertRaisesRegex(ValueError, "^the applied decision does not affect the question target: "
                                    + self.b["id"] + "$"):
            questions.resolve_user(self.runtime, [self.b["id"]], resolution_ref="unrelated", affected_ids=["A"])

    def test_an_ai_extension_cannot_resolve_a_user_question(self):
        context = {"instance_id": "I", "action": {"role": "research_plan"}, "question_links": self.runtime["question_links"]}
        extensions = {"question_resolutions": [{"question_id": self.a["id"], "disposition": "resolved",
                                                "evidence_refs": ["E"], "reason": "guess"}]}
        self.assertEqual(questions.validate_extensions({}, extensions, context), [{
            "path": "question_resolutions",
            "message": "only distinct open research or operations questions can be resolved by an AI extension"}])

    def test_source_identity_not_equal_text_controls_deduplication(self):
        from support.entry import entry
        _entry = entry()
        same = questions.link(self.runtime, execution_id="E1", field="output/questions/0", owner="user", targets=["A"], blocks=True, clock=_entry.ports.clock)
        self.assertEqual(same["id"], self.a["id"])
        self.assertEqual(len(self.runtime["question_links"]), 2)
        self.assertNotEqual(self.a["id"], self.b["id"])
        self.assertNotIn("text", self.a)

    def test_retry_bypasses_only_the_question_for_its_held_overflow(self):
        from support.entry import entry
        _entry = entry()
        other = questions.link(self.runtime, execution_id="E3", field="output/questions/0",
                               owner="user", targets=["A"], blocks=True, clock=_entry.ports.clock)
        action = {"id": "AC-1", "role": "research_work", "target": "A",
                  "input_overflow_retry": {"question_id": self.a["id"], "state": "pending"}}
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual([row["question_id"] for row in waits], [other["id"]])

        action["input_overflow_retry"]["state"] = "resolved"
        waits = questions.user_waits(action, self.instance, self.runtime)
        self.assertEqual(sorted(row["question_id"] for row in waits), sorted([self.a["id"], other["id"]]))


class QuestionRouteTests(unittest.TestCase):
    def test_route_targets_admit_the_records_of_the_record_index(self):
        # A grant a task relies on is a record the role may cite through its record_index.
        output = {'questions': ['May the task use GR-1 for this effect?']}
        route = {'question_index': 0, 'owner': 'user', 'target_ids': ['GR-1'], 'blocks': True,
                 'reason': 'The answer decides whether GR-1 authorizes the next action.'}
        context = {'instance_id': 'I', 'action': {'role': 'research_work'},
                   'record_index': {'research/grants': ['GR-1']}}
        self.assertEqual(questions.validate_extensions(output, {'question_routes': [route]}, context), [])
        route['target_ids'] = ['GR-unknown']
        self.assertEqual(questions.validate_extensions(output, {'question_routes': [route]}, context), [{
            'path': 'question_routes',
            'message': 'route targets must be IDs this input supplies or lists in its record_index, '
                       'and a user question needs at least one'}])


class RepetitionQuestionTests(unittest.TestCase):
    """A repetition limit's hold question, read through ``question_view`` from the history row it points to."""

    def held(self):
        from support.entry import entry
        _entry = entry()
        instance = {'id': 'I', 'config': {'selection_failure_limit': 1},
            'governance_sources': {'S': preserve_source('S', 'Authorize the exact continuation.', origin='user')},
            'decisions': {}}
        action = {'id': 'AC-held', 'role': 'research_plan', 'repetition_bases': {'selection_failure': 'population'}}
        runtime = {'tasks': {}, 'history': [], 'queue': [action], 'executions': {
            'EX-first': {'id': 'EX-first', 'role': 'research_plan', 'status': 'ended', 'action': deepcopy(action)}}}
        revisions.record_repetition(instance, runtime, lineage='selection_failure',
            lineage_id='population', event_ref='EX-first', outcome='rejected', owner='ai',
            reason='The returned plan omitted a candidate.', clock=_entry.ports.clock)
        return instance, runtime, action

    def view(self, instance, runtime):
        """``question_view`` over sources that never need the store: the reader must not be called."""
        def reader(refs):
            raise AssertionError('no question source is a stored artifact: ' + repr(refs))
        return question_view(instance, runtime, reader)

    def test_limit_question_reads_preserved_history_after_roundtrip_and_append(self):
        instance, runtime, action = self.held()
        original = revisions.repetition_hold(runtime, 'selection_failure', 'population')
        runtime = json.loads(json.dumps(runtime))
        runtime['history'].append({'kind': 'unrelated_later_event'})
        row = self.view(instance, runtime)[0]
        self.assertEqual(row['text'], original['question'])
        self.assertIn('selection_failure/population', row['text'])
        self.assertIn('1/1', row['text'])
        self.assertNotIn('source_status', row)
        self.assertEqual(user_questions(self.view(instance, runtime)), [original['question']])
        self.assertIsNone(Draft202012Validator(RECORDS['question_links']).validate(runtime['question_links'][0]))
        self.assertTrue(revisions.action_repetition_waits(instance, runtime, action))

    def test_scoped_continuation_resolves_only_the_current_hold_question(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime, action = self.held()
        first = runtime['question_links'][0]
        questions.link(runtime, execution_id='EX-other', field='error', owner='user', targets=['I'], blocks=False, clock=_entry.ports.clock)
        runtime['executions']['EX-other'] = {'id': 'EX-other', 'error': 'A separate choice remains.'}
        change = {'kind': 'repetition_continue', 'lineage': 'selection_failure',
            'lineage_id': 'population', 'hold_event_ref': 'EX-first',
            'allowed_action': revisions.action_scope(action), 'reason': 'Continue the exact held plan.'}
        decision = {'id': 'DC-continue', 'actor': 'user', 'source_ref': 'S', 'change': change}
        instance['decisions'][decision['id']] = decision
        revisions.continue_repetition(instance, runtime, change, decision, clock=_entry.ports.clock)
        self.assertEqual(first['status'], 'resolved')
        self.assertEqual(first['resolution_ref'], decision['id'])
        self.assertEqual(user_questions(self.view(instance, runtime)), ['A separate choice remains.'])
        self.assertFalse(revisions.action_repetition_waits(instance, runtime, action))
        runtime['executions']['EX-second'] = {'id': 'EX-second', 'role': 'research_plan',
            'status': 'ended', 'action': deepcopy(action)}
        revisions.record_repetition(instance, runtime, lineage='selection_failure',
            lineage_id='population', event_ref='EX-second', outcome='rejected', owner='ai',
            reason='The next returned plan still omitted a candidate.', clock=_entry.ports.clock)
        current = runtime['question_links'][-1]
        self.assertNotEqual(first['origin_field'], current['origin_field'])
        self.assertEqual(current['status'], 'open')
        self.assertIn('EX-second', self.view(instance, runtime)[-1]['text'])
        self.assertEqual(len(user_questions(self.view(instance, runtime))), 2)


class GovernanceQuestionTests(unittest.TestCase):
    def test_question_advice_does_not_block_and_partial_target_answer_does_not_erase_wait(self):
        from support.entry import entry
        _entry = entry()
        rt = {}; questions.link(rt, execution_id="E", field="questions/0", owner="user", targets=["I"], blocks=False, clock=_entry.ports.clock)
        self.assertEqual(questions.user_waits({"role": "research_preparation"}, {"id": "I"}, rt), [])
        blocking = questions.link(rt, execution_id="E", field="questions/1", owner="user", targets=["A", "B"], blocks=True, clock=_entry.ports.clock)
        questions.resolve_user(rt, [blocking["id"]], resolution_ref="D", affected_ids=["A"])
        self.assertEqual(blocking["status"], "open")
        self.assertEqual(blocking["unresolved_target_ids"], ["B"])

    def test_actual_answer_preserves_other_affected_targets(self):
        from support.entry import entry
        _entry = entry()
        i = domain_governance(); rt = {"tasks": {"A": {"id": "A"}, "B": {"id": "B"}}, "executions": {}, "queue": []}
        q = questions.link(rt, execution_id="E", field="q/0", owner="user", targets=["A", "B"], blocks=True, clock=_entry.ports.clock)
        _, updated, _ = gov.apply_decision(i, rt, {"kind": "question_answer", "text": "Answer A", "target_ids": ["A"],
                                                   "resolves_questions": [q["id"]]}, source_ref="S", clock=_entry.ports.clock)
        self.assertEqual(updated["question_links"][0]["unresolved_target_ids"], ["B"])
        self.assertEqual(updated["question_links"][0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
