---
유형: 정의 지도
범위: 원자료 6절 요구 1~3
상태: PASS 22/22 상태 입력
---

# P 대 NP 정의 지도

이 문서는 원자료 6절의 요구 1~3을 연구에서 재사용할 정의와 명제로 고정한다. 요구 4는 `barriers.md`가, 요구 5는 `barriers.md`와 `claim-source-matrix.md`가 소유한다. 이 문서는 요구 4와 요구 5의 결론을 만들지 않는다.

## 사용 규칙

각 명제는 아래 여섯 필드를 갖는다. `재판독 정리 좌표`는 원문을 다시 읽은 정리의 ID다. `원문 인용 좌표`는 원문에서 확인할 자리다. 확인 강도는 다음 닫힌 어휘만 쓴다.

| 확인 강도 | 뜻 |
|---|---|
| 원문 재판독 확인 | 재판독 정리가 원문의 정의 또는 정리를 원문 좌표와 함께 기록했다. |
| 형식화 교차 확인 | 독립 형식화가 같은 정의 또는 정리를 선언 좌표와 함께 기록했다. |
| 조건부 원문 확인 | 원문이 전제와 결론을 분리한 조건문으로 기록했다. |

## 요구 1: 계산 모형, 다항시간, 검증자, \(P\subseteq NP\)

### D-01: 결정론적 다항시간과 \(P\)

| 필드 | 내용 |
|---|---|
| 전제 | 고정 유한 알파벳 위의 문자열 언어와 결정론적 Turing machine을 쓴다. 시간은 입력 길이별 최악 경우 시간이다. |
| 결론 | \(P\)는 어떤 결정론적 Turing machine이 다항시간에 판정하는 언어의 계급이다. |
| 적용 범위 | 고전적 이산 문자열 결정 문제다. 양자 모형, BSS 모형, 평균 경우와 실제 실행 시간에는 적용하지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C03·Q01~Q03, `readings/L17.md` C02~C03·Q02~Q03. |
| 원문 인용 좌표 | Cook, p.1~2, §1, \(T_M(n)\) 식과 \(P\) 정의식. Arora–Barak, PDF 물리 43~45 / Definition 1.20. |
| 확인 강도 | 원문 재판독 확인 |

### D-02: 검증자, \(NP\), \(P\subseteq NP\)

| 필드 | 내용 |
|---|---|
| 전제 | 관계 \(R(w,y)\)가 결정론적 다항시간에 판정되고, 인증서 \(y\)의 길이가 \(|w|\)의 다항식으로 제한된다. |
| 결론 | \(L\in NP\)는 \(w\in L\Longleftrightarrow\exists y\,(|y|\le |w|^k\land R(w,y))\)를 뜻한다. \(P\)의 판정기를 \(y\)를 무시하는 검증자로 택할 수 있으므로 \(P\subseteq NP\)다. |
| 적용 범위 | YES 입력의 존재 인증과 모든 입력에서 멈추는 검증자에 한정한다. 단지 증명서가 존재한다는 사실은 \(NP\) 소속을 뜻하지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C04~C05·Q04·Q06, `readings/L17.md` C04·Q04, `readings/L21.md` C09. |
| 원문 인용 좌표 | Cook, p.2, §1, `checking relation` 문단과 \(NP\) 정의식. Arora–Barak, PDF 물리 56~59 / Definition 2.1·2.5, Theorem 2.6. Isabelle 형식화, PDF p.375~378 / `P-subseteq-NP`, `P-eq-NP`. |
| 확인 강도 | 형식화 교차 확인 |

## 요구 2: many-one 환원, NP-complete, SAT, 3-SAT

### D-03: 다항시간 many-one 환원

| 필드 | 내용 |
|---|---|
| 전제 | 함수 \(f\)가 다항시간에 계산되고, 두 언어의 입력 부호화가 고정된다. |
| 결론 | \(L_1\leq_p L_2\)는 모든 \(x\)에 대해 \(x\in L_1\Longleftrightarrow f(x)\in L_2\)인 함수 \(f\)가 존재한다는 뜻이다. 환원은 합성할 수 있다. |
| 적용 범위 | Karp many-one 환원이다. 여러 질의를 허용하는 Turing 환원과 같은 말로 쓰지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C12, `readings/L17.md` C05, `readings/L21.md` C08. |
| 원문 인용 좌표 | Cook, pp.4~5 / Definition 3. Karp, P8/92, 정리 2 뒤 문단의 Cook 환원 구별. Arora–Barak, PDF 물리 59~60 / Definition 2.7. Isabelle 형식화, PDF p.369 / `reducible`. |
| 확인 강도 | 형식화 교차 확인 |

