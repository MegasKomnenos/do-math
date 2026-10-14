# 전체 완료로 이어지는 현재 계획

이 파일은 현재 남김과 다음 판단을 관리한다. 상세한 과거 이력은 sources와 기존 repo 자료에 연결하고 여기에 반복 복사하지 않는다. 상태·근거·구체적 다음 질문 없이 '추가 감사 필요'만 적지 않는다.

## phase 001~022의 결과와 현재 상태

phase 001 세 분석 task의 A1~A4와 phase 002 mutation-baseline의 A1~A5를 manager가 검수했다. 정상 child의 증거 부재가 변이 포착으로 바뀌던 경로를 수리했고 관련 58개 시험 및 실제 child 19개 fixture의 원자료를 대조했다. phase 003은 공급자 smoke를 구현했으나 Codex schema 거부와 미러 원바이트 변형 때문에 partial이었다. Claude 최종 실호출과 정본 오프라인 23개 성공은 그 범위에서 승인했다. phase 004는 미러 치환과 양쪽 재생을 수리했으나 Git manifest 속성의 쓰기 범위가 부족해 A3를 완료하지 못했다. phase 005가 실제 하위 속성 두 파일을 고쳐 전88경로 raw/clean 동등성을 확인했고 manager가 A1~A3를 검수했다. phase 006은 원 의미를 보존하는 Codex 전송/수신 수리와 대표 실호출에 성공했다. 직접 소비11실패와 pair의 성공 표본 공백 때문에 partial이었다. phase 007이 현 fixture와 실제 분기 단언을 수리했고 manager가 A1~A5를 검수했다. 008은 운영/복구와 설치 지정 성과 A1~A4를 검수한 partial이며 그 A5의 기존 CLI 함수 표기4실패는009의 A1~A3 complete로 해소했다. 010의 host는 A1/A2/A4를 검수한 partial이며 관련61건의 두 회귀 문제는011의 새 양쪽136건 전부 통과로 해소했다.011 A1~A4를 검수했고 읽기 문구 반례도 종결했다. 읽기한도조사 완료/문구 수리와 L01/13-C 인증은 구별하며 실제 운전 프로필·출력 단위 결정은 남는다. 012의 Lean 실연쇄 A1~A4도 검수했다. 실제 대표 컴파일·verifier 정상/full 증거·타입 오류 및 정본/미러 각1 T5와 각48 회귀가 통과했다. 초기 두 도우미 오류는 역사 실패로 보존하며 설치 신뢰 승인으로 확대하지 않는다. 013 예약 A1~A4도 검수했다. 실제 held 등록/발화/wake/정리와 정본·미러 각33건을 승인했고, 초기3error 및 시계/OS stdout 관측 한계를 보존했다. live-final wake PID9492 원관측을 반영해 포괄적 미관측 표현만 정정했다. 014 학술 A1~A4도 검수했다. 최종 T5 1건·양쪽46회귀, 동일 native의 완료/양 본문/registry/격리와144corpus 경로를 승인했고 초기 두 실패·오관측의 적용 범위를 보존했다. 015는 T4 측정·양쪽70회귀를 검수한 partial이다. 015 당시 최종 T4 각295건의283통과·6오류·4실패·2skip은 역사 실패로 유지한다.016 두task는complete로 검수했고 정확10fixture/OS 실패가 양쪽 지정56passed로 해소됐다. Git 입력910파일 준비는 성공했으나 두 실제 비교와 양쪽 전체 T4는017 책임이다. 측정complete·부분회귀·입력준비와 전체기능 합격을 구별한다. 017은 A1/A2/A4 pass·A3 fail의 partial로 검수했다. 양쪽 두 exact 비교와 정본 raw6fixture/30snapshot/16DB는 성공했고015의12미통과는 새 양쪽 전체에서 passed다. 최종 정본294passed/1error·미러295passed이므로 Job cleanup 오류가 남는다. 초기 내부TEMP Git6실패와 긴resource cwd267은 같은 소스의 환경 대조로 구분했으며 원실패는 유지한다.018의 A1~A4도 검수했다. 종료확인 fixture 수리와 실제3상태/오류2경로, 정확1·양쪽관련27·양쪽전체T4 각295passed/exit0 및 각60worker 측정complete를 확인해 지정cleanup/T4 남김을 닫았다. 역사race와 bootstrap 원인미확인은 유지한다. 최종 전체일반/freshT3/전수변이 관문은 아직 실행하지 않았다. 현재 상태의 근거는 context C9~C12와 다음 자료다.

