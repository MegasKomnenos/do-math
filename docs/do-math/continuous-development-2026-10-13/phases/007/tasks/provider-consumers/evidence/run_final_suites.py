"""Run the three assigned final-source suites sequentially, with one worker."""
import sys
from run_command import EVIDENCE, run

groups = {
    'consumers-final': [
        'sim.test_operator_probe_contract', 'sim.test_operator_finish_recovery',
        'sim.test_operator_finish_provider', 'sim.test_operator_finish_cli',
        'sim.test_operator_finish_children', 'sim.test_operator_finish_supervision',
        'sim.test_operator_supervision_contract', 'sim.test_observation_delivery',
        'flows.test_provider_native_storage', 'flows.test_provider_raw_ingress',
        'flows.test_operator_recovery_contract', 'flows.test_scheduling_close_repair_exit',
        'flows.test_scheduling_close_remaining_exits', 'boundary.test_provider_worker_roots',
        'contracts.test_pairs',
        'flows.test_cross_required_events.RequiredEventSeedTests.test_installation_repair_unresolved_settles_and_does_not_repeat',
        'flows.test_cross_required_events.RequiredEventSeedTests.test_installation_repair_report_releases_one_successor',
    ],
    'boundaries': [
        'sim.test_provider_schema', 'sim.test_provider_runner', 'sim.test_provider_runner_gaps',
        'sim.test_provider_final_contract', 'sim.test_provider_pinned_runner',
        'sim.test_provider_workers', 'sim.test_provider_collection',
        'sim.test_provider_close_worker_rejections', 'unit.test_provider_live',
        'unit.test_provider_cli_surface', 'structure.test_test_smells', 'structure.test_layers',
    ],
    'corpus': ['structure.test_corpus', 'unit.test_corpus_replay', 'contracts.test_doubles_follow_corpus'],
}
for label, tests in groups.items():
    code = run(label + '-command', [sys.executable, '-u', '-B', '.claude/skills/do-math/scripts/run_tests.py',
                                   *tests, '--jobs', '1', '--output', str(EVIDENCE / label)])
    if code:
        raise SystemExit(code)
