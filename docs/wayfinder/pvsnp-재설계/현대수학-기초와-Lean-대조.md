# 현대 수학의 기초와 Lean 대조

- 조사 기준일: 2026-08-29
- 조사 질문: `Lean 핵심 타입 이론 + propext + Quot.sound + Classical.choice`를 현대 수학 학계가 일반적으로 사용하는 기초라고 부를 수 있는가

> **현행 지위:** 이 문서는 날짜를 고정한 기초 체계 비교 조사다. 후속 결정은 Lean 핵심 타입 이론과 세 표준 수학 공리를 이 프로젝트의 활성 기초로 채택했다. 이 문서는 그 선택을 다시 열지 않는다. 이 문서는 선택 이유를 학계 전체의 관행으로 잘못 설명하지 않도록 범위를 정밀화한다.

## 결론

그렇게 부르면 범위가 잘못된다.

`Lean 핵심 타입 이론 + propext + Quot.sound + Classical.choice`는 Lean에서 고전 수학을 수행하는 표준적인 형식 기초다. 이 기초는 현대 수학의 통상적인 고전 추론을 넓게 표현한다. Mathlib은 이 기초에서 연구 수준 수학을 형식화한다.

그러나 현대 수학 학계 전체가 일반 논문에서 이 Lean 기초를 사용하지는 않는다. 일반 논문은 대개 특정 형식 기초를 명시하지 않는다. 수학자는 해당 분야의 정의, 가정과 논증을 공통 수학 언어로 적는다.

형식 기초를 따져야 할 때는 고전 1차 논리와 Zermelo–Fraenkel 집합론 및 선택 공리(ZFC)가 통상적인 기준점이다. ZFC도 유일하거나 의무적인 기초는 아니다. 집합론, 단순 타입 이론과 종속 타입 이론을 사용하는 형식 체계가 함께 존재한다.

따라서 두 문장을 구별해야 한다.

- **통과:** Lean의 표준 고전 기초는 현대 수학의 넓은 범위를 표현하고 검증할 수 있다.
- **기각:** 현대 수학 학계는 Lean의 표준 고전 기초를 일반적인 형식 기초로 사용한다.

이 프로젝트는 Lean 기초를 정본으로 채택했다. 그 채택은 학계의 기존 단일 표준을 그대로 따른 결과가 아니다. 이 프로젝트의 목적에 맞게 선택한 형식 기초라는 뜻이다.

## 판정에 쓰는 네 구별

이 문서는 다음 표현을 같은 뜻으로 쓰지 않는다.

- **일반 논문에서 사용한다:** 저자가 논문에서 그 기초의 언어와 규칙으로 명제와 증명을 실제 작성한다.
- **통상적인 기준이다:** 형식화 가능성이나 기초 가정을 논할 때 널리 인정받는 비교 기준으로 삼는다.
- **표현할 수 있다:** 해당 기초 안에서 수학적 대상과 논증을 형식화할 수 있다.
- **정본으로 채택한다:** 이 프로젝트가 어느 표현을 수학적 내용의 최종 기준으로 정한다.

한 기초가 현대 수학을 표현할 수 있어도 수학자가 일반 논문에서 그 기초를 사용한다는 결론은 나오지 않는다. 프로젝트가 그 기초를 정본으로 채택해도 학계가 같은 정본을 채택했다는 결론은 나오지 않는다.

## 판정 1. 일반 논문은 보통 특정 형식 기초를 명시하지 않는다

