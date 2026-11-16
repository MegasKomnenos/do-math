# -*- coding: utf-8 -*-
r"""수식 구분자 밖에 남은 TeX 표기와 수식 안에 삼켜진 산문을 찾는다. `_katex_check.py`의 보완이며,
`불변식_v2.py`가 불변식 9로 부른다(실패 조건).

배경. `_katex_check.py`는 `$…$`·`$$…$$` 안만 KaTeX로 렌더해 오류를 세므로, 구분자 밖(인라인 코드 구간 `…`, 평문)에
쓰인 `e_n^{(k+1)}` 같은 TeX 표기는 KaTeX에 닿지 않아 오류 0으로 통과하고 PDF에 글자 그대로 찍힌다(2026-11-15 558쪽).
반대로 `$`가 빠져 산문이 수식 안으로 들어가면 KaTeX는 한글을 조용히 그리므로 역시 오류 0이다.

검사 항목(모두 실패):
  (가) 인라인 코드 구간 안의 TeX 흔적: `^{`, `_{`, `\명령`(역슬래시 뒤 글자 둘 이상).
  (나) 수식·코드를 걷어 낸 평문의 TeX 흔적: `^{`, `_{`, `\명령`(역슬래시 뒤 글자). Markdown 탈출 `\*`·`\_`·`\[` 등은 글자가 아니라 제외.
  (다) 한 줄 안의 `$` 홀수(디스플레이 수식을 걷어 낸 뒤).
  (라) 수식 안의 한글(`\text{…}`·`\mathrm{…}` 등 글자 명령의 인자 밖).
울타리 코드 블록(```)은 제외한다. 코드 구간은 줄 안에서 백틱을 차례로 짝지어 자른다.

사용: python -I _tex_outside_math_check.py [파일 ...]   (기본: 장v2/*.md 와 원고.md)
종료 코드: 발견 0건이면 0, 아니면 1.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = chr(92)  # backslash (heredoc 등이 역슬래시를 먹는 경로를 피해 문자로 만든다)
TEX_IN_CODE = re.compile(r"\^\{|_\{|" + BS + BS + r"[A-Za-z]{2,}")
TEX_IN_TEXT = re.compile(r"\^\{|_\{|" + BS + BS + r"[A-Za-z]+")
TEXT_CMD_ARG = re.compile(BS + BS + r"(?:text|textrm|textbf|textit|mathrm|mbox|operatorname)\s*\{[^{}]*\}")
HANGUL = re.compile(r"[가-힣]")
FENCE = re.compile(r"```.*?```", re.S)
DMATH = re.compile(r"\$\$.+?\$\$", re.S)
IMATH = re.compile(r"\$[^$\n]+?\$")


def code_spans(line):
    """줄 안의 단일 백틱 코드 구간 내용을 차례로 돌려준다(여닫이를 순서대로 짝지음)."""
    out, i = [], 0
    while True:
        a = line.find("`", i)
        if a < 0:
            break
        b = line.find("`", a + 1)
        if b < 0:
            break
        out.append(line[a + 1:b])
        i = b + 1
    return out


BOOKB_ROW = re.compile(r"^\| r[0-9a-f]{7} \| \d\d-\d\d \d\d:\d\d \| ")


def scan_text(text, name):
    """한 파일의 본문을 검사해 메시지 목록을 돌려준다."""
    msgs = []
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)  # 줄 번호 보존
    for m in DMATH.finditer(text):  # (라) 디스플레이 수식 안의 한글
        if HANGUL.search(TEXT_CMD_ARG.sub("", m.group(0))):
            ln = text.count("\n", 0, m.start()) + 1
            msgs.append(f"{name}:{ln}: (라) 수식 안의 한글: {m.group(0)[:100]!r}")
    text = DMATH.sub(lambda m: "§" + "\n" * m.group(0).count("\n"), text)
    for ln, line in enumerate(text.split("\n"), 1):
        for m in IMATH.finditer(line):  # (라) 인라인 수식 안의 한글
            if HANGUL.search(TEXT_CMD_ARG.sub("", m.group(0))):
                msgs.append(f"{name}:{ln}: (라) 수식 안의 한글: {m.group(0)[:100]}")
        nomath = IMATH.sub("§", line)
        if nomath.count("$") % 2 == 1:  # (다)
            msgs.append(f"{name}:{ln}: (다) 짝 없는 $: {line.strip()[:120]}")
        for sp in code_spans(nomath):  # (가)
            if TEX_IN_CODE.search(sp):
                msgs.append(f"{name}:{ln}: (가) 코드 구간 안의 TeX: `{sp[:120]}`")
        plain = re.sub(r"`[^`\n]*`", "¶", nomath)  # (나)
        m = TEX_IN_TEXT.search(plain)
        if m and BOOKB_ROW.match(line):  # 2026-11-16 결정 122-3: 부록 B의 기록 제목은 record.json의 평문 그대로(`r^{3/2}` 등) — (나)의 대상이 아니다
            m = None
        if m:
            a = max(0, m.start() - 60)
            msgs.append(f"{name}:{ln}: (나) 평문의 TeX: …{plain[a:m.start() + 80].strip()}")
    return msgs


def scan(paths):
    msgs = []
    for p in paths:
        msgs.extend(scan_text(io.open(p, encoding="utf-8").read(), os.path.relpath(p, ROOT)))
    return msgs


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "원고.md")]
    msgs = scan(files)
    for m in msgs:
        print(m)
    print(f"파일 {len(files)}개, 발견 {len(msgs)}건")
    sys.exit(0 if not msgs else 1)


if __name__ == "__main__":
    main()
