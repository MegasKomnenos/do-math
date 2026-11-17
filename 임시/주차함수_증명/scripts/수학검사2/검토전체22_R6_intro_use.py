# 7장 머리말(장7A 5행)이 받는다고 적은 라벨이 7A·7B 본문에서 실제로 쓰이는지, 거꾸로 본문이 쓰는 앞 장 라벨이 머리말에 있는지 센다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
A = open('장v2/장7A.md', encoding='utf-8').read().split('\n')
B = open('장v2/장7B.md', encoding='utf-8').read().split('\n')
intro = '\n'.join(A[0:9])
bodyA = '\n'.join(A[10:])
bodyB = '\n'.join(B)
pat = r'\{\{([0-9A-Z]+:[^}]+)\}\}'
il = sorted(set(re.findall(pat, intro)))
print('== 머리말 라벨의 본문 사용 횟수 (7A 본문, 7B) ==')
for l in il:
    t = '{{' + l + '}}'
    print(f'{l:32s} 7A={bodyA.count(t):3d} 7B={bodyB.count(t):3d}')
print('== 본문이 쓰는 앞 장(2~6) 라벨 가운데 머리말에 없는 것 ==')
used = sorted(set(re.findall(pat, bodyA + bodyB)))
for l in used:
    if l.split(':')[0] in '23456' and l not in il:
        t = '{{' + l + '}}'
        print(f'{l:32s} 7A={bodyA.count(t):3d} 7B={bodyB.count(t):3d}')
