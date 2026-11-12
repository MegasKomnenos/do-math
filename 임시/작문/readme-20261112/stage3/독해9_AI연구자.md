# 독해 9: 영어로 읽는 AI 시스템 연구자

읽은 순서: `README.md` → `docs/do-math/first-run-parking-unimodality.md` → `docs/do-math/running.md` → `zenodo-description.md`의 "## Description" 절. 아래에서 문서 이름은 각각 README, 첫 운전 문서, 운전 안내, Zenodo 설명문으로 줄여 부른다. 나는 이 저장소를 처음 열었고, do-math의 내부 용어는 몰랐으며, 문서를 쓴 대화나 의도는 모른다. 인용은 모두 영어 원문 그대로다.

---

## 1. 이해한 것

### 1.1 이 시스템이 무엇을 하는가

do-math는 하나의 수학 명제를 증명하거나 반증하기 위해 다수의 AI 세션을 돌리는 시스템이다. 세션은 서로 대화하지 않고, 파일만 넘긴다. 핵심 설계는 "만드는 세션, 써 주는 세션, 평가하는 세션이 서로 다른 대화"라는 세 단계 분리다.

> "A system for autonomous mathematical research in which many AI sessions work together to prove or refute a single mathematical statement. The session that produces a piece of mathematics, the session that writes it up for others and the session that assesses it are three different conversations, and every result is published together with its assessment." (README)

> "The sessions have no contact with one another. Each is a new Claude Code or Codex conversation that knows nothing of the others; what a session produces is handed on as files, and what survives review is published as a record in a shared knowledge base for every later session to read." (README)

다른 다중 에이전트 연구 시스템과의 차이로 내가 읽어낸 것은 세 가지다.

(a) 중앙 조정자가 일을 배분하지 않는다. attempt 세션은 지식 베이스를 읽고 스스로 작업할 노드를 고른다. 유일한 예외는 형식화다.

> "No session assigns work to another. A session in the first stage reads the knowledge base and decides for itself what to work on; the one exception is formalization, which the runner requests once a review has accepted an informal proof." (README)

(b) 조정은 강제가 아니라 정보로 이루어진다. 점유 현황(board)을 보여 주고 역할 안내서가 존중하라고 말하며, 프로그램은 기계적으로 판정 가능한 것만 거부한다.

> "Sessions coordinate through information rather than enforcement. The board shows which sections are occupied; the guide that each role receives, called its **role guide**, explains how to respect that; and the sessions are trusted to follow the guide." (README)

(c) 기록은 불변이며, 평가가 붙어 공개되고, 뒤의 판정은 덧붙는다. 완벽하지 않은 일도 평가와 함께 공개된다.

> "If the review judges the work worth keeping, the record is published with that assessment attached, and it is never edited afterwards. If a later review session finds a mistake in it or confirms one of its results, it appends a finding to the record, so that the original claim and what later became of it remain visible together." (README)

> "Useful work that is not yet perfect is still published, together with its assessment, so that a later session can tell an established result from a claim that still needs more." (README)

설계 동기는 연속성(세션 간 기억 없음 → 기록이 기억)과 독립 판단(자기 일을 자기가 인증하지 않음)이다.

> "A run can last for days and pass through hundreds of conversations, none of which remembers the one before, so the records are the research's memory from one session to the next" (README)

### 1.2 구조와 용어

- **instance**: 한 번의 운전. 자체 Git 저장소를 가진 디렉터리. `root.md`(명제), `settings.json`(모델·스케줄), 세션별 디렉터리, `knowledge/`(지식 베이스).
- **root**: 인스턴스가 풀려는 명제. 운전 중에 바뀌지 않는다.
- **node**: 정확히 적힌 수학 명제. root가 첫 노드이고, 그 뒤의 노드는 **relation**(검토된 함의)을 통해서만 들어온다.
- **section**: 노드가 주장하는 바의 정확한 일부(전체일 수도 있음). attempt는 노드와 section을 골라 등록한다.
- **lease**: 한 노드에서 section을 고르는 동안 한 세션만 고르게 하는 잠금. 시간 제한 없음.
- 여섯 역할: 생산 셋(**attempt**, **explorer**, **formalizer**), 처리 둘(**peer**, **review**), 정리 하나(**organizer**). 생산 세션 + peer + review = **pipeline**.
- **retained work**: 생산 세션이 자기 디렉터리에 남긴 모든 파일.
- **record**: review가 공개할 가치가 있다고 판단한 peer의 초안이 평가와 함께 Git에 커밋된 것.
- **frontier / index / board / glossary**: 저장소에서 렌더링되는 네 가지 뷰. 노드와 관계·상태, 기록 목록, 점유 현황, 공유 어휘.
- **question**: 정리 명제로 잡히지 않는 이해 목표. explorer가 하나를 맡는다.
- **concern / finding / comprehensive review**: 리뷰가 제기하는 이의, 기록에 덧붙는 판정, 공개된 증거를 재검토하는 리뷰.

