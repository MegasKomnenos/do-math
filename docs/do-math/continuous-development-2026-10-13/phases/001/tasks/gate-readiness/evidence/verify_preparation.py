"""Validate this task's proposed paths/options and observed hashes, without executing gates."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path('C:/math')
OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def options(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    return {arg.value for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'add_argument'
            for arg in node.args if isinstance(arg, ast.Constant)
            and isinstance(arg.value, str) and arg.value.startswith('--')}


gate = read('gate-readiness.json')
checks = []
for command in gate['commands']:
    script = ROOT / command['script']
    assert script.is_file(), script
    assert Path(command['executable']).is_file(), command['executable']
    proposed = {arg for arg in command['arguments'] if arg.startswith('--')}
    assert proposed <= options(script), (command['id'], proposed - options(script))
    checks.append({'command': command['id'], 'script_exists': True, 'options_present_in_current_parser': sorted(proposed), 'gate_executed': False})
ordinary = next(row for row in gate['commands'] if row['id'] == 'ordinary')['arguments']
assert ordinary == ['--jobs', '3', '--output', '{new_output_dir}']
t3 = next(row for row in gate['commands'] if row['id'] == 'fresh-t3')['arguments']
assert t3[:3] == ['--tier', 'T3', '--full'] and '--match' not in t3
for row in gate['commands']:
    if row['id'] == 'corpus-replay':
        for name in row['arguments'][:3]:
            assert (ROOT / '.claude/skills/do-math/scripts/tests' / (name.replace('.', '/') + '.py')).is_file()

population = read('population-and-corpus.json')
assert population['shard_count'] == len(population['shards']) == 17
assert all(row['exists'] for shard in population['shards'] for row in shard['files'])
assert not population['eligible_missing_on_disk']
assert not population['eligible_not_in_shards'] and not population['shard_duplicate_files']
assert len(population['eligible_modules']) == sum(n for layer, n in population['layer_counts'].items() if layer in ['1', '2', '3']) == 123
assert len(population['shard_ineligible_files']) == 7
assert population['test_module_counts']['smoke'] == 0
corpus = population['corpus']
assert not corpus['missing_files'] and not corpus['undeclared_files']
assert all(row['main_matches_recorded_hash'] is not False for row in corpus['entries'])
for record in corpus['entries']:
    for item in record['entry'].get('recordings', []):
        assert record['files'][item['path']]['sha256'] == item['sha256']
assert corpus['bytes_without_manifest'] <= 5 * 1024 * 1024

for item in read('historical-reports.json'):
    assert not item['missing_selected'] and not item['unexpected_rows'] and not item['duplicate_rows'], item['path']
    assert item['matches_transition_table_sha256'] is not False
    path = ROOT / item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
assert all(row['exit_code'] == 0 for row in read('environment.json')['versions'])
for item in read('source-contracts.json')['sources']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
before = read('source-before.json')
assert before['baseline_differences'] == []
assert all(row['baseline'] == row['current'] for row in before['source_engine_comparison'])

result = {'result': 'pass', 'scope': 'Static proposal, existing evidence hash/set and local path validation; no do-math tests, imports or live calls.', 'commands': checks, 'checks': ['default full selection preserved', 'fresh T3 full option and no narrowing', 'corpus selected modules exist', '17 shards/130 files cover 123 eligible and 7 ineligible files with no duplicates', 'no smoke test modules', 'corpus bytes and declared hashes', 'historical report selected/result bijections and original hashes', 'seven safe version commands exited 0', 'source excerpts still match current source', '969 canonical baseline hashes unchanged']}
(OUT / 'proposal-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'result': result['result'], 'commands_checked': len(checks), 'checks': result['checks']}, ensure_ascii=False, indent=2))
