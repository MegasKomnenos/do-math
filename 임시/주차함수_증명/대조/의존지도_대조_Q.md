# 의존 지도 대조 보고서 Q: 3절(Q⋆₂ 경로)과 4절 항목 8·9·10·11·13·14·15

작성 2026-11-12. 대상은 `C:\math\임시\주차함수_증명\의존지도.md`의 3절 전 행(26행)과 4절 항목 8, 9, 10, 11, 13, 14, 15다. 대조 원본은 인스턴스 `parking-unimodality-fresh-20261105-150803/knowledge`(아래 K)의 기록, 검토 판정, 프런티어(현재 판 382), 용어집이다. 기호 차이는 `장부_기호용어이름.md` 1.1절 변환표를 적용한 뒤 내용을 비교했다. 기록의 수학을 다시 증명하지 않았다.

판정 분포: 26행 가운데 `일치` 22, `정정` 4, `미확인` 0.

---

## 1. 중대 사항

### 1.1 검토가 지지하지 않은 입력

없음. 3절이 입력으로 적은 주장과, 기록이 실제로 쓰는데 3절에서 빠진 주장을 모두 검토 판정과 대조했다. 모두 `supported`다. 같은 기록 안의 비지지 주장은 다음과 같고, 3절은 이 가운데 어느 것도 쓰지 않는다.
- r845b205: c-small-deficit, p-Bk, p-rel-tilt-core, p-v-proof
- r39ea75d: apriori-bound, row-float-check
- r3172894: prop6-conditional-structure
- r79ee9e0: c-thmF-U(undetermined)

### 1.2 철회·우려

없음. 근거는 셋이다.
- 프런티어 판 382 전문에서 concern·철회·반박 표시를 찾았으나, 해당 노드 절에는 하나도 없다. 프런티어의 관계 305개는 모두 `supported`다.
- 위 3의 16개 기록 모두 `review/assessment.json`의 `concerns`가 빈 목록이다.
- 판 376 뒤에 공표된 기록 여섯(sequence 377–382: r84781b3, re5b2434, r701db1c, re34a705, rbe3f3fa, r8ac6bda)은 노드·관계·해를 하나도 등록하지 않았다. 그 가운데 re34a705는 re71a735의 정리 S′(p-thmSprime)와 보조정리 J(c-lemmaJ)를 "증명"으로 인용하며, 정정하지 않았다.

### 1.3 기록 사이의 어긋남과 검토 정정

1. **상수 50.62의 출처.** 세 기록에 같은 상수가 서로 다르게 적혀 있다.
   - r845b205/p-thmU(정리 U)의 진술은 "Σ[(Θ¹_d)″(t)]^+ ≤ 50.6/√t"이고, 기록 본문의 위합은 50.60이다.
   - 같은 기록의 검토는 "검토자 위합 C≤50.620"이라 적었다.
   - r317d678/c-vcore-quant는 "C_U는 r845b2055 검토의 위합 C_U≤50.620으로 잡는다"고 적었다.
   - r3d0856b 명제 T 증명 (3)은 "p-tv-proof와 r317 (2.5)의 상수 C_U = 50.62"라 적었다.
   - r845b205/p-tv-proof의 진술에는 50.62가 없고 "≤0.905<1"만 있다.

   50.62는 검토가 지지한 더 안전한 값이다(50.62 ≥ 50.60). 그러나 3절 8.4행이 50.62를 "[r845b205]/p-split, p-tv-proof"에 귀속한 것은 틀렸다. 정정은 5절 (가)에 있다.
2. **re71a735 정리 P의 ε(검토 정정).** 해설 §3.6은 "ε의 확률을 조건부로 읽든 결합 확률로 읽든 같은 값"이라 적었다. 검토(p-thmP)는 이렇게 판정했다. "조건부로 읽으면 52개가 어긋난다. … 쓰인 곳은 모두 결합 읽기라 결론에는 영향이 없다." 8장이 정리 P를 옮길 때는 결합 읽기로 적어야 한다.
3. **re71a735 생산자 CF의 비단조 예(검토 정정).** 해설의 예 "CF(6675) > CF(6668)"은 틀렸다. 검토에 따르면 실제 오름은 CF(6674)=0.143725에서 CF(6675)=0.143787이다. 증명은 CF가 아니라 CF♮를 쓰므로 결론에는 영향이 없다. `연구_파악.md` 2.3절은 이미 바른 예를 적었다.
4. **re71a735 §4.6의 오기(검토 정정).** m₀ > a 손실 R′의 "CF"는 "CF♮"이어야 한다. 표의 값 1.8146과 1.7703은 CF♮로 계산되었다.
5. **r3d0856b §5.5의 표기(검토 정정).** m₀−k = 300, 600 행은 명제 S(가)가 아니라 (나)의 꼴이다. 표 값은 맞다.

### 1.4 변환표(장부 1.1절)의 어긋남

없음. r3d0856b과 re71a735에 관계된 1.1절 행 13개를 기록의 정의에 대입해 검산했다. 첨자는 모두 맞는다. 검산 결과는 다음과 같다.
- **r3d0856b의 기본 양.** F_m(ℓ)=Pr_m(M≤ℓ)→s_m(ℓ+1), π_m(ℓ)→c_m(ℓ), s_m=π_m(k)+π_m(k−1)→c^(2)_m, Δπ_m→d_(m,k)/p_m.
- **r3d0856b의 머묾.** σ_n(ℓ)=F_(n+1)(ℓ+1)−F_n(ℓ)→σ_n(ℓ+1). 이 행은 r3d0856b §1이 적은 대응 "σ_(c+d−1)(c−1)=W_c(d)"(r98fb348의 W)와도 맞는다.
- **re71a735의 d-좌표 양.** s_d(y)→𝔰_d(y)=s_(y+d−1)(y), W_c(d)=s_d(c+1)−s_d(c)→σ_(c+d−1)(c)=s_(c+d)(c+1)−s_(c+d−1)(c), V_c(d)=π_(c+d)(c)→c_(c+d)(c), Δ_ds(c)→𝔰_d(c)−𝔰_(d+1)(c).
- **re71a735의 대각선 둘째 차분.** DD_m=(k+1)s_d(k+1)−2ks_d(k)+(k−1)s_d(k−1), d=m−k+1 → DD(m−1,k−1)=(k+1)s_(m+1)(k+1)−2ks_m(k)+(k−1)s_(m−1)(k−1).
- **머묾의 전역 정의.** 새 정의 σ_m(ℓ)=s_(m+1)(ℓ+1)−s_m(ℓ)은 용어집 '크기 성장 확률'의 머묾 질량 σ_n(k)=(1−θ_n(k))p_n(k)와 같다.

