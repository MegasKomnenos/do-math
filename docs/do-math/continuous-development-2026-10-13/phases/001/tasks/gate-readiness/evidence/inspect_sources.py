"""Read-only source/report inventory. Does not import or execute do-math code."""
from __future__ import annotations

import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import importlib.metadata
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path('C:/math')
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OLD = ROOT / 'docs/do-math/시험-재편-2026-09-29'
SKILL = ROOT / '.claude/skills/do-math'
SCRIPTS = SKILL / 'scripts'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', errors='replace'))
    return p.stdout.decode('utf-8').strip()


def snapshot(label):
    baseline = read(RUN / 'sources/baseline.json')
    # -z is used below to avoid Git's quoting of non-ASCII filenames.
    p = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', '.claude/skills/do-math'], cwd=ROOT, capture_output=True, check=True)
    names = sorted(set(p.stdout.decode('utf-8').strip('\0').split('\0')))
    product = {name: sha(ROOT / name) for name in names if (ROOT / name).is_file()}
    original = {row['path']: row['sha256'] for row in baseline['product_files']}
    sources = baseline['source_files'] + baseline['engine_files']
    comparison = [{'path': row['path'], 'baseline': row['sha256'], 'current': sha(ROOT / row['path']) if (ROOT / row['path']).is_file() else None} for row in sources]
    result = {
        'observed_at': datetime.now(timezone.utc).isoformat(),
        'head': git('rev-parse', 'HEAD'), 'baseline_head': baseline['head'],
        'baseline_product_count': len(original), 'current_product_count': len(product),
        'product_sha256': product,
        'baseline_differences': [name for name in sorted(product.keys() | original.keys()) if product.get(name) != original.get(name)],
        'source_engine_comparison': comparison,
        'git_status': git('-c', 'core.quotepath=false', 'status', '--short'),
        'note': 'Hashes of tracked and nonignored untracked canonical skill files; no product imports or test collection.'
    }
    if label == 'after':
        before = read(OUT / 'source-before.json')['product_sha256']
        result['changed_since_task_start'] = [name for name in sorted(before.keys() | product.keys()) if before.get(name) != product.get(name)]
    save('source-' + label + '.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['product_sha256', 'git_status', 'source_engine_comparison']}, ensure_ascii=False))
    print('source/engine differences:', [row['path'] for row in comparison if row['baseline'] != row['current']])


def summary(path):
    d = read(path)
    rows = [row for group in d.get('reports', []) for row in group.get('rows', []) if not row.get('fixture')]
    selected = d.get('selected', [])
    observed = Counter(row['id'] for row in rows)
    current = {p.relative_to(SCRIPTS).as_posix(): sha(p) for p in SCRIPTS.rglob('*.py') if '__pycache__' not in p.parts}
    recorded = d.get('source_sha256', {})
    return {
        'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
        **{k: d.get(k) for k in ['complete', 'successful', 'counts', 'fixture_counts', 'total_seconds', 'changed_during_run', 'folders', 'tiers', 'tests']},
        'selected_count': len(selected), 'rows_count': len(rows),
        'missing_selected': sorted(set(selected) - observed.keys()),
        'unexpected_rows': sorted(observed.keys() - set(selected)),
        'duplicate_rows': {k: n for k, n in observed.items() if n != 1},
        'nonpasses': [row for row in rows if row['outcome'] != 'passed'],
        'source_hash_count': len(recorded),
        'current_source_differences': [name for name in sorted(current.keys() | recorded.keys()) if current.get(name) != recorded.get(name)] if recorded else None,
        'groups': [{k: group.get(k) for k in ['group', 'complete', 'successful', 'tests_run', 'returncode']} for group in d.get('reports', [])],
        'selected_ids': selected,
    }


def reports():
    paths = [p for p in (OLD / '검증').rglob('*.json') if any('B' + str(n) in str(p.parent) for n in range(129, 135)) and p.name in ['report.json', 'repair.json']]
    work = read(OLD / '단계-전환표-2026-10-03.json')['current_work']
    expected_hashes = {}
    for key in ['query_document_runtime_binding', 'cli_document_runtime_binding', 'role_manifest_document_binding', 'continuation_document_binding', 'profile_selection_document_binding']:
        for row in work[key]['reports'].values():
            paths.append(ROOT / row['path'])
            expected_hashes[row['path']] = row['sha256']
    result = [summary(path) for path in sorted(paths)]
    for item in result:
        expected = expected_hashes.get(item['path'])
        item['matches_transition_table_sha256'] = item['sha256'] == expected if expected else None
    save('historical-reports.json', result)
    for item in result:
        print(json.dumps({k: item[k] for k in ['path', 'complete', 'successful', 'counts', 'total_seconds', 'selected_count', 'rows_count', 'missing_selected', 'matches_transition_table_sha256']}, ensure_ascii=False))
        print('current difference count:', len(item['current_source_differences'] or []))


def literal(path, name):
    for node in ast.parse(path.read_text(encoding='utf-8-sig')).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError((path, name))


def population():
    layers = literal(SCRIPTS / 'do_math/layers.py', 'LAYERS')
    eligible = {name for name, layer in layers.items() if layer in ('1', '2', '3')}
    tasks = read(OLD / '단계-전환표-2026-10-03.json')['current_work']['independent_execution']['plan']['tasks']
    shards = []
    memberships = Counter()
    for task in tasks:
        if task['id'].startswith('MUTATION-') and task['id'].split('-')[-1].isdigit():
            names = task['modification_scope']['allowed']
            rows = []
            for name in names:
                path = ROOT / name
                module = path.relative_to(SCRIPTS).as_posix()
                memberships[module] += 1
                rows.append({'path': name, 'module': module, 'exists': path.is_file(), 'layer': layers.get(module), 'eligible': module in eligible, 'sha256': sha(path) if path.is_file() else None})
            shards.append({'id': task['id'], 'population': task['population'], 'files': rows})
    tests = SCRIPTS / 'tests'
    folders = literal(SCRIPTS / 'run_tests.py', 'FOLDERS')
    disk_modules = {folder: [p.relative_to(tests).as_posix() for p in sorted((tests / folder).rglob('test_*.py'))] for folder in folders}
    index_path = tests / '.selection-index.json'
    index = read(index_path) if index_path.exists() else None
    index_info = {'exists': bool(index), 'path': index_path.relative_to(ROOT).as_posix()}
    if index:
        p = subprocess.run(['git', 'merge-base', '--is-ancestor', index['commit'], 'HEAD'], cwd=ROOT, capture_output=True)
        index_info.update(sha256=sha(index_path), format=index['format'], commit=index['commit'], created=index['created'], tests=len(index['tests']), files=len(index['files']), ancestor_exit=p.returncode)
    result = {
        'method': 'AST literal tables and filesystem inventory only; no discovery, imports, mutation execution or denominator claim for functions.',
        'layer_counts': dict(Counter(layers.values())), 'eligible_modules': sorted(eligible),
        'eligible_missing_on_disk': sorted(name for name in eligible if not (SCRIPTS / name).is_file()),
        'shards': shards, 'shard_count': len(shards), 'shard_unique_files': len(memberships),
        'eligible_not_in_shards': sorted(eligible - memberships.keys()),
        'shard_ineligible_files': sorted(memberships.keys() - eligible),
        'shard_duplicate_files': {name: n for name, n in memberships.items() if n > 1},
        'test_module_counts': {k: len(v) for k, v in disk_modules.items()}, 'disk_test_modules': disk_modules,
        'existing_selection_index': index_info,
        'pseudo_tested': {'exists': (tests / 'pseudo_tested.json').is_file(), 'content': read(tests / 'pseudo_tested.json') if (tests / 'pseudo_tested.json').is_file() else None},
        'corpus': corpus_inventory(),
    }
    save('population-and-corpus.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['shards', 'disk_test_modules', 'eligible_modules', 'pseudo_tested', 'corpus']}, ensure_ascii=False, indent=2))
    print('shards:', [(s['id'], len(s['files'])) for s in shards])
    print('pseudo_tested:', result['pseudo_tested'])
    print('corpus:', json.dumps({k: v for k, v in result['corpus'].items() if k != 'entries'}, ensure_ascii=False))


def corpus_inventory():
    corpus = SCRIPTS / 'tests/corpus'
    manifest = read(corpus / 'manifest.json')
    entries = []
    declared = set()
    for entry in manifest['entries']:
        files = set(entry[k] for k in ['path', 'final_path', 'source_path', 'compiled_path'] if k in entry)
        files.update(row['path'] for row in entry.get('recordings', []))
        declared.update(files)
        measurements = {name: {'exists': (corpus / name).is_file(), 'sha256': sha(corpus / name) if (corpus / name).is_file() else None} for name in sorted(files)}
        entries.append({'entry': entry, 'files': measurements, 'main_matches_recorded_hash': sha(corpus / entry['path']) == entry['source_sha256'] if entry.get('source_sha256') else None})
    present = {p.relative_to(corpus).as_posix() for p in corpus.rglob('*') if p.is_file()} - {'manifest.json', '.gitattributes'}
    return {'manifest_sha256': sha(corpus / 'manifest.json'), 'supported_stream_versions': manifest['supported_stream_versions'], 'entry_count': len(entries), 'kinds': dict(Counter(e['kind'] for e in manifest['entries'])), 'file_count': len(present), 'bytes_without_manifest': sum((corpus / name).stat().st_size for name in present), 'undeclared_files': sorted(present - declared), 'missing_files': sorted(declared - present), 'entries': entries}


def environment():
    lean = ROOT / '.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe'
    mathlib = ROOT / '.skill-workspace/do-math-toolchains/mathlib-4.32.0'
    codex = Path('C:/Users/wogud/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe')
    paths = [lean, lean.with_name('lake.exe'), mathlib / 'lean-toolchain', mathlib / 'lake-manifest.json', mathlib / 'lakefile.toml', mathlib / '.do-math-ready', mathlib / '.lake/packages/mathlib/Mathlib.lean', mathlib / '.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean', ROOT / 'services/scholarly-mcp/server.py', ROOT / 'services/scholarly-mcp/.venv/Scripts/python.exe', Path(sys.executable).with_name('pythonw.exe'), codex]
    path_info = [{'path': str(path), 'exists': path.is_file()} for path in paths]
    versions = []
    commands = [[sys.executable, '--version'], [shutil.which('git'), '--version'], [str(codex), '--version'], [shutil.which('claude'), '--version'], [str(lean), '--version'], [str(lean.with_name('lake.exe')), '--version'], [shutil.which('powershell'), '-NoProfile', '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.ToString()']]
    for argv in commands:
        if not argv[0] or not Path(argv[0]).is_file():
            versions.append({'argv': argv, 'cwd': str(ROOT), 'status': 'not_run', 'exit_code': None, 'reason': 'executable not present'})
            continue
        start = time.monotonic()
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        versions.append({'argv': argv, 'cwd': str(ROOT), 'status': 'executed', 'exit_code': p.returncode, 'stdout': p.stdout.decode('utf-8', errors='replace'), 'stderr': p.stderr.decode('utf-8', errors='replace'), 'seconds': round(time.monotonic() - start, 3)})
    packages = {}
    for name in ['coverage', 'hypothesis', 'jsonschema']:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    result = {'observed_at': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(), 'sys_executable': sys.executable, 'sys_monitoring_available': hasattr(sys, 'monitoring'), 'which': {name: shutil.which(name) for name in ['python', 'pythonw', 'git', 'claude', 'codex', 'powershell', 'pwsh', 'lean', 'lake', 'elan']}, 'paths': path_info, 'versions': versions, 'test_packages': packages, 'lean_test_override_present': bool(os.environ.get('DO_MATH_KNOWLEDGE_TEST_LEAN')), 'mathlib_toolchain': (mathlib / 'lean-toolchain').read_text(encoding='utf-8') if (mathlib / 'lean-toolchain').is_file() else None, 'credential_access': 'No credential files, tokens, authentication state or general environment dump were read. Live calls, downloads, compilation and task registration were not attempted.'}
    save('environment.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def contracts():
    relative = '.claude/skills/do-math/scripts/'
    requests = {
        'run_tests.py': ['test_modules', 'discover', '_edition', 'main', 'wait_for_worker', '_isolated', 'closing_eligible', '_finish_t3'],
        'tests/support/mutation.py': ['functions', 'rule_of', 'mutate', 'tests_for', '_child_run', 'run', 'passed', '_child', 'main'],
        'tests/support/branch_gate.py': ['gate', 'build_index', 'write_index'],
        'tests/support/t3_store.py': ['plan', 'read'],
        'probe_cli.py': ['background_completed_before_result', 'run_case', 'main'],
    }
    records = []
    interfaces = {}
    for name, symbols in requests.items():
        path = SCRIPTS / name
        source = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(source)
        snippets = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in symbols:
                snippets.append({'symbol': node.name, 'line': node.lineno, 'end_line': node.end_lineno, 'text': ast.get_source_segment(source, node)})
        options = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
                options.extend(arg.value for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith('--'))
        interfaces[relative + name] = sorted(options)
        records.append({'path': relative + name, 'sha256': sha(path), 'symbols': snippets})
    store_path = SCRIPTS / 'tests/.t3-store/records.json'
    old_store = read(store_path) if store_path.is_file() else None
    store = {'path': store_path.relative_to(ROOT).as_posix(), 'exists': old_store is not None, 'current_format': literal(SCRIPTS / 'tests/support/t3_store.py', 'FORMAT')}
    if old_store:
        store.update(sha256=sha(store_path), format=old_store.get('format'), created=old_store.get('created'), modules=len(old_store.get('modules', {})), coverage=old_store.get('coverage'))
    data = {'method': 'AST extraction only; exact source excerpts are identified by source SHA256 and line numbers. No extracted function was executed.', 'cli_options': interfaces, 'sources': records, 'tiers': literal(SCRIPTS / 'run_tests.py', 'TIERS'), 'existing_t3_store': store}
    save('source-contracts.json', data)
    print(json.dumps({'sources': len(records), 'cli_options': interfaces, 'existing_t3_store': store}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if sys.argv[1] == 'snapshot':
        snapshot(sys.argv[2])
    elif sys.argv[1] == 'reports':
        reports()
    elif sys.argv[1] == 'population':
        population()
    elif sys.argv[1] == 'environment':
        environment()
    elif sys.argv[1] == 'contracts':
        contracts()
