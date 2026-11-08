# 보완된 첫 question 다섯 개의 재검토

판정 대상: `initial-questions.revised.json`(question 5개). 판정 기준은 처음 검토 파견문(`파견_질문검토.md`)의 2절과 3절이다. 재심의 원칙 둘을 더했다. 하나, 처음 검토의 기준으로 판정한다. 둘, 처음 검토의 「보완할 점」이 해소되었는지를 중심으로 본다. 처음 검토에서 문제 삼지 않은 부분은, 보완 과정에서 새로 생긴 결함일 때만 다시 문제 삼았다.

작성자의 `initial-questions-보완대응.md`는 작성자의 주장으로만 읽었다. 판정은 인스턴스 `parking-unimodality-fresh-20261105-150803`의 원자료로 했다. 원자료는 기록의 exposition.md와 부속 문서, review/assessment.json과 feedback.md, index 모듈, glossary, frontier다. 인스턴스 디렉터리와 원본 파일에는 쓰지 않았다.

**frontier 판.** 검토를 시작할 때 frontier는 판 184였다. 검토 중에 판 185로 바뀌었다(2026-11-09 08:07). 바뀐 내용은 둘이다. 기록 `r317289416…`이 공표되었고, node `sa285576b08e84713a85bbec88889e550-one-step-local`(Q⋆)이 생겼다. 파견문에 따라 현재 판(185)을 기준으로 중복과 형식을 확인했다.

## 0. 요약

판정한 question 5개: `op-threshold-block`, `op-tie-block-transport`, `op-layer-period`, `op-continuum-ties-blocks`, `op-deformation-boundary`.

| ID | 판정 | 주된 사유 |
|---|---|---|
| op-threshold-block | admitted | 보완할 점 넷이 모두 해소되었다. 새 결함이 없고, 근거가 원자료와 맞는다 |
| op-tie-block-transport | admitted | 보완할 점 셋이 모두 해소되었다. 새 결함이 없고, 근거가 원자료와 맞는다 |
| op-layer-period | revise | 보완할 점 둘은 해소되었다. 그러나 보완 중에 statement에 새로 넣은 문장이 r9d97cea §8.2의 고정 비율 관찰(n/k=2.5, 4, 8, k≤800)을 극 체제 n≫k^(3/2)의 관찰처럼 적었다 |
| op-continuum-ties-blocks | admitted | 보완할 점 넷(권고 하나 포함)이 모두 해소되었다. 새 결함이 없고, 근거가 원자료와 맞는다 |
| op-deformation-boundary | revise | 보완할 점 넷은 해소되었다. 그러나 보완 중에 새로 쓴 "nothing is settled at the endpoints"가 공표 기록 rc70a0941…의 정리 J와 어긋난다. 그 정리는 경계 r=5/2에서 x^(5/2)f_X의 엄격 단봉성을 증명했고, review가 지지했다 |

판정별 개수: admitted 3, revise 2, declined 0.
통과한 ID: `op-threshold-block`, `op-tie-block-transport`, `op-continuum-ties-blocks`.

**어긋남으로 센 기준.** 처음 검토와 같다. 다음 셋을 어긋남으로 셌다.
- 원자료가 반대로 말하는 것을 사실로 적은 경우.
- 원자료가 유보하거나 정정한 것을 확립된 것처럼 적은 경우.
- 원자료가 보여 주지 않는 것을 보여 준다고 적은 경우.

statement의 사실 전제도 같은 방식으로 다루었다. 출처가 느슨하거나 숫자가 조금 어긋나도 뜻이 바뀌지 않으면 참고로만 적었다.

**형식(다섯 개 공통).** 다섯 ID 모두 `op-`로 시작한다. 소문자·숫자·하이픈만 쓰고, 목록 안에서 고유하며, `q0`이 아니다. frontier 판 185의 node ID와 겹치지 않는다. node ID는 `root`, `s<hex>-…` 꼴이고 새 node `sa285576…-one-step-local`도 포함해 확인했다. 이미 통과한 `op-central-window`, `op-left-right-asymmetry`와도 겹치지 않는다. 열 개 필드(statement·grounds ×5)는 모두 ASCII만 쓴 영어다. 아래 개별 항목에서는 "형식: 이상 없음"으로만 적는다.

**새 node와의 중복(다섯 개 공통).** 판 185에서 생긴 node Q⋆는 다음 범위의 부호 명제다: 모든 k≥2001, max(2k+103,20001)≤t≤⌈2k^(3/2)⌉−1에서 src_k(t)+FL_k(t)≥0. 다섯 question 가운데 이 부호나 범위를 다시 묻는 것은 없다.

---

## 1. op-threshold-block — admitted

### 처음 「보완할 점」의 해소

1. **전제를 k^(−1/3) 여유가 보인 체제로 한정한다: 해소.** 첫 문장이 "In four regimes the records show … a relative margin of order k^(−1/3)"로 바뀌었다. 네 체제와 각 지위가 원자료와 맞는다.
   - 중앙: rce3dc75 §10("두 큰 항의 선도 상수 4I/√π는 같고, 상대 차는 (2/I)k^(−1/3)뿐")과 r6b37c7e §5.2 표.
   - 첫 층: r9d97cea §6.4 peer 정리 B. 상대 여유 (m(λ)+o(1))k^(−1/3)이고 비형식 증명이다.
   - 둘째 층: r6b37c7e 추측 6.3과 §6.4–6.5. min m_3≈15.34이고 추측이다.
   - 오른쪽 창: ra4c01fc §10.1. 부족분 D(x̂)c^(−1/3), D≈5–9.5이고 비인증 binary64다.

   "universal"은 빠졌다.
