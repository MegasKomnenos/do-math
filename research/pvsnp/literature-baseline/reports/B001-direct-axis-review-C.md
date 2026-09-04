# B001 direct+axis abstract 검토 C 통합: cluster 105–156

범위는 `B001-direct-axis-queue.jsonl`을 `cluster_id`로 정렬한 105–156이다. C1–C8은 이 범위를 6+6+6+6+6+6+6+4 cluster로 분할한다. source queue와 C1–C8 cluster 집합의 대칭차는 0이고, source member 합계와 세부 보고 member 합계는 모두 **64**다.

| 처분 | clusters |
|---|---:|
| `core_barrier_or_method_candidate` | 8 |
| `standard_subaxis_research` | 12 |
| `conditional_problem_result` | 11 |
| `application_or_distant_bridge` | 7 |
| `alternative_model_or_relativized_variant` | 9 |
| `survey_history_or_commentary` | 3 |
| `needs_full_text_review` | 2 |
| `purported_resolution_requires_adversarial_review` | 0 |
| `non_tcs_false_positive` | 0 |
| **합계** | **52** |

세부 근거와 각 slice 검산은 [C1](B001-direct-axis-review-C1.md), [C2](B001-direct-axis-review-C2.md), [C3](B001-direct-axis-review-C3.md), [C4](B001-direct-axis-review-C4.md), [C5](B001-direct-axis-review-C5.md), [C6](B001-direct-axis-review-C6.md), [C7](B001-direct-axis-review-C7.md), [C8](B001-direct-axis-review-C8.md)에 있다. 이 링크들은 제목만의 추정이 아니라 helper가 회수한 raw abstract_excerpt/keywords, provenance·venue·type을 근거로 한 각 cluster의 처분을 제공한다.

## 통합 판정 경계

- algebrization, natural proofs, circuit lower bounds, MCSP/meta-complexity, proof complexity 문헌은 `core_barrier_or_method_candidate`다. 장벽·방법 후보이지 P≠NP 증명으로 승인하지 않는다.
- PCP, SAT/proof complexity, kernelization, sparse reductions, randomized reasoning은 표준 하위축 연구로 남긴다. 정리의 가정·환원 방향은 원문 판독 전 확정하지 않는다.
- 근사·매개변수·평균경우·응용 최적화의 `unless P=NP`, ETH, NP-hardness 결과는 `conditional_problem_result` 또는 distant bridge다. 이들은 고전 최악경우 P 대 NP와 동일하지 않다.
- oracle, relativization, alternative model 결과는 unrelativized 결론으로 전이하지 않는다.
- survey/essay와 thesis는 내용의 최종 타당성·후속 채택을 승인하지 않으며, 필요하면 full-text review로 남긴다.

따라서 이 통합은 초기 선별이며 `covered`나 최종 핵심층 판정이 아니다.
