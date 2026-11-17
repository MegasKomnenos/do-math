# 검토 23차 R1: 2장 진술 라벨이 다른 장 파일에서 불리는 횟수
import re,glob,io,sys
sys.stdout.reconfigure(encoding='utf-8')
files=sorted(x.replace(chr(92),'/') for x in glob.glob('장v2/*.md'))
txt={f:io.open(f,encoding='utf-8').read() for f in files}
labs=[]
for line in txt['장v2/장2.md'].split('\n'):
    m=re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s*\{\{([^}]+)\}\}(?!의 증명)',line)
    if m: labs.append((m.group(1),m.group(2)))
for kind,lab in labs:
    key='{{'+lab+'}}'
    own=txt['장v2/장2.md'].count(key)
    ch1=txt['장v2/장1.md'].count(key)
    others={f.split('/')[-1][:-3]:txt[f].count(key) for f in files if f not in('장v2/장2.md','장v2/장1.md') and txt[f].count(key)}
    body={k:v for k,v in others.items() if k.startswith('장')}
    flag='' if body else '  <== 3~10장 본문 호출 없음'
    print(f'{kind} {lab}: 2장 {own}, 1장 {ch1}, 그 밖 {others}{flag}')
