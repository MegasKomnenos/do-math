# 보완 판정 question 다섯의 보완 대응표

대상: `initial-questions-검토.md`에서 `revise` 판정을 받은 `op-threshold-block`, `op-tie-block-transport`, `op-layer-period`, `op-continuum-ties-blocks`, `op-deformation-boundary`. 보완 결과는 `initial-questions.revised.json`(question 5개)에 있다. 검토 보고의 「보완할 점」 각 항목과 대응을 적고, 지적이 원자료와 맞는지 다시 읽은 좌표를 함께 적는다. 인스턴스 `parking-unimodality-fresh-20261105-150803`의 원자료(frontier 판 184, 기록 exposition.md, review/assessment.json·feedback.md, index 모듈, glossary)를 읽기만 했고 쓰지 않았다.

다시 읽은 원자료: `knowledge/frontier.md` 전문(판 184), `knowledge/index.md`의 절 머리말과 모듈 목록, 기록별로 r6b37c7e §5.2–5.6·§6 전체, r9d97cea §6.1–6.5·§8, r10ff8c2 §5 전체, rf451d83 §3, r20df549 §3 전체·§5·§7, ra52a3c0 §4.3b–§7과 review/feedback.md §5·assessment의 `mode-constant-limits`, r1b79fab §5·§6·§8·§10·§12, r24b9bf1 §5, ra4c01fc §9·§10.1–10.2, rce3dc75 §10, r475ada §7, r5f5cf73 §2, r81e7051 exposition 전문과 limiting-shape.md §4, r7eeaca03 §6–7과 peer-extensions.md의 a_* 정의, rd4015a8 §6–9, index 모듈 large-subtree-path-and-borel-renewal·weighted-shapes-and-log-coordinates·lucky-weights-and-slices·total-displacement-tilts-and-geometric-endpoints·fixed-preference-orbits-and-dickman·surplus-spaces-and-sparse-collisions·outcome-fibres-and-saturation-obstructions·cumulative-and-tail-logconcavity의 모듈 머리말, glossary의 H_S·H_C 항목.

공통으로 한 일. 검토 보고 §8.2의 권고대로 다섯 question 모두 끝에 이웃 question(통과한 op-central-window·op-left-right-asymmetry 포함)과의 경계를 한 문장씩 적었다. 모든 수치·진술에 원자료의 지위(증명·인증·비형식·관찰·발견적·미지)를 붙였다.

---

## 1. op-threshold-block

**보완할 점 1. 전제를 원자료가 k^(−1/3) 상대 여유를 보인 체제로 한정한다(중앙 t→0, 첫 층 고정 λ, 둘째 층, 오른쪽 창의 유한 c 부족분).**

대응: 반영했다. 첫 문장을 "In every regime … the universal k^(−1/3) relative margin"에서 "In four regimes the records show … a relative margin of order k^(−1/3)"로 바꾸고 네 체제를 각각의 지위와 함께 열거했다. 중앙은 rce3dc75 §10("선도 상수 4I/√π는 같고 상대 차는 (2/I)k^(−1/3)뿐")과 r6b37c7e §5.2((R−1)k^(1/3)=2.63→2.39, binary64), 첫 층은 r9d97cea §6.4 peer 정리 B((m(λ)+o(1))k^(−1/3), 비형식 증명, "고정 λ와 중앙 사이의 균등 정리는 주장하지 않는다"), 둘째 층은 r6b37c7e §6.3 추측 6.3과 §6.4–6.5 측정(min m_3≈15.34, 추측), 오른쪽 창은 ra4c01fc §10.1(D(x̂)c^(−1/3), D≈5–9.5, 비인증 binary64)로 적었다. "universal"이라는 낱말은 뺐다. 군집 기제("착지")는 r9d97cea §6.3이 "이 경로 해석 자체는 증명하지 않았다"고 적은 대로 지위를 밝혔다.

**보완할 점 2. 창 내부(t∈[t_0,T])와 극 체제는 원자료가 다른 모습을 보이는 곳으로 밝히고, 그 차이 자체를 질문에 넣거나 대상에서 뺀다.**

