# do-math 마지막 두 커밋의 문제 유형과 잔여 결함

기준은 `c44dd7b7f34813d525ef4b79758dea7369984296`이다. 바로 앞 커밋은 `ff9b2b9c9f3bb9de5f9dd6773a927d7a17b973b8`다. 제품은 수정하지 않았다. 이 문서는 이후 수리를 위한 진단과 검증 기준이다.

핵심은 **확인한 사실이 다음 단계로 넘어갈 때, 내용·시점·대상·효력이 함께 보존되는가**다. 자료를 보존하는 것, 그 자료를 다음 판단자에게 전달하는 것, 지금도 사용할 수 있는 것은 서로 다른 조건이다. 두 커밋은 이 연결의 오류와 그 연결을 유지하는 데 드는 불필요한 비용을 고쳤다.

## 두 커밋에서 실제 고친 것

| 유형 | 기존 문제와 원인 | 수정의 핵심 |
|---|---|---|
| T1. 검사 경계와 현재성 | 등록·상태 조회·저장에서도 큰 신뢰 환경을 반복 검사하고, 긴 파일 검사가 중앙 처리와 응답 편입을 붙잡음 | 구조 검사와 실제 파일 관측 분리. 필요한 사용·편입 경계에서 전체 파일을 제한된 병렬 작업으로 새로 관측. 이미 봉인한 응답은 기다렸다가 재적용 |
| T2. 불변 원문과 저장 비용 | 큰 manifest·문자열이 여러 레코드에 중복 직렬화되고 같은 부모 상태도 재검증됨 | 내용 주소형 payload, 변경 불가 공유 값, Git OID·검사 계약에 결박한 부모 재사용. 물리 파일 해시와 논리 값 해시 구분 |
| T3. 실행 시작·종료 증거 | 시작 callback이 없다는 사실을 프로세스가 없다는 사실처럼 다룰 여지. Job 이름 충돌·PID 재사용·다른 세션도 구별 필요 | 프로세스 생성 전 launch ticket 저장. owner·세션·생성 시각·독점 Job 결박. 실제 종료 확인 후 슬롯 반환 |
| T4. 관찰 순서 | 늦게 소비한 로그를 방금 발생한 행동으로 평가하고, 이미 끝난 실행에 점검을 열거나 전달 전 행동을 위반으로 셈 | 수신 시각·바이트 좌표를 가진 batch, 실제 종료 재확인, batch 적용 뒤 평가, 요청 전달과 정확한 수신 확인 구별 |
| T5. 증거 전달과 검사 문맥 | 체크포인트가 저장돼도 운영 검토 입력에는 없거나, 읽을 수 있는 참조와 처분에 허용된 참조가 다름. 큰 과거 요청·레지스트리도 입력을 팽창시킴 | 체크포인트 본문·근거 파일을 고정 입력으로 지급. 허용 근거 목록을 생산자·수신자가 공유. 큰 원문은 검증 가능한 상세 참조로 제공 |
| T6. 판단 근거의 의미 | 제출 내용은 그대로인데 이후 형식 검사·동일성 판정 추가가 완료 근거 변경으로 잡힘 | 제출 내용의 근거와 전문 판정의 효력을 구별. 실제 의존 내용·효력 변경은 계속 무효화. 끝난 과제의 오래된 판정은 후속 사건으로 전달 |
| T7. 사건의 책임 | 최초 준비가 초기화 사건을 맡지 않거나, 정상 실행 점유가 착수조건 상실로 보여 불필요한 계획을 유발 | 최초 action에 사건 ID 결박, 수락 뒤 소비. 단순 점유와 실제 계약·입력·권한 상실 구별 |
| T8. 정비·관측 가능성 | 설치 교체의 종료 장벽과 단계별 시간·진행 근거가 불충분 | 새 배정을 막고 기존 실행을 정산하는 정비 fence, 단계별 계측·진행 sidecar. 정비·계측은 연구 권한이나 수학 승인과 별개 |

`ff9b2b9c`은 주로 T1–T3·T8과 큰 입력 보존을, `c44dd7b7`는 주로 T4–T7과 운영 입력 연결을 다룬다. 단순 속도 개선만도, 단순 조건문 수정만도 아니다. **같은 사실을 쓸데없이 다시 확인하지 않으면서도, 다른 사실을 확인한 것으로 착각하지 않게 하는 변경**이다.

## 확정된 수리 항목

아래 **7건**은 실제 현행 함수·저장소·실행기에서 반례를 확인한 항목이다. `P1`은 진행 차단 또는 기존 증거 접근 상실 때문에 먼저 수리할 항목, `P2`는 제한된 조건의 정합성·계보 결함이다. 발생 빈도나 실제 연구 피해를 측정한 등급은 아니다.

