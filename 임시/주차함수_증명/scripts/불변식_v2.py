# -*- coding: utf-8 -*-
"""둘째 판 원고.md의 불변식 검사(합의 v2 8절 완료 판정 2·3, 지침 v2 4·6·7절).

사용: python 불변식_v2.py [원고 경로]
실패(종료 코드 1):
  1. 진술 머리의 지위 표지 문법(쌍반점 하나; 다섯 낱말 가운데 증명됨·비형식 증명·계산 증거만 허용; 덧붙임 계산 보조(층)·작성자 판단·시작점 비명시·…에 의존; 층 이름 네 갈래), 식별자 꼴(r+7자리), 기록 이름 괄호의 식별자.
  2. 본문·부록 D가 인용한 식별자 집합 = 부록 B의 식별자 집합.
  3. 장별 번호의 연속, 참조된 번호의 존재.
  4. 구분자 균형($ 짝수, 중괄호).
  5. 금지어: 마디, 뿌리 문제, 뿌리 명제, 공표, 판 N(전체); 11장·부록 밖의 노드·프런티어·생산자·peer·검토·세션·인스턴스.
  6. 구별 문장(…와 다른 양/기호/뜻/결과/명제, 구별한다/구별된다), 기록 표기 문장(기록은 …로 적는다/부른다), 앞당김(이름은 …절에서 정한다), 정정 이력(검토가 … 고쳤다/정정했다), 「계산의 층과 범위」, 언급 금지 꼴(다루지 않는다, 옮기지 않는다, 싣지 않는다, 생략한다, 출처만, 기록을 보라, 않기로 했다, 사슬 밖).
  7. 남은 라벨·임시 기호({{…}}), 「부록 D.n」 참조가 실제 항목을 가리킴.
  8. 「보행」 첫 출현 앞에 「확률보행」.
참고 목록(실패 아님): 걸음 출현, 기록 이름 호출 후보(정리 T 등), 「무관」 출현, 사족 후보(확인하지 못, 보지 못, 적지 않는다), [todo] 목록, 지위 표지의 낯선 낱말.
"""
import io
import os
import re
import sys

STATUS_OK = ["증명됨", "비형식 증명", "계산 증거"]
STATUS_BAD = ["형식 증명", "추측", "발견적"]
MODIFIERS = ["계산 보조", "작성자 판단", "시작점 비명시"]
LAYER_WORDS = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "인증 아님"]
STMT_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) (\d+)\.(\d+)(?: \(((?:[^()]|\([^()]*\))*)\))?(?: \[([^\]]*)\])?\.?\*\*")
ID_RE_BRACKET = re.compile(r"\[([^\]]*)\]")
ID_TOKEN_RE = re.compile(r"(?<![0-9a-zA-Z])r[0-9a-f]{7}(?![0-9a-zA-Z])")
ANY_ID_RE = re.compile(r"\[(r[0-9a-fA-F]{6,})")
REF_RE = re.compile(r"(정의|정리|명제|보조정리|따름정리) (\d+)\.(\d+)")
D_REF_RE = re.compile(r"부록 D\.(\d+)")
D_HEAD_RE = re.compile(r"^### D\.(\d+)\b")
FORBIDDEN_ALL = [r"마디", r"뿌리 문제", r"뿌리 명제", r"공표", r"판 \d+"]
FORBIDDEN_BODY = [r"노드", r"프런티어", r"생산자", r"peer", r"검토", r"세션", r"인스턴스", r"운영자"]
DISTINCTION = [r"(?:[와과은는]|서로) 다른 (?:양|기호|함수|대상|수|뜻|명제|결과|분해|자름|말)(?:이다|이고|이며|이라|과|와|로)", r"구별(?:한다|된다|해야|하여|하고|이다)", r"글자가 같지만", r"글자만 같"]
RECORD_NOTATION = [r"기록(?:은|이|에서는|들은|들이)?(?: 이를| 이것을| 이 양을| 이 사건을| 이 결과를)? [^\s]+(?:라|이라|로|으로)고? (?:부른다|적는다|쓴다)"]
FORWARD_REF = [r"이름은 [\d.]+절에서 정한다", r"뒤에서 정의한다", r"다음 절에서 정의"]
CORRECTION_HISTORY = [r"검토가 [^.]{0,40}(?:고쳤|정정했|바로잡)", r"생산자는 [^.]{0,30}적었"]
OMISSION = [r"다루지 않는다", r"옮기지 않는다", r"옮기지 않고", r"싣지 않는다", r"싣지 않고", r"생략한다", r"출처만", r"기록을 보라", r"않기로 했", r"사슬 밖(?!의 (?:꼭짓점|점|자리|나무|부분|성분))", r"계산의 층과 범위", r"이 글에 싣지", r"여기에 적지 않"]
ASIDE_CANDIDATES = [r"확인하지 못", r"보지 못했", r"대조하지 못", r"적지 않는다", r"다시 적지 않", r"되풀이하지 않"]
RECORD_NAME_CALL = re.compile(r"(정리|명제|보조정리|따름정리) [A-Z](?:[A-Za-z0-9′″‴♮♯◇⋆⁺⁻\-]*)(?=[은는이가을를의에와과로]|\s(?:에|의|을|를|과|와|로|에서|이|가))")


