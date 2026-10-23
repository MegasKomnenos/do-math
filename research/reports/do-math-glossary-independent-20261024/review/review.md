# 용어 정본 300항목과 새 표시 급수의 독립 검토

대상은 k4a876a6088f14bf090cb7da8b6e40a37의 세 결과다. `glossary-snapshot`은 **not_supported**, `series-coefficients`와 `original-lower-bound`는 **supported / accepted / matches**로 판정한다. 정본의 조건 누락과 형식 대응 설명의 결함이 새 Lean 증명을 무효화하지는 않는다. 전체 P나 분자 계수의 전칭 비음수성은 수용하지 않는다.

## 실제 확인 범위

입력의 common·protocol·review·goal·settings·task를 읽었다. 시작 색인이 지정한 최신 정본은 k4dfeca2d4d014a23877e5aaa8f5cf457/glossary.md다. 대상이 적용했다고 밝힌 판본은 k183b91f20f754fb6a4b9e34936038adf이며, 이번에는 그 연구가 공개한 고정 사본을 판정한다. 최신 정본과 대상 사본의 본문 차이는 없었다(`latest-snapshot-diff.txt`). 이전 인스턴스·로컬 수학 기억·작성자 비공개 세션을 사용하지 않았다. 추가 파견·STOP 변경은 없다.

대상의 glossary.md 일곱 칸 전체 300항목, glossary-relations.md, exposition.md, verification.md를 읽었다. 원 정의 제안 43기록의 정의를 실제 대조했고, 기존 형식 대응에 인용된 독립 검토 29기록의 결과별 판정·정합성 범위와 필요한 선언 타입을 대조했다. 증명 연결이 중요한 곳은 원 Parking, Forest/CanonicalForest, MarkedComponents/MarkedLower/InteriorLower, ChainPositivity/CanonicalBridge, BranchAlignment 및 후속 Replica/Largest 원문으로 내려갔다. §68–70은 원 문헌 조사 exposition.md §4.4와 추가 검토의 블록·발생 번호 설명으로 대조했다.

[항목별 기록](entry-review.md)은 300개 번호마다 근거와 수학 메모·발견 사항을 담는다. [JSON 기록](entry-audit.json)은 대상 줄 번호와 기존 형식 판정의 근거 기록도 담는다. [번호 대조](coverage.json)의 누락은 0개다. 이는 1…338 전부가 아니라 현행 300개를 뜻한다. 삭제된 번호는 재사용되지 않았다. 기계 추출 보조자료 `source-definition-excerpts.txt`, `declaration-signatures.txt`, `existing-review-decisions.txt`는 원문 탐색을 재현하는 자료이며, 그 존재나 문자열 일치로 수학적 수용을 결정하지 않았다. 선언 추출에는 정의 본문을 생략한 조각도 있으므로 완전한 Lean 타입의 대용으로 사용하지 않는다.

모든 기존 연구 정리의 증명을 새로 작성하거나 기존 Lean 전체를 다시 컴파일하지는 않았다. 기존 미형식화 자체도 결함으로 세지 않았다. 외부 논문 전체를 이번에 다시 확보해 전사 대조한 검토는 아니다. 문헌 항목에서는 이 인스턴스의 공개 원 연구·검토가 실제 확인한 문면·영역·정규화를 정본이 보존하는지 판정했다. 새 두 파일은 아래처럼 직접 재컴파일·공리 감사했다. 항목 독해의 남은 번호 범위는 없으며, 이보다 강한 기존 결과 전체의 재인증은 이번 판정에 포함되지 않는다.

## 수정이 필요한 곳

**F1 — §199 잘 정의됨: 대각 조건 누락.** 일반 정의의 매개변수는 n≥0,x≥1,c≥0인데, 현재 설명은 “Tₙ−ℒₙ,ₓ₋₁ 동일성”이라고만 쓴다. 원 근거 k526e621123a64cee8d48c8b3c7c79a04/exposition.md §8 식 (23)은 정확히

\[
\widehat W^{cmp}_n(x;x)=T_n-\mathcal L_{n,x-1}\qquad(n,x\ge1)
\]

