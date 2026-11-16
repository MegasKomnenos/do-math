# -*- coding: utf-8 -*-
"""편집 전후의 수학 내용 보존 검사. 사용: python -I 보존검사.py <기준 폴더> <현재 폴더> [파일명...]
비교: 수식 구간의 열($$…$$, $…$), 진술 머리 집합, 라벨·식별자·부록 D 참조·식 번호의 다중집합, † 수, 증명·∎ 수, 절 머리 열.
수식 열이 다르면 첫 차이 자리와 양쪽 수식을 보인다."""
import collections, io, os, re, sys

MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
HEAD_RE = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{[^}]+\}\}.*$", re.M)
LABEL_RE = re.compile(r"\{\{[0-9A-Za-z]+:[A-Za-z0-9\-]+\}\}")
RID_RE = re.compile(r"\br[0-9a-f]{7}\b")
EQNO_RE = re.compile(r"\((\d+\.\d+)\)")
SEC_RE = re.compile(r"^#{2,4} .*$", re.M)

def feats(t):
    maths = MATH_RE.findall(t)
    prose = MATH_RE.sub(" ", t)
    return {
        "수식(열)": maths,
        "진술 머리(집합)": sorted(HEAD_RE.findall(t)),
        "라벨(다중집합)": sorted(LABEL_RE.findall(t)),
        "식별자(다중집합)": sorted(RID_RE.findall(t)),
        "식 번호(다중집합)": sorted(EQNO_RE.findall(prose)),
        "칼표 수": [t.count("†")],
        "증명·∎ 수": [t.count("**증명"), t.count("∎")],
        "절 머리(열)": SEC_RE.findall(t),
    }

def diff(a, b):
    out = []
    fa, fb = feats(a), feats(b)
    for k in fa:
        if fa[k] == fb[k]:
            continue
        if "집합" in k:
            ca, cb = collections.Counter(fa[k]), collections.Counter(fb[k])
            gone, new = list((ca - cb).elements()), list((cb - ca).elements())
            out.append(f"{k}: 사라짐 {len(gone)} {gone[:8]} / 새로 생김 {len(new)} {new[:8]}")
        elif k == "수식(열)":
            la, lb = fa[k], fb[k]
            ca, cb = collections.Counter(la), collections.Counter(lb)
            gone, new = list((ca - cb).elements()), list((cb - ca).elements())
            if not gone and not new:
                out.append(f"{k}: 다중집합은 같고 순서만 다름(길이 {len(la)})")
            else:
                out.append(f"{k}: 길이 {len(la)}→{len(lb)}; 사라진 수식 {len(gone)}: {gone[:6]} / 새 수식 {len(new)}: {new[:6]}")
        else:
            out.append(f"{k}: {fa[k][:5]} → {fb[k][:5]}")
    return out

def main():
    base, cur = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or sorted(n for n in os.listdir(base) if n.endswith(".md"))
    bad = 0
    for name in names:
        a = io.open(os.path.join(base, name), encoding="utf-8").read()
        b = io.open(os.path.join(cur, name), encoding="utf-8").read()
        d = diff(a, b)
        print("==", name, "차이 없음" if not d else "")
        for line in d:
            bad += 1
            print("  ", line)
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
