# -*- coding: utf-8 -*-
"""R5 정합 검토 둘째 스크립트: 부록 D 자료 줄 ↔ 원고_자료(README 두 표·디스크·SHA) ↔ 재실행표, 11.2 4·6열, 용어. 읽기만 한다.
사용: python -I scripts/수학검사2/검토정합_R5_자료.py [--sha]
"""
import glob
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAP = os.path.join(ROOT, "장v2")
DATA = os.path.join(ROOT, "원고_자료")
INPROG = ("세션_재계산/critical_window_rerun/", "세션_재계산/icert_py_full/", "세션_재계산/moment_cert_iv/")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토정합_R5_추출 import parse_D, parse_11_2, parse_heads, cell, STMT  # noqa: E402


def read(p):
    return io.open(p, encoding="utf-8").read().split("\n")


def parse_readme():
    lines = read(os.path.join(DATA, "README.md"))
    sess, files = {}, []
    mode = None
    for l in lines:
        if l.startswith("## 세션이 만든 수정판"):
            mode = "sess"
        elif l.startswith("## 파일 목록"):
            mode = "files"
        elif l.startswith("## "):
            mode = None
        if not l.startswith("| `"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if mode == "sess" and len(cells) == 2:
            sess[cells[0].strip("`")] = cells[1].strip("`")
        elif mode == "files" and len(cells) == 4:
            files.append(dict(path=cells[0].strip("`"), src=cells[1], label=cells[2], sha=cells[3].strip("`")))
    return sess, files


def label_sections():
    sec_of = {}
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md"))):
        sec = ""
        for ln in read(p):
            m = re.match(r"^### (\d+\.\d+)", ln)
            if m:
                sec = m.group(1)
                continue
            h = re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z0-9\-]+)\}\}", ln)
            if h and not ln[h.end():].lstrip().startswith("의 증명"):
                sec_of[(h.group(2), h.group(3))] = sec
    return sec_of


def sentences(s):
    return [x.strip() for x in re.split(r"(?<=다)\.\s", s) if x.strip()]


