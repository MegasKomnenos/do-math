# B001 direct+axis abstract 검토 C2: cluster 117–122

원자료: `B001-direct-axis-queue.jsonl` cluster_id 정렬 117–122와 `build_b001_catalog.py --show-review-candidate`의 raw `abstract_excerpt`/keywords. source slice 6 clusters, member 합계 6, 아래 ID 집합과 대칭차 0이다.

| cluster_id | members | 제목·venue | 처분 | abstract/keywords 근거 |
|---|---:|---|---|---|
| B001-AXIS-b688044d18424609e58f | 1 | *From P (sic) NP to Practice: Description Complexity and Certificate-First Algorithm Discovery for Hard Problems* — Mathematics | survey_history_or_commentary | raw abstract가 position/expository essay라고 명시하고, P=NP의 해답이 아니라 certificate-first heuristic/verification 방향을 제안한다. |
| B001-AXIS-b7378915045d241e0785 | 1 | *Thinking algorithmically about impossibility* — LIPIcs CSL | core_barrier_or_method_candidate | abstract는 lower bounds, circuit complexity, derandomization, satisfiability와 program meta-analysis를 직접 다룬다. P≠NP 증명은 아니며 방법 후보로 보관한다. |
| B001-AXIS-b88c8a2f339a2652983c | 1 | *Fixed-parameter algorithms for Kemeny rankings* — TCS | conditional_problem_result | raw abstract는 Kemeny score의 FPT/NP-complete 경계와 `unless P=NP` 조건을 명시한다. 계산사회선택 응용 결과다. |
| B001-AXIS-bb5629ea23156208f1df | 1 | *Qualitative relativizations of complexity classes* — JCSS | alternative_model_or_relativized_variant | raw abstract는 제한 oracle access의 positive relativization과 P=?NP∩coNP 질문을 명시한다. 일반 P/NP 분리가 아니다. |
| B001-AXIS-bb989dd80ea18c6b8b0c | 1 | *Parameterized modal satisfiability* — Algorithmica | conditional_problem_result | raw abstract는 modal satisfiability의 FPT와 tower dependence, ETH lower bound, `unless P=NP` 조건을 명시한다. |
| B001-AXIS-bce993c0e148ea269c3b | 1 | *Weak lower bounds on resource-bounded compression imply strong separations of complexity classes* — STOC | core_barrier_or_method_candidate | raw abstract는 MCSP/hardness magnification, resource-bounded Kolmogorov complexity, 조건부 `P≠NP`, `NP⊄P/poly` 연결을 명시한다. 직접 분리 증명이 아니라 방법 후보다. |

처분은 abstract의 조건·모형을 넘어 확정하지 않는다. `unless P=NP`, ETH, oracle/relativization, MCSP hardness magnification은 P vs NP 해결의 승인이 아니다.
