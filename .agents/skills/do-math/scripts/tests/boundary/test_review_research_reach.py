"""What a review seat and an investigator actually receive before the initial phase seals (설계 4.1).

The scene is ``support.review_research.research_sim``: the owner runs the
identity review of the theorem task A produced, through its registration, a
Job, the worker and the model double (``InvestigationResponder``). At the
peer's call, ``research_fixtures.role_reach`` looks where a secret reaches
the role: its actual prompt (``record_prompts``), its workspace files, and
through its installed read tool every indexed record and every snapshot file
that holds the secret (preserved rule K-48: an empty ``held`` proves nothing).
The read tool runs in its own process from the support archive and reads the
input snapshot through its own ``GitStateStore`` with no ports, so the Sim's
Git objects are written out as loose objects (``support.review_sim.export_objects``)
and a real ``git`` reads them; that real Git process and child process place
these tests with the boundary tests (``test_role_input_snapshot_reach`` for
the same reason). Moved from ``test_review_research`` (``ReviewResearchEngineTests``).
"""
import unittest
from test_categories import test_group

from support.purpose_answers import common
from support.cli_inputs import role_reach
from support.engine_purpose import drive
from support.review_research import InvestigationResponder, record_prompts, research_sim
from support.review_sim import export_objects


def setUpModule():
    research_sim()


def research():
    """``(sim, responder, prompts)``: the restored scene answered by ``InvestigationResponder``, its prompts recorded."""
    sim = research_sim()
    sim.model.responder = InvestigationResponder()
    return sim, sim.model.responder, record_prompts(sim)


def reach_of(sim, prompts, workspace, secret):
    """``role_reach`` of the call in progress, with the Sim's Git objects readable by a real ``git``."""
    export_objects(sim)
    return role_reach(prompts[-1], workspace, secret)


@test_group('resource')
class ResearchReachTests(unittest.TestCase):
    def test_initial_peer_question_is_not_exposed_before_phase_seal(self):
        """About 20 s: owner passes that each run a model call, and the read tool in a child process on real Git."""
        sim, responder, prompts = research()
        original, secret, reach = responder.runner.answer, 'PRIVATE-PEER-DOMAIN-QUESTION', []

        def question(role, context, workspace):
            action = context['action']
            if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-0':
                return {**common('Review remains uncertain'), 'questions': [secret],
                    'proposal_digest': context['role_review']['proposal_digest'], 'decision': 'unresolved', 'scope_complete': True, 'findings': []}
            if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-1':
                # The peer seat of the unsealed initial phase, as its role actually receives it.
                reach.append(reach_of(sim, prompts, workspace, secret))
            return original(role, context, workspace)
        responder.runner.answer = question
        drive(self, sim, predicate=lambda s: bool(reach))
        (reached, held), = reach
        self.assertTrue(held, 'The input snapshot must hold the peer question for this check to mean anything')
        self.assertEqual(reached, [])

    def test_investigator_does_not_receive_unsealed_peer_summary(self):
        """About 20 s: owner passes that each run a model call, and the read tool in a child process on real Git."""
        sim, responder, prompts = research()
        original, secret, reach = responder.runner.answer, 'PRIVATE-PEER-SUMMARY', []

        def peer_summary(role, context, workspace):
            if role == 'supplemental_research':
                # The investigator of initial-0's fixed question, as its role actually receives it.
                reach.append(reach_of(sim, prompts, workspace, secret))
            output = original(role, context, workspace)
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-1':
                output['summary'] = secret
            return output
        responder.runner.answer = peer_summary
        drive(self, sim, predicate=lambda s: bool(reach))
        (reached, held), = reach
        self.assertTrue(held, 'The input snapshot must hold the peer summary for this check to mean anything')
        self.assertEqual(reached, [])


if __name__ == '__main__':
    unittest.main()
