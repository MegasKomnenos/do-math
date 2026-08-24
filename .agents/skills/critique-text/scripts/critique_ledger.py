# 첨삭 장부 도구: 문장 단위 분할·장부 생성·판정표 커버리지 검사·축 판정표 병합
# 사용:
#   python critique_ledger.py build <대상파일> -o <장부파일>
#   python critique_ledger.py check <장부파일> <보고서파일>
#   python critique_ledger.py merge <장부파일> <축보고1> [<축보고2> ...]
# 분할 규칙: 괄호·따옴표 심도 0에서, 종결어미(다·까·함·음·임·됨) 뒤의 마침표 다음이
# 공백·행끝일 때만 문장 경계로 본다. 마침표 앞의 닫는 괄호·따옴표는 균형 그룹 단위로
# 건너뛰고 그 앞 글자로 종결을 판정한다(인용·증거 괄호 종지 "…하였다(대법원 … 판결)." 대응).
# 날짜(2025. 3. 21.)·항목 표지(가. 나.)·인용문 내부 마침표는 경계가 아니다. 경계가 없는
# 행(제목·표지)은 행 전체가 한 단위다. 괄호 앞이 종결어미가 아니면 병합을 유지한다(보수적).
import argparse
import os
import re
import sys

OPENERS = "(「『[{〔"
CLOSERS = ")」』]}〕"
QUOTE_PAIRS = {"“": 1, "”": -1, "‘": 1, "’": -1}  # 굽은 따옴표 " " ' '
TRAILING = CLOSERS + "\"”’'"  # 마침표 앞에서 건너뛸 닫는 기호들
FINALS = set("다까함음임됨")


def split_line(line):
    """한 행을 문장 단위 목록으로 분할한다."""
    units = []
    depth = 0
    quote_depth = 0
    in_straight_dq = False
    start = 0
    for i, ch in enumerate(line):
        if ch == '"':
            in_straight_dq = not in_straight_dq
            continue
        if ch in QUOTE_PAIRS and ch in "“”":
            quote_depth = max(0, quote_depth + QUOTE_PAIRS[ch])
            continue
        if ch in OPENERS:
            depth += 1
            continue
        if ch in CLOSERS:
            depth = max(0, depth - 1)
            continue
        if ch != "." or depth > 0 or quote_depth > 0 or in_straight_dq:
            continue
        if i + 1 < len(line) and not line[i + 1].isspace():
            continue
        j = i - 1
        while j >= start:
            if line[j] in CLOSERS:  # 균형 괄호 그룹을 통째로 건너뛴다
                grp = 1
                k = j - 1
                while k >= start and grp > 0:
                    if line[k] in CLOSERS:
                        grp += 1
                    elif line[k] in OPENERS:
                        grp -= 1
                    k -= 1
                if grp > 0:
                    break  # 짝 없는 닫는 괄호: 건너뛰지 않고 그 자리에서 판정
                j = k
            elif line[j] in "\"”’'":
                j -= 1
            else:
                break
        if j <= start:  # 앞 내용이 없거나 한 글자(항목 표지 '다.' 등)면 경계가 아니다
            continue
        if line[j] not in FINALS:
            continue
        unit = line[start : i + 1].strip()
        if unit:
            units.append(unit)
        start = i + 1
    tail = line[start:].strip()
    if tail:
        units.append(tail)
    return units


def split_units(text):
    """텍스트 전체를 (행번호, 문장) 목록으로 분할한다. 행번호는 1부터."""
    units = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        for unit in split_line(line):
            units.append((lineno, unit))
    return units


def build_ledger(target_path, ledger_path):
    """대상 파일의 장부를 생성하고 단위 ID 목록을 반환한다."""
    with open(target_path, encoding="utf-8") as f:
        text = f.read()
    units = split_units(text)
    if not units:
        raise SystemExit(f"오류: 분할된 단위가 없습니다: {target_path}")
    ids = []
    lines = [
        f"# 첨삭 장부: {target_path}",
        f"- 단위 수: {len(units)}",
        "",
    ]
    for n, (lineno, unit) in enumerate(units, start=1):
        uid = f"S-{n:03d}"
        ids.append(uid)
        lines.append(f"{uid} [행{lineno}] {unit}")
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return ids


LEDGER_ID_RE = re.compile(r"^(S-\d{3,}) ", re.MULTILINE)
COVER_RE = re.compile(r"S-(\d{3,})(?:\s*~\s*S-(\d{3,}))?")


def parse_ledger_ids(ledger_text):
    return [m.group(1) for m in LEDGER_ID_RE.finditer(ledger_text)]