2. **창 내부와 극 체제는 다른 모습을 보이는 곳으로 밝히고, 그 차이를 질문에 넣거나 대상에서 뺀다: 해소(질문에 넣는 쪽).** statement는 두 체제를 "look different in the records and are not assumed to share this premise"로 따로 적었다.
   - 창 내부: r6b37c7e §6.6과 맞는다. R은 k에 무관한 R_∞(t)로 가고, t≈4에서 최대 ≈2.25이며, 여유는 O(1)이다.
   - 극 체제: r10ff8c2 §5.1과 맞는다. E≈κ_kn이고 E²이 압도한다.

   충분한 답도 "same local object … or genuinely different objects"를 판정하라고 요구한다.
3. **극 체제의 '문턱 인접 성분'이 무엇인지 정한다: 해소.** statement는 그것을 "prime blocks of size just BELOW k, in a boundary layer of width k/σ_k"로 정했다. rf451d83 §3.1과 맞는다.
   - 몸통 n≤k의 인자 e^(σ_kn/k)가 n≈k 근처 폭 ≈k/σ_k의 경계층에 질량을 모은다.
   - n>k 꼬리의 질량은 0.176(k=501)에서 0.138(k=10^5)로 준다.

   "용량 바로 위 성분·k^(1/3) 질량·k^(−1/3) 여유는 보이지 않는다"는 서술도 rf451d83 §3.1–3.3과 r10ff8c2 §5.1에 맞는다.
4. **k^(2/3) 멈춤 깊이와 k^(1/3) 끝점 거리를 구분한다: 해소.** 두 척도를 따로 적고 "a local law must resolve both"를 넣었다.
   - 멈춤 깊이: ra52a3c0 §5와 맞는다. 손실 kE[H_k]의 92–95%가 k+0.5k^(2/3) 이하까지 내려간 사슬에서 나오고, D*=0.542k^(2/3)이며, 생산자의 발견적 그림이다.
   - 끝점 거리: r20df549 §3.6b와 맞는다. r*≈0.63k^(1/3)은 발견적 예측이고, 관측값은 1, 4, 8, 13이다.

   처음 grounds의 "that close"는 없어졌다.

### 보완 과정에서 새로 생긴 결함: 없음

참고로 두 가지를 적는다. 어긋남으로 세지는 않았다.
- 오른쪽 창은 "relative margin of order k^(−1/3)"인 네 체제의 하나로 묶였다. 그런데 ra4c01fc §10.1에서 그 창의 여유 자체는 O(1)이다(창 1.4≤x̂≤10, c≥10^4에서 e_n/B≥1.5). k^(−1/3) 차수인 것은 극한 여유와의 부족분이다. statement는 바로 이어 "the margin falls short of its universal limit by D(x̂)c^(−1/3)"라고 정확히 적었다. 이 체제를 넣으라는 것은 처음 검토가 권고한 것이다.
- "carried by one component that lands within O(k^(2/3)) above the capacity k (informal proof)"에서 '착지'라는 경로 해석은 r9d97cea §6.3에서 증명되지 않았다. 그러나 (6.4)와 정리 I이 j=k+tk^(2/3)인 무거운 꼭짓점 하나와 그 아래 k^(1/3) 군집을 비형식적으로 준다. grounds도 "the landing-path interpretation … is stated as not proved"라고 밝혔다. 뜻이 바뀌지 않는다.

### 근거의 정확성: 어긋남 없음

| 기록 | 원자료에서 본 것 | 판단 |
|---|---|---|
| rce3dc75 §10 | e_n과 J_n(k−1)의 선도 상수 4I/√π가 같고, 상대 차는 (2/I)k^(−1/3) | 맞음 |
| r6b37c7e §5.2 | (R−1)k^(1/3)=2.63, 2.46, 2.39 (k=10^4, 4·10^4, 8·10^4). §6.2는 2/I_0=2.130으로 내려가는 중이라고 적음 | 맞음 |
| r9d97cea §6.3–6.4 | (6.4) Pr(H_j=1)=D_λk^(−2/3)J(t)S(t)(1+o(1)). 정리 I. k^(2/3)EH_k, k^(−1/3)E(Z)_2→D_λI_0. 정리 B의 (m(λ)+o(1))k^(−1/3). "이 경로 해석 자체는 증명하지 않았다". "고정 λ와 중앙 사이의 균등 정리는 주장하지 않는다" | 맞음 |
| r9d97cea §8.1 | 중앙 n∈{2k−1,2k}: E Z가 k^(1/3) 규모(군집 하나) | 맞음 |
| r6b37c7e §6.1–6.3 | 명제 6.1 d=Conv−Kink(증명). D_λ=경계 흐름(증명). 추측 6.3. 명제 6.2(공표 비형식 입력 위의 증명) | 맞음 |
| r6b37c7e §6.4(d) | 두 층의 문턱 윤곽 비 1.854, 1.845, 1.838, 1.833 → D_3/D_λ=1.824. 각 윤곽보다 훨씬 빨리 자리 잡음(관찰) | 맞음 |
| r6b37c7e §6.5 | min m_3≈15.34 (λ≈0.392, r≈2.55). 명제 6.4의 9/(8I_0), 1/(3I_0) | 맞음 |
| r6b37c7e §6.6 | R_∞(t). t≈4에서 최대 ≈2.25. t∈[t_0,T]에서 O(1) 여유. "극한 함수를 … 구하는 일은 하지 않았다" | 맞음 |
| ra4c01fc §10.1 | D(x̂)c^(−1/3), D≈5–9.5(비인증 binary64). 중앙 (2/I)c^(−1/3) | 맞음 |
| r10ff8c2 §5.1 | 극 영역 n≫k^(3/2)에서 E≈κ_kn, E²이 압도 | 맞음 |
| rf451d83 §3.1–3.3 | 경계층(몸통 n≤k), 꼬리 질량 0.176→0.138. 주기 ≈k 진동. kθ≈2π의 골, 깊이 ≈1.5/σ_k(관찰) | 맞음 |
| ra52a3c0 §5 | 92–95%가 k+0.5k^(2/3) 이하에서. D*=0.542k^(2/3). "증명이 아닌 계산과 해석" | 맞음 |
| r20df549 §3.5, §3.6b | 보조정리 3.2(증명). h_π(0)=1/e. r*≈0.63k^(1/3)은 "모형에서 나온 발견적 예측". 관측 r*=1, 4, 8, 13 | 맞음 |
| r1b79fab §6.3 | 명제 2(비형식, 약한 판). d가 (8/√π)f_S를 따름 | 맞음 |

