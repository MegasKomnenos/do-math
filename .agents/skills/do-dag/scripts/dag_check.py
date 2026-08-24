"""파견표 검산 — 전개가 행을 저작한 직후 자기검사로, 오케가 파견 전 사이클마다 돌린다.

검산 대상은 아홉으로 한정하고, 아홉 다 파견표 한 파일의 문자열과 파일시스템만으로
닫힌다.

① 행 서식 — 칸이 정확히 일곱이고, 행 번호가 실재하고 문법에 맞고 유일한가.
② 상태·유형 어휘 — 닫힌 목록 안인가(공백 불허).
③ 칸 계약 — 행 유형이 요구하는 칸이 채워졌는가. 값·`—`(명시적 해당 없음)·빈
   칸(누락)은 서로 다른 사실이다. 미완결 전개의 완료 신호는 `<번호>-보고.md`다.
④ 서브트리 폐쇄 — 행 `X.n`은 `X` 또는 `X`의 범위 안만 선행으로 지목한다.
   바깥을 보려면 그 서브트리의 싱크(`*.z`)를 지목한다.
⑤ 싱크 수렴 — 전개 `X`의 모든 자손은 `X.z`에 도달하고, 최상위 행 전부는 국면
   싱크에 도달한다. 마디 있는 행은 자기 부모가 파견표에 실재해야 한다. 과거 형식에서
   완료 신호에 디렉토리를 적은 전개는 완결되면 자기 싱크를 실제로 깔았어야 한다.
   국면 종결 싱크는 정확히 하나다. 아직 펼쳐지지 않은 전개의 약속된 싱크는 통과 지점이다.
⑥ 순환 부재.
⑦ 좌표 실재 — 파견문이 파일시스템에 있는가. 그 파견문의 `계약:` 슬롯과 `불변식:`
   슬롯이 실재하는 파일을 싣는가. `불변식:` 슬롯이 상위 전개의 불변식 전건을 승계하고,
   그 좌표가 읽기 목록과 예산에 실렸는가. `모델 배정 근거:` 슬롯이 채워졌는가.
   【완결상태 · 완 · 비준】 행의 완료 신호가 전건 있고 비지 않았는가. 검증런 계약을
   적재한 완결 행은 동결·장부·종료보고와 장부의 라운드 1 본표·결산을 갖췄는가.
   그 종료보고의 「발견」 절에 항목이 있으면 같은 층의 전개 행이 그 종료보고를
   `정본:` 슬롯에 싣는가(검토전개 — `계약/검증런.md` 「발견 처리」).
   완결된 싱크는 결산 frontmatter의 `상태`가 반환과 같고 `단계`가 원장의
   종착값이어야 한다.
⑧ 게이트 결정 — 【완결상태 · 완 · 비준】 게이트의 결정 파일에 사용자 축자 절이 채워졌고
   frontmatter `상태`가 `결정됨`인가. 서식 플레이스홀더(`{…}`)만 남은 절은 빈 절이다.
   그 결정 파일을 선행 사슬의 어느 행이 낳는가. 그 게이트를 선행으로 지목해 일하는
   행이 전개이고 그 파견문의 `정본:` 슬롯이 결정 좌표를 싣는가.
⑨ 운전 — 파견 직전 행(미착수이고 선행이 전부 완결)의 실행 좌표가 완비됐는가.

두 모드가 있다. `partial`은 전개가 표를 작성하는 동안의 임시 상태를 허용하고,
`drive`(기본)는 오케가 파견하기 전에 적용하는 완성 계약이다. partial이 미루는 것은
넷뿐이다 — 국면 종결 싱크의 부재, 게이트 결정 파일을 낳는 행의 실재, 게이트 결정의
후행 소비, 운전 검사. 전개는 표를 쓰는 동안 partial로 재고, 오케는 `진행`인 `전개`
행이 있으면 partial·없으면 drive로 잰다(`대응표.md`).

partial은 **살아 있는 전개의 서브트리를 발견에서 제외한다.** 제외는 발견의 억제이지
행의 삭제가 아니다 — 제외된 행도 남의 선행으로 지목될 때는 실재하는 것으로 센다.
`--writer <행번호>`는 부르는 쪽이 자기를 밝히는 인자다. 그 행의 서브트리는 제외에서
빠지므로 전개가 자기검사에 쓴다. 없으면 살아 있는 전개 전부가 제외된다(오케가 쓴다).

`--sink-return <행번호> <첫 낱말>`은 두 모드와 별개인 반환 전용 게이트다. 전체 표를
다시 재지 않고 실제 싱크 반환과 결산 frontmatter만 대조한다.

목표 충실성·분해 타당성 같은 판단 성분은 코드가 아니라 렌즈와 판정 처분 전개의 몫이다.

사용:
    python dag_check.py --table .sdd/dag/<국면>/파견표.md
    python dag_check.py --table ... --mode partial
    python dag_check.py --table ... --mode partial --writer 2.5
    python dag_check.py --table ... --sink-return 2.z 완료미충족
    (exit 0 = 무발견, 1 = 발견. 발견 목록은 stdout)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# 아래 생성 블록의 값은 `전거/`가 정본이고 `dag_facts.py --render`가 채운다.
# 손으로 고치지 않는다 — 고칠 자리는 전거 항목이다.
# 【생성 상태】
STATES = ("미착수", "진행", "상신중", "예외", "완", "비준", "파킹")
# 【끝】
# 【생성 유형】
KINDS = ("파견", "전개", "싱크", "게이트")
# 【끝】
# 【생성 완결상태】
DONE_STATES = ("완", "비준")
# 【끝】
SINK_SUFFIX = ".z"
DECIDED = "결정됨"
# 【생성 검산모드】
MODES = ("drive", "partial")
# 【끝】

# 【생성 모델】
MODELS = ("sonnet", "opus", "fable", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna")
# 【끝】
# 【생성 노력】
EFFORTS = ("low", "med", "high")
# 【끝】

# 셋으로 가른다: 실제 값 · `—`(명시적 해당 없음) · 빈 칸(누락).
NONE_MARK = "—"
_DASH_TOKENS = {"-", "—", "–", "없음"}

# 【생성 센티널】
TABLE_END = "<!-- 행 끝 -->"
# 【끝】
DECISION_DIR = "결정/"
SETTLEMENT_SUFFIX = "-결산.md"
REPORT_SUFFIX = "-보고.md"
SINK_RETURN_WORDS = (
    "DONE",
    "DONE-비준",
    "귀속불일치",
    "완료미충족",
    "병합충돌",
    "계약이동",
    "대기",
)
VERIFY_RUN_CONTRACT = Path(__file__).resolve().parent.parent / "계약" / "검증런.md"
VERIFY_RUN_FILES = ("동결.md", "장부.md", "종료보고.md")
# verify-rounds 종료보고의 「발견」 절. 제목과 0건 표기의 정본은 verify-rounds SKILL.md
# §7 종료 보고 10항이다(전거/의존.md 의존:verify-rounds-종료보고).
_DISCOVERY_HEADING = re.compile(r"^(#{1,6})[ \t]*(?:\d+\.[ \t]*)?발견[ \t]*$", re.MULTILINE)
_ANY_HEADING = re.compile(r"^(#{1,6})[ \t]")
_DISCOVERY_ITEM = re.compile(r"^(?:- |\d+\. |#{1,6}[ \t]+R\d+-)")
VERIFY_LEDGER_SECTIONS = {
    "본표": re.compile(r"^##[ \t]+라운드[ \t]+1[ \t]+[—–-][ \t]+본표[ \t]*$", re.MULTILINE),
    "결산": re.compile(r"^##[ \t]+라운드[ \t]+1[ \t]+[—–-][ \t]+결산[ \t]*$", re.MULTILINE),
}

# 결산 단계 원장의 값. 순서가 계약이고 각 값의 뜻과 재개 자리는 전거 항목이 진다.
# 원장은 싱크 종류마다 하나이므로 둘을 뭉치지 않는다.
# 【생성 단계원장-노드】
NODE_SETTLEMENT_STAGES = (
    "판정완료",
    "격리커밋완료",
    "병합완료",
    "커밋완료",
    "회수완료",
    "종결",
)
# 【끝】
# 【생성 단계원장-국면】
PHASE_SETTLEMENT_STAGES = ("판정완료", "회수완료", "커밋완료", "종결")
# 【끝】
SETTLED = NODE_SETTLEMENT_STAGES[-1]

# 행 번호 문법. 마디는 숫자이고, 싱크(`z`)와 게이트(`g<번호>`)는 마지막 마디에만 온다.
_SEGMENT = re.compile(r"^\d+$")
_TERMINAL = re.compile(r"^(?:z|g\d+)$")

# 서식의 플레이스홀더 표기. 채워지지 않은 절은 이것만 남는다.
_PLACEHOLDER = re.compile(r"\{[^{}]*\}", re.DOTALL)

# 파견문 최상위 슬롯 `- 정본: <좌표>`. 게이트 결정의 소비가 서는 유일한 자리다.
_CANON_SLOT = re.compile(r"^[ \t]*[-*]?[ \t]*정본[ \t]*:[ \t]*(.*)$", re.MULTILINE)

# 파견문 최상위 슬롯 `- 계약: <좌표>[·<좌표>]`. 역할 계약의 적재가 서는 자리다.
# 콜론 앞에 낱말이 더 붙은 슬롯은 걸리지 않는다.
_CONTRACT_SLOT = re.compile(r"^[ \t]*[-*]?[ \t]*계약[ \t]*:[ \t]*(.*)$", re.MULTILINE)
_CONTRACT_SEP = re.compile(r"[·,]")

# 파견문 최상위 슬롯 `- 불변식: <절대 좌표>[·<절대 좌표>]`. 각 좌표는 현재 런
# 디렉토리의 서브트리 불변식 파일이다.
_INVARIANT_SLOT = re.compile(r"^[ \t]*[-*]?[ \t]*불변식[ \t]*:[ \t]*(.*)$", re.MULTILINE)
_INVARIANT_SEP = re.compile(r"[·,]")
_INVARIANT_NAME = re.compile(r"^불변식(?:-[1-9][0-9]*)?\.md$")
_TOP_LEVEL_SLOT = re.compile(r"^[-*][ \t]+[^\n:]+[ \t]*:", re.MULTILINE)

# 파견문 최상위 슬롯 `- 모델 배정 근거: <한 줄>`. 배정이 그 행에서 도출됐다는
# 기록이 서는 자리다(`references/서식.md` 배정표).
_ASSIGN_SLOT = re.compile(
    r"^[ \t]*[-*]?[ \t]*모델 배정 근거[ \t]*:[ \t]*(.*)$", re.MULTILINE
)


def _cell(raw: str) -> str:
    """칸 하나를 셋 중 하나로 읽는다: 실제 값 · `NONE_MARK` · `""`(누락)."""
    value = raw.strip().strip("`").strip()
    return NONE_MARK if value in _DASH_TOKENS else value


def _has(cell: str) -> bool:
    """실제 값인가. `—`도 빈 칸도 값이 아니다."""
    return bool(cell) and cell != NONE_MARK


@dataclass
class Row:
    id: str
    kind: str
    brief: str
    deps: list[str] = field(default_factory=list)
    signal: str = ""
    model: str = ""
    state: str = ""
    raw: str = ""

    @property
    def scope(self) -> str:
        """이 행이 속한 범위. 최상위 행은 빈 문자열."""
        return self.id.rpartition(".")[0]

    @property
    def leaf(self) -> str:
        """마지막 마디. 산출 이름 규칙이 이 값에서 파생한다."""
        return self.id.rpartition(".")[2]

    @property
    def signals(self) -> list[str]:
        """완료 신호 좌표. 여럿이면 쉼표로 나열되고 전건이 실재해야 한다."""
        return [s for s in (_cell(p) for p in self.signal.split(",")) if _has(s)]

    @property
    def dispatched(self) -> bool:
        """오케가 실제로 쏘는 행인가. 파견문이 없는 행은 쏘지 않는다."""
        return _has(self.brief)


def _table_body(text: str) -> str:
    """행이 사는 범위 — 【센티널 · <!-- 행 끝 --> · 부재 시 전문이 범위】."""
    head, sep, _ = text.partition(TABLE_END)
    return head if sep else text


def parse_rows(text: str) -> list[Row]:
    rows: list[Row] = []
    for line in _table_body(text).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        head = cells[0].strip()
        if head == "행" or _is_separator(cells):
            continue
        if not head:
            continue
        deps = [d for d in (_cell(p) for p in cells[3].split(",")) if _has(d)]
        rows.append(
            Row(
                id=_cell(cells[0]),
                kind=_cell(cells[1]),
                brief=_cell(cells[2]),
                deps=deps,
                signal=_cell(cells[4]),
                model=_cell(cells[5]),
                state=_cell(cells[6]),
                raw=line,
            )
        )
    return rows


def _is_separator(cells: list[str]) -> bool:
    """구분선은 전 칸이 대시다. 첫 칸만 대시인 행과 구별한다."""
    return all(c and set(c) <= set("-: ") for c in cells)


def hidden_rows(rows: list[Row], mode: str = "drive", writer: str | None = None) -> set[str]:
    """발견을 내지 않을 행 — partial에서 살아 있는 남의 전개가 쓰는 중인 서브트리.

    `writer`는 부르는 쪽이 자기를 밝힌 행 번호이고, 그 서브트리는 제외에서 빠진다.
    돌려주는 것은 **발견을 억제할 행 번호**이지 표에서 지울 행이 아니다 — 제외된 행도
    남의 선행으로 지목될 때는 실재하는 것으로 센다.
    """
    if mode != "partial":
        return set()
    out: set[str] = set()
    for r in rows:
        if r.kind == "전개" and r.state == "진행" and r.id != writer:
            out.add(r.id)
            out |= {x.id for x in rows if x.id.startswith(r.id + ".")}
    if writer is not None:
        out -= {writer} | {x.id for x in rows if x.id.startswith(writer + ".")}
    return out


def check_shape(text: str, hidden: set[str] | None = None) -> list[str]:
    """행의 칸 수와 행 번호를 본다.

    `parse_rows`가 칸이 모자란 줄과 행 번호가 빈 줄을 비-행으로 흘려보내므로 여기서
    세운다. 행 여부와 id의 판정은 같은 술어(`_has`)를 쓴다.
    """
    hidden = hidden or set()
    findings: list[str] = []
    for line in _table_body(text).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0].strip() == "행" or _is_separator(cells):
            continue
        if _cell(cells[0]) in hidden:
            continue
        if len(cells) != 7:
            findings.append(
                f"[서식] 행 {cells[0].strip() or '(번호 없음)'}의 칸이"
                f" {len(cells)}개다(7이어야 한다)"
            )
            continue
        if not _has(_cell(cells[0])):
            findings.append(f"[서식] 행 번호가 비어 있다: {line[:60]}")
    return findings


def check_ids(rows: list[Row], hidden: set[str] | None = None) -> list[str]:
    """행 번호의 문법과 유일성."""
    hidden = hidden or set()
    findings: list[str] = []
    seen: dict[str, int] = {}
    for r in rows:
        seen[r.id] = seen.get(r.id, 0) + 1
        if r.id in hidden:
            continue
        parts = r.id.split(".")
        ok = all(_SEGMENT.match(p) for p in parts[:-1]) and (
            _SEGMENT.match(parts[-1]) or _TERMINAL.match(parts[-1])
        )
        if not ok:
            findings.append(
                f"[서식] 행 번호 '{r.id}'가 문법 밖이다"
                " (마디는 숫자, 마지막 마디에만 z·g<번호>가 온다)"
            )
    findings.extend(
        f"[서식] 행 번호 '{rid}'가 {n}번 나온다 — 번호는 유일해야 한다"
        for rid, n in seen.items()
        if n > 1 and rid not in hidden
    )
    return findings


def check_states(rows: list[Row], hidden: set[str] | None = None) -> list[str]:
    hidden = hidden or set()
    findings = []
    for r in rows:
        if r.id in hidden:
            continue
        if r.state not in STATES:
            findings.append(
                f"[어휘] 행 {r.id}의 상태 '{r.state or '(빈 칸)'}'는 닫힌 목록 밖이다:"
                f" {' · '.join(STATES)}"
            )
        # 빈 유형도 발견이다 — 오케는 유형 칸으로 행동을 고른다.
        if r.kind not in KINDS:
            findings.append(
                f"[어휘] 행 {r.id}의 유형 '{r.kind or '(빈 칸)'}'은 닫힌 목록 밖이다:"
                f" {' · '.join(KINDS)}"
            )
    return findings


def _require(r: Row, cell: str, label: str) -> list[str]:
    if _has(cell):
        return []
    what = "빈 칸(누락)" if not cell else "해당 없음(—)"
    return [f"[계약] {r.kind} 행 {r.id} — {label} 칸이 {what}이다. 값이 필요하다"]


def _require_none(r: Row, cell: str, label: str) -> list[str]:
    if cell == NONE_MARK:
        return []
    if not cell:
        return [f"[계약] {r.kind} 행 {r.id} — {label} 칸이 빈 칸이다. 해당 없음은 `—`로 적는다"]
    return [f"[계약] {r.kind} 행 {r.id} — {label} 칸은 `—`이어야 한다: {cell}"]


def check_columns(rows: list[Row], hidden: set[str] | None = None) -> list[str]:
    """행 유형별 칸 계약. 유형이 정한 것과 각 칸의 값이 맞는가."""
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.id in hidden:
            continue
        if r.kind in ("파견", "전개"):
            findings += _require(r, r.brief, "파견문")
            findings += _require(r, r.signal, "완료 신호")
            findings += _require(r, r.model, "모델")
            if r.kind == "전개" and r.state not in DONE_STATES and _has(r.brief):
                brief = r.brief.replace("\\", "/")
                parent = brief.rpartition("/")[0]
                expected = f"{parent}/{r.leaf}{REPORT_SUFFIX}".lstrip("/")
                if expected not in [s.replace("\\", "/") for s in r.signals]:
                    findings.append(
                        f"[계약] 전개 행 {r.id}의 완료 신호에 완료보고가 없다:"
                        f" {r.signal} ('{expected}'이어야 한다)"
                    )
        elif r.kind == "게이트":
            findings += _require_none(r, r.brief, "파견문")
            findings += _require_none(r, r.model, "모델")
            findings += _require(r, r.signal, "완료 신호")
            for sig in r.signals:
                if not sig.startswith(DECISION_DIR):
                    findings.append(
                        f"[계약] 게이트 {r.id}의 완료 신호가 결정 파일이 아니다:"
                        f" {sig} ({DECISION_DIR} 아래여야 한다)"
                    )
        elif r.kind == "싱크":
            filled = [_has(r.brief), _has(r.signal), _has(r.model)]
            if all(filled):
                # 결산 좌표는 파견문 좌표에서 파생한다 — 같은 디렉토리, 같은 마디.
                brief = r.brief.replace("\\", "/")
                parent = brief.rpartition("/")[0]
                want = f"{parent}/{r.leaf}{SETTLEMENT_SUFFIX}".lstrip("/")
                if want not in [s.replace("\\", "/") for s in r.signals]:
                    findings.append(
                        f"[계약] 실행 싱크 {r.id}의 완료 신호가 결산이 아니다:"
                        f" {r.signal} ('{want}'이어야 한다)"
                    )
            elif any(filled):
                findings.append(
                    f"[계약] 싱크 {r.id}이 반쪽이다 — 실행 싱크는 파견문·완료 신호·모델을"
                    f" 함께 갖고, 무작업 싱크는 셋 다 `—`다"
                    f" (파견문 {r.brief or '(빈 칸)'} · 완료 신호 {r.signal or '(빈 칸)'}"
                    f" · 모델 {r.model or '(빈 칸)'})"
                )
            else:
                findings += _require_none(r, r.brief, "파견문")
                findings += _require_none(r, r.signal, "완료 신호")
                findings += _require_none(r, r.model, "모델")
    return findings


def _visible(rows: list[Row], scope: str) -> set[str]:
    """그 범위에서 지목 가능한 행 — 직접 구성원과 각 구성원의 싱크."""
    members = {r.id for r in rows if r.scope == scope}
    return members | {m + SINK_SUFFIX for m in members}


def check_closure(rows: list[Row], hidden: set[str] | None = None) -> list[str]:
    """선행 지목의 범위 폐쇄.

    `known`·`_visible`은 `hidden`을 걷어내지 않는다 — 억제되는 것은 제외된 행
    **자신이 낸** 발견뿐이다.
    """
    hidden = hidden or set()
    findings: list[str] = []
    known = {r.id for r in rows}
    # 아직 펼쳐지지 않은 전개의 싱크는 약속된 행이다 — 수렴 불변식이 그 존재를
    # 보장하므로 미리 지목할 수 있다.
    known |= {r.id + SINK_SUFFIX for r in rows if r.kind == "전개"}
    cache: dict[str, set[str]] = {}
    for r in rows:
        if r.id in hidden:
            continue
        allowed = cache.get(r.scope)
        if allowed is None:
            allowed = _visible(rows, r.scope)
            if r.scope:
                allowed = allowed | {r.scope}
            cache[r.scope] = allowed
        for dep in r.deps:
            if dep not in known:
                findings.append(f"[폐쇄] 행 {r.id}의 선행 {dep}이 파견표에 없다")
            elif dep not in allowed:
                findings.append(
                    f"[폐쇄] 행 {r.id}이 자기 범위 밖을 지목한다: {dep}"
                    f" (범위 '{r.scope or '최상위'}'. 바깥은 싱크로 지목한다)"
                )
    return findings


def _reverse_reachable(rows: list[Row], start: str) -> set[str]:
    deps = {r.id: r.deps for r in rows}
    expanders = {r.id for r in rows if r.kind == "전개"}
    seen: set[str] = set()
    stack = list(deps.get(start, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur in deps:
            stack.extend(deps[cur])
        elif cur.endswith(SINK_SUFFIX) and cur[: -len(SINK_SUFFIX)] in expanders:
            # 아직 펼쳐지지 않은 전개의 약속된 싱크. 그 전개로 이어 간다.
            stack.append(cur[: -len(SINK_SUFFIX)])
    return seen


def _phase_sinks(rows: list[Row]) -> list[str]:
    """마디 없는 싱크 행 — 국면 종결 행. 정확히 하나일 때만 최상위 수렴이 선다."""
    return [r.id for r in rows if r.kind == "싱크" and not r.scope]


def _check_parents(rows: list[Row], hidden: set[str]) -> list[str]:
    """마디 있는 행의 부모가 파견표에 실재하는가.

    부모 없는 서브트리는 수렴 검사의 두 모집단 어디에도 들지 않는다 — 행 `3`이 없는
    채 `3.1`만 남으면 어느 싱크에도 닿지 않는다.
    """
    known = {r.id for r in rows}
    return [
        f"[수렴] 행 {r.id}의 부모 {r.scope}가 파견표에 없다"
        " — 그 서브트리는 어느 싱크에도 수렴하지 않는다"
        for r in rows
        if r.scope and r.scope not in known and r.id not in hidden
    ]


def check_convergence(
    rows: list[Row], mode: str = "drive", hidden: set[str] | None = None
) -> list[str]:
    hidden = hidden or set()
    findings: list[str] = _check_parents(rows, hidden)
    known = {r.id for r in rows}
    for r in rows:
        if r.kind != "전개" or r.id in hidden:
            continue
        sink = r.id + SINK_SUFFIX
        prefix = r.id + "."
        descendants = [x.id for x in rows if x.id.startswith(prefix)]
        if not descendants:
            # 과거 형식은 디렉토리 완료 신호로 서브트리를 약속했다. 현행 전개는
            # 완료보고 파일을 쓰지만, 이 검사는 이미 완결된 과거 파견표도 읽는다.
            if r.state in DONE_STATES and any(s.endswith("/") for s in r.signals):
                findings.append(
                    f"[수렴] 전개 {r.id}이 {r.state}인데 약속한 싱크 {sink}를 만들지 않았다"
                )
            continue
        if sink not in known:
            findings.append(f"[수렴] 전개 {r.id}에 싱크 {sink}가 없다")
            continue
        reachable = _reverse_reachable(rows, sink)
        for d in descendants:
            if d != sink and d not in reachable and d not in hidden:
                findings.append(f"[수렴] 행 {d}이 싱크 {sink}에 도달하지 않는다")

    # 최상위 층을 소유한 전개 행은 파견표에 없어 위 순회로 닿지 않는다. 국면 싱크를
    # 루트로 삼아 같은 검사를 돌린다.
    tops = _phase_sinks(rows)
    if len(tops) > 1:
        findings.append(
            f"[수렴] 국면 종결 싱크가 둘 이상이다: {' · '.join(sorted(tops))}"
            " — 최상위 수렴점은 하나다"
        )
        return findings
    if not tops:
        if mode == "drive" and rows:
            findings.append("[수렴] 국면 종결 싱크가 없다 — 최상위 행들이 수렴할 자리가 없다")
        return findings
    phase_sink = tops[0]
    reachable = _reverse_reachable(rows, phase_sink)
    for r in rows:
        if r.scope or r.id == phase_sink or r.id in hidden:
            continue
        if r.id not in reachable:
            findings.append(f"[수렴] 행 {r.id}이 싱크 {phase_sink}에 도달하지 않는다")
    return findings


def check_cycle(rows: list[Row], hidden: set[str] | None = None) -> list[str]:
    """순환 부재.

    `hidden`은 다른 검사와 같은 계약이다 — 제외된 행이 **낸** 간선은 검사 그래프에
    들지 않는다. 살아 있는 전개의 서브트리 안 순환은 그 전개의 `--writer`
    자기검사가 잡는다.
    """
    hidden = hidden or set()
    graph = {r.id: [d for d in r.deps if d] for r in rows if r.id not in hidden}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {rid: WHITE for rid in graph}

    def dfs(node: str, stack: list[str]) -> list[str] | None:
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                return stack[stack.index(nxt):] + [nxt]
            if color[nxt] == WHITE:
                found = dfs(nxt, stack)
                if found:
                    return found
        color[node] = BLACK
        stack.pop()
        return None

    for rid in graph:
        if color[rid] == WHITE:
            cycle = dfs(rid, [])
            if cycle:
                return [f"[순환] {' → '.join(cycle)}"]
    return []


def _is_empty(target: Path) -> bool:
    if target.is_dir():
        return not any(target.iterdir())
    return target.stat().st_size == 0


def check_signals(rows: list[Row], run_dir: Path, hidden: set[str] | None = None) -> list[str]:
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.state not in DONE_STATES or r.id in hidden:
            continue
        for sig in r.signals:
            target = run_dir / sig
            if not target.exists():
                findings.append(
                    f"[실재] 행 {r.id}이 {r.state}인데 완료 신호가 없다: {sig}"
                )
            elif _is_empty(target):
                # 실재는 충족이 아니다 — 소멸한 에이전트가 껍데기를 남긴다.
                findings.append(
                    f"[실재] 행 {r.id}이 {r.state}인데 완료 신호가 비어 있다: {sig}"
                )
    return (
        findings
        + _check_verify_run_artifacts(rows, run_dir, hidden)
        + _check_discovery_followup(rows, run_dir, hidden)
        + _check_settlement_status(rows, run_dir, hidden)
        + _check_settlement_stage(rows, run_dir, hidden)
    )


def _contract_coords(text: str) -> list[str]:
    """파견문의 `계약:` 슬롯을 좌표 목록으로 읽는다."""
    return [
        part
        for match in _CONTRACT_SLOT.finditer(text)
        for raw in _CONTRACT_SEP.split(match.group(1))
        if (part := raw.strip().strip("`").strip())
    ]


def _uses_verify_run_contract(r: Row, run_dir: Path) -> bool:
    brief = run_dir / r.brief
    if not brief.is_file():
        return False
    text = brief.read_text(encoding="utf-8", errors="replace")
    return any(
        _same_path(_contract_path(coord, run_dir), VERIFY_RUN_CONTRACT)
        for coord in _contract_coords(text)
    )


def _check_verify_run_artifacts(
    rows: list[Row], run_dir: Path, hidden: set[str] | None = None
) -> list[str]:
    """완결 검증런의 세 정본과 장부 라운드 1 구조를 검사한다."""
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.state not in DONE_STATES or r.id in hidden or not r.dispatched:
            continue
        if not _uses_verify_run_contract(r, run_dir):
            continue
        reports = [run_dir / sig for sig in r.signals if Path(sig).name == "종료보고.md"]
        if not reports:
            findings.append(
                f"[실재] 검증런 행 {r.id}이 {r.state}인데 완료 신호에 종료보고.md가 없다"
            )
            continue
        output_dir = reports[0].parent
        for name in VERIFY_RUN_FILES:
            target = output_dir / name
            if not target.is_file():
                findings.append(
                    f"[실재] 검증런 행 {r.id}이 {r.state}인데 필수 산출이 없다: {target}"
                )
            elif _is_empty(target):
                findings.append(
                    f"[실재] 검증런 행 {r.id}이 {r.state}인데 필수 산출이 비어 있다: {target}"
                )
        ledger = output_dir / "장부.md"
        if not ledger.is_file() or _is_empty(ledger):
            continue
        ledger_text = ledger.read_text(encoding="utf-8", errors="replace")
        for label, pattern in VERIFY_LEDGER_SECTIONS.items():
            if not pattern.search(ledger_text):
                findings.append(
                    f"[실재] 검증런 행 {r.id}이 {r.state}인데 장부에 라운드 1 {label}가 없다: {ledger}"
                )
    return findings


def _discovery_count(report_text: str) -> int:
    """종료보고 「발견」 절의 항목 수. 절이 없거나 본문이 「없음」이면 0."""
    match = _DISCOVERY_HEADING.search(report_text)
    if not match:
        return 0
    level = len(match.group(1))
    body: list[str] = []
    for line in report_text[match.end():].split("\n"):
        heading = _ANY_HEADING.match(line)
        if heading and len(heading.group(1)) <= level:
            break
        body.append(line)
    text = "\n".join(body).strip()
    if not text or text.startswith("없음"):
        return 0
    items = [line for line in body if _DISCOVERY_ITEM.match(line)]
    return len(items) if items else 1


def _check_discovery_followup(
    rows: list[Row], run_dir: Path, hidden: set[str] | None = None
) -> list[str]:
    """완결 검증런의 종료보고에 발견이 있으면 같은 층에 그것을 정본으로 싣는 전개가 있어야 한다."""
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.state not in DONE_STATES or r.id in hidden or not r.dispatched:
            continue
        if not _uses_verify_run_contract(r, run_dir):
            continue
        reports = [sig for sig in r.signals if Path(sig).name == "종료보고.md"]
        if not reports or not (run_dir / reports[0]).is_file():
            continue
        count = _discovery_count(
            (run_dir / reports[0]).read_text(encoding="utf-8", errors="replace")
        )
        if count == 0:
            continue
        consumed = False
        for other in rows:
            if other.kind != "전개" or other.scope != r.scope or not other.dispatched:
                continue
            brief = run_dir / other.brief
            if not brief.is_file():
                continue
            text = brief.read_text(encoding="utf-8", errors="replace")
            if _brief_mentions(text, reports[0]):
                consumed = True
                break
        if not consumed:
            findings.append(
                f"[실재] 검증런 행 {r.id}의 종료보고 「발견」 {count}건인데 "
                f"그 종료보고를 정본으로 싣는 검토전개 행(전개)이 같은 층에 없다: {reports[0]}"
            )
    return findings


def _check_settlement_status(
    rows: list[Row], run_dir: Path, hidden: set[str] | None = None
) -> list[str]:
    """완결 싱크의 반환과 결산 frontmatter `상태`가 같은가."""
    hidden = hidden or set()
    expected_by_state = {"완": "DONE", "비준": "DONE-비준"}
    findings: list[str] = []
    for r in rows:
        if r.kind != "싱크" or r.state not in DONE_STATES or r.id in hidden:
            continue
        expected = expected_by_state[r.state]
        for sig in r.signals:
            if not sig.endswith(SETTLEMENT_SUFFIX):
                continue
            target = run_dir / sig
            if not target.is_file():
                continue
            status = _frontmatter(
                target.read_text(encoding="utf-8", errors="replace"), "상태"
            )
            if status != expected:
                findings.append(
                    f"[실재] 싱크 {r.id}이 {r.state}인데 결산 상태가"
                    f" '{status or '없음'}'이다({expected}이어야 한다): {sig}"
                )
    return findings


def check_sink_return(
    rows: list[Row], run_dir: Path, row_id: str, return_word: str
) -> list[str]:
    """실제 싱크 반환을 상태 열로 접기 전에 결산 frontmatter와 대조한다."""
    findings: list[str] = []
    matches = [r for r in rows if r.id == row_id]
    if not matches:
        return [f"[반환] 싱크 행 {row_id}이 파견표에 없다"]
    if len(matches) > 1:
        return [f"[반환] 행 번호 {row_id}이 유일하지 않다"]
    sink = matches[0]
    if sink.kind != "싱크":
        return [f"[반환] 행 {row_id}의 유형이 싱크가 아니다: {sink.kind}"]
    if return_word not in SINK_RETURN_WORDS:
        findings.append(
            f"[반환] 싱크 {row_id}의 첫 낱말 '{return_word}'는 닫힌 목록 밖이다:"
            f" {' · '.join(SINK_RETURN_WORDS)}"
        )

    settlements = [sig for sig in sink.signals if sig.endswith(SETTLEMENT_SUFFIX)]
    if not settlements:
        findings.append(f"[반환] 싱크 {row_id}의 완료 신호에 결산이 없다")
        return findings
    for sig in settlements:
        target = run_dir / sig
        if not target.is_file():
            findings.append(f"[반환] 싱크 {row_id}의 결산이 없다: {sig}")
            continue
        if _is_empty(target):
            findings.append(f"[반환] 싱크 {row_id}의 결산이 비어 있다: {sig}")
            continue
        text = target.read_text(encoding="utf-8", errors="replace")
        status = _frontmatter(text, "상태")
        if status != return_word:
            findings.append(
                f"[반환] 싱크 {row_id}의 첫 낱말은 '{return_word}'인데 결산 상태가"
                f" '{status or '없음'}'이다: {sig}"
            )
        if return_word in ("DONE", "DONE-비준"):
            stage = _frontmatter(text, "단계")
            if stage != SETTLED:
                findings.append(
                    f"[반환] 싱크 {row_id}이 {return_word}인데 결산 단계가"
                    f" '{stage or '없음'}'이다({SETTLED}이어야 한다): {sig}"
                )
    return findings


def _check_settlement_stage(
    rows: list[Row], run_dir: Path, hidden: set[str] | None = None
) -> list[str]:
    """완결된 싱크의 결산 단계가 원장의 종착값(`SETTLED`)인가.

    결산은 단계 원장이라 실재만으로는 어디까지 갔는지 알 수 없다. 종착값을 여기
    적지 않는다 — `SETTLED`가 원장에서 파생되므로 문면에 옮기면 정본이 둘이 된다.
    """
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.kind != "싱크" or r.state not in DONE_STATES or r.id in hidden:
            continue
        for sig in r.signals:
            if not sig.endswith(SETTLEMENT_SUFFIX):
                continue
            target = run_dir / sig
            if not target.is_file():
                continue  # 부재는 위 실재 검사가 이미 세었다
            stage = _frontmatter(target.read_text(encoding="utf-8", errors="replace"), "단계")
            if stage != SETTLED:
                findings.append(
                    f"[실재] 싱크 {r.id}이 {r.state}인데 결산 단계가"
                    f" '{stage or '없음'}'이다({SETTLED}이어야 한다): {sig}"
                )
    return findings


def check_briefs(rows: list[Row], run_dir: Path, hidden: set[str] | None = None) -> list[str]:
    """파견문이 실재하는가, 그리고 역할 계약과 배정 도출을 싣는가."""
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if not r.dispatched or r.id in hidden:
            continue
        brief = run_dir / r.brief
        if not brief.exists():
            findings.append(f"[실재] 행 {r.id}의 파견문이 없다: {r.brief}")
            continue
        if not brief.is_file():
            # 디렉토리를 열면 아래 read_text가 OSError를 올려 검산이 통째로 죽는다.
            findings.append(f"[실재] 행 {r.id}의 파견문 좌표가 파일이 아니다: {r.brief}")
            continue
        text = brief.read_text(encoding="utf-8", errors="replace")
        findings += _check_contract(r, text, run_dir)
        findings += _check_invariants(r, rows, text, run_dir)
        findings += _check_assignment(r, text)
    return findings


def _check_assignment(r: Row, text: str) -> list[str]:
    """파견문이 자기 모델·노력의 도출을 싣는가.

    배정 이탈은 행마다 새로 도출한다 — 앞선 행의 이탈은 선례가 되지 못하고
    임계값 대입은 도출이 아니다(`references/서식.md` 배정표). 슬롯이 비면 그
    도출이 어디에도 없다. 서식 플레이스홀더만 남은 슬롯은 빈 슬롯이다.
    도출이 배정표 문언에 서는지는 정합성 렌즈가 본다.
    """
    for m in _ASSIGN_SLOT.finditer(text):
        if _PLACEHOLDER.sub("", m.group(1)).strip():
            return []
    return [f"[실재] 행 {r.id}의 파견문에 `모델 배정 근거:` 슬롯이 없다: {r.brief}"]


def _check_contract(r: Row, text: str, run_dir: Path) -> list[str]:
    """파견문의 `계약:` 슬롯이 실재하는 계약 파일을 싣는가.

    계약 문면은 파견문에 전사되지 않고 `계약/` 아래 산다(`references/서식.md`
    「계약 자산」). 슬롯이 비면 그 에이전트는 자기 역할 계약 없이 돈다.
    이 검사가 보는 것은 슬롯의 존재와 좌표의 실재까지다 — 역할에 맞는 계약이
    실렸는지는 배치표를 읽는 전개와 정합성 렌즈의 몫이다.
    """
    coords = _contract_coords(text)
    if not coords:
        return [f"[실재] 행 {r.id}의 파견문에 `계약:` 슬롯이 없다: {r.brief}"]
    return [
        f"[실재] 행 {r.id}의 계약 좌표가 파일로 실재하지 않는다: {c}"
        for c in coords
        if not _contract_path(c, run_dir).is_file()
    ]


def _contract_path(coord: str, run_dir: Path) -> Path:
    """계약 좌표는 절대 경로가 정본이다. 상대 경로는 런 디렉토리 기준으로 읽는다."""
    p = Path(coord)
    return p if p.is_absolute() else run_dir / p


def _slot_coords(pattern: re.Pattern[str], text: str, sep: re.Pattern[str]) -> list[str]:
    """한 줄 좌표 슬롯을 좌표 목록으로 읽는다."""
    return [
        part
        for match in pattern.finditer(text)
        for raw in sep.split(match.group(1))
        if (part := _PLACEHOLDER.sub("", raw).strip().strip("`").strip())
    ]


def _invariant_path(run_dir: Path, owner: str) -> Path:
    """전개 행 번호에서 그 서브트리의 기본 불변식 좌표를 파생한다."""
    parts = owner.split(".")
    parent = run_dir / "행"
    for part in parts[:-1]:
        parent /= f"{part}.d"
    return parent / f"{parts[-1]}.d" / "불변식.md"


def _expected_invariants(r: Row, rows: list[Row], run_dir: Path) -> list[Path]:
    """행이 승계해야 하는 0번·상위 전개의 기본 불변식 전건."""
    expected = [_invariant_path(run_dir, "0")]
    parts = r.id.split(".")
    by_id = {row.id: row for row in rows}
    for depth in range(1, len(parts)):
        owner = ".".join(parts[:depth])
        if (parent := by_id.get(owner)) and parent.kind == "전개":
            expected.append(_invariant_path(run_dir, owner))
    return expected


def _slot_block(text: str, name: str) -> str:
    """최상위 `- <name>:` 슬롯의 값과 이어지는 들여쓴 블록."""
    start_re = re.compile(rf"^[-*][ \t]+{re.escape(name)}[ \t]*:[ \t]*(.*)$", re.MULTILINE)
    match = start_re.search(text)
    if not match:
        return ""
    next_slot = _TOP_LEVEL_SLOT.search(text, match.end())
    end = next_slot.start() if next_slot else len(text)
    return match.group(1) + text[match.end():end]


def _same_path(left: Path, right: Path) -> bool:
    """실재하지 않는 경로도 비교할 수 있게 비엄격 절대 좌표로 맞춘다."""
    return left.resolve(strict=False) == right.resolve(strict=False)


def _mentions_coord(block: str, coord: str) -> bool:
    """좌표의 두 구분자 표기를 같은 문자열로 본다."""
    normalized = block.replace("\\", "/")
    return coord.replace("\\", "/") in normalized


def _check_invariants(r: Row, rows: list[Row], text: str, run_dir: Path) -> list[str]:
    """파견문이 자기 서브트리의 불변식 정본을 승계하고 실제로 적재하는가."""
    raw_coords = _slot_coords(_INVARIANT_SLOT, text, _INVARIANT_SEP)
    if not raw_coords:
        return [f"[실재] 행 {r.id}의 파견문에 `불변식:` 슬롯이 없다: {r.brief}"]

    findings: list[str] = []
    paths: list[Path] = []
    run_root = run_dir.resolve(strict=False)
    expected = _expected_invariants(r, rows, run_dir)
    allowed_parents = [path.parent.resolve(strict=False) for path in expected]
    for coord in raw_coords:
        path = Path(coord)
        if not path.is_absolute():
            findings.append(f"[실재] 행 {r.id}의 불변식 좌표가 절대 경로가 아니다: {coord}")
            path = run_dir / path
        resolved = path.resolve(strict=False)
        paths.append(resolved)
        try:
            resolved.relative_to(run_root)
        except ValueError:
            findings.append(f"[실재] 행 {r.id}의 불변식 좌표가 현재 런 밖이다: {coord}")
        if (
            not _INVARIANT_NAME.fullmatch(resolved.name)
            or not any(_same_path(resolved.parent, parent) for parent in allowed_parents)
        ):
            findings.append(
                f"[계약] 행 {r.id}의 좌표가 적용 서브트리의 불변식이 아니다: {coord}"
            )
        if not resolved.is_file():
            findings.append(f"[실재] 행 {r.id}의 불변식 좌표가 파일로 실재하지 않는다: {coord}")
        elif resolved.stat().st_size == 0:
            findings.append(f"[실재] 행 {r.id}의 불변식 파일이 비어 있다: {coord}")

    for expected_path in expected:
        if not any(_same_path(path, expected_path) for path in paths):
            findings.append(
                f"[계약] 행 {r.id}이 상위 불변식을 승계하지 않았다: {expected_path}"
            )

    read_block = _slot_block(text, "읽기 목록")
    budget_block = _slot_block(text, "예산")
    for coord in raw_coords:
        if not _mentions_coord(read_block, coord):
            findings.append(f"[계약] 행 {r.id}의 불변식 좌표가 읽기 목록에 없다: {coord}")
        if "--files" not in budget_block or not _mentions_coord(budget_block, coord):
            findings.append(f"[계약] 행 {r.id}의 불변식 좌표가 예산 `--files`에 없다: {coord}")
    return findings


def _decision_body(text: str) -> str:
    """결정 파일의 사용자 축자 절. 「메인 결정」은 다른 절이다.

    플레이스홀더를 걷어낸 뒤 판정한다 — 결정 전 파일은 그 절에 `{…}`만 담고 있다.
    """
    body: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.startswith("## 결정")
            continue
        if inside:
            body.append(line)
    return _PLACEHOLDER.sub("", "\n".join(body)).strip()


def _frontmatter(text: str, key: str) -> str | None:
    """선두 `---` 블록에서 한 키를 읽는다. 블록이나 키가 없으면 None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        name, sep, value = line.partition(":")
        if sep and name.strip() == key:
            return value.strip()
    return None


