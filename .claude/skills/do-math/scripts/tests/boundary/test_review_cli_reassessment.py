"""The CLI's assessment report reaches the owner's reassessment over the real Git process (``cli.execute``).

``cli.execute`` opens the repository and the engine with the product's default
ports and takes no Ports, so it runs the real Git process; that places this
test with the boundary tests (``test_cli_file_reads`` for the same reason).
The instance is ``support.review_sim.produced_sim()``: a formal theorem research
work produced, verified and reviewed on a Sim, whose repository objects are
written out as loose objects so a real ``git`` reads the same history. One of
its initial reviewers is recorded as having inherited the research work's
context, the qualified defect the report names.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math import cli
from do_math.canonical import exact_content_hash
from do_math.repository import ResearchRepository
from support.provider_probes import ObservedCalls
from support.review_sim import export_objects, produced_sim, reviewed_theorem, warm_produced


def setUpModule():
    warm_produced()


class CliReassessmentReportTests(unittest.TestCase):
    def test_cli_report_reaches_qualified_reassessment_and_replay_is_idempotent(self):
        """About 6 s over the real Git process and the real ports, besides the Sim template the module builds once."""
        sim = produced_sim()
        _, assessment = reviewed_theorem(sim)
        original = sim.runtime['review_cycles'][assessment['review_cycle_id']]
        reviewer = original['results']['initial:1:initial-0']['execution_id']
        [producer] = original['producer_execution_ids']
        sim.engine.runtime['executions'][reviewer]['context_origin'] = [producer]
        sim.engine._save()
        export_objects(sim)
        report = {'assessment_id': assessment['id'], 'assessment_sha256': exact_content_hash(assessment),
                  'evidence': {'kind': 'author_context', 'execution_id': reviewer}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'assessment-report.json'
            text = json.dumps(report, indent=1)
            path.write_bytes(text.encode('utf-8'))
            args = ['request', '--repository', str(sim.repository), '--instance', sim.instance_id,
                    '--assessment-reassessment-file', str(path)]
            with ObservedCalls(control=cli._control) as observed:
                first, code = cli.execute(cli.build_parser().parse_args(args), codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id, ports=sim.ports)
                second, second_code = cli.execute(cli.build_parser().parse_args(args), codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id, ports=sim.ports)
        self.assertEqual((code, second_code), (0, 0))
        for captured in observed.captured('control'):
            self.assertEqual((captured['action'], captured['text']), ('request', text))
            self.assertEqual(captured['config'], {'role': 'identity_review', 'assessment_reassessment': report})
        self.assertEqual(len(observed.captured('control')), 2)
        self.assertEqual((first['accepted'], first['effect']), (True, 'applied'))
        # The same report is the same request: the second run replays its receipt and processes nothing again.
        self.assertEqual((second['request_id'], second['replayed'], second['snapshot']),
                         (first['request_id'], True, first['snapshot']))
        _, instance, runtime = ResearchRepository(sim.repository, sim.instance_id, backend=sim.ports.git_backend, clock=sim.ports.clock).load()
        results = [row['result'] for row in runtime['history'] if row.get('kind') == 'assessment_reassessment_control']
        self.assertEqual([row['disposition'] for row in results], ['reassessment_opened'])
        cycle = runtime['review_cycles'][results[0]['review_cycle_id']]
        self.assertEqual(cycle['proposal']['assessment_reassessment']['assessment_id'], assessment['id'])
        use = next(row for row in instance['assessment_uses'].values() if row['assessment_id'] == assessment['id'])
        self.assertEqual(use['status'], 'suspended')


if __name__ == '__main__':
    unittest.main()
