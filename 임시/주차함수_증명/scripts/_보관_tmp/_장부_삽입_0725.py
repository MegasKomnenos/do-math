import io, re, sys
p = '작업_장부.md'
t = io.open(p, encoding='utf-8').read()
item = io.open('대조v2/수학검사2/_장부_항목_전체검토2회수.txt', encoding='utf-8').read().rstrip('\n') + '\n'
resume = io.open('대조v2/수학검사2/_장부_재개15.txt', encoding='utf-8').read().rstrip('\n') + '\n'
key_item = item.split('**')[1]
key_res = '열다섯째 압축'
if key_item in t:
    print('항목 이미 있음')
else:
    marker = '\n## 재개 기록\n'
    i = t.index(marker)
    head = t[:i].rstrip('\n') + '\n\n' + item
    t = head + marker + t[i + len(marker):]
    print('항목 삽입')
if key_res in t:
    print('재개 기록 이미 있음')
else:
    t = t.rstrip('\n') + '\n' + resume
    print('재개 기록 추가')
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
