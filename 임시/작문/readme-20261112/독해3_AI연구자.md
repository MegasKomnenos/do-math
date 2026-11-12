# 독해 보고 3: AI 연구자 독자

대상: C:\math\임시\작문\readme-20261112\README.md (206행)

## 1. status

complete. 1행부터 206행까지 전문을 읽었다. 다른 파일, 링크된 문서, arXiv, Zenodo는 열지 않았다.

## 2. understanding

### (a) 세션들이 어떻게 협력하고, 그 설계에는 어떤 성질이 있는가

글에 따르면 runner라는 프로그램이 기억을 공유하지 않는 새 CLI 대화(Claude Code 또는 Codex)를 차례로 띄운다. 세션들이 공유하는 것은 지식 기반 하나뿐이다. 지식 기반은 기록(record)으로 이루어지고, 기록 하나는 세 단계를 거쳐 만들어진다. 생산 세션(attempt, explorer, formalizer)이 수학을 만들면, peer가 그것을 남이 읽을 수 있는 기록 후보로 다듬고, review가 주장마다 supported, unsupported, undetermined를 매긴다. 이렇게 게시된 기록은 바뀌지 않는다. 나중의 판단은 finding으로 덧붙는다. 작업을 배정하는 중앙 계획자는 없다. 각 attempt가 frontier, index, board를 읽고 스스로 node와 section을 고른다. lease는 한 node 위에서 section을 고르는 순간에만 한 세션씩 들어가게 하는 잠금이다.

글은 이 조정이 "강제가 아니라 정보"로 이루어진다고 말한다. 도구가 거부하는 것은 프로그램이 스스로 판정할 수 있는 세 경우뿐이다. relation은 명제 논리가 허용하는 모든 방향으로 전파되고, 양쪽이 다 지지되는 node는 contested로 표시된다. 판단의 독립성은 역할을 나누고 모델 선호를 다르게 두어서 "추구된다(sought)"고 쓰여 있다.

내가 읽은 바는 이렇다. 독립성은 설계의 의도로만 서술되어 있고, 실제로 얼마나 확보되었는지는 측정되지 않았다. 첫 운전에서 6일 저녁까지 평가 역할과 생산 역할은 같은 모델을 썼다. fallback 때문에 같은 모델이 쓰인 빈도도 집계되지 않았다. review가 생산 세션의 원본(originals)을 받는다는 점도 독립성을 제한하는 요인으로 읽힌다. 정보 기반 조정이 중복 작업을 얼마나 막았는지도 수치가 없다.

- 5행: "Independence of judgment is sought through the separation of roles"
- 21행: "Coordination between sessions works through information rather than enforcement. ... the sessions are trusted to follow the guide."
- 3행: "Each new session reads the knowledge base and decides for itself what to work on. No session plans or assigns the others' work."
- 27행: "The configuration is an ordered list with fallbacks, so a launch made while the preferred model is unavailable can use the same model as the producers."
- 57행: "Until the evening of 6 November, peer and review preferred the same model as the producing roles"

### (b) 게시된 결과가 보증하는 것과 보증하지 않는 것

supported는 "review가 제시된 증거로 그 주장이 서술된 대로 성립한다고 판단했다"는 뜻이다. 추측을 서술한 주장도 서술로서는 supported일 수 있다. informally proved는 사람도 증명 검사기도 아닌 AI review 세션이 자연어 증명을 받아들였다는 뜻이다. relation으로 도출된 증명은 전제가 모두 Lean으로 증명되어 있어도 항상 informal이다.

계산은 두 종류로 구별된다. 하나는 반올림을 스스로 통제하는 산술(정수, 구간, 방향 반올림)이고, 다른 하나는 binary64에 오차 모형을 미리 가정한 산술이다. 첫 운전의 review는 뒤의 것도 컴퓨터 보조 증명으로 받아들였다. 가정된 오차 모형을 받아들이지 않는 독자에게는 그 결과가 미증명이라고 글이 직접 말한다.