### D1 · P1 · 이전의 큰 원문을 다시 저장할 수 없다

- **재현:** 큰 문자열 A 저장 → 작은 문자열 B로 교체 → 같은 A로 복귀. 마지막 저장이 `existing runtime artifact bundles are immutable`로 거부된다.
- **원인:** [repository.py](../../../.claude/skills/do-math/scripts/do_math/repository.py) 94–108행은 현재 레코드가 참조하는 payload만 `old_files`에 넣는다. 188행은 그 목록에 없는 예전 payload를 신규 파일로 게시한다. 그러나 Git에는 이미 그 불변 artifact가 남아 있다. [git_store.py](../../../.claude/skills/do-math/scripts/do_math/git_store.py) 378행이 재기입을 거부한다.
- **범위:** 공통 저장 코덱을 사용하는 큰 문자열·큰 manifest의 참조가 끊겼다가 재등장하는 경우. 같은 내용의 재사용을 변경 시도로 오인하는 T2 문제다.
- **수리 기준:** 기존 내용 주소형 blob이 동일 바이트라면 다시 참조할 수 있어야 한다. 다른 바이트로 교체하려는 시도는 계속 거절해야 한다. A→B→A를 실제 Git 저장·재읽기로 검사한다.
- **재현 파일:** `repro_payload_storage.py`의 `orphan_reuse`.

### D2 · P2 · 검증한 payload를 저장 직전에 덮어써 읽을 수 없는 snapshot을 게시한다

- **재현:** `ResearchRepository.save_with_state(..., artifacts=...)`에 이번 상태 코덱이 만들 payload 경로와 같은 키, 다른 바이트를 제공한다. 저장은 정상 반환하지만 새 head의 `load()`는 `immutable payload bytes differ`로 실패한다.
- **원인:** [repository.py](../../../.claude/skills/do-math/scripts/do_math/repository.py) 183–191행에서 검증·인코딩한 상태 파일 위에 외부 `artifacts`를 뒤늦게 덮는다. 검사한 바이트와 게시한 바이트가 달라지는 새 하위 유형이다.
- **조건 제한:** 저장소 API 호출에서 재현했다. 표준 실행기의 일반 artifact 생산자는 `BA-`·`EX-` 등 별도 경로를 사용하므로, 일반 모델 응답만으로 이 충돌을 만들었다고 주장하지 않는다.
- **수리 기준:** 두 파일 집합을 합치는 경계에서 충돌을 검증해야 한다. 불일치 시 ref를 전진시키지 않고 실패하며, 성공 반환한 head는 반드시 다시 읽혀야 한다.
- **재현 파일:** `repro_payload_storage.py`의 `artifact_collision`.

### D3 · P1 · 실행 종료 때 체크포인트의 봉인 근거 연결이 사라진다

- **재현:** 체크포인트가 `proof.txt`의 원본을 지목하고 실행 중 관찰이 그 바이트를 보존한다. 파일만 바꾸고 같은 체크포인트로 실행을 끝내면, 종료 후 `evidence_files`는 사라진다. 운영 검토의 `checkpoint_files=[]`이고 일반 회수 파일에는 바뀐 바이트만 제공된다. 원본 artifact는 Git에 남아 있다.
- **원인:** [engine.py](../../../.claude/skills/do-math/scripts/do_math/engine.py) 3593–3609행이 파일에서 재구성한 체크포인트로 기존 관찰 레코드를 교체한다. [observations.py](../../../.claude/skills/do-math/scripts/do_math/observations.py)의 `bind_checkpoint_artifact`는 본문 참조만 연결하고 기존 `evidence_files`·`evidence_omitted`를 잇지 않는다.
- **범위:** 정상적인 결과 회수 경로의 성공·실패 공통 처리와 재시작 복구의 같은 helper 호출. 실행 중 수집만 검사하면 놓치는 T5 문제다. 재현 실행의 모델 결과는 의도적으로 실패시켜 후속 운영 진단까지 확인했다.
- **수리 기준:** 같은 checkpoint 해시에는 함께 봉인한 근거·누락 목록도 이어져야 한다. 다른 해시의 새 checkpoint에는 옛 증거를 임의로 붙이면 안 된다. 종료 뒤 검토 입력에서 원본 바이트를 다시 읽는 검사가 필요하다.
- **재현 파일:** `repro_checkpoints.py`의 `regular_end`.

### D4 · P1 · 재시작 복구가 마지막 유효 체크포인트를 버린다

