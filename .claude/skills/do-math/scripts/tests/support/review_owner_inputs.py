"""저장 검증된 장면에서 실제 입장·등록·문맥 생산자를 사용한다."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import knowledge
from support.review_scene import ReviewScene


class ReviewOwnerCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine
        # 공통 장면이 인용하는 author를 실제 등록·종료 생산자로 완성한다.
        from do_math.execution_lifecycle import transition_execution
        author = self.engine._register_execution(
            {'id': 'AC-review-author', 'role': 'research_work'},
            {'id': 'author', 'role': 'research_work', 'status': 'running'})
        self.assertIsNotNone(author)
        transition_execution(author, 'stopping', at=self.engine.ports.clock.now())
        transition_execution(author, 'ended', at=self.engine.ports.clock.now(), outcome='execution_incomplete')
        self.root = Path(temporary.name)

    def opened(self, *, scope=False):
        cid = self.engine._start_identity_review('K1') if scope else self.scene.start('K1')
        return cid, deepcopy(self.scene.pending())

    def registered(self):
        cid, action = self.opened()
        execution = self.engine._register_execution(action, {
            'id': 'EX-review-owner', 'role': 'identity_review', 'status': 'running',
            'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        self.assertIsNotNone(execution)
        execution['input_snapshot'] = self.engine.head
        context = self.engine._prepare_review_context(action, self.root / 'input-context')
        self.assertEqual(context['disposition'], 'ready')
        return cid, action, execution

    def staged(self):
        engine = self.engine
        engine.instance['trust_environments']['TE-review-next'] = {
            'id': 'TE-review-next', 'status': 'registered',
            'toolchain': {'sha256': 'review-next-toolchain', 'version': '합성 다음 판'}, 'allowed_axioms': []}
        transition = knowledge.begin_transition(engine.instance, 'TE-review-next', clock=engine.ports.clock)
        fid = engine.instance['knowledge']['K1']['formal_result_id']
        result = deepcopy(engine.instance['formal_results'][fid]['verification'])
        result.update(id='K1', toolchain=engine.instance['trust_environments']['TE-review-next']['toolchain'])
        result['declaration_evidence']['sample']['value'] = '합성 새 증명항'
        transition = knowledge.record_transition_result(engine.instance, transition, result)
        engine.runtime['trust_transitions'][transition['id']] = transition
        return transition['id']

    def assert_engine_rejected(self, reason, call):
        before = deepcopy((self.engine.instance, self.engine.runtime))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, reason):
            call()
        self.assertEqual((self.engine.instance, self.engine.runtime), before)
        self.assertEqual(self.engine.head, head)
