"""Read-only source census for document-closeout; never import the product/tests.

This records syntax and historical evidence, not runtime conformance. All writes
are confined to this task's evidence directory. Run with the assigned Python -B.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPO = Path('C:/math')
OUT = Path(__file__).resolve().parent
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
SKILL = REPO / '.claude/skills/do-math'
SUPPORT = SKILL / 'scripts/tests/support/doc_code.py'
TABLE = REPO / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json'


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    return 'repo:' + Path(path).relative_to(REPO).as_posix()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args):
    result = subprocess.run(['git', *args], cwd=REPO, capture_output=True, check=True)
    return result.stdout


def main():
    source = read(SUPPORT)
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    patterns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('SPAN', 'FIELD', 'ENTRY'):
                    patterns[target.id] = re.compile(ast.literal_eval(node.value.args[0]))
    # Explicit enumeration follows documents(), whose source is recorded below.
    documents = [SKILL / name for name in ('SKILL.md', 'README.md', 'GLOSSARY.md')]
    documents += sorted((SKILL / 'references').glob('*.md'))
    documents += sorted((SKILL / '계약').glob('*.md'))
    occurrences, spans, commands, policies, files = [], [], [], [], []
    for path in documents:
        text = read(path)
        files.append({'path': ref(path), 'sha256': digest(path), 'bytes': path.stat().st_size,
                      'lines': len(text.splitlines())})
        for line_number, line in enumerate(text.splitlines(), 1):
            directive = re.search(r'<!-- do-math fields: (.*?) -->', line)
            aliases = dict(item.strip().split('=', 1) for item in directive.group(1).split(',')) if directive else {}
            for token in patterns['SPAN'].findall(line):
                row = {'document': ref(path), 'line': line_number, 'token': token, 'text': line}
                spans.append({k: v for k, v in row.items() if k != 'text'})
                if patterns['FIELD'].fullmatch(token):
                    root = re.split(r'[.\[]', token)[0]
                    category = 'field'
                    if '[' not in token and token.endswith(('.py', '.json', '.md', '.txt', '.jsonl', '.exe')):
                        category = 'filename'
                    elif '[' not in token and root in {'contract_check', 'integration'}:
                        category = 'diagnostic'
                    occurrences.append({**row, 'root': root, 'owner': aliases.get(root, root),
                                        'aliases': aliases, 'category': category})
                for policy in re.findall(r'\b[a-z][a-z0-9_]*policy\b', token):
                    policies.append({**row, 'policy': policy})
            for command in patterns['ENTRY'].findall(line):
                commands.append({'document': ref(path), 'line': line_number, 'command': command, 'text': line})
    bodies = []
    for node in functions['field_schemas'].body:
        bodies.append({'line': node.lineno, 'end_line': node.end_lineno,
                       'source': ast.get_source_segment(source, node)})
    calls = []
    helpers = {'produced_object_schema', 'written_object_schema', 'consumed_object_schema'}
    for node in ast.walk(functions['field_schemas']):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in helpers:
            calls.append({'line': node.lineno, 'end_line': node.end_lineno,
                          'helper': node.func.id, 'source': ast.get_source_segment(source, node)})
    census = {'method': 'stdlib text/AST census only; product and test modules were not imported or run',
              'documents_rule': ast.get_source_segment(source, functions['documents']),
              'documents': files, 'field_occurrences': occurrences,
              'command_mentions': commands, 'policy_mentions': policies,
              'all_inline_spans': spans, 'field_schemas_statements': bodies,
              'remaining_ast_calls': sorted(calls, key=lambda row: row['line'])}
    save('source-census.json', census)

    baseline = json.loads(read(RUN / 'sources/baseline.json'))
    comparison = []
    for item in baseline['source_files'] + baseline['product_files']:
        path = REPO / item['path']
        actual = digest(path) if path.is_file() else None
        if actual != item['sha256']:
            comparison.append({'path': ref(path), 'baseline_sha256': item['sha256'], 'current_sha256': actual})
    save('baseline-observation.json', {
        'head': git('rev-parse', 'HEAD').decode().strip(), 'baseline_head': baseline['head'],
        'compared_files': len(baseline['source_files']) + len(baseline['product_files']),
        'hash_mismatches': comparison,
        'status_at_start': git('-c', 'core.quotepath=false', 'status', '--short').decode('utf-8'),
        'note': 'Existing dirty/untracked work is observed, not changed or claimed by this task.'})

    work = json.loads(read(TABLE))['current_work']
    review = work['independent_execution']['document_review']
    recent_keys = ('record_map_runtime_binding', 'summary_fact_runtime_bindings',
                   'status_repository_document_binding', 'progress_file_document_binding',
                   'query_document_runtime_binding', 'cli_document_runtime_binding',
                   'role_manifest_document_binding', 'continuation_document_binding',
                   'profile_selection_document_binding')
    save('history-selected.json', {'source': ref(TABLE), 'sha256': digest(TABLE),
                                 'document_review': review,
                                 'increments': {key: work[key] for key in recent_keys}})
    report_info = []
    for key in recent_keys:
        for stage, metadata in work[key].get('reports', {}).items():
            if not isinstance(metadata, dict) or 'path' not in metadata:
                continue
            path = REPO / metadata['path']
            raw = json.loads(read(path))
            report_info.append({'increment': work[key]['id'], 'stage': stage, 'path': ref(path),
                                'sha256': digest(path), 'recorded_sha256': metadata.get('sha256'),
                                'keys': list(raw),
                                'summary': {k: raw[k] for k in
                                    ('complete', 'successful', 'counts', 'selected', 'tests',
                                     'changed_during_run', 'total_seconds')},
                                'group_keys': [list(g) for g in raw.get('reports', [])]})
    save('raw-report-inspection.json', report_info)
    commits = {'B130': '6d1d1778', 'B131': 'f3ee5aeb', 'B132': 'e618f7b1',
               'B133': 'e54a6bd4', 'B134': '56e961ff'}
    for name, commit in commits.items():
        patch = git('show', '--format=fuller', '--no-ext-diff', commit, '--',
                    '.claude/skills/do-math/scripts/tests')
        (OUT / (name + '.patch')).write_bytes(patch)
    print(json.dumps({'documents': len(files),
                      'field_occurrences': sum(r['category'] == 'field' for r in occurrences),
                      'field_owners': len({r['owner'] for r in occurrences if r['category'] == 'field'}),
                      'inline_spans': len(spans), 'remaining_ast_call_sites': len(calls),
                      'baseline_mismatches': comparison, 'raw_reports': len(report_info)},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