formally proved에는 review가 직접 수행하는 세 검사가 필요하다. broker를 통한 재컴파일, 공리 목록 대조, 진술의 대상과 양화사 대조다. 첫 운전의 root는 informally proved 상태다. 사람의 검토는 없고, Lean 작업도 없다. 경로상의 한 단계(r030ffaeb)는 단조성 두 성질에 기대는데, 그 성질은 수치로만 확인되었고 증명되지 않았다. 그런데도 frontier의 root 상태는 바뀌지 않았다.

- 43행: "*Supported* means that the review found the offered evidence to establish the claim as stated"
- 45행: "\"Informal\" here means that the argument is written in ordinary mathematical language and was checked by an AI review session reading the candidate against the originals, not by a person and not by a proof checker."
- 47행: "a reader who does not accept an assumed error model should treat the results that depend on it as unproved."
- 61행: "Until a record proves them, the frontier's state of the root rests on this step as the reviews accepted it."
- 69행: "Every review was an AI session, and no person has reviewed the records."

### (c) 첫 운전에서 사람과 운영자가 개입한 범위, 측정된 것과 측정되지 않은 것

사용자는 이 저장소의 저자이고, 개입은 넓다. 다섯 날짜에 걸쳐 standing input이 들어갔다. 이전 인스턴스 자료 금지, 동치 node 점유 허용, section 등록 지시와 그 철회, 연구에 관한 에세이와 저자의 글쓰기 선호, formalization 중단, 대규모 계산보다 사고를 중시하라는 지시, "왜 unimodal인가"가 가장 알고 싶은 질문이라는 진술, 외부 세션 자료의 전달, 그리고 두 단조성 성질을 최우선으로 증명하라는 요청이다. 설정도 바뀌었다. 동시 세션 수는 4에서 16 사이를 오갔고, 모델 선호와 explorer 주기가 바뀌었다. 6일부터 9일 사이에는 소프트웨어 자체가 재생성되었다. relation의 전방위 전파, formalization 제한, 종료 재고(reconsideration), 질문(questions)이 이때 도입되었다. 운영자는 질문 다섯을 review 없이 frontier에 올렸다. 진행 중이던 formalization 다섯은 종료되었다. 경로상의 공백을 찾은 주체는 review 파이프라인이 아니라 저자와 운영자 세션이었다. Zenodo 예치는 손으로 했다.

측정된 것: 세션 수(역할별), 기록 수(출처별), 게시 커밋 수, node·relation·질문 수, section 등록 지시를 받은 세션 수(89), 테스트 316개 통과, Mathlib cold compile에 걸린 시간과 메모리.

측정되지 않은 것: 메커니즘(section, questions, reconsideration)이 연구 품질에 준 효과, 토큰 사용량과 비용, review가 주장을 기각하거나 정정한 빈도, fallback으로 평가 역할이 생산 역할과 같은 모델을 쓴 빈도. 글에는 없지만 내가 보기에 중복 작업률, reconsideration 뒤 세션이 계속 작업한 비율, 사람이 들인 시간도 수치가 없다.

- 65행: "The user and the operator intervened in the run in the following ways."
- 65행: "When the questions were introduced on 9 November, the operator placed five on the frontier without review."
- 61행: "The author and an operator session found the gap on 12 November while writing a manuscript from the records"
- 69행: "Whether the mechanisms described in the previous sections, such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured"
- 69행: "No figures were collected on token usage or cost, on how often reviews rejected or corrected claims, or on how often a fallback gave an assessing role the same model as the producers."
- 57행: "the runner had launched 1,227 sessions (305 attempts, 96 explorers, 12 formalizers, 371 peers, 362 reviews, 81 organizers) and published 337 records"

### (d) 설계 근거와 검증 보고를 더 읽을 수 있는 곳

- 설계와 결정 기록: docs/do-math/rebuild-design.md
- 설치 때 수행한 검사(두 CLI의 실제 실행, 작은 인스턴스의 형식 증명, runner 재시작 뒤 복구): docs/do-math/rebuild-verification.md
- 운영 세부: .claude/skills/do-math/SKILL.md, reference/operations.md, reference/lean.md
- 수학적 결과의 근거: Zenodo의 knowledge/ 디렉터리(버전 2 DOI 10.5281/zenodo.24142218). 확인 순서로 index.md, frontier.md, r5909c9e7의 review/feedback.md가 제시되어 있다.
- 런타임 테스트: .claude/skills/do-math/runtime/tests. 다만 이 테스트는 stand-in만 대상으로 한다.
- 원고, 해설, 영상, 계산 증거 묶음은 아직 공개되지 않았다(placeholder).

