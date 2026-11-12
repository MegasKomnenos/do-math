# 독해 보고: README.md (독자: LLM·에이전트 시스템 연구자)

## 1. status

complete. 1행부터 191행까지 전문을 읽었다. 지시대로 README.md 외의 파일은 읽지 않았다.

## 2. understanding

### (a) 세션들의 협력 방식과 설계의 성질

runner라는 프로그램이 서로를 기억하지 못하는 새 CLI 대화(Claude Code 또는 Codex)를 차례로 띄운다. 세션들이 공유하는 것은 Git으로 관리되는 knowledge base(records)뿐이다. 역할은 여섯이다. attempt·explorer·formalizer가 수학을 만들고, peer가 그것을 record candidate로 정리하고, review가 claim마다 status를 매기고 출판할지를 정하며, organizer가 knowledge base를 정돈한다. 작업은 누가 배정하지 않는다. attempt는 frontier·index·board를 읽고 node와 section을 스스로 고르며, lease와 등록으로 점유를 표시한다. 조정은 강제가 아니라 정보로 이루어진다. 도구가 거부하는 것은 기계적으로 판정되는 세 경우뿐이다. 세션이 끝나려 하면 session host가 같은 대화를 되살려 종료를 재고하게 한다(기본 세 번). 출판된 record는 바뀌지 않고, 이후의 판단은 finding으로 덧붙는다. frontier는 relation을 명제논리의 모든 방향으로 적용한다. 글이 주장하는 성질은 둘이다. 하나는 record를 통한 연속성이다. 다른 하나는 역할 분리에서 나오는 "독립적 판단"이고, 이를 뒷받침하려고 평가 역할이 생산 역할과 다른 모델을 기본으로 선호하게 했다. 내가 읽은 바는 다르다. 이 "독립성"의 근거는 대화가 분리되어 있고 모델 선호가 다르다는 설계뿐이다. 측정된 것은 없다. 게다가 fallback이 있으면 평가 세션도 생산 세션과 같은 모델로 뜰 수 있고, peer는 생산자의 대화 전체를 받으며 review도 생산자의 원본을 받는다. 그래서 나는 이것을 "독립 판단"이라기보다 "같은 계열 모델이 다른 대화에서 하는 재검토"에 가깝다고 읽었다. 글도 71행에서 이 메커니즘들의 효과가 측정되지 않았다고 스스로 밝힌다.

- 3행: "What the sessions share is a knowledge base" / "No session plans or assigns the others' work."
- 5행: "Independent judgment comes from the separation of roles: the session that writes a piece of mathematics, the session that turns it into a record, and the session that judges the record are three different conversations."
- 21행: "Coordination between sessions works through information rather than enforcement." / "the sessions are trusted to follow the guide."
- 27행: "The configuration is an ordered list with fallbacks, so a launch made while the preferred model is unavailable can use the same model as the producers."

### (b) 게시된 결과가 보증하는 것과 보증하지 않는 것

record의 claim마다 review가 매긴 status(supported/unsupported/undetermined)가 붙는다. 그러므로 record를 출판했다고 해서 그 안의 모든 내용이 보증되지는 않는다. "informally proved"의 뜻은 AI review 세션이 일상 수학 언어로 쓰인 증명을 받아들였다는 것이다. 사람이 확인한 것도, proof checker가 확인한 것도 아니다. relation을 거쳐 frontier가 유도한 증명은 전제에 Lean 증명이 있어도 항상 informal이다. "formally proved"가 되려면 review 세션이 직접 세 가지를 확인해야 한다. broker를 통한 강제 재컴파일, 허용 axiom 목록 대조, node 진술과의 객체·양화사 단위 대조다. run이 complete가 되려면 root가 이 formal 수준에서 정해져야 한다. 첫 run의 root는 informally proved 상태다. 이 상태가 보증하지 않는 것은 넷이다. 사람의 검토가 없었다. 일부 계산은 사전에 가정한 오차 모델 아래의 binary64로 수행되었다. 한 단계(r030ffaeb의 두 단조성)는 주장되고 수치로 확인되었을 뿐 증명되지 않았다. routes에 대한 Lean 작업은 없다. 유한 계산은 그 범위의 유한 진술만 증명한다.

- 43행: "A published record is not a certificate for everything it says."
- 45행: "\"Informal\" here means that the argument is written in ordinary mathematical language and was checked by an AI review session reading the candidate against the originals, not by a person and not by a proof checker."
- 45행: "A proof that the frontier derives through relations is always informal, even when every premise has a Lean proof"
- 47행: "A finite verification proves the finite claim it covers and nothing beyond it."
- 71행: "One step on the routes is asserted and numerically checked but not proved, as described above."

