# 인계 — UD (부록 D 전부, `exact_check.py`) (2026-11-15 12:3x)

새 글자·새 라벨·바뀐 이름: UD는 새 글자를 고르지 않았다. 바뀐 것은 다음 둘뿐이다.

| 종류 | 전 | 후 | 자리 |
|---|---|---|---|
| 라벨(부록 D 항목이 가리키는 진술) | `{{5:zeta-constants}}` | `{{2:zeta-constants}}` | `부록D_장2.md` 34·36행(옮긴 항목 D.{{D:zeta-constants}}; D 라벨은 그대로) |
| 수(exact_check 재실행) | `rescaled_enclosure_checks` 71,036 · `sign_checks` 21,106 | **71,638 · 21,166** | `left_columns_k2_120/exact_check.json`, `부록D_장5A.md` 19행 |
| 낱말 | 「최소 상대 여유」(D.exact-n20000 (ㄱ)(ㄴ)·독립 재계산, D.column-certification-k500 결과·독립 재계산) | 「인증 여유」(분모를 함께 적음) | `부록D_장5A.md` 17·19행, `부록D_장7A.md` 23·25행 |
| 항목 자리 | D.zeta-constants가 `부록D_장5B.md`(5.5절 묶음) | `부록D_장2.md` 끝(2.9절 묶음; fiber-nonunimodal-bound 뒤) | D 번호가 zeta부터 하나씩 밀림(조립기가 매김) |

행 번호는 12:3x 기준이다. 서식: 파일, 자리, 전→후 제안, 까닭.

