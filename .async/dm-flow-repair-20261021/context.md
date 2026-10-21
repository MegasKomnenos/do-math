# do-math 역할·작업 연결·검사 공통부 수리 개발

현재 상태(manager 0011): 최종 `final-contract-review`를 변경 없음으로 통합·수용했다. 학술 지급 문서 F1 해소와 이전 전체 R1~R7 리뷰의 유지 가능성을 독립 리뷰 및 공용 소스 대조로 확인했다. 사용자 개발 목표는 기록된 확인 범위에서 충족했고 실행 중·미해결 task가 없어 complete로 게시한다. 아래 17절이 이전 절의 대기·남은 작업 설명보다 최신이다. 원 수학 연구는 정지 상태를 유지하며 실제 연구 효능·미래 모델 준수는 확인하지 않았다.

이 작업은 C:\math의 do-math가 실제 수학 연구를 지속해서 수행하도록 역할 계약, 단계 사이의 판단과 인계, 공통 검사 및 이번 실행에서 드러난 결함을 조사·설계·수정하는 개발이다. 개발 서비스는 `C:\math\services\async-development`이고 공용 소스는 `C:\math`이다. 개발 기록 디렉터리 `C:\math\.async\dm-flow-repair-20261021`을 이 문서에서는 RECORDS라고 부른다.

사용자는 개별 오류의 임시 수리뿐 아니라 그 오류를 가능하게 한 역할 계약과 작업 연결을 전체 작업의 맥락에서 검토하도록 요청했다. 아래의 현행 요구는 사용자의 구체적 정정을 반영했다. 수행자는 이 문서에 적힌 의미를 배정문과 구현·검토에 유지한다. 원문을 대조할 때는 같은 디렉터리의 `user-messages.md`를 읽고, 뒤의 사용자 정정이 앞의 같은 주제에 우선한다.

## 1. 사용 상황과 이번 개발의 목적

사용자는 `research\problem-selection-2026-09-15`에서 선정한 주차 함수 최대 변위 분포의 단봉성 문제를 새 연구 인스턴스에서 연구하도록 요청했다. 인스턴스 `RI-01M5CYJ41RWYDQV0VCHMKTBR0N`을 새로 초기화하고 별도 연구 실행기로 인계했다. 모델은 주로 GPT 6.1 Sol을 사용하고 어려운 작업에 필요하면 GPT 6 Astra를 허용했다.

그 실행에서는 초기 입력 해석, 후보 준비, 작업 계약 검토, 주기 운영 점검, 계약 개정 판단과 계획만 수행됐다. 내부 실행 12건 중 11건은 모델 실행이고 1건은 신뢰 환경 활성화였다. 실제 연구 수행 역할의 실행과 수학 제안의 형식 검사는 0건이었다.

처음 준비된 과제는 문헌 현재성·핵심 세기식 조사, Lean 기초 정의, n≤60 정확 계산 세 개였다. 문헌조사 검토자가 scholarly 지원을 확인하지 못했다는 이유로 도구 항목을 미해결로 반환했다. 실행기는 이를 필수 계약 개정으로 바꿨다. 후보 준비는 계약 내용을 고칠 이유가 없는데 필수 개정을 변경 불필요로 끝낼 수 없어 운영 확인을 기다렸다. 운영 질문에는 담당 이름이 적혔지만 그 질문을 처리할 운영 실행은 생성되지 않았다. 다른 두 과제는 문헌조사 완료에 의존해 함께 기다렸다.

이는 이번 개발의 구체적 출발 사건이다. 역할 계약과 파이프라인 전체의 적합성을 판단할 때 이 사건만을 유일한 가능한 문제 유형으로 삼지 않는다. 각 역할이 전체 결과를 위해 무엇을 해야 하는지, 무엇을 판단할 권한과 재량을 가져야 하는지, 다음 단계와 어떻게 연결돼야 하는지를 실제 제품 흐름에서 검토한다.

## 2. 현행 요구

### R1. 역할 계약을 전체 작업의 맥락에서 검토하고 수정한다

계약 검토자는 명확히 드러난 문제를 발견하면 그 지적 자체가 타당한지 먼저 충분히 검토한 뒤 전달한다. 이때 실제 원문과 코드·기록을 확인하고, 자신의 오독·잘못된 전제·확인 부족이 문제로 보고된 것은 아닌지 점검한다. 판단을 전달할 때는 어떤 점이 왜 문제이며 해당 작업에 어떤 영향을 주는지 설명한다.

이번 검토자의 임무는 문헌조사 과제가 수행 가능한 질문·범위·입력·산출·완료 기준을 갖췄는지 판단하는 것이었다. 그 역할과 도구의 실제 확인을 수행할 역할, 연구 수행 중 실패를 처리할 역할의 책임을 전체 흐름에서 다시 설계한다. 수행자가 착수 후 확인하도록 정한 일을 검토자가 사전 승인 증거로 요구하게 되는 경계도 검토한다.

검토 범위는 do-math의 각 작업자 역할 계약 전체다. 현재 SKILL.md의 역할 읽기 대응표에서 실제 역할 모집단을 찾고, 역할 계약과 공통 문서, 입력 생성, 실제 출력 소비를 연결해 읽는다. 후보 준비·연구 계획·연구 수행·작업 계약 검토·동일성 검토·목표 감사·보충 조사·운영 점검·의도 해석·유지보수 및 독립 운영의 실제 책임 관계를 포함한다. 문서의 명칭이나 현재 목록이 바뀌어도 현행 코드에서 배정되는 역할을 따라 모집단을 완성한다.

각 계약의 목적, 책임, 판단 범위, 재량, 입력과 출력의 의미, 다른 역할과의 관계가 전체 작업에 적합하게 설계됐는지 판단한다. 계약들이 이미 모두 잘못됐다고 전제하지 않는다. 검토한 범위와 유지·수정한 내용, 그 이유를 실제 동작과 연결해 남긴다. 발견된 문제의 성격에 맞춰 문서·스키마·생산자·소비자를 함께 수정한다.

### R2. 단계 사이의 정상 처리와 예외 상황의 재량을 함께 설계한다

정상적인 요청 처리 흐름은 유지한다. 정상 흐름으로 적절하게 다룰 수 없는 예외 상황에서는 담당자가 전체 목적과 실제 상황에 맞는 대응을 선택할 수 있는 자유 범위를 둔다. 계약 개정 요청을 받았으나 그 요청의 전제가 잘못됐거나 실제 수정할 내용이 없는 상황이 이번의 예다. 이런 경우에는 실제 수리 없이 요청을 반려·기각·종결하는 선택도 가능해야 한다. 구체적인 처분 이름과 저장 형태는 구현자가 전체 의미에 맞게 정한다.

이 재량의 목적은 예외를 적절하게 처리하는 것이다. 일반 요청을 매번 의심하고 재심사하는 새 필수 절차로 바꾸지 않는다. 선택한 처분과 후속 상태가 연결돼 실제로 의무가 끝나거나 다음 담당으로 넘어가게 한다. 이름만 바꾼 처분을 추가한 뒤 기존 필수 수정·대기 상태를 그대로 남기지 않는다.

계약 개정 외의 단계 연결도 검토한다. 생산한 요청이 어떤 소비자에게 가고, 소비자가 무엇을 할 수 있으며, 정상 완료·예외·불필요해진 요청·확인 부족이 각각 어떻게 처리되는지 실제 코드를 따라 확인한다. 반드시 대응해야 하는 형식이 있으면 그 형식이 필요한 이유와 적용 범위를 검토한다. 전체 사용 목적과 실제 효과에 비추어 적합한 구조와 재량을 설계한다. 사용자가 정한 연구 목표·권한과 AI가 만든 개별 요청의 처리 재량은 서로 구별한다.

### R3. 운영 질문을 실제 운영 작업과 해소까지 연결한다

운영 질문이 등록되면 그 질문을 확인할 운영 작업이 실제로 배정되도록 한다. 질문의 소유자 이름뿐 아니라, 어느 요청이 어느 실행에 배정됐고 어떤 결과로 해소됐는지 연결돼야 한다.

