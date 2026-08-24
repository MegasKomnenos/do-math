# -*- coding: utf-8 -*-
"""vrlib 공용 파서 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_vrlib.py`).

검사 대상은 여덟으로 한정한다:
① frontmatter 파싱 — 키: 값 사전, 본문 시작 행, 수 키의 정수 해석(fm_int), 비정수 값의 ValueError
② 울타리 인식 절 분할 — `## ` 절 경계, 울타리(```·~~~) 안의 `## ` 줄은 경계가 아님(실물 기안_볼드_발췌.md R1-29)
③ 칸 마커 인식 — 계약이 닫은 `### <칸이름>` 제목 줄 하나만 마커다.
   거부: 볼드(`**칸**`, 기안_볼드_발췌.md) · 평문 대시(`칸 —`, 기안_평문_발췌.md) ·
   평문 콜론(`칸:`) · `####` 이하 제목(칸 내부 제목 — 칸 탈취 부재)
④ 어긋남 좌표(Mismatch) 서식과 emit의 exit 0/1 규약
⑤ 판정·처분·결합·승계 키 줄 해석(parse_status_line) — 계약이 닫은 `<키>: <값>` 반각
   축자만 받는다. 거부: 줄 전체 볼드, `**키:**`·`**키**:`, 공백 없는 `키:값`,
   목록 표지. 값의 볼드는 벗기지 않고 그대로 준다(닫힌 어휘 대조가 하류에서 거른다)
⑥ 개행 보존 — CRLF 파일은 읽을 때 접히고 쓸 때 CRLF로 복원된다. LF 파일은 LF로 남는다
⑦ 동결문 산출물 절 판독(parse_frozen_outputs) — `- <경로>` 줄만 목록이고, 절 부재·
   구간 줄 부재·절대 경로·중복 경로는 UsageError다
⑧ h1 종단(stop_at_h1) — 울타리 밖 `# ` 제목에서 절 수집을 멈추고, 울타리 안 `# ` 줄은
   종단이 아니며, h1이 없으면 종단을 켠 결과가 끈 결과와 같다

그 밖의 검사는 두지 않는다.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import vrlib  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


def read(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


class FrontmatterTest(unittest.TestCase):
    def test_기안_frontmatter(self):
        fm, body_start = vrlib.parse_frontmatter(read("기안_볼드_발췌.md"))
        self.assertEqual(fm["유형"], "기안")
        self.assertEqual(fm["기안자 번호"], "2")
        self.assertEqual(vrlib.fm_int(fm, "문면 건수"), 2)
        self.assertEqual(body_start, 6)

    def test_frontmatter_없으면_빈_사전(self):
        fm, body_start = vrlib.parse_frontmatter("# 제목\n\n본문\n")
        self.assertEqual(fm, {})
        self.assertEqual(body_start, 1)

    def test_fm_int_키_없으면_None(self):
        fm, _ = vrlib.parse_frontmatter("---\n항목: 3\n---\n")
        self.assertIsNone(vrlib.fm_int(fm, "지적수"))
        self.assertEqual(vrlib.fm_int(fm, "항목"), 3)

    def test_fm_int_비정수는_ValueError(self):
        fm, _ = vrlib.parse_frontmatter("---\n항목: 셋\n---\n")
        with self.assertRaises(ValueError):
            vrlib.fm_int(fm, "항목")


class SplitSectionsTest(unittest.TestCase):
    def test_울타리_안_절제목은_경계가_아니다(self):
        # 실물: R1-29의 대체 문면 셋째 블록이 「## 계약/심사.md · 계약/수리기안.md」 줄을 담는다.
        secs = vrlib.split_sections(read("기안_볼드_발췌.md"))
        self.assertEqual([s.title for s in secs], ["R1-01", "R1-29"])

    def test_시작_행_번호(self):
        secs = vrlib.split_sections(read("기안_볼드_발췌.md"))
        self.assertEqual(secs[0].start_line, 9)
        self.assertEqual(secs[1].start_line, 31)

    def test_물결_울타리도_인식(self):
        text = "## A\n\n~~~\n## 가짜\n~~~\n\n## B\n"
        secs = vrlib.split_sections(text)
        self.assertEqual([s.title for s in secs], ["A", "B"])

    def test_h1_종단_뒤의_h2는_절로_서지_않는다(self):
        text = "## 지적 하나\n\n본문.\n\n# 수행 기록\n\n## 읽은 범위\n\n- 전건\n"
        secs = vrlib.split_sections(text, stop_at_h1=True)
        self.assertEqual([s.title for s in secs], ["지적 하나"])
        self.assertNotIn("수행 기록", secs[0].body)

    def test_h1_종단은_울타리_안_h1을_지나친다(self):
        text = "## 지적 하나\n\n```\n# 인용 제목\n```\n\n## 지적 둘\n\n본문.\n"
        secs = vrlib.split_sections(text, stop_at_h1=True)
        self.assertEqual([s.title for s in secs], ["지적 하나", "지적 둘"])

    def test_h1이_없으면_종단_켬도_종전과_같다(self):
        text = "## 하나\n\nA.\n\n## 둘\n\nB.\n"
        self.assertEqual(
            [s.title for s in vrlib.split_sections(text, stop_at_h1=True)],
            [s.title for s in vrlib.split_sections(text)])

    def test_하위_제목은_경계가_아니다(self):
        secs = vrlib.split_sections(read("기안_제목_발췌.md"))
        self.assertEqual([s.title for s in secs], ["R1-01", "R1-02"])


CELLS = ["위치", "변경 범위", "형태", "원래 문면", "대체 문면", "근거", "치환"]


class ParseCellsTest(unittest.TestCase):
    def cells_of(self, fixture: str, idx: int = 0) -> dict:
        secs = vrlib.split_sections(read(fixture))
        return vrlib.parse_cells(secs[idx].body, CELLS)

    def test_제목_마커_수용(self):
        cells = self.cells_of("기안_제목_발췌.md")
        self.assertIn("29행", cells["위치"])
        self.assertEqual(cells["변경 범위"].strip(), "1")
        self.assertIn("정의 이해 3항목", cells["원래 문면"])

    def test_평문_대시_칸은_마커가_아니다(self):
        cells = self.cells_of("기안_평문_발췌.md")
        self.assertEqual(cells, {})

    def test_볼드_칸은_마커가_아니다(self):
        cells = self.cells_of("기안_볼드_발췌.md")
        self.assertEqual(cells, {})

    def test_콜론_칸은_마커가_아니다(self):
        body = "위치: 3행\n\n**근거:** 사유다\n"
        cells = vrlib.parse_cells(body, CELLS)
        self.assertEqual(cells, {})

    def test_4층_이하_제목은_칸을_탈취하지_않는다(self):
        body = "### 근거\n\n#### 위치\n\n칸 내부 제목 아래 본문이다.\n"
        cells = vrlib.parse_cells(body, CELLS)
        self.assertNotIn("위치", cells)
        self.assertIn("#### 위치", cells["근거"])
        self.assertIn("칸 내부 제목 아래 본문이다.", cells["근거"])

    def test_칸_이름으로_시작하는_본문_줄은_마커가_아니다(self):
        body = "### 근거\n\n형태 검산 위반 0이라는 본문 줄\n"
        cells = vrlib.parse_cells(body, CELLS)
        self.assertNotIn("형태", cells)
        self.assertIn("본문 줄", cells["근거"])

    def test_울타리_안_마커는_무시(self):
        body = "### 원래 문면\n\n```\n### 형태\n```\n"
        cells = vrlib.parse_cells(body, CELLS)
        self.assertNotIn("형태", cells)
        self.assertIn("### 형태", cells["원래 문면"])


class StatusLineTest(unittest.TestCase):
    def test_닫힌_축자를_받는다(self):
        self.assertEqual(vrlib.parse_status_line("판정: 승인", "판정"), "승인")
        self.assertEqual(vrlib.parse_status_line("결합: R1-18 · R1-32", "결합"),
                         "R1-18 · R1-32")
        self.assertIsNone(vrlib.parse_status_line("판정 결과를 적는다", "판정"))

    def test_볼드_감쌈은_받지_않는다(self):
        for line in ("**판정: 승인**", "**판정:** 승인", "**판정**: 승인"):
            self.assertIsNone(vrlib.parse_status_line(line, "판정"), line)

    def test_공백_없는_콜론은_받지_않는다(self):
        self.assertIsNone(vrlib.parse_status_line("판정:승인", "판정"))

    def test_목록_표지는_받지_않는다(self):
        self.assertIsNone(vrlib.parse_status_line("- 판정: 승인", "판정"))

    def test_값의_볼드는_벗기지_않는다(self):
        self.assertEqual(vrlib.parse_status_line("판정: **승인**", "판정"), "**승인**")


class NewlineTest(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root = Path(d.name)

    def test_CRLF_왕복_보존(self):
        p = self.root / "crlf.md"
        p.write_bytes("하나\r\n둘\r\n".encode("utf-8"))
        text = vrlib.read_text(p)
        self.assertEqual(text, "하나\n둘\n")
        vrlib.write_text(p, text + "셋\n")
        self.assertEqual(p.read_bytes(), "하나\r\n둘\r\n셋\r\n".encode("utf-8"))

    def test_LF_파일은_LF로_남는다(self):
        p = self.root / "lf.md"
        p.write_bytes("하나\n둘\n".encode("utf-8"))
        text = vrlib.read_text(p)
        vrlib.write_text(p, text + "셋\n")
        self.assertEqual(p.read_bytes(), "하나\n둘\n셋\n".encode("utf-8"))


class EmitTest(unittest.TestCase):
    def test_어긋남이_있으면_1과_stderr_좌표(self):
        out, err = io.StringIO(), io.StringIO()
        m = vrlib.Mismatch(file="x.md", line=4, expected="3", actual="2")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = vrlib.emit([m], ["요약"])
        self.assertEqual(code, 1)
        self.assertIn("x.md", err.getvalue())
        self.assertIn("4", err.getvalue())
        self.assertIn("기대=3", err.getvalue())
        self.assertIn("실측=2", err.getvalue())

    def test_어긋남이_없으면_0과_stdout_수치(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = vrlib.emit([], ["항목 0건"])
        self.assertEqual(code, 0)
        self.assertIn("항목 0건", out.getvalue())
        self.assertEqual(err.getvalue(), "")


class FrozenOutputsTest(unittest.TestCase):
    """⑦ 동결문 산출물 절 판독 — 산출물 목록의 정본이 동결문 하나임을 세운다."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def 쓰기(self, text: str) -> Path:
        p = self.tmp / "동결.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_구간_줄만_목록이다(self):
        # 절 머리의 산문 한 줄과 백틱은 목록에 들지 않는다.
        p = self.쓰기("# 동결문\n\n## 산출물\n\n추적 파일 둘이다.\n\n"
                    "- 제품.md\n- `하위/둘째.md`\n\n## 목적 진술\n\n- 미끼.md\n")
        self.assertEqual(vrlib.parse_frozen_outputs(p),
                         ["제품.md", "하위/둘째.md"])

    def test_절이_없으면_UsageError(self):
        p = self.쓰기("# 동결문\n\n## 목적 진술\n\n없다.\n")
        with self.assertRaises(vrlib.UsageError):
            vrlib.parse_frozen_outputs(p)

    def test_구간_줄이_없으면_UsageError(self):
        p = self.쓰기("# 동결문\n\n## 산출물\n\n산문만 있다.\n")
        with self.assertRaises(vrlib.UsageError):
            vrlib.parse_frozen_outputs(p)

    def test_절대_경로는_UsageError(self):
        p = self.쓰기(f"# 동결문\n\n## 산출물\n\n- {self.tmp / '제품.md'}\n")
        with self.assertRaises(vrlib.UsageError):
            vrlib.parse_frozen_outputs(p)

    def test_상위_경로는_UsageError(self):
        p = self.쓰기("# 동결문\n\n## 산출물\n\n- ../제품.md\n")
        with self.assertRaises(vrlib.UsageError):
            vrlib.parse_frozen_outputs(p)

    def test_중복_경로는_UsageError(self):
        # 중복이 서면 사본 뜨기와 영역 검산의 계수가 갈린다.
        p = self.쓰기("# 동결문\n\n## 산출물\n\n- 제품.md\n- 제품.md\n")
        with self.assertRaises(vrlib.UsageError):
            vrlib.parse_frozen_outputs(p)


if __name__ == "__main__":
    unittest.main()