대응: 반영했다(차이를 질문에 넣는 쪽). statement에 "Two other regimes look different in the records and are not assumed to share this premise"라는 문단을 두어, 창 내부는 r6b37c7e §6.6(R이 k에 무관한 R_∞(t)로 수렴, t≈4에서 최대 ≈2.25, 상대 여유 O(1), 극한 함수 미도출)대로, 극 체제는 r10ff8c2 §5.1(E≈κ_kn, E²이 압도)대로 적었다. 충분한 답에는 "창 내부 대상(두 성분, O(1) 여유)과 극 체제 경계층 블록이 같은 국소 대상의 다른 강도인지 다른 대상인지를 판정할 것"을 넣었다. 창 자체의 윤곽은 op-central-window의 몫이므로 경계 문장으로 구분했다.

**보완할 점 3. 극 체제에서 '문턱 인접 성분'이 무엇을 가리키는지 정한다(k 아래의 경계층 블록인지 등).**

대응: 반영했다. rf451d83 §3.1을 다시 읽었다. 소인 길이 분포의 몸통은 n≤k이고 인자 e^(σ_kn/k)가 n≈k 근처 폭 ≈k/σ_k의 경계층에 질량을 모으며, n>k 꼬리의 질량은 0.18→0.14다. 따라서 극 체제의 대상을 "prime blocks of size just BELOW k, in a boundary layer of width k/σ_k"로 정하고, 그 기록이 보여 주는 것은 주기 k 진동(§3.2)과 공명 골 kθ≈2π(§3.3)뿐이며 "용량 바로 위 성분, k^(1/3) 무거운 자리 질량, k^(−1/3) 여유 가운데 어느 것도 보여 주지 않는다"고 grounds에 명시했다. 원래 grounds의 "prime blocks of size near k"는 이 정의로 바꿨다.

**보완할 점 4. k^(2/3) 멈춤 깊이와 k^(1/3) 끝점 거리를 구분해 적는다.**

대응: 반영했다. 원래 grounds의 "… within 0.5k^(2/3) of k, and the gain/loss boundary r* ~ 0.63k^(1/3) is set by chains ending that close to the threshold"에서 "that close"를 없앴다. statement와 grounds 모두에서 두 척도를 따로 적었다. 군집이 놓이는 멈춤 깊이는 O(k^(2/3))(ra52a3c0 §5: 손실의 92–95%가 k+0.5k^(2/3) 이하까지 내려간 사슬에서; 생산자 발견적 그림; D*=0.542k^(2/3)), 이득/손실 경계는 끝점 거리 r*≈0.63k^(1/3)(r20df549 §3.6b, 발견적 예측; 관측 r*=1,4,8,13)로, "a band of the narrower scale k^(1/3)" 안에 있다고 썼다. "a local law must resolve both"를 질문에 넣었다.

추가로 고친 것: 원래 statement의 "D_λ cluster", "D_3 cluster", "the two components whose deficits add to S", "prime blocks of size near k"라는 네 체제 묘사를 위 구분에 맞게 다시 썼다. 중앙 체제의 국소 대상은 r9d97cea §8.1 표("중앙 n∈{2k−1,2k}: k^(1/3) 규모(군집 하나)")로 뒷받침했다. 원래 '충분한 답'의 "resonance depth at the pole" 복원 요구는 극 체제가 k^(−1/3) 체제가 아니므로 뺐다.

---

## 2. op-tie-block-transport

**보완할 점 1. H 절편 문장을 원자료대로 고친다(h≥1 절편이 최빈점 전부터 음수가 되므로, H를 보존하는 비교나 자리별 비교로는 부호를 얻을 수 없다는 뜻).**

대응: 반영했다. ra52a3c0 §6과 review/feedback.md §5.2를 다시 읽었다. §6: "h=0 절편은 항상 ≥0이다. 그러나 h≥1 절편은 최빈점 훨씬 전부터 음수다", "Z≤1 절편은 항상 ≤0", "자리별 비교 … i=k에서 즉시 깨진다". feedback §5.2: n=25의 'k≥10'은 h=1 절편에 대한 진술이고, 결론은 "H를 보존하는 절편별 비교나 자리별 비교로는 불가능"으로 읽어야 한다. statement의 "every H-slice or site-wise comparison is negative somewhere"를 "the h = 0 slice is always ≥ 0 while h ≥ 1 slices turn negative well before the mode, and the site-wise comparison already fails at site k: the positivity is a global compensation that no H-preserving slice-wise or site-wise injection can exhibit"로 바꿨다. grounds에도 review의 정정 내용을 그대로 적었다.

