# -*- coding: utf-8 -*-
"""6장 회수의 구조 변경: 5.1에 명제 {{5:witness-position-bound}}(작은 행의 증인 위치 경계; 계산 증거)를 명세·구조표에 더한다."""
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


def patch_fix(s):
    anchor = '    "{{5:SR-implies-QR}}": dict('
    assert s.count(anchor) == 1
    new = r'''    "{{5:witness-position-bound}}": dict(kind="명제", name="작은 행의 증인 위치 경계", record_name="정리 5.1의 인증 자료([r19de912]; 인용 [r7e03176] §8)",
        process="부록 D", cls="기계적", sources=[S("r7e03176", "8.3", note="증인 위치 경계의 인용 자리"), S("r19de912", "1", note="n≤20000 정확 정수 인증의 자료(행별 증인 위치)")],
        inputs=["{{5:old-5-1}}"],
        special="진술: $50\\le m\\le20000$에서 $m+1-\\ell^\\ast_m\\le1.99+0.59963(m+1)^{2/3}+1.24847(m+1)^{1/3}$. 지위 「계산 증거」; 값은 부록 D `{{D:exact-n20000}}`의 행별 증인 위치에서 확인된다(그 항목에 한 줄 더한다). 6장의 `{{6:small-k-bulk}}`·`{{6:old-8-11}}`·`{{6:old-8-12}}`가 입력으로 쓴다."),
'''
    if "{{5:witness-position-bound}}" not in s:
        s = s.replace(anchor, new + anchor)
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_수정.py"), patch_fix)


def patch_struct(s):
    a = "| 5.1 유한 인증 | 5.1, 5.2 | 첫 판 5.1 | 옮김(명세는 부록 D) |"
    assert s.count(a) == 1
    return s.replace(a, "| 5.1 유한 인증 | 5.1, `{{5:witness-position-bound}}` 작은 행의 증인 위치 경계(명제; 계산 증거; 정리 5.1 인증 자료 [r19de912]의 행별 증인 위치, 인용 [r7e03176] §8; 6장의 small-k-bulk·old-8-11·old-8-12가 쓴다), 5.2 | 첫 판 5.1 | 옮김(명세는 부록 D) |")


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


def patch_meta(s):
    old = '"5.1": ["{{5:old-5-1}}", "{{5:old-5-2}}"]'
    if old in s and "{{5:witness-position-bound}}" not in s:
        s = s.replace(old, '"5.1": ["{{5:old-5-1}}", "{{5:witness-position-bound}}", "{{5:old-5-2}}"]')
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_META.py"), patch_meta)