- 165행: "The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md), and the checks performed when it was installed ... are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md)."
- 67행: "To check the result, open `index.md`, go to `frontier.md` for the root's two routes and the records they cite, open record r5909c9e7 with its `review/feedback.md`, and continue into the records its proof uses."
- 173행: "These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce."
- 93행: "The [operator entry point](.claude/skills/do-math/SKILL.md) and the [operating guide](.claude/skills/do-math/reference/operations.md) explain the full path."

## 3. difficulties

- 3행: "supplies the proposition as an exact statement, together with any standing inputs, which are instructions that every session launched afterwards receives; the user does this through an AI conversation, called the operator, that prepares and operates the run on the user's behalf."
  한 문장에서 user, standing inputs, operator 세 용어를 동시에 정의한다. "afterwards"가 무엇의 뒤인지(입력 제출 뒤인지 운전 시작 뒤인지)는 140행에 가서야 분명해진다.
- 3행: "a repository of records, each holding mathematics that one session produced, a second session developed into an account for others, and a third session assessed, kept unchanged once published with the assessment beside it."
  관계절이 세 겹으로 겹치고, "kept unchanged"가 무엇을 수식하는지(record인지 repository인지) 다시 읽어야 했다.
- 7행: "every record and every relation on two routes from proved statements to the root"
  route와 relation이 여기서 처음 쓰인다. relation은 15행, route는 59행에서야 정의된다.
- 7행: "Several steps rest on computer-assisted inputs."
  어떤 종류의 계산인지는 47행과 59행을 읽어야 알 수 있다.
- 7행: "One necessary condition of the root does have a Lean proof."
  necessary condition은 31행에서 정의되고, 내용은 63행에서야 나온다.
- 15행: "If work settles a part of what a node asserts, the record can propose the parts as nodes together with the relation that the parts cover the whole."
  "a part"(단수)가 "the parts"(복수, 정관사)로 넘어간다. 해결된 부분과 나머지 부분을 모두 node로 제안한다는 뜻인지 분명하지 않다.
- 17행: "an **explorer** works to understand the problem"
  무엇을 산출하는지는 33행의 questions가 나오기 전까지 공백이다.
- 19행: "It stays occupied until the work has been developed into a record and reviewed"
  review가 게시를 거부하면 section이 풀리는지가 적혀 있지 않다.
- 23행: "asks the session to reconsider ending under its role guide, up to three times by default. The session either continues or submits an explicit decision"
  세 번을 다 써도 명시적 결정이 없을 때 어떻게 되는지 나와 있지 않다. "conversation ends"와 "the session"의 구별(대화가 끝나도 세션은 살아 있다)도 두 번 읽어야 했다.
- 27행: "which receives the candidate and the producing session's originals"
  "originals"가 정의되지 않았다. 25행의 retained work(대화 전체 포함)와 같은 것인지 알 수 없다. 독립성 판단에 중요한 대목이다.
- 31행: "on a sufficient path, when a chain of relations lets a proof of the node contribute to settling the root, or a necessary condition, when only its refutation can contribute"
  둘 다 아닌 node(root와 연결이 없는 node)를 어떻게 표시하는지 나와 있지 않다.
- 35행: "both are files in the skill's reference folder"
  "skill"이라는 낱말이 여기서 처음 쓰인다. 무엇을 가리키는지는 93행에서야 나온다.
- 37행: "groups published records into modules, each described the way a section of a survey would be"
  19행에서 기술 용어로 정의한 "section"을 일반 의미로 다시 쓴다.
- 51행: "A **concern** is a reported challenge to the support for a claim."
  누가 concern을 보고할 수 있는지(세션인지, 사용자인지, 운영자인지) 나와 있지 않다. 그래서 61행의 "no concern has been filed"가 무엇을 뜻하는지 판단하기 어렵다.
