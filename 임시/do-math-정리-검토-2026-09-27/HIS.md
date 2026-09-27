# HIS 영역 검토: 세 경량화의 이력과 산출물

검토 기준 시점은 main `9b434f4`의 작업 트리다. 경로 표기는 `C:/math/.claude/skills/do-math/` 아래 파일이면 그 기준의 상대 경로(예: `scripts/do_math/engine.py:519`)로, 그 밖의 파일은 저장소 루트 `C:/math/` 기준 상대 경로(예: `docs/do-math/검사-경량화-이음새-계약.md:69`)로 적는다.

## 1. 읽은 범위

**전문을 읽은 파일**

| 파일 | 행 수 |
|---|---|
| `임시/do-math-정리-검토-2026-09-27/기준.md` | 238 |
| `.claude/skills/do-math/AGENTS.md` | 11 |
| `기억/layer1/M-0348.md`, `M-0349.md`, `M-0350.md` | 126, 64, 101 |
| `docs/do-math/검사-경량화-설계-2026-09-26.md` | 429 |
| `docs/do-math/검사-경량화-설계-2026-09-26-검사분류.md` | 61 |
| `docs/do-math/경량화-설계-2026-09-26.md` | 194 |
| `docs/do-math/검사-경량화-이음새-계약.md` | 245 |
| `임시/경량화-조사-2026-09-26/기준.md` | 120 |
| 같은 폴더 `결과-A`, `결과-B`, `결과-C`, `결과-D`, `결과-E`, `결과-F`, `결과-K시험`, `결과-K제품`, `결과-문서`, `결과-병합A`, `결과-이음새` | 195, 102, 163, 122, 132, 95, 204, 116, 307, 93, 283 |
| `임시/시험-경량화-2026-09-26/계약.md`, `진단-B4.md`, `진단-B4-2.md` | 62, 93, 58 |
| `임시/시험-경량화-2026-09-26/작업자-노드/` 9개(B1·B2·B3·B4-M-0350·B4-M-0351·W-debt·W-eng·W-fix·W-git) | 32, 30, 33, 30, 22, 37, 36, 49, 65 |

**일부만 읽은 파일**

- `임시/시험-경량화-2026-09-26/작문/합의.md` 1~20행과 `작문-B4/run1.log` 첫 600바이트. 추적 상태와 성격을 확인하려고 읽었다.
- 조사 파일 8개(`ENG.md` 등)와 `분석-G1~G3.md`: 전문을 읽지 않았다. 파견문 지시대로 필요한 항목만 보았는데, 이번 판정에 필요한 항목은 결과 파일과 진단 파일이 인용한 좌표로 충분했다.
- 이음새 확인을 위해 제품·시험 원문의 해당 행만 읽었다. 대상은 `scripts/do_math/`의 `engine.py`, `lifecycle_engine.py`, `repository.py`, `git_store.py`, `payloads.py`, `contracts.py`, `review_cycle.py`, `review_engine.py`, `governance_engine.py`, `governance.py`, `scheduler.py`, `submission.py`, `academic_engine.py`, `control_contracts.py`, `codex_adapter.py`, `claude_adapter.py`, `model_runner.py`, `initialization.py`, `execution_profiles.py`와 `scripts/check_coverage.py`, `scripts/setup_lean.py`, `scripts/test_categories.py`, `scripts/tests/research_fixtures.py`, `references/CLI-실행-계약.md` 48~50행, `references/초기화-효율과-정비.md` 90~99행이다.

**전수로 훑은 것**

- 세 커밋 `8d2ffd0`, `379a171`, `9b434f4`의 `git show --stat`, `--name-status`, 그리고 제품 diff의 `+` 줄. `time.sleep`, 예외 삼킴, 재시도 반복문, 작업 ID 주석을 검색했다.
- `docs/do-math/implementation-v5/traceability.json`(1,349,970바이트). 로컬 경로·`임시/`·`.skill-workspace`를 검색하고, `observed_runs` 15건의 보관소 의존을 계산했다.

**읽지 못한 파일**: 없다.

## 2. 영역 판정

제품 코드의 이음새 정본은 현재 원문과 맞는다. 이음새 계약 11절 표의 식별자는 전부 코드에 실재하고 적힌 모듈에 정의되어 있다(6절). 반면 세 경량화의 산출 문서는 현행 정본과 끝난 작업 지시가 한 파일에 섞여 있다. 게다가 현행 정본은 스킬 밖의 날짜 붙은 문서에만 있고 `AGENTS.md`가 가리키지 않아서, 「이음새마다 정의는 하나」가 다음 개발자에게 전달되는 경로가 없다. 가장 큰 개선 여지는 두 가지로, 이음새 계약의 현행 부분을 스킬 안의 정본 하나로 옮기고 나머지 경량화 문서를 역사 기록으로 표지하는 것(HIS-01·05·06), 그리고 세 경량화가 부분적으로만 적용한 원칙 셋(시험 호스트를 위한 제품 방어 제거, 경로 키 캐시의 무효화 소유, 공유 스키마 노드의 독립성)을 모든 영역에 마저 적용하는 것(HIS-02~04)이다. 기록된 위험·미확인·열린 질문 63행(3.1절) 가운데 대부분은 M-0350의 최종 전체 실행이나 사용자 결정으로 닫혔고, 열린 것은 HIS-05와 HIS-07~20으로 냈다.

검토했고 없음: 임시방편, 결함

## 3. 후보

### 3.1 기록 항목 대조표

세 경량화의 기록이 남는 위험·미확인·열린 질문으로 적은 항목을 전수로 모아 현재 원문과 대조했다. 상태 어휘는 셋이다. `닫힘`은 현재 원문이나 실행 기록으로 해소된 것이고, `수용`은 사용자 결정이나 문서화된 설계 한계로 받아들인 것이며, `열림`은 아직 닫히지 않아 후보로 낸 것이다.

「M-0350:43」은 최종 판본의 통합 확인 기록이다. 1,860개 통과, 실패 0, 건너뜀 2이고, 실행 중 소스 변경은 없었다. 시험으로 관찰할 수 있는 위험은 이 기록으로 닫힌 것으로 본다. 시험이 없는 경로나 실제 외부 프로세스가 필요한 경로는 이 기록으로 닫지 않았다.

