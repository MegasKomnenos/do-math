import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))
from do_math.repository import ResearchRepository, new_id

def fixture(root):
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    repo = ResearchRepository(root, new_id('RI'))
    head = repo.initialize({'feature_version': 5, 'title': 'initial'},
                           {'feature_version': 5, 'status': 'initializing'})
    return repo, head

def orphan_reuse():
    with tempfile.TemporaryDirectory() as directory:
        repo, head = fixture(Path(directory))
        _, instance, runtime = repo.load(head)
        original = 'exact 원문\n' * 20000
        instance['title'] = original
        head, instance, runtime = repo.save_with_state(head, instance, runtime)
        instance['title'] = 'temporarily short'
        head, instance, runtime = repo.save_with_state(head, instance, runtime)
        instance['title'] = original
        try:
            repo.save_with_state(head, instance, runtime)
        except ValueError as error:
            assert str(error) == 'existing runtime artifact bundles are immutable', error
            print('CONFIRMED orphan payload reuse rejects valid save:', error)
        else:
            raise AssertionError('Expected current bug was not reproduced')

def artifact_collision():
    with tempfile.TemporaryDirectory() as directory:
        repo, head = fixture(Path(directory))
        _, instance, runtime = repo.load(head)
        instance['title'] = 'new exact 원문\n' * 20000
        candidate = repo.validate_candidate(instance, runtime, head)
        payload_path = next(path for path in candidate['files'] if path.startswith('runtime/artifacts/payload-'))
        head, _, _ = repo.save_with_state(head, instance, runtime, artifacts={payload_path: b'corrupt'})
        assert repo.read(payload_path, head) == b'corrupt'
        try:
            repo.load(head)
        except ValueError as error:
            assert str(error) == 'immutable payload bytes differ', error
            print('CONFIRMED validated save commits unreadable payload:', error)
        else:
            raise AssertionError('Expected current bug was not reproduced')

if __name__ == '__main__':
    orphan_reuse()
    artifact_collision()