- 57행: "the frontier held 108 nodes, 119 accepted relations and 17 questions, of which 10 were resolved."
  "of which"가 질문 17개만 가리키는지 앞의 항목 전체를 가리키는지가 문법상 두 가지로 읽힌다.
- 57행: "published 337 records ... in 422 publication commits"
  337과 422의 차이가 무엇인지(organization, finding, question 게시로 추정) 설명되지 않는다.
- 57행: "the default described above, under which the assessing roles prefer a different model"
  "above"가 27행을 가리키는지 확인하려고 되돌아가야 했다. 112행의 기본 목록(생산 역할은 Codex 우선)과 첫 운전 7일 이후의 구성(생산 역할 Fable 5.1, 평가 역할 Opus 5.5)이 같은 "default"인지도 불분명하다.
- 59행: "Both routes therefore pass through the increase of the sequence below the middle"
  네 번째 경우("both below m")를 불가능하게 만드는 것과 "중앙 아래에서 수열이 증가함"의 관계가 설명되지 않았다. 조합론을 모르는 독자로서 "therefore"를 따라가지 못했다.
- 59행: "where n lies between 2ℓ and about 2ℓ^(3/2)"
  "about"이 경계를 흐리게 한다.
- 59행: "whose right-half part was computed in integer interval arithmetic and whose left-half part was computed twice"
  무엇의 오른쪽 절반과 왼쪽 절반인지(ℓ 범위로 추정) 정의되지 않았다.
- 61행: "while listing the properties among its remaining points of rigor"
  "points of rigor"는 정의 없이 쓰인 용어다.
- 61행: "do-math's review criteria allow a review to support a result while naming such a point"
  27행과 43행의 기준과 맞추어 보려고 여러 번 읽었다(5절 참조).
- 65행: "an instruction to register a section before beginning research on it, which was withdrawn on 9 November after 89 sessions had received it"
  19행은 section 등록을 이미 설계의 일부로 서술한다. 왜 별도 지시가 필요했고 왜 철회되었는지 알 수 없다.
- 65행: "material from a session outside the instance, relayed as unverified matter for the sessions' own judgment"
  어떤 자료였는지, 어떤 세션이 받았는지 나와 있지 않다.
- 65행: "the request above, at 14:15"
  61행에서 standing input이라고 부른 것을 여기서는 "request"라고 부른다.
- 69행: "working on unresolved nodes and unresolved questions beside the root"
  "beside the root"는 "root 말고"로 읽히지만, root에 대한 작업도 포함하는지가 모호하다.
- 150행: "after attempts have reported that every unresolved node is occupied, a report that otherwise pauses attempt launches"
  attempt 발사를 멈추게 하는 이 메커니즘은 본문 설계 절에 나오지 않고 표에서 처음 등장한다.
- 165행: "a complete small instance whose root was formally proved with an independently reviewed Lean proof"
  "independently"가 무엇으로부터의 독립인지(AI review인지 사람인지) 정의되지 않았다.

## 4. overclaims

- 59행: "Each case was shown impossible." / "that was the last part to close." / "With that node proved, the frontier derived the root through the relations."
  단정형으로 서술된다. 그러나 61행은 바로 그 부분, 곧 중앙 아래의 증가가 기대는 단계에 미증명 공백이 있다고 밝힌다. "shown", "close"는 frontier 상태의 뜻(AI review가 받아들임)으로 한정되지 않은 채 읽힌다.
- 69행: "the run is evidence that they functioned at this scale"
  "functioned"가 무엇을 뜻하는지 정해져 있지 않고, 그것을 뒷받침하는 지표(예: 중복 등록 거부 횟수, contested 처리 횟수)도 제시되지 않았다. 효과를 부정하는 문장 안에 있어 약하게 표현되었지만, 작동했다는 주장 자체는 측정 근거 없이 서 있다.
- 165행: "an independently reviewed Lean proof"
  독립성의 근거나 정의가 없는 수식어다.
