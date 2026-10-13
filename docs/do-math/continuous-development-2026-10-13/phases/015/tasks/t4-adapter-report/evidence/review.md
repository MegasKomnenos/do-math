# T4 보고 구현과 검토 범위

014 manager의 source-inspected 2750개가 시작 시 현재 바이트와 모두 일치했다. 설계5.1/5.5/8, phase001 gate-readiness와 현재 TIERS/LAYERS, main/_isolated/_worker 및 Measurement 생명주기를 대조했다. 수정 전 실제 T4 clock10건은 통과하지만 adapter 보고가 없었다. 같은 실제 runner/worker를 소비하는 새 회귀는 t4_adapter KeyError로 red였다. 보고 부재와 시험 실패를 혼합하지 않는다.

## 현 구현

adapter_coverage.AdapterMeasurement는 기존 Measurement의 coverage branch tracer, fixture/test 문맥, D5 unmeasured, save 생명주기를 재사용한다. run:include를 현재 LAYERS의 adapter 파일로 좁히고 source=는 해제한다. 분석 morfs에는 전 adapter를 명시해 도달0인 파일도 소스로 분모를 얻는다. 기존 REASONED_EXCLUSION과 빈 partial_branches 규칙을 유지한다. 도달률은 임계 관문이 아니다.

T4 jobs1 단독은 인프로세스 boundary의 실제 시험/fixture를 관측하고, resource/lean 클래스는 실제 WindowsJob worker에서 discovery부터 관측한다. worker의 coverage.data/opened.json/entered.json을 유지하면서 adapter-measurement.json이 실행 ID·요청·시작 Python 소스판본·종료판본·게시파일 SHA를 결속한다. 같은 validate_publication을 게시자와 소비자가 호출한다. 수신자는 SQLite branch 데이터도 직접 연 뒤 합친다. 부재/파손/다른 실행·요청/종료판본은 invalid와 원경로/사유를 남기고 부분 합집합을 만든다. 완전성이 거짓이면 시험 successful과 별개로 runner exit1이다.

jobs2와 여러 tier 합집합은 boundary를 별도 worker로 보낸다. T3 부모가 측정하는 동안 T4 worker의 생성·대기·읽기는 unmeasured 안에서 수행한다. T3 finish의 시험 모집단은 TIERS[T3]로 제한한다. T4 자료는 T3 gate/index/store/변이에 흡수하지 않는다. boundary 측정 비용은 기존 일반/T3 캐시에 기록하지 않는다. T4 전용 병렬 시간은 boundary 묶음에 한번만 집계하며 일반 T3 parallel 시간을 덮지 않는다. 측정하지 않는 merger의 _stop은 활성 측정기를 비우지 않도록, 자기 활성 상태만 해제하고 정지를 멱등으로 했다. 이 생명주기는 기존/새 회귀로 확인한다.

## 실제 회귀와 실패 보존

native 표본은 공식 runner, 실제 subprocess/WindowsJob worker, 실제 coverage·게시/병합/분석을 사용한다. SystemClock.wall과 WindowsJob.resume의 현재 함수 본문행을 AST로 구하고 실제 도달행과 대조한다. 별도 jobs2는 parent Job 생성/inspect/resume의 거짓 도달을 반려한다. T3 단독과 T3+T4의 작은 full 선택(전체 T3가 아님)은 실제 gate/entered/store를 같게 만들고 boundary ID 부재를 검사한다. 누락 파일 주입은 실제 worker가 종료·게시한 뒤 DATA만 지우는 외부 실패 주입이며, 시험10passed/시험successful=true에서도 측정complete=false/exit1을 확인한다. 임의 대역 측정/미리 만든 보고로 대신하지 않는다.

