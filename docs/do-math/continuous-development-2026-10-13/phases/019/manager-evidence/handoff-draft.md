# 파일: services/continuous-development/protocol.md

# Phase 개발 세션 계약

이 도구는 하나의 개발 목표를 여러 작업으로 나누고, 각 작업의 결과에 따라 다음 작업을 정하며 개발을 이어 간다. 매번 새로 시작하는 AI가 이 문서와 지정된 파일을 읽고 수행할 수 있도록 작업의 단위, 전달할 정보, 결과 형식을 정한다.

## 작업의 단위와 진행 방식

**프로젝트**는 사용자가 요구한 결과를 만들기 위해 다루는 코드·설정·테스트·문서의 전체다. 프로젝트의 목표와 완료 기준은 공용 context에 적는다. **개발 실행**은 그 목표를 위해 이 도구로 이어 가는 작업 전체이며, 하나의 실행 기록 디렉터리에 배정과 결과를 보존한다.

**task**는 구체적인 목표와 완료 조건을 배정받은 작업 단위다. 구현, 조사, 검증, 검토가 task가 될 수 있다. task에는 바꿀 수 있는 파일 범위와 외부 구성 요소에 대한 책임을 정한다. 예를 들어 줄 집계 프로그램에서 문자열을 집계하는 함수 구현과 명령행 입력·출력 구현은 서로 다른 task다.

**세션(session)**은 `codex exec`를 한 번 호출해 시작하고 그 프로세스가 종료될 때까지의 수행이다. task 하나를 세션 하나가 맡는다. 이전 세션의 대화가 자동 전달된다고 전제하지 않으며, 필요한 맥락은 파일로 읽는다. 후속 phase의 작업은 새 세션에서 시작한다.

**phase**는 같은 시점에 배정해 병렬 수행하는 하나 이상의 task 묶음이다. 그 안의 task들은 같은 공용 문서를 기준으로 작업하며, 전부 종료돼야 다음 판단으로 넘어간다. **독립적으로 수행한다**는 것은 서로 다른 파일을 쓰는 것뿐 아니라, 같은 phase의 다른 task가 내놓을 결과를 기다리거나 그 task가 수정 중인 상태에 의존하지 않고 자기 작업을 수행·검증할 수 있다는 뜻이다. 이미 정한 경계의 약속에 의존하는 것은 가능하다.

**manager**는 phase의 모든 task가 종료된 뒤 새로 호출되는 세션의 역할이다. 프로젝트 전체의 목표와 계획, 모든 task의 결과를 읽고 현재 이해와 계획을 갱신해 다음 phase를 배정한다. 또는 최종 검토 결과로 개발 완료를 선언한다. manager는 직전 phase의 task 목록에 포함되지 않으며, task들과 동시에 공용 문서를 수정하지 않는다.

**review**는 완성됐다고 판단한 결과를 요구·경계 계약·실제 동작과 대조해, 충족 여부와 남은 문제를 근거와 함께 보고하는 작업이다. review phase에는 검토 task만 두고 제품을 수정하지 않는다. **work phase**는 조사·설계·구현·수정·연결 검증 등 최종 검토 이외의 작업을 담는다. review에서 수정 필요성이 드러나면 work와 review를 다시 배정할 수 있다.

**실행기(run.py)**는 task 세션들을 시작해 모두 기다린 다음 manager 세션을 시작해 기다린다. manager가 지정한 다음 phase가 있으면 반복하고, 명시적으로 종료하면 끝낸다. **검사기(check.py)**는 세션이 작성한 파일의 형식과 참조 관계를 정해진 규칙으로 확인하는 도구다. 같은 파일과 환경 상태에는 같은 판정을 내리며, AI를 호출해 내용의 타당성을 채점하지 않는다. 각 세션이 자기 제출 전에 검사기를 실행한다.

```text
phase 001: task A 세션 ─┐
           task B 세션 ─┴─ 모두 종료 → manager 세션
                                      │
                         다음 phase 배정 또는 개발 완료
```

세션 시작 메시지인 **부트스트랩**에는 역할과 작업 위치가 주어진다. `repo`는 프로젝트 루트, `run`은 개발 실행의 기록 루트, `engine`은 이 문서와 run.py·check.py가 있는 디렉터리다. 부트스트랩의 Python 경로는 검사 명령에 사용할 실행 파일이다. 이 문서의 `<repo>` 같은 표기는 실제 경로로 바꾸고 경로에 공백이 있어도 인수 하나로 전달되도록 인용한다.

## 세션 사이에 전달하는 정보

**context**는 프로젝트를 이해하고 개별 작업을 판단하는 데 필요한 현재의 공용 지식이다. 사용자가 어떤 상황에서 어떤 결과를 원하는지, 시스템이 어떻게 구성됐는지, 무엇을 왜 결정했는지, 무엇이 구현·검증됐고 아직 무엇을 모르는지를 담는다. 모든 task와 manager가 읽으며, 준비 세션이 처음 쓰고 manager가 갱신한다. 다음 행동의 타당성을 바꾸는 조건·예외·구체적인 근거를 유지한다.

**plan**은 프로젝트의 완료 기준에 도달하기 위해 현재 남은 일과 그 선행 관계를 정리한 계획이다. 무엇부터 해야 하는지, 어떤 문제를 어느 작업에서 해결할지, 이후 무엇을 검증할지 설명한다. manager가 실제 결과에 따라 갱신한다. 지금 알고 있는 프로젝트의 상태를 설명하는 context와, 그 상태에서 다음에 할 일을 정하는 plan은 역할이 다르다.

**objective**는 task 하나가 달성해야 할 목표를 작업 가능한 수준으로 지정한 문서다. 프로젝트에서 맡은 역할, 만들어야 할 결과, 완료를 판정할 조건, 구현자가 정할 수 있는 부분, 검증 방법을 담는다. 준비 세션 또는 직전 manager가 작성하고, 배정받은 task가 따른다. 예를 들어 “CLI 구현”만 적지 않고 어떤 입력에서 어떤 stdout·stderr·종료 코드가 나와야 하는지 지정한다.

**seam**은 서로 다른 구성 요소가 만나는 경계에서 제공자와 소비자가 함께 따르는 동작의 약속이다. 제공자는 약속한 기능을 구현해 노출하고, 소비자는 그 기능을 호출하거나 결과를 읽어 사용한다. 여기서 **인터페이스**는 그 접점의 형태다. 함수·HTTP 요청·파일 형식·명령행 등이 인터페이스가 될 수 있다. seam은 그 형태와 함께 입력의 의미, 결과, 실패, 부수 효과 등 의존에 필요한 동작을 정한다.

예를 들어 `count_lines(text: str) -> dict[str, int]`만으로는 공백 줄을 세는지, 대소문자를 구분하는지 알 수 없다. seam은 “길이 0인 줄만 제외하고, 공백과 대소문자를 보존한다”처럼 양쪽 구현의 판단이 같아질 만큼 정의한다. 함수 내부의 자료구조처럼 외부에서 의존하지 않는 세부사항은 제공자의 재량이다. `provides`는 구현해 노출할 seam, `uses`는 외부 제공자에게 맡기고 사용할 seam을 가리킨다. 테스트 대역으로 사용을 검증했어도 외부의 실제 구현과 연결됐다는 뜻은 아니다.

호환성을 결정하는 형식은 해당 프로젝트의 실제 타입·함수 선언·데이터 스키마 같은 파일을 정본으로 연결한다. 제공자와 소비자는 같은 정의를 사용한다. seam에는 그 파일의 경로·심볼, 호출 위치와 방식, 입력·출력의 구체적인 구조, 오류 표현, 확인할 명령을 적는다. 자연어는 그 정의로 표현하지 못하는 동작의 의미와 조건을 설명한다. 공유 정의가 아직 없으면 준비 세션이나 선행 task가 먼저 만든다. 모든 프로젝트에 별도 스키마 언어나 생성기를 도입할 필요는 없다.

줄 집계 예제에서는 contracts.py의 LineCounter가 `text` 매개변수와 반환 타입을 정의한다. 제공자는 공유 검사로 실제 함수의 import·호출 형식·반환 구조·사례를 확인한다. 소비자는 그 정의에서 만든 테스트 대역으로 인자 이름과 호출 방식의 불일치를 확인한다. 이후 실제 연결 검증에서 두 구현을 함께 실행한다. 단순히 이름이 S1로 같거나 JSON 형식 검사가 통과한 사실로 이 검증을 대신하지 않는다.

**report**는 task가 수행한 결과를 다음 manager에게 전달하는 보고서다. 무엇을 변경했는지, 각 완료 조건을 충족했는지, 실제로 무엇을 검사했는지, 어떤 사실·문제·미정 사항이 후속 판단에 영향을 주는지와 근거를 담는다. task가 report.json으로 작성한다. manager.json은 manager가 그 보고들에 내린 판단, 공용 정보의 변경, 다음 배정 또는 종료 결정을 기록하는 별도 보고서다.

**evidence(근거 자료)**는 보고의 주장을 확인할 실제 파일·검사 출력·원자료다. 보고서의 evidence 필드는 그 자료의 위치를 가리킨다. 세션의 stdout·stderr를 담은 **log**는 실행 기록이며, 그 안의 주장이 자동으로 참이 되는 것은 아니다. **findings(발견)**는 수행 중 얻은 정보 중 다음 작업의 판단을 바꾸는 사실·결정·가정·문제·질문이다. manager는 발견을 다음 작업에 반영하거나 근거를 들어 종결하는 **처분(disposition)**을 기록한다.

이 문서에서 **계약**은 세션들이 함께 따르기로 정한 목표·책임·절차·형식·경계 동작의 조건이다. **정본**은 같은 내용을 확인하거나 변경할 때 기준으로 삼는 파일이다. 아래에서 정보별 정본과 작성 책임을 지정한다.

## 종료와 완료의 구분

| 표현 | 정확한 의미 |
|---|---|
| 세션 종료 | Codex 프로세스가 끝났다. 배정된 목표를 달성했는지는 아직 별도 판단이다. |
| task 완료 | 해당 objective의 모든 완료 조건을 충족했고 report의 status가 complete다. 프로젝트 전체의 완료를 뜻하지 않는다. |
| 형식 검사 통과 | check.py가 파일의 형식·목록·참조 규칙 위반을 찾지 않았다. 보고된 내용의 진실성이나 요구 충족까지 입증하지는 않는다. |
| review task 완료 | 배정받은 검토를 수행하고 발견과 근거를 보고했다. 결함을 발견한 경우도 검토 자체는 완료할 수 있다. |
| 개발 완료 | 최종 review 후 manager가 프로젝트 완료 기준과 남은 문제를 판단해 next를 null로 제출했다. |

**검증**은 주장이나 완료 조건이 실제로 맞는지 근거를 대조하는 활동이다. 테스트 실행, 코드와 요구의 대조, 재현 입력 확인 등이 포함된다. **형식 검사**는 그중 파일의 기계적으로 판정 가능한 규칙을 검사하는 좁은 활동이다. **실제 연결 검증**은 테스트 대역 대신 실제 제공자와 소비자를 함께 실행해 그 조합의 동작을 확인하는 검증이다.

## 공용 정보와 책임

run 루트에는 `sources/`, `context.md`, `plan.md`, `seams.md`가 있다. manager의 공통 모델 설정을 지정하려면 `settings.json`도 둔다. 각 phase는 `run/phases/<phase>/`에 있다. 그 안에 `phase.json`, `tasks/<task>/objective.md`, `tasks/<task>/report.json`, `tasks/<task>/evidence/`, `logs/`, `manager.json`을 둔다.

task가 수행되는 동안 공용 문서·phase.json·objective는 고정한다. 모든 task가 종료된 뒤 manager가 공용 현재본을 갱신한다. phase별 입력 사본은 만들지 않는다. report, evidence, manager.json, 완료된 배정은 후속 세션이 다시 쓰지 않는다.

사용자 요구는 달성할 결과의 근거다. seam은 경계의 약속이다. 코드와 검증 출력은 실제 동작의 근거다. 이 세 가지가 다르면 차이를 보고하고 해소한다. 최신 코드가 요구를 자동으로 대체하지 않는다. report의 관찰도 자동으로 새로운 요구가 되지 않는다.

공용 context에는 목적·사용 상황·범위·완료 기준·구성 요소와 데이터 흐름·운영 전제·현재 검증 상태·결정과 이유·가정·미정 사항을 구체적으로 둔다. 이후 판단에 필요한 맥락 묶음은 `## C1 이름` 형태로 식별한다. 완료 기준은 `### G1 이름` 형태다. 각 항목에는 내용이 있어야 한다. 사실, 결정, 추론, 가정, 미정을 문장으로 구분하고 근거를 지정한다.

plan에는 현재 남은 일, 순서와 선행 관계, 미해결 문제와 다음 행동, 실제 연결 검증 책임, 최종 review 범위를 적는다. 먼 미래의 task들을 근거 없이 확정하지 않는다.

seams의 각 항목은 `## S1 이름` 형태다. 호출·읽기 위치, 제공·소비 구성 요소, 현재 구현 상태, 입력·출력·경계 사례·실패·부수 효과·검증 사례와 내부 구현 재량을 해당 경계에 필요한 만큼 명시한다. 이름과 시그니처만 적어 서로 다른 동작이 모두 맞다고 읽히게 두지 않는다. 독립적인 인터페이스가 없으면 seams 문서에 그 사실을 적고 S 항목은 두지 않아도 된다.

같은 인터페이스를 개정할 때는 기존 S ID를 유지하며 내용을 고친다. manager는 바뀐 조건·이유·영향받는 구현·다시 필요한 검증을 보고한다. 이전 phase의 conforms를 개정 후 계약의 충족 증거로 자동 간주하지 않는다. 안정적인 C/S/G ID를 다른 의미의 항목에 재사용하지 않는다. 근거가 참조하는 항목은 참조가 끊어지지 않게 유지하고, 통합·폐기가 필요하면 해당 항목에 현재 의미와 이동 위치를 분명히 적는다.

## Task 수행

1. 이 문서를 읽고, 공용 context·plan 전체와 자기 phase.json을 읽는다. 프로젝트 전체의 목적, 현재 단계, 자기 작업의 상·하류 역할을 구체적으로 파악한다.
2. seams의 공통 설명과 배정의 provides·uses 항목을 전문으로 읽는다. 자기 objective와 inputs에 지정된 원자료를 읽고, 필요한 정의와 근거를 원문까지 따라간다.
3. objective의 각 완료 조건을 구현과 검증으로 옮길 수 있는지 확인한다. 판단에 필요한 값이 비어 있으면 아래의 입력 해석 표에 따라 처리한다.
4. 배정된 프로젝트 writes 안에서 작업한다. 자기 report와 evidence는 별도로 작성할 수 있다. 다른 task의 파일, 공용 계약, 검사기, 실행기를 수정하지 않는다. Git checkout·reset·commit 등 전체 작업 상태를 바꾸는 작업은 수행하지 않는다.
5. objective의 검증을 수행하고 실제 출력과 필요한 근거를 자기 evidence에 보존한다. 수행하지 못한 검사와 그 영향을 밝힌다. 출력을 새로 꾸며서 증거로 만들지 않는다.
6. report.json을 아래 형식으로 쓴다. `python <engine>/check.py report <repo> <run> <phase> <task>`를 실행한다. 오류가 있으면 고치고 다시 검사한다. 통과 뒤 report나 근거를 수정했으면 다시 검사한다.
7. 마지막 응답에 report 경로와 작업 상태를 알리고 끝낸다. 다음 세션이 읽는 정본은 report 파일이다.

같은 phase의 다른 task가 작업 중인 구현을 읽거나 기다리는 것을 전제로 진행하지 않는다. 제공자는 seam을 구현하고 소비자는 그 계약을 사용한다. 아직 없는 제공자의 구현을 자기 제품 코드에 복제하지 않는다. 지정된 자체 테스트에서 대역을 사용할 수 있지만, 실제 연결 검증과 구분해 보고한다. 외부 구현의 존재·정확성을 확인하지 않았으면 확인했다고 쓰지 않는다.

| 입력을 해석하며 만난 상황 | 작업과 보고에 반영하는 방법 |
|---|---|
| 현재 코드·설정·원자료에서 확인할 수 있는 사실이 필요하다. | 해당 자료를 읽거나 명령으로 확인한다. 그 결과가 후속 작업에도 필요하면 findings의 fact로 근거와 함께 남긴다. |
| objective가 재량으로 둔 내부 구현 선택이다. | 완료 조건과 seam을 만족하는 방법을 선택한다. 이후 판단에 영향을 주는 선택만 decision으로 보고한다. |
| 두 해석이 다른 사용자 동작이나 seam을 만든다. | 근거와 위임된 결정 범위로 해소되는지 확인한다. 해소되지 않으면 영향을 받는 부분의 확정을 보류하고 question에 가능한 해석·영향·필요한 결정을 적는다. 독립적으로 수행할 수 있는 부분은 진행한다. |
| 문서의 약속과 실제 구현이 다르다. | 재현 입력·기대 동작·실제 동작을 issue로 보고한다. 자기 쓰기 범위의 계약 위반은 수정하고, 외부 구현이나 계약 개정이 필요한 부분은 다음 조치로 지정한다. |

question이나 issue 때문에 완료할 수 없는 A 항목은 fail 또는 not_run으로 보고하고 그 관계를 detail에 적는다. manager는 이 정보로 다음 배정을 만들 수 있어야 한다.

review phase의 task는 프로젝트 파일을 수정하지 않는다. 배정된 범위의 요구 충족·사용자 경로·seam·회귀·미검사 부분을 확인하고 증거 있는 발견을 보고한다. 검토를 모두 수행했다면 결함이 있어도 task는 complete일 수 있다. 제품 합격 여부는 별도다.

## Manager 수행

1. 이 문서, 공용 context·plan·seams와 직전 phase.json을 읽는다.
2. 모든 배정 task의 report를 전문으로 읽는다. 누락과 파손을 구분한다. 공용 문서를 갱신하기 전에 각 report 검사 명령을 실행하고 필요한 근거를 확인한다. 누락을 성공으로 처리하지 않는다.
3. 완료된 것, 실패한 것, 미검사 범위, seam의 문제, 가정과 질문을 파악한다. 다음 배정이나 종료를 좌우하는 주장은 실제 파일·검사 출력·원자료와 대조한다. 모든 단위 검사를 무조건 다시 실행할 필요는 없다.
4. 모든 findings에 처분을 내린다. 현재 context·plan 또는 다음 objective에 반영하거나, 근거를 들어 해결·기각한다. 부분 완료와 누락 보고의 후속 조치도 지정한다.
5. 공용 문서를 필요한 만큼 갱신한다. 기존의 유효한 조건·예외·근거·미해결 사항을 보존한다. 바뀌지 않은 내용을 다시 요약하지 않는다. 갱신 전후 내용을 편집 차이 등으로 대조하고 변경·제거·통합한 의미와 근거를 기록한다. 전체 과거 입력 사본의 영구 보관은 요구하지 않는다.
6. 실제 상황에 맞게 다음 phase를 정한다. 같은 phase의 task들은 독립적으로 진행할 수 있어야 한다. 쓰기 범위뿐 아니라 상대의 미완성 파일을 읽는 검사, 공유 DB·포트·캐시·lockfile 등 실행 환경의 충돌도 살핀다. 독립화하기 어렵다면 합치거나 다음 phase로 나눈다. 그러나 최대한 가능한 만큼 독립화하여 병렬 진행을 할 방법을 찾아 작업의 Throughput을 증가시킨다.
7. 다음 phase의 phase.json, 모든 objective, task별 evidence 디렉터리, logs 디렉터리를 만든다. task별 실행 모델을 선택할 필요가 있으면 배정 객체에 model과 effort를 기입한다. 그 task들이 읽을 공용 현재본을 완성한다. phase ID는 새로운 소문자 영문·숫자·하이픈 ID로 정한다. 이전 phase를 다시 실행할 ID로 돌려놓지 않는다.
8. 직전 phase에 manager.pending.json을 작성한다. `python <engine>/check.py handoff <repo> <run> <phase>`를 실행한다. 형식·참조 오류를 고쳐 통과시킨다. 검사기가 task report도 검사하므로 참조 항목을 불필요하게 삭제하지 않는다.
9. 검사 후 입력·제출물을 바꾸지 않고 manager.pending.json을 같은 디렉터리의 manager.json으로 이름 바꾼다. 그 경로를 알리고 세션을 끝낸다. 뒤늦게 변경했다면 다시 검사한다.

manager는 프로젝트 코드를 직접 수정하지 않는다. 제품 수정과 연결 검증은 task로 배정해 결과와 검토 범위를 남긴다. 미래의 정해진 단계표가 현재 보고보다 우선하지 않는다. task 하나인 phase도 정상이다.

최초 준비 세션은 같은 계약으로 원래 요구·공용 문서·첫 phase·출력 디렉터리를 만들고 `python <engine>/check.py phase <repo> <run> <phase>`를 통과시킨다. 처음부터 manager.json을 만들어 실행을 건너뛰지 않는다. 실행기가 준비 세션을 자동 호출하지는 않는다.

모델 선택을 manager에게 맡길 때는 준비 세션이 사용할 수 있는 모델 ID, effort 값, 선택 기준을 context에 기록한다. task별 선택이 없으면 기본 설정으로 실행할 수 있으므로 배정마다 값을 만들어 넣을 필요는 없다. settings.json은 준비 시 정하는 전역 실행 설정이며 manager의 phase별 편집 대상에 포함되지 않는다.

## Review와 종료

필요한 구현·실제 연결 검증이 완료됐다고 판단하면 다음 phase를 review로 만든다. 필요한 범위와 관점에 따라 task를 배정한다. 고정 인원이나 검토 횟수는 없다.

종료는 다음 조건을 모두 충족했을 때 `next: null`로 제출한다.

- 직전 phase가 review이고 그 모든 task가 배정된 검토를 완료했다.
- 모든 review report를 읽었다. 미검사·판정 불가 범위가 프로젝트 완료 기준을 가리지 않는다.
- context의 G 완료 기준 전부에 충족 근거가 있다.
- 모든 발견을 처리했다. 문제 아님이나 허용된 잔여사항이라는 판단도 실제 근거와 위임된 권한으로 설명한다. 요구 미충족을 이름만 바꿔 잔여사항으로 남기지 않는다.
- review 이후 제품 코드나 결과를 바꾸는 설정·요구·seam을 수정하지 않았다.

수정이 필요하면 다음은 work phase로 만들고 그 뒤 다시 review한다. 검토 완료는 제품 합격과 다르다. `next: null`은 일시 중단 표현이 아니다. 중요한 외부 결정이 필요하면 정확히 상신하고 성공 종료로 꾸미지 않는다. manager가 제출하지 못한 상태에는 실행기의 자동 복구가 없다.

## 파일 형식의 공통 규칙