def _check_gate_consumers(rows: list[Row], gate: Row, run_dir: Path) -> list[str]:
    """게이트 결정에 소비자가 배정됐는가.

    게이트를 선행으로 지목해 **일하는** 행은 전개여야 하고, 그 파견문에 그 게이트의
    결정 파일 좌표가 실려야 한다. 싱크와 게이트 후행은 이 계약 밖이다.
    """
    findings: list[str] = []
    for r in rows:
        if gate.id not in r.deps or r.kind in ("싱크", "게이트"):
            continue
        if r.kind != "전개":
            findings.append(
                f"[계약] 게이트 {gate.id}을 선행으로 지목한 행 {r.id}의 유형이"
                f" '{r.kind}'이다 — 전개여야 한다"
                f" (결정을 소비하려면 행을 만들 권한이 필요하다)"
            )
            continue
        if not r.dispatched:
            continue
        brief = run_dir / r.brief
        if not brief.is_file():
            # 파견문 부재는 ⑦이 보고한다. 여기서 겹쳐 세지 않는다.
            continue
        text = brief.read_text(encoding="utf-8", errors="replace")
        for sig in gate.signals:
            if not _brief_mentions(text, sig):
                findings.append(
                    f"[결정] 게이트 {gate.id}의 결정 좌표가 후행 전개 {r.id}의"
                    f" 파견문 `정본:` 슬롯에 없다: {sig}"
                    f" (읽기 목록·임무의 언급은 소비가 아니다)"
                )
    return findings


