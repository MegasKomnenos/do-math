# -*- coding: utf-8 -*-
"""장 파일들을 순서대로 이어 원고.md를 만들고, 진술 라벨을 번호로 푼다.

사용: python 조립.py [--out 원고.md] [--keep-labels]
입력: 상위 폴더의 장/장1.md … 장/장4.md, 장/장5A.md, 장/장5B.md, 장/장6.md … 장/장9.md, 장/부록A.md, 장/부록B.md, 장/부록C.md.
없는 파일은 건너뛰고 그 사실을 적는다(중간 판본에도 쓴다).

라벨 규칙(집필 공통 지침 7절):
  진술 머리  **정리 {{old:정리 2.13}} (이름) [지위; r…].**  또는  **정리 {{new:7:AR}} (…) [...].**
  참조       정리 {{old:정리 2.13}}, 명제 {{new:8:prop-S}}
  번호는 진술 머리가 놓인 장(## N. 머리)과 그 장 안의 등장 순서로 매긴다(장마다 1부터, 종류 공통 계수기).
  한 라벨은 진술 머리에 정확히 한 번 나와야 한다. 머리에 없는 라벨을 참조하면 실패로 적고 라벨을 남긴다.
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS = ["장1.md", "장2.md", "장3.md", "장4.md", "장5A.md", "장5B.md", "장6.md", "장7.md", "장8.md", "장9.md", "부록A.md", "부록B.md", "부록C.md"]  # 5장은 5A(5.1–5.4)·5B(5.5) 두 파일
TITLE = "# 주차함수 최대 변위 개수열의 단봉성: 증명\n"
LABEL_RE = re.compile(r"\{\{(old|new):([^}]+)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(old|new):([^}]+)\}\}(?= \(| \[|\.\*\*|\*\*)")  # '…의 증명.**' 같은 증명 머리는 정의로 세지 않는다
CHAPTER_RE = re.compile(r"^## (\d+)\.")
LITERAL_RE = re.compile(r"(?<![가-힣{:])(정리|명제|보조정리|따름정리|정의) \d+\.\d+(?![\d}])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "원고.md"))
    ap.add_argument("--keep-labels", action="store_true")
    args = ap.parse_args()
    pieces = [TITLE]
    missing = []
    problems = []
    texts = {}
    for name in PARTS:
        path = os.path.join(ROOT, "장", name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        text = io.open(path, encoding="utf-8").read()
        if not text.endswith("\n"):
            text += "\n"
        texts[name] = text
    # 5장: 장5A.md는 5.1–5.4와 5.6–5.7, 장5B.md는 5.5이므로 5B를 5A의 「### 5.6」 앞에 끼운다(독해 1의 지적 5).
    if "장5A.md" in texts and "장5B.md" in texts:
        a = texts["장5A.md"]
        cut = a.find("\n### 5.6")
        if cut < 0:
            problems.append("장5A.md에 「### 5.6」 머리가 없어 5.5를 제자리에 끼우지 못함")
        else:
            texts["장5A.md"] = a[:cut + 1] + "\n" + texts["장5B.md"] + a[cut + 1:]
            del texts["장5B.md"]
    for name in PARTS:
        if name in texts:
            pieces.append("\n" + texts[name])
    # 장 파일의 옛 번호 리터럴 검사: 라벨·기록 이름 괄호·문헌 표기 밖의 「정리 x.y」는 조립 뒤 다른 진술을 가리킬 수 있다
    literal_warnings = []
    for name, text in texts.items():
        for ln_no, ln in enumerate(text.split("\n"), 1):
            for m in LITERAL_RE.finditer(ln):
                before = ln[max(0, m.start() - 40): m.start()]
                if "{{old:" in ln[max(0, m.start() - 6): m.start()] or "기록 [" in before or "의 " == ln[max(0, m.start() - 2): m.start()] and "기록" in before:
                    continue
                literal_warnings.append(f"{name}:{ln_no}: 옛 번호 리터럴 '{m.group(0)}' (라벨이어야 하면 고칠 것) … {ln[max(0, m.start() - 30): m.end() + 20]}")
    if literal_warnings:
        print(f"[경고: 라벨 밖 진술 번호 {len(literal_warnings)}건 — 문헌·기록 번호 언급이면 정상]")
        for w in literal_warnings:
            print(" ", w)
    out = "".join(pieces)
    if not args.keep_labels:
        lines = out.split("\n")
        numbers = {}
        counters = {}
        chapter = 0
        for ln in lines:
            m = CHAPTER_RE.match(ln)
            if m:
                chapter = int(m.group(1))
                counters.setdefault(chapter, 0)
                continue
            h = HEAD_RE.match(ln)
            if h:
                key = f"{h.group(2)}:{h.group(3)}"
                if chapter == 0:
                    problems.append(f"장 머리 밖의 진술 라벨 {key}")
                    continue
                if key in numbers:
                    problems.append(f"라벨 중복 정의 {key}")
                    continue
                counters[chapter] += 1
                numbers[key] = f"{chapter}.{counters[chapter]}"
        used = set()
        def sub(m):
            key = f"{m.group(1)}:{m.group(2)}"
            used.add(key)
            if key in numbers:
                return numbers[key]
            problems.append(f"정의되지 않은 라벨 참조 {key}")
            return m.group(0)
        out = LABEL_RE.sub(sub, out)
        unused = sorted(set(numbers) - used)
        print(f"라벨 {len(numbers)}개 해소, 참조된 라벨 {len(used)}개")
        if unused:
            print("참조 없는 라벨(정의만 있음): " + ", ".join(unused))
    io.open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(f"조립: {args.out} ({len(out.encode('utf-8'))} bytes, {out.count(chr(10))} lines)")
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