**형식:** 이상 없음.

**통과한 두 question과의 중복: 없음.**
- op-central-window와의 관계: 이 question은 창 내부를 "다른 모습을 보이는 체제"로만 다룬다. 그곳의 국소 대상이 같은지 다른지만 묻는다. op-central-window가 묻는 것은 창의 윤곽(d, μ, R, ρ)과 지표점 일치와 t→0의 공통 원인이다. 산출이 다르다. 경계 문장도 적혀 있다.
- op-left-right-asymmetry와는 주제가 닿지 않는다.

**참고(판정과 무관).** 이 question을 점유할 탐색 세션은 기록 둘을 함께 읽으면 좋다. 둘 다 이 question이 인용하지 않은 공표 기록이다.
- r359ba037…(왼쪽 창 '두 모멘트 상쇄'): §4.4는 중앙 n=2k의 여유를 배경×군집 교차항으로 읽는다. 중앙 상수 2/μ=2·1·(1/μ)이고, 군집 크기는 r2d892ef2…/central-capacity-law의 Gamma 법칙을 따른다. §4.7의 정합 공식은 오른쪽 벌크, 중앙, 왼쪽 띠를 잇는다.
- r317289416…(판 185): §6.5에서 중앙 옆 띠의 두 척도 그림을 다룬다.

중앙의 국소 법칙은 이미 일부 알려진 셈이다. 그러나 "여러 체제의 국소 대상이 같은가"라는 이 question의 핵심을 이 기록들이 답하지는 않는다.

---

## 2. op-tie-block-transport — admitted

### 처음 「보완할 점」의 해소

1. **H 절편 문장을 원자료대로 고친다: 해소.** statement는 이렇게 바뀌었다: "the h = 0 slice is always ≥ 0 while h ≥ 1 slices turn negative well before the mode, and the site-wise comparison already fails at site k: the positivity is a global compensation that no H-preserving slice-wise or site-wise injection can exhibit". 원자료와 맞는다.
   - ra52a3c0 §6: h=0 절편은 항상 ≥0이다. h≥1 절편은 최빈점 훨씬 전부터 음수다. 자리별 비교는 i=k에서 깨진다.
   - feedback §5.2: 결론은 "H를 보존하는 절편별 비교나 자리별 비교로는 불가능"으로 읽어야 한다.

   grounds도 review의 n=25 정정(h=1은 k≥10에서, 어떤 h≥1 절편은 모든 2≤k≤24에서 음수)을 그대로 옮겼다.
2. **r*≈0.63k^(1/3)은 발견적 예측으로, −,+,− 모양은 큰 n의 관찰로 지위를 밝힌다: 해소.** statement가 지위를 넷으로 나누어 적었고, r20df549 §3.6과 §3.6b의 표시와 맞는다.
   - 증명: 끝점 분해와 위험률 극한.
   - 관찰: λ∈{0.6,0.7,0.8}, n≤3·10^4의 binary64.
   - 정확 인증: (300,210), (600,420), (1000,700).
   - 발견적 예측: r*≈0.63k^(1/3). 필요한 상계가 미증명이라는 점도 적었다.

   작은 n의 "+−" 우세(1610곳 가운데 1277곳, §3.3)도 넣어 세 단계 모양이 큰 n의 현상임을 밝혔다.
3. **찾거나 배제하려는 '국소 수송'의 종류를 정한다: 해소.** (i)에 세 층위를 정했다.
   - 가장 좁은 뜻: 같은 사슬의 마지막 걸음만 바꾸는 짝짓기. 끝점 이동은 O(1) 또는 o(k^(1/3))이다. r20df549 §7의 제안과 같다.
   - 넓은 뜻: 끝점 이동이 손실 띠의 폭 O(k^(1/3))인 수송.
   - 비국소: ≫k^(1/3)을 건너거나 다른 전역 구조 사이로 옮기는 수송.

   충분한 답의 배제 쪽도 "no transport with endpoint displacement O(k^(1/3)) exists"로 구체화했다.

### 보완 과정에서 새로 생긴 결함: 없음

참고로 한 가지를 적는다. (ii)의 뒷부분 "does that exclude every argument that loses a constant factor locally?"는 이미 r20df549 §5.1이 답을 적은 물음이다. 그 절은 생산자의 결론 "국소 수술로 상수 비율의 손실을 감수하는 단사 증명은 벌크에서 닫힐 수 없다"가 여유가 0으로 가는 한 성립한다고 적었다. 사실을 잘못 적은 것은 아니고 부속 물음이 거의 자명해진 것뿐이다. 어긋남으로 세지 않았다.

### 근거의 정확성: 어긋남 없음

