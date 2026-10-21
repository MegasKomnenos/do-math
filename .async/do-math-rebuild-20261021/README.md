# do-math 재구축 개발 기록

이 폴더는 do-math를 처음부터 다시 만든 async-development 개발의 기록이다. 개발은 2026-10-21에 진행됐다. 21:09에 실행기가 시작했고, 22:39에 최종 review 합격과 manager의 완료 게시(`queue.json`의 `status: complete`)로 끝났다. 만든 제품은 저장소의 `.claude/skills/do-math/`에 있으며, 사용자 진입점은 그 폴더의 `SKILL.md`다.

## 읽는 순서

1. **무엇을 왜 만들었는가**: [context.md](context.md)는 사용자가 확정한 결정과 설계 이유를, [user-messages.md](user-messages.md)는 사용자 원문을 담는다.
2. **어떤 순서로 만들었는가**: [plan.md](plan.md)는 결과물과 선행 관계를, [seams.md](seams.md)는 구성 요소 사이의 인터페이스를 담는다. 두 문서는 manager가 개발 중에 갱신한 최종본이다.
3. **어떻게 판정했는가**: 최종 검토는 [tasks/final-review/review.md](tasks/final-review/review.md)에 있다. 마지막 manager의 완료 판단은 [managers/0009/decision.md](managers/0009/decision.md)에 있다.
4. **실제 완주의 근거**: [tasks/mixed-completion/evidence.md](tasks/mixed-completion/evidence.md)는 실제 Codex·Claude 세션으로 작은 Lean 목표를 무인 완주한 과정을 담는다. 첫 시도에서 드러난 Windows 상태 파일 교체 결함과 그 수정도 여기에 있다.
5. **CLI 조사 근거**: [tasks/cli-discovery/cli-evidence.md](tasks/cli-discovery/cli-evidence.md)는 설치된 Codex·Claude CLI의 기동 옵션과 사용 한도 신호를 조사한 결과다.

task마다 `objective.md`(지시), `report.json`(보고), `integration.json`(통합 기록)이 추적된다.

## 로컬에만 있는 자료

다음 자료는 Git에서 제외된 이 호스트의 로컬 보관 자료다. 저장소를 다시 받아도 복원되지 않는다.

- 각 세션의 CLI 로그(`session.log`)와 프롬프트
- task 작업 사본(`workspace/`, `base/`)
- 실행기 로그(`runner.*.log`)와 상태(`state.json`)
- 실제 완주에 쓴 연구 인스턴스 둘. `tasks/mixed-completion/evidence/instance-add-zero-fixed-20261021/`이 완주 근거이고, `instance-add-zero-20261021/`은 결함을 드러낸 첫 시도다. 공개 기록·검토·목표 판정은 각 인스턴스의 `knowledge/`와 인스턴스 자체 Git에 있다.
- CLI 조사의 help·소스 발췌 파일들

## 남은 관찰

실행기의 상태 파일 교체는 Windows 접근 거부 오류(5/32/33)에 한해 최대 1초 다시 시도한다. 최종 review는 이를 관찰된 결함에 맞는 제한된 변경으로 판정했다. 실사용에서 같은 오류가 재발하면, 재시도 시간을 늘리는 대신 교체 방식 자체를 바꾸는 쪽을 검토한다. 그 방식은 POSIX 교체 의미를 쓰는 Windows API다.
