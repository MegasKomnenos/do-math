import io
p = '작업_장부.md'
t = io.open(p, encoding='utf-8').read()
item = io.open('대조v2/수학검사2/_장부_항목_전체검토3회수.txt', encoding='utf-8').read().rstrip('\n') + '\n'
key = item.split('**')[1]
if key in t:
    print('항목 이미 있음')
else:
    marker = '\n## 재개 기록\n'
    i = t.index(marker)
    t = t[:i].rstrip('\n') + '\n\n' + item + marker + t[i + len(marker):]
    print('항목 삽입')
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
