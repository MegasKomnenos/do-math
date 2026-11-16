# -*- coding: utf-8 -*-
"""조립본에서 진술 번호·부록 D 번호·식 번호 「(7.21)」 바로 뒤의 조사가 번호의 받침과 맞는지 센다.

사용: python -I scripts/_check_조사.py [원고.md]
규칙은 scripts/조립_v2.py의 particle_for와 같다(끝 숫자 읽기: 일·이·삼·사·오·육·칠·팔·구, 끝이 0이면 십).
출력: 어긋난 자리(행 | 앞뒤 글)와 총수. 어긋남이 없으면 0을 적고 종료 코드 0, 있으면 1.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from 조립_v2 import particle_for  # noqa: E402

NUM_RE = re.compile(
    r"(?:(?:정의|정리|명제|보조정리|따름정리) \d+\.\d*(\d)|부록 D\.\d*(\d)|\(\d+\.\d*(\d)\))"
    r"(으로|이다|이라|이고|이며|이면|이나|을|를|이|가|은|는|과|와|로|다|라|고|며|면|나)"
    r"(?=$|[^가-힣]|도|만|는|부터|써|의|까지|서)")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "원고.md")
    bad = 0
    for i, ln in enumerate(io.open(path, encoding="utf-8"), 1):
        for m in NUM_RE.finditer(ln):
            digit = m.group(1) or m.group(2) or m.group(3)
            particle = m.group(4)
            want = particle_for(digit, particle)
            if want != particle:
                bad += 1
                s = max(0, m.start() - 12)
                print(f"{i} | …{ln[s:m.end() + 6].rstrip()}… | {particle}→{want}")
    print(f"어긋난 조사 {bad}개 ({os.path.relpath(path, ROOT)})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