이다. c가 임의인 동일성이 아니다. n=2,x=1에서 일반 라벨 숲은 세 개다. 빈 표시가 3을 주고 두 방향 사슬의 뿌리 표시가 각각 c/2−1을 주므로 Ŵᶜᵐᵖ₂(1;c)=1+c다. T₂−ℒ₂,₀=3−1=2인 반면 c=2에서는 왼쪽이 3이다. 따라서 재사용에 필요한 c=x와 원 진술의 n≥1을 적어야 한다. n=0도 양변1임은 빈 합으로 별도 확장 가능하다. 원 연구 결과가 틀렸다는 지적이 아니라 정본의 조건 누락이다.

**F2 — §201 현재 형식 대응: 실제 숲 합과 경계 대수식 사이 보증을 구분해야 한다.** k41df00b303bc4da78d9d610e8bcf85ae/lean/BranchAlignment.lean의 evenBranch_grouped·oddBranch_grouped는 원 T로 정의한 유리수 경계식과 묶인 이항계수 식의 동일성이다. 타입에는 일반 라벨 숲·표시 집합·실제 ℬⁱⁿᶜ 합이 없다. 독립 검토 k1f431a6ad115453aaebaecc30aa9445b/review.md §4도 일반 숲 보정 전체의 형식화를 주장하지 않는다고 명시한다. ℬ의 숲 합을 두 닫힌 식에 연결하는 조합 논증은 k526의 §7 식 (17)–(21) 및 검토 k34fb712e85cd44ec8192ca96eb115da1의 비형식 범위다. 현재 칸의 “정본 함수의 두 경계 대입값을 다룬다 … accepted/matches”만으로는 이 연결이 형식 수용된 것처럼 읽힌다. 정확한 대입은 x=q−1,c=x,n=2q 또는2q+1,q≥2다. 일반 숲 합의 Lean 식별은 없고, 그 식별 뒤 사용하는 경계 대수식만 accepted/matches라고 밝혀야 한다. 기존 경계 정리의 수용을 거부하는 판정은 아니다.

**F3 — 현행 구현 누락.** §11의 “일반 실수 값 구현은 없다”, §198의 “비음수 실수 … Lean 연결은 별도”, §325–327의 “미형식화”는 현재 공개된 kb383160bb81746ce99bd620a97ee8da9/lean/ScalarForest.lean·Replica.lean을 반영하지 않는다. parentSum_nnreal, rootWeight, W, D, Unimodal과 W_one/rowCount_one/D_one_delta가 실제 공개되어 있다. §36에도 후속 D_one_delta 연결이 있고, §312의 최댓값 표현은 ka1754fb43f214d76ae4cd96762da033f/lean/Largest.lean의 mass 안에 구현되어 있다. 단, 이 두 후속 연구는 독립 검토 전이므로 accepted로 올리면 안 된다. “기존 수용 범위는 자연수이며, 다음 공개 구현은 미검토”로 보완한다. ϱ와 정규화 복제 행은 W/T 관계를 이용하는 별도 식별이 필요하므로, 그 함수 전부가 새로 형식 인증되었다고 적지 않는다. 이 검토는 해당 후속 연구를 재컴파일하거나 대신 수용한 것이 아니다.

**F4 — 칸 배치.** §137 관련 표현 끝의 “명시적 사슬 합의 일반 Lean 연결은 남는다”는 현재 형식 대응으로 옮긴다. §222 현재 형식 대응의 m≥ceil(q/2)에서 𝔅ᵖᵃⁱʳ/q⁴와 같다는 수학적 관계는 관련 표현으로 옮기고 형식 칸에는 미형식화를 남긴다. 수학적 오류와 구별되는 편집 결함이다.

**F5 — 통합을 검토할 수 있는 제한형.** §121과 §162는 같은 유한합의 q≥2 제한과 q≥1 확장이고, §16은 §153의 n=18 제한이다. 별도 함수의 영역을 유지한 것이므로 그 자체를 의미 위반으로 판정하지 않는다. 공용 이름 수를 더 줄이려면 넓은 정의 하나와 제한식으로 정리할 수 있다. 반대로 §134·135는 제한 밖에서 다르므로 합치면 안 된다. 아래 검산도 그 차이를 확인한다. F5는 선택적 편집 제안이며 수학적 거부 사유가 아니다.

구체적 대체 문구는 [수정안](proposed-edits.md)에 있다. 원 공개 기록은 수정하지 않았다. 같은 대상에 대한 선행 독립 검토는 없었으며 supersedes=[]이다. F1·F2는 기존 원 연구의 정리나 검토 판정 자체가 틀렸다는 주장이 아니다.