def _canon_slots(text: str) -> list[str]:
    """파견문 최상위 `정본:` 슬롯의 값들. 슬롯이 없으면 빈 목록.

    소비 계약이 지목하는 자리는 이 슬롯 하나다(`references/서식.md` 칸 계약).
    """
    return [m.group(1).strip() for m in _CANON_SLOT.finditer(text)]


def _brief_mentions(text: str, coord: str) -> bool:
    """파견문의 `정본:` 슬롯이 그 좌표를 싣고 있는가.

    **슬롯 값 안에서만 찾는다** — 읽기 목록·임무·주석의 언급은 소비가 아니다.

    슬롯의 좌표는 런 디렉토리 절대 경로로 변환되므로 꼬리 일치로 보고, 구분자는 두
    표기를 다 받는다.
    """
    return any(
        coord in value or coord.replace("/", "\\") in value
        for value in _canon_slots(text)
    )


def check_gates(
    rows: list[Row], run_dir: Path, mode: str = "drive", hidden: set[str] | None = None
) -> list[str]:
    hidden = hidden or set()
    findings: list[str] = []
    for r in rows:
        if r.kind != "게이트" or r.id in hidden:
            continue
        if mode == "drive":
            # 결정 파일을 낳는 행이 선행 사슬에 없으면 그 게이트는 영원히 기다린다.
            ancestors = _reverse_reachable(rows, r.id)
            produced = {
                s for x in rows if x.id in ancestors for s in x.signals
            }
            for sig in r.signals:
                if sig not in produced:
                    findings.append(
                        f"[계약] 게이트 {r.id}의 결정 파일을 낳는 행이 선행 사슬에 없다:"
                        f" {sig} (게이트 앞 행의 완료 신호에 더한다)"
                    )
            findings += _check_gate_consumers(rows, r, run_dir)
        if r.state not in DONE_STATES:
            continue
        for sig in r.signals:
            target = run_dir / sig
            if not target.is_file():
                continue
            text = target.read_text(encoding="utf-8", errors="replace")
            if not _decision_body(text):
                findings.append(
                    f"[결정] 게이트 {r.id}이 {r.state}인데 결정 절이 비어 있다: {sig}"
                )
            state = _frontmatter(text, "상태")
            if state != DECIDED:
                findings.append(
                    f"[결정] 게이트 {r.id}이 {r.state}인데 결정 파일 상태가"
                    f" '{state or '없음'}'이다({DECIDED}이어야 한다): {sig}"
                )
    return findings


