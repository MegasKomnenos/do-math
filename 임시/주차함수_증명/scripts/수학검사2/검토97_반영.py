# -*- coding: utf-8 -*-
"""결정 97 점검 P(수학·본문)·Q(참조·정합)의 지적 반영. 새 문장이 있으면 건너뜀(멱등)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EDITS = [
    # ---- 장10 (P-1, P-2, 확인 요 둘, Q 문법) ----
    ("장v2/장10.md", "장부의 첫 합을 Abel 합으로 재배열하면 한 걸음 양이 꼬리합 $\\mathfrak T_m$들의 양의 무게 합으로 적힌다.",
     "장부의 첫 합을 Abel 합으로 재배열하면 그 합이 꼬리합 $\\mathfrak T_m$들의 무게 합으로 적힌다. 무게는 $w_k$와 분할 무게의 증분 $w_m-w_{m-1}$이고, 보조정리 {{10:old-8-3}}(c)로 음이 아니다."),
    ("장v2/장10.md", "정수 $k\\ge2$, $n'\\le2k$와 수준 $\\ell\\ge1$에서 정확히", "정수 $k\\ge2$, $1\\le n'\\le2k+1$($n'=2k+1$이면 두 합은 빈 합)과 수준 $\\ell\\ge1$에서 정확히"),
    ("장v2/장10.md", "정수 $k\\ge2$, $2k+1\\le n\\le3k$에서 $w_{k-1}:=0$으로 두면 정확히", "정수 $k\\ge2$, $2k+1\\le n\\le3k$에서 정확히"),
    ("장v2/장10.md", "[증명됨, 정리 {{8:old-6-33}}·보조정리 {{10:old-8-3}}·명제 {{10:old-8-6}}에 의존; r3d0856b]", "[증명됨, 정리 {{8:old-6-33}}·보조정리 {{10:old-8-2}}·{{10:old-8-3}}·명제 {{10:old-8-6}}에 의존; r3d0856b]"),
    ("장v2/장10.md", "증명은 장부(보조정리 {{10:old-8-2}}), 분할 무게의 단조성(", "증명은 장부(보조정리 {{10:old-8-2}})와 그 꼬리합 꼴(명제 {{10:old-8-6}}), 분할 무게의 단조성("),
    # ---- 대응표 (P M-1, Q 1) ----
    ("장v2/부록C.md", "$\\mathfrak T_m$, $\\mathfrak L_\\nu$, $w_m$,", "$\\mathfrak T_m$, $w_m$,"),
    ("장v2/부록C.md", "$T_m$, $\\Lambda_\\nu$, $w_m$,", "$T_m$, $w_m$,"),
    ("장부_v2.md", "$\\mathfrak T_m$, $\\mathfrak L_\\nu$, $w_m$,", "$\\mathfrak T_m$, $w_m$,"),
    ("장부_v2.md", "$T_m$, $\\Lambda_\\nu$, $w_m$,", "$T_m$, $w_m$,"),
    # ---- 장부 1.3 (P M-2, Q 2) ----
    ("장부_v2.md", "$\\mathsf s_{\\mathrm{St}}$(줄기 하계 상수); ", ""),
    ("장부_v2.md", "$\\epsilon^{\\mathrm d}_m=c_m(k)-c_{m-1}(k-1)$(기록 [r3d0856b] L90 $\\delta_m$; 대각선 차 — 1.2 $\\delta_t$와 겹쳐 (ㄱ)); ", ""),
    ("장부_v2.md", "$\\mathfrak f^X_m,\\mathfrak f^Y_m$(1.2 장부 항 $\\mathfrak f_m$의 변형; 손실항); ", ""),
    ("장부_v2.md", "| 10.1 `{{10:old-8-2}}`–`{{10:old-8-7}}` 증명 |", "| 10.1 `{{10:old-8-2}}`·`{{10:old-8-3}}`·`{{10:old-8-4}}`·`{{10:old-8-6}}` 증명 |"),
    ("장부_v2.md", "기록 글자 유지($\\mathcal L_m$은 $\\mathfrak L_\\nu$와 글자체가 다름), ", "기록 글자 유지, "),
    # ---- 체류 꼴 → 머묾 꼴 (Q 범위 밖) ----
    ("장부_v2.md", "V-핵심 체류 꼴의 경계항", "V-핵심 머묾 꼴의 경계항"),
    ("장부_v2.md", "| 체류 꼴(명제 S)의 중앙 경계항(경계항 가족) |", "| 머묾 꼴(명제 S)의 중앙 경계항(경계항 가족) |"),
    ("장v2/부록A.md", "V-핵심 체류 꼴의 경계항", "V-핵심 머묾 꼴의 경계항"),
    ("장v2/부록A.md", "| 체류 꼴(명제 S)의 중앙 경계항(경계항 가족) |", "| 머묾 꼴(명제 S)의 중앙 경계항(경계항 가족) |"),
    ("구조표_v2.md", "| 10.2 체류 꼴 | 8.8 |", "| 10.2 머묾 꼴 | 8.8 |"),
    # ---- 결정 97 본문·장부 항목 (Q 3) ----
    ("대조v2/장부_설계_세션결정.md", "덤으로 프락투어 $\\mathfrak L$의 두 뜻(10장 $\\mathfrak L_\\nu$, 8장 띠 정리의 $\\mathfrak L_k$)이 하나로 준다. 적용 `scripts/수학검사2/결정97_문턱예산_정리.py`.",
     "덤으로 전역 글자 프락투어 $\\mathfrak L$은 8장 띠 정리의 $\\mathfrak L_k$ 하나만 남는다(장별 국소 $\\mathcal L$은 별개). 적용 `scripts/수학검사2/결정97_문턱예산_정리.py`; 후속(19:4x) 부록 A 기호 표의 $\\mathfrak L_\\nu$·$\\mathrm{Bd}^\\Lambda_\\nu$ 행 삭제와 장부 409행. "
     "점검 P·Q(20:0x) 반영(`검토97_반영.py`): 10.1 연결문의 정밀화(재배열되는 것은 장부의 첫 합, 무게의 비음성은 보조정리 10.3(c)), 보조정리 10.4의 범위 $1\\le n'\\le2k+1$(명제 10.7 증명의 $\\nu=k-1$·$m_0=2k$ 경계), 명제 10.6의 군더더기 $w_{k-1}:=0$ 삭제, 정리 10.9 머리에 보조정리 10.2·끝 문장에 명제 10.6, 「10.4로」 조사, 부록 C·장부 7절 대응표의 $\\mathfrak L_\\nu\\leftrightarrow\\Lambda_\\nu$ 삭제, 장부 1.3의 $\\mathsf s_{\\mathrm{St}}$·$\\epsilon^{\\mathrm d}_m$·$\\mathfrak f^X_m,\\mathfrak f^Y_m$·범위 표기·$\\mathcal L_m$ 구별 괄호, 장부 1절·부록 A·구조표의 「체류 꼴」→「머묾 꼴」."),
    ("작업_장부.md", "조립 2,361,936바이트·11,501행, 라벨 419(−2), **불변식 통과**", "조립 2,361,738바이트·11,499행(부록 A 기호 표의 $\\mathfrak L_\\nu$·$\\mathrm{Bd}^\\Lambda_\\nu$ 행 삭제·장부 409행 후속 뒤), 라벨 419(−2), **불변식 통과**"),
]

n = 0
for rel, old, new in EDITS:
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    if new and new in s and old not in s:
        continue
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new); io.open(p, "w", encoding="utf-8", newline="\n").write(s); n += 1
    elif c == 0 and new == "":
        continue   # 이미 지움
    else:
        print("앵커 수", c, rel, old[:60])
# 조사: 보조정리 10.4으로 → 10.4로 (둘)
p = os.path.join(ROOT, "장v2/장10.md"); s = io.open(p, encoding="utf-8").read()
c = s.count("보조정리 {{10:old-8-4}}으로")
if c:
    s = s.replace("보조정리 {{10:old-8-4}}으로", "보조정리 {{10:old-8-4}}로"); io.open(p, "w", encoding="utf-8", newline="\n").write(s); n += c
print("치환", n)
