# -*- coding: utf-8 -*-
"""자료 묶음 원고_자료/ 구성.

장v2/부록D_장*.md(또는 조립된 원고.md의 부록 D)의 각 항목에서 **자료.** 줄의 백틱 경로를 읽어
연구 기록 폴더의 파일을 원고_자료/<r7>/<파일 이름>으로 복사하고 SHA-256과 함께 README.md의 표를 채운다.

경로 꼴(지침 7.6): `records/r030ffae…/evidence/peer/rerun/work/cert_lib_fixed.py` 또는
                    `r030ffae/evidence/producer/report.md` (식별자 접두 + 기록 안 경로). 식별자는 접두사로 폴더를 찾는다.
사용: python 자료묶음_v2.py [--dry] [--source 원고.md]
"""
import argparse
import hashlib
import io
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECORDS = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
BUNDLE = os.path.join(ROOT, "원고_자료")
PATH_RE = re.compile(r"`(?:records[/\\])?(r[0-9a-f]{7,32})(?:[^`/\\]*)[/\\]([^`]+)`")
D_HEAD_RE = re.compile(r"^### D\.(?:\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}|(\d+))\s*(.*)$")


def find_record_dir(prefix):
    for name in sorted(os.listdir(RECORDS)):
        if name.startswith(prefix):
            return name
    return None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(texts):
    """[(D 항목 표지, 식별자 접두, 기록 안 경로)]"""
    items = []
    for text in texts:
        cur = None
        for ln in text.split("\n"):
            m = D_HEAD_RE.match(ln)
            if m:
                cur = m.group(1) or ("D." + m.group(2))
                continue
            if ln.startswith("**자료.**") and cur:
                for pm in PATH_RE.finditer(ln):
                    items.append((cur, pm.group(1), pm.group(2).replace("\\", "/")))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--source", help="조립된 원고(기본: 장v2/부록D_장*.md 전부)")
    args = ap.parse_args()
    if args.source:
        texts = [io.open(args.source, encoding="utf-8").read()]
    else:
        base = os.path.join(ROOT, "장v2")
        texts = [io.open(os.path.join(base, n), encoding="utf-8").read() for n in sorted(os.listdir(base)) if n.startswith("부록D_장")]
    items = collect(texts)
    rows, problems = [], []
    seen = set()
    for d_item, rid, rel in items:
        rdir = find_record_dir(rid)
        if not rdir:
            problems.append(f"{d_item}: 기록 폴더 없음 {rid}")
            continue
        src = os.path.join(RECORDS, rdir, rel)
        if not os.path.exists(src):
            problems.append(f"{d_item}: 파일 없음 {rid}/{rel}")
            continue
        short = rdir[:8]
        # 같은 이름이 다른 하위 폴더에서 오면 하위 폴더 이름을 접두로
        base_name = os.path.basename(rel)
        sub = os.path.dirname(rel).replace("/", "__")
        dest_name = base_name
        key = (short, base_name)
        if key in seen:
            dest_name = f"{sub}__{base_name}" if sub else base_name
        seen.add(key)
        dest = os.path.join(BUNDLE, short, dest_name)
        if not args.dry:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
        rows.append((f"{short}/{dest_name}", f"[{short}] `{rel}`", d_item, sha256(src)))
    rows = sorted(set(rows))
    print(f"항목 {len(items)}, 복사 {len(rows)}, 문제 {len(problems)}")
    for p in problems:
        print(" -", p)
    if args.dry:
        return 1 if problems else 0
    readme = os.path.join(BUNDLE, "README.md")
    s = io.open(readme, encoding="utf-8").read()
    table = ["| 경로 | 출처(기록·원 경로) | 부록 D 항목 | SHA-256 |", "|---|---|---|---|"]
    for path, src, d_item, digest in rows:
        table.append(f"| `{path}` | {src} | {d_item} | `{digest}` |")
    head = s.split("## 파일 목록", 1)[0]
    s2 = head + "## 파일 목록\n\n" + "\n".join(table) + "\n\n파일마다 원본의 SHA-256을 적었다. 복사 뒤 내용을 고치지 않았다.\n"
    io.open(readme, "w", encoding="utf-8", newline="\n").write(s2)
    print("README 갱신", readme)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
