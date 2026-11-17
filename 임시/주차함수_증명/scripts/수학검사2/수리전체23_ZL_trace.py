# 수리 전체23 ZL — 읽기 전용 흔적 검색: 토큰마다 파일별 출현 수(손 편집 범위와 생성물을 갈라 적는다).
import io, sys, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(BASE)
hand = sorted(glob.glob("장v2/*.md")) + ["장부_v2.md", "구조표_v2.md", "원고_자료/README.md"]
gen = ["의존지도_v2.md", "대조v2/라벨_번호_대응표_1114.md", "원고_자료/재실행표.md"]
txt = {f: open(f, encoding="utf-8").read() for f in hand + gen if os.path.exists(f)}
lines = {f: t.split("\n") for f, t in txt.items()}
for tok in open(sys.argv[1], encoding="utf-8").read().split("\n"):
    tok = tok.rstrip("\r")
    if not tok or tok.startswith("#"):
        continue
    out = []
    for f in hand + gen:
        if f not in txt:
            continue
        c = txt[f].count(tok)
        if c:
            ln = [str(i) for i, l in enumerate(lines[f], 1) if tok in l]
            out.append(f"{'[생성물] ' if f in gen else ''}{os.path.basename(f)}:{c}(행 {','.join(ln[:12])}{'…' if len(ln) > 12 else ''})")
    print(f"{tok!r}: " + ("; ".join(out) if out else "0건"))
