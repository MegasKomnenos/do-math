# -*- coding: utf-8 -*-
"""반영 뒤 세션 몫: 결정 33–37을 장부 v2·결정록·세션결정·구조표·META·지침에 적용한다.

33 err→nf; 34 Riemann 제타 값은 산세리프 명명 상수 z; 35 평평한 핵심의 정의식; 36 ε_hz·γ_L은 에이전트 판정 수용;
37 결정록 4절 15·16·18은 (가). 구조표: 2.21(Borel 질량)을 2.5로, ρ_k 정의를 7.2로, 1.5에 결손 두 셈법.
"""
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


# ------------------------------------------------------------------ 장부 v2
def patch_ledger(s):
    # 33: err -> nf
    n = s.count("\\mathrm{err}")
    s = s.replace("\\mathrm{err}", "\\mathrm{nf}").replace("| err·로마체 이름 |", "| nf·로마체 이름 |")
    print("  err→nf:", n)
    # 35: 평평한 핵심
    old = "| 평평한 핵심 $1+kD_k$ |"
    assert s.count(old) == 1, s.count(old)
    s = s.replace(old, "| 평평한 핵심 $k\\sum_{t=k+1}^{2k+1}x_t(k)$ |")
    # 34: Riemann 제타 값 상수 행(1.2 산세리프 묶음, x_k 행 뒤)
    lines = s.split("\n")
    zrow = ("| $\\mathsf z_{1/2}, \\mathsf z_{-1/2}, \\mathsf z_{3/2}$ | z·산세리프 | Riemann 제타 함수의 $\\tfrac12$, $-\\tfrac12$, $\\tfrac32$에서의 값(명명 상수; 수치와 인증 구간은 부록 D) "
            "| 8.2 | 8 | 없음 | $\\zeta(\\frac12)$, $\\zeta(-\\frac12)$, $\\zeta(\\frac32)$ ([r030ffae], [rfc69320]) |")
    if "z·산세리프" not in s:
        idx = [i for i, ln in enumerate(lines) if "| x·산세리프 |" in ln]
        assert len(idx) == 1, idx
        lines.insert(idx[0] + 1, zrow)
    s = "\n".join(lines)
    # 7절 끝에 대응 행
    z7 = "| $\\mathsf z_{1/2}, \\mathsf z_{-1/2}, \\mathsf z_{3/2}$ | [r030ffae], [rfc69320] | $\\zeta(\\frac12)$, $\\zeta(-\\frac12)$, $\\zeta(\\frac32)$ | 없음(기록의 함수 기호를 명명 상수로; 중앙 창 좌표 $\\zeta$와의 충돌 회피) |"
    if "[r030ffae], [rfc69320] | $\\zeta(\\frac12)$" not in s:
        i7 = s.index("## 7. 기록 글자 대응")
        i8 = s.index("## 8. 감사 규칙")
        sec7 = s[i7:i8]
        rows = sec7.split("\n")
        last = max(i for i, ln in enumerate(rows) if ln.startswith("|"))
        rows.insert(last + 1, z7)
        s = s[:i7] + "\n".join(rows) + s[i8:]
    # 5절 8장 행: 정의 글자에 더하고 산세리프 여유에서 z 제거
    i5 = s.index("## 5. 장별 배정과 여유 글자")
    i6 = s.index("## 6. 예약 글자")
    sec5 = s[i5:i6]
    rows = sec5.split("\n")
    for i, ln in enumerate(rows):
        if ln.startswith("| 8 |"):
            cells = ln.split(" | ")
            if "\\mathsf z_{1/2}" not in cells[1]:
                cells[1] = cells[1] + "; $\\mathsf z_{1/2}, \\mathsf z_{-1/2}, \\mathsf z_{3/2}$"
            cells[3] = cells[3].replace("$\\mathsf z$, ", "")
            rows[i] = " | ".join(cells)
    s = s[:i5] + "\n".join(rows) + s[i6:]
    return s


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger)


# ------------------------------------------------------------------ 결정록 4절 14–18의 세션 답
def patch_log(s):
    answers = {
        "| 14 |": "(나) $\\mathrm{nf}(n,d)$(정규화 인자; 세션 결정 33)",
        "| 15 |": "(가) 유지(세션 결정 37)",
        "| 16 |": "(가) 유지(세션 결정 37)",
        "| 17 |": "산세리프 명명 상수 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$로 1.2에 둔다(세션 결정 34; 이탤릭 $\\zeta$의 장식 변형은 R1′ 위반, 수치만 적으면 식의 정확성이 흐려짐)",
        "| 18 |": "(가) 유지(세션 결정 37)",
    }
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        for key, ans in answers.items():
            if ln.startswith(key) and ln.rstrip().endswith("|  |"):
                lines[i] = ln.rstrip()[:-4] + "| " + ans + " |"
    s = "\n".join(lines)
    s = s.replace("\\mathrm{err}", "\\mathrm{nf}")
    return s


