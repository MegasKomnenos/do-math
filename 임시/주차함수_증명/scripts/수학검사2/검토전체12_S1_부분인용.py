# 다른 장이 장2 진술의 부분((가)/(ㄱ)/(i)/(a)/(SM) 등)을 인용할 때 그 부분 표지가 장2 진술에 실제로 있는지 확인
import re, glob, os
root=r'C:\math\임시\주차함수_증명\장v2'
files={os.path.basename(p):open(p,encoding='utf-8').read() for p in glob.glob(os.path.join(root,'*.md'))}
t2=files['장2.md']
heads=[(m.start(),m.group(1)) for m in re.finditer(r'\*\*(?:정리|명제|보조정리|따름정리|정의)\s+\{\{(2:[^}]+)\}\}',t2)]
parts={}
for i,(pos,lab) in enumerate(heads):
    end=heads[i+1][0] if i+1<len(heads) else len(t2)
    body=t2[pos:end]
    # 진술 본문(증명 전)만: '**증명' 전까지
    stmt=body.split('**증명')[0]
    found=set(re.findall(r'\((가|나|다|라|마|바|사|아|ㄱ|ㄴ|ㄷ|i|ii|iii|iv|a|b|c|d|SM|DM0|SC)\)',stmt))
    parts[lab]=found
pat=re.compile(r'\{\{(2:[^}]+)\}\}(?:의)?\s*\(?((?:\((?:가|나|다|라|마|바|사|아|ㄱ|ㄴ|ㄷ|i|ii|iii|iv|a|b|c|d|SM|DM0|SC)\)[·,\s]*)+)')
for fn,txt in sorted(files.items()):
    if fn=='장2.md': continue
    for m in pat.finditer(txt):
        lab=m.group(1); cited=re.findall(r'\((가|나|다|라|마|바|사|아|ㄱ|ㄴ|ㄷ|i|ii|iii|iv|a|b|c|d|SM|DM0|SC)\)',m.group(2))
        for c in cited:
            if c not in parts.get(lab,set()):
                s=max(0,m.start()-60); print(fn, lab, '인용 부분',c,'| 실제 부분',sorted(parts.get(lab,[])),'|',txt[s:m.end()].replace('\n',' '))
print('done')
