# O14: 파일:행:키 를 받아 그 행에서 키 둘레 문맥을 찍는다(검토용 보조).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/math/임시/주차함수_증명/장v2/"
for spec in sys.argv[1:]:
    f, ln, key = spec.split(':', 2)
    lines = open(BASE + f, encoding='utf-8').read().split('\n')
    s = lines[int(ln) - 1]
    if key == '*':
        print(f"== {f}:{ln}\n{s[:700]}")
        continue
    i = s.find(key)
    if i < 0:
        print(f"== {f}:{ln} [{key}] 없음"); continue
    a = max(0, i - 130); b = min(len(s), i + len(key) + 130)
    print(f"== {f}:{ln} [{key}]\n...{s[a:b]}...")
