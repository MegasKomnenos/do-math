# 수리 전체24 ZL — 읽기 전용: 고정 문자열(백슬래시 포함)의 출현을 파일별로 세고, --show=N 이면 앞뒤 문맥을 찍는다.
# 쓰기: python -I -X utf8 수리전체24_ZL_count.py [--show=N] [--w=120] [--files=glob,glob] 토큰파일
# 토큰파일은 한 줄에 토큰 하나(#으로 시작하면 주석). 범위 기본값은 장v2/*.md, 장부, 구조표, README와 생성물 셋.
import io, sys, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(BASE)
show = 0; w = 120; files = None
args = sys.argv[1:]
while args and args[0].startswith("--"):
    a = args.pop(0)
    if a.startswith("--show="): show = int(a.split("=")[1])
    elif a.startswith("--w="): w = int(a.split("=")[1])
    elif a.startswith("--files="): files = a.split("=", 1)[1].split(",")
hand = sorted(glob.glob("장v2/*.md")) + ["장부_v2.md", "구조표_v2.md", "원고_자료/README.md"]
gen = ["의존지도_v2.md", "대조v2/라벨_번호_대응표_1114.md", "원고_자료/재실행표.md"]
if files:
    hand = []
    for g in files:
        hand += sorted(glob.glob(g))
    gen = []
txt = {f: open(f, encoding="utf-8").read() for f in hand + gen if os.path.exists(f)}
lines = {f: t.split("\n") for f, t in txt.items()}
for tok in open(args[0], encoding="utf-8").read().split("\n"):
    tok = tok.rstrip("\r")
    if not tok or tok.startswith("#"):
        continue
    out = []
    ctx = []
    for f in hand + gen:
        if f not in txt:
            continue
        c = txt[f].count(tok)
        if c:
            ln = [str(i) for i, l in enumerate(lines[f], 1) if tok in l]
            out.append(f"{'[생성물] ' if f in gen else ''}{os.path.basename(f)}:{c}(행 {','.join(ln[:14])}{'…' if len(ln) > 14 else ''})")
            if show:
                k = 0
                for i, l in enumerate(lines[f], 1):
                    s = 0
                    while k < show:
                        j = l.find(tok, s)
                        if j < 0:
                            break
                        ctx.append(f"    [{os.path.basename(f)}:{i}] …{l[max(0, j - w):j + len(tok) + w]}…")
                        k += 1
                        s = j + len(tok)
    print(f"{tok!r}: " + ("; ".join(out) if out else "0건"))
    for c in ctx:
        print(c)