### (c) 첫 run에서 사람이 개입한 범위, 측정된 것과 측정되지 않은 것

글은 사람(user)의 개입을 네 종류로 정리한다. 첫째는 standing input이다. 5일에는 이전 instance의 자료를 쓰지 말라고 했다. 7일에는 동등한 node를 점유할 수 있게 허용했다. 8일에는 에세이와 글쓰기 선호 문서를 넣었다. 9일에는 형식화를 멈추고, 큰 계산보다 사고에 비중을 두라고 하고, "왜 unimodal인가"가 가장 궁금하다고 밝혔다. 12일에는 외부 세션의 자료를 넣고 두 단조성을 우선 증명하라고 요청했다. 둘째는 설정 변경(동시성 4~16, 모델 선호)이다. 셋째는 9일에 review 없이 질문 다섯을 직접 게시한 것이다. 넷째는 9일에 진행 중이던 형식화 다섯을 종료한 것이다. 나는 여기에 두 가지가 더 있다고 읽었다. 하나는 런 도중에 runner 규칙(형식화를 root에 닿는 결과로 제한)을 추가한 일이고, 다른 하나는 사람 쪽이 원고를 쓰다가 12일에 공백을 발견한 일이다. 이 둘은 네 종류 목록에 들어 있지 않다. 측정되어 보고된 것은 집계다. 세션 1,209개와 역할별 내역, record 330개와 출처별 내역, publication commit 414개, node 103개, relation 117개, question 17개(그중 10개 해결), 활성 pipeline 10개, 테스트 316개 전부 통과가 그것이다. 측정되지 않은 것은 글이 직접 밝힌다. sections·questions·종료 재고 같은 메커니즘이 연구의 질을 바꾸었는지는 측정되지 않았다. 테스트는 stand-in에 대한 것이고 수학을 평가하지 않는다. 내가 보기에 다음도 보고되지 않았다. 이전 구현의 instance와의 비교, 비용·토큰, review의 오류율, concern·finding·contested·종료 재고의 발생 횟수, fallback으로 같은 모델이 review를 맡은 비율이다.

- 67행: "The user's interventions in the run were of four kinds."
- 67행: "Five questions were placed on the frontier on 9 November through the runner command, without review. And the five formalizations in progress on 9 November were ended."
- 59행: "At 16:00 Korean time on 12 November the runner had launched 1,209 sessions (302 attempts, 92 explorers, 12 formalizers, 367 peers, 356 reviews, 80 organizers) and published 330 records"
- 71행: "Whether the mechanisms described in the previous sections, such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured; the run shows that they operate, not that they help."
- 159행: "These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce."

(산술 대조: 302+92+12+367+356+80=1,209이고 235+88+7=330이다. formalizer 12개는 출판된 record 7개(65행)와 종료된 5개(65행·67행)의 합과 맞는다.)

### (d) 설계 근거와 검증 보고를 더 읽을 곳

결과는 Zenodo에 있다. concept DOI는 10.5281/zenodo.24110810이고, version 2(12일 02:38, record 300개)와 version 1(11일 00:19, root가 아직 열려 있던 시점)이 있다. 결과를 확인하려면 `index.md`에서 `frontier.md`로 가고, r5909c9e7과 그 `review/feedback.md`를 읽은 뒤, 그 증명이 쓰는 record들로 내려가면 된다. 구현 쪽 자료는 세 곳에 있다. 설계와 결정 기록은 `docs/do-math/rebuild-design.md`에 있다. 설치 시 검증(두 CLI의 실제 실행, root가 formal로 증명된 소형 instance, runner 재시작 후 복구)은 `docs/do-math/rebuild-verification.md`에 있다. 운영 세부는 `SKILL.md`, `reference/operations.md`, `reference/lean.md`에 있다. 원고·해설·영상·계산 증거 묶음은 아직 공개되지 않았다. 생산 세션의 대화와 작업 파일(`sessions/`)과 standing input(`control/inputs`)은 출판된 knowledge base에 들어 있지 않다.