- 요구별 종료 질문: run:phases/001/tasks/closure-map/evidence/requirement-state.json. 원래 19/11/61/12 항목을 보존한다. 1-D/11-A/11-B 및 이미 검토한 부분은 최종 판본 연결로 넘기고 새 결함 없이 재구현하지 않는다.
- 기존 109작업·25영역 재검토: 같은 evidence의 tracking-state.json과 prior-review-state.json. PR23과 PR06/B22의 완료 범위를 재사용하고 필요한 slice를 실제 수리/의미 확인과 결합한다. 없는 임시 원보고의 counts는 역사 주장으로 남긴다.
- 문서의 고정 잔여: run:phases/001/tasks/document-closeout/evidence/followup-packets.json 및 binding-inventory.json. 후보15묶음을 고정 phase15개로 만들지 않는다.
- 관문 준비와 미충족 조건: run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json. 제안 명령의 출력 경로·최종 HEAD·검증된 모델 값은 실행 task가 실제 값으로 결속한다.
- 정상 기준 수리·직접 소비 검증: run:phases/002/tasks/mutation-baseline/report.json 및 run:phases/002/manager-evidence/verification.json. CLI/T3 공통 passed의 비통과, D9·failfast·정상 실패 제외·시도별 근거를 확인했다. 최종 G6는 이 판본의 baselines/attempt 구조를 사용한다. PR01 중 이 slice만 검토를 종결했다.

- 공급자 실호출의 부분 결과: run:phases/003/tasks/provider-smoke/report.json 및 run:phases/003/manager-evidence/verification.json. task 종료 2254파일과 원보고/실호출 원자료를 대조했다. F1 Codex 거부의 새 해소는006 결과에 있고 F2의 미러 후속 상태는 다음 항목에 있다. F3 background의 한정 재사용과 PR15/B86/B87 지정 slice만 승인했다.
- 미러 수리와 당시 Git 남김: run:phases/004/tasks/mirror-corpus/report.json 및 run:phases/004/manager-evidence/verification.json. 종료 2624파일과 변경 9개, 양쪽 14선택/14passed, 원자료 44파일·각 41개 SHA 참조를 대조했다. 생성 치환은 해결됐고 당시 하위 corpus/.gitattributes의 manifest text 예외가 남았다. 이전 Lean/scheduler clean 관찰은 경로 표기에 따른 차이이며 현재 슬래시 경로에서 보존된다.
- Git 원바이트 수리: run:phases/005/tasks/corpus-git-bytes/report.json 및 run:phases/005/manager-evidence/verification.json. 현재 종료 2624파일과 허용된 두 속성 변경, 양쪽 88경로 raw/clean·41개씩의 SHA 참조를 대조했다. 녹화·manifest 불변과 기존 각 14개/22개 재사용을 승인하며 phase 004 A3/F1의 남김을 해소했다. stage/제품 커밋 검증은 관리 마감 시 별도다. task 시작 전 protocol.md 차이는 제품 변화와 구별한다.

- Codex 전달 수리와 소비 시험 남김: run:phases/006/tasks/codex-schema/report.json 및 run:phases/006/manager-evidence/verification.json. 종료2640소스·허용50변경·9묶음의 실제 선택/row/exit·새 Codex1호출과11개판정을 대조했다. 최종 corpus 정본18개/미러14개와 전102경로 Git 바이트는 통과했다. 당시 직접 소비45개 중11실패와 pair의 두 성공 표본 공백은007의 새 근거로 해소됐다. 역사 report는 그대로 유지한다.

- 공급자 직접 소비 종료: run:phases/007/tasks/provider-consumers/report.json 및 manager-evidence/verification.json. task26변경·최종98/74/14/59선택의 고유 row/exit·이전11실패 해소와 pair red/green을 대조했다. raw 정상 대조와42malformed의 정확 오류도 승인했다. runtime124·smoke입력3·corpus는 불변이고 현재 차이4파일은 운영자의 모델 정책 변경이다. 제품124파일은007 관리 마감의 정확 stage·바이트 검증 뒤 HEAD78d9c6d에 커밋됐다.

