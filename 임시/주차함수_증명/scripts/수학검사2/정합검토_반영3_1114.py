# -*- coding: utf-8 -*-
"""잔재 검사(정합검토_잔재검사_1114.py)가 낸 것의 정리. 멱등. 사용: python -I scripts/수학검사2/정합검토_반영3_1114.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRY = "--dry" in sys.argv
EDITS = [
    ("장v2/장6.md", r"**증명.** 사슬의 초과열이 $(q_1,\dots,q_L)$", r"**증명.** 사슬의 초과 수열이 $(q_1,\dots,q_L)$"),
    ("장v2/장7B.md", r"자르는 자리의 비용 $\mathrm{up}_n(\mathfrak l)$", r"자르는 크기의 비용 $\mathrm{up}_n(\mathfrak l)$"),
    ("장v2/장7B.md", r"그 대가로 자르는 자리의 비용을 생존 확률의", r"그 대가로 자르는 크기의 비용을 생존 확률의"),
    ("장부_v2.md", r"5B `{{5:old-5-23}}`의 $\mathcal C$와 겹쳐 로마체", r"5B 5.5절의 고정 사슬 $\mathcal C$와 겹쳐 로마체"),
    ("장부_v2.md", r"| 5.5 `{{5:old-5-23}}`–`{{5:old-5-30}}` 증명 |", r"| 5.5 `{{5:stirling-bor}}`–`{{5:old-5-30}}` 증명 |"),
    ("장v2/장1.md", r"binary64 사전 오차 해석이나 인증 아님 등급에 기대는 입력은 없다", r"binary64 사전 오차 해석이나 $\langle$정밀도$\rangle$ 평가 등급에 기대는 입력은 없다"),
    ("장v2/장11.md", r"넷째인 인증 아님 등급은 그 보증이 없는 등급이다", r"넷째인 $\langle$정밀도$\rangle$ 평가 등급은 그 보증이 없는 등급이다"),
    ("장부_v2.md", r"binary64 사전 오차 해석, 평가·인증 아님) | 1.5 |", r"binary64 사전 오차 해석, $\langle$정밀도$\rangle$ 평가) | 1.5 |"),
    ("장v2/부록D_장9.md", r"다시 계산해 칸 $20000$개에서", r"다시 계산해 구간 $20000$개에서"),
    ("장부_v2.md", r"(지정 사슬 크기열;", r"(지정 사슬 크기 수열;"),
    ("장v2/부록C.md", r"(지정 사슬 크기열;", r"(지정 사슬 크기 수열;"),
    ("구조표_v2.md", r"작은 행의 증인 위치 경계(명제;", r"작은 행의 증인 위치 상계(명제;"),
    ("장v2/장5A.md", r"그러면 $k=\ell+1\ge25001$이 되어 뒤의 정리들의 시작점이 자동으로 맞는다.", r"그러면 $k=\ell+1\ge25001$이다."),
    ("장v2/장5A.md", r"재배열을 틀로 삼아 $\mathsf W^\sharp$를 직접 증명하고, 5.6절은 다음의 더 강한 두 항 부등식, 곧 동률 쪽과 막힘 쪽의 두 항만 견주는 부등식을 증명한다.", r"재배열을 틀로 삼아 $\mathsf W^\sharp$를 직접 증명한다."),
]
changed = {}
for rel, old, new in EDITS:
    p = os.path.join(ROOT, rel)
    s = changed.get(rel) or io.open(p, encoding="utf-8").read()
    c = s.count(old)
    if c == 1:
        changed[rel] = s.replace(old, new)
    elif c == 0 and new in s:
        pass
    else:
        print(f"[앵커 {c}] {rel}: {old[:60]}")
for rel, s in changed.items():
    if not DRY:
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
print("고친 파일", len(changed), "(dry)" if DRY else "")