- 69행: "To check the result, open `index.md`, go to `frontier.md` for the root's two routes and the records they cite, open record r5909c9e7 with its `review/feedback.md`, and continue into the records its proof uses."
- 151행: "The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md), and the checks performed when it was installed ... are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md)."
- 87행: "The producing sessions' conversations and working files are not in `knowledge/`; they stay in the instance's `sessions/` directory, which the published knowledge base does not include."
- 67행: "The standing inputs are not part of `knowledge/`; they are in the instance's `control/inputs` directory."

## 3. difficulties

1. 3행: "a repository of records, each holding mathematics that one session produced, a second session developed into an account for others, and a third session assessed, kept unchanged once published with the assessment beside it." 관계절 셋과 분사구가 한 명사에 겹쳐 붙어 있다. "kept unchanged"가 record에 걸리는지 repository에 걸리는지 다시 읽어야 했다.
2. 7행: "The state has to be read with what it does not include." 무엇을 하라는 뜻인지 다음 문장들을 읽고서야 알았다. "include"의 목적어가 무엇인지 모호하다.
3. 7행: "One necessary condition of the root does have a Lean proof." "necessary condition"은 31행에 가서야 정의된다. 7행에서는 이것이 결과에 기여하는지 아닌지 판단할 수 없었다.
4. 7행과 15행: "do-math counts a proposition as settled only when an independently recompiled Lean proof..." / "A node is **settled** when its statement or its negation has been proved." 두 문장이 "settled"를 다르게 써서 이 낱말의 뜻을 확정하지 못했다(5절 1번 참조).
5. 15행: "The research represents the root, and every further proposition it decides to pursue, as a **node**". 결정을 내리는 주체가 "the research"로 되어 있다. 실제로 결정하는 쪽이 세션인지 peer인지 review인지 이 문장만으로는 알 수 없다.
6. 17행: "holding the definitions and assumptions it used, arguments and intermediate results, ... and the obligations that remain." retained work가 이것들을 반드시 담아야 한다는 규정인지, 보통 담는 것을 묘사한 것인지 구별되지 않는다.
7. 19행: "It stays occupied until the work has been developed into a record and reviewed". review가 출판하지 않기로 했을 때 점유가 어떻게 되는지 적혀 있지 않다.
8. 23행: "When its conversation ends, the runner does not close the session at once." conversation이 끝나는 것과 session이 끝나는 것이 어떻게 다른지 한 번 더 읽어야 했다. "up to three times by default" 이후, 즉 세 번 재고하고도 명시적 결정이 없으면 무슨 일이 생기는지도 적혀 있지 않다.
9. 25행: "It also decides what the record proposes to the shared state". "shared state"는 정의되지 않았다. frontier와 glossary를 합친 것으로 짐작했다.
10. 27행: "decides separately whether the record has enough useful content to publish at all". 29행의 "When review finds material worth keeping"과 같은 판정인지 확인해야 했다.
11. 31행: "Formalization is requested only for outcomes that can reach the root in this sense." "outcome"은 정의되지 않았다(proof 또는 refutation으로 읽었다). sufficient path에도 necessary condition에도 속하지 않는 node, 혹은 둘 다에 속하는 node를 어떻게 표시하는지도 나와 있지 않다.
12. 33행: "The user can also place questions on the frontier directly, through a runner command issued by the operator". 행위자가 user인지 operator인지 한 문장 안에서 둘로 갈린다. operator도 아직 정의되지 않았다(59행에서 정의).
13. 35행: "Both are given as understanding rather than as rules." 운영상 무엇이 다른지 알 수 없다. 예컨대 세션이 이 문서들을 따르지 않아도 되는지, 아니면 다른 방식으로 쓰이는지가 나와 있지 않다.
14. 35행: "Attempts, explorers, peers, reviewers and organizers also receive two documents in their starting context." do-math 설계의 일부로 읽히지만, 67행에서는 이 두 문서가 8일에 넣은 standing input이다. 이 문서들이 일반 설계인지 이 instance에만 해당하는지 다시 읽어야 했다.
15. 37행: "each described the way a section of a survey would be". 19행에서 정의한 용어 "section"과 겹쳐서 잠시 헷갈렸다.
16. 39행: "everything they read is supplied by do-math and saved at launch". 세션은 실행 중에 knowledge base를 읽고, 경우에 따라 literature search도 한다. 그래서 "everything"과 "saved at launch"가 어디까지를 가리키는지 모호하다.
17. 27행·43행: "It gives each claim one of three statuses, *supported*, *unsupported* or *undetermined*" (27행). 43행에서 정의된 것은 supported뿐이다. unsupported와 undetermined의 차이는 정의되지 않았다.
18. 51행: "A **concern** is a reported challenge to the support for a claim." 누가 concern을 보고할 수 있는지(세션, review, user)가 적혀 있지 않다.
19. 59행: "some pipelines, as a producing session together with its peer and review are called, were still in progress." 용어가 문장 끝에서 삽입절로 정의되어 다시 읽었다. 이어 "in 414 publication commits"는 record 수(330)보다 많은데, 무엇이 더 들어가는지(organization, finding, question 등) 설명이 없다.
20. 61행: "The first splits the statement into four cases by where a descent followed by a later ascent could lie, relative to the middle index n/2". 네 경우를 나열한 부분을 두 번 읽었다. 특히 "a descent just left of the middle followed by an ascent in the right half"와 "a descent in the left half ... followed by an ascent in the right half"의 경계가 어떻게 다른지 알기 어려웠다.
21. 61행: "the left half following from the same case as in the first route. Both routes therefore pass through the increase of the sequence on its left half". "the same case"가 네 경우 중 어느 것인지 지시되지 않는다. 또 "therefore"로 이어지는 "increase on its left half"는 앞에서 말한 네 경우 어디에도 이름으로 나오지 않았다.
22. 61행: "named pair-beats-capped-threshold in the frontier". 이름만 있고 무엇을 진술하는 node인지에 대한 설명이 없다.
23. 63행: "The gap was found on 12 November while a manuscript was being written from the records". 수동태라 누가 발견했는지(user, operator, 외부 세션) 알 수 없다. 사람의 개입 범위를 판단하는 데 필요한 정보다.
24. 63행: "requires an envelope function to be non-increasing in one variable and six auxiliary pieces to be monotone in another". 7행은 "two monotonicity properties"라고 했다. 이것이 "envelope 하나 + 조각 여섯 묶음 하나 = 둘"이라는 셈인지 확인해야 했다.
25. 65행: "The node is a necessary condition of the root". 이 극한 진술이 왜 root의 필요조건인지 설명이 없다. 받아들이기만 했다.
26. 114행: "a request for one exploration each time an attempt is launched (the request is a flag; it launches an explorer when a question is free and the interval has passed)". 요청, flag, 간격 조건이 어떻게 맞물리는지 두 번 읽었다.
27. 136행: "Request one reassessment of work availability after attempts have reported that every unresolved node is occupied, which otherwise pauses attempt launches." "which"의 선행사가 무엇인지 모호하다. 이 정지 동작은 앞의 설계 절에 나오지 않았다.
28. 147행: "Formal settlement of the root stops new attempts and explorations; existing sessions finish, formalizations and organizations still launch". root가 이미 formal로 정해졌는데 무엇을 형식화하러 formalization이 새로 뜨는지 알 수 없다.
29. 71행: "The research is not finished: at 16:00 Korean time on 12 November, ten pipelines were active." root가 informally proved된 뒤에 세션들이 무엇을 연구하고 있는지 글에 나와 있지 않다(45행에 따르면 informal proof가 난 node는 attempt의 대상에서 빠진다).
30. 168행: "a command-line client for Jev, a hosted model from TypeSafe". Jev와 TypeSafe에 대한 설명이 없다.
31. 177행: "grilling, grill-me". 한 행에 이름이 둘이다. 별개의 스킬인지 같은 스킬의 별칭인지 알 수 없다.
32. 191행: "Four skill directories are adapted from third-party projects". 어느 넷인지 이 글에서는 알 수 없다.

