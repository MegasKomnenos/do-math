# B001 P/NP 문맥+명시 복잡도 축 전수 검토

검토일: 2026-09-04 KST

제목에는 직접 P-vs-NP 표현이 없지만 원시 초록·keyword에서 P/NP 문맥과 proof complexity, circuit complexity, relativization, PCP/query, derandomization, GCT, parameterized·communication·fine-grained·meta-complexity 중 하나가 함께 나타난 186개 source record를 156개 cluster로 검토했다.

각 member는 `build_b001_catalog.py --show-review-candidate`로 provenance의 원시 파일·rank에서 abstract/keywords를 다시 회수했다. catalog의 검색 신호나 제목만으로 처분하지 않았고, 초록 전문은 추적 산출물에 복제하지 않았다.

## 범위와 검산

| slice | 보고서 | clusters | members | source 대칭차 |
|---|---|---:|---:|---:|
| 1–52 | [A](B001-direct-axis-review-A.md) | 52 | 64 | 0 |
| 53–104 | [B](B001-direct-axis-review-B.md) | 52 | 58 | 0 |
| 105–156 | [C](B001-direct-axis-review-C.md) | 52 | 64 | 0 |
| **합계** | — | **156** | **186** | **0** |

세 slice의 cluster 집합은 서로 겹치지 않고 source queue 전건과 일치한다. 한 DOI `10.1016/j.jco.2005.02.001`은 Scopus title에 공백이 있어 direct-title queue에, WoS title `P=NPfor…`에는 공백이 없어 이 axis queue에 각각 source record가 배치됐다. 두 record는 같은 DOI 관계로 연결되며, source record 자체는 어느 queue에서도 중복 처리하지 않았다.

## 처분

| 처분 | clusters |
|---|---:|
| `core_barrier_or_method_candidate` | 26 |
| `standard_subaxis_research` | 46 |
| `conditional_problem_result` | 24 |
| `application_or_distant_bridge` | 27 |
| `alternative_model_or_relativized_variant` | 18 |
| `survey_history_or_commentary` | 8 |
| `needs_full_text_review` | 7 |
| `purported_resolution_requires_adversarial_review` | 0 |
| `non_tcs_false_positive` | 0 |
| **합계** | **156** |

핵심 방법 후보에는 PCP/query tradeoff, algebrization·natural-proofs 이후 장벽, IPS·proof/circuit complexity, GCT/de-bordering, hardness magnification, MCSP·resource-bounded compression, meta-complexity, exhaustive-search와 lower-bound 연결이 있다. 표준 하위축은 structural/oracle complexity, sparse reductions, proof automation, kernelization·parameterized complexity, average-case·fine-grained·communication complexity를 보완한다.

조건부·응용 51개 cluster의 `unless P=NP`, ETH, NP-hardness, approximation/kernel lower bound는 해당 문제의 조건부 결과로만 유지한다. oracle·real/arithmetic model 18개도 고전 비상대화 P/NP 결론으로 전이하지 않는다. 7개 full-text 대기는 thesis와 abstract만으로 정확한 정리 범위를 확정하지 못한 record다.

기계 판독 가능한 처분은 `catalog/B001-direct-axis-decisions.jsonl`, source queue는 `catalog/B001-direct-axis-queue.jsonl`, 해시와 계수는 [`../manifests/B001-direct-axis-decisions.json`](../manifests/B001-direct-axis-decisions.json)에 있다. 이 검토는 최종 핵심층 승인이 아니라 원문·판본 판독 우선순위를 확정한다.