텍스트는 UTF-8로 쓴다. UTF-8 BOM도 검사기가 읽을 수 있다. JSON은 아래 명시한 필수·선택 키를 사용한다. 알려지지 않은 키, 중복 키, NaN·Infinity는 거부한다. 선택이라고 명시한 항목 외에는 필수다. 내용이 없는 목록은 `[]`, 정의된 미정 값만 `null`로 쓴다. 문자열 필드는 공백만으로 채우지 않는다.

JSON은 항목을 식별하고 연결하는 바깥 형식이다. narrative·detail·reason·decision·plan_update 등의 문자열에는 필요한 만큼 상세한 자유 산문을 쓴다. 여러 문단, 소제목, 목록, 코드 예시를 포함한 Markdown을 사용할 수 있다. JSON 문자열의 줄바꿈은 `\n`으로 저장하며, 파일을 만드는 언어의 JSON 직렬화기를 쓰면 줄바꿈과 따옴표를 직접 이스케이프할 필요가 없다. 검사기는 이 산문의 문단·절·분량을 제한하지 않는다.

보고에는 관찰한 내용, 판단의 근거, 적용 조건, 예외, 결과와 미검증 부분이 후속 세션의 판단에 필요한 깊이로 담겨야 한다. 상태와 근거 경로만으로 그 설명을 대신하지 않는다. 같은 내용을 여러 필드에 반복할 필요는 없다. narrative에는 작업 전반을 연결해 설명하고, 항목별 detail과 reason에는 해당 판정에 필요한 구체적인 내용을 둔다.

파일 참조는 `repo:src/module.py`, `run:context.md#C1`처럼 쓴다. 루트 기준 상대 경로에는 `/`를 쓰며 절대 경로·`..`·경로 별칭을 통한 루트 이탈을 허용하지 않는다. `#` 뒤에는 실제 Markdown 항목 C/S/A/G ID만 사용한다. 같은 문서의 같은 ID는 중복할 수 없다. C/S는 `##`, A/G는 `###` 제목으로 쓰고 이름과 본문을 둔다. 코드 블록 안의 제목은 실제 항목이 아니다.

references와 evidence는 파일 또는 항목 참조 문자열 목록이다. 실행 디렉터리인 cwd만 `repo:.` 또는 `run:.` 및 하위 디렉터리를 가리킨다. evidence는 주장을 확인할 자료의 좌표다. 코드 파일 경로만으로 모든 동작이 입증되는 것은 아니다.

### settings.json과 실행 모델

**model**은 Codex가 사용할 모델의 식별자다. **effort**는 모델이 추론에 들일 처리 정도를 요청하는 설정으로, Codex의 model_reasoning_effort에 전달한다. 사용할 수 있는 값은 해당 모델과 Codex 환경이 정한다. 검사기는 문자열 형식만 확인하며 모델 목록이나 지원 조합을 조회하지 않는다.

settings.json을 사용하면 최상위 필수 키는 manager이고 값은 객체다. manager 안의 model·effort는 각각 선택 문자열이다. 파일 자체가 없거나 해당 키를 생략하면 공통 CLI 옵션과 Codex 환경의 기본값을 따른다. `{ "manager": {} }`도 유효하다. 실행기는 이 전역 설정을 시작할 때 한 번 읽어 이후 모든 manager 세션에 적용한다.

task의 model·effort는 그 task에만, settings.json의 manager 선택은 manager에만 적용한다. 각 선택은 같은 항목의 공통 CLI 옵션보다 우선한다. model은 `--model`, effort는 `-c model_reasoning_effort=...`로 전달한다. 모델 또는 effort 하나만 선택해도 된다.

### phase.json

| 키 | 값 |
|---|---|
| kind | work 또는 review |
| purpose | 왜 지금 이 phase가 필요한지 |
| tasks | 아래 task 객체 하나 이상의 목록 |

task 객체의 필수 키는 `id, inputs, writes, provides, uses`이고 선택 키는 `model, effort`다.

- id: 소문자 영문·숫자 묶음을 하이픈으로 연결한 ID. 같은 phase 안에서 유일하다.
- inputs: 공용 문서·자기 objective 외에 반드시 읽을 파일 참조 목록.
- writes: 프로젝트 상대 파일 또는 `/`로 끝나는 디렉터리 목록. 디렉터리는 하위 전체를 포함한다. glob은 쓰지 않는다. 다른 task의 범위와 겹치지 않는다. 실행 기록·engine을 포함하지 않는다. 자기 report·evidence는 이 목록에 반복하지 않는다. review의 writes는 빈 목록이다.
- provides, uses: 공용 seams의 S ID 목록. 같은 phase에서 seam 제공자는 하나다. 그 밖의 독립성은 manager가 내용을 보고 확인한다.
- model, effort: manager가 해당 task에 선택한 실행 모델과 추론 설정. 생략한 항목은 공통 CLI 옵션과 Codex 환경 설정을 따른다.

### objective.md

다음 네 개의 `##` 절을 순서대로 사용한다. 본문은 필요한 만큼 상세하게 쓴다.

1. 목적과 역할: 프로젝트 결과에 대한 기여, 지금 수행하는 이유, 상·하류 역할.
2. 완료 조건: `### A1 이름`부터 관찰 가능한 조건과 판단 근거. 최소 하나. 모든 A 항목은 이 절 안에 둔다.
3. 판단과 경계: 확정 사항, 구현 재량, 변경할 수 없는 약속, 불확실성 처리.
4. 검증 방법: 실제 cwd·환경·명령 또는 판단 절차·입력·기대 결과·미검증 범위와 후속 책임.

### report.json

| 키 | 값 |
|---|---|
| status | complete / partial / blocked |
| narrative | 작업 전반의 보고 본문. 수행 내용·방법과 이유·관찰·검증 결과와 한계·후속 영향이 연결되는 자유 산문 |
| acceptance | `{id, result, detail, evidence}` 목록. 배정 A ID 전부를 정확히 한 번. result는 pass/fail/not_run |
| changes | `{path, detail}` 목록. 실제 변경한 프로젝트 파일. 삭제도 해당 파일 경로로 보고 |
| seams | `{id, result, detail, evidence}` 목록. provides·uses의 S ID 합집합을 정확히 한 번. result는 conforms/deviation/not_checked |
| findings | `{id, kind, detail, evidence, affects, next_action}` 목록 |
| checks | `{command, cwd, result, exit_code, evidence, detail}` 목록 |

모든 A가 pass일 때 complete다. 필수 입력·결정·의존성이 없어 진행할 수 없으면 blocked다. 나머지 미완료는 partial이다. 이미 수행한 유효한 작업은 blocked라도 보고한다. acceptance의 pass와 seams의 conforms에는 비어 있지 않은 evidence가 필요하다.

changes.path는 writes 안의 구체적인 파일 경로다. changes.detail은 실제 변화의 의미를 설명한다. findings.id는 task 안에서 유일한 F1 형태다. kind는 fact/decision/assumption/issue/question이다. affects는 영향을 받는 문서·파일·항목 참조 목록이다. 다음 판단을 바꾸는 발견을 기록하되 모든 사소한 구현 선택을 나열하지 않는다. 확인하지 못한 사항을 사실로 쓰지 않는다.

checks.result는 pass/fail/not_run이다. 실행한 명령의 exit_code는 실제 정수이고 evidence는 비어 있지 않은 목록이다. 실행하지 않은 명령은 exit_code가 null이며 detail에 사유를 적는다. 검증 목표에 실패 코드 관찰이 포함될 수 있으므로 pass가 반드시 exit_code 0을 뜻하지는 않는다. 기대값을 detail에 설명한다.

형식 검사는 업무 성공과 별개다. partial·blocked도 올바른 제출물이다. report 검사 자체를 checks에 넣기 위해 자기 report를 반복 수정할 필요는 없다. 검사 출력은 별도로 남길 수 있다.

### manager.json

| 키 | 값 |
|---|---|
| next | 새 phase ID 또는 종료 시 null |
| decision | manager의 판단 본문. 보고들의 관계·상충점·근거·불확실성을 설명하고 다음 배정·종료의 이유를 전개하는 자유 산문 |
| reports | `{task, state, detail, evidence}` 목록. 직전 phase의 task 전부를 정확히 한 번. state는 read/missing/invalid |
| dispositions | `{item, action, destination, reason, evidence}` 목록. read report의 모든 findings를 정확히 한 번 |
| context_updates | `{item, action, destination, reason, evidence}` 목록 |
| plan_update | 계획의 변경 내용. 변경이 없으면 그 사실과 이유 |
| seam_updates | `{id, detail, evidence}` 목록. 변경한 S 항목. 없으면 빈 목록 |
| completion | 계속 진행하면 null, 종료하면 아래 완료 객체 |

reports의 read는 실제로 읽고 report 검사를 통과한 경우다. missing은 파일 부재, invalid는 존재하지만 report 검사에 실패한 경우다. 각 행의 evidence는 비우지 않는다. missing/invalid이면 다음 phase가 있어야 하며, detail에 복구·재확인 배정을 설명하고 evidence에 다음 task의 objective 참조를 포함한다. 실패한 report를 임의로 고쳐서 task가 작성한 것처럼 만들지 않는다.

dispositions.item은 `001/cli/F1`처럼 phase/task/finding ID다. action은 carry/resolve/reject다. carry이면 destination에 공용 context·plan 또는 다음 task objective를 포함한다. resolve/reject에도 reason과 evidence가 필요하다. 종료할 때 carry 항목을 남기지 않는다.

context_updates.item은 C ID다. action은 add/amend/replace/retire다. reason은 무엇을 왜 바꿨는지 설명하고 evidence는 비우지 않는다. retire 외에는 destination도 비우지 않는다. add/amend는 해당 C 항목이 현재 context에 존재해야 한다. 바뀌지 않은 항목을 반복 기록할 필요는 없다. 기존 의미의 보존과 모든 중요한 변경의 기록 여부는 manager가 확인한다.

seam_updates.detail은 바뀐 조건·이유·소비자 영향과 필요한 후속 검증을 설명한다. evidence는 비우지 않는다. 형식 검사는 자연어 의미가 보존됐거나 구현이 새 seam을 충족한다고 판정하지 않는다.

completion의 키는 `criteria, review_reports, remaining`이다. criteria는 `{criterion, result, evidence}` 목록이다. criterion은 `run:context.md#G1` 형태로 현재 G 항목 전부를 정확히 한 번 참조하고 result는 satisfied이며 evidence는 비우지 않는다. review_reports는 직전 review phase의 모든 report 참조다. remaining은 기존 범위·권한에서 허용된 잔여사항과 그 근거를 설명하는 문자열 목록이다. 없으면 빈 목록이다.

## 검사 결과를 해석하는 방법

검사 명령은 통과 시 0, 위반 발견 시 1을 반환한다. 첫 위반의 파일·항목·내용을 출력한다. 오류를 고치고 통과할 때까지 다시 실행한다. 도구 고장이나 실행 불가는 통과가 아니다. 형식을 맞추기 위해 계약·검사기를 약화하지 않는다.

검사기는 키·형·허용값, ID와 목록 대응, 참조 존재, 선언된 쓰기 범위와 중첩, 다음 phase의 준비 상태, 종료의 구조적 조건을 확인한다. 실제 모든 쓰기 행위, 읽기 이해도, 증거의 의미, 자연어 갱신의 의미 보존, 성공 주장이나 사용자 권한의 타당성을 보장하지 않는다. 이 부분은 task의 실제 작업, manager의 근거 확인, review가 책임진다.


# 파일: docs/do-math/continuous-development-2026-10-13/context.md

# do-math 재편의 현재 공용 맥락

## C1 사용자 목표와 완료 기준

결함이 시험을 빠져나가는 기제를 막는 것이 목표다. 실제 제품 경로를 시험하고 대역은 외부 경계에 두며, 계약·불변식에서 기대값을 얻고, 이전 개선을 보존한다. 정확성·합리적인 개발 속도·유지 비용을 함께 만족해야 한다. 출발 요구와 사용자의 교정은 run:sources/user-decisions.md, 원문 위치와 시작 상태는 run:sources/baseline.json 및 run:sources/requirements-index.json에 있다. 요구 목록이 아니라 검토 가능한 증거로 아래 기준을 충족해야 한다.

### G1 원문 기능·시험 의무

원래 1단계 19개와 2단계 11개 의무의 명시 모집단·입력축·성질을 현재 구현과 시험에 연결한다. 실제 생산/수신, 저장, 형식·부재/null, 전이, 진행성, 정산, 역할·근거, 대기·계수, 시간·발동, 기동·운전·문서를 포함한다. 각 ID에 충족한 성질, 증거 판본, 구체적 남김과 판정이 있다. 목록 존재·설명·형식 검사만으로 의미 검증을 대신하지 않는다. 원문에 없는 무한 입력 공간의 무결함 증명을 새 종료조건으로 만들지 않는다.

### G2 기존 개선과 기대값 보존

원래 K ID의 보존 성질 61개와 원래 P2 12개 ID를 각각 현행 근거에 연결한다. K ID는 K-01~K-78 안의 비연속 집합이며 sources/requirements-index.json의 preservation 모집단을 따른다. 과거 원문의 timeout 등 폐기된 수단은 최신 사용자 지시와 현재 계약으로 처리한다. 기존 변경 재검토는 실제 diff·현재 소비자·원보고를 사용해 유지/교정/제거/추가 판정 필요를 결정한다. B01~B109를 25영역에 매핑했다는 사실은 검토 완료가 아니다. 결함 동작을 정상 기대값으로 남기지 않는다.

### G3 검증 방식의 실질

실제 제품 코드를 대역으로 가리는 시험, 현재와 다른 fixture, 속도 때문에 약해진 단언, 실제 최종 반환을 증명하지 못하는 문서용 AST 추정 등을 해소한다. 부류·등록·일반 검사가 현재 구성원을 실제로 검사하며 누락을 실패로 드러내는지 확인한다. 구현 방식의 복잡성과 실익을 검토하고 불필요한 장치를 늘리지 않는다. 의미 검토와 최종 실행 대기를 구분한다.

### G4 최종 판본 전체 일반 검사

최종 제품·시험 판본에서 공식 run_tests.py의 기본 전체 선택을 완결한다. 선택과 실제 결과가 전건 대응하고 실패·오류·미실행이 없어야 한다. 조건부 환경 건너뜀은 원문 계약상 정당성을 별도 판정하고 통과로 세지 않는다. 실행 전후 소스 해시와 종료 상태를 보존한다. B129의 실패 보고와 이후 부분 수리를 더해 전체 성공으로 만들지 않는다.

### G5 재사용 없는 최종 T3

최종 판본의 --tier T3 --full 실행으로 측정 누락 없는 분기 합집합과 함수 진입/선택 색인을 확보한다. 미도달은 실제 누락을 수리하거나 원문상 정당한 제외의 근거를 검토한다. 과거 수치·증분 캐시·부분 선택을 fresh 전체 증거로 대체하지 않는다.

### G6 대상 함수 전체의 극단 변이와 정상 기준

현재 대상 함수·변이 종류·선택 시험·정상 기준의 모집단을 실제 코드와 T3 자료로 확정한다. 기존 17개 파일 분할은 실행 준비의 출발점이며 고정된 함수 수가 아니다. 정상 기준 통과와 각 변이의 실제 결과를 대응시킨다. 시간 초과·측정 부재·환경 실패를 변이 포착으로 세지 않으며 생존·미실행을 숨기지 않는다.

### G7 실제 경계와 말뭉치

T4의 실제 구현 계약, T5의 최소 공급자 실호출 및 Job·Lean/Mathlib·예약·학술 도구 등 요구된 실제 연쇄를 현재 환경에서 확인한다. 공급자별 최소 호출을 실제 녹화와 함께 사용하고 판본·조건·실패·파싱 결과를 보존한다. --version 성공이나 합성 출력을 모델 호출 성공으로 세지 않는다. 필요한 외부 조건이 없으면 해당 기준은 미충족이며 정확히 상신한다.

### G8 최종 검토와 인도 일치

G1~G7의 증거를 대상으로 제품 수정 없는 최종 review phase를 수행한다. 모든 기준의 근거, 이전 발견의 처분, 실제 연결, 남김을 대조한다. 검증한 제품·시험·제품 문서와 main·미러·지침이 일치한다. review 후 그 내용을 바꾸면 필요한 work와 review를 다시 배정한다. next:null은 이 전체 완료에만 사용하며 중단·문제 은폐에 사용하지 않는다. push는 하지 않는다.

## C2 시작 당시 실제 상태와 증거의 한계

준비 시 확인한 HEAD는 56e961ff2b4666a373839e6524a9701d1f9c1462(2026-10-06)다. 준비 파일을 커밋하면 HEAD는 바뀌므로 이것을 영구 실행 전제나 미래 판본으로 쓰지 않는다. 각 task는 자기 입력의 현재 해시와 변경 여부를 확인한다. baseline의 문서·코드 해시가 달라졌다면 새 근거로 상태를 재판정한다.

B129는 기본 3990개 실행이 완결됐지만 3988통과·1실패·1건너뜀, successful=false, 10724초였다. 유일한 실패는 Git 대역 시험의 예외 세부 단언 누락이며 이후 관련 2개가 통과했다. 건너뜀은 Windows 심볼릭 링크 권한 부족(1314)이었다. 현재 전체 성공을 입증한 것은 아니다.

B130~B134는 조회·CLI·역할 입력 metadata·복원·profile_selection 문서 필드를 실제 결과로 연결했다. 각 관련 검사 22/25/26/28/28개는 그 범위의 증거다. DOC-RETURN-PURE와 DOC-RETURN-CLI는 종료됐고 ROLE은 _context 관련 남김, REVIEW/TRUST는 별도 남김이다. field_schemas의 현재 코드와 문서별 실제 소비를 확인해야 하며 단순히 남은 AST 호출 수를 완료율로 쓰지 않는다.

기존 계획에는 109개 추적 항목이 있고 4 complete, 2 partial_complete, 1 implementation_reviewed, 1 reviewed_pending_evidence, 101 planned다. 서로 다른 크기의 구현·근거 연결·검토·관문이 섞였으므로 4/109 완료율이나 미구현 101개로 표현하지 않는다. 상위 의무의 낡은 남김 문장과 최신 상세 기록을 구분한다. phase 001이 이 차이를 해소할 유한한 산출물을 만든다.

기존 실제 제품 수리와 유효한 검증은 유지한다. 반면 B110~B114의 문서 소스 추론 확장은 이후 반례로 교체 대상이 됐다. 최근 성과에는 이 재작업 비용도 포함돼 있다. 커밋 수·검사 수·새 보고서 수로 전체 진척을 대신하지 않는다.

phase 001의 세 분석 task는 모두 A1~A4를 완료했고 manager의 report 형식 검사를 통과했다. manager가 현재 HEAD 77b8f132c056bcb222e7b6ee431742aa4dc1f27e에서 baseline 979파일(제품969·원자료6·engine4)의 바이트 불변, 원래 19/11/61/12 ID·원문 대응, B129 및 B130~B134/repair 원보고 14개의 해시·선택/row 대응을 재확인했다. B129와 현재 Python 소스 차이는 8개이며 B134 green의 28개 부분 성공은 현재 Python 판본과 일치한다. 분석 complete는 G 충족이나 제품 합격이 아니다. 근거는 run:phases/001/manager-evidence/verification.json 및 세 task의 report다.

phase 002 mutation-baseline은 A1~A5를 완료했고 manager의 report 검사와 원자료 대조를 통과했다. 수리 전 실제 child 반례 1 fail/대조군 1 pass, 최종 관련 시험 58선택/58 passed와 exit 0을 보존했다. manager는 task 종료 파일 해시 2206개와 공식 보고의 Python 해시 862개가 현재와 일치하고, 전후 변경 12개가 배정 쓰기 범위와 일치함을 확인했다. 그중 2개는 생성된 .timings 캐시다. 실제 child fixture 19개(수리 전 2·최종 17)의 보고·시도 파일·정상 기준 연결도 대조했다. 검수 시 HEAD는 6385880f821743dab59bfc4853970597175e91b4이며 이번 관리 커밋 이후에도 이 해시는 당시 검증 좌표로 남는다. 이 부분 성공으로 G4~G7의 전체 실행을 대신하지 않는다. 근거는 run:phases/002/manager-evidence/verification.json과 run:phases/002/tasks/mutation-baseline/report.json이다.

phase 003 provider-smoke는 partial이다. A1/A3/A4의 지정 범위와 A2/A5의 실패를 manager가 승인했다. report 검사 뒤 종료 파일 2254개, 정본/미러 공식 보고의 Python 864개 해시와 선택/실제 row/exit, 세 실제 호출의 schema·prompt·worker·파일·종료 원자료를 대조했다. 변경 62개가 모두 writes 안이고 현재 종료 해시 불일치는 0개다. Claude 최종 1개 실호출과 정본 오프라인 23개는 통과했으나 Codex schema HTTP 400 및 미러 4선택 중 2실패는 미해결이다. 관리 검수 당시 HEAD는 ea4b4f0fc04dbc0f2b384ff4d60d7de5a817611d이다. 근거는 run:phases/003/manager-evidence/verification.json 및 run:phases/003/tasks/provider-smoke/report.json이며 구체적 현재 조건은 C12에 둔다.

phase 004 mirror-corpus도 partial이다. manager는 report 검사 후 종료 소스 2624개, 변경 9개와 writes, 양쪽 공식 보고의 Python 각 864개 및 14선택/14passed/exit 0을 실제 파일과 대조했다. 생성기 22개 성공·수리 전 5개 하위 사례 실패와 최종 생성/구조 검사도 원출력·실행 전후 해시로 확인했다. 미러 치환 실패는 해결됐고 정본 녹화는 불변이다. A3의 Git clean에서는 양쪽 manifest 두 파일의 변환만 남는다. 관리 검수 당시 HEAD는 d97525b213bbf0e3f5680f17fc623601143664f0이며 근거는 run:phases/004/manager-evidence/verification.json과 task report다. A1/A2/A4의 부분 성과를 유지하고 A3 미충족은 phase 005로 넘긴다. G4~G8 전체 성공은 아니다.

phase 005 corpus-git-bytes는 A1~A3 complete로 검수했다. report 검사 후 현재 종료 소스 2624개와 작업 전후의 두 속성 변경, 양쪽 corpus 88개 경로의 실제 Git raw/clean 출력·각 41개 명시 SHA 참조를 대조했다. 불일치는 0개이고 manifest·녹화 바이트는 불변이다. 각 트리의 6바이트 감소는 속성 한 줄 변경이다. 공식 --check의 1297파일 일치와 skill-only verified, 기존 양쪽 Python 각 864개·재생 각 14개와 생성기 22개 성공의 재사용 조건을 확인했다. 검수 당시 HEAD는 f0764fb192a405e6cf95fd9500f103ac11180cf3이다. 근거는 run:phases/005/manager-evidence/verification.json과 task report이며 모델 호출과 최종 전체 관문을 새로 수행한 결과는 아니다.