## 4. overclaims

### 효과나 성질을 단정한 문장(측정·근거 없음)

1. 5행: "Independent judgment comes from the separation of roles". 설계 의도가 아니라 효과를 단정하는 평서문이다. 독립성을 측정한 결과는 없다. 오히려 독립성을 약화시킬 사정들이 글 안에 있다. fallback 때문에 평가 세션이 같은 모델로 뜰 수 있다(27행). 첫 run 초기에는 평가 역할이 다른 모델을 선호하지 않았던 것으로 읽힌다(59행). peer와 review는 생산자의 원본을 받는다(25행, 27행).
2. 63행: "Record r030ffaeb, published on 11 November, establishes a lower bound (its Theorem W)". 같은 문단은 이 record의 논증이 증명되지 않은 성질에 의존한다고 말한다. 그런데도 "establishes"라고 단정한다.
3. 71행: "the run shows that they operate". 글은 sections, questions, 종료 재고가 실제로 몇 번 작동했는지 수치를 하나도 보고하지 않는다(재고 횟수, overlap 거부 횟수 등). 그래서 "작동함을 보인다"는 주장도 이 글만으로는 뒷받침되지 않는다.
4. 76행: "a manuscript that develops the two routes to the root as complete proofs from the records is being written". 63행이 routes 위에 증명되지 않은 단계가 있다고 밝힌 상태에서 "complete proofs"라고 썼다.
5. 151행: "a complete small instance whose root was formally proved with an independently reviewed Lean proof". 누가 "independently" 검토했는지 적혀 있지 않다. 글의 체계에서는 AI review 세션으로 읽히는데, 그렇다면 "independently"는 5행과 같은 근거 없는 수식어다.
6. 7행: "do-math counts a proposition as settled only when an independently recompiled Lean proof has been checked against the exact statement". 49행에 따르면 재컴파일하는 주체는 review 세션 자신이다. 이 맥락에서 "independently"가 무엇과 독립이라는 뜻인지 근거가 없다.
7. 3행: "The mathematics is then done by the sessions." 효과 주장은 아니다. 다만 67행의 방향 제시(우선순위 요청, "why"에 대한 관심 표명, 큰 계산 자제)와 63행의 외부 원고 작성 중 공백 발견을 생각하면, 사람의 기여가 실제보다 작게 읽힐 수 있는 단정이다.

