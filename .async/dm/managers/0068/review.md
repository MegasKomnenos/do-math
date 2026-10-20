# 0068: 전체 T3의 부분 수용과 실제 미도달 후속

g5-full의 변경 없는 측정 결과를 부분 수용한다. 전체 시험은 4,288선택=고유 실제4,288행, 4,287passed/WinError1314 조건부skip1이며 fixture오류·failed/error/not_run은 없다. 그러나 123개 대상 중55모듈의517미도달arc/653행 때문에 branch_gate.passed=false·최상위passed=false·실제 runner exit1이다. G5는 미충족이며 queue는 active다. wrapper/task 프로세스 exit0을 제품 관문 성공으로 해석하지 않는다.

## 근거와 확인 범위

protocol의 manager 절차, 공용 context/plan/seams의 현재 상태·목표/G1~G8·자원/인터페이스, inbox, g5-full의 objective/report/judgment와 원측정 자료를 읽었다. inbox.completed는 g5-full 하나, running은 빈 목록이다. 기존 task 정의와 objective는 바꾸지 않는다.

manager의 `verify.py`는 제품 시험을 실행하지 않고 다음을 직접 대조했다. 결과는 `verification-review.json`이다.

- 원 report와 보존본 SHA는 `64bc19db1e0a50551ee281f4f22126906659d8584600d0441ae348a31ad434fd`다. selected와 reports[].rows는 중복·누락·여분 없이 대응한다. 실제 counts/fixture_counts·여섯 묶음/최상위 complete/successful과 invocation의 exit1을 확인했다.
- 원보고의912Python SHA가 작업 제출판·공용판과 같고, 수용 G4의 소스 SHA/선택과도 같다. changed_during_run=[]다. `check.py report` PASS, `workspaces.py integrate`는 files=[]를 기록했다. 제품·시험·문서 변화가 없어 기존 G4를 재사용한다. Git 준비2749blob·전체 snapshot을 새로 재감사하지 않았다.
- 현재 `do_math/layers.py:LAYERS`의1·2·3층123대상과 raw coverage를 대조했다. gate의55모듈·517arc·653행·기존제외15행이 일치하며 unmeasured_modules/measurement_missing는 비었다. gap-inventory의 모듈/좌표와 현재 미도달행 원문이 맞다. scope의 새제외는 없다.
- `branch_gate.py:gate`, `run_tests.py:closing_eligible/_finish_t3`를 읽었다. closing_eligible=true·store full/526측정모듈/재사용0·index생성은 측정 자격과 산출 사실이며, gap 없는 관문 통과를 의미하지 않는다.
- 보존48파일의 사본 SHA/크기를 대조했다. 이 중 외부 원자료46개도 원본과 같다. 나머지2개는 생성 index/timing으로 원위치가 의도적으로 base로 복원됐음을 확인했다. 후속은 preserved index를 읽어야 한다. manager의 최초 비교는 복원된 두 원위치도 측정 SHA와 같다고 가정해 실패했고, 보고된 복원 계약을 반영한 비교에서 통과했다. 측정원본 손상으로 판정하지 않는다.
- 공식미러 check의1375파일 drift없음/exit0 기록을 읽었다. 공식16183.8초·외부16184.578초·소프트초과1658행을 보존한다. 시간 초과를 기능 실패·중단·새 최적화 의무로 쓰지 않는다. 일부 native자식 원자료는 기존 cleanup 때문에 없으며 별도 보존을 주장하지 않는다.

유일한 환경skip은 `unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported`다. 이를 passed 또는 실제 outside_symlink 반려로 세지 않는다. 실제 환경 반려와 L01/G7는 남는다. 독립 로컬HEAD `6f8e260b221fa95a44d49b140c857e907c6f5ae4`는 공용main/통과 인증이 아니며 .git을 통합하지 않는다. manager 제품시험은0회다.

## 범위 판단과 사용자 교정의 적용

사용자 `sources/storage-scope-direction-2026-10-15.md`와 원설계3.3/A22·5.5·시간정정을 대조했다. A22는 실제 저장검증 상시화/공통구조검사/T3 쓰기분기 도달로 책임을 나눈다. 따라서 이번 실제 미도달은 구체적인 좌표에서 처리할 이유가 있지만, 저장 가족별 모든 생산자·필드·새reader·옛head를 다시 입증할 이유는 아니다. 기존 산출물과 공통codec/업무 단언을 재사용하며 취소2건을 유지한다.

