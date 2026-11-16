# -*- coding: utf-8 -*-
"""원고.md의 불변식 검사.

사용: python 불변식.py [원고 경로] [--장부 장부_기호용어이름.md]
검사(합의 8절 완료 조건 2와 장부 6절):
  1. 번호 붙은 진술의 지위 표지(쌍반점 하나로 지위; 식별자)와 식별자 꼴(r+7자리 16진수); 머리 괄호의 기록 이름에는 식별자가 함께 있음.
  2. 본문이 인용한 식별자 집합 = 부록 B의 식별자 집합.
  3. 장별 번호의 연속(1부터 끊김 없이).
  4. "정리 x.y" 꼴 참조가 정의된 번호를 가리킴.
  5. 구분자 균형: 각 문단의 $ 개수 짝수, 중괄호·대괄호·소괄호 균형(수식 안 \\{ \\} 포함).
  6. 금지어(결정 8): 마디, 뿌리 문제, 뿌리 명제, 공표, 판 \\d+; 9장·부록 밖의 노드·프런티어·생산자·peer.
  7. 「걸음」 출현 목록(세션이 뜻을 판정).
  8. 「보행」이 처음 나오는 줄 앞에 「확률보행」이 있음.
  9. 부록 C(용어 대응표)가 본문의 「기록은 이를 … 부른다」 자리를 담음(낱말 포함 검사).
실패가 있으면 종료 코드 1. 7번은 목록만 내고 실패로 세지 않는다.
"""
import io
import os
import re
import sys

STATUS_WORDS = ["증명됨", "비형식 증명", "계산 증거", "형식 증명", "추측", "발견적"]
MODIFIERS = ["계산 보조", "시작점 비명시", "작성자 판단"]
LAYER_WORDS = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "인증 아님"]  # 넷째 갈래는 「<정밀도> 평가, 인증 아님」
STMT_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\d+)\.(\d+)(?: \(((?:[^()]|\([^()]*\))*)\))?(?: \[([^\]]*)\])?\.?\*\*")  # 이름 괄호는 한 단계 중첩 허용
ID_RE_BRACKET = re.compile(r"\[([^\]]*)\]")  # 대괄호 안의 모든 식별자(지위 표지의 쌍반점 뒤 포함)
ID_TOKEN_RE = re.compile(r"(?<![0-9a-zA-Z])r[0-9a-f]{7}(?![0-9a-zA-Z])")


def find_ids(line):
    out = []
    for m in ID_RE_BRACKET.finditer(line):
        out.extend(t for t in ID_TOKEN_RE.findall(m.group(1)))
    return out
ANY_ID_RE = re.compile(r"\[(r[0-9a-fA-F]{6,})")
REF_RE = re.compile(r"(정의|정리|명제|보조정리|따름정리) (\d+)\.(\d+)")
FORBIDDEN_ALL = [r"마디", r"뿌리 문제", r"뿌리 명제", r"공표", r"판 \d+"]
FORBIDDEN_BODY = [r"노드", r"프런티어", r"생산자", r"peer"]