| # | 출처 | 항목 | 상태 | 근거 좌표 |
|---|---|---|---|---|
| 1 | M-0348:60 | NTFS 터널링으로 지문이 교체를 놓침 | 수용 | `references/초기화-효율과-정비.md:96` |
| 2 | M-0348:54, 검사 설계:195 | "게시 직후 평가" 전제가 코드로 미확인 | 닫힘 | `scripts/do_math/scheduler.py:28-40`(매 바퀴 `_save`가 판정을 돈다) |
| 3 | M-0348:55, 검사 설계:245 | R12 변경 세대 카운터 포기 | 닫힘(대체) | `ResearchRepository.published_state`(계약 11절 행), `_state_generation` 0건 |
| 4 | M-0348:78-86 | 기존 실패 기준선 18개 | 닫힘 | M-0350:43, `작업자-노드/W-debt-M-0351.md:10-18` |
| 5 | M-0348:102 | 측정 인스턴스 paused 상태로 남음 | 닫힘(삭제) | M-0349:16. `.skill-workspace/` 목록에 `nat-add-zero-*` 없음 |
| 6 | M-0348:111 | 같은 사유의 `pause` 재전송이 영수증만 재생(미수정) | 수용(문서화) | `references/CLI-실행-계약.md:48-50`. 재개 뒤 같은 사유로 다시 정지하려면 새 `--idempotency-key`가 필요하다고 명시 |
| 7 | M-0348:47 | 결과 캐시 키 입도 | 닫힘(제거) | `AGENTS.md:11` |
| 8 | M-0349:54 | 손으로 합친 `schemas.py`의 필드 누락·중복 | 닫힘 | 중복 키 AST 검사 0건(6절), M-0350:43 |
| 9 | M-0349:55 | `validate_task_contract`가 손으로 만든 과제를 거부 | 닫힘 | `작업자-노드/B1-M-0350.md:19`, M-0350:43 |
| 10 | M-0349:56, 결과-C 5.3 | 새 스키마 키워드를 공급자 CLI가 받는지 | **열림** | HIS-10 |
| 11 | M-0349:57, 결과-이음새 5.2의 5 | `_ACTION`에서 지운 16개 필드의 동적 삽입 | 닫힘 | M-0350:43, 결과-이음새 7.2 |
| 12 | M-0349:47 | Codex final 대조의 표본이 5건뿐 | **열림** | HIS-10 |
| 13 | 결과-A 0절, 병합A 4의 5 | 운영 역할 동시 실행 상한 부재 | 수용 | 사용자 결정 4(기준 3절) |
| 14 | M-0350:53, 진단-B4-2:18 | V08: 소실 복구가 queued 시도를 `cancelled`로 종결 | **열림** | HIS-08 |
| 15 | M-0350:42 | 300초 목표 미달 | 수용 | 사용자 결정(안 C) |
| 16 | M-0350:44 | 경량화 뒤 커버리지 미측정 | 수용 | 사용자 결정 |
| 17 | M-0350:51, 진단-B4:66-80 | worktree에서 실제 Lean이 `unavailable` | 수용 | `DO_MATH_KNOWLEDGE_TEST_LEAN` 절차(진단-B4:73-80) |
| 18 | M-0348:73, M-0350:51, 진단-B4-2:27 | 추적표 검사가 추적되지 않는 로컬 보관소에 의존 | **열림** | HIS-17 |
| 19 | 검사 설계 10절 | 메타데이터 보존 손상, 판정 무관 파일, 의도적 변조, 응답 지연 | 수용(문서화) | `references/초기화-효율과-정비.md:93-99` |
| 20 | 검사분류:58-61 | 부분만 읽은 큰 파일에 반복 검사가 남았을 수 있음 | 닫힘(대체) | 2라운드 8영역 전문 조사(`docs/do-math/경량화-설계-2026-09-26.md:5`) |
| 21 | 경량화 설계:179-180 | TST-06 기각, TST-08 보류 | 닫힘(대체) | M-0350:33의 `restore_template` |
| 22 | 경량화 설계:150, 결과-D 5.2 | ENG-24: 투영과 원 인스턴스의 판정이 다름 | **열림** | HIS-09 |
| 23 | 결과-K제품:102, 결과-이음새 2.3 | `payloads.decode`의 S3 변종 처리 미정 | **열림** | HIS-12 |
| 24 | 결과-K제품:101 | 경로 성분 규칙 재사용 | 닫힘 | `scripts/do_math/git_store.py:83`의 `check_path_segment` |
| 25 | 결과-K제품:103 | 압축 JSON 사본 세 곳 | 닫힘 | 결과-이음새 1절 8번 |
| 26 | 결과-K제품:104 | `governance.WORK_ROLES` 동명이의 | 닫힘 | `TASK_WORK_ROLES`(계약 11절 238행) |
| 27 | 결과-K제품:105 | 문서 해시 형태 확인 | 닫힘 | `scripts/do_math/governance.py:104` |
| 28 | 결과-K제품:29 | `resolve_profile` 호출자의 복사 감사 | **열림** | HIS-14 |
| 29 | 결과-K시험 5.3 | 방어 `getattr` 5곳 | 닫힘(그 5곳) | 결과-A:63. 다른 곳의 같은 형태는 HIS-02 |
| 30 | 결과-K시험 5.2 | 순수 픽스처 분기 | 닫힘 | "Pure mixin fixtures" 0건 |
| 31 | 결과-K시험 5.5 | 대기열 병합 때 `import_id` 소실(확인 요청) | **열림** | HIS-11 |
| 32 | 결과-K시험 5.7 | 믹스인 직접 인스턴스 | **열림** | HIS-02에 포함 |
| 33 | 결과-K시험 1절 TST-10 | 저수준 초기화 약 20곳 미전환 | 닫힘(대체) | M-0350:34(`git_init`·`run_cli` 기반으로 약 25개 모듈 이전) |
| 34 | 결과-A:23 | RUN-05·RUN-21 잔여 | 닫힘 | `requeue_recovered_execution` 0건 |
| 35 | 결과-A 5.3 | 운영 역할의 모델 선택 해석 | 닫힘 | 결과-문서 1절 GLOSSARY가 현행 규칙을 서술 |
| 36 | 결과-A:142 | 지운 호스트 승인 제거 보호 시험의 재작성 | 닫힘 | `scripts/tests/test_connection_repairs.py:226`, `:278` |
| 37 | 결과-A 4절 1~6, 결과-B 4절 1·2·4·5·6, 결과-C 4.2절 1~8, 결과-E 4절(직접 적재·pump), 결과-병합A 4절 2~4, 결과-이음새 5.2절, 진단-B4 추적 범위, 작업자-노드 W-git 기존 실패 | 실행하지 않아 미확인이던 시험 관찰 가능 위험 | 닫힘 | M-0350:43 |
| 38 | 결과-B:84 | STO-03 부모 바이트 재사용이 `==`로 판정 | **열림** | HIS-15 |
| 39 | 결과-B:102 | `_academic_evidence`의 `read_many` 부재 처리 | **열림** | HIS-19 |
| 40 | 결과-C:116 | 부르지 않는 경로를 막는 `_available_inputs` 대역 | 영역 밖 | 5절 |
| 41 | 결과-D:81 | RES-07: 생산자 문맥에 `observed_at`가 없을 수 있음 | 닫힘 | `scripts/do_math/engine.py:1877` |
| 42 | 결과-D:98 | RES-17: 제출 미리보기의 반복 파생 | **열림** | HIS-18 |
| 43 | 결과-E:100 | 종료 뒤 마지막 행이 관찰 사실 하나를 늘림 | 수용 | 결과-E 5절 IO-01 |
| 44 | 결과-E:102 | `_observe_running`의 dict 사건 경로 | **열림** | HIS-13 |
| 45 | 결과-E:116 | `close`가 inbox의 `ValueError`를 삼킴 | 수용 | 결과-E 5절 IO-19에 이유가 기록됨 |
| 46 | 결과-F 4절 | `snapshot_report` 오류 동작, `external`의 지연 import | 수용 | 시험 반영(결과-F 4절) |
| 47 | 결과-병합A 4의 1 | 대기 기록의 `retry_at` | 닫힘 | 결과-이음새 2.2. `_ACTION`에서도 지움(7.2) |
| 48 | 결과-문서 5.1 | 입력-소비자.md의 필드 나열 축소 여부 | **열림** | HIS-16 |
| 49 | 결과-문서 5.5 | 결과 파일들의 이음새 계약 변경 요청 | **부분 열림** | HIS-05 |
| 50 | 결과-문서 5.6 | 운영-점검.md의 "비활동" | **열림** | HIS-16 |
| 51 | 결과-이음새 5.1 | `_raw_json`, `_KNOWLEDGE_ID`, 캡처 `origin` 유지 | 수용 | 결과-이음새 5.1. 계약 2.1절 74행 |
| 52 | 진단-B4:93 | `input_ref` 대체값 | 닫힘 | 진단-B4-2 3절. `get('input_ref'` 대체 0건(남은 2건은 비교 읽기) |
| 53 | 진단-B4:64 | `test_review_research.defer()`의 manifest 누락 | 닫힘 | `작업자-노드/B2-M-0350.md:22` |
| 54 | 진단-B4-2:19 | V09·V235 실행 요약 `not_run` | 수용 | 추적표 표준 문구 |
| 55 | B1:31 | `test_lifecycle_currentness` 조각 재배정 | 닫힘 | `scripts/test_categories.py:62-63` |
| 56 | B1:22 | F2·F3 템플릿 분리 미실시 | 수용 | 얻는 것이 run 1회라고 기록됨 |
| 57 | B2:21, :29 | 스키마 공유 노드 별칭 결함 | 닫힘(국소), 구조적 재발 방지 **열림** | `scripts/do_math/review_cycle.py:626-634`, `review_engine.py:1144-1146`. 구조 문제는 HIS-04 |
| 58 | W-debt:36 | 관찰 하나의 소유 루프 비용이 도착 간격보다 큼 | **열림** | HIS-20 |
| 59 | W-debt:37, W-eng:36, W-fix:43, W-git:60 | 병렬 작업자 노드 번호 충돌 | 닫힘(통합), 잔재 **열림** | 통합 노드는 `기억/layer1/M-0350.md` 하나다. 추적된 작업자 노드의 frontmatter 문제는 HIS-07 |
| 60 | W-eng:31 | `_refresh_readiness`·`discover_lean` 미감축 | 수용 | 작업자가 이유를 기록했다 |
| 61 | W-fix:25 | 경로 키 캐시를 `forget_repository_caches`에 더하는 규칙 | **열림(위반)** | HIS-03 |
| 62 | W-fix:41 | `test_formal_requires…` 느려짐 미재측정 | 수용 | M-0350 측정 생략 결정 |
| 63 | W-git:52-58 | DST 오프셋, freshen 없음, 저장소 로컬 설정 무시, `GIT_AUTHOR_*` 무시 | 수용(코드 주석) | `scripts/do_math/git_store.py:257-263`, `:275`, `:335-339` |

### 3.2 후보

