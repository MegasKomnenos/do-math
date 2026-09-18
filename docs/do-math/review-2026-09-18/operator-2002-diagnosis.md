# 독립 운영 진단 (2026-09-18T11:02Z)

관찰: status=waiting, snapshot c2021a0f…, active_execution 없음, HOLD·user_pause 없음, engine 예약 작업 Ready(last_result 0, 실행 중 아님).

waiting_actions 19건 중 16건(06:33–06:37Z 발생)은 모두 Claude CLI 429
"You've hit your session limit · resets 6:20pm (Asia/Seoul)"(=09:20Z)로 끝났다.
근거: work-v2/runs/<EX>/evidence/stdout.jsonl 의 api_error_status=429, duration_ms≈0.5–1.4s(KEABN 109s, KGK6D 10s).
대상: KEABN(research_work 7XQZ), KGK6D(prep ARGT), KJGDK(prep FGRJ), KKT4Z(prep), KHC1Z(contract review FGRJ),
KGWY0·KHZGN·KPA1A(research_plan) 및 이들의 자동 운영 점검 8건(KJZHN, KKC6D, KMDME, KMZQG, KN84S, KNQZH, KPKB1, KQASA).
직전 독립 운영 실행 07:02Z, 09:02Z도 같은 429로 모델 시작 전 실패했다(operator/runs/…/evidence/stdout.jsonl).

판단: 원인은 수학·계약·입력 결함이 아니라 공급자 세션 한도다. 한도 초기화 시각(09:20Z)이 지났고, 이 운영 실행 자체가 같은 계정으로 정상 동작한다.
나머지 3건(output_validation, 'a decision dependency changed', 04:2x–04:5x)은 과거 계획 진단 경합의 잔여로 이번 조치 대상이 아니다.

코드 근거: engine._resolve_failed_actions 는 role/target/stage 등이 같은 후속 실행 성공 시 해당 waiting action을 모두 해소한다.
따라서 research_plan 실패 3건은 계획 1건 재시도로, 자동 운영 점검 실패 8건은 같은 target의 새 운영 점검 성공으로 해소된다.

구현 관찰(미수리): 429 rate_limit 을 일반 execution_failure 로 분류해 자동 운영 점검까지 연쇄 실패시키고, 한도 초기화 뒤에도 수동 진단 요청 없이는 재개되지 않는다.
공급자 한도를 capacity_waiting(초기화 시각까지)으로 다루는 수리는 엔진 스케줄링 변경이라 이번 실행 범위에서 하지 않고 질문으로 남긴다.
