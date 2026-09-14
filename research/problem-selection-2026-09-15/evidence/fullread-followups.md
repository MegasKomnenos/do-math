# 후속 신착 논문 전문 독해와 적용 판정

## 1. 목적과 완료 상태

이 기록은 2026-09-15 KST를 기준으로 `evidence/검색-범위.md`에서 초록 또는 문자열 검색까지만 했던 네 논문의 최신 원문을 처음부터 참고문헌까지 전부 읽고, Celano 외 6인(2025)의 추측 6.5에 미치는 영향을 판정한다. 대상 추측은 고정된 `n`에서 최대변위가 정확히 `ℓ`인 일반 주차함수의 개수 `b[n,ℓ]`가 `ℓ`에 따라 단봉인지 묻는다. 이 기록은 연구 준비 검토이며 새 증명 탐색이나 새 범위 계산을 포함하지 않는다.

상태는 **READY**다. 네 PDF의 102쪽 전부를 원본 페이지 경계대로 순서대로 출력해 읽었고, 정의·정리·수식이 판정에 직접 쓰이는 13쪽과 직접 의존 원문 2쪽을 렌더 이미지로 대조했다. 읽지 못한 쪽이나 미완료 자료는 없다.

## 2. 확보와 독해 방법

scholarly MCP에서 `list_sources`로 arXiv의 구현 상태를 확인하고 `describe_source(arxiv)`로 검색·판본 고정·fetch·extract 문법을 읽었다. `fetch(2508.11587)`의 첫 호출은 timeout이었고, `2508.11587v1` 고정 재시도는 arXiv API의 HTTP 429를 받았다. 오류 artifact `scholarly://artifact/43c12e905d3202a4b6936544fdecc4739b84b0d933c9da87e6cc96600d9a4c54`를 `extract`하니 본문은 `Rate exceeded.` 한 줄이었다. 이 실패를 자료 부재로 해석하지 않았다.

허용된 보조 경로에 따라 공식 arXiv `abs` 페이지에서 제출 이력과 최신 판본을 확인하고, 공식 `pdf` URL에서 고정 판본을 직접 내려받았다. `extract-documents`의 `extract_all.py`는 네 PDF의 모든 쪽을 텍스트 레이어로 추출했고 `[[VISION ...]]` 플레이스홀더는 없었다. 그 뒤 PDF 자체에서 페이지별 텍스트를 다시 출력해 다음 구간을 모두 읽었다.

| 자료 | 판본·쪽수 | 실제 순차 출력·독해 구간 | 렌더 대조 |
|---|---:|---|---|
| Inversions in parking functions | 2508.11587v1, 30쪽 | 1–10, 11–20, 21–30 | 1, 11쪽 |
| Counting ℓ-interval Fubini rankings through their parking outcome | 2603.00693v1, 21쪽 | 1–10, 11–21 | 3, 17, 18쪽 |
| Luck and magic for Pitman–Stanley polytopes and parking functions | 2603.19194v2, 33쪽 | 1–11, 12–22, 23–33 | 2, 3, 20, 27쪽 |
| Parking functions, Smirnov words, and noncrossing Chow polynomials | 2609.05131v1, 18쪽 | 1–9, 10–18 | 4, 5, 14, 15쪽 |

전문 검색은 완독 뒤 확인 장치로만 사용했다. 네 원문 모두 `2507.07243`, `maximum displacement`, `maximal displacement`, `displacement`를 한 번도 쓰지 않는다. `real-root`, `log-conc`, `unimod`는 뒤의 두 논문에만 나오며 아래에서 그 다항식의 변수를 구별한다.

## 3. Inversions in parking functions

### 3.1 절별 독해

