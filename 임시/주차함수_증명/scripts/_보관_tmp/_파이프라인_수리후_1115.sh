#!/usr/bin/env bash
# 수리 뒤 파생물 재생성과 검사 (2026-11-15). 저장소 루트(임시/주차함수_증명)에서 실행.
# 사용: bash scripts/_보관_tmp/_파이프라인_수리후_1115.sh [--no-katex]
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/../.." || exit 1
echo "== $(date '+%H:%M:%S') 장부 4절 이름 동기화"; python -I scripts/_sync_4절이름.py
echo "== 11.2 표 5열(꺾쇠) 동기화"; python -I scripts/_sync_11_2꺾쇠.py
echo "== 11.2 표 6열(독립 재계산) 동기화"
LABELS=$(grep -o '^| 부록 D.{{D:[A-Za-z0-9-]*}}' 장v2/장10.md | sed 's/.*{{D:\(.*\)}}/\1/' | tr '\n' ' ')
python -I scripts/_sync_11_2행.py $LABELS | tail -3
echo "== 재실행표"; python -I scripts/_gen_재실행표.py | tail -2
echo "== 조립"; python -I scripts/조립_v2.py | tail -6
echo "== 의존지도·대응표"; python -I scripts/_gen_의존지도_1절.py | tail -4
echo "== 불변식"; python -I scripts/불변식_v2.py | tail -4
echo "== 수식 괄호"; python -I scripts/_check_math_braces.py | tail -2
echo "== 지위 서식"; python -I scripts/_check_지위서식.py | tail -2
echo "== 자리표시자"; python -I scripts/_check_자리표시자.py | tail -2
echo "== 라벨 뒤 조사"; python -I scripts/_check_조사.py | tail -2
echo "== 잔재 검사"; python -I scripts/수학검사2/정합검토_잔재검사_1114.py | tail -4
echo "== 자료묶음 --dry"; python -I scripts/자료묶음_v2.py --dry | tail -3
if [ "${1:-}" != "--no-katex" ]; then
  LOG="대조v2/_katex_$(date '+%H%M').log"
  echo "== KaTeX (배경) -> $LOG"; (python -I scripts/_katex_check.py > "$LOG" 2>&1 &)
fi
echo "== 끝 $(date '+%H:%M:%S')"
