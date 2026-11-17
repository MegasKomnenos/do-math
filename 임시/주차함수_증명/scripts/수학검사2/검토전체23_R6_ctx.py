# 고정 문자열을 파일에서 찾아 앞뒤 문맥을 잘라 보여 준다(자리 찾기 전용).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path, tok = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 160
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 12
lo = int(sys.argv[5]) if len(sys.argv) > 5 else 1
hi = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
n = 0
with open(path, encoding='utf-8') as f:
    for ln, line in enumerate(f, 1):
        if ln < lo or ln > hi: continue
        s = 0
        while True:
            i = line.find(tok, s)
            if i < 0: break
            n += 1
            if n <= mx:
                print(f"[{ln}:{i}] …{line[max(0,i-w):i+len(tok)+w].strip()}…")
            s = i + len(tok)
print("총", n, "건")
