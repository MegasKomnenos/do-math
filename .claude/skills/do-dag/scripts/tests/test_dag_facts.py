"""dag_facts 전거 검사 시험. 직접 실행이 정본이다: python .claude/skills/do-dag/scripts/tests/test_dag_facts.py

**이름 주의** — `dag_check`의 것은 **파견표 검산 ①~⑨**이고 여기 것은 **전거 검사
A~E**다. 두 도구가 재는 대상이 다르다: `dag_check`는 런의 파견표를, `dag_facts`는
스킬 자신의 파일을 잰다. 낱말이 섞이지 않게 번호 체계를 갈랐다.

A 미해결 인용 — 인용된 ID의 항목이 전거에 없다.
B 이중 정본 — 한 ID에 항목이 둘.
C 렌더 불일치 — `--render`가 바꿀 자리가 남아 있다.
D 형태 — 항목·블록·괄호가 문법에 어긋난다. 렌더는 그 자리를 건드리지 않는다.
E 역포인터 — 의존 대장의 좌표가 파일로 서지 않거나, 대장 항목이 「딛는 자리」를 싣지
  않았다. 재는 좌표는 「딛는 자리」 전건과 저장소 안이 정본인 「정본」이다.

핵심 시험 여섯:
- **판별성**(임시/do-dag_정본단일화_기안_2026-07-28.md §6-5) — 항목을 지우면 A가 그 인용을 **전부** 낸다.
- **멱등**(임시/do-dag_정본단일화_기안_2026-07-28.md §6-6) — 렌더를 두 번 돌리면 바이트가 같다. 첫 렌더가 실제로 채웠음을
  함께 잰다. 둘째만 재면 아무것도 안 하는 렌더가 통과한다.
- **차단** — D가 발견을 내면서 값을 밀어 넣으면 옳던 상수가 덮인다. 어긋난 자리를
  렌더가 건드리지 않는지 인라인·블록·생성 블록 셋 모두에서 잰다. 차단은 **파일
  층위**이기도 하다 — 어긋난 자리만 건너뛰고 이어 가면 다음 여는 마커가 앞 블록의
  대입을 삼킨다.
- **소스 안전** — 인라인 인용은 요지를 날것으로 써 넣는다. 파이썬 파일에서 따옴표는
  소스를 깨뜨리고 역슬래시는 값을 갈라 놓으며, 둘 다 렌더 후 `--check`가 조용하다.
- **울타리 길이** — 백틱 셋만 시험하면 넷 이상에서 가드가 빠진 것을 못 본다.
- **역포인터 판별성** — 없는 좌표 하나와 디렉토리로 뭉갠 좌표와 「딛는 자리」 줄의
  부재와 낡은 저장소 안 정본 좌표와 대장 소속의 파일 판별을 각각 E로 가른다. E만 이
  목록에 이름이 없으면 그 다섯을 지우는 개정을 막는 문면이 이 파일에 없다.

**이 파일은 인용 꼴을 축자로 싣지 않는다.** 실으면 도구가 자기 시험의 표본을 렌더해
버린다(스캔에서 빼는 예외를 두지 않았다). 표본은 `q()`가 `<<`·`>>`를 실제 괄호로
바꿔 만든다.

마지막 클래스는 대역이 아니라 **실물 전거**를 연다. 대역이 통과한 것은 대역이
통과한 것뿐이므로, 1b가 옮긴 상수 열하나(`MOVED`)가 내는 값이 현행 코드 상수와 실제로
같은지를 `ast.literal_eval`로 직접 잰다. `예산`처럼 `기계값:` 줄을 든 것과 `상태`처럼
요지에서 파생되는 것이 섞여 있다.

같은 클래스가 축 둘을 더 잰다. **값이 같은가**와 **생성 블록 안에 있는가**는 다른
것이다 — 값만 재면 손으로 맞춰 둔 상수가 통과하고, 다음 개정이 전거를 지나쳐 코드를
직접 고친다. 그리고 상수에 후행 주석으로 붙어 있던 사실은 값에서 파생되지 않으므로
**항목 본문이 진다**(생성 블록은 대입 하나만 담고 렌더가 주석을 지운다).
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import dag_check  # noqa: E402
import dag_facts  # noqa: E402
import dag_marker  # noqa: E402
import dag_measure  # noqa: E402

# 전거로 정본을 옮긴 상수. (항목 ID, 모듈, 대입 이름).
# `이름문법`이 감싸는 것은 사전 하나다. 한 사실이 사람이 읽는 요지와 기계가 집행하는
# 패턴 두 표기로 살고 한 항목의 기계값은 하나이므로, 두 표기를 사전에 담는다.
# `NAME_RULE`·`PHASE_RE`는 그 사전에서 파생하므로 따로 등재하지 않는다 — 등재하면
# 그것이 두 번째 정본이 된다(임시/do-dag_정본단일화_기안_2026-07-28.md §2.3 파생값 예외).
MOVED = (
    ("상태", dag_check, "STATES"),
    ("완결상태", dag_check, "DONE_STATES"),
    ("유형", dag_check, "KINDS"),
    ("검산모드", dag_check, "MODES"),
    ("모델", dag_check, "MODELS"),
    ("노력", dag_check, "EFFORTS"),
    ("센티널", dag_check, "TABLE_END"),
    ("단계원장-노드", dag_check, "NODE_SETTLEMENT_STAGES"),
    ("단계원장-국면", dag_check, "PHASE_SETTLEMENT_STAGES"),
    ("예산", dag_measure, "BUDGETS"),
    ("이름문법", dag_marker, "_NAME"),
)


def generated_name(module, item_id: str) -> str | None:
    """모듈 소스의 그 ID 생성 블록이 감싼 대입 이름. 블록이 없으면 None.

    부분문자열이 아니라 렌더와 **같은 인식기**로 잰다 — 이 시험이 렌더보다 너그러우면
    렌더가 닿지 않는 자리를 통과시킨다.
    """
    with Path(module.__file__).open(encoding="utf-8", newline="") as fh:
        lines = fh.read().splitlines()
    for i, line in enumerate(lines):
        m = dag_facts.GEN_OPEN_RE.match(line)
        if not m or m.group(2) != item_id:
            continue
        for body in lines[i + 1:]:
            if dag_facts.GEN_CLOSE_RE.match(body):
                return None  # 닫혔는데 대입이 없다
            a = dag_facts.ASSIGN_RE.match(body)
            if a:
                return a.group(2)
    return None


def q(s: str) -> str:
    """`<<ID>>` 꼴을 실제 인용 문법으로 바꾼다."""
    return s.replace("<<", dag_facts.L).replace(">>", dag_facts.R)


STATE_ITEM = q("""\
## <<상태>> 파견표 상태 어휘
요지: 미착수 · 진행 · 상신중 · 예외 · 완 · 비준 · 파킹

상태 열의 작성자는 둘이다 — 평시에는 오케, 예외 처분에 한해 예외 에이전트.
""")

BUDGET_ITEM = q("""\
## <<예산>> 모델 예산
요지: sonnet 150k · opus 200k · fable 250k
기계값: {"sonnet": 150_000, "opus": 200_000, "fable": 250_000}

