"""Inspect original reports and git revisions without executing product code."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path('C:/math')
OUT = Path(__file__).resolve().parent
SCRIPTS = REPO / '.claude/skills/do-math/scripts'
TABLE = REPO / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json'


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git_source(revision, name):
    path = '.claude/skills/do-math/scripts/' + name
    return subprocess.run(['git', 'show', revision + ':' + path], cwd=REPO,
                          capture_output=True, check=True).stdout.decode('utf-8-sig')


def function(source, name):
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1, (name, len(nodes))
    return nodes[0]


def asserts(source, name):
    return Counter(ast.unparse(n) for n in ast.walk(function(source, name)) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                   and n.func.value.id == 'self' and n.func.attr.startswith('assert'))


def calls(source, name):
    return Counter(ast.unparse(n.func) for n in ast.walk(function(source, name)) if isinstance(n, ast.Call))


def main():
    work = json.loads(read(TABLE))['current_work']
    reports = []
    for name in ('query_document_runtime_binding', 'cli_document_runtime_binding', 'role_manifest_document_binding',
                 'continuation_document_binding', 'profile_selection_document_binding'):
        entry = work[name]
        for stage, metadata in entry['reports'].items():
            path = REPO / metadata['path']
            raw = json.loads(read(path))
            rows = [row for group in raw['reports'] for row in group['rows']]
            selected, observed = Counter(raw['selected']), Counter(row['id'] for row in rows)
            source_changes = []
            for source_path, digest in raw['source_sha256'].items():
                current = SCRIPTS / source_path
                actual = hashlib.sha256(current.read_bytes()).hexdigest() if current.is_file() else None
                if actual != digest:
                    source_changes.append({'path': 'repo:.claude/skills/do-math/scripts/' + source_path,
                                           'recorded': digest, 'current': actual})
            reports.append({'id': entry['id'], 'stage': stage, 'path': 'repo:' + metadata['path'],
                'raw_hash_matches_record': hashlib.sha256(path.read_bytes()).hexdigest() == metadata['sha256'],
                'complete': raw['complete'], 'successful': raw['successful'], 'counts': raw['counts'],
                'selected': len(raw['selected']), 'row_count': len(rows),
                'selected_rows_match': selected == observed, 'outcomes': dict(Counter(row['outcome'] for row in rows)),
                'nonpassing_rows': [row for row in rows if row['outcome'] != 'passed'],
                'changed_during_run': raw['changed_during_run'], 'current_source_differences': source_changes})
    report = work['independent_execution']['plan']['tasks']
    optional = next(x for x in report if x['id'] == 'DOC-OPTIONAL-FLAG')
    for stage, metadata in optional['reports'].items():
        path = REPO / metadata['path']; raw = json.loads(read(path))
        reports.append({'id': 'B115', 'stage': stage, 'path': 'repo:' + metadata['path'],
            'raw_hash_matches_record': hashlib.sha256(path.read_bytes()).hexdigest() == metadata['sha256'],
            'complete': raw['complete'], 'successful': raw['successful'], 'counts': raw['counts'],
            'selected': len(raw['selected']),
            'nonpassing_rows': [r for g in raw['reports'] for r in g['rows'] if r['outcome'] != 'passed']})
    helper_path = 'tests/support/doc_code.py'
    old, current = git_source('136dc3d5', helper_path), read(SCRIPTS / helper_path)
    helper_comparison = []
    for name in ('producer_nodes', 'produced_object_schema', 'written_object_schema', 'consumed_object_schema',
                 'command_issues', 'documented_policies', 'policy_issues'):
        before, after = function(old, name), function(current, name)
        helper_comparison.append({'function': name,
            'same_ast_as_B115_review': ast.dump(before) == ast.dump(after),
            'current_lines': [after.lineno, after.end_lineno]})
    comparisons = []
    tasks = [
        ('B130', '6d1d1778', 'tests/unit/test_storage_record_queries.py', 'test_query_family_names_are_the_condition_grammar_names'),
        ('B130', '6d1d1778', 'tests/boundary/test_engine_cli.py', 'test_query_read_export_and_check_use_a_fixed_repository_snapshot'),
        ('B131', 'f3ee5aeb', 'tests/boundary/test_engine_cli.py', 'test_original_request_is_preserved_separately_from_the_mathematical_goal'),
        ('B131', 'f3ee5aeb', 'tests/boundary/test_engine_cli.py', 'test_profile_selection_respects_the_role_floor_without_model_execution'),
        ('B131', 'f3ee5aeb', 'tests/boundary/test_engine_cli.py', 'test_public_check_json_discovery_and_fixed_snapshot'),
        ('B132', 'e618f7b1', 'tests/unit/test_role_input_packaging.py', 'test_role_input_uses_current_schema_documents_and_private_resume_bytes'),
        ('B133', 'e54a6bd4', 'tests/unit/test_role_input_packaging.py', 'test_multihop_restores_latest_file_and_stage_evidence'),
        ('B134', '56e961ff', 'tests/unit/test_role_input_packaging.py', 'test_candidate_population_is_compact_profile_bound_and_reproducible'),
    ]
    for tag, revision, path, name in tasks:
        before, after, now = git_source(revision + '^', path), git_source(revision, path), read(SCRIPTS / path)
        old_asserts, new_asserts = asserts(before, name), asserts(after, name)
        comparisons.append({'increment': tag, 'path': 'repo:.claude/skills/do-math/scripts/' + path,
            'symbol': name, 'commit': revision, 'before_assertions': sum(old_asserts.values()),
            'after_assertions': sum(new_asserts.values()), 'removed_assertion_expressions': list((old_asserts-new_asserts).elements()),
            'added_assertion_expressions': list((new_asserts-old_asserts).elements()),
            'before_call_counts': calls(before, name), 'after_call_counts': calls(after, name),
            'current_call_counts': calls(now, name),
            'note': 'AST counts locate edits; human source/diff review decides equivalence, not these counts.'})
    save('history-verification.json', {'reports': reports, 'B115_helper_comparison': helper_comparison,
                                     'targeted_test_diffs': comparisons})
    print(json.dumps({'original_reports': len(reports),
        'hashes_all_match': all(r['raw_hash_matches_record'] for r in reports),
        'selected_rows_all_match': all(r.get('selected_rows_match', True) for r in reports),
        'B115_helpers': helper_comparison,
        'removed_assertions': [{'id': row['increment'], 'symbol': row['symbol'],
                               'expressions': row['removed_assertion_expressions']} for row in comparisons],
        'B134_current_source_differences': next(r['current_source_differences'] for r in reports
                                               if r['id']=='B134' and r['stage']=='green')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
