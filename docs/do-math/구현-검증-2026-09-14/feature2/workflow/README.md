# 실제 연구와 학술 후속

새 인스턴스에서 기존 Codex 로그인으로 실제 CLI 18회와 실제 Lean 1회를 실행했다. 작업 예산은 8회, 운영 예산은 10회 사용했다. 수학 과제와 학술 과제 모두 완료했고, 최종 인스턴스는 `completed`, 목표는 `mathematically_solved`, 학술 요구도 `completed`다. [보고서](report.json)와 [상태 검사](check-stdout.json)에 결과가 있다.

검증한 명제는 모든 자연수 n에 대해 n + 0 = n이라는 항등식이다. [Lean 소스](proof.lean)와 [해설](explanation.txt)은 검증된 K 기록에서 바이트를 추출했다. [재현 설명](reproducibility-note.md)은 별도 학술 수행의 보고 원문이며, 선언명·자연수 양화·실제 검증기에 기록된 Lean 판본을 독립 계획 실행이 대조했다. 학술 산출은 보고 본문으로 제출됐으며 별도 원고 파일이 있었다고 표현하지 않는다.

`state/research/instance.json`과 `state/runtime/state.json`에서 정본·실행·판정의 연결을 읽는다. `state/runtime/artifacts/`는 입력·출력·검사·checkpoint 원문이다. [research.bundle](research.bundle)은 단일 연구 ref의 전체 이력을 담고 Git 검증을 통과했다. `tested-skill.zip`은 [source-manifest.json](source-manifest.json)의 실행 당시 파일을 보존한다. `copy-manifest.json`은 scratch에서 복사한 원자료의 해시다. 읽기용으로 추출한 위 세 파일과 이 README는 그 복사 목록 밖의 파생 보기다.

`live_do_math_feature2.py`는 사용한 실행 절차이고 goal·config·academic-decision JSON은 실제 입력이다. 합성 모델 응답은 사용하지 않았다. 이 사례에서 실제 외부 공용 서비스에 학술 산출을 전송하지는 않았다.