- **재현:** 유효 checkpoint와 근거를 관찰·저장한 뒤, 디스크의 checkpoint를 미완성 JSON으로 만들고 이전 실행기 소실 복구를 수행한다. 기존 `worker_checkpoint`가 `observed_partial_state`로 바뀌고 검토 입력은 `not_preserved`가 된다. 이전 원문은 여전히 Git에서 읽힌다.
- **원인:** [engine.py](../../../.claude/skills/do-math/scripts/do_math/engine.py) 1659–1678행의 복구 경로에는 3604행의 일반 종료 경로에 있는 “마지막 유효 관찰 유지” 분기가 없다. 공통 실행 문서 208행의 “잘못된 갱신은 마지막 유효 기록을 대체하지 않는다”와 충돌한다.
- **수리 기준:** 마지막 유효 checkpoint를 유지하고, 종료 시점의 읽기 실패·손상은 별도 관찰로 남겨야 한다. 파일 손상·부재·근거 파일 누락을 구별해야 한다.
- **재현 파일:** `repro_checkpoints.py`의 `recovery_invalid_final`. 실제 Git·실행기 복구를 사용했고, 이전 프로세스의 종료 관측만 테스트 대역으로 명시했다.

### D5 · P2 · 관계를 통해 읽는 지식의 개정이 실행 중 독자를 기다리지 않는다

- **재현:** 현행 생성·검증·Git 저장을 통과한 관계 RL의 양끝 KN을 준비된 과제가 RL을 통해 읽는다. 그 과제가 실행 중이어도 양끝 KN에 대한 개정의 `revision_waits=[]`다. 같은 KN을 과제 입력에 직접 추가하면 즉시 `existing reader must finish before revision` 대기가 생긴다. 양끝 모두 확인했다.
- **원인:** [planning.py](../../../.claude/skills/do-math/scripts/do_math/planning.py) 62–95행의 읽기 의존 순회는 `relation_claim.source/target`은 따라가지만 정식 relation 레코드의 최상위 `source/target`은 따라가지 않는다. `revision_waits` 135행이 이 불완전한 읽기 집합을 사용한다.
- **확인 한계:** 같은 누락 형태가 `task_scope.assessment_basis`에도 있고 relation의 `evidence_refs`, `formal_result_refs`, `assessment_refs`도 두 순회에서 누락된다. 그러나 정상 지식 개정에는 별도의 `knowledge._impact_refs`→`apply_impact` 무효화가 있다. 축약 객체를 직접 수정한 실험만으로 “완료·승인 현재성도 우회된다”는 주장은 기각했다. D5의 확정 영향은 **개정 착수 전 독자 대기 누락**이다.
- **수리 기준:** 관계의 실제 스키마와 의미에 맞게 읽기 의존을 따라가야 한다. 직접 읽기/관계를 통한 읽기, 양끝, 관련 없는 기록, 기존 영향 무효화를 함께 대조한다.
- **재현 파일:** `reproduce_relation_reader.py`.

### D6 · P2 · 취소된 신뢰 검사 재실행의 명시적 계보가 저장되지 않는다

- **재현:** `trust_activate`를 정비 fence로 취소하고 해제 후 다시 실행한다. 지역 변수에는 `continuation_of=이전 EX`가 있지만 저장된 queue와 후속 실행에는 `null`이다. 후속은 정상 수락되고 소유 활동도 같다.
- **원인:** [lifecycle_engine.py](../../../.claude/skills/do-math/scripts/do_math/lifecycle_engine.py) 1216행이 `_save()` 뒤의 오래된 `action` 객체에만 후속 표시를 쓴다. `_save()`는 정규화된 분리 객체로 현재 상태를 교체한다. 기록을 고쳤다는 사실과 현재 저장 대상이 고쳐졌다는 사실이 달라지는 새 하위 유형이다.
- **영향 제한:** 이 실험에서 실행 실패·활동 고아화는 없었다. 명시적 선행 실행 연결의 유실을 확인했다.
- **동일 유형 대조:** `continuation_of` 등장 지점을 확장 조사했다. 유사한 `trust_check` 1412–1415행은 현재 queue에 다시 복사하므로 이 결함이 없다. 일반 재개·수리·외부 작업은 현재 상태를 갱신하거나 queue에 다시 넣는다.
- **수리 기준:** 현재 queue의 action에 연결을 기록하고 저장·재시작 뒤 후속 실행까지 같은 값을 유지해야 한다. 같은 활동 ID만 같다는 확인으로 대신하지 않는다.
- **재현 파일:** `probe_c.py`의 `cancelled_activation`.

### D7 · P1 · 잘못된 제어 입력이 반려되지 않고 같은 처리 실패를 반복한다

