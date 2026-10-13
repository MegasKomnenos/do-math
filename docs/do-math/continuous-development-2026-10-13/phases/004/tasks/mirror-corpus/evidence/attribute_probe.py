"""Observe path spelling and the permitted parent's inability to override a child."""
import hashlib
from pathlib import Path

from audit import git
from run_command import EVIDENCE, ROOT, write_json

paths = ['.claude/skills/do-math/scripts/tests/corpus/' + rel for rel in (
    'manifest.json', 'lean/lean-nat-add-zero-beq.lean', 'scheduler/absent-tasks.json')]
observations = []
for path in paths:
    variants = {'relative_posix': path, 'absolute_windows': str(ROOT / path),
                'absolute_posix': (ROOT / path).as_posix()}
    for spelling, argument in variants.items():
        raw = git(['hash-object', '--no-filters', argument])
        clean = git(['hash-object', argument])
        observations.append({'path': path, 'spelling': spelling, 'raw': raw, 'clean': clean,
                             'matches': raw['stdout'] == clean['stdout']})

parent = ROOT / '.claude/skills/do-math/.gitattributes'
original = parent.read_bytes()
trial = original + b'\n# Corpus-only trial in the authorized parent.\nscripts/tests/corpus/** -text -eol\n'
trial_results = {}
try:
    parent.write_bytes(trial)
    trial_results['parent_content'] = trial.decode('utf-8')
    trial_results['attributes'] = git(['check-attr', '--all', '--', *paths])
    trial_results['raw'] = git(['hash-object', '--no-filters', *paths])
    trial_results['clean'] = git(['hash-object', *paths])
finally:
    parent.write_bytes(original)

result = {'git_version': git(['--version']), 'path_spelling_observations': observations,
          'permitted_parent_trial': trial_results,
          'parent_original_sha256': hashlib.sha256(original).hexdigest(),
          'parent_restored_sha256': hashlib.sha256(parent.read_bytes()).hexdigest(),
          'child_path': '.claude/skills/do-math/scripts/tests/corpus/.gitattributes',
          'child_content': (ROOT / '.claude/skills/do-math/scripts/tests/corpus/.gitattributes').read_text(encoding='utf-8')}
write_json(EVIDENCE / 'attribute-probe.json', result)
assert result['parent_original_sha256'] == result['parent_restored_sha256']
assert trial_results['raw']['stdout'].splitlines()[0] != trial_results['clean']['stdout'].splitlines()[0]
print('Manifest still changes under the corpus-only parent rule; original parent bytes restored.')
print('Path spelling matches:', [(r['path'],r['spelling'],r['matches']) for r in observations])