미도달은 실행 가능한 정상 사례나 제품 결함이라는 뜻이 아니다. core_engine의 checkpoint 형식·복구/공개제어, record_schemas의 참조, context_store.safe_path, file_io의 OS 오류/재시도 등은 전제와 원인이 다르다. 공백을 직접 시험으로 보완하기 전에 현재 계약에서 불필요한 중복 방어/죽은 분기인지 검토한다. 필요한 공개 입력·저장·권한·현재성 검사는 보존한다. 원설계5.5는 의도적 미도달의 사유 있는 제외를 허용하지만, 임계값·층/분모 변경·무근거 no-cover·새skip은 해결책이 아니다. 현재 공백을 일괄 면제하거나 코드 결함으로 선판정하지 않는다.

g5-full은 objective가 허용한 여러 독립 영역의 큰 남김을 원자료와 함께 보고했다. 알려진 공백을 둔 전체 실행 반복이나 일부만 수정한 중간판 전체G4를 하지 않은 판단을 수용한다. 실제 수리는 다음 소유자에게 맡긴다.

## 새 배정과 남은 순서

| task | 원측정의 유한 범위 | 소유와 확인 |
|---|---|---|
| g5-core | core·생명주기·저장11모듈258arc/302행 | core_engine과 관련10모듈·직접시험/helper·README/정비/공통이음새·대응미러. 같은 큰 core 파일의 수리를 나눠 충돌시키지 않는다. |
| g5-inputs | 역할입력·계획·권한13모듈66arc/66행 | call/governance/payload/planning/provider/revision/역할입력·과제·대기·session 소유 코드와 직접시험/helper·입력/착수 문서·미러. |
| g5-io | 관찰·파일·프로세스7모듈63arc/93행 | context_store/file_io/observations/model_runner/operation_trace/parallel/scheduler·직접시험/helper·미러. |

각 task는 g5-full만 직접 선행한다. 세 작업의 파일 쓰기 범위는 겹치지 않는다. `assignment-scope.json`과 각 `gap-scope.json`이 정확한 경로·원좌표를 담는다. 기존 시험 파일은 관련 수리를 허용하는 상한이며 전부 수정/실행할 의무가 아니다. 기존 시험을 우선하며 신규 시험/helper 후보는 적절한 기존 자리가 없을 때만 쓴다. 수리·관련 확인·설명·미러를 같은 task에서 끝내고 별도 재확인/문서 task를 만들지 않는다.

세 작업에 각jobs1/시험슬롯1을 배정하여 합계3을 유지한다. 제품 시험을 더 실행할 수 있는 대역폭이 없어 worker·제어·CLI12모듈29arc/74행, 게시·지식·검토9모듈58arc/50행, Lean·신뢰3모듈43arc/68행은 준비된 후속 범위로 남긴다. 실제 선행이 아닌 task를 depends_on에 넣지 않는다. 다음 manager는 한 슬롯이 해제되면 남은 독립 소유 범위를 당시 공용판/실제 파일충돌에 맞춰 바로 게시하며 모든 동료의 종료를 기다리지 않는다. max_workers10과 worker gpt-6.1-sol/high는 그대로다. 지금 준비한 세 작업의 총범위는31모듈387arc/461행, 아직 미배정은24모듈130arc/192행이다.

이 단계는 가장 작은 기존 시험·필요하면 그 선택의 공식T3로 새 수리를 확인한다. 부분T3의 다른 모듈 gap/exit1은 전체 성공으로 세지 않는다. 자기 독립Git 준비는 측정도구가 요구할 때에만 objective의 범위에서 허용한다. 공개 원자료·상위Git·다른task·호스트권한은 변경하지 않는다. 전체G4/T3·전체변이·T4/T5·실예약·유료호출을 병행하지 않는다.

남은 공백을 처리한 최종 수용판에서 fresh 전체T3와 필요한 G4를 연결한다. G6는 최종 함수/색인의 모집단이 필요하므로 변이를 지금 수행하지 않는다. 현재 index는 정적 참고로 보존한다. G7의 실경계·L01/Windows1314, G1~G3의 최종 근거 연결, G8의 모든 work를 포괄하는 최종 review는 남는다.

## 게시

공용 context/plan/seams를 갱신하고 기존82개 task 정의·objective 및 취소2건을 유지한다. g5-full을 accepted에 추가해80개를 수용하고 새3개를 더해85개 task를 게시한다. 임시 queue를 `check.py queue`로 검사한 뒤 그 동일 파일을 원자 교체한다. 게시 뒤 이번 manager의 공용 변경을 끝낸다. 검사 exit·게시할 바이트SHA·원자교체 절차는 `publication.json`에 남긴다. `publish.py`는 교체 성공 뒤 그 사실과 SHA를 출력하고 종료한다.
