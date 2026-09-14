# P 대 NP 문제의 정본 명제와 선행연구

> 보존 자료: 2026-09-14 연구 초기화 이전의 입력·배경이다. 새 연구의 활성 계약이나 재개 지시가 아니며, 현재 상태는 `research/README.md`를 따른다. 본문의 실행 경로와 상태는 당시 기록이다.

## 결론

연구 대상의 정본 명제는 `P = NP`인지 판정하는 일이다. 여기서 `P`는 결정론적 다항시간 Turing machine이 판정하는 언어의 계급이다. `NP`는 다항 길이 증명서를 결정론적 다항시간에 검증할 수 있는 언어의 계급이다. 따라서 문제는 모든 다항시간 비결정론적 계산을 다항시간 결정론적 계산으로 바꿀 수 있는지 묻는다. 이 문서는 2026-08-25를 기준일로 한다. Clay Mathematics Institute(CMI)는 현재 `P vs NP`를 `Unsolved` 아래에 둔다. 그러므로 수용된 `P = NP` 증명이나 `P ≠ NP` 증명은 이 기준일에 확인되지 않는다. [CMI 현행 문제 페이지](https://www.claymath.org/millennium/p-vs-np/), [CMI 현행 Millennium Prize Problems 목록](https://www.claymath.org/millennium-problems/).

이 문서는 고전적 이산 계산복잡도 정식화만 연구 대상으로 둔다. 복소수 위의 BSS 기계, 양자 계산, 평균 경우 복잡도, 무작위 알고리즘의 동명 또는 유사 문제는 이 명제와 다른 계산 모형 또는 다른 자원 측정값을 쓴다. Cook의 공식 문제 설명도 복소수 모형의 별도 질문을 고전적 질문과 구별한다. [Stephen Cook, 공식 문제 설명, 6쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

## 1. 정본 명제, 기호, 정의와 전제

### 1.1 정본 명제

Cook의 공식 문제 설명은 다음 명제를 정본으로 둔다. 어떤 언어를 다항시간 비결정론적 알고리즘이 받아들이면, 그 언어를 다항시간 결정론적 알고리즘도 받아들이는가. 동치인 기호 명제는 다음과 같다. [Cook, 공식 문제 설명, 1쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

\[
\boxed{P=NP\;?}
\]

`P ⊆ NP`는 증명되어 있다. 따라서 연구가 판정할 내용은 `NP ⊆ P`다. `P ≠ NP`를 보이려면 `NP` 안의 언어 하나가 `P`에 없음을 보여야 한다. [Cook, 공식 문제 설명, 2쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

### 1.2 언어와 결정론적 다항시간

`Σ`는 원소가 둘 이상인 고정 유한 알파벳이다. `Σ*`는 `Σ` 위 유한 문자열의 집합이다. 언어 `L`은 `Σ*`의 부분집합이며, 결정 문제의 YES 입력을 모은 집합으로 읽는다. 이 문서에서 시간은 입력 길이 `n`에 대한 최악 경우 단계 수다. [Cook, 공식 문제 설명, 1쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

결정론적 Turing machine `M`의 입력 `w` 실행 시간이 `t_M(w)`일 때, 최악 경우 시간은 `T_M(n)=max{t_M(w) : w∈Σ^n}`다. 어떤 상수 `k`가 있어 모든 `n`에 `T_M(n) ≤ n^k+k`이면 `M`은 다항시간에 실행한다. `L(M)`은 `M`이 받아들이는 언어다. 따라서

\[
P=\{L\mid L=L(M)\text{ 이고 어떤 결정론적 Turing machine }M\text{이 다항시간에 실행한다}\}.
\]

단일 테이프 Turing machine을 정본 정의에 써도, 다중 테이프와 무한 random-access memory 같은 표준 모형은 다항식 시간 증가로 시뮬레이션된다. 그러므로 이 명제의 `P`는 그 표준 모형들 사이에서 견고하다. 이는 임의의 계산 모형이나 양자 모형까지 같은 뜻이라는 주장이 아니다. [Cook, 공식 문제 설명, 1쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

### 1.3 `NP`와 검증자 정의

`R(w,y)`는 입력 문자열 `w`와 증명서 `y`의 이항 관계다. `R`가 다항시간 관계라는 말은 `w#y`를 부호화한 언어가 `P`에 속한다는 뜻이다. 언어 `L`이 `NP`에 속한다는 조건은 어떤 상수 `k`와 다항시간 관계 `R`가 있어 모든 `w`에 대해 다음 식이 성립하는 것이다.

\[
w∈L \Longleftrightarrow \exists y\;\bigl(|y|\le |w|^k\ \land\ R(w,y)\bigr).
\]

따라서

\[
NP=\{L\mid L\text{ 이 위 조건을 만족한다}\}.
\]

`y`는 YES 입력에만 존재해야 한다. 검증자 `R`는 `w`와 `y`가 주어지면 결정론적으로 다항시간에 참과 거짓을 판정한다. 이 검증자 정의는 다항시간 비결정론적 Turing machine 정의와 동치다. `NP`의 `N`은 “non-deterministic”의 약자이며, “non-polynomial”의 약자가 아니다. [Cook, 공식 문제 설명, 1–2쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

### 1.4 환원과 NP-complete

언어 `L_1⊆Σ_1*`와 `L_2⊆Σ_2*`에 대해 `L_1 ≤_p L_2`는 다항시간 계산 가능 함수 `f:Σ_1*→Σ_2*`가 존재하여 모든 `x`에 대해 `x∈L_1 ⇔ f(x)∈L_2`를 만족한다는 뜻이다. 이는 다항시간 many-one 환원 또는 Karp 환원이다. `f(x)` 하나만 만들고 `L_2`를 한 번 판정하므로, 여러 질의를 허용하는 Turing 환원과 다르다. [Cook, 공식 문제 설명, 4쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), [Richard Karp, *Reducibility among Combinatorial Problems* (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9).

언어 `C`가 `NP-complete`라는 말은 `C∈NP`이고 모든 `L∈NP`에 대해 `L≤_p C`라는 뜻이다. `NP-hard`는 이 정의에서 `C∈NP` 조건을 뺀 말이다. 연구 문서와 증명에서는 어떤 환원을 썼는지 밝혀야 한다. Stephen Cook의 1971년 원 논문은 다항시간 oracle 또는 Turing 환원을 썼다. 현대의 `NP-complete` 표준 정의와 Karp의 21개 문제 결과는 다항시간 many-one 환원을 쓴다. [Cook, 공식 문제 설명, 3–4쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), [Stephen Cook, *The Complexity of Theorem-Proving Procedures* (1971)](https://doi.org/10.1145/800157.805047), [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9).

## 2. 주요 동치 명제와 동치의 범위

아래 동치는 모두 유한 문자열 언어, 결정론적 Turing machine의 다항시간, 다항시간 many-one 환원을 사용한다. `SAT`는 입력 명제 논리식이 만족 가능함을 판정하는 언어다. `3-SAT`는 각 절이 세 리터럴인 CNF 식의 만족 가능성을 판정하는 언어다.

1. `P=NP`.
2. `SAT∈P`.
3. `3-SAT∈P`.
4. 어떤 `NP-complete` 언어 `C`가 `P`에 속한다.
5. 모든 `NP-complete` 언어가 `P`에 속한다.

`SAT`와 `3-SAT`가 `NP-complete`이므로 2와 3은 1과 동치다. 4에서는 `C∈NP`와 모든 `L∈NP`의 `L≤_p C`를 사용한다. `C`의 다항시간 판정기 뒤에 환원 `f`를 합성하면 모든 `L∈NP`가 `P`에 들어간다. 반대로 `P=NP`이면 `NP`의 모든 언어가 `P`이므로 5가 성립한다. [Cook, 공식 문제 설명, 4–5쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9).

`P=NP`는 `NP=coNP`와 동치가 아니다. `P=NP`이면 여집합을 취해 `NP=coNP`가 따라온다. 그러나 `NP=coNP`에서 `P=NP`가 따르는지는 알려지지 않았다. 따라서 `NP≠coNP`는 `P≠NP`를 함의하지만, `NP=coNP`는 문제의 해답이 아니다. 이 구별은 결정 문제와 증명 체계의 결과를 적용할 때 필요하다. [Cook과 Reckhow, *The Relative Efficiency of Propositional Proof Systems* (1979)](https://doi.org/10.2307/2273702).

## 3. 2026-08-25의 현행 상태

CMI의 현행 개별 페이지는 `P vs NP`를 `Unsolved`로 표시한다. CMI의 현행 종합 목록도 `P vs NP`를 미해결 문제 목록에 둔다. 두 페이지는 현재 상태를 직접 표시하는 공식 기관 자료다. [CMI 개별 상태](https://www.claymath.org/millennium/p-vs-np/), [CMI 종합 상태](https://www.claymath.org/millennium-problems/).

Cook의 공식 설명에 있는 “대부분의 복잡도 이론가가 `P≠NP`를 믿는다”는 문장은 증명이나 현재 상태의 근거가 아니다. 이 문서는 그 견해를 해답의 근거로 사용하지 않는다. CMI 상금 규칙은 해답이 적격 출판물로 공개된 뒤 2년이 지나고 수학 공동체의 일반적 수용을 얻어야 상금 심사를 한다고 정한다. 이는 미해결 여부의 독립 증명은 아니지만, 수용된 해답을 무엇으로 볼지 정한 기관 규칙이다. [Cook, 공식 문제 설명, 7쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), [CMI 상금 규칙](https://www.claymath.org/millennium-problems/rules/).

## 4. 알려진 부분 결과

### 4.1 NP-completeness와 그 귀결

Cook–Levin 정리는 `SAT`가 `NP-complete`임을 보인다. Karp는 표준 many-one 환원으로 21개 조합 문제의 `NP-complete`성을 보였다. 이 결과는 한 `NP-complete` 문제의 다항시간 알고리즘이 모든 `NP` 언어의 다항시간 알고리즘을 준다는 것을 보인다. 그러나 어느 쪽의 알고리즘 또는 하계도 제공하지 않으므로 `P=NP`와 `P≠NP`를 판정하지 않는다. [Cook (1971)](https://doi.org/10.1145/800157.805047), [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9).

Ladner의 정리는 `P≠NP`를 가정하면 `NP` 안에 `P`에도 속하지 않고 다항시간 many-one 환원 아래 `NP-complete`도 아닌 언어가 존재한다고 말한다. 이 정리는 가정 아래의 구조 정리다. `P≠NP` 자체를 증명하지 않는다. Ladner는 Turing 환원과 many-one 환원의 구조가 다름도 분석한다. [Richard Ladner, *On the Structure of Polynomial Time Reducibility* (1975)](https://doi.org/10.1145/321864.321877).

### 4.2 제한된 회로 모형의 하계

일반 Boolean circuit에 대한 초다항 하계는 `P≠NP`를 보일 충분조건이다. `P`의 언어에는 다항 크기 회로족이 있기 때문이다. 그러나 이 충분조건은 일반 회로족에 대한 결과를 요구한다. 제한된 회로족의 하계는 그 제한을 제거하지 못한다. [Cook, 공식 문제 설명, 7–8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

알려진 하계는 제한된 회로 모형에서 강하다. Cook의 공식 설명은 단조 회로와 unbounded fan-in의 bounded-depth 회로에서 `NP` 문제의 지수 하계가 알려졌다고 기록한다. 이 결과는 unrestricted Boolean circuit의 하계가 아니다. [Cook, 공식 문제 설명, 8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

Williams는 `ACC` 회로족에 관해 `NEXP`가 다항 크기 non-uniform `ACC` 회로족을 갖지 않음을 증명했다. `ACC`는 상수 깊이의 unbounded fan-in `AND`, `OR`, `NOT`, `MOD_m` 게이트 회로 모형이다. 결론의 언어 계급은 `NEXP`이고 회로 모형은 `ACC`이므로, 이 결과는 일반 회로에 대한 `NP` 하계가 아니다. [Ryan Williams, *Nonuniform ACC Circuit Lower Bounds* (2014)](https://doi.org/10.1145/2559903), [저자 공개 원고](https://www.cs.cmu.edu/~ryanw/acc-lbs-ccc.pdf).

Kannan은 다항 계층 `PH`에 선형 크기 회로족으로 계산할 수 없는 언어가 있음을 보였다. Cook은 이 결과와 함께, `P⊆LINEAR-SIZE`이면 `P≠NP`라는 조건부 귀결을 적는다. 이는 `P⊆LINEAR-SIZE`라는 아직 증명되지 않은 전제를 쓴다. [Cook, 공식 문제 설명, 8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

Mahaney의 정리는 다항시간 many-one 환원 아래 sparse `NP-hard` 집합이 존재하면 `P=NP`라고 말한다. sparse는 각 길이 `n`에서 집합의 원소 수가 `n`의 다항식으로 제한되는 성질이다. 따라서 `P≠NP`라는 가정 아래에는 sparse `NP-complete` 집합이 없다는 조건부 귀결을 얻는다. 이 정리도 `P≠NP` 증명이 아니다. [Stephen Mahaney, *Sparse Complete Sets for NP* (1982)](https://doi.org/10.1016/0022-0000%2882%2990002-2).

## 5. 알려진 조건부 결과와 장벽 결과

### 5.1 조건부 귀결

다음 명제는 `P≠NP`의 무조건 증명이 아니다. 각 행은 왼쪽 전제를 받아들일 때만 오른쪽 결론을 준다.

| 전제 | 결론 | 근거와 조건 |
| --- | --- | --- |
| `NP≠coNP` | `P≠NP` | `P=NP`이면 `P`의 여집합 닫힘으로 `NP=coNP`가 되므로, 그 대우를 쓴다. [Cook–Reckhow (1979)](https://doi.org/10.2307/2273702) |
| 다항 계층 `PH`가 `P`로 붕괴하지 않음 | `P≠NP` | `P=NP`이면 oracle을 포함한 계층의 각 단계가 `P`가 된다. Cook은 이 붕괴를 사용해 조건부 명제를 적는다. [Cook, 공식 문제 설명, 8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf) |
| Exponential Time Hypothesis(ETH) | `P≠NP` | ETH는 3-SAT에 `2^{o(n)}` 시간 알고리즘이 없다고 가정한다. `P=NP`이면 3-SAT이 다항시간이므로 ETH와 모순된다. [Impagliazzo와 Paturi, *On the Complexity of k-SAT* (2001)](https://doi.org/10.1006/jcss.2000.1727) |
| `P⊆LINEAR-SIZE` | `P≠NP` | Cook이 Kannan의 `PH` 회로 하계와 `P=NP`이면 `PH=P`라는 사실에서 도출한 조건부 귀결이다. [Cook, 공식 문제 설명, 8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf) |

### 5.2 장벽 결과

장벽 결과는 특정 증명 방법군이 해답을 주지 못함을 보이거나, 조건 아래 그 가능성을 제한한다. 장벽 결과는 `P≠NP`의 증거가 아니다.

- Baker–Gill–Solovay는 재귀 oracle `A`, `B`를 구성하여 `P^A=NP^A`와 `P^B≠NP^B`를 각각 보였다. 따라서 모든 oracle에 대해 그대로 작동하는 relativizing 기법만으로는 원래의 `P` 대 `NP` 문제를 판정할 수 없다. 원래 명제의 oracle 없는 답은 이 결과가 정하지 않는다. [Baker·Gill·Solovay, *Relativizations of the P =? NP Question* (1975)](https://doi.org/10.1137/0204037).

- Razborov–Rudich는 강한 의사난수 생성기의 존재를 가정하면 자연성, 구성성, 유용성을 갖는 natural proof 방법이 일반 회로의 초다항 하계를 보일 수 없음을 보였다. 가정과 natural proof의 정의가 결론의 범위다. 이 결과는 모든 가능한 회로 하계 증명법을 배제하지 않는다. [Razborov와 Rudich, *Natural Proofs* (1997)](https://doi.org/10.1006/jcss.1997.1494).

- Aaronson–Wigderson은 relativization과 natural proof를 피하는 일부 산술화 기법도 algebrization을 한다고 보였다. 이들은 `P` 대 `NP`의 해답은 algebrizing 기법을 넘어야 한다고 정식화한다. algebrization도 증명 기법의 한계를 말할 뿐, 두 계급의 관계를 말하지 않는다. [Aaronson과 Wigderson, *Algebrization: A New Barrier in Complexity Theory* (2009)](https://doi.org/10.1145/1490270.1490272), [저자 공개 원고](https://www.scottaaronson.com/papers/alg.pdf).

## 6. 연구 전에 확보할 선행 정리와 표준 전거

연구 운영자는 아래 항목을 같은 정의와 환원으로 사용할 수 있어야 한다.

1. 결정론적·비결정론적 Turing machine, 다항시간, verifier 정의, `P⊆NP`. 정본 전거는 [Cook의 공식 문제 설명](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf)이다.
2. 다항시간 many-one 환원의 합성, `NP-complete` 정의, `SAT`와 `3-SAT`의 `NP-complete`성. 역사적 원전은 [Cook (1971)](https://doi.org/10.1145/800157.805047)과 [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9)이다. Cook 원전의 Turing 환원과 Karp 원전의 many-one 환원을 구별한다.
3. `coNP`, 다항 계층, 회로족, non-uniform 계산, oracle 계산. `NP=coNP`나 `PH` 붕괴의 결과를 `P=NP`와 동치라고 쓰지 않는다. [Cook, 공식 문제 설명, 7–9쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).
4. 제한 회로 하계와 unrestricted Boolean circuit 하계의 차이. `ACC` 하계와 단조 회로 하계는 전자의 결과다. [Williams (2014)](https://doi.org/10.1145/2559903), [Cook, 공식 문제 설명, 7–8쪽](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).
5. relativization, natural proofs, algebrization의 정확한 범위. 세 결과는 방법론의 경계를 제공한다. 세 결과 모두 `P≠NP`의 증거가 아니다. [Baker–Gill–Solovay (1975)](https://doi.org/10.1137/0204037), [Razborov–Rudich (1997)](https://doi.org/10.1006/jcss.1997.1494), [Aaronson–Wigderson (2009)](https://doi.org/10.1145/1490270.1490272).

종합 전거로는 Sanjeev Arora와 Boaz Barak의 *Computational Complexity: A Modern Approach*을 쓴다. 이 책은 계산 모형, 환원, 계층, 회로 복잡도를 한 표기 체계로 설명한다. 저자들이 공개한 초고를 표준 전거로 사용한다. [Arora–Barak 공개 초고](https://theory.cs.princeton.edu/complexity/book.pdf).

## 7. 계산 자료와 형식 증명 자료

### 7.1 계산 자료

SAT Competition 2024 Main Track 데이터셋은 DIMACS 형식 CNF 파일 400개와 4.3 GB 압축 묶음을 공개한다. 이 자료는 SAT solver의 유한 입력 성능과 재현 가능한 실험을 위한 benchmark다. 각 입력을 풀었다는 기록, 제한 시간 안에 풀지 못했다는 기록, solver 순위는 최악 경우 다항시간 알고리즘의 존재나 부재를 정하지 않는다. [Armin Biere, SAT Competition 2024 Main Track Benchmarks, Zenodo, 2025-03-27](https://zenodo.org/records/15095752), [SAT Competition 2026의 공개 결과·인스턴스 안내](https://satcompetition.github.io/2026/).

### 7.2 형식 증명 자료

Gäher와 Kunze의 공개 Coq/Rocq 저장소는 Cook–Levin 정리를 형식화한다. 저장소는 원 논문과 함께 빌드 절차와 생성된 문서를 공개한다. 이 형식화는 call-by-value lambda calculus를 계산 모형으로 사용한다. `P=NP` 또는 `P≠NP`를 형식 증명한 자료가 아니라, `SAT`의 `NP-complete`성을 뒷받침하는 선행 정리 자료다. [Gäher·Kunze, *Mechanising Complexity Theory: The Cook-Levin Theorem in Coq*](https://uds-psl.github.io/cook-levin/).

Archive of Formal Proofs의 Balbach 항목은 Isabelle/HOL에서 Cook–Levin 정리를 형식화한다. 이 항목은 결정론적 multi-tape Turing machine, `P`, `NP`, 다항시간 many-one 환원, `SAT`를 정의한다. `NP` 문제를 oblivious two-tape verifier Turing machine의 계산을 CNF로 부호화해 `SAT`로 환원한다. 따라서 Coq 자료와 같은 결론을 목표로 하지만 계산 모형과 형식 체계가 다르다. [Frank J. Balbach, *The Cook-Levin theorem*, AFP, 2023-01-08](https://isa-afp.org/entries/Cook_Levin.html).

Pierre Senellart의 Lean 4 라이브러리는 논리적 정의의 `NP`에 대해 machine-free Cook–Levin 정리와 Karp의 21개 문제를 형식화한다. 이 라이브러리는 time-bounded multi-tape Turing machine으로 정의한 `P`와 `NP`로 잇는 별도 bridge 정리도 둔다. 이 자료도 계급 분리를 결정하지 않는다. [Senellart, *descriptive-complexity* 공개 저장소](https://github.com/PierreSenellart/descriptive-complexity).

아래 범위에서는 수용된 `P=NP` 또는 `P≠NP`의 완전 형식 증명 저장소를 확인하지 못했다. 검색 범위는 Coq/Rocq Cook–Levin 공개 저장소, Isabelle Archive of Formal Proofs의 Cook–Levin 항목, Lean의 공개 complexity 라이브러리, SAT Competition과 Zenodo의 공개 benchmark 자료다. 이 부재는 위 저장소와 자료 유형에 한정한다. 공개 저장소 밖의 모든 형식화가 없다는 뜻은 아니다.

## 8. 연구 경계

이 연구 대상은 고전적 결정 문제의 최악 경우 계급 등식이다. 다음 항목은 서로 바꾸어 쓰지 않는다.

- 어떤 SAT benchmark 집합을 푸는 solver와 모든 입력에 대한 다항시간 SAT 알고리즘
- 제한 회로 모형의 하계와 unrestricted Boolean circuit 하계
- oracle 상대화 명제 `P^A=NP^A` 또는 `P^B≠NP^B`와 oracle 없는 `P=NP` 또는 `P≠NP`
- ETH, `NP≠coNP`, `P⊆LINEAR-SIZE` 같은 조건부 전제와 무조건 정리
- `P=NP`를 가정한 귀결과 `P=NP`의 증명
- Cook의 다항시간 Turing 환원과 Karp의 다항시간 many-one 환원

## 출처별 주장 대응표

| 출처 | 출처 유형 | 뒷받침하는 주장 | 기준일 또는 발행연도 |
| --- | --- | --- | --- |
| [CMI P vs NP 현행 페이지](https://www.claymath.org/millennium/p-vs-np/) | 공식 기관 현행 페이지 | `P vs NP`의 `Unsolved` 상태와 비형식적 질문 | 2026-08-25 확인 |
| [CMI Millennium Prize Problems](https://www.claymath.org/millennium-problems/) | 공식 기관 현행 목록 | `P vs NP`가 미해결 목록에 있음 | 2026-08-25 확인 |
| [Cook, 공식 문제 설명](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf) | CMI 공식 문제 명세 | 정본 명제, `P`·`NP` 정의, many-one 환원, `NP-complete`, 회로와 조건부 귀결 | 2000, CMI 공개 PDF 2022 |
| [Cook (1971)](https://doi.org/10.1145/800157.805047) | 동료평가 학회 논문 | 초기 `NP-complete` 개념과 다항시간 Turing 환원 | 1971 |
| [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9) | 학술 단행본 수록 논문 | 다항시간 many-one 환원과 21개 `NP-complete` 문제 | 1972 |
| [Ladner (1975)](https://doi.org/10.1145/321864.321877) | 동료평가 저널 논문 | `P≠NP` 가정 아래의 `NP-intermediate` 언어 | 1975 |
| [Baker–Gill–Solovay (1975)](https://doi.org/10.1137/0204037) | 동료평가 저널 논문 | 상대화 oracle `A`, `B`와 relativization 장벽 | 1975 |
| [Cook–Reckhow (1979)](https://doi.org/10.2307/2273702) | 동료평가 저널 논문 | 명제 증명 체계와 `NP=coNP` 관련 표준 전거 | 1979 |
| [Mahaney (1982)](https://doi.org/10.1016/0022-0000%2882%2990002-2) | 동료평가 저널 논문 | sparse `NP-hard` 집합의 조건부 결과 | 1982 |
| [Razborov–Rudich (1997)](https://doi.org/10.1006/jcss.1997.1494) | 동료평가 저널 논문 | natural-proofs 장벽의 조건과 범위 | 1997 |
| [Impagliazzo–Paturi (2001)](https://doi.org/10.1006/jcss.2000.1727) | 동료평가 저널 논문 | ETH와 k-SAT 조건부 난이도 | 2001 |
| [Aaronson–Wigderson (2009)](https://doi.org/10.1145/1490270.1490272) | 동료평가 저널 논문 | algebrization 장벽 | 2009 |
| [Williams (2014)](https://doi.org/10.1145/2559903) | 동료평가 저널 논문 | non-uniform `ACC`에 대한 `NEXP` 회로 하계 | 2014 |
| [SAT Competition 2024 데이터셋](https://zenodo.org/records/15095752) | 공개 연구 데이터셋 | DIMACS CNF benchmark 400개와 공개 위치 | 2025-03-27 |
| [Gäher–Kunze Coq/Rocq 자료](https://uds-psl.github.io/cook-levin/) | 공개 형식 증명 저장소 | Coq/Rocq Cook–Levin 형식화와 빌드 정보 | 2021 논문, 2026-08-25 확인 |
| [Balbach AFP 자료](https://isa-afp.org/entries/Cook_Levin.html) | 공식 형식 증명 아카이브 | Isabelle/HOL Cook–Levin 형식화, 두 테이프 oblivious TM 모형 | 2023-01-08 |
| [Senellart Lean 자료](https://github.com/PierreSenellart/descriptive-complexity) | 공개 형식 증명 저장소 | 논리적 `NP`의 Cook–Levin과 기계 모형 bridge | 2026-08-25 확인 |
| [Arora–Barak 공개 초고](https://theory.cs.princeton.edu/complexity/book.pdf) | 저자 공개 교재 초고 | 계산복잡도 표준 정의와 선행 정리의 종합 전거 | 2009 공개본 |
