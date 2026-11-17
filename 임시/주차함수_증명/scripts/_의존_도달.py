# -*- coding: utf-8 -*-
"""주 정리에서 출발한 의존 도달 검사(사용자 결정 91 (3)).

사용: python -I scripts/_의존_도달.py [--list] [--strict] [--mentions] [--d] [--all]
읽기만 한다(멱등). 장v2/장*.md의 진술 머리와 증명 본문, 뒤로 미룬 증명 단락에서 간선을 뽑고,
뿌리(주 정리와 그 증명)에서 닿지 않는 진술을 적는다.

간선 규칙(파견문):
  진술 머리 **정리 {{N:label}} (이름) [지위, …에 의존; r…].**  의 머리 줄이 인용하는 라벨,
  증명 본문(머리 다음부터 다음 진술 머리 전까지)이 인용하는 라벨,
  뒤로 미룬 증명 「**정리 {{…}}의 증명.**」 단락(다음 머리 전까지)이 인용하는 라벨.
  --strict 는 증명 본문을 「머리 다음부터 첫 ∎ 또는 다음 절 머리(###)까지」로 좁힌다(비교용).
부록 D 항목은 머리 줄과 「**확인하는 진술.**」 줄의 라벨 가운데 하나라도 닿으면 닿은 것으로 본다.
--mentions 는 닿지 않는 진술마다 장v2 전체·장부_v2.md·구조표_v2.md의 언급 자리를 적는다.
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "장v2")

LABEL_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
D_LABEL_RE = re.compile(r"\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DEFER_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*")
NAME_RE = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{\d+:[A-Za-z][A-Za-z0-9\-]*\}\} \(((?:[^()]|\([^()]*\))*)\)")
D_HEAD_RE = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
SECTION_RE = re.compile(r"^### (\d+\.\d+(?:\.\d+)?)")
CHAPTER_RE = re.compile(r"^## (\d+)\.")

ROOTS = ["1:main-theorem", "10:old-8-37"]


def chapter_files(prefix):
    out = []
    for i in range(1, 12):
        whole = f"{prefix}{i}.md"
        if os.path.exists(os.path.join(BASE, whole)):
            out.append(whole)
            continue
        parts = sorted(n for n in os.listdir(BASE) if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md", n))
        out.extend(parts)
    return out


def read_lines(path):
    return io.open(path, encoding="utf-8").read().split("\n")


def parse_chapters(strict=False):
    """진술 사전 {key: dict(kind, name, section, file, line, order, head, body_labels, body_dlabels)}와
    머리 줄/본문의 간선. 뒤로 미룬 증명은 해당 진술의 본문에 합친다."""
    stmts = {}
    order = 0
    defers = []  # (key, file, line, lines)
    for name in chapter_files("장"):
        lines = read_lines(os.path.join(BASE, name))
        section = ""
        chapter = 0
        # 머리 자리와 종류 모으기
        marks = []  # (line_idx, kind, key or None)  kind in head/defer/section
        for i, ln in enumerate(lines):
            m = CHAPTER_RE.match(ln)
            if m:
                chapter = int(m.group(1))
                section = f"{chapter}"
            m = SECTION_RE.match(ln)
            if m:
                section = m.group(1)
                marks.append((i, "section", None, section))
                continue
            d = DEFER_RE.match(ln)
            if d:
                marks.append((i, "defer", f"{d.group(2)}:{d.group(3)}", section))
                continue
            h = HEAD_RE.match(ln)
            if h:
                marks.append((i, "head", f"{h.group(2)}:{h.group(3)}", section))
        # 각 머리의 본문 범위 정하기
        for j, (i, kind, key, sec) in enumerate(marks):
            if kind == "section":
                continue
            # 다음 머리(진술 머리 또는 미룬 증명 머리)까지
            end = len(lines)
            for (i2, kind2, key2, sec2) in marks[j + 1:]:
                if kind2 in ("head", "defer"):
                    end = i2
                    break
            if strict:
                # 첫 ∎ 또는 다음 ### 까지
                end2 = end
                for t in range(i + 1, end):
                    if lines[t].startswith("### "):
                        end2 = t
                        break
                    if "∎" in lines[t]:
                        end2 = t + 1
                        break
                if "∎" in lines[i]:
                    end2 = i + 1
                end = end2
            head_line = lines[i]
            body = lines[i + 1:end]
            if kind == "head":
                order += 1
                hm = HEAD_RE.match(head_line)
                nm = NAME_RE.match(head_line)
                stmts[key] = dict(
                    kind=hm.group(1), name=(nm.group(1) if nm else ""), section=sec, file=name,
                    line=i + 1, order=order, head=head_line,
                    head_labels=set(f"{a}:{b}" for a, b in LABEL_RE.findall(head_line)) - {key},
                    body_labels=set(), body_dlabels=set(), body_end=end,
                )
                for ln in body:
                    stmts[key]["body_labels"].update(f"{a}:{b}" for a, b in LABEL_RE.findall(ln))
                    stmts[key]["body_dlabels"].update(D_LABEL_RE.findall(ln))
                stmts[key]["body_labels"].discard(key)
            else:
                defers.append((key, name, i + 1, [head_line] + body))
    for key, fname, ln_no, blines in defers:
        if key not in stmts:
            print(f"[경고] 미룬 증명의 진술이 없음: {key} ({fname}:{ln_no})")
            continue
        for ln in blines:
            stmts[key]["body_labels"].update(f"{a}:{b}" for a, b in LABEL_RE.findall(ln))
            stmts[key]["body_dlabels"].update(D_LABEL_RE.findall(ln))
        stmts[key]["body_labels"].discard(key)
        stmts[key].setdefault("defer", []).append(f"{fname}:{ln_no}")
    return stmts


def parse_appendix_d():
    items = {}
    cnt = 0
    for name in chapter_files("부록D_장"):
        lines = read_lines(os.path.join(BASE, name))
        cur = None
        for i, ln in enumerate(lines):
            m = D_HEAD_RE.match(ln)
            if m:
                cnt += 1
                cur = m.group(1)
                items[cur] = dict(file=name, line=i + 1, order=cnt, title=ln,
                                  labels=set(f"{a}:{b}" for a, b in LABEL_RE.findall(ln)), verify="")
                continue
            if cur and ln.startswith("**확인하는 진술.**"):
                items[cur]["labels"].update(f"{a}:{b}" for a, b in LABEL_RE.findall(ln))
                items[cur]["verify"] = ln
    return items


def reach(stmts, roots):
    seen = set()
    stack = list(roots)
    via = {}
    while stack:
        k = stack.pop()
        if k in seen:
            continue
        seen.add(k)
        s = stmts.get(k)
        if s is None:
            print(f"[경고] 정의되지 않은 라벨 인용: {k} (from {via.get(k)})")
            continue
        for nxt in s["head_labels"] | s["body_labels"]:
            if nxt not in seen:
                via.setdefault(nxt, k)
                stack.append(nxt)
    return seen, via


def mentions(key, stmts):
    """장v2 전체·장부_v2.md·구조표_v2.md에서 라벨이 나오는 줄(자기 머리와 본문 범위 밖)."""
    out = []
    pat = re.compile(r"\{\{" + re.escape(key) + r"\}\}")
    s = stmts[key]
    files = [os.path.join(BASE, n) for n in sorted(os.listdir(BASE)) if n.endswith(".md")]
    files += [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")]
    for p in files:
        name = os.path.basename(p)
        for i, ln in enumerate(read_lines(p), 1):
            if pat.search(ln):
                if name == s["file"] and s["line"] <= i < s["body_end"] + 1:
                    continue
                out.append((name, i, ln[:160]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="닿지 않는 진술 목록")
    ap.add_argument("--strict", action="store_true", help="증명 본문을 첫 ∎까지로 좁힌다")
    ap.add_argument("--mentions", action="store_true", help="닿지 않는 진술의 언급 자리")
    ap.add_argument("--d", action="store_true", help="부록 D 항목의 도달")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--roots", default=",".join(ROOTS))
    args = ap.parse_args()
    if args.all:
        args.list = args.d = args.mentions = True
    roots = [r for r in args.roots.split(",") if r]
    stmts = parse_chapters(strict=args.strict)
    seen, via = reach(stmts, roots)
    unreached = [k for k in sorted(stmts, key=lambda k: stmts[k]["order"]) if k not in seen]
    print(f"진술 {len(stmts)}개, 뿌리 {roots}, 닿음 {len(seen & set(stmts))}개, 닿지 않음 {len(unreached)}개"
          + (" [strict]" if args.strict else ""))
    if args.list:
        print("\n== 닿지 않는 진술(라벨 | 종류 | 이름 | 절 | 파일:행) ==")
        for k in unreached:
            s = stmts[k]
            print(f"{{{{{k}}}}} | {s['kind']} | {s['name']} | {s['section']} | {s['file']}:{s['line']}")
    if args.mentions:
        print("\n== 닿지 않는 진술의 언급 자리(자기 머리·본문 밖) ==")
        for k in unreached:
            ms = mentions(k, stmts)
            print(f"\n{{{{{k}}}}} ({stmts[k]['kind']} {stmts[k]['name']}): {len(ms)}곳")
            for name, i, ln in ms:
                print(f"  {name}:{i}: {ln}")
    if args.d:
        items = parse_appendix_d()
        cited = set()
        for k in seen:
            if k in stmts:
                cited |= stmts[k]["body_dlabels"]
        print(f"\n== 부록 D 항목 {len(items)}개 ==")
        for nm, it in sorted(items.items(), key=lambda kv: kv[1]["order"]):
            touched = it["labels"] & seen
            un = it["labels"] - seen
            flag = "닿음" if touched else "닿지 않음"
            extra = ""
            if un and touched:
                extra = f" (일부 라벨 닿지 않음: {', '.join(sorted(un))})"
            if not touched:
                extra = f" (라벨: {', '.join(sorted(it['labels']))})"
            print(f"D.{it['order']:>2} {{{{D:{nm}}}}} {flag}{extra}; 닿는 본문이 인용: {'예' if nm in cited else '아니오'}  [{it['file']}:{it['line']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
