# 독해 보고: AI 연구자 독자 (README.md, 181행)

## 1. status

complete. 1–181행 전문을 한 번에 읽었다. 다른 파일은 읽지 않았다. 링크(설계 문서, 검증 문서, Zenodo)는 열지 않았다.

## 2. understanding

### (a) 세션 협력과 구별되는 성질

내가 읽은 구조는 이렇다. 서로 기억을 공유하지 않는 CLI 세션(Claude Code 또는 Codex)을 runner가 계속 띄운다. 세션 사이의 유일한 통로는 Git 저장소다. 작업 하나는 세 단계를 거친다. attempt(또는 explorer, formalizer)가 일하고, 새 세션인 peer가 그 작업 전체(대화 포함)를 받아 수학을 직접 더 전개하면서 공개용 기록 후보를 쓴다. 다시 새 세션인 review가 후보와 원본을 양방향으로 대조해 주장마다 supported / unsupported / undetermined를 매긴다. 공개된 record는 바뀌지 않고, 나중의 판정은 finding으로 덧붙는다. frontier, index, board, glossary는 저장소에서 렌더링된다. 일을 나눠 주는 계획 세션은 없다. 각 attempt가 frontier를 읽고 node와 section을 스스로 고르며, 점유는 lease와 등록으로 알린다. 조정은 정보로 이루어지고 강제는 기계적으로 판정할 수 있는 몇 가지(동일 문장 등록, 부분 점유 중 전체 등록, 비중첩 사유 누락)에만 걸린다. 승인된 relation은 명제논리로 양방향 전파된다. 글이 명시적으로 내세우는 구별점은 계획자가 없다는 것, 연속성은 기록에서 오고 독립성은 역할 분리에서 온다는 것, 현재 상태에 대한 별도 서술이 없어 증거에서 벗어날 수 없다는 것이다. 다만 글은 다른 AI 수학 시스템이나 멀티에이전트 시스템과 비교하지 않는다. "무엇이 다른가"는 내가 설계 서술에서 추론한 것이다. 내가 구별되는 성질로 읽은 것은 다음 다섯이다. (i) 스티그머지 방식의 자기 선택. (ii) peer가 요약자가 아니라 공동 저자라는 점. (iii) review가 빠진 증명을 직접 써서 스스로 인증하지 못하게 막은 금지. (iv) 불변 기록과 finding의 분리. (v) 생산 역할과 검증 역할에 서로 다른 모델을 기본으로 배정한 것.
- 3행: "There is no planning session that hands out tasks."
- 5행: "do-math takes continuity from the records and independence from the separation of roles."
- 19행: "Coordination among sessions works through information rather than enforcement."
- 25행: "if accepting a claim would require an essential proof that the candidate does not contain, it reports the gap instead of writing the proof and certifying its own work."
- 27행: "No session writes a separate account of the current state that could drift from the evidence."

### (b) 게시된 결과가 보증하는 것과 보증하지 않는 것

record 하나는 주장 전부에 대한 인증서가 아니다. 주장마다 review 상태가 붙어 있다. 층위는 셋이다. 첫째, informally solved는 AI review 세션이 사람이 읽을 수 있는 증명을 원본과 대조해 받아들였다는 뜻일 뿐이다. 사람이나 기계가 확인한 것이 아니다. 둘째, 계산은 입력·범위·산술·코드·출력을 밝혀야 한다. 정수·구간 산술과 사전에 가정한 오차 모형을 쓰는 binary64를 구별하고, 후자에 기대는 승인은 그 사실을 표시한다. 셋째, formally solved는 review가 Lean을 다시 컴파일하고, 공리를 대조하고, 진술을 대상 하나하나 대조하는 세 확인을 통과한 경우다. root는 이 방법으로만 settled가 된다. relation을 거쳐 유도된 해는 전제에 Lean 증명이 있어도 늘 informal이다. 그러므로 첫 운전의 결과가 보증하는 것은 "AI 리뷰를 받은 논증 사슬이 있고, 그 증거가 공개되어 있다"까지다. 사람의 검토와 형식 검증은 보증하지 않는다. 마지막 고리는 binary64 계산 입력(n ≤ 20000 인증 포함)을 물려받는다. root 자체는 frontier가 relation 사슬로 유도한 것이고, 사슬 전체를 한 세션이 처음부터 끝까지 검토했다는 서술은 없다.
- 41행: ""Informal" here means that the argument was checked by an AI review session reading the candidate against the originals, not by a person and not by a machine."
- 41행: "A solution derived through accepted relations is always informal, even when every premise has a Lean proof"
- 49행: "No person has reviewed any of its records."
- 57행: "stated that the proof inherits computer-assisted inputs in binary64 from earlier records"
- 57행: "With that node proved, the frontier derived the root through the chain of accepted relations."