### 설계 의도를 서술한 문장(과장으로 보지 않음, 구별용)

- 5행: "so that a later session can tell an established result from a claim that still needs more." 목적절이다.
- 21행: "the sessions are trusted to follow the guide." 신뢰에 기반한다는 설계를 밝힌 것이고, 준수율을 주장하지 않는다.
- 27행: "it is asked to report the gap rather than to write the proof and certify its own work." 요청 사항을 서술했다.
- 29행: "so that the original claim and what later happened to its standing are both visible." 목적절이다.
- 35행: "Both are given as understanding rather than as rules." 의도를 서술했다.

### 측정되지 않았는데 글이 다루지 않은 비교축(주장이 없어 과장은 아니지만 연구자 독자에게 공백이 되는 것)

- 같은 문제를 다룬 "earlier instance ... under a previous implementation"(35행, 59행)과의 비교가 없다.
- 비용·토큰 사용량, review가 놓친 오류의 비율이 보고되지 않았다. 63행의 사례가 그런 오류의 한 예인데 비율은 없다.
- concern, finding, contested, comprehensive review의 발생 횟수가 보고되지 않았다.

## 5. inconsistencies

1. "settled"의 정의
   - 7행: "do-math counts a proposition as settled only when an independently recompiled Lean proof has been checked against the exact statement"
   - 15행: "A node is **settled** when its statement or its negation has been proved. A proof carries one of two levels of assurance, informal or formal ... the run as a whole is complete only when the root is settled at the formal level."
   - 7행에서 settled는 formal만을 뜻한다. 15행에서는 informal이든 formal이든 증명되면 settled이고, "settled at the formal level"이라는 한정어를 따로 둔다. 71행 "for settlement"와 147행 "Formal settlement"도 서로 다른 쪽을 따른다. 33행은 question에도 "settle"을 쓴다.
2. 평가 역할의 모델 선호(기본값과 첫 run)
   - 27행: "By default the peer and review roles prefer a model different from the one the producing roles prefer." / 114행: "peer and review use the reverse order."
   - 59행: "on the evening of 6 November peer and review were moved to Claude Opus 5.5 as their first choice, so that from then on the assessing roles preferred a model different from the producing roles'."
   - 59행은 6일 저녁 전에는 평가 역할이 생산 역할과 같은 모델을 선호했다는 뜻으로 읽힌다. 그러면 첫 run이 기본값을 따르지 않은 것이고, 그 이유가 설명되지 않는다. 같은 날 출판된 formal record r0af7f414와 formalizer record 일곱(65행 "all were published on 6 November")이 어느 쪽 조건에서 검토되었는지도 알 수 없다.
3. 모델 이름
   - 59행: "Claude Opus 5.5", "Claude Fable 5.1", "Codex gpt-6.1-sol"
   - 114행: "Claude `opus`", "Codex `gpt-6.1-sol`"
   - 같은 모델로 보이는 것을 다른 이름으로 부른다. 첫 run에서 6일 이후 평가 역할(Opus 5.5)과 7일 이후 생산 역할(Fable 5.1)은 둘 다 Claude 계열이다. 그런데 59행은 이를 "a model different"로 충족했다고 서술한다.