**보완할 점 2. r*~0.63k^(1/3)은 발견적 예측으로, −,+,− 모양은 큰 n에서 관찰된 것(세 위치에서 정확 인증)으로 지위를 밝힌다.**

대응: 반영했다. r20df549 §3.6b("이 점근식은 모형에서 나온 발견적 예측이며 증명이 아니다"; 상계 E[(N−1)²ρ^N|끝점]=O(k^(2/3))는 미증명)와 §3.6("'g→0'과 세 단계 모양의 지속은 binary64 관찰과 출판 군집 정리에 기댄 발견적 설명")대로 적었다. statement에서 증명된 것(정리 3.1 끝점 분해, 보조정리 3.2 위험률 극한)과 관찰된 것(λ∈{0.6,0.7,0.8}, n≤3·10⁴ binary64의 −,+,−; r*=1,4,8,13)과 정확 인증((300,210), (600,420), (1000,700))과 발견적 예측(r*≈0.63k^(1/3))을 각각 표시했다. 또 §3.3의 사실, 곧 n≤110에서 증가 위치 1610곳 중 1277곳이 "+−"이고 333곳만 "−+−"라는 점을 statement에 넣어 세 단계 모양이 큰 n의 현상임을 밝혔다(검토 보고의 어긋남 3에 해당).

**보완할 점 3. 찾거나 배제하려는 '국소 수송'이 어떤 종류인지 정한다.**

대응: 반영했다. 질문 (i)에서 세 층위를 정했다. 가장 좁은 뜻은 r20df549 §3.6·§7이 제안한 "같은 사슬의 마지막 걸음만 바꾸는 짝짓기"(끝점 이동 O(1) 또는 o(k^(1/3))), 넓은 뜻은 끝점 이동이 손실 띠의 폭 O(k^(1/3)) 안인 수송, 비국소는 끝점 거리 ≫k^(1/3)을 넘거나 다른 전역 구조 사이로 질량을 옮겨야 하는 경우다. 충분한 답의 배제 쪽은 "no transport with endpoint displacement O(k^(1/3)) exists"로 구체화했다. 질문 (ii)에 전단사 근접성(상대 간격 n^(−1/3), r20df549 §5.1·§7 "거의 전단사여야")을, (iii)에 왼쪽의 잎별 분해(r20df549 §7, r9d97cea §8.2)를 두었다.

추가로 고친 것: 원래 statement의 "relative gap of order k^(−1/3)"를 r20df549 §5.1의 표현대로 "n^(−1/3) in the right bulk"로 맞췄다(k와 n은 고정 비율에서 같은 차수이므로 내용은 같다). "the threshold-child hazard stays O(1)"는 보조정리 3.2의 내용(h_π(0)=1/e, h_π(r)~1/(2r))으로 풀어 썼다.

---

## 3. op-layer-period

**보완할 점 1. 내부 최솟값과 μ 단조성 실패의 지위를 원자료대로 적는다(r=2,3은 증명·인증, r=4는 수치와 발견적 국소 해석, r≥5는 미지, r≥6은 끝점 논법이 통하지 않을 수 있다; r1b79fab §10, §12의 3).**

대응: 반영했다. r1b79fab §5.1(λ*_2=0.6435334696 닫힌 꼴·Sturm, λ*_3=0.4240285084 구간 인증, λ*_4≈0.3082 "인증 아님"), §5.2(정리 B 비형식; B₂·B₃; B₄는 "수치 입력에 조건부", "예측"), §5.3("r=2,3에서는 이것이 정확히 성립한다", "r≥4에서는 사정이 다르다(§10)"), §10(Φ_4(1/3−)≈14.3 유한, Φ_4″≍ε^(−3/2), Φ_5″≍ε^(−1/2), r≥6 꼭짓점 기여 유계·모서리 미확인, "r≥6에서는 위 끝에서 M_r이 유계일 수 있으므로 … 끝점 논법만으로는 따르지 않는다", "발견적 결론"), §12의 3("일반 r≥5에서 M_r에 내부 최솟값이 있는지는 모른다")을 그대로 statement와 grounds에 옮겼다. 원래 statement의 "fixed-ratio profiles Phi_r with internal minima of Phi_r''/Phi_r"와 "mu-monotonicity breaking inside each layer because …"는 "r=2,3 확립(정리 B, 비형식), r=4 수치 조건부, 그 너머 미지"로 바꿨다. grounds의 "(sections 5.3, 10)" 인용은 §10이 실제로 말하는 내용(범위 제한)으로 고쳤다.

