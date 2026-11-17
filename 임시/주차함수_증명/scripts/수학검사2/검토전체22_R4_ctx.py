# 검토전체22 R4: 고정 문자열을 파일에서 찾아 앞뒤 문맥만 출력(읽기 전용).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path, needle = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 250
maxn = int(sys.argv[4]) if len(sys.argv) > 4 else 12
n = 0
with open(path, encoding='utf-8') as f:
    for ln, line in enumerate(f, 1):
        i = 0
        while True:
            j = line.find(needle, i)
            if j < 0: break
            n += 1
            if n <= maxn:
                print(f"[{ln}:{j}] ...{line[max(0,j-w):j+len(needle)+w].strip()}...")
                print()
            i = j + len(needle)
print("총", n, "건")
