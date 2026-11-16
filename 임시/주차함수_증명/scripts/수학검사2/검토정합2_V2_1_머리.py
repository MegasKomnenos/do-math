# -*- coding: utf-8 -*-
"""정합 검토 2차 V2: 진술 머리 대조·의존 선언·작성자 판단·† 검사. 읽기만 한다.
사용: python -I scripts/수학검사2/검토정합2_V2_1_머리.py"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CUR = os.path.join(ROOT, "장v2")
OLD = os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114")

LABEL_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DEFER_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*")
BR_RE = re.compile(r"\[([^\]]*)\]\.\*\*")


def chapter_files(base):
    out = []
    for i in range(1, 12):
        whole = f"장{i}.md"
        if os.path.exists(os.path.join(base, whole)):
            out.append(whole)
            continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(rf"장{i}[A-Z]\.md", n)))
    return out


def parse(base, fallback=None):
    """진술 사전. 본문 = 머리 다음 줄부터 첫 ∎(그 줄 포함) 또는 다음 머리/미룬 증명/### 까지. 미룬 증명 단락을 합친다."""
    stmts = {}
    defers = []
    order = 0
    for name in chapter_files(fallback or base):
        p = os.path.join(base, name)
        if not os.path.exists(p):
            p = os.path.join(fallback, name)
        L = io.open(p, encoding="utf-8").read().split("\n")
        marks = []
        for i, ln in enumerate(L):
            if ln.startswith("### ") or ln.startswith("## "):
                marks.append((i, "sec", None))
            elif DEFER_RE.match(ln):
                d = DEFER_RE.match(ln); marks.append((i, "defer", f"{d.group(2)}:{d.group(3)}"))
            elif HEAD_RE.match(ln):
                h = HEAD_RE.match(ln); marks.append((i, "head", f"{h.group(2)}:{h.group(3)}"))
        mset = {i: k for i, k, _ in marks}
        for i, kind, key in marks:
            if kind == "sec":
                continue
            # 전체 범위(다음 머리까지)
            end_all = len(L)
            for i2, k2, _ in marks:
                if i2 > i and k2 in ("head", "defer", "sec"):
                    end_all = i2; break
            # 엄격 범위(첫 ∎까지)
            end_strict = end_all
            for t in range(i + 1, end_all):
                if "∎" in L[t]:
                    end_strict = t + 1; break
            if "∎" in L[i]:
                end_strict = i + 1
            body_strict = L[i + 1:end_strict]
            body_all = L[i + 1:end_all]
            if kind == "head":
                order += 1
                h = HEAD_RE.match(L[i])
                br = BR_RE.search(L[i])
                stmts[key] = dict(kind=h.group(1), file=name, line=i + 1, order=order, head=L[i],
                                  bracket=br.group(1) if br else "",
                                  body_strict=list(body_strict), body_all=list(body_all),
                                  head_labels=set(f"{a}:{b}" for a, b in LABEL_RE.findall(L[i])) - {key})
            else:
                defers.append((key, name, i + 1, [L[i]] + body_strict, [L[i]] + body_all))
    for key, fname, ln, bs, ba in defers:
        if key in stmts:
            stmts[key]["body_strict"] += bs
            stmts[key]["body_all"] += ba
            stmts[key].setdefault("defer", []).append(f"{fname}:{ln}")
    for k, s in stmts.items():
        s["labels_strict"] = set(f"{a}:{b}" for ln in s["body_strict"] for a, b in LABEL_RE.findall(ln)) - {k}
        s["labels_all"] = set(f"{a}:{b}" for ln in s["body_all"] for a, b in LABEL_RE.findall(ln)) - {k}
        s["dagger_strict"] = any("†" in ln for ln in s["body_strict"])
        s["dagger_all"] = any("†" in ln for ln in s["body_all"])
    return stmts


def deps_of(bracket):
    """머리 괄호의 「…에 의존」 선언에서 라벨 집합(부분 의존 포함)."""
    status = bracket.split(";")[0]
    out = set()
    for m in re.finditer(r"((?:[^,\[\];]*?)에 의존)", status):
        out |= set(f"{a}:{b}" for a, b in LABEL_RE.findall(m.group(1)))
    return out


def is_X(s):
    """결정 60의 X 범위: 계산 증거·계산 보조·문헌 인용·…에 의존 을 가진 진술."""
    st = s["bracket"].split(";")[0]
    return any(w in st for w in ("계산 증거", "계산 보조", "문헌 인용", "에 의존"))


