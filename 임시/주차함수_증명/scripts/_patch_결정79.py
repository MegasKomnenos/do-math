# -*- coding: utf-8 -*-
"""세션 결정 79(외부 교정 셋째 묶음)와 장부 항목. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md")
LED = os.path.join(ROOT, "작업_장부.md")

D79 = r"""79. **외부 교정 셋째 묶음(오식·기호 미통일 열 항목)은 모두 타당했고 세션이 직접 고쳤다(2026-11-13 05:2x).** 원문 대조와 처리는 `대조v2/외부피드백_교정3.md`. 본문: 3.3 증명 첨자 $T^{(n)}_h\to T^{(n)}_I$; $kW_j\to k\mathrm{Wi}_j$ 14곳(4.3·5.6); Gauss 계수 보조정리 증명 끝 ∎; 5.2의 기록 글자 $D_d\to\mathrm{sd}_d$, 1차 글자 $V_i\to\mathrm{fs}_i$, $\tilde{\mathrm{fs}}\to\mathrm{fs}'$(정의는 고정 크기 응답 (다) 증명 한 곳), 인수 있는 $\mathrm{fs}_{r-1}(\cdot)$는 타일 합 $\mathcal V$로 통일; 5.5.7·5.5.9의 $H(\rho_0,Q_{\mathrm w})\to\mathrm{hov}$ 3곳; 7.2의 $\mathbb E_G\to\mathbb E_\Psi$, 기댓값 안의 절단 정수 $\mathcal J^{\mathrm S}_k$는 모멘트 판정 통계 $\mathcal T_k$로 2곳; 7.4 머리의 잘린 식별자 [r8d6850a]; 7.7의 $k\mathrm w_{2k}\to kw_{2k}$. 부록 C: 생성기 `부록_v2.py`의 원천인 장부 3절(첫 판 절·행 위치 표지와 첫 판 절 번호 26행)·4절(경화 번호 → 라벨)·7절(운영 낱말)을 고치고, 생성기에 `preclean`(위치 표지·Qnn·「(확인)」 제거)과 결과 대응표 중복 행 제거를 넣었다. 규칙: 부록 A·C에 닿는 장부 칸에는 첫 판 위치·설계 질문 번호·대조 표지·운영 낱말을 두지 않는다(두더라도 생성기가 걷어 낸다); 기록 안 행 참조 「L36」 꼴은 남긴다.
"""

ENTRY = (
    "- 2026-11-13 05:2x **외부 교정 셋째 묶음 반영**(사용자 전달; 오식·기호 미통일 열 항목): 지적이 닿는 절을 조각 원문에서 통째로 읽어 전부 타당함을 확인하고 세션이 직접 고쳤다(`_fix_외부교정3.py` 본문 6조각, `_patch_장부_외부교정3.py` 장부 3·4·7절, `_patch_부록생성기_정리{,2,3}.py`). 본문 치환 ~50곳(결정 79), 부록 C는 장부 원천과 생성기를 고쳐 재생성(첫 판 위치 표지·절 번호 26행, 중복 행 4쌍, 경화 번호 1, Qnn 9·「(확인)」 65·운영 낱말 5). 재조립 뒤 라벨 432·D 47·[todo] 0·불변식 통과·균형 0·지위 서식 0·예약 글자 δ_t만. KaTeX 전수 검사와 PDF 재렌더(`_md2pdf_0530.log`)는 배경 실행. 대조는 `대조v2/외부피드백_교정3.md`. 이전 PDF(05:11, 293쪽)는 이 수정 전 판."
)


def main():
    s = io.open(DEC, encoding="utf-8").read()
    if "79. **외부 교정 셋째 묶음" not in s:
        s = s.rstrip("\n") + "\n" + D79
        io.open(DEC, "w", encoding="utf-8", newline="\n").write(s)
        print("결정 79 추가")
    t = io.open(LED, encoding="utf-8").read()
    m = "\n## 재개 기록\n"
    if "**외부 교정 셋째 묶음 반영**" not in t:
        t = t.replace(m, "\n" + ENTRY + "\n" + m)
        t = t.replace("- 갱신 시각: 2026-11-13 05:0x (일관성 검토 셋·외부 반박 8.29 반영 종결, 자동 검사 통과(04:5x), PDF 재렌더 중;",
                      "- 갱신 시각: 2026-11-13 05:2x (일관성 검토 셋·외부 반박 8.29·외부 교정 셋째 묶음 반영 종결, 구조 검사 통과(05:2x), KaTeX 검사·PDF 재렌더 중;")
        io.open(LED, "w", encoding="utf-8", newline="\n").write(t)
        print("장부 항목 추가")


if __name__ == "__main__":
    main()