> "A node is on a **route** to the root when a chain of relations lets a proof of the node contribute to settling the root, and such a chain is itself called a route; a node is a necessary condition of the root when only its refutation can contribute." (README)

### 1.3 "증명됨"이 뜻하는 것

두 단계가 있다. **informally proved**는 AI 리뷰 세션이 사람 읽을 수 있는 증명을 받아들였거나, runner가 수용된 관계를 통해 파생한 것이다. 사람도 증명 검사기도 보지 않았다. 컴퓨터 보조 단계가 있으면 비형식에 머문다. **formally proved**는 Lean 증명을 리뷰 세션이 broker로 재컴파일하고, 공리 목록을 확인하고, 명제를 노드와 대상·한정사 단위로 대조한 뒤에만 성립한다.

> "'Informal' here means that the argument is written in ordinary mathematical language, with any computer-assisted steps stated as such, and that it was checked by an AI review session reading the candidate against the producer's retained work, not by a person and not by a proof checker." (README)

> "A node is **formally proved** only after a Lean proof has passed three checks that the review session carries out itself." (README)

컴퓨터 보조 단계 중에서도 두 종류를 구분한다. 보장 구간이 나오는 산술(정수·구간·방향 반올림)과, binary64 부동소수점에 오차 모형을 미리 가정하는 산술. 후자에 의존한 결과는 그 모형을 받아들이지 않으면 미증명으로 보라고 한다.

> "In the second kind, binary64 floating point with an error model assumed in advance, margins added to the results are trusted to cover the rounding error rather than tracked by the arithmetic." (README)

### 1.4 첫 운전의 결과와 상태

문제: 길이 n인 주차함수의 최대 변위 분포 b(n, 0), …, b(n, n−1)이 모든 n에 대해 단봉(unimodal)이라는 Celano 외(arXiv:2507.07243) 추측 6.5. 2026년 11월 5일 시작, 11월 11일 16:14 KST에 "informally proved" 도달. 두 경로(네 경우 분할 / 조건부 로그오목성)가 있고, 둘 다 "중간 아래에서는 감소하지 않는다"는 명제를 지나며, 그것을 닫은 기록 r5909c9e7은 binary64 계산과 n ≤ 20000 검증에 의존한다. Lean 증명은 없다. 필요조건 하나만 Lean 증명이 있다.

> "On 11 November the conjecture reached the state that do-math calls *informally proved*. This is a technical term of the system, and it means less than the words might suggest: along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session." (README)

> "Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to close. The record that closed it, r5909c9e7, inherits computer-assisted inputs from earlier records" (README)

규모(12일 17:45): 세션 1,227(attempt 305, explorer 96, formalizer 12, peer 371, review 362, organizer 81), 기록 337, 노드 108, 관계 119, 질문 17(10 해결). 12일 23:15에는 세션 1,237, 기록 340.

성과 측정은 없다고 명시한다.

> "Whether do-math's mechanisms changed the quality of the research has not been measured, and no figures were collected on cost or on how often reviews rejected or corrected claims." (README)

### 1.5 사람과 운영자가 어디까지 개입했는가

내가 읽어낸 개입의 층은 넷이다.

(a) **사용자(= 저장소 저자)**: 명제를 쓰고, standing input(이후 세션 모두에게 전달되는 지시문)을 넣고, 설정을 바꾸고, 형식화를 멈췄다. 손으로 세션을 띄우지는 않는다.

> "The user supplies the statement to be proved or refuted, written out exactly, and may add standing inputs, which are instructions that reach every session launched after them. The user does not launch sessions by hand." (README)

> "The user of this run is the author of this repository." (첫 운전 문서)

(b) **운영자(operator)**: 사용자를 대신해 인스턴스를 세팅하고 운전을 조작하는 AI 대화. 질문을 리뷰 없이 frontier에 올릴 수 있다.

> "An AI conversation called the operator sets up the instance from the user's statement and settings and operates the run on the user's behalf" (README)

> "9 November | Operator action | Five questions placed on the frontier without review, when questions were introduced" (첫 운전 문서)

(c) **운전 중 소프트웨어 변경**: 6~9일 사이 관계 전파, 형식화 제한, 종료 재고, 질문 기능이 운전 중에 추가됐다. 즉 README가 설계로 설명하는 기능 여럿이 첫 운전 도중에 들어왔다.

> "6 November | Software | Propagation of relations in every logical direction; formalization limited to outcomes that can reach the root; reconsideration of session endings" (첫 운전 문서)

