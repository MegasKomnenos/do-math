# -*- coding: utf-8 -*-
"""I11 검토 보조: 부록 D 항목 색인과 장 파일 라벨 색인을 만들고, 11.2절 표의 각 행을 부록 D 항목과 나란히 적는다.
판단은 사람이 한다. 이 스크립트는 자리를 찾고 나란히 놓는 데만 쓴다."""
import re, glob, os, sys, io
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")

# ---------- 부록 D 항목 ----------
ditems = {}
for f in sorted(glob.glob(os.path.join(CH, "부록D_장*.md"))):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{D:([^}]+)\}\}", txt)
    # parts: [pre, label, body, label, body...]
    for i in range(1, len(parts), 2):
        lab = parts[i]; body = parts[i+1]
        title = body.split("\n",1)[0].strip()
        def line(name):
            m = re.search(r"(?m)^\*\*"+name+r"\.\*\*\s*(.*)$", body)
            return m.group(1).strip() if m else None
        ditems[lab] = dict(file=os.path.basename(f), title=title,
                           stmt=line("확인하는 진술"), grade=line("산술 등급"),
                           indep=line("독립 재계산"), data=line("자료"), src=line("출처"))

# ---------- 장 파일 라벨 색인 ----------
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?|D):([^}]+)\}\}(.*)$")
SEC = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)[ .]")
labels = {}
for f in sorted(glob.glob(os.path.join(CH, "장*.md"))):
    cur_sec = None
    for ln, L in enumerate(open(f, encoding="utf-8"), 1):
        m = SEC.match(L)
        if m:
            cur_sec = m.group(2)
        m = HEAD.match(L)
        if m:
            kind, ch, lab, rest = m.groups()
            labels[(ch, lab)] = dict(kind=kind, file=os.path.basename(f), line=ln, sec=cur_sec, head=L.strip())

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "table"
    if mode == "table":
        txt = open(os.path.join(CH, "장11.md"), encoding="utf-8").read()
        rows = [L for L in txt.splitlines() if L.startswith("| 부록 D.{{D:")]
        for r in rows:
            cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
            lab = re.search(r"\{\{D:([^}]+)\}\}", cells[0]).group(1)
            d = ditems.get(lab)
            print("="*100)
            print("행:", lab)
            print("  표 진술 :", cells[1])
            print("  D 제목  :", d["title"] if d else "!!없음")
            print("  표 등급 :", cells[2])
            print("  D 등급  :", d["grade"] if d else "")
            print("  표 쓰인곳:", cells[3])
            # 진술의 실제 절
            for m in re.finditer(r"\{\{(\d+[AB]?):([^}]+)\}\}", cells[1]):
                ch, sl = m.groups()
                key = None
                for k in labels:
                    if k[1] == sl and k[0].rstrip("AB") == ch.rstrip("AB"):
                        key = k; break
                info = labels.get(key)
                print("    진술", ch, sl, "->", (info["file"], info["sec"], info["kind"]) if info else "!!라벨 없음")
            print("  표 재계산:", cells[4])
            print("  표 독립  :", cells[5])
            print("  D 독립   :", d["indep"] if d else "")
    elif mode == "labels":
        for k, v in labels.items():
            print(k, v["file"], v["sec"], v["kind"])
    elif mode == "ditems":
        for k, v in ditems.items():
            print(k, v["file"], "|", v["title"], "|", v["grade"])
