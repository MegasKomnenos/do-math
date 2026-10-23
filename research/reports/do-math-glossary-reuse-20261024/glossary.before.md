# 용어 정본 — 338개 항목

현재 유효한 수학적 대상·기호의 정의다. [제안 처리·폐기 이력](glossary-history.md)은 별도 파일에서 관리한다.

기록별 이명은 옛 기록을 읽는 데만 쓰며, 새 산출에서는 정본 이름을 사용한다.

## 1. 자연수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 자연수 · ℕ |
| 종류 | 표기 관례 |
| 정의 | ℕ := {0,1,2,…}. 본 문제의 크기는 n≥1이고, 크기 0은 빈 목록 및 점화식의 경계에만 사용한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | Lean 표준 `Nat` / `ℕ`. |
| 출처 | goal.md 「정확한 문제」; ℕ의 표기는 k47bedb96d62e487d959c55adc57235c7 |
| 기록별 이명 | 없음 |

## 2. 자리집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 자리집합 · [n] |
| 종류 | 대상 |
| 정의 | n∈ℕ에 대해 [n] := {1,…,n}; [0] := ∅. 차량 번호와 선호의 값도 같은 집합을 사용한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | Lean `Fin n`의 값 j를 원 번호 j+1로 옮기는 순서 보존 대응. k342ab0d73a284696bcb1050ba1ce7e00/objects.md. |
| 출처 | goal.md 「정확한 문제」; [n]의 표기는 k47bedb96d62e487d959c55adc57235c7 |
| 기록별 이명 | 없음 |

## 3. 선호 목록