- 운영/복구 문서의 지정 성과와 관련 회귀 남김: run:phases/008/tasks/document-recovery/report.json 및 manager-evidence/verification.json·review.md. 현재2640파일·허용30변경과8개 공식 실행을 대조했다. 정본110개106passed/4failed·미러89개85passed/4failed이며4실패는 기존 CLI 함수 표기다. P01 정상/오류/null/부재 및 N03-003 지정 문장 성과는 보존하고 전건 회귀와 제품 커밋은009 뒤 판단한다.

분류는 완료율이 아니다. 검토된 성질은 최종 증거 대기, 확정된 공백은 수리, 아직 모르는 성질은 한 종료 질문, 실행 관문은 최종 고정판 검증으로 구별한다. 오래된 109개 task를 그대로 재파견하지 않는다.

019 P02의 A1~A4를 검수했다. 실제 catalog/생산/저장/복원 결속과 양쪽187선택의186passed·권한1skip·exit0를 확인했다. P02 지정 남김을 닫고 symlink 실제 반려 미검사는 G4에 유지한다.28비캐시 제품경로를 관리 마감한다. 근거는019 manager verification.json·review.md다.

020 P03의 A1~A4를 검수했다. 실제 설치/최종 입력·양쪽 동일200선택의199passed/권한1skip 및875Python 판본을 확인했다. P03 지정 남김을 닫고 symlink 실제 반려 미검사는 G4에 유지한다.24비캐시 제품경로를 관리 마감한다. 근거는020 manager verification.json·review.md다.

021은 A1/A3/A4를 승인한 partial이다. 양쪽 같은270선택의269passed·권한1skip과 실제15반환을 검수했으나 answer/initial-0의 전문중복 기대1/실제2로 A2가 남는다. P05 필드/원자료 성과와 P04의 나머지는 유지한다.26비캐시 제품경로는 수리 뒤 검수까지 커밋을 보류하고 현재 바이트를 관리근거에 보존한다.

022 A1~A5를 검수했다. 전문중복의 독립 기대1을 실제반환 각80개에서 확인했고 P07 실제제출/반려/포장 결속을 승인했다. 양쪽동일364선택은363passed·권한1skip이며 이전270선택도 전부 유지됐다. 네절의 이름247개는 소유/정의 검토이고 다른packet 의미는 F5에 남는다.02126·02228 비캐시경로의 합36제품경로를 이번에 마감한다. 근거는022 manager verification.json·proposal-check.json·review.md다.

## 다음 phase: 023

gpt-6.1-sol/high document-governance 단일 work에 P06/P10 네owner를 묶는다. validate_import_units의 실제payload 소비와 check_import가 반환하는 bundle.check, governance_view의 유일한현재헌장과 academic_status의 조건별 결과를 문서에 연결한다. import_check.sha256와 submission_check.passed를 구별하고, 검사승인/사용자권한/실제적용·수학해결/학술후속완료의 차이를 유지한다. 관련 입력-소비자 서두/거버넌스절·초기화-운전6절·CLI의 수입승인/학술상태·공통-실행의 예정개정 절을 같은 경계에서 확인한다.

022 F5 중 N02-014의 impact_set/previous_hashes/revision_requests/revision_resolutions는 정확 문장·현재소비·기존검사로 충분성을 판정하고 빠진 축만 보완한다. runtime 수리가 필요하면 반례를 반환한다. 같은 doc_code/engine_context·문서순회·직접소비·미러/캐시를 한 담당자가 소유하므로 구현 병렬화는 하지 않는다. 기존packet과 현재코드가 종료질문을 제공해 추가조사task의 실익이 없다. 최종 관련 선택을 변경 영향으로 정하고 양쪽에서 동일선택을 완결한다. 이전364개에 계속 누적만 하는 고정명령을 만들지 않으며, 소유단언을 제외하려면 비소비 근거를 남긴다.