- 경계 사례(설계 근거로 볼 수 있어 포함 여부를 알린다) 5행: "The system is built this way because research that runs for days needs both continuity and judgment that does not come from whoever did the work."
  필요성을 단정하지만 설계 의도의 서술로도 읽힌다.

## 5. inconsistencies

- 23행 "In every case the retained work goes on to the processing roles."와 57행 "a producing session that ends without having begun research gets no peer"
  "모든 경우"라는 23행의 진술을 57행이 제한한다.
- 27행 "if accepting a claim would require an essential proof that the candidate does not contain, it is asked to report the gap rather than to write the proof and certify its own work."와 43행 "*Supported* means that the review found the offered evidence to establish the claim as stated", 그리고 61행 "its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among its remaining points of rigor; do-math's review criteria allow a review to support a result while naming such a point"
  수치 표본 확인만 된 두 성질에 기대는 결과가 supported, accepted가 되었다. 이것은 "증거가 주장을 확립한다"는 정의와도, "필수 증명이 없으면 공백을 보고하라"는 지시와도 맞지 않아 보인다.
- 7행 "On 11 November the root proposition reached the state do-math calls *informally proved*: every record and every relation on two routes ... had been accepted"와 61행 "One step of those routes is known to be unproved"
  root 상태에 대한 서술은 모순이 아니다. frontier 상태를 말한 것이기 때문이다. 다만 59행 "With that node proved, the frontier derived the root"까지 함께 읽으면 "proved"라는 낱말이 frontier 상태와 실제 증명 여부 두 뜻으로 섞여 쓰인다.
- 91행 "their model providers receive the material they read, as in ordinary CLI use"와 같은 문단의 91행 "Nothing is uploaded anywhere: publication means a commit to the instance's local Git repository"
  앞 문장은 모델 제공자에게 자료가 간다고 하고, 뒤 문장은 "어디에도 올라가지 않는다"고 단정한다. 콜론 뒤에서 게시(publication)로 범위가 좁혀지지만, 첫 마디는 앞 문장과 충돌한다.
- 31행 "Formalization is requested only for outcomes that can reach the root in this sense."와 65행 "the restriction of formalization to the root's routes"
  같은 규칙을 두 자리에서 다르게 부른다. 31행의 기준으로는 necessary condition의 반증도 대상이 되지만, 65행의 "routes"(59행 정의: proof를 root로 잇는 사슬)는 그것을 포함하지 않는다.
- 49행 "compares them with the allowed list, by default `propext`, `Classical.choice` and `Quot.sound`"와 128행 "The allowed Lean axioms are `propext`, `Classical.choice` and `Quot.sound`."
  앞은 기본값(설정 가능)이라 하고, 뒤는 고정된 것처럼 말한다.
- 3행 "No session plans or assigns the others' work."와 19행 "the user's standing inputs can state priorities, but the choice of work stays with the session"을 61행 "a standing input asked sessions launched afterwards to put proving the two properties before any other work"와 함께 읽을 때
  문자 그대로는 모순이 아니다. 배정한 주체가 세션이 아니라 사용자이기 때문이다. 그러나 "다른 모든 작업보다 먼저"라는 지시가 "선택은 세션에 남는다"와 실질적으로 양립하는지에는 긴장이 있다.
- 57행 "a standing input that it use no records or code from an earlier instance"(65행 "no material from the earlier instance")와 35행 "an essay ... which this repository's author and an operator session wrote after reading the records of an earlier instance", 65행 "8 November (the essay on research ...)"
  이전 인스턴스의 기록을 읽고 쓴 문서가 8일부터 세션에 전달되었다. 글은 "it draws its examples from the history of mathematics, not from that instance"라고 해명한다. 그래도 "no material" 입력과의 경계가 글 안에서 정리되어 있지 않다.
- 17행·23행 "processing roles"(peer와 review)와 57행·69행 "assessing roles"
  57행에서 "assessing roles"는 peer와 review를 함께 가리킨다. 그러나 25행에 따르면 peer는 평가하지 않고 다듬는다. 같은 대상을 다른 낱말로 부르고, 그 낱말이 한 구성원의 역할과 맞지 않는다.
