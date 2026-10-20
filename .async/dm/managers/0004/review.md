# r18 조사 수용과 native 파일 교체 검사 수리 배정

0004 inbox의 완료 사건은 r18이다. 시작 당시 실행 중인 r02-fix·r07-fix의 spec과 입력은 유지한다. 이후 도착하는 완료 사건은 다음 manager가 처리한다.

r18은 R18/9-A 현재 호출 모집단의 조사 결과로 수용한다. `check.py report`는 PASS이고 `workspaces.py integrate C:/math C:/math/.async/dm r18`은 `{"task":"r18","files":[]}`를 기록했다. 새 제품 변경·제품 시험·외부 호출은 없다. 이 수용은 제품 전체 합격이나 최종 review가 아니다.

## 판단 근거와 한계

현재 file_io의 `_windows_files`·`_replace_once`·`atomic_replace`, 구조 모듈의 `_product_files`·`_sites`·`_is` 및 소유권/호출 등록 단언, 실제 `test_storage_atomic_replace`의 네 시험을 읽었다. task의 conclusion·boundary-map·predicate-observations·순수 AST 반례 및 판본/원보고 연결을 대조했다. `verify_sources.py`는 task가 기록한 workspace 소스 155파일을 공용 소스와 비교해 모두 같은 해시임을 확인했다. 보존 원보고의 해당 row도 직접 읽어 대조했으며 결과는 source-review.json에 있다. manager는 r18의 전체 AST 조사나 실제 경계 시험을 다시 실행하지 않았다.

F1은 현재 구조 검사의 실제 누락이다. `_windows_files`가 `kernel.SetFileInformationByHandle`을 rename으로 반환하고 `_replace_once`가 받아 호출한다. 기존 소유권 검사는 os.replace/shutil.move Attribute Call만 찾으므로 Windows native 호출은 발견 결과에 없다. file_io 외부에 실제 잘못된 교체 구현이 있다는 뜻은 아니다. 현재 owner는 올바르며 runtime 변경은 필요하지 않다.

기존 네 파일 경계 시험은 실제 Windows 파일을 사용해 열린 reader의 한 버전, 같은 교체의 재시도, 영구/부재 오류, Unicode/긴 경로와 길이 변경을 단언한다. 보존 018-c4의 지정 43행에는 이 네 passed가 포함된다. B85 원보고 3개의 구조 6행 및 010/012/013의 지정 3/1/1행도 원보고와 대응한다. 이 과거 실행을 현재 전체 설치·환경 인증으로 확대하지 않는다. B13/B14/B62 임시 원보고 9참조(8고유 경로)는 실제 부재로 남긴다.

r18의 직접2·주입7 프로세스 호출, _job_run6소비, sys.executable8함수, 공통 정규화7호출/6소비의 유한 모집단 판정을 유지한다. PR02 B13/B14/B62/B85의 지정 slice와 029 parser 이동 판정도 이 범위에서 수용한다. parser 비교 자료가 참조하는 현재 setup/probe 해시는 공용판과 같다. 다른 PR02 성질이나 관련 K/P2 전체, 전체 OS 경계의 무결함을 새로 주장하지 않는다.

## 후속 수리와 배정 경계

`r18-fix`는 r18만 선행이다. test_boundary_invariants 및 미러에 현재 native binding·alias 소비의 발견과 owner 판정을 추가하고, 정상 source·이동 반례 및 관련 구조 모듈을 확인한다. 구현 방법은 현재 구문을 다루는 최소 확장으로 정하도록 하며 범용 별칭 분석기를 요구하지 않는다. 소비만 다른 모듈로 옮겨도 같은 owner 판정이 적용되는지 현재 tuple 형태로 확인하게 한다. 반례·구현·설명·미러·필요한 확인을 분리 배정하지 않는다.

의미 있는 쓰기 파일은 r02-fix·r07-fix와 독립적이므로 다른 두 작업의 종료를 기다리지 않는다. 실행기 max_workers=3과 각 jobs1을 유지한다. 비용 캐시는 기록을 evidence에 보존하고 자기 base로 복원하여 부수적인 통합 충돌을 피한다. r07-fix의 정본 문서나 provider helper를 이 배정에서 수정하지 않는다. 독립적인 새 제품 기능 요구는 이번 결과에서 확인되지 않았다.

R18/9-A는 읽기 완료·F1 수리 대기다. K-10/11/24/28/61/66/76 및 P2 B-02/B-14/B-15 전체와 PR02 전체를 닫지 않는다. G4~G8, L01 Q1/Q2·UTF-8 byte, Windows1314 symlink 실반려 미검사와 기존 다른 의미 질문은 유지한다.

## 게시

context·plan·seams와 r18-fix/objective를 먼저 갱신한다. 기존 queue의 모든 task 정의를 보존한 임시파일에 accepted r18과 새 r18-fix를 추가하고 check.py queue로 검사한다. 검사한 임시파일을 queue.json으로 원자 교체하여 마지막으로 게시한다. 상태는 active다. 제품 변경이 없어 이번 manager의 제품 commit은 없다. 게시 뒤 공용 변경을 종료한다.
