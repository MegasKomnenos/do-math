# R12 보고의 1절(읽은 범위)을 채운다. 보고 파일만 고친다.
import io
import sys

path = sys.argv[1]
old = "(끝에서 채운다 — 아래 2절을 항목 순서로 써 나간 뒤 확정한다.)"
new = """맡은 파일 넷을 처음부터 끝까지 읽었다(읽지 않은 범위 없음).

- `장v2/부록D_장7A.md` 1–29행: D.{{D:column-certification-k500}}.
- `장v2/부록D_장7B.md` 1–63행: D.{{D:band102-integer}}(1–19행), D.{{D:moment-certification}}(21–43행), D.{{D:column-certificates-501-2000}}(45–63행).
- `장v2/부록D_장8.md` 1–73행: D.{{D:window-mass-env}}(1–19행), D.{{D:band-boxes}}(21–53행), D.{{D:stored-table-check}}(55–73행).
- `장v2/부록D_장9.md` 1–19행: D.{{D:four-families}}.

항목이 가리키는 본문을 열어 맞춘 자리.

- `장v2/장1.md` 151행(계산의 두 방식), 1.5절의 지위·산술 등급 표(196–206행).
- `장v2/장2.md` 정리 {{2:old-2-6}}·명제 {{2:old-2-8}}(156–197행), 보조정리 {{2:power-sum-renewal}}(783–808행), 2.11절(878–938행의 사슬 법칙).
- `장v2/장4.md` 보조정리 {{4:gauss-contraction}}(183행), {{4:hermite-nu}}와 그 증명(244–283행), {{4:vertical-nu}}(417–441행), 명제 {{4:analytic-transfer}}와 그 증명(443–514행).
- `장v2/장5A.md` 정리 {{5:old-5-1}}의 머리와 증명 첫 조각(17–19행), `장v2/부록D_장5A.md` D.{{D:exact-n20000}}의 「확인하는 진술」·「식」·「알고리즘」·「산술 등급」(1–15행; 열 인증과 맞물리는 (ㄱ)(ㄴ)).
- `장v2/장6.md` 따름정리 {{6:old-8-11}}의 $\\mathsf u(k)$(597–599행), 명제 {{6:old-8-23}}(780–784행).
- `장v2/장7A.md` 7.1절(11–53행), 보조정리 {{7:column-lemma}}·명제 {{7:old-6-9}}(196–228행), 7.3절 전부(232–422행: {{7:prime-decomposition}}, {{7:pole-unique}}, {{7:fourier-lemmas}}, {{7:pole-frame}}, {{7:old-6-11}}, {{7:lemma-P-prime}}, {{7:theorem-G-prime}}).
- `장v2/장7B.md` 7.4절 머리와 보조정리 {{7:moment-recursion}}(1–29행), 「해석적 연쇄」·명제 {{7:integer-strips}}·정리 {{7:old-6-13}}의 머리와 증명 앞부분(160–195행).
- `장v2/장8.md` 8.2절(104–410행: {{8:escape-lower}}, {{8:envelope-H}}, {{8:envelope-HG}}, (8.8)–(8.21), {{8:closed-form-envelope}}, {{8:table-tolerance}}, {{8:large-q-bounds}}, {{8:cell-bound}}, {{8:reduction-J}}, {{8:old-6-28}}), 8.3절·8.4절(411–561행: {{8:old-6-30}}–{{8:old-6-32}}, {{8:hazard-H1}}, {{8:old-6-33}}와 그 증명 세 단계).
- `장v2/장9.md` 9.6절(352–560행: {{9:families}}, {{9:old-8-30}}–{{9:old-8-35}}, {{9:bulk-majorants}}, {{9:check-na}}, {{9:check-ga}}, {{9:old-8-36}}).
- `장v2/장10.md` 10.2절의 설명 문단과 표(15–38행; 여덟 행 29–36행).
- `장부_v2.md` 357행(7장 부록 D의 국소 글자 묶음)·1379행, `장v2/부록C.md` 424행, `의존지도_v2.md` 226행(지적이 닿는 자리의 확인).

자료(읽기만 함).

- 기록 사본 `원고_자료/rc9aee43/`, `r475ada3/`, `r6b37c7e/`, `r10ff8c2/`, `rb7effe0/`, `r030ffae/`, `rfc69320/`와 `원고_자료/README.md`·`재실행표.md`의 해당 줄.
- 이 글의 재계산 `원고_자료/세션_재계산/column_k500_iv/`, `moment_cert_iv/`, `column_cert_iv/`, `window_mass_env/`, `r030ffae_window/`, `band_boxes/`, `four_families_DDLnat/`의 코드 머리와 요약 출력, 열별 결과 파일.
- 기록 폴더(읽기 전용)의 `exposition.md`·`review/feedback.md` 절 머리와 인용된 절, `evidence/`·`review/`의 코드와 출력: rc9aee43, r475ada3, r6b37c7e, r10ff8c2, rb7effe0, r030ffae, rfc69320, re71a735. 「자료」 줄의 기록 경로는 항목마다 실제로 있는지 확인했다.

검산 스크립트(`scripts/수학검사2/`): `검토전체23_R12_counts.py`(열 인증의 비교 수·정수 부등식), `검토전체23_R12_audit_tally.py`(감사 $1871$회·음의 하계·$\\omega$·실행 1–4의 비교 수), `검토전체23_R12_colcert.py`(열별 인증서 「결과」의 수와 모멘트 인증의 위치 수), `검토전체23_R12_boxes.py`(띠 상자의 격자 수), `검토전체23_R12_seam.py`(이음새 네 값·제타 상수·최소 여유의 설명값), `검토전체23_R12_sec1.py`(이 절을 채운 편집 스크립트)."""
s = io.open(path, encoding="utf-8").read()
assert s.count(old) == 1
s = s.replace(old, new)
io.open(path, "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))
