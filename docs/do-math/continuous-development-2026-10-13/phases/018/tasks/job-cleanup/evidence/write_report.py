import subprocess
from pathlib import Path
from task_driver import E, REPO, RUN, read, write

prefix = 'run:phases/018/tasks/job-cleanup/evidence/'
def refs(*names): return [prefix+name for name in names]
verification = read(E/'verification.json')
preserved = read(E/'preservation.json')
changes = preserved['changes']
checks = []
labels = ['observe-before','observe-before2','observe-after','cleanup-faults',
          'canonical-exact-job','canonical-related','mirror-related','verify-mirror-plan','mirror-build',
          'canonical-t4-list','mirror-t4-list','canonical-t4-short','mirror-t4-short',
          'verify-final-mirror-plan','final-mirror-build','mirror-check','skill','final-verify']
for label in labels:
    d = read(E/(label+'.command.json'))
    assert 'exit_code' in d
    checks.append({'command':subprocess.list2cmdline(d['argv']), 'cwd':'repo:.',
        'result':'fail' if d['exit_code'] != 0 else 'pass','exit_code':d['exit_code'],
        'evidence':refs(label+'.command.json',label+'.stdout',label+'.stderr'),
        'detail':('수리 전 suspended cwd 삭제의 보조 관측 오류. 최초 원오류와 v1 소스를 보존하고 before2의 실제 초기화/live/종료 대조로 교정했다. 제품 시험 실패로 합산하지 않는다.'
                  if label == 'observe-before' else
                  '명령·시각·PID·실제 종료 코드와 원 stdout/stderr를 보존했다. 종료 코드 0을 관측했으며 제품 시험의 선택/고유row 및 소스·측정 검산은 verification.json에 별도로 결속한다.')})
details = []
for p in changes:
    name = Path(p).name
    if name in ('.timings.json','.timings-t3.json'):
        detail = '공식 실행/공식 미러 생성의 비용 캐시 변화. 통과 근거나 제품 Git 마감 대상이 아니다.'
    elif name == 'jobs.py':
        detail = '공유 JobsContract cleanup이 시험 소유 Job을 terminate→root wait→termination_confirmed 조건 관측한 뒤 finally에서 close하도록 수정. 대응 미러는 공식 생성물이다.'
    else:
        detail = '시험 운전 지침에 parent TEMP의 저장소 밖 격리와 resource output scratch의 별도 경로 길이 조건, Job 종료 확인/핸들 해제/디렉터리 정리 의미를 반영. 대응 미러는 공식 생성물이다.'
    details.append({'path':p,'detail':detail})

