# 수리 전체24 ZL — 읽기 전용 도우미: 파일에서 고정 문자열의 모든 출현을 줄 번호·앞뒤 문맥과 함께 찍는다.
# 쓰기: python -I -X utf8 수리전체24_ZL_ctx.py FILE ANCHOR [앞뒤 글자 수=200] [줄 범위 a-b]
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
path, anchor = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 200
lo, hi = 1, 10**9
if len(sys.argv) > 4:
    lo, hi = map(int, sys.argv[4].split("-"))
n = 0
with open(path, encoding="utf-8", newline="") as f:
    for i, line in enumerate(f, 1):
        if not (lo <= i <= hi):
            continue
        s = 0
        while True:
            j = line.find(anchor, s)
            if j < 0:
                break
            n += 1
            a, b = max(0, j - w), min(len(line), j + len(anchor) + w)
            print(f"[{i}:{j}] …{line[a:b].rstrip()}…")
            s = j + len(anchor)
print(f"== {n}건: {anchor!r} in {path}")
