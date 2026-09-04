# B001 direct+axis abstract 검토 C1: cluster 105–110

원자료: `B001-direct-axis-queue.jsonl`의 cluster_id 정렬 105–110과 `build_b001_catalog.py --show-review-candidate`가 반환한 raw `abstract_excerpt`/keywords. source slice는 6 clusters, member 합계 7이며 아래 ID 집합과의 대칭차는 0이다.

| cluster_id | members | 제목·venue | 처분 | abstract/keywords 근거 |
|---|---:|---|---|---|
| B001-AXIS-9f138e7aef2f9748f480 | 1 | *On guarded extensions of MMSNP* — LMCS | standard_subaxis_research | abstract는 MMSNP/CSP dichotomy와 NP embedding을 다루며, P vs NP 해결 주장이 아니라 descriptive complexity·CSP 하위축이다. |
| B001-AXIS-9f21580a999e815c23e5 | 1 | *Maximum Coverage in Random-Arrival Streams* — LIPIcs ESA | conditional_problem_result | abstract는 `1-1/e` 근사 한계가 `unless P=NP`라는 조건과 streaming space lower bound를 명시한다. 최대 coverage의 조건부 근사 결과이지 P/NP 분리가 아니다. |
| B001-AXIS-a2d55a48b9c3ba35e649 | 1 | *On the parameterized complexity of default logic and autoepistemic logic* — LNCS | conditional_problem_result | abstract는 parameterized logic problems의 FPT/XP 결과와 `unless P=NP` 조건을 명시한다. |
| B001-AXIS-a4229ff2d928827d2a83 | 1 | *Parameterized complexity of MaxSat above average* — LNCS | conditional_problem_result | abstract는 para-NP-completeness, ETH 조건, MaxSat-AA의 FPT 경계를 실제로 말한다. |
| B001-AXIS-a4ba8a366bfc2a242f54 | 1 | *On relativizations with restricted number of accesses to the oracle set* — Mathematical Systems Theory | alternative_model_or_relativized_variant | abstract는 Baker–Gill–Solovay phenomena와 제한 oracle query 모형의 positive/qualitative relativization을 다룬다. 일반 P vs NP 결론이 아니다. |
| B001-AXIS-a51347ebe319d0dee02d | 2 | *Symmetry of information from meta-complexity* — CCC 2022/LIPIcs | core_barrier_or_method_candidate | 두 raw abstract는 average-case NP-easiness, Kt complexity, MCSP/NP-hardness와 `NP ⊄ BPP`, `NP ⊄ P/poly` 조건부 separation의 연결을 명시한다. 직접 P vs NP 증명은 아니나 meta-complexity/average-case 방법 축의 핵심 후보로 보관한다. |

처분은 abstract의 조건·모형을 넘어서지 않는다. 특히 `unless P=NP`, oracle/relativized, ETH, NP-hardness는 P≠NP의 승인 근거가 아니다.

## cluster 111–116

원자료: 같은 queue 정렬 111–116과 helper의 raw abstract/keywords. source slice 6 clusters, member 합계 7, 아래 ID 집합과 대칭차 0이다.

| cluster_id | members | 제목·venue | 처분 | abstract/keywords 근거 |
|---|---:|---|---|---|
| B001-AXIS-a56aa21a96d794d035f0 | 1 | *Adding cardinality constraints to integer programs with applications to maximum satisfiability* — IPL | conditional_problem_result | raw abstract는 Max-SAT-CC의 근사비와 그 최적성이 `unless P=NP`임을 명시한다. 특정 근사 문제 결과다. |
| B001-AXIS-a687b4d2013208c82487 | 1 | *On reductions of NP sets to sparse sets* — JCSS | standard_subaxis_research | abstract는 SAT의 sparse set truth-table reduction이면 P=NP라는 조건부 결과와 sparse oracle construction을 명시한다. 구조복잡도 하위축이다. |
| B001-AXIS-ac209839b841d66c74d3 | 1 | *NP-Hardness of circuit minimization for multi-output functions* — CCC/LIPIcs | standard_subaxis_research | title·venue·queue axis는 MCSP/circuit minimization 하위축을 직접 가리킨다. raw abstract의 정리 세부는 후속 원문 판독 전 확정하지 않는다. |
| B001-AXIS-adf8702c96698e7bb602 | 1 | *Generic separations* — JCSS | alternative_model_or_relativized_variant | generic/oracle separation 방법의 구조복잡도 문맥이며, 일반 P/NP 해답으로 전이하지 않는다. |
| B001-AXIS-b3cb78ed8f3ddc67b99a | 1 | *The computational complexity of understanding binary classifier decisions* — JAIR | application_or_distant_bridge | classifier explanation의 계산 난도다. P/NP 직접 명제나 회로 하계가 아니다. |
| B001-AXIS-b4fb89398d6f61045eb2 | 2 | *Algebrization: a new barrier in complexity theory* — STOC | core_barrier_or_method_candidate | 두 raw abstract는 P≠NP, natural proofs, relativization을 넘어야 하는 algebrization barrier와 non-algebrizing techniques를 명시한다. 장벽 방법 후보이며 해결 증명이 아니다. |
