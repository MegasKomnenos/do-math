# -*- coding: utf-8 -*-
"""dream 2026-11-06: 색인.md의 layer-1 줄 전부를 id 순으로 색인_아카이브.md로 이관한다.

사용: python 임시/dream-20261106/archive_index.py [--apply]
--apply 없이 실행하면 이관할 줄 수와 처음·마지막 id만 출력한다(dry run).
layer-2 절은 손대지 않는다(이번 사이클의 D 줄은 메인이 직접 쓴다).
줄 끝은 LF로 유지한다(newline='').
"""
import io
import re
import sys

IDX = "기억/색인.md"
ARC = "기억/색인_아카이브.md"
LINE_RE = re.compile(r"^- (M-\d{4}) ")


def main(apply: bool) -> int:
    idx = io.open(IDX, encoding="utf-8", newline="").read()
    arc = io.open(ARC, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in idx else "\n"
    lines = idx.split(nl)

    # 절 경계
    try:
        i1 = lines.index("## layer-1")
        i2 = lines.index("## layer-2")
    except ValueError:
        print("절 머리를 찾지 못함")
        return 1

    head = lines[:i1 + 1]
    body = lines[i1 + 1:i2]
    tail = lines[i2:]

    m_lines = {}
    other = []
    for ln in body:
        m = LINE_RE.match(ln)
        if m:
            m_lines[m.group(1)] = ln
        elif ln.strip():
            other.append(ln)
    # layer-2 절 이후에 잘못 들어간 M 줄도 회수한다
    tail_keep = []
    for ln in tail:
        m = LINE_RE.match(ln)
        if m:
            m_lines[m.group(1)] = ln
        else:
            tail_keep.append(ln)

    ids = sorted(m_lines)
    print(f"이관 대상 M 줄: {len(ids)}개 ({ids[0]} ~ {ids[-1]})")
    if other:
        print("layer-1 절의 비-M 줄(검토 필요):", other)
    if not apply:
        return 0

    # 아카이브: layer-1 절 끝(## layer-2 앞)에 삽입
    arc_nl = "\r\n" if "\r\n" in arc else "\n"
    arc_lines = arc.split(arc_nl)
    try:
        a2 = arc_lines.index("## layer-2")
    except ValueError:
        print("아카이브의 ## layer-2 절 머리를 찾지 못함")
        return 1
    # layer-2 머리 앞의 빈 줄을 보존하도록 그 앞에 삽입
    insert_at = a2
    while insert_at > 0 and not arc_lines[insert_at - 1].strip():
        insert_at -= 1
    new_arc = arc_lines[:insert_at] + [m_lines[i] for i in ids] + [""] + arc_lines[a2:]
    io.open(ARC, "w", encoding="utf-8", newline="").write(arc_nl.join(new_arc))

    new_idx = head + ["", "(없음)", ""] + tail_keep
    io.open(IDX, "w", encoding="utf-8", newline="").write(nl.join(new_idx))
    print("적용 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv[1:]))