### (c) 첫 운전에서 사람이 개입한 범위, 측정된 것과 측정되지 않은 것

61행은 사용자 개입을 닫힌 목록으로 제시한다. 11월 5일 독립성 조건, 7일 점유된 node와 동치인 node를 택해도 된다는 허용, 8일 에세이와 글쓰기 서술, 9일 형식화 중지·대규모 계산 억제·"왜 단봉인가"라는 관심 표명, 같은 날 operator가 넣은 질문 다섯, 12일(root 이후) 외부 세션 자료와 단조성 사실 두 개의 증명 요청이다. 그러나 본문 다른 곳에 이 목록에 없는 개입이 나온다. 사용자가 동시 세션 수를 4–16 사이에서 여러 번 바꿨고(55행), 진행 중이던 형식화 다섯을 끝냈으며(59행), 11월 6일부터 peer/review 모델 배정이 바뀌었다(55행, 누가 바꿨는지 불명). 측정된 것은 규모 집계(세션 1,209, record 330, commit 414, node 103, relation 117, question 17/해결 10), 316개 테스트 통과, 그리고 기록 단위의 review 판정이다. 측정되지 않은 것은 글이 스스로 밝힌다. sections, questions, 종료 재고 같은 장치가 연구의 질을 바꿨는지는 측정되지 않았다. 내가 보기에 그 밖에도 기준선 비교, 비용(토큰·시간), review 거부율, review 오류율, peer와 review가 실제로 다른 모델로 돈 비율, 점유 장치가 중복을 얼마나 줄였는지에 대한 수치가 없다.
- 61행: "The user intervened in the run in the following ways, and only these."
- 55행: "The number of concurrent sessions was changed by the user several times, between 4 and 16."
- 65행: "Whether the mechanisms described above, such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured; the run is evidence that they operate, not that they help."
- 151행: "These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce."

### (d) 설계 근거와 검증 보고를 더 읽을 곳

설계와 결정 기록은 docs/do-math/rebuild-design.md에 있다. 설치 시 검증(두 CLI 실가동, Lean 증명으로 settled된 소형 인스턴스, runner 재시작 후 복구)은 docs/do-math/rebuild-verification.md에 있다. 운영과 실패 처리는 .claude/skills/do-math/reference/operations.md, broker는 reference/lean.md, 진입점은 SKILL.md, 예정 작업은 ROADMAP.md에 있다. 수학 결과에 대한 검증 보고는 Zenodo 지식 베이스(버전 2 DOI 10.5281/zenodo.24142218)의 각 record 안 review/feedback.md, review/assessment.json, 그리고 reviews/(comprehensive review)에서 읽는다. 원고, 해설, 영상, 계산 증거 묶음, root의 Lean 증명은 아직 공개되지 않았다(자리 표시만 있음).
- 143행: "The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md)"
- 143행: "are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md)."
- 63행: "To check the result, open `knowledge/index.md`, follow the frontier to the root's two routes, open record r5909c9e7 and its `review/feedback.md`, and continue into the records it cites."
- 67행: "Several artifacts of the run are being prepared and are not yet public."

## 3. difficulties