Fairouz Kamareddine, Joe Wells, Christoph Zengler와 Henk Barendregt는 수학 실무와 형식 기초의 관계를 직접 분석했다. 저자들은 수학자가 실제 작업을 특정 기초의 문장으로 표현하지 않는다고 설명한다. 저자들은 일반 수학 언어가 대체로 ZFC와 양립하지만, 완전한 형식 세부는 거의 쓰지 않는다고 설명한다. 또한 최선의 논리 기초에 관한 보편적 합의가 없다고 적는다. [Computerising Mathematical Text](https://www.macs.hw.ac.uk/~fairouz/forest/papers/journals-publications/siekmann.pdf)

Clay Mathematics Institute의 P vs NP 공식 기술도 이 실무를 보여 준다. Stephen Cook은 유한 알파벳, 문자열, 언어, Turing 기계와 실행 시간으로 문제를 정의한다. Cook은 ZFC, Lean 또는 다른 형식 기초를 지정하지 않는다. [Stephen Cook, The P versus NP Problem](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf)

Clay의 공식 규칙도 특정 형식 기초를 요구하지 않는다. 규칙은 완전한 수학적 해결, 심사 학술지 게재, 2년의 경과와 세계 수학계의 일반적 수용을 요구한다. 규칙은 ZFC나 Lean의 사용을 요구하지 않는다. [Millennium Prize Description and Rules](https://www.claymath.org/wp-content/uploads/2022/03/millennium_prize_rules_0.pdf)

이 자료들은 학계 전 분야의 논문을 계량한 전수 조사 결과가 아니다. 따라서 “모든 일반 논문이 형식 기초를 명시하지 않는다”라고 단정할 수는 없다. 확인한 근거가 지지하는 판정은 다음과 같다.

> P vs NP를 포함한 통상적인 수학 논문에서는 특정 형식 기초의 이름과 전체 공리 목록이 표준 필수 항목이 아니다.

기초가 결과에 영향을 주는 논문은 예외다. 집합론, 수리논리, 범주론의 크기 문제와 독립성 연구에서는 기초를 명시할 수 있다.

## 판정 2. 고전 논리와 ZFC는 통상적인 메타수학 기준이다

Jeremy Avigad는 현대 수학이 비계산적 함수와 비계산적 대상의 존재를 허용한다는 점에서 철저히 고전적이라고 설명한다. Avigad는 형식 기초의 세 주요 계열로 집합론, 단순 타입 이론과 종속 타입 이론을 구분한다. [Jeremy Avigad, Foundations](https://arxiv.org/html/2009.09541v4)

Avigad는 집합론이 현대 수학의 방법을 통일된 방식으로 담기 위해 설계됐다고 설명한다. Zermelo–Fraenkel 집합론의 공리는 고전 1차 논리로 작성된다. 선택 공리를 더한 체계가 ZFC다.

Mario Carneiro는 ZFC가 현대 수학의 공리화를 위한 “gold standard”가 됐다고 설명한다. Mathlib 논문도 많은 수학자가 집합론을 공식적이거나 논쟁이 적은 기초로 받아들인다고 설명한다. [Mario Carneiro, The Type Theory of Lean, 서론](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/intro.tex) [The mathlib Community, The Lean Mathematical Library](https://leanprover-community.github.io/papers/mathlib-paper.pdf)

여기서 ZFC의 지위는 일상 논문의 실제 문법이 아니다. ZFC의 지위는 다음과 같은 메타수학 기준이다.

- 통상적인 수학 논증을 완전 형식화할 수 있는가
- 어떤 추가 가정이 필요한가
- 두 기초가 같은 정리를 보존하는가
- 어떤 결과가 선택 공리나 큰 기수에 의존하는가.

따라서 “현대 수학은 통상적으로 고전적이다”라는 판정은 근거가 있다. “모든 현대 수학자는 ZFC 유도문을 직접 작성한다”라는 판정은 근거가 없다.

## 판정 3. ZFC는 유일하거나 의무적인 기초가 아니다

형식 수학에는 여러 기초가 실제로 사용된다. Avigad는 현행 증명 보조기의 주요 기초를 집합론, 단순 타입 이론과 종속 타입 이론으로 구분한다. Mizar와 Metamath 계열은 집합론을 사용한다. HOL 계열은 고전 단순 타입 이론을 사용한다. Lean은 종속 타입 이론을 사용한다. [Jeremy Avigad, Foundations](https://arxiv.org/html/2009.09541v4)

집합론 안에도 선택지가 있다. Michael Shulman은 범주론을 위한 ZFC, von Neumann–Bernays–Gödel 집합론(NBG), Morse–Kelley 집합론과 Grothendieck 우주 접근을 비교한다. Shulman은 NBG가 집합에 관한 문장에서는 ZFC의 보존적 확장이라고 설명한다. Shulman은 범주론의 기초 하나를 유일한 정답으로 제시하지 않는다. [Michael Shulman, Set Theory for Category Theory](https://arxiv.org/html/0810.1279v2)

Mizar Mathematical Library는 1차 Tarski–Grothendieck 집합론을 실제 정본으로 사용한다. 이 체계는 임의의 집합을 포함하는 더 큰 우주의 존재를 보장한다. 따라서 ZFC 단독보다 강한 큰 기수 원리를 포함한다. [Mizar Mathematical Library의 기초 설명](https://wiki.mizar.org/library/) [Andrzej Trybulec, Tarski Grothendieck Set Theory](https://fm.mizar.org/1990-1/pdf1-1/tarski.pdf)

이 사례들은 다음 두 전칭 주장을 반박한다.

- 현대 형식 수학은 반드시 ZFC만 사용한다.
- 현대 형식 수학은 반드시 Lean의 종속 타입 이론만 사용한다.

Clay의 P vs NP 공식 기술과 규칙도 특정 기초를 의무화하지 않는다. 그러므로 P vs NP 해결의 공식 자격 조건에서 ZFC나 Lean을 필수 기초라고 말할 수 없다.

## 판정 4. Lean 핵심 타입 이론과 세 공리의 정확한 지위

현행 Lean 커널은 종속 타입 이론의 한 종류를 검사한다. Lean Language Reference는 커널 언어를 다음 구성으로 설명한다.

- 완전한 종속 타입
- 상호 귀납형과 중첩 귀납형을 포함하는 귀납형
- 비서술적이고 증명 무관한 `Prop`
- 서술적이고 비누적적인 데이터 우주 계층
- 정의적 계산 규칙을 가진 몫
- 함수와 곱의 정의적 η-동등성
- 우주 다형 선언.

사용자 문법, 전술과 재귀 문법은 이 핵심 언어로 정교화된다. 커널은 정교화된 항이 타입 이론의 규칙을 따르는지 검사한다. [Lean Language Reference, Elaboration and Compilation](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/) [Lean Language Reference, The Type System](https://lean-lang.org/doc/reference/latest/The-Type-System/)

현행 Lean은 표준 공리 일곱 개를 열거한다. 그중 다음 세 공리가 Lean 수학의 주요 공리다.

```lean
Classical.choice : Nonempty α → α
propext          : (a ↔ b) → a = b
Quot.sound       : r a b → Quot.mk r a = Quot.mk r b
```

`Classical.choice`는 비어 있지 않은 타입에서 원소를 고른다. `propext`는 논리적으로 동치인 명제를 같은 명제로 만든다. `Quot.sound`는 몫 관계에 있는 대표들을 몫에서 같게 만든다. [Lean Language Reference, Axioms](https://lean-lang.org/doc/reference/latest/Axioms/)

“표준 고전 기초”라는 표현은 세 공리가 모두 고전 논리 공리라는 뜻이 아니다. `Classical.choice`가 비구성적 선택을 제공한다. `propext`는 명제 외연성을 제공하고, `Quot.sound`는 몫의 등식을 제공한다. Lean은 이들을 사용해 배중률과 고전적 귀류법을 유도한다.

이 세 공리는 ZFC 공리의 다른 표기가 아니다. 세 공리는 Lean의 타입, 명제, 등식과 몫 위에서 작동한다. ZFC는 한 종류의 대상인 집합과 원소 관계를 고전 1차 논리에서 공리화한다.

Lean의 구성적 핵심에 선택과 외연성을 더하면 고전적 추론을 얻는다. 배중률은 별도 원시 공리가 아니라 이 공리들에서 유도된다. Avigad는 함수 외연성, 명제 외연성과 선택을 더한 종속 타입 이론이 완전한 고전적 성격을 가진다고 설명한다. [Jeremy Avigad, Foundations §6.7](https://arxiv.org/html/2009.09541v4#S6.SS7)

따라서 다음 표현은 정확하다.

> Lean 핵심 타입 이론과 세 표준 수학 공리는 Lean과 Mathlib에서 고전 수학을 수행하는 표준 기초다.

다음 표현은 범위를 넘는다.

> Lean 핵심 타입 이론과 세 표준 수학 공리는 현대 수학 학계 전체가 일반적으로 사용하는 기초다.

또한 “세 공리만 허용한다”는 문장은 다른 Lean 공리를 금지한다는 뜻까지 포함한다. 현행 정본은 `sorryAx`, 컴파일러 신뢰 공리와 `native_decide`가 만드는 전용 공리를 허용하지 않는다.

## 판정 5. Lean 기초와 ZFC는 같지 않지만 양방향 모형 관계가 있다

### 5.1 네 관계를 구별해야 한다

Lean과 ZFC를 비교할 때는 다음 네 관계를 구별해야 한다.

- **모형 구성:** 한 체계 안에서 다른 체계의 공리를 만족하는 구조를 만든다.
- **상대 일관성:** 첫 체계가 일관되면 둘째 체계도 일관된다는 메타수학 결과다.
- **같은 일관성 강도:** 두 체계 사이에서 상대 일관성을 양방향으로 얻는다.
- **정리 보존:** 공유하는 문장에 대해 한 체계의 증명을 다른 체계의 증명으로 옮긴다.

같은 일관성 강도만으로 정리 보존은 나오지 않는다. 두 체계가 같은 명제를 같은 뜻으로 표현한다는 결론도 나오지 않는다.

### 5.2 ZFC에서 Lean의 모형을 만드는 방향

Carneiro의 2019년 논문은 당시 Lean의 타입 이론을 완전한 형식 규칙으로 제시한다. 이 체계에는 귀납형, 우주 계층, 증명 무관성, 몫, 명제 외연성과 선택이 들어간다. [The Type Theory of Lean, 공리 규칙](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/axioms.tex)

Carneiro는 집합론 모형을 구성해 다음 상대 일관성 결과를 얻는다.

> ZFC에 “적어도 `n`개의 강하게 도달 불가능한 기수가 존재한다”라는 공리를 모든 표준 자연수 `n`에 대해 더한 이론이 일관되면 Lean도 일관된다.

논문은 이를 `ZFC + {there are n inaccessible cardinals | n ∈ ω}`로 쓴다. 이하에서는 강하게 도달 불가능한 기수를 `도달 불가능 기수`라고 줄여 쓴다. 도출과 우주 변수의 값을 고정하면 충분히 큰 유한 `k`가 존재한다. 해당 도출의 집합론 해석에는 `k`에 맞는 도달 불가능 기수만 사용한다. [The Type Theory of Lean, Soundness](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/soundness.tex)

이 결과를 “ZFC만으로 Lean의 일관성을 증명했다”라고 쓰면 틀린다. 도달 불가능 기수의 존재는 ZFC 단독보다 강한 가정이다. Shulman은 `κ`가 도달 불가능 기수이면 $V_\kappa$가 ZFC의 모형이 된다고 설명한다. [Set Theory for Category Theory §8](https://arxiv.org/html/0810.1279v2#S8)

또한 위 공리 모음을 “하나의 집합으로 주어진 가산 무한 도달 불가능 기수열이 존재한다”와 바로 동일시하면 안 된다. Carneiro가 적은 정확한 이론은 모든 유한 `n`에 대한 공리들의 합집합이다.

### 5.3 Lean에서 ZFC의 모형을 만드는 방향

Carneiro는 Werner의 구성을 Lean에 옮기면 충분히 높은 Lean 우주에서 ZFC와 유한 개의 도달 불가능 기수를 가진 모형을 만들 수 있다고 설명한다. 이 방향과 앞 방향을 합치면 논문에서 정의한 Lean 체계는 위 집합론과 같은 일관성 강도를 가진다.

Mathlib은 이 방향의 현재 구현을 제공한다. `Mathlib.SetTheory.ZFC.Basic`은 `PSet`을 외연적 동치로 몫내어 `ZFSet`을 정의한다. 이 파일은 ZFC와 선택 공리를 Lean의 타입 이론 안에서 모형화한다고 명시한다. `ZFSet.choice`는 Lean의 선택 공리에서 증명한다. [Mathlib.SetTheory.ZFC.Basic 문서](https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/ZFC/Basic.html) [고정 소스 커밋](https://github.com/leanprover-community/mathlib4/blob/5ba95124681110751345e9bd360994de8541027c/Mathlib/SetTheory/ZFC/Basic.lean)

Mathlib의 ZFC 모형은 다음 결론을 주지 않는다.

- Lean의 모든 타입은 `ZFSet`이다.
- 모든 Lean 정리는 ZFC 단독의 정리다.
- Lean과 ZFC의 정의는 자동으로 같은 뜻이다.

일반 Lean 정리를 ZFC 정리로 옮기려면 별도 해석과 정리 보존 결과가 필요하다.

### 5.4 우주 계층의 강도

Mathlib 논문은 Lean의 우주 계층 때문에 Lean이 ZFC보다 높은 일관성 강도를 가진다고 설명한다. 이 설명은 Carneiro의 도달 불가능 기수 분석과 맞는다. [The Lean Mathematical Library](https://leanprover-community.github.io/papers/mathlib-paper.pdf)

그러나 전체 Lean 체계의 최대 강도와 개별 정리의 실제 필요 강도는 다르다. 특정 Lean 증명문은 유한하지만 우주 다형 선언은 여러 우주 수준에 인스턴스화할 수 있다. Carneiro의 모형은 도출과 우주 변수의 값을 고정한 뒤 유한 상한을 준다.

그 상한이 개별 정리의 최소 필요 강도라는 뜻은 아니다. P vs NP 명제는 유한 문자열과 Turing 기계에 관한 명제다. 실제 증명이 어느 기초 강도를 필요로 하는지는 그 증명의 의존 관계를 보고 별도로 판정해야 한다.

### 5.5 현행 Lean 4에 대한 한계

Carneiro의 완전한 메타이론은 2019년 논문이 정의한 Lean 체계를 대상으로 한다. 현행 Lean 4 Reference는 Carneiro의 논문을 커널 이론의 상세 자료로 인용한다. 그러나 이번 조사에서는 Lean 4의 현행 중첩·상호 귀납형 구현 전건까지 포함한 새 일관성 강도 증명을 찾지 못했다.

따라서 이 문서는 Carneiro의 정리를 현행 Lean 4 구현 전건에 대한 새 증명으로 확대하지 않는다. 현행 Lean 4의 정확한 메타이론 전이는 미판정으로 남긴다.

## 판정 6. Mathlib의 표현 범위는 학계 전체의 채택률을 말하지 않는다

Lean Language Reference는 Lean의 타입 이론이 최전선 연구 수학을 표현할 만큼 풍부하다고 설명한다. Mathlib 논문은 Mathlib을 연구 수준 수학의 기반으로 설계했다고 설명한다. Mathlib은 고전 수학, 대수학, 해석학, 위상수학, 범주론과 집합론의 큰 부분을 형식화한다.

이 사실은 다음 판정을 지지한다.

> Lean과 Mathlib은 현대 수학의 넓은 범위를 형식화하는 실용적 기반이다.

이 사실은 다음 판정을 지지하지 않는다.

> 현대 수학 학계 전체가 Lean의 기초를 일반 논문의 기초로 채택했다.

Mathlib의 존재는 표현력과 실제 형식화 사례를 보여 준다. 학계 전체의 일반 사용 여부는 별도의 사회적·계량적 주장이다. 조사한 1차 자료에서는 그 일반 사용을 입증하는 근거를 찾지 못했다.

증명 보조기 사이의 다양성도 같은 구별을 요구한다. Avigad가 열거한 Mizar, HOL, Isabelle, Coq, PVS, Agda와 Lean은 서로 다른 기초를 사용한다. 한 체계가 수학을 성공적으로 형식화했다는 사실은 다른 체계의 기초를 배제하지 않는다.

## 판정 7. P vs NP 연구의 기본 기초 선택에 생기는 직접 귀결

다음 항목은 조사에서 바로 나오는 귀결이다. 현행 선택의 정본은 컨텍스트 정본과 `do-math` 통합 설계 티켓이다.

1. Lean 기초를 선택한다면 선택 이유를 “현대 학계가 같은 기초를 일반적으로 사용한다”라고 쓰면 안 된다.
2. Lean 기초는 “이 프로젝트가 채택한 형식 기초”라고 명시해야 한다.
3. Lean 기초가 통상적인 고전 수학을 표현한다는 점은 선택 근거가 될 수 있다.
4. Lean 커널 수락은 선택한 Lean 기초에서 형식 명제가 도출된다는 증거다.
5. 검토자는 Lean 명제가 Cook의 공식 P vs NP 문제와 같은 수학적 내용을 갖는지 검토해야 한다.
6. 검토자는 사용자 공리, `sorryAx`, 컴파일러 신뢰 공리와 전용 계산 공리를 감사해야 한다.
7. `#print axioms`는 공리 상수를 추적하지만 커널 규칙과 전체 우주 강도를 열거하지 않는다.
8. 학계의 통상적인 ZFC 기준으로 결과를 옮겨야 한다면 별도 정리 보존 근거가 필요하다.
9. Lean과 ZFC의 같은 일관성 강도만으로 개별 P vs NP 정리의 이동을 주장하면 안 된다.
10. Clay 규칙상 Lean 커널 수락만으로 상금 해결 요건을 충족하지 않는다. 완전한 해결, 적격 출판과 수학계의 일반적 수용이 필요하다.

Lean 정본 원칙은 Clay 규칙보다 더 강한 내부 검증 절차가 될 수 있다. 그러나 내부 검증 절차와 외부 학계의 수용 기준은 다른 판정이다.

## 현행 설계에 넘기는 질문

조사 사실과 설계 결정을 분리한다. 활성 Lean 기초와 공리 허용 목록은 이미 정했다. 다음 구현·검증 항목은 `do-math` 통합 설계가 결정한다.

- 허용한 Lean 판본과 Mathlib 커밋을 어떻게 고정할지
- 개별 정리의 우주 수준을 어떤 방식으로 감사할지
- P vs NP 최종 정리에 ZFC 단독 또는 더 약한 산술 체계로의 정리 보존을 요구할지
- Lean 정본과 Cook의 공식 문제 기술 사이의 의미 대응을 누가 어떤 기준으로 승인할지.

권고할 수 있는 표현은 다음과 같다.

> 프로젝트는 Lean의 표준 고전 기초를 활성 기초로 사용한다. 이 기초는 현대 고전 수학을 넓게 표현한다. 이 기초는 현대 수학 학계의 유일하거나 의무적인 기초가 아니다.

## 기존 심층 검토 문서와의 대조

대상은 [`Lean-증명-표현력-심층검토.md`](./Lean-증명-표현력-심층검토.md)다.

### 검증을 통과한 주장

- Lean의 표면 문법, 핵심 타입 이론과 공리 상수를 구별해야 한다.
- `Classical.choice`, `propext`와 `Quot.sound`는 Lean의 세 표준 수학 공리다.
- 배중률을 쓰는 Lean 증명은 이 세 공리에 전이 의존할 수 있다.
- Lean은 통상적인 고전 수학을 넓게 형식화할 수 있다.
- Lean 안의 다른 논리 모형은 원래 논리와 자동으로 같은 뜻이 되지 않는다.
- Carneiro의 2019년 결과를 현행 Lean 4 구현 전건으로 옮기는 문제는 별도 검증이 필요하다.

### 불일치한 주장

없음.

### 이번 조사에서 추가한 범위

기존 문서는 Lean의 표현력과 검증 경계를 조사했다. 기존 문서는 현대 수학자가 일반 논문에서 어떤 형식 기초를 실제로 명시하는지 판정하지 않았다. 기존 문서는 Lean과 ZFC의 양방향 모형 관계와 우주 강도를 상세히 판정하지 않았다.

따라서 기존 문서의 다음 취지를 사회적 채택 주장으로 확대하면 안 된다.

> Lean은 현대 연구 수학을 표현할 수 있다.

위 문장에서 다음 문장은 나오지 않는다.

> 현대 수학 학계는 Lean의 기초를 일반적으로 사용한다.

## 미판정 항목

- 현대 수학 논문 전건에서 형식 기초 명시 빈도를 측정한 계량 연구는 확인하지 못했다.
- 현행 Lean 4 구현 전건의 정확한 일관성 강도 증명은 확인하지 못했다.
- 아직 존재하지 않는 P vs NP Lean 증명의 최소 공리 강도와 최소 우주 강도는 판정할 수 없다.
- Lean에서 증명한 P vs NP 문장을 ZFC 단독 또는 약한 산술로 옮기는 정리 보존 결과는 확인하지 못했다.
- Clay가 Lean 형식 증명만 담은 논문을 어떤 조건에서 일반적 수용으로 인정할지는 공식 규칙에 적혀 있지 않다.

공식 P vs NP 기술과 Clay 규칙에서 `ZFC`, `Lean`, `axiom`, `foundation`에 해당하는 기초 체계 요구는 발견하지 못했다. 현대 수학 학계가 Lean의 표준 고전 기초를 일반적으로 사용한다는 1차 자료도 발견하지 못했다.

## 읽고 대조한 1차 자료 전건

### Lean과 Mathlib

- Lean Language Reference, [Elaboration and Compilation](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/)
- Lean Language Reference, [The Type System](https://lean-lang.org/doc/reference/latest/The-Type-System/)
- Lean Language Reference, [Axioms](https://lean-lang.org/doc/reference/latest/Axioms/)
- Mario Carneiro, [The Type Theory of Lean v1.0](https://github.com/digama0/lean-type-theory/releases/tag/v1.0), 2019
- Mario Carneiro, [`intro.tex`](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/intro.tex), [`axioms.tex`](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/axioms.tex), [`soundness.tex`](https://raw.githubusercontent.com/digama0/lean-type-theory/v1.0/soundness.tex)
- The mathlib Community, [The Lean Mathematical Library](https://leanprover-community.github.io/papers/mathlib-paper.pdf), 2020
- Mathlib, [Mathlib.SetTheory.ZFC.Basic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/ZFC/Basic.html)
- Mathlib commit `5ba95124681110751345e9bd360994de8541027c`, [`Mathlib/SetTheory/ZFC/Basic.lean`](https://github.com/leanprover-community/mathlib4/blob/5ba95124681110751345e9bd360994de8541027c/Mathlib/SetTheory/ZFC/Basic.lean)

### 현대 수학의 실무와 기초

- Jeremy Avigad, [Foundations](https://arxiv.org/html/2009.09541v4), 2021 판본
- Jeremy Avigad, [The Mechanization of Mathematics](https://aslonline.org/wp-content/uploads/2020/03/Avigad.pdf), 2018 강연 자료
- Fairouz Kamareddine, Joe Wells, Christoph Zengler, Henk Barendregt, [Computerising Mathematical Text](https://www.macs.hw.ac.uk/~fairouz/forest/papers/journals-publications/siekmann.pdf), 2014
- Michael A. Shulman, [Set Theory for Category Theory](https://arxiv.org/html/0810.1279v2), 2008
- Mizar Mathematical Library, [공식 기초 설명](https://wiki.mizar.org/library/)
- Andrzej Trybulec, [Tarski Grothendieck Set Theory](https://fm.mizar.org/1990-1/pdf1-1/tarski.pdf), 1990

### P vs NP 공식 자료

- Stephen Cook, [The P versus NP Problem](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), Clay Mathematics Institute 공식 문제 기술
- Clay Mathematics Institute, [Millennium Prize Description and Rules](https://www.claymath.org/wp-content/uploads/2022/03/millennium_prize_rules_0.pdf), 2018 개정 규칙
- Clay Mathematics Institute, [Rules for the Millennium Prize Problems](https://www.claymath.org/millennium-problems/rules/)

### 저장소 대조 자료

- [`Lean-증명-표현력-심층검토.md`](./Lean-증명-표현력-심층검토.md)

## 최종 판정

`Lean 핵심 타입 이론 + propext + Quot.sound + Classical.choice`는 현대 고전 수학을 형식화하는 강력하고 타당한 기초다. Lean과 Mathlib에서 고전 수학을 수행할 때는 표준적인 선택이다.

그러나 그 조합을 “현대 수학 학계가 일반적으로 사용하는 기초”라고 부르면 실제 논문 관행, ZFC의 메타수학 지위와 여러 형식 기초의 공존을 합쳐 버린다.

프로젝트가 채택한 기초는 다음과 같이 설명한다.

> 이 프로젝트는 현대 고전 수학을 넓게 표현하는 Lean의 표준 고전 기초를 활성 기초로 사용한다.

이 문서는 채택한 기초의 학술적 지위와 표현 범위를 판정한다. 정확한 도구체인, Mathlib 판본과 검증 절차는 `do-math` 통합 설계가 정한다.
