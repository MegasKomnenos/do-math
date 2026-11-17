import io, sys
p = 'scripts/수학검사2/검토전체22_R13_부분_S5.md'
s = open(p, encoding='utf-8').read()
a, b = sys.argv[1], sys.argv[2]
a = open(a, encoding='utf-8').read().rstrip('\n'); b = open(b, encoding='utf-8').read().rstrip('\n')
assert s.count(a) == 1, s.count(a)
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