- **재현:** 공개 `control(..., action='trust')`로 등록 요청을 보내되 `manifest.foundation_profile=[]` 또는 `manifest.validation=[]`로 한다. 접수는 성공한다. `process_controls()`가 `AttributeError`로 끝나고 processed 목록에는 기록되지 않는다. 새 실행기를 두 번 만들어도 같은 요청에서 다시 실패한다.
- **원인:** [trust_validation.py](../../../.claude/skills/do-math/scripts/do_math/trust_validation.py) 33·47행의 중첩 값에 객체 타입 검사가 없고, [engine.py](../../../.claude/skills/do-math/scripts/do_math/engine.py) 910행의 반려 경계는 `ValueError`, `KeyError`, `TypeError`만 처리한다. 형식 오류가 정상 반려를 벗어나 지속적인 처리 장애가 된다.
- **확장 재현:** 실제 CLI `decision --file`에서도 헌장의 `record.content=[]`, 허가의 `grant.expires_at=1`이 같은 반복 실패를 일으킨다. 각각 [governance.py](../../../.claude/skills/do-math/scripts/do_math/governance.py) 306행의 `.items`, 337행의 `.replace`에서 예외가 난다. Python 공개 API에서는 8개 action의 `config=[1]`, `decision.change=[]`, `request.review_replacement.action=[]`도 같은 유형으로 재현됐다. CLI는 최상위 JSON 객체를 검사하므로 API 사례를 CLI 최상위 배열 허용으로 확대하지 않는다.
- **수리 기준:** 입력 경계에서 형식을 확인해 구조화된 반려를 남겨야 한다. 해당 요청의 반복 실패를 끝내고 그 뒤 정상 요청이 처리돼야 한다. 내부 프로그래밍 오류까지 조용히 삼키는 방식은 피한다.
- **재현 파일:** `repro_trust_input.py`, `probe_control_types.py`, `reproduce_control_boundary.py`. 같은 유형의 다른 제어 입구 조사 결과는 [coverage.md](coverage.md)에 기록한다.

## 검사 방법과 결과를 읽는 법

정본 242개 파일을 목록·해시로 고정했고, 두 커밋의 변경 파일 합집합은 81개다. 생성 미러 `.agents/`는 별도 구현으로 중복 계산하지 않았다. `graphify`는 조회만 했으며 상태는 `current`였다. 구조 지도는 위치 찾기에만 쓰고 현재 원문·코드로 판단했다. `find-needle-haystack`의 독립 중복 탐색과 `be-comprehensive`의 항목별 누락 대조를 적용했다.

절차는 **수정 이유 → 지켜야 할 조건 → 그 조건을 생산·저장·전달·소비하는 모든 지점 → 정상/경계 사례 대조**다. 동일 함수 이름만 찾지 않고 정상 종료/복구, 직접 참조/간접 참조, 현재 참조/재등장, 검증 전/게시 직전의 짝을 비교했다. 새 유형은 별도 검사 항목으로 추가했다. 검색 일치는 결함 판정으로 세지 않았다.

- 기존 관련 회귀 검사: **49개 통과**. `baseline-report.json`에 개별 결과와 실행 환경·범위를 보존했다.
- 구조 검사: `python .claude/skills/do-math/scripts/probe_cli.py --skill-only` 통과. 문서 의미·실제 모델 연구 성능을 인증하는 검사는 아니다.
- 보존 위치에서 재현 스크립트 **7개를 다시 실행하여 모두 완료**했다. [reproductions.json](reproductions.json)에 현재 판본, 스크립트 해시, 실행 결과·로그를 결박했다. 종료 코드 0은 결함 재현을 포함한 진단 완료이며 제품이 정상이라는 뜻이 아니다.
- 새 반례는 실제 모델 서비스·실제 연구 인스턴스를 사용하지 않는다. 폐기 가능한 Git 저장소, 현재 테스트 fixture와 실제 제품 함수를 사용하며 테스트 대역의 범위를 각 항목에 적었다.
- `inventory.json`은 정본 파일별 해시와 유형별 검색 좌표다. 모든 파일이 목록화됐다는 뜻이며, 모든 행의 모든 가능한 결함을 증명적으로 배제했다는 뜻은 아니다. 수리 항목과 기각·미확정 후보, 조사한 호출 경계는 `coverage.md`에서 구별한다.

후속 수리는 D7의 정상 반려, D1의 같은 바이트 재사용, D3–D4의 증거 연결 보존을 먼저 다루는 편이 좋다. D2·D5·D6도 각 재현을 실패 검사로 전환하고, 수정 후 같은 경계의 정상 사례가 유지되는지 확인한다. 과거 연구 기록의 자동 변환이나 구판 호환 계층을 추가할 사안은 아니다.

보존된 재현을 한 번에 실행하려면 저장소 루트에서 다음 명령을 사용한다. 이 스크립트들은 현행의 잘못된 결과를 확인하도록 작성되어 있으므로, 수리 이후에는 기대값을 정상 결과로 바꿔 회귀 검사로 전환한다.

```powershell
python docs/do-math/similar-defects-2026-09-25/run_reproductions.py
```