def parse_report_coverage(report_text):
    """보고서의 '## 문장 판정표' 절에서 커버된 ID 집합을 뽑는다."""
    m = re.search(r"^## 문장 판정표\s*$(.*?)(?=^## |\Z)", report_text, re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    covered = set()
    for g1, g2 in COVER_RE.findall(m.group(1)):
        a = int(g1)
        b = int(g2) if g2 else a
        width = max(len(g1), 3)
        for n in range(min(a, b), max(a, b) + 1):
            covered.add(f"S-{n:0{width}d}")
    return covered


def check_coverage(ledger_path, report_path):
    """(누락 ID 목록, 장부에 없는 ID 목록)을 반환한다."""
    with open(ledger_path, encoding="utf-8") as f:
        ledger_ids = parse_ledger_ids(f.read())
    with open(report_path, encoding="utf-8") as f:
        covered = parse_report_coverage(f.read())
    ledger_set = set(ledger_ids)
    missing = [i for i in ledger_ids if i not in covered]
    unknown = sorted(covered - ledger_set)
    return missing, unknown


ANNOT_RE = re.compile(r"^- S-(\d{3,})(?:\s*~\s*S-(\d{3,}))?\s*:\s*(.+?)\s*$", re.MULTILINE)


def parse_report_annotations(report_text):
    """'## 문장 판정표' 절에서 {ID: [지적 ID 목록]}을 뽑는다(통과는 빈 목록)."""
    m = re.search(r"^## 문장 판정표\s*$(.*?)(?=^## |\Z)", report_text, re.MULTILINE | re.DOTALL)
    if not m:
        return {}
    ann = {}
    for g1, g2, verdict in ANNOT_RE.findall(m.group(1)):
        tags = [] if verdict.strip() == "통과" else [t.strip() for t in verdict.split(",") if t.strip()]
        a, b = int(g1), int(g2) if g2 else int(g1)
        width = max(len(g1), 3)
        for n in range(min(a, b), max(a, b) + 1):
            uid = f"S-{n:0{width}d}"
            ann.setdefault(uid, []).extend(tags)
    return ann


def merge_reports(ledger_path, report_paths):
    """축 보고 판정표들을 합집합 병합한다.

    (통합 판정표 행 목록, 수렴 단위 ID 목록, 오류 목록)을 반환한다.
    수렴 = 둘 이상의 축 보고가 지적을 단 단위.
    """
    with open(ledger_path, encoding="utf-8") as f:
        ledger_ids = parse_ledger_ids(f.read())
    merged = {uid: [] for uid in ledger_ids}
    flagged_by = {uid: 0 for uid in ledger_ids}
    errors = []
    for path in report_paths:
        with open(path, encoding="utf-8") as f:
            ann = parse_report_annotations(f.read())
        missing = [uid for uid in ledger_ids if uid not in ann]
        if missing:
            errors.append(f"{os.path.basename(path)}: 판정 누락 {', '.join(missing)}")
        hit = False
        for uid in ledger_ids:
            tags = ann.get(uid, [])
            if tags:
                merged[uid].extend(tags)
                hit = True
        if hit:
            for uid in ledger_ids:
                if ann.get(uid):
                    flagged_by[uid] += 1
    lines = []
    run_start = None  # 연속 통과 구간의 시작 ID
    prev = None

    def flush(last):
        if run_start is None:
            return
        if run_start == last:
            lines.append(f"- {run_start}: 통과")
        else:
            lines.append(f"- {run_start}~{last}: 통과")

    for uid in ledger_ids:
        if merged[uid]:
            flush(prev)
            run_start = None
            lines.append(f"- {uid}: {', '.join(merged[uid])}")
        else:
            if run_start is None:
                run_start = uid
        prev = uid
    flush(prev)
    convergence = [uid for uid in ledger_ids if flagged_by[uid] >= 2]
    return lines, convergence, errors


def main():
    ap = argparse.ArgumentParser(description="첨삭 장부 생성·완전성 검사")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="대상 파일에서 장부 생성")
    b.add_argument("target")
    b.add_argument("-o", "--output", required=True)
    c = sub.add_parser("check", help="보고서 판정표의 장부 커버리지 검사")
    c.add_argument("ledger")
    c.add_argument("report")
    m = sub.add_parser("merge", help="축 보고 판정표들을 통합 판정표로 병합")
    m.add_argument("ledger")
    m.add_argument("reports", nargs="+")
    args = ap.parse_args()

    if args.cmd == "build":
        ids = build_ledger(args.target, args.output)
        print(f"장부 생성: {args.output} (단위 {len(ids)}개, {ids[0]}~{ids[-1]})")
        return 0

    if args.cmd == "merge":
        lines, convergence, errors = merge_reports(args.ledger, args.reports)
        for line in lines:
            print(line)
        if convergence:
            print(f"\n수렴 단위(2축 이상 지적): {', '.join(convergence)}")
        if errors:
            for e in errors:
                print(f"오류: {e}")
            return 1
        return 0

    missing, unknown = check_coverage(args.ledger, args.report)
    if not missing and not unknown:
        print("커버리지 완전: 장부의 전 단위가 판정표에 있습니다.")
        return 0
    if missing:
        print(f"누락 {len(missing)}개: {', '.join(missing)}")
    if unknown:
        print(f"장부에 없는 ID {len(unknown)}개: {', '.join(unknown)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