누락은 하나 있다(어긋남은 아님). r3d0856b 명제 S와 re71a735 §2가 쓰는 W^(ℓ)_n := F_n(ℓ) − F_(n−1)(ℓ−1)(F는 Pr(M≤ℓ) 규약)의 행이 없다. 변환은 W^(ℓ)_n = s_n(ℓ+1) − s_(n−1)(ℓ) = σ_(n−1)(ℓ)이다. Stays와 Bd가 이 기호로 정의되므로 8.2절 집필 전에 1.1절에 넣기를 권한다(5절 (사)).

---

## 2. 읽은 범위

**설계 쪽 파일**
- `의존지도.md`: 전문 104줄.
- `장부_기호용어이름.md`: 15–110행(1.1–1.3절), 252–270행(2.8절).
- `연구_파악.md`: 27–48행(2.1절), 93–123행(2.3–2.5절), 209–232행(8.2–8.3절).
- 파견문 전문.

**전문을 읽은 기록**
- r3d0856b811f14f8c8d71335597036243: `exposition.md` 579줄 전부, `record.json` 주장 25개 전부(진술 전문 9개: p-budget-identity, p-decomposition, p-tail-pivot, q-node-range, q-sojourn-form, q-flq-relation, q-t-route, q-window-survival, p-weights; 나머지 16개는 ID와 판정), 노드 1개, 관계 1개. `review/assessment.json`은 주장 25개 판정 전부와 reason·index_assessment. `review/feedback.md`는 §7–§9(정정과 단서).
- re71a735a86714433829f386919576084: `exposition.md` 472줄 전부, `record.json` 주장 31개 가운데 진술 전문 26개(p-frozen-split, p-thmA, p-thmB, p-lemma3, p-thmC, p-propM, c-lemmaN, c-propM-complete, p-lemmaSS, p-thmSprime, p-propX, p-propD, p-thmP, p-lemmaF, c-checks, c-lemmaB, c-lemmaJ, c-lemmaR, c-propU, c-propL, c-na, c-ga, c-flq, c-route, c-first-order-survival와 해 sol-flq), 의존 목록 전체(기록 밖 의존 14개). `review/assessment.json`은 판정 31개와 reason·index_assessment·solutions·concerns. `review/feedback.md`는 §0, §3의 S′ 문단, §4의 CF 문단, §6–§8.

**지정 절을 읽은 기록**
- r317d67810d1240bc9b19b5e9dd44eead: §1(17–45행), 제2부 §5–§8(160–321행), 제3부 §9–§11(322–418행), §2 걸음 4의 해당 줄. 주장 c-ledger, c-thmR, c-thmQ2, c-row3k, c-vcore-quant, c-vcore, c-bk-bound(진술과 판정).
- rb1d8cd535d9f4a9da52ab599dbc201a9: §1.2(53–71행), §3.2(103–131행). 주장 c-chain-representation, c-walk-comparison, 해 sol-flat-core. 용어집 항목 borel-renewal-area와 승인 여부.
- r845b2055d18c40c6894cca76b1dff184: §1(23–39행), §2.1(40–55행), §2.3(64–73행), §3(98–123행), §5(139–152행). 주장 c-sojourn, c-fixed-chain-convexity, p-split, p-thmU, p-tv-proof, p-rel-core-v와 관계 rel-core-implies-v.

**주장 ID와 진술만 확인한 기록(판정 포함)**
- r98fb348: c-thmS, c-propN
- r7e03176: p-bulk-point-mass, p-row-averaging-e3, p-thmF-prime
- r39ea75d: heavy-path-recurrence
- r051bfe1: c-sharp
- raad7e6d: p-ladder, p-rel-qstar, 관계 rel-v-implies-vstar, rel-vstar-implies-qstar
- r207f124: qstar-split-cover, qstar-finite-range, 관계 rel-qstar-column-split, 해 sol-qstar-columns-2001-3130
- r3172894: rel-qstar-wlflat, 관계 rel-qstar-implies-wlflat
- r79ee9e0: c-src, c-src-plus, 해 sol-source-side
- r60a6f55: size-coupling
- r030ffae: band-node, theorem-B-triple, §1(24–45행, (G1)(G2))
- r6a8c8b6: 용어집 항목 borel-renewal-set
- 추가(의존 추적): r8a9b11e/peer-theorem-W
- 위 16개 기록 모두에서 주장 ID 목록과 판정, concerns를 읽었다.

**프런티어(K/frontier.md, 1463줄)**
- 머리(Revision: 382)와 절 머리 목록.
- 지정 절 11개 전문: qstar2-first-layer-tail, qstar-second-layer, qstar-columns-from-3131, qstar-columns-2001-3130, one-step-local, source-side, prob-first-layer-tail, critical-tilt-first-layer-tail, left-residual-reduced, bvtheta-band, flat-core.
- 추가로 읽은 절: first-layer-weighted-tail, flat-first-layer-tail, prob-first-layer-core, bvtheta-bulk 전문. ul-near-window, ul-far-window, ul-small-k-bulk, lrp-second-layer, left-residual-increase, left-interior, cross-pairs, root는 State와 관계 줄만.
- 전문 grep: concern, retract, withdraw, 철회, 우려, refut, flag 등.

**용어집(K/glossary.md)**: 지정 8항목 전문(최대 나무 사슬, 첫 층 크기 편향 꼬리합, 블록 원천, Borel 갱신 집합, Borel 갱신 면적, 갱신 방문 핵, 제한 성장비, 크기 성장 확률).

**그 밖**
- K/events: sequence 374–382 목록. 판 376 뒤 기록 여섯의 노드·관계·해와 위 16개 기록에 대한 언급.
- 기존 원고 `C:\math\임시\주차함수_해설\원고.md`: 정리 2.13(250–275행), 정리 6.20(1446–1456행), 명제 6.14·6.16·6.17과 정리 6.18의 머리 줄.

---

## 3. 행별 판정 표

표기: "기록"은 K/records의 해당 기록이다. "보충"은 판정을 바꾸지 않는 권고이고, 5절 (아)에 모았다.

