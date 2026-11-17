# R11 보조: 파일에서 고정 문자열의 앞뒤 문맥을 출력 (정규식 아님)
# 사용: python -I 검토전체22_R11_ctx.py <파일> <앞 글자 수> <뒤 글자 수> <키> [키 ...]
import sys
path, before, after = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
keys = sys.argv[4:]
lines = open(path, encoding='utf-8').read().split('\n')
for key in keys:
    n = 0
    for ln, t in enumerate(lines, 1):
        i = t.find(key)
        while i >= 0:
            n += 1
            print(f"[{key}] {path}:{ln} col {i}: ...{t[max(0, i-before):i+len(key)+after]}...")
            i = t.find(key, i+1)
    print(f"[{key}] total {n}\n")