phase 005 F2의 engine 문서 차이는 작업 시작 전부터 존재했다. protocol.md의 phase 004 종료 SHA256 cd47a1cff33fccc82f5a3cf284831fece663e805d0a30569c62d097c1d91f3b4와 phase 005 시작/종료 및 이번 검수 SHA256 07d63532457b3b5b8732bad449c779fa45c11e9be51fcec69cd35ca4a6cf002f를 구분한다. task와 manager는 현재 protocol을 읽었고 engine을 수정하지 않았다. 첫 보조 검산의 exit 1은 전체 소스 불변 가정이 이 기존 차이를 만난 결과이며 제품 실패가 아니다. 원 실패 출력·당시 스크립트는 보존한다. 해시만으로 변경 주체·내용의 의미를 추측하지 않는다.

phase 006 codex-schema는 partial로 검수했다. report 형식 검사 후 시작 2624파일이 phase 005 종료와 같고, 종료 2640파일과 현재 파일의 차이가 0개임을 확인했다. 실제 50변경은 report changes 및 쓰기 범위와 일치한다. 공식 9묶음의 선택/고유 row/exit와 각 판본을 대조했으며 Codex 실호출 1passed와 11개 판정, 원/전송 schema·worker·파일·checkpoint·종료를 원파일에서 확인했다. 정본 corpus 18passed와 미러 14passed는 최종 Python 각 865개와 일치한다. 양쪽 각 18항목·51파일·223685바이트·50개 명시 SHA, 총102경로 raw/clean 동등성을 확인했다. 직접 소비 45건 중 11실패와 저장 pair의 성공 표본 공백 때문에 A3/A5는 미충족이다. A1/A2/A4의 지정 성과만 승인한다. 검수 당시 HEAD는 9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8이며 근거는 run:phases/006/manager-evidence/verification.json과 review.md다. 전체 관문의 성공은 아니다.

phase 007 provider-consumers는 A1~A5 complete로 검수했다. manager가 8개 공식 실행의 선택/고유 row/실제 exit와 소스 전후를 대조했고 최종 직접 소비98·경계74·corpus14·미러59개가 모두 passed였다. 이전11실패와 pair 두 성공 분기의 공백은 해소됐다. 시작2640파일은006 종료와 같고 task의26변경은 모두 writes와 report에 일치한다. 검수 시 현재와 종료 해시의 차이는 모델 정책에 따른 운영자 작문 도구4파일뿐이며 do-math는 불변이다. runtime124·smoke입력3과102 corpus 경로의 raw/clean을 검산했다. 검수 HEAD는 61f9e06fc15fb49ef30bf7d93c83c92e275eebad이고 근거는 run:phases/007/manager-evidence/verification.json 및 review.md다. 이 지정 회귀의 완료를 전체 일반/T3/변이/G7/최종 review의 완료로 확대하지 않는다.

phase 008 document-recovery는 A1~A4 pass·A5 fail의 partial로 검수했다. 현재2640파일과 task 종료 해시는 전건 같고30변경은 report/writes에 일치한다. 8개 공식 실행의 선택/고유row/exit·소스 전후를 대조했으며 최종 정본110건은106passed·4failed, 미러89건은85passed·4failed다. 두 최종 Python865파일은 현재와 같고 skip/error/미실행은 없다. P01 red2단언과 운영/복구·설치 지정 검사는 통과했으나 기존 CLI 함수 표기가 unowned field로 분류돼 전건 문서 검사4건이 실패한다. 현재/HEAD 원문과 당시 helper에서 같은 분류를 재현했고 현 함수 검사 표기로 해결 가능한 것을 확인했다. runtime124·smoke입력3·corpus102경로는 불변이며 Git raw/clean을 재확인했다. 검수 HEAD는12a751550dc06ac75cdc56058b622d8b621b21cd이고 근거는 run:phases/008/manager-evidence/verification.json 및 review.md다. 부분 성공을 최종 전체 관문이나 제품 합격으로 확대하지 않는다.

phase 009 document-callable은 A1~A3 complete로 검수했다. report 검사 후 현재2640파일과 종료 해시 전건 일치, 시작과008 종료 동일, 허용된 문서2·캐시2 변경만 있음을 확인했다. 원문에는 함수명 뒤 (...) 다섯 바이트만 추가됐다. 실제 callable·필드 검사와 nonexistent/noncallable 반려를 유지한 채 정본110·미러89 선택/고유row가 전건 passed·exit0이며008의 정확4실패가 양쪽 새 passed row에 연결된다. 각865개 Python과 문서의 실행 전후/현재 해시도 일치한다. task의 첫 mirror 계획 exit1은 개행 처리 오류로 제품 변화0이었고 수정 뒤 성공했다. manager 검산 첫 실행의 누락 인자 TypeError도 관리 스크립트만 고쳐 재검산했다. 검수 HEAD는 0af5dd66368b7409899b6eed5b04523db43db4c5, 근거는 run:phases/009/manager-evidence/verification.json·review.md다.008의 partial 원보고는 보존하고 그 F1/A5 남김만 새 근거로 닫는다. 전체 G 완료가 아니다.

phase 010의 두 report는 manager 형식 검사를 통과했다. host-smoke는 A1/A2/A4 pass·A3 fail의 partial이며 reading-limits는 조사 A1~A3 complete다. 현재2644파일은 host 종료와 전건 일치하고 시작2640파일은009 종료와 같다. 허용14변경, 공식 실행의 선택/고유row/exit·전후소스와 정본/미러 각4묶음 OS 원자료를 대조했다. 최종 host 각3passed와 관련61건의59passed·1failed·1error를 구별한다. 시작 사본의 정확 두ID도 동일 실패다. 사본976파일 중975개 비캐시 파일만 시작 해시와 같고 비용 캐시1개는 현재 캐시 복사라는 manifest 예외를 적용한다. task의 “976파일 시작 동등” 표현은 이 범위로 정정한다. 읽기16페이지160행·꼬리80행을 남기는 중간 절단·합산 절단 기록과 고정 입력50개 및 CLI 바이너리2개를 대조했다. 조사 완료는13-C/L01 충족이 아니다. 근거는 run:phases/010/manager-evidence/verification.json·review.md와 두 원report이며 최종 G 완료가 아니다.

phase 011 regression-reading은 A1~A4 complete로 검수했다. report 검사 후 현재2644파일과 종료 해시 전건 일치, 시작과010 manager 판본 동일, 허용10변경(정본4·미러4·비용캐시2)을 확인했다. focused6·최종 정본136/미러136의 선택·고유row·passed·exit0와 각867 Python 및 실행 전후소스를 대조했다.010의 정확 error/failed 두ID는 새 passed에 대응하며 runtime/helper/규칙은 불변이다. 읽기 문구는14행 한 문단만 교정됐고 원fixture16페이지160행과 중간/합산 절단을 대조했다. runtime124·입력3·corpus102경로와 host8원자료의 한정 재사용, Git raw/clean 및 --check1307파일을 확인했다. manager 첫 diff 검산의 exit1은 파일 순서를 달리 이어붙인 관리 스크립트 문제였으며 순서만 고쳐 통과했다. 근거는 run:phases/011/manager-evidence/verification.json·review.md다. 전체 G나 L01 인증은 아니다.

phase 012 lean-smoke는 A1~A4 complete로 검수했다. report 형식 검사 뒤 현재 2658파일과 종료 해시 전건 일치, 시작과011 manager 판본 동일, 허용22변경을 확인했다. 초기 live 두 건의 error1은 역사 실패로 유지한다. 최종 정본/미러 T5 각1passed, 관련 각48passed의 선택·고유row·실제exit0와 각869 Python 및 전후 소스를 대조했다. 실제 Mathlib 대표 컴파일과 정상 full32의존·타입 오류, 각20판정·5Job 종료, 설치 입력 바이트·11094판단파일 메타데이터 불변을 원자료로 확인했다. corpus 각19항목·56파일과 총112경로의 Git raw/clean, 새 원출력71704바이트와 기존18항목 보존을 검산했다. 근거는 run:phases/012/manager-evidence/verification.json·review.md다. 지정 Lean 경계의 완료이며 G 전체나 설치 신뢰 승인은 아니다.

phase 013 scheduler-smoke는 A1~A4 complete로 검수했다. manager report 검사 후 현재2674파일과 종료 해시 전건 일치, 시작과012 manager 판본 동일, 허용22변경을 확인했다. 초기 live 세 실행의 error1은 역사 실패로 유지한다. 최종 live1passed·정본/미러 각33passed의 선택·고유row·실제exit와 각871 Python을 대조했다. 세 성공 표본의 각19판정·26명령 원바이트·291 snapshot 파일, 실제 operator/engine start와 시각 wake의 미실행267011에서 새 ticks/Ready/0 전이, 최종세null·HOLD/연구무부수효과를 확인했다. live-final의 wake PID9492는 실제 관측됐으므로 보고서의 포괄적 PID 미관측 문장은 최종 정본/미러 관련 실행에 한정한다. 원보고는 고치지 않는다. corpus 각21항목·62파일과124경로 Git raw/clean·기존19항목 보존을 검산했다. 근거는 run:phases/013/manager-evidence/verification.json·review.md다. held 설치/OS 경계의 완료이며 연구 운전·전체 G 완료는 아니다.

phase 014 scholarly-smoke는 A1~A4 complete로 검수했다. manager report 검사 뒤 시작2726·종료2750파일, 이전013 검수본의 모든 경로 보존과 현재 종료 해시 전건 일치를 확인했다. 허용34변경(비용 캐시2 포함)은 report/writes와 같다. 초기 error1·failed1은 역사 실패로 남기고 최종 정본 T5 1passed/exit0·16판정과 최종 정본/미러 각46고유선택·46passed/exit0 및 각873 Python을 대조했다. 실제 세 CLI 호출은 각각 list_sources 한 요청이며 최종 native의 같은 ID 시작/완료·status=ok와49summary·양 본문, worker/argv/schema·nonce/final·로컬 종료를 확인했다. 초기 structured_content 부재 관측은 잘못된 키 조회였고 원report를 보존한 채 같은 원바이트와 현재 관찰자/최종 offline으로 정정됐다. corpus 각22항목·72파일·409886바이트 및144경로 raw/clean을 검산했다. 근거는 run:phases/014/manager-evidence/verification.json·review.md다. 지정 학술 목록 경계의 완료이며 search/fetch·전체 G 완료가 아니다.

phase 015 t4-adapter-report는 A1~A3 pass·A4 fail의 partial로 검수했다. report 검사 뒤 task 시작2667·종료2671파일과 현재 전건 일치, 허용16변경을 확인했다. 시작 모집단은014 inspected2750 중 skills/diff 부분이며 서로 다른 모집단의 숫자를 혼합하지 않는다. 최종 관련 정본/미러 각70선택·70passed·exit0와 각875 Python, 최종 T4 각295선택·고유row·283passed/6error/4failed/2skipped·exit1 및 소스 전후를 대조했다. 양쪽 각60worker의 실제 요청·판본·게시 SHA·branch DB, adapter5개의 원합집합 재분석을 확인했다. 측정 complete=true와 정본102/142·미러101/142 정보 도달은 기능 합격이 아니다. 근거는 run:phases/015/manager-evidence/verification.json·review.md다. 초기 실패와 정확 남김은 C11에 유지하며 G 전체 완료가 아니다.

phase 016의 두 task를 complete로 검수했다. manager가 두 report 형식 검사 뒤 현재2675파일과 fixture task 종료 해시의 전건 일치, 이전015 모집단2671파일과 시작의 동일성을 확인했다. 추가4개는 이전 snapshot에서 제외한 양쪽 T3-store이며 새 제품 변경이 아니다. fixture의12변경(정본5·미러5·비용캐시2)은 writes/report와 같고, 양쪽 경계21·unit/structure35 선택/고유row/exit0와 각875 Python 및 실행 전후를 대조했다. 이전 정확10error/failed와 bootstrap2가 새 passed row에 연결된다. 양쪽 각9worker 게시·요청·소스/artifact SHA와 OS 원핸들/종료를 확인했다. provenance는 도입bbe64043의 첫 부모010b0597에서 추출한910파일·9901995바이트·901blob을 새 Git 조회로 전건 검산했다. 입력 준비 완료는 두 실제 비교 성공이 아니다. 검수 HEAD는 72684c76ed5d282279de5de956523ea17ffd4e40이며 근거는 run:phases/016/manager-evidence/verification.json·review.md와 두 원report다. 전체 T4와 최종 G 관문은 미수행이다.

phase 017 t4-baseline-integration은 A1/A2/A4 pass·A3 fail의 partial로 검수했다. report 형식 검사 뒤 현재2675파일과 종료 해시, 시작과016 manager 판본의 전건 일치를 확인했고 변경은 허용된 양쪽 .timings-t3.json뿐이다. 정본/미러 두 exact 시험은 각각2passed/exit0이며 정본 companion의6fixture·30snapshot·16DB·30실제child를 다시 읽어 ordinary/literal/opens/import/coverage·명시 marker와 실제 merge를 대조했다. 네 전체 T4의 각295선택·고유row·실제exit와 각60worker 게시/원DB·adapter5개 분모를 확인했다. 최종 정본 c4는294passed/1error/exit1, 미러 m4는295passed/exit0이다.015의 정확12미통과는 새 양쪽 전체에서 passed지만 c4의 Job cleanup WinError32/5 때문에 전체 기능 합격은 아니다. 원task5919파일은 검산 전후 불변이다. 근거는 run:phases/017/manager-evidence/verification.json·review.md다. G4~G6/G8과 다른 의미·문서·L01 남김은 유지한다.

phase 018 job-cleanup은 A1~A4 complete로 검수했다. report 검사 뒤 시작2675파일과017 검수본 동일, 현재와 종료 전건 일치, 허용8변경(정본fixture/지침2·미러2·비용캐시4)을 확인했다. 정확1·양쪽관련27·양쪽전체T4 각295선택/고유passed/exit0와 각875Python·각60worker 게시/원DB/adapter5개를 대조했다. 실제 close 직후 root wait258과 live cwd 잠금, 수리 뒤 suspended/resumed/자연종료3상태의 signal/빈Job/삭제 및 real/fake 오류 보존을 확인했다. 역사race 미재현·오류순간 미관측과 bootstrap WinError5 원인미확인은 유지한다. manager 첫 검산의exit1은 생성 전 미러까지 관련 정본 실행의 최종동등성을 요구한 관리 오류이며 검사한tree/최종전체 양쪽으로 구별해 exit0을 얻었다. task2463파일과017 evidence5917파일은 불변이다. 근거는 run:phases/018/manager-evidence/verification.json·review.md다. 지정 T4 완료이며 전체G 완료는 아니다.

phase 019 document-results는 A1~A4 complete로 검수했다. 시작2675파일은018 manager 판본과 같고 종료/현재 전건 해시가 일치한다. 허용30변경(정본14·미러14·비용캐시2)과 최종 양쪽 동일187선택/고유row·186passed/1skipped/exit0, 각875Python·실행 전후를 대조했다. skip은 기존 symlink 생성 권한1314이며 통과나 실제 탈출 반려 증거로 세지 않는다. 수리 전8반례의 red·초기13error·corrected23passed와 최종 정확ID 해소를 검수했다. 실제 생산/물질화·동일 바이트 다른 실행 경로 반례와 원task181파일 불변을 확인했다. 근거는 run:phases/019/manager-evidence/verification.json·review.md다. 지정 P02 완료이며 전체G 완료는 아니다.

## C3 현재 정본과 이력의 역할

이 서비스가 시작된 뒤 현재 실행 판단의 정본은 이 context.md와 plan.md다. 이전 단계-전환표 JSON/MD는 B134까지의 기준선과 상세 근거로 보존하며 현재 작업판으로 이중 갱신하지 않는다. 원문 의무·보존/P2 항목과 과거 보고는 계속 요구·증거의 진입점이다. 새로운 판정은 이 실행의 task report/evidence와 manager의 처분에 연결한다.

sources/requirements-index.json은 기존 표의 원문 식별자·요구와 위치를 추출한 찾아보기다. 새 요구나 충족 판정이 아니다. 판단이 달라지면 원래 설계·결함 범주·실제 코드·원보고로 돌아가며 최신 구현이 요구를 자동 대체하지 않는다. sources/baseline.json에는 원자료 해시, 시작 Git 상태와 기존 미추적 파일을 기록했다. 같은 과거 입력 사본을 phase마다 만들지 않는다.

## C4 새 세션과 한정된 작업

서비스는 task와 manager 모두 phase마다 새 codex exec 세션을 만든다. 이전 대화를 이어받거나 /goal을 다시 만들지 않는다. 각 objective에는 원문 구간·실제 대상·변경 가능 범위·검사·A 종료조건을 준다. 넓은 '의미 감사'나 '_context 전체 개선'을 그대로 배정하지 않는다. 한 문맥에 들어오지 않는 입력이면 구현 전 범위를 나누고 유효한 부분·정확한 후속 질문을 보고한다. 새 세션이라는 사실만으로 자동 압축이 없다고 보장하지 않는다.

task는 작업 중 발견한 무관한 개선을 따라가지 않는다. 현재 A를 만족하는 데 필요한 수리만 수행하고 다른 문제는 원래 G/의무에 연결한 finding으로 반환한다. 구현 결과는 계약상 실제 경계의 정상·반례를 검증한다. 자료를 읽는 작업도 답할 질문과 종료 산출물이 있어야 한다. 긴 파일·JSONL·보고서 전문을 도구 출력으로 쏟지 않고 필요한 원문/JSON 키를 선택한다.

task의 complete는 A 완료다. 검토 task는 결함을 발견해도 배정된 검토를 끝냈으면 complete일 수 있다. manager는 이를 제품 합격으로 바꾸지 않으며 모든 finding에 carry/resolve/reject와 근거를 남긴다. 다음 행동마다 어느 G의 어떤 남김이 줄어드는지 밝힌다.

## C5 병렬 실행과 검증 자원

phase 001~019의 task 세션은 종료됐다.020 document-tools 단일 work가 P03의 execution_window·scholarly·formal_verifier·preview·submission_contract와 record_map.read_tool을 실제 설치/최종 입력에 연결한다. 공통 doc_code·직접 소비·미러·캐시를 같은 task가 수정하므로 다른 제품 작업과 병행하지 않는다. record_map 기본 반환과 P01/P02·B130~B134를 유지하며 jobs1·전체worker3 이하·한 묶음씩을 따른다. runtime/runner/adapter/Job fixture·corpus·기존 연구와 실호출 입력은 고정하고 범위 밖 결함은 반례로 반환한다. 새 유료 공급자·예약·학술 호출은 배정하지 않는다.

do-math 시험 프로세스는 전체 합계 worker 3 이하, 동시에 한 검사 묶음만 실행한다. 검사 중 제품·시험 정본을 고정한다. 공식 도구는 python -u -B .claude/skills/do-math/scripts/run_tests.py 이며 전체 일반 검사는 기본 선택을 쓴다. 긴 실행은 자기 evidence 아래 원보고와 실제 process/session·시작·종료 상태를 남긴다. 관찰 도구의 yield/대기 만료를 시험 실패로 해석하지 않는다. 실행 중 result.json은 do_math.file_io.read_bytes_shared로 읽어 Windows rename을 방해하지 않는다.

관련 수정은 관련 검사로 확인하고, 전체 일반 검사는 결합 변경 확인이나 최종 판본 관문에 배치한다. 이미 통과한 검사를 새 변경·실패·증거 무효화 이유 없이 반복하지 않는다. 시간 예산은 소프트 기준이다. 시간만으로 실패·미실행·변이 포착을 만들지 않는다. 빠른 검사를 만들기 위해 단언·실제 경로를 약화하지 않는다.

017 F2의 실행 환경 반례를 다음 검사에 반영한다. parent TEMP/TMP/TMPDIR는 저장소 밖의 짧은 자기 전용 경로를 쓰고 git rev-parse가 상위 저장소를 찾지 않는지 확인한다. resource worker는 공식 output 아래 scratch를 다시 쓰므로 출력 경로도 짧게 정한다.017의 실제 probe cwd262자는 WinError267,241자는 정상0/반려1이었다. 이것은 이 환경의 관측이며 Windows 보편 상한이 아니다.018의 짧은 task 이름과 evidence/c4·m4를 사용하고 실제 최종 cwd를 확인한다. 긴 경로 실패를 제품 기대값 완화·skip·무조건 재시도로 처리하지 않는다.

## C6 파일 소유와 Git 마감

task는 protocol의 writes와 자기 report/evidence에만 쓰며 Git commit/reset/checkout을 하지 않는다. 다른 task의 자료와 공용 context/plan/seams도 수정하지 않는다. 필요한 제품 문서 변경과 미러 생성 범위는 objective/writes에 포함한다. 생성기를 돌리기 전에 영향 범위를 확인하고 다른 작업의 변경을 덮지 않는다. 준비 시의 dirty/untracked는 일괄 stage·삭제·정리하지 않는다.

manager는 제품 코드나 제품 정본 문서를 직접 고치지 않는다. 검수 후 Git 커밋과 그에 필수인 기억 노드/색인 작성은 관리 마감으로 맡는다. .claude/skills/commit-harness/SKILL.md와 작성 직전 기억/세칙.md를 따른다. 작업당 관련 검증·검토·미러 근거가 충분한 뒤 정확한 자기 파일과 한 layer1 노드를 같은 커밋에 담는다. test/evidence의 거대한 scratch나 무관 파일을 git add -A로 포함하지 않는다. 원보고 bytes를 유지한다. Git 및 기억 마감은 manager 단독이며 병렬 task가 index를 공유하지 않는다.

manager는 next phase와 공용 문서·기억 등을 먼저 확정하고 pending handoff 검사를 통과한 뒤 manager.json을 게시한다. 이후 내용 변경 없이 필요한 정확 파일을 커밋한다. 이 실행의 manager 세션은 게시 뒤 정확한 파일의 커밋과 그 결과 확인까지 마친 후 종료한다. 게시 뒤에는 제품·공용 계약·배정을 바꾸지 않는다. Git 행정 마감이 code 변경이나 G 축소로 변하지 않게 한다. 전체 검증 후 커밋용 기억·보고만 추가한 경우와 제품/시험 변경으로 증거가 무효화된 경우를 구별한다.

## C7 서비스의 기능과 운영 한계

정본은 repo:services/continuous-development/protocol.md다. run.py는 모든 task 종료 후 새 manager를 호출하고 next를 따른다. 자동 검사·자동 재시도·자동 재개·timeout·최대 phase 수는 없다. report/handoff 검사는 각 역할의 필수 제출 절차다. 형식 통과가 근거의 의미를 보증하지 않으므로 manager와 최종 review가 실제 파일과 주장을 대조한다. README에 남은 output/continuous-development 경로 대신 현재 services 경로를 사용한다.

첫 실행은 이 기록 디렉터리의 start.py로 검사한 뒤 기동한다. 같은 phase 재실행은 task를 다시 실행하고 로그를 덮을 수 있으므로 금지한다. 프로세스가 사라졌거나 report가 없다고 성공·timeout 원인을 추측하지 않는다. 실제 PID/종료/로그를 확인하고 새 복구 phase 또는 manager 재호출을 사람이 검토해 시작한다. 이전 report/evidence/manager.json을 고쳐 성공 보고로 만들지 않는다.

