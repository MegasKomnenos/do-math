# -*- coding: utf-8 -*-
"""둘째 판: 장 파일들을 순서대로 이어 원고.md를 만들고 라벨을 번호로 푼다.

사용: python 조립_v2.py [--out 원고.md] [--keep-labels]
입력: 상위 폴더의 장v2/장1.md … 장v2/장11.md, 장v2/부록A.md, 장v2/부록B.md, 장v2/부록C.md,
      부록 D는 장v2/부록D_장N.md(N=1..11)를 장 순서로 이어 「## 부록 D. 계산 증거 자료」 아래에 둔다.
없는 파일은 건너뛰고 그 사실을 적는다(중간 판본에도 쓴다).

라벨 규칙(집필 공통 지침 v2 7절):
  진술 머리  **정리 {{6:F-prime}} (이름) [지위; r…].**   또는  **정리 {{6:old-7-13}} (…) [...].**
  참조       정리 {{6:F-prime}}
  번호는 진술 머리가 놓인 장(## N. 머리)과 그 장 안의 등장 순서로 매긴다(장마다 1부터, 종류 공통 계수기).
  라벨의 장 번호 N은 머리가 놓인 장과 같아야 한다.
  부록 D 항목 머리  ### D.{{D:이름}} 제목   참조  부록 D.{{D:이름}}
  한 라벨은 머리에 정확히 한 번 나와야 한다. 머리에 없는 라벨을 참조하면 실패로 적고 라벨을 남긴다.
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
APPENDICES = ["부록A.md", "부록B.md", "부록C.md"]


def chapter_files(base, prefix="장"):
    """장N.md 또는 나뉘어 쓰인 장NA.md, 장NB.md…(장 번호 순, 조각은 글자 순). prefix는 '장' 또는 '부록D_장'."""
    out = []
    for i in range(1, 12):
        whole = f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base, whole)):
            out.append(whole)
            continue
        parts = sorted(n for n in os.listdir(base) if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md", n))
        out.extend(parts if parts else [whole])
    return out
TITLE = "# 주차함수 최대 변위 개수열의 단봉성: 증명\n"
LABEL_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
D_LABEL_RE = re.compile(r"\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
D_HEAD_RE = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
CHAPTER_RE = re.compile(r"^## (\d+)\.")
LITERAL_RE = re.compile(r"(?<![가-힣{:A-Za-z])(정리|명제|보조정리|따름정리|정의) \d+\.\d+(?![\d}])")
LEGACY_RE = re.compile(r"\{\{(old|new|sym):")


def read(path):
    text = io.open(path, encoding="utf-8").read()
    if not text.endswith("\n"):
        text += "\n"
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "원고.md"))
    ap.add_argument("--keep-labels", action="store_true")
    args = ap.parse_args()
    base = os.path.join(ROOT, "장v2")
    pieces = [TITLE]
    missing, problems, warnings = [], [], []
    for name in chapter_files(base, "장") + APPENDICES:
        path = os.path.join(base, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        text = read(path)
        pieces.append("\n" + text)
        for ln_no, ln in enumerate(text.split("\n"), 1):
            if LEGACY_RE.search(ln):
                problems.append(f"{name}:{ln_no}: 첫 판 라벨 꼴 또는 임시 기호 {LEGACY_RE.search(ln).group(0)}…")
            for m in LITERAL_RE.finditer(ln):
                before = ln[max(0, m.start() - 40): m.start()]
                if "기록 [" in before or "Theorem" in before:
                    continue
                warnings.append(f"{name}:{ln_no}: 라벨 밖 진술 번호 '{m.group(0)}' … {ln[max(0, m.start() - 30): m.end() + 20]}")
    d_texts = []
    for name in chapter_files(base, "부록D_장"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            d_texts.append(read(path))
    if d_texts:
        pieces.append("\n## 부록 D. 계산 증거 자료\n\n" + "\n".join(d_texts))
    out = "".join(pieces)
    if warnings:
        print(f"[경고: 라벨 밖 진술 번호 {len(warnings)}건 — 문헌 번호 언급이면 정상]")
        for w in warnings:
            print(" ", w)
    if not args.keep_labels:
        lines = out.split("\n")
        numbers, counters = {}, {}
        chapter = 0
        d_numbers, d_count = {}, 0
        for ln in lines:
            m = CHAPTER_RE.match(ln)
            if m:
                chapter = int(m.group(1))
                counters.setdefault(chapter, 0)
                continue
            if ln.startswith("## 부록"):
                chapter = -1
                continue
            h = HEAD_RE.match(ln)
            if h:
                lab_ch, name = int(h.group(2)), h.group(3)
                key = f"{lab_ch}:{name}"
                if chapter <= 0:
                    problems.append(f"장 머리 밖의 진술 라벨 {key}")
                    continue
                if lab_ch != chapter:
                    problems.append(f"라벨의 장 번호 {lab_ch}가 놓인 장 {chapter}와 다름: {key}")
                if key in numbers:
                    problems.append(f"라벨 중복 정의 {key}")
                    continue
                counters[chapter] += 1
                numbers[key] = f"{chapter}.{counters[chapter]}"
                continue
            d = D_HEAD_RE.match(ln)
            if d:
                name = d.group(1)
                if name in d_numbers:
                    problems.append(f"부록 D 라벨 중복 {name}")
                    continue
                d_count += 1
                d_numbers[name] = f"{d_count}"
        used, d_used = set(), set()

        def sub(m):
            key = f"{m.group(1)}:{m.group(2)}"
            used.add(key)
            if key in numbers:
                return numbers[key]
            problems.append(f"정의되지 않은 라벨 참조 {key}")
            return m.group(0)

        def dsub(m):
            name = m.group(1)
            d_used.add(name)
            if name in d_numbers:
                return d_numbers[name]
            problems.append(f"정의되지 않은 부록 D 라벨 참조 {name}")
            return m.group(0)

        out = LABEL_RE.sub(sub, out)
        out = D_LABEL_RE.sub(dsub, out)
        unused = sorted(set(numbers) - used)
        print(f"라벨 {len(numbers)}개 해소, 참조된 라벨 {len(used)}개; 부록 D 항목 {len(d_numbers)}개, 참조된 항목 {len(d_used)}개")
        if unused:
            print("참조 없는 라벨(정의만 있음): " + ", ".join(unused))
        d_unused = sorted(set(d_numbers) - d_used)
        if d_unused:
            problems.append("본문이 가리키지 않는 부록 D 항목: " + ", ".join(d_unused))
    todo = len(re.findall(r"\[todo", out))
    io.open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(f"조립: {args.out} ({len(out.encode('utf-8'))} bytes, {out.count(chr(10))} lines); [todo] {todo}개")
    if missing:
        print("없는 조각: " + ", ".join(missing))
    if problems:
        print(f"[문제 {len(problems)}건]")
        for p in sorted(set(problems)):
            print(" ", p)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
