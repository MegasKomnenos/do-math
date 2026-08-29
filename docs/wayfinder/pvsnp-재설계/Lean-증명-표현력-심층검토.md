# Lean 증명 표현력 심층 검토

- 기준일: 2026-08-29
- 현행 참조판: Lean `4.34.0-rc2`
- 현행 안정판: Lean `4.33.1`

> **현행 지위:** 이 문서는 날짜를 고정한 Lean 표현력·검증 경계 조사다. 이 문서는 `do-math`의 검증 절차를 확정하지 않는다. 현행 연구 구조와 확정 원칙은 `docs/wayfinder/pvsnp-재설계/컨텍스트.md`가 요약한다. [「보편 수학 연구 스킬 do-math의 통합 설계를 확정한다」](https://github.com/MegasKomnenos/math/issues/18)가 이 조사 결과를 입력으로 검증 관문을 결정한다.

## 1. 검토 목적과 판정 어휘

이 문서는 “Lean으로 모든 종류의 증명이 가능한가”라는 질문을 여섯 뜻으로 나누어 답한다. 질문을 나누지 않으면 증명 방식, 증명 가능한 명제, 공리, 형식화와 커널 검사를 같은 말로 부르게 된다.

이 문서는 다음 다섯 표현을 구별한다.

- **표현할 수 있다**: Lean 자료형과 명제로 대상의 구문이나 의미를 기술할 수 있다.
- **증명할 수 있다**: 명제 `P : Prop`에 대해 Lean 항 `p : P`를 구성할 수 있다.
- **커널이 직접 지원한다**: Lean 핵심 타입 이론의 형성·타이핑·환원 규칙이 해당 구성을 다룬다.
- **공리를 가정한다**: 증명 항이 값이 없는 상수에 의존한다. 결론은 그 공리에 상대적이다.
- **객체 논리에서 성립한다**: Lean 안에 정의한 다른 논리의 도출 관계에 대한 Lean 정리를 얻었다. 그 결과가 Lean 자체의 정리라는 뜻은 아니다.

Lean의 표면 문법도 핵심 논리와 구별한다. 전술, 패턴 대응과 일반적인 재귀 문법은 증명 항을 만드는 전면부 기능이다. 커널은 전면부가 만든 명시적 핵심 항과 선언만 검사한다. 현행 참조 문서는 핵심 언어를 의존 함수, 우주, 귀납형과 몫으로 설명한다. [Lean 타입 체계](https://lean-lang.org/doc/reference/latest/The-Type-System/) [Lean 커널](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/)

## 2. 결론 여섯 개

### 판정 1. 통상적인 연역 수학의 증명 방식은 넓게 표현된다

Lean은 직접 증명, 경우 나누기, 귀납법, 정초 귀납법, 등식 추론과 귀류법을 표현한다. 고전 공리를 사용하면 고전적 존재 증명과 선택을 쓰는 증명도 표현한다. 다만 각 증명 방식이 별도 커널 명령으로 존재하지는 않는다. 전면부는 표면 증명을 의존 함수와 귀납형의 재귀자로 번역한다. [Lean 커널과 정교화 결과](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/) [Lean 귀납형](https://lean-lang.org/doc/reference/latest/The-Type-System/Inductive-Types/) [Lean 재귀 정의](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/)

`Theorem Proving in Lean 4`은 Lean의 의존 타입 이론이 거의 모든 통상적 수학 정리를 다룰 만큼 강하다고 설명한다. 이 설명은 닫힌 “모든 증명 방식” 정리를 제시하지 않는다. “통상적”이라는 범주에는 고정된 수학적 경계가 없기 때문이다. 따라서 정확한 판정은 **통상적인 유한 연역 증명을 매우 넓게 형식화할 수 있다**이다. [공식 입문](https://lean-lang.org/theorem_proving_in_lean4/introduction.html) [의존 타입 이론](https://lean-lang.org/theorem_proving_in_lean4/Dependent-Type-Theory/)

다음 표는 증명 방식을 Lean이 다루는 층을 구별한다.

| 증명 방식 | Lean에서의 처리 | 경계 |
|---|---|---|
| 직접 증명, 함의, 전칭 명제 | 의존 함수와 함수 적용 | 핵심 논리가 직접 지원한다. |
| 존재 증명 | `Exists`의 증명 항 | `Exists`는 `Prop`이므로 일반 프로그램은 증명에서 증인을 추출하지 못한다. |
| 경우 나누기와 수학적 귀납법 | 귀납형 재귀자 | 귀납형은 우주 조건과 엄격 양성 조건을 만족해야 한다. |
| 강한 귀납법과 정초 귀납법 | `WellFounded.fix`, 접근 가능성 증명 | 종료 관계와 감소 증명이 필요하다. |
| 초한 귀납법 | 형식화한 순서와 정초 관계 | 초한 귀납법은 별도 커널 원리가 아니다. 순서 정의와 정초성 증명이 필요하다. |
| 귀류법과 배중률을 쓰는 고전 증명 | `Classical.em`, `byContradiction` | `Classical.choice`, `propext`, `Quot.sound`에 의존한다. |
| 몫과 함수 외연성을 쓰는 증명 | 내장 `Quot`와 `Quot.sound` | 함수 외연성은 몫에서 유도된다. |
| 계산 증명과 반사 | 커널 환원, 검증한 결정 절차, 계산 증서 | 네이티브 계산을 신뢰하면 전용 공리가 생기고 신뢰 기반이 커진다. |
| 확률적 방법 | 확률 공간과 측도에 대한 정리 | 무작위 실행의 관측값만으로는 정리가 되지 않는다. |
| 공귀납 | `Prop` 값 공귀납 고정점 | Lean 타입 이론은 공귀납 자료형을 직접 지원하지 않는다. 현행 문법은 공귀납 술어를 인코딩한다. |
| 그림, 실험, 수치 관측 | 형식 명제와 검증 가능한 증서로 번역 | 관측 자료 자체를 커널이 수학적 증명으로 바꾸지 않는다. |

Lean의 현행 공귀납 기능은 이 경계를 명시한다. 타입 이론은 공귀납형을 직접 지원하지 않는다. `coinductive`와 `coinductive_fixpoint`는 `Prop`의 완비 격자에서 최대 고정점을 구성한다. [공귀납 술어 공식 절](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/)

Lean에 제출하는 증명 항은 유한한 구문이다. 무한 집합, 무한 수열과 무한 행동에 관한 정리는 함수, 귀납법이나 공귀납 술어로 유한하게 기술한다. 실제로 무한히 많은 추론 단계를 나열한 입력을 커널이 직접 받는 것은 아니다. [Lean 항과 타입](https://lean-lang.org/doc/reference/latest/The-Type-System/) [공귀납 술어 공식 절](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/)

### 판정 2. 충분히 강하고 일관된 고정 기초 체계는 모든 참인 명제를 증명하지 못한다

Lean 커널은 선택한 환경에서 도출되는 명제를 검사한다. 일관되고 효과적으로 주어진 고정 이론이 충분한 산술을 해석하면, 그 이론이 결정하지 못하는 문장이 존재한다. 따라서 그런 Lean 기초 환경은 의도한 모형의 모든 참을 증명하지 못한다. Gödel의 원 논문은 충분히 강한 형식 체계의 불완전성을 입증했다. Rosser는 단순 일관성만으로도 결정 불가능 문장을 얻도록 첫 정리를 강화했다. [Gödel 1931 원 논문](https://doi.org/10.1007/BF01700692) [Rosser 1936 원 논문](https://doi.org/10.2307/2269028)

이 한계는 “Lean의 자동화가 아직 약하다”는 공학적 한계가 아니다. 더 강한 참인 공리를 추가하면 기존 독립 명제를 결정할 수 있다. 그러나 새 기초 체계도 일관되고 효과적으로 주어졌으며 충분한 산술을 해석하면 다시 불완전하다. 모순 공리를 추가하면 모든 명제를 도출할 수 있지만, 그 결과는 참에 대한 완전한 증명 체계가 아니다.

다음 세 문장은 서로 다르다.

1. `P`가 선택한 Lean 환경에서 증명 가능하다.
2. `P`가 의도한 수학 모형에서 참이다.
3. Lean의 자동화가 `P`의 증명 항을 찾는다.

첫 문장은 형식 도출 관계를 말한다. 둘째 문장은 의미론을 말한다. 셋째 문장은 증명 탐색 능력을 말한다. 한 문장이 다른 문장을 자동으로 보장하지 않는다.

또한 Lean의 실제 타입 검사 알고리즘 자체도 모든 입력에서 종료한다고 보장되지 않는다. 현행 참조 문서는 타입이 환원 뒤 보존되는 주제 축약이 성립하지 않는다고 밝힌다. 알고리즘적 정의적 동등성도 반드시 추이적이지 않다. 의도적으로 만든 입력에서는 검사기가 종료하지 않을 수 있다. 문서는 이 성질들이 논리적 건전성을 깨지 않는다고 설명한다. [커널 절의 메타이론 한계](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/)

따라서 “유한한 올바른 증명 항이면 언제나 자원 제한 없이 즉시 검사된다”도 Lean이 보장하는 문장이 아니다. 실제 검사는 메모리, 시간, 재귀 깊이와 구현에 제한을 받는다.

### 판정 3. 핵심 규칙, 표준 공리와 사용자 공리를 구별해야 한다

Lean 4.34.0-rc2의 핵심 타입 이론은 다음 구성을 직접 다룬다.

- 의존 함수와 람다 항
- 비누적 우주 계층과 우주 다형성
- 비서술적 `Prop`
- 정의적으로 증명 무관한 증명
- 귀납형, 생성자, 재귀자와 귀납형 환원
- 내장 몫 형성자 `Quot`, `Quot.mk`, `Quot.lift`, `Quot.ind`
- `Quot.lift`의 정의적 환원
- 함수와 단일 생성자 구조체의 정의적 η-동등성.

현행 공식 소스는 함수 타입의 우주를 `imax`로 계산한다. 같은 소스는 같은 명제의 두 증명을 정의적 동등성으로 처리한다. [함수 타입 우주 계산 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L144-L165) [증명 무관성 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L930-L939)

Lean이 수학 내용 때문에 기본으로 제공하는 공리 상수는 세 개다.

| 공리 | 형식 | 역할 |
|---|---|---|
| `Classical.choice` | `Nonempty α → α` | 지워진 존재 증명에서 비계산적으로 값을 고른다. |
| `propext` | `(a ↔ b) → a = b` | 논리적으로 동치인 명제를 같은 명제로 취급한다. |
| `Quot.sound` | `r a b → Quot.mk r a = Quot.mk r b` | 몫 관계가 몫의 등식을 만든다. |

`Classical.choice`는 임의 우주의 `Nonempty α`에서 값을 고른다. 표준 라이브러리는 이 상수에서 타입 족 전체의 선택 함수도 유도한다. 따라서 이 상수는 배중률만 추가하는 원리보다 강한 선택 기능을 제공한다. [선택 공리 공식 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Prelude.lean#L778-L833) [선택 원리 유도](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Classical.lean#L115-L132)

공식 참조와 소스가 이 세 상수를 같은 형식으로 선언한다. [Lean 표준 공리](https://lean-lang.org/doc/reference/latest/Axioms/) [선택·몫 공리 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Prelude.lean#L738-L809) [명제 외연성 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Core.lean#L1600-L1610) [몫 건전성 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Prelude.lean#L4765-L4778)

배중률은 커널 원시 규칙도 별도 기본 공리도 아니다. `Classical.em`은 선택, 명제 외연성과 함수 외연성에서 Diaconescu 방식으로 유도된다. 함수 외연성은 `Quot.sound`와 `Quot.lift`의 환원에서 유도된다. 실제 `Classical.em` 구현과 `#print axioms` 결과에는 세 수학 공리가 나타난다. [고전 논리 구현](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Classical.lean#L28-L72) [몫에서 함수 외연성 유도](https://lean-lang.org/doc/reference/latest/The-Type-System/Quotients/)

`sorryAx`, `Lean.trustCompiler`, `Lean.ofReduceBool`과 `Lean.ofReduceNat`도 공식 참조가 열거하는 표준 공리다. 이 상수는 수학의 기초 원리를 채택하려는 공리가 아니다. `sorryAx`는 미완성 항을 채운다. 나머지는 컴파일러 계산에 의존했다는 사실을 추적한다. Lean 4.29부터 `native_decide` 계열은 호출별 전용 공리를 만든다. [공리와 네이티브 계산](https://lean-lang.org/doc/reference/latest/Axioms/) [증명 검증의 `Lean.trustCompiler` 절](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

사용자는 어떤 잘 형성된 타입에도 `axiom`을 선언할 수 있다. 커널은 공리의 타입이 타입인지 검사한다. 커널은 공리의 참이나 다른 공리와의 일관성을 검사하지 않는다. 그래서 추가 공리는 표현 범위를 넓히지만, 결론을 추가 공리에 상대적인 결론으로 바꾼다. [공리 선언과 일관성](https://lean-lang.org/doc/reference/latest/Axioms/)

공리 추가가 모든 논리 기초를 그대로 흡수하는 것은 아니다. Lean의 내장 등식은 `Prop`이고 모든 등식 증명은 정의적으로 같다. 따라서 등식 증명의 여러 경로를 자료로 구별하는 호모토피 타입 이론의 정체성 개념은 내장 `Eq`로 직접 얻지 못한다. 공식 참조는 증명 무관성에서 등식 증명 유일성과 공리 K가 따른다고 명시한다. 이런 기초는 별도 객체 논리나 별도 `Type` 값 등식 구조로 인코딩해야 한다. [등식 증명 유일성](https://lean-lang.org/doc/reference/latest/Basic-Propositions/)

### 판정 4. 다른 논리를 인코딩하면 상대적 보장을 얻고 원생 보장을 잃는다

Lean 안에 다른 논리의 식, 문맥과 도출 규칙을 자료형으로 정의할 수 있다. 도출 규칙을 귀납형으로 정의하면 객체 논리의 증명은 그 귀납형의 값이 된다. Lean4Lean은 이 방법으로 Lean의 표현식, 타입 이론과 검사기를 Lean 안에서 다룬다. 이 프로젝트는 객체 이론과 메타 이론을 분리할 수 있다는 실물 사례다. [Lean4Lean 논문](https://arxiv.org/abs/2403.14064) [Lean4Lean 현행 소스](https://github.com/digama0/lean4lean/tree/3adf6da696960c671096243420be6ea0f04b686e)

객체 논리에는 두 가지 대표적 인코딩이 있다.

| 인코딩 | 얻는 것 | 잃거나 별도로 입증할 것 |
|---|---|---|
| 얕은 인코딩 | Lean의 함수, `Prop`, 자동화와 라이브러리를 바로 쓴다. | Lean의 증명 무관성, 고전 공리와 외연성이 객체 논리에 섞일 수 있다. 객체 논리 고유 규칙만 썼다는 보장이 약하다. |
| 깊은 인코딩 | 식과 도출 규칙을 별도 자료형으로 둔다. 객체 논리 규칙을 정확히 제한할 수 있다. | 구문 대응, 치환, 도출의 건전성·완전성, 의미 대응을 별도로 증명해야 한다. Lean 자동화를 바로 쓰기 어렵다. |

깊은 인코딩에서 `Derivable Γ φ`의 값을 만들면 Lean 커널은 **작성한 `Derivable` 정의에 따라** 도출이 구성됐음을 검사한다. 커널은 그 정의가 원래 논리의 규칙과 같은지 검사하지 않는다. 객체 논리의 의미론 `Models Γ φ`로 옮기려면 `Derivable Γ φ → Models Γ φ` 같은 건전성 정리가 필요하다.

객체 논리의 모순은 자동으로 Lean의 모순이 되지 않는다. 예를 들어 객체 논리 안의 `Falseₒ` 도출은 그 자료형의 값이다. `Falseₒ`를 Lean의 `False`로 보내는 건전성 해석을 추가로 가정하거나 증명해야 Lean 전체에 영향이 생긴다.

반대로 객체 논리를 Lean 안에 정의해도 Lean의 메타이론은 바뀌지 않는다. 객체 논리의 증명 항을 `Prop`에 두면 Lean의 증명 무관성과 제거 제한을 받는다. 증명 과정을 구별해야 하면 증명 나무를 `Type`에 두고, 그 증명 나무가 도출을 나타낸다는 별도 정리를 두어야 한다.

객체 논리 인코딩이 주는 일관성 결과도 상대적이다. Lean 안에서 객체 논리의 모형을 만들면 “Lean의 기초를 가정하면 객체 논리가 건전하다”는 결과를 얻는다. 같은 강도의 체계가 자기 일관성을 무조건 입증한다는 결론은 불완전성 한계를 받는다.

### 판정 5. 타입 형성, 제거와 계산에는 구체적인 경계가 있다

#### 5.1 우주 계층

`Prop`은 `Sort 0`이다. `Type u`는 `Sort (u + 1)`이다. `Prop`은 모든 우주의 타입을 양화할 수 있는 비서술적 우주다. `Type` 계층은 서술적이고 비누적이다. 한 타입은 자동으로 더 높은 `Type`의 원소가 되지 않는다. `ULift`나 `PLift`가 필요한 경우가 있다. [Lean 우주](https://lean-lang.org/doc/reference/latest/The-Type-System/Universes/) [현행 우주 계산 구현](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L144-L165)

우주 변수는 선언을 여러 우주 높이에서 인스턴스화하는 스키마 매개변수다. 우주 높이를 일반 Lean 자료처럼 한 항 안에서 전칭 양화하는 기능과 같지 않다. 서로 다른 우주 인스턴스는 자동으로 같은 값이 되지 않는다.

이 계층은 `Type : Type`을 허용하지 않는다. 그래서 “모든 타입을 원소로 가지며 자기 자신도 원소인 한 타입”을 Lean의 내장 우주로 만들 수 없다. 필요한 전 우주 명제는 우주 다형 선언으로 만든다.

#### 5.2 귀납형과 `Prop` 제거

귀납형 선언은 생성자의 타입, 우주, 매개변수, 지표와 재귀 발생을 검사받는다. 재귀 발생은 엄격 양성 위치에 있어야 한다. 상호 귀납형은 같은 매개변수와 결과 우주를 가져야 한다. 중첩 귀납형은 커널이 상호 귀납형으로 번역할 수 있는 경우에만 허용한다. [귀납형 형성 조건](https://lean-lang.org/doc/reference/latest/The-Type-System/Inductive-Types/) [귀납형 검사 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/inductive.cpp#L254-L300) [양성과 우주 검사 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/inductive.cpp#L435-L489)

`Prop`의 일반 증명은 자료를 만들도록 제거할 수 없다. 증명이 실행 시 지워지고, 같은 명제의 모든 증명이 정의적으로 같기 때문이다. `Or`, `Exists`와 `Nonempty`의 증명에서 어느 생성자나 증인이 쓰였는지 일반 프로그램이 관찰하면 증명 무관성과 충돌한다.

Lean은 구문상 부분단일자인 명제에는 큰 제거를 허용한다. 생성자가 없거나 하나뿐이고, 자료를 드러내지 않는 생성자이면 재귀자의 결과가 임의의 `Sort u`에 놓일 수 있다. `False`, `True`, `And`와 `Eq`가 대표 예다. `Or`, `Exists`와 일반 `Nonempty`는 이 예외에 들지 않는다. [부분단일자 제거](https://lean-lang.org/doc/reference/latest/The-Type-System/Inductive-Types/) [제거 우주 판정 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/inductive.cpp#L522-L588)

이 경계는 “존재 정리를 증명할 수 없다”는 뜻이 아니다. `∃ x, P x`를 증명할 수 있다. 다만 그 증명을 일반 실행 자료로 꺼내지 못한다. 실행 가능한 증인이 필요하면 `Subtype`, `Sigma` 또는 증인 자료와 별도 정리를 사용한다. 고전 선택으로 증인을 고를 수도 있지만 결과는 `noncomputable`이다.

#### 5.3 재귀, 종료, `partial`과 `unsafe`

커널 핵심 언어에는 표면 재귀 정의와 종료 검사기가 없다. 구조 재귀는 재귀자 사용으로 번역된다. 정초 재귀는 접근 가능성 증명과 `WellFounded.fix`로 번역된다. 전면부가 만든 항과 종료 근거를 커널이 검사한다. [재귀 정의 개요](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/) [정초 재귀](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/)

재귀 정의의 다섯 경계를 구별해야 한다.

| 형식 | 논리 안의 의미 | 실행 | 증명에서의 사용 |
|---|---|---|---|
| 구조 재귀 | 전체 함수이며 재귀자 환원이 적용된다. | 가능 | 정의적으로 계산하기 좋다. |
| 정초 재귀 | 전체 함수이며 감소 증명을 가진다. | 가능 | 정의 방정식이 흔히 명제적 동등성으로만 주어진다. |
| `partial_fixpoint` | 방정식을 만족하는 전체 함수 하나를 논리적으로 고른다. | 원래 재귀 코드를 실행한다. | 전개 정리와 일부 모나드의 부분 정확성 정리를 쓴다. 런타임 종료를 보장하지 않는다. |
| `partial def` | 값이 하나 이상 존재하는 반환형의 임의 불투명 상수로 취급한다. | 종료하지 않을 수 있는 원래 코드를 실행한다. | 구현 방정식을 얻지 못한다. 상수 이름만 논리에 남는다. |
| `unsafe def` | 안전한 논리 환경에서 참조할 수 없다. | 일반 재귀와 위험 연산을 허용한다. | 정리는 `unsafe`일 수 없으므로 증명 의존 경로가 차단된다. |

`partial def`의 반환형에는 `Nonempty`나 `Inhabited` 인스턴스가 필요하다. 즉, 반환형에 값이 하나 이상 존재해야 한다. 그렇지 않으면 `Unit → Empty` 같은 불투명 상수에서 `Empty`의 값을 얻고 모든 명제를 증명할 수 있다. 현행 전면부는 존재하는 반환값을 논리용 불투명 본문으로 넣는다. 재귀 구현은 별도 `partial` 선언으로 컴파일한다. [부분 함수 공식 절](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/) [부분 정의 전면부 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/Main.lean#L20-L36) [부분 구현 분리 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/Basic.lean#L255-L294)

핵심 타입 이론은 `unsafe` 상수를 수학 정리의 근거로 쓰지 못하게 막는다. 안전한 선언에서 `unsafe` 상수를 참조하면 커널이 거부한다. 그러나 같은 프로세스에서 실행한 악의적 메타프로그램은 메모리나 검사 환경을 공격할 수 있다. 고위험 검증은 격리 빌드와 외부 재검사가 필요하다. 또한 `implemented_by`가 논리용 구현을 다른 런타임 구현으로 바꾸면, 증명은 논리용 구현에 관한 정리다. 실행 프로그램이 그 정리와 같은 동작을 한다는 보장은 별도 신뢰 조건이다. [unsafe 정의와 구현 교체](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/) [안전성 검사 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L101-L117) [악의적 코드 검증 경계](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

#### 5.4 몫

`Quot`은 귀납형이 아닌 커널 원시 구성이다. 커널은 `Quot`, `Quot.mk`, `Quot.lift`와 `Quot.ind`를 환경에 추가한다. `Quot.lift f h (Quot.mk r a)`는 정의적으로 `f a`로 환원된다. `Quot.sound`는 관련된 대표 둘이 몫에서 같다는 공리다. [몫 공식 절](https://lean-lang.org/doc/reference/latest/The-Type-System/Quotients/) [몫 원시 상수 구현](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/quot.cpp#L61-L125)

같은 동치류의 두 대표가 자동으로 정의적 동등한 것은 아니다. `Quot.sound`가 명제적 등식을 준다. 정의적 환원은 관계를 존중한다고 입증한 함수의 `Quot.lift` 적용에 걸린다.

`Quot`은 귀납형이 아니므로 중첩 귀납형을 감싸는 외부 타입 생성자로 사용할 수 없다. 이 경우 몫이 없는 귀납형과 별도 동치 관계로 다시 설계해야 한다. [몫과 중첩 귀납형](https://lean-lang.org/doc/reference/latest/The-Type-System/Quotients/)

#### 5.5 증명 무관성, 고전 선택과 계산

`p : Prop`의 모든 증명은 정의적으로 같다. 이 규칙은 공리 의존 목록에 나타나는 상수가 아니라 커널의 정의적 동등성 규칙이다. 그래서 `#print axioms`가 비었다고 해도 증명 무관성, 우주와 귀납형 규칙을 쓰지 않았다는 뜻은 아니다. [Lean 명제](https://lean-lang.org/doc/reference/latest/The-Type-System/Propositions/) [증명 무관성 구현](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L930-L939)

`Classical.choice`는 `Nonempty α`라는 지워지는 증명에서 `α`의 값을 고른다. 이 선택은 계산할 수 없으므로 그 값을 실행 자료에 쓰는 정의는 `noncomputable`이어야 한다. 공리와 `propext`가 포함된 항은 커널 정규화가 막힐 수도 있다. 반면 컴파일러는 증명과 타입을 지우므로, 공리를 증명에만 쓴 프로그램은 실행할 수 있다. [선택과 계산](https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/) [현행 공리 참조](https://lean-lang.org/doc/reference/latest/Axioms/)

커널 환원과 컴파일 실행도 구별해야 한다. `rfl`이나 `decide`가 커널 환원으로 닫히면 작은 커널 계산에 의존한다. `native_decide`는 컴파일된 계산 결과를 전용 공리로 주장한다. 전용 공리는 감사할 수 있지만, 결과의 참은 컴파일러와 런타임 구현에도 의존한다.

### 판정 6. 커널 수락, 공리 감사, 의미 대응은 서로 다른 보장이다

Lean 증명의 신뢰는 다음 다섯 층을 가진다.

| 층 | 보장 | 보장하지 않는 것 |
|---|---|---|
| 형식문 정교화 | 현재 문법, 표기와 타입 클래스에 따라 핵심 명제가 생성됐다. | 사람이 읽은 문장과 같은 뜻인지 보장하지 않는다. |
| 커널 수락 | 현재 환경의 정의·정리·공리에서 핵심 명제의 증명 항이 타입을 가진다. | 공리가 참인지, 커널 구현에 결함이 없는지 보장하지 않는다. |
| 공리 감사 | 정리가 의존하는 공리 상수의 전이 폐쇄를 열거한다. | 커널 내장 규칙, 정의의 의도, 공리의 일관성을 검사하지 않는다. |
| 독립 재검사 | 환경 우회와 한 구현의 결함 일부를 탐지한다. | 모든 검사기가 공유하는 결함을 배제하지 않는다. |
| 의미 대응 검토 | 형식 정의와 정리가 원래 수학 명제를 나타내는지 판정한다. | 커널이 자동으로 수행하지 않는다. |

일상적인 정직한 개발에서는 편집기 통과나 `lake build`가 형식문과 증명 항을 정교화하고 커널이 수락했음을 보장한다. `#print axioms`는 `sorryAx`, 사용자 공리와 네이티브 계산 공리를 찾는다. `lean4checker --fresh`는 `.olean`의 선언을 같은 Lean 커널에 다시 넣어 환경 상태 우회를 잡는다. [Lean 증명 검증](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

`lean4checker`는 독립 커널이 아니다. `.olean` 구조를 신뢰하며 같은 C++ 커널을 다시 사용한다. 악의적 증명에는 신뢰한 도전 형식문과 제출 형식문을 비교하고, 격리된 빌드와 외부 커널을 쓰는 `comparator`가 공식 권고의 최상 단계다. 현행 `comparator`는 허용 공리, 정리 형식문의 동일성과 외부 커널 실행을 검사한다. [공식 `comparator` 소스와 계약](https://github.com/leanprover/comparator/tree/8d84e678dc9954b12db91f7f3167a169b309e0c8)

이 구별은 이론상의 예방 문구만이 아니다. 2026년 7월에는 중첩 귀납형 검사 결함으로 공식 커널이 `False`의 항을 수락했다. 같은 산출물은 당시 별도 결함이 있던 구판 nanoda도 통과했다. Lean 책임자의 사후 보고는 최신 두 구현을 함께 사용해야 한다고 결론 낸다. [중첩 귀납형 결함 사후 보고](https://leodemoura.github.io/blog/2026-8-1-postmortem-for-kernel-soundness-bug-14576/)

2026-08-21의 Lean 4.33.1은 해당 조사에서 찾은 커널·런타임 결함 전건의 수정판으로 발표됐다. 현행 참조판 4.34.0-rc2의 소스는 중첩 귀납형의 사라진 매개변수를 다시 검사한다. 복원한 생성자와 재귀자도 다시 검사한다. `Prop` 판정은 우주 수준을 정규화하고 타입이 실제 `Sort`인지 먼저 확인한다. GMP를 쓰는 일반 빌드는 6.3.0 이상을 요구한다. 사용자가 `FORCE_GMP`로 이 검사를 우회하면 소스가 건전성 경고를 낸다. [커널 결함 조사 사후 보고](https://leodemoura.github.io/blog/2026-8-24-postmortem-for-the-kernel-soundness-bug-hunt/) [Lean 4.33.1 공식 릴리스](https://github.com/leanprover/lean4/releases/tag/v4.33.1) [4.33.0 수정 내역](https://lean-lang.org/doc/reference/latest/releases/v4.33.0/) [중첩 귀납형 재검사 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/inductive.cpp#L1315-L1352) [`Prop` 판정 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp#L383-L389) [GMP 요건과 우회 경고 소스](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/CMakeLists.txt#L307-L350)

현행 참조 문서는 검토하지 않은 인공지능 생성 증명을 악의적 입력과 같은 검증 단계로 취급한다. P vs NP 연구처럼 보상이 크고 모델이 증명 코드를 만드는 환경에서는 `lake build`만으로 공식 권고를 충족하지 않는다. 신뢰한 형식문, 공리 허용 목록, 격리 빌드와 최신 독립 커널이 필요하다. [악의적 증명 검증 기준](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

## 3. 기존 두 문서와의 대조

### 3.1 `Lean-중심-혼합-정본-논의.md`

| 기존 주장 | 판정 | 심층 검토 결과 |
|---|---|---|
| Lean 선언과 증명 항이 형식 수학 내용을 담을 수 있다. | 일치 | 정의, 명제와 도출 증거를 담을 수 있다. `partial`·`unsafe`·객체 논리 경계는 별도로 기록해야 한다. |
| 불확실 명제를 `def p_ne_np : Prop`로 정의해도 참을 가정하지 않는다. | 일치 | 명제의 이름만 만든다. 증명 항이나 공리 상수를 만들지 않는다. |
| `axiom p_ne_np_proof : P ≠ NP`는 증명 없이 사용할 수 있게 한다. | 일치 | 커널은 공리의 참과 일관성을 검사하지 않는다. |
| Lean 커널은 연구 지도 자료구조의 의도한 의미를 자동 검사하지 않는다. | 일치 | 자료구조 불변식은 Lean 정리나 별도 결정 검사기로 입증해야 한다. |
| 사용한 공리와 기초 프로필은 Lean 환경에서 바로 얻는다. | 수정 필요 | `#print axioms`는 공리 상수만 열거한다. 커널 내장 규칙, `partial`, 런타임 교체와 의미 대응은 별도 감사가 필요하다. 기초 프로필은 연구 체계가 정의해야 한다. |
| Lean 자체는 하나의 형식 기초를 제공한다. | 정밀화 필요 | 커널은 하나의 핵심 타입 이론을 구현한다. 각 import 환경은 공리와 정의로 그 이론을 확장한다. 객체 논리는 그 핵심 이론 안에 다시 인코딩할 수 있다. |
| 자연어와 Lean 선언이 충돌하면 Lean 선언이 수학 내용의 정본이다. | 설계 선택 | Lean이 보장하는 사실이 아니다. 그렇게 정본 경계를 정할 수 있으나, 원문 의미 대응은 사람과 별도 검토가 맡는다. |
| 현재 저장소와 실행 환경에는 Lean 도구체인이 없다. | 일치 | 2026-08-29에 `lean`과 `lake` 명령을 다시 찾았으나 발견하지 못했다. 이 사실은 Lean의 표현력 판정과 독립이다. |

### 3.2 `도구-지형-실사.md`

| 기존 주장 | 판정 | 심층 검토 결과 |
|---|---|---|
| 커널 통과는 import의 정의·정리·공리에서 형식 명제가 따른다는 뜻이다. | 일치 | 정직한 빌드와 정상 커널을 전제로 한 정확한 설명이다. |
| 자연어와 형식 명제의 의미 일치는 별도 검토 대상이다. | 일치 | 공식 검증 안내가 같은 경계를 명시한다. |
| `lake build`, `#print axioms`, `lean4checker --fresh`를 구별해야 한다. | 일치하나 불완전 | 악의적이거나 미검토 인공지능 증명에는 `comparator`와 최신 외부 커널 단계가 더 필요하다. |
| Lean 상태 표현을 “커널 수락과 공리 의존”으로 요약한다. | 수정 필요 | 커널 수락과 공리 의존은 서로 다른 상태다. 도구체인 판본, 형식문 동일성, 내장 규칙과 독립 재검사도 분리해야 한다. |
| Lean은 뭉텅이·연결 가설의 연구 의미를 직접 제공하지 않는다. | 일치 | 사용자 자료형으로 표현할 수 있지만 커널의 원생 연구 지도 의미론은 아니다. |
| Complexitylib과 DescriptiveComplexity가 제공하는 P·NP 형식화를 재사용할 수 있다. | 이 검토에서 미판정 | 이 문서는 두 라이브러리의 정의와 증명을 다시 감사하지 않았다. 기존 실사의 소스 판정에 의존한다. |

기존 두 문서의 가장 큰 수정점은 검증 단계다. `lake build`와 `lean4checker`만으로 고위험 인공지능 제출의 신뢰 계약을 닫을 수 없다. 두 문서의 “Lean 검증”은 커널 수락, 공리 감사, 형식문 비교와 독립 커널 검사를 각각 이름으로 적어야 한다.

## 4. `do-math` 설계와 P vs NP Lean 정의에 미치는 귀결

이 절은 현행 연구 체계와 검증 절차를 확정하지 않는다. 다음 설계 입력만 도출한다.

1. Lean 정리는 정확한 형식 명제와 기초 환경에 상대적인 입증이다. 연구 체계는 저장소, 커밋, Lean 판본, 선언 이름과 공리 의존을 함께 가리켜야 한다.
2. `P = NP`나 `P ≠ NP`의 형식문은 신뢰한 파일에서 먼저 고정해야 한다. 제출자가 계산 모형, 부호화, 환원 또는 `P`·`NP` 정의를 바꾸지 못하게 형식문과 전이 의존 정의를 비교해야 한다.
3. 불확실 명제는 `def conjecture : Prop := ...`처럼 내용만 정의할 수 있다. 불확실 명제의 증명 상수를 `axiom`이나 `sorry`로 만들면 확실한 정리의 의존 경로에 섞인다.
4. `#print axioms`만으로 기초 프로필을 완전히 감사할 수 없다. 프로필은 허용 공리, Lean 내장 규칙, 도구체인 판본, 네이티브 계산 허용 여부와 객체 논리 해석을 함께 명시해야 한다.
5. `partial` 상수는 논리적으로 안전하지만 구현 방정식이 없다. 의도한 알고리즘이나 복잡도 함수를 `partial`로 정의하면 의미 대응이 약해진다. P vs NP의 계산 모형과 시간 함수에는 전체 정의와 종료 근거를 우선 검토해야 한다.
6. `unsafe` 구현과 `implemented_by`는 논리 정리와 실행 코드가 갈라질 수 있다. 실행 결과를 증거로 쓰면 논리용 구현과 런타임 구현의 동등성을 별도로 관리해야 한다.
7. `native_decide`가 만든 전용 공리는 표준 수학 공리와 같지 않다. 계산 증서를 커널 안에서 다시 검사할지, 컴파일러 계산 공리를 허용할지 입증 유형별로 정해야 한다.
8. `Prop`의 증명 무관성 때문에 입증 기록의 서로 다른 출처와 검토 이력을 Lean 증명 항의 정체성으로 구별할 수 없다. 해당 정보는 연구 작업공간이나 별도 인증 기록에 둔다.
9. 존재 증명에서 실행 가능한 알고리즘을 얻어야 하면 `Exists`만으로 부족할 수 있다. 증인 자료와 정확성 정리를 분리하거나 `Subtype`·`Sigma`를 써야 한다.
10. 대안 기초를 Lean 안의 수학 대상으로 다루면 객체 논리의 구문, 도출과 의미 대응 정리를 구별해야 한다. 그 도출을 활성 기초 프로필의 무조건 결과로 자동 전이하면 안 된다.
11. 미검토 인공지능이 만든 고가치 증명은 공식 지침상 악의적 입력 절차를 적용할 대상이다. 신뢰한 도전 형식문, 격리 빌드, `comparator`와 최신 외부 커널을 검증 후보로 둔다.
12. Lean은 연구 과정 전체의 의미론을 자동 제공하지 않는다. 문헌 출처, 이의, 실패, 우선순위와 탐사 단서는 별도 표현·검사 문제가 남는다.

## 5. 원질문에 대한 뜻별 답

“증명 종류”가 **직접 증명, 귀납법, 귀류법, 경우 나누기, 계산 증명 같은 통상적 수학 방법**을 뜻하면, Lean은 거의 전부를 형식화할 수 있다. 일부는 핵심 논리로 직접 표현하고, 일부는 표준 공리나 검증된 인코딩으로 표현한다.

“모든 종류”가 **모든 참인 수학 명제**를 뜻하면, 충분한 산술을 표현하는 일관된 고정 기초 체계는 전부를 증명하지 못한다. 이 한계는 Gödel–Rosser 불완전성에서 온다.

“모든 종류”가 **모든 논리와 수학 기초를 Lean의 내장 규칙 그대로 사용한다**는 뜻이면, 그렇지 않다. Lean의 원생 기초는 증명 무관한 `Prop`, 비누적 우주, 귀납형과 몫을 가진 특정 의존 타입 이론이다.

“가능”이 **다른 논리를 Lean 안에 인코딩한다**는 뜻이면, 넓은 범위의 형식 논리를 객체 논리로 다룰 수 있다. 이때 커널은 인코딩한 도출을 검사한다. 원래 논리와 인코딩의 대응은 별도 정리가 맡는다.

“증명”이 **실험, 그림, 외부 프로그램 실행이나 자연어 설득 자체**를 뜻하면, Lean은 그 자료를 그대로 증명으로 수락하지 않는다. 형식 명제, 검증 가능한 증서와 의미 대응이 필요하다.

“Lean이 증명한다”가 **커널이 수락했다**는 뜻이면, 형식 도출에 대한 강한 기계 증거를 얻는다. 공리의 참, 자연어 의미, 커널 구현과 런타임의 무결성은 별도 신뢰 조건으로 남는다.

## 6. 미판정 항목

- “통상적인 모든 증명 방식”은 닫힌 열거가 아니므로 전칭 명제로 판정하지 못했다. 이 문서는 확인한 방식과 구조적 경계를 판정했다.
- Lean 4.34.0-rc2 전체 타입 이론과 C++ 구현을 함께 덮는 완성된 기계 검증은 확인하지 못했다. Lean4Lean의 검증은 진행 중이며, 2026-08-01 공식 사후 보고 시점에는 귀납형 일관성 증명이 완결되지 않았다.
- Carneiro의 2019 모형이 입증한 상대 일관성 결과를 Lean 4.34.0-rc2 전체 구현에 그대로 전이할 수 있는지는 판정하지 않았다. Lean 4가 추가한 상호·중첩 귀납형과 구현 세부를 별도로 대조해야 한다.
- Complexitylib과 DescriptiveComplexity의 P·NP 정의가 사용자가 최종 채택할 계산 모형과 같은지는 판정하지 않았다.
- P vs NP 전체 연구를 Lean으로 형식화할 때 필요한 인력, 기간과 성능은 판정하지 않았다. 표현 가능성과 실용 비용은 다른 질문이다.
- 현행 외부 커널들이 공유하지 않는 미발견 결함이 없다는 주장은 판정할 수 없다. 공식 검증 안내도 이 잔여 위험을 명시한다.

## 7. 읽고 대조한 1차 자료 전건

### 7.1 현행 Lean Language Reference

공식 참조의 `latest`는 검토일에 Lean `4.34.0-rc2`를 다뤘다. 문서 소스는 `leanprover/reference-manual` 커밋 `27991067eecfd8d9c312c943a94d6d7673ba1771`이었다. [참조 문서 첫 페이지](https://lean-lang.org/doc/reference/latest/) [문서 소스 커밋](https://github.com/leanprover/reference-manual/tree/27991067eecfd8d9c312c943a94d6d7673ba1771)

읽은 절은 다음과 같다.

- [Elaboration and Compilation](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/): 파서·정교화·커널·핵심 타입 이론·정교화 결과
- [The Type System](https://lean-lang.org/doc/reference/latest/The-Type-System/): 정의적 동등성·명제·우주
- [Universes](https://lean-lang.org/doc/reference/latest/The-Type-System/Universes/): 비서술성·비누적성·우주 다형성
- [Inductive Types](https://lean-lang.org/doc/reference/latest/The-Type-System/Inductive-Types/): 재귀자·부분단일자 제거·형성 조건·상호·중첩 귀납형
- [Recursive Definitions](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/): 구조·정초·부분 고정점·공귀납 술어·`partial`·`unsafe`
- [Axioms](https://lean-lang.org/doc/reference/latest/Axioms/): 공리 선언·일관성·표준 공리·계산·공리 감사
- [Quotients](https://lean-lang.org/doc/reference/latest/The-Type-System/Quotients/): 원시 몫·환원·함수 외연성·중첩 귀납형 제한
- [Basic Propositions](https://lean-lang.org/doc/reference/latest/Basic-Propositions/): 존재·명제 등식·등식 증명 유일성·공리 K
- [Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/): 빌드·공리 출력·`lean4checker`·`comparator`·외부 커널·잔여 신뢰
- [Lean 4.33.0 release notes](https://lean-lang.org/doc/reference/latest/releases/v4.33.0/): 2026년 커널 건전성 수정 내역.

### 7.2 Lean 4 공식 소스

기능 판정은 참조판과 같은 Lean 태그 `v4.34.0-rc2`, 커밋 `6a10ac8c22beadecabdbb0919c2b50214762f91d`에 고정했다. [Lean 공식 소스 태그](https://github.com/leanprover/lean4/tree/6a10ac8c22beadecabdbb0919c2b50214762f91d)

직접 읽은 구현 파일은 다음과 같다.

- [`src/kernel/type_checker.cpp`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/type_checker.cpp): 우주, 안전성, `Prop` 판정, 증명 무관성, 정의적 동등성
- [`src/kernel/inductive.cpp`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/inductive.cpp): 귀납형 형성, 양성, 제거 우주, 중첩 귀납형 번역과 재검사
- [`src/kernel/quot.cpp`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/quot.cpp): 몫 원시 상수 생성
- [`src/kernel/environment.cpp`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/environment.cpp): 공리·정의·정리·불투명·상호 정의 검사
- [`src/kernel/declaration.h`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/declaration.h)와 [`declaration.cpp`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/kernel/declaration.cpp): 선언 종류와 안전성
- [`src/Lean/Declaration.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Declaration.lean): Lean 측 선언 표현
- [`src/Init/Prelude.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Prelude.lean): `Quot`, `sorryAx`, `Classical.choice`, `Quot.sound`
- [`src/Init/Core.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Core.lean): `propext`, 컴파일러 신뢰 공리
- [`src/Init/Classical.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Init/Classical.lean): 배중률과 선택 원리 유도
- [`src/Lean/Elab/PreDefinition/Main.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/Main.lean)과 [`Basic.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/Basic.lean): 구조·정초·부분·unsafe 정의의 분기와 컴파일
- [`src/Lean/Elab/PreDefinition/MkInhabitant.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/MkInhabitant.lean): `partial` 정의의 논리용 반환값 구성
- [`src/Lean/Elab/PreDefinition/PartialFixpoint/Main.lean`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Elab/PreDefinition/PartialFixpoint/Main.lean): 부분 고정점 구성
- [`src/CMakeLists.txt`](https://github.com/leanprover/lean4/blob/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/CMakeLists.txt): 판본과 GMP 건전성 요건.

### 7.3 공식 교재와 저자 자료

- `Theorem Proving in Lean 4` 소스 커밋 `4e28129fdd58037f8f5857548d5e99fe4fb0cc57`, 도구체인 `v4.34.0-rc1`: [Dependent Type Theory](https://lean-lang.org/theorem_proving_in_lean4/Dependent-Type-Theory/), [Propositions and Proofs](https://lean-lang.org/theorem_proving_in_lean4/Propositions-and-Proofs/), [Axioms and Computation](https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/), [소스 커밋](https://github.com/leanprover/theorem_proving_in_lean4/tree/4e28129fdd58037f8f5857548d5e99fe4fb0cc57)
- Leonardo de Moura·Sebastian Ullrich, [The Lean 4 Theorem Prover and Programming Language](https://lean-lang.org/papers/lean4.pdf), 2021
- Sebastian Ullrich, [An Extensible Theorem Proving Frontend](https://lean-lang.org/papers/thesis-sebastian.pdf), 2023
- Mario Carneiro, [The Type Theory of Lean](https://github.com/digama0/lean-type-theory/releases/tag/v1.0), 2019
- Mario Carneiro, [Lean4Lean: Towards a Verified Typechecker for Lean, in Lean](https://arxiv.org/abs/2403.14064), 2024
- Lean4Lean 현행 커밋 `3adf6da696960c671096243420be6ea0f04b686e`: [소스와 검증 범위](https://github.com/digama0/lean4lean/tree/3adf6da696960c671096243420be6ea0f04b686e).

### 7.4 건전성 사건과 검증 도구

- Leonardo de Moura, [Postmortem for Kernel Soundness Bug #14576](https://leodemoura.github.io/blog/2026-8-1-postmortem-for-kernel-soundness-bug-14576/), 2026-08-01
- Leonardo de Moura, [Postmortem for the Kernel Soundness Bug Hunt](https://leodemoura.github.io/blog/2026-8-24-postmortem-for-the-kernel-soundness-bug-hunt/), 2026-08-24
- `leanprover/comparator` 커밋 `8d84e678dc9954b12db91f7f3167a169b309e0c8`: [README와 구현](https://github.com/leanprover/comparator/tree/8d84e678dc9954b12db91f7f3167a169b309e0c8)
- `ammkrn/nanoda_lib` 커밋 `05055695879dfebb6628a67da88ceca6cd6b0421`: [독립 Rust 검사기 소스](https://github.com/ammkrn/nanoda_lib/tree/05055695879dfebb6628a67da88ceca6cd6b0421).

### 7.5 불완전성 원전

- Kurt Gödel, [Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I](https://doi.org/10.1007/BF01700692), 1931
- J. Barkley Rosser, [Extensions of Some Theorems of Gödel and Church](https://doi.org/10.2307/2269028), 1936.

## 8. 최종 검증 결과

필수 여섯 판정은 모두 근거를 확인했다. 기존 두 문서의 Lean 검증 경계에는 수정할 주장이 있다. `comparator`와 외부 커널 단계가 빠졌고, 공리 의존이 기초 프로필 전체를 뜻하는 것처럼 읽힐 수 있다. 나머지 주요 주장에는 반증 근거를 발견하지 못했다.

Lean의 추상 논리, 커널 구현과 자연어 의미를 한 보장으로 합치는 설명은 검증을 통과하지 못한다. 세 층을 분리하면 원질문은 뜻별로 답할 수 있다. `do-math`의 정확한 검증 절차는 이 문서만으로 확정하지 않는다.