### D-04: NP-complete와 관문 정리

| 필드 | 내용 |
|---|---|
| 전제 | 언어 \(C\)가 \(NP\)에 속하고, 모든 \(L\in NP\)가 \(L\leq_p C\)를 만족한다. |
| 결론 | \(C\)는 NP-complete다. \(C\in P\)이면 환원과 판정기를 합성해 \(P=NP\)가 따른다. \(C\)의 NP-complete성만으로는 \(P\ne NP\)가 따르지 않는다. |
| 적용 범위 | 결론은 \(C\in NP\)와 Karp many-one 완전성에 의존한다. `NP-hard`는 \(C\in NP\) 조건을 포함하지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C12~C13, `readings/L17.md` C05~C06·Q05, `readings/L21.md` C09·C22·Q13. |
| 원문 인용 좌표 | Cook, pp.4~5 / Definition 4, Proposition 1, SAT 논증. Arora–Barak, PDF 물리 59~66 / Theorem 2.8·2.10. Isabelle 형식화, PDF p.377~378 / `NP-complete-imp`; PDF p.873~874 / `NP-complete-SAT`. |
| 확인 강도 | 형식화 교차 확인 |

### D-05: \(SAT\)와 \(3\text{-}SAT\)

| 필드 | 내용 |
|---|---|
| 전제 | \(SAT\)는 주어진 명제식이 만족 가능한지 묻는 언어다. \(3\text{-}SAT\)는 각 절이 세 리터럴인 CNF 식의 만족 가능성을 묻는 언어다. |
| 결론 | \(SAT\)와 \(3\text{-}SAT\)는 NP-complete다. 따라서 \(SAT\in P\) 또는 \(3\text{-}SAT\in P\)이면 \(P=NP\)다. |
| 적용 범위 | 이 결론은 결정 언어의 표준 부호화와 many-one 환원을 쓴다. SAT 솔버의 유한 실험 또는 NP-complete성만으로 \(P=NP\)나 \(P\ne NP\)를 판정하지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C13, `readings/L04.md` C22·C27, `readings/L17.md` C06, `readings/L20.md` C18·Q13, `readings/L21.md` C22·Q13. |
| 원문 인용 좌표 | Cook, p.5, `Thus the problem Satisfiability` 문단과 식 (2). Karp, P12/96 그림 1; P14/98, SAT→3-SAT. Arora–Barak, PDF 물리 60~66 / Theorem 2.10. Coq 형식화, `CookLevin.v:114-149`. Isabelle 형식화, PDF p.873~874 / `NP-complete-SAT`. |
| 확인 강도 | 형식화 교차 확인 |

## 요구 3: \(coNP\), 다항 계층, 회로족, non-uniform, oracle

### D-06: \(coNP\)

| 필드 | 내용 |
|---|---|
| 전제 | \(L\)의 여집합 \(\overline L\)을 같은 문자열 우주에서 정한다. |
| 결론 | \(coNP=\{L\mid\overline L\in NP\}\)다. \(NP\ne coNP\)이면 \(P\ne NP\)가 따르지만, \(NP=coNP\)가 \(P=NP\)를 뜻하지는 않는다. |
| 적용 범위 | 여집합과 언어 결정 문제에 관한 명제다. 증명 체계의 결과 또는 직관을 계급 동치로 바꾸지 않는다. |
| 재판독 정리 좌표 | `readings/L03.md` C16, `readings/L17.md` C08·Q07, `readings/L22.md` C14. |
| 원문 인용 좌표 | Cook, pp.5~6, `The set of complements` 문단. Arora–Barak, PDF 물리 72~73 / Definition 2.22, Example 2.23. Lean 라이브러리, `DescriptiveComplexity/Hierarchy.lean:L249-L286`. |
| 확인 강도 | 원문 재판독 확인 |

### D-07: 다항 계층 \(PH\)

