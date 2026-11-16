# -*- coding: utf-8 -*-
"""자료 묶음 원고_자료/ 구성.

장v2/부록D_장*.md(또는 조립된 원고.md의 부록 D)의 각 항목에서 **자료.** 줄의 백틱 경로를 읽어
연구 기록 폴더의 파일을 원고_자료/<r7>/<파일 이름>으로 복사하고 SHA-256과 함께 README.md의 표를 채운다.

경로 꼴(지침 7.6): `records/r030ffae…/evidence/peer/rerun/work/cert_lib_fixed.py` 또는
                    `r030ffae/evidence/producer/report.md` (식별자 접두 + 기록 안 경로). 식별자는 접두사로 폴더를 찾는다.
같은 「자료」 줄에서 위 꼴의 경로 뒤에 오는 백틱 항목이 슬래시 없는 파일 이름(확장자가 있고 공백이 없는 것; `a.py`·`b.py`처럼 `·`로 이은 것은 각각, `x-a.json`–`x-g.json` 범위는 디스크의 실제 파일로 풀어서)이면 직전 경로와 같은 기록·같은 폴더(직전이 `…/dir/` 폴더 참조면 그 안, 거기 없으면 그 곁)의 파일로 읽으며, `원고_자료/…`나 다른 슬래시 경로가 끼면 이어받지 않고 파일 뒤 한글 설명 속에서 폴더에 없는 이름은 읽지 않고 알린다.
하위 폴더가 붙은 상대 경로(`code/x.py`)는 직전 경로의 폴더·그 부모·기록 뿌리 순으로 찾고, 그 뒤의 맨 이름은 그 하위 폴더에서 먼저, 없으면 직전 경로의 원래 폴더에서 찾는다.
사용: python 자료묶음_v2.py [--dry] [--source 원고.md]
"""
import argparse
import glob
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
BARE_RE = re.compile(r"^[^\s/\\`·]+\.[A-Za-z][A-Za-z0-9]*$")  # 슬래시·공백 없는 파일 이름(확장자는 글자로 시작)
RANGE_GAP_RE = re.compile(r"^\s*[–—~-]\s*$")
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


def split_bare(seg):
    """백틱 항목이 슬래시 없는 파일 이름이면(`·`로 이은 것은 각각) 이름 목록, 아니면 None."""
    parts = [x.strip() for x in seg.split("·")]
    if parts and all(BARE_RE.match(x) for x in parts):
        return parts
    return None


def expand_range(rid, folder, a, b):
    """`a`–`b`: 두 끝 이름의 공통 접두·접미와 가운데 숫자·글자 범위로 폴더의 실제 파일을 찾는다. 두 끝은 항상 포함."""
    names = [a, b]
    rdir = find_record_dir(rid)
    d = os.path.join(RECORDS, rdir, folder) if rdir else None
    if d and os.path.isdir(d):
        n = min(len(a), len(b))
        p = 0
        while p < n and a[p] == b[p]:
            p += 1
        s = 0
        while s < n - p and a[len(a) - 1 - s] == b[len(b) - 1 - s]:
            s += 1
        ma, mb = a[p:len(a) - s], b[p:len(b) - s]
        pre, suf = re.escape(a[:p]), re.escape(a[len(a) - s:] if s else "")
        rx = None
        if ma.isdigit() and mb.isdigit():
            w = r"\d{%d}" % len(ma) if len(ma) == len(mb) else r"\d+"
            rx = re.compile("^" + pre + "(" + w + ")" + suf + "$")
            inr = lambda v: int(ma) <= int(v) <= int(mb)
        elif len(ma) == 1 and len(mb) == 1 and ma.isalpha() and mb.isalpha():
            rx = re.compile("^" + pre + "([A-Za-z])" + suf + "$")
            inr = lambda v: ma <= v <= mb
        if rx:
            for fn in sorted(os.listdir(d)):
                m = rx.match(fn)
                if m and inr(m.group(1)) and os.path.isfile(os.path.join(d, fn)):
                    names.append(fn)
    return sorted(set(names))


def pick_folder(rid, cands, name):
    """후보 폴더 가운데 name(와일드카드 가능)이 디스크에 있는 첫 폴더; 어디에도 없으면 첫 후보."""
    rdir = find_record_dir(rid)
    if rdir:
        for c in cands:
            if glob.glob(os.path.join(RECORDS, rdir, c, name)):
                return c
    return cands[0]


SKIPPED = []  # 한글 설명 뒤에 나와 같은 폴더에 없어서 읽지 않은 파일 이름