상신이 필요한 외부 결정이 있으면 finding과 context/plan에 정확한 질문·영향 G·확인한 증거를 남긴다. 독립적으로 진행할 일이 있으면 그 일을 배정한다. 모든 다음 행동이 같은 미해결 외부 조건에 막혔으면 빈 분석 phase를 계속 만들거나 next:null로 성공을 꾸미지 않는다. manager.json을 게시하지 않고 정확한 상신과 로그를 남겨 실행기를 오류로 종료시키며, 이 서비스에는 별도 paused 상태나 자동 복구가 없음을 알린다.

## C8 모델과 현재 준비의 범위

2026-10-14 사용자가 모델을 지정했다. 이후 서비스 task는 `gpt-6.1-sol` / `high`, manager는 `gpt-6-astra` / `xhigh`를 사용한다. 작문 도구의 독해 기본값도 `gpt-6.1-sol` / `high`다. 새 phase의 task에는 이 model/effort를 명시하며 임의로 다른 모델을 선택하지 않는다. start.py와 이번 교체 실행기의 공통 CLI 기본값은 task 설정이고 settings.json의 manager 설정이 이를 덮어쓴다. 서비스의 settings는 실행 시작 때 한 번 읽히므로 파일 수정만으로 기존 실행에 반영된다고 가정하지 않는다. 모델 전환 당시 phase 007 작업자(PID 33604)는 기존 `gpt-6-astra` / `max` 세션을 유지했다. 교체 실행기는 그 작업자의 exit 0을 확인한 뒤 007 manager를 새 설정으로 호출했다. 검수 때 상태는 manager_running이었으며 관찰 사본은 run:phases/007/manager-evidence/model-policy-observation.json에 있다. 원 실행기는 작업자를 종료하지 않고 교체했고 task와 로그도 재실행·덮어쓰지 않았다. 변경 근거와 실행 상태 위치는 run:sources/model-policy-2026-10-14.md다. 제품 T5 실호출에 지정하는 모델은 이 개발 담당 모델 설정과 구별한다.

준비 세션은 서비스 단위 검사(가짜 Codex 사용) 31개 중 30개 통과·권한 조건의 symlink 1개 건너뜀을 확인했다. 이것은 do-math나 실제 모델 호출 완료의 증거가 아니다. 준비 당시 실제 Codex 세션은 미기동이었다. phase 008까지의 기록에서는 phase 001 세 task와 phase 002~008 각 한 task의 report를 각각 새 manager가 검사했다. 이후 검수 상태는 C2와 아래 phase별 기록을 따른다. phase 003은 실제 공급자 경계를 실행했으나 A2/A5가 실패한 partial이며, phase 004는 그 미러 실패를 수리했으나 당시 Git clean 조건 A3가 실패한 partial이다. phase 005는 A1~A3 complete이고 004의 clean 남김을 새 근거로 닫았다. phase 006은 A1/A2/A4의 한정 성과를 승인한 partial이며 A3/A5의 직접 소비 남김은007의 새 근거로 해소됐다. phase 007은 A1~A5 complete로 검수했다. phase 008은 A1~A4를 승인한 partial이고 A5의 문서4실패는009의 A1~A3 complete로 해소했다.010 두 task는 같은 모델로 수행됐고011 regression-reading도 gpt-6.1-sol/high다.010 host의partial과reading의조사complete를 각각 검수하며 제품 전체 합격과 구별한다.011의 A1~A4 complete를 검수했고012 lean-smoke도 gpt-6.1-sol/high로 배정한다. 이전 partial report 자체는 수정하지 않는다. 개발 서비스의 세션 수행과 제품의 공급자·역할 스키마 실호출은 다른 경계이며 실제 T4/T5의 책임은 G7에 남는다.

012와013의 gpt-6.1-sol/high 작업을 검수했고014 scholarly-smoke도 같은 설정으로 배정한다. 각 세션의 모델 정책은 C8의 사용자 지정과 같으며 제품 공급자 호출 설정과 구별한다.014 제품 실호출은006의 검증된 Codex gpt-6-astra/low를 기본으로 사용하고 실제 도구 판본과 요청 설정을 기록한다.

014 scholarly-smoke의 gpt-6.1-sol/high 수행을 검수했고015 t4-adapter-report도 같은 설정으로 배정한다.014의 제품 실호출 세 번은 gpt-6-astra/low 요청이며 실제 모델명은 미보고다.015에는 새 유료 실호출을 배정하지 않는다.

015의 gpt-6.1-sol/high 수행을 검수했고016의 t4-fixture-repair와 provenance-baseline도 같은 사용자 지정 모델/effort로 배정한다. 후자는 코드 실행 없는 입력 준비이며 전자만 공식 제품 시험을 수행한다. 제품 공급자 실호출 모델을 새로 지정하지 않는다.

016 두 task의 gpt-6.1-sol/high 수행을 검수했다.017 t4-baseline-integration에도 같은 사용자 지정 모델/effort를 명시한다. 이는 개발 실행 모델이며 제품 공급자 실호출은 새로 배정하지 않는다.

017의 gpt-6.1-sol/high 작업을 검수했다.018 job-cleanup에도 같은 사용자 지정 모델/effort를 명시한다. manager 설정과 제품 공급자 실호출 모델은 그대로 구별한다.

018의 gpt-6.1-sol/high 작업을 검수했다.019 document-results도 같은 사용자 지정 모델/effort로 배정하며 manager 설정·제품 공급자 실호출과 구별한다.

019의 gpt-6.1-sol/high 수행을 검수했다.020 document-tools에도 같은 사용자 지정 model/effort를 명시한다.

## C9 요구별 상태와 과거 검토의 재사용 범위

phase 001의 requirement-state.json은 원래 19/11/61/12 항목을 각각 한 번씩 연결했고 tracking-state.json은 기존 109개 작업을 연결했다. 이들은 역사 근거와 종료 질문의 진입점이며 새로 수행한 전수 의미 감사가 아니다. 현재 판정은 이 context와 후속 report/manager의 처분을 따른다. 1-D/11-A/11-B의 검토된 성질, R17과 R07의 완료 부분, DOC-RETURN-PURE/CLI 및 B132~B134의 지정 경계는 유지하고 최종 판본 근거를 연결한다. 9-A의 R18 현재 외부 호출 전건, 1-E의 최종 반환 소유권 처분은 별도로 남는다. K-27/38/72/75와 P2 A-31/B-32는 후속 수리 이전의 낡은 remaining만으로 재수리하지 않는다.

prior-review-state.json의 phase 001 당시 실제 이전 검토는 PR23/B107~B109 완료, PR06/B22 부분 완료, 나머지 23영역 미검토다. 같은 구현을 다루는 후속 task에 해당 review_slices의 실제 diff·현재 소비자·원보고만 결합한다. 25영역 전체를 모든 수리의 선행 장벽으로 두지 않는다. phase 002는 PR01/B56의 mutation child 결과·정상 기준·공유 passed 소비 slice를 실제 bbe64043/f56a2772 diff·현재 소비·새 58개 시험으로 재검토했다. B56 원보고 네 임시 경로는 현재 없으며 과거 counts를 합산하지 않았다. 정상 증거 처리 교정과 D9·모듈 비용 순서·시간 종료 제거의 유지 판단을 승인한다. PR01의 T3 저장소·전체 runner·provenance까지 완료로 바꾸지 않는다. 근거는 run:phases/002/tasks/mutation-baseline/evidence/review-notes.md 및 run:phases/002/manager-evidence/verification.json이다.

phase 003에서 PR15/B86/B87의 공급자 녹화·native background completion slice를 검토했다. 46a67a7f/87fd1c1b 도입 diff·현재 소비자·존재하는 네 원보고를 대조했고 Codex error/turn.failed 분류, Claude task_id/tool_use_id 및 시작/완료/선택 result 순서의 현 계약을 유지한다. 기존 background 원보고는 actual_wait_tool=false와 passed=false 그대로다. 현재 계약의 nonce 파일·native completion·로컬 종료 성질만 재사용하며 maintenance schema 수락이나 연구 저장 증거로 넓히지 않는다. PR15의 다른 slice는 미검토다. 근거는 run:phases/003/tasks/provider-smoke/evidence/review-notes.md와 run:phases/003/manager-evidence/verification.json이다.

phase 004는 2fc686ac7f215222702519dfaf10e6e1ec961171의 생성기 도입 diff와 현재 transform/build_target의 바이트 경계를 대조했다. verbatim 선적용과 일반 지시문 변환은 유지하고 corpus 적용 누락만 교정한 판단을 승인했다. a0b0cc2e030b49229573aea4bf617845f27c44e5의 corpus 속성 중 manifest text 예외는 실제 clean 반례가 있어 phase 005에서 -text로 교정했다. 이 한 줄과 대응 생성 사본의 변경·전건 clean 동등성을 manager가 확인해 해당 반례의 재검토를 종결한다. 새 근거는 run:phases/005/manager-evidence/verification.json이다. 생성기 본문이나 PR15 전체를 다시 여는 근거는 없다. 이전 검토 근거는 run:phases/004/tasks/mirror-corpus/evidence/review-notes.md와 history-mirror/history-attributes 원출력, manager의 verification.json이다.

phase 006은 B49/065a323a의 전달·반려·수치·종료 slice를 실제 도입 diff와 현재 소비자에 대조했다. 두 Temp 원보고가 없다는 관찰을 유지하고 역사 161/6 counts를 새 성공으로 합산하지 않는다. 새 related-01의 5실패는 수정한 4개 fixture의 related-02와 오류 단언을 보강한 semantic-final에서 해소됐음을 원 row로 확인했다. pinned 입력·worker 반려·canonical 값 거부·종료 보호를 유지한 이 slice의 판단을 승인한다. 직접 소비 11실패와 pair 공백은 별도 미해결이며 B49의 다른 관찰 가족이나 PR15 전체를 완료로 바꾸지 않는다. 근거는 run:phases/006/tasks/codex-schema/evidence/history-b49.diff, history-review.json, review-notes.md와 run:phases/006/manager-evidence/verification.json이다.

저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다. 외부 임시 원보고 246개 위치 레코드(236개 고유 경로)는 현재 없다. 해당 slice의 판단에 필요할 때만 보존 근거를 찾고, 없으면 과거 counts와 현재 대체 재현을 구별한다. 삭제 원인을 추측하거나 사용자가 지운 작업을 복원하지 않는다. R05/R06의 현행 시험은 tests/flows/test_provider_native_storage.py의 NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository이며 과거 test_provider_close_native_storage.py 경로는 쓰지 않는다.

1-A의 원문 인용은 보존하되 repo:docs/do-math/시험-재편-2026-09-29/설계.md의3.3절·결정 A20에 따른 필수+선택 필드 역방향을 적용한다. 이 A20은 설계 결정 번호이며 task의 완료 조건 ID가 아니다. 이 역방향 검사는 수신자가 선언한 필수·선택 필드 전부가 실제 생산 표본에서 나오는지 확인한다. SHARDS·메모리 저장 대역 이름·하드 timeout 같은 폐기된 수단은 복원하지 않으며 현재 보호 성질과 사건/임대 의미를 유지한다. 구체적 근거는 run:phases/001/tasks/closure-map/evidence/requirement-state.json, prior-review-state.json, evidence-catalog.json 및 closure-decisions.md다.

010에서 Job/pythonw의23cc4df3·c71053d6·46aaa333 도입 diff, 현재 소비자와 B117/B118의 존재하는6원보고를 확인했다. 초기 Job 보류/소유자 소실/자손 종료와 pythonw의 지급 console_python·정상/권한반려·형제 실행기 부재 명시 반려를 유지한다. 공유화한3개 boundary의21개 test method AST가 HEAD와 같고 새 T5는 실제 worker/Job·자손과pythonw 출력 연쇄를 추가했다. 이 PR02/PR11 지정 slice의 유지/공유화/추가 판단만 승인한다. 없는Temp 원보고의 counts와 다른 setup/저장/예약 성질은 새 성공에 합산하지 않는다. 근거는 run:phases/010/tasks/host-smoke/evidence/review.md·history-existing-reports.json 및 manager verification.json이다.

012에서 B38/8afa57c7의 formal/setup Git 포트 slice를 실제 diff·현재 함수·원보고 selector와 대조했다. 필수 git_backend 전달, backend identity별 memo, None root·미추적 입력·.lake 제외 및 stop/오류 계약을 유지한다. 관련8개 sim과 실제 Lean 경로가 새 근거이며 원보고10개가 현재 없다는 한계를 유지한다. 이 slice의 유지 판단을 승인하지만 PR02 전체와 다른 B38 소비자까지 완료로 올리지 않는다. 근거는 run:phases/012/tasks/lean-smoke/evidence/history-b38.stdout·history-original-reports.json·review.md 및 manager 검수다.

013에서 0dd16a5e의 예약 포트 분리/real_ports 배선과 a0e6c2f4의 pythonw freeze Out-String·null/nonzero exit·빈 JSON 반려를 실제 diff·현재 소비자·양쪽33회귀로 대조했다. 이 예약 slice의 유지와 실제 OS 경계 추가 판단을 승인한다. 해당 raw 역사 report 위치를 task 입력/진행 기록에서 확인하지 못했다는 한계를 유지하며 부재의 원인이나 저장소 전체 부재를 단정하지 않는다. 다른 hunk와 PR02 전체는 미종결이다. 근거는 run:phases/013/tasks/scheduler-smoke/evidence/history-port.stdout·history-freeze.stdout·history-index.json·review.md와 manager 검수다.

014에서 d03f7d90의 scholarly closed command/args·실행별 data-dir,98ac7e5f의 files scholarly probe,b48dab8f의 worker_request/argv_inputs 정본 이동 slice를 actual diff·현 소비자·존재 원보고와 대조했다. 기존 분리와 입력/격리 계약을 유지하고 성공 완료 의미 검사를 추가한 판단을 승인한다. operator-probe.json은 서술 역사 근거로 존재하지만 그 native stdout/original_result_path는 현재 없다. 역사 counts를 새 성공에 더하지 않으며 다른 hunk·연구 운전·전체 PR은 미종결이다. 근거는 run:phases/014/tasks/scholarly-smoke/evidence/history-original-reports.json·review.md 및 manager 검수다.

015는b0d90537의 D5 자체 입출력 정지/D6 누락 worker 반려,bbe64043의 비용/공동 passed 소비와f56a2772의 시간 종료 제거를 actual diff·현재 소비 및002 근거와 대조했다. 이 한정 runner/측정 slice의 유지와 T4 보고 추가를 승인한다. 새 _read_json의 측정 전 import와 repo 내부 records.json 자기 의존은 이번 work의 실제 T3 반례로 교정됐고 양쪽70회귀에 기존 incremental/parallel 경계가 포함된다. 전체-T3-2026-10-03.json은 존재하는 역사 요약이고 연결된 raw는 부재라는 한계를 유지한다. 과거 counts를 새 성공에 더하거나 PR01 전체/provenance 검토를 닫지 않는다.015 F3의 두 baseline 비교 입력은016 provenance-baseline이 Git 도입 전후와 P10/P11에 결속해 준비하며 실제 비교는 후속 연결 작업 책임이다. 근거는015 task review.md·history-measurement.diff·history-runner.diff·history-timeout.diff 및 manager 검수다.

016은5d8db87a/bd3ae53f의 설치 fixture·포트 수축,3b37e80c의 실제 Job 관측,c4ba50b4의 writer lock,23cc4df3의 Git/자손 콘솔,407db136의 archive checker 및8afa57c7의 필수 backend slice를 현재 diff/소비와010~012의 한정 검수에 대조했다. 실제 compiler/저장/currentness/identity·잠금 반려/정상 획득·Unicode 바이트를 유지하고 현재 입력/포트/관측 fixture만 교정한 판단을 승인한다. 다른 PR/hunk나 부재 원보고 counts는 새 성공으로 올리지 않는다. provenance 도입bbe64043의 실제 첫 부모010b0597와 도입 M-0472의 동일 baseline 기록을 확인했다. B56 네 Temp 원보고는 현재 해당 경로에 없고 역사2passed15.2초는 새 비교 근거가 아니다. 이 비교의 P10/P11은 정확 시험/역사 표기이며 requirement-state103row의 ID나 문서 후속 packet P10/P11이 아니다. 원문 진입점은 설계5.3~5.5/A29·PR01/B56와 K-05/K-06이다. 이전 objective의 requirement-state P10/P11 경로 표현은 이 범위로 정정하며 원배정은 수정하지 않는다. 근거는016 두 task review.md·history-review.json·history-selection.json·requirement-trace.json과 manager 검수다. PR01 전체 종결은 아니다.

017에서016의 과거910파일 입력을 실제 소비한 두 exact 비교를 검수했다. 공식 정본/미러 각2passed와 정본 companion raw의 literal 빈 label·입력 순서·읽기·분기·명시 shared marker·양 worker merge를 대조했다. P10/P11로 지칭하던 이 한정 비교의 미실행 남김은 종료한다. 미러 원fixture raw는 별도 보존되지 않았으며 같은 시험 바이트/공식 변환과 미러 공식 실행 범위에서만 정본 raw를 재사용한다. 네 역사 Temp 원보고 부재와 PR01 다른 slice의 미검토는 유지한다. 근거는 run:phases/017/manager-evidence/verification.json 및 rechecked-raw-verification.json이다.

018에서 116cff28/0b05e8ab/23cc4df3의 실제 Job 도입/포트/시험 이행 diff와 현재 JobsContract·WindowsJob·collector,010/016의 승인 근거를 대조했다. 기존 kill-on-close와 별도 종료 관측 의미는 유지하고 shared fixture가 종료를 기다리지 않던 소비만 교정한 판단을 승인한다. PR02의 이 Job slice만 닫으며 전체PR·다른hunk·부재 원보고 counts는 확대하지 않는다. 근거는 run:phases/018/tasks/job-cleanup/evidence/review.md·history-job-origin.stdout·history-job-port.stdout·history-job-migration.stdout 및 manager 검수다.

019는 B110~B114의 P02 slice를 actual diff·현재 소비와 존재하는7원보고에 대조했다. source_ref와 stored/restored/results의 AST 조립을 실제 생산/복원 검사로 교체하고 명시 owner·line-local 별칭·저장/입력 구별은 유지한 판단을 승인한다. review_sources와 PR24의 다른 hunk는 남긴다. 역사 counts를 현재 성공에 더하지 않는다. 근거는 run:phases/019/tasks/document-results/evidence/history-verification.json·binding-review.md 및 manager 검수다.

## C10 문서 결속에서 남은 고정 범위

document-closeout의 원목록은 실제24문서(계약11 포함), inline 필드189회·lexical owner79개·노출 owner84개와 당시 AST34지점이다. 이 수는 역사 목록의 크기이며 현 의미 검증 완료율이 아니다.008에서 P01의 운영/복구6 AST지점을 실제 _context/포장 객체와 저장·물질화 파일 검사로 교체했다. operational_evidence와 recovery_materials의 동명 source를 구별하고 정상·restoration_error·checkpoint_source=null·live 부재·activity_continuations와 반환 사본/제품 입력 반례를 확인했다. 일반 재개의 result_source와 B130~B134 기존 성질을 유지하며, 마지막 소비가 없어진 checkpoint_source/recovery_source/checkpoint_files/recovered_output_files 단독 입력은 제거했다. defer 두 입력의 실제 문서 검사 담당과 오기/누락 반례도 확인했다. 근거는 run:phases/008/tasks/document-recovery/evidence/binding-review.md 및 run:phases/008/manager-evidence/review.md다.

독립-운영.md의 LIVE_INSTALLATION_ROOT 문장은008에서 현 bootstrap.main의 manifest.installation_root 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 전달하는 경계로 교정했다. 기존 bootstrap-info2개는 양쪽 최종 보고에서 통과했다. 옛 전역 이름은 제품에 복원하지 않았으며 N03의 다른 절은 미검토다.

008 F1/A5의 전건 관련 회귀 남김은009에서 해소됐다. CLI-실행-계약의 bare dotted 함수명을 provider_final.output_contract(...)로 교정해 기존 function_reference_issues의 실제 callable 검사에 연결했다. helper/schema/unknown/defer/runtime/시험 소스는 바꾸지 않았다. 정본110·미러89 선택은008과 같고 정확4실패가 모두 passed이며 현재 소스와 원보고 판본을 manager가 대조했다. P01 운영/복구와 N03-003 설치 설명의 지정 성과 및 관련 회귀를 닫고008~009 변경 단위를 마감한다. N03의 다른 절·P02~P11은 그대로 남는다. 근거는 run:phases/009/manager-evidence/verification.json·review.md다.

followup-packets.json의 P01~P11·N01~N03·L01은 유한한 후보 범위다. 15개 고정 phase를 예약한 것이 아니다. P01과009에서 종료한 지정 회귀, P02 원자료/과제 결과, P03 실행 안내/설치를 구별하고 REVIEW/TRUST·D-06·단독 이름을 실제 소비 경계별로 닫는다. instance는 명시 소비가 없는 제거 후보이며 config/profile/execution은 유지 근거가 있다. recovery_source 단독 입력은008에서 마지막 소비가 사라져 제거됐다는 위 처분을 따른다. 마지막 소비자가 없어지기 전 AST helper를 일괄 삭제하지 않는다.

L01/13-C의 읽기 한도 절은010 조사 뒤에도 미인증이다. 실제 개발 task의 Codex0.162.1 도구는 개별 명령과 합산에 별도의 token 예산을 적용한다. 비밀 없는 ASCII/Unicode 두80행fixture는400-token 출력에서 끝80행을 남기며 중간을 생략했고 명시10행씩16페이지는160행을 정확히 회수했다. 합산150-token 출력은 내부 두 결과가 온전해도 최종 수신을 잘랐다. 파일 해시·exit0·끝표지는 전문 수신의 증거가 아니며 수신은 독해/준수의 증명도 아니다. SKILL의 마지막 받은 부분 다음이라는 문구는 마지막 표시 꼬리로 읽힐 수 있었고011 A3에서14행 문단을 수리했다. 온전한 연속 접두 또는 명시 구간별 수신으로 모든 공백을 회수하고 개별·합산 절단 및 긴 행의 부분 문자를 구별한다. 기존 필수 순서·판본 재사용·내부 역할 경계는 유지됐다. 원fixture의 ASCII18~63/Unicode16~65 및 합산 누락에 새 절차를 대조해010 reading F2의 한정 문구 문제를 종결한다. 근거는 run:phases/011/tasks/regression-reading/evidence/changes.diff·reading-verification.json 및 manager 검수다. 문구 반례와 실제 운영자의 오류 발생을 구별하며 L01 인증은 아니다.