durations = {label:round(data['seconds'],3) for label,data in verification['suites'].items()}
report = {
    'status':'complete',
    'narrative':f'phase018 job-cleanup의 A1~A4를 완료했다. 시작 skills/diff2675파일은017 manager 검수본과 전건 일치했다.017 c4 정확 오류의 원trace와 LIFO cleanup·현 공개 API를 대조했고 새 실제 PID/FILETIME/IsProcessInJob 관측에서 close 직후 root 미신호258인 suspended/resumed 표본과 실제 live cwd 삭제 WinError32/종료후 삭제 성공을 확인했다. 역사 race 자체는 새 원fixture 작은 실행에서 재현되지 않았고 과거 오류 순간 상태는 없으므로 원인을 확정하거나 빈도를 추정하지 않는다. 첫 보조 관측 exit1은 suspended cwd 삭제의 경로 부재 가정 오류이며 원자료/v1을 보존하고 before2로 교정했다.\n\n공통 fixture의 종료/빈Job 확인을 기존 termination_confirmed 정본으로 보강하고 finally에서 핸들을 해제한다. runtime close·ports·fakes·runner·측정·요구는 바꾸지 않았다. suspended/resumed/자연 종료된 실제 Job은 정리전 barrier와 디렉터리 삭제 성공이 대응했고, 실제/대역의 인위적 fixture 관측 실패에서도 본문 오류와 cleanup 오류가 함께 기록되고 핸들/디렉터리가 정리됐다. 기존 공유11개 성질과 livefake5개는 그대로이며 정본/미러 관련각27passed, 정확ID1passed였다. PR02의 실제 116cff28/0b05e8ab/23cc4df3 diff·현 소비와010/016 근거에 한정하여 kill-on-close/종료 관측 API를 유지하고 fixture 소비만 교정했다.\n\n같은 최종 소스 판본의 공식 --list와 정본/미러 전체T4가 각각295선택/295고유row/295passed·exit0으로 완결됐다. 각60worker의 요청/run_id/Python875소스·게시artifact SHA/branchDB와 부모합집합·현adapter5개 소스분모 및 보고 재분석을 대조했다. 측정complete와 기능전건passed를 별도로 확인했으며 정보 도달률은 임계관문이 아니다.015의12미통과 및017 환경7ID와 정확Job오류는 양쪽 새전체passed에 대응한다. 실제 실행초는 {durations}이다. 소프트 예산을 넘은 실제 시간을 숨기거나 시간만으로 중단하지 않았고, 이번 work는 fixture 정확성 수리이며 무관한 속도 개선을 추가하지 않았다.\n\n각 parent TEMP는 저장소 밖 짧은 dm018-*이며 Git비저장소 exit128을 확인했다. resource output도 evidence/c4·m4로 줄였고 불변 installed-probe의 고정폭 경로구성229자를 사전대조했다.229자는 계산된 현재구성이며017 실제241자성공과 대비한 이 환경조건이지 보편Windows상한이 아니다. 관련지침과 공식미러를 맞추고 사전예상변경/writes·최종 --check/skill-only를 확인했다. runtime139입력·corpus144/150명시SHA·host8/도구·baseline910·index/pseudo/T3-store 및015~016제품22경로 중 수리 범위 밖20경로의 바이트는 불변이다. 허용된 시험 지침2경로에는 필요한 단락만 추가했고 원래 바이트는 시작 SHA와 대조하여 보존했다.017원evidence5917개(\u005f\u005fpycache\u005f\u005f 제외)의전후hash도 같다. TestCase/WORKER/SNAPSHOT·계측이불변인017정본companion만 한정재사용하며 미러raw를보존했다고주장하지않는다. 기존실호출입력/제품/도구가불변이므로 승인성질만유지하고 새유료/예약/학술호출은없다.\n\n전체일반G4/freshT3G5/전수변이G6/최종reviewG8·나머지의미/문서/L01·과거bootstrapWinError5미확인·015~016제품22경로의Git마감은후속manager책임이다. 이전원보고/실패를고치지않았고 stage/commit/reset/checkout/push·graphify갱신·기존연구운전/삭제는수행하지않았다.',
    'acceptance':[
        {'id':'A1','result':'pass','detail':'시작2675경로 전건동등과 정확 역사error/앞선passed를 구별했다. LIFO/MARK cwd·real/fake/API·도입diff를 대조하고 새실제 root/Job/cwd 대조로 동기화공백을 확인했다. 역사race 미재현/당시상태미관측 한계는 유지한다.',
         'evidence':refs('environment.json','source-start.json','review.md','job-observation-before2.json','history-job-origin.stdout','history-job-port.stdout','history-job-migration.stdout')},
        {'id':'A2','result':'pass','detail':'공통 fixture만 기존API/termination_confirmed로 수리했다. 핸들은finally에서해제하며 실제/대역 오류보존도확인했다. 실제 suspended/resumed/이미종료 표본의 정리전 barrier와 directory_removed가대응한다. 정확ID1·양쪽관련각27선택/고유passed·exit0이며 기존11shared/5livefake성질은불변이다.',
         'evidence':refs('changes.diff','job-observation-after.json','cleanup-faults.json','canonical-exact-job-verification.json','canonical-related-verification.json','mirror-related-verification.json')},
        {'id':'A3','result':'pass','detail':'최종양쪽 전체T4 각각295선택/295고유row/295passed·exit0과list전건대응,Python875불변·각60worker게시/branchDB/부모합집합·adapter5개소스분모/정보보고를검산했다.910baseline 공급·두exact실행·01512미통과/0177환경ID/cleanup1의새passed대응을확인했다. 불변017정본raw한정재사용이며과거부분성공을합산하지않았다.',
         'evidence':refs('verification.json','canonical-t4-short-verification.json','mirror-t4-short-verification.json','canonical-t4-list.stdout','mirror-t4-list.stdout','start-baseline.json','final-baseline.json','raw-reuse-basis.json')},
        {'id':'A4','result':'pass','detail':'parent외부짧은전용TEMP/Git비저장소·별도짧은resourceoutput및경로구성229<=017실제성공241을사전대조했다.지침/공식미러예상writes/생성/check/skill-only를확인했고139입력·144corpus/150SHA·8host/도구·910baseline·index/pseudo/T3-store·수리밖기존제품20경로및과거raw를보존했다.기존22중허용지침2경로는명시추가와원바이트보존을구별했다.전체G및Git마감/역사미관측한계는후속책임으로유지한다.',
         'evidence':refs('path-preflight.json','preservation.json','corpus-raw-clean.json','final-baseline.json','initial-mirror-plan.json','mirror-plan.json','mirror-check.command.json','mirror-check.stdout','skill.command.json','skill.stdout','review.md')}
    ],
    'changes':details,'seams':[],
    'findings':[
        {'id':'F1','kind':'fact','detail':'실제close직후heldrootwait258과livecwd삭제WinError32/종료확인뒤성공을관측했다. fixture의종료동기화공백은현API로교정했지만017오류순간상태는없고같은역사race자체는작은원fixture관측에서미재현이다.과거bootstrapWinError5의원인도미확인이다.',
         'evidence':refs('job-observation-before2.json','job-observation-after.json','review.md'),
         'affects':['run:context.md#C11','run:plan.md','repo:.claude/skills/do-math/scripts/tests/support/port_contracts/jobs.py'],
         'next_action':'현재fixture교정과새전체통과를검수해cleanup남김을처분하되역사인과/빈도및bootstrap미확인한계를유지한다.'},
        {'id':'F2','kind':'fact','detail':'최종양쪽전체T4는각295passed/exit0이고각60workeradapter측정complete다.현정보분모5adapter및소스/게시/분기합집합이대응한다.01512미통과·0177환경ID·cleanup오류1은새전체passed로연결됐다.이는G4~G6/G8·의미/문서/L01전체종료근거는아니다.',
         'evidence':refs('verification.json','canonical-t4-short-verification.json','mirror-t4-short-verification.json'),
         'affects':['run:context.md#C11','run:plan.md'],
         'next_action':'T4지정남김의새전건근거를검수하고남은전체관문/의미/문서/L01을기존기준대로배정한다.'},
        {'id':'F3','kind':'fact','detail':'runtime139입력·corpus144/150SHA·8host/도구·910baseline·기존22중수리밖20제품·index/pseudo/T3-store와017정본companion정의/원자료를보존했다.허용지침2경로는필요단락을추가하고원바이트를시작SHA로검증해보존했다.공유시험cleanup/운전지침변경은기존실호출승인입력/경로를바꾸지않으며공식미러/check/skill-only가맞는다.22제품Git마감은아직수행하지않았다.',
         'evidence':refs('preservation.json','raw-reuse-basis.json','verification.json','final-baseline.json','mirror-check.stdout'),
         'affects':['run:context.md#C12','run:plan.md'],
         'next_action':'기존실호출의승인성질만한정재사용하고015~016제품22경로및018fixture/지침의검수후Git마감을manager가판단한다.'}
    ],'checks':checks
}
report['narrative'] = f'''phase 018 job-cleanup의 A1~A4를 완료했다. 시작 skills/diff 2675개 파일은 phase 017 manager 검수본과 전건 일치했다. 정확 역사 오류는 다시 resume 반려 이후 TemporaryDirectory 삭제의 WinError32/5였다. LIFO상 close가 먼저 호출되지만 close는 종료 barrier가 아니다. 새 실제 PID/FILETIME·IsProcessInJob·root/Job/cwd 관측에서 close 직후 held root의 wait(0)=258과, 초기화된 live Job의 cwd 삭제 WinError32/종료 확인 후 삭제 성공을 확인했다. 역사 race 자체는 작은 원fixture 실행에서 재현되지 않았고 당시 오류 순간 상태도 없으므로 인과나 빈도를 확정하지 않는다. 첫 observe-before exit1은 suspended cwd가 이미 삭제된 경우를 잘못 처리한 보조 코드 오류였다. 원스크립트 v1/명령/출력을 보존하고 ready marker를 사용하는 before2 대조로 교정했다.

공통 fixture는 시험 소유 Job을 명시 terminate하고 root wait와 기존 cli_execution.termination_confirmed를 확인한 뒤 finally에서 핸들을 닫는다. runtime close·ports·fakes·runner·측정·요구는 바꾸지 않았다. suspended/resumed/자연 종료한 실제 Job의 정리 전 barrier와 디렉터리 삭제 성공이 대응한다. real/fake의 명시 fixture 관측 오류에서도 원본문 오류와 cleanup 오류를 별도로 기록하고 핸들/디렉터리를 정리했다. 기존 shared 11개 성질과 live fake 5개는 유지했으며 정확 ID 1건, 양쪽 관련 각27건이 공식 runner에서 모두 passed·exit0이다. PR02의 Job slice는 116cff28/0b05e8ab/23cc4df3 실제 diff·현 소비·010/016 근거에만 대조했다. 기존 kill-on-close와 종료 관측을 유지하고 fixture 소비만 교정했으며 전체 PR이나 없는 원보고 counts를 승인하지 않는다.

최종 동일 제품·시험 판본의 공식 전체 T4는 정본/미러 각각295선택·295고유row·295passed·exit0이다. --list 대응, 각875개 Python 소스 불변, 각60개 worker의 요청/run_id/소스·게시artifact SHA/branch DB·부모 합집합과 현adapter5개 분모/정보 보고를 검산했다. 측정 complete와 기능 합격을 별도로 확인했다. 도달은 양쪽102/142이며 임계 관문이 아니다. 015의12미통과와017의환경7ID/cleanup오류1은 새 전체 passed에 대응한다. 실제 실행초는 {durations}이다. 소프트 예산 초과를 숨기거나 시간만으로 종료하지 않았고, 무관한 속도 개선이나 전체 재시도를 추가하지 않았다.

parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 dm018-* 실행 전용 경로이며 git rev-parse exit128/빈stdout을 보존했다. resource output도 evidence/c4·m4로 줄였다. 불변 installed-probe의 고정폭 구성으로 계산한 cwd229자는017 실제 성공241자 이하이며, 계산과 이전 실측을 구별한다. 보편 Windows 상한으로 쓰지 않는다. 이 경로 교훈과 Job 정리 의미를 시험 지침에 추가하고 공식 미러 예상변경/writes·생성·최종 --check1336/skill-only verified를 확인했다. 실제8변경은 fixture2·지침2·비용캐시4다. 캐시는 성공 근거나 제품 Git 마감 대상이 아니다.

runtime 포함139입력·corpus144경로/150명시SHA·host8원자료/도구·baseline910파일·index/pseudo/T3-store는 불변이다. 기존015~016제품22경로 중 수리 범위 밖20경로의 바이트를 보존했다. 명시 수정 범위와 겹치는 지침2경로에는 필요한 단락만 추가했고 원본문 바이트는 시작SHA와 정확히 일치하는 역편집 자료로 보존했다. 사전 복사 주장과 이 역변환 검증을 구별하며 변경을 별도 기록한다.017원evidence5917파일(__pycache__ 제외)의 전후 해시도 같다. TestCase/WORKER/SNAPSHOT·계측이 불변인017정본 companion만 한정 재사용하며 미러 companion raw를 확보했다고 주장하지 않는다. 공유fixture/시험지침은 기존 실호출의 입력·제품·도구를 바꾸지 않으므로 승인 성질만 유지한다. 새 유료/예약/학술 호출은 없다.

전체일반G4/freshT3G5/전수변이G6/최종reviewG8, 남은 의미·문서·L01 외부 결정, 과거bootstrap WinError5 원인 미확인, 기존22경로 및 이번fixture/지침의 Git 마감은 후속 manager 책임이다. 이전 report/raw를 고치거나 stage/commit/reset/checkout/push·graphify갱신·기존 연구 운전/삭제를 수행하지 않았다.'''

