"""조사 소유자의 실제 등록·원천 보존·실패 인계 경로."""
from copy import deepcopy
import hashlib

from do_math import review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.review_inputs import review_stage_output
from support.review_scene import warm


def setUpModule():
    warm()


class ResearchOwnerContractTests(ReviewOwnerCase):
    def investigation(self):
        cid, parent, execution = self.registered()
        requests = [{'id': 'domain', 'question': '공리의 정확 범위는 무엇인가',
                     'source_refs': ['proposal:formal.axioms', 'proposal:lean_code']}]
        execution['extensions'] = {'research_requests': requests}
        cycle = self.engine.runtime['review_cycles'][cid]
        provisional = review_stage_output(cycle, 'initial', decision='unresolved', scope_complete=False)
        self.assertTrue(self.engine._defer_review_for_research(parent, provisional, execution['id']))
        action = deepcopy(next(a for a in self.engine.runtime['queue'] if a['role'] == 'supplemental_research'))
        request = self.engine.runtime['review_cycles'][cid]['research'][action['research_request_id']]
        answer = {'summary': '고정 질문을 확인했다', 'used_sources': [request['source_refs'][0]], 'questions': [],
                  'research_request_id': request['id'], 'request_digest': request['request_digest'],
                  'outcome': 'answered', 'answer': '정확 원문에서 확인', 'scope_complete': True,
                  'evidence_refs': [request['source_refs'][0]]}
        return cid, action, answer

    def registered_investigation(self):
        cid, action, answer = self.investigation()
        execution = self.engine._register_execution(action, {'id': 'EX-investigation', 'role': 'supplemental_research',
            'status': 'running', 'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        self.assertIsNotNone(execution)
        return cid, action, answer, execution

    def test_wrong_requesting_slot_is_rejected_without_mutation(self):
        _, action, _ = self.investigation()
        self.assert_engine_rejected('review investigation points to a different requesting slot',
            lambda: self.engine._pending_review_research({**action, 'requesting_slot': 'other'}))

    def test_research_schema_pins_question_and_digest(self):
        _, action, answer = self.investigation()
        schema = self.engine._review_research_schema(action)
        self.assertEqual(schema['properties']['research_request_id']['enum'], [answer['research_request_id']])
        self.assertEqual(schema['properties']['request_digest']['enum'], [answer['request_digest']])
        self.assertFalse(schema['additionalProperties'])

    def test_acceptance_requires_matching_execution_before_consumption(self):
        _, action, answer, execution = self.registered_investigation()
        execution['action']['research_request_id'] = 'other'
        self.assert_engine_rejected('research result has no matching assigned execution',
            lambda: self.engine._apply_review_research(action, answer, execution['id']))

    def test_workspace_evidence_requires_preserved_artifact(self):
        _, action, answer, execution = self.registered_investigation()
        answer['evidence_refs'] = ['workspace:missing.txt']
        self.assert_engine_rejected('investigation evidence file was not preserved',
            lambda: self.engine._apply_review_research(action, answer, execution['id']))

    def test_fixed_sources_used_twice_are_not_duplicated_in_receipt(self):
        cid, action, answer, execution = self.registered_investigation()
        request = deepcopy(self.engine.runtime['review_cycles'][cid]['research'][action['research_request_id']])
        self.engine._apply_review_research(action, answer, execution['id'])
        result = self.engine.runtime['review_cycles'][cid]['research'][request['id']]['result']
        self.assertEqual(result['source_records'], request['source_records'])
        self.assertEqual(result['output'], answer)
        self.assertEqual(result['execution_id'], execution['id'])
        before = deepcopy(self.engine.runtime)
        self.assertEqual(self.engine._obsolete_review_reason(action), 'The fixed investigation is no longer pending')
        self.assertFalse(self.engine._abandon_review_research(action, execution['id'], '이미 소비됨'))
        self.assertEqual(self.engine.runtime, before)

    def test_followup_reservation_evidence_cannot_omit_mandatory_slots(self):
        from do_math.execution_lifecycle import end_preparation
        cid, action, _ = self.investigation()
        for index in range(24):
            execution = self.engine._register_execution(action, {'id': f'EX-failed-research-{index}',
                'role': 'supplemental_research', 'status': 'queued'})
            if execution is None:
                break
            end_preparation(execution, at=self.engine.ports.clock.now(), stage='context', reason='합성 준비 중단', cancelled=True)
        else:
            self.fail('24번 안에 필수 후속 예약이 입장을 거부해야 한다')
        cycle = deepcopy(self.engine.runtime['review_cycles'][cid])
        record = rc.resource_disposition(cycle)
        self.assertEqual(record['reason'], 'review_followup_reserved')
        self.assertEqual(rc.validate_resource_disposition(cycle, self.engine.runtime), record)
        record['detail']['reserved_execution_slots'] = []
        with self.assertRaisesRegex(ValueError, 'review followup fits the available resources'):
            rc.validate_resource_disposition(cycle, self.engine.runtime)

    def test_failed_investigation_returns_once_with_original_wait_and_question(self):
        cid, action, _, execution = self.registered_investigation()
        wait = {'kind': 'provider_wait', 'action': deepcopy(action)}
        self.engine.runtime['waiting_actions'] = {action['id']: deepcopy(wait)}
        self.assertTrue(self.engine._finish_failed_investigation(action, execution['id'], '공급자 중단'))
        event = self.engine.runtime['history'][-1]
        self.assertEqual(event, {'kind': 'failed_investigation_returned', 'execution_id': execution['id'],
            'research_request_id': action['research_request_id'], 'review_cycle_id': cid,
            'reason': '공급자 중단', 'previous': wait})
        self.assertNotIn(action['id'], self.engine.runtime['waiting_actions'])
        cycle = self.engine.runtime['review_cycles'][cid]
        request = cycle['research'][action['research_request_id']]
        self.assertEqual(request['result']['execution_status'], 'incomplete')
        self.assertEqual(request['result']['output']['questions'], [request['question']])
        self.assertEqual(request['result']['output']['outcome'], 'unresolved')
        self.assertIn(request['action'], rc.next_actions(cycle))
        before = deepcopy(self.engine.runtime)
        self.assertFalse(self.engine._finish_failed_investigation(action, execution['id'], '반복'))
        self.assertEqual(self.engine.runtime, before)

    def test_research_deferral_rejects_wrong_execution_assignment(self):
        _, action, execution = self.registered()
        execution['extensions'] = {'research_requests': [{'id': 'r', 'question': '범위는 무엇인가', 'source_refs': ['proposal']}]}
        execution['action']['slot'] = 'other'
        self.assert_engine_rejected('research request execution was assigned to another review slot',
            lambda: self.engine._defer_review_for_research(action, {}, execution['id']))

    def test_research_source_spec_reads_own_transcript_and_knowledge_projection(self):
        cid, action = self.opened()
        cycle = rc.record_turn(self.engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'tool', 'message_id': 'tool', 'content': '정확 공개 도구 결과'}])
        self.engine.runtime['review_cycles'][cid] = cycle
        context = self.engine._prepare_review_context(action, self.root / 'source-context')['context']
        reference = context['source_refs'][0]['ref']
        own = self.engine._research_source_spec(cycle, action, reference)
        self.assertEqual(own, rc.inline_source_row(reference, cycle['turns'][action['slot']][0]))
        from do_math import knowledge_records as kr
        expected = {**rc.review_proposal(self.engine.instance, 'K1'), 'usable_links': kr.usable_links(self.engine.instance, 'K1')}
        self.assertEqual(self.engine._research_source_spec(cycle, action, 'K1'), rc.inline_source_row('K1', expected))

    def test_research_source_spec_preserves_actual_repository_bytes_and_snapshot(self):
        raw = '보존된 입력 원문'.encode('utf-8')
        path = 'runtime/artifacts/review-source/source.txt'
        self.engine._save({path: raw})
        cid, action = self.opened()
        source = {'id': 'S-review', 'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        self.engine._prepare_review_context(action, self.root / 'supplied', sources=[source])
        row = self.engine._research_source_spec(self.engine.runtime['review_cycles'][cid], action, 'S-review')
        self.assertEqual(row, {'ref': 'S-review', 'artifact_ref': path, 'snapshot': self.engine.head,
                              'sha256': source['sha256'], 'bytes': len(raw)})
        visible = self.engine._materialize_research_sources([row], self.root / 'source-bytes')
        self.assertEqual((self.root / 'source-bytes' / visible[0]['local_path']).read_bytes(), raw)

    def test_fixed_question_context_keeps_original_bytes_after_unrelated_publication(self):
        cid, action, _ = self.investigation()
        request = deepcopy(self.engine.runtime['review_cycles'][cid]['research'][action['research_request_id']])
        self.engine._save({'runtime/artifacts/unrelated/note.txt': b'unrelated publication'})
        head = self.engine.head
        context = self.engine._review_research_context(action, self.root / 'frozen')
        from support.engine_context import assert_review_documents
        cycle = self.engine.runtime['review_cycles'][cid]
        assert_review_documents(self, context['review_research'], owner='review_research', cycle=cycle,
                                request=request, engine=self.engine, workspace=self.root / 'frozen')
        assert_review_documents(self, context['review_research']['sources'], owner='review_sources',
                                sources=request['source_records'], engine=self.engine, workspace=self.root / 'frozen')
        workspace = self.root / 'frozen'
        final = context['review_research']
        for field in ('question', 'id', 'request_digest', 'proposal_digest', 'sources'):
            changed = deepcopy(final)
            del changed[field]
            with self.subTest(missing=field), self.assertRaises(AssertionError):
                assert_review_documents(self, changed, owner='review_research', cycle=cycle, request=request,
                                        engine=self.engine, workspace=workspace)
        borrowed = workspace / 'input' / 'borrowed.json'
        borrowed.write_bytes((workspace / final['sources'][0]['local_path']).read_bytes())
        for field in ('ref', 'local_path', 'sha256', 'bytes'):
            changed = deepcopy(final['sources'])
            del changed[0][field]
            with self.subTest(source_missing=field), self.assertRaises(AssertionError):
                assert_review_documents(self, changed, owner='review_sources', sources=request['source_records'],
                                        engine=self.engine, workspace=workspace)
        for fault in ('borrowed_path', 'general_sources', 'other_ref'):
            changed = deepcopy(final['sources'])
            if fault == 'borrowed_path':
                changed[0]['local_path'] = 'input/borrowed.json'
            elif fault == 'general_sources':
                changed[0] = {'id': changed[0]['ref'], 'path': changed[0]['local_path'],
                              'sha256': changed[0]['sha256'], 'bytes': changed[0]['bytes']}
            else:
                changed[0]['ref'] = changed[1]['ref']
            with self.subTest(source_fault=fault), self.assertRaises(AssertionError):
                assert_review_documents(self, changed, owner='review_sources', sources=request['source_records'],
                                        engine=self.engine, workspace=workspace)
        local = workspace / final['sources'][0]['local_path']
        original = local.read_bytes()
        local.write_bytes(b'damaged delivered source')
        with self.assertRaises(AssertionError):
            assert_review_documents(self, final['sources'], owner='review_sources', sources=request['source_records'],
                                    engine=self.engine, workspace=workspace)
        local.unlink()
        with self.assertRaises(FileNotFoundError):
            assert_review_documents(self, final['sources'], owner='review_sources', sources=request['source_records'],
                                    engine=self.engine, workspace=workspace)
        local.write_bytes(original)
        self.assertEqual(context['review_research']['question'], request['question'])
        self.assertEqual(context['review_research']['request_digest'], request['request_digest'])
        self.assertEqual(context['proposal'], self.engine.runtime['review_cycles'][cid]['proposal'])
        for actual, fixed in zip(context['review_research']['sources'], request['source_records'], strict=True):
            self.assertEqual((self.root / 'frozen' / actual['local_path']).read_bytes(), rc.inline_source_bytes(fixed))
        self.assertEqual(self.engine.head, head)
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['research'][request['id']], request)

    def test_fixed_question_rejects_changed_proposal_before_materializing(self):
        _, action, _ = self.investigation()
        exposition = self.engine.instance['expositions'][self.engine.instance['knowledge']['K1']['exposition_id']]
        next(item for item in exposition['items'] if item['kind'] == 'statement')['text'] = '별개의 명제'
        self.assert_engine_rejected('sealed mathematical proposal changed during review',
            lambda: self.engine._review_research_context(action, self.root / 'stale'))
        self.assertFalse((self.root / 'stale').exists())

    def test_provisional_acceptance_rechecks_frozen_scope_before_deferral(self):
        cid, action, execution = self.registered()
        execution['extensions'] = {'research_requests': [{'id': 'fixed', 'question': '정확 범위는 무엇인가',
                                                        'source_refs': ['proposal']}]}
        provisional = review_stage_output(self.engine.runtime['review_cycles'][cid], 'initial',
                                          decision='unresolved', scope_complete=False)
        self.engine.runtime['review_cycles'][cid]['activity_execution_limit'] += 1
        self.assert_engine_rejected('review inputs changed before acceptance',
            lambda: self.engine._defer_review_for_research(action, provisional, execution['id']))
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['research'], {})

    def test_completed_investigation_is_private_until_requesting_slot_is_sealed(self):
        cid, action, answer, execution = self.registered_investigation()
        self.engine._apply_review_research(action, answer, execution['id'])
        cycle = self.engine.runtime['review_cycles'][cid]
        requester = cycle['research'][action['research_request_id']]['action']
        peer = next(a for a in rc.next_actions(cycle) if a['slot'] != requester['slot'])
        own = rc.context_for(cycle, requester)
        other = rc.context_for(cycle, peer)
        self.assertEqual([r['id'] for r in own['supplemental_results']], [action['research_request_id']])
        self.assertEqual(other['supplemental_results'], [])
        self.assertEqual(other['self_messages'], [])
        self.assertEqual(other['completed_results'], {})
        final = rc.accept_result(cycle, requester, review_stage_output(cycle, 'initial'), 'EX-final-requester')
        objection = review_stage_output(final, 'initial', decision='mismatch', findings=[
            {'id': 'scope', 'statement': '추가 범위 판정 필요', 'evidence': ['proposal']}])
        final = rc.accept_result(final, peer, objection, 'EX-final-peer')
        organize = rc.next_actions(final)[0]
        self.assertEqual(organize['stage'], 'organize')
        public = rc.context_for(final, organize)
        self.assertEqual([r['id'] for r in public['supplemental_results']], [action['research_request_id']])
        self.assertEqual(len(public['completed_results']), 2)


    def test_prepared_source_uses_its_snapshot_after_head_advances(self):
        raw = '고정 당시의 원천'.encode('utf-8')
        path = 'runtime/artifacts/frozen-source/source.txt'
        self.engine._save({path: raw})
        cid, action = self.opened()
        source = {'id': 'S-frozen', 'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        self.engine._prepare_review_context(action, self.root / 'pinned-source', sources=[source])
        snapshot = self.engine.head
        self.engine._save({'runtime/artifacts/later-source/source.txt': b'later source'})
        self.assertNotEqual(self.engine.head, snapshot)
        row = self.engine._research_source_spec(self.engine.runtime['review_cycles'][cid], action, 'S-frozen')
        self.assertEqual(row, {'ref': 'S-frozen', 'artifact_ref': path, 'snapshot': snapshot,
                              'sha256': source['sha256'], 'bytes': len(raw)})
        visible = self.engine._materialize_research_sources([row], self.root / 'restored-frozen', slot=action['slot'])
        self.assertEqual((self.root / 'restored-frozen' / visible[0]['local_path']).read_bytes(), raw)
        from support.engine_context import assert_review_documents
        assert_review_documents(self, visible, owner='review_sources', sources=[row], engine=self.engine,
                                workspace=self.root / 'restored-frozen')
        for field in ('snapshot', 'artifact_ref', 'ref'):
            changed = deepcopy(visible)
            changed[0][field] = 'another-source-coordinate'
            with self.subTest(artifact_coordinate=field), self.assertRaises(AssertionError):
                assert_review_documents(self, changed, owner='review_sources', sources=[row], engine=self.engine,
                                        workspace=self.root / 'restored-frozen')
