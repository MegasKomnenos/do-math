"""Publication index and overview contract, with real files and Git."""

import copy
import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_runner import RunnerTests
from test_check import HandoffTests, envelope, judgment, write_json
import runner
from check import check_session


class OverviewTests(HandoffTests):
    def test_all_sessions_require_overview(self):
        session, output = self.research()
        del output['overview']
        write_json(session / 'output/output.json', output)
        self.assertTrue(any('overview' in e for e in check_session(session)))
        output['overview'] = {'title': 'A bounded result', 'summary': 'Only the stated case was proved; P remains open.'}
        write_json(session / 'output/output.json', output)
        self.assertEqual(check_session(session), [])
        output['overview']['summary'] = ' '
        write_json(session / 'output/output.json', output)
        self.assertTrue(any('overview.summary' in e for e in check_session(session)))

    def test_review_must_judge_overview_and_cannot_skip_existing_one(self):
        author, output = self.research()
        output['overview'] = {'title': 'Claim', 'summary': 'A partial claim.'}
        write_json(author / 'output/output.json', output)
        self.publish(author, 'k1')
        target = {'kind': 'research', 'record': 'k1'}
        review = envelope('review', overview={'title': 'Review', 'summary': 'A partial result was checked.'},
            target=target, results=[{'result': 'r1', 'assessment': judgment('supported'),
                'lean': judgment('not_checked'), 'alignment': judgment('not_checked'),
                'terminology': judgment('conforms')}], summary='Detailed review.')
        session = self.session('new-review', review, target=target)
        del review['overview_assessment']
        write_json(session / 'output/output.json', review)
        self.assertTrue(any('overview_assessment' in e for e in check_session(session)))
        review['overview_assessment'] = judgment('not_applicable')
        write_json(session / 'output/output.json', review)
        self.assertTrue(check_session(session))
        review['overview_assessment'] = judgment('not_supported')
        write_json(session / 'output/output.json', review)
        self.assertEqual(check_session(session), [])