한 파견 단위가 완주해야 하는 문맥 상한이다.
""")

GIST = "미착수 · 진행 · 상신중 · 예외 · 완 · 비준 · 파킹"
STATES_LITERAL = '("미착수", "진행", "상신중", "예외", "완", "비준", "파킹")'


def tree(**files: str) -> Path:
    """임시 스킬 루트를 깐다. 키의 `/`는 디렉토리 구분이다."""
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = root.joinpath(*rel.split("/"))
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    return root


def base(**extra: str) -> Path:
    """표본 두 항목이 선 전거 + 인자로 준 소비 파일."""
    files = {"전거/실행.md": STATE_ITEM, "전거/파견단위.md": BUDGET_ITEM}
    files.update(extra)
    return tree(**files)


def read(root: Path, rel: str) -> str:
    with root.joinpath(*rel.split("/")).open(encoding="utf-8", newline="") as fh:
        return fh.read()


class ItemParseTest(unittest.TestCase):
    def test_요지가_기계값_없이_튜플로_파생된다(self):
        items, findings = dag_facts.load_items(base() / "전거")
        self.assertEqual(findings, [])
        self.assertEqual(items["상태"].value_literal(), STATES_LITERAL)

    def test_기계값_줄이_있으면_그것이_리터럴이다(self):
        items, _ = dag_facts.load_items(base() / "전거")
        self.assertEqual(
            items["예산"].value_literal(),
            '{"sonnet": 150_000, "opus": 200_000, "fable": 250_000}',
        )

    def test_제목_요지_본문이_갈린다(self):
        items, _ = dag_facts.load_items(base() / "전거")
        s = items["상태"]
        self.assertEqual(s.title, "파견표 상태 어휘")
        self.assertEqual(s.gist, GIST)
        self.assertIn("작성자는 둘이다", s.body)
        self.assertNotIn("요지:", s.body)


class RenderTest(unittest.TestCase):
    def test_저자형_인라인이_요지를_받는다(self):
        root = base(**{"SKILL.md": q("상태는 <<상태>> 일곱이다.\n")})
        dag_facts.render(root)
        self.assertEqual(read(root, "SKILL.md"),
                         q(f"상태는 <<상태 · {GIST}>> 일곱이다.\n"))

    def test_낡은_요지가_갱신된다(self):
        root = base(**{"SKILL.md": q("<<상태 · 옛값 · 또옛값>>\n")})
        dag_facts.render(root)
        self.assertIn("미착수 · 진행", read(root, "SKILL.md"))
        self.assertNotIn("옛값", read(root, "SKILL.md"))

    def test_블록이_요지와_본문을_받는다(self):
        root = base(**{"대응표.md": "```전거 상태\n낡은 내용\n```\n"})
        dag_facts.render(root)
        out = read(root, "대응표.md")
        self.assertIn(f"요지: {GIST}\n", out)
        self.assertIn("작성자는 둘이다", out)
        self.assertNotIn("낡은 내용", out)

    def test_블록은_기계값_줄을_싣지_않는다(self):
        root = base(**{"대응표.md": "```전거 예산\n```\n"})
        dag_facts.render(root)
        out = read(root, "대응표.md")
        self.assertIn("요지: sonnet 150k", out)
        self.assertNotIn("기계값:", out)

    def test_파이썬_생성_블록이_대입_이름을_보존한다(self):
        src = q("# <<생성 상태>> — dag_facts.py --render가 채운다\n"
                "STATES = ()\n# <<끝>>\n")
        root = base(**{"scripts/dag_check.py": src})
        dag_facts.render(root)
        self.assertIn(f"STATES = {STATES_LITERAL}\n",
                      read(root, "scripts/dag_check.py"))

    def test_생성_블록_마커를_인용으로_오인하지_않는다(self):
        src = q("# <<생성 예산>>\nBUDGETS = {}\n# <<끝>>\n")
        root = base(**{"scripts/dag_measure.py": src})
        self.assertEqual(
            [f for f in dag_facts.check(root) if f.startswith("A")], [])
        dag_facts.render(root)
        out = read(root, "scripts/dag_measure.py")
        self.assertIn(q("# <<생성 예산>>\n"), out)
        self.assertIn(q("# <<끝>>\n"), out)
        self.assertIn('BUDGETS = {"sonnet": 150_000', out)

    def test_전거_선언_헤딩은_렌더되지_않는다(self):
        """같은 파일 본문의 인용은 렌더된다 — 선언만 예외다."""
        root = base(**{"전거/실행.md": STATE_ITEM + q("\n예산은 <<예산>>이다.\n")})
        dag_facts.render(root)
        out = read(root, "전거/실행.md")
        self.assertIn(q("## <<상태>> 파견표 상태 어휘\n"), out)
        self.assertIn(q("예산은 <<예산 · sonnet 150k · opus 200k · fable 250k>>이다.\n"),
                      out)

    def test_렌더가_멱등이다(self):
        root = base(**{
            "SKILL.md": q("<<상태>> 그리고 <<예산>>\n"),
            "대응표.md": "```전거 상태\n```\n",
            "scripts/dag_check.py": q("# <<생성 상태>>\nSTATES = ()\n# <<끝>>\n"),
        })
        rels = ("SKILL.md", "대응표.md", "scripts/dag_check.py")
        changed, _ = dag_facts.render(root)
        self.assertEqual(len(changed), 3, f"첫 렌더가 세 파일을 다 채우지 않았다: {changed}")
        first = {rel: read(root, rel) for rel in rels}
        changed, _ = dag_facts.render(root)
        self.assertEqual({rel: read(root, rel) for rel in rels}, first)
        self.assertEqual(changed, [], "두 번째 렌더가 파일을 바꿨다")

    def test_긴_튜플은_줄을_나눈다(self):
        long_gist = " · ".join(f"아주긴상태이름{i}" for i in range(8))
        root = tree(**{
            "전거/실행.md": q(f"## <<긴것>> 제목\n요지: {long_gist}\n"),
            "scripts/x.py": q("# <<생성 긴것>>\nNAMES = ()\n# <<끝>>\n"),
        })
        dag_facts.render(root)
        out = read(root, "scripts/x.py")
        self.assertIn("NAMES = (\n", out)
        self.assertIn('    "아주긴상태이름0",\n', out)
        self.assertIn(")\n", out)
        changed, _ = dag_facts.render(root)
        self.assertEqual(changed, [], "여러 줄 생성 블록이 멱등이 아니다")


class CheckTest(unittest.TestCase):
    def test_무발견이면_비어_있다(self):
        root = base(**{"SKILL.md": q(f"<<상태 · {GIST}>>\n")})
        self.assertEqual(dag_facts.check(root), [])

    def test_A_항목을_지우면_그_인용을_전부_낸다(self):
        """판별성. 이 시험이 없으면 검사 A가 조용히 죽어도 알 수 없다."""
        consumers = {
            "SKILL.md": q("<<상태>> 그리고 또 <<상태>>\n"),
            "대응표.md": "```전거 상태\n```\n",
            "scripts/dag_check.py": q("# <<생성 상태>>\nSTATES = ()\n# <<끝>>\n"),
        }
        root = base(**consumers)
        self.assertEqual(
            [f for f in dag_facts.check(root) if f.startswith("A")], [])

        with (root / "전거" / "실행.md").open("w", encoding="utf-8", newline="") as fh:
            fh.write("")
        found = [f for f in dag_facts.check(root) if f.startswith("A")]
        self.assertEqual(len(found), 4, f"인용 4자리 중 놓친 것이 있다: {found}")
        for rel in consumers:
            self.assertTrue(
                any(rel.split("/")[-1] in f for f in found),
                f"{rel}의 인용을 내지 않았다: {found}",
            )

    def test_A_미해결_인용은_렌더가_건드리지_않는다(self):
        """같은 파일의 해결된 인용은 렌더된다 — 무동작 렌더로는 통과할 수 없다."""
        root = base(**{"SKILL.md": q("<<없는것>> 그리고 <<상태>>\n")})
        dag_facts.render(root)
        self.assertEqual(read(root, "SKILL.md"),
                         q(f"<<없는것>> 그리고 <<상태 · {GIST}>>\n"))

    def test_B_한_ID에_항목이_둘이면_낸다(self):
        root = base(**{"전거/검증.md": STATE_ITEM})
        found = [f for f in dag_facts.check(root) if f.startswith("B")]
        self.assertEqual(len(found), 1, found)
        self.assertIn("상태", found[0])
        self.assertIn("실행.md", found[0])
        self.assertIn("검증.md", found[0])

    def test_중괄호를_담은_ID의_인용도_발견으로_나온다(self):
        """판별성. 좌표를 나중에 `str.format`으로 채우면 ID의 중괄호가 필드 이름으로
        읽혀 `--check`가 발견 대신 `ValueError`로 죽는다. `_ID` 문법은 중괄호를
        배제하지 않으므로 이 자리를 시험이 막는다."""
        root = base(**{"SKILL.md": q("<<가{나>>\n")})
        found = [f for f in dag_facts.check(root) if f.startswith("A")]
        self.assertEqual(len(found), 1, found)
        self.assertIn("가{나", found[0])
        self.assertIn("SKILL.md", found[0])

    def test_C_렌더가_밀리면_낸다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n")})
        found = [f for f in dag_facts.check(root) if f.startswith("C")]
        self.assertEqual(len(found), 1, found)
        self.assertIn("SKILL.md", found[0])
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])


class RefsTest(unittest.TestCase):
    def test_선언과_인용을_함께_낸다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n"), "대응표.md": "무관\n"})
        out = dag_facts.refs(root, "상태")
        self.assertTrue(any("전거/실행.md" in r and "정본" in r for r in out), out)
        self.assertTrue(any("SKILL.md" in r and "인용" in r for r in out), out)
        self.assertFalse(any("대응표.md" in r for r in out), out)

    def test_블록_인용과_생성_블록도_센다(self):
        root = base(**{"d.md": "```전거 상태\n```\n",
                       "s.py": q("# <<생성 상태>>\nV = ()\n# <<끝>>\n")})
        out = dag_facts.refs(root, "상태")
        self.assertTrue(any("d.md" in r and "인용" in r for r in out), out)
        self.assertTrue(any("s.py" in r and "인용" in r for r in out), out)

    def test_줄_한가운데의_울타리는_인용이_아니다(self):
        """렌더가 울타리로 보지 않는 자리를 refs가 인용으로 세면 둘이 어긋난다."""
        root = base(**{"scripts/x.py": 'src = "```전거 상태\\n```\\n"\n'})
        out = dag_facts.refs(root, "상태")
        self.assertFalse(any("scripts/x.py" in r for r in out), out)

    def test_전거_밖의_선언_꼴은_정본으로_세지_않는다(self):
        """`refs`가 정본을 전거 안으로 한정하는 게이트의 부정 방향. 렌더 쪽에는 같은
        게이트의 부정 방향 시험이 서 있고 여기에는 없었다.

        게이트가 빠지면 소비 자리의 선언 꼴이 둘째 정본으로 뜬다 — 「이 사실의 정본이
        어디인가」에 답하는 유일한 명령이 답을 둘 낸다(실측)."""
        root = tree(**{"전거/x.md": q("## <<갑>> 제목\n요지: 가 · 나\n"),
                       "SKILL.md": q("## <<갑>> 남의 파일에 선 선언 꼴\n")})
        rows = dag_facts.refs(root, "갑")
        canon = [r for r in rows if ": 정본" in r]
        self.assertEqual(len(canon), 1, rows)
        self.assertIn("전거/x.md", canon[0])
        self.assertTrue(any("SKILL.md" in r and ": 인용" in r for r in rows), rows)


class CliTest(unittest.TestCase):
    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dag_facts.main(list(argv))
        return rc, buf.getvalue()

    def test_check가_무발견에_0_발견에_1을_낸다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n")})
        rc, out = self._run("--check", "--root", str(root))
        self.assertEqual(rc, 1)
        self.assertIn("발견", out)
        self._run("--render", "--root", str(root))
        rc, out = self._run("--check", "--root", str(root))
        self.assertEqual(rc, 0)
        self.assertIn("무발견", out)

    def test_render가_발견이_있으면_1을_낸다(self):
        """`--render`가 발견을 내면서 0을 내면 `render → 커밋` 자동화가 초록으로
        읽는다. 검출과 종료코드는 같은 것을 말해야 한다."""
        root = base(**{"s.md": q("<<없는것>>\n")})
        self.assertEqual(dag_facts.main(["--root", str(root), "--render"]), 1)
        self.assertEqual(dag_facts.main(["--root", str(root), "--render"]), 1)

    def test_render가_E_역포인터도_낸다(self):
        """E는 렌더가 해소하지 않는다 — C는 자리를 채우면 사라지지만 낡은 좌표는
        몇 번을 돌려도 그대로다. `--render`가 E를 빼고 0을 내면 렌더 뒤에 곧바로
        커밋하는 자리가 낡은 대장을 초록으로 읽는다(실측: 좌표를 없는 파일로 바꾼
        사본에서 `--render`가 exit 0 「발견 0건」, 같은 사본 `--check`가 exit 1)."""
        root = base(**{"전거/의존.md": q(
            "## <<의존:샘플>> 표본\n요지: 밖이 정본이다\n\n"
            "정본: 저장소 밖\n"
            "딛는 자리: scripts/없는파일.py\n")})
        rc, out = self._run("--render", "--root", str(root))
        self.assertEqual(rc, 1, out)
        self.assertIn("E 역포인터", out)

    def test_check도_E_역포인터를_낸다(self):
        """`check()`가 `check_backpointers()`를 합치는 자리를 CLI 종료값으로 잰다.
        E의 다른 시험은 함수 직접 호출이거나 `--render` 경로이고, `--check` 시험의
        표본은 의존 대장을 담지 않는다 — 그 합성을 지워도 전건 통과한다(실측).
        그러면 `--root`로 준 사본에서 `--check`를 게이트로 쓰는 자리가 낡은 좌표를
        무발견·exit 0으로 읽는다."""
        root = base(**{"전거/의존.md": q(
            "## <<의존:샘플>> 표본\n요지: 밖이 정본이다\n\n"
            "정본: 저장소 밖\n"
            "딛는 자리: scripts/없는파일.py\n")})
        rc, out = self._run("--check", "--root", str(root))
        self.assertEqual(rc, 1, out)
        self.assertIn("E 역포인터", out)

    def test_render가_바꾼_파일을_알린다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n")})
        rc, out = self._run("--render", "--root", str(root))
        self.assertEqual(rc, 0)
        self.assertIn("SKILL.md", out)

    def test_없는_root는_오류다(self):
        """무발견 exit 0을 내면 오타 난 루트가 자동화에서 초록으로 읽힌다."""
        rc, _ = self._run("--check", "--root", str(Path(tempfile.mkdtemp()) / "없다"))
        self.assertEqual(rc, 2)

    def test_refs가_빈_ID여도_check로_흐르지_않는다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n")})
        rc, out = self._run("--refs", "", "--root", str(root))
        self.assertNotIn("렌더 불일치", out, "요구한 하위명령이 아닌 것이 돌았다")

    def test_refs가_ID를_받는다(self):
        root = base(**{"SKILL.md": q("<<상태>>\n")})
        rc, out = self._run("--refs", "상태", "--root", str(root))
        self.assertEqual(rc, 0)
        self.assertIn("SKILL.md", out)


class StructureCheckTest(unittest.TestCase):
    """검사 D — 형태 위반. 이것이 없으면 형태가 어긋난 입력이 조용히 틀린 답을 낸다."""

    def _D(self, root):
        """형태 발견만. `D 차단`은 그 귀결이지 형태 위반의 계수가 아니다."""
        return [f for f in dag_facts.check(root) if f.startswith("D 형태")]

    def test_요지_줄이_없으면_낸다(self):
        root = tree(**{"전거/x.md": q("## <<상태>> 제목\n\n본문만 있다.\n")})
        self.assertEqual(len(self._D(root)), 1, dag_facts.check(root))

    def test_요지가_비면_낸다(self):
        root = tree(**{"전거/x.md": q("## <<상태>> 제목\n요지:\n")})
        self.assertEqual(len(self._D(root)), 1, dag_facts.check(root))

    def test_요지가_헤딩과_떨어지면_낸다(self):
        """빈 줄 하나가 요지를 본문으로 밀어 값이 조용히 빈 튜플이 된다."""
        root = tree(**{"전거/x.md": q("## <<상태>> 제목\n\n요지: 가 · 나\n")})
        found = self._D(root)
        self.assertTrue(found, "요지가 본문으로 밀린 것을 내지 않았다")
        self.assertTrue(any("요지" in f for f in found), found)

    def test_기계값이_본문으로_밀리면_낸다(self):
        root = tree(**{"전거/x.md": q('## <<예산>> 제목\n요지: a\n\n기계값: {"a": 1}\n')})
        found = self._D(root)
        self.assertTrue(any("기계값" in f for f in found), found)

    def test_기계값이_파이썬_리터럴이_아니면_낸다(self):
        root = tree(**{"전거/x.md": q('## <<예산>> 제목\n요지: a\n기계값: {"a": 1,,}\n')})
        self.assertEqual(len(self._D(root)), 1, dag_facts.check(root))

    def test_요지에_괄호가_있으면_낸다(self):
        root = tree(**{"전거/x.md": q("## <<상태>> 제목\n요지: 가<<나 · 다\n")})
        self.assertEqual(len(self._D(root)), 1, dag_facts.check(root))

    def test_인용_꼴이_아닌_괄호를_낸다(self):
        """사람 눈에 인용인데 도구가 인식하지 못하는 셋. 죽은 인용의 원천이다."""
        root = base(**{"SKILL.md": q("1 << 상태 >>\n2 <<상태·옛값>>\n3 <<상태 >>\n")})
        found = self._D(root)
        self.assertEqual(len(found), 3, found)

    def test_전거_디렉토리가_없으면_낸다(self):
        root = tree(**{"SKILL.md": "무관\n"})
        self.assertEqual(len(self._D(root)), 1, dag_facts.check(root))

    def test_항목_자신의_머리_줄은_렌더가_건드리지_않는다(self):
        """`요지:`·`기계값:`은 정본 데이터지 인용 자리가 아니다."""
        root = base(**{"전거/갑.md": q("## <<갑>> 제목\n요지: 가<<상태>>나\n")})
        before = read(root, "전거/갑.md")
        dag_facts.render(root)
        self.assertEqual(read(root, "전거/갑.md"), before, "전거 정본을 고쳐 썼다")

    def test_형태가_어긋난_항목은_렌더가_건드리지_않는다(self):
        """D를 내면서 값을 밀어 넣으면 옳던 상수가 빈 값으로 덮인다."""
        root = tree(**{
            "전거/x.md": q("## <<상태>> 제목\n\n요지: 가 · 나\n"),
            "s.py": q("# <<생성 상태>>\nSTATES = ('가', '나')\n# <<끝>>\n"),
            "SKILL.md": q("<<상태>>\n"),
        })
        dag_facts.render(root)
        self.assertIn("STATES = ('가', '나')", read(root, "s.py"),
                      "형태가 어긋난 항목의 빈 값이 옳던 상수를 덮었다")
        self.assertEqual(read(root, "SKILL.md"), q("<<상태>>\n"))

    def test_생성_블록에_대입이_둘이면_낸다(self):
        root = base(**{"s.py": q("# <<생성 상태>>\nA = ()\nB = ()\n# <<끝>>\n")})
        self.assertTrue(self._D(root), dag_facts.check(root))

    def test_생성_블록에_주석이_있으면_낸다(self):
        root = base(**{"s.py": q("# <<생성 상태>>\nA = ()\n# 설명\n# <<끝>>\n")})
        self.assertTrue(self._D(root), dag_facts.check(root))


class BlockBoundaryTest(unittest.TestCase):
    """블록의 끝을 잘못 잡으면 렌더가 소스와 산문을 지운다. 셋 다 실측된 파괴다."""

    def test_닫히지_않은_생성_블록이_뒤_블록을_삼키지_않는다(self):
        src = q("# <<생성 상태>>\nFIRST = ()\ndef 보존할함수():\n    return 1\n"
                "# <<생성 상태>>\nSECOND = ()\n# <<끝>>\n")
        root = base(**{"s.py": src})
        found = [f for f in dag_facts.check(root) if f.startswith("D")]
        self.assertTrue(any("닫히지" in f for f in found), dag_facts.check(root))
        dag_facts.render(root)
        out = read(root, "s.py")
        self.assertIn("def 보존할함수():", out, "블록 밖 소스를 지웠다")
        self.assertIn("SECOND", out, "둘째 블록을 지웠다")

    def test_닫히지_않은_전거_블록이_뒤_울타리를_삼키지_않는다(self):
        md = ("```전거 상태\n낡음\n\n## 무관한 절\n보존할 산문.\n\n"
              "```python\nprint(1)\n```\n\n끝 문단.\n")
        root = base(**{"d.md": md})
        found = [f for f in dag_facts.check(root) if f.startswith("D")]
        self.assertTrue(found, dag_facts.check(root))
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn("## 무관한 절", out, "블록 밖 산문을 지웠다")
        self.assertIn("print(1)", out, "무관한 코드 예시를 지웠다")

    def test_본문에_울타리가_있어도_블록이_멱등이다(self):
        item = q("## <<울타리>> 제목\n요지: 가 · 나\n\n예시:\n\n```python\nx = 1\n```\n\n뒷 문단.\n")
        root = tree(**{"전거/x.md": item, "d.md": "```전거 울타리\n```\n뒤 산문\n"})
        dag_facts.render(root)
        first = read(root, "d.md")
        changed, _ = dag_facts.render(root)
        self.assertEqual(changed, [], "본문 울타리에서 렌더가 발산한다")
        self.assertEqual(read(root, "d.md"), first)
        self.assertIn("x = 1", first)
        self.assertIn("뒤 산문", first, "블록 뒤 산문을 지웠다")
        self.assertEqual(dag_facts.check(root), [])

    def test_생성_블록_다중_대입은_건드리지_않는다(self):
        root = base(**{"s.py": q("# <<생성 상태>>\nA = ()\n# 설명\nB = 1\n# <<끝>>\n")})
        dag_facts.render(root)
        out = read(root, "s.py")
        self.assertIn("# 설명", out)
        self.assertIn("B = 1", out)

    def test_짝_없는_닫는_마커를_형태로_낸다(self):
        """`INLINE_RE`가 먼저 잡으면 「A 미해결 인용 <<끝>>」이 되어, 없는 항목을
        등재하라고 지시한다. 실제 결함은 짝을 잃은 닫는 마커다."""
        root = base(**{"s.py": q("STATES = ('가', '나')\n# <<끝>>\n")})
        found = dag_facts.check(root)
        self.assertTrue(
            any(f.startswith("D 형태") and "짝" in f for f in found), found)
        self.assertEqual([f for f in found if f.startswith("A")], [], found)


class FenceLengthTest(unittest.TestCase):
    """울타리 길이 경로. 백틱 셋만 시험하면 넷 이상에서 가드가 빠진 것을 못 본다."""

    ITEM = q("## <<상태>> 제목\n요지: 가 · 나\n\n본문.\n")
    SWALLOW = ("낡음\n\n## 무관한 절\n보존할 산문.\n\n{f}md\n예시 표\n{f}\n\n끝 문단.\n")

    def _tree(self, fence: str):
        md = f"{fence}전거 상태\n" + self.SWALLOW.format(f=fence)
        return tree(**{"전거/x.md": self.ITEM, "d.md": md})

    def test_백틱_넷으로_열린_블록도_삼킴을_낸다(self):
        """백틱 셋에서만 서는 가드는 넷에서 산문을 지운다."""
        for fence in ("```", "````", "`````"):
            with self.subTest(fence=fence):
                root = self._tree(fence)
                found = [f for f in dag_facts.check(root) if f.startswith("D")]
                self.assertTrue(found, f"{fence}: 삼킴을 내지 않았다")
                dag_facts.render(root)
                out = read(root, "d.md")
                self.assertIn("## 무관한 절", out, f"{fence}: 산문을 지웠다")
                self.assertIn("예시 표", out, f"{fence}: 내용을 지웠다")

    def test_짝이_맞는_본문_울타리는_삼킴이_아니다(self):
        """렌더가 스스로 낸 산출을 삼킴으로 오판하면 영구히 붉다."""
        item = q("## <<상태>> 제목\n요지: 가 · 나\n\n```python\nx = 1\n```\n")
        root = tree(**{"전거/x.md": item, "d.md": "```전거 상태\n```\n뒤 산문\n"})
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        self.assertIn("x = 1", read(root, "d.md"))

    def test_저자가_넷으로_연_정상_블록(self):
        root = tree(**{"전거/x.md": self.ITEM, "d.md": "````전거 상태\n````\n뒤 산문\n"})
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn("요지: 가 · 나", out)
        self.assertIn("뒤 산문", out)
        changed, _ = dag_facts.render(root)
        self.assertEqual(changed, [])

    def test_닫는_울타리가_더_길어도_인식한다(self):
        root = tree(**{"전거/x.md": self.ITEM, "d.md": "```전거 상태\n`````\n뒤 산문\n"})
        self.assertEqual([f for f in dag_facts.check(root) if "닫히지" in f], [])
        dag_facts.render(root)
        self.assertIn("요지: 가 · 나", read(root, "d.md"))

    def test_전거_블록도_어긋난_항목이면_건드리지_않는다(self):
        root = tree(**{"전거/x.md": q("## <<갑>> 제목\n요지:\n"),
                       "d.md": "```전거 갑\n옳던 블록 내용\n```\n"})
        dag_facts.render(root)
        self.assertIn("옳던 블록 내용", read(root, "d.md"))


class GenBlockContentTest(unittest.TestCase):
    """생성 블록은 대입 하나만 담는다. 그 규칙이 실제로 집행되는가."""

    def test_후행_주석을_낸다(self):
        """1b가 옮길 상수의 주석은 전부 후행형이다. 줄 전체 주석만 보면 못 잡는다."""
        root = base(**{"s.py": q("# <<생성 상태>>\nSTATES = ()  # 손으로 단 설명\n# <<끝>>\n")})
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("D")],
                        dag_facts.check(root))
        dag_facts.render(root)
        self.assertIn("손으로 단 설명", read(root, "s.py"))

    def test_블록_안_무관한_소스를_낸다(self):
        src = q("# <<생성 상태>>\nSTATES = ()\n\ndef 보존할함수():\n    return 1\n\n# <<끝>>\n")
        root = base(**{"s.py": src})
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("D")],
                        dag_facts.check(root))
        dag_facts.render(root)
        self.assertIn("def 보존할함수", read(root, "s.py"))

    def test_기계값은_길어도_줄을_나누지_않는다(self):
        long_machine = "{" + ", ".join(f'"키{i}": {i}' for i in range(12)) + "}"
        root = tree(**{"전거/x.md": q(f"## <<긴값>> 제목\n요지: a\n기계값: {long_machine}\n"),
                       "s.py": q("# <<생성 긴값>>\nV = {}\n# <<끝>>\n")})
        dag_facts.render(root)
        self.assertIn(f"V = {long_machine}\n", read(root, "s.py"))


class LiteralSafetyTest(unittest.TestCase):
    def test_요지_원소의_따옴표와_역슬래시가_보존된다(self):
        """리터럴 검사는 기계값에만 있다. 요지 파생은 깨진 파이썬을 낼 수 있었다."""
        parts = ['가"나', "다\\라", "마"]
        root = tree(**{"전거/x.md": q("## <<따옴표>> 제목\n요지: " + " · ".join(parts) + "\n"),
                       "s.py": q("# <<생성 따옴표>>\nV = ()\n# <<끝>>\n")})
        dag_facts.render(root)
        line = [l for l in read(root, "s.py").splitlines() if l.startswith("V = ")][0]
        self.assertEqual(ast.literal_eval(line.split(" = ", 1)[1]), tuple(parts))
        self.assertEqual(dag_facts.check(root), [])

    def test_원소가_하나면_후행_쉼표가_붙는다(self):
        """쉼표가 빠지면 튜플이 아니라 문자열이 된다 — 센티널이 그 형태다."""
        root = tree(**{"전거/x.md": q("## <<센티널>> 제목\n요지: <!-- 행 끝 -->\n"),
                       "s.py": q("# <<생성 센티널>>\nV = ()\n# <<끝>>\n")})
        dag_facts.render(root)
        line = [l for l in read(root, "s.py").splitlines() if l.startswith("V = ")][0]
        self.assertIsInstance(ast.literal_eval(line.split(" = ", 1)[1]), tuple)


class ScanScopeTest(unittest.TestCase):
    def test_전거_밖_파일의_선언_꼴은_렌더된다(self):
        """`is_facts_file` 게이트의 부정 방향. 예외가 전거 밖으로 새면 죽은 인용이 된다."""
        root = base(**{"SKILL.md": q("## <<상태>> 아무 제목\n")})
        dag_facts.render(root)
        self.assertIn("미착수 · 진행", read(root, "SKILL.md"))

    def test_선언_줄_제목의_축자_괄호를_낸다(self):
        root = tree(**{"전거/x.md": q("## <<갑>> 제목 << 이상한 >>\n요지: 가\n")})
        self.assertTrue([f for f in dag_facts.check(root) if "괄호" in f],
                        dag_facts.check(root))

    def test_pycache는_스캔하지_않는다(self):
        root = base(**{"__pycache__/x.md": q("<<없는것>>\n")})
        self.assertEqual(dag_facts.check(root), [])

    def test_A_발견이_옳은_줄_번호를_싣는다(self):
        root = base(**{"SKILL.md": q("첫 줄\n둘째 줄\n<<없는것>>\n")})
        found = [f for f in dag_facts.check(root) if f.startswith("A")]
        self.assertEqual(len(found), 1, found)
        self.assertIn("SKILL.md:3", found[0])


class WrapTest(unittest.TestCase):
    def test_줄바꿈은_코드포인트가_아니라_표시폭으로_잰다(self):
        """전각 문자는 1코드포인트가 2열이다. 코드포인트로 재면 눈으로 넘쳐도 안 나뉜다."""
        stages = (
            "ＡＢＣＤ", "ＥＦＧＨ", "ＩＪＫＬ", "ＭＮＯＰ",
            "ＱＲＳＴ", "ＵＶＷＸ", "ＹＺＡＢ", "ＣＤＥＦ",
        )
        lit = "(" + ", ".join(f'"{t}"' for t in stages) + ")"
        one = f"NODE_SETTLEMENT_STAGES = {lit}"
        self.assertLessEqual(len(one), dag_facts.WRAP_WIDTH,
                             "표본이 코드포인트로는 상한 안이어야 이 시험이 성립한다")
        root = tree(**{
            "전거/x.md": q(f"## <<단계노드>> 노드 싱크 단계\n요지: {' · '.join(stages)}\n"),
            "s.py": q("# <<생성 단계노드>>\nNODE_SETTLEMENT_STAGES = ()\n# <<끝>>\n"),
        })
        dag_facts.render(root)
        self.assertIn("NODE_SETTLEMENT_STAGES = (\n", read(root, "s.py"))


class SourceSafetyTest(unittest.TestCase):
    """인라인 인용은 요지를 날것으로 써 넣는다 — 생성 블록과 달리 이스케이프가 없다.

    파이썬 파일에서 그 자리가 문자열 리터럴이면 따옴표는 소스를 깨뜨리고 역슬래시는
    이스케이프로 먹혀 **값이 조용히 갈린다**. 둘 다 렌더 후 `--check`가 무발견이다.
    """

    def _root(self, gist: str):
        return tree(**{"전거/x.md": q(f"## <<갑>> 제목\n요지: {gist}\n"),
                       "s.py": q('D = "(<<갑>>)"\n')})

    def _잰다(self, gist: str):
        root = self._root(gist)
        before = read(root, "s.py")
        found = dag_facts.check(root)
        self.assertTrue([f for f in found if f.startswith("D")],
                        f"D가 서야 한다 — {found}")
        dag_facts.render(root)
        self.assertEqual(read(root, "s.py"), before, "렌더가 건드리면 안 된다")

    def test_요지의_따옴표가_파이썬_소스로_들어가지_않는다(self):
        self._잰다('가 "나" 다')

    def test_요지의_역슬래시가_파이썬_소스로_들어가지_않는다(self):
        self._잰다(r"경로 C:\tmp")

    def test_주석_자리는_위험_문자를_받는다(self):
        """위험은 자리의 성질이지 요지의 내용이 아니다. 주석에는 이스케이프가 없어
        따옴표도 역슬래시도 소스를 깨뜨리지 못한다 — 거기까지 막으면 과차단이고,
        인용을 못 거는 자리가 좌표 문자열을 지게 된다."""
        root = tree(**{"전거/x.md": q("## <<갑>> 제목\n요지: 금지 문자(`~^:?*[\\`)는 깨뜨린다\n"),
                       "s.py": q("# 규칙은 <<갑>>이다.\n")})
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        out = read(root, "s.py")
        self.assertIn("금지 문자", out)
        compile(out, "s.py", "exec")

    def test_문자열_리터럴_자리는_여전히_막는다(self):
        root = tree(**{"전거/x.md": q("## <<갑>> 제목\n요지: 금지 문자(`~^:?*[\\`)는 깨뜨린다\n"),
                       "s.py": q('D = "(<<갑>>)"\n')})
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("D")])

    def test_읽을_수_없는_파이썬_소스는_전부_위험_자리다(self):
        """`_string_rows`는 토큰화가 실패하면 `None`을 내고, 렌더는 그 파일의 모든
        행을 문자열 리터럴 자리로 본다. 실패를 빈 집합으로 바꾸면 이미 문법이 깨진
        소스에 따옴표가 든 요지가 들어가 값이 갈리고 `--check`가 조용하다(실측)."""
        root = tree(**{"전거/x.md": q('## <<갑>> 제목\n요지: 가 "나" 다\n'),
                       "s.py": q('def f(:\n    D = "(<<갑>>)"\n')})
        self.assertIsNone(dag_facts._string_rows(read(root, "s.py")))
        before = read(root, "s.py")
        found = dag_facts.check(root)
        self.assertTrue([f for f in found if f.startswith("D")],
                        f"D가 서야 한다 — {found}")
        dag_facts.render(root)
        self.assertEqual(read(root, "s.py"), before, "렌더가 건드리면 안 된다")

    def test_성한_요지는_그대로_채운다(self):
        """가드가 성한 입력까지 막으면 인라인 인용이 파이썬에서 죽는다."""
        root = self._root("가 · 나")
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        self.assertIn(q("(<<갑 · 가 · 나>>)"), read(root, "s.py"))


class RenderBlockingTest(unittest.TestCase):
    def test_막힌_파일을_발견이_지목한다(self):
        """차단이 파일 층위인데 발견은 어긋난 자리만 가리킨다. 그 파일의 다른
        인용·생성 블록이 함께 멈춘 것을 저자가 알 길이 없다."""
        root = base(**{"s.py": q(
            "# <<생성 상태>>\n# <<생성 예산>>\nSTATES = ()\n# <<끝>>\n")})
        _, found = dag_facts.render(root)
        self.assertTrue([f for f in found if f.startswith("D 차단")], found)

    def test_D를_낸_파일은_렌더가_통째로_건드리지_않는다(self):
        """검출과 차단은 다른 일이다. 미닫힘 블록을 내고 스캔을 이어 가면 다음 여는
        마커가 앞 블록의 대입과 끝 마커를 자기 것으로 삼아 값을 덮는다(실측)."""
        root = base(**{"s.py": q(
            "# <<생성 상태>>\n# <<생성 예산>>\nSTATES = ()\n# <<끝>>\n")})
        before = read(root, "s.py")
        _, found = dag_facts.render(root)
        self.assertTrue([f for f in found if f.startswith("D")], found)
        self.assertEqual(read(root, "s.py"), before)


class FactsDirTest(unittest.TestCase):
    """등록소를 읽는 경로. 적재와 스캔이 같은 범위를 봐야 한다."""

    def test_BOM이_붙어도_첫_선언이_인식된다(self):
        """BOM은 첫 선언을 인식 밖으로 밀어낸다. 그러면 그 항목의 인용이 전부
        `A 미해결 인용`으로 뒤집혀 보고되고, 선언 자신도 그렇게 보고된다 — 원인과
        증상이 어긋나 저자가 BOM을 의심할 길이 없다.

        발견으로 내지 않고 벗겨서 읽는다. D로 내면 파일 층위 차단이 렌더를 막아
        BOM이 영구히 남는다."""
        root = tree(**{"전거/x.md": "﻿" + q("## <<갑>> 제목\n요지: 가 · 나\n"),
                       "s.md": q("<<갑>>\n")})
        items, findings = dag_facts.load_items(root / "전거")
        self.assertIn("갑", items)
        self.assertEqual(findings, [])
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        self.assertIn(q("<<갑 · 가 · 나>>"), read(root, "s.md"))

    def test_스킵_디렉토리의_선언은_적재되지_않는다(self):
        """적재가 재귀가 되면서 스캔이 거르는 디렉토리를 함께 훑는다. 스캔 밖에
        사는 파일이 스캔 안 파일들의 값을 정하고, 형태 검사도 닿지 않는다."""
        root = tree(**{"전거/실행.md": STATE_ITEM,
                       "전거/__pycache__/x.md": q("## <<상태>> 오염\n요지: 오염값\n")})
        items, findings = dag_facts.load_items(root / "전거")
        self.assertEqual(findings, [])
        self.assertEqual(items["상태"].gist, GIST)

    def test_BOM은_낡음으로_잡혀_렌더가_벗긴다(self):
        """`_read`가 벗겨 읽으므로 BOM은 인용 구간 밖의 바이트다. 낡음에 넣지
        않으면 도구가 그 바이트를 **다른 이유로 파일을 쓸 때만** 말없이 지운다 —
        같은 트리에서 어떤 파일은 잃고 어떤 파일은 남긴다."""
        root = tree(**{"전거/x.md": "﻿" + q("## <<갑>> 제목\n요지: 가 · 나\n"),
                       "d.md": "﻿본문뿐. 인용 없음\n"})
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("C")])
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        for rel in ("전거/x.md", "d.md"):
            with root.joinpath(*rel.split("/")).open("rb") as fh:
                self.assertNotEqual(fh.read(3), b"\xef\xbb\xbf", rel)

    def test_refs가_하위_디렉토리_선언을_정본으로_센다(self):
        """`--refs`는 「이 사실의 정본이 어디인가」에 답하는 유일한 명령이다.
        적재·렌더가 재귀가 됐는데 여기만 얕게 남으면 정본이 0자리로 보인다."""
        root = tree(**{"전거/실행.md": STATE_ITEM,
                       "전거/하위/y.md": q("## <<을>> 제목\n요지: 다 · 라\n"),
                       "s.md": q("<<을>>\n")})
        dag_facts.render(root)
        rows = dag_facts.refs(root, "을")
        self.assertEqual(len([r for r in rows if ": 정본" in r]), 1, rows)
        self.assertEqual(len([r for r in rows if ": 인용" in r]), 1, rows)

    def test_하위_디렉토리의_선언도_항목으로_적재된다(self):
        """스캔은 재귀인데 적재가 얕으면 그 선언은 정본이 되지 못한 채 인용으로
        렌더된다 — 등록소가 자기 항목을 남의 인용 자리로 읽는다."""
        root = tree(**{
            "전거/실행.md": STATE_ITEM,
            "전거/하위/y.md": q("## <<을>> 제목\n요지: 가 · 나\n"),
            "s.md": q("<<을>>\n"),
        })
        items, findings = dag_facts.load_items(root / "전거")
        self.assertIn("을", items)
        self.assertEqual(findings, [])
        dag_facts.render(root)
        self.assertEqual(dag_facts.check(root), [])
        self.assertIn(q("<<을 · 가 · 나>>"), read(root, "s.md"))
        self.assertIn(q("## <<을>> 제목"), read(root, "전거/하위/y.md"))


class BlockProjectionTest(unittest.TestCase):
    def test_블록_렌더가_경계_줄을_투영하지_않는다(self):
        """임시/do-dag_정본단일화_기안_2026-07-28.md §2.1 — `- _경계_`·`- _실패 유형_`은 등록소를 읽는 개정자만 본다.
        소비 자리로 밀려 나가는 것은 사실이지 그 사실에 대한 주석이 아니다."""
        root = tree(**{
            "전거/x.md": q("## <<갑>> 제목\n요지: 가 · 나\n\n본문 한 줄.\n"
                           "- _경계_ 개정자만 본다.\n- _실패 유형_ 이것도.\n"),
            "d.md": q("```전거 갑\n```\n"),
        })
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn("본문 한 줄.", out)
        self.assertNotIn("개정자만 본다", out)
        self.assertNotIn("이것도", out)
        self.assertEqual(dag_facts.check(root), [], "멱등이어야 한다")

    def test_울타리_안의_경계_표기는_살아남는다(self):
        """항목이 경계 표기법 자체를 예시로 담으면 그 예시가 지워져 빈 울타리만
        남는다. 투영에서 뺄 것은 항목이 단 방주이지 항목이 인용한 문면이 아니다."""
        root = tree(**{
            "전거/x.md": q("## <<갑>> 제목\n요지: 가 · 나\n\n본문.\n\n"
                           "```md\n- _경계_ 이렇게 쓴다\n```\n"),
            "d.md": q("````전거 갑\n````\n"),
        })
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn("이렇게 쓴다", out)
        self.assertEqual(dag_facts.check(root), [], "멱등이어야 한다")

    def test_들여쓴_블록도_렌더된다(self):
        """목록 항목 안의 블록을 지나치면 낡은 내용이 남은 채 `--check`가 조용하다.
        생성 블록은 이미 앞머리 공백을 받는다 — 두 블록 문법이 같아야 한다."""
        root = tree(**{
            "전거/x.md": q("## <<갑>> 제목\n요지: 가 · 나\n"),
            "d.md": "- 목록:\n\n  ```전거 갑\n  낡은 내용\n  ```\n\n뒤 산문\n",
        })
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("C")],
                        "들여쓴 블록을 통째로 지나쳤다")
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn("  ```전거 갑\n  요지: 가 · 나\n  ```\n", out)
        self.assertNotIn("낡은 내용", out)
        self.assertIn("뒤 산문", out, "블록 뒤 산문을 지웠다")
        self.assertEqual(dag_facts.check(root), [], "멱등이어야 한다")

    def test_블록이_본문의_인라인_인용을_풀어_싣는다(self):
        """`item.body`는 렌더 전의 문면이다. 그대로 투영하면 첫 렌더가 저자형을
        밀어 넣고 둘째 렌더가 그 자리를 또 바꿔 멱등이 깨진다."""
        root = tree(**{
            "전거/x.md": q("## <<갑>> 제목\n요지: 갑요지\n\n"
                           "완결 상태는 <<을>>이다.\n\n"
                           "## <<을>> 제목\n요지: 완 · 비준\n"),
            "d.md": q("```전거 갑\n```\n"),
        })
        changed, _ = dag_facts.render(root)
        self.assertEqual(len(changed), 2, f"첫 렌더가 둘을 다 채우지 않았다: {changed}")
        first = read(root, "d.md")
        self.assertIn(q("완결 상태는 <<을 · 완 · 비준>>이다."), first)
        changed, _ = dag_facts.render(root)
        self.assertEqual(changed, [], "둘째 렌더가 파일을 바꿨다")
        self.assertEqual(read(root, "d.md"), first)

    def test_블록_투영이_어긋난_항목의_인라인_인용을_그대로_둔다(self):
        """`_resolve_inline`은 피인용 항목의 형태가 어긋나면 저자형을 보존한다.
        그 가드가 빠지면 빈 요지가 소비 블록에 정상값처럼 실린다 — D 발견은 전거
        파일의 그 항목을 가리키므로, 소비 자리만 읽는 사람은 요지가 실제로 비어
        있다고 읽는다."""
        root = tree(**{
            "전거/x.md": q("## <<갑>> 제목\n요지: 갑요지\n\n"
                           "완결 상태는 <<을>>이다.\n\n"
                           "## <<을>> 제목\n요지:\n"),
            "d.md": q("```전거 갑\n```\n"),
        })
        self.assertTrue([f for f in dag_facts.check(root) if f.startswith("D")])
        dag_facts.render(root)
        out = read(root, "d.md")
        self.assertIn(q("완결 상태는 <<을>>이다."), out)
        self.assertNotIn(q("<<을 · >>"), out)


class AtomicWriteTest(unittest.TestCase):
    def test_쓰기가_중단돼도_원본이_남고_잔재가_없다(self):
        """직접 절단 쓰기는 렌더 중 중단되면 부분 기록을 남긴다. 렌더가 한 번에
        여러 파일을 쓰므로 중단은 실제 경로다."""
        root = tree(**{"x.md": "원본\n"})
        path = root / "x.md"
        with mock.patch("dag_facts.os.replace", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                dag_facts._write(path, "새것\n")
        self.assertEqual(read(root, "x.md"), "원본\n")
        self.assertEqual([p.name for p in root.iterdir()], ["x.md"])

    def test_교체가_거부되면_직접_쓰기로_물러선다(self):
        """Windows는 대상 파일을 누가 **읽기로만** 열고 있어도 `os.replace`를
        거부한다. 물러설 곳이 없으면 회귀다 — 한 파일 안의 부분 기록을 막으려다
        여러 파일에 걸친 부분 렌더를 만든다."""
        root = tree(**{"x.md": "원본\n"})
        with mock.patch("dag_facts.os.replace", side_effect=OSError("교체 거부")):
            dag_facts._write(root / "x.md", "새것\n")
        self.assertEqual(read(root, "x.md"), "새것\n")
        self.assertEqual([p.name for p in root.iterdir()], ["x.md"])

    def test_대상이_읽기로_열려_있어도_렌더가_완주한다(self):
        """위 회귀의 실물 형태. 한 파일이 잠겨 렌더가 죽으면 그 앞 파일은 이미
        쓰였고 뒤 파일은 안 쓰였다 — 이 변경이 막겠다고 든 바로 그 상태다."""
        root = base(**{"a.md": q("<<상태>>\n"), "b.md": q("<<상태>>\n"),
                       "c.md": q("<<상태>>\n")})
        with (root / "b.md").open(encoding="utf-8"):
            changed, findings = dag_facts.render(root)
        self.assertEqual(findings, [])
        for name in "abc":
            self.assertIn("미착수 · 진행", read(root, f"{name}.md"), name)


class RealTreeTest(unittest.TestCase):
    """대역이 아니라 실물 전거를 연다."""

    def setUp(self):
        self.items, self.dup = dag_facts.load_items(dag_facts.FACTS_DIR)

    def test_전거_적재가_이중_정본도_형태_결함도_내지_않는다(self):
        self.assertEqual(self.dup, [])

    def test_스킬_전체가_전거_검사를_통과한다(self):
        self.assertEqual(dag_facts.check(dag_facts.ROOT), [])

    def test_옮긴_상수의_값이_전거_항목과_같다(self):
        """전거를 고치고 `--render`를 잊으면 여기가 붉어진다. 검사 C와 다른 축이다 —
        C는 파일의 문면을 보고, 이것은 실제로 적재되는 값을 본다."""
        for iid, module, name in MOVED:
            with self.subTest(항목=iid):
                self.assertIn(iid, self.items)
                self.assertEqual(
                    ast.literal_eval(self.items[iid].value_literal()),
                    getattr(module, name))

    def test_옮긴_상수가_생성_블록_안에_있다(self):
        """1b의 구조적 산출. 값이 같아도 블록이 없으면 다음 개정이 코드를 직접 고친다."""
        for iid, module, name in MOVED:
            with self.subTest(항목=iid):
                self.assertEqual(generated_name(module, iid), name)

    def test_단계_원장_두_항목의_표가_값을_순서대로_설명한다(self):
        """상수에 후행 주석으로 붙어 있던 사실. 값에서 파생되지 않으므로 본문이 진다 —
        생성 블록은 대입 하나만 담고 렌더가 주석을 지운다.

        **값 이름의 등장만 재면 안 된다.** 옆 항목을 인용한 줄에 같은 낱말이 들어
        있어 표를 통째로 지워도 통과한다(실측 4/10). 표의 행을 순서대로 뽑아 상수와
        견주고 설명 두 칸이 비지 않았는지 함께 본다 — 순서가 계약이기도 하다."""
        for iid, name in (("단계원장-노드", "NODE_SETTLEMENT_STAGES"),
                          ("단계원장-국면", "PHASE_SETTLEMENT_STAGES")):
            with self.subTest(항목=iid):
                body = self.items[iid].body if iid in self.items else ""
                rows = re.findall(r"^\| `([^`]+)` \|([^|]*)\|([^|]*)\|",
                                  body, re.M)
                self.assertEqual([v.split()[0] for v, _, _ in rows],
                                 list(getattr(dag_check, name)))
                for v, a, b in rows:
                    self.assertTrue(a.strip() and b.strip(),
                                    f"{v} 행의 설명 칸이 비었다")

    def test_완결상태가_상태_어휘_안에_있다(self):
        """항목 **사이**의 파생 관계는 어느 검사도 보지 않는다. `상태`에서 한
        낱말을 고치고 `완결상태`를 두면 `--check`가 초록인 채로 하류 흘려보내기가
        조용히 막힌다(실측)."""
        self.assertLessEqual(set(dag_check.DONE_STATES), set(dag_check.STATES))

    def test_예산의_요지가_기계값과_이어진다(self):
        """임시/do-dag_정본단일화_기안_2026-07-28.md §5-1⑴이 이 항목에 방어를 두지 않은 근거는 「기계로 잇지 못하므로」다.
        `k`를 천 배로 읽으면 이어진다 — 면제의 전제가 성립하지 않는다."""
        item = self.items["예산"]
        derived = {}
        for part in item.gist_parts():
            name, value = part.rsplit(" ", 1)
            derived[name] = int(value.rstrip("k")) * 1000
        self.assertEqual(derived, ast.literal_eval(item.machine))

    def test_기계값이_요지와_어긋나지_않는다(self):
        """`기계값:` 줄은 손으로 유지된다 — 요지만 고치면 상수는 그대로이고
        `--check`는 무발견을 낸다(실측). 두 표기가 기계로 이어지는 항목은 여기서 잰다.
        `예산`은 `150k`와 `150_000`이라 이을 수 없어 대상이 아니다(임시/do-dag_정본단일화_기안_2026-07-28.md §5-1⑴)."""
        for iid, take, expect in (
                ("이름문법", lambda m: m["요지"], lambda i: i.gist),
                ("센티널", lambda m: m, lambda i: i.gist_parts()[0])):
            with self.subTest(항목=iid):
                item = self.items[iid]
                self.assertEqual(take(ast.literal_eval(item.machine)),
                                 expect(item))

    def test_이름문법의_두_표기가_같은_상한을_말한다(self):
        """요지는 사람이 읽고 패턴은 기계가 집행한다. 허용 문자의 두 표기
        (「글자·숫자」와 `\\w`)는 기계로 잇지 못하지만 상한은 이어진다 — 실제로 갈릴
        값이 그 하나다.

        요지의 상한만 128로 고치면 `--render`도 `--check`도 초록인 채 국면명 100자가
        「128자 이하」라는 문면과 함께 거부된다(실측)."""
        machine = ast.literal_eval(self.items["이름문법"].machine)
        gist_limit = re.search(r"\((\d+)자 이하\)", machine["요지"])
        pattern_limit = re.search(r"\{1,(\d+)\}", machine["패턴"])
        self.assertIsNotNone(gist_limit, "요지가 상한을 말하지 않는다")
        self.assertIsNotNone(pattern_limit, "패턴이 상한을 말하지 않는다")
        self.assertEqual(gist_limit.group(1), pattern_limit.group(1))

    def test_의존_대장이_비지_않았고_딛는_자리가_전부_실재한다(self):
        """E. 정본이 스킬 밖인 사실에는 `grep ID`가 서지 않는다 — 대장이 그 대신 딛는
        자리를 싣는다. 좌표가 낡으면 정본이 바뀔 때 무엇이 깨지는지 아무도 못 찾는다.

        빈 대장 위의 무발견은 공허참이므로 항목이 실제로 있는지 함께 잰다."""
        ledger = dag_facts.FACTS_DIR / "의존.md"
        deps = [i for i, it in self.items.items() if it.path == ledger]
        self.assertTrue(deps, "의존 대장이 비었다")
        self.assertEqual(
            dag_facts.check_backpointers(dag_facts.FACTS_DIR, dag_facts.ROOT), [])

    def test_의존_대장의_항목마다_정본과_증상이_선다(self):
        """대장 서두가 항목마다 정본·딛는 자리·증상 셋을 들라 적고 「증상」이 이 대장의
        값이라 적는다. 검사 E가 보는 것은 셋 중 「딛는 자리」 하나뿐이라, 나머지 둘은
        여덟 항목에서 열여섯 줄을 통째로 지워도 `--check`가 무발견을 낸다(실측).
        정본이 스킬 밖인 사실은 깨져도 이 저장소가 조용하므로, 증상 줄이 없으면 깨진
        자리를 만난 사람이 원인을 밖에서 찾을 길이 없다 — 그 줄의 실재를 여기서 잰다.

        빈 대장 위의 통과는 공허참이므로 항목이 실제로 있는지 함께 잰다."""
        ledger = dag_facts.FACTS_DIR / "의존.md"
        deps = [i for i, it in self.items.items() if it.path == ledger]
        self.assertTrue(deps, "의존 대장이 비었다")
        for iid in deps:
            with self.subTest(항목=iid):
                for row in ("정본", "증상"):
                    self.assertRegex(self.items[iid].body,
                                     rf"(?m)^{row}:[ \t]*\S",
                                     f"{row} 줄이 없거나 비었다")

    def test_없는_딛는_자리는_E를_낸다(self):
        """판별성. 검사가 실재를 실제로 보는지를 없는 좌표 하나로 가른다."""
        root = base(**{
            "scripts/있는파일.py": "x = 1\n",
            "전거/의존.md": q(
                "## <<의존:샘플>> 표본\n요지: 밖이 정본이다\n\n"
                "정본: 저장소 밖\n"
                "딛는 자리: scripts/있는파일.py · scripts/없는파일.py\n")})
        findings = dag_facts.check_backpointers(root / "전거", root)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("없는파일.py", findings[0])
        self.assertTrue(findings[0].startswith("E "), findings[0])

    def test_딛는_자리가_없는_의존_항목은_E를_낸다(self):
        """판별성. 있는 줄의 좌표만 훑으면 `전거/의존.md`의 여덟 줄을 다 지워도
        `--check`가 exit 0을 내고 시험도 전건 통과한다(실측). 부재는 좌표 0건이라
        순회가 조용히 빈다 — 줄의 실재를 따로 세지 않으면 아무도 잡지 않는다."""
        root = base(**{"전거/의존.md": q(
            "## <<의존:샘플>> 표본\n요지: 밖이 정본이다\n\n"
            "정본: 저장소 밖\n")})
        findings = dag_facts.check_backpointers(root / "전거", root)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("의존:샘플", findings[0])
        self.assertTrue(findings[0].startswith("E "), findings[0])

    def test_값이_빈_딛는_자리는_다음_줄을_좌표로_삼지_않는다(self):
        """판별성. `BACKPOINTER_RE`의 뒤를 `\\s*`로 넓히면 값이 빈 줄이 개행을 삼켜
        다음 줄의 실재 경로를 좌표로 잡는다. 그러면 좌표 계수가 올라 줄 부재 판정이
        꺼지고, 대장이 딛는 자리를 하나도 싣지 않은 채 초록으로 선다(실측: 넓힌
        변이본에서 시험이 전건 통과했다). 줄 부재만 재는 앞 시험은 이 축을 가르지
        못한다 — 그 표본에는 `딛는 자리:` 줄 자체가 없다."""
        root = base(**{
            "scripts/있는파일.py": "x = 1\n",
            "전거/의존.md": q(
                "## <<의존:샘플>> 표본\n요지: 밖이 정본이다\n\n"
                "정본: 저장소 밖\n"
                "딛는 자리:\n"
                "scripts/있는파일.py\n")})
        findings = dag_facts.check_backpointers(root / "전거", root)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("의존:샘플", findings[0])
        self.assertTrue(findings[0].startswith("E "), findings[0])

    def test_대장_소속을_ID_접두가_아니라_파일로_가른다(self):
        """판별성. 「딛는 자리」를 요구하는 근거는 대장 파일 서두이지 ID 접두가 아니다.
        소속을 `의존:` 접두로 가르는 구현으로 바꿔도 앞의 두 시험은 붉어지지 않는다 —
        두 표본이 다 접두를 달고 있어서다. 접두 없는 대장 항목과 대장 밖의 접두 항목을
        함께 세워 그 축을 가른다."""
        root = base(**{
            "전거/의존.md": q(
                "## <<외부표기>> 표본\n요지: 밖이 정본이다\n\n"
                "정본: 저장소 밖\n"),
            "전거/실행.md": STATE_ITEM + q(
                "\n## <<의존:대장밖>> 표본\n요지: 안이 정본이다\n")})
        findings = dag_facts.check_backpointers(root / "전거", root)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("외부표기", findings[0])
        self.assertTrue(findings[0].startswith("E "), findings[0])

    def test_디렉토리_좌표와_낡은_저장소안_정본이_E를_낸다(self):
        """판별성. 좌표의 실재만 재면 파일 좌표가 상위 디렉토리로 뭉개져도 초록이
        선다(실측: `딛는 자리: scripts`가 무발견을 냈다). 「정본」 줄은 어느 인식기도
        물지 않아 저장소 안 정본이 옮겨져도 조용하다. 두 분기를 함께 가른다.

        저장소 루트는 `.git`을 진 조상이므로 표본 루트에 그 자리를 깐다."""
        root = base(**{
            ".git/HEAD": "ref: refs/heads/master\n",
            "scripts/있는파일.py": "x = 1\n",
            "전거/의존.md": q(
                "## <<의존:디렉토리>> 표본\n요지: 밖이 정본이다\n\n"
                "정본: 저장소 밖\n"
                "딛는 자리: scripts\n\n"
                "## <<의존:정본좌표>> 표본\n요지: 안이 정본이다\n\n"
                "정본: `없는설정.json` (저장소 안, 주석을 못 받는 형식)\n"
                "딛는 자리: scripts/있는파일.py\n")})
        findings = dag_facts.check_backpointers(root / "전거", root)
        self.assertEqual(len(findings), 2, findings)
        self.assertTrue(all(f.startswith("E ") for f in findings), findings)
        self.assertTrue(any("의존:디렉토리" in f for f in findings), findings)
        self.assertTrue(any("없는설정.json" in f for f in findings), findings)

    def test_예산표가_모델_어휘를_전건_덮는다(self):
        """`모델`의 요지와 `예산`의 기계값 열쇠가 같은 집합이어야 `run_budget`이
        판정을 낸다. 그 관계를 A~E도 다른 시험도 보지 않는다 — `모델` 요지에
        모델 하나를 더하면 `--render`·`--check`와 시험 일곱이 전부 초록인 채
        `MODELS`만 늘고, 검산 ⑨가 그 행을 통과시킨 뒤 예산 블록이 「예산 안/예산
        초과」 대신 「미지 모델」을 exit 0으로 낸다(실측)."""
        self.assertEqual(set(dag_check.MODELS), set(dag_measure.BUDGETS))

    def test_이름문법에서_파생한_둘이_사전을_딛는다(self):
        """파생이 끊어지면 값이 갈려도 아무 검사가 서지 않는다 — 두 대입이 실제로
        사전을 딛는지를 잰다. 딛지 않으면 그 자리가 두 번째 정본이다.

        **값 동등은 파생을 재지 못한다.** 파생을 끊고 같은 값 리터럴을 박으면
        `--check`도 시험도 전부 초록이다(실측). 소스를 파싱해 두 대입의 우변이
        `_NAME`을 어느 열쇠로 읽는지 뽑고, 뽑은 값이 실제로 적재된 값과 같은지를
        이어서 잰다 — 우변이 사전을 읽어도 열쇠가 어긋나면 값이 갈린다."""
        tree_ = ast.parse(Path(dag_marker.__file__).read_text(encoding="utf-8"))
        keys = {}
        for node in ast.walk(tree_):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            name = getattr(node.targets[0], "id", None)
            if name not in ("NAME_RULE", "PHASE_RE"):
                continue
            keys[name] = {
                sub.slice.value for sub in ast.walk(node.value)
                if isinstance(sub, ast.Subscript)
                and isinstance(sub.value, ast.Name) and sub.value.id == "_NAME"
                and isinstance(sub.slice, ast.Constant)}
        self.assertEqual(keys, {"NAME_RULE": {"요지"}, "PHASE_RE": {"패턴"}})
        self.assertEqual(dag_marker.NAME_RULE, dag_marker._NAME["요지"])
        self.assertEqual(dag_marker.PHASE_RE.pattern, dag_marker._NAME["패턴"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