1. `장v2/장11.md`, 11.2절 표 37행(D.zeta-constants 행), 2열 「보조정리 {{5:zeta-constants}}」→「보조정리 {{2:zeta-constants}}」, 4열 「5.5」→「2.9」, 행 위치를 2장 묶음(D.fiber-nonunimodal-bound 행 바로 뒤)으로 옮김. 까닭: 항목이 `부록D_장2.md`로 옮겨 가 D 번호 순서가 바뀌었고 라벨이 바뀌었다(판정 1항). 5·6열은 sync. (U11)
2. `장v2/장11.md`, 11.3절 104행 「세 제타 상수: 보조정리 {{5:zeta-constants}} | 보조정리 {{5:zeta-constants}}: 방향 반올림 구간 | …」의 라벨 둘 → `{{2:zeta-constants}}`. 까닭: 같은 이동. (U11)
3. `장v2/장11.md`, 11.2절 표 27·29·30·32·35·38·44·46·60행의 5·6열(꺾쇠와 「독립 재계산」). 부록 D의 같은 줄이 바뀌었다: 27행 crossing-small-n(독립 재계산 둘째 문장·`pv_check_rows.py`), 29행 exact-n20000(「인증 여유」 낱말, 71,638·21,166), 30행 c50(첫 문장 삭제, 56,152 괄호), 32행 tail-T1(첫·마지막 문장 삭제), 35행 critical-window-rig(기록 결함 서술 → 중립 한 문단; 자리표시자 그대로), 38행 band-check(7.72 문장 삭제), 44행 column-certification-k500(「인증 여유」), 46행 self-consistent-constants(꺾쇠 「범위 전체」와 새 서술), 60행 band-LP(5·6열은 그대로이나 결과 줄은 표에 없음 — 변경 없음일 수 있음), 51행 column-certificates-841-2000(187열 괄호). 까닭: 표 5·6열은 부록 D에서 생성(`_sync_11_2행.py`). (세션)
4. `scripts/_gen_재실행표.py` 61행 CONFIG["exact-n20000"]의 expect 문자열 「exact_check success: True(enclosure 36,421·rescaled 71,036·sign 21,106, failures 0)」→「rescaled 71,638·sign 21,166」; 그 뒤 `원고_자료/재실행표.md` 15행 재생성. 까닭: J11-1 재실행. (세션)
5. `원고_자료/README.md` 486행 `세션_재계산/left_columns_k2_120/code/exact_check.py`·491행 `exact_check.json`의 SHA-256 재생성(`자료묶음_v2.py`); 562행 설명 문단은 수를 적지 않아 바꿀 것이 없으나 「(비교 1,175,466개, 실패 0, 최소 상대 여유 $1.2608\times10^{-4}$ …)」의 「최소 상대 여유」는 부록 D의 「인증 여유」와 낱말이 갈리므로 `_patch_README_세션파일.py`의 PARAS에서 「최소 인증 여유」로 맞추기를 권함(558행 column_k500_iv 문단도 같음). 까닭: 자료 파일 내용 변경과 J12 5A-1의 낱말. (세션)
6. `원고_자료/README.md` 560행 「부록 D의 유한 크기 전달 $\mathsf X'$의 다섯 층 인증 항목」→「부록 D의 유한 크기 전달의 다섯 층 인증 항목」. 까닭: J6-3 연동으로 D 항목 제목에서 `$\mathsf X'$`를 뺐다(`_patch_README_세션파일.py` PARAS). (세션)
7. `장v2/장5A.md` 23행(정리 {{5:old-5-1}} 증명 둘째 조각) 괄호 「상대 여유(한 칸 차분을 항의 크기로 나눈 값)」→「(한 칸 차분을 누적 개수 $A_{n,k-1}$로 나눈 값)」 또는 「인증 여유」. 까닭: J12 5A-1 (ii); 그 수 $2.6\times10^{-7}$은 기록 r15df76b의 $(b_{n,k}-b_{n,k-1})/A_{n,k-1}$의 하계이고(기록 123행) 1.5절의 $d/b$가 아니다. 부록 D (ㄴ)은 그렇게 고쳤다. (U3)
8. `scripts/_gen_재실행표.py` 81행 CONFIG["column-certification-k500"] expect 「최소 상대 여유 $1.3778…$」·222행 「열일곱 구간의 최소 상대 여유」 — 81행은 부록 D 7A가 「인증 여유」로 바뀌었으므로 같은 낱말로; 222행(window-mass-env)은 부록 D 8장이 「상대 여유」 그대로이니 그대로. 까닭: 재실행표 낱말을 부록 D와 맞춤. (세션)
9. `장v2/장7A.md` 729행 머리 「(유한 크기 전달 $\mathsf X'$)」와 715행 「명제 $\mathsf X'$」 — J6-3(U6). 부록 D 71행 제목은 UD가 고쳤다. `의존지도_v2.md` 246행·`장부_v2.md` 979행은 생성·첫 판 이름이라 그대로. (U6·생성)
10. D 번호 이동 알림: zeta-constants 항목이 `부록D_장2.md` 셋째 항목(D.3)이 되어 D.3 이후 번호가 하나씩 밀린다. 장 파일·장부·구조표에 고정 D 번호는 없음을 확인했다(`부록 D\.[0-9]` 0건). `의존지도_v2.md`·`대조v2/라벨_번호_대응표_1114.md`·11.2 표의 행 차례는 생성기가 다시 매긴다. (세션)
11. `장v2/부록D_장7B.md` 13행 (ㅁ) 「F1: … 최소 상대 여유 $2.639\cdot10^{-7}$($(9999,20001)$). F2: … 최소 상대 여유 $1.9\cdot10^{-4}$」의 분모가 적혀 있지 않다(기록 r6b37c7e `audit_f1_f2.json`·`audit_strip*.json`). 1.5절 정의대로 $d/b$인지 (ㄴ)처럼 $d/A$인지 확인한 뒤 낱말·분모를 맞출 자리. UD는 열지 않았다. (세션 또는 5차 검토)
12. **(13:1x 갱신) 기다리던 인계 셋 모두 처리됨.** U7 몫(7B 삼중)·U9 몫(9장 $\vartheta$)·U3 몫(5A 92·94·114행)을 반영했다. 남은 「대기」 없음.
13. (U7 인계 반영; 알림) `장v2/장11.md` 11.2 표 49행(D.band102-integer 행) 6열 — 부록 D 15행 「다섯 삼중과 열한 행」으로 sync. 2열·4열은 변동 없음. (세션)
14. (U9 인계 반영; 알림) `원고_자료/재실행표.md` 47행(D.pair-one-variable 행)의 「$\vartheta\in[0.48,1]$에서 $\mathfrak F(6668,\vartheta)\ge1.149$」는 부록 D 51행에서 생성되므로 재생성하면 $\mathfrak j$가 든다. `장11.md` 11.2 표 61행·11.3 118행에는 $\vartheta$가 없음(U9 인계 10과 같음). (세션)
15. (알림) 번역 측 전달 문서: 부록 D의 이번 변경 가운데 번역에 닿는 것 — D.zeta-constants 항목의 장 이동(2장 묶음), 「상대 여유」→「인증 여유」(D.exact-n20000·D.column-certification-k500), D.xcert-partAB 제목에서 `$\mathsf X'$` 제거, D.band102-integer 다섯 삼중, D.pair-one-variable의 $\mathfrak j$, D.critical-window-rig 중립 문단, D.crossing-small-n·D.self-consistent-constants·D.seed-certificates-k120 서술 변경. (세션)
16. (U3 인계 1·2 반영; 알림) `장v2/장11.md` 11.2 표 33행(D.bernstein-signs 행) 2열 「보조정리 {{5:kernel-bounds}}, 정리 {{5:old-5-7}}」→「정리 {{5:old-5-7}}」(U11; U3 인계 15와 같음); 5열 꺾쇠는 「〔구현 같은 코드 재실행·다른 방법; 범위 전체; 산술 정확 정수·유리수·배정밀도 평가; 자료 기록〕」, 6열은 새 「독립 재계산」 줄로 sync(세션). 3열 「정확 정수·유리수」·4열 「5.2」는 그대로.
17. (U3 인계 2 반영; 알림) `원고_자료/README.md` 820–839·982–983행 bernstein-signs 자료 표에서 (ㄱ) 자료 `r690be93/kernel-proof.md`(836)·`kernel_audit.py`(837)·`k1k2_check_output.json`(835)과 r7798355의 `effective-concavity-proof.md`(982)·`kernel-check.json`(983)을 빼고, 새로 자료 줄에 든 `evidence/producer/certify_entry.py`·`evidence/peer/kernel_sample.py`를 더한다(`자료묶음_v2.py`가 만드는 표이면 재생성). `peer/kernel_sample/*.json`(823–829)·`reproduction/*`(830–834)·`tsv_crosscheck_output.txt`(838)·`window_check.json`(839)은 (ㄴ)의 자료라 남긴다. `scripts/_재실행표_여유.json` 14행 「bernstein-signs」 값 「(ㄴ) 전체 최대 계수 $-0.02965$ 대 문턱 $0$($<-\frac1{40}$); (ㄱ) 정확 유리수 부호·항등식(여유 개념 없음)」→「전체 최대 계수 $-0.02965$ 대 문턱 $0$($<-\frac1{40}$)」. `_gen_재실행표.py`의 bernstein-signs CONFIG에 (ㄱ) 코드·출력(`kernel_audit.py`, `kernel-audit.json`, `k1k2_check_output.json` 등)이 들어 있으면 뺀다(UD는 CONFIG를 열지 않았다). (세션)
18. (알림) D.bernstein-signs의 「독립 재계산」 꺾쇠에서 산술 「60자리 평가」가 「배정밀도 평가」로 바뀌었다. 지운 (ㄱ)의 60자리 대조가 빠지고 남은 「다른 방법」(`kernel_sample.py`)이 float64 진단이기 때문이다. 11.2 표 33행 5열 sync 때 같이 바뀐다(16번). (세션·U11)
