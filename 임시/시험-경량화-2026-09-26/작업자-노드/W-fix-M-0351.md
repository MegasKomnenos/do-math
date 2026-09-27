---
worker_id: W-fix
layer: 1
title: do-math 시험의 시작 상태를 프로세스당 한 번 만들고 같은 절대 경로에 복원하는 공유 기반
convention_version: 27
---

## 맥락

do-math 시험 경량화 작업(공통 계약 `임시/시험-경량화-2026-09-26/계약.md`)에서 W-fix 작업자로 시험 기반을 맡았다. 작업은 worktree `C:/math-worktrees/t-fix`, 브랜치 `t-fix`에서 했다. 대부분의 무거운 시험은 시험마다 공개 활성화(`research_fixtures.activate`: 제어 여러 건과 해석 실행 2회)를 처음부터 다시 돌렸다. 시험마다 `git init`과 CLI 자식 프로세스도 띄웠다. 임무는 두 가지였다. 이 반복을 없애는 공유 기반을 만들고, `test_purpose_engine`·`test_engine`에 적용해 효과를 보이는 것이다. 나머지 모듈은 다음 단계의 작업자가 fixture docstring만 보고 옮긴다.

만든 것은 다음과 같다.
- `research_fixtures.restore_template(build, **parameters)`: `build(root, shared, **parameters)`를 프로세스당 한 번 돌린다. 그다음 매 호출마다 같은 경로 `root`에 빌드 결과의 바이트 사본을 복원해 `(root, value)`를 돌려준다.
- 준비된 빌드 두 개: 공개 활성화 `activated_instance`와 합성 활성 `state_fixtures.active_instance`.
- 자식 프로세스를 대신하는 도우미 두 개: `git_init`(빈 `.git` 복사), `run_cli`(`cli.main`을 프로세스 안에서 호출).
- 하네스: `test_purpose_engine.ActivatedPurposeHarness`의 `make`와 `make_active`.
- 기반 계약을 지키는 시험 하나: 복원본이 게시 상태와 같은지, 서로 독립인지, 캐시가 비워진 뒤 load되는지를 본다.

## 터득한 것

**경로를 치환하지 않고 같은 절대 경로에 복원한다.** 상태 안의 절대 경로(작업공간, 제어 inbox, 신뢰 toolchain과 기록)는 Git 커밋과 내용 해시에 들어 있다. 불변 레코드(`execution_profiles`, 신뢰 기록 ID)도 이 경로에 걸려 있다. 그래서 경로를 치환하려면 해시를 다시 계산해야 하고, 불변 레코드는 고칠 수도 없다. 시험은 한 프로세스 안에서 차례로 돌므로, 템플릿마다 고정 경로를 하나 두고 매 시험 그 경로를 지운 뒤 원본 사본을 다시 복사하면 된다. 이렇게 하면 복제본은 제품이 실제로 게시한 바이트 그대로가 되어 `do-math-state/6` 검증을 그대로 통과한다. G2 분석도 같은 결론에 이르렀다.

**복사하면 안 되는 파일이 있다.** 신뢰 환경의 지문은 `file_io.stat_fingerprint`의 (크기, mtime, 생성 시각)이다. 복사본은 생성 시각이 달라지므로 지문이 어긋나 환경이 바뀐 것으로 판정된다. 그래서 빌드가 신뢰 파일을 복사 대상 밖의 `shared`에 두게 했다. 제품은 신뢰 기록을 쓰지 않으므로(`write_record`는 `setup_lean.py`만 부른다) 이 파일은 불변 공유 입력이다. 합성 경로에 이를 적용하려고 `active_engine`에 `trust_root`를 더했다.

**같은 경로를 재사용하면 제품의 프로세스 캐시가 시험 사이에 샌다.** git_dir 경로를 키로 쓰는 캐시가 네 개 있다(`repository.VERIFIED_ARTIFACTS`, `_VALIDATED_READS`, `planning._VALID_ARTIFACTS`, `submission._ISSUED_INPUTS`). 복원할 때마다 그 경로의 항목을 지운다. 그러면 새 엔진이 복원된 head를 처음부터 전체 검증한다. 제품에 경로 키 캐시가 새로 생기면 `forget_repository_caches`에 더해야 한다.