| 필드 | 내용 |
|---|---|
| 전제 | 다항 길이 양화사와 다항시간 술어를 쓰며, 교대 횟수는 입력 길이와 무관한 상수다. |
| 결론 | \(PH\)는 \(\Sigma_i^p\), \(\Pi_i^p\) 층의 합집합이다. \(\Sigma_i^p=\Pi_i^p\)이면 \(PH\)는 \(i\)층에서 붕괴한다. \(P=NP\)이면 \(PH=P\)다. |
| 적용 범위 | 마지막 결론은 \(P=NP\)를 전제로 한다. \(PH\) 붕괴나 \(NP=coNP\)를 \(P=NP\)와 동치로 쓰지 않는다. |
| 재판독 정리 좌표 | `readings/L17.md` C12·Q10, `readings/L22.md` C05·C14. |
| 원문 인용 좌표 | Arora–Barak, PDF 물리 107~110 / Definition 5.4, Theorem 5.6. Lean 라이브러리, `DescriptiveComplexity/Hierarchy.lean:L249-L286`; `README.md:L84-L102`. |
| 확인 강도 | 조건부 원문 확인 |

### D-08: 회로족과 non-uniform 계산

| 필드 | 내용 |
|---|---|
| 전제 | 입력 길이 \(n\)마다 별도 Boolean circuit \(C_n\)을 허용한다. 회로 크기는 \(n\)의 다항식으로 제한한다. |
| 결론 | \(P/poly\)는 길이마다 다른 다항 크기 회로를 쓰는 non-uniform 계급이다. \(NP\subseteq P/poly\)이면 \(PH=\Sigma_2^p\)다. |
| 적용 범위 | 비균일 회로족의 존재는 균일 다항시간 알고리즘의 존재와 다르다. 계수 논증의 무작위 함수 하한은 명시적 \(NP\) 함수의 일반 회로 하한이 아니다. |
| 재판독 정리 좌표 | `readings/L17.md` C14~C15·Q12~Q13. |
| 원문 인용 좌표 | Arora–Barak, PDF 물리 117~129 / Definition 6.2~6.5, Theorem 6.13·6.15, Remark 6.16. |
| 확인 강도 | 조건부 원문 확인 |

### D-09: oracle 계산

| 필드 | 내용 |
|---|---|
| 전제 | machine이 oracle \(A\)에 질의할 수 있고, \(P^A\), \(NP^A\)는 같은 oracle을 쓰는 상대화 계급이다. |
| 결론 | 어떤 oracle \(A\)에서는 \(P^A=NP^A\)이고 다른 oracle \(B\)에서는 \(P^B\ne NP^B\)다. 따라서 상대화하는 기법만으로는 P 대 NP를 판정할 수 없다. |
| 적용 범위 | oracle 세계의 등식·분리는 비상대화 세계의 \(P=NP\) 또는 \(P\ne NP\) 증거가 아니다. 이 명제는 증명 기법의 범위를 제한한다. |
| 재판독 정리 좌표 | `readings/L03.md` I08, `readings/L17.md` C10·Q09. |
| 원문 인용 좌표 | Cook, p.8, `relative to a generic oracle` 문단. Arora–Barak, PDF 물리 86~88 / Theorem 3.9, §3.5 결론. |
| 확인 강도 | 원문 재판독 확인 |

## 요구 ID와 소유자

| 요구 ID | 원자료 6절의 요구 | 이 문서의 처리 | 소유자 |
|---|---|---|---|
| R1 | Turing machine·다항시간·verifier·\(P\subseteq NP\) | D-01~D-02 | `definitions.md` |
| R2 | many-one·NP-complete·SAT·3-SAT | D-03~D-05 | `definitions.md` |
| R3 | \(coNP\)·PH·회로족·non-uniform·oracle | D-06~D-09 | `definitions.md` |
| R4 | 제한 회로 하계와 일반 Boolean circuit 하계의 차이 | 이 문서는 정의 경계만 보존한다. 결과 지도는 쓰지 않는다. | `barriers.md` |
| R5 | relativization·natural proofs·algebrization의 정확한 범위 | 이 문서는 oracle 정의만 둔다. 세 장벽의 가정·결론·범위·비적용 범위는 쓰지 않는다. | `barriers.md`, `claim-source-matrix.md` |

## 상태 22건

아래 표는 [문헌 재판독 상태표](literature-status.md)의 문헌별 상태 22행을 손실 없이 다시 적는다. 좌표의 `PASS`는 최종 재판독 정리와 지정된 직후 검증 또는 대체 검증을 함께 소비한 유효 상태다.

