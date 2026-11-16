# -*- coding: utf-8 -*-
"""수학 검사 3: 첨삭 뒤 수학 토큰 수정(멱등). 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
실행: python -I scripts/수학검사/3_fix.py
대상: 장v2/장3.md — 정리 {{3:old-3-5}}(누적 로그오목성의 실패)의 표지에서 「명제 {{3:old-3-1}}에 의존」을 뺀다.
      근거: 1.5절의 표지 규칙(「…에 의존」은 증명이 기대는 진술만 적는다). 정리 3-5는 증명 없는 유한 계산 진술이고,
      그 계산(부록 D.{{D:cumulative-logconcavity}}; 기록 r059f11e exposition.md §3.1)은 마지막 차 재귀(정리 2-6)만 쓰며
      해싱 극한(명제 3-1)을 쓰지 않는다. 의존지도 v2 70행도 입력 「—」로 적는다.
      장v2/부록D_장3.md는 수정 없음."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, "장v2", "장3.md")

# (앵커, 치환) — 모두 원시 문자열
EDITS = [
    (r"[계산 증거(정확 정수·유리수, binary64 사전 오차 해석), 명제 {{3:old-3-1}}에 의존; r059f11e].**",
     r"[계산 증거(정확 정수·유리수, binary64 사전 오차 해석); r059f11e].**"),
]

def main():
    s = io.open(TARGET, encoding="utf-8").read()
    changed = 0
    for old, new in EDITS:
        n_old, n_new = s.count(old), s.count(new)
        if n_old == 0 and n_new == 1:
            print(f"이미 적용됨: {old!r}")
            continue
        if n_old != 1:
            print(f"앵커 수 {n_old} != 1, 건너뜀: {old!r}"); continue
        s = s.replace(old, new, 1); changed += 1
        print(f"치환: {old!r} -> {new!r}")
    if changed:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(s)
    print("치환 수", changed)

if __name__ == "__main__":
    main()
