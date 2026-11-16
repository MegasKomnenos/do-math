# -*- coding: utf-8 -*-
"""정합 검토 일곱의 지적 가운데 사용자 결정(2026-11-14 23:0x)이 난 것을 반영한다.
(1) 5.6절(두 항 부등식 X의 둘째 길)과 고아 넷(5.23·5.24·5.25·2.23) 삭제와 파생물 정리, (2) †가 있는 증명의 머리에 「작성자 판단」,
(3) 산술 등급 기준(이 글의 재계산)·144비트 정수 구간의 등급·「인증 아님」 이름, (4) 「칸」→구간·구획, 격자점 등재, 위 끝 허용,
(5) 사전(3절·1.2·부록 A·부록 C) 보강과 절 번호 정정, (6) 10.7절 다섯 고리를 둘째 증명 안으로, (7) 11.4 문헌 행 둘, (8) D.four-families 문장 이동,
(9) 명제 old-7-6 괄호의 기록 이름, (10) 1.5절 등급 표의 「인증 아님」. 멱등(앵커가 없고 새 문장이 있으면 건너뜀).
사용: python -I scripts/수학검사2/정합검토_반영2_1114.py [--dry]"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
DRY = "--dry" in sys.argv
FILES = {}
LOG = []


def rd(rel):
    if rel not in FILES:
        FILES[rel] = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    return FILES[rel]


def wr(rel, s):
    FILES[rel] = s


def rep(rel, old, new, must=True):
    s = rd(rel)
    c = s.count(old)
    if c == 1:
        wr(rel, s.replace(old, new)); LOG.append(("고침", rel, old[:50])); return True
    if c == 0 and new and new in s:
        return True
    if must:
        print(f"[앵커 {c}] {rel}: {old[:70]}")
    return False


def del_lines(rel, start_pred, end_pred, keep_end=True, note=""):
    """start_pred(line)이 참인 첫 줄부터 end_pred(line)이 참인 줄 앞까지(end 포함 여부 keep_end) 지운다."""
    lines = rd(rel).split("\n")
    si = next((i for i, l in enumerate(lines) if start_pred(l)), None)
    if si is None:
        return False
    ei = next((i for i in range(si + 1, len(lines)) if end_pred(lines[i])), len(lines))
    del lines[si:ei]
    # 빈 줄이 둘 이상 이어지면 하나로
    out = []
    for l in lines:
        if l == "" and out and out[-1] == "":
            continue
        out.append(l)
    wr(rel, "\n".join(out)); LOG.append(("줄 삭제", rel, f"{si+1}–{ei} {note}")); return True


def del_row(rel, pred):
    lines = rd(rel).split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| ") and pred(l)]
    if len(idx) == 1:
        del lines[idx[0]]; wr(rel, "\n".join(lines)); LOG.append(("행 삭제", rel, idx[0] + 1)); return True
    if len(idx) == 0:
        return False
    print("[행 삭제 후보 여럿]", rel, idx); return False


def insert_after_row(rel, pred, newrow):
    lines = rd(rel).split("\n")
    if newrow in lines:
        return True
    idx = [i for i, l in enumerate(lines) if l.startswith("| ") and pred(l)]
    if len(idx) == 1:
        lines.insert(idx[0] + 1, newrow); wr(rel, "\n".join(lines)); LOG.append(("행 삽입", rel, idx[0] + 2)); return True
    print("[삽입 앵커]", rel, len(idx), newrow[:50]); return False


# =============================== (1) 5.6절·고아 삭제 ===============================
# 장5A: 정의 X·보조정리 X⇒W♯(5.4절 끝)
del_lines("장v2/장5A.md", lambda l: l.startswith("**정의 {{5:old-5-16}}"), lambda l: False, note="X 정의·X⇒W♯(파일 끝까지)")
s = rd("장v2/장5A.md").rstrip("\n") + "\n"; wr("장v2/장5A.md", s)
rep("장v2/장5A.md", r"5.4.2절은 이 부등식을 $1.4\le\hat x\le10$의 창에서 적분 표현으로 보이고, 5.6절의 대체 경로는 같은 부등식을 창 너머 $\hat x>10$의 벌크 전체로 넓힌다.", r"5.4.2절은 이 부등식을 $1.4\le\hat x\le10$의 창에서 적분 표현으로 보인다.")
rep("장v2/장5A.md", r" 5.6절의 정리 {{5:old-5-39}}는 $\hat x>10$의 범위에서 행이 비감소임을 4.3절의 방법으로 따로 증명한다. 그래서 5.5절의 증명을 대신할 수 있는 대체 경로가 되지만, 두 길 어느 쪽의 입력도 아니다.", "")
# 장5B: 5.6절 전체, 5.23–5.25
del_lines("장v2/장5B.md", lambda l: l.startswith("### 5.6 "), lambda l: l.startswith("### 5.7"), note="5.6절")
del_lines("장v2/장5B.md", lambda l: l.startswith("**보조정리 {{5:old-5-23}}"), lambda l: l.startswith("**보조정리 {{5:stirling-bor}}"), note="5.23–5.25")
rep("장v2/장5B.md", r"창 항을 막으려면 음의 부분 $(x_t(y))_-$의 크기를 알아야 하는데, 그 크기는 나무 하나의 가장 큰 나무 사슬을 고정하고 보면 드러난다. 사슬을 고정하면 둘째 차분에서 음수가 될 수 있는 항은 하나뿐이다.", r"먼저 Borel 질량의 상하계와 세 제타 상수를 준비한다.")
rep("장v2/장5B.md", r"| 정리 {{5:old-5-18}} 또는 정리 {{5:old-5-39}} |", r"| 정리 {{5:old-5-18}} |")
# 장2: 명제 2.23
rep("장v2/장2.md", r"이라 한다(정리 {{2:old-2-10}}). 정리 {{2:old-2-10}}의 증명에서 허용 숲의 지수 생성함수는 허용 나무의 지수 생성함수의 지수함수였다. 그러므로 임계점에서 값을 취하면 허용 숲의 생성함수 값은 나무 생존 확률을 Borel 질량으로 가중해 더한 합의 지수함수다.", r"이라 한다(정리 {{2:old-2-10}}).")
del_lines("장v2/장2.md", lambda l: l.startswith("**명제 {{2:old-2-23}}"), lambda l: l.startswith("임계 볼츠만 법칙은 길이를 섞어 놓은 법칙이어서"), note="명제 2.23")
# 부록 D 5B: 두 항목(파일 끝까지)
del_lines("장v2/부록D_장5B.md", lambda l: l.startswith("### D.{{D:lemma-H-interval}}"), lambda l: False, note="D.lemma-H-interval·lemma-V-coefficients")
wr("장v2/부록D_장5B.md", rd("장v2/부록D_장5B.md").rstrip("\n") + "\n")
# 11장
del_row("장v2/장11.md", lambda l: l.startswith("| 부록 D.{{D:lemma-H-interval}}"))
del_row("장v2/장11.md", lambda l: l.startswith("| 부록 D.{{D:lemma-V-coefficients}}"))
rep("장v2/장11.md", r", 5.6절, 보조정리 {{5:old-5-41}}", "")
# 부록 A
del_row("장v2/부록A.md", lambda l: l.startswith("| $\\mathsf X$ |"))
# 부록 C
for key in ("| 기록 [r5f5cf73]의 Dawson 세 사실 |", "| 기록 [ra4c01fc]의 bulk-arc-leading-identities |", "| 기록 [r5f5cf73]의 보조정리 H(", "| 기록 [r5f5cf73]의 보조정리 V(", "| 안장점 |", "| 인증 구간 |"):
    del_row("장v2/부록C.md", lambda l, k=key: l.startswith(k))
# 장부 v2
del_row("장부_v2.md", lambda l: "[r5f5cf73] L79" in l)                                   # 1.3 5.6 묶음
del_row("장부_v2.md", lambda l: l.startswith("| $\\mathsf X$ |"))                        # 1.2 X
del_row("장부_v2.md", lambda l: l.startswith("| 인증 구간 |"))                            # 3절
del_row("장부_v2.md", lambda l: l.startswith("| 안장점 |"))                              # 3절
rep("장부_v2.md", r"| 첫 층 안쪽 | 첫 층의 가운데 부분 | 10.1 | 첫 층 벌크 |", r"| 첫 층 벌크 | 첫 층의 가운데 부분 | 6.4 | 같음 |")
rep("장부_v2.md", r"| 덮개 | 5.6 구간 산술의 덮개(상자들의 모임) | 5.6 | 덮개 |", r"| 덮개 | 구간 산술의 덮개(상자들의 모임) | 부록 D | 덮개 |")
rep("장부_v2.md", r"| Gauss 체제, Airy 체제, 선도항, 주항 | 5.6의 영역과 항 이름 | 5.6 | 같음 |", r"| 선도항, 주항 | 점근 전개의 첫 항과 주된 항 | 2.12, 4.3 | 같음 |")
rep("장부_v2.md", r"임계 창 잔여, 두 항 부등식 | 5장 ", r"임계 창 잔여 | 5장 ")
for old in (r"$\mathsf X$; ", r"안장점; ", r", 두 항 부등식", r"Gauss 체제, Airy 체제, "):
    rep("장부_v2.md", old, "")
# 5절 5장 행의 「인증 구간」(3절 행을 뺐으므로)과 「보조 뿌리」(3절 666 행·5절 10장 행 둘 다 — 자기 행으로 옮김)
_s = rd("장부_v2.md").split("\n")
for _i, _l in enumerate(_s):
    if _l.startswith("| 5 | $(\\mathrm G)_d$") and "인증 구간; " in _l:
        _s[_i] = _l.replace("인증 구간; ", "", 1); LOG.append(("고침", "장부 5절 5장 행", "인증 구간"))
    if "젊은 사슬, 익은 사슬, 면적, 임계 면적, 볼록 몫, 보조 뿌리, 첫째 꼴," in _l:
        _s[_i] = _l.replace("젊은 사슬, 익은 사슬, 면적, 임계 면적, 볼록 몫, 보조 뿌리, 첫째 꼴,", "젊은 사슬, 익은 사슬, 면적, 임계 면적, 볼록 몫, 첫째 꼴,"); LOG.append(("고침", "장부", "보조 뿌리 묶음"))
wr("장부_v2.md", "\n".join(_s))
rep("장부_v2.md", r"첫 층 안쪽; 격자, 격자점;", r"첫 층 벌크; 격자, 격자점;")
# 장부 4절: 뺌으로
REMOVED = {"5:old-5-16", "5:old-5-17", "5:old-5-39", "5:dawson-facts", "5:arc-leading", "5:gauss-moments", "5:old-5-40", "5:old-5-41",
           "5:old-5-23", "5:old-5-24", "5:old-5-25", "2:old-2-23"}
lines = rd("장부_v2.md").split("\n")
for i, l in enumerate(lines):
    if l.startswith("| ") and "{{" in l:
        m = re.search(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}", l)
        if m and m.group(1) in REMOVED:
            c = [x.strip() for x in l.strip()[1:-1].split("|")]
            if len(c) == 6:
                c[4] = "뺌"; c[5] = "(" + m.group(1) + ")"
                lines[i] = "| " + " | ".join(c) + " |"
                LOG.append(("뺌 행", "장부_v2.md", m.group(1)))
wr("장부_v2.md", "\n".join(lines))
# 첫 판 번호만 있고 현행 행도 뺌 행도 없던 아홉(결정 102)
NEW_REMOVED_ROWS = [
    "| 5.3 | 정리 | 마지막 102항 |  | 뺌 | (5:old-5-3) |",
    "| 5.6 | 정리 | 꼬리 오목성 TC |  | 뺌 | (5:old-5-6) |",
    "| 6.17 | 명제 | 원천 쪽 SRC⁺(`{{7:src-plus}}`로 대체) |  | 뺌 | (7:old-6-17) |",
    "| 7.47 | 명제 | 조각남 확률의 점근 꼴 | 기록 [r5909c9e]의 명제 A | 뺌 | — |",
    "| 7.48 | 명제 | 창×창 쌍 대 덮인 문턱의 극한 | 기록 [r5909c9e]의 명제 B | 뺌 | — |",
    "| 7.49 | 명제 | $PAIR/\\Theta$의 극한 | 기록 [r5909c9e]의 명제 C | 뺌 | — |",
    "| 8.7 | 명제 | 피벗 | 기록 [r3d0856b]의 명제 5 | 뺌 | (10:old-8-7) |",
    "| 8.27 | 명제 | 머묾 질량의 사슬 표현 | 기록 [re71a735]의 명제 D | 뺌 | (10:old-8-27) |",
    "| 8.29 | 보조정리 | 창 맨 앞의 하계 | 기록 [re71a735]의 보조정리 F | 뺌 | (10:old-8-29) |",
]
lines = rd("장부_v2.md").split("\n")
last_removed = max(i for i, l in enumerate(lines) if l.startswith("| ") and "| 뺌 |" in l)
for r in reversed(NEW_REMOVED_ROWS):
    if r not in lines:
        lines.insert(last_removed + 1, r)
wr("장부_v2.md", "\n".join(lines))
# 구조표
rep("구조표_v2.md", r"| 5.6 $X$의 증명 | 5.39,", r"| 5.6 $X$의 증명 | (결정 101로 5.6절 전체와 5.4의 정의 X·보조정리 X⇒W♯를 뺌 — 어느 증명도 쓰지 않는 둘째 길) 5.39,")
# 재실행표 여유 JSON
for key in ("lemma-H-interval", "lemma-V-coefficients"):
    s = rd("scripts/_재실행표_여유.json")
    s2 = re.sub(r'\n  "' + key + r'": "[^"\n]*",?', "", s)
    if s2 != s:
        # 마지막 항목의 쉼표 정리
        s2 = re.sub(r",(\n\})", r"\1", s2)
        wr("scripts/_재실행표_여유.json", s2); LOG.append(("JSON 키 삭제", key, ""))

# =============================== (2) † ↔ 작성자 판단 ===============================
import importlib
DD = importlib.import_module("_의존_도달")


def add_author_flag(head):
    if "작성자 판단" in head:
        return head
    m = re.search(r"\[([^\]]*)\]\.\*\*", head)
    inner = m.group(1)
    status, _, ids = inner.partition(";")
    # 「…에 의존」 앞에 넣고, 없으면 끝에
    dm = re.search(r", ((?:정리|명제|보조정리|따름정리|정의)[^,;\[\]]*에 의존)$", status)
    if dm:
        status = status[:dm.start()] + ", 작성자 판단, " + dm.group(1)
    else:
        status = status + ", 작성자 판단"
    return head[:m.start(1)] + status + ";" + ids + head[m.end(1):]


def apply_author_flags():
    # 임시로 현재 수정본을 파일에 반영하지 않고 메모리에서 분석하기 위해 장 파일을 임시 디렉토리에 쓰지 않는다 —
    # 대신 _의존_도달의 규칙을 간단히 재구현: 머리부터 다음 머리·'### ' 전까지가 본문.
    heads_to_flag = set()
    for name in DD.chapter_files("장"):
        rel = "장v2/" + name
        L = rd(rel).split("\n")
        marks = [(i, DD.HEAD_RE.match(l) is not None, DD.DEFER_RE.match(l) is not None, l.startswith("### ") or l.startswith("## ")) for i, l in enumerate(L)]
        for i, l in enumerate(L):
            h = DD.HEAD_RE.match(l)
            if not h:
                continue
            key = f"{h.group(2)}:{h.group(3)}"
            j = i + 1
            while j < len(L) and not (marks[j][1] or marks[j][2] or marks[j][3]):
                if "∎" in L[j]:
                    j += 1
                    break
                j += 1
            body = "\n".join(L[i:j])
            if "†" in body and "작성자 판단" not in l:
                heads_to_flag.add(key)
        # 뒤로 미룬 증명 단락
        for i, l in enumerate(L):
            d = DD.DEFER_RE.match(l)
            if not d:
                continue
            key = f"{d.group(2)}:{d.group(3)}"
            j = i + 1
            while j < len(L) and not (marks[j][1] or marks[j][2] or marks[j][3]):
                j += 1
            if "†" in "\n".join(L[i:j]):
                heads_to_flag.add(key)
    heads_to_flag |= {"7:transfer-F", "7:old-6-20", "7:old-6-21"}  # 절 도입 산문의 †가 세운 사실을 쓰는 진술
    heads_to_flag -= REMOVED
    n = 0
    for name in DD.chapter_files("장"):
        rel = "장v2/" + name
        L = rd(rel).split("\n")
        for i, l in enumerate(L):
            h = DD.HEAD_RE.match(l)
            if h and f"{h.group(2)}:{h.group(3)}" in heads_to_flag and "작성자 판단" not in l:
                L[i] = add_author_flag(l); n += 1
        wr(rel, "\n".join(L))
    LOG.append(("작성자 판단 머리", n, sorted(heads_to_flag)))
    return heads_to_flag


# 진술 밖 산문의 † 가운데 보충 설명인 것은 †를 뺀다(1.5절의 †는 증명 단계의 자리) — 머리 표지 계산보다 먼저
rep("장v2/장2.md", r"확률임을 알 수 있다. † $t\le2k$이면", r"확률임을 알 수 있다. $t\le2k$이면")
rep("장v2/장3.md", "\n† 꼬리 합에 대한 위의 논증을", "\n꼬리 합에 대한 위의 논증을")
rep("장v2/장5A.md", r"에서 확인된다. † 다만 실수축 나머지를 누르는", r"에서 확인된다. 다만 실수축 나머지를 누르는")
FLAGGED = apply_author_flags()
# 1.5절: 절 도입에서 미리 세운 단계의 †
rep("장v2/장1.md", r"이 글에서 메운 단계가 있음을 뜻하고, 본문에서는 그 단계가 시작하는 문장 앞에 칼표 †를 붙인다.", r"이 글에서 메운 단계가 있음을 뜻하고, 본문에서는 그 단계가 시작하는 문장 앞에 칼표 †를 붙인다. 그 단계가 절의 도입에서 미리 세운 사실이면 †는 그 문장에 두고 덧붙임은 그 사실을 쓰는 진술의 머리에 단다.")
# 1.5절 등급 표: 「인증 아님」 이름 폐기(부록 D의 표기대로)
rep("장v2/장1.md", r"| $\langle$정밀도$\rangle$ 평가, 인증 아님 | 반올림 오차의 상계를 증명하지 않은 부동소수점 계산이다. 정밀도를 이름에 넣어 「배정밀도 평가, 인증 아님」처럼 적는다 |", r"| $\langle$정밀도$\rangle$ 평가 | 반올림 오차의 상계를 증명하지 않은 부동소수점 계산이다. 정밀도를 이름에 넣어 「배정밀도 평가」처럼 적는다 |")

# =============================== (3) 산술 등급 기준 ===============================
rep("장v2/장11.md", r"다만 서술이 긴 항목은 앞부분만 옮기고 세부 수치와 기록의 검토가 한 일의 나머지는 부록 D에 둔다.", r"이 열은 부록 D 항목의 「독립 재계산」 줄에서 꺾쇠 괄호를 뺀 나머지를 그대로 옮긴 것이다.")
rep("장v2/장11.md", r"「산술 등급」 열의 등급은 증명이 기대는 처음 계산의 것이고,", r"「산술 등급」 열의 등급은 증명이 기대는 계산, 곧 이 글의 재계산이 있으면 그 재계산(부록 D 「산술 등급」 줄의 첫 등급)의 것이고,")
rep("장v2/장2.md", r"[진술은 증명됨, 유한 $n$의 상계값은 계산 증거(정확 정수·유리수, 방향 반올림 구간); r88bed8a]", r"[진술은 증명됨, 유한 $n$의 상계값은 계산 증거(방향 반올림 구간); r88bed8a]")
L = rd("장v2/장7A.md").split("\n")
for i, l in enumerate(L):
    if l.startswith("**보조정리 {{7:column-lemma}}") and "계산 보조(방향 반올림 구간)" in l:
        L[i] = l.replace("계산 보조(방향 반올림 구간)", "계산 보조(정확 정수·유리수)", 1); LOG.append(("등급", "column-lemma 머리", ""))
wr("장v2/장7A.md", "\n".join(L))
rep("장v2/부록D_장7A.md", r"**산술 등급.** 방향 반올림 구간. $144$비트 고정소수점 정수 구간이고, 기록의 독립 재계산은 $160$비트, 이 글의 재계산은 $160$비트다.", r"**산술 등급.** 정확 정수·유리수($144$비트 고정소수점 정수 구간; 1.5절의 등급 표대로 바깥쪽으로만 반올림하는 정수 구간은 이 등급에 든다). 기록의 독립 재계산은 $160$비트, 이 글의 재계산은 $160$비트다.")
rep("장v2/장11.md", r"| 부록 D.{{D:column-certification-k500}} | 보조정리 {{7:column-lemma}} | 방향 반올림 구간 | 7.2 |", r"| 부록 D.{{D:column-certification-k500}} | 보조정리 {{7:column-lemma}} | 정확 정수·유리수 | 7.2 |")
rep("장v2/장11.md", r"정리 {{7:seed-transfer}}: 정확 정수·유리수; 보조정리 {{7:column-lemma}}: 방향 반올림 구간 |", r"정리 {{7:seed-transfer}}·보조정리 {{7:column-lemma}}: 정확 정수·유리수 |")

# =============================== (4) 칸·격자점·위 끝 ===============================
KAN = {
    "장v2/부록D_장7A.md": [("먼 칸", "먼 구획"), ("칸 반폭", "구획 반폭"), ("칸 $i$", "구획 $i$"), ("칸 입력", "구획 입력"), ("칸별 상·하계", "구획별 상·하계"),
                        ("칸의 양 끝", "구획의 양 끝"), ("칸의 오른쪽 끝값", "구획의 오른쪽 끝값"), ("첫 칸", "첫 구획"), ("칸이 ", "구획이 ")],
    "장v2/부록D_장8.md": [("항 $q$의 칸", "항 $q$의 구간"), ("$400$칸", "$400$개 구간"), ("$6000$칸", "$6000$개 구간"), ("칸마다", "구간마다")],
    "장v2/부록D_장9.md": [("같은 길이의 칸", "같은 길이의 구간"), ("칸마다", "구간마다"), ("칸 $80000$개", "구간 $80000$개"), ("칸 전체", "구간 전체"), ("칸 길이", "구간 길이")],
    "장v2/부록D_장10.md": [("구간 칸 $40000$개", "구간 $40000$개"), ("기하 칸", "기하 구간"), ("칸(비", "구간(비"), ("칸마다", "구간마다"), ("칸 전체", "구간 전체")],
    "장v2/장11.md": [("칸 $20000$개", "구간 $20000$개")],
    "장v2/장3.md": [("칸 $C_\\ell$", "구획 $C_\\ell$")],
    "장v2/장7A.md": [("단위원을 칸으로 덮고, 칸마다", "단위원을 구간으로 덮고, 구간마다")],
    "원고_자료/빠른_확인.py": [("저장된 칸 표의 판독", "저장된 구간 표의 판독")],
}
for rel, pairs in KAN.items():
    s = rd(rel)
    for a, b in pairs:
        if a in s:
            s = s.replace(a, b); LOG.append(("칸", rel, a))
    wr(rel, s)
rep("장부_v2.md", r"| 격자 | 계산 인증에서 상자·셀을 놓거나 값을 평가한 점들의 모임(5.4의 계산 격자; 7.3의 격자 판정; 8.2의 기하 격자 $J_i$) | 5.4 | 격자점, 노드 위치 |",
    r"| 격자 | 계산 인증에서 상자·셀을 놓거나 값을 평가한 점들의 모임(5.4의 계산 격자; 7.3의 격자 판정; 8.2의 기하 격자 $J_i$) | 5.4 | 노드 위치 |")
insert_after_row("장부_v2.md", lambda l: l.startswith("| 격자 | 계산 인증에서"), r"| 격자점 | 격자를 이루는 점 하나(상자·셀의 끝점이나 값을 평가한 점) | 5.4 | 격자점 |")
rep("장부_v2.md", r"| 상단·하단 | 구간의 두 끝(구간 산술의 결과 구간, 정수 구간, 인증 구간의 위·아래 끝) | 부록 D | 구간 상한·하한 |",
    r"| 상단·하단 | 구간의 두 끝(구간 산술의 결과 구간, 정수 구간, 인증된 구간의 위·아래 끝); 「위 끝·아래 끝」도 같은 뜻으로 쓴다 | 부록 D | 구간 상한·하한 |")
rep("장부_v2.md", r"| 칸 | 수열에서 이웃한 항 사이의 한 단위(한 칸 차분; 끝에서 $r+1$번째 칸) | 1.3 | 칸; 분할의 칸은 「구획」, 적분 비교의 구간은 「구간」 |",
    r"| 칸 | 수열에서 이웃한 항 사이의 한 단위(한 칸 차분; 끝에서 $r+1$번째 칸; 5.2의 $r$ 칸; 부동소수점의 이웃 수 사이도 한 칸) | 1.3 | 칸; 분할의 칸은 「구획」, 적분 비교의 구간은 「구간」 |")

# =============================== (5) 사전 보강 ===============================
NEW_WORDS = [  # (앞 행 판별 접두, 새 행)
    ("| 용량 |", r"| 용량 가중 결과 순열 법칙 | 최대 변위가 열의 용량보다 작다는 조건 아래 결과 순열이 따르는 법칙(7장 모멘트 판정의 바탕) | 1.4, 7.1 | 같음 |"),
    ("| 기저량 |", r"| 창 항 | 5.5의 차분 하계에서 크기가 용량 바로 위인 나무들이 내는 음의 항을 모은 것($\mathrm{WIN}_0$) | 5.5 | 같음 |"),
    ("| 나무 함수 |", None),
]
# 3절의 표 끝(「## 4.」 앞)에 묶어 넣는 쪽이 안전: 3절 마지막 행 뒤에 삽입
lines = rd("장부_v2.md").split("\n")
i3 = next(i for i, l in enumerate(lines) if l.startswith("## 3. 낱말 사전"))
i4 = next(i for i, l in enumerate(lines) if i > i3 and l.startswith("## 4."))
last_row = max(i for i in range(i3, i4) if lines[i].startswith("| "))
ADD_ROWS = [
    r"| 용량 가중 결과 순열 법칙 | 최대 변위가 열의 용량보다 작다는 조건 아래 결과 순열이 따르는 법칙(7장 모멘트 판정의 바탕) | 1.4, 7.1 | 같음 |",
    r"| 창 항 | 5.5의 차분 하계에서 크기가 용량 바로 위인 나무들이 내는 음의 항을 모은 것($\mathrm{WIN}_0$) | 5.5 | 같음 |",
    r"| 허용 숲, 허용 나무 | 최대 변위가 수준 $\ell$ 이하인 숲과 나무(정리 `{{2:old-2-10}}`의 증명) | 2.4 | 같음 |",
    r"| 대각선 둘째 차분 | $y\,s_m(y)$를 결손 $d=m-y+1$을 고정한 대각선 방향으로 두 번 차분한 양 | 6.6 | 같음 |",
    r"| 사슬 생존 곱 | 무거운 사슬의 걸음별 생존 인자의 곱 $\Pi_j(y)=\prod_{i\le j}y/(y+q_i)$ | 6.6 | 같음 |",
    r"| 나무 함수 | 뿌리 라벨 나무의 지수 생성함수 $T(x)=\sum_{t\ge1}t^{t-1}x^t/t!$ | 2.5 | — |",
    r"| 상쇄 분해, 중앙 상쇄 항등식 | 중앙 틈 증명에서 둘째 차분을 서로 상쇄하는 조각들로 가른 분해와 그 항등식 | 4.3 | — |",
    r"| 원 비교 | 모멘트 판정을 거치지 않은 비교 $b_{n,k-1}<b_{n,k}$ 자체 | 7.4 | — |",
    r"| Green 응답 | 2.7의 재귀에서 무거운 자리가 들어 있지 않은 항 하나하나가 내는 몫(그 몫 하나의 꼴) | 2.7 | 같음 |",
    r"| 꼭대기 보정 | 5.5 기저 항등식의 보정항 $\mathrm{top}$ | 5.5 | 같음 |",
    r"| 중복 몫 | 한 나무 재귀의 $\mathrm{dup}_m$($e^{\mathcal B_k}-1-\mathcal B_k$에서 오는 몫) | 8.1 | 같음 |",
    r"| 기울임 증분 | 기울임 함수 $g$의 두 값의 차 $\mathrm{inc}^\pm_q$ | 10.5 | 같음 |",
    r"| 용량 구간 | 자리에서 자기 용량만큼 왼쪽으로 뻗은 구간 | 2.5 | 같음 |",
    r"| 오차 예산 | 수치 계산에서 허용하는 오차의 총량(예: 실수축 나머지의 $e^{-800}$, FFT 오차 예산 $\mathfrak e$) | 5.4 | 같음 |",
    r"| 보조 뿌리 | 숲의 모든 뿌리를 매다는 가상의 뿌리(숲을 크기 $n+1$의 나무로 보기 위한 것) | 2.11 | 같음 |",
]
for r in reversed(ADD_ROWS):
    if r not in lines:
        lines.insert(last_row + 1, r)
wr("장부_v2.md", "\n".join(lines))
rep("장부_v2.md", r"| 엄격 단봉 | 올라가는 구간과 내려가는 구간에서 부등식이 모두 엄격한 단봉 | 3.2 | 강단봉성, 엄격 단봉성 |", r"| 엄격 단봉 | 올라가는 구간과 내려가는 구간에서 부등식이 모두 엄격한 단봉(성질 이름은 「엄격 단봉성」) | 3.2 | 강단봉성 |")
rep("장부_v2.md", r"Cayley 무게, 모양 무게) | 2.5 | 무게, 가중치 |", r"Cayley 무게, 모양 무게) | 2.5 | 무게, 가중치(이름 밖에서) |")
rep("장부_v2.md", r"| Borel 꼬리 | $\mathrm{Bor}_>(q)=\sum_{d>q}\mathrm{Bor}(d)$ | 6.1 | 같음 |", r"| Borel 꼬리 | Borel 분포의 꼬리 합: 4.3의 $\mathrm{Bor}^{\mathrm{tail}}_k(s)$와 6.1의 $\mathrm{Bor}_>(q)=\sum_{d>q}\mathrm{Bor}(d)$ | 4.3, 6.1 | 같음 |")
rep("장부_v2.md", r"| 첫째 보정, 둘째 보정 | 가중치 $W_n(\gamma)$의 $1/n$ 전개를 일차·이차까지 남긴 것 | 5.4 | 같음 |", r"| 첫째 보정, 둘째 보정 | 가중치 $W_n(\gamma)$의 $1/n$ 전개를 일차·이차까지 남긴 것(5.4); 중앙 틈 점근의 두 보정항(4.3) | 4.3, 5.4 | 같음 |")
rep("장부_v2.md", r"| 조각 | 오른쪽에서 본 최댓값 자리에서 자른 것(정리 `{{7:old-6-6}}` 증명의 $(r_{t-1},r_t]$) | 7.2 | 블록(셋째 뜻), 조각 |", r"| 조각 | 오른쪽에서 본 최댓값 자리에서 자른 것(정리 `{{7:old-6-6}}` 증명의 $(r_{t-1},r_t]$); 증명·적분·범위의 부분을 셀 때는 일반어 | 7.2 | 블록(셋째 뜻), 조각 |")
rep("장부_v2.md", r"| 지배 극, 갱신열, 갱신 인증서, 유한 크기 전달 | 7.3의 도구 이름 | 7.3 | 같음 |", r"| 지배 극, 갱신열, 갱신 인증서, 유한 크기 전달 | 7.3의 도구 이름(갱신열은 7.2의 극 정규화 갱신열부터) | 7.2, 7.3 | 같음 |")
rep("장부_v2.md", r"덮인 문턱, 덮개 몫, 한 나무 항등식, 착지 비, 착지 무게, 쌍 보정, 요구값 | 9.2–9.3의 도구 이름 | 9.2 | 같음 |", r"덮인 문턱, 덮개 몫, 한 나무 항등식, 착지 비, 착지 무게, 쌍 보정, 요구값 | 9.2–9.3의 도구 이름(덮개 몫은 9.5) | 9.2, 9.3, 9.5 | 같음 |")
rep("장부_v2.md", r"꺾인 무게, 문턱 뒤 머묾 질량, 띠 인자, 방문 질량, 첫 도달 몫 | 10장의 도구 이름 | 10.1–10.4 | 같음 |", r"꺾인 무게, 문턱 뒤 머묾 질량, 띠 인자, 방문 질량, 첫 도달 몫 | 10장의 도구 이름(이차 몫·선형 몫은 7.5부터) | 7.5, 10.1–10.4 | 같음 |")
rep("장부_v2.md", r"| 상자 | 구간 산술 검사의 단위(변수 범위의 직사각형; 8.4에서는 $(k,\nu)$ 상자) | 1.5(상자 여유), 8.4 | 상자; 계산의 「블록」 |", r"| 상자 | 구간 산술 검사의 단위(변수 범위의 직사각형; 8.4에서는 $(k,\nu)$ 상자) | 1.5(상자 여유), 8.4 | 상자; 계산의 「블록」(행렬·코드의 블록은 그대로 「블록」) |")
rep("장부_v2.md", r"| 경계 | 구간·절반·영역의 가장자리와 그 항(두 절반의 경계, 증가 경계·반감 경계, 경계 다항식·경계 응답·경계항). 상계·하계의 뜻으로는 쓰지 않는다(결정 95) | 1.5 |", r"| 경계 | 구간·절반·영역의 가장자리와 그 항(두 절반의 경계, 증가 경계·반감 경계, 경계 다항식·경계 응답·경계항). 상계·하계의 뜻으로는 쓰지 않는다(결정 95) | 1.4 |")
rep("장v2/부록C.md", r"| 연쇄 | 사슬(둘째·셋째 뜻) | 2.11, 4.3 |", r"| 연쇄 | 사슬(둘째·셋째 뜻) | 4.3 |")
rep("장v2/부록C.md", r"| 무거운, 가벼운 | 무거운, 가벼운; 「무거운 자리·가벼운 자리」는 「무거운 환경·가벼운 환경」 | 2.5 |", r"| 무거운, 가벼운 | 무거운, 가벼운; 「무거운 자리·가벼운 자리」는 「무거운 환경·가벼운 환경」 | 1.5 |")
# 3절 머리: 첫 정의 절 관례와 부록 C 유지 방식
rep("장부_v2.md", r"첫 정의 절은 구조표 v2대로이며 그 절 앞에서는 쓰지 않는다.", r"첫 정의 절은 구조표 v2대로이며 그 절 앞에서는 쓰지 않는다. 첫 정의 절은 기술적 정의가 놓인 절이고, 1.4절 개관이 먼저 이름을 부른 낱말도 기술적 정의의 절로 적는다(1.4절에서 정의가 끝나는 낱말만 1.4). 부록 C의 낱말 표는 이 표에서 생성한 뒤 손 편집으로 유지하며 새 행은 증분 동기화로 옮긴다(결정 100).")
# 1.2 행 추가: 𝒪_n, rq
insert_after_row("장부_v2.md", lambda l: l.startswith("| $\\mathcal N_\\ell(t)$ |") and "N·필기체" in l, r"| $\mathcal O_n$ | O·필기체 | 재생 항등식의 교차항 $d_{n,k}-\sum_{t=k}^{n}\binom nt\,\delta_t\,A_{n-t,k-1}$(명제 `{{9:regeneration-S}}`(나); 모든 $n\ge0$에서 음이 아니고 $2k+1\le n\le3k-1$에서 $\mathrm{PAIR}_n$과 같다) | 9.4 | 9 | — | $\mathcal X_n$ ([r05cf8c9]) |")
insert_after_row("장부_v2.md", lambda l: l.startswith("| $\\mathrm{regen}_n$ |"), r"| $\mathrm{rq}_r, \mathrm{rq}$ | rq·로마체 이름 | 사슬 가중치의 전개에 쓰는 꼬리 좌표와 행 크기의 비: 5.2.3절부터 $\mathrm{rq}_r:=(r+3)/n$, 5.4절부터 $\mathrm{rq}:=r/n$(첨자 유무로 두 정의를 가른다) | 5.2 | 5 | $\varrho_r$, $\varrho$ | — |")
# 1.2·부록 A: 국소 글자와 겹치는 전역 글자의 구별 구절
for rel in ("장부_v2.md", "장v2/부록A.md"):
    rep(rel, r"용량 이동 비 $s_N(k-1)/s_N(k)$의 하계(보조정리 `{{8:old-6-30}}`)", r"용량 이동 비 $s_N(k-1)/s_N(k)$의 하계(보조정리 `{{8:old-6-30}}`; 5.5의 국소 상수 $\mathfrak c_0$과 다른 양)")
    rep(rel, r"정규화 수준 질량의 최댓값 $\max_{k\le N\le2k-1}\mathrm{cl}^-_N$와 그 임의 상계", r"정규화 수준 질량의 최댓값 $\max_{k\le N\le2k-1}\mathrm{cl}^-_N$와 그 임의 상계(7.2의 국소 미분 횟수 $\mathfrak d_k$와 다른 양)")
    rep(rel, r"| $\mathrm{BV}_n-(\Theta_n-\Theta^\circ_n)$ | 9.2 |", r"| $\mathrm{BV}_n-(\Theta_n-\Theta^\circ_n)$(6.6의 국소 사슬 경로 집합 $\mathcal C_n$과 다른 양) | 9.2 |", must=False)
rep("장부_v2.md", r"| $\mathcal C_n$ | C·필기체 | $\mathrm{BV}_n-(\Theta_n-\Theta^\circ_n)$ | 9.2 |", r"| $\mathcal C_n$ | C·필기체 | $\mathrm{BV}_n-(\Theta_n-\Theta^\circ_n)$(6.6의 국소 사슬 경로 집합 $\mathcal C_n$과 다른 양) | 9.2 |", must=False)
rep("장부_v2.md", r"피적분함수(인수 $\theta$는 5.5.6의 국소 척도 변수 $z/Y^{1/3}$)", r"피적분함수(인수 $\theta$는 5.5.6의 국소 척도 변수 $z/Y^{1/3}$; 4.3의 국소 $\mathfrak g(\kappa)$와 다른 양)")
rep("장v2/부록A.md", r"피적분함수(인수 $\theta$는 5.5.6의 국소 척도 변수 $z/Y^{1/3}$)", r"피적분함수(인수 $\theta$는 5.5.6의 국소 척도 변수 $z/Y^{1/3}$; 4.3의 국소 $\mathfrak g(\kappa)$와 다른 양)")
# 7절 thr_n 주석
rep("장부_v2.md", r"| $\Theta_n$ | [rcb2e2d4]; [r05cf8c9] | $\mathrm{thr}_n=\varpi_n(k)/k$; $K_n=-\Theta_n$ | 글자; 부호 |", r"| $\Theta_n$ | [rcb2e2d4]; [r05cf8c9] | $\mathrm{thr}_n=\varpi_n(k)/k$(7.5의 국소 $\mathrm{thr}_n$과 다른 양); $K_n=-\Theta_n$ | 글자; 부호 |")
rep("장v2/부록C.md", r"| $\Theta_n$ | [rcb2e2d4]; [r05cf8c9] | $\mathrm{thr}_n=\varpi_n(k)/k$; $K_n=-\Theta_n$ | 글자; 부호 |", r"| $\Theta_n$ | [rcb2e2d4]; [r05cf8c9] | $\mathrm{thr}_n=\varpi_n(k)/k$(7.5의 국소 $\mathrm{thr}_n$과 다른 양); $K_n=-\Theta_n$ | 글자; 부호 |", must=False)

# =============================== (6) 10.7절 다섯 고리를 둘째 증명 안으로 ===============================
L = rd("장v2/장10.md").split("\n")
i_first = next((i for i, l in enumerate(L) if l.startswith("첫째 고리는 ")), None)
i_head = next((i for i, l in enumerate(L) if l.startswith("**정리 {{10:old-8-37}}")), None)
if i_first is not None and i_head is not None and i_first < i_head:
    head = L[i_head]
    # 머리 뒤: 빈 줄, 「**증명.** 위에 적은 다섯 고리를 차례로 이으면 된다. ∎」, 빈 줄, 비교 문장
    j = i_head + 1
    while j < len(L) and L[j] == "":
        j += 1
    proof_line = L[j]
    assert proof_line.startswith("**증명.** 위에 적은 다섯 고리"), proof_line
    links = L[i_first:i_head]                       # 다섯 고리 단락(끝 빈 줄 포함)
    while links and links[-1] == "":
        links.pop()
    # 마지막 고리 단락 끝에 ∎
    links[-1] = links[-1].rstrip() + " ∎"
    new_block = [head, "", "**증명.** 다섯 고리를 차례로 잇는다.", ""] + links + [""]
    L = L[:i_first] + new_block + L[j + 1:]
    wr("장v2/장10.md", "\n".join(L)); LOG.append(("10.7 재배열", "", ""))

# =============================== (7) 11.4 문헌 행 둘 ===============================
insert_after_row("장v2/장11.md", lambda l: l.startswith("| Tanner, *A problem of interference"), r"| OEIS Foundation, *The On-Line Encyclopedia of Integer Sequences*, 수열 A078434 | $\zeta(3/2)=2.6123753486\ldots$의 십진 전개 | 보조정리 {{6:lemma-Hprime}} |")
lines = rd("장v2/장11.md").split("\n")
coth = r"| Ahlfors, 같은 책 | Chapter 5 §2.1(부분분수 전개; $\pi\cot\pi z$의 전개에서 $\coth$의 전개 $\sigma\coth\sigma=1+\sum_{i\ge1}2\sigma^2/(\sigma^2+i^2\pi^2)$가 나온다) | 보조정리 {{6:geometric-mean}} |"
if coth not in lines:
    ti = next(i for i, l in enumerate(lines) if l.startswith("| Tanner, *A problem of interference"))
    lines.insert(ti, coth); wr("장v2/장11.md", "\n".join(lines)); LOG.append(("11.4 coth 행", "", ""))

# =============================== (8) D.four-families 문장 이동 ===============================
L = rd("장v2/부록D_장10.md").split("\n")
i_ff = next((i for i, l in enumerate(L) if l.startswith("### D.{{D:four-families}}")), None)
if i_ff is not None:
    j_chk = next(i for i in range(i_ff, len(L)) if L[i].startswith("**확인하는 진술.**"))
    j_ind = next(i for i in range(i_ff, len(L)) if L[i].startswith("**독립 재계산.**"))
    m = re.search(r" 또 각 가족에서[^.]*\{\{10:old-8-32\}\}[^.]*해석적 논증이다\)\.", L[j_chk])
    if m:
        sent = m.group(0).strip()
        L[j_chk] = L[j_chk][:m.start()] + L[j_chk][m.end():]
        L[j_ind] = L[j_ind].rstrip() + " 이 밖에 " + sent[len("또 "):] if sent.startswith("또 ") else L[j_ind].rstrip() + " " + sent
        wr("장v2/부록D_장10.md", "\n".join(L)); LOG.append(("four-families 문장 이동", "", ""))

# =============================== (9) 명제 old-7-6 괄호 ===============================
rep("장v2/장9.md", r"**명제 {{9:old-7-6}} (줄기 더하기 쌍, 벌크; 명제 $\mathsf B^+$)", r"**명제 {{9:old-7-6}} (줄기 더하기 쌍, 벌크; 기록 [rae1f209]의 명제 $\mathsf B^+$)")
rep("장부_v2.md", r"| 7.6 | 명제 | 줄기 더하기 쌍, 벌크 |  | 9.2 | {{9:old-7-6}} |", r"| 7.6 | 명제 | 줄기 더하기 쌍, 벌크 | 기록 [rae1f209]의 명제 $\mathsf B^+$ | 9.2 | {{9:old-7-6}} |")
insert_after_row("장v2/부록C.md", lambda l: l.startswith("| 기록 [rae1f209]의 정리 A | 정리 {{9:old-7-5}} |"), r"| 기록 [rae1f209]의 명제 $\mathsf B^+$ | 명제 {{9:old-7-6}} | 줄기 더하기 쌍, 벌크 |")

# =============================== η: 5.6 밖에 쓰임이 없으면 행 삭제 ===============================
eta_elsewhere = False  # 3·6·7장의 η는 국소 글자(1.3 묶음에 등록)이고 1.2의 전역 뜻 (r+1)/k는 5.6절과 함께 사라진다
if not eta_elsewhere:
    del_row("장부_v2.md", lambda l: l.startswith("| $\\eta$ | \\eta·일반(이탤릭) | 임계 창의 척도 매개변수"))
    del_row("장v2/부록A.md", lambda l: l.startswith("| $\\eta$ | 임계 창의 척도 매개변수"))
    rep("장부_v2.md", r"$\mathsf W, \mathsf W^\sharp$; $\eta$; $\mathrm{tail}_t(y)$", r"$\mathsf W, \mathsf W^\sharp$; $\mathrm{tail}_t(y)$", must=False)
    LOG.append(("η 행 삭제", "", ""))
else:
    LOG.append(("η 남음(확인 요)", "", ""))

# =============================== 쓰기 ===============================
for rel, s in FILES.items():
    if not DRY:
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
for item in LOG:
    print(item if len(str(item)) < 300 else str(item)[:300])
print("파일", len(FILES), "(dry)" if DRY else "")