#### HIS-01 이음새 정본이 스킬 밖 날짜 문서에만 있고 스킬에서 도달할 수 없다
- 검토: 1
- 종류: 문서
- 좌표: `docs/do-math/검사-경량화-이음새-계약.md:161-244`(11절 S10 표); `AGENTS.md:1-11`; `scripts/do_math/repository.py:69`, `submission.py:44`, `:118`, `:1384`, `planning.py:536`, `review_cycle.py:314`, `review_engine.py:1167`, `codex_adapter.py:144`; `scripts/tests/test_native_final_submission.py:206`, `test_submission_flow.py:94`, `:450`
- 현상: 「이음새마다 정의는 하나」의 정본 목록(74개 정본 행)과 커널 규칙(1~3절)은 `docs/do-math/`의 날짜 붙은 경량화 산출 문서에 있다. 스킬 트리(`.claude/skills/do-math/`) 어디에도 이 문서를 가리키는 곳이 없다. 스킬의 개발 원칙 `AGENTS.md`도 이음새 원칙과 검사 위치 원칙(기준 2절 1·2항)을 담지 않는다. 그런데 제품 코드 주석 8곳과 시험 주석 3곳은 "contract S3"를, `codex_adapter.py:144`는 "R22"를 근거로 든다. 이 이름들은 스킬 밖 문서의 절 번호다.
- 근거: `Grep "검사-경량화-설계|경량화-설계-2026-09-26|검사-경량화-이음새-계약|경량화-조사-2026-09-26|시험-경량화-2026-09-26"`을 `.claude/skills/do-math`에 돌리면 0건이다. `grep -rnE "\b(S[1-9]|S10)\b|\bR[0-9]{1,2}\b"`(scripts의 py)에서 관련 일치는 12건이다. 그 가운데 `knowledge.py:338`의 S0·S1은 다른 개념이라 뺐다. `AGENTS.md`는 11행 전체에 "이음새·공유·커널·정본"이 없다. `.agents/` 미러는 스킬 트리만 복제하므로 `docs/`가 따라가지 않는다.
- 제안: 이음새 계약 1~3절의 규칙과 11절 표를 스킬 안의 정본 하나로 옮긴다. 예를 들면 `references/이음새-정본.md`다. 그리고 `AGENTS.md` 개발 원칙에 두 문장과 링크를 더한다. 하나는 "두 모듈이 같은 규칙을 쓰면 정본 하나를 참조한다"이고, 다른 하나는 "검사 함수는 하나, 생산자·수신자 양쪽에서 실행"이다. 코드 주석의 "contract S3"는 새 문서의 절 이름으로 바꾼다. `docs/do-math/검사-경량화-이음새-계약.md`는 HIS-05에 따라 역사 기록으로 남긴다.
- 실익: 사라지는 것은 정본이 스킬 설치·미러에 포함되지 않는 틈, 그리고 개발자가 정본 목록을 모른 채 사본을 새로 만드는 여지다. 2라운드가 없애려던 바로 그 원인이다. 코드 주석 12곳의 참조 대상도 설치본 안에 생긴다.
- 비용과 위험: 문서 1개 신설(약 90행 이동), `AGENTS.md` 2~3행, 주석 12곳 수정, 미러 재생성이 든다. 새 상태·수명·복구 규칙은 없다. 문서 수치 정본 원칙(결정 5)과 충돌하지 않는다. 표는 수치가 아니라 이름과 위치다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-02 시험 호스트를 위한 제품 방어가 `_init_process_state` 원칙 밖에 15곳 남았고, 검사 경량화도 둘을 새로 더했다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/engine.py:519-534`(`_init_process_state`), `:1016`, `:1030`, `:2488`, `:3665`, `:4053`, `:4244`; `scripts/do_math/lifecycle_engine.py:89`, `:172`, `:341`, `:725`, `:730`, `:732`, `:811`, `:813`; `scripts/do_math/scheduler.py:46`; `scripts/tests/test_decision_basis.py:18`, `:61`; `scripts/tests/test_questions.py:59`, `:73`, `:91`, `:166`
- 현상: 2라운드 TST-01은 프로세스 상태 초기화를 `_init_process_state` 하나로 모았다. 시험용 방어 `getattr` 14곳(결과-K시험 1절)과 추가 5곳(결과-A:63)도 지웠다. 그러나 같은 형태가 15곳 남았다. 형태는 둘이다.
  - 초기화 밖에서 게으르게 생기는 프로세스 속성을 `getattr(self, 이름, 기본값)`으로 읽는다. 대상은 `_feedback_delivered`, `_retrying_publication`, `_next_lean_discovery`, `_external_preparation_binding`(3곳), `_goal_audit_contract`, `_clock_failure`, `_goal_basis_memo`다.
  - `ResearchEngine`이 늘 가진 메서드를 없을 때를 대비해 감싼다. 대상은 `getattr(self, '_governance_owner_handlers', lambda: None)()` 2곳, `hasattr(self, '_solution_basis')` 2곳, `getattr(self, '_academic_evidence', None)` 2곳이다. `ResearchEngine`은 `GovernanceEngineMixin`과 `AcademicEngineMixin`을 모두 상속한다(`engine.py:499`). 따라서 뒤의 기본값은 믹스인을 단독으로 쓰거나 `SimpleNamespace` 호스트를 쓰는 시험에서만 도달한다.

  15곳 가운데 둘(`scheduler.py:46`의 `_goal_basis_memo`, `engine.py:2488`의 `_next_lean_discovery`)은 검사 경량화 `8d2ffd0`가 새로 더한 것이다. 원칙을 세운 경량화가 같은 형태를 만들고, 다음 라운드가 목록에 있던 것만 지운 셈이다.
- 근거: `grep -rn "getattr(self, *['\"]_" do_math`는 14건을 반환했고, 그 가운데 13건이 관련이다. 제외한 1건은 `git_store.py:545`로, 5절에 적었다. `grep -rn "hasattr(self" do_math`는 5건을 반환했고 관련은 2건이다(`lifecycle_engine.py:730`, `:811`). `git log -S`로 도입 커밋을 확인했다. `7d2597e`이 10곳, `fe59ca0`가 1곳(`_goal_audit_contract`), `8d2ffd0`가 2곳이다. 결과-K시험 5.7절은 믹스인 직접 인스턴스 6곳을 "후속으로 `bare_engine`으로 바꿀 후보"로 남겼고, 원문에 그대로 있다.
- 제안: 게으른 프로세스 속성 8개는 `_init_process_state`에서 초기화하거나 `_documents`처럼 `cached_property`로 바꾸고, `getattr` 기본값을 지운다. 메서드 방어 6곳은 직접 호출로 바꾼다. 남은 믹스인 직접 인스턴스 6곳과 `SimpleNamespace` 호스트는 `research_fixtures.bare_engine`으로 옮긴다. 시험 원칙 "구형 fixture를 살리려고 제품 코드에 예외를 넣지 않는다"(`AGENTS.md:7`)를 끝까지 적용하는 일이다.
- 실익: 제품 방어 15곳이 사라진다. 속성 초기화 지점이 하나가 되므로 새 속성을 추가할 때의 기준도 하나가 된다. 방어가 가리는 실제 초기화 누락(예: 새 엔진 경로에서 속성이 없음)의 여지도 사라진다.
- 비용과 위험: `engine.py`, `lifecycle_engine.py`, `scheduler.py` 약 17행, 시험 2개 모듈과 SimpleNamespace 호스트(예: `test_control_shapes.py:174`)의 수정이 든다. 새 상태는 없다. `_clock_failure`는 초기값이 `None`이어야 의미가 보존된다(`lifecycle_engine.py:89`).
- 기능·커버리지 영향: 없음(시험이 같은 성질을 현행 엔진으로 단언)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-03 경로 키 프로세스 캐시 8개 가운데 4개만 시험 복원 때 비워진다
- 검토: 1
- 종류: 비대
- 좌표: `scripts/tests/research_fixtures.py:783-795`(`forget_repository_caches`); `scripts/do_math/repository.py:39`, `:97`, `:111`, `:133-134`; `scripts/do_math/planning.py:32`; `scripts/do_math/submission.py:108`; `scripts/do_math/engine.py:74`; `임시/시험-경량화-2026-09-26/작업자-노드/W-fix-M-0351.md:25`
- 현상: 세 경량화가 저장소 경로(`git_dir`)를 키로 하는 프로세스 전역 캐시를 차례로 더했다.
  - `8d2ffd0`: `repository.VERIFIED_ARTIFACTS`, `_VALIDATED_READS`, `planning._VALID_ARTIFACTS`
  - `379a171`: `submission._ISSUED_INPUTS`
  - `9b434f4`: `repository._RETAINED_READS`, `_ARTIFACT_FACTS`, `_PUBLISHED_PARENTS`, `engine._CONTROL_READERS`

  시험 템플릿은 같은 절대 경로에 새 저장소를 복원한다. 그래서 `forget_repository_caches`가 제품의 비공개 이름 넷을 직접 열거해 비운다. W-fix는 "제품에 경로 키 캐시가 새로 생기면 `forget_repository_caches`에 더해야 한다"는 규칙을 남겼다. 그런데 같은 라운드의 W-eng가 더한 네 캐시는 목록에 없다. 이 넷의 효과는 다음과 같다.
  - `_CONTROL_READERS`는 `(경로, 인스턴스)`마다 `ResearchRepository` 객체를 재사용한다. 복원된 저장소에 앞 시험의 객체가 쓰인다.
  - `_ARTIFACT_FACTS`는 바이트를 들고 있다. 따라서 복원 뒤 저장 바이트를 바꾸는 변조 시험이 가려질 수 있다. `VERIFIED_ARTIFACTS`가 지워져야 하는 것과 같은 이유다(진단-B4:41).
- 근거: `grep -n "^_[A-Z_]* *[:=].*\({}\|dict\|OrderedDict"`와 `lru_cache`·`@cache` 검색으로 전역 캐시 21건을 찾았다. 그 가운데 `git_dir` 또는 저장소 경로를 키로 하는 것이 8건이다. 도입 커밋은 `git log -S "<선언문>"`으로 확인했다. `forget_repository_caches`의 대상 튜플은 `research_fixtures.py:792-793`의 넷이다.
- 제안: 경로 키 캐시의 목록과 비우기를 제품의 한 곳이 소유하게 한다. 가장 단순한 형태는 `repository`에 모듈 상수 `PATH_KEYED_CACHES`(캐시 객체 튜플)를 두는 것이다. 다른 모듈의 캐시도 여기에 등록하고, 시험 도우미는 이 상수만 순회한다. 이러면 새 캐시를 더할 때 등록을 잊는 일이 선언 옆에서 드러난다. 또는 캐시마다 키가 내용 주소(OID·sha256)인지 먼저 판정하는 방법이 있다. 내용 주소라서 복원과 무관하게 옳은 캐시는 목록에서 빼고, 이유를 선언 옆 주석에 한 줄 둔다.
- 실익: 시험이 제품 비공개 이름 넷을 직접 건드리는 이음새 하나가 사라진다. 빠진 네 캐시로 인한 시험 사이 누수 여지(변조 시험 가림, 저장소 객체 재사용)도 닫힌다.
- 비용과 위험: 제품 1~2행과 시험 도우미 3행이 바뀐다. 새 수명·복구 규칙은 없다. 비우는 범위가 넓어지면 템플릿 복원 뒤 첫 적재가 조금 느려질 수 있다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 네 캐시가 빠진 사실은 확인했다. 실제 누수로 시험 결과가 바뀌는지는 확인하지 못했다. `_ARTIFACT_FACTS`를 채운 뒤 같은 경로를 복원하고 바이트를 바꾸는 시험 하나로 확정된다.

#### HIS-04 "독립 스키마"를 돌려주는 함수가 공유 노드를 사본 안에서도 공유한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/contracts.py:120-121`(`TEXT`, `REFS`), `:212-219`(`schema_for`, docstring "Return an independent JSON Schema"), `:100-110`(`with_integration_schema`의 `copy.deepcopy`), `:237`(제자리 대입); `scripts/do_math/review_cycle.py:626-634`; `scripts/do_math/review_engine.py:1144-1146`
- 현상: 2라운드는 비지 않은 텍스트 스키마를 `contracts.TEXT` 하나로 모았다. wire·저장 과제·제출·통합 스키마가 이 모듈 전역 dict를 직접 싣는다. 역할 스키마는 `copy.deepcopy`로 사본을 만드는데, deepcopy는 memo 때문에 한 원본 안에서 여러 번 쓰인 노드를 사본 안에서도 한 객체로 둔다. 그래서 사본의 한 필드를 제자리에서 고치면 같은 노드를 쓰는 다른 필드가 모두 바뀐다. 3라운드가 찾은 제품 결함 1건(M-0350:48, 보충 조사 제출이 전부 거부됨)이 이 기전이었다. 수리는 두 곳의 국소 대응이다. `research_schema`는 필드마다 사본을 만들고, `_review_research_schema`는 노드를 새로 묶는다. 두 곳 모두 "공유 노드를 고치지 말라"는 주석으로 규칙을 적었다. 구조적 보장은 없다.
- 근거: 파이썬 한 줄 확인(6절)에 따르면 `contracts.schema_for(role)`가 돌려준 스키마 10개 모두에 사본 안에서 공유되는 dict 노드가 3~6개 있다. `contracts.py:237`은 `schema_for` 결과의 `candidates` 노드를 제자리에서 고친다. 지금은 이 노드가 공유되지 않아 안전하다(같은 확인에서 `candidates shared: False`). `grep`으로 찾은 스키마 제자리 대입은 `contracts.py:109`(재바인딩, 안전), `:132`(모듈 적재 시 한 번), `:156`(공유 노드 대입), `:237`이다.
- 제안: 역할 스키마를 "독립 사본"으로 만드는 곳에서 deepcopy 대신 공유를 끊는 복제를 한 함수로 쓴다. 예를 들면 `json.loads(json.dumps(schema))`다. 스키마는 JSON 값이므로 의미가 같고, 모든 노드가 서로 다른 객체가 된다. 대상은 `schema_for`, `with_integration_schema`, `research_schema`다. 이렇게 하면 `review_engine.py:1144`의 재바인딩 규칙과 `review_cycle.py:627`의 필드별 사본이 필요 없어진다. 대안은 공유 노드가 없음을 단언하는 unit 시험 하나다.
- 실익: 2라운드의 공유화가 만든 별칭 결함이 재발할 여지를 구조로 없앤다. 국소 규칙 주석 두 곳도 지울 수 있다.
- 비용과 위험: 1~3곳 교체와 선택적 시험 1개가 든다. 새 상태는 없다. 스키마 생성 비용은 JSON 왕복이 deepcopy와 비슷하다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. 기전과 현재 공유 노드 수는 실행으로 확인했다. 재발 가능성 자체는 앞으로의 편집에 달렸다.

