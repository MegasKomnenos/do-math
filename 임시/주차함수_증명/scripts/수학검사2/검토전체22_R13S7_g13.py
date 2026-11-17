# 1.3 묶음에서 주어진 고정 문자열이 어느 행(행 번호, 둘째 열=자리)에 있는지 찾는다
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
keys = sys.argv[1:]
for k in keys:
    print('==', k)
    for i in range(288, 357):
        l = L[i]
        if k in l:
            c = l.split(' | ')
            j = l.find(k)
            print('  ', i+1, '| 자리:', (c[1][:70] if len(c) > 1 else ''), '| …', l[max(0, j-90):j+140].replace('\n', ' '))
