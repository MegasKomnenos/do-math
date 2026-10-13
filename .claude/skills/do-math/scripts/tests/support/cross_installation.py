"""Actual repair launcher and Repository; only provider spawn/Ports are doubles."""
from pathlib import Path

from do_math import scheduled_operator
from support.operator_finish_scene import Scene


def recover_report(sim, outcome):
    assert outcome in {'unresolved', 'repaired'}
    scene = Scene(sim)
    scene.installation = sim.engine.installation_root
    scene.answer(outcome, diagnosed=True)

    def actual_input(call):
        prompt = call['prompt']
        assert 'failure_inputs' in prompt and 'installation:' in prompt
        assert 'repair_outcome' in call['output_schema']['properties']
        # This is explicitly an external provider/verification-port answer.
        # It certifies no actual repair or regression execution by this test.
        (Path(call['cwd']) / 'regression.txt').write_text(
            'Synthetic external repair report: ' + outcome + '. No real regression was executed.\n', encoding='utf-8')

    scene.cli.on_input = actual_input
    before = set(sim.runtime['executions'])
    result = scene.call(scheduled_operator.recovery)
    sim.restart()
    rows = [row for eid, row in sim.runtime['executions'].items() if eid not in before and row['role'] == 'recovery']
    assert len(rows) == 1, result
    assert rows[0]['status'] == 'ended', rows[0]
    assert rows[0]['capacity']['local_termination'] == 'confirmed', rows[0]
    assert all(job.done and job.closed for job in scene.jobs.launched)
    if outcome == 'unresolved':
        assert any(row['status'] == 'installation_repair_waiting'
                   for row in sim.runtime['operational_dispositions'].values())
    else:
        assert result['outcome'] == 'repaired', result
        assert any(row['status'] == 'applied' and row.get('result', {}).get('installation_repair', {}).get('status') == 'repaired'
                   for row in sim.runtime['operational_dispositions'].values())
    return result
