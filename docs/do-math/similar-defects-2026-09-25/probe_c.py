from pathlib import Path
import sys, json, tempfile, traceback
from copy import deepcopy

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_input_recovery import InputRecoveryPublicTests
from do_math.engine import ResearchEngine
from do_math import maintenance_gate
from do_math.trust_validation import verify_environment_files

def cancelled_activation():
    fixture = InputRecoveryPublicTests()
    fixture.setUp()
    try:
        owner = ResearchEngine(fixture.repo, fixture.identifier)
        old = owner.instance['trust_environments'][owner.instance['active_trust_environment']]
        chain = deepcopy(old['toolchain']); chain['version'] = 'audit-next-version'
        owner._apply_extended_control({'id':'UC-audit-register', 'action':'trust', 'origin':'user',
            'config':{'operation':'register', 'toolchain':chain, 'manifest':deepcopy(old['manifest']),
                      'allowed_axioms':deepcopy(old['allowed_axioms'])}})
        env = next(k for k, v in owner.instance['trust_environments'].items() if v['toolchain'] == chain)
        owner._apply_extended_control({'id':'UC-audit-transition', 'action':'trust', 'origin':'user',
            'config':{'operation':'transition', 'env_id':env}})
        owner._save()
        action = next(a for a in owner.runtime['queue'] if a['role'] == 'trust_activate')
        generator = owner._trust_activation_steps(action)
        execution_id, arguments = next(generator)
        owner._live_execution_ids.add(execution_id)
        maintenance_gate.apply_control(owner.runtime, {'id':'UC-fence', 'action':'quiesce', 'origin':'user',
            'text':'audit controlled interruption', 'created_at':owner.runtime['last_observed_utc']})
        assert arguments['should_stop']()
        result = verify_environment_files(**arguments)
        assert result['status'] == 'cancelled', result
        owner._local_call_returned(execution_id, result)
        try: generator.send(result)
        except StopIteration: pass
        queued = next(a for a in owner.runtime['queue'] if a['id'] == action['id'])
        _, _, persisted = owner.store.load()
        persisted_action = next(a for a in persisted['queue'] if a['id'] == action['id'])
        first = deepcopy(owner.runtime['executions'][execution_id])
        maintenance_gate.settle(owner.runtime)
        maintenance_gate.apply_control(owner.runtime, {'id':'UC-release', 'action':'release_quiesce', 'origin':'user',
            'config':{'fence_id':'UC-fence'}, 'created_at':owner.runtime['last_observed_utc']})
        owner._save()
        successor_action = next(a for a in owner.runtime['queue'] if a['id'] == action['id'])
        second_generator = owner._trust_activation_steps(successor_action)
        second_id, second_args = next(second_generator)
        successor = deepcopy(owner.runtime['executions'][second_id])
        owner._live_execution_ids.add(second_id)
        second_result = verify_environment_files(**second_args)
        owner._local_call_returned(second_id, second_result)
        try: second_generator.send(second_result)
        except StopIteration: pass
        return {'first_execution':execution_id, 'first_status':first['status'],
            'local_action_continuation':action.get('continuation_of'),
            'queued_continuation':queued.get('continuation_of'),
            'persisted_action_continuation':persisted_action.get('continuation_of'),
            'successor_continuation':successor.get('continuation_of'),
            'same_owner_activity':first['owner_activity_id'] == successor['owner_activity_id'],
            'successor_outcome':owner.runtime['executions'][second_id].get('outcome')}
    finally:
        fixture.doCleanups()

if __name__ == '__main__':
    result = cancelled_activation()
    assert result['first_status'] == 'ended'
    assert result['local_action_continuation'] == result['first_execution']
    assert result['persisted_action_continuation'] is None
    assert result['successor_continuation'] is None
    assert result['same_owner_activity'] is True
    assert result['successor_outcome'] == 'output_accepted'
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    Path(__file__).with_name('repro-result.json').write_text(rendered, encoding='utf-8')
    print(rendered)
