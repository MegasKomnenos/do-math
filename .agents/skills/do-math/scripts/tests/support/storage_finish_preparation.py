"""Child interpreter checks on a genuinely imported installation copy."""
import io
import json
import os
from pathlib import Path
import sys
import zipfile


def check(root, mode):
    from do_math import submission, file_io
    from support.provider_probes import ObservedCalls, settle
    from support.storage_files import audit_events
    from support.fakes.clock import FakeClock
    package = root / 'installation/scripts/do_math'
    for module in (submission, file_io):
        assert Path(module.__file__).resolve().parent == package.resolve(), module.__file__
    for name, module in list(sys.modules.items()):
        if name.startswith('do_math.') and getattr(module, '__file__', None):
            assert Path(module.__file__).resolve().is_relative_to(package.resolve()), (name, module.__file__)
    source = package / 'checker.py'
    source.write_bytes(b'edition = 1\n')
    for path in package.rglob('*.py'):
        settle(path)
    submission._support_archive.cache_clear()
    clock = FakeClock()
    if mode == 'contexts':
        contexts = [{'action': {'role': 'maintenance'}, 'snapshot': name} for name in ('first', 'second')]
        with ObservedCalls(zip=zipfile.ZipFile.__init__) as calls:
            for name, context in zip(('left', 'right'), contexts):
                submission.install_tools(root / name, context, {'type': 'object'}, 1024, clock=clock)
        writes = [row for row in calls.captured('zip') if row['mode'] == 'w']
        assert calls.count('zip') == 1, calls.calls
        assert len(writes) == 1, writes
        assert (root / 'left/input/tools/submission-support.zip').read_bytes() == (root / 'right/input/tools/submission-support.zip').read_bytes()
        for name, expected in zip(('left', 'right'), ('first', 'second')):
            assert json.loads((root / name / 'input/submission/context.json').read_bytes())['snapshot'] == expected
        return {'zip_calls': calls.count('zip'), 'compression_count': len(writes), 'contexts': ['first', 'second']}
    submission.install_tools(root / 'first', {'action': {'role': 'maintenance'}}, {}, None, clock=clock)
    with ObservedCalls(hash=file_io.sha256_file, zip=zipfile.ZipFile.__init__) as calls, audit_events('open') as opens:
        submission.install_tools(root / 'again', {'action': {'role': 'maintenance'}}, {}, None, clock=clock)
    assert calls.count('hash') == 0, calls.calls
    assert calls.count('zip') == 0, calls.calls
    assert not [row for row in calls.captured('zip') if row['mode'] == 'w'], calls.calls
    reads = [args for _, args in opens if isinstance(args[0], str)
             and Path(args[0]).resolve().is_relative_to(package.resolve())]
    assert reads == [], reads
    stamp = source.stat()
    source.write_bytes(b'edition = 2\n')
    os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns + 10 ** 9))
    assert source.stat().st_mtime_ns == stamp.st_mtime_ns + 10 ** 9
    submission.install_tools(root / 'second', {'action': {'role': 'maintenance'}}, {}, None, clock=clock)
    first = (root / 'first/input/tools/submission-support.zip').read_bytes()
    assert first == (root / 'again/input/tools/submission-support.zip').read_bytes()
    second = (root / 'second/input/tools/submission-support.zip').read_bytes()
    assert first != second
    with zipfile.ZipFile(io.BytesIO(second)) as archive:
        assert archive.read('do_math/checker.py') == b'edition = 2\n'
    return {'hash_rereads': 0, 'zip_calls': calls.count('zip'), 'code_opens': 0, 'edited_bytes': 'edition = 2\n'}


if __name__ == '__main__':
    # Add the copied product before support, before the first do_math import.
    root = Path(sys.argv[1]).resolve()
    sys.path[:0] = [str(root / 'installation/scripts'), str(Path(__file__).resolve().parents[1])]
    print(json.dumps(check(root, sys.argv[2])))
