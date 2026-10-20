# manager 0105 — G6 수리 통합과 최종 요구 연결

g6-finish의 complete 보고를 검수하고 정본36·미러36, 총72파일을 workspaces.py integrate로 충돌 없이 반영했다. 원 G6 모집단1677함수의 문제32개는 이전 해결10·정확 동등1·이번 해결21로 처분됐고 미해결/미실행은0이다. 이는 여러 보존 판본의 유효 결과를 연결한 판단이며 최종판 전체를 새로 실행한 성공이 아니다. 프로젝트는 G1~G3 연결과 G5/G7의 외부 조건·G8이 남아 active다.

## 변경과 판단

공식 restore로 기존32정본의 baseline을 복원하고 신규4파일을 포함한36정본 diff를 읽었다. 첫 restore는 신규파일을 baseline에 요청해 반려됐으며 baseline에 존재하는 경로만 요청한 두 번째 restore가 성공했다. 원자료·제품을 고친 오류가 아니다. accepted-diff.txt에 실제 차이를 보존했다. 기존31후보의 검토는0103/0104를 재사용하고 최종 변경과 대조했다.

mutation.run(..., function_selectors=())/main의 반복 --function module:key는 기존 AST 함수 키를 정확히 선택한다. 중첩·반복 이름을 기존 functions/changed_functions에 맡기고 모든 입력의 해석을 마친 뒤 child를 시작한다. 오타·범위 밖·변경범위 밖은 ValueError/CLI exit2이며 유효 입력의 기존 index+명시시험 선택, failfast, 정상 기준, jobs 합계상한과 listing 의미를 유지한다. 기본 호출과 잘못된 base의 exit1도 유지한다. 실행 뒤에는 선택 전용 오류형과 summary만 바뀌었으며 post-execution-diff.txt에서 확인했다. 유효 계획/child/판정이 같으므로21개를 반복하지 않았다.

예열 단계가 제품 오류를 fixture 오류로 가리던 경우 실제 소비자의 시험 본문에서 같은 생산물을 사용하게 했고, Sim은 Future로 원오류를 한 번 보관한다. 초기화의 기존 active/formal 미호출 단언을 유지하며 합성 action 수만32로 한정했다. Job 정리는 기존 runner 대기를 사용하고 제품 termination_confirmed는 직접 단언한다. 나머지는 실제 반환·효과·부적합 입력 단언 보강과 공유 요청 생산자 이동, callable 설명 수리다. runtime123모듈은 원G6와 동일하다. 저장 가족별 quota나 새 검증 프레임워크는 추가하지 않았다.

## 확인한 근거와 재사용 범위

inspect_result.py와 verification-review.json은72변경의 baseline/통합 전 공용/결과SHA,36미러쌍 동일바이트, runtime123SHA와 최종924PythonSHA를 대조한다. 통합 뒤에도72공용바이트가 제출판과 같음을 확인했다. check.py report는 PASS, integrate는72경로 충돌0이다.

7개 정확 명령의 native exit0/source_unchanged, jobs3/interrupted=false/baseline_failing=[]와 정확 선택을 읽었다.21개는0104 pending의 module/function/rule과 누락·중복 없이 일치한다. 각 원 attempt.json/result.json에서 finished·exit0, 실제 비fixture 변이 실패행과 해당 baselines ID의 정상passed행이 killed_by와 대응하는지 직접 대조했다. 최종 선택기2ID는 complete/successful·2passed·fixture0이며 source_sha256이 제출924Python과 같다. CLI 오타exit2·기존 invalid-base exit1, listing의 정확동등1개와 무조건None 구현도 확인했다. 초기 선택기와 최종 결과는 합산하지 않았다.

기존1613killed/32trivial와 이전10해결, 후보의 단언보존/재사용 영향은0103/0104의 수용 근거를 재사용한다. 원selection ordinal·추가시험 합집합의 상세 비교, 독립Git/index 준비, generated10파일 복원, 공식전체미러1388 check는 worker의 보존 근거를 재사용한다. manager 제품시험·실호출·환경probe는0이다. repair-b09 부모는 여전히 미완료이고 이전 세 개별 child만 유효하다. g6p-run은 cancelled·미수용으로 불변 보존한다.

## 다음 작업과 종료 조건

독립된 두 유한 연결 작업을 배정한다. g1-close는 g1-handoff의 원30의무와 이후 수용delta를 현행 정의/기존 G4~G7 증거에 연결한다. g23-close는 g23-handoff의 K61/P2 12·PR25를 이후 역사/기반 review 및 G6 수리에 연결한다. 두 작업은 writes=[]·시험슬롯0이며 서로를 선행으로 요구하지 않는다. 기존 검토를 다시 수행하거나 문서 번호별 task·새 전수감사를 만들지 않는다. 실제 결함을 새로 발견한 경우에만 정확 입력·경계·필요 수리를 보고한다.

이 연결은 인도를 판단하는 데 필요한 남은 결과다. 새 독립 제품결함은 이번 결과에서 발견하지 않았다. 원G4의4522passed/1조건부skip와 전체T3, 정확T4 세입력 및 예약/공급자/Lean/학술의 유효한 성질은 기존 판본 범위에서 재사용한다. 단순 최종판 표기를 이유로 전체일반/T3/T4·변이·실호출을 자동 반복하지 않는다. G4의 최종판 요건을 없애지는 않으며 새 변경과 기존 실행 근거 사이 실제 남김을 g1-close가 구체적으로 구별한다. 다음 T3는 지정5모듈 관련추가만 가능하고 환경6arc/10행·부분index/자동store 제약을 숨기지 않는다.

G7의 현지원 quota/복수result/동적 역할schema 원자료, L01 Q1 운전프로필·Q2 원UTF-8 출력byte 기준, 실제 symlink/POSIX 조건은 아직 입력이 없다. 같은 probe·질문·호출quota를 반복하지 않고 기존 정확 질문과 미충족을 유지한다. 과거 외부 비의도 설치물의 정책거부 정리는 별도 운영 남김이며 이번 삭제는 없다. 두 결과 수용 후 실제 남김을 판단하고 모든 수용work를 선행으로 하는 제품수정 없는 G8 review를 준비한다. 독립 진척이 가능한 현재는 blocked/complete가 아니다.

## 게시

inbox는 g6-finish 종료0·running0이다. 기존123 task 정의와 objective는 불변이다. accepted에 g6-finish를 추가하고 g1-close/g23-close를 준비해125정의·accepted117·cancelled6·미해결2로 게시한다. 모델 gpt-6.1-sol/high·max_workers10·시험worker 총3상한을 유지한다. 공용문서와 objective를 먼저 갱신하고 queue.pending.json 검사 후 같은 파일을 원자 교체한다. 게시 후 이번 manager의 공용 변경을 끝내고 workspace 정리는 실행기에 맡긴다.
