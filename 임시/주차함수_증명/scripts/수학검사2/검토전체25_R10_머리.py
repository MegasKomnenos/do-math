# 진술 머리(굵은 글씨 첫 조각)를 모두 뽑아 표지에 든 낱말로 걸러 보여 준다. 자리 찾기용.
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
pat = sys.argv[1] if len(sys.argv) > 1 else '계산'
files = [base + f'장{c}.md' for c in ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']]
n = 0
for f in files:
    for i, ln in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'\*\*((?:정리|명제|보조정리|따름정리|정의) \{\{[^}]+\}\}.*?)\.\*\*', ln)
        if m:
            n += 1
            h = m.group(1)
            if re.search(pat, h):
                print(f.split('/')[-1], i, h)
print('heads total', n)