| 기록 | 원자료에서 본 것 | 판단 |
|---|---|---|
| r20df549 §3.2 | 정리 3.1(증명). k+1≤n≤2k−1. n≤110의 2969곳에서 정확 검산. n=2k, 2k+1에서 실패 | 맞음 |
| r20df549 §3.3 | 증가 쪽 1610곳 가운데 "+−" 1277곳, "−+−" 333곳(모두 n≥49, 최빈점 쪽). 가장 얕은 급은 늘 음수 | 맞음 |
| r20df549 §3.4–3.5 | D(m)>0⟺g>Ψ/Φ. g≈E[N(N−1)]/k. 보조정리 3.2: h_π(0)=1/e, h_π(1)=0.21410, h_π(r)~1/(2r) | 맞음 |
| r20df549 §3.6 | λ=0.7에서 r*=1, 4, 8, 13. "'g→0'과 세 단계 모양의 지속은 … 발견적 설명" | 맞음 |
| r20df549 §3.6b | kD(k)/A=−0.949, −2.500, −4.150. 깊이 법칙 모형. r*≈0.63k^(1/3)은 "발견적 예측이며 증명이 아니다". 상계 E[(N−1)²ρ^N\|끝점]=O(k^(2/3))는 미증명 | 맞음 |
| r20df549 §5.1, §7 | 상대 여유 n^(−1/3). 급 사이 수송은 열린 질문이고 "거의 전단사여야". 잎별 분해는 시도하지 않음 | 맞음 |
| ra52a3c0 §6, feedback §5.2 | 위 1의 내용. Z≤1 절편은 늘 ≤0 | 맞음 |
| r475ada §7의 3 | 왼쪽 손실은 B≤J^G에 있음. '𝒦″의 초과 대 B의 초과'(처음 검토에서 확인, 문구 불변) | 맞음 |
| r9d97cea §8.2 | n>2k의 측가지. 정리 R1. Ψ의 점근 해석은 남음 | 맞음 |

**형식:** 이상 없음.

**통과한 두 question과의 중복: 없음.** op-left-right-asymmetry와 같은 왼쪽 나무 구조를 다루지만 산출이 다르다.
- op-left-right-asymmetry: 두 절반을 가르는 원인 구조와 무조건화 장치의 이식을 묻는다.
- 이 question의 (iii): 사슬 끝점 급을 대신할 잎별 분해와 그 두 성분 부호 판정을 묻는다.

경계 문장도 적혀 있다.

**참고(판정과 무관).** 판 185에 공표된 r317289416…은 이 question이 인용하지 않은 기록이다. 그 기록은 왼쪽 창의 상대 둘째 차분을 Cartesian 나무의 꼭짓점별 원천으로 쓴다. 음의 원천은 문턱 뿌리 블록에서만 나오고, k·src_k(k+d)→−β_(d+1)(Borel 질량)이다. (iii)의 '왼쪽 판'과 직접 닿는 결과다. 이 question을 점유할 탐색 세션은 그 기록에서 출발해야 한다. 판정에는 넣지 않았다. 이 question의 사실 진술은 그 기록과 어긋나지 않는다(grounds의 "not attempted"는 r20df549에 한정한 진술이다). (iii)이 묻는 '같은 두 성분 판정과 수송'도 그 기록이 답하지 않는다.

---

## 3. op-layer-period — revise

### 처음 「보완할 점」의 해소

1. **내부 최솟값과 μ 단조성 실패의 지위를 원자료대로 적는다: 해소.** statement가 r별로 나누어 적었다.
   - r=2: λ*_2=0.6435, 닫힌 꼴.
   - r=3: λ*_3=0.4240, 구간 인증.
   - r=4: λ*_4≈0.308은 수치이고, 내부 최솟값은 발견적 국소 해석에 기댄다. M_4는 위 끝에서 ε^(−3/2)로 발산한다.
   - r≥5: 미지.
   - r≥6: 위 끝 특이성이 유계일 수 있어 끝점 논법이 통하지 않을 수 있다.

   기제("born/disappears")는 r=2,3에서 확립(정리 B, 비형식), r=4는 수치에 조건부, 그 너머는 열림으로 적었다. 이 지위는 r1b79fab의 다음 절과 맞는다.
   - §5.1: λ*_4는 "인증 아님".
   - §5.2: 귀결 B₄는 "수치 입력에 조건부", "예측"이다.
   - §5.3: "r=2,3에서는 이것이 정확히 성립한다".
   - §10: "발견적 결론", "r≥6에서는 … 끝점 논법만으로는 따르지 않는다".
   - §12의 3: "일반 r≥5에서 … 모른다".

   grounds의 §10 인용도 범위 제한으로 바르게 고쳤다.
2. **r≥4 부분이 그 미지를 직접 묻게 한다: 해소.** 질문에 넣은 것: "do M_r and m_r keep an interior minimum and does the k^(−1/3) margin scale persist when the upper-end singularity of Φ_r weakens (r≥6)". 충분한 답에 넣은 것: "settles the existence of interior minima of M_r and m_r for r≥4 (at least deciding r=4 rigorously)".

### 보완 과정에서 새로 생긴 결함: 있음(근거의 정확성 어긋남)

statement의 다음 문장은 보완 중에 새로 들어갔다.

> "… in the pole regime n >> k^(3/2) the same period-k structure reappears as the second zero pair of the prime-block renewal, whose gap delta* sigma_k^2 = 33-47 at k <= 10^5 is still far from the asymptotic 2 pi^2, **and the mean matches the one-pole formula (N/k) kappa_k - 1 with the logarithmic growth of E[Z] confined to the cell j/k in [1, 1.25).**"

굵게 표시한 부분은 "in the pole regime n >> k^(3/2)" 절 안에 놓여 있다. 그래서 극 체제의 관찰로 읽힌다. 그런데 출처 r9d97cea §8.2가 보여 주는 것은 다른 체제의 관찰이다.