- 7행 "the user paused formalization on 9 November ... and no Lean work exists for the routes to the root"와 63행 "the five formalizations then in progress were ended"
  9일에 진행 중이던 formalization 다섯이 route 위 node를 다루고 있었다면 "Lean work가 없다"는 말과 어긋난다. 그것들이 무엇을 다뤘는지 적혀 있지 않아 확정할 수 없다. 6절의 불확실 항목과 겹친다.

## 6. writing

처음 쓰이는 전문 용어가 그 문장이나 바로 앞 문장에서 정의되지 않은 자리:
- 7행: "two routes from proved statements to the root" (route는 59행에서 정의)
- 7행: "every relation" (relation은 15행에서 정의)
- 7행: "One necessary condition of the root" (31행에서 정의)
- 7행: "computer-assisted inputs"
- 27행: "the producing session's originals" (정의 없음)
- 35행: "the skill's reference folder" (skill은 93행에서 처음 설명)
- 59행: "right-half part", "left-half part"
- 61행: "points of rigor"
- 150행: "a report that otherwise pauses attempt launches" (본문에서 정의된 적 없는 메커니즘)
- 전편: "Lean"은 정의되지 않는다(이 독자는 알지만 기록해 둔다).

문장이 내용 대신 계획을 예고하는 자리:
- 9행: "The sections below describe how the sessions cooperate, what a published result does and does not certify, the first run with its evidence and its limits, the layout of a published knowledge base, and how to run do-math on a proposition of your own."
- 65행: "The user and the operator intervened in the run in the following ways."
- 69행: "The result has the following limits."
- 71행: "Several artifacts of the run are being prepared and are not yet public."

과장, 비유, 경구, 최상급:
- 21행: "Coordination between sessions works through information rather than enforcement." (경구형 문장)
- 33행: "what an object looks like where every estimate loses its margin" (비유적)
- 59행: "In the part of it that resisted longest" (의인화, 최상급)
- 59행: "that was the last part to close" (최상급. 61행의 공백 때문에 사실 서술로도 문제가 있다)

독자의 내적 상태를 단정하는 문장: 찾지 못했다. 47행 "a reader who does not accept an assumed error model should treat ..."는 조건부라서 해당하지 않는다고 보았다.

닫힌 열거로 읽히는 분류:
- 21행: "Tools refuse only what a program can decide by itself: registering a statement identical ..., registering a whole node while ..., or omitting the reason ..." ("only"로 닫힌다)
- 31행: "on a sufficient path, ... or a necessary condition" (어느 쪽도 아닌 node가 빠진다)
- 57행: "The session counts differ from the record count because a producing session that ends without having begun research gets no peer, interrupted peers and reviews are replaced by fresh sessions, some candidates are not published, and some pipelines ... were still in progress." (네 원인이 전부인 것처럼 읽힌다)
- 17행: "Six roles do the work"와 51행의 comprehensive review. comprehensive review가 여섯 역할 중 어디에 속하는지 분류에서 빠져 있다.

사족:
- 128행: "The allowed Lean axioms are `propext`, `Classical.choice` and `Quot.sound`." (49행의 반복이고 표현도 다르다)
- 7행 문단 전체가 59~63행과 69행의 내용을 미리 요약한다. 요약이라는 기능은 있으나, 61행·63행·69행에서 같은 사실(사람의 검토 없음, Lean 작업 없음, 단조성 공백)이 세 번씩 되풀이된다.
- 182행: "[services/jev-cli](services/jev-cli/README.md): a command-line client for Jev, a hosted model from TypeSafe." 이 독자의 목적과 무관하다.

같은 대상을 다른 낱말로 부르는 자리:
- user와 author: 57행 "The user of this run is the author of this repository."라고 같게 둔 뒤, 61행 "The author and an operator session found the gap"과 63행 "the user paused all formalization"처럼 섞어 쓴다.
- processing roles(17행, 23행)와 assessing roles(57행, 69행)
- standing input(61행)과 request(65행 "the request above, at 14:15")
- "outcomes that can reach the root"(31행, 63행)와 "the root's routes"(65행)
- computer-assisted inputs(7행), computer-assisted steps(77행), computer-assisted proof(47행, 61행)
- 받아들임을 가리키는 supported(주장 단위)와 accepted(증명, 기록 단위)가 59행 "Its review supported the proof's claims, accepted the proof"처럼 섞여 쓰인다. 구별이 의도인지 분명하지 않다.
- 기술 용어 section(19행)과 일반어 section(37행 "a section of a survey", 9행 "The sections below")

