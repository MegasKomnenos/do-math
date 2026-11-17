#!/bin/sh
# ZD 인계(2026-11-17) 「세션」 1: Z32 수정 뒤 띠 상자 계산 전체 재실행. 항목 자료 줄의 차례대로.
cd "C:/math/임시/주차함수_증명/원고_자료/세션_재계산/band_boxes" || exit 1
rm -f log_H_* log_FH_* box_H_* box_FH_* tail_H_* run_all_log.txt
rm -rf __pycache__
echo "start $(date +%T)"
python -I band_iv.py box H 12 25 6668 0 2 > /dev/null 2>&1 &
p0=$!
python -I band_iv.py box H 12 25 6668 1 2 > /dev/null 2>&1 &
p1=$!
wait $p0 $p1
echo "box H done $(date +%T)"
sh run_all.sh
echo "run_all done $(date +%T)"
python -I band_summary.py > band_result.txt 2>&1
python -I compare_record.py > compare_record_out.txt 2>&1
rm -rf __pycache__
echo "all done $(date +%T)"
ls -la
