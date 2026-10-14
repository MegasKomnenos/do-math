# phase 018 manager 검수

report 전문과 A1~A4를 읽고 공용 문서 편집 전에 check.py report를 통과했다. source-start2675개는017 manager 검수와 같고, 현재2675개는 task 종료와 전건 같다. 허용8변경은 fixture2·지침2·비용캐시4이며 report/writes에 대응한다. runtime/공급자·Lean·예약 입력139, corpus144/150SHA, host8원자료·도구, baseline910파일과 Git blob, index/pseudo/T3-store를 원자료와 대조했다.

현재 JobsContract._cleanup_job는 명시 terminate 뒤 root wait, 기존 cli_execution.termination_confirmed의 root signal·active0·빈PID를 확인하고 finally에서 close한다. 원문11shared test method와 runtime API는 유지했다. 실제 before2의 close 직후 wait258, 초기화된 live cwd의 WinError32와 종료 뒤 삭제 성공, after의 세 상태·각 signal0/빈Job/directory_removed를 읽었다. 두 오류 주입 사례는 본문 ValueError와 cleanup ObservationFault를 따로 기록하고 real/fake 핸들을 해제한다. 역사 race는 미재현이고017 오류 순간 상태는 없으며 bootstrap WinError5 원인도 미확인이다. 이 한계는 유지하고 현재 동기화 공백과 새 회귀 통과로 F1을 종결한다.

공식 exact1·정본관련27·미러관련27과 최종 정본/미러 T4 각각295개 선택·고유row·passed·실제exit0를 재대조했다. 양쪽 전체 --list와 실제 결과가 같고 Python875개가 현재와 일치한다. 각60worker의 요청/run_id/소스·공유 publication 검사·artifact SHA/원branch DB·부모 합집합 포함과 adapter5개 raw 재분석을 확인했다. 양쪽102/142는 정보이며 기능합격과 별도로 측정complete다.015의12미통과와017의 정확cleanup 오류는 새 전체에서 passed다. 기존 source-identical 환경7ID도 모두 선택에 포함돼 passed다. manager는 제품 시험을 다시 실행하지 않았다.

첫 manager 검산 exit1은 canonical exact/related 실행 뒤 아직 생성 전인 미러2파일까지 최종 동일성을 요구한 관리 스크립트 오류다. 원script는 verify-v1.py에 보존했다. 실제 검사한 tree의 동등성을 관련 실행별로 확인하고 최종 두 전체에는 양쪽 tree 불변을 요구하도록 교정해 exit0을 얻었다. 제품 판정이나 시험 근거를 고치지 않았다. task2463파일과 이전017 evidence5917파일은 검산 전후 불변이다.

018의 parent TEMP는 외부 전용 경로, git probe는128/빈stdout이며 resource output은c4/m4다.229자 cwd는 현 고정폭 구성으로 계산한 값이고017의241자 성공은 실제 관측이다. 이를 같은 종류의 관측으로 바꾸지 않는다. 두 실제 전체 실행의 설치probe 정상/반려 통과를 함께 사용한다. 지침2파일 추가는 허용 범위이며 기존22제품 중 나머지20파일은 불변이다. 원지침의 역편집은 시작SHA와 일치하나 사전 복사라고 주장하지 않는다.

F2의 지정 T4 남김과 F3의 보존 사실을 종결한다.015~016제품22경로와018fixture2경로, 합24경로는 관련 검수와 최종 T4 연결이 충분하므로 이번 관리 커밋에 포함한다. 비용캐시4·무관 dirty는 제외한다. 원task 자료와24제품 바이트는 raw-evidence.zip에 보존하고 추적/로컬 구분과 SHA는 preservation.json에 둔다. 새 커밋용 관리·기억만 추가하며 제품 바이트는 그대로다.

다음019는P02 네owner의 문서 결속을 실제 생산·저장·역할 입력으로 연결하는 단일 work다. 공유doc_code와 미러/캐시를 한 task가 소유하며, 독립된 무관 조사를 추가하지 않는다. L01 운전host·단위의 외부 결정은 답변 전 기존byte 요구/미충족으로 남긴다. P03/REVIEW/TRUST/다른 의미·문서와 G4~G6/G8 전체 관문도 유지한다. 직전 phase는 work이고 전체 기준 근거가 없으므로 종료하지 않는다.
