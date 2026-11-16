# 수리 전체10 R6 — 글자 검색 보조(읽기 전용). python -I 로 돌린다.
import re, io, glob, sys, os
os.chdir(r"C:\math\임시\주차함수_증명")

def lines(f):
    return io.open(f, encoding="utf-8").read().split("\n")

mode = sys.argv[1] if len(sys.argv) > 1 else "all"

if mode in ("all", "roman"):
    names = {}
    for f in glob.glob("장v2/*.md") + ["장부_v2.md"]:
        for m in re.finditer(r"\\mathrm\{([A-Za-z]+)\}", io.open(f, encoding="utf-8").read()):
            names[m.group(1)] = names.get(m.group(1), 0) + 1
    print("ROMAN NAMES:", " ".join(sorted(names)))
    print()

if mode in ("all", "7b"):
    for i, l in enumerate(lines("장v2/장7B.md"), 1):
        for t in [r"\mathfrak U", r"\mathfrak W", r"\mathfrak V", r"\mathcal Q", r"\gamma_y", r"R_U"]:
            if t in l:
                j = l.find(t)
                print(f"7B:{i} [{t}] ...{l[max(0,j-70):j+70]}...")
    print()
    for i in (395, 393, 663, 715):
        l = lines("장v2/장7B.md")[i - 1]
        ms = [l[max(0, m.start() - 25):m.end() + 25] for m in re.finditer(r"(?<![A-Za-z\\{])R(?![A-Za-z_^])", l)]
        print("7B bare R", i, ms[:4])
    l = lines("장v2/장5A.md")[731]; j = l.find(r"\mathfrak Z"); print("5A 732:", l[max(0, j - 120):j + 80])
    for i in (407, 412):
        l = lines("장부_v2.md")[i - 1]; j = l.find(r"R^\sharp"); print("장부", i, ":", l[max(0, j - 60):j + 40])
    l = lines("장v2/부록D_장7A.md")[80]; j = l.find(r"\tilde{\mathfrak Z}"); print("D7A 81:", l[max(0, j - 300):j + 200])

if mode == "count":
    # 토큰 전수 검색: 인수로 받은 고정 문자열들을 범위 파일에서 센다
    files = sorted(glob.glob("장v2/*.md")) + ["장부_v2.md", "구조표_v2.md", "원고_자료/README.md"]
    for tok in sys.argv[2:]:
        print(f"### {tok}")
        total = 0
        for f in files:
            hits = [(i, l.count(tok)) for i, l in enumerate(lines(f), 1) if tok in l]
            if hits:
                n = sum(c for _, c in hits); total += n
                print(f"  {f}: {n}  행 {[i for i,_ in hits]}")
        print(f"  합계 {total}")
