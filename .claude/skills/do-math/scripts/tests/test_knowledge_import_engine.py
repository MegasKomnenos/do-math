"""Structured user data reaches the real verification and query consumers."""
from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control, query_records
from do_math.knowledge import assess_use
from test_purpose_engine import PurposeHarness, theorem


class KnowledgeImportTests(PurposeHarness):
    def test_imported_theorem_only_becomes_usable_after_actual_engine_gates(self):
        engine, runner = self.make()
        engine.runtime['queue'] = []; engine._save()
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation':'import','candidate':theorem()})
        engine.process_controls()
        kid = next(iter(engine.instance['knowledge']))
        self.assertFalse(assess_use(engine.instance['knowledge'][kid], engine.instance)['valid'])
        self.assertEqual(engine.runtime['queue'][0]['role'], 'formal_check')
        engine.run(max_steps=3)
        self.assertTrue(assess_use(engine.instance['knowledge'][kid], engine.instance)['valid'])
        self.assertEqual(len(engine.instance['knowledge'][kid]['reviews']), 2)
        self.assertTrue(engine.check()['passed'], engine.check())
        page = query_records(self.repo, engine.instance['id'], kind='kind-definition')
        self.assertTrue(any(item['record']['token']=='formally_implies' for item in page['items']))

    def test_reimport_preserves_identity_but_requires_new_formal_and_full_review(self):
        engine, _ = self.make()
        engine.runtime['queue'] = []; engine._save()
        value = {**theorem(), 'id':'KN-import-fixture'}
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation':'import','candidate':value})
        engine.process_controls(); engine.run(max_steps=3)
        old = deepcopy(engine.instance['knowledge'][value['id']])
        changed = {**value, 'summary':'The equality holds over the complete natural-number domain.'}
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation':'import','candidate':changed})
        engine.process_controls()
        current = engine.instance['knowledge'][value['id']]
        self.assertEqual(current['revision'], old['revision']+1)
        self.assertEqual(current['history'][-1]['summary'], old['summary'])
        self.assertEqual(current['status'], 'candidate')
        self.assertEqual(current['previous_review_cycle_id'], old['review_cycle_id'])
        self.drive(engine, lambda e: assess_use(e.instance['knowledge'][value['id']], e.instance)['valid'], limit=8)
        self.assertTrue(assess_use(engine.instance['knowledge'][value['id']], engine.instance)['valid'])
        self.assertNotEqual(engine.instance['knowledge'][value['id']]['review_cycle_id'], old['review_cycle_id'])

    def test_custom_kind_is_available_to_the_next_worker_schema(self):
        engine, _ = self.make()
        definition = {'family':'knowledge','token':'computational_lemma','meaning':'An explicitly bounded computational proposition.',
                      'constraints':{'mathematical_claim':False}}
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation':'register-kind','definition':definition})
        engine.process_controls()
        schema = engine._response_schema({'role':'research_work'})
        self.assertIn('computational_lemma', schema['properties']['knowledge']['items']['properties']['kind']['enum'])
