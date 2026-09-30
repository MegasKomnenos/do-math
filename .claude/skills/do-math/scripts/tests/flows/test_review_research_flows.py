"""Fixed-question review investigations the owner runs (설계 4.1): deferral, investigation, resumption, stop and revision.

Every test restores ``support.review_research.research_sim``: the purpose
scenario on a Sim whose task A produced the theorem ``add_zero_fixture``, which
the owner verified through the Lean double and whose identity review it just
opened. The model double answers as ``InvestigationResponder``: the first
initial reviewer asks fixed questions, investigators answer them from their
fixed sources, and its input checks (returned source hashes, no inherited
task contract, the purpose runner's checks) fail the test at once through
``support.engine_purpose.drive``. Each attempt runs through the owner's
registration and admission, a Job, the worker and the workspace submission
tool; nothing in the engine is replaced. The flows are longer than the Sim
budget because each owner pass here runs one model call (about 2 s).
Moved from ``test_review_research`` (``ReviewResearchEngineTests``), which ran
the real engine with ``InvestigationRunner`` in real Windows Jobs.
"""
from copy import deepcopy
from datetime import timedelta
import unittest

from do_math import knowledge, knowledge_records as kr
from do_math.canonical import canonical_json
from do_math.contracts import prompt_documents
from do_math.execution_profiles import resolve_profile
from do_math.review_cycle import next_actions
from purpose_fixtures import EXPLANATION
from support.engine_lifecycle import applied
from support.engine_overflow import apply_limit
from support.engine_purpose import drive
from support.fakes.jobs import job_turn
from support.review_research import InvestigationResponder, research_sim


def setUpModule():
    # Build both templates now (about 10 s each), so no test pays a build.
    research_sim()
    research_sim(review_research_limit=1)


def research(*, repeat=False, batch=False, **config):
    """``(sim, responder)``: the restored scene with ``InvestigationResponder`` answering its model calls."""
    sim = research_sim(**config)
    sim.model.responder = InvestigationResponder(repeat=repeat, batch=batch)
    return sim, sim.model.responder


def revise(sim, knowledge_id, sentence, reason):
    """The user's public revision of ``knowledge_id``'s explanation, with the impact the product computes."""
    roots = knowledge.revision_roots(sim.instance, knowledge_id)
    applied(sim, 'knowledge', config={'operation': 'revise', 'id': knowledge_id,
        'changes': {'explanation': EXPLANATION + sentence},
        'declared_impact': knowledge.plan_impact(sim.instance, sim.runtime, roots, [])['computed_impact'],
        'reason': reason})