> "The software changed several times between 6 and 9 November: the installed copy that the instance executes was regenerated and the runner restarted, while sessions already running kept the code and guides they had been launched with." (첫 운전 문서)

(d) **내용에 닿는 개입**: 이전 인스턴스 자료 사용 금지, 연구 에세이·작문 선호 문서 주입, "큰 계산보다 사고에 비중", "왜 단봉인가가 사용자가 가장 원하는 질문", 외부 세션의 자료 전달, 그리고 특정 표의 단조성 둘을 "다른 어떤 일보다 먼저" 증명하라는 지시.

> "12 November, 14:15 | Standing input | Prove the two monotonicity properties that the table used by record r030ffaeb depends on, before any other work; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove them" (첫 운전 문서)

사람이 수학 자체를 검토하지는 않았다는 점은 네 문서가 모두 반복한다.

> "Every judgment in this archive was made by an AI session, and no person has refereed its records." (Zenodo 설명문)

### 1.6 직접 돌리려면

- Python 3.12+, Git, 표준 라이브러리만. Codex CLI 또는 Claude Code CLI(로그인된 상태). API 직접 호출 없음, 과금은 CLI 설정대로.
- Lean 4는 항상 필요(설정이 Lean 설치를 지명하고 broker가 runner와 함께 뜨기 때문). Mathlib은 필요한 문제일 때.
- Windows에서 개발·검증. Linux는 미검증, macOS 미지원.
- 세션은 권한 프롬프트 없이, 샌드박스 없이, 내 계정으로 파일·명령을 실행한다. 시간·세션 수·사용량 상한 없음.

> "Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox" (운전 안내)

- 시작은 두 길: 저장소에서 Claude Code/Codex를 띄우고 do-math 스킬에 시작을 부탁하거나(그 대화가 operator), 손으로 `root.md`와 `settings.json`을 쓰고 `runner.py init` → `start` → `status`.
- 기본값: 동시 8세션, attempt/explorer 간격 180초, attempt 하나당 explorer 요청 하나, 연구 공개 4건마다 organizer, 종료 재고 최대 3회. 모델 기본은 Codex 우선·Claude 차선, peer/review만 반대.
- standing input은 `input --file`로 넣고, 철회는 파일을 `control/inputs`에서 옮기는 것(명령 없음). root 변경은 새 인스턴스.
- 종료는 `stop` → `kill-session` 각각 → runner 프로세스 종료.

> "Standing inputs, such as the language of the records or limits on methods, are plain text files submitted with `input --file <file>`, before `start` when they should reach every session. They apply only to sessions launched after them and accumulate" (운전 안내)

---

## 2. 읽기 어려웠던 자리

총 44항목. 번호 순은 읽은 순서이며, 무게 순이 아니다.

### README

**R1.** 한눈 보기 표의 셋째 행 제목 `State of the root`. "root"가 무엇인지 모른 채 첫 화면에서 만났다. 정의는 한참 뒤("The statement in `root.md` is called the **root** of the instance.")에 나온다. 표 제목에서 멈춰 나중에 되돌아왔다.

**R2.** > "An AI conversation called the operator sets up the instance from the user's statement and settings and operates the run on the user's behalf, and a program called the runner then launches sessions as the work requires, several at a time, for as long as the research goes on."
"instance"가 정의 전에 나온다. 또 한 문장에 "and ... and ... and"로 세 절이 이어져 어디서 끊어 읽을지 두 번 되짚었다.

**R3.** > "decides what the record should propose for the frontier, such as new statements to pursue."
"frontier"가 처음 등장하는 자리인데 정의가 없다. 뒤의 "The choice of work" 절에서야 정의된다.

**R4.** > "Useful work that is not yet perfect is still published, together with its assessment, so that a later session can tell an established result from a claim that still needs more."
"needs more"가 목적어 없이 끝난다. more evidence? more work? 뜻은 짐작되지만 영어 문장으로 매달린 느낌이다.

**R5.** > "along two chains of implications leading from statements already proved to the conjecture itself, every record and every implication had been accepted by an AI review session."
"statements already proved"에서 멈췄다. 이 시스템에서 "proved"가 곧 AI 리뷰 수용이라면 "already proved"는 무엇이 다른가? 같은 과정으로 먼저 증명된 노드라는 뜻으로 읽었지만, 정의가 순환하는 것처럼 보였다.

**R6.** > "do-math considers a run complete only when a Lean proof of the statement, or of its negation, has been recompiled by a review session and matched against the exact statement, and the user paused formalization on 9 November so that the research could finish first."
가장 크게 멈춘 자리다. 운전이 완료되려면 Lean 증명이 필요하다고 바로 앞에서 말해 놓고, "research could finish first"라며 형식화를 멈췄다고 한다. 시스템 정의상 연구는 형식화 없이 끝날 수 없는데, 무엇이 "finish"하는가? 비형식 증명 도달을 뜻한다고 추측했지만 문장 자체는 모순으로 읽힌다. 첫 운전 문서와 Zenodo 설명문에서도 같은 표현이 반복된다.