#### HIS-05 이음새 계약 문서에 현행 정본과 끝난 작업자 지시가 섞여 있고, 낡은 서술이 남았다
- 검토: 2
- 종류: 낡음
- 좌표: `docs/do-math/검사-경량화-이음새-계약.md:1-3`(제목 "G1~G4 공통"), `:11-21`(0절), `:69`, `:83-85`, `:100-109`, `:117-121`, `:127-129`, `:145-159`
- 현상: 기준 2절 1항과 M-0349:59는 이 문서를 현행 정본으로 가리킨다. 그러나 문서 대부분은 1라운드 병렬 작업자(G1~G4)에게 내린 지시다. 현재와 어긋나는 서술은 다음과 같다.
  - 0절: 브랜치 `do-math-check-kernel`은 없고(`git branch -a`), 커널 커밋 `fe44b61`은 main에서 도달할 수 없다(`git merge-base --is-ancestor` 결과 unreachable).
  - 2.1절 69행: "worker 능력 식별의 파일 범위가 `control_transport`와 `file_io`"라고 적었다. 현재 식별 모듈은 어댑터별로 6개와 9개다(`codex_adapter.py:332`, `claude_adapter.py:28`). 결과-E:81이 수정을 요청했으나 반영되지 않았다.
  - 3절 83행: 번들 불변 검사의 위치를 "현 396-397행"이라 적었다. 현재는 `git_store.py:516-517`이다. 85행은 `artifact_verified`의 서명에서 `size`를 뺐는데, 83행과 코드(`repository.py:47`)는 `size=None`을 가진다.
  - 4절 100~109행: head 이동 지점이 1라운드 기준 좌표이고, 2라운드의 `_reload`(`engine.py:818`)가 빠졌다. "변경 세대 카운터(R12): G3가 구현한다면"은 포기된 설계이며 코드에 0건이다. 결과-B:66이 두 수정을 요청했으나 반영되지 않았다.
  - 6절: 픽스처 규칙이 G2~G4 대상이다. 결과-K시험:140이 요청한 시험 기반 정의(`bare_engine` 등)는 없다.
  - 7절 128~129행: `payloads.fingerprint`와 `repair_execution.installation_fingerprint`를 "정리할 것"으로 적었다. 두 이름은 코드에 이미 0건이다.
  - 9·10절: G1~G4 작업자의 커밋 전 점검과 반환 항목이다.

  반면 11절 표는 정확하다(6절의 두 검사에서 불일치 0건).
- 근거: 위 좌표의 원문 대조와 `grep`(`_state_generation` 0건, `installation_fingerprint` 0건, `def fingerprint`는 `file_io`의 두 함수뿐, `_validate_artifact_changes`의 현재 행)을 썼다. 결과-문서 5.5절은 "이음새 계약 문서 변경은 통합자 몫으로 두었다"고 적었다.
- 제안: HIS-01과 함께 처리한다. 현행 정본(1~3절의 규칙, 11절 표, 4절의 "메모리 상태에는 head 키를 쓰지 않는다" 규칙)은 스킬 안 정본으로 옮긴다. 이 문서는 첫머리에 "1라운드 작업 계약의 역사 기록, 현행 정본은 …"이라는 표지를 두고 본문은 그대로 동결한다. HIS-01을 채택하지 않는다면 최소한 위의 낡은 서술 일곱 곳을 고친다.
- 실익: 정본 문서 안의 거짓 서술(없는 브랜치, 틀린 행 번호, 포기된 카운터, 이미 지운 이름)이 사라진다. 한 문서가 "작업자 지시"와 "현행 계약"을 겸하는 지위 혼재도 끝난다.
- 비용과 위험: 문서 편집만 든다. 코드는 바뀌지 않는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-06 두 설계 문서와 검사분류가 구현 전 상태를 현재형으로 말하고, 지워진 작업 공간을 근거로 든다
- 검토: 2
- 종류: 낡음
- 좌표: `docs/do-math/검사-경량화-설계-2026-09-26.md:3`, `:54`, `:180`, `:195`, `:238`, `:245`, `:429`; `docs/do-math/경량화-설계-2026-09-26.md:3`, `:5`; `docs/do-math/검사-경량화-설계-2026-09-26-검사분류.md:3`
- 현상: 세 문서에는 지위 표지가 없다. 그래서 역사 기록이라는 사실을 독자가 알 수 없다. 현재와 어긋나는 서술은 다음과 같다.
  - 검사 설계 3행: "코드와 계약 문서는 아직 바꾸지 않았다"고 적었다. `8d2ffd0`가 구현했다.
  - 245행 R12 "변경 세대 카운터로 바꾼다": 포기했다(M-0348:55). `published_state`로 대체되었다.
  - 238행 R4 "부모 head의 검증 집합을 승계": `VERIFIED_ARTIFACTS`로 대체되었다(M-0348:57).
  - 180행: "`lake env`는 1초 안팎이므로 유지"라고 적었다. 실측은 2초였고 메모로 바뀌었다(`formal.py:190-191`, M-0348:62).
  - 195행: "게시 직후" 평가를 가정했다. 매 바퀴 게시로 바뀌었다(`scheduler.py:34-40`).
  - 54행과 429행: 측정 근거인 작업 공간 `.skill-workspace/nat-add-zero-fresh-20260926/`에 대해 "지우지 않았다", "종결 뒤에도 파일로 남는다"고 적었다. 이 폴더는 결정 1로 삭제되었다(M-0349:16. 현재 `.skill-workspace/` 목록에 없음).
  - 경량화 설계 5행: "후보의 좌표…는 조사 파일이 정본"이라 적었다. 조사 파일 좌표는 `8d2ffd0` 기준이라 현재 좌표가 아니다.
