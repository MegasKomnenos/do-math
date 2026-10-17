"""Temporary installations and external failures for the trust branch checks."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
from unittest.mock import patch

from do_math import formal


@contextmanager
def checker_files(installed):
    """Filesystem resolution of a relocated, byte-identical checker installation."""
    source = Path(formal.__file__)
    installed.parent.mkdir(parents=True, exist_ok=True)
    installed.write_bytes(source.read_bytes())
    original = Path.resolve
    resolved = original(installed)
    def resolve(path, *args, **kwargs):
        return resolved if path == source else original(path, *args, **kwargs)
    with patch.object(Path, 'resolve', resolve):
        yield installed


def setup_main(argv, **options):
    """Capture the actual command's single JSON result, stderr and exit status."""
    import setup_lean
    stdout, stderr = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            setup_lean.main(argv, **options)
        except SystemExit as error:
            code = error.code
    return code, json.loads(stdout.getvalue()), stderr.getvalue()


class UnavailableJobs:
    """The external Job service refuses launch; no compiler result is fabricated."""
    def launch(self, *args, **kwargs):
        raise OSError('owned test Job service unavailable')
