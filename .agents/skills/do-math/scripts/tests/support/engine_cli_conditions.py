"""External storage fault and public setup calls for the conditional CLI journey."""
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import json
import sys

import setup_lean
from do_math.engine import ResearchEngine


def setup_call(sim, *arguments):
    """Keep setup's JSON and actual exit, including its documented refusal exits."""
    output = StringIO()
    code = 0
    with redirect_stdout(output):
        try:
            setup_lean.main(list(map(str, arguments)), ports=sim.ports, environment=sim.environment)
        except SystemExit as exited:
            code = exited.code
    return code, json.loads(output.getvalue())


@contextmanager
def native_capture_refused(sim):
    """Refuse one Git publication at native capture; the provider and owner run normally."""
    backend = sim.ports.git_backend
    original = backend.update_ref
    refused = []

    def update_ref(repository, ref, new, old):
        frame = sys._getframe(1)
        while frame is not None:
            if frame.f_code is ResearchEngine._capture_native_submission.__code__ and not refused:
                refused.append({'new': new, 'old': old})
                raise OSError('fixture: native capture publication unavailable')
            frame = frame.f_back
        return original(repository, ref, new, old)

    backend.update_ref = update_ref
    try:
        yield refused
    finally:
        del backend.update_ref