class IndexTests(RunnerTests):
    def publish_record(self, name, output):
        path = self.instance / 'knowledge' / name / 'output.json'
        path.parent.mkdir(parents=True)
        runner.write_json(path, output)
        runner.git(self.instance, 'add', '--', 'knowledge/' + name)
        runner.git(self.instance, 'commit', '-m', 'Publish ' + name)

    def index(self):
        return (self.instance / 'knowledge/index.md').read_text(encoding='utf-8')

    def test_publication_produces_index_and_new_prompt(self):
        self.until(lambda: self.engine.state['complete'] and not self.engine.active())
        self.assertTrue((self.instance / 'knowledge/index.md').exists())
        content = self.index()
        for sid, session in self.engine.state['sessions'].items():
            self.assertIn(f'({session["record"]}/output.json)', content)
            data = runner.read_json(self.instance / 'sessions' / sid / 'input.json')
            self.assertNotIn('output_contract', data)
            self.assertIn('knowledge', (self.instance / 'sessions' / sid / 'prompt.txt').read_text(encoding='utf-8'))
            self.assertIn('index.md', (self.instance / 'sessions' / sid / 'prompt.txt').read_text(encoding='utf-8'))
        self.assertIn('overview', runner.read_json(self.instance / 'knowledge' / session['record'] / 'output.json'))

    def test_review_supersession_conflict_and_rebuild(self):
        research = envelope('research', overview={'title': 'A [partial] result', 'summary': 'Proved one case. General P is open.'},
                            results=[{'id': 'r1'}], failed_attempts=[], open_questions=['P?'])
        self.publish_record('k1', research)
        self.engine.refresh_index()
        self.assertIn('검토 전', self.index())
        review = envelope('review', overview={'title': 'First review', 'summary': 'Checked only the submitted scope.'},
            target={'kind': 'research', 'record': 'k1'}, results=[{'result': 'r1', 'assessment': judgment('supported'),
            'lean': judgment('not_applicable'), 'alignment': judgment('not_applicable'),
            'terminology': judgment('conforms')}],
            overview_assessment=judgment('supported'), summary='Detailed judgment')
        self.publish_record('k2', review)
        self.engine.refresh_index()
        self.assertIn('요약 판정: supported', self.index())
        negative = copy.deepcopy(review)
        negative['results'][0]['assessment'] = judgment('not_supported')
        self.publish_record('k3', negative)
        self.engine.refresh_index()
        self.assertIn('상충: r1/assessment', self.index())
        replacement = copy.deepcopy(review)
        replacement['supersedes'] = ['k3']
        self.publish_record('k4', replacement)
        self.engine.refresh_index()
        first_section = self.index().split('## ', 2)[1]
        self.assertNotIn('상충:', first_section)
        research['supersedes'] = ['k1']
        self.publish_record('k5', research)
        self.engine.refresh_index()
        self.assertIn('대체됨', self.index())
        self.assertIn('검토 전', self.index().split('## ')[-1])
        before = self.index()
        commits = runner.git(self.instance, 'rev-list', '--count', 'HEAD')
        self.engine.refresh_index()
        self.assertEqual(self.index(), before)
        self.assertEqual(runner.git(self.instance, 'rev-list', '--count', 'HEAD'), commits)
        (self.instance / 'knowledge/index.md').unlink()
        runner.Runner(self.instance, self.skill).refresh_index()
        self.assertEqual(self.index(), before)

    def test_index_uses_author_overview_without_changing_original(self):
        output = envelope('research', overview={'title': 'Historical result', 'summary': 'A limited result; P remains open.'},
                          results=[{'id': 'old', 'exposition': 'exposition.md'}], failed_attempts=[], open_questions=[])
        self.publish_record('old1', output)
        folder = self.instance / 'knowledge/old1'
        (folder / 'exposition.md').write_text('# Historical result\n\nA limited result; P remains open.\n', encoding='utf-8')
        before = (folder / 'output.json').read_bytes()
        self.engine.refresh_index()
        self.assertIn('Historical result', self.index())
        self.assertIn('P remains open', self.index())
        self.assertEqual((folder / 'output.json').read_bytes(), before)

    def test_index_links_research_status_of_latest_plan_only(self):
        self.publish_record('p1', envelope('plan'))
        (self.instance / 'knowledge/p1/research-status.md').write_text('# old\n', encoding='utf-8')
        self.publish_record('p2', envelope('plan'))
        (self.instance / 'knowledge/p2/research-status.md').write_text('# new\n', encoding='utf-8')
        self.engine.refresh_index()
        header = self.index().split('\n## ', 1)[0]
        self.assertIn('(p2/research-status.md)', header)
        self.assertNotIn('p1/research-status.md', self.index())
        # A latest plan without the file must not point readers to an older, stale status.
        self.publish_record('p3', envelope('plan'))
        self.engine.refresh_index()
        self.assertNotIn('research-status.md)', self.index())

    def test_index_links_glossary_of_latest_plan_only(self):
        self.publish_record('p1', envelope('plan'))
        (self.instance / 'knowledge/p1/glossary.md').write_text('# old\n', encoding='utf-8')
        self.publish_record('p2', envelope('plan'))
        (self.instance / 'knowledge/p2/glossary.md').write_text('# new\n', encoding='utf-8')
        self.engine.refresh_index()
        header = self.index().split('\n## ', 1)[0]
        self.assertIn('(p2/glossary.md)', header)
        self.assertNotIn('p1/glossary.md', self.index())
        self.publish_record('p3', envelope('plan'))
        self.engine.refresh_index()
        self.assertNotIn('glossary.md)', self.index())

    def test_index_marks_exploration_as_unreviewed_by_design(self):
        self.publish_record('e1', envelope('explore', exposition='notes.md', questions=[]))
        self.engine.refresh_index()
        section = self.index().split('\n## ', 1)[1]
        self.assertIn('탐구 · [e1](e1/output.json)', section)
        self.assertIn('독립 검토를 받지 않는', section)
        self.assertNotIn('검토 전', section)

    def test_index_shows_overview_verdict_without_reason(self):
        self.publish_record('k1', envelope('research', results=[{'id': 'r1'}], failed_attempts=[], open_questions=[]))
        review = envelope('review', target={'kind': 'research', 'record': 'k1'},
            results=[{'result': 'r1', 'assessment': judgment('supported'),
                      'lean': judgment('not_applicable'), 'alignment': judgment('not_applicable'),
                      'terminology': judgment('deviates')}],
            overview_assessment={'verdict': 'supported', 'reason': 'UNIQUE-REASON-TEXT'}, summary='Detailed')
        self.publish_record('k2', review)
        self.engine.refresh_index()
        self.assertIn('요약 판정: supported', self.index())
        self.assertNotIn('terminology:', self.index())
        self.assertNotIn('\n검토 · ', self.index())
        self.assertIn('(k2/output.json)', self.index())
        self.assertNotIn('UNIQUE-REASON-TEXT', self.index())
        self.assertIn('overview_assessment', self.index().split('\n## ', 1)[0])

    def test_index_escapes_only_text_hiding_markdown(self):
        summary = 'b(n,1)<b(n,2) when 0<L and n>3; f_(L,m)+1*2 & [x](y) `c` \\q'
        self.publish_record('k1', envelope('research', overview={'title': 'T', 'summary': summary},
                                           results=[], failed_attempts=[], open_questions=[]))
        self.engine.refresh_index()
        text = self.index()
        self.assertIn('b(n,1)\\<b(n,2) when 0\\<L and n>3; f_(L,m)+1*2 & \\[x\\](y) \\`c\\` \\\\q', text)
        self.assertNotIn('&lt;', text)

    def test_index_command_rebuilds_missing_file(self):
        (self.instance / 'knowledge/index.md').unlink()
        result = subprocess.run([sys.executable, str(runner.SCRIPT), 'index', str(self.instance)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.instance / 'knowledge/index.md').exists())

    def test_index_rebuilds_corrupted_derived_file(self):
        path = self.instance / 'knowledge/index.md'
        expected = path.read_bytes()
        path.write_bytes(b'\xffbroken')
        self.engine.refresh_index()
        self.assertEqual(path.read_bytes(), expected)

    def test_restart_recovers_publication_before_index_only_commit(self):
        record = 'kpending'
        data = envelope('research', results=[], failed_attempts=[], open_questions=[])
        folder = self.instance / 'knowledge' / record
        folder.mkdir()
        runner.write_json(folder / 'output.json', data)
        self.engine.state['sessions']['spending'] = {
            'category': 'research', 'status': 'publishing', 'record': record, 'request': None}
        self.engine.save()
        engine = runner.Runner(self.instance, self.skill)
        with patch.object(engine, 'tick', side_effect=RuntimeError('end startup test')):
            with self.assertRaisesRegex(RuntimeError, 'end startup test'):
                engine.run()
        for commit in runner.git(self.instance, 'rev-list', 'HEAD').splitlines():
            content = runner.git(self.instance, 'show', commit + ':knowledge/index.md')
            if '(kpending/output.json)' in content:
                self.assertTrue(runner.git(self.instance, 'ls-tree', '--name-only', commit,
                                           '--', 'knowledge/kpending/output.json'))


def load_tests(loader, tests, pattern):
    # Reuse fixture setup without rerunning imported/inherited regression suites.
    return unittest.TestSuite(loader.loadTestsFromName(name, cls)
        for cls in (OverviewTests, IndexTests)
        for name in cls.__dict__ if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main()