설치 Claude2.1.289의 정적 Read는 기본25,000token, 전체 파일 입력262,144bytes와 세션 fileReadingLimits override를 구별한다. PARTIAL 접두/긴 행 일부·명시offset/limit 오류와 설명2,000행 대 실제limit 미지정을 확인했다. 이것은 실제 운전 세션의 효과값이나 Read 실행이 아니다. 최신allow_large 설명도 설치 판본에 소급하지 않는다. 입력 byte guard와 shell character 제한을 출력 byte 상한으로 바꾸지 않는다. 내부10역할의 문서·전체 prompt UTF-8/stdin 전달은 운전 도구 출력과 별개이며 기존 분석은 현재 코드/문서가 같은 성질만 재사용한다.

010 reading F4/Q1~Q2의 외부 결정은 남는다. 공급자별 실제 운영 host/CLI판본·model·Read 또는 shell·개별/합산 호출 설정을 특정하고, 원문의 UTF-8 출력 byte 기준을 유지할지 실제token/character와 전 구간 수신 기준으로 개정할지 결정해야 한다. manager는 기준 변경을 자의 승인하지 않았고 사용자에게 단위 선택을 상신했다. 답변 전에는 기존byte 요구와 미충족 판정을 유지한다. 현재 개발 host를 제품operator로 자동 지정하지 않는다. 외부 결정과 독립적인011 문구 수리와012 Lean work는 완료했다.013 예약과014 학술 최소 연결도 완료했다.015 T4 측정과016의 fixture/OS 수리·과거 입력 준비를 검수했고017의 실제 비교/전체 T4 검수와018 Job cleanup 수리는 이 답변과 독립적이다. Claude 실제 Read 후속 검증은 해당 운전 프로필과 권한을 확정한 뒤 수행한다. B-20의 AI준수 한계는 유지한다. 구체적 선택지/잃는 보증은 run:phases/010/tasks/reading-limits/evidence/reading-boundaries.json·review.md, 검수는 run:phases/010/manager-evidence/verification.json·review.md다. 학술 외부 어휘는 별도 실제 응답 계약에서 확인한다. P02~P11/N01~N03의 다른 남김은 바꾸지 않았다.

019에서 P02 네 소유자의 지정 남김을 닫았다. source_ref는 실제 catalog canonical bytes/total과 input/details snapshot에, research_sources·materialized_output_files·results는 실제 _apply 저장/보존과 _context·포장의 파일/소유자/바이트에 연결됐다. 실제 수신과600k 재개가 생산·비중복을 맡고 수제fixture는 물질화만 맡는다. 필드 누락·다른 실행의 동일바이트 경로·hash/size 교란, 실제 손상 반려, 소유자별 문서검사/defer 누락을 확인했다. P01/P02 및 B130~B134의 완료 성질은 유지한다. 근거는 run:phases/019/manager-evidence/review.md와 원task binding-review.md다.

020은 P03 여섯 소유자의 실행 안내/지급 도구 설치 후 최종 입력만 맡는다. 기본 record_map의 실제 반환은 유지하고 read_tool의 AST만 실제 설치로 연결한다. scholarly.configured는 호출 성공과 구별하고 preview 지급 명령은 반환 JSON과 다른 경계다. L01 외부 결정, REVIEW/TRUST·P04~P11·N의 다른 절과 최종 관문은 유지한다. 근거는 run:phases/020/tasks/document-tools/objective.md다.

## C11 최종 관문을 막는 도구·실경계 공백

phase 001 gate-readiness F4의 정상 child 근거 부재에 의한 거짓 포착은 phase 002에서 재현·수리됐다. 현재 mutation.py는 selection/collected/rows/tests_run/load_error의 단일 결과를 생산자·수신자의 validate_result로 검사하고 PID·exit·오류를 attempt.json에 보존한다. 정상 시험 row가 실제 passed일 때만 mutant의 failure/error/unexpected success를 포착으로 인정한다. load 오류는 동일 batch의 정상 수집·실행·통과와 대조하며 오류 문자열을 시험 ID로 쓰지 않는다. 부재·파손·skip·expected failure·fixture 오류·빈 실행·미실행·비정상 exit는 execution_error로 구별한다. 정상 실패는 제외 후 다음 후보를 검사하되 baseline_failing으로 관문을 막는다. baselines와 outcomes[].attempts의 연결 및 별도 재시도 경로를 최종 G6의 근거로 사용한다. 이전 failing 문자열 결과·옛 출력 경로 설명은 현재 계약이 아니다. D9의 지연 정상 확인·동일 선택 재사용·모듈 비용 순서·timeout 없음은 유지한다. 근거는 run:phases/002/tasks/mutation-baseline/report.json과 run:phases/002/manager-evidence/review.md다. 전체 함수 모집단·fresh T3·전체 변이는 여전히 미완료다.

기존 변이17분할은 130파일이며 현재 LAYERS 1/2/3의 123모듈을 포함한다. adapter인 git_process/http_transport/powershell_scheduler/system_clock/windows_job 5개와 run_tests.py/test_categories.py는 해당 필터 밖이다. 설계 5.5/6.3 및 현재 도구 정본에 따라 이 7파일은 G6의 layer1/2/3 변이 분모에서 제외한다. adapter 5개는 T4 실제 계약·별도 분기 보고/T5로, runner·격리 표지는 관련 도구 시험과 G4/G5 선택·종료 검증으로 확인할 책임을 유지한다. 제외를 실행 성공으로 세지 않는다. 현 함수·rule·trivial·시험 진입 집합은 fresh T3 뒤 확정하고 오래된 1586함수나 17분할을 분모로 쓰지 않는다.

phase 001 당시 T5의 smoke 폴더에는 test_*.py가 없었고 runner는 빈 선택을 거부했다. phase 003이 현재 두 공급자 시험을 연결했으며 실제 결과와 남김은 C12를 따른다. probe_cli의 files/background는 작은 protocol_probe 경계라 실제 역할 schema·Job/pythonw·Lean/Mathlib·예약 등록/발화/해제·학술 list_sources의 전체 요구를 대신하지 않는다. G7 work에서 필요한 실제 연쇄와 녹화를 최종 소스 고정 전에 완결한다. 공급자 최소 smoke의 구현과 부분 실호출만으로 다른 연쇄를 대신하지 않는다. phase 001~014 당시 T4 단독은 Measurement를 만들지 않아 adapter 분기 보고가 없었다. 이 공백은015에서 실제 worker 수집/병합으로 해소됐다. 아래의 기능 실패·baseline 부재를 별도로 처리하며 최종 T3 모집단에 T4를 섞지 않는다.

phase 003은 현행 maintenance action schema 전체로 공급자 최소 smoke를 구현·실행했다. Claude 역할 응답·파일·checkpoint·종료 회수는 최종 호출에서 성공했고 Codex는 동일 schema를 거부했다. 실제 원출력과 현재 parser 재생은 보존됐다. 미러 생성의 녹화 원바이트 변형은 phase 004에서, Git manifest 속성은 phase 005에서 수리·검수했다. Codex 역할 schema 거부는 phase 006의 원 의미를 보존하는 전송/수신 수리와 새 실호출로 해소됐다. 직접 소비 fixture·pair 공백은007에서 해소됐고 그 검수와 실호출 재사용 조건은 C12에 둔다. Job/pythonw 전용 경계·Lean/Mathlib·예약·학술·L01과 G7 전체는 후속 책임이며 PR15 전체 검토로 확대하지 않는다.

phase 001 gate-readiness 당시 설치 Codex는 0.162.1, 녹화 manifest는 0.160.0이며 Claude는 양쪽 2.1.289였다. phase 003은 현재 command-surface와 새 역할 호출을 녹화했고 이전 항목도 보존했다. corpus12항목/20파일의 해시 일치는 현재 인증·모델 호출 성공을 뜻하지 않는다. Claude background의 해당 native completion·파일·종료 조건 재판정은 phase 003과 C9/C12에서 완료했다. Lean/Lake/Mathlib·pythonw·학술 서버 자료의 존재/버전은 확인됐으나 인증·지원 모델·계정 한도·컴파일·예약 권한·MCP 응답은 미확인이다. 독립적으로 가능한 수리를 진행하면서 가까운 G7 작업에서 비밀 비노출 방식으로 조건을 확인하고, 부족한 외부 조건은 정확히 상신한다. 근거는 run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json, population-and-corpus.json, environment.json, source-contracts.json 및 manager의 verification.json이다.

010의 새 host T5는 실제 real_ports/ModelRunner/worker/Job·외부CLI 자손/collector와 pythonw→PowerShell→지급 제품 읽기를 실행해 정본3/미러3건이 모두passed였다. 외부 모델CLI만 결정적 로컬프로그램이며 유료 공급자 호출이나 실예약은0건이다. 커널PID/FILETIME·Job소유·정확exit7/stderr·명시취소/held handle 종료·빈Job·정상/반려JSON과exit0/1을 원자료에서 확인했다. 기존21개 boundary 단언도 유지됐다. 첫host 표본의turn.started 누락은 표본만 교정한 최종 통과로 해소했다.

010 관련61건의59passed·1failed·1error는 역사 실패로 보존한다. F1은 _job_run의 필수clock/environment 누락으로 실제취소를 못 하고 실패dict의 tuple 인덱싱이 KeyError를 낸 시험이었다. F2는 test_doc_code 한곳·test_knowledge_currentness 세곳의 unpinned_rejection이었다.010 시작 사본의 동일두ID 재현은975비캐시파일 동등의 한계를 유지한다.011은 실제 real_ports 인자를 전달하고 owner thread 시작/판단·정확 stop tuple·한 번 수집/continuation·빈Job·추가collect0을 보강했다. 네 음성 단언은 원인별 owner/method·local_path·봉인 좌표 반려에 연결됐다. runtime/helper/규칙을 바꾸지 않고010 전체61개와 문서/복구75개를 합친 양쪽136건이 모두passed·exit0이어서010 F1/F2의 남김을 종결한다.010 A3 원보고는 fail 그대로이며 새 해소 근거는 run:phases/011/manager-evidence/verification.json·review.md다.

012에서 기존 portable Lean4.32.0/Lake5.0.0/Mathlib v4.32.0의 실제 대표 컴파일과 verifier 정상·타입 오류를 T5로 연결했다. 각 설치의9의존 HEAD와 manifest revision, 실행 파일 SHA 및 입력/신뢰 기록 불변을 확인했다. 정상 선언2개의 정확 서명·빈 공리·full32의존 증거를 원출력에서 재생했고 오류는 exit1/failed/lean rejected와 타입 진단이다. 초기 도우미 오류2건을 성공으로 소급하지 않으며 live-final의79.4초/미러84.4초만 최종 완료 근거다. 대표 컴파일의308.3초/21.2초 차이는 캐시 조건이 다른 관찰이며 코드 최적화나 시간 제한 근거가 아니다. 설치 신뢰 채택·연구 저장/평가를 수행한 것으로 확대하지 않는다. 근거는 run:phases/012/manager-evidence/verification.json·review.md 및 task 원자료다.

013에서 시험 소유의 실제 OS 예약 등록·pythonw 동결/발화·one-shot wake·취소·해제 범위를 닫았다. real_ports/PowerShellScheduler/operator_schedule.ps1·scheduled_operator.schedule·operator_bootstrap는 불변이다. 새 workspace의 HOLD가 상태 읽기/모델 호출보다 먼저 반환하는 현재 경로, 실제 action/인자·Interactive/Limited·operator PT2H/PT1H35M·engine PT0S·snapshot291파일을 대조했다. 최종 정본/미러 각33건은 새 설치/OS 실실행을 포함한다. 별도 직접 pythonw freeze/held stdout과 OS task의 실행 관측은 서로 다른 증거다.

세 성공 표본의 operator/engine/wake는 미실행267011/1999시각에서 새 LastRunTime ticks·Ready·LastTaskResult0으로 바뀌었다. wake에는 start 요청이 없고 XML의 시각 트리거와 WakeKey를 대조했다. 마지막 실제 status는 세null이고 자기 프로세스 부재·HOLD 불변·빈 repository·engine/recovery 미생성을 확인했다. 초기3error는 수정 전 helper/관찰 실패로 유지한다. live03은 확인된 소유 작업만 명시 해제했다. 서비스시각과 관찰 벽시계의 차이는 원인 미확인이며 정확 시간 지연 측정으로 사용하지 않는다. Operational 로그는 disabled이고 OS stdout은 미관측이다. task F2의 PID 미관측 표현은 정정한다. live-final await-wake 원출력에는 정확 live bootstrap/workspace의 pythonw PID9492가 있고, 최종 canonical-related/mirror-related에는 PID 관측이 없다. 이 정정은 원report 수정이나 새 OS 실행을 뜻하지 않는다. 근거는 run:phases/013/manager-evidence/verification.json·review.md와 원smoke/명령 자료다.

014에서 실제 Codex worker와 설정 서버의 list_sources 성공 완료를 검수했다. 같은 native ID/server/tool의 시작/완료·error=null과 status=ok 전체49summary를 설치 registry/Source.summary에 대조했다.49는 관측값이며 고정 모집단이 아니다. Codex의 native structured_content와 text content가 전부 같음을 원자료와 현재 관찰자로 확인했다. 초기 camelCase 조회의 부재 표시는 원report에 남기고 최종 offline 근거로 보완한다. MCP handshake/협상 protocolVersion/wire isError는 별도 미관측이며 패키지 판본을 그 증거로 대체하지 않는다. worker snapshot·argv 해시·실행별 scholarly-data·파일/checkpoint/final과 confirmed/root-signaled/빈 Job을 확인했다. list_sources는 ArtifactStore._write를 호출하지 않아 data 디렉터리 생성 부재가 정상이다. 초기 bytes 직렬화와 디렉터리 존재 단언의 실패를 유지한다. search/fetch·자료원 계정 접근·원격 종료·실제 모델명/비용까지 확대하지 않는다. 근거는 run:phases/014/manager-evidence/verification.json·review.md와 원task 자료다.

015에서 T4 보고 공백을 해소했다. AdapterMeasurement는 기존 Measurement/coverage·D5 pause를 재사용하고 현 LAYERS adapter5개를 도달0까지 소스 분모로 보고한다. worker 게시와 수신은 같은 validate_publication으로 실행 ID·요청·소스 판본·artifact SHA/branch DB를 검사하며 누락/파손은 incomplete와 exit1이다. 실제 jobs1/jobs2·누락/외부자료·거짓 도달·fail/skip/not_run, T3 합집합 분리와 기존 T3 incremental/parallel 회귀를 검수했다. 각60worker와 최종 양쪽 adapter 원합집합을 독립 재분석했다. 정본102/142와 미러101/142는 각 실제 보고와 일치하는 정보이며 같은 값이나 임계 통과를 요구하지 않는다. branch_gate._stop의 자기 활성 상태/멱등 정지와 _t3_plan의 unmeasured, 설정의 측정 전 제품 import 제거도 지정 회귀로 확인했다. 새 runner/branch_gate는 기존 T3 저장소 무효화 대상이며 최종 fresh G5를 대체할 수 없다.

015의 최종 T4는 양쪽 각각295건 중283passed·6error·4failed·2skipped다. 설치 Lean을 쓰는 formal_consumer4·lean_storage2는 installed_request가 nonempty fingerprint와 empty content를 조합해 record_errors의 모집단 검사에서 반려된다. 보존된 identity를 사용한 측정 없는 fixture 최소 재현도 같은 ValueError이며 제품 검사는 유지한다. RealJobObservation은 선언하지 않은 ok를 닫힌 object schema로 반환하고, WriterLock child는 ResearchRepository의 필수 backend를 누락해 TypeError, archive preview child는 ports/env 부재로 NameError다.016 t4-fixture-repair가 현재 공개 producer/전송/포트 계약에 fixture를 맞추고 정확 실패 ID와 관련 검사를 확인한다. 약한 기대값·구형 fallback·대역으로 실제 compiler/Job/저장 경로를 가리지 않는다.

SharedInputProvenanceTests의 두 exact-baseline 시험은 SHARED_INPUT_BASELINE_SCRIPTS가 없어 skip됐다. P10/P11의 literal entry/open/import-open/coverage 보존과 명시 marker 차이·두 worker raw union은 미검사다.016 provenance-baseline은 실제 도입 diff/원보고와 연결되는 별도 pre-fix scripts 트리를 자기 evidence에 Git 바이트로 준비한다. 현재 트리를 과거 기준으로 복제하거나 과거 요약 counts를 실행 증거로 사용하지 않는다. 수리 task와 독립인 정적 입력 준비이며 두 비교의 공식 실행과 전체 T4는 두 결과 검수 뒤 후속 연결 작업에 배정한다.

OS 관측도 미해결로 유지한다. 첫 정본 전건의 bootstrap freeze staging.rename WinError5는 최종 양쪽 동일 ID에서 통과했으나 원인이나 transient 여부는 미확인이다. real_git_descendants는 첫 정본에서 통과하고 최종 정본·미러에서는 store.publish/update-ref가 stdin handle을 DuplicateHandle하는 중 WinError6으로 실패했다. 현재 probe는 같은 pythonw에서 AttachConsole/FreeConsole 뒤 저장을 수행한다는 코드 사실을 확인했으나 인과는 아직 가설이다.016 t4-fixture-repair가 정확 ID·child/OS handle 조건·정상 대조로 판별하며 제품 수리가 쓰기 범위를 넘으면 최소 반례를 반환한다. 이전 failed/error를 소급 pass로 바꾸지 않는다. 근거는015 manager verification.json·review.md 및 task 원report다.13-C/L01·다른 문서/의미 질문과 G4~G6/G8 최종 관문은 남는다.

016에서015의 정확9fixture와 WinError6 남김을 새 근거로 해소했다. installed_request는 현재 trust_inventory producer의 실제 지문/content11094파일 모집단·원바이트를 사용하며 clean-build validation/연구 채택 권한은 여전히 합성이다. 설치 공유 신뢰 기록을 승인/수정하지 않는다. 실제 compiler/저장/authoritative 소비의 범위는 원시험대로 유지한다. observation은 ok의 의미 schema와 Codex 문자열 전송을 같이 맞췄고, lock/archive child는 자기 real_ports를 전달한다. 양쪽21+35는 전건passed이며 이전10실패와 정확 대응한다.

WinError6은 일반 child에서는 재현되지 않았고 실제 Job의 control은 null stdin/exit0, 원 AttachConsole/FreeConsole 관측은 invalid nonnull stdin/exit1·DuplicateHandle 실패였다. 시험의 콘솔 관측만 별도 pythonw child로 분리해 저장 stdin을 보존하고 실제 Git/자손·hidden console 양성 대조·visible=[]·binary readback을 유지했다. 별도 수리 관측의 실제 exit0/root_signaled/빈Job도 검수했다. 제품 Git runtime은 불변이다. bootstrap-info2는 현재 양쪽passed이나015 첫 WinError5의 원인은 미확인이다.017 전체 T4에서 재현되면 정확 trace/OS 조건으로 처리하며 무조건 retry/skip을 하지 않는다. 초기 진단의 없는 Job API/개행 계획/count-row 혼동 오류는 원exit1과 함께 보존하고 제품 실패와 구별한다.

017에서 provenance의 두 exact 비교를 완료했다.016 baseline-manifest의 과거910파일은 전후 불변이고 현재 원바이트 SHA/Git blob과 일치한다. SHARED_INPUT_BASELINE_SCRIPTS가 실제30child에 전달됐고 old/current scripts 선택을 확인했다. 양쪽 공식 각2passed·skip0·exit0이며 정본의 현재 TestCase/WORKER/SNAPSHOT을 사용한6fixture의30snapshot·16DB와 실제 두 판본 merge를 검산했다. ordinary 결과/읽기·모든 literal label/pair(빈 label 포함)·opens/import·파일/context/line/arc 및 명시 marker 차이를 현재 단언과 대조했다. 정본 raw의 미러 재사용은 동일 시험 바이트·공식 변환과 별도 미러 공식 실행에 한정하며 미러 fixture raw를 보존했다고 주장하지 않는다.

017 전체 T4의 첫 내부 긴 TEMP 실행은289passed/4failed/2error/exit1이다. Git 없는 fixture가 상위 C:\math를 찾는4실패와 SHA256 rev-list의 Filename too long2오류를 원trace/현재 입력에 대조했다. 같은 제품의 외부 짧은 TEMP 전체는294passed/1error로 Git6건이 통과했고 설치 probe cwd262자의 WinError267이 남았다. 기존 TestCase의 직접 긴/짧은 경로 대조는262자에서267,241자에서 정상0·반려1을 보였다. parent TEMP와 resource worker output을 함께 짧게 지정한 최종 c4/m4에서 이7ID는 모두 passed다. 두 초기 전체 실패를 소급 성공으로 바꾸거나 제품 수리로 기록하지 않는다. bootstrap2도 현재 passed지만 과거 WinError5 원인은 미확인이다.

최종 c4는295선택 중294passed·1error·exit1, m4는295passed·exit0이다. 정확 오류 ID는 boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once이며 재resume 반려 검사 뒤 TemporaryDirectory cleanup의 WinError32/5다. JobsContract.launch는 job.close를 디렉터리 정리 전에 등록하지만 종료를 기다리지 않는다. 현 WindowsJob.close는 핸들 닫기/kill-on-close 계약이며 root wait·빈Job 확인은 별도다. 종료와 cwd 해제의 경쟁은 가설이고 오류 순간 프로세스/핸들 소유는 미관측이다. 같은ID의 앞선 두 정본/미러 통과를 이 오류의 해소로 세지 않는다.018은 이 한정 cleanup 소비를 검증·수리하고 real/fake 계약과 실제 root/빈Job/cwd 해제를 확인한 뒤 양쪽 전체 T4를 새로 완결한다. runtime 계약 변경이 필요하면 후속 배정으로 반환한다.

네 전체 실행은 각각60worker의 실제 요청/소스875개·게시 artifact SHA·branch DB와 부모 합집합을 검산했고 adapter5개 측정complete다. 최종 c4/m4 도달은 각102/142이며 정보 보고다.015의 정확10실패/오류·2skip은 새 양쪽 전체에서 passed로 연결돼 그 남김을 닫는다. 측정 완전성·미러 성공과 정본 기능 오류는 구별한다. 근거는 run:phases/017/manager-evidence/verification.json·review.md와 원task 자료다. L01·다른 의미/문서 질문 및 G4~G6/G8은 유지한다.

018에서017의 정확 cleanup 남김을 종결했다. 시험이 소유한 Job을 terminate·root wait·termination_confirmed로 확인한 뒤 finally에서 close하고 디렉터리를 정리한다. 현재 runtime API는 불변이다. 실제3상태와 오류2경로, exact1·양쪽관련27 및 새 양쪽전체T4 각295passed/exit0를 검수했다. 각60worker 측정complete·원branch DB/게시·부모합집합·adapter5개 정보102/142도 대조했다.015의12미통과와017환경7ID/cleanup1은 새 전체passed에 대응한다. 역사 실패·race 원인미확인·bootstrap WinError5 미확인과017 raw의 미러재사용 한계는 유지한다.229자cwd는 계산값이며241자 과거실측과 구별한다. 이번 전체T4를 G4 기본전체/G5 freshT3/G6 전수변이/G8 최종review로 대체하지 않는다. 근거는 run:phases/018/manager-evidence/verification.json·review.md다.

