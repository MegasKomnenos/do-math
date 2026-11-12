# -*- coding: utf-8 -*-
"""사전 최종 정리 회수: 세션 결정 54–56을 적고 작업 장부에 회수·재개 항목을 더한다."""
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


D = (
    "54. **본문과 사전의 두 전역 글자(2026-11-13 새벽; 최종 정리 10.5의 1·2).** 본문이 $T^{\\mathrm G}(x)$(2·4·5A·5B·7B, 62곳)와 $\\mathfrak K^{\\mathrm U}_N$(8장·7A 부록 D, 17곳)으로 적은 두 양은 사전이 $\\mathrm{Gr}(x)$·$\\mathrm{km}_N$으로 정한 것이다($T(x)$·9.3 $\\mathfrak K_N$과의 바탕 글자 중복 회피). 사전이 이기며 세션이 본문을 일괄 치환했다(`scripts/_sweep_Gr_km.py`).\n"
    "55. **Bor 가족의 장식 변형(2026-11-13 새벽; 10.5의 4).** 4장이 둔 $\\mathrm{Bor}^{\\mathrm{sum}}_k$, $\\mathrm{Bor}^{\\mathrm{ld}}$, $\\mathrm{Bor}(j;\\mathfrak Z)$는 1.2의 $\\mathrm{Bor}$ 가족($\\mathrm{Bor}(m)$, $\\mathrm{Bor}^{\\mathrm{tail}}_k$, $\\mathrm{Bor}_>$, $\\mathrm{Bor}^{*j}$)과 같은 꼴이다. Borel 분포에서 파생한 양들의 로마체 이름 가족으로 보고 위첨자·인수로 가르는 것을 허용한다(기존 가족과 같은 전례). 1.3 4.3 묶음의 국소 글자 $\\mathcal G_{z,i,n}$·$\\mathfrak J$는 전역으로 올리지 않는다(결정 53 범위).\n"
    "56. **집필자 글자와 그 장의 전역의 겹침(2026-11-13 새벽; 10.5의 5·6).** 최종 정리가 1.3에 「세션 판정 요」로 등록한 40곳(집필자가 고른 국소 글자가 그 장에서 쓰이는 1.2 전역 또는 예약 글자와 (바탕 글자, 글자체)가 같음)은 R1′ 위반이므로 본문 쪽을 바꾼다. 5A·5B·6·7A·7B·9·10장 집필자에게 장별 목록을 보내 고치게 하고, 7B가 남긴 같은 장 안 겹침(4장 $\\mathfrak U$·$\\mathfrak W$·$\\mathfrak N$ 대 7A X-cert $\\mathfrak U_i$·S∞ $\\mathfrak W(\\varkappa)$·P′ $\\mathfrak N$; 7B $\\Omega$ 대 4장 $\\omega$·7A $\\Omega^{\\mathrm{pr}}$)은 7A·7B 쪽을 바꾼다(4장 글자는 결정 53으로 고정). 그 뒤 설계 에이전트가 1.3의 해당 묶음을 집필자 최종 글자로 갱신한다(마지막 짧은 재개).\n"
)


def patch_decisions(s):
    if "54. **본문과 사전의 두 전역 글자" in s:
        return s
    assert "53. **다른 장이 인용하는 진술의 국소 글자" in s
    return s.rstrip("\n") + "\n" + D


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


ENTRY = (
    "- 2026-11-13 02:4x **사전 최종 정리 회수**(설계 에이전트, 83분): `장부_v2.md` 재생성 — 0절 R1′에 결정 47·53 조항; 1.2 12고침·2삭제(309행; 정의 절 $\\mathcal P^{(k)}_m$ 7.4·$C_k$ 7.2·$\\xi$ 8.1, 쓰이는 장 추가, $m^\\ast$·첨자 없는 $m^{\\mathrm{hit}}$ 삭제); 1.3 52고침·6추가(70묶음; 열두 조각 최종 글자 합침, 4.3 두 보조정리 글자 묶음, 「세션 판정 요」 40곳 표지); 3절 35추가·2가름·1삭제·7고침(185행; 덮인 패치 둘 복구, 소인·극 7.2, 뿌리 자리 법칙 7.4, 꼬리 띠, h-변환 5.5, 피벗·넘침·명시적 띠 삭제, 조각별 낱말 33); 5절 재생성; 4·6·7·8절 불변. 검산 여덟 통과(1.2 중복 예외 2뿐; 1.3 R1′ 0/1223 — 「세션 판정 요」 40 제외; 7절 68/68·204행; (ㄱ) 351). 처리표 「10. 최종 정리」. "
    "세션 결정 54($T^{\\mathrm G}\\to\\mathrm{Gr}$ 62곳·$\\mathfrak K^{\\mathrm U}\\to\\mathrm{km}$ 17곳 일괄 치환 완료), 55(Bor 가족 장식 변형 허용), 56(겹침 40곳은 본문 쪽을 바꿈 — 5A·5B·6·7A·7B·9·10장 집필자 일곱에 장별 목록으로 재개; 7A는 X-cert $\\mathfrak U_i$·S∞ $\\mathfrak W$·P′ $\\mathfrak N$도, 7B는 $\\Omega\\to\\omega$와 7A 추종). 그 뒤 설계 에이전트 마지막 짧은 재개(1.3 갱신) → 4절 재생성 → `_patch_9장_2차대조.py` 검산 → 명세 재빌드 → 조립."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "**사전 최종 정리 회수**" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("(열세 조각 전부 완료; 사전 최종 정리와 5B 수정판 코드 재계산 진행 중)", "(사전 최종 정리 완료; 결정 56 글자 정리를 일곱 장에 재개 — 그 뒤 1.3 갱신·4절·명세·조립)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)
