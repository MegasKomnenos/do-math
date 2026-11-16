# -*- coding: utf-8 -*-
"""일관성 검토 반영 뒤 집필자 반환이 적은 새 글자·낱말을 사전 1.3·3절에 등록한다(세션 결정 67·70; 장4·7B·9·6·2장 기록). 멱등."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장부_v2.md")
DRY = "--dry" in sys.argv

s = io.open(P, encoding="utf-8").read()
orig = s
log = []


def rep(old, new, what, count=1):
    global s
    n = s.count(old)
    if n == 0:
        if new in s:
            log.append((what, "이미 반영"))
        else:
            raise SystemExit(f"{what}: 원문을 찾지 못함: {old[:80]}")
        return
    if n != count:
        raise SystemExit(f"{what}: {n}곳 발견(기대 {count})")
    s = s.replace(old, new)
    log.append((what, "고침"))


# 4.3 묶음(two-corrections): W_j → Wi_j, 국소 L 삭제, 새 보조정리의 글자
rep("$W_j$; $L=\\mathfrak G\\sqrt k$(수직선 반길이), $\\mathfrak G$(호 매개변수), $z$(수직선 변수);",
    "$\\mathrm{Wi}_j$($j=0,1,2$; 두 보정의 수직선 적분 $\\int_0^1e^{kv^2/2}v^2\\mathrm{Bor}^{\\mathrm{tail}}_k(1-v)(v^2/2)^jdv$ — 세션 결정 67; 1차 $W_j$; 5.6이 씀); $\\mathfrak G$(호 매개변수), $z$(수직선 변수; 수직선 반길이 $\\mathfrak G\\sqrt k$는 글자 없이 — 결정 67);",
    "4.3 Wi_j·L")
rep("$G_k(z)$(윤곽 핵),",
    "$\\mathrm{Mag}_k(z)$, $\\mathrm{Ph}_k(z)$, $\\mathrm{Pq}(z,\\rho)$, $\\mathrm{Bn}_k$, $\\mathrm{Mag}^{\\mathrm J}_k(z)$, $\\mathrm{Am}_\\rho(z)$, $\\mathrm{Ph}^{\\mathrm J}_\\rho(z)$(보조정리 `{{4:correction-contour}}`의 진술 글자 — 세션 결정 64·70; 옛 증명 국소 $G_k$, $\\psi_k$, $\\Pi_0$, $\\mathsf m_k$, $\\mathfrak w$, $\\mathfrak o_\\rho$, $\\Psi$를 대신함; 7.4가 가리킨다),",
    "4.3 correction-contour 글자")

# 6.6 묶음: v_r 삭제(6장이 풀어 적음)
rep("$\\mathfrak v_r$(꼬리 차분 비), ", "", "6.6 v_r 삭제")

# 9.1 묶음: p_m(chi) 추가
rep("$\\mathfrak x_m(\\chi)$(경로 가중치; 기록 $T_m$), ",
    "$\\mathfrak x_m(\\chi)$(경로 가중치; 기록 $T_m$), $\\mathfrak p_m(\\chi)$(경로 $\\chi$의 확률 $[\\prod_i\\mathrm{Bor}(S_{i-1}-S_i)]\\mathrm{Bor}(S_L)/\\mathrm{Bor}(m+1)\\cdot\\pi^0_{S_L-1}(w)$; 정리 2.14의 식에서 유도 — 세션 결정 64(ㄴ)), ",
    "9.1 p_m(chi)")

# 7장 부록 D 국소 글자: 새 D 항목(7B)
rep("$c_0$·$h_A$는 코드 변수 표기) | 7장 부록 D(7A의 D1·D3·D4·D5)의 국소 글자",
    "$c_0$·$h_A$는 코드 변수 표기; D.column-certificates-841-2000(7B; 세션 결정 72): $\\mathfrak S(u)$(절단 소인 질량 합), $\\tilde v_i$(격자값), $\\mathrm{Lip}$, $\\mathfrak e$(오차 예산; 7A P′의 글자), $\\mathrm{REL}$, $\\mathfrak N$·$\\mathfrak J$·$\\mathfrak N_{\\mathrm f}$(7A 부록 D와 같은 글자), $\\rho_{\\mathrm U}$, $\\Gamma(n)$(인증서 상수를 $n$의 함수로 본 것)) | 7장 부록 D(7A의 D1·D3·D4·D5와 7B의 열별 인증서 항목)의 국소 글자",
    "7장 부록 D 새 글자")

# 3절: Robbins 나머지 낱말
if "| Robbins 나머지 |" not in s:
    lines = s.split("\n")
    i0 = next(i for i, l in enumerate(lines) if l.startswith("## 3. 낱말 사전"))
    i1 = next(i for i, l in enumerate(lines) if i > i0 and l.startswith("## 4. "))
    last2 = None
    for i in range(i0, i1):
        l = lines[i]
        if l.startswith("| ") and not l.startswith("| 낱말 |") and not l.startswith("|---"):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[2].startswith("2."):
                last2 = i
    if last2 is None:
        raise SystemExit("3절에 2.x 행을 찾지 못함")
    lines.insert(last2 + 1, "| Robbins 나머지 | $\\mathrm{rb}_m=\\log m!-(m+\\tfrac12)\\log m+m-\\tfrac12\\log(2\\pi)$(Robbins 부등식 $m!=\\sqrt{2\\pi m}(m/e)^me^{\\mathrm{rb}_m}$의 지수; $\\frac1{12m+1}<\\mathrm{rb}_m<\\frac1{12m}$) | 2.9 | Robbins 오차, $\\epsilon_m$·$\\varepsilon_m$ |")
    s = "\n".join(lines)
    log.append(("3절 Robbins 나머지", "추가"))
else:
    log.append(("3절 Robbins 나머지", "이미 반영"))

for w, r in log:
    print(f"[{w}] {r}")
if DRY:
    print("(dry)")
elif s != orig:
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("patched 장부_v2.md")
else:
    print("unchanged")