실제 한 worker 게시를 정상 대조로 사용해 부재·파손 JSON·다른 run·판본·request·digest를 맞춘 파손 SQLite를 각각 반려한다. 실제 측정 중 실패/skip/fixture error/미실행 표본은 coverage가 완료돼도 기존 시험 row와 successful=false를 유지한다. synthetic 결과를 새 실경계 성공으로 표시하지 않는다.

초기 native 시도들의 실패와 argparse 준비 오류, 새 http 미도달 단언의 import-time class-definition arc 오류는 원보고 그대로 보존한다. http body는 미실행이지만 class-definition arc는 discovery에서 실행될 수 있으므로 현재 시험은 실제 _http 본문 미도달을 판정한다. 첫 합집합 fixture의 비연속 위치 인자를 argparse가 반려한 것은 fixture 배열만 교정했다. native 시험의 초기 일반 worker error1은 child 상세가 임시 폴더 정리로 남지 않았으므로 원인을 단정하지 않는다. 이후 동일 native 표본의 성공과 retained scratch를 확보했고 과거 실패를 합산하거나 수정하지 않는다. 마지막 지침에 측정 범위/미도달/불완전/시험판정/T3분리를 연결한다.

## 과거 변경의 한정 처분

b0d90537의 actual runner/Measurement diff에서 D5 자체입출력의 측정 정지와 D6 누락 worker의 명시적 비통과, gate와 함수 진입의 목적 분리를 확인했다. D5/D6 및 현재 1/2/3층 gate·선택 색인을 유지하고 T4의 필요 경로만 추가했다. bbe64043의 fixture-inclusive 비용·whole-module 비용 기록과 mutation.passed 공동소비, f56a2772의 시간 종료 제거는 그대로 유지한다. phase002의 실제 red2/최종58건과 정상 근거/지연기준 D9를 읽었으며 mutation 구현과 정상 기준은 수정하지 않았다. 별도 T4 비용을 기존 T3 비용에 넣지 않아 D11을 보존한다.

존재하는 전체-T3-2026-10-03.json은 역사 요약으로 읽었다. 그 report_path의 실제 원보고는 현재 없으며 요약의 gate 미통과·예전 판본 한계를 유지한다. PR01/B56의 phase002 원보고 부재 판단도 읽었다. 없는 원보고의 counts나 과거 성공을 이번 결과에 더하지 않는다. PR01 전체나 provenance 전체의 재검토 완료를 주장하지 않는다.

## 후속 책임

첫 정본 T4 전건은295선택/고유row,281passed·7error·5failed·2skipped,exit1이었고 측정은complete=true/60worker/101 of142branch였다. 이 판본을 최종 성공으로 표시하지 않는다. 여기에 드러난 두 T3 문제는 원인 확인 후 runner 안에서 교정했다. 새 worker 설정을 _read_json으로 측정 시작 전에 읽으면서 do_math.file_io의 import42행이 worker에서 빠졌으므로 표준 라이브러리로 설정을 읽어 원래 start-before-product-import 순서를 복원했다. 실제 serial T3 저장소의 prime/repeat에서는 자기 records.json이 import input에 들어가 다음 실행을 full로 만들었다. repo 안의 owned scratch에서 재현됐고 _t3_plan 읽기 전체를 D5 unmeasured로 감쌌다. branch gate나 저장소 무효화 조건을 낮추지 않았으며 기존 boundary.test_runner_incremental_t3/parallel_t3를 정확 소비자로 추가했다.

쓰기 범위 밖의 기존 문제가 첫 전건에 함께 드러났다. installed_request는 nonempty fingerprint/empty content를 만들어 현 record_errors에서6건이 반려됐다. 이전 실제 Lean identity를 이용해 측정 없이 해당 공개 producer만 호출한 fixture-reproduction.json에서도 같은 반려를 재현했다. RealJobObservation의 explicit raw {ok:true}/닫힌 빈 object schema, WriterLock child의 TypeError, standalone preview archive child의 ports NameError도 각각 원row로 남는다. bootstrap freeze rename의 WinError5는 환경/경쟁 원인을 단정하지 않는다. P10/P11 두 baseline 비교는 별도 pre-provenance-fix scripts tree 입력 부재로 skipped였다. 완전한 측정은 이 기능 실패나 부재 입력을 합격으로 바꾸지 않는다. 이 fixture/설치/입력 문제는 이번 writes 밖이므로 현 검증을 약화하거나 제품을 고쳐 우회하지 않고 다음 배정에 반환한다.