- **체제가 다르다.** §8.2의 자료는 "수치 지도(binary64; x=n/k=2.5, 4, 8, k≤800)"다. 고정 비율 n/k≤8이다. 이 자료의 모든 점은 극 체제 밖에 있다. k=800이면 n≤6400<k^(3/2)≈22600이고, k=100이어도 n≤800<1000이다. "로그 성장이 j/k∈[1,1.25) 칸에 있다"는 관찰도 x=4에서 k=100→800일 때 4.31→9.30이라는 고정 비율의 k-성장이다.
- **적합도 단서가 빠졌다.** 같은 절은 한 극점 공식이 "x=8에서 10^(−4), x=4·2.5에서 0.07–0.25 벗어남"이라고 적었다. statement는 이 차이를 빼고 "matches"로만 적었다. grounds는 "on the left … within 10^(−4) at n/k = 8, off by 0.07-0.25 at n/k = 4, 2.5"라고 바르게 적었다. statement와 grounds가 서로 어긋난다.
- **질문의 핵심에 닿는 어긋남이다.** 이 question이 묻는 것은 층 서술에서 갱신(극) 서술로의 이행이다. 그런데 고정 비율에서 한 극점 공식이 얼마나 맞기 시작하는지, 그리고 그 맞음이 x=2.5, 4에서 x=8로 가며 좋아진다는 것은 바로 그 이행에 대한 관찰이다. statement는 이 관찰을 극 체제의 사실로 옮겼다. 그러면 탐색 세션은 이행에 대한 단서를 극 체제 안의 기정사실로 받게 된다. 출처를 느슨하게 단 정도가 아니라 뜻이 바뀐다고 판단했다.

r9d97cea §8.1 표가 적은 극 체제의 한 극점 평균((n+1)kΛ′(k+)−1, 공표 rd8b6…·ra4cb6…)만 가리켰다면 맞는 진술이었다. 그러나 문장이 붙인 j/k∈[1,1.25) 칸 관찰과 "matches"는 §8.2의 고정 비율 자료다.

### 근거의 정확성: 어긋남 있음(위 한 곳). 나머지는 맞음

| 기록 | 원자료에서 본 것 | 판단 |
|---|---|---|
| r24b9bf1 §5 | "이 단조 밀도 논법은 정확한 둘째 차분 극한을 주지는 않는다". hierarchy-convexity는 review가 지지한 증명 | 맞음 |
| r1b79fab §5.1–5.3, §10, §12의 3 | 위 1의 내용. Φ_4(1/3−)≈14.3 유한, Φ_4″≍ε^(−3/2), Φ_5″≍ε^(−1/2), r≥6 꼭짓점 기여 유계(모서리 미확인) | 맞음 |
| r6b37c7e §6.2–6.5, §6.8 | D_λ=경계 흐름(증명). m(1/2+)=2/I_0. 추측 6.3. 명제 6.2. 표의 κ_3, D_3, m_3. 명제 6.4. 지수 규칙. min m_3≈15.34. 층 번호가 자라는 경우는 "하지 않았다". 2001≤k≤9949 열 | 맞음 |
| r10ff8c2 §5.3, §5.4, §5.7 | n_J≈2.1k–3.6k. 주기 ≈k 진동. T_n 감소(k=25600, n/k 2.105→2.556). 연속 근사 T≈κ_r | 맞음 |
| rf451d83 §3.2–3.3 | δ*σ_k²=32.8–47.3 (k=501…10^5) 대 2π²≈19.7. "반례는 아니다". 공명 골 kθ≈2π | 맞음 |
| r9d97cea §8.2 | 고정 비율 x=2.5, 4, 8(k≤800)에서 E Z≈(N/k)κ_k−1(x=8에서 10^(−4), x=4·2.5에서 0.07–0.25). 로그 성장은 j/k∈[1,1.25). 왼쪽 문턱 밀도의 t 모양은 J(t)S(t)에 비례하지 않음. Ψ의 점근은 열림 | grounds는 맞음. **statement는 극 체제로 옮겨 적어 어긋남** |

참고로 한 가지를 적는다. 어긋남으로 세지는 않았다. statement의 "the end-of-layer constants 9/(8 I_0) and 1/(3 I_0) and an exponent rule are proved"와 grounds의 "section 6.5 Proposition 6.4 (proved): …, the end-of-layer exponent rule …, min m_3 ~ 15.34 …"는 지위 표시가 조금 넓다. 지수 규칙은 명제 6.4 자체가 아니다. 그것은 "두 도함수까지 거듭제곱 꼴을 따르면"이라는 조건 아래의 계산이고, 기록은 다루는 네 끝 모두 그 조건을 만족한다고 적었다. min m_3≈15.34는 격자 수치다. 다만 statement에서 15.34는 "conjecture with measurements"의 괄호 안에 있고, 두 끝 상수는 명제 6.4가 증명한다. 그래서 뜻이 바뀐다고 보지 않았다.

**형식:** 이상 없음.

**통과한 두 question과의 중복: 없음.** op-left-right-asymmetry는 m_3이 중앙에서 1.198/δ로 발산하고 첫 층은 유한하다는 비대칭을 근거로 쓴다. 이 question은 r≥4와 r→∞의 층 상수와 극 체제로의 이행을 묻는다. 산출이 다르다. op-central-window와는 주제가 닿지 않는다.

### 보완할 점

1. 굵게 표시한 문장을 극 체제 절에서 떼어 낸다. 그 관찰의 체제와 적합도를 statement에 그대로 적는다: 고정 비율 n/k=2.5, 4, 8, k≤800, binary64이고, 한 극점 공식과의 차는 n/k=8에서 10^(−4), n/k=4, 2.5에서 0.07–0.25다. j/k∈[1,1.25) 칸 관찰도 같은 고정 비율 자료로 적는다.
2. 극 체제의 평균이 한 극점 공식으로 주어진다는 사실을 따로 쓰려면 그 출처를 r9d97cea §8.1 표(공표 rd8b6…·ra4cb6…)로 단다.
3. 지수 규칙과 min m_3의 지위를 명제 6.4와 구분해 적는다. 지수 규칙은 거듭제곱 꼴을 가정한 계산이고, 네 끝에서 그 가정이 확인되었다. min m_3은 격자 수치다(권고).