019의 관련 양쪽187건에는 기존 ContextStoreTests.test_outside_symlink_is_reported_when_supported가 Windows1314로 각1skip됐다. P02 지정 성질은 실행됐으나 실제 symlink 탈출 반려는 이번 환경에서 미검사다. G4 최종 기본전체에서 권한조건 skip의 원문상 정당성을 별도 판정하며 통과로 세지 않는다. 권한이나 완료 기준은 변경하지 않았다. 근거는019 manager verification.json과 최종 c/m 원report다.

## C12 공급자 부분 성공과 원바이트 인도

phase 003이 추가한 T5 선택은 Codex/Claude maintenance 각 한 건이다. 003 당시 실 ModelRunner·real_ports·worker·adapter·parser를 사용했고 세 worker schema가 당시 action_schema 전체와 같았다. 새 호출은 Codex 1회·Claude 2회다. live-01은 2선택/2실패이며 Claude는 읽기 도구 출력에 checkpoint가 섞여 정확 비교가 실패했다. prompt를 명확히 한 live-02의 Claude 1선택은 모든 9개 판정과 공식 row가 통과했다. 003의 마지막 live와 종료 사이에는 호출 경로가 불변이고 오프라인 corpus 검사 세 파일만 바뀌었다. 003 검수 시 최종 정본 23개 및 미러 4개의 Python 864개 해시는 당시 종료 판본과 일치했다. 006 이후 판본은 아래의 새 근거를 따른다. 근거는 run:phases/003/manager-evidence/verification.json 및 task의 live-01/live-02/offline-01/mirror-replay 원보고다.

phase 003 F1은 실제 제품 전달 실패였다. Codex 0.162.1/gpt-6-astra/low는 보통 maintenance schema의 선택 필드 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema를 반환했다. worker exit 1, parse_complete=true, turn_failed=true, final/파일/checkpoint 부재와 로컬 종료 barrier는 역사 실패 그대로 보존한다. 인증 부재나 timeout 또는 연구 control_binding 실패로 해석하지 않는다. phase 006의 새 전달 표현과 대표 실호출은 아래의 범위에서 이 거부를 해소했다. 원 schema의 선택 필드 부재/null/값과 제약은 그대로다.

phase 003 F2의 미러 치환 위반은 phase 004에서 해결됐다. 당시 정본과 미러는 각각 17항목·44파일·200872바이트이고 정본 raw·manifest·역사 verdict는 불변이다. 기존/신규 두 Claude help는 원 SHA a58ca228…로 복구됐으며 각 트리의 41개 명시 SHA 참조가 모두 맞는다. 기존 _rules.json의 verbatim에 corpus 전체 경계 하나를 추가했고 경계 밖 지시문의 치환은 유지한다. 수리 전 공식 4선택/2통과/2실패는 역사 실패로 보존하며 양쪽 관련 14선택/14통과가 새 근거다. 생성기 전체 22개와 최종 --check/skill-only도 통과했다. 생성 규칙 일치·재생·Git 바이트 보존은 별개이며 당시 Git 남김 때문에 A3는 미충족이었다. phase 005의 새 해소 근거는 아래에 두며 G7/G8 전체는 여전히 미완료다. 근거는 run:phases/004/tasks/mirror-corpus/report.json과 run:phases/004/manager-evidence/verification.json이다.

phase 004 F1과 A3에 남았던 두 manifest의 Git clean 변환은 phase 005에서 해소됐다. 실제 하위 정본 corpus/.gitattributes의 `manifest.json text eol=lf whitespace`를 `manifest.json -text whitespace`로 바꾸고 공식 생성기로 대응 사본에 반영했다. 이전 manager 배정에 이 하위 위치가 빠져 상위 규칙으로 해결하지 못했던 경위는 004 report와 manager 기록에 보존한다. task가 무효한 상위 변경을 복원하고 partial로 반환한 판단은 유지한다. 양쪽 88개 경로의 raw/clean은 전건 같고 두 manifest는 원 raw db61141d…와 같은 clean 값을 갖는다. text가 unset인 상태에서 상속 eol=lf 표시는 남지만 실제 바이트는 보존된다. 005 검수 당시 각 트리는 17항목·44파일·200866바이트, 41개 명시 SHA 참조다. 두 속성 외 86개 파일·manifest 항목·역사 verdict는 불변이다. 기존 재생 각 14개·생성기 22개 성공과 최종 --check/skill-only 근거를 함께 검수했다. 이것은 작업트리와 실제 clean 결과이며 staged blob이나 최종 제품 커밋의 증거로 확대하지 않는다. 새 근거는 run:phases/005/tasks/corpus-git-bytes/report.json, run:phases/005/manager-evidence/verification.json 및 git-clean-observation.json이다. 수리 전 반례는 run:phases/004/tasks/mirror-corpus/evidence/attribute-probe.json, proposed-corpus-attributes.diff와 run:phases/004/manager-evidence/git-clean-observation.json에 보존한다.

phase 004 F2는 이전 세 파일 clean 관찰의 한계를 구체화했다. Git 2.50.0.windows.2에서 Lean/scheduler는 역슬래시 절대 경로일 때만 변환되고 슬래시 상대·절대 경로에서는 보존된다. manifest는 세 표기 모두 변환된다. manager가 같은 argv의 9개 관찰을 재확인했다. phase 003 기록에는 정확한 argv가 없으므로 당시 표기를 단정하지 않으며 원 관찰은 그대로 보존한다. 현재 정본 인도 판정은 cwd와 슬래시 경로의 실제 argv를 남기는 검사에 따른다. Lean/scheduler 녹화를 다시 쓸 근거는 없다. 근거는 run:phases/004/manager-evidence/path-spelling-observation.json이다.

phase 003 F3의 한정 재사용을 승인했다. 보존된 Claude background 원자료 9파일의 해시, 같은 task/tool ID와 시작<완료<result 순서, nonce 파일과 종료 barrier 및 현재 직접 코드 판본을 manager가 대조했다. 과거 passed=false를 유지하며 native completion·파일·로컬 종료 성질만 사용한다. 관련 B86/B87 판정은 C9에 있다. 별도 background 유료 호출은 필요하지 않다. 새 Claude 두 호출의 reported list cost 합계 약 USD 0.4631016은 실제 청구액이 아니며 Codex 거부 비용은 미보고다.

phase 006은 provider_final.output_contract/semantic_output에 Codex 문자열 봉투를 정의했다. ModelRunner는 원 prompt와 output.schema.json을 보존하고 transport.schema.json을 CLI에 전달한다. collector의 source_request·worker hash·native final 일치·종료 검사 뒤 classify_run이 봉투를 엄격히 해석해 canonical 값과 원 schema를 검증한다. 선택 필드 삭제/필수화, null/default 보충, 구형 fallback은 없다. Claude의 직접 JSON 및 control_binding의 중앙 제출 분기는 유지한다. 실제 코드와 의미 회귀를 검수했으며 이 제품 정의를 중복 schema로 다시 만들지 않는다.

006의 Codex 0.162.1 새 호출은 요청 model=gpt-6-astra/effort=low를 명시했고 1선택/1passed/exit0이며 11개 판정이 전부 참이다. 원/전송 schema·prompt·worker snapshot/hash·native final·파일·checkpoint와 종료의 대응을 확인했다. live 이후 runtime124파일과 smoke helper는 불변이며 이후 Python 변경은 corpus 검사3모듈뿐이다. 실제 모델명·비용·내부 요청 수는 미보고다. 새 성공 녹화는 codex-maintenance-transport-20261014이며 기존17항목과 실패 verdict는 유지한다. 현재 각 corpus는18항목·51파일·223685바이트·50명시SHA이고 manager도 전102경로 raw/clean을 검산했다. 정본18개·미러14개 corpus 회귀와 --check1305파일/skill-only 성공은 이 범위에서 승인한다. 근거는 run:phases/006/manager-evidence/verification.json 및 git-clean-observation.json이다.

006 F2/F3와 A3/A5의 직접 소비 남김은007의 새 근거로 해소했다. consumers45건의11실패를 최종98개 묶음의 정확한 passed ID에 연결했다. pair는 실제 runner/worker/collector로 두 공급자의 성공·결박·불완전·정지8표본을 만들고 status/output/collection/error_kind/정확 오류·원자료 해시·종료를 검사한다. 수리 전 새 단언의 두 성공 subTest 실패와 수리 후 성공은 원보고로 보존한다. 단일 chunk의20관찰/한callback과 설치 복구 두 사례도 최종 묶음에서 통과했다. raw ingress의 첫97통과/1실패는 정상 후속 행 위치가 별도 final mismatch를 만들던 fixture 오류였다. 같은 stream의 정상 대조군을 completed로 확인하고 malformed만 주입하는42사례에서 공급자별 정확 collector 반려와 저장/재전달 무효과를 확인했다. 이를 제품 parser 수리나 실패 기대값 완화로 읽지 않는다. 근거는 run:phases/007/tasks/provider-consumers/report.json 및 manager-evidence/verification.json과 review.md다.

006 F4의 Claude 재사용은 한정 승인한다. 원 smoke를 현 parser/collector/분류기로 재수신한 completed·정확 output, 같은 prompt/schema·worker/tool12모듈 및 경로·버전/help 근거를 확인했다. 당시 CLI 바이너리 SHA는 미기록이므로 실행 파일 바이트 동등성을 주장하지 않는다. 새 Claude/background 호출은 없다. 기존 background의 승인된 성질과 역사 passed=false도 그대로다. 이후 입력/실행 경로/도구 조건이 바뀌면 영향을 받는 실호출을 별도로 판단한다. 이번 Codex 성공은 유지된 실행 경로에 한해 후속 시험 수정 뒤에도 재사용할 수 있다. 근거는 run:phases/006/tasks/codex-schema/evidence/claude-reuse.json과 manager 검수다.

007 검수로 공급자 단위의 관련 회귀가 완료돼003~007의 검수된 제품·시험·문서·미러124파일을 하나의 커밋 단위로 마감한다. 비용 캐시는 실행 부산물로 Git 대상에서 제외한다. 이전 archive는 각 당시 판본의 원바이트 근거로 유지하며 자동 복원 지시가 아니다. staged corpus102경로와 선별 원보고의 바이트를 Git blob으로 확인한 후 커밋한다. 관리 기록·008 배정·기억도 같은 인계에 포함한다. 운영자 모델 전환의 작문 도구·settings/start/README 변경은 제품 단위에 섞지 않으며 C8과 정책 원문은 현재 공용 맥락으로 보존한다. 실제 commit/stage 수신 기록과 정확 경로는 run:phases/007/manager-evidence/preservation.json 및 로컬 commit.json에 남긴다. 다른 G1~G8 의무, 문서/의미 질문, Job/pythonw·Lean/Mathlib·예약·학술·L01 및 최종 관문은 유지한다.

008 F2의 보존 사실은 manager가 확인해 종결했다.008의 문서·시험 변경은 공급자 runtime124·smoke입력3·corpus102경로를 바꾸지 않았으므로 기존 실호출의 승인된 성질은 유지한다.007의 제품124파일 마감은 로컬 commit.json의 exit0 및 HEAD78d9c6d에서 확인했다.008 제품30경로(비용 캐시2 포함)는 문서4실패가 남아009 검증 뒤 커밋하며 현재 raw 바이트는008 manager-evidence의 archive로 보존한다. 이번 커밋은 관리 기록·선별 원근거·009 배정·기억만 포함한다. 원바이트/추적 범위는 run:phases/008/manager-evidence/preservation.json에 둔다. G4~G6/G8의 새 최종 판본 검증과 나머지 G7 책임은 유지한다.

009 F2의 보존 사실을 검수했다. 현재 runtime124·smoke입력3·양쪽 corpus102경로와 속성/생성 규칙은008과 같아 기존 실호출 및 명시SHA/Git clean의 한정 근거를 유지한다. --check1305파일·skill-only verified의 원출력과 판본도 확인했다.008~009의 승인된 제품·시험·문서·미러28경로를 이번 관리 마감에 포함하고 비용 캐시2개는 제외한다. 원근거의 raw archive와 Git staged blob은 별도로 대조한다. 정확 경로·해시·추적/로컬 보존 구분은 run:phases/009/manager-evidence/preservation.json, 행정 수신은 로컬 commit.json에 둔다. 제품 바이트를 고치지 않은 관리 커밋은 기존 검증을 무효화하지 않는다. G4~G6/G8 최종 관문, 나머지 문서/의미 질문과 G7 실연쇄는010 및 후속 계획으로 유지한다.

010 검수에서 runtime124·기존 공급자smoke입력3·양쪽corpus102경로가 시작과 같고102경로의Git raw/clean 동등성을 재확인했다. 기존 공급자 실호출의 승인된 성질과 역사실패는 유지한다. --check1307파일·skill-only verified와 실제판본을 대조했다.010의제품14변경(비용캐시2포함)은011 회귀수리·검수 뒤 마감하며 이번에는 제품을stage하지 않는다. 현재 제품원바이트와원OS/읽기근거는 manager-evidence/raw-evidence.zip 및 preservation.json에 결정화한다. 압축파일은자동복원지시가 아니다. 관리기록·선별원보고·011배정·기억만 커밋하며 원task report는 수정하지 않는다. 큰baseline사본과일부중복소스스냅샷의원경로는로컬보관이며 정리로 사라질 수 있다. 정확추적/보존범위는 run:phases/010/manager-evidence/preservation.json에 둔다.

011 F3의 불변 근거를 검수해010 host의 정본3·미러3 성질과 기존 공급자 실호출을 한정 재사용한다. host8원자료의 SHA/판정, Python/pythonw SHA·판본과 PowerShell 당시 경로/판본의 한계를 유지하며 새 OS T5/유료호출은 없다. 현재 corpus102경로의 Git raw/clean을 재확인했고 manifest/녹화·속성·생성규칙은 불변이다.010~011의 검수된 제품·시험·문서·미러20경로를 같은 관리 커밋으로 마감하고 비용캐시2개는 제외한다. 원task report/evidence는 수정하지 않는다.011 원자료 전부와 현재 제품 원바이트는 raw-evidence.zip으로도 보존한다. 추적하는 선별 원경로와 압축 항목·SHA는 run:phases/011/manager-evidence/preservation.json에, 커밋 행정 수신은 로컬 commit.json에 둔다. 원경로 중 압축으로만 추적되는 scratch/중복 snapshot 및 행정 수신은 로컬 정리로 사라질 수 있다.012의 새 Lean 자료는 기존 공급자/host 성과를 재인증하는 작업이 아니며 G4~G6/G8과 나머지G7 책임을 유지한다.

012 F3의 불변 근거를 검수했다. runtime124·공급자 입력3·host 입력과8원자료의 바이트는 같고 기존 corpus18항목/verdict·100비manifest 경로도 유지됐다. 새 full Lean 녹화와 재생만 추가해 현재 corpus는 각19항목·56파일·320687바이트다. 총112경로의 명시 SHA·Git raw/clean·양쪽 바이트와 공식 --check1314파일을 확인했다. 이전 실호출은 기존 승인 성질과 도구 조건 안에서만 재사용하며 이번에 새 host/공급자 호출은 없다.012의 검수된 제품·시험·지침·미러20경로를 이번 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원 task report/evidence와 제품 원바이트는 raw-evidence.zip에 보존하며 선별 원경로와 압축 항목·SHA는 run:phases/012/manager-evidence/preservation.json에 둔다. 압축으로만 추적되는 scratch/중복 snapshot의 원경로와 stage/commit 수신은 로컬 보관으로 정리 시 사라질 수 있다. 압축은 자동 복원 지시가 아니다.013 배정과 공용 문서·기억의 행정 추가는 제품 검증 판본을 바꾸지 않는다.

013 F4의 불변 근거를 검수했다. runtime124·공급자3·host4·Lean4 입력과 host8원자료, 도구 조건은 유지됐고 기존19corpus 항목/verdict·110비manifest경로도 보존됐다. 새 scheduler 원녹화 두 항목과 현 parser 재생을 확인해 현재 각21항목·62파일·344100바이트, 총124경로의 명시 SHA·Git raw/clean·양쪽 바이트가 일치한다. --check1322와 skill-only를 확인했다. 새 정본/미러 관련33건을 과거 성공과 합산해 전체 관문으로 읽지 않는다. 검수된 제품·시험·지침·미러20경로를 이번 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원 task 자료와 제품 원바이트는 raw-evidence.zip에 보존한다. 선별 원경로·압축 항목·SHA와 로컬 보관 범위는 run:phases/013/manager-evidence/preservation.json, 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch/중복 snapshot의 원경로는 정리 시 사라질 수 있으며 자동 복원 지시가 아니다.014 배정과 공용 문서·기억의 행정 추가는 제품 판본을 바꾸지 않는다.

014 F2/F4의 원자료 보존과 한정 재사용을 검수했다. runtime124를 포함한139입력·host8원자료·도구 SHA, 기존21corpus 항목/verdict와122비manifest 경로가 유지됐다. 성공 녹화1항목·10원파일을 추가했고 현재 각22항목72파일409886바이트·75명시SHA 및144경로 Git raw/clean·미러 바이트가 일치한다. 공식 --check1334파일과 양쪽46회귀가 통과했다.129공식 변환 입력과 미러 offline은 정본 실호출의 한정 재사용이며 새 미러 유료호출0이다. 초기 두 공식 실패와 structured-content 오관측은 소급 수정하지 않는다. 이번 검수 제품·시험·지침·미러32경로를 관리 커밋으로 마감하고 비용 캐시2개는 제외한다. 원task 자료와32제품 원바이트는 raw-evidence.zip에 보존한다. 선별 추적 경로·압축 항목·SHA는 run:phases/014/manager-evidence/preservation.json에, stage/commit 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch 원경로와 행정 수신은 로컬 정리로 사라질 수 있으며 압축은 자동 복원 지시가 아니다.015 배정·공용 문서·기억 추가는 검증한 제품 바이트를 바꾸지 않는다.

015 F5의 보존 사실을 검수했다. runtime 포함139입력·corpus144경로·host8원자료·도구 SHA와 index/pseudo 목록은 불변이며 전144경로 Git raw/clean을 확인했다. 공식 --check1336과 skill-only 및 양쪽70회귀를 승인된 성질로 유지한다.015의12개 제품/시험/지침/미러 경로(16변경 중 비용캐시4 제외)는 전체 T4 실패/skip 해소와 연결 검수 뒤 커밋하도록 대기한다. 이번 관리 커밋에는 공용 인계·선별 원근거·기억만 담고 현재12제품 원바이트와 task 원자료를 raw-evidence.zip에 보존한다. 추적 범위/항목 SHA는 run:phases/015/manager-evidence/preservation.json에, stage/commit 행정 수신은 로컬 commit.json에 둔다. 압축으로만 추적되는 scratch 원경로와 행정 수신은 정리로 사라질 수 있으며 압축은 자동 복원 지시가 아니다.016 배정은 기존 성공을 전체 G 합격으로 바꾸지 않는다.

016 F3의 보존 사실을 검수했다.015의12제품 경로, runtime 포함139실호출 입력·144corpus 경로·8host 원자료·도구SHA·index/pseudo/T3-store는 불변이다. 전144경로 Git raw/clean과 공식 --check1336/skill-only 및 관련 양쪽56passed를 확인했다. 기존 실호출은 불변 경로/도구의 승인된 성질만 재사용하며 새 유료/예약 호출은 없다.01512경로와01610비캐시 제품경로, 합22경로의 커밋은017 전체 T4 연결 검수 뒤 판단한다. 이번 관리 마감은 공용 인계·두 원보고/선별 근거·017 배정·기억만 포함한다. 두 task 원자료(과거910파일 포함)와22제품 원바이트는 raw-evidence.zip으로 보존하고 전건 SHA/선별 추적 경로는 run:phases/016/manager-evidence/preservation.json에 둔다. 원경로 중 압축으로만 추적하는 scratch/중복 snapshot과 stage/commit 행정 수신은 로컬 보관이며 정리로 사라질 수 있다. 압축은 자동 복원 지시가 아니다.017 배정·관리 기록은 제품 검증 판본이나 G 완료 조건을 바꾸지 않는다.

017 F3의 보존 사실을 검수했다. runtime 포함139입력·corpus144경로/150명시SHA·host8원자료/도구·과거910파일·index/pseudo/T3-store와01512/01610 비캐시 제품22경로는 불변이다. 전144경로 Git raw/clean, 공식 --check1336과 skill-only 원출력을 대조했다. 기존 승인된 실호출 성질을 같은 입력/도구 조건에서 한정 재사용한다. 제품22경로의 커밋은 c4 Job cleanup 오류의018 수리/전체 연결 검수까지 보류한다. 이번 관리 마감은 공용 인계·선별 원근거·018 배정·기억만 포함하며 원task 자료와22제품 바이트를 raw-evidence.zip으로 보존한다. 전건SHA·선별 추적 경로는 run:phases/017/manager-evidence/preservation.json에 둔다. 압축으로만 추적되는 scratch/중복snapshot의 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있고 압축은 자동 복원 지시가 아니다.

018 F3의 보존과 한정 재사용을 검수했다. runtime139입력·corpus144경로/150명시SHA·host8원자료/도구·baseline910·index/pseudo/T3-store는 불변이다. 기존22제품 중 허용된 지침2에 단락을 추가했고 나머지20은 불변이며,017 companion 정의/원자료도 보존됐다. --check1336/skill-only와 실제 양쪽전체T4 성공을 확인해015~016제품22 및018fixture2, 합24비캐시 제품경로를 이번 관리 커밋으로 마감한다. 기존 실호출의 승인 성질만 재사용하며 새 호출은 없다. 원task 자료와24제품 바이트의 압축/전건SHA·선별 추적 경로는 run:phases/018/manager-evidence/preservation.json에 둔다. 압축만 추적하는 scratch/중복snapshot의 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 자동 복원 지시가 아니다.019 배정/관리·기억 추가는 검증한 제품 바이트를 바꾸지 않는다.

019 F3의 보존과 한정 재사용을 검수했다. runtime/실호출139입력·corpus144경로/150명시SHA·host8원자료/도구5·baseline910·T4 고정 경계는 불변이다. 문서두문장은 향후 일반 역할 prompt판본을 바꾸므로 역사 고정 smoke를 새 문서 읽기/준수의 실측으로 확대하지 않는다. 검수된 제품·시험·문서·미러28경로를 이번 관리 커밋으로 마감하고 비용캐시2는 제외한다. 원task181파일과 제품원바이트는 manager-evidence/raw-evidence.zip에 보존하며 전건SHA·선별 추적범위는 run:phases/019/manager-evidence/preservation.json에 둔다. 압축만 추적하는 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 자동 복원 지시가 아니다.020 배정·관리·기억 추가는 제품 검증 판본을 바꾸지 않는다.


# 파일: docs/do-math/continuous-development-2026-10-13/plan.md

# 전체 완료로 이어지는 현재 계획