def pick_exists(rid, cands, name):
    rdir = find_record_dir(rid)
    return bool(rdir) and any(glob.glob(os.path.join(RECORDS, rdir, c, name)) for c in cands)


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
                last = None  # (식별자 접두, 기록 안 폴더): 직전 경로의 기록·폴더
                segs = list(re.finditer(r"`([^`]+)`", ln))
                skip = set()
                for i, sm in enumerate(segs):
                    if i in skip:
                        continue
                    seg = sm.group(1)
                    if seg.startswith("원고_자료/") or seg.startswith("원고_자료\\"):
                        last = None
                        continue  # 세션이 만든 파일(수정판 코드·재실행 출력)은 세션이 묶음에 직접 둔다.
                    pms = list(PATH_RE.finditer("`" + seg + "`"))
                    for pm in pms:
                        rel = pm.group(2).replace("\\", "/")
                        items.append((cur, pm.group(1), rel))
                        par = os.path.dirname(rel.rstrip("/")).replace("\\", "/")
                        # 파일 경로: 같은 폴더. 폴더 참조(끝이 /): 그 폴더 안, 없으면 그 폴더의 형제 위치.
                        last = (pm.group(1), [rel.rstrip("/"), par] if rel.endswith("/") else [par], rel.endswith("/"))
                    if pms:
                        continue
                    bare = split_bare(seg)
                    if bare is not None:
                        if last is None:
                            continue
                        rid, cands, is_dir = last
                        if (not is_dir and i > 0 and re.search("[가-힣]", ln[segs[i - 1].end():sm.start()])
                                and not any(pick_exists(rid, cands, n) for n in bare)):
                            SKIPPED.append((cur, rid, cands[0], bare))
                            continue  # 파일 뒤에 글이 끼고(예: 「(입력은 `x.tsv`」) 같은 폴더에도 없으면 다른 곳의 파일을 가리키는 설명 속 언급이다.
                        if (len(bare) == 1 and i + 1 < len(segs) and i + 1 not in skip
                                and RANGE_GAP_RE.match(ln[sm.end():segs[i + 1].start()])):
                            b2 = split_bare(segs[i + 1].group(1))
                            if b2 is not None and len(b2) == 1:
                                folder = pick_folder(rid, cands, bare[0])
                                bare = expand_range(rid, folder, bare[0], b2[0])
                                skip.add(i + 1)
                                for name in bare:
                                    items.append((cur, rid, (folder + "/" + name) if folder else name))
                                continue
                        for name in bare:
                            folder = pick_folder(rid, cands, name)
                            items.append((cur, rid, (folder + "/" + name) if folder else name))
                    elif "/" in seg or "\\" in seg:
                        # 하위 폴더가 붙은 상대 경로(`code/x.py`, `outputs/y.txt`): 직전 기록 경로의 폴더, 그 부모 폴더, 기록 뿌리 순으로 찾는다.
                        rel_seg = seg.replace("\\", "/").strip()
                        found = None
                        if last is not None and not rel_seg.startswith("records") and not re.match(r"r[0-9a-f]{7}", rel_seg) and " " not in rel_seg:
                            rid, cands, is_dir = last
                            rdir = find_record_dir(rid)
                            base = cands[0]
                            for t in (base + "/" + rel_seg, os.path.dirname(base) + "/" + rel_seg, rel_seg):
                                t = t.lstrip("/")
                                if rdir and os.path.exists(os.path.join(RECORDS, rdir, t)):
                                    found = t
                                    break
                        if found:
                            items.append((cur, rid, found))
                            # 뒤의 맨 이름은 이 하위 폴더에서 먼저 찾고, 없으면 직전 경로의 원래 폴더(들)에서 찾는다.
                            # (`…/output/a.json`, `code/x.py`, `run.log`의 `run.log`는 output/code/가 아니라 output/에 있다.)
                            keep = [os.path.dirname(found)] + [c for c in cands if c != os.path.dirname(found)]
                            last = (rid, keep, False)
                        else:
                            last = None  # 알 수 없는 슬래시 경로가 끼면 직전 경로의 폴더를 이어받지 않는다.
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
        short = rdir[:8]
        if "*" in rel or "?" in rel:
            # 와일드카드 경로: 기록 폴더 안에서 확장해 파일마다 복사한다.
            matches = sorted(p for p in glob.glob(src) if os.path.isfile(p))
            if not matches:
                problems.append(f"{d_item}: 파일 없음 {rid}/{rel}")
                continue
            for fsrc in matches:
                frel = os.path.relpath(fsrc, os.path.join(RECORDS, rdir)).replace("\\", "/")
                fdest = os.path.join(BUNDLE, short, frel)
                if not args.dry:
                    os.makedirs(os.path.dirname(fdest), exist_ok=True)
                    shutil.copy2(fsrc, fdest)
                rows.append((f"{short}/{frel}", f"[{short}] `{frel}`(패턴 `{rel}`)", d_item, sha256(fsrc)))
            continue
        if not os.path.exists(src):
            problems.append(f"{d_item}: 파일 없음 {rid}/{rel}")
            continue
        if os.path.isdir(src):
            # 폴더 참조: 폴더 구조를 유지해 파일 전부를 복사한다(__pycache__ 제외).
            for root_, dirs_, files_ in os.walk(src):
                dirs_[:] = [d for d in dirs_ if d != "__pycache__"]
                for fn in sorted(files_):
                    fsrc = os.path.join(root_, fn)
                    frel = os.path.relpath(fsrc, os.path.join(RECORDS, rdir)).replace("\\", "/")
                    fdest = os.path.join(BUNDLE, short, frel)
                    if not args.dry:
                        os.makedirs(os.path.dirname(fdest), exist_ok=True)
                        shutil.copy2(fsrc, fdest)
                    rows.append((f"{short}/{frel}", f"[{short}] `{frel}`(폴더 `{rel}`)", d_item, sha256(fsrc)))
            continue
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
    for d_item, rid, folder, names in SKIPPED:
        print(f" ~ 읽지 않음(설명 속 언급) {d_item}: {'·'.join(names)} (직전 경로 폴더 {rid}/{folder})")
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