이 question의 주제와 구체성, 비중복은 그대로 충족한다. 위 1만 고치면 통과 수준이다.

---

## 4. op-continuum-ties-blocks — admitted

### 처음 「보완할 점」의 해소

1. **"monotonically"를 빼고 review 정정대로 적는다: 해소.** statement는 "compatible, moving toward them for n ≥ 1000 though not monotonically"로 적었다. grounds는 ra52a3c0 feedback §5.1과 assessment의 claim `mode-constant-limits` 정정을 그대로 적었다. 적힌 수치는 원자료와 맞는다.
   - 𝔢_c/n^(1/3): 0.5521→0.5476→0.5488, 극한 0.5507.
   - ε_c: −0.2972→−0.2946→−0.2957, 극한 −0.29710.
   - E[Z_cH_c]는 n=400에서 미세하게 감소한다.
   - Var Z_c, kE[H_c], −2Cov−Var H, F_c는 단조다.
   - review의 판정: ε_c 극한의 수치 근거는 서술보다 약하다. "발견적 예측과 수치 양립"으로 지지한다.
2. **항등식 확인 정밀도를 원자료 값으로 고친다: 해소.** grounds의 값이 ra4c01fc §9.2와 맞는다. 열 점 x∈{0.5, 0.8, 1, 1.5, 2, 2.7312, 4, 6, 8, 10}에서 상대 차 1.2×10^(−11)–6.0×10^(−10)이고, 영점에서는 절대 차 ≈4×10^(−12)다.
3. **X와 행 증가의 관계를 "한쪽 함의는 증명, 반대쪽은 관찰과 비형식 전개"로 적는다: 해소.** grounds가 r5f5cf73의 내용을 지위대로 적었다.
   - §2.1 명제 2.1: 2E2_(n,c)−B_(n,c−1)≤b_(n,c)−b_(n,c−1)(증명). 그래서 X⇒행 증가이고, 행 감소⇒X 거짓이다.
   - §2.2: 반대쪽은 관찰이다.
   - §2.3 따름정리 2.4: 공표 비형식 전개에 기댄 비형식 증명이다.
   - 기록 자신이 "사실상"이라고 쓴다는 점도 적었다.

   처음의 "holds exactly where the row increases"는 없어졌다.
4. **(권고) r1b79fab §8의 환원을 전제로 놓고 그 위에서 무엇을 더 묻는지 밝힌다: 해소.** statement의 "Two things are already known about this identity" 문단이 두 가지를 전제로 놓았다. 그 위에서 묻는 것을 "which events of (R, Λ) are 'two cars tie at the maximum' and 'the maximum is blocked by capacity'"로 한 문장으로 적었다. 충분한 답도 (a)–(d)로 나누었다.
   - 명제 R(R1)에서 c^(4/3)(V−B)/p_n→−f′다. 따라서 정리 C가 맞으면, 항등식은 넷 이상 동률이 창 척도에서 무시된다는 명제와 동치다.
   - ra52a3c0 §4.3b의 발견적 식별.

### 보완 과정에서 새로 생긴 결함: 없음

statement에 "Theorem C (informal outline, not written out)"가 새로 들어갔다. ra4c01fc §9.1("생산자는 이 개요를 전개된 증명으로 적지 않았다")과 맞는다. (c)의 H_S, H_C 식은 glossary 정의와 같다.

### 근거의 정확성: 어긋남 없음

| 기록 | 원자료에서 본 것 | 판단 |
|---|---|---|
| ra4c01fc §9.1–9.2 | 정리 C의 극한식 c^(4/3)B/p_n→𝔅/(2π), c^(4/3)e_n/p_n→𝔈/π. 비형식 개요. 극한 여유의 영점 x̂_0=0.59963, x̂=2.7312에서 최대 2.2218, ≈8.3/x̂. (9.1)은 "증명하지는 않았다" | 맞음 |
| r1b79fab §8.1 | 명제 R의 (R1)–(R4). 정리 C가 맞으면 (9.1)⇔c^(4/3)(V−e_n)/p_n→0. c≤16000에서 e_n/V=1−O(10^(−5)) | 맞음 |
| r1b79fab §8.2 | m=0.599625, x_f=1.282169, x_μ=1.803587. [0.25,2.5]의 구간 인증 | 맞음 |
| ra52a3c0 §4.3b | φ=0.55072, V=0.19013, q_0/h_0=0.49342, q_1/h_0=0.44299. 극한값 0.14589, −0.29710, −0.34251. "식별 단계 … 증명하지 않았다" | 맞음 |
| ra52a3c0 feedback §5.1, assessment `mode-constant-limits` | 위 1의 내용 | 맞음 |
| r5f5cf73 §2.1–2.3 | 위 3의 내용. k=500…25001에서 같은 정수 쌍에서 부호 전환. c_1∈(1.24846,1.24848) | 맞음 |
| glossary H_S(r0dc57fa…), H_C(r3e8c952…) | H_S=−2[h_2f″+3h_3f′]. H_C=2q_1h_2−3h_3q_0=2h_2h_2′−3h_3f′. H_S=2H_C−2h_2q_0′ | 맞음 |
| r1b79fab §6.3 | 중앙 창의 S=X⁽¹⁾+X⁽²⁾ 밀도(명제 2, 비형식) | 맞음 |

**형식:** 이상 없음.

**통과한 두 question과의 중복: 없음.** (d)의 내용은 중앙 창에서 같은 사건 식별이 무엇을 주는지다. 이것은 op-central-window의 "두 성분 극한 법칙에서 창 윤곽을 유도"와 주제가 닿는다. 그러나 (d)는 사건 식별만 요구하고, 윤곽의 유도와 지표점 일치는 op-central-window에 남겨 두었다. 경계 문장도 적혀 있다. 이 question의 핵심은 오른쪽 임계 창의 두 개수를 (R, Λ)의 사건으로 식별하는 일이고, 고유하다. op-left-right-asymmetry와는 주제가 닿지 않는다.