4. 사람 개입의 범위
   - 67행: "The user's interventions in the run were of four kinds."
   - 65행: "the rule that limits formalization to outcomes that can reach the root was added to the runner afterwards, with this node as the occasion."
   - 런 도중의 runner 코드 변경은 네 종류(standing input, 설정, 질문 게시, 세션 종료) 어디에도 들어가지 않는다. 63행 "The gap was found on 12 November while a manuscript was being written from the records"의 발견 주체도 목록 밖에 있다.
5. "current implementation"의 고정성
   - 7행: "The first full run of the current implementation began on 5 November 2026"
   - 65행: "the rule ... was added to the runner afterwards"
   - "current implementation"의 run이라고 했지만 구현이 run 도중에 바뀌었다.
6. 두 문서가 설계에 속하는지 입력에 속하는지
   - 35행: "Attempts, explorers, peers, reviewers and organizers also receive two documents in their starting context." (일반 설계처럼 현재형으로 서술)
   - 67행: "8 November (the essay on research and the description of the user's writing preferences)" (이 instance의 standing input)
7. r030ffaeb의 지위
   - 63행: "Record r030ffaeb ... establishes a lower bound (its Theorem W)"
   - 63행: "One step of those routes is known to be unproved." / "No record proves them."
8. informal proof의 기준과 실제 수리
   - 45행: "A node is **informally proved** when review accepts a human-readable proof of its statement"; 27행: "if accepting a claim would require an essential proof that the candidate does not contain, it is asked to report the gap rather than to write the proof"
   - 63행: "its review checked them numerically at several parameter values and accepted the record with the remark that they remained to be proved."
   - review는 공백을 보고했지만(remark) 동시에 받아들였다. 글은 이 수리가 45행의 기준과 어떻게 맞는지 설명하지 않는다. 그 결과 root가 "informally proved"로 표시된다(7행).
9. concern 절차와 공백에 대한 실제 대응
   - 51행: "A comprehensive review is launched when a concern is reported, when a node becomes contested, or when the user requests one with a runner command."
   - 63행: "the user asked the instance, through a standing input, to prove the two properties before any other work. Until a record does so, the frontier's state of the root rests on this step as the reviews accepted it."
   - 글이 설계한 이의 제기 경로는 concern과 comprehensive review다. 그런데 이 경우에는 그 경로가 쓰였다는 언급이 없고, standing input이 대응 수단으로 서술된다. 엄밀히 모순은 아니지만 두 서술이 서로 연결되지 않는다.
10. 계산 산술의 분류
   - 47행: "The records distinguish exact integer and interval arithmetic, in which the computation itself controls rounding, from binary64 floating point with an error model assumed in advance"
   - 61행: "in integer interval arithmetic and in floating point with directed rounding"
   - 47행의 이분법에는 "floating point with directed rounding"이 들어갈 자리가 없다.
11. organizer의 역할
   - 37행: "An **organizer** groups published records into modules, ... decides which locally introduced terms become shared vocabulary, and merges nodes or questions that turn out to be the same."
   - 83행: "`index.md`, which lists records the organizer selected as shared context for new sessions"
   - 새 세션의 공유 맥락을 고르는 기능은 역할 서술에 없다. 3행 "No session plans or assigns the others' work."와 비교해 보면, organizer가 다른 세션의 주의를 이끄는 장치로도 읽힌다.
12. pending concern의 효과
   - 51행: "A pending concern changes nothing"
   - 51행: "keep their standing, marked as resting on a questioned claim"
   - "아무것도 바꾸지 않는다"고 하면서 표시(marking)는 바뀐다고 한다.
13. 질문을 직접 게시하는 주체
   - 33행: "The user can also place questions on the frontier directly, through a runner command issued by the operator"
   - 85행: "a question the user placed directly shows an operator publication as its source"
   - 87행: "`questions/` the questions the user published"
14. 역할 이름
   - 17행: "an **explorer**"; 39행·114행: "exploration", "explorations"
   - 17행: "a **review**"; 35행: "reviewers"
15. 미결 상태의 이름
   - 69행: "while the root was still open"; 31행: "counts neither as open work"
   - 51행·85행: "unresolved"

## 6. writing

### 처음 쓰이는 전문 용어가 그 문장이나 바로 앞 문장에서 정의되지 않음

