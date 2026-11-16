# -*- coding: utf-8 -*-
"""정합 검토 2차 V2 (ㄷ): 11.2 표 각 행의 3열(산술 등급)·5열(재계산 꺾쇠)·6열(독립 재계산 전문)을 부록 D 항목의
「산술 등급」 첫 등급·「독립 재계산」 줄과 대조하고, 「확인하는 진술」의 머리 괄호 등급과도 견준다. 읽기만 한다.
사용: python -I scripts/수학검사2/검토정합2_V2_3_등급.py"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
M = importlib.import_module("검토정합2_V2_1_머리")

ROOT = M.ROOT
GRADES = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "평가"]


def grades_in(text):
    out = []
    for g in ("정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석"):
        for m in re.finditer(re.escape(g), text):
            out.append((m.start(), g))
    for m in re.finditer(r"(배정밀도|\d+자리|\d+ 자리|\$\\langle\$정밀도\$\\rangle\$|〈정밀도〉) 평가", text):
        out.append((m.start(), m.group(0)))
    return [g for _, g in sorted(out)]


def parse_D():
    items = {}
    order = 0
    for name in M.chapter_files.__globals__["os"].listdir(os.path.join(ROOT, "장v2")):
        pass
    files = sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_장*.md")), key=lambda p: (len(os.path.basename(p)), os.path.basename(p)))
    # 장 순서: 2,3,4,5A,5B,6,7A,7B,8,9,10
    def key(p):
        b = os.path.basename(p)[len("부록D_장"):-3]
        m = re.match(r"(\d+)([A-Z]?)", b)
        return (int(m.group(1)), m.group(2))
    files.sort(key=key)
    for p in files:
        L = io.open(p, encoding="utf-8").read().split("\n")
        cur = None
        for i, ln in enumerate(L):
            m = re.match(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}(.*)", ln)
            if m:
                order += 1
                cur = m.group(1)
                items[cur] = dict(order=order, file=os.path.basename(p), line=i + 1, title=m.group(2), verify="", grade="", recomp="")
                continue
            if cur is None:
                continue
            if ln.startswith("**확인하는 진술.**"):
                items[cur]["verify"] = ln[len("**확인하는 진술.**"):].strip()
            elif ln.startswith("**산술 등급.**"):
                items[cur]["grade"] = ln[len("**산술 등급.**"):].strip()
            elif ln.startswith("**독립 재계산.**"):
                items[cur]["recomp"] = ln[len("**독립 재계산.**"):].strip()
    return items


def parse_112():
    L = io.open(os.path.join(ROOT, "장v2", "장11.md"), encoding="utf-8").read().split("\n")
    rows = []
    for i, ln in enumerate(L):
        if ln.startswith("| 부록 D.{{D:"):
            cells = [c.strip() for c in ln.strip()[1:-1].split(" | ")]
            # 셀 안에 " | "가 없다고 가정; 셀 수 확인
            if len(cells) != 6:
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip()[1:-1])]
            rows.append(dict(line=i + 1, cells=cells, key=re.match(r"부록 D\.\{\{D:([A-Za-z0-9\-]+)\}\}", cells[0]).group(1)))
    return rows


def main():
    cur = M.parse(M.CUR)
    D = parse_D()
    rows = parse_112()
    print(f"부록 D 항목 {len(D)}, 11.2 행 {len(rows)}")
    dk = [k for k, _ in sorted(D.items(), key=lambda kv: kv[1]["order"])]
    rk = [r["key"] for r in rows]
    if dk != rk:
        print("순서/집합 차이: D만", [k for k in dk if k not in rk], "표만", [k for k in rk if k not in dk])
        if set(dk) == set(rk):
            print("  (집합은 같고 순서만 다름)")
    for r in rows:
        k = r["key"]; it = D.get(k)
        c = r["cells"]
        if it is None:
            print(f"\n[{k}] 부록 D 항목 없음"); continue
        if len(c) != 6:
            print(f"\n[{k}] 11.2 행 셀 수 {len(c)}")
            continue
        notes = []
        # 3열 vs D 산술 등급 첫 등급
        g_table = grades_in(c[2])
        g_D = grades_in(it["grade"])
        first_D = g_D[0] if g_D else "?"
        if not g_table:
            notes.append(f"3열에 등급 없음: {c[2]!r}")
        elif g_table[0] != first_D:
            notes.append(f"3열 첫 등급 {g_table[0]!r} ≠ D 산술 등급 첫 등급 {first_D!r}")
        # 3열 전체 vs D 산술 등급 문장
        if set(g_table) != set(g_D):
            notes.append(f"3열 등급 집합 {g_table} vs D 산술 등급 줄의 등급 {g_D}")
        # 5열 vs 꺾쇠
        m = re.match(r"〔([^〕]*)〕\s*(.*)", it["recomp"], re.S)
        if not m:
            notes.append("D 독립 재계산 줄에 꺾쇠 없음")
        else:
            br, rest = "〔" + m.group(1) + "〕", m.group(2).strip()
            if c[4] != br:
                notes.append(f"5열 ≠ 꺾쇠: 표 {c[4][:80]!r} / D {br[:80]!r}")
            if c[5] != rest:
                # 차이 위치
                j = next((i for i, (a, b) in enumerate(zip(c[5], rest)) if a != b), min(len(c[5]), len(rest)))
                notes.append(f"6열 ≠ 전문(길이 표 {len(c[5])} / D {len(rest)}; 첫 차이 {j}): 표 …{c[5][max(0,j-40):j+60]!r} / D …{rest[max(0,j-40):j+60]!r}")
            # 재계산 산술 vs 3열 (규칙 (ㄴ): 이 글의 재계산이 있으면 그 재계산 등급)
            mm = re.search(r"산술 ([^;〕]*)", m.group(1))
            if mm:
                g_re = grades_in(mm.group(1))
                this_paper = "이 글" in (re.search(r"자료 ([^;〕]*)", m.group(1)).group(1) if re.search(r"자료 ([^;〕]*)", m.group(1)) else "")
                notes.append(f"(참고) 재계산 산술 {g_re}, 자료에 이 글 {'있음' if this_paper else '없음'}; D 산술 등급 줄: {it['grade'][:140]!r}")
        # 2열 진술들의 머리 괄호 등급
        labs = re.findall(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}", c[1])
        vlabs = re.findall(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}", it["verify"])
        if set(labs) != set(vlabs):
            notes.append(f"2열 라벨 {labs} ≠ D 확인하는 진술 라벨 {vlabs}")
        for lab in labs:
            s = cur.get(lab)
            if s is None:
                notes.append(f"  머리 없음 {lab}"); continue
            g_h = grades_in(s["bracket"].split(";")[0])
            if not g_h:
                notes.append(f"  머리 {lab}: 괄호에 등급 없음 [{s['bracket'][:100]}]")
            elif not set(g_table) & set(g_h):
                notes.append(f"  머리 {lab}: 괄호 등급 {g_h} 과 3열 {g_table} 겹침 없음 [{s['bracket'][:100]}]")
            elif set(g_h) != set(g_table):
                notes.append(f"  (참고) 머리 {lab}: 괄호 등급 {g_h} vs 3열 {g_table} [{s['bracket'][:100]}]")
        print(f"\n[{k}] 11.2:{r['line']} / {it['file']}:{it['line']}  3열={c[2]!r}")
        for n in notes:
            print("   -", n)


if __name__ == "__main__":
    main()
