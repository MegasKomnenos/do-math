# -*- coding: utf-8 -*-
"""기억 그래프 색인 무결성 CHECK.

색인.md·색인_아카이브.md의 줄 id 집합과 기억/layer{1,2,3}/ 파일 집합을 양방향 대조한다.
승인 근거: D-0019 제안 1(M-0054 색인 줄 id 오기 2회 신호). 실행 시점: dream 커밋 직전
수동 실행(세칙_dream.md v20). 상시 훅이 아니다(병행 세션의 일반 커밋에 개입하지 않는 설계).

검사: (1) 모든 노드 파일 id가 색인+아카이브에 정확히 1회 등장, (2) 모든 줄 id에 실재 파일,
(3) L 줄은 색인.md에만(아카이브의 L 줄은 소멸 노드 잔재로 오류).
exit 0 = 정합, exit 1 = 불일치(내역 출력).
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 기억/
ID_RE = re.compile(r"^- ([MDL]-\d{4}) ", re.M)


def file_ids():
    ids = set()
    for layer in ("layer1", "layer2", "layer3"):
        d = os.path.join(ROOT, layer)
        for fn in os.listdir(d):
            m = re.match(r"([MDL]-\d{4})\.md$", fn)
            if m:
                ids.add(m.group(1))
    return ids


def line_ids(path):
    text = io.open(path, encoding="utf-8").read()
    found = ID_RE.findall(text)
    dupes = {i for i in found if found.count(i) > 1}
    return found, dupes


def main():
    files = file_ids()
    idx_list, idx_dupes = line_ids(os.path.join(ROOT, "색인.md"))
    arc_list, arc_dupes = line_ids(os.path.join(ROOT, "색인_아카이브.md"))
    errors = []

    for i in sorted(idx_dupes | arc_dupes):
        errors.append(f"중복 줄: {i}")
    both = set(idx_list) & set(arc_list)
    for i in sorted(both):
        errors.append(f"색인·아카이브 동시 등장: {i}")

    lines = set(idx_list) | set(arc_list)
    for i in sorted(files - lines):
        errors.append(f"파일은 있으나 색인 줄 없음: {i}")
    for i in sorted(lines - files):
        errors.append(f"색인 줄은 있으나 파일 없음: {i}")

    for i in sorted(set(arc_list)):
        if i.startswith("L-"):
            errors.append(f"아카이브에 L 줄(소멸 노드 잔재?): {i}")

    if errors:
        print("[validate_memory_index] 불일치 %d건" % len(errors))
        for e in errors:
            print(" -", e)
        return 1
    print("[validate_memory_index] 정합: 파일 %d개 = 색인 %d + 아카이브 %d줄" % (
        len(files), len(set(idx_list)), len(set(arc_list))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
