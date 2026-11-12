# 의존 지도 대조 보고서: P◇ 경로(2절)와 4절 항목 1–7, 10, 11, 16

작성 2026-11-12. 대상 `C:\math\임시\주차함수_증명\의존지도.md`의 2절 36행과 4절 지정 항목. 기준 원본은 인스턴스 `C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\`(아래 `K`)의 기록 원문, `review/assessment.json`, `review/feedback.md`, `frontier.md`(Revision 382), `glossary.md`다. 기록의 수학은 다시 증명하지 않았다. 기호는 `장부_기호용어이름.md` 1.1·1.2절의 변환표를 적용한 뒤 내용으로 비교했다.

판정 요약: 36행 가운데 일치 17, 정정 19, 미확인 0. 정정 19건은 세 갈래로 나뉜다.
- 입력 확정 3건(8·12·13행): 세션이 "대조에서 확정"으로 남겨 둔 출처를 정한 것이다.
- 경미한 보충 4건(5·11·14·34행).
- 내용 정정 12건: 주장 ID, 지위 표지, 빠진 입력, 비고의 상수 이름.

중대 사항은 6건이다: 1.3 (가)(나), 1.4의 장부 Ψ^low와 변환표 누락, 1.5, 1.6.

---

## 1. 중대 사항

### 1.1 미지지 입력: 없음

2절의 입력 열에 적힌 주장, 그리고 대조에서 확정하거나 보충하라고 제안한 주장은 모두 각 기록의 `assessment.json`에서 `supported`다. 의존 기록 안에 미지지 주장이 7개 있지만 어느 것도 2절의 입력이 아니다. 목록은 이렇다: [rae1f209]/p-pair-analytic-feasibility, [r5909c9e]/c-k6668-ledger, [r4868e30]/p-landing-reading, [r6f5f48f]/pr-landing-and-first-layer·pr-numerics, [r39ea75d]/apriori-bound·row-float-check, [r79ee9e0]/c-thmF-U, [r6b37c7e]/twocap-check.

### 1.2 철회·우려: 없음

`K/frontier.md`의 첫 줄들은 `Revision: 382`다. 의존 지도가 기준으로 적은 판 376보다 여섯 판 뒤다. 지정한 노드 절 15개와 root 절에 concern·withdrawn·retracted 표시가 없고, 해당 노드는 모두 `State: informal_proved`다(bvtheta-bulk만 `unresolved`이며 이는 원래 상태다). 의존 기록 29개의 `assessment.json`에서 `concerns`는 모두 빈 목록이다. frontier 전체에서 concern이라는 낱말이 나오는 자리는 1381행 하나뿐이고, 그것은 질문 본문의 "the question concerns"라는 영어 표현이다. 기록별 결과는 4절 항목 11에 있다.

### 1.3 기록 사이의 어긋남

**(가) 같은 기호 W₀′가 두 기록에서 다른 양이다. 변환 장부 2.7이 틀린 쪽을 7.4에 배정했다.**
- [rae1f209] §1(공표 r77e234e1/p-theta-circ-kernel-bound에서 옴): "W₀′(N) := Σ_(g=k+2)^N ϖ_N(g)k/g".
- [r5909c9e] §3.4(정리 P◇′의 증명): "A^◇_N/p_N ≤ s_N(1 − W₀′),  W₀′ := Σ_(g=k+104)^N ϖ_N(g)k/g". 이것은 [rae1f209] §5.1의 W₀″(N)이다.
- `장부_기호용어이름.md` 2.7은 "$W_0'(N)$ | 생존 없는 핵 질량 상계의 양 $\sum_{g\ge k+2}\pi_N(g)k/g$ | 7.4 | [rae1f209] §1"로 적었다. 그런데 7.4(정리 P◇′)에서 쓰는 양은 g ≥ k+104 쪽이다. 두 주장은 모두 지지되었고, 수학이 아니라 표기가 어긋난다. 7.4에서는 [rae1f209]의 W₀″와 같은 기호를 쓰거나 새 글자를 정해야 한다.

**(나) 크기 결합 두 부등식의 지위를 기록마다 다르게 적었다.**
- [r60a6f55]/size-coupling은 "비형식 정리"이고 문헌(Fleurat v2 정리 1)에 기댄다. 결합 Mtilde_n ≤ Mtilde_(n+1) ≤ Mtilde_n+1과 부등식 a_(n+1)(ℓ) ≤ a_n(ℓ) ≤ a_(n+1)(ℓ+1)을 함께 준다.
- [r79ee9e0]/c-lemma-sh는 같은 두 부등식 (DM0)·(SM)에 대한 "증명(... 외부 정리 없음)"이다. review는 "마지막 차 재귀와 결합만 쓰는 m 귀납이 ... 닫힌다"며 증명으로 지지했다.
- [rb6a2cd0]의 review는 P⁺⁺가 "V-core·크기 결합(비형식)"에 기댄다고 적었다.
- 두 판정 모두 지지 상태다. (SM)·(DM0)만 쓰는 행은 c-lemma-sh로 손 증명 위에 놓을 수 있다. 결합 자체(0 또는 1 증가)는 문헌 위에 남는다. 어느 쪽을 택할지는 세션이 정한다. 2.8 크기 결합 행의 정정이 이 점과 관련된다.

### 1.4 변환표의 어긋남

- 1.1절과 1.2절 가운데 P◇ 경로가 쓰는 항목은 모두 기록과 맞는다. 그 항목은 ϖ_N(s)→π_N(s), 표시 나무 무게→𝒯_n, P₀→π⁰_N(k), r_N 두 가지, s_N·q_N·t_N, c^±_m, ℓ_N, L_m, δ_k, w_m(s), c_m, X_n, V_m, N′₂·M₂, E_m, Ψ, U(D), Υ̂_k, g̃, g, 창 좌표다. 확인한 근거는 [rae1f209] §1, [rb6a2cd0] §1.2, [r5909c9e] §1, [r030ffae] §1, [r4868e30] §1의 정의문이다.
- **장부 2.7의 어긋남 둘.** 첫째는 위 1.3 (가)의 W₀′다. 둘째로 장부는 "$\xi$, $\Psi^{low}(\xi)$"라 적었다. 그러나 [r5909c9e] §3.2의 Ψ^low는 정수 b(또는 d)의 함수다: "Ψ^low(d) := 0.3989(2√d − 1.678)". 보조정리 8도 b 단위로 적분한다("I_i(k) := ∫_a^(c−1)Ψ^low(x)dx", a = y_ik^(2/3)). 그러므로 Ψ^low의 인자는 ξ = b/k^(2/3)가 아니다.
- **변환표에 빠진 것.** [r4868e30] §1의 "c_N(κ):=min(N,κ)·A_(N−1,κ−1)"(나무 개수)이 표에 없다. 2.9(정리 T)를 [r4868e30]에서 옮길 때 이 기호가 새 원고의 수준 질량 c_m(Y)와 충돌한다. 같은 기록은 "c_0:=1"로 두므로 Ren(0)의 규약도 함께 정해야 한다.

### 1.5 지위 열이 컴퓨터 보조·비형식 입력을 드러내지 않는 행(정정 7건)

7.3의 정리 10·11, 보조정리 4.1·따름정리 12·13, 정리 P, 정리 P⁺와 7.5의 정리 Q, P◇∧띠⇒B⁺가 여기에 든다. 이 행들의 지위는 "증명"이거나 "증명(공표 입력 위)"인데, 기록과 review는 다음을 적는다. H*₊는 "구간 산술 인증"이다([rb6a2cd0] §1.3). (V) c-vcore-quant는 "[비형식 증명 ...]"이다. 정리 P는 "닫힌 꼴 상수의 수치 평가 포함"이고, 정리 P⁺·P⁺⁺는 "binary64 ... 구간 산술 아님"이다. 정리 Q의 승인 사유는 "근거는 컴퓨터 보조 공표 입력과 binary64 유한 확인이다"다. 완료 조건 1은 "지위와 좌표와 함께 인용"이므로 이 차이는 본문의 지위 표지로 그대로 옮겨진다. 행별 문구는 5절에 있다.

### 1.6 존재하지 않는 주장 ID(정정 1건)

2.9 정리 T 행의 "c-theorem-T"는 [r4868e30] `record.json`에 없다. 정리 T의 주장 ID는 **c-threshold-subtree**다(진술 첫머리 "[증명] 정리 T. k≥2를 고정하고 ..."). c-inner-head-sum은 실재한다.

### 참고: 중대 사항은 아니지만 집필에서 부딪칠 이름 충돌

2절 안에 같은 이름이 다른 진술을 가리키는 자리가 있다. 새 번호를 붙일 때 구별해야 한다.
- "보조정리 C": [rae1f209]의 수준 방문 보존(2.8)과 [rb6a2cd0]의 꼬리 상한(7.3).
- "보조정리 1"·"보조정리 4": [rae1f209]와 [r5909c9e]에서 서로 다르다.
- "(E1)": [r030ffae] §3.1의 r_L 한 블록 재귀와 [r5909c9e] §4.4의 PAIR 한 블록 꼴(2.10).
- "명제 B": [rae1f209]의 행 조건 식과 [r5909c9e]의 창×창 극한.
- "정리 T"·"보조정리 T": [r4868e30]과 [rae1f209].
- "정리 P"·"명제 P": [rb6a2cd0]과 [r5909c9e] §6.3.

---

## 2. 읽은 범위

| 파일 | 읽은 범위 | 대략의 행 수 |
|---|---|---|
| `의존지도.md` | 전문 | 104 |
| `장부_기호용어이름.md` | 1.1–1.3절(15–110행), 2.7절(228–251행) | 120 |
| `연구_파악.md` | 2.1–2.2절(27–92행), 8절(187–232행, 참고) | 110 |
| [rae1f209] exposition.md | 전문 | 375 |
| [rae1f209] record.json / assessment.json | claims 26개 전부와 nodes·relations·glossary / claims·nodes·relations 판정 전부 | 447 / 188 |
| [rae1f209] feedback.md | 1–120행, 120–190행은 grep | 약 150 |
| [rb6a2cd0] exposition.md | 전문 | 475 |
| [rb6a2cd0] record.json / assessment.json | claims 31개 전부와 relations / 판정 전부 | 673 / 177 |
| [rb6a2cd0] feedback.md | 1–40행 | 40 |
| [r5909c9e] exposition.md | 전문 | 374 |
| [r5909c9e] record.json / assessment.json | claims 16개 전부와 solutions / 판정 전부 | 362 / 104 |
| [r5909c9e] feedback.md | 1–30행, 72–88행 | 47 |
| [r4868e30] exposition.md | §1–§3.4(29–191행) | 163 |
| [r4868e30] record.json / assessment.json | claims 목록 전부, c-threshold-subtree·c-inner-head-sum 전문 / 판정 전부 | — |
| [r030ffae] exposition.md | §1(24–45), §3.1(62–77), §3.7–3.8(165–188), §4(189–213), §4′(215–230, 255–264), §4″.2–4″.6(301–389) | 약 210 |
| [r030ffae] record.json / assessment.json | e1-one-block, theorem-W, theorem-B-prime, theorem-B-mono, theorem-B-triple, lemma-cap-shift, largest-tree-facts, band-node의 진술과 판정, solutions | — |
| ID·진술만 확인한 기록 22개 | 파견문이 지정한 주장의 record.json 진술 전문과 review 사유. 기록마다 전체 claim ID 목록, relations, solutions | 기록당 10–40 |
| 추가로 확인한 기록 5개 | [r207f124]/diag-lossless, [re597c0e]/c-sojourn-identity, [r52e9c83]/c-lemma4-chain·c-lemma5-neg-bound, [r2ec875c]/c-psi-correction, [r0ee343a]/p-exp-form·p-capacity-differences | — |
| `K/frontier.md` | 1–4행(Revision), root 절(5–49), 지정 15절의 State와 관계 목록 전부, 파일 전체 키워드 grep | 1463행 가운데 약 250 |
| `K/glossary.md` | 지정 6항목: 표시 나무 무게, 문턱 나무 항, 제한 성장비, 갱신 방문 핵, 수준 방문 보존 하계, 숲–나무 재생 원천 | 60 |

---

## 3. 행별 판정 표(의존지도 2절, 36행)

판정의 근거 문구는 각 기록 원문에서 옮겼다. "입력 보충"은 기록의 증명이 쓰는데 행에 적히지 않은 입력이다.

| # | 새 글의 자리 / 진술 앞부분 | 판정 | 근거와 차이 |
|---|---|---|---|
| 1 | 2.10 / 다섯 조각 분해 d_n=−Θ_n+FL^(5)_n+… | 일치 | [r6f5f48f]/pr-five-pieces "정수 k≥2와 2k+1≤n≤3k−1에서 d_(n,k)=…=−Θ_n+FL_n+BV_n+KD_n+PAIR_n"(지지). 지수 공식의 출처는 [r0ee343a]/p-exp-form이고 행은 글 안 2.6을 가리킨다. |
| 2 | 2.10 / 쌍 항의 정수 꼴과 비음성, 확률 꼴 | 일치 | [rae1f209]/c-pair-explicit "[증명; 공표 r6f5f48f2/pr-five-pieces의 재유도] … 모든 항이 음이 아니다"(지지). 확률 꼴은 §2.3에 있다. |
| 3 | 2.10 / 한 블록 꼴 PAIR_n=½Σ_sC(n,s)[…], Θ_n=C(n,k)v_kA | 일치 | [r5909c9e] §4.4 "2k ≤ n ≤ 3k−1이면 PAIR_n = ½·Σ_(s=k)^(n−k) C(n,s)·[v_s·b_(n−s,k−1) + u_s·b_(n−s,k)], Θ_n = C(n,k)·v_k·A_(n−k,k−1) (E1)". 주장 c-pair-marginal-identity(지지). "peer는 3 ≤ k ≤ 8의 … 정수로 같음을 확인". 행의 범위(2k≤n≤3k−1)는 비어 있지만 틀린 것은 아니다. 주장 ID를 적고 (E1) 이름 충돌을 피하기를 권한다. |
| 4 | 2.8 / 크기 결합 s_(m+1)(k)≤s_m(k), s_(m−1)(k)≤s_m(k+1), 0 또는 1 오름 | **정정** | 진술은 변환 뒤 [r60a6f55]/size-coupling "a_(n+1)(ell)<=a_n(ell)<=a_(n+1)(ell+1)"과 같다. 입력: "[r79ee9e0]의 초등 재증명"의 주장 ID는 c-lemma-sh다. 기록들이 실제로 인용하는 재진술 [r207f124]/diag-lossless가 빠졌다([rae1f209] §1 "r207f1244/diag-lossless로 재진술", p-visit-conservation "공표 r207f1244/diag-lossless (DM0) 위"). 지위: 두 부등식은 c-lemma-sh로 손 증명이 지지되어 있다(1.3 (나)). 문헌 비형식인 것은 결합 진술뿐이다. |
| 5 | 2.8 / 보조정리 C(수준 방문 보존) | **정정**(경미) | 진술·ID·지위는 [rae1f209]/p-visit-conservation(지지)과 일치한다. 입력 (DM0)의 기록 식별자 [r207f124]/diag-lossless가 빠졌다. review의 귀속 정정이 비고에 없다: "무게 없는 꼴은 공표 체류 항등식 re597c0e7/c-sojourn-identity(…)의 Σπ=1−F+Σσ에서 음이 아닌 머묾 항 σ를 버린 것이다. … 이 기록의 새 몫은 무게 판과 정리 F′와의 결합이다". |
| 6 | 2.9 / 정리 T (i)–(iv), 따름정리 (a)–(d) | **정정** | 주장 ID "c-theorem-T"는 없다. **c-threshold-subtree**가 맞다(1.6). c-inner-head-sum은 맞다. 입력 보충: (iii)의 사슬 구조 "[공표 r33475a7c p-heavy-path-ratio]", (d)의 "공표 c-psi-correction의 Ψ(J)≤0.7979√J"([r2ec875c]/c-psi-correction). 지위 "증명"은 review와 맞는다("(a)–(d)는 증명으로 지지"). 끝 맞물림은 발견적이다. 비고 "[r52e9c83] 보조정리 4·5와 같음"은 맞다. 단 원문은 "(i)의 점별 부호와 (ii)의 첫 층 판"이라 적었다. |
| 7 | 7.1 / 보조정리 1: A°_N/p_N=P₀(N)+(k/(k+1))ϖ_N(k+1) | 일치 | [rae1f209] §2.1, c-theta0-closed-form(지지). 범위는 k+2≤N≤2k+1이고 행에는 없다. 비고의 무게중심 정지 확률 [r2fe0259]/p-centroid-stop 숲 꼴 "(1−π_2(F+1))/(F+1)"이 맞다. 기호는 [rae1f209]의 ϖ_N(=새 원고 π_N)이다. |
| 8 | 7.1 / 병합 항등식 BV_n=ΣK_n(m)L_m, Θ_n−Θ°_n=ΣK_n(m)c_mΘ_m | **정정** | 입력이 "대조에서 확정"으로 비어 있다. 확정: **[r6f5f48f]/pr-merge-identity**. 진술은 "2k+2≤n≤3k−1에서 Θ_n=Θ°_n+Σ_(m=2k+1)^(n−1)C(n,m+1)p_(n−1−m)·(k(m+1)/(m+1−k))·Θ_m"(지지)이다. 범위 2k+2≤n≤3k−1을 적는다. BV_n=ΣK_n(m)L_m은 BV의 정의다. |
| 9 | 7.1 / 보조정리 T(잘린 병합 항등식) | 일치 | [rae1f209] §5.1, p-truncated-merge(지지). 진술은 글자 그대로 같다. "k = 3–8, 0 ≤ T ≤ k−1의 모든 n에서 정확 유리수로 확인". |
| 10 | 7.1 / 보조정리 4: A^◇_N/p_N=P₀(N)+Σ_(g=k+1)^(k+103)… | 일치 | [r5909c9e] §3.2 "k+1 ≤ N ≤ 2k−1이면 A^◇_(N,k)/p_N = P₀(N) + Σ_(g=k+1)^(min(N,k+103)) ϖ_N(g)·(k/g)·s_(g−1)". 정확한 항등식이고 c-pdiamond-theorem 안에 있다. |
| 11 | 7.1 / 정리 A: X_n=ΣK_n(m)c_mΘ_m(𝒬_m−1); (가)(나) | **정정**(경미) | [rae1f209]/c-reduction-theorem-A "[증명; 공표 병합 항등식 위]"(지지). 입력에 병합 항등식([r6f5f48f]/pr-merge-identity, 8행)을 적는다. |
| 12 | 7.2 / 명제 B(행 조건의 정확한 식) | **정정** | (OB)의 출처를 확정한다: **[r77e234e]/ob-identity**. 근거는 c-row-identity-B "[증명; 공표 r77e234e1/ob-identity 위]"(지지)이고, ob-identity도 지지다. |
| 13 | 7.2 / 보조정리 V: V_m=b_(m,k−1)+M₂, L_m≥(1−δ_k/2)(…) | **정정** | 보조정리 P의 출처를 확정한다: **[r77e234e]/lemma-P**. 근거는 p-lemma-V "[증명; 공표 r77e234e1/lemma-P 위] 정수 k≥2와 2k≤m≤3k−1에서 … V_m=b_(m,k−1)+M₂"(지지)이다. 범위: 항등식은 2k≤m≤3k−1, L_m 부등식은 2k+1≤m≤3k−1. |
| 14 | 7.2 / 명제 R(행 조건의 귀납) | **정정**(경미) | [rae1f209]/p-row-criterion(지지). 입력 보충: 공표 "Θ°/Θ≤1−W₀′"([r77e234e]/p-theta-circ-kernel-bound), 보조정리 V·정리 A·보조정리 1·명제 B(record.json 의존성), 크기 단조성 (SM). |
| 15 | 7.2 / 정리 AR 네 단계 | **정정** | 지위 "증명(공표 입력 위)"는 review "공표 입력(정리 B‴은 컴퓨터 보조, 정리 F′, 크기 결합, 보조정리 F·P, 무게중심 꼴, (OB)) 위의 증명으로 지지"와 맞는다. 검토 단서도 맞다. 상수가 모두 맞는다: L_*(6668)=1.206, δ_k≤6.62/√k, 띠 ≤1.0845, 벌크 ≤1.0786(k=6668). 입력 보충: **보조정리 V**(p-lemma-V; (3)의 띠 행 "보조정리 V와 합치면"), **보조정리 T**(p-truncated-merge; (3)의 벌크 행 "보조정리 T의 항별 꼴", (4)의 "보조정리 T(T = 102)에 이 결과를 넣은 것"), 명제 B/(OB)(c-row-identity-B가 record.json 의존성), 초등 경계 "π₂(M) ≤ (8/(πM))^(1/2)". 주장 ID: p-analytic-row-theorem(본체), p-landing-minorant((1)), p-delta-bound((2)). |
| 16 | 7.2 / 따름정리: P◇이면 B⁺ | 일치 | [rae1f209] §5.1 따름정리. 관계 주장은 p-pair-node-relation이다(32행 참조). |
| 17 | 7.3 / 명제 2.1 분해 | 일치 | [rb6a2cd0]/c-structure(지지). 의존성은 r05cf8c9e의 네 주장으로 행과 같다. 범위 2k+1≤n≤3k+1. 비고의 fs-source는 주장이 아니라 [r05cf8c9] record.json의 glossary ID이며, `K/glossary.md` 856행 '숲–나무 재생 원천'의 Source다. |
| 18 | 7.3 / 두 나무 꼴 (2.1) | 일치 | [rb6a2cd0]/c-two-tree-form(지지) "ϖ_n(s)는 n!·e^(n+1)·Bor(s)·Bor(n+1−s)·𝔰_(n−s)와 같다". 주의: 이 ϖ는 [rb6a2cd0]의 표시 나무 무게(새 원고 𝒯_n)다. 7·10행의 ϖ(새 원고 π_N)와 같은 표 안에서 뜻이 다르다. 행을 𝒯_n(s)=n!e^(n+1)Bor(s)Bor(n+1−s)s_(n−s)(k)로 적기를 권한다. |
| 19 | 7.3 / 정리 L과 보조정리 R | 일치 | (L)=[rcb2e2d4]/c-weight-monotone "n≥k+1, k≤s≤n−1이면 ϖ_n(s+1)/ϖ_n(s)=e^(g(s))/r_(n−s−1)"(지지). 변환하면 𝒯·𝔯 꼴과 같다. 보조정리 R=c-ratio(지지): 의존성 size-coupling·lemma-cap-shift·c-weight-monotone이 행과 같다. (CS) "(a) t_N/s_N≥(1−1/k)^(ν+1)"([r030ffae]/lemma-cap-shift, 지지). |
| 20 | 7.3 / 정리 10 (a)(b)(c) | **정정**(지위) | 입력 ID와 진술이 모두 맞다. (D) p-lemmaD-sharp "kD_k≥−1−Υ_k". (Υ) p-ups-bound "모든 k≥3131에서 Υ_k=…≤(k−1)g(k)/(2k+1)<0.198". (H*₊) c-hplus "k≥3132와 k+1≤s≤m₁(k)… k·P_s(k)≤−6/5". 지위 "증명"은 입력의 성격을 감춘다. [rb6a2cd0] §1.3 "(H*₊)는 구간 산술 인증이다". p-ups-bound는 "공표 입력 위의 증명"이고, 그 입력 p-row-averaging-e3는 "컴퓨터 보조 인증(n≤20000)과 공표 비형식 증명에 기댄다"(review). review: "c-flat-tails | 공표 입력 위의 증명으로 지지". |
| 21 | 7.3 / 정리 11, (3.2)·(3.3), ϱ^H·ϱ^L | **정정**(지위·입력) | 입력 ID가 맞고, κ_N≥0.307(k≥2000)도 맞다(c-hazard "κ_N≥0.307(k≥2000)"). 지위: (V) c-vcore-quant의 진술 첫머리가 "[비형식 증명; c-vcore와 같은 공표 지지 입력 위]"다. 정리 10을 거쳐 H*₊도 들어온다. 입력 보충: 정리 L(c-weight-monotone), 정리 10(c-flat-tails). 둘 다 record.json 의존성이다. |
| 22 | 7.3 / 보조정리 4.1, 따름정리 12·13 | **정정**(입력·지위) | 입력 열이 위치만 있고 비어 있다. 주장은 c-x-shape "[증명; 닫힌 꼴 함수의 초등 해석, 경계 수치는 binary64와 50자리 mpmath]", c-cor12(의존성에 [r030ffae]/band-node), c-cor13이다. 입력은 정리 11, (V), 정리 L이고, 따름정리 12에는 band-node(B‴, 컴퓨터 보조)가 더해진다. |
| 23 | 7.3 / 정리 P (ν₁=103 at k≥38887) | **정정**(지위·입력) | c-band-thmP "[증명; 공표 입력 위, 닫힌 꼴 상수의 수치 평가 포함]". 경우 (3): "38887≤k≤48965에서는 닫힌 꼴 F_k(103)을 각 k에서 계산했다. … binary64와 50자리 mpmath". 입력 보충: 정리 11, 보조정리 R(c-ratio), 보조정리 4.1(c-x-shape). (B′)·(B‴)는 맞다. 상수 38887, ν₁=103이 맞다. |
| 24 | 7.3 / 보조정리 C(꼬리 상한), 정리 11′, 정리 P⁺ | **정정**(지위·입력) | 보조정리 C=c-tail-cap, 입력 [r4868e30]/c-inner-head-sum (a)가 맞다. 정리 P⁺=c-band-thmP-plus "[증명; 공표 입력 위, 닫힌 꼴 부등식의 유한 확인 포함] … 9467≤k≤38886 … 모든 k에서 확인(binary64, 최소 여유 4.6·10^(−9))". review "binary64 유한 확인으로 지지(구간 산술 아님)". 지위 "증명/계산(블록 확인)"에는 binary64와 범위를 적는다. 입력 보충: (B′), 보조정리 R, (V), (Hz), 정리 P. 문턱 9467이 맞다. |
| 25 | 7.3 / 정리 11″(LP), 정리 P⁺⁺ | **정정**(비고·입력) | 지위 "비형식(binary64 LP 확인, 2799개 k)"가 맞다(6668≤k≤9466은 2799개). 비고 "최소 여유 0.0056"은 원문과 다르다. 원문은 "블록 경계의 최소 여유는 3.1·10^(−7)이다 … 점별 최솟값은 k=6668, ν=103의 F^LP=0.0056이다"이다. 입력 보충: 보조정리 R, 정리 P·P⁺(c-band-thmP-pp 의존성), 보조정리 C(c-tail-cap), 정리 10. |
| 26 | 7.3 / 따름정리 P′⁺⁺ | 일치 | c-lrp2-band-pp: 의존성 finite-P-20000, integer-certificate, theorem-S, theorem-4B, P⁺⁺가 행과 같다. 지위 비형식이 맞다. |
| 27 | 7.4 / 보조정리 1–3 | 일치 | [r5909c9e] §3.1. 보조정리 2 "k ≥ 6668, 1 ≤ b ≤ 4k^(2/3)", 보조정리 3 "a는 366 이상 … (1 − 2.3·10^(−4))", 정리 W가 [r030ffae] §3.7에 있는 것이 모두 맞다. 지위 "증명(정리 W 위)"는 c-pdiamond-theorem "[비형식 증명; 공표 정리 W(컴퓨터 보조) 위 …]"과 합치한다. 사소한 입력(p-exp-form, p-capacity-differences, largest-tree-facts)은 2.10 행으로 대신할 수 있다. |
| 28 | 7.4 / 보조정리 5–6 | 일치 | [r5909c9e] §3.2. Robbins와 Borel 초등 합만 쓴다. |
| 29 | 7.4 / 보조정리 7–8, (3.2), k-단조성, 정리 P◇ | 일치 | 지위 "비형식(… binary64, 40자리 재평가)"가 맞다. 원문: "5200개 구간 … 최솟값은 1.14936 … 40자리 mpmath로 다시 하면 1.149357", "50개 칸". 비고: 정리의 상수는 "PAIR_n ≥ 1.149·…"이다. 1.149357은 격자 최솟값이다. |
| 30 | 7.4 / 정리 P◇′ | **정정**(입력) | c-pdiamond-giant-bound의 의존성은 theorem-W, heavy-path-recurrence, c-lemma-sh, c-pair-marginal-identity, p-exp-form, p-capacity-differences다. 행은 heavy path와 c-lemma-sh만 적었다. **정리 W(컴퓨터 보조)**와 한 블록 꼴(c-pair-marginal-identity), Q^up(보조정리 5–6)을 더한다. 정리 상수는 "2.27"이다. 원문 "최솟값은 2.274이고 θ′ ≈ 0.567"과 행의 2.274는 맞다. |
| 31 | 7.5 / 정리 Q: B⁺⇒LRP₂ | **정정**(지위) | 주장 c-rel-bplus-lrp2(지지)와 입력이 맞다. 보충할 입력은 c-bplus-bulk, [rae1f209]/c-pair-explicit이다. 지위: 입력 P⁺⁺는 binary64 유한 확인이다. 관계 승인 사유: "근거는 컴퓨터 보조 공표 입력과 binary64 유한 확인이다(검토자가 독립 재판정)". |
| 32 | 7.5 / P◇∧띠⇒B⁺ | **정정** | "rel-pairnode-band-implies-bplus"는 관계 ID(전체 sbc38cd…-rel-pairnode-band-implies-bplus)다. 주장 ID는 **p-pair-node-relation**이다. 입력 보충: 정리 AR(p-analytic-row-theorem), 노드 bvtheta-band([r030ffae]/sol-bvtheta-band의 주장 band-node, 곧 B‴). 지위 "증명"을 "증명(공표 입력 위; 정리 AR·B‴, B‴는 컴퓨터 보조)"로 바꾼다. 비고에 review 단서를 옮긴다: "정리 AR의 띠 행은 6668≤k≤9948에서 노드 bvtheta-band의 범위(n≥20001) 밖인 행 m<20001까지 주장 r030ffaeb/theorem-B-triple 자체를 쓴다. … 그 주장이 철회되면 이 관계를 다시 검토해야 한다." |
| 33 | 7.5 / LRP₂⇒W_L♭ | 일치 | 관계 s5a4a7531…-rel-v-lrp2-implies-wlflat, 주장 c-rel-v-lrp2-wlflat(지지). 전제 V, source-side, qstar-columns-2001-3130은 판 382에서 established다. 주장 ID를 적기를 권한다. |
| 34 | 7.5 / W_L♭⇒W_L⇒L⇒T, 네 위치쌍⇒뿌리 | **정정**(경미) | 관계와 주장: [r7c26b8b] rel-wlflat-implies-wl / rel-claim-wlflat-implies-wl, [rb6423c6] rel-wl-implies-left-interior / wl-implies-left-interior("증명(공표 비형식 정리 사용)"), [rce3dc75] left-implies-cross-rel / left-implies-cross, split-four-position-pairs / four-part-cover. 모두 지지다. 전제 central-gap·right-interior(established)를 적는다. 지위를 "증명(공표 입력 위)"로 바꾼다. |
| 35 | 7.6 / 명제 A | 일치 | c-fragmentation-asymptotic "[증명]"(지지). 원문 "공표 r39ea75d8…/bulk-first-order(지지)의 둘째 진술 … 와 같다". |
| 36 | 7.6 / 명제 B·C, 수준 위험률 극한 | 일치 | c-pair-vs-fragmentation-limit, c-pair-theta-asymptotics. 둘 다 "[비형식 유도; …]"이고 지위대로 지지되었다. review 단서: 명제 B의 수치 확인은 θ′=0.8에서 극한 쪽으로 움직이지 않는다. |

---

## 4. 4절 항목의 답

### 항목 1. 공표 병합 항등식: 확인. [r6f5f48f]/pr-merge-identity(supported)

- [rae1f209] §1: "**짝 없는 문턱 손실과 병합 항등식** [공표 r6f5f48f2/pr-merge-identity]. Θ°_n := C(n,k)k^(k−2)A°_(n−k) … 2k+2 ≤ n ≤ 3k−1에서 Θ_n = Θ°_n + Σ_(m=2k+1)^(n−1) K_n(m)·c_m·Θ_m".
- [r6f5f48f] record.json pr-merge-identity: "증명(병합 항등식): 2k+2≤n≤3k−1에서 Θ_n=Θ°_n+Σ_(m=2k+1)^(n−1)C(n,m+1)p_(n−1−m)·(k(m+1)/(m+1−k))·Θ_m, … A°_N=#{크기 N 배치: M≤k−1, 모든 뿌리 블록 크기≤k+1}".
- review: "증명으로 지지. … k=3–11의 모든 2k+2≤n≤3k−1에서 항등식을 정확 유리수로 확인했다."

### 항목 2. (OB): 확인. [r77e234e]/ob-identity(supported)

- [rae1f209] §1: "**다섯 조각과 그 안쪽** [공표 r6f5f48f2/pr-five-pieces, r77e234e1/ob-identity]. … 한 블록 항등식(OB)은 2k+1 ≤ m ≤ 3k−1에서 L_m = Θ_m + k·BV_m + k·FL1_m + E_m + Pair⁺_m".
- [rae1f209]/c-row-identity-B: "[증명; 공표 r77e234e1/ob-identity 위]".
- [r77e234e]/ob-identity: "[증명] 정수 k≥2와 2k+1≤m≤3k−1에서 L_m:=b_(m,k)+b_(m,k−1)은 L_m=Θ_m+k·BV_m+k·FL1_m+E_m+Pair⁺_m을 만족한다." review: "증명으로 지지. … k=3–14의 모든 m∈[2k+1,3k−1]에서 정확히 확인".

### 항목 3. 보조정리 P와 F: 보조정리 P의 기록을 찾았다. [r77e234e]/lemma-P(supported), 보조정리 F는 [r77e234e]/lemma-F(supported)

- [rae1f209]/p-lemma-V 진술 첫머리: "[증명; 공표 r77e234e1/lemma-P 위]". [rae1f209] §1의 "공표 보조정리 P는 Pair⁺_m = N′₂ − M₂ … M₂ ≤ (δ_k/2)V_m"과 [rae1f209] review의 입력 대조 목록 "r77e234e1(ob-identity, lemma-P, lemma-F, p-theta-circ-kernel-bound, centroid-end)"이 같은 출처를 가리킨다.
- [r77e234e]/lemma-P: "[증명] 2k+1≤m≤3k−1에서 Pair⁺_m=N′₂−M₂, … M₂≤(δ_k/2)V_m, … δ_k=max_(k≤N≤2k−1)Pr_N(M=k−1|M≤k−1). 따라서 Pair⁺_m≥−(δ_k/2)V_m." review: "증명으로 지지. … k=3–14에서 항등식과 부등식을 정확히 확인했다."
- [r77e234e]/lemma-F: "[증명] … 따라서 δ_k≤max{f_k, max_(k<N≤2k−1)s_N/(k P₀(N))}." review: 증명으로 지지. [rae1f209] §1 "보조정리 F(r77e234e1/lemma-F, 증명)".

### 항목 4. (S)와 fs-source: 확인

- [rb6a2cd0] §1.3: "(S) | r05cf8c9e/c-rel-onelevel-fs, c-renewal-identity, c-lemma1, c-X-nonneg | FS 노드 범위의 모든 n에서 σ̃_n=λ_k(n)+B_k(n)+𝒳_n …". [rb6a2cd0]/c-structure의 의존성도 이 네 주장이다.
- 네 주장은 [r05cf8c9] record.json에 모두 있고 모두 supported다. c-lemma1 "증명(공표 결과와 같음) … δ_s=k·d_(s−1,k)+b_(s−1,k)+b_(s−1,k−1)", c-X-nonneg "모든 k≥2, n≥0에서 𝒳_n≥0", c-renewal-identity "k≥2, n≥k+2에서 d_n=𝒳_n+K_n+T1_n+Land_n+Σ𝒦(n,m)d_m", c-rel-onelevel-fs "σ̃_n=λ_k(n)+B_k(n)+𝒳_n … B_k(n)≥0".
- fs-source는 **주장이 아니라 [r05cf8c9] record.json의 glossary 항목 ID**다: "id": "fs-source", "name": "숲–나무 재생 원천", "symbol": "σ̃_n(k)". 정의는 "정수 k≥2, n≥2k+1에서 σ̃_n(k)=d_(n,k)−k·Σ_(m=2k+1)^(n−1)C(n,m+1)A_(n−m−1,k−1)d_(m,k)"다. `K/glossary.md` 856–863행에 영구 항목으로 있다("Source: … r05cf8c9e90704aebbe42f8729b4be48d/fs-source"). 그 기록의 assessment는 glossary_approved: True다.

### 항목 5. 정리 L: 확인. [rcb2e2d4]/c-weight-monotone(supported)

"[증명] (정리 L) k≥2, n≥k+1, k≤s≤n−1이면 ϖ_n(s+1)/ϖ_n(s)=e^(g(s))/r_(n−s−1)=e^(g(s)−g(n−s))·𝔰_(n−s−1)/𝔰_(n−s)이다. … 따라서 ϖ_n(s+1)≥ϖ_n(s)이고, 등호는 (s,n)=(k,2k)일 때만 성립한다." review: "증명으로 지지. … 공표 c-sharp·등호 유일성(r051bfe18, 지지됨)으로". 입력에 [r051bfe1]/c-sharp가 들어 있다.

### 항목 6. (D), (Υ), (H*₊): 확인. 진술과 범위가 세션 서술과 같다

- (D) [r696d62c]/p-lemmaD-sharp(supported): "정수 y≥2, y+1≤n≤2y+1에서 y·D2S_n(y)≥−1−y(y−1)c_(n−1)(y−1)/n이다. … n=2k+1이면 첫 층 기저 D_k에 대해 kD_k≥−1−Υ_k(Υ_k=k(k−1)c_(2k)(k−1)/(2k+1))이고 모든 k≥3131에서 kD_k>−1.198이다." 원문은 모든 y≥2에 대한 진술이라 사용 범위를 포함한다([rb6a2cd0] review 같은 판단).
- (Υ) [r29b01e8]/p-ups-bound(supported): "[공표 입력 위의 증명] 모든 k≥3131에서 Υ_k=((k−1)/(2k+1))·k·Pr_(2k)(M=k−1)≤(k−1)g(k)/(2k+1)<0.198(공표 p-row-averaging-e3: k·Pr_(2k)(M=k−1)≤g(k), g 감소, g(3131)=0.395)." 따라서 **진술은 "Υ_k≤Υ̂_k, Υ̂_k=(k−1)g̃(k)/(2k+1)"이 맞다.** g̃는 [r7e03176]의 g(k)=(3/0.35)(1.35+1/k)(0.65−1/k)^(−3/2)k^(−1/2)를 새 원고 기호로 바꾼 것이다. **"<0.198"의 범위는 k≥3131이 맞다.** 근거는 review "Υ_k≤g(3131)/2=0.1975<0.198"이다. 이 주장은 손 증명이 아니라 "공표 입력 위의 증명"이다. 그 입력 [r7e03176]/p-row-averaging-e3는 "컴퓨터 보조 인증(n≤20000)과 공표 비형식 증명에 기댄다"(review).
- (H*₊) [r33475a7]/c-hplus(supported): "[증명; 공표 명시 경계 위의 구간 산술 인증] (정리 H*₊) 모든 정수 k≥3132와 k+1≤s≤m₁(k)인 모든 정수 s에 대해 k·P_s(k)≤−6/5이다." review: "공표 명시 경계 위의 컴퓨터 보조 증명으로 지지".

### 항목 7. (Hz): 확인. 상수 0.307의 범위는 k≥2000이 맞다

- [r051bfe1]/c-hazard(supported): "모든 k≥2와 N≥k에서 h_k(N) ≥ 1−e^(−δ_N)(1−κ_N/(N+1)) … κ_N≥1/9(모든 k≥2), κ_N≥0.307(k≥2000)".
- [r051bfe1]/c-hazard-implies-published (b)(supported): "모든 N≥k에서 k·h_k(N)+k(1−g(N+1)) ≥ 3/2−47/(24k)+(1−3/(2k))κ_N·k/(N+1)이고, k≥2001, N≤2k−2에서 우변 >1.65이다."
- [rb6a2cd0] §1.3의 (Hz) 표기는 이 둘을 합친 것이다. 그 review도 "(Hz)의 κ_N≥0.307은 원문에서 k≥2000 조건이다"라고 확인했다.

### 항목 10. 2절 행의 진술·지위·검토 지지·상수

2절 36행의 결과는 3절 표에 있다. 세션이 적은 상수를 원문과 글자 그대로 맞대면 다음과 같다.

| 상수 | 원문 | 판정 |
|---|---|---|
| L_*(6668)=1.206 | [rae1f209] §5.1 "L_*(k) := J(k) + J′(k) + Bd(k) + Bd′(k) ≥ L_*(6668) = 1.206"(review 1.20604) | 일치 |
| δ_k≤6.62/√k | "(2) δ_k의 해석적 상계: k ≥ 6668에서 δ_k ≤ 6.62/√k" | 일치 |
| 띠 행 ≤1.0845, 벌크 행 ≤1.0786 | "오른쪽은 k = 6668에서 1.0786 이하이고 띠 행의 요구값은 1.0845 이하다"(review: 정확한 값으로 1.0752) | 일치 |
| LP 0.0056, 블록 3.1·10⁻⁷ | [rb6a2cd0] §4.8 "블록 경계의 최소 여유는 3.1·10^(−7) … 점별 최솟값은 k=6668, ν=103의 F^LP=0.0056" | 수치는 일치. 의존지도의 "최소 여유 0.0056"은 이름이 틀렸다(25행) |
| 2799개 k | "2799개 k 모두에서 실패가 없고"(6668–9466) | 일치 |
| 문턱 9467, 38887 | "K₁⁺=9467", "모든 k≥38887에서 ν₁(k)=103" | 일치 |
| P◇ 1.149357 | [r5909c9e] §3.3 "최솟값은 1.14936 … 40자리 mpmath로 다시 하면 1.149357"; 정리 상수 1.149 | 일치(격자 최솟값) |
| P◇′ 2.274 | §3.4 "최솟값은 2.274이고 θ′ ≈ 0.567"; 정리 상수 2.27 | 일치(격자 최솟값) |
| a≥366, 1−2.3·10⁻⁴ | 보조정리 3 "정수 a는 366 이상", "(1 − 2.3·10^(−4))" | 일치 |
| 50칸, 5200 구간 | "창 [0, 4]를 50개 칸", "[0.48, 1]을 5200개 구간" | 일치 |
| 정리 W 포착 0.729 | [r030ffae] §3.7 "∫_0^6 W(y)√(2y/π)dy ≈ 0.729"; [r5909c9e] §4.3 "창 질량의 0.729" | 일치 |
| 1≤b≤4k^(2/3) | 보조정리 2 "k ≥ 6668, 1 ≤ b ≤ 4k^(2/3)"(정리 W 자체는 ⌊6k^(2/3)⌋) | 일치 |
| ν₁=103 at k≥38887 | 정리 P "또 모든 k≥38887에서 ν₁(k)=103이다" | 일치 |
| c(k)의 50.62(정리 11의 (V)) | [r317d678]/c-vcore-quant "c(k) := 2 − 2·min(1,3c_k·a_k^(−3/2)) − 2g(k) − 50.62/√(k−1)" | 일치 |

3절 행(Q⋆₂ 경로)의 상수는 **검사하지 않음**이다. 1.15, 0.53192, +0.589/+0.505/+0.467/+0.205, 8065/9551/9705가 여기에 든다. 이 파견의 범위가 2절이기 때문이다. 50.62는 2절 (V)의 c(k)에서 맞음을 확인했다.

### 항목 11. 프런티어 현재 판과 의존 기록의 우려·철회

**현재 판: Revision 382**(의존지도는 376 기준). 아래 표에서 "frontier 등장 절"은 그 기록 ID가 관계나 해로 나오는 노드 절이다. "표시"는 그 절들에 concern·withdrawn·retracted·refuted(노드 상태) 표시가 있는지다. "assessment concerns"는 기록의 review 파일 값이다.

| 기록 | frontier 등장 절 | 표시 | assessment concerns |
|---|---|---|---|
| rae1f209 | bvtheta-band, bvtheta-bulk, flat-first-layer-tail, lrp-second-layer, pair-beats-capped-threshold, stem-plus-pair-bulk | 없음 | [] |
| rb6a2cd0 | lrp-second-layer, stem-plus-pair-bulk | 없음 | [] |
| r5909c9e | pair-beats-capped-threshold(해 sol-pair-beats-capped-threshold) | 없음 | [] |
| r4868e30 | (등장 없음: 노드·관계·해 제안이 없는 기록) | 해당 절 없음 | [] |
| r030ffae | bvtheta-band(해), bvtheta-bulk, stem-gain-vs-threshold | 없음 | [] |
| r6f5f48f | first-layer-weighted-tail, left-residual-pole, lrp-from-3k, lrp-second-layer, stem-gain-vs-threshold | 없음 | [] |
| r77e234e | (등장 없음) | 해당 절 없음 | [] |
| r60a6f55 | (등장 없음) | 해당 절 없음 | [] |
| r7e03176 | first-layer-weighted-tail, ul-core, ul-far-window, ul-near-window, ul-small-k-bulk | 없음 | [] |
| r29b01e8 | flat-first-layer-tail, flat-core, lrp-second-layer 등 8절 | 없음 | [] |
| r696d62c | band-criterion-flat, band-criterion-inequality, diagonal-lower-bound 등 | 없음 | [] |
| r05cf8c9 | fs-window, left-residual-reduced, onelevel-attachment, qstar-columns-2001-3130 | 없음 | [] |
| rcb2e2d4 | (등장 없음) | 해당 절 없음 | [] |
| r051bfe1 | onelevel-attachment, tilted-source-tails, tilted-survival-decay | 없음 | [] |
| r33475a7 | head-sum-margin(해 c-hplus), flat-core, lrp-second-layer 등 | 없음 | [] |
| r317d678 | left-residual-reduced, lrp-second-layer, prob-first-layer-tail, source-side, qstar-columns-2001-3130 등 | 없음 | [] |
| r7c26b8b | left-residual-increase, left-residual-reduced, left-moment 등 | 없음 | [] |
| rb6423c6 | left-interior, left-residual-increase | 없음 | [] |
| rce3dc75 | root, central-gap(해), cross-pairs, left-interior, right-interior | 없음 | [] |
| r39ea75d | (등장 없음) | 해당 절 없음 | [] |
| r79ee9e0 | source-side(해 c-src-plus), qstar-columns-from-3131, qstar-second-layer, first-layer-weighted-tail | 없음 | [] |
| r2fe0259 | clock-counting-path | 없음 | [] |
| r7e396da | (등장 없음) | 해당 절 없음 | [] |
| r8456f59 | (등장 없음) | 해당 절 없음 | [] |
| r475ada3 | (등장 없음) | 해당 절 없음 | [] |
| r6b37c7e | (등장 없음) | 해당 절 없음 | [] |
| r15df76b | (등장 없음) | 해당 절 없음 | [] |
| r207f124(추가) | one-step-local, qstar-columns-2001-3130(해), qstar-columns-from-3131 | 없음 | [] |
| r52e9c83(추가) | (등장 없음) | 해당 절 없음 | [] |

지정 노드 절의 상태(판 382)는 이렇다. root, central-gap, right-interior, cross-pairs, left-interior, left-residual-increase, left-residual-reduced, lrp-second-layer, stem-plus-pair-bulk, pair-beats-capped-threshold, bvtheta-band, prob-first-layer-tail, source-side, qstar-columns-2001-3130은 모두 `informal_proved`다. bvtheta-bulk는 `unresolved`다. P◇ 사슬의 관계 다섯은 모두 "supported"이고 전제는 모두 "(established)"다. 다섯 관계는 rae1f209/…-rel-pairnode-band-implies-bplus, rb6a2cd0/…-rel-bplus-implies-lrp2, r317d678/…-rel-v-lrp2-implies-wlflat, r7c26b8b/rel-wlflat-implies-wl·rb6423c6/rel-wl-implies-left-interior·rce3dc75/left-implies-cross-rel, rce3dc75/split-four-position-pairs다.

참고로 root 절의 "Relation r801ec22…/failed-increment-refutes-root, supported: [refuted … critical-egf-increment (open)] implies refuted root"는 조건부 관계 한 줄이다. 철회 표시가 아니며 전제 노드는 open이다.

### 항목 16. 정리 AR의 입력과 [r5909c9e] §5의 사슬 지위

**(가) [rae1f209] §5.1 정리 AR, 글자 그대로**

- 머리: "**정리 AR (해석적 행 정리).** [증명; 공표 정리 B‴·F′·크기 결합·보조정리 F·P 위] 모든 정수 k ≥ 6668과 2k+103 ≤ m ≤ 3k−2에서 L_m ≥ c_mΘ_m, 곧 𝒬_m ≥ 1이다. 따라서 모든 벌크 n(max(2k+103, 20001) ≤ n ≤ 3k−1, n − 2k > 0.48k)에서 BV_n ≥ Θ_n − C(n,k)k^(k−2)A^◇_(n−k)이다."
- (1): "Robbins의 Stirling 부등식으로 Bor(m) = (2π)^(−1/2)m^(−3/2)e^(−ρ_m) …", "생존 비는 (SM)으로 지워지므로", "보조정리 C(수준 방문 보존)의 Abel 판과 정리 F′(용량 k와 k−1, 둘 다 ≥ 4000)를 넣으면", "초등 적분의 구적값이고(`analytic_bounds.out` …)".
- (2): "보조정리 F의 δ_k ≤ max{f_k, max_(1≤a≤k−1) s_(k+a)/(kP₀(k+a))}를 쓴다. 분자에는 정리 F′의 min(1, 3k·a^(−3/2))를 넣는다. 분모 P₀(N) = Σ_(N/2<g≤k)ϖ_N(g) + (1 − π₂(N+1))/(N+1)(공표 무게중심 꼴)은 아래에서 막는다. 둘째 항은 π₂(M) ≤ (8/(πM))^(1/2) ≤ 0.0195로 …. 첫째 항은 Robbins로 …".
- (3): "띠 행(103 ≤ j ≤ 0.48k)에서는 공표 정리 B‴가 BV_m ≥ Θ_m을 준다. 보조정리 V와 합치면 …", "벌크 행 …에서는 귀납 가정 "[2k+103, m−1]의 모든 행에서 𝒬 ≥ 1"과 보조정리 T의 항별 꼴, 그리고 (SM)의 s_(g−1) ≥ s_N으로 …", "Robbins 상계 ϖ_N(g) ≤ … 와 항 수 세기로 …".
- (4): "마지막 주장은 보조정리 T(T = 102)에 이 결과를 넣은 것이다. ∎"
- 맺음: "이 증명에는 정리 W, 한 블록 전파, E_m, 창 행의 거대 블록 착지가 하나도 쓰이지 않는다. 첫 층 생존의 상계는 정리 F′ 한 가지가 두 곳에 들어갈 뿐이다."
- record.json p-analytic-row-theorem의 첫머리: "[증명; 공표 입력 위 — 정리 B‴(컴퓨터 보조), 정리 F′, 크기 결합, 보조정리 F·P]". 의존성: p-landing-minorant, p-delta-bound, p-lemma-V, p-truncated-merge, c-row-identity-B. review의 입력 목록: "공표 입력(정리 B‴은 컴퓨터 보조, 정리 F′, 크기 결합, 보조정리 F·P, 무게중심 꼴, (OB))".

**(나) [r5909c9e] §5, 글자 그대로**

- "1. **(P◇) ∧ bvtheta-band ⇒ B⁺** (rae1f20952…/sbc38cd5566204ef29cb705f612bd6e97-rel-pairnode-band-implies-bplus; 증명 p-pair-node-relation). bvtheta-band는 확립(r030, 정리 B‴; 컴퓨터 보조). 증명은 정리 AR의 BV_n ≥ Θ_n − C(n,k)k^(k−2)A^◇_N(해석적; 정리 B‴·F′·크기 결합 위)에 (P◇)를 더한 것이다. 그 review의 단서: 정리 AR의 띠 행은 6668 ≤ k ≤ 9948에서 노드 bvtheta-band의 범위(n ≥ 20001) 밖의 행까지 r030/theorem-B-triple 자체를 쓴다. …"
- "2. **B⁺ ⇒ LRP₂** (rb6a2cd0e6d434a8eb512088619fe9be7/s6fd65c6e63714bdeb8a19d6230b440f7-rel-bplus-implies-lrp2; 증명 c-rel-bplus-lrp2, 판 341). LRP₂의 위치는 n ≤ 20000(공표 유한 인증), 중앙 띠 n − 2k ≤ 102(공표 띠 정리), 띠 103 ≤ n − 2k ≤ ⌊0.48k⌋(그 기록의 정리 P⁺⁺; 6668 ≤ k ≤ 38886은 닫힌 꼴 부등식의 binary64 확인), 벌크(B⁺와 다섯 조각 항등식)로 덮인다. …"
- "3. **LRP₂ ⇒ W_L♭** (r317d6781…/s5a4a7531a2d8409f8720f0e0511e8320-rel-v-lrp2-implies-wlflat; 다른 세 전제 (V)·source-side·qstar-columns-2001-3130은 확립). …"
- "4. **W_L♭ ⇒ W_L ⇒ left-interior ⇒ cross-pairs**(r7c26b8b9…/rel-wlflat-implies-wl, rb6423c6…/rel-wl-implies-left-interior, rce3dc75…/left-implies-cross-rel), 그리고 네 위치쌍 분할 central-gap ∧ right-interior ∧ cross-pairs ∧ left-interior ⇒ root(rce3dc75…/split-four-position-pairs; 앞의 둘은 확립)."
- 지위 문단: "그러므로 (P◇)의 해가 받아들여지면 frontier는 생산자의 절 1(W_L♭)과 root를 비형식으로 증명된 상태로 적는다. 이 결론은 사슬의 모든 고리가 기대는 공표 입력의 지위를 그대로 물려받는다. 그 가운데 컴퓨터 보조 부분은 정리 W·정리 B‴(r030; binary64 인증), 정리 P⁺⁺의 유한 확인(rb6a2cd0e), n ≤ 20000의 정수 인증, H*₊(r33475a7c) 등이다. review들이 각 기록에서 재실행하거나 독립 재구현해 지지했다. 이 기록이 더한 컴퓨터 몫은 §3.3의 한 변수 확인 하나다."

**(다) 2절 행과의 대응**

| 원문 항목 | 2절의 행 | 대응 |
|---|---|---|
| AR: 정리 B‴ | 7.2 정리 AR 입력 | 있음 |
| AR: 정리 F′ | 7.2 정리 AR 입력 | 있음 |
| AR: 크기 결합 (SM)·(DM0) | 7.2 입력, 2.8 | 있음 |
| AR: 보조정리 F·P | 7.2 입력(13행에서 lemma-P 확정) | 있음 |
| AR: Robbins | 7.2 입력 | 있음 |
| AR: 보조정리 C의 Abel 판 | 7.2 입력, 2.8 | 있음 |
| AR: 무게중심 꼴(P₀) | 7.2 입력, 7.1 보조정리 1 비고 | 있음 |
| AR: L_*(6668) 구적 | 7.2 입력 | 있음 |
| AR: **보조정리 V** | 7.2 보조정리 V 행은 있으나 AR 입력에 없음 | **빠짐**(AR 입력 열에) |
| AR: **보조정리 T** | 7.1 보조정리 T 행은 있으나 AR 입력에 없음 | **빠짐**(AR 입력 열에) |
| AR: (OB)/명제 B(record.json 의존성, review 목록) | 7.2 명제 B 행 | **빠짐**(AR 입력 열에) |
| AR: π₂(M) ≤ (8/(πM))^(1/2) | 없음 | **빠짐**(초등, 출처 기록 없음) |
| §5-1: (P◇)∧bvtheta-band⇒B⁺, p-pair-node-relation | 7.5 "P◇∧띠⇒B⁺" | 있음. 주장 ID와 band 전제·단서가 빠졌다(32행) |
| §5-1: bvtheta-band(정리 B‴) | 2절에 행 없음(몸통 기존 정리 6.23로 보임) | 2절 밖. 1절에서 확인할 것 |
| §5-2: B⁺⇒LRP₂, c-rel-bplus-lrp2 | 7.5 정리 Q | 있음 |
| §5-2: n≤20000 인증, 중앙 띠 정리, P⁺⁺, 다섯 조각 | 7.5 정리 Q 입력, 7.3 P⁺⁺, 2.10 | 있음 |
| §5-3: LRP₂⇒W_L♭와 (V)·source-side·qstar-columns-2001-3130 | 7.5 셋째 행 | 있음 |
| §5-4: W_L♭⇒W_L⇒left-interior⇒cross-pairs, 네 위치쌍 | 7.5 넷째 행 | 있음. 관계 ID, 전제 central-gap·right-interior가 빠졌다(34행) |
| 지위: 정리 W | 7.4 보조정리 1–3 입력 | 있음. P◇′ 행에는 빠짐(30행) |
| 지위: 정리 B‴ | 7.2 AR 입력 | 있음 |
| 지위: P⁺⁺ 유한 확인 | 7.3 P⁺⁺ 지위 | 있음. 정리 Q 지위에는 반영되지 않음(31행) |
| 지위: n≤20000 정수 인증 | 7.3 P′⁺⁺, 7.5 정리 Q 입력 | 있음 |
| 지위: H*₊ | 7.3 정리 10 입력 | 있음. 지위 표지에 구간 산술이 반영되지 않음(20행) |
| 지위: §3.3의 한 변수 확인 | 7.4 정리 P◇ 지위 | 있음 |

세션이 빠뜨린 입력: 정리 AR 입력 열에 보조정리 V, 보조정리 T, (OB)/명제 B, π₂ 초등 경계. P◇∧띠⇒B⁺ 행에 정리 AR과 bvtheta-band(B‴). 정리 P◇′ 행에 정리 W. 마지막 고리 행에 전제 노드 central-gap·right-interior.

---

## 5. 정정 제안 목록(의존지도 2절)

| 행(새 글의 자리 / 진술 앞부분) | 열 | 바꿀 문구 |
|---|---|---|
| 2.8 / 크기 결합 | 입력 | "[r60a6f55]/size-coupling(문헌 Fleurat 위; 결합 Mtilde_n≤Mtilde_(n+1)≤Mtilde_n+1), 재진술 [r207f124]/diag-lossless((SM)·(DM0)), 두 부등식의 초등 증명 [r79ee9e0]/c-lemma-sh" |
| 2.8 / 크기 결합 | 지위 | "(SM)·(DM0): 증명([r79ee9e0]/c-lemma-sh); 결합(0 또는 1 증가): 비형식(문헌)" |
| 2.8 / 보조정리 C | 입력 | "[rae1f209] §3.3 보조정리 C(p-visit-conservation); 입력 (DM0)=[r207f124]/diag-lossless(크기 결합의 둘째 단조성)" |
| 2.8 / 보조정리 C | 비고 | 덧붙일 문구: "검토의 귀속 정정: 무게 없는 꼴은 [re597c0e]/c-sojourn-identity에서 머묾 항을 버린 것이고, 새 몫은 Abel 판과 정리 F′의 결합" |
| 2.9 / 정리 T | 입력 | "[r4868e30] §3.3–3.4(c-threshold-subtree, c-inner-head-sum); 입력: 숲 표현(2.4), Cayley 공식, Stirling, [r33475a7]/p-heavy-path-ratio((iii)), [r2ec875c]/c-psi-correction((d)의 Ψ(J)≤0.7979√J)" |
| 2.9 / 정리 T | 비고 | "(i)의 점별 부호와 (ii)의 첫 층 판은 [r52e9c83] 보조정리 4·5(c-lemma4-chain, c-lemma5-neg-bound)와 같음" |
| 7.1 / 병합 항등식 | 입력 | "[r6f5f48f]/pr-merge-identity(2k+2≤n≤3k−1); BV_n=ΣK_n(m)L_m은 BV의 정의" |
| 7.1 / 병합 항등식 | 비고 | "대조 항목 4-1" 대신 "4-1 확인(판 382, supported)" |
| 7.1 / 정리 A | 입력 | "[rae1f209] §2.2 정리 A(c-reduction-theorem-A); 입력 병합 항등식([r6f5f48f]/pr-merge-identity)" |
| 7.2 / 명제 B | 입력 | "[rae1f209] §3.1(c-row-identity-B); 입력 (OB)=[r77e234e]/ob-identity" |
| 7.2 / 보조정리 V | 입력 | "[rae1f209] §3.2(p-lemma-V); 입력 보조정리 P=[r77e234e]/lemma-P(M₂≤(δ_k/2)V_m)" |
| 7.2 / 명제 R | 입력 | "[rae1f209] §3.2(p-row-criterion); 입력 보조정리 V, 정리 A, 보조정리 1, 명제 B, Θ°/Θ≤1−W₀′([r77e234e]/p-theta-circ-kernel-bound), (SM)" |
| 7.2 / 정리 AR | 입력 | 기존 목록 뒤에 덧붙일 문구: "보조정리 V(p-lemma-V), 보조정리 T(p-truncated-merge), 명제 B/(OB)(c-row-identity-B), π₂(M)≤(8/(πM))^(1/2)(초등); 주장 p-analytic-row-theorem·p-landing-minorant·p-delta-bound" |
| 7.3 / 두 나무 꼴 | 진술 | "$\mathcal T_n(s)=n!e^{n+1}\mathrm{Bor}(s)\mathrm{Bor}(n+1-s)s_{n-s}(k)$"([rb6a2cd0]의 ϖ_n은 새 원고 𝒯_n) |
| 7.3 / 정리 10 | 지위 | "증명(공표 입력 위; (H*₊)는 구간 산술 인증, (Υ)는 p-row-averaging-e3를 거쳐 n≤20000 인증·right-bulk-increase에 기댐)" |
| 7.3 / 정리 11 | 입력 | 덧붙일 문구: "정리 L(c-weight-monotone), 정리 10(c-flat-tails)" |
| 7.3 / 정리 11 | 지위 | "증명(공표 입력 위; (V)=c-vcore-quant는 비형식, 정리 10을 거쳐 H*₊ 구간 산술)" |
| 7.3 / 보조정리 4.1, 따름정리 12·13 | 입력 | "[rb6a2cd0] §4.1–4.2(c-x-shape, c-cor12, c-cor13); 입력 정리 11, (V), 정리 L; 따름정리 12는 [r030ffae]/band-node" |
| 7.3 / 보조정리 4.1, 따름정리 12·13 | 지위 | "증명(공표 입력 위; 보조정리 4.1의 경계값은 binary64·50자리 mpmath)" |
| 7.3 / 정리 P | 입력 | "[rb6a2cd0] §4.5(c-band-thmP); 입력 정리 11, 보조정리 R, 보조정리 4.1, (B′)·(B‴)" |
| 7.3 / 정리 P | 지위 | "증명(공표 입력 위; 38887≤k≤48965는 닫힌 꼴 F_k(103)의 k별 계산, binary64·50자리 mpmath)" |
| 7.3 / 보조정리 C, 정리 11′, 정리 P⁺ | 입력 | "[rb6a2cd0] §4.7(c-tail-cap, c-fl-lower-loc, c-band-thmP-plus); 입력 정리 T 따름 (a)([r4868e30]/c-inner-head-sum), (B′), 보조정리 R, (V), (Hz), 정리 P" |
| 7.3 / 보조정리 C, 정리 11′, 정리 P⁺ | 지위 | "보조정리 C·정리 11′: 증명(공표 입력 위); 정리 P⁺: 비형식(9467≤k≤38886 binary64 블록 확인, 구간 산술 아님, 최소 여유 4.6·10⁻⁹, 경계 k 30자리 mpmath)" |
| 7.3 / 정리 11″, 정리 P⁺⁺ | 입력 | 덧붙일 문구: "보조정리 R, 보조정리 C(꼬리 상한), 정리 10, 정리 P·P⁺" |
| 7.3 / 정리 11″, 정리 P⁺⁺ | 비고 | "점별 최솟값 F^LP=0.0056(k=6668, ν=103), 블록 경계 최소 여유 3.1·10⁻⁷" |
| 7.4 / 보조정리 7–8, 정리 P◇ | 비고 | "정리의 상수 1.149(격자 최솟값 1.14936, 40자리 1.149357)" |
| 7.4 / 정리 P◇′ | 입력 | "[r5909c9e] §3.4(c-pdiamond-giant-bound); 입력 정리 W([r030ffae]/theorem-W), 한 블록 꼴(c-pair-marginal-identity), 보조정리 4–6, heavy path 점화식([r39ea75d]/heavy-path-recurrence), 크기 단조성([r79ee9e0]/c-lemma-sh)" |
| 7.4 / 정리 P◇′ | 비고 | "정리의 상수 2.27(격자 최솟값 2.274)" |
| 7.5 / 정리 Q | 입력 | 덧붙일 문구: "c-bplus-bulk, [rae1f209]/c-pair-explicit" |
| 7.5 / 정리 Q | 지위 | "비형식(입력 P⁺⁺의 binary64 유한 확인, n≤20000 인증, 중앙 띠의 컴퓨터 보조 정리를 물려받음)" |
| 7.5 / P◇∧띠⇒B⁺ | 입력 | "[rae1f209]/p-pair-node-relation(관계 sbc38cd…-rel-pairnode-band-implies-bplus); 입력 정리 AR(p-analytic-row-theorem), 노드 bvtheta-band([r030ffae]/band-node=B‴)" |
| 7.5 / P◇∧띠⇒B⁺ | 지위 | "증명(공표 입력 위; 정리 AR·B‴, B‴는 컴퓨터 보조)" |
| 7.5 / P◇∧띠⇒B⁺ | 비고 | "검토 단서: AR의 띠 행은 6668≤k≤9948에서 band 노드 범위 밖 행 m<20001까지 theorem-B-triple 자체를 씀. B‴ 철회 시 재검토" |
| 7.5 / LRP₂⇒W_L♭ | 입력 | "[r317d678]/c-rel-v-lrp2-wlflat(관계 s5a4a753…-rel-v-lrp2-implies-wlflat); 입력 V, source-side, Q⋆(2001–3130)" |
| 7.5 / W_L♭⇒…⇒뿌리 | 입력 | "[r7c26b8b]/rel-claim-wlflat-implies-wl, [rb6423c6]/wl-implies-left-interior, [rce3dc75]/left-implies-cross, [rce3dc75]/four-part-cover(관계 split-four-position-pairs); 전제 central-gap·right-interior(established)" |
| 7.5 / W_L♭⇒…⇒뿌리 | 지위 | "증명(공표 입력 위; wl-implies-left-interior는 공표 비형식 정리 사용)" |
| 3절 8.7 / "프런티어 판 376" | 입력 | 이 파견의 범위 밖이다. 현재 판은 382이므로 마무리 전 재확인을 권한다 |

장부(의존지도 밖)에 대한 제안:
- `장부_기호용어이름.md` 2.7의 W₀′ 행: 7.4에서는 g≥k+104의 양([r5909c9e] §3.4, [rae1f209] §5.1의 W₀″)으로 고친다. 또는 7.1–7.2의 W₀′(g≥k+2)와 다른 글자를 둔다.
- 같은 2.7의 "Ψ^{low}(ξ)": Ψ^low(b)(정수 b 또는 실수 x의 b 단위 함수)로 고친다.
- 1.2에 [r4868e30]의 c_N(κ)(나무 개수 min(N,κ)A_(N−1,κ−1))와 c_0:=1 규약을 넣는다.

---

## 6. 미확인·읽지 못한 것

- **미확인 행: 없음.** 2절 36행 모두 기록 원문으로 판정했다.
- **ID·진술만 확인한 기록 22개**는 파견문의 "해설 문단"을 열지 않았다. record.json의 진술 전문과 review 사유로 대신했다. 해당 기록은 r6f5f48f, r77e234e, r60a6f55, r7e03176, r29b01e8, r696d62c, r05cf8c9, rcb2e2d4, r051bfe1, r33475a7, r317d678, r7c26b8b, rb6423c6, rce3dc75, r39ea75d, r79ee9e0, r2fe0259, r7e396da, r8456f59, r475ada3, r6b37c7e, r15df76b다. 지정 주장의 실재와 진술은 모두 확인했다. 두 가지는 주장 ID가 아니다: rce3dc75의 "split-four-position-pairs"는 관계 ID이고 주장은 four-part-cover, r79ee9e0의 "sol-source-side"는 해 ID이고 주장은 c-src-plus다.
- **[r030ffae] 안 읽은 절**: §3.2–3.6(78–164행), §4′의 231–254행, §4″.1(269–300행). 정리 W·B′·B‴·(E1)·lemma-cap-shift의 진술은 §3.1, §3.7, §4, §4″.5와 record.json에서 확인했다.
- **[rb6a2cd0]·[r5909c9e]의 feedback.md**는 앞부분과 사슬 절만 읽었다(각 40행, 47행). 주장별 판정은 assessment.json 전부로 확인했다.
- **검사하지 않음**: 3절(Q⋆₂ 경로)의 행과 상수, 4절 항목 8, 9, 12–15. 다른 파견의 범위다.
- 임시 파일은 `C:\math\임시\주차함수_증명\대조\_tmp_P\`에 남겼다(claims.py, front.py: 읽기 전용 추출 스크립트).
