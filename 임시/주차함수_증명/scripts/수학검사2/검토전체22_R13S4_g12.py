# 장부 1.1·1.2(20–288행)에서 첫 셀에 주어진 고정 문자열이 든 행을 찾아 (행 번호, 기호, 뜻 앞부분, 정의 절, 쓰이는 장)을 낸다. 자리 찾기용.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
n = int(sys.argv[1]) if sys.argv[1].isdigit() else 200
toks = sys.argv[2:] if sys.argv[1].isdigit() else sys.argv[1:]
for t in toks:
    hit = False
    for i in range(19, 288):
        l = L[i]
        if not l.startswith('|'): continue
        c = l.strip().strip('|').split(' | ')
        if t in c[0]:
            hit = True
            if len(c) >= 6:   # 1.2: 기호|글자체|뜻|정의 절|쓰이는 장|...
                print(f"{i+1}: {c[0]} || {c[2][:n]} || 정의 {c[3]} || 장 {c[4]}")
            else:
                print(f"{i+1}: {c[0]} || {' | '.join(c[1:])[:n]}")
    if not hit: print(f"-- {t}: 1.1·1.2 첫 셀에 없음")