**R7.** > "The lease has no time limit; it ends when the session registers its section, releases the lease, or ends."
한 문장 안에서 "ends ... or ends". 주어가 다르다(lease / session)는 것을 두 번 읽고 알았다.

**R8.** > "An attempt has no time cap, and the runner does not close it the moment its CLI process exits. A separate process called the **session host**, started with the session and alive for as long as the session is, resumes the same conversation and asks the session, under its role guide, to reconsider whether to end, up to three times by default."
CLI 프로세스가 종료됐는데 "세션"은 살아 있고, session host는 "세션이 살아 있는 동안" 살아 있다. 여기서 session = CLI process가 아니라 session = 재개 가능한 대화라는 것을 추론해야 했다. 문서 전체에서 "session"이 프로세스·대화·디렉터리 셋 중 무엇인지 매번 가려 읽어야 했고, 이 문단이 그 혼란을 드러낸다.

**R9.** > "a session that only checked for available work and found none ends without them."
"them"이 가리키는 "a peer and a review"가 앞 문장 중간에 있어 되돌아가 찾았다.

**R10.** > "A **peer** is a new session that receives the producing session's complete retained work, including the full conversation"
앞에서 retained work를 "the files it keeps in its own directory while it works"로 정의하고 정의·논증·계산·문헌·실패 접근·남은 단계를 열거했는데, 대화 전체는 그 목록에 없었다. 여기서 갑자기 포함된다. 정의가 확장된 것인지 처음부터 포함이었는지 알 수 없다.

**R11.** > "A node is on a **route** to the root when a chain of relations lets a proof of the node contribute to settling the root, and such a chain is itself called a route"
"route"가 노드의 성질과 사슬 자체 두 가지로 쓰인다고 문장이 스스로 말한다. 이후 "two routes to the root"가 나올 때마다 어느 뜻인지 잠깐 멈춘다. 또 "a node is a necessary condition of the root when only its refutation can contribute"는 논리적 정의(root → node)가 아니라 조작적 정의여서 수학적 의미와 맞춰 보느라 되돌아갔다.

**R12.** > "This repository's author and an operator session wrote it after reading the records of an earlier instance that had worked on the same problem under a previous implementation"
이 절은 일반 설계 설명인데 "the same problem"이 나온다. 어느 문제와 같은가? 첫 운전의 주차함수 문제를 가리킨다고 추측했지만 이 절 안에는 선행사가 없다. 또 이 문장으로 "earlier instance"의 존재를 처음 알았다.

**R13.** > "The other describes the writing the author prefers, with the occasions on which those preferences became clear."
"with the occasions on which ..." 구문이 영어로 어색하다. 선호가 "분명해진 계기"를 함께 적었다는 뜻으로 읽었지만 두 번 읽었다.

**R14.** > "Besides their role guides, attempt, explorer, peer, review and organizer sessions receive two documents"
여섯 역할 중 formalizer만 빠져 있는데 이유가 없다. 의도인지 누락인지 알 수 없다.

**R15.** > "If a later review session, whether reviewing another candidate or examining published evidence, finds a defect in it or confirms a result, it appends a **finding** to the record"
와
> "until a **comprehensive review** issues a finding that withdraws or reaffirms the claim."
앞 문장은 어떤 리뷰 세션이든 finding을 덧붙일 수 있다고 하고, 뒤 문장은 철회·재확인은 comprehensive review의 finding이 한다고 한다. 일반 리뷰의 finding은 claim의 standing을 바꾸는가? 두 문장 사이의 관계를 찾지 못했다.

**R16.** > "Work may close something, let the research see something it could not see before, or change how the problem is approached"
"close something"이 무엇을 닫는다는 것인지 모호하다. 이 문서 전체에서 "close"가 "증명하여 마무리하다"의 뜻으로 쓰이는데(아래 R20 참조) 정의가 없다.

**R17.** > "The second route shows that a conditional log-concavity suffices: log-concavity required only at steps where the sequence has already started to decrease"
"a conditional log-concavity"는 표준 용어가 아니고 관사 "a"가 붙어 셀 수 있는 명사처럼 쓰여 어색했다. 콜론 뒤 설명으로 겨우 뜻을 잡았다.

**R18.** > "Both routes pass through one statement, that the sequence never decreases below the middle, and this statement was the last part to close. The record that closed it, r5909c9e7, inherits computer-assisted inputs from earlier records"
"close"가 자동사·타동사로 연이어 쓰이고, "inherits ... inputs"라는 동사–명사 짝이 영어로 낯설다. "depends on computer-assisted inputs from earlier records"로 읽어야 했다.