| # | 새 글의 자리 | 행(요지) | 판정 | 근거와 메모 |
|---|---|---|---|---|
| 1 | 2.5 | 무거운 사슬 공식 Pr_N(M≤y−1)=E∏_(S_i>y)(y/S_i) (N≤2y+1) | 일치 | 진술: r39ea75d/heavy-path-recurrence "y=ℓ+1, N≤2y+1에서 Pr_N(M≤y−1)=… 이는 최대 나무 사슬 S_i에 대한 E∏_(S_i>y)(y/S_i)와 같다"와 같다. 판정 supported("증명(정확한 항등식)"). 용어집 '최대 나무 사슬'(1≤N≤2y+1)과도 같다. 4-8 참조. |
| 2 | 2.11 | Borel 갱신 집합 H_B(r), 갱신 항등식 (G1)(G2) | 일치 | H_B는 용어집 borel-renewal-set(출처 r6a8c8b6, 기록 glossary 승인)의 정의 그대로다. (G1)(G2)는 r030ffae §1에 생성함수 증명과 함께 있다(주장 ID 없음, 본문 인용). 지위 "증명"은 정의와 본문 항등식에 대해 맞다. re71a735는 H_B를 쓰지 않는다(그 기록이 쓰는 것은 u(j)=jBor(j)). |
| 3 | 2.11 | 보조정리 B(갱신 다리) | 일치 | re71a735 §4.2, 주장 c-lemmaB, supported("증명으로 지지"). 범위는 δ≤y+2, 1≤b<c<δ. 보충: 주장 ID c-lemmaB를 적는다. |
| 4 | 2.11(조건부) | rb1d8cd5 명제 1(무거운 사슬 표현·Poisson 보행 표현), 𝔄_D | 일치 | 내용은 rb1d8cd5 §3.2 명제 1(c-chain-representation, supported)과 §1.2, 용어집 borel-renewal-area(승인)와 같다. 그러나 이 행의 조건("re71a735 §4.8이 쓰는 경우에만")은 성립하지 않는다(4-13·4-14: 쓰지 않음). 5절 (마)에서 행 삭제를 제안한다. |
| 5 | 8.1 | 노드 Q⋆₂의 진술, 정리 R A_t[src+FL]=d_(t,k)−KD′_t | 일치 | 노드 진술(r3d0856b §0.1)은 프런티어 qstar-second-layer 절과 글자 그대로 같다(k≥6667, max(2k+103,20001)≤t≤3k). 정리 R은 r317d678/c-thmR "정수 k≥2와 2k+1≤t≤3k에서 A_(t,k−1)·[src_k(t)+FL_k(t)]=d_(t,k)−KD′_t", supported. 기존 정리 6.20(원고 1448행)과 같다. 보충: 범위 2k+1≤t≤3k와 c-thmR. |
| 6 | 8.1 | 보조정리 1(장부) = r317/c-ledger | 일치 | r3d0856b §2.1 "보조정리 1 (장부; r317/c-ledger)". c-ledger는 supported이고 범위는 2k+1≤t≤3k다. |
| 7 | 8.1 | 보조정리 2(분할 무게); 입력 c-sharp | 일치 | r3d0856b §2.2, 주장 p-weights "[증명; 공표 c-sharp 위]", supported. c-sharp "모든 k≥2와 N≥0에서 … ≤((k+1)/k)^(k−1)"은 행의 괄호와 같다. 보충: 기록 의존 목록에는 r317/c-thmQ2(같은 단조성 논증)도 있다. |
| 8 | 8.1 | 보조정리 3(문턱 예산 Λ_ν) | 일치 | r3d0856b §2.3, p-budget-identity, supported("증명으로 지지"). 범위 k≥2, 1≤ν≤k. |
| 9 | 8.1 | 명제 4, 6, 5 | 일치 | r3d0856b §2.4–2.5, p-decomposition(c-ledger 위)과 p-tail-pivot, 둘 다 supported. |
| 10 | 8.2 | 명제 S (가)(나)(다); 입력 c-sojourn; 증명(대수 항등식); 273개 경우 | 일치 | r3d0856b §3.5, q-sojourn-form, supported("대수 항등식(증명)으로 지지"). "3 ≤ k ≤ 9, 1 ≤ ν ≤ k−1, k ≤ m₀ ≤ 2k의 273개 경우 모두에서 (가)(나)를, 같은 범위에서 (다)를 정확 유리수로 확인"(정확 산술). (다)가 c-sojourn을 쓴다. 보충: 범위 k≥3, 1≤ν≤k−1(곧 t<3k). 기록 의존 목록에는 r98fb348/c-propN(DD_m=(k+1)W−(k−1)W의 동일시), r60a6f55/size-coupling(머묾 ≥0의 해석)도 있다. |
| 11 | 8.3 | 노드 FLQ, 관계 FLQ∧띠⇒Q⋆₂; 입력 c-ledger, c-thmQ2, c-sharp, band-node | 일치 | r3d0856b §5.1, q-flq-relation, supported("증명으로 지지"). 네 입력은 기록이 "쓰는 입력은 공표 지지 주장 r317/c-ledger, r317/c-thmQ2, r051bfe18/c-sharp와 노드 bvtheta-band(r030ffae/band-node로 확립)"라 적은 그대로다. 노드 진술은 프런티어 qstar2-first-layer-tail 절과 같다. 보충: 주장문의 "t=3k에서 FLQ는 (V)와 r317 정리 T로 성립"은 r317/c-row3k에 기댄다. band-node는 theorem-B-triple(컴퓨터 보조, binary64 상자 검사) 위에 있다. |
| 12 | 8.4 | 명제 T; 입력 정리 F′, 따름정리 E, 정리 S·U(p-split, p-tv-proof, 상수 50.62), c-thmS, 크기 결합, 무거운 경로 재귀 | **정정** | 지위 "증명(공표 입력 위)"는 q-t-route의 판정("공표 입력 위의 증명으로 지지")과 맞는다. 입력 열에는 두 문제가 있다. (i) 50.62의 귀속이 틀렸다. p-tv-proof의 진술은 "≤0.905<1"이다. 50.62는 r845b205 검토의 위합이고 [r317d678]/c-vcore-quant (2.5)가 채택했다. 기록 §5.4 (3)의 문장은 "p-tv-proof와 r317 (2.5)의 상수 C_U = 50.62"다. (ii) 기록 의존 목록에 있는데 3절 어디에도 없는 입력이 있다. [r317d678]/c-vcore-quant(상수, 그리고 증명 (2)의 "r317 §2 걸음 4(다)", 곧 c-bk-bound)와 [r317d678]/c-row3k(증명 (4)(5)의 "r317 정리 T 걸음 3" τ 논증)다. 정리 F′의 ID [r7e03176]/p-thmF-prime도 빠졌다. 범위 k≥6667, max(2k+103,20001)≤t<3k도 적는다. 5절 (가). |
| 13 | 8.4 | 명제 W(창의 생존 상계) | 일치 | r3d0856b §5.4, q-window-survival, supported("증명으로 지지"). 범위 y≥1, y≤N≤2y+1. 보충: 기록의 주장문은 "[공표 입력 위의 증명]"이고, 입력은 [r39ea75d]/heavy-path-recurrence(3절 2.5행)다. |
| 14 | 8.5 | 보조정리 1(h-변환), 보조정리 2(=c-fixed-chain-convexity), 정리 A | 일치 | re71a735 §3.1, p-frozen-split(의존 heavy-path-recurrence, r845b205/c-fixed-chain-convexity)과 p-thmA, 둘 다 supported. c-fixed-chain-convexity의 진술 "ψ″=(ψ/y²)[(Σx_i)²+Σx_i²]"는 해설과 같다. |
| 15 | 8.5 | 정리 B, 보조정리 3, 4·5, N, 정리 C | 일치 | re71a735 §3.2, p-thmB, p-lemma3, c-lemmaN, p-thmC, 모두 supported. 보조정리 4·5는 p-thmC 안에 있다. c-lemmaN은 생산자 셈 근거의 정정이다(검토 지지). |
| 16 | 8.5 | 명제 M♮(CF♮), 여섯 단계 | 일치 | re71a735 §3.3, c-propM-complete, supported("여섯 단계를 모두 따랐다"). 계산의 종류: J₁′, J₂′는 30자리 tanh-sinh 수치 적분이고, 두 치환으로 같은 값을 냈다(구간 산술 아님). 생산자의 p-propM(CF의 단조성)은 "단조성 주장은 거짓"이고 증명에 쓰이지 않는다. |
| 17 | 8.5 | 보조정리 SS, 정리 S′; 상수 1.15, 문턱 2/√π | 일치 | re71a735 §3.4, p-lemmaSS와 p-thmSprime, supported. 정리 S′의 진술: "y≥6666이면 모든 1≤d≤y+2에서 s_d(y)≤min(1, 1.15(y+d)/d^(3/2))", 문턱 "2/√π = 1.12838". |
| 18 | 8.5 | 명제 X·D; 입력 θ=1 체류 법칙, 벌크 점질량 상계 | **정정** | 지위가 다르다. p-propX의 주장문은 "[공표 입력 위 증명]"이고, 검토도 "공표 입력 위 증명으로 지지"라 했다. 벌크 점질량 상계(p-bulk-point-mass)는 n≤20000 정수 인증과 right-bulk-increase에 기댄다(re71a735 §4.8 표). p-propX는 정리 S′(p-thmSprime)도 쓴다. 명제 D(p-propD)는 "증명"(정리 A의 따름)이다. 5절 (나). |
| 19 | 8.5 | 정리 P, 보조정리 F | 일치 | re71a735 §3.6, p-thmP("증명으로 지지(결합 읽기)")와 p-lemmaF(supported, "최종 증명에는 쓰이지 않는다"). 보충: ε는 결합 확률로 읽는다(1.3절 2). 보조정리 F는 size-coupling을 쓰며, 최종 증명은 그 다듬은 꼴(보조정리 R)을 쓴다. |
| 20 | 8.6 | 보조정리 J, R, R′(x-감소 증명 포함) | 일치 | re71a735 §4.2, c-lemmaJ와 c-lemmaR, supported. x-감소 범위 "y≥6669, x∈[1.04,2^(2/3)], δ=xy^(2/3)≥562"는 기록 그대로다. 보조정리 R은 size-coupling(결손 고정 크기 단조성)을 쓴다. |
| 21 | 8.6 | 명제 U와 단조성 | 일치 | re71a735 §4.3, c-propU, supported("증명으로 지지"). 값 U(9705;1.3k^(2/3))=1.1507 등. 보충: 입력은 c-thmS, p-bulk-point-mass, p-thmSprime, p-propX다(모두 3절 다른 행에 있음). 검토 단서: "S를 [η_k,0.6]으로 바꾸는 단계는 η_k≥A_c/c일 때만 그대로 정당하다. … 쓰인 세 ν̄에서는 그 조건이 바로 성립한다." |
| 22 | 8.6 | 상쇄 보조정리, 명제 L, 단조성 | 일치 | re71a735 §4.4, c-propL, supported. 첫 차수 상쇄의 문장은 "첫 도달 몫이 얻는 3ν/k … 와 줄기 하계 θ가 잃는 3ν/k가 첫 차수에서 정확히 지워진다"다. 보충: 입력은 r3d0856b/q-t-route, q-window-survival(8.4), p-thmSprime, c-propM-complete다. |
| 23 | 8.6 | (나)의 네 가족 검사, (가)의 창 밖·창 안·가장자리; 입력 right-bulk-increase, 중앙 증가, 정수 인증의 최빈 위치 상계; 비형식(배정밀도 검사) | **정정** | 진술과 수치는 맞다. 시작점은 6668·8065·9551·9705이고, (나)의 여유는 "+0.589, +0.505, +0.467, +0.205"다(검토 독립 재현 +0.5894, +0.5046, +0.4673, +0.2047). (가)의 최소 여유는 +0.236(1a, δ=2). 지위는 c-na·c-ga의 판정("공표 입력 위의 비형식 증명으로 지지. 시작점 검사는 배정밀도이고 구간 인증은 아니다")과 맞는다. 입력 열의 식별자가 빠졌다. §4.8 표가 적은 [r3d0856b]/q-flq-a-window(§5.5)가 없고, right-bulk-increase(c-ga 의존 [r8a9b11e]/peer-theorem-W), 중앙 증가, 정수 인증이 이름만 있으며, 주장 ID c-na, c-ga도 없다. 이 식별자들은 3절 어디에도 없다. 5절 (다). |
| 24 | 8.6 | 정리 FLQ(c-flq); 비형식; 해 승인 | **정정** | 진술과 지위는 맞다. c-flq는 "[공표 입력 위의 비형식 증명]"으로 supported이고, sol-flq는 level informal로 승인되었다. 범위는 k≥6667, max(2k+103,20001)≤t≤3k다. 그러나 t=3k 부분의 입력이 3절 어디에도 없다. 기록의 문장은 "t=3k에서는 (V)와 r317/c-row3k로 이미 성립하고"이고, 의존 목록은 r317/c-row3k와 r317/c-vcore다. §4.8 표의 "r317 정리 T, (V) / r317/c-row3k, 노드 prob-first-layer-tail / 확립 / t = 3k"에 대응하는 행이 없다. 5절 (라). |
| 25 | 8.7 | 사슬 여섯 고리 | 일치 | 4-9 표 참조. 여섯 고리의 관계가 모두 해당 기록의 record.json에 있다. 프런티어(판 382)는 모두 supported로 적었고 전제 노드는 모두 established다. 진술도 맞는다. 보충: "판 376" 뒤 판 382까지 해당 절에 변화가 없다(1.2절). 입력의 컴퓨터 보조 지위는 이렇다. bvtheta-band는 binary64 상자 검사, source-side의 극 영역은 rf451d83 binary64 인증서, 2001–3130은 binary64와 Part B 자료(qstar-finite-range "컴퓨터 보조 증명")다. |
| 26 | 8.8 | 정리 FO(첫 차수 생존 법칙) | 일치 | re71a735 §6, c-first-order-survival, supported("증명으로 지지. … FLQ의 증명에는 쓰이지 않는다"). |

