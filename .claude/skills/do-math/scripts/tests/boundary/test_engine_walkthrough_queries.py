"""Design walkthrough 12 (통합-설계.md 17.3): a useful failed search keeps its epistemic status up to a published query.

The walkthrough runs on a restored active instance whose theorem ``k1`` the Lean
double verified and a sealed identity review matched
(``support.governance_sim.theorem_sim``). A research work result carrying the
metadata of a useful failed search is received by the engine; the published
state is then queried with ``query_records`` and ``read_record``. Those read
through ``ResearchRepository`` on the product's real Git process (they take no
Ports), so the Sim's objects are written out as loose objects first
(``support.review_sim.export_objects``) and the test lives with the boundary
tests. The legacy walkthrough published only the knowledge families of an
in-memory engine to a new ``git_init`` repository; here the engine's own state
is published.
"""
from copy import deepcopy
import unittest

from do_math import knowledge, knowledge_io, knowledge_records as kr
from do_math.engine import query_records, read_record
from support.engine_lifecycle import _ended_execution, task
from support.engine_walkthroughs import truth_candidate
from support.governance_sim import theorem_sim
from support.review_sim import export_objects


def setUpModule():
    theorem_sim()  # build the theorem template before the test, so the test does not pay for it


class DesignWalkthroughs(unittest.TestCase):
    def test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions(self):
        from support.entry import entry
        from do_math.wiring import real_ports
        _entry = entry()
        _entry.ports = real_ports(environment=_entry.environment)
        sim = theorem_sim()
        e = sim.engine
        kid = next(k for k, row in e.instance['knowledge'].items() if row['title'] == 'k1')
        record = e.instance['knowledge'][kid]
        (aid,) = [key for key, row in e.instance['identity_assessments'].items()
                  if (row['formal_result_id'], row['exposition_id'], row['decision'])
                  == (record['formal_result_id'], record['exposition_id'], 'match')]
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        task(e, 'TK-work')
        _ended_execution(e, 'EX-work', 'research_work')
        e.runtime['executions']['EX-work'].update(extensions={'knowledge_metadata': [{
            'title': 'Useful failed search', 'epistemic_status': 'exploratory',
            'selection_relevance': 'Avoid the exhausted finite search',
            'uncertainty_assessment': {'claim': 'Not a proof', 'scope': 'finite search only'}}]})
        useful = truth_candidate('Useful failed search', '')
        useful.update(title='Useful failed search', declaration_names=[], kind='observation')
        before = set(e.instance['knowledge'])
        e._apply({'id': 'AC-work', 'role': 'research_work', 'target': 'TK-work'}, {'report': 'No proof found',
                 'outcome': 'partial', 'remaining_work': ['general case'], 'knowledge': [useful], 'relations': [],
                 'questions': []}, 'EX-work')
        (imported,) = [row for key, row in e.instance['knowledge'].items() if key not in before]
        self.assertEqual(imported['selection_relevance'], 'Avoid the exhausted finite search')
        self.assertFalse(knowledge.assess_use(imported, e.instance)['valid'])
        e.instance = kr.set_assessment_use(e.instance, aid, 'suspended', 'new objection', 'review')
        self.assertFalse(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        e.instance, relation_id = knowledge_io.import_relation(e.instance, {
            'kind': 'supports', 'source': imported['id'], 'target': kid,
            'confirmed_scope': 'Search history informs reuse; no formal implication',
            'evidence_refs': [imported['id']]}, source_ref='fixture:search-history', actor_ref='EX-relation', clock=sim.ports.clock)
        e._save()
        head = e.head
        export_objects(sim)
        found = query_records(sim.repository, sim.instance_id, kind='knowledge', snapshot=head, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
        self.assertEqual(found['snapshot'], head)
        self.assertEqual({r['record']['id'] for r in found['items']}, {kid, imported['id']})
        record = read_record(sim.repository, sim.instance_id, imported['id'], snapshot=head, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
        self.assertEqual(record['record']['uncertainty_assessment'], {'claim': 'Not a proof', 'scope': 'finite search only'})
        outward = query_records(sim.repository, sim.instance_id, related_to=imported['id'], direction='outgoing', snapshot=head, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
        inward = query_records(sim.repository, sim.instance_id, related_to=imported['id'], direction='incoming', snapshot=head, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
        self.assertEqual({r['record']['id'] for r in outward['items']}, {kid, relation_id})
        self.assertEqual(inward['items'], [])
        self.assertTrue(outward['query_basis']['complete'])


if __name__ == '__main__':
    unittest.main()