**R19.** > "a certification that the root holds for all n ≤ 20000, carried out in interval arithmetic with integer endpoints and, for the steps below the middle, also in floating point with directed rounding."
"certification"이 무엇을 뜻하는지(유한 검증 계산이라는 것) 뒤 "What counts as established"의 "A finite verification proves the finite claim it covers"와 맞춰 보고서야 알았다. 또 root 자체가 n ≤ 20000에서 확인된 것이라면 그 범위에서는 증명이 끝난 것인데, 그것이 "input"이 되는 구조를 이해하는 데 시간이 걸렸다.

**R20.** > "It needs Lean 4 in every case, and Mathlib when the proofs will draw on it."
왜 모든 경우에 Lean이 필요한지 README에는 이유가 없다. 운전 안내에 가서야 "because the settings name a Lean installation and the broker starts with the runner"를 읽었다. README만 읽는 독자는 의아하게 남는다.

**R21.** > "Then, from Claude Code or Codex started in the repository, ask the do-math skill to start research on a statement."
"skill"이 Claude Code의 기능 단위라는 것은 외부 지식으로 메웠다. 문서 안에는 정의가 없다.

**R22.** > "Its entry point is `index.md`, which lists the records that the organizer selected as shared context for new sessions, a directory of modules with their descriptions, and the recent records not yet organized."
"a directory of modules"가 파일 시스템 디렉터리인지 목록(directory = listing)인지 두 가지로 읽혔다. 문맥상 목록 같지만 바로 뒤 문단에서 `records/`, `events/` 같은 진짜 디렉터리가 나와 혼동됐다.

**R23.** > "`events/` holds one file per publication with its time, `organizations/` the organizer outputs, `questions/` the questions the operator published, and `reviews/` the comprehensive reviews"
동사를 생략한 병렬이 넷 이어져 "the organizer outputs"가 명사구인지 "organizer가 출력한다"는 절인지 한순간 헷갈렸다.

**R24.** > "The sixth role, the **organizer**, keeps the knowledge base navigable."
와 역할 표의 "Modules of records, the choice of shared context, glossary decisions, merges". 표 끝의 "merges"가 홀로 서 있어 무엇을 합치는지 여기서는 알 수 없고, 한참 뒤 "merges nodes or questions that turn out to be the same"에서 알았다.

**R25.** 한눈 보기 표와 본문 사이: 표는 "every record and every reviewed implication on two routes to the root was accepted", 본문은 "every record and every implication had been accepted". 사소하지만 "reviewed"의 유무로 본문의 implication이 검토된 것인지 되묻게 된다.

**R26.** > "the frontier held 108 nodes, and ten pipelines were still working on nodes and questions other than the root."
이 숫자는 23:15 시점으로 적혀 있는데, 첫 운전 문서의 108 nodes는 17:45 표에 있고 23:15 문단에는 노드 수가 없다. 같은 값이 맞는지 문서만으로 확정할 수 없다.

### 첫 운전 문서

**F1.** > "This document is the full account of the first run of the current do-math implementation, as of the evening of 12 November 2026; the run continues. The size table below is a snapshot from 17:45 Korean time that day."
그리고 Limits 절은 23:15 숫자를 준다. 한 문서에 기준 시각이 둘이어서 어느 숫자를 인용해야 할지 멈췄다.

**F2.** > "with the statement above as its root and a standing input that it use no records or code from an earlier instance"
"that it use"는 가정법 현재로 문법적이지만 처음 읽을 때 오타로 보여 되돌아갔다.

**F3.** > "In the first case the descent is at the step from m−1 to m and the ascent at or beyond m; in the second both are at or beyond m; in the third the descent is below m−1 and the ascent at or beyond m; in the fourth both are below m."
네 경우가 모든 가능성을 덮는지 문장이 말해 주지 않아 직접 따져 봐야 했다(d < a 조건 하에서는 덮는다). 또 "step"이 인덱스 ℓ인지 ℓ→ℓ+1 이동인지를 "the step from m−1 to m"으로 미루어 정해야 했다.

**F4.** > "The third and fourth cases of the first route were in turn proved by showing that the sequence has no descent at all below the middle, that is, that it never decreases there."
"below the middle"이 step m−1(b(m−1)→b(m))을 포함하는지 모호하다. 첫째 경우가 그 step을 따로 다루고, 넷째 경우는 "both are below m"이라 포함하는 것처럼 읽힌다. README의 "never decreases below the middle"도 같은 모호함을 가진다.

**F5.** > "The last open premise on the routes was a single node, pair-beats-capped-threshold."
노드 이름이 설명 없이 슬러그로 나온다. 어떤 "pair"가 어떤 "capped threshold"를 이긴다는 것인지 "in outline, it is an inequality between two counts of configurations"로 짐작만 했다.

