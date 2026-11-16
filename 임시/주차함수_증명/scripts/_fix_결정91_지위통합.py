# -*- coding: utf-8 -*-
"""결정 91: 지위 낱말 「비형식 증명」을 「증명됨」에 합친다. 외부 입력(연구 문헌의 정리, 컴퓨터 계산)은 덧붙임 「문헌 인용」·「계산 보조」가 이미 표시한다.
(1) 장v2/장*.md 진술 머리의 지위 괄호 안 「비형식 증명」→「증명됨」, (2) 장1 1.5 표의 행 삭제와 「증명됨」 뜻 확장, (3) 장부_v2·구조표_v2의 「다섯 지위」 서술.
같은 머리에서 지위가 둘 다 「증명됨」이 되어 「(가)는 증명됨, (나)는 증명됨」 꼴이 남는 곳은 출력한다(손질은 Edit). 멱등. --dry 지원."""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
HEAD = re.compile(r"^(\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{\d+:[A-Za-z0-9\-]+\}\}.*?)\[([^\]]*)\](; [^\]]*)?\.\*\*", re.M)


def main():
    total = 0
    dup = []
    for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
        s = io.open(p, encoding="utf-8").read()
        lines = s.split("\n")
        changed = 0
        for i, ln in enumerate(lines):
            if not ln.startswith("**") or "비형식 증명" not in ln:
                continue
            k = ln.find(".**")
            if k < 0:
                continue
            head, rest = ln[:k + 3], ln[k + 3:]
            a = head.rfind("[")
            if a < 0:
                continue
            new_head = head[:a] + head[a:].replace("비형식 증명", "증명됨")
            if new_head != head:
                changed += 1
                lines[i] = new_head + rest
                if len(re.findall(r"증명됨", new_head[a:])) >= 2:
                    dup.append((os.path.basename(p), i + 1, new_head[a:][:160]))
        if changed:
            total += changed
            print(os.path.basename(p), changed)
            if not DRY:
                io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("머리 교체", total)
    for d in dup:
        print("  지위 중복 손질 필요:", d)
    # (2) 장1 1.5 표
    p1 = os.path.join(ROOT, "장v2", "장1.md")
    s = io.open(p1, encoding="utf-8").read()
    old_row = "| 증명됨 | 증명의 모든 단계가 이 글 안에 손으로 적힌 결과. 교과서 수준의 표준 결과를 진술과 출처와 함께 인용한 단계나 이 글의 앞선 진술에 기대는 단계가 있어도 이 지위다 |"
    new_row = "| 증명됨 | 증명이 이 글 안에 적힌 결과. 교과서 수준의 표준 결과를 진술과 출처와 함께 인용한 단계나 이 글의 앞선 진술에 기대는 단계가 있어도 이 지위이고, 연구 문헌의 정리나 컴퓨터 계산에 기대는 단계가 있으면 덧붙임 「문헌 인용」과 「계산 보조」가 그 단계를 표시한다 |"
    row_informal = re.search(r"\| 비형식 증명 \|[^\n]*\n", s)
    n1 = 0
    if old_row in s:
        s = s.replace(old_row, new_row); n1 += 1
    if row_informal:
        s = s.replace(row_informal.group(0), ""); n1 += 1
    print("장1 1.5 표 편집", n1)
    for m in re.finditer("비형식 증명", s):
        ln = s.count("\n", 0, m.start()) + 1
        print("  장1 남은 언급:", ln, s[max(0, m.start() - 80):m.end() + 80].replace("\n", " ⏎ "))
    if not DRY:
        io.open(p1, "w", encoding="utf-8", newline="\n").write(s)
    # (3) 장부·구조표
    for rel, old, new in [
        ("장부_v2.md", "다섯 지위 낱말(증명됨, 비형식 증명, 계산 증거, 형식 증명, 추측·발견적)", "네 지위 낱말(증명됨, 계산 증거, 형식 증명, 추측·발견적)"),
        ("구조표_v2.md", "다섯 지위의 정의 표(증명됨·비형식 증명·계산 증거·형식 증명·추측·발견적; 뒤 둘은 이 글에 쓰이지 않음)", "네 지위의 정의 표(증명됨·계산 증거·형식 증명·추측·발견적; 뒤 둘은 이 글에 쓰이지 않음)"),
    ]:
        pp = os.path.join(ROOT, rel)
        t = io.open(pp, encoding="utf-8").read()
        if old in t:
            t = t.replace(old, new); print(rel, "고침")
            if not DRY:
                io.open(pp, "w", encoding="utf-8", newline="\n").write(t)
        elif new in t:
            print(rel, "이미")
        else:
            print(rel, "앵커 없음")


if __name__ == "__main__":
    main()
