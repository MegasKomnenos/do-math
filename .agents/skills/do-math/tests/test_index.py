"""Publication index and overview contract, with real files and Git."""

import copy
import json
from pathlib import Path
import shutil
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

    def module(self, name):
        return (self.instance / 'knowledge/index' / (name + '.md')).read_text(encoding='utf-8')

    def test_publication_produces_index_and_new_prompt(self):
        self.until(lambda: self.engine.state['complete'] and not self.engine.active())
        self.assertTrue((self.instance / 'knowledge/index.md').exists())
        # The last plan filed the reviewed work into a module; everything else is in the general module.
        content = self.index() + self.module('reviewed').replace('(../', '(')
        plans = [s['record'] for s in self.engine.state['sessions'].values() if s['category'] == 'plan']
        for sid, session in self.engine.state['sessions'].items():
            if session['category'] == 'plan':
                self.assertEqual(f'({session["record"]}/output.json)' in content, session['record'] == plans[-1])
            else:
                self.assertIn(f'({session["record"]}/output.json)', content)
            data = runner.read_json(self.instance / 'sessions' / sid / 'input.json')
            self.assertNotIn('output_contract', data)
            prompt = (self.instance / 'sessions' / sid / 'prompt.txt').read_text(encoding='utf-8')
            self.assertIn('knowledge', prompt)
            self.assertIn('index.md', prompt)
            self.assertIn('general module', prompt)
        self.assertIn('overview', runner.read_json(self.instance / 'knowledge' / session['record'] / 'output.json'))
        self.assertIn(f'Latest plan: [{plans[-1]}]({plans[-1]}/output.json)', self.index())
        self.assertIn('| [Reviewed work](index/reviewed.md) | Work whose bundle review is in. | 1 | 0 | 0 |', self.index())
        self.assertIn('(../index.md)', self.module('reviewed'))
        # The module file is part of the publication commit, not a loose file.
        self.assertEqual(runner.git(self.instance, 'status', '--porcelain', '--', 'knowledge'), '')
        self.assertIn('knowledge/index/reviewed.md', runner.git(self.instance, 'ls-files', '--', 'knowledge/index'))

    def test_review_supersession_conflict_and_rebuild(self):
        research = envelope('research', overview={'title': 'A [partial] result', 'summary': 'Proved one case. General P is open.'},
                            results=[{'id': 'r1'}], failed_attempts=[], open_questions=['P?'])
        self.publish_record('k1', research)
        self.engine.refresh_index()
        self.assertIn('Unreviewed', self.index())
        review = envelope('review', overview={'title': 'First review', 'summary': 'Checked only the submitted scope.'},
            target={'kind': 'research', 'record': 'k1'}, results=[{'result': 'r1', 'assessment': judgment('supported'),
            'lean': judgment('not_applicable'), 'alignment': judgment('not_applicable'),
            'terminology': judgment('conforms')}],
            overview_assessment=judgment('supported'), summary='Detailed judgment')
        self.publish_record('k2', review)
        self.engine.refresh_index()
        self.assertIn('overview assessment: supported', self.index())
        negative = copy.deepcopy(review)
        negative['results'][0]['assessment'] = judgment('not_supported')
        self.publish_record('k3', negative)
        self.engine.refresh_index()
        self.assertIn('Conflict: r1/assessment', self.index())
        replacement = copy.deepcopy(review)
        replacement['supersedes'] = ['k3']
        self.publish_record('k4', replacement)
        self.engine.refresh_index()
        first_section = self.index().split('## ', 2)[1]
        self.assertNotIn('Conflict:', first_section)
        research['supersedes'] = ['k1']
        self.publish_record('k5', research)
        self.engine.refresh_index()
        self.assertIn('Superseded by', self.index())
        self.assertIn('Unreviewed', self.index().split('## ')[-1])
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

    def test_plan_records_have_no_entries(self):
        self.publish_record('p1', envelope('plan', overview={'title': 'FIRST-PLAN-TITLE', 'summary': 'Planned.'}))
        self.publish_record('p2', envelope('plan', overview={'title': 'SECOND-PLAN-TITLE', 'summary': 'Planned again.'}))
        self.publish_record('k1', envelope('research', results=[], failed_attempts=[], open_questions=[]))
        self.engine.refresh_index()
        content = self.index()
        self.assertNotIn('FIRST-PLAN-TITLE', content)
        self.assertNotIn('SECOND-PLAN-TITLE', content)
        self.assertNotIn('(p1/output.json)', content)
        self.assertIn('Latest plan: [p2](p2/output.json)', content)
        self.assertIn('3 published records · 1 index entry (plan, peer and review records not listed separately)', content)
        self.assertEqual(content.count('\n## '), 1)

    def plan_with_modules(self, modules):
        return envelope('plan', index={'modules': modules})

    def test_modules_render_general_complement_counts_and_links(self):
        for rid in ('k1', 'k2', 'k3'):
            self.publish_record(rid, envelope('research', overview={'title': 'Title ' + rid, 'summary': 'Summary ' + rid},
                                              results=[{'id': 'r1'}], failed_attempts=[], open_questions=[]))
        self.publish_record('e1', envelope('explore', exposition='notes.md', questions=[]))
        negative = envelope('review', target={'kind': 'research', 'record': 'k2'}, overview_assessment=judgment('supported'),
            results=[{'result': 'r1', 'assessment': judgment('not_supported'), 'lean': judgment('not_applicable'),
                      'alignment': judgment('not_applicable'), 'terminology': judgment('conforms')}], summary='Detailed')
        positive = copy.deepcopy(negative)
        positive['results'][0]['assessment'] = judgment('supported')
        self.publish_record('v1', negative)
        self.publish_record('v2', positive)
        self.publish_record('p1', self.plan_with_modules([
            {'name': 'general', 'title': 'Base context', 'description': 'CUSTOM-GENERAL-DESCRIPTION', 'records': ['k3']},
            {'name': 'closed-route', 'title': 'Closed route', 'description': 'Closed by |k3|; open if revisited.',
             'records': ['k2', 'k1']}]))
        self.engine.refresh_index()
        main = self.index()
        self.assertIn('**Base context**: CUSTOM-GENERAL-DESCRIPTION', main)
        # A separator inside a description must not split the table row.
        self.assertIn('| [Closed route](index/closed-route.md) | Closed by \\|k3\\|; open if revisited. | 2 | 1 | 1 |', main)
        self.assertIn('7 published records · 4 index entries', main)
        self.assertIn('2 in the general module · 2 filed in 1 other module', main)
        general = main.split('**Modules filed by the last plan**', 1)[1]
        self.assertIn('## Title k3', general)
        self.assertIn('(e1/output.json)', general)
        self.assertNotIn('## Title k1', general)
        self.assertNotIn('## Title k2', general)
        module = self.module('closed-route')
        self.assertTrue(module.startswith('# Closed route\n\nClosed by |k3|; open if revisited.\n'))
        self.assertIn('2 records · 1 unreviewed · 1 with conflicting reviews', module)
        # Publication order inside the module, whatever order the plan listed.
        self.assertLess(module.index('## Title k1'), module.index('## Title k2'))
        self.assertIn('(../k1/output.json)', module)
        self.assertIn('[current review v1](../v1/output.json)', module)
        self.assertIn('Conflict: r1/assessment', module)
        self.assertNotIn('(k1/output.json)', module.replace('(../k1/output.json)', ''))
        self.assertIn('knowledge/index/closed-route.md', runner.git(self.instance, 'ls-files', '--', 'knowledge/index'))

    def test_later_layout_replaces_stale_module_files(self):
        self.publish_record('k1', envelope('research', results=[], failed_attempts=[], open_questions=[]))
        self.publish_record('p1', self.plan_with_modules([
            {'name': 'old', 'title': 'Old', 'description': 'To be retired.', 'records': ['k1']}]))
        self.engine.refresh_index()
        self.assertTrue((self.instance / 'knowledge/index/old.md').is_file())
        commits = runner.git(self.instance, 'rev-list', '--count', 'HEAD')
        self.engine.refresh_index()
        self.assertEqual(runner.git(self.instance, 'rev-list', '--count', 'HEAD'), commits)
        self.publish_record('p2', self.plan_with_modules([
            {'name': 'new', 'title': 'New', 'description': 'Replaces old.', 'records': ['k1']}]))
        self.engine.refresh_index()
        self.assertFalse((self.instance / 'knowledge/index/old.md').exists())
        self.assertTrue((self.instance / 'knowledge/index/new.md').is_file())
        self.assertEqual(runner.git(self.instance, 'ls-files', '--', 'knowledge/index'), 'knowledge/index/new.md')
        self.assertEqual(runner.git(self.instance, 'status', '--porcelain', '--', 'knowledge'), '')
        # A plan without a layout (or an old plan) leaves only the general module.
        self.publish_record('p3', envelope('plan'))
        self.engine.refresh_index()
        self.assertFalse((self.instance / 'knowledge/index').exists())
        self.assertEqual(runner.git(self.instance, 'ls-files', '--', 'knowledge/index'), '')
        self.assertNotIn('Modules filed', self.index())
        self.assertNotIn('**', self.index().split('published record', 1)[1])  # no declared general: no heading line
        self.assertIn('(k1/output.json)', self.index())
        # An uncommitted leftover module file is removed without a Git error.
        (self.instance / 'knowledge/index').mkdir()
        (self.instance / 'knowledge/index/leftover.md').write_text('stale', encoding='utf-8')
        self.engine.refresh_index()
        self.assertFalse((self.instance / 'knowledge/index').exists())

    def test_publication_commit_carries_index_changes(self):
        self.publish_record('k1', envelope('research', results=[], failed_attempts=[], open_questions=[]))
        self.publish_record('p1', self.plan_with_modules([
            {'name': 'old', 'title': 'Old', 'description': 'To be retired.', 'records': ['k1']}]))
        self.engine.refresh_index()
        # A newly copied plan that retires the module, not yet committed, as finish() sees it.
        folder = self.instance / 'knowledge/p2'
        folder.mkdir()
        runner.write_json(folder / 'output.json', self.plan_with_modules([
            {'name': 'new', 'title': 'New', 'description': 'Replaces old.', 'records': ['k1']}]))
        commits = int(runner.git(self.instance, 'rev-list', '--count', 'HEAD'))
        self.engine.refresh_index(publish='p2')
        self.assertEqual(int(runner.git(self.instance, 'rev-list', '--count', 'HEAD')), commits + 1)
        self.assertEqual(runner.git(self.instance, 'log', '-1', '--format=%s'), 'Publish p2')
        changed = runner.git(self.instance, 'show', '--name-status', '--no-renames', '--format=', 'HEAD').splitlines()
        self.assertIn('A\tknowledge/p2/output.json', changed)
        self.assertIn('A\tknowledge/index/new.md', changed)
        self.assertIn('D\tknowledge/index/old.md', changed)
        self.assertIn('M\tknowledge/index.md', changed)
        self.assertEqual(runner.git(self.instance, 'status', '--porcelain', '--', 'knowledge'), '')

    def test_index_command_and_restart_rebuild_modules(self):
        self.publish_record('k1', envelope('research', results=[], failed_attempts=[], open_questions=[]))
        self.publish_record('p1', self.plan_with_modules([
            {'name': 'lean', 'title': 'Lean layer', 'description': 'Formal results.', 'records': ['k1']}]))
        self.engine.refresh_index()
        expected = (self.instance / 'knowledge/index/lean.md').read_bytes()
        shutil.rmtree(self.instance / 'knowledge/index')
        (self.instance / 'knowledge/index.md').unlink()
        result = subprocess.run([sys.executable, str(runner.SCRIPT), 'index', str(self.instance)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.instance / 'knowledge/index/lean.md').read_bytes(), expected)
        shutil.rmtree(self.instance / 'knowledge/index')
        engine = runner.Runner(self.instance, self.skill)
        with patch.object(engine, 'tick', side_effect=RuntimeError('end startup test')):
            with self.assertRaisesRegex(RuntimeError, 'end startup test'):
                engine.run()
        self.assertEqual((self.instance / 'knowledge/index/lean.md').read_bytes(), expected)

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

    def test_index_marks_exploration_claim_scope(self):
        self.publish_record('e1', envelope('explore', exposition='notes.md', questions=[]))
        self.engine.refresh_index()
        section = self.index().split('\n## ', 1)[1]
        self.assertIn('exploration · [e1](e1/output.json)', section)
        self.assertIn('distinguish observations and conjectures from reviewed propositions', section)
        self.assertIn('Unreviewed', section)

    def test_index_shows_overview_verdict_without_reason(self):
        self.publish_record('k1', envelope('research', results=[{'id': 'r1'}], failed_attempts=[], open_questions=[]))
        review = envelope('review', target={'kind': 'research', 'record': 'k1'},
            results=[{'result': 'r1', 'assessment': judgment('supported'),
                      'lean': judgment('not_applicable'), 'alignment': judgment('not_applicable'),
                      'terminology': judgment('deviates')}],
            overview_assessment={'verdict': 'supported', 'reason': 'UNIQUE-REASON-TEXT'}, summary='Detailed')
        self.publish_record('k2', review)
        self.engine.refresh_index()
        self.assertIn('overview assessment: supported', self.index())
        self.assertNotIn('terminology:', self.index())
        self.assertNotIn('\nreview · ', self.index())
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