---

## 4. 4절 항목의 답

### 4-8. heavy-path-recurrence와 기존 정리 2.13 셋째 식

**같다.** 둘을 나란히 놓는다.
- 기록 r39ea75d/heavy-path-recurrence(supported): "정수 ℓ≥0, 1≤N≤2ℓ+3에서 A_(N,ℓ)=f_N(ℓ+1)+Σ_(m=ℓ+2)^N binom(N,m)(ℓ+1)A_(m−1,ℓ)p_(N−m)이다. … 따라서 y=ℓ+1, N≤2y+1에서 Pr_N(M≤y−1)=Pr_N(G≤y)+Σ_(m=y+1)^N π_N(m)(y/m)Pr_(m−1)(M≤y−1)이고, 이는 최대 나무 사슬 S_i에 대한 E∏_(S_i>y)(y/S_i)와 같다."
- 기존 원고 정리 2.13(256행 이하): "정수 ℓ≥0과 1≤N≤2ℓ+3에 대해 A_(N,ℓ)=f_N(ℓ+1)+… 이다. y=ℓ+1, a_N=A_(N,y−1)/p_N, c_N=Pr_N(G≤y)로 쓰면 N≤2y+1에서 a_N=c_N+Σπ_N(m)(y/m)a_(m−1), a_N=Pr_N(M≤y−1)=E[∏_(i=1)^J y/S_i]이다."

