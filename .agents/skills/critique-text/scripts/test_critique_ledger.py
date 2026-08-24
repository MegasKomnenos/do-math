# critique_ledger.py 재현 테스트 (TDD RED -> GREEN)
# 실행: python test_critique_ledger.py  (이 디렉토리에서)
# 픽스처는 실물 문서(보충서면_2026-10986, 심판개요서)의 구조 특성을 보존한 축소 표본이다.
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from critique_ledger import split_units, build_ledger, check_coverage, merge_reports

FAILURES = []


def expect(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        FAILURES.append(name)


def texts(units):
    return [u[1] for u in units]


def test_split_basic():
    units = split_units("이 부분 처분사유는 인정된다. 따라서 적법하다.")
    expect("split_basic", texts(units) == ["이 부분 처분사유는 인정된다.", "따라서 적법하다."], repr(units))


def test_date_periods_no_split():
    units = split_units("2026. 7. 4.")
    expect("date_no_split", texts(units) == ["2026. 7. 4."], repr(units))


def test_date_inside_sentence():
    units = split_units("청구인은 2025. 5. 16. 심판청구를 하였다. 청구기간을 준수하였다.")
    expect(
        "date_inside_sentence",
        texts(units) == ["청구인은 2025. 5. 16. 심판청구를 하였다.", "청구기간을 준수하였다."],
        repr(units),
    )


def test_paren_citation_internal_period():
    line = "판시하였습니다(대법원 2003. 12. 11. 선고 2001두8827 판결. 위 판시는 현행법에 해당합니다). 다음 문장입니다."
    units = split_units(line)
    expect(
        "paren_internal_period",
        len(units) == 2 and units[0][1].endswith("해당합니다).") and units[1][1] == "다음 문장입니다.",
        repr(units),
    )


def test_quote_internal_period():
    line = '제안요청서는 "산출물은 대학교가 소유권을 갖는다. 다만 예외가 있다"라고 정하고 있습니다. 다음 문장입니다.'
    units = split_units(line)
    expect(
        "quote_internal_period",
        len(units) == 2 and units[0][1].endswith("정하고 있습니다.") and units[1][1] == "다음 문장입니다.",
        repr(units),
    )


def test_paren_close_then_period():
    line = "과징금을 부과하였다(이하 '이 사건 처분'이라 한다). 청구인은 취소를 구하였다."
    units = split_units(line)
    expect(
        "paren_close_then_period",
        len(units) == 2 and units[0][1].endswith("한다).") and units[1][1] == "청구인은 취소를 구하였다.",
        repr(units),
    )


def test_heading_label_da_no_split():
    units = split_units("다. 처분기준 제4호 본문과의 관계")
    expect("heading_da", texts(units) == ["다. 처분기준 제4호 본문과의 관계"], repr(units))


def test_heading_label_ga_no_split():
    units = split_units("가. 현지조사 확인서 및 붙임 명단의 증명력")
    expect("heading_ga", texts(units) == ["가. 현지조사 확인서 및 붙임 명단의 증명력"], repr(units))


def test_subitem_reference_no_split():
    units = split_units("이 점은 아래 5.라.항에서 판단한다.")
    expect("subitem_ref", texts(units) == ["이 점은 아래 5.라.항에서 판단한다."], repr(units))


def test_line_without_period():
    units = split_units("중앙행정심판위원회  귀중")
    expect("no_period_line", texts(units) == ["중앙행정심판위원회  귀중"], repr(units))


def test_nominal_endings():
    units = split_units("청구를 기각함. 이유는 다음과 같음.")
    expect("nominal_endings", texts(units) == ["청구를 기각함.", "이유는 다음과 같음."], repr(units))


# 인용·증거 괄호로 끝나는 문장의 경계 (실측 픽스처: 보충서면 S-029·S-072, 심판개요서 S-021)
def test_citation_paren_ending_split():
    line = "판단한 원심을 수긍하였습니다(대법원 2018. 11. 29. 선고 2016두45165 판결). 사인의 영업상 정보라 하더라도 좁게 인정된다는 것입니다."
    units = split_units(line)
    expect(
        "citation_paren_ending_split",
        len(units) == 2 and units[0][1].endswith("판결).") and units[1][1].startswith("사인의"),
        repr(units),
    )


def test_evidence_paren_ending_split():
    line = "업체별 평가점수를 공개하였습니다(을 제4호증). 제안서에 관한 평가의 객관적 결과가 분리되어 공개될 수 있음을 실증한 것입니다."
    units = split_units(line)
    expect(
        "evidence_paren_ending_split",
        len(units) == 2 and units[0][1].endswith("호증).") and units[1][1].startswith("제안서에"),
        repr(units),
    )


def test_law_paren_ending_split():
    line = "처분청인 보건복지부장관이 피청구인 적격을 가진다(같은 법 제17조 제1항). 청구인은 심판청구를 하였다."
    units = split_units(line)
    expect(
        "law_paren_ending_split",
        len(units) == 2 and units[0][1].endswith("제1항).") and units[1][1].startswith("청구인은"),
        repr(units),
    )


def test_noun_before_paren_stays_merged():
    # 괄호 앞이 종결어미가 아니면 경계로 보지 않는다(보수적 병합 유지)
    line = "근거는 제9조 제1항 제7호(법인등의 정당한 이익). 다만 예외가 있다."
    units = split_units(line)
    expect("noun_before_paren_merged", len(units) == 1, repr(units))


DOC = """보 충 서 면

Ⅰ. 답변서 주장의 요지

피청구인은 다음과 같이 주장합니다. 첫째 주장은 이렇습니다.
이 사건 처분은 위법합니다.
"""


def test_build_ledger_file():
    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, "doc.txt")
        ledger = os.path.join(d, "ledger.md")
        with open(target, "w", encoding="utf-8") as f:
            f.write(DOC)
        ids = build_ledger(target, ledger)
        with open(ledger, encoding="utf-8") as f:
            content = f.read()
        ok = (
            ids == ["S-001", "S-002", "S-003", "S-004", "S-005"]
            and "S-001 [행1] 보 충 서 면" in content
            and "S-003 [행5] 피청구인은 다음과 같이 주장합니다." in content
            and "S-004 [행5] 첫째 주장은 이렇습니다." in content
            and "S-005 [행6] 이 사건 처분은 위법합니다." in content
        )
        expect("build_ledger_file", ok, content)


