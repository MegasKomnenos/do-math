import hashlib
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as runtime
from check import Invalid, audit_formal, check_session
from knowledge import replay
from runtime_support import read_json, write_json
from test_research import InstanceCase, assessment, claim_row, implication, record, solution


class ProposalIdentityTests(InstanceCase):
    def peer_candidate(self, sid, node_id, statement):
        folder = self.instance / 'sessions' / sid
        output = folder / 'output'
        output.mkdir(parents=True)
        data = record([claim_row('connection')],
                      nodes=[{'id': node_id, 'statement': statement, 'connection': 'connection'}],
                      relations=[implication('connection', node_id)])
        write_json(output / 'record.json', data)
        (output / 'record.md').write_text('The conditional argument and its definitions.', encoding='utf-8')
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid,
                                           'role': 'peer', 'task': {}})
        return folder, data

    def test_peer_rejects_unscoped_new_node_ids_before_candidate_freeze(self):
        sid = 's' + '1' * 32
        folder, data = self.peer_candidate(sid, 'q', 'First question.')
        errors = check_session(folder)
        self.assertTrue(any('peer session prefix' in error for error in errors), errors)
        data['nodes'][0]['id'] = sid + '-q'
        data['relations'][0]['premises'][0]['node'] = sid + '-q'
        write_json(folder / 'output/record.json', data)
        self.assertEqual(check_session(folder), [])

    def test_same_local_node_label_from_two_peers_cannot_collide_during_review(self):
        first_sid, second_sid = 's' + '1' * 32, 's' + '2' * 32
        first_id, second_id = first_sid + '-q', second_sid + '-q'
        first, first_data = self.peer_candidate(first_sid, first_id, 'First question.')
        second, second_data = self.peer_candidate(second_sid, second_id, 'Different question.')
        self.assertEqual(check_session(first), [])
        self.assertEqual(check_session(second), [])
        # Both candidates passed before either publication; then the first is admitted.
        self.publish('rfirst', first_data)
        reviewer = self.instance / 'sessions/sreview'
        output = reviewer / 'output'
        output.mkdir(parents=True)
        candidate = second / 'output'
        hashes = runtime.tree_hashes(candidate)
        write_json(reviewer / 'input.json', {'instance': str(self.instance), 'session': 'sreview',
            'role': 'review', 'task': {'kind': 'candidate', 'candidate': str(candidate),
                                     'candidate_hashes': hashes}})
        write_json(output / 'assessment.json', assessment(second_data))
        (output / 'feedback.md').write_text('The distinct question and connection are supported.', encoding='utf-8')
        self.assertEqual(check_session(reviewer), [])
        self.publish('rsecond', second_data)
        model = replay(self.instance)
        self.assertEqual(model['nodes'][first_id]['statement'], 'First question.')
        self.assertEqual(model['nodes'][second_id]['statement'], 'Different question.')

    def test_identification_with_an_existing_node_reuses_it_while_admission_needs_a_supported_connection(self):
        # Admitting a proposal creates a node, so review must support the claim connecting it; identifying
        # the proposal with an existing node reuses a node the research already connects
        # (reference/review-output.md). The proposal here restates the root through an unsupported claim.
        sid = 's' + '1' * 32
        node_id = sid + '-q'
        folder, data = self.peer_candidate(sid, node_id, 'For every natural number n, n + 0 = n, restated.')
        candidate = folder / 'output'
        reviewer = self.instance / 'sessions/sreview'
        output = reviewer / 'output'
        output.mkdir(parents=True)
        write_json(reviewer / 'input.json', {'instance': str(self.instance), 'session': 'sreview',
            'role': 'review', 'task': {'kind': 'candidate', 'candidate': str(candidate),
                                     'candidate_hashes': runtime.tree_hashes(candidate)}})
        (output / 'feedback.md').write_text('The proposal restates the root; its connecting argument has a gap.',
                                            encoding='utf-8')
        verdict = assessment(data)
        verdict['claims'][0].update(status='unsupported', reason='The connecting argument has a gap.')
        verdict['relations'][0].update(accepted=False, reason='Its claim is unsupported.')
        write_json(output / 'assessment.json', verdict)
        errors = check_session(reviewer)
        self.assertTrue(any('new node needs supported connection' in error for error in errors), errors)
        verdict['nodes'][0].update(node='root', reason='The proposal states the root itself.')
        write_json(output / 'assessment.json', verdict)
        self.assertEqual(check_session(reviewer), [])
        self.publish('ridentified', data, verdict)
        self.assertEqual(replay(self.instance)['aliases'][node_id], 'root')


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

    def test_review_output_cannot_collide_with_the_formal_evidence_attachment(self):
        # Publication adds a formal solution's broker evidence under review/lean-evidence/
        # (Runner.copy_formal_evidence), as it adds review/ and provenance.json beside a candidate.
        runner, _ = self.candidate_pipeline()
        output = runner.session_dir('sreview') / 'output'
        self.assertEqual(check_session(output.parent), [])
        for name, directory in (('lean-evidence', True), ('Lean-Evidence', True), ('lean-evidence', False)):
            with self.subTest(name=name, directory=directory):
                path = output / name
                if directory:
                    path.mkdir()
                else:
                    path.write_text('Copied compile output.', encoding='utf-8')
                try:
                    errors = check_session(output.parent)
                    self.assertTrue(errors)
                    self.assertIn('reserved', errors[0])
                finally:
                    path.rmdir() if directory else path.unlink()

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
        shutil.copytree(candidate, candidate.parent / 'output')
        session = self.instance / 'sessions/sreview'
        (session / 'output').mkdir(parents=True)
        write_json(session / 'output/assessment.json', assessment(data))
        (session / 'output/feedback.md').write_text('Independent assessment.', encoding='utf-8')
        task = {'kind': 'candidate', 'candidate': str(candidate), 'candidate_hashes': runtime.tree_hashes(candidate),
                'peer': str(candidate.parent), 'source': str(runner.session_dir('sauthor'))}
        jid = runner.enqueue('review', task, pid, pid + ':review')
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': 'sreview',
                                           'role': 'review', 'task': task})
        (session / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (session / 'cli.stderr.log').write_text('', encoding='utf-8')
        runner.state['jobs'][jid].update(status='running', session='sreview')
        runner.state['jobs'][producer]['status'] = 'done'
        runner.state['sessions']['sreview'] = {'id': 'sreview', 'role': 'review', 'status': 'running', 'job': jid,
                                              'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': 1,
                                              'exit_code': 0}
        runner.save()
        return runner, runner.state['jobs'][jid]

    def test_publication_restart_rechecks_the_copied_candidate(self):
        runner, job = self.candidate_pipeline()
        self.assertEqual(check_session(runner.session_dir('sreview')), [])
        runner.prepare_publication('sreview', job, 'record')
        candidate = Path(job['task']['candidate'])
        (candidate / 'record.md').write_text('Changed after publication preparation.', encoding='utf-8')
        recovered = runtime.Runner(self.instance, self.skill)
        recovered.publish()
        job = recovered.state['jobs'][job['id']]
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(job['last_error'], 'candidate changed after review assignment')
        self.assertEqual(recovered.state['sessions']['sreview']['status'], 'failed')
        self.assertEqual(list((self.instance / 'knowledge/events').glob('*.json')), [])
        self.assertEqual(list((self.instance / 'knowledge/records').iterdir()), [])
        self.assertEqual(list((self.instance / 'runner').glob('stage-*')), [])
        restored = Path(job['task']['candidate'])
        self.assertNotEqual(restored, candidate)
        self.assertEqual(runtime.tree_hashes(restored), job['task']['candidate_hashes'])
        self.assertEqual((candidate / 'record.md').read_text(encoding='utf-8'),
                         'Changed after publication preparation.')
        self.finish_replacement_review(recovered, job)
        self.assertEqual(job['status'], 'done')
        event = read_json(next((self.instance / 'knowledge/events').glob('*.json')))
        published = self.instance / 'knowledge' / event['folder']
        self.assertEqual((published / 'record.md').read_bytes(), b'The proof.')

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
        restored = Path(job['task']['candidate'])
        self.assertNotEqual(restored, candidate)
        self.assertEqual(runtime.tree_hashes(restored), job['task']['candidate_hashes'])
        self.assertEqual((candidate / 'record.md').read_text(encoding='utf-8'),
                         'A different argument after assignment.')
        self.finish_replacement_review(runner, job)
        self.assertEqual(job['status'], 'done')
        event = read_json(next((self.instance / 'knowledge/events').glob('*.json')))
        self.assertEqual((self.instance / 'knowledge' / event['folder'] / 'record.md').read_bytes(), b'The proof.')

    def finish_replacement_review(self, runner, job):
        sid = 'sreplacement'
        session = runner.session_dir(sid)
        shutil.copytree(runner.session_dir('sreview') / 'output', session / 'output')
        write_json(session / 'input.json', {'instance': str(self.instance), 'session': sid,
                                           'role': 'review', 'task': job['task']})
        (session / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (session / 'cli.stderr.log').write_text('', encoding='utf-8')
        reviewer = {'id': sid, 'role': 'review', 'status': 'running', 'job': job['id'],
                    'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': 2,
                    'exit_code': 0}
        runner.state['sessions'][sid] = reviewer
        job.update(status='running', session=sid)
        runner.state['pipelines'][job['pipeline']]['review'] = sid
        runner.finish(sid, reviewer)

    def test_changed_candidate_and_changed_peer_output_return_to_peer_then_publish(self):
        runner, job = self.candidate_pipeline()
        candidate = Path(job['task']['candidate'])
        for folder in (candidate, candidate.parent / 'output'):
            (folder / 'record.md').write_text('Changed retained bytes.', encoding='utf-8')
        runner.session_dir('sauthor').mkdir(parents=True, exist_ok=True)
        write_json(runner.session_dir('sauthor') / 'declaration.json', {'sections': [{'id': 'sp', 'node': 'root', 'whole': True, 'statement': 'The whole root node.'}]})
        runner.finish('sreview', runner.state['sessions']['sreview'])
        pipeline = runner.state['pipelines'][job['pipeline']]
        self.assertEqual(job['status'], 'cancelled')
        self.assertEqual(pipeline['stage'], 'peer')
        peer_job = next(j for j in runner.state['jobs'].values() if j['role'] == 'peer')
        self.assertEqual(peer_job['status'], 'pending')
        self.assertIn(str(candidate.parent), peer_job['task']['previous_partial_sessions'])
        self.assertEqual(peer_job['task']['sections'], [{'id': 'sp', 'node': 'root', 'whole': True, 'statement': 'The whole root node.'}])
        self.assertEqual((candidate / 'record.md').read_text(encoding='utf-8'), 'Changed retained bytes.')
        peer_sid = 'snewpeer'
        peer = runner.session_dir(peer_sid)
        shutil.copytree(candidate.parent / 'output', peer / 'output')
        (peer / 'output/record.md').write_text('A newly developed proof.', encoding='utf-8')
        write_json(peer / 'input.json', {'instance': str(self.instance), 'session': peer_sid,
                                       'role': 'peer', 'task': peer_job['task']})
        (peer / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (peer / 'cli.stderr.log').write_text('', encoding='utf-8')
        worker = {'id': peer_sid, 'role': 'peer', 'status': 'running', 'job': peer_job['id'],
                  'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': 2,
                  'exit_code': 0}
        runner.state['sessions'][peer_sid] = worker
        peer_job.update(status='running', session=peer_sid)
        pipeline['peer'] = peer_sid
        runner.finish(peer_sid, worker)
        review_job = next(j for j in runner.state['jobs'].values()
                          if j['role'] == 'review' and j['status'] == 'pending')
        self.assertNotEqual(review_job['id'], job['id'])
        self.assertEqual(Path(review_job['task']['candidate']), peer / 'candidate')
        # A replacement for an interrupted review of the new candidate receives that review's partial
        # work, not the assessment of the damaged candidate the new peer replaced.
        cut_sid = 'sinterrupted'
        cut_folder = runner.session_dir(cut_sid)
        cut_folder.mkdir()
        (cut_folder / 'cli.stdout.jsonl').write_text('', encoding='utf-8')
        (cut_folder / 'cli.stderr.log').write_text('', encoding='utf-8')
        cut = {'id': cut_sid, 'role': 'review', 'status': 'running', 'job': review_job['id'],
               'model': 'codex/gpt-6.1-sol', 'provider': 'codex', 'started_at': 2, 'exit_code': 1}
        runner.state['sessions'][cut_sid] = cut
        review_job.update(status='running', session=cut_sid)
        runner.finish(cut_sid, cut)
        self.assertEqual((review_job['status'], review_job['task']['previous_partial_sessions']),
                         ('pending', [str(cut_folder)]))
        self.finish_replacement_review(runner, review_job)
        self.assertEqual(pipeline['stage'], 'done')
        event = read_json(next((self.instance / 'knowledge/events').glob('*.json')))
        self.assertEqual((self.instance / 'knowledge' / event['folder'] / 'record.md').read_text(encoding='utf-8'),
                         'A newly developed proof.')


    def test_interrupted_review_does_not_apply_a_structurally_usable_assessment(self):
        runner, job = self.candidate_pipeline()
        session = runner.state['sessions']['sreview']
        folder = runner.session_dir('sreview')
        verdict = read_json(folder / 'output/assessment.json')
        for publish in (True, False):
            verdict['publish'] = publish
            verdict['solutions'][0]['level'] = 'informal' if publish else 'none'
            write_json(folder / 'output/assessment.json', verdict)
            for code, refusal in ((1, None), (None, None),
                                  (0, {'reason': 'usage_limit'})):
                with self.subTest(publish=publish, exit_code=code, refusal=refusal):
                    self.assertEqual(check_session(folder), [])
                    session.update(status='running', exit_code=code, refusal=refusal)
                    job.update(status='running', session='sreview')
                    runner.finish('sreview', session)
                    self.assertEqual((session['status'], job['status']), ('failed', 'pending'))
                    self.assertEqual(runner.state['pipelines'][job['pipeline']]['stage'], 'review')
                    self.assertIn(str(folder), job['task']['previous_partial_sessions'])
                    self.assertIsNone(runner.state['publication'])
                    self.assertEqual(list((self.instance / 'knowledge/events').glob('*.json')), [])
                    self.assertEqual(list((self.instance / 'knowledge/records').iterdir()), [])
                    self.assertFalse(runner.archive_due)

    def test_completed_exclusion_releases_occupancy_without_publishing(self):
        runner, job = self.candidate_pipeline()
        pipeline = runner.state['pipelines'][job['pipeline']]
        producer = runner.session_dir(pipeline['producer'])
        producer.mkdir(parents=True)
        write_json(producer / 'declaration.json', {'sections': [
            {'id': pipeline['producer'] + '-1', 'node': 'root', 'whole': True, 'statement': None,
             'reasons': {}, 'at': 1}], 'at': 1})
        self.assertEqual(runner.available_nodes(), [])
        session = runner.session_dir('sreview')
        verdict = read_json(session / 'output/assessment.json')
        verdict.update(publish=False, reason='No useful supported material.',
                       index_assessment='The offered argument is unsupported.')
        verdict['claims'][0].update(status='unsupported', reason='The argument does not establish the claim.')
        verdict['solutions'][0].update(level='none', reason='No solution established.')
        write_json(session / 'output/assessment.json', verdict)
        reviewer = runner.state['sessions']['sreview']
        runner.finish('sreview', reviewer)
        self.assertEqual((reviewer['status'], job['status'], pipeline['stage']),
                         ('integrated', 'done', 'done'))
        self.assertTrue(reviewer['rejected'])
        self.assertEqual(pipeline['rejection_session'], 'sreview')
        self.assertIsNone(runner.state['publication'])
        self.assertEqual(list((self.instance / 'knowledge/events').glob('*.json')), [])
        self.assertEqual(list((self.instance / 'knowledge/records').iterdir()), [])
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'unresolved')
        self.assertEqual(runner.available_nodes(), ['root'])
        recovered = runtime.Runner(self.instance, self.skill)
        self.assertEqual(recovered.available_nodes(), ['root'])
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

    def test_axiom_output_must_name_the_exact_candidate_theorem(self):
        candidate, _, check, solution = self.evidence()
        log = self.instance / 'runner/lean/jobs' / check['job'] / 'stdout.log'
        for suffix, axioms in (
                ('does not depend on any axioms', []),
                ('depends on axioms: [propext]', ['propext'])):
            check['axioms'] = axioms
            with self.subTest(suffix=suffix, theorem='target'):
                log.write_text("'target' " + suffix + '\n', encoding='utf-8')
                audit_formal(self.instance, 'sreview', check, solution, candidate)
            for reported in ('not_target', 'Namespace.target'):
                with self.subTest(suffix=suffix, theorem=reported):
                    log.write_text("'" + reported + "' " + suffix + '\n', encoding='utf-8')
                    with self.assertRaisesRegex(Invalid, 'did not print target axiom dependencies'):
                        audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_modified_working_copy_cannot_reuse_old_compile(self):
        candidate, working, check, solution = self.evidence()
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        working.write_bytes(working.read_bytes() + b'\n#print axioms target\n')
        with self.assertRaisesRegex(Invalid, 'submitted compile'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_review_compile_must_be_the_candidate_bytes_plus_axiom_commands(self):
        # The broker compiled exactly this copy; a repaired or extended copy is not the final source.
        candidate, working, check, solution = self.evidence()
        result = self.instance / 'runner/lean/jobs' / check['job'] / 'result.json'
        original = (candidate / 'Proof.lean').read_bytes()
        for copied, message in (
                (original.replace(b'by trivial', b'by exact True.intro') + b'\n#print axioms target\n',
                 'unchanged copy'),
                (original + b'\ntheorem extra : True := by trivial\n#print axioms target\n',
                 'only axiom inspection commands')):
            with self.subTest(message=message):
                working.write_bytes(copied)
                write_json(result, {**read_json(result), 'source_sha256': hashlib.sha256(copied).hexdigest()})
                with self.assertRaisesRegex(Invalid, message):
                    audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_placeholder_axiom_is_rejected_despite_exit_zero(self):
        candidate, _, check, solution = self.evidence(axiom_line="'target' depends on axioms: [sorryAx]")
        check['axioms'] = ['sorryAx']
        with self.assertRaisesRegex(Invalid, 'unapproved axiom'):
            audit_formal(self.instance, 'sreview', check, solution, candidate)

    def test_formal_level_needs_a_candidate_lean_solution(self):
        # A solution without lean can still be marked formal by mistake; the check names what is missing.
        candidate, _, check, _ = self.evidence()
        with self.assertRaisesRegex(Invalid, "candidate solution's lean theorem and sources"):
            audit_formal(self.instance, 'sreview', check, {'lean': None}, candidate)

    def test_failed_single_file_review_compile_is_not_formal_evidence(self):
        candidate, _, check, solution = self.evidence()
        result = self.instance / 'runner/lean/jobs' / check['job'] / 'result.json'
        receipt = read_json(result)
        # Lean still prints the target's axioms when another declaration fails, so
        # only the compiler's exit code can reject this job. -9 is how Python
        # reports a compiler ended by a signal after its output was written.
        for code in (1, -9):
            with self.subTest(exit_code=code):
                write_json(result, {**receipt, 'exit_code': code})
                with self.assertRaisesRegex(Invalid, 'review compile failed'):
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

    def test_formal_check_must_match_candidate_theorem_sources_and_printed_axioms(self):
        # Each formal_check field is compared with the evidence it names; the reviewer's
        # own entry, or a stale one, does not pass the audit by itself.
        candidate, _, check, solution = self.evidence()
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        for change, message in (
                ({'alignment': 'differs'}, 'exact mathematical correspondence'),
                ({'theorem': 'other_target'}, 'formal theorem differs from candidate'),
                ({'axioms': ['propext']}, 'reported axioms differ from broker output'),
                ({'source_hashes': {'Proof.lean': hashlib.sha256(b'edited source').hexdigest()}},
                 'identify the final candidate source bytes'),
                ({'source_files': {'Proof.lean': 'input.json'}}, 'absent from the reviewing compile')):
            with self.subTest(change=change):
                with self.assertRaisesRegex(Invalid, message):
                    audit_formal(self.instance, 'sreview', {**check, **change}, solution, candidate)

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

    def stage_formal_evidence(self, check):
        stage = self.root / 'stage'
        (stage / 'review').mkdir(parents=True)
        write_json(stage / 'review/assessment.json', {'solutions': [{'level': 'formal', 'formal_check': check}]})
        runtime.Runner(self.instance, self.skill).copy_formal_evidence(stage, 'sreview')
        return stage / 'review/lean-evidence' / check['job']

    def test_duplicate_submission_id_is_audited_and_published_as_its_original_job(self):
        candidate, _, check, solution = self.evidence()
        original = check['job']
        duplicate = 'j' + 'b' * 32
        directory = self.instance / 'runner/lean/jobs' / duplicate
        directory.mkdir(parents=True)
        # The broker's answer to the same submission repeated while the first was still running.
        write_json(directory / 'result.json', {'id': duplicate, 'status': 'duplicate', 'duplicate_of': original})
        check['job'] = duplicate
        audit_formal(self.instance, 'sreview', check, solution, candidate)
        evidence = self.stage_formal_evidence(check)
        self.assertEqual(read_json(evidence / 'result.json')['id'], original)
        self.assertIn("'target' does not depend on any axioms",
                      (evidence / original / 'stdout.log').read_text(encoding='utf-8'))

    def test_published_build_evidence_keeps_module_logs_without_environment(self):
        _, _, check, _, receipt, _ = self.build_evidence()
        target_job = receipt['modules']['Proof']['job']
        write_json(self.instance / 'runner/lean/jobs' / target_job / 'launch.json',
                   {'argv': ['lean', 'Proof.lean'], 'cwd': 'work', 'env': {'PRIVATE_TOKEN': 'not for publication'}})
        evidence = self.stage_formal_evidence(check)
        self.assertEqual(read_json(evidence / 'result.json'), receipt)
        module = evidence / target_job
        self.assertEqual(read_json(module / 'result.json')['source_sha256'],
                         receipt['modules']['Proof']['source_sha256'])
        self.assertIn("'target' does not depend on any axioms",
                      (module / 'stdout.log').read_text(encoding='utf-8'))
        self.assertEqual(read_json(module / 'launch.json'), {'argv': ['lean', 'Proof.lean'], 'cwd': 'work'})


if __name__ == '__main__':
    unittest.main()