정의 2.12에서 J는 "S_i>y인 i의 수"이므로 ∏_(i=1)^J와 ∏_(S_i>y)는 같은 곱이다. 범위(N≤2y+1)와 세 식이 모두 일치한다. 3절 2.5행의 진술도 같다. 장부 1.2절대로 정리 2.13의 국소 c_N은 새 원고에서 π⁰_N(y)로 적는다.

### 4-9. 3절 8.7행의 여섯 고리

| 고리 | (가) record.json의 관계(주장) | (나) 프런티어 판 382: 상태와 전제 | (다) 진술 대조 |
|---|---|---|---|
| (1) FLQ ∧ 띠 ⇒ Q⋆₂ | 있음. r3d0856b relations의 `s3ecdd70238dc414eb88520eb4c580813-rel-flq-band-implies-qstar2`(주장 q-flq-relation, supported) | supported. 전제 qstar2-first-layer-tail (established), bvtheta-band (established) | 결론 qstar-second-layer. 서술과 같다. |
| (2) V ⇒ V* | 있음. raad7e6d `s7a2a959f478e4009a2dba3c577ae5e6b-rel-v-implies-vstar`(주장 p-ladder, supported) | supported. 전제 prob-first-layer-tail (established) | 결론 critical-tilt-first-layer-tail(V*). 같다. 기존 명제 6.17(사다리, raad7e6d)과도 머리 줄이 맞는다. |
| (2′) V 자체 | 있음. r845b205 `sb3bdcc77aa3a4451809bf65574fe07d8-rel-core-implies-v`(주장 p-rel-core-v, supported) | supported. 전제 prob-first-layer-core, ul-near-window, ul-far-window, ul-small-k-bulk, 모두 established | 전제 넷이 서술("V-core ∧ ul-near-window ∧ ul-far-window ∧ ul-small-k-bulk")과 같다. V-core는 r317d678/sol-vcore로 established. |
| (3) source-side ∧ V* ∧ Q⋆₂ ⇒ qstar-columns-from-3131 | 있음. raad7e6d `s7a2a959f478e4009a2dba3c577ae5e6b-rel-vstar-implies-qstar`(주장 p-rel-qstar, supported) | supported. 전제 source-side, critical-tilt-first-layer-tail, qstar-second-layer, 모두 established | 같다. source-side는 r79ee9e0/sol-source-side(주장 c-src-plus, supported). 기존 명제 6.16의 머리 줄이 "극 영역은 binary64 인증서에 의존"을 적는다. |
| (4) 2001–3130 ∧ from-3131 ⇒ one-step-local | 있음. r207f124 `rel-qstar-column-split`(주장 qstar-split-cover, supported) | supported. 전제 qstar-columns-2001-3130, qstar-columns-from-3131, 둘 다 established | 같다. 2001–3130은 r207f124/sol-qstar-columns-2001-3130(주장 qstar-finite-range, "컴퓨터 보조 증명(binary64와 명시 반올림 한계, 공표 Part B 인증 자료에 기댐)", supported). |
| (5) one-step-local ⇒ W_L♭ | 있음. r3172894 `rel-qstar-implies-wlflat`(주장 rel-qstar-wlflat, supported) | supported. 전제 one-step-local (established) | 결론 left-residual-reduced. 같다. 기존 명제 6.14(흡수 귀납, r3172894)의 머리 줄과 맞는다. |
| (6) W_L♭⇒W_L⇒L⇒T, 네 위치쌍 ⇒ 뿌리 | 프런티어에 r7c26b8b/rel-wlflat-implies-wl, rb6423c6/rel-wl-implies-left-interior, rce3dc75/left-implies-cross-rel, rce3dc75/split-four-position-pairs가 있다(이 네 기록의 record.json은 열지 않았다) | 넷 모두 supported. 전제(left-residual-reduced, left-residual-increase, left-interior, central-gap·right-interior·cross-pairs·left-interior) 모두 established | 같다. 2절 7.5행과 같은 사슬이다. |

프런티어의 qstar-columns-from-3131에는 다른 관계 r79ee9e0/rel-qstar-from-3131-three-parts도 있다. 그 전제 first-layer-weighted-tail은 open이고, 8.7행은 그 관계를 쓰지 않는다.

### 4-10. 행의 진술·지위·상수(3절 범위)

행별 판정은 3절 표에 있다. 세션이 적은 상수 가운데 Q⋆₂ 경로의 것을 글자 그대로 대조했다.

