# 보고 파일에서 주어진 머리 문구로 시작하는 한 문단(빈 줄까지)을 지운다.
import sys
p = 'scripts/수학검사2/검토전체22_R13_부분_S5.md'
s = open(p, encoding='utf-8').read()
head = open(sys.argv[1], encoding='utf-8').read().rstrip('\n')
i = s.find(head); assert i >= 0 and s.count(head) == 1
j = s.find('\n\n', i)
open(p, 'w', encoding='utf-8').write(s[:i] + s[j + 2:])
print('cut', j - i)