1. 7행 "the operator paused formalization on 9 November" / 59행 "on 9 November the user paused all formalization" / 69행 "formalization is paused by the operator's decision of 9 November". 55행은 operator를 사용자가 인스턴스를 다루는 AI 대화로 정의한다. 그렇다면 중지를 결정한 주체가 사람인지 AI operator인지가 글 안에서 엇갈린다. 개입 범위를 따지는 독자에게 이 차이는 핵심이다.
2. 7행 "operator"가 정의 없이 먼저 쓰이고, 정의는 55행에 가서야 나온다.
3. 7행 "do-math counts a proposition as settled only when an independently recompiled Lean proof has been checked" 대 15행 "A node is settled by proving its statement or by proving its negation." 15행만 읽으면 informal 증명으로도 settled가 되는 것처럼 읽힌다. 45행 "The root is settled only this way"를 보면 root에 한정한 말인지, 모든 node에 해당하는 말인지 두 가지로 읽힌다.
4. 17행 "A section is registered through the node's **lease**, which lets one session at a time choose on that node; the lease has no time limit and ends only when the session registers, releases, or ends." 등록하면 lease가 끝난다고 하므로 lease는 고르는 동안의 상호배제이고, 점유는 등록이 맡는다. 같은 문단의 "it stays occupied until..."까지 다시 읽고 나서야 두 층이 구별되었다. "choose on that node"는 뜻이 모호하다.
5. 19행 "the role guides explain how to respect it". role guide는 여기서 처음 나오는데 정의가 없다. 143행의 "six worker guides"와 같은 것으로 추정했다.
6. 21행 "It retains its work as it goes" / 23행 "the attempt's private folder". "retained work"가 저장되는 위치와 형식이 정의되지 않는다.
7. 21행 "A separate process, the session host". runner와의 관계(runner가 띄우는 하위 프로세스인지)가 불명이다.
8. 23행 "It goes to a peer." 앞 문단 끝의 "its retained work goes on"을 이어받는 "It"이 문단 첫머리에 온다. 지시 대상을 찾으려고 앞 문단으로 돌아가야 했다.
9. 23행 "what the record proposes to the shared state: new nodes, relations, solutions, questions, and terminology". "solutions"를 제안한다는 것이 무엇인지(해의 주장인지, 해 기록인지) 정의되지 않는다.
10. 25행 "By default, peer and review are assigned a model different from the one the producing roles use." "producing roles"가 무엇을 가리키는지 정의되지 않는다(attempt·explore·formalizer로 추정, organizer 포함 여부는 불명). 108행에서는 이것이 선호 순서와 대체(fallback)라는 것이 드러난다. 그렇다면 대체가 일어나면 같은 모델이 될 수 있는지가 불명이다.
11. 27행 "A later review that finds a defect, or confirms a result, attaches a **finding**". 어떤 review인지(일반 review인지 47행의 comprehensive review인지)는 47행을 읽고 나서야 추정할 수 있다.
12. 29행 "Each node is also marked by how it stands to the root". 표지의 범주가 주어지지 않는다(79행에도 없음).
13. 29행 "formal work is sent only for outcomes that can reach the root through the accepted relations" 대 59행. 59행에서 Lean으로 증명된 node는 필요조건이므로 "its proof leaves the root open"이다. 증명이라는 결과는 root에 닿지 못하는데 형식화되었다. 29행 규칙과 어떻게 맞는지 다시 읽어도 풀리지 않았다(반박이라면 닿는다는 뜻일 수 있다).
14. 31행 "what an object looks like in the regime where every estimate loses its margin". 비유적이라 구체적인 뜻을 알 수 없다.
15. 33행 "Both are given as understanding rather than as rules." "understanding으로 준다"는 것이 운영상 무엇을 뜻하는지(프롬프트 안 위치, 준수 검사 유무) 불명이다.
16. 33행 "written for this system after reading the records of an earlier run". 이전 운전이 같은 문제에 대한 것인지 불명이다. 55행의 "use no material from any earlier research on the problem"과 충돌할 가능성을 판단할 수 없다.
17. 35행 "eligible exploration". eligible의 조건이 정의되지 않는다.
18. 35행 "under your existing authentication". 독자 "you"가 여기서 갑자기 등장한다.
19. 41행 "the result can be used within its supported scope". "supported scope"가 정의되지 않는다.
20. 43행 "binary64 floating point with an error model assumed in advance". 오차 모형이 증명된 상계인지 가정인지 모호하다. 이 단계에 기대는 결과가 수학적으로 엄밀한지 판단할 수 없다.
21. 45행 "three independent checks by the review session". 한 세션이 하는 세 확인을 "independent"라 부른다. 무엇으로부터 독립인지 두 가지로 읽힌다.
22. 47행 "a **comprehensive review** examines the evidence and its actual uses". 언제, 누가 촉발하는지가 132행 명령표를 보기 전에는 불명이다. 자동으로 촉발되는지는 끝까지 불명이다.
23. 55행 "from 6 November, peer and review were assigned a different model from the producing roles". 25행에서 기본값으로 서술한 것이 운전 도중에 도입되었다는 뜻으로 읽힌다. "first full run of the current implementation"(7행)과 함께 읽으면 운전 중 구현이나 설정이 바뀌었는지 불명이다.
24. 55행 "1,209 sessions (302 attempts, 92 explorations, 12 formalizers, 367 peers, 356 reviews, 80 organizers) and published 330 records". 생산 세션은 406개인데 peer는 367개, review는 356개, record는 330개다. 차이(작업 없음, 진행 중, 거부, 교체된 세션)가 설명되지 않는다. review 거부율을 읽어낼 수 없다.
25. 57행 "a conditional log-concavity on the decreasing side of the sequence". 정의가 없다.
26. 57행 "differ by a relative margin of order k^(−1/3)". 왜 이 대목이 어려운지에 대한 함의를 비전공자는 알 수 없다.
27. 57행 "record r15df76b, 8 November, which used two independent arithmetics for the left half". 오른쪽 절반은 어떤 산술을 썼는지 언급이 없다.
28. 59행 "Fₗ(z) = Σₘ A(m, ℓ) zᵐ/m! ... the increment Fᵧ(1/e) − Fᵧ₋₁(1/e), scaled by y^(3/2)". 지표가 ℓ에서 y로 바뀐다. 같은 변수인지 다시 읽었다.
29. 61행 "material from a session outside the instance, relayed as unverified matter". 무슨 자료인지 불명이다.
30. 61행 "a manuscript based on the records". 누가 쓰는 원고인지(70행의 원고와 같은지) 불명이다.
31. 61행 대 63행. 12일 입력 둘이 버전 2 스냅숏(12일 02:38) 전인지 후인지 불명이다.
32. 63행 "contains the record above". "above"가 r5909c9e7을 가리킨다고 추정했다(직전 문단은 r0af7f414).
33. 65행 "at the time of writing, ten pipelines are active." pipeline이 정의되지 않는다(attempt→peer→review 한 줄로 추정).
34. 71행 "the Korean text has been through two verification rounds". verification round가 정의되지 않는다.
35. 108행 "an exploration requested at every attempt launch". 뜻이 불명이다. 매번 하나씩 띄운다는 것인지, 요청만 쌓는다는 것인지.
36. 49행 "a model-reviewed argument whose complete evidence is open for inspection" 대 73행 "the code, inputs and outputs behind the computer-assisted steps of the proofs will be distributed with the manuscript". 81행에 따르면 evidence/에 코드와 데이터가 있다. 계산 증거가 지금 완전히 공개되어 있는지 두 가지로 읽힌다.