def chapter_of(line_no, chapter_starts):
    ch = 0
    for start, num in chapter_starts:
        if line_no >= start:
            ch = num
    return ch


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    path = args[0] if args else os.path.join(root, "원고.md")
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    failures = []
    notes = []

    # 장 경계
    chapter_starts = []  # (line index 1-based, chapter number or 100+appendix)
    appendix_start = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^## (\d+)\.", ln)
        if m:
            chapter_starts.append((i, int(m.group(1))))
        elif re.match(r"^## 부록 ([ABC])", ln):
            if appendix_start is None:
                appendix_start = i
            chapter_starts.append((i, 100 + "ABC".index(re.match(r"^## 부록 ([ABC])", ln).group(1))))

    # 0. 제어 문자
    for i, ln in enumerate(lines, 1):
        bad = [c for c in ln if ord(c) < 32 and c not in "	"]
        if bad:
            failures.append(f"{i}: 제어 문자 {['U+%04X' % ord(c) for c in bad]}")

    # 1. 진술 머리
    defined = set()
    per_chapter = {}
    for i, ln in enumerate(lines, 1):
        m = STMT_RE.match(ln)
        if not m:
            continue
        kind, ch, num, name, bracket = m.groups()
        key = (int(ch), int(num))
        if key in defined:
            failures.append(f"{i}: 번호 중복 {kind} {ch}.{num}")
        defined.add(key)
        per_chapter.setdefault(int(ch), []).append(int(num))
        if name and "기록" in name and not re.search(r"\[r[0-9a-f]{7}\]", name):
            failures.append(f"{i}: 머리 괄호의 기록 이름에 식별자 없음 ({name})")
        if bracket is None:
            if kind != "정의":
                failures.append(f"{i}: 지위 표지 없음: {kind} {ch}.{num}")
            continue
        if kind == "정의" and ";" not in bracket:
            status_part, ids_part = "", bracket.strip()  # 정의의 대괄호는 출처 식별자만 적는다
        else:
            outside = bracket
            for _ in range(3):
                outside = re.sub(r"\([^()]*\)", "", outside)  # 괄호 안(계산 증거(범위; 층) 등)의 쌍반점은 세지 않는다
            if outside.count(";") != 1:
                failures.append(f"{i}: 지위 표지의 괄호 밖 쌍반점은 하나(지위; 식별자)여야 함 [{bracket}]")
            status_part, _, ids_part = bracket.rpartition(";")
            status_part = status_part.strip()
            ids_part = ids_part.strip()
        if kind != "정의":
            if not any(w in status_part for w in STATUS_WORDS):
                failures.append(f"{i}: 지위 낱말 없음 [{bracket}]")
            extra = status_part
            for w in STATUS_WORDS + MODIFIERS:
                extra = extra.replace(w, "")
            extra = re.sub(r"[,，·\s은는이가의와과에서도만\(\)]+|항등식|부등식|대응|극한 진술|문헌의 정리에 기댄|앞 두 문장|셋째 문장|문장|부분|입력|의존|중앙 증가에|각 입력의 지위는 괄호|binary64 상자 검사|네 적분의 배정밀도 위합|정리 \d+\.\d+에 기댄|n\\le\d+의|n\\ge N_0의|\$[^$]*\$", "", extra)
            if extra.strip():
                notes.append(f"{i}: 지위 표지에 낯선 낱말: '{extra.strip()}' ([{bracket}])")
            # 층 이름: 계산 보조(…)·계산 증거(…)의 괄호는 네 갈래 이름 가운데 하나를 담아야 한다
            for m2 in re.finditer(r"계산 (보조|증거)(\(([^()]*(?:\([^()]*\))?[^()]*)\))?", status_part):
                inner = m2.group(3) or ""
                if m2.group(1) == "보조" and not inner:
                    failures.append(f"{i}: 「계산 보조」에 층 괄호가 없음 [{bracket}]")
                    continue
                if inner and not any(w in inner for w in LAYER_WORDS):
                    failures.append(f"{i}: 계산 {m2.group(1)}의 괄호에 네 갈래 층 이름이 없음 '({inner})' [{bracket}]")
            if re.search(r"(?<!비형식 )증명됨", status_part) and "계산 보조" in status_part and "비형식 증명" not in status_part:  # 부분 지정에서 계산 보조가 비형식 증명 쪽에 붙은 꼴은 허용
                failures.append(f"{i}: 「증명됨」과 「계산 보조」를 함께 둘 수 없음(계산에 기댄 부분은 비형식 증명 또는 계산 증거) [{bracket}]")
        if kind != "정의" and not ids_part:
            failures.append(f"{i}: 식별자 없음(정리·명제·보조정리·따름정리는 식별자 또는 「표준」이 필요) [{bracket}]")
        for tok in re.split(r"[,\s]+", ids_part):
            if not tok or tok == "표준":
                continue
            if not re.fullmatch(r"r[0-9a-f]{7}", tok):
                failures.append(f"{i}: 식별자 꼴 이상 '{tok}' in [{bracket}]")

    # 3. 번호 연속
    for ch, nums in sorted(per_chapter.items()):
        nums_sorted = sorted(nums)
        expected = list(range(1, len(nums_sorted) + 1))
        if nums_sorted != expected:
            failures.append(f"장 {ch}: 번호 불연속 {nums_sorted}")

    # 4. 참조 해소
    for i, ln in enumerate(lines, 1):
        if STMT_RE.match(ln):
            continue
        for m in REF_RE.finditer(ln):
            key = (int(m.group(2)), int(m.group(3)))
            if key not in defined:
                failures.append(f"{i}: 정의되지 않은 번호 참조 {m.group(0)}")

    # 2. 식별자 집합 = 부록 B
    body_ids = set()
    appendix_b_ids = set()
    in_b = False
    for i, ln in enumerate(lines, 1):
        if re.match(r"^## 부록 B", ln):
            in_b = True
        elif re.match(r"^## 부록 [AC]", ln) or (re.match(r"^## ", ln) and in_b and not ln.startswith("## 부록 B")):
            in_b = False
        ids = find_ids(ln)
        if in_b:
            appendix_b_ids.update(ids)
            appendix_b_ids.update(re.findall(r"^\|\s*(r[0-9a-f]{7})\s*\|", ln, re.M))
        else:
            body_ids.update(ids)
        for m in ANY_ID_RE.finditer(ln):
            tok = m.group(1)
            if not re.fullmatch(r"r[0-9a-f]{7}", tok):
                failures.append(f"{i}: 식별자 꼴 이상 '[{tok}'")
    if appendix_b_ids or body_ids:
        only_body = sorted(body_ids - appendix_b_ids)
        only_b = sorted(appendix_b_ids - body_ids)
        if only_body:
            failures.append("부록 B에 없는 본문 식별자: " + ", ".join(only_body))
        if only_b:
            failures.append("본문에 없는 부록 B 식별자: " + ", ".join(only_b))

    # 5. 구분자 균형(문단 단위)
    para = []
    para_start = 1
    def check_para(pl, start):
        s = "\n".join(pl)
        if s.strip() == "" or s.lstrip().startswith("|"):
            return
        if s.count("$") % 2 == 1:
            failures.append(f"{start}: 문단의 $ 개수 홀수")
        if s.count("{") != s.count("}"):
            failures.append(f"{start}: 문단의 중괄호 불균형 ({s.count('{')} vs {s.count('}')})")
        for o, c in ["()", "[]"]:
            if s.count(o) != s.count(c):
                notes.append(f"{start}: 문단의 {o}{c} 개수 차이 ({s.count(o)} vs {s.count(c)}; 반열린 구간이면 정상)")
    for i, ln in enumerate(lines, 1):
        if ln.strip() == "":
            check_para(para, para_start)
            para = []
            para_start = i + 1
        else:
            para.append(ln)
    check_para(para, para_start)

    # 6. 금지어
    for i, ln in enumerate(lines, 1):
        ch = chapter_of(i, chapter_starts)
        for pat in FORBIDDEN_ALL:
            for m in re.finditer(pat, ln):
                ctx = ln[max(0, m.start() - 15): m.end() + 15]
                if pat == "공표" and "기록" in ctx and "부른다" in ctx:
                    continue
                if ch == 9 or ch >= 100:
                    notes.append(f"{i}(9장/부록): 금지어 '{m.group(0)}' … {ctx}")
                else:
                    failures.append(f"{i}: 금지어 '{m.group(0)}' … {ctx}")
        if ch != 9 and ch < 100:
            for pat in FORBIDDEN_BODY:
                for m in re.finditer(pat, ln):
                    ctx = ln[max(0, m.start() - 15): m.end() + 15]
                    if "부른다" in ctx or "기록은" in ctx:
                        notes.append(f"{i}: 운영 어휘 언급(허용 문맥 확인) '{m.group(0)}' … {ctx}")
                    else:
                        failures.append(f"{i}: 9장 밖 운영 어휘 '{m.group(0)}' … {ctx}")

    # 7. 걸음 목록, 8. 보행
    first_bohaeng = None
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r"걸음", ln):
            ctx = ln[max(0, m.start() - 12): m.end() + 12]
            notes.append(f"{i}: 걸음 … {ctx}")
        if first_bohaeng is None and "보행" in ln:
            first_bohaeng = i
    if first_bohaeng is not None:
        before = "\n".join(lines[:first_bohaeng])
        if "확률보행" not in before:
            failures.append(f"{first_bohaeng}: 「보행」 첫 출현 앞에 「확률보행」 정의가 없음")

    # 9. 부록 C가 「기록은 이를 … 부른다」 자리를 담음
    c_text = ""
    for i, ln in enumerate(lines, 1):
        ch = chapter_of(i, chapter_starts)
        if ch == 102:
            c_text += ln + "\n"
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r"기록(?:은|이|에서는|들은)?(?: 이를| 이것을| 이 양을| 이 사건을)? ([^\s,.()]+)(?:라|이라)고? 부른다", ln):
            word = m.group(1)
            if c_text and word not in c_text:
                failures.append(f"{i}: 부록 C에 없는 기록 용어 '{word}'")

    print(f"검사 대상: {path} ({len(lines)} lines)")
    print(f"번호 붙은 진술: {len(defined)}; 인용 식별자: {len(body_ids)}; 부록 B: {len(appendix_b_ids)}")
    if notes:
        print("\n[참고 목록]")
        for n in notes:
            print(" ", n)
    if failures:
        print(f"\n[실패 {len(failures)}건]")
        for f in failures:
            print(" ", f)
        return 1
    print("\n불변식 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
