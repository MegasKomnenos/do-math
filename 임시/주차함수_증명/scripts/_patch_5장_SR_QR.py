# -*- coding: utf-8 -*-
"""4장 회수의 구조 변경: 5.2에 따름정리 {{5:SR-implies-QR}}(S_R⇒Q_R; [r708d99c] §3 따름 B2)을 명세·구조표에 더한다."""
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
    anchor = '    "{{5:cayley-ratio}}": dict('
    assert s.count(anchor) == 1
    new = r'''    "{{5:SR-implies-QR}}": dict(kind="따름정리", name="경계 응답 부등식에서 조건부 로그오목성으로($\\mathsf S_R\\Rightarrow\\mathsf Q_R$)", record_name="기록 [r708d99c]의 명제 B1·따름 B2",
        process="전개", cls="고비", sources=[S("r708d99c", "3", note="네 용량 환원: 명제 B1과 따름 B2(133행)와 증명")],
        inputs=["{{5:source-rep}}", "{{5:green-connection}}", "{{4:old-4-3}}", "{{2:old-2-28}}"],
        special="첫 판 4.2의 함의($B_-=B_{n,k-1}$, $B_+=\\mathcal K_{n,k}(k+2)-A_{n,k+1}$, 한 칸 차분의 분해)는 5.2의 Green 연결·양의 원천 표현이 입력이므로 4장이 아니라 여기서 증명한다. 정리 5.4·5.5의 「따라서 $\\mathsf Q$」 단계가 이 따름정리를 인용한다. 원천별 비교 항 $(\\mathrm G)_d$와 낱말 「원천별 비교 항」도 여기서 정의한다."),
'''
    if "{{5:SR-implies-QR}}" not in s:
        s = s.replace(anchor, new + anchor)
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_수정.py"), patch_fix)


def patch_struct(s):
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| 5.2 ") and "{{5:SR-implies-QR}}" not in ln:
            tok = "`{{5:source-rep}}`"
            if tok in ln:
                ln = ln.replace(tok, tok + ", `{{5:SR-implies-QR}}` 따름정리 $\\mathsf S_R\\Rightarrow\\mathsf Q_R$ [r708d99c] §3 133행(명제 B1·따름 B2; 첫 판 4.2의 함의는 5.2의 Green 연결이 입력이라 4장에서 옮김; $(\\mathrm G)_d$와 「원천별 비교 항」도 여기서 정의)", 1)
            else:
                cells = ln.split(" | ")
                cells[1] = cells[1] + "; `{{5:SR-implies-QR}}` 따름정리 $\\mathsf S_R\\Rightarrow\\mathsf Q_R$ [r708d99c] §3 133행(첫 판 4.2의 함의를 옮김; $(\\mathrm G)_d$도 여기서 정의)"
                ln = " | ".join(cells)
            lines[i] = ln
        if ln.startswith("| 4.2 ") and "함의는 5.2" not in ln:
            cells = ln.split(" | ")
            cells[1] = cells[1] + " (4.2는 $\\Gamma_d$, $\\Gamma^\\pm$, $\\mathcal S_{n,k}$, $\\mathsf S_R$의 정의만 두고 함의 $\\mathsf S_R\\Rightarrow\\mathsf Q_R$는 5.2 `{{5:SR-implies-QR}}`로 옮김)"
            lines[i] = " | ".join(cells)
    return "\n".join(lines)


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)
