# B001 direct+axis abstract 검토 B

기준 시각: 2026-09-04 KST  
범위: `B001-direct-axis-queue.jsonl`의 `cluster_id` 오름차순 53–104번, **52 clusters / 58 members**.

## 방법과 경계

각 member의 B001 provenance/rank가 가리키는 Scopus CSV, WoS RIS, ACM/IEEE BibTeX 또는 PQDT RIS 원시 export를 열어 abstract·keywords의 P/NP 언급과 `named_axes`를 대조했다. 예컨대 Scopus 원시 CSV에는 `Abstract`, `Author Keywords`, `Index Keywords`가, PQDT RIS에는 `AB`가 실제로 있다. queue의 signal은 그 원시 필드에서 만들어진 표상이므로, 여기서는 title과 독립으로 문맥을 재판정했다.

abstract가 P/NP를 배경으로만 언급하고 주 결과가 parameterized/graph/physics/biology인 경우에는 직접 핵심으로 올리지 않았다. `P=NP`·분리·장벽과 비슷한 문면도 모형·가정·상대화·증명 상태를 확인하지 않으면 승인하지 않는다. 인용 순위·점수는 쓰지 않았다.

## cluster별 처분

`members`에는 동일 title의 모든 source/type/venue를 적었다. `ctx`는 원시 abstract/keywords에서 회수한 직접 문맥(축 또는 결과 종류)이다.