runner/Measurement 변경은 최종 G4/G5 판본을 바꾼다. t3_store.RUNNER에 해당 파일들이 있으므로 기존 증분 자료는 전체 재측정 대상이며 정확 기존 invalidation 시험을 실행한다. 이번 작은 T3는 gate가 미도달로 exit1인 부분 회귀이고 전체/fresh G5 성공이 아니다. 전체 일반/fresh T3/전체 변이, 나머지 문서·의미 질문, L01 외부 결정과 최종 review는 manager의 후속 책임이다. 기존 runtime/입력/녹화가 불변인 실호출의 승인된 성질만 재사용하며 새 유료 호출·예약 변경·연구 재개·graphify·Git 마감은 수행하지 않는다.

## 최종 대조

정본 canonical-related-04와 mirror-related-final은 각70선택/고유row/70passed/exit0이다. 기존 실제 T3 incremental2·parallel1을 포함한다. 교정 뒤 양쪽 최종 T4는 각295선택/고유row,283passed·6error·4failed·2skipped,complete=true/successful=false/exit1이며 소스 전후와 현재 판본은 동일하다. 두 최종 실행에서 T3 증분/병렬의 정확 ID는 passed다. 각60worker의 요청·run ID·875 Python 시작/종료판본·게시 SHA·실제 branch DB를 확인했고 측정 complete=true다. adapter.data를 coverage로 다시 분석해5개 파일의 SHA·행/분기·제외/요약과 합계가 실제 보고와 같음을 확인했다. 이 정보 보고를 기능 합격으로 바꾸지 않는다.

두 최종 실행의 steady fixture 오류6+3과 exact-baseline2skip 외에, scheduling_background_processes.test_real_git_descendants_are_observed_without_visible_windows도 양쪽에서 Git subprocess.DuplicateHandle WinError6 invalid handle로 failed였다. 첫 정본 전건에서는 이 ID가 passed였고 bootstrap-info freeze WinError5가 error였다. 최종 두 bootstrap-info ID는 양쪽에서 passed다. 각 원관측을 구분하고 OS 원인을 단정하지 않는다. 정확 row와 child trace는 verification.suites[].nonpassed 및 각 원report다. 소급 수정하거나 timeout/측정 누락/환경 조건을 포착·합격으로 만들지 않는다.

자기 snapshot 모집단은 source-start2667에서source-final2671로 늘었으며, 실제16변경(정본/미러 각6개·비용캐시 각2개)이 전부writes 안이다. 이 모집단은 skills/diff이며 시작 때 대조한014 manager inspected2750파일 모집단과 구분한다. runtime·입력139,corpus144경로·host8원자료와 Python/pythonw/PowerShell/Lean/Lake SHA는 보존됐다. 기존 index/pseudo 목록도 불변이다. 최종 생성 사전계획은 비용 캐시2개뿐이고 --check1336파일/skill-only가 통과했다. 실제 branch 합계는 정본102/142,미러101/142이며 각자 raw 재분석과 일치한다. 둘의 정보 도달률을 같게 만들거나 관문으로 만들지 않는다. 최초 mirror-plan의 false는 Windows write_text 개행을 LF로 비교한 보조 검사 오류였으며 native 개행으로 교정한 새 계획과 실제 생성에서 manifest bytes 불변을 확인했다. 원초기 결과는 보존한다. 이번 partial은A1~A3의 지정 성과와A4의 전건 기능/별도 baseline 입력 미충족을 구분한 제출이다.