질문의 실제 내용과 역할 범위에 맞게 운영 점검·유지보수 등 처리자를 고른다. 질문 조사에서 문제가 없다고 확인하는 경우, 기술 수리가 필요한 경우, 다른 자료나 사용자 결정이 필요한 경우를 목적에 맞게 처리한다. 같은 질문이 여러 보고나 재시작을 통해 전달돼도 의미상 같은 의무가 불필요하게 중복 실행되지 않도록 한다. 열린 질문을 잃어버려도 안 된다.

처리 결과의 근거가 질문 해소와 연결되고, 그 질문 때문에 남아 있던 대기·개정 의무·검토·계획이 적절한 다음 단계로 이어지게 한다. 질문을 닫았다는 사실과 과제 계약 승인·연구 완료는 각각의 의미에 맞게 구별한다. 사용자 정지 상태에서는 연구 실행을 다시 시작하지 않는다.

### R4. 사전 검사와 적용 검사의 공통 내용을 한곳에 둔다

사전 검사와 적용 검사가 공통으로 확인하는 내용은 한곳에 구현하고, 양쪽에서 이를 호출한다. 각 검사 위치에서 추가로 필요한 검사는 각자 수행한다.

공통 내용은 같은 입력 의미와 같은 판단 규칙을 가리킨다. 함수 이름만 비슷한지를 기준으로 정하지 않는다. 현재 경로에는 작업자가 제출 전에 실행하는 검사, 중앙이 제출을 받는 시점의 검사, 실제 상태에 적용할 때의 검사가 있다. 이 경로들에서 어떤 사항이 반복 확인되는지 읽고, 실제로 공통인 판단과 위치별로 필요한 판단을 구분한다. 공통 구현에 필요한 입력을 양쪽에서 동일한 의미로 제공하고, 공통 결과와 실패 종류도 같은 뜻으로 사용한다.

기존 구현에도 공통 검사 함수가 있다. 이번 결함은 단순히 두 구현이 전부 별개였다는 것으로 설명되지 않는다. 공통 검사에 들어가는 입력이 다른 경로에서 달라졌고, 적용 단계의 별도 해시 확인과 실패 분류가 이어지면서 문제가 발생했다. 따라서 공통 함수의 호출뿐 아니라 그 입력을 만드는 부분, 공통 규칙의 실제 검사 범위, 결과를 소비하는 부분까지 연결해 수리한다.

### R5. 해시 누락과 그 처리의 근본 문제를 해결한다

보류 응답이 대상 과제의 `previous_hashes`를 빠뜨린 것이 생산자 오류였다. 역할이 읽는 과제 상세에는 `content_sha256`이 있었으나 검사 문맥을 구성할 때 `tasks`가 원장 과제로 다시 교체돼 그 필드가 사라졌다. `integration.inspect_bundles()`는 기대 해시가 있을 때만 누락 여부를 검사해 이 오류를 놓쳤다.

뒤의 `bundle_impact_request()`는 누락을 발견해 일반 ValueError를 냈다. `apply_bundles()`는 당시 단계 이름이 currentness였다는 이유로 이를 `integration.currentness`로 분류했다. 이어 `failure_kind()`는 실패 종류를 `currentness_changed`로, `submission_outcome()`은 다음 처리에 사용할 결과를 `premises_changed`로 정했다. 그 결과 출력 오류의 수리 대신 입력 전제가 달라졌을 때 사용하는 새 판단 실행이 열렸다. 원 실행과 후속 실행의 대상 과제·목표·정책·허가·프로필은 같았다.

공통 검사 입력에 필요한 값의 전달, 누락된 필드의 검사, 실제 전제 변경과 제출 오류의 구별, 각 실패의 복구·재실행 경로를 함께 고친다. 같은 잘못된 제출을 사전·접수·적용 각 경로에 넣었을 때 공통 판단이 일치하는지 확인한다. 실제 내용·효력·권한이 달라진 사례는 그에 맞는 별도 결과를 내는지 확인한다.

### R6. Windows 명령의 올바른 예시를 실제 작업 문맥에 제공한다

Windows 명령 작성 시점에 작업자가 읽는 공통 실행 문서·역할 입력·도구 안내 중 적합한 위치에 올바른 표기 예시를 넣는다. 참고 문서를 만들었다는 사실보다 실제 명령을 작성하는 역할에게 전달되는 경로가 중요하다.

이번에는 cmd에 `\"경로\"`를 전달하는 형태가 파일 읽기 4건과 Python 호출 1건을 실패시켰다. PowerShell의 `Get-Content -LiteralPath`, 실행파일 호출 연산자 `&`, 공백이 있는 경로의 인수 처리와 cmd를 사용하는 경우의 정확한 표기를 실행 가능한 예로 제시한다. 예시는 파일 읽기나 `python --version` 같은 무해한 동작으로 확인한다. PowerShell, cmd, JSON 문자열의 인코딩을 섞어 설명하지 않는다.

### R7. 추가 세 문제를 각각 조사하고 수리·개선한다

1. 같은 파일을 한 패치 요청에서 여러 작업 대상으로 지정해 거부된 오류 2건: 실제 도구 계약과 작업자가 받는 지시·예시를 대조하고, 올바른 패치 작성과 필요한 수리 동작을 설계·반영한다.
2. Codex의 모델 목록 갱신 timeout 1건: 실제 실패 위치와 사용할 수 있는 진단 자료를 조사한다. 이 실행은 최종 응답을 제출해 수락됐으므로 모델 실행 전체 실패와 구별한다. 네트워크·공급자 내부 원인은 아직 미확정이다. 원인을 임의로 정해 timeout만 늘리거나 모델 목록 확인을 제거하는 방식으로 수리 완료를 선언하지 않는다. 확인 가능한 범위에서 적절한 개선과 검증을 수행하고 외부 원인 때문에 해결할 수 없는 부분은 실제 한계로 남긴다.
3. 상태 복원과 조회의 반복 Git 호출: 기록 복원 중 아직 읽지 않은 별도 payload마다 Git을 호출하는 경로를 조사하고 개선한다. 해시·정확 판본·입출력 검사를 보존하면서 호출을 묶거나 재사용하는 적절한 방법을 정한다. 실제 명령으로 개선 전후의 정확성과 호출 수·시간을 비교한다.

## 3. 확인된 증거와 확인되지 않은 사항

원장 기준 snapshot은 `811c4576af7fc8a5054181ad0208db42ddd329c6`이다. 당시 설치 manifest의 파일 291개와 감사 시점 설치의 해시가 일치했다. 원래 코드에 보존 입력을 넣어 해시 누락의 사전 검사 통과, 검사 문맥의 해시만 복구했을 때 오류 검출, 적용 검사에서 같은 누락 발견, 현재성 변경으로의 잘못된 분류, 운영 질문 기록만으로 큐가 생성되지 않는 동작을 재현했다.

scholarly의 실제 호출은 최초 준비의 list_sources, 마지막 계획의 list_sources와 describe_source(arxiv) 세 건이고 모두 성공했다. 도구 지원을 보류한 계약 검토와 후속 준비는 scholarly를 호출하지 않았다. 계약 검토자의 읽기 가능한 실행 목록에는 최초 성공 실행 ID가 있었지만 성공 근거를 읽은 기록은 찾지 못했다.

해시를 보완한 후속 모델은 도구 이름 다섯 개와 “도구가 노출되지 않았다”는 결론을 같은 파일에 썼다. 이 파일은 모델이 작성한 보고서다. 당시 공급자가 실제로 제시한 도구 목록 원본은 확보되지 않았다. 최초 미노출 인식과 후속 자기모순의 모델 내부 원인은 확정하지 못했다. 모델의 심리·고착·서버 장애를 확인된 원인으로 인계하지 않는다.

상태 조회의 격리 계측 한 번에서는 전체 38.717초, Git 하위 호출 274건에서 35.953초가 관측됐다. 이 시간들은 다른 중첩 측정값과 합산하지 않는다. 과거 기동·종료의 저장 자료 복원에도 약 101초·74초 구간이 있었다. 계측 한 번으로 전체 지연이나 비용을 일반화하지 않는다.

다음 자료는 모두 이 호스트에서 읽을 수 있다. 기존 실행과 감사 자료는 읽기 전용 증거로 사용한다.

