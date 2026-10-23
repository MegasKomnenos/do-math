"""Work/peer review boundaries and source attribution."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check import check_session
from knowledge_index import render_index


def envelope(category, **fields):
    return dict(category=category, overview={'title': category, 'summary': 'Bounded fixture'},
                references=[], supersedes=[], **fields)


def result(name):
    return {'id': name, 'exposition': 'note.md', 'verification': 'Fixture', 'lean': None}


def verdicts():
    return {key: {'verdict': value, 'reason': 'Fixture'} for key, value in
            [('assessment', 'supported'), ('lean', 'not_applicable'),
             ('alignment', 'not_applicable'), ('terminology', 'conforms')]}


class PeerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.knowledge = self.root / 'knowledge'
        self.knowledge.mkdir()
        self.context = self.root / 'context.md'
        self.context.write_text('Fixture', encoding='utf-8')
        self.work = envelope('research', results=[result('r1')], failed_attempts=[], open_questions=[])
        self.peer = envelope('peer', target={'kind': 'research', 'record': 'work'},
                             exposition='note.md', questions=[], results=[result('p1')])
        self.publish('work', self.work)
        self.publish('peer', self.peer)
        self.target = {'kind': 'bundle', 'work': 'work', 'peer': 'peer'}
        self.review = envelope('review', target=self.target, exposition='note.md', summary='Both checked',
            overview_assessments=[{'record': rid, 'assessment': {'verdict': 'supported', 'reason': 'Fixture'}}
                                  for rid in ['work', 'peer']],
            results=[dict(id='c1', source={'record': 'work', 'result': 'r1'}, **verdicts()),
                     dict(id='c2', source={'record': 'peer', 'result': 'p1'}, **verdicts())])

    def publish(self, rid, data):
        folder = self.knowledge / rid
        folder.mkdir(exist_ok=True)
        (folder / 'output.json').write_text(json.dumps(data), encoding='utf-8')
        (folder / 'note.md').write_text('Public evidence', encoding='utf-8')

    def check(self, data, target=None):
        session = self.root / 'session'
        output = session / 'output'
        output.mkdir(parents=True, exist_ok=True)
        task = {'instructions': 'Read and judge', 'references': [], 'target': target or data.get('target')}
        inp = {'instance': str(self.root), 'category': data['category'], 'task': task,
               'context': {'common': [str(self.context)], 'category': str(self.context)}}
        (session / 'input.json').write_text(json.dumps(inp), encoding='utf-8')
        (output / 'output.json').write_text(json.dumps(data), encoding='utf-8')
        (output / 'note.md').write_text('Evidence', encoding='utf-8')
        return check_session(session)

    def test_peer_and_bundle_valid(self):
        self.assertEqual(self.check(self.peer), [])
        self.assertEqual(self.check(self.review), [])

    def test_peer_without_new_results_is_valid(self):
        data = copy.deepcopy(self.peer)
        data['results'] = []
        self.assertEqual(self.check(data), [])

    def test_peer_cannot_issue_goal_or_overview_verdict(self):
        for key, value in [('goal', {'verdict': 'achieved'}), ('overview_assessment', {'verdict': 'supported'})]:
            data = copy.deepcopy(self.peer)
            data[key] = value
            self.assertTrue(self.check(data))

    def test_bundle_must_match_peer_work(self):
        other = copy.deepcopy(self.work)
        self.publish('other', other)
        data = copy.deepcopy(self.review)
        data['target']['work'] = 'other'
        self.assertTrue(self.check(data))

    def test_missing_or_duplicate_source_result_is_rejected(self):
        data = copy.deepcopy(self.review)
        data['results'].pop()
        self.assertTrue(self.check(data))
        data['results'].append(dict(id='c3', source={'record': 'work', 'result': 'r1'}, **verdicts()))
        self.assertTrue(self.check(data))

    def test_cross_record_source_and_unknown_result_rejected(self):
        for source in [{'record': 'other', 'result': 'r1'}, {'record': 'work', 'result': 'p1'}]:
            data = copy.deepcopy(self.review)
            data['results'][0]['source'] = source
            self.assertTrue(self.check(data))

    def test_exploration_has_precise_prose_claims(self):
        self.work = envelope('explore', exposition='note.md', questions=[])
        self.peer['target']['kind'] = 'explore'
        self.publish('work', self.work)
        self.publish('peer', self.peer)
        data = copy.deepcopy(self.review)
        data['results'][0]['source'] = {'record': 'work', 'file': 'note.md', 'statement': 'For every n, bounded claim'}
        self.assertEqual(self.check(data), [])
        del data['results'][0]['source']['statement']
        self.assertTrue(self.check(data))

    def test_both_overviews_required(self):
        data = copy.deepcopy(self.review)
        data['overview_assessments'].pop()
        self.assertTrue(self.check(data))

    def test_peer_result_reference_and_bundle_result_reference(self):
        self.publish('review', self.review)
        data = copy.deepcopy(self.peer)
        data['references'] = [{'record': 'peer', 'result': 'p1'}, {'record': 'review', 'result': 'c1'}]
        self.assertEqual(self.check(data), [])

    def test_bundle_supersession_cannot_erase_other_target(self):
        self.publish('old', envelope('review', target={'kind': 'research', 'record': 'work'}))
        data = copy.deepcopy(self.review)
        data['supersedes'] = ['old']
        self.assertTrue(self.check(data))
        self.publish('old', self.review)
        self.assertEqual(self.check(data), [])

    def test_index_keeps_links_and_detects_old_new_conflict(self):
        old = envelope('review', target={'kind': 'research', 'record': 'work'},
            overview_assessment={'verdict': 'supported', 'reason': 'Fixture'},
            results=[dict(result='r1', **verdicts())], summary='Fixture')
        new = copy.deepcopy(self.review)
        new['results'][0]['assessment']['verdict'] = 'not_supported'
        index = render_index([('work', self.work), ('peer', self.peer), ('old', old), ('new', new)])
        self.assertIn('(peer/output.json)', index)
        self.assertIn('(new/output.json)', index)
        self.assertIn('상충: r1/assessment', index)
        self.assertNotIn('## peer', index)
        self.assertNotIn('## review', index)
        self.assertNotIn('  assessment:', index)


if __name__ == '__main__':
    unittest.main()
