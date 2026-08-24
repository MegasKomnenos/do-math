"""전거 렌더·검사 — 한 사실이 한 자리에만 살게 하는 도구.

값을 담지 않는다. `전거/`를 읽어 인용 자리를 채우고, 채워진 것이 어긋나지 않았는지
검사한다. 런타임에 적재되지 않는다 — 읽는 주체는 이 스킬을 개정하는 자뿐이고, 값은
렌더로 소비 자리에 밀려 나가 커밋된다. 검산 도구가 자기가 지키는 산문에 런타임
의존을 갖지 않는다.

**이름 주의** — `dag_check`의 것은 **파견표 검산 ①~⑨**이고 여기 것은 **전거 검사
A~E**다. 같은 「검사」라는 낱말이 두 체계를 가리키지 않도록 번호 체계를 갈랐다.
`dag_check`는 런의 파견표를 재고, `dag_facts`는 스킬 자신의 파일을 잰다.
**재지 않는 것 하나를 밝혀 둔다.** 「`전거/의존.md`의 `딛는 자리`가 실제로 그
항목의 정본을 딛는가」는 A~E 어느 검사도 재지 않는다. E가 보는 것은
`전거/의존.md`가 실은 좌표까지다.

A 미해결 인용 — 인용된 ID의 항목이 전거에 없다. 렌더는 그 자리를 건드리지 않는다.
B 이중 정본 — 한 ID에 항목이 둘.
C 렌더 불일치 — `--render`가 바꿀 자리가 남아 있다.
D 형태 — 항목·블록·괄호가 문법에 어긋나거나, 요지가 그 자리에 실릴 수 없다.
  **D를 낸 파일은 렌더가 통째로 건드리지 않는다.**
E 역포인터 — 의존 대장의 좌표가 파일로 서지 않거나, 대장 항목이 「딛는 자리」를 싣지
  않았다. 재는 좌표는 「딛는 자리」 전건과 저장소 안이 정본인 「정본」이다.

**E가 다른 넷과 방향이 반대다.** A~D는 이 스킬 안이 정본인 사실을 지킨다 — 인용이
ID로 서므로 `grep ID`가 영향 범위를 낸다. **정본이 스킬 밖이면 그 장치가 없다.**
정본을 고치는 사람이 이 저장소를 보지 않거나, 정본이 주석을 못 받는 형식이라 그 자리에
포인터를 남길 수 없다. 그래서 `전거/의존.md`가 방향을 뒤집어 딛는 자리를 싣고, E가 그
좌표의 실재를 지킨다. 좌표가 낡으면 대장이 가리키는 곳에 아무것도 없어, 정본이
바뀌었을 때 무엇이 깨지는지 찾을 길이 사라진다.

D가 없으면 형태 위반이 예외가 아니라 **조용히 틀린 답**으로 나온다. 실측된 것들이다:
요지가 헤딩과 떨어지면 값이 빈 튜플이 되어 옳던 상수를 덮어썼고, 닫히지 않은 블록이
뒤의 마커를 삼켜 그 사이 소스를 지웠고, 요지의 역슬래시가 파이썬 문자열 안에서
이스케이프로 먹혀 값이 갈렸다. 전부 `--check`가 무발견을 냈다.

**자리 층위 D의 차단은 파일 층위다.** 어긋난 자리만 건너뛰고 스캔을 이어 가면 다음
여는 마커가 앞 블록의 대입과 끝 마커를 자기 것으로 삼아 값을 덮는다(실측: `STATES`가
유형 어휘로 덮이고 exit 0). 검출은 차단이 아니므로 그 파일의 렌더를 통째로 버리고,
멈췄다는 사실은 `D 차단`이 함께 낸다 — 자리만 가리키면 같은 파일의 다른 인용·생성
블록이 멎은 것을 못 본다. 항목 층위 D(요지 결손 등)는 마커를 깨뜨리지 않으므로
그 항목의 인용 자리만 막고 파일은 렌더된다.

`--render`는 발견이 있으면 1을 낸다. 발견을 내면서 0을 내면 렌더 뒤에 곧바로 커밋하는
자리가 초록으로 읽는다.

표시 없는 사본(등재 없이 손으로 옮겨 적은 것)은 A~D가 잡지 못한다. 규율이 실제로
새는지 보고 나서 전열거 스캔을 넣는다.

## 항목

`전거/` 아래에만 산다(하위 디렉토리 포함 — 적재와 스캔이 같은 범위를 본다). 괄호는
U+3010/3011이고, 아래 예시에서는 `<<ID>>`로 적는다. U+27E6/27E7을 쓰던 초기 괄호는
cp949 밖 코드포인트라 Windows 콘솔·도구를 거치며 깨졌다 — 괄호를 다시 고를 일이
있으면 KS X 1001 안에서 고른다.

    ## <<상태>> 파견표 상태 어휘
    요지: 미착수 · 진행 · 상신중 · 예외 · 완 · 비준 · 파킹
    기계값: {"sonnet": 150_000}      (선택)

    <본문>

`기계값:` 줄이 없으면 요지를 ` · `로 갈라 문자열 튜플로 낸다. 있으면 그 줄이 파이썬
리터럴 그대로다. **두 줄은 헤딩에 붙어야 한다** — 사이에 빈 줄이 들어가면 본문으로
밀리고, D가 그것을 낸다.

## 인용 셋

| 형태 | 저자가 쓰는 것 | 받는 것 |
|---|---|---|
| 인라인 | `<<ID>>` | `<<ID · 요지>>` |
| 블록 | ` ```전거 ID ` 울타리 | 요지 줄 + 본문(`- _경계_` 류 제외) |
| 파이썬 생성 블록 | `# <<생성 ID>>` … `# <<끝>>` | 대입 이름은 보존하고 값만 |

`- _경계_`·`- _실패 유형_` 류는 등록소를 읽는 개정자만 본다. 소비 자리로
밀려 나가는 것은 사실이지 그 사실에 붙인 주석이 아니므로 블록이 투영하지 않는다.

저자는 ID만 쓴다 — 첫 ` · ` 뒤부터 닫는 괄호까지는 도구 소유 구간이라 요지를 손으로
쓰는 길이 없다. 블록은 기계값 줄을 싣지 않는다: 산문 자리에 파이썬 리터럴이 섞이면
두 표기 중 어느 쪽이 정본인지 눈으로 갈리지 않는다.

**인라인 인용에는 이스케이프가 없다.** 생성 블록은 `_pystr`로 리터럴을 만들지만
인라인은 요지를 그 자리에 날것으로 써 넣는다. **위험은 자리의 성질이다** — 파이썬
문자열 리터럴 안에서 따옴표는 소스를 깨뜨리고 역슬래시는 이스케이프로 먹히므로 요지가
그 둘을 담으면 D가 막는다. 주석·도크스트링은 이스케이프가 없어 받는다(`tokenize`로
가른다). 마크다운에는 대응 검사가 없다 — 요지가 인라인 HTML을 담으면 산문 자리에서
렌더가 그 원소를 지우고, 백틱을 담은 요지를 코드스팬 안에 인용하면 문면이 깨진다. 둘
다 `--check`가 조용하다. 백틱을 담지 않은 요지는 인용 자리를 코드스팬으로 감싸 앞의
위험을 막는다 — `전거/실행.md`의 `센티널` 인용이 그 자리다.

**`기계값:`이 따로 드는 항목은 요지와의 정합을 도구가 보지 않는다.** 요지만 고치면
상수는 그대로이고 `--check`가 무발견을 낸다. 두 표기가 기계로 이어지는 항목은 시험이
붙든다(`tests/test_dag_facts.py`의 `test_기계값이_요지와_어긋나지_않는다`).

**생성 블록은 이름 하나에 대입하는 문 하나만 담는다.** 렌더가 그 안을 통째로 다시
쓰므로 나머지는 전부 지워진다. 주석 판별은 `tokenize`가 하므로 **줄 끝에 붙은 주석도**
걸린다 — 1b가 옮긴 상수의 후행 주석 열하나가 그 형태였다. 전거 블록의 닫는 자리는 울타리
길이로 정하고(CommonMark), 안에 열린 채 남은 울타리가 있으면 남의 닫는 자리를 삼킨
것이라 D가 막는다.

**이 파일과 `tests/test_dag_facts.py`는 괄호를 축자로 싣지 않는다** — 실으면 도구가
자기 소스와 자기 시험의 표본을 렌더한다. 괄호는 아래 `L`·`R`에서 코드포인트로
조립하고, 문서에는 `<<ID>>`로 적는다. 스캔에서 빼는 예외를 두지 않았고, D의 「인용
꼴이 아닌 괄호」는 치환 뒤에 남은 괄호만 낸다. 성한 꼴 축자는 인용으로 인식되어
치환에서 사라지므로 그 D가 서지 않는다. 실측 — 두 파일에 `<<상태>>`를 축자로 심으면
`--check`가 C 하나만 내고, `--render`가 그 줄을 요지까지 든 꼴로 고쳐 쓴 뒤
`--check`가 무발견을 낸다. 이 규율은 검사가 아니라 저자가 지킨다.

사용:
    python dag_facts.py --render      전거를 읽어 인용 자리를 채운다
    python dag_facts.py --check       A~E. exit 0 = 무발견, 1 = 발견, 2 = 루트 오류
    python dag_facts.py --refs 상태   그 ID의 정본과 인용 전건
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re
import sys
import textwrap
import tokenize
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS_DIR = ROOT / "전거"

SCAN_SUFFIXES = (".md", ".py")
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git"}

L, R = chr(0x3010), chr(0x3011)  # 축자로 두면 D가 자기 소스를 낸다 — 코드포인트로 적는다
GIST_SEP = " · "
WRAP_WIDTH = 96  # 표시 폭. 한글은 1코드포인트가 2열이라 코드포인트로 재면 눈으로 넘친다

_ID = rf"[^\s{L}{R}·]+"
DECL_RE = re.compile(rf"^## {L}({_ID}){R}(?:\s+(.*))?$")
INLINE_RE = re.compile(rf"{L}({_ID})(?: · [^{L}{R}]*)?{R}")
GEN_OPEN_RE = re.compile(rf"^(\s*)#\s*{L}생성 ({_ID}){R}")
GEN_CLOSE_RE = re.compile(rf"^\s*#\s*{L}끝{R}")
QUOTE_OPEN_RE = re.compile(rf"^(\s*)(`{{3,}})전거 ({_ID})\s*$")
FENCE_RE = re.compile(r"^`{3,}")
ASIDE_RE = re.compile(r"^\s*- _[^_]+_")  # `- _경계_` 류. 블록 렌더가 투영하지 않는다
GIST_RE = re.compile(r"^요지:\s*(.*)$")
MACHINE_RE = re.compile(r"^기계값:\s*(.*)$")
# 의존 대장이 싣는 「딛는 자리」. 검사 E가 이 좌표가 파일로 서는지 본다.
# 뒤를 `[ \t]*`로 좁힌다 — `\s*`는 개행을 삼켜 값이 빈 줄이 다음 줄을 좌표로 삼는다.
BACKPOINTER_RE = re.compile(r"^딛는 자리:[ \t]*(.*)$", re.MULTILINE)
# 같은 대장의 「정본」. 저장소 안이 정본인 좌표만 E가 재고, 그 좌표는 백틱에 담기고
# 뒤에 `(저장소 안`으로 시작하는 괄호를 단다 — 표기를 정하지 않으면 인식기가 물지 못한
# 줄이 조용히 검사 밖에 선다.
SOURCE_RE = re.compile(r"^정본:[ \t]*(.*)$", re.MULTILINE)
INREPO_RE = re.compile(r"^`([^`]+)`\s*\(저장소 안")
ASSIGN_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*=")
# 인라인 인용은 요지를 날것으로 써 넣는다. 파이썬 소스에서 이 셋은 문자열 리터럴을
# 깨뜨리거나(따옴표) 이스케이프로 먹혀 값을 갈라 놓는다(역슬래시).
SOURCE_UNSAFE_RE = re.compile(r"[\"'\\]")
STRING_TOKENS = {tokenize.STRING} | {
    getattr(tokenize, n) for n in
    ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END") if hasattr(tokenize, n)
}
BOM_BYTES = b"\xef\xbb\xbf"


def _width(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _pystr(t: str) -> str:
    """요지 원소를 파이썬 문자열 리터럴로. 따옴표·역슬래시를 그냥 감싸면 깨진다."""
    return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'


@dataclass
class Item:
    id: str = ""
    title: str = ""
    gist: str = ""
    machine: str | None = None
    body: str = ""
    stray: list[str] = field(default_factory=list)  # 본문으로 밀린 머리 줄
    path: Path = field(default_factory=Path)
    line: int = 0
    ok: bool = True  # 형태가 성한가. 어긋나면 렌더가 이 항목의 인용을 건드리지 않는다

    def gist_parts(self) -> list[str]:
        return [t.strip() for t in self.gist.split(GIST_SEP) if t.strip()]

    def value_literal(self) -> str:
        """파이썬 생성 블록이 받을 리터럴."""
        if self.machine is not None:
            return self.machine.strip()
        parts = self.gist_parts()
        inner = ", ".join(_pystr(t) for t in parts)
        return f"({inner},)" if len(parts) == 1 else f"({inner})"

    def defects(self) -> list[str]:
        """검사 D 중 항목 층위. 문면만 낸다 — 좌표는 부르는 쪽이 붙인다."""
        out = []
        if not self.gist:
            out.append("요지 줄이 없거나 비었다")
        elif L in self.gist or R in self.gist:
            out.append("요지에 괄호가 있다 — 렌더가 발산한다")
        for s in self.stray:
            head = "요지" if GIST_RE.match(s) else "기계값"
            out.append(f"`{head}:` 줄이 헤딩에서 떨어져 본문으로 밀렸다")
        if self.machine is not None:
            try:
                ast.literal_eval(self.machine.strip())
            except (ValueError, SyntaxError):
                out.append("기계값이 파이썬 리터럴이 아니다")
        return out


# --- 읽기 ---------------------------------------------------------------


def _read(path: Path) -> str:
    """BOM은 벗겨서 읽는다 — 붙어 있으면 첫 줄의 선언·인용이 인식 밖으로 밀리고,
    그 항목의 인용 전부가 `A 미해결 인용`으로 뒤집혀 보고된다."""
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return fh.read()


def _write(path: Path, text: str) -> None:
    """임시 파일에 쓰고 갈아 끼운다. 한 번의 렌더가 여러 파일을 쓰므로 중단은 실제
    경로이고, 직접 절단 쓰기는 그때 부분 기록을 남긴다.

    **교체가 거부되면 직접 쓰기로 물러선다.** Windows는 대상 파일을 누가 **읽기로만**
    열고 있어도 `os.replace`를 거부하는데, 직접 절단 쓰기는 그 상황에서 선다. 물러설
    곳이 없으면 한 파일 안의 부분 기록을 막으려다 **여러 파일에 걸친 부분 렌더**를
    만든다 — 이 함수가 막으려던 바로 그 상태다(실측).
    """
    tmp = path.with_name(path.name + ".dag_facts.tmp")
    try:
        with tmp.open("w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except OSError:
        with path.open("w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    finally:
        tmp.unlink(missing_ok=True)


def _split(line: str) -> tuple[str, str]:
    """줄을 본문과 줄바꿈으로 가른다. 줄바꿈 표기를 보존해야 렌더가 멱등이다."""
    body = line.rstrip("\r\n")
    return body, line[len(body):]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def parse_items(path: Path) -> list[Item]:
    items: list[Item] = []
    cur: Item | None = None
    buf: list[str] = []

    def flush() -> None:
        if cur is None:
            return
        rest: list[str] = []
        for s in buf:
            if not rest:
                m = GIST_RE.match(s)
                if m:
                    cur.gist = m.group(1).strip()
                    continue
                m = MACHINE_RE.match(s)
                if m:
                    cur.machine = m.group(1).strip()
                    continue
            rest.append(s)
            if GIST_RE.match(s) or MACHINE_RE.match(s):
                cur.stray.append(s)
        cur.body = "\n".join(rest).strip()
        items.append(cur)

    for no, line in enumerate(_read(path).splitlines(), 1):
        m = DECL_RE.match(line)
        if m:
            flush()
            cur = Item(id=m.group(1), title=(m.group(2) or "").strip(),
                       path=path, line=no)
            buf = []
        elif cur is not None:
            buf.append(line)
    flush()
    return items


def load_items(facts_dir: Path) -> tuple[dict[str, Item], list[str]]:
    """전거를 읽는다. 두 번째 값은 검사 B와 항목 층위 D다."""
    root = facts_dir.parent
    if not facts_dir.is_dir():
        return {}, [f"D 형태 — 전거 디렉토리가 없다 — {_rel(facts_dir, root)}"]

    seen: dict[str, list[Item]] = {}
    # 재귀다 — 스캔이 하위 디렉토리를 훑는데 적재가 얕으면 그 선언은 정본이 되지
    # 못한 채 남의 인용 자리로 읽혀 렌더된다.
    for path in sorted(facts_dir.rglob("*.md")):
        if SKIP_DIRS & set(path.relative_to(facts_dir).parts):
            continue  # 스캔 밖 파일이 스캔 안 파일들의 값을 정하면 안 된다
        for item in parse_items(path):
            seen.setdefault(item.id, []).append(item)

    items: dict[str, Item] = {}
    findings: list[str] = []
    for iid, group in sorted(seen.items()):
        items[iid] = group[0]
        if len(group) > 1:
            where = " · ".join(f"{_rel(i.path, root)}:{i.line}" for i in group)
            findings.append(f"B 이중 정본 {L}{iid}{R} — {where}")
        defects = group[0].defects()
        group[0].ok = not defects
        for msg in defects:
            findings.append(
                f"D 형태 — {msg} {L}{iid}{R} — "
                f"{_rel(group[0].path, root)}:{group[0].line}")
    return items, findings


def scan_files(root: Path) -> list[Path]:
    out = [p for p in root.rglob("*")
           if p.is_file() and p.suffix in SCAN_SUFFIXES
           and not SKIP_DIRS & set(p.relative_to(root).parts)]
    return sorted(out)


# --- 렌더 ---------------------------------------------------------------


def _assignment_lines(indent: str, name: str, item: Item, eol: str) -> list[str]:
    one = f"{indent}{name} = {item.value_literal()}"
    if item.machine is not None or _width(one) <= WRAP_WIDTH:
        return [one + eol]
    lines = [f"{indent}{name} = (" + eol]
    lines += [f"{indent}    {_pystr(t)}," + eol for t in item.gist_parts()]
    lines.append(f"{indent})" + eol)
    return lines


def _gen_defect(inner: list[str]) -> str | None:
    """생성 블록은 도구 소유 구간이라 대입 하나만 담는다. 나머지는 렌더가 지운다."""
    src = textwrap.dedent("".join(_split(x)[0] + "\n" for x in inner))
    try:
        if any(t.type == tokenize.COMMENT
               for t in tokenize.generate_tokens(io.StringIO(src).readline)):
            return "생성 블록에 주석이 있다 — 렌더가 지운다"
        body = ast.parse(src).body
    except (SyntaxError, IndentationError, tokenize.TokenError):
        return "생성 블록을 파이썬으로 읽을 수 없다"
    if (len(body) != 1 or not isinstance(body[0], ast.Assign)
            or len(body[0].targets) != 1
            or not isinstance(body[0].targets[0], ast.Name)):
        return "생성 블록은 이름 하나에 대입하는 문 하나만 담는다 — 나머지는 렌더가 지운다"
    return None


def _unbalanced_fence(region: list[str]) -> bool:
    """열린 채 남은 울타리가 있으면 이 블록이 남의 닫는 자리를 자기 것으로 삼았다."""
    open_len = None
    for line in region:
        body = _split(line)[0]
        m = FENCE_RE.match(body)
        if not m:
            continue
        run = len(m.group(0))
        if open_len is None:
            open_len = run
        elif run >= open_len and body.strip() == "`" * run:
            open_len = None
    return open_len is not None


def _strip_asides(body: str) -> list[str]:
    """`- _경계_`·`- _실패 유형_` 류를 뺀다.

    그 줄은 등록소를 읽는 개정자만 본다. 소비 자리로 밀려 나가는 것은 사실이지 그
    사실에 붙인 주석이 아니다. 이어진 들여쓰기 줄까지 함께 뺀다.

    **울타리 안은 건드리지 않는다.** 항목이 경계 표기법 자체를 예시로 담으면 그
    예시가 지워져 빈 울타리만 남는다. 뺄 것은 항목이 단 방주이지 항목이 인용한
    문면이 아니다.
    """
    out: list[str] = []
    dropping = False
    fence: str | None = None
    for line in body.split("\n"):
        run = FENCE_RE.match(line)
        if run or fence is not None:
            if run and fence is None:
                fence = run.group(0)
            elif run and len(run.group(0)) >= len(fence) \
                    and line.strip() == run.group(0):
                fence = None
            dropping = False
            out.append(line)
            continue
        if ASIDE_RE.match(line):
            dropping = True
            continue
        if dropping and line.strip() and line[:1] in " \t":
            continue
        dropping = False
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return out


def _resolve_inline(line: str, items: dict[str, Item]) -> str:
    """인라인 인용을 요지까지 든 꼴로 푼다. 발견은 내지 않는다 — 이 줄의 정본은
    전거 파일이고 그 파일을 렌더할 때 같은 자리가 A를 낸다."""
    def repl(mo: re.Match) -> str:
        cited = items.get(mo.group(1))
        if cited is None or not cited.ok:
            return mo.group(0)  # 전거 파일 쪽 렌더도 이 자리를 그대로 둔다
        return f"{L}{mo.group(1)}{GIST_SEP}{cited.gist}{R}"
    return INLINE_RE.sub(repl, line)


def _block_lines(item: Item, eol: str, items: dict[str, Item]) -> list[str]:
    """블록이 실을 줄. **본문의 인라인 인용을 풀고 싣는다.**

    `item.body`는 렌더 **전**의 문면이다. 그대로 투영하면 같은 렌더가 전거 파일의
    그 줄은 요지까지 든 꼴로 갱신하면서 블록 자리에는 저자형을 밀어 넣고, 다음
    렌더가 블록 자리를 또 바꾼다 — 불변식 「`--render`가 멱등이다」가 깨진다.
    그 사이 렌더는 발견 0건·exit 0을 내므로 렌더 직후 커밋하는 자리가 초록으로
    읽는다."""
    out = [f"요지: {item.gist}" + eol]
    body = _strip_asides(item.body) if item.body else []
    if body:
        out.append(eol)
        out += [_resolve_inline(s, items) + eol for s in body]
    return out


def _fence_len(content: list[str]) -> int:
    """본문에 든 울타리보다 긴 울타리라야 블록이 제 자리에서 닫힌다."""
    longest = 0
    for line in content:
        m = FENCE_RE.match(_split(line)[0])
        if m:
            longest = max(longest, len(m.group(0)))
    return max(3, longest + 1)


def _string_rows(text: str) -> set[int] | None:
    """파이썬 소스에서 문자열 리터럴이 걸친 행. 읽을 수 없으면 None(전부 위험).

    위험은 **자리의 성질**이다 — 주석에는 이스케이프가 없어 따옴표도 역슬래시도
    소스를 깨뜨리지 못한다. 거기까지 막으면 인용을 못 거는 자리가 좌표 문자열을
    지게 되고, 그 좌표는 낡아도 아무 검사가 잡지 않는다.
    """
    rows: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in STRING_TOKENS:
                rows.update(range(tok.start[0], tok.end[0] + 1))
    except (SyntaxError, IndentationError, tokenize.TokenError):
        return None
    return rows


def render_text(text: str, items: dict[str, Item], *,
                coord: str,
                is_facts_file: bool = False,
                is_python: bool = False) -> tuple[str, list[str]]:
    """인용 자리를 채운 본문과 검사 A·D를 낸다. 발견의 좌표 자리에 `coord`가 든다.

    **발견 문면을 다시 포맷하지 않는다.** 문면은 ID를 축자로 담으므로, 좌표만
    자리표시자로 남겼다가 나중에 `str.format`으로 채우면 중괄호를 담은 ID가 필드
    이름으로 읽혀 검사 전체가 예외로 죽는다(`_ID` 문법이 중괄호를 배제하지 않는다).
    그래서 `coord`에 기본값을 두지 않는다 — 기본값이 있으면 다음 개정이 자리표시자를
    되돌릴 자리가 남는다.
    """
    str_rows = _string_rows(text) if is_python else set()
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    findings: list[str] = []
    i = 0

    def miss(iid: str, no: int) -> None:
        findings.append(f"A 미해결 인용 {L}{iid}{R} — {coord}:{no}")

    def bad(msg: str, no: int) -> None:
        findings.append(f"D 형태 — {msg} — {coord}:{no}")

    while i < len(lines):
        body, eol = _split(lines[i])

        m = GEN_OPEN_RE.match(body)
        if m:
            close = None
            for j in range(i + 1, len(lines)):
                b = _split(lines[j])[0]
                if GEN_CLOSE_RE.match(b):
                    close = j
                    break
                if GEN_OPEN_RE.match(b):
                    break  # 다음 블록이 먼저 열렸다 — 이 블록은 닫히지 않았다
            if close is None:
                bad("생성 블록이 닫히지 않았다", i + 1)
                out.append(lines[i])
                i += 1
                continue
            inner = lines[i + 1:close]
            defect = _gen_defect(inner)
            assign = next((a for a in (ASSIGN_RE.match(_split(x)[0]) for x in inner)
                           if a), None)
            item = items.get(m.group(2))
            if item is None:
                miss(m.group(2), i + 1)
                out += lines[i:close + 1]
            elif not item.ok:
                out += lines[i:close + 1]  # 항목 층위 D가 이미 냈다
            elif defect or assign is None:
                bad(defect or "생성 블록에 대입이 없다", i + 1)
                out += lines[i:close + 1]
            else:
                out.append(lines[i])
                out += _assignment_lines(assign.group(1), assign.group(2),
                                         item, _split(inner[0])[1] or eol)
                out.append(lines[close])
            i = close + 1
            continue

        # 여는 마커를 만난 블록은 위에서 닫는 마커까지 삼켰다. 여기 남은 닫는
        # 마커는 짝이 없다. 먼저 가르지 않으면 `INLINE_RE`가 `끝`을 ID로 잡아
        # 「A 미해결 인용」으로 내고, 그 문면은 없는 항목을 등재하라고 지시한다.
        if GEN_CLOSE_RE.match(body):
            bad("생성 블록의 닫는 마커에 짝이 없다 — 여는 마커가 없거나 지워졌다",
                i + 1)
            out.append(lines[i])
            i += 1
            continue

        m = QUOTE_OPEN_RE.match(body)
        if m:
            # 목록 항목·인용문 안의 블록은 앞머리 공백을 진다. 그 공백을 받지
            # 않으면 검사도 렌더도 그 자리를 통째로 지나쳐, 낡은 내용이 남은 채
            # `--check`가 무발견을 낸다. 생성 블록은 이미 공백을 받는다.
            indent, n = m.group(1), len(m.group(2))
            close_re = re.compile(r"^%s`{%d,}\s*$" % (re.escape(indent), n))
            close = next((j for j in range(i + 1, len(lines))
                          if close_re.match(_split(lines[j])[0])), None)
            if close is None:
                bad("전거 블록이 닫히지 않았다", i + 1)
                out.append(lines[i])
                i += 1
                continue
            # 중첩 울타리 판별은 블록 안쪽 좌표로 한다 — 앞머리 공백을 벗기지
            # 않으면 들여쓴 블록에서 삼킴 가드가 서지 않는다.
            region = [x[len(indent):] if x.startswith(indent) else x
                      for x in lines[i + 1:close]]
            item = items.get(m.group(3))
            if item is None:
                miss(m.group(3), i + 1)
                out += lines[i:close + 1]
            elif not item.ok:
                out += lines[i:close + 1]  # 항목 층위 D가 이미 냈다
            elif _unbalanced_fence(region):
                bad("전거 블록이 중첩 울타리를 삼켰다 — 닫는 자리가 틀렸다", i + 1)
                out += lines[i:close + 1]
            else:
                content = _block_lines(item, eol, items)
                fence = "`" * _fence_len(content)
                out.append(f"{indent}{fence}전거 {m.group(3)}" + eol)
                out += [indent + s if s.strip() else s for s in content]
                out.append(indent + fence + eol)
            i = close + 1
            continue

        def stray(text: str, no: int) -> None:
            if L in INLINE_RE.sub("", text) or R in INLINE_RE.sub("", text):
                bad("인용 꼴이 아닌 괄호 — 사람 눈에는 인용이나 렌더가 닿지 않는다", no)

        if is_facts_file:
            # 선언과 `요지:`·`기계값:`은 정본 데이터지 인용 자리가 아니다.
            decl = DECL_RE.match(body)
            if decl:
                stray(decl.group(2) or "", i + 1)
                out.append(lines[i])
                i += 1
                continue
            if GIST_RE.match(body) or MACHINE_RE.match(body):
                out.append(lines[i])
                i += 1
                continue

        no = i + 1

        def repl(mo: re.Match) -> str:
            item = items.get(mo.group(1))
            if item is None:
                miss(mo.group(1), no)
                return mo.group(0)
            if not item.ok:
                return mo.group(0)  # 항목 층위 D가 이미 냈다
            if (is_python and (str_rows is None or no in str_rows)
                    and SOURCE_UNSAFE_RE.search(item.gist)):
                bad("요지에 따옴표·역슬래시가 있다 — 파이썬 문자열 리터럴 안의"
                    " 인라인 인용은 이스케이프가 없어 리터럴을 깨거나 값을"
                    " 갈라 놓는다", no)
                return mo.group(0)
            return f"{L}{mo.group(1)}{GIST_SEP}{item.gist}{R}"

        new = INLINE_RE.sub(repl, body)
        stray(GEN_OPEN_RE.sub("", new), no)
        out.append(new + eol)
        i += 1

    return "".join(out), findings


def render(root: Path = ROOT, write: bool = True) -> tuple[list[Path], list[str]]:
    """인용 자리를 채운다. (바뀐 파일, 검사 A·B·D). `write=False`면 재기만 한다."""
    facts_dir = root / "전거"
    items, findings = load_items(facts_dir)
    changed: list[Path] = []
    for path in scan_files(root):
        text = _read(path)
        new, found = render_text(text, items,
                                 coord=_rel(path, root),
                                 is_facts_file=facts_dir in path.parents,
                                 is_python=path.suffix == ".py")
        findings += found
        if any(f.startswith("D 형태") for f in found):
            # 형태가 깨진 파일은 통째로 건드리지 않는다 — 검출은 차단이 아니다.
            # 차단이 파일 층위이므로 그 사실을 발견이 함께 말해야 한다. 어긋난
            # 자리만 가리키면 같은 파일의 다른 인용·생성 블록이 멈춘 것을 못 본다.
            findings.append(
                f"D 차단 — {_rel(path, root)}의 렌더를 전부 멈췄다"
                " (위 D를 고쳐야 이 파일이 갱신된다)")
            continue
        with path.open("rb") as fh:
            had_bom = fh.read(3) == BOM_BYTES
        if new != text or had_bom:
            changed.append(path)
            if write:
                _write(path, new)
    return changed, findings


def check_backpointers(facts_dir: Path, root: Path) -> list[str]:
    """E 역포인터 정합 — 의존 대장의 좌표가 파일로 서는가.

    전거 항목은 `grep ID`가 인용 전건을 내므로 정본을 고치는 사람이 영향 범위를 기계로
    안다. **정본이 스킬 밖이면 그 장치가 없다** — 고치는 사람이 이 저장소를 보지
    않거나, 정본이 주석을 못 받는 형식이다. 그래서 방향을 뒤집어 딛는 자리를 대장에
    싣고, 그 좌표의 실재를 여기서 지킨다. 좌표가 낡으면 대장이 가리키는 곳에 아무것도
    없어, 정본이 바뀌었을 때 무엇이 깨지는지 찾을 길이 사라진다.

    **발견 분기는 셋이고 위 선언과 모듈 도크스트링이 셋을 다 싣는다.** 선언이 하나만
    싣던 동안 그 선언을 계약으로 읽는 개정자는 나머지 분기를 구현의 군더더기로 보고
    지울 수 있었다.

    **좌표는 파일이라야 한다.** 대장 서두가 「딛는 자리」를 파일로 정의하고 「정본」을
    거처로 따로 두므로 단위가 파일이다. 실재만 재면 좌표가 상위 디렉토리로 뭉개져도
    초록이 선다(실측: `딛는 자리: scripts`가 무발견을 냈다). 그때 정본이 바뀐 뒤 그
    좌표를 따라간 사람은 디렉토리 하나를 받고 어느 파일이 깨질지 알지 못한다.

    **줄의 부재도 E다.** 있는 줄의 좌표만 훑으면 대장의 여덟 줄을 다 지워도 무발견이
    된다(실측). 부재는 좌표 0건이라 순회가 조용히 비고, 그때 대장은 딛는 자리를 하나도
    싣지 않은 채 초록으로 선다 — 방향을 뒤집은 장치가 통째로 사라진 상태다. 그래서
    대장 파일 `전거/의존.md`의 항목마다 좌표를 최소 하나 요구한다.

    **저장소 안이 정본인 좌표도 잰다.** 대장이 자기 손으로 지킬 수 있는 좌표가 그것뿐
    이다 — 저장소 밖 정본에는 걸 길이 없다. 재지 않으면 그 정본 파일이 옮겨져도 대장이
    낡은 좌표를 쥔 채 `--check`가 exit 0을 낸다.

    **대장 소속은 파일로 가른다.** 요구의 근거가 그 파일 서두의 「각 항목은 셋을 더
    든다」이고, ID 접두 `의존:`을 요구하는 문면은 없다. 접두로 가르면 접두 없이 세운
    항목이 이 요구 밖에 서고, 그 항목에 대해 위 상태가 그대로 돌아온다.

    **좌표의 기준이 둘이다** — 「딛는 자리」는 스킬 루트 기준이고 「정본」은 저장소 루트
    기준이다. 저장소 루트는 `.git`을 진 조상으로 찾는다. 없으면(저장소 밖 사본) 정본
    좌표를 재지 않는다 — 재면 사본의 `--check`가 사본에 있을 수 없는 파일을 발견으로
    낸다. 두 좌표 다 ` · `로 나열한다.
    """
    items, _ = load_items(facts_dir)
    ledger = facts_dir / "의존.md"
    repo = next((p for p in (root, *root.parents) if (p / ".git").exists()), None)
    findings: list[str] = []
    for iid, item in sorted(items.items()):
        seen = 0
        for m in BACKPOINTER_RE.finditer(item.body or ""):
            for raw in m.group(1).split(GIST_SEP):
                coord = raw.strip().strip("`").strip()
                if not coord:
                    continue
                seen += 1
                if not (root / coord).is_file():
                    findings.append(
                        f"E 역포인터 — {L}{iid}{R}의 딛는 자리가 파일로 서지 않는다:"
                        f" {coord}")
        if repo is not None:
            for m in SOURCE_RE.finditer(item.body or ""):
                for raw in m.group(1).split(GIST_SEP):
                    inrepo = INREPO_RE.match(raw.strip())
                    if inrepo and not (repo / inrepo.group(1)).is_file():
                        findings.append(
                            f"E 역포인터 — {L}{iid}{R}의 정본이 파일로 서지 않는다:"
                            f" {inrepo.group(1)}")
        if item.path == ledger and not seen:
            findings.append(
                f"E 역포인터 — {L}{iid}{R}이 딛는 자리를 싣지 않았다")
    return findings


def check(root: Path = ROOT) -> list[str]:
    stale, findings = render(root, write=False)
    return findings + [
        f"C 렌더 불일치 — {_rel(p, root)} (--render 필요)" for p in stale
    ] + check_backpointers(root / "전거", root)


def _cites(line: str, item_id: str) -> bool:
    """렌더가 인용으로 보는 자리인가. 부분문자열이 아니라 같은 인식기로 판별한다."""
    m = GEN_OPEN_RE.match(line)
    if m:
        return m.group(2) == item_id
    m = QUOTE_OPEN_RE.match(line)
    if m:
        return m.group(3) == item_id
    return any(mo.group(1) == item_id for mo in INLINE_RE.finditer(line))


def refs(root: Path = ROOT, item_id: str = "") -> list[str]:
    """그 ID의 정본과 인용 전건. grep의 포장이지 별도 자료가 아니다."""
    facts_dir = root / "전거"
    out: list[str] = []
    for path in scan_files(root):
        declaring = facts_dir in path.parents
        for no, line in enumerate(_read(path).splitlines(), 1):
            m = DECL_RE.match(line)
            if declaring and m:
                if m.group(1) == item_id:
                    out.append(f"{_rel(path, root)}:{no}: 정본 {line.strip()}")
                continue
            if _cites(line, item_id):
                out.append(f"{_rel(path, root)}:{no}: 인용 {line.strip()}")
    return out


# --- CLI -----------------------------------------------------------------


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", default=str(ROOT), help="스킬 루트(기본: do-dag)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--render", action="store_true", help="인용 자리를 채운다")
    g.add_argument("--check", action="store_true", help="A~E. 발견이면 exit 1")
    g.add_argument("--refs", metavar="ID", help="그 ID의 정본과 인용 전건")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[dag_facts] 루트가 없다 — {root}")
        return 2

    if args.refs is not None:
        rows = refs(root, args.refs)
        for r in rows:
            print(f"[dag_facts] {r}")
        print(f"[dag_facts] {L}{args.refs}{R} {len(rows)}자리")
        return 0

    if args.render:
        changed, findings = render(root)
        # E는 렌더가 해소하지 않는다 — C는 자리를 채우면 사라지지만 낡은 좌표는
        # 몇 번을 돌려도 그대로다. 빼고 0을 내면 렌더 뒤 커밋 자리가 초록으로 읽는다.
        findings += check_backpointers(root / "전거", root)
        for path in changed:
            print(f"[dag_facts] 렌더 {_rel(path, root)}")
        for f in findings:
            print(f"[dag_facts] {f}")
        print(f"[dag_facts] 렌더 {len(changed)}파일 · 발견 {len(findings)}건")
        # 발견을 내면서 0을 내면 `--render` → 커밋 자동화가 초록으로 읽는다.
        return 1 if findings else 0

    findings = check(root)
    if not findings:
        items, _ = load_items(root / "전거")
        print(f"[dag_facts] 무발견 (전거 {len(items)}항목)")
        return 0
    for f in findings:
        print(f"[dag_facts] {f}")
    print(f"[dag_facts] 발견 {len(findings)}건")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
