# -*- coding: utf-8 -*-
"""{{5:SR-implies-QR}}의 절 배정 수정: 구조표 4.2 행의 라벨 언급을 말로 바꾸고 META 5.2 순서에 넣는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_struct(s):
    return s.replace("함의 $\\mathsf S_R\\Rightarrow\\mathsf Q_R$는 5.2 `{{5:SR-implies-QR}}`로 옮김)", "함의 $\\mathsf S_R\\Rightarrow\\mathsf Q_R$는 5.2의 새 따름정리로 옮김)")


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


def patch_meta(s):
    old = '"5.2": ["{{5:tail-poly}}", "{{5:rational-cert}}", "{{5:sharp-546}}", "{{5:old-5-3}}",'
    assert s.count(old) == 1
    # 순서 목록 안에서 source-rep 뒤에 삽입
    i = s.index(old)
    j = s.index("]", i)
    seg = s[i:j]
    if "{{5:SR-implies-QR}}" not in seg:
        seg2 = seg.replace('"{{5:source-rep}}",', '"{{5:source-rep}}", "{{5:SR-implies-QR}}",', 1)
        assert seg2 != seg, "source-rep not in 5.2 order"
        s = s[:i] + seg2 + s[j:]
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_META.py"), patch_meta)
