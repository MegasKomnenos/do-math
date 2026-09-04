# B001 직접-title 검토 B

기준 시각: 2026-09-04 KST  
범위: `B001-direct-title-queue.jsonl`을 `cluster_id` 오름차순 정렬한 37–72번 **36 clusters / 58 members**.

## 판정 경계

각 행은 cluster의 모든 member 제목·venue·type·search signal을 B001 queue와 candidate 원문에서 다시 대조했다. `direct_p_vs_np` signal은 검색 라우팅 신호일 뿐 핵심성·정확성·해결 주장의 증거가 아니다. DOI가 있는 핵심 연구 전거는 공식 DOI/venue record도 소량 대조했다. purported resolution은 `purported_resolution_requires_adversarial_review`에만 두며 승인하지 않는다.

`source`는 member의 B001 발견 자료원, `sig`는 queue가 보존한 signal 종류의 합집합이다. 같은 제목의 복수 member는 source별로 원문 서지가 반복되므로, 표 안에 각 source/type/venue를 모두 적되 title은 공통 title로 한 번 적는다.

## cluster별 처분

| # | cluster ID · members (title; source/type/venue; sig) | 처분 | 근거와 경계 |
|---:|---|---|---|
| 37 | `5b8308…`; 2: *What one has to know when attacking P vs. NP*; Scopus/article/JCSS, WoS/article/JCSS; direct·complexity·polytime·SAT | `standard_pnp_research` | JCSS DOI [10.1016/j.jcss.2019.06.004](https://doi.org/10.1016/j.jcss.2019.06.004), Hromkovič–Rossmanith, 2020. 공격에 필요한 회로/복잡도 지식을 다루는 연구 전거; 해결 주장 아님. |
| 38 | `5c009b…`; 3: *Microteaching: … and P vs NP*; ACM/inproc/SIGCSE, Scopus/conf/SIGCSE, WoS/inproc/SIGCSE; direct-title | `education_or_commentary` | 수업 microteaching session이다. P vs NP 연구 결과가 아니다. |
| 39 | `5dd260…`; 2: *… Proving P=NP as a Conclusion*; IEEE/inproc/CSCI, Scopus/conf/CSCI; direct·polytime | `purported_resolution_requires_adversarial_review` | 제목이 P=NP 결론을 주장한다. conference record만으로 승인하지 않으며, 주장·정의·reduction을 적대적으로 원문 검토해야 한다. |
| 40 | `684569…`; 2: *The P versus NP-complete dichotomy … graph theory*; Scopus/article/DAM, WoS/article/DAM; direct·NP-hardness·complexity | `conditional_hardness_or_consequence` | 그래프 문제군의 P/NP-complete dichotomy로 보이는 분야별 결과다. 전역 P vs NP 해결이 아니다. |
| 41 | `6a7e88…`; 2: *Time to P=NP*; Scopus/letter/New Scientist, WoS/article/New Scientist; direct-title | `education_or_commentary` | 대중 과학지 letter/short commentary다. 연구 근거나 해결 판정으로 쓰지 않는다. |
| 42 | `6b35d4…`; 2: *Chipping away at P vs NP: how far … circuit size lower bounds?*; ACM/inproc/Australasian Theory, Scopus/conf/CRPIT; direct·lower-bounds·complexity | `standard_pnp_research` | Eric Allender, 2008; circuit lower-bound 장벽의 연구/설명 전거. title의 질문은 해결 선언이 아니다. |
| 43 | `705251…`; 2: *On the P vs NP problem over reals with integer oracle*; IEEE/inproc/Dynamics, Scopus/conf/Dynamics; direct·complexity·relativization | `alternative_model_or_relativized_variant` | real/integer-oracle 모형의 상대화 문제다. 고전 Boolean (P) 대 (NP)에 자동 전이하지 않는다. |
| 44 | `706f7e…`; 1: *The P versus NP Problem in Quantum Physics*; WoS/article/NeuroQuantology; direct·polytime | `needs_full_text_review` | 표제는 실제 P/NP를 지칭하지만 양자물리와 고전 complexity class의 연결·주장 근거를 metadata만으로 판정할 수 없다. |
| 45 | `724bed…`; 2: *A Field-Theoretical Approach … Quantum Monte Carlo*; Scopus/article/Condensed Matter, WoS/article/Condensed Matter; direct-title | `alternative_model_or_relativized_variant` | QMC phase-sign/물리 계산 모형의 복잡도 연결이다. 고전 문제의 해결이 아니다. |
| 46 | `744479…`; 1: *Programmability and P=NP conjecture*; Scopus/conf/LNCS; direct·abstract | `needs_full_text_review` | 1977 LNCS record이나 title·signal만으로 정확한 모형·주장 범위를 확정할 수 없다. |
| 47 | `782df3…`; 3: *The status of the P versus NP problem*; ACM/article/CACM, Scopus/review/CACM, WoS/article/CACM; direct·SAT·NP-hardness·polytime | `authoritative_status_or_history` | Lance Fortnow, CACM 52(9), 2009, DOI [10.1145/1562164.1562186](https://doi.org/10.1145/1562164.1562186). 상태/역사 설명 전거이며 새 해결 결과가 아니다. |
| 48 | `7830f3…`; 1: *Quantum authentication … even if P = NP*; Scopus/conf/LNCS; direct-title | `conditional_hardness_or_consequence` | P=NP를 가정한 암호 프로토콜의 조건부 안전성 문면이다. P=NP 주장 아니다. |
| 49 | `7b8e52…`; 1: *On honest polynomial reductions, relativizations, and P = NP*; Scopus/conf/venue 미기재; direct·relativization | `alternative_model_or_relativized_variant` | honest reduction/relativization의 구조 결과다. 원문에서 reduction 종류를 확인해야 한다. |
| 50 | `7c48df…`; 1: *Inapproximability … assuming P ≠ NP*; Scopus/conf/LNCS; direct·lower-bounds·complexity | `conditional_hardness_or_consequence` | 명시적으로 P≠NP 가정 아래의 inapproximability 결과다. 가정을 결론으로 바꾸지 않는다. |
| 51 | `7d5977…`; 2: *Consequences of an exotic definition for P = NP*; Scopus/article/AMC, WoS/article/AMC; direct | `alternative_model_or_relativized_variant` | 제목이 exotic definition을 한정한다. 표준 P/NP 정의에 대한 해결 근거가 아니다. |
| 52 | `7e6901…`; 1: *Hypotheses that imply the independence of P = NP from strong axiomatic systems*; Scopus/book chapter/economic dynamics volume; direct-title | `alternative_model_or_relativized_variant` | 강한 공리계 독립성이라는 조건부 논리 모형이다. 표준 문제 해결이나 독립성 확정이 아니다. |
| 53 | `7f319e…`; 1: *P vs. NP Poll Results*; WoS/article/CACM; direct-title | `education_or_commentary` | poll 결과다. 수학적 증거나 status의 권위 있는 단독 전거가 아니다. |
| 54 | `8030a6…`; 2: *P versus NP and geometry*; Scopus/article/JSC, WoS/article/JSC; direct·complexity·GCT | `standard_pnp_research` | J. M. Landsberg, 2010, DOI [10.1016/j.jsc.2010.06.015](https://doi.org/10.1016/j.jsc.2010.06.015). geometric complexity theory의 직접 연구 전거; 해결 선언이 아니다. |
| 55 | `8081ac…`; 1: *Hypotheses that imply the independence of P = NP from strong axiomatic systems*; Scopus/book chapter/economic dynamics volume; direct | `alternative_model_or_relativized_variant` | 52번과 DOI/book-level signal이 달라도 같은 independence 주제의 chapter record다. 조건을 표준 결론으로 전이하지 않는다. |
| 56 | `81e24b…`; 1: *The P versus NP problem through cellular computing with membranes*; Scopus/article/LNCS; direct·NP-hardness·polytime | `alternative_model_or_relativized_variant` | membrane/cellular computing 모형의 결과다. 고전 TM P/NP와 모형 경계를 유지한다. |
| 57 | `84397a…`; 1: *Positive relativizations of the P = ? NP problem*; Scopus/article/JCSS; direct·relativization | `alternative_model_or_relativized_variant` | Craig A. Rich, JCSS 38(3), 1989, DOI [10.1016/0022-0000(89)90014-7](https://doi.org/10.1016/0022-0000(89)90014-7). 상대화 결과로서 비상대화 문제를 결정하지 않는다. |
| 58 | `84a6a6…`; 1: *The P versus NP problem in quantum physics*; Scopus/article/NeuroQuantology; direct·polytime | `needs_full_text_review` | 44번의 별 자료원 출현이다. 실제 P/NP 표제이므로 검색 오탐으로 버리지 않되 원문 없이 직접 TCS 결과로 승격하지 않는다. |
| 59 | `86f9ac…`; 2: *Relativizations … over the reals (and other ordered rings)*; Scopus/article/TCS, WoS/article/TCS; direct·complexity·relativization | `alternative_model_or_relativized_variant` | T. Emerson, TCS 133(1), 1994, DOI [10.1016/0304-3975(94)00068-9](https://doi.org/10.1016/0304-3975(94)00068-9). real/ordered-ring 상대화이며 표준 문제 결론 아님. |
| 60 | `884c97…`; 1: *A model of the P=NP-problem with a positive solution*; WoS/article/Acta Informatica; direct-title | `alternative_model_or_relativized_variant` | positive solution은 제목이 한정한 model 안의 결과다. 표준 P=NP 증명이 아니다. |
| 61 | `8cdc3c…`; 2: *Oracle with P=NP∩coNP, but No Many-One Completeness …*; Scopus/conf/LIPIcs, WoS/inproc/MFCS; direct·complexity·proof-complexity | `alternative_model_or_relativized_variant` | MFCS 2022 LIPIcs DOI [10.4230/LIPIcs.MFCS.2022.45](https://doi.org/10.4230/LIPIcs.MFCS.2022.45). oracle/relativized 구조 결과다. |
| 62 | `8d835c…`; 1: *P≠NP for the reals with various analytic functions*; WoS/article/Journal of Complexity; direct-title | `alternative_model_or_relativized_variant` | real computation+analytic-function 모형의 분리다. Boolean P/NP 분리로 쓰지 않는다. |
| 63 | `8ec166…`; 2: *Fast quantifier elimination means P = NP*; Scopus/conf/LNCS, WoS/incollection/proceedings; direct | `conditional_hardness_or_consequence` | 빠른 QE라는 가정/전제가 P=NP를 함의한다는 문면이다. 전제가 성립한다거나 P=NP가 증명됐다는 뜻이 아니다. |
| 64 | `9158f0…`; 2: *P ≠ NP for all infinite Boolean algebras*; Scopus/article/MLQ, WoS/article/MLQ; direct | `alternative_model_or_relativized_variant` | infinite Boolean algebra의 일반화 모형 결과다. 표준 finite Boolean decision language 결론 아님. |
| 65 | `91f4f5…`; 2: *An Argument for P=NP*; Scopus/article/Minds and Machines, WoS/article/Minds and Machines; direct | `purported_resolution_requires_adversarial_review` | 제목이 직접 해결을 주장한다. DOI [10.1007/s11023-017-9454-1](https://doi.org/10.1007/s11023-017-9454-1) record만으로 승인하지 않는다. |
| 66 | `92aab0…`; 1: *Interior solutions to Einstein-Maxwell equations … when P=NP*; WoS/article/Physical Review D; direct-title | `non_tcs_false_positive` | 물리 논문의 `P`,`NP`는 고전 complexity class를 뜻한다는 근거가 없다. |
| 67 | `93b067…`; 1: *… P vs NP rats … ethanol*; WoS/article/American Journal of Medical Genetics; direct-title | `non_tcs_false_positive` | 동물 표현형 표기 `P`/`NP`의 충돌이다. TCS와 무관. |
| 68 | `99183e…`; 1: *Multivariate polynomial integration and differentiation are polynomial time inapproximable unless P=NP*; Scopus/conf/LNCS; direct·polytime | `conditional_hardness_or_consequence` | `unless P=NP`의 조건부 inapproximability다. 가정의 진위를 결론으로 바꾸지 않는다. |
| 69 | `99edac…`; 3: *On relativizations … for several structures*; Scopus/conf/CCA, Scopus/article/ENTCS, WoS/article/ENTCS; direct·relativization | `alternative_model_or_relativized_variant` | C. Gassner, 2008, DOI [10.1016/j.entcs.2008.12.008](https://doi.org/10.1016/j.entcs.2008.12.008). 여러 구조의 상대화 결과다. |
| 70 | `9a8fcb…`; 2: *Inductive complexity of the P versus NP problem*; Scopus/article/PPL, WoS/article/PPL; direct·complexity | `needs_full_text_review` | inductive complexity의 정확한 정의·표준 P/NP와의 관계는 title/signal만으로 확정 못함. |
| 71 | `9e1598…`; 1: *P=NP for some structures over the binary words*; Scopus/article/Journal of Complexity; direct·complexity·relativization·polytime | `alternative_model_or_relativized_variant` | 특정 structure over binary words의 결과다. standard P=NP가 아니다. |
| 72 | `9f9c3f…`; 2: *Beyond P vs. NP: Quadratic-Time Hardness for Big Data Problems*; ACM/inproc/SPAA, WoS/inproc/SPAA; direct·fine-grained·NP-hardness·polytime | `standard_pnp_research` | Piotr Indyk, SPAA 2017, DOI [10.1145/3087556.3087603](https://doi.org/10.1145/3087556.3087603). fine-grained hardness를 P-vs-NP와 구별해 다루는 직접 연구다. |

## 집계와 검산

| 처분 | clusters | members |
|---|---:|---:|
| `authoritative_status_or_history` | 1 | 3 |
| `standard_pnp_research` | 4 | 8 |
| `conditional_hardness_or_consequence` | 5 | 7 |
| `alternative_model_or_relativized_variant` | 15 | 23 |
| `education_or_commentary` | 3 | 6 |
| `purported_resolution_requires_adversarial_review` | 2 | 4 |
| `non_tcs_false_positive` | 2 | 2 |
| `needs_full_text_review` | 4 | 5 |
| **합계** | **36** | **58** |

source slice는 cluster ID 정렬 37–72의 36개 ID이며, 위 표의 cluster ID 집합도 36개다. 이 두 집합의 대칭차는 0이어야 한다. 이 보고서는 B001 intake/candidate/queue를 수정하지 않고, 원문 미판독 record를 최종 핵심층으로 승인하지 않는다.

### cluster ID 전개표

본문 첫 열의 짧은 식별자는 다음의 완전 `cluster_id`를 가리킨다.

| 순번 | cluster_id |
|---:|---|
| 37 | `B001-DIRECT-5b8308eb572abb5bfcb9` |
| 38 | `B001-DIRECT-5c009b4eea63a5b4ac53` |
| 39 | `B001-DIRECT-5dd26007393b05c115b6` |
| 40 | `B001-DIRECT-6845693c4c16c1027df7` |
| 41 | `B001-DIRECT-6a7e88be79f76b98abfa` |
| 42 | `B001-DIRECT-6b35d45f6cbdd8fb9774` |
| 43 | `B001-DIRECT-7052512837730ebccd6d` |
| 44 | `B001-DIRECT-706f7e5b8921b5d3b7e7` |
| 45 | `B001-DIRECT-724bedf1e2acdd1ca90d` |
| 46 | `B001-DIRECT-744479588d0a5cf51d08` |
| 47 | `B001-DIRECT-782df3adde6e04070310` |
| 48 | `B001-DIRECT-7830f3c1630d4ce25cc9` |
| 49 | `B001-DIRECT-7b8e5201e033a3f5bcef` |
| 50 | `B001-DIRECT-7c48dfd8a14ba9019e62` |
| 51 | `B001-DIRECT-7d59776cd38746ca0f07` |
| 52 | `B001-DIRECT-7e690164d7921bf5aa51` |
| 53 | `B001-DIRECT-7f319e212bb971149cc6` |
| 54 | `B001-DIRECT-8030a61eaf21bcf225e3` |
| 55 | `B001-DIRECT-8081ac760269870dc4c1` |
| 56 | `B001-DIRECT-81e24b416fa827bbf09e` |
| 57 | `B001-DIRECT-84397ab4c79f92d0a4ff` |
| 58 | `B001-DIRECT-84a6a6980604a81fd472` |
| 59 | `B001-DIRECT-86f9acbe4f2482dc711f` |
| 60 | `B001-DIRECT-884c97e35a01eab5fb22` |
| 61 | `B001-DIRECT-8cdc3c51b366910c0f4f` |
| 62 | `B001-DIRECT-8d835c4024a6713f0421` |
| 63 | `B001-DIRECT-8ec1665ca29367ee8b95` |
| 64 | `B001-DIRECT-9158f094450c6d968b1c` |
| 65 | `B001-DIRECT-91f4f56d528a6273c8a3` |
| 66 | `B001-DIRECT-92aab05dc4004761fd2b` |
| 67 | `B001-DIRECT-93b0675abf397a879cbe` |
| 68 | `B001-DIRECT-99183e749b8e81a09529` |
| 69 | `B001-DIRECT-99edacb1b251bd64f419` |
| 70 | `B001-DIRECT-9a8fcb9696711d2149b4` |
| 71 | `B001-DIRECT-9e15988d9b7a63f40385` |
| 72 | `B001-DIRECT-9f9c3fda8100c655185a` |