## 4. overclaims

1. 5행: "long research needs two things at once that a single AI conversation cannot supply: continuity across days of work, and judgment independent of whoever did the work." 단일 대화가 이것을 "cannot" 제공한다는 근거나 비교가 없다.
2. 5행: "do-math takes continuity from the records and independence from the separation of roles." 독립성을 설계로 확보한다고 단정한다. 같은 모델 계열 사이의 상관이나, 대체 시 같은 모델이 될 가능성에 대한 측정이 없다.
3. 7행: "accepted by an independent review session". 독립성의 정도가 측정되지 않았다.
4. 17행: "so that no later attempt repeats work it cannot yet read". 효과로 서술했지만 중복 발생률이 측정되지 않았다(65행이 sections의 효과는 측정되지 않았다고 스스로 밝힌다).
5. 23행: "The peer is not a summarizer. It works the mathematics itself, may complete an argument the attempt left unfinished, may find the counterexample or the identity that the attempt passed over". 역할의 의도인지 관찰된 행동인지 구별되지 않는다. 빈도 근거가 없다.
6. 25행: "so that a result the attempt established does not disappear and a claim the candidate makes without support does not pass." review가 그렇게 한다고 단정한다. review의 누락률이나 오수용률이 측정되지 않았다.
7. 45행: "three independent checks by the review session". 한 세션이 수행하는 확인에 "independent"를 붙였다.
8. 49행: "whose complete evidence is open for inspection". 73행과 충돌할 수 있다(계산 증거 묶음은 미공개).
9. 143행: "a complete small instance settled with an independently reviewed Lean proof". 검증 문서에 기댄 주장이고 이 글 안에서는 확인할 수 없다. 예제가 94행의 n + 0 = n 수준인지도 불명이다.