**보완할 점 2. 그렇게 고치면 r≥4 부분이 그 미지를 직접 묻게 된다.**

대응: 반영했다. 질문에 "do M_r and m_r keep an interior minimum and does the k^(−1/3) margin scale persist when the upper-end singularity of Φ_r weakens (r≥6)"를 넣고, 충분한 답에 "settles the existence of interior minima of M_r and m_r for r≥4 (at least deciding r=4 rigorously)"를 추가했다. 층 상수의 현황도 r별로 나눠 적었다. r=2는 닫힌 꼴 m(λ)(r9d97cea 비형식 정리; r6b37c7e §6.5에서 λ²Φ_2″/Φ_2=m(λ)D_λI_0 기호 확인), r=3은 추측 6.3과 측정, 양 끝 상수 9/(8I_0)·1/(3I_0)와 지수 규칙은 증명(명제 6.4), r≥4와 r이 k와 함께 자라는 영역은 미처리(§6.8).

추가로 고친 것: 원래 statement의 "in the pole regime … the same period-k structure reappearing"에 rf451d83 §3.2의 단서(δ*σ_k²=33–47, 점근값 2π²과 거리가 멂, 반례 아님)를 붙였다. r9d97cea §8.2의 한 극점 공식 일치에 적합도(x=8에서 10^(−4), x=4·2.5에서 0.07–0.25 벗어남)와 "왼쪽에서 문턱 밀도의 t 모양은 J(t)S(t)에 비례하지 않는다"는 단서를 넣었다. r10ff8c2 §5.7의 연속 근사 T≈κ_r=(로그 기울기)²+(로그 곡률)도 층 상수와 모멘트 통계를 잇는 근거로 추가했다.

---

## 4. op-continuum-ties-blocks

**보완할 점 1. "monotonically"를 빼고 review 정정대로 적는다.**

대응: 반영했다. ra52a3c0 review/feedback.md §5.1과 assessment의 `mode-constant-limits` 항목을 다시 읽었다. 𝔢_c/n^(1/3)(0.5521→0.5476→0.5488, 극한 0.5507)과 ε_c(−0.2972→−0.2946→−0.2957, 극한 −0.29710)는 비단조, E[Z_cH_c]는 n=400에서 미세 감소, Var·kE[H]·−2Cov−Var H·F_c는 단조; 값들은 극한과 양립하고 n≥1000에서 극한 쪽으로 움직이지만 ε_c 극한의 수치 근거는 서술보다 약하다; 주장은 "단조 수렴 서술을 뺀 발견적 예측과 수치 양립"으로 지지된다. statement는 "with which the measured values (n = 200 … 20000) are compatible, moving toward them for n ≥ 1000 though not monotonically"로, grounds는 위 수치와 review의 판정을 그대로 적었다.

**보완할 점 2. 항등식 확인 정밀도를 원자료 값(1.2×10^(−11)–6.0×10^(−10))으로 고친다.**

대응: 반영했다. ra4c01fc §9.2: 열 점 x∈{0.5,0.8,1,1.5,2,2.7312,4,6,8,10}, 상대 차 1.2×10^(−11)–6.0×10^(−10), 영점 x=0.59963에서는 절대 차 ≈4×10^(−12). grounds에 이 값과 점 목록을 적었다.

**보완할 점 3. X와 행 증가의 관계를 "한쪽 함의는 증명, 반대쪽은 표본 관찰과 비형식 전개"로 적는다.**