---

## 5. op-deformation-boundary — revise

### 처음 「보완할 점」의 해소

1. **변형의 범위를 정한다: 해소.** statement가 변형을 세 부류로 조직했다. 원 행 자체의 현황은 따로 적었다. 판정할 대상 집합도 "the recorded set - the items of (A)-(C) above"로 고정했다.
   - (A) 원 행의 재가중: r^a, 로그 꼬리 좌표, 행운 가중, q^T, t^ℓ.
   - (B) 과정 매개변수의 변경: 자리 n+r−1개.
   - (C) 원 행의 분해: 결과 순열 섬유, 고정 선호 다중집합.
2. **각 예에서 깨진 성질을 단봉성과 Q로 구분한다: 해소.** 첫 문장이 "two distinct properties … unimodality of a row, and decreasing-side log-concavity Q"로 바뀌었다. 처음 지적된 세 예는 모두 바르게 구분되었다.
   - 섬유: 단봉성 실패.
   - r^a 가중 유한 행: 가중 행의 단봉성 최종 실패.
   - 자리 n+r−1개: Q 실패. n=7, r=63 행은 엄격 감소라 단봉이다(rd4015a8 §6.2).
   - 원 행 전체: 로그오목성 실패.

   새로 더한 항목 가운데 행운 가중과 q^T 기울임은 statement에 무엇이 깨지는지 적지 않았다. 다만 grounds가 적었다: 행운 가중은 x=n/c의 가중 골, q^T는 각 칸 로그볼록성과 Q 실패다. 충분한 답도 각 항목에 성질을 붙이라고 요구한다. 그래서 해소로 보았다(참고).
3. **"exactly"를 빼고, 범위 밖에는 결론이 없음을 밝힌다: "exactly"는 빠졌다. 그러나 새로 쓴 범위 밖 서술이 원자료와 어긋난다(아래 새 결함).** r^a 쪽의 "exactly 2<a<a_*"는 r7eeaca03 §6의 표현대로 극한 밀도의 골에만 걸었다. 유한 행에는 "for every such a … eventually non-unimodal"로 바르게 적었다.
4. **충분한 답의 판정 기준을 적는다: 해소.** 처음 검토가 예로 든 기준을 채택했다. 하나는 "a single property that separates every recorded success from every recorded failure together with the reason it holds for the original process"이고, 다른 하나는 그런 성질이 없음을 보이는 것이다. 없음을 보이는 경우의 형태도 정했다(서로 다른 성질을 없애고 원 행에 공통 귀결이 없는 두 실패).

### 보완 과정에서 새로 생긴 결함: 있음(근거의 정확성 어긋남)

statement에 새로 쓴 다음 문장이 원자료와 어긋난다.

> "… the power-weighted limit density x^r f_X is strictly unimodal for -1/2 < r < 5/2 (proved) and non-unimodal for 5/2 < r < 5/2 + eps_0 (from the published tail expansion); **nothing is settled at the endpoints** or for r <= -1/2."

- 공표 기록 rc70a0941…(「최대 변위의 임계 크기 전이와 모든 고정 차수의 부호 장애」) §6에 정리 J가 있다: "기존 x^αf(x)의 α<5/2 단봉성을 경계로 보내 w=x^(5/2)f가 유일한 유한 모드를 가지며 양쪽에서 엄격히 증감함을 증명한다". review는 assessment의 claim `boundary-weighted-density-unimodality`를 "supported"로 판정했다(feedback §6). 도함수의 고립 영점 가능성을 남긴 약한 부호 진술이라는 단서가 붙어 있다.
- 따라서 끝점 r=5/2는 정리되어 있다. 경계에서도 엄격 단봉이다. "nothing is settled at the endpoints"는 원자료가 정한 것을 정해지지 않았다고 적은 것이다. 미결로 남은 것은 r=−1/2와 r<−1/2뿐이다.
- 작성자가 읽었다고 적은 index 모듈 `weighted-shapes-and-log-coordinates`의 머리말에도 "−1/2<a<5/2의 연속 가중 밀도 엄격 단봉성과 경계 a=5/2의 유일 모드"가 있다. 같은 모듈의 rc70a0941 항목은 "경계 가중 밀도 x^(5/2)f의 엄격 단봉성을 증명했다"고 적었다.
- 이 문장은 이 question이 묻는 "단봉성의 경계가 어디인가"에 직접 닿는다. 탐색 세션이 이미 정리된 경계점을 미결로 알고 출발하게 된다. 그래서 뜻이 바뀐다고 판단했다.
- 이 결함은 처음 검토의 보완할 점 3("범위 밖에 대해서는 결론이 없음을 밝힌다")을 따르는 과정에서 생겼다. 처음 검토의 그 문구는 r81e7051 limiting-shape.md §4 한 기록만 보고 쓴 것이다. 그 절의 "범위의 양 끝점이나 바깥에 대해서는 **여기서** 결론을 내리지 않는다"는 그 기록 안에 한정한 진술이다. 작성자는 범위 밖 한쪽(5/2<r<5/2+ε_0)은 r7eeaca03 §7로 바로잡았다. 그러나 끝점은 기록 전체의 미결로 바꾸어 적었다. 그래서 보완 과정에서 새로 생긴 결함으로 셌다. grounds의 r81e7051 인용("no conclusion is drawn here …")은 그 기록에 한정되어 있으므로 정확하다. 어긋남은 statement에 있다.

### 근거의 정확성: 어긋남 있음(위 한 곳). 나머지는 맞음