**조기 종료를 판단할 때는 러너 안의 검사도 단언으로 센다.** 처음에는 `test_objection…`을 knowledge가 사용 가능해지는 시점에서 멈추게 했다. 그러나 `PurposeRunner`의 `goal_audit` 응답은 효력 있는 최종 identity 판정만 받았는지 검사하고, 아니면 예외를 낸다. 이의 제기 뒤에 이 검사가 도는 시험은 이 시험 하나였다. 그래서 끝까지 몰도록 되돌렸다. 이 판단 기준을 docstring의 조기 종료 절에 넣었다.

**`owner_calls`의 60초 대기는 실측으로 확인했다.** `ControlTransport.wait_receipt`를 계측해 보니, scope 호출이 영수증 없이 60.02초를 기다렸다. 그 뒤 러너가 AssertionError를 냈지만, 호출이 끝난 뒤의 한 번의 펌프가 의도를 게시해 준비가 이뤄지는 우회 경로였다. 고친 내용은 소유 루프처럼 루프마다 `engine._transport.pump`를 부르는 것이다. `test_walkthrough_followup…test_failed_review_slot…`이 90.3초에서 28.9초로 줄었다.

**시간 비교는 부하 때문에 믿기 어렵다.** 같은 기계에서 커버리지 기준선 실행과 다른 작업자들이 함께 돌았다. 코드를 바꾸지 않은 공개 경로 시험이 63.2초, 30.5초, 39.0초로 흔들렸다. 그래서 효과는 같은 프로세스 안의 직접 측정으로 보였다.
- 공개 활성화 템플릿: 빌드 44.8초, 복원 1.3~1.5초, 엔진 load 0.9초.
- 합성 활성 템플릿: 빌드 2.9초, 복원 0.3초.
- 자식 프로세스: `git init` 0.10초에서 0.02초로, CLI `--help` 1.10초에서 0.04초로, `status` 2.15초에서 0.60초로.
- 모듈 합계(부하 아래): `test_purpose_engine` 2753초에서 2131초로, `test_engine` 587초에서 499~519초로.

마지막으로 고친 fixture를 넣은 `test_purpose_engine` 최종 전체 실행은 사용자 지시로 중단했다. 그 뒤에 이 모듈에 닿은 변경(키 정규화, 값 복사)은 `test_engine` 최종 실행이 같은 경로로 통과시켰다.

## 남은 것과 경계

- `test_formal_requires…`가 222초에서 256·259초로 느렸다. 정적 분석으로는 템플릿이 준비 비용을 줄였을 뿐 시나리오의 입력을 바꾸지 않았다. 다시 재지 않았다.
- 회귀 16개 모듈 304개 시험에서 오류 5건이 났다. 1건은 기준 목록의 `every_call_budget…resume`이다. 나머지 4건은 379a171에서도 같은 증상으로 실패함을 stash로 확인했다. fe59ca0 기준 목록에는 없다.
- 이 노드 번호는 병행 작업자 브랜치와 겹칠 수 있다. 통합 때 확인한다.
- 측정 로그 `C:/math-worktrees/t-fix-measure/*.log`는 저장소 밖 로컬 자료이며 정리로 사라질 수 있다. 수치는 이 노드와 반환 보고가 정본이다.

## 작업 너머 시사점

- dream에서 묶을 후보: [[L-0001]]의 "시험 전제·검사 경계 보존"에 두 가지를 잇는다. 스크립트된 러너 안의 예외 검사도 시험의 판정 대상이라는 점, 그리고 준비 단계가 실패한 채 우회 경로로 통과하던 시험(`owner_calls`)이다. 통과만 보면 준비 경로가 실패하고 있다는 사실을 놓친다.
- dream에서 묶을 후보: [[M-0348]]의 tfix(공개 활성화를 합성 상태로 대체)와 이 노드의 템플릿(공개 활성화 결과를 복제)은 같은 비용에 대한 두 해법이다. 복제는 합성과 달리 실제 경로의 산출을 보존하므로, 합성 대체가 판정을 바꾸던 시험에도 쓸 수 있다.
