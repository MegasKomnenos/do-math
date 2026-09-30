"""What the engine gives a governance role (``governance_engine``): the interpretation context and the audit input.

Each test starts from a restored public activation. An input arrives by the
public ``input`` control and the owner applies it; the engine's own
``_governance_context`` then builds the interpreter's context from the stored
state. Nothing replaces an engine method or the store.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unicodedata
import unittest

from do_math import governance as gov
from support.sim import Sim, warm_template

setUpModule = warm_template

SKILL = Path(__file__).resolve().parents[3]


def received_input(sim, text, **options):
    """The ID of a public ``input`` control with ``text`` the owner applied."""
    request = sim.control('input', text=text, **options)
    sim.engine.process_controls()
    if request['request_id'] not in [row['id'] for row in sim.runtime['inputs']]:
        raise AssertionError('the owner did not record the input ' + request['request_id'])
    return request['request_id']


class InterpretationContextTests(unittest.TestCase):
    def test_intent_input_exposes_actual_consumers_and_exact_source(self):
        sim = Sim.activated()
        text = 'e\u0301 has two code points'
        identifier = received_input(sim, text)
        engine = sim.engine
        context = engine._governance_context({'role': 'intent_interpretation', 'target': identifier}, {})
        self.assertEqual(context['user_request']['text'], context['original_source']['text'])
        self.assertEqual(context['original_source']['text'], text)
        kinds = {row['owner_kind'] for row in context['import_consumers']}
        self.assertEqual(kinds, gov.GOVERNANCE_KINDS | {'grant', 'revoke', 'delegation', 'question_answer',
            'task_scope'} | set(engine.governance_owner_handlers()))
        self.assertEqual(context['governance_records'], list(engine.instance['governance'].values()))
        for row in context['import_consumers']:
            document = SKILL / row['payload_contract']['document']
            self.assertIn(row['owner_kind'], document.read_text(encoding='utf-8'))

    def test_intent_input_tasks_carry_the_contract_hash_a_scope_decision_binds(self):
        # 입력-소비자.md task_scope uses the supplied task edition and hash; the application
        # compares that hash with planning.contract_hash (governance.apply_decision).
        from do_math.planning import contract_hash
        from record_fixtures import task_contract
        sim = Sim.activated()
        identifier = received_input(sim, 'Waive the first obligation.')
        task = task_contract()
        context = sim.engine._governance_context({'role': 'intent_interpretation', 'target': identifier},
                                                 {'tasks': [{**deepcopy(task), 'content_sha256': 'c' * 64}]})
        self.assertEqual(context['tasks'][0]['contract_sha256'], contract_hash(task))

    def test_nfd_original_reaches_actual_context_and_coverage(self):
        # The initial input: its source comes from the lifecycle's immutable input (governance.import_input_source).
        text = 'Prove that e\u0301 has two code points.'
        raw = text.encode(); working = unicodedata.normalize('NFC', text).encode()
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory, goal=text)
            engine = sim.engine
            identifier = engine.instance['lifecycle']['input_id']
            self.assertEqual(engine.instance['lifecycle']['immutable_input']['text'], text)
            context = engine._governance_context({'role': 'intent_interpretation', 'target': identifier}, {})
            self.assertEqual(context['user_request']['text'], text)
            self.assertEqual(context['original_source']['text'], text)
            source = engine._governance_input_source(identifier)
            self.assertEqual(source['sha256'], hashlib.sha256(raw).hexdigest())
            output = {'questions': [], 'question_details': [], 'import_units': [{
                'unit_id': 'U', 'source_range': {'start': 0, 'end': len(text)}, 'interpretation': 'Exact codepoint assertion',
                'owner_kind': 'charter', 'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': []}]}
            bundle = gov.prepare_import(engine.instance, engine.runtime, source, output, execution_id='AUTHOR',
                                        input_ref=identifier)
            self.assertEqual(bundle['source']['text'], text)
            output['import_units'][0]['source_range']['end'] = len(working.decode())
            with self.assertRaisesRegex(ValueError, '^incomplete source coverage$'):
                gov.prepare_import(engine.instance, engine.runtime, source, output, execution_id='AUTHOR',
                                   input_ref=identifier)


class RestartedContextTests(unittest.TestCase):
    """A publicly initialized instance (the legacy ``new_instance``), restarted from its repository."""

    def initialized(self, **options):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return Sim(directory.name, **options)

    def test_exact_initial_input_context_survives_actual_git_restart(self):
        text = 'Prove that e\u0301 contains two Unicode codepoints.'
        sim = self.initialized(goal=text)
        sim.restart()
        engine = sim.engine
        context = engine._governance_context({'role': 'intent_interpretation',
            'target': engine.instance['lifecycle']['input_id']}, {})
        self.assertEqual(context['user_request']['text'], text)
        self.assertEqual(context['original_source']['text'], text)

    def test_exact_public_input_and_replay_preserve_codepoints_after_git_restart(self):
        sim = self.initialized()
        text = 'e\u0301 is a two-codepoint literal'
        received_input(sim, text, request_id='literal-input')
        sim.restart()
        context = sim.engine._governance_context({'role': 'intent_interpretation', 'target': 'literal-input'}, {})
        self.assertEqual(context['original_source']['text'], text)
        self.assertEqual(context['user_request']['text'], text)
        with self.assertRaisesRegex(ValueError, '^request_id reused with different payload$'):
            sim.control('input', text='\u00e9 is a two-codepoint literal', request_id='literal-input')


if __name__ == '__main__':
    unittest.main()
