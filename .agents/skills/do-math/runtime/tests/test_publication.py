import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as runtime
from check import Invalid, audit_formal
from knowledge import replay
from runtime_support import read_json, write_json
from test_research import InstanceCase, assessment, claim_row, record, solution


class PublicationTests(InstanceCase):
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
        jid = runner.enqueue('review', {'kind': 'candidate', 'candidate': str(candidate)}, pid, pid + ':review')
        runner.state['jobs'][jid].update(status='running', session='sreview')
        runner.state['jobs'][producer]['status'] = 'done'
        runner.state['sessions']['sreview'] = {'id': 'sreview', 'role': 'review', 'status': 'running', 'job': jid}
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


if __name__ == '__main__':
    unittest.main()
