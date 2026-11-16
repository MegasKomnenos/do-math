# -*- coding: utf-8 -*-
"""D.32(polar-blocks-488) 마무리: (1) 기록 코드의 반올림 부풀림 인자 (1±10^-13), (1±10^-12), (1±10^-9)를 식에서 걷어 내고 알고리즘 줄에 한 문장으로 남김,
(2) 「완료되지 않음」 괄호 삭제와 마지막 블록 대조 문장·자료 추가(블록 대조 몫의 덧붙임), (3) 명제 polar-W 머리의 등급 낱말 교체. 멱등."""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "부록D_장7A.md")
H = os.path.join(ROOT, "장v2", "장7A.md")
DRY = "--dry" in sys.argv

AUDIT = (r" 이 글을 쓰며 다시 인증한 $[9843156,10^7]$ 블록의 경계를 기록의 검토가 다른 다섯 블록에 쓴 방법 그대로 블록 안 세 $k$($9843156$, $9921578$, $10^7$)의 참값과 $135$개 항목 대조했다. "
         r"$135$개 모두 경계가 참값을 담았고, 가장 얇은 상대 여유는 $k=10^7$에서 $n\le k$ 부분의 2차 모멘트 상계가 남긴 $6.3\times10^{-7}$이다. 참값 계산의 오차(항별 $1.5\times10^{-14}$ 이하, 구적·보간 $1.3\times10^{-12}$ 이하)는 이 여유보다 다섯 자리 이상 작다.")
AUDIT_FILES = (r"; `원고_자료/세션_재계산/r89eb039_polar_block_audit/block_vs_truth_9843156.py`, `bvt_block_9843156_10000000.txt`, `bvt_block_9843156_10000000.json`, "
               r"`truth_accuracy_check.py`, `truth_accuracy_check.json`(블록 $[9843156,10^7]$의 참값 대조)")
RECORD_NOTE = r" 기록의 코드는 같은 식의 양의 항 합과 곱에 $(1\pm10^{-13})$, $(1\pm10^{-12})$, $(1\pm10^{-9})$의 부풀림 인자를 곱하고 초월함수의 결과를 $4$ ulp 밀어 반올림을 덮었다."


def main():
    s = io.open(P, encoding="utf-8").read()
    i = s.find("### D.{{D:polar-blocks-488}}"); j = s.find("\n### D.", i + 1)
    blk = s[i:j]
    # (1) 부풀림 인자
    before = blk
    blk = blk.replace(r"\frac{(1-10^{-13})^2}{k_2}", r"\frac{1}{k_2}")
    blk = blk.replace(r"\Bigl((1+10^{-13})^2\sum", r"\Bigl(\sum")
    n_tok = len(re.findall(r"\(1[+-]10\^\{-(?:13|12|9)\}\)", blk))
    blk = re.sub(r"\(1[+-]10\^\{-(?:13|12|9)\}\)", "", blk)
    print("부풀림 인자 제거", n_tok, "곳 (+제곱 둘)" if before != blk else "")
    lines = blk.split("\n")
    for k, l in enumerate(lines):
        if l.startswith("**알고리즘.**") and "부풀림 인자를 곱하고" not in l:
            lines[k] = l.rstrip() + RECORD_NOTE; print("알고리즘 줄에 기록 코드 문장 추가")
        if l.startswith("**독립 재계산.**"):
            old = r"($[9843156,10^7]$ 블록의 블록 수준 대조는 완료되지 않음)"
            if old in l:
                l = l.replace(old, ""); print("「완료되지 않음」 괄호 삭제")
            if "block_vs_truth" not in l and "135$개 모두 경계가 참값을 담았고" not in l:
                l = l.rstrip() + AUDIT; print("블록 대조 문장 추가")
            lines[k] = l
        if l.startswith("**자료.**") and "r89eb039_polar_block_audit" not in l:
            lines[k] = l.rstrip().rstrip(".") + AUDIT_FILES + "."; print("자료에 대조 파일 추가")
    blk = "\n".join(lines)
    s2 = s[:i] + blk + s[j:]
    # (3) 머리
    h = io.open(H, encoding="utf-8").read()
    old_h = "(극 영역의 왼쪽 증가; 기록 [r89eb039]의 주정리와 §7) [비형식 증명, 계산 보조(binary64 사전 오차 해석); r89eb039].**"
    new_h = "(극 영역의 왼쪽 증가; 기록 [r89eb039]의 주정리와 §7) [비형식 증명, 계산 보조(방향 반올림 구간); r89eb039].**"
    if old_h in h:
        h = h.replace(old_h, new_h); print("머리 등급 교체")
    elif new_h in h:
        print("머리 이미")
    else:
        print("머리 앵커 없음"); sys.exit(1)
    if DRY:
        print("(dry)"); return
    io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
    io.open(H, "w", encoding="utf-8", newline="\n").write(h)
    print("기록함")


if __name__ == "__main__":
    main()
