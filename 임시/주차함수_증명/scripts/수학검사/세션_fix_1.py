# -*- coding: utf-8 -*-
"""수학 검사 회수 뒤 세션이 직접 고치는 문장 수준의 수학 오류 셋(작업자는 토큰만 고치므로 보고로 올린 것).
(1) 장3 261행: 첨삭이 덧붙인 「우변은 n에 대해 감소하므로」는 거짓(λ=⌈3n/4⌉/n이 진동) → 증명(243–245행)의 실제 논법대로.
(2) 장3 135행 정리 old-3-4 표지: 증명이 쓰지 않는 「·정리 {{3:old-3-3}}」 의존 제거(1.5절 규칙; 의존지도 69행 입력 「—」).
(3) 장5B 80행: 첨삭이 뒤집은 「IH는 꼭대기 쪽에서만 쓰인다」 → 기준 판의 뜻(두 하계 모두; 꼬리 창 쪽은 tail_{t_0-1}(y)≥0을 버리는 데 씀). 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EDITS = {
    os.path.join(ROOT, "장v2", "장3.md"): [
        ("$n=1000$에서 세 수 $751/1000$, $1/31$, $1/1000$을 넣은 $J=8$의 우변이 $1/2$보다 작고, 우변은 $n$에 대해 감소하므로 그 위의 모든 $n$이 덮인다.",
         "우변은 $\\lambda$, $n^{-1/2}$, $n^{-1}$ 각각에 대해 증가하고 $n\\ge1000$에서 이 세 양은 각각 $751/1000$, $1/31$, $1/1000$ 이하이므로, 이 세 수를 넣은 $J=8$의 우변이 $1/2$보다 작다는 것 하나로 $n\\ge1000$ 전체가 덮인다."),
        ("시작점 비명시, 명제 {{3:old-3-1}}·정리 {{3:old-3-3}}에 의존; r81e7051, r15524fd].**",
         "시작점 비명시, 명제 {{3:old-3-1}}에 의존; r81e7051, r15524fd].**"),
    ],
    os.path.join(ROOT, "장v2", "장5B.md"): [
        ("가정 $\\mathrm{IH}(n,y)$는 두 하계 가운데 꼭대기 쪽에서만 쓰인다. 꼬리 창에서는 $x_t(y)$의 부호를 통제할 수 없어 음의 부분만 세고, 꼭대기에서는 $x_t(y)\\ge c^{(2)}_{t-1}(y)/t\\ge0$이 성립하기 때문이다.",
         "가정 $\\mathrm{IH}(n,y)$는 두 하계 모두에 쓰인다. 꼭대기 쪽에서는 $x_t(y)\\ge c^{(2)}_{t-1}(y)/t\\ge0$을 주고, 꼬리 창 쪽에서는 꼬리합을 $\\mathrm{tail}_{t_0-1}(y)\\ge0$으로 자르는 데 쓰인다. 꼬리 창 안에서는 $x_t(y)$의 부호를 통제할 수 없어 음의 부분만 센다."),
    ],
}
for p, edits in EDITS.items():
    s = io.open(p, encoding="utf-8").read(); n = 0
    for old, new in edits:
        c = s.count(old)
        if c == 1:
            s = s.replace(old, new); n += 1
        elif new in s:
            pass
        else:
            print("앵커 수", c, ":", os.path.basename(p), old[:40])
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(os.path.basename(p), "고침", n)