def main():
    cur = parse(CUR)
    old = parse(OLD, fallback=CUR)
    print(f"현재 진술 {len(cur)}, 이전 진술 {len(old)}")
    # 1. 머리 차이
    print("\n== (1) 머리가 바뀐 진술 ==")
    nchg = 0
    for k in sorted(cur, key=lambda k: cur[k]["order"]):
        if k in old and old[k]["head"] != cur[k]["head"]:
            nchg += 1
            print(f"\n[{cur[k]['file']}:{cur[k]['line']}] {k}\n  전: {old[k]['head'][:400]}\n  후: {cur[k]['head'][:400]}")
    print(f"\n머리 바뀐 진술 {nchg}; 지워진 진술 {sorted(set(old)-set(cur))}; 새 진술 {sorted(set(cur)-set(old))}")
    # 2. 의존 선언 검사
    print("\n== (2) 「…에 의존」 선언 검사(현재) ==")
    for k in sorted(cur, key=lambda k: cur[k]["order"]):
        s = cur[k]
        decl = deps_of(s["bracket"])
        used_strict = s["labels_strict"]
        used_all = s["labels_all"]
        # 증명이 쓰는 X-형 진술 가운데 선언에서 빠진 것
        xs_used = {u for u in used_strict if u in cur and is_X(cur[u]) and cur[u]["kind"] != "정의"}
        missing = xs_used - decl
        not_used = decl - used_strict
        not_used_all = decl - used_all
        not_X = {d for d in decl if d in cur and not is_X(cur[d])}
        undefined = {d for d in decl if d not in cur}
        if decl or missing:
            flags = []
            if missing:
                flags.append(f"선언 빠짐(본문이 쓰는 X형): {sorted(missing)}")
            if not_used:
                flags.append(f"선언했으나 엄격 본문에 없음: {sorted(not_used)}" + (f" (넓은 본문에도 없음: {sorted(not_used_all)})" if not_used_all else " (넓은 본문엔 있음)"))
            if not_X:
                flags.append(f"선언한 것이 X 범위 밖: {sorted(not_X)}")
            if undefined:
                flags.append(f"선언한 라벨이 없음: {sorted(undefined)}")
            if flags:
                print(f"[{s['file']}:{s['line']}] {k} [{s['bracket'][:120]}]")
                for f in flags:
                    print("   -", f)
    # 3. 작성자 판단 ↔ †
    print("\n== (3) 작성자 판단 ↔ † ==")
    for k in sorted(cur, key=lambda k: cur[k]["order"]):
        s = cur[k]
        flag = "작성자 판단" in s["bracket"]
        if flag and not s["dagger_strict"]:
            print(f"[{s['file']}:{s['line']}] {k}: 표지 있음, 엄격 본문에 † 없음" + (" (넓은 본문엔 있음)" if s["dagger_all"] else " (넓은 본문에도 없음)"))
        if not flag and s["dagger_strict"]:
            print(f"[{s['file']}:{s['line']}] {k}: 엄격 본문에 † 있음, 표지 없음")
        if not flag and not s["dagger_strict"] and s["dagger_all"]:
            print(f"[{s['file']}:{s['line']}] {k}: (참고) ∎ 뒤 다음 머리 전 산문에 † 있음, 표지 없음")
    n_flag = sum(1 for s in cur.values() if "작성자 판단" in s["bracket"])
    n_old_flag = sum(1 for s in old.values() if "작성자 판단" in s["bracket"])
    print(f"작성자 판단 머리: 현재 {n_flag}, 이전 {n_old_flag}")
    # 4. 덧붙임 어순
    print("\n== (4) 덧붙임 어순(증명됨, 계산 보조(…), 문헌 인용, 시작점 비명시, 작성자 판단, …에 의존) ==")
    ORDER = ["증명됨", "계산 증거", "계산 보조", "문헌 인용", "시작점 비명시", "작성자 판단", "에 의존"]
    for k in sorted(cur, key=lambda k: cur[k]["order"]):
        s = cur[k]
        st = s["bracket"].split(";")[0]
        pos = [(st.find(w), w) for w in ORDER if w in st]
        seq = [w for _, w in sorted(pos)]
        exp = [w for w in ORDER if w in seq]
        if seq != exp:
            print(f"[{s['file']}:{s['line']}] {k}: [{st}]  순서 {seq}")
    # 5. 「에 의존」 머리 수
    n_dep = sum(1 for s in cur.values() if "에 의존" in s["bracket"])
    print(f"\n「에 의존」 머리 수: 현재 {n_dep}, 이전 {sum(1 for s in old.values() if '에 의존' in s['bracket'])}")
    # 6. † 가 있는 진술 밖 산문(어느 머리 본문에도 속하지 않는 †)
    print("\n== (6) † 전체 자리 ==")
    for name in chapter_files(CUR):
        L = io.open(os.path.join(CUR, name), encoding="utf-8").read().split("\n")
        for i, ln in enumerate(L, 1):
            if "†" in ln:
                print(f"  {name}:{i}: {ln[:100]}")


if __name__ == "__main__":
    main()