## 가족별 의미·영역 검토

원 PF·A·b·M·M̄는 서로의 빈 경계를 덮어쓰지 않는다. M은 양수 크기에서만, b도 양수 크기에서만 정의되고, A₀,ℓ=1과 Aₙ,−1=0은 서로 다른 경계다. Nat의 변위 차는 pref_le_slot에 의해 정수 차와 같다. 최종 차분은 정수 또는 유리수에서 취한다. 유한 표의 n<15,ℓ<14 및 n<19,ℓ<18 범위를 전칭 계산기로 확대하지 않았다.

숲 F의 작은 인자·큰 크기 수 a·정확 적중 수 e를 구분했다. 한 숲 항은 w^< U^aY^e이고 표시 다항식은 F(qz,qv)다. 따라서 p차 U 미분에는 q^p/p! 인자가 붙는다. 정확 e=2 부분나무의 서로소성은 a+qe≤n을 주며, n≤2q+1의 e≤2,a≤1 제한과 n<3q의 e≤2 제한을 혼용하지 않았다. Jᵃᵉʰ의 m<2q는 F의 전역 정의역과 다르다. Γ와 전진 곡률·적중 보정도 각기 다른 문턱을 유지한다.

순열의 최대 원소가 위치 k+1이면 폭은 k+1, 왼쪽과 오른쪽 폭은 표준화 후 보존된다. 감소 숲의 최대 라벨 성분에서 뿌리를 지우는 분해도 같은 이항계수·근 인자·두 작은 합을 준다. 초기값1과 크기 귀납으로 일반 근 가중치의 두 합이 같다. w(t)=t(t<q),qv(t=q),qu(t>q)를 대입하면 F(qu,qv)가 된다. 따라서 §110을 순열 정의로 남기면서 §118–120을 F에서 정의한 것은 수학적 의미를 잃지 않는다. 직접 순열 합과 과거 atoms 목록의 일반 Lean 동일성까지 새로 확보한 것으로 읽지 않는다.

B와 J는 k,n≥0,n≤2k+1에서 같다. k=0도 실제 ChainPositivity.actualBase_eq_smallCount의 영역이다. B의 합에서 r=s+1로 바꾸고 rT_(r−1)=r^(r−1)를 쓰면 원 사슬 기저의 유한합과 같다. §98·134를 §85 앞에 둔 순서도 맞다. k=1,n=4에서 B=−11,J=1이므로 전역 통합은 틀리다.

복제 함수의 확률·개수·숲별 조건부 법칙에서는 T 인자를 빠뜨리지 않았다. (n,y)=(0,0)을 정본에서 지정하지 않은 것과 구현의 보조 확장을 구별한다. ℓ=0의 복제 인접 차는 bₙ,₁−bₙ,₀이며 원 Δₙ,₀를 새로 도입하지 않는다. 브라운 면적, 그 법칙 ν, 한 실현 변수 Yν, 경로 시계 τB를 같은 객체로 합치지 않는다. 고정 시계 밀도는 a=τy^(−3/2) 변수변환으로 (3/2)τ^(−2/3)h_(5/3)(a)가 되어 정규화 인자가 맞다. 잔차 정의에는 작은 오차라는 가정을 넣지 않았다. 갱신층 §336·337의 β 인수는 모두 양수여서 제거된 갱신 핵의 0 이하 보조 관례를 요구하지 않는다.

## 새 급수 계수와 원 하계의 직접 검증

공개 두 파일과 의존 원문19개를 [lean/](lean/)에 바이트 동일하게 복사했다. 설정의 lake env lean, Mathlib cwd와 PATH를 사용했다. [실행 근거](execution-evidence.json)는 판본·환경·해시를, [모듈별 명령](independent-lean/execution.json)은 실제 argv·cwd·종료 코드를 기록한다. 21모듈 모두 종료0이다. 원문에 있는 #print axioms를 실제 실행하여 새 정리9개와 급수 정의4개, 합계13개 모두 [propext, Classical.choice, Quot.sound]만 출력했다. [공리 목록](independent-lean/axioms.json), [GlossaryRepair 로그](independent-lean/logs/GlossaryRepair.log), [SeriesRepair 로그](independent-lean/logs/SeriesRepair.log)를 공개한다. 스타일 linter 경고는 있으나 sorryAx나 새 공리는 없다. 현재 Lean은 4.32.0, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35다.

