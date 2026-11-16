#!/bin/bash
# run_ct.sh가 A5 뒤에 띄울 A3 프로세스(--low, BelowNormal)를 감지해 Normal(32)로 올리고 끝난다. 60초마다 확인, 최대 7일.
export MSYS_NO_PATHCONV=1
LOG="$(dirname "$0")/_watch_A3_priority.log"
echo "$(date '+%F %T') watcher start" >> "$LOG"
for i in $(seq 1 10080); do
  PID=$(wmic process where "Name='python.exe' and CommandLine like '%sweep_nb A3%'" get ProcessId /format:value 2>/dev/null | grep = | cut -d= -f2 | tr -d '\r' | head -1)
  if [ -n "$PID" ]; then
    wmic process where "ProcessId=$PID" CALL setpriority 32 >/dev/null 2>&1
    PR=$(wmic process where "ProcessId=$PID" get Priority /format:value | grep = | cut -d= -f2 | tr -d '\r')
    echo "$(date '+%F %T') A3 pid=$PID priority=$PR" >> "$LOG"
    exit 0
  fi
  sleep 60
done
echo "$(date '+%F %T') watcher timeout" >> "$LOG"
