import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as runtime
from check import Invalid, audit_formal, check_session
from knowledge import replay
from runtime_support import read_json, write_json
from test_research import InstanceCase, assessment, claim_row, record, solution


class PublicationTests(InstanceCase):
    def test_candidate_cannot_collide_with_publication_attachments(self):
        session = self.instance / 'sessions/speer'
        output = session / 'output'
        output.mkdir(parents=True)
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': 'speer',
                                           'role': 'peer', 'task': {}})
        write_json(output / 'record.json', record())
        (output / 'record.md').write_text('Retained mathematics.', encoding='utf-8')
        self.assertEqual(check_session(session), [])
        for name, directory in (('review', True), ('Review', True),
                                ('provenance.json', False), ('PROVENANCE.JSON', False)):
            with self.subTest(name=name):
                path = output / name
                if directory:
                    path.mkdir()
                else:
                    path.write_text('Historical evidence.', encoding='utf-8')
                try:
                    errors = check_session(session)
                    self.assertTrue(errors)
                    self.assertIn('reserved for publication attachments', errors[0])
                finally:
                    path.rmdir() if directory else path.unlink()
        evidence = output / 'evidence'
        evidence.mkdir()
        (evidence / 'review').mkdir()
        (evidence / 'provenance.json').write_text('Historical evidence.', encoding='utf-8')
        self.assertEqual(check_session(session), [])

    def candidate_pipeline(self):
        runner = runtime.Runner(self.instance, self.skill)
        producer = runner.producer('attempt')
        pid = runner.state['jobs'][producer]['pipeline']
        pipeline = runner.state['pipelines'][pid]
        pipeline.update(producer='sauthor', peer='speer', review='sreview', stage='review')
        candidate = self.instance / 'sessions/speer/candidate'
        candidate.mkdir(parents=True)
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        write_json(candidate / 'record.json', data)
        (candidate / 'record.md').write_text('The proof.', encoding='utf-8')
        session = self.instance / 'sessions/sreview'
        (session / 'output').mkdir(parents=True)
        write_json(session / 'output/assessment.json', assessment(data))
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        task = {'kind': 'candidate', 'candidate': str(candidate), 'candidate_hashes': runtime.tree_hashes(candidate)}
        jid = runner.enqueue('review', task, pid, pid + ':review')
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': 'sreview',
                                           'role': 'review', 'task': task})
        (session / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (session / 'cli.stderr.log').write_text('', encoding='utf-8')
        runner.state['jobs'][jid].update(status='running', session='sreview')
        runner.state['jobs'][producer]['status'] = 'done'
        runner.state['sessions']['sreview'] = {'id': 'sreview', 'role': 'review', 'status': 'running', 'job': jid,
                                              'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': 1}
        runner.save()
        return runner, runner.state['jobs'][jid]

    def test_commit_failure_recovers_same_publication_without_duplicates(self):
        runner, job = self.candidate_pipeline()
        runner.prepare_publication('sreview', job, 'record')
        identity = runner.state['publication']['event']['id']
        original = runtime.git
        def broken(instance, *args):
            if args[0] == 'commit':
                raise RuntimeError('simulated unavailable commit')
            return original(instance, *args)
        with patch('runner.git', side_effect=broken):
            with self.assertRaisesRegex(RuntimeError, 'simulated'):
                runner.publish()
        recovered = runtime.Runner(self.instance, self.skill)
        recovered.publish()
        recovered.publish()
        self.assertEqual(list(replay(self.instance)['records']), [identity])
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(recovered.state['jobs'][job['id']]['status'], 'done')
        self.assertEqual(len(list((self.instance / 'knowledge/events').glob('*.json'))), 1)
        history = original(self.instance, 'log', '--format=%s')
        self.assertEqual(history.count('Publish ' + identity), 1)

    def test_review_finish_publishes_the_unchanged_assigned_candidate(self):
        runner, job = self.candidate_pipeline()
        runner.finish('sreview', runner.state['sessions']['sreview'])
        events = list((self.instance / 'knowledge/events').glob('*.json'))
        self.assertEqual(len(events), 1)
        event = read_json(events[0])
        self.assertEqual(event['kind'], 'record')
        self.assertEqual(job['status'], 'done')
        self.assertEqual(runner.state['sessions']['sreview']['status'], 'integrated')
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'done')
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual((published / 'record.md').read_bytes(), b'The proof.')

    def test_review_finish_retries_instead_of_publishing_a_changed_candidate(self):
        runner, job = self.candidate_pipeline()
        candidate = Path(job['task']['candidate'])
        (candidate / 'record.md').write_text('A different argument after assignment.', encoding='utf-8')
        runner.finish('sreview', runner.state['sessions']['sreview'])
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(job['retries'], 1)
        self.assertEqual(job['last_error'], 'candidate changed after review assignment')
        self.assertEqual(runner.state['sessions']['sreview']['status'], 'failed')
        self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'review')
        self.assertIsNone(runner.state['publication'])
        self.assertEqual(list((self.instance / 'knowledge/events').glob('*.json')), [])
        self.assertEqual(list((self.instance / 'knowledge/records').iterdir()), [])


    def test_completed_exclusion_releases_occupancy_without_publishing(self):
        runner, job = self.candidate_pipeline()
        pipeline = runner.state['pipelines'][job['pipeline']]
        producer = runner.session_dir(pipeline['producer'])
        producer.mkdir(parents=True)
        write_json(producer / 'declaration.json', {'nodes': ['root'], 'at': 1})
        self.assertEqual(runner.available_nodes(), ([], 0))
        session = runner.session_dir('sreview')
        verdict = read_json(session / 'output/assessment.json')
        verdict.update(publish=False, reason='No useful supported material.',
                       index_assessment='The offered argument is unsupported.')
        verdict['claims'][0].update(status='unsupported', reason='The argument does not establish the claim.')
        verdict['solutions'][0].update(level='none', reason='No solution established.')
        write_json(session / 'output/assessment.json', verdict)
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': 'sreview',
                                           'role': 'review', 'task': job['task']})
        (session / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (session / 'cli.stderr.log').write_text('', encoding='utf-8')
        reviewer = runner.state['sessions']['sreview']
        reviewer.update(provider='codex', model='codex/gpt-6.1-sol', started_at=1)
        runner.finish('sreview', reviewer)
        self.assertEqual((reviewer['status'], job['status'], pipeline['stage']),
                         ('integrated', 'done', 'done'))
        self.assertTrue(reviewer['rejected'])
        self.assertEqual(pipeline['rejection_session'], 'sreview')
        self.assertIsNone(runner.state['publication'])
        self.assertEqual(list((self.instance / 'knowledge/events').glob('*.json')), [])
        self.assertEqual(list((self.instance / 'knowledge/records').iterdir()), [])
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'unresolved')
        self.assertEqual(runner.available_nodes(), (['root'], 0))
        recovered = runtime.Runner(self.instance, self.skill)
        self.assertEqual(recovered.available_nodes(), (['root'], 0))
        self.assertEqual(recovered.state['jobs'][job['id']]['status'], 'done')