022의 runtime변경으로 과거전체설치/T4의 최종판동등성은 주장하지 않는다. 불변하위경계의 실호출 성질만 재사용하고 영향받은 검토slice는022의 새근거를 쓴다. L01 Q1/Q2·원문byte 미충족, G4권한skip·최종전체일반/freshT3/전수변이·G7최종판연결·최종review는 유지한다.

## 가까운 후속 배정과 선행 관계

**다음 배정에 적용할 사용자 지시(2026-10-14):** run:sources/document-batching-2026-10-14.md에 따라021 결과 이후 남은 문서 작업을 공유 helper·직접 소비·검사 범위별로 묶는다. 문서 번호마다 별도 phase를 만들지 않는다. 서로 독립적인 고정판 조사만 병렬화하고, 공유 구현·미러·관련 검사는 한 담당자가 통합해 반복 실행과 manager 마감을 줄인다. 새 장기 조사 없이 기존 packet/원문과 실제 쓰기 중첩으로 다음 묶음을 결정하며, 한 세션에서 끝낼 수 있는 범위를 유지한다. 현재021 작업은 재시작하거나 중간 확장하지 않는다.

**022 manager의 묶음 결정:** P06/P10을023에 함께 배정한다. 남은 P09/P11에는022 F5의 입력초과 해소/실패·question_links·요청/해결의 현재성과 사용자retry를 결합한다. N01-260의 scope/replay_safety/repair_target은 운영처분의 정확종료·재개권한 질문으로 그 후속범위에 유지한다. P08/TRUST와 다른 N은 별도후보다. 고정 phase표가 아니며023의 실제결과로 다시 정한다. 이미 검수한 P01~P05/P07은 새반례 없이 다시 열지 않는다.

007 공급자 변경과008~009 문서·시험28경로는009관리마감까지커밋됐다.010의 host/읽기 조사를 검수했고011에서 두 회귀 문제와 문구 반례를 수리·검수했다.010~011 제품20경로는011 관리 커밋571d282c로 마감됐다.012 Lean/Mathlib 제품20경로는 a8fb1e41로 마감됐다.013 예약 제품20경로는 8d0ade6c으로 마감됐다.014 학술 제품32경로는 eb701074로 마감됐다.015 T4 측정과016 fixture/OS 수리를 검수했다.016의Gitbaseline910파일과 새 양쪽56회귀를 승인하되 정확baseline 비교는017에서 통과했고 전체T4의 정본 Job cleanup 오류는018의 fixture수리와 양쪽295passed로 종결됐다.01512·01610·018fixture2의 합24비캐시 제품경로는018 관리커밋a29f3c6a로 마감됐다. 근거는016~018 manager-evidence/verification.json·review.md다. 그 밖의 구체적 남김은 아래와 같다. 먼저 해야 할 수리가 늘어나면 원래 G와 반례를 붙여 반환하고, 확인된 부분은 다시 탐색하지 않는다.