| 상수 | 3절·연구_파악의 표기 | 기록 원문 | 판정 |
|---|---|---|---|
| 50.62 | 8.4행 "정리 S·U(…p-tv-proof, 상수 50.62)" | r3d0856b §5.4: "DDL(k) := 2·50.62/√(k−1)", "p-tv-proof와 r317 (2.5)의 상수 C_U = 50.62". r317/c-vcore-quant: "C_U는 r845b2055 검토의 위합 C_U≤50.620". r845b205/p-thmU 진술: "50.6/√t" | 값은 맞다. 귀속은 정정(3절 #12) |
| 1.15 | 8.5행 | p-thmSprime: "1.15(y+d)/d^(3/2)", y≥6666 | 일치 |
| 2/√π = 1.12838 | 8.5행 | §3.4: "2β√2 = 2/√π = 1.12838" | 일치 |
| I₁ = 0.53192 | 연구_파악 2.3(장부 1.2) | §1: "I₁ := 4β/3 = 0.53192". c-lemmaJ: "I₁=4/(3√(2π))" | 일치 |
| 시작점 6668·8065·9551·9705 | 8.6행(파견문) | §4.1 표와 §4.5 표: 6668, 8065, 9551, 9705 | 일치 |
| +0.589/+0.505/+0.467/+0.205 | 8.6행(연구_파악) | §4.5 표: "+0.589", "+0.505", "+0.467", "+0.205" | 일치 |
| 273개 경우 | 8.2행 | §3.5: "273개 경우 모두에서 (가)(나)를" | 일치 |
| x∈[1.04, 2^(2/3)] | 연구_파악 2.3 | §4.2: "x ∈ [1.04, 2^(2/3)]이며 δ = xy^(2/3) ≥ 562", y ≥ 6669 | 일치 |
| 첫 차수 상쇄 3ν/k | 연구_파악 2.3 | §4.4: "3ν/k … 3ν/k가 첫 차수에서 정확히 지워진다" | 일치 |

검사하지 않음: 4-10의 P◇ 경로 상수(1.206, 6.62/√k, 1.0845, 1.0786, 0.0056, 3.1·10^(−7), 1.149357, 2.274, 9467, 38887, 0.729)와 2절의 행. 다른 파견의 범위다.

### 4-11. concern·철회와 현재 판

**프런티어의 현재 판은 382**(K/frontier.md 첫 줄 `Revision: 382`)이고, 지도가 기준으로 쓴 판은 376이다. 판 377–382의 기록 여섯은 노드·관계·해를 등록하지 않았다. 그러므로 아래 노드 절의 관계·상태는 판 376 이후 바뀌지 않았다. 판 376의 프런티어 파일 자체는 인스턴스에 없어 직접 비교하지는 못했다.

| 기록 | 프런티어에서 그 기록이 나오는 노드 절(상태) | concern·철회 표시 | assessment의 concerns |
|---|---|---|---|
| r3d0856b | qstar-second-layer, qstar2-first-layer-tail, bvtheta-band (모두 informal_proved) | 없음 | [] |
| re71a735 | qstar2-first-layer-tail (informal_proved) | 없음 | [] |
| r317d678 | source-side, prob-first-layer-tail, lrp-second-layer, left-residual-reduced, qstar-columns-2001-3130, prob-first-layer-core (모두 informal_proved) | 없음 | [] |
| rb1d8cd5 | flat-core (informal_proved) | 없음 | [] |
| r845b205 | prob-first-layer-tail, prob-first-layer-core, ul-far-window, ul-near-window, ul-small-k-bulk (모두 informal_proved) | 없음 | [] (비지지 주장 4개는 3절이 쓰지 않음) |
| r98fb348 | ul-core-borel-convexity, ul-core-borel-convexity-explicit, ul-core (unresolved), ul-core-visit-moment (informal_proved) | 없음 | [] |
| r7e03176 | first-layer-weighted-tail, ul-core (unresolved), ul-far-window, ul-near-window, ul-small-k-bulk (informal_proved) | 없음 | [] |
| r39ea75d | 해당 노드 절 없음(프런티어 언급 0) | 해당 없음 | [] (비지지 2개는 3절이 쓰지 않음) |
| r051bfe1 | onelevel-attachment, tilted-source-tails (unresolved), tilted-survival-decay (informal_proved) | 없음 | [] |
| raad7e6d | first-layer-weighted-tail (unresolved), qstar-second-layer, source-side, critical-tilt-first-layer-tail, prob-first-layer-tail, qstar-columns-from-3131 (informal_proved) | 없음 | [] |
| r207f124 | one-step-local, qstar-columns-2001-3130, qstar-columns-from-3131 (informal_proved) | 없음 | [] |
| r3172894 | left-residual-reduced, one-step-local (informal_proved) | 없음 | [] (비지지 1개는 3절이 쓰지 않음) |
| r79ee9e0 | first-layer-weighted-tail (unresolved), qstar-second-layer, source-side, qstar-columns-from-3131 (informal_proved) | 없음 | [] (undetermined 1개는 3절이 쓰지 않음) |
| r60a6f55 | 해당 노드 절 없음(언급 0) | 해당 없음 | [] |
| r030ffae | bvtheta-band (informal_proved), bvtheta-bulk, stem-gain-vs-threshold (unresolved) | 없음 | [] |
| r6a8c8b6 | 해당 노드 절 없음(언급 0) | 해당 없음 | [] |

P◇ 경로(2절)의 의존 기록 가운데 위 목록 밖의 것(r6f5f48f, rae1f209, r5909c9e, rb6a2cd0 등)은 검사하지 않음.

### 4-13. re71a735 §4.8 표가 rb1d8cd5(flat-core)의 주장을 쓰는가

**쓰지 않음.** 근거는 셋이다.
- §4.8 표(4-15에 전문)의 출처 칸에 rb1d8cd5가 없다.
- re71a735의 `exposition.md`, `record.json`(모든 주장의 dependencies), `review/feedback.md`, `provenance.json`에서 "rb1d8cd5", "flat-core", "flat", "chain-representation"은 0회 나온다.
- 기록 밖 의존 14개는 r317/c-row3k, r317/c-vcore, r39ea75d/heavy-path-recurrence, r3d0856b/q-flq-a-window·q-flq-relation·q-sojourn-form·q-t-route·q-window-survival, r60a6f55/size-coupling, r7e03176/p-bulk-point-mass·p-row-averaging-e3·p-thmF-prime, r845b205/c-fixed-chain-convexity, r8a9b11e/peer-theorem-W, r98fb348/c-thmS이다. rb1d8cd5는 없다.

참고로 re71a735의 점질량 사슬 표현은 자기 기록의 정리 P(p-thmP, 무거운 사슬 공식 위)이고, rb1d8cd5 명제 1과는 독립이다.

### 4-14. re71a735가 Borel 갱신 면적 𝔄_D(rb1d8cd5/borel-renewal-area)를 쓰는가

**쓰지 않음.** 위 네 파일에서 "갱신 면적", "𝔄", "borel-renewal", "Poisson", "갱신 집합"은 0회다. re71a735가 쓰는 '면적'은 둘이다.
- 정리 B의 경로 면적 X̃_j = Σ_(i≤j) a_i/(y₀+1+a_i)
- 보조정리 J와 정리 FO의 "사슬이 지나는 수준들의 합" Σa_i

둘 다 자기 기록 안에서 정의되었다. 용어집 borel-renewal-area의 global_reason은 "여러 첫 층 기록이 같은 양을 조건부 면적·여유 합·Σa_i 등 다른 이름으로 썼다"고 적어 같은 종류의 양임을 밝힌다. 그러나 re71a735는 rb1d8cd5를 인용하지 않는다. 그러므로 3절 2.11(조건부) 행은 그 행의 조건에 따라 넣지 않는다.

### 4-15. re71a735 §4.8 표 전문과 3절 대응

**§4.8 "쓰인 입력과 그 지위"(원문 그대로)**

| 입력 | 출처 | 지위 | 쓰인 곳 |
|---|---|---|---|
| 명제 S(체류 꼴) | r3d0856b/q-sojourn-form | 증명(정확 항등식) | (가), (나) |
| 명제 T(T 경로) | r3d0856b/q-t-route | 공표 입력 위 증명 | (나) |
| 명제 W(창 생존 상계 W_b) | r3d0856b/q-window-survival | 증명 | 1a의 Λ |
| 공표 행 증가의 창 밖 논증 | r3d0856b/q-flq-a-window(§5.5), right-bulk-increase, 중앙 증가, n ≤ 20000 정수 인증 | 비형식 정리·컴퓨터 인증 | (가) 창 밖 |
| θ=1 체류 법칙 | r98fb348c/c-thmS | 증명 | 명제 X·U, Stays_PM |
| 벌크 점질량 상계 | r7e03176b/p-bulk-point-mass | 공표 입력 위 증명(review 지지; 행 증가는 n ≤ 20000 정수 인증에 기댐) | 명제 U(위쪽), Stays_PM |
| 따름정리 E, 정리 F′ | r7e03176b/p-row-averaging-e3, p-thmF-prime | 증명(review 지지; 따름정리 E는 정수 인증 n ≤ 20000에 기댐) | BD, F′ |
| 크기 결합 | r60a6f557/size-coupling | 비형식 정리 | 단조성 |
| 무거운 사슬 공식 | r39ea75d8/heavy-path-recurrence | 증명 | 전부 |
| r317 정리 T, (V) | r317/c-row3k, 노드 prob-first-layer-tail | 확립 | t = 3k |
| 보조정리 2·3, 정리 A·B·C | 생산자(이 기록) | 증명, peer 정확 확인 | DDL₂ |
| 명제 M♮(CF♮ ≥ DDL₂, 감소) | peer(이 기록; 생산자 명제 M의 완성) | 증명(§3.3) | 모든 가족 |
| 보조정리 SS, 정리 S′ | 생산자(이 기록) | 증명, peer 재유도 | φ_C, 명제 U |
| 정리 P | 생산자(이 기록) | 증명, peer 정확 확인 | 보조정리 R |
| 보조정리 B·J·R·R′, 명제 U, 상쇄 보조정리, 가족 하계 | peer(이 기록) | 증명 | 균일화 |
| 한 점·유한 검사 | peer(이 기록) | 배정밀도 계산(인증 아님), 여유 ≥ 0.205 | 시작점 |

**3절 행과의 대응**

| §4.8 입력 | 3절의 대응 행 | 대응 상태 |
|---|---|---|
| 명제 S | 8.2 | 있음 |
| 명제 T | 8.4 | 있음(입력 열 정정 필요, 3절 #12) |
| 명제 W | 8.4 | 있음 |
| 공표 행 증가의 창 밖 논증 | 8.6 "네 가족" 행의 입력 | 부분. q-flq-a-window가 없고, right-bulk-increase·중앙 증가·정수 인증은 이름만 있다 |
| θ=1 체류 법칙 | 8.4·8.5의 입력([r98fb348]/c-thmS) | 있음(입력으로만) |
| 벌크 점질량 상계 | 8.5 명제 X·D의 입력([r7e03176]/p-bulk-point-mass) | 있음(입력으로만) |
| 따름정리 E, 정리 F′ | 8.4의 입력 | 부분. 따름정리 E는 ID가 있고, 정리 F′은 ID([r7e03176]/p-thmF-prime)가 없다 |
| 크기 결합 | 8.4의 입력(이름만). 지위는 2절 2.8행 | 부분. 3절에는 ID([r60a6f55]/size-coupling)가 없다 |
| 무거운 사슬 공식 | 2.5 | 있음 |
| r317 정리 T, (V) | 없음 | **빠짐**: [r317d678]/c-row3k(와 c-vcore-quant), 노드 prob-first-layer-tail(8.7에 V로만 나옴) |
| 보조정리 2·3, 정리 A·B·C | 8.5 두 행 | 있음 |
| 명제 M♮ | 8.5 | 있음 |
| 보조정리 SS, 정리 S′ | 8.5 | 있음 |
| 정리 P | 8.5 | 있음 |
| 보조정리 B·J·R·R′, 명제 U, 상쇄 보조정리, 가족 하계 | 2.11(B), 8.6(J·R·R′; U; 상쇄·L) | 있음 |
| 한 점·유한 검사 | 8.6 "네 가족" 행 | 있음 |

**세션이 빠뜨린 입력.** 기록의 의존 목록과 본문을 기준으로 한다.
1. [r317d678]/c-row3k(정리 T)와 노드 prob-first-layer-tail(V). 정리 FLQ의 t=3k 부분에 쓰인다. c-flq의 의존 목록에는 [r317d678]/c-vcore도 있다. 정리 T의 상수 c(k)는 [r317d678]/c-vcore-quant에서 온다.
2. [r3d0856b]/q-flq-a-window(§5.5). (가)의 창 밖 논증에 쓰인다.
3. 식별자: right-bulk-increase(c-ga 의존 [r8a9b11e]/peer-theorem-W, 노드 s02738f0396be497f9a02a1415fb0df47-right-bulk-increase), 중앙 증가([rce3dc75]/central-gap-closed, r3d0856b §2.5가 인용), n≤20000 정수 인증과 최빈 위치 자료. 마지막의 출처 후보는 따름정리 E의 의존 목록에 있는 [rce3dc75]/integer-certificate, [r19de912c]/right-half-unimodal-finite, mode-formula-crosscheck이고, 그 진술은 미확인이다.
4. 명제 T의 입력에서 빠진 [r317d678]/c-vcore-quant(상수 50.62, c-bk-bound 경유의 행 2k 단조 구간)와 [r317d678]/c-row3k(τ 논증). §4.8 표 밖이지만 q-t-route의 의존 목록에 있다.
5. ID 보충: [r7e03176]/p-thmF-prime, [r60a6f55]/size-coupling.

---

## 5. 정정 제안 목록

(가) **3절 8.4 명제 T 행, "입력" 열**을 다음으로 바꾼다.
> [r3d0856b] §5.4(q-t-route); 입력: 명제 S(8.2), 보조정리 2(e)(8.1), 정리 F′([r7e03176]/p-thmF-prime), 따름정리 E([r7e03176]/p-row-averaging-e3)와 행 2k 단조 구간의 (k−1)c_(2k)(k)≤g(k)([r317d678]/c-bk-bound = r317 §2 걸음 4(다)), 정리 S (라)([r845b205]/p-split), 정리 U의 정수판([r845b205]/p-tv-proof; 상수 C_U=50.62는 [r845b205] 검토의 위합으로 [r317d678]/c-vcore-quant (2.5)가 채택했다. 기록 p-thmU의 진술은 50.6), θ=1 체류 법칙([r98fb348]/c-thmS), 크기 결합([r60a6f55]/size-coupling), 무거운 사슬 공식([r39ea75d]/heavy-path-recurrence, 2.5)과 r317 정리 T 걸음 3의 τ·두 나무 논증([r317d678]/c-row3k)

같은 행의 "비고" 열에는 "범위 k≥6667, max(2k+103,20001)≤t<3k(ν≤k−1). 정리 U의 적분 위합은 배정밀도"를 더한다.

(나) **3절 8.5 명제 X·D 행, "지위" 열**을 "증명"에서 다음으로 바꾼다.
> 명제 X: 증명(공표 입력 위; θ=1 체류 법칙·벌크 점질량 상계·정리 S′ 위, 벌크 점질량 상계는 n≤20000 정수 인증과 right-bulk-increase에 기댐). 명제 D: 증명(정리 A의 따름)

"입력" 열에는 "정리 S′(8.5)"를 더한다.

(다) **3절 8.6 "네 가족 검사" 행, "입력" 열**을 다음으로 바꾼다.
> [re71a735] §4.5–4.6(c-na, c-ga); 입력: 명제 S·T·W(8.2·8.4), 정리 C·명제 M♮·정리 S′(8.5), 보조정리 J·R·R′·명제 U·명제 L(8.6), 창 밖 논증 [r3d0856b]/q-flq-a-window(§5.5), right-bulk-increase(노드 s02738f…-right-bulk-increase, [r8a9b11e]/peer-theorem-W), 중앙 증가([rce3dc75]/central-gap-closed), n≤20000 정수 인증의 최빈 위치 상계(출처 ID는 대조에서 확정; 후보 [rce3dc75]/integer-certificate, [r19de912c]/right-half-unimodal-finite, mode-formula-crosscheck), 따름정리 E·정리 F′·벌크 점질량 상계·θ=1 체류 법칙

"비고" 열에는 "(가) 최소 여유 +0.236(1a, δ=2). 1a는 30자리 독립 재계산"을 더한다.

(라) **3절 8.6 정리 FLQ 행, "입력" 열**을 다음으로 바꾼다.
> [re71a735] §4.7(c-flq, 해 sol-flq); 입력: c-na, c-ga(8.6); t=3k는 노드 prob-first-layer-tail(V)과 [r317d678]/c-row3k(정리 T; 상수 c(k)는 [r317d678]/c-vcore-quant, c-flq 의존 목록에는 [r317d678]/c-vcore)

"지위" 열은 "비형식(공표 입력 위; 시작점 검사 배정밀도, 구간 인증 아님)"으로 다듬는다. 이 입력들을 따로 인용하려면 3절에 "r317 정리 T(t=3k)" 행 하나를 더하는 방법도 있다.

(마) **3절 2.11(조건부) 행**을 삭제한다. 그 행의 조건("[re71a735] §4.8의 입력 표가 이를 쓰는 경우에만")이 성립하지 않는다(4-13·4-14: 쓰지 않음). 4절 항목 13·14에는 "쓰지 않음(대조 Q)"을 적는다.

(바) **4절 항목 11의 문구** "판 376 이후 현재 판 포함"에 현재 판 382를 적는다. 3절 8.7행 "입력" 열의 "프런티어 판 376"도 "프런티어 판 376(판 382에서 같음, 대조 Q)"로 바꾼다.

(사) **장부 1.1절 보충**(어긋남이 아니라 누락). 다음 두 행을 더하기를 권한다.
- "W^(ℓ)_n := F_n(ℓ) − F_(n−1)(ℓ−1) (F_n(ℓ)=Pr_n(M≤ℓ) 규약) | [r3d0856b], [re71a735] §2 | σ_(n−1)(ℓ) | Stays, Bd의 정의에 쓰인다"
- DD_m 행의 출처 칸에 [r3d0856b](명제 S의 DD_m, 같은 정의)을 더한다.

(아) **판정을 바꾸지 않는 보충 권고**(일치 행)
- #3 2.11 보조정리 B: 입력 열에 "c-lemmaB".
- #5 8.1 정리 R: "(c-thmR; k≥2, 2k+1≤t≤3k)".
- #7 8.1 보조정리 2: 입력에 "[r317d678]/c-thmQ2(기록 의존 목록)".
- #10 8.2 명제 S: 비고에 "범위 k≥3, 1≤ν≤k−1. 273은 (가)(나)의 경우 수. 기록 의존에 [r98fb348]/c-propN".
- #11 8.3: 비고에 "bvtheta-band의 근거 band-node는 theorem-B-triple(컴퓨터 보조, binary64 상자 검사). 주장문의 t=3k 문장은 [r317d678]/c-row3k에 기댐".
- #13 8.4 명제 W: 입력에 "[r39ea75d]/heavy-path-recurrence(2.5)".
- #16 8.5 명제 M♮: 비고에 "J₁′, J₂′는 30자리 수치 적분".
- #19 8.5 정리 P: 비고에 "ε는 결합 확률로 읽는다(검토 정정). 보조정리 F는 최종 증명에 쓰이지 않음".
- #21 8.6 명제 U: 입력에 "θ=1 체류 법칙, 벌크 점질량 상계, 정리 S′, 명제 X". 비고에 "η_k<A_c/c 경우 한 줄 보충(검토)".
- #22 8.6 상쇄·L: 입력에 "명제 T·W(8.4), 정리 S′, 명제 M♮".
- #25 8.7: 관계 ID를 전체형으로 적는다(4-9 표의 (가) 칸).

---

## 6. 미확인·읽지 못한 것

- **미확인 판정**: 없음.
- **검사하지 않음(범위 밖)**: 2절(P◇ 경로)의 행, 4절 항목 1–7·12·16, 4-10의 P◇ 상수, 4-11의 P◇ 의존 기록.
- **읽지 않았거나 부분만 읽은 것**
  - r3d0856b `feedback.md` §0–§6과 re71a735 `feedback.md` §1–§5, §9–§11. 판정과 정정은 assessment와 읽은 절로 확인했다.
  - r39ea75d, r98fb348, r7e03176, r051bfe1, raad7e6d, r207f124, r3172894, r79ee9e0, r60a6f55, r030ffae, r6a8c8b6의 해설(파견문대로 주장 ID와 진술만).
  - 고리 (6)의 네 기록(r7c26b8b, rb6423c6, rce3dc75, r656206c)의 record.json(프런티어 줄만 읽음).
  - 정수 인증의 최빈 위치 상계 출처 후보 r19de912c의 주장 진술(미확인).
- **직접 비교하지 못한 것**: 프런티어 판 376 파일 자체(인스턴스에는 현재 판 382만 있다). 대신 판 377–382에 공표된 기록 여섯이 노드·관계·해를 등록하지 않았음을 확인했다.
- **기존 원고 대조의 한계**: 8.7행의 "기존 명제 6.14·6.16·6.17, 6.7"은 원고의 머리 줄과 귀속 기록만 대조했다. 본문은 읽지 않았다.