- 근거: `ls C:/math/.skill-workspace/`(목록에 `nat-add-zero-*` 없음), `grep -c _state_generation` 0, M-0348:54-62. 스킬 트리에서 이 문서들을 가리키는 곳은 없고, `traceability.json:15978`, `:24588`은 결정 근거로 경량화 설계 1.4·1.5절을 인용한다.
- 제안: 세 문서 첫머리에 한 줄 표지를 둔다. 문구는 "구현 완료(커밋 …)된 설계의 역사 기록이다. 현행 계약은 스킬 문서와 이음새 정본이며, 구현 중 바뀐 결정은 M-0348·M-0349를 본다"이다. 54·429행 옆에는 "이 작업 공간은 2026-09-26 결정 1로 삭제됨"을 괄호로 더한다. 본문은 고치지 않는다. 추적표가 결정 근거로 인용하므로 역사 기록으로 보존하는 편이 맞다.
- 실익: 역사 기록을 현행 설계로 오독할 여지가 사라진다. 특히 R12·R4·`lake env`처럼 구현이 설계와 다르게 끝난 곳이 문제다. 없는 자료를 근거로 가리키는 서술도 바로잡힌다.
- 비용과 위험: 문서 세 곳에 1~3행을 더한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-07 추적되는 임시 자료가 자기를 "Git 제외"라 적고, 중복 노드 ID와 작문 중간 산출물을 담는다
- 검토: 2
- 종류: 잔재
- 좌표: `임시/시험-경량화-2026-09-26/작업자-노드/B1-M-0350.md:10`, `B2-M-0350.md:10`, `B3-M-0350.md:10`, `B4-M-0350.md:10`, `B4-M-0351.md:10`, `W-debt-M-0351.md:10`, 9개 파일의 frontmatter 2행; `임시/시험-경량화-2026-09-26/작문/`(3개), `작문-B4/`(4개, `run1.log` 91,043바이트)
- 현상: `9b434f4`가 `임시/시험-경량화-2026-09-26/`을 `git add -f`로 추적했다. 그런데 작업자 노드 여섯 개는 "Git 제외 경로라 정리로 사라질 수 있다", "Git 무시 대상인 로컬 보관"이라고 자기 지위를 적는다. 추적된 지금은 거짓이다. 작업자 노드 9개의 frontmatter는 `id: M-0350`(6개)이나 `id: M-0351`(3개)이다. 통합 노드는 `기억/layer1/M-0350.md` 하나이고, `M-0351`은 아직 없는 다음 번호다. 다음 기억 노드가 M-0351을 받으면 같은 ID를 가진 추적 파일이 넷이 된다. 또 `작문/`·`작문-B4/`의 write-for-reader 중간 산출물(합의·독자·대조 JSON)과 시험 실행 로그 `run1.log`가 함께 추적되었다. M-0350:101이 밝힌 추적 대상(계약, 분석, 진단, 작업자 노드)에는 이것들이 없다.
- 근거: `git ls-files 임시/시험-경량화-2026-09-26`에서 22건을 확인했다. `.gitignore:50-56`는 `임시/*/*`를 기본 무시하고 `git add -f`로 추적하는 규칙이다. `ls 기억/layer1/ | tail`에 `M-0350.md`가 마지막으로 나온다. 같은 성격의 `임시/경량화-조사-2026-09-26/작문/`은 추적되지 않는다(`git ls-files`에 없음). 두 라운드의 처리가 다르다.
- 제안: 세 가지를 한다.
  - 작업자 노드 여섯 개의 지위 문장은 고치지 않고, 폴더에 한 줄 README를 둔다. 문구는 "추적된 원문 사본. 본문의 'Git 제외' 서술은 작성 시점 기준"이다. 작업자 원문을 보존한다는 취지를 지키기 위해서다.
  - frontmatter의 `id:` 줄은 `worker_id: B1` 식으로 바꾸거나, 파일을 `.md.txt`처럼 기억 노드로 오인되지 않는 형태로 둔다.
  - `작문/`·`작문-B4/` 7개 파일은 추적에서 뺀다(`git rm --cached`). 2라운드와 같은 처리다.
- 실익: 추적 파일 안의 거짓 지위 서술이 무력화된다. 기억 ID 충돌 여지가 사라진다. 증거 가치 없는 중간 산출물 약 101KB도 추적에서 빠진다.
- 비용과 위험: 파일 1개 추가, frontmatter 9곳 수정, 추적 해제 7개가 든다. 새 상태는 없다. 기억 도구가 `임시/`를 훑지 않는다면 ID 충돌은 실제 해가 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. ID 충돌의 실제 해는 추정이며, `memory-harness`의 노드 탐색 범위를 확인하면 확정된다.

#### HIS-08 V08 열린 질문: 권한 기록 전 queued 시도를 `cancelled`로 종결하는 것이 맞는지 판정되지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/engine.py:1645-1653`; `docs/do-math/implementation-v5/traceability.json`의 `vectors.V08.gaps[1]`; `기억/layer1/M-0350.md:53`; `임시/시험-경량화-2026-09-26/진단-B4-2.md:18`
- 현상: 소실 복구는 권한 기록 전 queued 시도를 `end_preparation(..., cancelled=True)`로 종결한다. 원천 기대(V08)는 `start_failed`다. 추적표는 이를 "판정되지 않았다"는 gap으로 적었고 M-0350은 "열린 질문"으로 남겼다. 2라운드 전에도 같은 동작이었다.
- 근거: `engine.py:1645`의 `if state == "queued":` 분기와 `:1653`의 `cancelled=True`를 확인했다. `traceability.json` V08의 `mapping`은 `partial`이고, gap 문장은 원문 그대로다.
- 제안: 사용자나 통합자가 한 문장으로 판정한다. 기준은 "권한 기록 전 소실된 시도는 시작 실패인가, 준비 취소인가"다. `cancelled`가 맞으면 V08 gap을 "설계 변경(분류 c)"으로 닫고 근거를 적는다. `start_failed`가 맞으면 `engine.py:1653`의 종결 사유와 해당 시험을 바꾼다.
- 실익: 추적표의 확인된 미연결(분류 a) 1건이 닫힌다. 실행 소실 복구의 종결 의미가 하나로 정해진다.
- 비용과 위험: 판정만 하면 문서 한 곳이 바뀐다. 동작을 바꾸면 `engine.py` 1행과 복구 시험 몇 개가 바뀐다. 새 상태는 없다.
- 기능·커버리지 영향: 판정에 따라 없음 또는 있음(종결 상태 값)
- 사용자 결정 관련: 없음(판정 대기)
- 확신도: 확인

#### HIS-09 ENG-24: 착수 판정과 계약 검토 기반이 호출자에 따라 투영과 원 인스턴스로 갈린다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/initialization.py:103-106`(`governance_working_view`); `scripts/do_math/lifecycle_engine.py:941`, `:969-998`; `scripts/do_math/engine.py:989`, `:1812`, `:2075`, `:3134`, `:3887`; `scripts/do_math/decision_engine.py:70`, `:113`, `:128`, `:149`; `임시/경량화-조사-2026-09-26/결과-D.md:89-93`
- 현상: 그룹 D는 투영(`{**instance, **governance_view(instance)}`)과 원 인스턴스가 `task_ready` 판정과 `capture_task_basis` 해시에서 다름을 원문으로 보였다. 투영은 `/goal_revision`·`/policy_revision`을 노출하고 원 인스턴스는 그렇지 않다. 그래서 인스턴스 가족 조건은 투영에서만 뜻을 가지며, 원 인스턴스에서는 `evaluation_error`가 된다. 계약 검토 기반도 봉인 지점에 따라 해시가 달라진다. 그룹 D는 "어느 쪽이 맞는 입력인지는 설계 판단이 필요하다"며 바꾸지 않았고, 그 뒤 판단 기록이 없다. 현재도 `lifecycle_engine.py:969-998`은 `query_instance`(투영)로, `engine.py`와 `decision_engine.py`의 9곳은 `self.instance`로 판정한다.
- 근거: `grep -rn "task_ready(\|ready_task_ids(\|capture_task_basis(\|contract_review_current("`는 20건을 반환했고, 그 가운데 판정 입력이 있는 호출 13곳을 분류했다. `governance_working_view` 사용처는 7곳이다.
- 제안: 판정 입력을 하나로 정한다. 그룹 D의 분석대로라면 인스턴스 가족 조건이 투영에서만 뜻을 가지므로 투영이 후보다. 정한 입력을 `planning` 쪽의 한 함수(예: `evaluation_instance(instance)`)로 두고, 13곳이 그것을 부르게 한다. 원 인스턴스가 맞다면 `EXPOSED_FIELDS['instance']`에서 두 포인터를 뺀다.
- 실익: 같은 과제가 소유 루프와 엔진 경로에서 다른 착수 상태를 얻는 여지가 사라진다. 계약 검토 기반이 봉인 지점에 따라 달라 검토가 헛되이 낡는 여지도 사라진다. 이음새 원칙(정의 하나)의 미적용 1건이 닫힌다.
- 비용과 위험: 판정 입력 함수 1개와 호출부 13곳이 바뀐다. 투영을 택하면 원 인스턴스로 봉인한 기존 계약 검토 기반이 한 번 낡을 수 있다. 결정 1로 옛 인스턴스가 없으므로 영향은 새 인스턴스뿐이다.
- 기능·커버리지 영향: 있음(인스턴스 가족 조건의 판정이 한 가지로 정해짐)
- 사용자 결정 관련: 없음(설계 판정 대기)
- 확신도: 추정. 호출 분기는 확인했다. 두 입력의 판정 차이가 실제 과제에서 나타나는지는 `record_field_equals` 인스턴스 조건을 가진 과제 하나를 두 경로로 평가해 보면 확정된다.

