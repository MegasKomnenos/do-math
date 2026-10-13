# 사용자 지정 모델과 실행기 전환

2026-10-14 사용자가 이 대화에서 순서대로 지시했다.

> 해당 작문 도구에 gpt 6.1 sol 을 활용하도록 네가 지금 바꿔줘
> 서비스 작업자도 앞으로 gpt 6.1 sol high 로
> manager는 gpt 6 astra xhigh

독해 도구의 기존 high를 유지하고 모델 기본값만 gpt-6.1-sol로 바꾼다. 서비스의 이후 task는 gpt-6.1-sol/high, manager는 gpt-6-astra/xhigh다. 새 phase의 task.model과 task.effort에 명시한다. manager의 독해 호출도 기본값을 사용하며 이전 gpt-6-astra/medium 재시도 인자를 복사하지 않는다. 제품 공급자 시험의 호출 설정은 이 요청의 대상이 아니다.

기존 run.py가 manager 설정을 시작 때 캐시하므로 settings.json 변경만으로 현재 실행을 바꿀 수 없었다. 서비스 엔진을 고치지 않고 이 실행의 dispatcher만 교체했다. 기존 phase 007 작업자 PID 33604를 Windows 프로세스 핸들로 확보한 뒤 dispatcher PID 29472만 종료했다. 작업자는 유지하고 종료를 기다린다. 교체 실행기는 007 manager를 새 설정으로 한 번 호출하고, 이후 manager.json의 next를 기존 서비스 run()에 넘긴다. 같은 phase의 task를 다시 실행하거나 로그를 덮어쓰지 않는다. 새 독해 기본값과 미러·설정 검증을 마친 뒤 준비 신호로 후속 호출을 연다.

현재 실행 상태 정본은 `runtime/model-change.json`, 전환 실행 로그는 `runtime/model-change.stdout.log`와 `runtime/model-change.stderr.log`다. `runtime/launch-001.json`은 교체된 원 실행기의 종료 기록이며 개발 목표 완료를 의미하지 않는다. 전환 스크립트는 `runtime/change-models.py`이며 이번 실행 전용이다. 새로 시작하는 미사용 phase에는 start.ps1/start.py가 같은 task 기본값과 settings.manager를 적용한다.

정본 작문 도구 2개 파일과 대응 미러, 이 실행의 settings/start/context/README 및 이 사용자 지시 기록은 운영자 변경이다. phase 007 task 변경으로 귀속하지 않는다. 과거 report와 호출 모델 기록은 변경하지 않는다. 실행 중인 모델 세션의 설정을 바꿨거나 새 모델의 실제 호출 성공을 확인한 것으로 해석하지 않는다.