이 파일은 현재 남김과 다음 판단을 관리한다. 상세한 과거 이력은 sources와 기존 repo 자료에 연결하고 여기에 반복 복사하지 않는다. 상태·근거·구체적 다음 질문 없이 '추가 감사 필요'만 적지 않는다.

## phase 001~019의 결과와 현재 상태

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

## 다음 phase: 020

gpt-6.1-sol/high의 document-tools 단일 work를 배정한다. P03의 execution_window·scholarly·formal_verifier·preview·submission_contract와 record_map.read_tool을 실제 _context·install_tools·prepare_role_input 결과와 설치 파일에 연결한다. 기본 record_map 실제 반환과 P01/P02·B130~B134를 유지하고 필드 누락/다른 명령 차용·조건부 미설치·console sibling 반려를 기존 준비/설치 시험에서 검증한다.

doc_code와 직접 소비/helper·문서·미러·캐시를 한 task가 소유한다. 공유 상태를 수정하는 제품 작업을 병행하지 않으며 jobs1·한 묶음씩 실행한다. runtime·runner·adapter·Job fixture·corpus·실호출 입력은 고정한다. 같은 최종 관련 선택을 양쪽에서 완결하고 공식 생성/check/skill-only를 확인한다. 새 실호출이나 전체T4 반복은 배정하지 않는다.

018의 제품24경로는 HEAD929fa4cc의 관리 커밋으로 마감됐다. 이번에는019의28비캐시 제품경로를 커밋한다. L01 Q1/Q2는 미정이며 원문byte 기준과 미충족을 유지한다. P04~P11·REVIEW/TRUST·N의 다른 절·남은 의미 질문, 전체일반/freshT3/전수변이·최종review는 별도 후속 책임이다.

## 가까운 후속 배정과 선행 관계

007 공급자 변경과008~009 문서·시험28경로는009관리마감까지커밋됐다.010의 host/읽기 조사를 검수했고011에서 두 회귀 문제와 문구 반례를 수리·검수했다.010~011 제품20경로는011 관리 커밋571d282c로 마감됐다.012 Lean/Mathlib 제품20경로는 a8fb1e41로 마감됐다.013 예약 제품20경로는 8d0ade6c으로 마감됐다.014 학술 제품32경로는 eb701074로 마감됐다.015 T4 측정과016 fixture/OS 수리를 검수했다.016의Gitbaseline910파일과 새 양쪽56회귀를 승인하되 정확baseline 비교는017에서 통과했고 전체T4의 정본 Job cleanup 오류는018의 fixture수리와 양쪽295passed로 종결됐다.01512·01610·018fixture2의 합24비캐시 제품경로는018 관리커밋a29f3c6a로 마감됐다. 근거는016~018 manager-evidence/verification.json·review.md다. 그 밖의 구체적 남김은 아래와 같다. 먼저 해야 할 수리가 늘어나면 원래 G와 반례를 붙여 반환하고, 확인된 부분은 다시 탐색하지 않는다.

| 남김 | 다음 담당 작업과 끝나는 조건 | 선행/한계 |
|---|---|---|
| G1/G2/G3 공급자 단위의 최종 판본 연결 | 007에서 관련 회귀를 종료했다. 이후 변경이 그 경계에 영향을 주면 필요한 근거만 교체하고 G4~G7 최종 관문에 연결한다. | 006 Codex 대표 호출·003 Claude 한정 재사용과 역사 실패를 유지한다. 중간 회귀 합산은 전체 성공이 아니다. |
| G7 Job/pythonw 관련 회귀 |010 host정본3·미러3을 한정 재사용하고011의 실제 취소·네 음성 단언 및 양쪽136건 통과로 관련 남김을 닫았다. |010 실패 원보고는 보존한다. 이후 입력/경로 변경 시 재사용을 재판정한다. |
| G1/G3 읽기 문구와 L01 |011A3의 연속 접두/누락 구간/개별·합산 절단 문구 수리는 종료됐다. Q1/Q2의 운전 프로필·단위 결정 뒤 실제 읽기/한도 검증을 배정한다. | 현재조사complete는13-C인증이아니다. 원문byte기준은사용자답변전유지하며Claude실호출은미관측이다. |
| G7 Lean/예약/학술 |012의 실제 Mathlib·정상/오류·full 녹화/재생을 검수해 지정 Lean 범위를 닫았다.013의 시험 이름 등록·pythonw 발화·해제도 검수했다.014의 Codex worker를 통한 list_sources 성공 완료·전체 결과와 격리·녹화/재생도 검수했다. 각 경계의 최종 판본 재사용 조건을 유지한다. | 공유 manifest/캐시·생성기 의존을 순차화한다. Job/pythonw 성공·예약 cmdlet 대역·도구 판본만으로 대신하지 않는다. 설치 신뢰 승인/연구 검증은 Lean smoke 밖이고 held 예약 성공은 연구 운전 성공이 아니다. 학술 도구 시작 사건만으로 성공 응답을 판정하지 않는다. |
| G1/G3 문서 P01 및 전건 회귀 |008 지정 성과와009 정본110/미러89 전건 통과를 검수해 이 부분을 닫았다. | B132~B134 및008 단언 유지. 최종 전체 판본 연결은 G4~G6/G8에 남는다. |
| G1/G8 문서 N03 지정 문장 |008의 installation_root 전달 설명·bootstrap-info2건과009 회귀를 검수해 같은 문서 변경 단위로 인도한다. | 옛 전역은 복원하지 않는다. N03 다른 절은 계속 미검토. |
| G1/G3 나머지 문서·정책 | 019의 P02 네owner를 닫았다.020이 P03 실행 안내/지급 도구를 맡고 P04~P11·N01~N03의 다른 미결 절은 후속으로 남긴다. 실제 반환/공유 계약·기존 시험에 연결한다. 명시 소비 없는 instance는 제거 가능성을 판정한다. | 34 AST 구문지점의 제거 수로 진척을 세지 않고 마지막 소비자 뒤 helper를 정리한다. |
| G7 T4 adapter 보고 | 015의 실제 측정/게시/병합과 현 adapter 전체 정보 보고를 검수했다. 각60worker·원DB 재분석과 양쪽70회귀를 유지한다. | 도달률은 임계 관문이 아니다. T4 기능 실패/skip 및 G5 fresh 최종 판본은 별개다. |
| G1/G3/G7 T4 fixture·OS 실패 | 016의 정확10실패/오류는017 양쪽 전체 T4에서 모두passed로 검수해 닫았다. 새 Job cleanup 한 오류도018의 종료확인 수리와 양쪽전체295passed로 닫았다. | Git WinError6은 관측자의 stdin 부수효과였다. 제품runtime/신뢰guard는 유지했고 과거bootstrap WinError5 원인은 미확인이다. |
| G2/G3/G7 P10/P11 실제 비교 | 017에서910파일 실제소비·양쪽각2passed와 정본raw6fixture/30snapshot/16DB를 검수해 이 비교를 닫았다. PR01 다른slice는 유지한다. | P10/P11은 여기서 역사/정확시험 표기이며 requirement-state ID나 문서packet과 다르다. 역사raw4개부재와 새 성공을 구별하며 미러 원fixture raw는 별도 보존되지 않았다는 한계를 유지한다. |
| G7 T4 실제 연결과015~016 제품 마감 | 018의 최종 정본/미러 각295passed/exit0·각60worker 측정complete를 검수해 지정 T4 연결을 닫았다. 기존22와018fixture2의 합24제품경로는018 관리커밋a29f3c6a에 포함됐다. | 부분합산은전체성공이아니다. 미해결실패/skip은정확후속work로넘기며G4~G8전체완료로확대하지않는다. |
| G4 조건부 symlink 미검사 |019 관련 양쪽의 Windows1314 skip은 실제 탈출 반려를 입증하지 않았다. 최종 기본전체에서 원문상 환경조건을 판정하고 미검사를 명시한다. |권한이나 G4 기준을 자의 변경하지 않으며 skip을 통과로 세지 않는다. |
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


# 파일: docs/do-math/continuous-development-2026-10-13/seams.md

# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~008의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 의미는 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 현재 결과와 남김은 context C11/C12에 있다.

phase 006의 비결박 경로는 중앙 제출 control_binding 없이 CLI 최종 응답을 직접 받는 ModelRunner 호출이다. 이 Codex 전송의 정본은 do_math/provider_final.py의 output_contract·semantic_output이다. ModelRunner가 원 schema를 output.schema.json에 보존하고 전송 schema를 transport.schema.json으로 넘긴다. source_request·worker snapshot/hash·native final과 종료는 기존 수집 경계를 거쳐야 한다. classify_run은 전송을 해석한 의미 값을 canonical 검사와 원 schema로 검증한다. 선택 필드 부재/null/값과 원 제약은 유지한다. Claude는 직접 JSON을, control_binding은 별도 중앙 제출 계약을 유지한다. 코드 정의를 자연어의 별도 schema로 복제하지 않는다.

phase 007은 같은 경계의 fixture와 pair를 수리했고 manager가 지정 회귀를 검수했다. 제품 runtime은 불변이다. phase 008은 기존 _context 반환의 operational_evidence/recovery_materials를 문서와 실제 반환 검사로 연결한다. 일반 재개 restore_continuation과 동일한 필드명을 사용하더라도 다른 생산자다. 원자료의 정상/복원 오류/null/부재를 각 실제 객체에서 확인한다. 독립-운영의 설치 경로 설명도 현재 operator_bootstrap.main과 scheduled_operator.main 경계로 교정한다. 제품 계약 개정이나 새 task 사이 인터페이스가 없어 provides/uses는 빈 목록으로 유지하며 S 항목을 추가하지 않는다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase 004의 verbatim과005의 하위 manifest -text를 유지한다.007은 새 녹화 없이 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인했다. 008도 corpus를 수정하지 않으며 허용된 문서·시험 사본만 공식 생성한다.

제품 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. report 형식은 서비스 protocol.md가 직접 규정한다. 후속 phase에서 외부 제공자/소비자를 분리 배정하려면 manager가 먼저 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 공유 검사와 실제 연결 책임을 해당 S 항목에 정한다. 같은 인터페이스는 같은 S ID를 유지하며 제품 내부 선택을 불필요한 seam으로 승격하지 않는다.

008의 운영/복구 및 설치 설명 지정 성과를 검수했으나 전건 문서 검사는 기존 CLI 함수 표기로4건 실패했다. 009는 해당 표기를 function_reference_issues의 현 함수 표기 계약에 맞추는 문서 수리이며 제품 경계·오류·입력 의미를 바꾸지 않는다. provides/uses는 계속 빈 목록이고 새 S 항목은 없다. 검수 근거는 run:phases/008/manager-evidence/review.md, 후속 책임은009 objective다.

009는 기존 함수 참조 표기만 교정해 정본110·미러89 전건 관련 회귀를 통과했고 manager가 원자료/현재 소스를 대조했다. 제품 경계 계약의 개정은 없다.010 host-smoke는 기존 windows_job/Jobs·실제 worker·console_python/PowerShell 출력 계약을 소비하며 테스트 공유화는 한 task 내부다.010 reading-limits는 고정된 운전 문서·CLI 입력 경로와 외부 호스트 읽기 계약을 독립 조사한다. 서로의 결과를 제공/소비하지 않아 S 항목을 새로 만들지 않는다. runtime 경계 변경이 필요하면 별도 finding과 후속 배정으로 돌린다.

010 host의 기존 runtime 소비 성과와 reading 조사를 검수했다.011은 현 _job_run의 필수 clock/environment를 기존 fixture에 전달하고 지정 음성 단언과 읽기 문구만 교정한다. 기존코드정본/실포트의입력·반환·오류의미는바꾸지않는다. 전건검사/미러/캐시소유를한task로모아제공자/소비자분리가없으며S항목·provides/uses는추가하지않는다. 읽기출력byte요구나운전host지정은이work의재량밖이다.

011의 기존 포트 fixture·정확 음성 단언·읽기 문구 수리를 검수했다.012는 현재 setup_lean.verify_environment/inspect_toolchain/verify_lean과 real_ports를 소비하는 Lean/Mathlib 최소 실연쇄다. 입력/반환/실패의 정본은 기존 함수·lean_evidence·trust_inventory이며 별도 형식 복제나 제품 계약 개정은 없다. 새 smoke/helper·녹화/재생과 미러를 한 task가 소유해 provides/uses는 빈 목록이고 S 항목은 추가하지 않는다. 설치/신뢰 상태 변경이나 runtime 수리가 필요하면 반례를 다음 배정으로 반환한다.

012 Lean/Mathlib의 기존 API 소비와 새 full 녹화/재생을 검수했다.013은 기존 PowerShellScheduler.run → operator_schedule.ps1, scheduled_operator.schedule/hold와 operator_bootstrap의 실제 OS 경계를 소비한다. 인자·Task-View 반환·실패의 정본은 이 코드와 ports/scheduler.py 및 현 계약 시험이며 별도 schema나 새 의미를 만들지 않는다. smoke/helper·corpus·미러를 한 task가 소유하므로 S 항목과 provides/uses는 추가하지 않는다. task 이름의 부재 확인·자기 소유 증거·정리는 외부 부수 효과의 범위이며 기존 예약/연구를 변경할 권한이 아니다. runtime/OS 권한 변경이 필요하면 후속 판단으로 반환한다.

013의 기존 예약 API 소비와 실제 OS 발화/정리·녹화 재생을 검수했다.014는 resolve_scholarly_server의 command/args, ModelRunner.run의 scholarly_server 및 worker의 실행별 scholarly-data 격리, native 도구 사건과 services/scholarly-mcp/server.py의 list_sources/ToolResult·registry.Source.summary를 소비한다. 시작 도구명과 완료 성공 응답은 구별한다. 새 시험·작은 지원 정의·corpus/reader·미러를 한 task가 소유하며 기존 제품 인터페이스를 개정하지 않으므로 S 항목·provides/uses는 추가하지 않는다. runtime·서버·공유 설정 변경이 필요하면 정확 반례와 후속 책임으로 반환한다.

014의 기존 scholarly API 소비·성공 완료/양 본문·격리와 녹화 재생을 검수했다.015는 run_tests.py의 main/_isolated/_worker/결과 집계와 tests/support/branch_gate.py의 측정/저장/병합 정의, do_math.layers.LAYERS를 기준으로 T4 보고를 연결한다. 시험 결과와 측정 완전성·분기 도달 보고는 구별하고 T3 gate·선택 색인·증분 저장소 의미를 유지한다. 같은 task가 생산자/소비자·회귀를 함께 수정하므로 별도 S 항목이나 provides/uses는 추가하지 않는다. 새 보고 형식의 정본은 구현의 실제 선언과 검증으로 두며 자연어의 중복 schema를 만들지 않는다.015 task가 지침과 생산/소비 시험을 같은 변경으로 맞춘다.

015의 T4 보고 정의는 tests/support/adapter_coverage.py의 AdapterMeasurement·validate_publication과 run_tests의 실제 소비가 정본이다. manager는 실제 worker 자료와 양쪽70회귀를 검수했고 T3 의미는 유지했다.016 t4-fixture-repair는 기존 trust_inventory/ModelRunner/ResearchRepository/formal/실포트 계약의 fixture 소비만 고친다. provenance-baseline은 Git 원바이트 입력을 자기 evidence에 준비하며 같은 phase의 다른 task와 제공/소비하지 않는다. SHARED_INPUT_BASELINE_SCRIPTS의 실제 소비는 기존 test_shared_input_provenance.py가 정의하고 후속 연결 task가 맡는다. 제품 인터페이스 개정이나 병렬 제공자/소비자 분리가 없어 S 항목과 provides/uses는 추가하지 않는다.

016은 현재 fixture 소비만 교정했고 Git과 과거 입력 원바이트를 검수했다.017은 기존 SHARED_INPUT_BASELINE_SCRIPTS 소비·TestCase/WORKER/SNAPSHOT·run_tests/AdapterMeasurement의 실제 연결을 검증한다. 두 task 사이 새 인터페이스를 구현하지 않고 한 task가 고정된 제공/소비를 함께 실행하므로 S 항목·provides/uses는 추가하지 않는다. 의미/형식/오류의 정본은 기존 코드와015 측정 정의이며 과거910파일을 새 제품 계약이나 호환 분기로 만들지 않는다.

017의 두 exact 비교와 실제 T4 측정·게시 연결을 검수했다.018은 현 Jobs 포트의 launch/resume/terminate/wait/inspect/close를 사용하는 시험 fixture cleanup만 교정한다. close의 핸들 닫기/kill-on-close와 root/빈Job 종료 관측을 구별하며 제품 API 의미를 개정하지 않는다. real/fake 공유 fixture와 관련 시험·전체 T4를 한 task가 소유하므로 새 S 항목·provides/uses는 없다. runtime/계약 개정 필요성은 정확 반례로 다음 manager에 반환한다.

018의 기존 Jobs API 소비와 최종 양쪽T4 연결을 검수했다.019는 기존 write_source_catalog·_preserve_outputs·_apply·_context·prepare_role_input의 생산/저장/복원을 실제 소비하는 문서 검사 수리다. 정본은 해당 함수·contracts/record schema이며 별도 제품 형식을 만들지 않는다. 같은task가 doc_code와 직접소비/helper·미러를 소유하고 독립 제공자/소비자로 나누지 않으므로 S항목·provides/uses는 추가하지 않는다. runtime/입출력 의미 개정이 필요하면 반례로 후속 판단에 반환한다.

019의 P02 실제 생산/저장/복원 문서 결속을 검수했다.020은 기존 _context·record_map·prepare_role_input·install_tools의 실행 안내와 지급 도구 경계를 소비한다. 명령/설치파일/오류/조건부 부재는 현 코드가 정본이고 문서 검사용 별도 schema를 제품 계약으로 만들지 않는다. 같은task가 helper와 직접 소비·미러를 소유하며 제품 인터페이스를 개정하지 않으므로 S항목·provides/uses는 추가하지 않는다. record_map 기본 반환, preview 지급과 실제 검증 결과의 차이, scholarly 설정과 실호출의 차이를 유지한다.


# 파일: docs/do-math/continuous-development-2026-10-13/phases/019/manager-evidence/review.md

# phase 019 검수

P02의 지정 A1~A4를 승인한다. manager는 원 report 형식 검사 뒤 현재2675파일·시작과018 판본 동일·허용30변경, 공식 선택/실제 row/exit와875개 Python 해시를 직접 검산했다. 정본과 미러의 동일187개 ID는 각각186passed·권한1314의 symlink1skipped·exit0이다. skip은 G4에서 원문 계약에 따른 조건부 미검사를 판정할 대상으로 유지한다. 개발 전체 완료는 아니다.

실제 코드 diff에서 source_ref의 catalog writer, results의 _apply 보존, _context의 원자료/과제 결과 물질화와 prepare_role_input을 확인했다. 새 helper는 저장 artifact와 이번 workspace의 task/execution별 local_path, snapshot 원바이트·SHA·크기를 대조한다. 동일 바이트의 다른 실행 경로도 반려한다. 수제 results는 복원만 증명하고 실제 생산·knowledge 별도 권위·독립 bundle 비중복은 기존 수신과600k 보고/파일 개정·재개 시험이 맡는다. 일반 defer의 담당 AST 검사는 실제 결과를 추론하는 데 쓰이지 않고 담당 method와 문서 검사 호출의 존재만 확인한다. 실제 실행 row와 구체적 단언을 함께 대조했다.

수리 전8개 owner/별칭 subTest의 red, 초기13error와 corrected23passed, 최종 양쪽의 정확 failed/error ID 해소를 원 row로 확인했다. 정상 빈 배열은 원소 필드 증거와 구별되고 실제 제품의 손상 hash 반려·read_source size/hash 사유는 반환 사본 교란과 별도다. P01·B130~B134 및 다른 owner의 실패 단언이 최종 선택에 남는다. B110~B114 중 P02 AST/문자열 조립만 교체한 처분을 승인하며 PR24·REVIEW/TRUST 전체는 종결하지 않는다.

runtime/실호출139입력·144corpus경로/150명시SHA·host8원자료/도구5·baseline910의 바이트/Git blob·T4 고정 경계가 보존됐다. 공식 생성·캐시 동기화·check와 skill-only의 실제 exit와 원출력을 확인했다. 두 문장은 앞으로 일반 역할 prompt에 들어가므로 과거 고정 smoke를 새 문서 읽기/AI준수의 근거로 사용하지 않는다. 원task181파일은 검산 전후 불변이며 이전 실패도 수정하지 않았다.

다음020은 P03의 실행 안내와 지급 도구를 실제 설치 후 최종 입력에 연결한다. 현재 doc_code의 해당 AST 조립과 install_tools/_context를 직접 확인해 한정 범위를 정했다. 공통 helper·문서 순회·미러·캐시가 겹쳐 다른 제품 작업과 병행하지 않는다. L01의 외부 결정과 독립적이며 새 실호출·전체T4 반복은 배정하지 않는다. G4 기본전체, G5 freshT3, G6 전수변이, 나머지 의미/문서 및 최종 review가 남아 next:null 조건은 충족하지 않는다.


# 파일: docs/do-math/continuous-development-2026-10-13/phases/019/manager.pending.json