대응: 반영했다. r5f5cf73 §2.1 명제 2.1(증명: 2E2−B≤b_(n,c)−b_(n,c−1); X⇒행 증가, 행 감소⇒X 거짓), §2.2(k=500…25001에서 같은 정수 쌍에서 부호 전환; 전환점이 m+c_1n^(−1/3)을 따름; 관찰), §2.3 따름정리 2.4(공표 비형식 전개에 기댄 비형식 증명), 기록 자신의 "사실상"을 grounds에 그대로 적었다. 원래의 "the node X holds exactly where the row increases"는 뺐다.

**보완할 점 4(권고). r1b79fab §8의 환원(정리 C ⇒ 항등식 ⇔ 넷 이상 동률 무시)을 전제로 놓고, 이 question이 그 위에서 무엇을 더 묻는지 밝힌다.**

대응: 반영했다. statement에 "Two things are already known about this identity"라는 문단을 두어 r1b79fab §8.1 명제 R의 환원(c^(4/3)(V−B)/p_n→−f′, V=2E; 정리 C가 맞으면 항등식 ⇔ c^(4/3)(V−e_n)/p_n→0, 곧 넷 이상 동률이 창 척도에서 무시됨; e_n/V=1−O(10^(−5)), c≤16000과 정합)과 ra52a3c0 §4.3b의 발견적 식별을 전제로 적었다. 그 위에서 묻는 것을 "which events of (R,Λ) are 'two cars tie at the maximum' and 'the maximum is blocked by capacity'"로 한 문장으로 적고, 충분한 답을 (a) 정리 C 증명 또는 𝔈·𝔅의 (R,Λ) 범함수 식별, (b) 문턱↔dR 식별과 창 극한에서의 차분·미분 교환 증명, (c) H_S·H_C와의 정합, (d) 중앙 창(S=X⁽¹⁾+X⁽²⁾)에서의 같은 읽기로 나눴다. H_S·H_C는 glossary의 정의(H_S=−2[h_2f″+3h_3f′], H_C=2h_2h_2′−3h_3f′, H_S=2H_C−2h_2q_0′)를 그대로 적었다.

추가로 고친 것: ra4c01fc §9.1의 정리 C가 "전개된 증명으로 적지 않은 비형식 개요"임을 statement에서도 밝혔다.

---

## 5. op-deformation-boundary

**보완할 점 1. 변형의 범위를 정한다(원 행의 재가중, 원 과정 매개변수의 변경, 원 행의 분해 조각을 구분).**

대응: 반영했다. statement를 세 부류로 조직했다. (A) 원 행의 재가중: 꼬리 좌표 거듭제곱 r^a(r7eeaca03 §6), 로그 꼬리 좌표 강화의 n=304 반례(§7), 그리고 index 모듈이 다루는 행운 가중 x^(lucky), 총변위 기울임 q^T, 지수 가중 t^ℓ. (B) 원 과정 매개변수의 변경: 자리 n+r−1개(rd4015a8). (C) 원 행의 분해 조각: 결과 순열 섬유(r81e7051), 고정 선호 다중집합(index 모듈). 원 행 자체의 현황(P 미해결, 로그오목성의 최종 실패와 첫 실패 n=80, x^rf_X의 범위)은 따로 한 문장으로 적었다. (A)의 index 모듈 세 항목은 모듈 머리말만 읽었고 원 기록은 읽지 않았음을 grounds에 밝혔다. 특히 weighted-shapes 모듈의 "Q ⇔ 모든 t≥1에서 (t^ℓb_(n,ℓ))의 단봉성"은 재가중 가운데 실패가 아니라 동치인 예이므로, '충분한 답'이 분류해야 할 기록된 성공 쪽에 넣었다.

**보완할 점 2. 각 예에서 깨진 성질을 단봉성과 로그오목성으로 구분해 적는다.**

대응: 반영했다. 첫 문장을 "two distinct properties have been found to fail - unimodality of a row, and decreasing-side log-concavity Q"로 바꾸고 항목마다 표시했다. 섬유: 단봉성 실패(222>216<264). 거듭제곱 가중 유한 행(2<a<a_*): 가중 행의 단봉성 최종 실패. 자리 n+r−1개: Q 실패이며, rd4015a8 §6.2의 n=7, r=63 행 (19)는 엄격 감소라 단봉("what fails there is Q, not unimodality"). 원 행: 전체 로그오목성 실패(r81e7051; 첫 실패 n=80, ℓ=40). 충분한 답의 요구에도 "each labelled by the property that fails or survives (unimodality or Q)"를 넣었다.

