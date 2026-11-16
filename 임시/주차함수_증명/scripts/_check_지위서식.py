# -*- coding: utf-8 -*-
"""진술 머리의 지위 표지 서식 검사(세션 결정 51·60·62).

- 「X에 의존」: 「과」 금지, 같은 유형 낱말의 되풀이(「정리 A·정리 B」) 금지, X는 라벨 `{{N:…}}`.
- 「계산 증거(…)」·「계산 보조(…)」 괄호 안: 네 등급 이름(쉼표 나열)만. 쌍반점·범위 문구 금지.
- 「(가)는 증명됨, (나)는 증명됨」처럼 같은 지위를 나누어 적은 꼴 경고.
대상: 장v2/장*.md(부록 D 조각 제외). 출력: 파일:행 | 머리 앞부분 | 문제.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP = os.path.join(ROOT, "장v2")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\{\{\d+:[A-Za-z0-9\-]+\}\})(.*?)\[(.*?)\]\.\*\*")
GRADES = ("정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석")
GRADE_EVAL = re.compile(r"^(배정밀도|\d+ ?자리) 평가$")
TYPES = "정의|정리|명제|보조정리|따름정리"


def check_grades(par):
    items = [x.strip() for x in par.split(",")]
    bad = []
    i = 0
    while i < len(items):
        it = items[i]
        if it in GRADES or GRADE_EVAL.match(it):
            i += 1
            continue
        bad.append(it)
        i += 1
    return bad


def main():
    problems = []
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md"))):
        name = os.path.basename(p)
        for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
            m = HEAD.match(ln)
            if not m:
                continue
            kind, lab, _, status = m.groups()
            where = f"{name}:{no} {kind} {lab}"
            # 괄호 안 등급
            for par in re.findall(r"계산 (?:증거|보조)\(([^)]*)\)", status):
                if ";" in par:
                    problems.append((where, f"괄호 안 쌍반점: ({par})"))
                else:
                    bad = check_grades(par)
                    if bad:
                        problems.append((where, f"괄호 안 등급 아닌 문구: {bad}"))
            if re.search(r"계산 증거(?!\()", status):
                problems.append((where, "「계산 증거」에 등급 괄호 없음"))
            # 의존 목록
            for dep in re.findall(r"((?:[^,\[\];]*?)에 의존)", status):
                body = dep[: -len("에 의존")]
                if "과 " in body or body.endswith("과"):
                    problems.append((where, f"의존 목록에 「과」: {dep}"))
                types = re.findall(TYPES, body)
                for a, b in zip(types, types[1:]):
                    if a == b:
                        problems.append((where, f"의존 목록에 유형 낱말 되풀이: {dep}"))
                        break
                if "{{" not in body and re.search(r"\d+\.\d+", body):
                    problems.append((where, f"의존 목록이 라벨이 아닌 번호: {dep}"))
            # 같은 지위를 나누어 적음
            parts = re.findall(r"\([가-힣]\)(?:\([가-힣]\))*는 (증명됨|계산 증거)", status)
            if len(parts) >= 2 and len(set(parts)) == 1:
                problems.append((where, f"같은 지위를 나누어 적음: [{status[:80]}]"))
    for w, msg in problems:
        print(w, "|", msg)
    print(f"문제 {len(problems)}건")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
