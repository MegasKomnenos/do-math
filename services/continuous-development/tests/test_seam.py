import os
import subprocess
import sys
import unittest

from support import ENGINE


class ExecutableSeamTests(unittest.TestCase):
    def test_shared_definition_catches_call_and_result_mismatches(self):
        project = ENGINE / "examples/linecount/project"
        source = '''
from collections import Counter
from linecount.contracts import LineCounts
from contract_checks.s1 import assert_provider, make_consumer_stub, assert_consumed_text

def good(text: str) -> LineCounts:
    return dict(Counter(line for line in text.replace("\\r\\n", "\\n").replace("\\r", "\\n").split("\\n") if line))

assert_provider(good)

def renamed(content: str) -> LineCounts:
    return good(content)

def wrapped(text: str) -> LineCounts:
    return {"counts": good(text)}

def bool_counts(text: str) -> LineCounts:
    return {key: bool(value) for key, value in good(text).items()}

for bad in (renamed, wrapped, bool_counts):
    try:
        assert_provider(bad)
    except (AssertionError, TypeError):
        pass
    else:
        raise AssertionError(f"mismatch accepted: {bad.__name__}")

stub = make_consumer_stub({"x": 1})
try:
    stub(content="x")
except TypeError:
    pass
else:
    raise AssertionError("consumer's wrong keyword accepted")
if stub(text="x") != {"x": 1}:
    raise AssertionError("consumer stub result mismatch")
assert_consumed_text(stub, "x")
try:
    assert_consumed_text(stub, "other")
except AssertionError:
    pass
else:
    raise AssertionError("changed consumer input accepted")
print("PASS executable seam mismatches")
'''
        env = dict(os.environ, PYTHONPATH=str(project / "src"))
        for flags in ([], ["-O"]):
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, *flags, "-c", source], cwd=project, env=env, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
                self.assertIn(b"PASS executable seam mismatches", result.stdout)


if __name__ == "__main__":
    unittest.main()