1–3절은 선호열 자체의 역전수 `inv(α)`를 다룬다. Francon의 labeled rooted forest 대응에서 parental preorder inversion이 선호열 역전수와 일치함을 보이고, Haiman의 parking-function symmetric function과 stable principal specialization을 이용해 `PF_n(q)=Σ q^{inv(α)}`의 q-지수생성함수를 얻는다. 조합적 증명도 같은 forest 분해를 q-다항계수로 정리한다.

4절은 unit interval parking function `UPF_n={α:M(α)≤1}`에 한정한다. block structure를 Cayley permutation으로 보내는 전단사 `ψ`가 선호열 역전수를 보존하고, `UPF_n(q)`를 순열의 inversion-ascent 다항식의 `t=2` 특수화로 나타낸다. 따라서 Fubini 수의 q-유사 생성함수를 얻는다. 이 결과는 `M≤1`인 한 층의 객체 안에서 **역전수**를 분포시키며, `M`의 층별 분포를 만들지 않는다.

5절의 k-transitive 방법은 위치 집합에 대한 합으로 표현되는 통계의 평균을 `S_n`-불변 word family에서 한 위치의 확률로 환원한다. inversion/descents, ties, small/big inversions와 descents 등에 적용한다. 정리 5.2는 통계 자체의 재배열 불변성을 요구하지 않는다. `PF_n`은 `S_n`-불변이므로 그 조건은 충족한다. 그러나 유용한 적용에는 통계가 작은 고정 `k`개의 좌표만 보는 함수 `χ`의 위치별 합 `f_χ` 또는 연속 위치별 합 `g_χ`로 표현되어야 한다. 최대변위는 주차 결과의 전역 점유 이력에서 생기는 차량별 변위의 최댓값이고, 이 논문은 이를 그런 고정 `k` 합으로 나타내거나 국소 통계와 연결하는 정리를 주지 않는다. `k=n`으로 모든 함수를 형식상 넣는 것은 정리의 환원이 항등식이 되어 정보를 주지 않는다. 6절의 열린 문제도 다른 word statistic의 생성함수를 제안할 뿐 최대변위를 언급하지 않는다.

### 3.2 원문 조건과 국소 결함

PDF 1쪽의 unit interval 조건은 outcome permutation을 `π(α)(spot)=car`로 정의한 뒤 `π(α)^{-1}(i)-α_i≤1`로 쓴다. 렌더 대조 결과 이는 차량 `i`의 실제 자리와 선호의 차가 1 이하라는 뜻으로 시작 문서의 정의와 일치한다.

PDF 11쪽 정리 4.1(1)은 약증가 재배열 `α↑=(a'_1,…,a'_n)`에 대해 `a'_i∈{i,i+1}`이라고 인쇄했다. 이는 `α=11∈UPF_2`의 `a'_2=1`부터 거짓이다. 인용한 Bradt 외(2024) 정리 2.9의 원문 PDF 6–7쪽을 대조하면 원 정리는 block별 상대 순서와 다항계수만 진술하고, 증명은 단일 block이 `11 2 3 … n−1`임을 보인다. 따라서 좌표별로 의도한 식은 `a'_i∈{i−1,i}`로 보인다. 후속 Lemma 4.2와 정리 4.4는 block 크기·block 내 상대 순서와 Cayley 대응을 사용하며 이 잘못 인쇄된 (1)에 의존하지 않는다.

### 3.3 추측 6.5에 대한 판정

- 직접 해결: 아니다.
- 간접 귀결: 읽은 본문이 제공하는 적용 사슬로는 도출되지 않는다. 역전수 생성함수와 평균 합에서 최대변위 분포로 가는 보존 연결을 확인하지 못했다.
- 접근 발판: 제한적이다. 고정 `k` 위치 통계의 합으로 환원되는 통계와 전역 점유 이력의 최댓값인 최대변위 사이의 구조적 장벽을 명확히 한다. 최대변위를 다루려면 차량 도착 순서와 점유 상태를 보존하는 refinement가 추가로 필요하다.

## 4. Counting ℓ-interval Fubini rankings through their parking outcome