**F6.** > "Its review supported the proof's claims and accepted the proof, marking one peripheral claim about a table's coverage as unsupported."
"a table"이 어느 표인지 여기서는 알 수 없다. 뒤의 개입 표에 "the table used by record r030ffaeb"가 나오면서 같은 표인가 싶었지만 연결이 문서에 없다.

**F7.** > "the rule that limits formalization to outcomes that can reach the root was added to the runner afterwards, prompted by this node."
README는 이 규칙을 설계의 일부처럼 서술한다("Formalization is requested only for the proof of a node on a route or for the refutation of a necessary condition."). 첫 운전 문서에 와서야 이 규칙이 운전 중 사례에서 나왔다는 것을 알았다. 두 문서가 틀린 말을 하는 것은 아니지만 README만으로는 "설계된 시스템을 돌렸다"로 읽히고, 첫 운전 문서로는 "돌리면서 설계했다"로 읽힌다.

**F8.** 개입 표의 "Kind" 열: `Standing input`, `Software`, `Settings`, `Operator action`, `Session termination`. README는 이 문서가 "every intervention by the user and the operator"를 서술한다고 했는데, 표의 대부분 행은 사용자와 운영자 중 누가 했는지 적지 않는다. `Operator action`만 명시되어 있어 나머지는 사용자가 했다고 추측했지만, "Software" 변경은 저자가 코드를 고친 것이고 "Settings"는 operator가 바꿨을 수도 있다. 사람 개입 범위를 알고 싶은 독자에게 핵심인 구분이 비어 있다.

**F9.** > "7 November, evening | Standing input | Register a section before beginning research on it; withdrawn on 9 November after 89 sessions had received it"
왜 철회했는지 이유가 없다. README는 section 등록을 조정 메커니즘의 핵심으로 설명하므로, 그것을 명시하는 지시가 철회됐다는 것은 의미 있는 사실인데 멈춰 서서 이유를 찾다가 포기했다.

**F10.** > "12 November, 04:54 | Standing input | Material from a session outside the instance, passed on as unverified material for the sessions to judge for themselves"
어떤 자료인지 전혀 알 수 없다. 수학적 내용인가, 운영 지시인가? "a session outside the instance"는 사용자가 따로 돌린 AI 대화인가? 이 운전의 "autonomous"가 어디까지인지 판단하는 데 직접 걸리는 항목인데 내용이 비어 있다.

**F11.** > "12 November, 14:15 | Standing input | Prove the two monotonicity properties that the table used by record r030ffaeb depends on, before any other work; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove them"
세 가지 문제가 겹친다. (가) r030ffaeb가 처음 나오는데 무엇을 한 기록인지 설명이 없다(Limits에서 binary64에 의존한다는 것만 나온다). (나) "each prove them"은 세 기록이 각각 두 성질을 모두 증명했다는 뜻으로 읽히는데, 같은 것을 셋이 따로 증명했다는 것인지 각각 하나씩인지 두 가지로 읽혔다. (다) 가장 무거운 것: 11일에 "informally proved"가 됐는데 12일에 사용자가 "표가 의존하는 단조성을 먼저 증명하라"고 지시했다면, 11일의 상태가 미증명 가정 위에 있었다는 뜻인가? 그렇다면 README의 "every record and every implication had been accepted"와 어떻게 맞는가? 문서는 이 연결을 말하지 않는다.

**F12.** README의
> "The user's standing inputs may state priorities, but the choice of what to work on stays with the session."
와 첫 운전 문서의 "before any other work" 지시 사이. 후자는 우선순위 진술이 아니라 작업 배정으로 읽힌다. 두 문서가 서로 다른 그림을 준다.

**F13.** > "On 9 November the user paused all formalization so that the research could finish first, and the five formalizations then in progress were ended without peer or review, so nothing of them was published."
README는 "if the session had begun research, its retained work goes on to a peer and a review"라고 했다. 여기서 그 규칙이 사람의 결정으로 무시됐다. 규칙과 예외의 관계가 어느 문서에도 적혀 있지 않다.

**F14.** > "Until the evening of 6 November, peer and review preferred the same model as the producing roles; they were then moved to Claude Opus 5.5 as their first choice"
README의 "independent judgment" 설계 설명을 읽은 뒤라, 첫 이틀 가까이 같은 모델이 자기 종류의 일을 평가했다는 사실에서 멈췄다. 틀린 말은 아니지만 README의 설계 서술이 첫 운전 전체에 적용되지는 않는다.

**F15.** > "In the part of it that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records found that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows"
"the part of it"의 "it"이 "that statement"(중간 아래에서 감소하지 않음)인지 "the fourth case"인지 한 문장 되돌아갔다.

