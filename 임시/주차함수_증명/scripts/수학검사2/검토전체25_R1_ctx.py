# R1 보조: 고정 문자열의 앞뒤 문맥을 글자 단위로 출력 (읽기 전용)
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
path, needle = sys.argv[1], sys.argv[2]
before = int(sys.argv[3]) if len(sys.argv) > 3 else 200
after = int(sys.argv[4]) if len(sys.argv) > 4 else 300
maxhits = int(sys.argv[5]) if len(sys.argv) > 5 else 20
hits = 0
with open(path, encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        start = 0
        while True:
            i = line.find(needle, start)
            if i < 0:
                break
            hits += 1
            if hits <= maxhits:
                print(f"{no}: …{line[max(0, i - before):i + len(needle) + after].rstrip()}…")
            start = i + len(needle)
print(f"[{hits} hits] {path} :: {needle}")
