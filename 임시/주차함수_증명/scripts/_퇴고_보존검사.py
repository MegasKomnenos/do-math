# -*- coding: utf-8 -*-
"""산문 퇴고 전후의 수학적 내용 보존 검사.
사용: python -I scripts/_퇴고_보존검사.py <기준 파일 또는 폴더> <퇴고본 파일 또는 폴더>
비교: (1) 수식 구간의 열($$…$$와 $…$; 순서 포함), (2) 진술 머리 줄 집합(`**종류 {{라벨}} … .**`의 지위 괄호까지),
(3) 라벨 `{{N:…}}`·식별자 `r[0-9a-f]{7}`·식 번호 `(N.M)`·숫자 토큰의 다중집합, (4) 칼표 † 수, (5) 「증명.」과 ∎의 수,
(6) 절 머리(`### `) 열. 모두 같으면 「차이 0」과 exit 0, 아니면 항목별 차이를 적고 exit 1.
폴더를 주면 같은 이름의 파일끼리 비교한다."""
import collections
import io
import os
import re
import sys

MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
HEAD_RE = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{[^}]+\}\}.*?\]\.\*\*", re.M)
LABEL_RE = re.compile(r"\{\{[0-9A-Za-z]+:[A-Za-z0-9\-]+\}\}")
RID_RE = re.compile(r"\br[0-9a-f]{7}\b")
EQNO_RE = re.compile(r"\(\d+\.\d+\)")
NUM_RE = re.compile(r"(?<![A-Za-z\\{])\d+(?:[.,]\d+)*")
SEC_RE = re.compile(r"^### .*$", re.M)


def features(text):
    maths = MATH_RE.findall(text)
    prose = MATH_RE.sub(" ", text)
    return {
        "수식 구간(열)": maths,
        "진술 머리(집합)": sorted(HEAD_RE.findall(text)),
        "라벨(다중집합)": sorted(LABEL_RE.findall(text)),
        "식별자(다중집합)": sorted(RID_RE.findall(text)),
        "식 번호(다중집합)": sorted(EQNO_RE.findall(prose)),
        "숫자 토큰(다중집합, 산문)": sorted(NUM_RE.findall(prose)),
        "칼표 수": [text.count("†")],
        "증명·∎ 수": [text.count("**증명"), text.count("∎")],
        "절 머리(열)": SEC_RE.findall(text),
    }


def diff(a, b):
    out = []
    fa, fb = features(a), features(b)
    for k in fa:
        if fa[k] != fb[k]:
            if "집합" in k:
                ca, cb = collections.Counter(fa[k]), collections.Counter(fb[k])
                gone = list((ca - cb).elements())[:12]
                new = list((cb - ca).elements())[:12]
                out.append(f"{k}: 사라짐 {len(list((ca-cb).elements()))} {gone} / 새로 생김 {len(list((cb-ca).elements()))} {new}")
            else:
                la, lb = fa[k], fb[k]
                i = next((t for t in range(min(len(la), len(lb))) if la[t] != lb[t]), min(len(la), len(lb)))
                out.append(f"{k}: 길이 {len(la)}→{len(lb)}, 첫 차이 자리 {i}: {str(la[i:i+1])[:160]} → {str(lb[i:i+1])[:160]}")
    return out


def main():
    base, cur = sys.argv[1], sys.argv[2]
    pairs = []
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            if name.endswith(".md") and os.path.exists(os.path.join(cur, name)):
                pairs.append((os.path.join(base, name), os.path.join(cur, name)))
    else:
        pairs.append((base, cur))
    bad = 0
    for pb, pc in pairs:
        a = io.open(pb, encoding="utf-8").read()
        b = io.open(pc, encoding="utf-8").read()
        d = diff(a, b)
        if d:
            bad += 1
            print("==", os.path.basename(pc))
            for line in d:
                print("  ", line)
    print("차이", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
