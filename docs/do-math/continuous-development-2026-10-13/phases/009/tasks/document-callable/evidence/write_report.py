"""Write the task submission from completed verification and actual command records."""
import json
import subprocess
from run_command import ROOT, EVIDENCE, write_json

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
PREFIX = 'run:phases/009/tasks/document-callable/evidence/'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def refs(*paths):
    return [PREFIX + p for p in paths]

verified = read(EVIDENCE / 'verification-final.json')
checks = []
details = {
    'prepare': '008 종료2640파일 및 검수 source-final 해시와 일치. 승인된 미커밋 제품30경로와 원실패4개씩을 대조했다. HEAD 변화는 관리 기록·공용 문서·기억뿐이며 제품 변화와 구별했다.',
    'notation': 'bare dotted 함수명 한 곳에 (...)만 추가했다. 기존 function_reference_issues로 실제 callable을 확인했고 unowned 목록은 빈 값이다. nonexistent/noncallable 반려도 유지되며 문서의 다른 바이트는 보존했다.',
    'canonical-final': '정본110선택/110고유row/110passed, complete=true, successful=true, 실제exit0.008과 선택ID가 같고 정확한4실패는 모두passed다. Python865파일 및 문서 판본은 실행 전후/최종과 일치한다.',
    'plan-build': '보조 계획 검산이 Windows Path.write_text의 CRLF 변환을 고려하지 않아 manifest 원바이트 단언에서exit1. 제품 변화0. 실제 원출력은 보존했고 생성 전 보조 검산을 교정했다. 제품 드리프트나 시험 실패로 세지 않는다.',
    'plan-build-02': '생성기의 newline=None 쓰기를 os.linesep으로 정확히 반영해 재검산했다. 생성/삭제0, manifest불변, 허용된 미러 문서·비용캐시2경로만 변경 예정이다.',
    'mirror-build': '공식 생성기exit0. 실제 변경은 계획의 미러 문서·비용캐시2경로와 정확히 같다. 쓰기 범위 밖 드리프트는 없다.',
    'mirror-final': '미러89선택/89고유row/89passed, complete=true, successful=true, 실제exit0.008과 선택ID가 같고 정확한4실패는 모두passed다. Python865파일 및 문서 판본은 실행 전후/최종과 일치한다. scoped packaging 정본21개 책임은 기존 배분대로 정본에서 검사했다.',
    'plan-cache': '미러 시험 후 공식 재생성 계획은 미러 비용캐시1개뿐이다. 문서·manifest·그 외 파일 변화는 없다.',
    'cache-sync': '공식 생성기로 미러 비용캐시1개만 정본과 재동기화했다. 계획과 실제가 같고 양쪽 캐시 바이트가 일치한다.',
    'mirror-check': '공식 --check exit0,1305파일 드리프트 없음. 검사 전후 소스는 최종판과 같다.',
    'skill-only': 'probe_cli --skill-only exit0,verified. 검사 전후 소스는 최종판과 같다.',
    'final-verification': '선택/고유row/counts/실제exit·소스 전후·정확4실패 대응·최종4변경과writes를 대조했다. runtime124·smoke입력3·corpus102경로·그 외 시험 소스는불변.008 입력/역사보고도 변경하지 않았다.'
}
for label, detail in details.items():
    command = read(EVIDENCE / label / 'command.json')
    assert command['state'] == 'exited'
    checks.append({'command': subprocess.list2cmdline(command['argv']), 'cwd': 'repo:.',
                   'result': 'pass' if command['exit_code'] == 0 else 'fail',
                   'exit_code': command['exit_code'],
                   'evidence': refs(label + '/command.json', label + '/stdout.txt', label + '/stderr.txt'),
                   'detail': detail})
