# P vs NP 직접 기초: 초기 핵심층 판독 지도

기준 시각: 2026-09-04 KST  
상태: **직접 기초층의 초기 판독 지도. `covered`·최종 핵심층 승인·원문 완독·P vs NP 해답 판정이 아니다.**

## 사용 경계

이 문서는 현대 P vs NP 연구가 최소한으로 다시 들어가야 할 직접 원 성과·장벽·구조 경계·종합 전거를 묶는다. 서지와 공개 판본/공식 record를 실제로 대조했지만, 아래 원 논문의 증명 전체를 판독하거나 검증하지는 않았다. `함의`는 해당 work가 주장하는 결과의 역할이고, `비함의`는 흔한 과잉 해석을 막는 경계다.

이 지도는 9개 work를 다룬다. B002 후보 JSONL의 정규화 제목만 정확 일치시키면 9/9가 나오지 않지만, 저자·연도·DOI·부제를 함께 대조하면 Arora–Barak의 2009 책은 `MR2500087`로 B002에 있다. 따라서 work 수준에서 B002 밖인 것은 8개다. 정확 제목 부재를 곧 작업 부재로 바꾸지 않는다. 나머지 부재도 B002의 `-00/-01/-02` 상위 100 표본 한계의 관찰이지, 해당 work의 독자적 핵심성 증명은 아니다.

B001 전수 정규화 뒤에는 이 9개 중 세 work가 실제 후보로 연결된다. Razborov–Rudich는 1997 JCSS DOI `10.1006/jcss.1997.1494`가 ACM·MathSciNet(`MR1473047`)·Scopus·WoS 4개 source record에, 1994 STOC 판은 별도 DOI `10.1145/195058.195134`로 잡힌다. Aaronson–Wigderson은 2008 STOC와 2009 TOCT가 각각 별도 DOI로 잡히며, Arora–Barak은 B001·B002의 같은 `MR2500087`이다. 나머지 여섯 직접 기초 work는 B001의 exact work/DOI 후보에서도 확인되지 않았다. B001에 같은 제목의 2010 *The P versus NP problem* 장이 있지만 CMI Cook description과는 다른 work다. 따라서 B001은 B002를 실질적으로 보완하지만 Cook·Levin·Karp·Ladner·BGS 원 성과를 모두 대체하지 않는다.