- 7행: "One necessary condition of the root does have a Lean proof." (necessary condition은 31행에서 정의)
- 7행: "every relation on two routes from proved statements to the root" (relation은 15행, route는 61행에서 정의)
- 7행: "an independently recompiled Lean proof" (Lean, recompile 절차는 49행)
- 25행: "the shared state" (정의 없음)
- 29행: "the shared glossary" (처음 등장, 85행에서 설명)
- 31행: "outcomes that can reach the root" (outcome 정의 없음)
- 33행·35행: "issued by the operator", "an operator session" (operator는 59행에서 정의)
- 27행: "*unsupported* or *undetermined*" (43행에서도 정의되지 않음)
- 59행: "some pipelines, as a producing session together with its peer and review are called" (사용과 정의가 같은 문장 끝에서 일어남)
- 63행: "through a standing input" (3행의 "standing conditions"와 같은 것인지 정의 없음)
- 61행: "pair-beats-capped-threshold" (이름만 있음)
- 63행: "an envelope function", "six auxiliary pieces" (정의 없음)
- 69행: "concept DOI" (정의 없음, 괄호 설명만 있음)
- 87행: "A formal record" (정의 없음)
- 168행: "Jev", "TypeSafe" (정의 없음)

### 문장이 내용 대신 계획을 예고함

- 9행: "The sections below describe how the sessions cooperate, what a published result does and does not certify, the first run with its evidence and its limits, the layout of a published knowledge base, and how to run do-math on a proposition of your own."
- 73행: "Several artifacts of the run are being prepared and are not yet public."
- 15행: "which the next section defines" (부분 예고)
- 170행: "The repository's other skills support its development." (표의 머리말 역할)

### 과장·비유·경구·최상급

- 5행: "research that runs for days needs both continuity and judgment that does not come from whoever did the work." (근거 없이 일반 원칙처럼 단정한 경구형 문장)
- 21행: "Coordination between sessions works through information rather than enforcement." (대구형 표어)
- 71행: "the run shows that they operate, not that they help." (대구형 경구)
- 35행: "Both are given as understanding rather than as rules." (대구형)
- 61행: "that was the last part to close", "The last open premise" (서열 표현이지만 사실 서술이다. 과장은 아니다)

### 독자의 내적 상태를 단정하는 문장

- 해당 없음. 7행 "The state has to be read with what it does not include."는 독자에게 지시하는 문장이지 내적 상태를 단정하지 않는다.

### 닫힌 열거로 읽히는 분류

- 17행: "Six roles do the work ... Three roles produce mathematics ... Two roles process ..." (organizer가 나머지 하나로 남는다. 83행에서는 organizer가 맥락 선별도 맡아 역할 분류 밖의 기능이 드러난다)
- 21행: "Tools refuse only what a program can decide by itself: registering ..., registering ..., or omitting ..." ("only"로 닫음)
- 47행: 산술 두 종류(61행에서 세 번째가 나타남)
- 59행: "The session counts differ from the record count because ..." (네 원인을 닫힌 목록처럼 제시)
- 67행: "The user's interventions in the run were of four kinds." (5절 4번 참조)
- 85행: "its state (unresolved, informally proved or refuted, formally proved or refuted, or contested)"
- 35행: "and the like" (열린 열거임을 표시한 사례로, 대조용)

### 사족(반복)

- "사람이 검토하지 않았다"는 내용이 세 번 반복된다. 7행 "No person has reviewed the records.", 53행 "In the first run described next, every one of these judgments was made by AI sessions, and no person has reviewed any record.", 71행 "Every review was an AI session, and no person has reviewed the records." (45행 "not by a person"까지 치면 네 번)
- 형식화 중지가 네 번 반복된다. 7행 "the user paused formalization on 9 November", 65행 "The pause is still in force, and the routes to the root have no Lean work.", 71행 "The formal verification that do-math requires for settlement has not begun", 75행 placeholder
- 63행과 71행: 공백 단계를 다시 서술한다("as described above"로 스스로 반복을 표시)

### 같은 대상을 다른 낱말로 부름

- standing conditions(3행, 126행) / standing inputs(63행, 67행) / inputs(126행) / standing information(137행)
- open(69행) / unresolved(51행, 85행)
- explorer(17행) / exploration(39행, 114행)
- review(17행) / reviewers(35행)
- processing roles(23행) / assessing roles(59행) / peer and review(27행)
- producing session(17행) / producer(25행, 27행) / originals(27행) / retained work(17행)
- record candidate(25행) / candidate(27행)
- account(3행) / exposition(25행, 29행)
- 증명을 받아들이는 동사: accepts(45행) / supported(85행 "every supported proof") / accepted(61행)
- Claude Opus 5.5(59행) / Claude `opus`(114행)
- operator(59행) / operator session(35행) / the conversation that handles that request(95행)
- settled(15행) / proved(45행) / close(61행 "the last part to close")