네 급수의 n번째 지수계수는 각각

\[
q^a\partial_U^aF(q,q),\quad F(q-1,q),\quad q\partial_YF(q-1,q),\quad
q^2\{\partial_U^2F(q,q)-\partial_YF(q-1,q)\}
\]

이며 ordinary coefficient에는 1/n!이 붙는다. marked_coeff·dampedValue_coeff·damped_coeff·numerator_coeff의 타입과 일치한다. 정본의 q≥2,a∈{1,2}에서는 평가점이 자연수라 ℕ 다항식 평가 후 ℚ 포함과 일치한다. n=0이면 F=1이라 네 지수계수는 0,1,0,0이다. 구현 정리는 모든 자연수 q,a에도 성립하지만 q−1은 **Nat 뺄셈**이다. 예컨대 q=0을 대입한 구현을 음수 −1에서 평가한 유리수 다항식으로 해석하면 안 된다. 정본의 q≥2 영역은 이 차이를 피한다.

GlossaryRepair.power_gap_le_derivative는 q∈ℤ,q≥1,e∈ℕ에서 q^e−(q−1)^e≤e q^(e−1)를 증명한다. e=0의 오른쪽은 계수0이므로0이다. 각 숲 항에 비음수 B(q−1)^a를 곱해 합하면 정확 Y 손실≤∂YF(q−1,q). 기존 original_delta_finite_loss_lower의 “이득−정확 손실≤Δ”에서 손실을 더 큰 값으로 바꾸면 하계가 낮아진다. 이것이 original_delta_F_restored다.

numerator_coeff_original_lower의 n,ℓ:ℕ+와 q=ℓ+1은 정확히 n≥1,q≥2 전부를 덮는다. n!과 q²는 양수이고, 원 Parking.b 두 값을 먼저 ℚ로 올린 뒤 뺀다. 따라서

\[
\frac{n!}{q^2}[x^n]\mathcal X_q\le b_{n,q}-b_{n,q-1}.
\]

좌변 계수≥0을 **가정**하는 original_increase_of_numerator_coeff의 결론이 원 bₙ,q−1≤bₙ,q다. q≥n도 제외하지 않으며, 하계 자체의 부호를 증명하지 않는다. 의존 원 Parking.b는 실제 성공 목록의 최대 변위 필터 개수이고, 재귀로 새로 정의한 수열이 아니다. 원 Parking.next의 최소 후보 선택과 run의 List.ofFn 도착 순서를 직접 읽었다. 정리 의존 사슬의 재컴파일·전이적 공리 확인은 이 원 연결도 포함한다.

[독립 계산](independent_checks.py)은 작성자 모듈을 import하지 않는다. n=1…6 원 선호 목록 전수의 b행을 구하고, n=0…7,q=1…5 순열과 실제 부모 함수 숲의 표시 계수 전체 40쌍을 비교했다. q=1은 보조 계산이며 정본 F 영역 확장이 아니다. n=1…6,q=2…5의 24쌍에서 세 A 평가, 정확 손실 상계와 새 하계도 확인했다. B/J 제한영역110쌍 및 F1의 반례를 별도 확인했다. 결과는 [independent-checks.json](independent-checks.json)에 있다. 이는 전칭 증명을 대신하지 않는다.

재현은 세션 폴더에서 `python output/verify_lean.py --settings <instance>/settings.json --work <이 세션 안의 새 경로>`와 `python output/independent_checks.py`로 가능하다. 첫 스크립트는 공개 재현 코드의 읽고 확인한 사본이다. 기존 실행 로그를 읽는 것에 그치지 않고 이번에 다시 실행했다.

## 최종 범위

소개는 검토 전인 고정 검토 대상을 공개한다는 설명이고, 전체 의미 보존의 독립 판정이 아직 없음을 명시한다. 따라서 소개는 supported다. 정본 편집 결과는 F1·F2 등의 수정이 필요하여 not_supported이고, 두 새 형식 결과는 주장된 범위에서 수용한다. 세 결과의 terminology는 conforms다. 발견한 문제는 새 이름이나 원 객체의 조용한 재정의가 아니라 조건·보증·현재 구현 설명의 문제다. 원문 미형식화, 아직 남은 분자 부호·전체 P는 별도로 남긴다. 원 연구의 failed_attempts는 비어 있으며 open_questions의 두 미해결 범위를 새 Lean이 닫지 않는 것도 확인했다.