- 사람용 전체 원인 보고: `C:\math\research\parking-unimodality-audit-2026-10-21\원인-분석.md`.
- 정확한 실행표·역할별 응답·부분 명령 오류: `C:\math\.skill-workspace\parking-unimodality-20261021\audit\executions.csv`, `execution-audit.json`, `subcommand-failures.json`, `mcp-calls.json`.
- 원본 함수 재현과 결과: 같은 audit 디렉터리의 `reproduce_causes.py`, `reproduction-results.json`, `shell-quoting-reproduction.json`.
- 정확한 조회 자료: 같은 audit 디렉터리의 `records.json`, `snapshot\` 전체, `installation-comparison.json`, `status-profile.txt`, `status-profile.pstats`.
- 원 실행의 보존 입력·CLI 출력·산출: `C:\math\.skill-workspace\parking-unimodality-20261021\work\runs\` 아래 실행별 디렉터리.
- 새 개발자가 우선 대조할 오류 실행: `EX-01M5CZSKE82FXDZJHKDYYB393R`(문헌조사 계약 검토), `EX-01M5D0ZPXND4CN3VV67DA6HGB2`(해시 누락), `EX-01M5D15WHYKST11MJ1JG3CNC47`(후속·자기모순), `EX-01M5D19Y02PMCZQPKPS32G4FF0`(성공 호출을 확보한 계획).

감사 보고는 증거의 안내다. 구현을 바꿀 때에는 연결된 실제 코드와 원 입력·출력을 읽는다. 처음부터 같은 조사를 반복할 필요는 없지만, 증거가 입증하지 않은 의미를 사실로 확대하지 않는다.

## 4. 공용 소스와 개발 범위

정본은 `C:\math\.claude\skills\do-math\`다. Codex 배포 사본은 `C:\math\.agents\skills\do-math\`다. 정본의 AGENTS.md, `scripts/이음새-정본.md`, `scripts/tests/시험-지침.md`를 작업에 맞게 읽는다. 변경은 정본에 수행하고 설치된 writing-skills의 공식 미러 생성기로 Codex 사본을 동기화한다. 생성기의 전체 스킬 비교에 필요한 소스도 작업 사본에 포함돼 있다.

수정 범위는 do-math의 코드·역할 계약·공통 문서·설정 및 응답 스키마·시험·예시·실행 안내와 그 공식 미러다. 조사·설계·검증 결과 문서는 이 RECORDS와 새 `docs/do-math/flow-repair-20261021/`에 둘 수 있다. 미러용 `.agents/diff` 변경은 기존 생성 규칙이 실제로 요구하는 경우에 한정한다. 서비스 자체나 scholarly 서버 코드에 수정이 필요한 구체적 원인이 확인되면 manager가 그 근거와 경계를 먼저 정리해 별도 writes 범위의 task로 배정할 수 있다.

사용자는 새 연구 인스턴스 사용을 선택했고 현재 그 연구를 정지했다. `C:\math\.skill-workspace\parking-unimodality-20261021\repo`와 `work`, 원 감사 자료, HOLD·예약 작업은 수정하거나 재개하지 않는다. 새 코드의 검증은 별도 임시 사본·시험 인스턴스에서 수행한다. 프리알파의 현행 계약 하나를 수정하는 개발이며, 과거 연구 기록을 계속 운전하려는 호환·변환 작업은 이번 목적이 아니다.

다른 작업의 수정과 자료는 보존한다. 시작 시 공용 Git HEAD는 `9c2dfca4fe89f52dedc1be45490b5adcda79ea79`였으며 `research/parking-unimodality-audit-2026-10-21/`가 미추적이었다. 그것은 이번 인계 전에 작성된 조사 결과다. task는 자기 workspace와 배정 writes 안에서 수정하고, manager는 서비스의 충돌 검사 통합 경로로 수용한다.

## 5. 설계·구현·검증의 판단

manager가 먼저 역할·작업 연결·공통 검사의 현재 구조와 수정할 경계를 파악하고, 필요한 공통 정의와 제공·소비 인터페이스를 `seams.md`에 구체화한다. 공유되는 규칙을 서로 다른 작업자가 각자 설계한 뒤 나중에 맞추게 하지 않는다. 공통 사항이 정해지면 실제로 독립적인 변경은 병렬로 배정하고, 결과가 필요한 소비자에게만 선행관계를 둔다.

검증은 바꾼 동작과 남은 불확실성을 판단할 수 있을 만큼 수행한다. 실제 소비 경로와 원 문제의 입력을 사용해 확인한다. 보고서의 필드 존재나 클래스 이름, 함수 호출 하나를 기능 전체의 완료 근거로 대신하지 않는다. 서비스의 최소 검증 원칙과 제품의 시험 지침은 불필요한 반복을 줄이는 데 적용하며, 사용자 요구를 확인하는 데 필요한 검사까지 생략하는 근거로 쓰지 않는다.

완료 판단에는 다음 결과가 필요하다.

- 역할 계약 모집단과 실제 파이프라인 연결을 검토하고, 목적·책임·판단·재량·인계의 적합성에 관한 유지·수정 근거를 남겼다.
- 정상 요청 처리와 예외에서의 재량이 구현·문서·상태 전이에 맞게 연결된다. 실제 수정할 내용이 없는 개정 요청을 적절한 처분으로 끝내는 경로를 확인했다.
- 운영 질문의 등록, 실제 작업 배정, 조사 결과, 해소, 영향을 받은 후속 업무가 끝까지 연결된다. 재시작·중복 전달·사용자 정지에서 필요한 동작을 확인했다.
- 사전·적용 검사의 공통 판단은 동일 구현을 호출하며, 각 위치의 추가 검사와 구별된다. 공통 입력과 오류 의미도 일치한다.
- 이번 해시 누락을 올바른 종류의 오류로 발견·처리하고, 실제 입력 변경은 별도로 처리하는 동작을 원 입력에 대한 대조로 확인했다.
- Windows·패치 작성 예시는 실제 해당 작업 문맥에 전달된다. timeout과 저장 조회 문제는 각각 조사한 원인·적용한 개선·실제 검증·남은 한계를 보고한다.
- 변경된 문서·스키마·코드·시험·공식 미러가 같은 현행 계약을 가리킨다. 수용된 구현 전체를 사용자 요구와 대조한 최종 review와 manager의 수용 판단이 있다.

모든 결과를 단지 “이번 보류가 사라짐”으로 판정하지 않는다. 실제 연구 목적에 기여하는 수행·검토·후속 처리로 이어지는지 확인한다. 불확실성은 조사 범위와 다음 판단에 필요한 자료를 명시한다. 구현자가 정할 수 있는 되돌릴 수 있는 세부사항은 재량으로 정하되, 사용자 요구를 다른 목표나 추가 필수 절차로 바꾸지 않는다.

## 6. 모델, 실행, 인계

이 개발은 대부분 `gpt-6.1-sol`로 수행한다. 어려운 설계·판정·구현에 필요하면 task의 `model`을 `gpt-6-astra`로 정하고 구체적 이유를 objective에 적을 수 있다. effort는 각 작업의 특성에 맞게 선택한다. 시작 구성은 manager Sol/high, worker 기본 Sol/high, 동시 task 상한 3이다. 이 숫자와 초기 effort는 준비자가 선택한 운용값이며 사용자가 직접 지정한 수치로 표현하지 않는다.

manager 0001이 최초 배정을 준비했고 manager 0002~0006이 저장 조회, 역할 설계, 공통 검사/해시 수리, Windows/패치 안내, Codex 진단, 역할·개정·운영 질문 구현을 차례로 수용했다. manager 0007은 `intent-check-evidence`의 39파일을 충돌 없이 통합·수용했다. 의도 검사 unresolved는 같은 원문/import_id/묶음 SHA의 자료 대기로, 실제 새 해소 영수증/자료 변화는 같은 묶음의 새 독립 check로 이어진다. 이전 check 봉인·이력·실제 해소/실행 계보·저장 첫 reader와 공식 미러가 연결됐고 provider 이음새 문구 보완도 완료했다.

manager 0008은 `integration-repair-check`의 정본/공식 미러 43쌍과 결과 문서 1개, 총 87파일을 충돌 없이 통합·수용했다. 알려진 구조 연결 3건과 통합 확인에서 드러난 catalog 해시의 저장 schema 투영·선택적 자식의 필수 부모 개정 의무 정산을 함께 수리했다. 정상/예외 및 실제 질문·의도·저장 fixture도 현행 생산자와 맞췄다. 현재 계획은 plan.md, 역할·개정·QU는 seams.md 1~2·13절, 의도 검사는 10·14절, 검사·저장·안내·진단은 3~5·11~12절을 따른다. 이번 정확한 추가 정의와 검증 범위는 seams 15절과 아래 14절이 제공한다. seams 7절은 최초 배정, 8~9절은 구현 전 설계 기록이며 context 7~13절도 각 manager 당시 기록이다.

이번 inbox의 실행 중 task는 없다. 구조 잔여와 관측한 통합 실패는 해소됐으며 새 `final-goal-review`는 수용한 전체 구현을 사용자 R1~R7과 실제 생산/소비·지급·상태 전이에 독립 대조한다. 추가 독립 기능이나 미수리 제품 결함은 이번 manager 검토에서 확인되지 않았다. 상태는 active이며 최종 review 수용과 manager 판단이 남아 있다. 판본별 선택 통과를 마지막 판본의 전체 회귀 성공으로 표현하지 않는다.

이번 사용자 대화의 역할은 입력을 제대로 작성하고 서비스의 실제 시작을 확인해 넘기는 데까지다. 서비스 시작이 확인된 뒤 대화 담당이 개발을 계속 따라가거나 manager를 대신하지 않는다. 개발의 후속 책임은 이 기록의 manager와 task 실행에 있다. 수학 연구의 정지는 유지한다.

## 7. manager 0001의 현행 코드 확인과 배정 판단

다음은 이번 manager가 공용 소스를 정적으로 읽어 직접 확인한 사실이다. 초기 감사의 재현을 새로 실행한 결과와 구별한다.

- `contracts.reading_map()`은 SKILL.md의 common 및 역할별 표를 실제 지급 문서로 사용하고 `prompt_documents()`가 문서 내용·해시를 읽는다. 현행 표에는 열 가지 내부 AI 역할이 있고 독립 운영/설치 복구는 별도 계약과 고정 프롬프트 경계다. 전체 모집단·실제 출력 소비의 적합성 평가는 첫 설계 task가 완성한다.
- `context_store`의 계획 역할 검사 문맥은 역할이 읽는 과제 목록을 원장 전체 과제로 교체한다. `integration.inspect_bundles()`는 기대 `content_sha256`이 참일 때만 고정 해시를 대조한다. 적용의 `bundle_impact_request()`는 해시 누락에 일반 ValueError를 내며 `apply_bundles()`는 명시적인 CurrentnessChanged 외에도 stage 이름으로 rule을 정한다. 따라서 공통 함수 자체와 별개로 입력 전달과 오류 의미를 함께 고쳐야 한다.
- `QuestionEngineMixin._record_output_questions()`는 질문 행을 만들고 이 함수 안에서 담당 action을 배정하지 않는다. `questions.link()`의 기존 중복 키는 origin execution/field이고 운영 담당 역할은 operational_review/maintenance다. `_apply_question_resolutions()`는 근거를 확인해 질문을 닫지만 개정 의무를 해소하는 전이는 별도로 설계해야 한다.
- `RevisionEngineMixin._apply_revision_followup()`과 필수 개정의 unchanged 검사에는 개정 의무·위임·대기 소유자를 보존하는 별도 경로가 있다. 예외 처분을 추가할 때 이 경로와 계약 검토·착수 판정을 함께 바꿔야 한다. 단순 enum 추가를 구현 완료로 보지 않는다.
- `ResearchRepository._read_documents()`는 비artifact 상태 파일을 read_many로 읽고, 아직 읽지 않은 payload는 read_bytes를 개별 호출한다. `GitStateStore.read_many()`는 이미 정확 commit의 blob 집합을 한 read_objects 호출로 읽는다. 개선은 현재 포트와 봉인 검증을 먼저 활용한다.
- Codex 어댑터의 수집은 종료 장벽 확인 뒤 stdout/stderr/final/status를 읽고 collection_reasons로 수집 결과를 구별한다. 모델 목록 timeout 자체의 내부 원인을 이번 manager가 조사 완료한 것은 아니다.

역할·개정·운영 질문의 새 공유 상태와 책임을 여러 구현자가 각자 정하지 않게 설계 작업 하나로 먼저 묶었다. 이 조사·설계는 R1~R3의 제품 완료가 아니다. 이미 경계를 확인한 공통 검사/해시 수리와 저장 조회 수리는 이 설계를 기다리지 않는다. Windows·패치 안내와 Codex 진단도 독립 배정으로 준비했다. 제품 코드 수정은 task가 자기 사본에서 수행하며, manager 0001은 제품 코드를 수정하거나 원 연구를 재개하지 않았다.

현재 settings.snapshot_paths에는 `docs/`가 포함되지 않는다. 수용 후 `docs/do-math/flow-repair-20261021/`의 산출물을 다음 task가 읽어야 하면 objective와 inputs에 공용 소스의 정확한 절대 경로를 명시해 읽기 전용으로 제공한다. 다른 task의 정리될 workspace 경로를 영구 입력으로 사용하지 않는다. task의 영구 report/evidence는 RECORDS에 남고 필요하면 서비스 restore로 정확 baseline/result를 새 경로에 복원한다.

## 8. 수용된 저장 조회 개선 — manager 0002

`batch-payload-reads`의 정본 코드·시험 및 대응하는 공식 미러 12개 파일과 설명 문서 1개를 `workspaces.py integrate`로 공용 소스에 반영했다. `repository._read_documents`는 고정된 같은 head에서 payload 경로를 최대 64개씩 기존 `GitStateStore.read_many`로 읽는다. `payloads.prefetch`는 확인된 snapshot 노드의 도달 가능한 참조 집합을 차례로 공급하고 기존 decode와 참조·노드·셀 검사를 공유한다. 외부 Git 포트, 상태 스키마, 업무 전이는 바꾸지 않았다.

task의 실제 Git 측정은 정확 snapshot `811c4576af7fc8a5054181ad0208db42ddd329c6`의 별도 저장소 복사본과 별도 Python 프로세스에서 수행됐다. 시험 종료 후 한 쌍에서 cold Git 자식은 260→23회, 경과는 31.261→3.677초였고 warm은 양쪽 0회였다. manager는 원자료 두 파일의 명령 수·성공 반환, 복원 논리 해시, 보관 파일 765개·4,399,529 bytes의 경로/길이/해시 일치를 직접 대조했다. 여섯 정본/미러 파일 쌍의 bytes도 직접 비교했다. 변경 코드와 선택 시험을 읽고 기존 해시·길이·정규 JSON·관계·저장 검사의 유지 경로를 확인했다. 선택 시험 58개의 최종 통과는 task 실행 기록에 근거하며 manager가 재실행한 것은 아니다.

원인·설계·한계·제품 이음새 문서에 옮길 문장은 `C:\math\docs\do-math\flow-repair-20261021\batch-payload-reads.md`, 영구 원자료는 `RECORDS/tasks/batch-payload-reads/evidence/`에 있다. OS 캐시/호스트 부하는 통제하지 않았고 이 한 쌍을 다른 연구의 성능으로 일반화하지 않는다. 경로 수 64는 byte 한도가 아니며 기존 snapshot 캐시의 용량 정책과 깊은 단일 참조 사슬 비용은 남는다. 전체 회귀는 수행하지 않았다. 제품 `scripts/이음새-정본.md`의 보완은 그 파일을 소유한 진행 중 hash task와 충돌하지 않도록 후속 통합 보완에 묶는다. 저장 기능의 추가 수리 결함은 이번 검토에서 확인되지 않았다.

## 9. 수용된 역할·연결 설계와 남은 제품 수리 — manager 0003

`C:\math\docs\do-math\flow-repair-20261021\role-flow-design.md`는 내부 AI 역할 10개와 동적 단계, 기계 action, 예약 감독 및 별도 설치 복구의 실제 입력·출력 소비를 연결해 유지/수정 근거와 구현 경계를 제공한다. manager는 문서 전체, report와 `evidence/inspect_current.py`, `evidence/current-observations.json`을 읽고 주요 결론을 현행 원 코드와 대조했다. `core_engine._apply`는 계약 검토의 비승인 두 값을 필수 개정으로 보내며, `planning.revision_required`는 현재 판본의 과거 비승인을 OR한다. `lifecycle_engine._refresh_readiness`는 같은 기초의 이전 검토가 있으면 새 검토를 억제한다. `questions.link`는 origin별 중복만 막고 `QuestionEngineMixin._record_output_questions`는 배정 없이 등록한다. `governance_engine._apply_governance_intent`도 모든 비승인을 재저작으로 보내며 `governance.check_import`는 기존 check 뒤 재검사를 거부한다. 이들은 정적 대조로 확인한 사실이다.

task의 제한 호출은 실제 지급 문서 10개 역할의 목록·해시, 같은 origin QU 1개/다른 origin의 같은 질문 QU 2개, 등록 뒤 빈 queue, 운영 질문 해소 역할 제한, required unchanged 반려 및 과거 부정+후속 승인에서도 revision_required=True를 기록했다. manager는 코드와 원자료를 대조했으며 이 호출을 재실행하지 않았다. 설계의 새 처분·배정·후속 전이는 아직 구현·실행 검증되지 않았다. 조사·설계 task의 수용을 R1~R3 제품 완료로 해석하지 않는다.

새 구현은 계약 검토의 실제 책임과 도구 확인 책임을 분명히 하고, unresolved와 실제 개정을 구분한다. AI 요청은 근거 있는 dismissed로 종결할 수 있으나 사용자 의무나 독립 승인을 대체하지 않는다. 운영 질문은 기존 QU 안에서 안정된 의무·원 보고·실제 action/execution·근거 처분·대기/이관·영향받은 후속 판단에 연결한다. 의도 검사에서 자료 부족이면 같은 정확 묶음의 후속 검사로 이어져야 한다. 설계 문서의 구체적 구조는 구현자가 고른 수단이다. 기존 구조로 같은 결과를 더 간단히 만들 수 있으면 관련 생산자·소비자를 한 계약으로 함께 고치고 이유를 보고한다. 고정 필드 수나 새 장치 구현 자체는 사용자 완료 조건이 아니다.

증거 소비의 추가 공백은 정적 분석상 발견이다. 제출 검사는 `workspace:` 근거를 허용할 수 있지만 질문 적용은 `_academic_evidence`로 기존 head를 읽으므로 이번 수집 파일을 못 찾을 수 있다. `role-question-flow`는 실제 candidate reader/봉인 파일을 작은 입력으로 확인하고 필요한 수리를 함께 한다. 현재 구현에서 이미 해결됐으면 불필요한 새 resolver를 추가하지 않고 근거를 보고한다. 저장 이음새의 자잘한 문구 보완은 같은 task에 묶었다. 원 연구·감사·HOLD·예약은 계속 읽기 전용이며 최종 review는 모든 구현 수용 뒤 남아 있다.


## 10. 수용된 검사 수리·실행 안내와 정확한 잔여 — manager 0004

`shared-validation-hashes`의 정본/미러 코드·시험·제품 이음새 20개와 결과 문서 1개를 충돌 없이 통합했다. `context_store.prepare_role_input`은 계획 역할의 전체 검사 tasks에 원장 `knowledge.content_hash`를 지급하고 비교 과제에서도 `content_sha256`을 유지한다. 공통 `integration.inspect_bundles`는 mutation 대상 부재, 검사 해시 부재·손상, 제출 previous_hashes 누락·불일치를 구별한다. live `bundle_impact_request`는 올바른 고정 선언 뒤 실제 내용 변경만 `CurrentnessChanged`로 전달하며 적용 단계 이름을 변경 증거로 쓰지 않는다. 실제 사용 효력·권한·정지는 기존 결정 전제와 현재 권한을 추가 검사한다. 출력 결함은 bounded 수리, 실제 변경은 refresh, 환경·게시 실패는 engine 대기, 깨진 검사 입력은 기존 운영 진단으로 연결한다. 새 질문/개정 처분 구현은 아니다.

manager는 변경 코드·시험·이음새를 읽고 원 입력 재현 `tasks/shared-validation-hashes/evidence/audit-replay.json`과 선택 시험 보고들을 대조했다. 원바이트 응답은 시작판의 premises_changed에서, 올바른 검사 catalog를 제공한 수리판의 output_rejected로 달라졌다. 정확 reader 해시 선언은 공통 검사를 통과하고 실제 live 내용 변경은 별도 premises_changed였다. 이는 공통 검사·별도 작은 실제 소비 시험의 근거이며 과거 응답 전체를 현행 schema로 적용한 성공은 아니다. task의 정지·권한 회수·사용 효력 선택 시험과 최종 owner/live-target 통과를 확인했으며 manager가 실행을 반복하지 않았다. 실제 보고의 repair-tests counts는 passed 66/failed 1이고 그 실패는 후속 수정·선택 통과 보고로 구별한다. 서로 다른 실행 통과 수를 합산해 전체 회귀로 표현하지 않는다.

`shared-validation-hashes`는 partial 보고 그대로 수용했다. 잔여는 `scripts/tests/unit/test_knowledge_impact_review.py`의 옛 오류 단언과 mutation catalog fixture 세 사례이며 기존 제품 검사를 우회하는 사유가 아니다. 정확한 보완을 미착수 `role-question-flow/objective.md` 마지막 절에 묶었다. 해당 task의 기존 tests/ 쓰기 권한으로 수행하므로 배정 정의·의존관계·실행 중 task를 변경하지 않았다. R4~R5 전체 완료와 전체 회귀 성공은 이 잔여 및 최종 통합 확인 전에는 주장하지 않는다.

`windows-patch-guidance`는 공통 실행 문서·읽기 시험의 정본/미러 4개와 결과 문서 1개를 충돌 없이 통합했다. 기존 common 지급 경로로 PowerShell LiteralPath/호출 연산자, cmd 실제 문자열과 외부 호출, JSON 해석, 한 파일 한 Update/여러 hunk 및 거부 후 재독 절차를 전달한다. task evidence의 무해한 명령·실제 패치 거부/성공 재독, 20개 역할/트리 프롬프트 전문 포함, 54개 선택 시험 통과를 검토했다. 원 패치 요청 본문과 내부 cmd wrapper argv는 확보되지 않았으므로 과거 거부 요청의 정확 형태나 wrapper 실패 원인을 확정하지 않는다. 미래 역할 준수·독립 운영 고정 프롬프트 전건은 이 확인 범위가 아니다.

두 task의 변경 정본/미러 12쌍 bytes를 manager가 직접 비교했고 모두 같았다. 영구 근거는 각 task의 report/evidence/integration 및 `managers/0004/verification-summary.json`, 판단은 `managers/0004/decision.md`에 남긴다. 소스 사본 정리 뒤 필요 파일은 서비스 restore로 복원한다. 원 연구·HOLD·예약·감사·graphify를 수정하거나 연구를 재개하지 않았다.

## 11. 수용된 Codex 목록 갱신 진단과 남은 범위 — manager 0005

`codex-refresh-diagnostics`의 정본/공식 미러 12개 파일과 결과 문서 1개를 충돌 없이 통합했다. `codex_stream.stderr_diagnostics`와 adapter 훅은 종료 장벽 확인 뒤 stderr의 인식 가능한 목록 갱신 timeout을 기존 결과 artifact의 `execution.collect.diagnostics`에 색인한다. 종류·CLI가 보고한 시각/수준·원 stderr 바이트 좌표를 제공하며, 기존 완료/실패·출력 수리·재시도 판정에 이 목록을 사용하지 않는다. 기존 `call_engine._receive_call`의 결과 보존을 소비하므로 중앙 상태 스키마를 추가하지 않았다. 정확한 제공·소비 의미는 seams 12절과 `C:\math\docs\do-math\flow-repair-20261021\codex-refresh-diagnostics.md`에 있다.

원 실행 `EX-01M5D097XN0TR7G5S582K1MKX4`는 CLI models-manager timeout 로그와 worker exit 0·정상 stdout/final·native 영수증·편입 수락이 함께 있었다. task의 원바이트/원장 대조 및 현재 adapter 재생 결과를 검토했다. 과거 종료 장벽을 Job 대역으로 재생한 것이며 현재 OS 종료나 새 모델 호출을 관측한 검사가 아니다. 네트워크/공급자 내부 원인과 목록 요청의 실제 기한·소요 시간은 미확정이다. 실행 원장의 467.066195초를 목록 요청 시간으로 해석하지 않는다. 외부 timeout 확대나 목록 확인 제거를 하지 않았으며 외부 원인을 해결했다고 주장하지 않는다.

manager는 실제 변경과 소비 코드를 정적으로 읽고 선택 시험 42 passed/complete=true/successful=true, 정상+로그와 exit 1/turn.failed/제품 기한 초과의 구별, 원바이트·색인 보존 근거를 검토했다. 통합된 두 제품 모듈의 해시가 선택 시험 report와 같고 정본/미러 6쌍의 bytes가 같음을 직접 확인했다. `check.py report`는 PASS, 통합은 13파일 성공이다. manager가 같은 제품 시험이나 live 호출을 반복한 것은 아니다. 영구 근거는 `tasks/codex-refresh-diagnostics/report.json`, `evidence/`, `integration.json`과 `managers/0005/verification-summary.json`, 판단은 같은 manager의 `decision.md`다.

R7.2의 조사·가능한 제품 진단 개선 범위는 수용했다. 작은 제품 이음새 문구 보완은 미착수 `intent-check-evidence/objective.md`에 묶어 정본/미러를 맞추도록 했다. 실행 중 `role-question-flow`의 배정은 그대로다. 독립 신규 기능의 필요는 이번 결과에서 확인되지 않았고 기존 의도 검사 task가 이미 준비돼 있다. R1~R3 구현·의도 검사 소비, 영향 검토 시험 잔여와 마지막 변경 후 필요한 최소 통합 확인·최종 review가 남아 있으므로 개발은 active다. 원 연구/HOLD/예약/감사/graphify는 변경하지 않았다.


## 12. 수용된 역할·개정·운영 질문과 실제 남은 결과 — manager 0006

`role-question-flow`는 정본/공식 미러 46쌍과 공용 결과 문서 1개를 제공했다. manager가 report·결과 문서·실제 코드/시험/역할 문서 변경을 대조한 뒤 `check.py report` PASS와 `workspaces.py integrate`의 93파일 무충돌 통합을 확인했다. 통합 bytes가 task 결과와 같고 정본/미러 46쌍이 일치하며 마지막 syntax 기록의 Python 35개 hash도 같았다. 제공 문서는 `C:\math\docs\do-math\flow-repair-20261021\role-question-flow.md`, 영구 근거는 `tasks/role-question-flow/report.json`, `evidence/`, `integration.json`과 `managers/0006/verification-summary.json`, 판단은 `managers/0006/decision.md`다.

계약 검토는 실제 수행 가능성과 지적의 타당성을 판단하며 수행자의 미래 도구 호출 성공·연구 결과를 사전 증명 의무로 만들지 않는다. 역할 모집단의 유지/수정 이유와 실제 common/role 지급 문서가 연결됐다. approved/revision_required/unresolved는 현재 승인·실제 개정·필수 판단 자료 대기로 분리된다. AI 요청의 근거 있는 dismissed는 대응 요청 출처와 부모/자기·실패 의무를 정산하고 필요한 새 독립 검토를 연다. 사용자 task_scope/revise 권위는 실제 결정에 결박돼 AI 기각으로 제거할 수 없다. 반복 충돌은 동일 기초의 자동 무한 검토 대신 실제 decision_conflict QU와 자료/영수증 대기로 남는다. 사용자 원 학술 계약의 개정 요청도 실제 수신자에게 전달하되 AI가 원 계약을 다시 쓰지는 않는다.

운영 질문은 descriptor/명시 QU와 원 보고를 보존하고 등록의 같은 CAS에서 실제 maintenance 또는 EX 대상 operational_review action에 연결된다. generation/고정 대상·execution/activity·봉인 근거와 resolved/superseded/waiting/transferred의 실제 수신자·조건을 보존한다. 새 보고는 live 입력을 바꾸지 않고 늦은 처분은 읽지 않은 대상/관찰을 닫지 않는다. 해소 뒤 계약 검토·보류 개정 준비·부모 handler·연구의 다음 계획에 실제 영수증을 연결한다. 질문 close는 독립 승인·개정 이행·연구 완료나 사용자 정지 해제가 아니다. 첫 reader·왕복·retention과 실제 처분 integration receipt도 새 의미를 소비한다. 별도 티켓 원장이나 구판 변환 계층은 추가하지 않았다.

후속 의도 검사는 `questions.question_scope_state(runtime, QU, target_ids)`의 `{resolved,resolution_refs}`와 자기 고정 scope·이미 읽은 영수증 basis를 비교한다. 다른 대상이 남아 있는 QU 전체 status와 이미 소비한 영수증의 단순 존재로 재검사를 반복하지 않는다. 근거는 `submission.resolve_output_evidence`/`_resolve_execution_evidence`로 이번 봉인 output_files의 artifact_ref/sha256/bytes와 실제 bytes를 검증한다. 정확한 제공·소비 정의는 seams 13절에 있다. 의도 check의 비승인 분기/check_history/import_seal은 아직 변경되지 않았다.

manager는 저장된 18개 공식 시험 report와 주장된 결과 행을 대조했다. 308개 역사 ID 중 writer 예약을 필수 수정 이유로 취급하던 두 ID는 현행 의미의 이름으로 교체됐고, 새 두 ID를 포함한 현행 306개 ID의 마지막 기록은 passed다. 이는 여러 시점의 선택 실행이며 최종 소스의 전체 회귀 인증이 아니다. 영향 검토 20개는 첫 실행 19 passed와 추가 fixture 수정 후 남은 ID passed로 확인됐고 고정 검사를 약화하지 않았다. 구조 probe verified/exit 0과 공식 미러 --check exit 0은 task 근거이며 manager가 같은 제품 시험을 다시 실행하지 않았다. 설치 복구는 검증 완료 영수증을 공급한 기존 writer/새 대기 reader 경계의 확인이고 실제 외부 복구 AI·검증 자체의 성공은 아니다.

남은 결과는 의도 검사 대기·후속 독립 검사와 작은 provider 문구 보완, 마지막 구현 수용 뒤 필요한 최소 T2+flows/실제 경계의 통합 확인, 최종 review다. 이번 수용에서 새 독립 기능이나 별도 제품 수리의 필요는 확인되지 않았다. 이미 준비된 의도 검사 작업의 실제 소비 지침과 영구 evidence 입력만 보완한다. 원 연구·감사·HOLD·예약·graphify 및 실행기 state는 변경하지 않는다.


## 13. 수용된 의도 검사 근거 대기와 통합 잔여 — manager 0007

`intent-check-evidence`의 정본/공식 미러 19쌍과 공용 결과 문서 1개를 통합했다. manager는 실제 변경·역할 문서·시험·보고를 읽고 check.py report PASS 및 integrate의 39파일 무충돌 반영, task 결과/공용 bytes 일치와 미러 19쌍을 확인했다. syntax의 Python 32파일 hash 및 final-scoped report의 Python 소스 hash 전부가 현재 통합 소스와 일치한다. 결과 설명은 `C:\math\docs\do-math\flow-repair-20261021\intent-check-evidence.md`, 영구 근거는 `tasks/intent-check-evidence/report.json`, `evidence/`, `integration.json`, manager 판단은 `managers/0007/decision.md`와 `verification-summary.json`이다.

의도 검사의 정상 approved는 기존 명시 승인/owner 적용으로, 실제 revision_required는 재저작으로, unresolved/불완전 승인은 import_check_evidence 대기와 실제 질문 담당으로 이어진다. 대기는 고정 question_scopes와 실제 읽은 question_resolution_basis/evidence_basis·원문/묶음/검사 SHA를 보존한다. 고정 범위의 새 해소 영수증 또는 실제 인용 자료 변화에서만 원 검사 수락·물리 종료·예약 반환 뒤 새 독립 check를 연다. 해소 기록과 action.import_check_release, execution.import_check_basis, check.reconsideration_ref가 실제 출처·실행 계보에 결박된다. bundle.check_history의 이전 봉인과 현행 check를 첫 reader가 검사하고 import_seal은 같은 원 해석 SHA를 유지한다. 같은 영수증/보고 수 증가로 반복하지 않으며 원문·적용 전제 변화는 기존 rework다. 초기화와 일반 입력이 같은 upkeep 규칙을 소비한다. 질문 해소·check 승인은 명시 사용자 승인·owner 적용·정지 해제를 대신하지 않는다. 제공/소비의 정확 정의는 seams 14절에 있다.

provider 문구도 실제 codex_stream/codex_adapter/call_engine 정의와 연결됐다. 기존 result.json의 execution.collect.diagnostics는 원 stderr 좌표의 부가 색인이며 실행 원장 최상위 필드가 아니다. 성공/실패·재시도·원격 종료·공급자 원인을 판정하지 않는다. 외부 timeout 원인은 여전히 미확정이다.

manager가 저장된 5개 선택 report의 실제 counts/결과 행을 대조했다. 네 의도 flow의 마지막 기록은 passed다. 서로 다른 시점의 선택 실행별 최신 203 ID 중 passed 200/failed 3이며 마지막 final-scoped는 passed 64/failed 3이다. 전체 회귀 성공으로 합산하지 않는다. 남은 구조 3건은 CLI 문서의 source.offset/bytes·turn.failed 및 execution.collect 소유자 연결, questions의 obligation_schema/resolution_schema/route_schema/wait_schema와 revisions.resolution_schema 선언 누락이다. 실제 원 실패와 관련 파일 시작판 동일 SHA 근거를 확인했으며, 새 통합 task가 수리와 필요한 확인까지 맡는다. 전체 T2+flows·필요한 실제 경계·최종 review는 남아 있다. manager가 제품 시험·외부 모델/학술/Lean·설치 복구를 실행하거나 원 연구·HOLD·예약·graphify·state.json을 변경하지 않았다.

## 14. 통합 수리 수용과 최종 독립 대조 — manager 0008

수용 결과는 `C:\math\docs\do-math\flow-repair-20261021\integration-repair-check.md`에 있다. CLI 진단 문서는 실제 결과 artifact를 `call_result`로 명명하고 실제 runner 반환의 직렬화 소비 시험에 연결했다. 실행 원장에 가짜 수집 필드를 추가하지 않았다. 질문/개정 schema builder의 인자별 형태와 가변 노드 독립성을 선언 모집단에 포함했다. 조건부 schema는 owner/disposition이 실제 있을 때 해당 추가 필수 필드를 요구하며 루트 필수 조건은 유지한다.

`planning.validate_plan_submission`은 catalog의 비교 과제를 새 객체로 투영할 때 표시용 `content_sha256`만 제외한다. 원 catalog의 해시·누락/불일치 검사와 다른 미등록 필드 반려는 유지한다. `revisions.resolved_targets(action,extensions,*,consumer_targets=None)`에 소비자의 의무 범위를 전달해 선택적 자식의 unchanged가 필수 부모를 종결하지 못하게 했다. 부모 개정 후속·자동 실패 정산·명시 해소가 같은 정본을 소비하며 실제 revised는 해당 필수 의무를 종결한다. 사용자 revise 권위와 다른 출처·대상은 기존 정산대로 유지한다. 정확한 정의는 seams 15절에 있다.

task는 공식 T2+flows 전체를 한 번 실행했다(4610개: passed 4482/failed 115/error 11/not_run 1/skipped 1, fixture error 1 별도). 관련 수리 뒤 선택 실행 179개는 passed 170/failed 8/error 1, 다음 실제 경계·잔여 32개는 passed 30/failed 2, 마지막 두 fixture는 모두 passed다. manager는 실제 report의 선택 ID·결과 행·fixture·counts·완결/종료 상태와 판본별 SHA를 직접 대조했다. 최초 비통과 127 ID 및 후속 관측 비통과의 미해소 항목은 없다. 여러 판본에서 관측한 최신 결과는 4618 passed/1 skipped이며 최종 판본 전체 회귀 성공이 아니다. 마지막 두 fixture 수리 전후 제품 Python 변경은 없고 최종 보고서 Python 930개 hash가 통합 소스와 같다. 실제 Git batch 복원 2개·CLI 결정 1개·설치된 제출 검사 도구 3개·고정 snapshot/문서 소비 CLI 2개도 task 기록에서 passed다.

manager가 check.py report PASS, 87파일 무충돌 integrate, 모든 변경 bytes의 결과/공용 일치와 정본/미러 43쌍을 직접 확인했다. probe verified 및 공식 미러 1394파일 drift 없음은 task 실행 근거다. Windows symlink 생성 권한 부족의 skip 1건은 해당 OS 동작 미확인이다. 마지막 전체 재실행·T3 full/T5·새 live 모델/scholarly/실제 Lean/설치 복구 AI·원 연구 재개는 수행하지 않았다. 원 snapshot의 Git 수/시간 한 쌍·무해 명령/실제 지급·Codex 원자료 재생은 선행 영구 근거의 범위로 유지하며 timeout 외부 원인은 미확정이다.

영구 근거는 `tasks/integration-repair-check/report.json`, `evidence/`, `integration.json`, `managers/0008/verification-summary.json` 및 `decision.md`다. 새 최종 review는 이 한계를 유지하며 역할 모집단·정상 처리/예외 재량·실제 후속 소비가 사용자 목적에 맞는지 판단한다. 제품 코드 수정은 맡기지 않으며 발견이 있으면 manager가 실제 사용을 막는 결함과 선택 개선을 구별해 후속 수리를 배정한다. 사용자 목표 충족·최종 review 수용·실행 중/미해결 task 없음이 확인되기 전 complete로 게시하지 않는다.

## 15. 최종 독립 대조 수용과 학술 지급 문서 잔여 — manager 0009

`final-goal-review`는 내부 AI 열 역할과 동적 단계·독립 운영/설치 복구, 실제 입력 지급·출력 소비·질문/개정 후속·공통 검사·저장/미러를 R1~R7에 대조했다. 주요 구현은 확인한 범위에서 요구에 맞으며 추가로 입증된 런타임 차단 결함이나 별도 독립 기능 필요는 찾지 못했다. 다만 실제 후보 준비에 지급되는 `계약/후보-준비.md:214`는 학술 revision_required 또는 unresolved를 평가·관찰 규칙 일괄 재준비와 현행 분리로 설명한다. `references/모델과-실행예산.md:68`, `references/CLI-실행-계약.md:144`의 일반화와 `계약/작업-계약-검토.md`의 관련 문구도 같은 변경에서 정리한다. CLI의 인접 contract_revision 설명도 자료 대기와 개정 처분을 같은 의미로 설명해야 한다.

manager는 F1의 실제 문구와 `core_engine._apply`의 unresolved/revision_required 분기, `planning_engine._ensure_model_assessments`, `contracts.prompt_documents` 지급 설명을 대조했다. unresolved는 기존 평가·규칙을 보존하고 `contract_review_input`과 실제 질문 담당을 기다린다. 실제 revision_required에서만 `revision_fields`를 소비한다. model_assessment와 initial_observation_rules는 지적된 필드만 history로 옮겨 보충하며, contract이면 사용자 원 계약을 보존하는 별도 요청 처리로 간다. 이 문서 불일치는 R1의 실제 역할 인계와 같은 현행 계약의 잔여이며, 엔진의 옛 삭제 동작이나 새 live 연구 재발을 발견한 것으로 확대하지 않는다.

리뷰의 `assessment.md`, report와 `evidence/{contract-consistency,edition-and-reports,original-evidence-comparison}.json`을 읽고 check.py report PASS 및 workspaces.py integrate의 변경 없음 기록을 확인했다. 리뷰는 기존 공식 보고의 선택/결과/판본, 최종 Python 930개 SHA 일치, 원자료 provenance, Git 비교를 읽기 전용으로 대조하고 공식 미러 1394파일 drift 없음을 직접 확인했다. manager가 새 제품 시험·벤치마크·live 호출을 수행하거나 이 결과를 마지막 전체 회귀 성공으로 확대하지 않았다. 최종 판본 전체 회귀/T3 full/T5·실제 모델/Lean 연구 효능·Windows symlink 권한 skip 및 외부 Codex timeout 원인 미확정의 한계는 유지한다.

후속 `academic-contract-guidance`는 위 네 문서와 대응 공식 미러만 수정하고 실제 프롬프트 지급·현행 코드와의 정적 대조·공식 미러 확인까지 한 작업으로 끝낸다. 기존 코드·schema를 옛 설명에 맞추거나 새 승인 절차를 만들지 않는다. `final-contract-review`는 수정 수용판에서 F1 해소와 이전 전체 리뷰의 유지 가능성을 독립 판단한다. 수정 범위가 문서에 머물면 전체 시험·원자료 재생을 반복하지 않는다. 영구 근거는 task 디렉터리에 남기며 정리될 workspace를 입력으로 삼지 않는다. 원 연구·감사·HOLD·예약·graphify·state.json은 변경하지 않는다.

## 16. 학술 지급 문서 수용과 최종 판단 대기 — manager 0010

이번 inbox의 완료는 `academic-contract-guidance` 한 건이며 실행 중 task는 없다. report·objective·실제 변경 문서와 `evidence/assigned-documents.diff`, `static-comparison.md`, 지급 확인 스크립트 및 저장된 지급 결과를 읽었다. manager가 `check.py report` PASS와 `workspaces.py integrate`의 8파일 무충돌 통합을 직접 확인했다. 제품 Python/schema/시험은 변경되지 않았다.

후보 준비의 기존 과제 보충 절은 상세 정본으로 유지된다. `unresolved` 자체는 기존 평가·관찰 규칙을 보존한 `contract_review_input`과 실제 질문 담당의 근거 대기다. 같은 계약의 고정 질문 범위 전부 해소와 읽지 않은 해소 영수증, 또는 실제 검토 근거 변화에서 새 독립 검토로 이어진다. 실제 `revision_required`는 `revision_fields`에 contract가 없으면 지적된 평가·규칙만 해당 history와 계약 판본·해시·원 검토 실행에 보존해 분리·보충한다. contract가 다른 필드와 함께 포함돼도 먼저 사용자 원 계약을 보존하는 일반 요청 처리로 간다. AI 요청의 근거 있는 기각·자료 또는 실제 사용자 결정 대기와 사용자 권위·독립 승인 구별을 유지했다. 작업 계약 검토·모델과 실행예산·CLI의 요약과 링크도 같은 의미로 정리했고 CLI에 실제 대기·요청/실행 ID 조회를 연결했다.

manager는 `core_engine._apply`, `planning_engine._ensure_model_assessments/_finish_assessment_preparation`, `question_engine._resume_contract_review_waits`의 실제 분기와 수정 문구를 정적으로 대조했다. 통합 8파일 bytes와 task 결과·integration SHA 일치, 정본/미러 4쌍 일치, 정적 근거의 코드 발췌 15개 SHA 일치를 확인했다. task의 정본/미러 각 두 역할, 총 네 지급 호출이 보존한 프롬프트 SHA와 각 8개 문서의 정확 전문·SHA를 통합판에 대조했다. 후보 준비/계약 검토에 수정 역할 계약과 예산 문서가 실제 지급됐으며 CLI는 이 두 역할의 직접 지급 목록 밖이므로 CLI 지급은 주장하지 않는다. 공식 미러 1394파일 drift 없음은 task 실행 기록이고 manager가 전체 생성기를 반복 실행하지 않았다.

문서 의미와 저장 지급 근거의 대조를 수용한 것이며, 새 런타임 전이·모델 준수·최종 전체 회귀·live 모델/학술/Lean 연구 효능을 확인한 것은 아니다. 기존 여러 판본의 시험 관측, symlink 권한 skip, Codex 외부 원인 미확정과 Git 한 쌍의 한계를 유지한다. 별도 독립 기능이나 추가 필수 제품 수리의 근거는 이번 검토에서 확인하지 못했다. `final-contract-review`의 기존 ID·정의·선행관계를 유지해 실행 가능하게 하며, 독립 최종 판단과 manager 수용 전에는 complete로 게시하지 않는다.

영구 자료는 `tasks/academic-contract-guidance/{report.json,integration.json,evidence/}`와 `managers/0010/{decision.md,verification-summary.json,verify_result.py}`다. 과거 파일은 서비스 restore로 복원하며 정리될 workspace를 영구 근거 경로로 사용하지 않는다. 원 연구·감사·HOLD·예약·graphify·state.json은 변경하거나 재개하지 않았다.

## 17. 최종 리뷰 수용과 개발 완료 — manager 0011

inbox 완료는 `final-contract-review` 한 건이고 실행 중 task는 없다. manager는 objective·report·assessment·비교 근거와 이전 전체 `final-goal-review/assessment.md`, 수리 문서 및 실제 코드의 관련 분기를 대조했다. `check.py report`는 PASS, `workspaces.py integrate`는 files=[]/changes={}로 기록됐다. 이 최종 review는 모든 work를 직접 또는 간접 선행으로 포함한다. 기존 task ID·정의·의존관계는 유지하고 새 배정은 추가하지 않는다.

F1은 해소됐다. 학술 `unresolved`는 기존 평가·관찰 규칙을 보존한 실제 질문 근거 대기다. 실제 `revision_required`는 contract 미포함 시 지적된 필드만 보충하며 contract가 다른 필드와 함께 있어도 사용자 원 계약을 보존하는 일반 요청 처리를 우선한다. 실제 지급 문서가 이 분기와 정상 개정·예외 재량·사용자 권위·독립 승인의 구별을 함께 설명한다. 이전 전체 리뷰가 확인한 역할 모집단/인계, QU의 실제 배정·근거 처분·후속, 의도 검사의 같은 묶음 새 독립 검사, 공통 검사·해시·복구, Windows/패치 안내, Codex 진단, 정확 snapshot Git 조회의 R1~R7 결론을 유지할 수 있다. 확인된 추가 필수 수리나 독립 후속 기능은 없다.

manager의 읽기 전용 대조에서 현재 공용 소스의 baseline 3,420파일이 최종 리뷰 판본과 모두 같았다. 이전 전체 리뷰 이후 차이는 이미 수용한 문서 8개뿐이다. 정본/미러 네 쌍, 저장 코드 발췌 15개의 SHA·전문, 저장 프롬프트 네 개의 SHA 및 각 현재 지급 문서 전문이 일치했다. 이는 판본과 저장 근거의 대조이며 새 프롬프트 생성·제품 시험·live 실행이 아니다. CLI는 두 역할의 직접 지급 목록 밖이므로 해당 지급을 주장하지 않는다. 서비스 state 읽기에서도 11개 task가 모두 exited였고 최종 review 외 10개는 이미 수용돼 있었다. 최종 review 수용으로 미해결 배정이 없다.

개발 목표 완료는 실제 연구 재개나 수학적 성과를 뜻하지 않는다. 여러 판본의 최신 관측 4,618 passed/1 skipped를 최종 판본 전체 회귀 성공으로 해석하지 않는다. 최종 전체 회귀/T3 full/T5·새 live 모델/scholarly/실제 Lean/설치 복구 AI·미래 역할 준수/수학 연구 효능, Windows symlink 권한 skip의 OS 동작은 미확인이다. Codex 외부 timeout 원인·요청 시간은 미확정이고 Git 비교는 기존 한 쌍의 범위다. 이 한계 외에 현재 결과 사용을 막는 추가 결함은 확인되지 않았으므로 새 blocker를 만들지 않는다.

영구 근거는 `tasks/final-contract-review/{report.json,assessment.md,integration.json,evidence/}`, 전체 목표 대조는 `tasks/final-goal-review/{assessment.md,evidence/}`, manager 판단과 직접 대조는 `managers/0011/{decision.md,verification-summary.json,verify_result.py}`다. 공용 context/plan/seams를 먼저 갱신하고 final-contract-review를 accepted에 더한 complete 임시 queue를 검사한 뒤 검사한 같은 파일을 원자 교체한다. workspace 보존·정리는 manager 종료 뒤 실행기가 맡는다. 원 연구·감사·HOLD·예약·graphify·state.json은 변경하거나 재개하지 않았다.
