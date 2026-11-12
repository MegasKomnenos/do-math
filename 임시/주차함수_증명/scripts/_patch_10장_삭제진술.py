# -*- coding: utf-8 -*-
"""10장 2차 대조 뒤 삭제된 첫 판 진술 8.7·8.27·8.29를 라벨 등록부 생성기(DELETED)와 구조표 10.1·10.5에 반영한다."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_gen(s):
    m = re.search(r"^DELETED\s*=\s*\{([^}]*)\}", s, re.M)
    assert m, "DELETED not found"
    body = m.group(1)
    add = [x for x in ('"8.7"', '"8.27"', '"8.29"') if x not in body]
    if add:
        new_body = body.rstrip().rstrip(",") + ", " + ", ".join(add)
        s = s[: m.start(1)] + new_body + s[m.end(1):]
    return s


rw(os.path.join(ROOT, "scripts", "_gen_라벨_v2.py"), patch_gen)


def patch_struct(s):
    a = "| 10.1 둘째 층의 $1/p$ 장부 | 8.1–8.7 | 첫 판 8.1 | 옮김 |"
    if s.count(a) == 1:
        s = s.replace(a, "| 10.1 둘째 층의 $1/p$ 장부 | 8.1–8.6(8.7 피벗은 어느 증명도 쓰지 않아 뺌; 10장 2차 대조) | 첫 판 8.1 | 옮김 |")
    b = "| 10.5 얼린 볼록 몫, 젊은 사슬, 상해 원리 | 8.16–8.29; 8.23의 30자리 수치 적분은 부록 D | 첫 판 8.5 | 옮김 |"
    if s.count(b) == 1:
        s = s.replace(b, "| 10.5 얼린 볼록 몫, 젊은 사슬, 상해 원리 | 8.16–8.26, 8.28(8.27 머묾 질량의 사슬 표현·8.29 창 맨 앞의 하계는 어느 증명도 쓰지 않아 뺌; 10장 2차 대조); 8.23의 30자리 수치 적분은 부록 D | 첫 판 8.5 | 옮김 |")
    return s


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)
