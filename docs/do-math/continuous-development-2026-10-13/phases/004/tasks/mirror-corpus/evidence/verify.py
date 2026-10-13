"""Verify the handoff and expose the unresolved clean conversion as a failure."""
import collections
import hashlib
import json
from pathlib import Path

from audit import RUN, allowed, git
from run_command import EVIDENCE, ROOT, changed, snapshot, write_json


def read(path):
    return json.loads(path.read_bytes())


before = read(EVIDENCE / 'source-before.json')
after = snapshot()
write_json(EVIDENCE / 'source-final.json', after)
modified = changed(before, after)
outside = [p for p in modified if not allowed(p)]
prior_dir = RUN / 'phases/003/tasks/provider-smoke/evidence'
prior_final = read(prior_dir / 'source-final.json')
prior_changes = {row['path'] for row in read(prior_dir.parent / 'report.json')['changes']}
start_mismatches = [p for p, sha in prior_final.items() if before.get(p) != sha]
change_rows = [{'path': p, 'before_sha256': before.get(p), 'after_sha256': after.get(p),
                'also_changed_in_phase_003': p in prior_changes} for p in modified]
write_json(EVIDENCE / 'changes.json', change_rows)

baseline = read(EVIDENCE / 'corpus-before.json')
final = read(EVIDENCE / 'corpus-final.json')
canonical_prefix = '.claude/skills/do-math/scripts/tests/corpus/'
canonical_changes = [p for p in modified if p.startswith(canonical_prefix)]
corpus_initial_matches = all(before[row['path']] == row['sha256']
                             for tree in baseline['trees'].values() for row in tree['files'].values())
runs = {}
for name, runtime in [('canonical-replay', '.claude'), ('mirror-replay', '.agents')]:
    report = read(EVIDENCE / name / 'report.json')
    command = read(EVIDENCE / (name + '-command') / 'command.json')
    rows = [row for group in report['reports'] for row in group['rows']]
    row_ids = [row['id'] for row in rows]
    source_mismatches = [p for p, sha in report['source_sha256'].items()
                         if after.get(runtime + '/skills/do-math/scripts/' + p) != sha]
    during = command['changed_sources']
    checked = {'selected': report['selected'], 'rows': rows, 'counts': report['counts'],
               'selection_matches_rows': collections.Counter(report['selected']) == collections.Counter(row_ids),
               'unique_rows': len(row_ids) == len(set(row_ids)),
               'all_passed': all(row['outcome'] == 'passed' for row in rows),
               'complete': report['complete'], 'successful': report['successful'],
               'fixture_counts': report['fixture_counts'], 'exit_code': command['exit_code'],
               'pid': command['pid'], 'started_at': command['started_at'], 'ended_at': command['ended_at'],
               'report_changed_during_run': report['changed_during_run'],
               'whole_tree_changed_during_run': during,
               'only_timing_cache_changed': during == [runtime + '/skills/do-math/scripts/tests/.timings.json'],
               'python_files_checked': len(report['source_sha256']), 'python_mismatches': source_mismatches,
               'report_sha256': hashlib.sha256((EVIDENCE / name / 'report.json').read_bytes()).hexdigest()}
    assert checked['selection_matches_rows'] and checked['unique_rows'] and checked['all_passed']
    assert checked['complete'] and checked['successful'] and command['exit_code'] == 0
    assert not checked['fixture_counts'] and not checked['report_changed_during_run']
    assert checked['only_timing_cache_changed'] and not source_mismatches
    runs[name] = checked

old_report = read(prior_dir / 'mirror-replay/report.json')
old_rows = [row for group in old_report['reports'] for row in group['rows']]
prior_head = read(RUN / 'phases/003/manager-evidence/verification.json')['head']
prior_rules = git(['show', prior_head + ':.agents/diff/_rules.json'])
prior_reuse = {'selected': len(old_report['selected']), 'rows': len(old_rows), 'counts': old_report['counts'],
               'python_hashes_match_initial': all(before.get('.agents/skills/do-math/scripts/' + p) == sha
                                                  for p, sha in old_report['source_sha256'].items()),
               'report_sha256': hashlib.sha256((prior_dir / 'mirror-replay/report.json').read_bytes()).hexdigest(),
               'phase_003_rules_snapshot_present': '.agents/diff/_rules.json' in prior_final,
               'phase_003_git_rules': prior_rules,
               'rules_match_phase_003_git_revision_with_crlf': before['.agents/diff/_rules.json'] == hashlib.sha256(prior_rules['stdout'].replace('\n', '\r\n').encode('utf-8')).hexdigest()}
sha_bindings = {runtime: len(tree['sha_bindings']) for runtime, tree in final['trees'].items()}
result = {'head': git(['rev-parse', 'HEAD'])['stdout'].strip(), 'source_file_count': len(after),
          'phase_003_source_file_count': len(prior_final), 'phase_003_to_start_mismatches': start_mismatches,
          'changes': change_rows, 'outside_writes': outside,
          'unchanged_phase_003_changes': sorted(prior_changes - set(modified)),
          'canonical_corpus_changes': canonical_changes, 'initial_corpus_hashes_match': corpus_initial_matches,
          'byte_differences': final['byte_differences'], 'sha_bindings_checked': sha_bindings,
          'git_clean_differences': final['git_clean_differences'], 'runs': runs,
          'historical_failure_reuse': prior_reuse,
          'generator_implementation_unchanged': before['.claude/skills/writing-skills/scripts/build_skill_mirrors.py'] == after['.claude/skills/writing-skills/scripts/build_skill_mirrors.py'],
          'overlay_manifest_unchanged': before['.agents/diff/_manifest.json'] == after['.agents/diff/_manifest.json']}
inputs = read(EVIDENCE / 'input-hashes-before.json')
now_inputs = {ref: hashlib.sha256(((RUN if ref.startswith('run:') else ROOT) / ref.split(':', 1)[1]).read_bytes()).hexdigest()
              for ref in inputs}
write_json(EVIDENCE / 'input-hashes-final.json', now_inputs)
result['input_changes'] = changed(inputs, now_inputs)
(EVIDENCE / 'git-status-final.txt').write_text(git(['-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])['stdout'], encoding='utf-8')
assert not outside and not start_mismatches and not canonical_changes and corpus_initial_matches
assert not final['byte_differences'] and all(not tree['bad_bindings'] and not tree['undeclared'] for tree in final['trees'].values())
assert result['generator_implementation_unchanged'] and result['overlay_manifest_unchanged']
assert prior_reuse['python_hashes_match_initial'] and prior_reuse['rules_match_phase_003_git_revision_with_crlf']
result['in_scope_verification_passed'] = True
result['all_acceptance_conditions_met'] = not final['git_clean_differences']
write_json(EVIDENCE / 'verification.json', result)
print(json.dumps({k: v for k, v in result.items() if k not in ('changes', 'runs', 'unchanged_phase_003_changes')}, ensure_ascii=False))
raise SystemExit(0 if result['all_acceptance_conditions_met'] else 1)
