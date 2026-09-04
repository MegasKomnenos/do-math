# B001 직접 P/NP 제목 전수 검토

검토일: 2026-09-04 KST

`B001-candidates.jsonl`에서 제목 자체에 P-vs-NP 표현이 있는 165개 source record를 DOI 또는 DOI 없는 exact 제목·creator·연도 신호로 107개 검토 cluster에 모았다. 이 cluster는 복수 색인의 같은 work 후보를 함께 읽기 위한 단위이며 판본 병합이나 최종 핵심층 승인이 아니다.

세 slice [A: 1–36](B001-direct-title-review-A.md), [B: 37–72](B001-direct-title-review-B.md), [C: 73–107](B001-direct-title-review-C.md)의 cluster 집합은 source queue와 대칭차 0이고 member 합계는 54+58+53=165다.

## 처분

| 처분 | clusters | 의미 |
|---|---:|---|
| `authoritative_status_or_history` | 9 | 상태·역사·권위 있는 종합 후보 |
| `standard_pnp_research` | 11 | 고전 P/NP와 직접 연결된 연구·장벽 후보 |
| `conditional_hardness_or_consequence` | 17 | P=NP/P≠NP 가정 또는 문제별 난도 결과; 가정을 결론으로 전환 금지 |
| `alternative_model_or_relativized_variant` | 35 | oracle·real/ring·infinite-time·membrane 등 다른 모형; 고전 문제와 경계 유지 |
| `education_or_commentary` | 20 | 강의·poll·대중 논평·editorial; 연구 명제 근거와 분리 |
| `purported_resolution_requires_adversarial_review` | 8 | 표준 문제 해결을 표방하나 승인하지 않은 주장 |
| `non_tcs_false_positive` | 3 | P/NP 문자열이 complexity class를 뜻하지 않는 검색 오탐 |
| `needs_full_text_review` | 4 | metadata만으로 모형·주장 범위를 판정할 수 없음 |
| **합계** | **107** | — |

## 핵심 관찰

B001은 B002의 기준서 표본에 없던 직접 연구와 상태 전거를 실제로 보완한다. Fortnow의 2009 CACM status, GCT I 및 후속 JACM/CACM 축, circuit lower-bound 방법론, bounded proof theory, fine-grained hardness, 2026 time-bounded Kolmogorov-complexity STOC record 등이 여기에 있다. 이는 B001을 최종 집합에서 제외할 수 없다는 직접 근거다.

조건부·대체 모형 52개 cluster는 별도 가치가 있지만 표준 Boolean uniform P 대 NP와 같은 명제로 쓰지 않는다. `P≠NP for the reals`, infinite-time Turing machine, ring/Boolean algebra, oracle, membrane·quantum/physical model의 결론은 각각 계산 모형과 환원 정의를 다시 읽어야 한다.

해결을 표방한 8개 cluster에는 *A New Proof of Inequality*, *An Argument for P=NP*, perfect-graph 접근으로 P=NP를 결론내린다는 논문, dialectical-systems 해법, 2023·2024·2025의 inequality/experimental proof 주장이 있다. 조사 시점의 [Clay Mathematics Institute 공식 페이지](https://www.claymath.org/millennium/p-vs-np/)는 문제를 여전히 **Unsolved**로 표시하므로, 이 8건은 핵심 결과로 승인하지 않고 주장·정의·환원·반박을 적대적으로 검토할 대기열로 둔다.

명백한 검색 오탐은 Einstein–Maxwell 물리식의 `P=NP`, 선호/비선호 rat 표기의 `P vs NP`, forensic DNA database의 다른 p/np 문면 3건이다. 반대로 *The P versus NP Problem in Quantum Physics* 두 source record는 제목이 실제 P/NP를 가리키므로 오탐으로 버리지 않고 full-text 검토로 보냈다.

기계 판독 가능한 처분은 `catalog/B001-direct-title-decisions.jsonl`, source queue는 `catalog/B001-direct-title-queue.jsonl`, 해시와 계수는 [`../manifests/B001-direct-title-decisions.json`](../manifests/B001-direct-title-decisions.json)에 있다. 다음 단계는 20개 권위/표준 후보의 판본·원문 좌표를 확정하고, 8개 해결 주장과 4개 미확정 항목을 우선 반증·검증하는 것이다.