### 4.1 절별 독해

1–2절은 Fubini ranking을 ordered set partition과 동일시한다. 각 동률 block의 차량은 증가 순서로 연속 주차하며, ordered set partition의 block을 평탄화하면 parking outcome이 된다. outcome permutation의 각 증가 run 안에서는 block 경계를 자유롭게 더 넣을 수 있고 descent에서는 반드시 경계가 생기므로, run이 `k`개인 outcome의 Fubini ranking 수는 `2^{n-k}`다.

3절은 unit Fubini ranking, 곧 Fubini ranking 중 동률 크기가 2 이하인 하위족을 다룬다. 고정 outcome의 각 증가 run에 허용되는 표준화된 약증가 unit Fubini ranking 수가 Fibonacci 수이고, 서로 다른 run의 선택이 독립이므로 run 길이별 Fibonacci 수의 곱을 얻는다.

4절은 동률 크기가 `ℓ+1` 이하인 `ℓ`-interval Fubini ranking으로 확장한다. 약증가 하위족의 수는 `(ℓ+1)`항 재귀와 초기값 `2^{j-1}`을 갖는 `ℓ`-Pingala 수다. Lemma 4.1은 고정 outcome의 한 run에 제한한 선호열을 첫 선호만큼 평행이동해 표준 약증가 `ℓ`-interval Fubini ranking으로 보내는 전단사를 준다. Theorem 4.2는 run 길이가 `ℓ+1` 이하이면 `2^{s-1}`, 더 길면 `P_s(ℓ)`를 곱한다. 5절은 `(m,n)`·b-restricted·fixed maximum rank·fixed number of ties 문제를 제안한다. fixed maximum rank는 선호값의 최댓값이며 최대변위가 아니다.

Fubini ranking에서는 한 동률 block의 선호가 그 block의 첫 자리이고, block의 차들이 연속 자리에 주차한다. 따라서 그 block의 최대변위는 `block size−1`이다. 그러므로 이 논문의 `ℓ`-interval Fubini ranking은 `FR_n∩{M≤ℓ}`와 일치한다. 이는 정의와 Lemma 2.4에서 따르는 제한 하위족의 정확한 연결이다. 일반 주차함수 전체 `PF_n`에 대한 `A[n,ℓ]` 또는 `b[n,ℓ]` 공식은 아니다.

### 4.2 S2 의존 정리와 교정 여부

새 논문은 Aguilar-Fraga 외(2024)의 정리 4.16, 즉 **약증가** `ℓ`-interval Fubini ranking의 재귀만 인용한다. S2의 정리 4.1과 4.14는 인용하거나 수정하지 않는다.

S2 정리 4.15는 “unit Fubini rankings의 수”가 Fibonacci라고 써서 전체 집합과 약증가 하위집합을 혼동한다. 새 논문 PDF 14쪽의 Corollary 3.1은 정확히 `|O^{-1}_{UFR_n}(id)|=|UFR_n^↑|=F_n`으로 한정하고, PDF 16쪽 Example 3.1은 전체 `|UFR_3|=12`라고 확인한다. 따라서 후속 원문은 S2의 범위 오류를 사실상 교정한다.

S2 정리 4.16의 recurrence 자체는 새 논문의 Definition 4.1과 Theorem 4.2에서 사용된다. S2의 인쇄 증명에는 마지막 동률 block의 크기가 `x+1`일 때 rank를 `n−x+1`이라고 쓴 off-by-one이 있으며, block 시작 rank는 `n−x`여야 한다. 새 논문은 이 문장을 반복하지 않는다.