report = {
    'status': 'complete',
    'narrative': 'CLI-실행-계약의 공급자 절에 있는 provider_final.output_contract를 기존 함수 검사 표기인 provider_final.output_contract(...)로 교정했다. 함수명을 유지하며 (...) 다섯 바이트만 추가했고 다른 문장·개행·바이트는 보존했다. 기존 callable·필드 검사와 nonexistent/noncallable 반려를 확인했으며 helper/schema/unknown/defer/runtime/시험 소스를 바꾸지 않았다. 시작 HEAD는 ' + verified['head'] + '이고 2640소스는 008 종료/manager 검수와 전건 일치한다. HEAD 관리 마감과 승인된 제품 30경로의 미커밋 변경을 구별하고 기존 dirty를 보존했다.\n\n008의 수리 전 원실패/HEAD helper 재현을 재사용했다. 새 정본 110개와 미러 89개를 각각 한 번 jobs1로 공식 실행해 전건 passed·실제 exit0을 확인했다. 선택 ID·고유 row가 008과 같고 네 실패 ID는 양쪽 모두 passed로 연결된다. 운영/복구 실제 객체·파일·정상/오류/null/live 부재·소유자 교란, 일반 재개·manifest/profile_selection·bootstrap-info 기존 단언은 소스 불변인 채 이 선택에서 통과했다.\n\n공식 미러 계획과 실제 변경을 대조했다. 첫 보조 검산의 exit1은 제가 manifest의 Windows 개행 변환을 빠뜨린 오류이며 생성 전 교정했다. 실패 stdout/stderr/exit를 보존했고 제품 변화는 0이다. 이후 문서·캐시 2경로만 생성했고 미러 검사 뒤 캐시 1개만 재동기화했다. --check 1305파일/skill-only verified는 exit0이다. 최종 4변경은 허용 문서 2개·캐시 2개로만 구성되고 양쪽 Python 865파일·runtime 124·smoke 입력 3·corpus 102경로와 그 외 시험은 불변이다. corpus 원바이트와 규칙/속성이 008 검수와 같으므로 명시 SHA/Git clean 및 공급자 실호출의 기존 한정 재사용 근거를 연결한다. 새 모델 호출이나 Git 마감은 수행하지 않았다.\n\n이번 A1~A3는 pass다. 008의 partial 원보고는 보존하며 008 P01/N03-003 지정 성과와 이번 함수 표기·관련 회귀만 닫는다. N03 전체·P02~P11·다른 G7 실연쇄·최종 일반/T3/변이/review는 여전히 후속 책임이고 프로젝트 전체 완료로 확대하지 않는다.',
    'acceptance': [
        {'id': 'A1', 'result': 'pass',
         'detail': '008 종료/검수와 시작 2640파일·미커밋 30경로를 대조했다. 공급자 함수명 한 곳에 (...)만 추가하고 원 schema/transport·부재/null·worker/native·Claude/control_binding 설명을 보존했다. 실제 callable과 함수 검사 연결, unowned 오분류 해소, nonexistent/noncallable 반례를 확인했다.',
         'evidence': refs('start-state.json', 'source-start.json', 'input-hashes.json', 'baseline-reference.json', 'cli-before.txt', 'notation.diff', 'callable-probe.json', 'notation/command.json')},
        {'id': 'A2', 'result': 'pass',
         'detail': '정본 110/미러 89의 선택 ID와 008 선택이 같다. 각 고유 row 전건 passed·complete/successful true·실제 exit0이며 skip/error/미실행 0이다. 네 원실패의 정확 ID 모두 양쪽 passed다. 실행 전후와 최종 Python 865파일·문서 해시가 같고 기존 시험 단언은 불변이다.',
         'evidence': refs('canonical-final/results/report.json', 'canonical-final/command.json', 'mirror-final/results/report.json', 'mirror-final/command.json', 'verification-final.json')},
        {'id': 'A3', 'result': 'pass',
         'detail': '공식 생성 계획 2경로와 실제 변경이 같고 미러 시험 후 캐시 1개만 재동기화했다. --check 1305파일/skill-only는 exit0이다. 최종 4변경은 writes와 같으며 runtime 124·smoke 3·corpus 102·그 외 시험은 불변이다. 각 corpus 18항목/51파일/223685바이트/50명시 SHA의 008 원바이트 검수와 Git clean 근거를 재사용한다. 전체 관문과 다른 G7의 책임은 남긴다.',
         'evidence': refs('mirror-plan.json', 'mirror-build/command.json', 'cache-plan.json', 'cache-sync/command.json', 'mirror-check/stdout.txt', 'skill-only/stdout.txt', 'source-final.json', 'verification-final.json') + ['run:phases/008/manager-evidence/git-clean-observation.json']}
    ],
    'changes': [{'path': p, 'detail': ('공급자 output_contract 함수명을 기존 callable 검사 표기 provider_final.output_contract(...)로 교정한 정본 문서.' if p.startswith('.claude') else '공식 생성기로 동기화한 대응 문서 사본.')
                if p.endswith('.md') else '공식 run_tests 실행이 갱신한 비용 캐시.' + (' 미러 실행 후 정본 바이트로 공식 재동기화했다.' if p.startswith('.agents') else '')}
                for p in verified['changes']],
    'seams': [],
    'findings': [
        {'id': 'F1', 'kind': 'fact',
         'detail': '008 F1/A5의 기존 함수 표기 공백이 해소됐다. 문서 한 곳의 표기만 바꾸고 기존 검사를 유지한 채 정본 110/미러 89 모두 passed다. 이전 네 실패 ID의 passed 대응은 verification-final에 있다. 008의 partial 보고와 수리 전 실패는 변경하지 않았다.',
         'evidence': refs('verification-final.json', 'canonical-final/results/report.json', 'mirror-final/results/report.json', 'notation.diff'),
         'affects': ['run:context.md#C10', 'run:context.md#G1', 'run:context.md#G3', 'run:plan.md', 'run:phases/008/tasks/document-recovery/objective.md#A5'],
         'next_action': 'manager가 실제 원보고·선택/row/exit·변경 범위를 검수하고 008 F1/A5 남김의 해소를 공용 상태에 반영한다. 008~009 문서·시험 변경 단위의 Git 마감은 manager가 맡는다.'},
        {'id': 'F2', 'kind': 'fact',
         'detail': 'runtime 124·smoke 입력 3·양쪽 corpus 102와 그 외 시험 소스는 008 검수 바이트 그대로다. 공급자 호출 0이며 기존 실호출의 한정 재사용 조건과 corpus 명시 SHA/Git clean 판정은 유지된다. 최종 변경은 문서 2/비용 캐시 2뿐이다. 문서 판본이 바뀌었으므로 G4~G6/G8 최종 관문·다른 G7 실연쇄와 나머지 문서 범위는 이번 회귀로 대체하지 않는다.',
         'evidence': refs('source-start.json', 'source-final.json', 'verification-final.json', 'mirror-check/stdout.txt', 'skill-only/stdout.txt') + ['run:phases/008/manager-evidence/verification.json', 'run:phases/008/manager-evidence/git-clean-observation.json'],
         'affects': ['run:context.md#C12', 'run:context.md#G4', 'run:context.md#G5', 'run:context.md#G6', 'run:context.md#G7', 'run:context.md#G8', 'run:plan.md'],
         'next_action': 'manager는 기존 한정 실호출 근거의 재사용을 유지하고 최종 판본 관문·나머지 문서·G7 연쇄를 별도 배정한다. N03 전체나 프로젝트 전체 완료로 확대하지 않는다.'}
    ],
    'checks': checks
}
write_json(EVIDENCE.parent / 'report.json', report)
print('report.json written: complete, A1/A2/A3 pass; canonical110 and mirror89 passed.')