**보완할 점 3. "exactly"를 빼고, 범위 밖에 대해서는 결론이 없음을 밝힌다.**

대응: 반영했다. r81e7051 limiting-shape.md §4의 추가 정리(−1/2<r<5/2에서 엄격 단봉; "범위의 양 끝점이나 바깥에 대해서는 여기서 결론을 내리지 않는다")대로 "strictly unimodal for −1/2 < r < 5/2 (proved)"로만 적었다. 다만 r7eeaca03 §7이 Janson의 꼬리 전개 (16)으로 "어떤 ε_0>0에 대해 모든 0<ε<ε_0의 x^(5/2+ε)f_X가 비단봉"임을 준다고 적었으므로, 그것을 그 지위로("from the published tail expansion") 덧붙이고 "nothing is settled at the endpoints or for r ≤ −1/2"로 범위 밖의 미결을 밝혔다. 가중 유한 행 쪽의 "exactly 2<a<a_*"는 r7eeaca03 §6의 표현("정확히 2<a<a_*에서 제한된 밀도 θ^ah(θ)에 골이 있으며 … 그 모든 지수에서 충분히 큰 모든 유한 가중 행이 비단봉")에 맞춰, 'exactly'는 밀도의 골에만 걸고 유한 행에는 "for every such a … eventually non-unimodal"로 적었다. a_*의 정의 (14)와 수치 ≈2.5748(peer-extensions.md: "이 소수값을 증명의 전제로 사용하지 않는다")도 그 지위로 적었다.

**보완할 점 4. 충분한 답의 판정 기준을 적는다.**

대응: 반영했다. 검토 보고가 예로 든 기준을 그대로 채택해 "either gives a single property that separates every recorded success from every recorded failure together with the reason it holds for the original process, or proves that no single property does (two recorded failures removing different properties with no common consequence for the original row)"로 적었다. 판정의 대상 집합도 "the recorded set - the items of (A)-(C) above"로 고정했다.

추가로 고친 것: rd4015a8 §9(peer)의 r_n≥n^(1+δ)에서의 최종 Q 실패, §7의 성분별 Q·역방향 우도비(n≤80 관찰)와 혼합의 Q 위반, §8의 "원 자리 n개는 이 희박한 영역이 아니므로"를 grounds에 넣었다. 원래 grounds의 "r7eeaca03 … 2 < a < a_* ~ 2.57480775688"은 위 지위 구분으로 다시 썼다.

---

## 6. 반영하지 않은 지적

없음. 「보완할 점」 열일곱 항목(op-threshold-block 4, op-tie-block-transport 3, op-layer-period 2, op-continuum-ties-blocks 4(권고 하나 포함), op-deformation-boundary 4)은 모두 원자료와 맞았고 모두 반영했다.

## 7. 합치거나 뺀 question

없음. 다섯 question은 주제를 유지했고, 보완 뒤에도 서로 다른 산출을 요구한다. 통과한 두 question과의 관계는 다음과 같다.

- op-threshold-block은 창 윤곽·지표점 일치(op-central-window)를 묻지 않고 문턱 국소 대상의 공통성만 묻는다. 창 내부는 '다른 모습을 보이는 체제'로만 다룬다.
- op-tie-block-transport의 왼쪽 판(잎별 분해)은 op-left-right-asymmetry(원인 구조 식별과 무조건화 장치의 이식)와 산출이 다르다.
- op-continuum-ties-blocks의 (d)(중앙 창에서의 같은 읽기)는 사건 식별만 요구하고, 창 윤곽의 유도는 op-central-window에 남긴다.
- op-layer-period는 거시 층 상수와 r→∞ 이행을, op-threshold-block은 국소 대상을 묻는다. D_r이 양쪽에 등장하지만 요구하는 산출이 다르다.

각 question의 마지막 문장에 이 경계를 적었다.
