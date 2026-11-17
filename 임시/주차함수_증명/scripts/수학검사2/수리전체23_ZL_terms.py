# 수리 전체23 ZL — 읽기 전용: 부록 B의 75개 기록 폴더의 .md/.json/.txt에서 낱말이 나오는 기록 수와 총 출현 수를 센다.
# 쓰기: python -I -X utf8 수리전체23_ZL_terms.py 낱말1 낱말2 …   (첫 인자가 --show=N 이면 낱말마다 N개의 문맥도 찍는다)
import re, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
ids = re.findall(r"(?m)^\| \[?(r[0-9a-f]{7})\]? ", open(os.path.join(BASE, "장v2", "부록B.md"), encoding="utf-8").read())
dirs = {d[:8]: d for d in os.listdir(R)}
args = sys.argv[1:]
show = 0
if args and args[0].startswith("--show="):
    show = int(args[0].split("=")[1]); args = args[1:]
terms = args
cnt = {t: [0, 0, []] for t in terms}   # 기록 수, 총 출현, 문맥
for i in ids:
    seen = set()
    for dp, dn, fn in os.walk(os.path.join(R, dirs[i])):
        for f in fn:
            if not f.lower().endswith((".md", ".json", ".txt")):
                continue
            try:
                s = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for t in terms:
                c = s.count(t)
                if c:
                    cnt[t][1] += c
                    seen.add(t)
                    if show and len(cnt[t][2]) < show:
                        j = s.find(t)
                        cnt[t][2].append(f"    [{i}] {os.path.relpath(os.path.join(dp, f), os.path.join(R, dirs[i]))}: …{s[max(0, j-70):j+len(t)+70]}…".replace("\n", " "))
    for t in seen:
        cnt[t][0] += 1
for t in terms:
    print(f"{t!r}: 기록 {cnt[t][0]}개, 출현 {cnt[t][1]}회")
    for c in cnt[t][2]:
        print(c)
