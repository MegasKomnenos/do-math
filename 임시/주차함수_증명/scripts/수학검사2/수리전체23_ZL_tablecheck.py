# 수리 전체23 ZL — 읽기 전용: 표마다 행의 칸 수가 머리 행과 같은지($…$ 수식과 `…` 안의 세로줄은 세지 않는다), CR·끝 개행·$ 짝·{{ }} 짝을 본다.
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
def cols(line):
    n = 0; inm = False; inb = False; i = 0
    while i < len(line):
        ch = line[i]
        if ch == chr(92): i += 2; continue
        if ch == "`": inb = not inb
        elif ch == "$" and not inb: inm = not inm
        elif ch == "|" and not inm and not inb: n += 1
        i += 1
    return n
for path in sys.argv[1:]:
    b = open(path, "rb").read()
    s = b.decode("utf-8"); L = s.split("\n")
    bad = []; hdr = None
    for i, l in enumerate(L, 1):
        if l.startswith("|"):
            c = cols(l)
            if hdr is None: hdr = c
            elif c != hdr: bad.append((i, c, hdr))
        else:
            hdr = None
    odd = [i for i, l in enumerate(L, 1) if l.replace(chr(92) + "$", "").count("$") % 2]
    lab = [i for i, l in enumerate(L, 1) if l.count("{{") != l.count("}}")]
    print(f"{os.path.basename(path)}: {len(b)}바이트, {len(L)-1}줄, CR {b.count(bytes([13]))}, 끝 개행 {'하나' if s.endswith(chr(10)) and not s.endswith(chr(10)*2) else '이상'}, 칸 수 어긋난 행 {bad[:8]}, $ 홀수 행 {odd[:8]}, 라벨 괄호 어긋난 행 {lab[:8]}")