#### HIS-10 실제 공급자 CLI로만 닫히는 두 위험을 확인할 장치가 없다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/probe_cli.py:17-25`; `scripts/do_math/preflight.py:23`(`_check_schema_pair`); `기억/layer1/M-0349.md:47`, `:56`; `임시/경량화-조사-2026-09-26/결과-C.md:161-163`, `결과-E.md:22`, `:98`
- 현상: 2라운드는 역할 출력 스키마에 새 키워드(`pattern`, `enum`, `anyOf`+null, `minItems`·`maxItems`, `const`)를 넣었다(REV-01·07·15, RUN-19). 또 Codex 일반 수집에 `final.txt`와 종료 직전 `agent_message`의 바이트 대조를 넣었다(IO-05). 앞의 것이 틀리면 해당 역할 호출이 모두 스키마 거부로 실패하고, 뒤의 것이 틀리면 모든 Codex 일반 실행이 `final_response_mismatch`로 실패한다. 3라운드의 전체 실행은 가짜 어댑터만 쓰므로 둘을 확인하지 않는다. `probe_cli.py`는 실제 CLI를 부르지만 자체 최소 스키마(`status`, `nonce`)만 보낸다. `preflight`는 메타스키마 적합성만 본다. Codex 대조는 보존된 실행 5건으로만 확인되었다(M-0349:47). `--output-schema`를 쓰는 비결합 실행은 확인 표본에 없다(결과-E:98).
- 근거: `probe_cli.py:22`의 `schema = {"type": "object", ...}`는 고정 최소 스키마다. `grep -n "schema_for\|stage_schema\|role_output" probe_cli.py` 결과는 0건이다.
- 제안: `probe_cli.py`에 선택 인자 하나를 둔다(예: `--role <역할>`). 실제 역할 스키마(`contracts.schema_for` 또는 `review_cycle.stage_schema`)를 보내고, 수락 여부와 final 대조 결과만 기록하게 한다. 통합자가 공급자마다 한 번 돌려 두 위험을 닫는다. 새 도구를 만들지 않고 기존 실호출 경로에 스키마만 바꿔 넣는 형태다.
- 실익: 운전 첫 실행에서야 드러날 전면 실패 두 종류를 개발 시점에 닫는다. 이후 스키마를 바꿀 때도 같은 확인을 반복할 수 있다.
- 비용과 위험: `probe_cli.py` 약 10~20행과 실호출 비용(공급자당 수 회)이 든다. 새 상태는 없다.
- 기능·커버리지 영향: 있음(실제 CLI 수용 확인이 생김)
- 사용자 결정 관련: 없음
- 확신도: 확인. 장치가 없다는 점은 확인했다. 두 위험이 실제로 일어나는지는 미확인이며, 제안한 실행으로 확정된다.

#### HIS-11 `research_preparation` 요청의 `import_id`는 생산자만 있고 소비자가 없다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/governance_engine.py:184`; `scripts/do_math/engine.py:638`; `scripts/do_math/governance_engine.py:136`, `:172-174`; `scripts/do_math/engine.py:3576-3578`(`_enqueue` 비교 키); `임시/경량화-조사-2026-09-26/결과-K시험.md:191-195`
- 현상: 헌장 적용 뒤 `research_preparation`을 `import_id=import_id`와 함께 대기열에 넣는다(`governance_engine.py:184`). 대기 행동의 `import_id`를 읽는 곳은 세 곳이고, 모두 `intent_interpretation` 전용이다. `engine.py:638`은 check 단계만, `governance_engine.py:136`은 해석 입력만, `:174`는 `role == 'intent_interpretation'`만 본다. `_enqueue`의 비교 키에 `import_id`가 없어서, 같은 역할의 요청과 병합되면 값이 사라진다. 결과-K시험은 이를 "확인 요청, 결함 판정 아님"으로 통합자에게 넘겼고, 그 뒤 처분 기록이 없다. 2라운드 원칙 "생산자 없는 필드는 지운다"의 반대 방향, 곧 소비자 없는 필드다.
- 근거: `grep -n "import_id" engine.py context_store.py planning.py scheduler.py submission.py`는 1건(`engine.py:638`)을 반환했다. `governance_engine.py`의 `import_id` 일치 13건 가운데 대기 행동의 값을 읽는 것은 `:136`, `:174` 둘이다. `grep -rn "import_id" tests | grep -i preparation`은 0건이다.
- 제안: `governance_engine.py:184`에서 `import_id=import_id`를 지운다. 후속 준비가 어느 해석 적용에서 왔는지 기록이 필요하면 `reason` 문자열이나 `event_refs`로 표현한다. `event_refs`는 병합 때 합쳐진다(`engine.py:3596`).
- 실익: 소비자 없는 필드 하나와 병합 소실의 여지가 사라진다. 조사가 남긴 확인 요청도 닫힌다.
- 비용과 위험: 제품 1행이 바뀐다. `_ACTION` 스키마의 `import_id`는 `intent_interpretation`이 쓰므로 유지한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-12 `payloads.decode`가 S3 소비 규칙을 따로 구현하는데, 계약은 이를 예외로 적지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/payloads.py:155`, `:172`, `:180`; `docs/do-math/검사-경량화-이음새-계약.md:87`; `임시/경량화-조사-2026-09-26/결과-이음새.md:60`
- 현상: 계약 3절 87행은 `sealed_bytes`를 "이미 대조했으면 생략, 아니면 대조" 규칙의 정본으로 정하고 "호출자는 이 함수를 부르고 규칙을 다시 구현하지 않는다"고 적는다. `payloads.decode`는 `artifact_verified`와 `mark_artifact_verified`를 직접 조합해 같은 규칙의 변종을 구현한다. 표시 시점을 정규 JSON 검사 뒤로 미루기 때문이다. 결과-이음새는 "커널 API 확장 여부는 이음새 계약 작성 때 정한다"고 미뤘다. 11절 작성 뒤에도 그 결정은 기록되지 않았다.
- 근거: `grep -n "mark_artifact_verified\|artifact_verified\|sealed_bytes" payloads.py`는 3건을 반환했고, `sealed_bytes`는 0건이다.
- 제안: 둘 중 하나로 닫는다. (a) `sealed_bytes`에 표시 전 검사 콜백 인자(예: `accept=`)를 두고 `payloads.decode`가 그것을 쓴다. (b) 계약 3절에 "`payloads.decode`는 정규 JSON 검사 뒤 표시하는 유일한 변종"을 한 줄로 적는다. (b)가 단순하고, 표시 시점이 다른 규칙이라는 결과-이음새의 판단과도 맞는다.
- 실익: 정본 규칙과 실제 코드 사이의 미기록 예외가 사라진다.
- 비용과 위험: (b)는 문서 1행, (a)는 커널 인자 하나와 호출부 1곳이다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-13 `_observe_running`의 dict 사건 경로는 시험만 쓴다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/engine.py:2786-2792`; `scripts/do_math/model_runner.py:178`; `scripts/tests/test_observations.py:388`; `scripts/tests/test_redesign_ENGINE.py:1387`, `:1392`; `임시/경량화-조사-2026-09-26/결과-E.md:102`
- 현상: `_observe_running`은 `event: dict | ObservationBatch`를 받고, dict이면 `[event]`로 감싼다. 제품의 유일한 생산자인 러너는 늘 `ObservationBatch`를 보낸다(`model_runner.py:178`). 따라서 dict 경로는 `{"type": "tick"}`을 넘기는 시험 세 곳에서만 도달한다. 결과-E가 "대역을 모두 묶음으로 바꾸면 이 경로를 지울 수 있다"고 남겼고, 그대로다.
- 근거: `grep -rn "_observe_running(" do_math tests`는 제품 호출 1곳(`engine.py:3421`, 러너 콜백)과 시험 5곳을 반환했다. 그 가운데 dict를 넘기는 것이 3곳이다.
- 제안: 시험 세 곳이 빈 `ObservationBatch`를 넘기게 바꾸고, 제품의 `dict |` 분기와 `batch is None` 처리를 지운다.
- 실익: 시험 전용 제품 분기 하나가 사라진다(`AGENTS.md:7`).
- 비용과 위험: 제품 3~4행과 시험 3곳이 바뀐다. `live` 판정(`batch is None or not batch.is_terminated()`)이 단순해진다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-14 `resolve_profile`의 30개 호출자가 복사가 필요한지 감사되지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/execution_profiles.py:287-289`; 호출자 17개 모듈(아래 근거); `임시/경량화-조사-2026-09-26/결과-K제품.md:29`
- 현상: STO-16은 조회 정본 `match_profile_ref`(재해시·복사 없음)를 만들었다. 그러나 기존 호출자는 "복사가 필요할 수 있어" `resolve_profile = deepcopy(match_profile_ref(...))`를 그대로 부르게 두었다. "호출자마다 변경 여부를 감사해야 한다"는 잔여가 그대로다.
- 근거: `grep -rn "resolve_profile(" | grep -v def`는 30건을 반환했다. 모듈별로 `lifecycle_engine` 7, `execution_profiles` 4, `initialization` 3, `governance_engine`·`review_cycle` 각 2, 나머지 12개 모듈 각 1이다. `match_profile_ref`를 직접 부르는 곳은 8곳이다(`record_schemas/__init__.py` 6).
- 제안: 호출자마다 반환값을 고치는지 확인한다. 고치지 않는 호출자는 `match_profile_ref`로 옮기고, 고치는 호출자만 `resolve_profile`을 남긴다. 고치는 호출자가 없으면 `resolve_profile`을 지운다.
- 실익: 프로필 조회마다 드는 deepcopy가 대부분 사라진다(비용 측정 없음). "복사가 필요한가"가 호출부에 드러난다.
- 비용과 위험: 호출부 최대 30곳이 바뀐다. 읽기 전용 호출자가 나중에 반환값을 고치면 저장 상태가 오염될 수 있다. 이 위험은 HIS-04와 같은 성격이다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 30곳 가운데 반환값을 고치는 곳의 수를 호출부별로 읽어 보면 확정된다.

#### HIS-15 부모 바이트 재사용이 파이썬 `==`로 판정되어 형만 바뀐 값을 놓칠 수 있다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/repository.py:890-891`; `임시/경량화-조사-2026-09-26/결과-B.md:84`
- 현상: 후보 인코딩은 부모 레코드와 `==`인 레코드에 부모 파일 바이트를 그대로 쓴다. 파이썬에서 `1 == True`, `1 == 1.0`이므로, 값의 형만 바뀐 레코드에 옛 바이트가 게시될 수 있다. 그러면 메모리의 게시 상태 캐시에는 새 형이, 저장소에는 옛 형이 남는다. 그 레코드는 `canonical_json`의 저장 값 검사도 건너뛴다(`repository.py:855-857` 설명). 그룹 B는 "생산 코드가 형만 바꾸는 경로는 찾지 못했다"고 남겼다.
- 근거: `repository.py:890`의 `prior.get(identifier, _ABSENT) == record`를 원문으로 확인했다.
- 제안: 비교를 형까지 보는 판정으로 바꾼다. 예를 들면 레코드 인코딩 바이트 비교다. 다만 그러면 재사용의 이득(직렬화 생략)이 사라진다. 이득을 지키려면 `type(a) is type(b)`를 재귀로 더하는 작은 도우미를 쓰거나, 저장 스키마가 정수 자리의 bool을 이미 거부함을 근거로 위험을 수용하고 설명 주석에 적는다.
- 실익: 게시 바이트와 메모리 상태가 조용히 갈라질 여지가 닫히거나, 그 수용 근거가 기록된다.
- 비용과 위험: 도우미 1개(10행 안팎) 또는 주석 1줄이 든다. 도우미를 쓰면 비교 비용이 조금 늘어난다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 레코드 필드 가운데 `integer`와 `boolean`을 함께 허용하거나 스키마 없는 EVIDENCE 객체 안에 수치가 들어가는 자리를 전수로 확인하면, 실제로 도달 가능한지 확정된다.