| 남김 | 다음 담당 작업과 끝나는 조건 | 선행/한계 |
|---|---|---|
| G1/G2/G3 공급자 단위의 최종 판본 연결 | 007에서 관련 회귀를 종료했다. 이후 변경이 그 경계에 영향을 주면 필요한 근거만 교체하고 G4~G7 최종 관문에 연결한다. | 006 Codex 대표 호출·003 Claude 한정 재사용과 역사 실패를 유지한다. 중간 회귀 합산은 전체 성공이 아니다. |
| G7 Job/pythonw 관련 회귀 |010 host정본3·미러3을 한정 재사용하고011의 실제 취소·네 음성 단언 및 양쪽136건 통과로 관련 남김을 닫았다. |010 실패 원보고는 보존한다. 이후 입력/경로 변경 시 재사용을 재판정한다. |
| G1/G3 읽기 문구와 L01 |011A3의 연속 접두/누락 구간/개별·합산 절단 문구 수리는 종료됐다. Q1/Q2의 운전 프로필·단위 결정 뒤 실제 읽기/한도 검증을 배정한다. | 현재조사complete는13-C인증이아니다. 원문byte기준은사용자답변전유지하며Claude실호출은미관측이다. |
| G7 Lean/예약/학술 |012의 실제 Mathlib·정상/오류·full 녹화/재생을 검수해 지정 Lean 범위를 닫았다.013의 시험 이름 등록·pythonw 발화·해제도 검수했다.014의 Codex worker를 통한 list_sources 성공 완료·전체 결과와 격리·녹화/재생도 검수했다. 각 경계의 최종 판본 재사용 조건을 유지한다. | 공유 manifest/캐시·생성기 의존을 순차화한다. Job/pythonw 성공·예약 cmdlet 대역·도구 판본만으로 대신하지 않는다. 설치 신뢰 승인/연구 검증은 Lean smoke 밖이고 held 예약 성공은 연구 운전 성공이 아니다. 학술 도구 시작 사건만으로 성공 응답을 판정하지 않는다. |
| G1/G3 문서 P01 및 전건 회귀 |008 지정 성과와009 정본110/미러89 전건 통과를 검수해 이 부분을 닫았다. | B132~B134 및008 단언 유지. 최종 전체 판본 연결은 G4~G6/G8에 남는다. |
| G1/G8 문서 N03 지정 문장 |008의 installation_root 전달 설명·bootstrap-info2건과009 회귀를 검수해 같은 문서 변경 단위로 인도한다. | 옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토. |
| G1/G3 나머지 문서·정책 | 019 P02·020 P03·021 P05 및022 P04 단일지급/P07을 검수했다.023이 P06/P10과 관련문장·F5의 개정 네 이름을 맡는다. P09/P11·P08/TRUST 및 F5의 다른의미/N 나머지는 후속으로 유지한다. 실제 반환/공유 계약·기존 시험에 연결한다. 명시 소비 없는 instance는 제거 가능성을 판정한다. | 34 AST 구문지점의 제거 수로 진척을 세지 않고 마지막 소비자 뒤 helper를 정리한다. |
| G7 T4 adapter 보고 | 015의 실제 측정/게시/병합과 현 adapter 전체 정보 보고를 검수했다. 각60worker·원DB 재분석과 양쪽70회귀를 유지한다. | 도달률은 임계 관문이 아니다. T4 기능 실패/skip 및 G5 fresh 최종 판본은 별개다. |
| G1/G3/G7 T4 fixture·OS 실패 | 016의 정확10실패/오류는017 양쪽 전체 T4에서 모두passed로 검수해 닫았다. 새 Job cleanup 한 오류도018의 종료확인 수리와 양쪽전체295passed로 닫았다. | Git WinError6은 관측자의 stdin 부수효과였다. 제품runtime/신뢰guard는 유지했고 과거bootstrap WinError5 원인은 미확인이다. |
| G2/G3/G7 P10/P11 실제 비교 | 017에서910파일 실제소비·양쪽각2passed와 정본raw6fixture/30snapshot/16DB를 검수해 이 비교를 닫았다. PR01 다른slice는 유지한다. | P10/P11은 여기서 역사/정확시험 표기이며 requirement-state ID나 문서packet과 다르다. 역사raw4개부재와 새 성공을 구별하며 미러 원fixture raw는 별도 보존되지 않았다는 한계를 유지한다. |
| G7 T4 실제 연결과015~016 제품 마감 | 018의 최종 정본/미러 각295passed/exit0·각60worker 측정complete를 검수해 지정 T4 연결을 닫았다. 기존22와018fixture2의 합24제품경로는018 관리커밋a29f3c6a에 포함됐다. | 부분합산은전체성공이아니다. 미해결실패/skip은정확후속work로넘기며G4~G8전체완료로확대하지않는다. |
| G4 조건부 symlink 미검사 |019~022 관련 양쪽의 Windows1314 skip은 실제 탈출 반려를 입증하지 않았다. 최종 기본전체에서 원문상 환경조건을 판정하고 미검사를 명시한다. |권한이나 G4 기준을 자의 변경하지 않으며 skip을 통과로 세지 않는다. |
| G1/G2 남은 의미 질문·과거 재검토 | requirement-state의 해당 생산자/소비자/입력/단언 질문과 관련 PR slice만 배정한다. 이미 충분하면 유지하고 빠진 축만 수리한다. | R05/R06은 현 test_provider_native_storage 경로 사용. 없는 원보고는 해당 slice에서만 회수/대체 증거 필요를 판정한다. |

