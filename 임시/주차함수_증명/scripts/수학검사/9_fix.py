# -*- coding: utf-8 -*-
"""태그 9 수학 검사의 수정 스크립트(멱등). 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
사용: python -I scripts/수학검사/9_fix.py
수정:
  (1) 9.4절 교차항의 글자 $\\mathcal X_n$(아홉 자리) -> $\\mathcal O_n$ (10.1절 예산 분해 몫 $\\mathcal X_n$과의 충돌 해소)
  (2) 65행 「$g$가 순증가하므로」 -> 「$g$가 엄격히 증가하므로」 (보조정리 {{2:old-2-26}}(가)는 엄격 증가를 준다)
  (3) 663행 「2.9절의 무게 $1/(t+1)^t$로 잰」 -> 「6.4절의 무게 $1/t^{t-1}$로 잰」
      (나무 곡률 $x_t(k)=\\delta_t/t^{t-1}$; 무게의 이름 「평평한 무게」는 6.4절 489행이 정한다)
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "장v2", "장9.md")

s = io.open(PATH, encoding="utf-8", newline="").read()  # 줄끝을 그대로 보존한다
orig = s
log = []


def replace_once(text, old, new, name):
    n = text.count(old)
    if n == 0:
        if text.count(new) >= 1:
            log.append(f"[{name}] 이미 적용됨(앵커 없음, 새 토큰 있음)")
            return text
        raise SystemExit(f"[{name}] 앵커를 찾지 못함: {old!r}")
    if n > 1:
        raise SystemExit(f"[{name}] 앵커가 {n}번 나타남(정확히 한 번이어야 함): {old!r}")
    log.append(f"[{name}] 치환 1회")
    return text.replace(old, new)


# (1) 교차항 글자. 아홉 자리 전부가 같은 토큰이므로, 수가 정확히 9이고 다른 \mathcal X 쓰임이 없음을 확인한 뒤 전부 바꾼다.
OLD1 = r"\mathcal X_n"
NEW1 = r"\mathcal O_n"
n_old = s.count(OLD1)
n_anyX = len(re.findall(r"\\mathcal X(?![a-zA-Z])", s))
n_anyO = len(re.findall(r"\\mathcal O(?![a-zA-Z])", s))
if n_old == 0 and s.count(NEW1) == 9:
    log.append("[1 교차항] 이미 적용됨(\\mathcal O_n 9자리)")
elif n_old == 9 and n_anyX == 9 and n_anyO == 0:
    lines = [i + 1 for i, l in enumerate(s.split("\n")) if OLD1 in l]
    s = s.replace(OLD1, NEW1)
    log.append(f"[1 교차항] \\mathcal X_n -> \\mathcal O_n 9회 치환(행 {lines})")
else:
    raise SystemExit(f"[1 교차항] 예상과 다른 상태: X_n={n_old}, 모든 \\mathcal X={n_anyX}, \\mathcal O={n_anyO}")

# (2) 순증가 -> 엄격히 증가
s = replace_once(
    s,
    r"(1) $S_L\le m<m+1$이고 $g$가 순증가하므로(보조정리 {{2:old-2-26}})",
    r"(1) $S_L\le m<m+1$이고 $g$가 엄격히 증가하므로(보조정리 {{2:old-2-26}})",
    "2 엄격 증가",
)

# (3) 평평한 무게의 식과 절 참조
s = replace_once(
    s,
    r"평평하다는 말은 2.9절의 무게 $1/(t+1)^t$로 잰 꼬리합이라는 뜻이다.",
    r"평평하다는 말은 6.4절의 무게 $1/t^{t-1}$로 잰 꼬리합이라는 뜻이다.",
    "3 평평한 무게",
)

if s != orig:
    io.open(PATH, "w", encoding="utf-8", newline="").write(s)
    log.append(f"저장: {PATH}")
else:
    log.append("변경 없음(이미 적용됨)")
print("\n".join(log))