def ready_rows(rows: list[Row]) -> list[Row]:
    """파견 직전 행 — 미착수이고 선행이 전부 완결이다."""
    state = {r.id: r.state for r in rows}
    return [
        r for r in rows
        if r.state == "미착수"
        and all(state.get(d) in DONE_STATES for d in r.deps)
    ]


def check_drive(rows: list[Row]) -> list[str]:
    """파견 직전 행의 실행 좌표. 모델 열은 Agent 인자가 되는 두 낱말이다."""
    findings: list[str] = []
    for r in ready_rows(rows):
        if not r.dispatched:
            continue
        parts = r.model.split()
        if len(parts) != 2 or parts[0] not in MODELS or parts[1] not in EFFORTS:
            findings.append(
                f"[운전] 행 {r.id}은 파견 직전인데 모델 열이 '{r.model or '(빈 칸)'}'이다"
                f" — `모델 노력` 두 낱말이어야 한다"
                f" (모델: {' · '.join(MODELS)} / 노력: {' · '.join(EFFORTS)})"
            )
    return findings


def run(text: str, run_dir: Path, mode: str = "drive", writer: str | None = None) -> list[str]:
    rows = parse_rows(text)
    hidden = hidden_rows(rows, mode, writer)
    findings = (
        check_shape(text, hidden)
        + check_ids(rows, hidden)
        + check_states(rows, hidden)
        + check_columns(rows, hidden)
        + check_closure(rows, hidden)
        + check_convergence(rows, mode, hidden)
        + check_cycle(rows, hidden)
        + check_signals(rows, run_dir, hidden)
        + check_briefs(rows, run_dir, hidden)
        + check_gates(rows, run_dir, mode, hidden)
    )
    if mode == "drive":
        findings += check_drive(rows)
    return findings


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--table", required=True, help="파견표.md 경로")
    p.add_argument("--run-dir", help="런 디렉토리(기본: 파견표의 부모)")
    p.add_argument(
        "--mode", choices=MODES, default="drive",
        help="drive(기본, 오케 소비 전 완성 계약) · partial(전개가 표를 작성하는 동안)",
    )
    p.add_argument(
        "--writer",
        help="partial 전용. 지금 표를 쓰는 행 번호 — 그 서브트리는 제외에서 빠진다",
    )
    p.add_argument(
        "--sink-return",
        nargs=2,
        metavar=("행번호", "첫낱말"),
        help="싱크 반환 전용. 실제 반환 첫 낱말을 결산 상태·단계와 대조한다",
    )
    p.add_argument(
        "--ready",
        action="store_true",
        help="무발견일 때 운전 정보를 덧낸다 — 파견 직전 행의 표 줄과 진행·상신중·예외 행 번호",
    )
    args = p.parse_args(argv)
    if args.writer and args.mode != "partial":
        p.error("--writer는 --mode partial에서만 쓴다")
    if args.writer and args.sink_return:
        p.error("--writer와 --sink-return은 함께 쓰지 않는다")
    if args.ready and args.sink_return:
        p.error("--ready와 --sink-return은 함께 쓰지 않는다")
    table = Path(args.table)
    run_dir = Path(args.run_dir) if args.run_dir else table.parent
    text = table.read_text(encoding="utf-8")
    if args.sink_return:
        row_id, return_word = args.sink_return
        findings = check_sink_return(parse_rows(text), run_dir, row_id, return_word)
    else:
        findings = run(text, run_dir, args.mode, args.writer)
    if not findings:
        # 돌린 검사만 열거한다. 재지 않은 것은 이름도 올리지 않는다.
        if args.sink_return:
            row_id, return_word = args.sink_return
            print(f"[dag_check] 무발견 (싱크 반환: {row_id} · {return_word})")
            return 0
        if args.mode == "drive":
            checked = "서식·어휘·칸 계약·폐쇄·수렴·순환·좌표 실재·게이트 결정·운전"
        else:
            # partial의 ⑤는 국면 종결 싱크의 부재를, ⑧은 완결분 밖을 미룬다.
            checked = (
                "서식·어휘·칸 계약·폐쇄·수렴(국면 종결 싱크 부재 유보)·순환"
                "·좌표 실재·게이트 결정(완결분 축자·상태)"
            )
        hidden = hidden_rows(parse_rows(text), args.mode, args.writer)
        scope = f" · 제외 서브트리 {' · '.join(sorted(hidden))}" if hidden else ""
        print(f"[dag_check] 무발견 ({args.mode}: {checked}{scope})")
        if args.ready:
            rows = parse_rows(text)
            ready = ready_rows(rows)
            print(f"[dag_check] ready {len(ready)}행 (미착수·선행 완결)")
            for r in ready:
                print(r.raw)
            live = [r for r in rows if r.state == "진행"]
            print(f"[dag_check] 진행 {len(live)}행")
            for r in live:
                print(r.raw)
            for label in ("상신중", "예외"):
                ids = [r.id for r in rows if r.state == label]
                tail = ": " + " · ".join(ids) if ids else ""
                print(f"[dag_check] {label} {len(ids)}행{tail}")
        return 0
    for f in findings:
        print(f"[dag_check] {f}")
    print(f"[dag_check] 발견 {len(findings)}건")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