**표준 문제 문면.** 입력 길이에 대한 결정문제 언어 (L)에서, (P)는 결정적 Turing machine이 다항 시간에 결정하는 언어이고, (NP)는 다항 길이 증명서가 다항 시간 검증기로 확인되는 언어(동치로 비결정적 다항시간 TM 언어)로 쓴다. 질문은 이 두 계급이 같은가다. CMI의 [공식 P vs NP 페이지](https://www.claymath.org/millennium/p-vs-np/)는 이를 “해를 쉽게 확인할 수 있으면 쉽게 찾을 수도 있는가”라는 접근 가능한 문면으로 제시하고, 현재 상태를 **Unsolved**로 표시한다. 이 설명은 실무의 ‘쉬움’이나 특정 기계의 성능을 수학적으로 정의하지 않으므로, 계산 모형·입력 부호화·다항식 변수는 Cook 원문과 아래 종합 전거에서 다시 고정해야 한다.

## 작업 목록

### 1. 공식 문제 설명과 상태 — CMI / Cook

- **정확한 work:** Stephen Cook, *The P versus NP Problem*, Clay Mathematics Institute Millennium Problems official problem description (2000; CMI 공개 PDF/현행 페이지). [CMI 현행 상태 페이지](https://www.claymath.org/millennium/p-vs-np/), [공개 problem description](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).
- **역할:** 표준 질문의 공식 공개 진입점과 조사 시점 상태 전거. CMI 페이지는 Cook·Levin의 독립 정식화를 함께 언급한다.
- **함의 / 비함의:** 문제의 대상이 ‘검증 대 생성’의 격차인지 설명하고 현재 해결되지 않았음을 보인다. (P\ne NP), (P=NP), 특정 NP 문제의 난도, 혹은 특정 증명 기법의 실패를 함의하지 않는다.
- **판독 좌표·판본:** 공개 PDF pp. 1–12 전체; 특히 정의·NP-completeness·결론 문면을 사용하기 전 원문 좌표를 확인한다. CMI 공개 PDF는 원 논문을 대체하지 않는다.
- **B002:** exact-title 대조 결과 없음.

### 2. Cook–Levin 축 I — Cook 1971

- **정확한 work:** Stephen A. Cook, “The complexity of theorem-proving procedures,” *Proceedings of the Third Annual ACM Symposium on Theory of Computing (STOC ’71)*, 1971, pp. 151–158, DOI [10.1145/800157.805047](https://doi.org/10.1145/800157.805047). [ACM 공식 record](https://dl.acm.org/doi/10.1145/800157.805047); 공개 판본은 [CMU course mirror](https://www.cs.cmu.edu/~15455/resources/Cook1971-complx-thm-proof.pdf)에서 확인했으나, 이는 ACM 출판본과 동일 판본인지 아직 대조하지 않았다.
- **역할:** 다항시간 비결정적 TM 인식 문제를 propositional tautology로 다항시간 oracle-style reduction하는 원 성과; NP-completeness 전통의 출발점이다.
- **함의 / 비함의:** 보완을 취하면 SAT의 NP-completeness라는 현대적 Cook–Levin 결론으로 재진입할 수 있다. 이 논문은 (P\ne NP)를 증명하지 않으며, 모든 어려워 보이는 문제의 난도나 특정 회로 하계를 자동으로 주지 않는다.
- **판독 좌표·판본:** ACM proceedings pp. 151–158 전체. 현대 SAT 문면과 원문의 tautology·reduction 문면을 같은 말로 바꾸지 말고, 해당 정의와 reduction 절을 직접 대조한다.
- **B002:** exact-title 대조 결과 없음.

### 3. Cook–Levin 축 II — Levin 원문·번역

- **정확한 work:** L. A. Levin, “Универсальные задачи перебора” / “Universal Sequential Search Problems,” *Problemy Peredachi Informatsii* 9(3) (1973), pp. 115–116; 영어판 *Problems of Information Transmission* 9(3) (1973), pp. 265–266. [MathNet 원/번역 공식 record](https://www.mathnet.ru/eng/ppi914)와 해당 공개 원문 링크가 있다. MathNet은 접수일 1972-06-07, 원문 언어 Russian, 영어판의 별도 페이지 범위를 명시한다.
- **역할:** universal sequential search problems의 원 성과이며, Cook과 독립된 NP-completeness 역사축으로 다룬다.
- **함의 / 비함의:** search 문제의 보편성/환원 관점을 제공한다. Cook의 1971 논문과 같은 출판 시점·같은 문면·같은 reduction 정의라는 뜻은 아니며, (P\ne NP)를 증명하지 않는다.
- **판독 좌표·판본:** 러시아 원문 pp. 115–116과 영어 번역 pp. 265–266을 각각 판본으로 기록한다. 번역의 정확성과 현대 NP-complete 용어와의 대응은 원문·번역을 나란히 읽어야 한다.
- **B002:** exact-title 대조 결과 없음.

### 4. NP-completeness의 문제군 전개 — Karp 1972

- **정확한 work:** Richard M. Karp, “Reducibility among Combinatorial Problems,” in *Complexity of Computer Computations*, 1972, pp. 85–103, DOI [10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9). [Springer 공식 chapter/book record](https://link.springer.com/book/10.1007/978-1-4684-2001-2)는 저자와 pp. 85–103을 명시한다.
- **역할:** 조합 문제군의 다항시간 many-one reducibility와 완전성 전개를 위한 원 전거다.
- **함의 / 비함의:** 한 문제의 NP-completeness가 다른 문제로 전파되는 환원 지도를 제공한다. (P\ne NP)를 증명하지 않고, 목록의 모든 문제에 실무적 난도를 보장하지 않으며, Cook reduction과 Karp reduction을 무표지로 같다고 하지 않는다.
- **판독 좌표·판본:** chapter pp. 85–103 전체; 정의와 각 reduction을 사용하려면 해당 target problem 절을 다시 읽는다. 이번에는 Springer 공개 metadata만 확인했으며 공개 full chapter 판본은 확보하지 않았다.
- **B002:** exact-title 대조 결과 없음.

### 5. 구조 복잡도의 조건부 경계 — Ladner 1975

- **정확한 work:** Richard E. Ladner, “On the Structure of Polynomial Time Reducibility,” *Journal of the ACM* 22(1) (1975), pp. 155–171, DOI [10.1145/321864.321877](https://doi.org/10.1145/321864.321877), [ACM 공식 record](https://dl.acm.org/doi/10.1145/321864.321877).
- **역할:** (P\ne NP)라는 조건 아래 (NP) 안에 (P)에도 속하지 않고 다항시간 many-one NP-complete도 아닌 문제들이 존재한다는 Ladner-type 중간 문제 경계의 원 전거다.
- **함의 / 비함의:** 조건부로 NP-intermediate 문제가 존재함을 준다. 조건을 제거한 무조건 (P\ne NP) 증명도, 자연스러운 특정 문제가 intermediate라는 판정도, 특정 후보의 완전성 부정도 아니다.
- **판독 좌표·판본:** JACM pp. 155–171 전체, 특히 theorem의 가정·reducibility 종류·구성 절. 공식 record는 확인했지만 공개 full text 판본은 이번에 확보하지 않았다.
- **B002:** exact-title 대조 결과 없음.

### 6. 상대화 장벽 — Baker–Gill–Solovay 1975

- **정확한 work:** Theodore Baker, John Gill, Robert Solovay, “Relativizations of the \(\mathcal P=?\mathcal{NP}\) Question,” *SIAM Journal on Computing* 4(4) (1975), pp. 431–442, DOI [10.1137/0204037](https://doi.org/10.1137/0204037), [SIAM 공식 record](https://epubs.siam.org/doi/abs/10.1137/0204037).
- **역할:** 재귀 oracle (A,B)를 만들어 (P^A=NP^A) 및 (P^B\ne NP^B)를 보이는 상대화 장벽의 원 성과다.
- **함의 / 비함의:** 상대화하는 증명 방식만으로는 비상대화 (P) 대 (NP)를 해결할 수 없다는 방법론적 한계를 준다. (P=NP)나 (P\ne NP) 어느 쪽도 증명하지 않고, 모든 diagonalization 또는 모든 oracle-free 방법을 배제하지 않는다.
- **판독 좌표·판본:** SIAM pp. 431–442 전체; (A,B) oracle 구성과 결론의 quantifier를 재확인한다. SIAM 공식 abstract record는 공개이나 출판 PDF 확보 여부는 이번에 판정하지 않았다.
- **B002:** exact-title 대조 결과 없음.

### 7. Natural-proofs 장벽 — Razborov–Rudich 1997

- **정확한 work:** Alexander A. Razborov, Steven Rudich, “Natural Proofs,” *Journal of Computer and System Sciences* 55(1) (1997), pp. 24–35, DOI [10.1006/jcss.1997.1494](https://doi.org/10.1006/jcss.1997.1494), [Elsevier 공식 record](https://linkinghub.elsevier.com/retrieve/pii/S002200009791494X). 저자 공개 목록은 [Rudich page](https://www.cs.cmu.edu/~rudich/papers/index.htm)에 public PostScript 판본을 연결한다.
- **역할:** largeness와 constructivity를 갖는 natural proof의 개념을 제시하고, 적절한 pseudorandomness/hardness 가정 아래 일반 회로의 강한 lower bound를 natural proof 방식으로 얻는 데 생기는 장벽을 분석한다.
- **함의 / 비함의:** 특정 조건 아래 natural-proofs 방법군의 한계를 준다. 가정 없는 (P=NP) 또는 (P\ne NP) 결론, 모든 circuit lower-bound 방법의 불가능성, one-way function의 존재·부재를 함의하지 않는다.
- **판독 좌표·판본:** JCSS pp. 24–35 전체; natural property 정의, 가정, main barrier theorem을 분리해 읽는다. 공개 PostScript의 출판본 대응은 아직 대조하지 않았다.
- **B002:** exact-title 대조 결과 없음.

### 8. Algebrization 장벽 — Aaronson–Wigderson 2008/2009

- **정확한 work:** Scott Aaronson, Avi Wigderson, “Algebrization: A New Barrier in Complexity Theory,” STOC 2008, pp. 731–740; journal version *ACM Transactions on Computation Theory* 1(1) (2009), Article 2, pp. 2:1–2:54, DOI [10.1145/1490270.1490272](https://doi.org/10.1145/1490270.1490272), [ACM 공식 record](https://dl.acm.org/doi/10.1145/1490270.1490272). [Wigderson IAS 공개 판본](https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/SCOTT/alg.pdf)과 [ECCC TR08-005](https://eccc.weizmann.ac.il/eccc-reports/2008/TR08-005/Paper.pdf)를 대조했다.
- **역할:** algebraic oracle/low-degree extension을 통한 algebrization을 정의하고, 주요 문제를 해결하려면 non-algebrizing technique이 필요함을 보이는 장벽 전거다.
- **함의 / 비함의:** algebrizing proof 방식이 P 대 NP를 해결할 수 없다는 방법론 경계를 준다. non-algebrizing 방법이면 성공한다는 보장, (P\ne NP) 결론, natural proofs·relativization을 모두 회피하는 모든 방법의 성공을 뜻하지 않는다.
- **판독 좌표·판본:** IAS 공개본 pp. 1–3(정의·기여), Section 2(정의), Section 5(oracle separation)와 journal Article 2의 대응 좌표를 대조한다. STOC·journal·IAS/ECCC 판본은 자동 병합하지 않는다.
- **B002:** exact-title 대조 결과 없음.

### 9. 권위 있는 종합·재진입 전거 — Arora–Barak 2009

- **정확한 work:** Sanjeev Arora, Boaz Barak, *Computational Complexity: A Modern Approach*, Cambridge University Press, 2009. 저자/Princeton [공식 companion page](https://theory.cs.princeton.edu/complexity/)는 공개 Internet draft와 보조 자료를 제공하며, 해당 draft는 출판본과 별개 판본이다.
- **역할:** 복잡도 계급, 환원·NP-completeness, oracle/상대화, circuit complexity 및 관련 장벽을 현대 용어로 다시 연결하는 종합·survey 전거다. 조사 시점 상태는 이 책이 아니라 위 CMI 공식 Unsolved 표시에 둔다.
- **함의 / 비함의:** 표준 정의·배경·문헌 경로를 제공한다. 2009 출판본/이전 Internet draft는 최신 연구 전선이나 CMI의 현행 상태를 단독으로 확정하지 않으며, 원 성과를 대체하지 않는다.
- **판독 좌표·판본:** 저자 companion page의 공개 draft와 출판본의 목차·장·정리 번호를 사용 전에 대조한다. 이 보고서는 Internet draft의 위치를 2009 출판본의 좌표로 단정하지 않는다.
- **B002:** 전체 제목 *Computational Complexity: A Modern Approach*의 exact-title은 없지만, `MR2500087`이 제목 *Computational complexity*, NOTE *A modern approach*, 같은 저자·2009·ISBN·DOI로 이 work와 일치한다.

## 축별 최소 재진입 순서

| 축 | 먼저 읽을 work | 다음 연결 |
|---|---|---|
| 문제 문면·계산 모형 | CMI Cook description → Cook 1971 → Arora–Barak | 직관 문면과 TM/certificate·입력 부호화를 분리 |
| Cook–Levin / NP-completeness | Cook 1971 → Levin 1973 원/번역 → Karp 1972 | tautology/SAT, search/decision, reduction 종류를 혼동하지 않음 |
| 구조 경계 | Ladner 1975 | 가정 (P\ne NP), many-one reducibility, intermediate의 범위를 고정 |
| 장벽 | BGS 1975 → RR 1997 → AW 2009 | 각 장벽의 방법군·가정·배제 범위를 따로 기록 |
| status/survey | CMI current page → Arora–Barak | 현재 미해결 상태와 역사/정의 종합의 권한을 분리 |

## 판본·원문 결손과 다음 행동

공개 원문 또는 공식 공개 판본을 실제로 확인한 것은 CMI Cook description, Levin의 MathNet record/원문 링크, Aaronson–Wigderson IAS/ECCC 판본, Arora–Barak 저자 draft다. Cook 1971은 ACM 공식 record와 공개 course mirror가 있으나 판본 일치 미확정이다. Karp 1972, Ladner 1975, BGS 1975, Razborov–Rudich 1997은 공식 publisher record를 확인했지만, 이번 단계에서 출판 full text의 적법한 공개 판본을 확보·판독하지 않았다.

따라서 다음 단계는 필요한 원 논문 판본을 적법한 공개 경로에서 확보하고, 각 work의 위 재진입 좌표에서 정의·정리·가정·결론을 판독 지도에 기록하는 일이다. 특히 Levin의 러시아 원문과 영어 번역, Cook의 공개 mirror와 ACM proceedings, AW의 STOC/journal/IAS/ECCC 판본은 관계를 실제로 대조해야 한다. 이 보고서는 그 대조나 최종 `covered` 판정을 대신하지 않는다.