class ResearchFlowTests(unittest.TestCase):
    def test_common_document_overflow_waits_without_reconstructing_the_proposal(self):
        """The review's mandatory common documents alone exceed the input limit of the profile its attempt runs under.

        The limit is the byte size of the installed documents the identity
        review reads, adopted by the public configuration and probe (as the
        CLI's ``configure`` does) after the review opened; the attempt is
        prepared under the new profile edition, so this is the actual limit.
        """
        sim, _ = research()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'identity_review')
        knowledge_id = action['target']
        before = deepcopy(sim.instance['knowledge'][knowledge_id])
        limit = sum(len(document['content'].encode('utf-8')) for document in prompt_documents('identity_review'))
        apply_limit(sim, limit, 'UC-document-limit')
        calls = [row['action']['id'] for row in sim.model.calls if row['role'] == 'identity_review']
        # A blocked review must not call its model. The lowered limit also stops
        # queued research_plan work, so wait for this action's own overflow receipt.
        drive(self, sim, predicate=lambda s: any(
            w['action'].get('id') == action['id'] and w.get('reason') == 'input_overflow'
            for w in s.runtime.get('waiting_actions', {}).values()), limit=6)
        self.assertEqual([row['action']['id'] for row in sim.model.calls if row['role'] == 'identity_review'], calls)
        self.assertEqual(sim.instance['knowledge'][knowledge_id], before)
        self.assertTrue(any(w['action'].get('id') == action['id'] and w['reason'] == 'input_overflow'
                            for w in sim.runtime.get('waiting_actions', {}).values()))
        self.assertFalse(any(row.get('event') == 'review_resource_disposition'
                             for row in sim.runtime['review_cycles'][action['review_cycle_id']]['history']))
        wait = next(w for w in sim.runtime['waiting_actions'].values() if w['action']['id'] == action['id'])
        self.assertEqual((wait['detail']['cause'], wait['detail']['limit_bytes']), ('common_documents_or_governance', limit))
        question = next(q for q in sim.runtime['question_links'] if q['id'] == wait['question_id'])
        self.assertEqual(question['status'], 'open')
        self.assertIn(knowledge_id, question['target_ids'])

    def test_all_fixed_questions_return_before_resuming_the_deferred_slot(self):
        sim, responder = research(batch=True)
        drive(self, sim, predicate=lambda s: bool(responder.resumed_contexts)
              and any(c['decision'] == 'match' for c in s.runtime['review_cycles'].values()))
        self.assertEqual(len(responder.research_answers), 2)
        self.assertEqual(len(responder.resumed_contexts), 1)
        self.assertEqual(len(responder.resumed_contexts[0]['supplemental_results']), 2)
        cycle = next(iter(sim.runtime['review_cycles'].values()))
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(sum(row['action']['stage'] == 'initial' for row in cycle['results'].values()), 2)
        self.assertIn('scope:1:scope', cycle['results'])
        self.assertFalse(cycle['deferred_actions'])
        requests = list(cycle['research'].values())
        self.assertEqual(len(requests), 2)
        self.assertEqual(responder.resumed_contexts[0]['action']['slot'], 'initial-0')
        self.assertTrue(any(message['role'] == 'tool' and message.get('kind') == 'supplemental_research'
                            for message in cycle['turns']['initial-0']))
        self.assertIn('declaration_signatures', cycle['proposal']['formal'])
        self.assertIn('signature_hash', cycle['proposal']['formal'])
        final_id = next(result['execution_id'] for result in cycle['results'].values()
                        if result['action']['slot'] == 'initial-0')
        for request in requests:
            investigation = sim.runtime['executions'][request['result']['execution_id']]
            self.assertEqual(investigation['role'], 'supplemental_research')
            # An investigation is work: its immutable profile reserves a work slot.
            self.assertTrue(resolve_profile(sim.instance['execution_profiles'],
                                            investigation['execution_profile_ref'])['ai']['capacity_refs'])
            self.assertEqual(request['action']['slot'], 'initial-0')
            self.assertNotEqual(request['requested_by'], investigation['id'])
            self.assertNotEqual(final_id, request['requested_by'])
            self.assertNotIn(request['requested_by'], {r['execution_id'] for r in cycle['results'].values()})
        actual_roles = [call['role'] for call in responder.calls]
        research_positions = [i for i, role in enumerate(actual_roles) if role == 'supplemental_research']
        resumed_position = next(i for i, call in enumerate(responder.calls) if call['role'] == 'identity_review'
            and call['action']['slot'] == 'initial-0' and call['context']['role_review']['supplemental_results'])
        self.assertGreater(resumed_position, max(research_positions))

    def test_repeated_unanswered_request_closes_unresolved_at_the_activity_limit(self):
        sim, responder = research(repeat=True, review_research_limit=1)
        drive(self, sim, predicate=lambda s: any(c['status'] == 'unresolved' for c in s.runtime['review_cycles'].values()))
        cycle = next(iter(sim.runtime['review_cycles'].values()))
        self.assertEqual(len(responder.research_answers), 1)
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertTrue(cycle['followup'])
        # Why it closed: the repeated question exceeds the investigation limit and the review's remaining attempts.
        [closing] = [row for row in cycle['history'] if row.get('event') == 'investigation_limit_closed']
        self.assertEqual((closing['action']['slot'], closing['limit'], closing['budget_available']), ('initial-0', 1, False))
        self.assertEqual([row['reason'] for row in cycle['followup']],
                         ['supplemental investigation limit or reserved review budget exhausted'])
        self.assertFalse(any(kr.usable_links(sim.instance, kid) for kid in sim.instance['knowledge']))
        self.assertFalse(any(a.get('review_cycle_id') == cycle['id'] for a in sim.runtime['queue']))
        self.assertTrue(any('external textbook definition' in (question.get('text') or '') for question in sim.engine._question_view()))

    def test_user_revision_cancels_old_investigation_and_reviews_new_revision(self):
        sim, _ = research()
        drive(self, sim, predicate=lambda s: any(a['role'] == 'supplemental_research' for a in s.runtime['queue']))
        item = next(iter(sim.instance['knowledge'].values()))
        old_cycle_id = item['review_cycle_id']
        revise(sim, item['id'], ' The revised statement explicitly retains that domain.', 'Explicit source revision')
        self.assertFalse(any(a.get('review_cycle_id') == old_cycle_id for a in sim.runtime['queue']))
        old_cycle = sim.runtime['review_cycles'][old_cycle_id]
        self.assertEqual(old_cycle['status'], 'unresolved')
        self.assertTrue(all(r['status'] == 'cancelled' for r in old_cycle['research'].values()))
        drive(self, sim, predicate=lambda s: any(row.get('supersedes') == item['id']
              and kr.usable_links(s.instance, row['id']) for row in s.instance['knowledge'].values()))
        replacement = next(row for row in sim.instance['knowledge'].values() if row.get('supersedes') == item['id'])
        self.assertNotEqual(replacement['review_cycle_id'], old_cycle_id)
        self.assertTrue(kr.usable_links(sim.instance, replacement['id']))

    def test_supplemental_evidence_is_readable_again_in_the_next_revision(self):
        sim, responder = research()
        drive(self, sim, predicate=lambda s: any(kr.usable_links(s.instance, kid) for kid in s.instance['knowledge']))
        item = next(iter(sim.instance['knowledge'].values()))
        revise(sim, item['id'], ' This revision adds an explicit domain reminder.', 'New proposal revision')
        drive(self, sim, predicate=lambda s: len(responder.resumed_contexts) >= 2
              and any(row.get('supersedes') == item['id'] and kr.usable_links(s.instance, row['id'])
                      for row in s.instance['knowledge'].values()))
        self.assertEqual(len(responder.research_answers), 1)
        self.assertEqual(len(responder.resumed_contexts), 2)
        self.assertIn('previous_revision', responder.resumed_contexts[-1]['supplemental_results'][0])

    def test_inline_stop_returns_execution_incomplete_to_the_requesting_slot(self):
        """The owner stops a running investigation alone: its incomplete result returns to the slot that asked.

        The Jobs fake runs live (이음매 장부 18), so the owner takes a pass at
        each of the investigator's turns. While it runs, having written a
        blocked checkpoint, the user replaces the research grant it holds by
        public control; the owner applies the decision, which revokes that grant
        and requests a stop of its consumers (``grant_revoked``), judges the stop
        and terminates the Job at the investigator's next turn. The instance
        itself neither pauses nor stops.
        """
        sim, responder = research()
        original, stops = responder.runner.answer, []
        replaced = sim.instance['grants']['GR-research-sim']

        def stopped(role, context, workspace):
            if role != 'supplemental_research':
                return original(role, context, workspace)
            (workspace / 'checkpoint.json').write_bytes(canonical_json({'current_claim': 'Investigation is blocked',
                'evidence_paths': [], 'attempts': ['Checked fixed inputs'], 'remaining_work': ['Resolve the fixed question'],
                'next_step': 'Return the exact missing evidence', 'progress_state': 'blocked'}))
            grant = {**{key: replaced[key] for key in ('kind', 'roles', 'reuse')}, 'id': 'GR-research-next',
                     'expires_at': (sim.clock.wall() + timedelta(days=2)).isoformat()}
            stops.append(context['action']['id'])
            sim.control('decision', text='Replace the research grant while its investigation runs',
                        config={'change': {'kind': 'grant', 'grant': grant, 'replaces': ['GR-research-sim']}})
            for _ in range(30):
                job_turn()  # a terminated Job ends the investigator here
            raise AssertionError('the owner did not stop the investigation whose grant was replaced')
        responder.runner.answer = stopped
        sim.jobs.live = True
        drive(self, sim, predicate=lambda s: any(r.get('result', {}).get('execution_status') == 'incomplete'
              for c in s.runtime['review_cycles'].values() for r in c.get('research', {}).values() if r.get('result')))
        cycle = next(iter(sim.runtime['review_cycles'].values()))
        self.assertEqual(cycle['status'], 'working')
        self.assertNotEqual(sim.runtime['status'], 'paused')
        self.assertFalse(cycle['deferred_actions'])
        self.assertTrue(any(a['slot'] == 'initial-0' for a in next_actions(cycle)))
        request = next(iter(cycle['research'].values()))
        self.assertEqual(request['status'], 'unresolved')
        self.assertEqual(request['result']['output']['outcome'], 'unresolved')
        # The result came back through the owner's stop of that one execution.
        investigation = sim.runtime['executions'][request['result']['execution_id']]
        self.assertEqual([investigation['action']['id']], stops)
        self.assertEqual((investigation['stop_reason'], investigation['outcome']), ('grant_revoked', 'execution_incomplete'))
        self.assertIn(investigation['id'], [row['execution_id'] for row in sim.runtime['history']
                                            if row.get('kind') == 'failed_investigation_returned'])


if __name__ == '__main__':
    unittest.main()