명사 하나로 자리만 잡아 두고 다음 문장에서 지시어로 채우는 자리:
- 7행: "One necessary condition of the root does have a Lean proof." (내용은 63행에서야 나온다)
- 59행: "The frontier shows two, established by records rce3dc75b and r15524fdd." (뒤에서 "The first route", "The second route"로 채운다)
- 61행: "One step of those routes is known to be unproved." (다음 문장의 "Record r030ffaeb ..."로 채운다)
- 63행: "One node has a formal proof." (다음 문장의 "Record r0af7f414 ..."로 채운다)

## 7. uncertainties

- 27행·57행·112행의 "different model"이 공급자가 같은 다른 모델(첫 운전 7일 이후 Claude Fable 5.1과 Claude Opus 5.5)도 포함하는지 확정하지 못했다. 글자 그대로는 포함한다고 읽었다. 그렇다면 7일 이후 첫 운전의 생산 역할과 평가 역할은 같은 공급자였고, 독립성 논의에서 이 점은 다뤄지지 않았다.
- 27행 "originals"를 25행의 retained work(전체 대화 포함)와 같은 것으로 추정했다. 확정할 수 없다.
- 59행에서 "중앙 아래의 증가"를 네 번째 경우를 닫는 더 강한 진술로, 그리고 두 번째 경로의 "below m" 조건이 거기서 공허하게 성립하는 것으로 해석했다. 조합론 지식으로 메운 추론이고, 글은 이를 설명하지 않는다.
- 59행의 right-half와 left-half를 ℓ 범위의 절반으로 추정했다.
- 57행 "of which 10 were resolved"를 질문 17개 중 10개로 읽었다.
- 337개 기록과 422개 게시 커밋의 차이는 organization, finding, question 게시라고 추정했다(85행의 events, organizations, questions, reviews 목록에 기댐).
- 61행에서 사용자가 공백을 알고도 concern을 내지 않은 이유와, 사용자가 concern을 낼 수 있는 주체인지는 글만으로 알 수 없다. 51행은 사용자가 comprehensive review를 명령으로 요청할 수 있다고 하는데, 그것도 하지 않은 것으로 읽힌다.
- 65행 12일 04:54의 외부 세션 자료는 r5909c9e7(11일 16:14 게시)보다 늦으므로 root의 informally proved 도달에는 영향을 주지 않았다고 날짜로 추론했다. 자료의 내용과 출처는 알 수 없다.
- 9일에 종료된 formalization 다섯이 무엇을 대상으로 했는지, 그 retained work가 peer와 review로 넘어갔는지(156행 "its retained work is still processed"에 비추어) 알 수 없다. 기록 7개가 모두 6일 게시분이므로 결과물은 게시되지 않은 것으로 읽었다.
- 65행 "an instruction to register a section before beginning research on it"이 19행의 설계와 어떻게 다른지, 예컨대 당시 구현에서는 등록이 선택 사항이었는지 확정하지 못했다.
- 165행 "independently reviewed"가 별도의 AI review 세션을 뜻하는지 사람을 뜻하는지 확정하지 못했다. 앞뒤 맥락으로 보아 AI review로 추정한다.
- 49행·128행의 Lean 공리 목록이 표준 Lean 4/Mathlib 공리라는 점, 55행의 (n+1)ⁿ⁻¹ 같은 parking function의 성질, binary64 반올림의 의미는 외부 지식으로 확인했다. Celano et al. 논문과 Conjecture 6.5의 실재, Zenodo DOI, 모델 이름(gpt-6.1-sol, Fable 5.1, Opus 5.5)은 확인하지 않았다(지시에 따라 링크를 열지 않음).
