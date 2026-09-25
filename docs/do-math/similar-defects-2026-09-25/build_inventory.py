"""Repeatable bounded inventory; hits are navigation, not defect verdicts."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
OUT = Path(__file__).resolve().parent
PREFIX = '.claude/skills/do-math/'
RULES = {
 'T1_trust_observation': r'trust_environment_errors|require_trust_environment|verify_environment_files|EnvironmentChecks|_observe_environment|verify_formal',
 'T2_storage_identity': r'payload|_validated_read|save_with_state|validate_candidate|exact_content_hash|fingerprint',
 'T3_launch_termination': r'launch_ticket|termination_confirmed|named_job_empty|local_termination|owner_ended|launch_not_created',
 'T4_observation_order': r'ObservationBatch|_observe_running|on_observation|request_self_check|record_delivery|acknowledged_source|def pump|def collect',
 'T5_evidence_handoff': r'operational_evidence|admissible_basis_refs|capture_checkpoint_files|bind_checkpoint_artifact|recovered_checkpoint|reference_catalog|validation_context|request_source_ref',
 'T6_semantic_currentness': r'assessment_basis|assessment_current|action_read_ids|contract_review_current|refresh_task_assessments|relation_claim|formal_result_refs|assessment_refs',
 'T7_event_responsibility': r'event_refs|pending_events|dispatch_occupied|_consume_action_events|task_assessment_invalidated',
 'T8_maintenance_telemetry': r'maintenance_fence|quiesce|operation_trace|engine_operation|workspace_operation|phase_rows',
 'N1_public_input_boundary': r'def control|def _.*control|_json_document|manifest_errors|except \(ValueError, KeyError, TypeError\)',
 'N2_detached_state_continuation': r'continuation_of|queued.update|save_with_state|self.head, self.instance, self.runtime',
}
def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args]).decode('utf-8')

files = git('ls-files', '-z', '--', PREFIX).strip('\0').split('\0')
changes = {}
for commit in ('ff9b2b9c', 'c44dd7b7'):
    changes[commit] = git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', commit, '--', PREFIX).strip('\0').split('\0')
inventory, hits = [], {key: [] for key in RULES}
for name in files:
    path = ROOT / name
    raw = path.read_bytes()
    lines = raw.decode('utf-8-sig').splitlines()
    local_hits = {}
    for key, expression in RULES.items():
        matches = [index for index, line in enumerate(lines, 1) if re.search(expression, line)]
        if matches:
            local_hits[key] = matches
            hits[key].append({'path': name, 'lines': matches})
    inventory.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'lines': len(lines),
        'surface': 'test' if '/tests/' in name else 'code' if path.suffix in {'.py', '.ps1'} else 'document_or_data',
        'changed_in': [commit for commit, names in changes.items() if name in names], 'navigation_hits': local_hits})
result = {'head': git('rev-parse', 'HEAD').strip(), 'scope': PREFIX,
          'note': 'Every tracked canonical file inventoried. Regex hits are navigation only; see manual coverage report for verdicts.',
          'file_count': len(files), 'changed_file_count': len(set(sum(changes.values(), []))),
          'rules': RULES, 'files': inventory, 'hits': hits}
(OUT / 'inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'files': len(files), 'changed_files': result['changed_file_count'],
    'hits': {key: {'files': len(rows), 'lines': sum(len(r['lines']) for r in rows)} for key, rows in hits.items()}}, indent=2))