def main():
    do_sha = "--sha" in sys.argv
    items, order = parse_D()
    rows = parse_11_2()
    sess, files = parse_readme()
    sec_of = label_sections()
    print(f"README 세션 표 {len(sess)}행, 파일 목록 {len(files)}행")
    by_label = {}
    for f in files:
        by_label.setdefault(f["label"], []).append(f)
    print("README 파일 목록의 라벨 가운데 D에 없는 것:", sorted(set(by_label) - set(items)))
    print()

    for lab in order:
        it = items[lab]
        F = it["fields"]
        print("=" * 100)
        print(f"[{lab}]")
        row = rows[lab]
        # 4열
        mt = re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", it["title"])
        tl = STMT.findall(mt.group(1)) if mt else []
        secs = sorted({sec_of.get((a, b), "?") for _, a, b in tl}, key=lambda s: tuple(int(x) for x in s.split(".")) if s != "?" else (99,))
        want = "·".join(secs)
        if want != row["cells"][3]:
            print(f" !! 4열 {row['cells'][3]} ≠ 머리 괄호 진술의 절 {want}")
        # 6열 문장 포함 검사
        rc = F.get("독립 재계산", (0, ""))[1]
        mb = re.match(r"〔([^〕]*)〕\s*(.*)$", rc)
        dtxt = cell(mb.group(2).strip()) if mb else ""
        c6 = row["cells"][5]
        if c6 != dtxt and not dtxt.startswith(c6):
            ds = set(sentences(dtxt))
            miss = [s for s in sentences(c6) if s not in ds and (s + ".") not in dtxt and s.rstrip(".") not in dtxt]
            if miss:
                print(" !! 6열에 D 문단에 없는 문장:", miss)
            else:
                print(f" 6열: D의 문장 부분집합(문장 {len(sentences(c6))}/{len(sentences(dtxt))}; 앞부분만은 아님)")
        # 재실행 열 대조는 재실행표에서
        # 자료 줄 토큰 해석
        mat = F.get("자료", (0, ""))[1]
        toks = re.findall(r"`([^`]+)`", mat)
        curdir = None
        missing, checked, bare_unresolved = [], 0, []
        dnames = set()
        for t in toks:
            t0 = t.strip()
            if t0.startswith("원고_자료/"):
                rel = t0[len("원고_자료/"):]
                full = os.path.join(ROOT, t0)
                checked += 1
                if not (os.path.exists(full) or glob.glob(full)):
                    missing.append(t0)
                curdir = rel if rel.endswith("/") else os.path.dirname(rel)
                dnames.add(rel.rstrip("/"))
                continue
            if t0.startswith("records/"):
                curdir = None
                base = os.path.basename(t0.rstrip("/"))
                if base and "…" not in base:
                    dnames.add(base)
                continue
            if " " in t0 or t0.startswith("--") or t0.startswith("python") or t0.startswith("cd ") or t0.startswith("sh ") or t0.startswith("cmd"):
                continue
            # 맨이름
            if re.search(r"\.[A-Za-z0-9]{1,5}$|\*|/$", t0):
                dnames.add(os.path.basename(t0.rstrip("/")))
                if curdir is not None:
                    checked += 1
                    full = os.path.join(DATA, curdir, t0)
                    if not (os.path.exists(full) or glob.glob(full)):
                        # 하위 폴더 포함 탐색
                        hits = glob.glob(os.path.join(DATA, curdir, "**", t0), recursive=True)
                        if not hits:
                            missing.append(f"{curdir}/{t0}")
                else:
                    bare_unresolved.append(t0)
        inprog = any(x in (F.get("자료", (0, ""))[1]) for x in INPROG)
        print(f" 자료 줄: 원고_자료 경로·맨이름 {checked}개 검사, 없음 {len(missing)}개{' (계산 중 폴더 포함)' if inprog else ''}: {missing[:40]}")
        # README 파일 목록(기록 사본) 대조: 이 라벨의 README 행 basename ↔ D 자료 줄의 이름
        rrows = by_label.get(lab, [])
        rnames = {os.path.basename(r["path"]) for r in rrows}
        rnames_src = {os.path.basename(r["src"].split("`")[1]) if "`" in r["src"] else "" for r in rrows}
        d_rec = {n for n in dnames if not n.startswith("세션_재계산")}
        not_in_readme = sorted(n for n in d_rec if n not in rnames and n not in rnames_src and not n.endswith("/") and "*" not in n and not n.endswith(".md"))
        readme_not_in_d = sorted(os.path.basename(r["path"]) for r in rrows if os.path.basename(r["path"]) not in dnames and (r["src"].split("`")[1].split("/")[-1] if "`" in r["src"] else "") not in dnames)
        print(f" README 파일 목록(이 라벨) {len(rrows)}행; D 자료 줄 이름 가운데 README에 없음 {len(not_in_readme)}: {not_in_readme[:30]}")
        print(f"   README 행 가운데 D 자료 줄에 이름이 없음 {len(readme_not_in_d)}: {readme_not_in_d[:30]}")
        # 세션_재계산 파일: README 세션 표에 있는가
        sess_dirs = {d for d in dnames if d.startswith("세션_재계산")}
        for d in sorted(sess_dirs):
            full = os.path.join(DATA, d)
            if os.path.isdir(full):
                fl = [os.path.relpath(os.path.join(dp, f), DATA).replace("\\", "/") for dp, _, fs in os.walk(full) for f in fs]
            else:
                fl = [d]
            notin = [f for f in fl if f not in sess and "__pycache__" not in f and not f.endswith(".pyc")]
            if notin and not any(d.startswith(x.rstrip("/")) for x in INPROG):
                print(f"   세션 폴더 {d}: 디스크 파일 {len(fl)}개 가운데 README 세션 표에 없음 {len(notin)}: {notin[:12]}{' …' if len(notin) > 12 else ''}")
    print()
    print("=" * 100)
    # README 두 표의 파일 존재·SHA
    bad, miss = [], []
    allrows = [(p, s) for p, s in sess.items()] + [(f["path"], f["sha"]) for f in files]
    seen = set()
    for p, sha in allrows:
        if (p, sha) in seen:
            continue
        seen.add((p, sha))
        full = os.path.join(DATA, p)
        if not os.path.exists(full):
            miss.append(p)
            continue
        if do_sha:
            h = hashlib.sha256()
            with open(full, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != sha:
                bad.append((p, sha[:12], h.hexdigest()[:12]))
    print(f"README 표 경로 {len(seen)}개: 디스크에 없음 {len(miss)}: {miss}")
    if do_sha:
        print(f"SHA 불일치 {len(bad)}: {bad}")
    # 재실행표: 재실행 열 ↔ 꺾쇠 자료, 산술 등급 열 ↔ D 첫 문장, 스크립트 존재
    print("=" * 100)
    for l in read(os.path.join(DATA, "재실행표.md")):
        if not l.startswith("| D.{{D:"):
            continue
        c = [x.strip() for x in l.strip().strip("|").split(" | ")]
        lab = re.match(r"D\.\{\{D:([A-Za-z0-9\-]+)\}\}", c[0]).group(1)
        it = items[lab]
        rc = it["fields"].get("독립 재계산", (0, ""))[1]
        mb = re.match(r"〔([^〕]*)〕", rc)
        parts = [x.strip() for x in mb.group(1).split(";")] if mb else []
        jaryo = parts[-1].replace("자료 ", "") if parts else "?"
        if jaryo != c[9]:
            print(f" !! 재실행표 {lab}: 재실행 열 「{c[9]}」 ≠ 꺾쇠 자료 「{jaryo}」")
        for s in re.findall(r"`([^`]+)`", c[2]):
            if s.startswith("세션_재계산/") and not os.path.exists(os.path.join(DATA, s)):
                print(f" !! 재실행표 {lab}: 스크립트 없음 {s}")
        g = it["fields"].get("산술 등급", (0, ""))[1]
        if not g.startswith(c[7].rstrip(".")[:20]):
            print(f" !! 재실행표 {lab}: 산술 등급 열 「{c[7][:60]}」 vs D 「{g[:60]}」")
    # 용어
    print("=" * 100)
    words = {"칸": r"칸(?![가-힣])|칸마다|칸의|칸으로|칸에|칸은|칸을|칸 ", "블록": r"블록", "사슬": r"사슬", "한쪽 경계": r"한쪽 경계|반대쪽 경계|경계식|경계값", "위 끝/아래 끝": r"위 끝|아래 끝|위끝|아래끝", "상단/하단": r"상단|하단", "상한/하한": r"상한|하한"}
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_*.md"))) + [os.path.join(CHAP, "장11.md"), os.path.join(DATA, "README.md"), os.path.join(DATA, "재실행표.md"), os.path.join(DATA, "빠른_확인.py")]:
        txt = io.open(p, encoding="utf-8").read()
        if p.endswith("장11.md"):
            txt = "\n".join(txt.split("\n")[14:66])
        cnt = {w: len(re.findall(rx, txt)) for w, rx in words.items()}
        print(os.path.basename(p), cnt)
    print()
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_*.md"))) + [os.path.join(DATA, "README.md"), os.path.join(DATA, "재실행표.md"), os.path.join(DATA, "빠른_확인.py")]:
        for i, l in enumerate(read(p), 1):
            for m in re.finditer(r"블록|사슬|한쪽 경계|반대쪽 경계|경계식|경계값", l):
                s = max(0, m.start() - 40)
                print(f"  {os.path.basename(p)}:{i} …{l[s:m.end()+40]}…")


if __name__ == "__main__":
    main()
