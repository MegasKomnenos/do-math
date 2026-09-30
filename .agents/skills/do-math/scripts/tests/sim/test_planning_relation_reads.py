"""A task reading a relation reads its endpoints, for revision order and user questions alike
(``planning.revision_waits``, ``questions.user_waits`` through ``relation_refs``; layer 2),
moved from ``test_relation_dependencies`` (``RelationReadTests``).

The legacy test published two knowledge records and a relation on a real Git
repository after a public ``initialize`` (``engine_fixtures.start_query_repository``)
and read the stored families back. Here the records are made by the same
producers (``knowledge_io.import_candidate``, ``import_relation``) on a restored
Sim's instance, published through its real ``ResearchRepository`` over the Git
port fake and loaded back from that head; the judgments are the product's pure
functions on the approved task of the record fixtures holding those families.
"""
from copy import deepcopy
import unittest

from do_math import planning, questions, revisions
from do_math.knowledge_io import import_candidate, import_relation
from record_fixtures import approve_task, approved_task
from support.sim import Sim, warm_template

setUpModule = warm_template

FAMILIES = ('knowledge', 'formal_results', 'expositions', 'identity_assessments', 'assessment_uses',
            'kind_definitions', 'relations')


def stored_relation():
    """``(stored instance, [One, Two], relation ID)``: definition One supports theorem Two, as published and loaded."""
    sim = Sim.activated()
    store, source = sim.engine.store, sim.instance_id
    head, instance, runtime = store.load(sim.engine.head)
    kids = []
    for title, kind, summary in (('One', 'definition', 'alpha'), ('Two', 'theorem', 'beta')):
        instance, runtime, kid = import_candidate(instance, runtime,
            {'kind': kind, 'title': title, 'statement': summary, 'summary': summary,
             'explanation': 'Explicit query fixture: ' + summary, 'lean_code': '',
             'declaration_names': [], 'dependencies': []}, source_ref=source, actor_ref=source)
        kids.append(kid)
    instance, relation_id = import_relation(instance,
        {'kind': 'supports', 'source': kids[0], 'target': kids[1], 'evidence': 'alpha'},
        source_ref=source, actor_ref=source)
    published = store.save_with_state(head, instance, runtime)[0]
    _, stored, _ = store.load(published)
    return stored, kids, relation_id


class RelationReadTests(unittest.TestCase):
    def test_indirect_endpoints_obey_both_revision_directions_and_question_gates(self):
        stored, kids, relation_id = stored_relation()
        self.assertEqual({kid: stored['knowledge'][kid]['title'] for kid in kids}, dict(zip(kids, ('One', 'Two'))))
        task, instance, runtime = approved_task()
        for family in FAMILIES:
            instance[family] = deepcopy(stored[family])
        task['inputs'].append(relation_id)
        approve_task(task, instance, runtime)
        self.assertEqual(planning.task_ready(task, instance, runtime)['state'], 'ready')
        reader = {'id': 'AC-reader', 'role': 'research_work', 'target': task['id']}
        for endpoint in kids:
            with self.subTest(endpoint=endpoint):
                writer = {'id': 'AC-writer', 'role': 'research_preparation',
                    'revision_targets': revisions.capture_targets(instance, runtime, [endpoint])}
                runtime['executions'] = {'EX-reader': {'id': 'EX-reader', 'status': 'running', 'action': reader}}
                self.assertTrue(planning.revision_waits(writer, instance, runtime))
                runtime['executions'] = {}
                runtime['queue'] = [writer]
                self.assertTrue(planning.revision_waits(reader, instance, runtime))
                runtime['queue'] = []
                runtime['question_links'] = []
                question = questions.link(runtime, execution_id='EX-question', field='answer',
                    owner='user', targets=[endpoint], blocks=True)
                self.assertEqual(questions.user_waits(reader, instance, runtime)[0]['question_id'], question['id'])
        runtime['question_links'] = []
        questions.link(runtime, execution_id='EX-other', field='answer', owner='user', targets=['KN-unrelated'], blocks=True)
        self.assertEqual(questions.user_waits(reader, instance, runtime), [])


if __name__ == '__main__':
    unittest.main()