rw(os.path.join(ROOT, "대조v2", "장부_설계_결정록.md"), patch_log)


# ------------------------------------------------------------------ 세션결정 7절
def patch_decisions(s):
    add = r"""
## 7. 반영 처리표(`장부_기록대조_반영.md`) 뒤 세션의 결정(결정 33–37)

33. **사슬 전개 정규화 인자의 이름.** 기록 대조로 $\mathcal R(n,d)=e^d\frac{n!}{(n-d)!}\frac{(n-d)^{n-d-2}}{n^{n-2}}$가 가산 오차항이 아니라 $\ge1$인 곱 인자임이 드러났으므로 이름 $\mathrm{err}$를 버리고 $\mathrm{nf}(n,d)$(normalizing factor)로 한다. 장부·결정록의 모든 자리를 치환했다.
34. **Riemann 제타 값의 표기.** $\zeta(\tfrac12)$, $\zeta(-\tfrac12)$, $\zeta(\tfrac32)$는 1장 전역 $\zeta$(중앙 창 좌표)와 바탕 글자가 같고, 이탤릭 $\zeta$의 장식 변형은 R1′ 위반이며, 수치만 적으면 식의 정확성이 흐려진다. 산세리프 명명 상수 $\mathsf z_{1/2}$, $\mathsf z_{-1/2}$, $\mathsf z_{3/2}$로 1.2(정의 절 8.2)에 두고 7절에 대응 행을 두었다. 수치와 인증 구간은 부록 D.
35. **평평한 핵심의 정의식.** $\varphi^\flat_k$(6.4)의 뜻을 $k\sum_{t=k+1}^{2k+1}x_t(k)$로 적어 6.5의 $D_k$를 앞서 쓰는 위반을 없앤다($1+kD_k$와 같은 수).
36. **에이전트 판정의 수용.** $\epsilon_{\mathrm{hz}}$는 [r030ffae] review §2.6(c)의 정정판($\nu^{-1/2}$)을 따르고(결정 29의 「$\nu+1$」은 첫 대조의 오독), $\gamma_L(j)$는 [r5bbc534] L103에 있으므로 삭제 대신 출처 교체(결정 30의 예외), $\mathsf n_k$와 5.6의 $N_k$는 식이 같으므로 한 글자. 방문 확률 $\zeta_N(m)$과 열 합 $\mathcal C_N(Y)$는 글자 없이 풀어 적는다.
37. **결정록 4절 15·16·18.** 모두 (가). $W_n(\gamma)$의 상계 조건은 정의 진술에 있고 1.2 비고에 되살리지 않는다.

구조표 반영(세션): 1.5에 결손의 두 셈법($n+1-M_n$ 대 $m-M$)의 관계; 정의 2.21(Borel 질량)을 2.6에서 2.5로; 극 $\rho_k$의 정의를 7.3에서 7.2로. $\mathrm{DDL}_2$·$\mathrm{DDL}^\natural$·$\mathfrak H_d$는 10.5 정의로 가른 그대로(10.4 셀은 $\mathrm{DDL}_2$를 부르지 않는다).
"""
    if "## 7. 반영 처리표" not in s:
        s = s.rstrip("\n") + "\n" + add
    return s


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