#### HIS-16 문서 단계가 판단으로 남긴 두 항목이 닫히지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `references/입력-소비자.md:5-54`; `계약/운영-점검.md:27`; `임시/경량화-조사-2026-09-26/결과-문서.md:287-291`, `:299`
- 현상: 두 항목이 미결이다.
  - 입력-소비자.md는 제출 검사(`governance.validate_import_units`, `validate_governance_record`)가 형태의 정본임을 적었다. 그러면서도 같은 필드를 나열한다. 문서 단계는 AI에게 다른 작성 안내 원천이 없어 나열을 지우지 않았고, "필드 나열을 실제로 줄일지는 통합자·사용자의 판단"으로 남겼다.
  - 운영-점검.md:27의 점검 발동 사건 목록에 "비활동"이 있다. 결정 3이 활성 시간 출처를 지운 뒤, 이 낱말이 무엇을 가리키는지 코드로 확인하지 못해 그대로 두었다. 현재 운영 점검 발동 종류는 `operational_review_due`, `tool_review_due`, `periodic_review_due`, `explicit_review_due`이고 비활동을 따로 판정하는 신호는 없다(`engine.py:2853`, `grep "inactiv\|idle"` 관련 0건).
- 근거: 두 파일의 현재 원문과 위 검색 결과다.
- 제안: 입력-소비자.md는 지금 형태(정본 포인터와 작성 안내 나열)를 유지한다고 판정하고 결과를 기록한다. 문서 단계의 근거가 타당하다. "비활동"은 `periodic_review_due`(주기 관찰)를 가리키면 그 이름으로 바꾸고, 대응 신호가 없으면 지운다. 두 문서는 DOC 영역 소유이므로 실제 수정은 DOC 후보와 합친다.
- 실익: 역할 문서의 발동 사건 목록에 생산자 없는 사건 이름이 남는 문제가 사라진다. 결정 3의 잔재다. 남아 있던 판단 대기 1건도 닫힌다.
- 비용과 위험: 문서 1~2행이 바뀐다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 있음. 입력-소비자.md 나열 축소는 결과-문서가 사용자 판단으로 넘긴 항목이다.
- 확신도: 확인

#### HIS-17 추적표 전체 검사가 추적되지 않는 로컬 보관소 419MB에 의존하고, 없는 폴더를 근거로 든다
- 검토: 2
- 종류: 공백
- 좌표: `docs/do-math/implementation-v5/traceability.json`(`observed_runs` 15건, `임시/do-math_설계대조_2026-09-19` 참조 15곳); `scripts/check_coverage.py:90-110`; `scripts/tests/test_redesign_EVIDENCE.py:300-301`; `기억/layer1/M-0348.md:73`, `M-0350.md:51`; `임시/시험-경량화-2026-09-26/진단-B4-2.md:27`
- 현상: `test_full_trace_is_structurally_valid_not_an_execution_pass`는 `observed_runs` 15건의 보관 디렉터리를 읽는다. 대상은 `임시/do-math-resume-20260920` 10건(384MB)과 `임시/do-math-implementation-20260920` 5건(35MB)이며, 둘 다 추적되지 않는다. 그래서 worktree나 새 체크아웃에서는 이 시험이 "archive directory unavailable"로 실패한다. 세 경량화가 모두 이 증상을 다시 만나 환경 원인으로 기록했다(M-0348:73, M-0350:51, 진단-B4-2:27). 또 추적표의 근거 문장 15곳은 `임시/do-math_설계대조_2026-09-19/재검토/…`를 가리키는데, 이 폴더는 추적된 적도 없고 지금 로컬에도 없다. 이 참조는 `7d2597e`(세 경량화 이전)에서 들어왔고 검증 대상 필드가 아니다.
- 근거: `grep -o "임시/[^\"/]*" traceability.json | sort | uniq -c`는 세 이름을 반환했다(15·5·17건). `ls`와 `git ls-files`로 설계대조 폴더가 없고 두 보관소가 추적되지 않음을 확인했다. 시험이 요구하는 최소 부분집합(run.json, stderr.txt, 스냅숏 manifest 파일)을 계산하면 5,191개 파일, 104.4MB다(6절). 추적하기에는 크다.
- 제안: 보관소가 없을 때 이 시험 하나를 이유와 함께 건너뛰게 한다(`skipUnless(<보관소 존재>)`). 이미 심볼릭 링크 권한·휴대용 Lean 부재를 같은 방식으로 건너뛴다(M-0350:43의 건너뜀 2). 그러면 worktree 통합 확인에서 보관소를 복사하는 절차(M-0350:51)가 필요 없어진다. 설계대조 참조 15곳은 근거 문장이므로 고치지 않고, 추적표 머리 설명에 "로컬 보관 원자료, 삭제됨"을 한 줄 둔다.
- 실익: 세 라운드가 반복해서 치른 환경 실패 판정 비용이 사라진다. 보관소 복사 절차(419MB)도 필요 없어진다.
- 비용과 위험: 시험 1곳 2~3행이 바뀐다(TSB 소유 파일). 보관소가 있는 `C:/math`에서는 지금처럼 전체 검사를 한다. 없는 환경에서는 이 시험이 검사하지 않는다는 사실이 건너뜀으로 드러난다.
- 기능·커버리지 영향: 있음(보관소 없는 환경에서 전체 추적 검사를 건너뜀. 구조 검사 `setUpClass`는 그대로 돈다)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-18 RES-17: 제출 미리보기가 묶음 파생을 여러 번 계산하고 `integration`의 비공개 함수를 부른다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/submission.py:1033`, `:1036-1040`, `:1153`, `:1158`; `scripts/do_math/integration.py`의 `derived_bundles`(계약 11절 225행); `임시/경량화-조사-2026-09-26/결과-D.md:98`
- 현상: 그룹 D는 `apply_bundles`만 `derived_bundles`를 한 번 계산해 넘기게 바꿨다. 제출 미리보기의 같은 반복(`inspect_bundles`, `protocol_output`, `split_bundles`를 각자 호출)은 그룹 C 소유라 선택 인자만 열어 두었다. 현재 미리보기는 파생을 따로 계산하고, `integration._split_research`(비공개)를 두 곳에서 부른다.
- 근거: `grep -n "derived_bundles\|inspect_bundles\|split_bundles" submission.py`는 3건을 반환했고, `derived_bundles`는 0건이다.
- 제안: 미리보기가 `integration.derived_bundles`를 한 번 계산해 `derived=`로 넘기게 한다. 결과-D가 "두 줄"로 추정한 변경이다. `_split_research`는 공개 이름으로 바꾸거나 `derived_bundles` 결과에 싣는다.
- 실익: 같은 파생 계산 하나를 두 경로가 따로 하던 곳이 정본 하나를 쓴다. 모듈 경계를 넘는 비공개 호출도 사라진다.
- 비용과 위험: `submission.py` 2~4행, `integration.py` 이름 1개가 바뀐다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### HIS-19 `_academic_evidence`가 없는 경로를 `None`으로 받으려는 듯하지만 기본 `raise`로 읽는다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/academic_engine.py:93-94`; `scripts/do_math/lifecycle_engine.py:732`; `임시/경량화-조사-2026-09-26/결과-B.md:102`
- 현상: `self.store.read_many([ref], self.head).get(ref)`는 `.get`으로 부재를 `None`으로 다루려는 모양이다. 그러나 `read_many`의 기본 `missing="raise"`로 부르므로 없는 경로는 예외가 된다. 2라운드가 `missing="omit"`을 만들었을 때 그룹 B가 "그룹 D가 판단한다"고 넘겼고, 그 뒤 판단 기록이 없다.
- 근거: 원문 94행과 `read_many`의 `missing` 인자(계약 11절 175행)를 대조했다.
- 제안: 호출자(`bind_external_prerequisite`의 `resolve_evidence`)가 부재를 `None`으로 처리하면 `missing="omit"`을 넘긴다. 부재가 오류여야 하면 `.get(ref)`를 `[ref]`로 바꿔 의도를 드러낸다.
- 실익: 한 줄의 의도와 동작이 일치한다. 남은 판단 대기 1건이 닫힌다.
- 비용과 위험: 1행이 바뀐다.
- 기능·커버리지 영향: 선택에 따라 없음 또는 있음(부재 증거의 처리)
- 사용자 결정 관련: 없음
- 확신도: 추정. `academic.bind_external_prerequisite`의 `resolve_evidence` 반환값 처리를 읽으면 어느 쪽이 의도인지 확정된다.

