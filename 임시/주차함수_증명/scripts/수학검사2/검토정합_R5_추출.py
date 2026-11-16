# -*- coding: utf-8 -*-
"""R5 정합 검토: 부록 D 항목 ↔ 11.2 표 ↔ 진술 머리 ↔ 원고_자료 를 기계적으로 대조한다. 읽기만 한다.
사용: python -I scripts/수학검사2/검토정합_R5_추출.py
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAP = os.path.join(ROOT, "장v2")
DATA = os.path.join(ROOT, "원고_자료")

HEAD = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}\s*(.*)$")
STMT = re.compile(r"(정리|명제|보조정리|따름정리|정의)?\s*\{\{(\d+[AB]?):([A-Za-z0-9\-]+)\}\}")


def read(p):
    return io.open(p, encoding="utf-8").read().split("\n")


def parse_D():
    items = {}
    order = []
    for p in sorted(glob.glob(os.path.join(CHAP, "부록D_*.md"))):
        lines = read(p)
        cur = None
        for i, l in enumerate(lines, 1):
            m = HEAD.match(l)
            if m:
                cur = dict(label=m.group(1), file=os.path.basename(p), line=i, title=m.group(2), fields={}, body=[])
                items[cur["label"]] = cur
                order.append(cur["label"])
                continue
            if cur is None:
                continue
            cur["body"].append((i, l))
            m2 = re.match(r"^\*\*([^*]+)\.\*\*\s*(.*)$", l)
            if m2:
                cur["fields"][m2.group(1)] = (i, m2.group(2))
    return items, order


def parse_11_2():
    p = os.path.join(CHAP, "장11.md")
    rows = {}
    for i, l in enumerate(read(p), 1):
        if l.startswith("| 부록 D.{{D:"):
            cells = [c.strip() for c in l.strip().strip("|").split(" | ")]
            lab = re.match(r"부록 D\.\{\{D:([A-Za-z0-9\-]+)\}\}", cells[0]).group(1)
            rows[lab] = dict(line=i, cells=cells)
    return rows


def parse_heads():
    """장 파일의 진술 머리: label -> (type, 이름, 표지, file, line)"""
    heads = {}
    rx = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?):([A-Za-z0-9\-]+)\}\}(.*?)\*\*")
    for p in sorted(glob.glob(os.path.join(CHAP, "장*.md"))):
        for i, l in enumerate(read(p), 1):
            m = rx.match(l)
            if m:
                rest = m.group(4)
                if rest.lstrip().startswith("의 증명"):
                    continue
                tag = None
                mb = re.search(r"\[([^\]]*)\]\.\s*$", rest)
                if mb:
                    tag = mb.group(1)
                heads[(m.group(2), m.group(3))] = dict(type=m.group(1), rest=rest, tag=tag, file=os.path.basename(p), line=i)
    return heads


def cell(s):
    return re.sub(r"\$[^$]*\$", lambda m: m.group().replace("|", r"\vert "), s)


def main():
    items, order = parse_D()
    rows = parse_11_2()
    heads = parse_heads()
    print("D 항목 수", len(items), "; 11.2 행 수", len(rows))
    print("D에만:", [x for x in order if x not in rows])
    print("11.2에만:", [x for x in rows if x not in items])
    print("순서 같음:", order == list(rows.keys()))
    print()

    for lab in order:
        it = items[lab]
        row = rows.get(lab)
        F = it["fields"]
        print("=" * 100)
        print(f"[{lab}] {it['file']}:{it['line']}  11.2행 {row['line'] if row else '-'}")
        # (ㄱ) 머리 괄호 진술
        mt = re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", it["title"])
        title_stmts = STMT.findall(mt.group(1)) if mt else []
        # 확인하는 진술 줄의 라벨
        chk = F.get("확인하는 진술", (0, ""))[1]
        chk_stmts = STMT.findall(chk)
        print(" 제목:", it["title"][:160])
        if row:
            c2 = STMT.findall(row["cells"][1])
            t_set = [(a, b) for _, a, b in title_stmts]
            c_set = [(a, b) for _, a, b in c2]
            print(" 머리괄호 진술:", [(t or "?", a, b) for t, a, b in title_stmts])
            print(" 11.2 2열:", [(t or "?", a, b) for t, a, b in c2])
            if t_set != c_set:
                print(" !! 머리괄호 ≠ 11.2 2열 (집합 같음=%s)" % (set(t_set) == set(c_set)))
            # 진술 머리 표지
            for t, a, b in title_stmts:
                h = heads.get((a, b))
                if not h:
                    print(f" !! 진술 {{{{{a}:{b}}}}} 머리를 장 파일에서 찾지 못함")
                    continue
                flag = ""
                if t and t != h["type"]:
                    flag = f" !! 유형 불일치(D 제목 {t} / 장 파일 {h['type']})"
                tag = h["tag"] or "(표지 없음)"
                has = ("계산 보조" in tag) or ("계산 증거" in tag)
                print(f"   {h['type']} {{{{{a}:{b}}}}} {h['file']}:{h['line']} 표지=[{tag}]{flag}{'' if has else '  !! 계산 보조·계산 증거 없음'}")
            # 11.2 2열의 진술 유형 대조
            for t, a, b in c2:
                h = heads.get((a, b))
                if h and t and t != h["type"]:
                    print(f" !! 11.2 2열 유형 불일치 {t} {{{{{a}:{b}}}}} / 장 파일 {h['type']}")
            # (ㄴ) 3열 산술
            grade = F.get("산술 등급", (0, ""))[1]
            print(" D 산술 등급:", grade[:200])
            print(" 11.2 3열:", row["cells"][2])
            # 5·6열
            rc = F.get("독립 재계산", (0, ""))[1]
            mb = re.match(r"〔([^〕]*)〕\s*(.*)$", rc)
            if not mb:
                print(" !! 독립 재계산 줄에 꺾쇠 없음:", rc[:100])
            else:
                br = "〔" + mb.group(1) + "〕"
                txt = cell(mb.group(2).strip())
                c5 = row["cells"][4]
                c6 = row["cells"][5]
                if br != c5:
                    print(" !! 5열 ≠ 꺾쇠\n    D :", br, "\n    11:", c5)
                if c6 == txt:
                    print(" 6열: D 전문과 같음")
                elif txt.startswith(c6):
                    print(f" 6열: D의 앞부분({len(c6)}/{len(txt)}자)")
                else:
                    # 첫 차이 위치
                    k = 0
                    while k < min(len(c6), len(txt)) and c6[k] == txt[k]:
                        k += 1
                    print(f" !! 6열 ≠ D(앞부분도 아님). 첫 차이 위치 {k}\n    D :…{txt[max(0,k-60):k+120]}\n    11:…{c6[max(0,k-60):k+120]}")
            # 4열 쓰인 곳
            print(" 4열 쓰인 곳:", row["cells"][3])
        # (ㄷ) 자료 줄 경로
        mat = F.get("자료", (0, ""))[1]
        paths = re.findall(r"`([^`]+)`", mat)
        missing = []
        checked = 0
        for pth in paths:
            if pth.startswith("원고_자료/"):
                rel = pth[len("원고_자료/"):]
                checked += 1
                full = os.path.join(ROOT, pth)
                if not (os.path.exists(full) or glob.glob(full)):
                    missing.append(pth)
        print(f" 자료 줄 원고_자료 경로 {checked}개, 없음: {missing}")
        # 자료 줄의 records/ 접두 기록 식별자가 원고_자료/ 아래 폴더로 있는가
        recs = set(re.findall(r"records/(r[0-9a-f]{7})", mat))
        recs_missing = [r for r in sorted(recs) if not os.path.isdir(os.path.join(DATA, r))]
        print(f" 기록 폴더 {sorted(recs)} 없음: {recs_missing}")
        # 결정 95·96 용어
        body = "\n".join(l for _, l in it["body"])
        for w in ["상한", "하한", "경계", "판정 사슬", "체류", "칸", "블록", "윤곽", "순증가", "멈춤 확률", "젊은 경로", "문턱 예산", "피벗", "꼬리 오목"]:
            for ln, l in it["body"]:
                for m in re.finditer(w, l):
                    s = max(0, m.start() - 25)
                    print(f"   용어「{w}」 {it['file']}:{ln}: …{l[s:m.end()+25]}…")
    print()
    # 라벨별 진술 머리의 계산 보조/계산 증거 표지가 있는데 D 항목에 안 든 진술
    print("=" * 100)
    print("계산 보조·계산 증거 표지가 있는 진술 가운데 어느 D 항목의 머리 괄호에도 없는 것:")
    inD = set()
    for lab in order:
        it = items[lab]
        mt = re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", it["title"])
        for _, a, b in (STMT.findall(mt.group(1)) if mt else []):
            inD.add((a, b))
    for key, h in sorted(heads.items(), key=lambda kv: (kv[1]["file"], kv[1]["line"])):
        tag = h["tag"] or ""
        if ("계산 보조" in tag or "계산 증거" in tag) and key not in inD:
            print(f"  {h['type']} {{{{{key[0]}:{key[1]}}}}} {h['file']}:{h['line']} [{tag}]")


if __name__ == "__main__":
    main()