| # | cluster_id · members | ctx | 처분 |
|---:|---|---|---|
| 53 | `B001-AXIS-5a337c37bd7d2e75d6bb`; 2: *Finding Connected Secluded Subgraphs*; Scopus conf/LIPIcs, WoS inproc/IPEC | parameterized complexity·P/NP background | `standard_subaxis_research` |
| 54 | `B001-AXIS-5b1bbb83704b5665acc4`; 1: *Stringent relativization*; Scopus article/LNCS | relativization·complexity classes | `standard_subaxis_research` |
| 55 | `B001-AXIS-5d13a69e06873862dbb8`; 1: *Chromatic Index Under Parameterized Settings*; Scopus conf/LNCS | parameterized settings·NP-hardness | `standard_subaxis_research` |
| 56 | `B001-AXIS-5d690416d0e0e98dcd41`; 1: *Reductions and Propositional Proofs for Total NP Search Problems*; PQDT thesis | proof complexity·lower bounds | `needs_full_text_review` |
| 57 | `B001-AXIS-5e5e792cbdf8b291fe0a`; 1: *Relativized alternation and space-bounded computation*; Scopus article/JCSS | relativization·space-bounded computation | `standard_subaxis_research` |
| 58 | `B001-AXIS-5f3bfd11eae69ce349b4`; 1: *On backdoors to tractable constraint languages*; Scopus conf/LNCS | CSP backdoors·parameterized tractability | `standard_subaxis_research` |
| 59 | `B001-AXIS-5f9e4c61e5ce5251df36`; 1: *Fine-Grained Complexity in a World Without Cryptography*; Scopus conf/LNCS | fine-grained complexity·cryptography boundary | `standard_subaxis_research` |
| 60 | `B001-AXIS-607eaeea5483c63571ae`; 1: *Probabilistically Checkable Proofs with Low Amortized Query Complexity*; Scopus conf/FOCS | PCP·query complexity·NP-hardness | `core_barrier_or_method_candidate` |
| 61 | `B001-AXIS-617d8b921edc742b82f2`; 1: *Circuit Complexity, Proof Complexity, and Polynomial Identity Testing: The Ideal Proof System*; WoS article/JACM | circuit/proof complexity·PIT·lower bounds | `core_barrier_or_method_candidate` |
| 62 | `B001-AXIS-61ebf7235dd51bdca14a`; 1: *Computational complexity of graphs*; Scopus chapter/*Advances in Network Complexity* | graph/network complexity application | `application_or_distant_bridge` |
| 63 | `B001-AXIS-63acd1166aea331bc74f`; 2: *Nondeterministic Polynomial-Time Computations and Models of Arithmetic*; ACM article/JACM, Scopus article/JACM | arithmetic models·relativization | `alternative_model_or_relativized_variant` |
| 64 | `B001-AXIS-649ddce10333a71a12e8`; 1: *Lower bounds on kernelization*; Scopus article/Discrete Optimization | kernel lower bounds·parameterized complexity | `standard_subaxis_research` |
| 65 | `B001-AXIS-6601133fd45f28d8b6c4`; 1: *Proceedings of the 24th Annual ACM Symposium on the Theory of Computing*; Scopus conference review/STOC | communication complexity signal only; proceedings object | `survey_history_or_commentary` |
| 66 | `B001-AXIS-688766dbd56d7d179c68`; 1: *On the Parameterized Complexity of Bend-Minimum Orthogonal Planarity*; Scopus article/Algorithmica | planarity·NP-hardness·parameterized complexity | `standard_subaxis_research` |
| 67 | `B001-AXIS-6911caeba21ee13f08d6`; 1: *Stringent relativization*; WoS incollection/FSTTCS | relativization·complexity classes | `standard_subaxis_research` |
| 68 | `B001-AXIS-6ace40d73a5d697af411`; 1: *The intractability of computing the Hamming distance*; Scopus article/TCS | intractability·parameterized complexity | `standard_subaxis_research` |
| 69 | `B001-AXIS-6e3744027a40402574e5`; 1: *Hardness Magnification Near State-of-the-Art Lower Bounds*; Scopus article/Theory of Computing | circuit lower bounds·hardness magnification | `core_barrier_or_method_candidate` |
| 70 | `B001-AXIS-7086b777b3dde9033155`; 1: *Covering graphs with few complete bipartite subgraphs*; Scopus article/TCS | graph cover hardness·parameterized complexity | `standard_subaxis_research` |
| 71 | `B001-AXIS-7110a268ca9e3284f159`; 1: *Low complexity algorithms in knot theory*; Scopus article/IJAC | knot theory application; complexity background | `application_or_distant_bridge` |
| 72 | `B001-AXIS-722dd0cb816e21d5e4e4`; 1: *Learning the Coefficients: … Border Complexity … Circuit Factoring*; ACM inproc/STOC | geometric complexity theory·border complexity | `core_barrier_or_method_candidate` |
| 73 | `B001-AXIS-74a1b0083d2ae411bd82`; 1: *Further oracles separating conjectures about incompleteness in the finite domain*; Scopus article/TCS | proof complexity·oracle separations | `alternative_model_or_relativized_variant` |
| 74 | `B001-AXIS-7696324400c0399ead24`; 1: *Towards average-case complexity analysis of NP optimization problems*; Scopus conf/IEEE Structure in Complexity | average-case NP optimization | `standard_subaxis_research` |
| 75 | `B001-AXIS-784455f8fa9f97315e58`; 1: *Some Studies on Circuit Complexity*; PQDT thesis | circuit complexity·lower bounds | `needs_full_text_review` |
| 76 | `B001-AXIS-792d1ab532f6fb4158d5`; 1: *Polynomial kernelizations for MIN F+π1 and MAX NP*; Scopus article/Algorithmica | kernelization·parameterized complexity | `standard_subaxis_research` |
| 77 | `B001-AXIS-7b9a4195da831d170da9`; 1: *Maximizing Phylogenetic Diversity …*; Scopus conf/LIPIcs | ecological/phylogenetic application·parameterized complexity | `application_or_distant_bridge` |
| 78 | `B001-AXIS-7c7bf0a7b5fbcf4605ef`; 1: *Automating OBDD proofs is NP-hard*; Scopus conf/LIPIcs | proof automation·NP-hardness | `standard_subaxis_research` |
| 79 | `B001-AXIS-7cc9aca6319c8cd73369`; 1: *Logic, Automata, and Computational Complexity: The Works of Stephen A. Cook*; ACM book | Cook works/history·proof complexity signal | `survey_history_or_commentary` |
| 80 | `B001-AXIS-7e010f0d8ab13d1370f9`; 1: *Constrained Level Planarity Is FPT …*; Scopus conf/LIPIcs | FPT·vertex-cover parameter | `standard_subaxis_research` |
| 81 | `B001-AXIS-820629250d2b59bac055`; 1: *Two-query PCP with subconstant error*; ACM article/JACM | PCP·query complexity·NP-hardness | `core_barrier_or_method_candidate` |
| 82 | `B001-AXIS-82d1a6210e47f13288c0`; 1: *Oracles for structural properties … public-key cryptography*; Scopus conf | oracle/structural complexity | `alternative_model_or_relativized_variant` |
| 83 | `B001-AXIS-8377daae2bcae3581fa8`; 1: *Relativizations of the P=? NP and other Problems*; Scopus conf/LNCS | relativization·structural complexity | `alternative_model_or_relativized_variant` |
| 84 | `B001-AXIS-842195ec16705dcde364`; 1: *A Dual Perspective on Computational Complexity*; PQDT thesis | natural proofs·lower bounds | `needs_full_text_review` |
| 85 | `B001-AXIS-84b28787bf01d1d85166`; 1: *A superpolynomial lower bound … clique function …*; Scopus article/SICOMP | circuit lower bound | `core_barrier_or_method_candidate` |
| 86 | `B001-AXIS-84ca06dc8216d7a00364`; 1: *Geometric Complexity Theory V: Efficient Algorithms for Noether Normalization*; WoS article/JAMS | GCT·Noether normalization | `standard_subaxis_research` |
| 87 | `B001-AXIS-8912789c891eb6b162f8`; 1: *New perspectives on the complexity of computational learning …*; PQDT thesis | derandomization signal; thesis scope unresolved | `needs_full_text_review` |
| 88 | `B001-AXIS-8a32c55ae5dd97bfd032`; 1: *Maximum minimal vertex cover parameterized by vertex cover*; Scopus article/SIDMA | parameterized vertex cover | `standard_subaxis_research` |
| 89 | `B001-AXIS-8ab1938c0a5778c38b87`; 3: *Computing Multiplicities of Lie Group Representations*; IEEE inproc/FOCS, Scopus conf/FOCS, WoS inproc/FOCS | GCT·representation multiplicities | `standard_subaxis_research` |
| 90 | `B001-AXIS-8b898bbbf86a9dee2501`; 2: *Non-probabilistic techniques in circuit complexity*; ACM PhD thesis, PQDT thesis | circuit complexity·lower bounds | `needs_full_text_review` |
| 91 | `B001-AXIS-8db522e219158f611fa6`; 1: *The Complexity of Homomorphism Reconstructibility*; Scopus article/ACM TOCT | homomorphism/parameterized complexity | `standard_subaxis_research` |
| 92 | `B001-AXIS-8fa6225cd76233a76afc`; 1: *Barrier coverage … aggregate movements*; Scopus conf/LIPIcs | movement-planning application·parameterized complexity | `application_or_distant_bridge` |
| 93 | `B001-AXIS-90ab957cc7c368357ed3`; 1: *Improving exhaustive search implies superpolynomial lower bounds*; Scopus article/SICOMP | exhaustive search–circuit lower-bound implication | `core_barrier_or_method_candidate` |
| 94 | `B001-AXIS-952b19929ed992812cad`; 1: *Separated borders: Exponential-gap fanin-hierarchy theorem …*; ACM article/JACM | approximative depth-3 circuits·GCT signal | `core_barrier_or_method_candidate` |
| 95 | `B001-AXIS-971dfe29f5cc32ac4d9e`; 1: *Characterizing non-deterministic circuit size*; Scopus conf/STOC | communication/circuit complexity·lower bounds | `standard_subaxis_research` |
| 96 | `B001-AXIS-977e0b2ca79421e97388`; 1: *Random resolution refutations*; ACM inproc/CCC | proof complexity·resolution | `standard_subaxis_research` |
| 97 | `B001-AXIS-97c70edd8ae61c14b97a`; 1: *Structural properties of oracle classes*; Scopus article/IPL | oracle classes·relativization | `alternative_model_or_relativized_variant` |
| 98 | `B001-AXIS-99ff2bdc23c675ef878a`; 1: *An Axiomatic Approach to Algebrization*; Scopus conf/Dagstuhl | algebrization·relativization | `core_barrier_or_method_candidate` |
| 99 | `B001-AXIS-9a3b46dcf2139a3d1862`; 1: *The Acrobatics of BQP*; Scopus conf/LIPIcs | BQP/query complexity model | `application_or_distant_bridge` |
| 100 | `B001-AXIS-9de3e60f87df4ac09455`; 2: *Automating resolution is NP-hard*; Scopus conf/FOCS, WoS inproc/FOCS | proof automation·NP-hardness·resolution | `standard_subaxis_research` |
| 101 | `B001-AXIS-9e15988d9b7a63f40385`; 1: *P=NP for some structures over the binary words*; WoS article/Journal of Complexity | specified structures·relativization | `alternative_model_or_relativized_variant` |
| 102 | `B001-AXIS-9e2a25a3fdd3efc54446`; 1: *On generating solved instances of computational problems*; Scopus conf/LNCS | solved-instance generation·relativization | `alternative_model_or_relativized_variant` |
| 103 | `B001-AXIS-9e7c6feb5dc43770a00a`; 1: *On the complexity of various parameterizations of common induced subgraph isomorphism*; Scopus conf/LNCS | parameterizations·NP-hardness | `standard_subaxis_research` |
| 104 | `B001-AXIS-9ee12fe0e3bdfa86814e`; 1: *Oracles for structural properties … public-key cryptography*; Scopus article/JCSS | oracle/structural complexity | `alternative_model_or_relativized_variant` |

## 원시 abstract/keywords 대조 표본

다음은 helper가 provenance의 raw export에서 회수한 excerpt가 실제로 처분을 바꾼 예다. 전체 표의 `ctx`도 같은 방식으로 abstract/keywords와 named axis를 대조해 썼다.

- `B001-SCOPUS-41d18a7c4dcfaa1d00a8` (60번)는 PCP error/query tradeoff, 약 1.5 amortized query NP characterization, Max-kCSP NP-hard approximation을 말한다. 따라서 일반 query-complexity 잡음이 아니라 `core_barrier_or_method_candidate`다.
- `B001-WOS-080cef3efbf600c0e1e9` (61번)는 algebraic proof system의 Nullstellensatz certificate circuit size와 PIT·proof/circuit complexity 연결을 말한다. 그래서 IPS는 core method 후보로 남긴다.
- `B001-SCOPUS-b17b0a06f1993563f8ed` (57번)는 Baker–Gill–Solovay를 relativized P=?NP의 원형으로 명시한다. 따라서 상대화 문헌이지 비상대화 해답이 아니다.
- `B001-SCOPUS-48ad2f9aef29de2798cc` (78번)와 `B001-SCOPUS-130a66d7e918dbcbc1da` (100번)는 각각 OBDD/Resolution automatability가 `unless P=NP`라는 조건부 hardness 문맥임을 명시한다. 해답 주장으로 처분하지 않았다.
- `B001-WOS-61980ad227ff51b3fcaf` (101번)는 binary-word universe의 특정 finite-signature structure에서 (P=NP)라고 명시한다. 바로 그 모형 한정 때문에 `alternative_model_or_relativized_variant`다.
- `B001-SCOPUS-031c111972c1c821d21d` (71번)는 knot genus NP-completeness와 `unless P=NP`를 말하지만 주 결과가 knot algorithm이다. 따라서 P vs NP 직접 해답이 아니라 distant bridge다.

## 집계와 검산

| 처분 | clusters | members |
|---|---:|---:|
| `core_barrier_or_method_candidate` | 9 | 9 |
| `standard_subaxis_research` | 24 | 28 |
| `conditional_problem_result` | 0 | 0 |
| `application_or_distant_bridge` | 4 | 4 |
| `alternative_model_or_relativized_variant` | 8 | 9 |
| `survey_history_or_commentary` | 2 | 2 |
| `purported_resolution_requires_adversarial_review` | 0 | 0 |
| `non_tcs_false_positive` | 0 | 0 |
| `needs_full_text_review` | 5 | 6 |
| **합계** | **52** | **58** |

source slice는 cluster ID 정렬 53–104의 52개 ID이며, 위 표의 ID 집합도 52개다. 이 두 집합의 대칭차는 0이어야 한다. 이 보고서는 B001 intake/candidate/queue를 수정하지 않으며, 원문 미판독 thesis·신규 논문·장벽 후보를 최종 핵심층으로 승인하지 않는다.