(참고로 65행 "the run is evidence that they operate, not that they help"와 151행은 측정 범위를 스스로 제한한다. 이 둘은 과장이 아니라 제한 진술로 관찰했다.)

## 5. writing

### 처음 쓰이는 전문 용어가 그 문장이나 바로 앞 문장에서 정의되지 않음
- 3행 "any standing conditions" (120행에서야 예시)
- 3행 "records of mathematics" (record는 27행에서 정의)
- 7행 "the state do-math calls *informally proved*" (41행에서 "informally solved"로 정의)
- 7행 "the operator" (55행에서 정의)
- 7행 "a reviewed chain of records"
- 19행 "the role guides"
- 21행 "its retained work"
- 25행 "the producing roles"
- 29행 "how it stands to the root"
- 35행 "eligible exploration"
- 41행 "its supported scope"
- 47행 "a **comprehensive review**" (정의가 기능 서술뿐이고 촉발 조건 없음)
- 57행 "a conditional log-concavity"
- 65행 "ten pipelines"
- 71행 "two verification rounds"
- 87행 "live verification"

### 절 제목이나 문장이 내용 대신 계획을 예고함
- 9행 문단 전체: "A reader who wants to evaluate the system will find how the sessions cooperate under ..."
- 35행: "Three further roles complete the picture."
- 39행: "Three kinds of assurance appear in the records, and the frontier keeps them apart."
- 49행: "the files that let anyone inspect it are described in the next two sections."
- 61행: "The user intervened in the run in the following ways, and only these."
- 65행: "The limits of this result are the ones stated in the previous section, made concrete."

### 과장·비유·경구·최상급
- 7행, 57행 "chain" / 7행 "The last open link"
- 31행 "Questions are the business of the **explore** role."
- 31행 "in the regime where every estimate loses its margin"
- 35행 "complete the picture"
- 39행 "a *supported* conjecture is still a conjecture." (경구)
- 43행 "A finite verification proves the finite claim it covers and nothing beyond it." (경구)
- 53행 "Parking functions arise from a simple process."
- 65행 "the run is evidence that they operate, not that they help." (경구 형식)

### 독자의 내적 상태를 단정하는 문장
- 9행 "A reader who wants to evaluate the system ... A reader who wants to evaluate the mathematics ... A reader who wants to run do-math" (독자의 의도를 세 가지로 상정)
- 49행 "The assurance a reader should attach to the result is that of a model-reviewed argument"

### 닫힌 열거로 읽히는 분류
- 9행 독자 세 부류
- 33행 "something it closes, something it lets the research see that it could not see before, or a change in how the problem is approached" (진전의 정의를 셋으로 닫음)
- 39행 "Three kinds of assurance" (그런데 47행 concern이 넷째 층처럼 이어지고, 계산은 node 상태가 아니어서 층위가 섞임)
- 61행 "in the following ways, and only these" (55행, 59행에 목록 밖 개입이 있음)
- 57행 "four cases by where a descent and a later ascent could lie (across the center, inside the right half, crossing the halves, inside the left half)" (빠짐없는 분할인지 비전공자는 확인할 수 없음)

### 사족(작성 경위, 범위 밖 언급 등)
- 55행 "as in do-math's guides"
- 61행 "their contents are summarized here so that a reader of the published knowledge base knows what the sessions were told."
- 63행 "which always resolves to the latest version"
- 65행 "at the time of writing"
- 71행 "the Korean text has been through two verification rounds and its publication form is not yet decided"
- 72행 "its hosting is not yet decided"
- 155행 "None of these is needed to run do-math."
- 157행 "some others go through one university library's login."
- 160행 "It is unrelated to do-math."