| 문헌 | 최종 정리 | 직후 판정 또는 대체 검증 | 유효 상태 | 대체 소비 | 미확인 범위와 영향 |
|---|---|---|---|---|---|
| L01 | `readings/L01.md:5` PASS | `2.7.10.3.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L02 | `readings/L02.md:3` PASS | `2.7.10.5.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L03 | `readings/L03.md:3` PASS | `2.7.10.7.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L04 | `readings/L04.md:3` PASS | `2.7.10.55.3.d/종료보고.md:6~10,58~76,131~136,182~189` 재작업 검증 통과 | PASS | 원 FAIL과 원 직후 판정 대신 `55.2→55.3`을 소비 | 없음 |
| L05 | `readings/L05.md:4,153` PASS | `2.7.10.55.12.3.d/종료보고.md:1~18,41~46` 좌표 수리 검증 통과 | PASS | 원 FAIL과 원 직후 판정 대신 `55.12.2→55.12.3`을 소비 | 없음 |
| L06 | `readings/L06.md:3` PASS | `2.7.10.13.d/종료보고.md:107` PASS | PASS | 없음 | 없음 |
| L07 | `readings/L07.md:3` PASS | `2.7.10.15.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L08 | `readings/L08.md:3` PASS | `2.7.10.17.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L09 | `readings/L09.md:3` PASS | `2.7.10.19.d/종료보고.md:75` PASS | PASS | 봉쇄 접근 FAIL 비소비 | 없음 |
| L10 | `readings/L10.md:5,10` PASS | `2.7.10.21.d/종료보고.md:14` PASS | PASS | 없음 | 없음 |
| L11 | `readings/L11.md:3` PASS | `2.7.10.23.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L12 | `readings/L12.md:3` PASS | `2.7.10.25.d/종료보고.md:14` PASS | PASS | 없음 | 없음 |
| L13 | `readings/L13.md:3` PASS | `2.7.10.27.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L14 | `readings/L14.md:6` PASS | `2.7.10.29.d/종료보고.md:102` PASS | PASS | 없음 | 없음 |
| L15 | `readings/L15.md:3` PASS | `2.7.10.55.11.d/종료보고.md:8~15,51~53` 대체 PASS | PASS | 원 FAIL `2.7.10.31.d/종료보고.md` 대신 `55.10→55.11`을 소비 | 없음 |
| L16 | `readings/L16.md:3` PASS | `2.7.10.33.d/종료보고.md:74` PASS | PASS | 봉쇄 접근 FAIL 비소비 | 없음 |
| L17 | `readings/L17.md:3` PASS | `2.7.10.43.d/종료보고.md:78` PASS | PASS | 봉쇄 접근 FAIL 비소비 | 없음 |
| L18 | `readings/L18.md:3` PASS | `2.7.10.45.d/종료보고.md:59` PASS | PASS | 없음 | 없음 |
| L19 | `readings/L19.md:3` PASS | `2.7.10.47.d/종료보고.md:11` PASS | PASS | 없음 | 없음 |
| L20 | `readings/L20.md:3` PASS | `2.7.10.49.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L21 | `readings/L21.md:3` PASS | `2.7.10.51.d/종료보고.md:8` PASS | PASS | 없음 | 없음 |
| L22 | `readings/L22.md:3` PASS | `2.7.10.53.d/종료보고.md:58` PASS | PASS | 봉쇄 접근 FAIL 비소비 | 없음 |

누적 54의 PASS와 누적 60의 원 FAIL은 상태표의 `누적 상태` 절에서 L04·L05·L15의 대체 소비로 처리한다. 유효 상태 22개가 모두 PASS이므로 프레임 A는 개방 가능하다. 이 처분은 P 대 NP의 답이 아니다.

## 비적용 범위

- 유한 벤치마크, SAT 대회, 솔버 실행 결과는 유한 입력과 구현 맥락이다. 이 문서는 그 결과로 복잡도 계급을 판정하지 않는다.
- 제한 회로 하계와 일반 Boolean circuit 하계의 구별은 R4 소유 문서가 원문 좌표와 함께 쓴다.
- relativization, natural proofs, algebrization의 장벽 결론은 R5 소유 문서가 전제와 결론을 분리해 쓴다. 장벽 결과는 \(P\ne NP\)의 증거가 아니다.