class FormalEvidenceTests(InstanceCase):
    def evidence(self, owner='sreview', axiom_line="'target' does not depend on any axioms"):
        candidate = self.root / 'candidate'; candidate.mkdir()
        source = b'theorem target : True := by trivial\n'
        (candidate / 'Proof.lean').write_bytes(source)
        session = self.instance / 'sessions/sreview'
        (session / 'work').mkdir(parents=True)
        write_json(session / 'input.json', {'settings': read_json(self.instance / 'settings.json')})
        working = session / 'work/Proof.lean'
        working.write_bytes(source + b'\n#print axioms target\n')
        job = 'j' + 'a' * 32
        directory = self.instance / 'runner/lean/jobs' / job
        directory.mkdir(parents=True)
        write_json(directory / 'result.json', {'id': job, 'session': owner, 'status': 'finished', 'exit_code': 0,
                                              'source': str(working), 'source_sha256': hashlib.sha256(working.read_bytes()).hexdigest()})
        (directory / 'stdout.log').write_text(axiom_line, encoding='utf-8')
        check = {'job': job, 'theorem': 'target', 'axioms': [], 'alignment': 'matches', 'reason': 'Exact statement.',
                 'source_hashes': {'Proof.lean': hashlib.sha256(source).hexdigest()}, 'source_files': {'Proof.lean': 'work/Proof.lean'}}
        solution = {'lean': {'theorem': 'target', 'sources': ['Proof.lean']}}
        return candidate, working, check, solution

    def test_authors_job_is_not_independent_review(self):
        candidate, _, check, solution = self.evidence(owner='sauthor')
        with self.assertRaisesRegex(Invalid, 'reviewing session'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_modified_working_copy_cannot_reuse_old_compile(self):
        candidate, working, check, solution = self.evidence()
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        working.write_bytes(working.read_bytes() + b'\n#print axioms target\n')
        with self.assertRaisesRegex(Invalid, 'submitted compile'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_placeholder_axiom_is_rejected_despite_exit_zero(self):
        candidate, _, check, solution = self.evidence(axiom_line="'target' depends on axioms: [sorryAx]")
        check['axioms'] = ['sorryAx']
        with self.assertRaisesRegex(Invalid, 'unapproved axiom'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_formal_axiom_policy_is_the_reviewers_launch_snapshot(self):
        candidate, _, check, solution = self.evidence(axiom_line="'target' depends on axioms: [custom_assumption]")
        check['axioms'] = ['custom_assumption']
        inp = read_json(self.instance / 'sessions/sreview/input.json')
        inp['settings']['lean']['allowed_axioms'].append('custom_assumption')
        write_json(self.instance / 'sessions/sreview/input.json', inp)
        # The current instance does not allow this axiom, but this reviewer was
        # launched under a condition that did. Later conditions do not alter it.
        self.assertNotIn('custom_assumption', read_json(self.instance / 'settings.json')['lean']['allowed_axioms'])
        audit_formal(self.instance, 'sreview', check, solution, candidate)

    def build_evidence(self):
        candidate, working, check, solution = self.evidence()
        target = b'import Basis\n' + (candidate / 'Proof.lean').read_bytes()
        (candidate / 'Proof.lean').write_bytes(target)
        working.write_bytes(target + b'\n#print axioms target\n')
        check['source_hashes']['Proof.lean'] = hashlib.sha256(target).hexdigest()
        target_job = check['job']
        job_path = self.instance / 'runner/lean/jobs' / target_job / 'result.json'
        compiled = read_json(job_path)
        compiled['source_sha256'] = hashlib.sha256(working.read_bytes()).hexdigest()
        write_json(job_path, compiled)
        dependency = b'theorem basis : True := by trivial\n'
        (candidate / 'Basis.lean').write_bytes(dependency)
        copied = working.with_name('Basis.lean')
        copied.write_bytes(dependency)
        build_id = 'b' + 'a' * 32
        receipt = {
            'id': build_id, 'session': 'sreview', 'status': 'finished',
            'targets': ['Proof'], 'modules': {
                'Basis': {'source': str(copied),
                          'source_sha256': hashlib.sha256(dependency).hexdigest(),
                          'status': 'cached', 'exit_code': 0, 'job': None},
                'Proof': {'source': str(working),
                          'source_sha256': hashlib.sha256(working.read_bytes()).hexdigest(),
                          'status': 'finished', 'exit_code': 0, 'job': target_job},
            },
        }
        directory = self.instance / 'runner/lean/builds' / build_id
        directory.mkdir(parents=True)
        write_json(directory / 'result.json', receipt)
        check['job'] = build_id
        check['source_hashes']['Basis.lean'] = hashlib.sha256(dependency).hexdigest()
        check['source_files']['Basis.lean'] = 'work/Basis.lean'
        solution['lean']['sources'].insert(0, 'Basis.lean')
        return candidate, copied, check, solution, receipt, directory

    def test_formal_build_allows_cached_dependencies_but_requires_a_fresh_successful_target(self):
        candidate, _, check, solution, receipt, directory = self.build_evidence()
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        target = receipt['modules']['Proof'].copy()
        for changes in ({'status': 'cached', 'job': None},
                        {'exit_code': 1}, {'job': None}):
            with self.subTest(changes=changes):
                receipt['modules']['Proof'] = {**target, **changes}
                write_json(directory / 'result.json', receipt)
                with self.assertRaisesRegex(Invalid, 'freshly compile targets'):
                    audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_formal_build_rejects_changed_bytes_of_a_cached_dependency(self):
        candidate, copied, check, solution, _, _ = self.build_evidence()
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        changed = copied.read_bytes() + b'-- changed after the build\n'
        copied.write_bytes(changed)
        (candidate / 'Basis.lean').write_bytes(changed)
        check['source_hashes']['Basis.lean'] = hashlib.sha256(changed).hexdigest()
        with self.assertRaisesRegex(Invalid, 'submitted compile'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)


if __name__ == '__main__':
    unittest.main()