# ------------------------------------------------------------------ 구조표
def patch_struct(s):
    a = "| 2.5 가장 큰 나무와 최대 나무 사슬 | 2.12–2.20 | 첫 판 2.5 | 옮김(2.20의 상계값 계산은 부록 D) |"
    b = "| 2.5 가장 큰 나무와 최대 나무 사슬 | 2.12–2.20, 2.21(Borel 질량; 2.6에서 앞당김 — 2.5의 가장 큰 나무 핵 $\\pi_n(m)$이 쓴다) | 첫 판 2.5, 2.6 | 옮김(2.20의 상계값 계산은 부록 D) |"
    assert s.count(a) == 1
    s = s.replace(a, b)
    a2 = "| 2.6 Borel 분포, 임계 볼츠만 법칙, 생존 확률 | 2.21–2.26 | 첫 판 2.6 | 옮김 |"
    assert s.count(a2) == 1
    s = s.replace(a2, "| 2.6 Borel 분포, 임계 볼츠만 법칙, 생존 확률 | 2.22–2.26(2.21은 2.5로) | 첫 판 2.6 | 옮김 |")
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| 7.2 왼쪽 잔여 증가와 문턱 |") and "극 $\\rho_k$의 정의" not in ln:
            cells = ln.split(" | ")
            cells[1] = cells[1] + "; 극 $\\rho_k$의 정의($C_k(\\rho_k)=1$인 양의 근; 첫 판 6.3·1867 문단)를 7.3에서 앞당겨 7.2에 둔다(7.2의 $\\mathfrak P_k(\\infty)$가 쓴다; 세션 결정 28)"
            lines[i] = " | ".join(cells)
        if ln.startswith("| 1.5 읽는 법: 지위, 표기, 좌표 |") and "결손의 두 셈법" not in ln:
            cells = ln.split(" | ")
            cells[1] = cells[1] + " 결손의 두 셈법(3장의 $n+1-M_n$과 5·6·8·10장의 $m-M$)의 관계를 한 문장으로 적는다."
            lines[i] = " | ".join(cells)
    return "\n".join(lines)


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


# ------------------------------------------------------------------ META 추가 지시
def patch_meta(s):
    block = r'''
# 2026-11-12 저녁: 기록 대조 반영 뒤의 장별 지시(세션 결정 28·33–35)
EXTRA_NOTES.setdefault(1, []).append("1.5에서 변수 글자 $k$, $r=n-\\ell-1=n-k$, $N=n-k$, $\\nu=n-2k$, $d$, $q$를 정의한다(장부 1.1). 결손의 두 셈법(3장의 $n+1-M_n$, 뒤 장들의 $m-M$)의 관계를 한 문장으로 적는다.")
EXTRA_NOTES.setdefault(2, []).append("첫 판 정의 2.21(Borel 질량 $\\mathrm{Bor}(m)$)은 2.6이 아니라 2.5에 둔다(2.5의 가장 큰 나무 핵 $\\pi_n(m)$이 쓴다). 사슬 전개의 정규화 인자는 $\\mathrm{nf}(n,d)$다(가산 오차항이 아니라 $\\ge1$인 곱 인자).")
EXTRA_NOTES.setdefault(6, []).append("평평한 핵심 $\\varphi^\\flat_k$의 정의는 $k\\sum_{t=k+1}^{2k+1}x_t(k)$다(6.5의 $D_k$를 6.4에서 미리 쓰지 않는다).")
EXTRA_NOTES.setdefault(7, []).append("극 $\\rho_k$($C_k(\\rho_k)=1$인 양의 근)의 정의를 7.3이 아니라 7.2에 둔다(7.2의 $\\mathfrak P_k(\\infty)$가 쓴다).")
EXTRA_NOTES.setdefault(8, []).append("Riemann 제타 함수의 값은 장부의 산세리프 명명 상수 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$로 적는다(8.2에서 한 번 정의; 이탤릭 $\\zeta$는 중앙 창 좌표다). 수치와 인증 구간은 부록 D.")
EXTRA_NOTES.setdefault(10, []).append("$\\mathrm{DDL}(k)$는 10.4에서, $\\mathrm{DDL}_2$·$\\mathrm{DDL}^\\natural$·$\\mathfrak H_d$는 10.5에서 정의한다. 10.4의 진술은 $\\mathrm{DDL}_2$를 부르지 않는다.")

'''
    anchor = "def apply(ch):"
    if "기록 대조 반영 뒤의 장별 지시" not in s:
        s = s.replace(anchor, block + anchor)
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_META.py"), patch_meta)


# ------------------------------------------------------------------ 지침 v2 3절: (ㄱ) 목록
def patch_guide(s):
    anchor = "고른 국소 기호는 대조 파일 「장부에 없는 기호와 여유 글자의 사용」에 뜻과 함께 적는다."
    assert s.count(anchor) == 1
    add = (" 장부 1.3의 묶음마다 「바꿔야 할 기록 글자」 목록이 있다. 그 글자는 기록 그대로 쓰면 그 장의 전역 기호나 변수와 겹치므로 반드시 여유 글자에서 다시 고르고, 묶음의 넷째 열(기록·첫 판 글자)에 적힌 글자는 전역 글자가 있으면 그것으로 옮겨 쓴다."
           " 1.2의 「뜻」은 안내이고 정본은 정의 진술이다. 양의 정의는 사전의 식이 아니라 기록 원문에서 옮긴다.")
    if "바꿔야 할 기록 글자」 목록이 있다" not in s:
        s = s.replace(anchor, anchor + add)
    return s


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)