{
  "next": "020",
  "decision": "019 document-results의 A1~A4를 검수해 P02 지정 남김을 닫는다. 원 report 형식, actual source diff, 현재2675파일·허용30변경과 양쪽 동일187ID의186passed/1skipped/exit0를 대조했다. 실제 catalog/생산/저장/복원 검사와 담당 위임, 초기 실패의 최종 해소를 확인했으며 수제fixture의 물질화와 _apply 생산 근거는 구별한다.\n\nWindows1314 symlink skip은 실제 탈출 반려나 G4 통과로 세지 않는다. runtime139·corpus144/150SHA·host8/tools5·baseline910·T4 경계는 불변이고 두 문장 변경은 미래 역할 prompt에 영향을 준다. 이전 고정 smoke의 승인된 성질만 재사용하며 새 문서 준수의 실측으로 확대하지 않는다. 검수된28비캐시 제품경로를 관리 마감한다.\n\n020은 P03 실행 안내와 지급 도구 여섯 소유자를 실제 설치 후 최종 입력에 연결하는 단일 work다. 현재 doc_code·install_tools·_context에서 경계를 확인했다. 공유 helper/미러/캐시·시험 판본이 겹쳐 다른 제품 task와 병렬화하지 않는다. L01 결정과 독립적인 작업이고 새 외부 호출/전체T4 반복은 필요하지 않다. 직전 phase가 work이며 다른 의미/문서와 G4~G6/G8이 남아 종료 조건은 충족하지 않는다.",
  "reports": [
    {
      "task": "document-results",
      "state": "read",
      "detail": "report 형식 검사와 A1~A4의 원자료/현재 코드 대조를 통과했다. 지정 complete를 승인하고 symlink 조건부 미검사·최종 G의 남김은 유지한다.",
      "evidence": [
        "run:phases/019/tasks/document-results/report.json",
        "run:phases/019/manager-evidence/report-check.json",
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md"
      ]
    }
  ],
  "dispositions": [
    {
      "item": "019/document-results/F1",
      "action": "resolve",
      "destination": [
        "run:context.md#C9",
        "run:context.md#C10",
        "run:plan.md"
      ],
      "reason": "실제 생산/복원/문서 담당과 원결과를 검수해 P02 slice만 종결한다. PR24·다른 packet은 유지한다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/019/tasks/document-results/evidence/binding-review.md"
      ]
    },
    {
      "item": "019/document-results/F2",
      "action": "carry",
      "destination": [
        "run:context.md#C11",
        "run:plan.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ],
      "reason": "P02 필수 성질은 실행됐으나 실제 symlink 탈출 반려는 권한1314로 미검사다. G4의 원문상 조건부 환경 판정에 남기며 통과나 권한 변경으로 처리하지 않는다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/tasks/document-results/evidence/c/report.json",
        "run:phases/019/tasks/document-results/evidence/m/report.json"
      ]
    },
    {
      "item": "019/document-results/F3",
      "action": "resolve",
      "destination": [
        "run:context.md#C12",
        "run:plan.md"
      ],
      "reason": "현재 바이트/Git clean·명시SHA·도구/원자료를 검수해 보존 사실을 승인한다. 기존 성질만 재사용하고 미래 prompt 영향과 최종 판본 관문은 유지한다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/tasks/document-results/evidence/preservation.json",
        "run:phases/019/manager-evidence/review.md"
      ]
    }
  ],
  "context_updates": [
    {
      "item": "C2",
      "action": "amend",
      "destination": [
        "run:context.md#C2"
      ],
      "reason": "019의 지정 완료·판본/회귀와 미검사 범위를 추가했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C5",
      "action": "amend",
      "destination": [
        "run:context.md#C5"
      ],
      "reason": "현재 단일 작업을020 P03으로 바꾸고 공유 helper/미러/실행 자원의 소유를 명시했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C6",
      "action": "amend",
      "destination": [
        "run:context.md#C6"
      ],
      "reason": "기존 관리 마감의 순서를 명확히 했다. manager.json 게시 뒤 계약을 바꾸지 않고 정확한 커밋을 확인한 뒤 세션을 종료한다.",
      "evidence": [
        "run:phases/018/manager-evidence/finalize.py",
        "run:phases/019/manager-evidence/writing-decision-1.json"
      ]
    },
    {
      "item": "C8",
      "action": "amend",
      "destination": [
        "run:context.md#C8"
      ],
      "reason": "사용자 지정 모델을020에도 적용했다. 모델 전환 이력의008 당시 검수와 현재019 상태를 구별하도록 시점 표현을 명확히 했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C9",
      "action": "amend",
      "destination": [
        "run:context.md#C9"
      ],
      "reason": "B110~B114의 P02 한정 처분을 추가하고 다른 slice를 보존했다. A20을 설계.md의3.3절·설계 결정 번호로 명시했으며 검사 의무는 유지했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C10",
      "action": "amend",
      "destination": [
        "run:context.md#C10"
      ],
      "reason": "019의 예정 작업을 실제 완료와020의 한정 책임으로 교체했다. 기존 P/N/L01 조건은 보존했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C11",
      "action": "amend",
      "destination": [
        "run:context.md#C11"
      ],
      "reason": "019 symlink 권한 skip을 G4의 별도 미검사 책임으로 추가했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    },
    {
      "item": "C12",
      "action": "amend",
      "destination": [
        "run:context.md#C12"
      ],
      "reason": "139입력 등 보존과 미래 prompt 영향,28제품 마감/원근거 보존 경계를 추가했다.",
      "evidence": [
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/020/tasks/document-tools/objective.md"
      ]
    }
  ],
  "plan_update": "019 P02를 지정 완료로 닫고020 P03 실행 안내/지급 도구를 단일 work로 배정했다. symlink 조건부 미검사를 G4에 명시하고018 제품마감을 실제 HEAD929fa4cc로 정정했다. 나머지 의미/문서·L01·전체일반/freshT3/전수변이·최종review의 선행 관계와 책임은 보존했다. A20의 원문 소속과 P03 preview 하위 객체 관계도 명확히 했다. seams의011 역사 문장은 의미를 유지하며 띄어쓰기만 교정했고 S계약 개정은 없다.",
  "seam_updates": [],
  "completion": null
}


# 파일: docs/do-math/continuous-development-2026-10-13/phases/020/phase.json

{
  "kind": "work",
  "purpose": "P03 실행 안내와 지급 도구의 문서 필드를 실제 설치·최종 역할 입력에 연결한다.",
  "tasks": [
    {
      "id": "document-tools",
      "model": "gpt-6.1-sol",
      "effort": "high",
      "inputs": [
        "run:sources/user-decisions.md",
        "run:sources/model-policy-2026-10-14.md",
        "run:phases/001/tasks/document-closeout/report.json",
        "run:phases/001/tasks/document-closeout/evidence/followup-packets.json",
        "run:phases/001/tasks/document-closeout/evidence/binding-inventory.json",
        "run:phases/001/tasks/closure-map/evidence/prior-review-state.json",
        "run:phases/019/tasks/document-results/report.json",
        "run:phases/019/tasks/document-results/evidence/binding-review.md",
        "run:phases/019/tasks/document-results/evidence/preservation.json",
        "run:phases/019/manager-evidence/verification.json",
        "run:phases/019/manager-evidence/review.md",
        "run:phases/019/manager-evidence/source-inspected.json",
        "run:phases/010/tasks/host-smoke/evidence/review.md",
        "run:phases/012/tasks/lean-smoke/evidence/review.md",
        "repo:docs/do-math/시험-재편-2026-09-29/설계.md",
        "repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md",
        "repo:.claude/skills/do-math/AGENTS.md",
        "repo:.claude/skills/do-math/scripts/tests/시험-지침.md",
        "repo:.claude/skills/do-math/scripts/이음새-정본.md",
        "repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md",
        "repo:.claude/skills/do-math/README.md",
        "repo:.claude/skills/do-math/references/CLI-실행-계약.md",
        "repo:.claude/skills/do-math/references/공통-실행.md",
        "repo:.claude/skills/do-math/references/입력-소비자.md",
        "repo:.claude/skills/do-math/references/자기-점검.md",
        "repo:.claude/skills/do-math/references/지식-저작과-재사용.md",
        "repo:.claude/skills/do-math/계약/연구-수행.md",
        "repo:.claude/skills/do-math/계약/유지보수.md",
        "repo:.claude/skills/do-math/scripts/do_math/context_store.py",
        "repo:.claude/skills/do-math/scripts/do_math/core_engine.py",
        "repo:.claude/skills/do-math/scripts/do_math/submission.py",
        "repo:.claude/skills/do-math/scripts/do_math/contracts.py",
        "repo:.claude/skills/do-math/scripts/tests/support/doc_code.py",
        "repo:.claude/skills/do-math/scripts/tests/support/engine_context.py",
        "repo:.claude/skills/do-math/scripts/tests/sim/test_role_input_context.py",
        "repo:.claude/skills/do-math/scripts/tests/unit/test_submission_preview_commands.py",
        "repo:.claude/skills/do-math/scripts/tests/sim/test_knowledge_project_identity.py"
      ],
      "writes": [
        ".claude/skills/do-math/scripts/tests/support/doc_code.py",
        ".claude/skills/do-math/scripts/tests/support/engine_context.py",
        ".claude/skills/do-math/scripts/tests/structure/test_doc_code.py",
        ".claude/skills/do-math/scripts/tests/sim/test_role_input_context.py",
        ".claude/skills/do-math/scripts/tests/sim/test_knowledge_project_identity.py",
        ".claude/skills/do-math/scripts/tests/unit/test_submission_preview_commands.py",
        ".claude/skills/do-math/scripts/tests/unit/test_role_input_packaging.py",
        ".claude/skills/do-math/scripts/tests/unit/test_role_input_scoped_packaging.py",
        ".claude/skills/do-math/scripts/tests/unit/test_preflight.py",
        ".claude/skills/do-math/scripts/tests/unit/test_context_catalog.py",
        ".claude/skills/do-math/scripts/tests/sim/test_submission_receiver.py",
        ".claude/skills/do-math/scripts/tests/flows/test_submission_acceptance.py",
        ".claude/skills/do-math/scripts/tests/flows/test_knowledge_impact_retry.py",
        ".claude/skills/do-math/scripts/tests/boundary/test_engine_cli.py",
        ".claude/skills/do-math/scripts/tests/unit/test_storage_report_projections.py",
        ".claude/skills/do-math/scripts/tests/unit/test_engine_trace_report_corruption.py",
        ".claude/skills/do-math/scripts/tests/unit/test_storage_record_queries.py",
        ".claude/skills/do-math/scripts/tests/sim/test_knowledge_currentness.py",
        ".claude/skills/do-math/README.md",
        ".claude/skills/do-math/references/CLI-실행-계약.md",
        ".claude/skills/do-math/references/공통-실행.md",
        ".claude/skills/do-math/references/입력-소비자.md",
        ".claude/skills/do-math/references/자기-점검.md",
        ".claude/skills/do-math/references/지식-저작과-재사용.md",
        ".claude/skills/do-math/계약/연구-수행.md",
        ".claude/skills/do-math/계약/유지보수.md",
        ".claude/skills/do-math/scripts/tests/.timings.json",
        ".claude/skills/do-math/scripts/tests/.timings-t3.json",
        ".agents/skills/do-math/scripts/tests/support/doc_code.py",
        ".agents/skills/do-math/scripts/tests/support/engine_context.py",
        ".agents/skills/do-math/scripts/tests/structure/test_doc_code.py",
        ".agents/skills/do-math/scripts/tests/sim/test_role_input_context.py",
        ".agents/skills/do-math/scripts/tests/sim/test_knowledge_project_identity.py",
        ".agents/skills/do-math/scripts/tests/unit/test_submission_preview_commands.py",
        ".agents/skills/do-math/scripts/tests/unit/test_role_input_packaging.py",
        ".agents/skills/do-math/scripts/tests/unit/test_role_input_scoped_packaging.py",
        ".agents/skills/do-math/scripts/tests/unit/test_preflight.py",
        ".agents/skills/do-math/scripts/tests/unit/test_context_catalog.py",
        ".agents/skills/do-math/scripts/tests/sim/test_submission_receiver.py",
        ".agents/skills/do-math/scripts/tests/flows/test_submission_acceptance.py",
        ".agents/skills/do-math/scripts/tests/flows/test_knowledge_impact_retry.py",
        ".agents/skills/do-math/scripts/tests/boundary/test_engine_cli.py",
        ".agents/skills/do-math/scripts/tests/unit/test_storage_report_projections.py",
        ".agents/skills/do-math/scripts/tests/unit/test_engine_trace_report_corruption.py",
        ".agents/skills/do-math/scripts/tests/unit/test_storage_record_queries.py",
        ".agents/skills/do-math/scripts/tests/sim/test_knowledge_currentness.py",
        ".agents/skills/do-math/README.md",
        ".agents/skills/do-math/references/CLI-실행-계약.md",
        ".agents/skills/do-math/references/공통-실행.md",
        ".agents/skills/do-math/references/입력-소비자.md",
        ".agents/skills/do-math/references/자기-점검.md",
        ".agents/skills/do-math/references/지식-저작과-재사용.md",
        ".agents/skills/do-math/계약/연구-수행.md",
        ".agents/skills/do-math/계약/유지보수.md",
        ".agents/skills/do-math/scripts/tests/.timings.json",
        ".agents/skills/do-math/scripts/tests/.timings-t3.json"
      ],
      "provides": [],
      "uses": []
    }
  ]
}


# 파일: docs/do-math/continuous-development-2026-10-13/phases/020/tasks/document-tools/objective.md

## 목적과 역할

G1/G3의 문서 결속 중 phase 001 followup-packets의 P03을 닫는다. 실행 안내와 지급 도구의 필드가 실제 설치 후 역할 입력을 검사하도록 기존 시험에 연결한다. 대상 소유자는 record_map의 read_tool, execution_window, scholarly, formal_verifier, preview, submission_contract다. record_map 기본 반환에 대한 기존 검증은 보존한다. 현재 doc_code의 AST 조립은 install_tools가 만든 파일과 최종 입력의 일치를 증명하지 못한다.

019의 P02는 검수됐고 양쪽187건 중186통과·기존 symlink 권한1skip이었다. 수리한 P01/P02·B130~B134의 실제 결과 검사를 유지한다. P03은 그 검사 기반을 공유하므로 한 task가 doc_code·직접 소비·미러를 소유한다. 실행 도구 설치와 포장을 확인하되 도구가 실제 모델·Lean·학술 호출에 성공했다는 별도 주장을 만들지 않는다.

## 완료 조건

### A1 현재 문서와 설치 전후 경계 확정

시작 skills/diff 해시를019 manager source-inspected2675파일과 대조하고 차이의 출처를 구별한다. P03의 현재 문서 위치·별칭·조건을 _context, prepare_role_input, record_map, install_tools의 실제 생산/소비에 연결한다. followup-packets의 역사 행 번호는 현재 제목과 코드로 확인한다. 결함-범주.md의13-C와 P03 지정 원문을 읽되 다른 packet으로 조사 범위를 늘리지 않는다.

문서의 preview 소유자는 install_tools가 formal_verifier 안에 추가한 formal_verifier.preview 객체를 별도로 순회하는 경계다. formal_verifier 전체와 그 preview 하위 객체를 검사하되 서로 다른 생산 결과로 만들지 않는다. execution_window의 경로 안내와 실제 동적 파일, scholarly.configured와 실제 도구 노출/호출, formal_verifier.preview의 지급 명령과 그 명령의 반환 JSON을 구별한다. B110~B114의 이 P03 slice만 actual diff·현재 소비·존재 원보고로 유지/교체/제거 판단한다. record_map 기본 반환과010 host·012 Lean의 승인된 성질은 재사용하고 PR24 전체를 완료로 올리지 않는다.

### A2 실제 설치와 최종 입력에 결속

기존 PreparedInputTests·RoleScopeContextTests·LeanPreviewTests·FormalInputManifestTests와 role packaging 시험을 사용해 대상 여섯 소유자를 실제 반환 또는 기존 공유 계약에 연결한다. install_tools가 쓴 input/tools의 check_submission.py·read_input.py·check_lean.py와 submission-support.zip, 제출 schema/context 파일과 실제 command/경로·tool_sha256·snapshot·권한 범위를 대조한다. 기존 archive/명령 실행 근거가 충분하면 재사용하고 새 장기 엔진 시나리오를 만들지 않는다.

_context의 실제 execution_window.self_check_directory와 고정 프로필에 따른 scholarly, 실제 formal_verifier, 설치 후 preview/record_map.read_tool/submission_contract 및 limits.checkpoint_bytes/max_artifact_bytes를 확인한다. 최종 fitted 입력에서 참조로 포장된 경우에는 정확한 참조 파일을 읽는다. 검사 정상 표본을 수동 복제하거나 제품 내부 생산/설치/포장을 대역으로 가리지 않는다. 외부 포트 대역과 실제 실행 근거의 범위는 구별한다. 기본 record_map 반환 검사를 유지하면서 read_tool AST만 실제 설치 결과에 연결한다.

문서의 기한·정지·종료 요청 의미, preview의 authoritative=false 및 중앙 재검사, scholarly 설정과 실제 성공의 차이, 콘솔 없는 실행기에서 지급하는 console Python 조건을 보존한다. 필요한 문장·별칭만 writes의 문서에 반영한다. runtime API와 입력/출력 의미를 문서 검사 편의로 바꾸지 않는다.

### A3 누락·다른 도구·조건부 부재와 실제 담당 검사

실제 반환 후 사본에서 self_check_directory, 지급 command, checkpoint_bytes, max_artifact_bytes를 각각 삭제해 문서 검사가 반려하는지 확인한다. 같은 command 필드라도 다른 지급 도구의 명령으로 바꾸거나 파일/해시를 차용하면 거부해야 한다. 설치된 정상 preview와 설치하지 않은 조건을 구별하고, 미설치 경로를 정상 필드 증거로 쓰지 않는다. windowless 실행기의 console sibling 정상 선택과 sibling 부재의 명시 반려·무부수효과는 현재 기존 시험에 연결한다. 고정 프로필 외 도구 override 반려와 실제 worker 미기동 단언을 보존한다.

새 단언이 드러내는 정확한 공백을 수리 전 실행해 red를 남기고 같은 성질의 green을 연결한다. 일반 문서 순회가 실제 입력 담당에게 위임하는 경우 소유자별 실제 문서 검사 위치를 명시한다. defer 오기·담당 누락·다른 소유자 동시 건너뜀 반례와 기존 P01/P02 등의 음성 단언을 유지한다. 범용 추론기·전역 등록부를 추가하지 않으며 이번 대상의 마지막 소비가 없어지는 AST 조립만 제거한다.

### A4 관련 회귀와 인도 근거

아래 최종 관련 선택을 정본과 미러에서 완결하고 선택/고유 row/실제 exit 및 실행 전후 소스를 보존한다. 허용 범위의 공식 미러 생성·마지막 캐시 동기화·--check·skill-only를 통과한다. 조건부 환경 skip은 통과로 세지 않고 원인·영향 성질·G4 후속 책임을 기록한다. P03 필수 성질 자체가 미실행이면 해당 A는 pass가 아니다.

019 preservation의 runtime/실호출139입력·corpus144경로/150명시SHA·host8원자료/도구5·과거baseline910·T4 고정 경계를 보존한다. 문서 수정이 향후 역할 prompt 판본에 미치는 영향과 기존 실호출의 한정 재사용을 구별한다. P04~P11·REVIEW/TRUST·나머지 P/N·L01과 G4~G6/G8은 후속 책임으로 남긴다.

## 판단과 경계

writes는 지정 시험/helper·문서 및 대응 미러/캐시다. 모두를 수정하라는 뜻은 아니다. helper의 작은 공통 함수와 구체적 시험 배치는 재량이다. runtime/core_engine/context_store/submission·runner·adapter·Job fixture·corpus·서버·설치 신뢰·공유 설정·공용 context/plan·다른 phase는 고정한다. 범위 밖 결함은 정확 재현, 필요한 파일, 영향 A와 후속 조치로 반환한다. 다른 owner의 AST가 남았다는 이유만으로 이번 범위를 늘리지 않는다.

전체 worker3 이하, jobs1, 한 묶음씩이며 검사 중 소스를 고정한다. parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 전용 경로를 사용하고 output/resource cwd도 짧게 둔다. 시간 예산은 소프트 기준이다. 새 유료 공급자·예약·학술 호출, 설치 신뢰 변경, 기존 연구 운전/삭제, graphify 갱신, Git stage/commit/reset/checkout/push는 수행하지 않는다. 개발 작업은 gpt-6.1-sol/high이며 제품 실호출 설정과 다르다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 공식 run_tests.py에 -u -B, --jobs 1, --output <자기 evidence의 짧은 새 경로>를 쓴다. argv/cwd/환경·PID/시각·종료·stdout/stderr·판본을 보존한다. 진행 result.json은 do_math.file_io.read_bytes_shared로 읽는다.

1. A1 경계를 확정하고 A3의 정확한 새 반례를 수리 전 실행한다.
2. 최종 정본에서 structure.test_doc_code sim.test_role_input_context unit.test_submission_preview_commands sim.test_knowledge_project_identity unit.test_role_input_packaging unit.test_role_input_scoped_packaging unit.test_preflight를 실행한다. 현재 class/method를 확인해 실제 설치와 최종 포장 경로의 포함을 기록한다.
3. 공유 helper와 문서 순회의 회귀에는 unit.test_context_catalog sim.test_submission_receiver flows.test_submission_acceptance unit.test_storage_report_projections unit.test_engine_trace_report_corruption unit.test_storage_record_queries boundary.test_engine_cli sim.test_knowledge_currentness.RecoveryMaterialTests flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests를 포함한다. 2/3의 중복을 없애 한 묶음 또는 순차 묶음으로 실행한다. 목록 밖 직접 소비에서 이번 변경으로 오류가 확인되면 정확 ID를 검증에 추가하고 writes 밖 수정은 manager에 반환한다.
4. 공식 생성 계획이 writes 안인지 확인한 뒤 미러를 생성한다. 미러 run_tests.py로 같은 최종 선택을 실행하고 마지막 캐시 동기화 뒤 build_skill_mirrors.py --check와 probe_cli.py --skill-only를 통과한다. 새 변경·실패 없이 성공 검사를 반복하지 않는다. 전체일반/freshT3/전수변이·전체T4·새T5는 이번 배정에 없다.
5. 지정 Python으로 services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 020 document-tools를 통과한다. report에 A1~A4, 실제 changes, 정상/반례·소유자별 책임, 역사 근거 재사용과 미검사 범위를 기록한다. 마지막 응답은 상태와 report 경로다.


# 파일: 기억/layer1/M-0569.md

---
id: M-0569
layer: 1
title: 결과 문서 결속을 검수하고 실행 안내와 지급 도구를 배정함
convention_version: 27
---

## 맥락

phase 019는 P02의 원자료·과제 결과 필드를 AST 조립에서 실제 catalog·생산·저장·복원 검사로 바꿨다. manager는 현재2675파일과 양쪽187개 선택/실제 결과를 대조해 지정 A1~A4를 승인했다. 양쪽186passed와 기존 symlink 권한1314의1skip을 구별하며 전체 일반·freshT3·전수변이·나머지 의미/문서·최종review는 유지한다. 검수된28비캐시 제품경로를 마감하고020 P03을 배정한다.

## 판단에 남길 조건

동일 바이트의 다른 실행 경로를 차용한 반례는 파일 해시만으로 소유권을 증명할 수 없음을 구체화한다. 검사는 이번 workspace와 task/execution 좌표, 저장 artifact와 snapshot을 함께 대조한다. 수제 results의 복원과 실제 _apply의 생산/비중복은 서로 다른 시험이 맡고600k 보고·파일의 기존 개정/재개 흐름을 재사용했다. 일반 defer의 AST 검사는 담당 method와 문서 검사 호출의 존재만 확인하며 최종 결과 의미는 실제 실행 단언이 맡는다.

새로운 문서 문구는 미래 일반 역할 prompt를 바꾸지만 역사 고정 smoke 입력은 그대로다. 기존 실호출은 승인된 성질만 유지하고 새 문서의 읽기/준수 증거로 넓히지 않는다. 다음 P03도 지급 명령·설치파일·최종 입력 결속과 실제 외부 호출 성공을 구별하도록 배정했다. 공통 doc_code와 미러/캐시를 동시에 바꾸는 제품 task는 독립 검증이 어려워 하나로 묶었다.

원근거 진입점은 docs/do-math/continuous-development-2026-10-13/phases/019/manager.json과 manager-evidence/verification.json·review.md다. 원task181파일과28제품 바이트는 raw-evidence.zip에 추적하고 전건SHA·선별 추적경로는 preservation.json에 둔다. 압축만 추적하는 중복 snapshot 원경로 및 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다. 원report와 역사 실패는 수정하지 않았다.