원래 1-A는 설계.md의3.3절·결정 A20에 따른 필수+선택 역방향을 적용하고 역사 SHARDS/저장대역/timeout 표현은 현재 의미로 판정한다. 의미를 모르는 항목을 일괄 final-evidence로 올리지 않는다. G7이 외부 조건에 막혀도 독립 수리는 진행하며, 모든 행동이 막히면 context C7의 정확한 상신 절차를 따른다.

## 구현과 기존 작업 재검토

확인된 공백과 관련 과거 변경을 같은 한정 단위에서 처리한다. 25개 재검토 영역 전체의 완료를 모든 구현의 선행 장벽으로 만들지 않는다. 기존 실제 코드·시험을 재사용하고 source/diff/원보고가 입증한 성질은 계약 변경이나 새 반례가 있을 때만 다시 연다.

전체 범위는 다음 네 묶음으로 보존한다. phase 001의 구체적 종료 질문과 이후 결과로 가까운 순서를 정하며 무관한 발견으로 방향을 바꾸지 않는다.

1. 대기·계수·관측·정산: 모든 지정 상태 공간의 생성, 유지, 해소, 담당자, 후속 호출과 실제 표시.
2. 입력·평가·근거: 역할 변형, 실제 생산/수신, 판정 함수와 교란 축, 원래 평가자 쌍·보존/P2 기대값.
3. 소유자·시간·발동: 실패 격벽, 타 단위 진행, 시간 규칙의 국면, 대상·사건별 실제 발동/비발동.
4. 기동·문서·경계·규모: 설치/기동 판본, 문서 실제 계약, 필수 자료·읽기/출력 한도, 입력 규모와 읽기·해시·복사 비용, 실제 경계/말뭉치.

문서 검사기는 source-owner 전부를 임의로 지원하는 새 추론기로 키우지 않는다. 현재 원문이 참조하는 계약을 실제 반환/공유 계약에 연결하고, 불필요한 결속이나 중복은 제거 후보로 판정한다. DOC-RETURN-ROLE의 _context, REVIEW, TRUST와 이름·정책·읽기 한계는 서로 구분해 종료한다. AST 제거 개수는 전체 완료율이 아니다.

새 API/공유 계약을 병렬 개발하려면 먼저 seams에 실제 정본·의미·오류·공유 검사와 실제 연결 책임을 정의한다. 그 전에는 같은 phase의 미완성 구현에 기대는 검사를 배정하지 않는다. 반복 검증의 명확한 병목이 있으면 같은 경로·단언의 전후 근거로 그 좁은 병목을 개선할 수 있다. 예산만 맞추려는 우회는 하지 않는다.

## 최종 관문과 완료 review

필요한 실제 경계 호출·녹화와 코드 수리를 먼저 끝내 최종 판본을 고정한다. G4 전체 일반 → G5 fresh T3 → G6 정상 기준/현재 함수 전체 극단 변이의 근거를 확보하고 G7의 실제 경계·녹화 판본을 연결한다. G6 담당 작업이 fresh T3 뒤 현 함수·rule·trivial·선택 시험 manifest를 확정한다. context C11의 adapter5·runner2 제외 처분을 명시하고 layer1/2/3 변이 분모와 별도 검증을 혼합하지 않는다. 공유 pseudo_tested 목록을 쓰는 분할은 순차 실행한다. 오래된 함수 수나 분할 개수를 성공의 분모로 사용하지 않는다.

후속 변경이 생기면 어떤 기존 증거가 무효화됐는지 기록하고 그 범위의 검증을 교체한다. 최종 동일 판본 조건이 필요한 전체 관문은 필요한 시점에 다시 완결한다. 중간 부분 통과를 합산하지 않는다. 유효한 기존 실제 경계 결과의 재사용은 코드·도구 판본과 성질을 대조해 판단한다.

완성됐다고 판단하면 review kind의 phase를 배정한다. 고정된 제품을 대상으로 요구 충족/검출력·기존 개선 보존/실환경·인도 증거를 독립적으로 검토할 수 있다. 모든 G를 충족하는 근거와 미해결 finding의 처분을 manager가 확인해야 next:null을 제출한다. 문제를 발견하면 정확한 work task 뒤 다시 review한다. 검토 인원이나 반복 횟수 자체를 종료조건으로 삼지 않는다.
