"""Read-only corpus, Git clean, and official mirror planning evidence."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from run_command import EVIDENCE, ROOT, changed, snapshot, write_json

sys.path.insert(0, str(ROOT / '.claude/skills/writing-skills/scripts'))
import build_skill_mirrors as bsm

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
WRITES = json.loads((RUN / 'phases/004/phase.json').read_bytes())['tasks'][0]['writes']


def allowed(path):
    return any(path.startswith(w) if w.endswith('/') else path == w for w in WRITES)


def git(args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    result.check_returncode()
    return {'argv': ['git', *args], 'exit_code': result.returncode,
            'stdout': result.stdout.decode('utf-8'), 'stderr': result.stderr.decode('utf-8')}


def corpus_audit(label):
    trees = {}
    all_paths = []
    for runtime in ('.claude', '.agents'):
        base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
        files = {p.relative_to(base).as_posix(): p for p in sorted(base.rglob('*')) if p.is_file()}
        manifest = json.loads(files['manifest.json'].read_bytes())
        rows = {rel: {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for rel, p in files.items()}
        references = []
        bindings = []
        for entry in manifest['entries']:
            for field in ('path', 'final_path', 'source_path', 'compiled_path', 'schema_path'):
                if field in entry:
                    references.append({'entry': entry['id'], 'field': field, 'path': entry[field]})
            for pathfield, hashfield in (('path', 'source_sha256'), ('schema_path', 'schema_sha256')):
                if hashfield in entry:
                    bindings.append({'entry': entry['id'], 'field': hashfield,
                                     'path': entry[pathfield], 'expected': entry[hashfield]})
            for recording in entry.get('recordings', []):
                references.append({'entry': entry['id'], 'field': 'recordings', 'path': recording['path']})
                bindings.append({'entry': entry['id'], 'field': 'recordings.sha256',
                                 'path': recording['path'], 'expected': recording['sha256']})
        for binding in bindings:
            binding['actual'] = rows.get(binding['path'], {}).get('sha256')
            binding['matches'] = binding['expected'] == binding['actual']
        trees[runtime] = {'entry_count': len(manifest['entries']), 'file_count': len(files),
                          'bytes': sum(row['bytes'] for row in rows.values()), 'files': rows,
                          'references': references, 'sha_bindings': bindings,
                          'bad_bindings': [row for row in bindings if not row['matches']],
                          'undeclared': sorted(set(files) - {r['path'] for r in references}
                                               - {'manifest.json', '.gitattributes'})}
        all_paths.extend(row['path'] for row in rows.values())
    source = trees['.claude']['files']
    mirror = trees['.agents']['files']
    differences = [p for p in sorted(source.keys() | mirror.keys())
                   if source.get(p, {}).get('sha256') != mirror.get(p, {}).get('sha256')]
    for rel in differences:
        a = (ROOT / source[rel]['path']).read_text(encoding='utf-8').splitlines(keepends=True)
        b = (ROOT / mirror[rel]['path']).read_text(encoding='utf-8').splitlines(keepends=True)
        (EVIDENCE / (label + '-' + Path(rel).name + '.diff')).write_text(
            ''.join(difflib.unified_diff(a, b, fromfile=source[rel]['path'], tofile=mirror[rel]['path'])),
            encoding='utf-8')
    raw = git(['hash-object', '--no-filters', *all_paths])
    clean = git(['hash-object', *all_paths])
    attributes = git(['check-attr', '--all', '--', *all_paths])
    clean_rows = [{'path': p, 'raw_object_id': a, 'clean_object_id': b, 'matches': a == b}
                  for p, a, b in zip(all_paths, raw['stdout'].splitlines(), clean['stdout'].splitlines(), strict=True)]
    result = {'trees': trees, 'byte_differences': differences,
              'git_commands': [raw, clean, attributes], 'git_clean': clean_rows,
              'git_clean_differences': [r for r in clean_rows if not r['matches']]}
    write_json(EVIDENCE / (label + '.json'), result)
    print(json.dumps({'label': label, 'populations': {k: [v['entry_count'], v['file_count'], v['bytes']]
                                                    for k, v in trees.items()},
                      'byte_differences': differences,
                      'bad_bindings': {k: len(v['bad_bindings']) for k, v in trees.items()},
                      'git_clean_differences': result['git_clean_differences']}, ensure_ascii=False))


def plan(label):
    rules = bsm.load_rules(ROOT / '.agents/diff')
    base = bsm.iter_files(ROOT / bsm.BASE_REL)
    overlays = {r: p for r, p in bsm.iter_files(ROOT / '.agents/diff').items() if r not in bsm.RESERVED}
    outputs = {r: bsm.transform(r, p.read_bytes(), rules) for r, p in base.items()}
    outputs.update({r: p.read_bytes() for r, p in overlays.items()})
    current = bsm.iter_files(ROOT / '.agents/skills')
    paths = ['.agents/skills/' + r for r in sorted(outputs.keys() | current.keys())
             if r not in outputs or r not in current or outputs[r] != current[r].read_bytes()]
    manifest_path = ROOT / '.agents/diff/_manifest.json'
    expected_manifest = {'overlays': {r: bsm.sha1(base[r].read_bytes()) for r in sorted(overlays) if r in base}}
    expected_bytes = (json.dumps(expected_manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n').replace('\n', '\r\n').encode('utf-8')
    check_ok, messages = bsm.build_target('.agents', check=True, bless=False)
    result = {'changed': paths, 'outside_writes': [p for p in paths if not allowed(p)],
              'check_ok': check_ok, 'check_messages': messages,
              'overlay_manifest_bytes_unchanged': manifest_path.read_bytes() == expected_bytes,
              'git_status': git(['-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])}
    write_json(EVIDENCE / (label + '.json'), result)
    print(json.dumps({k:v for k,v in result.items() if k != 'git_status'},ensure_ascii=False))
    assert not result['outside_writes'], result['outside_writes']
    assert result['overlay_manifest_bytes_unchanged'], 'Official build would change the overlay manifest'
    assert all('드리프트' in m or '추가 문서' in m for m in messages), messages


if __name__ == '__main__':
    {'corpus': corpus_audit, 'plan': plan}[sys.argv[1]](sys.argv[2])