새 논문 내부에도 두 국소 표기 결함이 있다. PDF 3쪽은 `P_1(n)=F_n`을 설명하며 seed를 `F_1=F_2=1`이라고 쓰지만, PDF 14–16쪽과 Definition 4.1은 run 길이에 맞춘 `F_1=1,F_2=2`를 사용한다. PDF 19쪽 Corollary 4.1의 증명 한 줄은 곱 지수를 `2^{c_1-1}`로 인쇄했지만 정리식 (18)과 계산은 `2^{c_i-1}`을 사용한다. 둘 다 최종 곱 공식의 실제 convention과 계산은 분명하지만 시작 자료에서 인덱싱을 인용할 때 주의해야 한다.

### 4.3 추측 6.5에 대한 판정

- 직접 해결: 아니다. 대상이 `PF_n` 전체가 아니라 Fubini ranking 하위족이다.
- 간접 귀결: 읽은 본문이 제공하는 적용 사슬로는 도출되지 않는다. 하위족의 누적 계수를 일반 `b[n,ℓ]`로 이전하는 분해나 보존 대응을 확인하지 못했다.
- 접근 발판: 네 논문 중 가장 구체적이다. 고정 outcome에서 제한 조건을 증가 run별 독립 곱으로 바꾸는 성공 사례를 준다. 시작 문서의 outcome별 식을 연구할 때, 일반 주차함수에서 왜 같은 run 분리가 실패하는지 또는 어떤 추가 상태가 있으면 회복되는지 비교할 수 있다.

## 5. Luck and magic for Pitman–Stanley polytopes and parking functions

### 5.1 절별 독해와 증명 사슬

2절은 Pitman–Stanley polytope, `y`-parking function, Ehrhart 다항식과 magic basis `t^i(1+t)^{d-i}`를 정의한다. 3–4절의 핵심은 Ehrhart 다항식의 magic 계수를 변형 주차 절차의 lucky car 수로 해석하는 것이다. 충분히 큰 `y`에서는 block parking protocol의 독립 선택으로 바로 양성을 얻고, 일반 양의 `y`에서는 알고리즘이 composition의 dominance 조건을 보존함을 보인 뒤 이중계수한다. PDF 20쪽 Theorem 4.5와 PDF 27쪽 Proposition 4.13의 증명을 렌더로 대조했다.

Theorem 1.1은 magic positivity를 주고, 외부의 Brändén 선형변환 보존 정리를 적용한 Theorem 1.2가 Pitman–Stanley `h*`-다항식의 실근성을 얻는다. 따라서 `h*` 계수의 로그오목성과 단봉성이 따른다. 여기서 lucky는 차가 자기 선호 자리에 주차했는지이고, first space를 막은 변형 protocol도 사용한다. 최대변위의 값이나 `M=ℓ`인 층은 어느 다항식에도 기록되지 않는다.

### 5.2 추측 6.5에 대한 판정

- 직접 해결: 아니다.
- 간접 귀결: 읽은 본문이 제공하는 적용 사슬로는 도출되지 않는다. 실근 다항식은 Pitman–Stanley `h*`이고, magic 계수의 lucky 분포에서 `b[n,ℓ]`로 가는 보존 연결을 확인하지 못했다.
- 접근 발판: 일반 방법론의 비교 사례다. 강한 계수 성질을 이전하려면 magic positivity와 목표 다항식 사이의 정확한 선형변환 같은 연결이 필요함을 보여준다. 현재 원문에는 최대변위 보존 연결이 없다.

## 6. Parking functions, Smirnov words, and noncrossing Chow polynomials

### 6.1 절별 독해와 실근성 대상

3–4절은 tie가 없는 주차함수의 descent 다항식을 multiplicity type별로 finite-alphabet Smirnov word descent 다항식에 옮긴다. 마지막 문자로 refinement한 벡터가 Leander의 보존 정리 아래 interlacing sequence를 이루므로 합도 실근이다. 이 결과가 noncrossing partition lattice의 Chow 다항식 실근성을 준다.