acceptance_details = [
    '시작2675경로 전건 동등과 정확 역사 error/앞선 passed를 구별했다. LIFO·MARK cwd·real/fake·공개 API·도입 diff를 대조하고 실제 root/Job/cwd 관측으로 동기화 공백을 확인했다. 역사 race 미재현과 당시 상태 미관측 한계를 유지한다.',
    '공통 fixture만 기존 API/termination_confirmed로 수리했다. finally의 핸들 해제와 실제/대역 오류 보존을 확인했다. suspended/resumed/이미 종료한 실제 표본의 정리 전 barrier와 directory_removed가 대응한다. 정확ID1건과 양쪽 관련 각27선택/고유passed·exit0이며 기존 shared11/livefake5 성질은 유지했다.',
    '최종 양쪽 전체 T4 각각295선택/295고유row/295passed·exit0과 --list 전건 대응, Python875 불변·각60worker 게시/branch DB/부모합집합·adapter5개 소스 분모/정보 보고를 검산했다. baseline910 공급과 두 exact 실행, 이전015의12미통과 및017의환경7ID/cleanup오류1이 새 passed에 대응한다. 불변017정본 raw만 한정 재사용하며 과거 부분 성공을 합산하지 않았다.',
    '외부 짧은 전용 parent TEMP/Git 비저장소와 별도 짧은 resource output을 확인하고 현재 cwd 구성229<=017실측성공241을 사전 대조했다. 지침/공식 미러 예상 writes·생성/check/skill-only를 확인했다.139입력·144corpus/150SHA·8host/도구·910baseline·index/pseudo/T3-store·기존제품 중 수리밖20경로와 과거 raw를 보존했다. 기존22 중 허용 지침2경로의 명시 추가/원바이트 보존을 구별하며 전체G/Git마감/역사한계를 유지한다.'
]
for row,detail in zip(report['acceptance'],acceptance_details): row['detail'] = detail
finding_details = [
    '실제 close 직후 held root의 wait(0)=258과 live cwd 삭제 WinError32/종료 확인 뒤 성공을 관측했다. fixture의 종료 동기화 공백은 현 API로 교정했지만017 오류 순간 상태는 없고 같은 역사 race 자체는 작은 원fixture 관측에서 미재현이다. 과거 bootstrap WinError5 원인도 미확인이다.',
    '최종 양쪽 전체 T4는 각각295passed/exit0이며 각60worker adapter 측정도 complete다. 현5adapter의 소스 분모·게시·분기합집합이 대응한다.015의12미통과 및017의환경7ID/cleanup오류1은 새 전체 passed로 연결됐다. 이것은 G4~G6/G8·남은 의미/문서/L01의 전체 종료 근거는 아니다.',
    'runtime139입력·corpus144/150SHA·host8/도구·baseline910·기존22 중 수리밖20제품·index/pseudo/T3-store와017정본 companion 정의/원자료를 보존했다. 허용 지침2경로는 필요한 단락을 추가하고 시작SHA로 검증한 원바이트를 보존했다. 기존 실호출의 승인 입력/경로는 불변이며 공식 미러/check/skill-only가 맞는다. 제품 Git 마감은 수행하지 않았다.'
]
for row,detail in zip(report['findings'],finding_details): row['detail'] = detail
write(E.parent/'report.json',report)
print('report written',E.parent/'report.json')