| 기록 | 원자료에서 본 것 | 판단 |
|---|---|---|
| r81e7051 exposition | σ=(1,2,3,5,4,6,7)의 섬유 (1,31,130,222,216,264,144). b_7은 단봉. 모든 n≥7의 비단봉 섬유. 포화. 충분히 큰 n의 비로그오목성(비명시). n≤120 단봉성. 첫 로그오목성 실패 n=80, ℓ=40 | 맞음 |
| r81e7051 limiting-shape.md §4 | −1/2<r<5/2의 엄격 단봉성. "범위의 양 끝점이나 바깥에 대해서는 여기서 결론을 내리지 않는다" | grounds의 인용은 맞음 |
| rc70a0941 §6 정리 J, assessment `boundary-weighted-density-unimodality` | x^(5/2)f의 유일한 유한 모드와 양쪽 엄격 증감. review 지지 | **statement의 "nothing is settled at the endpoints"와 어긋남** |
| r7eeaca03 §6, peer-extensions.md | θ^ah(θ)의 골은 정확히 2<a<a_*. a_*>18/7. ≈2.57480775688은 "증명의 전제로 사용하지 않는다". 그 모든 a에서 유한 가중 행은 결국 비단봉. 정리 E2는 역을 주장하지 않음 | 맞음 |
| r7eeaca03 §7 | n=304의 정확한 골. 원 개수는 감소이므로 P·Q의 반증이 아님. n=269, r=133. Janson 전개로 x^(5/2+ε)f_X 비단봉(0<ε<ε_0) | 맞음 |
| rd4015a8 §6–9 | a_(n,k)=C(n,k+1)(k+1)^(k−1). η_k<1(τ_m의 엄격 로그볼록성). 정리 C(n≥7, r≥64n³, 64n³은 최적 아님). n=7, r=63 행 (19)는 엄격 감소이고 Q 실패. §7 성분별 Q와 역방향 MLR(n≤80 관찰), 그러나 혼합은 Q 위반. §8 "원 Q로 옮길 수 없다". §9 r_n≥n^(1+δ)에서 최종 Q 실패 | 맞음 |
| index 모듈 weighted-shapes-and-log-coordinates | Q⟺모든 t≥1에서 (t^ℓb_(n,ℓ)) 단봉 | 맞음 |
| index 모듈 lucky-weights-and-slices | b_(n,ℓ)(x)=Σx^lucky, x=1이 원 행, x=n/c의 가중 골 | 맞음 |
| index 모듈 total-displacement-tilts-and-geometric-endpoints | 고정 q<1에서 띠 c log n≤k≤D log n의 각 칸 로그볼록성. "원 q=1의 반례가 아니다" | 맞음 |
| index 모듈 fixed-preference-orbits-and-dickman | 모든 n≥5의 세 항 골. 한 선호 다중집합 안의 q개 엄격 국소 봉우리 | 맞음 |
| index 모듈 surplus-spaces-and-sparse-collisions, outcome-fibres-and-saturation-obstructions | 원 P/Q의 반례가 아니라는 서술 | 맞음 |

**형식:** 이상 없음.

**통과한 두 question과의 중복: 없음.** 두 question은 원 모형 안의 구조를 묻고, 이 question은 변형 아래의 경계를 묻는다.

### 보완할 점

1. 극한 밀도 x^r f_X의 현황을 원자료대로 고친다.
   - −1/2<r<5/2에서 엄격 단봉: r81e7051 limiting-shape.md §4.
   - 경계 r=5/2에서도 유일한 유한 모드와 양쪽 엄격 증감: rc70a0941 정리 J, review 지지. 도함수의 고립 영점 가능성은 남는다.
   - 5/2<r<5/2+ε_0에서 비단봉: r7eeaca03 §7.
   - 미결로 적을 것은 r=−1/2와 r<−1/2뿐이다. grounds에도 rc70a0941을 더한다.
2. (A)에 새로 넣은 행운 가중과 q^T 기울임에도 statement에서 깨지는 성질을 붙인다(권고). 행운 가중은 x=n/c에서 가중 행의 단봉성 실패이고, q^T는 고정 q<1에서 Q 실패다. t^ℓ 항목은 실패나 성공이 아니다. 원 Q와 동치인 미결 항목이다. 그 성격도 밝히면 "recorded success/failure" 분류가 흔들리지 않는다.

이 question의 주제와 구체성, 비중복은 충족한다. 위 1만 고치면 통과 수준이다.

---

## 6. 목록 전체에 대한 관찰(참고, 판정 아님)

1. **처음 지적의 해소 상태.** 처음 「보완할 점」 열일곱 항목은 모두 해소되었다. revise로 남은 두 question은 처음 지적 때문이 아니다. 보완 중에 statement에 새로 넣은 문장이 원자료와 어긋났기 때문이다. 두 경우 모두 grounds는 원자료를 정확히 적었고, statement가 그것을 일반화하거나 체제를 옮겼다. 처음 검토가 짚은 공통 모양(statement의 일반화)이 새 문장에서 한 번씩 되풀이되었다.
2. **frontier 판 185.** 검토 중에 공표된 r317289416…과 node Q⋆는 다섯 question과 중복되지 않는다. 다만 r317289416…은 op-tie-block-transport의 (iii)에 직접 닿는다. 그 전에 공표된 r359ba037…도 op-threshold-block의 중앙 체제와 op-layer-period의 극 체제(누율 항등식, 세 극점의 '두 극 예측')에 닿는다. 배포 뒤 이 question들을 점유할 탐색 세션에 이 두 기록을 알려 줄 필요가 있다.
3. **배포 묶음.** 이번 재검토로 통과한 셋과 이미 통과한 둘을 합치면 배포 question은 다섯 개다(ID 중복 없음). 다섯 개의 경계 문장이 서로를 가리키고 있다. 같은 하위 문제를 여러 탐색 세션이 겹쳐 연구할 위험은 처음 목록보다 작다.