### 명사 하나로 자리만 잡아 두고 다음 문장에서 지시어로 채움

- 7행: "The state has to be read with what it does not include. No person has reviewed the records. ..."
- 23행: "When its conversation ends, the runner does not close the session at once. A separate process, the **session host**, ..."
- 43행: "A published record is not a certificate for everything it says. Each claim in a record carries the review's status."
- 57행: "Parking functions come from the following process. There are n parking spots ..."
- 61행: "The frontier shows two. The first splits ..."
- 63행: "One step of those routes is known to be unproved. Record r030ffaeb, ..."
- 65행: "One node has a formal proof. Record r0af7f414, ..."
- 67행: "The user's interventions in the run were of four kinds. Standing inputs, ..."
- 71행: "The result has the following limits. Every review was an AI session, ..."

## 7. uncertainties

1. 6일 저녁 전에 peer와 review가 어떤 모델을 선호했는지 글에 적혀 있지 않다. 59행의 "so that from then on"에서 그 전에는 생산 역할과 같은 모델이었다고 추론했다. 이 추론이 맞다면, 6일에 출판된 formal record r0af7f414의 review가 같은 모델로 이루어졌는지도 확정할 수 없다.
2. run 전체에서 fallback 때문에 review가 생산자와 같은 모델로 뜬 횟수는 보고되지 않았다.
3. "Claude Fable 5.1"과 "Claude Opus 5.5"가 "different model"로서 얼마나 다른지는 글에 근거가 없다. 둘 다 Claude 계열이라는 것은 이름에서 읽은 것이다.
4. 12일의 공백을 누가 발견했는지 모른다. "while a manuscript was being written from the records"의 원고 작성자가 user인지, operator인지, instance 밖의 AI 세션인지 확정하지 못했다. 76행·77행의 원고와 해설을 누가 쓰는지도 마찬가지다.
5. r030ffaeb의 공백에 대해 concern이 제기되었는지, comprehensive review가 열렸는지, frontier가 지금 그 의존을 표시하는지 글만으로는 알 수 없다.
6. `control/inputs`, 에세이, 글쓰기 선호 문서가 공개되는지 모른다. 87행과 67행에 따르면 이것들은 `knowledge/`에 없다. 그렇다면 외부 독자는 사람의 개입 내용과 세션에 주입된 맥락을 출판물만으로 대조할 수 없다고 읽었다.
7. 에세이를 쓴 user와 operator는 이전 instance의 record를 읽었다(35행). 5일의 조건은 이전 instance 자료를 쓰지 말라는 것이었다(59행, 67행). 이 둘 사이의 정보 누출 가능성에 대해 글은 "it draws its examples from the history of mathematics, not from that instance"라고만 말한다. 그 이상의 통제가 있었는지는 알 수 없다.
8. 12일 04:54에 넣은 외부 세션 자료(67행)의 내용과 영향을 모른다. version 2는 그 전에 찍혔으므로 root의 informal 증명에는 영향이 없다고 읽었다. 이것도 69행의 시각 대조에서 추론한 것이다.
9. root가 informally proved된 뒤에 활성 pipeline 10개(71행)가 무엇을 하는지 모른다.
10. 첫 run의 record가 어느 언어로 쓰였는지, scholarly-mcp가 첫 run에 설정되었는지 글에 나와 있지 않다.
11. 이전 구현의 instance가 같은 문제에서 어떤 결과를 냈는지 글에 없다. 그래서 이번 결과를 구현 변경의 효과로 해석할 근거도 없다.
12. 61행에서 두 route의 논리 구조, 즉 네 경우와 "increase on its left half"의 관계와 "the same case"가 무엇을 가리키는지를 확정하지 못했다. 65행의 극한 진술이 root의 필요조건이라는 것도 확인하지 못하고 받아들였다. 조합론을 모르는 독자로서 글만으로는 검증할 수 없었다.
13. 414 publication commits와 330 records의 차이가 무엇으로 채워지는지(organization, finding, question 게시 등) 짐작만 했다.
14. 151행의 "independently reviewed"가 AI review 세션을 뜻하는지 사람의 검토를 뜻하는지 글만으로는 확정하지 못했다. 글의 체계에 비추어 AI review로 읽었다.
