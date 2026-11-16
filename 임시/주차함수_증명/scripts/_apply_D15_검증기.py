# -*- coding: utf-8 -*-
"""D.{{D:critical-window-rig}}: 결과 줄의 첫 셀 구절 정정, 독립 재계산 줄에 네 항목 꺾쇠와 검증기 문장, 자료 줄에 파일 추가. 멱등."""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "부록D_장5A.md")
DRAFT = os.path.join(ROOT, "원고_자료", "세션_재계산", "critical_window", "D항목_초안.md")
TAG = "〔구현 다른 방법·인증서 판독; 범위 부분(참값 대조는 표본 상자·표본점)·전체(정정 후 여백의 부호); 산술 배정밀도 평가·40자리 평가·방향 반올림 구간; 자료 기록·이 글〕 "
OLD_RES = r"첫 셀에서 최대 $4.8\times10^{-3}$이나 그 셀의 여백은 $0.046$ 이상)"
NEW_RES = r"첫 셀에서 최대 $4.8\times10^{-3}$(A00)이나, 첫 셀의 정정 후 여백은 가장 작은 A20에서도 $0.0054$)"


def section(d, head, nxt):
    i = d.find(head); j = d.find(nxt, i + 1)
    return d[i + len(head):j].strip()


def main():
    d = io.open(DRAFT, encoding="utf-8").read()
    add_indep = section(d, "## 「독립 재계산」 줄 끝에 덧붙일 문장", "## 「자료」")
    add_data = section(d, "## 「자료」 줄 끝에 덧붙일 문장", "## 참고").lstrip("; ").rstrip(".")
    s = io.open(P, encoding="utf-8").read()
    i = s.find("### D.{{D:critical-window-rig}}"); j = s.find("\n### D.", i + 1)
    blk = s[i:j]
    if OLD_RES in blk:
        blk = blk.replace(OLD_RES, NEW_RES); print("결과 줄 정정")
    elif NEW_RES in blk:
        print("결과 줄 이미")
    else:
        print("결과 줄 앵커 없음"); sys.exit(1)
    lines = blk.split("\n")
    for k, l in enumerate(lines):
        if l.startswith("**독립 재계산.**"):
            body = l[len("**독립 재계산.**"):].strip()
            if body.startswith("〔"):
                print("꺾쇠 이미")
            else:
                body = TAG + body
            if "verify_margins.py" not in body:
                body = body.rstrip() + " " + add_indep
                print("검증기 문장 덧붙임")
            lines[k] = "**독립 재계산.** " + body
        if l.startswith("**자료.**") and "critical_window/verify_margins.py" not in l:
            lines[k] = l.rstrip().rstrip(".") + "; " + add_data + "."
            print("자료 덧붙임")
    blk = "\n".join(lines)
    s2 = s[:i] + blk + s[j:]
    io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
    print("기록함")


if __name__ == "__main__":
    main()
