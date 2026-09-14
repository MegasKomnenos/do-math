"""Check imported sources and published n <= 9 data; no new research range.

Run from the repository root:
  python research/problem-selection-2026-09-15/verify_reference.py
The report is written beside the source catalog. Missing local PDFs fail explicitly.
"""

import hashlib
import json
from datetime import datetime, timezone
from functools import cache
from itertools import product
from math import comb
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


@cache
def cumulative(n, bound):
    """S2, Theorem 3.7: last car splits the street into two parts."""
    if n == 0:
        return 1
    return sum(
        comb(n - 1, left) * min(left + 1, bound + 1)
        * cumulative(left, bound) * cumulative(n - 1 - left, bound)
        for left in range(n)
    )


def parking_spots(preferences):
    occupied = set()
    spots = []
    n = len(preferences)
    for preferred in preferences:
        spot = next((j for j in range(preferred, n + 1) if j not in occupied), None)
        if spot is None:
            return None
        occupied.add(spot)
        spots.append(spot)
    return spots


def direct_row(n):
    counts = [0] * n
    for preferences in product(range(1, n + 1), repeat=n):
        spots = parking_spots(preferences)
        if spots is not None:
            counts[max(s - a for s, a in zip(spots, preferences))] += 1
    return counts


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks, errors = [], []

    def check(name, passed, **detail):
        checks.append({"name": name, "passed": bool(passed), **detail})
        if not passed:
            errors.append(name)

    catalog = json.loads((BASE / "evidence/source-catalog.json").read_text(encoding="utf-8"))
    for source in catalog["sources"]:
        path = BASE / source["file"]
        check(source["id"] + " original hash", path.exists() and sha256(path) == source["artifact"]["sha256"])
        manifest = ROOT / source["manifest"]
        check(source["id"] + " MCP manifest hash", manifest.exists() and sha256(manifest) == source["artifact"]["ref"].rsplit("/", 1)[1])

    data = json.loads((BASE / "evidence/published-counts.json").read_text(encoding="utf-8"))
    for key, expected in data["rows"].items():
        n = int(key)
        if not 1 <= n <= 9 or len(expected) != n:
            raise ValueError("Only the published 1 <= n <= 9 range is allowed")
        values = [cumulative(n, bound) for bound in range(n)]
        actual = [value - (values[k - 1] if k else 0) for k, value in enumerate(values)]
        check(f"published row n={n}", actual == expected, actual=actual)
        check(f"total n={n}", sum(actual) == (n + 1) ** (n - 1))
        if n <= 5:
            direct = direct_row(n)
            check(f"independent parking enumeration n={n}", direct == expected, actual=direct)

    # Published examples distinguish order-sensitive maximum from invariant total.
    displacements = {}
    for word in [(1, 1, 2), (1, 2, 1)]:
        spots = parking_spots(word)
        displacements[str(word)] = [s - a for s, a in zip(spots, word)]
    check("sorting changes maximum", displacements == {"(1, 1, 2)": [0, 1, 1], "(1, 2, 1)": [0, 0, 2]})
    # This is a check of a source-side boundary claim, not a conjecture refutation.
    check("n=2 boundary sentence is false", data["rows"]["2"][0] > data["rows"]["2"][1])
    check("n=3 counting polynomial is not real-rooted", 7 * 7 - 4 * 6 * 3 == -23)

    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "scope": "Source bytes; S1 published table n=1..9 via S2 recurrence; direct enumeration n=1..5; interpretation boundaries. No n>9 computation, new proof, Lean run or do-math instance.",
        "check_count": len(checks), "errors": errors, "checks": checks,
    }
    (BASE / "evidence/reference-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "check_count", "errors", "scope"]}, ensure_ascii=False))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
