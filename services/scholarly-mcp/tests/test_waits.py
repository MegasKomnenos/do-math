import ast, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SKIP = {"waits.py"}
DEFAULTS = {"set_default_timeout", "set_default_navigation_timeout"}


def adapter_sources():
    for path in sorted(ROOT.glob("*.py")):
        if path.name not in SKIP:
            yield path


def numeric_waits(path):
    """timeout 인자와 기본 대기 설정 안에 숫자가 그대로 박힌 자리를 찾는다.

    page.wait_for_timeout(...)은 의도적인 일시 정지이므로 대기 한도가 아니다.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        values = [keyword.value for keyword in node.keywords if keyword.arg == "timeout"]
        if name in DEFAULTS:
            values += list(node.args)
        if name == "Timeout":
            # httpx.Timeout(90, connect=20)처럼 생성자에 박힌 한도도 같은 결함이다. timeout= 인자만 보던 검사가 EuDML의 90초·120초를 놓쳤다.
            values += list(node.args) + [keyword.value for keyword in node.keywords]
        for value in values:
            for inner in ast.walk(value):
                if isinstance(inner, ast.Constant) and isinstance(inner.value, (int, float)):
                    found.append(f"{path.name}:{inner.lineno}:{inner.value}")
    return found


class Waits(unittest.TestCase):
    def test_source_wait_is_five_minutes_and_overridable(self):
        import waits
        self.assertEqual(waits.SOURCE_WAIT_MS, 300000)
        self.assertEqual(waits.SOURCE_WAIT_S, 300)
        self.assertLess(waits.PROBE_WAIT_MS, waits.SOURCE_WAIT_MS)
        self.assertEqual(waits.wait_ms("SCHOLARLY_SOURCE_WAIT_MS", 300000, {"SCHOLARLY_SOURCE_WAIT_MS": "90000"}), 90000)
        self.assertEqual(waits.wait_ms("SCHOLARLY_SOURCE_WAIT_MS", 300000, {"SCHOLARLY_SOURCE_WAIT_MS": "nan"}), 300000)

    def test_no_wait_limit_is_written_as_a_number(self):
        offenders = [item for path in adapter_sources() for item in numeric_waits(path)]
        self.assertEqual(offenders, [], "wait limits must come from waits.py")