### 운전 안내

**U1.** > "The defaults are eight concurrent sessions (`max_sessions`), attempts and explorers launched at least 180 seconds apart (`launch_interval`), an exploration request raised by the runner each time an attempt is launched (`explore_every`; the request is granted when a question is free, that is, open and held by no session, and the interval has passed), an organizer after four research publications (`organizer_every_records`), and up to three reconsideration turns before a session may end (`max_end_resumptions`)."
다섯 기본값이 한 문장에 들어 있고 셋째 항목 괄호 안에 조건절이 둘 더 들어 있어 세 번 읽었다. "research publications"라는 말도 record와 같은 뜻인지(organizer 출력은 빼는 것인지) 정의가 없다.

**U2.** > "With only Claude Code installed, list Claude models only, both in the common list and in the two role entries, as here with the Opus alias the Claude CLI resolves"
"as here with the Opus alias the Claude CLI resolves"는 관계절이 압축되어 어색하다. "`claude/opus`는 Claude CLI가 실제 모델로 풀어 주는 별칭이다"라는 뜻을 세 번 읽어 잡았다.

**U3.** > "`start` launches the runner as a detached process, waits until the runner has written the record that confirms it is up"
여기서 "record"는 지식 베이스의 record가 아니라 runner의 상태 파일이다. 문서 전체가 record를 전문 용어로 쓰고 있어 "runner가 기록(record)을 공개했다는 뜻인가" 하고 멈췄다.

**U4.** > "`kill-session <id>` | End the identified session's CLI process; session IDs are in the `status` output. Retained research is still processed once launching is resumed."
"Retained research"는 앞서 쓰인 "retained work"의 변형이다. 같은 것인지 확인하느라 되돌아갔다. 또 "once launching is resumed"는 stop을 먼저 했다는 전제를 깔고 있어 kill-session만 쓴 경우에는 무슨 일이 나는지 알 수 없다.

**U5.** > "The runtime needs Lean 4 in every case, even for a problem whose proofs will not use it, because the settings name a Lean installation and the broker starts with the runner"
이유가 "설정이 그것을 지명하기 때문"이어서 순환으로 들린다. 설계상의 이유(왜 선택적으로 만들지 않았는가)는 알 수 없다.

**U6.** > "beyond those, the sessions have only the CLIs' built-in tools, which include shell commands and web search."
세션이 웹 검색을 쓸 수 있다는 것을 여기서 처음 알았다. README의 "the only outbound traffic is the CLIs' own"과 모순은 아니지만, 외부 지식 유입 경로가 있다는 점은 README가 드러내지 않는다.

**U7.** > "a cold compile against Mathlib took about seven minutes and about a gigabyte of memory on the development machine, which is why compiles go through the broker."
"which is why"의 선행사가 컴파일 비용인데, 비용이 크다는 것이 왜 broker라는 별도 프로세스를 요구하는지(동시 컴파일 메모리 제한)는 README의 broker 설명을 떠올려야 연결됐다.

### Zenodo 설명문

**Z1.** > "The conjecture has no Lean proof, because the user paused formalization on 9 November so that the research could finish first."
두 가지. (가) "the user"가 이 독립 문서 안에서는 정의 없이 나온다. do-math에 "user"라는 역할이 있다는 것은 README를 읽은 뒤에야 안다. 마지막 문단에 "the instructions that the user gave to the sessions"가 있어 간접 정의가 되지만 순서가 뒤다. (나) "because"가 인과를 과하게 잡는다. 멈추지 않았더라도 Lean 증명이 있었으리라는 보장은 없다. README의 병렬 서술("And there is no Lean proof ... and the user paused")이 더 정확하다.

**Z2.** > "The state has qualifications that a reader should know before relying on it."
"The state"가 앞 문단의 "the state that do-math calls informally proved"를 받는데, 문단이 바뀐 뒤여서 추상 주어 하나로 받으면 잠깐 끊긴다.

**Z3.** > "The term is do-math's own and claims less than the words may suggest"
"term ... claims"는 의인화가 어색하다. README의 "it means less than the words might suggest"가 자연스럽다.

**Z4.** > "Every record was produced in three stages by three different sessions: one worked on the problem, a second read everything the first left behind and developed it into the record, and a third checked that record against the first session's files and assessed every claim in it."
README의 "a session works on the problem: it tries to prove or refute a statement, to understand some feature of the problem, or to turn an accepted proof into Lean"과 달리 여기서는 Lean 작업이 "worked on the problem"에 묻힌다. 틀리지는 않지만 Lean 기록 r0af7f414를 뒤에서 언급하므로 첫 단계에 형식화도 들어간다는 것을 모르는 독자는 어리둥절할 수 있다.

