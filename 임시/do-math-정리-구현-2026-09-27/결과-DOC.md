# 결과: DOC 그룹(스킬 문서)

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-doc`. worktree는 `C:/math-worktrees/c-doc`이며, `c-int`의 `34a034f`(OPS 그룹 병합)에서 시작했다.
- 마지막 커밋: `2e20aff`

바꾼 파일은 아래와 같다. 경로는 `.claude/skills/do-math/` 기준이다.

- 제품 코드: 없음. 읽기 대응표는 코드가 `SKILL.md`의 표 블록을 파싱하므로 코드를 바꿀 필요가 없었다.
- 시험
  - `scripts/tests/test_reading_map.py`: 기존 순서 단언을 고쳤고, 역할 행 배분을 단언하는 시험 하나를 더했다.
- 문서
  - `SKILL.md`
  - `GLOSSARY.md`
  - `README.md`
  - `AGENTS.md`
  - `references/공통-실행.md`
  - `references/자기-점검.md` (신규)
  - `references/모델과-실행예산.md`
  - `references/입력-소비자.md`
  - `references/과제-착수조건.md`
  - `references/CLI-실행-계약.md`
  - `references/초기화-운전.md`
  - `references/초기화-효율과-정비.md`
  - `계약/후보-준비.md`
  - `계약/연구-계획.md`
  - `계약/연구-수행.md`
  - `계약/운영-점검.md`
  - `계약/독립-운영.md`
  - `계약/동일성-검토.md`
  - `scripts/tests/시험-지침.md`: 1절만 고쳤다. DOC-10의 이전이다.
- 저장소 임시 자료(HIS-07): `임시/시험-경량화-2026-09-26/`
  - 작업자 노드 9개의 frontmatter를 고쳤다.
  - 작업자 노드 폴더에 `README.md`를 새로 두었다(`git add -f`).
  - `작문/`의 3개와 `작문-B4/`의 4개를 `git rm --cached`로 추적에서 뺐다. 파일은 디스크에 남아 있다.

## 2. ID별 처분

### 담당 ID

| ID | 처분 | 내용 |
|---|---|---|
| DOC-01 | 구현함 | 편입 묶음 선언 조건의 정본을 `공통-실행.md` 「주 응답의 의미와 보존」 절의 번호 목록 하나로 두었다. 목록은 코드와 같은 네 경우다(확장 `knowledge_changes`·`task_dispositions`·`revision_resolutions`, `revises_task_id` 후보, `action.revision_targets`, 부분 편입 재시도). `revision_requests`는 선언 대상이 아니라고 적었다.<br>GLOSSARY의 상황표와 SKILL의 세 문단은 요지와 참조로 줄였다. 공통 실행의 철회 예시와 `연구-계획.md` 철회 문단에는 선언 필요를 한 줄씩 더했다. CLI 712·853행 부근에는 "과제 철회 포함"과 개정 대상 배정 실행을 적었다. |
| DOC-02 | 구현함 | 사용자 결정 2절 3항의 두 항목만 구현했다. 세부는 아래 「DOC-02의 구현」에 있다. |
| DOC-03 | 구현함 | 먼저 `모델과-실행예산.md` 66-93행의 고유 규칙을 `후보-준비.md` 보충 절로 옮겼다. 옮긴 규칙은 배정되는 두 경우, 학술 과제 반려 시 `model_assessment_history`·`observation_rule_history` 보존, 평가 반환·보류 형식과 예시, 사용자 요구 변경 시 보류, 수신자의 판본 대조와 비적용, 보류의 `waiting_actions`·재요청 조건, 반려 뒤 재검토다.<br>그다음 `모델과-실행예산.md` 절을 요지와 참조로 줄였다. "계약 검토 모델은 난이도·중요도·역할 하한 중 높은 등급"은 모델 배정 규칙이라 그 절에 남겼다. `SKILL.md:69`, `공통-실행.md`의 확장 절 문장, `CLI:913`은 요지와 참조로 바꿨다. 후보 준비 절 첫머리에는 정본 선언과 중심 규칙 요지를 두었다. |
| DOC-04 | 구현함 | `SKILL.md` 145-151행(제출 네 문단)을 "「최종 응답을 전달하고 필요한 오류를 수리한다」 절을 따른다"는 한 문장과, 기계 검사가 판정을 대신하지 않는다는 한 문장으로 줄였다.<br>`SKILL.md:71`의 제출 사본은 "기계 검사 통과는 계약 검토 승인이 아니다" 한 문장으로 줄였다. `CLI:923`의 SKILL 사본은 SKILL 절 참조로 바꿨다. 95-99행은 DOC-01과 함께 처리했다. 대응표 블록 자체는 DOC-02 말고는 바꾸지 않았다. |
| DOC-05 | 구현함 | 정정을 따랐다.<br>(1) README에만 있던 writer lock 실패 행 내용을 CLI 종료 코드 표 5행으로 옮기고 `exit-codes` 앵커를 두었다. 그 뒤 README의 종료 코드 절과 정책 JSON 예시를 CLI 참조로 바꿨다.<br>(2) 300초는 CLI 설정 계약 한 곳에만 두었다. CLI 323행(구 321행)은 그곳을 가리킨다.<br>(3) `공통-실행.md`의 4 MiB·64 KiB는 `submission_contract.limits.checkpoint_bytes`·`observation_rules_bytes`로 바꿨다. 16개 한도는 남겼다.<br>(4) 부록 절에서 앞 절이나 다른 정본과 겹치는 문단만 지웠다. 지운 것은 판본 재초기화 문단, 묶음 규칙 재서술, `claude_only_assigned_model` 문단, 공급자 대기 재서술 일부, `probe_cli --skill-only` 재서술이다.<br>(5) 검증이 고유하다고 한 `input_metrics`, `operating_summary`, `review_basis_key`, `decision_basis`와 `error_kind` 표, `question_links`, `finish_notice_seconds`, `timeline`은 그대로 두었다. |
| DOC-06 | 구현함 | (나)를 택했다. `SKILL.md:12`·`39`는 복구 AI가 실행기 고정 프롬프트를 따르고 독립 운영 계약은 그 경계를 운영자에게 설명한다고 고쳤다.<br>`독립-운영.md`에는 지시·금지의 정본이 `scheduled_operator.py` 프롬프트이고 이 문서는 복구 AI에게 지급되지 않는다고 적었다. 금지 목록은 코드 프롬프트 내용(`scheduled_operator.py:554-556`)의 요지로 바꿨다. 반환 필드의 정본은 `repair_report_schema`와 프롬프트라고 적었다. |
| DOC-07 | 구현함 | CLI 5·7·54·56·93·128·254·442·873·905·933·936·942·944·952행과 README 500·504·506행, `초기화-운전.md:5`의 "판본 5"·"기능 판본 5" 산문을 현행 표현으로 바꾸거나 지웠다.<br>옛 두 루트 snapshot의 명시적 거부 문장(CLI 56), `research/instance.json` 가정 문장(254), 옛 두 루트 수입 문장(944)은 지웠다. 부록 절 제목은 「전제·대기·조회 계약」으로 바꿨다. 실제 값인 `schema_version:5`와 `do-math-cli/5`는 유지했다. |
| DOC-08 | 구현함 | `운영-점검.md:27`의 "비활동"을 코드의 `periodic_review_due`에 대응하는 "주기 점검 도래"로 바꿨다. |
| DOC-09 | 구현함 | GLOSSARY의 「툴체인 기록」·「판본 식별」·「지문」 정의를 `초기화-효율과-정비.md` 「신뢰 환경 확인의 개요」로 옮겼다. 그 절에는 이미 같은 요지가 있어 목록으로 합쳤다.<br>GLOSSARY 「신뢰 환경」에는 우발적 변경만 다룬다는 문장과 링크만 남겼다. `동일성-검토.md:101`은 편입 관문이 실행기의 일이며 검토자의 판단 대상이 아니라는 요지와 참조로 줄였다.<br>검증 정정대로 "지문을 편입 때 재대조하지 않는 이유"는 운영 문서에 남겼다. 이 내용은 이미 `초기화-효율과-정비.md`의 시점별 표와 그 아래 문단에 있었다. 없던 사실인 "같은 원문·판본 식별이면 기존 형식 검사 결과 재사용"은 그 문단으로 옮겼다. |
| DOC-10 | 구현함 | 먼저 README에만 있던 운용 사실을 `시험-지침.md` 1절로 옮겼다. 옮긴 사실은 discovery 수집과 조각 순차 실행, 선택 없음 실패, `--timeout` 기본 300초와 제품 계약 무관성, 시간 초과 시 Job 자식 종료·미실행 기록·계속 진행, 비격리 시험의 상한 없음, `report.json` 필드(`shard_seconds`, 느린 목록, 코드 판본·실행 중 변경), `scratch/` 위치, `unittest discover` 한계다. 각 사실은 `run_tests.py`에서 확인했다.<br>그다음 README 절을 두 문장으로 줄였다. AGENTS의 "결과 캐시는 없다"는 지웠다. 시험 지침의 다른 절과 1절의 기존 "캐시 없음" 문장은 건드리지 않았다. |
| DOC-11 | 구현함 | 「활동」의 고유 내용을 「AI 활동」에 합쳤다. 합친 내용은 계보 유지, 대기 중 슬롯 비점유, 중복 저작 금지, 활동 종료와 과제 완료의 구별이다. 「활동」은 같은 개념의 줄임말이라는 한 줄로 두었다.<br>`공통-실행.md:3`의 `request_source_ref` 문단은 「시작할 때 입력을 확인한다」 절의 `action.source_ref` 문단 뒤로 옮겼다. |
| HIS-16 | 구현함 | 두 항목을 처리했다.<br>(1) `입력-소비자.md`의 필드 나열은 현 형태 유지로 판정한다. 근거는 `governance.py`가 기본 소비자의 producer contract로 이 문서의 절을 직접 가리키고, 의도 해석 출력 스키마에는 payload 모양이 없어 이 나열이 유일한 작성 안내라는 점이다. 7행은 이미 "검사와 다르면 검사가 정한다"로 우선순위를 닫고 있다.<br>(2) "비활동"은 DOC-08과 합쳐 "주기 점검 도래"로 바꿨다. |
| HIS-07 | 구현함 | 작업자 노드 폴더에 지위 안내 `README.md`를 두었다. 내용은 추적된 원문 사본이라는 점, 본문의 "Git 제외" 서술은 작성 시점 기준이라는 점, 기억 노드가 아니라는 점이다.<br>frontmatter `id: M-035x` 9곳을 `worker_id: <작업자>`로 바꿨다(B1, B2, B3, B4×2, W-debt, W-eng, W-fix, W-git). 작업 트리는 CRLF 그대로다.<br>`작문/`의 3개와 `작문-B4/`의 4개를 `git rm --cached`했다. `임시/*/*` 무시 규칙 아래에서 다시 추적되지 않는다. |

#### DOC-02의 구현

**「모델과 실행예산」.** common 행에서 빼 `research_preparation`, `research_plan`, `task_contract_review` 행에 넣었다.

의도 해석의 인용(`입력-소비자.md:48`)은 선택지 가운데 옮기는 쪽을 택했다. 그 인용이 가리키던 설정 작성 규칙을 `입력-소비자.md` configuration 절로 옮겼다. 옮긴 규칙은 다음과 같다.

- `claude:`·`claude-` 접두어로 CLI를 고르는 규칙
- 등급마다 모델 하나를 지정한다는 규칙
- `session_limits.work`에 같은 표기로 모델 전부를 적고, 0 이상 정수이며 0은 대기라는 규칙
- 별칭과 전체 ID를 섞으면 별도 예산이 된다는 규칙
- 두 맵은 전체를 제안한다는 규칙
- `role_tiers`
- `claude_only_assigned_model`의 효과와 한 모델 전용 연구의 표기

`모델과-실행예산.md:11`에서는 표기 규칙을 지우고 CLI 설정 계약(233행, 같은 규칙을 이미 가짐)으로의 참조를 두었다. `공통-실행.md:73`의 인용은 그 문서를 받는 세 역할에 한정되도록 고쳤다.

**자기 점검.** 새 `references/자기-점검.md`로 옮기고 `research_work`, `operational_review` 행에 넣었다. 코드의 근거는 `observations.py:204`의 `research = profile["role"] == "research_work"`다. 공통에는 검증 정정대로 세 가지를 남겼다.

- 규칙 필드(구 128행)
- 연산자 표와 그 해설(130-139행)
- 교체 객체·최초 규칙·`$execution` 결박과 예시(141-161행)

남긴 절의 제목은 「관찰 규칙의 형식」이고, 도입문에서 응답 절차의 소재를 밝혔다. 옮긴 것은 120·122·124·126·163·165-181행이다. `연구-수행.md:78`, `운영-점검.md:13`, `CLI:228`, `CLI:825`의 인용도 새 문서를 가리키게 고쳤다. 검사 결과 이 인용을 쓰는 다른 역할 계약은 없었다.

**`test_reading_map`.** 순서 단언을 새 공통 목록으로 고쳤다. 연구 수행 프롬프트에 모델 선택 문서가 없다는 단언을 더했다. 역할 행 여섯의 배분을 단언하는 `test_role_rows_add_their_references_after_the_common_documents`를 더했다.

**절감량.** 검증 정정 값으로 적는다. 역할별 공통 입력 바이트이며, `c-int` 대비 DOC-02만의 효과다.

| 역할 | 절감 |
|---|---|
| 동일성 검토, 목표 감사, 보충 조사, 유지보수 | 23,730B(`모델과-실행예산` 현 크기 17,543B + 자기 점검 순감 6,187B) |
| 의도 해석 | 22,622B(위에서 옮겨 온 설정 규칙 1,108B를 뺌) |
| 연구 수행, 운영 점검 | 16,209B(17,543B에서 새 문서의 머리·도입 1,334B를 뺌) |
| 후보 준비, 연구 계획, 작업 계약 검토 | 6,187B |

검토 원안의 "약 33KB·23KB·11KB"보다 작다. 원인은 정정대로 두 가지다. 규칙 형식·연산자 표·`$execution`을 공통에 남겼고, 의도 해석은 인용 해소분이 더해졌다.

다른 ID까지 합친 역할별 전체 감소는 다음과 같다. 연구 수행 −24,856, 운영 점검 −24,813, 동일성 검토 −32,687, 목표 감사·보충 조사·유지보수 −32,468, 의도 해석 −31,360, 후보 준비 −11,283, 연구 계획 −14,816, 작업 계약 검토 −14,845B.

### 통합자가 추가한 항목

| 항목 | 처분 | 내용 |
|---|---|---|
| `test_static_review_repairs.InputBoundaryRepairs.test_profile_query_document_reads_cli_result_envelope` 실패 | 구현함 | 원인은 `초기화-운전.md:169`·`174`의 PowerShell 예시가 `query --kind execution_profiles`를 쓴 데 있다. ENG-07 뒤 `engine._QUERY_FAMILIES`가 결과의 `family`를 공개 이름 `execution-profile`로 바꾸고, `query_records`의 `--kind` 필터가 그 공개 이름과 비교하므로 조회가 비었다. 두 줄을 `--kind execution-profile`로 고쳤다(ENG 반환 4절 항목과 같은 수정).<br>이 시험 ID는 `c-doc`에서 통과했다. 수정 직후 한 번, 마지막 문서 수정 뒤 인계 확인에서 한 번 통과했다. 변경 전 판본에서의 실패는 통합자 보고와 위 정적 원인으로 확인했고, 직접 재현하지는 않았다. |

### 반영한 후속 문서 변경(출처별)

| 출처 | 항목 | 처분 |
|---|---|---|
| KS | README 15행, CLI 5·54행의 `do-math-state/6` → `/7` | 반영 |
| KS | `동일성-검토.md:13`의 `policy_version=5` 삭제 | 반영. 같은 사안인 CLI 746행 "정책 ID와 판본 5"도 "정책 ID"로 고쳤다(`review_policy.py:18`에 판본 필드 없음). |
| KS | `과제-착수조건.md` 포인터 표의 knowledge `/value`, governance `/lifecycle` 삭제 | 반영. 알려진 실패 `test_readiness_document_tables_match_the_condition_grammar`가 통과한다. |
| KS | (선택) "판본 식별은 루트 manifest만 싣고, 기록과 metadata에는 판본 표지가 없다" | 반영하지 않음. 코드와 어긋난다. `repository.py:816`의 `_envelope`가 기록마다 `contract_id`를 싣고, 915·957행이 metadata와 기록 봉투의 `contract_id`를 대조한다. KS 자신의 반환 52행도 "루트 manifest의 `contract`와 기록 봉투의 `contract_id`에만 남겼다"고 적는다. |
| KC | CLI 146행 `DEFAULT_CONFIG` 위치 → `scripts/do_math/configuration.py` | 반영 |
| KC | (선택) README 개발·시험 부근에 `scripts/이음새-정본.md` 한 줄 | 반영하지 않음. README는 운영자 문서이고, 개발 원칙 문서인 `AGENTS.md`가 이미 그 파일을 가리킨다. |
| ENG | `초기화-운전.md:169`·`174`의 `--kind execution-profile` | 반영(통합자 추가 항목과 같음) |
| ENG | CLI query 절에 가족 이름 규칙 한 문장 | 반영. 조건 문법 가족 이름, 표 밖은 저장 이름, 질문 행은 `question`이다. |
| ENG | README status 표와 508행: snapshot 조회의 관측 필드 null, `pending_controls` 조건 | 반영. 관측 필드인 `budget` 행에도 같은 조건을 붙였다(`reporting.OBSERVED_FIELDS`). 508행의 "저장된 … 슬롯 예산·`provider_waits`" 서술은 관측 필드라는 현행 사실로 고쳤다. |
| ENG | README 사람용 status의 단일 렌더러·`not observed` | 반영 |
| ENG | CLI configure 설명에 운영자 출처가 바꿀 수 없는 다섯 키와 접수 거부 | 반영(`control_contracts.USER_DECISION_SETTINGS`) |
| RUN | README 458행, CLI 230행 `role_tiers.independent_operator` → `role_tiers.recovery` | 반영 |
| IO | `공통-실행.md` 165행: 응답 형식은 도구 설명의 JSON Schema로 공개 | 반영. 이 문단은 DOC-02에 따라 `자기-점검.md`로 옮겨졌다. `control_transport.py:558-560`에서 확인했다. |
| IO | `초기화-운전.md` 215행 식별 모듈에 `cli_worker` | 반영(`codex_adapter.py:330`) |
| RES | `초기화-효율과-정비.md` 18·61행: 검사기를 모듈 바이트 SHA-256으로 대조 | 반영. 61행의 판본 식별 정의 한 곳에 넣었다. 18행 표는 "판본 식별 파일 대조"라서 정의를 따른다(`formal.py:19-22`). |
| RES | (선택) `과제-착수조건.md` 18행: 경로 규칙 위반의 제출 단계 거부 | 반영(`planning.validate_condition` 331-343행) |
| REV | `동일성-검토.md` 범위 계획 절의 `scope_complete`·`questions` 문장 | 반영(`review_cycle.py:942-943`) |
| OPS | `초기화-효율과-정비.md` 91행 수동 잠금 삭제 절차 → OS 잠금 | 반영. 잠금 경합 시 기다리지 않고 `status: error`, 종료 코드 2로 끝나며 지울 파일이 없다고 적었다(`trust_inventory.writer_lock`, `setup_lean.py:277-279`). |
| OPS | `시험-지침.md` 41행 보관소 복사 안내 삭제 | 반영하지 않음. 시험 지침 2절이며 파견문이 DOC-10 이전만 허락했다. 시험 단계 그룹(TORG)으로 넘긴다. |
| OPS | `scripts/이음새-정본.md` validate_config 행 반환값 | 반영하지 않음. 후속 배정표에서 통합자 몫이며 스킬 문서 범위 밖이다. |
| KS·KC·IO·OPS | `.agents/` 미러 재생성과 `.agents/diff/_rules.json` verbatim 두 항목 | 반영하지 않음. 파견문이 `.agents/`를 금한다. 통합자가 재생성할 때 이번 신규 파일 `references/자기-점검.md`도 포함해야 한다. |
| STO | 없음 | 해당 없음 |
| RUN | 소유 루프 반응 시간 문장 | 해당 문서가 없어 반영할 곳이 없다(RUN 반환과 같은 판단). |

처분별 건수는 다음과 같다.

- 담당 ID 13건: 구현함 13
- 통합자 추가 1건: 구현함 1
- 후속 문서 변경 21행: 반영 16(선택 1 포함), 반영하지 않음 5(부정확한 선택 문장 1, 선택 문장 1, 다른 절·범위 밖 2, `.agents/` 1). 해당 없음 2행은 따로 셌다.

## 3. 새 공유 정의와 지운 공개 이름

- 새 공유 정의: 없음. 새 역할 참조 문서 `references/자기-점검.md`와 CLI 종료 코드 앵커 `exit-codes`를 두었다.
- 지운 공개 이름: 없음. GLOSSARY 표제어 「툴체인 기록」·「판본 식별」·「지문」은 `초기화-효율과-정비.md`로 옮겼고, 스킬 안에서 이 표제어를 이름으로 인용하는 곳은 없다.

## 4. 필요한 문서 변경

이 그룹이 고치지 않았고 다른 담당이 할 것은 다음과 같다.

1. `.agents/skills/do-math/`(통합자): 미러를 재생성한다. 신규 `references/자기-점검.md`가 포함되어야 한다.
2. `scripts/tests/시험-지침.md` 2절(TORG): OPS 반환 4절 1항대로 보관소 복사 안내를 지운다. 1절의 기존 문장 "결과를 재사용하는 캐시는 없으므로 명령을 실행하면 선택한 시험이 항상 실제로 돈다"는 AGENTS에서 지운 것과 같은 경위성 문장이다. 시험 지침 소유 그룹이 지울지 판단한다.
3. `scripts/이음새-정본.md` validate_config 행(통합자): OPS 반환 4절 3항이다.

## 5. 실행한 시험과 작문 독해

### 시험

모두 `c-doc`에서 한 번에 프로세스 하나로 돌렸다.

| 명령 | 결과 | 비고 |
|---|---|---|
| `python scripts/run_tests.py test_walkthrough_repairs.WalkthroughRepairs.test_readiness_document_tables_match_the_condition_grammar test_walkthrough_repairs.WalkthroughRepairs.test_documented_readiness_examples_match_the_live_grammar` | 통과 2 | 앞 시험은 변경 전부터 실패하던 알려진 실패이며, 표를 고친 뒤 통과했다. |
| `python scripts/run_tests.py test_reading_map test_preflight test_contracts` | 통과 28 | DOC-02 편집 확인 |
| `python scripts/run_tests.py test_static_review_repairs.InputBoundaryRepairs.test_profile_query_document_reads_cli_result_envelope` 외 문서 대조 시험 4개(`test_walkthrough_repairs`의 착수조건 표·예시, U+N+4 하한, 연구 grant 예시) | 통과 5 | |
| 인계 확인: 위 세 모듈 + 문서 대조 시험 5개 | 통과 33, 실패 0, 오류 0 | 마지막 문서 수정 뒤 |
| `python scripts/probe_cli.py --skill-only` | `verified` | `installed_documents`, `role_output_schemas`. 모델 호출 없음. |
| `py_compile`(test_reading_map), `scripts/tests` 전 132개 `test_*.py` import | 오류 0 | |
| 옛 이름 grep | 남은 참조 0 | `independent_operator`, `--kind execution_profiles`, `state/6`, 문서의 "결과 캐시", "비활동"(발동 사유 의미), `policy_version`, `engine.py`의 `DEFAULT_CONFIG`, "판본 5", "기능 판본". GLOSSARY 251행의 "연구상 비활동 후보"는 다른 뜻이다. |

돌리지 않은 관련 시험은 없다. 제품 코드를 바꾸지 않았으므로 소비자 쪽 시험은 통합 확인에 맡겼다.

### write-for-reader 적용

세션은 `do-math-doc-20260927`이다. 사용자가 작업 중에 "독해를 동시에 할 수 있으면 하라"고 지시했다. 도구는 세션마다 활성 작업을 하나만 허용하고 ASCII 세션 ID만 받는다. 그래서 마지막 세 문서는 `do-math-doc-20260927-indep`, `-identity`, `-tests` 세션으로 나누어 병렬로 독해했다. 합의·독자·대조 파일은 `C:/math-worktrees/c-doc/임시/do-math-doc-작문/<문서>/`에 있고 추적하지 않는다. 독해 기록은 `C:/math-worktrees/c-doc/.codex/writing-flow/`에 있다. 모든 세션의 상태는 `ready`이고 `completion_problem`은 없다.

| 문서 | 적용 | 결과 |
|---|---|---|
| `references/자기-점검.md` | 독해 절차 | 1회 accept |
| `references/공통-실행.md` | 독해 절차 | 1차 revise, 2차 accept. 편입 묶음 네 경우를 번호 목록으로 바꾸고, 부분 봉인 조건 문장을 나누고, "비연구 역할"을 명시했다. |
| `계약/후보-준비.md` | 독해 절차 | 1차 revise, 2차 accept. 보충 절 첫머리에 정본 선언과 중심 규칙 요지를 두고, "평가된 독립 과제"를 명시했다. |
| `references/모델과-실행예산.md` | 독해 절차 | 1회 accept |
| `references/입력-소비자.md` | 독해 절차 | 1회 accept |
| `GLOSSARY.md` | 독해 절차 | 1회 accept. SKILL 독해에서 같은 표현("개정 대상이 배정된 실행")이 다시 지적되어 두 문서를 함께 고쳤고, 재독해도 accept였다. |
| `SKILL.md` | 독해 절차 | 1차 revise, 2차 accept. 대응표 도입에 배분 원칙 한 문장을 더했다. |
| `references/초기화-효율과-정비.md` | 독해 절차 | 두 번 blocked 뒤 accept. 독해자가 굵은 글씨 표지를 뺀 인용을 내 도구의 인용 대조에서 실패했다. 새 정의 목록의 굵은 표지를 지운 뒤 성공했다. |
| `계약/독립-운영.md` | 독해 절차 | 1회 accept |
| `계약/동일성-검토.md` | 독해 절차 | 1회 accept |
| `scripts/tests/시험-지침.md` | 독해 절차 | 1회 accept |
| `README.md` | 기본 점검 | 한 줄 사실 교정, 사본의 참조 치환, 절 축약이다. 주장·근거를 새로 세우지 않았다. |
| `references/CLI-실행-계약.md` | 기본 점검 | 한 줄 사실 교정, 판본 산문 정리, 중복 문단 삭제다. 새 문장은 query 가족 이름·configure 제한 두 문장이다. |
| `AGENTS.md`, `계약/연구-계획.md`, `계약/연구-수행.md`, `계약/운영-점검.md`, `references/과제-착수조건.md`, `references/초기화-운전.md` | 기본 점검 | 한 줄 교정·참조 |
| `임시/…/작업자-노드/README.md` | 기본 점검 | 한 문단의 지위 안내이며 스킬 문서가 아니다. |

## 6. 기능이나 시험 범위가 바뀐 것

- **역할 입력.**
  - 대상: 7개 역할이 「모델과 실행예산」을, 8개 역할이 자기 점검 절차를 더 받지 않는다.
  - 이유: 사용자 결정 2절 3항이다.
  - 잃는 것: 그 역할들이 두 문서의 내용을 참고할 수 없다. 인용 대조로는 이를 인용하는 역할 문서가 남지 않았다. 다만 M-0323이 적은 위험, 곧 실제로 필요할 때 저하가 오류로 드러나지 않는 위험은 남는다.
  - 얻는 것: 2절 DOC-02 절감량이다.
- **의도 해석.**
  - 대상: 설정 작성 규칙을 「모델과 실행예산」 대신 `입력-소비자.md`에서 받는다.
  - 이유: 인용 해소다.
  - 잃는 것: 모델 배정 기준 전문이다. 이 역할은 쓰지 않는다.
  - 얻는 것: 22.6KB 감소다.
- **시험.**
  - 대상: `test_reading_map`의 순서 단언을 새 대응표로 바꿨고, 역할 행 배분 단언을 더했다.
  - 이유: 대응표 변경이다.
  - 잃는 것: 없음. 같은 성질을 현행 계약으로 단언한다.
  - 얻는 것: 역할별 추가 문서의 배분이 시험된다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **줄 끝.** Python `write_text`가 Windows에서 CRLF를 써서 `과제-착수조건.md`에 CRLF가 들어갔다. 스킬 폴더는 `eol=lf`여서 곧바로 LF로 되돌렸다. 이후 모든 편집은 바이트 단위 치환으로 했다. `임시/` 작업자 노드는 `core.autocrlf=true`의 작업 트리 CRLF를 유지했다.
- **KS의 선택 문장.** KS가 권한 선택 문장("기록과 metadata에는 판본 표지가 없다")이 코드와 KS 자신의 반환에 모두 어긋나 반영하지 않았다.
- **DOC-02의 선택.** 의도 해석에 「모델과 실행예산」을 주는 대신 규칙을 옮기는 쪽을 택했다. 옮긴 규칙이 「모델과 실행예산」과 사본이 되지 않도록 원 문서의 표기 규칙을 지우고 CLI 설정 계약(같은 규칙 보유)을 가리키게 했다.
- **독해의 경중 판정.** 큰 문서(공통 실행 74KB, 후보 준비 49KB)는 독해자가 문서 전체를 절 단위 요지로 요약한다. 그래서 개정한 절의 세부 규칙이 이해 항목에 열거되지 않았다. 1차에서는 revise로 두고 절 첫머리 요지와 번호 목록으로 두드러지게 했다. 2차에서는 정본 문장이 원고에 명시되어 있고 중심 항목으로 잡힌 것을 근거로 accept했다.
- **독해 도구의 인용 대조.** 굵은 글씨가 있는 목록 행에서 독해자 인용과 원고가 두 번 불일치했다(blocked). 굵은 표지를 지운 뒤 통과했다.
- **통합자 추가 항목.** 원인이 ENG 반환 4절의 문서 변경과 같은 줄이어서, 이미 반영한 수정으로 해결되었다.

## 8. 다른 그룹 범위에서 발견한 문제

- `scripts/tests/시험-지침.md` 1절 9행의 "결과를 재사용하는 캐시는 없으므로 …"는 DOC-10이 AGENTS에서 지운 것과 같은 경위성 문장이다(시험 지침 소유 그룹).
- 그 밖에는 없음(확인 범위: 이번에 읽은 코드 `contracts.py`, `observations.py`, `planning.py`, `control_transport.py`, `scheduled_operator.py`, `formal.py`, `trust_inventory.py`, `setup_lean.py`, `run_tests.py`, `reporting.py`, `engine.py` 조회부).
