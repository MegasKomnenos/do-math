# 학술 지급 문서 수리 이후의 최종 독립 판단

## 얻을 결과와 판본

수용된 `academic-contract-guidance`가 최종 전체 리뷰의 F1을 실제로 해소했는지 독립 판단한다. 제품을 수정하지 않는 최종 review이며, 해당 work를 선행으로 모든 기존 work 결과를 간접 포함한다. inputs/context.md, plan.md, seams.md, task.json과 `C:\math\.async\dm-flow-repair-20261021\user-messages.md`의 최신 정정을 읽는다. 정본 AGENTS.md를 따르고 R1~R7과 사용자가 실제로 연구할 수 있게 하는 목적을 기준으로 판단한다.

이전 전체 대조는 `C:\math\.async\dm-flow-repair-20261021\tasks\final-goal-review\assessment.md`, report.json, evidence/에 남아 있다. manager의 수용·범위는 `C:\math\.async\dm-flow-repair-20261021\managers\0009\decision.md`와 verification-summary.json이다. 새 수리는 `C:\math\.async\dm-flow-repair-20261021\tasks\academic-contract-guidance\{report.json,integration.json,evidence/}`를 읽는다. 모든 task의 영구 자료는 기존 디렉터리에 남으므로 정리된 workspace 경로를 사용하지 않는다. 옛 파일이 필요하면 서비스 workspaces.py restore baseline/result로 별도 디렉터리에 복원한다. docs/가 필요하면 공용 `C:\math\docs\do-math\flow-repair-20261021\`를 읽기 전용으로 사용한다.

manager 0010이 새 수리 8파일을 충돌 없이 통합·수용했다. 현재 수용 판단과 저장 지급 근거/통합 bytes 대조는 `C:\math\.async\dm-flow-repair-20261021\managers\0010\decision.md`와 `verification-summary.json`에 있다. 추가 읽기 근거이며 기존 배정의 목표·범위·선행관계는 같다. manager의 정적 판단을 독립 리뷰 결론으로 대신하지 않는다.

## 최종 대조

1. 실제 수정판의 정본 `계약/후보-준비.md`, `계약/작업-계약-검토.md`, `references/모델과-실행예산.md`, `references/CLI-실행-계약.md`와 대응 공식 미러를 읽는다. core_engine의 unresolved/계약 개정 분기와 planning_engine._ensure_model_assessments의 revision_fields 소비에 비추어 자료 대기·필드별 보충·사용자 원 계약 요청 처리가 같은 의미인지 확인한다. 인접 CLI 대기 설명도 함께 확인한다.
2. 후보 준비/계약 검토의 실제 지급 근거가 수정 전문을 가리키는지 보고, 부족하면 작은 읽기 전용 호출로 확인한다. 미러 일치만으로 의미 정확성을 대신하지 않는다. F1의 재준비 일괄 지시가 사라지고 정상 개정·예외 재량·사용자 권위·독립 승인/연구 완료 구별이 유지되는지 판단한다.
3. 실제 변경 목록이 문서 범위에 머물며 이전 전체 리뷰의 코드·schema·저장·질문/개정 후속·공통 검사·Git/진단·Windows 안내 결론을 무효화하는 변화가 없는지 확인한다. 기존 전체 assessment의 R1~R7 결론과 한계를 이어서 이 수정판의 사용자 목표 충족 여부를 명시한다. 좁은 수정만 보고 전체를 새로 실행 검증했다고 주장하지 않는다.
4. 추가 실제 결함이 있다면 재현 조건·영향·정확한 파일/심볼·최소 후속을 기록한다. 선택 개선과 미확정 외부 원인을 별도 blocker로 만들지 않는다. 새 검증 장치를 추가하기 전에 기존 자료와 정적 대조로 판단할 수 있는지 살핀다.

기존 여러 판본 최신 관측 4618 passed/1 skipped는 마지막 전체 회귀 성공이 아니다. 최종 전체 회귀/T3 full/T5·실제 모델/scholarly/Lean/설치 복구 AI·미래 역할 준수/수학 연구 효능은 미확인이고 Windows symlink 1개는 권한 skip이다. 외부 Codex 목록 timeout의 네트워크/공급자 내부 원인 미확정과 Git 한 쌍의 한계도 유지한다. 전체 시험·역할 모집단/원자료 감사·성능 비교·live 호출을 일괄 반복하지 않는다. 새 불확실성이 있다면 그 동작만 필요한 최소 확인을 한다.

## 보고와 범위

writes는 빈 목록이다. 제품·서비스 state/queue·공용 문서·다른 task·원 연구/감사/HOLD/예약·graphify는 변경하거나 재개하지 않는다. 자기 task 디렉터리의 assessment.md에 F1 해소, 실제 지급, 전체 목표에 대한 결론과 직접/기존 근거의 구별·한계를 남긴다. report.json의 changes는 []이고 status는 리뷰 수행 완료 여부다. 프로젝트 완료/수용은 manager가 판단한다.

제출 전 `python C:\math\services\async-development\check.py report C:\math\.async\dm-flow-repair-20261021 final-contract-review`로 보고와 순변경 범위를 확인한다.