LEDGER = """# 첨삭 장부: doc.txt
- 단위 수: 5

S-001 [행1] 보 충 서 면
S-002 [행3] Ⅰ. 답변서 주장의 요지
S-003 [행5] 피청구인은 다음과 같이 주장합니다.
S-004 [행5] 첫째 주장은 이렇습니다.
S-005 [행6] 이 사건 처분은 위법합니다.
"""

REPORT_OK = """# 첨삭 보고
## 지적 목록
### C-01 S-004
- 지적: 지시어 불명

## 문장 판정표
- S-001~S-003: 통과
- S-004: C-01
- S-005: 통과

## 통계
"""

REPORT_MISSING = REPORT_OK.replace("- S-005: 통과\n", "")
REPORT_UNKNOWN = REPORT_OK.replace("- S-005: 통과", "- S-005~S-009: 통과")


def run_check(report_text):
    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "ledger.md")
        report = os.path.join(d, "report.md")
        with open(ledger, "w", encoding="utf-8") as f:
            f.write(LEDGER)
        with open(report, "w", encoding="utf-8") as f:
            f.write(report_text)
        return check_coverage(ledger, report)


def test_check_all_covered():
    missing, unknown = run_check(REPORT_OK)
    expect("check_all_covered", missing == [] and unknown == [], f"missing={missing} unknown={unknown}")


def test_check_missing():
    missing, unknown = run_check(REPORT_MISSING)
    expect("check_missing", missing == ["S-005"] and unknown == [], f"missing={missing} unknown={unknown}")


def test_check_unknown():
    missing, unknown = run_check(REPORT_UNKNOWN)
    expect(
        "check_unknown",
        missing == [] and unknown == ["S-006", "S-007", "S-008", "S-009"],
        f"missing={missing} unknown={unknown}",
    )


AXIS_A = """# 첨삭 축A 보고

## 지적 목록
### A-01 (S-004)

## 문장 판정표
- S-001~S-003: 통과
- S-004: A-01
- S-005: 통과
"""

AXIS_B = """# 첨삭 축B 보고

## 지적 목록
### B-01 (S-001)

## 문장 판정표
- S-001: B-01
- S-002~S-005: 통과
"""

AXIS_B_CONV = AXIS_B.replace("- S-002~S-005: 통과", "- S-002~S-003: 통과\n- S-004: B-02\n- S-005: 통과")

AXIS_GAP = """# 축 보고 (누락 있음)

## 문장 판정표
- S-001~S-004: 통과
"""


def run_merge(axis_texts):
    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "ledger.md")
        with open(ledger, "w", encoding="utf-8") as f:
            f.write(LEDGER)
        paths = []
        for n, t in enumerate(axis_texts):
            p = os.path.join(d, f"axis{n}.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(t)
            paths.append(p)
        return merge_reports(ledger, paths)


def test_merge_union():
    lines, convergence, errors = run_merge([AXIS_A, AXIS_B])
    expect(
        "merge_union",
        lines == ["- S-001: B-01", "- S-002~S-003: 통과", "- S-004: A-01", "- S-005: 통과"]
        and convergence == [] and errors == [],
        f"lines={lines} conv={convergence} err={errors}",
    )


def test_merge_convergence():
    lines, convergence, errors = run_merge([AXIS_A, AXIS_B_CONV])
    expect(
        "merge_convergence",
        "- S-004: A-01, B-02" in lines and convergence == ["S-004"] and errors == [],
        f"lines={lines} conv={convergence} err={errors}",
    )


def test_merge_gap_detected():
    lines, convergence, errors = run_merge([AXIS_A, AXIS_GAP])
    expect("merge_gap", len(errors) == 1 and "S-005" in errors[0], f"err={errors}")


if __name__ == "__main__":
    for fn in sorted(list(globals().keys())):
        if fn.startswith("test_"):
            globals()[fn]()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILED: {FAILURES}")
        sys.exit(1)
    print("\nALL PASS")