### 문서 사이에서 서로 다른 말을 하는 자리 (위에 적지 않은 것)

**X1.** README 역할 설명과 첫 운전 문서의 기본값 변경: README는 "By default the peer and review roles prefer a different model from the one the producing roles prefer."라고 현재형으로 말하고, 첫 운전 문서는 "the default described in the README ... was adopted at the same time"(6일 저녁)이라고 한다. 첫 운전의 처음 1.5일은 README의 기본값이 아니었다.

**X2.** README는 explorer 요청 빈도를 말하지 않고, 운전 안내는 "an exploration request raised by the runner each time an attempt is launched"를 기본값으로 주며, 첫 운전 문서는 "Explorer cadence changed from one request per three attempt launches to one per launch"(9일)라고 한다. 기본값이 운전 중에 바뀐 값인지, 설정만 바뀐 것인지 알 수 없다.

**X3.** README의 "No session assigns work to another ... the one exception is formalization"과 첫 운전 문서의 operator가 질문을 리뷰 없이 올린 행위·사용자의 "before any other work" 지시. README의 "no session"은 세션 사이의 말이고 사람·operator는 세션이 아니라고 읽으면 모순은 아니지만, 자율성의 그림이 두 문서에서 다르다.

---

## 3. 확정하지 못한 것

문서만으로 알 수 없어 외부 지식으로 메웠거나 추측한 것들이다.

1. **Lean 4, Mathlib, Lake, `sorryAx`, `propext`/`Classical.choice`/`Quot.sound`**: 증명 보조기와 그 표준 라이브러리, 빌드 도구, 미완성 증명 표지 공리, 고전 논리 표준 공리 셋이라는 것은 외부 지식이다. 문서는 어느 것도 설명하지 않는다.
2. **binary64**: IEEE 754 배정도 부동소수점이라는 것은 외부 지식.
3. **Claude Code의 "skill", 권한 프롬프트, Codex의 approval policy·sandbox**: CLI 동작의 의미는 외부 지식으로 메웠다.
4. **"Korean time"**: UTC+9로 가정했다.
5. **Zenodo의 concept DOI와 version DOI의 관계**: 외부 지식.
6. **사용자와 운영자의 분담**: 개입 표의 어느 행을 사람이 직접 했고 어느 행을 operator AI가 했는지 추측했다(Operator action 하나만 명시). "Software" 변경은 저자가 직접 코드를 고친 것이라고 추측했다.
7. **12일 04:54의 외부 자료의 내용**: 전혀 알 수 없다. 수학적 힌트였다면 결과의 자율성 평가가 달라진다.
8. **11일의 "informally proved"가 r030ffaeb 표의 미증명 단조성에 의존했는가**: 12일 14:15 지시로 미루어 그랬을 가능성을 추측했으나 문서는 말하지 않는다. 만약 그랬다면 11일의 상태와 "every record and every implication had been accepted"의 관계를 다시 물어야 한다.
9. **"register a section" 지시의 철회 이유**: 알 수 없다. 세션들이 이미 그렇게 하고 있어 중복이었거나, 역효과가 있었다고 추측만 했다.
10. **"earlier instance ... under a previous implementation"**: 어떤 것이었는지, 결과가 무엇이었는지 알 수 없다. 저자가 그 기록을 읽고 에세이를 썼으므로 사람을 거친 간접 영향 경로가 있다는 것만 안다.
11. **수학적 결과의 정확성**: 문서는 경로의 구조만 주므로 증명이 맞는지는 전혀 판단할 수 없다. b(n, n−1) = nⁿ⁻² 같은 수치도 직접 따져서 받아들였다.
12. **"below the middle"의 정확한 범위**(F4): step m−1 포함 여부를 확정하지 못했다.
13. **retained work에 대화 전체가 포함되는가**(R10): peer 문단으로 미루어 포함된다고 받아들였다.
14. **일반 리뷰의 finding이 claim standing을 바꾸는가**(R15): comprehensive review만 바꾼다고 추측했다.
15. **비용·토큰 사용량**: 문서가 수집하지 않았다고 명시했으므로 알 수 없다. 1,200여 세션을 100만 토큰 컨텍스트로 돌린 규모는 가늠만 했다.
16. **Linux에서 실제로 도는가**: 미검증이라고 했으므로 모른다.
17. **Jev, TypeSafe**: 무엇인지 모른다. do-math와 무관한 도구라 넘어갔다.
18. **v3의 기록 수와 시각**: 자리 표시자가 남아 있어 모른다.
19. **23:15의 노드 수 108**(R26): 17:45 값과 같은지 확정하지 못했다.
20. **"research publications"**(U1): record와 같은 뜻인지, organizer 출력·comprehensive review를 뺀 것인지 추측했다(뺀 것으로).