### 같은 대상을 다른 낱말로 부름
- 사람: 3행 "The person who starts a run", 33행 "the person who runs the research", 55행 "the user", 35·87·97행 "you"
- 형식화 중지의 주체: 7행·69행 "the operator", 59행 "the user"
- 상태: 7행 "informally proved", 41행 "informally solved", 79행 "informally proved or refuted"; 7행·15행·45행 "settled", 41행 "solved", 57행 "proved"
- 관계: 15행 "connection", 15행·29행 "relation", 57행 "link", "premise"
- 기록 후보: 23행 "record candidate", 25행 "the candidate"
- 검증 역할: 25행 "review", 7행 "review session", 33행 "reviewers"
- 탐색 역할: 31행 "explore role", "explorer", 35행 "exploration"
- 공개물: 7행 "knowledge base", 57행 "the archive", 9행 "the published files", 63행 "`knowledge/` directory"
- 형식 결과: 45행 "Lean proof", 59행 "formal proof", "Lean result", 65행 "formal verification", 69행 "Lean formal solution"
- 지표 변수: 59행 ℓ와 y

### 명사 하나로 자리만 잡아 두고 다음 문장에서 지시어로 채움
- 21–23행: "its retained work goes on." → (새 문단) "It goes to a peer."
- 7행: "What remains is the formal part." → 다음 문장에서 내용을 채움
- 35행: "Three further roles complete the picture." → 이어지는 문장들이 채움
- 39행: "Three kinds of assurance appear in the records" → 다음 세 문단이 채움
- 61행: "in the following ways, and only these." → 같은 문단 뒤에서 채움

## 6. uncertainties

1. 55행 "a standing condition that it use no material from any earlier research on the problem"이 기존 문헌(Celano et al. 이후 연구)을 가리키는지, do-math의 이전 운전을 가리키는지 확정하지 못했다. 33행의 에세이가 "an earlier run"의 기록을 읽고 쓰였다는 점과 어떤 관계인지도 확정하지 못했다.
2. 형식화 중지를 결정한 주체(사람인가 operator인가)를 확정하지 못했다. 7·59·69행이 엇갈린다.
3. root의 informal 증명이 하나의 문서로 검토된 적이 있는지, 아니면 frontier가 링크별 승인만으로 기계적으로 유도한 것인지. 나는 후자로 읽었다(57행 "the frontier derived the root"). 사슬 전체에 대한 comprehensive review가 있었는지는 글에 없다.
4. binary64 단계의 "error model assumed in advance"가 엄밀한 상계인지 휴리스틱 가정인지 확정하지 못했다. 이에 따라 "informally proved"가 수학적 엄밀성을 어디까지 뜻하는지도 확정하지 못했다.
5. peer/review 모델 분리가 운전 전체에서 실제로 얼마나 지켜졌는지(6일 이전, 그리고 대체 시). 108행의 선호 순서로 보아 대체되면 같은 모델이 될 수 있다고 추론했지만 글은 이를 말하지 않는다.
6. 55행 집계의 차이(생산 406, peer 367, review 356, record 330)의 원인. review가 공개를 거부한 건수를 확정할 수 없다.
7. 운전 도중(6일 모델 배정, 10일 테스트) 구현이나 설정이 바뀌었는지.
8. 12일 입력 둘과 버전 2 스냅숏의 선후.
9. 외부 지식으로 메운 것: Lean의 표준 공리 셋(propext, Classical.choice, Quot.sound)과 sorryAx의 의미, Zenodo concept DOI의 의미, 단봉성·로그오목성의 일반 정의, "스티그머지"라는 분류(글에 없는 내 용어). "gpt-6.1-sol", "Fable 5.1"은 모르는 모델명이어서 글의 서술을 그대로 받아들였다.
10. 29행의 "formal work is sent only for outcomes that can reach the root" 규칙 아래에서 59행의 필요조건 node가 형식화된 경위. 반박이 root에 닿는다는 점 때문인지, 중지 전 규칙이 달랐기 때문인지 확정하지 못했다.
