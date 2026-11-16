# -*- coding: utf-8 -*-
"""극 영역 488블록 재인증(θ 지표 k−ℓ) 통과 뒤 D.{{D:polar-blocks-488}}를 맞춘다: (ㄹ)의 지표 식을 원천 합의 지표로,
독립 재계산 줄에 이 글의 재인증을, 자료 줄에 재인증 파일을. 멱등. 사용: python scripts/_fix_D32_재인증.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
P = os.path.join(ROOT, "장v2", "부록D_장7A.md")

OLD_R = (r"$j:=k+i-\ell\in[k_1+i-\ell,k_2+i-\ell]$(코드의 지표. 원천 합의 $\theta$ 지표는 $k+i-m=k-\ell$이므로 코드는 $\theta_j$의 두 경계를 $i$만큼 큰 $j$에서 읽는다. "
         r"하계 $e^{5/(12j)}$는 그래서 더 작아 그대로 하계이고, 상계 $1+0.7/j$는 참 지표의 것보다 상대 $0.7i/((k-\ell)(k+i-\ell))\le0.6/k$만큼 작을 수 있다. "
         r"이 차이가 블록의 결정 여유 안에 드는지는 이 글에서 확인하지 않았다)에서")
NEW_R = r"$j:=k-\ell\in[k_1-\ell,k_2-\ell]$에서"

ADD_INDEP = (r" 이 글을 쓰며 $488$블록 전부를 다시 인증했다(`원고_자료/세션_재계산/r89eb039_polar/`). 모두 통과했고, "
             r"블록의 결정 여유 $\eta$와 $V\sqrt k$는 기록의 값과 상대 $3\times10^{-4}$ 안에서 같다.")
ADD_DATA = (r"; `원고_자료/세션_재계산/r89eb039_polar/recert.py`, `sparts.py`, `fixed/cert_ia2.py`, `inputs/*.jsonl`(기록의 블록 입력), "
            r"`NEW_recert_*.jsonl`, `NEW_adaptive_2087_5000.jsonl`과 같은 이름의 `.log`(재인증 결과)")


def main():
    s = io.open(P, encoding="utf-8").read()
    head = "### D.{{D:polar-blocks-488}}"
    i = s.find(head)
    j = s.find("\n### D.", i + 1)
    if i < 0:
        print("D.32 블록 없음"); sys.exit(1)
    blk = s[i:j] if j > 0 else s[i:]
    if OLD_R in blk:
        blk = blk.replace(OLD_R, NEW_R, 1); print("(ㄹ) 지표 식 교체")
    elif NEW_R in blk:
        print("(ㄹ) 이미")
    else:
        print("(ㄹ) 앵커 없음"); sys.exit(1)
    lines = blk.split("\n")
    for k, l in enumerate(lines):
        if l.startswith("**독립 재계산.**"):
            if ADD_INDEP.strip() not in l:
                lines[k] = l.rstrip() + ADD_INDEP; print("독립 재계산 덧붙임")
            else:
                print("독립 재계산 이미")
        if l.startswith("**자료.**"):
            if "r89eb039_polar/recert.py" not in l:
                lines[k] = l.rstrip().rstrip(".") + ADD_DATA; print("자료 덧붙임")
            else:
                print("자료 이미")
    blk = "\n".join(lines)
    s2 = s[:i] + blk + (s[j:] if j > 0 else "")
    if DRY:
        print("(dry) 쓰지 않음"); return
    io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
    print("기록함:", P)


if __name__ == "__main__":
    main()