| 칸 | 내용 |
|---|---|
| 이름·기호 | 선호 목록 · α=(a₁,…,aₙ) |
| 종류 | 대상 |
| 정의 | n∈ℕ에 대한 선호 목록 α :⇔ α는 [n]에서 [n]으로 가는 함수이며 aᵢ=α(i)이다. n=0에는 빈 함수, 즉 빈 목록 하나가 있다. 함수 표기와 길이 n의 순서 있는 목록 표기를 동일하게 사용한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | `Parking.Pref n := Fin n → Fin n` (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| 출처 | goal.md 「정확한 문제」; 크기 0의 빈 목록 관례도 같은 절 |
| 기록별 이명 | 없음 |

## 4. 주차 과정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 주차 과정 · Parkₙ(α) |
| 종류 | 함수 |
| 정의 | n∈ℕ 및 선호 목록 α에 대해 Parkₙ(α) := 다음 유한 알고리즘의 출력. 처음에는 모든 자리가 비어 있다. i=1,…,n 순서로, 아직 실패하지 않았다면 현재 빈자리 중 aᵢ 이상인 것의 집합을 만들고, 비어 있으면 실패를 출력하고 종료하며, 아니면 그 최솟값에 차 i를 주차한다. 끝까지 성공하면 도착 순서에 따른 주차 자리의 순서쌍 목록을 출력한다. n=0의 출력은 성공한 빈 목록이다. |
| 잘 정의됨 | 단계마다 후보가 유한하므로 비어 있지 않으면 최솟값이 유일하고, 단계 수는 n 이하이다. 이는 정의의 존재·유일성 설명이며 공개 Lean 대응과 그 검토 상태는 아래와 같다. |
| Lean 대응 | `Parking.park`, `Parking.run`, `Parking.next`; 후보의 최솟값 또는 실패를 반환한다 (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| 출처 | goal.md 「정확한 문제」; Parkₙ은 k47bedb96d62e487d959c55adc57235c7의 명시적 알고리즘 표기 |
| 기록별 이명 | 없음 |

## 5. 주차 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 주차 함수 · PFₙ |
| 종류 | 대상 |
| 정의 | n∈ℕ에 대해 PFₙ := {선호 목록 α : Parkₙ(α)가 실패하지 않고 모든 차를 주차시킨다}. 따라서 PF₀는 빈 목록 하나로 이루어진다. 각 목록은 도착 순서를 유지하며, 선호를 정렬하거나 차량 순서를 바꾼 목록과 동일시하지 않는다. |
| 잘 정의됨 | 주차 과정의 결정성 및 선호 목록 전체가 유한하다는 사실에 따른다. |
| Lean 대응 | `Parking.PF n`, `Parking.Success` (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 없음 |

## 6. 실제 주차 자리

| 칸 | 내용 |
|---|---|
| 이름·기호 | 실제 주차 자리 · sᵢ |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ, i∈[n]에 대해 sᵢ := Parkₙ(α)가 차 i에 배정한 자리. α가 바뀌면 sᵢ도 바뀌며 필요하면 sᵢ(α)로 쓴다. |
| 잘 정의됨 | α∈PFₙ이므로 성공 출력의 i번째 성분이 존재하고 유일하다. |
| Lean 대응 | `(Parking.slot a i).val + 1` (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 없음 |

## 7. 변위

| 칸 | 내용 |
|---|---|
| 이름·기호 | 변위 · dᵢ |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ, i∈[n]에 대해 dᵢ := sᵢ−aᵢ. 주차 규칙에 의해 sᵢ≥aᵢ이므로 dᵢ∈ℕ이다. 필요하면 dᵢ(α)로 쓴다. |
| 잘 정의됨 | 실제 주차 자리의 존재·유일성과 정수 뺄셈에 따른다. Lean의 자연수 뺄셈을 쓰면 sᵢ≥aᵢ를 확인한다. |
| Lean 대응 | `Parking.displacement`; `pref_le_slot`, `displacement_original`이 원 차와의 연결을 주장한다 (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean; 검토 k92260b6c2f6e4c999f741f37265db176에서 수용). |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 없음 |

## 8. 최대 변위

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 변위 · M(α) |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ에 대해 M(α) := max{dᵢ : i∈[n]}. 크기 0에서 M의 값을 이 정본은 정하지 않는다. 구현상 빈 최댓값 관례를 더하면 보조 확장임을 명시한다. |
| 잘 정의됨 | n≥1이므로 비어 있지 않은 유한 정수 집합의 최댓값이 존재한다. |
| Lean 대응 | `Parking.M`의 n≥1 제한. 구현 전체의 보조 확장은 아래 M̄ 항목이며 `M_attained` 연결은 검토 k92260b6c2f6e4c999f741f37265db176에서 수용 (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 없음 |

## 9. 누적 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 누적 개수 · Aₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1 및 정수 ℓ≥0에 대해 Aₙ,ℓ := #{α∈PFₙ : M(α)≤ℓ}. 모든 n≥0에서 Aₙ,₋₁ := 0으로 확장한다. 빈 목록 경계는 ℓ≥0에서 A₀,ℓ := 1이다. 더 작은 크기 j의 Aⱼ,ℓ도 ℓ가 j−1보다 크다는 이유로 생략하지 않는다. |
| 잘 정의됨 | PFₙ이 유한하므로 그 부분집합의 개수가 정의된다. 경계값은 명시된 별도 관례다. |
| Lean 대응 | `Parking.A`, `Parking.Aint`. 후자는 정수 ℓ<0 전체에 0을 반환하는 구현상 보조 확장을 포함한다. 정본에서 정한 음수 경계는 ℓ=−1뿐이다 (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| Lean 추가 대응 | k2809252f588641b39bcaf13513db3951/Evaluator.lean의 `ParkingLastCar.evalA ℓ n`은 Aₙ,ℓ의 점화식 계산 구현이다. `evalA_eq_original`이 모든 자연수 n,ℓ에서 동일성을 증명한다. 같은 기록 Recurrence.lean의 `ParkingLastCar.A_recurrence`가 원 A의 점화식을 증명한다. 검토 k41050a1934d84a1fae10f1e3af32d0a1에서 accepted/matches. |
| Lean 유한 대응 | k83ac8ca8d9c44903b97b8979ac04bdd3/Finite.lean의 `ParkingLeft.entry`는 0≤n<15,0≤ℓ<14에서 Aₙ,ℓ와 같다. `certificate_eq_original`이 원 A와의 동일성을 증명하며 검토 kb196a5163fc74633b71d21d0bc248fa2에서 accepted/matches다. 표 밖 기본값은 원 A의 정의가 아니다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.aq q n` (q≥1)은 Aₙ,ᵩ₋₁의 ℚ 포함값. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean의 ParkingForest.original_A_parent_sum은 모든 n,ℓ∈ℕ의 실제 A와 부모 함수 숲 합을 식별한다. lean/GainLoss.lean의 original_A_pos도 모든 n,ℓ에서 양수성을 증명한다. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. k2874758a73b749c0b8af17fcc1be6660/lean/FiniteUpper.lean의 ParkingFreshUpper.entry 및 certificate_eq_original은 0≤n≤18,0≤ℓ≤17의 별도 유한 구현이며 kcc189037a61c4faea0745b876c66fffe에서 accepted/matches로 수용됐다. 표 밖 값은 원 A가 아니다. |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 기록 k2809252f588641b39bcaf13513db3951의 Rℓ(n) (점화 계산기의 값). 모든 n,ℓ∈ℕ에서 Aₙ,ℓ와 같음이 evalA_eq_original으로 증명되어 동일시했다. 이후 새 산출의 수학 표기는 Aₙ,ℓ를 쓴다. |

## 10. 정확 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정확 개수 · bₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1 및 정수 ℓ≥0에 대해 bₙ,ℓ := #{α∈PFₙ : M(α)=ℓ}. A를 사용한 차분 bₙ,ℓ=Aₙ,ℓ−Aₙ,ℓ₋₁은 정의에서 따라 증명할 관계이며 ℓ=0에는 Aₙ,₋₁=0을 사용한다. b의 크기 0 값은 정하지 않는다. |
| 잘 정의됨 | PFₙ의 유한 부분집합의 개수다. |
| Lean 대응 | `Parking.b (n : ℕ+) (ℓ : ℕ)` (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). |
| Lean 유한 대응 | k83ac8ca8d9c44903b97b8979ac04bdd3/Finite.lean의 `ParkingLeft.exactEntry`는 양수 n<15,0≤ℓ<14에서 bₙ,ℓ와 같다. `b_eq_exactEntry` 및 검토 kb196a5163fc74633b71d21d0bc248fa2에서 accepted/matches다. 크기 0의 b를 도입하지 않는다. |
| Lean 추가 대응 | k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 ParkingWidth.original_even_widResponse 및 original_odd_widResponse_explicit는 q≥2의 원 b 인접 차에 대한 정확 등식이다. 검토 k0d67ab01617a4814aae5265ebb219b1a에서 accepted/matches. 두 경계 부호나 단봉성 정리가 아니다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: original_boundary_exact_sum, original_boundary_quartic_lower. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 현재 형식 대응 | k2874758a73b749c0b8af17fcc1be6660/lean/FiniteUpper.lean의 ParkingFreshUpper.exactEntry와 b_eq_exactEntry는 1≤n≤18,0≤ℓ≤17에서 원 b와의 동일성을 증명한 구현으로 kcc189037a61c4faea0745b876c66fffe에서 accepted/matches다. 이 수용은 크기 0의 b나 전체 P를 추가하지 않는다. |
| 출처 | goal.md 「정확한 문제」 |
| 기록별 이명 | 없음 |

## 11. 단봉성

| 칸 | 내용 |
|---|---|
| 이름·기호 | 단봉성 · Unimodal(x) |
| 종류 | 성질·관계 |
| 정의 | m∈ℕ 및 실수 유한 수열 x=(x₀,…,xₘ)에 대해 Unimodal(x) :⇔ 어떤 정수 c∈{0,…,m}가 존재하여, 모든 정수 0≤k<c에 xₖ≤xₖ₊₁이고 모든 정수 c≤k<m에 xₖ≥xₖ₊₁이다. 자연수 수열은 실수에 포함시켜 같은 뜻으로 읽는다. 평평한 봉우리를 허용한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 자연수 값 수열에 대한 `Parking.Unimodal`; 일반 실수 값 구현은 없다 (k342ab0d73a284696bcb1050ba1ce7e00/Parking.lean). k21248694f4c24bad89564e3143deba52/Criterion.lean의 `ParkingCriterion.unimodal_iff_no_drop_rise`는 자연수 유한열에서 엄격한 감소 뒤 재증가 없음과의 동치를 증명하며 검토 k8489c648c0964cb3b3bf9fe09c296340에서 accepted/matches다. |
| 출처 | goal.md의 명제 P에 쓰인 조건을 k47bedb96d62e487d959c55adc57235c7에서 일반 유한 수열에 대해 표기 |
| 기록별 이명 | 없음 |

## 12. 선호 접두부 · β

| 칸 | 내용 |
|---|---|
| 이름·기호 | 선호 접두부 · β |
| 종류 | 대상 |
| 정의 | 정수 $N\ge0,0\le k\le N$에 대해 선호 접두부 β :⇔ β는 $[N]^k$의 원소다. 처음 $k$대에 주차 과정의 같은 단계 규칙을 적용한다. |
| 잘 정의됨 | 각 단계의 첫 빈자리 선택의 결정성으로 부분 과정도 결정된다. |
| Lean 대응 | 미형식화 |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md 「점유 집합으로 세는 누적 개수」 |
| 기록별 이명 | |

## 13. 직전 빈자리 · p_S(s)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 직전 빈자리 · $p_S(s)$ |
| 종류 | 함수 |
| 정의 | $N\in\mathbb N$, $S\subseteq[N]$, $s\in[N]\setminus S$에 대해 $p_S(s):=\max(\{0\}\cup\{t\in[N]:t<s,t\notin S\})$. |
| 잘 정의됨 | 0을 포함하는 유한 집합의 유일한 최댓값이다. |
| Lean 대응 | 미형식화 |
| Lean 추가 대응 | k3c8d00ecefb9486697fd5692a47dad49/lean/Gap.lean의 ParkingArrivalProof.prev. 내부 자리 s₀에 대해 원 p_S(s₀+1)과 대응한다. 검토 kf60b5d44129f444b9c13cfa739536768 accepted/matches. |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md의 가중치 도출 |
| 기록별 이명 | |

## 14. 전이 간격 · g_S(s)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전이 간격 · $g_S(s)$ |
| 종류 | 함수 |
| 정의 | $N\in\mathbb N$, $S\subseteq[N]$, $s\in[N]\setminus S$에 대해 $g_S(s):=s-p_S(s)$. |
| 잘 정의됨 | 직전 빈자리가 유일하고 $0\le p_S(s)<s$다. |
| Lean 대응 | 미형식화 |
| Lean 추가 대응 | k3c8d00ecefb9486697fd5692a47dad49/lean/Gap.lean의 ParkingArrivalProof.gap,next_interval,gaps_pair. 검토 kf60b5d44129f444b9c13cfa739536768 accepted/matches. |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md의 가중치 도출 |
| 기록별 이명 | |

## 15. 전이 가중치 · w_ℓ(S,s)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전이 가중치 · $w_\ell(S,s)$ |
| 종류 | 함수 |
| 정의 | $N\in\mathbb N$, 정수 $ℓ\ge0$, $S\subseteq[N]$, $s\in[N]\setminus S$에 대해 $w_\ell(S,s):=\min(g_S(s),\ell+1)$. |
| 잘 정의됨 | 유한 정수의 최솟값이다. 이 값이 원 선호의 개수임은 exposition.md에서 별도로 논증한다. |
| Lean 대응 | 미형식화 |
| Lean 추가 대응 | k3c8d00ecefb9486697fd5692a47dad49/lean/Gap.lean의 ParkingArrivalProof.weight_le가 조건별 한 차량 선호 개수 W_(d≤ℓ)와 이 전이 가중치를 식별한다. 검토 kf60b5d44129f444b9c13cfa739536768 accepted/matches. |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md의 식 (1) 도출 |
| 기록별 이명 | |

## 16. 제한 점유 접두부 개수 · D_ℓ(S)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 점유 접두부 개수 · $D_\ell(S)$ |
| 종류 | 함수 |
| 정의 | $S\subseteq[18]$, 정수 $ℓ\ge0$에 대해 $D_\ell(S):=\#\{\beta\in[18]^{\lvert S\rvert}:\beta\text{가 전부 성공하여 정확히 }S\text{를 점유하고 각 변위가 }\ell\text{ 이하}\}$. 빈 접두부에는 변위 조건이 공허하여 $D_\ell(\varnothing)=1$. |
| 잘 정의됨 | 원 과정의 부분 실행이 결정적이며 유한 집합을 센다. 작은 판과의 일치는 exposition.md의 별도 논증이다. |
| Lean 대응 | 미형식화 |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md 「점유 집합으로 세는 누적 개수」 |
| 기록별 이명 | |

## 17. 정확 점유 접두부 개수 · H(S,m)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정확 점유 접두부 개수 · $H(S,m)$ |
| 종류 | 함수 |
| 정의 | 비어 있지 않은 $S\subseteq[18]$, 정수 $m\ge0$에 대해 $H(S,m):=\#\{\beta\in[18]^{\lvert S\rvert}:\beta\text{가 전부 성공하여 정확히 }S\text{를 점유하고 최대 변위가 }m\}$. 보조 초기화로만 $H(\varnothing,0):=1$, $m>0$에서 $H(\varnothing,m):=0$을 둔다. |
| 잘 정의됨 | 비어 있지 않은 성공 접두부의 최댓값은 유일하며 목록 집합은 유한하다. 빈 경우는 별도 관례다. |
| Lean 대응 | 미형식화 |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md 「최대 변위를 직접 전달하는 별도 검산」 |
| 기록별 이명 | |

## 18. 첫 실패 개수 · F_n,k

| 칸 | 내용 |
|---|---|
| 이름·기호 | 첫 실패 개수 · $F_{n,k}$ |
| 종류 | 함수 |
| 정의 | $n\ge1,0\le k<n$에 대해 $F_{n,k}:=\#\{\alpha\in[n]^n:\text{차 }1,\ldots,k\text{는 성공하고 차 }k+1\text{이 실패}\}$. |
| 잘 정의됨 | 원 과정의 결정성과 유한 집합의 개수다. |
| Lean 대응 | 미형식화 |
| 출처 | k746a9db449ff45fd9b973172e4b40861/exposition.md 「실패 수의 별도 계수와 경계 검사」 |
| 기록별 이명 | |

## 19. 점유 자리집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 점유 자리집합 · O |
| 종류 | 대상 |
| 정의 | n∈ℕ에 대해 O⊆[n]은 현재 이미 주차한 차가 차지하는 자리들의 집합이다. 시작 상태는 ∅이며 새 차가 s에 주차하면 O를 O∪{s}로 바꾼다. |
| 잘 정의됨 | 주차 과정의 상태로 주어지는 유한 집합이다. |
| Lean 대응 | `occupied : Finset (Fin n)`; `Parking.run`, `Parking.next`의 매개변수. 번호는 값에 1을 더한다. |
| 출처 | k342ab0d73a284696bcb1050ba1ce7e00/objects.md 「실제 알고리즘」; glossary-proposals.md의 exposition.md 기재를 실제 공개 파일명으로 보정 |
| 기록별 이명 | |

## 20. 후보 자리집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 후보 자리집합 · Cₙ(a,O) |
| 종류 | 함수 |
| 정의 | n∈ℕ, a∈[n], O⊆[n]에 대해 Cₙ(a,O):={s∈[n]:a≤s, s∉O}. |
| 잘 정의됨 | 유한 집합의 조건 부분집합이다. 비어 있지 않을 때 그 최솟값은 유일하다. |
| Lean 대응 | `Parking.candidates`; `Parking.next_spec`, `Parking.next_failure`가 다음 자리와 실패를 특성화한다. |
| 출처 | k342ab0d73a284696bcb1050ba1ce7e00/objects.md 「실제 알고리즘」; glossary-proposals.md의 exposition.md 기재를 실제 공개 파일명으로 보정 |
| 기록별 이명 | |

## 21. 빈 목록까지 확장한 보조 최대 변위

| 칸 | 내용 |
|---|---|
| 이름·기호 | 빈 목록까지 확장한 보조 최대 변위 · M̄ |
| 종류 | 함수 |
| 정의 | n∈ℕ, α∈PFₙ에 대해 M̄(α):=0 (n=0), M̄(α):=max{dᵢ: i∈[n]} (n≥1). 이는 자연수 유한 supremum의 빈 값 0 관례와 같으며 양수 크기에서는 원래 최대 변위 M과 같다. |
| 잘 정의됨 | 유한 supremum으로 정의한다. 양수 크기에서 모든 dᵢ≤M̄ 및 실제 달성 여부를 `displacement_le_M`, `M_attained`로 증명한다. |
| Lean 대응 | `Parking.M`; n≥1일 때 정본의 M에 대응한다. |
| 출처 | k342ab0d73a284696bcb1050ba1ce7e00/counts.md 「최대 변위와 빈 목록 경계」; glossary-proposals.md의 exposition.md 기재를 실제 공개 파일명으로 보정 |
| 기록별 이명 | |

## 22. 봉우리 위치 조건

| 칸 | 내용 |
|---|---|
| 이름·기호 | 봉우리 위치 조건 · Uₙ(c) |
| 종류 | 성질·관계 |
| 정의 | n≥1, c∈ℕ에 대해 Uₙ(c):⇔ c<n이고 모든 자연수 k<c에서 bₙ,ₖ≤bₙ,ₖ₊₁이며 모든 자연수 c≤k<n−1에서 bₙ,ₖ₊₁≤bₙ,ₖ이다. |
| 잘 정의됨 | 해당 없음. ∃c Uₙ(c)는 정본의 길이 n 수열에 대한 단봉성이다. |
| Lean 대응 | `Parking.UnimodalAt`; 양수 크기 인수 `n : ℕ+`를 받는다. `Parking.P`는 원 목표 P의 전칭 진술이다. k21248694f4c24bad89564e3143deba52/Criterion.lean의 `ParkingCriterion.original_P_iff_no_drop_rise`는 원 P의 엄격한 감소·재증가 배제 조건과의 동치이며 검토 k8489c648c0964cb3b3bf9fe09c296340에서 accepted/matches다. P 자체의 증명은 아니다. |
| 출처 | k342ab0d73a284696bcb1050ba1ce7e00/objects.md 「P의 정확한 양화」; glossary-proposals.md의 exposition.md 기재를 실제 공개 파일명으로 보정 |
| 기록별 이명 | |

## 23. 주차 결과 순열 · π

| 칸 | 내용 |
|---|---|
| 이름·기호 | 주차 결과 순열 · π |
| 종류 | 대상 |
| 정의 | n≥1 및 α∈PFₙ에 대해 πⱼ := 자리 j에 주차한 차량 번호 (j∈[n]). |
| 잘 정의됨 | 성공한 n대가 서로 다른 n자리를 차지하므로 유일한 순열이다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/exposition.md §2; Celano 외 Definition 2.2의 car permutation과 같은 대상 |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c의 차 순열 car_α. 같은 자리별 차량 번호 순열이다. 이후에는 주차 결과 순열 π를 쓴다. 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 결과 순열 σ_α. 같은 자리별 차량 번호 함수이며 이후 주차 결과 순열 π를 쓴다. |

## 24. 선호 선택 폭 · hⱼ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 선호 선택 폭 · hⱼ |
| 종류 | 함수 |
| 정의 | n≥1, π∈𝔖ₙ, j∈[n]에 대해 hⱼ := j−max({0}∪{i∈[n]:i<j 및 πᵢ>πⱼ}). |
| 잘 정의됨 | 최댓값을 취하는 집합은 0을 포함하는 유한 집합이다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/exposition.md §2 |
| 기록별 이명 | |

## 25. 전체 개수 · Tₙ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 개수 · Tₙ |
| 종류 | 함수 |
| 정의 | n∈ℕ에서 Tₙ:=|PFₙ|. 특히 T₀=1. |
| 잘 정의됨 | PFₙ의 유한성. prime-analysis.md §1은 n≥1에서 Tₙ=(n+1)ⁿ⁻¹을 증명한다. |
| Lean 대응 | k5bedcf491ebd45f1a1dcb7fb84fad705/Deficit.lean의 ParkingSign.totalCount는 같은 Tₙ의 구현 대응이다. 검토 kdd117882498f411286f292377dc9abda에서 원 결손 형식 결과의 일부로 accepted/matches이며 닫힌 식 자체의 형식 증명은 아니다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.tq n`은 원 `ParkingSign.totalCount n`의 ℚ 포함값. 원 Cayley 공식의 현재 일반 형식 수용은 아래 보완 대응을 따른다. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/Cayley.lean의 `ParkingCayley.totalCount_zero`, `totalCount_cayley`, `totalCount_rooted` 및 세 `card_PF_*`는 원 PF의 개수를 직접 진술한다. T₀=1을 별도로, Tₙ=(n+1)^(n−1)을 n≥1에서, (s+1)Tₛ=(s+1)^s를 모든 s≥0에서 증명했다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 정의는 원 PF 개수 그대로다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: totalCount_pos, totalCount_convolution. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §1 |
| 기록별 이명 | |

## 26. 프라임 주차 함수 · PPFₙ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 프라임 주차 함수 · PPFₙ |
| 종류 | 대상 |
| 정의 | n≥1에서 PPFₙ:={α∈PFₙ: 모든 1≤j<n에 #{i:aᵢ≤j}>j}. 크기 0의 집합은 정의하지 않는다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §1 |
| 기록별 이명 | |

## 27. 프라임 누적 개수 · pᵖʳₙ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 프라임 누적 개수 · pᵖʳₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ∈ℕ에서 pᵖʳₙ,ℓ:=#{α∈PPFₙ:M(α)≤ℓ}; 계수 경계 pᵖʳ₀,ℓ:=0. 모든 n≥0에 pᵖʳₙ,₋₁:=0으로 확장한다. |
| 잘 정의됨 | 유한 집합의 개수. PF₀ 또는 A₀,ℓ를 변경하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §1 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 pₙ,ℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. |

## 28. 프라임 정확 개수 · qₙ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 프라임 정확 개수 · qₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ≥0에서 qₙ,ℓ:=pᵖʳₙ,ℓ−pᵖʳₙ,ℓ₋₁. 최대 변위가 정확히 ℓ인 프라임 목록의 수이다. |
| 잘 정의됨 | 누적 조건의 포함. 원래 bₙ,ℓ와 다른 집합을 센다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/boundaries.md 머리말 |
| 기록별 이명 | |

## 29. 누적 지수 생성함수 · ℱℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 누적 지수 생성함수 · ℱℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 ℱℓ(x):=∑ₙ≥₀ Aₙ,ℓ xⁿ/n!. 우선 형식적 멱급수이며 가능한 해석 영역에서 같은 함수를 뜻한다. |
| 잘 정의됨 | 형식적 계수로 유일하게 정의된다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §2 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 Fℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 ℓ-지수 생성함수 Fℓ. 계수 정의가 누적 지수 생성함수 ℱℓ와 같다. |

## 30. 프라임 누적 지수 생성함수 · 𝒞ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 프라임 누적 지수 생성함수 · 𝒞ℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 𝒞ℓ(x):=∑ₙ≥₁ pᵖʳₙ,ℓ xⁿ/n!. |
| 잘 정의됨 | 형식적 계수로 유일하게 정의된다. 전해석성의 비형식 근거는 같은 기록 prime-analysis.md §2이며 검토 k011d78d902664efbb1f1ef0d601484a7/prime_analytic에서 supported다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §2 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 Cℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. |

## 31. 포화 보정 다항식 · Vℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 포화 보정 다항식 · Vℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 Vℓ(x):=∑ⱼ₌₀^(ℓ−1)(ℓ−j)Tⱼ xʲ/j!. ℓ=0에는 빈 합 0. |
| 잘 정의됨 | 유한 다항식. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §2 |
| 기록별 이명 | |

## 32. 보정 원시함수 · Wℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 보정 원시함수 · Wℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 Wℓ(x):=∫₀ˣ Vℓ(t)dt. |
| 잘 정의됨 | 다항식의 상수항 0인 유일한 원시함수. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §2 |
| 기록별 이명 | |

## 33. 프라임 정확 지수 생성함수 · ℋℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 프라임 정확 지수 생성함수 · ℋℓ |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 ℋℓ(x):=𝒞ℓ(x)−𝒞ℓ₋₁(x). |
| 잘 정의됨 | 앞의 형식적 멱급수 두 개의 차. 해석적 사용은 전해석성 논증의 검토 지위를 따른다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §5 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 Hℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. |

## 34. 양의 단순극 위치 · ρℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 양의 단순극 위치 · ρℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 ρℓ:=𝒞ℓ(x)=1을 만족하는 유일한 양의 실수 x. |
| 잘 정의됨 | prime-analysis.md §3이 존재성·유일성·단순성을 비형식으로 증명한다. 해당 결과 prime_analytic은 검토 k011d78d902664efbb1f1ef0d601484a7에서 supported다. 정의 채택과 별도의 수학적 판정이다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §3 |
| 기록별 이명 | |

## 35. 점근 계수 · κℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 점근 계수 · κℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 κℓ:=1/(ρℓ 𝒞ℓ′(ρℓ)). |
| 잘 정의됨 | ρℓ>0 및 𝒞ℓ′(ρℓ)>0을 prime-analysis.md §3에서 비형식으로 증명한다. 해당 결과 prime_analytic은 검토 k011d78d902664efbb1f1ef0d601484a7에서 supported다. 정의 채택과 별도의 수학적 판정이다. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §3 |
| 기록별 이명 | |

## 36. 인접 차분 · Δⱼ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 인접 차분 · Δⱼ,ℓ |
| 종류 | 함수 |
| 정의 | j∈ℕ, ℓ≥1에서 Δⱼ,ℓ:=Aⱼ,ℓ₊₁−2Aⱼ,ℓ+Aⱼ,ℓ₋₁. 정수 차분이다. Δ₀,ℓ=0이며 j≥1에는 bⱼ,ℓ₊₁−bⱼ,ℓ와 같다. |
| 잘 정의됨 | A가 정의되어 있으므로 유일하다. |
| Lean 대응 | 함수 정의는 미형식화. 기록 k12c717105e4f436ebbc4a311ae64134a/OriginalBridge.lean의 ParkingCurvature.original_curvature가 원 b와의 연결을 증명한다. 검토 k011d78d902664efbb1f1ef0d601484a7/original_bridge는 accepted/matches다. 같은 연결을 k2809252f588641b39bcaf13513db3951/PInterface.lean의 `ParkingLastCar.b_curvature`가 재현하며, 검토 k41050a1934d84a1fae10f1e3af32d0a1에서 accepted/matches다. 함수 Δ 자체의 새 선언은 아니다. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Initial.lean Delta_eq_original/J_row_Delta/Z_row_Delta. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| Lean 추가 대응 | k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 ParkingWidth.original_curvature_widResponse는 n:ℕ+,ℓ≥1,n≤2ℓ+3에서 실제 원 b의 차를 응답 재귀와 전체 linearGap으로 나타낸다. k0d67ab01617a4814aae5265ebb219b1a에서 accepted/matches. 적분·양수 원천·κ의 일반 형식 동일성은 포함하지 않는다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: original_boundary_exact_sum, original_boundary_quartic_lower. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/GainLoss.lean의 ParkingForest.delta 및 delta_gain_loss, delta_normalized와 세 부호 동치는 n,ℓ≥1의 원 정수 인접 차를 다룬다. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. 이 구현은 §36의 j=0 계수 경계까지 확장한 선언은 아니다. |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/curvature.md 머리말 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 Dⱼ,ℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. |


현재 형식 수용 보완: k0c2f8df2c56e4828bbf691cacca83b2a/lean/BoundaryForest.lean의 original_delta_empty_path는 n,ℓ≥1,n≤2(ℓ+1)+1에서 원 Δ=D⁽⁰⁾+D⁽¹⁾를 증명한다. kfaeb6535dad54592857b1f726417d954에서 accepted/matches다. 부호 정리나 일반 성분 사슬 합 인증은 아니다.

## 37. 누적 증분 · eⱼ,ᵣ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 누적 증분 · eⱼ,ᵣ |
| 종류 | 함수 |
| 정의 | j∈ℕ, r≥1에서 eⱼ,ᵣ:=Aⱼ,ᵣ−Aⱼ,ᵣ₋₁. e₀,ᵣ=0이다. b₀,ᵣ를 정의하는 관례가 아니다. |
| 잘 정의됨 | 누적 개수의 단조성으로 비음수. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/curvature.md 머리말 |
| 기록별 이명 | |

## 38. 마지막 차량 가중치 · ωₖ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 마지막 차량 가중치 · ωₖ,ℓ |
| 종류 | 함수 |
| 정의 | k,ℓ∈ℕ에서 ωₖ,ℓ:=min(k+1,ℓ+1). |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 기록 k12c717105e4f436ebbc4a311ae64134a/Curvature.lean의 ParkingCurvature.weight는 이 값을 정수로 포함시킨다. 국소 항등식 결과의 검토는 k011d78d902664efbb1f1ef0d601484a7/local_lean이다. k2809252f588641b39bcaf13513db3951/Recurrence.lean의 `A_recurrence`에도 같은 자연수 최솟값 가중치가 나타난다. |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/curvature.md 식 (11)의 국소 증명 |
| 기록별 이명 | 기록 k12c717105e4f436ebbc4a311ae64134a의 wₖ,ℓ. 이 옛 기호는 이후 산출에서 사용하지 않는다. |

## 39. 포화 손실 · Kₙ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 포화 손실 · Kₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥2, 1≤ℓ≤n−1, 2ℓ≥n−1에서 Kₙ,ℓ:=binom(n−1,ℓ)TℓTₙ₋₁₋ℓ. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/curvature.md 마지막 절 |
| 기록별 이명 | |

## 40. 정규화 전체 계수 · fⱼ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정규화 전체 계수 · fⱼ |
| 종류 | 함수 |
| 정의 | j∈ℕ에서 fⱼ:=Tⱼ/j!. |
| 잘 정의됨 | j!>0. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/curvature.md 마지막 절 |
| 기록별 이명 | |

## 41. 단위 허용 거리 정규화 계수 · uₙ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 단위 허용 거리 정규화 계수 · uₙ |
| 종류 | 함수 |
| 정의 | n∈ℕ에서 uₙ:=Aₙ,₁/n!. 선호 성분 aᵢ와 구분한다. |
| 잘 정의됨 | n!>0. |
| Lean 대응 | 미형식화 |
| 출처 | k12c717105e4f436ebbc4a311ae64134a/prime-analysis.md §4 |
| 기록별 이명 | |

## 42. 선착 조건

| 칸 | 내용 |
|---|---|
| 이름·기호 | 선착 조건 · Cert(O;a,p) |
| 종류 | 성질·관계 |
| 정의 | m,N∈ℕ, 초기 점유 O⊆[N], 함수 a,p:[m]→[N]에 대해 Cert(O;a,p) :⇔ p가 단사이고, 모든 i∈[m]에 pᵢ∉O 및 aᵢ≤pᵢ이며, 모든 i∈[m], s∈[N]에 aᵢ≤s<pᵢ이면 s∈O 또는 ∃j∈[m], j<i 및 pⱼ=s이다. 여기의 p는 임의 배정 함수이며 실제 주차 자리임은 조건과 원 실행의 동치로 확인한다. |
| 잘 정의됨 | 해당 없음. 원 기록 Certificates.lean의 certified_run/run_certified가 처음 O를 점유한 원 실행의 출력과 동치임을 증명한다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/Certificates.lean의 `ParkingLastCar.Certified`. Fin 값에 1을 더하는 원 번호 대응을 사용한다. |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 선착 조건 정의 문단 및 Certificates.lean |
| 기록별 이명 | 없음 |

## 43. 변위 제한 실행 기록

| 칸 | 내용 |
|---|---|
| 이름·기호 | 변위 제한 실행 기록 · Trₙ,ℓ |
| 종류 | 대상 |
| 정의 | n,ℓ∈ℕ에서 Trₙ,ℓ := {(a,p)∈([n]→[n])² : Cert(∅;a,p) 및 ∀i∈[n], pᵢ−aᵢ≤ℓ}. 차는 정수 차이며 선착 조건에 의해 비음수다. n=0에서는 빈 함수 쌍 하나이고 차량별 제한은 공허하다. |
| 잘 정의됨 | 유한 부분집합이다. 같은 선호의 배정 유일성과 원 제한 PF와의 동치는 traceEquiv, 그 개수와 원 A의 일치는 card_trace로 증명한다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/Certificates.lean의 `ParkingLastCar.Trace`, `traceEquiv`, `card_trace` |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Profile.lean의 td_traceOf/profileOriginalEquiv. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 변위 제한 실행 기록 정의 문단 및 Certificates.lean |
| 기록별 이명 | 없음 |

## 44. 왼쪽 차량 번호 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 왼쪽 차량 번호 집합 · Iₓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ, x=(a,p)∈Trₙ₊₁,ℓ에서 Iₓ := {i∈[n] : pᵢ<pₙ₊₁}. |
| 잘 정의됨 | 주어진 배정에서 유일한 부분집합이다. leftSet_card는 원 번호로 \|Iₓ\|=pₙ₊₁−1임을 증명한다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/LastCar.lean의 `ParkingLastCar.leftSet`. 내부 마지막 자리 값은 원 번호보다 1 작다. |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 왼쪽 차량 번호 집합 정의 및 LastCar.lean |
| 기록별 이명 | 없음 |

## 45. 도착 번호 표준화

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 번호 표준화 · ι_I |
| 종류 | 함수 |
| 정의 | n∈ℕ, I⊆[n]에서 ι_I:[\|I\|]→[n+1] := I의 원소들을 증가하는 순서로 나열한 함수. 그 상은 I이며 마지막 번호 n+1을 포함하지 않는다. I=∅이면 빈 함수다. |
| 잘 정의됨 | 유한 선형순서의 증가하는 열거는 존재하고 유일하다. 공개 구현은 Finset.orderIsoOfFin을 쓴다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/LastCar.lean의 `ParkingLastCar.index I` |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 증가하는 번호 열거 문단 및 LastCar.lean |
| 기록별 이명 | 없음 |

## 46. 제한 기록 분해 자료

| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 기록 분해 자료 · Ξₙ,ℓ |
| 종류 | 대상 |
| 정의 | n,ℓ∈ℕ에서 Ξₙ,ℓ := ⨿(I⊆[n]) {0,…,min(\|I\|,ℓ)} × Tr_\|I\|,ℓ × Tr_n−\|I\|,ℓ. ⨿는 I 자체도 보존하는 서로소 합이며 Iᶜ=[n]∖I이다. |
| 잘 정의됨 | 모든 항이 유한하다. 마지막 변위 선택은 0부터의 정수이며 원 번호 집합 [·]과 구별한다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/Assembly.lean의 `ParkingLastCar.Pieces`. 오른쪽 자식 크기는 Iᶜ.card, 변위 선택은 Fin(min(\|I\|+1,ℓ+1))으로 표현한다. |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 역조립 입력 정의 및 Assembly.lean |
| 기록별 이명 | 없음 |

## 47. 원 제한 분해 자료

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 제한 분해 자료 · Ξᴾᶠₙ,ℓ |
| 종류 | 대상 |
| 정의 | n,ℓ∈ℕ에서 Ξᴾᶠₙ,ℓ := ⨿(I⊆[n]) {0,…,min(\|I\|,ℓ)} × {α_L∈PF_\|I\| : M̄(α_L)≤ℓ} × {α_R∈PF_n−\|I\| : M̄(α_R)≤ℓ}. |
| 잘 정의됨 | 유한 부분집합들의 합·곱이다. Ξₙ,ℓ와 동치지만 한쪽은 선호·배정 쌍을 저장하므로 같은 집합으로 정의하지 않는다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/Equivalence.lean의 `ParkingLastCar.OriginalPieces`, `piecesOriginalEquiv` |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 최종 동치 오른쪽 집합 및 Equivalence.lean |
| 기록별 이명 | 없음 |

## 48. 마지막 차량 분해 대응

| 칸 | 내용 |
|---|---|
| 이름·기호 | 마지막 차량 분해 대응 · Φₙ,ℓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ, α=(aᵢ)∈PFₙ₊₁, M̄(α)≤ℓ에 대해 실제 배정 pᵢ:=sᵢ(α), x:=(a,p), k:=pₙ₊₁−1, I:=Iₓ, t:=pₙ₊₁−aₙ₊₁로 두고 Φₙ,ℓ(α):=(I,t,α_L,α_R)∈Ξᴾᶠₙ,ℓ로 정의한다. 여기서 α_L(r):=a_{ι_I(r)} (r∈[k]), α_R(r):=a_{ι_{Iᶜ}(r)}−(k+1) (r∈[n−k]). |
| 잘 정의됨 | leftSet_card로 \|I\|=k. last_barrier, certified_restrict와 extractLeft/extractRight가 자식의 원 선호 범위·성공·변위 제한을 보장한다. t∈{0,…,min(k,ℓ)}이다. assemble_extract/extract_assemble와 originalLastCarEquiv가 원 목록을 역조립하는 동치임을 증명한다. n=0 및 빈 자식은 기존 M̄만 사용한다. |
| Lean 대응 | k2809252f588641b39bcaf13513db3951/Equivalence.lean의 `ParkingLastCar.originalLastCarEquiv`의 정방향; 의존 원문 Certificates/LastCar/Assembly/Extraction.lean |
| 출처 | k2809252f588641b39bcaf13513db3951/exposition.md의 양방향 분해 및 최종 동치 설명, Equivalence.lean |
| 기록별 이명 | 없음 |

## 49. 원형 주차 확률모형

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원형 주차 확률모형 · 𝔓ₙ |
| 종류 | 대상 |
| 정의 | n≥1에서 𝔓ₙ := 표본공간 [n+1]ⁿ, 각 표본의 확률 (n+1)⁻ⁿ인 균일 확률공간과 그 표본을 선호 목록으로 쓰는 원형 주차 과정의 쌍. 자리는 1,…,n+1, 다음 순서는 1→2→⋯→n+1→1이다. 차는 번호 순서로 도착하여 선호 자리부터 이 순서의 첫 빈자리에 주차하며 개별 원형 변위는 배정까지 지나간 점유 자리 수다. |
| 잘 정의됨 | n대와 n+1자리이므로 각 도착 때 빈자리가 남고 선택은 유일하다. 원 PF와의 회전 대응 및 통계 보존은 검토 k8489c648c0964cb3b3bf9fe09c296340의 uniform_tail에서 비형식 범위로 supported이며 전체 Lean 연결은 없다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §4 |
| 기록별 이명 | 없음 |

## 50. 정확 변위 차량 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정확 변위 차량 수 · Yℓ |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ, ℓ∈ℕ에서 Yℓ(α):=#{i∈[n]:dᵢ(α)=ℓ}. |
| 잘 정의됨 | 유한 집합의 개수. |
| Lean 대응 | k21248694f4c24bad89564e3143deba52/Marked.lean의 `ParkingMarked.exactCars`의 n≥1 제한. 구현은 n=0에도 빈 개수 0을 반환한다. 검토 k8489c648c0964cb3b3bf9fe09c296340의 original_marked_lean에서 accepted/matches로 확인한 원 정의의 구현 대응이다. |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §2 및 Marked.lean |
| 기록별 이명 | 없음 |

## 51. 고변위 차량 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 고변위 차량 수 · Zℓ |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ, ℓ∈ℕ에서 Zℓ(α):=#{i∈[n]:dᵢ(α)≥ℓ}. |
| 잘 정의됨 | 유한 집합의 개수. |
| Lean 대응 | k21248694f4c24bad89564e3143deba52/Marked.lean의 `ParkingMarked.highCars`의 n≥1 제한. 구현은 n=0에도 빈 개수 0을 반환한다. 검토 k8489c648c0964cb3b3bf9fe09c296340의 original_marked_lean에서 accepted/matches로 확인한 원 정의의 구현 대응이다. |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §2 및 Marked.lean |
| 기록별 이명 | 없음 |

## 52. 변위 표시 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 변위 표시 개수 · ℛₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ∈ℕ에서 ℛₙ,ℓ:=Σ(α∈PFₙ)Yℓ(α). 계수 경계는 ℛ₀,ℓ:=0이다. |
| 잘 정의됨 | 유한 합이다. 같은 목록의 여러 차량을 각각 세므로 정확 개수 b와 다른 함수다. |
| Lean 대응 | k21248694f4c24bad89564e3143deba52/Marked.lean의 `ParkingMarked.markedCount (n : ℕ+) ℓ` (크기 0 경계는 구현 밖). 검토 k8489c648c0964cb3b3bf9fe09c296340의 original_marked_lean에서 accepted/matches로 확인한 원 정의의 구현 대응이다. |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §2 및 Marked.lean |
| 기록별 이명 | 기록 k21248694f4c24bad89564e3143deba52의 Rₙ,ℓ. 계산기 값에 쓰였던 기존 이명 Rℓ(n)와 구별하여 ℛ로 개명했다. 옛 표기는 해당 기록 해독에만 쓴다. |

## 53. 동반 표시 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 동반 표시 개수 · Ωₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ∈ℕ에서 Ωₙ,ℓ:=Σ(α∈PFₙ)Yℓ(α)(Zℓ(α)−1), 정수 차를 쓰며 Yℓ=0인 항의 곱은 0이다. 계수 경계 Ω₀,ℓ:=0. |
| 잘 정의됨 | 유한 합. Yℓ>0이면 Zℓ≥1이므로 각 항은 비음수이고 자연수 잘린 차로 계산한 곱과 같다. 동반 발생 상계는 검토 k8489c648c0964cb3b3bf9fe09c296340의 uniform_tail에서 비형식 범위로 supported이며 전체 Lean 연결은 없다. |
| Lean 대응 | k21248694f4c24bad89564e3143deba52/Marked.lean의 `ParkingMarked.overlapCount (n : ℕ+) ℓ` (크기 0 경계는 구현 밖). 검토 k8489c648c0964cb3b3bf9fe09c296340의 original_marked_lean에서 accepted/matches로 확인한 원 정의의 구현 대응이다. |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §2 및 Marked.lean |
| 기록별 이명 | 없음 |

## 54. 표시 개수 간격

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 개수 간격 · Jₙ,ℓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ에서 Jₙ,ℓ:=ℛₙ,ℓ−ℛₙ,ℓ₊₁∈ℤ. 특히 J₀,ℓ=0. |
| 잘 정의됨 | 정의된 두 정수의 차다. 원 기록의 양수성·닫힌 공식은 검토 k8489c648c0964cb3b3bf9fe09c296340의 marked_formula에서 비형식 범위로 supported이며 일반 Lean 연결은 없다. |
| Lean 대응 | 별도 J 함수는 미형식화. k21248694f4c24bad89564e3143deba52/Marked.lean의 `ParkingMarked.original_signed_gap_lower_bound`는 두 markedCount의 정수 차를 직접 쓴다. 이 부분 부등식은 검토 k8489c648c0964cb3b3bf9fe09c296340의 original_marked_lean에서 accepted/matches다. 닫힌 공식 전체의 형식화는 아니다. |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §2–3 |
| 기록별 이명 | 없음 |

## 55. 전체 지수 생성함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 지수 생성함수 · Ψ |
| 종류 | 함수 |
| 정의 | Ψ(x):=Σ(n≥0)Tₙxⁿ/n!∈ℚ[[x]]. |
| 잘 정의됨 | 정의된 유리 계수의 형식급수다. 제한 누적 지수 생성함수 ℱℓ와 구별한다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §3 |
| 기록별 이명 | 없음 |

## 56. 전체 생성함수 보조 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 생성함수 보조 급수 · τ |
| 종류 | 함수 |
| 정의 | τ(x):=xΨ(x)∈ℚ[[x]]. |
| 잘 정의됨 | 형식급수의 곱이다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §3 |
| 기록별 이명 | 없음 |

## 57. 표시 간격 지수 생성함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 간격 지수 생성함수 · 𝒥ℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 𝒥ℓ(x):=Σ(n≥1)Jₙ,ℓxⁿ/n!∈ℚ[[x]]. |
| 잘 정의됨 | 정의된 계수의 형식급수다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/exposition.md §3 |
| 기록별 이명 | 없음 |

## 58. 포화 결손

| 칸 | 내용 |
|---|---|
| 이름·기호 | 포화 결손 · Eₙ,ℓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ에서 Eₙ,ℓ:=Tₙ−Aₙ,ℓ. 차는 정수 차다. |
| 잘 정의됨 | A가 PF의 부분집합을 세므로 비음수다. 기존 누적 증분 eⱼ,ᵣ와 다른 함수다. |
| Lean 대응 | k5bedcf491ebd45f1a1dcb7fb84fad705/Deficit.lean의 ParkingSign.deficit는 같은 Eₙ,ℓ의 구현 대응이다. 새 일반 재귀·상계의 작성자 형식 결과는 검토 kdd117882498f411286f292377dc9abda에서 해당 부분 범위 supported다. 형식 결과는 accepted/matches이고 비형식 확장은 미형식화다. |
| 출처 | k21248694f4c24bad89564e3143deba52/remaining-sign.md §1 |
| 기록별 이명 | 없음 |

## 59. 고변위 표시 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 고변위 표시 다항식 · Gₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ∈ℕ에서 Gₙ,ℓ(z):=Σ(α∈PFₙ)z^{Zℓ(α)}∈ℤ[z]. 경계 G₀,ℓ(z):=1. 다항식의 상수 단항식 z⁰은 1이다. |
| 잘 정의됨 | 유한 다항식이다. z=0 평가에서도 상수 단항식은 1이다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/remaining-sign.md §3 |
| 기록별 이명 | 없음 |

## 60. 이항 표시 모멘트

| 칸 | 내용 |
|---|---|
| 이름·기호 | 이항 표시 모멘트 · μₙ,ℓ,ₚ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ,p∈ℕ에서 μₙ,ℓ,ₚ:=Σ(α∈PFₙ)binom(Zℓ(α),p). 경계 μ₀,ℓ,₀:=1, μ₀,ℓ,ₚ:=0(p>0). |
| 잘 정의됨 | 유한 합이다. Gₙ,ℓ(1+y)의 yᵖ 계수라는 관계는 이항전개로 읽는다. 일반 볼록성과 정확 교대합은 검토 k8489c648c0964cb3b3bf9fe09c296340의 moment_and_deficit에서 비형식 범위로 supported다. 교대합의 전칭 부호 제어는 미해결이며 일반 Lean 연결도 없다. |
| Lean 대응 | 미형식화 |
| 출처 | k21248694f4c24bad89564e3143deba52/remaining-sign.md §3 |
| 기록별 이명 | 없음 |

## 61. ℓ-구간 주차 함수 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | ℓ-구간 주차 함수 집합 · IPFₙ(ℓ) |
| 종류 | 대상 |
| 정의 | n∈ℕ, ℓ∈ℕ에서 IPFₙ(ℓ):={α∈PFₙ:M̄(α)≤ℓ}. n≥1에서는 M̄=M이고, n=0에서는 빈 목록 하나다. 최대 변위 M의 크기 0 값을 새로 정하지 않는다. |
| 잘 정의됨 | 정의된 유한 집합의 부분집합이다. 크기 0에는 기존 보조 M̄만 사용한다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §2.1·2.4 및 glossary-proposals.md. Celano 외 arXiv:2507.07243 Definition 2.7; 문면의 양의 ℓ와 달리 실제 ℓ=0 사용을 포함한다. Aguilar-Fraga 외 arXiv:2311.14055v5의 빈 경계를 따른다. |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c §4.4의 단위 구간 주차 함수 집합 UPFₙ은 IPFₙ(1)과 동일하다. 매개변수 1의 특수화이므로 별도 정본 이름을 만들지 않는다. |

## 62. 최대 변위 수준 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 변위 수준 집합 · IPFₙ(ℓ)^max |
| 종류 | 대상 |
| 정의 | n≥1, ℓ∈ℕ에서 IPFₙ(ℓ)^max:={α∈PFₙ:M(α)=ℓ}. 크기 0에는 정의하지 않는다. |
| 잘 정의됨 | 정의된 유한 집합의 부분집합이다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §2.3 및 glossary-proposals.md; Celano 외 §6. 그 개수는 기존 정확 개수 bₙ,ℓ다. |
| 기록별 이명 | 없음 |

## 63. 절단 길이

| 칸 | 내용 |
|---|---|
| 이름·기호 | 절단 길이 · L_ℓ(i;σ) |
| 종류 | 함수 |
| 정의 | n≥1, σ∈𝔖ₙ, i∈[n], ℓ∈ℕ에서 L_ℓ(i;σ):=min(ℓ+1,hᵢ(σ)). 여기서 hᵢ는 §24의 선호 선택 폭이다. |
| 잘 정의됨 | 기존 hᵢ와 자연수 최솟값으로 정의된다. 원 제안의 t=min{u∈[i]:∀k∈[u,i],σₖ≤σᵢ}에 대해 i−t+1=hᵢ이므로 같은 정의다. 절단 전 hᵢ와 절단 후 L_ℓ는 다른 함수다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.3 및 glossary-proposals.md; Celano 외 식 (6). hᵢ의 변수명을 π에서 σ로 바꾼 것뿐이다. |
| 기록별 이명 | 없음 |

## 64. 총 변위

| 칸 | 내용 |
|---|---|
| 이름·기호 | 총 변위 · 𝒟(α) |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ에서 𝒟(α):=Σ(i∈[n])dᵢ(α). |
| 잘 정의됨 | 이미 정의된 변위의 유한 합이다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.7 및 glossary-proposals.md; Celano 외 Definition 2.5, Selig–Zhu의 변위 합. 이 정의 채택만으로 로그오목성 정리를 수용하지 않는다. |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c의 D(α), disp(α). 기존 인접 차분의 옛 Dⱼ,ℓ 등과 혼동을 피하여 𝒟로 개명했다. |

## 65. 비감소 주차 함수 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 비감소 주차 함수 집합 · PFₙ↑ |
| 종류 | 대상 |
| 정의 | n≥1에서 PFₙ↑:={α∈PFₙ:a₁≤a₂≤⋯≤aₙ}. |
| 잘 정의됨 | 유한 집합의 부분집합이다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.5 및 glossary-proposals.md; Celano 외 PFₙ↑, Selig–Zhu arXiv:2403.17438v2의 PF_n^inc. |
| 기록별 이명 | 없음 |

## 66. Fubini 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | Fubini 수 · Fubₙ |
| 종류 | 함수 |
| 정의 | n≥1에서 Fubₙ:=[n]의 순서 있는 집합 분할의 수. 즉 합집합이 [n]인 비어 있지 않은 서로소 부분집합들의 순서 있는 나열을 센다. |
| 잘 정의됨 | 유한 개의 유한 나열을 센다. 동치식 Σ(k=1..n)k!S(n,k)에서 S는 제2종 Stirling 수다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.1 및 glossary-proposals.md; Celano 외 Remark 2.12, OEIS A000670. Aₙ,₁과의 등식은 문헌의 대응 정리이며 정의 채택과 구별한다. |
| 기록별 이명 | 없음 |

## 67. 원형 선형 탐사의 최대 변위

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원형 선형 탐사의 최대 변위 · d_max(h) |
| 종류 | 함수 |
| 정의 | 정수 m≥2, 1≤v<m, h=(h₁,…,hᵥ)∈[m]ᵛ에서 항목 i=1,…,v를 순서대로 hᵢ부터 순환 순서 1→⋯→m→1의 첫 빈칸 qᵢ에 넣고 d_max(h):=max(1≤i≤v)((qᵢ−hᵢ) mod m). mod 값은 {0,…,m−1}에서 취한다. v=0의 최댓값은 정의하지 않는다. |
| 잘 정의됨 | v<m이므로 매 단계 빈칸이 있고 첫 빈칸이 유일하다. v≥1이므로 최댓값이 존재한다. m=v+1의 균일 무작위화는 §49의 𝔓ᵥ와 같은 과정이지만 이 함수는 다른 적재율도 포함한다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.6 및 glossary-proposals.md; Petersson (CPC 22 (2013))의 모형. 제안의 0≤v<m 중 최대가 실제 정의된 v≥1만 명시했다. 원 dᵢ 기호는 재정의하지 않았다. |
| 기록별 이명 | 없음 |

## 68. 단위 허용 거리의 블록 구조

| 칸 | 내용 |
|---|---|
| 이름·기호 | 단위 허용 거리의 블록 구조 · 𝓑(β) |
| 종류 | 함수 |
| 정의 | n≥1, β=(b₁,…,bₙ)∈IPFₙ(1)에서 (bᵢ,i)를 값 우선·번호 차선의 사전식 순서로 정렬한다. 정렬 위치 t≥2의 값이 t이면 그 항 바로 앞에 구분선을 넣는다. 𝓑(β):=그 구분선으로 얻는 원 번호들의 순서 있는 비어 있지 않은 목록들 (B₁,…,B_q). 블록의 r번째 원소는 목록 Bⱼ의 r번째 번호다. |
| 잘 정의됨 | 사전식 순서는 전순서이고 번호가 다르므로 정렬과 분할이 유일하다. 동일한 값의 두 발생은 원 번호 순서로 구별된다. IPFₙ(1)에서 각 블록의 값이 원 목록에서도 이 순서로 나온다는 성질은 원문 Theorem 2.10의 주장으로, 정의와 구별한다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4의 제안 누락을 검토 k729b98f8fd5b48759aa02dc87308ae48 §5에 따라 ka9e88e95ff094c8f92f8cb44c8c8cbda이 처리. Celano 외 Theorem 2.10. 표준적인 안정 정렬로 원문의 발생 순서 관례를 명시화했다. |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c의 블록 구조 π₁|⋯|π_m. 주차 결과 순열 π와 다른 대상이다. 블록을 본문에서 두 대상을 혼동한 오류는 검토가 발견하지 않았다. |

## 69. 블록 셋째 이후 위치 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 블록 셋째 이후 위치 집합 · S^blk(β) |
| 종류 | 함수 |
| 정의 | n≥1, β∈IPFₙ(1), 𝓑(β)=(B₁,…,B_q)에서 S^blk(β):={Bⱼ(r):1≤j≤q, 3≤r≤길이(Bⱼ)}⊆[n]. |
| 잘 정의됨 | §68의 유일한 유한 목록들의 위치 집합이다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4의 제안 누락; Celano 외 Theorem 4.12. 검토 k729b98f8fd5b48759aa02dc87308ae48 §5에 따라 ka9e88e95ff094c8f92f8cb44c8c8cbda이 처리. |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c의 𝒮(β). |

## 70. 뒤따르는 블록 둘째 위치 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 뒤따르는 블록 둘째 위치 집합 · R^blk(β) |
| 종류 | 함수 |
| 정의 | n≥1, β∈IPFₙ(1), 𝓑(β)=(B₁,…,B_q)에서 R^blk(β):={Bⱼ(2):2≤j≤q, 길이(Bⱼ)≥2, Bⱼ(2)>Bⱼ₋₁(길이(Bⱼ₋₁))}⊆[n]. 부등식은 원 목록의 위치 번호를 비교한다. |
| 잘 정의됨 | §68의 블록은 비어 있지 않으므로 앞 블록의 마지막 위치가 유일하다. |
| Lean 대응 | 미형식화 |
| 출처 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4의 제안 누락; Celano 외 Theorem 4.12. 검토 k729b98f8fd5b48759aa02dc87308ae48 §5에 따라 ka9e88e95ff094c8f92f8cb44c8c8cbda이 처리. |
| 기록별 이명 | 기록 kdd440866190648ffb7237cbd5b1d4c7c의 𝓡(β). 변위 표시 개수 ℛₙ,ℓ와도 다른 대상이다. |

## 71. 선형 결손 상계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 선형 결손 상계 · ℒₙ,ℓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ에서 ℒ₀,ℓ:=0, ℒₙ₊₁,ℓ:=Σ(k=0..n)binom(n,k)[max(k−ℓ,0)TₖTₙ₋ₖ+(ℓ+k+2)Tₖℒₙ₋ₖ,ℓ]∈ℤ. |
| 잘 정의됨 | 오른쪽은 더 작은 크기만 쓰는 삼각 재귀이므로 존재하고 유일하다. E≤ℒ 및 n≤2ℓ+3에서 E=ℒ라는 성질은 새 연구의 주장으로 검토 kdd117882498f411286f292377dc9abda에서 해당 부분 범위 supported다. 형식 결과는 accepted/matches이고 비형식 확장은 미형식화다. |
| Lean 대응 | k5bedcf491ebd45f1a1dcb7fb84fad705/LinearDeficit.lean의 ParkingSign.linearDeficit ℓ n. 작성자는 일반 상계·일치의 컴파일과 공리 감사를 보고했으나 검토 kdd117882498f411286f292377dc9abda에서 original-deficit-majorant가 accepted/matches다. |
| Lean 추가 대응 | k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 ParkingWidth.widResponse_excess는 모든 n,ℓ∈ℕ에서 EGF 원천 (k−ℓ)₊Tₖ와 매개변수 ℓ+1의 응답 재귀가 ParkingSign.linearDeficit와 같음을 증명한다. k0d67ab01617a4814aae5265ebb219b1a에서 accepted/matches. 일반 적분과 재귀의 식별은 아직 비형식이다. |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/deficit.md §2 및 glossary-proposals.md. |
| 기록별 이명 | 기록 k5bedcf491ebd45f1a1dcb7fb84fad705의 Lₙ,ℓ. 이번에 새로 채택한 절단 길이 L_ℓ(i;σ)와 머리기호 혼동을 피하여 ℒ로 개명했다. |

## 72. 수송 자식 가중치

| 칸 | 내용 |
|---|---|
| 이름·기호 | 수송 자식 가중치 · ϑₙ,ⱼ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 0≤j<n에서 ϑₙ,ⱼ:=binom(n−1,j)Tₙ₋₁₋ⱼ. |
| 잘 정의됨 | 정의된 두 자연수의 곱이다. |
| Lean 대응 | 미형식화 |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/transport.md §1 및 glossary-proposals.md. |
| 기록별 이명 | 없음 |

## 73. 인접 수송 경계합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 인접 수송 경계합 · 𝔅ₙ,ℓ |
| 종류 | 함수 |
| 정의 | 정수 n≥4, 1≤ℓ≤n−3, n≤2ℓ+1에서 𝔅ₙ,ℓ:=(n−1)binom(n−1,ℓ+1)TℓTₙ₋ℓ₋₂+Kₙ,ℓ−Kₙ,ℓ₊₁∈ℤ. |
| 잘 정의됨 | 가정은 두 K의 정의역을 보장한다. §68의 블록 구조 𝓑와 다른 대상이다. |
| Lean 대응 | 미형식화 |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/transport.md §1 및 glossary-proposals.md. |
| 기록별 이명 | 없음 |

## 74. 말단 항 유지 수송 상계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 말단 항 유지 수송 상계 · 𝔘⁽ˢ⁾ₙ,ℓ |
| 종류 | 함수 |
| 정의 | 𝔅ₙ,ℓ의 정의역과 정수 s≥1, s+3≤n−ℓ에서 𝔘⁽ˢ⁾ₙ,ℓ:=𝔅ₙ,ℓ+Σ(j=ℓ+2..ℓ+s+1)ϑₙ,ⱼ[(n+ℓ+3−j)Δⱼ,ℓ₊₁−(n+ℓ−j)Δⱼ,ℓ]+3Σ(j=ℓ+s+2..n−1)ϑₙ,ⱼΔⱼ,ℓ. |
| 잘 정의됨 | 정의된 정수의 유한 합이고 빈 합은 0이다. 상계 성질은 나머지 자식의 하강·C 가정을 둔 새 연구의 주장이다. 정의 자체는 C의 참 여부와 독립적이다. 기존 봉우리 위치 조건 Uₙ(c)와 다르다. |
| Lean 대응 | 미형식화 |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/transport.md §2 및 glossary-proposals.md. |
| 기록별 이명 | 없음 |

## 75. 고정 끝 거리 표시 간격 극한

| 칸 | 내용 |
|---|---|
| 이름·기호 | 고정 끝 거리 표시 간격 극한 · γᵣ |
| 종류 | 함수 |
| 정의 | 정수 r≥1에서 γᵣ:=exp(1−r)r^(r−1)/(r−1)!∈ℝ. |
| 잘 정의됨 | 분모 (r−1)!는 양수다. 명칭의 극한 성질은 새 tail-curvature.md (T8)의 주장으로 검토 kdd117882498f411286f292377dc9abda에서 해당 부분 범위 supported다. 형식 결과는 accepted/matches이고 비형식 확장은 미형식화다. |
| Lean 대응 | 미형식화 |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/tail-curvature.md §3 및 glossary-proposals.md. |
| 기록별 이명 | 없음 |

## 76. 포화 초과 가중 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 포화 초과 가중 급수 · 𝒬ℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에서 𝒬ℓ(x):=Σ(k≥ℓ+1)(k−ℓ)fₖxᵏ∈ℚ[[x]]. |
| 잘 정의됨 | 계수마다 값이 지정된 형식급수다. 해석적 수렴을 정의의 전제로 쓰지 않는다. |
| Lean 대응 | 미형식화 |
| 재첨자화 확인 | 기록 k526e621123a64cee8d48c8b3c7c79a04의 전체 계수 꼬리 원천 Qᵗᵃⁱˡ_x(z)는 정확히 𝒬ₓ₋₁(z)다(x≥1). 계수 (r+1−x)T_r/r!=(r−(x−1))f_r가 같으므로 새 정의를 만들지 않는다. |
| Lean 추가 대응 | k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 ParkingWidth.excessSource l k=(k−l)₊Tₖ는 이 급수의 정수 EGF 계수 구현이다. widResponse_excess의 재귀 연결은 k0d67ab01617a4814aae5265ebb219b1a에서 accepted/matches. 급수 전체의 PowerSeries 식별을 수용한 것은 아니다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: sourceSeries_excess_tail. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k5bedcf491ebd45f1a1dcb7fb84fad705/deficit.md §3 및 glossary-proposals.md. |
| 기록별 이명 | 기록 k526e621123a64cee8d48c8b3c7c79a04의 전체 계수 꼬리 원천 Qᵗᵃⁱˡ_x(z)=𝒬ₓ₋₁(z). |

## 77. 앞선 큰 값 위치

| 칸 | 내용 |
|---|---|
| 이름·기호 | 앞선 큰 값 위치 · pg_π(j) |
| 종류 | 함수 |
| 정의 | n≥1, π∈𝔖ₙ, j∈[n]에서 pg_π(j):=max({0}∪{i∈[n]:i<j, πᵢ>πⱼ}). |
| 잘 정의됨 | 0을 포함하는 유한 집합의 최댓값이다. 기존 hⱼ=j−pg_π(j)와 정의상 연결된다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.1 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 앞선 큰 값 위치 pg_σ(j). 변수만 정본 π로 바꾼다. |

## 78. 뿌리 있는 숲

| 칸 | 내용 |
|---|---|
| 이름·기호 | 뿌리 있는 숲 · G |
| 종류 | 대상 |
| 정의 | n∈ℕ에서 [n] 위 뿌리 있는 숲 G :⇔ 부모 함수 p_G:{0,…,n}→{0,…,n}로서 p_G(0)=0이고 모든 v∈[n]에서 어떤 k≥1에 p_G^k(v)=0인 것. 0은 가상 뿌리다. |
| 잘 정의됨 | 정의는 유한 함수의 조건이다. 조건은 [n] 안의 자기고리와 순환을 배제한다. |
| Lean 대응 | 미형식화 |
| 현재 형식 대응 | 일반 G 전체는 미형식화다. 감소 숲으로 제한하면 k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean의 ParkingForest.ParentForest와 parent_reaches_zero가 부모 함수와 양의 반복 종료를 구현한다. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. 일반 숲 전체를 구현한 것으로 확대하지 않는다. |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.2 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 뿌리 있는 숲 G. 원 제안의 [n] 위 부모 함수를 p_G(0)=0으로 확장해 반복 표기를 명시화한다. |

## 79. 부분나무 크기

| 칸 | 내용 |
|---|---|
| 이름·기호 | 부분나무 크기 · t_v(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, v∈[n]에서 t_v(G):=1+#{w∈[n]∖{v}: 어떤 k≥1에 p_G^k(w)=v}. 중괄호의 w를 v의 진자손이라 한다. |
| 잘 정의됨 | 유한 집합의 개수다. |
| Lean 대응 | 미형식화 |
| 현재 형식 대응 | 감소 숲 제한에서 k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean의 ParkingForest.subtreeSize, subtreeSize_encode가 부모 반복으로 정의된 이 크기를 구현·식별한다. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. 번호 제약 없는 일반 숲 크기 전체의 Lean 구현은 별도다. |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.2 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 부분나무 크기 h_v(G). 기존 선호 선택 폭 hⱼ와 구별하여 기호를 개명했다. |

## 80. 감소 숲

| 칸 | 내용 |
|---|---|
| 이름·기호 | 감소 숲 · 𝔉↓ₙ |
| 종류 | 대상 |
| 정의 | n∈ℕ에서 𝔉↓ₙ:={G:[n] 위 뿌리 있는 숲이고 모든 v∈[n]에서 p_G(v)=0 또는 p_G(v)>v}. |
| 잘 정의됨 | 유한 부모 함수들의 부분집합이다. 개수나 가중합 항등식은 정의와 구별한다. |
| Lean 대응 | 미형식화 |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean의 ParkingForest.ParentForest, parentEquiv, parent_reaches_zero. 실제 부모 함수 부분타입·가상 뿌리·반복 종료의 일반 연결이며 k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.2 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 감소 숲 F. 원문 F는 개별 원소를 나타내며 이후 감소 숲 G∈𝔉↓ₙ으로 쓴다. |

## 81. 큰 자손 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 큰 자손 수 · rᐳ_v(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, v∈[n]에서 rᐳ_v(G):=#{w∈[n]∖{v}: w>v이고 어떤 k≥1에 p_G^k(w)=v}. |
| 잘 정의됨 | 유한 집합의 개수다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.3 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 큰 자손 수 r_v(G). 기존 매개변수 r·여러 R계열과 구별하도록 기호를 명시했다. |

## 82. 최대 큰 자손 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 큰 자손 수 · rᐳ_max(G) |
| 종류 | 함수 |
| 정의 | n≥1, [n] 위 뿌리 있는 숲 G에서 rᐳ_max(G):=max{rᐳ_v(G):v∈[n]}. 크기 0에는 정의하지 않는다. |
| 잘 정의됨 | n≥1의 비어 있지 않은 유한 집합의 최댓값이다. 원 M과의 분포 일치는 정의가 아닌 탐구의 주장이다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.3 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 최대 큰 자손 수 R(G). 기존 R계열 이명들과 구별하여 개명했다. |

## 83. 최대 변위 끝 거리

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 변위 끝 거리 · δ(α) |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ에서 δ(α):=n−1−M(α). |
| 잘 정의됨 | 원 M≤n−1에 의해 {0,…,n−1}의 정수다. 포화 결손 E 및 총 변위 𝒟와 다르다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §1·§5.2 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 결손 D(α). 기존 결손 E와 여러 D 이명에 충돌하므로 이름과 기호를 개명했다. |

## 84. 사슬 제한 가중합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 제한 가중합 · 𝒲_q(m) |
| 종류 | 함수 |
| 정의 | 정수 q≥1, 0≤m≤2q+1에서 𝒲_q(m):=T_m−Σ(s=q+1..m)binom(m,s)s^(s−1)T_(m−s)∈ℤ. 빈 합은 0이다. |
| 잘 정의됨 | 이미 정의된 개수와 정수들의 유한 합이다. 숲 해석은 별도이며 비음수성은 ka8fb76538efa4aa28114eaab004058ff/exposition.md (4)의 형식급수 논증과 검토 k2f5a509346a04efc9720bfffb293aeee/original_chain_mixture에서 비형식 범위로 수용되었다. 현재 제한 기저 연결의 형식 수용은 아래 보완 대응을 따른다. |
| Lean 대응 | 선행 수용 기록에서는 미형식화. 새 구현은 다음 행에서 구별한다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.canonicalBase k n`은 기존 정의의 ℚ 포함값. 해당 기록 당시에는 전역 원 성분 절단 기저와의 제한 영역 일반 Lean 동일성이 미완료였다. 현재 연결은 아래 보완 대응과 같다. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `ParkingCayley.canonicalWeight k n hk hn`은 k≥1,n≤2k+1에서 이 정수식의 ℚ 포함값이다. `actualBase_eq_canonicalWeight`는 원 성분 절단 기저의 같은 영역 제한과의 무조건 동일성이다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 전역 정의역을 이 항목에 부여하거나 𝔖·𝔐 전체 식별을 주장하지 않는다. |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.6 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 제한 가중합 W_L(m). 기존 보정 원시함수 Wℓ와 충돌하여 이름과 기호를 개명했다. 원 매개변수 L은 q로 옮긴다. |

## 85. 사슬 재귀 가중합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 재귀 가중합 · 𝒴_q(H) |
| 종류 | 함수 |
| 정의 | 정수 q≥1, q<H≤2q+1에서 𝒴_q(H):=q[𝒲_q(H−1)+Σ(q<H′<H)binom(H−1,H′)T_(H−1−H′)𝒴_q(H′)]∈ℤ. |
| 잘 정의됨 | 더 작은 H′만 참조하는 유한 삼각 재귀다. 모든 𝒲 인수는 정의역 안이다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §3.6 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k10f126a516ee4c4caf6cf7cc38d28a09의 사슬 가중합 Y_L(H). 정확 변위 차량 수 Yℓ와 구별하여 이름·기호를 개명했다. |

## 86. 최댓값 면적

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최댓값 면적 · 𝒵 |
| 종류 | 대상 |
| 정의 | [0,1] 위 연속 경로 판본의 표준 브라운 운동 B에서 𝒵:=∫₀¹ sup(0≤u≤t)B_u dt. |
| 잘 정의됨 | 거의 확실히 연속인 경로 위에서 유한한 적분으로 정의되며 영확률 예외 경로에서는 0으로 둔다. 평균·극한 법칙은 정의에 포함하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | k10f126a516ee4c4caf6cf7cc38d28a09/exploration.md §5.2 및 glossary-proposals.md. 정의 처리: k817e480061dd494f8b8fc4f8fb0e60f7. 탐구 결과의 수학적 인정은 별개다. |
| 기록별 이명 | 기록 k24d813562f8a4abfad309a53255354c9의 Brownian 상한 넓이 𝒜, 기록 kdd440866190648ffb7237cbd5b1d4c7c §4.6의 넓이 A. 적분의 정의가 같은 대상이므로 동일시한다.  기록 k10f126a516ee4c4caf6cf7cc38d28a09의 최댓값 면적 Z. 고변위 차량 수 Zℓ와 혼동을 피하여 기호 𝒵로 개명했다. |

## 87. 원형 최대 변위 재척도화

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원형 최대 변위 재척도화 · ξ_m(h) |
| 종류 | 함수 |
| 정의 | 정수 m≥2, h∈[m]^(m−1)에서 ξ_m(h):=(m−d_max(h))/m^(2/3)∈ℝ. 확률모형은 h를 독립 균등하게 뽑는 경우를 기본으로 하며 confined 조건은 최종 칸 m이 비는 사건에 조건화한 분포다. |
| 잘 정의됨 | m>0이므로 분모는 양수이고 §67의 d_max가 정의되어 있다. 두 분포의 동일성은 별도 회전 논증이다. |
| Lean 대응 | 미형식화 |
| 출처 | k24d813562f8a4abfad309a53255354c9/review.md §3–4 및 glossary-proposals.md. 검토가 대조한 Janson–Petersson (2009), Janson (2010)의 정의를 정본 표기로 옮긴다. |
| 기록별 이명 | 기록 k24d813562f8a4abfad309a53255354c9 및 기록 kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.6의 거의 꽉 찬 표의 재척도화 최대 변위 Y^m. 기존 정확 변위 차량 수·사슬 가중합의 Y계열과 구별하여 개명했다. |

## 88. 최댓값 면적 라플라스 변환

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최댓값 면적 라플라스 변환 · φ_𝒵(s) |
| 종류 | 함수 |
| 정의 | 실수 s≥0에서 φ_𝒵(s):=E[exp(−s𝒵)]. |
| 잘 정의됨 | 𝒵≥0이므로 적분 대상은 [0,1] 안이며 기대값이 존재한다. |
| Lean 대응 | 미형식화 |
| 출처 | k24d813562f8a4abfad309a53255354c9/review.md §3–4 및 glossary-proposals.md. 검토가 대조한 Janson–Petersson (2009), Janson (2010)의 정의를 정본 표기로 옮긴다. |
| 기록별 이명 | 기록 k24d813562f8a4abfad309a53255354c9 및 기록 kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.6의 Brownian 상한 넓이의 Laplace 변환 ψ. §86의 동일시와 함께 정본 이름·기호로 개명했다. |

## 89. 최대 변위 재척도화 극한분포

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 변위 재척도화 극한분포 · ν |
| 종류 | 대상 |
| 정의 | 𝒵와 독립인 평균 1의 지수 확률변수 X에 대해 ν:=Law((X/𝒵)^(2/3)). 𝒵=0인 경로에서는 비를 0으로 두는 측정가능한 보조 확장을 사용한다. |
| 잘 정의됨 | 곱확률공간에서 독립 X를 만들 수 있고, 𝒵는 거의 확실히 양수다. 영확률 예외의 확장은 분포를 바꾸지 않는다. ξ_m의 수렴 정리는 정의가 아닌 문헌 주장이다. |
| Lean 대응 | 미형식화 |
| 출처 | k24d813562f8a4abfad309a53255354c9/review.md §3–4 및 glossary-proposals.md. 검토가 대조한 Janson–Petersson (2009), Janson (2010)의 정의를 정본 표기로 옮긴다. |
| 기록별 이명 | 기록 k24d813562f8a4abfad309a53255354c9 및 기록 kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.6의 거의 꽉 찬 표의 재척도화 극한 Y. 원문이 분포를 대상으로 하므로 확률변수의 선택에 의존하지 않는 분포 ν로 명명했다. |

## 90. 허용 거리 비교 인자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 허용 거리 비교 인자 · ηℓ |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ에 대해 ηℓ := (2ℓ+3)/(2ℓ+2)∈ℚ. |
| 잘 정의됨 | 분모 2ℓ+2가 양수다. |
| Lean 대응 | `ParkingLeft.distanceFactor` (Quadratic.lean). |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/exposition.md §2.1; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 91. 제한 순열 가중치

| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 순열 가중치 · ϖq(π) |
| 종류 | 함수 |
| 정의 | n∈ℕ, q≥1, π∈𝔖ₙ에 대해 ϖq(π) := ∏(i∈[n])min(hᵢ(π),q). n=0에서는 빈 곱 1이다. |
| 잘 정의됨 | n≥1에서는 기존 선호 선택 폭의 유한 곱이고 n=0에서는 hᵢ를 평가할 인덱스가 없다. |
| Lean 대응 | 미형식화. |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/attempts.md §4; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 92. 큰 선택 폭 위치 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 큰 선택 폭 위치 수 · Nᐳq(π) |
| 종류 | 함수 |
| 정의 | n∈ℕ, q≥1, π∈𝔖ₙ에 대해 Nᐳq(π) := #{i∈[n]:hᵢ(π)>q}. n=0에서는 0이다. |
| 잘 정의됨 | 유한 집합의 개수다. 원 차량 변위를 세는 Zℓ와 다른 대상이다. |
| Lean 대응 | 미형식화. |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/attempts.md §4; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 93. 문턱 선택 폭 위치 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 문턱 선택 폭 위치 수 · N⁼q(π) |
| 종류 | 함수 |
| 정의 | n∈ℕ, q≥1, π∈𝔖ₙ에 대해 N⁼q(π) := #{i∈[n]:hᵢ(π)=q}. n=0에서는 0이다. |
| 잘 정의됨 | 유한 집합의 개수다. 원 차량 변위를 세는 Yℓ와 다른 대상이다. |
| Lean 대응 | 미형식화. |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/attempts.md §4; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 94. 제한 큰 폭 계승 모멘트

| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 큰 폭 계승 모멘트 · 𝔪⁽ᵃ⁾n,q |
| 종류 | 함수 |
| 정의 | n∈ℕ, q≥1, a∈{1,2}에 대해 𝔪⁽¹⁾n,q := Σ(π∈𝔖ₙ)ϖq(π)Nᐳq(π), 𝔪⁽²⁾n,q := Σ(π∈𝔖ₙ)ϖq(π)Nᐳq(π)(Nᐳq(π)−1). 괄호의 차는 정수 차이며 N=0인 곱은 0이다. n=0의 두 합은 0이다. |
| 잘 정의됨 | 유한 계승 곱의 합이다. 원 PF의 이항 표시 모멘트 μ와 다른 대상이다. |
| Lean 대응 | 미형식화. Python `tilted_probe.moments`의 첫 두 배열. |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/attempts.md §4; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 95. 제한 문턱 폭 표시 합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 문턱 폭 표시 합 · 𝔥n,q |
| 종류 | 함수 |
| 정의 | n∈ℕ, q≥1에 대해 𝔥n,q := Σ(π∈𝔖ₙ)ϖq(π)N⁼q(π). n=0에서는 0이다. |
| 잘 정의됨 | 유한 합이다. 원 변위 표시 개수 ℛ와 다른 대상이다. |
| Lean 대응 | 미형식화. Python `tilted_probe.moments`의 셋째 배열. |
| 출처 | k83ac8ca8d9c44903b97b8979ac04bdd3/attempts.md §4; glossary-proposals.md. 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | 없음 |

## 96. 큰 크기 사슬 집합 · \(\mathfrak C_{n,a}\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 큰 크기 사슬 집합 · \(\mathfrak C_{n,a}\) |
| 종류 | 대상 |
| 정의 | 정수 a≥1,0≤n≤2a+1에서 \(\mathfrak C_{n,a}:=\{(H_1,\ldots,H_t):t\ge1,n\ge H_1>\cdots>H_t>a\}\). |
| 잘 정의됨 | 길이 t≤n−a인 유한 정수열 집합이다. |
| Lean 대응 | 미형식화 |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §3 식 (8) 앞; 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 97. 사슬 계수 · \(\mathfrak c_{n,a}\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 계수 · \(\mathfrak c_{n,a}(\mathbf H)\) |
| 종류 | 함수 |
| 정의 | 위 영역과 \(\mathbf H\in\mathfrak C_{n,a}\)에서 \(\mathfrak c_{n,a}(\mathbf H):=\binom n{H_1}T_{n-H_1}\prod_{r=1}^{t-1}[\binom{H_r-1}{H_{r+1}}T_{H_r-1-H_{r+1}}]\mathcal W_a(H_t-1)\). |
| 잘 정의됨 | 유한 곱이고 𝒲의 모든 인수가 정의역 안이다. |
| Lean 대응 | 미형식화 |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §3 (8); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 98. 성분 수송 계수 · \(\mathfrak I(n,s)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 성분 수송 계수 · \(\mathfrak I(n,s)\) |
| 종류 | 함수 |
| 정의 | n,s∈ℕ에서 s<n이면 \(\mathfrak I(n,s):=\binom n{s+1}T_{n-s-1}\), s≥n이면 0. |
| 잘 정의됨 | 유한 정수 산술이다. 정본의 ϑₙ,ⱼ와 이항계수의 윗첨자가 다르다. |
| Lean 대응 | 선행 수용 기록에는 별도 선언 없음. 새 구현은 다음 행에서 구별한다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.transport n s`는 s≥n의 0까지 원 T 기반 정의. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §4 (12); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 99. 사슬 응답 다항식 · \(\mathfrak K_z(n,s)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 응답 다항식 · \(\mathfrak K_z(n,s)\) |
| 종류 | 함수 |
| 정의 | n,s∈ℕ에서 n≤s이면 0, n>s이면 \(\mathfrak K_z(n,s):=\mathfrak I(n,s)+z\sum_{j=s+1}^{n-1}\mathfrak I(n,j)\mathfrak K_z(j,s)\in\mathbb Z[z]\). 실수 z 대입도 사용한다. |
| 잘 정의됨 | n에 대한 삼각 재귀. |
| Lean 대응 | ka8fb76538efa4aa28114eaab004058ff/UpperRatio.lean의 `ParkingUpperRatio.response q s d`는 T 닫힌 식 `totalFormula`로 만든 수치 재귀다. 해당 기록에서는 자연수 q에서 𝔎q(s+1+d,s)와 같은 값이라는 연결이 비형식이었다. 현재 일반 동일성은 아래 보완 대응을 따른다. 구현의 국소 정리만 검토 k2f5a509346a04efc9720bfffb293aeee에서 accepted/matches다. 그 선행 기록에서 다항식 자체는 미형식화. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.responsePolynomial n s`와 `response z n s`; responsePolynomial_eval의 유리수 대입 연결은 독립 수용. 닫힌 식 기반 UpperRatio 구현과의 동일성은 아래 별도 보완 결과다. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `response_eq_closed`가 모든 자연수 q,s,d에서 `ParkingChain.response (q:ℚ) (s+1+d) s = (ParkingUpperRatio.response q s d:ℚ)`를 증명했다. `totalFormula_eq_totalCount`도 모든 자연수에서 원 T와 같다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 임의 유리수 q의 자연수 구현이나 n≤s의 잘린 인덱스 확장 동일성은 주장하지 않는다. |
| Lean 보완 대응 | k39ce4750627e4a0e9735832b2fb49076/ShiftCompare.lean의 `ParkingNegative.actual_response_source_parameter_shift`는 모든 자연수 q,s,d, q≤s+2에서 (s+d+2)𝔎_q(s+d+1,s)≤(s+2)𝔎_(q+1)(s+d+2,s+1)을 증명한다. 검토 k32399dd4a57c4e8f980f7103f4fda6d3에서 accepted/matches. 실수 q 전체나 원 U의 정리가 아니다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §4 (13); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 100. 사슬 경계 손실 다항식 · \(\mathfrak D_{n,k}(z)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 경계 손실 다항식 · \(\mathfrak D_{n,k}(z)\) |
| 종류 | 함수 |
| 정의 | n,k∈ℕ에서 \(\mathfrak D_{n,k}(z):=T_k\mathfrak K_z(n,k)\). |
| 잘 정의됨 | 두 정의된 다항식·정수의 곱이다. |
| Lean 대응 | UpperRatio.lean의 `boundaryLoss n k`와 `shiftedLoss n k`는 n≥k+1에서 각각 z=k+2,k+3의 비형식 구현 대응이다. 해당 기록 당시에는 원 T와 totalFormula의 일반 Lean 동일성이 남았다. 현재 손실 구현 동일성은 아래 보완 대응을 따른다. 구현의 n≤k 값은 잘린 인덱스 보조 확장으로서 이 항목과 같다고 주장하지 않는다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.lossPolynomial n k`와 `loss z n k`; n≤k에서 정확히 0. 기존 잘린 인덱스 보조 확장을 쓰지 않는다. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `boundaryLoss_eq_original`, `shiftedLoss_eq_original`은 n≥k+1에서 각각 원 𝔇ₙ,ₖ(k+2), 𝔇ₙ,ₖ(k+3)의 ℚ 포함값과 같다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. n≤k의 보조 확장은 동일시하지 않는다. |
| Lean 보완 대응 | k39ce4750627e4a0e9735832b2fb49076/ShiftCompare.lean의 `ParkingNegative.actual_boundary_loss_shift`는 원 T 기반 손실의 동시 이동 비교다. 검토 k32399dd4a57c4e8f980f7103f4fda6d3에서 accepted/matches. 같은 최종 행의 곡률 비교나 U를 포함하지 않는다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §4 (14); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 101. 사슬 길이 가중 다항식 · \(\mathfrak S_{n,k}(z)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 길이 가중 다항식 · \(\mathfrak S_{n,k}(z)\) |
| 종류 | 함수 |
| 정의 | k≥1,0≤n≤2k+1에서 \(\mathfrak S_{n,k}(z):=\mathcal W_k(n)+\sum_{\mathbf H\in\mathfrak C_{n,k}}\mathfrak c_{n,k}(\mathbf H)z^{\operatorname{length}(\mathbf H)}\). |
| 잘 정의됨 | 유한 다항식이다. |
| Lean 대응 | 미형식화 |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §4 (11); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 102. 사슬 길이 곡률 다항식 · \(\mathfrak M_{n,k}(u)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 길이 곡률 다항식 · \(\mathfrak M_{n,k}(u)\) |
| 종류 | 함수 |
| 정의 | S와 같은 n,k 영역에서 \(\mathfrak M_{n,k}(u):=\mathfrak S_{n,k}(u+2)-2\mathfrak S_{n,k}(u+1)+\mathfrak S_{n,k}(u)\). |
| 잘 정의됨 | 다항식의 차분이다. 최대 변위 M(α)와 다르다. |
| Lean 대응 | 미형식화 |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §5 (16); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 103. 사슬 곡률 비율 · \(\mathfrak R_{n,k}\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 곡률 비율 · \(\mathfrak R_{n,k}\) |
| 종류 | 함수 |
| 정의 | k≥1,k+2≤n≤2k+1에서 \(\mathfrak R_{n,k}:=1+\Delta_{n,k}/\mathfrak D_{n,k}(k+2)\in\mathbb Q\). |
| 잘 정의됨 | 분모 양수는 응답 재귀로 따른다. M(k)/D(k+2)와의 동일성·양수성은 exposition.md (17)–(18)의 비형식 정리이다. |
| Lean 대응 | `ParkingUpperRatio.normalized`는 원 b와 닫힌 식 기반 손실로 정의한다. 부호 동치와 조건부 정리는 검토 k2f5a509346a04efc9720bfffb293aeee에서 accepted/matches다. k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `boundaryLoss_eq_original`은 n≥k+1에서 해당 분모의 원 T 기반 값과의 동일성을 증명했고 kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches다. 정본 𝔐의 사슬 열 합 식별 및 그에 의한 곡률 비율 표현 전체의 Lean 연결은 아직 별도다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §5 (18); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 104. 사슬 이동 손실 · \(\mathfrak H_{n,k}\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 이동 손실 · \(\mathfrak H_{n,k}\) |
| 종류 | 함수 |
| 정의 | k≥1,n≥k+3에서 \(\mathfrak H_{n,k}:=2\mathfrak D_{n,k}(k+3)-2\mathfrak D_{n,k}(k+2)+\mathfrak D_{n,k+1}(k+3)\). |
| 잘 정의됨 | 유한 정수 차이며 D의 z에 대한 증가와 마지막 항의 양수성으로 양수다. |
| Lean 대응 | `ParkingUpperRatio.transportLoss`는 닫힌 식 기반 응답의 위 영역 비형식 구현 대응이다. 양수성·조건부 연결은 k2f5a509346a04efc9720bfffb293aeee에서 accepted/matches이며 그 원 T 기반 함수와의 일반 Lean 동일성은 아래 보완 대응을 따른다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.shiftedLoss n k`는 원 T 기반 이동 손실. 해당 영역 양수성도 독립 수용. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `transportLoss_eq_original`은 n≥k+2에서 `ParkingUpperRatio.transportLoss n k = ParkingChain.shiftedLoss n k`를 증명했다. 따라서 본 항목의 원 영역 k≥1,n≥k+3 전체에 적용된다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 부호 부등식 자체의 증명은 아니다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §7의 임시 기호 H. 이 제안은 그 식에 안정적인 인덱스를 붙인다.; 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 105. 말단 크기 곡률 다항식 · \(\mathfrak N_{n,s}(u)\)
| 칸 | 내용 |
|---|---|
| 이름·기호 | 말단 크기 곡률 다항식 · \(\mathfrak N_{n,s}(u)\) |
| 종류 | 함수 |
| 정의 | 정수 n≥2,0≤s≤n−2에서 \(\mathfrak N_{n,s}(u):=(u+2)\mathfrak K_{u+2}(n,s)-2(u+1)\mathfrak K_{u+1}(n,s)+u\mathfrak K_u(n,s)\). |
| 잘 정의됨 | 다항식이고 u≥0에서 양수다. |
| Lean 대응 | 선행 수용 기록에서는 미형식화. 새 구현은 다음 행에서 구별한다. |
| Lean 추가 대응 | kdc2eaac490144ba1be92ba8a428a2228: `ParkingChain.terminalPolynomial n s`와 `terminal n s u`; terminalPolynomial_eval 및 s+2≤n,u≥0의 양수성도 독립 수용. 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 구현·연결 결과는 accepted/matches. 명시된 범위와 미완료 동일성은 유지한다. |
| 출처 | ka8fb76538efa4aa28114eaab004058ff/exposition.md §7.1 (27); 정의 처리: k2f87a4c4b02c4f5bb434e0bc167f8f07. |
| 기록별 이명 | |

## 106. 선형 결손 오차
| 칸 | 내용 |
|---|---|
| 이름·기호 | 선형 결손 오차 · \(\mathfrak G_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ에 대해 \(\mathfrak G_{n,\ell}:=\mathcal L_{n,\ell}-E_{n,\ell}\in\mathbb Z\). |
| 잘 정의됨 | 기존 두 정수 함수의 차다. |
| Lean 대응 | `ParkingBoundary.linearGap n l`, k9001cda0e9704d678342f834dec9e9d6/BoundaryCorrections.lean; 검토 k9fa99dedff1641a4a41924f945e4bf2c의 해당 형식 결과는 accepted/matches. 전칭 부호·경로 튜플 전체 형식화는 포함하지 않는다. |
| 출처 | k9001cda0e9704d678342f834dec9e9d6/exposition.md §3. 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 107. 선형 원천
| 칸 | 내용 |
|---|---|
| 이름·기호 | 선형 원천 · \(\mathfrak F_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ에서 \(\mathfrak F_{0,\ell}:=0\), n≥1에서 \(\mathfrak F_{n,\ell}:=\sum_{k=0}^{n-1}\binom{n-1}k(k-\ell)_+T_kT_{n-1-k}\). |
| 잘 정의됨 | 정수의 유한 합이다. 기존 누적 생성함수 ℱℓ와 다른 대상이다. |
| Lean 대응 | `ParkingBoundary.linearForcing l n`, k9001cda0e9704d678342f834dec9e9d6/LinearExpansion.lean; 검토 k9fa99dedff1641a4a41924f945e4bf2c의 해당 형식 결과는 accepted/matches. 전칭 부호·경로 튜플 전체 형식화는 포함하지 않는다. |
| 출처 | k9001cda0e9704d678342f834dec9e9d6/linear-expansion.md §1 식 (12). 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 108. 선형 전이 연산자
| 칸 | 내용 |
|---|---|
| 이름·기호 | 선형 전이 연산자 · \(\mathfrak T_\ell\) |
| 종류 | 함수 |
| 정의 | ℓ∈ℕ, g:ℕ→ℤ에 대해 \((\mathfrak T_\ell g)(0):=0\), n≥1에서 \((\mathfrak T_\ell g)(n):=\sum_{k=0}^{n-1}\binom{n-1}k(\ell+k+2)T_k g(n-1-k)\). |
| 잘 정의됨 | 각 n의 값은 정수의 유한 합이다. 원 전체 개수 T와 다른 대상이다. |
| Lean 대응 | `ParkingBoundary.linearStep l g n`, k9001cda0e9704d678342f834dec9e9d6/LinearExpansion.lean; 검토 k9fa99dedff1641a4a41924f945e4bf2c의 해당 형식 결과는 accepted/matches. 전칭 부호·경로 튜플 전체 형식화는 포함하지 않는다. |
| 출처 | k9001cda0e9704d678342f834dec9e9d6/linear-expansion.md §1 식 (12). 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 109. 선형 전개 층
| 칸 | 내용 |
|---|---|
| 이름·기호 | 선형 전개 층 · \(\mathfrak V^{(r)}_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | n,ℓ,r∈ℕ에서 \(\mathfrak V^{(0)}_{n,\ell}:=\mathfrak F_{n,\ell}\), \(\mathfrak V^{(r+1)}_{n,\ell}:=(\mathfrak T_\ell\mathfrak V^{(r)}_{\bullet,\ell})(n)\). |
| 잘 정의됨 | r에 대한 자연수 재귀다. 기존 포화 보정 다항식 Vℓ와 다른 대상이다. |
| Lean 대응 | `ParkingBoundary.linearLayer l r n`, k9001cda0e9704d678342f834dec9e9d6/LinearExpansion.lean; 검토 k9fa99dedff1641a4a41924f945e4bf2c의 해당 형식 결과는 accepted/matches. 전칭 부호·경로 튜플 전체 형식화는 포함하지 않는다. |
| 출처 | k9001cda0e9704d678342f834dec9e9d6/linear-expansion.md §1 식 (13). 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 110. 제한 이항 폭 모멘트
| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 이항 폭 모멘트 · \(\mathfrak t^{\triangleright}_{n,q,p}\) |
| 종류 | 함수 |
| 정의 | n,p∈ℕ, q≥1, \(\triangleright\in\{>,\ge\}\)에서 \(\mathfrak t^{\triangleright}_{n,q,p}:=\sum_{\pi\in\mathfrak S_n}\varpi_q(\pi)\binom{\#\{j:h_j\triangleright q\}}p\). n=0에는 빈 순열·빈 곱을 써 p=0이면 1, p>0이면 0이다. |
| 잘 정의됨 | 유한 순열 집합의 정수 가중 합이다. q≥2인 하계와 q≥1인 정의역을 구별한다. |
| Lean 대응 | 미형식화. moment_probe.py는 p=0,…,4의 계산 구현이다. |
| 출처 | k9001cda0e9704d678342f834dec9e9d6/moment-bound.md §2 식 (22). 기존 제한 큰 폭 모멘트와는 \(\mathfrak t^>_{n,q,1}=\mathfrak m^{(1)}_{n,q}\), \(2\mathfrak t^>_{n,q,2}=\mathfrak m^{(2)}_{n,q}\)인 일부 값에서만 동일시한다. 원 PF의 제한 없는 고변위 이항 표시 모멘트 μ와는 가중치·표시 통계량이 다르다. 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 111. 제한 폭 결합 표시 다항식
| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 폭 결합 표시 다항식 · Θₙ,ᵩ(u,v) |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2에서 Θₙ,ᵩ(u,v):=Σ(π∈𝔖ₙ)ϖq(π)u^{Nᐳq(π)}v^{N⁼q(π)}. Θ₀,ᵩ=1. 유리 계수 이변수 다항식이다. |
| 잘 정의됨 | 유한 순열 합. exposition.md §2의 최대 원소 분할이 정확한 재귀를 준다. |
| Lean 대응 | Joint.lean의 `ParkingRestricted.evaluate (atoms q n) u v`는 이 다항식 평가의 재귀 구현이다. 원 A와의 특수값 동일성은 형식 증명했고, 순열 합과 목록 자체의 일반 식별은 §2의 비형식 논증이다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §2 식 (4)–(5) 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 112. 감쇠 제한 가중치
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 제한 가중치 · ϖ̃q(π) |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2,π∈𝔖ₙ에서 ϖ̃q(π):=ϖq(π)((q−1)/q)^{Nᐳq(π)}. |
| 잘 정의됨 | 분모 q>0. 폭>q의 인자 q를 q−1로 바꾸는 곱이므로 비음수 정수다. |
| Lean 대응 | Joint.lean 평가에서 `(u,v)=(1−1/q,1)`인 각 가중 항. 개별 순열 함수 자체는 미형식화. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §2 식 (7) 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 113. 감쇠 제한 가중합
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 제한 가중합 · Ãₙ,ᵩ |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2에서 Ãₙ,ᵩ:=Σ(π∈𝔖ₙ)ϖ̃q(π)=Θₙ,ᵩ(1−1/q,1). |
| 잘 정의됨 | 유한 비음수 정수 합. Ã₀,ᵩ=1. 원 누적 개수 Aₙ,ℓ와 다른 대상이다. |
| Lean 대응 | `evaluate (atoms q n) (1−1/q) 1`의 재귀 구현 대응. 일반 순열 합 식별의 형식 한계는 앞 항목과 같다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §2 식 (7) 뒤 문단 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 114. 감쇠 문턱 표시 합
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 문턱 표시 합 · 𝔥̂ₙ,ᵩ |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2에서 𝔥̂ₙ,ᵩ:=Σ(π∈𝔖ₙ)ϖ̃q(π)N⁼q(π). 빈 경계는 0. |
| 잘 정의됨 | 유한 비음수 정수 합. 원 𝔥에는 감쇠가 없으므로 다른 대상이다. |
| Lean 대응 | Bound.lean의 `dampedThreshold (atoms q n) (1/q)`는 정확 전달의 재귀 구현. 원 b에 대한 하계는 `original_b_lower`로 형식 증명. 직접 순열 합과의 동일성은 비형식이다. 검토 k533a625813b0497dae732e87b1c05808에서 원 하계의 재귀 구현은 accepted/matches다. 분자 비음수와 직접 순열 합의 일반 Lean 식별은 미완료다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §1 식 (2), §2 식 (8) 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 115. 감쇠 문턱 쌍 합
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 문턱 쌍 합 · 𝔥̂⁽[2]⁾ₙ,ᵩ |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2에서 𝔥̂⁽[2]⁾ₙ,ᵩ:=Σ(π∈𝔖ₙ)ϖ̃q(π)binom(N⁼q(π),2). |
| 잘 정의됨 | 유한 비음수 정수 합. n<3q에서 원 이차 차분의 정확 문턱 손실 보정이라는 사실은 별도 식 (12)–(13)으로 증명한다. |
| Lean 대응 | 미형식화. remainder_probe.py의 `pair`가 구현한다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §3 식 (13) 뒤 문단 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 116. 순열별 제한 곡률
| 칸 | 내용 |
|---|---|
| 이름·기호 | 순열별 제한 곡률 · χq(π) |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2,π∈𝔖ₙ에서 χq(π):=∏ᵢmin(hᵢ,q+1)−2∏ᵢmin(hᵢ,q)+∏ᵢmin(hᵢ,q−1)∈ℤ. |
| 잘 정의됨 | 유한 정수 곱의 차. 빈 순열에서 0이며 원 Δ의 크기 0 경계와 양립한다. |
| Lean 대응 | 개별 순열 함수는 미형식화. Bound.lean의 `restored_local_lower`가 가중치 밖 r,h에 대한 국소 하계를 증명한다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §5.1 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 117. 결합 표시 재귀 목록
| 칸 | 내용 |
|---|---|
| 이름·기호 | 결합 표시 재귀 목록 · atoms(q,n) |
| 종류 | 함수 |
| 정의 | q,n∈ℕ에서 atoms(q,0):=[(1,0,0)]. n+1에서는 k=0,…,n과 각 자식 항 (w,r,h),(w′,r′,h′)을 순서대로 훑어 (binom(n,k)min(k+1,q)ww′,r+r′+[k+1>q],h+h′+[k+1=q])를 나열한 목록이다. 같은 표시를 합치지 않은 중복 목록이다. |
| 잘 정의됨 | 자식 크기가 모두 작으므로 강한 재귀로 유일하게 정의된다. q=0,1 구현은 보조 확장이며 본 연구의 순열 해석은 q≥2에서만 사용한다. |
| Lean 대응 | Joint.lean의 `ParkingRestricted.Atom`, `merge`, `atoms`, `evaluate`. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §6; Joint.lean 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 118. 제한 표시 지수 급수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 표시 지수 급수 · $\mathcal M_q^{(a)}(x)$ |
| 종류 | 함수 |
| 정의 | q≥2,a∈{1,2}에서 $\mathcal M_q^{(a)}(x):=\sum_{n\ge0}\mathfrak m^{(a)}_{n,q}x^n/n!\in\mathbb Q[[x]]$. |
| 잘 정의됨 | 정의된 표시 합의 형식급수. 원 𝔪 자체와 다른 급수 대상이다. |
| Lean 대응 | 미형식화. 식 (14)의 첫 두 표시 방정식은 비형식 유도 및 source_probe.py의 유한 검산. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 식 (14) 앞 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 119. 감쇠 제한 지수 급수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 제한 지수 급수 · ℱ̃q(x) |
| 종류 | 함수 |
| 정의 | q≥2에서 ℱ̃q(x):=Σ(n≥0)Ãₙ,ᵩxⁿ/n!∈ℚ[[x]]. |
| 잘 정의됨 | 정의된 감쇠 합의 형식급수. 원 ℱℓ와 구별된다. |
| Lean 대응 | 급수 전체는 미형식화. 계수는 `evaluate`의 감쇠 특수값으로 구현. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 120. 감쇠 문턱 지수 급수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 문턱 지수 급수 · ℋ̂q(x) |
| 종류 | 함수 |
| 정의 | q≥2에서 ℋ̂q(x):=Σ(n≥0)𝔥̂ₙ,ᵩxⁿ/n!∈ℚ[[x]]. |
| 잘 정의됨 | 정의된 감쇠 표시 합의 형식급수. 정본의 프라임 정확 급수 ℋℓ와 다른 대상이다. |
| Lean 대응 | 급수 전체는 미형식화. 계수는 `dampedThreshold`로 구현. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 121. 전체 계수 절단 다항식
| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 계수 절단 다항식 · 𝓟q(x) |
| 종류 | 함수 |
| 정의 | q≥2에서 𝓟q(x):=Σ(j=0..q−1)fⱼxʲ. |
| 잘 정의됨 | 정본 f의 유한 합이다. 단봉성 명제 P와 다르다. |
| Lean 대응 | 미형식화. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | 기록 k9a8431776364465195c7ae81c0c031ec의 𝒫q(q≥2 부분). q=1 보조 확장 전체는 §162의 다른 정의역 함수다. |

## 122. 제한 표시 전달 계수 쌍
| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 표시 전달 계수 쌍 · $(\mathcal K_q(x),\widetilde{\mathcal K}_q(x))$ |
| 종류 | 함수 |
| 정의 | q≥2에서 $\mathcal K_q:=2q\mathcal F_{q-1}-V_{q-1}$, $\widetilde{\mathcal K}_q:=2(q-1)\widetilde{\mathcal F}_q-V_{q-2}+f_{q-1}x^{q-1}$. 모두 ℚ[[x]]의 원소다. |
| 잘 정의됨 | 앞서 정의한 급수의 대수적 결합. 정본 포화 손실 Kₙ,ℓ와 다르다. |
| Lean 대응 | 미형식화. source_probe.py의 `K`,`Kt`는 지수 계수 구현. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 123. 감쇠 표시 분자 급수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 표시 분자 급수 · 𝓧q(x) |
| 종류 | 함수 |
| 정의 | q≥2에서 $\mathcal X_q:=\mathcal M_q^{(2)}-q\widehat{\mathcal H}_q\in\mathbb Q[[x]]$. |
| 잘 정의됨 | 정의된 급수의 차. 각 계수의 비음수성은 정의에 포함하지 않는다. |
| Lean 대응 | 급수는 미형식화. 계수의 원 b 하계 연결은 Bound.lean으로 형식화. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 식 (15) 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 124. 감쇠 표시 원천 급수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 감쇠 표시 원천 급수 · 𝓖q(x) |
| 종류 | 함수 |
| 정의 | q≥2에서 $\mathcal G_q:=2q(\mathcal M_q^{(1)})^2+2q(2\mathcal F_{q-1}-\mathcal P_q)\mathcal M_q^{(1)}+q(\mathcal K_q-\widetilde{\mathcal K}_q)\widehat{\mathcal H}_q-q^2f_{q-1}x^{q-1}\widetilde{\mathcal F}_q$. |
| 잘 정의됨 | 정의된 급수의 대수적 결합. |
| Lean 대응 | 미형식화. source_probe.py의 `src`가 지수 계수를 구현한다. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 식 (15) 앞 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 125. 제한 표시 응답 커널
| 칸 | 내용 |
|---|---|
| 이름·기호 | 제한 표시 응답 커널 · $\mathscr K^{(q)}_{n,j}$ |
| 종류 | 함수 |
| 정의 | q≥2,n,j∈ℕ에서, $Y(0)=0,Y'=\mathcal K_qY+x^j/j!$의 유일한 형식급수 해에 대해 $\mathscr K^{(q)}_{n,j}:=n![x^n]Y$. |
| 잘 정의됨 | 상수항 0, 선형 미분 방정식의 계수별 삼각 재귀로 존재·유일. 정본 사슬 응답 𝔎z(n,s)와 다르다. |
| Lean 대응 | 미형식화. 소행렬식 (16)은 첫 세 비영 계수의 직접 대수 계산. |
| 출처 | k772e2708b66f4a2e8e9322e151db43ab/exposition.md §4 식 (16) 앞 정의 처리: k8871441acfea4f0eafa463d0494456c6. |
| 기록별 이명 | |

## 126. 역급수 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 역급수 계수 · \(\mathfrak a_m\) |
| 종류 | 함수 |
| 정의 | 정수 m≥1에서 \(\mathfrak a_m:=(m-1)^{m-1}/m!\in\mathbb Q\), m=1의 0⁰=1. |
| 잘 정의됨 | m!>0. Ψ⁻¹의 비상수 계수의 음수라는 성질은 §3에서 별도 증명. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §3, (5) 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 127. 사슬 응답 지수급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 사슬 응답 지수급수 · \(\mathscr E_{s,z}(x)\) |
| 종류 | 함수 |
| 정의 | s∈ℕ, 형식변수 z에 대해 \(\mathscr E_{s,z}(x):=\sum_{n>s}\mathfrak K_z(n,s)x^n/n!\in\mathbb Q[z][[x]]\). 실수 z 대입도 사용. |
| 잘 정의됨 | 각 계수는 사슬 응답 재귀의 다항식. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §3, (4) 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 128. 동차 응답 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 동차 응답 다항식 · \(\mathscr Q_j(a)\) |
| 종류 | 함수 |
| 정의 | j∈ℕ와 형식변수 a에 대해 \(\mathscr Q_j(a):=[x^j](\Psi(x)^{-1}-ax)^{-1}\in\mathbb Q[a]\). 실수 a 대입도 사용. |
| 잘 정의됨 | 역을 취하는 두 급수의 상수항은 모두 1. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §3, (7). 기존 포화 초과 가중 급수 \(\mathcal Q_\ell(x)\)와는 정의와 변수, 서체가 다름. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 129. 말단 경계 요구 비

| 칸 | 내용 |
|---|---|
| 이름·기호 | 말단 경계 요구 비 · \(\mathfrak Z_{k,d}\) |
| 종류 | 함수 |
| 정의 | 정수 k≥1,2≤d≤k,n=k+d+1에서 \(\mathfrak Z_{k,d}:=\{\mathfrak N_{n,k}(k+1)\mathfrak K_{k+2}(n,k)-2\mathfrak N_{n,k}(k)[\mathfrak K_{k+3}(n,k)-\mathfrak K_{k+2}(n,k)]\}/[\mathfrak N_{n,k}(k)\mathfrak K_{k+3}(n,k+1)]\). |
| 잘 정의됨 | 분모의 두 응답 값이 양수. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §5, (17) 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 130. 이항 절단 비 하계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 이항 절단 비 하계 · \(\mathscr B_p(k)\) |
| 종류 | 함수 |
| 정의 | 정수 k≥1,p≥0에서 \(\mathscr B_p(k):=(k+1)\sum_{j=0}^{\min(p,k)}\binom kj/(k+1)^j\in\mathbb Q\). |
| 잘 정의됨 | k+1>0. T 비의 하계라는 성질은 이항전개로 증명. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §5–6. 기존 인접 수송 경계합 \(\mathfrak B_{n,\ell}\)와 다른 함수·서체·매개변수. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 131. 응답 1차 차분

| 칸 | 내용 |
|---|---|
| 이름·기호 | 응답 1차 차분 · \(\mathscr U_{n,s}(u)\) |
| 종류 | 함수 |
| 정의 | 정수 n>s≥0에서 \(\mathscr U_{n,s}(u):=(u+1)\mathfrak K_{u+1}(n,s)-u\mathfrak K_u(n,s)\in\mathbb Q[u]\). |
| 잘 정의됨 | 정의된 두 다항식의 차. |
| Lean 대응 | 미형식화 |
| 출처 | k52423a2c3ac04a04a4e61cb863a834a7/exposition.md §7, (20) 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 132. 원 성분 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 성분 계수 · c^{cmp}_q(i) |
| 종류 | 함수 |
| 정의 | q≥1,i∈ℕ에서 c^{cmp}_q(i):=min(i+1,q)Aᵢ,ᵩ₋₁∈ℕ. |
| 잘 정의됨 | 원 A와 자연수 곱. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.component q i`는 ℚ로의 포함값. q=0은 계산상 확장이며 원 거리 q−1의 해석을 하지 않는다. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §3, OriginalChain.lean. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 133. 전체 성분 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 성분 계수 · τ^{cmp}(i) |
| 종류 | 함수 |
| 정의 | i∈ℕ에서 τ^{cmp}(i):=(i+1)Tᵢ∈ℕ. |
| 잘 정의됨 | 원 전체 개수 T의 곱이다. 거듭제곱으로 재정의하지 않는다. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.totalComponent i`는 ℚ로의 포함값. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `totalComponent_eq_power`가 모든 s≥0에서 τ^{cmp}(s)=(s+1)^s의 ℚ 포함값 동일성을 증명했다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 원 정의 (s+1)Tₛ는 유지한다. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §3, OriginalChain.lean. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 134. 원 성분 절단 기저

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 성분 절단 기저 · B^{cmp}_k(n) |
| 종류 | 함수 |
| 정의 | k,n∈ℕ에서 \(B^{\rm cmp}_k(n):=T_n-\sum_{s=k}^{n-1}\mathfrak I(n,s)(s+1)T_s\in\mathbb Z\). |
| 잘 정의됨 | 유한 정수 차. n≤2k+1의 actualBase_eq_smallCount 및 비음수성은 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 accepted/matches다. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.actualBase k n : ℚ`. |
| Lean 보완 대응 | k0ee8ae2f5ad94097af2c3778062ded44/CanonicalBridge.lean의 `actualBase_eq_canonicalWeight`가 k≥1,n≤2k+1에서 이 함수의 제한과 정본 𝒲의 ℚ 구현 동일성을 증명했다. kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. 전역 함수의 이름·정의역은 유지한다. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §4 식 (C). 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

이 항목은 k,n∈ℕ 전체의 확장 함수다. 기존 𝒲·𝔖·𝔐는 k≥1,n≤2k+1의 제한 영역 대상이다. 그 제한 영역에서는 수용된 비형식 Cayley 공식과 삼각 재귀에 의해 대응하는 값이 같다. 별도 항목을 두는 이유는 정의역이 더 넓기 때문이며, 제한 영역에서 서로 다른 값을 갖는다는 뜻이 아니다. 이 기저의 제한·일반 Lean 동일성은 위 보완 대응에서 수용되었다. 사슬·곡률의 명시적 열 합 식별은 아직 별도다. 기존 제한 대상에는 기존 정본 이름을 쓴다.


## 135. 소성분 조립 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 소성분 조립 개수 · J^{cmp}_k(n) |
| 종류 | 함수 |
| 정의 | k,n∈ℕ에서 J^{cmp}_k(0):=1, J^{cmp}_k(n+1):=Σ(i=0..n)binom(n,i)[i<k](i+1)TᵢJ^{cmp}_k(n−i)∈ℕ. |
| 잘 정의됨 | 자식 인수 n−i<n+1의 유한 자연수 재귀. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.smallCount k n`. n≤2k+1에서 B^{cmp}_k(n)와의 동일성 `actualBase_eq_smallCount`는 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 accepted/matches다. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §4, ChainPositivity.lean. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |


현재 비형식 수용 보완: k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §4 (7)의 실제 감소 숲 성분 해석은 kfaeb6535dad54592857b1f726417d954의 exact-empty-loss-and-all-chain-strata 검토에서 supported다. 이 성분 해석 전체에 새 Lean 인증을 추가한 것은 아니다.

## 136. 원 성분 사슬 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 성분 사슬 다항식 · C^{cmp}_{n,k}(z) |
| 종류 | 함수 |
| 정의 | k,n∈ℕ에서 \(C^{\rm cmp}_{n,k}(z):=B^{\rm cmp}_k(n)+z\sum_{s=k}^{n-1}\mathfrak I(n,s)C^{\rm cmp}_{s,k}(z)\in\mathbb Q[z]\). |
| 잘 정의됨 | s<n인 삼각 재귀. n≤k이면 Tₙ. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.actualChainPolynomial k n`; 유리수 대입은 `ParkingChain.chain z k n`. `actualChainPolynomial_eval`로 연결했다. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §4 식 (E). 정본 𝔖와의 일반 형식 동일성은 미완료. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

이 항목은 k,n∈ℕ 전체의 확장 함수다. 기존 𝒲·𝔖·𝔐는 k≥1,n≤2k+1의 제한 영역 대상이다. 그 제한 영역에서는 수용된 비형식 Cayley 공식과 삼각 재귀에 의해 대응하는 값이 같다. 별도 항목을 두는 이유는 정의역이 더 넓기 때문이며, 제한 영역에서 서로 다른 값을 갖는다는 뜻이 아니다. 그 제한·일반 Lean 동일성은 아직 미완료다. 기존 제한 대상에는 기존 정본 이름을 쓴다.


## 137. 원 성분 곡률 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 성분 곡률 다항식 · Q^{cmp}_{n,k}(u) |
| 종류 | 함수 |
| 정의 | k,n∈ℕ에서 Q^{cmp}_{n,k}(u):=C^{cmp}_{n,k}(u+2)−2C^{cmp}_{n,k}(u+1)+C^{cmp}_{n,k}(u). |
| 잘 정의됨 | 유한 다항식 차분. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingChain.curvature n k u`는 유리수 대입값. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §5 식 (H) 앞. 정본 𝔐와의 일반 형식 동일성은 미완료. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

이 항목은 k,n∈ℕ 전체의 확장 함수다. 기존 𝒲·𝔖·𝔐는 k≥1,n≤2k+1의 제한 영역 대상이다. 그 제한 영역에서는 수용된 비형식 Cayley 공식과 삼각 재귀에 의해 대응하는 값이 같다. 별도 항목을 두는 이유는 정의역이 더 넓기 때문이며, 제한 영역에서 서로 다른 값을 갖는다는 뜻이 아니다. 그 제한·일반 Lean 동일성은 아직 미완료다. 기존 제한 대상에는 기존 정본 이름을 쓴다.


## 138. 절단 계수 일치 관계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 절단 계수 일치 관계 · Jet(N,f,g) |
| 종류 | 성질·관계 |
| 정의 | N∈ℕ,f,g∈ℚ[[x]]에서 Jet(N,f,g) :⇔ 모든 0≤i<N에서 [xⁱ]f=[xⁱ]g. |
| 잘 정의됨 | 해당 없음. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingJets.Jet N f g`. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/exposition.md §3, Jets.lean. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 139. 일반 지수 정규화 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 일반 지수 정규화 연산 · egf(f) |
| 종류 | 함수 |
| 정의 | f:ℕ→ℚ에서 egf(f):=Σ(n≥0)f(n)xⁿ/n!∈ℚ[[x]]. |
| 잘 정의됨 | 계수별 정의. 원 ℱℓ는 특정 원 A를 대입한 경우이며 이 연산 자체와 구별한다. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingJets.egf f`. |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/Jets.lean. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 140. 적분 성분 원천 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 적분 성분 원천 연산 · source(c) |
| 종류 | 함수 |
| 정의 | c:ℕ→ℚ에서 source(c):=Σ(h≥1)c(h−1)xʰ/h!∈ℚ[[x]]. 상수항은 0이다. |
| 잘 정의됨 | 계수별 정의. |
| Lean 대응 | 검토 k1d0504eb9d5a478c8e6c31ae760d4630에서 해당 결과 accepted/matches: kdc2eaac490144ba1be92ba8a428a2228의 구현. `ParkingJets.source c`; `der_source`는 도함수=egf(c). |
| 출처 | kdc2eaac490144ba1be92ba8a428a2228/Jets.lean, exposition.md §3. 정의 처리: k7e8742aa996f47718faf175011dd4251. |
| 기록별 이명 | |

## 141. 보조 Abel 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 보조 Abel 다항식 · 𝔞ᵣ(X) |
| 종류 | 함수 |
| 정의 | r∈ℕ에서 𝔞₀(X):=1, 𝔞ᵣ₊₁(X):=X(X+r+1)ʳ∈ℚ[X]. |
| 잘 정의됨 | 유리 계수 다항식의 유한 곱·거듭제곱이다. |
| Lean 대응 | k0ee8ae2f5ad94097af2c3778062ded44/Abel.lean의 `ParkingCayley.abelPoly`. 관련 정리와의 정합성은 kb4a55fd1ff714b01a68cad95eb87f3c3에서 accepted/matches. |
| 출처 | k0ee8ae2f5ad94097af2c3778062ded44/exposition.md §2 및 glossary-proposals.md. 정의 처리: kf1d81645162943279b011bd0d3cac6a3. |
| 기록별 이명 | |

## 142. 실수 허용 거리 누적 함수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 실수 허용 거리 누적 함수 · 𝒜ₙ(x) |
| 종류 | 함수 |
| 정의 | n∈ℕ, 실수 x≥0에 대해 𝒜ₙ(x) := Σ(π∈𝔖ₙ) ∏(j∈[n]) min(hⱼ(π), x). n=0에서는 빈 순열 한 개와 빈 곱의 관례로 𝒜₀(x) := 1이다. |
| 잘 정의됨 | 유한 합이다. 정수 ℓ≥0과 n≥1에서 𝒜ₙ(ℓ+1)=Aₙ,ℓ은 정의가 아니라, 수용된 순열 상자 표현(k12c717105e4f436ebbc4a311ae64134a, 검토 k011d78d902664efbb1f1ef0d601484a7)에서 따르는 관계다. 실수 x 판본의 확률 해석은 kafb8753e508c467d89d38921889dab4a/exploration.md 명제 3.2다. |
| Lean 대응 | 미형식화 |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.2 |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 143. 연속 최대 변위
| 칸 | 내용 |
|---|---|
| 이름·기호 | 연속 최대 변위 · M̃(α,v) |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ, v=(v₁,…,vₙ)∈[0,1)ⁿ에 대해 M̃(α,v) := max{dᵢ(α)+vᵢ : i∈[n]}. |
| 잘 정의됨 | 비어 있지 않은 유한 집합의 최댓값이다. ⌊M̃(α,v)⌋=M(α)이다. α를 PFₙ에서, v를 [0,1)ⁿ에서 독립 균등하게 뽑으면 P(M̃<x)=𝒜ₙ(x)/Tₙ이다(kafb8753e508c467d89d38921889dab4a/exploration.md 명제 3.2, 비형식 증명과 n≤6 정확 대조). |
| Lean 대응 | 미형식화 |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.2 |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 144. 원형 호
| 칸 | 내용 |
|---|---|
| 이름·기호 | 원형 호 · X(e) |
| 종류 | 대상 |
| 정의 | n≥1이라 하자. 원형 주차 확률모형 𝔓ₙ의 자리 1,…,n+1(다음 순서 1→2→⋯→n+1→1)에서 점유 자리집합 O가 \|O\|≤n이고 e∉O라 하자. 이때 X(e) := {e} ∪ {e보다 앞에서 e까지 끊김 없이 이어진 점유 자리}이다. 정확히는, e에서 역방향으로 한 칸씩 이동하며 처음 만나는 빈자리 직전까지의 점유 자리를 모은 집합과 {e}의 합집합이다. |
| 잘 정의됨 | \|O\|≤n이면 빈자리가 있으므로 역방향 이동은 유한 번에 멈춘다. 서로 다른 빈자리의 호들은 자리 전체를 분할한다. |
| Lean 대응 | 미형식화 |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.1 명제 3.1. 차 i가 선호 a∈X(e)로 도착하면 e에 주차하고, 변위는 X(e) 안에서 균등하다. 대표 목록에서는 \|X(e)\|=h_{sᵢ}(π)이다. |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 145. 톱니 상승량
| 칸 | 내용 |
|---|---|
| 이름·기호 | 톱니 상승량 · 𝔯ₙ,ₖ |
| 종류 | 함수 |
| 정의 | 정수 n≥2, 1≤k≤n−1에 대해 𝔯ₙ,ₖ := (𝒜ₙ′(k⁻) − bₙ,ₖ₋₁) + (bₙ,ₖ − 𝒜ₙ′(k⁺)). 여기서 𝒜ₙ′(k^±)는 𝒜ₙ의 좌·우 도함수다. |
| 잘 정의됨 | 𝒜ₙ은 각 단위 구간에서 다항식이므로 한쪽 도함수가 존재한다. 볼록성으로 두 괄호는 음이 아니다. bₙ,ₖ₋₁=∫_{k−1}^{k}𝒜ₙ′, bₙ,ₖ=∫_k^{k+1}𝒜ₙ′이다. 관계 bₙ,ₖ−bₙ,ₖ₋₁=𝔯ₙ,ₖ−𝔥ₙ,ₖ/k와 𝒜ₙ′(k⁻)−𝒜ₙ′(k⁺)=𝔥ₙ,ₖ/k는 kafb8753e508c467d89d38921889dab4a/exploration.md §3.2–3.3에서 유도했고, n=60,120,200,300의 모든 k에서 정확한 정수로 단언 확인했다. |
| Lean 대응 | 미형식화 |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.3 |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 146. 마지막 최대 변위 차량
| 칸 | 내용 |
|---|---|
| 이름·기호 | 마지막 최대 변위 차량 · τ(α) |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ에 대해 τ(α) := max{i∈[n] : dᵢ(α)=M(α)}. 차 번호가 곧 도착 순서이므로, 최대 변위를 내는 차들 가운데 가장 늦게 도착한 차의 번호다. |
| 잘 정의됨 | M(α)는 어떤 dᵢ로 달성되므로, 집합은 비어 있지 않은 유한 집합이다. |
| Lean 대응 | 미형식화 |
| Lean 보완 대응 | k3402f089d15b489eb2cbad3ffa444bb7/lean/Arrival.lean의 `ParkingArrival.tau`; 내부 번호의 `.val+1`이 원 번호다. `tau_attains`, `le_tau`가 원 최대 달성·최후성을 증명하며 검토 kfd8c65fff6a84089ad0591255b0674a3에서 accepted/matches다. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.8 |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 147. 도착 시각별 정확 개수
| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 시각별 정확 개수 · b^{(τ)}_{n,ℓ} |
| 종류 | 함수 |
| 정의 | n≥1, τ∈[n], 정수 ℓ≥0에 대해 b^{(τ)}_{n,ℓ} := #{α∈PFₙ : M(α)=ℓ, τ(α)=τ}. |
| 잘 정의됨 | PFₙ의 유한 부분집합의 개수다. Σ(τ∈[n]) b^{(τ)}_{n,ℓ} = bₙ,ℓ이다. |
| Lean 대응 | 미형식화 |
| Lean 보완 대응 | k3402f089d15b489eb2cbad3ffa444bb7/lean/Arrival.lean의 `ParkingArrival.bArrival`; `arrival_event_iff`, `sum_bArrival`, `mixed_jump`가 원 사건 분할·원 b 합·혼합 문턱 차를 증명한다. 검토 kfd8c65fff6a84089ad0591255b0674a3에서 accepted/matches이며 L 부호 자체는 포함하지 않는다. |
| Lean 추가 대응 | k3c8d00ecefb9486697fd5692a47dad49/lean/Monotonicity.lean의 ParkingArrivalProof.bArrival_adjacent,bArrival_monotone,bArrival_original_indices. 원 도착 번호 단조성. 검토 kf60b5d44129f444b9c13cfa739536768 accepted/matches. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Marked.lean arrival_recurrence. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  kafb8753e508c467d89d38921889dab4a/exploration.md §3.8. 원 과정의 정확 동적 계획은 `code/arrival_split_dp.py`(n≤17)이다. |
| 기록별 이명 | |

이 정의의 채택은 kafb8753e508c467d89d38921889dab4a의 관계식·관측·문헌 해석의 독립 수용이 아니다. 이 탐구에 Lean 증명은 없으며, 수학적 근거로 쓰려면 연구·독립 검토가 필요하다.


## 148. 정규화 사슬 응답
| 칸 | 내용 |
|---|---|
| 이름·기호 | 정규화 사슬 응답 · \(\mathscr F_{s,z,c}(j)\) |
| 종류 | 함수 |
| 정의 | s,j∈ℕ, z∈ℝ, c>0에서 \(\mathscr F_{s,z,c}(j):=(s+1)!\mathfrak K_z(s+j+1,s)/((s+j+1)!c^j)\). |
| 잘 정의됨 | 분모 양수. |
| Lean 대응 | 미형식화. `certified_probe.responses`는 특정 유리수 입력의 구간 계산이다. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  k178f470ddcb549fe86572026bed89f80/exposition.md §3. |
| 기록별 이명 | |

검토 kfd75ab1e7c494041851fb5f82f97d9e8에서 원 응답·결합·혼합 항등식과 특정 입력의 유리수 구간 계산을 비형식 supported로 수용했다. 이 함수의 원 대상 일반 Lean 식별·부호 정리·구간 코드 커널 인증은 미완료다.


## 149. 말단 혼합 보정
| 칸 | 내용 |
|---|---|
| 이름·기호 | 말단 혼합 보정 · \(\mathscr G^{\rm mix}_{n,k}\) |
| 종류 | 함수 |
| 정의 | k≥1, k+3≤n≤2k+1에서 \(\mathscr G^{\rm mix}_{n,k}:=\mathfrak N_{n,k}(k+1)/\mathfrak N_{n,k}(k)-\mathfrak M_{n,k}(k+1)/\mathfrak M_{n,k}(k)\). |
| 잘 정의됨 | 두 분모 양수는 기존 말단·전체 곡률 양수성. 이 정의에 부호 가정은 없다. |
| Lean 대응 | 미형식화. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  k178f470ddcb549fe86572026bed89f80/exposition.md §5 식 (9). |
| 기록별 이명 | |

검토 kfd75ab1e7c494041851fb5f82f97d9e8에서 원 응답·결합·혼합 항등식과 특정 입력의 유리수 구간 계산을 비형식 supported로 수용했다. 이 함수의 원 대상 일반 Lean 식별·부호 정리·구간 코드 커널 인증은 미완료다.


## 150. 일반 삼각 해 연산
| 칸 | 내용 |
|---|---|
| 이름·기호 | 일반 삼각 해 연산 · \(\operatorname{TriSolve}_a(z,w)(n)\) |
| 종류 | 함수 |
| 정의 | a:ℕ×ℕ→ℚ, w:ℕ→ℚ, z∈ℚ, n∈ℕ에서 \(\operatorname{TriSolve}_a(z,w)(n):=w(n)+z\sum_{j<n}a(n,j)\operatorname{TriSolve}_a(z,w)(j)\). |
| 잘 정의됨 | 엄격히 작은 n만 쓰는 유한 삼각 귀납. |
| Lean 대응 | k178f470ddcb549fe86572026bed89f80/CoupledJets.lean의 `CoupledJets.solve`, `solve_rec`. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  k178f470ddcb549fe86572026bed89f80/CoupledJets.lean 및 formal-verification.md. |
| 기록별 이명 | |

검토 kfd75ab1e7c494041851fb5f82f97d9e8가 일반 삼각 해의 네 정리를 재컴파일·별도 공리 감사하여 accepted/matches로 수용했다. 허용 세 공리만 사용한다. 원 사슬과의 일반 형식 동일성이나 원 U/P의 증명은 이 수용 범위에 포함되지 않는다.


## 151. 일반 삼각 해의 매개변수 차분
| 칸 | 내용 |
|---|---|
| 이름·기호 | 일반 삼각 해의 매개변수 차분 · \(\operatorname{TriJet}_a(w,z,r)(n)\) |
| 종류 | 함수 |
| 정의 | 위 a,w,z와 r,n∈ℕ에서 TriJet(w,z,0)(n):=TriSolve(z,w)(n), TriJet(w,z,r+1)(n):=TriJet(w,z+1,r)(n)−TriJet(w,z,r)(n). |
| 잘 정의됨 | 차분 차수 r에 대한 유한 귀납. |
| Lean 대응 | k178f470ddcb549fe86572026bed89f80/CoupledJets.lean의 `CoupledJets.jet`, `jet_rec`, `jet_as_solve`. |
| 출처 | 정의 처리: kf1d81645162943279b011bd0d3cac6a3.  k178f470ddcb549fe86572026bed89f80/CoupledJets.lean 및 formal-verification.md. |
| 기록별 이명 | |

검토 kfd75ab1e7c494041851fb5f82f97d9e8가 일반 삼각 해의 네 정리를 재컴파일·별도 공리 감사하여 accepted/matches로 수용했다. 허용 세 공리만 사용한다. 원 사슬과의 일반 형식 동일성이나 원 U/P의 증명은 이 수용 범위에 포함되지 않는다.


## 152. 혼합 문턱 개수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 혼합 문턱 개수 · Bᵐⁱˣₙ,ⱼ,ℓ |
| 종류 | 함수 |
| 정의 | n∈ℕ,0≤j≤n,ℓ∈ℕ에서 Bᵐⁱˣₙ,ⱼ,ℓ := #{α∈PFₙ : i≤j인 모든 차의 dᵢ≤ℓ이고 i>j인 모든 차의 dᵢ<ℓ}. n=0에서는 공허 조건을 써 1이다. |
| 잘 정의됨 | 원 과정의 결정성과 유한성. Bᵐⁱˣ₀,₀,₀=1을 A₀,₋₁=0과 동일시하지 않는다. |
| Lean 대응 | k3402f089d15b489eb2cbad3ffa444bb7/lean/Arrival.lean `ParkingArrival.MixedPred`, `mixed`. j>n에서는 전 차가 높은 문턱인 구현 보조 확장. `mixed_full`, `mixed_no_high`, `mixed_zero_threshold`, `mixed_jump`가 원 A,b⁽ᵗ⁾와의 관계를 증명한다. |
| Lean 추가 대응 | k3c8d00ecefb9486697fd5692a47dad49/lean/Chords.lean의 ParkingArrivalProof.mixed_chord,mixed_chord_sharp,mixed_difference_zero. 원 mixed의 현·영 경계. 검토 kf60b5d44129f444b9c13cfa739536768 accepted/matches. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/MixedRecurrence.lean mixed_recurrence_original/mixed_empty/mixed_recurrence_full. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §3 (7) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 153. 앞부분 개수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 앞부분 개수 · Fᵖʳᵉₙ,ℓ(S) |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ,S⊆[n]에서 Fᵖʳᵉₙ,ℓ(S) := #{β∈[n]^|S| : 빈 판에서 처음 |S|대가 성공해 정확히 S를 점유하고 각 변위≤ℓ}. Fᵖʳᵉₙ,ℓ(∅)=1. |
| 잘 정의됨 | 원 부분 과정의 결정성과 유한성. |
| Lean 대응 | 미형식화. k3402f089d15b489eb2cbad3ffa444bb7/code/independent.py `occupancy`의 `forward`. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §3 (10) 앞 정의. 기존 Dℓ(S)는 [18]에 제한된 대상이므로 이 전역 판 크기 매개변수의 새 대상과 구별한다. |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 154. 뒷부분 개수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 뒷부분 개수 · Gᵖᵒˢᵗₙ,ℓ(S) |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ,S⊆[n]에서 Gᵖᵒˢᵗₙ,ℓ(S) := #{γ∈[n]^(n−|S|) : 점유 집합 S에서 시작해 모든 차가 성공하고 각 변위<ℓ}. Gᵖᵒˢᵗₙ,ℓ([n])=1. |
| 잘 정의됨 | 현재 S와 다음 선호로 첫 빈자리가 유일하며 이후 단계도 결정된다. |
| Lean 대응 | 미형식화. k3402f089d15b489eb2cbad3ffa444bb7/code/independent.py `occupancy`의 `backward`. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §3 (10) 앞 정의 |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 155. 도착 원천 개수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 원천 개수 · Sᵃʳʳₕ,ℓ |
| 종류 | 함수 |
| 정의 | h,ℓ∈ℕ에서 Sᵃʳʳₕ,ℓ := b⁽ʰ⁺¹⁾ₕ₊₁,ℓ. 크기는 h+1이므로 원 b의 크기 0 값을 정의하지 않는다. |
| 잘 정의됨 | 기존 도착 시각별 정확 개수의 제한 대입이다. |
| Lean 대응 | 독립 함수 선언 없음. k3402f089d15b489eb2cbad3ffa444bb7/lean/Arrival.lean `bArrival`에 n=h+1,t=마지막 차량을 대입한 대상. (13)의 일반 합 식별은 미형식화. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Source.lean source_recurrence/source_zero_above. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §4.2 (13) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 156. 도착 전달 커널


| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 전달 커널 · Hᵃʳʳₘ,ⱼ,ℓ |
| 종류 | 함수 |
| 정의 | m,ℓ∈ℕ,0≤j≤m에서 Hᵃʳʳₘ,ⱼ,ℓ := (ℓ+min(m+1,ℓ)) Bᵐⁱˣₘ,ⱼ,ℓ. |
| 잘 정의됨 | 자연수의 유한 곱이다. |
| Lean 대응 | k3402f089d15b489eb2cbad3ffa444bb7/lean/Arrival.lean `arrivalKernel`, `kernel_threshold_gain`. j>m에는 mixed의 보조 확장에 따른 구현 값이다. 원 표시 재귀 (15) 전체의 형식 보증은 없다. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Marked.lean marked_root_saturation. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §4.2 (14) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 157. 혼합 문턱 이변수 급수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 혼합 문턱 이변수 급수 · Gᵐⁱˣℓ(x,y) |
| 종류 | 함수 |
| 정의 | 정수 ℓ≥1에서 Gᵐⁱˣℓ(x,y) := Σₕ,ᵣ≥₀ Bᵐⁱˣₕ₊ᵣ,ₕ,ℓ xʰyʳ/(h!r!) ∈ ℚ[[x,y]]. |
| 잘 정의됨 | 각 계수를 (7)의 유한 개수로 주는 형식급수다. 수렴 가정이 없다. |
| Lean 대응 | 미형식화 |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §4.3 (17) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 158. 도착 표시 이변수 급수


| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 표시 이변수 급수 · Gᵃʳʳℓ(x,y) |
| 종류 | 함수 |
| 정의 | 정수 ℓ≥1에서 Gᵃʳʳℓ(x,y) := Σₕ,ᵣ≥₀ b⁽ʰ⁺¹⁾ₕ₊ᵣ₊₁,ℓ xʰyʳ/(h!r!) ∈ ℚ[[x,y]]. |
| 잘 정의됨 | 각 계수는 양수 크기의 원 도착 시각별 정확 개수다. |
| Lean 대응 | 미형식화 |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §4.3 (17) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 159. 도착 인접 차


| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 인접 차 · Jₕ,ᵣ,ℓ |
| 종류 | 함수 |
| 정의 | h,r∈ℕ,정수 ℓ≥1에서 Jₕ,ᵣ,ℓ := b⁽ʰ⁺¹⁾ₕ₊ᵣ₊₁,ℓ₊₁−b⁽ʰ⁺¹⁾ₕ₊ᵣ₊₁,ℓ ∈ ℤ. |
| 잘 정의됨 | 두 유한 개수의 정수 차다. 원 전체 차분 Δ와 구별한다. |
| Lean 대응 | 별도 함수 선언 없음. 원 `bArrival`의 정수 포함 차. (20)의 재귀 동일성은 미형식화. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Bounds.lean J_recurrence 및 Initial.lean의 정수 초기값·행 합. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §5.3 (20) 앞 정의 |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 160. 도착 부호 전달 하계


| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 부호 전달 하계 · Zᵋₕ,ᵣ,ℓ |
| 종류 | 함수 |
| 정의 | h,r∈ℕ,ℓ≥1,ε∈{0,1}에서 Zᵋₕ,₀,ℓ := Sᵃʳʳₕ,ℓ₊₁−Sᵃʳʳₕ,ℓ. r≥1에서는 Σₐ₌₀ʰΣᵦ₌₀ʳ⁻¹ binom(h,a)binom(r−1,b)[Hᵃʳʳₐ₊ᵦ,ₐ,ℓ₊₁ Zᵋₕ₋ₐ,ᵣ₋₁₋ᵦ,ℓ + ε Bᵐⁱˣₐ₊ᵦ,ₐ,ℓ b⁽ʰ⁻ᵃ⁺¹⁾ₕ₊ᵣ₋ₐ₋ᵦ,ℓ]로 정의한다. 값은 ℤ다. |
| 잘 정의됨 | 재귀 오른쪽의 r−1−b가 r보다 작으므로 r 귀납으로 유일하다. |
| Lean 대응 | 미형식화. k3402f089d15b489eb2cbad3ffa444bb7/code/transport_bounds.py의 `bounds[0]`, `bounds[1]`. |
| 추가 형식 대응 | ke2436447b98547689b08023d2935b621/Bounds.lean Z_order/Z_le_J 및 Initial.lean Z_row_Delta. 검토 kd5aa5110d39449359578cdc2287a86a9가 해당 일반 형식 결과를 accepted/matches로 수용했다. 전칭 부호·P는 포함하지 않는다. 정의·정의역은 그대로다. |
| 출처 | k3402f089d15b489eb2cbad3ffa444bb7/exposition.md §5.3 (21) |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 kfd8c65fff6a84089ad0591255b0674a3는 원 사건·혼합 문턱 끝점·커널 증가만 형식 수용하고 일반 마지막 차량 전달·두 급수·J 및 Z의 재귀·전칭 부호는 형식 수용하지 않았다.

## 161. 역방향 차분 원천


| 칸 | 내용 |
|---|---|
| 이름·기호 | 역방향 차분 원천 · 𝒵ʳᵉᵛₖ,ⱼ (`\mathscr Z^{\rm rev}_{k,j}`) |
| 종류 | 함수 |
| 정의 | 정수 k≥1,j≥k+1에서, j=k+1이면 𝒵ʳᵉᵛₖ,ⱼ:=(2k+2)Tₖ−Tₖ₊₁이고, j≥k+2이면 𝒵ʳᵉᵛₖ,ⱼ:=3Δⱼ,ₖ+Tₖ binom(j+1,j−k)(j−k−1)^(j−k−1)이다. 차는 정수 차다. |
| 잘 정의됨 | j≥k+2인 두 번째 경우의 거듭제곱 밑과 지수는 모두 양수다. Δ는 k≥1의 정본 정의역 안이며, b의 크기 0 값을 사용하지 않는다. |
| Lean 대응 | 미형식화. `k39ce4750627e4a0e9735832b2fb49076/reverse_probe.py`의 `a[j]`는 유한 입력의 계산 구현이다. |
| 출처 | 기록 k39ce4750627e4a0e9735832b2fb49076의 `exposition.md` §3 식 (10). |
| 기록별 이명 | 없음 |

정의 채택: k35e89dbf2de54499b885a8a7b000a2d8. 독립 검토 k32399dd4a57c4e8f980f7103f4fda6d3는 원천 항등식과 무한 부분족을 비형식으로 수용했다. 원천 합의 일반 Lean 연결·혼합 부호·U/P는 미해결이다.

## 162. 문턱 1까지 확장한 전체 계수 절단 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 문턱 1까지 확장한 전체 계수 절단 다항식 · 𝓟⁺q(z) |
| 종류 | 함수 |
| 정의 | 정수 q≥1에서 𝓟⁺q(z):=Σₘ₌₀^(q−1)fₘzᵐ∈ℚ[z]. |
| 잘 정의됨 | 유한 합이다. f₀=1이므로 𝓟⁺₁=1. q≥2에서 §121의 𝓟q와 값이 같지만 정의역이 다른 함수다. q=0은 포함하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 및 glossary-proposals.md 첫 제안. 정의역 확장에 기존 이름을 재사용하지 않도록 k1223d51b5e5d4388aedff155d690d78d에서 개명했다. |
| 기록별 이명 | 기록 k9a8431776364465195c7ae81c0c031ec의 𝒫q(q≥1의 보조 확장). 기존 q≥2 부분의 이름은 §121 참조. |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 163. 두 차량 국소 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 두 차량 국소 계수 · (σᵃᵈʲℓ(g,d),τᵃᵈʲℓ(g,d),σˢᵉᵖℓ(g,d),τˢᵉᵖℓ(g,d)) |
| 종류 | 함수 |
| 정의 | g,d,ℓ∈ℕ에서 σᵃᵈʲ=[g>ℓ]min(g+d,ℓ)+[d>ℓ]min(g,ℓ), τᵃᵈʲ=[g+d>ℓ]min(g,ℓ+1)+[g>ℓ]min(d,ℓ+1), σˢᵉᵖ=[g>ℓ]min(d,ℓ)+[d>ℓ]min(g,ℓ), τˢᵉᵖ=[d>ℓ]min(g,ℓ+1)+[g>ℓ]min(d,ℓ+1). 원 두 빈자리 적용에는 g,d≥1이다. |
| 잘 정의됨 | 유한 자연수 식이다. 원 과정과의 일반 분할 연결은 비형식 증명이다. |
| Lean 대응 | k9a8431776364465195c7ae81c0c031ec/lean/PairGap.lean의 adjacentSource, adjacentTarget, separatedSource, separatedTarget 및 여섯 정리 중 국소 정리 다섯 개. 독립 검토 ke14b219b620141348788edb5c86fe65c에서 accepted/matches다. 원 도착 단조성의 일반 연결은 아직 미형식화다. |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §3, 식 (6) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 164. 도착 초기 음수 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 초기 음수 급수 · Nˢʳᶜℓ(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 Nˢʳᶜℓ(z):=fℓzℓℱℓ(z)∈ℚ[[z]]. 이름은 초기 차에서 이 비음수 급수를 음수로 전달한다는 뜻이다. |
| 잘 정의됨 | 기존 정본 급수와 다항식의 곱이다. |
| Lean 대응 | 미형식화; k9a8431776364465195c7ae81c0c031ec/code/envelopes.py의 negative는 지수 계수 구현 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 식 (10) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 165. 도착 초기 양수 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 초기 양수 급수 · Uˢʳᶜℓ(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 Uˢʳᶜℓ:=(ℱℓ₊₁+ℱℓ−𝓟ℓ₊₁)(ℱℓ₊₁−ℱℓ)∈ℚ[[z]]. |
| 잘 정의됨 | §121의 𝓟의 기존 정의역 ℓ+1≥2에서 정의된다. 포화와 A의 문턱 단조성으로 계수별 비음수다. |
| Lean 대응 | 미형식화; k9a8431776364465195c7ae81c0c031ec/code/envelopes.py의 positive는 식 (11)의 동일한 지수 계수 구현 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 식 (10) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 166. 도착 부호 전달 지수급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 부호 전달 지수급수 · Ẑℓ(x,y) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 Ẑℓ(x,y):=Σₕ,ᵣ≥₀ Z¹ₕ,ᵣ,ℓ xʰyʳ/(h!r!)∈ℚ[[x,y]]. |
| 잘 정의됨 | 정본 Z¹의 계수로 유일하게 정의된다. Z¹의 새 의미가 아니라 그 지수급수다. |
| Lean 대응 | 미형식화 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 식 (12) 앞 |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 167. 부호 분리 전달 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 부호 분리 전달 급수 · (Xℓ,Yℓ) |
| 종류 | 함수 |
| 정의 | ℓ≥1, K₊=2(ℓ+1)Gᵐⁱˣℓ₊₁−Vℓ(x+y)에서 ∂yXℓ=K₊Xℓ+GᵐⁱˣℓGᵃʳʳℓ, Xℓ(x,0)=Uˢʳᶜℓ(x), ∂yYℓ=K₊Yℓ, Yℓ(x,0)=Nˢʳᶜℓ(x)를 만족하는 ℚ[[x,y]] 급수로 정의한다. |
| 잘 정의됨 | y차수 귀납으로 계수별 유일하다. 모든 계수가 비음수이고 Ẑℓ=Xℓ−Yℓ다. |
| Lean 대응 | 미형식화 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 식 (12) 뒤 |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 168. 도착 대각 적분

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 대각 적분 · 𝓘[P] |
| 종류 | 함수 |
| 정의 | P∈ℚ[[x,y]]에서 𝓘[P](z):=∫₀ᶻP(x,z−x)dx∈ℚ[[z]]. 항별 다항식 적분으로 정의한다. P=Σcₕᵣxʰyʳ/(h!r!)이면 𝓘[P]=Σₙ≥₁(Σₕ₊ᵣ₌ₙ₋₁cₕᵣ)zⁿ/n!. |
| 잘 정의됨 | 매 차수마다 유한 합이며 계수마다 유일하다. 기존 일반 지수 정규화 연산이나 적분 성분 원천 연산과는 정의역이 다르다. |
| Lean 대응 | 미형식화 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §4 식 (13) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 169. 계승비 커널 보정 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 계승비 커널 보정 급수 · Rᶠᵃᶜℓ,p(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1,1≤p≤ℓ+2에서 Rᶠᵃᶜℓ,p(z):=2(ℓ+1)Σₘ≥ℓ₊₂,⌊m/(m−ℓ−1)⌋₌ₚ bₘ,ℓ₊₁ zᵐ⁻ᵖ/m!. |
| 잘 정의됨 | m−ℓ−1>0이고 p≤ℓ+2≤m이다. 각 차수·p에서 항은 유한하다. |
| Lean 대응 | 미형식화; k9a8431776364465195c7ae81c0c031ec/code/factorial_envelope.py의 corrections는 보통 계수의 재척도 구간 구현 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §5 식 (17) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 170. 양수 전달 하한 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 양수 전달 하한 급수 · Pᵉⁿᵛℓ(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 Pᵉⁿᵛℓ(0)=0, (Pᵉⁿᵛℓ)'=𝒦ℓ₊₁Pᵉⁿᵛℓ+Uˢʳᶜℓ+(ℱℓ²−ℱℓ₋₁²)/2를 만족하는 ℚ[[z]]의 유일 급수. |
| 잘 정의됨 | 지수 계수 귀납으로 유일하다. 𝒦는 정본 §122의 첫 성분이며 q=ℓ+1≥2다. |
| Lean 대응 | 미형식화; factorial_envelope.py의 pl,pu는 보통 계수의 재척도 하·상 구간 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §5 식 (19) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 171. 음수 전달 상한 모멘트

| 칸 | 내용 |
|---|---|
| 이름·기호 | 음수 전달 상한 모멘트 · Mᵉⁿᵛℓ,d(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1,d∈ℕ에서 Mᵉⁿᵛℓ,d(0)=0, (Mᵉⁿᵛℓ,d)'=𝒦ℓ₊₁Mᵉⁿᵛℓ,d+Σₚ₌₁^(ℓ+2)Rᶠᵃᶜℓ,pMᵉⁿᵛℓ,d+p+zᵈNˢʳᶜℓ인 유일 급수족. |
| 잘 정의됨 | 미분식의 n+1차 계수는 n차 계수만 참조한다. 최소 차수 ℓ+d+1이므로 매 고정 차수에서는 유한한 d만 필요하다. |
| Lean 대응 | 미형식화; factorial_envelope.py의 vl,vu는 보통 계수 재척도 구간 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §5 식 (19) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 172. 부호 전달 포락선

| 칸 | 내용 |
|---|---|
| 이름·기호 | 부호 전달 포락선 · Cᵉⁿᵛℓ(z) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 Cᵉⁿᵛℓ(z):=Pᵉⁿᵛℓ(z)−Mᵉⁿᵛℓ,0(z)∈ℚ[[z]]. |
| 잘 정의됨 | 앞의 두 급수의 차다. 원 Δ 또는 Z¹의 재정의가 아니라 식 (20)의 실제 하계다. |
| Lean 대응 | 미형식화. 계산의 low,upper는 [zⁿ]Cᵉⁿᵛℓ(z/3)의 바깥쪽 구간이다. |
| 출처 | k9a8431776364465195c7ae81c0c031ec/exposition.md §5 식 (20) |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.


## 173. 끝점·현 포락선

| 칸 | 내용 |
|---|---|
| 이름·기호 | 끝점·현 포락선 · (Cᵉⁿᵈℓ,Cˢᵉᶜ,⁰ℓ,Cˢᵉᶜ,¹ℓ) |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 a=𝒦ℓ₊₁,b=2(ℓ+1)ℱℓ₊₁−Vℓ,c=2ℓℱℓ₋₁−Vℓ₋₁,d=ℱℓ₋₁,S=ℱℓ(ℱℓ−𝓟⁺ℓ),R=2(ℓ+1)(ℱℓ₊₁−ℱℓ)/z로 놓는다. 상수항 0인 u'=au+Uˢʳᶜℓ,v'=bv+Nˢʳᶜℓ,w'=cw+S,t'=at+dw 및 L_d'=aL_d+RL_d₊₁+zᵈNˢʳᶜℓ를 푼다. Cᵉⁿᵈℓ:=u−v+t, Cˢᵉᶜ,⁰ℓ:=u+t−L₀, Cˢᵉᶜ,¹ℓ:=Pᵉⁿᵛℓ−L₀. |
| 잘 정의됨 | 각 미분식은 계수 귀납으로 유일하다. R의 분자는 최소 차수 ℓ+2이므로 z 나눗셈은 유일하다. ℓ=1에도 §162의 𝓟⁺를 쓴다. |
| Lean 대응 | 미형식화; envelopes.py, probe_convex.py의 실패 비교 재현 구현 |
| 출처 | k9a8431776364465195c7ae81c0c031ec/calculation-notes.md 「첫 포락선의 수식」 및 「현 상계 단계」 |
| 기록별 이명 | 없음 |

정의 처리: k1223d51b5e5d4388aedff155d690d78d. ke14b219b620141348788edb5c86fe65c는 이 정의를 쓰는 부분 결과를 수용했으며 전칭 L/P를 수용한 것은 아니다.



## 174. 혼합 역분모 자료

| 칸 | 내용 |
|---|---|
| 이름·기호 | 혼합 역분모 자료 · (Eᵐⁱˣq,Iᵐⁱˣq,Dᵐⁱˣq,Qᵐⁱˣq) |
| 종류 | 함수 |
| 정의 | 정수 q≥1에서 Eᵐⁱˣq(z):=exp(−Wq₋₁(z)), Iᵐⁱˣq(z):=∫₀ᶻEᵐⁱˣq(t)dt, Dᵐⁱˣq(z):=1−qIᵐⁱˣq(z), Qᵐⁱˣq(z):=Dᵐⁱˣq(z)−Eᵐⁱˣq(z)/ℱq(z). 모두 ℚ[[z]]이다. |
| 잘 정의됨 | W의 상수항은 0, ℱ의 상수항은 1이므로 형식 지수·역급수가 유일하다. |
| Lean 대응 | 미형식화. code/exact_transport.py의 mixed_data. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §3.1 식 (2). |
| 기록별 이명 | |

해설에서 E_q,I_q,D_q,Q_q는 이 한 절의 명시적 줄임이다. 원 포화 결손·정본 사슬 곡률 등의 기호를 바꾸지 않는다. Q의 계수는 일반적으로 부호를 가진다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 175. 도착 원천 지수급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 원천 지수급수 · 𝒮ᵃʳʳq |
| 종류 | 함수 |
| 정의 | 정수 q≥1에서 𝒮ᵃʳʳq(x):=Σₕ≥₀Sᵃʳʳₕ,q xʰ/h!∈ℚ[[x]]. |
| 잘 정의됨 | 정본 도착 원천 개수의 계수별 정의. 원천의 크기는 h+1≥1이다. |
| Lean 대응 | 미형식화. mixed_data의 S. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §3.1. ℱq(ℱq−𝓟⁺q)와의 동일성은 수용된 마지막 차량 분할에서 따른다. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 176. 도착 전달 커널 지수급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 전달 커널 지수급수 · **H**q |
| 종류 | 함수 |
| 정의 | 정수 q≥1에서 **H**q(x,y):=Σₕ,ᵣ≥₀Hᵃʳʳₕ₊ᵣ,ₕ,q xʰyʳ/(h!r!)∈ℚ[[x,y]]. |
| 잘 정의됨 | 기존 원 커널의 계수별 정의. 2qGᵐⁱˣq−Vq₋₁(x+y)와 같다. |
| Lean 대응 | 전체 급수는 미형식화. 계수는 기존 ParkingArrival.arrivalKernel. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §3.1; 기존 Hᵃʳʳ의 급수 표기. |
| 기록별 이명 | |

정본의 한 변수 𝒦q 및 Hᵃʳʳ의 정수 계수와 구별한다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 177. 원 공통 동차 전달자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 공통 동차 전달자 · 𝒯q[u] |
| 종류 | 함수 |
| 정의 | 정수 q≥1,u∈ℚ[[x]]에서 𝒯q[u]는 ∂y𝒯q[u]=**H**q𝒯q[u], 𝒯q[u](x,0)=u(x)를 만족하는 ℚ[[x,y]] 급수다. |
| 잘 정의됨 | y차수 귀납으로 존재·유일. |
| Lean 대응 | 미형식화. homogeneous는 그 대각 적분의 계산이다. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §3.1 식 (6) 앞. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 178. 원 공통 강제 전달자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 공통 강제 전달자 · 𝒱q[v] |
| 종류 | 함수 |
| 정의 | 정수 q≥1,v∈ℚ[[x,y]]에서 𝒱q[v]는 ∂y𝒱q[v]=**H**q𝒱q[v]+v, 𝒱q[v](x,0)=0을 만족하는 ℚ[[x,y]] 급수다. |
| 잘 정의됨 | y차수 귀납으로 존재·유일. |
| Lean 대응 | 미형식화. minimum_forcing은 특정 v의 대각 적분 계산이다. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §4.1 식 (9) 앞. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 179. 정확 버린 원천 급수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정확 버린 원천 급수 · 𝓡ᵃʳʳℓ |
| 종류 | 함수 |
| 정의 | 정수 ℓ≥1에서 𝓡ᵃʳʳℓ(x,y):=**H**ℓ₊₁(x,y)−**H**ℓ(x,y)−Gᵐⁱˣℓ(x,y). |
| 잘 정의됨 | 기존 두 변수 급수들의 차. 각 계수의 비음수성은 원 커널 잔여와 혼합 문턱 단조성에서 따른다. |
| Lean 대응 | 급수는 미형식화. 계수 항등식은 k9a843…/lean/PairGap.lean의 ParkingPairGap.original_kernel_residual. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §4.1 식 (11). |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 180. 최소 원천 분리 원시함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최소 원천 분리 원시함수 · Tˢᵉᵖℓ,p,k |
| 종류 | 함수 |
| 정의 | ℓ≥1,p≥0,k∈{0,1,2},q=ℓ+1에서 Tˢᵉᵖℓ,p,k(z):=∫₀ᶻ(Eᵐⁱˣℓ(t))²(Iᵐⁱˣq(t))ᵏ/((Eᵐⁱˣq(t))(Dᵐⁱˣℓ(t))ᵖ⁺³)dt. |
| 잘 정의됨 | 분모의 상수항은 1, 형식 적분의 상수항은 0으로 고정된다. |
| Lean 대응 | 미형식화. minimum_forcing의 Tp[p][k]. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §4.2의 고정 ℓ에서 쓰는 임시 T_{p,k}. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 181. 삼각 적분 차 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 삼각 적분 차 연산 · 𝔄(f,g) |
| 종류 | 함수 |
| 정의 | f,g∈ℚ[[z]]에서 𝔄(f,g)(z):=g(z)∫₀ᶻf(x)dx−∫₀ᶻf(x)g(x)dx. |
| 잘 정의됨 | 계수별 유한 합과 유리수 적분. |
| Lean 대응 | 미형식화. minimum_forcing의 T*prim−(poly*T).integral(). |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §4.2 식 (14) 앞. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 182. 대각 커널 부호 보정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대각 커널 부호 보정 · 𝒞ᵏᵉʳℓ |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 𝒞ᵏᵉʳℓ:=𝓘[(Gᵐⁱˣℓ₊₁(x,y)−ℱℓ(x+y))(Gᵃʳʳℓ₊₁(x,y)−Gᵃʳʳℓ(x,y))]∈ℚ[[z]]. |
| 잘 정의됨 | 기존 급수의 곱과 정본 대각 적분. 부호를 갖는 급수다. |
| Lean 대응 | 미형식화. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §6.2 식 (17). |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 183. 공통 분모 곡률 분자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 공통 분모 곡률 분자 · 𝒩ᵈᵉⁿℓ |
| 종류 | 함수 |
| 정의 | ℓ≥1에서 𝒩ᵈᵉⁿℓ:=(ℱℓ₊₁−2ℱℓ+ℱℓ₋₁)/(ℱℓ₊₁ℱℓℱℓ₋₁)∈ℚ[[z]]. |
| 잘 정의됨 | 각 ℱ의 상수항은 1이다. |
| Lean 대응 | 미형식화. comparison_probes.py와 summarize.py의 num. |
| 출처 | k1e30f22632294be9991c2e6b0dba5d04/exposition.md §6.4 식 (21). |
| 기록별 이명 | |

Ĵℓ=Gᵃʳʳℓ₊₁−Gᵃʳʳℓ는 해설에서 정본 J의 지수급수를 줄여 쓴 임시 표기다. 정본 Ẑℓ와 혼동하지 않는다. 원 J의 정의·정의역을 변경하거나 다른 개수로 바꾸지 않았다.

정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k1e30f22632294be9991c2e6b0dba5d04의 공개 파일이다. 검토 k9ec509cf72594adeb4ffac9e09a9f6bd는 비형식 부분 결과를 supported로 수용했으며 새 일반 Lean 연결은 없다.

## 184. 조건별 한 차량 선호 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건별 한 차량 선호 개수 · W_R(S,s) |
| 종류 | 함수 |
| 정의 | n∈ℕ, S⊆[n], s∈[n], R:ℕ→Prop에서 W_R(S,s):=#{a∈[n]: next(a,S)=s ∧ R(s−a)}. next는 정본 원 과정의 한 단계 첫 빈자리 선택이며 실패이면 등식이 거짓이다. |
| 잘 정의됨 | 유한 집합의 개수다. `weight_gap`이 빈자리에서는 d=0,…,g_S(s)−1의 R 만족 개수와 같음을 증명한다. |
| Lean 대응 | `ParkingArrivalProof.weight` 및 `weight_occupied`, `weight_gap`, `weight_lt`, `weight_le`, `weight_eq` (`lean/Gap.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §3.1. |
| 기록별 이명 | |

R(d)=(d≤ℓ)인 제한은 정본 §15의 wℓ(S,s)와 같다. 기존 가중치의 이름을 일반 R 함수에 재사용하지 않고 확장을 명시했다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 185. 순서 있는 두 자리 선호쌍 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 순서 있는 두 자리 선호쌍 개수 · C_{R,T}(S;p,q) |
| 종류 | 함수 |
| 정의 | n∈ℕ, S⊆[n], p,q∈[n], R,T:ℕ→Prop에서 C_{R,T}(S;p,q):=W_R(S,p)W_T(S∪{p},q). |
| 잘 정의됨 | 유한 개수의 곱. `pairCoeff_card`가 실제 두 원 선호쌍의 개수임을 증명한다. |
| Lean 대응 | `ParkingArrivalProof.pairCoeff`, `pairCoeff_card`, `pairCoeff_adjacent`, `pairCoeff_separated` (`lean/Transfer.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §3.2. |
| 기록별 이명 | |

정본 §163의 네 국소 계수와 다른 보조 함수다. 조건 (=ℓ,<ℓ) 또는 (≤ℓ,=ℓ)에서 두 순서를 합하고 연속·분리 간격을 대입하면 그 네 계수와 같다는 것을 이번에 원 과정에서 증명했다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 186. 조건별 한 단계 합산 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건별 한 단계 합산 연산 · T_R |
| 종류 | 함수 |
| 정의 | n∈ℕ, R:ℕ→Prop, f:𝒫([n])→ℕ에서 (T_R f)(S):=Σ_{s∈[n]}W_R(S,s) f(S∪{s}). |
| 잘 정의됨 | 유한 자연수 합이다. |
| Lean 대응 | `ParkingArrivalProof.step`, `step_preferences`, `step_exchange` (`lean/Transfer.lean`, `lean/Count.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §3.3. |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 187. 조건 목록을 만족하는 부분 실행

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건 목록을 만족하는 부분 실행 · Good(ℛ,β,S) |
| 종류 | 성질·관계 |
| 정의 | n,k∈ℕ, ℛ=(R₁,…,Rₖ), Rᵢ:ℕ→Prop, β∈[n]^k, S⊆[n]에서 Good(ℛ,β,S):⇔ S에서 시작한 원 과정이 β의 차들을 순서대로 전부 성공시키고 각 변위 dᵢ가 Rᵢ(dᵢ)를 만족한다. 길이가 다른 β에는 거짓으로 구현한다. |
| 잘 정의됨 | 원 부분 과정의 결정성. |
| Lean 대응 | `ParkingArrivalProof.Good`, `good_run`, `good_original` (`lean/Count.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §3.4. |
| 기록별 이명 | |

정본 §43의 ‘변위 제한 실행 기록’은 특정 균일 문턱과 실행 자료를 담는 대상이다. 이번 Good은 임의 조건 목록에 대한 관계이므로 별도 보조 관계로 둔다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 188. 조건 목록의 완료 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건 목록의 완료 개수 · Nᶜᵒⁿᵈ_ℛ(S) |
| 종류 | 함수 |
| 정의 | 위 n,ℛ,S에서 Nᶜᵒⁿᵈ_ℛ(S):=#{β∈[n]^k:Good(ℛ,β,S)}. |
| 잘 정의됨 | 유한 개수. 구현은 Nᶜᵒⁿᵈ_∅=1, Nᶜᵒⁿᵈ_{R::ℛ}=T_R Nᶜᵒⁿᵈ_ℛ를 사용하며 `value_count`가 위 원 유한 개수와의 일반 동일성을 증명한다. |
| Lean 대응 | `ParkingArrivalProof.value`, `value_count`, `value_count_length`, `value_ofFn`, `value_arrival` (`lean/Count.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §3.4. |
| 기록별 이명 | |

원 누적 개수 A나 원 도착 개수 b⁽ᵗ⁾의 재정의가 아닌 보조 함수이며, 조건 목록과 점유 집합을 인수로 명시한다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 189. 도착 성분 부분합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 성분 부분합 · Sᵖᵃʳᵗₙ,ⱼ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, ℓ∈ℕ, 0≤j≤n에서 Sᵖᵃʳᵗₙ,ⱼ,ℓ:=Σ_{t=1}^j b⁽ᵗ⁾ₙ,ℓ. 빈 합은 0이다. |
| 잘 정의됨 | 유한 자연수 합. |
| Lean 대응 | `ParkingArrivalProof.arrivalPrefix`, `mixed_prefix`, `mixed_difference_prefix` (`lean/Chords.lean`). j>n에는 전 성분 합으로 포화되는 구현상 보조 확장이 있다. |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §5. |
| 기록별 이명 | |

ℓ≥1이면 원 Bᵐⁱˣₙ,ⱼ,ℓ−Aₙ,ℓ₋₁와 같다. ℓ=0에서 같은 차분 대입을 정의하지 않는다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 190. 정수 Green 가중치

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정수 Green 가중치 · G_{D,s}(r) |
| 종류 | 함수 |
| 정의 | D∈ℕ, 0≤s,r≤D에서 G_{D,s}(r):=min(r,s)(D−max(r,s))∈ℕ. 정수 합에서는 ℤ에 포함시킨다. 길이 D는 명제 L과 구별한다. |
| 잘 정의됨 | 유한 자연수 곱이며 max(r,s)≤D이다. |
| Lean 대응 | `ParkingArrivalProof.greenWeight`, `greenWeight_formula`, `greenWeight_step`, `green_identity`, `original_green_internal` (`lean/Green.lean`). |
| 출처 | k3c8d00ecefb9486697fd5692a47dad49/`exposition.md` §6. |
| 기록별 이명 | |

구현의 전 자연수 r,s에 대한 별도 보조 확장은 r≤s일 때 r(D−s), 그렇지 않으면 s(D−r)를 정수에서 계산한다. 정본 제안 영역 밖의 이 조각식은 비음수 가중치라고 주장하지 않는다. 이번 적용은 항상 0≤r,s≤D이다.


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 k3c8d00ecefb9486697fd5692a47dad49의 공개 파일이다. 검토 kf60b5d44129f444b9c13cfa739536768는 세 형식 결과를 supported/accepted/matches/conforms로 수용했다.

## 191. 도착 숲 · G_α

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 숲 · G_α |
| 종류 | 함수 |
| 정의 | n≥1, α∈PFₙ에 대해 G_α := 부모 함수 p_α로 정한 [n] 위 뿌리 있는 숲. 여기서 p_α(0):=0이고 v∈[n]에 대해 p_α(v) := (자리 s>s_v 가운데 그 자리에 주차한 차의 번호가 v보다 큰 가장 작은 s에 주차한 차의 번호), 그런 자리가 없으면 p_α(v):=0. |
| 잘 정의됨 | 성공 목록에서 자리마다 차가 하나씩 있으므로 최솟값의 차가 유일하다. p_α(v)>v 또는 0이므로 부모 사슬은 0에서 끝나고 G_α∈𝔉↓ₙ다. α ↦ (G_α, d(α))가 {(G,δ): G∈𝔉↓ₙ, 0≤δ_v≤t_v(G)−1}로 가는 전단사라는 사실은 exploration.md §3.1 명제 1(탐구 기록, 미검토)과 n≤7 전수 대조다. |
| Lean 대응 | 미형식화 |
| 이번 보완 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md의 원 전단사·숲 가중합·골격 분해는 검토 k34fb712e85cd44ec8192ca96eb115da1에서 비형식 supported다. 부모 함수 숲·개별 전단사의 일반 Lean 증명은 아직 없다. |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §3.1 |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 192. 골격 · Sk_x(G)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 · Sk_x(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, 실수 x≥0에 대해 Sk_x(G) := {v∈[n] : t_v(G)>x}. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 이번 보완 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md의 원 전단사·숲 가중합·골격 분해는 검토 k34fb712e85cd44ec8192ca96eb115da1에서 비형식 supported다. 부모 함수 숲·개별 전단사의 일반 Lean 증명은 아직 없다. |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §5.1 |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 193. Cayley 분할 핵 · Spl(t,s)

| 칸 | 내용 |
|---|---|
| 이름·기호 | Cayley 분할 핵 · Spl(t,s) |
| 종류 | 함수 |
| 정의 | 정수 t≥2, (t−1)/2<s≤t−1에 대해 Spl(t,s) := binom(t−1,s)·s^{s−1}·(t−s)^{t−s−2}/t^{t−2}. (t−s=1이면 (t−s)^{t−s−2}=1^{−1}=1.) |
| 잘 정의됨 | 유한 유리수. 크기 t−1 위 뿌리 있는 숲 중 가장 큰 나무의 크기가 s인 것의 비율이며, s>(t−1)/2이면 가장 큰 나무가 유일하다. |
| Lean 대응 | 미형식화 |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §5.1 |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 194. 골격 가중 다항식 · Ŵₙ(x;c)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 가중 다항식 · Ŵₙ(x;c) |
| 종류 | 함수 |
| 정의 | n∈ℕ, 정수 x≥1, 실수 c≥0에 대해 Ŵₙ(x;c) := Σ_{G∈𝔉↓ₙ} ∏_{v∈[n]} w_{x,c}(t_v(G)), 여기서 w_{x,c}(t):=t (t≤x), :=c (t>x). n=0에서는 빈 숲 하나와 빈 곱으로 Ŵ₀(x;c)=1. |
| 잘 정의됨 | 유한합. 점화식 Ŵ_{m+1}=Σ_{r=0}^{m} binom(m,r) w_{x,c}(r+1) Ŵ_r Ŵ_{m−r}로 계산된다(exploration.md §4.1). Ŵₙ(x;x)=Aₙ,ₓ₋₁, Ŵₙ(x;x+1)=Aₙ,ₓ는 §3.1 명제 1에서 따른다. |
| Lean 대응 | 미형식화 |
| 이번 보완 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md의 원 전단사·숲 가중합·골격 분해는 검토 k34fb712e85cd44ec8192ca96eb115da1에서 비형식 supported다. lean/SkeletonAlgebra.lean의 skeletonEval/gammaPlus/gammaMinus는 재귀 평가기의 구현이며 원 A·b와의 대수 연결만 accepted/matches다. 이는 그 선행 기록 당시의 범위다. 현재 자연수 제한의 일반 식별은 아래 k1b4bb39af602435783a027a919ef8943의 수용된 형식 대응을 따른다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.canonicalSkeleton, canonicalSkeleton_eq. 자연수 x≥1,c≥0 제한의 실제 숲 합과 skeletonEval 동일성. 실수 c 전체는 별도이며 x=0은 보조 확장. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §4.1 |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 195. 골격 곡률 이득 · Γ⁺ₙ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 곡률 이득 · Γ⁺ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 ℓ≥1, x:=ℓ+1에 대해 Γ⁺ₙ,ℓ := Aₙ,ℓ₊₁ − 2Aₙ,ℓ + Ŵₙ(x;x−1). |
| 잘 정의됨 | 해당 없음. 비음수성과 Δₙ,ℓ=Γ⁺ₙ,ℓ−Γ⁻ₙ,ℓ는 exploration.md §4.1 명제 4(탐구 기록, 미검토)이며 n≤120 정확 계산으로 대조했다. |
| Lean 대응 | 미형식화 |
| 이번 보완 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md의 원 전단사·숲 가중합·골격 분해는 검토 k34fb712e85cd44ec8192ca96eb115da1에서 비형식 supported다. lean/SkeletonAlgebra.lean의 skeletonEval/gammaPlus/gammaMinus는 재귀 평가기의 구현이며 원 A·b와의 대수 연결만 accepted/matches다. 이는 그 선행 기록 당시의 범위다. 현재 자연수 제한의 일반 식별은 아래 k1b4bb39af602435783a027a919ef8943의 수용된 형식 대응을 따른다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.canonicalGammaPlus, canonicalGammaPlus_eq. 양수 n,ℓ의 정본 최초 정의를 정수 차로 구현하고 기존 gammaPlus와 식별. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §4.1 |
| 기록별 이명 | |


제안의 세 Ŵ 값 표현 대신 원 해설 §4.1 최초 정의를 채택한다. 두 표현의 동일성은 원 숲 가중합 연결을 확립할 연구 의무다.

정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 196. 꽉 찬 상자 손실 · Γ⁻ₙ,ℓ

| 칸 | 내용 |
|---|---|
| 이름·기호 | 꽉 찬 상자 손실 · Γ⁻ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 ℓ≥1, x:=ℓ+1에 대해 Γ⁻ₙ,ℓ := Ŵₙ(x;x−1) − Aₙ,ℓ₋₁. |
| 잘 정의됨 | 해당 없음. 정본의 톱니 상승량 𝔯ₙ,ₖ·제한 문턱 폭 표시 합 𝔥ₙ,q와 비슷한 역할(증가분과 꺾임 손실의 분리)을 하지만, 이산 문턱에서 정의한 다른 대상이며 정확한 관계는 확인하지 않았다. |
| Lean 대응 | 미형식화 |
| 이번 보완 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md의 원 전단사·숲 가중합·골격 분해는 검토 k34fb712e85cd44ec8192ca96eb115da1에서 비형식 supported다. lean/SkeletonAlgebra.lean의 skeletonEval/gammaPlus/gammaMinus는 재귀 평가기의 구현이며 원 A·b와의 대수 연결만 accepted/matches다. 이는 그 선행 기록 당시의 범위다. 현재 자연수 제한의 일반 식별은 아래 k1b4bb39af602435783a027a919ef8943의 수용된 형식 대응을 따른다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.canonicalGammaMinus, canonicalGammaMinus_eq. 양수 n,ℓ의 정본 최초 정의를 정수 차로 구현하고 기존 gammaMinus와 식별. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §4.1 |
| 기록별 이명 | |


정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

현재 엄격 양수성 대응: k716f5d11dad24f78a224774000d9f0b0/lean/StrictCorrections.lean의 ParkingCombined.canonicalGammaMinus_pos는 양수 n,ℓ 및 n≥ℓ+1에서 원 Γ⁻ₙ,ℓ>0를 증명한다. 독립 검토 k60bb458604ee4921a8ed08021b1ef90d/original-strict-corrections가 accepted/matches로 수용했다. 전체 행렬식 부호나 원 U는 포함하지 않는다.


## 197. 상반부 형상 함수 · Φ₁(u)

| 칸 | 내용 |
|---|---|
| 이름·기호 | 상반부 형상 함수 · Φ₁(u) |
| 종류 | 함수 |
| 정의 | 실수 1/2<u<1에 대해 Φ₁(u) := (2/√(2π))·(2u−1)/((1−u)√(u(1−u))). |
| 잘 정의됨 | 해당 없음. √n·Aₙ,⌊un⌋/Tₙ→Φ₁(u)는 추측(exploration.md §5.2 추측 A)이며 정의와 별개다. |
| Lean 대응 | 미형식화 |
| 출처 | kb555148741aa4c0687e60906bd144e43/exploration.md §5.2 |
| 기록별 이명 | |

정의 채택: ka372020d7f46458b80d8dfba3f339c14. 위 표의 구현·상대 경로는 기록 kb555148741aa4c0687e60906bd144e43의 공개 파일이다. 탐구는 미검토다. 잘 정의됨 칸에 있는 전단사·가중합·확률 해석은 탐구 저자의 주장이고 이번 정의 채택으로 수용하지 않는다. 정의된 유한 합·함수의 존재와 별개인 항등식은 연구에서 확립해야 한다.

## 198. 일반 가중 재귀 평가기

| 칸 | 내용 |
|---|---|
| 이름·기호 | 일반 가중 재귀 평가기 · Eval_w(n) |
| 종류 | 함수 |
| 정의 | w:ℕ→ℝ≥0, n∈ℕ에서 Eval_w(0):=1, Eval_w(n+1):=Σₖ₌₀ⁿ binom(n,k)w(k+1)Eval_w(k)Eval_w(n−k). |
| 잘 정의됨 | 하위 인수가 모두 n 이하인 강한 자연수 재귀. 감소 숲 가중합과의 동일성은 exposition.md §5의 최대 라벨 분해로 별도 증명한다. |
| Lean 대응 | 자연수 가중치 w:ℕ→ℕ 제한은 lean/SkeletonAlgebra.lean의 ParkingSkeleton.weightedEval. weightedEval_original이 원 A와 동일성을 증명한다. 그 선행 모듈 자체는 평가기 대수이며 현재의 부모 함수 합 동일성은 아래 k1b4bb39af602435783a027a919ef8943 대응을 따른다. |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.parent_forest_sum_eq_weightedEval. 모든 n∈ℕ,w:ℕ→ℕ에서 실제 부모 함수 숲 합=평가기. 영 가중치·빈 숲을 포함하며 실수 가중치 전역은 별도. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md §5 식 (13) |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.

현재 자연수 평가기 보완: k716f5d11dad24f78a224774000d9f0b0/lean/StrictCorrections.lean의 weightedEval_pos, weightedEval_strict는 w:ℕ→ℕ, w(1)>0에서 모든 크기 평가값의 양수성 및 w≤v,1≤s≤n,w(s)<v(s)인 엄격 비교를 증명한다. k60bb458604ee4921a8ed08021b1ef90d/original-strict-corrections에서 accepted/matches. 실수 가중치 전체의 형식화는 아니다.


## 199. 비교 가능한 표시 합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 비교 가능한 표시 합 · Ŵᶜᵐᵖₙ(x;c) |
| 종류 | 함수 |
| 정의 | n∈ℕ, 정수 x≥1, 실수 c≥0에서 Ŵᶜᵐᵖₙ(x;c):=Σ_G Σ_J ∏_{v∈J}(c/t_v(G)−1). G는 [n] 위 번호 제약 없는 뿌리 숲 전부, J는 Sk_x(G)의 부분집합 중 모든 쌍이 조상 관계인 것. 빈 J 포함. |
| 잘 정의됨 | 유한합. 전체 숲의 경로 모양만 합한 것과 다르다. (15),(16)의 별도 평가식과 Tₙ−ℒₙ,ₓ₋₁ 동일성을 본문에서 비형식으로 증명했다. |
| Lean 대응 | 미형식화 |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md §6 식 (14)–(16) |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 200. 맨 위 뿌리 표시 합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 맨 위 뿌리 표시 합 · Pᵗᵒᵖ_s(x;c) |
| 종류 | 함수 |
| 정의 | s≥1, 정수 x≥1, 실수 c≥0에서 Pᵗᵒᵖ_s(x;c):=Σ_H Σ_J ∏_{v∈J}(c/t_v(H)−1). H는 [s] 위 뿌리 있는 나무 전부이고, J⊆Sk_x(H)는 뿌리를 포함하며 모든 쌍이 조상 관계인 집합. s≤x이면 빈 합 0, 구현상 s=0도 0. |
| 잘 정의됨 | 유한합. exposition.md 식 (15)의 재귀는 다음 표시 부분나무의 유일성으로 증명한다. |
| Lean 대응 | 미형식화 |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md §6 |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 201. 비교 불가능 표시 보정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 비교 불가능 표시 보정 · ℬⁱⁿᶜₙ(x;c) |
| 종류 | 함수 |
| 정의 | n∈ℕ, 정수 x≥1, 실수 c≥0에서 ℬⁱⁿᶜₙ(x;c):=Σ_G Σ_J ∏_{v∈J}(c/t_v(G)−1). G는 모든 라벨 뿌리 숲, J⊆Sk_x(G)는 비조상 쌍을 하나 이상 포함하는 집합. |
| 잘 정의됨 | 유한합. Ŵ−Ŵᶜᵐᵖ와 같음은 가중 숲 법칙과 표시 전개로 증명한다. 모든 c에서 비음수인 함수라고 정의하지 않는다. |
| Lean 대응 | 미형식화 |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: evenBranch_grouped, oddBranch_grouped: 두 경계 대입값만. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/exposition.md §6–7 식 (14),(17),(19) |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 202. 전체 급수 원시함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 전체 급수 원시함수 · 𝒰ᵗᵒᵗ(z) |
| 종류 | 함수 |
| 정의 | 𝒰ᵗᵒᵗ(z):=Σ_{s≥1}T_{s−1}z^s/s!∈ℚ[[z]]. |
| 잘 정의됨 | 상수항 0인 Ψ의 형식 원시함수. τ−τ²/2와의 동일성을 sign-research.md §1에서 증명한다. 정본 보정 원시함수 Wℓ와 다르다. |
| Lean 대응 | 미형식화 |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: totalPrimitive, coeff_totalPrimitive_succ. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/sign-research.md §1 |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 203. 지수 원천 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 지수 원천 계수 · zˢʳᶜ_q,k,j |
| 종류 | 함수 |
| 정의 | 정수 q≥2,k≥1,j≥0에서 zˢʳᶜ_q,k,j:=(1−k)(q+1)^j+2kq^j−(1+k)(q−1)^j∈ℤ. |
| 잘 정의됨 | 정수식. |
| Lean 대응 | 별도 def는 없으며 lean/SkeletonAlgebra.lean의 signed_source_four_negative가 q=13+u,k=q−4,j=4 대입의 일반 음수성을 증명한다. 원 급수 계수와의 식별은 미형식화. |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/sign-research.md §2 |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 204. 반복 원시함수 커널

| 칸 | 내용 |
|---|---|
| 이름·기호 | 반복 원시함수 커널 · I_r,j(z) |
| 종류 | 함수 |
| 정의 | r,j∈ℕ에서 I_r,0(z):=z^(r+1)/(r+1)!, I_r,j+1(z):=∫₀ᶻΨ(t)I_r,j(t)dt∈ℚ[[z]]. 적분은 상수항 0인 형식 원시함수. |
| 잘 정의됨 | j에 대한 재귀. 지수계수는 정수이며 초기 계수와 정수 이항 합·적분 재귀로 확인한다. |
| Lean 대응 | 미형식화 |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: iteratedKernel, egfCoeff_iteratedKernel. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/sign-research.md §3 |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 205. 원천 지수 층

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원천 지수 층 · Ξˢʳᶜₙ,q,j |
| 종류 | 함수 |
| 정의 | n,j∈ℕ,q≥2에서 Ξˢʳᶜₙ,q,j:=n![zⁿ]Ψ(z)(−T_{q−1}(q−1)^jI_{q−1,j}(z)+Σ_{r≥q}T_r zˢʳᶜ_q,r+1−q,j I_r,j(z)). |
| 잘 정의됨 | 각 차수에 유한 개 항만 기여한다. 정본 선형 전개 층 𝔙와 다른 함수다. |
| Lean 대응 | 미형식화 |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/sign-research.md §3 식 (32) |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 206. 짝지은 4차 하계 분자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 짝지은 4차 하계 분자 · 𝔅ᵖᵃⁱʳₙ,q |
| 종류 | 함수 |
| 정의 | n∈ℕ,q≥2에서 𝔅ᵖᵃⁱʳₙ,q:=−q³(𝔱≥ₙ,q,1−𝔱>ₙ,q,1)+q²(𝔱>ₙ,q,2+𝔱≥ₙ,q,2)+q(𝔱>ₙ,q,3−𝔱≥ₙ,q,3)+2𝔱>ₙ,q,4. |
| 잘 정의됨 | 기존 제한 이항 폭 모멘트의 정수 결합. q⁴Δ≥𝔅ᵖᵃⁱʳ은 n≥1,n≤2q+1에만 증명하며 분자의 전칭 비음수성은 주장하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | k526e621123a64cee8d48c8b3c7c79a04/sign-research.md §4 식 (34) |
| 기록별 이명 | |

이 기록의 일반 전단사·분기· 하계는 k34fb712e85cd44ec8192ca96eb115da1의 비형식 supported 범위다. 위 Lean 대응은 평가기 대수 범위만 포함하며 전칭 부호는 미해결이다.


## 207. 조건별 변위 제한 실행 기록

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건별 변위 제한 실행 기록 · Trᵖₙ,ℓ |
| 종류 | 대상 |
| 정의 | n,ℓ∈ℕ, p:[n]×ℕ→Prop에 대해 Trᵖₙ,ℓ := {x=(a,s)∈Trₙ,ℓ : ∀i∈[n], p(i,sᵢ−aᵢ)}. Trₙ,ℓ는 기존 변위 제한 실행 기록이다. |
| 잘 정의됨 | 유한 집합의 부분집합이다. p에 추가 가정을 두지 않으며 원 PF와의 연결은 profileOriginalEquiv/profile_card_original_nat에서 증명한다. |
| Lean 대응 | Profile.lean `ProfileTrace n l p`. `td`는 기존 기록의 자리−선호 차를 쓰는 보조 약칭이며 원 기록에서 원 displacement와 같다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §2 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 208. 조건별 제한 분해 자료

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건별 제한 분해 자료 · Ξᵖₙ,ℓ |
| 종류 | 대상 |
| 정의 | n,ℓ∈ℕ,p:[n+1]×ℕ→Prop에서 Ξᵖₙ,ℓ := ⨿(I⊆[n]) {t∈ℕ : t≤min(|I|,ℓ), p(n+1,t)} × Tr^{p∘(ι_I,id)}_{|I|,ℓ} × Tr^{p∘(ι_{Iᶜ},id)}_{n−|I|,ℓ}. 자식의 조건은 각각 (i,d)↦p(ι_I(i),d), (i,d)↦p(ι_{Iᶜ}(i),d)다. |
| 잘 정의됨 | 유한 서로소 합·곱이며, 원 도착 번호 표준화 ι는 기존 정본 §45를 사용한다. |
| Lean 대응 | Profile.lean `ProfilePieces n l p` |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §2 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 209. 조건별 마지막 차량 조립 대응

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건별 마지막 차량 조립 대응 · Ψᵖₙ,ℓ |
| 종류 | 함수 |
| 정의 | n,ℓ∈ℕ,p:[n+1]×ℕ→Prop에서 Ψᵖₙ,ℓ:Ξᵖₙ,ℓ→Trᵖₙ₊₁,ℓ는 기존 마지막 차량 역조립 assemble의 제한이다. 원 번호에서 왼쪽 자식을 ι_I에 끼워 넣고, 오른쪽 자식의 선호·자리에 |I|+1을 더하여 ι_{Iᶜ}에 끼워 넣고, 마지막 자리 |I|+1과 선호 |I|+1−t를 붙인다. |
| 잘 정의됨 | profile_assemble_iff가 p 제한을 보존한다. profileEquiv가 단사·전사와 역함수 extract의 제한을 증명한다. 기존 원 assemble의 성공·실행 유일성·양방향 역을 사용한다. |
| Lean 대응 | Profile.lean `profileEquiv n l p`의 순방향 |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §2 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 210. 문턱 앞 선택 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 문턱 앞 선택 수 · cutCount(I,j) |
| 종류 | 함수 |
| 정의 | n∈ℕ, I⊆[n],0≤j≤n에서 cutCount(I,j) := #{i∈I:i≤j}. |
| 잘 정의됨 | 유한 부분집합의 개수다. |
| Lean 대응 | Cut.lean `cutCount I j`; 내부 번호 i.val<j를 센다. 코드의 j>n 보조 확장은 |I|이며 수학 정의역을 바꾸지 않는다. index_cut, cutCount_compl이 증가 열거와 보완집합의 관계를 증명한다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §3 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 211. 혼합 분해 유효 첨자집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 혼합 분해 유효 첨자집합 · 𝔙ᵐⁱˣₕ,ₖ |
| 종류 | 대상 |
| 정의 | h,k∈ℕ에서 𝔙ᵐⁱˣₕ,ₖ := {(r,a)∈ℕ²:a≤h, a≤r, r−a≤k}. 동치로 {(a+c,a):0≤a≤h,0≤c≤k}다. |
| 잘 정의됨 | r≤h+k이므로 유한하다. 두 표현의 동치는 validSplits_iff에서 증명한다. validSplits_indices가 a≤r 및 h−a≤h+k−r를 증명하여 두 자식의 혼합 첨자가 유효함을 확인한다. |
| Lean 대응 | MixedRecurrence.lean `validSplits h k` |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §3 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 212. 이항 이변수 합성

| 칸 | 내용 |
|---|---|
| 이름·기호 | 이항 이변수 합성 · f⋆g |
| 종류 | 함수 |
| 정의 | f,g:ℕ²→ℤ와 h,k∈ℕ에서 (f⋆g)(h,k) := Σₐ₌₀ʰΣ𝚌₌₀ᵏ binom(h,a)binom(k,c) f(a,c)g(h−a,k−c). |
| 잘 정의됨 | 유한 정수 합이다. |
| Lean 대응 | Convolution.lean `conv f g h k`; conv_comm이 교환성을 증명한다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §4 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 213. 배열 이동·차 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 배열 이동·차 연산 · (Dₓᵃʳʳ,Dᵧᵃʳʳ,𝒟ᵃʳʳ) |
| 종류 | 함수 |
| 정의 | f:ℕ²→ℤ에 대해 Dₓᵃʳʳf(h,k):=f(h+1,k), Dᵧᵃʳʳf(h,k):=f(h,k+1), 𝒟ᵃʳʳf(h,k):=Dₓᵃʳʳf(h,k)−Dᵧᵃʳʳf(h,k). |
| 잘 정의됨 | 자연수 첨자의 대입과 정수 차다. |
| Lean 대응 | Convolution.lean `dx`, `dy`, `dd`. conv_dx,conv_dy,conv_dd가 합성의 이동식·곱 법칙을 증명한다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §4 |
| 기록별 이명 | 기록 ke2436447b98547689b08023d2935b621의 (Dₓ,Dᵧ,𝒟). §64의 총 변위 𝒟(α)와 다른 대상이므로 위첨자를 붙여 개명했다. |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 214. 도착 커널 증가량

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 커널 증가량 · δHₘ,ⱼ,ℓ |
| 종류 | 함수 |
| 정의 | m,ℓ∈ℕ,0≤j≤m에서 δHₘ,ⱼ,ℓ := Hᵃʳʳₘ,ⱼ,ℓ₊₁−Hᵃʳʳₘ,ⱼ,ℓ∈ℤ. |
| 잘 정의됨 | 기존 원 도착 전달 커널 두 값의 정수 차다. |
| Lean 대응 | Bounds.lean `kernelGain l m j`. kernelGain_lower는 δH≥Bᵐⁱˣ를 증명한다. 코드의 j>m은 기존 커널의 보조 확장에 따른 값이다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §5 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.


## 215. 도착 전달 잔여

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도착 전달 잔여 · Rᵃʳʳₕ,ᵣ,ℓ |
| 종류 | 함수 |
| 정의 | h,r∈ℕ,ℓ≥1에서 Rᵃʳʳₕ,ᵣ,ℓ := Jₕ,ᵣ,ℓ−Z¹ₕ,ᵣ,ℓ∈ℤ. |
| 잘 정의됨 | 기존 정본 J와 Z¹ 두 정수의 차다. |
| Lean 대응 | Residual.lean `Remainder l h r`; remainder_recurrence, remainder_nonnegative, remainder_row_exact가 원 강제 전달·비음수성·행 합을 증명한다. |
| 출처 | ke2436447b98547689b08023d2935b621/exposition.md §6 |
| 기록별 이명 | |

정의 채택과 수학적 수용을 구별한다. ke2436447b98547689b08023d2935b621의 해당 일반 원 정리는 검토 kd5aa5110d39449359578cdc2287a86a9에서 accepted/matches다. 전칭 하계 부호·P의 형식 증명은 아니다.

이하 새 항목에서 f_r는 기존 전체 개수 T_r를 r!로 나눈 값의 약자다. 독립적인 새 이름으로 채택하지 않는다.

## 216. 대칭 폭 원천

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대칭 폭 원천 · \(\mathcal E^{\rm wid}_q(z)\) |
| 종류 | 함수 |
| 정의 | q≥2에서 \(\mathcal E^{\rm wid}_q(z):=\sum_{r=q}^{2q}(f_r-\sum_{j=q}^{r-1}f_jf_{r-1-j})z^r\in\mathbb Q[z]\). |
| 잘 정의됨 | 유한 합. 출처 기록 exposition.md (7)이 양수 계수 분해를 준다. |
| Lean 대응 | 미형식화. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: widSourceSeries, sourceSeries_widSource, widSource_split, widSource_pos. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §3, (6). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 217. 대칭 폭 원천의 전체 항

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대칭 폭 원천의 전체 항 · \(\mathcal E^{\rm wid,0}_q(z)\) |
| 종류 | 함수 |
| 정의 | q≥2에서 \(\mathcal E^{\rm wid,0}_q(z):=\sum_{r=q}^{2q}f_rz^r/(r+1)\). |
| 잘 정의됨 | 유한 합, r+1>0. |
| Lean 대응 | 미형식화. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: widSource_split의 첫 항. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §3, (8). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 218. 대칭 폭 원천의 가운데 항

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대칭 폭 원천의 가운데 항 · \(\mathcal E^{\rm wid,mid}_q(z)\) |
| 종류 | 함수 |
| 정의 | q≥2에서 \(\mathcal E^{\rm wid,mid}_q(z):=\tfrac12\sum_{r=q}^{2q}\sum_{j=r-q}^{q-1}f_jf_{r-1-j}z^r\). r=2q의 안쪽 합은 빈 합이다. |
| 잘 정의됨 | 유한 합. |
| Lean 대응 | 미형식화. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: widSource_split의 가운데 항. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §3, (8). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 219. 폭 원천 전이 응답

| 칸 | 내용 |
|---|---|
| 이름·기호 | 폭 원천 전이 응답 · \(\mathscr H^{\rm wid}_{q,j}[S](z)\) |
| 종류 | 함수 |
| 정의 | 정수 q≥1,j≥0,S∈ℚ[[z]]에서 \(\mathscr H^{\rm wid}_{q,j}[S](z):=\Psi(z)\int_0^z S(t)\exp(q(\mathcal U^{\rm tot}(z)-\mathcal U^{\rm tot}(t)))(\mathcal U^{\rm tot}(z)-\mathcal U^{\rm tot}(t))^j/j!\,dt\). |
| 잘 정의됨 | 각 z 차수에서 유한한 다항식 적분. 출처 기록 exposition.md (11)의 삼각 재귀와도 일치한다. |
| Lean 대응 | 미형식화. 원 공통 강제 전달자 𝒱q나 제한 표시 응답 커널과 다른 대상이다. |
| Lean 추가 대응 | k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 ParkingWidth.widResponse c S n은 정수 EGF 원천 S의 j=0 응답 계수 재귀 구현이다. 선형성·국소성·최초 계수·고정 n 단조성과 excessSource 대입의 원 ℒ 연결은 k0d67ab01617a4814aae5265ebb219b1a에서 accepted/matches. 적분 정의와 재귀의 일반 동일성은 비형식이다. c=0은 구현의 보조 확장이며 정본 정의역 c≥1을 바꾸지 않는다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: widResponse_expansion, responseSeries_ode, response_tail_integration. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §4, (10). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 220. 폭 원천 4차 이득 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 폭 원천 4차 이득 함수 · \(\mathcal G^{\rm wid}_q[S]\) |
| 종류 | 함수 |
| 정의 | 정수 q≥2,S∈ℚ[[z]]에서 \(\mathcal G^{\rm wid}_q[S]:=2\mathscr H^{\rm wid}_{q,1}[S]+2q\mathscr H^{\rm wid}_{q,2}[S]+2\mathscr H^{\rm wid}_{q,3}[S]+2q\mathscr H^{\rm wid}_{q,4}[S]\). |
| 잘 정의됨 | 앞 응답의 유한 선형 결합. |
| Lean 대응 | 미형식화. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §5, (18). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 221. 대칭 폭 원천의 끝띠 하계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대칭 폭 원천의 끝띠 하계 · \(\mathcal E^{\rm wid,[m]}_q(z)\) |
| 종류 | 함수 |
| 정의 | 정수 q≥2,m≥0에서 \(\mathcal E^{\rm wid,[m]}_q(z):=\mathcal E^{\rm wid,0}_q(z)+\tfrac12\sum_{r=q}^{2q}\sum_{\{j:r-q\le j\le q-1,\;j-(r-q)<m\;\lor\;q-1-j<m\}}f_jf_{r-1-j}z^r\). 합의 첨자는 집합이므로 겹치는 항은 한 번만 센다. |
| 잘 정의됨 | 유한 합. |
| Lean 대응 | 미형식화. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §6, (22). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.

## 222. 끝띠 폭 비교값

| 칸 | 내용 |
|---|---|
| 이름·기호 | 끝띠 폭 비교값 · \(\mathfrak C^{\rm wid}_{n,q,m}\) |
| 종류 | 함수 |
| 정의 | 정수 q≥2,1≤n≤2q+1,m≥0에서 \(\mathfrak C^{\rm wid}_{n,q,m}:=n![z^n](\mathcal G^{\rm wid}_q[\mathcal E^{\rm wid,[m]}_q]-\mathscr H^{\rm wid}_{q,0}[f_{q-1}z^{q-1}]+\mathscr H^{\rm wid}_{q,1}[f_{q-1}z^{q-1}]-\mathscr H^{\rm wid}_{q,2}[f_{q-1}z^{q-1}])+\mathcal B^{\rm inc}_n(q-1;q-1)\). |
| 잘 정의됨 | 형식급수의 유리 계수와 기존 유한 숲 합. |
| Lean 대응 | 미형식화. 원 분자 𝔅ᵖᵃⁱʳ와는 m에 의존하는 다른 하계이며 m≥ceil(q/2)에서만 𝔅ᵖᵃⁱʳ/q⁴와 같다. |
| 출처 | kcee4fdfe71574e5ab1b3a1c16c325818/exposition.md §6, (24). |
| 기록별 이명 | 없음 |

정의 채택: kd1e1bd3b4eef437f833afc4d0f9b1e9d. 일반 비교의 현재 수용은 k71703e1d7aa843708536575e297d4f33의 비형식 supported 범위이며 일반 Lean 연결은 없다.


## 223. 폭 전이의 매개변수 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 폭 전이의 매개변수 계수 · \(\kappa^{\rm wid}_{n,r,a}\) |
| 종류 | 함수 |
| 정의 | \(n,r,a\in\mathbb N\)에서 \(\kappa^{\rm wid}_{n,r,a}:=n![z^n]\Psi(z)\int_0^z(t^r/r!)(\mathcal U^{\rm tot}(z)-\mathcal U^{\rm tot}(t))^a/a!\,dt\). |
| 잘 정의됨 | 고정 차수에서 유한한 형식 적분. 출처 exposition.md (7)의 유한 조성 합과 반복 원시함수 커널의 정수 EGF 재귀로 비음수 정수임을 비형식 증명했다. \(n<r+a+1\)이면 0이다. |
| Lean 대응 | 미형식화. k4ae9589f84b84e11861e1ef456c2e3b5/lean/WidthResponse.lean의 widResponse_leading은 응답 재귀의 최초 계수만 다루며 이 함수 전체의 식별 정리가 아니다. |
| 수용된 구현 대응 | k41df00b303bc4da78d9d610e8bcf85ae: widKappa, widKappaNat, widKappa_eq_nat, widKappa_integer. 실제 선언별 대응은 그 기록 formal-verification.md. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b에서 관련 네 일반 형식 결과 accepted/matches로 수용했다. j=0 응답·두 경계 등 명시된 범위만 뜻한다. 기존 정의·영역을 바꾸지 않는다. |
| 출처 | k4ae9589f84b84e11861e1ef456c2e3b5/exposition.md §3 (6),(7), glossary-proposals.md §1. 검토 k0d67ab01617a4814aae5265ebb219b1a에서 비형식 supported/conforms. |
| 기록별 이명 | 없음 |

기존 §204의 z-급수 커널과 달리 세 자연수의 정수값 함수다. §35 점근 계수와 장식·영역·뜻이 다르다. 정의 채택은 일반 Lean 식별의 수용이 아니다.

## 224. 정확 손실 정규화 폭 비교비

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정확 손실 정규화 폭 비교비 · \(\rho^{\rm wid}_{q,\varepsilon}\) |
| 종류 | 함수 |
| 정의 | 정수 \(q\ge2,\varepsilon\in\{0,1\},n=2q+\varepsilon\)에서 \(\rho^{\rm wid}_{q,\varepsilon}:=(n![z^n]\mathcal G^{\rm wid}_q[\mathcal E^{\rm wid}_q]+\mathcal B^{\rm inc}_n(q-1;q-1))/(n![z^n]\mathscr H^{\rm wid}_{q-1,0}[f_{q-1}z^{q-1}])\). |
| 잘 정의됨 | 분모는 출처 exposition.md (11)의 양수 유한 합이다. |
| Lean 대응 | 미형식화. |
| 출처 | k4ae9589f84b84e11861e1ef456c2e3b5/exposition.md §5.2 (20), glossary-proposals.md §2. 검토 k0d67ab01617a4814aae5265ebb219b1a에서 비형식 supported/conforms. |
| 기록별 이명 | 없음 |

분기 보정이 분자에 들어 있다. 기존 §34의 양의 단순극 위치와 다른 함수다. q에 대한 비감소성은 두 경계 모두 q=64→65에서 실패한다. 이 실패는 비 자체가 1 미만이라는 뜻이 아니다.

## 225. 골격 크기

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 크기 · a_x(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, 실수 x≥0에서 a_x(G):=\|Sk_x(G)\|=#{v∈[n]: t_v(G)>x}. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 자연수 q≥2인 실제 감소 부모 함수의 구현은 k7a6fb5f6105e475dab570454a8d5ef85/lean/MarkedComponents.lean의 ParkingForest.largeCount다. kdaa41390eadc4ac381e275adac86f547에서 accepted/matches. 정의의 실수 문턱·일반 숲 전체 구현이나 조건부 법칙 전체 인증으로 확대하지 않는다. |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3 |
| 기록별 이명 | |

정의 채택 당시에는 탐구의 정의만 관리했다. 관련 항등식의 현재 수용 범위는 아래 보완을 따르며 전칭 단조성을 수용하지 않는다.


현재 비형식 수용 보완: k2874758a73b749c0b8af17fcc1be6660의 conditional-size-chain-and-transport는 kcc189037a61c4faea0745b876c66fffe에서 supported다. 정수 x≥2,2x>n의 원 가중 법칙·a_x≤n−x·e_x≤1·기울임 및 정규화 기대값/이동식의 명시 범위만 수용한다. 정의의 일반 영역과 실제 전칭 부호·단조성의 미해결은 보존한다. 조건부 확률 법칙 전체의 Lean 인증은 없다.

현재 형식 수용 보완: k9a3297b965b24ea7a87eb1a666b8cd1a/lean/InteriorLower.lean의 three_cap_hit_bounds, interior_hit_bounds는 실제 포장에서 n<3q의 e≤2, q≥4,n≤2q+3의 e≤2 및 e=2⇒a≤n−2q를 증명한다. 검토 kc0a4185b9ecf4d70b84ed75e8e3caf67/general-finite-loss-and-interior-two-hit-lower에서 supported/accepted/matches/conforms다. 기존 정의·정의역은 보존한다.


## 226. 문턱 꼭짓점 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 문턱 꼭짓점 수 · e_x(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, 정수 x≥1에서 e_x(G):=#{v∈[n]: t_v(G)=x}. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 자연수 q≥2인 실제 감소 부모 함수의 구현은 k7a6fb5f6105e475dab570454a8d5ef85/lean/MarkedComponents.lean의 ParkingForest.hitCount다. kdaa41390eadc4ac381e275adac86f547에서 accepted/matches. 정의의 더 넓은 영역은 보존한다. |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3 |
| 기록별 이명 | |

정의 채택 당시에는 탐구의 정의만 관리했다. 관련 항등식의 현재 수용 범위는 아래 보완을 따르며 전칭 단조성을 수용하지 않는다.


현재 비형식 수용 보완: k2874758a73b749c0b8af17fcc1be6660의 conditional-size-chain-and-transport는 kcc189037a61c4faea0745b876c66fffe에서 supported다. 정수 x≥2,2x>n의 원 가중 법칙·a_x≤n−x·e_x≤1·기울임 및 정규화 기대값/이동식의 명시 범위만 수용한다. 정의의 일반 영역과 실제 전칭 부호·단조성의 미해결은 보존한다. 조건부 확률 법칙 전체의 Lean 인증은 없다.

현재 형식 수용 보완: k9a3297b965b24ea7a87eb1a666b8cd1a/lean/InteriorLower.lean의 three_cap_hit_bounds, interior_hit_bounds는 명시된 범위의 실제 e≤2와 e=2일 때의 a 제한을 증명한다. 검토 kc0a4185b9ecf4d70b84ed75e8e3caf67/general-finite-loss-and-interior-two-hit-lower에서 supported/accepted/matches/conforms다. 기존 정의·정의역은 보존한다.


## 227. 골격 잎 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 잎 수 · λ_x(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, [n] 위 뿌리 있는 숲 G, 실수 x≥0에서 λ_x(G):=#{v∈Sk_x(G): p_G(w)=v이고 t_w(G)>x인 w∈[n]이 없다}. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §8 |
| 기록별 이명 | |

탐구가 제안한 정의만 채택했다. 원 PF와의 법칙 동일성·새 항등식·관측·단조성의 수학적 수용은 추가하지 않는다.


현재 형식 수용 보완: k0c2f8df2c56e4828bbf691cacca83b2a/lean/BoundaryForest.lean의 canonicalLeafCount는 자연수 문턱의 λ 구현이며 kfaeb6535dad54592857b1f726417d954에서 accepted/matches다. canonicalLeafCount_le_one 및 canonicalLeafCount_zero_iff는 명시된 n≤2q+1 영역과 빈 골격 조건을 다룬다. 실수 문턱 전체 구현으로 확대하지 않는다.

## 228. 조건부 도착 숲 법칙

| 칸 | 내용 |
|---|---|
| 이름·기호 | 조건부 도착 숲 법칙 · ζ_{n,y} |
| 종류 | 대상 |
| 정의 | n≥1, 실수 y>0에서 ζ_{n,y}는 𝔉↓ₙ 위의 확률측도로, ζ_{n,y}(G):=∏_{v∈[n]}min(t_v(G),y) / Σ_{G'∈𝔉↓ₙ}∏_{v∈[n]}min(t_v(G'),y). |
| 잘 정의됨 | y>0이면 모든 인수가 양수라 분모가 양수다. |
| Lean 대응 | 미형식화 |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §4.1 |
| 기록별 이명 | |

정의 채택 당시에는 탐구의 정의만 관리했다. 관련 항등식의 현재 수용 범위는 아래 보완을 따르며 전칭 단조성을 수용하지 않는다.


현재 비형식 수용 보완: k2874758a73b749c0b8af17fcc1be6660의 conditional-size-chain-and-transport는 kcc189037a61c4faea0745b876c66fffe에서 supported다. 정수 x≥2,2x>n의 원 가중 법칙·a_x≤n−x·e_x≤1·기울임 및 정규화 기대값/이동식의 명시 범위만 수용한다. 정의의 일반 영역과 실제 전칭 부호·단조성의 미해결은 보존한다. 조건부 확률 법칙 전체의 Lean 인증은 없다.

## 229. Gibbs 성분 가중

| 칸 | 내용 |
|---|---|
| 이름·기호 | Gibbs 성분 가중 · 𝔴_x(s) |
| 종류 | 함수 |
| 정의 | 정수 x≥1, s≥1에서 𝔴_x(s):=min(s,x)·A_{s−1,x−1}/s!. A_{0,x−1}=1을 쓴다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §4.2 |
| 기록별 이명 | |

탐구가 제안한 정의만 채택했다. 원 PF와의 법칙 동일성·새 항등식·관측·단조성의 수학적 수용은 추가하지 않는다.

## 230. 골격 잎 수별 차분 기여

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 잎 수별 차분 기여 · D⁽ᵏ⁾ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 ℓ≥1, k∈ℕ, x:=ℓ+1에서 D⁽ᵏ⁾ₙ,ℓ:=Σ_{G∈𝔉↓ₙ, λ_x(G)=k}[∏_v min(t_v(G),ℓ+2)−2∏_v min(t_v(G),ℓ+1)+∏_v min(t_v(G),ℓ)]. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §8 |
| 기록별 이명 | |

탐구가 제안한 정의만 채택했다. 원 PF와의 법칙 동일성·새 항등식·관측·단조성의 수학적 수용은 추가하지 않는다.


현재 형식 수용 보완: k0c2f8df2c56e4828bbf691cacca83b2a/lean/BoundaryForest.lean의 canonicalClassContribution은 양수 n,ℓ의 실제 원 D 구현이며 kfaeb6535dad54592857b1f726417d954에서 accepted/matches다. original_delta_empty_path의 n≤2(ℓ+1)+1 합 분해는 부호를 가정하지 않는 등식이다. 성분 사슬 합의 일반 Lean 및 전칭 부호는 남는다.

## 231. 정규화 이득

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정규화 이득 · 𝔤⁺ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 ℓ≥1에서 𝔤⁺ₙ,ℓ:=(ℓ+1)²·Γ⁺ₙ,ℓ/Aₙ,ℓ. |
| 잘 정의됨 | Aₙ,ℓ≥1이므로 분모가 양수다. |
| Lean 대응 | 미형식화 |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.normalizedGain, normalizedGain_eq. n,ℓ≥1에서 정수 Γ의 유리수 포함으로 정의된 정규화 이득. 실제 단조성은 미증명. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §6.3 |
| 기록별 이명 | |

정의 채택 당시에는 탐구의 정의만 관리했다. 관련 항등식의 현재 수용 범위는 아래 보완을 따르며 전칭 단조성을 수용하지 않는다.


현재 비형식 수용 보완: k2874758a73b749c0b8af17fcc1be6660의 conditional-size-chain-and-transport는 kcc189037a61c4faea0745b876c66fffe에서 supported다. 정수 x≥2,2x>n의 원 가중 법칙·a_x≤n−x·e_x≤1·기울임 및 정규화 기대값/이동식의 명시 범위만 수용한다. 정의의 일반 영역과 실제 전칭 부호·단조성의 미해결은 보존한다. 조건부 확률 법칙 전체의 Lean 인증은 없다.

## 232. 정규화 손실

| 칸 | 내용 |
|---|---|
| 이름·기호 | 정규화 손실 · 𝔤⁻ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 정수 ℓ≥1에서 𝔤⁻ₙ,ℓ:=(ℓ+1)²·Γ⁻ₙ,ℓ/Aₙ,ℓ. |
| 잘 정의됨 | Aₙ,ℓ≥1이므로 분모가 양수다. |
| Lean 대응 | 미형식화 |
| 현재 형식 대응 | k1b4bb39af602435783a027a919ef8943/lean/CanonicalForest.lean 및 lean/GainLoss.lean의 ParkingForest.normalizedLoss, normalizedLoss_eq. n,ℓ≥1에서 정수 Γ의 유리수 포함으로 정의된 정규화 손실. 실제 단조성은 미증명. k93022a6f4bf2430ba692974597fa8f1e에서 관련 결과 accepted/matches. |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §6.3 |
| 기록별 이명 | |

정의 채택 당시에는 탐구의 정의만 관리했다. 관련 항등식의 현재 수용 범위는 아래 보완을 따르며 전칭 단조성을 수용하지 않는다.


현재 비형식 수용 보완: k2874758a73b749c0b8af17fcc1be6660의 conditional-size-chain-and-transport는 kcc189037a61c4faea0745b876c66fffe에서 supported다. 정수 x≥2,2x>n의 원 가중 법칙·a_x≤n−x·e_x≤1·기울임 및 정규화 기대값/이동식의 명시 범위만 수용한다. 정의의 일반 영역과 실제 전칭 부호·단조성의 미해결은 보존한다. 조건부 확률 법칙 전체의 Lean 인증은 없다.

## 233. 부분나무 크기 묶음별 정확 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 부분나무 크기 묶음별 정확 개수 · b^{[𝔰]}ₙ,ℓ |
| 종류 | 함수 |
| 정의 | n≥1, 원소 수 n인 양의 정수 중복집합 𝔰, 정수 ℓ≥0에서 PFₙ[𝔰]:={α∈PFₙ: 중복집합 {t_v(G_α): v∈[n]}=𝔰}, b^{[𝔰]}ₙ,ℓ:=#{α∈PFₙ[𝔰]: M(α)=ℓ}. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | ka1c3633303ca4d7fb91d8a309579022b/exploration.md §3, §7 |
| 기록별 이명 | |

탐구가 제안한 정의만 채택했다. 원 PF와의 법칙 동일성·새 항등식·관측·단조성의 수학적 수용은 추가하지 않는다.

## 234. 단항 원천 응답 매개변수 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 단항 원천 응답 매개변수 다항식 · Πʷⁱᵈ,ᵖᵃʳₙ,ᵣ(X) |
| 종류 | 함수 |
| 정의 | n,r∈ℕ에서 Π₀,ᵣ(X):=0, Πₙ₊₁,ᵣ(X):=Σₖ₌₀ⁿ binom(n,k){(X+k+1)TₖΠₙ₋ₖ,ᵣ(X)+[k=r]Tₙ₋ₖ}∈ℚ[X]. |
| 잘 정의됨 | 크기 n에 대한 삼각 재귀. |
| Lean 대응 | `ParkingWidth.atomResponsePolynomial r n`; `atomResponsePolynomial_coeff`가 Xᵃ 계수=κʷⁱᵈₙ,ᵣ,ₐ, `atomResponsePolynomial_eval`이 자연수 c 대입=widResponse(c,[k=r],n)를 증명한다. |
| 출처 | k41df00b303bc4da78d9d610e8bcf85ae/exposition.md §2 및 lean/ResponseExpansion.lean. |
| 기록별 이명 | |

정의는 원 해설에서 채택했다. 이 연구의 네 형식 결과는 k1f431a6ad115453aaebaecc30aa9445b에서 accepted/matches로 수용됐으며 전칭 부호는 별도다.

## 235. 절단 전 대칭 폭 원천

| 칸 | 내용 |
|---|---|
| 이름·기호 | 절단 전 대칭 폭 원천 · \(\widetilde{\mathcal E}^{wid}_q\) |
| 종류 | 함수 |
| 정의 | q∈ℕ에서 \(\widetilde{\mathcal E}^{wid}_q(z):=(1-z\Psi(z))\sum_{r\ge q}f_rz^r\in\mathbb Q[[z]]\). |
| 잘 정의됨 | 형식급수의 곱이며 각 계수의 합이 유한하다. |
| Lean 대응 | `sourceSeries (ParkingWidth.fullWidSource q)`; `sourceSeries_fullWidSource`가 위 곱과의 동일성을 증명한다. `tailSource q r=[q≤r]T_r`는 정의 오른쪽 꼬리의 정수 EGF 계수 구현이다. |
| 출처 | k41df00b303bc4da78d9d610e8bcf85ae/exposition.md §4 및 lean/SourceIntegration.lean. |
| 기록별 이명 | |

정의는 원 해설에서 채택했다. 이 연구의 네 형식 결과는 k1f431a6ad115453aaebaecc30aa9445b에서 accepted/matches로 수용됐으며 전칭 부호는 별도다.

## 236. 가중 폭 원천 유한 합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 가중 폭 원천 유한 합 · \(\mathfrak F^{wid}_{n,q}[w]\) |
| 종류 | 함수 |
| 정의 | q≥2, q≤n≤2q+1 및 w:ℕ→ℤ에서 \(\mathfrak F^{wid}_{n,q}[w]:=\sum_{r=q}^{n-2}(r![z^r]\mathcal E^{wid}_q)\sum_{a=1}^{n-r-1}w(a)\kappa^{wid}_{n,r,a}\in\mathbb Q\). 빈 합은 0이다. |
| 잘 정의됨 | 유한 합이며 계승 척도는 명시되어 있다. |
| Lean 대응 | `ParkingWidth.finiteGain w q n`. 구현의 자연수 전체 보조 확장은 이 정본 제안의 수학적 영역 밖 성질을 주장하지 않는다. |
| 출처 | k41df00b303bc4da78d9d610e8bcf85ae/exposition.md §5 및 lean/FiniteSum.lean. |
| 기록별 이명 | |

정의는 원 해설에서 채택했다. 이 연구의 네 형식 결과는 k1f431a6ad115453aaebaecc30aa9445b에서 accepted/matches로 수용됐으며 전칭 부호는 별도다.

## 237. 유한 순서 라벨 감소 숲

| 칸 | 내용 |
|---|---|
| 이름·기호 | 유한 순서 라벨 감소 숲 · 𝔉↓(V) |
| 종류 | 대상 |
| 정의 | 유한 선형 순서집합 V에서 𝔉↓(V):={p:V→Option(V): 모든 u,v∈V에서 p(u)=some(v) ⇒ u<v}. none은 가상 뿌리다. |
| 잘 정의됨 | 유한 함수들의 부분집합. 부모 경로의 가상 뿌리 도달은 terminal_exists와 reaches_virtual_root로 증명된다. V=Fin n은 라벨 값+1과 none↔0을 통해 §80의 숲과 동일시된다. |
| Lean 대응 | k1b4bb39af602435783a027a919ef8943/lean/Forest.lean의 ParkingForest.Forest; lean/CanonicalForest.lean의 parentEquiv. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k1b4bb39af602435783a027a919ef8943/exposition.md §3 및 glossary-proposals.md. 이번 계획에서 채택. |
| 기록별 이명 | |

## 238. 부모 함수 조상 관계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 부모 함수 조상 관계 · Anc_G(u,v) |
| 종류 | 성질·관계 |
| 정의 | 유한 선형 순서집합 V, G∈𝔉↓(V), u,v∈V에서 Anc_G(u,v) :⇔ 관계 p_G(u)=some(v)의 반사·추이 폐포가 u에서 v로 잇는다. 자기 자신을 포함한다. |
| 잘 정의됨 | 표준 관계 폐포. anc_iterate가 가상 뿌리로 확장한 부모의 어떤 k≥0회 반복이 u를 v로 보냄과의 동치를 증명한다. |
| Lean 대응 | k1b4bb39af602435783a027a919ef8943/lean/Forest.lean의 ParkingForest.Anc, anc_iterate. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k1b4bb39af602435783a027a919ef8943/exposition.md §3 및 glossary-proposals.md. 이번 계획에서 채택. |
| 기록별 이명 | |

## 239. 자손 닫힘 성질

| 칸 | 내용 |
|---|---|
| 이름·기호 | 자손 닫힘 성질 · Closed(G,S) |
| 종류 | 성질·관계 |
| 정의 | 유한 선형 순서집합 V, G∈𝔉↓(V), S⊆V에서 Closed(G,S) :⇔ 모든 u,v∈V에서 p_G(u)=some(v) 및 v∈S이면 u∈S이다. |
| 잘 정의됨 | 해당 없음. 부모를 따라가는 방향이 아니라 자손을 취하는 방향이다. closed_anc가 모든 자손에 대한 닫힘을 준다. |
| Lean 대응 | k1b4bb39af602435783a027a919ef8943/lean/Forest.lean의 ParkingForest.Closed, closed_anc, restrict_anc, restrict_size. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k1b4bb39af602435783a027a919ef8943/exposition.md §4 및 glossary-proposals.md. 이번 계획에서 채택. |
| 기록별 이명 | |

## 240. 유한 순서 라벨 감소 숲 가중합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 유한 순서 라벨 감소 숲 가중합 · Total_w(V) |
| 종류 | 함수 |
| 정의 | 유한 선형 순서집합 V, w:ℕ→ℕ에서 Total_w(V):=Σ_{G∈𝔉↓(V)}∏_{v∈V}w(#{u∈V:Anc_G(u,v)}). V가 비면 빈 부모 함수 하나와 빈 곱으로 값은 1이다. |
| 잘 정의됨 | 유한합이다. total_eq_eval이 기존 Eval_w(카디널리티 V)와의 동일성을 별도로 증명한다. 재귀로 합을 정의하지 않는다. |
| Lean 대응 | k1b4bb39af602435783a027a919ef8943/lean/Forest.lean의 ParkingForest.total, weight, size; lean/ForestEvaluation.lean의 total_eq_eval. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k1b4bb39af602435783a027a919ef8943/exposition.md §5 및 glossary-proposals.md. 기존 [n] 숲 합의 임의 순서 라벨 집합 일반화. 이번 계획에서 채택. |
| 기록별 이명 | |

## 241. 최대 라벨 분해 자료

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 라벨 분해 자료 · Parts(V,r) |
| 종류 | 대상 |
| 정의 | 비어 있지 않은 유한 선형 순서집합 V와 그 최댓값 r에서 Parts(V,r):={(S,F,H):S⊆V∖{r}, F∈𝔉↓(S), H∈𝔉↓(V∖(S∪{r}))}. 두 부분은 V의 순서를 물려받는다. |
| 잘 정의됨 | 유한 종속 합. splitEquiv가 실제 부모 함수 감소 숲과의 양방향 전단사를 증명한다. |
| Lean 대응 | k1b4bb39af602435783a027a919ef8943/lean/ForestSplit.lean의 ParkingForest.Parts, splitEquiv; lean/CanonicalForest.lean의 canonicalMaxSplitEquiv. k93022a6f4bf2430ba692974597fa8f1e에서 accepted/matches. |
| 출처 | k1b4bb39af602435783a027a919ef8943/exposition.md §4 및 glossary-proposals.md. 이번 계획에서 채택. |
| 기록별 이명 | |

## 242. 골격·문턱 결합 표시 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격·문턱 결합 표시 다항식 · Z^{ae}_{m,x}(z,v) |
| 종류 | 함수 |
| 정의 | 정수 x≥1,0≤m<2x에서 Z^{ae}_{m,x}(z,v):=Σ_{G∈𝔉↓ₘ}(∏ᵤmin(tᵤ(G),x))z^{a_x(G)}v^{e_x(G)}. z,v는 다항식 변수이며 m=0이면 1이다. |
| 잘 정의됨 | 유한합. 계수는 비음수 정수다. x=1도 정의되지만 원 해설 (7)의 사슬 재귀 사용은 그 문면의 x≥2 제한을 따른다. x≥2,0≤m<2x의 v 차수 1 이하·재귀·조건부 크기 사슬은 kcc189037a61c4faea0745b876c66fffe에서 비형식 supported다. |
| Lean 대응 | 미형식화. chain_polynomials는 계산 구현이다. |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md §1, exposition.md (6),(7). 정의 채택 뒤 conditional-size-chain-and-transport가 위 검토에서 supported. 전체 Lean 연결은 미완료. |
| 기록별 이명 | |

## 243. 적중 축약 경로 인자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 적중 축약 경로 인자 · C^{hit}_d(x) |
| 종류 | 함수 |
| 정의 | 정수 d≥0,실수 x>1에서 C^{hit}_d(x):=E_{F,U}[∏_{v∈U↝0, v≠0}(x−1)/(x+t_v(F))]. F는 [d] 위 번호 제약 없는 뿌리 있는 숲의 균등 법칙, U는 F와 독립인 {0,…,d}의 균등 부착점, U↝0은 부모 경로다. d=0의 빈 곱은 1이다. |
| 잘 정의됨 | 유한 확률공간이고 모든 분모가 양수다. 원 Γ⁻와의 동일성은 추가 영역 n=x+d,정수 x≥2,x>n/2에서 kcc189037a61c4faea0745b876c66fffe가 T3–T5의 비형식 논증을 supported로 수용했다. 일반 Lean 동일성은 없다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/tail-proof.md (T4),(T5) 및 glossary-proposals.md §2. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 244. 균등 부착점 평균 깊이

| 칸 | 내용 |
|---|---|
| 이름·기호 | 균등 부착점 평균 깊이 · μ^{depth}_d |
| 종류 | 함수 |
| 정의 | 정수 d≥0에서 μ^{depth}_d:=E_{F,U}[#{v∈U↝0:v≠0}]. F,U와 경로는 §243 적중 축약 경로 인자의 정의와 같다. |
| 잘 정의됨 | 유한합. d=0이면 0이다. 정확 꼬리합·깊이 상계는 kcc189037a61c4faea0745b876c66fffe에서 T6–T9의 비형식 supported 범위다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/tail-proof.md §3, (T6) 및 glossary-proposals.md §3. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 245. 균등 숲 문턱 표시 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 균등 숲 문턱 표시 수 · H^{tree}_{n,x} |
| 종류 | 함수 |
| 정의 | 정수 n≥1,1≤x≤n에서 H^{tree}_{n,x}:=Σ_G e_x(G). G는 [n] 위 번호 제약 없는 뿌리 있는 숲 전부다. |
| 잘 정의됨 | 유한 정수 합. 닫힌 식 binom(n,x)x^{x−1}(n−x+1)^{n−x}와의 동일성은 kcc189037a61c4faea0745b876c66fffe에서 T3의 비형식 supported로 수용됐다. 정의와 이 동일성은 구별한다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/tail-proof.md (T3) 및 glossary-proposals.md §4. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 246. 균등 숲 순서쌍 표시 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 균등 숲 순서쌍 표시 수 · B^{tree}_{n,x} |
| 종류 | 함수 |
| 정의 | 정수 n≥1,x≥1에서 B^{tree}_{n,x}:=Σ_G a_x(G)(a_x(G)−1). G는 [n] 위 번호 제약 없는 뿌리 있는 숲 전부다. |
| 잘 정의됨 | 유한 정수 합. 조상 사슬 이중합과의 동일성에는 x>n/2가 필요하며 kcc189037a61c4faea0745b876c66fffe에서 T10–T16의 비형식 supported로 수용됐다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/tail-proof.md (T10)–(T12) 및 glossary-proposals.md §5. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 247. Cayley 보조 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | Cayley 보조 계수 · β^C_j |
| 종류 | 함수 |
| 정의 | 정수 j≥1에서 β^C_j:=exp(−j)j^j/j!. |
| 잘 정의됨 | 양의 실수. f_j나 u_n과 다른 대상이다. 계수 부등식은 kcc189037a61c4faea0745b876c66fffe에서 T17–T19의 비형식 supported로 수용됐으며 일반 Lean 인증은 없다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/tail-proof.md (T15),(T17) 및 glossary-proposals.md §6. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 248. 골격 크기별 정규화 이득 값

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 크기별 정규화 이득 값 · φ^{gain}_x(a) |
| 종류 | 함수 |
| 정의 | 정수 x≥2,a≥0에서 φ^{gain}_x(a):=x²[(1+1/x)^a+(1−1/x)^a−2]. |
| 잘 정의됨 | 유한 실수 식. 정수 x≥2,2x>n에서 ζ 기대값이 정규화 이득 𝔤⁺라는 항등식과 인접 이동식은 kcc189037a61c4faea0745b876c66fffe에서 비형식 supported로 수용됐다. 전칭 단조성은 미해결이다. |
| Lean 대응 | 미형식화 |
| 출처 | k2874758a73b749c0b8af17fcc1be6660/exposition.md §7,(12) 및 glossary-proposals.md §7. 이번 계획에서 정의 채택. |
| 기록별 이명 | |

## 249. 자손 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 자손 집합 · Desc_G(v) |
| 종류 | 함수 |
| 정의 | 유한 선형 순서집합 V, G∈𝔉↓(V), v∈V에서 Desc_G(v):={u∈V:Anc_G(u,v)}. [n] 위 정본 부모 함수에는 동일한 자기 자신 포함 조상 조건으로 정의한다. |
| 잘 정의됨 | 유한 집합. cardinality가 t_v인 것은 수용된 size·subtreeSize_encode와 일치한다. |
| Lean 대응 | 기록 k0c2f8df2c56e4828bbf691cacca83b2a의 구현(kfaeb6535dad54592857b1f726417d954에서 accepted/matches): lean/BoundaryForest.lean의 ParkingForest.descendants. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §3. |
| 기록별 이명 | |


현재 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. kfaeb6535dad54592857b1f726417d954가 original-empty-path-decomposition을 accepted/matches로 수용했다. 원 차분 등식 및 명시된 구조 범위이며 전칭 부호나 성분 사슬 합 전체 인증은 아니다.

## 250. 골격 잎 집합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격 잎 집합 · 𝓛_q(G) |
| 종류 | 함수 |
| 정의 | q∈ℕ, 유한 선형 순서집합 V, G∈𝔉↓(V)에서 𝓛_q(G):={v∈V:q<t_v(G) ∧ ∀w∈V, q<t_w(G) ⇒ p_G(w)≠v}. [n] 위 정본 부모 함수에는 같은 식을 사용한다. |
| 잘 정의됨 | 유한 집합. 정본 λ_q(G)는 이 집합의 크기다. λ 자체의 재정의나 다른 이명이 아니다. |
| Lean 대응 | 기록 k0c2f8df2c56e4828bbf691cacca83b2a의 구현(kfaeb6535dad54592857b1f726417d954에서 accepted/matches): skeletonLeaves, canonicalSkeletonLeaves. canonicalLeaves_encode가 두 부모 표현의 식별을 증명한다. canonicalLeafCount는 기존 λ의 자연수 문턱 구현이다. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §3. |
| 기록별 이명 | |


현재 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. kfaeb6535dad54592857b1f726417d954가 original-empty-path-decomposition을 accepted/matches로 수용했다. 원 차분 등식 및 명시된 구조 범위이며 전칭 부호나 성분 사슬 합 전체 인증은 아니다.

## 251. 한 숲의 차분 기여

| 칸 | 내용 |
|---|---|
| 이름·기호 | 한 숲의 차분 기여 · χᶠᵒʳᵉˢᵗ_ℓ(G) |
| 종류 | 함수 |
| 정의 | n≥1,ℓ≥1,G∈𝔉↓ₙ에서 χᶠᵒʳᵉˢᵗ_ℓ(G):=∏_v min(t_v,ℓ+2)−2∏_v min(t_v,ℓ+1)+∏_v min(t_v,ℓ), 차는 ℤ에서 계산한다. |
| 잘 정의됨 | 유한 정수 곱·차. |
| Lean 대응 | 기록 k0c2f8df2c56e4828bbf691cacca83b2a의 구현(kfaeb6535dad54592857b1f726417d954에서 accepted/matches): forestCurvature. 함수는 보조적으로 n=0에도 빈 곱의 정수 차 0을 갖지만 b₀,ℓ를 정의하지 않는다. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §3, 식 (4)의 대괄호. |
| 기록별 이명 | |

정본 §116의 χ_q(π)는 순열 위 함수다. 위 함수는 실제 감소 숲 위 함수이므로 같은 이름·정의역을 덮어쓰지 않는다.


현재 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. kfaeb6535dad54592857b1f726417d954가 original-empty-path-decomposition을 accepted/matches로 수용했다. 원 차분 등식 및 명시된 구조 범위이며 전칭 부호나 성분 사슬 합 전체 인증은 아니다.

현재 형식 수용 보완: k9a3297b965b24ea7a87eb1a666b8cd1a/lean/InteriorLower.lean의 curvature_two_hits_negative는 q≥6,a≤3의 단항식 음수, two_hit_subsum_nonpos는 q≥6,n≤2q+3의 실제 e=2 부분합 비양수를 증명한다. 전체 Δ 부호는 아니다. 검토 kc0a4185b9ecf4d70b84ed75e8e3caf67/general-finite-loss-and-interior-two-hit-lower에서 supported/accepted/matches/conforms다. 기존 정의·정의역은 보존한다.


## 252. 소부분나무 가중 결합 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 소부분나무 가중 결합 계수 · Cᵃᵉₘ,q(a,e) |
| 종류 | 함수 |
| 정의 | m,a,e∈ℕ,q≥2에서 Cᵃᵉₘ,q(a,e):=Σ_{G∈𝔉↓ₘ,a_q(G)=a,e_q(G)=e} ∏_{v:t_v(G)<q}t_v(G). |
| 잘 정의됨 | 유한 자연수 합. 빈 숲의 (a,e)=(0,0) 계수는 1, 나머지는 0이다. |
| Lean 대응 | k7a6fb5f6105e475dab570454a8d5ef85/lean/MarkedComponents.lean의 ParkingForest.smallWeightedCoefficient 및 componentPolynomial_coefficient. 실제 부모 함수 C 계수와 F 계수의 동일성은 kdaa41390eadc4ac381e275adac86f547에서 accepted/matches. 성분 분할 재귀 전체 Lean은 별도다. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §5 (13). |
| 기록별 이명 | |

정본 §242의 Zᵃᵉ는 중간 누적 가중치 ∏min(t,q)를 포함하고 m<2q에 제한된다. Cᵃᵉ는 그 가중치의 q^(a+e)를 제외한 계수이며 모든 m에서 정의되므로 같은 대상으로 이름을 바꾸지 않는다.


현재 비형식 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. k0c2f8df2c56e4828bbf691cacca83b2a의 exact-empty-loss-and-all-chain-strata는 kfaeb6535dad54592857b1f726417d954에서 supported다. 이는 선행 성분 항등식·동률·국소 부호 논증의 비형식 수용이다. 이후 실제 C/F 계수 연결과 중앙차 하한의 형식 수용 범위는 위 Lean 대응에 기록했다. 성분 분할 수송 전체 Lean과 두 경계 전칭 부호는 여전히 남는다.

## 253. 골격·적중 성분 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격·적중 성분 다항식 · Fᵃᵉₘ,q(U,Y) |
| 종류 | 함수 |
| 정의 | m∈ℕ,q≥2에서 Fᵃᵉₘ,q(U,Y):=Σ_{a,e≥0}Cᵃᵉₘ,q(a,e)U^aY^e∈ℕ[U,Y]. |
| 잘 정의됨 | a,e≤m이므로 유한 다항식이다. |
| Lean 대응 | k7a6fb5f6105e475dab570454a8d5ef85/lean/MarkedComponents.lean의 ParkingForest.componentPolynomial. 실제 부모 함수 합과 C 계수, 세 평가값의 원 A/Δ 연결은 kdaa41390eadc4ac381e275adac86f547에서 accepted/matches. 모든 m≥0,q≥2의 원 동일성과 경계 부호를 구별한다. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §5, 식 (13) 직후. |
| 기록별 이명 | |


현재 비형식 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. k0c2f8df2c56e4828bbf691cacca83b2a의 exact-empty-loss-and-all-chain-strata는 kfaeb6535dad54592857b1f726417d954에서 supported다. 이는 선행 성분 항등식·동률·국소 부호 논증의 비형식 수용이다. 이후 실제 C/F 계수 연결과 중앙차 하한의 형식 수용 범위는 위 Lean 대응에 기록했다. 성분 분할 수송 전체 Lean과 두 경계 전칭 부호는 여전히 남는다.

현재 형식 수용 보완: k9a3297b965b24ea7a87eb1a666b8cd1a/lean/InteriorLower.lean의 evalComponents_eq_weightedEval, evalComponents_succ는 자연수 평가값의 최대 라벨 재귀를, original_delta_finite_loss_lower는 모든 n≥1,q≥2에서 정확 유한 Y 손실을 보존한 원 하계를, original_delta_two_hits_lower는 n<3q의 미분식 원 하계를 증명한다. 하계의 비음수성·원 두 무한족 부호·라벨 분할 전체 Lean은 포함하지 않는다. 검토 kc0a4185b9ecf4d70b84ed75e8e3caf67/general-finite-loss-and-interior-two-hit-lower에서 supported/accepted/matches/conforms다. 기존 정의·정의역은 보존한다.


## 254. 빈 골격 성분 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 빈 골격 성분 다항식 · Eᶜᵐᵖₘ,q(Y) |
| 종류 | 함수 |
| 정의 | m∈ℕ,q≥2에서 Eᶜᵐᵖₘ,q(Y):=Σ_{G∈𝔉↓ₘ,a_q(G)=0}(∏_{v:t_v<q}t_v)Y^{e_q(G)}. |
| 잘 정의됨 | 유한 다항식. Fᵃᵉₘ,q(0,Y)와 같음은 유한 합의 a=0 분할로 확인된다. |
| Lean 대응 | 미형식화. code/direct_chain.py의 empty_polynomials. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §4, 식 (6) 앞. |
| 기록별 이명 | |

정본 포화 결손 Eₙ,ℓ와 장식·인수·뜻이 다르다. 정본 𝒲_q(m)는 자연수 가중치 Y=q의 제한 영역 값과 관련되지만 변수 Y를 가진 이 함수와 같은 대상이라고 하지 않는다.


현재 비형식 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. k0c2f8df2c56e4828bbf691cacca83b2a의 exact-empty-loss-and-all-chain-strata는 kfaeb6535dad54592857b1f726417d954에서 supported다. 명시된 성분 항등식·동률·국소 부호 논증의 수용이며 일반 Lean 연결과 두 경계 전칭 부호는 미해결이다.


후속 검토 보완: k7a6fb5f6105e475dab570454a8d5ef85의 n≤2q+1 성분 분할·미분·공통 핵은 kdaa41390eadc4ac381e275adac86f547에서 비형식 supported다. 별도 E 상수나 그 성분 분할 재귀 전체의 일반 Lean 수용은 아니다.

## 255. 거듭제곱 중앙차

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 중앙차 · h_q(a) |
| 종류 | 함수 |
| 정의 | q≥2,a∈ℕ에서 h_q(a):=(q+1)^a−2q^a+(q−1)^a∈ℤ. |
| 잘 정의됨 | 정수 거듭제곱·차. |
| Lean 대응 | 별도 h 함수 상수 선언은 없다. k7a6fb5f6105e475dab570454a8d5ef85/lean/MarkedLower.lean의 ParkingForest.central_power_lower 및 central_power_lower_int가 명시적 중앙차의 2차 하한을 증명한다. kdaa41390eadc4ac381e275adac86f547에서 accepted/matches. |
| 출처 | k0c2f8df2c56e4828bbf691cacca83b2a/exposition.md §7, 식 (19) 앞. |
| 기록별 이명 | |

정본 §248의 φᵍᵃⁱⁿ_q(a)는 q²[(1+1/q)^a+(1−1/q)^a−2]다. 둘의 관계 h_q(a)=q^(a−2)φᵍᵃⁱⁿ_q(a)는 q>0인 유리수 식의 항등식이며 같은 함수로 개명하지 않는다.


현재 비형식 수용 보완: 정의는 직전 계획 kfc4dd3376c07461aacc17637fedd6c06에서 채택됐다. k0c2f8df2c56e4828bbf691cacca83b2a의 exact-empty-loss-and-all-chain-strata는 kfaeb6535dad54592857b1f726417d954에서 supported다. 이는 선행 성분 항등식·동률·국소 부호 논증의 비형식 수용이다. 이후 실제 C/F 계수 연결과 중앙차 하한의 형식 수용 범위는 위 Lean 대응에 기록했다. 성분 분할 수송 전체 Lean과 두 경계 전칭 부호는 여전히 남는다.

현재 형식 수용 보완: k9a3297b965b24ea7a87eb1a666b8cd1a/lean/InteriorLower.lean의 curvature_finite_loss_lower, monomial_finite_loss_lower, curvature_two_hits_lower, monomial_two_hits_lower는 중앙차 하한에 비음수 실제 가중치를 곱한 일반 하계다. 하계 우변의 비음수는 미증명이다. 검토 kc0a4185b9ecf4d70b84ed75e8e3caf67/general-finite-loss-and-interior-two-hit-lower에서 supported/accepted/matches/conforms다. 기존 정의·정의역은 보존한다.


## 256. 골격·연속 적중 동시 표시 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 골격·연속 적중 동시 표시 다항식 · J^{aeh}_{m,x}(z,u,v) |
| 종류 | 함수 |
| 정의 | 정수 x≥2,0≤m<2x에서 J^{aeh}_{m,x}(z,u,v):=Σ_{G∈𝔉↓ₘ} (∏_{w∈[m]}min(t_w(G),x)) z^{a_x(G)}u^{e_x(G)}v^{e_{x+1}(G)}∈ℕ[z,u,v]. |
| 잘 정의됨 | 유한 감소 부모 함수 숲 위의 유한 다항식 합이다. m=0은 빈 숲·빈 곱으로 1이다. J(z,u,1)=Z^{ae}(z,u)라는 주변 관계와 정의는 구별한다. |
| Lean 대응 | 미형식화. 일반 동시 재귀·적중 인수분해는 kf0625227f0b24a178ad0ee9a63601def에서 비형식 supported이며 전체 Lean은 없다. |
| 출처 | kb29a863507944e8d9442e6cd0a3f1d8f/joint-law.md (2), glossary-proposals.md 첫 항목. 계획 kebb9203d1da440949d97eb4334dbe1b4에서 채택. |
| 기록별 이명 | 없음 |

## 257. 현재 골격의 전진 곡률

| 칸 | 내용 |
|---|---|
| 이름·기호 | 현재 골격의 전진 곡률 · F^{step}_{n,ℓ} |
| 종류 | 함수 |
| 정의 | 정수 n≥1,ℓ≥1,x:=ℓ+1에서 F^{step}_{n,ℓ}:=Ŵₙ(x;x+2)−2Ŵₙ(x;x+1)+Ŵₙ(x;x)∈ℤ. |
| 잘 정의됨 | Ŵ의 자연수 매개변수 대입값을 정수로 올려 차를 취한다. 현재 문턱 x를 고정하며 다음 문턱의 Γ⁺와 다르다. |
| Lean 대응 | kb29a863507944e8d9442e6cd0a3f1d8f/lean/CombinedTransport.lean의 ParkingCombined.forwardGain, forwardGain_nonneg, forward_delta. kf0625227f0b24a178ad0ee9a63601def에서 original-forward-transport-algebra가 accepted/matches. 모든 양수 n,ℓ의 이 정의·비음수성과 원 전진 차분 동일성만 뜻한다. |
| 출처 | kb29a863507944e8d9442e6cd0a3f1d8f/transport.md (12), glossary-proposals.md 둘째 항목. 계획 kebb9203d1da440949d97eb4334dbe1b4에서 채택. |
| 기록별 이명 | 없음 |

## 258. 다음 정확 적중 보정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 다음 정확 적중 보정 · H^{step}_{n,ℓ} |
| 종류 | 함수 |
| 정의 | 정수 n≥1,ℓ≥1,x:=ℓ+1에서 H^{step}_{n,ℓ}:=Ŵₙ(x;x+2)−Aₙ,ℓ₊₂∈ℤ. |
| 잘 정의됨 | 자연수 가중합과 원 개수를 정수로 올려 차를 취한다. H^{tree}·Γ⁻ 및 조건부 적중 확률과 다른 대상이다. |
| Lean 대응 | kb29a863507944e8d9442e6cd0a3f1d8f/lean/CombinedTransport.lean의 ParkingCombined.nextCorrection, nextCorrection_nonneg, forward_delta. kf0625227f0b24a178ad0ee9a63601def에서 original-forward-transport-algebra가 accepted/matches. 응답 다항식 식별 전체까지 형식화된 것은 아니다. |
| 출처 | kb29a863507944e8d9442e6cd0a3f1d8f/transport.md (12), glossary-proposals.md 셋째 항목. 계획 kebb9203d1da440949d97eb4334dbe1b4에서 채택. |
| 기록별 이명 | 없음 |

현재 엄격 양수성 대응: k716f5d11dad24f78a224774000d9f0b0/lean/StrictCorrections.lean의 nextCorrection_pos는 양수 n,ℓ 및 n≥ℓ+2에서 원 H^{step}ₙ,ℓ>0를 증명한다. k60bb458604ee4921a8ed08021b1ef90d/original-strict-corrections에서 accepted/matches. 응답·블록 인수분해와 전체 꼬리의 일반 Lean 수용은 아니다.


## 259. 합친 수송 행렬식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 합친 수송 행렬식 · 𝓜^{step}_{n,ℓ} |
| 종류 | 함수 |
| 정의 | 정수 n≥1,ℓ≥1에서 𝓜^{step}_{n,ℓ}:=Γ⁺ₙ,ℓ H^{step}_{n,ℓ}−F^{step}_{n,ℓ} Γ⁻ₙ,ℓ∈ℤ. |
| 잘 정의됨 | 앞서 정의한 정수 값의 곱과 차다. 비음수성은 정의나 확립된 정리에 포함하지 않는다. |
| Lean 대응 | kb29a863507944e8d9442e6cd0a3f1d8f/lean/CombinedTransport.lean의 ParkingCombined.determinant_step, determinant_strict_step에서 hM에 위 식을 전개해 사용한다. 별도 함수 선언은 없다. kf0625227f0b24a178ad0ee9a63601def에서 해당 조건부 수송은 accepted/matches이며 hM 자체의 증명은 없다. |
| 출처 | kb29a863507944e8d9442e6cd0a3f1d8f/transport.md (15), glossary-proposals.md 넷째 항목. 계획 kebb9203d1da440949d97eb4334dbe1b4에서 채택. |
| 기록별 이명 | 없음 |

현재 부분 부호의 보증 경계: k716f5d11dad24f78a224774000d9f0b0/determinant-tail.md (8),(18)의 x=ℓ+1,d=n−x≥2,x≥2d³에서의 𝓜^{step}>0는 k60bb458604ee4921a8ed08021b1ef90d/combined-determinant-cubic-tail에서 비형식 supported다. 마지막 실수 산술 cubic_budget_new만 형식화됐고 실제 행렬식 꼬리 전체는 미형식화다. 새 무조건 U 무한 영역은 없으며 일반 행렬식 부호는 미해결이다.


## 260. 소부분나무 기초 가중치

| 칸 | 내용 |
|---|---|
| 이름·기호 | 소부분나무 기초 가중치 · w^{<}_q(G) |
| 종류 | 함수 |
| 정의 | m∈ℕ,q≥2,G∈𝔉↓ₘ에서 w^{<}_q(G):=∏_{v:t_v(G)<q}t_v(G). 빈 곱은 1. |
| 잘 정의됨 | 유한 곱. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 lean/MarkedComponents.lean의 ParkingForest.smallBase. kdaa41390eadc4ac381e275adac86f547에서 해당 구현·원 연결·경계 하계가 accepted/matches다. 하계의 비음수성은 미증명이다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §2 (3). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 261. 표시 2차 이득

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 2차 이득 · Pᵐᵃʳᵏₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,0≤m≤2q+1에서 Pᵐᵃʳᵏₘ,q:=(∂²_U Fᵃᵉₘ,q)(q,q). ∂는 통상 형식 미분. |
| 잘 정의됨 | 유한 자연수 다항식의 미분·평가. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 component_UU의 U=Y=q인 LHS. 별도 함수 상수 선언을 만들지 않았다. kdaa41390eadc4ac381e275adac86f547에서 해당 구현·원 연결·경계 하계가 accepted/matches다. 하계의 비음수성은 미증명이다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §4 (12). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 262. 표시 정확 손실

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 정확 손실 · Bᵐᵃʳᵏₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,0≤m≤2q+1에서 Bᵐᵃʳᵏₘ,q:=(∂_Y Fᵃᵉₘ,q)(q−1,0)+(2q−1)/2·(∂²_Y Fᵃᵉₘ,q)(q−1,0). |
| 잘 정의됨 | 유리수 식이며 ∂²_Y의 모든 계수가 짝수이므로 정수. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 component_Y, component_YY의 해당 평가값. original_delta_marked_lower에서는 전체를 2배하여 구현. kdaa41390eadc4ac381e275adac86f547에서 해당 구현·원 연결·경계 하계가 accepted/matches다. 하계의 비음수성은 미증명이다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §4 (12). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 263. 표시 2차 하계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 2차 하계 · Lᵐᵃʳᵏₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,0≤m≤2q+1에서 Lᵐᵃʳᵏₘ,q:=Pᵐᵃʳᵏₘ,q−Bᵐᵃʳᵏₘ,q∈ℤ. |
| 잘 정의됨 | 앞 두 정수 함수의 차. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 original_delta_marked_lower의 RHS/2. n≥1인 범위의 원 Δ 하계를 증명하며 L≥0은 미증명. kdaa41390eadc4ac381e275adac86f547에서 해당 구현·원 연결·경계 하계가 accepted/matches다. 하계의 비음수성은 미증명이다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §4 (12),(13). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 264. 표시 원천

| 칸 | 내용 |
|---|---|
| 이름·기호 | 표시 원천 · Sᵐᵃʳᵏₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,0≤m≤2q+1에서 Sᵐᵃʳᵏₘ,q:=Lᵐᵃʳᵏₘ,q−q Σ_{s=q+1}^m binom(m,s)Eᶜᵐᵖₘ₋ₛ,q(q)Lᵐᵃʳᵏₛ₋₁,q. |
| 잘 정의됨 | 유한 정수 합. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 미형식화. kdaa41390eadc4ac381e275adac86f547에서 해당 비형식 논증·계산의 명시 범위를 supported로 수용했다. 이 함수의 일반 Lean 인증은 없다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §6 (20),(21). (20)은 이 정의와 동치인 직접 미분식. 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 265. 원 차분 전달 원천

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 차분 전달 원천 · Sᵉˣᵃᶜᵗₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,q≤m≤2q+1에서 Sᵉˣᵃᶜᵗₘ,q:=Eᶜᵐᵖₘ,q(q−1)−Eᶜᵐᵖₘ,q(q)+Σ_{s=q+1}^m binom(m,s)Tₘ₋ₛ(Aₛ₋₁,q−Aₛ₋₁,q₋₂)−1_{m=2q+1}(q−1)binom(2q+1,q)T_q₋₁(T_q−T_q₋₁). |
| 잘 정의됨 | 유한 정수 합。s−1≥q≥2이므로 모든 A의 영역이 맞는다. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 미형식화. kdaa41390eadc4ac381e275adac86f547에서 해당 비형식 논증·계산의 명시 범위를 supported로 수용했다. 이 함수의 일반 Lean 인증은 없다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §7 (23). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 266. 원 차분 전달 핵

| 칸 | 내용 |
|---|---|
| 이름·기호 | 원 차분 전달 핵 · Rᶜᵃᵖₙ,ᵣ(q) |
| 종류 | 함수 |
| 정의 | q≥2,q≤r≤n≤2q+1에서 Rᶜᵃᵖₙ,ᵣ(q):=1_{n=r}+qΣ_{s=q+1}^n binom(n,s)Tₙ₋ₛRᶜᵃᵖₛ₋₁,ᵣ(q). 재귀의 k<r인 값은 0으로 둔다. |
| 잘 정의됨 | 크기 n에 대한 삼각 재귀이며 모든 계수는 비음수 정수. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 미형식화. code/exact_transport.py의 R. kdaa41390eadc4ac381e275adac86f547에서 해당 비형식 논증·계산의 명시 범위를 supported로 수용했다. 이 함수의 일반 Lean 인증은 없다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §7 (27). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 267. 비절단 문턱 표시합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 비절단 문턱 표시합 · Hᵘⁿᶜₘ,q |
| 종류 | 함수 |
| 정의 | m∈ℕ,q≥2에서 Hᵘⁿᶜₘ,q:=Σ_{G∈𝔉↓ₘ}Σ_{v:t_v(G)=q}∏_{u≠v}t_u(G). |
| 잘 정의됨 | 유한 자연수 합. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 미형식화. code/source_probe.py의 uncapped_hit는 최대 라벨 미분 재귀 계산 구현. kdaa41390eadc4ac381e275adac86f547에서 해당 비형식 논증·계산의 명시 범위를 supported로 수용했다. 이 함수의 일반 Lean 인증은 없다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §8 (29). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 268. 대칭 홀수 잔여

| 칸 | 내용 |
|---|---|
| 이름·기호 | 대칭 홀수 잔여 · Ωᵐᵃʳᵏₘ,q |
| 종류 | 함수 |
| 정의 | q≥2,0≤m≤2q+1에서 Ωᵐᵃʳᵏₘ,q:=Fᵃᵉₘ,q(q+1,q)−Fᵃᵉₘ,q(q−1,q)−2(∂_U Fᵃᵉₘ,q)(q,q). |
| 잘 정의됨 | 유한 정수 다항식 평가·미분. 비음수성은 exposition.md (28b)의 이항 전개로 별도 증명한다. |
| Lean 대응 | 기록 k7a6fb5f6105e475dab570454a8d5ef85의 미형식화. code/source_comparison.py의 omega. kdaa41390eadc4ac381e275adac86f547에서 해당 비형식 논증·계산의 명시 범위를 supported로 수용했다. 이 함수의 일반 Lean 인증은 없다. |
| 출처 | k7a6fb5f6105e475dab570454a8d5ef85/exposition.md §7.1 (28a). 계획 kebb9203d1da440949d97eb4334dbe1b4에서 정의 채택. |
| 기록별 이명 | |

정의의 채택과 독립 수학 검토는 별개다. 원천·전달·하계의 부호는 정의에 포함하지 않는다.

## 269. 연속 블록 표시 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 연속 블록 표시 다항식 · 𝓑^{blk}_{a,b}(c;z) |
| 종류 | 함수 |
| 정의 | 정수 1≤a≤b+1에서 𝓑^{blk}_{a,b}(c;z):=Σ_π∏_{J∈π}w(J). π는 {a,…,b}의 연속 블록 분할 전부이고 w({i}):=z(1+c/i), 길이 r≥2의 블록 가중치 w(J):=𝔞ᵣ. c,z는 형식변수이며 유리수 다항식으로 정의한다. 빈 구간의 값은 1. |
| 잘 정의됨 | 유한 구간의 유한 분할 합이며 i≥1이다. |
| Lean 대응 | 미형식화. code/marked_blocks.py의 marked는 계산 구현. |
| 출처 | k716f5d11dad24f78a224774000d9f0b0/cancellation.md (19). z=1의 기존 정규화 응답과의 동일성은 (20)이며, z표시는 새로운 대상이다. 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

정규화 응답과 z=1에서의 동일성은 k60bb458604ee4921a8ed08021b1ef90d가 비형식 supported로 수용했다. z를 유지하는 새 다항식 전체의 Lean은 없다.


## 270. 첫 칸 복원 표시 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 첫 칸 복원 표시 다항식 · 𝓔^{blk}_{x,d}(c;z) |
| 종류 | 함수 |
| 정의 | 정수 x≥2,d≥2에서 𝓔^{blk}_{x,d}(c;z):=(1+c/(x+1))𝓑^{blk}_{x+2,x+d}(c;z)+z𝔞₂𝓑^{blk}_{x+3,x+d}(c;z)+Σ_{r=2}^{d−1}𝔞ᵣ₊₁𝓑^{blk}_{x+r+2,x+d}(c;z). c,z는 형식변수. |
| 잘 정의됨 | 유한 유리수 다항식 합. |
| Lean 대응 | 미형식화. code/marked_blocks.py의 extension는 계산 구현. |
| 출처 | k716f5d11dad24f78a224774000d9f0b0/cancellation.md (21). z는 첫 칸을 지운 뒤 남은 분할의 한 칸 수를 표시한다. z=1에서만 𝓑^{blk}_{x+1,x+d}(c;1)와 같다고 쓴다. 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

z는 첫 칸 삭제 뒤 남는 분할의 한 칸 수를 표시한다. 통상적인 전체 분할의 한 칸 수 표시와 같다고 정의하지 않는다. z=1의 항등식과 일반 정의를 구별한다.


## 271. 블록 층 말단 행렬식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 블록 층 말단 행렬식 · 𝓓^{blk}_{x,d}(z) |
| 종류 | 함수 |
| 정의 | 정수 x≥2,2≤d<x에서 B(c;z):=𝓑^{blk}_{x+2,x+d}(c;z), g(z):=(x+1)B(x+1;z)−2xB(x;z)+(x−1)B(x−1;z), f(z):=(x+2)B(x+2;z)−2(x+1)B(x+1;z)+xB(x;z)라 쓰고 𝓓^{blk}_{x,d}(z):=Tₓg(z)B(x+2;z)−(x+1)Tₓ₋₁f(z)𝓔^{blk}_{x,d}(x−1;z)∈ℚ[z]. |
| 잘 정의됨 | 앞 유한 다항식들의 곱과 차. |
| Lean 대응 | 미형식화. code/marked_blocks.py의 point 안 det는 계산 구현. |
| 출처 | k716f5d11dad24f78a224774000d9f0b0/cancellation.md (23). (24)의 계승 배율을 곱하면 s=x 말단 원천 괄호이며 전체 𝓜^{step}와 다른 대상이다. 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

k60bb458604ee4921a8ed08021b1ef90d가 4≤d<x의 1차 계수 음수성을 비형식 supported로 수용했다. z=1에서 계승 배율을 곱한 값은 s=x 말단 원천 괄호이며 전체 𝓜^{step}가 아니다. 전체 원 행렬식·U/P의 반례가 아니다.


## 272. 큰 연결 성분 수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 큰 연결 성분 수 · r^{cmp}_q(G) |
| 종류 | 함수 |
| 정의 | m∈ℕ,정수 q≥2,G∈𝔉↓ₘ에서 r^{cmp}_q(G):=#{v∈[m]:p_G(v)=0 및 t_v(G)>q}. |
| 잘 정의됨 | 유한 집합의 크기. 각 연결 성분의 유일한 뿌리의 자손 집합이 그 성분 전체이므로 크기>q인 연결 성분 수와 같다. |
| Lean 대응 | 미형식화. code/independent.py의 j가 실제 부모 함수를 직접 분류한다. a_q 또는 λ_q와 동일시하지 않는다. |
| 출처 | k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md §3. 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

정의 채택과 수학적 수용은 구별한다. kc0a4185b9ecf4d70b84ed75e8e3caf67는 실제 라벨 분할·전단사를 명시된 범위에서 비형식 supported로 수용했다. 원 두 내부 무한족의 부호와 일반 분할 Lean은 미완료다.


## 273. 큰 연결 성분 수별 성분 다항식

| 칸 | 내용 |
|---|---|
| 이름·기호 | 큰 연결 성분 수별 성분 다항식 · F^{ae,[j]}_{m,q}(U,Y) |
| 종류 | 함수 |
| 정의 | m,j∈ℕ,정수 q≥2에서 F^{ae,[j]}_{m,q}(U,Y):=Σ_{G∈𝔉↓ₘ,r^{cmp}_q(G)=j}w^{<}_q(G)U^{a_q(G)}Y^{e_q(G)}∈ℕ[U,Y]. |
| 잘 정의됨 | 실제 감소 숲의 유한 부분집합 위의 자연수 계수 다항식 합. |
| Lean 대응 | 미형식화. code/two_components.py의 component_split이 (8),(9)를 구현하고 별도 직접 부모 함수 분류와 대조한다. |
| 출처 | k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md §3 식 (6)–(9). 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

F^{ae,[0]}=Eᶜᵐᵖ 및 m<3(q+1)에서의 0/1/2 성분 분할은 k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md §3의 비형식 정리로 kc0a4185b9ecf4d70b84ed75e8e3caf67에서 supported다. 실제 라벨 분할 전체의 일반 Lean은 없다.


## 274. 성분 세 평가 차 연산

| 칸 | 내용 |
|---|---|
| 이름·기호 | 성분 세 평가 차 연산 · 𝒟^{cmp}_q |
| 종류 | 함수 |
| 정의 | 정수 q≥2,f∈ℚ[U,Y]에서 𝒟^{cmp}_q f:=f(q+1,q)−2f(q,q)+f(q−1,q−1)∈ℚ. |
| 잘 정의됨 | 유리수 다항식의 세 평가값의 선형 결합. 정수 계수 다항식에는 정수 값을 갖는다. |
| Lean 대응 | 이 연산을 별도 정의하지 않았다. 원 F의 경우 재사용 original_delta_components; 일반 다항식 연산은 미형식화. |
| 출처 | k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md §4 식 (12). 정의 관리: 이번 계획. |
| 기록별 이명 | 기록 k9a3297b965b24ea7a87eb1a666b8cd1a의 성분 세 평가 차 연산 \(\mathscr D_q\). 총 변위 𝒟(α)와 다른 대상이므로 이후에는 𝒟^{cmp}_q를 쓴다. |

기존 총 변위의 기호 𝒟와 구별하기 위한 기호 개명이며 함수 정의는 그대로다. 원 n≥1의 F 적용값과 Δ의 동일성은 이미 수용된 original_delta_components를 사용한다. 상수 다항식 1의 값 0은 b₀,ℓ의 정의가 아니다.


## 275. 두 큰 성분 보존 원천

| 칸 | 내용 |
|---|---|
| 이름·기호 | 두 큰 성분 보존 원천 · S^{2cmp}_{m,q} |
| 종류 | 함수 |
| 정의 | m∈ℕ,정수 q≥4,0≤m≤2q+3에서, q 고정의 Fᵣ=Fᵃᵉᵣ,q,Eᵣ=Eᶜᵐᵖᵣ,q를 써 \(S^{2cmp}_{m,q}:=E_m(q-1)-E_m(q)+\mathscr D^{cmp}_qF^{ae,[2]}_{m,q}+\sum_{s=q+1}^m\binom ms[E_{m-s}(q)\{F_{s-1}(q+1,q)-F_{s-1}(q-1,q-1)\}+(q-1)F_{s-1}(q-1,q-1)\{E_{m-s}(q-1)-E_{m-s}(q)\}]\)∈ℤ. |
| 잘 정의됨 | 앞서 정의한 다항식들의 정수 평가값·정수 계수의 유한 합. 원천의 부호는 정의에서 정하지 않는다. |
| Lean 대응 | 미형식화. code/two_components.py의 transport[].source가 모든 항을 보존해 계산한다. |
| 출처 | k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md §6 식 (20). 정의 관리: 이번 계획. |
| 기록별 이명 | 없음 |

k9a3297b965b24ea7a87eb1a666b8cd1a/exposition.md (20),(21)의 실제 라벨 분할과 수송은 kc0a4185b9ecf4d70b84ed75e8e3caf67에서 비형식 supported로 수용됐다. 경계의 Sᵉˣᵃᶜᵗ와 같은 대상이 아니며 정의역을 바꾸어 같은 이름으로 쓰지 않는다. 일반 수송 Lean과 원 부호는 미완료다.

## 276. 문턱 지수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 문턱 지수 · Λ_y(G) |
| 종류 | 함수 |
| 정의 | n∈ℕ, G∈𝔉↓ₙ, 실수 y>0에 대해 Λ_y(G) := Σ_{v∈[n]} max(0, log(t_v(G)/y)). 로그는 자연로그다. |
| 잘 정의됨 | 유한 합. 정의에서 바로 e^{−Λ_y(G)} = ∏_v min(1, y/t_v(G))이고, y에 대해 비증가이며 y≥n이면 0이다. 표기 관례로 n≥1에서 Λ_0(G):=+∞, e^{−Λ_0(G)}:=0을 쓴다(P(M≤−1)=0에 대응). |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §3, §4 |
| 기록별 이명 | 없음 |

## 277. 복제 문턱 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 문턱 함수 · ϱₙ(y,r) |
| 종류 | 함수 |
| 정의 | n≥1, 실수 y>0, r>0에 대해 ϱₙ(y,r) := Tₙ⁻¹ Σ_{G∈𝔉↓ₙ} (∏_{v∈[n]} t_v(G)) · e^{−r Λ_y(G)}. |
| 잘 정의됨 | 유한 합. 정수 ℓ≥0에서 ϱₙ(ℓ+1,1)=Aₙ,ℓ/Tₙ는 정의가 아니라 수용된 숲 가중합 Aₙ,ₓ₋₁=Σ_G∏_v min(t_v,x)(kb29a863507944e8d9442e6cd0a3f1d8f/exposition.md 식 (1)의 재사용 범위)에서 따르는 관계다. y≥n이면 ϱₙ(y,r)=1. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §3, §7 |
| 기록별 이명 | 없음 |

## 278. 복제 최대 변위 분포

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 최대 변위 분포 · 𝔟ʳᵉᵖₙ,ℓ(r) |
| 종류 | 함수 |
| 정의 | n≥1, 실수 r>0, ℓ∈{0,…,n−1}에 대해 𝔟ʳᵉᵖₙ,₀(r) := ϱₙ(1,r), ℓ≥1이면 𝔟ʳᵉᵖₙ,ℓ(r) := ϱₙ(ℓ+1,r) − ϱₙ(ℓ,r). |
| 잘 정의됨 | 유한 값의 차. ϱₙ이 y에 대해 비감소이므로 음이 아니고, 합은 ϱₙ(n,r)=1이다. r=1이면 bₙ,ℓ/Tₙ와 같다(위 관계). 정수 r이면 같은 숲을 공유하는 r개의 독립 균등 변위 상자 전체의 최댓값 분포다(본문 §4). 기존 도착 시각별 정확 개수 b^{(τ)}ₙ,ℓ와 다른 대상이다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §3, §7 |
| 기록별 이명 | 없음 |

## 279. 연속 문턱 창 개수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 연속 문턱 창 개수 · Bʷⁱⁿₙ(y) |
| 종류 | 함수 |
| 정의 | n≥1, 실수 y≥0에 대해 Bʷⁱⁿₙ(y) := 𝒜ₙ(y+1) − 𝒜ₙ(y). |
| 잘 정의됨 | 𝒜ₙ이 유한 합이므로 정의된다. 정수 ℓ에서 Bʷⁱⁿₙ(ℓ)=bₙ,ℓ는 정본 §142의 관계 𝒜ₙ(ℓ+1)=Aₙ,ℓ(수용된 순열 상자 표현에서 따름)과 𝒜ₙ(0)=0(n≥1)에서 따른다. 확률로는 Bʷⁱⁿₙ(y)/Tₙ = P(y≤M̃<y+1)이다(정본 §143의 해석, 탐구 수준). |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §8 |
| 기록별 이명 | 없음 |

## 280. 로그–로그 오목성

| 칸 | 내용 |
|---|---|
| 이름·기호 | 로그–로그 오목성 · LLC_θ(x) |
| 종류 | 성질·관계 |
| 정의 | 정수 m≥2, 양의 실수 수열 x=(x₀,…,x_m), 실수 θ>0에 대해 LLC_θ(x) :⇔ 모든 1≤k≤m−1에서 (log x_k − log x_{k+1})/log((m−k+θ)/(m−k−1+θ)) ≥ (log x_{k−1} − log x_k)/log((m−k+1+θ)/(m−k+θ)). |
| 잘 정의됨 | θ>0이므로 모든 로그의 인수가 양수이고 분모가 양수다. 뜻: 점 (log(m−k+θ), log x_k)를 m−k+θ가 커지는 순서로 이은 꺾은선이 오목하다. b행에는 m=n−1, x_k=bₙ,ₖ로 적용하며 이때 m−k+θ=n−1−ℓ+θ는 끝에서 잰 거리에 θ를 더한 값이다. 이 성질은 Unimodal(x)를 함의한다(기울기가 비증가이므로 부호가 +에서 −로 많아야 한 번 바뀐다). |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §6.3 |
| 기록별 이명 | 없음 |

## 281. 최댓값 면적 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최댓값 면적 밀도 · f_𝒵(x) |
| 종류 | 함수 |
| 정의 | 실수 x>0에 대해 f_𝒵(x) := 2^{7/6}Γ(2/3)⁻¹ e^{−3x²/2} U(−1/6; 2/3; 3x²/2). U는 2종 합류초기하함수(Abramowitz–Stegun 13.1.3)다. |
| 잘 정의됨 | 닫힌 식. 이것이 𝒵의 확률밀도라는 것은 Janson, arXiv:1002.4135v1, Theorem 1.8(넷째 식)의 문헌 결과이며 정의와 별개다. Janson은 𝒵를 A로 쓴다. 같은 정리의 1F1 표현과 급수 표현이 이 식과 수치로 일치함을 본문 §5.4에서 확인했다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §5.1; Janson (2010) Theorem 1.8 |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 면적 밀도 f |

## 282. 극한 최대 변위 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 극한 최대 변위 밀도 · f_ν(y) |
| 종류 | 함수 |
| 정의 | 실수 y>0에 대해 f_ν(y) := (3/2) y^{1/2} ∫₀^∞ a e^{−y^{3/2} a} f_𝒵(a) da. |
| 잘 정의됨 | 적분이 수렴한다(f_𝒵는 유계이고 가우스 꼴로 감쇠). 이것이 ν의 밀도라는 것은 ν의 정의(정본 §89)와 Janson Lemma 1.11, 그리고 미분과 적분의 교환(E𝒵<∞)에서 따른다(본문 §5.1). Janson Theorem 1.13의 급수와 수치로 일치한다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §5.1 |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 극한 밀도 p_ν |

## 283. 로그 시계 핵

| 칸 | 내용 |
|---|---|
| 이름·기호 | 로그 시계 핵 · 𝔨(u) |
| 종류 | 함수 |
| 정의 | 실수 u에 대해 𝔨(u) := exp(u/3 − e^u). |
| 잘 정의됨 | 닫힌 식. ∫𝔨 = Γ(1/3)이고 log 𝔨가 오목하다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §5.3 |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 합성곱 핵 k |

## 284. 연속 약단봉성

| 칸 | 내용 |
|---|---|
| 이름·기호 | 연속 약단봉성 · \(\mathrm{CUni}_I(v)\) |
| 종류 | 성질·관계 |
| 정의 | I는 열린 실수 구간, v:I→[0,∞)는 연속함수일 때 CUni_I(v) :⇔ 어떤 a∈I가 존재하여 v가 I∩(−∞,a]에서 비감소하고 I∩[a,∞)에서 비증가한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/exposition.md 첫 정의. 정본 §11의 유한열 Unimodal과 별개. |
| 기록별 이명 | 없음 |

## 285. 연속 엄격 단봉성

| 칸 | 내용 |
|---|---|
| 이름·기호 | 연속 엄격 단봉성 · \(\mathrm{CSUni}_I(v)\) |
| 종류 | 성질·관계 |
| 정의 | I는 열린 실수 구간, v:I→[0,∞)는 연속함수일 때 CSUni_I(v) :⇔ 어떤 a∈I가 존재하여 v가 I∩(−∞,a]에서 엄격 증가하고 I∩[a,∞)에서 엄격 감소한다. |
| 잘 정의됨 | 해당 없음 |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/exposition.md 첫 정의. 이 정의 자체에 도함수 부호나 음의 이계도함수를 포함하지 않는다. |
| 기록별 이명 | 없음 |

## 286. 극한분포 보조변수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 극한분포 보조변수 · \(Y_\nu\) |
| 종류 | 대상 |
| 정의 | 정본 𝒵와 독립인 평균 1 지수변수 X의 곱확률공간에서 Y_ν:=(X/𝒵)^(2/3). 𝒵=0인 예외에는 0으로 둔다. |
| 잘 정의됨 | 𝒵>0가 거의 확실. density.md §1. ν를 갖는 한 확률변수 선택이며 원 M과 다름. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/literature.md §1, density.md §1. 정본 §89의 ν 정의는 유지. |
| 기록별 이명 | 없음 |

## 287. 기울인 면적 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울인 면적 함수 · \(h_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>0,x>0에서 h_c(x):=x^c f_𝒵(x). |
| 잘 정의됨 | 양의 실수 거듭제곱. 정규화 밀도라는 뜻은 아니다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md (T1) 앞 |
| 기록별 이명 | 기록 k2d51fc12f1254808a99f42f03fe5224b의 h_𝒵는 h_(5/3)의 특수화다. 이후에는 기울인 면적 함수 h_(5/3)를 쓴다. |

## 288. 기울임 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울임 계수 · \(Q_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>0,x>0에서 Q_c(x):=c(c+2/3)/x²+5−3c. |
| 잘 정의됨 | x>0. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md (T1) |
| 기록별 이명 | 없음 |

## 289. 기울임 적분인자

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울임 적분인자 · \(\mu_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>0,x>0에서 μ_c(x):=x^(1/3−2c)exp(3x²/2). |
| 잘 정의됨 | 양수 유한. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md (T1) |
| 기록별 이명 | 없음 |

## 290. 기울임 미분량

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울임 미분량 · \(V_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>0,x>0에서 V_c(x):=μ_c(x)h_c′(x). |
| 잘 정의됨 | h_c는 양의 반직선에서 매끄럽다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md (T1) |
| 기록별 이명 | 없음 |

## 291. 기울임 계수 전환점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울임 계수 전환점 · \(a_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>5/3에서 a_c:=sqrt(c(c+2/3)/(3c−5)). |
| 잘 정의됨 | 근호 안은 양수. c≤5/3에는 정의하지 않음. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md §5 |
| 기록별 이명 | 없음 |

## 292. 가중 로그 좌표 밀도값

| 칸 | 내용 |
|---|---|
| 이름·기호 | 가중 로그 좌표 밀도값 · \(𝒢_ν\) |
| 종류 | 함수 |
| 정의 | 실수 z에서 𝒢_ν(z):=f_ν(exp(2z/3)). |
| 잘 정의됨 | y>0. z의 확률밀도를 뜻하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §2 |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 가중 로그 좌표 밀도값 G |

## 293. 역로그 면적 기울임

| 칸 | 내용 |
|---|---|
| 이름·기호 | 역로그 면적 기울임 · \(m\) |
| 종류 | 함수 |
| 정의 | 실수 ζ에서 m(ζ):=exp(−5ζ/3)f_𝒵(exp(−ζ)). |
| 잘 정의됨 | 양수 유한. 적분가능성과 엄격 단봉성은 density.md §3. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md (D3) |
| 기록별 이명 | 없음 |

## 294. 기본 합성곱 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기본 합성곱 함수 · \(g^conv_ν\) |
| 종류 | 함수 |
| 정의 | 실수 z에서 g^conv_ν(z):=∫_ℝ 𝔨(z−ζ)m(ζ)dζ. |
| 잘 정의됨 | 로그 시계 핵 𝔨는 유계, m∈L¹이므로 절대수렴. 정본 §212의 이항 이변수 합성과 구별. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §4 |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 기본 합성곱 함수 g |

## 295. 로그 극한변수 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 로그 극한변수 밀도 · \(q_{\log Y_\nu}\) |
| 종류 | 함수 |
| 정의 | 실수 w에서 q_(log Y_ν)(w):=exp(w)f_ν(exp(w)). |
| 잘 정의됨 | 밀도 변수변환. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md (D5) |
| 기록별 이명 | 없음 |

## 296. 재척도 로그 극한변수 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 재척도 로그 극한변수 밀도 · \(q_{(3/2)\log Y_\nu}\) |
| 종류 | 함수 |
| 정의 | 실수 z에서 q_((3/2)log Y_ν)(z):=(2/3)exp(2z/3)f_ν(exp(2z/3)). |
| 잘 정의됨 | 밀도 변수변환. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md (D5) |
| 기록별 이명 | 없음 |

## 297. 로그 지수시계 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 로그 지수시계 밀도 · \(k_0\) |
| 종류 | 함수 |
| 정의 | 실수 u에서 k₀(u):=exp(u−exp(u)). |
| 잘 정의됨 | log X의 밀도 변수변환. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §2 |
| 기록별 이명 | 없음 |

## 298. 역로그 면적 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 역로그 면적 밀도 · \(m_0\) |
| 종류 | 함수 |
| 정의 | 실수 ζ에서 m₀(ζ):=exp(−ζ)f_𝒵(exp(−ζ)). |
| 잘 정의됨 | −log 𝒵의 밀도 변수변환. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §2 |
| 기록별 이명 | 없음 |

## 299. 브라운 최댓값과정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 브라운 최댓값과정 · \(S_B\) |
| 종류 | 함수 |
| 정의 | 연속 브라운 경로 B와 실수 t≥0에서 S_B(t):=sup{B_u:0≤u≤t}. |
| 잘 정의됨 | 콤팩트 위 연속함수의 최댓값. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md §2; 정본 §86의 적분 안 최댓값을 별도 함수로 표기. |
| 기록별 이명 | 없음 |

## 300. 최댓값 면적과정

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최댓값 면적과정 · \(\mathcal A_B\) |
| 종류 | 함수 |
| 정의 | 연속 브라운 경로 B와 실수 t≥0에서 𝒜_B(t):=∫₀ᵗ S_B(v)dv. |
| 잘 정의됨 | 연속함수의 적분. 𝒜_B(1)=𝒵. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md (S2) |
| 기록별 이명 | 없음 |

## 301. 척도 격자간격

| 칸 | 내용 |
|---|---|
| 이름·기호 | 척도 격자간격 · \(\delta_n\) |
| 종류 | 함수 |
| 정의 | 정수 n≥1에서 δ_n:=(n+1)^(−2/3). |
| 잘 정의됨 | n+1>0. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md §4 |
| 기록별 이명 | 없음 |

## 302. 끝거리 좌표

| 칸 | 내용 |
|---|---|
| 이름·기호 | 끝거리 좌표 · \(s_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | 정수 n≥1,0≤ℓ≤n−1에서 s_(n,ℓ):=(n+1−ℓ)δ_n. |
| 잘 정의됨 | 실수 곱. 원 실제 주차 자리 s_i와 다른 두 첨자 좌표. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md §4 |
| 기록별 이명 | 없음 |

## 303. 최대 변위 점확률

| 칸 | 내용 |
|---|---|
| 이름·기호 | 최대 변위 점확률 · \(p^{PF}_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | 정수 n≥1,0≤ℓ≤n−1에서 p^PF_(n,ℓ):=b_(n,ℓ)/|PF_n|. |
| 잘 정의됨 | 목록 (1,2,…,n)이 성공하므로 |PF_n|>0. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md (S5) |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 최대 변위 점확률 p_(n,ℓ). 과거 프라임 누적 개수 이명 pₙ,ℓ와 구별한다. |

## 304. 밀도 근사 잔차

| 칸 | 내용 |
|---|---|
| 이름·기호 | 밀도 근사 잔차 · \(\varepsilon_{n,\ell}\) |
| 종류 | 함수 |
| 정의 | 정수 n≥1,0≤ℓ≤n−1에서 ε_(n,ℓ):=p^PF_(n,ℓ)−δ_n f_ν(s_(n,ℓ)). |
| 잘 정의됨 | s_(n,ℓ)>0. 작다는 가정은 정의에 포함하지 않는다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md (S5) |
| 기록별 이명 | 없음 |

## 305. 기울인 면적 최대점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 기울인 면적 최대점 · \(r_c\) |
| 종류 | 함수 |
| 정의 | 실수 c>0에서 r_c:=h_c가 (0,∞)에서 전역 최대를 이루는 유일한 점. |
| 잘 정의됨 | 존재·유일성은 tilts.md §2,4,5의 비형식 증명이다. 정의 채택은 그 증명의 수용과 별개. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/tilts.md (T2) |
| 기록별 이명 | 없음 |

## 306. 역로그 기울임 최대점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 역로그 기울임 최대점 · \(\beta_m\) |
| 종류 | 대상 |
| 정의 | β_m:=−log(r_(5/3)). |
| 잘 정의됨 | r_(5/3)>0. m의 최대점이라는 사실은 density.md (D8). |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §3. 정본의 선호 접두부 β와 다른 기호 β_m를 씀. |
| 기록별 이명 | 없음 |

## 307. 핵 비율

| 칸 | 내용 |
|---|---|
| 이름·기호 | 핵 비율 · \(R^conv_z\) |
| 종류 | 함수 |
| 정의 | 실수 z,ζ에서 R^conv_z(ζ):=𝔨(z−ζ)/𝔨(z−β_m). |
| 잘 정의됨 | 분모 양수. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md (D11) |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 핵 비율 · \(R_z\) |

## 308. 도함수 비교함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 도함수 비교함수 · \(H^conv_ν\) |
| 종류 | 함수 |
| 정의 | 실수 z에서 H^conv_ν(z):=g^conv_ν′(z)/𝔨(z−β_m). |
| 잘 정의됨 | g^conv_ν는 매끄럽고 분모 양수. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md (D11) |
| 기록별 이명 | 기록 k79ddad1bf51547cd86cce1308aac35c1의 도함수 비교함수 · \(H\) |

## 309. 합성곱 최대점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 합성곱 최대점 · \(z_*\) |
| 종류 | 대상 |
| 정의 | z_*:=H^conv_ν(z)=0을 만족하는 유일한 실수 z. |
| 잘 정의됨 | density.md §5의 존재·유일성 증명. 정의와 증명 수용은 별개. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §5 |
| 기록별 이명 | 없음 |

## 310. 극한 밀도 최대점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 극한 밀도 최대점 · \(y_*\) |
| 종류 | 대상 |
| 정의 | y_*:=exp(2z_*/3). |
| 잘 정의됨 | 양수 유한. f_ν의 최대점이라는 사실은 density.md (D13). |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/density.md §5 |
| 기록별 이명 | 없음 |

## 311. 역면적 시계

| 칸 | 내용 |
|---|---|
| 이름·기호 | 역면적 시계 · \(\tau_B\) |
| 종류 | 대상 |
| 정의 | Wiener 법칙과 독립 Exp(1) 시계 X의 곱공간에서 τ_B:=inf{t≥0:𝒜_B(t)≥X}. 잘 정의되지 않는 영확률 예외에는 0으로 확장. |
| 잘 정의됨 | scope.md §2의 양수·엄격 증가·무한대 극한으로 유일한 도달시간. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k79ddad1bf51547cd86cce1308aac35c1/scope.md (S2) |
| 기록별 이명 | 없음 |

## 312. 가장 큰 성분 크기

| 칸 | 내용 |
|---|---|
| 이름·기호 | 가장 큰 성분 크기 · L_max(G) |
| 종류 | 함수 |
| 정의 | n≥1, G∈𝔉↓ₙ에서 L_max(G):=max{t_v(G):v∈[n]}. 감소 숲의 각 성분 뿌리가 그 성분 전체를 자손으로 가지므로 가장 큰 연결 성분의 크기다. |
| 잘 정의됨 | [n]은 비어 있지 않은 유한 집합이고 t_v(G)∈[n]이다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §4.3, §7.2의 L을 이번 계획에서 명시적으로 등록. |
| 기록별 이명 | 기록 k2d51fc12f1254808a99f42f03fe5224b의 가장 큰 성분 크기 L. 연구 현황의 명제 라벨 L과 다른 대상이다. |

## 313. 숲 조건부 복제 누적함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 숲 조건부 복제 누적함수 · F_{G,r}(y) |
| 종류 | 함수 |
| 정의 | n≥1,G∈𝔉↓ₙ,r>0,y≥0에서 F_{G,r}(0):=0, y>0이면 F_{G,r}(y):=exp(−rΛ_y(G))=∏_v min(1,y/t_v(G))^r. |
| 잘 정의됨 | 양의 밑의 유한 곱. y↓0에서 0으로 수렴하고 y≥n에서 1이므로 연속 누적함수다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 kb0b4ce4e999f41b3821a41a4d3bbe87f/response.md §2. 원고의 숲별 조건부 누적확률에 별도 기호를 붙였다. 혼합 ϱ와 다르며 G를 고정한다. |
| 기록별 이명 | 없음 |

## 314. 숲 조건부 복제 행

| 칸 | 내용 |
|---|---|
| 이름·기호 | 숲 조건부 복제 행 · p_{G,ℓ}(r) |
| 종류 | 함수 |
| 정의 | n≥1,G∈𝔉↓ₙ,r>0,0≤ℓ≤n−1에서 p_{G,ℓ}(r):=F_{G,r}(ℓ+1)−F_{G,r}(ℓ). |
| 잘 정의됨 | 비감소 함수의 차분이므로 비음수, 망원합은 1이다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 kb0b4ce4e999f41b3821a41a4d3bbe87f/response.md §2. 𝔟ʳᵉᵖ는 이 행을 숲에 대해 평균한 것으로 서로 다른 대상이다. |
| 기록별 이명 | 없음 |

## 315. 시계 조건부 최대 변위 분포

| 칸 | 내용 |
|---|---|
| 이름·기호 | 시계 조건부 최대 변위 분포 · c_ℓ(τ) |
| 종류 | 함수 |
| 정의 | 고정 n≥1,τ>0,0≤ℓ≤n−1에서 c_ℓ(τ):=Tₙ⁻¹Σ_{G∈𝔉↓ₙ}(∏_v t_v(G))1{Λ_{ℓ+1}(G)≤τ<Λ_ℓ(G)}. |
| 잘 정의됨 | 유한 합. Λ₀=+∞의 경계 관례를 사용한다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 kb0b4ce4e999f41b3821a41a4d3bbe87f/response.md §2와 §5. 대상 탐구 exploration.md §4.2의 c_ℓ(τ)와 같은 대상이며 r는 1로 고정한다. |
| 기록별 이명 | 없음 |

## 316. 거듭제곱 면적 시계 변수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 면적 시계 변수 · \(Y^{\mathrm{pow}}_\alpha\) |
| 종류 | 대상 |
| 정의 | 실수 α>0에서 𝒵와 독립 Exp(1) 변수 X의 곱공간 위 Y^{pow}_α:=(X/𝒵)^{1/α}. 𝒵=0인 예외에는 0. |
| 잘 정의됨 | 𝒵>0가 거의 확실이며 α>0. α=3/2에서 대상 원고의 Yν와 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §3. 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 317. 거듭제곱 면적 시계 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 면적 시계 밀도 · \(p^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>0,y>0에서 p^{pow}_α(y):=α y^{α−1}∫₀∞ a exp(−ay^α)f_𝒵(a) da. |
| 잘 정의됨 | 본문 §3의 Tonelli·변수변환으로 위 변수의 밀도. α=3/2에서 대상 원고의 pν와 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §3 (4). 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 318. 거듭제곱 합성곱 핵

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 합성곱 핵 · \(k^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>1,u∈ℝ에서 k^{pow}_α(u):=exp((1−1/α)u−exp(u)). |
| 잘 정의됨 | 양수 유한. α=3/2에서 대상 원고의 k와 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §4 (5). 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 319. 거듭제곱 역로그 면적 기울임

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 역로그 면적 기울임 · \(m^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>1,ζ∈ℝ에서 m^{pow}_α(ζ):=exp(−(1+1/α)ζ)f_𝒵(exp(−ζ)). |
| 잘 정의됨 | 최댓값 면적 밀도 f_𝒵를 사용. α=3/2에서 역로그 면적 기울임 m과 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §4 (5). 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 320. 거듭제곱 합성곱 함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 합성곱 함수 · \(g^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>1,z∈ℝ에서 g^{pow}_α(z):=∫ℝ k^{pow}_α(z−ζ)m^{pow}_α(ζ)dζ. |
| 잘 정의됨 | 핵 유계·기울임 L¹로 절대수렴. α=3/2에서 대상 원고의 g와 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §4 (5). 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 321. 거듭제곱 역로그 최대점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 역로그 최대점 · \(\beta^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>1에서 β^{pow}_α:=−log r_{1+1/α}. 여기서 r_c는 대상 원고의 기울인 면적 최대점. |
| 잘 정의됨 | 본문 §2에서 존재·유일성을 다시 논증. α=3/2에서 대상 원고의 β_m과 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §4 (7) 앞. 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 322. 거듭제곱 도함수 비교함수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 거듭제곱 도함수 비교함수 · \(H^{\mathrm{pow}}_\alpha\) |
| 종류 | 함수 |
| 정의 | 실수 α>1,z∈ℝ에서 H^{pow}_α(z):=(g^{pow}_α)′(z)/k^{pow}_α(z−β^{pow}_α). |
| 잘 정의됨 | 분모 양수·합성곱 매끄러움. α=3/2에서 대상 원고의 H와 같다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k897ef751296e4645b92f7c47695977cd/response.md §4 (8) 앞. 원고의 특수값 정의를 확장한 동료의 정의. |
| 기록별 이명 | 없음 |

## 323. 경로 역면적 시계 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 경로 역면적 시계 밀도 · φ_B(t) |
| 종류 | 함수 |
| 정의 | 연속 브라운 경로 B와 t>0에서 φ_B(t):=S_B(t)exp(−𝒜_B(t)). |
| 잘 정의됨 | 앞에 정의한 함수의 합성·곱이다. 조건부 밀도로서의 정규화와 주장 범위는 검토 ke330047776da47ba92abe22d49ec3865/work-path-components 및 review.md §3. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §5.4–5.6. 원 제안 누락을 이번 계획에서 처리. |
| 기록별 이명 | 기록 k2d51fc12f1254808a99f42f03fe5224b의 φ_B. 이후에는 이 정본 이름·기호를 사용. |

## 324. 시계 고정 극한 밀도

| 칸 | 내용 |
|---|---|
| 이름·기호 | 시계 고정 극한 밀도 · p^clk_τ(y) |
| 종류 | 함수 |
| 정의 | 실수 τ>0,y>0에서 p^clk_τ(y):=(3/2)τ^(−2/3)h_(5/3)(τ y^(−3/2)). |
| 잘 정의됨 | 앞에 정의한 함수의 합성·곱이다. 조건부 밀도로서의 정규화와 주장 범위는 검토 ke330047776da47ba92abe22d49ec3865/work-path-components 및 review.md §3. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k2d51fc12f1254808a99f42f03fe5224b/exploration.md §5.4–5.6. 원 제안 누락을 이번 계획에서 처리. |
| 기록별 이명 | 기록 k2d51fc12f1254808a99f42f03fe5224b의 p_τ. 이후에는 이 정본 이름·기호를 사용. |

## 325. 복제 비정규화 누적합

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 비정규화 누적합 · \(W^{\rm rep}_n(y,r)\) |
| 종류 | 함수 |
| 정의 | n≥1,y>0,r>0에서 \(W^{\rm rep}_n(y,r):=\sum_{G\in\mathfrak F_n^\downarrow}\prod_vt_v^{1-r}\min(t_v,y)^r\). 재귀용 n=0,y>0 값은 1, n≥1,y=0 값은 0. |
| 잘 정의됨 | 유한 합과 양의 밑의 실수 거듭제곱. n≥1,y>0에서 \(W^{\rm rep}_n=T_n\varrho_n\). |
| Lean 대응 | 미형식화. 자연수 가중치 제한의 기존 Eval_w 형식 결과와 구별한다. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §2 (1)–(3) |
| 기록별 이명 | |

## 326. 복제 뿌리 인수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 뿌리 인수 · \(w_{y,r}(s)\) |
| 종류 | 함수 |
| 정의 | y>0,r>0,s∈ℕ에서 s=0이면 0, s≥1이면 \(w_{y,r}(s):=s^{1-r}\min(s,y)^r\). |
| 잘 정의됨 | s=0을 별도 정의하여 음의 실수 지수의 0 밑을 사용하지 않는다. |
| Lean 대응 | 미형식화. 정본 Eval_w의 특수 입력이다. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §2 (3) 직전 |
| 기록별 이명 | |

## 327. 복제 인접 차

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 인접 차 · \(D^{\rm rep}_{n,\ell}(r)\) |
| 종류 | 함수 |
| 정의 | n≥2,r>0,0≤ℓ≤n−2에서 \(D^{\rm rep}_{n,\ell}(r):=T_n(\mathfrak b^{\rm rep}_{n,\ell+1}(r)-\mathfrak b^{\rm rep}_{n,\ell}(r))\). |
| 잘 정의됨 | 실수 차. ℓ≥1,r=1에서 원 Δ와 같고, ℓ=0에서는 \(b_{n,1}-b_{n,0}\). 원 Δₙ,₀를 정의하지 않는다. |
| Lean 대응 | 원 숲 함수 전체는 미형식화. `ReplicaShape`의 볼록성 정리가 마지막 차의 인수화 뒤 적용된다. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §5 (8) |
| 기록별 이명 | |

## 328. 복제 마지막 차 볼록화

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 마지막 차 볼록화 · \(H_n(r)\) |
| 종류 | 함수 |
| 정의 | n≥3,r∈ℝ에서 c=(n−1)/n,b=(n−2)/(n−1),h=c^{n−2},d=b/c를 국소 약칭으로 두고 \(H_n(r):=(1-h)c^{-r}-2+(1-h)b^r+hd^r+hb^{2r}\). |
| 잘 정의됨 | 모든 밑이 양수. r>0에서 \(D^{\rm rep}_{n,n-2}(r)=n^{n-1}c^rH_n(r)\)는 exposition.md §5의 별도 비형식 정리다. |
| Lean 대응 | `ReplicaShape.tailConvex h A B C r`에 A=−log c,B=log b,C=log d 대입. `tailConvex_strict`는 추상 매개변수의 엄격 볼록성이다. 숲 동일성은 미형식화. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §5 (11), 기록 k46d25e2fa94842ba880225ee0a0666b9/lean/Shape.lean |
| 기록별 이명 | |

## 329. 복제 마지막 차 영점

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 마지막 차 영점 · \(\rho_n\) |
| 종류 | 함수 |
| 정의 | n≥3에서 \(\rho_n:=\) \(D^{\rm rep}_{n,n-2}(r)=0\)을 만족하는 유일한 양의 실수 r. |
| 잘 정의됨 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §5 (10)–(11)의 연속성·엄격 볼록성·양끝 부호 논증. 계획이 원문을 대조했으며 묶음 검토 kb60d0f9d760c4878b61f88cdef869a3c/work-last-comparison-single-crossing에서 비형식 supported다. 항상 ρₙ>1이다. |
| Lean 대응 | `strictConvex_unique_positive_root`는 일반 함수의 충분조건 아래 존재·부호를 증명한다. 원 숲 함수의 존재 선택과 식별은 미형식화. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §5 (10) |
| 기록별 이명 | |

## 330. 복제 마지막 차 영점 척도 상수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 마지막 차 영점 척도 상수 · \(s_*\) |
| 종류 | 대상 |
| 정의 | \(h_*=e^{-1}\)을 국소 약칭으로 두고 \(s_*:=-\log\frac{2(1-h_*)}{1+\sqrt{1+4h_*(1-h_*)}}\). |
| 잘 정의됨 | 로그 밑은 (0,1)에 속한다. exposition.md §5의 이차 다항식에서 확인한다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §5 (13) |
| 기록별 이명 | |

## 331. 복제 차의 이중 누적 핵

| 칸 | 내용 |
|---|---|
| 이름·기호 | 복제 차의 이중 누적 핵 · \(K^{\rm rep}_{n,\ell}(t)\) |
| 종류 | 함수 |
| 정의 | n≥2,0≤ℓ≤n−2,t≥0에서 ℓ≥1이면 K^{rep}_{n,ℓ}(t):=Σ_{G∈𝔉↓ₙ}(∏_v t_v(G))[max(0,t−Λ_{ℓ+2}(G))−2max(0,t−Λ_{ℓ+1}(G))+max(0,t−Λ_ℓ(G))]. ℓ=0이면 마지막 max 항을 0으로 대체한다. |
| 잘 정의됨 | 유한합이다. 원 연구 §6의 같은 유리수 밑 병합 전개와 동일하며 전개 선택에 의존하지 않는다. Laplace 적분 동일성과 교차 성질은 별도 결과다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k46d25e2fa94842ba880225ee0a0666b9/exposition.md §6 (14)–(17) |
| 기록별 이명 | |

## 332. 크기 2 이하 성분 숲 총무게

| 칸 | 내용 |
|---|---|
| 이름·기호 | 크기 2 이하 성분 숲 총무게 · 𝓑_m |
| 종류 | 함수 |
| 정의 | m∈ℕ에서 𝓑_m:=Σ_{G∈𝔉↓_m, 모든 v에 t_v(G)≤2}∏_v t_v(G). 빈 숲의 곱은 1이다. |
| 잘 정의됨 | 유한합이다. response.md §2에서 𝓑_m=Σ_{j=0}^{⌊m/2⌋}m!/((m−2j)!j!)를 증명한다. |
| Lean 대응 | 미형식화 |
| 출처 | 기록 k18d51110f43e4d8b926f7ea6c8a4dfd3/response.md §2 식 (1). 일반 숲 가중합을 특정 가중치로 평가한 특수 경우다. |
| 기록별 이명 | |


## 333. 갱신 핵

| 칸 | 내용 |
|---|---|
| 이름·기호 | 갱신 핵 · $u^{\rm ren}_r$ |
| 종류 | 함수 |
| 정의 | 정수 r≥1에서 $u^{\rm ren}_r:=e^{-r}r^r/r!$. 차분·급수 계산의 보조 확장으로 $u^{\rm ren}_r:=0$ (r≤0). |
| 잘 정의됨 | 양의 계승으로 나눈 명시식이다. Borel 계수의 갱신 합과의 동일성은 exposition.md (6)에서 증명한다. |
| Lean 대응 | 실제 이 수열은 미형식화. Boundary.lean은 그 비율 가정을 받는 국소 대수만 다룬다. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md (5)–(6). |
| 기록별 이명 | |

## 334. 갱신 정규화 전체 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 갱신 정규화 전체 계수 · $g^{\rm ren}_j$ |
| 종류 | 함수 |
| 정의 | 정수 j≥0에서 $g^{\rm ren}_j:=e^{-j}T_j/(j+1)!$. |
| 잘 정의됨 | 정본 T_0=1과 전체 개수 T_j를 사용하며 분모 양수다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md (5). |
| 기록별 이명 | |

## 335. 끝거리 누적확률

| 칸 | 내용 |
|---|---|
| 이름·기호 | 끝거리 누적확률 · $\mathsf C_N(m)$ |
| 종류 | 함수 |
| 정의 | 정수 N≥3과 정수 0≤m≤⌊N/2⌋에서 $\mathsf C_N(m):=A_{N-1,N-m-2}/T_{N-1}$. 뒤 차분의 보조 확장으로 m<0에서 1. |
| 잘 정의됨 | 원 문턱 N−m−2≥0이고 T_(N−1)>0이다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md §3. |
| 기록별 이명 | |

## 336. 갱신 교대층

| 칸 | 내용 |
|---|---|
| 이름·기호 | 갱신 교대층 · $\mathsf V_{N,k}(m)$ |
| 종류 | 함수 |
| 정의 | 정수 N≥3, 정수 0≤m≤⌊N/2⌋, 정수 k≥1에서, 양의 정수 r_1,…,r_k의 부분합 R_i:=Σ_{j=1}^i r_j와 R_0=0에 대해 $\mathsf V_{N,k}(m):=\sum_{R_k\le m}(g^{\rm ren}_{N-1-R_k}/g^{\rm ren}_{N-1})\prod_{i=1}^k[u^{\rm ren}_{r_i}(m-R_i+1)/(N-R_{i-1})]$. k≥1,m<0에서는 0. k=0에서는 모든 해당 m에 1. |
| 잘 정의됨 | 유한 합이며 모든 분모 양수다. 끝거리 누적확률과의 교대합 관계는 별도 정리다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md (8)–(9). |
| 기록별 이명 | |

## 337. 균질 갱신층

| 칸 | 내용 |
|---|---|
| 이름·기호 | 균질 갱신층 · $\mathsf B_k(m)$ |
| 종류 | 함수 |
| 정의 | 정수 k≥0,m에 대해 $\mathsf B_0(m):=1$; k≥1,m<0에서 0; k≥1,m≥0에서 $\mathsf B_k(m):=\sum_{j=0}^{m-1}u^{\rm ren}_{m-j}(j+1)\mathsf B_{k-1}(j)$. |
| 잘 정의됨 | k와 m의 유한 귀납으로 유일하다. m<k에서 0이다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md (10). |
| 기록별 이명 | |

## 338. 갱신층 계수

| 칸 | 내용 |
|---|---|
| 이름·기호 | 갱신층 계수 · $\gamma_k^{\rm ren}$ |
| 종류 | 함수 |
| 정의 | 정수 k≥0에서 $\gamma_k^{\rm ren}:=\prod_{j=0}^{k-1}(1+3j/2)$, 빈 곱은 1. |
| 잘 정의됨 | 유한 양수 곱이다. |
| Lean 대응 | 미형식화. |
| 출처 | 기록 k4b37ac60c05b499ab584ccb775bc7267 exposition.md (12), finite-differences.md (D20),(D25). |
| 기록별 이명 | |