def find_ids(line):
    out = []
    for m in ID_RE_BRACKET.finditer(line):
        out.extend(ID_TOKEN_RE.findall(m.group(1)))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    path = args[0] if args else os.path.join(root, "원고.md")
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    failures, notes = [], []

    # 장 경계: 1..11, 부록 A/B/C/D = 101..104
    starts = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^## (\d+)\.", ln)
        if m:
            starts.append((i, int(m.group(1))))
            continue
        m = re.match(r"^## 부록 ([ABCD])", ln)
        if m:
            starts.append((i, 101 + "ABCD".index(m.group(1))))

    def chapter_of(i):
        ch = 0
        for s, n in starts:
            if i >= s:
                ch = n
        return ch

    for i, ln in enumerate(lines, 1):
        bad = [c for c in ln if ord(c) < 32 and c != "\t"]
        if bad:
            failures.append(f"{i}: 제어 문자 {['U+%04X' % ord(c) for c in bad]}")
        if "{{" in ln:
            failures.append(f"{i}: 남은 라벨 또는 임시 기호 … {ln[max(0, ln.find('{{') - 20): ln.find('{{') + 30]}")

    # 1. 진술 머리
    defined, per_chapter = set(), {}
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
        if int(ch) != chapter_of(i):
            failures.append(f"{i}: 진술 번호의 장 {ch}가 놓인 장 {chapter_of(i)}와 다름")
        if name and "기록" in name and not re.search(r"\[r[0-9a-f]{7}\]", name):
            failures.append(f"{i}: 머리 괄호의 기록 이름에 식별자 없음 ({name})")
        if bracket is None:
            if kind != "정의":
                failures.append(f"{i}: 지위 표지 없음: {kind} {ch}.{num}")
            continue
        if kind == "정의" and ";" not in bracket:
            status_part, ids_part = "", bracket.strip()
        else:
            outside = bracket
            for _ in range(3):
                outside = re.sub(r"\([^()]*\)", "", outside)
            if outside.count(";") != 1:
                failures.append(f"{i}: 지위 표지의 괄호 밖 쌍반점은 하나여야 함 [{bracket}]")
            status_part, _, ids_part = bracket.rpartition(";")
            status_part, ids_part = status_part.strip(), ids_part.strip()
        if kind != "정의":
            if not any(w in status_part for w in STATUS_OK):
                failures.append(f"{i}: 지위 낱말 없음 [{bracket}]")
            extra = status_part
            for w in STATUS_OK + MODIFIERS:
                extra = extra.replace(w, "")
            for w in STATUS_BAD:
                if w in extra:
                    failures.append(f"{i}: 이 글에 쓰이지 않는 지위 「{w}」 [{bracket}]")
            extra = re.sub(r"의존(?:하는)?|(?:\([가-힣]\))+", "", extra)
            extra = re.sub(r"[,，·\s은는이가의와과에서도만\(\)]+|항등식|부등식|대응|극한 진술|진술|앞 두 문장|셋째 문장|마지막 문장|문장|부분|입력|의존|(?:정리|명제|보조정리|따름정리) \d+\.\d+(?:·\d+\.\d+)*에?|\$[^$]*\$|" + "|".join(map(re.escape, LAYER_WORDS)) + r"|배정밀도 평가|30자리 수치 적분|40자리 평가|전수|\d+", "", extra)
            if extra.strip():
                notes.append(f"{i}: 지위 표지에 낯선 낱말 '{extra.strip()}' ([{bracket}])")
            for m2 in re.finditer(r"계산 (보조|증거)(\(([^()]*(?:\([^()]*\))?[^()]*)\))?", status_part):
                inner = m2.group(3) or ""
                if m2.group(1) == "보조" and not inner:
                    failures.append(f"{i}: 「계산 보조」에 층 괄호가 없음 [{bracket}]")
                    continue
                if inner and not any(w in inner for w in LAYER_WORDS):
                    failures.append(f"{i}: 계산 {m2.group(1)}의 괄호에 층 이름이 없음 '({inner})' [{bracket}]")
            if re.search(r"(?<!비형식 )증명됨", status_part) and "계산 보조" in status_part and "비형식 증명" not in status_part:
                failures.append(f"{i}: 「증명됨」과 「계산 보조」를 함께 둘 수 없음 [{bracket}]")
        if kind != "정의" and not ids_part:
            failures.append(f"{i}: 식별자 없음 [{bracket}]")
        for tok in re.split(r"[,\s]+", ids_part):
            if not tok or tok == "표준":
                continue
            if not re.fullmatch(r"r[0-9a-f]{7}", tok):
                failures.append(f"{i}: 식별자 꼴 이상 '{tok}' in [{bracket}]")

    # 3. 번호 연속·참조
    for ch, nums in sorted(per_chapter.items()):
        ns = sorted(nums)
        if ns != list(range(1, len(ns) + 1)):
            failures.append(f"장 {ch}: 번호 불연속 {ns}")
    for i, ln in enumerate(lines, 1):
        if STMT_RE.match(ln):
            continue
        for m in REF_RE.finditer(ln):
            before = ln[max(0, m.start() - 10): m.start()]
            if "Theorem" in before:
                continue
            key = (int(m.group(2)), int(m.group(3)))
            if key not in defined:
                failures.append(f"{i}: 정의되지 않은 번호 참조 {m.group(0)}")

    # 2. 식별자 집합 = 부록 B
    body_ids, b_ids = set(), set()
    for i, ln in enumerate(lines, 1):
        ch = chapter_of(i)
        ids = find_ids(ln)
        if ch == 102:
            b_ids.update(ids)
            b_ids.update(re.findall(r"^\|\s*(r[0-9a-f]{7})\s*\|", ln, re.M))
        else:
            body_ids.update(ids)
        for m in ANY_ID_RE.finditer(ln):
            if not re.fullmatch(r"r[0-9a-f]{7}", m.group(1)):
                failures.append(f"{i}: 식별자 꼴 이상 '[{m.group(1)}'")
    if b_ids or body_ids:
        ob, oB = sorted(body_ids - b_ids), sorted(b_ids - body_ids)
        if ob:
            failures.append("부록 B에 없는 본문 식별자: " + ", ".join(ob))
        if oB:
            failures.append("본문에 없는 부록 B 식별자: " + ", ".join(oB))

    # 4. 구분자 균형
    para, para_start = [], 1

    def check_para(pl, start):
        s = "\n".join(pl)
        if s.strip() == "" or s.lstrip().startswith("|"):
            return
        if s.count("$") % 2 == 1:
            failures.append(f"{start}: 문단의 $ 개수 홀수")
        if s.count("{") != s.count("}"):
            failures.append(f"{start}: 문단의 중괄호 불균형 ({s.count('{')} vs {s.count('}')})")
    for i, ln in enumerate(lines, 1):
        if ln.strip() == "":
            check_para(para, para_start)
            para, para_start = [], i + 1
        else:
            para.append(ln)
    check_para(para, para_start)

    # 5·6. 금지어, 구별 문장, 기록 표기, 앞당김, 정정 이력, 언급 금지
    for i, ln in enumerate(lines, 1):
        ch = chapter_of(i)
        in_body = 1 <= ch <= 10
        in_guarantee = ch == 11
        in_app = ch >= 101
        for pat in FORBIDDEN_ALL:
            for m in re.finditer(pat, ln):
                ctx = ln[max(0, m.start() - 15): m.end() + 15]
                if in_guarantee or in_app:
                    notes.append(f"{i}(11장/부록): 금지어 '{m.group(0)}' … {ctx}")
                else:
                    failures.append(f"{i}: 금지어 '{m.group(0)}' … {ctx}")
        if in_body:
            for pat in FORBIDDEN_BODY:
                for m in re.finditer(pat, ln):
                    ctx = ln[max(0, m.start() - 15): m.end() + 15]
                    failures.append(f"{i}: 11장 밖 운영 어휘 '{m.group(0)}' … {ctx}")
            for pat in DISTINCTION:
                for m in re.finditer(pat, ln):
                    failures.append(f"{i}: 구별 문장 … {ln[max(0, m.start() - 25): m.end() + 10]}")
            for pat in RECORD_NOTATION:
                for m in re.finditer(pat, ln):
                    failures.append(f"{i}: 기록 표기 문장 … {ln[max(0, m.start() - 10): m.end() + 5]}")
            for pat in FORWARD_REF:
                for m in re.finditer(pat, ln):
                    failures.append(f"{i}: 앞당김 참조 … {ln[max(0, m.start() - 20): m.end() + 5]}")
            for pat in CORRECTION_HISTORY:
                for m in re.finditer(pat, ln):
                    failures.append(f"{i}: 정정 이력 문장 … {ln[max(0, m.start() - 10): m.end() + 10]}")
        if in_body or in_guarantee:
            for pat in OMISSION:
                for m in re.finditer(pat, ln):
                    failures.append(f"{i}: 언급 금지 꼴 '{m.group(0)}' … {ln[max(0, m.start() - 25): m.end() + 10]}")
            for pat in ASIDE_CANDIDATES:
                for m in re.finditer(pat, ln):
                    notes.append(f"{i}: 사족 후보 '{m.group(0)}' … {ln[max(0, m.start() - 25): m.end() + 10]}")
            for m in re.finditer(r"무관", ln):
                notes.append(f"{i}: 무관 … {ln[max(0, m.start() - 20): m.end() + 10]}")
            if not STMT_RE.match(ln):
                for m in RECORD_NAME_CALL.finditer(ln):
                    before = ln[max(0, m.start() - 12): m.start()]
                    if "기록 [" in before or "Theorem" in before:
                        continue
                    notes.append(f"{i}: 기록 이름 호출 후보 '{m.group(0)}' … {ln[max(0, m.start() - 20): m.end() + 10]}")
        if "[todo" in ln:
            notes.append(f"{i}: [todo] … {ln[:80]}")

    # 7. 부록 D 참조
    d_items = set()
    for ln in lines:
        m = D_HEAD_RE.match(ln)
        if m:
            d_items.add(int(m.group(1)))
    d_refs = set()
    for i, ln in enumerate(lines, 1):
        for m in D_REF_RE.finditer(ln):
            n = int(m.group(1))
            d_refs.add(n)
            if n not in d_items:
                failures.append(f"{i}: 존재하지 않는 부록 D.{n} 참조")
    for n in sorted(d_items - d_refs):
        notes.append(f"부록 D.{n}은 본문이 가리키지 않음")

    # 8. 걸음·보행
    first_b = None
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r"걸음", ln):
            notes.append(f"{i}: 걸음 … {ln[max(0, m.start() - 12): m.end() + 12]}")
        if first_b is None and "보행" in ln:
            first_b = i
    if first_b is not None and "확률보행" not in "\n".join(lines[:first_b]):
        failures.append(f"{first_b}: 「보행」 첫 출현 앞에 「확률보행」 정의가 없음")

    todo = sum(1 for n in notes if "[todo]" in n)
    print(f"검사 대상: {path} ({len(lines)} lines)")
    print(f"번호 붙은 진술: {len(defined)}; 인용 식별자: {len(body_ids)}; 부록 B: {len(b_ids)}; 부록 D 항목: {len(d_items)}; [todo]: {todo}")
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
