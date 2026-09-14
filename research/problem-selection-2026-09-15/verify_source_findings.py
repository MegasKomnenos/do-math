"""Reproduce small counterexamples to printed source statements, not to problem P."""
import json
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path

BASE = Path(__file__).resolve().parent


def park(preferences, spots):
    occupied, result = set(), []
    for a in preferences:
        place = next((j for j in range(a, spots + 1) if j not in occupied), None)
        if place is None:
            return None
        occupied.add(place)
        result.append(place)
    return result


def increasing_lists(n, m, bound):
    result = []
    for word in combinations_with_replacement(range(1, m + 1), n):
        positions = park(word, m)
        if positions is not None and all(s - a <= bound for s, a in zip(positions, word)):
            result.append(word)
    return result


def main():
    findings = []
    # S1 Eq. (6), q=t=1, printed product upper bound ell=1.
    lhs = sum(1 for w in [(1, 1), (1, 2), (2, 1)] if park(w, 2) is not None)
    rhs = sum(1 for _ in permutations([1, 2]))
    assert (lhs, rhs) == (3, 2)
    findings.append({"id": "S1-E6", "source_page": 6, "input": {"n": 2, "ell": 1, "q": 1, "t": 1}, "left": lhs, "printed_right": rhs})

    # Permanent car labels are kept when C3 moves in front of C1.
    before = dict(zip([1, 2, 3], park([2, 1, 1], 3)))
    after = dict(zip([3, 1, 2], park([1, 2, 1], 3)))
    assert before[1] == after[1] and before != after
    findings.append({"id": "S1-L5.6", "source_page": 17, "j": 1, "k": 3, "before_by_car": before, "after_by_car": after})

    words = increasing_lists(2, 3, 1)
    # m-n=1, so the printed product has only the block before the sole empty spot z.
    printed = sum(len(increasing_lists(z - 1, z - 1, 1)) for z in [1, 2, 3])
    assert len(words) == 5 and printed == 4
    findings.append({"id": "S2-T4.1", "source_pages": [10, 11], "n": 2, "m": 3, "ell": 1, "actual_lists": words, "printed_right": printed})

    # S2 Eq. (9): k=ell+1=2; [t^2](1-t)/(1-2t)=2, independent of n.
    words = increasing_lists(3, 3, 1)
    printed_coefficient = 2 ** 2 - 2 ** 1
    assert len(words) == 4 and printed_coefficient == 2
    findings.append({"id": "S2-E9", "source_page": 14, "n": 3, "ell": 1, "actual_lists": words, "printed_coefficient": printed_coefficient})

    words = increasing_lists(1, 2, 0)
    literal, slope_corrected = [], []
    for north in combinations(range(3), 1):
        x = y = 0
        on_literal = on_corrected = True
        height = 0
        steps = []
        for i in range(3):
            if i in north:
                y += 1
                steps.append("N")
            else:
                x += 1
                steps.append("E")
            on_literal &= y >= 2 * x
            on_corrected &= 2 * y >= x
            height = max(height, y - x)
        if on_literal and height <= 1:
            literal.append("".join(steps))
        if on_corrected and height <= 1:
            slope_corrected.append("".join(steps))
    assert len(words) == 2 and literal == [] and slope_corrected == ["NEE"]
    findings.append({"id": "S2-T4.14", "source_pages": [14, 15], "n": 1, "m": 2, "ell": 0, "actual_lists": words, "printed_slope_paths": literal, "corrected_slope_paths": slope_corrected})

    report = {"status": "CONFIRMED", "scope": "Five printed source claims checked on specified finite examples. These are not counterexamples to the selected unimodality conjecture P.", "findings": findings}
    (BASE / "evidence/source-findings.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "confirmed_findings": len(findings)}))


if __name__ == "__main__":
    main()