#### HIS-20 관찰 하나의 소유 루프 비용이 부하 아래 관찰 도착 간격보다 크다는 기록이 열려 있다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/engine.py:2786-2799`; `scripts/do_math/parallel.py`의 관찰 펌프(M-0350:49); `임시/시험-경량화-2026-09-26/작업자-노드/W-debt-M-0351.md:26`, `:36`
- 현상: W-debt는 관찰 하나의 적용 비용을 기록했다. tracker와 runtime의 깊은 복사, `_unchanged` 비교, 때로 게시가 들어가며, 부하 아래 0.1초를 넘는다. 그래서 여러 호출이 출력을 흘리면 펌프를 한정해도 적용 대기가 쌓인다고 남겼다. 3라운드는 펌프 한정(무한 소진 결함)만 고쳤다. 현재도 `_observe_running`은 관찰마다 `deepcopy(tracker)`와 `deepcopy(self.runtime)`를 한다(`engine.py:2789`, `:2798`).
- 근거: 원문 두 행과 W-debt 기록이다. 측정은 W-debt의 부하 아래 값만 있다.
- 제안: 게시 비용은 안 C(보류)에 속하므로 건드리지 않는다. 깊은 복사만 줄인다. 되돌림용 사본을 runtime 전체가 아니라 관찰이 고치는 하위 키(관찰 사실, 자기 점검 의무)로 한정한다. 이 판단이 가능한지 먼저 원문으로 확인한다.
- 실익: 동시 호출 수에 비례하는 소유 루프 지연이 줄어든다. 추정이며 측정이 필요하다.
- 비용과 위험: `engine.py`의 되돌림 경계를 좁히면 실패 시 되돌리지 못하는 키가 생길 수 있다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 있음. 안 C(내구성 저장 절감 보류)와 인접한다. 이 후보는 게시가 아니라 복사만 다루므로 결정과 충돌하지 않는다.
- 확신도: 추정. 호출 3개가 동시에 출력을 흘리는 시험에서 관찰 적용 대기열 길이를 재면 확정된다.

## 4. 보존 판정

- `scripts/setup_lean.py:95-107`(`_settled_fingerprint`의 `time.sleep(RACY_NS / 1e9)` 재시도): 겉보기에는 시간 지연으로 경쟁을 가리는 코드다. 실제로는 기준 지문에 racy 창(2초) 안의 시각을 기록하지 않게 하는 규칙(이음새 계약 1절 `fingerprint_settled`)이며, 3회 뒤에는 명시적으로 실패한다. 임시방편이 아니다.
- `scripts/do_math/engine.py:1060-1064`(`_sealed_bytes`)와 `engine.py:503-504`(`_governance`): 한 줄 위임처럼 보이지만 엔진의 저장소·head·상태를 인자로 묶는 어댑터다. 호출부 12곳과 5곳의 인자 반복을 없앤다.
- `scripts/do_math/governance.py:343-345`(`timestamp`): `parse_utc`의 감싸개처럼 보이지만 `None`을 현재 시각으로 해석하는 별도 의미를 36곳이 쓴다.
- `scripts/do_math/record_schemas/schemas.py:23`의 `TEXT`(`{"type":"string"}`)와 `contracts.TEXT`(비지 않은 텍스트): 이름은 같지만 다른 규칙이다. 저장 스키마는 `contracts.TEXT`를 `_NONEMPTY_TEXT`로 가져와 구별한다(`schemas.py:12`). 합치면 모든 저장 가족의 문자열이 강화된다(결과-B 5절 REV-14).
- `임시/경량화-조사-2026-09-26/`의 조사 8개와 결과 11개: 추적은 유지한다. 2라운드 설계(5행)와 추적표(15978·24588행)가 근거로 가리키는 역사 기록이다. HIS-06의 지위 표지 대상이지 삭제 대상은 아니다.
- `scripts/do_math/git_store.py:257-263`, `:275`, `:335-339`: W-git이 남긴 쓰기 경로의 한계(fsync 기본값, 압축 수준, 로컬 시간대 오프셋, 고정 작성자)가 코드 설명에 드러나 있다. 추가 조치가 필요 없다.
- `references/초기화-효율과-정비.md:93-99`: 검사 설계 10절의 남는 위험과 NTFS 터널링이 스킬 문서에 옮겨져 있다. 검사 설계 문서가 역사 기록이 되어도(HIS-06) 현행 한계의 정본은 여기다.
- 공급자 CLI 호출의 가짜 어댑터 기반 시험 전반: HIS-10은 시험을 실제 CLI로 바꾸자는 것이 아니다. 실호출 확인을 명시적 탐침 하나에 두자는 것이다.

## 5. 영역 밖 관찰

- ENG `scripts/do_math/engine.py:2493`과 TSB `scripts/tests/test_lifecycle_engine.py:774`, `:823`, `scripts/tests/test_redesign_ENGINE.py:542`: 결과-C 4.1절은 `_available_inputs` 대역이 "이제 부르지 않는 경로를 막지만 해가 없어 남겼다"고 적었다. 대역을 쓰는 세 시험이 실제로 그 경로를 타는지 확인하고, 타지 않으면 대역을 지운다.
- STO `scripts/do_math/git_store.py:545`(`getattr(self, "_git_dir", self.repository)`), `:572`(`hasattr(self, "_git_boundary")`): 저장소 객체의 방어적 속성 접근이다. HIS-02와 같은 형태인지 초기화 경로로 판정한다.
- IO `scripts/do_math/model_runner.py:126`(`hasattr(self._adapter, "capability_identity")`): 모든 어댑터가 기반 `LocalCLIAdapter`에서 이 메서드를 받으면 방어가 불필요하다.
- REV `scripts/do_math/contracts.py:156`(`TASK_CANDIDATE["properties"]["description"] = TEXT`): 공유 노드를 다른 스키마에 대입한다. HIS-04의 복제 방식이 들어가면 자동으로 안전해진다.
- ENG·RES `scripts/do_math/formal.py`의 도구 모음 위치: `formal.py` 기준 다섯 단계 위의 `.skill-workspace/do-math-toolchains`를 찾는다(M-0350:51). 저장소 배치에 묶인 이 탐색 때문에 worktree에서 실제 Lean이 `unavailable`이 된다. 설정 키나 환경 변수 하나로 대체할지 검토할 만하다.
- IO `scripts/do_math/control_transport.py`의 `close`: inbox 파일마다 `ValueError`를 삼킨다(결과-E 5절 IO-19). 이유가 기록된 의도된 처리이지만, 삼킨 오류가 어디에도 기록되지 않는지 확인이 필요하다.

## 6. 작업 기록

- 저장소 전체를 대상으로 한 참조 검색(`grep -rln … .`)이 120초 제한을 넘어 백그라운드로 넘어갔다. 그래서 대상 폴더(`.claude/skills/do-math`, `docs`, `기억`)별 `Grep`으로 바꿨다. 백그라운드 결과에서 `.codex/writing-flow/` 아래의 일치는 추적되지 않는 도구 상태 파일이다(`git ls-files .codex`는 2건뿐이다).
- 파견문이 "열려 있으면 `공백` 후보로 낸다"고 정했으므로, 특정 파일 하나에 묶인 열린 항목도 HIS 후보로 냈다(HIS-08, HIS-11~15, HIS-18~20). 기준 9절의 소유 규칙과 다른 부분이므로, 통합자가 해당 영역 후보와 합칠 때 중복을 볼 필요가 있다.
- 3.1절 37번 행은 여러 결과 파일의 "실행하지 않아 확인하지 못한 위험"을 M-0350의 최종 전체 실행(1,860 통과, 실패 0)으로 한꺼번에 닫았다. 이 판정은 그 위험들이 시험으로 관찰 가능하다는 전제에 선다. 시험이 없는 경로(실제 CLI, 공급자 수용)는 이 행에 넣지 않았다.
- 시험은 실행하지 않았다. 저장소를 바꾸지 않는 파이썬 확인 다섯 가지를 했다.
  1. `do_math` 전체 AST에서 dict 리터럴과 `dict(...)` 키워드의 중복 키를 찾았다. 결과는 0건이다.
  2. 이음새 계약 11절 표의 모든 식별자가 `scripts/` 소스에 실재하는지 검사했다. 누락은 0건이다.
  3. 11절 각 행의 첫 식별자가 적힌 모듈에 정의되어 있는지 검사했다. 불일치는 0건이다.
  4. `contracts.schema_for(role)` 10개 역할에서 사본 안에 공유된 dict 노드 수를 셌다. 결과는 3~6개였고, `research_preparation`의 `candidates` 노드는 공유되지 않았다.
  5. `traceability.json`의 `observed_runs`가 요구하는 보관소 최소 부분집합을 계산했다. 결과는 5,191개 파일, 104.4MB다.
- 예상과 다른 결과가 셋 있었다.
  - 이음새 계약 11절은 코드와 완전히 일치했지만, 같은 문서의 1~10절에는 낡은 서술이 일곱 곳 있었다.
  - 결과 파일들이 이음새 계약에 요청한 수정(결과-B:66, 결과-E:81, 결과-K시험:140)은 11절 추가 때 반영되지 않았다.
  - W-fix가 캐시 등록 규칙을 남긴 같은 라운드에 그 규칙을 따르지 않은 캐시 넷이 들어왔다.
