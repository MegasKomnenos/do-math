"""실제 후보 생산 후 고정 질문 조사에 지급하는 독립 입력."""
from copy import deepcopy
import unittest

from support.review_research import research_sim, InvestigationResponder


class BlindInputTests(unittest.TestCase):
    def test_actual_investigation_context_blocks_peer_ledger_and_author_context(self):
        """실제 준비·후보·조사 작업자 연쇄가 필요하다. 최초 sim 측정 18.2초로 flows에 둔다."""
        sim = research_sim()
        seen = []
        class ObservedResponder(InvestigationResponder):
            def respond(self, role, context, workspace):
                if role == 'supplemental_research':
                    seen.append(deepcopy(context))
                return super().respond(role, context, workspace)
        base = ObservedResponder()
        sim.model.responder = base
        sim.run_until(lambda s: bool(seen), max_steps=12)
        self.assertEqual(base.failures, [])
        self.assertEqual(len(seen), 1)
        context = seen[0]
        self.assertIn('review_research', context)
        for key in ('tasks', 'recent_history', 'open_questions', 'question_links'):
            self.assertNotIn(key, context)
        execution = next(e for e in sim.runtime['executions'].values() if e['role'] == 'supplemental_research')
        self.assertEqual(execution['context_origin'], [])