5–6절은 최대 **선호값**을 `m`으로 제한하고 새 최대 문자를 삽입하는 유한 recurrence로 peak와 tie를 센다. 여기의 bounded maximum은 `max_i w_i≤m`이며 최대변위가 아니다. 7절은 Diaconis–Hicks의 descent-set 등분포로 일반 주차함수의 descent 다항식을 모든 `[n+1]^n` word의 descent 다항식으로 옮겨 실근성을 얻는다.

8절은 toric g-contribution의 fixed-row common interlacer를 증명해 비음수 행 결합과 약한 123-회피 주차함수의 ascent/descent 다항식 실근성을 얻는다. 9절은 Pollak 순환 작용이 image size를 보존한다는 점과 occupancy recurrence를 이용해 `Σ t^{|im(w)|-1}`의 단순 음의 실근을 증명한다. 이어 labeled-Dyck model의 두 패턴 회피 하위족에서 ascent/descent 다항식을 Jacobi 다항식으로 나타낸다.

이 원문이 말하는 real-rooted polynomial은 tieless descent/Chow, ordinary descent, toric g-contribution과 그 비음수 결합, 123-회피 ascent/descent, image size, 두 패턴 회피 ascent/descent다. 어느 것도 최대변위를 변수로 갖지 않는다. proof-level 공통 원리는 통계에 맞는 finite refinement를 선택해 recurrence가 interlacing을 보존하게 하는 것이다.

### 6.2 추측 6.5에 대한 판정

- 직접 해결: 아니다.
- 간접 귀결: 읽은 본문이 제공하는 적용 사슬로는 도출되지 않는다. content type, local comparison, image size에서 최대변위 분포로 가는 보존 연결을 확인하지 못했다.
- 접근 발판: 방법론적으로 유의미하다. 최대변위에 맞는 유한 상태와 interlacing-preserving 전이를 찾을 수 있다면 사용할 수 있는 틀을 보여준다. 원문의 last-letter state나 Pollak 궤도는 그대로는 최대변위를 보존하지 않으므로 추가 정리가 필수다.

## 7. 현재 시작 자료의 판정과 개선점

`문제와-선정-근거.md`와 `선행연구와-시작-자료.md`의 핵심 경계는 전문 독해 뒤에도 옳다. 즉, 최대변위의 정확 분포를 총변위·선호합·역전수·descent·image size·lucky car·약증가 목록의 결과와 구별해야 하고, 다른 다항식의 실근성을 목표 다항식으로 자동 이전하면 안 된다. 네 후속 원문 중 추측 6.5를 해결하거나 짧은 귀결로 만드는 논문은 없으므로 현재 문제 선택을 철회할 근거는 없다.

시작 자료에는 다음 내용을 보강하는 것이 적절하다.

1. 검색 기록의 네 항목을 “초록 확인”에서 “최신 고정판 전문 완독”으로 갱신하고, 모두 `2507.07243`과 최대변위를 언급하지 않았음을 기록한다.
2. Fubini 하위족에서 `M≤ℓ`가 최대 동률 block 크기 `≤ℓ+1`과 같고, 고정 outcome의 계수가 run별 Pingala 곱으로 분해된다는 제한적 발판을 추가한다. 일반 `PF_n`의 공식으로 확대하지 않는다.
3. 역전수 논문의 `S_n`-불변 평균화와 Smirnov 논문의 finite-state interlacing을 접근 후보가 아니라 **필요 조건을 드러내는 비교 틀**로 기록한다. 최대변위는 작은 고정 수의 좌표만 보는 함수의 위치별 합이나 local comparison 통계로 주어지지 않으므로, 주차 과정의 점유 상태와 최댓값을 보존하는 별도 상태가 필요하다.
4. 인용 시 unit interval 구조 정리의 인쇄 오기, Fubini/Pingala Fibonacci seed convention, S2의 전체/약증가 범위를 교정한다.

이 개선은 연구 준비의 문헌 정확성과 접근 경계를 강화한다. 실제 풀이, 새로운 `n`의 계산, 문제 재선정은 하지 않았다.
